// Один слой кадра «собрал кадры» из ролика «Слова под бит» на прозрачном фоне.
// Слой 0 страница, 1 слово «собрал», 2 лаймовая плашка, 3 слово «кадры», 4–18 пятнадцать клеток.
// Из этих слоёв ролик «19 слоёв» собирает разложенный кадр: tools/layers.mjs рендерит их в PNG.
import React from 'react';
import { AbsoluteFill } from 'remotion';
import { color, column, safe, sans } from '../lib/brand';
import { Mask } from '../lib/Mask';

export const LAYERS = 19;
export const LAYER_NAMES = ['страница', 'слово', 'плашка', 'слово', ...new Array(15).fill(0).map((_, i) => `клетка ${i + 1}`)];

const PAPER = '#ECEADE';
const PX = 250;
const cols = 5, rows = 3, gap = 18;
const w = (column - gap * (cols - 1)) / cols;
const h = (600 - gap * (rows - 1)) / rows;

export const WordsLayer: React.FC<{ layer: number }> = ({ layer }) => (
  <AbsoluteFill style={{ background: layer === 0 ? PAPER : 'transparent' }}>
    {layer === 1 && (
      <div style={{ position: 'absolute', left: safe.left, top: safe.top, fontFamily: sans, fontWeight: 700, fontSize: 76, lineHeight: '96px', letterSpacing: '-0.03em', color: color.olive }}>собрал</div>
    )}
    {(layer === 2 || layer === 3) && (
      // та же разметка, что в ролике (v2-words/Words.tsx): плашка по ширине слова плюс 18 px с боков
      <div style={{ position: 'absolute', left: safe.left, top: safe.top + 102 }}>
        <div style={{ position: 'relative' }}>
          {layer === 2 && (
            <div style={{ position: 'absolute', left: -18, right: -18, top: PX * 0.5, height: PX * 0.52, borderRadius: PX * 0.12, background: color.lime }} />
          )}
          <div style={{ position: 'relative', opacity: layer === 3 ? 1 : 0 }}>
            <Mask px={PX} color={color.graphite}>кадры</Mask>
          </div>
        </div>
      </div>
    )}
    {layer >= 4 && (() => {
      const i = layer - 4;
      return (
        <div style={{
          position: 'absolute', left: safe.left + (i % cols) * (w + gap), top: 800 + Math.floor(i / cols) * (h + gap), width: w, height: h,
          borderRadius: 22, background: color.graphite, boxShadow: `inset 0 0 0 4px ${color.graphite}`,
        }} />
      );
    })()}
  </AbsoluteFill>
);
