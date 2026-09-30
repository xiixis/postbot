// Движение ролика «Карандаш»: всё считается из номера кадра.
// Карандаш рисует четыре сцены ролика «Слова под бит» → квадраты переворачиваются в настоящие
// кадры → кадры оживают → первый разворачивается во весь экран → кнопка карандашом → петля.
import { interpolate } from 'remotion';
import { curve } from '../lib/brand';
import { d as pathOf, type Pt, rect, wobble } from '../mock/strokes';

export const BEAT = 20;                          // 90 ударов в минуту
export const BAR = 80;
export const LENGTH = BAR * 10;                  // 800 кадров, 26,7 с
export const b = (n: number) => n * BEAT;

export const T = {
  hook: 0, frames: BAR, doodles: 2 * BAR, flip: 4 * BAR, play: 6 * BAR, grow: 6 * BAR + 40, cta: 8 * BAR, loop: 9 * BAR, end: LENGTH,
} as const;

const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
// рука пишет ровно: для надписей и маркера кривая не нужна
export const linear = (t: number) => t;
export const ease = (frame: number, from: number, to: number, easing = curve.both) =>
  interpolate(frame, [from, to], [0, 1], { ...clamp, easing });

// ── Раскладка: четыре квадрата два на два, подписи от руки под ними ────────────────────
export const CELL = 390;
export const CELLS: Pt[] = [[80, 540], [510, 540], [80, 1030], [510, 1030]];
export const VERBS = ['написал', 'собрал', 'поставил', 'свёл'];
export const NOUNS = ['текст', 'кадры', 'движение', 'звук'];
// кадр ролика «Слова под бит», в который переворачивается квадрат, и откуда он потом играет
export const SCENE_AT = [138, 208, 279, 342];

// ── Штрихи ──────────────────────────────────────────────────────────────────────────────
export type Stroke = { pts: Pt[]; len: number };
const stroke = (pts: Pt[]): Stroke => {
  let len = 0;
  for (let i = 1; i < pts.length; i++) len += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
  return { pts, len };
};
export const pathD = (s: Stroke) => pathOf(s.pts);
// точка на штрихе по доле длины: сюда ставится кончик карандаша
export const pointAt = (s: Stroke, p: number): Pt => {
  let left = s.len * Math.max(0, Math.min(1, p));
  for (let i = 1; i < s.pts.length; i++) {
    const [x0, y0] = s.pts[i - 1], [x1, y1] = s.pts[i];
    const seg = Math.hypot(x1 - x0, y1 - y0);
    if (left <= seg) return [x0 + (x1 - x0) * (left / (seg || 1)), y0 + (y1 - y0) * (left / (seg || 1))];
    left -= seg;
  }
  return s.pts[s.pts.length - 1];
};

const shift = (pts: Pt[], [ox, oy]: Pt): Pt[] => pts.map(([x, y]) => [x + ox, y + oy]);

// рамки квадратов
export const FRAMES: Stroke[][] = CELLS.map((c, i) => rect(c[0], c[1], CELL, CELL, 100 + i).map(stroke));

// наброски сцен в своих квадратах; слово сцены пишется шрифтом от руки отдельно
const doodle = (i: number): Stroke[] => {
  const at = CELLS[i];
  const local: Pt[][] = [];
  if (i === 0) {
    [300, 250, 290, 210, 120].forEach((w, k) => local.push(wobble([[34, 170 + k * 44], [34 + w, 170 + k * 44]], 200 + k, 1.6, 8)));
  } else if (i === 1) {
    for (let k = 0; k < 15; k++) {
      const x = 34 + (k % 5) * 66, y = 160 + Math.floor(k / 5) * 70;
      local.push(...rect(x, y, 54, 58, 300 + k));
    }
  } else if (i === 2) {
    const pts: Pt[] = [];
    for (let t = 0; t <= 1.0001; t += 0.05) pts.push([40 + t * 290, 330 - t * 150 - Math.sin(t * Math.PI * 2) * 70]);
    local.push(wobble(pts, 400, 1.2, 2));
    const [cx, cy] = pts[pts.length - 1];
    const ring: Pt[] = [];
    for (let a = 0; a <= Math.PI * 2.1; a += 0.35) ring.push([cx + Math.cos(a) * 16, cy + Math.sin(a) * 16]);
    local.push(wobble(ring, 401, 1, 2));
  } else {
    const hs = [60, 120, 80, 160, 110, 190, 140, 90, 170, 120, 70, 130, 60, 40];
    hs.forEach((h, k) => local.push(wobble([[42 + k * 22, 270 - h / 2], [42 + k * 22, 270 + h / 2]], 500 + k, 1.4, 5)));
  }
  return local.map((p) => stroke(shift(p, at)));
};
export const DOODLES: Stroke[][] = [0, 1, 2, 3].map(doodle);

// ── Когда что рисуется ──────────────────────────────────────────────────────────────────
// рамка квадрата: первая с нулевого кадра, остальные на ударах второго такта
export const frameWindow = (i: number): [number, number] => (i === 0 ? [0, 40] : [T.frames + (i - 1) * BEAT, T.frames + (i - 1) * BEAT + 22]);
// набросок: слово сцены 12 кадров, дальше штрихи, каждый квадрат на половине такта
export const wordWindow = (i: number): [number, number] => [T.doodles + i * 40, T.doodles + i * 40 + 12];
export const doodleWindow = (i: number): [number, number] => [T.doodles + i * 40 + 10, T.doodles + i * 40 + 38];
export const verbWindow = (i: number): [number, number] => [T.frames + i * BEAT + 8, T.frames + i * BEAT + 20];

// доля нарисованного по окну; первая рамка на петле: к концу ролика дорисовывается до 15 %,
// чтобы последний кадр встал в первый
export const drawn = (frame: number, [a, z]: [number, number], easing = curve.calm) => ease(frame, a, z, easing);
export const firstFrame = (frame: number) => (frame >= T.loop ? 0.15 * ease(frame, T.end - 24, T.end, curve.calm) : 0.15 + 0.85 * ease(frame, 0, 40, curve.calm));

// несколько штрихов подряд: каждому своя доля окна по длине
export const split = (strokes: Stroke[], p: number) => {
  const total = strokes.reduce((s, x) => s + x.len, 0);
  let left = p * total;
  return strokes.map((s) => {
    const q = Math.max(0, Math.min(1, left / s.len));
    left -= s.len;
    return q;
  });
};

// ── Перевороты и оживание ───────────────────────────────────────────────────────────────
// первый квадрат после лаймовой обводки, остальные всё чаще
export const FLIPS = [T.flip + 22, T.flip + 80, T.flip + 100, T.flip + 112];
export const flip = (i: number, frame: number) => ease(frame, FLIPS[i], FLIPS[i] + 16, curve.both);
export const markWindow: [number, number] = [T.flip, T.flip + 18];
// первый квадрат разворачивается во весь экран, остальные разлетаются
export const grow = (frame: number) => ease(frame, T.grow, T.grow + 30, curve.both);
export const lift = (frame: number) => ease(frame, T.cta, T.cta + 16, curve.in);
