// Субтитры по словам: слово подсвечивается ровно в тот миг, когда звучит.
// Время слов снимает распознавание с готовой дорожки голоса (tools/words.py) и кладёт в
// src/series/words/<ролик>.json. Пока файла нет, строка пустая: ролик собирается без неё.
import React from 'react';
import { useCurrentFrame } from 'remotion';
import { color, enter, leave, safe, sans } from '../lib/brand';

export type Word = { w: string; s: number; e: number; line: number };

type Props = { words: Word[]; top?: number; px?: number; hide?: [number, number][]; align?: 'left' | 'center'; tone?: 'dark' | 'light' };

// Тёмный фон: слово крем, текущее лаймом. Светлая страница: слово графит, текущее оливой.
const TONES = {
  dark: { now: color.lime, said: color.cream, wait: 'rgba(241,242,234,0.42)', shadow: '0 2px 18px rgba(0,0,0,0.45)' },
  light: { now: color.olive, said: color.graphite, wait: 'rgba(18,19,15,0.34)', shadow: '0 0 14px rgba(236,234,222,0.95)' },
};

// Строки субтитров собираются по номеру фразы: одна фраза появляется целиком, слова
// зажигаются по очереди, фраза уходит через треть секунды после последнего слова.
export const Captions: React.FC<Props> = ({ words, top = 1290, px = 56, hide = [], align = 'left', tone = 'dark' }) => {
  const c = TONES[tone];
  const frame = useCurrentFrame();
  const t = frame / 30;
  if (hide.some(([a, z]) => frame >= a && frame < z)) return null;
  const lines = new Map<number, Word[]>();
  words.forEach((w) => lines.set(w.line, [...(lines.get(w.line) ?? []), w]));
  const current = [...lines.values()].find((ws) => t >= ws[0].s - 0.12 && t < ws[ws.length - 1].e + 0.35);
  if (!current) return null;
  const from = Math.round((current[0].s - 0.12) * 30);
  const to = Math.round((current[current.length - 1].e + 0.35) * 30);
  const inn = enter(frame, from, 8);
  const out = leave(frame, to - 6, 6);
  return (
    <div style={{
      position: 'absolute', left: safe.left, top, width: safe.right - safe.left, display: 'flex', flexWrap: 'wrap',
      justifyContent: align === 'center' ? 'center' : 'flex-start', columnGap: px * 0.3, rowGap: px * 0.12,
      fontFamily: sans, fontWeight: 700, fontSize: px, lineHeight: 1.15, letterSpacing: '-0.02em',
      opacity: inn * (1 - out), transform: `translateY(${(1 - inn) * 24}px)`,
    }}>
      {current.map((w, i) => {
        const said = t >= w.s;
        const now = t >= w.s && t < w.e + 0.08;
        return (
          <span key={i} style={{
            color: now ? c.now : said ? c.said : c.wait,
            transform: `scale(${now ? 1.06 : 1})`, transformOrigin: '50% 100%', display: 'inline-block',
            textShadow: c.shadow,
          }}>
            {w.w}
          </span>
        );
      })}
    </div>
  );
};
