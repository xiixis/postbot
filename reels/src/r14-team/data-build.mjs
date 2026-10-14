// Данные сцен r14 в один файл: node src/r14-team/data-build.mjs → src/r14-team/shared/data.js
//
// Значки — настоящие файлы пакета @phosphor-icons/core (MIT), а не рисунки «под них».
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

const REGULAR = ['chat-circle', 'user', 'heart', 'cursor-click', 'paper-plane-tilt', 'sparkle', 'image', 'puzzle-piece', 'plug',
  'gear', 'folder-simple', 'clock', 'eye', 'pencil-simple-line', 'palette', 'film-strip', 'waveform', 'check', 'x',
  'arrow-up-right', 'bookmark-simple', 'telegram-logo', 'hand-palm', 'lightbulb', 'microphone', 'film-slate',
  'magnifying-glass', 'play', 'text-t', 'users-three', 'arrow-counter-clockwise', 'scissors', 'arrow-bend-down-left'];
const FILL = ['heart', 'telegram-logo', 'check-circle', 'x-circle', 'bookmark-simple', 'play', 'sparkle', 'lightbulb', 'hand-palm',
  'folder-simple', 'user'];
const BOLD = ['check', 'x', 'arrow-up-right', 'arrow-bend-down-left', 'pencil-simple-line', 'palette', 'film-strip', 'waveform', 'eye',
  'puzzle-piece', 'plug', 'gear', 'users-three', 'microphone', 'lightbulb', 'film-slate', 'magnifying-glass', 'clock',
  'arrow-counter-clockwise'];

const icons = Object.fromEntries(REGULAR.map((n) => [n, svgInner('regular', n)]));
const fill = Object.fromEntries(FILL.map((n) => [n, svgInner('fill', n)]));
const bold = Object.fromEntries(BOLD.map((n) => [n, svgInner('bold', n)]));

const out = `// Собрано src/r14-team/data-build.mjs, руками не править.
// Иконки Phosphor (MIT): содержимое <svg viewBox="0 0 256 256" fill="currentColor">.
export const ICONS = ${JSON.stringify(icons)};
export const FILL = ${JSON.stringify(fill)};
export const BOLD = ${JSON.stringify(bold)};
`;
fs.mkdirSync(path.join(here, 'shared'), { recursive: true });
fs.writeFileSync(path.join(here, 'shared', 'data.js'), out);
console.log(`shared/data.js: ${(out.length / 1024).toFixed(0)} КБ, значков ${REGULAR.length + FILL.length + BOLD.length}`);
