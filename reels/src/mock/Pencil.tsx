// Макет ролика «Карандаш»: 0 бумага и первый квадрат с заголовком, 1 четыре квадрата с дудлами,
// 2 первый квадрат перевернулся в настоящий кадр, 3 призыв с карандашной кнопкой, ставшей настоящей.
import React from 'react';
import { loadFont } from '@remotion/google-fonts/Caveat';
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import { color, safe, sans, W } from '../lib/brand';
import { bars, button, catDoodle, d, type Pt, rect } from './strokes';

const hand = loadFont('normal', { weights: ['500', '700'], subsets: ['latin', 'cyrillic'] }).fontFamily;
const PAPER = '#F1EFE4';
const INK = '#2A2B24';
const MARK = 'rgba(199,226,75,0.55)';

// Четыре квадрата раскадровки, два на два.
const CELL = 380;
const grid = [[80, 560], [620, 560], [80, 1000], [620, 1000]] as Pt[];

const Stroke: React.FC<{ paths: Pt[][]; width?: number; ink?: string }> = ({ paths, width = 5, ink = INK }) => (
  <g fill="none" stroke={ink} strokeLinecap="round" strokeLinejoin="round">
    {paths.map((p, i) => (
      <React.Fragment key={i}>
        <path d={d(p)} strokeWidth={width} strokeOpacity={0.9} />
        <path d={d(p.map(([x, y]) => [x + 1.5, y + 1.2]))} strokeWidth={width * 0.6} strokeOpacity={0.4} />
      </React.Fragment>
    ))}
  </g>
);

const Paper: React.FC = () => (
  <svg width={W} height={1920} style={{ position: 'absolute', inset: 0 }}>
    <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" /><feColorMatrix values="0 0 0 0 0.2 0 0 0 0 0.2 0 0 0 0 0.15 0 0 0 0.16 0" /></filter>
    <rect width={W} height={1920} fill={PAPER} />
    <rect width={W} height={1920} filter="url(#grain)" />
  </svg>
);

const Label: React.FC<{ x: number; y: number; text: string }> = ({ x, y, text }) => (
  <div style={{ position: 'absolute', left: x, top: y, fontFamily: hand, fontWeight: 700, fontSize: 52, color: INK, transform: 'rotate(-2deg)' }}>{text}</div>
);

export const MockPencil: React.FC = () => {
  const stage = useCurrentFrame();
  const squares = grid.map(([x, y], i) => rect(x, y, CELL, CELL, 100 + i));
  const cat = catDoodle(grid[0][0] + CELL / 2, grid[0][1] + CELL / 2 + 10, 110);
  const wave = bars(grid[2][0] + 40, grid[2][1] + 60, CELL - 80, CELL - 120);
  const btn = button(grid[3][0] + 50, grid[3][1] + CELL / 2 - 55, CELL - 100, 110);
  return (
    <AbsoluteFill style={{ background: PAPER }}>
      <Paper />
      <div style={{ position: 'absolute', left: safe.left, top: 230, fontFamily: hand, fontWeight: 700, fontSize: 124, color: INK, lineHeight: 1.0, transform: 'rotate(-1.5deg)' }}>
        {stage === 3 ? 'План стал роликом' : 'План на 4 квадрата'}
      </div>
      <svg width={W} height={1920} style={{ position: 'absolute', inset: 0 }}>
        {stage === 0 && <Stroke paths={squares[0]} />}
        {stage >= 1 && stage < 3 && squares.map((s, i) => (stage === 2 && i === 0 ? null : <Stroke key={i} paths={s} />))}
        {stage >= 1 && stage < 3 && stage !== 2 && <Stroke paths={cat} width={5} />}
        {stage >= 1 && stage < 3 && <Stroke paths={wave} width={7} />}
        {stage >= 1 && stage < 3 && <Stroke paths={btn} width={5} />}
        {stage === 2 && <rect x={grid[0][0] - 14} y={grid[0][1] - 14} width={CELL + 28} height={CELL + 28} rx={22} fill="none" stroke={MARK} strokeWidth={16} />}
        {stage === 3 && <Stroke paths={button(safe.left, 760, 700, 164)} width={6} />}
      </svg>
      {stage >= 1 && stage < 3 && (
        <>
          <Label x={grid[0][0] + 20} y={grid[0][1] + CELL + 10} text="кот" />
          <Label x={grid[1][0] + 20} y={grid[1][1] + CELL + 10} text="слово" />
          <Label x={grid[2][0] + 20} y={grid[2][1] + CELL + 10} text="удары" />
          <Label x={grid[3][0] + 20} y={grid[3][1] + CELL + 10} text="кнопка" />
          <div style={{ position: 'absolute', left: grid[1][0] + 40, top: grid[1][1] + 96, fontFamily: sans, fontWeight: 800, fontSize: 150, color: INK, letterSpacing: '-0.04em', opacity: 0.85 }}>БИТ</div>
        </>
      )}
      {stage === 2 && (
        <div style={{ position: 'absolute', left: grid[0][0], top: grid[0][1], width: CELL, height: CELL, borderRadius: 14, overflow: 'hidden', boxShadow: '0 18px 40px rgba(42,43,36,0.25)' }}>
          <Img src={staticFile('v2-words/cover.jpg')} style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: '50% 20%' }} />
        </div>
      )}
      {stage === 3 && (
        <>
          <div style={{ position: 'absolute', left: safe.left + 350, top: 760, width: 350, height: 164, borderRadius: '0 999px 999px 0', background: color.lime, boxShadow: `inset 0 0 0 6px ${INK}` }} />
          <div style={{ position: 'absolute', left: safe.left, top: 760, width: 700, height: 164, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: sans, fontWeight: 800, fontSize: 76, color: INK, letterSpacing: '-0.025em' }}>Подписаться</div>
          <div style={{ position: 'absolute', left: safe.left, top: 980, width: 800, fontFamily: hand, fontWeight: 700, fontSize: 68, color: INK, lineHeight: 1.1, transform: 'rotate(-1deg)' }}>
            Какой план нарисовать следующим?
          </div>
          <Img src={staticFile('v2-words/end.jpg')} style={{ position: 'absolute', left: 300, top: 1120, width: 760, maskImage: 'linear-gradient(180deg,#000 70%,transparent 100%)', WebkitMaskImage: 'linear-gradient(180deg,#000 70%,transparent 100%)' }} />
        </>
      )}
    </AbsoluteFill>
  );
};
