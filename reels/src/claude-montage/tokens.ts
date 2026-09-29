// Ролик «Этот ролик никто не монтировал»: цвета, шрифты, кегли и сетка времени.
// Всё, что в кадре имеет цвет, кегль или момент появления, берёт его отсюда.
import { Easing, interpolate } from 'remotion';
import { loadFont as loadOnest } from '@remotion/google-fonts/Onest';
import { loadFont as loadMono } from '@remotion/google-fonts/JetBrainsMono';

export const W = 1080;
export const H = 1920;
export const FPS = 30;
export const TOTAL = 450;

// Лайм отмечает то, что действует: курсор, отправку, бегущий кадр, кнопку.
// Терракотовый — только слово Claude (правило владельца от 23.09.2026).
export const color = {
  ground: '#12130F',
  deep: '#0B0C09',
  ink: '#F1F2EA',
  action: '#C7E24B',
  claude: '#D97757',
} as const;

// Музыка 100 ударов в минуту: удар — 18 кадров, такт — 72. Состояния меняются по тактам.
export const BEAT = 18;
export const BAR = 72;
export const at = {
  hook: 0,
  prompt: BAR,
  code: BAR * 2,
  frames: BAR * 3,
  reveal: BAR * 4,
  cta: BAR * 5,
} as const;

// Внизу подпись площадки, справа внизу её кнопки: текст туда не ставится.
export const safe = { left: 80, right: 900, top: 230, bottom: 1500 } as const;
export const column = safe.right - safe.left;

export const size = { display: 140, title: 84, body: 54, code: 34 } as const;

export const sans = loadOnest('normal', { weights: ['500', '700'], subsets: ['latin', 'cyrillic'] }).fontFamily;
export const mono = loadMono('normal', { weights: ['500'], subsets: ['latin', 'cyrillic'] }).fontFamily;

// Одна манера движения на весь ролик: приходит с замедлением, уходит с разгоном, без отскока.
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const OUT = Easing.bezier(0.16, 1, 0.3, 1);
const IN = Easing.bezier(0.7, 0, 0.84, 0);
const BOTH = Easing.bezier(0.65, 0, 0.35, 1);

export const enter = (frame: number, from: number, dur = 24) => interpolate(frame, [from, from + dur], [0, 1], { ...clamp, easing: OUT });
export const leave = (frame: number, from: number, dur = 12) => interpolate(frame, [from, from + dur], [0, 1], { ...clamp, easing: IN });
export const glide = (frame: number, from: number, dur = 30) => interpolate(frame, [from, from + dur], [0, 1], { ...clamp, easing: BOTH });
export const steady = (frame: number, from: number, to: number) => interpolate(frame, [from, to], [0, 1], clamp);
export const mix = (t: number, a: number, b: number) => a + (b - a) * t;
