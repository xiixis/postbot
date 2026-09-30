// Точки для ролика «20 000 точек»: откуда берутся их места и цвета.
// Портрет считается с картинки кота: точка садится туда, где пиксель тёмный (тело) или
// лаймовый (глаза, линии); слово и знак канала берутся с растра текста и картинки знака.
import * as THREE from 'three';
import { color, rnd } from '../lib/brand';

export const N = 20000;

export type Cloud = { pos: Float32Array; col: Float32Array; size: Float32Array };

const LIME = new THREE.Color(color.lime);
const CREAM = new THREE.Color(color.cream);
const CLAUDE = new THREE.Color(color.claude);

const empty = (): Cloud => ({ pos: new Float32Array(N * 3), col: new Float32Array(N * 3), size: new Float32Array(N) });

// Выбор N точек из кандидатов с весами: перебор по накопленной сумме, детерминированный.
const pick = (weights: number[], n: number) => {
  const total = weights.reduce((a, b) => a + b, 0);
  const out: number[] = [];
  for (let i = 0; i < n; i++) {
    let r = rnd(i * 1.37 + 0.5) * total;
    let j = 0;
    while (j < weights.length - 1 && r > weights[j]) { r -= weights[j]; j++; }
    out.push(j);
  }
  return out;
};

const pixels = (img: HTMLImageElement | HTMLCanvasElement, w: number, h: number) => {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  const ctx = c.getContext('2d') as CanvasRenderingContext2D;
  ctx.drawImage(img, 0, 0, w, h);
  return ctx.getImageData(0, 0, w, h).data;
};

// Портрет: картинка кота на светлом фоне. Точки ложатся на тёмное и на лаймовое.
export const portrait = (img: HTMLImageElement, height = 5.0): Cloud => {
  const w = 220, h = Math.round((w * img.height) / img.width);
  const data = pixels(img, w, h);
  const weights: number[] = [];
  for (let i = 0; i < w * h; i++) {
    const r = data[i * 4], g = data[i * 4 + 1], b = data[i * 4 + 2];
    const lum = (r + g + b) / 3;
    const lime = g > r * 1.15 && g > b * 1.6 && g > 110;
    weights.push(lime ? 3 : Math.max(0, (150 - lum) / 150) ** 1.4);
  }
  const chosen = pick(weights, N);
  const cloud = empty();
  const scale = height / h;
  chosen.forEach((j, i) => {
    const x = j % w, y = Math.floor(j / w);
    const r = data[j * 4], g = data[j * 4 + 1], b = data[j * 4 + 2];
    const lime = g > r * 1.15 && g > b * 1.6 && g > 110;
    const lum = (r + g + b) / 3;
    cloud.pos[i * 3] = (x - w / 2 + rnd(i * 2.1) - 0.5) * scale;
    cloud.pos[i * 3 + 1] = (h / 2 - y + rnd(i * 3.3) - 0.5) * scale;
    cloud.pos[i * 3 + 2] = lime ? 0.12 : (rnd(i * 4.7) - 0.5) * 0.25;
    const c = lime ? LIME : CREAM.clone().multiplyScalar(0.55 + 0.45 * (1 - lum / 150));
    cloud.col[i * 3] = c.r; cloud.col[i * 3 + 1] = c.g; cloud.col[i * 3 + 2] = c.b;
    cloud.size[i] = lime ? 1.6 : 0.7 + rnd(i * 5.9) * 0.6;
  });
  return cloud;
};

// Слово: растр текста на холсте, точки ложатся на буквы.
export const word = (text: string, height = 1.3, tint = CLAUDE): Cloud => {
  const c = document.createElement('canvas');
  c.width = 1400; c.height = 360;
  const ctx = c.getContext('2d') as CanvasRenderingContext2D;
  ctx.fillStyle = '#fff';
  ctx.font = '800 300px Onest, sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, 700, 190);
  const w = 350, h = 90;
  const data = pixels(c, w, h);
  const weights: number[] = [];
  for (let i = 0; i < w * h; i++) weights.push(data[i * 4] > 128 ? 1 : 0);
  const chosen = pick(weights, N);
  const cloud = empty();
  const scale = height / h;
  chosen.forEach((j, i) => {
    const x = j % w, y = Math.floor(j / w);
    cloud.pos[i * 3] = (x - w / 2 + rnd(i * 2.1) - 0.5) * scale;
    cloud.pos[i * 3 + 1] = (h / 2 - y + rnd(i * 3.3) - 0.5) * scale;
    cloud.pos[i * 3 + 2] = (rnd(i * 4.7) - 0.5) * 0.2;
    cloud.col[i * 3] = tint.r; cloud.col[i * 3 + 1] = tint.g; cloud.col[i * 3 + 2] = tint.b;
    cloud.size[i] = 0.9 + rnd(i * 5.9) * 0.5;
  });
  return cloud;
};

// Знак канала с картинки с прозрачностью.
export const mark = (img: HTMLImageElement, height = 1.6): Cloud => {
  const w = 160, h = Math.round((w * img.height) / img.width);
  const data = pixels(img, w, h);
  const weights: number[] = [];
  for (let i = 0; i < w * h; i++) weights.push(data[i * 4 + 3] > 100 ? 1 : 0);
  const chosen = pick(weights, N);
  const cloud = empty();
  const scale = height / h;
  chosen.forEach((j, i) => {
    const x = j % w, y = Math.floor(j / w);
    cloud.pos[i * 3] = (x - w / 2 + rnd(i * 2.1) - 0.5) * scale;
    cloud.pos[i * 3 + 1] = (h / 2 - y + rnd(i * 3.3) - 0.5) * scale;
    cloud.pos[i * 3 + 2] = (rnd(i * 4.7) - 0.5) * 0.2;
    cloud.col[i * 3] = LIME.r; cloud.col[i * 3 + 1] = LIME.g; cloud.col[i * 3 + 2] = LIME.b;
    cloud.size[i] = 1.1 + rnd(i * 5.9) * 0.5;
  });
  return cloud;
};

// Воронка: три спиральных рукава, как галактика, в нижних двух третях кадра.
export const vortex = (turn = 0): Cloud => {
  const cloud = empty();
  for (let i = 0; i < N; i++) {
    const t = rnd(i * 1.1);
    const arm = i % 3;
    const a = t * Math.PI * 4 + (arm * Math.PI * 2) / 3 + turn;
    const r = 0.35 + t * 2.7;
    const spread = 0.12 + t * 0.35;
    const ax = Math.cos(a) * r + (rnd(i * 2.2) - 0.5) * spread;
    const az = Math.sin(a) * r + (rnd(i * 3.3) - 0.5) * spread;
    cloud.pos[i * 3] = ax;
    cloud.pos[i * 3 + 1] = -1.1 + az * 0.55 + (rnd(i * 4.4) - 0.5) * 0.25;
    cloud.pos[i * 3 + 2] = az * 0.5;
    const lime = rnd(i * 7.7) > 0.86;
    const c = lime ? LIME : CREAM.clone().multiplyScalar(0.3 + 0.6 * (1 - t));
    cloud.col[i * 3] = c.r; cloud.col[i * 3 + 1] = c.g; cloud.col[i * 3 + 2] = c.b;
    cloud.size[i] = 0.5 + rnd(i * 5.9) * 0.9;
  }
  return cloud;
};

// Спрайт точки: мягкое пятно, ярче к середине.
export const sprite = () => {
  const s = 64;
  const c = document.createElement('canvas');
  c.width = s; c.height = s;
  const ctx = c.getContext('2d') as CanvasRenderingContext2D;
  const g = ctx.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.3, 'rgba(255,255,255,0.75)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, s, s);
  const t = new THREE.CanvasTexture(c);
  return t;
};
