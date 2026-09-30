// Карандашные штрихи без сторонних зависимостей: линия дрожит, как рука, и ложится в два прохода.
import { rnd } from '../lib/brand';

export type Pt = [number, number];

// Точки ломаной с дрожанием: сдвиг по нормали, плавный по длине, с зерном по номеру штриха.
export const wobble = (pts: Pt[], seed: number, amount = 2.2, steps = 14): Pt[] => {
  const out: Pt[] = [];
  for (let s = 0; s < pts.length - 1; s++) {
    const [x0, y0] = pts[s], [x1, y1] = pts[s + 1];
    const len = Math.hypot(x1 - x0, y1 - y0) || 1;
    const nx = -(y1 - y0) / len, ny = (x1 - x0) / len;
    for (let k = 0; k <= steps; k++) {
      const t = k / steps;
      const n = (rnd(seed * 3.1 + s * 7.7 + k * 0.9) - 0.5) * 2 * amount * Math.sin(Math.PI * t) + (rnd(seed * 5.3 + s) - 0.5) * amount * 0.6;
      out.push([x0 + (x1 - x0) * t + nx * n, y0 + (y1 - y0) * t + ny * n]);
    }
  }
  return out;
};

export const d = (pts: Pt[]) => pts.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`).join(' ');

// Прямоугольник с небольшим перехлёстом углов, как рисуют от руки.
export const rect = (x: number, y: number, w: number, h: number, seed: number): Pt[][] => {
  const o = 6;
  return [
    [[x - o, y], [x + w + o, y]],
    [[x + w, y - o], [x + w, y + h + o]],
    [[x + w + o, y + h], [x - o, y + h]],
    [[x, y + h + o], [x, y - o]],
  ].map((seg, i) => wobble(seg as Pt[], seed + i));
};

// Окружность из ломаной с чуть незамкнутым концом.
export const circle = (cx: number, cy: number, r: number, seed: number, from = -1.9, to = 4.5): Pt[] => {
  const pts: Pt[] = [];
  for (let a = from; a <= to; a += 0.25) pts.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]);
  return wobble(pts, seed, 1.6, 4);
};

// Дудл кота: голова, уши, глаза, нос, усы. Порядок массива это порядок рисования.
export const catDoodle = (cx: number, cy: number, r: number): Pt[][] => [
  circle(cx, cy, r, 11),
  wobble([[cx - r * 0.75, cy - r * 0.55], [cx - r * 0.95, cy - r * 1.35], [cx - r * 0.25, cy - r * 0.9]], 12),
  wobble([[cx + r * 0.25, cy - r * 0.9], [cx + r * 0.95, cy - r * 1.35], [cx + r * 0.75, cy - r * 0.55]], 13),
  circle(cx - r * 0.38, cy - r * 0.1, r * 0.22, 14, 0, 6.4),
  circle(cx + r * 0.38, cy - r * 0.1, r * 0.22, 15, 0, 6.4),
  wobble([[cx - r * 0.08, cy + r * 0.25], [cx + r * 0.08, cy + r * 0.25], [cx, cy + r * 0.38], [cx - r * 0.08, cy + r * 0.25]], 16, 1),
  wobble([[cx - r * 0.55, cy + r * 0.3], [cx - r * 1.15, cy + r * 0.2]], 17, 1.2),
  wobble([[cx + r * 0.55, cy + r * 0.3], [cx + r * 1.15, cy + r * 0.2]], 18, 1.2),
];

export const bars = (x: number, y: number, w: number, h: number): Pt[][] =>
  [0.55, 0.95, 0.7, 1.0].map((k, i) => wobble([[x + i * (w / 4) + w / 8, y + h], [x + i * (w / 4) + w / 8, y + h - h * k]], 21 + i, 1.5, 6));

export const button = (x: number, y: number, w: number, h: number): Pt[][] => {
  const r = h / 2;
  const pts: Pt[] = [];
  for (let a = Math.PI / 2; a <= Math.PI * 1.5; a += 0.3) pts.push([x + r + Math.cos(a) * r, y + r + Math.sin(a) * r]);
  for (let a = -Math.PI / 2; a <= Math.PI / 2; a += 0.3) pts.push([x + w - r + Math.cos(a) * r, y + r + Math.sin(a) * r]);
  pts.push(pts[0]);
  return [wobble(pts, 31, 1.6, 3), wobble([[x + w * 0.36, y + h * 0.52], [x + w * 0.46, y + h * 0.7], [x + w * 0.66, y + h * 0.3]], 32, 1.2)];
};
