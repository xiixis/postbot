// Ролик «Этот ролик никто не монтировал»: 15 секунд, 1080×1920, один непрерывный план.
// Шесть состояний по такту музыки: крючок, просьба, код, кадры, развязка, призыв.
// Начинается с готовой сцены, как с обложки: первый кадр решает, остановится ли зритель.
// Склеек нет: каждое состояние вырастает из предыдущего, всё движется в одной манере.
// Спека: docs/superpowers/specs/2026-09-29-ролик-claude-монтаж-design.md
import React from 'react';
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { Code } from './Code';
import { CTA, PRESS, Reveal } from './Ending';
import { Counter, Frames, UNDO_FROM, UNDO_TO } from './Frames';
import { KEYS, Prompt, SEND, SPACE } from './Prompt';
import { Hook, Story } from './Text';
import { H, W, at, color, enter, leave } from './tokens';

// Какую музыку вшить: a тёплая, b кино, c ночь, d плавный хип-хоп, e бум-бэп —
// или none, когда музыку подкладывают после рендера.
export type FilmProps = { music: 'a' | 'b' | 'c' | 'd' | 'e' | 'none' };

// Земля первых секунд — та же сцена, но не в фокусе: свет и цвет в кадре одни с первого кадра.
const Ground: React.FC = () => (
  <AbsoluteFill style={{ background: color.ground }}>
    <Img src={staticFile('claude-montage/scene-soft.jpg')} style={{ width: W, height: H }} />
    <AbsoluteFill style={{ background: 'rgba(14,15,12,0.38)' }} />
  </AbsoluteFill>
);

// Подложка под текст, пока под ним сцена и бегущие лаймовые клетки: в начале под крючком,
// в середине под подписью.
const Scrim: React.FC = () => {
  const frame = useCurrentFrame();
  const hook = 1 - leave(frame, UNDO_TO - 8, 16);
  const story = enter(frame, at.frames - 6, 20) * (1 - leave(frame, at.reveal + 4, 20));
  return (
    <>
      {hook > 0 && <AbsoluteFill style={{ opacity: hook, background: 'linear-gradient(180deg, rgba(11,12,9,0.78) 0%, rgba(11,12,9,0.7) 34%, rgba(11,12,9,0) 50%)' }} />}
      {story > 0 && <AbsoluteFill style={{ opacity: story, background: 'linear-gradient(180deg, rgba(11,12,9,0.9) 0%, rgba(11,12,9,0.82) 22%, rgba(11,12,9,0) 36%)' }} />}
    </>
  );
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
// У клавиш пять разных тонов и своя громкость у каждой, пробел и ввод ниже и глуше:
// один и тот же щелчок пятнадцать раз подряд звучит как метроном (tools/keys.py).
const SOUNDS: [number, string, number][] = [
  ...KEYS.map((k, i): [number, string, number] => [k, i === SPACE ? 'key-space' : `key-${((i * 2) % 5) + 1}`, 0.3 + ((i * 37) % 9) / 100]),
  [UNDO_FROM - 2, 'whoosh', 0.14],
  [SEND, 'key-space', 0.5],
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
