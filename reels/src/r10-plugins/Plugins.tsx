// Ролик «5 бесплатных плагинов»: рерайт рилса @chingizkhan_yt, разбор в РЕФЕРЕНС.md.
// Один ролик, три исполнения:
//   Plugins        Remotion: сцены ставит по кадру src/lib/gsap.ts, заголовок рисует React
//   PluginsHybrid  гибрид: сцены сняты в HyperFrames (public/plugins/hf-scenes.mp4),
//                  заголовок, знак и звук кладёт Remotion
//   hf/r10-plugins HyperFrames целиком: tools/hf-build.mjs собирает его из той же папки shared
// Вид и движение сцен общие (shared/scenes.css, shared/scenes.js), время берётся с голоса:
// timeline.json пишет tools/layout.py. Тезис ролика записан в шапке shared/scenes.js.
import React, { useLayoutEffect, useState } from 'react';
import gsap from 'gsap';
import { AbsoluteFill, Audio, OffthreadVideo, continueRender, delayRender, interpolate, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { curve, fontsReady } from '../lib/brand';
import { useTimeline } from '../lib/gsap';
import './shared/scenes.css';
// @ts-ignore общий модуль написан на чистом JS: его же без сборки читает HyperFrames
import { buildScenes, headlines, markup } from './shared/scenes.js';
import timeline from './timeline.json';

type Line = [string, number, string?][];
type Head = { id: string; light: boolean; from: number; to: number; l1: Line; l2: Line };
const HEADS: Head[] = headlines(timeline);
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

// Заголовок: слово проявляется из размытия в тот миг, когда звучит. Уходит весь разом.
const Headline: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const h = HEADS.find((x) => t >= x.from && t < x.to);
  if (!h) return null;
  const gone = interpolate(t, [h.to - 0.26, h.to], [0, 1], { ...clamp, easing: curve.in });
  const line = (words: Line, cls: string) => words.length > 0 && (
    <div className={cls}>
      {words.map(([txt, at, mark], i) => {
        const p = interpolate(t, [Math.max(h.from, at - 0.06), Math.max(h.from, at - 0.06) + 0.36], [0, 1], { ...clamp, easing: curve.out });
        return (
          <span key={i} className={mark} style={{ opacity: p * (1 - gone), transform: `translateY(${(1 - p) * 20}px)`, filter: `blur(${Math.max(1 - p, gone) * 12}px)` }}>
            {txt}
          </span>
        );
      })}
    </div>
  );
  return <div className={`hl ${h.light ? 'light' : ''}`}>{line(h.l1, 'l1')}{line(h.l2, 'l2')}</div>;
};

const Logo: React.FC = () => <div className="logo"><img src={staticFile('plugins/logo.png')} /></div>;

// Сцены: разметка из общего модуля, таймлайн GSAP на паузе, головка стоит по кадру.
const Scenes: React.FC = () => {
  const [html] = useState(() => markup(staticFile('plugins')));
  const [wait] = useState(() => delayRender('картинки и шрифты сцен'));
  const root = useTimeline((tl, el) => buildScenes(gsap, tl, el, timeline));
  useLayoutEffect(() => {
    const imgs = [...(root.current?.querySelectorAll('img') ?? [])];
    Promise.all([fontsReady(), ...imgs.map((i) => i.decode().catch(() => undefined))]).then(() => continueRender(wait));
  }, [root, wait]);
  return <div ref={root} style={{ position: 'absolute', inset: 0 }} dangerouslySetInnerHTML={{ __html: html }} />;
};

export const Plugins: React.FC<{ engine: 'remotion' | 'hybrid'; sound: boolean }> = ({ engine, sound }) => (
  <AbsoluteFill style={{ background: '#0A0B08' }}>
    <div className="r10">
      {engine === 'remotion' ? <Scenes /> : <OffthreadVideo src={staticFile('plugins/hf-scenes.mp4')} muted style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }} />}
      <Logo />
      <Headline />
    </div>
    {sound && <Audio src={staticFile('plugins/sound.m4a')} />}
  </AbsoluteFill>
);
