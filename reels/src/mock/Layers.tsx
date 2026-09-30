// Макет ролика «19 слоёв»: 0 плоский кадр с заголовком, 1 разложенный кадр с подписями,
// 2 слои сошлись и кадр ожил, 3 призыв.
import React, { useLayoutEffect, useMemo } from 'react';
import { ThreeCanvas } from '@remotion/three';
import { useThree } from '@react-three/fiber';
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import * as THREE from 'three';
import { color, H, mono, safe, sans, W } from '../lib/brand';
import { Mask } from '../lib/Mask';
import { useTextures } from '../lib/textures';
import { LAYER_NAMES, LAYERS } from './WordsLayer';

const PAPER = '#ECEADE';
// плоскость ровно во весь кадр на расстоянии 9,6: 2 · 9,6 · tan(20°)
const PLANE = { w: 3.93, h: 6.99 };
const FOV = 40;
const GAP = 0.3;                                   // глубина между слоями в разложенном виде

// Камера макета считается и внутри холста, и снаружи: подписи проецируются той же камерой.
const poseOf = (stage: number) => {
  if (stage === 1) return { pos: new THREE.Vector3(7.6, 2.4, 13.4), aim: new THREE.Vector3(0.3, -0.5, 2.6) };
  return { pos: new THREE.Vector3(0, 0, 9.6), aim: new THREE.Vector3(0, 0, 0) };
};
const layerZ = (i: number, stage: number) => (stage === 1 ? i * GAP : i * 0.002);

const Rig: React.FC<{ stage: number }> = ({ stage }) => {
  const cam = useThree((s) => s.camera);
  const { pos, aim } = poseOf(stage);
  useLayoutEffect(() => {
    cam.position.copy(pos);
    cam.lookAt(aim);
    cam.updateMatrixWorld();
  });
  return null;
};

const Scene: React.FC<{ stage: number; maps: THREE.Texture[] }> = ({ stage, maps }) => (
  <>
    <Rig stage={stage} />
    {maps.map((m, i) => (
      <mesh key={i} position={[0, 0, layerZ(i, stage)]} renderOrder={i}>
        <planeGeometry args={[PLANE.w, PLANE.h]} />
        <meshBasicMaterial map={m} transparent={i > 0} depthWrite={i === 0} toneMapped={false} />
      </mesh>
    ))}
    {stage === 1 && maps.map((_, i) => i > 0 && (
      // тень слоя на предыдущем: полупрозрачная плоскость чуть ниже
      <mesh key={`s${i}`} position={[0.06, -0.08, layerZ(i, stage) - 0.01]} renderOrder={i}>
        <planeGeometry args={[PLANE.w, PLANE.h]} />
        <meshBasicMaterial map={maps[i]} transparent opacity={0.18} color="#000000" depthWrite={false} />
      </mesh>
    ))}
  </>
);

// Проекция точки слоя в пиксели кадра: подписи стоят у своих слоёв.
const project = (stage: number, i: number, x: number, y: number) => {
  const cam = new THREE.PerspectiveCamera(FOV, W / H, 0.1, 60);
  const { pos, aim } = poseOf(stage);
  cam.position.copy(pos);
  cam.lookAt(aim);
  cam.updateMatrixWorld();
  cam.updateProjectionMatrix();
  const p = new THREE.Vector3(x, y, layerZ(i, stage)).project(cam);
  return { px: ((p.x + 1) / 2) * W, py: ((1 - p.y) / 2) * H };
};

export const MockLayers: React.FC = () => {
  const stage = useCurrentFrame();
  const maps = useTextures(new Array(LAYERS).fill(0).map((_, i) => staticFile(`mock/layers/${String(i).padStart(2, '0')}.png`)));
  const labels = useMemo(() => [0, 2, 3, 4, 10, 18].map((i, k) => ({ i, ...project(1, i, PLANE.w / 2, PLANE.h / 2 - 0.6 - k * 0.42) })), []);
  return (
    <AbsoluteFill style={{ background: PAPER }}>
      {maps && stage < 3 && (
        <ThreeCanvas width={W} height={H} flat camera={{ fov: FOV, near: 0.1, far: 60 }}>
          <color attach="background" args={[PAPER]} />
          <Scene stage={stage} maps={maps} />
        </ThreeCanvas>
      )}
      {stage === 0 && (
        <div style={{ position: 'absolute', left: safe.left, top: safe.top - 90 }}>
          <Mask px={132} color={color.graphite}>19 слоёв</Mask>
          <Mask px={132} color={color.olive}>в одном кадре</Mask>
        </div>
      )}
      {stage === 1 && labels.map(({ i, px, py }) => (
        <div key={i} style={{ position: 'absolute', left: px + 6, top: py - 24, display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 70, height: 4, background: color.lime }} />
          <div style={{ fontFamily: mono, fontWeight: 500, fontSize: 34, color: color.graphite, background: 'rgba(236,234,222,0.85)', padding: '4px 12px', borderRadius: 10 }}>
            {LAYER_NAMES[i]}
          </div>
        </div>
      ))}
      {stage === 1 && (
        <div style={{ position: 'absolute', left: safe.left, top: 1330, fontFamily: sans, fontWeight: 700, fontSize: 56, color: color.graphite, lineHeight: 1.15 }}>
          Каждый собрал <span style={{ color: color.olive }}>Claude</span>.
        </div>
      )}
      {stage === 2 && (
        <div style={{ position: 'absolute', left: safe.left, top: 660, fontFamily: sans, fontWeight: 700, fontSize: 56, color: color.graphite, lineHeight: 1.15 }}>
          Сошлись. И ролик пошёл.
        </div>
      )}
      {stage === 3 && (
        <>
          <Img src={staticFile('v2-words/end.jpg')} style={{ position: 'absolute', left: 40, top: 760, width: 1040 }} />
          <div style={{ position: 'absolute', left: safe.left, top: safe.top, display: 'flex', alignItems: 'center', gap: 20 }}>
            <Img src={staticFile('brand/logo.png')} style={{ width: 72, height: 72, filter: 'brightness(0.55) saturate(1.2)' }} />
            <div style={{ fontFamily: sans, fontWeight: 800, fontSize: 54, color: color.graphite }}>4xTube</div>
          </div>
          <div style={{ position: 'absolute', left: safe.left, top: 340, width: 700, height: 172, borderRadius: 999, background: color.lime, boxShadow: `inset 0 0 0 6px ${color.graphite}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: sans, fontWeight: 800, fontSize: 78, color: color.graphite, letterSpacing: '-0.025em' }}>
            Подписаться
          </div>
          <div style={{ position: 'absolute', left: safe.left, top: 560, width: 800, fontFamily: sans, fontWeight: 700, fontSize: 60, lineHeight: 1.14, color: color.graphite }}>
            Какой кадр разложить следующим?
          </div>
        </>
      )}
    </AbsoluteFill>
  );
};
