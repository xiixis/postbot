// Код становится кадрами: 450 клеток, по клетке на кадр ролика. Бегущий кадр проходит их по
// порядку и открывает сцену; когда доходит до конца, клетки смыкаются в цельную картинку.
import React from 'react';
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import { H, TOTAL, W, at, color, enter, glide, leave, mix, mono, safe, steady } from './tokens';

const COLS = 15;
const ROWS = TOTAL / COLS;          // 30 рядов: 15 × 30 = 450
const CW = W / COLS;
const CH = H / ROWS;
const GAP = 3;
const TRAIL = 40;                   // сколько клеток за бегущим кадром ещё светятся
const RUN_FROM = at.frames + 8;
const RUN_TO = at.reveal - 6;
const SHUT = at.reveal;             // клетки смыкаются
const WHOLE = SHUT + 18;            // дальше одна цельная картинка

const SCENE = staticFile('claude-montage/scene.jpg');

export const rendered = (frame: number) => Math.round(steady(frame, RUN_FROM, RUN_TO) * TOTAL);

export const Frames: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame < at.frames - 6) {
    // Картинка грузится заранее, чтобы первая клетка не ждала её.
    return <Img src={SCENE} style={{ position: 'absolute', width: 1, height: 1, opacity: 0 }} />;
  }

  if (frame >= WHOLE) {
    const push = glide(frame, WHOLE, TOTAL - WHOLE);
    return (
      <AbsoluteFill style={{ overflow: 'hidden' }}>
        <Img src={SCENE} style={{ width: W, height: H, transform: `scale(${mix(push, 1, 1.05)})`, transformOrigin: '60% 56%' }} />
      </AbsoluteFill>
    );
  }

  const appear = enter(frame, at.frames - 4, 22);
  const done = steady(frame, RUN_FROM, RUN_TO) * TOTAL;
  const shut = enter(frame, SHUT, 18);
  const gap = mix(shut, GAP, 0);
  const radius = mix(shut, 9, 0);
  const cells: React.ReactNode[] = [];
  for (let i = 0; i < TOTAL; i++) {
    const c = i % COLS;
    const r = Math.floor(i / COLS);
    const open = i < done;
    const glow = open ? Math.max(0, 1 - (done - i) / TRAIL) * (1 - shut) : 0;
    const x = c * CW + gap;
    const y = r * CH + gap;
    cells.push(
      <div key={i} style={{
        position: 'absolute', left: x, top: y, width: CW - gap * 2, height: CH - gap * 2, borderRadius: radius, overflow: 'hidden',
        backgroundImage: open ? `url(${SCENE})` : undefined, backgroundSize: `${W}px ${H}px`, backgroundPosition: `${-x}px ${-y}px`,
        boxShadow: open ? undefined : `inset 0 0 0 1.5px rgba(241,242,234,${0.11 * appear})`,
      }}>
        {glow > 0.01 && <div style={{ position: 'absolute', inset: 0, background: color.action, opacity: glow * 0.92 }} />}
      </div>,
    );
  }
  return <AbsoluteFill>{cells}</AbsoluteFill>;
};

export const Counter: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame < at.frames || frame > at.reveal + 14) return null;
  const inn = enter(frame, at.frames + 4, 22);
  const out = leave(frame, at.reveal, 12);
  return (
    <div style={{
      position: 'absolute', left: safe.left, top: 1404, opacity: inn * (1 - out), transform: `translateY(${(1 - inn) * 18}px)`,
      padding: '14px 28px', borderRadius: 20, background: 'rgba(11,12,9,0.72)',
      fontFamily: mono, fontWeight: 500, fontSize: 46, color: color.ink, fontVariantNumeric: 'tabular-nums', whiteSpace: 'pre',
    }}>
      кадр <span style={{ color: color.action }}>{String(rendered(frame)).padStart(3, ' ')}</span> из {TOTAL}
    </div>
  );
};
