// Развязка и призыв. Оба стоят на цельной сцене: кот за монтажным столом остаётся в кадре.
import React from 'react';
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import { Claude, Line } from './Text';
import { BEAT, at, color, column, enter, leave, mix, safe, sans, size } from './tokens';

export const Reveal: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame < at.reveal + 4 || frame > at.cta + 6) return null;
  const out = leave(frame, at.cta - 10, 12);
  const note = enter(frame, at.reveal + 34, 24);
  return (
    <div style={{ position: 'absolute', left: safe.left, top: safe.top, width: column, opacity: 1 - out, transform: `translateY(${-out * 30}px)` }}>
      <Line px={96} from={at.reveal + 10}>Его собрал</Line>
      <Line px={232} from={at.reveal + 16} dur={30} tight={1.0}><Claude /></Line>
      <div style={{
        marginTop: 38, fontFamily: sans, fontWeight: 700, fontSize: size.body, lineHeight: 1.2, color: color.ink,
        letterSpacing: '-0.015em', whiteSpace: 'nowrap', opacity: note, transform: `translateY(${(1 - note) * 18}px)`,
      }}>450 кадров<br />и ни одного клика мышкой</div>
    </div>
  );
};

export const PRESS = at.cta + BEAT * 2;      // кадр 396, на удар

const Slot: React.FC<{ from: number; children: React.ReactNode }> = ({ from, children }) => {
  const frame = useCurrentFrame();
  const t = enter(frame, from, 24);
  return <div style={{ opacity: t, transform: `translateY(${(1 - t) * 26}px)` }}>{children}</div>;
};

export const CTA: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame < at.cta - 8) return null;
  const dim = enter(frame, at.cta - 8, 30);
  const done = frame >= PRESS;
  const press = frame >= PRESS - 3 && frame < PRESS ? 0.955 : mix(enter(frame, PRESS, 12), 0.955, 1);
  const ring = enter(frame, PRESS, 26);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{
        opacity: dim,
        background: 'linear-gradient(180deg, rgba(11,12,9,0.86) 0%, rgba(11,12,9,0.7) 38%, rgba(11,12,9,0.12) 62%, rgba(11,12,9,0) 100%)',
      }} />
      <div style={{ position: 'absolute', left: safe.left, top: safe.top, width: column, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 40 }}>
        <Slot from={at.cta + 2}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
            <Img src={staticFile('claude-montage/logo.png')} style={{ width: 72, height: 72 }} />
            <div style={{ fontFamily: sans, fontWeight: 700, fontSize: 52, color: color.ink, letterSpacing: '-0.02em' }}>4xTube</div>
          </div>
        </Slot>

        <Slot from={at.cta + 8}>
          <div style={{ position: 'relative', transform: `scale(${press})`, transformOrigin: 'left center' }}>
            <div style={{
              position: 'absolute', inset: 0, borderRadius: 999, boxShadow: `0 0 0 4px ${color.action}`,
              transform: `scale(${1 + ring * 0.16}, ${1 + ring * 0.4})`, opacity: done ? (1 - ring) * 0.8 : 0,
            }} />
            <div style={{
              width: 660, height: 156, borderRadius: 999, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 20,
              background: done ? 'rgba(11,12,9,0.7)' : color.action, boxShadow: `inset 0 0 0 4px ${color.action}`,
              fontFamily: sans, fontWeight: 700, fontSize: 70, letterSpacing: '-0.02em', color: done ? color.action : color.ground,
            }}>
              {done ? 'Вы подписаны' : 'Подписаться'}
              {done && (
                <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke={color.action} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M4.5 12.5l5 5 10-10.5" />
                </svg>
              )}
            </div>
          </div>
        </Slot>

        <Slot from={at.cta + 18}>
          <div style={{ width: 760, fontFamily: sans, fontWeight: 700, fontSize: 58, lineHeight: 1.16, letterSpacing: '-0.02em', color: color.ink }}>
            Как повторить, показываю в Telegram
          </div>
        </Slot>

        <Slot from={at.cta + 26}>
          <div style={{
            padding: '18px 36px', borderRadius: 22, background: color.action,
            fontFamily: sans, fontWeight: 700, fontSize: 46, color: color.ground, letterSpacing: '-0.01em',
          }}>ссылка в профиле ↗</div>
        </Slot>
      </div>
    </AbsoluteFill>
  );
};
