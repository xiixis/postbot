// Серия 2, ролик 4: «12 слов, и текст живёт под бит».
//
// Тезис: показ умения gsap и motion-design. После промпта и трёх скилов идёт чистая
// типографика под бит: буквы по одной, слова на ударах, строка по кривой, пульс на такте.
// Ни одной картинки в показе. Характер энергичный, один фон, входы снизу.
import React from 'react';
import gsap from 'gsap';
import { SplitText } from 'gsap/SplitText';
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { hit } from '../lib/beat';
import { color, column, enter, leave, mix, mono, safe, sans, W } from '../lib/brand';
import { useTimeline } from '../lib/gsap';
import { Captions, type Word } from '../series/Captions';
import { b, BAR, BEAT, BPM, LENGTH, T } from '../series/grid';
import { Cta, Headline, Prompt, promptSounds, Save, Show } from '../series/parts';
import words from '../series/words/r4.json';

gsap.registerPlugin(SplitText);

const GROUND = '#12130F';
export const PROMPT = 'Текст живёт под бит: буквы по одной, слова на ударах, без отскоков';
export const SKILLS = ['gsap', 'motion-design', 'genjutsu'];

const big: React.CSSProperties = { fontFamily: sans, fontWeight: 800, fontSize: 150, lineHeight: 1.0, letterSpacing: '-0.035em', color: color.cream, textTransform: 'uppercase' };

// Крючок: кот крупно на весь кадр, заголовок сверху; кот едва заметно наезжает.
const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const out = leave(frame, BAR - 10, 10);
  return (
    <AbsoluteFill>
      <Img src={staticFile('series/opening.jpg')} style={{
        position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover',
        transform: `scale(${mix(enter(frame, -10, 90), 1.12, 1.04)}) translateY(${out * -120}px)`, transformOrigin: '50% 60%', opacity: 1 - out,
      }} />
      <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(18,19,15,0.86) 0%, rgba(18,19,15,0.55) 30%, rgba(18,19,15,0) 55%)' }} />
      <Headline lines={[<span style={{ color: color.lime }}>12 слов</span>, 'и текст живёт', 'под бит']} px={118} />
    </AbsoluteFill>
  );
};

// Шкала долей: четыре точки, текущая доля горит. Вторичный слой всего показа.
const Scale: React.FC = () => {
  const frame = useCurrentFrame();
  const beat = Math.floor(frame / BEAT) % 4;
  const inn = enter(frame, 0, 12);
  return (
    <div style={{ position: 'absolute', left: safe.left, top: 1240, display: 'flex', gap: 22, alignItems: 'center', opacity: inn }}>
      {[0, 1, 2, 3].map((i) => {
        const on = i === beat;
        const pop = hit(frame, Math.floor(frame / BEAT) * BEAT, 8);
        return <div key={i} style={{ width: on ? 64 : 22, height: 22, borderRadius: 11, background: on ? color.lime : 'rgba(241,242,234,0.28)', transform: `scale(${on ? 1 + pop * 0.15 : 1})` }} />;
      })}
      <div style={{ marginLeft: 18, fontFamily: mono, fontWeight: 500, fontSize: 34, color: 'rgba(241,242,234,0.55)' }}>{BPM} bpm · доля {beat + 1}</div>
    </div>
  );
};

// Такт 1: буквы по одной. Каскад в кадр за 15 кадров, кончается к удару.
const Letters: React.FC = () => {
  const frame = useCurrentFrame();
  const root = useTimeline((tl, scope) => {
    scope.querySelectorAll('.l').forEach((el, i) => {
      const s = new SplitText(el, { type: 'chars' });
      tl.from(s.chars, { yPercent: 120, opacity: 0, duration: 0.42, ease: 'expo.out', stagger: 0.035 }, i * 0.2);
    });
  });
  const out = leave(frame, BAR - 7, 7);
  return (
    <AbsoluteFill ref={root} style={{ opacity: 1 - out, transform: `translateY(${-out * 120}px)` }}>
      <div style={{ position: 'absolute', left: safe.left, top: 540 }}>
        <div style={{ overflow: 'hidden' }}><div className="l" style={big}>Разбил</div></div>
        <div style={{ overflow: 'hidden' }}><div className="l" style={big}>текст</div></div>
        <div style={{ overflow: 'hidden' }}><div className="l" style={{ ...big, color: color.lime }}>на буквы</div></div>
      </div>
    </AbsoluteFill>
  );
};

// Такт 2: четыре слова на четыре удара. Слово встаёт ровно на доле и толкается.
const OnBeats: React.FC = () => {
  const frame = useCurrentFrame();
  const out = leave(frame, BAR - 7, 7);
  const items = ['Поставил', 'слова', 'на', 'удары'];
  return (
    <AbsoluteFill style={{ opacity: 1 - out, transform: `translateY(${-out * 120}px)` }}>
      <div style={{ position: 'absolute', left: safe.left, top: 500, width: column, display: 'flex', flexWrap: 'wrap', columnGap: 40, rowGap: 0 }}>
        {items.map((w, i) => {
          const at = b(i);
          const t = enter(frame, at, 9);
          return (
            <div key={w} style={{
              ...big, fontSize: 168, color: i === 3 ? color.lime : color.cream,
              opacity: t, transform: `translateY(${(1 - t) * 60}px) scale(${1 + hit(frame, at, 9) * 0.12})`, transformOrigin: '0% 100%',
            }}>
              {w}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// Такт 3: слово едет по кривой и садится без отскока; сама кривая рисуется под ним.
// Путь считается кубической кривой, кривая времени — наша «появление»: быстрый старт, мягкая посадка.
const PATH = [[80, 1120], [560, 1040], [520, 640], [80, 560]];
const at = (u: number) => {
  const p = (i: number) => (1 - u) ** 3 * PATH[0][i] + 3 * (1 - u) ** 2 * u * PATH[1][i] + 3 * (1 - u) * u ** 2 * PATH[2][i] + u ** 3 * PATH[3][i];
  return [p(0), p(1)];
};
const trail = (upTo: number) => new Array(81).fill(0).map((_, i) => at((i / 80) * upTo)).map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`).join(' ');

const Curve: React.FC = () => {
  const frame = useCurrentFrame();
  const u = enter(frame, 2, 34);
  const [x, y] = at(u);
  const tail = enter(frame, b(2), 12);
  const out = leave(frame, BAR - 7, 7);
  return (
    <AbsoluteFill style={{ opacity: 1 - out, transform: `translateY(${-out * 120}px)` }}>
      <svg width={W} height={1920} viewBox={`0 0 ${W} 1920`} style={{ position: 'absolute', inset: 0 }}>
        <path d={trail(1)} fill="none" stroke={color.cream} strokeOpacity="0.14" strokeWidth="8" strokeLinecap="round" strokeDasharray="4 26" />
        <path d={trail(Math.max(u, 0.001))} fill="none" stroke={color.lime} strokeWidth="14" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <div style={{ position: 'absolute', left: x + 26, top: y - 78, ...big, fontSize: 150, whiteSpace: 'nowrap', color: color.lime }}>Кривые</div>
      <div style={{ position: 'absolute', left: safe.left, top: 700, overflow: 'hidden', height: 170 }}>
        <div style={{ ...big, color: color.cream, transform: `translateY(${(1 - tail) * 120}%)` }}>выбрал сам</div>
      </div>
    </AbsoluteFill>
  );
};

// Такты 4–5: «мимо такта» ни разу. Слово «такта» пульсирует на каждом ударе, счёт долей
// идёт крупно, на последней доле строка сжимается в точку.
const Pulse: React.FC = () => {
  const frame = useCurrentFrame();
  const beatAt = Math.floor(frame / BEAT) * BEAT;
  const pop = hit(frame, beatAt, 9);
  const count = (Math.floor(frame / BEAT) % 4) + 1;
  const out = leave(frame, 2 * BAR - 8, 8);
  const inn = enter(frame, 0, 10);
  return (
    <AbsoluteFill style={{ opacity: inn * (1 - out), transform: `translateY(${-out * 120}px)` }}>
      <div style={{ position: 'absolute', left: safe.left, top: 470 }}>
        <div style={{ ...big, fontSize: 140, transform: `translateY(${(1 - inn) * 60}px)` }}>Ни разу</div>
        <div style={{ ...big, fontSize: 140 }}>мимо</div>
        <div style={{ ...big, fontSize: 210, color: color.lime, transform: `scale(${1 + pop * 0.1})`, transformOrigin: '0% 60%' }}>такта</div>
      </div>
      <div style={{ position: 'absolute', right: 120, top: 1040, fontFamily: mono, fontWeight: 500, fontSize: 200, color: 'rgba(241,242,234,0.16)', transform: `scale(${1 + pop * 0.08})`, transformOrigin: '100% 50%' }}>
        {count}
      </div>
    </AbsoluteFill>
  );
};

const SOUNDS: [number, string, number][] = [
  ...promptSounds(T.prompt),
  [T.show, 'whoosh.wav', 0.35],
  [T.press, 'click.wav', 0.5],
];

export type TypeProps = { music: boolean };

export const Type: React.FC<TypeProps> = ({ music }) => {
  const frame = useCurrentFrame();
  const bump = frame >= T.show && frame < T.save ? hit(frame, Math.floor(frame / BEAT) * BEAT, 9) * 0.008 : 0;
  return (
    <AbsoluteFill style={{ background: GROUND }}>
      <AbsoluteFill style={{ transform: `scale(${1 + bump})` }}>
        <Sequence from={T.hook} durationInFrames={BAR + 2}><Hook /></Sequence>
        <Sequence from={T.prompt} durationInFrames={T.show - T.prompt}><Prompt text={PROMPT} skills={SKILLS} hold={T.show - T.prompt} /></Sequence>
        <Show>
          <Scale />
          <Sequence from={0} durationInFrames={BAR}><Letters /></Sequence>
          <Sequence from={BAR} durationInFrames={BAR}><OnBeats /></Sequence>
          <Sequence from={2 * BAR} durationInFrames={BAR}><Curve /></Sequence>
          <Sequence from={3 * BAR} durationInFrames={2 * BAR}><Pulse /></Sequence>
        </Show>
        <Sequence from={T.save} durationInFrames={BAR}><Save text={PROMPT} skills={SKILLS} /></Sequence>
        <Sequence from={T.cta}><Cta question="Что дать ему смонтировать следующим?" cat="series/wave-dark.jpg" catTop={840} catWidth={1000} /></Sequence>
        <Captions words={words as Word[]} hide={[[0, BAR], [T.show, LENGTH]]} />
      </AbsoluteFill>
      {music && <Audio src={staticFile('series/r4.m4a')} volume={0.92} />}
      {SOUNDS.map(([from, name, volume], i) => (
        <Sequence key={i} from={from} layout="none"><Audio src={staticFile(`sfx/${name}`)} volume={volume} /></Sequence>
      ))}
    </AbsoluteFill>
  );
};
