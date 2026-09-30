// Движение ролика «Одна фраза запустила всё»: цепная реакция, всё считается из номера кадра.
// Шарик → плитки CLAUDE → рычаг и карточка → тоннель из кадров → телефон → кнопка → снова полка.
import { interpolate } from 'remotion';
import * as THREE from 'three';
import { curve } from '../lib/brand';

export const BPM = 100;
export const BEAT = 18;
export const BAR = 72;
export const LENGTH = BAR * 11;                 // 792 кадра, 26,4 с
export const b = (n: number) => n * BEAT;

export const T = {
  hook: 0, roll: BAR, tiles: 2 * BAR, lever: 3 * BAR, tunnel: 4 * BAR, phone: 6 * BAR,
  button: 7 * BAR, press: 7 * BAR + b(1), cta: 8 * BAR, back: 10 * BAR, end: LENGTH,
} as const;

const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
export const ease = (frame: number, from: number, to: number, easing = curve.both) =>
  interpolate(frame, [from, to], [0, 1], { ...clamp, easing });
const v = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);

// ── Стол: где что стоит ─────────────────────────────────────────────────────────────────
export const R = 0.28;                          // радиус шарика
export const SHELF = { from: v(-9.0, 3.0, 0), to: v(-4.0, 2.92, 0) };
export const REST = 0.93;                       // где на полке лежит шарик, доля длины
export const PLANK = { from: v(-4.0, 2.88, 0), to: v(-1.3, 0.1, 0) };
export const TILE = { w: 0.9, h: 1.4, d: 0.12, step: 1.1, x0: -0.5 };
export const TILES = 6;
export const HOLE = v(-1.15, 0, 0.75);          // куда проваливается шарик после удара
export const LEVER = { pivot: v(6.55, 0.35, 0), half: 0.9 };
// тоннель: винт из карточек, сужается к телефону и слегка опускается
// шаг между карточками сокращается к концу: гуще, быстрее, как разгон
// к концу карточки мельче и ближе к оси: последние закрывают телефон, пока их не всосёт
export const TUNNEL = { x: 6.55, y0: 3.4, y1: 2.2, z0: 1.6, step0: 0.62, step1: 0.4, r0: 2.1, r1: 0.7, s0: 1, s1: 0.45, n: 36, stop: 9 };
const depth = (i: number) => TUNNEL.step0 * i + (TUNNEL.step1 - TUNNEL.step0) * i * (i - 1) / (2 * (TUNNEL.n - 1));
const Z_LAST = TUNNEL.z0 - depth(TUNNEL.n - 1);
export const PHONE = v(TUNNEL.x, 1.5, Z_LAST - 1.4);
export const BUTTON = v(TUNNEL.x + 2.5, 0.25, PHONE.z + 0.4);
export const PIPE_END = v(BUTTON.x, 2.75, BUTTON.z);
// труба с коленом: встаёт из пола и выплёвывает шарик над кнопкой
export const PIPE = [
  v(BUTTON.x + 1.6, -0.3, BUTTON.z), v(BUTTON.x + 1.6, 2.3, BUTTON.z), v(BUTTON.x + 1.45, 3.15, BUTTON.z),
  v(BUTTON.x + 0.8, 3.55, BUTTON.z), v(BUTTON.x + 0.15, 3.25, BUTTON.z), PIPE_END.clone(),
];

const shelfRest = () => { const p = SHELF.from.clone().lerp(SHELF.to, REST); return v(p.x, p.y + R + 0.06, p.z); };

// ── Шарик ────────────────────────────────────────────────────────────────────────────────
export const ball = (frame: number) => {
  // покой на полке, к концу такта медленно подкатывается к краю доски
  if (frame < T.roll) {
    const t = ease(frame, b(2), T.roll, curve.in);
    const p = SHELF.from.clone().lerp(SHELF.to, REST + (1 - REST) * t);
    // на краю шарик чуть покачивается: вот-вот сорвётся
    const rock = Math.sin(frame / 4.2) * 0.04 * (1 - t);
    return { pos: v(p.x + rock * 0.4, p.y + R + 0.06, p.z), spin: t * 1.2 + rock, seen: true };
  }
  // разгон по доске: скорость растёт, как под тяжестью
  if (frame < T.tiles) {
    const t = ease(frame, T.roll, T.tiles, curve.in);
    const p = PLANK.from.clone().lerp(PLANK.to, t);
    return { pos: v(p.x, p.y + R + 0.06, p.z), spin: 1.2 + t * 9, seen: true };
  }
  // удар по первой плитке и падение в люк
  if (frame < T.tiles + 26) {
    const t = ease(frame, T.tiles, T.tiles + 26, curve.in);
    const p = v(PLANK.to.x, PLANK.to.y + R + 0.06, 0).lerp(v(HOLE.x, -0.8, HOLE.z), t);
    return { pos: p, spin: 10.2 + t * 2, seen: true };
  }
  // прячется в трубе, выпадает над кнопкой
  if (frame < T.button + 4) return { pos: v(0, -5, 0), spin: 0, seen: false };
  const t = ease(frame, T.button + 4, T.press, curve.in);
  const p = v(PIPE_END.x, PIPE_END.y - 0.1, PIPE_END.z).lerp(v(BUTTON.x, BUTTON.y + 0.25 + R - 0.16, BUTTON.z), t);
  return { pos: p, spin: 12.2 + t, seen: true };
};

// второй шарик: в финале прикатывается по полке и замирает там, где лежал первый
export const ball2 = (frame: number) => {
  const from = T.back + 34, to = T.end - 8;
  if (frame < from) return { pos: v(0, -5, 0), spin: 0, seen: false };
  const t = ease(frame, from, to, curve.out);
  const p = SHELF.from.clone().lerp(SHELF.to, 0.1 + (REST - 0.1) * t);
  return { pos: v(p.x, p.y + R + 0.06, p.z), spin: t * 9, seen: true };
};

// ── Плитки: падают одна за другой, каждая тянет следующую ───────────────────────────────
export const tileFall = (i: number, frame: number) => ease(frame, T.tiles + i * 7, T.tiles + i * 7 + 12, curve.in);
export const tileLands = (i: number) => T.tiles + i * 7 + 12;

// ── Рычаг и карточка ────────────────────────────────────────────────────────────────────
export const leverAt = T.tiles + (TILES - 1) * 7 + 10;
export const lever = (frame: number) => ease(frame, leverAt, leverAt + 10, curve.in);
export const cardLaunch = leverAt + 6;
export const cardLands = cardLaunch + 40;
// карточка летит дугой с дальнего конца рычага ко входу в тоннель и там висит первой
export const card = (frame: number) => {
  const t = ease(frame, cardLaunch, cardLands, curve.calm);
  const from = v(LEVER.pivot.x + LEVER.half, LEVER.pivot.y + 0.4, 0);
  const to = tunnelSlot(0);
  const p = from.clone().lerp(to.pos, t);
  p.y += Math.sin(Math.PI * t) * 1.2;
  const q = new THREE.Quaternion().slerp(to.quat, t).multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 0, (1 - t) * Math.PI * 1.5)));
  return { pos: p, quat: q, t };
};

// ── Тоннель ─────────────────────────────────────────────────────────────────────────────
export const axis = (i: number) => {
  const k = i / (TUNNEL.n - 1);
  return { y: TUNNEL.y0 + (TUNNEL.y1 - TUNNEL.y0) * k, r: TUNNEL.r0 + (TUNNEL.r1 - TUNNEL.r0) * k, s: TUNNEL.s0 + (TUNNEL.s1 - TUNNEL.s0) * k, z: TUNNEL.z0 - depth(i) };
};
export const tunnelSlot = (i: number) => {
  const a = (i / TUNNEL.n) * Math.PI * 2 * 3.5 + Math.PI / 2;
  const { y, r, z } = axis(i);
  const pos = v(TUNNEL.x + Math.cos(a) * r, y + Math.sin(a) * r, z);
  const quat = new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 0, a + Math.PI / 2));
  return { pos, quat };
};
// карточка i вылетает вперёд из-за спины камеры и садится в свой паз; после полёта
// все карточки по очереди всасываются в экран телефона
export const tunnelCard = (i: number, frame: number) => {
  const slot = tunnelSlot(i);
  const u = i === 0 ? (frame >= cardLands ? 1 : 0) : ease(frame, cardLaunch + 6 + i * 3, cardLaunch + 28 + i * 3, curve.out);
  const gone = ease(frame, T.phone - 10 + (TUNNEL.n - 1 - i) * 0.9, T.phone + 6 + (TUNNEL.n - 1 - i) * 0.9, curve.in);
  const pos = slot.pos.clone();
  pos.z += (1 - u) * 6;
  pos.lerp(v(PHONE.x, PHONE.y, PHONE.z + 0.1), gone);
  return { pos, quat: slot.quat, u, gone, scale: axis(i).s * (0.6 + 0.4 * u) * (1 - gone * 0.96) };
};

// ── Телефон и кнопка ────────────────────────────────────────────────────────────────────
export const phoneOn = (frame: number) => ease(frame, T.phone - 6, T.phone + 10, curve.out);
export const pressed = (frame: number) => {
  const t = frame - T.press;
  if (t < 0) return 0;
  if (t < 3) return t / 3;
  return 1;
};

// ── Камера ──────────────────────────────────────────────────────────────────────────────
type Pose = { pos: THREE.Vector3; aim: THREE.Vector3 };
const lerpPose = (a: Pose, c: Pose, t: number): Pose => ({ pos: a.pos.clone().lerp(c.pos, t), aim: a.aim.clone().lerp(c.aim, t) });
const bend = (a: THREE.Vector3, m: THREE.Vector3, c: THREE.Vector3, t: number) =>
  a.clone().multiplyScalar((1 - t) ** 2).add(m.clone().multiplyScalar(2 * (1 - t) * t)).add(c.clone().multiplyScalar(t * t));

const rest = shelfRest();
export const shelfPose: Pose = { pos: v(rest.x - 0.1, rest.y + 0.7, 5.0), aim: v(rest.x + 0.3, rest.y - 0.6, 0) };

export const camera = (frame: number): Pose & { fov: number } => {
  const bp = ball(frame).pos;
  const roll = ease(frame, T.roll, T.tiles);
  const rolling: Pose = { pos: v(bp.x + 1.2, bp.y + 1.5, 5.8 - roll * 1.2), aim: v(bp.x + 0.6, bp.y - 0.2, 0) };
  // вдоль ряда плиток: ряд уходит по диагонали вглубь
  const tiles: Pose = { pos: v(-4.2, 3.0, 5.2), aim: v(0.6, 0.6, -0.2) };
  // камера провожает карточку взглядом вверх
  const lift = ease(frame, cardLaunch, cardLaunch + 26, curve.calm);
  const lever: Pose = { pos: v(4.4, 1.7 + lift * 0.9, 6.6), aim: v(6.5, 1.6 + lift * 2.6, 0) };
  const mouth: Pose = { pos: v(TUNNEL.x, TUNNEL.y0, TUNNEL.z0 + 6.0), aim: v(TUNNEL.x, TUNNEL.y0 - 0.3, TUNNEL.z0 - 8) };
  const zEnd = axis(TUNNEL.n - TUNNEL.stop).z;
  const inside = (t: number): Pose => {
    const y = TUNNEL.y0 + (TUNNEL.y1 - TUNNEL.y0) * t;
    return { pos: v(TUNNEL.x, y, TUNNEL.z0 + 1.5 - t * (TUNNEL.z0 + 1.5 - zEnd)), aim: v(TUNNEL.x, y - 0.4, zEnd - 8) };
  };
  const phone: Pose = { pos: v(PHONE.x + 0.4, 2.3, PHONE.z + 5.0), aim: v(PHONE.x + 0.1, PHONE.y + 0.1, PHONE.z) };
  const button: Pose = { pos: v(BUTTON.x - 1.3, 4.4, BUTTON.z + 7.0), aim: v(BUTTON.x - 0.3, 0.7, BUTTON.z) };
  const wide: Pose = { pos: v(BUTTON.x - 1.2, 7.4, BUTTON.z + 6.2), aim: v(BUTTON.x - 0.7, 0.3, BUTTON.z - 0.5) };

  let p = shelfPose;
  p = lerpPose(p, rolling, ease(frame, T.roll - 10, T.roll + 20));
  p = lerpPose(p, tiles, ease(frame, T.tiles - 28, T.tiles - 2));
  p = lerpPose(p, lever, ease(frame, leverAt - 14, leverAt + 12));
  p = lerpPose(p, mouth, ease(frame, cardLaunch + 24, T.tunnel - 4));
  const flight = ease(frame, T.tunnel, T.phone - 10, curve.calm);
  if (flight > 0) p = lerpPose(p, inside(flight), Math.min(1, flight * 6));
  p = lerpPose(p, phone, ease(frame, T.phone - 14, T.phone + 16));
  p = lerpPose(p, button, ease(frame, T.button - 14, T.button + 10));
  p = lerpPose(p, wide, ease(frame, T.cta, T.cta + 44, curve.calm));
  // назад к полке: дугой над всей дорожкой, чтобы зритель увидел путь целиком
  // камера держит кнопку, пока читается призыв, потом резким броском уходит к полке
  const back = ease(frame, T.back + 22, T.back + 50, curve.both);
  if (back > 0) {
    const over = v(1.0, 6.0, -4.0);
    p = { pos: bend(wide.pos, over, shelfPose.pos, back), aim: wide.aim.clone().lerp(shelfPose.aim, ease(frame, T.back + 22, T.back + 46, curve.both)) };
  }
  // дрейф: кадр не стоит
  p.pos.x += Math.sin(frame / 53) * 0.05;
  p.pos.y += Math.sin(frame / 41) * 0.04;
  // угол обзора расширяется в полёте: скорость чувствуется телом
  const fov = 42 + Math.sin(Math.PI * flight) * 22;
  return { ...p, fov };
};
