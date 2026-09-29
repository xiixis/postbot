// Карта ролика «Монтажный стол». Дорожки на экране показывают сам этот ролик: сцены, надписи,
// начала движений и музыку. Границы клипов — настоящие кадры, поэтому всё считается отсюда.
export const BPM = 100;
export const BEAT = 18;
export const TOTAL = 450;
export const b = (n: number) => n * BEAT;

export const T = { hook: 0, desk: b(4), build: b(8), map: b(16), cta: b(20), press: b(22) } as const;

// Раскладка стола в пикселях кадра 1080×1920.
export const VIEW = { x: 80, y: 470, w: 333, h: 592 };            // окно просмотра
export const SIDE = { x: 453, y: 470, w: 447, h: 592, head: 192, row: 100 };   // панель справа от окна
export const CARD = { x: 612, y: 590, w: 280, h: 498 };           // окно просмотра на призыве
export const LINE = { x: 80, y: 1112, w: 820, ruler: 36, lane: 78, gap: 10 };
export const laneTop = (i: number) => LINE.y + LINE.ruler + 10 + i * (LINE.lane + LINE.gap);
export const at = (frame: number) => LINE.x + (frame / TOTAL) * LINE.w;

export const LANES = ['кадры', 'текст', 'движение', 'звук'] as const;

type Clip = { from: number; to: number; drop: number; label?: string };

export const SCENES: Clip[] = [
  { from: T.hook, to: T.desk, drop: b(8) },
  { from: T.desk, to: T.build, drop: b(9) },
  { from: T.build, to: T.map, drop: b(11) },
  { from: T.map, to: T.cta, drop: b(14) },
  { from: T.cta, to: TOTAL, drop: b(14) + 6 },
];

export const TITLES: Clip[] = [
  { from: 0, to: 66, drop: b(10), label: 'Монтаж' },
  { from: 92, to: 140, drop: b(10) + 5, label: 'Программу' },
  { from: 144, to: 284, drop: b(13), label: 'Дорожки собирает Claude' },
  { from: 288, to: 356, drop: b(13) + 5, label: 'Это таймлайн' },
  { from: 366, to: TOTAL, drop: b(15), label: 'Подписаться' },
];

// Кадры, на которых в ролике начинается движение: появление надписи, падение клипа, нажатие.
export const MOVES = [0, 36, 72, 92, ...new Array(8).fill(0).map((_, i) => b(8 + i)), 288, 360, 396];
export const MOVES_DROP = b(15);

// Музыка ложится на дорожку слева направо за два удара.
export const WAVE_FROM = b(12);
export const WAVE_TO = b(14);

// Когда дорожка собрана целиком: в списке справа у неё появляется отметка.
export const DONE = [b(14) + 12, b(15) + 6, b(15) + 12, WAVE_TO];

// Удары, на которых падает клип: на них стоит щелчок.
export const TICKS = [b(8), b(9), b(10), b(11), b(13), b(14), b(15)];
