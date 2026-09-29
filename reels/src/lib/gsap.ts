// GSAP внутри Remotion.
// GSAP живёт по своим часам, а ролик считается из номера кадра. Поэтому таймлайн собирается
// один раз и стоит на паузе, а на каждом кадре его головка ставится в нужную секунду.
// Рендер может считать кадры не по порядку и в несколько вкладок: от этого ничего не
// зависит, потому что положение головки задаётся кадром, а не прошедшим временем.
import { useLayoutEffect, useRef } from 'react';
import gsap from 'gsap';
import { useCurrentFrame, useVideoConfig } from 'remotion';

// Сборщик получает пустой таймлайн и корневой элемент сцены. Селекторы внутри него
// ищут только в этой сцене: две сцены с одинаковыми классами друг другу не мешают.
export type Build = (tl: gsap.core.Timeline, root: HTMLElement) => void;

// lead — на сколько секунд таймлайн опережает кадр. Нужен первой сцене ролика: на нулевом
// кадре движение уже идёт, и первый кадр не выходит пустым.
export const useTimeline = (build: Build, lead = 0) => {
  const root = useRef<HTMLDivElement>(null);
  const timeline = useRef<gsap.core.Timeline | null>(null);
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  useLayoutEffect(() => {
    const scope = root.current;
    if (!scope) return undefined;
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ paused: true });
      build(tl, scope);
      timeline.current = tl;
    }, scope);
    return () => {
      timeline.current = null;
      ctx.revert();
    };
    // Сборщик зависит только от разметки сцены, пересобирать его на каждом кадре нельзя.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useLayoutEffect(() => {
    timeline.current?.seek(Math.max(0, frame / fps + lead), false);
  }, [frame, fps, lead]);

  return root;
};

// Секунды из кадров и ударов: GSAP считает в секундах, музыка в ударах.
export const sec = (frames: number, fps = 30) => frames / fps;
export const beats = (n: number, bpm: number) => (n * 60) / bpm;
