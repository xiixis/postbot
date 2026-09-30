// Каркас второй серии: двенадцать тактов по 72 кадра, состояния на первых долях тактов.
// Спека: docs/superpowers/specs/2026-09-30-ролики-серия-2-сценарии.md
export const BPM = 100;
export const BEAT = 18;
export const BAR = BEAT * 4;
export const LENGTH = BAR * 12;                 // 864 кадра, 28,8 с
export const b = (n: number) => n * BEAT;
export const bar = (n: number) => n * BAR;

export const T = {
  hook: bar(0),
  prompt: bar(1),
  skills: bar(3),
  show: bar(4),
  save: bar(9),
  cta: bar(10),
  press: bar(10) + b(2),
  end: LENGTH,
} as const;

export const seconds = (frame: number) => frame / 30;
