// Макет ролика «20 000 точек»: четыре ключевых кадра, по одному на кадр композиции.
// 0 крючок с воронкой, 1 портрет кота из точек, 2 слово CLAUDE, 3 призыв со знаком.
import React, { useLayoutEffect, useMemo } from 'react';
import { ThreeCanvas } from '@remotion/three';
import { useThree } from '@react-three/fiber';
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import * as THREE from 'three';
import { color, H, mono, safe, sans, W } from '../lib/brand';
import { Mask } from '../lib/Mask';
import { useTextures } from '../lib/textures';
import { type Cloud, mark, N, portrait, sprite, vortex, word } from './points';

const GROUND = '#07080A';

const Rig: React.FC<{ z: number; y: number; turn: number }> = ({ z, y, turn }) => {
  const cam = useThree((s) => s.camera);
  useLayoutEffect(() => {
    cam.position.set(Math.sin(turn) * z, y, Math.cos(turn) * z);
    cam.lookAt(0, y * 0.3, 0);
    cam.updateMatrixWorld();
  });
  return null;
};

const Points: React.FC<{ cloud: Cloud; size: number }> = ({ cloud, size }) => {
  const map = useMemo(() => sprite(), []);
  const geometry = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(cloud.pos, 3));
    g.setAttribute('color', new THREE.BufferAttribute(cloud.col, 3));
    return g;
  }, [cloud]);
  return (
    <points geometry={geometry}>
      <pointsMaterial map={map} size={size} sizeAttenuation vertexColors transparent depthWrite={false} blending={THREE.AdditiveBlending} toneMapped={false} />
    </points>
  );
};

const Scene: React.FC<{ stage: number; cat: THREE.Texture; logo: THREE.Texture }> = ({ stage, cat, logo }) => {
  const clouds = useMemo(() => [vortex(0), portrait(cat.image as HTMLImageElement, 4.2), word('CLAUDE', 0.8), mark(logo.image as HTMLImageElement, 1.5)], [cat, logo]);
  const cloud = clouds[Math.min(stage, 3)];
  return (
    <>
      <Rig z={stage === 1 ? 7.8 : 8.4} y={stage === 0 ? -0.6 : stage === 3 ? 1.1 : stage === 1 ? -0.3 : 0.3} turn={stage === 1 ? 0.22 : 0} />
      <Points cloud={cloud} size={stage === 0 ? 0.075 : 0.05} />
    </>
  );
};

export const MockDots: React.FC = () => {
  const stage = useCurrentFrame();
  const maps = useTextures([staticFile('v2-words/cover.jpg'), staticFile('brand/logo.png')]);
  return (
    <AbsoluteFill style={{ background: GROUND }}>
      {maps && (
        <ThreeCanvas width={W} height={H} flat camera={{ fov: 40, near: 0.1, far: 60 }}>
          <color attach="background" args={[GROUND]} />
          <Scene stage={stage} cat={maps[0]} logo={maps[1]} />
        </ThreeCanvas>
      )}
      {stage === 0 && (
        <div style={{ position: 'absolute', left: safe.left, top: safe.top }}>
          <Mask px={132} color={color.lime}>20 000 точек</Mask>
          <Mask px={132} color={color.cream}>и одна фраза</Mask>
        </div>
      )}
      {stage === 1 && (
        <div style={{ position: 'absolute', left: safe.left, top: 1330, fontFamily: sans, fontWeight: 700, fontSize: 56, color: color.cream, lineHeight: 1.15 }}>
          Он посчитал <span style={{ color: color.lime }}>каждую</span>.
        </div>
      )}
      {stage === 2 && (
        <div style={{ position: 'absolute', left: safe.left, top: 1330, fontFamily: sans, fontWeight: 700, fontSize: 56, color: color.cream, lineHeight: 1.15 }}>
          И подписал сам.
        </div>
      )}
      {stage === 3 && (
        <>
          <div style={{ position: 'absolute', left: safe.left, top: safe.top, display: 'flex', alignItems: 'center', gap: 20 }}>
            <Img src={staticFile('brand/logo.png')} style={{ width: 72, height: 72 }} />
            <div style={{ fontFamily: sans, fontWeight: 800, fontSize: 54, color: color.cream }}>4xTube</div>
          </div>
          <div style={{ position: 'absolute', left: safe.left, top: 1130, width: 700, height: 164, borderRadius: 999, background: color.lime, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: sans, fontWeight: 800, fontSize: 76, color: color.graphite, letterSpacing: '-0.025em' }}>
            Подписаться
          </div>
          <div style={{ position: 'absolute', left: safe.left, top: 1330, width: 820, fontFamily: sans, fontWeight: 700, fontSize: 56, lineHeight: 1.14, color: color.lime }}>
            Что собрать из точек в следующий раз?
          </div>
        </>
      )}
      <div style={{ position: 'absolute', left: safe.left, top: 1500 - 60, fontFamily: mono, fontWeight: 500, fontSize: 28, color: 'rgba(241,242,234,0.45)' }}>
        {stage === 1 ? `${N.toLocaleString('ru-RU')} точек` : ''}
      </div>
      <AbsoluteFill style={{ background: 'radial-gradient(120% 80% at 50% 60%, rgba(7,8,10,0) 60%, rgba(7,8,10,0.6) 100%)', pointerEvents: 'none' }} />
    </AbsoluteFill>
  );
};
