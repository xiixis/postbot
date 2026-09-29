// Проба: настоящая трёхмерная сцена в Remotion. Объёмный знак канала, свет, тень на полу.
// Всё движение считается из номера кадра. На эту пробу ссылается скил threejs.
import React, { useMemo } from 'react';
import { ThreeCanvas } from '@remotion/three';
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from 'remotion';
import * as THREE from 'three';
import { color, enter, sans } from '../claude-montage/tokens';

// Знак «4» как плоский контур; объём даёт выдавливание с фаской.
const mark = () => {
  const s = new THREE.Shape();
  s.moveTo(0.35, -1.5);
  s.lineTo(0.35, -0.55);
  s.lineTo(-1.35, -0.55);
  s.lineTo(-1.35, 0.05);
  s.lineTo(0.2, 1.5);
  s.lineTo(0.95, 1.5);
  s.lineTo(0.95, 0.05);
  s.lineTo(1.4, 0.05);
  s.lineTo(1.4, -0.55);
  s.lineTo(0.95, -0.55);
  s.lineTo(0.95, -1.5);
  s.closePath();
  const hole = new THREE.Path();
  hole.moveTo(0.35, 0.05);
  hole.lineTo(0.35, 0.78);
  hole.lineTo(-0.5, 0.05);
  hole.closePath();
  s.holes.push(hole);
  return s;
};

// Камера с углом 32° на расстоянии 9 видит 5,16 единицы по высоте и 2,9 по ширине кадра 9:16.
// Знак шириной 2,75 при повороте выходит за край, поэтому он уменьшен.
const FIT = 0.6;

const Mark: React.FC = () => {
  const frame = useCurrentFrame();
  const geometry = useMemo(() => {
    const g = new THREE.ExtrudeGeometry(mark(), { depth: 0.7, bevelEnabled: true, bevelSize: 0.05, bevelThickness: 0.05, bevelSegments: 4 });
    g.center();
    return g;
  }, []);
  const arrive = enter(frame, 0, 40);
  const turn = interpolate(frame, [0, 150], [-0.9, 0.7]);
  return (
    <group position={[0, -0.35 + (1 - arrive) * -1.2, 0]} rotation={[0.18, turn, 0]} scale={(0.6 + arrive * 0.4) * FIT}>
      <mesh geometry={geometry} castShadow>
        <meshStandardMaterial color={color.action} roughness={0.32} metalness={0.15} emissive={color.action} emissiveIntensity={0.12} />
      </mesh>
    </group>
  );
};

export const ThreeProbe: React.FC = () => {
  const { width, height } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: color.ground }}>
      <ThreeCanvas width={width} height={height} shadows camera={{ position: [0, 0.6, 9], fov: 32 }}>
        <ambientLight intensity={0.35} />
        <directionalLight position={[4, 6, 5]} intensity={2.6} castShadow shadow-mapSize={[2048, 2048]} />
        <pointLight position={[-4, 1, 3]} intensity={30} color={color.action} />
        <Mark />
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1.35, 0]} receiveShadow>
          <planeGeometry args={[30, 30]} />
          <shadowMaterial opacity={0.45} />
        </mesh>
      </ThreeCanvas>
      <div style={{ position: 'absolute', left: 80, top: 230, fontFamily: sans, fontWeight: 700, fontSize: 84, color: color.ink, letterSpacing: '-0.035em' }}>
        Настоящий объём
      </div>
    </AbsoluteFill>
  );
};
