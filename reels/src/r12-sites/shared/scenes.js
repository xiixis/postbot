// Ролик «5 бесплатных сайтов для монтажа» (r12), вторая версия. Движок один: HyperFrames.
//
// Рерайт рилса @chingizkhan_yt (instagram.com/reel/Dd-8Bk5x_He). Первая версия вышла слабее оригинала
// (владелец 04.10.2026: «что по эффектам, что по хуку и что по тексту»). Разбор, что было не так и
// что изменено, — ../ВЕРСИЯ-2.md. Коротко:
// - голос одним потоком, без пауз между фразами и без растяжки до двух секунд: ролик 40 с вместо 54;
// - крючок — одна форма: монтажный стол сжимается в телефон, на экране мелькают кадры этого ролика,
//   потом экран пустеет; заголовок наверху показывает фразу кусками, по словам, как у автора,
//   а нижней плашки субтитров и плашек «N/5» больше нет: заголовок и есть субтитры;
// - у каждого сайта свой цвет света (Mixkit синий, FreshLUTs янтарь, LottieFiles мята, Phosphor и
//   React Bits сирень, Claude терракота, сундук золото); наше — знак, кот, шрифты, лаймовая полоса;
// - в кадре живое видео со стока Mixkit (лицензия Free, проверена на странице каждого клипа), цвет
//   «как в кино» — настоящая таблица LUT на движущемся кадре и шторка «до/после» по клику;
// - числа крутятся барабаном, на смене сцен камера пролетает сквозь кадр, клик курсора открывает сайт.
// Всё записано твинами без обратных вызовов: перемотка в любую секунду даёт верный кадр. Видео
// перематывает сам HyperFrames по их data-start; слой сцен поэтому без времени (tools/hf-build.mjs).

export const SITES = [
  { id: 'c1', name: 'Mixkit', logo: 'mixkit-icon.png' },
  { id: 'c2', name: 'FreshLUTs', logo: 'freshluts-icon.png' },
  { id: 'c3', name: 'LottieFiles', logo: 'lottiefiles.png' },
  { id: 'c4', name: 'Phosphor', logo: 'phosphor.png' },
  { id: 'c5', name: 'React Bits', logo: 'reactbits.png' },
];
// Порядок фраз сценария: номер строки субтитров (T.caps[].line) = номер фразы с единицы.
const ORDER = ['hook', 'five', 'c1', 'mix', 'mix2', 'c2', 'luts', 'c3', 'lot', 'c4', 'ph', 'c5', 'rb', 'how', 'share', 'cta'];

const rnd = (seed) => { const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const ic = (name, cls = '', set = 'r') => `<svg class="ic ${cls}" viewBox="0 0 256 256" fill="currentColor">${(set === 'b' ? BOLD : ICONS)[name]}</svg>`;
const CLAUDE = '<svg viewBox="0 0 24 24"><path d="M12 1.5l1.6 7.1 6.4-3.6-3.6 6.4 7.1 1.6-7.1 1.6 3.6 6.4-6.4-3.6L12 22.5l-1.6-7.1-6.4 3.6 3.6-6.4L.5 12l7.1-1.6L4 4l6.4 3.6z"/></svg>';
const CURSOR = '<svg class="cur" viewBox="0 0 32 32"><path d="M5 3l20 12.5-8.6 1.8 5 9.4-3.7 2-5-9.4L6.5 26z" fill="#F1F2EA" stroke="#12130F" stroke-width="1.8" stroke-linejoin="round"/></svg>';
const sc = (id, T) => T.scenes[id];
// Видео: время на самом теге, относительно начала ролика. Звук у клипов вырезан.
let TRACK = 2;
const vid = (A, file, from, to, cls = '', style = '') =>
  `<video id="v${TRACK}" class="vd ${cls}" src="${A}/clips/${file}" muted playsinline data-start="${from.toFixed(2)}" data-duration="${Math.max(0.5, to - from).toFixed(2)}" data-track-index="${TRACK++}" style="${style}"></video>`;
const wave = (top, n = 58, cls = '') => `<div class="wave ${cls}" style="top:${top}px">${Array.from({ length: n }, (_, i) =>
  `<i style="height:${Math.round(10 + 64 * rnd(i + 3) * (0.35 + 0.65 * Math.abs(Math.sin(i * 0.4))))}px"></i>`).join('')}<b></b></div>`;
// Барабан цифр: в окне столбец 0–9 (для крутки — дважды), цифра встаёт прокруткой столбца.
const drum = (digits, cls = '') => `<span class="drum ${cls}">${[...digits].map((d) => /\d/.test(d)
  ? `<span class="dcol"><span class="dstrip" data-layout-ignore>${'01234567890123456789'.split('').map((x) => `<i>${x}</i>`).join('')}</span></span>`
  : `<span class="dsep">${d}</span>`).join('')}</span>`;

const editor = (A, id, clips, shown = false) => `<div class="editor glass ${shown ? '' : 'h'}" id="${id}">
  <div class="eui">
    <div class="ebar">${ic('play', 'eic')}<span class="tc mono">00:00:00:<b class="fr">14</b></span>${ic('scissors', 'eic')}</div>
    <div class="trk v">${clips.map((c) => `<div class="clip ${c.cls || ''}" style="width:${c.w}px">${c.img ? `<img src="${A}/${c.img}">` : ''}<span>${c.t || ''}</span></div>`).join('')}</div>
    <div class="trk v2"><div class="clip" style="width:300px"><img src="${A}/lc3.jpg"></div><div class="clip" style="width:190px"><img src="${A}/rezhisser.jpg"></div><div class="clip" style="width:230px"><img src="${A}/g3.jpg"></div></div>
    <div class="trk a">${Array.from({ length: 70 }, (_, i) => `<i style="height:${Math.round(14 + 50 * rnd(i + 70) * (0.4 + 0.6 * Math.abs(Math.sin(i * 0.33))))}px"></i>`).join('')}</div>
    <div class="head"><b></b><i></i></div>
  </div>
</div>`;

const GRID = ['video-camera', 'music-note', 'film-strip', 'waveform', 'speaker-high', 'image', 'camera', 'sparkle', 'star', 'heart',
  'check-circle', 'arrow-bend-up-right', 'smiley', 'paper-plane-tilt', 'play', 'scissors', 'magic-wand', 'palette', 'sun', 'moon',
  'lightning', 'rocket', 'bell', 'gift', 'cat', 'folder', 'download-simple', 'cloud', 'gear', 'pencil-simple', 'eye', 'fire',
  'crown', 'trophy', 'map-pin', 'chat-circle', 'music-notes', 'headphones', 'microphone', 'film-slate', 'cursor-click', 'lightbulb',
  'aperture', 'monitor-play', 'film-reel'];

/** Разметка всех сцен. A — адрес папки с картинками, T — раскладка (видео нужно знать своё время). */
export const markup = (A, T) => {
  TRACK = 2;
  const S = (id) => sc(id, T).s, E = (id) => sc(id, T).e;
  return `
<script src="${A}/lottie_light.min.js"><\/script>
<div class="bg bg-light"></div>
${['lime', 'amber', 'violet', 'warm', 'gold', 'blue', 'mint', 'lilac'].map((g) => `<div class="glow glow-${g}" data-layout-ignore${g === 'lime' ? ' style="opacity:1"' : ''}><i></i></div>`).join('')}
<div class="vignette" style="opacity:1"></div>

<div class="sc" id="sc-hook" style="opacity:1">
  <div class="floats abs" data-layout-ignore style="inset:0">
    <div class="float" style="left:-110px;top:420px;width:380px;height:240px;transform:rotate(-8deg)"><img src="${A}/rezhisser.jpg"></div>
    <div class="float" style="left:810px;top:400px;width:400px;height:250px;transform:rotate(7deg)"><img src="${A}/lc3.jpg"></div>
    <div class="float" style="left:-90px;top:1300px;width:420px;height:280px;transform:rotate(9deg)"><img src="${A}/g3.jpg"></div>
    <div class="float" style="left:770px;top:1290px;width:420px;height:280px;transform:rotate(-8deg)"><img src="${A}/reactbits-pc.jpg" style="object-position:0 0"></div>
  </div>
  <div class="kbd abs h" data-layout-ignore><div class="keys">${'<i></i>'.repeat(36)}</div></div>
  <div class="morph abs" id="mph">
    ${editor(A, 'ed1', [{ w: 150, img: 'teaser/t1.jpg' }, { w: 220, img: 'lc0.jpg' }, { w: 150, img: 'teaser/t5.jpg' }, { w: 200, img: 'mixkit-ph.jpg' }], true)}
    <div class="scr abs">${[1, 2, 3, 4, 5, 6, 7].map((k) => `<img class="tz tz${k}" src="${A}/teaser/t${k}.jpg">`).join('')}</div>
    <div class="empty abs"></div>
  </div>
  <div class="cpill pill h"><s>${CLAUDE}</s>Claude Code</div>
  <div class="tray glass abs h">${['film-strip', 'music-note', 'image', 'sparkle', 'cursor-click'].map((n) => `<div class="slot2">${ic(n)}</div>`).join('')}</div>
</div>

<div class="sc" id="sc-five">
  <div class="big fbig" style="top:300px">${drum('5', 'd5')}</div>
  <div class="cap" style="top:600px"><span class="h">бесплатных</span> <span class="h">сайтов</span></div>
  <div class="brw abs h" style="left:140px;top:760px;width:800px">
    <div class="tabs">${SITES.map((p, k) => `<div class="tab h t${k}"><img src="${A}/${p.logo}"><span>${p.name}</span></div>`).join('')}</div>
    <div class="bar"><i></i><i></i><i></i><div class="url">mixkit.co</div></div>
    <div class="brwimg"><img src="${A}/mixkit-pc.jpg"></div>
  </div>
  <div class="cursor abs h" style="left:0;top:0">${CURSOR}</div>
</div>

<div class="sc light" id="sc-c1">
  <div class="floats abs" data-layout-ignore style="inset:0">
    <div class="vt lf" style="left:-60px;top:560px;width:300px;height:400px">${vid(A, 'road-v.mp4', S('c1'), E('c1'))}</div>
    <div class="vt lf" style="left:840px;top:500px;width:280px;height:380px">${vid(A, 'sea-v.mp4', S('c1'), E('c1'))}</div>
    <div class="vt lf" style="left:830px;top:1000px;width:300px;height:200px"><img src="${A}/lc3.jpg"></div>
    <div class="vt lf" style="left:-70px;top:1060px;width:300px;height:200px"><img src="${A}/g1.jpg"></div>
  </div>
  <div class="ph2 abs h" style="left:360px;top:470px"><div class="phone white"><img class="scroll" src="${A}/mixkit-ph.jpg"></div></div>
  ${wave(1250, 58, 'blue')}
</div>

<div class="sc light" id="sc-mix">
  <div class="mcard abs h" style="left:140px;top:470px;width:800px;height:450px">
    ${vid(A, 'music.mp4', S('mix'), E('mix'), 'm1')}
    ${vid(A, 'sea-v.mp4', S('mix'), E('mix'), 'm2', 'opacity:0;object-fit:cover')}
    <div class="mbar"><div class="play">${ic('play', '', 'b')}</div>${wave(0, 40, 'mini')}</div>
  </div>
  <div class="stat s1 pill h" style="left:140px;top:960px">${ic('music-note', '', 'b')}${drum('1000', 'd1')}<em>+ треков</em></div>
  <div class="stat s2 pill h" style="left:560px;top:960px">${ic('waveform', '', 'b')}${drum('3000', 'd2')}<em>+ звуков</em></div>
  <div class="abs" style="left:-80px;top:1080px;width:1240px"><div style="transform:rotate(-3deg)"><div class="film strip h" data-layout-ignore style="height:200px">${
    ['lc0.jpg', 'rezhisser.jpg', 'g3.jpg', 'teaser/t2.jpg', 'g1.jpg', 'lc3.jpg', 'g2.jpg', 'teaser/t6.jpg'].map((f) => `<div class="cell" style="width:240px"><img src="${A}/${f}" style="width:100%;height:100%;object-fit:cover;border-radius:0"></div>`).join('')}</div></div></div>
  <div class="stat s3 pill h" style="left:290px;top:1330px">${ic('film-strip', '', 'b')}${drum('46000', 'd3')}<em>+ видео</em></div>
</div>

<div class="sc light" id="sc-mix2">
  <div class="bezel abs h" style="left:140px;top:520px;width:800px">
    <div class="core">
      <img class="mlogo" src="${A}/mixkit.png">
      <div class="trow t1">${ic('cursor-click', 'ti')}<span>Коммерция</span><div class="tog"><i></i></div></div>
      <div class="trow t2">${ic('user', 'ti')}<span>Без указания автора</span><div class="tog"><i></i></div></div>
    </div>
  </div>
  <div class="ftypes">${['file-video', 'file-audio', 'waveform', 'film-slate', 'music-note'].map((n) => `<div class="ft h">${ic(n, '', 'b')}<u></u></div>`).join('')}</div>
  <div class="cursor abs h" style="left:0;top:0">${CURSOR}</div>
</div>

<div class="sc" id="sc-c2">
  <div class="laptop abs h" style="left:110px;top:500px"><div class="lscr"><img class="lsimg" src="${A}/freshluts-pc.jpg"></div><div class="lbase"></div></div>
  <div class="swatches">${[0, 1, 2, 3, 4].map((k) => `<div class="sw h"><img src="${A}/lc${k}.jpg"></div>`).join('')}</div>
  <div class="dl pill h" style="left:330px;top:1290px">${ic('download-simple', '', 'b')}3 млн скачиваний</div>
  <div class="cursor abs h" style="left:0;top:0">${CURSOR}</div>
</div>

<div class="sc" id="sc-luts">
  <div class="photo abs h" style="left:110px;top:500px;width:860px;height:574px">
    ${vid(A, 'lut-a.mp4', S('luts'), E('luts'), 'la')}
    <div class="split abs">${vid(A, 'lut-b.mp4', S('luts'), E('luts'), 'lb')}</div>
    <div class="sline abs"></div>
    <div class="curve glass abs"><svg viewBox="0 0 200 130"><path class="cv" d="M14 116 C 70 116, 90 30, 186 14" fill="none" stroke="#F2B24A" stroke-width="5" stroke-linecap="round"/><circle class="cvd" cx="104" cy="58" r="7" fill="#F1F2EA"/></svg></div>
  </div>
  <div class="lname pill h"><s>${ic('palette', '', 'b')}</s><b class="ln0">Original</b><b class="ln1">Vintage</b><b class="ln2">Cross</b><b class="ln4">Noir</b><b class="ln3">Blockbuster</b></div>
  <div class="chiprow">${[0, 1, 2, 4, 3].map((k) => `<div class="gc h c${k}"><img src="${A}/lc${k}.jpg"><u></u></div>`).join('')}</div>
  <div class="cursor abs h" style="left:0;top:0">${CURSOR}</div>
</div>

<div class="sc light" id="sc-c3">
  <div class="lotpath abs" data-layout-ignore id="lp" style="left:40px;top:1000px;width:1000px;height:460px"></div>
  <div class="bezel abs h lcard" style="left:200px;top:480px;width:680px">
    <div class="core lgrid">${['heart', 'star', 'bell', 'rocket', 'music-note', 'arrow-bend-up-right', 'check-circle', 'smiley', 'paper-plane-tilt', 'gift', 'sparkle', 'fire']
      .map((n, k) => `<div class="lt h" style="--c:${['#7BE3C8', '#F3D9A0', '#CDEB9A', '#F6CBBE'][k % 4]}">${ic(n)}</div>`).join('')}</div>
  </div>
</div>

<div class="sc light" id="sc-lot">
  <div class="tiles">${['arrow', 'check', 'smile'].map((k) => `<div class="tl h" id="tl-${k}"><div class="lot" id="lot-${k}"></div></div>`).join('')}</div>
  <div class="keys2 h"><div class="krail">${Array.from({ length: 6 }, (_, k) => `<i style="left:${40 + k * 116}px"></i>`).join('')}</div><b class="kph"></b></div>
  <div class="comm pill h" style="left:50%;top:1080px;transform:translateX(-50%)">${ic('check-circle', '', 'b')}можно в коммерцию</div>
</div>

<div class="sc light" id="sc-c4">
  <div class="pgrid" data-layout-ignore>${Array.from({ length: 54 }, (_, k) => `<div class="pg">${ic(GRID[k % GRID.length])}</div>`).join('')}</div>
  <div class="search pill h" style="left:200px;top:470px">${ic('magic-wand', '', 'b')}<span>Search 1 512 icons</span><em>Regular</em></div>
  <div class="bezel abs h pcard" style="left:330px;top:660px;width:420px">
    <div class="core" style="padding:40px;text-align:center"><img src="${A}/phosphor.png" style="width:180px;height:180px;border-radius:46px;margin:0 auto"><div class="pname">Phosphor</div><div class="purl">phosphoricons.com</div></div>
  </div>
</div>

<div class="sc" id="sc-ph">
  <div class="big pbig" style="top:300px">${drum('1 200', 'd12')}<span class="plus">+</span></div>
  <div class="cap" style="top:540px"><span class="h">иконок</span> <span class="h">в</span> <span class="h">одном</span> <span class="h" style="color:#C9A8FF">стиле</span></div>
  <div class="wbox glass h">${Object.keys(CAT_WEIGHTS).map((k) => `<svg class="wcat w-${k}" viewBox="0 0 256 256" fill="currentColor">${CAT_WEIGHTS[k]}</svg>`).join('')}</div>
  <div class="wnames">${Object.keys(CAT_WEIGHTS).map((k) => `<span class="h wn-${k}">${k[0].toUpperCase() + k.slice(1)}</span>`).join('')}</div>
  <div class="p3 abs" style="left:0;top:1110px;width:1080px;height:300px"><div class="dgrid" data-layout-ignore>${Array.from({ length: 40 }, (_, k) => `<div class="dg">${ic(GRID[(k * 7) % GRID.length])}</div>`).join('')}</div></div>
</div>

<div class="sc light" id="sc-c5">
  <div class="laptop abs h" style="left:110px;top:500px"><div class="lscr"><img src="${A}/reactbits-pc.jpg"></div><div class="lbase light"></div></div>
  <div class="fx">${['linear-gradient(135deg,#B58CFF,#5B2EB8)', 'radial-gradient(circle at 30% 30%,#F1F2EA,#9C7BFF 60%,#2A1A55)', 'repeating-linear-gradient(115deg,#1B1530 0 14px,#7B52E0 14px 28px)', 'linear-gradient(160deg,#D97757,#1B1530)']
    .map((b) => `<div class="fxt h" style="background:${b}"></div>`).join('')}</div>
</div>

<div class="sc light" id="sc-rb">
  <div class="tags">${['BlurText', 'ShinyText', 'Particles'].map((t, k) => `<div class="tag2 pill h t${k}">${ic(['sparkle', 'magic-wand', 'star'][k], '', 'b')}${t}</div>`).join('')}</div>
  <div class="frame abs h">${vid(A, 'sunset-v.mp4', S('rb'), E('rb'), 'fv')}<div class="fshade abs"></div>
    <div class="ftitle">${[...'Закат'].map((c) => `<span class="ch">${c}</span>`).join('')}<div class="shine abs"></div></div>
    <div class="sparks abs">${Array.from({ length: 24 }, (_, k) => `<i class="spk" style="left:${Math.round(30 + rnd(k + 9) * 380)}px;top:${Math.round(40 + rnd(k + 51) * 560)}px;width:${8 + Math.round(rnd(k + 3) * 10)}px;height:${8 + Math.round(rnd(k + 3) * 10)}px"></i>`).join('')}</div>
  </div>
</div>

<div class="sc" id="sc-how">
  <div class="prompt2 glass h"><s>${CLAUDE}</s><span class="ptext">${[...'вставь в ролик'].map((c) => `<span class="ch">${c}</span>`).join('')}</span><u></u></div>
  <div class="file pill h">${ic('file-video', '', 'b')}clip.mp4</div>
  ${editor(A, 'ed2', [{ w: 150, img: 'teaser/t1.jpg' }, { w: 130, img: 'lc1.jpg', cls: 'pre' }, { w: 0, img: 'lc3.jpg', cls: 'ins', t: 'clip.mp4' }, { w: 170, img: 'teaser/t4.jpg', cls: 'post' }, { w: 150, img: 'mixkit-ph.jpg', cls: 'post' }])}
  <div class="cursor abs h" style="left:0;top:0">${CURSOR}</div>
</div>

<div class="sc" id="sc-share">
  <div class="scat abs h" style="left:60px;top:600px;width:440px"><img src="${A}/cat-share.png" style="width:100%"></div>
  <div class="sheet2 glass h">
    <div class="sh-t">Поделиться</div>
    ${[['Монтажёр', '#C7E24B'], ['Дима · клипы', '#E9D7A8'], ['Аня · reels', '#D97757']].map(([n, c], k) => `<div class="who w${k}"><i style="background:${c}">${ic('user', '', 'b')}</i><span>${n}</span><b class="ok">${ic('check', '', 'b')}</b></div>`).join('')}
    <div class="send">${ic('paper-plane-tilt', '', 'b')}Отправить</div>
  </div>
  <div class="plane abs h">${ic('paper-plane-tilt', '', 'b')}</div>
  <div class="cursor abs h" style="left:0;top:0">${CURSOR}</div>
</div>

<div class="sc" id="sc-cta">
  <div class="rays abs" data-layout-ignore></div>
  <div class="chest abs h" style="left:230px;top:600px;width:620px"><img src="${A}/cat-chest.png" style="width:100%"></div>
  <div class="tgc h" style="left:470px;top:450px">${ic('telegram-logo', '', 'r')}</div>
  ${SITES.map((p, k) => `<div class="fly h f${k}"><img src="${A}/${p.logo}"></div>`).join('')}
  <div class="go h" style="top:1240px"><span>Ссылка в профиле<div class="shim"></div></span></div>
  <div class="save h" style="top:1370px"><span>${ic('bookmark-simple', '', 'b')}Сохрани, чтобы не потерять</span></div>
  <div class="cursor abs h" style="left:0;top:0">${CURSOR}</div>
</div>
`;
};

// Заголовок: фраза кусками. Для каждой фразы — куски [слов в первой строке, слов во второй].
// Слова и их время берутся из субтитров раскладки (текст «на экране»), без точки в конце.
const SEGS = {
  hook: [[1, 3], [2, 3], [2, 4]], mix: [[2, 3]], mix2: [[3, 3]], luts: [[2, 0], [4, 3]],
  lot: [[2, 0], [2, 1], [1, 3]], rb: [[2, 5]], how: [[2, 2], [3, 4]], share: [[1, 1], [2, 0]], cta: [[4, 4]],
};
// Названия сайтов: знак и имя; слово «Первый» голос говорит, на экране только имя.
const NAMES = { c1: 0, c2: 1, c3: 2, c4: 3, c5: 4 };

export const headlines = (T) => {
  const lines = new Map();
  T.caps.forEach((c) => lines.set(c.line, [...(lines.get(c.line) || []), c]));
  const out = [];
  ORDER.forEach((id, n) => {
    const ws = (lines.get(n + 1) || []).map((c) => ({ w: c.w.replace(/[.!]$/, ''), s: c.s }));
    const s = T.scenes[id].s, e = T.scenes[id].e;
    const light = ['c1', 'mix', 'mix2', 'c3', 'lot', 'c4', 'c5', 'rb'].includes(id);
    if (id in NAMES) {
      const p = SITES[NAMES[id]];
      out.push({ id, light, from: s, to: e, name: p, at: ws[1] ? ws[1].s : s + 0.3 });   // время первого слова названия
      return;
    }
    if (!SEGS[id]) return;
    let k = 0;
    SEGS[id].forEach(([a, b], j) => {
      const l1 = ws.slice(k, k + a), l2 = ws.slice(k + a, k + a + b);
      k += a + b;
      const next = SEGS[id][j + 1] ? ws[k] : null;
      out.push({ id, light, from: j === 0 ? s : l1[0].s - 0.08, to: next ? next.s - 0.1 : e, l1, l2, first: id === 'hook' && j === 0 });
    });
  });
  return out;
};

// Время Lottie считается от начала ролика: начало анимации вшивается в её слои.
const shiftLottie = (data, sec) => {
  const d = JSON.parse(JSON.stringify(data));
  const f = sec * d.fr;
  d.layers.forEach((l) => { l.ip += f; l.op += f; l.st = (l.st || 0) + f; });
  d.op += f;
  return d;
};

/** Таймлайн сцен. tl — пустой таймлайн на паузе, root — блок с разметкой markup(). */
export const buildScenes = (gsap, tl, root, T) => {
  const $ = (sel, from = root) => from.querySelector(sel);
  const $$ = (sel, from = root) => [...from.querySelectorAll(sel)];
  const s = (id) => T.scenes[id].s;
  const e = (id) => T.scenes[id].e;
  const w = (id, i) => T.w[id][i];
  const L = T.length;
  const REST = { x: 0, y: 0, scale: 1, rotation: 0, rotationY: 0, rotationX: 0, filter: 'blur(0px)' };
  const inn = (el, t, from = { y: 40 }, duration = 0.5, ease = 'power3.out') => {
    const to = { opacity: 1, duration, ease };
    Object.keys(from).forEach((k) => { to[k] = REST[k]; });
    return tl.fromTo(el, { opacity: 0, ...from }, to, t);
  };
  const out = (el, t, duration = 0.25) => tl.to(el, { opacity: 0, duration, ease: 'power2.in' }, t);
  const pop = (el, t) => { tl.set(el, { transformOrigin: '50% 50%' }, 0); return inn(el, t, { scale: 0.8, y: 16 }, 0.4, 'back.out(1.25)'); };
  const word = (el, t) => inn(el, t - 0.06, { y: 18, filter: 'blur(10px)' }, 0.3);
  const draw = (el, t, duration, ease = 'power2.inOut') => {
    const len = el.getTotalLength();
    return tl.fromTo(el, { strokeDasharray: len, strokeDashoffset: len }, { strokeDashoffset: 0, duration, ease }, t);
  };
  const sweep = (el, t, duration = 1.0) => tl.fromTo(el, { '--sp': '-25%' }, { '--sp': '125%', duration, ease: 'power2.inOut' }, t);
  // Барабан: каждая цифра крутится на полный оборот и встаёт на свою; правые крутятся дольше.
  const spin = (drumEl, digits, t, dur = 0.8) => {
    const cols = $$('.dstrip', drumEl), ds = [...digits].filter((c) => /\d/.test(c));
    cols.forEach((col, i) => {
      const target = 10 + Number(ds[i]);
      tl.fromTo(col, { yPercent: 0 }, { yPercent: -(target / 20) * 100, duration: dur + i * 0.12, ease: 'power3.out' }, t);
      tl.fromTo(col, { filter: 'blur(6px)' }, { filter: 'blur(0px)', duration: dur * 0.8 + i * 0.12, ease: 'power2.in' }, t);
    });
  };
  const cursorTo = (el, pts) => {
    pts.forEach(([x, y, t, click], k) => {
      if (k === 0) tl.fromTo(el, { opacity: 0, x: x + 50, y: y + 70 }, { opacity: 1, x, y, duration: 0.25, ease: 'power2.out' }, t);
      else tl.to(el, { x, y, duration: Math.max(0.15, t - pts[k - 1][2] - 0.05), ease: 'power2.inOut' }, pts[k - 1][2] + 0.05);
      if (click) tl.to(el, { scale: 0.82, duration: 0.07, ease: 'power2.out', yoyo: true, repeat: 1, transformOrigin: '10% 10%' }, t);
    });
  };

  // Сцены: входят из глубины, уходят «пролётом камеры» — растут и размываются. Внутри блока сайта
  // переходы короче и спокойнее, между сайтами — пролёт.
  const CONT = ['hook', 'five', 'c1', 'mix', 'mix2', 'c2', 'luts', 'c3', 'lot', 'c4', 'ph', 'c5', 'rb', 'how', 'share', 'cta'];
  const FLY = new Set(['five', 'mix2', 'luts', 'lot', 'ph', 'rb', 'how', 'share']);
  const SC = {};
  CONT.forEach((id, n) => {
    const el = $('#sc-' + id);
    SC[id] = el;
    if (n > 0) tl.fromTo(el, { opacity: 0, scale: 0.86, filter: 'blur(14px)' }, { opacity: 1, scale: 1, filter: 'blur(0px)', duration: 0.42, ease: 'expo.out' }, s(id) - 0.04);
    if (id !== 'cta') {
      const end = e(id);
      if (FLY.has(id)) tl.to(el, { opacity: 0, scale: 1.3, filter: 'blur(18px)', duration: 0.3, ease: 'power2.in' }, end - 0.24);
      else tl.to(el, { opacity: 0, scale: 1.06, filter: 'blur(12px)', duration: 0.26, ease: 'power2.in' }, end - 0.2);
    }
  });

  // Свет: у каждого блока свой цвет. Светлые блоки — сайты, где у автора светлые сцены.
  const bgL = $('.bg-light'), vig = $('.vignette');
  const G = (n) => $('.glow-' + n);
  const BLOCKS = [['hook', 0, 'lime'], ['c1', 1, 'blue'], ['c2', 0, 'amber'], ['c3', 1, 'mint'], ['c4', 1, 'lilac'], ['ph', 0, 'violet'],
    ['c5', 1, 'lilac'], ['how', 0, 'warm'], ['share', 0, 'lime'], ['cta', 0, 'gold']];
  BLOCKS.forEach(([id, light, g], k) => {
    if (k === 0) return;
    const t = s(id) - 0.08, prev = BLOCKS[k - 1];
    if (prev[1] !== light) tl.to(bgL, { opacity: light ? 1 : 0, duration: 0.35, ease: 'power2.out' }, t);
    tl.to(vig, { opacity: light ? 0 : 1, duration: 0.35 }, t);
    if (prev[2] !== g) { tl.to(G(prev[2]), { opacity: 0, duration: 0.35 }, t); tl.to(G(g), { opacity: 1, duration: 0.5 }, t); }
  });
  $$('.glow i').forEach((el, i) => tl.fromTo(el, { scale: 0.95 }, { scale: 1.06, duration: 2.6 + i * 0.3, ease: 'sine.inOut', yoyo: true, repeat: Math.max(0, Math.floor(L / (2.6 + i * 0.3)) - 1) }, 0));

  const editorRun = (ed, a, b) => {
    tl.fromTo($('.head', ed), { x: 0 }, { x: 680, duration: b - a, ease: 'none' }, a);
    tl.fromTo($('.fr', ed), { textContent: 14 }, { textContent: 14 + Math.round((b - a) * 30), duration: b - a, ease: 'none', snap: { textContent: 1 } }, a);
  };
  const waveRun = (sc, a, b) => tl.fromTo($('.wave b', sc), { x: 30 }, { x: 670, duration: b - a, ease: 'none' }, a);

  // 1. Крючок. Стол живёт с первого кадра, на «этот ролик» он сжимается в телефон, на экране
  // мелькают кадры этого же ролика; на «но материалы» экран пустеет, снизу пустые места.
  {
    const sc = SC.hook, morphAt = w('hook', 4) - 0.12, emptyAt = w('hook', 9) - 0.05;
    tl.fromTo($('.floats', sc), { scale: 1.12 }, { scale: 1, duration: morphAt, ease: 'power1.out' }, 0);
    editorRun($('#ed1', sc), 0, morphAt + 0.3);
    tl.fromTo($('#mph', sc), { y: 30 }, { y: 0, duration: 1.0, ease: 'power2.out' }, 0);
    // одна форма: прямоугольник стола становится телефоном
    // маской, а не размерами: left/top/width дёргаются по целым пикселям, маска нет
    tl.fromTo($('#mph', sc), { clipPath: 'inset(80px 0px 90px 0px round 40px)' }, { clipPath: 'inset(0px 270px 0px 270px round 54px)', duration: 0.55, ease: 'power3.inOut' }, morphAt);
    tl.to($('#ed1 .eui', sc), { opacity: 0, scale: 0.9, duration: 0.25 }, morphAt);
    tl.to($('.scr', sc), { opacity: 1, duration: 0.25 }, morphAt + 0.25);
    const tz = $$('.tz', sc), step = Math.max(0.16, (emptyAt - morphAt - 0.35) / tz.length);
    tz.forEach((img, k) => tl.set(img, { opacity: 1 }, morphAt + 0.3 + k * step));
    inn($('.kbd', sc), morphAt + 0.2, { y: 60 }, 0.5);
    pop($('.cpill', sc), w('hook', 8) - 0.12);
    tl.to($('.scr', sc), { opacity: 0, filter: 'blur(10px)', duration: 0.3 }, emptyAt);
    tl.fromTo($('.empty', sc), { opacity: 0 }, { opacity: 1, duration: 0.3 }, emptyAt + 0.1);
    out($('.cpill', sc), emptyAt, 0.2);
    out($('.kbd', sc), emptyAt, 0.25);
    inn($('.tray', sc), emptyAt + 0.1, { y: 60 }, 0.45);
    $$('.slot2', sc).forEach((el, k) => tl.fromTo(el, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.3, ease: 'back.out(1.6)' }, emptyAt + 0.25 + k * 0.07));
    $$('.slot2', sc).forEach((el, k) => tl.to(el, { borderColor: 'rgba(199,226,75,.9)', duration: 0.2, yoyo: true, repeat: 1 }, w('hook', 14) - 0.2 + k * 0.05));
  }

  // 2. Пять: барабан, слова, вкладки встают, курсор открывает первую.
  {
    const sc = SC.five, t = s('five');
    spin($('.d5', sc), '5', w('five', 1) - 0.25, 0.7);
    tl.fromTo($('.fbig', sc), { scale: 0.8 }, { scale: 1, duration: 0.7, ease: 'expo.out' }, t);
    $$('.cap span', sc).forEach((el, i) => word(el, w('five', 2 + i)));
    inn($('.brw', sc), w('five', 3), { y: 120, rotationX: 20 }, 0.55);
    $$('.tab', sc).forEach((el, k) => inn(el, w('five', 4) + k * 0.07, { y: 20 }, 0.3));
    cursorTo($('.cursor', sc), [[900, 1300, w('five', 5)], [250, 800, e('five') - 0.35, true]]);
    tl.to($('.t0', sc), { backgroundColor: '#FFFFFF', color: '#12130F', duration: 0.15 }, e('five') - 0.32);
  }

  // 3. Mixkit: телефон со страницей, вокруг живые клипы стока.
  {
    const sc = SC.c1, t = s('c1'), end = e('c1');
    inn($('.ph2', sc), t + 0.02, { y: 140, rotation: 4 }, 0.55);
    tl.fromTo($('.scroll', sc), { y: 0 }, { y: -90, duration: end - t, ease: 'power1.inOut' }, t);
    $$('.lf', sc).forEach((el, k) => tl.fromTo(el, { y: 50 * (k % 2 ? 1 : -1), opacity: 0 }, { y: -20 * (k % 2 ? 1 : -1), opacity: 1, duration: end - t, ease: 'power1.out' }, t));
    waveRun(sc, t, end);
  }

  // Музыка, звуки, видео: в карточке играет клип, на «стоковое видео» он сменяется морем.
  {
    const sc = SC.mix, t = s('mix'), end = e('mix');
    inn($('.mcard', sc), t, { y: 70, scale: 0.94 }, 0.5);
    waveRun(sc, t, end);
    pop($('.s1', sc), w('mix', 0) - 0.08); spin($('.d1', sc), '1000', w('mix', 0), 0.6);
    pop($('.s2', sc), w('mix', 1) - 0.08); spin($('.d2', sc), '3000', w('mix', 1), 0.6);
    tl.to($('.m2', sc), { opacity: 1, duration: 0.3 }, w('mix', 3) - 0.1);
    inn($('.strip', sc), w('mix', 3) - 0.15, { y: 90 }, 0.45);
    tl.fromTo($('.strip', sc), { x: 0 }, { x: -320, duration: end - t, ease: 'none' }, t);
    pop($('.s3', sc), w('mix', 4) - 0.05); spin($('.d3', sc), '46000', w('mix', 4), 0.6);
  }

  // Можно в коммерцию: курсор включает тумблеры на своих словах, вторая строка выезжает.
  {
    const sc = SC.mix2, t = s('mix2'), t1 = w('mix2', 2), t2 = w('mix2', 5);
    inn($('.bezel', sc), t, { y: 70, scale: 0.94 }, 0.5);
    tl.set($('.t2', sc), { opacity: 0, y: 30 }, 0);
    tl.to($('.t2', sc), { opacity: 1, y: 0, duration: 0.3, ease: 'power3.out' }, w('mix2', 3) - 0.1);
    cursorTo($('.cursor', sc), [[900, 1150, t + 0.15], [805, 726, t1, true], [805, 848, t2, true], [900, 1250, t2 + 0.4]]);
    [['.t1', t1], ['.t2', t2]].forEach(([r, at]) => {
      tl.to($(r + ' .tog', sc), { backgroundColor: '#3B82F6', duration: 0.18 }, at);
      tl.to($(r + ' .tog i', sc), { x: 52, duration: 0.22, ease: 'back.out(1.6)' }, at);
    });
    $$('.ft', sc).forEach((el, k) => inn(el, t + 0.3 + k * 0.06, { y: 40, scale: 0.85 }, 0.4, 'back.out(1.2)'));
    $$('.ft u', sc).forEach((el, k) => tl.fromTo(el, { opacity: 0, scale: 0 }, { opacity: 1, scale: 1, duration: 0.2, ease: 'back.out(2)' }, t2 + 0.1 + k * 0.05));
  }

  // 4. FreshLUTs: ноутбук, страница едет, курсор листает, ряд цветов, число скачиваний.
  {
    const sc = SC.c2, t = s('c2'), end = e('c2');
    inn($('.laptop', sc), t, { y: 120, rotationX: 18 }, 0.55);
    tl.fromTo($('.lsimg', sc), { y: 0 }, { y: -60, duration: end - t, ease: 'power1.inOut' }, t);
    $$('.sw', sc).forEach((el, k) => inn(el, t + 0.3 + k * 0.06, { y: 30 }, 0.35));
    cursorTo($('.cursor', sc), [[900, 1200, t + 0.2], [420, 820, end - 0.5, true]]);
    pop($('.dl', sc), w('c2', 1));
  }

  // Цвет: живой кадр дороги, курсор перебирает таблицы, на «клик» шторка открывает «Blockbuster».
  {
    const sc = SC.luts, t = s('luts'), click = w('luts', 8);
    inn($('.photo', sc), t, { y: 80, scale: 0.94 }, 0.5);
    inn($('.lname', sc), t + 0.25, { y: 30 }, 0.35);
    const chipsEl = $$('.gc', sc);
    chipsEl.forEach((el, k) => inn(el, t + 0.2 + k * 0.05, { y: 30 }, 0.35));
    tl.set($$('.lname b', sc), { opacity: 0 }, 0); tl.set($('.ln0', sc), { opacity: 1 }, 0);
    const name = (k, at) => {
      $$('.lname b', sc).forEach((b) => tl.to(b, { opacity: b.classList.contains('ln' + k) ? 1 : 0, duration: 0.12 }, at));
      chipsEl.forEach((c) => tl.to($('u', c), { opacity: c.classList.contains('c' + k) ? 1 : 0, duration: 0.12 }, at));
    };
    // курсор водит по ряду: Vintage, Cross, Noir — и щёлкает Blockbuster
    const X = { 1: 372, 2: 540, 4: 708, 3: 876 };
    cursorTo($('.cursor', sc), [[900, 1420, t + 0.2], [X[1], 1240, w('luts', 2)], [X[2], 1240, w('luts', 4)], [X[4], 1240, w('luts', 6)], [X[3], 1240, click, true], [940, 1420, click + 0.5]]);
    name(1, w('luts', 2)); name(2, w('luts', 4)); name(4, w('luts', 6)); name(3, click);
    tl.set($('.split', sc), { clipPath: 'inset(0% 100% 0% 0%)' }, 0);
    tl.to($('.split', sc), { clipPath: 'inset(0% 0% 0% 0%)', duration: 0.6, ease: 'power2.inOut' }, click + 0.03);
    tl.fromTo($('.sline', sc), { opacity: 0, x: 0 }, { opacity: 1, duration: 0.06 }, click);
    tl.to($('.sline', sc), { x: 856, duration: 0.6, ease: 'power2.inOut' }, click + 0.03);
    out($('.sline', sc), click + 0.62, 0.12);
    inn($('.curve', sc), w('luts', 3), { y: 20, scale: 0.9 }, 0.35);
    draw($('.cv', sc), w('luts', 3) + 0.05, 0.7);
    tl.fromTo($('.cvd', sc), { x: -40, y: 30 }, { x: 0, y: 0, duration: 0.7, ease: 'power2.inOut' }, w('luts', 3) + 0.05);
  }

  // 5. LottieFiles: карточка анимаций, за ней рисуется пунктирный путь — настоящая анимация с сайта.
  {
    const sc = SC.c3, t = s('c3');
    inn($('.lcard', sc), t, { y: 90, scale: 0.93 }, 0.5);
    $$('.lt', sc).forEach((el, k) => inn(el, t + 0.2 + k * 0.04, { scale: 0.6 }, 0.35, 'back.out(1.4)'));
    $$('.lt svg', sc).forEach((el, k) => tl.fromTo(el, { rotation: -8 }, { rotation: 8, duration: 0.6, ease: 'sine.inOut', yoyo: true, repeat: 1 }, t + 0.6 + (k % 4) * 0.1));
  }

  // Готовые анимации: плитки встают, каждая анимация играет на своём слове, потом «можно в коммерцию».
  {
    const sc = SC.lot, t = s('lot');
    $$('.tl', sc).forEach((el, k) => inn(el, t + 0.1 + k * 0.08, { y: 60, scale: 0.85 }, 0.45, 'back.out(1.2)'));
    inn($('.keys2', sc), t + 0.35, { y: 40 }, 0.4);
    const a = w('lot', 2), b = w('lot', 5);
    tl.fromTo($('.kph', sc), { x: 0 }, { x: 640, duration: b - a, ease: 'none' }, a);
    $$('.krail i', sc).forEach((el, k) => tl.to(el, { backgroundColor: '#14B88F', scale: 1.3, duration: 0.12 }, a + (k / 5) * (b - a)));
    [0, 1, 2].forEach((k) => tl.to($$('.tl', sc)[k], { scale: 1.08, duration: 0.15, ease: 'power2.out', yoyo: true, repeat: 1 }, w('lot', 2 + k) - 0.05));
    pop($('.comm', sc), w('lot', 6) - 0.1);
  }

  // 6. Phosphor: сетка его иконок волной, поиск, карточка со знаком.
  {
    const sc = SC.c4, t = s('c4');
    $$('.pg', sc).forEach((el, k) => tl.fromTo(el, { opacity: 0, scale: 0.6 }, { opacity: 0.55, scale: 1, duration: 0.35, ease: 'power3.out' }, t + ((k % 6) + Math.floor(k / 6)) * 0.03));
    inn($('.search', sc), t + 0.15, { y: -30 }, 0.4);
    inn($('.pcard', sc), w('c4', 1) - 0.12, { scale: 0.85, y: 40 }, 0.45, 'back.out(1.2)');
  }

  // Больше 1200 иконок в одном стиле: барабан, потом одна иконка проходит шесть начертаний.
  {
    const sc = SC.ph, t = s('ph'), end = e('ph');
    spin($('.d12', sc), '1 200', t + 0.02, 0.9);
    tl.fromTo($('.pbig', sc), { scale: 0.84 }, { scale: 1, duration: 0.8, ease: 'power3.out' }, t);
    pop($('.plus', sc), t + 1.0);
    $$('.cap span', sc).forEach((el, k) => word(el, w('ph', 3 + k)));
    inn($('.wbox', sc), t + 0.2, { y: 60, scale: 0.9 }, 0.45);
    const keys = Object.keys(CAT_WEIGHTS), step = (end - t - 0.6) / keys.length;
    keys.forEach((k, i) => {
      const at = t + 0.35 + i * step;
      tl.set($('.w-' + k, sc), { opacity: 1 }, at);
      if (i < keys.length - 1) tl.set($('.w-' + k, sc), { opacity: 0 }, at + step);
      tl.fromTo($('.wn-' + k, sc), { opacity: 0.32 }, { opacity: 1, duration: 0.1 }, at);
      if (i < keys.length - 1) tl.to($('.wn-' + k, sc), { opacity: 0.32, duration: 0.1 }, at + step);
    });
    $$('.dg', sc).forEach((el, k) => {
      const c = k % 10, r = Math.floor(k / 10);
      tl.fromTo(el, { opacity: 0, y: 30 }, { opacity: 0.6, y: 0, duration: 0.35, ease: 'power3.out' }, t + 0.1 + (c + r) * 0.03);
      tl.to(el, { color: '#C9A8FF', opacity: 1, duration: 0.18, yoyo: true, repeat: 1 }, t + 0.8 + c * 0.07 + r * 0.04);
    });
  }

  // 7. React Bits: ноутбук со страницей, плитки эффектов переливаются.
  {
    const sc = SC.c5, t = s('c5');
    inn($('.laptop', sc), t, { y: 120, rotationX: 18 }, 0.55);
    $$('.fxt', sc).forEach((el, k) => inn(el, t + 0.3 + k * 0.06, { y: 40, scale: 0.85 }, 0.4, 'back.out(1.2)'));
    $$('.fxt', sc).forEach((el, k) => tl.fromTo(el, { backgroundPosition: '0% 0%' }, { backgroundPosition: '100% 100%', duration: e('c5') - t, ease: 'none' }, t + k * 0.08));
  }

  // Эффекты для кадров: живой закат, буквы из размытия, блик, искры — приёмы React Bits твинами.
  {
    const sc = SC.rb, t = s('rb');
    inn($('.frame', sc), t, { y: 90, scale: 0.92 }, 0.5);
    $$('.ftitle .ch', sc).forEach((c, k) => tl.fromTo(c, { opacity: 0, y: 30, filter: 'blur(14px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.4, ease: 'power3.out' }, w('rb', 1) + k * 0.06));
    tl.fromTo($('.shine', sc), { xPercent: -140 }, { xPercent: 140, duration: 0.8, ease: 'power2.inOut' }, w('rb', 3));
    $$('.spk', sc).forEach((el, k) => {
      const at = w('rb', 6) - 0.3 + rnd(k + 2) * 0.4;
      tl.fromTo(el, { opacity: 0, scale: 0, rotation: 0 }, { opacity: 1, scale: 1, rotation: 90, duration: 0.3, ease: 'back.out(2)' }, at);
      tl.to(el, { opacity: 0, scale: 0.4, rotation: 180, duration: 0.4, ease: 'power1.in' }, at + 0.35);
    });
    [[0, w('rb', 1)], [1, w('rb', 3)], [2, w('rb', 6) - 0.2]].forEach(([k, at]) => pop($('.t' + k, sc), at));
  }

  // 8. Скачал, отдал Claude, он сам вставил: файл падает, курсор тащит его в промпт, клип встаёт.
  {
    const sc = SC.how, t = s('how'), ins = w('how', 7);
    const ed = $('#ed2', sc);
    inn(ed, t, { y: 100 }, 0.5);
    editorRun(ed, t, e('how'));
    inn($('.prompt2', sc), t + 0.15, { y: -40 }, 0.4);
    inn($('.file', sc), w('how', 0) - 0.05, { y: -160, scale: 0.8 }, 0.45, 'back.out(1.2)');
    const drag = w('how', 2);
    cursorTo($('.cursor', sc), [[880, 820, w('how', 1)], [640, 700, drag - 0.08, true], [550, 610, drag + 0.4], [700, 1300, ins + 0.3]]);
    tl.to($('.file', sc), { x: -90, y: -80, scale: 0.7, duration: 0.45, ease: 'power2.inOut' }, drag);
    tl.to($('.file', sc), { opacity: 0, duration: 0.15 }, drag + 0.45);
    $$('.prompt2 .ch', sc).forEach((c, k) => tl.set(c, { opacity: 1 }, drag + 0.48 + k * 0.03));
    tl.to($('.clip.ins', ed), { width: 190, duration: 0.5, ease: 'power3.inOut' }, ins);
    tl.fromTo($('.clip.ins', ed), { boxShadow: '0 0 0 0 rgba(217,119,87,0)' }, { boxShadow: '0 0 0 5px rgba(217,119,87,.9)', duration: 0.25, yoyo: true, repeat: 1 }, ins + 0.5);
  }

  // Перешли другу-монтажёру: кот протягивает самолётик, курсор выбирает «Монтажёр» и жмёт «Отправить».
  {
    const sc = SC.share, t = s('share'), send = w('share', 3);
    inn($('.scat', sc), t, { x: -140 }, 0.5);
    inn($('.sheet2', sc), t + 0.12, { y: 120 }, 0.5);
    $$('.who', sc).forEach((el, k) => inn(el, t + 0.3 + k * 0.08, { x: 40 }, 0.35));
    cursorTo($('.cursor', sc), [[900, 1300, t + 0.3], [700, 795, w('share', 1), true], [730, 1141, send, true], [900, 1320, send + 0.5]]);
    pop($('.w0 .ok', sc), w('share', 1));
    tl.to($('.send', sc), { scale: 0.94, duration: 0.07, yoyo: true, repeat: 1 }, send);
    tl.fromTo($('.plane', sc), { opacity: 0, x: 0, y: 0, rotation: -10, scale: 0.6 }, { opacity: 1, x: 540, y: -520, rotation: 20, scale: 1.1, duration: 0.8, ease: 'power2.in' }, send + 0.05);
    tl.to($('.plane', sc), { opacity: 0, duration: 0.15 }, send + 0.75);
  }

  // Призыв: сундук светится, лучи вращаются, из него вылетают пять сайтов, Telegram, потом ссылка.
  {
    const sc = SC.cta, t = s('cta');
    inn($('.chest', sc), t, { y: 140, scale: 0.9 }, 0.6);
    tl.fromTo($('.rays', sc), { opacity: 0, rotation: 0 }, { opacity: 1, rotation: 30, duration: L - t, ease: 'none' }, t + 0.2);
    tl.fromTo($('.chest img', sc), { filter: 'brightness(1) drop-shadow(0 40px 60px rgba(0,0,0,.55))' }, { filter: 'brightness(1.12) drop-shadow(0 0 60px rgba(242,178,74,.55))', duration: 0.6, ease: 'sine.inOut', yoyo: true, repeat: Math.max(1, Math.floor((L - t - 0.6) / 0.6)) }, t + 0.6);
    const P = [[110, 600], [270, 500], [700, 500], [860, 600], [120, 880]];
    $$('.fly', sc).forEach((el, k) => {
      const at = w('cta', 1) + k * 0.1;
      tl.fromTo(el, { opacity: 0, x: 470, y: 840, scale: 0.3, rotation: -30 }, { opacity: 1, x: P[k][0], y: P[k][1], scale: 1, rotation: 0, duration: 0.6, ease: 'expo.out' }, at);
      tl.to(el, { y: P[k][1] - 14, duration: 1.2, ease: 'sine.inOut', yoyo: true, repeat: Math.max(0, Math.floor((L - at - 0.6) / 1.2) - 1) }, at + 0.6);
    });
    tl.fromTo($('.tgc', sc), { opacity: 0, y: 340, scale: 0.4 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: 'expo.out' }, w('cta', 7) - 0.2);
    inn($('.go', sc), w('cta', 8) - 0.1, { y: 40, scale: 0.9 }, 0.4, 'back.out(1.2)');
    sweep($('.go span', sc), w('cta', 8) + 0.25, 0.8);
    cursorTo($('.cursor', sc), [[900, 1460, w('cta', 8)], [640, 1290, w('cta', 10) + 0.1, true], [900, 1470, w('cta', 10) + 0.6]]);
    inn($('.save', sc), w('cta', 10) + 0.3, { y: 40, scale: 0.9 }, 0.4, 'back.out(1.2)');
  }

  // Анимации LottieFiles: плеер без автозапуска, время вшито в файл, перематывает адаптер HyperFrames.
  if (typeof window !== 'undefined' && window.lottie) {
    window.__hfLottie = window.__hfLottie || [];
    const load = (id, data, at) => window.__hfLottie.push(window.lottie.loadAnimation({
      container: root.querySelector(id), renderer: 'svg', loop: false, autoplay: false, animationData: shiftLottie(data, at) }));
    load('#lot-arrow', LOTTIE.arrow, w('lot', 2) - 0.1);
    load('#lot-check', LOTTIE.check, w('lot', 3) - 0.1);
    load('#lot-smile', LOTTIE.smile, w('lot', 4) - 0.2);
    load('#lp', LOTTIE.path, s('c3'));
  }
  return tl;
};

/** Слой поверх сцен: знак канала, полоса ролика, заголовок-субтитры. */
export const overlayMarkup = (A, T) => `<div class="logo"><img src="${A}/logo.png"></div>
<div class="prog">${'<i><b></b></i>'.repeat(8)}</div>
` + headlines(T).map((h) => h.name
  ? `<div class="hl nm ${h.light ? 'light' : ''}"><div class="l1"><span class="nmi"><img src="${A}/${h.name.logo}"></span><span>${h.name.name}</span></div></div>`
  : `<div class="hl ${h.light ? 'light' : ''} ${h.first ? 'first' : ''}">${[h.l1, h.l2].map((line, k) => line.length ? `<div class="${k ? 'l2' : 'l1'}">${
    line.map((x) => `<span class="${/^Claude,?$/.test(x.w) ? 'cl' : /^Telegram/.test(x.w) ? 'tgw' : ''}">${x.w === 'пять' ? '5' : x.w}</span>`).join('')}</div>` : '').join('')}</div>`).join('');

export const buildOverlay = (gsap, tl, root, T) => {
  const s = (id) => T.scenes[id].s;
  const L = T.length;
  headlines(T).forEach((h, n) => {
    const box = root.querySelectorAll('.hl')[n];
    const spans = [...box.querySelectorAll('.l1 > span, .l2 > span')];
    if (h.name) {
      tl.fromTo(spans, { opacity: 0, y: 26, filter: 'blur(12px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.35, ease: 'expo.out', stagger: 0.06 }, Math.max(h.from, h.at - 0.12));
    } else {
      const words = [...h.l1, ...h.l2];
      spans.forEach((sp, i) => {
        // первое слово ролика стоит с нулевого кадра: это обложка
        if (h.first && i === 0) return;
        tl.fromTo(sp, { opacity: 0, y: 22, filter: 'blur(10px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.26, ease: 'power3.out' }, Math.max(h.from, words[i].s - 0.05));
      });
    }
    if (h.to < L - 0.05) tl.to(spans, { opacity: 0, filter: 'blur(10px)', duration: 0.18, ease: 'power2.in' }, h.to - 0.18);
  });

  // Полоса ролика: восемь отрезков — крючок, пять сайтов, «отдал Claude», призыв. На заставке её
  // нет: прорисовывается на смене первого кадра (стол сжимается в телефон) и идёт до самого конца.
  const prog = root.querySelector('.prog');
  const старт = T.w.hook[4] - 0.12;
  [...prog.querySelectorAll('i')].forEach((el, i) =>
    tl.fromTo(el, { opacity: 0, scaleX: 0 }, { opacity: 1, scaleX: 1, duration: 0.4, ease: 'expo.out' }, старт + 0.05 + i * 0.04));
  const части = [старт + 0.3, s('c1'), s('c2'), s('c3'), s('c4'), s('c5'), s('how'), s('cta'), L - 0.3];
  [...prog.querySelectorAll('b')].forEach((b, i) =>
    tl.fromTo(b, { scaleX: 0 }, { scaleX: 1, duration: части[i + 1] - части[i], ease: 'none' }, части[i]));
  [['c1', 1], ['c2', 0], ['c3', 1], ['ph', 0], ['c5', 1], ['how', 0]].forEach(([id, light]) =>
    tl.set(prog, { '--pf': light ? '#56690C' : '#C7E24B', '--pt': light ? 'rgba(18,19,15,.16)' : 'rgba(241,242,234,.2)' }, s(id)));
  return tl;
};
