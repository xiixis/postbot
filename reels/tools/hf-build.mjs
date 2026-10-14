// Сборка проекта HyperFrames из общей папки ролика: node tools/hf-build.mjs <ролик> [--scenes]
//
// HyperFrames рендерит обычную страницу: один index.html, время сцен в data-атрибутах, один
// таймлайн GSAP на паузе. Сборщика у него нет, поэтому страница складывается здесь из того же,
// что читает Remotion: src/<ролик>/shared/scenes.{css,js} и src/<ролик>/timeline.json.
// Разметка пишется в файл готовой (а не строится скриптом при загрузке): так её видят
// проверки HyperFrames. Картинки, шрифты и GSAP кладутся рядом: в рендере сети нет.
//
//   hf/<ролик>/          ролик целиком: сцены, заголовки, знак, звук
//   hf/<ролик>-scenes/   с ключом --scenes: одни сцены без заголовков и звука, для гибрида —
//                        их снимает HyperFrames, остальное кладёт Remotion
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [reel, flag] = process.argv.slice(2);
if (!reel) {
  console.error('нужно имя ролика, например r10-plugins');
  process.exit(2);
}
const bare = flag === '--scenes';
const src = path.join(root, 'src', reel);
const out = path.join(root, 'hf', bare ? `${reel}-scenes` : reel);
const T = JSON.parse(fs.readFileSync(path.join(src, 'timeline.json'), 'utf8'));
const scenario = JSON.parse(fs.readFileSync(path.join(root, 'voice', `${reel.split('-')[0]}.json`), 'utf8'));
// картинки и шрифты могут быть общими у двух версий ролика, а звук у каждой свой
const pub = path.join(root, 'public', scenario['картинки'] || scenario['звук']);
const sound = path.join(root, 'public', scenario['звук'], 'sound.m4a');

// Данные сцен (иконки, анимации Lottie) могут лежать отдельно, в shared/data.js: они идут перед
// сценами одним модулем. Импортов между файлами нет: модуль собирается строкой.
const dataFile = path.join(src, 'shared', 'data.js');
const code = (fs.existsSync(dataFile) ? `${fs.readFileSync(dataFile, 'utf8')}\n` : '')
  + fs.readFileSync(path.join(src, 'shared', 'scenes.js'), 'utf8');
const mod = await import(`data:text/javascript;base64,${Buffer.from(code).toString('base64')}`);
const css = fs.readFileSync(path.join(src, 'shared', 'scenes.css'), 'utf8');
const fonts = fs.readFileSync(path.join(pub, 'fonts', 'fonts.css'), 'utf8').replaceAll('{{A}}', 'assets');

fs.mkdirSync(path.join(out, 'assets'), { recursive: true });
fs.cpSync(pub, path.join(out, 'assets'), { recursive: true, filter: (f) => !/hf-scenes\.mp4$|fonts\.css$|sound\.m4a$|[\\/]v\d+$/.test(f) });
if (!bare) fs.copyFileSync(sound, path.join(out, 'assets', 'sound.m4a'));
fs.copyFileSync(path.join(root, 'node_modules', 'gsap', 'dist', 'gsap.min.js'), path.join(out, 'assets', 'gsap.min.js'));

// Объём: если у ролика есть shared/three.js, рядом кладётся Three.js из node_modules (в рендере сети нет), а на
// страницу — карта импортов и модуль сцены. Сцена рисует кадр по событию hf-seek от HyperFrames, а не по часам;
// готовность (шрифты для надписей, текстуры) отдаёт через window.__hf.buildReady, рендер её ждёт.
// Проверено пробой 14.10.2026 (r14): знак Claude выдавлен из SVG, свет и отражения, кадры повторяются.
const threeFile = path.join(src, 'shared', 'three.js');
const three = !bare && fs.existsSync(threeFile) ? fs.readFileSync(threeFile, 'utf8') : '';
const THREE_ADDONS = { SVGLoader: 'loaders/SVGLoader.js', RoomEnvironment: 'environments/RoomEnvironment.js', RoundedBoxGeometry: 'geometries/RoundedBoxGeometry.js' };
if (three) {
  fs.copyFileSync(path.join(root, 'node_modules', 'three', 'build', 'three.module.js'), path.join(out, 'assets', 'three.module.js'));
  for (const rel of Object.values(THREE_ADDONS)) {
    fs.mkdirSync(path.dirname(path.join(out, 'assets', 'addons', rel)), { recursive: true });
    fs.copyFileSync(path.join(root, 'node_modules', 'three', 'examples', 'jsm', rel), path.join(out, 'assets', 'addons', rel));
  }
}
const threeHead = three ? `    <script type="importmap">{ "imports": { "three": "./assets/three.module.js", "three/addons/": "./assets/addons/" } }</script>\n` : '';
const threeBody = three ? `    <script type="module">
import * as THREE from 'three';
${Object.entries(THREE_ADDONS).map(([n, rel]) => `import { ${n} } from 'three/addons/${rel}';`).join('\n')}
// объём: src/${reel}/shared/three.js
${three.replace(/^export /gm, '')}
window.__hf = window.__hf || {};
window.__hf.buildReady = window.__hf.buildReady || {};
let draw = null;
window.__hf.buildReady['${reel}-three'] = buildThree(THREE, { ${Object.keys(THREE_ADDONS).join(', ')} }, document.getElementById('gl'), T, 'assets')
  .then((f) => { draw = f; f(window.__hfThreeTime || 0); });
window.addEventListener('hf-seek', (e) => { if (draw) draw(e.detail.time); });
    </script>\n` : '';

const D = T.length.toFixed(2);
// У <video> время задаётся на самом теге, и HyperFrames запрещает видео внутри размеченного временем
// предка (lint: video_nested_in_timed_element; кадры берутся не те, клип пропадает посреди окна).
// Поэтому, если в сценах есть видео, слой сцен остаётся простым блоком без времени.
const stageTimed = !/<video[\s>]/.test(mod.markup('assets', T));
const html = `<!doctype html>
<html lang="ru" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>${scenario['композиция']}</title>
    <script src="assets/gsap.min.js"></script>
${threeHead}    <style>
${fonts}
html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #0A0B08; }
#root { position: relative; width: 100%; height: 100%; overflow: hidden; }
${css}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="${D}" data-width="1080" data-height="1920" data-fps="${T.fps}">
      <div id="stage" class="r10${stageTimed ? ' clip" data-start="0" data-duration="' + D + '" data-track-index="0"' : '"'}>
${mod.markup('assets', T)}
${bare ? '' : `<div id="overlay">${mod.overlayMarkup('assets', T)}</div>`}
      </div>
${bare ? '' : `      <audio id="sound" data-start="0" data-duration="${D}" data-track-index="1" data-volume="1" src="assets/sound.m4a"></audio>`}
    </div>
    <script>
// время сцен и слов: src/${reel}/timeline.json, пишет tools/layout.py
const T = ${JSON.stringify({ ...T, wave: undefined, words: undefined, lines: undefined })};
// сцены и движение: src/${reel}/shared/scenes.js, тот же файл читает Remotion
${code.replace(/^export /gm, '')}
const tl = gsap.timeline({ paused: true });
const stage = document.getElementById('stage');
buildScenes(gsap, tl, stage, T);
${bare ? '' : "buildOverlay(gsap, tl, document.getElementById('overlay'), T);"}
window.__timelines["main"] = tl;
    </script>
${threeBody}  </body>
</html>
`;
fs.writeFileSync(path.join(out, 'index.html'), html);
const cli = 'npx --yes hyperframes@0.8.111';
fs.writeFileSync(path.join(out, 'package.json'), `${JSON.stringify({ name: path.basename(out), private: true, type: 'module',
  scripts: { dev: `${cli} preview`, check: `${cli} check`, render: `${cli} render` } }, null, 2)}\n`);
fs.writeFileSync(path.join(out, 'hyperframes.json'), `${JSON.stringify({ $schema: 'https://hyperframes.heygen.com/schema/hyperframes.json',
  registry: 'https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry',
  paths: { blocks: 'compositions', components: 'compositions/components', assets: 'assets' }, media: { autoProxy: true } }, null, 2)}\n`);
console.log(`${path.relative(root, out)}/index.html: ${(html.length / 1024).toFixed(0)} КБ, ${D} с`);
