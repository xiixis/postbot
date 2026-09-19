// Снимок ЗНАКА сервиса, а не страницы целиком: node снять-знак.mjs <имя> <адрес>
//   → снимки/<имя>.png, квадрат с прозрачным фоном подложки.
//
// Почему не снимок первого экрана, как в `подборка-сайтов/снять.mjs`: там кадр
// показывает сайт целиком и живёт на пол-кадра. Здесь плитка в готовом кадре всего
// ~300 px, и страница 1440×900, ужатая в неё, превращается в кашу — проверено
// 19.09.2026 на Figma и HeyGen: логотип в углу мелкий, вокруг случайный баннер.
// Поэтому снимается именно элемент знака в шапке, крупно и с полями.
//
// Базу playwright и Chrome ищем перебором — жёсткие пути уже один раз протухли.
import { createRequire } from "module";
import { fileURLToPath } from "url";
import { existsSync, readdirSync } from "fs";
import { join } from "path";
import { homedir } from "os";

function найти(корень, годится) {
  if (!existsSync(корень)) return null;
  return readdirSync(корень).sort().reverse().map(и => join(корень, и)).find(годится) ?? null;
}

const база = найти(join(homedir(), ".npm/_npx"), п => existsSync(join(п, "node_modules/playwright-core")));
if (!база) { console.error("нет playwright-core: `npx playwright --version`"); process.exit(1); }
const require = createRequire(join(база, "package.json"));
const { chromium } = require("playwright-core");

const версия = найти(join(homedir(), ".cache/chrome-headless-shell/chrome-headless-shell"),
                     п => existsSync(join(п, "chrome-headless-shell-mac-arm64/chrome-headless-shell")));
if (!версия) { console.error("нет chrome-headless-shell"); process.exit(1); }
const CHROME = join(версия, "chrome-headless-shell-mac-arm64/chrome-headless-shell");

const [имя, адрес] = process.argv.slice(2);

// Настоящий User-Agent: со стандартным headless часть сайтов сразу отдаёт капчу.
const UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " +
           "(KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36";

const браузер = await chromium.launch({ executablePath: CHROME, headless: true });
try {
  const стр = await браузер.newPage({ viewport: { width: 1440, height: 900 },
                                      deviceScaleFactor: 3, userAgent: UA });
  await стр.goto(адрес, { waitUntil: "domcontentloaded", timeout: 45000 });
  await стр.waitForTimeout(5000);

  // Капчу узнаём по тексту: снимать её знак бессмысленно, лучше честно сказать.
  const текст = (await стр.evaluate(() => document.body.innerText || "")).slice(0, 400);
  if (/verify you are human|security verification|checking your browser|just a moment/i.test(текст)) {
    console.log(`${имя}: КАПЧА — знак не снят`);
    process.exit(2);
  }

  // Ищем знак: заметная картинка или svg в шапке. Если шапки как таковой нет или
  // знак лежит вне её (так у Figma — проверено 19.09.2026), ищем по всей верхней
  // полосе страницы: логотип всё равно стоит в первых 200 px сверху.
  const найденный = await стр.evaluate(() => {
    const собрать = узлы => {
      const к = [];
      for (const у of узлы) {
        const р = у.getBoundingClientRect();
        if (р.width < 24 || р.height < 16 || р.top > 220 || р.top < -10) continue;
        if (р.width > 460) continue;                       // это баннер, не знак
        if (р.left > 700) continue;                        // правый край шапки — это кнопки входа
        к.push({ р, у });
      }
      return к;
    };
    // Сперва самое надёжное: картинка внутри ссылки на корень сайта либо с
    // подписью про логотип. «Самый левый верхний svg» этого не заменяет — там
    // сплошь и рядом кнопка меню: у Gemini так снялась стрелка «раскрыть»,
    // у Figma — иконка инструмента вместо знака (проверено 19.09.2026).
    const корневые = [...document.querySelectorAll(
      'a[href="/"] svg, a[href="/"] img, [aria-label*=logo i] svg, [aria-label*=logo i] img,'
      + '[class*=logo i] svg, [class*=logo i] img, [data-testid*=logo i] svg, [data-testid*=logo i] img')];
    let кандидаты = собрать(корневые);
    if (!кандидаты.length) {
      const шапки = [...document.querySelectorAll("header, nav, [class*=header i], [class*=navbar i]")];
      кандидаты = собрать(шапки.flatMap(ш => [...ш.querySelectorAll("svg, img")]));
    }
    if (!кандидаты.length) кандидаты = собрать(document.querySelectorAll("svg, img"));
    if (!кандидаты.length) return null;
    // Из найденных берём самый широкий: знак шире кнопки-иконки почти всегда,
    // и именно этим отличается от стрелки «раскрыть» или гамбургера рядом.
    // Прежняя сортировка «самый левый из верхних» здесь была бы вредна: она
    // перебивала выбор и возвращала ту самую кнопку слева от логотипа.
    кандидаты.sort((а, б) => (б.р.width - а.р.width) || (а.р.top - б.р.top));
    const { р } = кандидаты[0];
    кандидаты[0].у.setAttribute("data-знак", "1");
    return { x: р.left, y: р.top, w: р.width, h: р.height };
  });

  if (!найденный) { console.log(`${имя}: знак не найден`); process.exit(3); }

  // Квадрат вокруг знака с полями: в кадре плитка квадратная, и знак должен дышать.
  // Поле умеренное: при 0.35 в квадрат снизу попадала чужая баннерная полоса (HeyGen).
  const поле = Math.max(найденный.w, найденный.h) * 0.22;
  const сторона = Math.max(найденный.w, найденный.h) + поле * 2;
  const cx = найденный.x + найденный.w / 2, cy = найденный.y + найденный.h / 2;
  const clip = { x: Math.max(0, cx - сторона / 2), y: Math.max(0, cy - сторона / 2),
                 width: сторона, height: сторона };

  const куда = fileURLToPath(new URL(`./снимки/${имя}.png`, import.meta.url));
  await стр.screenshot({ path: куда, clip });
  console.log(`${имя}: знак снят ${Math.round(сторона)}×${Math.round(сторона)}`);
} finally {
  await браузер.close();
}
