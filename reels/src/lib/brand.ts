// Общее для всех роликов канала: цвета, шрифты, размер кадра, безопасные поля, кривые.
// Ролик берёт это отсюда, а своё (сетку времени, кегли) держит у себя.
import { Easing, interpolate } from 'remotion';
import { loadFont as loadOnest } from '@remotion/google-fonts/Onest';
import { loadFont as loadMono } from '@remotion/google-fonts/JetBrainsMono';

export const W = 1080;
export const H = 1920;
export const FPS = 30;

// Лайм отмечает то, что действует. Терракотовый — только слово Claude.
export const color = {
  graphite: '#12130F',
  cream: '#F1F2EA',
  lime: '#C7E24B',
  olive: '#56690C',
  forest: '#1B2108',
  claude: '#D97757',
} as const;

// Внизу подпись площадки, справа внизу её кнопки: текст туда не ставится.
export const safe = { left: 80, right: 900, top: 230, bottom: 1500 } as const;
export const column = safe.right - safe.left;

const onest = loadOnest('normal', { weights: ['500', '600', '700', '800'], subsets: ['latin', 'cyrillic'] });
const jet = loadMono('normal', { weights: ['500'], subsets: ['latin', 'cyrillic'] });
export const sans = onest.fontFamily;
export const mono = jet.fontFamily;
// Холст рисует шрифтом только после его загрузки: сцены с надписями в текстурах ждут этого.
export const fontsReady = () => Promise.all([onest.waitUntilDone(), jet.waitUntilDone()]);

const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
export const curve = {
  out: Easing.bezier(0.16, 1, 0.3, 1),        // появление: быстрый старт, мягкая посадка
  in: Easing.bezier(0.7, 0, 0.84, 0),          // уход
  both: Easing.bezier(0.65, 0, 0.35, 1),       // перемещение на месте
  calm: Easing.bezier(0.4, 0, 0.2, 1),         // «дорогой» характер
  pop: Easing.bezier(0.34, 1.56, 0.64, 1),     // с перелётом
} as const;

export const enter = (frame: number, from: number, dur = 24, easing = curve.out) =>
  interpolate(frame, [from, from + dur], [0, 1], { ...clamp, easing });
export const leave = (frame: number, from: number, dur = 12) =>
  interpolate(frame, [from, from + dur], [0, 1], { ...clamp, easing: curve.in });
export const glide = (frame: number, from: number, dur = 30) =>
  interpolate(frame, [from, from + dur], [0, 1], { ...clamp, easing: curve.both });
export const steady = (frame: number, from: number, to: number) => interpolate(frame, [from, to], [0, 1], clamp);
export const mix = (t: number, a: number, b: number) => a + (b - a) * t;

// Псевдослучайное число по зерну: одно и то же во всех вкладках рендера.
export const rnd = (seed: number) => {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
