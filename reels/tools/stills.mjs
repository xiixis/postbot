// Контрольные кадры ролика одной сборкой: node tools/stills.mjs <композиция> <кадр> [кадр…]
// `remotion still` собирает проект заново на каждый кадр; здесь сборка одна на все.
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { bundle } from '@remotion/bundler';
import { renderStill, selectComposition } from '@remotion/renderer';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [id, ...frames] = process.argv.slice(2);
if (!id || !frames.length) {
  console.error('нужны композиция и хотя бы один кадр');
  process.exit(2);
}

const serveUrl = await bundle({ entryPoint: path.join(root, 'src/index.ts'), publicDir: path.join(root, 'public') });
const composition = await selectComposition({ serveUrl, id });
for (const f of frames) {
  const output = path.join(root, 'out', id, `${String(f).padStart(3, '0')}.jpg`);
  await renderStill({ composition, serveUrl, frame: Number(f), output, imageFormat: 'jpeg', jpegQuality: 90, logLevel: 'error' });
  console.log(output);
}
