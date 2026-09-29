// Версия «Клавиши». 15 секунд, 1080×1920, музыка 100 ударов в минуту.
//
// Тезис: монтаж теперь печатают. Один непрерывный план над клавиатурой: камера отъезжает от
// лаймовой клавиши Enter, на клавишах набирается задача, после Enter шесть клавиш поднимаются
// и складываются в слово CLAUDE, а клавиатура печатает сама. Характер спокойный и дорогой.
// Разрешённые приёмы: лаймовый свет из-под клавиш, волна от Enter, терракотовые клавиши слова.
import React, { useEffect, useState } from 'react';
import gsap from 'gsap';
import { SplitText } from 'gsap/SplitText';
import { ThreeCanvas } from '@remotion/three';
import { AbsoluteFill, Audio, continueRender, delayRender, Img, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { color, column, enter, fontsReady, H, leave, mono, safe, sans, W } from '../lib/brand';
import { sec, useTimeline } from '../lib/gsap';
import { Mask } from '../lib/Mask';
import { Board, Lights, Rig } from './Board';
import { ASK, camera, FOV, T, TYPED, WORD } from './motion';

gsap.registerPlugin(SplitText);

const GROUND = '#0D0E0B';
const LEAD = 0.4;

const useFonts = () => {
  const [ready, setReady] = useState(false);
  const [handle] = useState(() => delayRender('шрифты для надписей на клавишах'));
  useEffect(() => {
    fontsReady().then(() => {
      setReady(true);
      continueRender(handle);
    });
  }, [handle]);
  return ready;
};

const rise = (scope: HTMLElement, tl: gsap.core.Timeline, at = 0) => {
  scope.querySelectorAll('.h').forEach((el, i) => {
    const s = new SplitText(el, { type: 'chars' });
    tl.from(s.chars, { yPercent: 118, duration: 0.5, ease: 'expo.out', stagger: 0.02 }, at + i * 0.12);
  });
};

const Hook: React.FC = () => {
  const root = useTimeline((tl, scope) => {
    rise(scope, tl);
    tl.to('.head', { yPercent: -30, opacity: 0, duration: 0.24, ease: 'power2.in' }, LEAD + sec(T.type) - 0.3);
  }, LEAD);
  return (
    <AbsoluteFill ref={root}>
      <div className="head" style={{ position: 'absolute', left: safe.left, top: safe.top }}>
        <Mask px={122} color={color.cream} className="h">Монтаж теперь</Mask>
        <Mask px={122} color={color.cream} className="h">печатают</Mask>
      </div>
    </AbsoluteFill>
  );
};

const Typing: React.FC = () => {
  const frame = useCurrentFrame();
  const at = frame + T.type;
  const inn = enter(frame, 0, 12);
  const out = leave(frame, T.rest - T.type - 8, 8);
  const typed = TYPED.filter((k) => at >= k.at).length;
  const sent = at >= T.enter;
  return (
    <AbsoluteFill style={{ opacity: 1 - out, transform: `translateY(${-out * 90}px)` }}>
      <div style={{ position: 'absolute', left: safe.left, top: safe.top, width: column, opacity: inn, transform: `translateY(${(1 - inn) * 50}px)` }}>
        <div style={{ fontFamily: sans, fontWeight: 700, fontSize: 84, lineHeight: 1.08, letterSpacing: '-0.035em', color: color.cream }}>
          Я пишу, что<br />хочу увидеть
        </div>
        <div style={{ marginTop: 56, height: 150, display: 'flex', alignItems: 'center', borderBottom: `5px solid ${sent ? color.lime : 'rgba(241,242,234,0.28)'}` }}>
          <div style={{ fontFamily: mono, fontWeight: 500, fontSize: 86, color: sent ? color.lime : color.cream, whiteSpace: 'pre', letterSpacing: '-0.02em' }}>
            {ASK.slice(0, typed)}
            <span style={{ display: 'inline-block', width: 10, height: 92, marginLeft: 8, verticalAlign: '-14px', borderRadius: 3, background: color.lime, opacity: sent ? 0 : 1 }} />
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Rest: React.FC = () => {
  const frame = useCurrentFrame();
  const root = useTimeline((tl, scope) => rise(scope, tl));
  const out = leave(frame, T.cta - T.rest - 10, 10);
  return (
    <AbsoluteFill ref={root} style={{ opacity: 1 - out, transform: `translateY(${-out * 90}px)` }}>
      <div style={{ position: 'absolute', left: safe.left, top: safe.top }}>
        <Mask px={132} color={color.cream} className="h">Остальное</Mask>
        <Mask px={132} color={color.cream} className="h">делает</Mask>
      </div>
    </AbsoluteFill>
  );
};

const Cta: React.FC = () => {
  const frame = useCurrentFrame();
  const slot = (from: number) => {
    const t = enter(frame, from, 12);
    return { opacity: t, transform: `translateY(${(1 - t) * 60}px)` } as React.CSSProperties;
  };
  return (
    <AbsoluteFill>
      <div style={{ position: 'absolute', left: safe.left, top: safe.top, display: 'flex', alignItems: 'center', gap: 20, ...slot(4) }}>
        <Img src={staticFile('brand/logo.png')} style={{ width: 72, height: 72 }} />
        <div style={{ fontFamily: sans, fontWeight: 800, fontSize: 54, color: color.cream, letterSpacing: '-0.02em' }}>4xTube</div>
      </div>
      <div style={{ position: 'absolute', left: safe.left, top: 690, width: 820, fontFamily: sans, fontWeight: 700, fontSize: 66, lineHeight: 1.14, letterSpacing: '-0.025em', color: color.cream, ...slot(14) }}>
        Как повторить, показываю в Telegram
      </div>
      <div style={{ position: 'absolute', left: safe.left, top: 890, ...slot(20) }}>
        <div style={{ padding: '18px 36px', borderRadius: 22, background: color.cream, fontFamily: sans, fontWeight: 700, fontSize: 46, color: color.graphite }}>
          ссылка в профиле
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Сверху темнее, чтобы текст читался поверх дальнего края клавиатуры; по краям лёгкая виньетка.
const Finish: React.FC = () => (
  <AbsoluteFill style={{
    background: `linear-gradient(180deg, rgba(13,14,11,0.9) 0%, rgba(13,14,11,0.62) 24%, rgba(13,14,11,0) 46%),
      radial-gradient(120% 80% at 50% 62%, rgba(13,14,11,0) 55%, rgba(13,14,11,0.55) 100%)`,
  }} />
);

const ROWS: Record<number, string> = { 1: 'r1', 2: 'r2', 3: 'r3', 4: 'space' };
const SOUNDS: [number, string, number][] = [
  ...TYPED.flatMap((k, i): [number, string, number][] => {
    const loud = 0.7 + ((i * 37) % 9) / 50;
    const row = ROWS[k.key.row];
    return [
      [k.at, `keyboard/press-${row}.wav`, loud],
      row === 'space' ? [k.at + 3, 'keyboard/release-space.wav', loud * 0.2] : [k.at + 3, 'keyboard/release.wav', loud * 0.4],
    ];
  }),
  [T.enter, 'keyboard/press-enter.wav', 0.95],
  [T.enter + 3, 'keyboard/release-enter.wav', 0.45],
  ...WORD.map((w, i): [number, string, number] => [w.tap, `keyboard/press-${ROWS[w.key.row]}.wav`, 0.34 + (i % 2) * 0.05]),
  [T.press, 'keyboard/press-enter.wav', 0.8],
];

export type KeysProps = { music: boolean };

export const Keys: React.FC<KeysProps> = ({ music }) => {
  const frame = useCurrentFrame();
  const ready = useFonts();
  const cam = camera(frame);
  return (
    <AbsoluteFill style={{ background: GROUND }}>
      {ready && (
        <ThreeCanvas width={W} height={H} flat shadows camera={{ fov: FOV, near: 0.1, far: 160 }}>
          <color attach="background" args={[GROUND]} />
          <fog attach="fog" args={[GROUND, 15, 44]} />
          <Rig cam={cam} />
          <Lights frame={frame} cam={cam} />
          <Board frame={frame} cam={cam} />
        </ThreeCanvas>
      )}
      <Finish />
      <Sequence from={T.hook} durationInFrames={T.type + 2}><Hook /></Sequence>
      <Sequence from={T.type} durationInFrames={T.rest - T.type}><Typing /></Sequence>
      <Sequence from={T.rest} durationInFrames={T.cta - T.rest}><Rest /></Sequence>
      <Sequence from={T.cta}><Cta /></Sequence>
      {music && <Audio src={staticFile('v3-keys/music.m4a')} volume={0.92} />}
      {SOUNDS.map(([from, name, volume], i) => (
        <Sequence key={i} from={from} layout="none"><Audio src={staticFile(`sfx/${name}`)} volume={volume} /></Sequence>
      ))}
    </AbsoluteFill>
  );
};
