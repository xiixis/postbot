// Надписи на клавишах и свечение рисуются на холсте и идут в сцену текстурами.
// Рисуются белым: цвет надписи задаёт материал, поэтому его можно менять по кадрам.
import * as THREE from 'three';
import { mono, sans } from '../lib/brand';
import type { Key } from './layout';

const PX = 256;                       // точек холста на единицу длины клавиши
export const INSET = 0.24;            // на столько надпись меньше клавиши по каждой стороне

const canvas = (w: number, h: number) => {
  const c = document.createElement('canvas');
  c.width = Math.round(w);
  c.height = Math.round(h);
  const ctx = c.getContext('2d') as CanvasRenderingContext2D;
  ctx.fillStyle = '#fff';
  ctx.strokeStyle = '#fff';
  return { c, ctx };
};

const texture = (c: HTMLCanvasElement) => {
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  return t;
};

const arrow = (ctx: CanvasRenderingContext2D, cx: number, cy: number, s: number) => {
  ctx.lineWidth = s * 0.14;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.beginPath();
  ctx.moveTo(cx + s * 0.5, cy - s * 0.42);
  ctx.lineTo(cx + s * 0.5, cy + s * 0.12);
  ctx.lineTo(cx - s * 0.5, cy + s * 0.12);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(cx - s * 0.22, cy - s * 0.16);
  ctx.lineTo(cx - s * 0.5, cy + s * 0.12);
  ctx.lineTo(cx - s * 0.22, cy + s * 0.4);
  ctx.stroke();
};

// Обычная надпись: латинская буква слева сверху, русская справа снизу, как на живой клавиатуре.
export const legend = (key: Key) => {
  const w = (key.w - INSET) * PX, h = (1 - INSET) * PX;
  const { c, ctx } = canvas(w, h);
  ctx.textBaseline = 'middle';
  if (key.kind === 'enter') {
    arrow(ctx, w * 0.5, h * 0.5, h * 0.62);
  } else if (key.kind === 'mod') {
    ctx.font = `500 ${h * 0.24}px ${mono}`;
    ctx.globalAlpha = 0.62;
    ctx.textAlign = 'left';
    ctx.fillText(key.en, h * 0.08, h * 0.8);
  } else if (key.kind === 'char' && key.ru) {
    ctx.font = `600 ${h * 0.3}px ${sans}`;
    ctx.globalAlpha = 0.55;
    ctx.textAlign = 'left';
    ctx.fillText(key.en.toUpperCase(), h * 0.08, h * 0.24);
    ctx.font = `700 ${h * 0.5}px ${sans}`;
    ctx.globalAlpha = 1;
    ctx.textAlign = 'right';
    ctx.fillText(key.ru.toUpperCase(), w - h * 0.08, h * 0.68);
  } else if (key.kind === 'char') {
    ctx.font = `600 ${h * 0.42}px ${sans}`;
    ctx.globalAlpha = 0.8;
    ctx.textAlign = 'center';
    ctx.fillText(key.en, w * 0.5, h * 0.52);
  }
  return texture(c);
};

// Клавиша в слове: одна крупная латинская буква по центру.
export const letter = (ch: string) => {
  const s = (1 - INSET) * PX;
  const { c, ctx } = canvas(s, s);
  ctx.font = `800 ${s * 0.78}px ${sans}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(ch.toUpperCase(), s * 0.5, s * 0.54);
  return texture(c);
};

// Надпись на широкой клавише-кнопке.
export const label = (text: string, units: number, check = false) => {
  const w = (units - INSET) * PX, h = (1.3 - INSET) * PX;
  const { c, ctx } = canvas(w, h);
  ctx.font = `800 ${h * 0.46}px ${sans}`;
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'center';
  const tick = check ? h * 0.5 : 0;
  // длинная надпись ужимается, чтобы не срезаться краями клавиши
  const room = (w - tick) * 0.88;
  const wide = ctx.measureText(text).width;
  if (wide > room) ctx.font = `800 ${h * 0.46 * (room / wide)}px ${sans}`;
  ctx.fillText(text, (w - tick) * 0.5, h * 0.53);
  if (check) {
    const tw = ctx.measureText(text).width;
    const x = (w - tick) * 0.5 + tw * 0.5 + h * 0.16, y = h * 0.52, s = h * 0.34;
    ctx.lineWidth = h * 0.075;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x + s * 0.36, y + s * 0.36);
    ctx.lineTo(x + s, y - s * 0.4);
    ctx.stroke();
  }
  return texture(c);
};

// Мягкое пятно света над нажатой клавишей.
export const halo = () => {
  const s = 256;
  const { c, ctx } = canvas(s, s);
  const g = ctx.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
  g.addColorStop(0, 'rgba(255,255,255,0.9)');
  g.addColorStop(0.35, 'rgba(255,255,255,0.32)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, s, s);
  return texture(c);
};
