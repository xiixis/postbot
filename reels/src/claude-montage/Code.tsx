// Код, который пишет Claude. Строки настоящие: так в этом ролике появляется его первая фраза.
import React from 'react';
import { useCurrentFrame } from 'remotion';
import { at, color, enter, leave, mono, safe, size } from './tokens';

type Part = [string, 'plain' | 'word' | 'said'];
const CODE: Part[][] = [
  [['const', 'word'], [' frame = ', 'plain'], ['useCurrentFrame', 'word'], ['();', 'plain']],
  [],
  [['const', 'word'], [' show = ', 'plain'], ['interpolate', 'word'], ['(', 'plain']],
  [['  frame, [0, 24], [0, 1],', 'plain']],
  [['  { easing: Easing.', 'plain'], ['out', 'word'], ['(Easing.exp) },', 'plain']],
  [[');', 'plain']],
  [],
  [['return', 'word'], [' (', 'plain']],
  [['  <', 'plain'], ['Headline', 'word'], [' style={{ opacity: show }}>', 'plain']],
  [['    Этот ролик никто не монтировал', 'said']],
  [['  </', 'plain'], ['Headline', 'word'], ['>', 'plain']],
  [[');', 'plain']],
];
const INK: Record<Part[1], string> = { plain: 'rgba(241,242,234,0.72)', word: color.ink, said: color.action };
const LEADING = 54;
const FROM = at.code + 20;      // поле с просьбой к этому кадру уже уехало наверх

export const Code: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame < FROM - 2 || frame > at.frames + 14) return null;
  const out = leave(frame, at.frames - 4, 14);
  return (
    <div style={{
      position: 'absolute', left: safe.left, top: 690, opacity: 1 - out,
      transform: `scale(${1 - out * 0.03})`, transformOrigin: 'left top',
      fontFamily: mono, fontWeight: 500, fontSize: size.code, lineHeight: `${LEADING}px`, whiteSpace: 'pre',
    }}>
      {CODE.map((line, i) => {
        const t = enter(frame, FROM + i * 1.6, 14);
        return (
          <div key={i} style={{ height: LEADING, opacity: t, transform: `translateY(${(1 - t) * 14}px)` }}>
            {line.map(([text, kind], k) => <span key={k} style={{ color: INK[kind] }}>{text}</span>)}
          </div>
        );
      })}
    </div>
  );
};
