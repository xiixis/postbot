// Рамка для стенда. Держит приложение в окне ровно 390 пикселей и заодно
// собирает всё, на чём оно спотыкается.
//
// Собирает нарочно: разбор скрипта («node --check») говорит только, что файл
// не сломан. Обращение к несуществующей переменной внутри листа он пропускает,
// а лист от этого не открывается вовсе — и в постботе это уже случалось.
//
// Адрес: #раздел или #раздел+пост, где «+пост» значит «открой первый пост
// в списке» — это самый ходовой лист и самый дорогой, если он упал.

const части = decodeURIComponent(location.hash.slice(1)).split("+");
const раздел = части[0] || "today";
const открыть_пост = части.includes("пост");

const беды = [];
const рамка = document.getElementById("телефон");
const доска = document.getElementById("беды");

function записать(что) {
  беды.push(String(что));
  if (доска) доска.textContent = "БЕДЫ: " + JSON.stringify(беды);
}

rамка_готова();

function rамка_готова() {
  рамка.addEventListener("load", () => {
    const окно = рамка.contentWindow;
    окно.addEventListener("error", с =>
      записать(`${с.message} (${(с.filename || "").split("/").pop()}:${с.lineno})`));
    окно.addEventListener("unhandledrejection", с =>
      записать("необработанный отказ: " + (с.reason && с.reason.message || с.reason)));
    if (доска) доска.textContent = "БЕДЫ: []";
    if (открыть_пост) setTimeout(() => {
      try {
        const строка = окно.document.querySelector("[data-open],[data-пост]");
        if (!строка) return записать("нечего открыть: строк поста нет");
        строка.click();
        setTimeout(() => {
          if (!окно.document.querySelector(".sheet"))
            записать("лист поста не открылся");
        }, 400);
      } catch (e) { записать("не смог нажать: " + e.message); }
    }, 1200);
  });
  рамка.src = "index.html?key=%D1%81%D1%82%D0%B5%D0%BD%D0%B4#"
            + encodeURIComponent(раздел);
}
