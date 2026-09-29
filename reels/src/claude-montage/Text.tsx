// Текст ролика: крючок, подписи-рассказ и общий курсор.
import React from 'react';
import { useCurrentFrame } from 'remotion';
import { at, color, column, enter, leave, safe, sans, size } from './tokens';

// Лаймовый курсор — сквозная примета ролика: им «пишет» Claude.
export const Cursor: React.FC<{ height: number; on?: boolean }> = ({ height, on = true }) => {
  const frame = useCurrentFrame();
  const blink = 0.35 + 0.65 * (0.5 + 0.5 * Math.cos((frame / 27) * Math.PI * 2));
  return (
    <span style={{
      display: 'inline-block', width: Math.max(8, Math.round(height * 0.085)), height, marginLeft: height * 0.1,
      verticalAlign: `${-height * 0.12}px`, borderRadius: 3, background: color.action, opacity: on ? blink : 0,
      boxShadow: '0 0 28px rgba(199,226,75,0.55)',
    }} />
  );
};

export const Claude: React.FC = () => <span style={{ color: color.claude }}>Claude</span>;

const display: React.CSSProperties = {
  fontFamily: sans, fontWeight: 700, color: color.ink, letterSpacing: '-0.035em', whiteSpace: 'nowrap',
};

// Строка выезжает из-под шторки. Высота шторки с запасом под выносные элементы букв.
export const Line: React.FC<{ children: React.ReactNode; px: number; from: number; dur?: number; tight?: number }> = ({
  children, px, from, dur = 26, tight = 1.06,
}) => {
  const frame = useCurrentFrame();
  const t = enter(frame, from, dur);
  const box = px * 1.3;
  return (
    <div style={{ height: box, overflow: 'hidden', marginBottom: px * tight - box }}>
      <div style={{ ...display, fontSize: px, lineHeight: `${box}px`, transform: `translateY(${(1 - t) * box}px)` }}>{children}</div>
    </div>
  );
};

const HOOK = ['Этот ролик', 'никто не', 'монтировал'];

export const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const out = leave(frame, at.prompt - 14, 14);
  if (out >= 1) return null;
  return (
    <div style={{ position: 'absolute', left: safe.left, top: 520, opacity: 1 - out, transform: `translateY(${-out * 46}px)` }}>
      {HOOK.map((line, i) => (
        <Line key={line} px={size.display} from={-14 + i * 4}>
          {line}{i === HOOK.length - 1 && <Cursor height={size.display * 0.86} />}
        </Line>
      ))}
    </div>
  );
};

// Подписи ведут рассказ: одна мысль на такт, всегда на одном месте.
const STORY: { from: number; to: number; lines: React.ReactNode[] }[] = [
  // Не «одну строку»: на деле было описание из нескольких фраз и круг правок.
  { from: at.prompt, to: at.code, lines: ['Я описал его', 'словами'] },
  { from: at.code, to: at.frames, lines: [<Claude key="c" />, 'написал код'] },
  { from: at.frames, to: at.reveal, lines: ['Код стал', 'кадрами'] },
];

export const Story: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      {STORY.map((s) => {
        if (frame < s.from - 2 || frame > s.to + 6) return null;
        const out = leave(frame, s.to - 8, 10);
        return (
          <div key={s.from} style={{
            position: 'absolute', left: safe.left, top: safe.top, width: column,
            opacity: 1 - out, transform: `translateY(${-out * 20}px)`,
          }}>
            {s.lines.map((l, i) => <Line key={i} px={size.title} from={s.from + 4 + i * 4} dur={24} tight={1.1}>{l}</Line>)}
          </div>
        );
      })}
    </>
  );
};
