// Текстуры для трёхмерной сцены грузятся до того, как холст смонтирован.
// Почему не useLoader внутри холста: на нулевом кадре Remotion не ждёт перерисовки R3F, и
// пока Suspense грузит картинки, кадр уходит пустым. Здесь рендер задерживается явно,
// а холст получает уже готовые текстуры.
import { useEffect, useState } from 'react';
import { continueRender, delayRender } from 'remotion';
import * as THREE from 'three';

export const useTextures = (urls: string[]) => {
  const [maps, setMaps] = useState<THREE.Texture[] | null>(null);
  const [handle] = useState(() => delayRender('текстуры сцены'));
  useEffect(() => {
    const loader = new THREE.TextureLoader();
    Promise.all(urls.map((u) => loader.loadAsync(u))).then((loaded) => {
      loaded.forEach((m) => {
        m.colorSpace = THREE.SRGBColorSpace;
        m.anisotropy = 8;
      });
      setMaps(loaded);
      continueRender(handle);
    });
    // адреса постоянны на весь ролик
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [handle]);
  return maps;
};
