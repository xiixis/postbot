// Альбом рейтинга для Telegram: node src/r13-rating/картинка.mjs → out/r13-rating-рейтинг.png (весь рейтинг
// одним видом, его обещает ролик) и out/r13-rating-рейтинг-1…4.png (ранги крупно, 1080×1350). Всё с двойной
// плотностью. Общий вид один в ленте не читается: подписи выходят по 7 пунктов на экране телефона.
// Тот же тир-лист и те же стили, что в ролике. Chrome и playwright-core — те же, что у tools/x-shot.mjs.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import { homedir } from 'node:os';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const src = path.join(root, 'src', 'r13-rating', 'shared');
const mod = await import(pathToFileURL(path.join(src, 'scenes.js')).href);
const A = pathToFileURL(path.join(root, 'public', 'rating')).href;
const fonts = fs.readFileSync(path.join(root, 'public', 'rating', 'fonts', 'fonts.css'), 'utf8').replaceAll('{{A}}', A);
const css = fs.readFileSync(path.join(src, 'scenes.css'), 'utf8');
const html = `<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>
${fonts}
html, body { margin: 0; width: 1080px; background: #0A0B08; }
${css}
.r10 { position: relative; inset: auto; width: 1080px; overflow: visible; }
.r10 .pic { position: relative; padding: 0 0 40px; background: radial-gradient(ellipse 80% 40% at 50% 45%, rgba(137,168,28,.28), rgba(10,11,8,0) 70%), #0A0B08; }
.r10 .pic .logo { position: absolute; }
.r10 .pt { padding: 46px 40px 0 170px; height: 196px; box-sizing: border-box; }
.r10 .pt b { display: block; font-family: var(--disp); font-weight: 800; font-size: 60px; letter-spacing: -0.045em; line-height: 1.1; }
.r10 .pt span { display: block; margin-top: 12px; font-size: 30px; color: var(--dim); }
/* тир-лист на всю ширину: 7 плиток в строке, подписи 19 px вместо 9 */
.r10 .ptab { margin: 0 24px; }
.r10 .ptab .tl { display: flex; gap: 8px; }
.r10 .ptab .tr .lb { width: 96px; font-size: 30px; }
.r10 .ptab .tr .lb.g { font-size: 20px; }
.r10 .ptab .tr .ts { gap: 8px 8px; padding: 12px; max-width: none; flex: 1; }
.r10 .ptab .mt { width: 122px; height: 152px; }
.r10 .ptab .mt .ic { width: 96px; height: 96px; border-radius: 22px; }
.r10 .ptab .mt .ic img { width: 62px; height: 62px; }
.r10 .ptab .mt .ic.tx { font-size: 32px; }
.r10 .ptab .mt b { font-size: 19px; line-height: 1.15; margin-top: 6px; font-weight: 700; }
.r10 .pfoot { margin-top: 26px; text-align: center; font-size: 30px; font-weight: 700; color: var(--lime); }
/* карточки альбома: 5 плиток в строке, подписи 30 px */
.r10 .card4 { position: relative; width: 1080px; height: 1350px; overflow: hidden; display: flex; flex-direction: column;
  background: radial-gradient(ellipse 80% 50% at 50% 50%, rgba(137,168,28,.26), rgba(10,11,8,0) 70%), #0A0B08; }
.r10 .card4 .logo { position: absolute; left: 40px; top: 40px; }
.r10 .ch4 { padding: 40px 40px 0 170px; height: 190px; box-sizing: border-box; flex: none; }
.r10 .ch4 b { display: block; font-family: var(--disp); font-weight: 800; font-size: 58px; letter-spacing: -0.045em; line-height: 1.1; }
.r10 .ch4 span { display: block; margin-top: 10px; font-size: 34px; font-weight: 700; color: var(--lime); }
.r10 .cbody { flex: 1; display: flex; align-items: center; margin: 0 24px; }
.r10 .cbody .tl { display: flex; gap: 14px; width: 100%; }
.r10 .cbody .tr .lb { width: 128px; font-size: 44px; }
.r10 .cbody .tr .lb.g { font-size: 30px; }
.r10 .cbody .tr .ts { gap: 14px 12px; padding: 16px; max-width: none; flex: 1; }
.r10 .cbody .mt { width: 160px; height: auto; min-height: 236px; }
.r10 .cbody .mt .ic { width: 128px; height: 128px; border-radius: 30px; }
.r10 .cbody .mt .ic img { width: 84px; height: 84px; }
.r10 .cbody .mt .ic.tx { font-size: 44px; }
.r10 .cbody .mt b { font-size: 29px; line-height: 1.12; margin-top: 10px; font-weight: 700; white-space: normal; }
.r10 .cbody .mt u { left: calc(50% - 73px); top: -9px; width: 146px; height: 146px; border-radius: 38px; border-width: 6px; }
.r10 .cbody .mt.grk u { opacity: 1; }
.r10 .cnote { flex: none; margin: 0 48px 10px; font-size: 38px; line-height: 1.25; font-weight: 600; color: var(--dim); text-align: center; }
.r10 .cnote b { color: #8EC9F2; }
.r10 .cfoot { flex: none; margin: 10px 0 44px; text-align: center; font-size: 32px; font-weight: 700; color: var(--lime); }
</style></head><body><div class="r10">${mod.pictureMarkup(A)}</div></body></html>`;
const pages = [['r13-rating-рейтинг', html]].concat(mod.CARDS.map((_, k) => [`r13-rating-рейтинг-${k + 1}`,
  html.replace(/<body>[\s\S]*<\/body>/, `<body><div class="r10">${mod.cardMarkup(A, k)}</div></body>`)]));
for (const [name, h] of pages) fs.writeFileSync(path.join(root, 'out', name + '.html'), h);
const out = path.join(root, 'out', 'r13-rating-рейтинг.html');
console.log(pathToFileURL(out).href);

const find = (r, ok) => fs.existsSync(r) ? fs.readdirSync(r).sort().reverse().map((i) => path.join(r, i)).find(ok) : null;
const base = find(path.join(homedir(), '.npm/_npx'), (p) => fs.existsSync(path.join(p, 'node_modules/playwright-core')));
const { chromium } = createRequire(path.join(base, 'package.json'))('playwright-core');
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
const page = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
for (const [name] of pages) {
  const f = path.join(root, 'out', name + '.html');
  await page.goto(pathToFileURL(f).href);
  await page.evaluate(() => document.fonts.ready);
  const png = f.replace(/\.html$/, '.png');
  await page.screenshot({ path: png, fullPage: true });
  console.log(png, await page.evaluate(() => document.body.scrollHeight));
}
await b.close();

