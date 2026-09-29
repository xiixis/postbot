// Всё движение версии «Клавиши»: сетка времени, нажатия, волны света, камера и полёт клавиш.
// Каждая функция считает состояние из номера кадра: порядок рендера кадров ни на что не влияет.
import { interpolate } from 'remotion';
import * as THREE from 'three';
import { curve, H, rnd, W } from '../lib/brand';
import { byEn, byRu, ENTER, LETTERS, type Key } from './layout';

export const BPM = 100;
export const BEAT = 18;
export const b = (n: number) => n * BEAT;

// Состояния стоят на ударах: крючок, набор, Enter, слово, призыв, нажатие кнопки.
export const T = { hook: 0, type: b(4), enter: b(10), rest: b(11), word: b(16), cta: b(20), press: b(22), end: 450 } as const;

const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const ease = (frame: number, from: number, to: number, easing = curve.both) => interpolate(frame, [from, to], [0, 1], { ...clamp, easing });

// Набор задачи. Паузы неровные, как у живых рук; на пробеле рука медлит.
export const ASK = 'смонтируй ролик';
const PAUSES = [0, 6, 5, 7, 6, 5, 6, 7, 5, 6, 8, 6, 5, 6, 6];
export const TYPED = ASK.split('').map((ch, i) => ({
  ch, key: byRu(ch), at: T.type + 12 + PAUSES.slice(0, i + 1).reduce((a, p) => a + p, 0),
}));

// Слово из клавиш. Каждая садится на свою долю и на ударе T.word нажимается по очереди.
export const WORD = 'claude'.split('').map((ch, i) => ({
  ch, key: byEn(ch), land: T.rest + BEAT + i * 9, tap: T.word + i * 9, back: T.cta - 16 + i * 2,
}));
const FLIGHT = 32;
const RETURN = 18;
const inWord = new Set(WORD.map((w) => w.key.id));

// Клавиатура печатает сама, пока работает Claude.
const GHOST = new Array(Math.floor((T.cta - 8 - (T.rest + 24)) / 3)).fill(0).map((_, i) => {
  const at = T.rest + 24 + i * 3;
  return { at, key: LETTERS[Math.floor(rnd(at * 1.7) * LETTERS.length)] };
}).filter((g) => !inWord.has(g.key.id));

// Нажатие: клавиша внизу ровно на кадре события, туда идёт два кадра, обратно восемь.
const tap = (frame: number, at: number) => {
  const t = frame - (at - 2);
  if (t < 0 || t > 12) return 0;
  if (t < 2) return t / 2;
  if (t < 4) return 1;
  return 1 - curve.both((t - 4) / 8);
};
const lit = (frame: number, at: number, len = 18) => {
  const t = frame - at;
  return t < 0 || t > len ? 0 : (1 - t / len) ** 2;
};

// Волна: кольцо расходится от клавиши, под ним клавиши проседают и загораются.
type Wave = { from: number; at: Key; speed: number; width: number; life: number; press: number; glow: number };
const WAVES: Wave[] = [
  ...[-6, b(1), b(2), b(3)].map((from) => ({ from, at: ENTER, speed: 0.55, width: 1.3, life: 30, press: 0.4, glow: 0.7 })),
  { from: T.enter, at: ENTER, speed: 0.7, width: 1.8, life: 34, press: 0.85, glow: 1 },
  { from: T.word, at: byRu('п'), speed: 0.6, width: 1.5, life: 26, press: 0.35, glow: 0.5 },
];
const wave = (frame: number, key: Key, w: Wave) => {
  const t = frame - w.from;
  if (t < 0 || t > w.life) return 0;
  const r = Math.hypot(key.x - w.at.x, key.z - w.at.z);
  return Math.exp(-(((r - t * w.speed) / w.width) ** 2)) * (1 - t / w.life);
};

// glow — свет из-под клавиши и цвет надписи; flash — вспышка от настоящего нажатия.
export type State = { press: number; glow: number; flash: number };

export const state = (frame: number, key: Key): State => {
  let press = 0, glow = 0, flash = 0;
  for (const w of WAVES) {
    const a = wave(frame, key, w);
    press = Math.max(press, a * w.press);
    glow = Math.max(glow, a * w.glow);
  }
  for (const e of TYPED) {
    if (e.key.id !== key.id) continue;
    press = Math.max(press, tap(frame, e.at));
    flash = Math.max(flash, lit(frame, e.at, 22));
  }
  if (key.id === ENTER.id) {
    press = Math.max(press, tap(frame, T.enter));
    flash = Math.max(flash, lit(frame, T.enter, 30));
  }
  for (const g of GHOST) {
    if (g.key.id !== key.id || frame < g.at - 2 || frame > g.at + 16) continue;
    press = Math.max(press, tap(frame, g.at) * 0.8);
    flash = Math.max(flash, lit(frame, g.at, 16) * 0.85);
  }
  return { press, glow: Math.max(glow, flash), flash };
};

// Общий свет под клавишами дышит на каждый удар.
export const breath = (frame: number) => {
  const since = frame - Math.floor(frame / BEAT) * BEAT;
  return 0.16 + 0.12 * Math.max(0, 1 - since / 12) ** 2;
};

// ── Камера ────────────────────────────────────────────────────────────────────────────────
// Камера задаётся точкой на клавиатуре, расстоянием, подъёмом и поворотом вокруг точки.
// back отодвигает прицел за клавиатуру: от этого она опускается в кадре и сверху есть место тексту.
type Pose = { fx: number; fz: number; d: number; el: number; az: number; back: number };
const MACRO: Pose = { fx: 7.2, fz: 0.3, d: 10, el: 0.62, az: -0.62, back: 1.3 };
const RUNWAY: Pose = { fx: 0.6, fz: 0.2, d: 21, el: 0.75, az: -1.15, back: 6 };
const REST: Pose = { fx: 0.4, fz: 0.2, d: 16, el: 0.95, az: -0.3, back: 5.2 };
const CTA: Pose = { fx: 0.4, fz: 0.2, d: 19, el: 1.0, az: -0.15, back: 5.4 };

const blend = (a: Pose, c: Pose, t: number): Pose => ({
  fx: a.fx + (c.fx - a.fx) * t, fz: a.fz + (c.fz - a.fz) * t, d: a.d + (c.d - a.d) * t,
  el: a.el + (c.el - a.el) * t, az: a.az + (c.az - a.az) * t, back: a.back + (c.back - a.back) * t,
});

export const FOV = 34;
export type Cam = { pos: THREE.Vector3; aim: THREE.Vector3; quat: THREE.Quaternion; right: THREE.Vector3; up: THREE.Vector3; fwd: THREE.Vector3 };

export const camera = (frame: number): Cam => {
  let p = blend(MACRO, RUNWAY, ease(frame, -20, T.type + 6, curve.calm));
  p = blend(p, REST, ease(frame, T.enter + 2, T.rest + 44));
  p = blend(p, CTA, ease(frame, T.cta - 6, T.cta + 40));
  // медленный дрейф: кадр не стоит ни секунды
  const az = p.az + (frame - 225) * 0.0005;
  const focus = new THREE.Vector3(p.fx, 0, p.fz);
  const dir = new THREE.Vector3(Math.sin(az) * Math.cos(p.el), Math.sin(p.el), Math.cos(az) * Math.cos(p.el));
  const pos = focus.clone().addScaledVector(dir, p.d);
  const aim = focus.clone().add(new THREE.Vector3(-Math.sin(az), 0, -Math.cos(az)).multiplyScalar(p.back));
  const m = new THREE.Matrix4().lookAt(pos, aim, new THREE.Vector3(0, 1, 0));
  const quat = new THREE.Quaternion().setFromRotationMatrix(m);
  return {
    pos, aim, quat,
    right: new THREE.Vector3(1, 0, 0).applyQuaternion(quat),
    up: new THREE.Vector3(0, 1, 0).applyQuaternion(quat),
    fwd: new THREE.Vector3(0, 0, -1).applyQuaternion(quat),
  };
};

// Точка в пространстве, которая на экране стоит в пикселе (px, py) на расстоянии dist от камеры.
const half = (dist: number) => dist * Math.tan((FOV * Math.PI) / 360);
export const hud = (cam: Cam, px: number, py: number, dist: number) => {
  const hh = half(dist), hw = hh * (W / H);
  return cam.pos.clone()
    .addScaledVector(cam.fwd, dist)
    .addScaledVector(cam.right, ((px - W / 2) / (W / 2)) * hw)
    .addScaledVector(cam.up, ((H / 2 - py) / (H / 2)) * hh);
};
// Сколько единиц длины в одном пикселе экрана на этом расстоянии.
export const unit = (dist: number) => (2 * half(dist)) / H;

// Клавиша лицом к зрителю: верх смотрит в камеру, чуть завален назад, чтобы был виден объём.
const FACE = new THREE.Quaternion().setFromEuler(new THREE.Euler(Math.PI / 2 - 0.42, 0, 0));
export const facing = (cam: Cam, lean = 0) =>
  cam.quat.clone().multiply(FACE).multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 0, lean)));

// ── Полёт клавиш ──────────────────────────────────────────────────────────────────────────
export const HUD = 9;                       // расстояние от камеры до клавиш, висящих перед зрителем
export const REST_Y = 0.27;                 // высота центра клавиши над основанием

export type Fly = { pos: THREE.Vector3; quat: THREE.Quaternion; scale: number; u: number; press: number; glow: number };

const fly = (slot: THREE.Vector3, to: THREE.Vector3, face: THREE.Quaternion, size: number, u: number, turn: number) => {
  const pos = slot.clone().lerp(to, u);
  pos.y += Math.sin(Math.PI * u) * 1.6;
  const spin = new THREE.Quaternion().setFromEuler(new THREE.Euler(0, turn * (1 - u) * Math.PI * 2, 0));
  const quat = new THREE.Quaternion().slerp(face, u).multiply(spin);
  return { pos, quat, scale: 1 + (size - 1) * u };
};

const WORD_PX = { y: 720, pitch: 150, centre: 490 };

export const word = (frame: number, cam: Cam): (Fly & { ch: string; key: Key })[] =>
  WORD.map((w, i) => {
    const up = ease(frame, w.land - FLIGHT, w.land, curve.out);
    const down = ease(frame, w.back, w.back + RETURN, curve.both);
    const u = up * (1 - down);
    const to = hud(cam, WORD_PX.centre + (i - 2.5) * WORD_PX.pitch, WORD_PX.y + Math.sin(frame / 19 + i * 0.9) * 7, HUD);
    const size = (WORD_PX.pitch * unit(HUD)) / 1.12;
    const slot = new THREE.Vector3(w.key.x, REST_Y, w.key.z);
    const press = Math.max(tap(frame, w.land + 2) * 0.7, tap(frame, w.tap));
    const glow = Math.max(lit(frame, w.land, 20), lit(frame, w.tap, 22));
    // вверх клавиша летит с оборотом, домой возвращается прямо
    return { ...fly(slot, to, facing(cam), size, u, down > 0 ? 0 : 0.5), u, press, glow, ch: w.ch, key: w.key };
  });

export const BUTTON = { units: 5.6, px: 800, x: 480, y: 520 };

export const button = (frame: number, cam: Cam): Fly & { done: boolean } => {
  const u = ease(frame, T.cta + 2, T.cta + 28, curve.out);
  const to = hud(cam, BUTTON.x, BUTTON.y, HUD);
  const size = (BUTTON.px * unit(HUD)) / BUTTON.units;
  const slot = new THREE.Vector3(ENTER.x, REST_Y, ENTER.z);
  const f = fly(slot, to, facing(cam), size, u, 0.12);
  // кнопка вырастает из клавиши Enter по дороге к зрителю
  f.scale = size * (0.12 + 0.88 * u);
  return { ...f, u, press: tap(frame, T.press), glow: lit(frame, T.press, 26), done: frame >= T.press };
};
