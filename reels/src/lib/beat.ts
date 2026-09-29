// Сетка ударов: где в ролике стоит удар и насколько кадр от него далеко.
// Склейки и акценты берутся отсюда, а не расставляются на глаз.

export type Grid = { bpm: number; fps: number; perBar: number };

export const grid = (bpm: number, fps = 30, perBar = 4): Grid => ({ bpm, fps, perBar });

// Кадр, на котором стоит удар номер n (считая с нуля). Дробные удары разрешены: 0.5 — слабая доля.
export const beat = (g: Grid, n: number) => Math.round((n * 60 * g.fps) / g.bpm);
export const bar = (g: Grid, n: number) => beat(g, n * g.perBar);

// Толчок на ударе: 1 в момент удара и спад до нуля за `len` кадров. До удара — ноль.
export const hit = (frame: number, at: number, len = 8) =>
  frame < at ? 0 : Math.max(0, 1 - (frame - at) / len) ** 2;

// Толчок на каждом ударе подряд: для пульса фона или счётчика.
export const pulse = (g: Grid, frame: number, len = 8, every = 1) => {
  const step = (60 * g.fps * every) / g.bpm;
  const since = frame - Math.floor(frame / step) * step;
  return Math.max(0, 1 - since / len) ** 2;
};
