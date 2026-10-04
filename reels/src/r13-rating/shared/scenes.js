// Ролик «Маск согласился: Grok хуже» (r13). Рерайт рилса instagram.com/reel/DeBhoSnRegX, движок HyperFrames.
//
// Разбор референса и что заменено: ../РЕФЕРЕНС.md, текст по ролям: ../ОЗВУЧКА.md.
// Тезис: состояние — одна фраза голоса, движется то, о чём говорят. Рейтинг проходится снизу
// вверх, как у автора: отдельный ранг Google, E, размазанный Grok, A, S, SS и один SSS на вершине.
// Внизу кадра идёт бегунок рангов: зритель видит, сколько осталось до вершины, и досматривает.
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
const label = (n, extra = '', style = '') => `<div class="lbx ${extra}${n === 'Google' ? ' g' : ''}" style="background:${T_[n][1]};${style}">${n}</div>`;

const PLANE = '<svg viewBox="0 0 24 24"><path d="M21.900 3.300 2.700 10.700c-1.300.500-1.300 1.300-.200 1.600l4.900 1.500 1.900 5.800c.200.700.400.900.900.900.400 0 .600-.200.900-.500l2.300-2.300 4.900 3.600c.900.500 1.500.200 1.800-.800l3.200-15.200c.300-1.300-.500-1.900-1.400-2zM8.300 13.500l10-6.300c.500-.300.900-.100.500.200l-8.200 7.400-.300 3.400z"/></svg>';
const BADGE = '<svg class="vb" viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="#1D9BF0"/><path d="M7 12.300l3.200 3.200L17 8.700" fill="none" stroke="#fff" stroke-width="2.600" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const EYE = '<svg viewBox="0 0 24 24"><path d="M1.500 12S5.500 4.500 12 4.500 22.500 12 22.500 12 18.500 19.500 12 19.500 1.500 12 1.500 12z" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="3.400" fill="currentColor"/></svg>';
const SEND = '<svg viewBox="0 0 24 24"><path d="M3 11.500 20.500 3.500 13 21l-2.200-7.300z" fill="currentColor"/></svg>';
const SAVE = '<svg viewBox="0 0 24 24"><path d="M6 3h12v18l-6-4.500L6 21z"/></svg>';

// Псевдослучайное число по зерну: одно и то же в каждой вкладке рендера.
const rnd = (seed) => { const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
// Шарики в цветах бренда: у автора разноцветные, у нас лайм, крем, олива и терракота Claude.
const BALL = ['#C7E24B', '#F1F2EA', '#89A81C', '#D97757', '#56690C', '#E4ECB8'];
const ball = (i, x, y, r, extra = '', style = '') => `<i class="ball ${extra}" style="left:${x}px;top:${y}px;width:${r}px;height:${r}px;--c:${BALL[i % BALL.length]};${style}"></i>`;

// Пост Маска в телефоне. Фото не ставим: инициалы на круге.
const xpost = () => `<div class="xp">
  <div class="sbar"><b>15:09</b><span>●●● ▮</span></div>
  <div class="xh"><span>←</span><b>Пост</b><span>···</span></div>
  <div class="who"><i class="av">EM</i><div><b>Elon Musk ${BADGE}</b><small>@elonmusk</small></div><span class="xl">𝕏</span></div>
  <div class="said">Accurate (for now)</div>
  <div class="quote"><div class="qh"><i></i><b>AI tier list</b><small>· 7,2 млн просмотров</small></div>
    <div class="mini">${TIERS.map((t, k) => `<div><i style="background:${t[1]}"></i>${t[2].slice(0, 7).map(() => '<s></s>').join('')}</div>`).join('')}</div></div>
</div>`;

/** Разметка всех сцен. A — адрес папки с картинками. */
export const markup = (A) => `
<div class="bg bg-light"></div>
<div class="glow glow-lime" data-layout-ignore style="opacity:1"><i></i></div><div class="glow glow-blue" data-layout-ignore><i></i></div><div class="glow glow-mint" data-layout-ignore><i></i></div><div class="glow glow-warm" data-layout-ignore><i></i></div>
<div class="vignette" style="opacity:1"></div>
<div class="ghostbg" data-layout-ignore><div class="gl">ABCABCA</div><div class="gl" style="margin-left:-260px">CBACBAC</div><div class="gl">BCACEAB</div></div>
<div class="spot" data-layout-ignore></div>

<div class="sc" id="sc-hook" style="opacity:1">
  <div class="abs balls" data-layout-ignore style="inset:0">${[[60, 560, 70], [930, 640, 54], [120, 1180, 96], [860, 1090, 84], [300, 1320, 40], [760, 470, 34]].map(([x, y, r], i) => ball(i, x, y, r, 'soft')).join('')}</div>
  <div class="hk"><div class="k1">Илон Маск</div><div class="k2">согласился</div></div>
  <div class="hk hk2"><div class="k1"><span class="h">Grok</span> <span class="h">хуже,</span></div><div class="k3"><span class="h">чем</span> <span class="h">у</span> <span class="h">конкурентов</span></div></div>
  <div class="ph abs" style="left:330px;top:480px"><div class="phone">${xpost()}</div></div>
  <div class="vs abs h" style="left:0;top:560px;width:1080px">
    <div class="abs vs1" style="left:419px;top:0">${row(A, T_.SSS, 'solo')}</div>
    <div class="abs" style="left:0;top:250px;width:1080px;text-align:center"><span class="down pill h"><b>↓</b> на 3 ранга ниже</span></div>
    <div class="abs vs2" style="left:124px;top:380px;width:833px;height:286px"><div style="transform:scale(0.9);transform-origin:0 0;width:max-content">${list(A, ['A'], 'cut')}</div></div>
  </div>
</div>

<div class="sc" id="sc-post">
  <div class="tab abs h" style="left:316px;top:470px;width:449px;height:817px"><div style="transform:scale(0.46);transform-origin:0 0;width:max-content">${mini(list(A, LADDER.slice().reverse()))}</div></div>
</div>

<div class="sc" id="sc-views">
  <div class="big72" style="top:520px"><span class="c7">0</span><span class="dec h">,2</span></div>
  <div class="cap" style="top:830px;font-size:64px"><span class="h">млн</span> <span class="h">просмотров</span></div>
  <div class="src pill h" style="position:absolute;left:390px;top:950px">${EYE}пост в 𝕏</div>
  <div class="heap abs" data-layout-ignore style="left:300px;top:1060px;width:480px;height:200px">${Array.from({ length: 16 }, (_, i) => {
    const r = 56 + Math.round(rnd(i + 7) * 26); const x = Math.round(rnd(i + 2) * 400); const y = Math.round(90 - Math.sin((x / 400) * Math.PI) * 80 + rnd(i + 9) * 50);
    return ball(i, x, y, r, 'h');
  }).join('')}</div>
</div>

<div class="sc" id="sc-musk">
  <div class="card glass abs h" style="left:150px;top:520px;width:780px;height:300px">
    <div class="who" style="left:44px;top:40px"><i class="av">EM</i><div><b>Elon Musk ${BADGE}</b><small>@elonmusk</small></div></div>
    <div class="acc"><span class="h">Accurate</span> <span class="fn h">(for now)</span></div>
  </div>
  <div class="tr2 pill h" style="position:absolute;left:0;top:880px;width:1080px;background:none;border:none;justify-content:center"><span class="tp">Точно.</span><span class="tp2">Пока что</span></div>
  <div class="bars abs" data-layout-ignore style="left:190px;top:1020px;width:700px;height:200px">${Array.from({ length: 26 }, (_, i) =>
    `<i style="left:${i * 27}px;height:${Math.round(18 + Math.pow(i / 25, 1.6) * 170)}px;opacity:${(0.25 + 0.75 * i / 25).toFixed(2)}"></i>`).join('')}</div>
</div>

<div class="sc" id="sc-look">
  <div class="clipw abs h" style="left:205px;top:470px;width:670px;height:770px">
    <div class="tab abs pan" style="left:0;top:0;width:670px;height:1222px"><div style="transform:scale(0.69);transform-origin:0 0;width:max-content">${mini(list(A, LADDER.slice().reverse()))}</div></div>
  </div>
</div>

<div class="sc light" id="sc-bottom">
  <div class="ladder abs" style="left:430px;top:500px;width:220px">${LADDER.slice(1).reverse().map((n, k) => label(n, 'h rung', `top:${k * 66}px`)).join('')}</div>
  <div class="dash abs h" data-layout-ignore style="left:380px;top:1046px;width:320px"></div>
  ${label('Google', 'h gb', 'left:430px;top:1086px;width:220px;height:110px;font-size:40px')}
</div>

<div class="sc light" id="sc-google">
  <div class="gtile abs h" style="left:400px;top:560px">${label('Google', 'big', '')}</div>
  <div class="ring2 abs h" data-layout-ignore style="left:340px;top:500px;width:400px;height:400px"></div>
</div>

<div class="sc light" id="sc-gem">
  ${label('Google', 'h glb', 'left:150px;top:560px;width:250px;height:250px;font-size:56px;border-radius:44px')}
  <div class="abs" style="left:440px;top:500px"><div class="grid4">${T_.Google[2].map((m) => tile(A, m, 'h')).join('')}</div></div>
</div>

<div class="sc light" id="sc-f">
  <div class="abs h grow" style="left:248px;top:500px">${list(A, ['Google'], 'sm')}</div>
  <div class="fcard abs h" style="left:290px;top:720px;width:500px;height:430px"><span class="fl">F</span>
    <svg viewBox="0 0 500 430" style="position:absolute;inset:0;width:100%;height:100%"><path class="strike" d="M40 330 L460 110" fill="none" stroke="#2F7FD8" stroke-width="16" stroke-linecap="round"/></svg></div>
</div>

<div class="sc light" id="sc-e">
  <div class="abs h ed" style="left:305px;top:520px">${list(A, ['D'], 'dim')}</div>
  <div class="abs h ee" style="left:230px;top:716px;width:620px;height:222px"><div style="transform:scale(1.32);transform-origin:0 0;width:max-content">${list(A, ['E'])}</div></div>
  <div class="abs h eg" style="left:248px;top:972px">${list(A, ['Google'], 'dim')}</div>
</div>

<div class="sc" id="sc-grok">
  <div class="tilt abs" style="left:124px;top:500px;width:833px;height:603px"><div style="position:relative;width:926px;height:670px;transform:scale(0.9);transform-origin:0 0;width:max-content">
    <div class="abc abs h" style="left:0;top:0;width:926px;height:670px">${list(A, ['A', 'B', 'C'])}
      <svg class="gp" viewBox="0 0 922 660" style="position:absolute;left:0;top:0;width:922px;height:660px;overflow:visible"><path class="gpath" d="M290 554 C 380 470, 560 330, 632 210 S 642 92, 632 60" fill="none" stroke="#C7E24B" stroke-width="5" stroke-linecap="round"/></svg>
    </div>
  </div></div>
</div>

<div class="sc" id="sc-a">
  <div class="abs h arow" style="left:68px;top:560px;width:945px;height:324px"><div style="transform:scale(1.02);transform-origin:0 0;width:max-content">${list(A, ['A'])}</div></div>
</div>

<div class="sc" id="sc-s">
  <div class="rays abs" data-layout-ignore style="left:140px;top:420px;width:800px;height:800px"></div>
  ${label('S', 'h sl', 'left:465px;top:470px;width:150px;height:100px;font-size:56px')}
  <div class="abs h fb" style="left:405px;top:640px;width:270px;height:364px"><div style="transform:scale(2.6);transform-origin:0 0;width:max-content">${tile(A, T_.S[2][0])}</div></div>
  <div class="abs h sol" style="left:405px;top:640px;width:270px;height:364px"><div style="transform:scale(2.6);transform-origin:0 0;width:max-content">${tile(A, T_.S[2][1])}</div></div>
</div>

<div class="sc" id="sc-ss">
  <div class="abs h ssr" style="left:298px;top:560px;width:484px;height:336px"><div style="transform:scale(2);transform-origin:0 0;width:max-content">${row(A, T_.SS, 'solo')}</div></div>
  <div class="abs h sbelow" style="left:380px;top:944px;width:320px;height:151px"><div style="transform:scale(0.9);transform-origin:0 0;width:max-content">${row(A, T_.S, 'solo dim')}</div></div>
  <div class="pod abs h" data-layout-ignore style="left:250px;top:1106px;width:580px;height:46px"></div>
  <div class="pod abs h" data-layout-ignore style="left:190px;top:1166px;width:700px;height:50px"></div>
</div>

<div class="sc" id="sc-top">
  ${Array.from({ length: 14 }, (_, i) => `<i class="spk h" data-layout-ignore style="left:${Math.round(160 + rnd(i + 51) * 760)}px;top:${Math.round(470 + rnd(i + 77) * 640)}px"></i>`).join('')}
  <div class="abs h sssr" style="left:262px;top:540px;width:557px;height:386px"><div style="transform:scale(2.3);transform-origin:0 0;width:max-content">${row(A, T_.SSS, 'solo')}</div></div>
  <div class="ell abs h" data-layout-ignore style="left:200px;top:1060px;width:680px;height:120px"></div>
  <div class="cpill pill h" style="position:absolute;left:0;top:930px;width:1080px;background:none;border:none;justify-content:center"><span class="cl">Claude Opus 5.5</span></div>
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

<div class="sc" id="sc-race">
  <div class="fnp pill h" style="position:absolute;left:330px;top:470px"><b>Accurate</b><span>(for now)</span></div>
  <div class="finish abs" data-layout-ignore style="left:868px;top:590px;height:520px"></div>
  ${[['claude', 0.93], ['openai', 0.85], ['grok', 0.58], ['gemini', 0.42]].map(([l, p], i) => `<div class="lane2 abs h ln${i}" style="left:150px;top:${600 + i * 128}px;width:740px"><b class="fill2" style="--p:${p}"></b><i class="knob2 ${l === 'claude' ? 'cl' : ''}"><img src="${A}/m/${FILE[l]}"></i></div>`).join('')}
</div>

<div class="sc" id="sc-q">
  <div class="abs" style="left:174px;top:520px"><div class="qgrid">${[['Opus 5.5', 'claude'], ['GPT-6<br>Astra', 'openai'], ['Grok 4.7', 'grok'], ['Gemini 3.8<br>Flash', 'gemini'], ['DeepSeek<br>V4.1 Flash', 'deepseek'], ['Kimi K3', 'kimi'], ['Qwen3.8<br>Max', 'qwen'], ['Mistral<br>Medium 3.5', 'mistral']].map((m) => tile(A, m, 'h qt')).join('')}</div></div>
  <div class="qmark abs h" style="left:0;top:1000px;width:1080px">?</div>
</div>

<div class="sc" id="sc-com">
  <div class="cbox glass abs h" style="left:150px;top:520px;width:780px;height:560px">
    <div class="inp"><i class="ball" style="position:relative;left:0;top:0;width:66px;height:66px;--c:#C7E24B"></i><div class="field"><span class="ph2">Мой ранг:</span> ${[...'SSS — Claude'].map((c) => `<span class="ch h">${c === ' ' ? '&nbsp;' : c}</span>`).join('')}</div></div>
    <div class="rk">${LADDER.slice().reverse().map((n) => `<span class="rkc h${n === 'SSS' ? ' on' : ''}${n === 'Google' ? ' g' : ''}">${n}</span>`).join('')}</div>
    <div class="sendb h">${SEND}Отправить</div>
  </div>
  <i class="cur h" data-layout-ignore></i>
</div>

<div class="sc" id="sc-share">
  <div class="sbox glass abs h" style="left:150px;top:520px;width:780px;height:560px">
    <div class="st">Поделиться</div>
    <div class="avs">${[0, 1, 2, 3].map((i) => `<i class="ball av2 h" style="position:relative;left:0;top:0;width:110px;height:110px;--c:${['#F1F2EA', '#89A81C', '#D97757', '#C7E24B'][i]}">${i === 3 ? '<u></u>' : ''}</i>`).join('')}</div>
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

// Какие сцены светлые: группа рангов внизу и Siri. Остальное тёмное, как у автора.
const LIGHT = ['bottom', 'google', 'gem', 'f', 'e', 'siri'];

/** Заголовок сверху: слово встаёт, когда звучит. Номера слов — по тексту голоса (voice/r13.json). */
export const headlines = (T) => {
  const w = (id, i) => T.w[id][i];
  const s = (id) => T.scenes[id].s;
  const e = (id) => T.scenes[id].e;
  const H = (id, l1, l2 = []) => ({ id, light: LIGHT.includes(id), from: s(id), to: e(id), l1, l2 });
  return [
    { ...H('post', [['Разработчик', w('post', 0)]], [['выложил', w('post', 1)], ['рейтинг', w('post', 2)]]), to: e('views') },
    H('musk', [['Маск', w('musk', 1)], ['ответил', w('musk', 2)]]),
    H('look', [['Смотри,', w('look', 0)]], [['кто', w('look', 1)], ['где', w('look', 2)]]),
    H('bottom', [['В', w('bottom', 0)], ['самом', w('bottom', 1)], ['низу', w('bottom', 2)]], [['отдельный', w('bottom', 3)], ['ранг', w('bottom', 4)]]),
    H('google', [['Ранг', s('google') + 0.12]], [['Google', w('google', 3), 'gg']]),
    H('gem', [['Там', w('gem', 0)], ['все', w('gem', 1)]], [['Gemini', w('gem', 2)]]),
    H('f', [['Им', w('f', 0)], ['даже', w('f', 1)]], [['букву', w('f', 2)], ['F', w('f', 3), 'gg'], ['пожалели', w('f', 4)]]),
    H('e', [['Чуть', w('e', 0)], ['выше', w('e', 1)]], [['Haiku,', w('e', 2)], ['Mistral,', w('e', 3)], ['Nemotron', w('e', 5)]]),
    H('grok', [['Grok', w('grok', 0)], ['Маска', w('grok', 2)]], [['от', w('grok', 5)], ['C', w('grok', 6), 'lm'], ['до', w('grok', 7)], ['A', w('grok', 8), 'lm']]),
    H('a', [['В', w('a', 0)], ['A', w('a', 1)], ['ещё', w('a', 2)]], [['DeepSeek,', w('a', 3)], ['Kimi', w('a', 4)]]),
    H('s', [['В', w('s', 0)], ['S', w('s', 1)]], [['новый', w('s', 2)], ['Fable', w('s', 3)]]),
    H('ss', [['Ещё', w('ss', 0)], ['выше', w('ss', 1)]], [['GPT-6', w('ss', 2)], ['Astra', w('ss', 4)]]),
    H('top', [['На', w('top', 1)], ['вершине', w('top', 3)]], [['только', w('top', 4)], ['один', w('top', 5), 'lm']]),
    H('fight', [['Бьются', w('fight', 1)]], [['за', w('fight', 2)], ['SSS', w('fight', 3), 'lm']]),
    H('siri', [['А', w('siri', 0)], ['Siri', w('siri', 1)]], [['ищет', w('siri', 4)], ['в', w('siri', 6)], ['интернете', w('siri', 7)]]),
    H('race', [['«Пока', w('race', 2)], ['что»', w('race', 3)]], [['гонка', w('race', 5)], ['не', w('race', 6)], ['закончена', w('race', 7)]]),
    H('q', [['А', w('q', 0)], ['ты', w('q', 1)]], [['на', w('q', 2)], ['какой?', w('q', 3)]]),
    H('com', [['Пиши', w('com', 0)], ['в', w('com', 1)], ['комменты', w('com', 2)]], [['свой', w('com', 3)], ['ранг', w('com', 4)]]),
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
  const hi = (el, t, scale = 1.12) => {
    tl.to($('u', el), { opacity: 1, duration: 0.18, ease: 'power2.out' }, t);
    tl.fromTo(el, { scale: 1 }, { scale, duration: 0.35, ease: 'back.out(1.6)' }, t);
  };
  const lo = (el, t) => {
    tl.to($('u', el), { opacity: 0, duration: 0.2 }, t);
    tl.to(el, { scale: 1, duration: 0.3, ease: 'power2.out' }, t);
  };
  const dim = (els, t, to = 0.3) => tl.to(els, { opacity: to, duration: 0.35, ease: 'power2.out' }, t);
  const type = (chars, a, b) => chars.forEach((c, i) => tl.set(c, { opacity: 1 }, a + (i * (b - a)) / Math.max(1, chars.length)));

  // Сцены перетекают из размытия, но приходят с разных сторон и с разной скоростью.
  const ENTER = {
    post: [{ y: 110 }, 0.6, 'power3.out'], views: [{ scale: 1.16 }, 0.6, 'expo.out'], musk: [{ x: 110 }, 0.55, 'power4.out'],
    look: [{ scale: 0.92 }, 0.6, 'power3.out'], bottom: [{ y: -90 }, 0.55, 'power3.out'], google: [{ scale: 1.14 }, 0.5, 'expo.out'],
    gem: [{ x: 110 }, 0.5, 'power4.out'], f: [{ y: 90 }, 0.5, 'power3.out'], e: [{ y: 110 }, 0.55, 'power4.out'],
    grok: [{ scale: 1.12 }, 0.6, 'expo.out'], a: [{ x: -110 }, 0.5, 'power4.out'], s: [{ scale: 0.9 }, 0.6, 'expo.out'],
    ss: [{ y: 110 }, 0.6, 'power3.out'], top: [{ y: 110 }, 0.6, 'power3.out'], fight: [{ scale: 1.14 }, 0.45, 'expo.out'],
    siri: [{ y: 90 }, 0.55, 'power3.out'], race: [{ x: 110 }, 0.5, 'power4.out'], q: [{ scale: 0.92 }, 0.55, 'power3.out'],
    com: [{ y: 100 }, 0.55, 'power3.out'], share: [{ x: -110 }, 0.5, 'power4.out'], cta: [{ y: 100 }, 0.6, 'power3.out'],
  };
  const order = ['hook', 'post', 'views', 'musk', 'look', 'bottom', 'google', 'gem', 'f', 'e', 'grok', 'a', 's', 'ss', 'top', 'fight', 'siri', 'race', 'q', 'com', 'share', 'cta'];
  const SC = {};
  order.forEach((id, n) => {
    const el = $('#sc-' + id);
    SC[id] = el;
    // у призыва две фразы (cta и link): сцена держится до конца ролика
    const end = id === 'cta' ? L : e(id);
    const [from, dur, ease] = ENTER[id] || [{ scale: 0.955 }, 0.5, 'power3.out'];
    const to = { opacity: 1, filter: 'blur(0px)', duration: dur, ease };
    Object.keys(from).forEach((k) => { to[k] = k === 'scale' ? 1 : 0; });
    if (n > 0 && id === 'post') {
      // тир-лист появляется сразу, без затухания: тёмные буквы рангов в полупрозрачном кадре
      // проверка контраста считает браком. Вход идёт сдвигом и размытием, крючок уходит поверх.
      tl.set(el, { opacity: 1 }, s(id));
      const { opacity, filter, ...move } = to;
      tl.fromTo(el, from, move, s(id));
    } else if (n > 0) tl.fromTo(el, { opacity: 0, filter: 'blur(16px)', ...from }, to, s(id));
    if (id !== 'cta') tl.to(el, { opacity: 0, scale: 1.05, filter: 'blur(16px)', duration: 0.34, ease: 'power2.in' }, end - 0.24);
  });

  // Фон: светлая группа рангов внизу и светлая сцена Siri. Пятна света: лайм на тёмном,
  // голубое на ранге Google (цвет ранга с тир-листа), мятное на светлых.
  const bgL = $('.bg-light'), vig = $('.vignette');
  const gLime = $('.glow-lime'), gBlue = $('.glow-blue'), gMint = $('.glow-mint'), gWarm = $('.glow-warm');
  [['bottom', 'grok', gBlue], ['siri', 'race', gMint]].forEach(([a, b, g]) => {
    tl.to(bgL, { opacity: 1, duration: 0.45, ease: 'power2.out' }, s(a) - 0.1);
    tl.to([gLime, vig], { opacity: 0, duration: 0.3 }, s(a) - 0.1);
    tl.to(g, { opacity: 1, duration: 0.6 }, s(a));
    tl.to(bgL, { opacity: 0, duration: 0.45, ease: 'power2.out' }, s(b) - 0.1);
    tl.to(g, { opacity: 0, duration: 0.3 }, s(b) - 0.1);
    tl.to([gLime, vig], { opacity: 1, duration: 0.5 }, s(b));
  });
  // на ранге E голубое пятно сменяется мятным
  tl.to(gBlue, { opacity: 0, duration: 0.4 }, s('e') - 0.1);
  tl.to(gMint, { opacity: 1, duration: 0.5 }, s('e'));
  tl.to(gMint, { opacity: 0, duration: 0.3 }, s('grok') - 0.1);
  // вершина: тёплое пятно Claude под SSS
  tl.to(gWarm, { opacity: 1, duration: 0.6 }, s('top'));
  tl.to(gWarm, { opacity: 0, duration: 0.4 }, e('fight') - 0.1);
  // фон с буквами рангов — на Grok и ранге A, как у автора
  const ghost = $('.ghostbg');
  tl.fromTo(ghost, { opacity: 0, x: 0 }, { opacity: 1, duration: 0.5 }, s('grok'));
  tl.to(ghost, { x: -160, duration: e('a') - s('grok'), ease: 'none' }, s('grok'));
  tl.to(ghost, { opacity: 0, duration: 0.3 }, e('a') - 0.2);
  // луч сверху: SS и SSS стоят под светом
  const spot = $('.spot');
  tl.fromTo(spot, { opacity: 0 }, { opacity: 1, duration: 0.6 }, s('ss'));
  tl.to(spot, { opacity: 0, duration: 0.3 }, e('top') - 0.2);
  // пятна дышат: медленно, в пределах пяти процентов
  $$('.glow i').forEach((el, i) => tl.fromTo(el, { scale: 0.96 }, { scale: 1.05, duration: 3.2 + i * 0.5, ease: 'sine.inOut', yoyo: true, repeat: Math.max(0, Math.floor(L / (3.2 + i * 0.5)) - 1) }, 0));

  // 1. Крючок: заголовок читается с нулевого кадра. На слове «Grok» телефон уходит,
  // встаёт сравнение: SSS у Claude и Grok тремя рангами ниже.
  {
    const sc = SC.hook, go = w('hook', 4) - 0.15;
    tl.fromTo($('.hk', sc), { scale: 1.04 }, { scale: 1, duration: 0.6, ease: 'expo.out' }, 0);
    tl.fromTo($('.ph', sc), { y: 40 }, { y: 0, duration: 0.8, ease: 'power3.out' }, 0);
    $$('.balls .ball', sc).forEach((b, i) => tl.fromTo(b, { y: 0 }, { y: -40 - i * 8, duration: go, ease: 'none' }, 0));
    tl.to($('.hk', sc), { opacity: 0, y: -30, filter: 'blur(12px)', duration: 0.3, ease: 'power2.in' }, go - 0.1);
    $$('.hk2 span', sc).forEach((el, k) => word(el, w('hook', [4, 5, 6, 7, 8][k])));
    tl.to($('.ph', sc), { x: -420, scale: 0.7, opacity: 0, filter: 'blur(14px)', duration: 0.55, ease: 'power3.in' }, go);
    tl.set($('.vs', sc), { opacity: 1 }, go);
    inn($('.vs1', sc), go + 0.15, { y: -80, scale: 0.9 }, 0.55);
    inn($('.vs2', sc), go + 0.3, { y: 90 }, 0.6);
    pop($('.down', sc), w('hook', 5));
    $$('.vs2 .m-grok46, .vs2 .m-grok47', sc).forEach((el) => hi(el, w('hook', 6)));
    dim($$('.vs2 .mt', sc).filter((m) => !m.classList.contains('m-grok46') && !m.classList.contains('m-grok47')), w('hook', 6), 0.35);
    hi($('.vs1 .mt', sc), w('hook', 8), 1.08);
  }

  // 2. Тир-лист появляется в рамке планшета.
  {
    const sc = SC.post, t = s('post');
    tl.set($('.tab', sc), { opacity: 1 }, t);
    tl.fromTo($('.tab', sc), { y: 120, scale: 0.9 }, { y: 0, scale: 1, duration: 0.7, ease: 'power3.out' }, t + 0.05);
    tl.fromTo($('.tab', sc), { rotation: -2 }, { rotation: 1, duration: e('post') - t, ease: 'none' }, t);
  }

  // 3. Семь и два миллиона: число досчитывает, шарики насыпаются горкой.
  {
    const sc = SC.views, t = s('views');
    tl.fromTo($('.c7', sc), { textContent: 0 }, { textContent: 7, duration: 0.7, ease: 'power2.out', snap: { textContent: 1 } }, t + 0.05);
    tl.fromTo($('.big72', sc), { scale: 0.84 }, { scale: 1, duration: 0.8, ease: 'power3.out' }, t + 0.05);
    pop($('.dec', sc), t + 0.75);
    $$('.cap span', sc).forEach((el, k) => word(el, w('views', 2 + k)));
    pop($('.src', sc), w('views', 3) + 0.2);
    $$('.heap .ball', sc).forEach((b, i) => tl.fromTo(b, { opacity: 0, y: -520 - i * 30 }, { opacity: 1, y: 0, duration: 0.55, ease: 'bounce.out' }, t + 0.25 + i * 0.05));
  }

  // 4. Ответ Маска: «Accurate», потом плашка «(for now)», ниже перевод и растущий график.
  {
    const sc = SC.musk, t = s('musk');
    inn($('.card', sc), t + 0.05, { y: 60, scale: 0.94 }, 0.6);
    word($('.acc span', sc), w('musk', 2));
    pop($('.acc .fn', sc), w('musk', 4) - 0.1);
    tl.fromTo($('.acc .fn', sc), { boxShadow: '0 0 0 0 rgba(199,226,75,0)' }, { boxShadow: '0 0 40px 6px rgba(199,226,75,.45)', duration: 0.4 }, w('musk', 4));
    inn($('.tr2', sc), w('musk', 3) - 0.05, { y: 30 }, 0.4);
    $$('.bars i', sc).forEach((b, i) => tl.fromTo(b, { scaleY: 0 }, { scaleY: 1, duration: 0.5, ease: 'power3.out' }, t + 0.3 + i * 0.035));
  }

  // 5. Весь рейтинг: камера идёт по списку сверху вниз.
  {
    const sc = SC.look, t = s('look');
    inn($('.clipw', sc), t + 0.05, { scale: 0.94 }, 0.6);
    tl.fromTo($('.pan', sc), { y: 0 }, { y: -450, duration: e('look') - t + 0.2, ease: 'power1.inOut' }, t + 0.2);
  }

  // 6. Отдельный ранг: лестница рангов, под ней пунктир и отдельно Google.
  {
    const sc = SC.bottom, t = s('bottom');
    $$('.rung', sc).forEach((el, k) => inn(el, t + 0.05 + k * 0.05, { y: -30 }, 0.4));
    dim($$('.rung', sc), w('bottom', 2), 0.35);
    inn($('.dash', sc), w('bottom', 3) - 0.1, { scaleX: 0.2 }, 0.4);
    pop($('.gb', sc), w('bottom', 3));
    tl.fromTo($('.gb', sc), { boxShadow: '0 0 0 0 rgba(142,201,242,0)' }, { boxShadow: '0 0 80px 20px rgba(142,201,242,.7)', duration: 0.5 }, w('bottom', 4));
  }

  // 7. Ранг Google крупно.
  {
    const sc = SC.google, t = s('google');
    inn($('.gtile', sc), t + 0.05, { scale: 0.5 }, 0.55, 'back.out(1.3)');
    tl.fromTo($('.ring2', sc), { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1.25, duration: 0.9, ease: 'power2.out' }, w('google', 3) - 0.05);
    tl.to($('.ring2', sc), { opacity: 0, duration: 0.5 }, w('google', 3) + 0.85);
  }

  // 8. Там все Gemini: четыре плитки встают по одной.
  {
    const sc = SC.gem, t = s('gem');
    inn($('.glb', sc), t + 0.05, { x: 120, scale: 1.3 }, 0.55);
    $$('.grid4 .mt', sc).forEach((el, k) => pop(el, w('gem', 2) - 0.15 + k * 0.12));
  }

  // 9. Букву F пожалели: ряд Google наверху, ниже пустая карточка, F зачёркивается.
  {
    const sc = SC.f, t = s('f');
    inn($('.grow', sc), t + 0.05, { y: -60 }, 0.5);
    inn($('.fcard', sc), t + 0.25, { y: 60, scale: 0.94 }, 0.55);
    tl.fromTo($('.fl', sc), { opacity: 0, scale: 1.3 }, { opacity: 1, scale: 1, duration: 0.4, ease: 'expo.out' }, w('f', 3) - 0.08);
    draw($('.strike', sc), w('f', 4), 0.4, 'power3.out');
  }

  // 10. Чуть выше: ранг E крупно, кольцо идёт по Haiku, Mistral и Nemotron на их словах.
  {
    const sc = SC.e, t = s('e');
    inn($('.ed', sc), t + 0.05, { y: -50 }, 0.5);
    inn($('.ee', sc), t + 0.12, { scale: 0.9 }, 0.55);
    inn($('.eg', sc), t + 0.05, { y: 50 }, 0.5);
    const ms = $$('.ee .mt', sc);
    [2, 3, 5].forEach((wi, k) => { hi(ms[k], w('e', wi) - 0.05); if (k < 2) lo(ms[k], w('e', [3, 5][k]) - 0.05); });
  }

  // 11. Grok размазан: блок A–C в наклоне, Grok загорается в C и дважды в A, линия соединяет их.
  {
    const sc = SC.grok, t = s('grok');
    tl.set($('.abc', sc), { transformPerspective: 1400, transformOrigin: '50% 100%' }, 0);
    inn($('.abc', sc), t + 0.05, { y: 80, rotationX: 18 }, 0.7);
    const g45 = $('.m-grok45', sc), g46 = $('.m-grok46', sc), g47 = $('.m-grok47', sc);
    dim($$('.abc .mt', sc).filter((m) => m !== g45 && m !== g46 && m !== g47), w('grok', 3), 0.32);
    hi(g45, w('grok', 3));
    hi(g47, w('grok', 7) - 0.2);
    hi(g46, w('grok', 8) - 0.05);
    draw($('.gpath', sc), w('grok', 5), w('grok', 8) - w('grok', 5) + 0.2, 'power1.inOut');
    tl.fromTo($('.abc', sc), { x: 0 }, { x: -12, duration: e('grok') - t, ease: 'none' }, t);
  }

  // 12. Ранг A крупно: DeepSeek, Kimi, потом прошлые Claude.
  {
    const sc = SC.a, t = s('a');
    inn($('.arow', sc), t + 0.05, { x: -80 }, 0.55);
    const all = $$('.arow .mt', sc);
    const ds = $('.m-deepseekv41flash', sc), km = $('.m-kimik3', sc), o5 = $('.m-opus5', sc), f5 = $('.m-fable5', sc);
    dim(all.filter((m) => ![ds, km, o5, f5].includes(m)), w('a', 2), 0.3);
    dim([o5, f5], w('a', 2), 0.3);
    hi(ds, w('a', 3) - 0.05);
    hi(km, w('a', 4) - 0.05);
    tl.to([o5, f5], { opacity: 1, duration: 0.3 }, w('a', 6) - 0.05);
    hi(o5, w('a', 7) - 0.1);
    hi(f5, w('a', 7) - 0.1);
  }

  // 13. Ранг S: лучи, Fable 5.1 в центре, на «GPT-6 Sol» Fable уходит влево, Sol встаёт справа.
  {
    const sc = SC.s, t = s('s'), go = w('s', 6) - 0.1;
    tl.fromTo($('.rays', sc), { opacity: 0, rotation: -20, scale: 0.8 }, { opacity: 1, rotation: 0, scale: 1, duration: 0.8, ease: 'power3.out' }, t);
    tl.to($('.rays', sc), { rotation: 18, duration: e('s') - t - 0.8, ease: 'none' }, t + 0.8);
    pop($('.sl', sc), w('s', 1) - 0.1);
    inn($('.fb', sc), w('s', 3) - 0.15, { scale: 0.6, y: 20 }, 0.5, 'back.out(1.3)');
    tl.to($('.fb', sc), { x: -150, duration: 0.5, ease: 'power3.inOut' }, go);
    tl.fromTo($('.sol', sc), { opacity: 0, x: 320, scale: 0.8 }, { opacity: 1, x: 150, scale: 1, duration: 0.5, ease: 'power3.out' }, go + 0.1);
  }

  // 14. SS: подиум под лучом, GPT-6 Astra наверху, ниже бледный ранг S.
  {
    const sc = SC.ss, t = s('ss');
    $$('.pod', sc).forEach((el, k) => inn(el, t + 0.1 + k * 0.1, { y: 40 }, 0.5));
    inn($('.sbelow', sc), t + 0.15, { y: 40 }, 0.5);
    inn($('.ssr', sc), w('ss', 2) - 0.25, { y: -80, scale: 0.85 }, 0.6, 'power4.out');
    hi($('.ssr .mt', sc), w('ss', 4) - 0.05, 1.06);
  }

  // 15. SSS: один Claude Opus 5.5 на вершине, искры, тёплое пятно под ним.
  {
    const sc = SC.top, t = s('top');
    inn($('.ell', sc), t + 0.1, { scaleX: 0.4 }, 0.6);
    inn($('.sssr', sc), w('top', 4) - 0.2, { y: -120, scale: 0.8 }, 0.7, 'power4.out');
    hi($('.sssr .mt', sc), w('top', 6) - 0.05, 1.08);
    pop($('.cpill', sc), w('top', 6) - 0.1);
    $$('.spk', sc).forEach((el, k) => {
      const at = w('top', 6) + rnd(k + 3) * 1.2;
      tl.fromTo(el, { opacity: 0, scale: 0.2 }, { opacity: 1, scale: 1, duration: 0.25, ease: 'power2.out' }, at);
      tl.to(el, { opacity: 0, scale: 0.4, duration: 0.5, ease: 'power2.in' }, at + 0.3);
    });
  }

  // 16. Бьются за SSS: четыре плитки сходятся к центру и отскакивают, между ними искры.
  {
    const sc = SC.fight, t = s('fight');
    const dir = [[1, 1], [-1, 1], [1, -1], [-1, -1]];
    $$('.fgt', sc).forEach((el, i) => {
      inn(el, t + 0.05 + i * 0.06, { x: -dir[i][0] * 120, y: -dir[i][1] * 80, scale: 0.8 }, 0.45);
      tl.to(el, { x: dir[i][0] * 18, y: dir[i][1] * 14, rotation: dir[i][0] * 5, duration: 0.22, ease: 'power2.in', yoyo: true, repeat: 3 }, Math.max(w('fight', 1) - 0.1, t + 0.75) + i * 0.03);
    });
    $$('.spark', sc).forEach((el, k) => {
      tl.fromTo(el, { opacity: 0, scaleX: 0.2 }, { opacity: 1, scaleX: 1, duration: 0.12 }, w('fight', 1) + 0.1 + (k % 3) * 0.44);
      tl.to(el, { opacity: 0, duration: 0.2 }, w('fight', 1) + 0.25 + (k % 3) * 0.44);
    });
  }

  // 17. Siri: карточка, вопрос про погоду, колесо и «ищу ответ в интернете», полоски поиска мерцают.
  {
    const sc = SC.siri, t = s('siri'), end = e('siri');
    inn($('.siri', sc), t + 0.05, { y: 60, scale: 0.94 }, 0.55);
    tl.fromTo($('.sorb', sc), { rotation: 0 }, { rotation: 360, duration: end - t, ease: 'none' }, t);
    tl.fromTo($('.spin', sc), { rotation: 0 }, { rotation: 720, duration: end - t, ease: 'none' }, t);
    $$('.dots i', sc).forEach((d, k) => tl.fromTo(d, { opacity: 0.2 }, { opacity: 1, duration: 0.3, yoyo: true, repeat: Math.max(1, Math.floor((end - t) / 0.6)), ease: 'sine.inOut' }, t + k * 0.2));
    $$('.skel i', sc).forEach((el, k) => tl.fromTo(el, { x: -300 }, { x: 700, duration: 1.1, ease: 'power1.inOut', repeat: Math.max(0, Math.floor((end - t) / 1.1) - 1) }, t + 0.3 + k * 0.15));
  }

  // 18. Гонка: дорожки заполняются, Claude впереди, на слове «гонка» Grok догоняет.
  {
    const sc = SC.race, t = s('race'), go = w('race', 5) - 0.1;
    pop($('.fnp', sc), t + 0.15);
    $$('.lane2', sc).forEach((el, k) => {
      inn(el, t + 0.1 + k * 0.07, { x: -60 }, 0.45);
      const p = [0.93, 0.85, 0.58, 0.42][k];
      tl.fromTo($('.fill2', el), { scaleX: 0.05 }, { scaleX: p, duration: go - t - 0.3, ease: 'power2.out' }, t + 0.3);
      tl.fromTo($('.knob2', el), { x: 0 }, { x: (740 - 92) * p, duration: go - t - 0.3, ease: 'power2.out' }, t + 0.3);
    });
    const g = $('.ln2', sc);
    tl.to($('.fill2', g), { scaleX: 0.8, duration: 0.8, ease: 'power3.inOut' }, go);
    tl.to($('.knob2', g), { x: (740 - 92) * 0.8, duration: 0.8, ease: 'power3.inOut' }, go);
    tl.to($('.knob2', g), { boxShadow: '0 0 40px 8px rgba(199,226,75,.6)', duration: 0.3 }, go + 0.2);
  }

  // 19. На какой сидишь: плитки моделей встают сеткой, под ними вопрос.
  {
    const sc = SC.q, t = s('q');
    $$('.qt', sc).forEach((el, k) => pop(el, t + 0.1 + k * 0.07));
    $$('.qt', sc).forEach((el, k) => tl.to(el, { y: -10, duration: 0.6 + (k % 3) * 0.15, ease: 'sine.inOut', yoyo: true, repeat: 1 }, t + 0.8 + k * 0.05));
    inn($('.qmark', sc), w('q', 3) - 0.1, { scale: 1.4, filter: 'blur(14px)' }, 0.4, 'expo.out');
  }

  // 20. Комментарий: ранги встают, курсор жмёт SSS, текст набирается, «Отправить».
  {
    const sc = SC.com, t = s('com'), end = e('com');
    inn($('.cbox', sc), t + 0.05, { y: 50, scale: 0.95 }, 0.5);
    $$('.rkc', sc).forEach((el, k) => pop(el, t + 0.3 + k * 0.04));
    inn($('.sendb', sc), t + 0.5, { y: 20 }, 0.35);
    const cur = $('.cur', sc), tap = w('com', 3) - 0.1;
    tl.fromTo(cur, { opacity: 0, x: 760, y: 1200 }, { opacity: 1, x: 296, y: 768, duration: tap - t - 0.2, ease: 'power2.inOut' }, t + 0.2);
    tl.to(cur, { scale: 0.75, duration: 0.1, yoyo: true, repeat: 1 }, tap);
    tl.to($('.rkc.on', sc), { backgroundColor: '#C7E24B', color: '#12130F', scale: 1.1, duration: 0.2 }, tap + 0.05);
    type($$('.ch', sc), tap + 0.15, w('com', 4) + 0.3);
    tl.to(cur, { x: 540, y: 976, duration: 0.35, ease: 'power2.inOut' }, end - 0.75);
    tl.to(cur, { scale: 0.75, duration: 0.1, yoyo: true, repeat: 1 }, end - 0.4);
    tl.to($('.sendb', sc), { scale: 0.94, duration: 0.1, yoyo: true, repeat: 1 }, end - 0.4);
  }

  // 21. Скинь другу: выбрать друга, набрать «Siri, какая погода?», отправить.
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

  // 22. Призыв: весь рейтинг одной картинкой, потом знак Telegram, кот показывает на него. В конце «сохрани».
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
    inn($('.save', sc), w('link', 3) - 0.1, { y: 40, scale: 0.9 }, 0.45, 'back.out(1.2)');
    tl.to($('.save span', sc), { scale: 1.06, duration: 0.45, ease: 'sine.inOut', yoyo: true, repeat: 1 }, w('link', 3) + 0.5);
  }
  return tl;
};

/** Слой поверх сцен: знак канала, полоса ролика, бегунок рангов, заголовки, субтитры. */
export const overlayMarkup = (A, T) => {
  const lines = new Map();
  T.caps.forEach((c) => lines.set(c.line, [...(lines.get(c.line) || []), c]));
  return `<div class="logo"><img src="${A}/logo.png"></div>
<div class="prog">${'<i><b></b></i>'.repeat(9)}</div>
<div class="pg" data-layout-ignore><s></s><s class="pf"></s>${LADDER.map((n) => `<i></i>`).join('')}<b class="knob"></b></div>
` + headlines(T).map((h) => `<div class="hl ${h.light ? 'light' : ''}">${[h.l1, h.l2].map((line, k) => line.length ? `<div class="${k ? 'l2' : 'l1'}">${
    line.map(([txt, , c]) => `<span class="${c || ''}">${txt}</span>`).join('')}</div>` : '').join('')}</div>`).join('') + `
<div class="ccs">${[...lines.values()].map((ws) => `<div class="cc"><p>${ws.map((c) => `<span>${c.w}</span>`).join(' ')}</p></div>`).join('')}</div>`;
};

export const buildOverlay = (gsap, tl, root, T) => {
  const s = (id) => T.scenes[id].s;
  const e = (id) => T.scenes[id].e;
  const w = (id, i) => T.w[id][i];
  headlines(T).forEach((h, n) => {
    const box = root.querySelectorAll('.hl')[n];
    const spans = [...box.querySelectorAll('span')];
    [...h.l1, ...h.l2].forEach(([, at], i) =>
      tl.fromTo(spans[i], { opacity: 0, y: 24, filter: 'blur(12px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: i === 0 ? 0.3 : 0.38, ease: i === 0 ? 'expo.out' : 'power3.out' }, Math.max(h.from, at - 0.06)));
    tl.to(spans, { opacity: 0, filter: 'blur(12px)', duration: 0.24, ease: 'power2.in' }, h.to - 0.26);
  });

  // Субтитры: фраза целиком, слово загорается, когда звучит, сказанное остаётся светлым.
  const lines = new Map();
  T.caps.forEach((c) => lines.set(c.line, [...(lines.get(c.line) || []), c]));
  const groups = [...lines.values()];
  [...root.querySelectorAll('.cc')].forEach((box, n) => {
    const ws = groups[n], next = groups[n + 1];
    const from = Math.max(0, ws[0].s - 0.14), to = next ? next[0].s - 0.16 : T.length - 0.3;
    tl.fromTo(box, { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.2, ease: 'power3.out' }, from);
    tl.to(box, { opacity: 0, duration: 0.12, ease: 'power2.in' }, Math.max(from + 0.3, to - 0.12));
    [...box.querySelectorAll('span')].forEach((sp, i) => {
      tl.set(sp, { color: '#C7E24B' }, ws[i].s);
      if (ws[i + 1]) tl.set(sp, { color: '#F1F2EA' }, ws[i + 1].s);
    });
  });

  // Полоса ролика: на заставке её нет, она прорисовывается на смене первого кадра и идёт до самого
  // конца девятью отрезками по абзацам (README, «Ролик с голосом»).
  const prog = root.querySelector('.prog');
  const старт = s('post');
  [...prog.querySelectorAll('i')].forEach((el, i) =>
    tl.fromTo(el, { opacity: 0, scaleX: 0 }, { opacity: 1, scaleX: 1, duration: 0.45, ease: 'expo.out' }, старт + 0.1 + i * 0.05));
  const части = [старт + 0.3, s('musk'), s('bottom'), s('e'), s('s'), s('fight'), s('race'), s('q'), s('cta'), T.length - 0.4];
  [...prog.querySelectorAll('b')].forEach((b, i) =>
    tl.fromTo(b, { scaleX: 0 }, { scaleX: 1, duration: части[i + 1] - части[i], ease: 'none' }, части[i]));
  // Цвет полосы и бегунка следует за светом сцены.
  const pg = root.querySelector('.pg');
  [['post', 0], ['bottom', 1], ['grok', 0], ['siri', 1], ['race', 0]].forEach(([id, light]) =>
    tl.set([prog, pg], { '--pf': light ? '#56690C' : '#C7E24B', '--pt': light ? 'rgba(18,19,15,.16)' : 'rgba(241,242,234,.2)' }, s(id)));

  // Бегунок рангов: от отдельного ранга Google до SSS. Точка встаёт на ранг, когда о нём говорят.
  const X = (k) => 34 + k * 52;
  tl.fromTo(pg, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.45, ease: 'power3.out' }, s('bottom') + 0.2);
  tl.to(pg, { opacity: 0, duration: 0.3 }, e('fight') - 0.26);
  const knob = root.querySelector('.knob'), fill = root.querySelector('.pg .pf');
  tl.set(knob, { x: X(0) }, 0);
  tl.set(fill, { scaleX: 0 }, 0);
  [[w('e', 0), 1], [w('grok', 6), 3], [w('grok', 8), 5], [w('s', 1), 6], [w('ss', 1), 7], [w('top', 3), 8]].forEach(([at, k]) => {
    tl.to(knob, { x: X(k), duration: 0.45, ease: 'power3.inOut' }, at - 0.1);
    tl.to(fill, { scaleX: k / 8, duration: 0.45, ease: 'power3.inOut' }, at - 0.1);
  });
  return tl;
};

/** Картинка рейтинга для Telegram (ролик её обещает): весь тир-лист, заголовок, знак канала. 1080×1350. */
export const pictureMarkup = (A) => `<div class="pic">
  <div class="logo" style="left:64px;top:56px"><img src="${A}/logo.png"></div>
  <div class="pt"><b>Рейтинг нейросетей</b><span>Маск ответил: «Accurate (for now)»</span></div>
  <div class="tab abs" style="left:248px;top:250px;width:584px;height:1064px"><div style="transform:scale(0.6);transform-origin:0 0;width:max-content">${list(A, LADDER.slice().reverse())}</div></div>
</div>`;
