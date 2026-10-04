// Картинка рейтинга для Telegram: node src/r13-rating/картинка.mjs → out/r13-rating-рейтинг.html,
// снимок делает Chrome (команда в конце вывода). Тот же тир-лист и те же стили, что в ролике.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const src = path.join(root, 'src', 'r13-rating', 'shared');
const mod = await import(pathToFileURL(path.join(src, 'scenes.js')).href);
const A = pathToFileURL(path.join(root, 'public', 'rating')).href;
const fonts = fs.readFileSync(path.join(root, 'public', 'rating', 'fonts', 'fonts.css'), 'utf8').replaceAll('{{A}}', A);
const css = fs.readFileSync(path.join(src, 'scenes.css'), 'utf8');
const html = `<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>
${fonts}
html, body { margin: 0; width: 1080px; height: 1350px; overflow: hidden; background: #0A0B08; }
${css}
.r10 .pic { position: absolute; inset: 0; background: radial-gradient(ellipse 70% 50% at 50% 55%, rgba(137,168,28,.35), rgba(10,11,8,0) 70%), #0A0B08; }
.r10 .pt { position: absolute; left: 190px; top: 54px; }
.r10 .pt b { display: block; font-family: var(--disp); font-weight: 800; font-size: 62px; letter-spacing: -0.045em; line-height: 1.1; }
.r10 .pt span { display: block; margin-top: 14px; font-size: 36px; color: var(--dim); }
</style></head><body><div class="r10">${mod.pictureMarkup(A)}</div></body></html>`;
const out = path.join(root, 'out', 'r13-rating-рейтинг.html');
fs.writeFileSync(out, html);
console.log(pathToFileURL(out).href);
