// Ролик «Маск согласился: Grok хуже» (r13). Рерайт рилса instagram.com/reel/DeBhoSnRegX, движок HyperFrames.
//
// Разбор референса и что заменено: ../РЕФЕРЕНС.md, текст по ролям: ../ОЗВУЧКА.md.
// Тезис: состояние — одна фраза голоса, движется то, о чём говорят. Рейтинг проходится снизу
// вверх, как у автора: отдельный ранг Google, E, размазанный Grok, A, S, SS и один SSS на вершине.
// Цвета рангов взяты с тир-листа (это примета темы), всё остальное наше: графит, крем, лайм, олива,
// Unbounded для крупного, Onest для остального, знак канала в углу, кот в финале.
// Зерна, вспышек и конфетти нет (README, «Приёмы на пробу»: запреты из чужого вкуса).
// Всё записано твинами без обратных вызовов: перемотка в любую секунду даёт верный кадр.
// Селекторы склеиваются плюсом, а не шаблонной строкой: на ней падает разбор HyperFrames.

// Знаки моделей: набор @lobehub/icons-static-svg (MIT), файлы в public/rating/m. Двух знаков в наборе
// нет (Thinking Machines, K2 Horizon): у них плитка с буквами, знак по памяти не рисуется.
const FILE = {
  claude: 'claude.svg', openai: 'openai.svg', grok: 'grok.svg', gemini: 'gemini-color.svg', kimi: 'kimi-color.svg',
  qwen: 'qwen-color.svg', zhipu: 'zhipu-color.svg', meta: 'meta-color.svg', deepseek: 'deepseek-color.svg',
  hunyuan: 'hunyuan-color.svg', minimax: 'minimax-color.svg', mistral: 'mistral-color.svg', nvidia: 'nvidia-color.svg',
  mimo: 'xiaomimimo.svg', google: 'google-color.svg',
};

// Тир-лист как у автора (кадр 12,4 с референса). Проценты голосов у автора есть, у нас не ставятся.
export const TIERS = [
  ['SSS', '#E95BE6', [['Opus 5.5', 'claude']]],
  ['SS', '#C47BEA', [['GPT-6<br>Astra', 'openai']]],
  ['S', '#F08C8C', [['Fable 5.1', 'claude'], ['GPT-6<br>Sol', 'openai']]],
  ['A', '#F6C684', [['Opus 5', 'claude'], ['Fable 5', 'claude'], ['GPT-5.6<br>Sol', 'openai'], ['Kimi K3', 'kimi'], ['Grok 4.6', 'grok'], ['Qwen3.8<br>Max', 'qwen'], ['GLM-5.3', 'zhipu'],
    ['GPT-6<br>Luna', 'openai'], ['Muse Spark<br>1.3', 'meta'], ['DeepSeek<br>V4.1 Flash', 'deepseek'], ['Hy-4<br>Preview', 'hunyuan'], ['Grok 4.7', 'grok']]],
  ['B', '#F2EE9C', [['GPT-5.6<br>Terra', 'openai'], ['Qwen3.8<br>Flash', 'qwen'], ['GLM-5.3<br>Flash', 'zhipu'], ['Sonnet 5', 'claude'], ['K2<br>Horizon', 'tx:K2']]],
  ['C', '#CDEB8B', [['GPT-5.6<br>Luna', 'openai'], ['Grok 4.5', 'grok'], ['Qwen3.8<br>27B', 'qwen'], ['Muse Spark<br>1.2', 'meta'], ['MiMo V2.5<br>Pro', 'mimo'], ['Hy-3', 'hunyuan'], ['MiniMax<br>M3', 'minimax']]],
  ['D', '#9DE39A', [['Inkling', 'tx:TM'], ['Nemotron 3<br>Ultra', 'nvidia'], ['Muse<br>Glimmer', 'meta']]],
  ['E', '#8CE6E2', [['Haiku 4.5', 'claude'], ['Mistral<br>Medium 3.5', 'mistral'], ['Nemotron 3.5<br>Lightning', 'nvidia']]],
  ['Google', '#8EC9F2', [['Gemini 3.8<br>Flash', 'gemini'], ['Gemini 3.7<br>Flash', 'gemini'], ['Gemini 3.6<br>Flash', 'gemini'], ['Gemini 3.5<br>Flash', 'gemini']]],
];
const T_ = Object.fromEntries(TIERS.map((t) => [t[0], t]));
// бегунок рангов внизу кадра: снизу вверх
const LADDER = ['Google', 'E', 'D', 'C', 'B', 'A', 'S', 'SS', 'SSS'];

const slug = (name) => name.replace(/<br>/g, ' ').toLowerCase().replace(/[^a-z0-9]/g, '');
const cls = (t) => 't-' + t.toLowerCase();

/** Плитка модели: знак на тёмной плитке, у Claude плитка терракотовая (как у автора), подпись под ней. */
const tile = (A, [name, logo], extra = '') => {
  const tx = logo.startsWith('tx:');
  return `<div class="mt m-${slug(name)} ${extra}"><div class="ic ${logo === 'claude' ? 'cl' : ''} ${tx ? 'tx' : ''}">${
    tx ? logo.slice(3) : `<img src="${A}/m/${FILE[logo]}">`}</div><b>${name}</b><u></u></div>`;
};
const row = (A, t, extra = '') => `<div class="tr ${cls(t[0])} ${extra}"><div class="lb${t[0] === 'Google' ? ' g' : ''}" style="background:${t[1]}">${t[0]}</div><div class="ts">${t[2].map((m) => tile(A, m)).join('')}</div></div>`;
const list = (A, names, extra = '', style = '') => `<div class="tl ${extra}" style="${style}">${names.map((n) => row(A, T_[n])).join('')}</div>`;
// Уменьшенный тир-лист целиком: проверка HyperFrames меряет подписи без учёта масштаба обёртки и видит
// их в зоне субтитров, которых они в кадре не касаются. Помечаем именно эти подписи, а не сцену.
const mini = (html) => html.replaceAll('<b>', '<b data-layout-allow-overlap>').replaceAll('class="lb', 'data-layout-allow-overlap class="lb');
// Закрытая вершина (четвёртая версия): кто первый, зритель узнаёт только на вершине подъёма.
const MYS = ['???', 'tx:?'];
const rowMys = (A) => `<div class="tr t-sss solo"><div class="lb" style="background:${T_.SSS[1]}">SSS</div><div class="ts">${tile(A, MYS, 'mys')}</div></div>`;
// Колонна подъёма: весь рейтинг сверху вниз. На вершине под «?» лежит Opus 5.5, у Google справа пустое место буквы F.
const column = (A) => `<div class="tl col">${LADDER.slice().reverse().map((n) => {
  if (n === 'SSS') return `<div class="tr t-sss"><div class="lb" style="background:${T_.SSS[1]}">SSS</div><div class="ts"><div class="flip">${tile(A, T_.SSS[2][0], 'opus')}${tile(A, MYS, 'mys')}</div></div></div>`;
  if (n === 'Google') return row(A, T_.Google).replace(/<\/div><\/div>$/, `<div class="fslot"><span>F</span><svg viewBox="0 0 104 140"><path class="fstrike" d="M10 112 L94 26" fill="none" stroke="#F08C8C" stroke-width="9" stroke-linecap="round"/></svg></div></div></div>`);
  return row(A, T_[n]);
}).join('')}</div>`;
const label = (n, extra = '', style = '') => `<div class="lbx ${extra}${n === 'Google' ? ' g' : ''}" style="background:${T_[n][1]};${style}">${n}</div>`;

const PLANE = '<svg viewBox="0 0 24 24"><path d="M21.900 3.300 2.700 10.700c-1.300.500-1.300 1.300-.200 1.600l4.900 1.500 1.900 5.800c.200.700.400.900.900.900.400 0 .600-.200.900-.500l2.300-2.300 4.900 3.600c.900.500 1.500.200 1.800-.800l3.200-15.200c.300-1.300-.500-1.900-1.400-2zM8.300 13.500l10-6.300c.500-.300.900-.100.500.200l-8.200 7.400-.300 3.400z"/></svg>';
const BADGE = '<svg class="vb" viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="#1D9BF0"/><path d="M7 12.300l3.200 3.200L17 8.700" fill="none" stroke="#fff" stroke-width="2.600" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const EYE = '<svg viewBox="0 0 24 24"><path d="M1.500 12S5.500 4.500 12 4.500 22.500 12 22.500 12 18.500 19.500 12 19.500 1.500 12 1.500 12z" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="3.400" fill="currentColor"/></svg>';
const SEND = '<svg viewBox="0 0 24 24"><path d="M3 11.500 20.500 3.500 13 21l-2.200-7.300z" fill="currentColor"/></svg>';
const SAVE = '<svg viewBox="0 0 24 24"><path d="M6 3h12v18l-6-4.500L6 21z"/></svg>';

// Псевдослучайное число по зерну: одно и то же в каждой вкладке рендера.
const rnd = (seed) => { const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

/** Разметка всех сцен. A — адрес папки с картинками. */
export const markup = (A) => `
<div class="bg bg-light"></div>
<div class="glow glow-lime" data-layout-ignore><i></i></div><div class="glow glow-news" data-layout-ignore style="opacity:1"><i></i></div><div class="glow glow-amber" data-layout-ignore><i></i></div><div class="glow glow-violet" data-layout-ignore><i></i></div><div class="glow glow-blue" data-layout-ignore><i></i></div><div class="glow glow-mint" data-layout-ignore><i></i></div><div class="glow glow-warm" data-layout-ignore><i></i></div>
<div class="vignette" style="opacity:1"></div>
<div class="ghostbg" data-layout-ignore><div class="gl">ABCABCA</div><div class="gl" style="margin-left:-260px">CBACBAC</div><div class="gl">BCACEAB</div></div>
<div class="spot" data-layout-ignore></div>

<div class="sc" id="sc-hook" style="opacity:1">
  <div class="abs floats" data-layout-ignore style="inset:0">${[['claude', 40, 560, -9], ['openai', 880, 610, 8], ['gemini', 90, 1150, 7], ['grok', 850, 1080, -7], ['deepseek', 300, 1330, 5], ['kimi', 720, 1350, -5]].map(([l, x, y, r]) =>
    `<div class="flt ${l === 'claude' ? 'cl' : ''}" style="left:${x}px;top:${y}px;transform:rotate(${r}deg)"><img src="${A}/m/${FILE[l]}"></div>`).join('')}</div>
  <div class="hk"><div class="k1">Илон Маск</div><div class="k2">сам признал</div></div>
  <div class="hk hk2"><div class="k1"><span class="h">Grok</span> <span class="h">хуже,</span></div><div class="k3"><span class="h">чем</span> <span class="h">у</span> <span class="h">конкурентов</span></div></div>
  <div class="ph abs" style="left:330px;top:480px"><div class="phone xreal"><img src="${A}/x/app-musk.png"><div class="said"></div></div></div>
  <div class="vs abs h" style="left:0;top:560px;width:1080px">
    <div class="abs vs1" style="left:419px;top:0">${rowMys(A)}</div>
    <div class="abs" style="left:0;top:250px;width:1080px;text-align:center"><span class="down pill h"><b>↓</b> на 3 ранга ниже</span></div>
    <div class="abs vs2" style="left:124px;top:380px;width:833px;height:286px"><div style="transform:scale(0.9);transform-origin:0 0;width:max-content">${list(A, ['A'], 'cut')}</div></div>
  </div>
  <div class="abs gptx h" style="left:420px;top:920px;width:240px;height:322px"><div style="transform:scale(2.3);transform-origin:0 0;width:max-content">${tile(A, ['ChatGPT', 'openai'])}</div>
    <svg viewBox="0 0 198 198" style="position:absolute;left:0;top:-4px;width:240px;height:240px;overflow:visible"><path class="x1" d="M22 22 L176 176" fill="none" stroke="#F08C8C" stroke-width="14" stroke-linecap="round"/><path class="x2" d="M176 22 L22 176" fill="none" stroke="#F08C8C" stroke-width="14" stroke-linecap="round"/></svg></div>
</div>

<div class="sc" id="sc-post">
  <div class="tab abs h xreal2" style="left:290px;top:430px;width:500px;height:860px"><img src="${A}/x/app-deep.png"><div class="vring"></div></div>
  <div class="vfade" data-layout-ignore></div>
</div>

<div class="sc" id="sc-musk">
  <div class="card glass abs h" style="left:110px;top:480px;width:860px;height:182px;padding:0;overflow:hidden"><img src="${A}/x/app-musk-head.png" style="width:860px;display:block;background:#000"></div>
  <div class="acc" style="left:0;top:720px;width:1080px;text-align:center;font-size:96px"><span class="h">Accurate</span> <span class="fn h">(for now)</span></div>
  <div class="tr2 pill h" style="position:absolute;left:0;top:900px;width:1080px;background:none;border:none;justify-content:center"><span class="tp">Точно.</span><span class="tp2">Пока что</span></div>
</div>

<div class="sc" id="sc-climb">
  <div class="rays abs" data-layout-ignore style="left:140px;top:470px;width:800px;height:800px"></div>
  <div class="cam abs" data-layout-ignore style="left:0;top:0;width:926px"><div class="colw" style="position:relative">${mini(column(A))}
    <svg class="gp" viewBox="0 0 10 10" style="position:absolute;left:0;top:0;width:10px;height:10px;overflow:visible"><path class="gpath" d="M0 0 L1 1" fill="none" stroke="#C7E24B" stroke-width="5" stroke-linecap="round"/></svg></div></div>
  ${Array.from({ length: 14 }, (_, i) => `<i class="spk h" data-layout-ignore style="left:${Math.round(160 + rnd(i + 51) * 760)}px;top:${Math.round(560 + rnd(i + 77) * 560)}px"></i>`).join('')}
  <div class="cfade" data-layout-ignore></div>
  <div class="cpill pill h" style="position:absolute;left:0;top:1150px;width:1080px;background:none;border:none;justify-content:center"><span class="cl">Claude Opus 5.5</span></div>
</div>

<div class="sc" id="sc-fight">
  ${[['Opus 5.5', 'claude', 250, 520, -8], ['GPT-6<br>Astra', 'openai', 590, 500, 9], ['Fable 5.1', 'claude', 230, 840, 7], ['GPT-6<br>Sol', 'openai', 600, 830, -9]].map(([n, l, x, y, r], i) =>
    `<div class="abs fwrap" style="left:${x}px;top:${y}px"><div style="transform:rotate(${r}deg)"><div class="fgt f${i} h" style="width:198px;height:266px"><div style="transform:scale(1.9);transform-origin:0 0;width:max-content">${tile(A, [n, l])}</div></div></div></div>`).join('')}
  ${Array.from({ length: 6 }, (_, i) => `<i class="spark h" data-layout-ignore style="left:${520 + Math.round(Math.cos(i) * 40)}px;top:${770 + Math.round(Math.sin(i) * 40)}px;transform:rotate(${i * 60}deg)"></i>`).join('')}
</div>

<div class="sc light" id="sc-siri">
  <div class="siri glass abs h" style="left:160px;top:520px;width:760px;height:560px">
    <div class="sorb"></div>
    <div class="sname">Siri</div>
    <div class="sq">Какая сегодня погода?</div>
    <div class="sline"><span class="spin"></span><span>Ищу ответ в интернете</span><span class="dots"><i>.</i><i>.</i><i>.</i></span></div>
    <div class="skel" style="top:390px;width:600px"><i></i></div><div class="skel" style="top:440px;width:470px"><i></i></div><div class="skel" style="top:490px;width:540px"><i></i></div>
  </div>
</div>

<div class="sc" id="sc-q">
  <div class="cbox glass abs h" style="left:150px;top:520px;width:780px;height:560px">
    <div class="inp"><i class="avc"><img src="${A}/cat-face.png"></i><div class="field"><span class="ph2">Мой ранг:</span> ${[...'SSS — Claude'].map((c) => `<span class="ch h">${c === ' ' ? '&nbsp;' : c}</span>`).join('')}</div></div>
    <div class="rk">${LADDER.slice().reverse().map((n) => `<span class="rkc h${n === 'SSS' ? ' on' : ''}${n === 'Google' ? ' g' : ''}">${n}</span>`).join('')}</div>
    <div class="sendb h">${SEND}Отправить</div>
  </div>
  <i class="cur h" data-layout-ignore></i>
</div>

<div class="sc" id="sc-share">
  <div class="sbox glass abs h" style="left:150px;top:520px;width:780px;height:560px">
    <div class="st">Поделиться</div>
    <div class="avs">${[0, 1, 2, 3].map((i) => `<i class="av2 avp h" style="--c:${['#F1F2EA', '#89A81C', '#D97757', '#C7E24B'][i]}"><svg viewBox="0 0 24 24"><circle cx="12" cy="8.5" r="4.2" fill="currentColor"/><path d="M3.8 21c.9-4.300 4.300-6.400 8.200-6.400s7.300 2.100 8.200 6.400z" fill="currentColor"/></svg>${i === 3 ? '<u></u>' : ''}</i>`).join('')}</div>
    <div class="msg"><span class="ph3">Сообщение</span>${[...'Siri, какая погода?'].map((c) => `<span class="ch h">${c === ' ' ? '&nbsp;' : c}</span>`).join('')}</div>
    <div class="sendb h" style="top:440px">${SEND}Отправить</div>
  </div>
  <i class="cur h" data-layout-ignore></i>
</div>

<div class="sc" id="sc-cta">
  <div class="first abs" style="inset:0">
    <div class="tab abs h mini2" style="left:366px;top:470px;width:348px;height:632px"><div style="transform:scale(0.355);transform-origin:0 0;width:max-content">${mini(list(A, LADDER.slice().reverse()))}</div></div>
    <div class="cap h c1" style="top:1124px;font-size:58px"><span style="color:var(--lime)">Весь рейтинг</span> одной картинкой</div>
  </div>
  <div class="tg h" style="left:310px;top:440px">${PLANE}</div>
  <div class="point abs h" style="left:660px;top:420px;width:226px"><img src="${A}/cat-point.png" style="width:100%;filter:drop-shadow(0 30px 40px rgba(0,0,0,.5))"></div>
  <div class="abs tgt" style="left:0;top:770px;width:1080px;text-align:center"><div class="h t1" style="font-size:80px;line-height:1">Telegram</div><div class="h t2" style="font-size:56px;color:var(--lime);margin-top:18px">@FourXtube</div></div>
  <div class="go h" style="top:990px"><span>Ссылка в профиле<div class="shim"></div></span></div>
  <div class="save h" style="top:1150px"><span>${SAVE}Сохрани, чтобы не потерять</span></div>
</div>
`;

// Светлая только Siri (четвёртая версия): подъём по рейтингу идёт одной тёмной сценой, свет меняет пятно.
const LIGHT = ['siri'];

/** Заголовок сверху: слово встаёт, когда звучит. Номера слов — по тексту голоса (voice/r13.json). */
export const headlines = (T) => {
  const w = (id, i) => T.w[id][i];
  const s = (id) => T.scenes[id].s;
  const e = (id) => T.scenes[id].e;
  const H = (id, l1, l2 = []) => ({ id, light: LIGHT.includes(id), from: s(id), to: e(id), l1, l2 });
  return [
    H('tease', [['Первое', w('tease', 1)], ['место', w('tease', 2)]], [['не', w('tease', 5)], ['у', w('tease', 6)], ['ChatGPT', w('tease', 7), 'lm']]),
    { ...H('post', [['Разработчик', w('post', 0)]], [['выложил', w('post', 1)], ['рейтинг', w('post', 2)]]), to: e('views') },
    H('musk', [['Маск', w('musk', 1)], ['ответил', w('musk', 2)]]),
    H('look', [['Идём', w('look', 0)]], [['снизу', w('look', 1)], ['вверх', w('look', 2), 'lm']]),
    H('google', [['В', w('google', 0)], ['самом', w('google', 1)], ['низу', w('google', 2)]], [['ранг', w('google', 4)], ['Google', w('google', 9), 'gg']]),
    H('gem', [['Там', w('gem', 0)], ['все', w('gem', 1)], ['Gemini', w('gem', 2), 'gg']], [['букву', w('gem', 5)], ['F', w('gem', 6), 'gg'], ['пожалели', w('gem', 7)]]),
    H('grok', [['Grok', w('grok', 0)], ['Маска', w('grok', 2)]], [['от', w('grok', 5)], ['C', w('grok', 6), 'lm'], ['до', w('grok', 7)], ['A', w('grok', 8), 'lm']]),
    H('s', [['Выше,', w('s', 0)], ['в', w('s', 1)], ['S', w('s', 2), 'lm']], [['Fable', w('s', 4)], ['и', w('s', 7)], ['GPT-6 Sol', w('s', 8)]]),
    H('ss', [['Ещё', w('ss', 0)], ['выше', w('ss', 1)]], [['GPT-6', w('ss', 2)], ['Astra', w('ss', 4)]]),
    H('top', [['На', w('top', 1)], ['вершине', w('top', 3)]], [['только', w('top', 4)], ['один', w('top', 5), 'lm']]),
    H('fight', [['Бьются', w('fight', 2)]], [['за', w('fight', 3)], ['SSS', w('fight', 4), 'lm']]),
    H('siri', [['Ну', w('siri', 0)], ['а', w('siri', 1)], ['Siri', w('siri', 2)]], [['пока', w('siri', 3)], ['что', w('siri', 4)], ['ищет', w('siri', 5)]]),   // владелец 04.10: «ну а Siri, пока что…» — так шутка понятна
    H('q', [['А', w('q', 0)], ['ты', w('q', 1)], ['на', w('q', 2)], ['какой?', w('q', 3)]], [['Пиши', w('q', 6)], ['свой', w('q', 9)], ['ранг', w('q', 10), 'lm']]),
    H('share', [['Скинь', w('share', 1)], ['другу', w('share', 2)]]),
  ];
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
  const inn = (el, t, from = { y: 40 }, duration = 0.6, ease = 'power3.out') => {
    const to = { opacity: 1, duration, ease };
    Object.keys(from).forEach((k) => { to[k] = REST[k]; });
    return tl.fromTo(el, { opacity: 0, ...from }, to, t);
  };
  const pop = (el, t) => { tl.set(el, { transformOrigin: '50% 50%' }, 0); return inn(el, t, { scale: 0.8, y: 16 }, 0.45, 'back.out(1.25)'); };
  const word = (el, t) => inn(el, t - 0.06, { y: 18, filter: 'blur(10px)' }, 0.34);
  const draw = (el, t, duration, ease = 'power2.inOut') => {
    const len = el.getTotalLength();
    return tl.fromTo(el, { strokeDasharray: len, strokeDashoffset: len }, { strokeDashoffset: 0, duration, ease }, t);
  };
  // Подсветка модели: кольцо лайма и плитка чуть крупнее; остальные в блоке гаснут.
  // Обводка загорается, плитка стоит на месте: рост плитки с пружиной сдвигал рамку и подписи соседей,
  // и обводка будто сползала (владелец 04.10).
  const hi = (el, t) => {
    tl.to($('u', el), { opacity: 1, duration: 0.2, ease: 'power2.out' }, t);
  };
  const lo = (el, t) => {
    tl.to($('u', el), { opacity: 0, duration: 0.2 }, t);
  };
  const dim = (els, t, to = 0.3) => tl.to(els, { opacity: to, duration: 0.35, ease: 'power2.out' }, t);
  const type = (chars, a, b) => chars.forEach((c, i) => tl.set(c, { opacity: 1 }, a + (i * (b - a)) / Math.max(1, chars.length)));

  // Сцены (четвёртая версия): девять больших кадров вместо двадцати. Рейтинг — одна сцена подъёма
  // с «идём снизу вверх» до вершины: камера едет по колонне, а не сцены сменяют друг друга.
  // [ид сцены, первая фраза, последняя фраза]
  const SCENES = [['hook', 'hook', 'tease'], ['post', 'post', 'views'], ['musk', 'musk', 'musk'], ['climb', 'look', 'top'],
    ['fight', 'fight', 'fight'], ['siri', 'siri', 'siri'], ['q', 'q', 'q'], ['share', 'share', 'share'], ['cta', 'cta', 'link']];
  const ENTER = {
    post: [{ y: 110 }, 0.42, 'power3.out'], musk: [{ x: 110 }, 0.42, 'power4.out'], climb: [{ scale: 0.92 }, 0.42, 'power3.out'],
    fight: [{ scale: 1.14 }, 0.42, 'expo.out'], siri: [{ y: 90 }, 0.42, 'power3.out'], q: [{ y: 100 }, 0.42, 'power3.out'],
    share: [{ x: -110 }, 0.42, 'power4.out'], cta: [{ y: 100 }, 0.42, 'power3.out'],
  };
  const SC = {};
  SCENES.forEach(([id, a, b], n) => {
    const el = $('#sc-' + id);
    SC[id] = el;
    const end = id === 'cta' ? L : e(b);
    const [from, dur, ease] = ENTER[id] || [{ scale: 0.955 }, 0.42, 'power3.out'];
    const to = { opacity: 1, filter: 'blur(0px)', duration: dur, ease };
    Object.keys(from).forEach((k) => { to[k] = k === 'scale' ? 1 : 0; });
    if (id === 'post') {
      // тир-лист появляется сразу, без затухания: тёмные буквы рангов в полупрозрачном кадре
      // проверка контраста считает браком. Вход идёт сдвигом и размытием, крючок уходит поверх.
      tl.set(el, { opacity: 1 }, s(a));
      const { opacity, filter, ...move } = to;
      tl.fromTo(el, from, move, s(a));
    // Смена внахлёст: новая сцена начинает проявляться за 0,12 с до смены, старая гаснет поверх неё —
    // между сценами нет мутного полупустого кадра.
    } else if (n > 0) tl.fromTo(el, { opacity: 0, filter: 'blur(12px)', ...from }, to, s(a) - 0.12);
    if (id !== 'cta') tl.to(el, { opacity: 0, scale: 1.1, filter: 'blur(14px)', duration: 0.22, ease: 'power2.in' }, end - (id === 'hook' ? 0.3 : 0.06));
  });

  // Свет: синий — новость и низ рейтинга, янтарный — Grok, фиолетовый — S, SS, SSS, светлый — Siri,
  // лайм бренда — финал. В подъёме свет меняется по высоте, как этажи.
  const bgL = $('.bg-light'), vig = $('.vignette');
  const gLime = $('.glow-lime'), gBlue = $('.glow-blue'), gMint = $('.glow-mint'), gWarm = $('.glow-warm');
  const gNews = $('.glow-news'), gAmber = $('.glow-amber'), gViolet = $('.glow-violet');
  const swap = (off, on, at) => { tl.to(off, { opacity: 0, duration: 0.3 }, at - 0.1); tl.to(on, { opacity: 1, duration: 0.55 }, at); };
  const toLight = (at) => { tl.to(bgL, { opacity: 1, duration: 0.4, ease: 'power2.out' }, at - 0.1); tl.to(vig, { opacity: 0, duration: 0.3 }, at - 0.1); };
  const toDark = (at) => { tl.to(bgL, { opacity: 0, duration: 0.4, ease: 'power2.out' }, at - 0.1); tl.to(vig, { opacity: 1, duration: 0.5 }, at); };
  swap(gNews, gBlue, s('google'));
  swap(gBlue, gAmber, s('grok'));
  swap(gAmber, gViolet, s('s'));
  tl.to(gWarm, { opacity: 1, duration: 0.6 }, s('top'));
  tl.to(gWarm, { opacity: 0, duration: 0.4 }, e('fight') - 0.1);
  toLight(s('siri')); swap(gViolet, gMint, s('siri'));
  toDark(s('q')); swap(gMint, gLime, s('q'));
  // фон с буквами рангов — на Grok, как у автора
  const ghost = $('.ghostbg');
  tl.fromTo(ghost, { opacity: 0, x: 0 }, { opacity: 1, duration: 0.5 }, s('grok'));
  tl.to(ghost, { x: -160, duration: e('grok') - s('grok'), ease: 'none' }, s('grok'));
  tl.to(ghost, { opacity: 0, duration: 0.3 }, e('grok') - 0.2);
  // луч сверху: SS и SSS стоят под светом
  const spot = $('.spot');
  tl.fromTo(spot, { opacity: 0 }, { opacity: 1, duration: 0.6 }, s('ss'));
  tl.to(spot, { opacity: 0, duration: 0.3 }, e('top') - 0.2);
  // пятна дышат: медленно, в пределах пяти процентов
  $$('.glow i').forEach((el, i) => tl.fromTo(el, { scale: 0.96 }, { scale: 1.05, duration: 3.2 + i * 0.5, ease: 'sine.inOut', yoyo: true, repeat: Math.max(0, Math.floor(L / (3.2 + i * 0.5)) - 1) }, 0));

  // 1. Крючок: заголовок читается с нулевого кадра. На слове «Grok» телефон уходит,
  // встаёт сравнение: SSS у Claude и Grok тремя рангами ниже.
  {
    const sc = SC.hook, go = w('hook', 5) - 0.15;
    tl.fromTo($('.hk', sc), { scale: 1.04 }, { scale: 1, duration: 0.6, ease: 'expo.out' }, 0);
    // телефон стоит в наклоне и выпрямляется, камера наезжает; строка Маска загорается на «признал»
    tl.fromTo($('.ph', sc), { y: 40, rotationY: -24, rotationX: 8, transformPerspective: 1400 }, { y: 0, rotationY: 0, rotationX: 0, duration: 1.1, ease: 'power3.out' }, 0);
    // наезд, как у автора: с целого поста на строку «Accurate (for now)» настоящего снимка из X
    tl.set($('.ph .phone', sc), { transformOrigin: '50% 0%' }, 0);
    tl.fromTo($('.ph .phone', sc), { scale: 1, x: 0, y: 0 }, { scale: 1.8, x: -102, y: -28, duration: 0.6, ease: 'power2.inOut' }, 0.35);   // пост целиком по ширине кадра
    tl.fromTo($('.said', sc), { backgroundColor: 'rgba(199,226,75,0)', boxShadow: '0 0 0 0px rgba(199,226,75,0)' }, { backgroundColor: 'rgba(199,226,75,0.2)', boxShadow: '0 0 0 3px rgba(199,226,75,1)', duration: 0.25, ease: 'power2.out' }, w('hook', 3) - 0.05);
    $$('.floats .flt', sc).forEach((b, i) => tl.fromTo(b, { y: 0 }, { y: -40 - i * 8, duration: go, ease: 'none' }, 0));
    tl.to($('.hk', sc), { opacity: 0, y: -30, filter: 'blur(12px)', duration: 0.3, ease: 'power2.in' }, go - 0.1);
    $$('.hk2 span', sc).forEach((el, k) => word(el, w('hook', [5, 6, 7, 8, 9][k])));
    // телефон гаснет целиком до того, как встаёт сравнение: два движения разом (наезд и уход) ломали кадр
    tl.to($('.ph', sc), { opacity: 0, filter: 'blur(14px)', duration: 0.3, ease: 'power2.in' }, go - 0.32);
    tl.set($('.vs', sc), { opacity: 1 }, go);
    inn($('.vs1', sc), go + 0.15, { y: -80, scale: 0.9 }, 0.55);
    inn($('.vs2', sc), go + 0.3, { y: 90 }, 0.6);
    pop($('.down', sc), w('hook', 6));
    $$('.vs2 .m-grok46, .vs2 .m-grok47', sc).forEach((el) => hi(el, w('hook', 7)));
    dim($$('.vs2 .mt', sc).filter((m) => !m.classList.contains('m-grok46') && !m.classList.contains('m-grok47')), w('hook', 7), 0.35);
    hi($('.vs1 .mt', sc), w('hook', 9));

    // Петля (четвёртая версия): «первое место вовсе не у ChatGPT». Ряд Grok уходит, закрытая вершина
    // выходит в центр, снизу подъезжает ChatGPT и зачёркивается. Кто первый — узнаем на вершине подъёма.
    const tz = s('tease');
    tl.to([$('.hk2', sc), $('.vs2', sc), $('.down', sc)], { opacity: 0, y: 30, filter: 'blur(10px)', duration: 0.3, ease: 'power2.in' }, tz - 0.15);
    tl.set($('.vs1', sc), { transformOrigin: '50% 50%' }, 0);
    tl.to($('.vs1', sc), { scale: 2.1, y: 50, duration: 0.6, ease: 'power3.inOut' }, tz - 0.05);
    inn($('.gptx', sc), w('tease', 7) - 0.15, { y: 90, scale: 0.85 }, 0.45, 'back.out(1.3)');
    draw($('.gptx .x1', sc), w('tease', 8) + 0.1, 0.18, 'power2.out');
    draw($('.gptx .x2', sc), w('tease', 8) + 0.25, 0.18, 'power2.out');
    tl.to($('.gptx .mt', sc), { opacity: 0.45, duration: 0.3 }, w('tease', 8) + 0.3);
  }

  // 2. Тир-лист появляется в рамке планшета.
  {
    const sc = SC.post, t = s('post');
    tl.set($('.tab', sc), { opacity: 1 }, t);
    tl.fromTo($('.tab', sc), { y: 120, scale: 0.9 }, { y: 0, scale: 1, duration: 0.7, ease: 'power3.out' }, t + 0.05);
    tl.fromTo($('.tab', sc), { rotation: -2 }, { rotation: 0, duration: e('post') - t, ease: 'none' }, t);
    tl.to($('.tab', sc), { scale: 1.05, duration: e('post') - t - 0.6, ease: 'none' }, t + 0.6);   // пост не стоит мёртвым кадром
    // на «семи миллионах» камера наезжает на настоящую строку «7,2 млн Просмотры» под постом и
    // обводит её: подлинность видна в самом снимке, а строка поднимается выше полосы подписи площадки
    tl.set($('.tab', sc), { transformOrigin: '50% 0%' }, 0);
    tl.to($('.tab', sc), { scale: 1.6, y: -780, duration: 0.7, ease: 'power2.inOut' }, s('views') - 0.05);   // пост целиком по ширине, строка просмотров на ~900
    // верх рейтинга уходит под заголовок — затемняем его, чтобы строки не наползали на картинку
    tl.to($('.vfade', sc), { opacity: 1, duration: 0.5, ease: 'power2.out' }, s('views') + 0.1);
  }

  // 3. Семь и два миллиона: число досчитывает, шарики насыпаются горкой.
  {
    const sc = SC.post, t = s('views');
    tl.fromTo($('.vring', sc), { opacity: 0, scale: 1.3 }, { opacity: 1, scale: 1, duration: 0.3, ease: 'back.out(1.6)' }, w('views', 1));
  }

  // 4. Ответ Маска: «Accurate», потом плашка «(for now)», ниже перевод и растущий график.
  {
    const sc = SC.musk, t = s('musk');
    inn($('.card', sc), t + 0.05, { y: 60, scale: 0.94 }, 0.6);
    word($('.acc span', sc), w('musk', 2));
    pop($('.acc .fn', sc), w('musk', 4) - 0.1);
    tl.fromTo($('.acc .fn', sc), { boxShadow: '0 0 0 0 rgba(199,226,75,0)' }, { boxShadow: '0 0 40px 6px rgba(199,226,75,.45)', duration: 0.4 }, w('musk', 4));
    inn($('.tr2', sc), w('musk', 3) - 0.05, { y: 30 }, 0.4);
  }

  // 5. Подъём по рейтингу: одна сцена с «идём снизу вверх» до вершины. Камера (обёртка .cam, точка
  // отсчёта в левом верхнем углу) на каждой фразе едет к своему рангу и стоит, пока фраза звучит;
  // на слове загорается обводка. Ранги вне кадра камеры гаснут. Места рядов берутся из вёрстки
  // (offsetTop/offsetLeft не зависят от преобразований), поэтому колонну можно править в разметке.
  {
    const sc = SC.climb, cam = $('.cam', sc), col = $('.colw', sc);
    const at = (el) => { let x = 0, y = 0; for (let n = el; n && n !== col; n = n.offsetParent) { x += n.offsetLeft; y += n.offsetTop; } return { x, y, w: el.offsetWidth, h: el.offsetHeight }; };
    const box = (els) => { const r = els.map(at); const x0 = Math.min(...r.map((b) => b.x)), y0 = Math.min(...r.map((b) => b.y));
      return { x0, y0, x1: Math.max(...r.map((b) => b.x + b.w)), y1: Math.max(...r.map((b) => b.y + b.h)) }; };
    const R = (n) => $('.tr.' + cls(n), sc);
    const rows = $$('.col > .tr', sc);
    // кадр камеры: середина ранга встаёт в точку (540, CY), масштаб — сколько влезает, но не больше cap.
    // CY = 930: при 860 нижний ряд (Google) оставлял под собой пустую половину кадра.
    const CY = 930;
    const shot = (b, cap, hMax = 760) => { const k = Math.min(cap, 980 / (b.x1 - b.x0), hMax / (b.y1 - b.y0));
      return { scale: k, x: 540 - k * (b.x0 + b.x1) / 2, y: CY - k * (b.y0 + b.y1) / 2 }; };
    const go = (b, cap, t, d = 0.7) => tl.to(cam, { ...shot(b, cap), duration: d, ease: 'power3.inOut' }, t);
    const focus = (on, t) => rows.forEach((r) => tl.to(r, { opacity: on.includes(r) ? 1 : 0.22, duration: 0.45, ease: 'power2.out' }, t));
    const lead = 0.12;   // камера трогается чуть раньше фразы: к первому ударному слову она уже на месте

    // обзор: вся колонна, вершина закрыта; камера медленно поднимается снизу вверх
    const all = box(rows);
    const o = shot(all, 1, 1020);   // обзор крупнее: колонна на всю высоту от заголовка до 1450
    tl.set(cam, { transformOrigin: '0 0', ...o }, 0);
    tl.fromTo(cam, { y: o.y + 60 }, { y: o.y - 30, duration: e('look') - s('look') + 0.1, ease: 'sine.inOut' }, s('look') - 0.12);
    hi($('.t-sss .mys', sc), w('look', 2) - 0.05);

    // Google: камера ныряет на дно
    const gRow = R('Google');
    go(box([$('.lb', gRow), $('.fslot', gRow)]), 1.6, s('google') - lead, 0.8);
    focus([gRow], s('google') - lead);
    lo($('.t-sss .mys', sc), s('google'));
    tl.to($('.lb', gRow), { scale: 1.12, duration: 0.25, ease: 'power2.out', yoyo: true, repeat: 1 }, w('google', 9) - 0.05);
    tl.fromTo($('.lb', gRow), { boxShadow: '0 0 0 0 rgba(142,201,242,0)' }, { boxShadow: '0 0 40px 8px rgba(142,201,242,.7)', duration: 0.35 }, w('google', 9) - 0.05);
    // все Gemini — обводки по очереди; пустое место F проявляется и зачёркивается
    const gems = $$('.mt', gRow);
    gems.forEach((m, k) => hi(m, w('gem', 2) - 0.1 + k * 0.1));
    tl.fromTo($('.fslot', gRow), { opacity: 0, scale: 0.7 }, { opacity: 1, scale: 1, duration: 0.35, ease: 'back.out(1.4)' }, w('gem', 6) - 0.1);
    draw($('.fstrike', gRow), w('gem', 7), 0.25, 'power2.out');

    // Grok: камера отъезжает на A–C, Grok загорается трижды, линия ведёт от C до A
    const abc = [R('A'), R('B'), R('C')];
    go(box(abc), 1.1, s('grok') - lead, 0.8);
    focus(abc, s('grok') - lead);
    gems.forEach((m) => lo(m, s('grok')));
    const g45 = $('.t-c .m-grok45', sc), g46 = $('.t-a .m-grok46', sc), g47 = $('.t-a .m-grok47', sc);
    dim($$('.mt', R('A')).concat($$('.mt', R('B')), $$('.mt', R('C'))).filter((m) => ![g45, g46, g47].includes(m)), w('grok', 0), 0.3);
    [g45, g46, g47].forEach((m) => hi(m, w('grok', 0) - 0.05));
    const c = (m) => { const b = at($('.ic', m)); return [b.x + b.w / 2, b.y + b.h / 2]; };
    const [p0, p1, p2] = [c(g45), c(g47), c(g46)];
    const path = $('.gpath', sc);
    path.setAttribute('d', `M${p0[0]} ${p0[1]} C ${p0[0] + 120} ${p0[1] - 120}, ${p1[0] - 60} ${p1[1] + 140}, ${p1[0]} ${p1[1]} S ${p2[0] + 80} ${p2[1] + 60}, ${p2[0]} ${p2[1]}`);
    tl.set(path, { opacity: 1 }, 0);
    draw(path, w('grok', 5), Math.max(0.5, w('grok', 8) - w('grok', 5) + 0.15), 'power1.inOut');
    tl.to(path, { opacity: 0, duration: 0.25 }, e('grok') - 0.2);

    // S: камера наверх, лучи; Fable и GPT-6 Sol на своих словах
    const sRow = R('S');
    go(box([sRow.firstElementChild, ...$$('.mt', sRow)]), 2.15, s('s') - lead);
    focus([sRow], s('s') - lead);
    [g45, g46, g47].forEach((m) => lo(m, s('s')));
    tl.fromTo($('.rays', sc), { opacity: 0, rotation: -20, scale: 0.8 }, { opacity: 1, rotation: 0, scale: 1, duration: 0.8, ease: 'power3.out' }, s('s'));
    tl.to($('.rays', sc), { rotation: 30, duration: e('top') - s('s'), ease: 'none' }, s('s'));
    const [fb, sol] = $$('.mt', sRow);
    hi(fb, w('s', 4) - 0.05);
    hi(sol, w('s', 8) - 0.05);

    // SS: ещё выше, под лучом
    const ssRow = R('SS');
    go(box([ssRow.firstElementChild, $('.mt', ssRow)]), 2.35, s('ss') - lead);
    focus([ssRow], s('ss') - lead);
    [fb, sol].forEach((m) => lo(m, s('ss')));
    hi($('.mt', ssRow), w('ss', 2) - 0.05);

    // SSS: вершина. «?» переворачивается — Claude Opus 5.5, искры, подпись
    const top = R('SSS'), mys = $('.mys', top), opus = $('.opus', top);
    go(box([top.firstElementChild, $('.flip', top)]), 2.45, s('top') - lead);
    focus([top], s('top') - lead);
    lo($('.mt', ssRow), s('top'));
    hi(mys, w('top', 3) - 0.05);
    const flip = w('top', 6) - 0.12;
    tl.set([mys, opus], { transformPerspective: 900 }, 0);
    tl.set(opus, { opacity: 0 }, 0);
    tl.to(mys, { rotationY: 90, duration: 0.16, ease: 'power2.in' }, flip);
    tl.set(mys, { opacity: 0 }, flip + 0.16);
    tl.fromTo(opus, { opacity: 1, rotationY: -90 }, { rotationY: 0, duration: 0.24, ease: 'back.out(1.6)', immediateRender: false }, flip + 0.16);
    hi(opus, flip + 0.35);
    tl.to(rows.filter((r) => r !== top), { opacity: 0, duration: 0.3, ease: 'power2.out' }, flip);
    pop($('.cpill', sc), flip + 0.3);
    $$('.spk', sc).forEach((el, k) => {
      const a = flip + 0.2 + rnd(k + 3) * 1.1;
      tl.fromTo(el, { opacity: 0, scale: 0.2 }, { opacity: 1, scale: 1, duration: 0.25, ease: 'power2.out' }, a);
      tl.to(el, { opacity: 0, scale: 0.4, duration: 0.5, ease: 'power2.in' }, a + 0.3);
    });
    // пока звучит «Клод Опус пять и пять», камера медленно подаётся вперёд
    const k = shot(box([top.firstElementChild, $('.flip', top)]), 2.45);
    tl.to(cam, { scale: k.scale * 1.06, x: 540 - (540 - k.x) * 1.06, y: CY - (CY - k.y) * 1.06, duration: e('top') - flip - 0.2, ease: 'sine.out' }, flip + 0.2);
  }

  // 6. Бьются за SSS: четыре плитки сходятся к центру и отскакивают, между ними искры.
  {
    const sc = SC.fight, t = s('fight');
    const dir = [[1, 1], [-1, 1], [1, -1], [-1, -1]];
    $$('.fgt', sc).forEach((el, i) => {
      inn(el, t + 0.05 + i * 0.06, { x: -dir[i][0] * 120, y: -dir[i][1] * 80, scale: 0.8 }, 0.45);
      tl.to(el, { x: dir[i][0] * 18, y: dir[i][1] * 14, rotation: dir[i][0] * 5, duration: 0.22, ease: 'power2.in', yoyo: true, repeat: 3 }, Math.max(w('fight', 2) - 0.1, t + 0.75) + i * 0.03);
    });
    $$('.spark', sc).forEach((el, k) => {
      tl.fromTo(el, { opacity: 0, scaleX: 0.2 }, { opacity: 1, scaleX: 1, duration: 0.12 }, w('fight', 2) + 0.1 + (k % 3) * 0.44);
      tl.to(el, { opacity: 0, duration: 0.2 }, w('fight', 2) + 0.25 + (k % 3) * 0.44);
    });
  }

  // 7. Siri: карточка, вопрос про погоду, колесо и «ищу ответ в интернете», полоски поиска мерцают.
  {
    const sc = SC.siri, t = s('siri'), end = e('siri');
    inn($('.siri', sc), t + 0.05, { y: 60, scale: 0.94 }, 0.55);
    tl.fromTo($('.sorb', sc), { rotation: 0 }, { rotation: 360, duration: end - t, ease: 'none' }, t);
    tl.fromTo($('.spin', sc), { rotation: 0 }, { rotation: 720, duration: end - t, ease: 'none' }, t);
    $$('.dots i', sc).forEach((d, k) => tl.fromTo(d, { opacity: 0.2 }, { opacity: 1, duration: 0.3, yoyo: true, repeat: Math.max(1, Math.floor((end - t) / 0.6)), ease: 'sine.inOut' }, t + k * 0.2));
    $$('.skel i', sc).forEach((el, k) => tl.fromTo(el, { x: -300 }, { x: 700, duration: 1.1, ease: 'power1.inOut', repeat: Math.max(0, Math.floor((end - t) / 1.1) - 1) }, t + 0.3 + k * 0.15));
  }

  // 8. Вопрос и комментарий: ранги встают, на «свой ранг» курсор жмёт SSS, текст набирается, «Отправить».
  {
    const sc = SC.q, t = s('q'), end = e('q');
    inn($('.cbox', sc), t + 0.05, { y: 50, scale: 0.95 }, 0.5);
    $$('.rkc', sc).forEach((el, k) => pop(el, t + 0.3 + k * 0.04));
    inn($('.sendb', sc), t + 0.5, { y: 20 }, 0.35);
    const cur = $('.cur', sc), tap = w('q', 9) - 0.1;
    tl.fromTo(cur, { opacity: 0, x: 760, y: 1200 }, { opacity: 1, x: 296, y: 768, duration: tap - t - 0.2, ease: 'power2.inOut' }, t + 0.2);
    tl.to(cur, { scale: 0.75, duration: 0.1, yoyo: true, repeat: 1 }, tap);
    tl.to($('.rkc.on', sc), { backgroundColor: '#C7E24B', color: '#12130F', scale: 1.1, duration: 0.2 }, tap + 0.05);
    type($$('.ch', sc), tap + 0.15, w('q', 10) + 0.35);
    tl.to(cur, { x: 540, y: 976, duration: 0.35, ease: 'power2.inOut' }, end - 0.75);
    tl.to(cur, { scale: 0.75, duration: 0.1, yoyo: true, repeat: 1 }, end - 0.4);
    tl.to($('.sendb', sc), { scale: 0.94, duration: 0.1, yoyo: true, repeat: 1 }, end - 0.4);
  }

  // 9. Скинь другу: выбрать друга, набрать «Siri, какая погода?», отправить.
  {
    const sc = SC.share, t = s('share'), end = e('share');
    inn($('.sbox', sc), t + 0.05, { x: -60 }, 0.5);
    $$('.av2', sc).forEach((el, k) => pop(el, t + 0.2 + k * 0.08));
    inn($('.sendb', sc), t + 0.5, { y: 20 }, 0.35);
    const cur = $('.cur', sc), pick = w('share', 2);
    tl.fromTo(cur, { opacity: 0, x: 900, y: 1300 }, { opacity: 1, x: 759, y: 695, duration: pick - t - 0.1, ease: 'power2.inOut' }, t + 0.1);
    tl.to(cur, { scale: 0.75, duration: 0.1, yoyo: true, repeat: 1 }, pick);
    tl.to($('.av2 u', sc), { opacity: 1, duration: 0.2 }, pick + 0.05);
    tl.to($('.ph3', sc), { opacity: 0, duration: 0.1 }, w('share', 3) - 0.1);
    type($$('.ch', sc), w('share', 3), w('share', 10) + 0.2);
    tl.to(cur, { x: 540, y: 1006, duration: 0.4, ease: 'power2.inOut' }, end - 0.8);
    tl.to(cur, { scale: 0.75, duration: 0.1, yoyo: true, repeat: 1 }, end - 0.42);
    tl.to($('.sendb', sc), { scale: 0.94, duration: 0.1, yoyo: true, repeat: 1 }, end - 0.42);
  }

  // 10. Призыв: весь рейтинг одной картинкой, потом знак Telegram, кот показывает на него. В конце «сохрани».
  {
    const sc = SC.cta, tg = w('cta', 6) - 0.25;
    inn($('.mini2', sc), s('cta') + 0.1, { y: 60, scale: 0.9 }, 0.55);
    word($('.c1', sc), w('cta', 1));
    tl.to($('.first', sc), { opacity: 0, y: -70, filter: 'blur(14px)', duration: 0.3, ease: 'power2.in' }, tg - 0.2);
    tl.fromTo($('.tg', sc), { opacity: 0, x: -420, y: 260, rotation: -160, scale: 0.6 }, { opacity: 1, x: 0, y: 0, rotation: 0, scale: 1, duration: 0.8, ease: 'expo.out' }, tg);
    word($('.t1', sc), w('cta', 7));
    word($('.t2', sc), w('cta', 7) + 0.3);
    inn($('.point', sc), w('cta', 7), { x: 160 }, 0.5, 'power3.out');
    inn($('.go', sc), w('link', 0) - 0.1, { y: 40, scale: 0.9 }, 0.45, 'back.out(1.2)');
    tl.fromTo($('.go .shim', sc), { '--sp': '-25%' }, { '--sp': '125%', duration: 0.9, ease: 'power2.inOut' }, w('link', 0) + 0.3);
    inn($('.save', sc), w('link', 2) + 0.3, { y: 40, scale: 0.9 }, 0.45, 'back.out(1.2)');
    tl.to($('.save span', sc), { scale: 1.06, duration: 0.45, ease: 'sine.inOut', yoyo: true, repeat: 1 }, w('link', 2) + 0.9);
  }
  return tl;
};

/** Слой поверх сцен: знак канала, полоса ролика, заголовки. */
export const overlayMarkup = (A, T) => {
  return `<div class="logo"><img src="${A}/logo.png"></div>
<div class="prog">${'<i><b></b></i>'.repeat(9)}</div>
` + headlines(T).map((h) => `<div class="hl ${h.light ? 'light' : ''}">${[h.l1, h.l2].map((line, k) => line.length ? `<div class="${k ? 'l2' : 'l1'}">${
    line.map(([txt, , c]) => `<span class="${c || ''}">${txt}</span>`).join('')}</div>` : '').join('')}</div>`).join('');
};

export const buildOverlay = (gsap, tl, root, T) => {
  const s = (id) => T.scenes[id].s;
  const e = (id) => T.scenes[id].e;
  const w = (id, i) => T.w[id][i];
  headlines(T).forEach((h, n) => {
    const box = root.querySelectorAll('.hl')[n];
    const spans = [...box.querySelectorAll('span')];
    [...h.l1, ...h.l2].forEach(([, at], i) =>
      tl.fromTo(spans[i], { opacity: 0, y: 24, filter: 'blur(12px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: i === 0 ? 0.3 : 0.38, ease: i === 0 ? 'expo.out' : 'power3.out' },
        // в быстром темпе последнее слово звучит у самого конца сцены: встаёт не позже, чем за 0,6 с до ухода
        Math.max(h.from, Math.min(at - 0.06, h.to - 0.6))));
    tl.to(spans, { opacity: 0, filter: 'blur(12px)', duration: 0.24, ease: 'power2.in' }, h.to - 0.26);
  });

  // Нижних субтитров нет (вторая версия): заголовок сверху показывает фразу по словам, как у автора.

  // Полоса ролика: на заставке её нет, она прорисовывается на смене первого кадра и идёт до самого
  // конца девятью отрезками по абзацам (README, «Ролик с голосом»).
  const prog = root.querySelector('.prog');
  const старт = s('post');
  [...prog.querySelectorAll('i')].forEach((el, i) =>
    tl.fromTo(el, { opacity: 0, scaleX: 0 }, { opacity: 1, scaleX: 1, duration: 0.45, ease: 'expo.out' }, старт + 0.1 + i * 0.05));
  const части = [старт + 0.3, s('musk'), s('look'), s('grok'), s('s'), s('top'), s('fight'), s('q'), s('cta'), T.length - 0.4];
  [...prog.querySelectorAll('b')].forEach((b, i) =>
    tl.fromTo(b, { scaleX: 0 }, { scaleX: 1, duration: части[i + 1] - части[i], ease: 'none' }, части[i]));
  // Цвет полосы следует за светом сцены.
  [['post', 0], ['siri', 1], ['q', 0]].forEach(([id, light]) =>
    tl.set(prog, { '--pf': light ? '#56690C' : '#C7E24B', '--pt': light ? 'rgba(18,19,15,.16)' : 'rgba(241,242,234,.2)' }, s(id)));

  // Бегунка рангов внизу больше нет (04.10): он стоял неподвижной капсулой посреди кадра с 12-й секунды,
  // владелец принял его за сломанную полосу. Ход ролика показывает полоса наверху.
  return tl;
};

/** Картинка рейтинга для Telegram (ролик её обещает): весь тир-лист на всю ширину, заголовок, знак канала.
 *  Кадр 1080 в ширину, высота по содержимому; снимок с двойной плотностью (картинка.mjs).
 *  Было: тир-лист ужат до 0,6 в колонку 584 px — подписи по 9 px, с телефона не читались (владелец 04.10). */
export const pictureMarkup = (A) => `<div class="pic">
  <div class="logo" style="left:40px;top:44px"><img src="${A}/logo.png"></div>
  <div class="pt"><b>Рейтинг нейросетей</b><span>Маск ответил: «Accurate (for now)» — точно, пока что</span></div>
  <div class="ptab">${list(A, LADDER.slice().reverse())}</div>
  <div class="pfoot">Telegram @FourXtube</div>
</div>`;

/** Карточки рейтинга для альбома Telegram: 1080×1350, по 2–3 ранга крупно. Одна картинка со всеми 45
 *  моделями в ленте телефона читается подписями по 7 пунктов (владелец 04.10: «с телефона не читается»),
 *  поэтому общий вид идёт первой картинкой альбома, а следом ранги крупно. Grok Маска обведён. */
export const CARDS = [
  [['SSS', 'SS', 'S'], 'Вершина'], [['A', 'B'], 'Середина'], [['C', 'D'], 'Ниже среднего'], [['E', 'Google'], 'Самый низ'],
];
export const cardMarkup = (A, k) => {
  const [names, title] = CARDS[k];
  return `<div class="card4">
  <div class="logo"><img src="${A}/logo.png"></div>
  <div class="ch4"><b>Рейтинг нейросетей</b><span>${title} · ${k + 1} / ${CARDS.length}</span></div>
  <div class="cbody">${list(A, names).replace(/class="mt m-grok/g, 'class="mt grk m-grok')}</div>
  ${names.includes('Google') ? '<div class="cnote">Отдельный ранг так и назвали: <b>Google</b>. Даже букву F пожалели</div>' : ''}
  <div class="cfoot">Telegram @FourXtube</div>
</div>`;
};

