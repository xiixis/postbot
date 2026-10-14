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
const kind = (id) => (['cream', 'stone'].includes(PAGE[id]) ? 'light' : PAGE[id] === 'lime' ? 'lime' : '');

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
const CODE = [
  '<span class="k">const</span> tl = gsap.timeline();',
  'tl.from(card, { y: <span class="n">140</span> }, <span class="n">0.4</span>);',
  'tl.to(title, { opacity: <span class="n">1</span> }, <span class="n">1.2</span>);',
  'spin(drum, <span class="s">\'1200\'</span>, <span class="n">2.0</span>);',
  '<span class="c">// голос, музыка, звуки</span>',
  'render({ fps: <span class="n">30</span> });'];
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

/** Разметка всех сцен. A — адрес папки с картинками, T — раскладка. */
export const markup = (A, T) => `
${['dark', 'cream', 'stone', 'lime', 'olive', 'forest'].map((p) => `<div class="pg pg-${p}"></div>`).join('')}
<div class="pg pg-dark reveal" style="opacity:0"></div>
${['lime', 'warm'].map((g) => `<div class="glow glow-${g}" data-layout-ignore${g === 'lime' ? ' style="opacity:1"' : ''}><i></i></div>`).join('')}
<div class="vignette" style="opacity:1"></div>
<canvas id="gl" class="gl" width="1080" height="1920" data-layout-ignore></canvas>

<div class="sc" id="sc-hook" style="opacity:1">
  <div class="wall3d" data-layout-ignore><div class="wallin">${MSGS.map(([x, y, t, d]) => `<div class="msg d${d}" style="left:${x}px;top:${y}px;transform:translateZ(${DEPTH[d]}px)"><span class="av">${ic('user', '', 'f')}</span>${t}</div>`).join('')}</div></div>
  <div class="qb h"><span class="av">${ic('chat-circle')}</span><span>кто монтирует эти ролики?</span><span class="badge">1</span></div>
  <div class="ans h" style="top:770px"><span class="dots"><i></i><i></i><i></i></span><span class="nt">Никто.</span></div>
  <div class="brand h">${WORD()}</div>
  <div class="pill ccode h">${CODEMARK()}Claude Code</div>
</div>

<div class="sc" id="sc-code">
  <div class="tilt t-gen"><div class="gen"><div class="blob"></div><div class="play">${ic('play', '', 'f')}</div><div class="lab">${ic('sparkle', '', 'f')}<span>генерирую видео…</span><b></b></div></div>
    <svg class="strike" viewBox="0 0 800 560"><path d="M10 540 L790 20"/></svg></div>
  <div class="tilt t-code"><div class="code mono h">${CODE.map((l) => `<div class="ln">${l}</div>`).join('')}</div></div>
  <div class="tilt t-prev"><div class="prev h">${['s1', 's2', 's3'].map((f, k) => `<img class="pv pv${k}" src="${A}/real/${f}.jpg" style="opacity:${k ? 0 : 1}">`).join('')}</div></div>
  <div class="tilt t-edit"><div class="edit h">
    <div class="trk"><span class="tl">${ic('text-t')}текст</span><div class="cl2" style="width:250px;background:#F1F2EA">заголовок</div><div class="cl2" style="width:300px;background:#C7E24B">субтитры</div><div class="cl2" style="width:160px;background:#F1F2EA">итог</div></div>
    <div class="trk"><span class="tl">${ic('film-strip', '', 'b')}кадр</span>${['s1', 's2', 's3', 's4'].map((f) => `<div class="cl2" style="width:170px;padding:0"><img src="${A}/real/${f}.jpg"></div>`).join('')}</div>
    <div class="trk"><span class="tl">${ic('waveform', '', 'b')}звук</span><div class="wv">${Array.from({ length: 62 }, (_, i) => `<i style="height:${Math.round(10 + 50 * rnd(i + 5) * (0.35 + 0.65 * Math.abs(Math.sin(i * 0.37))))}px"></i>`).join('')}</div></div>
    <div class="trk"><span class="tl">${ic('sparkle', '', 'f')}переход</span>${'<i class="kf"></i>'.repeat(6)}</div>
    <div class="head"></div>
  </div></div>
  <div class="pill limep done h" style="left:360px;top:900px">${ic('check', '', 'b')}ролик собран</div>
</div>

<div class="sc lt" id="sc-hype"><div class="hword">${WORD()}</div></div>

<div class="sc lt" id="sc-try">
  <div class="tilt t-inp"><div class="inp">${SPARK()}<div class="tx">${[...'сделай ролик'].map((c) => `<i>${c === ' ' ? '&nbsp;' : c}</i>`).join('')}<span class="caret"></span></div><div class="send">${ic('paper-plane-tilt', '', 'r')}</div></div></div>
  <div class="tilt t-wait"><div class="wait h"><b></b><div class="ring"></div></div></div>
  <div class="cursor">${CURSOR}</div>
</div>

<div class="sc lt" id="sc-slop"><div class="stamp h">нейрослоп</div></div>

<div class="sc lt" id="sc-stop">
  <div class="hand">${ic('hand-palm', '', 'f')}</div>
  <div class="model h">${SPARK()}Claude Opus 5.5</div>
  <svg class="mark" viewBox="0 0 780 170"><path d="M20 98 L760 72"/></svg>
</div>

<div class="sc lt" id="sc-why"><div class="qm">?</div></div>

<div class="sc" id="sc-team"></div>

<div class="sc lt" id="sc-same">
  <div class="pill limep pp h" style="left:330px;top:1080px">${ic('user', '', 'f')}человек в кадре</div>
</div>

<div class="sc lt" id="sc-refs">
  <div class="refs3d"><div class="refs"><div class="refcol">${Array.from({ length: 27 }, (_, k) => refTile(k)).join('')}</div></div></div>
  <div class="pill white clock h"><div class="dial"><b></b></div>часы поиска</div>
  <div class="cursor">${CURSOR}</div>
</div>

<div class="sc" id="sc-design">
  <div class="pill limep dtag h">${ic('palette', '', 'b')}дизайнер-агент</div>
  <div class="dcard"><div class="dv dv0" style="opacity:1">ролик<u></u></div><div class="dv dv1">ролик</div><div class="dv dv2">&lt;ролик/&gt;</div><div class="dv dv3"><em></em><span>ролик</span></div></div>
</div>

<div class="sc lt" id="sc-uniq"><div class="pill white made h">собрано в ${CODEMARK()}<span class="cl">Claude</span>&nbsp;Code</div></div>

<div class="sc" id="sc-check">
  <div class="pill limep chk h">${ic('eye', '', 'b')}проверяющий</div>
  <div class="pill redo h">${ic('arrow-counter-clockwise', '', 'b')}на переделку</div>
</div>

<div class="sc" id="sc-path">
  ${STEPS.map((n, k) => `<div class="pname pn${k}" style="top:${STEP_Y(k) - 46}px">${n}</div>`).join('')}
  <div class="pill limep sys h">${ic('users-three', '', 'b')}команда агентов</div>
</div>

<div class="sc lt" id="sc-pack"></div>

<div class="sc lt" id="sc-cta">
  <div class="tilt t-tg"><div class="tg h"><div class="top"><div class="tgi">${TG()}</div><div><div class="t1">Telegram</div><div class="t2">вся система внутри</div></div></div>
    <div class="go">ссылка в профиле ${ic('arrow-up-right', '', 'b')}<b></b></div></div></div>
  <div class="pill dark save h">${ic('bookmark-simple', '', 'f')}сохрани</div>
  <img class="cat h" src="${A}/cat-point.png">
  <div class="cursor">${CURSOR}</div>
</div>
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

export const buildScenes = (gsap, tl, root, T) => {
  const $ = (sel, from = root) => from.querySelector(sel);
  const $$ = (sel, from = root) => [...from.querySelectorAll(sel)];
  const s = (id) => T.scenes[id].s;
  const e = (id) => T.scenes[id].e;
  const w = (id, i) => T.w[id][i];
  const L = T.length;
  const REST = { x: 0, y: 0, z: 0, scale: 1, rotation: 0, rotationY: 0, rotationX: 0, filter: 'blur(0px)' };
  const inn = (el, t, from = { y: 40 }, duration = 0.5, ease = 'power3.out') => {
    const to = { opacity: 1, duration, ease };
    Object.keys(from).forEach((k) => { to[k] = REST[k]; });
    return tl.fromTo(el, { opacity: 0, ...from }, to, t);
  };
  const pop = (el, t) => { tl.set(el, { transformOrigin: '50% 50%' }, 0); return inn(el, t, { scale: 0.9, y: 16 }, 0.4, 'expo.out'); };
  const draw = (el, t, duration, ease = 'power2.inOut') => {
    const len = el.getTotalLength();
    // скруглённый конец рисует точку даже у линии нулевой длины: до начала линия скрыта
    tl.set(el, { strokeDasharray: len, strokeDashoffset: len, opacity: 0 }, 0);
    tl.set(el, { opacity: 1 }, t);
    return tl.to(el, { strokeDashoffset: 0, duration, ease }, t);
  };
  const sweep = (el, t, duration, dist = 1300) => tl.fromTo(el, { x: 0 }, { x: dist, duration, ease: 'power2.inOut' }, t);
  const cursorTo = (el, pts) => {
    pts.forEach(([x, y, t, click], k) => {
      if (k === 0) tl.fromTo(el, { opacity: 0, x: x + 50, y: y + 70 }, { opacity: 1, x, y, duration: 0.3, ease: 'power2.out' }, t);
      else tl.to(el, { x, y, duration: Math.max(0.15, t - pts[k - 1][2] - 0.05), ease: 'power2.inOut' }, pts[k - 1][2] + 0.05);
      if (click) tl.to(el, { scale: 0.82, duration: 0.07, ease: 'power2.out', yoyo: true, repeat: 1, transformOrigin: '10% 10%' }, t);
    });
  };
  // Мигание каретки: оно значит «ждёт ввода», поэтому живёт только пока ждёт.
  const blink = (el, a, b) => { for (let t = a; t < b; t += 1.0) tl.set(el, { opacity: 0 }, t + 0.5).set(el, { opacity: 1 }, Math.min(b, t + 1.0)); };

  // Сцены-контейнеры: входят из глубины, уходят чуть вперёд с размытием. Внутри контейнера склеек нет.
  const SC = {};
  GROUPS.forEach(([a, b], n) => {
    const el = $('#sc-' + a);
    SC[a] = el;
    if (n > 0) tl.fromTo(el, { opacity: 0, scale: 0.94, filter: 'blur(12px)' }, { opacity: 1, scale: 1, filter: 'blur(0px)', duration: 0.42, ease: 'expo.out' }, s(a) - 0.04);
    if (b !== 'cta') tl.to(el, { opacity: 0, scale: 1.05, filter: 'blur(10px)', duration: 0.26, ease: 'power2.in' }, e(b) - 0.22);
  });

  // Свет: страница блока и пятно на тёмных. Команда открывается кругом из «?».
  const vig = $('.vignette');
  ORDER.forEach((id, n) => {
    if (n === 0) return;
    const prev = ORDER[n - 1], t = s(id) - 0.1;
    if (PAGE[prev] !== PAGE[id]) {
      if (id === 'team') {
        const rv = $('.reveal');
        tl.set(rv, { opacity: 1, clipPath: 'circle(0% at 50% 49%)' }, 0);
        tl.set(rv, { opacity: 0 }, 0.001);
        tl.set(rv, { opacity: 1 }, t - 0.05);
        tl.to(rv, { clipPath: 'circle(75% at 50% 49%)', duration: 0.6, ease: 'power3.inOut' }, t - 0.05);
        tl.set($('.pg-dark:not(.reveal)'), { opacity: 1 }, t + 0.6);
        tl.set($('.pg-' + PAGE[prev]), { opacity: 0 }, t + 0.6);
        tl.set(rv, { opacity: 0 }, t + 0.61);
      } else {
        tl.to($('.pg-' + PAGE[id] + (PAGE[id] === 'dark' ? ':not(.reveal)' : '')), { opacity: 1, duration: 0.35, ease: 'power2.out' }, t);
        tl.to($('.pg-' + PAGE[prev] + (PAGE[prev] === 'dark' ? ':not(.reveal)' : '')), { opacity: 0, duration: 0.35, ease: 'power2.out' }, t);
      }
    }
    const dark = PAGE[id] === 'dark', wasDark = PAGE[prev] === 'dark';
    if (dark !== wasDark) tl.to(vig, { opacity: dark ? 1 : 0, duration: 0.35 }, t);
    if (GLOW[prev] !== GLOW[id]) {
      if (GLOW[prev]) tl.to($('.glow-' + GLOW[prev]), { opacity: 0, duration: 0.35 }, t);
      if (GLOW[id]) tl.to($('.glow-' + GLOW[id]), { opacity: 1, duration: 0.5 }, t);
    }
  });
  $$('.glow i').forEach((el, i) => tl.fromTo(el, { scale: 0.96 }, { scale: 1.05, duration: 3 + i * 0.4, ease: 'sine.inOut', yoyo: true,
    repeat: Math.max(0, Math.floor(L / (3 + i * 0.4)) - 1) }, 0));

  // 1–2. Стена вопросов в глубине: камера медленно въезжает в неё с нулевого кадра. На «кто» главный вопрос
  // прилетает из глубины. На «Отвечаю» он уезжает вверх, печатается «Никто», объёмный знак Claude прилетает
  // ответом (three.js), под ним встают настоящая надпись Claude и плашка Claude Code.
  {
    const sc = SC.hook, ask = w('hook', 3) - 0.12, up = s('who');
    tl.fromTo($('.wallin', sc), { z: -80, rotationY: -7, rotationX: 5 }, { z: 260, rotationY: 6, rotationX: -2, duration: up + 0.6, ease: 'power1.inOut' }, 0);
    tl.set($('.qb', sc), { transformOrigin: '0% 100%' }, 0);
    inn($('.qb', sc), ask, { z: -900, y: 60, rotationX: 25 }, 0.6, 'expo.out');
    tl.fromTo($('.qb .badge', sc), { scale: 0 }, { scale: 1, duration: 0.3, ease: 'expo.out' }, ask + 0.3);
    tl.to($('.wall3d', sc), { opacity: 0.2, filter: 'blur(8px)', duration: 0.45, ease: 'power2.out' }, up);
    tl.to($('.qb', sc), { y: -330, scale: 0.8, rotationX: -8, duration: 0.55, ease: 'power3.inOut' }, up);
    tl.to($('.qb .badge', sc), { scale: 0, duration: 0.2 }, up);
    tl.set($('.ans', sc), { transformOrigin: '100% 100%' }, 0);
    inn($('.ans', sc), w('who', 0) + 0.05, { y: 60, scale: 0.9, rotationY: -30 }, 0.5, 'expo.out');
    tl.set($('.ans .nt', sc), { opacity: 0 }, 0);
    $$('.ans .dots i', sc).forEach((d, k) => tl.fromTo(d, { y: 0 }, { y: -12, duration: 0.18, ease: 'sine.inOut', yoyo: true, repeat: 3 }, w('who', 0) + 0.15 + k * 0.08));
    tl.to($('.ans .dots', sc), { opacity: 0, duration: 0.1 }, w('who', 1) - 0.08);
    tl.to($('.ans .nt', sc), { opacity: 1, duration: 0.15 }, w('who', 1) - 0.05);
    inn($('.brand', sc), w('who', 2) + 0.35, { y: 40, rotationX: 70 }, 0.55, 'expo.out');
    inn($('.ccode', sc), w('who', 3) + 0.1, { y: 40, scale: 0.9 }, 0.45, 'expo.out');
  }

  // 3–4. Карточку «генерирую видео» перечёркивает линия; знак Claude садится ей на угол и на «пишет» крутится,
  // код печатается; на «сам собирает» код уходит, встают дорожки монтажа и превью, знак едет вместе с бегунком.
  {
    const sc = SC.code, t = s('code'), swap = w('code', 7) - 0.1, sel = s('self');
    inn($('.gen', sc), t, { y: 60, scale: 0.95, rotationY: 25 }, 0.6, 'expo.out');
    tl.fromTo($('.gen .lab b', sc), { x: 0 }, { x: 1100, duration: 1.4, ease: 'none', repeat: 1 }, t + 0.2);
    draw($('.strike path', sc), w('code', 5) - 0.05, 0.45, 'power3.inOut');
    tl.to($('.t-gen', sc), { x: -260, rotationY: 40, opacity: 0, filter: 'blur(8px)', duration: 0.45, ease: 'power2.in' }, swap);
    inn($('.code', sc), swap + 0.12, { x: 200, rotationY: -35 }, 0.6, 'expo.out');
    // код печатается целиком до смены сцены: строки по 0,12 с с «Он пишет»
    $$('.code .ln', sc).forEach((ln, k) => tl.fromTo(ln, { clipPath: 'inset(0% 100% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 0.2, ease: 'none' },
      swap + 0.25 + k * 0.12));
    tl.to($('.code', sc), { y: -60, rotationX: 30, opacity: 0, filter: 'blur(8px)', duration: 0.38, ease: 'power2.in' }, sel - 0.22);
    inn($('.prev', sc), sel + 0.02, { y: 80, rotationY: 40 }, 0.55, 'expo.out');
    inn($('.edit', sc), sel + 0.1, { y: 160, rotationX: 50 }, 0.6, 'expo.out');
    const a = sel + 0.35, b = e('self') - 0.45;
    tl.fromTo($('.edit .head', sc), { x: 0 }, { x: 690, duration: b - a, ease: 'none' }, a);
    tl.to($('.pv1', sc), { opacity: 1, duration: 0.12 }, a + (b - a) * 0.36);
    tl.to($('.pv2', sc), { opacity: 1, duration: 0.12 }, a + (b - a) * 0.7);
    pop($('.done', sc), b - 0.05);
  }

  // 5. Хайп: над крупным объёмным знаком (three.js) поднимаются сердца; надпись Claude встаёт из плоскости.
  {
    const sc = SC.hype, t = s('hype');
    tl.set($('.hword', sc), { transformOrigin: '50% 100%' }, 0);
    inn($('.hword', sc), t + 0.2, { y: 40, rotationX: 80 }, 0.65, 'expo.out');
  }

  // 6. «Сделай ролик»: буквы печатаются на своих словах, курсор жмёт «отправить», ждём.
  {
    const sc = SC.try, t = s('try'), a = w('try', 4), b = w('try', 6) + 0.35;
    inn($('.inp', sc), t, { y: 50, rotationX: -40 }, 0.6, 'expo.out');
    const chars = $$('.tx i', sc);
    chars.forEach((c, k) => tl.set(c, { opacity: 1 }, a + (k / chars.length) * (b - a)));
    blink($('.inp .caret', sc), t + 0.2, a);
    const click = w('try', 7);
    cursorTo($('.cursor', sc), [[760, 900, b - 0.2], [890, 620, click, true]]);
    tl.to($('.inp .send', sc), { scale: 0.88, duration: 0.08, yoyo: true, repeat: 1 }, click);
    tl.to($('.inp .caret', sc), { opacity: 0, duration: 0.05 }, click);
    inn($('.wait', sc), click + 0.15, { y: 120, rotationX: 50 }, 0.6, 'expo.out');
    tl.fromTo($('.wait .ring', sc), { rotation: 0 }, { rotation: 540, duration: e('try') - click, ease: 'none' }, click + 0.15);
    sweep($('.wait b', sc), click + 0.3, 1.1, 1200);
  }

  // 7. Нейрослоп: штамп падает на сетку одинаковых шаров (three.js).
  {
    const sc = SC.slop;
    tl.set($('.stamp', sc), { transformOrigin: '50% 50%' }, 0);
    tl.fromTo($('.stamp', sc), { opacity: 0, scale: 1.5, rotation: -14, z: 300 }, { opacity: 1, scale: 1, rotation: -6, z: 0, duration: 0.3, ease: 'power4.out' }, w('slop', 0) - 0.02);
  }

  // 8. Стоп: ладонь бьёт из плоскости, ниже модель, маркер её перечёркивает.
  {
    const sc = SC.stop, t = s('stop');
    tl.set($('.hand', sc), { transformOrigin: '50% 100%' }, 0);
    tl.fromTo($('.hand', sc), { opacity: 0, scale: 1.25, rotationX: 70 }, { opacity: 1, scale: 1, rotationX: 0, duration: 0.32, ease: 'power4.out' }, t);
    inn($('.model', sc), w('stop', 1) - 0.08, { y: 60, rotationX: -60 }, 0.5, 'expo.out');
    draw($('.mark path', sc), w('stop', 4) - 0.05, 0.35, 'power2.out');
  }

  // 9. Знак вопроса поворачивается к зрителю; к концу сжимается в точку, из неё кругом открывается команда.
  {
    const sc = SC.why, t = s('why');
    tl.set($('.qm', sc), { transformOrigin: '50% 55%' }, 0);
    tl.fromTo($('.qm', sc), { opacity: 0, scale: 0.86, rotationY: -80 }, { opacity: 1, scale: 1, rotationY: 0, duration: 0.5, ease: 'expo.out' }, t);
    tl.to($('.qm', sc), { scale: 0.2, duration: 0.45, ease: 'power3.in' }, e('why') - 0.4);
  }

  // 14–15. Одинаковые телефоны — объём; здесь только плашка «человек в кадре».
  pop($('.pp', SC.same), w('same2', 3) - 0.08);

  // 16. Референсы: наклонная стена листается, курсор крутит колесо; на «уходят часы» встают часы, стрелка бежит.
  {
    const sc = SC.refs, t = s('refs'), end = e('refs');
    tl.fromTo($('.refcol', sc), { y: 40 }, { y: -1100, duration: end - t, ease: 'power1.inOut' }, t);
    cursorTo($('.cursor', sc), [[820, 980, t + 0.2], [800, 1020, end - 0.3]]);
    pop($('.clock', sc), w('refs', 6) - 0.1);
    tl.fromTo($('.clock .dial b', sc), { rotation: 0 }, { rotation: 720, duration: end - w('refs', 6), ease: 'none' }, w('refs', 6));
  }

  // 17. Дизайнер-агент: карточка переворачивается и с каждым поворотом показывает «ролик» в новом облике.
  {
    const sc = SC.design, t = s('design');
    const card = $('.dcard', sc);
    inn(card, t, { y: 120, rotationX: 40 }, 0.6, 'expo.out');
    pop($('.dtag', sc), w('design', 3) - 0.1);
    const STATES = [[w('design', 5), '#12130F', 120], [w('design', 7), '#C7E24B', 18], [w('design', 9), '#1B2108', 300]];
    STATES.forEach(([at, bg, r], k) => {
      const mid = at - 0.04;
      tl.to(card, { rotationY: 90, duration: 0.2, ease: 'power2.in' }, mid - 0.2);
      tl.set(card, { backgroundColor: bg, borderRadius: r, rotationY: -90 }, mid);
      tl.set($('.dv' + k, sc), { opacity: 0 }, mid);
      tl.set($('.dv' + (k + 1), sc), { opacity: 1 }, mid);
      tl.to(card, { rotationY: 0, duration: 0.42, ease: 'expo.out' }, mid);
    });
  }

  // 18. Веер настоящих роликов — объём; плашка «собрано в Claude Code».
  pop($('.made', SC.uniq), w('uniq', 5) - 0.1);

  // 19. Проверка: конвейер — объём; плашки «проверяющий» и «на переделку».
  pop($('.chk', SC.check), s('check') + 0.15);
  pop($('.redo', SC.check), w('check', 7) - 0.05);

  // 20. Путь: подписи ступеней загораются на своих словах; на «делает система» — «команда агентов».
  {
    const sc = SC.path, t = s('path');
    $$('.pname', sc).forEach((el, k) => {
      inn(el, t + k * 0.06, { x: -40 }, 0.45, 'expo.out');
      tl.to(el, { color: '#F1F2EA', duration: 0.25 }, w('path', k) - 0.05);
    });
    pop($('.sys', sc), w('path', 7) - 0.1);
  }

  // 22. Финал: знак Claude ныряет в значок Telegram (three.js), и карточка встаёт; курсор жмёт «ссылка в профиле»
  // и «сохрани»; кот показывает лапой.
  {
    const sc = SC.cta, t = s('cta');
    inn($('.tg', sc), t + 0.45, { y: 80, scale: 0.92, rotationX: 40 }, 0.6, 'expo.out');
    inn($('.cat', sc), t + 0.5, { x: -160 }, 0.6, 'expo.out');
    tl.set($('.cat', sc), { scaleX: -1 }, 0);
    tl.fromTo($('.cat', sc), { y: 0 }, { y: -10, duration: 1.4, ease: 'sine.inOut', yoyo: true, repeat: Math.max(0, Math.floor((L - t - 1.2) / 1.4)) }, t + 1.1);
    const go = w('cta', 3);
    sweep($('.go b', sc), go - 0.1, 0.8, 1000);
    cursorTo($('.cursor', sc), [[760, 1000, go - 0.45], [560, 790, go + 0.1, true], [640, 1150, w('cta', 7) + 0.15, true], [720, 1300, w('cta', 7) + 0.7]]);
    tl.to($('.go', sc), { scale: 0.96, duration: 0.08, yoyo: true, repeat: 1 }, go + 0.1);
    pop($('.save', sc), w('cta', 7) - 0.12);
    tl.to($('.save', sc), { backgroundColor: '#3F4D08', duration: 0.15 }, w('cta', 7) + 0.15);
    tl.to($('.save .ic', sc), { color: '#C7E24B', duration: 0.15 }, w('cta', 7) + 0.15);
  }
  return tl;
};

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
  ORDER.forEach((id, n) => {
    if (n && PAGE[id] === PAGE[ORDER[n - 1]]) return;
    const [f, t] = ЦВЕТ[PAGE[id]];
    tl.set(prog, { '--pf': f, '--pt': t }, Math.max(0, s(id) - 0.1));
  });
  return tl;
};
