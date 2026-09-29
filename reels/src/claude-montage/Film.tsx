// Ролик «Этот ролик никто не монтировал»: 15 секунд, 1080×1920, один непрерывный план.
// Шесть состояний по такту музыки: крючок, просьба, код, кадры, развязка, призыв.
// Склеек нет: каждое состояние вырастает из предыдущего, всё движется в одной манере.
// Спека: docs/superpowers/specs/2026-09-29-ролик-claude-монтаж-design.md
import React from 'react';
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { Code } from './Code';
import { CTA, PRESS, Reveal } from './Ending';
import { Counter, Frames } from './Frames';
import { KEYS, Prompt, SEND } from './Prompt';
import { Hook, Story } from './Text';
import { H, W, at, color, enter, leave } from './tokens';

// Какую музыку вшить: a, b, c — или none, когда музыку подкладывают после рендера.
export type FilmProps = { music: 'a' | 'b' | 'c' | 'none' };

// Земля первых секунд — та же сцена, но не в фокусе: свет и цвет в кадре одни с первого кадра.
const Ground: React.FC = () => (
  <AbsoluteFill style={{ background: color.ground }}>
    <Img src={staticFile('claude-montage/scene-soft.jpg')} style={{ width: W, height: H }} />
    <AbsoluteFill style={{ background: 'rgba(14,15,12,0.38)' }} />
  </AbsoluteFill>
);

// Подложка под подпись на время счёта кадров: бегущие лаймовые клетки проходят и под текстом.
const Scrim: React.FC = () => {
  const frame = useCurrentFrame();
  const t = enter(frame, at.frames - 6, 20) * (1 - leave(frame, at.reveal + 4, 20));
  if (t <= 0) return null;
  return <AbsoluteFill style={{ opacity: t, background: 'linear-gradient(180deg, rgba(11,12,9,0.9) 0%, rgba(11,12,9,0.82) 22%, rgba(11,12,9,0) 36%)' }} />;
};

const Finish: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: 'none' }}>
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse 85% 70% at 50% 46%, rgba(0,0,0,0) 52%, rgba(0,0,0,0.42) 100%)' }} />
      <AbsoluteFill style={{ mixBlendMode: 'overlay', opacity: 0.07 }}>
        <svg width={W} height={H}>
          <filter id={`grain-${frame % 6}`}>
            <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={frame % 6} />
            <feColorMatrix type="saturate" values="0" />
          </filter>
          <rect width={W} height={H} filter={`url(#grain-${frame % 6})`} />
        </svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// Звуков мало и они тихие: клавиши, отправка, начало счёта кадров, нажатие кнопки.
const SOUNDS: [number, string, number][] = [
  ...KEYS.map((k): [number, string, number] => [k, 'tick', 0.22]),
  [SEND, 'click', 0.4],
  [at.frames - 2, 'whoosh', 0.16],
  [PRESS, 'click', 0.45],
];

export const Film: React.FC<FilmProps> = ({ music }) => (
  <AbsoluteFill style={{ background: color.ground }}>
    <Ground />
    <Frames />
    <Scrim />
    <Hook />
    <Story />
    <Prompt />
    <Code />
    <Counter />
    <Reveal />
    <CTA />
    <Finish />
    {music !== 'none' && <Audio src={staticFile(`claude-montage/music-${music}.m4a`)} volume={0.92} />}
    {SOUNDS.map(([from, name, volume], i) => (
      <Sequence key={i} from={from} layout="none">
        <Audio src={staticFile(`sfx/${name}.wav`)} volume={volume} />
      </Sequence>
    ))}
  </AbsoluteFill>
);
