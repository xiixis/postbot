// Объём ролика r14, третья версия: один мир — светлая студия-мастерская (выбор владельца 14.10.2026, проба «А»).
//
// Почему так: владелец сказал «дизайн не выглядит целостным». Разбор референсов (Apple «Wonderful Tools» — Buck,
// Vercel Ship — basement, DeepMind «Visualising AI», лучшие ролики Opus 5.5 на skillry: @twoclipping, @heyiamnick)
// дал общее правило: один фон, один материал, один свет, одна сквозная нить, переход — движение, а не растворение.
// Отсюда: 15 станций стоят в одной студии рядком по оси X, камера переезжает между ними на смене сцены, внутри
// станции только чуть наезжает. Всё матовое, как глина: фигуры графит, постаменты крем, инструменты олива; лайм —
// только «задача» и активное; терракота — только Claude. Сквозной герой — настоящий знак Claude.
// Кадр — чистая функция времени (событие hf-seek), без часов и случайных чисел.

export const buildThree = async (THREE, X, canvas, T, A) => {
  const { SVGLoader, RoundedBoxGeometry, RoomEnvironment } = X;
  await Promise.all(['800 64px Unbounded', '700 40px Onest', '800 40px Onest', '600 40px Onest', '500 40px "JetBrains Mono"'].map((f) => document.fonts.load(f)));

  // ── Палитра и мир ─────────────────────────────────────────────────────────────────────────────────
  const C = { bg: 0xE7E8DD, fig: 0x2A2B24, ped: 0xF6F7EF, tool: 0x56690C, lime: 0xC7E24B, claude: 0xD97757, cream: 0xF1F2EA, stone: 0xD3D4C8 };
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(1080, 1920, false);
  renderer.toneMapping = THREE.NeutralToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.VSMShadowMap;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(C.bg);
  scene.fog = new THREE.Fog(C.bg, 15, 30);
  const camera = new THREE.PerspectiveCamera(34, 1080 / 1920, 0.1, 120);
  scene.add(new THREE.HemisphereLight(0xFFF6E8, 0xBFC0B2, 1.4));
  const key = new THREE.DirectionalLight(0xFFF3E0, 2.0);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.radius = 14;
  key.shadow.blurSamples = 24;
  Object.assign(key.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7, near: 1, far: 40 });
  scene.add(key, key.target);
  // отражения только для металла и стекла телефона: глине они не нужны
  const envTex = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;

  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  const clay = (c, r = 0.82, o = {}) => new THREE.MeshStandardMaterial({ color: c, roughness: r, metalness: 0, ...o });
  const mesh = (geo, mat, parent) => { const m = new THREE.Mesh(geo, mat); m.castShadow = true; m.receiveShadow = true; if (parent) parent.add(m); return m; };
  const rbox = (w, h, d, r = 0.06, seg = 4) => new RoundedBoxGeometry(w, h, d, seg, Math.min(r, w / 2 - 0.001, h / 2 - 0.001, d / 2 - 0.001));
  // Студия без горизонта: пол плавно загибается в стену (циклорама), как в студийной съёмке Apple и DeepMind
  // (владелец 14.10.2026 выбрал «студия без горизонта»). Профиль: пол до z = −1,6, дуга радиусом 3,4, стена на z = −5.
  const cyc = (() => {
    const prof = [];
    for (let z = 9; z > -1.6; z -= 0.5) prof.push([z, 0]);
    for (let i = 0; i <= 24; i++) { const a = (i / 24) * (Math.PI / 2); prof.push([-1.6 - 3.4 * Math.sin(a), 3.4 - 3.4 * Math.cos(a)]); }
    for (let y = 4; y <= 22; y += 1) prof.push([-5.0, y]);
    const x0 = -20, x1 = 110, pos = [], idx = [];
    prof.forEach(([z, y]) => { pos.push(x0, y, z, x1, y, z); });
    for (let i = 0; i < prof.length - 1; i++) { const a2 = i * 2; idx.push(a2, a2 + 1, a2 + 2, a2 + 1, a2 + 3, a2 + 2); }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
    return g;
  })();
  const floor = new THREE.Mesh(cyc, clay(C.bg, 1));
  floor.receiveShadow = true; scene.add(floor);

  // ── Время сценария ────────────────────────────────────────────────────────────────────────────────
  const s = (id) => T.scenes[id].s, e = (id) => T.scenes[id].e, w = (id, i) => T.w[id][i];
  const cl = (x) => Math.max(0, Math.min(1, x));
  const pr = (t, a, d) => cl((t - a) / d);
  const eOut = (x) => 1 - Math.pow(1 - x, 3);
  const eExpo = (x) => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x));
  const eIO = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
  const eIn = (x) => x * x * x;
  // пружина без перелёта (критическое затухание): 1 − (1 + ωt)·e^(−ωt)
  const spring = (t, a, wgt = 16) => (t <= a ? 0 : 1 - (1 + wgt * (t - a)) * Math.exp(-wgt * (t - a)));
  const lerp = (a, b, x) => a + (b - a) * x;
  const vl = (a, b, x) => a.clone().lerp(b, x);
  const hop = (x, hgt) => Math.sin(Math.PI * cl(x)) * hgt;

  // ── Текстуры: надписи шрифтом канала, значки Phosphor контурами ────────────────────────────────────
  const PPU = 266;                                       // пикселей кадра на единицу мира у центра станции
  const tex = (cv) => { const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; };
  const pathsOf = (svg) => [...svg.matchAll(/\sd="([^"]+)"/g)].map((m) => m[1]);
  const icon = (name, set = 'f') => (set === 'f' ? FILL : set === 'b' ? BOLD : ICONS)[name];
  const drawIcon = (g, name, x, y, size, color, set = 'f') => {
    g.save(); g.translate(x, y); g.scale(size / 256, size / 256); g.fillStyle = color;
    pathsOf(icon(name, set)).forEach((d) => g.fill(new Path2D(d))); g.restore();
  };
  const measure = (text, font) => { const g = document.createElement('canvas').getContext('2d'); g.font = font; return g.measureText(text).width; };
  const card = (wpx, hpx, draw) => { const cv = document.createElement('canvas'); cv.width = wpx * 2; cv.height = hpx * 2; const g = cv.getContext('2d'); g.scale(2, 2); draw(g, wpx, hpx); return cv; };
  const face = (cv, wu, parent, z) => {
    const p = new THREE.Mesh(new THREE.PlaneGeometry(wu, (wu * cv.height) / cv.width), new THREE.MeshBasicMaterial({ map: tex(cv), transparent: true, toneMapped: false }));
    p.position.z = z; if (parent) parent.add(p); return p;
  };
  const roundRect = (g, x, y, w2, h2, r) => { g.beginPath(); g.roundRect(x, y, w2, h2, r); g.fill(); };

  // пузырь сообщения: плита со скруглением и надписью
  const bubble = (text, { px = 30, bg = 0xFAFAF4, fg = '#12130F', weight = 700, depth = 0.08 } = {}) => {
    const font = `${weight} ${px}px Onest`;
    const wpx = Math.ceil(measure(text, font)) + px * 1.6, hpx = Math.round(px * 2.1);
    const g = new THREE.Group();
    mesh(rbox(wpx / PPU, hpx / PPU, depth, hpx / PPU / 2 - 0.004), clay(bg, 0.7), g);
    face(card(wpx, hpx, (c) => { c.font = font; c.fillStyle = fg; c.textBaseline = 'middle'; c.textAlign = 'center'; c.fillText(text, wpx / 2, hpx / 2 + 1); }), wpx / PPU, g, depth / 2 + 0.002);
    return g;
  };
  // выдавливание контура SVG (viewBox vbw×vbh), размер по ширине
  const extrude = (ds, vbw, vbh, width, depthK = 0.18, bevelK = 0.03) => {
    const svg = `<svg viewBox="0 0 ${vbw} ${vbh}">${ds.map((d) => `<path d="${d}"/>`).join('')}</svg>`;
    const shapes = new SVGLoader().parse(svg).paths.flatMap((p) => SVGLoader.createShapes(p));
    const k = Math.max(vbw, vbh);
    const geo = new THREE.ExtrudeGeometry(shapes, { depth: k * depthK, bevelEnabled: true, bevelThickness: k * bevelK, bevelSize: k * bevelK * 0.6, bevelSegments: 5, curveSegments: 14 });
    geo.center();
    geo.rotateX(Math.PI);                                // SVG сверху вниз: поворот, а не масштаб −1 (тот выворачивает грани)
    geo.scale(width / vbw, width / vbw, width / vbw);
    geo.computeVertexNormals();
    return geo;
  };

  // ── Станции ───────────────────────────────────────────────────────────────────────────────────────
  // Каждая станция — группа в своей точке X. Камера: p — где стоит, l — куда смотрит, относительно станции.
  const GAP = 5;                                        // соседняя станция въезжает в кадр по ходу переезда: пустых кадров нет
  const ST = [
    { name: 'msg', ids: ['hook', 'who'], p: V(0, 3.6, 9.6), l: V(0, 1.65, 0.3) },
    { name: 'code', ids: ['code', 'self'], p: V(0, 4.6, 8.8), l: V(0, 1.2, 0) },
    { name: 'hype', ids: ['hype'], p: V(0, 3.0, 9.6), l: V(0, 1.5, 0.3) },
    { name: 'try', ids: ['try'], p: V(0, 3.6, 9.2), l: V(0, 1.75, 0.3) },
    { name: 'slop', ids: ['slop'], p: V(0, 6.8, 7.0), l: V(0, 0.45, 0.1) },
    { name: 'stop', ids: ['stop', 'why'], p: V(0, 3.2, 9.4), l: V(0, 1.55, 0.3) },
    { name: 'team', ids: ['team', 'roles', 'skills', 'much'], p: V(0, 5.2, 10.6), l: V(0, 0.65, 0.4) },
    { name: 'same', ids: ['same', 'same2'], p: V(0, 3.0, 9.4), l: V(0, 1.3, 0) },
    { name: 'refs', ids: ['refs'], p: V(0, 4.0, 9.2), l: V(0, 1.35, 0) },
    { name: 'design', ids: ['design'], p: V(0, 3.2, 9.2), l: V(-0.2, 1.45, 0.2) },
    { name: 'uniq', ids: ['uniq'], p: V(0, 3.0, 9.6), l: V(0, 1.5, 0) },
    { name: 'check', ids: ['check'], p: V(0, 4.2, 9.4), l: V(0, 1.2, 0) },
    { name: 'path', ids: ['path'], p: V(0, 3.6, 10.2), l: V(0, 1.45, 0) },
    { name: 'pack', ids: ['pack'], p: V(0, 5.0, 9.0), l: V(0, 1.3, 0.2) },
    { name: 'cta', ids: ['cta'], p: V(0, 3.2, 9.6), l: V(0, 1.55, 0.4) },
  ];
  ST.forEach((st, k) => { st.x = k * GAP; st.g = new THREE.Group(); st.g.position.x = st.x; scene.add(st.g); st.a = s(st.ids[0]); st.b = e(st.ids[st.ids.length - 1]); });
  const S = Object.fromEntries(ST.map((st) => [st.name, st]));
  const W = (st, x, y, z) => V(st.x + x, y, z);       // точка станции в мире

  // общие предметы
  const pedestal = (r, h, parent, c = C.ped) => { const m = mesh(new THREE.CylinderGeometry(r, r * 1.06, h, 64), clay(c), parent); m.position.y = h / 2; return m; };
  const sparkGeo = extrude([BRAND.spark], 24, 24, 1, 0.07, 0.016);
  const sparkMat = () => clay(C.claude, 0.45, { emissive: C.claude, emissiveIntensity: 0.16 });
  const T_ = clay(C.tool);
  const TOOLS = {
    pen: () => { const g = new THREE.Group(); mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.42, 16), T_, g); const tip = mesh(new THREE.ConeGeometry(0.035, 0.08, 16), clay(C.lime), g); tip.position.y = -0.25; tip.rotation.x = Math.PI; g.rotation.z = 0.5; return g; },
    palette: () => { const g = new THREE.Group(); const d = mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.035, 32), T_, g); d.rotation.x = Math.PI / 2.4; [[0.06, 0.05, C.lime], [-0.06, 0.06, C.fig], [0, -0.07, C.cream]].forEach(([a, b, c]) => { const sp = mesh(new THREE.SphereGeometry(0.035, 16, 12), clay(c, 0.5), g); sp.position.set(a, b, 0.04); }); return g; },
    film: () => { const g = new THREE.Group(); mesh(rbox(0.32, 0.22, 0.04, 0.02), T_, g); mesh(rbox(0.22, 0.13, 0.05, 0.01), clay(C.lime), g); return g; },
    phones: () => { const g = new THREE.Group(); mesh(new THREE.TorusGeometry(0.14, 0.025, 12, 32, Math.PI), T_, g); [-0.14, 0.14].forEach((x) => { const c = mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.06, 20), clay(C.lime), g); c.rotation.z = Math.PI / 2; c.position.set(x, -0.01, 0); }); return g; },
    loupe: () => { const g = new THREE.Group(); mesh(new THREE.TorusGeometry(0.1, 0.025, 12, 32), T_, g); const h = mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.18, 12), T_, g); h.position.set(0.1, -0.13, 0); h.rotation.z = 0.7; return g; },
  };
  // агент — наш маскот в позе своей роли (владелец 14.10.2026: «вместо круглых персонажей поставить моего маскота»).
  // Объёмной модели кота нет, есть его 3D-рендеры: кот стоит картинкой на постаменте, всегда лицом к камере, с мягкой тенью.
  const loader0 = new THREE.TextureLoader();
  const CAT = Object.fromEntries(await Promise.all(['noutbuk', 'ideya', 'kamera', 'mikrofon', 'lupa'].map(async (n) => {
    const t = await loader0.loadAsync(`${A}/cats/cat-${n}.png`); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return [n, t];
  })));
  const blobTex = tex(card(128, 128, (g) => { const gr = g.createRadialGradient(64, 64, 4, 64, 64, 62); gr.addColorStop(0, 'rgba(30,32,20,.45)'); gr.addColorStop(1, 'rgba(30,32,20,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); }));
  const CATS = [];
  const agent = (pose, parent, hgt = 0.98) => {
    const g = new THREE.Group();
    const ped = mesh(new THREE.CylinderGeometry(0.42, 0.46, 0.16, 48), clay(C.ped), g); ped.position.y = 0.08;
    const blob = new THREE.Mesh(new THREE.PlaneGeometry(0.75, 0.75), new THREE.MeshBasicMaterial({ map: blobTex, transparent: true, depthWrite: false, toneMapped: false }));
    blob.rotation.x = -Math.PI / 2; blob.position.y = 0.162; g.add(blob);
    const body = new THREE.Group(); body.position.y = 0.16; g.add(body);
    const tx = CAT[pose], asp = tx.image.width / tx.image.height;
    const geo = new THREE.PlaneGeometry(hgt * asp, hgt); geo.translate(0, hgt / 2, 0);
    body.add(new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ map: tx, transparent: true, alphaTest: 0.35, toneMapped: false })));
    if (parent) parent.add(g);
    const a = { g, ped, body, wob: 0 }; CATS.push(a); return a;
  };
  // настоящий кадр ролика: телефон с текстурой
  const loader = new THREE.TextureLoader();
  const img = async (file) => { const t = await loader.loadAsync(`${A}/${file}`); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; };
  const REAL = Object.fromEntries(await Promise.all(['fan1', 'fan2', 'fan3', 's1', 's2', 's3', 's4', 's5', 's6', 's7'].map(async (f) => [f, await img(`real/${f}.jpg`)])));
  // Телефон как настоящий: контур с радиусом углов 16 % ширины выдавлен с округлой фаской, рамка — титан с отражениями,
  // кнопки по бокам, блок камер на спинке, экран с чёрной кромкой и «островком» (владелец 14.10.2026: «модельку телефона
  // сделать более настоящей»).
  const titan = new THREE.MeshStandardMaterial({ color: 0x3B3C3F, metalness: 0.88, roughness: 0.32, envMap: envTex, envMapIntensity: 1.1 });
  const glassBlack = new THREE.MeshStandardMaterial({ color: 0x0B0B0C, metalness: 0.2, roughness: 0.12, envMap: envTex, envMapIntensity: 0.9 });
  const screenOf = (src, ratio) => {                            // картинка или холст → экран с кромкой и островком
    const W2 = 540, H2 = Math.round(540 * ratio);
    const cv = document.createElement('canvas'); cv.width = W2; cv.height = H2;
    const g = cv.getContext('2d');
    g.fillStyle = '#060606'; roundRect(g, 0, 0, W2, H2, W2 * 0.15);
    const b = W2 * 0.032;
    g.save(); g.beginPath(); g.roundRect(b, b, W2 - 2 * b, H2 - 2 * b, W2 * 0.125); g.clip();
    const sw = src.width, sh = src.height, k = Math.max((W2 - 2 * b) / sw, (H2 - 2 * b) / sh);
    g.drawImage(src, (W2 - sw * k) / 2, (H2 - sh * k) / 2, sw * k, sh * k); g.restore();
    g.fillStyle = '#000'; roundRect(g, W2 * 0.36, b + W2 * 0.03, W2 * 0.28, W2 * 0.075, W2 * 0.0375);
    return tex(cv);
  };
  const phoneShape = (w2, h2, r) => {
    const s = new THREE.Shape(), x = -w2 / 2, y = -h2 / 2;
    s.moveTo(x + r, y); s.lineTo(x + w2 - r, y); s.absarc(x + w2 - r, y + r, r, -Math.PI / 2, 0, false);
    s.lineTo(x + w2, y + h2 - r); s.absarc(x + w2 - r, y + h2 - r, r, 0, Math.PI / 2, false);
    s.lineTo(x + r, y + h2); s.absarc(x + r, y + h2 - r, r, Math.PI / 2, Math.PI, false);
    s.lineTo(x, y + r); s.absarc(x + r, y + r, r, Math.PI, Math.PI * 1.5, false);
    return s;
  };
  const phone = (map, wd, ht, parent) => {
    const g = new THREE.Group();
    const d = wd * 0.075, bev = d * 0.42;
    const geo = new THREE.ExtrudeGeometry(phoneShape(wd - 2 * bev, ht - 2 * bev, wd * 0.16 - bev), { depth: d - 2 * bev, bevelEnabled: true, bevelThickness: bev, bevelSize: bev, bevelSegments: 8, curveSegments: 28 });
    geo.translate(0, 0, -(d - 2 * bev) / 2);
    mesh(geo, titan, g);
    const front = new THREE.Mesh(new THREE.ShapeGeometry(phoneShape(wd * 0.985, ht * 0.99, wd * 0.155), 28), glassBlack); front.position.z = d / 2 + 0.001; g.add(front);
    const scr = new THREE.Mesh(new THREE.PlaneGeometry(wd * 0.965, ht * 0.975), new THREE.MeshBasicMaterial({ map: screenOf(map.image, (ht * 0.975) / (wd * 0.965)), transparent: true, toneMapped: false }));
    scr.position.z = d / 2 + 0.003; g.add(scr);
    const btn = (x, y, hh) => { const m = mesh(rbox(wd * 0.03, hh, d * 0.45, 0.004), titan, g); m.position.set(x, y, 0); };
    btn(-wd / 2 - wd * 0.006, ht * 0.27, ht * 0.05); btn(-wd / 2 - wd * 0.006, ht * 0.17, ht * 0.08); btn(-wd / 2 - wd * 0.006, ht * 0.06, ht * 0.08);
    btn(wd / 2 + wd * 0.006, ht * 0.15, ht * 0.13);
    const cam = mesh(rbox(wd * 0.42, wd * 0.42, d * 0.25, wd * 0.08), titan, g); cam.position.set(-wd * 0.2, ht * 0.5 - wd * 0.3, -d / 2 - d * 0.1);
    [[-0.09, 0.09], [-0.09, -0.09], [0.09, 0]].forEach(([a, b2]) => {
      const l = mesh(new THREE.CylinderGeometry(wd * 0.075, wd * 0.075, d * 0.3, 32), glassBlack, g); l.rotation.x = Math.PI / 2;
      l.position.set(-wd * 0.2 + a * wd, ht * 0.5 - wd * 0.3 + b2 * wd, -d / 2 - d * 0.22);
    });
    if (parent) parent.add(g);
    return { g, scr };
  };

  // ── 1–2. Сообщения: из телефона вылетают вопросы, приходит главный, ответ «Никто», на постамент падает Claude ──
  const MSG = S.msg;
  const msgPhone = phone(tex(card(260, 500, (g, W2, H2) => {
    g.fillStyle = '#F1F2EA'; g.fillRect(0, 0, W2, H2);
    g.fillStyle = '#DADBD0'; [[24, 70, 150], [86, 140, 150], [24, 210, 120], [70, 280, 166], [24, 350, 140]].forEach(([x, y, ww]) => roundRect(g, x, y, ww, 46, 23));
  })), 1.2, 2.3, MSG.g);
  msgPhone.g.position.set(0, 1.18, -0.4);
  // Лавина: десятки вопросов сыплются сверху всё гуще и ложатся горой у телефона, счётчик растёт до «99+»
  // (владелец 14.10.2026: «чтобы в начале будто меня завалили сообщениями, чтобы их прям было оооочень много»).
  const FLOOD_TEXT = ['как ты делаешь такие ролики?', 'это нейросеть?', 'скинь программу', 'чем монтируешь?', 'научи так же',
    'сколько стоит монтаж?', 'где взять шаблон?', 'это After Effects?', 'кто тебе монтирует?', 'дай гайд', 'хочу так же',
    'как??', 'это ИИ?', 'ответь пж', 'сделаешь мне?', 'какой софт?', 'сколько часов на ролик?', 'это Claude?',
    'покажи процесс', 'а бесплатно можно?', 'научишь?', 'чем озвучиваешь?', 'это шаблон?', 'где скачать?'];
  const r1 = (k) => { const x = Math.sin(k * 91.7 + 17.3) * 43758.5453; return x - Math.floor(x); };
  const FLOOD_N = 110;
  const FLOOD = Array.from({ length: FLOOD_N }, (_, k) => {
    const b = bubble(FLOOD_TEXT[k % FLOOD_TEXT.length], { px: 27, bg: k % 5 === 2 ? 0xF1F2EA : 0xFBFBF6 });
    MSG.g.add(b);
    const u = k / (FLOOD_N - 1);
    const x = (r1(k) - 0.5) * 3.1;
    const layer = Math.floor(k / 11);
    return {
      b, k,
      ts: -0.95 + 2.75 * Math.pow(u, 0.72),                    // всё гуще; на обложке первые уже летят и лежат
      rest: V(x, 0.07 + layer * 0.11 + 0.55 * Math.max(0, 1 - Math.abs(x) / 1.6) * (layer / 9) + r1(k + 13) * 0.05, -0.05 + r1(k + 9) * 1.65),
      from: V(x * 0.7 + (r1(k + 2) - 0.5), 6.4 + r1(k + 3) * 1.6, -0.5 + r1(k + 9) * 1.2),
      rx: -0.55 - r1(k + 21) * 0.65, rz: (r1(k + 23) - 0.5) * 0.9, ry: (r1(k + 27) - 0.5) * 0.7, spin: (r1(k + 29) - 0.5) * 7,
    };
  });
  const badgeCv = document.createElement('canvas'); badgeCv.width = 220; badgeCv.height = 120;
  const badgeTex = tex(badgeCv);
  let badgeShown = '';
  const drawBadge = (txt) => {
    if (txt === badgeShown) return; badgeShown = txt;
    const g = badgeCv.getContext('2d'); g.clearRect(0, 0, 220, 120);
    g.fillStyle = '#C7E24B'; roundRect(g, 4, 4, 212, 112, 56);
    g.font = '800 70px Onest'; g.fillStyle = '#12130F'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(txt, 110, 64);
    badgeTex.needsUpdate = true;
  };
  const badge = new THREE.Mesh(new THREE.PlaneGeometry(0.44, 0.24), new THREE.MeshBasicMaterial({ map: badgeTex, transparent: true, toneMapped: false }));
  badge.position.set(0.5, 1.12, 0.07); msgPhone.g.add(badge);
  const ask = bubble('кто монтирует эти ролики?', { px: 40, bg: C.lime, weight: 800 }); MSG.g.add(ask);
  const nobody = bubble('Никто.', { px: 58, bg: C.fig, fg: '#F1F2EA', weight: 800, depth: 0.1 }); MSG.g.add(nobody);
  const whoPed = pedestal(0.62, 0.42, MSG.g);
  const codePlate = new THREE.Group(); MSG.g.add(codePlate);
  mesh(rbox(1.55, 0.36, 0.08, 0.17), clay(C.fig, 0.6), codePlate);
  face(card(412, 96, (g) => {
    g.save(); g.translate(28, 22); g.scale(52 / 24, 52 / 24); g.fillStyle = '#D97757'; g.fill(new Path2D(BRAND.code), 'evenodd'); g.restore();
    g.font = '800 40px Onest'; g.fillStyle = '#F1F2EA'; g.textBaseline = 'middle'; g.fillText('Claude Code', 100, 50);
  }), 1.55, codePlate, 0.042);

  // ── 3–4. Код и монтаж ──────────────────────────────────────────────────────────────────────────────
  const CODE = S.code;
  const genPivot = new THREE.Group(); genPivot.position.set(-0.2, 0, -0.5); CODE.g.add(genPivot);
  const gen = new THREE.Group(); genPivot.add(gen); gen.position.y = 0.95;
  mesh(rbox(2.5, 1.6, 0.12, 0.1), clay(C.fig, 0.5), gen);
  face(card(640, 410, (g, W2, H2) => {
    const gr = g.createRadialGradient(W2 * 0.45, H2 * 0.4, 20, W2 * 0.5, H2 * 0.5, W2 * 0.6);
    gr.addColorStop(0, '#CFC8E0'); gr.addColorStop(0.6, '#8A86A0'); gr.addColorStop(1, '#4C4A58');
    g.fillStyle = gr; roundRect(g, 0, 0, W2, H2, 22);
    g.fillStyle = 'rgba(255,255,255,.28)'; g.beginPath(); g.arc(W2 / 2, H2 / 2 - 20, 54, 0, Math.PI * 2); g.fill();
    drawIcon(g, 'play', W2 / 2 - 24, H2 / 2 - 44, 48, '#FFFFFF');
    g.fillStyle = 'rgba(0,0,0,.3)'; roundRect(g, 30, H2 - 88, W2 - 60, 58, 29);
    drawIcon(g, 'sparkle', 50, H2 - 78, 38, '#FFFFFF');
    g.font = '600 30px Onest'; g.fillStyle = '#FFFFFF'; g.textBaseline = 'middle'; g.fillText('генерирую видео…', 100, H2 - 58);
  }), 2.4, gen, 0.062);
  const strikeBar = mesh(rbox(3.3, 0.16, 0.16, 0.07), clay(C.fig, 0.6), CODE.g);
  // первая строка кода разбита на части: проверка HyperFrames принимает её текст за второй таймлайн ролика
  const CODE_LINES = [['const', ' tl = gsap.' + 'timeline();'], ['', 'tl.from(card, { y: 140 }, 0.4);'], ['', 'tl.to(title, { opacity: 1 }, 1.2);'],
    ['', "spin(drum, '1200', 2.0);"], ['//', ' голос, музыка, звуки'], ['', 'render({ fps: 30 });']];
  const codeCv = document.createElement('canvas'); codeCv.width = 1400; codeCv.height = 880;
  const codeTex = tex(codeCv);
  let codeShown = -1;
  const drawCode = (n, frac) => {
    const key2 = n * 100 + Math.floor(frac * 40);
    if (key2 === codeShown) return; codeShown = key2;
    const g = codeCv.getContext('2d'); g.setTransform(2, 0, 0, 2, 0, 0);
    g.fillStyle = '#15160F'; g.fillRect(0, 0, 700, 440);
    g.font = '500 30px "JetBrains Mono"'; g.textBaseline = 'top';
    CODE_LINES.forEach(([k0, rest], i) => {
      if (i > n) return;
      const full = k0 + rest, len = i < n ? full.length : Math.floor(full.length * frac);
      const shown = full.slice(0, len);
      const kw = shown.slice(0, Math.min(len, k0.length)), tail = shown.slice(kw.length);
      g.fillStyle = k0 === '//' ? 'rgba(241,242,234,.45)' : '#C7E24B'; g.fillText(kw, 36, 40 + i * 62);
      g.fillStyle = k0 === '//' ? 'rgba(241,242,234,.45)' : '#F1F2EA'; g.fillText(tail, 36 + g.measureText(kw).width, 40 + i * 62);
    });
    codeTex.needsUpdate = true;
  };
  const tablet = new THREE.Group(); CODE.g.add(tablet);
  mesh(rbox(2.7, 1.72, 0.1, 0.1), clay(C.fig, 0.5), tablet);
  const tabFace = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 1.634), new THREE.MeshBasicMaterial({ map: codeTex, toneMapped: false })); tabFace.position.z = 0.052; tablet.add(tabFace);
  // стол монтажа: дорожки, клипы, бегунок, превью
  const board = new THREE.Group(); CODE.g.add(board);
  mesh(rbox(3.7, 0.1, 2.0, 0.08), clay(C.ped), board).position.y = 0.05;
  const LANE_Z = [-0.65, -0.22, 0.22, 0.65];
  [[-1.35, 0.9, C.cream], [-0.35, 1.05, C.lime], [0.75, 0.8, C.cream]].forEach(([x, wd, c]) => { mesh(rbox(wd, 0.07, 0.32, 0.04), clay(c, 0.6), board).position.set(x, 0.14, LANE_Z[0]); });
  ['s1', 's2', 's3', 's4'].forEach((f, k) => {
    const clip = mesh(rbox(0.82, 0.07, 0.32, 0.04), clay(C.fig, 0.6), board); clip.position.set(-1.3 + k * 0.88, 0.14, LANE_Z[1]);
    const top = new THREE.Mesh(new THREE.PlaneGeometry(0.76, 0.28), new THREE.MeshBasicMaterial({ map: REAL[f], toneMapped: false }));
    top.rotation.x = -Math.PI / 2; top.position.set(-1.3 + k * 0.88, 0.177, LANE_Z[1]); board.add(top);
  });
  for (let i = 0; i < 46; i++) { const hgt = 0.04 + 0.16 * Math.abs(Math.sin(i * 0.61) * Math.cos(i * 0.23)); mesh(rbox(0.045, hgt, 0.045, 0.015), clay(C.tool), board).position.set(-1.65 + i * 0.072, 0.1 + hgt / 2, LANE_Z[2]); }
  for (let i = 0; i < 6; i++) { const d = mesh(rbox(0.13, 0.13, 0.13, 0.03), clay(C.lime, 0.6), board); d.position.set(-1.4 + i * 0.56, 0.18, LANE_Z[3]); d.rotation.y = Math.PI / 4; }
  const playhead = mesh(rbox(0.05, 0.42, 1.9, 0.02), clay(C.fig, 0.5), board); playhead.position.y = 0.3;
  const preview = phone(REAL.s1, 0.86, 1.53, CODE.g); preview.g.position.set(0, 1.0, -1.45);
  const doneP = bubble('ролик собран', { px: 34, bg: C.lime, weight: 800 }); CODE.g.add(doneP);

  // ── 5. Хайп: Claude на постаменте, настоящая надпись Claude объёмом, поднимаются сердца ────────────────
  const HYPE = S.hype;
  pedestal(0.8, 0.55, HYPE.g);
  const word = mesh(extrude(BRAND.text, 97, 24, 2.2, 0.14, 0.02), clay(C.fig, 0.6), HYPE.g); word.position.set(0, 0.36, 1.35);
  const hs = new THREE.Shape();
  hs.moveTo(0.25, 0.25); hs.bezierCurveTo(0.25, 0.25, 0.2, 0, 0, 0); hs.bezierCurveTo(-0.3, 0, -0.3, 0.35, -0.3, 0.35);
  hs.bezierCurveTo(-0.3, 0.55, -0.1, 0.77, 0.25, 0.95); hs.bezierCurveTo(0.6, 0.77, 0.8, 0.55, 0.8, 0.35);
  hs.bezierCurveTo(0.8, 0.35, 0.8, 0, 0.5, 0); hs.bezierCurveTo(0.35, 0, 0.25, 0.25, 0.25, 0.25);
  const heartGeo = new THREE.ExtrudeGeometry(hs, { depth: 0.22, bevelEnabled: true, bevelThickness: 0.08, bevelSize: 0.06, bevelSegments: 5, curveSegments: 16 });
  heartGeo.center(); heartGeo.rotateZ(Math.PI); heartGeo.computeVertexNormals();
  const rnd = (k) => { const x = Math.sin(k * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  const HEARTS = Array.from({ length: 12 }, (_, k) => ({ m: mesh(heartGeo, clay([C.claude, C.lime, C.fig][k % 3], 0.6), HYPE.g), x: (k % 2 ? 1 : -1) * (0.9 + rnd(k + 3) * 0.75), z: -0.6 + rnd(k + 7) * 1.2, d: rnd(k + 9), sz: 0.22 + rnd(k + 11) * 0.16 }));

  // ── 6. «Сделай ролик»: строка ввода, курсор отправляет, ожидание ──────────────────────────────────────
  const TRY = S.try;
  const inpCv = document.createElement('canvas'); inpCv.width = 1800; inpCv.height = 380;
  const inpTex = tex(inpCv);
  let inpShown = -1;
  const drawInput = (n, caret) => {
    const k2 = n * 2 + (caret ? 1 : 0); if (k2 === inpShown) return; inpShown = k2;
    const g = inpCv.getContext('2d'); g.setTransform(2, 0, 0, 2, 0, 0);
    g.clearRect(0, 0, 900, 190);
    g.save(); g.translate(40, 61); g.scale(68 / 24, 68 / 24); g.fillStyle = '#D97757'; g.fill(new Path2D(BRAND.spark)); g.restore();
    g.font = '700 62px Onest'; g.fillStyle = '#12130F'; g.textBaseline = 'middle';
    const txt = 'сделай ролик'.slice(0, n); g.fillText(txt, 140, 97);
    if (caret) { g.fillRect(146 + g.measureText(txt).width, 62, 5, 70); }
    inpTex.needsUpdate = true;
  };
  const inp = new THREE.Group(); TRY.g.add(inp);
  mesh(rbox(3.4, 0.72, 0.16, 0.34), clay(0xFBFBF6, 0.6), inp);
  const inpFace = new THREE.Mesh(new THREE.PlaneGeometry(3.4, 0.718), new THREE.MeshBasicMaterial({ map: inpTex, transparent: true, toneMapped: false })); inpFace.position.z = 0.082; inp.add(inpFace);
  const send = new THREE.Group(); inp.add(send); send.position.set(1.32, 0, 0.1);
  const sendBody = mesh(new THREE.CylinderGeometry(0.25, 0.25, 0.12, 40), clay(C.fig, 0.5), send); sendBody.rotation.x = Math.PI / 2;
  face(card(120, 120, (g) => drawIcon(g, 'paper-plane-tilt', 22, 22, 76, '#C7E24B')), 0.3, send, 0.065);
  const cursorGeo = extrude(pathsOf(FILL.cursor), 256, 256, 0.42, 0.08, 0.02);
  const cursor3 = mesh(cursorGeo, clay(C.fig, 0.5), TRY.g);
  const wait = new THREE.Group(); TRY.g.add(wait);
  mesh(rbox(2.6, 1.3, 0.1, 0.12), clay(C.stone, 0.8), wait);
  const spinner = mesh(new THREE.TorusGeometry(0.22, 0.04, 12, 48, Math.PI * 1.4), clay(C.fig, 0.5), wait); spinner.position.z = 0.1;

  // ── 7. Нейрослоп: девять одинаковых плиток с одинаковым шаром, штамп ─────────────────────────────────
  const SLOP = S.slop;
  const tileGeo = rbox(0.82, 0.14, 0.82, 0.06), blobGeo = new THREE.SphereGeometry(0.25, 48, 32);
  const SLOPS = [];
  for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
    const g = new THREE.Group(); g.position.set((c - 1) * 0.98, 0, (r - 1) * 0.98); SLOP.g.add(g);
    mesh(tileGeo, clay(C.ped), g).position.y = 0.07;
    const blob = mesh(blobGeo, clay(0xBDB6D6, 0.5), g); blob.scale.set(1, 0.85, 1);
    SLOPS.push({ g, blob, k: r + c });
  }
  const stamp = new THREE.Group(); SLOP.g.add(stamp);
  mesh(rbox(2.7, 0.7, 0.14, 0.14), clay(C.fig, 0.55), stamp);
  face(card(700, 182, (g) => { g.font = '800 82px Unbounded'; g.fillStyle = '#C7E24B'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('нейрослоп', 350, 96); }), 2.6, stamp, 0.072);

  // ── 8–9. Стоп: объёмная ладонь бьёт сверху, «Claude Opus 5.5» перечёркнут; потом «?» ──────────────────
  const STOP = S.stop;
  const hand = mesh(extrude(pathsOf(FILL['hand-palm']), 256, 256, 1.7, 0.1, 0.025), clay(C.fig, 0.55), STOP.g);
  const model = new THREE.Group(); STOP.g.add(model);
  mesh(rbox(2.9, 0.62, 0.12, 0.29), clay(0xFBFBF6, 0.6), model);
  face(card(770, 164, (g) => {
    g.save(); g.translate(40, 44); g.scale(76 / 24, 76 / 24); g.fillStyle = '#D97757'; g.fill(new Path2D(BRAND.spark)); g.restore();
    g.font = '800 62px Onest'; g.fillStyle = '#12130F'; g.textBaseline = 'middle'; g.fillText('Claude Opus 5.5', 140, 84);
  }), 2.9, model, 0.062);
  const mark = mesh(rbox(3.2, 0.12, 0.1, 0.05), clay(C.fig, 0.5), STOP.g);
  const qm = mesh(extrude(pathsOf(BOLD['question-mark']), 256, 256, 2.3, 0.12, 0.02), clay(C.fig, 0.55), STOP.g);

  // ── 10–13. Команда: Claude в центре, пять агентов, «задача» переходит от одного к другому ────────────
  const TEAM = S.team;
  pedestal(0.62, 0.42, TEAM.g);
  const R = 1.18;
  const ROLE_TOOLS = ['noutbuk', 'ideya', 'kamera', 'mikrofon', 'lupa'];
  const AG = ROLE_TOOLS.map((tl, k) => {
    const a = agent(tl, TEAM.g);
    const ang = -Math.PI / 2 + (k * Math.PI * 2) / 5 + Math.PI;
    a.g.position.set(Math.cos(ang) * R, 0, Math.sin(ang) * R);
    a.g.rotation.y = Math.atan2(-a.g.position.x, -a.g.position.z) + Math.PI;
    return a;
  });
  const threadMat = new THREE.MeshBasicMaterial({ color: C.claude });
  const THREADS = AG.map((a) => {
    const p = a.g.position;
    const curve = new THREE.QuadraticBezierCurve3(V(0, 0.3, 0), V(p.x * 0.5, 0.05, p.z * 0.5), V(p.x * 0.82, 0.05, p.z * 0.82));
    const m = new THREE.Mesh(new THREE.TubeGeometry(curve, 48, 0.013, 8), threadMat); TEAM.g.add(m); return m;
  });
  const task = mesh(rbox(0.32, 0.32, 0.32, 0.07), clay(C.lime, 0.6, { emissive: C.lime, emissiveIntensity: 0.12 }), TEAM.g);
  const PLUGS = [['puzzle-piece', V(-0.85, 0.2, 2.15)], ['plug', V(0.85, 0.2, 2.15)]].map(([ic, at]) => {
    const g = new THREE.Group(); TEAM.g.add(g);
    mesh(rbox(0.46, 0.46, 0.46, 0.1), clay(C.lime, 0.6), g);
    face(card(160, 160, (c) => drawIcon(c, ic, 20, 20, 120, '#12130F')), 0.34, g, 0.232);
    const curve = new THREE.QuadraticBezierCurve3(at.clone().add(V(0, 0.1, -0.2)), V(at.x * 0.4, 0.05, 1.0), V(0, 0.25, 0.55));
    const thread = new THREE.Mesh(new THREE.TubeGeometry(curve, 48, 0.013, 8), threadMat); TEAM.g.add(thread);
    return { g, at, thread };
  });

  // ── 14–15. Одинаковые ролики: три одинаковых телефона двигаются разом ───────────────────────────────
  const SAME = S.same;
  const sameScreen = (lime) => tex(card(210, 380, (g, W2, H2) => {
    const gr = g.createLinearGradient(0, 0, 0, H2); gr.addColorStop(0, '#3A3B33'); gr.addColorStop(1, '#22231C');
    g.fillStyle = gr; g.fillRect(0, 0, W2, H2);
    g.fillStyle = 'rgba(241,242,234,.82)'; g.beginPath(); g.arc(105, 135, 36, 0, Math.PI * 2); g.fill();
    roundRect(g, 50, 180, 110, 115, [55, 55, 10, 10]);
    g.fillStyle = lime ? '#C7E24B' : '#FFFFFF'; roundRect(g, 23, 305, 164, 48, 11);
    g.fillStyle = '#8E9080'; roundRect(g, 38, 318, 134, 8, 4); roundRect(g, 38, 332, 85, 8, 4);
    drawIcon(g, 'sparkle', 160, 18, 34, '#E8C468');
  }));
  const scrA = screenOf(sameScreen(false).image, (1.52 * 0.975) / (0.84 * 0.965)), scrB = screenOf(sameScreen(true).image, (1.52 * 0.975) / (0.84 * 0.965));
  const PH3 = [-1.0, 0, 1.0].map((x) => { const p = phone(sameScreen(false), 0.84, 1.52, SAME.g); p.g.position.set(x, 0.8, 0); return p; });

  // ── 16. Референсы: наклонная доска с плитками листается, часы ───────────────────────────────────────
  const REFS = S.refs;
  const refBoard = new THREE.Group(); REFS.g.add(refBoard); refBoard.position.set(0, 1.2, -0.3); refBoard.rotation.x = -0.55; refBoard.scale.setScalar(0.84);
  mesh(rbox(3.3, 3.6, 0.1, 0.12), clay(C.ped), refBoard).position.z = -0.06;
  const RCOL = ['#2A2B24', '#56690C', '#B9B9AE', '#8C8E7E', '#E2E2D8', '#3F4A1C'];
  const REFT = Array.from({ length: 18 }, (_, k) => {
    const bg = RCOL[Math.floor(rnd(k + 3) * RCOL.length)], fg = RCOL[(RCOL.indexOf(bg) + 1 + Math.floor(rnd(k + 7) * 4)) % RCOL.length];
    const t0 = Math.floor(rnd(k + 11) * 4);
    const cv = card(200, 250, (g, W2, H2) => {
      g.fillStyle = bg; roundRect(g, 0, 0, W2, H2, 18); g.fillStyle = fg;
      if (t0 === 0) { g.beginPath(); g.arc(100, 125, 62, 0, Math.PI * 2); g.fill(); }
      if (t0 === 1) { g.fillRect(0, 130, 200, 120); g.fillStyle = '#F1F2EA'; g.beginPath(); g.arc(100, 80, 40, 0, Math.PI * 2); g.fill(); }
      if (t0 === 2) { g.beginPath(); g.moveTo(0, 0); g.lineTo(200, 0); g.lineTo(0, 250); g.fill(); }
      if (t0 === 3) { roundRect(g, 26, 34, 148, 24, 12); roundRect(g, 26, 76, 100, 24, 12); g.globalAlpha = 0.6; roundRect(g, 26, 140, 148, 80, 14); }
    });
    const tile = new THREE.Group(); refBoard.add(tile);
    mesh(rbox(0.92, 1.15, 0.06, 0.07), clay(C.ped), tile);
    face(cv, 0.86, tile, 0.032);
    return { tile, k };
  });
  const clock = new THREE.Group(); REFS.g.add(clock);
  const clockFace = mesh(new THREE.CylinderGeometry(0.5, 0.5, 0.12, 64), clay(0xFBFBF6, 0.6), clock); clockFace.rotation.x = Math.PI / 2;
  const rim = mesh(new THREE.TorusGeometry(0.5, 0.05, 16, 64), clay(C.fig, 0.5), clock); rim.position.z = 0.02;
  const handM = mesh(rbox(0.05, 0.36, 0.04, 0.02), clay(C.fig, 0.5), clock); handM.geometry.translate(0, 0.15, 0); handM.position.z = 0.09;
  const handH = mesh(rbox(0.06, 0.24, 0.04, 0.02), clay(C.tool, 0.5), clock); handH.geometry.translate(0, 0.1, 0); handH.position.z = 0.1;

  // ── 17. Дизайнер-агент переворачивает карточку: «ролик» в четырёх обликах ────────────────────────────
  const DES = S.design;
  const designer = agent('ideya', DES.g, 1.15); designer.g.position.set(-1.05, 0, 0.75); designer.g.rotation.y = 0.5;
  const dCard = new THREE.Group(); DES.g.add(dCard); dCard.position.set(0.35, 1.3, 0);
  mesh(rbox(1.75, 2.35, 0.08, 0.12), clay(C.ped), dCard);
  const STYLE = [
    (g, W2, H2) => { g.fillStyle = '#F1F2EA'; roundRect(g, 0, 0, W2, H2, 30); g.font = '800 84px Onest'; g.fillStyle = '#12130F'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('РОЛИК', W2 / 2, H2 / 2 - 10); g.fillStyle = '#56690C'; roundRect(g, 70, H2 / 2 + 50, W2 - 140, 12, 6); },
    (g, W2, H2) => { g.fillStyle = '#12130F'; roundRect(g, 0, 0, W2, H2, 80); g.font = '800 78px Unbounded'; g.fillStyle = '#C7E24B'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('ролик', W2 / 2, H2 / 2); },
    (g, W2, H2) => { g.fillStyle = '#C7E24B'; roundRect(g, 0, 0, W2, H2, 12); g.font = '500 58px "JetBrains Mono"'; g.fillStyle = '#12130F'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('<ролик/>', W2 / 2, H2 / 2); },
    (g, W2, H2) => { g.fillStyle = '#1B2108'; roundRect(g, 0, 0, W2, H2, 200); g.strokeStyle = '#C7E24B'; g.lineWidth = 5; g.beginPath(); g.ellipse(W2 / 2, H2 / 2, 150, 92, 0, 0, Math.PI * 2); g.stroke(); g.font = 'italic 800 86px Onest'; g.fillStyle = '#F1F2EA'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('ролик', W2 / 2, H2 / 2); },
  ].map((f) => tex(card(420, 565, f)));
  const dFace = new THREE.Mesh(new THREE.PlaneGeometry(1.68, 2.26), new THREE.MeshBasicMaterial({ map: STYLE[0], transparent: true, toneMapped: false })); dFace.position.z = 0.042; dCard.add(dFace);

  // ── 18. Веер: три настоящих ролика канала ──────────────────────────────────────────────────────────
  const UNIQ = S.uniq;
  const FAN = ['fan1', 'fan2', 'fan3'].map((f) => phone(REAL[f], 1.2, 2.13, UNIQ.g));
  const made = new THREE.Group(); UNIQ.g.add(made);
  mesh(rbox(2.6, 0.42, 0.08, 0.2), clay(0xFBFBF6, 0.6), made);
  face(card(700, 112, (g) => {
    g.font = '700 44px Onest'; g.textBaseline = 'middle'; g.fillStyle = '#12130F'; g.fillText('собрано в', 70, 58);
    const x0 = 70 + g.measureText('собрано в ').width;
    g.save(); g.translate(x0, 34); g.scale(48 / 24, 48 / 24); g.fillStyle = '#D97757'; g.fill(new Path2D(BRAND.code), 'evenodd'); g.restore();
    g.fillStyle = '#D97757'; g.fillText('Claude', x0 + 62, 58); g.fillStyle = '#12130F'; g.fillText('Code', x0 + 62 + g.measureText('Claude ').width, 58);
  }), 2.6, made, 0.042);

  // ── 19. Проверка: конвейер, рамка-сканер, агент с лупой, брак падает с ленты ─────────────────────────
  const CHK = S.check;
  mesh(rbox(4.6, 0.18, 1.1, 0.08), clay(C.fig, 0.6), CHK.g).position.set(0, 0.09, 0);
  const gate = new THREE.Group(); CHK.g.add(gate);
  [[-0.62, 1.0], [0.62, 1.0]].forEach(([x, hgt]) => mesh(rbox(0.12, 2.0, 0.12, 0.05), clay(C.fig, 0.5), gate).position.set(x, hgt, 0));
  mesh(rbox(1.36, 0.12, 0.12, 0.05), clay(C.fig, 0.5), gate).position.set(0, 2.0, 0);
  const scan = mesh(rbox(1.1, 0.05, 0.5, 0.02), clay(C.lime, 0.5, { emissive: C.lime, emissiveIntensity: 0.25 }), gate);
  const inspector = agent('lupa', CHK.g, 1.1); inspector.g.position.set(0.95, 0, -1.0); inspector.g.rotation.y = -0.5;
  const STRIP = ['s1', 's2', 's4', 's6', 's5', 's3', 's7'];
  const BAD = 3;
  const CARDS = STRIP.map((f, k) => {
    const p = phone(REAL[f], 0.66, 1.17, CHK.g);
    const b = new THREE.Group(); p.g.add(b); b.position.set(0, 0.78, 0.05);
    mesh(new THREE.CylinderGeometry(0.15, 0.15, 0.06, 32), clay(k === BAD ? C.fig : C.lime, 0.5), b).rotation.x = Math.PI / 2;
    face(card(80, 80, (c) => drawIcon(c, k === BAD ? 'x' : 'check', 12, 12, 56, k === BAD ? '#F1F2EA' : '#12130F', 'b')), 0.2, b, 0.035);
    return { ...p, badge: b };
  });

  // ── 20. Путь: пять ступеней, Claude поднимается по ним ────────────────────────────────────────────
  const PATH = S.path;
  const STEPS = [['lightbulb', 'Идея'], ['pencil-simple-line', 'Сценарий'], ['microphone', 'Голос'], ['film-strip', 'Монтаж'], ['eye', 'Проверка']];
  const STEP = STEPS.map(([ic, name], k) => {
    const hgt = 0.32 + k * 0.34;
    const g = new THREE.Group(); PATH.g.add(g); g.position.set(-1.12 + k * 0.6, 0, 0.3 - k * 0.12);
    const box = mesh(rbox(0.58, hgt, 0.8, 0.05), clay(C.ped), g); box.position.y = hgt / 2;
    const top = mesh(rbox(0.55, 0.04, 0.77, 0.02), clay(C.lime, 0.6), g); top.position.y = hgt + 0.01;
    const f = face(card(210, 120, (c) => { drawIcon(c, ic, 75, 6, 60, '#12130F'); c.font = '800 30px Unbounded'; c.fillStyle = '#12130F'; c.textAlign = 'center'; c.fillText(name, 105, 104); }), 0.56, g, 0.403);
    f.position.y = Math.max(0.22, hgt - 0.24);
    return { g, hgt, top };
  });

  // ── 21. Коробка «система»: агенты, скилы и настройки улетают внутрь, крышка закрывается ──────────────
  const PACK = S.pack;
  const boxG = new THREE.Group(); PACK.g.add(boxG); boxG.position.set(0, 0.5, 0.2); boxG.rotation.y = -0.38;
  const BW = 1.8, BH = 1.0, BD = 1.3, TH = 0.07;
  const olive = clay(C.tool, 0.7);
  [[BW, TH, BD, 0, -BH / 2, 0], [BW, BH, TH, 0, 0, BD / 2], [BW, BH, TH, 0, 0, -BD / 2], [TH, BH, BD, BW / 2, 0, 0], [TH, BH, BD, -BW / 2, 0, 0]]
    .forEach(([a, b, c, x, y, z]) => mesh(rbox(a, b, c, 0.025, 2), olive, boxG).position.set(x, y, z));
  const lidPivot = new THREE.Group(); lidPivot.position.set(0, BH / 2, -BD / 2); boxG.add(lidPivot);
  mesh(rbox(BW + 0.06, TH, BD + 0.05, 0.025, 2), olive, lidPivot).position.set(0, 0, BD / 2);
  const sys = face(card(400, 110, (c) => { c.font = '800 70px Unbounded'; c.fillStyle = '#F1F2EA'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('система', 200, 58); }), 1.45, boxG, BD / 2 + 0.04);
  const ITEMS = [['users-three', 'агенты', V(-1.05, 2.05, 0.7)], ['puzzle-piece', 'скилы', V(1.05, 2.05, 0.7)], ['gear', 'настройки', V(0, 2.45, 0.5)]].map(([ic, name, at]) => {
    const g = new THREE.Group(); PACK.g.add(g);
    mesh(rbox(0.5, 0.5, 0.5, 0.1), clay(C.lime, 0.6), g);
    face(card(160, 160, (c) => drawIcon(c, ic, 20, 20, 120, '#12130F')), 0.36, g, 0.252);
    const lb = bubble(name, { px: 26, bg: 0xFBFBF6, weight: 800, depth: 0.05 }); lb.position.set(0, -0.45, 0.1); g.add(lb);
    return { g, at, lb };
  });
  const mouth = V(0, 1.05, 0.2);

  // ── 22. Финал: настоящий логотип Telegram объёмом, Claude ныряет в него, «ссылка в профиле», «сохрани», кот ──
  const CTA = S.cta;
  pedestal(0.75, 0.5, CTA.g);
  const tg = mesh(extrude([BRAND.tg], 24, 24, 1.55, 0.12, 0.02), clay(0x26A5E4, 0.5), CTA.g); tg.position.set(0, 1.42, 0);
  const link = new THREE.Group(); CTA.g.add(link);
  mesh(rbox(2.9, 0.6, 0.14, 0.29), clay(C.fig, 0.55), link);
  face(card(770, 160, (g) => {
    g.font = '800 54px Onest'; g.fillStyle = '#C7E24B'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('ссылка в профиле', 360, 82);
    drawIcon(g, 'arrow-up-right', 640, 52, 60, '#C7E24B', 'b');
  }), 2.9, link, 0.072);
  const bookmark = mesh(extrude(pathsOf(FILL['bookmark-simple']), 256, 256, 0.62, 0.12, 0.02), clay(C.lime, 0.55), CTA.g);
  const saveB = bubble('сохрани', { px: 34, bg: C.fig, fg: '#C7E24B', weight: 800 }); CTA.g.add(saveB);
  const catTex = await img('cat-point.png');
  const cat = new THREE.Mesh(new THREE.PlaneGeometry(1.25, 1.25 * 799 / 578), new THREE.MeshBasicMaterial({ map: catTex, transparent: true, alphaTest: 0.5, toneMapped: false }));
  CTA.g.add(cat);
  const cursorB = mesh(cursorGeo, clay(C.fig, 0.5), CTA.g);

  // ── Герой: настоящий знак Claude ─────────────────────────────────────────────────────────────────
  const hero = mesh(sparkGeo, sparkMat()); scene.add(hero);
  const put = (pos, size, ry = 0, rx = 0, sq = 1) => { hero.visible = size > 0.004; hero.position.copy(pos); hero.scale.set(size * (2 - sq), size * sq, size); hero.rotation.set(rx, ry, 0); };
  const heroAt = (t) => {
    const sway = 0.4 * Math.sin(t * 1.1);
    const tw = w('who', 2) - 0.2;
    const landWho = W(MSG, 0.95, 1.15, 0.75);
    if (t < tw) return put(landWho, 0);
    if (t < s('code') - 0.05) {                                 // падает с неба на постамент, чуть сплющивается при посадке
      const x = eIn(pr(t, tw, 0.42));
      const sq = 1 - 0.18 * Math.sin(Math.PI * pr(t, tw + 0.42, 0.24));
      return put(vl(W(MSG, 0.95, 7, 0.75), landWho, x), 1.05, sway, 0, sq);
    }
    const watch = W(CODE, 1.45, 2.25, 0.2);
    if (t < s('self') - 0.1) {                                  // летит со станцией, садится на угол, на «пишет» крутится
      const x = eIO(pr(t, s('code') - 0.05, 0.7));
      const spin = eIO(pr(t, w('code', 7), 1.3)) * Math.PI * 4;
      return put(vl(landWho, watch, x).add(V(0, 0.05 * Math.sin(t * 5), 0)), lerp(1.05, 0.55, x), sway + spin, 0.1);
    }
    const a = s('self') + 0.35, b = e('self') - 0.45;
    const headX = (-1.55 + 3.15 * cl((t - a) / (b - a))) * 0.8;
    const onHead = W(CODE, headX, 0.7, 0.35);
    if (t < s('hype') - 0.05) {                                 // едет на бегунке
      const x = eIO(pr(t, s('self') - 0.1, 0.5));
      return put(vl(watch, onHead, x), lerp(0.55, 0.36, x), 0.5 * Math.sin(t * 3), 0);
    }
    const onPed = W(HYPE, 0, 1.55, 0.05);
    if (t < s('try') - 0.05) {                                  // хайп: крупно на постаменте
      const x = eIO(pr(t, s('hype') - 0.05, 0.7));
      return put(vl(onHead, onPed, x).add(V(0, hop(x, 1.2), 0)), lerp(0.36, 1.55, x), sway, 0.08);
    }
    if (t < s('team') - 0.05) return put(onPed, 0);
    const center = W(TEAM, 0, 0.98, 0.05);
    if (t < e('much')) {                                        // команда: вырастает в центре кольца из точки «?»
      const x = spring(t, s('team') - 0.05, 9);
      return put(center, 0.95 * x, sway * 0.8, 0.08);
    }
    if (t < s('path') - 0.05) return put(center, 0);
    if (t < e('path')) {                                        // путь: стоит на ступени, на её слове прыгает на следующую
      const topOf = (k) => W(PATH, -1.12 + k * 0.6, STEP[k].hgt + 0.32, 0.3 - k * 0.12);
      let k = 0; for (let i = 1; i < 5; i++) if (t >= w('path', i) - 0.3) k = i;
      const at = k ? w('path', k) - 0.3 : s('path');
      const x = k ? eIO(pr(t, at, 0.36)) : spring(t, s('path') - 0.05, 12);
      const pos = k ? vl(topOf(k - 1), topOf(k), x).add(V(0, hop(x, 0.5), 0)) : topOf(0);
      return put(pos, k ? 0.46 : 0.46 * x, sway + (k ? Math.PI * 2 * x : 0), 0.05);
    }
    if (t < s('cta') - 0.05) return put(center, 0);
    const into = W(CTA, 0, 1.42, 0.1);                           // финал: падает сверху и ныряет в логотип Telegram
    const x1 = eExpo(pr(t, s('cta') + 0.05, 0.4)), x2 = eIn(pr(t, s('cta') + 0.4, 0.38));
    return put(vl(vl(W(CTA, 0, 6, 0.6), W(CTA, 0, 3.1, 0.6), x1), into, x2), lerp(lerp(0.6, 0.9, x1), 0, x2), t * 2.5, 0.1);
  };

  // ── Камера: стоит у станции, на смене переезжает к следующей, внутри станции чуть наезжает ──────────
  const pose = (st, t) => {
    const punch = 1 - 0.05 * pr(t, st.a, st.b - st.a);
    let p = st.p.clone(), l = st.l.clone();
    if (st.name === 'code') { const up = eIO(pr(t, s('self') - 0.1, 0.6)); p = vl(p, V(0, 7.0, 6.4), up); l = vl(l, V(0, 0.45, 0.3), up); }
    if (st.name === 'msg') { const x = eIO(pr(t, s('who') - 0.05, 0.6)); p.x += 0.2 * x; l.x += 0.2 * x; }
    if (st.name === 'team') { const back = eIO(pr(t, s('much') - 0.05, 0.75)); p = vl(p, V(0, 8.6, 13.5), back); l = vl(l, V(0, 0.2, 0), back); p.x += 0.5 * Math.sin((t - st.a) * 0.25); }
    p = l.clone().add(p.sub(l).multiplyScalar(punch));
    return { p: p.add(V(st.x, 0, 0)), l: l.add(V(st.x, 0, 0)) };
  };
  const placeCamera = (t) => {
    let k = 0; ST.forEach((st, i) => { if (t >= st.a - 0.05) k = i; });
    const cur = pose(ST[k], t);
    let p = cur.p, l = cur.l;
    if (k > 0) {
      const x = eIO(pr(t, ST[k].a - 0.05, 0.5));
      if (x < 1) { const prev = pose(ST[k - 1], t); p = vl(prev.p, p, x); l = vl(prev.l, l, x); }
    }
    camera.position.copy(p); camera.lookAt(l);
    key.position.copy(l).add(V(-3, 8, 8)); key.target.position.copy(l);
    return k;
  };

  // ── Кадр ─────────────────────────────────────────────────────────────────────────────────────────
  let tMain = 0;                                         // время самого кадра: по нему лавина и счётчик, без размытия
  const frame = (t) => {
    const k = placeCamera(t);
    ST.forEach((st, i) => { st.g.visible = Math.abs(i - k) <= 1; });
    heroAt(t);

    // 1–2. сообщения
    {
      const up = s('who');
      const out = eIO(pr(t, up, 0.55));
      FLOOD.forEach((f) => {
        const tf = tMain;                                                 // вопросы читаются в полёте: без размытия
        const x = pr(tf, f.ts, 0.62);
        const sweep = eIn(pr(tf, up + (f.k % 12) * 0.025, 0.5));         // на «Отвечаю» гора уезжает вглубь и тает
        f.b.visible = tf >= f.ts && sweep < 0.99;
        if (!f.b.visible) return;
        const fall = x * x;                                               // падение с разгоном
        const settle = 0.05 * Math.sin(Math.PI * pr(tf, f.ts + 0.62, 0.16));
        f.b.position.copy(vl(f.from, f.rest, fall)).add(V(0, settle, 0)).add(V(f.rest.x * 0.5 * sweep, -1.1 * sweep, -2.6 * sweep));
        const tumble = (1 - x) * f.spin;
        f.b.rotation.set(lerp(-0.12, f.rx, x * x), f.ry + tumble * 0.25, f.rz + tumble);   // в полёте лицом к камере, кувыркается вбок
        f.b.scale.setScalar(Math.max(0.001, 1 - sweep));
      });
      const arrived = FLOOD.filter((f) => tMain >= f.ts + 0.5).length;
      const cnt = Math.round(9 + arrived * 0.95);
      drawBadge(cnt > 99 ? '99+' : String(cnt));
      badge.scale.setScalar(1 + 0.12 * Math.sin(Math.PI * pr(tMain % 0.25, 0, 0.12)) * (tMain < up ? 1 : 0));
      const a = spring(t, w('hook', 3) - 0.14, 13);
      ask.position.copy(vl(V(0, 1.4, -0.3), V(0, 1.75, 2.1), a)).add(V(0.25 * out, 0.45 * out, -0.4 * out));
      ask.scale.setScalar(Math.max(0.001, a * (1 - 0.18 * out)));
      ask.rotation.set(-0.1, 0, 0);
      msgPhone.g.position.set(-1.3 * out, 1.18, -0.4 - 0.4 * out); msgPhone.g.rotation.y = 0.12 + 0.45 * out;
      const nb = spring(t, w('who', 1) - 0.08, 15);
      nobody.position.set(-0.15 + 0.1 * (1 - nb), 1.5, 1.5); nobody.scale.setScalar(Math.max(0.001, nb)); nobody.rotation.set(-0.08, 0.1, 0);
      const pd = spring(t, w('who', 2) - 0.45, 12);
      whoPed.position.set(0.95, 0.21 - 0.6 * (1 - pd), 0.75); whoPed.visible = pd > 0.01;
      const cp = spring(t, w('who', 3) - 0.05, 13);
      codePlate.position.set(0.95, 0.3 + 0.25 * cp, 1.55); codePlate.rotation.x = -0.35; codePlate.scale.setScalar(Math.max(0.001, cp));
    }

    // 3–4. код и монтаж
    {
      const t0 = s('code'), sw = w('code', 7) - 0.1, sel = s('self');
      const g0 = spring(t, t0 - 0.05, 12);
      gen.scale.setScalar(Math.max(0.001, g0));
      const hit = pr(t, w('code', 5) - 0.12, 0.3);
      strikeBar.visible = hit > 0;
      const fall = eIn(pr(t, w('code', 6) - 0.05, 0.5));
      strikeBar.position.set(lerp(3.6, -0.15, eOut(hit)), lerp(2.6, 0.95, eOut(hit)) - fall * 0.7, 0.05 - 0.5 + fall * 0.3);
      strikeBar.rotation.set(0, 0, lerp(1.1, 0.55, eOut(hit)) + fall * 0.4);
      genPivot.rotation.x = -1.48 * fall;
      if (t > sel + 0.4) { gen.visible = false; strikeBar.visible = false; } else gen.visible = true;
      // планшет с кодом встаёт из пола; строки печатаются; на «сам собирает» ложится и уступает место столу
      const rise = spring(t, sw, 10);
      const lie = eIO(pr(t, sel - 0.15, 0.55));
      tablet.visible = rise > 0.01 && lie < 0.98;
      tablet.position.set(0, lerp(-1.0, 1.15, rise) - lie * 1.0, 0.1 + lie * 0.4);
      tablet.rotation.set(-0.12 - lie * 1.4, 0, 0);
      tablet.scale.setScalar(1 - 0.4 * lie);
      const typed = (t - (sw + 0.25)) / 0.13;
      drawCode(Math.max(-1, Math.min(5, Math.floor(typed))), cl(typed - Math.floor(typed)));
      const bd = spring(t, sel + 0.05, 11);
      board.visible = bd > 0.01; board.scale.setScalar(Math.max(0.001, bd * 0.8)); board.position.set(0, 0, 0.35);
      const a = sel + 0.35, b = e('self') - 0.45;
      playhead.position.x = -1.55 + 3.15 * cl((t - a) / (b - a));
      const pv = spring(t, sel + 0.15, 11);
      preview.g.visible = false; preview.g.scale.setScalar(Math.max(0.001, pv));
      preview.scr.material.map = t < a + (b - a) * 0.36 ? REAL.s1 : t < a + (b - a) * 0.7 ? REAL.s2 : REAL.s3;
      const dn = spring(t, b - 0.05, 14);
      doneP.visible = dn > 0.01; doneP.scale.setScalar(Math.max(0.001, dn)); doneP.position.set(0, 0.55, 1.3); doneP.rotation.x = -0.9;
    }

    // 5. хайп
    {
      const a = s('hype'), b = e('hype');
      const wd = spring(t, a + 0.2, 11);
      word.scale.setScalar(Math.max(0.001, wd)); word.rotation.set(-0.25 - (1 - wd) * 1.2, 0, 0);
      HEARTS.forEach((h) => {
        const st = a + 0.05 + h.d * (b - a - 1.0);
        const x = pr(t, st, 1.7);
        h.m.visible = x > 0 && x < 1;
        h.m.position.set(h.x, lerp(0.2, 3.6, eOut(x)), h.z);
        h.m.scale.setScalar(Math.max(0.001, h.sz * (0.5 + 0.5 * eExpo(x * 4)) * (1 - eIn(pr(x, 0.8, 0.2)))));
        h.m.rotation.set(0.3 * Math.sin(t * 2 + h.d * 6), Math.sin(t * 1.3 + h.d * 4) * 0.8, 0.2 * Math.sin(t * 1.5));
      });
    }

    // 6. «сделай ролик»
    {
      const a0 = s('try'), ta = w('try', 4), tb = w('try', 6) + 0.35, click = w('try', 7);
      const i0 = spring(t, a0, 12);
      inp.position.set(0, lerp(1.4, 2.25, i0), 0.4); inp.rotation.x = -0.22; inp.scale.setScalar(Math.max(0.001, i0 * 0.82));
      const n = Math.max(0, Math.min(12, Math.floor(((t - ta) / (tb - ta)) * 12)));
      drawInput(t < ta ? 0 : n, t < click && Math.floor(t * 2) % 2 === 0);
      const press = Math.sin(Math.PI * pr(t, click - 0.04, 0.16));
      send.position.z = 0.1 - 0.06 * press;
      const c1 = eIO(pr(t, tb - 0.25, Math.max(0.2, click - tb + 0.2)));
      cursor3.visible = t > tb - 0.3;
      cursor3.position.copy(vl(V(2.0, 0.6, 1.6), V(1.16, 2.1, 0.62), c1)).add(V(0, 0, -0.08 * press));
      cursor3.rotation.set(-0.3, 0, 0.35);
      const wt = spring(t, click + 0.15, 11);
      wait.visible = wt > 0.01; wait.scale.setScalar(Math.max(0.001, wt * 0.85)); wait.position.set(0, 0.85, 0.2); wait.rotation.x = -0.15;
      spinner.rotation.z = -(t - click) * 6;
    }

    // 7. нейрослоп
    {
      const a = s('slop');
      SLOP.g.rotation.y = 0.18 * Math.sin((t - a) * 0.6);
      const jump = Math.sin(Math.PI * pr(t, w('slop', 3) - 0.08, 0.42));
      SLOPS.forEach((o) => {
        const x = spring(t, a + o.k * 0.05, 12);
        o.g.scale.setScalar(Math.max(0.001, x));
        o.blob.position.y = 0.39 + 0.03 * Math.sin(t * 4) + jump * 0.5;
        o.blob.rotation.y = t * 1.5 + jump * Math.PI;
      });
      const sl = eIn(pr(t, w('slop', 0) - 0.22, 0.22));
      stamp.visible = t > w('slop', 0) - 0.25;
      stamp.position.set(0, lerp(5, 0.85, sl), lerp(0.5, 0.35, sl)); stamp.rotation.set(-0.95, 0, -0.12);
      const sq = Math.sin(Math.PI * pr(t, w('slop', 0) - 0.01, 0.16));
      stamp.scale.set(1 + 0.04 * sq, 1 - 0.1 * sq, 1);
    }

    // 8–9. стоп и «?»
    {
      const a = s('stop'), q = s('why');
      const sl = eIn(pr(t, a - 0.05, 0.26));
      const sink = eIn(pr(t, q - 0.05, 0.4));
      hand.visible = t > a - 0.08 && sink < 1;
      const sq = Math.sin(Math.PI * pr(t, a + 0.21, 0.18));
      hand.position.set(0, lerp(6, 1.95, sl) - sink * 3.2, -0.2); hand.scale.set(1 + 0.05 * sq, 1 - 0.08 * sq, 1);
      const m0 = spring(t, w('stop', 1) - 0.1, 12);
      model.visible = m0 > 0.01 && sink < 1; model.position.set(0, lerp(0.2, 0.7, m0) - sink * 2, 1.15); model.rotation.x = -0.3; model.scale.setScalar(Math.max(0.001, m0));
      const mk = eOut(pr(t, w('stop', 4) - 0.06, 0.3));
      mark.visible = mk > 0 && sink < 1; mark.position.set(lerp(-3.4, 0, mk), 0.7 - sink * 2, 1.27); mark.rotation.set(-0.3, 0, -0.05);
      const qa = spring(t, q + 0.02, 11), qs = eIn(pr(t, e('why') + 0.45, 0.3));   // «?» уезжает с переездом, а не тает заранее: без пустого кадра
      qm.visible = qa > 0.01 && qs < 0.999;
      qm.position.set(0, 1.45, 0.2); qm.scale.setScalar(Math.max(0.001, qa * (1 - qs))); qm.rotation.set(0, (1 - qa) * -1.4 + qs * 3, 0);
    }

    // 10–13. команда
    {
      const a = s('team');
      const draw = eIO(pr(t, a + 0.25, 0.8));
      THREADS.forEach((m) => { m.geometry.setDrawRange(0, Math.floor((m.geometry.index.count * draw) / 6) * 6); });
      AG.forEach((ag, i) => {
        const pop = spring(t, w('team', 7) - 0.12 + i * 0.07, 13);
        ag.body.scale.set(1, Math.max(0.001, pop), 1); ag.body.visible = pop > 0.01;
        ag.ped.scale.setScalar(0.6 + 0.4 * spring(t, a + 0.1 + i * 0.05, 12));
      });
      // «задача» переходит к агенту на слове его роли; принявший подпрыгивает, его постамент загорается лаймом
      const ROLE_T = [w('roles', 0), w('roles', 1), w('roles', 2), w('roles', 3), w('roles', 5)];
      let cur = -1; ROLE_T.forEach((rt, i) => { if (t >= rt - 0.3) cur = i; });
      const above = (i) => (i < 0 ? V(0, 1.85, 0.05) : AG[i].g.position.clone().add(V(0, 1.5, 0)));   // над головой кота, не на ней
      if (cur < 0) {
        const x = spring(t, ROLE_T[0] - 0.9, 12);
        task.visible = x > 0.01; task.position.copy(above(-1)); task.scale.setScalar(Math.max(0.001, x));
      } else {
        const x = eIO(pr(t, ROLE_T[cur] - 0.3, 0.32));
        task.visible = true; task.scale.setScalar(1);
        task.position.copy(vl(above(cur - 1), above(cur), x)).add(V(0, hop(x, 0.6), 0));
      }
      task.rotation.set(t * 0.9, t * 1.3, 0);
      AG.forEach((ag, i) => {
        const got = i <= cur ? eOut(pr(t, ROLE_T[i] - 0.02, 0.25)) : 0;
        ag.ped.material.color.set(C.ped).lerp(new THREE.Color(C.lime), got);
        ag.body.position.y = 0.16 + hop(pr(t, ROLE_T[i] - 0.02, 0.3), 0.18);
      });
      PLUGS.forEach((p, i) => {
        const at = w('skills', i ? 4 : 2) - 0.1;
        const x = spring(t, at, 12);
        p.g.visible = x > 0.01; p.g.position.copy(p.at).add(V(0, 0, 1.2 * (1 - x))); p.g.rotation.set(0.3, 0.6 * Math.sin(t + i), 0);
        const dr = eIO(pr(t, at + 0.25, 0.35));
        p.thread.visible = dr > 0; p.thread.geometry.setDrawRange(0, Math.floor((p.thread.geometry.index.count * dr) / 6) * 6);
      });
    }

    // 14–15. одинаковые ролики
    {
      const a = s('same');
      const jump = Math.sin(Math.PI * pr(t, w('same2', 2) - 0.08, 0.4));
      const flash = pr(t, w('same2', 6) - 0.05, 0.05) * (1 - pr(t, w('same2', 6) + 0.45, 0.05));
      const spin = eIO(pr(t, w('same2', 8) - 0.05, 0.7)) * Math.PI * 2;
      PH3.forEach((p, i) => {
        const x = spring(t, a + i * 0.08, 11);
        p.g.position.set([-1.0, 0, 1.0][i], 0.8 + jump * 0.35 - (1 - x) * 1.6, 0);
        p.g.rotation.set(0, 0.35 * Math.sin((t - a) * 1.6) + spin, 0);
        p.scr.material.map = flash > 0.5 ? scrB : scrA;
      });
    }

    // 16. референсы
    {
      const a = s('refs');
      const scroll = (t - a) * 0.9;
      REFT.forEach(({ tile, k: n }) => {
        const col = n % 3, row = Math.floor(n / 3);
        let y = 1.75 - row * 1.25 + scroll;
        y = (((y + 2.6) % 7.5) + 7.5) % 7.5 - 2.6;                 // по кругу, как бесконечная лента
        tile.position.set((col - 1) * 1.02, y - 0.95, 0.04);
        const edge = cl((1.95 - Math.abs(y - 0.85)) / 0.5);
        tile.visible = edge > 0.01; tile.scale.setScalar(Math.max(0.001, edge));
      });
      const c0 = spring(t, w('refs', 6) - 0.1, 12);
      clock.visible = c0 > 0.01; clock.scale.setScalar(Math.max(0.001, c0)); clock.position.set(0.9, 0.75, 1.5); clock.rotation.set(-0.15, -0.3, 0);
      handM.rotation.z = -(t - w('refs', 6)) * 9; handH.rotation.z = -(t - w('refs', 6)) * 1.2;
    }

    // 17. дизайнер переворачивает карточку
    {
      const a = s('design');
      const c0 = spring(t, a, 11);
      dCard.scale.setScalar(Math.max(0.001, c0));
      const FL = [w('design', 5), w('design', 7), w('design', 9)];
      let st = 0, rot = 0;
      FL.forEach((ft, i) => {
        const x = pr(t, ft - 0.25, 0.55);
        if (x >= 0.5) st = i + 1;
        if (x > 0 && x < 1) rot = x < 0.5 ? eIn(x * 2) * (Math.PI / 2) : -(1 - eOut((x - 0.5) * 2)) * (Math.PI / 2);
      });
      dCard.rotation.set(0, rot + 0.12 * Math.sin(t * 0.8), 0);
      dFace.material.map = STYLE[st];
      designer.wob = FL.reduce((acc, ft) => acc + 0.12 * Math.sin(Math.PI * pr(t, ft - 0.3, 0.4)), 0);
    }

    // 18. веер
    {
      const a = s('uniq');
      const spread = eIO(pr(t, w('uniq', 1) - 0.05, 0.7));
      const POS = [[-0.98, -0.05, -0.3, 0.55, 0.1], [0, 0.05, 0.3, 0, 0], [0.98, -0.05, -0.3, -0.55, -0.1]];
      FAN.forEach((p, i) => {
        const x = spring(t, a + i * 0.06, 11);
        const [px, py, pz, ry, rz] = POS[i];
        p.g.position.set(px * spread, 1.2 + py * spread - (1 - x) * 2, pz * spread);
        p.g.rotation.set(0, ry * spread + 0.06 * Math.sin(t * 0.9 + i), rz * spread);
      });
      const m0 = spring(t, w('uniq', 5) - 0.1, 13);
      made.visible = m0 > 0.01; made.scale.setScalar(Math.max(0.001, m0 * 0.9)); made.position.set(0, 0.42, 1.45); made.rotation.x = -0.12;
    }

    // 19. проверка
    {
      const a = s('check');
      const t0 = a + 0.45, tb = w('check', 5) - 0.05;
      const GAPc = 0.95, v = (BAD * GAPc) / (tb - t0);
      CARDS.forEach((c, i) => {
        const x = i * GAPc - v * (t - t0);
        const lift = i === BAD ? eExpo(pr(t, w('check', 6) - 0.1, 0.4)) : 0;
        const away = i === BAD ? eIn(pr(t, w('check', 7) - 0.05, 0.6)) : 0;
        c.g.position.set(x, 0.18 + 0.585 + lift * 0.5 - away * 1.2, 0.05 - away * 1.4);
        c.g.rotation.set(-away * 1.3, -0.25 * Math.max(-1, Math.min(1, x)), i === BAD ? lift * 0.15 : 0);
        const passed = t0 + (i * GAPc) / v;
        const bt = spring(t, passed, 15);
        c.badge.scale.setScalar(Math.max(0.001, bt)); c.badge.visible = bt > 0.01;
      });
      scan.position.y = 1.0 + 0.85 * Math.sin((t - a) * 4.2);
      inspector.wob = 0.04 * Math.sin(t * 2);
    }

    // 20. путь
    {
      const a = s('path');
      STEP.forEach((stp, i) => {
        const x = spring(t, a + i * 0.06, 12);
        stp.g.scale.set(1, Math.max(0.001, x), 1);
        const on = eExpo(pr(t, w('path', i) - 0.08, 0.3));
        stp.top.visible = on > 0.01; stp.top.scale.set(Math.max(0.001, on), 1, Math.max(0.001, on));
      });
    }

    // 21. коробка
    {
      const a = s('pack'), go = w('pack', 5) - 0.05;
      const b0 = spring(t, a + 0.05, 11);
      boxG.scale.setScalar(Math.max(0.001, b0)); boxG.rotation.y = -0.38 + 0.08 * Math.sin((t - a) * 0.8);
      ITEMS.forEach((it, i) => {
        const appear = spring(t, w('pack', [0, 1, 3][i]) - 0.1, 13);
        const fly = eIn(pr(t, go + i * 0.1, 0.5));
        it.g.visible = appear > 0.01 && fly < 0.98;
        it.g.position.copy(vl(it.at, mouth, fly)).add(V(0, hop(fly, 0.7), 0));
        it.g.scale.setScalar(Math.max(0.001, appear * (1 - 0.5 * fly)));
        it.g.rotation.set(0.15 + fly * 2, 0.4 * Math.sin(t + i) + fly * 3, 0);
        it.lb.visible = fly < 0.1;
      });
      lidPivot.rotation.x = lerp(-1.95, 0, eIO(pr(t, go + 0.6, 0.35)));
      sys.material.opacity = eOut(pr(t, w('pack', 7) - 0.1, 0.35));
    }

    // 22. финал
    {
      const a = s('cta');
      const pulse = Math.sin(Math.PI * pr(t, a + 0.72, 0.3));
      const t0 = spring(t, a - 0.05, 10);
      tg.scale.setScalar(Math.max(0.001, t0 * (1 + 0.12 * pulse))); tg.rotation.set(0, 0.25 * Math.sin(t * 0.9), 0);
      const ln = spring(t, w('cta', 3) - 0.15, 12);
      const click = w('cta', 3) + 0.1, press = Math.sin(Math.PI * pr(t, click - 0.04, 0.16));
      link.visible = ln > 0.01; link.scale.setScalar(Math.max(0.001, 0.8 * ln * (1 - 0.04 * press))); link.position.set(0, 0.38, 1.35); link.rotation.x = -0.35;
      const sv = spring(t, w('cta', 7) - 0.12, 13);
      bookmark.visible = sv > 0.01; bookmark.scale.setScalar(Math.max(0.001, sv)); bookmark.position.set(1.0, 1.05 + 0.06 * Math.sin(t * 2), 0.9); bookmark.rotation.set(0, -0.4 + 0.2 * Math.sin(t), 0);
      saveB.visible = sv > 0.01; saveB.scale.setScalar(Math.max(0.001, sv)); saveB.position.set(0.95, 1.7, 0.9); saveB.rotation.x = -0.1;
      const ct = spring(t, a + 0.55, 10);
      cat.visible = ct > 0.01; cat.position.set(-1.0, 0.72, 0.85); cat.scale.set(-Math.max(0.001, ct * 0.85), Math.max(0.001, ct * 0.85), 1);
      const c1 = eIO(pr(t, click - 0.5, 0.45)), c2 = eIO(pr(t, w('cta', 7) - 0.2, 0.4));
      cursorB.visible = t > click - 0.55;
      cursorB.position.copy(vl(vl(V(1.9, -0.2, 2.2), V(0.45, 0.38, 1.6), c1), V(1.08, 0.4, 1.45), c2)).add(V(0, 0, -0.06 * press));
      cursorB.rotation.set(-0.3, 0, 0.35);
    }

    // коты всегда лицом к камере (по горизонтали), покачивание — поверх
    CATS.forEach((ct) => {
      if (!ct.g.parent || !ct.g.parent.visible) return;
      const wp = new THREE.Vector3(); ct.body.getWorldPosition(wp);
      ct.body.lookAt(camera.position.x, wp.y, camera.position.z);
      if (ct.wob) ct.body.rotateZ(ct.wob);
    });
  };

  // ── Размытие движения внутри объёма ────────────────────────────────────────────────────────────────
  // На кадр сцена рисуется SUB раз в пределах половины кадра (затвор 180°) и усредняется: у летящих предметов гладкая
  // смазка, неподвижное резкое, заголовки поверх не размываются. Смешивание подкадров рендера на 120 и 240 к/с давало
  // «лесенку» из отдельных копий и двоило текст (проверено 14.10.2026), поэтому так.
  const SUB = 8, SHUTTER = 0.5 / 30;
  const rtSub = new THREE.WebGLRenderTarget(1080, 1920, { type: THREE.HalfFloatType, samples: 4 });
  const rtAcc = new THREE.WebGLRenderTarget(1080, 1920, { type: THREE.HalfFloatType });
  const quadCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const accScene = new THREE.Scene();
  accScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.MeshBasicMaterial({ map: rtSub.texture, transparent: true, opacity: 1 / SUB,
    blending: THREE.AdditiveBlending, depthTest: false, depthWrite: false, toneMapped: false })));
  const outScene = new THREE.Scene();
  outScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.MeshBasicMaterial({ map: rtAcc.texture, depthTest: false, depthWrite: false, toneMapped: true })));
  return (t) => {
    tMain = t;
    renderer.setRenderTarget(rtAcc); renderer.setClearColor(0x000000, 0); renderer.clear();
    for (let i = 0; i < SUB; i++) {
      frame(Math.max(0, t - (SHUTTER * i) / SUB));
      renderer.setRenderTarget(rtSub); renderer.render(scene, camera);
      renderer.setRenderTarget(rtAcc); renderer.autoClear = false; renderer.render(accScene, quadCam); renderer.autoClear = true;
    }
    renderer.setRenderTarget(null); renderer.render(outScene, quadCam);
  };
};
