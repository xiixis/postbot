// Два плана и их 450 клеток, по клетке на кадр ролика.
// В начале стоит крупный план: кот смотрит в камеру, это обложка ролика. Он разбирается на
// клетки. В середине код собирает из клеток уже другой, общий план: кот за монтажным столом.
// Планы разные нарочно: одна картинка в начале и в конце съедала развязку.
import React from 'react';
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import { H, TOTAL, W, at, color, enter, glide, leave, mix, mono, safe, steady } from './tokens';

const COLS = 15;
const ROWS = TOTAL / COLS;          // 30 рядов: 15 × 30 = 450
const CW = W / COLS;
const CH = H / ROWS;
const GAP = 3;
const TRAIL = 40;                   // сколько клеток у бегущего кадра ещё светятся

// Начало: отъезд камеры, потом клетки расходятся и гаснут с конца к началу.
const PULL = 38;                    // к этому кадру камера встала
export const UNDO_FROM = 44;
export const UNDO_TO = 66;

// Середина: клетки открываются по порядку и смыкаются.
const RUN_FROM = at.frames + 8;
const RUN_TO = at.reveal - 6;
const SHUT = at.reveal;
const WHOLE = SHUT + 18;            // дальше одна цельная картинка

const OPENING = staticFile('claude-montage/opening.jpg');
const SCENE = staticFile('claude-montage/scene.jpg');
const FOCUS = '60% 56%';            // голова кота на общем плане: на неё наезжает камера
// Крупный план увеличен от верхнего края: так уши кота стоят ниже заголовка на всём отъезде.
const TOP = '50% 0%';
const CLOSE = 1.06;

export const rendered = (frame: number) => Math.round(steady(frame, RUN_FROM, RUN_TO) * TOTAL);

const Whole: React.FC<{ src: string; scale: number; origin: string }> = ({ src, scale, origin }) => (
  <AbsoluteFill style={{ overflow: 'hidden' }}>
    <Img src={src} style={{ width: W, height: H, transform: `scale(${scale})`, transformOrigin: origin }} />
  </AbsoluteFill>
);

// edge — сколько клеток открыто; ahead — с какой стороны от края лежит светящийся след.
const Cells: React.FC<{ src: string; edge: number; ahead: boolean; gap: number; radius: number; outline: number; glow: number }> = ({
  src, edge, ahead, gap, radius, outline, glow,
}) => {
  const cells: React.ReactNode[] = [];
  for (let i = 0; i < TOTAL; i++) {
    const open = i < edge;
    const far = ahead ? i - edge : edge - i;
    const lit = (ahead ? !open : open) && far < TRAIL ? (1 - far / TRAIL) * glow : 0;
    if (!open && outline <= 0.01 && lit <= 0.01) continue;
    const x = (i % COLS) * CW + gap;
    const y = Math.floor(i / COLS) * CH + gap;
    cells.push(
      <div key={i} style={{
        position: 'absolute', left: x, top: y, width: CW - gap * 2, height: CH - gap * 2, borderRadius: radius, overflow: 'hidden',
        backgroundImage: open ? `url(${src})` : undefined, backgroundSize: `${W}px ${H}px`, backgroundPosition: `${-x}px ${-y}px`,
        boxShadow: open ? undefined : `inset 0 0 0 1.5px rgba(241,242,234,${0.11 * outline})`,
      }}>
        {lit > 0.01 && <div style={{ position: 'absolute', inset: 0, background: color.action, opacity: lit * 0.92 }} />}
      </div>,
    );
  }
  return <AbsoluteFill>{cells}</AbsoluteFill>;
};

export const Frames: React.FC = () => {
  const frame = useCurrentFrame();

  // Начало: крупный план, камера отъезжает от кота.
  if (frame < PULL) return <Whole src={OPENING} origin={TOP} scale={mix(enter(frame, 0, PULL), 1.34, CLOSE)} />;

  // Крупный план разбирается на клетки.
  if (frame < UNDO_TO + 10) {
    const apart = enter(frame, PULL, 8);
    return (
      <AbsoluteFill style={{ transform: `scale(${CLOSE})`, transformOrigin: TOP }}>
        <Img src={SCENE} style={{ position: 'absolute', width: 1, height: 1, opacity: 0 }} />
        <Cells
          src={OPENING} edge={TOTAL * (1 - steady(frame, UNDO_FROM, UNDO_TO))} ahead
          gap={mix(apart, 0, GAP)} radius={mix(apart, 0, 9)}
          outline={apart * (1 - steady(frame, UNDO_TO - 4, UNDO_TO + 10))} glow={1 - steady(frame, UNDO_TO, UNDO_TO + 8)}
        />
      </AbsoluteFill>
    );
  }

  // Пока идут просьба и код, сцены в кадре нет; картинка остаётся загруженной.
  if (frame < at.frames - 6) return <Img src={SCENE} style={{ position: 'absolute', width: 1, height: 1, opacity: 0 }} />;

  if (frame >= WHOLE) return <Whole src={SCENE} origin={FOCUS} scale={mix(glide(frame, WHOLE, TOTAL - WHOLE), 1, 1.05)} />;

  // Код собирает сцену обратно.
  const shut = enter(frame, SHUT, 18);
  return (
    <Cells
      src={SCENE} edge={steady(frame, RUN_FROM, RUN_TO) * TOTAL} ahead={false}
      gap={mix(shut, GAP, 0)} radius={mix(shut, 9, 0)}
      outline={enter(frame, at.frames - 4, 22)} glow={1 - shut}
    />
  );
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
