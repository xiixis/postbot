// Серия 2, ролик 6: «Три голоса, ноль актёров: субтитры по словам сам».
//
// Тезис: показ озвучки. Слова рассказчика встают крупно по центру и вспыхивают лаймом ровно
// в миг звучания, под ними живая волна голоса. Потом ту же фразу читают ещё два голоса, и
// подсветка не сбивается: время каждого слова снято распознаванием с его записи.
// Характер деловой, один фон, входы снизу.
import React from 'react';
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { hit } from '../lib/beat';
import { color, column, enter, leave, mix, mono, safe, sans } from '../lib/brand';
import { Captions, type Word } from '../series/Captions';
import { BAR, BEAT, LENGTH, T } from '../series/grid';
import { Cta, Headline, Prompt, promptSounds, Save, Show } from '../series/parts';
import words from '../series/words/r6.json';
import wave from '../series/words/r6-wave.json';

const GROUND = '#12130F';
export const PROMPT = 'Озвучь ролик и подпиши каждое слово в тот миг, когда оно звучит';
export const SKILLS = ['Fish Audio', 'распознавание речи', 'motion-design'];

// Какие фразы сценария идут крупно на показе и чьим голосом они прочитаны.
const SHOW = [
  { line: 4, voice: 'А', name: 'рассказчик', from: 0, len: 2 * BAR },
  { line: 5, voice: 'Б', name: 'девушка', from: 2 * BAR, len: BAR },
  { line: 6, voice: 'В', name: 'низкий', from: 3 * BAR, len: BAR },
  { line: 7, voice: 'А', name: 'рассказчик', from: 4 * BAR, len: BAR },
];

const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const out = leave(frame, BAR - 10, 10);
  return (
    <AbsoluteFill>
      <Img src={staticFile('series/mic.jpg')} style={{
        position: 'absolute', left: -60, top: 420, width: 1200,
        transform: `scale(${mix(enter(frame, -10, 90), 1.1, 1.03)}) translateY(${out * -120}px)`, transformOrigin: '50% 40%', opacity: 1 - out,
        maskImage: 'radial-gradient(ellipse 60% 62% at 50% 50%, #000 58%, transparent 100%)',
        WebkitMaskImage: 'radial-gradient(ellipse 60% 62% at 50% 50%, #000 58%, transparent 100%)',
      }} />
      <Headline lines={[<span style={{ color: color.lime }}>3 голоса</span>, 'и ни одного', 'актёра']} px={118} />
    </AbsoluteFill>
  );
};

// Волна голоса: столбики по кадрам из дорожки, живут только пока голос звучит.
const Wave: React.FC<{ frame: number; top: number; tint?: string; width?: number; bars?: number }> = ({ frame, top, tint = color.lime, width = column, bars = 46 }) => {
  const levels = wave as number[];
  const step = width / bars;
  return (
    <div style={{ position: 'absolute', left: safe.left, top, width, height: 120, display: 'flex', alignItems: 'center', gap: step * 0.35 }}>
      {new Array(bars).fill(0).map((_, i) => {
        // столбик показывает громкость на своём кадре вокруг текущего: бегущее окно
        const at = frame - Math.round((bars / 2 - i) * 1.5);
        const v = at >= 0 && at < levels.length ? levels[at] : 0;
        const h = 8 + v * 112;
        return <div key={i} style={{ width: step * 0.65, height: h, borderRadius: step, background: i === Math.floor(bars / 2) ? color.cream : tint, opacity: 0.35 + v * 0.65 }} />;
      })}
    </div>
  );
};

// Караоке: слова фразы крупно, каждое зажигается в свой миг.
const Karaoke: React.FC<{ line: number; px?: number }> = ({ line, px = 104 }) => {
  // показ живёт в своей последовательности, а время слов считано от начала ролика
  const frame = useCurrentFrame() + T.show;
  const t = frame / 30;
  const ws = (words as Word[]).filter((w) => w.line === line);
  if (!ws.length) return null;
  return (
    <div style={{ position: 'absolute', left: safe.left, top: 560, width: column, display: 'flex', flexWrap: 'wrap', columnGap: px * 0.28, rowGap: px * 0.1 }}>
      {ws.map((w, i) => {
        const said = t >= w.s;
        const now = t >= w.s && t < w.e + 0.1;
        const pop = said ? hit(frame, Math.round(w.s * 30), 8) : 0;
        return (
          <span key={i} style={{
            fontFamily: sans, fontWeight: 800, fontSize: px, lineHeight: 1.06, letterSpacing: '-0.03em',
            color: now ? color.lime : said ? color.cream : 'rgba(241,242,234,0.22)',
            transform: `scale(${1 + pop * 0.08}) translateY(${said ? 0 : 6}px)`, transformOrigin: '0% 100%', display: 'inline-block',
          }}>
            {w.w}
          </span>
        );
      })}
    </div>
  );
};

const Chip: React.FC<{ voice: string; name: string; frame: number }> = ({ voice, name, frame }) => {
  const t = enter(frame, 0, 10);
  return (
    <div style={{ position: 'absolute', left: safe.left, top: 440, display: 'flex', alignItems: 'center', gap: 18, opacity: t, transform: `translateY(${(1 - t) * 30}px)` }}>
      <div style={{ width: 64, height: 64, borderRadius: 32, background: color.lime, color: color.graphite, fontFamily: sans, fontWeight: 800, fontSize: 36, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{voice}</div>
      <div style={{ fontFamily: mono, fontWeight: 500, fontSize: 36, color: 'rgba(241,242,234,0.7)' }}>голос {voice} · {name}</div>
    </div>
  );
};

// Показ: четыре фразы по очереди, у каждой чип голоса, караоке и волна.
const Stage: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      {SHOW.map((s) => {
        const local = frame - s.from;
        if (local < 0 || local >= s.len) return null;
        const out = leave(local, s.len - 8, 8);
        return (
          <AbsoluteFill key={s.line} style={{ opacity: 1 - out, transform: `translateY(${-out * 90}px)` }}>
            <Chip voice={s.voice} name={s.name} frame={local} />
            <Karaoke line={s.line} />
            <Wave frame={frame + T.show} top={1040} />
          </AbsoluteFill>
        );
      })}
      <div style={{ position: 'absolute', left: safe.left, top: 1240, fontFamily: mono, fontWeight: 500, fontSize: 34, color: 'rgba(241,242,234,0.5)' }}>
        {`время слов снято с записи · ${Math.min(3, 1 + SHOW.filter((s) => s.line !== 7 && frame >= s.from).length - 1)} из 3 голосов`}
      </div>
    </AbsoluteFill>
  );
};

const SOUNDS: [number, string, number][] = [
  ...promptSounds(T.prompt),
  [T.show, 'whoosh.wav', 0.3],
  [T.press, 'click.wav', 0.5],
];

export type VoiceProps = { music: boolean };

export const Voice: React.FC<VoiceProps> = ({ music }) => {
  const frame = useCurrentFrame();
  const bump = frame >= T.show && frame < T.save ? hit(frame, Math.floor(frame / BEAT) * BEAT, 9) * 0.005 : 0;
  return (
    <AbsoluteFill style={{ background: GROUND }}>
      <AbsoluteFill style={{ transform: `scale(${1 + bump})` }}>
        <Sequence from={T.hook} durationInFrames={BAR + 2}><Hook /></Sequence>
        <Sequence from={T.prompt} durationInFrames={T.show - T.prompt}><Prompt text={PROMPT} skills={SKILLS} hold={T.show - T.prompt} /></Sequence>
        <Show><Stage /></Show>
        <Sequence from={T.save} durationInFrames={BAR}><Save text={PROMPT} skills={SKILLS} what="промпт и инструменты" /></Sequence>
        <Sequence from={T.cta}><Cta question="Каким голосом озвучить следующий?" cat="series/wave-dark.jpg" catTop={840} catWidth={1000} /></Sequence>
        <Captions words={words as Word[]} hide={[[0, BAR], [T.show, LENGTH]]} />
      </AbsoluteFill>
      {music && <Audio src={staticFile('series/r6.m4a')} volume={0.92} />}
      {SOUNDS.map(([from, name, volume], i) => (
        <Sequence key={i} from={from} layout="none"><Audio src={staticFile(`sfx/${name}`)} volume={volume} /></Sequence>
      ))}
    </AbsoluteFill>
  );
};

