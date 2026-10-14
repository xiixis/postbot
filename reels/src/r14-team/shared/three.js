// Объём ролика r14: одна сцена Three.js под вёрсткой, кадр считается из времени (событие hf-seek), не из часов.
//
// Сквозной герой — настоящий знак Claude (контур из public/team/brand/claude-color.svg), выдавленный с фаской:
// он приходит ответом на вопрос, «пишет» код, едет по дорожке монтажа, стоит в центре команды, поднимается
// по ступеням процесса и в финале ныряет в Telegram. Остальные предметы живут в своих окнах времени и
// появляются/уходят вместе со сценами вёрстки (те же 0,42 с входа и 0,26 с ухода).
// Координаты задаются в пикселях кадра 1080×1920 (P): камера с углом 30° на расстоянии 14 видит 256 px на единицу.

export const buildThree = async (THREE, X, canvas, T, A) => {
  const { SVGLoader, RoomEnvironment, RoundedBoxGeometry } = X;
  // надписи на холсте рисуются только загруженным шрифтом
  await Promise.all(['800 64px Unbounded', '700 40px Onest', '800 40px Onest'].map((f) => document.fonts.load(f)));

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(1080, 1920, false);
  renderer.setClearColor(0x000000, 0);
  renderer.toneMapping = THREE.NeutralToneMapping;
  renderer.toneMappingExposure = 0.95;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.45;
  const camera = new THREE.PerspectiveCamera(30, 1080 / 1920, 0.1, 200);
  const U = 256;
  const P = (x, y, z = 0) => new THREE.Vector3((x - 540) / U, (960 - y) / U, z);

  scene.add(new THREE.AmbientLight(0xffffff, 0.3));
  const key = new THREE.DirectionalLight(0xffffff, 2.3);
  key.position.set(-4, 7, 8);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -6, right: 6, top: 8, bottom: -8, near: 0.5, far: 40 });
  key.shadow.bias = -0.0005;
  scene.add(key);
  const rim = new THREE.PointLight(0xC7E24B, 55, 30);
  rim.position.set(3, 3, -5);
  scene.add(rim);
  const fill = new THREE.PointLight(0xFFE2D0, 18, 30);
  fill.position.set(-4, -3, 5);
  scene.add(fill);

  // время сценария
  const s = (id) => T.scenes[id].s, e = (id) => T.scenes[id].e, w = (id, i) => T.w[id][i];
  const cl = (x) => Math.max(0, Math.min(1, x));
  const pr = (t, a, d) => cl((t - a) / d);
  const eOut = (x) => 1 - Math.pow(1 - x, 3);
  const eExpo = (x) => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x));
  const eIO = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
  const eIn = (x) => x * x * x;
  const lerp = (a, b, x) => a + (b - a) * x;
  const vlerp = (a, b, x) => a.clone().lerp(b, x);
  // окно сцены: вход 0,42 с, уход 0,26 с — как у вёрстки
  const win = (t, a, b, last = false) => eOut(pr(t, a - 0.04, 0.42)) * (last ? 1 : 1 - eIn(pr(t, b - 0.22, 0.26)));

  // материалы и прозрачность
  const mats = [];
  const M = (o) => { const m = new THREE.MeshPhysicalMaterial({ transparent: true, ...o }); m.userData.op = o.opacity ?? 1; mats.push(m); return m; };
  const fade = (obj, o) => {
    obj.visible = o > 0.003;
    obj.traverse((n) => {
      const list = n.material ? (Array.isArray(n.material) ? n.material : [n.material]) : [];
      list.forEach((m) => { if (m.userData.op === undefined) m.userData.op = m.opacity; m.opacity = m.userData.op * o; m.transparent = true; });
    });
  };
  const shadowed = (mesh) => { mesh.castShadow = true; return mesh; };

  // текстуры: значки Phosphor контурами Path2D, надписи — загруженным шрифтом
  const icon = (name, set = 'b') => (set === 'f' ? FILL : set === 'r' ? ICONS : BOLD)[name];
  const pathsOf = (svg) => [...svg.matchAll(/\sd="([^"]+)"/g)].map((m) => m[1]);
  const tex = (cv) => { const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; };
  const iconTex = (name, fg, set = 'b', size = 256) => {
    const cv = document.createElement('canvas'); cv.width = cv.height = size;
    const g = cv.getContext('2d');
    g.fillStyle = fg;
    g.scale(size / 256, size / 256);
    pathsOf(icon(name, set)).forEach((d) => g.fill(new Path2D(d)));
    return tex(cv);
  };
  const textTex = (text, font, color, h = 96) => {
    const cv = document.createElement('canvas');
    const g0 = cv.getContext('2d'); g0.font = font;
    const wpx = Math.ceil(g0.measureText(text).width) + 40;
    cv.width = wpx; cv.height = h;
    const g = cv.getContext('2d');
    g.font = font; g.fillStyle = color; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(text, wpx / 2, h / 2 + 2);
    return { map: tex(cv), w: wpx, h };
  };
  const label = (text, color = '#F1F2EA', px = 34, weight = 700) => {
    const { map, w: tw, h } = textTex(text, `${weight} ${px * 2}px Onest`, color, Math.round(px * 2.8));
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map, transparent: true, depthWrite: false }));
    sp.scale.set(tw / 2 / U, h / 2 / U, 1);
    return sp;
  };
  const loader = new THREE.TextureLoader();
  const img = async (file) => { const t = await loader.loadAsync(`${A}/${file}`); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; };
  const [fan1, fan2, fan3, ...strip] = await Promise.all(['fan1', 'fan2', 'fan3', 's1', 's2', 's4', 's6', 's5', 's3', 's7'].map((f) => img(`real/${f}.jpg`)));

  // ── Герой: знак Claude ─────────────────────────────────────────────────────────────────────────────
  const sparkShapes = new SVGLoader().parse(`<svg viewBox="0 0 24 24"><path d="${BRAND.spark}"/></svg>`).paths.flatMap((p) => SVGLoader.createShapes(p));
  const sparkGeo = new THREE.ExtrudeGeometry(sparkShapes, { depth: 1.1, bevelEnabled: true, bevelThickness: 0.35, bevelSize: 0.22, bevelSegments: 8, curveSegments: 10 });
  sparkGeo.center();
  sparkGeo.scale(1 / 24, -1 / 24, 1 / 24);
  sparkGeo.computeVertexNormals();
  const sparkMat = () => M({ color: 0xD97757, roughness: 0.38, metalness: 0, clearcoat: 0.8, clearcoatRoughness: 0.2 });
  const hero = shadowed(new THREE.Mesh(sparkGeo, sparkMat()));
  scene.add(hero);

  // ── Сердца хайпа ──────────────────────────────────────────────────────────────────────────────────
  const hs = new THREE.Shape();
  hs.moveTo(0.25, 0.25); hs.bezierCurveTo(0.25, 0.25, 0.2, 0, 0, 0); hs.bezierCurveTo(-0.3, 0, -0.3, 0.35, -0.3, 0.35);
  hs.bezierCurveTo(-0.3, 0.55, -0.1, 0.77, 0.25, 0.95); hs.bezierCurveTo(0.6, 0.77, 0.8, 0.55, 0.8, 0.35);
  hs.bezierCurveTo(0.8, 0.35, 0.8, 0, 0.5, 0); hs.bezierCurveTo(0.35, 0, 0.25, 0.25, 0.25, 0.25);
  const heartGeo = new THREE.ExtrudeGeometry(hs, { depth: 0.22, bevelEnabled: true, bevelThickness: 0.08, bevelSize: 0.06, bevelSegments: 6, curveSegments: 16 });
  heartGeo.center(); heartGeo.rotateZ(Math.PI); heartGeo.scale(0.9, 0.9, 0.9);
  const rnd = (k) => { const x = Math.sin(k * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  const HEART_COL = [0xD97757, 0x56690C, 0x2A2B24, 0xD97757, 0xC7E24B];
  const hearts = new THREE.Group(); scene.add(hearts);
  const HEARTS = Array.from({ length: 14 }, (_, k) => {
    const m = shadowed(new THREE.Mesh(heartGeo, M({ color: HEART_COL[k % HEART_COL.length], roughness: 0.32, clearcoat: 0.7, clearcoatRoughness: 0.2 })));
    hearts.add(m);
    const side = k % 2 ? 1 : -1;
    return { m, x: 540 + side * (220 + rnd(k + 3) * 260), d: rnd(k + 9), size: 70 + rnd(k + 17) * 70, z: -0.5 + rnd(k + 21) * 1.4, spin: (rnd(k + 5) - 0.5) * 3 };
  });

  // ── Нейрослоп: девять одинаковых плиток с одинаковым шаром ───────────────────────────────────────────
  const slop = new THREE.Group(); scene.add(slop);
  slop.position.copy(P(540, 930)); slop.rotation.x = 0.9;
  const tileGeo = new RoundedBoxGeometry(0.82, 0.16, 0.82, 4, 0.06);
  const blobGeo = new THREE.SphereGeometry(0.25, 48, 32);
  const SLOP = [];
  for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
    const g = new THREE.Group();
    g.position.set((c - 1) * 0.98, 0, (r - 1) * 0.98);
    const tile = shadowed(new THREE.Mesh(tileGeo, M({ color: 0xBFBEB6, roughness: 0.7 })));
    tile.receiveShadow = true;
    const blob = shadowed(new THREE.Mesh(blobGeo, M({ color: 0xBDB6D6, roughness: 0.45, clearcoat: 0.5 })));
    blob.scale.set(1, 0.85, 1);
    g.add(tile, blob);
    slop.add(g);
    SLOP.push({ g, blob, k: r + c });
  }
  const floor = (w2, h2, op = 0.22) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w2, h2), new THREE.ShadowMaterial({ opacity: op, transparent: true })); m.receiveShadow = true; return m; };
  const slopFloor = floor(6, 6); slopFloor.rotation.x = -Math.PI / 2; slopFloor.position.y = -0.085; slop.add(slopFloor);

  // ── Команда: кольцо вокруг Claude, пять ролей, скилы и MCP ─────────────────────────────────────────
  const team = new THREE.Group(); scene.add(team);
  const RING_R = 1.3;
  const ringPts = Array.from({ length: 241 }, (_, i) => { const a = (i / 240) * Math.PI * 2; return new THREE.Vector3(Math.cos(a) * RING_R, Math.sin(a) * RING_R, 0); });
  const ringLine = new THREE.Line(new THREE.BufferGeometry().setFromPoints(ringPts), new THREE.LineBasicMaterial({ color: 0xC7E24B, transparent: true, opacity: 0.55 }));
  const orbit = new THREE.Group(); orbit.rotation.x = 0.85; orbit.position.copy(P(540, 940)); orbit.add(ringLine); team.add(orbit);
  const nodeGeo = new RoundedBoxGeometry(0.54, 0.54, 0.54, 4, 0.11);
  const ROLES = [['pencil-simple-line', 'сценарист'], ['palette', 'дизайнер'], ['film-strip', 'монтажёр'], ['waveform', 'звукорежиссёр'], ['eye', 'проверяющий']];
  const NODES = ROLES.map(([ic, name]) => {
    const g = new THREE.Group();
    const box = shadowed(new THREE.Mesh(nodeGeo, M({ color: 0x24251E, roughness: 0.35, clearcoat: 0.6 })));
    const face = new THREE.Mesh(new THREE.PlaneGeometry(0.36, 0.36), new THREE.MeshBasicMaterial({ map: iconTex(ic, '#12130F'), transparent: true, opacity: 0, toneMapped: false }));
    face.position.z = 0.276;
    const lab = label(name);
    lab.position.set(0, -0.5, 0.3);
    g.add(box, face, lab);
    team.add(g);
    return { g, box, face, lab };
  });
  const PLUGS = [['puzzle-piece', 'скилы', P(370, 1370)], ['plug', 'MCP', P(710, 1370)]].map(([ic, name, at]) => {
    const g = new THREE.Group();
    const box = shadowed(new THREE.Mesh(new RoundedBoxGeometry(0.46, 0.46, 0.46, 4, 0.1), M({ color: 0xC7E24B, roughness: 0.35, clearcoat: 0.6 })));
    const face = new THREE.Mesh(new THREE.PlaneGeometry(0.3, 0.3), new THREE.MeshBasicMaterial({ map: iconTex(ic, '#12130F'), transparent: true, toneMapped: false }));
    face.position.z = 0.236;
    const lab = label(name, '#F1F2EA', 32); lab.position.set(0, -0.42, 0.3);
    g.add(box, face, lab);
    g.position.copy(at);
    team.add(g);
    const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([at.clone().add(new THREE.Vector3(0, 0.26, 0)), P(540, 940)]),
      new THREE.LineBasicMaterial({ color: 0xC7E24B, transparent: true, opacity: 0.7 }));
    team.add(line);
    return { g, at, line };
  });

  // ── Одинаковые ролики: три одинаковых телефона ─────────────────────────────────────────────────────
  const phoneScreen = (lime) => {
    const cv = document.createElement('canvas'); cv.width = 420; cv.height = 760;
    const g = cv.getContext('2d');
    const gr = g.createLinearGradient(0, 0, 0, 760); gr.addColorStop(0, '#3A3B33'); gr.addColorStop(1, '#22231C');
    g.fillStyle = gr; g.fillRect(0, 0, 420, 760);
    g.fillStyle = 'rgba(241,242,234,.82)';
    g.beginPath(); g.arc(210, 270, 72, 0, Math.PI * 2); g.fill();
    g.beginPath(); g.roundRect(100, 360, 220, 230, [110, 110, 20, 20]); g.fill();
    g.fillStyle = lime ? '#C7E24B' : '#FFFFFF';
    g.beginPath(); g.roundRect(46, 610, 328, 96, 22); g.fill();
    g.fillStyle = '#8E9080';
    g.beginPath(); g.roundRect(76, 636, 268, 16, 8); g.fill();
    g.beginPath(); g.roundRect(76, 664, 170, 16, 8); g.fill();
    g.fillStyle = '#E8C468'; g.scale(0.36, 0.36); g.translate(860, 90);
    pathsOf(icon('sparkle', 'f')).forEach((d) => g.fill(new Path2D(d)));
    return tex(cv);
  };
  const scrA = phoneScreen(false), scrB = phoneScreen(true);
  const phoneGeo = (wd, ht) => new RoundedBoxGeometry(wd, ht, 0.09, 4, 0.07);
  const makePhone = (map, wd, ht) => {
    const g = new THREE.Group();
    const body = shadowed(new THREE.Mesh(phoneGeo(wd, ht), M({ color: 0x15160F, roughness: 0.3, clearcoat: 1, clearcoatRoughness: 0.1 })));
    const scr = new THREE.Mesh(new THREE.PlaneGeometry(wd - 0.07, ht - 0.07), new THREE.MeshBasicMaterial({ map, transparent: true, toneMapped: false }));
    scr.position.z = 0.047;
    g.add(body, scr);
    return { g, scr };
  };
  const same = new THREE.Group(); scene.add(same);
  const SAME = [270, 540, 810].map((x) => { const p = makePhone(scrA, 0.92, 1.66); p.g.position.copy(P(x, 790)); same.add(p.g); return p; });
  const sameWall = floor(8, 6, 0.2); sameWall.position.set(0, P(0, 790).y, -0.7); same.add(sameWall);

  // ── Веер: три настоящих ролика канала ──────────────────────────────────────────────────────────────
  const uniq = new THREE.Group(); scene.add(uniq);
  const FAN = [fan1, fan2, fan3].map((map) => { const p = makePhone(map, 1.2, 2.13); uniq.add(p.g); return p; });
  const uniqWall = floor(9, 7, 0.18); uniqWall.position.set(0, P(0, 860).y, -1.1); uniq.add(uniqWall);

  // ── Проверка: лента кадров на конвейере, рамка-сканер, галочки и крест ──────────────────────────────
  const check = new THREE.Group(); scene.add(check);
  const CARDS = strip.map((map) => { const p = makePhone(map, 0.74, 1.32); check.add(p.g); return p; });
  const gate = new THREE.Group();
  const gm = new THREE.MeshBasicMaterial({ color: 0xC7E24B, transparent: true, toneMapped: false });
  [[0.96, 0.05, 0, 0.78], [0.96, 0.05, 0, -0.78], [0.05, 1.6, 0.46, 0], [0.05, 1.6, -0.46, 0]].forEach(([a, b, x, y]) => {
    const m = new THREE.Mesh(new RoundedBoxGeometry(a, b, 0.05, 2, 0.02), gm); m.position.set(x, y, 0.15); gate.add(m);
  });
  const scanBar = new THREE.Mesh(new THREE.PlaneGeometry(0.86, 0.025), gm); scanBar.position.z = 0.16; gate.add(scanBar);
  gate.position.copy(P(540, 1030)); check.add(gate);
  const badge = (name, bg) => {
    const cv = document.createElement('canvas'); cv.width = cv.height = 160;
    const g = cv.getContext('2d'); g.fillStyle = bg; g.beginPath(); g.arc(80, 80, 76, 0, Math.PI * 2); g.fill();
    g.fillStyle = bg === '#C7E24B' ? '#12130F' : '#FFFFFF'; g.translate(28, 28); g.scale(104 / 256, 104 / 256);
    pathsOf(icon(name, 'b')).forEach((d) => g.fill(new Path2D(d)));
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex(cv), transparent: true, depthWrite: false }));
    sp.scale.set(0.3, 0.3, 1);
    return sp;
  };
  const BAD = 3;
  const BADGES = CARDS.map((c, k) => { const b = badge(k === BAD ? 'x' : 'check', k === BAD ? '#E5544B' : '#C7E24B'); b.position.set(0.3, 0.6, 0.12); c.g.add(b); return b; });

  // ── Путь: пять ступеней, знак Claude поднимается по ним ─────────────────────────────────────────────
  const path = new THREE.Group(); scene.add(path);
  const STEPS = ['lightbulb', 'pencil-simple-line', 'microphone', 'film-strip', 'eye'];
  const STEP_Y = (k) => 1320 - k * 175;
  const stepGeo = new RoundedBoxGeometry(0.64, 0.64, 0.64, 4, 0.1);
  const STEP = STEPS.map((ic, k) => {
    const g = new THREE.Group();
    const box = shadowed(new THREE.Mesh(stepGeo, M({ color: 0x2B3620, roughness: 0.4, clearcoat: 0.5 })));
    box.receiveShadow = true;
    const off = new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.4), new THREE.MeshBasicMaterial({ map: iconTex(ic, 'rgba(241,242,234,0.55)'), transparent: true, toneMapped: false }));
    const on = new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.4), new THREE.MeshBasicMaterial({ map: iconTex(ic, '#12130F'), transparent: true, opacity: 0, toneMapped: false }));
    off.position.z = on.position.z = 0.326;
    g.add(box, off, on);
    g.position.copy(P(300, STEP_Y(k)));
    g.rotation.set(-0.18, 0.5, 0);
    path.add(g);
    return { g, box, off, on };
  });

  // ── Папка: агенты, скилы и настройки улетают в коробку «система» ────────────────────────────────────
  const pack = new THREE.Group(); scene.add(pack);
  const boxG = new THREE.Group(); boxG.position.copy(P(540, 1190)); boxG.rotation.set(0.38, -0.42, 0); pack.add(boxG);
  const olive = () => M({ color: 0x56690C, roughness: 0.55, clearcoat: 0.3 });
  const BW = 1.7, BH = 0.95, BD = 1.25, TH = 0.06;
  [[BW, TH, BD, 0, -BH / 2, 0], [BW, BH, TH, 0, 0, BD / 2], [BW, BH, TH, 0, 0, -BD / 2], [TH, BH, BD, BW / 2, 0, 0], [TH, BH, BD, -BW / 2, 0, 0]]
    .forEach(([a, b, c, x, y, z]) => { const m = shadowed(new THREE.Mesh(new RoundedBoxGeometry(a, b, c, 2, 0.025), olive())); m.position.set(x, y, z); m.receiveShadow = true; boxG.add(m); });
  const lidPivot = new THREE.Group(); lidPivot.position.set(0, BH / 2, -BD / 2); boxG.add(lidPivot);
  const lid = shadowed(new THREE.Mesh(new RoundedBoxGeometry(BW + 0.06, TH, BD + 0.04, 2, 0.025), olive())); lid.position.set(0, 0, BD / 2); lidPivot.add(lid);
  const sysTex = textTex('система', '800 120px Unbounded', '#F1F2EA', 170);
  const sysFace = new THREE.Mesh(new THREE.PlaneGeometry(sysTex.w / 470, sysTex.h / 470), new THREE.MeshBasicMaterial({ map: sysTex.map, transparent: true, opacity: 0, toneMapped: false }));
  sysFace.position.set(0, 0, BD / 2 + 0.036); boxG.add(sysFace);
  const packFloor = floor(8, 8, 0.2); packFloor.rotation.x = -Math.PI / 2; packFloor.position.y = -BH / 2 - 0.03; boxG.add(packFloor);
  const ITEMS = [['users-three', 'агенты', P(300, 620)], ['puzzle-piece', 'скилы', P(780, 620)], ['gear', 'настройки', P(540, 800)]].map(([ic, name, at]) => {
    const g = new THREE.Group();
    const box = shadowed(new THREE.Mesh(new RoundedBoxGeometry(0.5, 0.5, 0.5, 4, 0.1), M({ color: 0xC7E24B, roughness: 0.35, clearcoat: 0.6 })));
    const face = new THREE.Mesh(new THREE.PlaneGeometry(0.32, 0.32), new THREE.MeshBasicMaterial({ map: iconTex(ic, '#12130F'), transparent: true, toneMapped: false }));
    face.position.z = 0.256;
    const lab = label(name, '#12130F', 32, 800); lab.position.set(0, -0.44, 0.3);
    g.add(box, face, lab);
    g.position.copy(at);
    pack.add(g);
    return { g, at, lab };
  });
  const boxMouth = P(540, 1190).add(new THREE.Vector3(0, 0.25, 0));

  // ── Герой по времени ──────────────────────────────────────────────────────────────────────────────
  const hide = () => { hero.visible = false; };
  const put = (pos, sizePx, ry, rx = 0.12, op = 1) => {
    hero.visible = op > 0.003;
    hero.position.copy(pos);
    hero.scale.setScalar(sizePx / U);
    hero.rotation.set(rx, ry, 0);
    fade(hero, op);
  };
  // бегунок дорожки: плоский x 268…958, но дорожки наклонены (rotateX 24° у .t-edit), верх уходит вглубь: ×0,952 к центру
  const headX = (t) => { const a = s('self') + 0.35, b = e('self') - 0.45; return 540 + (268 + 690 * cl((t - a) / (b - a)) - 540) * 0.952; };
  const heroAt = (t) => {
    const tw = w('who', 2) - 0.15;
    if (t < tw) return hide();
    const sway = 0.28 * Math.sin(t * 1.1);
    // 2. ответ: знак прилетает из глубины, крутясь, и встаёт над надписью Claude
    const whoPos = P(540, 1060);
    if (t < s('code') - 0.25) {
      const x = eExpo(pr(t, tw, 0.9));
      return put(vlerp(P(540, 1060, -30), whoPos, x), 300, lerp(-7, 0, x) + sway, 0.15 * Math.sin(t * 0.8));
    }
    // 3. «пишет код»: знак уходит в угол карточки и на «Он пишет» быстро крутится
    const codePos = P(910, 520);
    if (t < s('self') - 0.15) {
      const x = eIO(pr(t, s('code') - 0.25, 0.6));
      const spin = eIO(pr(t, w('code', 7), 1.4)) * Math.PI * 4;
      const bob = 0.05 * Math.sin(t * 6) * pr(t, w('code', 7), 0.2);
      return put(vlerp(whoPos, codePos, x).add(new THREE.Vector3(0, bob, 0)), lerp(300, 130, x), sway * (1 - x) + spin, 0.12);
    }
    // 4. едет по дорожке монтажа вместе с бегунком
    if (t < s('hype') - 0.25) {
      const x = eIO(pr(t, s('self') - 0.15, 0.5));
      return put(vlerp(codePos, P(headX(t), 995), x), lerp(130, 84, x), 0.6 * Math.sin(t * 3), 0.1);
    }
    // 5. хайп: крупно в центре, вращается
    if (t < e('hype')) {
      const x = eIO(pr(t, s('hype') - 0.25, 0.6));
      const op = 1 - eIn(pr(t, e('hype') - 0.22, 0.26));
      return put(vlerp(P(headX(t), 995), P(540, 640), x), lerp(84, 400, x), 0.55 * Math.sin(t * 0.9), 0.18 * Math.sin(t * 0.9), op);
    }
    // 10–13. команда: выходит из точки «?» в центр кольца
    if (t >= s('team') - 0.1 && t < e('much')) {
      const x = eExpo(pr(t, s('team') - 0.1, 0.8));
      const op = 1 - eIn(pr(t, e('much') - 0.22, 0.26));
      return put(P(540, 940, lerp(-1.5, 0, x)), lerp(40, 205, x), 0.5 * Math.sin(t * 0.7), 0.15, op * cl(x * 3));
    }
    // 20. путь: стоит на ступени и прыгает на следующую на её слове
    if (t >= s('path') - 0.04 && t < e('path')) {
      const top = (k) => P(160, STEP_Y(k), 0.45);
      let k = 0;
      for (let i = 1; i < 5; i++) if (t >= w('path', i) - 0.3) k = i;
      const at = k ? w('path', k) - 0.3 : s('path');
      const x = k ? eIO(pr(t, at, 0.36)) : 1;
      const from = top(Math.max(0, k - 1)), to = top(k);
      const pos = vlerp(from, to, x).add(new THREE.Vector3(0, Math.sin(Math.PI * x) * (k ? 0.45 : 0), 0));
      const op = win(t, s('path'), e('path'));
      return put(pos, 110, 0.45 * Math.sin(t * 1.5) + (k ? Math.PI * 2 * x : 0), 0.12, op);
    }
    // 22. финал: знак падает сверху и ныряет в значок Telegram на карточке
    if (t >= s('cta') - 0.1 && t < s('cta') + 0.75) {
      const x1 = eExpo(pr(t, s('cta') - 0.1, 0.35)), x2 = eIn(pr(t, s('cta') + 0.25, 0.45));
      const pos = vlerp(vlerp(P(540, 300, 2), P(540, 900), x1), P(236, 616, -0.3), x2);
      return put(pos, lerp(lerp(160, 320, x1), 30, x2), t * 3, 0.15, 1 - pr(t, s('cta') + 0.62, 0.1));
    }
    return hide();
  };

  // ── Кадр ──────────────────────────────────────────────────────────────────────────────────────────
  const BASE_CAM = new THREE.Vector3(0, 0, 14);
  const ORIGIN = new THREE.Vector3(0, 0, 0);
  return (t) => {
    // камера: на месте; в команде медленно облетает кольцо, на «Зачем столько?» отъезжает; в веере — наезд
    camera.position.copy(BASE_CAM);
    let look = ORIGIN.clone();
    if (t > s('team') - 0.3 && t < e('much') + 0.1) {
      const k = t - s('team');
      const back = eIO(pr(t, s('much') - 0.05, 0.7));
      const c = P(540, 940);
      camera.position.set(c.x + 0.9 * Math.sin(k * 0.22), c.y + 0.25 + back * 1.1, 14 + back * 4.5);
      look = c.clone();
    }
    if (t > s('uniq') - 0.3 && t < e('uniq') + 0.1) camera.position.z = 14 - 0.8 * eIO(pr(t, s('uniq'), e('uniq') - s('uniq')));
    camera.lookAt(look);
    camera.updateMatrixWorld();
    orbit.updateMatrixWorld();

    heroAt(t);

    // 5. сердца поднимаются вокруг знака
    {
      const a = s('hype'), b = e('hype');
      const op = win(t, a, b);
      fade(hearts, op);
      HEARTS.forEach((h) => {
        const st = a + 0.05 + h.d * (b - a - 0.9);
        const x = pr(t, st, 1.6);
        h.m.visible = op > 0.003 && x > 0 && x < 1;
        h.m.position.copy(P(h.x, lerp(1560, 560, eOut(x)), h.z));
        h.m.scale.setScalar((h.size / U) * (0.6 + 0.4 * eExpo(x * 3)));
        h.m.rotation.set(0.3 * Math.sin(t * 2 + h.d * 6), h.spin * t, 0.25 * Math.sin(t * 1.5 + h.d * 3));
      });
    }

    // 7. нейрослоп: плитки встают каскадом, шары качаются разом, на «одинаково» подпрыгивают все вместе
    {
      const a = s('slop'), b = e('slop');
      fade(slop, win(t, a, b));
      slop.rotation.y = 0.35 * Math.sin((t - a) * 0.6) - 0.15;
      const jump = Math.sin(Math.PI * pr(t, w('slop', 3) - 0.08, 0.42));
      SLOP.forEach((o) => {
        const x = eExpo(pr(t, a + o.k * 0.05, 0.5));
        o.g.scale.setScalar(Math.max(0.001, x));
        o.blob.position.y = 0.32 + 0.04 * Math.sin(t * 4) + jump * 0.45;
        o.blob.rotation.y = t * 1.5 + jump * Math.PI;
      });
    }

    // 10–13. команда: кольцо рисуется, места встают на «команда», роли заполняются по словам, снизу скилы и MCP
    {
      const a = s('team'), b = e('much');
      const op = win(t, a, b) * (1 - 0.55 * eIO(pr(t, s('much') - 0.05, 0.7)));
      fade(team, op);
      ringLine.geometry.setDrawRange(0, Math.floor(241 * eIO(pr(t, a + 0.15, 1.0))));
      const turn = (t - a) * 0.18;
      const fillAt = [w('roles', 0), w('roles', 1), w('roles', 2), w('roles', 3), w('roles', 5)];
      NODES.forEach((n, k) => {
        const ang = Math.PI / 2 + (k * Math.PI * 2) / 5 + turn;
        const local = new THREE.Vector3(Math.cos(ang) * RING_R, Math.sin(ang) * RING_R, 0);
        n.g.position.copy(local.applyMatrix4(orbit.matrixWorld));
        n.g.quaternion.copy(camera.quaternion);
        n.g.rotateY(0.25 * Math.sin(t * 1.3 + k));
        const pop = eExpo(pr(t, w('team', 7) - 0.1 + k * 0.07, 0.5));
        n.g.scale.setScalar(Math.max(0.001, pop));
        const f = eExpo(pr(t, fillAt[k] - 0.06, 0.35));
        n.box.material.color.set(0x24251E).lerp(new THREE.Color(0xC7E24B), f);
        n.box.material.emissive.set(0xC7E24B).multiplyScalar(0.12 * f);
        n.face.material.opacity = f * op;
        n.lab.material.opacity = eOut(pr(t, fillAt[k], 0.3)) * op;
      });
      PLUGS.forEach((p, k) => {
        const at = w('skills', k ? 4 : 2) - 0.1;
        const x = eExpo(pr(t, at, 0.55));
        p.g.visible = x > 0.003 && op > 0.003;
        p.g.position.copy(p.at).add(new THREE.Vector3(0, -1.2 * (1 - x), 0));
        p.g.rotation.set(0.15, 0.4 * Math.sin(t * 1.2 + k), 0);
        p.line.geometry.setDrawRange(0, pr(t, at + 0.25, 0.3) > 0 ? 2 : 0);
        p.line.material.opacity = 0.7 * pr(t, at + 0.25, 0.3) * op;
      });
      orbit.updateMatrixWorld();
    }

    // 14–15. три одинаковых телефона двигаются разом: качаются, подпрыгивают, субтитры мигают, крутятся
    {
      const a = s('same'), b = e('same2');
      fade(same, win(t, a, b));
      const jump = Math.sin(Math.PI * pr(t, w('same2', 2) - 0.08, 0.4));
      const flash = pr(t, w('same2', 6) - 0.05, 0.05) * (1 - pr(t, w('same2', 6) + 0.45, 0.05));
      const spin = eIO(pr(t, w('same2', 8) - 0.05, 0.7)) * Math.PI * 2;
      SAME.forEach((p, k) => {
        const x = eExpo(pr(t, a + k * 0.1, 0.6));
        p.g.position.copy(P([270, 540, 810][k], 790 + (1 - x) * 300)).add(new THREE.Vector3(0, jump * 0.35, 0));
        p.g.rotation.set(0.08 + (1 - x) * 0.6, 0.38 * Math.sin((t - a) * 1.6) + spin, 0);
        p.scr.material.map = flash > 0.5 ? scrB : scrA;
      });
    }

    // 18. веер: три настоящих ролика встают стопкой и расходятся в пространстве
    {
      const a = s('uniq'), b = e('uniq');
      fade(uniq, win(t, a, b));
      const spread = eIO(pr(t, w('uniq', 1) - 0.05, 0.7));
      const POS = [[-1.25, 0.05, -0.2, 0.55, 0.12], [0, 0.12, 0.35, 0, 0], [1.25, 0.05, -0.2, -0.55, -0.12]];
      FAN.forEach((p, k) => {
        const x = eExpo(pr(t, a + k * 0.06, 0.6));
        const [px, py, pz, ry, rz] = POS[k];
        const c = P(540, 860);
        p.g.position.set(c.x + px * spread, c.y + py * spread - (1 - x) * 1.4, pz * spread + (k === 1 ? 0.05 : 0));
        p.g.rotation.set(0.05, ry * spread + 0.08 * Math.sin(t * 0.9 + k), rz * spread);
      });
    }

    // 19. проверка: кадры едут дугой сквозь рамку; прошедший получает галочку, брак — крест, поднимается и уезжает назад
    {
      const a = s('check'), b = e('check');
      const op = win(t, a, b);
      fade(check, op);
      const t0 = a + 0.4, tb = w('check', 5) - 0.05;
      const GAP = 0.86, v = (BAD * GAP) / (tb - t0);
      const base = P(540, 1030);
      CARDS.forEach((c, k) => {
        let x = k * GAP - v * (t - t0);
        const lift = k === BAD ? eExpo(pr(t, w('check', 6) - 0.1, 0.4)) : 0;
        const away = k === BAD ? eIn(pr(t, w('check', 7) - 0.05, 0.7)) : 0;
        x -= away * 4;
        c.g.position.set(base.x + x, base.y + lift * 0.62, -0.32 * x * x);
        c.g.rotation.set(0, Math.max(-1, Math.min(1, -0.55 * x)), k === BAD ? lift * 0.18 : 0);
        const passed = t0 + (k * GAP) / v;
        const bt = eExpo(pr(t, passed, 0.3));
        BADGES[k].scale.setScalar(Math.max(0.001, 0.3 * bt));
        BADGES[k].material.opacity = bt * op * (1 - away);
      });
      scanBar.position.y = 0.72 * Math.sin((t - a) * 4.5);
      gm.opacity = op;
    }

    // 20. путь: ступени встают снизу вверх, на своём слове загораются лаймом
    {
      const a = s('path'), b = e('path');
      const op = win(t, a, b);
      fade(path, op);
      STEP.forEach((st, k) => {
        const x = eExpo(pr(t, a + k * 0.06, 0.5));
        st.g.position.copy(P(300, STEP_Y(k) + (1 - x) * 120));
        st.g.rotation.y = 0.5 + 0.12 * Math.sin(t * 0.8 + k * 0.5);
        const on = eExpo(pr(t, w('path', k) - 0.08, 0.3));
        st.box.material.color.set(0x2B3620).lerp(new THREE.Color(0xC7E24B), on);
        st.on.material.opacity = on * op;
        st.off.material.opacity = (1 - on) * op;
      });
    }

    // 21. коробка: плитки встают на своих словах, на «собрал» летят дугой внутрь, крышка закрывается
    {
      const a = s('pack'), b = e('pack');
      const op = win(t, a, b);
      fade(pack, op);
      boxG.rotation.y = -0.42 + 0.1 * Math.sin((t - a) * 0.8);
      const go = w('pack', 5) - 0.05;
      ITEMS.forEach((it, k) => {
        const appear = eExpo(pr(t, w('pack', [0, 1, 3][k]) - 0.08, 0.45));
        const fly = eIn(pr(t, go + k * 0.1, 0.55));
        const pos = vlerp(it.at, boxMouth, fly).add(new THREE.Vector3(0, Math.sin(Math.PI * fly) * 0.8, 0));
        it.g.position.copy(pos);
        it.g.scale.setScalar(Math.max(0.001, appear * (1 - 0.55 * fly)));
        it.g.rotation.set(0.2 + fly * 2, 0.5 * Math.sin(t + k) + fly * 3, 0);
        it.g.visible = appear > 0.003 && fly < 0.98 && op > 0.003;
        it.lab.material.opacity = (1 - pr(t, go + k * 0.1, 0.2)) * op;
      });
      lidPivot.rotation.x = lerp(-1.95, 0, eIO(pr(t, go + 0.65, 0.45)));
      sysFace.material.opacity = eOut(pr(t, w('pack', 7) - 0.1, 0.35)) * op;
    }

    renderer.render(scene, camera);
  };
};
