// Материал экрана с видео внутри ThreeCanvas.
// При рендере видео приходит кадром через useOffthreadVideoTexture, в студии ставится картинка.
// Материал собирается руками: смена текстуры требует пересборки шейдера (needsUpdate).
// Кадр видео приходит позже, чем ThreeCanvas отрисовал сцену по смене номера кадра,
// поэтому после подмены карты сцена рисуется ещё раз через advance(): без этого экран белый.
import { useLayoutEffect, useMemo, useRef } from 'react';
import { useThree } from '@react-three/fiber';
import { useRemotionEnvironment } from 'remotion';
import * as THREE from 'three';

export const useScreen = (map: THREE.Texture | null, on = 1, opacity = 1) => {
  const mat = useMemo(() => new THREE.MeshBasicMaterial({ toneMapped: false, transparent: true }), []);
  const advance = useThree((s) => s.advance);
  const { isRendering } = useRemotionEnvironment();
  const last = useRef<THREE.Texture | null>(null);
  useLayoutEffect(() => {
    if (map) map.colorSpace = THREE.SRGBColorSpace;
    mat.map = map;
    mat.color.setRGB(on, on, on);
    mat.opacity = opacity;
    mat.needsUpdate = true;
    if (isRendering && map && map !== last.current) advance(performance.now());
    last.current = map;
  });
  return mat;
};
