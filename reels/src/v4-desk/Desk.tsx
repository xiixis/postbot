// Версия «Монтажный стол». 15 секунд, 1080×1920, музыка 100 ударов в минуту.
//
// Тезис: монтаж без монтажной программы. Кадр с котом сжимается в окно просмотра, вокруг него
// линиями рисуется монтажный стол, на удары на дорожки падают клипы. Дорожки показывают сам
// этот ролик: настоящие границы сцен, надписей и музыки, а головка идёт по ним до конца.
// Разрешённые приёмы: линия рисует себя, клип падает на удар, лаймовая головка.
import React from 'react';
import gsap from 'gsap';
import { DrawSVGPlugin } from 'gsap/DrawSVGPlugin';
import { SplitText } from 'gsap/SplitText';
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { hit } from '../lib/beat';
import { color, column, curve, enter, glide, H, leave, mix, mono, safe, sans, W } from '../lib/brand';
import { sec, useTimeline } from '../lib/gsap';
import { Mask } from '../lib/Mask';
import { at, b, BEAT, CARD, DONE, LANES, laneTop, LINE, MOVES, MOVES_DROP, SCENES, SIDE, T, TICKS, TITLES, TOTAL, VIEW, WAVE_FROM, WAVE_TO } from './tracks';
import { WAVE } from './wave';

gsap.registerPlugin(SplitText, DrawSVGPlugin);

const GROUND = '#15170B';
const LEAD = 0.4;
const line = 'rgba(241,242,234,0.3)';
const cover = staticFile('v4-desk/cover.jpg');

// Кадр с котом: на весь экран, потом в окне просмотра, на призыве карточкой справа.
const Picture: React.FC = () => {
  const frame = useCurrentFrame();
  const small = glide(frame, T.desk, 24);
  const card = glide(frame, T.cta, 20);
  const box = {
    x: mix(card, mix(small, 0, VIEW.x), CARD.x), y: mix(card, mix(small, 0, VIEW.y), CARD.y),
    w: mix(card, mix(small, W, VIEW.w), CARD.w), h: mix(card, mix(small, H, VIEW.h), CARD.h),
  };
  const push = mix(enter(frame, -10, 110, curve.calm), 1.16, 1.03) + frame * 0.00012;
  return (
    <div style={{
      position: 'absolute', left: box.x, top: box.y, width: box.w, height: box.h, overflow: 'hidden',
      borderRadius: small * 30, boxShadow: `0 0 0 ${small * 4}px ${color.cream}, 0 ${small * 30}px ${small * 80}px rgba(0,0,0,0.45)`,
      transform: `rotate(${card * 3}deg)`,
    }}>
      <Img src={cover} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${push})`, transformOrigin: '50% 58%' }} />
      <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(21,23,11,0.78) 0%, rgba(21,23,11,0) 34%)', opacity: 1 - small }} />
    </div>
  );
};

const Hook: React.FC = () => {
  const root = useTimeline((tl, scope) => {
    scope.querySelectorAll('.h').forEach((el, i) => {
      const s = new SplitText(el, { type: 'chars' });
      tl.from(s.chars, { yPercent: 118, duration: 0.5, ease: 'expo.out', stagger: 0.02 }, i * 0.12);
    });
    tl.fromTo('.cut', { drawSVG: '0%' }, { drawSVG: '100%', duration: 0.3, ease: 'power3.out' }, LEAD + sec(b(2)))
      .to('.head', { yPercent: -30, opacity: 0, duration: 0.24, ease: 'power2.in' }, LEAD + sec(T.desk) - 0.3);
  }, LEAD);
  return (
    <AbsoluteFill ref={root}>
      <div className="head" style={{ position: 'absolute', left: safe.left, top: safe.top }}>
        <Mask px={132} color={color.cream} className="h">Монтаж без</Mask>
        <div style={{ position: 'relative', display: 'inline-block' }}>
          <Mask px={132} color={color.cream} className="h">монтажки</Mask>
          <svg width="700" height="40" viewBox="0 0 700 40" style={{ position: 'absolute', left: -16, top: 92 }}>
            <path className="cut" d="M6 24 C 170 8, 420 34, 694 16" fill="none" stroke={color.lime} strokeWidth="13" strokeLinecap="round" />
          </svg>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Подпись над столом: строки выезжают снизу по буквам, уходят вверх целиком.
const Caption: React.FC<{ lines: React.ReactNode[]; life: number; px?: number }> = ({ lines, life, px = 80 }) => {
  const frame = useCurrentFrame();
  const root = useTimeline((tl, scope) => {
    scope.querySelectorAll('.h').forEach((el, i) => {
      const s = new SplitText(el, { type: 'words' });
      tl.from(s.words, { yPercent: 118, duration: 0.45, ease: 'expo.out', stagger: 0.05 }, i * 0.1);
    });
  });
  const out = leave(frame, life - 8, 8);
  return (
    <AbsoluteFill ref={root} style={{ opacity: 1 - out, transform: `translateY(${-out * 70}px)` }}>
      <div style={{ position: 'absolute', left: safe.left, top: safe.top }}>
        {lines.map((l, i) => <Mask key={i} px={px} weight={700} color={color.cream} className="h" style={{ letterSpacing: '-0.035em' }}>{l}</Mask>)}
      </div>
    </AbsoluteFill>
  );
};

// Линии стола рисуют себя: линейка, деления, дорожки.
const Lines: React.FC = () => {
  const frame = useCurrentFrame();
  const root = useTimeline((tl) => {
    tl.fromTo('.rule', { drawSVG: '0%' }, { drawSVG: '100%', duration: 0.5, ease: 'power2.out' }, 0.25)
      .fromTo('.tick', { drawSVG: '0%' }, { drawSVG: '100%', duration: 0.2, ease: 'power2.out', stagger: 0.025 }, 0.35)
      .fromTo('.lane', { drawSVG: '0%' }, { drawSVG: '100%', duration: 0.6, ease: 'power2.inOut', stagger: 0.09 }, 0.45)
      .fromTo('.side', { drawSVG: '0%' }, { drawSVG: '100%', duration: 0.4, ease: 'power2.out', stagger: 0.07 }, 0.5);
  });
  const gone = glide(frame, T.cta - T.desk, 14);
  return (
    <AbsoluteFill ref={root}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} fill="none" stroke={line} strokeWidth={3} strokeLinecap="round">
        <path className="rule" d={`M${LINE.x} ${LINE.y + LINE.ruler} H${LINE.x + LINE.w}`} />
        {new Array(16).fill(0).map((_, i) => {
          const x = at(i * 30), tall = i % 5 === 0 ? 22 : 11;
          return <path key={i} className="tick" d={`M${x} ${LINE.y + LINE.ruler} v${-tall}`} />;
        })}
        {LANES.map((_, i) => (
          <rect key={i} className="lane" x={LINE.x} y={laneTop(i)} width={LINE.w} height={LINE.lane} rx={14} />
        ))}
        <g opacity={1 - gone}>
          {[0, 1, 2, 3].map((i) => <path key={i} className="side" d={`M${SIDE.x} ${SIDE.y + SIDE.head + i * SIDE.row} H${SIDE.x + SIDE.w}`} />)}
        </g>
      </svg>
      {[0, 5, 10, 15].map((s) => (
        <div key={s} style={{
          position: 'absolute', left: at(s * 30) + (s === 15 ? -40 : 8), top: LINE.y - 8, fontFamily: mono, fontWeight: 500, fontSize: 24,
          color: color.cream, opacity: 0.5 * enter(frame, 14 + s, 12),
        }}>
          {s}
        </div>
      ))}
    </AbsoluteFill>
  );
};

const drop = (frame: number, from: number): React.CSSProperties => {
  const t = enter(frame, from, 9);
  return { opacity: Math.min(1, t * 3), transform: `translateY(${(1 - t) * -46}px) scaleY(${1 - hit(frame, from + 7, 7) * 0.08})`, transformOrigin: '50% 100%' };
};

const Clips: React.FC = () => {
  const frame = useCurrentFrame();
  const bar = LINE.w / WAVE.length;
  const heard = glide(frame, WAVE_FROM, WAVE_TO - WAVE_FROM);
  return (
    <AbsoluteFill>
      {SCENES.map((c, i) => (
        <div key={`s${i}`} style={{
          position: 'absolute', left: at(c.from) + 3, top: laneTop(0) + 4, width: at(c.to) - at(c.from) - 6, height: LINE.lane - 8, borderRadius: 10,
          backgroundImage: `url(${cover})`, backgroundSize: `auto ${LINE.lane + 50}px`, backgroundPosition: `${-12 - i * 11}px 38%`,
          boxShadow: `inset 0 0 0 3px ${color.cream}`, ...drop(frame, c.drop),
        }} />
      ))}
      {TITLES.map((c, i) => (
        <div key={`t${i}`} style={{
          position: 'absolute', left: at(c.from) + 3, top: laneTop(1) + 4, width: at(c.to) - at(c.from) - 6, height: LINE.lane - 8, borderRadius: 10,
          background: color.lime, overflow: 'hidden', display: 'flex', alignItems: 'center', padding: '0 12px',
          fontFamily: sans, fontWeight: 700, fontSize: 30, color: color.graphite, whiteSpace: 'nowrap', ...drop(frame, c.drop),
        }}>
          {c.label}
        </div>
      ))}
      {MOVES.map((m, i) => {
        const t = enter(frame, MOVES_DROP + i * 1.4, 8);
        return (
          <div key={`m${i}`} style={{
            position: 'absolute', left: at(m) + 6 - 12, top: laneTop(2) + LINE.lane / 2 - 12, width: 24, height: 24, borderRadius: 5,
            background: frame >= m && frame < m + 8 ? color.lime : color.cream, transform: `rotate(45deg) scale(${t})`,
          }} />
        );
      })}
      <div style={{ position: 'absolute', left: LINE.x, top: laneTop(3), width: LINE.w * heard, height: LINE.lane, overflow: 'hidden' }}>
        {WAVE.map((v, i) => (
          <div key={i} style={{
            position: 'absolute', left: i * bar + bar * 0.2, top: (LINE.lane * (1 - v * 0.8)) / 2, width: bar * 0.6, height: LINE.lane * v * 0.8,
            borderRadius: bar, background: at(frame) - LINE.x > i * bar ? color.lime : 'rgba(199,226,75,0.42)',
          }} />
        ))}
      </div>
    </AbsoluteFill>
  );
};

const Playhead: React.FC = () => {
  const frame = useCurrentFrame();
  const t = enter(frame, T.desk + 24, 12);
  const x = at(frame);
  return (
    <div style={{ position: 'absolute', left: x - 3, top: LINE.y - 6, width: 6, height: (laneTop(3) + LINE.lane + 10 - LINE.y) * t, borderRadius: 3, background: color.lime, opacity: t }}>
      <div style={{ position: 'absolute', left: -13, top: -8, width: 32, height: 30, background: color.lime, clipPath: 'polygon(0 0, 100% 0, 100% 55%, 50% 100%, 0 55%)' }} />
    </div>
  );
};

const two = (n: number) => String(n).padStart(2, '0');

const Side: React.FC = () => {
  const frame = useCurrentFrame();
  const inn = enter(frame, T.desk + 22, 14);
  const out = leave(frame, T.cta - 4, 10);
  return (
    <div style={{ position: 'absolute', left: SIDE.x, top: SIDE.y, width: SIDE.w, height: SIDE.h, opacity: inn * (1 - out), transform: `translateY(${(1 - inn) * 40 - out * 50}px)` }}>
      <div style={{ fontFamily: mono, fontWeight: 500, fontSize: 98, lineHeight: 1, color: color.cream, letterSpacing: '-0.05em' }}>
        00:{two(Math.floor(frame / 30))}:{two(frame % 30)}
      </div>
      <div style={{ marginTop: 22, fontFamily: mono, fontWeight: 500, fontSize: 34, color: color.cream, opacity: 0.55 }}>
        кадр {frame + 1} из {TOTAL}
      </div>
      {LANES.map((name, i) => {
        const done = frame >= DONE[i];
        return (
          <div key={name} style={{ position: 'absolute', left: 0, top: SIDE.head + i * SIDE.row, width: SIDE.w, height: SIDE.row, display: 'flex', alignItems: 'center', gap: 22 }}>
            <div style={{
              width: 30, height: 30, borderRadius: i === 2 ? 5 : 9, transform: i === 2 ? 'rotate(45deg) scale(0.8)' : undefined,
              background: i === 0 ? color.cream : i === 1 || i === 3 ? color.lime : color.cream, opacity: i === 3 ? 0.7 : 1,
            }} />
            <div style={{ flex: 1, fontFamily: sans, fontWeight: 700, fontSize: 52, letterSpacing: '-0.03em', color: color.cream, opacity: done ? 1 : 0.42 }}>{name}</div>
            <svg width="50" height="50" viewBox="0 0 24 24" fill="none" stroke={color.lime} strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round"
              style={{ transform: `scale(${enter(frame, DONE[i], 8)})` }}>
              <path d="M4.5 12.5l5 5 10-10.5" />
            </svg>
          </div>
        );
      })}
    </div>
  );
};

const Cta: React.FC = () => {
  const frame = useCurrentFrame();
  const slot = (from: number) => {
    const t = enter(frame, from, 12);
    return { opacity: t, transform: `translateY(${(1 - t) * 60}px)` } as React.CSSProperties;
  };
  const PRESS = T.press - T.cta;
  const done = frame >= PRESS;
  const press = frame >= PRESS - 2 && frame < PRESS ? 0.94 : 1 + hit(frame, PRESS, 10) * 0.05;
  return (
    <AbsoluteFill>
      <div style={{ position: 'absolute', left: safe.left, top: safe.top, display: 'flex', alignItems: 'center', gap: 20, ...slot(4) }}>
        <Img src={staticFile('brand/logo.png')} style={{ width: 72, height: 72 }} />
        <div style={{ fontFamily: sans, fontWeight: 800, fontSize: 54, color: color.cream, letterSpacing: '-0.02em' }}>4xTube</div>
      </div>
      <div style={{ position: 'absolute', left: safe.left, top: 346, ...slot(10) }}>
        <div style={{
          width: column, height: 170, borderRadius: 999, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 20,
          background: done ? 'transparent' : color.lime, boxShadow: `inset 0 0 0 6px ${color.lime}`,
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
      <div style={{ position: 'absolute', left: safe.left, top: 590, width: 510, fontFamily: sans, fontWeight: 700, fontSize: 60, lineHeight: 1.12, letterSpacing: '-0.025em', color: color.cream, ...slot(20) }}>
        Как повторить, показываю в Telegram
      </div>
      <div style={{ position: 'absolute', left: safe.left, top: 850, ...slot(26) }}>
        <div style={{ padding: '18px 36px', borderRadius: 22, background: color.cream, fontFamily: sans, fontWeight: 700, fontSize: 46, color: color.graphite }}>
          ссылка в профиле
        </div>
      </div>
    </AbsoluteFill>
  );
};

const SOUNDS: [number, string, number][] = [
  ...TICKS.map((f, i): [number, string, number] => [f, 'click.wav', 0.2 + (i % 2) * 0.05]),
  [T.press, 'click.wav', 0.5],
];

export type DeskProps = { music: boolean };

export const Desk: React.FC<DeskProps> = ({ music }) => {
  const frame = useCurrentFrame();
  const bump = frame >= T.build && frame < T.cta ? hit(frame, Math.floor(frame / BEAT) * BEAT, 9) * 0.006 : 0;
  return (
    <AbsoluteFill style={{ background: GROUND }}>
      <AbsoluteFill style={{ transform: `scale(${1 + bump})` }}>
        <Sequence from={T.desk}><Lines /></Sequence>
        <Clips />
        <Playhead />
        <Side />
        <Picture />
        <Sequence from={T.hook} durationInFrames={T.desk + 2}><Hook /></Sequence>
        <Sequence from={T.desk + 20} durationInFrames={T.build - T.desk - 20}>
          <Caption life={T.build - T.desk - 20} px={72} lines={['Программу для монтажа', 'я не открывал']} />
        </Sequence>
        <Sequence from={T.build} durationInFrames={T.map - T.build}>
          <Caption life={T.map - T.build} lines={['Дорожки', <>собирает <span style={{ color: color.claude }}>Claude</span></>]} />
        </Sequence>
        <Sequence from={T.map} durationInFrames={T.cta - T.map}>
          <Caption life={T.cta - T.map} px={76} lines={['Это таймлайн ролика,', 'который ты смотришь']} />
        </Sequence>
        <Sequence from={T.cta}><Cta /></Sequence>
      </AbsoluteFill>
      {music && <Audio src={staticFile('v4-desk/music.m4a')} volume={0.92} />}
      {SOUNDS.map(([from, name, volume], i) => (
        <Sequence key={i} from={from} layout="none"><Audio src={staticFile(`sfx/${name}`)} volume={volume} /></Sequence>
      ))}
    </AbsoluteFill>
  );
};
