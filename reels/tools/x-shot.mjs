// Снимок поста X как с телефона: node tools/x-shot.mjs <ссылка на пост> <файл.png> → <файл>-post.png по рамке поста.
// Мобильный размер, тёмная тема, русский интерфейс, без входа; плашка «Откройте в приложении» убирается.
import { createRequire } from "module";
import { existsSync, readdirSync } from "fs";
import { join } from "path";
import { homedir } from "os";
const find = (r, ok) => existsSync(r) ? readdirSync(r).sort().reverse().map(i => join(r, i)).find(ok) : null;
const base = find(join(homedir(), ".npm/_npx"), p => existsSync(join(p, "node_modules/playwright-core")));
const require = createRequire(join(base, "package.json"));
const { chromium } = require("playwright-core");
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const [url, out] = process.argv.slice(2);
const b = await chromium.launch({ executablePath: CHROME, headless: true });
const ctx = await b.newContext({ viewport: { width: 430, height: 932 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true,
  colorScheme: "dark", locale: "ru-RU",
  userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1" });
const p = await ctx.newPage();
await p.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
await p.waitForTimeout(9000);
// Плашку «Откройте этот пост в приложении» и полосу входа убираем, как cookie-баннеры у снимальщика
// сайтов: сам пост X показывает без входа, это реклама приложения, а не закрытый доступ.
await p.evaluate(() => {
  for (const el of document.querySelectorAll('[role="dialog"], [data-testid="sheetDialog"], [data-testid="BottomBar"]')) el.remove();
  const l = document.querySelector('#layers'); if (l) for (const c of [...l.children]) c.remove();
  document.documentElement.style.overflow = document.body.style.overflow = 'auto';
});
await p.waitForTimeout(800);
const box = await p.evaluate(() => { const a = document.querySelector('article'); const r = a ? a.getBoundingClientRect() : null; return r ? { x: r.x, y: r.y, w: r.width, h: r.height } : null; });
console.log('пост', JSON.stringify(box));
if (box) await p.screenshot({ path: out.replace('.png', '-post.png'), clip: { x: 0, y: Math.max(0, box.y), width: 430, height: box.h } });
const info = await p.evaluate(() => ({ title: document.title, hasTweet: !!document.querySelector('article[data-testid="tweet"]'), text: document.body.innerText.slice(0, 300) }));
console.log(JSON.stringify(info));
await p.screenshot({ path: out });
await b.close();
