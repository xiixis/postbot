// Ролик «Карандаш». 26,7 с, 1080×1920, музыка 90 ударов в минуту, бумага и карандаш.
//
// Тезис: карандаш рисует план ролика «Слова под бит»: четыре квадрата, четыре сцены (написал
// текст, собрал кадры, поставил движение, свёл звук). Потом квадраты по одному, всё чаще,
// переворачиваются в настоящие кадры этих сцен, кадры оживают, первый разворачивается во весь
// экран и играет. В конце карандаш рисует кнопку, лаймовый маркер её заливает, и лист
// возвращается к нулевому кадру: ролик закольцован.
// Разрешённые приёмы: зерно бумаги, дрожащая линия в два прохода, рукописный шрифт, лаймовый
// маркер, переворот квадрата. Никакого объёма и света: это другой мир, чем цепочка и слои.
import React from 'react';
import { loadFont } from '@remotion/google-fonts/Caveat';
import { AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { hit } from '../lib/beat';
import { color, curve, enter, leave, safe, sans, W } from '../lib/brand';
import { button, type Pt } from '../mock/strokes';
import { Captions, type Word } from '../series/Captions';
import {
  b, BAR, CELL, CELLS, linear, doodleWindow, DOODLES, drawn, ease, firstFrame, flip, FLIPS, frameWindow, FRAMES, grow, LENGTH, lift,
  markWindow, NOUNS, pathD, pointAt, SCENE_AT, split, type Stroke, T, VERBS, verbWindow, wordWindow,
} from './motion';
import words from '../series/words/r9.json';

const hand = loadFont('normal', { weights: ['500', '700'], subsets: ['latin', 'cyrillic'] }).fontFamily;
const PAPER = '#F1EFE4';
const INK = '#2A2B24';
const MARK = 'rgba(199,226,75,0.6)';
const HEAD = 'План на 4 сцены';

// ── Бумага ──────────────────────────────────────────────────────────────────────────────
const Paper: React.FC = () => (
  <svg width={W} height={1920} style={{ position: 'absolute', inset: 0 }}>
    <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" /><feColorMatrix values="0 0 0 0 0.2 0 0 0 0 0.2 0 0 0 0 0.15 0 0 0 0.16 0" /></filter>
    <rect width={W} height={1920} fill={PAPER} />
    <rect width={W} height={1920} filter="url(#grain)" />
  </svg>
);

// ── Штрих: рисуется по длине, второй проход тоньше и со сдвигом, как второй нажим ───────
const Line: React.FC<{ s: Stroke; p: number; width?: number; ink?: string; opacity?: number }> = ({ s, p, width = 5, ink = INK, opacity = 1 }) => {
  if (p <= 0) return null;
  const d = pathD(s);
  const dash = { strokeDasharray: `${s.len + 1} ${s.len + 1}`, strokeDashoffset: s.len * (1 - p) };
  return (
    <g fill="none" stroke={ink} strokeLinecap="round" strokeLinejoin="round" opacity={opacity}>
      <path d={d} strokeWidth={width} strokeOpacity={0.92} style={dash} />
      <path d={d} strokeWidth={width * 0.55} strokeOpacity={0.38} transform="translate(1.6 1.2)" style={dash} />
    </g>
  );
};
const Lines: React.FC<{ strokes: Stroke[]; p: number; width?: number; ink?: string }> = ({ strokes, p, width, ink }) => (
  <>{split(strokes, p).map((q, i) => <Line key={i} s={strokes[i]} p={q} width={width} ink={ink} />)}</>
);

// Надпись от руки: проявляется слева направо, как будто её пишут.
const Hand: React.FC<{ text: string; x: number; y: number; px: number; p: number; rotate?: number; ink?: string; width?: number }> = ({ text, x, y, px, p, rotate = -1.5, ink = INK, width }) => p <= 0 ? null : (
  <div style={{
    position: 'absolute', left: x, top: y, width, fontFamily: hand, fontWeight: 700, fontSize: px, lineHeight: 1.05, color: ink,
    transform: `rotate(${rotate}deg)`, transformOrigin: 'left center', clipPath: `inset(-20% ${(1 - p) * 100}% -20% ${p < 0.02 ? 0 : -2}%)`,
  }}>{text}</div>
);
// где кончик карандаша, пока пишется надпись: грубая оценка ширины рукописной строки
const handTip = (text: string, x: number, y: number, px: number, p: number): Pt => [x + text.length * px * 0.43 * p, y + px * 0.8];

// ── Карандаш ────────────────────────────────────────────────────────────────────────────
const PencilShape: React.FC<{ at: Pt; opacity: number; tilt: number }> = ({ at, opacity, tilt }) => (
  <svg width={W} height={1920} style={{ position: 'absolute', inset: 0, opacity, pointerEvents: 'none' }}>
    <defs>
      <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6" /></filter>
    </defs>
    <g transform={`translate(${at[0] + 10} ${at[1] + 14}) rotate(${tilt})`} opacity={0.22} filter="url(#soft)">
      <rect x={-16} y={-350} width={32} height={336} rx={6} fill="#000" />
    </g>
    <g transform={`translate(${at[0]} ${at[1]}) rotate(${tilt})`}>
      <polygon points="-15,-52 15,-52 5,-14 -5,-14" fill="#E7C9A0" />
      <polygon points="-5,-14 5,-14 0,0" fill={INK} />
      <rect x={-15} y={-300} width={30} height={248} fill={color.lime} />
      <rect x={-5} y={-300} width={10} height={248} fill="#B5D03C" />
      <rect x={-16} y={-324} width={32} height={26} rx={3} fill="#B9B9B0" />
      <rect x={-15} y={-352} width={30} height={30} rx={8} fill={color.olive} />
    </g>
  </svg>
);

// ── Квадрат сцены: лицо набросок, изнанка настоящий кадр ────────────────────────────────
const M = 24;                                    // поле вокруг квадрата под перехлёст штрихов
const CellFront: React.FC<{ i: number; frame: number }> = ({ i, frame }) => {
  const [cx, cy] = CELLS[i];
  // на петле лист чистый: заново рисуется только начало первой рамки
  const L = frame >= T.loop;
  const pFrame = i === 0 ? firstFrame(frame) : L ? 0 : drawn(frame, frameWindow(i));
  const pDoodle = L ? 0 : drawn(frame, doodleWindow(i));
  const pWord = L ? 0 : drawn(frame, wordWindow(i), linear);
  return (
    <div style={{ position: 'absolute', inset: -M, backfaceVisibility: 'hidden' }}>
      <svg width={CELL + M * 2} height={CELL + M * 2} viewBox={`${cx - M} ${cy - M} ${CELL + M * 2} ${CELL + M * 2}`} style={{ position: 'absolute', inset: 0, overflow: 'visible' }}>
        <Lines strokes={FRAMES[i]} p={pFrame} />
        <Lines strokes={DOODLES[i]} p={pDoodle} width={i === 1 ? 3.6 : 4.6} />
      </svg>
      <Hand text={NOUNS[i]} x={M + 32} y={M + 34} px={70} p={pWord} />
    </div>
  );
};

const CellBack: React.FC<{ i: number; frame: number }> = ({ i, frame }) => {
  const playing = frame >= T.play && frame < T.loop;
  const g = i === 0 ? grow(frame) : 0;
  const media: React.CSSProperties = { width: '100%', height: '100%', objectFit: 'cover', objectPosition: `50% ${22 + 28 * g}%` };
  return (
    <div style={{ position: 'absolute', inset: 0, backfaceVisibility: 'hidden', transform: 'rotateY(180deg)', borderRadius: 16 * (1 - g), overflow: 'hidden', background: PAPER, boxShadow: `0 0 0 ${5 * (1 - g)}px ${INK}` }}>
      {playing
        ? <Sequence from={T.play} layout="none"><OffthreadVideo src={staticFile('r7-chain/screen.mp4')} startFrom={SCENE_AT[i]} muted style={media} /></Sequence>
        : <Img src={staticFile(`r9-pencil/s${i + 1}.jpg`)} style={media} />}
    </div>
  );
};

const Cell: React.FC<{ i: number; frame: number }> = ({ i, frame }) => {
  const L = frame >= T.loop;
  const f = L ? 0 : flip(i, frame);
  const [cx, cy] = CELLS[i];
  const g = L ? 0 : grow(frame);
  const up = L ? 0 : lift(frame);
  // первый квадрат растёт во весь экран, остальные уходят к краям
  let box = { left: cx, top: cy, width: CELL, height: CELL };
  let away = 0;
  if (i === 0) {
    box = { left: cx * (1 - g), top: cy * (1 - g), width: CELL + (W - CELL) * g, height: CELL + (1920 - CELL) * g };
  } else away = L ? 0 : ease(frame, T.grow - 4, T.grow + 20, curve.in);
  const dx = (cx - 300) * away * 0.9, dy = (cy - 800) * away * 0.9;
  const pop = Math.sin(Math.PI * f) * 0.08;
  return (
    <div style={{
      position: 'absolute', ...box, perspective: 1600, zIndex: i === 0 ? 5 : 1,
      transform: `translate(${dx}px, ${dy - up * 1960 * (i === 0 ? 1 : 0)}px) scale(${1 + pop - away * 0.4})`, opacity: 1 - away,
    }}>
      <div style={{ position: 'absolute', inset: 0, transformStyle: 'preserve-3d', transform: `rotateY(${f * 180}deg)` }}>
        <CellFront i={i} frame={frame} />
        <CellBack i={i} frame={frame} />
      </div>
      {f > 0 && f < 1 && <div style={{ position: 'absolute', inset: 0, boxShadow: `0 ${30 * pop * 10}px ${60 * pop * 10}px rgba(42,43,36,${0.3 * pop * 10})`, borderRadius: 16, pointerEvents: 'none' }} />}
    </div>
  );
};

// ── Где кончик карандаша ────────────────────────────────────────────────────────────────
type Task = { a: number; z: number; at: (p: number) => Pt };
const onStrokes = (strokes: Stroke[], p: number): Pt => {
  const q = split(strokes, p);
  let k = q.findIndex((x) => x < 1);
  if (k < 0) k = strokes.length - 1;
  return pointAt(strokes[k], q[k]);
};
const BTN = { x: safe.left, y: 700, w: 700, h: 164 };
const BTN_LINE: Stroke[] = [button(BTN.x, BTN.y, BTN.w, BTN.h)[0]].map((pts) => {
  let len = 0;
  for (let k = 1; k < pts.length; k++) len += Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]);
  return { pts, len };
});
const CTA = { draw: [T.cta + 6, T.cta + 30] as [number, number], fill: T.cta + b(2), ask: [T.cta + 30, T.cta + 60] as [number, number] };
const HEAD_AT = { x: safe.left, y: 230, px: 118 };
const HEAD_REWRITE: [number, number] = [T.loop + 16, T.loop + 50];

const TASKS: Task[] = [
  { a: 0, z: 40, at: (p) => onStrokes(FRAMES[0], 0.15 + 0.85 * p) },
  ...[0, 1, 2, 3].flatMap((i): Task[] => [
    ...(i > 0 ? [{ a: frameWindow(i)[0], z: frameWindow(i)[1], at: (p: number) => onStrokes(FRAMES[i], p) }] : []),
    { a: verbWindow(i)[0], z: verbWindow(i)[1], at: (p: number) => handTip(VERBS[i], CELLS[i][0] + 10, CELLS[i][1] + CELL + 8, 54, p) },
  ]).sort((x, y) => x.a - y.a),
  ...[0, 1, 2, 3].flatMap((i): Task[] => [
    { a: wordWindow(i)[0], z: wordWindow(i)[1], at: (p) => handTip(NOUNS[i], CELLS[i][0] + 32, CELLS[i][1] + 34, 70, p) },
    { a: doodleWindow(i)[0] + 2, z: doodleWindow(i)[1], at: (p) => onStrokes(DOODLES[i], p) },
  ]),
  { a: markWindow[0], z: markWindow[1], at: (p) => onStrokes(MARK_RING, p) },
  { a: CTA.draw[0], z: CTA.draw[1], at: (p) => onStrokes(BTN_LINE, p) },
  { a: CTA.ask[0], z: CTA.ask[1], at: (p) => handTip('Какой план нарисовать', safe.left, 940, 68, p) },
  { a: HEAD_REWRITE[0], z: HEAD_REWRITE[1], at: (p) => handTip(HEAD, HEAD_AT.x, HEAD_AT.y, HEAD_AT.px, p) },
  { a: T.end - 24, z: T.end, at: (p) => onStrokes(FRAMES[0], 0.15 * p) },
];

// лаймовая обводка первого квадрата перед переворотом
const MARK_RING: Stroke[] = (() => {
  const [cx, cy] = CELLS[0];
  const pts: Pt[] = [];
  for (let a = -2.2; a <= 4.4; a += 0.2) pts.push([cx + CELL / 2 + Math.cos(a) * (CELL * 0.72), cy + CELL / 2 + Math.sin(a) * (CELL * 0.66)]);
  let len = 0;
  for (let k = 1; k < pts.length; k++) len += Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]);
  return [{ pts, len }];
})();

const REST: Pt = [1000, 1700];
const tip = (frame: number): { at: Pt; seen: number } => {
  const now = TASKS.find((t) => frame >= t.a && frame <= t.z);
  // пока квадраты переворачиваются и играют, карандаш уходит за край листа
  const gone = ease(frame, markWindow[1] + 4, markWindow[1] + 20, curve.in) * (1 - ease(frame, T.cta - 10, T.cta + 6, curve.out));
  if (now) return { at: now.at(ease(frame, now.a, now.z, curve.calm)), seen: 1 - gone };
  const prev = [...TASKS].filter((t) => t.z < frame).sort((x, y) => y.z - x.z)[0];
  const next = [...TASKS].filter((t) => t.a > frame).sort((x, y) => x.a - y.a)[0];
  const from = prev ? prev.at(1) : REST;
  const to = next ? next.at(0) : REST;
  const k = prev && next ? ease(frame, prev.z, next.a, curve.both) : 0;
  const at: Pt = [from[0] + (to[0] - from[0]) * k, from[1] + (to[1] - from[1]) * k];
  const offscreen: Pt = [W + 260, at[1] + 200];
  return { at: [at[0] + (offscreen[0] - at[0]) * gone, at[1] + (offscreen[1] - at[1]) * gone], seen: 1 };
};

// ── Сцены ───────────────────────────────────────────────────────────────────────────────
const Sheet: React.FC<{ frame: number }> = ({ frame }) => {
  const markP = drawn(frame, markWindow, linear);
  const markOut = ease(frame, FLIPS[0] + 10, FLIPS[0] + 24);
  const headOut = frame >= T.loop ? 0 : ease(frame, T.grow - 10, T.grow + 6);
  const headIn = frame >= T.loop ? ease(frame, ...HEAD_REWRITE, linear) : 1;
  return (
    <>
      <div style={{ opacity: 1 - headOut }}>
        <Hand text={HEAD} x={HEAD_AT.x} y={HEAD_AT.y} px={HEAD_AT.px} p={frame >= T.cta && frame < T.loop ? 0 : headIn} width={900} />
      </div>
      {frame < T.cta && [0, 1, 2, 3].map((i) => (
        <div key={i} style={{ opacity: 1 - ease(frame, T.grow - 4, T.grow + 14) }}>
          <Hand text={VERBS[i]} x={CELLS[i][0] + 10} y={CELLS[i][1] + CELL + 8} px={54} p={drawn(frame, verbWindow(i), linear)} rotate={-2} />
        </div>
      ))}
      <svg width={W} height={1920} style={{ position: 'absolute', inset: 0, overflow: 'visible', opacity: 1 - markOut }}>
        {markP > 0 && <Line s={MARK_RING[0]} p={markP} width={18} ink={MARK} />}
      </svg>
      {(frame < T.cta + 20 || frame >= T.loop) && [3, 2, 1, 0].map((i) => <Cell key={i} i={i} frame={frame} />)}
    </>
  );
};

const Cta: React.FC<{ frame: number }> = ({ frame }) => {
  if (frame < T.cta || frame >= T.loop + 30) return null;
  const out = ease(frame, T.loop - 4, T.loop + 14);
  const pLine = drawn(frame, CTA.draw);
  const fill = ease(frame, CTA.fill - 10, CTA.fill, curve.out);
  const press = hit(frame, CTA.fill, 10);
  return (
    <AbsoluteFill style={{ opacity: 1 - out }}>
      <Hand text="План стал роликом" x={HEAD_AT.x} y={HEAD_AT.y} px={HEAD_AT.px} p={ease(frame, T.cta + 2, T.cta + 22, linear)} width={900} />
      <div style={{ position: 'absolute', left: BTN.x, top: BTN.y, width: BTN.w, height: BTN.h, transform: `scale(${1 - press * 0.04})` }}>
        <div style={{ position: 'absolute', inset: 8, borderRadius: 999, background: MARK, clipPath: `inset(0 ${(1 - fill) * 100}% 0 0)` }} />
        <svg width={W} height={1920} viewBox={`${BTN.x} ${BTN.y} ${W} 1920`} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible' }}>
          <Line s={BTN_LINE[0]} p={pLine} width={6} />
        </svg>
        <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: sans, fontWeight: 800, fontSize: 76, color: INK, letterSpacing: '-0.025em', opacity: enter(frame, CTA.draw[0] + 8, 12) }}>
          Подписаться
        </div>
      </div>
      <Hand text="Какой план нарисовать следующим?" x={safe.left} y={940} px={68} p={drawn(frame, CTA.ask, linear)} width={820} rotate={-1} />
      <Img src={staticFile('v2-words/end.jpg')} style={{
        position: 'absolute', left: 300, top: 1120, width: 760, opacity: enter(frame, T.cta + 36, 14),
        transform: `translateY(${(1 - enter(frame, T.cta + 36, 14)) * 80}px)`,
        maskImage: 'linear-gradient(180deg,#000 70%,transparent 100%)', WebkitMaskImage: 'linear-gradient(180deg,#000 70%,transparent 100%)',
      }} />
    </AbsoluteFill>
  );
};

const SOUNDS: [number, string, number][] = [
  ...FLIPS.map((f, i): [number, string, number] => [f, 'whoosh.wav', 0.22 + i * 0.04]),
  [T.grow, 'whoosh.wav', 0.4],
  [T.cta, 'whoosh.wav', 0.3],
  [CTA.fill, 'click.wav', 0.5],
];

export type PencilProps = { music: boolean };

export const PencilReel: React.FC<PencilProps> = ({ music }) => {
  const frame = useCurrentFrame();
  const pencil = tip(frame);
  return (
    <AbsoluteFill style={{ background: PAPER }}>
      <Paper />
      <Sheet frame={frame} />
      <Cta frame={frame} />
      <PencilShape at={pencil.at} opacity={pencil.seen} tilt={28 + Math.sin(frame / 7) * 2} />
      {/* субтитры: над квадратами, пока лист с набросками; внизу, пока кадр во весь экран */}
      <AbsoluteFill style={{ zIndex: 10 }}>
        <Captions words={words as Word[]} top={392} px={52} tone="light" hide={[[0, BAR], [T.grow + 10, LENGTH]]} />
        <Captions words={words as Word[]} top={1416} px={50} tone="light" hide={[[0, T.grow + 10], [T.cta, LENGTH]]} />
      </AbsoluteFill>
      {music && <Audio src={staticFile('series/r9.m4a')} volume={0.92} />}
      {SOUNDS.map(([from, name, volume], i) => (
        <Sequence key={i} from={from} layout="none"><Audio src={staticFile(`sfx/${name}`)} volume={volume} /></Sequence>
      ))}
    </AbsoluteFill>
  );
};
