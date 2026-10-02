// Ролик «5 бесплатных плагинов», улучшенная версия (r11). Движок один: HyperFrames.
//
// Основа — сцены r10 (рерайт рилса @chingizkhan_yt). Что изменено и по какому скилу, записано
// в ../ЧТО-УЛУЧШЕНО.md. Коротко: крючок говорит результат, а не перечень; крупное набрано
// широким Unbounded против ровного Onest; внизу субтитры по словам для тех, кто смотрит без
// звука; вверху полоса «какой плагин из пяти»; появления идут с разных сторон и с разной
// скоростью; зерно, блик по стеклу, вспышка на смене света, конфетти на слове «бесплатно».
//
// Тезис тот же: состояние — одна фраза голоса, движется то, о чём говорят. Характер «дорогой»,
// но крючок и доказательство в конце резче остального: они работают на остановку и досмотр.
// Всё записано твинами без обратных вызовов: перемотка в любую секунду даёт верный кадр.
// Селекторы склеиваются плюсом, а не шаблонной строкой: на ней падает разбор HyperFrames.

export const PLUGINS = [
  { id: 'c1', name: 'HyperFrames', url: 'heygen-com/hyperframes', stars: '55 тыс.', icon: 'hyperframes.png' },
  { id: 'c2', name: 'Remotion', url: 'remotion-dev/remotion', stars: '61 тыс.', icon: 'remotion.png' },
  { id: 'c3', name: 'taste-skill', url: 'Leonxlnx/taste-skill', stars: '92 тыс.', icon: 'taste.png' },
  { id: 'c4', name: 'impeccable', url: 'pbakaus/impeccable', stars: '74 тыс.', icon: 'impeccable.png' },
  { id: 'c5', name: 'Эмиль Ковальски', url: 'emilkowalski/skills', stars: '43 тыс.', icon: '' },
];

const GH = '<svg viewBox="0 0 24 24"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C2.422 18.07 1.633 17.7 1.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>';
const STAR = 'M12 1.6l3.1 6.6 7.1.9-5.2 5 1.3 7.1L12 17.7 5.7 21.2 7 14.1 1.8 9.1l7.1-.9z';
const SPARK = '<svg viewBox="0 0 24 24"><path d="M12 1l2.2 7.3L21.5 10l-7.3 2.2L12 19.5l-2.2-7.3L2.5 10l7.3-1.7zM19.5 15l.9 2.6 2.6.9-2.6.9-.9 2.6-.9-2.6-2.6-.9 2.6-.9z"/></svg>';
const USER = '<svg viewBox="0 0 24 24"><circle cx="12" cy="8.5" r="4"/><path d="M4.5 20.5c1-4 4-5.5 7.5-5.5s6.500 1.500 7.500 5.500"/></svg>';
const CHECK = '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path class="ck" d="M7.500 12.400l3.100 3.100 6-6.500"/></svg>';
const TERM = '<svg viewBox="0 0 24 24"><path d="M5 7l5 5-5 5M12.500 17.500H19"/></svg>';
const PLANE = '<svg viewBox="0 0 24 24"><path d="M21.900 3.300 2.700 10.700c-1.300.500-1.300 1.300-.200 1.600l4.900 1.500 1.900 5.800c.200.700.400.900.900.900.400 0 .600-.200.900-.500l2.300-2.300 4.900 3.600c.900.500 1.500.200 1.800-.800l3.200-15.200c.300-1.300-.500-1.900-1.400-2zM8.300 13.500l10-6.300c.500-.300.900-.100.500.200l-8.200 7.400-.300 3.400z"/></svg>';

// Псевдослучайное число по зерну: одно и то же в каждой вкладке рендера.
// За сколько секунд HyperFrames считает этот ролик на маке владельца. Число звучит в ролике:
// после правок, меняющих время рендера, его перемеряют и переозвучивают фразу proof.
export const RENDER_SECONDS = 67;

const rnd = (seed) => { const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

const chips = (A, top, extra = '', style = '') => `<div class="chips ${extra}" style="top:${top}px;${style}">${PLUGINS.map((p) =>
  `<div class="chip h">${p.icon ? `<img src="${A}/${p.icon}">` : '<b>EK</b>'}<u></u></div>`).join('')}</div>`;

const wave = (top, color = '') => `<div class="wave" style="top:${top}px">${Array.from({ length: 58 }, (_, i) =>
  `<i style="height:${Math.round(10 + 64 * rnd(i + 3) * (0.35 + 0.65 * Math.abs(Math.sin(i * 0.4))))}px;${color ? `background:${color}` : ''}"></i>`).join('')}<b></b></div>`;

const slop = `<div class="slop">${SPARK}<b>AI-Powered Magic</b><small>Revolutionize your workflow</small><span>Get Started</span></div>`;
const slopGrid = (extra = '') => `<div class="slopwrap" data-layout-ignore style="${extra}"><div class="mover abs" style="inset:0"><div class="slopgrid">${slop.repeat(30)}</div></div></div>`;

const HERO = (A) => ({
  c1: `<div class="hero cream"><img src="${A}/hyperframes.png" style="mix-blend-mode:multiply"><div class="wm"><small>HeyGen</small>HyperFrames</div></div>`,
  c2: `<div class="hero white"><img src="${A}/remotion.png"><div class="wm" style="font-size:104px">remotion</div></div>`,
  c3: `<div class="hero cream" style="background:#F3EEDF"><img src="${A}/taste.png"><div class="wm" style="font-weight:600;font-size:74px">Taste Skill<small style="font-size:22px;font-weight:500;letter-spacing:0;opacity:.55;margin-top:14px">Anti-Slop Frontend Framework</small></div></div>`,
  c4: `<div class="hero black" style="flex-direction:column;gap:22px"><div class="slopcard"><span class="mono">+ gradient text</span><b>AI-Powered Magic</b><small>Reimagining the future of everything</small></div><div style="font-size:26px;letter-spacing:0;opacity:.7">Detect AI slop in any web page.</div></div>`,
  c5: `<div class="hero black"><div class="emil"><div>Emil Kowalski<b>animations.dev</b></div></div></div>`,
});

const CODEBG = {
  c1: `&lt;div id="frame" data-composition-id="<em>reel</em>" data-fps="30"&gt;
  data-width="<em>1080</em>" data-height="<em>1920</em>" data-duration="<em>57</em>"
  &lt;section class="scene" data-start="<em>8.7</em>"&gt;
    &lt;h1 class="title"&gt;HyperFrames&lt;/h1&gt;
    &lt;div class="glass window"&gt;&lt;/div&gt;
  &lt;/section&gt;
  &lt;audio data-start="0" src="<em>voice.wav</em>"&gt;`,
  c2: `import {useCurrentFrame, interpolate} from <em>'remotion'</em>;

export const Reel = () =&gt; {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 1]);
  return (
    &lt;AbsoluteFill style={{opacity}}&gt;
      &lt;Captions words={words} /&gt;`,
  c3: `## 9. AI TELLS (Forbidden Patterns)
  NO neon / outer glows by default
  NO 3-column equal feature cards
  NO gradient text for large headers
  DESIGN_VARIANCE: <em>8</em>
  MOTION_INTENSITY: <em>6</em>
  VISUAL_DENSITY: <em>4</em>`,
  c4: `/critique   /audit    /polish   /layout
/typeset    /bolder   /quieter  /distill
/colorize   /animate  /delight  /overdrive
/harden     /onboard  /clarify  /adapt
/shape      /extract  /optimize /document`,
  c5: `--ease-out: cubic-bezier(<em>0.23, 1, 0.32, 1</em>);
--ease-in-out: cubic-bezier(<em>0.77, 0, 0.175, 1</em>);
transition: transform <em>200ms</em> var(--ease-out);
.button:active { transform: scale(<em>0.97</em>); }
@starting-style { opacity: 0; }`,
};

const card = (A, p, i, light) => `<div class="sc ${light ? 'light' : ''}" id="sc-${p.id}">
  <pre class="codebg mono" data-layout-ignore>${CODEBG[p.id]}</pre>
  <div class="p3" style="left:170px;top:400px;width:740px"><div class="repo h"><div class="shim"></div>
    <div class="bar"><i></i><i></i><i></i><div class="url">${GH}github.com/${p.url}</div></div>
    ${HERO(A)[p.id]}
    <div class="foot"><div class="name h">${p.name}</div><div><div class="stars h"><svg viewBox="0 0 24 24"><path d="${STAR}"/></svg>${p.stars}</div></div></div>
  </div></div>
  ${chips(A, 1170)}
</div>`;

const RING = ['/clarify', '/adapt', '/overdrive', '/delight', '/layout', '/typeset', '/colorize', '/animate', '/onboard', '/harden', '/distill', '/quieter', '/bolder', '/shape', '/extract', '/document'];
const FILM5 = (A) => [
  `<div class="cell" style="width:250px;background:#ECEBDD"><img src="${A}/hyperframes.png" style="mix-blend-mode:multiply"></div>`,
  `<div class="cell" style="width:430px;background:#fff;grid-auto-flow:column;gap:14px;color:#12130F;font-size:78px;font-weight:800;letter-spacing:-0.04em"><img src="${A}/remotion.png" style="width:100px">remotion</div>`,
  `<div class="cell" style="width:250px;background:#F3EEDF"><img src="${A}/taste.png"></div>`,
  `<div class="cell" style="width:250px;background:#0D0E0A"><img src="${A}/impeccable.png"></div>`,
  `<div class="cell" style="width:250px;background:#0D0E0A;color:#F1F2EA;font-size:84px;font-weight:700;letter-spacing:0">EK</div>`,
].join('');

/** Разметка всех сцен. A — адрес папки с картинками. */
export const markup = (A) => `
<div class="bg bg-light"></div>
<div class="glow glow-lime" data-layout-ignore style="opacity:1"><i></i></div><div class="glow glow-warm" data-layout-ignore><i></i></div><div class="glow glow-mint" data-layout-ignore><i></i></div>
<div class="vignette" style="opacity:1"></div>

<div class="sc" id="sc-hook" style="opacity:1">
  <div class="floats abs" data-layout-ignore style="inset:0">
    <div class="float" style="left:-110px;top:96px;width:400px;height:250px;background:#ECEBDD;transform:rotate(-7deg)"><img src="${A}/hyperframes-logo.png" style="object-fit:contain;mix-blend-mode:multiply"></div>
    <div class="float" style="left:800px;top:120px;width:400px;height:240px;background:#fff;transform:rotate(6deg)"><img src="${A}/remotion.png" style="object-fit:contain"></div>
    <div class="float" style="left:-90px;top:1010px;width:450px;height:340px;transform:rotate(8deg)"><img src="${A}/shot-d.jpg"></div>
    <div class="float" style="left:730px;top:980px;width:430px;height:370px;transform:rotate(-9deg)"><img src="${A}/shot-a.jpg"></div>
  </div>
  <div class="abs" data-layout-ignore style="inset:0;background:radial-gradient(ellipse 70% 34% at 50% 34%,rgba(10,11,8,.82),rgba(10,11,8,0))"></div>
  <div class="kt"><div class="k1">Этот ролик</div><div class="k2">никто не</div><div class="k3"><span>монтировал</span></div></div>
  <div class="peek abs h" style="left:400px;top:880px;width:280px"><img src="${A}/cat-hi.png" style="width:100%"></div>
</div>

<div class="sc" id="sc-five">
  <div class="tile"><span class="num">1</span><div class="shim"></div></div>
  <div class="cap" style="top:1006px"><span class="h">бесплатных</span> <span class="h">плагинов</span></div>
  ${chips(A, 1150)}
</div>

<div class="sc" id="sc-hook2">
  <div class="win glass h">
    <div class="bar"><i></i><i></i><i></i><div class="ttl"><s>✳</s>Claude Code</div></div>
    <div class="prompt"><em>›</em>${[...'собери ролик'].map((c) => `<span class="ch h">${c}</span>`).join('')}<u></u></div>
    ${chips(A, 232, 'sm', 'left:56px;width:auto')}
    <div class="track" style="top:372px"><i></i></div>
  </div>
  <div class="tline glass h">
    <div class="cell h" style="background:#ECEBDD"><img src="${A}/hyperframes.png" style="mix-blend-mode:multiply"></div>
    <div class="cell h" style="background:#fff"><img src="${A}/remotion.png"></div>
    <div class="cell h" style="background:#F3EEDF"><img src="${A}/taste.png"></div>
    <div class="cell h" style="background:#0D0E0A"><img src="${A}/impeccable.png"></div>
    <div class="cell h" style="background:#0D0E0A"><img src="${A}/shot-b.jpg" style="width:100%;height:100%;object-fit:cover;border-radius:0"></div>
  </div>
  <div class="head abs h" style="left:150px;top:1118px;width:0"><img src="${A}/cat-face.png" style="width:62px;margin-left:-28px"><i style="display:block;width:5px;height:150px;margin:-6px 0 0 0;background:#F1F2EA;border-radius:3px"></i></div>
</div>

<div class="sc" id="sc-all">
  <div class="p3" style="left:0;top:520px;width:1080px;height:760px">
    <div class="ph-l abs h" style="left:118px;top:60px"><div style="transform:rotateY(34deg) rotateZ(-7deg) scale(.9)"><div class="phone"><img src="${A}/shot-a.jpg"></div></div></div>
    <div class="ph-r abs h" style="left:622px;top:60px"><div style="transform:rotateY(-34deg) rotateZ(7deg) scale(.9)"><div class="phone cream" style="display:grid;place-items:center"><div style="width:170px;height:170px;border-radius:44px;background:#12130F;display:grid;place-items:center"><img src="${A}/logo.png" style="width:110px;height:110px"></div></div></div></div>
    <div class="ph-c abs h" style="left:370px;top:16px"><div class="phone">
      <img src="${A}/shot-b.jpg" style="height:56%;opacity:.9">
      <div class="abs" style="left:0;right:0;top:30%;height:30%;background:linear-gradient(rgba(13,14,10,0),#0D0E0A)"></div>
      <div class="labels"><span><u></u><b>кадры</b></span><span><u></u><b>движение</b></span><span><u></u><b>субтитры</b></span></div>
      <div class="orb h" style="left:135px;bottom:16px"></div>
    </div></div>
  </div>
  ${wave(1250)}
</div>

${card(A, PLUGINS[0], 0, true)}

<div class="sc light" id="sc-hf">
  <div class="p3" style="left:0;top:0;width:1080px;height:1920px">
    <div class="paper abs h" style="left:170px;top:520px;width:740px"><div class="code paper mono"><span class="fn">index.html</span>&lt;div id="frame" data-composition-id=<em>"reel"</em>
     data-width=<em>"1080"</em> data-height=<em>"1920"</em>&gt;
  &lt;<b>section</b> class=<em>"scene"</em> data-start=<em>"8.7"</em>&gt;
    &lt;<b>h1</b> class=<em>"title"</em>&gt;HyperFrames&lt;/<b>h1</b>&gt;
    &lt;<b>div</b> class=<em>"glass window"</em>&gt;&lt;/<b>div</b>&gt;
  &lt;/<b>section</b>&gt;
  &lt;<b>video</b> class=<em>"clip"</em> data-start=<em>"11.1"</em>
         src=<em>"page.mp4"</em>&gt;&lt;/<b>video</b>&gt;
  &lt;<b>audio</b> data-start=<em>"0"</em>
         src=<em>"voice.wav"</em>&gt;&lt;/<b>audio</b>&gt;
&lt;/div&gt;</div></div>
    <div class="player abs h" style="left:370px;top:500px"><div class="phone cream">
      <div class="pill h" style="position:absolute;left:54px;top:34px;font-size:27px;height:56px;color:#12130F;font-weight:700;letter-spacing:0"><i style="width:14px;height:14px;border-radius:50%;background:#56690C;display:block"></i>HTML → MP4</div>
      <img src="${A}/hyperframes.png" style="width:210px;height:210px;position:absolute;left:65px;top:230px;mix-blend-mode:multiply">
      <div class="track" style="left:44px;right:44px;bottom:60px;background:rgba(18,19,15,.14)"><i style="background:#56690C"></i></div>
    </div></div>
  </div>
  <div class="strip abs h" data-layout-ignore style="left:-60px;top:1110px;width:1220px"><div style="transform:rotate(-3deg)"><div class="film" style="height:190px">${
    Array.from({ length: 8 }, () => `<div class="cell h" style="width:128px;background:#ECEBDD"><img src="${A}/hyperframes.png" style="mix-blend-mode:multiply"></div>`).join('')}</div></div></div>
</div>

<div class="sc light" id="sc-stars">
  <svg class="ghmark h" viewBox="0 0 24 24"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C2.422 18.07 1.633 17.7 1.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>
  <svg class="chart" viewBox="0 0 1080 1920"><polyline class="lnA" points="-20,1210 160,1150 300,1180 470,1080 640,1110 800,1000 960,1030 1100,930" fill="none" stroke="#56690C" stroke-width="3" opacity=".55"/>
    ${[[160, 1150], [470, 1080], [800, 1000]].map(([x, y]) => `<circle class="dot h" cx="${x}" cy="${y}" r="11" fill="#56690C"/>`).join('')}</svg>
  ${Array.from({ length: 16 }, (_, i) => { const s = 22 + Math.round(rnd(i + 20) * 30); return `<svg class="star tw h" style="left:${Math.round(60 + rnd(i + 1) * 940)}px;top:${Math.round(330 + rnd(i + 40) * 880)}px;width:${s}px;height:${s}px;opacity:.5" viewBox="0 0 24 24"><path d="${STAR}"/></svg>`; }).join('')}
  <svg class="star top h" style="left:490px;top:390px;width:100px;height:100px" viewBox="0 0 24 24"><path d="${STAR}"/></svg>
  <div class="big" style="top:520px"><span class="cnt">12</span><span class="tys h"> тыс.</span></div>
  <div class="cap" style="top:780px;color:#3A3E2D"><span class="h">звёзд</span> <span class="h">на</span> <span class="h" style="color:#12130F">GitHub</span></div>
</div>

${card(A, PLUGINS[1], 1, false)}

<div class="sc" id="sc-rem">
  <div class="p3" style="left:0;top:0;width:1080px;height:1920px">
    <div class="tsx abs h" style="left:-70px;top:640px;width:520px"><div class="code night mono" style="font-size:24px">const Reel = () =&gt; {
  const frame =
    <b>useCurrentFrame</b>();
  const o = <b>interpolate</b>(
    frame, [<em>0</em>, <em>30</em>], [<em>0</em>, <em>1</em>]);

  &lt;<b>Captions</b>
     words={words} /&gt;
  &lt;<b>RouteMap</b>
     from=<em>"A"</em> to=<em>"B"</em> /&gt;</div></div>
    <div class="map abs h" style="left:730px;top:650px;width:460px;height:470px"><div class="gridp" style="width:100%;height:100%"><svg viewBox="0 0 460 470" style="width:100%;height:100%"><path class="route" d="M-10 330 C 90 250, 150 400, 240 300 S 380 180, 470 210" fill="none" stroke="#C7E24B" stroke-width="12" stroke-linecap="round"/><circle class="pin h" cx="60" cy="302" r="14" fill="#F1F2EA"/></svg></div></div>
    <div class="shot abs h" style="left:370px;top:520px"><div class="phone"><img src="${A}/shot-b.jpg">
      <div class="pill mono" style="position:absolute;left:44px;top:32px;font-size:27px;height:56px;background:rgba(13,14,10,.72)">кадр <span class="fr">520</span></div>
    </div></div>
  </div>
  <div class="caps abs" style="left:300px;top:1066px;width:600px;font-size:46px;display:flex;gap:18px;align-items:center"><span class="tag h">субтитры,</span><span class="h" style="text-shadow:0 2px 18px rgba(0,0,0,.6)">карты</span></div>
  <div class="rbar h" style="top:404px"><span>render <b class="pc">0</b>%</span><div class="fill abs" style="inset:0;background:#C7E24B;border-radius:46px"><span style="color:#12130F;mix-blend-mode:normal;filter:none">render <b class="pc">0</b>%</span></div></div>
  ${wave(1250)}
</div>

<div class="sc" id="sc-free">
  <div class="burst abs" data-layout-ignore style="left:540px;top:900px;width:0;height:0">${Array.from({ length: 26 }, (_, i) => `<i class="cf" style="background:${['#C7E24B', '#F1F2EA', '#89A81C'][i % 3]}"></i>`).join('')}</div>
  <div class="rbar" style="top:404px"><div class="abs" style="inset:0;background:#C7E24B;border-radius:46px"></div><span style="color:#12130F;mix-blend-mode:normal;filter:none">render 100%</span></div>
  <div class="abs" style="left:-220px;top:1040px;width:1560px"><div style="transform:rotate(-14deg)"><div class="roll" data-layout-ignore><div class="film" style="height:170px">${
    Array.from({ length: 9 }, () => `<div class="cell" style="width:200px;background:#fff;grid-auto-flow:column;gap:8px;color:#12130F;font-size:34px;font-weight:800"><img src="${A}/remotion.png" style="width:52px">remotion</div>`).join('')}</div></div></div></div>
  <div class="panel glass abs h" style="left:210px;top:620px;width:660px;height:500px;text-align:center">
    <div class="users" style="margin-top:60px"><i class="h">${USER}</i><i class="h">${USER}</i><i class="h">${USER}</i></div>
    <div class="freeb h" style="font-size:92px;line-height:1;margin-top:52px">Бесплатно</div>
    <div class="frees" style="font-size:54px;color:var(--dim);margin-top:22px"><span class="h">до</span> <span class="h">трёх</span> <span class="h">человек</span></div>
  </div>
</div>

${card(A, PLUGINS[2], 2, true)}

<div class="sc light" id="sc-copy">
  ${slopGrid()}
  <div class="abs" style="left:0;top:0;width:1080px;height:560px;background:linear-gradient(#F1F2EA 34%,rgba(241,242,234,0))"></div>
  <div class="lens h" data-layout-ignore>${slop}</div>
</div>

<div class="sc light" id="sc-taste">
  ${slopGrid('filter:blur(12px);opacity:.42')}
  <div class="abs" style="left:0;top:0;width:1080px;height:560px;background:linear-gradient(#F1F2EA 34%,rgba(241,242,234,0))"></div>
  <div class="back abs h" style="left:720px;top:1010px;width:440px;height:400px"><div style="transform:rotate(7deg);width:100%;height:100%;border-radius:30px;overflow:hidden;box-shadow:0 40px 90px rgba(40,50,10,.3)"><img src="${A}/shot-c.jpg" style="width:100%;height:100%;object-fit:cover"></div></div>
  <div class="site h"><div class="bar"><i></i><i></i><i></i><div class="url" style="color:#12130F"><img src="${A}/taste.png" style="width:30px;height:30px;border-radius:8px">taste-skill · пример</div></div>
    <div class="page"><img class="hero-img" src="${A}/shot-b.jpg"><h4>Кот<br><i>режиссёр.</i></h4><p>Каждый кадр собран под задачу, а не взят из шаблона.</p><div class="cta-s">Смотреть</div>
      <div class="thumbs"><img class="h" src="${A}/shot-a.jpg"><img class="h" src="${A}/shot-d.jpg"><img class="h" src="${A}/shot-c.jpg"></div></div></div>
  <div class="anti pill h" style="position:absolute;left:400px;top:1290px;font-size:36px;height:72px;color:#12130F;font-weight:700"><i style="width:26px;height:26px;border-radius:50%;background:radial-gradient(circle at 36% 30%,#fff,#C7E24B 40%,#56690C);display:block"></i>Anti-Slop</div>
</div>

${card(A, PLUGINS[3], 3, false)}

<div class="sc" id="sc-n24">
  <div class="abs" style="left:120px;top:1330px;width:840px;opacity:.5;filter:blur(2px)"><div style="transform:rotate(-5deg)"><div class="slopcard"><span class="mono">+ gradient text</span><b>AI-Powered Magic</b><small>Reimagining the future of everything</small></div></div></div>
  <div class="ring h" data-layout-ignore>${RING.map((wd, i) => { const up = i % 2 === 0; const k = Math.floor(i / 2) / 7;
    // верхняя дуга обходит подпись, нижняя не доходит до слов под числом
    const a = up ? Math.PI * (1.04 + 0.92 * k) : Math.PI * (0.06 + 0.88 * k);
    const x = Math.round(Math.cos(a) * 440); const y = Math.round(Math.sin(a) * (up ? 215 : 165));
    return `<span class="mono" style="left:${x}px;top:${y}px;transform:translate(-50%,-50%)">${wd}</span>`; }).join('')}</div>
  <div class="cap h lbl" style="top:276px;font-size:58px;color:var(--dim)">impeccable</div>
  <div class="big n24" style="top:428px"><span class="cnt">1</span></div>
  <div class="cap" style="top:838px;font-size:76px"><span class="h">команды</span> <span class="h">для</span> <span class="h">дизайна</span></div>
  <div class="list glass h mono"><div><u></u><s>⌘</s><b>/critique</b></div><div><u></u><s>⌘</s><b>/audit</b></div><div><u></u><s>⌘</s><b>/polish</b></div></div>
</div>

<div class="sc" id="sc-fix">
  <div class="guides"></div>
  <div class="wf bad h"><h5>AI-Powered Magic</h5>
    <div class="blk" style="left:30px;top:130px;width:626px;height:194px"><div class="blk in" style="left:26px;top:28px;width:540px;height:130px"><div class="ln" style="left:28px;top:36px;width:300px"></div><div class="ln" style="left:28px;top:70px;width:210px;opacity:.6"></div></div></div>
    <div class="blk" style="left:40px;top:358px;width:176px;height:140px"></div><div class="blk" style="left:252px;top:342px;width:194px;height:164px"></div><div class="blk" style="left:476px;top:366px;width:170px;height:136px"></div></div>
  <div class="mark m1 h" style="left:216px;top:588px;width:500px;height:92px"></div>
  <div class="mark m2 h" style="left:206px;top:676px;width:654px;height:222px"></div>
  <div class="mark m3 h" style="left:400px;top:880px;width:64px;height:64px;border-radius:50%"></div>
  <div class="wf good"><h5>AI-Powered Magic</h5>
    <div class="blk" style="left:44px;top:136px;width:612px;height:184px"><div class="blk in" style="left:26px;top:27px;width:560px;height:130px"><div class="ln" style="left:28px;top:36px;width:300px"></div><div class="ln" style="left:28px;top:70px;width:210px;opacity:.6"></div></div></div>
    <div class="blk" style="left:44px;top:352px;width:192px;height:150px"></div><div class="blk" style="left:254px;top:352px;width:192px;height:150px"></div><div class="blk" style="left:464px;top:352px;width:192px;height:150px"></div></div>
  <div class="wipe h"></div>
  <div class="abs mono" style="left:0;top:1150px;width:1080px;height:70px">${['/audit', '/layout', '/polish'].map((c) => `<div class="cmd h abs" style="left:0;width:1080px;text-align:center"><span class="pill" style="font-size:34px"><span style="opacity:.5">⌘</span>${c}</span></div>`).join('')}</div>
  <div class="slots"><i></i><i></i><i></i><i></i><i></i><i></i></div>
</div>

${card(A, PLUGINS[4], 4, true)}

<div class="sc light" id="sc-made">
  <div class="abs h tst" style="left:640px;top:440px"><div style="transform:rotate(4deg)"><div class="toast" style="position:relative"></div></div></div>
  <div class="vercel abs h" style="left:150px;top:560px;width:340px"><svg viewBox="0 0 340 300" style="width:100%;overflow:visible"><defs><linearGradient id="vg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4A4D3E"/><stop offset="1" stop-color="#12130F"/></linearGradient></defs><polygon points="170,6 334,290 6,290" fill="#9A9C8E" transform="translate(10 12)"/><polygon points="170,6 334,290 6,290" fill="url(#vg)"/></svg></div>
  <div class="linear abs h" style="left:570px;top:800px;width:300px"><svg viewBox="0 0 100 100" style="width:100%"><defs><clipPath id="lc"><circle cx="50" cy="50" r="48"/></clipPath><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8B93E8"/><stop offset="1" stop-color="#5E6AD2"/></linearGradient></defs><g clip-path="url(#lc)"><rect width="100" height="100" fill="url(#lg)"/><g stroke="#F1F2EA" stroke-width="7"><line x1="-10" y1="38" x2="62" y2="110"/><line x1="-10" y1="56" x2="44" y2="110"/><line x1="-10" y1="74" x2="26" y2="110"/></g></g></svg></div>
  <div class="sheet abs h" style="left:370px;top:1180px;width:340px;height:300px;border-radius:44px;background:rgba(255,255,255,.9);box-shadow:0 30px 70px rgba(60,74,12,.2)"><div style="margin:26px auto 0;width:70px;height:8px;border-radius:4px;background:rgba(18,19,15,.3)"></div><div style="margin:44px 40px 0;height:12px;border-radius:6px;background:rgba(86,105,12,.3)"></div><div style="margin:20px 40px 0;width:150px;height:12px;border-radius:6px;background:rgba(86,105,12,.2)"></div></div>
</div>

<div class="sc light" id="sc-teach">
  ${[['рывком', 600], ['плавно', 880]].map(([label, top], n) => `<div class="lane l${n} h" style="top:${top}px">${
    Array.from({ length: 6 }, (_, k) => { const p = k / 5; const e = n ? (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2) : p; return `<i style="left:${Math.round(36 + e * 584)}px"></i>`; }).join('')}<b></b></div>
  <div class="abs lab${n} h" style="left:0;top:${top + 146}px;width:1080px;text-align:center"><span class="pill" style="color:#12130F;font-size:34px"><i style="width:14px;height:14px;border-radius:50%;background:${n ? '#56690C' : '#9A9C8E'};display:block"></i>${label}</span></div>`).join('')}
  <div class="curve abs h" style="left:230px;top:1090px;width:620px;height:250px;border-radius:36px;background:rgba(255,255,255,.9);box-shadow:0 30px 70px rgba(60,74,12,.2)"><svg viewBox="0 0 620 250" style="width:100%;height:100%"><path class="ease" d="M70 200 C 190 200, 260 54, 550 50" fill="none" stroke="#56690C" stroke-width="6" stroke-linecap="round"/><circle cx="70" cy="200" r="11" fill="#12130F"/><circle class="h end" cx="550" cy="50" r="11" fill="#56690C"/></svg></div>
</div>

<div class="sc light" id="sc-rules">
  <div class="abs h ec" style="left:520px;top:450px"><div style="transform:rotate(-9deg)"><div class="ecard" style="position:relative;color:#F1F2EA"><div class="emil"><div style="font-size:30px;padding:18px 30px">Emil Kowalski<b>animations.dev</b></div></div></div></div></div>
  <svg class="chart" viewBox="0 0 1080 1920"><path class="arc" d="M60 1500 C 150 1260, 250 1080, 400 960" fill="none" stroke="#56690C" stroke-width="4" opacity=".5"/></svg>
  ${['Плавность', 'Скорость', 'Длительность'].map((r, i) => `<div class="rule h" style="top:${640 + i * 158}px">${CHECK}${r}</div>`).join('')}
</div>

<div class="sc" id="sc-final">
  <div class="abs" style="left:-120px;top:600px;width:1500px"><div style="transform:rotate(-4deg)"><div class="reel" data-layout-ignore><div class="film" style="height:300px;width:3400px">${FILM5(A)}${FILM5(A)}</div></div></div></div>
  <div class="needle abs h" style="left:537px;top:500px"><img src="${A}/cat-face.png" style="width:84px;margin-left:-39px"><i style="display:block;width:6px;height:470px;margin-top:-8px;background:#F1F2EA;border-radius:3px;box-shadow:0 0 24px rgba(241,242,234,.7)"></i></div>
  ${chips(A, 1100)}
  ${wave(1250, 'rgba(217,119,87,.62)')}
</div>

<div class="sc" id="sc-proof">
  <div class="cap h plbl" style="top:372px;font-size:54px;color:var(--dim)">рендер этого ролика</div>
  <div class="big pnum" style="top:520px"><span class="cnt">0</span></div>
  <div class="cap h psec" style="top:930px;font-size:92px">секунд</div>
  <div class="rbar" style="top:1110px"><span>готово <b class="pc">0</b>%</span><div class="fill abs" style="inset:0;background:#C7E24B;border-radius:46px"><span style="color:#12130F">готово <b class="pc">0</b>%</span></div></div>
</div>

<div class="sc" id="sc-cta">
  <div class="ghost" data-layout-ignore style="left:40px;top:700px">&gt;_</div>
  <div class="first abs" style="inset:0">
    <div class="ibox glass h">${TERM}</div>
    <div class="cap h ctat" style="top:540px;font-size:104px">5 команд</div>
    <div class="row glass h r1" style="top:740px"><s class="mono">⌘</s>установки</div>
    <div class="row glass h r2" style="top:884px"><s class="mono">5</s>всех пяти плагинов</div>
  </div>
  <div class="tg h" style="left:310px;top:420px">${PLANE}</div>
  <div class="point abs h" style="left:654px;top:404px;width:226px"><img src="${A}/cat-point.png" style="width:100%;filter:drop-shadow(0 30px 40px rgba(0,0,0,.5))"></div>
  <div class="abs tgt" style="left:0;top:748px;width:1080px;text-align:center"><div class="h t1" style="font-size:80px;line-height:1">Telegram</div><div class="h t2" style="font-size:56px;color:var(--lime);margin-top:18px">@FourXtube</div></div>
  <div class="go h" style="top:960px"><span>Ссылка в профиле<div class="shim"></div></span></div>
  <div class="save h" style="top:1120px"><span><svg viewBox="0 0 24 24"><path d="M6 3h12v18l-6-4.500L6 21z"/></svg>Сохрани, чтобы не потерять</span></div>
</div>
`;

/** Заголовок сверху: слово встаёт, когда звучит. Одна таблица на все движки. */
// Фраза «Его собрал Клод Код. И пять бесплатных плагинов» держит два состояния: окно Claude Code
// и плитку с пятёркой. Вторая половина выделяется в свою сцену five.
const prep = (T) => {
  if (!T.scenes.five) {
    const cut = T.w.hook2[4] - 0.22;
    T.scenes.five = { s: cut, e: T.scenes.hook2.e };
    T.scenes.hook2 = { s: T.scenes.hook2.s, e: cut };
  }
  return T;
};

export const headlines = (T) => {
  prep(T);
  const w = (id, i) => T.w[id][i];
  const s = (id) => T.scenes[id].s;
  const e = (id) => T.scenes[id].e;
  const H = (id, light, l1, l2 = []) => ({ id, light, from: s(id), to: e(id), l1, l2 });
  return [
    // заголовок держится и на плитке с пятёркой: фраза одна, состояний два
    { ...H('hook2', false, [['Собрал', w('hook2', 1)]], [['Claude', w('hook2', 2), 'cl'], ['Code', w('hook2', 3), 'cl']]), to: e('five') },
    H('all', false, [['Делает', w('all', 5)], ['сам', w('all', 6)]]),
    H('hf', true, [['Веб-страница', w('hf', 2)]], [['→', w('hf', 6)], ['готовое', w('hf', 7)], ['видео', w('hf', 8)]]),
    H('rem', false, [['Видео', w('rem', 3)], ['кодом', w('rem', 4)]]),
    H('copy', true, [['Всё', w('copy', 3)], ['под', w('copy', 5)], ['копирку', w('copy', 6)]]),
    H('taste', true, [['Не', w('taste', 3)], ['рисует', w('taste', 4)]], [['по', w('taste', 5)], ['шаблону', w('taste', 6)]]),
    H('fix', false, [['Кривые', w('fix', 2)], ['отступы', w('fix', 3)]], [['→', w('fix', 6) - 0.12], ['ровно', w('fix', 6)]]),
    H('made', true, [['Делал', w('made', 1)], ['интерфейсы', w('made', 2)]], [['Vercel', w('made', 3)], ['и', w('made', 4)], ['Linear', w('made', 5)]]),
    H('teach', true, [['Учит', w('teach', 1)], ['Claude', w('teach', 2), 'cl']], [['движению', w('teach', 4)]]),
    H('rules', true, [['Три', s('rules') + 0.12], ['правила', s('rules') + 0.3]], [['движения', s('rules') + 0.52]]),
    H('final', false, [['От', w('final', 7)], ['первого', w('final', 8)], ['кадра', w('final', 9)]], [['до', w('final', 10)], ['субтитров', w('final', 11)]]),
  ];
};

/** Таймлайн сцен. tl — пустой таймлайн на паузе, root — блок с разметкой markup(). */
export const buildScenes = (gsap, tl, root, T) => {
  prep(T);
  const $ = (sel, from = root) => from.querySelector(sel);
  const $$ = (sel, from = root) => [...from.querySelectorAll(sel)];
  const s = (id) => T.scenes[id].s;
  const e = (id) => T.scenes[id].e;
  const w = (id, i) => T.w[id][i];
  const L = T.length;
  const REST = { x: 0, y: 0, scale: 1, rotation: 0, rotationY: 0, rotationX: 0, filter: 'blur(0px)' };
  // появление: из «откуда» в покой, прозрачность вместе со сдвигом
  const inn = (el, t, from = { y: 40 }, duration = 0.6, ease = 'power3.out') => {
    const to = { opacity: 1, duration, ease };
    Object.keys(from).forEach((k) => { to[k] = REST[k]; });
    return tl.fromTo(el, { opacity: 0, ...from }, to, t);
  };
  const out = (el, t, duration = 0.3) => tl.to(el, { opacity: 0, duration, ease: 'power2.in' }, t);
  const pop = (el, t) => { tl.set(el, { transformOrigin: '50% 50%' }, 0); return inn(el, t, { scale: 0.8, y: 16 }, 0.45, 'back.out(1.25)'); };
  const word = (el, t) => inn(el, t - 0.06, { y: 18, filter: 'blur(10px)' }, 0.34);
  const draw = (el, t, duration, ease = 'power2.inOut') => {
    const len = el.getTotalLength();
    return tl.fromTo(el, { strokeDasharray: len, strokeDashoffset: len }, { strokeDashoffset: 0, duration, ease }, t);
  };
  const count = (el, from, to, t, duration, ease = 'power2.out') =>
    tl.fromTo(el, { textContent: from }, { textContent: to, duration, ease, snap: { textContent: 1 } }, t);

  // Сцена входит перетеканием из размытия, но не одним приёмом на всё: показы приходят с разных
  // сторон и с разной скоростью, карточки плагинов — из глубины. Уходят все одинаково быстро.
  const ENTER = {
    five: [{ scale: 1.14 }, 0.42, 'expo.out'], all: [{ y: 90 }, 0.6, 'power3.out'],
    hf: [{ x: 110 }, 0.55, 'power4.out'], stars: [{ scale: 1.16 }, 0.7, 'expo.out'],
    rem: [{ x: -110 }, 0.55, 'power4.out'], free: [{ y: 100 }, 0.6, 'power3.out'],
    copy: [{ scale: 1.18 }, 0.6, 'expo.out'], taste: [{ scale: 0.94 }, 0.7, 'power2.out'],
    n24: [{ y: 110 }, 0.55, 'power4.out'], fix: [{ x: 110 }, 0.5, 'power3.out'],
    made: [{ x: -110 }, 0.55, 'power4.out'], teach: [{ y: 90 }, 0.55, 'power3.out'], rules: [{ x: 110 }, 0.5, 'power3.out'],
    final: [{ scale: 1.12 }, 0.7, 'expo.out'], proof: [{ scale: 0.9 }, 0.45, 'expo.out'], cta: [{ y: 100 }, 0.6, 'power3.out'],
  };
  const sweep = (el, t, duration = 1.1) => tl.fromTo(el, { '--sp': '-25%' }, { '--sp': '125%', duration, ease: 'power2.inOut' }, t);
  const SC = {};
  const order = ['hook', 'hook2', 'five', 'all', 'c1', 'hf', 'stars', 'c2', 'rem', 'free', 'c3', 'copy', 'taste', 'c4', 'n24', 'fix', 'c5', 'made', 'teach', 'rules', 'final', 'proof', 'cta'];
  order.forEach((id, n) => {
    const el = $('#sc-' + id);
    SC[id] = el;
    const end = id === 'cta' ? L : e(id);
    const [from, dur, ease] = ENTER[id] || [{ scale: 0.955 }, 0.5, 'power3.out'];
    const to = { opacity: 1, filter: 'blur(0px)', duration: dur, ease };
    Object.keys(from).forEach((k) => { to[k] = k === 'scale' ? 1 : 0; });
    if (n > 0) tl.fromTo(el, { opacity: 0, filter: 'blur(16px)', ...from }, to, s(id));
    if (id !== 'cta') tl.to(el, { opacity: 0, scale: 1.05, filter: 'blur(16px)', duration: 0.34, ease: 'power2.in' }, end - 0.24);
  });

  // Фон: тёмные и светлые группы сцен чередуются, как у референса.
  const light = [['c1', 'c2'], ['c3', 'c4'], ['c5', 'final']];
  const bgL = $('.bg-light');
  const gLime = $('.glow-lime'), gWarm = $('.glow-warm'), gMint = $('.glow-mint'), vig = $('.vignette');
  light.forEach(([a, b]) => {
    tl.to(bgL, { opacity: 1, duration: 0.45, ease: 'power2.out' }, s(a) - 0.1);
    tl.to(gMint, { opacity: 1, duration: 0.6 }, s(a));
    tl.to([gLime, vig], { opacity: 0, duration: 0.3 }, s(a) - 0.1);
    tl.to(bgL, { opacity: 0, duration: 0.45, ease: 'power2.out' }, s(b) - 0.1);
    tl.to(gMint, { opacity: 0, duration: 0.3 }, s(b) - 0.1);
    tl.to(vig, { opacity: 1, duration: 0.5 }, s(b));
    tl.to(b === 'final' ? gWarm : gLime, { opacity: 1, duration: 0.6 }, s(b));
  });
  tl.to(gWarm, { opacity: 0, duration: 0.4 }, s('cta') - 0.1);
  tl.to(gLime, { opacity: 1, duration: 0.6 }, s('cta'));
  // фон дышит: медленно, в пределах пяти процентов
  $$('.glow i').forEach((el, i) => tl.fromTo(el, { scale: 0.96 }, { scale: 1.05, duration: 3.2 + i * 0.5, ease: 'sine.inOut', yoyo: true, repeat: Math.max(0, Math.floor(L / (3.2 + i * 0.5)) - 1) }, 0));
  // пятно света съезжает к герою сцены
  [['stars', 690], ['c2', 760], ['n24', 640], ['fix', 760], ['made', 800], ['teach', 760]].forEach(([id, y]) =>
    tl.to([gLime, gMint], { y: y - 760, duration: 0.8, ease: 'power2.inOut' }, s(id)));

  // Ряд значков: значки встают по одному, текущий получает кольцо.
  const chipsIn = (sc, t, on = -1) => {
    const list = $$('.chip', sc);
    list.forEach((c, i) => inn(c, t + i * 0.06, { y: 26, scale: 0.85 }, 0.42, 'power3.out'));
    if (on >= 0) {
      tl.to($('u', list[on]), { opacity: 1, duration: 0.3 }, t + 0.5);
      tl.to(list[on], { scale: 1.14, duration: 0.4, ease: 'power3.out' }, t + 0.5);
      list.forEach((c, i) => i !== on && tl.to(c, { opacity: 0.42, duration: 0.3 }, t + 0.5));
    }
  };
  const waveRun = (sc, a, b) => tl.fromTo($('.wave b', sc), { x: 40 }, { x: 660, duration: b - a, ease: 'none' }, a);

  // 1. Крючок: три строки бьют по словам голоса. На нулевом кадре надпись уже читается.
  {
    const sc = SC.hook;
    tl.fromTo($('.floats', sc), { scale: 1.14 }, { scale: 1, duration: e('hook'), ease: 'power1.out' }, 0);
    [['.k1', w('hook', 0)], ['.k2', w('hook', 2)], ['.k3', w('hook', 4)]].forEach(([k, at]) =>
      tl.fromTo($(k, sc), { opacity: 0.3, scale: 1.06, filter: 'blur(5px)' }, { opacity: 1, scale: 1, filter: 'blur(0px)', duration: 0.24, ease: 'expo.out' }, Math.max(0.06, at - 0.05)));
    tl.fromTo($('.peek', sc), { opacity: 0, y: 140, rotation: 8 }, { opacity: 1, y: 0, rotation: 0, duration: 0.6, ease: 'power3.out' }, 0.4);
  }

  // Плитка с пятёркой: число досчитывает, слова подписи встают, по стеклу проходит блик.
  {
    const sc = SC.five, t = s('five');
    tl.fromTo($('.tile', sc), { scale: 0.8, rotation: -6 }, { scale: 1, rotation: 0, duration: 0.6, ease: 'expo.out' }, t);
    count($('.num', sc), 1, 5, t + 0.05, 0.45, 'power1.out');
    sweep($('.tile', sc), t + 0.5);
    $$('.cap span', sc).forEach((el, i) => word(el, w('hook2', 6 + i)));
    chipsIn(sc, t + 0.35);
  }

  // 2. Окно Claude Code: промпт набирается, полоса идёт, дорожка заполняется.
  {
    const sc = SC.hook2, t = s('hook2'), end = e('hook2');
    inn($('.win', sc), t + 0.05, { y: 50, scale: 0.94 }, 0.6);
    $$('.ch', sc).forEach((c, i) => tl.set(c, { opacity: 1 }, t + 0.3 + i * 0.045));
    
    chipsIn(sc, w('hook2', 2) - 0.1);
    tl.fromTo($('.track i', sc), { scaleX: 0 }, { scaleX: 1, duration: end - t - 0.35, ease: 'none' }, t + 0.3);
    inn($('.tline', sc), t + 0.3, { y: 60 }, 0.6);
    inn($('.head', sc), t + 0.5, { y: 20 }, 0.3);
    tl.fromTo($('.head', sc), { x: 40 }, { x: 740, duration: Math.max(0.4, end - t - 0.6), ease: 'none' }, t + 0.5);
    $$('.tline .cell', sc).forEach((c, i) => inn(c, t + 0.5 + i * Math.max(0.05, (end - t - 0.8) / 5), { scale: 0.8 }, 0.3));
  }

  // 3. Три телефона веером: слово звучит, его плашка загорается.
  {
    const sc = SC.all, t = s('all');
    inn($('.ph-c', sc), t + 0.05, { y: 70, scale: 0.92 }, 0.65);
    inn($('.ph-l', sc), t + 0.18, { x: 130 }, 0.7);
    inn($('.ph-r', sc), t + 0.18, { x: -130 }, 0.7);
    const labels = $$('.labels span', sc);
    [0, 1, 3].forEach((wi, i) => {
      const at = w('all', wi) - 0.05, next = i < 2 ? w('all', [1, 3][i]) - 0.05 : w('all', 4) + 0.1;
      tl.fromTo(labels[i], { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.25, ease: 'power3.out' }, at);
      tl.fromTo($('u', labels[i]), { opacity: 0 }, { opacity: 1, duration: 0.12 }, at);
      tl.fromTo($('b', labels[i]), { color: '#12130F' }, { color: '#F1F2EA', duration: 0.2 }, next);
      tl.to($('u', labels[i]), { opacity: 0, duration: 0.2 }, next);
    });
    pop($('.orb', sc), w('all', 6));
    waveRun(sc, t, e('all'));
  }

  // Карточка плагина: окно репозитория встаёт из наклона, имя приходит на слове.
  PLUGINS.forEach((p, i) => {
    const sc = SC[p.id], t = s(p.id);
    tl.fromTo($('.codebg', sc), { y: 34 }, { y: -34, duration: e(p.id) - t, ease: 'none' }, t);
    inn($('.repo', sc), t + 0.05, { rotationY: -26, x: -90, scale: 0.9 }, 0.75);
    word($('.name', sc), Math.min(w(p.id, 1), t + 0.9));
    pop($('.stars', sc), Math.min(w(p.id, 1), t + 0.9) + 0.32);
    chipsIn(sc, t + 0.3, i);
    sweep($('.repo', sc), t + 0.75, 0.9);
  });

  // HyperFrames: страница с кодом уезжает в бок, из неё получается ролик и плёнка кадров.
  {
    const sc = SC.hf, t = s('hf'), go = w('hf', 4) - 0.15;
    inn($('.paper', sc), t + 0.05, { y: 60, scale: 0.92 }, 0.6);
    tl.to($('.paper', sc), { x: -330, rotationY: 40, scale: 0.8, duration: 0.85, ease: 'power3.inOut' }, go);
    inn($('.player', sc), go + 0.15, { scale: 0.72, y: 60 }, 0.7);
    pop($('.player .pill', sc), w('hf', 6));
    tl.fromTo($('.player .track i', sc), { scaleX: 0 }, { scaleX: 1, duration: e('hf') - w('hf', 6), ease: 'none' }, w('hf', 6));
    inn($('.strip', sc), go + 0.3, { y: 120 }, 0.7);
    $$('.strip .cell', sc).forEach((c, k) => inn(c, w('hf', 6) + k * 0.13, { scale: 0.7 }, 0.3));
  }

  // Звёзды: число досчитывает до 55, за ним «тыс.» и подпись по словам.
  {
    const sc = SC.stars, t = s('stars');
    inn($('.ghmark', sc), t, { scale: 1.16 }, 1.4, 'power2.out');
    count($('.cnt', sc), 12, 55, t + 0.1, 0.85);
    tl.fromTo($('.big', sc), { scale: 0.86 }, { scale: 1, duration: 0.9, ease: 'power3.out' }, t + 0.1);
    word($('.tys', sc), w('stars', 2));
    pop($('.star.top', sc), t + 0.25);
    $$('.cap span', sc).forEach((el, k) => word(el, w('stars', 3 + k)));
    $$('.tw', sc).forEach((el, k) => tl.fromTo(el, { opacity: 0, scale: 0.3, rotation: -40 }, { opacity: 0.5, scale: 1, rotation: 0, duration: 0.5, ease: 'back.out(1.2)' }, t + 0.2 + k * 0.07));
    draw($('.lnA', sc), t + 0.4, 1.5);
    $$('.dot', sc).forEach((el, k) => pop(el, t + 0.8 + k * 0.35));
  }

  // Remotion: кадры считаются, субтитры и карта встают на своих словах, потом рендер.
  {
    const sc = SC.rem, t = s('rem'), end = e('rem');
    inn($('.shot', sc), t + 0.05, { y: 60, scale: 0.92 }, 0.6);
    tl.fromTo($('.tsx', sc), { opacity: 0, x: -140, rotationY: 34 }, { opacity: 1, x: 0, rotationY: 34, duration: 0.7, ease: 'power3.out' }, t + 0.2);
    tl.fromTo($('.map', sc), { opacity: 0, x: 140, rotationY: -34 }, { opacity: 1, x: 0, rotationY: -34, duration: 0.7, ease: 'power3.out' }, t + 0.2);
    count($('.fr', sc), 520, 520 + Math.round((end - t) * 30), t, end - t, 'none');
    pop($('.caps .tag', sc), w('rem', 5));
    word($$('.caps span', sc)[1], w('rem', 6));
    draw($('.route', sc), w('rem', 6), 1.1);
    pop($('.pin', sc), w('rem', 6));
    const r = w('rem', 8) - 0.1;
    inn($('.rbar', sc), r, { y: -30 }, 0.4);
    tl.fromTo($('.rbar .fill', sc), { clipPath: 'inset(0% 100% 0% 0% round 46px)' }, { clipPath: 'inset(0% 0% 0% 0% round 46px)', duration: end - r - 0.35, ease: 'power1.inOut' }, r + 0.1);
    $$('.pc', sc).forEach((el) => count(el, 0, 100, r + 0.1, end - r - 0.35, 'power1.inOut'));
    waveRun(sc, t, end);
  }

  // Бесплатно: плёнка едет по диагонали, на стекле трое и главное слово.
  {
    const sc = SC.free, t = s('free');
    tl.fromTo($('.roll', sc), { x: -260 }, { x: 0, duration: e('free') - t, ease: 'none' }, t);
    inn($('.panel', sc), t + 0.05, { y: 60, scale: 0.93 }, 0.6);
    $$('.users i', sc).forEach((el, k) => pop(el, t + 0.3 + k * 0.12));
    $$('.frees span', sc).forEach((el, k) => word(el, w('free', 2 + k)));
    inn($('.freeb', sc), w('free', 5) - 0.08, { scale: 1.3, filter: 'blur(14px)' }, 0.32, 'expo.out');
    // конфетти на главном слове: разлёт и падение, направления посчитаны по зерну
    $$('.cf', sc).forEach((p, i) => {
      const a = rnd(i + 5) * Math.PI * 2, r = 220 + rnd(i + 31) * 320, at = w('free', 5) - 0.02;
      tl.fromTo(p, { opacity: 0, x: 0, y: 0, rotation: 0, scale: 0.5 }, { opacity: 1, x: Math.cos(a) * r, y: Math.sin(a) * r * 0.8 - 120, rotation: 200 + i * 40, scale: 1, duration: 0.5, ease: 'power3.out' }, at);
      tl.to(p, { y: Math.sin(a) * r * 0.8 + 260, opacity: 0, rotation: 420 + i * 40, duration: 0.75, ease: 'power1.in' }, at + 0.5);
    });
  }

  // Под копирку: сетка одинаковых карточек плывёт, лупа идёт по ней.
  {
    const sc = SC.copy, t = s('copy'), end = e('copy');
    tl.fromTo($('.mover', sc), { x: 70, y: 50 }, { x: -70, y: -50, duration: end - t, ease: 'none' }, t);
    const lens = $('.lens', sc);
    tl.fromTo(lens, { opacity: 0, scale: 0.5, x: 120, y: 640 }, { opacity: 1, scale: 1, x: 150, y: 660, duration: 0.5, ease: 'back.out(1.2)' }, t + 0.35);
    tl.to(lens, { x: 560, y: 790, duration: (end - t - 1) * 0.55, ease: 'power2.inOut' }, t + 0.85);
    tl.to(lens, { x: 350, y: 620, duration: (end - t - 1) * 0.45, ease: 'power2.inOut' }, t + 0.85 + (end - t - 1) * 0.55);
  }

  // Не по шаблону: сетка уходит в размытие, на её место встаёт собранная страница.
  {
    const sc = SC.taste, t = s('taste');
    tl.fromTo($('.mover', sc), { x: -70, y: -50 }, { x: -110, y: -80, duration: e('taste') - t, ease: 'none' }, t);
    inn($('.site', sc), t + 0.15, { y: 110, scale: 0.9 }, 0.75);
    inn($('.back', sc), t + 0.45, { x: 120 }, 0.7);
    $$('.thumbs img', sc).forEach((el, k) => inn(el, t + 0.6 + k * 0.1, { y: 30 }, 0.4));
    pop($('.anti', sc), w('taste', 5));
  }

  // 24 команды: число досчитывает, вокруг кольцо команд, подсветка идёт по списку.
  {
    const sc = SC.n24, t = s('n24'), end = e('n24');
    word($('.lbl', sc), t + 0.15);
    count($('.cnt', sc), 1, 24, t + 0.05, 0.8);
    tl.fromTo($('.big', sc), { scale: 0.82 }, { scale: 1, duration: 0.85, ease: 'power3.out' }, t + 0.05);
    tl.fromTo($('.ring', sc), { opacity: 0, scale: 0.72, rotation: -10 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.9, ease: 'power3.out' }, t + 0.25);
    tl.to($('.ring', sc), { rotation: 5, duration: end - t - 1.15, ease: 'none' }, t + 1.15);
    $$('.cap span', sc).filter((el) => !el.classList.contains('lbl')).forEach((el, k) => word(el, w('n24', 2 + k)));
    inn($('.list', sc), w('n24', 2) + 0.15, { y: 50 }, 0.5);
    const rows = $$('.list u', sc), step = Math.max(0.42, (end - w('n24', 2) - 0.7) / 3);
    rows.forEach((u, k) => {
      const a = w('n24', 2) + 0.4 + k * step;
      tl.to(u, { opacity: 1, duration: 0.14 }, a);
      if (k < rows.length - 1) tl.to(u, { opacity: 0, duration: 0.14 }, a + step);
    });
  }

  // Кривые отступы: рамки находят ошибки, шторка проходит и оставляет ровное.
  {
    const sc = SC.fix, t = s('fix'), end = e('fix');
    inn($('.wf.bad', sc), t + 0.05, { y: 60, scale: 0.93 }, 0.6);
    const cmd = $$('.cmd', sc), fixAt = w('fix', 5) - 0.05;
    pop(cmd[0], w('fix', 0));
    out(cmd[0], w('fix', 2) - 0.1, 0.15); pop(cmd[1], w('fix', 2));
    out(cmd[1], fixAt, 0.15); pop(cmd[2], fixAt + 0.1);
    [['.m1', w('fix', 1)], ['.m2', w('fix', 2)], ['.m3', w('fix', 3)]].forEach(([m, at]) => {
      inn($(m, sc), at, { scale: 1.12 }, 0.4, 'back.out(1.2)');
      out($(m, sc), fixAt + 0.25, 0.3);
    });
    tl.set($('.wf.good', sc), { clipPath: 'inset(0% 100% 0% 0% round 36px)' }, 0);
    tl.to($('.wf.good', sc), { clipPath: 'inset(0% 0% 0% 0% round 36px)', duration: 0.9, ease: 'power2.inOut' }, fixAt);
    tl.fromTo($('.wipe', sc), { opacity: 0, x: 0 }, { opacity: 1, x: 0, duration: 0.1 }, fixAt - 0.05);
    tl.to($('.wipe', sc), { x: 698, duration: 0.9, ease: 'power2.inOut' }, fixAt);
    out($('.wipe', sc), fixAt + 0.9, 0.2);
    $$('.slots i', sc).forEach((el, k) => tl.fromTo(el, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power3.out' }, t + 0.4 + k * 0.06));
    void end;
  }

  // Vercel и Linear: знаки встают на своих словах.
  {
    const sc = SC.made, t = s('made');
    inn($('.tst', sc), t + 0.2, { x: 120 }, 0.6);
    tl.fromTo($('.vercel', sc), { opacity: 0, scale: 0.55, rotation: -28 }, { opacity: 1, scale: 1, rotation: -6, duration: 0.6, ease: 'back.out(1.2)' }, w('made', 3) - 0.1);
    tl.fromTo($('.linear', sc), { opacity: 0, scale: 0.55, rotation: 40 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.6, ease: 'back.out(1.2)' }, w('made', 5) - 0.1);
    inn($('.sheet', sc), t + 0.4, { y: 160 }, 0.7);
  }

  // Движение: верхняя шайба едет рывком, нижняя плавно, след показывает разницу.
  {
    const sc = SC.teach, t = s('teach'), go = w('teach', 1), dur = Math.max(1.1, e('teach') - go - 0.5);
    [0, 1].forEach((n) => {
      inn($('.l' + n, sc), t + 0.1 + n * 0.12, { y: 40 }, 0.5);
      pop($('.lab' + n, sc), t + 0.35 + n * 0.12);
      tl.fromTo($('.l' + n + ' b', sc), { x: 0 }, { x: 584, duration: dur, ease: n ? 'power2.inOut' : 'steps(5)' }, go);
      $$('.l' + n + ' i', sc).forEach((dot, k) => {
        // точки стоят там, где шайба бывает через равные доли времени: у плавной они сгущаются к краям
        tl.set(dot, { opacity: 1 }, go + (k / 5) * dur);
      });
    });
    inn($('.curve', sc), t + 0.5, { y: 80 }, 0.6);
    draw($('.ease', sc), go, dur, 'power2.inOut');
    pop($('.end', sc), go + dur - 0.1);
  }

  // Три правила: строка встаёт на своём слове, галочка рисуется следом.
  {
    const sc = SC.rules, t = s('rules');
    inn($('.ec', sc), t + 0.15, { x: 160 }, 0.7);
    draw($('.arc', sc), t + 0.2, 1.2);
    $$('.rule', sc).forEach((el, k) => {
      const at = w('rules', k) - 0.08;
      inn(el, at, { x: -70, scale: 0.95 }, 0.5);
      draw($('.ck', el), at + 0.2, 0.35, 'power2.out');
    });
  }

  // Итог: плёнка из пяти плагинов идёт под иглой, кот ведёт ролик.
  {
    const sc = SC.final, t = s('final'), end = e('final');
    tl.fromTo($('.reel', sc), { x: 260 }, { x: -640, duration: end - t + 0.3, ease: 'none' }, t);
    inn($('.needle', sc), t + 0.3, { y: -60 }, 0.5);
    chipsIn(sc, w('final', 1) - 0.1);
    waveRun(sc, t, end);
  }

  // Доказательство: за сколько секунд посчитан сам ролик. Число настоящее, см. README.
  {
    const sc = SC.proof, t = s('proof'), to = w('proof', 5) + 0.25;
    word($('.plbl', sc), t + 0.2);
    count($('.cnt', sc), 0, RENDER_SECONDS, t + 0.25, to - t - 0.25, 'power2.out');
    tl.fromTo($('.pnum', sc), { scale: 0.8 }, { scale: 1, duration: to - t, ease: 'power3.out' }, t);
    tl.to($('.pnum', sc), { scale: 1.08, duration: 0.14, ease: 'power2.out', yoyo: true, repeat: 1 }, to);
    word($('.psec', sc), w('proof', 6));
    tl.fromTo($('.rbar .fill', sc), { clipPath: 'inset(0% 100% 0% 0% round 46px)' }, { clipPath: 'inset(0% 0% 0% 0% round 46px)', duration: to - t - 0.25, ease: 'power2.out' }, t + 0.25);
    $$('.pc', sc).forEach((el) => count(el, 0, 100, t + 0.25, to - t - 0.25, 'power2.out'));
  }

  // Призыв: что лежит в канале, потом знак Telegram, кот показывает на него. В конце «сохрани».
  {
    const sc = SC.cta, tg = w('cta', 5) - 0.25;
    pop($('.ibox', sc), s('cta') + 0.15);
    word($('.ctat', sc), w('cta', 1));
    inn($('.r1', sc), w('cta', 2) - 0.05, { x: -80 }, 0.4);
    inn($('.r2', sc), w('cta', 3) - 0.05, { x: 80 }, 0.4);
    tl.to($('.first', sc), { opacity: 0, y: -70, filter: 'blur(14px)', duration: 0.3, ease: 'power2.in' }, tg - 0.2);
    tl.fromTo($('.tg', sc), { opacity: 0, x: -420, y: 260, rotation: -160, scale: 0.6 }, { opacity: 1, x: 0, y: 0, rotation: 0, scale: 1, duration: 0.8, ease: 'expo.out' }, tg);
    word($('.t1', sc), w('cta', 6));
    word($('.t2', sc), w('cta', 6) + 0.3);
    inn($('.point', sc), w('cta', 6), { x: 160 }, 0.5, 'power3.out');
    inn($('.go', sc), w('link', 0) - 0.1, { y: 40, scale: 0.9 }, 0.45, 'back.out(1.2)');
    sweep($('.go span', sc), w('link', 0) + 0.3, 0.9);
    inn($('.save', sc), w('link', 3) - 0.1, { y: 40, scale: 0.9 }, 0.45, 'back.out(1.2)');
    tl.to($('.save span', sc), { scale: 1.06, duration: 0.45, ease: 'sine.inOut', yoyo: true, repeat: 1 }, w('link', 3) + 0.5);
  }
  return tl;
};

/** Слой поверх сцен: знак канала, полоса «какой плагин из пяти», заголовки, субтитры, зерно, вспышка. */
export const overlayMarkup = (A, T) => {
  prep(T);
  const lines = new Map();
  T.caps.forEach((c) => lines.set(c.line, [...(lines.get(c.line) || []), c]));
  return `<div class="logo"><img src="${A}/logo.png"></div>
<div class="prog h">${PLUGINS.map(() => '<i><b></b></i>').join('')}</div>
` + headlines(T).map((h) => `<div class="hl ${h.light ? 'light' : ''}">${[h.l1, h.l2].map((line, k) => line.length ? `<div class="${k ? 'l2' : 'l1'}">${
    line.map(([txt, , cls]) => `<span class="${cls || ''}">${txt}</span>`).join('')}</div>` : '').join('')}</div>`).join('') + `
<div class="ccs">${[...lines.values()].map((ws) => `<div class="cc"><p>${ws.map((c) => `<span>${c.w}</span>`).join(' ')}</p></div>`).join('')}</div>
<div class="flash" data-layout-ignore></div>
<div class="grain" data-layout-ignore><i></i></div>`;
};

export const buildOverlay = (gsap, tl, root, T) => {
  prep(T);
  const s = (id) => T.scenes[id].s;
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

  // Полоса плагинов: отрезок заполняется, пока идёт блок своего плагина. Цвет следует за светом сцены.
  const prog = root.querySelector('.prog');
  const marks = ['c1', 'c2', 'c3', 'c4', 'c5', 'final'];
  tl.fromTo(prog, { opacity: 0 }, { opacity: 1, duration: 0.4 }, s('c1'));
  [...prog.querySelectorAll('b')].forEach((b, i) =>
    tl.fromTo(b, { scaleX: 0 }, { scaleX: 1, duration: s(marks[i + 1]) - s(marks[i]), ease: 'none' }, s(marks[i])));
  marks.forEach((id, i) => {
    const light = i % 2 === 0 && id !== 'final';
    tl.set(prog, { '--pf': light ? '#56690C' : '#C7E24B', '--pt': light ? 'rgba(18,19,15,.16)' : 'rgba(241,242,234,.2)' }, s(id));
    // вспышка на смене света: короткий удар вместо ещё одного перетекания
    tl.fromTo(root.querySelector('.flash'), { opacity: 0 }, { opacity: 0.34, duration: 0.07, ease: 'power1.out' }, s(id) - 0.02);
    tl.to(root.querySelector('.flash'), { opacity: 0, duration: 0.34, ease: 'power2.out' }, s(id) + 0.05);
  });
  return tl;
};
