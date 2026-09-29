// Строка-просьба: печатается, отправляется и уходит наверх, уступая место коду.
import React from 'react';
import { useCurrentFrame } from 'remotion';
import { Cursor } from './Text';
import { at, color, column, enter, glide, leave, mix, mono, safe, steady } from './tokens';

const ASK = 'смонтируй ролик';
const TYPE_FROM = at.prompt + 18;
export const SEND = at.prompt + 60;
// Человек печатает неровно: где-то быстрее, перед пробелом и после него медлит.
// Числа — сколько кадров проходит перед каждой следующей клавишей.
const PAUSES = [0, 2, 2, 3, 2, 2, 3, 2, 2, 3, 4, 2, 2, 3, 2];
export const SPACE = ASK.indexOf(' ');
export const KEYS = PAUSES.reduce<number[]>((all, p, i) => [...all, (i ? all[i - 1] : TYPE_FROM) + p], []);

export const Prompt: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame < at.prompt || frame > at.frames + 8) return null;
  const inn = enter(frame, at.prompt + 2, 26);
  const up = glide(frame, at.code - 4, 24);
  const out = leave(frame, at.frames - 8, 12);
  const typed = KEYS.filter((k) => frame >= k).length;
  const full = typed === ASK.length;
  const sent = frame >= SEND;
  const press = frame >= SEND - 3 && frame < SEND ? 0.9 : mix(enter(frame, SEND, 10), 0.9, 1);
  const flash = sent ? 1 - steady(frame, SEND, SEND + 20) : 0;

  return (
    <div style={{
      position: 'absolute', left: safe.left, top: mix(up, 850, 500), width: column, height: 176,
      transform: `translateY(${(1 - inn) * 46}px) scale(${mix(up, 1, 0.66)})`, transformOrigin: 'left top',
      opacity: inn * (1 - out) * mix(up, 1, 0.82),
      borderRadius: 44, background: 'rgba(11,12,9,0.62)',
      boxShadow: `inset 0 0 0 2px rgba(${sent ? '199,226,75' : '241,242,234'},${sent ? 0.35 + flash * 0.65 : 0.2}), 0 30px 80px rgba(0,0,0,0.45)`,
      display: 'flex', alignItems: 'center', padding: '0 28px 0 46px', justifyContent: 'space-between',
    }}>
      <div style={{ fontFamily: mono, fontWeight: 500, fontSize: 66, color: color.ink, whiteSpace: 'pre', letterSpacing: '-0.02em' }}>
        {ASK.slice(0, typed)}
        <Cursor height={70} on={!sent} />
      </div>
      <div style={{
        width: 112, height: 112, borderRadius: 56, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: full ? color.action : 'rgba(241,242,234,0.12)', transform: `scale(${press})`,
        boxShadow: full ? `0 0 ${30 + flash * 50}px rgba(199,226,75,${0.35 + flash * 0.4})` : undefined,
      }}>
        <svg width="54" height="54" viewBox="0 0 24 24" fill="none" stroke={full ? color.ground : color.ink} strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" opacity={full ? 1 : 0.5}>
          <path d="M12 19V5M5.5 11.5 12 5l6.5 6.5" />
        </svg>
      </div>
    </div>
  );
};
