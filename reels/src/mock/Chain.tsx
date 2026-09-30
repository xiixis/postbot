// Макет ролика «Одна фраза запустила всё»: цепная реакция. Четыре ключевых кадра:
// 0 шарик на доске с заголовком, 1 плитки CLAUDE падают, 2 тоннель из кадров, 3 шарик на кнопке.
import React, { useLayoutEffect, useMemo } from 'react';
import { ThreeCanvas } from '@remotion/three';
import { useThree } from '@react-three/fiber';
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/examples/jsm/geometries/RoundedBoxGeometry.js';
import { color, H, sans, safe, W } from '../lib/brand';
import { Mask } from '../lib/Mask';
import { useTextures } from '../lib/textures';
import { label, letter } from '../v3-keys/legend';

const GROUND = '#0E0F0C';
const LIME = new THREE.Color(color.lime);
const CLAUDE = new THREE.Color(color.claude);
const CREAM = new THREE.Color(color.cream);
const INK = new THREE.Color(color.graphite);

// Кадры наших роликов на карточках тоннеля.
const FRAMES = ['series/opening.jpg', 'v2-words/cover.jpg', 'series/opening-b.jpg', 'v4-desk/cover.jpg', 'series/mic.jpg', 'series/scene.jpg', 'v2-words/end.jpg', 'series/wave-dark.jpg'];

const Rig: React.FC<{ pos: [number, number, number]; aim: [number, number, number] }> = ({ pos, aim }) => {
  const cam = useThree((s) => s.camera);
  useLayoutEffect(() => {
    cam.position.set(...pos);
    cam.lookAt(...aim);
    cam.updateMatrixWorld();
  });
  return null;
};

const Ball: React.FC<{ position: [number, number, number] }> = ({ position }) => (
  <mesh position={position} castShadow>
    <sphereGeometry args={[0.28, 48, 48]} />
    <meshStandardMaterial color={LIME} roughness={0.25} metalness={0.15} emissive={LIME} emissiveIntensity={0.25} />
  </mesh>
);

// Наклонная доска: длинная коробка, по ней катится шарик.
const Plank: React.FC<{ from: [number, number, number]; to: [number, number, number] }> = ({ from, to }) => {
  const a = new THREE.Vector3(...from), b = new THREE.Vector3(...to);
  const mid = a.clone().add(b).multiplyScalar(0.5);
  const len = a.distanceTo(b);
  const dir = b.clone().sub(a).normalize();
  const quat = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(1, 0, 0), dir);
  return (
    <mesh position={mid} quaternion={quat} castShadow receiveShadow>
      <boxGeometry args={[len, 0.12, 1.0]} />
      <meshStandardMaterial color="#1B1D16" roughness={0.6} metalness={0.05} />
    </mesh>
  );
};

// Плитка с буквой: как клавиша, только выше и тоньше; падает поворотом вокруг нижнего ребра.
const TILE = { w: 0.9, h: 1.4, d: 0.12 };
const shape = new RoundedBoxGeometry(TILE.w, TILE.h, TILE.d, 4, 0.05);

const Tile: React.FC<{ x: number; z: number; map: THREE.Texture; fall: number }> = ({ x, z, map, fall }) => (
  <group position={[x, 0, z]} rotation={[0, 0, -fall * (Math.PI / 2 - 0.12)]}>
    <group position={[0, TILE.h / 2, 0]}>
      <mesh geometry={shape} castShadow receiveShadow>
        <meshStandardMaterial color={CLAUDE} roughness={0.5} metalness={0.05} emissive={CLAUDE} emissiveIntensity={0.18} />
      </mesh>
      <mesh position={[0, 0, TILE.d / 2 + 0.003]}>
        <planeGeometry args={[TILE.w * 0.78, TILE.w * 0.78]} />
        <meshBasicMaterial map={map} color={CREAM} transparent toneMapped={false} />
      </mesh>
    </group>
  </group>
);

const Card: React.FC<{ position: [number, number, number]; rotation: [number, number, number]; map: THREE.Texture }> = ({ position, rotation, map }) => (
  <group position={position} rotation={rotation}>
    <mesh position={[0, 0, -0.012]} castShadow>
      <boxGeometry args={[1.22, 2.2, 0.02]} />
      <meshStandardMaterial color="#1B1D16" roughness={0.6} />
    </mesh>
    <mesh position={[0, 0, -0.001]}>
      <planeGeometry args={[1.2, 2.18]} />
      <meshBasicMaterial color={LIME} toneMapped={false} />
    </mesh>
    <mesh>
      <planeGeometry args={[1.14, 2.12]} />
      <meshBasicMaterial map={map} toneMapped={false} />
    </mesh>
  </group>
);

// Кнопка: широкая клавиша с надписью.
const Button: React.FC<{ map: THREE.Texture; pressed: number; position: [number, number, number] }> = ({ map, pressed, position }) => {
  const g = useMemo(() => new RoundedBoxGeometry(3.2, 0.5, 1.3, 5, 0.12), []);
  return (
    <group position={[position[0], position[1] - pressed * 0.16, position[2]]}>
      <mesh geometry={g} castShadow receiveShadow>
        <meshStandardMaterial color={LIME} roughness={0.45} emissive={LIME} emissiveIntensity={0.3} />
      </mesh>
      <mesh position={[0, 0.254, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[2.9, 1.0]} />
        <meshBasicMaterial map={map} color={INK} transparent toneMapped={false} />
      </mesh>
    </group>
  );
};

const Scene: React.FC<{ stage: number; maps: THREE.Texture[] }> = ({ stage, maps }) => {
  const letters = useMemo(() => 'claude'.split('').map((ch) => letter(ch)), []);
  const follow = useMemo(() => label('Подписаться', 3.2), []);
  const done = useMemo(() => label('Вы подписаны', 3.2, true), []);
  const cams: Record<number, { pos: [number, number, number]; aim: [number, number, number] }> = {
    0: { pos: [-4.6, 3.6, 5.2], aim: [-4.2, 2.6, 0] },
    1: { pos: [-0.2, 3.0, 9.0], aim: [1.6, 0.7, 0] },
    2: { pos: [0, 0.8, 2.6], aim: [0, 0.8, -6] },
    3: { pos: [3.0, 3.8, 7.6], aim: [3.6, 0.2, 0] },
  };
  const cam = cams[Math.min(stage, 3)];
  return (
    <>
      <Rig pos={cam.pos} aim={cam.aim} />
      <ambientLight intensity={0.55} color="#E4E8D8" />
      <directionalLight position={[-6, 10, 6]} intensity={2.4} color="#FFF1DC" castShadow shadow-mapSize={[2048, 2048]} shadow-bias={-0.0004}
        shadow-camera-left={-14} shadow-camera-right={14} shadow-camera-top={14} shadow-camera-bottom={-14} shadow-camera-far={50} />
      <directionalLight position={[8, 4, -8]} intensity={0.5} color={color.lime} />
      <pointLight position={[-4.2, 3.4, 1.2]} intensity={6} distance={6} decay={1.3} color={color.lime} />
      {/* стол */}
      <mesh position={[0, -0.05, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[80, 80]} />
        <meshStandardMaterial color="#111310" roughness={0.9} />
      </mesh>
      {/* полка и доска */}
      <Plank from={[-6.4, 3.0, 0]} to={[-4.0, 2.9, 0]} />
      <Plank from={[-4.0, 2.85, 0]} to={[-1.4, 0.12, 0]} />
      {stage === 0 && <Ball position={[-4.3, 3.24, 0]} />}
      {stage === 1 && <Ball position={[-1.55, 0.4, 0]} />}
      {/* плитки CLAUDE */}
      {stage <= 1 && letters.map((m, i) => <Tile key={i} x={-0.6 + i * 1.1} z={0} map={m} fall={stage === 1 ? Math.max(0, Math.min(1, (2.5 - i) / 1.2)) : 0} />)}
      {/* тоннель из кадров */}
      {stage === 2 && new Array(28).fill(0).map((_, i) => {
        const a = (i / 28) * Math.PI * 2 * 3.5;
        const r = 2.1;
        const z = -1 - i * 0.55;
        return <Card key={i} position={[Math.cos(a) * r, 0.8 + Math.sin(a) * r, z]} rotation={[0, 0, a + Math.PI / 2]} map={maps[i % maps.length]} />;
      })}
      {/* кнопка и шарик на ней */}
      {stage === 3 && (
        <>
          <Button map={done} pressed={1} position={[3.6, 0.25, 0]} />
          <Ball position={[3.6, 0.72, -0.1]} />
        </>
      )}
      {stage === 3 && <Plank from={[6.6, 3.2, -1.6]} to={[4.4, 1.0, -0.6]} />}
      {stage === 1 && <Button map={follow} pressed={0} position={[7.2, 0.25, 0]} />}
    </>
  );
};

export const MockChain: React.FC = () => {
  const stage = useCurrentFrame();
  const maps = useTextures(FRAMES.map((f) => staticFile(f)));
  return (
    <AbsoluteFill style={{ background: GROUND }}>
      {maps && (
        <ThreeCanvas width={W} height={H} flat shadows camera={{ fov: 42, near: 0.1, far: 80 }}>
          <color attach="background" args={[GROUND]} />
          <fog attach="fog" args={[GROUND, 10, 30]} />
          <Scene stage={stage} maps={maps} />
        </ThreeCanvas>
      )}
      <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(14,15,12,0.85) 0%, rgba(14,15,12,0.45) 26%, rgba(14,15,12,0) 45%)' }} />
      {stage === 0 && (
        <div style={{ position: 'absolute', left: safe.left, top: safe.top }}>
          <Mask px={128} color={color.lime}>Одна фраза</Mask>
          <Mask px={128} color={color.cream}>запустила всё</Mask>
        </div>
      )}
      {stage === 1 && <div style={{ position: 'absolute', left: safe.left, top: 1330, fontFamily: sans, fontWeight: 700, fontSize: 56, color: color.cream }}>Буквы встали <span style={{ color: color.lime }}>сами</span>.</div>}
      {stage === 2 && <div style={{ position: 'absolute', left: safe.left, top: 1330, fontFamily: sans, fontWeight: 700, fontSize: 56, color: color.cream }}>Четыреста пятьдесят <span style={{ color: color.lime }}>кадров</span>.</div>}
      {stage === 3 && (
        <>
          <div style={{ position: 'absolute', left: safe.left, top: safe.top, display: 'flex', alignItems: 'center', gap: 20 }}>
            <Img src={staticFile('brand/logo.png')} style={{ width: 72, height: 72 }} />
            <div style={{ fontFamily: sans, fontWeight: 800, fontSize: 54, color: color.cream }}>4xTube</div>
          </div>
          <div style={{ position: 'absolute', left: safe.left, top: 1330, width: 820, fontFamily: sans, fontWeight: 700, fontSize: 56, color: color.lime, lineHeight: 1.14 }}>Что запустить следующим?</div>
        </>
      )}
    </AbsoluteFill>
  );
};
