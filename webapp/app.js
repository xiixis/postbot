function ходРабот() {
  const э = document.getElementById("ход");
  const работы = С?.работы || [];
  // Пока открыт лист шагов, он и есть состояние: показывать то же самое
  // ещё и полоской сверху значит говорить одно и то же трижды.
  const влисте = !!document.querySelector(".sheet .work");
  э.hidden = !работы.length || влисте;
  э.innerHTML = работы.map(з => {
    const с = словами(з);
    return `<div class="полоска">
      <span class="spin"></span>
      <span class="что">${экр(с.что)}</span>
      <span class="этап">${экр(с.этап)}</span>
    </div>`;
  }).join("");

  // Пока что-то делается, состояние подтягивается само: иначе полоска
  // застынет на первом этапе и будет врать. Весь экран перерисовываем
  // только когда работа кончилась — иначе лента прыгала бы каждые три
  // секунды под руками.
  clearTimeout(опросХода);
  if (!работы.length) return;
  опросХода = setTimeout(async () => {
    try { С = await зов("/api/state"); } catch (e) { ходРабот(); return; }
    ходРабот();
    if (!(С.работы || []).length) { рисовать(); считать(); }
  }, 3000);
}

// Верхний экран это станки, а не лента постов. Внутрь станка заходят за
// сменой, из смены — в пост. Возврат всегда один и тот же, поэтому вкладки
// не нужны и заблудиться негде.
let экран = "цех", станок = null;

const АДРЕСА = {"цех": "shop", "сырьё": "stock"};

function идти(куда, код) {
  экран = куда; станок = код || null;
  // В адресе латиница: кириллицу браузер кодирует процентами, и ссылка
  // перестаёт узнаваться при возврате.
  location.hash = куда === "станок" ? "m-" + код : (АДРЕСА[куда] || "shop");
  рисовать();
  window.scrollTo(0, 0);
}

const НАЗАД = {станок: "Цех", "сырьё": "Цех"};

// ── родные кнопки телеграма ───────────────────────────────────────────
// «Назад» и главное действие рисует сам клиент. Они не уезжают со скроллом,
// не занимают место в вёрстке и выглядят так, как человек привык во всех
// остальных мини-приложениях. В обычном браузере их нет, и тогда работают
// наши собственные — поэтому те никуда не деваются, а только прячутся.
let нажатиеГлавной = null;

function главноеДело() {
  if (!С) return null;
  const спит = !С.mac?.alive;
  if (экран === "цех") {
    const пусто = (С.pipeline || []).reduce((а, н) => а + смена(н.код).пусто, 0);
    return {текст: пусто ? `✨ Собрать недостающее · ${пусто}` : "✨ Собрать пост",
            нельзя: спит, что: () => листЗаказа()};
  }
  if (экран === "станок") {
    const н = (С.pipeline || []).find(п => п.код === станок) || {};
    const с = смена(станок);
    if (н.режим !== "сам" && с.готово)
      return {текст: `📥 Забрать ${с.готово}`, нельзя: спит,
              что: () => document.querySelector("[data-забрать]")?.click()};
    return {текст: с.пусто ? `✨ Дособрать · ${с.пусто}` : "✨ Собрать ещё",
            нельзя: спит, что: () => листЗаказа({код: станок})};
  }
  return null;
}

function площадка() {
  if (!ТГ) return;
  // Пока открыт лист, «назад» означает «закрой лист», а не «уйди в цех»:
  // иначе экран под ним менялся, а сам лист оставался висеть.
  if (версия("6.1") && ТГ.BackButton) {
    (НАЗАД[экран] || document.querySelector(".sheet"))
      ? ТГ.BackButton.show() : ТГ.BackButton.hide();
  }
  const главная = ТГ.MainButton;
  if (!главная) return;
  // Пока открыт лист, главное действие принадлежит ему: две главные
  // кнопки разом — верный способ нажать не ту.
  const дело = document.querySelector(".sheet") ? null : главноеДело();
  document.body.dataset.родная = дело ? "да" : "";
  if (нажатиеГлавной) { главная.offClick(нажатиеГлавной); нажатиеГлавной = null; }
  if (!дело) return главная.hide();
  нажатиеГлавной = () => { тук("medium"); дело.что(); };
  главная.onClick(нажатиеГлавной);
  главная.setParams({text: дело.текст, color: "#c6ff34", text_color: "#171717",
                     is_active: !дело.нельзя, is_visible: true});
}

function рисовать() {
  document.body.dataset.экран = экран;
  ходРабот();
  const п = document.getElementById("путь");
  // Своя строка «назад» показывается всегда, даже когда телеграм рисует
  // свою кнопку. Две стрелки лучше, чем ни одной: на части клиентов родная
  // не появляется, и человек оказывался заперт внутри станка.
  п.hidden = !НАЗАД[экран];
  if (!п.hidden) п.innerHTML =
    `<button class="назад" data-идти="цех">← ${экр(НАЗАД[экран])}</button>`;
  const в = document.getElementById("view");
  в.innerHTML = экран === "станок" ? экранСтанок(станок)
              : экран === "сырьё" ? экранСырьё()
              : экранЦех();
  подвязать();
  площадка();
}

// ── связка ────────────────────────────────────────────────────────────────
// ── связка ────────────────────────────────────────────────────────────────
function подвязать() {
  // Создание переехало в лист: на главном экране остаётся очередь, а не
  // форма, которую заполняют раз в день.
  const сз = document.getElementById("создать");
  if (сз) сз.onclick = () => { тук(); листЗаказа(); };

  // Переходы вглубь и обратно. Один и тот же атрибут и в шапке, и в цехе.
  document.querySelectorAll("[data-идти]").forEach(э => э.onclick = () => {
    тук(); идти(э.dataset.идти);
  });

  // Станок целиком — дверь внутрь. Тумблер и вещи внутри него нажимаются
  // сами по себе, поэтому клик по ним до двери не доходит.
  document.querySelectorAll("[data-станок]").forEach(э => э.onclick = (с) => {
    if (с.target.closest("[data-вкл],[data-пост]")) return;
    тук(); идти("станок", э.dataset.станок);
  });

  // Автопилот. Переключается прямо из цеха: это главный рычаг, и прятать
  // его в настройках значит заставлять ходить туда каждый раз.
  document.querySelectorAll("[data-вкл]").forEach(э => э.onclick = async () => {
    тук("medium");
    try {
      const о = await зов("/api/pipeline", {net: э.dataset.вкл, what: "auto"});
      С.pipeline = о.pipeline || С.pipeline;
      рисовать(); считать();
    } catch (e) { сказать(e.message, true); }
  });

  document.querySelectorAll("[data-пост]").forEach(э => э.onclick = () => {
    const ид = +э.dataset.пост;
    const п = [...(С.drafts || []), ...(С.schedule || []), ...(С.history || [])]
      .find(x => x.id === ид);
    if (!п) return сказать("Пост не нашёлся, обновите приложение", true);
    тук();
    try { открыть(п); }
    catch (e) { сказать("Не открылось: " + e.message, true); }
  });

  // Пустая ячейка — это работа, а не отсутствие: нажатие ставит заказ.
  document.querySelectorAll("[data-пусто]").forEach(э => э.onclick = () => {
    тук(); листЗаказа({код: станок, час: э.dataset.пусто});
  });

  // Настройки станка живут внутри станка и открываются тем же листом.
  document.querySelectorAll("[data-нстр]").forEach(э => э.onclick = () => {
    тук(); листКонвейера(станок);
  });

  document.querySelectorAll("[data-факт-долой]").forEach(б => б.onclick = async () => {
    тук("medium");
    try {
      await зов("/api/facts/drop", {name: б.getAttribute("data-факт-долой")});
      С = await зов("/api/state");
      сказать("Забыл"); рисовать(); считать();
    } catch (e) { сказать(e.message, true); }
  });

  const фн = document.getElementById("факт-новый");
  if (фн) фн.onclick = () => {
    const э = лист(`
      <div class="t">Что ещё бот должен знать</div>
      <div class="hint">Короткое имя и значение. Из этого он и пишет:
        неверный факт разъедется по всем постам сразу.</div>
      <input type="text" id="ф-имя" placeholder="Каналов на ютубе"
             style="margin-top:.625rem">
      <input type="text" id="ф-знач" placeholder="5" style="margin-top:.375rem">
      <button class="btn primary wide" id="ф-сохр"
              style="margin-top:.75rem">Запомнить</button>`);
    э.querySelector("#ф-сохр").onclick = async () => {
      const имя = э.querySelector("#ф-имя").value.trim();
      const знач = э.querySelector("#ф-знач").value.trim();
      if (!имя || !знач) return сказать("Нужны и имя, и значение", true);
      тук("medium");
      try {
        await зов("/api/facts/save", {name: имя, value: знач});
        С = await зов("/api/state");
        э.remove(); сказать("🧠 Запомнил"); рисовать(); считать();
      } catch (e) { сказать(e.message, true); }
    };
  };

  // Забрать всё готовое одной кнопкой прямо из цеха: при ручной публикации
  // это и есть ежедневная работа, и ходить за ней внутрь станка незачем.
  document.querySelectorAll("[data-забрать]").forEach(б => б.onclick = async (с) => {
    с.stopPropagation();
    const код = б.getAttribute("data-забрать");
    const готовы = смена(код).ячейки.filter(я => я.п && !я.вышло).map(я => я.п);
    if (!готовы.length) return сказать("Забирать нечего", true);
    тук("medium");
    б.disabled = true;
    let взято = 0;
    for (const п of готовы) {
      б.textContent = `⏳ ${взято + 1} из ${готовы.length}…`;
      try {
        await работа("/api/take", {id: п.id, куда: код}, ШАГИ_ФАЙЛЫ);
        взято++;
      } catch (e) { сказать(e.message, true); break; }
    }
    б.disabled = false;
    if (взято) сказать(`📥 ${взято} в чате, папки открыты на маке`);
    рисовать();
  });

  // Повтор после сбоя. Станок встал — вернуть его в строй должно быть
  // одним нажатием там же, где написано, что он встал.
  document.querySelectorAll("[data-станок-снова]").forEach(б => б.onclick = async (с) => {
    с.stopPropagation();
    const код = б.getAttribute("data-станок-снова");
    const готовы = смена(код).ячейки.filter(я => я.п && !я.вышло).map(я => я.п);
    if (!готовы.length) return сказать("Повторять нечего", true);
    тук("medium");
    try {
      await довести(await зов("/api/publish", {id: готовы[0].id}));
      сказать("🚀 Ушло");
      С = await зов("/api/state"); рисовать(); считать();
    } catch (e) { сказать(e.message, true); }
  });

  // Одобрить — значит дать посту час в смене. Ни времени в расписании, ни
  // публикации это не включает: в ручном режиме выкладывает человек.
  document.querySelectorAll("[data-одобрить]").forEach(б => б.onclick = async (с) => {
    с.stopPropagation();
    тук("medium");
    б.disabled = true;
    try {
      const о = await зов("/api/approve", {
        id: +б.getAttribute("data-одобрить"),
        час: б.getAttribute("data-час"),
      });
      С = о.state || С;
      сказать(`🕑 В смену на ${б.getAttribute("data-час")}`);
      рисовать(); считать();
    } catch (e) { сказать(e.message, true); б.disabled = false; }
  });

  const доб = document.getElementById("дособрать");
  if (доб) доб.onclick = () => { тук(); листЗаказа({код: станок}); };

  const зб = document.getElementById("забрать-все");
  if (зб) зб.onclick = async () => {
    const с = смена(станок);
    const готовы = с.ячейки.filter(я => я.п && !я.вышло).map(я => я.п);
    if (!готовы.length) return;
    тук("medium");
    зб.disabled = true;
    let взято = 0;
    for (const п of готовы) {
      зб.textContent = `⏳ ${взято + 1} из ${готовы.length}…`;
      try {
        await работа("/api/take", {id: п.id, куда: станок}, ШАГИ_ФАЙЛЫ);
        взято++;
      } catch (e) { сказать(e.message, true); break; }
    }
    зб.disabled = false; зб.textContent = `📥 Забрать ${готовы.length}`;
    if (взято) сказать(`📥 ${взято} в чате, папки открыты на маке`);
  };

  const н = document.getElementById("go-week");
  if (н) н.onclick = () => { тук(); планЛист(); };
  const уб = document.getElementById("go-clean");
  if (уб) уб.onclick = async () => {
    тук();
    уб.disabled = true; уб.textContent = "⏳ Убираю…";
    try {
      await довести(await зов("/api/cleanup", {}));
      сказать("🧹 Прибрался");
    } catch (e) { сказать(e.message, true); }
    уб.disabled = false; уб.textContent = "🧹 Прибраться";
  };

  const заметка = document.getElementById("заметка");
  const вкопилку = document.getElementById("в-копилку");
  if (вкопилку) вкопилку.onclick = async () => {
    const текст = (заметка.value || "").trim();
    if (!текст) return сказать("Напишите заметку", true);
    тук("medium");
    вкопилку.disabled = true;
    try {
      const о = await зов("/api/ideas/add", {text: текст});
      С = о.state || С;
      заметка.value = "";
      const обновлено = Object.entries(о.facts_updated || {});
      сказать(обновлено.length
        ? "📊 Обновил: " + обновлено.map(([и, з]) => `${и} ${з}`).join(", ")
        : "💡 В копилке");
      рисовать(); считать();
    } catch (e) { сказать(e.message, true); }
    вкопилку.disabled = false;
  };
  document.querySelectorAll("[data-идея]").forEach(б => б.onclick = () => {
    тук(); листСоздания((С.ideas || []).find(и => и.id == б.dataset.идея)?.text || "");
  });
  document.querySelectorAll("[data-взять-идею]").forEach(б => б.onclick = () => {
    тук(); листЗаказа({тема: б.getAttribute("data-взять-идею")});
  });

  document.querySelectorAll("[data-убрать-идею]").forEach(б => б.onclick = async () => {
    тук();
    try {
      const о = await зов("/api/ideas/drop", {id: +б.getAttribute("data-убрать-идею")});
      С.ideas = о.ideas; рисовать();
    } catch (e) { сказать(e.message, true); }
  });

  document.querySelectorAll("[data-open]").forEach(б => б.onclick = () => {
    const все = [...(С.schedule || []), ...(С.history || []), ...(С.drafts || [])];
    const п = все.find(x => x.id == б.dataset.open);
    if (п) { тук(); открыть(п); }
  });
  const п = document.getElementById("поиск");
  if (п) п.oninput = () => { искомое = п.value; };
}

// Лист создания: тип поста, рубрика и тема. Открывается кнопкой, а не висит
// на главном экране.
// Заказ станку. Не «создай пост», а «закрой мне столько ячеек»: разница
// видна на пятой публикации за день, когда собирать по одной и каждую
// руками ставить на время — десять действий вместо одного.
// ВНИМАНИЕ на составные имена: dataset убирает дефис, только если следом
// идёт латинская строчная буква. «data-з-станок» остаётся ключом
// «з-станок», и dataset.зСтанок равен undefined. Такие атрибуты читаем
// через getAttribute.
function считать() {
  const ч = document.getElementById("ch");
  ч.textContent = С.channel || "канал не задан";
  ч.classList.toggle("main", С.channels?.["выбран"] === "основной");
  const жив = С.mac?.alive;
  const м = document.getElementById("mac");
  м.innerHTML = жив ? '💻<span class="слово"> мак на связи</span>'
                    : '💤<span class="слово"> мак спит</span>';
  м.classList.toggle("off", !жив);
  м.title = жив ? "Мак включён, всё доступно"
                : "Мак выключен. Сочинять и публиковать нельзя: "
                  + "сессия аккаунта лежит на нём";
  const к = document.getElementById("звук");
  к.textContent = С.silent ? "🔕" : "🔔";
  к.classList.toggle("off", !!С.silent);
  к.title = С.silent ? "Все посты уходят без звука" : "Посты со звуком, ночью тихо";
}

document.getElementById("gear").onclick = () => { тук(); настройки(); };
document.getElementById("ch").onclick = () => { тук(); каналы(); };
document.getElementById("звук").onclick = async () => {
  тук("medium");
  try {
    const о = await зов("/api/sound");
    С = о.state; считать();
    сказать(о.silent ? "🔕 Посты уходят без звука"
                     : "🔔 Звук включён, ночью всё равно тихо");
  } catch (e) { сказать(e.message, true); }
};

ТГ?.BackButton?.onClick?.(() => { тук(); if (!закрытьЛист()) идти("цех"); });

// Escape — то же самое для тех, кто открыл приложение в браузере.
addEventListener("keydown", с => {
  if (с.key !== "Escape") return;
  if (!закрытьЛист() && экран !== "цех") идти("цех");
});

(async () => {
  try {
    С = await зов("/api/state");
    // Ссылка вида #станок-tiktok открывает станок сразу: её удобно держать
    // на телефоне под рукой.
    const адрес = decodeURIComponent(location.hash.slice(1));
    if (адрес.startsWith("m-")) { экран = "станок"; станок = адрес.slice(2); }
    else if (адрес === "stock") экран = "сырьё";
    считать(); рисовать();
  } catch (e) {
    document.getElementById("view").innerHTML =
      `<div class="empty"><b>Не пускает</b>${экр(e.message)}</div>`;
  }
})();
