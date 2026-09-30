// Общие части второй серии: промпт, карточки скилов, кадр «сохрани», призыв.
// У каждого ролика свой показ, а эти четыре состояния одинаковые: так серия узнаётся.
import React from 'react';
import gsap from 'gsap';
import { SplitText } from 'gsap/SplitText';
import { AbsoluteFill, Img, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { hit } from '../lib/beat';
import { color, column, enter, glide, leave, mix, mono, rnd, safe, sans } from '../lib/brand';
import { useTimeline } from '../lib/gsap';
import { Mask } from '../lib/Mask';
import { b, BAR, T } from './grid';

gsap.registerPlugin(SplitText);

export const INK = { light: color.cream, dim: 'rgba(241,242,234,0.55)' };

// Заголовок крючка: две строки, буквы доезжают с опережением, уходит вверх к концу такта.
export const Headline: React.FC<{ lines: React.ReactNode[]; px?: number; color?: string; top?: number; lead?: number }> =
  ({ lines, px = 122, color: ink = color.cream, top = safe.top, lead = 0.4 }) => {
    const root = useTimeline((tl, scope) => {
      scope.querySelectorAll('.h').forEach((el, i) => {
        const s = new SplitText(el, { type: 'chars' });
        tl.from(s.chars, { yPercent: 118, duration: 0.5, ease: 'expo.out', stagger: 0.02 }, i * 0.12);
      });
      tl.to('.head', { yPercent: -30, opacity: 0, duration: 0.24, ease: 'power2.in' }, lead + BAR / 30 - 0.3);
    }, lead);
    return (
      <AbsoluteFill ref={root}>
        <div className="head" style={{ position: 'absolute', left: safe.left, top }}>
          {lines.map((l, i) => <Mask key={i} px={px} color={ink} className="h">{l}</Mask>)}
        </div>
      </AbsoluteFill>
    );
  };

// Слова промпта ложатся в карточку одно за другим за полтакта: как вставленный текст, а не набор.
export const WORDS_IN = b(2);
const TYPE_FROM = 6;

export const Prompt: React.FC<{ text: string; skills: string[]; hold?: number; dark?: boolean }> = ({ text, skills, hold = T.save - T.prompt, dark = true }) => {
  const frame = useCurrentFrame();
  const words = text.split(' ');
  const inn = enter(frame, 0, 12);
  const out = leave(frame, hold - 8, 8);
  const shown = words.filter((_, i) => frame >= TYPE_FROM + (i * WORDS_IN) / words.length).length;
  const done = shown === words.length;
  const chipsAt = T.skills - T.prompt;
  return (
    <AbsoluteFill style={{ opacity: 1 - out, transform: `translateY(${-out * 90}px)` }}>
      <div style={{ position: 'absolute', left: safe.left, top: 300, width: column, opacity: inn, transform: `translateY(${(1 - inn) * 60}px)` }}>
        <div style={{ fontFamily: mono, fontWeight: 500, fontSize: 30, color: INK.dim, marginBottom: 18, letterSpacing: '0.02em' }}>
          {frame < 8 ? '' : 'я › claude'}
        </div>
        <div style={{
          borderRadius: 40, padding: '44px 48px', background: dark ? '#1C1E17' : color.graphite,
          boxShadow: done ? `0 0 0 5px ${color.lime}` : '0 0 0 3px rgba(241,242,234,0.16)',
          fontFamily: sans, fontWeight: 700, fontSize: 74, lineHeight: 1.16, letterSpacing: '-0.02em', color: color.cream,
        }}>
          {words.slice(0, shown).join(' ')}
          <span style={{ display: 'inline-block', width: 9, height: 70, marginLeft: 8, verticalAlign: '-9px', borderRadius: 3, background: color.lime, opacity: done ? (Math.floor(frame / 9) % 2 ? 0.25 : 1) : 1 }} />
        </div>
        <div style={{ display: 'flex', gap: 18, marginTop: 30, flexWrap: 'wrap' }}>
          {skills.map((s, i) => {
            const at = chipsAt + b(i);
            const t = enter(frame, at, 10);
            return (
              <div key={s} style={{
                padding: '16px 30px', borderRadius: 999, background: color.lime, color: color.graphite,
                fontFamily: mono, fontWeight: 500, fontSize: 40, letterSpacing: '-0.01em',
                opacity: t, transform: `translateY(${(1 - t) * 40}px) scale(${1 + hit(frame, at, 8) * 0.05})`,
              }}>
                {s}
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Звуки вставки промпта: россыпь настоящих клавиш за полтакта, неровная, и Enter в конце.
export const promptSounds = (from: number, count = 14): [number, string, number][] => {
  const keys: [number, string, number][] = [];
  let at = from + TYPE_FROM;
  for (let i = 0; i < count; i++) {
    at += 1 + Math.floor(rnd(i * 5.3 + from) * 3);
    if (at > from + TYPE_FROM + WORDS_IN) break;
    keys.push([at, `keyboard/press-${['r1', 'r2', 'r3'][i % 3]}.wav`, 0.5 + rnd(i * 2.1) * 0.25]);
  }
  keys.push([from + TYPE_FROM + WORDS_IN + 4, 'keyboard/press-enter.wav', 0.8]);
  return keys;
};

// Кадр «сохрани»: промпт и скилы одной карточкой, строка про описание.
export const Save: React.FC<{ text: string; skills: string[]; what?: string }> = ({ text, skills, what = 'промпт и скилы' }) => {
  const frame = useCurrentFrame();
  const inn = enter(frame, 0, 14);
  const out = leave(frame, BAR - 8, 8);
  return (
    <AbsoluteFill style={{ opacity: inn * (1 - out), transform: `translateY(${(1 - inn) * 70 - out * 90}px)` }}>
      <div style={{ position: 'absolute', left: safe.left, top: safe.top, width: column }}>
        <div style={{ fontFamily: sans, fontWeight: 800, fontSize: 96, lineHeight: 1.05, letterSpacing: '-0.035em', color: color.cream }}>
          Сохрани
        </div>
        <div style={{ fontFamily: sans, fontWeight: 700, fontSize: 52, lineHeight: 1.15, letterSpacing: '-0.02em', color: INK.dim, marginTop: 10 }}>
          {what} лежат в описании
        </div>
        <div style={{
          marginTop: 46, borderRadius: 34, padding: '34px 40px', background: '#1C1E17', boxShadow: '0 0 0 3px rgba(241,242,234,0.16)',
          fontFamily: sans, fontWeight: 700, fontSize: 46, lineHeight: 1.2, letterSpacing: '-0.015em', color: color.cream,
        }}>
          {text}
        </div>
        <div style={{ display: 'flex', gap: 16, marginTop: 24, flexWrap: 'wrap' }}>
          {skills.map((s) => (
            <div key={s} style={{ padding: '12px 26px', borderRadius: 999, background: color.lime, color: color.graphite, fontFamily: mono, fontWeight: 500, fontSize: 36 }}>{s}</div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Призыв: кнопка нажимается на ударе, вопрос зрителю, кот; в конце всё уезжает вверх,
// чтобы повтор ролика начинался без шва.
export const Cta: React.FC<{ question: string; cat: string; catTop?: number; catWidth?: number }> = ({ question, cat, catTop = 900, catWidth = 1000 }) => {
  const frame = useCurrentFrame();
  const PRESS = T.press - T.cta;
  const slot = (from: number) => {
    const t = enter(frame, from, 12);
    return { opacity: t, transform: `translateY(${(1 - t) * 60}px)` } as React.CSSProperties;
  };
  const done = frame >= PRESS;
  const press = frame >= PRESS - 2 && frame < PRESS ? 0.94 : 1 + hit(frame, PRESS, 10) * 0.05;
  const rise = enter(frame, 2, 22);
  const leaveAll = glide(frame, 2 * BAR - 14, 14);
  return (
    <AbsoluteFill style={{ transform: `translateY(${-leaveAll * 260}px)`, opacity: 1 - leaveAll }}>
      {/* снимок на тёмном фоне под цвет страницы не выравнивается: край прячет мягкая маска */}
      <Img src={staticFile(cat)} style={{
        position: 'absolute', left: (1080 - catWidth) / 2, width: catWidth, top: 0,
        transform: `translateY(${mix(rise, 1920, catTop)}px) rotate(${Math.sin(frame / 7) * 0.8}deg)`, transformOrigin: '50% 85%',
        maskImage: 'radial-gradient(ellipse 58% 62% at 50% 52%, #000 55%, transparent 100%)',
        WebkitMaskImage: 'radial-gradient(ellipse 58% 62% at 50% 52%, #000 55%, transparent 100%)',
      }} />
      <div style={{ position: 'absolute', left: safe.left, top: safe.top, width: column, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 30 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 20, ...slot(0) }}>
          <Img src={staticFile('brand/logo.png')} style={{ width: 72, height: 72 }} />
          <div style={{ fontFamily: sans, fontWeight: 800, fontSize: 54, color: color.cream, letterSpacing: '-0.02em' }}>4xTube</div>
        </div>
        <div style={{ ...slot(6) }}>
          <div style={{
            width: 700, height: 164, borderRadius: 999, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 20,
            background: done ? 'transparent' : color.lime, boxShadow: `inset 0 0 0 6px ${color.lime}`,
            fontFamily: sans, fontWeight: 800, fontSize: 76, letterSpacing: '-0.025em', color: done ? color.lime : color.graphite,
            transform: `scale(${press})`, transformOrigin: 'left center',
          }}>
            {done ? 'Вы подписаны' : 'Подписаться'}
            {done && (
              <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke={color.lime} strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4.5 12.5l5 5 10-10.5" />
              </svg>
            )}
          </div>
        </div>
        <div style={{ width: 820, fontFamily: sans, fontWeight: 700, fontSize: 56, lineHeight: 1.14, letterSpacing: '-0.025em', color: color.cream, ...slot(12) }}>
          Как повторить, показываю в Telegram
        </div>
        <div style={{ width: 820, fontFamily: sans, fontWeight: 700, fontSize: 58, lineHeight: 1.14, letterSpacing: '-0.025em', color: color.lime, ...slot(18) }}>
          {question}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Сцена «показ» получает свой такт с нуля: так внутри неё удары считаются от начала показа.
export const Show: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <Sequence from={T.show} durationInFrames={T.save - T.show}>{children}</Sequence>
);
