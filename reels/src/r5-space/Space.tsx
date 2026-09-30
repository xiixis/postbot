// Серия 2, ролик 5: «Одна фраза, и Claude строит объём».
//
// Тезис: показ умения threejs. Семь карточек с картинками кота стоят кольцом в настоящем
// пространстве, камера идёт сквозь кольцо и облетает его одним планом, в конце карточки
// слетаются в стену со знаком канала. Характер дорогой: одна кривая, туман, три источника
// света, тени на полу. Текст вёрсткой поверх холста.
import React, { useLayoutEffect, useMemo } from 'react';
import { ThreeCanvas } from '@remotion/three';
import { useLoader, useThree } from '@react-three/fiber';
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame } from 'remotion';
import * as THREE from 'three';
import { hit } from '../lib/beat';
import { color, curve, enter, glide, H, leave, mix, W } from '../lib/brand';
import { Captions, type Word } from '../series/Captions';
import { b, BAR, BEAT, LENGTH, T } from '../series/grid';
import { Cta, Headline, Prompt, promptSounds, Save, Show } from '../series/parts';
import words from '../series/words/r5.json';

const GROUND = '#0D0E0B';
export const PROMPT = 'Расставь картинки кота в объёме, поставь свет и облети их камерой';
export const SKILLS = ['threejs', 'motion-design'];

// Карточки: семь картинок кота из наших роликов. Все режутся под 3:4.
// Порядок такой, чтобы похожие картинки не шли подряд.
const CARDS = ['series/opening.jpg', 'v2-words/cover.jpg', 'series/opening-b.jpg', 'series/wave-dark.jpg', 'series/mic.jpg', 'series/scene.jpg', 'v2-words/end.jpg', 'v4-desk/cover.jpg'];
// Карточки стоят винтом вокруг оси: восемь ступеней по кругу и по высоте. В вертикальном кадре
// кольцо целиком не помещается, а винт читается: карточки видны и над камерой, и под ней.
const RING = 3.3;                                  // радиус винта
const STEP = 1.25;                                 // подъём на карточку
const N = 8;
const spiral = (i: number) => ({ angle: (i / N) * Math.PI * 2, y: (i - (N - 1) / 2) * STEP });
const CARD = { w: 1.7, h: 2.27 };                  // 3:4
const FOV = 40;

const LIME = new THREE.Color(color.lime);

// ── Камера ────────────────────────────────────────────────────────────────────────────────
// Один план: внутри кольца → сквозь просвет наружу → облёт → стена лицом к камере.
type Pose = { pos: THREE.Vector3; aim: THREE.Vector3 };
const v = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);
const ring = (angle: number, r = RING, y = 0) => v(Math.sin(angle) * r, y, Math.cos(angle) * r);

const lerpPose = (a: Pose, c: Pose, t: number): Pose => ({ pos: a.pos.clone().lerp(c.pos, t), aim: a.aim.clone().lerp(c.aim, t) });

// Стена: три на три перед камерой в её конечной позе, знак канала в середине.
const WALL_Z = 2.0;
const WALL_CAM: Pose = { pos: v(0, 0.3, WALL_Z + 15.6), aim: v(0, 0.3, WALL_Z) };
const WALL_ORDER = [0, 1, 2, 3, 5, 6, 7, 8];          // карточки обходят середину
const wallSlot = (slot: number) => {
  const col = slot % 3, row = Math.floor(slot / 3);
  return v((col - 1) * (CARD.w + 0.2), (1 - row) * (CARD.h + 0.2) + 0.3, WALL_Z);
};

export const camera = (frame: number): Pose => {
  // камера стоит на оси винта и смотрит на карточку; на показе поднимается по оси и
  // поворачивается вслед за винтом, карточки проходят перед ней одна за другой
  const along = (t: number, lead = 0): Pose => {
    const a = spiral(0).angle + t * (spiral(N - 1).angle - spiral(0).angle) + lead;
    const y = spiral(0).y + t * (spiral(N - 1).y - spiral(0).y);
    return { pos: v(-Math.sin(a) * 0.5, y + 0.15, -Math.cos(a) * 0.5), aim: ring(a, RING, y + 0.25) };
  };
  const drift = Math.sin(frame / 90) * 0.04;
  let p = along(0, drift);
  const t = enter(frame, T.show - 6, 4 * BAR - 30, curve.calm);
  if (t > 0) p = along(t);
  p = lerpPose(p, WALL_CAM, enter(frame, T.show + 4 * BAR - 8, 44, curve.both));
  return p;
};

const Rig: React.FC<{ frame: number }> = ({ frame }) => {
  const cam = useThree((s) => s.camera);
  const pose = camera(frame);
  useLayoutEffect(() => {
    cam.position.copy(pose.pos);
    cam.up.set(0, 1, 0);
    cam.lookAt(pose.aim);
    cam.updateMatrixWorld();
  });
  return null;
};

// ── Карточки ──────────────────────────────────────────────────────────────────────────────
// Место карточки: на кольце лицом внутрь; на восьмом такте она улетает в стену.
const cardPose = (i: number, frame: number) => {
  const { angle, y } = spiral(i);
  const onRing = ring(angle, RING, y);
  const faceIn = new THREE.Quaternion().setFromEuler(new THREE.Euler(0, angle + Math.PI, 0));
  const flyAt = T.show + 4 * BAR + i * 4;
  const u = enter(frame, flyAt, 36, curve.both);
  const slot = wallSlot(WALL_ORDER[i]);
  const faceCam = new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 0, 0));
  const pos = onRing.clone().lerp(slot, u);
  pos.y += Math.sin(Math.PI * u) * 1.2;
  const quat = faceIn.clone().slerp(faceCam, u);
  // на ударе карточка едва заметно кивает камере
  const beatAt = Math.floor(frame / BEAT) * BEAT;
  const nod = frame >= T.show && frame < T.show + 4 * BAR ? hit(frame, beatAt, 14) * 0.06 * (i % 2 ? 1 : -1) : 0;
  quat.multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(0, nod, 0)));
  return { pos, quat, u };
};

const Card: React.FC<{ i: number; map: THREE.Texture; frame: number }> = ({ i, map, frame }) => {
  const { pos, quat } = cardPose(i, frame);
  return (
    <group position={pos} quaternion={quat}>
      {/* картинка и рамка с обеих сторон, поэтому кольцо читается и снаружи; подложка даёт толщину */}
      <mesh position={[0, 0, -0.0085]} castShadow receiveShadow>
        <boxGeometry args={[CARD.w + 0.08, CARD.h + 0.08, 0.009]} />
        <meshStandardMaterial color="#1B1D16" roughness={0.65} metalness={0.05} />
      </mesh>
      {[0, -0.017].map((z) => (
        <group key={z} position={[0, 0, z]} rotation={[0, z < 0 ? Math.PI : 0, 0]}>
          <mesh position={[0, 0, -0.002]}>
            <planeGeometry args={[CARD.w + 0.06, CARD.h + 0.06]} />
            <meshBasicMaterial color={LIME} toneMapped={false} />
          </mesh>
          <mesh position={[0, 0, 0.002]} castShadow>
            <planeGeometry args={[CARD.w, CARD.h]} />
            <meshStandardMaterial map={map} roughness={0.85} metalness={0} />
          </mesh>
        </group>
      ))}
    </group>
  );
};

// Знак канала: восьмая карточка стены. Появляется, когда первая карточка села.
const Mark: React.FC<{ map: THREE.Texture; frame: number }> = ({ map, frame }) => {
  const u = enter(frame, T.show + 4 * BAR + 26, 24, curve.out);
  const slot = wallSlot(4);
  return (
    <group position={[slot.x, slot.y - (1 - u) * 1.2, slot.z]} scale={0.6 + 0.4 * u}>
      <mesh position={[0, 0, -0.012]} castShadow>
        <boxGeometry args={[CARD.w + 0.1, CARD.h + 0.1, 0.02]} />
        <meshStandardMaterial color={LIME} roughness={0.5} emissive={LIME} emissiveIntensity={0.35 * u} />
      </mesh>
      <mesh position={[0, 0, 0.004]}>
        <planeGeometry args={[CARD.w * 0.55, CARD.w * 0.55]} />
        <meshBasicMaterial map={map} transparent toneMapped={false} opacity={u} />
      </mesh>
    </group>
  );
};

const Scene: React.FC<{ frame: number }> = ({ frame }) => {
  const maps = useLoader(THREE.TextureLoader, CARDS.map((c) => staticFile(c)));
  const logo = useLoader(THREE.TextureLoader, staticFile('brand/logo.png'));
  useMemo(() => {
    maps.forEach((m) => {
      m.colorSpace = THREE.SRGBColorSpace;
      m.anisotropy = 8;
      // картинка режется под 3:4 по центру, ничего не тянется
      const ratio = m.image.width / m.image.height / (CARD.w / CARD.h);
      if (ratio < 1) {
        m.repeat.set(1, ratio);
        m.offset.set(0, (1 - ratio) / 2);
      } else {
        m.repeat.set(1 / ratio, 1);
        m.offset.set((1 - 1 / ratio) / 2, 0);
      }
    });
    logo.colorSpace = THREE.SRGBColorSpace;
  }, [maps, logo]);
  const beatAt = Math.floor(frame / BEAT) * BEAT;
  const pulse = hit(frame, beatAt, 12);
  return (
    <>
      <ambientLight intensity={0.6} color="#E9E6DA" />
      <directionalLight
        position={[6, 9, 8]} intensity={2.8} color="#FFF1DC" castShadow shadow-mapSize={[2048, 2048]} shadow-bias={-0.0005}
        shadow-camera-left={-12} shadow-camera-right={12} shadow-camera-top={12} shadow-camera-bottom={-12} shadow-camera-far={40}
      />
      <pointLight position={[0, 0, 0]} intensity={3 + pulse * 3} distance={12} decay={1.4} color={color.lime} />
      <directionalLight position={[-8, 3, -6]} intensity={0.35} color={color.lime} />
      {maps.map((m, i) => <Card key={CARDS[i]} i={i} map={m} frame={frame} />)}
      <Mark map={logo} frame={frame} />
      <mesh position={[0, spiral(0).y - CARD.h / 2 - 0.3, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[80, 80]} />
        <shadowMaterial opacity={0.5} />
      </mesh>
    </>
  );
};

// Крючок и промпт лежат поверх сцены, поэтому у них своя тёмная подложка сверху.
const Scrim: React.FC<{ strength: number }> = ({ strength }) => (
  <AbsoluteFill style={{ background: `linear-gradient(180deg, rgba(13,14,11,${0.92 * strength}) 0%, rgba(13,14,11,${0.7 * strength}) 40%, rgba(13,14,11,${0.15 * strength}) 70%, rgba(13,14,11,0) 100%)` }} />
);

const SOUNDS: [number, string, number][] = [
  ...promptSounds(T.prompt),
  [T.show, 'whoosh.wav', 0.35],
  [T.show + 4 * BAR, 'whoosh.wav', 0.3],
  [T.press, 'click.wav', 0.5],
];

export type SpaceProps = { music: boolean };

export const Space: React.FC<SpaceProps> = ({ music }) => {
  const frame = useCurrentFrame();
  // подложка: плотная под промптом, прозрачная на показе, снова плотная под «сохрани»
  const scrim = frame < T.show ? 1 - enter(frame, T.show - 20, 20) : frame >= T.save ? enter(frame, T.save - 10, 14) : 0;
  return (
    <AbsoluteFill style={{ background: GROUND }}>
      <ThreeCanvas width={W} height={H} flat shadows camera={{ fov: FOV, near: 0.1, far: 120 }}>
        <color attach="background" args={[GROUND]} />
        <fog attach="fog" args={[GROUND, 14, 38]} />
        <Rig frame={frame} />
        <Scene frame={frame} />
      </ThreeCanvas>
      <Scrim strength={Math.max(scrim, 0.35)} />
      {frame >= T.save && <AbsoluteFill style={{ background: GROUND, opacity: 0.72 * enter(frame, T.save - 10, 14) }} />}
      <Sequence from={T.hook} durationInFrames={BAR + 2}>
        <Headline lines={[<span style={{ color: color.lime }}>Одна фраза</span>, 'и Claude', 'строит объём']} px={118} />
      </Sequence>
      <Sequence from={T.prompt} durationInFrames={T.show - T.prompt}><Prompt text={PROMPT} skills={SKILLS} hold={T.show - T.prompt} /></Sequence>
      <Show><></></Show>
      <Sequence from={T.save} durationInFrames={BAR}><Save text={PROMPT} skills={SKILLS} /></Sequence>
      <Sequence from={T.cta}><Cta question="Что построить объёмным в следующий раз?" cat="series/wave-dark.jpg" catTop={840} catWidth={1000} /></Sequence>
      <Captions words={words as Word[]} hide={[[0, BAR], [T.save, LENGTH]]} />
      {music && <Audio src={staticFile('series/r5.m4a')} volume={0.92} />}
      {SOUNDS.map(([from, name, volume], i) => (
        <Sequence key={i} from={from} layout="none"><Audio src={staticFile(`sfx/${name}`)} volume={volume} /></Sequence>
      ))}
    </AbsoluteFill>
  );
};
