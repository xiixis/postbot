// Движение ролика «19 слоёв»: всё считается из номера кадра.
// Кадр наклонён → слои отрываются один за другим, всё быстрее → облёт стопки → слои сходятся →
// кадр оживает видео → камера отъезжает, и кадр оказывается одним из 450 → ныряет обратно.
import { interpolate } from 'remotion';
import * as THREE from 'three';
import { curve } from '../lib/brand';

export const BEAT = 15;                          // 120 ударов в минуту
export const BAR = 60;
export const LENGTH = BAR * 13;                  // 780 кадров, 26 с
export const b = (n: number) => n * BEAT;

export const T = {
  hook: 0, peel: BAR, orbit: 3 * BAR, join: 5 * BAR, live: 6 * BAR, pull: 7 * BAR, cta: 10 * BAR, dive: 12 * BAR, end: LENGTH,
} as const;

const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
export const ease = (frame: number, from: number, to: number, easing = curve.both) =>
  interpolate(frame, [from, to], [0, 1], { ...clamp, easing });
const v = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);

// ── Кадр и слои ─────────────────────────────────────────────────────────────────────────
export const LAYERS = 19;
export const FOV = 40;
export const PLANE = { w: 3.93, h: 6.99 };      // ровно во весь кадр на расстоянии 9,6
export const FULL = 9.6;
// пиксель кадра 1080×1920 → точка на плоскости слоя
export const onPlane = (px: number, py: number) => v((px / 1080 - 0.5) * PLANE.w, (0.5 - py / 1920) * PLANE.h, 0);

// слой отрывается: страница стоит, три слоя слов на ударах, пятнадцать клеток каскадом всё чаще
export const liftAt = (i: number) => (i === 0 ? Infinity : i <= 3 ? T.peel + i * BEAT : T.peel + 4 * BEAT + (i - 4) * 4);
export const lift = (i: number, frame: number) => (i === 0 ? 0 : ease(frame, liftAt(i), liftAt(i) + 10, curve.out));
export const lifted = (frame: number) => new Array(LAYERS).fill(0).filter((_, i) => i === 0 ? frame >= T.peel : frame >= liftAt(i)).length;
export const join = (frame: number) => ease(frame, T.join, T.join + 12, curve.in);
const gap = (frame: number) => 0.34 + 0.3 * ease(frame, T.orbit - 30, T.join - 20, curve.both);
export const layerZ = (i: number, frame: number) => i * 0.002 + lift(i, frame) * gap(frame) * i * (1 - join(frame));
export const spread = (frame: number) => Math.min(1, lift(4, frame) * 1.5) * (1 - join(frame));

// ── Сетка из 450 кадров ролика, 22 в ряд: наш кадр 208-й, строка 9, столбец 10 ─────────
const PX = 108 / PLANE.w;                        // 27,48 точки атласа на единицу сцены: кадр 108 px во всю ширину слоя
export const CELL = { x: 116 / PX, y: 200 / PX }; // шаг сетки: кадр 108×192 плюс поля по 4
export const ATLAS = { w: 2552 / PX, h: 2200 / PX };
const cellAt = (row: number, col: number) => v((col - 10) * CELL.x, -(row - 9) * CELL.y, 0);
export const ATLAS_POS = [cellAt(5, 10.5), cellAt(16, 10.5)]; // центры двух половин атласа по 11 строк
export const GRID_CENTER = cellAt(10.2, 10.5);
// сетка видна только издалека: вблизи её кадры мелкие и размытые, а на нулевом кадре её нет
export const gridAlpha = (z: number) => Math.min(1, Math.max(0, (z - 18) / 25));

// ── Видео ────────────────────────────────────────────────────────────────────────────────
export const VIDEO_AT = 208;                     // кадр ролика, в который сходятся слои (6,95 с)
export const videoOn = (frame: number) => ease(frame, T.live, T.live + 6, curve.both) * (1 - ease(frame, T.dive + 6, T.dive + 20, curve.both));

// ── Камера: цель, направление взгляда и расстояние ──────────────────────────────────────
type Pose = { aim: THREE.Vector3; dir: THREE.Vector3; d: number };
const pose = (pos: THREE.Vector3, aim: THREE.Vector3): Pose => ({ aim, dir: pos.clone().sub(aim).normalize(), d: pos.distanceTo(aim) });
// расстояние меняется по логарифму: наезд и отъезд идут с ровной скоростью для глаза;
// цель при большом отъезде идёт за расстоянием, чтобы наш кадр не уехал из центра раньше времени
const blend = (a: Pose, c: Pose, t: number, followDistance = false): Pose => {
  const d = a.d * Math.pow(c.d / a.d, t);
  const k = followDistance ? (d - a.d) / (c.d - a.d || 1) : t;
  return { aim: a.aim.clone().lerp(c.aim, k), dir: a.dir.clone().lerp(c.dir, t).normalize(), d };
};

const P0 = pose(v(3.4, 1.9, 15.2), v(0.25, 1.55, 0));        // обложка: кадр наклонён, внизу
const P1 = pose(v(9.6, 3.0, 15.8), v(0.4, 0.1, 3.4));        // сбоку: слои уходят вглубь
const P2 = pose(v(-10.2, -2.6, 14.6), v(0, 0.2, 3.8));       // облёт на другую сторону
const PF = pose(v(0, 0, FULL), v(0, 0, 0));                   // строго в кадр, во весь экран
const PG = pose(v(GRID_CENTER.x, GRID_CENTER.y, 238), GRID_CENTER.clone());
const PG2 = pose(v(GRID_CENTER.x, GRID_CENTER.y, 222), GRID_CENTER.clone());

export const camera = (frame: number) => {
  let p = blend(P0, pose(v(3.0, 1.6, 14.0), v(0.25, 1.4, 0)), ease(frame, 0, T.peel, curve.calm));
  p = blend(p, P1, ease(frame, T.peel - 6, T.peel + 60, curve.both));
  p = blend(p, P2, ease(frame, T.orbit - 20, T.join - 16, curve.both));
  p = blend(p, PF, ease(frame, T.join - 16, T.join + 14, curve.both));
  p = blend(p, PG, ease(frame, T.pull, T.pull + 120, curve.both), true);
  p = blend(p, PG2, ease(frame, T.pull + 120, T.dive, curve.calm));
  if (frame >= T.dive) p = blend(PG2, P0, ease(frame, T.dive, T.end - 6, curve.both), true);
  const pos = p.aim.clone().add(p.dir.clone().multiplyScalar(p.d));
  return { pos, aim: p.aim };
};
