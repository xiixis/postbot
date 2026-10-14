// Ролик «Кто монтирует эти ролики?» (r14), вторая версия. Движок один: HyperFrames, объём — Three.js (shared/three.js).
//
// Рерайт рилса @milanko.ai (instagram.com/reel/DePqiY2AiDn, референс №32). Тезис и раскадровка — ../ТЕЗИС.md.
// Вторая версия по слову владельца 14.10.2026: «нужен реальный логотип Claude; графика слабая, нужно красивее,
// больше 3D, движения и логики». Отсюда:
// - логотипы настоящие: знак, надпись Claude и Claude Code — @lobehub/icons, Telegram — simple-icons (data-build.mjs);
// - сквозной герой — объёмный знак Claude (three.js): отвечает на вопрос, пишет код, едет по дорожке монтажа,
//   стоит в центре команды, поднимается по ступеням и ныряет в Telegram;
// - всё, что считается предметом, — в объёме (кольцо агентов, плитки «нейрослопа», телефоны, лента проверки, ступени,
//   коробка); вёрстка держит текст и карточки, у них перспектива CSS 3D;
// - характер один, «дорогой»: появление expo.out, уход power2.in, без отскоков, вспышек и зерна.
// Всё записано твинами без обратных вызовов: перемотка в любую секунду даёт верный кадр.

// Порядок фраз сценария: номер строки субтитров (T.caps[].line) = номер фразы с единицы.
const ORDER = ['hook', 'who', 'code', 'self', 'hype', 'try', 'slop', 'stop', 'why', 'team', 'roles', 'skills', 'much',
  'same', 'same2', 'refs', 'design', 'uniq', 'check', 'path', 'pack', 'cta'];
// Сцены-контейнеры: одна форма живёт несколько фраз подряд.
const GROUPS = [['hook', 'who'], ['code', 'self'], ['hype', 'hype'], ['try', 'try'], ['slop', 'slop'], ['stop', 'stop'], ['why', 'why'],
  ['team', 'much'], ['same', 'same2'], ['refs', 'refs'], ['design', 'design'], ['uniq', 'uniq'], ['check', 'check'], ['path', 'path'],
  ['pack', 'pack'], ['cta', 'cta']];
const PAGE = { hook: 'dark', who: 'dark', code: 'dark', self: 'dark', hype: 'cream', try: 'cream', slop: 'stone', stop: 'lime', why: 'lime',
  team: 'dark', roles: 'dark', skills: 'dark', much: 'dark', same: 'stone', same2: 'stone', refs: 'cream', design: 'olive', uniq: 'cream',
  check: 'dark', path: 'forest', pack: 'cream', cta: 'lime' };
const GLOW = { hook: 'lime', who: 'lime', code: 'warm', self: 'warm', team: 'lime', roles: 'lime', skills: 'lime', much: 'warm', check: 'lime' };
const kind = () => 'light';                          // один мир — светлая студия: заголовки везде одного вида

const rnd = (seed) => { const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const ic = (name, cls = '', set = 'r') => `<svg class="ic ${cls}" viewBox="0 0 256 256" fill="currentColor">${(set === 'f' ? FILL : set === 'b' ? BOLD : ICONS)[name]}</svg>`;
// Настоящие логотипы (контуры из public/team/brand).
const SPARK = (cls = '') => `<svg class="spark ${cls}" viewBox="0 0 24 24"><path fill="#D97757" d="${BRAND.spark}"/></svg>`;
const WORD = (cls = '') => `<svg class="word ${cls}" viewBox="0 0 97 24" fill="currentColor">${BRAND.text.map((d) => `<path d="${d}"/>`).join('')}</svg>`;
const CODEMARK = (cls = '') => `<svg class="codemark ${cls}" viewBox="0 0 24 24"><path fill="#D97757" fill-rule="evenodd" clip-rule="evenodd" d="${BRAND.code}"/></svg>`;
const TG = (cls = '') => `<svg class="tglogo ${cls}" viewBox="0 0 24 24"><path fill="#26A5E4" d="${BRAND.tg}"/></svg>`;
const CURSOR = '<svg class="cur" viewBox="0 0 32 32"><path d="M5 3l20 12.5-8.6 1.8 5 9.4-3.7 2-5-9.4L6.5 26z" fill="#F1F2EA" stroke="#12130F" stroke-width="1.8" stroke-linejoin="round"/></svg>';

// Стена вопросов в личных: x, y, текст, глубина (0 — близко, 2 — далеко и размыто).
const MSGS = [[70, 480, 'как ты делаешь такие ролики?', 0], [600, 630, 'это нейросеть?', 1], [-80, 660, 'скинь программу', 2],
  [110, 1090, 'научи так же', 1], [520, 1190, 'сколько стоит монтаж?', 0], [-40, 1330, 'где взять шаблон?', 2],
  [600, 1430, 'чем монтируешь?', 1], [690, 770, 'нужен такой же', 2], [300, 1560, 'это After Effects?', 2]];
const DEPTH = [90, -220, -560];
const RCOL = ['#12130F', '#56690C', '#B9B9AE', '#8C8E7E', '#E2E2D8', '#3F4A1C'];
const refTile = (k) => {
  const bg = RCOL[Math.floor(rnd(k + 3) * RCOL.length)];
  const fg = RCOL[(RCOL.indexOf(bg) + 1 + Math.floor(rnd(k + 7) * 4)) % RCOL.length];
  const t = Math.floor(rnd(k + 11) * 4);
  const shape = [
    `<i style="left:45px;top:80px;width:140px;height:140px;border-radius:50%;background:${fg}"></i>`,
    `<i style="left:0;top:150px;width:230px;height:150px;background:${fg}"></i><i style="left:70px;top:50px;width:90px;height:90px;border-radius:50%;background:#F1F2EA"></i>`,
    `<i style="left:-60px;top:-60px;width:250px;height:250px;transform:rotate(45deg);background:${fg}"></i>`,
    `<i style="left:30px;top:40px;width:170px;height:28px;border-radius:14px;background:${fg}"></i><i style="left:30px;top:90px;width:120px;height:28px;border-radius:14px;background:${fg}"></i><i style="left:30px;top:170px;width:170px;height:90px;border-radius:18px;background:${fg};opacity:.6"></i>`][t];
  return `<div class="rf" style="background:${bg}">${shape}</div>`;
};
const STEPS = ['Идея', 'Сценарий', 'Голос', 'Монтаж', 'Проверка'];
const STEP_Y = (k) => 1320 - k * 175;          // центр ступени по высоте; то же число в three.js

/** Разметка: третья версия — весь мир в объёме (three.js), вёрстка держит только заголовок, знак и полосу хода. */
export const markup = () => `<div class="bgv3"></div>
<canvas id="gl" class="gl" width="1080" height="1920" data-layout-ignore></canvas>
`;

// Заголовок-субтитры: фраза кусками [строка1, строка2] по числу слов. Строка 1 крупная, строка 2 — продолжение.
const SEGS = {
  hook: [[3, 0]], who: [[2, 3]], code: [[4, 3], [2, 2]], self: [[3, 2]], hype: [[2, 3]], try: [[4, 3], [3, 0]], slop: [[1, 3]],
  stop: [[1, 4]], why: [[3, 0]], team: [[2, 3], [2, 2]], roles: [[0, 2], [0, 2], [0, 2]], skills: [[2, 3]], much: [[2, 0]],
  same: [[4, 4]], same2: [[2, 1], [3, 1], [0, 3]], refs: [[2, 1], [3, 2]], design: [[3, 3], [0, 4]], uniq: [[2, 2], [3, 0]],
  check: [[2, 3], [3, 1]], path: [[0, 3], [0, 2], [2, 2]], pack: [[3, 3], [0, 3]], cta: [[3, 0], [0, 3], [2, 3]],
};
const ACCENT = new Set(['Никто', 'Нейрослоп', 'модели', 'команда', 'одинаковые', 'часы', 'стиль', 'нет', 'Брак', 'система', 'сохрани']);
export const headlines = (T) => {
  const lines = new Map();
  T.caps.forEach((c) => lines.set(c.line, [...(lines.get(c.line) || []), c]));
  const out = [];
  ORDER.forEach((id, n) => {
    const ws = (lines.get(n + 1) || []).map((c) => ({ w: c.w.replace(/[.!]$/, ''), s: c.s }));
    const s = T.scenes[id].s, e = T.scenes[id].e;
    let k = 0;
    SEGS[id].forEach(([a, b], j) => {
      const l1 = ws.slice(k, k + a), l2 = ws.slice(k + a, k + a + b);
      k += a + b;
      const next = SEGS[id][j + 1] ? ws[k] : null;
      const first = [...l1, ...l2][0];
      out.push({ id, kind: kind(id), from: j === 0 ? s : first.s - 0.08, to: next ? next.s - 0.1 : e, l1, l2, first: id === 'hook' && j === 0 });
    });
  });
  return out;
};

// Третья версия: сцены — станции объёмного мира (three.js), здесь им нечего двигать. Таймлайн держит длину ролика.
export const buildScenes = (gsap, tl, root, T) => tl.to({}, { duration: T.length }, 0);

/** Слой поверх сцен: знак канала, полоса ролика, заголовок-субтитры. */
export const overlayMarkup = (A, T) => `<div class="logo"><img src="${A}/logo.png"></div>
<div class="prog">${'<i><b></b></i>'.repeat(6)}</div>
` + headlines(T).map((h) => `<div class="hl ${h.kind} ${h.first ? 'first' : ''}">${[h.l1, h.l2].map((line, k) => line.length ? `<div class="${k ? 'l2' : 'l1'}">${
  line.map((x) => `<span class="${/^Claude/.test(x.w) ? 'cl' : ACCENT.has(x.w.replace(/[,:?]$/, '')) ? 'ac' : ''}">${x.w}</span>`).join('')}</div>` : '').join('')}</div>`).join('');

export const buildOverlay = (gsap, tl, root, T) => {
  const s = (id) => T.scenes[id].s;
  const L = T.length;
  headlines(T).forEach((h, n) => {
    const box = root.querySelectorAll('.hl')[n];
    const spans = [...box.querySelectorAll('.l1 > span, .l2 > span')];
    const words = [...h.l1, ...h.l2];
    let shown = 0;
    spans.forEach((sp, i) => {
      if (h.first && i < h.l1.length) return;                 // первая строка ролика стоит с нулевого кадра: это обложка
      const at = Math.max(h.from, words[i].s - 0.05);
      shown = Math.max(shown, at + 0.26);
      tl.fromTo(sp, { opacity: 0, y: 22, filter: 'blur(10px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.26, ease: 'power3.out' }, at);
    });
    // Гаснет не раньше, чем последнее слово успело встать: иначе затухание кончится до появления и слово
    // останется висеть под следующими заголовками (14.10.2026, «Никто» во фразе 2).
    if (h.to < L - 0.05) tl.fromTo(spans, { opacity: 1, filter: 'blur(0px)' }, { opacity: 0, filter: 'blur(10px)', duration: 0.18, ease: 'power2.in', immediateRender: false },
      Math.max(h.to - 0.18, shown));
  });

  // Полоса ролика: шесть отрезков по блокам. На заставке её нет: встаёт, когда приходит главный вопрос, и идёт до конца.
  const prog = root.querySelector('.prog');
  const старт = T.w.hook[3] - 0.12;
  [...prog.querySelectorAll('i')].forEach((el, i) =>
    tl.fromTo(el, { opacity: 0, scaleX: 0 }, { opacity: 1, scaleX: 1, duration: 0.4, ease: 'expo.out' }, старт + 0.05 + i * 0.04));
  const части = [старт + 0.3, s('hype'), s('why'), s('same'), s('check'), s('pack'), L - 0.3];
  [...prog.querySelectorAll('b')].forEach((b, i) =>
    tl.fromTo(b, { scaleX: 0 }, { scaleX: 1, duration: части[i + 1] - части[i], ease: 'none' }, части[i]));
  const ЦВЕТ = { dark: ['#C7E24B', 'rgba(241,242,234,.22)'], olive: ['#C7E24B', 'rgba(241,242,234,.25)'], forest: ['#C7E24B', 'rgba(241,242,234,.22)'],
    cream: ['#56690C', 'rgba(18,19,15,.16)'], stone: ['#3F4D08', 'rgba(18,19,15,.18)'], lime: ['#12130F', 'rgba(18,19,15,.2)'] };
  tl.set(prog, { '--pf': ЦВЕТ.cream[0], '--pt': ЦВЕТ.cream[1] }, 0);
  return tl;
};
