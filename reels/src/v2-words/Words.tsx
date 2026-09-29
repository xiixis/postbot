// Версия «Слова под бит». 15 секунд, 1080×1920, музыка 100 ударов в минуту.
//
// Тезис: ролик собран из слов. На каждый такт в кадр встаёт одно слово о том, что сделал Claude:
// буквы приходят снизу по одной, на втором ударе под слово ложится лаймовая плашка, под ним
// картинка показывает это дело. Характер энергичный, фон светлый, всё движется снизу вверх.
// Состояний шесть, каждое держится такт или дольше: быстрее владелец назвал хаосом.
// Разрешённые приёмы: лаймовая плашка под словом, толчок кадра на удар, кот, знак канала.
import React from 'react';
import gsap from 'gsap';
import { DrawSVGPlugin } from 'gsap/DrawSVGPlugin';
import { SplitText } from 'gsap/SplitText';
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { hit } from '../lib/beat';
import { color, column, curve, enter, leave, mix, safe, sans, W } from '../lib/brand';
import { beats, useTimeline } from '../lib/gsap';
import { Mask } from '../lib/Mask';
import { Grid, Lines, Path, Wave } from './Demo';

gsap.registerPlugin(SplitText, DrawSVGPlugin);

const BPM = 100;
const BEAT = 18;
const b = (n: number) => n * BEAT;
const PAPER = '#ECEADE';                 // снимки с котом выровнены под этот цвет: края не видно

// Состояния стоят на первых долях тактов: обложка, четыре слова, призыв.
const T = { cover: 0, items: b(4), cta: b(20), end: 450 } as const;
const STEP = b(4);

// Обложка идёт с опережением: на нулевом кадре заголовок уже читается и ещё доезжает.
const LEAD = 0.4;

const Cover: React.FC = () => {
  const frame = useCurrentFrame();
  const root = useTimeline((tl, scope) => {
    scope.querySelectorAll('.h').forEach((el, i) => {
      const s = new SplitText(el, { type: 'chars' });
      tl.from(s.chars, { yPercent: 118, duration: 0.5, ease: 'expo.out', stagger: 0.02 }, i * 0.12);
    });
    tl.fromTo('.squiggle', { drawSVG: '0%' }, { drawSVG: '100%', duration: 0.45, ease: 'power2.out' }, LEAD + beats(2, BPM))
      .to('.head', { yPercent: -35, opacity: 0, duration: 0.22, ease: 'power2.in' }, LEAD + beats(4, BPM) - 0.26);
  }, LEAD);
  const rise = enter(frame, -8, 24);
  const out = leave(frame, T.items - 9, 9);
  return (
    <AbsoluteFill ref={root}>
      <Img src={staticFile('v2-words/cover.jpg')} style={{
        position: 'absolute', left: -60, top: 560, width: W + 120,
        transform: `translateY(${(1 - rise) * 200 + out * 1400}px) scale(${mix(enter(frame, 0, 72, curve.calm), 1.07, 1)})`, transformOrigin: '50% 40%',
      }} />
      <div className="head" style={{ position: 'absolute', left: safe.left, top: safe.top }}>
        <Mask px={132} color={color.graphite} className="h">Мой монтажёр</Mask>
        <Mask px={132} color={color.graphite} className="h">это <span style={{ color: color.claude }}>Claude</span></Mask>
        <svg width="560" height="40" viewBox="0 0 560 40" style={{ marginTop: 34, marginLeft: 232 }}>
          <path className="squiggle" d="M6 26 C 90 6, 170 36, 270 18 S 470 8, 554 24" fill="none" stroke={color.lime} strokeWidth="14" strokeLinecap="round" />
        </svg>
      </div>
    </AbsoluteFill>
  );
};

type ItemData = { verb: string; noun: string; px: number; Demo: React.FC };
const ITEMS: ItemData[] = [
  { verb: 'написал', noun: 'текст', px: 250, Demo: Lines },
  { verb: 'собрал', noun: 'кадры', px: 250, Demo: Grid },
  { verb: 'поставил', noun: 'движение', px: 164, Demo: Path },
  { verb: 'свёл', noun: 'звук', px: 290, Demo: Wave },
];

const Item: React.FC<ItemData> = ({ verb, noun, px, Demo }) => {
  const frame = useCurrentFrame();
  const root = useTimeline((tl, scope) => {
    const s = new SplitText(scope.querySelector('.noun'), { type: 'chars' });
    tl.from('.verb', { yPercent: 120, duration: 0.3, ease: 'expo.out' }, 0)
      .from(s.chars, { yPercent: 118, duration: 0.4, ease: 'expo.out', stagger: 0.022 }, 0.06)
      .fromTo('.mark', { scaleX: 0 }, { scaleX: 1, duration: 0.32, ease: 'expo.out' }, beats(1, BPM))
      .from('.demo', { y: 70, opacity: 0, duration: 0.35, ease: 'expo.out' }, 0.12);
  });
  const out = leave(frame, STEP - 6, 6);
  return (
    <AbsoluteFill ref={root} style={{ opacity: 1 - out, transform: `translateY(${-out * 140}px)` }}>
      <div style={{ position: 'absolute', left: safe.left, top: safe.top }}>
        <div style={{ overflow: 'hidden', height: 96 }}>
          <div className="verb" style={{ fontFamily: sans, fontWeight: 700, fontSize: 76, lineHeight: '96px', letterSpacing: '-0.03em', color: color.olive }}>{verb}</div>
        </div>
        <div style={{ position: 'relative', marginTop: 6 }}>
          <div className="mark" style={{
            position: 'absolute', left: -18, right: -18, top: px * 0.5, height: px * 0.52, borderRadius: px * 0.12,
            background: color.lime, transformOrigin: 'left center',
          }} />
          <div style={{ position: 'relative' }}>
            <Mask px={px} color={color.graphite} className="noun">{noun}</Mask>
          </div>
        </div>
      </div>
      <div className="demo" style={{ position: 'absolute', left: safe.left, top: 800 }}>
        <Demo />
      </div>
    </AbsoluteFill>
  );
};

const PRESS = b(2);

const Cta: React.FC = () => {
  const frame = useCurrentFrame();
  const slot = (from: number) => {
    const t = enter(frame, from, 12);
    return { opacity: t, transform: `translateY(${(1 - t) * 60}px)` } as React.CSSProperties;
  };
  const done = frame >= PRESS;
  const press = frame >= PRESS - 2 && frame < PRESS ? 0.94 : 1 + hit(frame, PRESS, 10) * 0.06;
  const cat = enter(frame, 0, 22);
  return (
    <AbsoluteFill>
      <Img src={staticFile('v2-words/end.jpg')} style={{
        position: 'absolute', left: 40, top: 0, width: 1040,
        transform: `translateY(${mix(cat, 1920, 760)}px) rotate(${Math.sin(frame / 7) * 0.9}deg)`, transformOrigin: '50% 85%',
      }} />
      <div style={{ position: 'absolute', left: safe.left, top: safe.top, width: column, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 34 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 20, ...slot(2) }}>
          <Img src={staticFile('brand/logo.png')} style={{ width: 72, height: 72, filter: 'brightness(0.55) saturate(1.2)' }} />
          <div style={{ fontFamily: sans, fontWeight: 800, fontSize: 54, color: color.graphite, letterSpacing: '-0.02em' }}>4xTube</div>
        </div>
        <div style={{ ...slot(6) }}>
          <div style={{
            width: 700, height: 172, borderRadius: 999, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 20,
            background: done ? color.graphite : color.lime, boxShadow: `inset 0 0 0 6px ${color.graphite}`,
            fontFamily: sans, fontWeight: 800, fontSize: 78, letterSpacing: '-0.025em', color: done ? color.lime : color.graphite,
            transform: `scale(${press})`, transformOrigin: 'left center',
          }}>
            {done ? 'Вы подписаны' : 'Подписаться'}
            {done && (
              <svg width="62" height="62" viewBox="0 0 24 24" fill="none" stroke={color.lime} strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4.5 12.5l5 5 10-10.5" />
              </svg>
            )}
          </div>
        </div>
        <div style={{ width: 800, fontFamily: sans, fontWeight: 700, fontSize: 62, lineHeight: 1.14, letterSpacing: '-0.025em', color: color.graphite, ...slot(12) }}>
          Как повторить, показываю в Telegram
        </div>
        <div style={{ padding: '18px 36px', borderRadius: 22, background: color.graphite, fontFamily: sans, fontWeight: 700, fontSize: 46, color: color.cream, ...slot(18) }}>
          ссылка в профиле
        </div>
      </div>
    </AbsoluteFill>
  );
};

export type WordsProps = { music: boolean };

export const Words: React.FC<WordsProps> = ({ music }) => {
  const frame = useCurrentFrame();
  // Толчок всего кадра на каждый удар: едва заметный, он и связывает картинку с музыкой.
  const bump = hit(frame, Math.floor(frame / BEAT) * BEAT, 9) * 0.008;
  return (
    <AbsoluteFill style={{ background: PAPER }}>
      <AbsoluteFill style={{ transform: `scale(${1 + bump})` }}>
        <Sequence from={T.cover} durationInFrames={T.items - T.cover + 2}><Cover /></Sequence>
        {ITEMS.map((it, i) => (
          <Sequence key={it.noun} from={T.items + i * STEP} durationInFrames={STEP}><Item {...it} /></Sequence>
        ))}
        <Sequence from={T.cta}><Cta /></Sequence>
      </AbsoluteFill>
      {music && <Audio src={staticFile('v2-words/music.m4a')} volume={0.92} />}
      <Sequence from={T.cta + PRESS} layout="none"><Audio src={staticFile('sfx/click.wav')} volume={0.5} /></Sequence>
    </AbsoluteFill>
  );
};
