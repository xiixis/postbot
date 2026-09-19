// Официальный значок сервиса: node взять-лого.mjs <имя> <адрес> → снимки/<имя>.png
//
// Берём не снимок шапки сайта (знак там мелкий и в окружении чужого баннера), а
// фирменный значок, который сайт сам отдаёт браузеру: `apple-touch-icon`, затем
// иконка манифеста, затем og:image, затем favicon. Это чистый квадратный логотип
// в фирменных цветах — ровно то, что стоит в плитках у автора референса.
//
// Решение владельца 19.09.2026: в кадрах нужны настоящие логотипы, а не снимки.
import { createRequire } from "module";
import { existsSync, readdirSync, writeFileSync } from "fs";
import { join } from "path";
import { homedir } from "os";
import { fileURLToPath } from "url";

function найти(корень, годится) {
  if (!existsSync(корень)) return null;
  return readdirSync(корень).sort().reverse().map(и => join(корень, и)).find(годится) ?? null;
}
const база = найти(join(homedir(), ".npm/_npx"), п => existsSync(join(п, "node_modules/playwright-core")));
if (!база) { console.error("нет playwright-core"); process.exit(1); }
const require = createRequire(join(база, "package.json"));
const { chromium } = require("playwright-core");
const версия = найти(join(homedir(), ".cache/chrome-headless-shell/chrome-headless-shell"),
                     п => existsSync(join(п, "chrome-headless-shell-mac-arm64/chrome-headless-shell")));
const CHROME = join(версия, "chrome-headless-shell-mac-arm64/chrome-headless-shell");

const [имя, адрес] = process.argv.slice(2);
const UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
         + "(KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36";

const браузер = await chromium.launch({ executablePath: CHROME, headless: true });
try {
  const стр = await браузер.newPage({ viewport: { width: 1280, height: 800 }, userAgent: UA });
  await стр.goto(адрес, { waitUntil: "domcontentloaded", timeout: 45000 });
  await стр.waitForTimeout(2500);

  // Собираем кандидатов по убыванию качества. Размер из атрибута sizes — подсказка,
  // но врут все, поэтому реальный вес проверяем уже скачав.
  const кандидаты = await стр.evaluate(() => {
    const с = [];
    const добавить = (url, вес) => { if (url) с.push({ url: new URL(url, location.href).href, вес }); };
    for (const у of document.querySelectorAll('link[rel*="apple-touch-icon" i]')) {
      const р = parseInt((у.getAttribute("sizes") || "180").split("x")[0], 10) || 180;
      добавить(у.getAttribute("href"), 1000 + р);
    }
    for (const у of document.querySelectorAll('link[rel="icon"], link[rel="shortcut icon"]')) {
      const р = parseInt((у.getAttribute("sizes") || "64").split("x")[0], 10) || 64;
      добавить(у.getAttribute("href"), (у.getAttribute("type") === "image/svg+xml" ? 900 : 300) + р);
    }
    const ог = document.querySelector('meta[property="og:image"]');
    if (ог) добавить(ог.getAttribute("content"), 200);
    return с.sort((а, б) => б.вес - а.вес);
  });

  // Манифест часто держит самую крупную иконку — читаем и его.
  const манифест = await стр.evaluate(() => {
    const м = document.querySelector('link[rel="manifest"]');
    return м ? new URL(м.getAttribute("href"), location.href).href : null;
  });
  if (манифест) {
    try {
      const о = await стр.request.get(манифест);
      const д = await о.json();
      for (const и of (д.icons || [])) {
        const р = parseInt((и.sizes || "0").split("x")[0], 10) || 0;
        if (р >= 180) кандидаты.push({ url: new URL(и.src, манифест).href, вес: 1100 + р });
      }
      кандидаты.sort((а, б) => б.вес - а.вес);
    } catch { /* манифеста может не быть или он закрыт — не беда */ }
  }

  if (!кандидаты.length) { console.log(`${имя}: значков не найдено`); process.exit(3); }

  const куда = fileURLToPath(new URL(`./снимки/${имя}.png`, import.meta.url));
  for (const к of кандидаты.slice(0, 6)) {
    try {
      const о = await стр.request.get(к.url, { timeout: 20000 });
      if (!о.ok()) continue;
      const тело = await о.body();
      // Мелочь вроде favicon 16×16 в плитке 300 px будет мылом — пропускаем.
      if (тело.length < 1200) continue;
      const тип = (о.headers()["content-type"] || "").toLowerCase();
      const путь = тип.includes("svg") ? куда.replace(/\.png$/, ".svg") : куда;
      writeFileSync(путь, тело);
      console.log(`${имя}: взят ${тип.includes("svg") ? "SVG" : "PNG"} ${Math.round(тело.length / 1024)} КБ ← ${к.url.slice(0, 70)}`);
      process.exit(0);
    } catch { /* следующий кандидат */ }
  }
  console.log(`${имя}: ни один значок не скачался`);
  process.exit(4);
} finally {
  await браузер.close();
}
