// Ролик «5 бесплатных сайтов для монтажа» (r12). Движок один: HyperFrames.
//
// Рерайт рилса @chingizkhan_yt (instagram.com/reel/Dd-8Bk5x_He), разбор — ../РЕФЕРЕНС.md. Каркас,
// порядок сцен, свет и приёмы автора: монтажный стол в крючке, пустой телефон «материалы нужны»,
// пятёрка с вкладками, по сайту — телефон или ноутбук со страницей и один показ, сундук в финале.
// Наше: графит, крем, лайм, олива; Unbounded для крупного, Onest для остального; кот; знак канала;
// субтитры по словам; полоса хода с первой смены кадра до конца; «перешли другу» и «сохрани».
//
// В кадре настоящие вещи каждого сайта: снимки страниц (Style/подборка-сайтов/снять.mjs), иконки
// Phosphor из его пакета, анимации с LottieFiles (их перематывает адаптер HyperFrames), цвет кадра
// пропущен через настоящую таблицу LUT. Данные — shared/data.js (собирает ../data-build.mjs).
//
// Тезис: состояние — одна фраза голоса, движется то, о чём говорят. Из «Приёмов на пробу» памятки:
// одна форма без склеек (телефон крючка пустеет, а не сменяется; кадр в сцене цвета один на две
// фразы), курсор как причина (тумблеры, выбор цвета, перетаскивание файла, кнопка «Отправить»),
// жизнь в паузе (бегунок, прокрутка страницы, дыхание свечения). Без конфетти и вспышки на смене
// света: README велел попробовать без них. Без зерна.
// Всё записано твинами без обратных вызовов: перемотка в любую секунду даёт верный кадр.

export const SITES = [
  { id: 'c1', name: 'Mixkit', n: 1, logo: 'mixkit-icon.png' },
  { id: 'c2', name: 'FreshLUTs', n: 2, logo: 'freshluts-icon.png' },
  { id: 'c3', name: 'LottieFiles', n: 3, logo: 'lottiefiles.png' },
  { id: 'c4', name: 'Phosphor', n: 4, logo: 'phosphor.png' },
  { id: 'c5', name: 'React Bits', n: 5, logo: 'reactbits.png' },
];

const rnd = (seed) => { const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const ic = (name, cls = '', set = 'r') => `<svg class="ic ${cls}" viewBox="0 0 256 256" fill="currentColor">${(set === 'b' ? BOLD : ICONS)[name]}</svg>`;
const CLAUDE = '<svg viewBox="0 0 24 24"><path d="M12 1.5l1.6 7.1 6.4-3.6-3.6 6.4 7.1 1.6-7.1 1.6 3.6 6.4-6.4-3.6L12 22.5l-1.6-7.1-6.4 3.6 3.6-6.4L.5 12l7.1-1.6L4 4l6.4 3.6z"/></svg>';
const CURSOR = '<svg class="cur" viewBox="0 0 32 32"><path d="M5 3l20 12.5-8.6 1.8 5 9.4-3.7 2-5-9.4L6.5 26z" fill="#F1F2EA" stroke="#12130F" stroke-width="1.8" stroke-linejoin="round"/></svg>';

// Пять значков сайтов в ряд: текущий получает кольцо (как вкладки у автора).
const chips = (A, top, extra = '') => `<div class="chips ${extra}" style="top:${top}px">${SITES.map((p) =>
  `<div class="chip h"><img src="${A}/${p.logo}"><u></u></div>`).join('')}</div>`;
const wave = (top, n = 58, color = '') => `<div class="wave" style="top:${top}px">${Array.from({ length: n }, (_, i) =>
  `<i style="height:${Math.round(10 + 64 * rnd(i + 3) * (0.35 + 0.65 * Math.abs(Math.sin(i * 0.4))))}px;${color ? `background:${color}` : ''}"></i>`).join('')}<b></b></div>`;
const num = (n) => `<div class="num-pill h"><b>${n}</b> / 5</div>`;

// Монтажный стол из крючка и из сцены «отдал Claude»: дорожки, волна, бегунок.
const editor = (A, id, clips, shown = false) => `<div class="editor glass ${shown ? '' : 'h'}" id="${id}">
  <div class="ebar">${ic('play', 'eic')}<span class="tc mono">00:00:00:<b class="fr">14</b></span>${ic('scissors', 'eic')}</div>
  <div class="trk v">${clips.map((c) => `<div class="clip ${c.cls || ''}" style="width:${c.w}px">${c.img ? `<img src="${A}/${c.img}">` : ''}<span>${c.t || ''}</span></div>`).join('')}</div>
  <div class="trk v2"><div class="clip" style="width:300px"><img src="${A}/g0.jpg"></div><div class="clip" style="width:180px"><img src="${A}/rezhisser.jpg"></div><div class="clip" style="width:190px"><img src="${A}/g3.jpg"></div></div>
  <div class="trk a">${Array.from({ length: 64 }, (_, i) => `<i style="height:${Math.round(14 + 50 * rnd(i + 70) * (0.4 + 0.6 * Math.abs(Math.sin(i * 0.33))))}px"></i>`).join('')}</div>
  <div class="head"><b></b><i></i></div>
</div>`;

const GRID = ['video-camera', 'music-note', 'film-strip', 'waveform', 'speaker-high', 'image', 'camera', 'sparkle', 'star', 'heart',
  'check-circle', 'arrow-bend-up-right', 'smiley', 'paper-plane-tilt', 'play', 'scissors', 'magic-wand', 'palette', 'sun', 'moon',
  'lightning', 'rocket', 'bell', 'gift', 'cat', 'folder', 'download-simple', 'cloud', 'gear', 'pencil-simple', 'eye', 'fire',
  'crown', 'trophy', 'map-pin', 'chat-circle', 'music-notes', 'headphones', 'microphone', 'film-slate', 'cursor-click', 'lightbulb',
  'aperture', 'monitor-play', 'film-reel'];

/** Разметка всех сцен. A — адрес папки с картинками. */
export const markup = (A) => `
<script src="${A}/lottie_light.min.js"><\/script>
<div class="bg bg-light"></div>
<div class="glow glow-lime" data-layout-ignore style="opacity:1"><i></i></div><div class="glow glow-warm" data-layout-ignore><i></i></div><div class="glow glow-mint" data-layout-ignore><i></i></div>
<div class="vignette" style="opacity:1"></div>

<div class="sc" id="sc-hook" style="opacity:1">
  <div class="floats abs" data-layout-ignore style="inset:0">
    <div class="float" style="left:-120px;top:150px;width:420px;height:270px;transform:rotate(-8deg)"><img src="${A}/rezhisser.jpg"></div>
    <div class="float" style="left:800px;top:120px;width:420px;height:260px;transform:rotate(7deg)"><img src="${A}/mixkit-pc.jpg" style="object-position:0 0"></div>
    <div class="float" style="left:-100px;top:1250px;width:440px;height:300px;transform:rotate(9deg)"><img src="${A}/g3.jpg"></div>
    <div class="float" style="left:760px;top:1240px;width:440px;height:300px;transform:rotate(-8deg)"><img src="${A}/reactbits-pc.jpg" style="object-position:0 0"></div>
  </div>
  <div class="abs" data-layout-ignore style="inset:0;background:radial-gradient(ellipse 72% 40% at 50% 38%,rgba(10,11,8,.86),rgba(10,11,8,0))"></div>
  <div class="kt"><div class="k1">Монтажёры</div><div class="k2">меня</div><div class="k3">возненавидят</div></div>
  ${editor(A, 'ed1', [{ w: 150, img: 'r11-1.5.jpg' }, { w: 210, img: 'g1.jpg' }, { w: 140, img: 'r11-14.jpg' }, { w: 170, img: 'mixkit-ph.jpg' }], true)}
  <div class="abs h laptopcat" style="left:40px;top:1050px;width:240px"><img src="${A}/cat-laptop.png" style="width:100%"></div>
</div>

<div class="sc" id="sc-hook2">
  <div class="cpill pill h"><s>${CLAUDE}</s>Claude Code</div>
  <div class="kbd abs h" data-layout-ignore><div class="keys">${'<i></i>'.repeat(36)}</div></div>
  <div class="ph1 abs h" style="left:370px;top:560px"><div class="phone">
    <img class="scr" src="${A}/r11-1.5.jpg">
    <div class="empty abs"></div>
    <div class="rend abs"><i></i></div>
  </div></div>
  ${[['film-strip', 120, 640, -8], ['music-note', 800, 600, 7], ['image', 150, 960, 6], ['sparkle', 790, 930, -6]].map(([n, x, y, r]) =>
    `<div class="slot abs h" style="left:${x}px;top:${y}px"><div style="transform:rotate(${r}deg)" class="slotin">${ic(n, '', 'r')}</div></div>`).join('')}
</div>

<div class="sc" id="sc-five">
  <div class="tile"><span class="num">1</span><div class="shim"></div></div>
  <div class="cap" style="top:806px"><span class="h">бесплатных</span> <span class="h">сайтов</span></div>
  ${chips(A, 950)}
  <div class="brw abs h" style="left:150px;top:1070px;width:780px"><div class="bar"><i></i><i></i><i></i><div class="url">mixkit.co</div></div>
    <div class="brwimg"><img src="${A}/mixkit-pc.jpg"></div></div>
</div>

<div class="sc light" id="sc-c1">
  ${num(1)}
  <div class="floats abs" data-layout-ignore style="inset:0">
    <div class="float lf" style="left:-70px;top:600px;width:300px;height:200px"><img src="${A}/g1.jpg"></div>
    <div class="float lf" style="left:830px;top:520px;width:300px;height:190px"><img src="${A}/rezhisser.jpg"></div>
    <div class="float lf" style="left:820px;top:960px;width:290px;height:190px"><img src="${A}/g3.jpg"></div>
    <div class="float lf" style="left:-60px;top:1000px;width:280px;height:180px"><img src="${A}/r11-34.jpg"></div>
  </div>
  <div class="ph2 abs h" style="left:370px;top:470px"><div class="phone white"><img class="scroll" src="${A}/mixkit-ph.jpg" style="height:auto;object-fit:initial"></div></div>
  ${wave(1240, 58, 'rgba(86,105,12,.55)')}
</div>

<div class="sc light" id="sc-mix">
  <div class="player glass h" style="left:150px;top:520px;width:780px">
    <div class="pl-top"><div class="play">${ic('play', '', 'b')}</div><div class="pl-t"><b>Ocean Breeze</b><small>Mixkit · Stock Music</small></div></div>
    ${wave(150, 52, '')}
  </div>
  <div class="stat s1 pill h" style="left:150px;top:840px">${ic('music-note', '', 'b')}<span><b class="cnt">0</b>+</span>треков</div>
  <div class="stat s2 pill h" style="left:560px;top:840px">${ic('waveform', '', 'b')}<span><b class="cnt">0</b>+</span>звуков</div>
  <div class="abs" style="left:-80px;top:950px;width:1240px"><div style="transform:rotate(-3deg)"><div class="film strip h" data-layout-ignore style="height:200px">${
    ['g0.jpg', 'rezhisser.jpg', 'g3.jpg', 'r11-14.jpg', 'g1.jpg', 'montazh.jpg', 'g2.jpg', 'r11-34.jpg'].map((f) => `<div class="cell" style="width:240px"><img src="${A}/${f}" style="width:100%;height:100%;object-fit:cover;border-radius:0"></div>`).join('')}</div></div></div>
  <div class="stat s3 pill h" style="left:300px;top:1215px">${ic('film-strip', '', 'b')}<span><b class="cnt">0</b>+</span>видео</div>
</div>

<div class="sc light" id="sc-mix2">
  <div class="bezel abs h" style="left:150px;top:540px;width:780px">
    <div class="core">
      <img class="mlogo" src="${A}/mixkit.png">
      <div class="trow t1">${ic('cursor-click', 'ti')}<span>Коммерция</span><div class="tog"><i></i></div></div>
      <div class="trow t2">${ic('user', 'ti')}<span>Без указания автора</span><div class="tog"><i></i></div></div>
    </div>
  </div>
  <div class="ftypes">${['file-video', 'file-audio', 'waveform', 'film-slate', 'music-note'].map((n) => `<div class="ft h">${ic(n, '', 'b')}</div>`).join('')}</div>
  <div class="cursor abs h" style="left:0;top:0">${CURSOR}</div>
</div>

<div class="sc" id="sc-c2">
  ${num(2)}
  <div class="logoplate abs h" style="left:340px;top:470px"><img src="${A}/freshluts.png"></div>
  <div class="laptop abs h" style="left:110px;top:620px"><div class="lscr"><img src="${A}/freshluts-pc.jpg"></div><div class="lbase"></div></div>
  <div class="swatches">${[0, 1, 2, 3, 4].map((k) => `<div class="sw h"><img src="${A}/g${k}.jpg"></div>`).join('')}</div>
  <div class="dl pill h" style="left:330px;top:1270px">${ic('download-simple', '', 'b')}3 млн скачиваний</div>
</div>

<div class="sc" id="sc-luts">
  <div class="photo abs h" style="left:110px;top:500px;width:860px;height:573px">
    ${[0, 1, 2, 4, 3].map((k) => `<img class="gr g${k}" src="${A}/g${k}.jpg">`).join('')}
    <div class="split abs"><img src="${A}/g3.jpg"></div>
    <div class="sline abs"></div>
    <div class="curve glass abs"><svg viewBox="0 0 200 130"><path class="cv" d="M14 116 C 70 116, 90 30, 186 14" fill="none" stroke="#D97757" stroke-width="5" stroke-linecap="round"/><circle class="cvd" cx="104" cy="58" r="7" fill="#F1F2EA"/></svg></div>
  </div>
  <div class="lname pill h"><s>${ic('palette', '', 'b')}</s><b class="ln0">Original</b><b class="ln1">Vintage</b><b class="ln2">Cross</b><b class="ln4">Noir</b><b class="ln3">Teal &amp; Orange</b></div>
  <div class="chiprow">${[0, 1, 2, 4, 3].map((k) => `<div class="gc h c${k}"><img src="${A}/g${k}.jpg"><u></u></div>`).join('')}</div>
  <div class="cursor abs h" style="left:0;top:0">${CURSOR}</div>
</div>

<div class="sc light" id="sc-c3">
  ${num(3)}
  <div class="lotpath abs" data-layout-ignore id="lp" style="left:40px;top:860px;width:1000px;height:460px"></div>
  <div class="bezel abs h lcard" style="left:220px;top:470px;width:640px">
    <div class="core lgrid"><img class="llogo" src="${A}/lottiefiles.png">${['heart', 'star', 'bell', 'rocket', 'music-note', 'arrow-bend-up-right', 'check-circle', 'smiley', 'paper-plane-tilt', 'gift', 'sparkle', 'fire']
      .map((n, k) => `<div class="lt h" style="--c:${['#C7E24B', '#E9D7A8', '#D7E6A0', '#F1D3C5'][k % 4]}">${ic(n)}</div>`).join('')}</div>
  </div>
</div>

<div class="sc light" id="sc-lot">
  <div class="tiles">${['arrow', 'check', 'smile'].map((k) => `<div class="tl h" id="tl-${k}"><div class="lot" id="lot-${k}"></div></div>`).join('')}</div>
  <div class="keys2 h"><div class="krail">${Array.from({ length: 6 }, (_, k) => `<i style="left:${40 + k * 116}px"></i>`).join('')}</div><b class="kph"></b></div>
  <div class="comm pill h" style="left:50%;top:1110px;transform:translateX(-50%)">${ic('check-circle', '', 'b')}можно в коммерцию</div>
</div>

<div class="sc light" id="sc-c4">
  ${num(4)}
  <div class="pgrid" data-layout-ignore>${Array.from({ length: 48 }, (_, k) => `<div class="pg">${ic(GRID[k % GRID.length])}</div>`).join('')}</div>
  <div class="search pill h" style="left:200px;top:470px">${ic('magic-wand', '', 'b')}<span>Search 1 512 icons</span><em>Regular</em></div>
  <div class="bezel abs h pcard" style="left:340px;top:640px;width:400px">
    <div class="core" style="padding:40px;text-align:center"><img src="${A}/phosphor.png" style="width:170px;height:170px;border-radius:44px;margin:0 auto"><div class="pname">Phosphor</div><div class="purl">phosphoricons.com</div></div>
  </div>
</div>

<div class="sc" id="sc-ph">
  <div class="big pbig" style="top:340px"><span class="cnt">0</span><span class="plus">+</span></div>
  <div class="cap" style="top:610px"><span class="h">иконок</span> <span class="h">в</span> <span class="h">одном</span> <span class="h" style="color:var(--lime)">стиле</span></div>
  <div class="wbox glass h">${Object.keys(CAT_WEIGHTS).map((k) => `<svg class="wcat w-${k}" viewBox="0 0 256 256" fill="currentColor">${CAT_WEIGHTS[k]}</svg>`).join('')}</div>
  <div class="wnames">${Object.keys(CAT_WEIGHTS).map((k) => `<span class="h wn-${k}">${k[0].toUpperCase() + k.slice(1)}</span>`).join('')}</div>
  <div class="p3 abs" style="left:0;top:1130px;width:1080px;height:240px"><div class="dgrid" data-layout-ignore>${Array.from({ length: 30 }, (_, k) => `<div class="dg">${ic(GRID[(k * 7) % GRID.length])}</div>`).join('')}</div></div>
</div>

<div class="sc light" id="sc-c5">
  ${num(5)}
  <div class="laptop abs h" style="left:110px;top:520px"><div class="lscr"><img src="${A}/reactbits-pc.jpg"></div><div class="lbase light"></div></div>
  <div class="fx">${['linear-gradient(135deg,#C7E24B,#56690C)', 'radial-gradient(circle at 30% 30%,#F1F2EA,#89A81C 60%,#2C3410)', 'repeating-linear-gradient(115deg,#12130F 0 14px,#56690C 14px 28px)', 'linear-gradient(160deg,#D97757,#12130F)']
    .map((b) => `<div class="fxt h" style="background:${b}"></div>`).join('')}</div>
</div>

<div class="sc light" id="sc-rb">
  <div class="tags">${['BlurText', 'ShinyText', 'Particles'].map((t, k) => `<div class="tag2 pill h t${k}">${ic(['sparkle', 'magic-wand', 'star'][k], '', 'b')}${t}</div>`).join('')}</div>
  <div class="frame abs h"><img src="${A}/g3.jpg"><div class="fshade abs"></div>
    <div class="ftitle">${[...'Монтаж'].map((c) => `<span class="ch">${c}</span>`).join('')}<div class="shine abs"></div></div>
    <div class="sparks abs">${Array.from({ length: 22 }, (_, k) => `<i class="spk" style="left:${Math.round(30 + rnd(k + 9) * 360)}px;top:${Math.round(40 + rnd(k + 51) * 520)}px;width:${8 + Math.round(rnd(k + 3) * 10)}px;height:${8 + Math.round(rnd(k + 3) * 10)}px"></i>`).join('')}</div>
  </div>
</div>

<div class="sc" id="sc-how">
  <div class="prompt2 glass h"><s>${CLAUDE}</s><span class="ptext">${[...'вставь в ролик'].map((c) => `<span class="ch">${c}</span>`).join('')}</span><u></u></div>
  <div class="file pill h">${ic('file-video', '', 'b')}clip.mp4</div>
  ${editor(A, 'ed2', [{ w: 150, img: 'r11-1.5.jpg' }, { w: 130, img: 'g1.jpg', cls: 'pre' }, { w: 0, img: 'g3.jpg', cls: 'ins', t: 'clip.mp4' }, { w: 170, img: 'r11-14.jpg', cls: 'post' }, { w: 150, img: 'mixkit-ph.jpg', cls: 'post' }])}
  <div class="cursor abs h" style="left:0;top:0">${CURSOR}</div>
</div>

<div class="sc" id="sc-share">
  <div class="scat abs h" style="left:70px;top:600px;width:430px"><img src="${A}/cat-share.png" style="width:100%"></div>
  <div class="sheet2 glass h">
    <div class="sh-t">Поделиться</div>
    ${[['Монтажёр Дима', '#C7E24B'], ['Аня · клипы', '#E9D7A8'], ['Сашa · reels', '#D97757']].map(([n, c], k) => `<div class="who w${k}"><i style="background:${c}">${ic('user', '', 'b')}</i><span>${n}</span><b class="ok">${ic('check', '', 'b')}</b></div>`).join('')}
    <div class="send">${ic('paper-plane-tilt', '', 'b')}Отправить</div>
  </div>
  <div class="plane abs h">${ic('paper-plane-tilt', '', 'b')}</div>
  <div class="cursor abs h" style="left:0;top:0">${CURSOR}</div>
</div>

<div class="sc" id="sc-cta">
  <div class="rays abs" data-layout-ignore></div>
  <div class="chest abs h" style="left:240px;top:560px;width:600px"><img src="${A}/cat-chest.png" style="width:100%"></div>
  <div class="tgc h" style="left:470px;top:440px">${ic('telegram-logo', '', 'r')}</div>
  ${SITES.map((p, k) => `<div class="fly h f${k}"><img src="${A}/${p.logo}"></div>`).join('')}
  <div class="go h" style="top:1135px"><span>Ссылка в профиле<div class="shim"></div></span></div>
  <div class="save h" style="top:1262px"><span>${ic('bookmark-simple', '', 'b')}Сохрани, чтобы не потерять</span></div>
</div>
`;

/** Заголовок сверху: слово встаёт, когда звучит. */
export const headlines = (T) => {
  const w = (id, i) => T.w[id][i];
  const s = (id) => T.scenes[id].s;
  const e = (id) => T.scenes[id].e;
  const H = (id, light, l1, l2 = []) => ({ id, light, from: s(id), to: e(id), l1, l2 });
  return [
    H('hook2', false, [['Этот', w('hook2', 0)], ['ролик', w('hook2', 1)]], [['собрал', w('hook2', 3)], ['Claude', w('hook2', 4), 'cl']]),
    H('need', false, [['Но', w('need', 0)], ['материалы', w('need', 1)]], [['всё', w('need', 3)], ['равно', w('need', 4)], ['нужны', w('need', 5)]]),
    { ...H('c1', true, [['Mixkit', w('c1', 1)]]), from: s('c1') },
    H('mix', true, [['Музыка,', w('mix', 0)], ['звуки', w('mix', 1)]], [['и', w('mix', 2)], ['стоковое', w('mix', 3)], ['видео', w('mix', 4)]]),
    H('mix2', true, [['Можно', w('mix2', 0)], ['в', w('mix2', 1)], ['коммерцию', w('mix2', 2)]], [['без', w('mix2', 3)], ['указания', w('mix2', 4)], ['автора', w('mix2', 5)]]),
    H('c2', false, [['FreshLUTs', w('c2', 1)]]),
    H('luts', false, [['Бесплатные', w('luts', 0)], ['луты', w('luts', 1)]], [['для', w('luts', 2)], ['цвета', w('luts', 3)]]),
    H('luts2', false, [['Как', w('luts2', 1)], ['в', w('luts2', 2)], ['кино', w('luts2', 3)]], [['в', w('luts2', 4)], ['один', w('luts2', 5)], ['клик', w('luts2', 6)]]),
    H('c3', true, [['LottieFiles', w('c3', 1)]]),
    H('lot', true, [['Готовые', w('lot', 0)], ['анимации', w('lot', 1)]]),
    H('lot2', true, [['Стрелки,', w('lot2', 0)], ['галочки,', w('lot2', 1)]], [['эмодзи', w('lot2', 2)]]),
    H('c4', true, [['Phosphor', w('c4', 1)]]),
    H('c5', true, [['React', w('c5', 1)], ['Bits', w('c5', 2)]]),
    H('rb', true, [['Эффекты', w('rb', 0)], ['и', w('rb', 1)], ['анимации', w('rb', 2)]], [['для', w('rb', 3)], ['твоих', w('rb', 4)], ['кадров', w('rb', 5)]]),
    H('how', false, [['Скачал', w('how', 0)], ['файл', w('how', 1)]], [['отдал', w('how', 2)], ['Claude', w('how', 3), 'cl']]),
    H('how2', false, [['Сам', w('how2', 2)], ['вставит', w('how2', 3)]], [['в', w('how2', 5)], ['ролик', w('how2', 6)]]),
    H('share', false, [['Перешли', w('share', 0)], ['другу', w('share', 1)]], [['кто', w('share', 2)], ['монтирует', w('share', 6)], ['руками', w('share', 7)]]),
    { ...H('cta', false, [['Все', w('cta', 0)], ['5', w('cta', 1)], ['ссылок', w('cta', 2)]], [['в', w('cta', 4)], ['Telegram', w('cta', 6), 'tgw']]), to: T.length },
  ];
};

// Время Lottie считается от начала ролика (адаптер HyperFrames перематывает плеер на время
// композиции), поэтому начало анимации вшивается в её слои: сдвиг в кадрах самого файла.
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
  const sweep = (el, t, duration = 1.1) => tl.fromTo(el, { '--sp': '-25%' }, { '--sp': '125%', duration, ease: 'power2.inOut' }, t);
  // курсор: появляется у края, едет к цели, щёлкает (сжимается) в момент события
  const cursorTo = (el, pts) => {
    pts.forEach(([x, y, t, click], k) => {
      if (k === 0) tl.fromTo(el, { opacity: 0, x: x + 50, y: y + 70 }, { opacity: 1, x, y, duration: 0.3, ease: 'power2.out' }, t);
      else tl.to(el, { x, y, duration: Math.max(0.2, t - pts[k - 1][2] - 0.05), ease: 'power2.inOut' }, pts[k - 1][2] + 0.05);
      if (click) tl.to(el, { scale: 0.82, duration: 0.08, ease: 'power2.out', yoyo: true, repeat: 1, transformOrigin: '10% 10%' }, t);
    });
  };

  // Сцены (контейнеры): некоторые держат две фразы — это одна форма, у которой меняется состояние.
  const CONT = [['hook', 'hook', 'hook'], ['hook2', 'hook2', 'need'], ['five', 'five', 'five'], ['c1', 'c1', 'c1'], ['mix', 'mix', 'mix'],
    ['mix2', 'mix2', 'mix2'], ['c2', 'c2', 'c2'], ['luts', 'luts', 'luts2'], ['c3', 'c3', 'c3'], ['lot', 'lot', 'lot2'], ['c4', 'c4', 'c4'],
    ['ph', 'ph', 'ph'], ['c5', 'c5', 'c5'], ['rb', 'rb', 'rb'], ['how', 'how', 'how2'], ['share', 'share', 'share'], ['cta', 'cta', 'link']];
  const ENTER = {
    hook2: [{ y: 90 }, 0.6, 'power3.out'], five: [{ scale: 1.14 }, 0.42, 'expo.out'], c1: [{ x: 110 }, 0.55, 'power4.out'],
    mix: [{ y: 100 }, 0.6, 'power3.out'], mix2: [{ scale: 0.94 }, 0.6, 'power2.out'], c2: [{ x: -110 }, 0.55, 'power4.out'],
    luts: [{ scale: 1.12 }, 0.6, 'expo.out'], c3: [{ y: 100 }, 0.55, 'power3.out'], lot: [{ x: 110 }, 0.5, 'power3.out'],
    c4: [{ scale: 1.16 }, 0.6, 'expo.out'], ph: [{ y: 110 }, 0.55, 'power4.out'], c5: [{ x: -110 }, 0.55, 'power4.out'],
    rb: [{ scale: 0.92 }, 0.6, 'power2.out'], how: [{ y: 90 }, 0.55, 'power3.out'], share: [{ x: 110 }, 0.5, 'power3.out'], cta: [{ scale: 0.9 }, 0.6, 'expo.out'],
  };
  const SC = {};
  CONT.forEach(([id, a, b], n) => {
    const el = $('#sc-' + id);
    SC[id] = el;
    const end = id === 'cta' ? L : e(b);
    const [from, dur, ease] = ENTER[id] || [{ scale: 0.955 }, 0.5, 'power3.out'];
    const to = { opacity: 1, filter: 'blur(0px)', duration: dur, ease };
    Object.keys(from).forEach((k) => { to[k] = k === 'scale' ? 1 : 0; });
    if (n > 0) tl.fromTo(el, { opacity: 0, filter: 'blur(16px)', ...from }, to, s(a));
    if (id !== 'cta') tl.to(el, { opacity: 0, scale: 1.05, filter: 'blur(16px)', duration: 0.34, ease: 'power2.in' }, end - 0.24);
  });

  // Свет: тёмные и светлые блоки чередуются, как у автора. У тёплых блоков (цвет, Claude, сундук) тёплое пятно.
  const bgL = $('.bg-light'), gLime = $('.glow-lime'), gWarm = $('.glow-warm'), gMint = $('.glow-mint'), vig = $('.vignette');
  const LIGHT = [['c1', 'c2', 'warm'], ['c3', 'ph', 'lime'], ['c5', 'how', 'warm']];
  LIGHT.forEach(([a, b, next]) => {
    tl.to(bgL, { opacity: 1, duration: 0.45, ease: 'power2.out' }, s(a) - 0.1);
    tl.to(gMint, { opacity: 1, duration: 0.6 }, s(a));
    tl.to([gLime, gWarm, vig], { opacity: 0, duration: 0.3 }, s(a) - 0.1);
    tl.to(bgL, { opacity: 0, duration: 0.45, ease: 'power2.out' }, s(b) - 0.1);
    tl.to(gMint, { opacity: 0, duration: 0.3 }, s(b) - 0.1);
    tl.to(vig, { opacity: 1, duration: 0.5 }, s(b));
    tl.to(next === 'warm' ? gWarm : gLime, { opacity: 1, duration: 0.6 }, s(b));
  });
  tl.to(gWarm, { opacity: 0, duration: 0.4 }, s('share') - 0.1);
  tl.to(gLime, { opacity: 1, duration: 0.6 }, s('share'));
  tl.to(gLime, { opacity: 0, duration: 0.4 }, s('cta') - 0.1);
  tl.to(gWarm, { opacity: 1, duration: 0.6 }, s('cta'));
  $$('.glow i').forEach((el, i) => tl.fromTo(el, { scale: 0.96 }, { scale: 1.05, duration: 3.2 + i * 0.5, ease: 'sine.inOut', yoyo: true, repeat: Math.max(0, Math.floor(L / (3.2 + i * 0.5)) - 1) }, 0));
  [['five', 900], ['luts', 760], ['ph', 700], ['cta', 820]].forEach(([id, y]) => tl.to([gLime, gWarm, gMint], { y: y - 760, duration: 0.8, ease: 'power2.inOut' }, s(id)));

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
  const numIn = (sc, t) => pop($('.num-pill', sc), t);
  // монтажный стол живёт с первого кадра: бегунок едет, счёт кадров идёт
  const editorRun = (ed, a, b) => {
    tl.fromTo($('.head', ed), { x: 0 }, { x: 640, duration: b - a, ease: 'none' }, a);
    count($('.fr', ed), 14, 14 + Math.round((b - a) * 30), a, b - a, 'none');
  };

  // 1. Крючок: три строки бьют по словам голоса. На нулевом кадре надпись уже читается, стол уже идёт.
  {
    const sc = SC.hook;
    tl.fromTo($('.floats', sc), { scale: 1.14 }, { scale: 1, duration: e('hook'), ease: 'power1.out' }, 0);
    [['.k1', w('hook', 0)], ['.k2', w('hook', 1)], ['.k3', w('hook', 3)]].forEach(([k, at]) =>
      tl.fromTo($(k, sc), { opacity: 0.62, scale: 1.06 }, { opacity: 1, scale: 1, duration: 0.24, ease: 'expo.out' }, Math.max(0.06, at - 0.05)));
    tl.fromTo($('#ed1', sc), { y: 40 }, { y: 0, duration: 1.2, ease: 'power2.out' }, 0);
    editorRun($('#ed1', sc), 0, e('hook'));
    inn($('.laptopcat', sc), 0.35, { y: 120, rotation: -6 }, 0.6);
  }

  // 2. Этот ролик собрал Claude → но материалы нужны: тот же телефон, экран пустеет, вокруг пустые места.
  {
    const sc = SC.hook2, t = s('hook2'), n = s('need');
    inn($('.ph1', sc), t + 0.05, { y: 120, scale: 0.92 }, 0.65);
    inn($('.kbd', sc), t + 0.15, { y: 80 }, 0.6);
    pop($('.cpill', sc), w('hook2', 3) - 0.1);
    tl.fromTo($('.rend i', sc), { scaleX: 0 }, { scaleX: 1, duration: n - t - 0.5, ease: 'power1.inOut' }, t + 0.3);
    tl.to($('.scr', sc), { opacity: 0, scale: 0.9, filter: 'blur(10px)', duration: 0.4, ease: 'power2.in' }, n - 0.05);
    tl.to($('.rend', sc), { opacity: 0, duration: 0.2 }, n - 0.05);
    tl.fromTo($('.empty', sc), { opacity: 0 }, { opacity: 1, duration: 0.35 }, n + 0.15);
    out($('.cpill', sc), n, 0.25);
    $$('.slot', sc).forEach((el, k) => inn(el, w('need', 1) + k * 0.12, { scale: 0.7, y: 30 }, 0.45, 'back.out(1.3)'));
    $$('.slotin', sc).forEach((el, k) => tl.fromTo(el, { opacity: 0.55 }, { opacity: 1, duration: 0.5, ease: 'sine.inOut', yoyo: true, repeat: 3 }, w('need', 3) + k * 0.1));
  }

  // 3. Пятёрка: число досчитывает, вкладки встают, под ними страница первого сайта.
  {
    const sc = SC.five, t = s('five');
    tl.fromTo($('.tile', sc), { scale: 0.8, rotation: -6 }, { scale: 1, rotation: 0, duration: 0.6, ease: 'expo.out' }, t);
    count($('.num', sc), 1, 5, t + 0.05, 0.45, 'power1.out');
    sweep($('.tile', sc), t + 0.5);
    $$('.cap span', sc).forEach((el, i) => word(el, w('five', 2 + i)));
    chipsIn(sc, w('five', 4) - 0.2);
    inn($('.brw', sc), w('five', 5), { y: 140 }, 0.6);
  }

  // Плашка «N / 5» встаёт в начале каждого сайта: счёт держит до конца.
  SITES.forEach((p) => numIn(SC[p.id], s(p.id) + 0.15));

  // 4. Mixkit: телефон со страницей сайта, страница прокручивается, вокруг плывут кадры стока.
  {
    const sc = SC.c1, t = s('c1'), end = e('c1');
    inn($('.ph2', sc), t + 0.05, { y: 130, rotation: 4 }, 0.7);
    tl.fromTo($('.scroll', sc), { y: 0 }, { y: -70, duration: end - t - 0.4, ease: 'power1.inOut' }, t + 0.4);
    $$('.lf', sc).forEach((el, k) => tl.fromTo(el, { y: 40 * (k % 2 ? 1 : -1) }, { y: -40 * (k % 2 ? 1 : -1), duration: end - t, ease: 'none' }, t));
    waveRun(sc, t, end);
  }

  // Музыка, звуки, видео: проигрыватель, счётчики встают на своих словах, плёнка едет.
  {
    const sc = SC.mix, t = s('mix'), end = e('mix');
    inn($('.player', sc), t + 0.05, { y: 60, scale: 0.94 }, 0.55);
    waveRun(sc, t, end);
    [['.s1', 0, 1000], ['.s2', 1, 3000], ['.s3', 4, 46000]].forEach(([k, wi, n]) => {
      pop($(k, sc), w('mix', wi) - 0.08);
      count($(k + ' .cnt', sc), 0, n, w('mix', wi), 0.7);
    });
    inn($('.strip', sc), w('mix', 3) - 0.15, { y: 90 }, 0.55);
    tl.fromTo($('.strip', sc), { x: 0 }, { x: -300, duration: end - t, ease: 'none' }, t);
  }

  // Можно в коммерцию: курсор включает оба тумблера на своих словах.
  {
    const sc = SC.mix2, t = s('mix2');
    inn($('.bezel', sc), t + 0.05, { y: 70, scale: 0.94 }, 0.6);
    const t1 = w('mix2', 2), t2 = w('mix2', 5);
    cursorTo($('.cursor', sc), [[900, 1150, t + 0.3], [826, 744, t1, true], [826, 866, t2, true], [900, 1250, t2 + 0.6]]);
    [['.t1', t1], ['.t2', t2]].forEach(([r, at]) => {
      tl.to($(r + ' .tog', sc), { backgroundColor: '#56690C', duration: 0.2 }, at);
      tl.to($(r + ' .tog i', sc), { x: 52, duration: 0.25, ease: 'back.out(1.6)' }, at);
    });
    $$('.ft', sc).forEach((el, k) => inn(el, t + 0.5 + k * 0.08, { y: 40, scale: 0.85 }, 0.45, 'back.out(1.2)'));
  }

  // 5. FreshLUTs: знак, ноутбук со страницей, ряд цветов, число скачиваний.
  {
    const sc = SC.c2, t = s('c2');
    pop($('.logoplate', sc), w('c2', 1) - 0.1);
    inn($('.laptop', sc), t + 0.05, { y: 120, rotationX: 18 }, 0.7);
    $$('.sw', sc).forEach((el, k) => inn(el, t + 0.45 + k * 0.07, { y: 40 }, 0.4));
    pop($('.dl', sc), e('c2') - 0.9);
  }

  // Цвет: один кадр на две фразы. Сперва перебор лутов, потом курсор выбирает «кино» и шторка проходит.
  {
    const sc = SC.luts, t = s('luts'), click = w('luts2', 5);
    inn($('.photo', sc), t + 0.05, { y: 80, scale: 0.94 }, 0.6);
    inn($('.lname', sc), t + 0.35, { y: 30 }, 0.4);
    const chipsEl = $$('.gc', sc);
    chipsEl.forEach((el, k) => inn(el, t + 0.3 + k * 0.06, { y: 30 }, 0.4));
    const show = (k, at) => {
      $$('.gr', sc).forEach((img) => tl.to(img, { opacity: img.classList.contains('g' + k) ? 1 : 0, duration: 0.18 }, at));
      $$('.lname b', sc).forEach((b) => tl.to(b, { opacity: b.classList.contains('ln' + k) ? 1 : 0, duration: 0.15 }, at));
      chipsEl.forEach((c) => tl.to($('u', c), { opacity: c.classList.contains('c' + k) ? 1 : 0, duration: 0.15 }, at));
    };
    tl.set($$('.gr', sc), { opacity: 0 }, 0); tl.set($('.g0', sc), { opacity: 1 }, 0);
    tl.set($$('.lname b', sc), { opacity: 0 }, 0); tl.set($('.ln0', sc), { opacity: 1 }, 0);
    show(1, w('luts', 1)); show(2, w('luts', 2) + 0.1); show(4, w('luts', 3) + 0.25); show(0, s('luts2') + 0.1);
    // клик: шторка «до → после» на «один клик»
    cursorTo($('.cursor', sc), [[880, 1400, s('luts2')], [866, 1246, click, true], [920, 1420, click + 0.9]]);
    tl.set($('.split', sc), { clipPath: 'inset(0% 100% 0% 0%)', opacity: 1 }, 0);
    tl.to($('.split', sc), { clipPath: 'inset(0% 0% 0% 0%)', duration: 0.8, ease: 'power2.inOut' }, click + 0.05);
    tl.fromTo($('.sline', sc), { opacity: 0, x: 0 }, { opacity: 1, duration: 0.08 }, click);
    tl.to($('.sline', sc), { x: 856, duration: 0.8, ease: 'power2.inOut' }, click + 0.05);
    out($('.sline', sc), click + 0.85, 0.15);
    chipsEl.forEach((c) => tl.to($('u', c), { opacity: c.classList.contains('c3') ? 1 : 0, duration: 0.15 }, click));
    $$('.lname b', sc).forEach((b) => tl.to(b, { opacity: b.classList.contains('ln3') ? 1 : 0, duration: 0.15 }, click + 0.1));
    inn($('.curve', sc), w('luts2', 1), { y: 20, scale: 0.9 }, 0.4);
    draw($('.cv', sc), w('luts2', 1) + 0.1, 0.8);
    tl.fromTo($('.cvd', sc), { x: -40, y: 30 }, { x: 0, y: 0, duration: 0.8, ease: 'power2.inOut' }, w('luts2', 1) + 0.1);
  }

  // 6. LottieFiles: карточка с анимациями, за ней пунктирный путь — настоящая анимация с сайта.
  {
    const sc = SC.c3, t = s('c3');
    inn($('.lcard', sc), t + 0.05, { y: 90, scale: 0.93 }, 0.6);
    $$('.lt', sc).forEach((el, k) => inn(el, t + 0.35 + k * 0.05, { scale: 0.6 }, 0.4, 'back.out(1.4)'));
    $$('.lt svg', sc).forEach((el, k) => tl.fromTo(el, { rotation: -8 }, { rotation: 8, duration: 0.9, ease: 'sine.inOut', yoyo: true, repeat: 1 }, t + 0.8 + (k % 4) * 0.12));
  }

  // Стрелки, галочки, эмодзи: плитки встают пустыми, каждая анимация играет на своём слове.
  {
    const sc = SC.lot, t = s('lot');
    $$('.tl', sc).forEach((el, k) => inn(el, t + 0.15 + k * 0.1, { y: 60, scale: 0.85 }, 0.5, 'back.out(1.2)'));
    inn($('.keys2', sc), t + 0.45, { y: 40 }, 0.45);
    tl.fromTo($('.kph', sc), { x: 0 }, { x: 640, duration: e('lot2') - s('lot2') - 0.2, ease: 'none' }, s('lot2'));
    $$('.krail i', sc).forEach((el, k) => tl.to(el, { backgroundColor: '#56690C', scale: 1.3, duration: 0.15 }, s('lot2') + (k / 5) * (e('lot2') - s('lot2') - 0.2)));
    [0, 1, 2].forEach((k) => tl.to($$('.tl', sc)[k], { scale: 1.08, duration: 0.18, ease: 'power2.out', yoyo: true, repeat: 1 }, w('lot2', k) - 0.05));
    pop($('.comm', sc), e('lot2') - 1.0);
  }

  // 7. Phosphor: сетка его иконок, поиск, карточка со знаком.
  {
    const sc = SC.c4, t = s('c4');
    $$('.pg', sc).forEach((el, k) => tl.fromTo(el, { opacity: 0, scale: 0.6 }, { opacity: 0.55, scale: 1, duration: 0.4, ease: 'power3.out' }, t + 0.1 + ((k % 6) + Math.floor(k / 6)) * 0.035));
    inn($('.search', sc), t + 0.3, { y: -30 }, 0.45);
    inn($('.pcard', sc), w('c4', 1) - 0.1, { scale: 0.85, y: 40 }, 0.55, 'back.out(1.2)');
  }

  // Больше 1200 иконок в одном стиле: счёт, потом одна иконка проходит все шесть начертаний.
  {
    const sc = SC.ph, t = s('ph'), end = e('ph');
    count($('.cnt', sc), 0, 1200, t + 0.05, w('ph', 3) - t - 0.1, 'power2.out');
    tl.fromTo($('.pbig', sc), { scale: 0.82 }, { scale: 1, duration: 0.9, ease: 'power3.out' }, t + 0.05);
    pop($('.plus', sc), w('ph', 3) - 0.1);
    $$('.cap span', sc).forEach((el, k) => word(el, w('ph', 3 + k)));
    inn($('.wbox', sc), t + 0.3, { y: 60, scale: 0.9 }, 0.55);
    const keys = Object.keys(CAT_WEIGHTS), step = (end - t - 0.9) / keys.length;
    keys.forEach((k, i) => {
      const at = t + 0.5 + i * step;
      tl.set($('.w-' + k, sc), { opacity: 1 }, at);
      if (i < keys.length - 1) tl.set($('.w-' + k, sc), { opacity: 0 }, at + step);
      tl.fromTo($('.wn-' + k, sc), { opacity: 0.32 }, { opacity: 1, duration: 0.12 }, at);
      if (i < keys.length - 1) tl.to($('.wn-' + k, sc), { opacity: 0.32, duration: 0.12 }, at + step);
    });
    $$('.dg', sc).forEach((el, k) => {
      const c = k % 10, r = Math.floor(k / 10);
      tl.fromTo(el, { opacity: 0, y: 30 }, { opacity: 0.6, y: 0, duration: 0.4, ease: 'power3.out' }, t + 0.2 + (c + r) * 0.04);
      tl.to(el, { color: '#C7E24B', opacity: 1, duration: 0.2, yoyo: true, repeat: 1 }, t + 1.2 + c * 0.09 + r * 0.05);
    });
  }

  // 8. React Bits: ноутбук со страницей, под ним плитки эффектов.
  {
    const sc = SC.c5, t = s('c5');
    inn($('.laptop', sc), t + 0.05, { y: 120, rotationX: 18 }, 0.7);
    $$('.fxt', sc).forEach((el, k) => inn(el, t + 0.5 + k * 0.08, { y: 40, scale: 0.85 }, 0.45, 'back.out(1.2)'));
    $$('.fxt', sc).forEach((el, k) => tl.fromTo(el, { backgroundPosition: '0% 0%' }, { backgroundPosition: '100% 100%', duration: e('c5') - t, ease: 'none' }, t + k * 0.1));
  }

  // Эффекты для кадров: буквы из размытия, блик по слову, искры — переписаны твинами с приёмов React Bits.
  {
    const sc = SC.rb, t = s('rb');
    inn($('.frame', sc), t + 0.05, { y: 90, scale: 0.92 }, 0.6);
    $$('.ftitle .ch', sc).forEach((c, k) => tl.fromTo(c, { opacity: 0, y: 30, filter: 'blur(14px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.45, ease: 'power3.out' }, w('rb', 0) + k * 0.06));
    tl.fromTo($('.shine', sc), { xPercent: -140 }, { xPercent: 140, duration: 0.9, ease: 'power2.inOut' }, w('rb', 2));
    $$('.spk', sc).forEach((el, k) => {
      const at = w('rb', 5) - 0.3 + rnd(k + 2) * 0.5;
      tl.fromTo(el, { opacity: 0, scale: 0, rotation: 0 }, { opacity: 1, scale: 1, rotation: 90, duration: 0.35, ease: 'back.out(2)' }, at);
      tl.to(el, { opacity: 0, scale: 0.4, rotation: 180, duration: 0.5, ease: 'power1.in' }, at + 0.45);
    });
    [[0, w('rb', 0)], [1, w('rb', 2)], [2, w('rb', 5) - 0.2]].forEach(([k, at]) => pop($('.t' + k, sc), at));
  }

  // 9. Скачал, отдал Claude, он сам вставил: файл падает, курсор тащит его в промпт, клип встаёт в дорожку.
  {
    const sc = SC.how, t = s('how'), ins = w('how2', 3);
    const ed = $('#ed2', sc);
    inn(ed, t + 0.05, { y: 100 }, 0.6);
    editorRun(ed, t, e('how2'));
    inn($('.prompt2', sc), t + 0.25, { y: -40 }, 0.45);
    inn($('.file', sc), w('how', 0), { y: -160, scale: 0.8 }, 0.55, 'back.out(1.2)');
    const drag = w('how', 2);
    cursorTo($('.cursor', sc), [[880, 820, w('how', 1)], [640, 700, drag - 0.1, true], [550, 610, drag + 0.55], [700, 1300, ins + 0.4]]);
    tl.to($('.file', sc), { x: -90, y: -80, scale: 0.7, duration: 0.6, ease: 'power2.inOut' }, drag);
    tl.to($('.file', sc), { opacity: 0, duration: 0.2 }, drag + 0.6);
    $$('.prompt2 .ch', sc).forEach((c, k) => tl.set(c, { opacity: 1 }, drag + 0.65 + k * 0.04));
    // клип раздвигает дорожку: соседи справа уезжают, новый растёт из нуля
    tl.to($('.clip.ins', ed), { width: 190, duration: 0.6, ease: 'power3.inOut' }, ins);
    tl.fromTo($('.clip.ins', ed), { boxShadow: '0 0 0 0 rgba(217,119,87,0)' }, { boxShadow: '0 0 0 5px rgba(217,119,87,.9)', duration: 0.3, yoyo: true, repeat: 1 }, ins + 0.6);
  }

  // Перешли другу: кот протягивает самолётик, курсор отмечает друзей и жмёт «Отправить».
  {
    const sc = SC.share, t = s('share'), send = w('share', 6);
    inn($('.scat', sc), t + 0.05, { x: -140 }, 0.6);
    inn($('.sheet2', sc), t + 0.2, { y: 120 }, 0.6);
    $$('.who', sc).forEach((el, k) => inn(el, t + 0.45 + k * 0.1, { x: 40 }, 0.4));
    cursorTo($('.cursor', sc), [[900, 1300, t + 0.5], [700, 795, w('share', 2), true], [700, 911, w('share', 4), true], [730, 1141, send, true], [900, 1320, send + 0.6]]);
    [[0, w('share', 2)], [1, w('share', 4)]].forEach(([k, at]) => pop($('.w' + k + ' .ok', sc), at));
    tl.to($('.send', sc), { scale: 0.94, duration: 0.08, yoyo: true, repeat: 1 }, send);
    tl.fromTo($('.plane', sc), { opacity: 0, x: 0, y: 0, rotation: -10, scale: 0.6 }, { opacity: 1, x: 540, y: -520, rotation: 20, scale: 1.1, duration: 0.9, ease: 'power2.in' }, send + 0.05);
    tl.to($('.plane', sc), { opacity: 0, duration: 0.2 }, send + 0.85);
  }

  // Призыв: сундук светится, из него вылетают пять сайтов и знак Telegram, потом ссылка и «сохрани».
  {
    const sc = SC.cta, t = s('cta');
    inn($('.chest', sc), t + 0.05, { y: 140, scale: 0.9 }, 0.7);
    tl.fromTo($('.rays', sc), { opacity: 0, rotation: 0 }, { opacity: 1, rotation: 25, duration: L - t, ease: 'none' }, t + 0.3);
    const P = [[110, 560], [280, 480], [690, 480], [860, 560], [120, 830]];
    $$('.fly', sc).forEach((el, k) => {
      const at = w('cta', 1) + k * 0.12;
      tl.fromTo(el, { opacity: 0, x: 540 - 70, y: 860, scale: 0.3, rotation: -30 }, { opacity: 1, x: P[k][0], y: P[k][1], scale: 1, rotation: 0, duration: 0.7, ease: 'expo.out' }, at);
      tl.to(el, { y: P[k][1] - 16, duration: 1.4, ease: 'sine.inOut', yoyo: true, repeat: Math.max(0, Math.floor((L - at - 0.7) / 1.4) - 1) }, at + 0.7);
    });
    tl.fromTo($('.tgc', sc), { opacity: 0, y: 340, scale: 0.4 }, { opacity: 1, y: 0, scale: 1, duration: 0.75, ease: 'expo.out' }, w('cta', 6) - 0.2);
    inn($('.go', sc), w('link', 0) - 0.1, { y: 40, scale: 0.9 }, 0.45, 'back.out(1.2)');
    sweep($('.go span', sc), w('link', 0) + 0.3, 0.9);
    inn($('.save', sc), w('link', 3) - 0.1, { y: 40, scale: 0.9 }, 0.45, 'back.out(1.2)');
    tl.to($('.save span', sc), { scale: 1.06, duration: 0.45, ease: 'sine.inOut', yoyo: true, repeat: 1 }, w('link', 3) + 0.5);
  }

  // Анимации LottieFiles: плеер без автозапуска, время вшито в файл, перематывает адаптер HyperFrames.
  if (typeof window !== 'undefined' && window.lottie) {
    window.__hfLottie = window.__hfLottie || [];
    const load = (id, data, at) => window.__hfLottie.push(window.lottie.loadAnimation({
      container: root.querySelector(id), renderer: 'svg', loop: false, autoplay: false, animationData: shiftLottie(data, at) }));
    load('#lot-arrow', LOTTIE.arrow, w('lot2', 0) - 0.1);
    load('#lot-check', LOTTIE.check, w('lot2', 1) - 0.1);
    load('#lot-smile', LOTTIE.smile, w('lot2', 2) - 0.2);
    load('#lp', LOTTIE.path, s('c3') + 0.2);
  }
  return tl;
};

/** Слой поверх сцен: знак канала, полоса ролика по абзацам, заголовки, субтитры. */
export const overlayMarkup = (A, T) => {
  const lines = new Map();
  T.caps.forEach((c) => lines.set(c.line, [...(lines.get(c.line) || []), c]));
  return `<div class="logo"><img src="${A}/logo.png"></div>
<div class="prog">${'<i><b></b></i>'.repeat(8)}</div>
` + headlines(T).map((h) => `<div class="hl ${h.light ? 'light' : ''}">${[h.l1, h.l2].map((line, k) => line.length ? `<div class="${k ? 'l2' : 'l1'}">${
    line.map(([txt, , cls]) => `<span class="${cls || ''}">${txt}</span>`).join('')}</div>` : '').join('')}</div>`).join('') + `
<div class="ccs">${[...lines.values()].map((ws) => `<div class="cc"><p>${ws.map((c) => `<span>${c.w}</span>`).join(' ')}</p></div>`).join('')}</div>`;
};

export const buildOverlay = (gsap, tl, root, T) => {
  const s = (id) => T.scenes[id].s;
  headlines(T).forEach((h, n) => {
    const box = root.querySelectorAll('.hl')[n];
    const spans = [...box.querySelectorAll('span')];
    [...h.l1, ...h.l2].forEach(([, at], i) =>
      tl.fromTo(spans[i], { opacity: 0, y: 24, filter: 'blur(12px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: i === 0 ? 0.3 : 0.38, ease: i === 0 ? 'expo.out' : 'power3.out' }, Math.max(h.from, at - 0.06)));
    if (h.to < T.length - 0.05) tl.to(spans, { opacity: 0, filter: 'blur(12px)', duration: 0.24, ease: 'power2.in' }, h.to - 0.26);
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

  // Полоса ролика: восемь отрезков — крючок, пять сайтов, «отдал Claude», призыв; последний
  // заполняется к самому концу. На заставке её нет: прорисовывается на смене первого кадра.
  const prog = root.querySelector('.prog');
  const старт = s('hook2');
  [...prog.querySelectorAll('i')].forEach((el, i) =>
    tl.fromTo(el, { opacity: 0, scaleX: 0 }, { opacity: 1, scaleX: 1, duration: 0.45, ease: 'expo.out' }, старт + 0.1 + i * 0.05));
  const части = [старт + 0.3, s('c1'), s('c2'), s('c3'), s('c4'), s('c5'), s('how'), s('cta'), T.length - 0.4];
  [...prog.querySelectorAll('b')].forEach((b, i) =>
    tl.fromTo(b, { scaleX: 0 }, { scaleX: 1, duration: части[i + 1] - части[i], ease: 'none' }, части[i]));
  // цвет полосы следует за светом сцены
  [['c1', 1], ['c2', 0], ['c3', 1], ['ph', 0], ['c5', 1], ['how', 0]].forEach(([id, light]) =>
    tl.set(prog, { '--pf': light ? '#56690C' : '#C7E24B', '--pt': light ? 'rgba(18,19,15,.16)' : 'rgba(241,242,234,.2)' }, s(id)));
  return tl;
};
