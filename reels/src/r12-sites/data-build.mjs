// Данные сцен r12 в один файл: node src/r12-sites/data-build.mjs → src/r12-sites/shared/data.js
//
// Ролик рассказывает о Phosphor и LottieFiles, поэтому в кадре их настоящие вещи, а не рисунки «под них»:
// иконки берутся из пакета @phosphor-icons/core (MIT), анимации — файлы с LottieFiles (Lottie Simple
// License, номера в именах файлов, источник в public/sites/lottie/CREDITS.md). Анимации перекрашены
// в оливу бренда: у авторов чужая палитра. Время начала вшивает сама страница (shiftLottie в scenes.js).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..', '..');
const ph = path.join(root, 'node_modules', '@phosphor-icons', 'core', 'assets');

const svgInner = (weight, name) => {
  const file = path.join(ph, weight, weight === 'regular' ? `${name}.svg` : `${name}-${weight}.svg`);
  return fs.readFileSync(file, 'utf8').replace(/^[\s\S]*?<svg[^>]*>/, '').replace(/<\/svg>\s*$/, '').trim();
};

// Сетка для сцены Phosphor и значки по всему ролику. Порядок задаёт раскладку сетки.
const NAMES = ['video-camera', 'music-note', 'film-strip', 'waveform', 'speaker-high', 'image', 'camera', 'sparkle',
  'star', 'heart', 'check-circle', 'arrow-bend-up-right', 'smiley', 'paper-plane-tilt', 'play', 'scissors',
  'magic-wand', 'palette', 'sun', 'moon', 'lightning', 'rocket', 'bell', 'gift', 'cat', 'folder',
  'download-simple', 'cloud', 'gear', 'pencil-simple', 'eye', 'fire', 'crown', 'trophy', 'map-pin',
  'chat-circle', 'music-notes', 'headphones', 'microphone', 'film-slate', 'cursor-click', 'lightbulb',
  'aperture', 'monitor-play', 'film-reel', 'user', 'share-fat', 'link', 'telegram-logo', 'bookmark-simple',
  'file-video', 'file-audio', 'cursor'];
const icons = Object.fromEntries(NAMES.map((n) => [n, svgInner('regular', n)]));
const bold = Object.fromEntries(['music-note', 'film-strip', 'waveform', 'file-video', 'file-audio', 'film-slate', 'sparkle', 'play', 'check', 'link', 'cursor-click', 'paper-plane-tilt', 'user', 'bookmark-simple', 'share-fat']
  .map((n) => [n, svgInner('bold', n)]));
const weights = Object.fromEntries(['thin', 'light', 'regular', 'bold', 'fill', 'duotone'].map((w) => [w, svgInner(w, 'cat')]));

// Lottie: каждую заливку и обводку красим в один цвет. Прозрачность и анимация цвета не трогаются.
const recolor = (node, rgb) => {
  if (Array.isArray(node)) { node.forEach((n) => recolor(n, rgb)); return; }
  if (!node || typeof node !== 'object') return;
  if ((node.ty === 'fl' || node.ty === 'st') && node.c && node.c.a === 0 && Array.isArray(node.c.k)) node.c.k = [...rgb, 1];
  Object.values(node).forEach((v) => recolor(v, rgb));
};
const OLIVE = [86 / 255, 105 / 255, 12 / 255];
const lottie = {};
for (const [key, file] of [['arrow', 'arrow-1523914'], ['check', 'check-1023841'], ['smile', 'smile-87316'], ['path', 'path-1519888']]) {
  const data = JSON.parse(fs.readFileSync(path.join(root, 'public', 'sites', 'lottie', `${file}.json`), 'utf8'));
  recolor(data.layers, OLIVE);
  recolor(data.assets || [], OLIVE);
  lottie[key] = data;
}

const out = `// Собрано src/r12-sites/data-build.mjs, руками не править.
// Иконки Phosphor (MIT): содержимое <svg viewBox="0 0 256 256" fill="currentColor">.
export const ICONS = ${JSON.stringify(icons)};
export const BOLD = ${JSON.stringify(bold)};
export const CAT_WEIGHTS = ${JSON.stringify(weights)};
// Анимации LottieFiles, перекрашены в оливу. Номера и ссылки: public/sites/lottie/CREDITS.md.
export const LOTTIE = ${JSON.stringify(lottie)};
`;
fs.writeFileSync(path.join(here, 'shared', 'data.js'), out);
console.log(`data.js: ${(out.length / 1024).toFixed(0)} КБ, иконок ${NAMES.length}, жирных ${Object.keys(bold).length}, анимаций ${Object.keys(lottie).length}`);
