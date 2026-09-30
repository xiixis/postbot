// Ролик «Одна фраза запустила всё». 26,4 с, 1080×1920, музыка 100 ударов в минуту.
//
// Тезис: цепная реакция из вещей монтажа, один план без склеек. Лаймовый шарик срывается с
// полки, роняет плитки CLAUDE, последняя бьёт по рычагу, карточка с кадром взлетает ко входу
// в тоннель из кадров наших роликов, камера летит сквозь него, все кадры всасываются в
// телефон, на котором начинается настоящий ролик, а шарик выпадает из трубы на кнопку
// «Подписаться». В финале камера дугой возвращается к полке, куда прикатывается новый шарик:
// последний кадр повторяет первый, и ролик замыкается в петлю.
import React, { useLayoutEffect, useMemo, useRef } from 'react';
import { ThreeCanvas, useOffthreadVideoTexture } from '@remotion/three';
import { useThree } from '@react-three/fiber';
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame, useRemotionEnvironment } from 'remotion';
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/examples/jsm/geometries/RoundedBoxGeometry.js';
import { hit } from '../lib/beat';
import { color, enter, H, leave, safe, sans, W } from '../lib/brand';
import { Mask } from '../lib/Mask';
import { useTextures } from '../lib/textures';
import { Captions, type Word } from '../series/Captions';
import { label, letter } from '../v3-keys/legend';
import { ball, ball2, BAR, BEAT, BUTTON, camera, card, cardLands, cardLaunch, HOLE, lever, LEVER, LENGTH, PHONE, PIPE, PLANK, phoneOn, pressed, SHELF, T, TILE, tileFall, tileLands, TILES, TUNNEL, tunnelCard } from './motion';
import words from '../series/words/r7.json';

const GROUND = '#0E0F0C';
const LIME = new THREE.Color(color.lime);
const CLAUDE = new THREE.Color(color.claude);
const CREAM = new THREE.Color(color.cream);
const INK = new THREE.Color(color.graphite);
const WOOD = '#1B1D16';
const METAL = '#2A2C22';

const FRAMES = ['series/opening.jpg', 'v2-words/cover.jpg', 'series/opening-b.jpg', 'v4-desk/cover.jpg', 'series/mic.jpg', 'series/scene.jpg', 'v2-words/end.jpg', 'series/wave-dark.jpg'];

const Rig: React.FC<{ frame: number }> = ({ frame }) => {
  const cam = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  const { pos, aim, fov } = camera(frame);
  useLayoutEffect(() => {
    cam.position.copy(pos);
    cam.lookAt(aim);
    cam.fov = fov;
    cam.updateProjectionMatrix();
    cam.updateMatrixWorld();
  });
  return null;
};

const Plank: React.FC<{ from: THREE.Vector3; to: THREE.Vector3; width?: number }> = ({ from, to, width = 1.0 }) => {
  const mid = from.clone().add(to).multiplyScalar(0.5);
  const dir = to.clone().sub(from).normalize();
  const quat = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(1, 0, 0), dir);
  return (
    <mesh position={mid} quaternion={quat} castShadow receiveShadow>
      <boxGeometry args={[from.distanceTo(to), 0.12, width]} />
      <meshStandardMaterial color={WOOD} roughness={0.6} metalness={0.05} />
    </mesh>
  );
};

const Ball: React.FC<{ pos: THREE.Vector3; spin: number }> = ({ pos, spin }) => (
  <mesh position={pos} rotation={[0, 0, -spin]} castShadow>
    <sphereGeometry args={[0.28, 48, 48]} />
    <meshStandardMaterial color={LIME} roughness={0.25} metalness={0.15} emissive={LIME} emissiveIntensity={0.25} />
  </mesh>
);

const tileShape = new RoundedBoxGeometry(TILE.w, TILE.h, TILE.d, 4, 0.05);

const Tile: React.FC<{ i: number; map: THREE.Texture; frame: number }> = ({ i, map, frame }) => {
  const fall = tileFall(i, frame);
  const glow = hit(frame, tileLands(i), 12);
  return (
    <group position={[TILE.x0 + i * TILE.step, 0, 0]} rotation={[0, 0, -fall * (Math.PI / 2 - 0.14)]}>
      <group position={[0, TILE.h / 2, 0]}>
        <mesh geometry={tileShape} castShadow receiveShadow>
          <meshStandardMaterial color={CLAUDE} roughness={0.5} metalness={0.05} emissive={CLAUDE} emissiveIntensity={0.15 + glow * 0.5} />
        </mesh>
        <mesh position={[0, 0, TILE.d / 2 + 0.003]}>
          <planeGeometry args={[TILE.w * 0.78, TILE.w * 0.78]} />
          <meshBasicMaterial map={map} color={CREAM} transparent toneMapped={false} />
        </mesh>
      </group>
    </group>
  );
};

const Card: React.FC<{ pos: THREE.Vector3; quat: THREE.Quaternion; scale?: number; map: THREE.Texture }> = ({ pos, quat, scale = 1, map }) => (
  <group position={pos} quaternion={quat} scale={scale}>
    <mesh position={[0, 0, -0.012]} castShadow>
      <boxGeometry args={[1.22, 2.2, 0.02]} />
      <meshStandardMaterial color={WOOD} roughness={0.6} />
    </mesh>
    <mesh position={[0, 0, -0.001]}>
      <planeGeometry args={[1.2, 2.18]} />
      <meshBasicMaterial color={LIME} toneMapped={false} side={THREE.DoubleSide} />
    </mesh>
    <mesh>
      <planeGeometry args={[1.14, 2.12]} />
      <meshBasicMaterial map={map} toneMapped={false} side={THREE.DoubleSide} />
    </mesh>
  </group>
);

// Экран телефона: при рендере на нём идёт настоящий ролик, в студии стоит кадр обложки.
// Материал собирается руками: смена текстуры требует пересборки шейдера (needsUpdate).
// Кадр видео приходит позже, чем ThreeCanvas отрисовал сцену по смене номера кадра,
// поэтому после подмены карты сцена рисуется ещё раз через advance().
const useScreen = (map: THREE.Texture | null, on: number) => {
  const mat = useMemo(() => new THREE.MeshBasicMaterial({ toneMapped: false }), []);
  const advance = useThree((s) => s.advance);
  const { isRendering } = useRemotionEnvironment();
  const last = useRef<THREE.Texture | null>(null);
  useLayoutEffect(() => {
    if (map) map.colorSpace = THREE.SRGBColorSpace;
    mat.map = map;
    mat.color.setRGB(on, on, on);
    mat.needsUpdate = true;
    if (isRendering && map && map !== last.current) advance(performance.now());
    last.current = map;
  });
  return mat;
};

const VideoScreen: React.FC<{ on: number }> = ({ on }) => {
  const map = useOffthreadVideoTexture({ src: staticFile('mock/reel.mp4'), toneMapped: false });
  const mat = useScreen(map, on);
  return <mesh position={[0, 0, 0.072]} material={mat}><planeGeometry args={[1.38, 2.45]} /></mesh>;
};

const StillScreen: React.FC<{ on: number; map: THREE.Texture }> = ({ on, map }) => {
  const mat = useScreen(map, on);
  return <mesh position={[0, 0, 0.072]} material={mat}><planeGeometry args={[1.38, 2.45]} /></mesh>;
};

const Phone: React.FC<{ frame: number; fallback: THREE.Texture }> = ({ frame, fallback }) => {
  const { isRendering } = useRemotionEnvironment();
  const on = phoneOn(frame);
  const body = useMemo(() => new RoundedBoxGeometry(1.5, 2.9, 0.14, 5, 0.16), []);
  return (
    <group position={PHONE} rotation={[-0.1, 0.16, 0]}>
      <mesh geometry={body} castShadow receiveShadow>
        <meshStandardMaterial color="#15171A" roughness={0.35} metalness={0.4} />
      </mesh>
      {isRendering ? (
        <Sequence from={T.phone} layout="none"><VideoScreen on={on} /></Sequence>
      ) : <StillScreen on={on} map={fallback} />}
      <pointLight position={[0, 0.4, 1.2]} intensity={on * 6} distance={5} decay={1.4} color="#DDE6C8" />
    </group>
  );
};

const Pipe: React.FC = () => {
  const g = useMemo(() => new THREE.TubeGeometry(new THREE.CatmullRomCurve3(PIPE), 32, 0.36, 18, false), []);
  return (
    <mesh geometry={g} castShadow receiveShadow>
      <meshStandardMaterial color={METAL} roughness={0.55} metalness={0.2} side={THREE.DoubleSide} />
    </mesh>
  );
};

const Button: React.FC<{ frame: number; follow: THREE.Texture; done: THREE.Texture }> = ({ frame, follow, done }) => {
  const g = useMemo(() => new RoundedBoxGeometry(3.2, 0.5, 1.3, 5, 0.12), []);
  const p = pressed(frame);
  const isDone = frame >= T.press + 2;
  const flash = hit(frame, T.press + 2, 14);
  return (
    <group position={[BUTTON.x, BUTTON.y - p * 0.16, BUTTON.z]} rotation={[0, 0.3, 0]}>
      <mesh geometry={g} castShadow receiveShadow>
        <meshStandardMaterial color={isDone ? WOOD : LIME} roughness={0.45} emissive={LIME} emissiveIntensity={isDone ? flash * 0.5 : 0.3} />
      </mesh>
      {isDone && (
        <mesh position={[0, -0.24, 0]}>
          <boxGeometry args={[3.3, 0.04, 1.4]} />
          <meshBasicMaterial color={LIME} toneMapped={false} />
        </mesh>
      )}
      <mesh position={[0, 0.254, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[2.9, 1.0]} />
        <meshBasicMaterial map={isDone ? done : follow} color={isDone ? LIME : INK} transparent toneMapped={false} />
      </mesh>
    </group>
  );
};

const Scene: React.FC<{ frame: number; maps: THREE.Texture[] }> = ({ frame, maps }) => {
  const letters = useMemo(() => 'claude'.split('').map((ch) => letter(ch)), []);
  const follow = useMemo(() => label('Подписаться', 3.0), []);
  const done = useMemo(() => label('Подписаны', 3.0, true), []);
  const bl = ball(frame);
  const b2 = ball2(frame);
  const lv = lever(frame);
  const cd = card(frame);
  const cam = camera(frame);
  const glow = b2.seen ? b2.pos : bl.pos;
  return (
    <>
      <Rig frame={frame} />
      <ambientLight intensity={0.5} color="#E4E8D8" />
      <directionalLight position={[-6, 12, 8]} intensity={2.4} color="#FFF1DC" castShadow shadow-mapSize={[2048, 2048]} shadow-bias={-0.0004}
        shadow-camera-left={-16} shadow-camera-right={16} shadow-camera-top={16} shadow-camera-bottom={-30} shadow-camera-far={60} />
      <directionalLight position={[8, 4, -8]} intensity={0.45} color={color.lime} />
      <pointLight position={[glow.x, glow.y + 0.6, glow.z + 0.8]} intensity={bl.seen || b2.seen ? 5 : 0} distance={5} decay={1.4} color={color.lime} />
      <mesh position={[0, -0.05, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[120, 120]} />
        <meshStandardMaterial color="#111310" roughness={0.9} />
      </mesh>

      {/* полка, доска, люк */}
      <Plank from={SHELF.from} to={SHELF.to} />
      <Plank from={PLANK.from} to={PLANK.to} />
      <mesh position={[HOLE.x, 0.01, HOLE.z]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[0.42, 32]} />
        <meshBasicMaterial color="#000000" />
      </mesh>
      <mesh position={[HOLE.x, 0.02, HOLE.z]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.42, 0.5, 32]} />
        <meshBasicMaterial color={LIME} toneMapped={false} />
      </mesh>

      {bl.seen && <Ball pos={bl.pos} spin={bl.spin} />}
      {b2.seen && <Ball pos={b2.pos} spin={b2.spin} />}

      {letters.map((m, i) => <Tile key={i} i={i} map={m} frame={frame} />)}

      {/* рычаг: качели на оси; дальний конец подбрасывает карточку */}
      <group position={LEVER.pivot} rotation={[0, 0, (0.28 - lv * 0.56)]}>
        <mesh castShadow receiveShadow>
          <boxGeometry args={[LEVER.half * 2, 0.1, 0.9]} />
          <meshStandardMaterial color={WOOD} roughness={0.6} />
        </mesh>
      </group>
      <mesh position={[LEVER.pivot.x, 0.18, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <cylinderGeometry args={[0.16, 0.16, 0.9, 24]} />
        <meshStandardMaterial color={METAL} roughness={0.6} />
      </mesh>

      {frame >= cardLaunch - 30 && frame < cardLands && <Card pos={cd.pos} quat={cd.quat} map={maps[0]} />}
      {frame >= cardLands && new Array(TUNNEL.n).fill(0).map((_, i) => {
        const c = tunnelCard(i, frame);
        if (c.u <= 0.001 || c.gone >= 0.999) return null;
        // карточки за спиной и вплотную к камере не рисуются
        if (c.pos.z > cam.pos.z - 0.9) return null;
        return <Card key={i} pos={c.pos} quat={c.quat} scale={c.scale} map={maps[i % maps.length]} />;
      })}

      {frame >= T.tunnel && <Phone frame={frame} fallback={maps[1]} />}
      {frame >= T.tunnel && (
        <>
          <Pipe />
          <Button frame={frame} follow={follow} done={done} />
        </>
      )}
    </>
  );
};

const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const out = leave(frame, BAR - 10, 10);
  return (
    <AbsoluteFill style={{ opacity: 1 - out, transform: `translateY(${-out * 90}px)` }}>
      <div style={{ position: 'absolute', left: safe.left, top: safe.top }}>
        <Mask px={128} color={color.lime}>Одна фраза</Mask>
        <Mask px={128} color={color.cream}>запустила всё</Mask>
      </div>
    </AbsoluteFill>
  );
};

const Cta: React.FC = () => {
  const frame = useCurrentFrame();
  const slot = (from: number) => {
    const t = enter(frame, from, 12);
    return { opacity: t, transform: `translateY(${(1 - t) * 60}px)` } as React.CSSProperties;
  };
  const out = leave(frame, T.back - T.cta + 20, 30);
  return (
    <AbsoluteFill style={{ opacity: 1 - out }}>
      <div style={{ position: 'absolute', left: safe.left, top: safe.top, display: 'flex', alignItems: 'center', gap: 20, ...slot(0) }}>
        <Img src={staticFile('brand/logo.png')} style={{ width: 72, height: 72 }} />
        <div style={{ fontFamily: sans, fontWeight: 800, fontSize: 54, color: color.cream, letterSpacing: '-0.02em' }}>4xTube</div>
      </div>
      <div style={{ position: 'absolute', left: safe.left, top: 340, width: 820, fontFamily: sans, fontWeight: 700, fontSize: 60, lineHeight: 1.14, letterSpacing: '-0.025em', color: color.cream, ...slot(6) }}>
        Как повторить, показываю в Telegram
      </div>
      <div style={{ position: 'absolute', left: safe.left, top: 500, width: 820, fontFamily: sans, fontWeight: 700, fontSize: 60, lineHeight: 1.14, letterSpacing: '-0.025em', color: color.lime, ...slot(14) }}>
        Что запустить следующим?
      </div>
    </AbsoluteFill>
  );
};

const SOUNDS: [number, string, number][] = [
  ...new Array(TILES).fill(0).map((_, i): [number, string, number] => [tileLands(i), `keyboard/press-${['r1', 'r2', 'r3'][i % 3]}.wav`, 0.75]),
  [cardLaunch, 'whoosh.wav', 0.4],
  [T.tunnel + 10, 'whoosh.wav', 0.35],
  [T.phone, 'click.wav', 0.35],
  [T.press, 'keyboard/press-enter.wav', 0.9],
];

export type ChainProps = { music: boolean };

export const Chain: React.FC<ChainProps> = ({ music }) => {
  const frame = useCurrentFrame();
  const maps = useTextures(FRAMES.map((f) => staticFile(f)));
  const bump = hit(frame, Math.floor(frame / BEAT) * BEAT, 8) * 0.004 + hit(frame, T.press, 10) * 0.02;
  return (
    <AbsoluteFill style={{ background: GROUND }}>
      {maps && (
        <AbsoluteFill style={{ transform: `scale(${1 + bump})` }}>
          <ThreeCanvas width={W} height={H} flat shadows camera={{ fov: 42, near: 0.1, far: 90 }}>
            <color attach="background" args={[GROUND]} />
            <fog attach="fog" args={[GROUND, 12, 60]} />
            <Scene frame={frame} maps={maps} />
          </ThreeCanvas>
        </AbsoluteFill>
      )}
      <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(14,15,12,0.85) 0%, rgba(14,15,12,0.4) 24%, rgba(14,15,12,0) 42%)' }} />
      <Sequence from={T.hook} durationInFrames={BAR + 2}><Hook /></Sequence>
      <Sequence from={T.cta}><Cta /></Sequence>
      {/* субтитры наверху, на тёмном градиенте: низ кадра занят сценой */}
      <Captions words={words as Word[]} top={safe.top} hide={[[0, BAR], [T.cta, LENGTH]]} />
      {music && <Audio src={staticFile('series/r7.m4a')} volume={0.92} />}
      {SOUNDS.map(([from, name, volume], i) => (
        <Sequence key={i} from={from} layout="none"><Audio src={staticFile(`sfx/${name}`)} volume={volume} /></Sequence>
      ))}
    </AbsoluteFill>
  );
};
