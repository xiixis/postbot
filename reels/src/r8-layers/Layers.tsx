// Ролик «19 слоёв». 26 с, 1080×1920, музыка 120 ударов в минуту, светлая страница.
//
// Тезис: кадр «собрал кадры» из ролика «Слова под бит» разбирается на девятнадцать слоёв,
// слои отрываются всё чаще, камера облетает стопку, слои сходятся, и кадр оживает настоящим
// видео. Потом камера отъезжает, и этот кадр оказывается одним из 450 кадров ролика. В конце
// камера ныряет обратно в свой кадр и встаёт как на нулевом кадре: ролик закольцован.
// Разрешённые приёмы: бумага, графит, олива, лаймовые линии подписей, моно для подписей.
import React, { useLayoutEffect, useMemo } from 'react';
import { ThreeCanvas, useOffthreadVideoTexture } from '@remotion/three';
import { useThree } from '@react-three/fiber';
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame, useRemotionEnvironment } from 'remotion';
import * as THREE from 'three';
import { hit } from '../lib/beat';
import { color, enter, H, leave, mono, safe, sans, W } from '../lib/brand';
import { Mask } from '../lib/Mask';
import { useScreen } from '../lib/screen';
import { useTextures } from '../lib/textures';
import { LAYER_NAMES } from '../mock/WordsLayer';
import { Captions, type Word } from '../series/Captions';
import { ATLAS, ATLAS_POS, b, BAR, camera, FOV, gridAlpha, LAYERS, layerZ, LENGTH, lift, liftAt, lifted, onPlane, PLANE, spread, T, VIDEO_AT, videoOn } from './motion';
import words from '../series/words/r8.json';

const PAPER = '#ECEADE';
const DESK = '#DAD7C8';                          // стол под страницей: страница видна листом

const TEXTURES = [
  ...new Array(LAYERS).fill(0).map((_, i) => `mock/layers/${String(i).padStart(2, '0')}.png`),
  'r8-layers/atlas-0.jpg', 'r8-layers/atlas-1.jpg', 'r8-layers/f208.jpg', 'r8-layers/last.jpg',
];

// Где у слоя подпись: правый верх страницы, середина слова, плашки, клетки.
const cellCenter = (k: number) => {
  const w = (820 - 18 * 4) / 5, h = (600 - 18 * 2) / 3;
  return [80 + (k % 5) * (w + 18) + w / 2, 800 + Math.floor(k / 5) * (h + 18) + h / 2] as const;
};
const ANCHOR = (i: number): readonly [number, number] =>
  i === 0 ? [1000, 120] : i === 1 ? [300, 278] : i === 2 ? [690, 520] : i === 3 ? [700, 440] : cellCenter(i - 4);

const Rig: React.FC<{ frame: number }> = ({ frame }) => {
  const cam = useThree((s) => s.camera);
  const { pos, aim } = camera(frame);
  useLayoutEffect(() => {
    cam.position.copy(pos);
    cam.lookAt(aim);
    cam.updateMatrixWorld();
  });
  return null;
};

const VideoPlane: React.FC<{ frame: number }> = ({ frame }) => {
  const map = useOffthreadVideoTexture({ src: staticFile('r7-chain/screen.mp4'), toneMapped: false });
  const mat = useScreen(map, 1, videoOn(frame));
  return <mesh position={[0, 0, 0.05]} material={mat} renderOrder={40}><planeGeometry args={[PLANE.w, PLANE.h]} /></mesh>;
};

const StillPlane: React.FC<{ frame: number; map: THREE.Texture }> = ({ frame, map }) => {
  const mat = useScreen(map, 1, videoOn(frame));
  return <mesh position={[0, 0, 0.05]} material={mat} renderOrder={40}><planeGeometry args={[PLANE.w, PLANE.h]} /></mesh>;
};

const Scene: React.FC<{ frame: number; maps: THREE.Texture[] }> = ({ frame, maps }) => {
  const { isRendering } = useRemotionEnvironment();
  const layers = maps.slice(0, LAYERS);
  const [atlasA, atlasB, still208, last] = maps.slice(LAYERS);
  const s = spread(frame);
  const camZ = camera(frame).pos.z;
  const grid = gridAlpha(camZ);
  // рамка толще издалека, чтобы наш кадр читался среди всех; на ударе вспыхивает
  const border = Math.max(0.17, camZ * 0.009) * (1 + hit(frame, Math.floor(frame / 15) * 15, 8) * 0.25);
  const showLayers = frame < T.live + 8 || frame >= T.dive;
  const showGrid = frame >= T.join + 20 && grid > 0.01;
  const ring = Math.min(videoOn(frame), ease01(frame, T.pull, T.pull + 20)) * (1 - ease01(frame, T.dive + 10, T.dive + 30));
  // видео играет с 6,95 с исходного ролика до его конца, дальше стоит последний кадр
  const videoFrom = T.live - VIDEO_AT;
  const videoLeft = 450 - VIDEO_AT;
  return (
    <>
      <Rig frame={frame} />
      {/* тень страницы на столе */}
      <mesh position={[0.12, -0.16, -0.03]}>
        <planeGeometry args={[PLANE.w, PLANE.h]} />
        <meshBasicMaterial color="#000000" transparent opacity={0.16} depthWrite={false} />
      </mesh>
      {showLayers && layers.map((m, i) => (
        <group key={i}>
          <mesh position={[0, 0, layerZ(i, frame)]} renderOrder={i * 2 + 1}>
            <planeGeometry args={[PLANE.w, PLANE.h]} />
            <meshBasicMaterial map={m} transparent={i > 0} depthWrite={i === 0} toneMapped={false} />
          </mesh>
          {i > 0 && s > 0.01 && (
            // тень слоя на нижних: та же картинка чёрным, со сдвигом, только пока слои разведены
            <mesh position={[0.05, -0.07, layerZ(i, frame) - 0.012]} renderOrder={i * 2}>
              <planeGeometry args={[PLANE.w, PLANE.h]} />
              <meshBasicMaterial map={m} transparent opacity={0.2 * s * lift(i, frame)} color="#000000" depthWrite={false} />
            </mesh>
          )}
        </group>
      ))}
      {showGrid && ATLAS_POS.map((p, k) => (
        <mesh key={k} position={[p.x, p.y, -0.02]}>
          <planeGeometry args={[ATLAS.w, ATLAS.h]} />
          <meshBasicMaterial map={k === 0 ? atlasA : atlasB} toneMapped={false} transparent opacity={grid} />
        </mesh>
      ))}
      {ring > 0.01 && (
        // лаймовая рамка: вот он, наш кадр среди всех
        <mesh position={[0, 0, 0.03]}>
          <planeGeometry args={[PLANE.w + border * 2, PLANE.h + border * 2]} />
          <meshBasicMaterial color={color.lime} transparent opacity={ring} toneMapped={false} />
        </mesh>
      )}
      {frame >= T.live && frame < T.dive + 22 && (
        isRendering && frame < T.live + videoLeft
          ? <Sequence from={videoFrom} durationInFrames={450} layout="none"><VideoPlane frame={frame} /></Sequence>
          : <StillPlane frame={frame} map={frame < T.live + videoLeft ? still208 : last} />
      )}
    </>
  );
};

const ease01 = (frame: number, a: number, z: number) => Math.min(1, Math.max(0, (frame - a) / (z - a)));

// Подпись у слоя: лаймовая линия и имя, проецируются той же камерой, что снимает сцену.
const Label: React.FC<{ frame: number }> = ({ frame }) => {
  const n = lifted(frame);
  if (n === 0 || frame >= T.join) return null;
  const i = n - 1;
  const since = frame - (i === 0 ? T.peel : liftAt(i));
  const out = leave(frame, T.join - 10, 10);
  const { pos, aim } = camera(frame);
  const cam = new THREE.PerspectiveCamera(FOV, W / H, 0.1, 600);
  cam.position.copy(pos);
  cam.lookAt(aim);
  cam.updateMatrixWorld();
  cam.updateProjectionMatrix();
  const [ax, ay] = ANCHOR(i);
  const p = onPlane(ax, ay);
  p.z = layerZ(i, frame);
  p.project(cam);
  const px = ((p.x + 1) / 2) * W, py = ((1 - p.y) / 2) * H;
  const t = enter(frame, frame - since, 6);
  return (
    <div style={{ position: 'absolute', left: px, top: py - 26, display: 'flex', alignItems: 'center', gap: 12, opacity: t * (1 - out) }}>
      <div style={{ width: 14, height: 14, borderRadius: 7, background: color.lime, boxShadow: `0 0 0 3px ${color.graphite}` }} />
      <div style={{ width: 60 * t, height: 4, background: color.graphite }} />
      <div style={{ fontFamily: mono, fontWeight: 600, fontSize: 36, color: color.graphite, background: color.lime, padding: '4px 14px', borderRadius: 10 }}>
        {LAYER_NAMES[i]}
      </div>
    </div>
  );
};

// Счётчик слоёв: растёт с каждым оторванным слоем, на последнем замирает.
const Counter: React.FC<{ frame: number }> = ({ frame }) => {
  const n = lifted(frame);
  if (n === 0) return null;
  const inn = enter(frame, T.peel, 12);
  const out = leave(frame, T.join + 4, 12);
  const kick = hit(frame, n === 1 ? T.peel : liftAt(n - 1), 6);
  return (
    <div style={{ position: 'absolute', left: safe.left, top: 1330, opacity: inn * (1 - out), display: 'flex', alignItems: 'baseline', gap: 14 }}>
      <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 132, color: color.graphite, transform: `scale(${1 + kick * 0.06})`, transformOrigin: 'left bottom', letterSpacing: '-0.04em' }}>{n}</div>
      <div style={{ fontFamily: mono, fontWeight: 500, fontSize: 56, color: color.olive }}>/ 19 слоёв</div>
    </div>
  );
};

const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const out = leave(frame, BAR - 10, 10);
  return (
    <AbsoluteFill style={{ opacity: 1 - out, transform: `translateY(${-out * 90}px)` }}>
      <div style={{ position: 'absolute', left: safe.left, top: safe.top - 40 }}>
        <Mask px={132} color={color.graphite}>19 слоёв</Mask>
        <Mask px={132} color={color.olive}>в одном кадре</Mask>
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
  const out = leave(frame, T.dive - T.cta + 4, 14);
  const done = frame >= PRESS;
  const press = frame >= PRESS - 2 && frame < PRESS ? 0.94 : 1 + hit(frame, PRESS, 10) * 0.06;
  return (
    <AbsoluteFill style={{ opacity: 1 - out }}>
      <AbsoluteFill style={{ background: `linear-gradient(180deg, ${PAPER} 0%, rgba(236,234,222,0.92) 34%, rgba(236,234,222,0) 52%)` }} />
      <div style={{ position: 'absolute', left: safe.left, top: safe.top, width: 820, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 34 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 20, ...slot(0) }}>
          <Img src={staticFile('brand/logo.png')} style={{ width: 72, height: 72, filter: 'brightness(0.55) saturate(1.2)' }} />
          <div style={{ fontFamily: sans, fontWeight: 800, fontSize: 54, color: color.graphite, letterSpacing: '-0.02em' }}>4xTube</div>
        </div>
        <div style={{ ...slot(6) }}>
          <div style={{
            width: 700, height: 172, borderRadius: 999, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 20,
            background: done ? color.graphite : color.lime, boxShadow: `inset 0 0 0 6px ${color.graphite}`, transform: `scale(${press})`,
            fontFamily: sans, fontWeight: 800, fontSize: 78, letterSpacing: '-0.025em', color: done ? color.lime : color.graphite,
          }}>
            {done ? 'Подписаны' : 'Подписаться'}
            {done && (
              <svg width="62" height="62" viewBox="0 0 24 24" fill="none" stroke={color.lime} strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12.5l4.5 4.5L19 7" />
              </svg>
            )}
          </div>
        </div>
        <div style={{ width: 800, fontFamily: sans, fontWeight: 700, fontSize: 62, lineHeight: 1.14, letterSpacing: '-0.025em', color: color.graphite, ...slot(12) }}>
          Какой кадр разложить следующим?
        </div>
      </div>
    </AbsoluteFill>
  );
};

const SOUNDS: [number, string, number][] = [
  [T.peel, 'keyboard/press-space.wav', 0.5],
  ...new Array(LAYERS - 1).fill(0).map((_, k): [number, string, number] => [liftAt(k + 1), `keyboard/press-${['r1', 'r2', 'r3'][k % 3]}.wav`, 0.32 + 0.02 * k]),
  [T.orbit - 20, 'whoosh.wav', 0.3],
  [T.join + 10, 'keyboard/press-enter.wav', 0.85],
  [T.pull + 4, 'whoosh.wav', 0.4],
  [T.cta + PRESS, 'click.wav', 0.5],
  [T.dive + 4, 'whoosh.wav', 0.35],
];

export type LayersProps = { music: boolean };

export const LayersReel: React.FC<LayersProps> = ({ music }) => {
  const frame = useCurrentFrame();
  const maps = useTextures(TEXTURES.map((f) => staticFile(f)));
  const flash = hit(frame, T.join + 12, 10) * 0.35;
  return (
    <AbsoluteFill style={{ background: DESK }}>
      {maps && (
        <ThreeCanvas width={W} height={H} flat camera={{ fov: FOV, near: 0.1, far: 600 }}>
          <color attach="background" args={[DESK]} />
          <Scene frame={frame} maps={maps} />
        </ThreeCanvas>
      )}
      <AbsoluteFill style={{ background: '#FFFFFF', opacity: flash }} />
      <Label frame={frame} />
      <Counter frame={frame} />
      <Sequence from={T.hook} durationInFrames={BAR + 2}><Hook /></Sequence>
      <Sequence from={T.cta} durationInFrames={T.dive - T.cta + 20}><Cta /></Sequence>
      {/* пока слои разобраны, субтитры наверху; когда кадр во весь экран, его надписи наверху,
          и субтитры уходят вниз, где в ролике пусто */}
      <Captions words={words as Word[]} top={safe.top} tone="light" hide={[[0, BAR], [T.join, LENGTH]]} />
      <Captions words={words as Word[]} top={1416} px={50} tone="light" hide={[[0, T.join], [T.cta, LENGTH]]} />
      {music && <Audio src={staticFile('series/r8.m4a')} volume={0.92} />}
      {SOUNDS.map(([from, name, volume], i) => (
        <Sequence key={i} from={from} layout="none"><Audio src={staticFile(`sfx/${name}`)} volume={volume} /></Sequence>
      ))}
    </AbsoluteFill>
  );
};

