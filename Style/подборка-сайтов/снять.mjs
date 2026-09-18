// Снимок первого экрана сайта без всплывающих окон и cookie-плашек.
// node снять.mjs <имя> <адрес> [ширина высота]  → сайты/<имя>.png
import { createRequire } from "module";
import { fileURLToPath } from "url";
const require = createRequire("/Users/xiix/4xSoft/html-instagram-carousel/package.json");
const { chromium } = require("playwright-core");

const [имя, адрес, ш = "1440", в = "900"] = process.argv.slice(2);
const CHROME = "/Users/xiix/.cache/chrome-headless-shell/chrome-headless-shell/mac_arm-153.0.8010.36/chrome-headless-shell-mac-arm64/chrome-headless-shell";

const браузер = await chromium.launch({ executablePath: CHROME, headless: true });
try {
  const стр = await браузер.newPage({ viewport: { width: +ш, height: +в }, deviceScaleFactor: 2 });
  await стр.goto(адрес, { waitUntil: "domcontentloaded", timeout: 45000 });
  await стр.waitForTimeout(6000);
  await стр.keyboard.press("Escape");
  // Чистка идёт дважды: часть баннеров подгружается отдельным скриптом и появляется
  // уже после первого прохода — снимок Submagic ловил плашку именно так.
  for (const проход of [0, 1]) {
  if (проход) await стр.waitForTimeout(2500);
  await стр.evaluate(() => {
    const окна = '[role=dialog],[aria-modal=true],[class*=cookie i],[id*=cookie i],[class*=consent i],[id*=consent i],[class*=privacy i],iframe[src*=consent i],iframe[src*=cookie i]';
    for (const у of document.querySelectorAll(окна)) у.remove();
    for (const у of document.querySelectorAll("body *")) {
      const с = getComputedStyle(у);
      if (с.position !== "fixed" && с.position !== "sticky") continue;
      const р = у.getBoundingClientRect();
      if (+с.zIndex > 40 && р.height > 250) { у.remove(); continue; }
      // Полоса, прилипшая к низу окна, — это cookie-баннер, даже когда он низкий и без
      // слова cookie в классах. Согласия не даём: элемент просто убирается со снимка.
      const прилип = р.bottom > innerHeight - 8 && р.height < innerHeight * 0.5;
      const полоса = прилип && р.width > innerWidth * 0.4;
      // Узкая карточка в углу тоже бывает баннером — её выдаёт собственный текст.
      const проcогласие = прилип && /cookie|куки|согласи|consent|privacy/i.test(у.innerText || "");
      if (полоса || проcогласие) у.remove();
    }
    for (const у of document.querySelectorAll("body *")) {
      const т = у.innerText || "";
      if (!/cookie|куки|соглас/i.test(т) || т.length > 700) continue;
      const свой = ![...у.children].some(р => /cookie|куки|соглас/i.test(р.innerText || ""));
      const р = у.getBoundingClientRect();
      if (свой && р.height > 60 && р.height < innerHeight * 0.6) у.remove();
    }
    // Виджеты согласия и чаты живут в своих фреймах: изнутри страницы их текст не виден,
    // поэтому мелкий фрейм в нижней половине экрана убирается по одному размеру и месту.
    for (const ф of document.querySelectorAll("iframe")) {
      const р = ф.getBoundingClientRect();
      if (р.width < 640 && р.height < 640 && р.top > innerHeight * 0.35) ф.remove();
    }
    document.documentElement.style.overflow = document.body.style.overflow = "auto";
    document.body.style.pointerEvents = "auto";
  });
  }
  await стр.waitForTimeout(1500);
  await стр.screenshot({ path: fileURLToPath(new URL(`./сайты/${имя}.png`, import.meta.url)) });
  console.log(имя, "снят");
} finally {
  await браузер.close();
}
