// Слои кадра в PNG с прозрачностью: node tools/layers.mjs
// Рендерит композицию WordsLayer по одному слою в public/mock/layers/NN.png.
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { bundle } from '@remotion/bundler';
import { renderStill, selectComposition } from '@remotion/renderer';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const LAYERS = 19;
const serveUrl = await bundle({ entryPoint: path.join(root, 'src/index.ts'), publicDir: path.join(root, 'public') });
for (let layer = 0; layer < LAYERS; layer++) {
  const composition = await selectComposition({ serveUrl, id: 'WordsLayer', inputProps: { layer } });
  const output = path.join(root, 'public/mock/layers', `${String(layer).padStart(2, '0')}.png`);
  await renderStill({ composition, serveUrl, frame: 0, output, imageFormat: 'png', inputProps: { layer }, logLevel: 'error' });
  console.log(output);
}
