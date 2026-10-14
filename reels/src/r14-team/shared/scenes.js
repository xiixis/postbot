// Ролик «Кто монтирует эти ролики?» (r14). Движок один: HyperFrames.
//
// Рерайт рилса @milanko.ai (instagram.com/reel/DePqiY2AiDn, референс №32). Тезис и раскадровка, одобренные
// владельцем 14.10.2026, — ../ТЕЗИС.md. Коротко:
// - ролик почти без склеек: вопрос в личных сообщениях уезжает вверх и получает ответ «Никто», код уступает
//   место дорожкам монтажа, «?» сжимается в кольцо команды, кольцо живёт три фразы подряд, одна карточка
//   дизайнера меняет облик четыре раза;
// - характер один, «дорогой»: появление expo.out, уход power2.in, без отскоков, вспышек и зерна;
// - свет блоками, как у автора: графит, крем, серый «нейрослоп», лайм «стоп», тёмная команда, олива, лес, лайм финала;
// - доказательства настоящие: кадры роликов r11–r13 этого канала (public/team/real), а не рисунки «под них».
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
const STAR = (cls = '') => `<svg class="star ${cls}" viewBox="0 0 24 24"><path d="M12 1.5l1.6 7.1 6.4-3.6-3.6 6.4 7.1 1.6-7.1 1.6 3.6 6.4-6.4-3.6L12 22.5l-1.6-7.1-6.4 3.6 3.6-6.4L.5 12l7.1-1.6L4 4l6.4 3.6z"/></svg>`;
const CURSOR = '<svg class="cur" viewBox="0 0 32 32"><path d="M5 3l20 12.5-8.6 1.8 5 9.4-3.7 2-5-9.4L6.5 26z" fill="#F1F2EA" stroke="#12130F" stroke-width="1.8" stroke-linejoin="round"/></svg>';

// Стена вопросов в личных: x, y, текст, глубина (0 — резко, 2 — далеко и размыто).
const MSGS = [[70, 480, 'как ты делаешь такие ролики?', 0], [600, 630, 'это нейросеть?', 1], [-80, 660, 'скинь программу', 2],
  [110, 1090, 'научи так же', 1], [520, 1190, 'сколько стоит монтаж?', 0], [-40, 1330, 'где взять шаблон?', 2],
  [600, 1430, 'чем монтируешь?', 1], [690, 770, 'нужен такой же', 2]];
// Строки кода: короткие, чтобы влезли крупно; приёмы те же, что в сценах наших роликов.
const CODE = [
  '<span class="k">const</span> tl = gsap.timeline();',
  'tl.from(card, { y: <span class="n">140</span> }, <span class="n">0.4</span>);',
  'tl.to(title, { opacity: <span class="n">1</span> }, <span class="n">1.2</span>);',
  'spin(drum, <span class="s">\'1200\'</span>, <span class="n">2.0</span>);',
  '<span class="c">// голос, музыка, звуки</span>',
  'render({ fps: <span class="n">30</span> });'];
// Пять мест вокруг Claude: центр места, значок, роль. Круг r=300 с центром (540, 940).
const SLOTS = [[540, 640, 'pencil-simple-line', 'сценарист'], [825, 847, 'palette', 'дизайнер'], [716, 1183, 'film-strip', 'монтажёр'],
  [364, 1183, 'waveform', 'звукорежиссёр'], [255, 847, 'eye', 'проверяющий']];
const HEARTS = Array.from({ length: 11 }, (_, k) => ({
  x: Math.round(60 + rnd(k + 1) * 900), y: Math.round(560 + rnd(k + 20) * 780), s: Math.round(56 + rnd(k + 40) * 70),
  c: ['', 'o', 'g'][k % 3], d: rnd(k + 60) }));
// Референсы: плитки-композиции в цветах канала, как сетка у автора.
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
const STRIP = ['s1', 's2', 's4', 's6', 's5', 's3', 's7'];
const BAD = 3;
const STEPS = [['lightbulb', 'Идея'], ['pencil-simple-line', 'Сценарий'], ['microphone', 'Голос'], ['film-strip', 'Монтаж'], ['eye', 'Проверка']];

/** Разметка всех сцен. A — адрес папки с картинками, T — раскладка. */
export const markup = (A, T) => `
${['dark', 'cream', 'stone', 'lime', 'olive', 'forest'].map((p) => `<div class="pg pg-${p}"></div>`).join('')}
<div class="pg pg-dark reveal" style="opacity:0"></div>
${['lime', 'warm'].map((g) => `<div class="glow glow-${g}" data-layout-ignore${g === 'lime' ? ' style="opacity:1"' : ''}><i></i></div>`).join('')}
<div class="vignette" style="opacity:1"></div>

<div class="sc" id="sc-hook" style="opacity:1">
  <div class="wall" data-layout-ignore>${MSGS.map(([x, y, t, d]) => `<div class="msg d${d}" style="left:${x}px;top:${y}px"><span class="av">${ic('user', '', 'f')}</span>${t}</div>`).join('')}</div>
  <div class="qb h"><span class="av">${ic('chat-circle')}</span><span>кто монтирует эти ролики?</span><span class="badge">1</span></div>
  <div class="ans h" style="top:770px"><span class="dots"><i></i><i></i><i></i></span><span class="nt">Никто.</span></div>
  <div class="ccard h" style="top:1010px"><div class="seal">${STAR()}</div><div class="nm"><span class="cl">Claude</span> Code<small>делает мои ролики</small></div></div>
</div>

<div class="sc" id="sc-code">
  <div class="gen"><div class="blob"></div><div class="play">${ic('play', '', 'f')}</div><div class="lab">${ic('sparkle', '', 'f')}<span>генерирую видео…</span><b></b></div></div>
  <svg class="strike" viewBox="0 0 880 640"><path d="M40 600 L840 40"/></svg>
  <div class="code mono h">${CODE.map((l) => `<div class="ln">${l}</div>`).join('')}</div>
  <div class="prev h">${['s1', 's2', 's3'].map((f, k) => `<img class="pv pv${k}" src="${A}/real/${f}.jpg" style="opacity:${k ? 0 : 1}">`).join('')}</div>
  <div class="edit h">
    <div class="trk"><span class="tl">${ic('text-t')}текст</span><div class="cl2" style="width:250px;background:#F1F2EA">заголовок</div><div class="cl2" style="width:300px;background:#C7E24B">субтитры</div><div class="cl2" style="width:160px;background:#F1F2EA">итог</div></div>
    <div class="trk"><span class="tl">${ic('film-strip', '', 'b')}кадр</span>${['s1', 's2', 's3', 's4'].map((f) => `<div class="cl2" style="width:170px;padding:0"><img src="${A}/real/${f}.jpg"></div>`).join('')}</div>
    <div class="trk"><span class="tl">${ic('waveform', '', 'b')}звук</span><div class="wv">${Array.from({ length: 62 }, (_, i) => `<i style="height:${Math.round(10 + 50 * rnd(i + 5) * (0.35 + 0.65 * Math.abs(Math.sin(i * 0.37))))}px"></i>`).join('')}</div></div>
    <div class="trk"><span class="tl">${ic('sparkle', '', 'f')}переход</span>${'<i class="kf"></i>'.repeat(6)}</div>
    <div class="head"></div>
  </div>
  <div class="pill limep done h" style="left:360px;top:900px">${ic('check', '', 'b')}ролик собран</div>
</div>

<div class="sc lt" id="sc-hype">
  ${HEARTS.map((h, k) => `<div class="heart hr${k} ${h.c}" data-layout-ignore style="left:${h.x}px;top:${h.y}px;font-size:${h.s}px">${ic('heart', '', 'f')}</div>`).join('')}
  ${STAR('hstar')}
  <div class="hword">Claude</div>
</div>

<div class="sc lt" id="sc-try">
  <div class="inp">${STAR()}<div class="tx">${[...'сделай ролик'].map((c) => `<i>${c === ' ' ? '&nbsp;' : c}</i>`).join('')}<span class="caret"></span></div><div class="send">${ic('paper-plane-tilt', '', 'r')}</div></div>
  <div class="wait h"><b></b><div class="ring"></div></div>
  <div class="cursor">${CURSOR}</div>
</div>

<div class="sc lt" id="sc-slop">
  <div class="slop">${Array.from({ length: 9 }, () => `<div class="tile"><div class="bl"></div>${ic('sparkle', '', 'f')}</div>`).join('')}</div>
  <div class="stamp h">нейрослоп</div>
</div>

<div class="sc lt" id="sc-stop">
  <div class="hand">${ic('hand-palm', '', 'f')}</div>
  <div class="model h">${STAR()}Claude Opus 5.5</div>
  <svg class="mark" viewBox="0 0 780 170"><path d="M20 98 L760 72"/></svg>
</div>

<div class="sc lt" id="sc-why"><div class="qm">?</div></div>

<div class="sc" id="sc-team">
  <div class="ringg">
    <svg class="orbit" viewBox="0 0 1080 1920"><circle cx="540" cy="940" r="300"/><line class="ln1" x1="420" y1="1380" x2="490" y2="1236"/><line class="ln2" x1="680" y1="1380" x2="600" y2="1234"/></svg>
    <div class="core">${STAR()}</div><div class="corelab">Claude</div>
    ${SLOTS.map(([x, y, icon, name], k) => `<div class="slot s${k}" style="left:${x}px;top:${y}px"><div class="fill">${ic(icon, '', 'b')}</div><div class="nm">${name}</div></div>`).join('')}
  </div>
  <div class="pill plug p1 h" style="left:270px">${ic('puzzle-piece', '', 'b')}скилы</div>
  <div class="pill plug p2 h" style="left:600px">${ic('plug', '', 'b')}MCP</div>
</div>

<div class="sc lt" id="sc-same">
  <div class="same">${[0, 1, 2].map((k) => `<div class="ph p${k}"><div class="who">${ic('user', '', 'f')}</div><div class="spk">${ic('sparkle', '', 'f')}</div><div class="sub"><i></i><i></i></div></div>`).join('')}</div>
  <div class="pill limep pp h" style="left:330px;top:1060px">${ic('user', '', 'f')}человек в кадре</div>
</div>

<div class="sc lt" id="sc-refs">
  <div class="refs"><div class="refcol">${Array.from({ length: 21 }, (_, k) => refTile(k)).join('')}</div></div>
  <div class="pill white clock h"><div class="dial"><b></b></div>часы поиска</div>
  <div class="cursor">${CURSOR}</div>
</div>

<div class="sc" id="sc-design">
  <div class="pill limep dtag h">${ic('palette', '', 'b')}дизайнер-агент</div>
  <div class="dcard"><div class="dv dv0" style="opacity:1">ролик<u></u></div><div class="dv dv1">ролик</div><div class="dv dv2">&lt;ролик/&gt;</div><div class="dv dv3"><em></em><span>ролик</span></div></div>
</div>

<div class="sc lt" id="sc-uniq">
  <div class="fan">${[['fan1', 0], ['fan3', 2], ['fan2', 1]].map(([f, k]) => `<div class="fp f${k}"><img src="${A}/real/${f}.jpg"></div>`).join('')}</div>
  <div class="pill white made h">собрано в <span class="cl">Claude</span> Code</div>
</div>

<div class="sc" id="sc-check">
  <div class="strip">${STRIP.map((f, k) => `<div class="fr fr${k}" style="left:${k * 210}px"><img src="${A}/real/${f}.jpg">${k === BAD ? '<i class="shift"></i>' : ''}<div class="ok">${ic('check', '', 'b')}</div>${k === BAD ? `<div class="no">${ic('x', '', 'b')}</div>` : ''}</div>`).join('')}</div>
  <div class="scan"><b></b></div>
  <div class="pill limep chk h">${ic('eye', '', 'b')}проверяющий</div>
  <div class="pill redo h">${ic('arrow-counter-clockwise', '', 'b')}на переделку</div>
</div>

<div class="sc" id="sc-path">
  <div class="rail" style="top:580px;height:640px"><b></b></div>
  ${STEPS.map(([icon, name], k) => `<div class="step st${k}" style="top:${520 + k * 160}px"><div class="dot">${ic(icon, '', 'b')}</div><div class="nm">${name}</div></div>`).join('')}
  <div class="pill limep sys h">${ic('users-three', '', 'b')}команда агентов</div>
</div>

<div class="sc lt" id="sc-pack">
  <div class="pill white item i0 h" style="left:110px;top:520px">${ic('users-three', '', 'b')}агенты</div>
  <div class="pill white item i1 h" style="left:560px;top:520px">${ic('puzzle-piece', '', 'b')}скилы</div>
  <div class="pill white item i2 h" style="left:300px;top:660px">${ic('gear', '', 'b')}настройки</div>
  <div class="folder h"><svg viewBox="0 0 256 256" fill="currentColor">${FILL['folder-simple']}</svg><span class="h">система</span></div>
</div>

<div class="sc lt" id="sc-cta">
  <div class="tg h"><div class="top"><div class="tgi" style="background:none;color:#2AABEE;font-size:140px">${ic('telegram-logo', '', 'f')}</div><div><div class="t1">Telegram</div><div class="t2">вся система внутри</div></div></div>
    <div class="go">ссылка в профиле ${ic('arrow-up-right', '', 'b')}<b></b></div></div>
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
  const REST = { x: 0, y: 0, scale: 1, rotation: 0, rotationX: 0, filter: 'blur(0px)' };
  const inn = (el, t, from = { y: 40 }, duration = 0.5, ease = 'power3.out') => {
    const to = { opacity: 1, duration, ease };
    Object.keys(from).forEach((k) => { to[k] = REST[k]; });
    return tl.fromTo(el, { opacity: 0, ...from }, to, t);
  };
  const out = (el, t, duration = 0.25, more = {}) => tl.to(el, { opacity: 0, duration, ease: 'power2.in', ...more }, t);
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

  // 1–2. Стена вопросов с нулевого кадра; на «кто» приходит главный вопрос. На «Отвечаю» он уезжает вверх,
  // печатается ответ «Никто», под ним встаёт карточка Claude Code.
  {
    const sc = SC.hook, ask = w('hook', 3) - 0.12, up = s('who');
    tl.fromTo($('.wall', sc), { scale: 1, y: 0 }, { scale: 1.08, y: -30, duration: up + 0.4, ease: 'power1.out', transformOrigin: '50% 50%' }, 0);
    tl.set($('.qb', sc), { transformOrigin: '0% 100%' }, 0);
    inn($('.qb', sc), ask, { y: 90, scale: 0.9 }, 0.5, 'expo.out');
    tl.fromTo($('.qb .badge', sc), { scale: 0 }, { scale: 1, duration: 0.3, ease: 'expo.out' }, ask + 0.25);
    tl.to($('.wall', sc), { opacity: 0.22, filter: 'blur(8px)', duration: 0.45, ease: 'power2.out' }, up);
    tl.to($('.qb', sc), { y: -330, scale: 0.8, duration: 0.55, ease: 'power3.inOut' }, up);
    tl.to($('.qb .badge', sc), { scale: 0, duration: 0.2 }, up);
    tl.set($('.ans', sc), { transformOrigin: '100% 100%' }, 0);
    inn($('.ans', sc), w('who', 0) + 0.05, { y: 60, scale: 0.9 }, 0.45, 'expo.out');
    tl.set($('.ans .nt', sc), { opacity: 0 }, 0);
    $$('.ans .dots i', sc).forEach((d, k) => tl.fromTo(d, { y: 0 }, { y: -12, duration: 0.18, ease: 'sine.inOut', yoyo: true, repeat: 3 }, w('who', 0) + 0.15 + k * 0.08));
    tl.to($('.ans .dots', sc), { opacity: 0, duration: 0.1 }, w('who', 1) - 0.08);
    tl.to($('.ans .nt', sc), { opacity: 1, duration: 0.15 }, w('who', 1) - 0.05);
    inn($('.ccard', sc), w('who', 2) - 0.1, { y: 120 }, 0.55, 'expo.out');
    tl.fromTo($('.ccard .seal svg', sc), { rotation: -40 }, { rotation: 0, duration: 0.9, ease: 'power3.out' }, w('who', 2) - 0.05);
  }

  // 3–4. Карточку «генерирую видео» перечёркивает линия; её сменяет код, строки печатаются;
  // на «сам собирает» код уходит, встают дорожки монтажа и превью, бегунок проходит, «ролик собран».
  {
    const sc = SC.code, t = s('code'), swap = w('code', 7) - 0.1, sel = s('self');
    inn($('.gen', sc), t, { y: 60, scale: 0.95 }, 0.5);
    tl.fromTo($('.gen .lab b', sc), { x: 0 }, { x: 1100, duration: 1.4, ease: 'none', repeat: 1 }, t + 0.2);
    draw($('.strike path', sc), w('code', 5) - 0.05, 0.45, 'power3.inOut');
    tl.to($('.gen', sc), { x: -180, rotation: -4, opacity: 0, filter: 'blur(8px)', duration: 0.4, ease: 'power2.in' }, swap);
    tl.to($('.strike', sc), { x: -180, opacity: 0, duration: 0.4, ease: 'power2.in' }, swap);
    inn($('.code', sc), swap + 0.12, { x: 160 }, 0.5, 'expo.out');
    // код печатается целиком до смены сцены: строки по 0,12 с с «Он пишет»
    $$('.code .ln', sc).forEach((ln, k) => tl.fromTo(ln, { clipPath: 'inset(0% 100% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 0.2, ease: 'none' },
      swap + 0.25 + k * 0.12));
    tl.to($('.code', sc), { y: -60, scale: 0.92, opacity: 0, filter: 'blur(8px)', duration: 0.35, ease: 'power2.in' }, sel - 0.2);
    inn($('.prev', sc), sel + 0.02, { y: 80, scale: 0.94 }, 0.5, 'expo.out');
    inn($('.edit', sc), sel + 0.1, { y: 140 }, 0.55, 'expo.out');
    const a = sel + 0.35, b = e('self') - 0.45;
    tl.fromTo($('.edit .head', sc), { x: 0 }, { x: 690, duration: b - a, ease: 'none' }, a);
    tl.to($('.pv1', sc), { opacity: 1, duration: 0.12 }, a + (b - a) * 0.36);
    tl.to($('.pv2', sc), { opacity: 1, duration: 0.12 }, a + (b - a) * 0.7);
    pop($('.done', sc), b - 0.05);
  }

  // 5. Хайп: звезда и слово Claude, вокруг поднимаются сердца.
  {
    const sc = SC.hype, t = s('hype'), end = e('hype');
    inn($('.hword', sc), t + 0.05, { y: 60, scale: 0.94 }, 0.55, 'expo.out');
    inn($('.hstar', sc), t, { scale: 0.7 }, 0.55, 'expo.out');
    tl.fromTo($('.hstar', sc), { rotation: -30 }, { rotation: 30, duration: end - t, ease: 'power1.out' }, t);
    HEARTS.forEach((h, k) => {
      const at = t + 0.1 + h.d * (end - t - 0.9);
      const el = $('.hr' + k, sc);
      tl.fromTo(el, { opacity: 0, y: 80, scale: 0.8 }, { opacity: 0.95, y: 0, scale: 1, duration: 0.45, ease: 'expo.out' }, at);
      tl.to(el, { y: -90, opacity: 0, duration: 0.9, ease: 'power1.in' }, at + 0.5);
    });
  }

  // 6. «Сделай ролик»: буквы печатаются на своих словах, курсор жмёт «отправить», ждём.
  {
    const sc = SC.try, t = s('try'), a = w('try', 4), b = w('try', 6) + 0.35;
    inn($('.inp', sc), t, { y: 50, scale: 0.96 }, 0.5);
    const chars = $$('.tx i', sc);
    chars.forEach((c, k) => tl.set(c, { opacity: 1 }, a + (k / chars.length) * (b - a)));
    blink($('.inp .caret', sc), t + 0.2, a);
    const click = w('try', 7);
    cursorTo($('.cursor', sc), [[760, 900, b - 0.2], [890, 620, click, true]]);
    tl.to($('.inp .send', sc), { scale: 0.88, duration: 0.08, yoyo: true, repeat: 1 }, click);
    tl.to($('.inp .caret', sc), { opacity: 0, duration: 0.05 }, click);
    inn($('.wait', sc), click + 0.15, { y: 80 }, 0.5, 'expo.out');
    tl.fromTo($('.wait .ring', sc), { rotation: 0 }, { rotation: 540, duration: e('try') - click, ease: 'none' }, click + 0.15);
    sweep($('.wait b', sc), click + 0.3, 1.1, 1200);
  }

  // 7. Нейрослоп: одинаковые плитки, штамп, на «одинаково» все качнулись разом.
  {
    const sc = SC.slop, t = s('slop');
    $$('.tile', sc).forEach((el, k) => inn(el, t + (Math.floor(k / 3) + (k % 3)) * 0.04, { y: 40, scale: 0.94 }, 0.4));
    tl.set($('.stamp', sc), { transformOrigin: '50% 50%' }, 0);
    tl.fromTo($('.stamp', sc), { opacity: 0, scale: 1.35, rotation: -12 }, { opacity: 1, scale: 1, rotation: -6, duration: 0.3, ease: 'power4.out' }, w('slop', 0) - 0.02);
    $$('.tile', sc).forEach((el) => tl.to(el, { rotation: 3, duration: 0.14, ease: 'sine.inOut', yoyo: true, repeat: 3 }, w('slop', 3) - 0.05));
  }

  // 8. Стоп: ладонь бьёт, ниже модель, маркер её перечёркивает.
  {
    const sc = SC.stop, t = s('stop');
    tl.fromTo($('.hand', sc), { opacity: 0, scale: 1.3 }, { opacity: 1, scale: 1, duration: 0.28, ease: 'power4.out' }, t);
    inn($('.model', sc), w('stop', 1) - 0.08, { y: 60 }, 0.45, 'expo.out');
    draw($('.mark path', sc), w('stop', 4) - 0.05, 0.35, 'power2.out');
  }

  // 9. Знак вопроса; к концу он сжимается, и из его центра открывается тёмная сцена команды.
  {
    const sc = SC.why, t = s('why');
    tl.set($('.qm', sc), { transformOrigin: '50% 55%' }, 0);
    tl.fromTo($('.qm', sc), { opacity: 0, scale: 0.86 }, { opacity: 1, scale: 1, duration: 0.45, ease: 'expo.out' }, t);
    tl.to($('.qm', sc), { scale: 0.25, duration: 0.45, ease: 'power3.in' }, e('why') - 0.4);
  }

  // 10–13. Кольцо: Claude в центре, пустые места встают на «команда», роли заполняются по словам,
  // снизу подключаются скилы и MCP; на «Зачем столько?» кольцо отъезжает и гаснет наполовину.
  {
    const sc = SC.team, t = s('team');
    const ring = $('.orbit circle', sc);
    tl.set($('.core', sc), { transformOrigin: '50% 50%' }, 0);
    inn($('.core', sc), t + 0.05, { scale: 0.6 }, 0.55, 'expo.out');
    inn($('.corelab', sc), t + 0.3, { y: 20 }, 0.4);
    draw(ring, t + 0.2, 1.0, 'power2.inOut');
    tl.fromTo($('.core svg', sc), { rotation: 0 }, { rotation: 90, duration: e('much') - t, ease: 'none' }, t);
    $$('.slot', sc).forEach((el, k) => {
      tl.set(el, { transformOrigin: '50% 50%' }, 0);
      tl.fromTo(el, { opacity: 0, scale: 0.7 }, { opacity: 1, scale: 1, duration: 0.35, ease: 'expo.out' }, w('team', 7) - 0.1 + k * 0.07);
    });
    const at = [w('roles', 0), w('roles', 1), w('roles', 2), w('roles', 3), w('roles', 5)];
    $$('.slot', sc).forEach((el, k) => {
      tl.fromTo($('.fill', el), { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.3, ease: 'expo.out' }, at[k] - 0.06);
      tl.fromTo($('.nm', el), { opacity: 0, y: -10 }, { opacity: 1, y: 0, duration: 0.3, ease: 'power3.out' }, at[k]);
    });
    inn($('.p1', sc), w('skills', 2) - 0.1, { y: 60 }, 0.45, 'expo.out');
    tl.set($('.ln1', sc), { opacity: 1 }, w('skills', 2) + 0.15);
    draw($('.ln1', sc), w('skills', 2) + 0.15, 0.35);
    inn($('.p2', sc), w('skills', 4) - 0.1, { y: 60 }, 0.45, 'expo.out');
    tl.set($('.ln2', sc), { opacity: 1 }, w('skills', 4) + 0.15);
    draw($('.ln2', sc), w('skills', 4) + 0.15, 0.35);
    tl.to($('.ringg', sc), { scale: 0.74, y: -40, opacity: 0.4, duration: 0.6, ease: 'power3.inOut' }, s('much') - 0.05);
    tl.to($$('.plug', sc), { opacity: 0.4, y: -120, scale: 0.8, duration: 0.6, ease: 'power3.inOut' }, s('much') - 0.05);
  }

  // 14–15. Три одинаковых ролика: качнулись разом на «одинаковые», «человек в кадре», субтитры мигнули разом,
  // искры повернулись разом.
  {
    const sc = SC.same, t = s('same');
    $$('.ph', sc).forEach((el, k) => inn(el, t + k * 0.1, { y: 100 }, 0.5, 'expo.out'));
    $$('.ph', sc).forEach((el) => tl.to(el, { scale: 1.04, duration: 0.16, ease: 'sine.inOut', yoyo: true, repeat: 1 }, w('same2', 2) - 0.05));
    pop($('.pp', sc), w('same2', 3) - 0.08);
    $$('.ph .sub', sc).forEach((el) => tl.to(el, { backgroundColor: '#C7E24B', duration: 0.15, yoyo: true, repeat: 1 }, w('same2', 6) - 0.05));
    $$('.ph .spk', sc).forEach((el) => tl.fromTo(el, { rotation: 0 }, { rotation: 180, duration: 0.5, ease: 'power2.inOut' }, w('same2', 8) - 0.05));
  }

  // 16. Референсы: сетка листается, курсор крутит колесо; на «уходят часы» встают часы, стрелка бежит.
  {
    const sc = SC.refs, t = s('refs'), end = e('refs');
    tl.fromTo($('.refcol', sc), { y: 40 }, { y: -900, duration: end - t, ease: 'power1.inOut' }, t);
    cursorTo($('.cursor', sc), [[820, 980, t + 0.2], [800, 1020, end - 0.3]]);
    pop($('.clock', sc), w('refs', 6) - 0.1);
    tl.fromTo($('.clock .dial b', sc), { rotation: 0 }, { rotation: 720, duration: end - w('refs', 6), ease: 'none' }, w('refs', 6));
  }

  // 17. Дизайнер-агент: одна карточка, слово «ролик» трижды меняет облик — фон, скругление, шрифт.
  {
    const sc = SC.design, t = s('design');
    inn($('.dcard', sc), t, { y: 120, scale: 0.94 }, 0.55, 'expo.out');
    pop($('.dtag', sc), w('design', 3) - 0.1);
    const card = $('.dcard', sc);
    const STATES = [[w('design', 5), '#12130F', 120], [w('design', 7), '#C7E24B', 18], [w('design', 9), '#1B2108', 300]];
    STATES.forEach(([at, bg, r], k) => {
      tl.to(card, { backgroundColor: bg, borderRadius: r, duration: 0.45, ease: 'power3.inOut' }, at - 0.12);
      tl.to($('.dv' + k, sc), { opacity: 0, scale: 0.9, duration: 0.2, ease: 'power2.in' }, at - 0.12);
      tl.fromTo($('.dv' + (k + 1), sc), { opacity: 0, scale: 1.1 }, { opacity: 1, scale: 1, duration: 0.35, ease: 'expo.out' }, at + 0.05);
    });
  }

  // 18. Веер: три настоящих ролика канала встают стопкой и расходятся; подпись «собрано в Claude Code».
  {
    const sc = SC.uniq, t = s('uniq'), spread = w('uniq', 1) - 0.05;
    $$('.fp', sc).forEach((el, k) => inn(el, t + k * 0.06, { y: 160 }, 0.5, 'expo.out'));
    tl.to($('.f0', sc), { x: -260, rotation: -10, duration: 0.6, ease: 'power3.inOut' }, spread);
    tl.to($('.f2', sc), { x: 260, rotation: 10, duration: 0.6, ease: 'power3.inOut' }, spread);
    tl.to($('.f1', sc), { y: -30, scale: 1.04, duration: 0.6, ease: 'power3.inOut' }, spread);
    pop($('.made', sc), w('uniq', 5) - 0.1);
  }

  // 19. Проверка: лента кадров идёт под рамкой, каждый принятый получает галочку; бракованный поднимается,
  // получает крест и уезжает назад «на переделку».
  {
    const sc = SC.check, t = s('check'), end = e('check');
    const t0 = t + 0.4, tb = w('check', 5) - 0.05;
    const v = (BAD * 210) / (tb - t0);
    const X = (time) => 445 - v * (time - t0);
    tl.fromTo($('.strip', sc), { x: X(t) }, { x: X(end), duration: end - t, ease: 'none' }, t);
    pop($('.chk', sc), t + 0.15);
    tl.fromTo($('.scan b', sc), { y: 0 }, { y: 330, duration: 0.7, ease: 'sine.inOut', yoyo: true, repeat: Math.floor((end - t) / 0.7) }, t);
    STRIP.forEach((_, k) => {
      const at = t0 + (k * 210) / v;
      if (at > end - 0.2) return;
      if (k === BAD) return;
      tl.fromTo($('.fr' + k + ' .ok', sc), { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: 0.25, ease: 'expo.out' }, at);
    });
    const bad = $('.fr' + BAD, sc);
    tl.to($('.shift', bad), { opacity: 1, duration: 0.1 }, tb - 0.3);
    tl.fromTo($('.no', bad), { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: 0.25, ease: 'expo.out' }, tb);
    tl.to(bad, { y: -110, borderColor: '#E5544B', duration: 0.35, ease: 'power3.out' }, w('check', 6) - 0.1);
    tl.to(bad, { x: -900, opacity: 0, duration: 0.7, ease: 'power2.in' }, w('check', 7) - 0.05);
    pop($('.redo', sc), w('check', 7) - 0.05);
  }

  // 20. Путь: пять шагов загораются на своих словах, полоса растёт; на «делает система» — «команда агентов».
  {
    const sc = SC.path, t = s('path');
    $$('.step', sc).forEach((el, k) => inn(el, t + k * 0.05, { x: -40 }, 0.45, 'expo.out'));
    inn($('.rail', sc), t, { scaleY: 0.6 }, 0.4);
    $$('.step', sc).forEach((el, k) => {
      const at = w('path', k) - 0.05;
      tl.to($('.dot', el), { backgroundColor: '#C7E24B', color: '#12130F', borderColor: '#C7E24B', scale: 1.06, duration: 0.25, ease: 'expo.out' }, at);
      tl.to($('.dot', el), { scale: 1, duration: 0.3, ease: 'power2.out' }, at + 0.25);
      tl.to($('.nm', el), { color: '#F1F2EA', duration: 0.25 }, at);
      tl.to($('.rail b', sc), { scaleY: k / 4, duration: 0.3, ease: 'power2.out' }, at);
    });
    pop($('.sys', sc), w('path', 7) - 0.1);
  }

  // 21. Агенты, скилы, настройки встают на своих словах и на «собрал» улетают в одну папку «система».
  {
    const sc = SC.pack, t = s('pack');
    inn($('.folder', sc), t + 0.1, { y: 100, scale: 0.94 }, 0.5, 'expo.out');
    [0, 1, 3].forEach((wi, k) => pop($('.i' + k, sc), w('pack', wi) - 0.08));
    const C = [[230, 568], [675, 568], [460, 708]];
    const go = w('pack', 5) - 0.05;
    $$('.item', sc).forEach((el, k) => tl.to(el, { x: 540 - C[k][0], y: 1080 - C[k][1], scale: 0.35, opacity: 0, duration: 0.5, ease: 'power3.in' }, go + k * 0.1));
    tl.set($('.folder', sc), { transformOrigin: '50% 70%' }, 0);
    tl.to($('.folder', sc), { scale: 1.05, duration: 0.18, ease: 'power2.out', yoyo: true, repeat: 1 }, go + 0.55);
    inn($('.folder span', sc), w('pack', 7) - 0.1, { y: 20 }, 0.35);
  }

  // 22. Финал: карточка Telegram, курсор жмёт «ссылка в профиле», потом «сохрани»; кот показывает лапой.
  {
    const sc = SC.cta, t = s('cta');
    inn($('.tg', sc), t, { y: 120, scale: 0.95 }, 0.55, 'expo.out');
    inn($('.cat', sc), t + 0.3, { x: -160 }, 0.6, 'expo.out');
    tl.set($('.cat', sc), { scaleX: -1 }, 0);
    tl.fromTo($('.cat', sc), { y: 0 }, { y: -10, duration: 1.4, ease: 'sine.inOut', yoyo: true, repeat: Math.max(0, Math.floor((L - t - 1) / 1.4)) }, t + 0.9);
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
