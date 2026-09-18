// Картинка с сайта за проверкой Vercel: сначала пройти её страницей, потом fetch изнутри.
// node значок-браузером.mjs <страница> <адрес картинки> <файл>
import { createRequire } from "module";
import { writeFileSync } from "fs";
const require = createRequire("/Users/xiix/4xSoft/html-instagram-carousel/package.json");
const { chromium } = require("playwright-core");
const [стр, адрес, файл] = process.argv.slice(2);
const CHROME = "/Users/xiix/.cache/chrome-headless-shell/chrome-headless-shell/mac_arm-153.0.8010.36/chrome-headless-shell-mac-arm64/chrome-headless-shell";
const б = await chromium.launch({ executablePath: CHROME, headless: true });
try {
  const с = await б.newPage({ userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36" });
  await с.goto(стр, { waitUntil: "domcontentloaded", timeout: 45000 });
  await с.waitForTimeout(10000);
  const [тип, б64] = await с.evaluate(async a => { const r = await fetch(a); const buf = new Uint8Array(await r.arrayBuffer()); let s = ""; for (const x of buf) s += String.fromCharCode(x); return [r.headers.get("content-type"), btoa(s)]; }, адрес);
  writeFileSync(файл, Buffer.from(б64, "base64"));
  console.log(тип, файл);
} finally { await б.close(); }
