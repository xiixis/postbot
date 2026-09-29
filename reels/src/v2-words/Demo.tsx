// Четыре картинки к словам «текст», «кадры», «движение», «звук». Каждая живёт один такт, 72 кадра.
// Каждая показывает дело, а не украшает: строки печатаются, кадры заполняются, точка едет по
// кривой, полосы звука прыгают в такт.
import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';
import { color, column, curve, enter, rnd } from '../lib/brand';
import { hit } from '../lib/beat';

const BOX = { width: column, height: 600 } as const;
const BEAT = 18;

// Строки текста: полосы растут слева направо, как при наборе, в конце строки стоит курсор.
export const Lines: React.FC = () => {
  const frame = useCurrentFrame();
  const rows = [0.92, 0.74, 0.86, 0.6, 0.8, 0.42];
  return (
    <div style={{ ...BOX, display: 'flex', flexDirection: 'column', gap: 44, justifyContent: 'center' }}>
      {rows.map((w, i) => {
        const t = interpolate(frame, [10 + i * 8, 22 + i * 8], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
        const typing = t > 0 && t < 1;
        return (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, height: 56 }}>
            <div style={{ width: column * w * t, height: 56, borderRadius: 16, background: i === rows.length - 1 ? color.olive : color.graphite }} />
            <div style={{ width: 12, height: 72, borderRadius: 4, background: color.lime, opacity: typing ? 1 : 0, boxShadow: `0 0 0 3px ${color.graphite}` }} />
          </div>
        );
      })}
    </div>
  );
};

// Кадры: пятнадцать вертикальных кадров заполняются по одному.
export const Grid: React.FC = () => {
  const frame = useCurrentFrame();
  const cols = 5, rows = 3, gap = 18;
  const w = (column - gap * (cols - 1)) / cols;
  const h = (BOX.height - gap * (rows - 1)) / rows;
  return (
    <div style={{ ...BOX, position: 'relative' }}>
      {new Array(cols * rows).fill(0).map((_, i) => {
        const at = 10 + i * 3.2;
        const fill = enter(frame, at, 8);
        const fresh = hit(frame, Math.round(at), 10);
        return (
          <div key={i} style={{
            position: 'absolute', left: (i % cols) * (w + gap), top: Math.floor(i / cols) * (h + gap), width: w, height: h,
            borderRadius: 22, boxShadow: `inset 0 0 0 4px ${color.graphite}`, overflow: 'hidden',
          }}>
            <div style={{
              position: 'absolute', inset: 0, transform: `translateY(${(1 - fill) * 101}%)`,
              background: fresh > 0.05 ? color.lime : color.graphite,
            }} />
          </div>
        );
      })}
    </div>
  );
};

// Движение: точка едет по кривой, за ней остаётся след.
const CURVE = [
  [[30, 520], [200, 60], [380, 60], [430, 300]],
  [[430, 300], [480, 540], [640, 570], [790, 90]],
];
const point = (k: number) => {
  const seg = CURVE[k < 0.5 ? 0 : 1];
  const u = k < 0.5 ? k * 2 : (k - 0.5) * 2;
  const p = (i: number) => (1 - u) ** 3 * seg[0][i] + 3 * (1 - u) ** 2 * u * seg[1][i] + 3 * (1 - u) * u ** 2 * seg[2][i] + u ** 3 * seg[3][i];
  return [p(0), p(1)];
};
const STEPS = 120;
const line = (upTo: number) => {
  const n = Math.max(1, Math.round(upTo * STEPS));
  return new Array(n + 1).fill(0)
    .map((_, i) => point((i / n) * upTo))
    .map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`)
    .join(' ');
};

export const Path: React.FC = () => {
  const frame = useCurrentFrame();
  const t = enter(frame, 10, 50, curve.both);
  const [x, y] = point(t);
  return (
    <svg width={BOX.width} height={BOX.height} viewBox={`0 0 ${BOX.width} ${BOX.height}`} style={{ overflow: 'visible' }}>
      <path d={line(1)} fill="none" stroke={color.graphite} strokeOpacity={0.16} strokeWidth={10} strokeLinecap="round" strokeDasharray="4 26" />
      <path d={line(Math.max(t, 0.001))} fill="none" stroke={color.graphite} strokeWidth={14} strokeLinecap="round" strokeLinejoin="round" />
      <circle cx={x} cy={y} r={44} fill={color.lime} stroke={color.graphite} strokeWidth={8} />
    </svg>
  );
};

// Звук: полосы прыгают в такт. Высота каждой своя, толчок общий на каждый удар.
export const Wave: React.FC = () => {
  const frame = useCurrentFrame();
  const n = 22, gap = 14;
  const w = (column - gap * (n - 1)) / n;
  const beatNow = Math.max(...[0, 1, 2, 3].map((n) => hit(frame, BEAT * n, 12)));
  return (
    <div style={{ ...BOX, display: 'flex', alignItems: 'center', gap }}>
      {new Array(n).fill(0).map((_, i) => {
        const grow = enter(frame, 4 + i * 0.7, 10);
        const own = 0.25 + rnd(i * 3.7) * 0.5;
        const live = 0.5 + 0.5 * Math.sin(frame / 2.2 + i * 1.3);
        const height = BOX.height * Math.min(1, own * (0.55 + 0.45 * live) + beatNow * 0.35 * (i % 3 === 0 ? 1 : 0.5)) * grow;
        return <div key={i} style={{ width: w, height, borderRadius: w / 2, background: i % 3 === 0 ? color.lime : color.graphite, boxShadow: i % 3 === 0 ? `inset 0 0 0 4px ${color.graphite}` : undefined }} />;
      })}
    </div>
  );
};
