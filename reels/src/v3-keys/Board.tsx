// Трёхмерная часть версии «Клавиши»: клавиатура, свет и клавиши, которые висят перед зрителем.
import React, { useLayoutEffect, useMemo } from 'react';
import { useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/examples/jsm/geometries/RoundedBoxGeometry.js';
import { color } from '../lib/brand';
import { DEPTH, ENTER, KEYS, WIDTH } from './layout';
import { halo, INSET, label, legend, letter } from './legend';
import { breath, button, BUTTON, type Cam, hud, REST_Y, state, T, word } from './motion';

const TALL = 0.42;                    // высота клавиши
const GAP = 0.1;                      // зазор между клавишами
const TRAVEL = 0.17;                  // ход клавиши при нажатии

const tone = (hex: string) => new THREE.Color(hex);
const BODY = tone('#23251D');
const MOD = tone('#191A14');
const CASE = '#0B0C09';
const CREAM = tone(color.cream);
const LIME = tone(color.lime);
const INK = tone(color.graphite);
const CLAUDE = tone(color.claude);
const between = (a: THREE.Color, c: THREE.Color, t: number) => a.clone().lerp(c, Math.min(1, Math.max(0, t)));

// Клавиша сужается кверху: верхняя грань меньше основания на INSET.
const shapes = new Map<string, THREE.BufferGeometry>();
const shape = (w: number, d: number) => {
  const id = `${w}:${d}`;
  const ready = shapes.get(id);
  if (ready) return ready;
  const g = new RoundedBoxGeometry(w - GAP, TALL, d - GAP, 5, 0.085);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const t = (p.getY(i) + TALL / 2) / TALL;
    p.setX(i, p.getX(i) * (1 - ((INSET - GAP) * t) / (w - GAP)));
    p.setZ(i, p.getZ(i) * (1 - ((INSET - GAP) * t) / (d - GAP)));
  }
  shapes.set(id, g);
  return g;
};

type CapProps = {
  w: number; d?: number;
  position: THREE.Vector3 | [number, number, number];
  quaternion?: THREE.Quaternion;
  scale?: number;
  body: THREE.Color;
  ink: THREE.Color;
  map: THREE.Texture;
  over?: THREE.Texture;               // вторая надпись поверх первой
  mix?: number;                       // насколько вторая надпись проявлена
  shine?: number;                     // собственное свечение клавиши
  rim?: number;                       // лаймовая кайма вокруг клавиши
};

const Cap: React.FC<CapProps> = ({ w, d = 1, position, quaternion, scale = 1, body, ink, map, over, mix = 0, shine = 0, rim = 0 }) => (
  <group position={position} quaternion={quaternion} scale={scale}>
    {rim > 0 && (
      <mesh position={[0, -TALL / 2 + 0.02, 0]}>
        <boxGeometry args={[w + 0.06, 0.04, d + 0.06]} />
        <meshBasicMaterial color={LIME} toneMapped={false} />
      </mesh>
    )}
    <mesh geometry={shape(w, d)} castShadow receiveShadow>
      <meshStandardMaterial color={body} roughness={0.5} metalness={0.08} emissive={body} emissiveIntensity={shine} />
    </mesh>
    <mesh position={[0, TALL / 2 + 0.004, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      <planeGeometry args={[w - INSET, d - INSET]} />
      <meshBasicMaterial map={map} color={ink} transparent opacity={1 - mix} depthWrite={false} toneMapped={false} />
    </mesh>
    {over && (
      <mesh position={[0, TALL / 2 + 0.006, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[d - INSET, d - INSET]} />
        <meshBasicMaterial map={over} color={ink} transparent opacity={mix} depthWrite={false} toneMapped={false} />
      </mesh>
    )}
  </group>
);

export const Rig: React.FC<{ cam: Cam }> = ({ cam }) => {
  const camera = useThree((s) => s.camera);
  useLayoutEffect(() => {
    camera.position.copy(cam.pos);
    camera.quaternion.copy(cam.quat);
    camera.updateMatrixWorld();
  });
  return null;
};

export const Lights: React.FC<{ frame: number; cam: Cam }> = ({ frame, cam }) => {
  const enter = Math.max(0, 1 - Math.abs(frame - T.enter) / 26);
  // свет для клавиш, висящих перед зрителем: до клавиатуры он не достаёт
  const front = Math.min(1, Math.max(0, (frame - (T.rest - 6)) / 30));
  return (
    <>
      <pointLight position={hud(cam, 380, 380, 5.6)} intensity={front * 24} distance={7.5} decay={1.2} color="#FFF3DE" />
      <ambientLight intensity={0.5} color="#DDE3CF" />
      <directionalLight
        position={[-8, 14, 6]} intensity={2.4} castShadow
        shadow-mapSize={[2048, 2048]} shadow-bias={-0.0004}
        shadow-camera-left={-14} shadow-camera-right={14} shadow-camera-top={14} shadow-camera-bottom={-14} shadow-camera-far={50}
      />
      <directionalLight position={[10, 5, -9]} intensity={0.7} color={color.lime} />
      <pointLight position={[ENTER.x, 1.5, ENTER.z + 0.4]} intensity={9 + enter * 40} distance={9} decay={1.6} color={color.lime} />
    </>
  );
};

export const Board: React.FC<{ frame: number; cam: Cam }> = ({ frame, cam }) => {
  const maps = useMemo(() => ({
    keys: new Map(KEYS.map((k) => [k.id, legend(k)])),
    letters: new Map('claude'.split('').map((ch) => [ch, letter(ch)])),
    follow: label('Подписаться', BUTTON.units),
    done: label('Вы подписаны', BUTTON.units, true),
    halo: halo(),
  }), []);
  const caseShape = useMemo(() => new RoundedBoxGeometry(WIDTH + 0.7, 0.5, DEPTH + 0.7, 5, 0.22), []);

  const flying = word(frame, cam);
  const lifted = new Map(flying.map((f) => [f.key.id, f]));
  const base = breath(frame);
  const knob = button(frame, cam);

  return (
    <>
      {/* свет клавиатуры на столе */}
      <mesh position={[0, -0.49, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[WIDTH * 2.1, DEPTH * 3.4]} />
        <meshBasicMaterial map={maps.halo} color={LIME} transparent opacity={0.2 + base * 0.5} depthWrite={false} toneMapped={false} />
      </mesh>
      <mesh position={[0, -0.5, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[200, 200]} />
        <shadowMaterial opacity={0.5} />
      </mesh>
      <mesh geometry={caseShape} position={[0, -0.25, 0]} receiveShadow castShadow>
        <meshStandardMaterial color={CASE} roughness={0.8} metalness={0.1} />
      </mesh>

      {KEYS.map((k) => {
        const s = state(frame, k);
        const away = lifted.get(k.id);
        const gone = away ? away.u : 0;
        const enter = k.kind === 'enter';
        const glow = Math.min(1, base + s.glow);
        return (
          <group key={k.id} position={[k.x, 0, k.z]}>
            <mesh position={[0, 0.012, 0]} rotation={[-Math.PI / 2, 0, 0]}>
              <planeGeometry args={[k.w + 0.02, 1.02]} />
              <meshBasicMaterial color={between(tone('#000000'), LIME, glow * (1 - gone * 0.6))} toneMapped={false} />
            </mesh>
            {s.flash > 0.02 && gone < 0.02 && (
              <mesh position={[0, TALL + 0.16, 0]} rotation={[-Math.PI / 2, 0, 0]}>
                <planeGeometry args={[k.w + 1.9, 2.9]} />
                <meshBasicMaterial map={maps.halo} color={LIME} transparent opacity={s.flash * 0.42} depthWrite={false} blending={THREE.AdditiveBlending} toneMapped={false} />
              </mesh>
            )}
            {gone < 0.001 && (
              <Cap
                w={k.w} position={[0, REST_Y - s.press * TRAVEL, 0]}
                body={enter ? LIME : between(k.kind === 'mod' || k.kind === 'space' ? MOD : BODY, LIME, s.glow * 0.1 + s.flash * 0.3)}
                ink={enter ? INK : between(CREAM, LIME, s.glow * 1.4)}
                map={maps.keys.get(k.id) as THREE.Texture}
                shine={enter ? 0.22 + s.flash * 0.5 : s.flash * 0.5}
              />
            )}
          </group>
        );
      })}

      {/* клавиша перед зрителем нажимается от него: ход не виден, поэтому она ещё и сжимается */}
      {flying.filter((f) => f.u > 0.001).map((f) => {
        const push = new THREE.Vector3(0, -f.press * TRAVEL * f.scale, 0).applyQuaternion(f.quat);
        return (
          <Cap
            key={f.ch} w={1} position={f.pos.clone().add(push)} quaternion={f.quat} scale={f.scale * (1 - 0.12 * f.press)}
            body={between(BODY, CLAUDE, f.u * 1.6)} ink={between(CREAM, INK, f.u * 1.6)}
            map={maps.keys.get(f.key.id) as THREE.Texture} over={maps.letters.get(f.ch)} mix={Math.min(1, f.u * 2)}
            shine={0.3 * f.u + f.glow * 0.4}
          />
        );
      })}

      {frame >= T.cta + 2 && (
        <Cap
          w={BUTTON.units} d={1.3}
          position={knob.pos.clone().add(new THREE.Vector3(0, -knob.press * TRAVEL * knob.scale, 0).applyQuaternion(knob.quat))}
          quaternion={knob.quat} scale={knob.scale * (1 - 0.06 * knob.press)}
          body={knob.done ? tone('#1B1D16') : LIME} ink={knob.done ? LIME : INK} rim={knob.done ? 1 : 0}
          map={knob.done ? maps.done : maps.follow}
          shine={knob.done ? 0 : 0.85}
        />
      )}
    </>
  );
};
