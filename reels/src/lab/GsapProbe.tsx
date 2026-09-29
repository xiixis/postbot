// Проба: GSAP в Remotion. Три приёма, которых нет в голом Remotion:
// буквы по одной (SplitText), линия, которая рисуется сама (DrawSVG), и свой таймлайн с метками.
// На эту пробу ссылается скил gsap: код отсюда проверен рендером.
import React from 'react';
import gsap from 'gsap';
import { DrawSVGPlugin } from 'gsap/DrawSVGPlugin';
import { SplitText } from 'gsap/SplitText';
import { AbsoluteFill } from 'remotion';
import { beats, useTimeline } from '../lib/gsap';
import { color, sans } from '../claude-montage/tokens';

gsap.registerPlugin(SplitText, DrawSVGPlugin);

const BPM = 100;

export const GsapProbe: React.FC = () => {
  const root = useTimeline((tl, scope) => {
    const title = new SplitText(scope.querySelector('.title'), { type: 'chars,words' });
    tl.addLabel('in', 0)
      .from(title.chars, { yPercent: 110, opacity: 0, duration: 0.6, ease: 'power3.out', stagger: 0.025 }, 'in')
      .fromTo('.line', { drawSVG: '0%' }, { drawSVG: '100%', duration: 0.8, ease: 'power2.inOut' }, beats(2, BPM))
      .from('.note', { y: 30, opacity: 0, duration: 0.5, ease: 'power3.out' }, beats(3, BPM))
      .addLabel('out', beats(6, BPM))
      .to(title.chars, { yPercent: -110, opacity: 0, duration: 0.35, ease: 'power2.in', stagger: 0.012 }, 'out');
  });

  return (
    <AbsoluteFill ref={root} style={{ background: color.ground, padding: '420px 80px 0', fontFamily: sans, color: color.ink }}>
      <div style={{ overflow: 'hidden' }}>
        <div className="title" style={{ fontSize: 132, fontWeight: 700, lineHeight: 1.08, letterSpacing: '-0.035em' }}>
          Буквы едут по одной
        </div>
      </div>
      <svg width="820" height="40" viewBox="0 0 820 40" style={{ marginTop: 30 }}>
        <path className="line" d="M4 24 C 180 4, 320 38, 470 18 S 720 8, 816 22" fill="none" stroke={color.action} strokeWidth="8" strokeLinecap="round" />
      </svg>
      <div className="note" style={{ marginTop: 40, fontSize: 54, fontWeight: 700 }}>и линия рисуется сама</div>
    </AbsoluteFill>
  );
};
