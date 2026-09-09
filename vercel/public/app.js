const ТГ = window.Telegram?.WebApp;
const AUTH = ТГ?.initData || "";
// Вне телеграма подписи нет, и тогда пропуском служит ключ из адреса.
// Он же остаётся в браузере, чтобы не таскать его в ссылке при каждом заходе.
const КЛЮЧ = (new URLSearchParams(location.search).get("key")
              || localStorage.getItem("ключ") || "");
if (КЛЮЧ) { try { localStorage.setItem("ключ", КЛЮЧ); } catch (e) {} }
let С = null, рубрика = null, тема = "";

// Мини-приложение живёт внутри телеграма, и половина его удобства — это
// не наша вёрстка, а то, что даёт сама площадка. Берём то, что есть, и
// молча обходимся без остального: у людей разные версии клиента.
const версия = н => !!ТГ?.isVersionAtLeast?.(н);

if (ТГ) {
  ТГ.ready(); ТГ.expand();
  ТГ.setHeaderColor?.("#0f0f0f");
  ТГ.setBackgroundColor?.("#0f0f0f");
  if (версия("7.10")) ТГ.setBottomBarColor?.("#0f0f0f");
  // Свайп вниз по умолчанию закрывает приложение. У нас длинный цех и
  // длинные листы: пролистывая их, человек регулярно выкидывал себя в чат.
  if (версия("7.7")) ТГ.disableVerticalSwipes?.();
  // Отступы под чёлку и полосу жеста считает сам телеграм: в вебвью
  // env(safe-area-inset) врёт.
  const отступы = () => {
    const н = ТГ.contentSafeAreaInset || {}, б = ТГ.safeAreaInset || {};
    document.documentElement.style.setProperty(
      "--низ", `${(н.bottom || 0) + (б.bottom || 0)}px`);
    document.documentElement.style.setProperty(
      "--верх", `${(н.top || 0) + (б.top || 0)}px`);
  };
  if (версия("8.0")) {
    отступы();
    ТГ.onEvent?.("safeAreaChanged", отступы);
    ТГ.onEvent?.("contentSafeAreaChanged", отступы);
  }
}
const тук = (в="light") => ТГ?.HapticFeedback?.impactOccurred?.(в);

async function зов(путь, тело) {
  const о = await fetch(путь, {
    method: "POST",
    headers: {"Content-Type": "application/json", "X-Init-Data": AUTH},
    body: JSON.stringify(КЛЮЧ ? {...(тело || {}), key: КЛЮЧ} : (тело || {}))
  });
  const д = await о.json().catch(() => ({error: "сервер молчит"}));
  if (!о.ok) throw new Error(д.error || "не вышло");
  return д;
}

// Всплывашка сообщает об итоге действия, и человек с чтецом экрана должен
// его услышать: без aria-live она для него просто не существует.
function сказать(текст, плохо) {
  document.querySelector(".toast")?.remove();
  const э = document.createElement("div");
  э.className = "toast" + (плохо ? " bad" : "");
  э.setAttribute("role", плохо ? "alert" : "status");
  э.setAttribute("aria-live", плохо ? "assertive" : "polite");
  э.textContent = текст;
  document.body.appendChild(э);
  setTimeout(() => э.remove(), 2600);
}

// Карточка из хранилища открывается напрямую, своя, с диска, только по подписи
const кар = п => !п.image ? null
  : п.image.startsWith("http") ? п.image
  : п.image + "?auth=" + encodeURIComponent(AUTH)
    + (КЛЮЧ ? "&key=" + encodeURIComponent(КЛЮЧ) : "");
// Одинарная кавычка здесь не для красоты: атрибуты в шаблонах сегодня в
// двойных, но стоит написать где-то class='...' — и незакрытая защита
// откроет дыру молча, без единой ошибки в консоли.
const экр = т => (т || "").replace(/[&<>"']/g,
  с => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#x27;"}[с]));

// ── экраны ────────────────────────────────────────────────────────────────
// Пропорции у площадок называются по-своему; в настройках станка человеку
// нужны цифры, а не наши внутренние клички.
const ВИДЫ_ФОРМАТА = {"квадрат": "1:1", "широкий": "16:9", "3к4": "3:4",
                      "вертикаль": "9:16"};

const ВИДЫ_РАБОТ = {
  "заказ": "🎠 Собираю заказ",
  "карусель": "🎠 Собираю карусель", "пост": "📝 Сочиняю пост",
  "переписать": "✏️ Переписываю", "перерисовать": "🎨 Перерисовываю кота",
  "неделя": "📅 Набиваю план на неделю", "обновить": "🔄 Обновляю",
  "запланировать": "🕑 Ставлю в план", "опубликовать": "🚀 Публикую",
};
let опросХода = null;

// Что делает работа, человеческими словами. «заказ · 2 из 3 · слайд 4 из 9»
// само по себе ничего не значит; «вторая из трёх, слайд 4 из 9» — значит.
function словами(з) {
  const части = String(з.этап || "").split("·").map(с => с.trim()).filter(Boolean);
  const партия = части.length > 1 ? части.shift() : "";
  const этап = части.join(" · ") || "начинаю";
  const куда = з.куда ? " для " + чистоеИмя(площадкаИмя(з.куда)) : "";
  const сколько = з.сколько > 1 ? ` · ${з.сколько} штуки` : "";
  return {
    что: (ВИДЫ_РАБОТ[з.вид] || з.вид) + куда,
    этап: (партия ? партия + " · " : "") + этап,
    подпись: сколько,
  };
}
const площадкаИмя = код => ((С.pipeline || []).find(п => п.код === код) || {}).имя
                          || код || "";

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

// ── станок ────────────────────────────────────────────────────────────
// Внутри площадки всё её: смена по часам, очередь и её же настройки.
// «Пять в день» — свойство TikTok, а не приложения, и искать его в общем
// списке настроек значит каждый раз вспоминать, чьё оно.
function экранСтанок(код) {
  const н = (С.pipeline || []).find(п => п.код === код);
  if (!н) return `<div class="пусто"><b>Станка нет</b>Вернитесь в цех.</div>`;
  const руками = н.режим !== "сам";
  const с = смена(код);
  const без_ячейки = с.ждут || [];
  const вышли = (С.history || []).filter(п => ушёл(п, код)).slice(0, 6);

  const ячейки = с.ячейки.map(я => я.п ? `
    <div class="ячейка${я.вышло ? " прошла" : ""}" data-пост="${я.п.id}">
      <span class="час">${экр(я.ч)}</span>
      ${кар(я.п) ? `<img src="${кар(я.п)}" alt="Превью: ${экр(я.п.title)}"
                 width="30" height="40" loading="lazy">` : ""}
      <span class="т">${экр(я.п.title)}</span>
      <span class="сост${я.вышло ? "" : я.одобрен ? " одобрен" : " готов"}">${я.вышло
        ? "вышло" + (я.п.views ? " · 👁 " + я.п.views : "")
        : я.одобрен ? (руками ? "забрать" : "одобрен") : "в плане"}</span>
    </div>` : `
    <div class="ячейка пуста${вМинутах(я.ч) <= вМинутах(С.now) ? " прошла" : ""}"
         ${вМинутах(я.ч) > вМинутах(С.now) ? `data-пусто="${экр(я.ч)}"` : ""}
      >${экр(я.ч)} · ${вМинутах(я.ч) <= вМинутах(С.now)
        ? "прошла впустую" : "пусто · собрать"}</div>`
  ).join("") || `<div class="ячейка пуста">часы выхода не заданы</div>`;

  return `
    <div class="станок" style="margin-bottom:1rem">
      <div class="гол">
        <span class="зн" style="font-size:1.625rem">${экр(значок(н.имя))}</span>
        <div>
          <b style="font-size:1.0625rem">${экр(чистоеИмя(н.имя))}</b>
          <div class="низ">${код === "tiktok" && С.tiktok?.connected
            ? экр("@" + (С.tiktok.nick || "")) + " · подключён"
            : код === "телеграм" ? экр(С.channel || "канал не задан")
            : (н.вкл ? "автопилот включён" : "автопилот выключен")}</div>
        </div>
        <div class="тумблер${н.вкл ? " on" : ""}" data-вкл="${н.код}"
             title="Автопилот"><i></i></div>
      </div>
    </div>

    <div class="lbl">Смена сегодня · ${с.вышло} вышло из
      ${(н.часы || []).length}</div>
    ${ячейки}

    <div class="row" style="margin-top:.625rem">
      ${руками && с.готово ? `<button class="btn primary" id="забрать-все"
        >📥 Забрать ${с.готово}</button>` : ""}
      <button class="btn ghost" id="дособрать" ${С.mac?.alive ? "" : "disabled"}
        >✨ ${с.пусто ? "Дособрать · " + с.пусто : "Собрать ещё"}</button>
    </div>

    ${без_ячейки.length ? `
      <div class="lbl свер">На одобрении · ${без_ячейки.length}</div>
      <div class="hint" style="margin:-.25rem 0 .5rem">Пока пост не одобрен,
        он в смену не встаёт. Выберите ему час — или откройте и посмотрите.</div>
      ${без_ячейки.map(п => `
        <div class="карточка-ждёт">
          <div class="верхушка" data-пост="${п.id}">
            ${кар(п) ? `<img src="${кар(п)}" alt="Превью: ${экр(п.title)}"
                 width="44" height="59" loading="lazy">` : ""}
            <span class="т"><span class="номер">№${п.id}</span> ${экр(п.title)}</span>
            <span class="стр">›</span>
          </div>
          <div class="часы-выбор">${(с.ячейки.filter(я => !я.п)
            .map(я => `<button data-одобрить="${п.id}" data-час="${экр(я.ч)}"
              >${экр(я.ч)}</button>`).join("")) ||
            '<span class="муть" style="font-size:.75rem">свободных ячеек нет</span>'}
          </div>
        </div>`).join("")}` : `
      <div class="hint" style="margin-top:.625rem">Всё одобренное разложено
        по ячейкам выше. Ничего не ждёт.</div>`}

    <div class="lbl свер">Настройки станка</div>
    <div class="нстр" data-нстр="режим">Публикует
      <span class="знч">${руками ? "выкладываете вы" : "станок сам"}</span>
      <span class="стр">›</span></div>
    <div class="нстр" data-нстр="часы">Сколько в день
      <span class="знч">${(н.часы || []).length}</span><span class="стр">›</span></div>
    <div class="нстр" data-нстр="дней">Запас
      <span class="знч">на ${н.дней} дн. · ${н.запас} шт.</span>
      <span class="стр">›</span></div>
    <div class="нстр" data-идти="сырьё">Угол следующей
      <span class="знч">${экр(н.угол || "по кругу")}</span>
      <span class="стр">›</span></div>
    <div class="нстр" data-нстр="формат">Формат
      <span class="знч">${экр(ВИДЫ_ФОРМАТА[н.формат] || н.формат || "—")}${
        н.файл ? " · " + экр(н.файл.toUpperCase()) : ""}${
        н.ширина ? " " + н.ширина : ""}</span>
      <span class="стр">›</span></div>
    <div class="нстр" data-нстр="аккаунт">Аккаунт
      <span class="знч">${код === "tiktok"
        ? экр(С.tiktok?.nick ? "@" + С.tiktok.nick : "не подключён")
        : экр(С.channel || "канал не задан")}</span>
      <span class="стр">›</span></div>

    <div class="lbl свер">Часы выхода</div>
    <div class="часы-станка">${(н.часы || []).map(ч =>
      `<span>${экр(ч)}</span>`).join("")}<span class="плюс"
      data-нстр="часы">＋</span></div>

    ${вышли.length ? `
      <div class="lbl свер">Уже вышли</div>
      ${вышли.map(п => строка(п)).join("")}` : ""}`;
}

// ── сырьё ─────────────────────────────────────────────────────────────
// Идеи, углы и факты — это не «настройки», а материал, из которого станок
// делает посты. Когда карусели выходят похожими друг на друга, чинить надо
// здесь, и путь сюда должен быть очевиден прямо из цеха.
function экранСырьё() {
  const идеи = С.ideas || [];
  const факты = С.facts || [];
  const углы = С.углы || [];
  const текущий = ((С.pipeline || []).find(п => п.код === "tiktok") || {}).угол;
  const место = углы.indexOf(текущий);

  return `
    <div class="lbl">Копилка · ${идеи.length}</div>
    <div class="идея">
      <label for="заметка" class="sr">Заметка в копилку</label>
      <input type="text" id="заметка" style="flex:1" autocomplete="off"
             placeholder="Ссылка, мысль или «каналов стало 6»…">
      <button class="btn" id="в-копилку" aria-label="Записать в копилку">💡</button>
    </div>
    <div class="hint">Голосовое прямо боту в чат попадает сюда же: он
      расшифрует и запишет.</div>
    ${идеи.map(и => `
      <div class="идея" style="margin-top:.375rem">
        <button class="взять" data-взять-идею="${экр(и.text)}">${экр(и.text)}</button>
        <button class="выкинуть" data-убрать-идею="${и.id}"
                aria-label="Выкинуть идею">✖️</button>
      </div>`).join("")}

    ${углы.length ? `
      <div class="lbl свер">Углы · идут по кругу</div>
      <div class="hint" style="margin:-.25rem 0 .5rem">Чтобы карусели не
        приедались, станок берёт следующий угол по кругу и не повторяется,
        пока не пройдёт все ${углы.length}.</div>
      <div class="углы">${углы.map((у, и) => `<span class="${
        у === текущий ? "on" : место >= 0 && и < место ? "был" : ""
      }">${экр(у)}</span>`).join("")}</div>` : ""}

    <div class="lbl свер">Что бот знает о проекте · ${факты.length}</div>
    ${факты.length ? `<div class="факты">${факты.map(ф => `
      <div style="display:flex;gap:.625rem;align-items:flex-start">
        <div style="flex:1;min-width:0">
          <div class="к">${экр(ф.name)}</div>
          <div class="з">${экр(ф.value)}</div>
        </div>
        <button class="выкинуть" data-факт-долой="${экр(ф.name)}"
          aria-label="Забыть факт «${экр(ф.name)}»">✖️</button></div>`).join("")}</div>`
      : `<div class="пусто" style="padding:1.25rem 1rem"><b>Пусто</b>
           Бот пишет вслепую. Расскажите ему про проект.</div>`}
    <button class="btn wide ghost" id="факт-новый"
            style="margin-top:.5rem">＋ Добавить факт</button>`;
}

// ── смена станка ──────────────────────────────────────────────────────
const назначен = (п, код) => (п.where || []).some(в => в.код === код && в.выбрана);
const ушёл = (п, код) => !!(((п.card || {})["выложено"] || {})[код])
                       || (код === "телеграм" && !!п.link);
const сегодня = с => (с || "").startsWith("сегодня");
const часПоста = п => ((п.when || "").split(" в ").pop() || "").trim();
const вМинутах = ч => {
  const м = /(\d{1,2}):(\d{2})/.exec(ч || "");
  return м ? +м[1] * 60 + +м[2] : -1;
};

// Часы берутся из настроек станка, в них раскладывается запланированное.
// Вышедшее садится в ближайшую свободную ячейку: точная минута выхода не
// важна, важно, что ячейка отработана и дырой не считается.
function смена(код) {
  const н = (С.pipeline || []).find(п => п.код === код) || {};
  const план = (С.schedule || []).filter(п => сегодня(п.when) && назначен(п, код));
  const вышли = (С.history || []).filter(п => сегодня(п.published) && ушёл(п, код));
  const занятые = new Map(план.map(п => [часПоста(п), п]));
  const ячейки = (н.часы || []).map(ч => {
    const п = занятые.get(ч);
    if (п) занятые.delete(ч);
    return {ч, п, вышло: false};
  });
  for (const в of вышли) {
    const когда = вМинутах((в.published || "").split(" в ").pop());
    let лучшая = -1, ближе = 1e9;
    ячейки.forEach((я, и) => {
      if (я.п) return;
      const д = Math.abs(вМинутах(я.ч) - когда);
      if (д < ближе) { ближе = д; лучшая = и; }
    });
    if (лучшая >= 0) { ячейки[лучшая].п = в; ячейки[лучшая].вышло = true; }
  }
  // Пост, поставленный на час, которого в настройках нет, всё равно виден:
  // прятать запланированное значит врать про день.
  for (const [ч, п] of занятые) ячейки.push({ч, п, вышло: false});
  ячейки.sort((а, б) => вМинутах(а.ч) - вМинутах(б.ч));

  // В смену пост попадает только после одобрения. Раньше свежие черновики
  // садились в ячейки сами, и человек видел день закрытым, хотя ничего
  // ещё не смотрел: смена показывала намерение, а не решение.
  const свои = (С.drafts || []).filter(п => назначен(п, код));
  const сейчас = вМинутах(С.now);
  // Одобренный пост занимает свою ячейку. Отметка стоит на самом посте:
  // так она переживает перезагрузку и видна и боту, и приложению.
  const одобрен = п => ((п.card || {})["ячейка"] || "").trim();
  for (const я of ячейки) {
    if (я.п) continue;
    const п = свои.find(x => одобрен(x) === я.ч);
    if (п) { я.п = п; я.одобрен = true; }
  }
  const свободные = свои.filter(п => !одобрен(п) || !ячейки.some(я => я.п === п));

  return {ячейки, вышло: вышли.length,
          готово: ячейки.filter(я => я.п && !я.вышло).length,
          ждут: свободные,
          пусто: ячейки.filter(я => !я.п).length,
          следующая: (ячейки.find(я => !я.п && вМинутах(я.ч) > сейчас) || {}).ч};
}

// ── цех ───────────────────────────────────────────────────────────────
function экранЦех() {
  const черновики = С.drafts || [];
  const свод = (С.pipeline || []).map(н =>
    ({н, с: смена(н.код), очередь: черновики.filter(п => назначен(п, н.код))}));
  const вышло = свод.reduce((а, с) => а + с.с.вышло, 0);
  const готовы = свод.reduce((а, с) => а + с.с.готово, 0);
  const пусто = свод.reduce((а, с) => а + с.с.пусто, 0);
  const охват = ((С.reach || [])[0] || {}).avg;
  const ничьи = черновики.filter(п => !(п.where || []).some(в => в.выбрана));

  // Состояние станка живёт в самой карточке, а не полоской над экраном:
  // в цехе ломается машина, и говорить надо про машину — что с ней,
  // почему и что вернёт её в строй.
  const станки = свод.map(({н, с, очередь}) => {
    // Только своя работа. Раньше карточка обоих станков зажигалась на любой
    // генерации, и заказ для TikTok подсвечивал заодно телеграм.
    const работа = (С.работы || []).find(р =>
      ["заказ", "карусель", "новый"].includes(р.вид) &&
      (!р.куда || р.куда === н.код));
    const беда = (С.беды || []).find(б => !б.куда || б.куда === н.код);
    const спит = !С.mac?.alive;
    const закрыта = н.вкл && !с.пусто && !с.готово && с.вышло;
    const руками = н.режим !== "сам";
    const состояние =
      спит ? {класс: "обесточен", зн: "💤", т: "Обесточен",
              п: "Мак выключен: собирать, рисовать и забирать файлы нельзя."}
    : работа ? {класс: "работает", зн: "",
                т: словами(работа).что.replace(/^\S+\s/, ""),
                п: экр(словами(работа).этап)}
    : беда ? {класс: "встал", зн: "🛑", т: "Встал",
              п: экр(беда.беда)}
    : закрыта ? {класс: "", зн: "🌙", т: "Смена закрыта",
                 п: `${с.вышло} из ${(н.часы || []).length} вышло. Следующая партия соберётся к утру.`}
    : null;

    return `
    <div class="станок${н.вкл ? "" : " спит"}${состояние ? " " + состояние.класс : ""}"
         data-станок="${н.код}">
      <div class="гол">
        <span class="зн">${экр(значок(н.имя))}</span>
        <div>
          <b>${экр(чистоеИмя(н.имя))}</b>
          <div class="низ">${н.вкл ? "пишет сам" : "спит"} ·
            ${руками ? "выкладываете вы" : "публикует сам"} ·
            ${н.часов} в день</div>
        </div>
        <div class="тумблер${н.вкл ? " on" : ""}" data-вкл="${н.код}"
             title="Автопилот"><i></i></div>
      </div>

      ${состояние ? `<div class="сост-станка">
        ${состояние.зн ? `<span class="зн">${состояние.зн}</span>`
                       : '<span class="spin"></span>'}
        <div><b>${состояние.т}</b><span>${состояние.п}</span></div>
      </div>` : ""}

      <div class="шкала">${(() => {
        // Первая пустая ячейка мигает, пока станок работает: труд виден
        // там же, где виден его итог, и отдельной полоски для этого не надо.
        let первая_пустая = работа
          ? с.ячейки.findIndex(я => !я.п) : -1;
        return с.ячейки.map((я, и) =>
          `<span class="${я.вышло ? "вышло" : я.п ? "готов"
            : и === первая_пустая ? "идёт" : ""}"></span>`).join("")
          || '<span class="' + (работа ? "идёт" : "") + '"></span>';
      })()}</div>
      <div class="подшкала">
        <span><b>${с.вышло}</b> вышло · <b>${с.готово}</b> готово ·
          <b>${с.пусто}</b> пусто</span>
        <span>${с.следующая ? "ячейка " + экр(с.следующая) : "на сегодня всё"}</span>
      </div>

      ${(с.ждут || []).length ? `<div class="вещь ждут">
        <span class="т">⏳ ${(с.ждут || []).length}
          ${склонить((с.ждут || []).length, "пост ждёт", "поста ждут", "постов ждут")}
          одобрения</span>
        <span class="сост">посмотреть</span></div>` : ""}
      ${с.ячейки.filter(я => я.п && !я.вышло).slice(0, 2).map(я => `
        <div class="вещь" data-пост="${я.п.id}">
          ${кар(я.п) ? `<img src="${кар(я.п)}" alt="Превью: ${экр(я.п.title)}"
                 width="30" height="40" loading="lazy">` : ""}
          <span class="час">${экр(я.ч)}</span>
          <span class="т">${экр(я.п.title)}</span>
          <span class="сост">${руками ? "забрать" : "готов"}</span>
        </div>`).join("")}
      ${с.готово > 2 ? `<div class="вещь"><span class="т муть"
        >и ещё ${с.готово - 2}</span></div>` : ""}

      ${руками && с.готово ? `<button class="btn primary" data-забрать="${н.код}"
        style="width:100%;height:2.75rem;margin-top:.625rem"
        >📥 Забрать ${с.готово} ${склонить(с.готово, "файлами", "файлами", "файлами")}</button>`
      : беда ? `<div class="row" style="margin-top:.625rem">
          <button class="btn" data-забрать="${н.код}">📥 Забрать файлами</button>
          <button class="btn ghost" data-станок-снова="${н.код}">🔁 Ещё раз</button>
        </div>` : ""}

      <div class="внутрь">внутрь станка · вся смена и настройки ›</div>
    </div>`;
  }).join("");

  return `
    <div class="сводка">
      <div class="кол"><b>${вышло}</b><span>вышло<br>сегодня</span></div>
      <div class="раз"></div>
      <div class="кол"><b>${готовы}</b><span>готовы<br>ждут вас</span></div>
      <div class="раз"></div>
      <div class="кол"><b class="${пусто ? "тревога" : ""}">${пусто}</b>
        <span>ячейки<br>пустуют</span></div>
      <div class="раз"></div>
      <div class="кол"><b>${охват || "—"}</b><span>средний<br>охват</span></div>
    </div>

    ${станки || `<div class="пусто"><b>Станков нет</b>
      Конвейер не отозвался — настройки видно боту: ⚙️ → Конвейер.</div>`}

    ${ничьи.length ? `<div class="lbl свер">Без адреса · ${ничьи.length}</div>
      ${ничьи.map(п => строка(п)).join("")}` : ""}

    <div class="lbl свер">Сырьё</div>
    <div class="сырьёкн">
      <div data-идти="сырьё"><b>💡 ${(С.ideas || []).length}
        ${идей((С.ideas || []).length)}</b>
        ${(С.ideas || []).length ? "из копилки, ждут своей карусели"
                                 : "копилка пуста — бот пишет наугад"}</div>
      <div data-идти="сырьё"><b>🧠 ${(С.facts || []).length}
        ${фактов((С.facts || []).length)}</b>
        о проекте, из них бот и пишет</div>
    </div>

    <div style="height:.75rem"></div>
    <button class="btn primary wide" id="создать" ${С.mac?.alive ? "" : "disabled"}
      >✨ ${пусто ? "Собрать недостающее · " + пусто : "Собрать пост"}</button>`;
}

const чистоеИмя = и => (и || "").replace(/^\S+\s/, "");
const значок = и => (и || "").split(" ")[0];

// Русское число согласуется по последней цифре, кроме подростков.
function склонить(н, один, два, много) {
  if (н % 100 >= 11 && н % 100 <= 14) return много;
  const п = н % 10;
  return п === 1 ? один : п >= 2 && п <= 4 ? два : много;
}
const постов = н => склонить(н, "пост", "поста", "постов");
const фактов = н => склонить(н, "факт", "факта", "фактов");
const идей = н => склонить(н, "идея", "идеи", "идей");

function строка(п, толькоЧасы) {
  const рис = кар(п);
  const час = толькоЧасы && п.when ? п.when.split(" в ").pop() : п.when;
  // Пост, отданный телеграму, выйдет даже когда всё выключено. Разное
  // поведение должно и выглядеть по-разному.
  const сам = п.at_telegram ? ' <span class="сам">выйдет сам</span>' : "";
  const охват = п.views ? `<span class="охват">👁 ${п.views}</span>` : "";
  const метка = (п.images || []).length ? ` · 🎠 ${п.images.length}` : "";
  const когда = п.when ? `<div class="w">${час}${сам}${метка}</div>`
              : п.published ? `<div class="w past">вышел ${п.published} ${охват}</div>` : "";
  return `<button class="line" data-open="${п.id}" style="margin-top:.5rem">
    ${рис ? `<img src="${рис}" alt="Превью: ${экр(п.title)}"
             width="72" height="41" loading="lazy">` : ""}
    <div><div class="t">${экр(п.title)}</div>${когда}</div>
  </button>`;
}

function открыть(п) {
  const слоты = С.slots.map(с =>
    `<button class="chip" data-slot="${с.iso}">${с.label}</button>`).join("");
  const свои = new Date(Date.now() + 36e5).toISOString().slice(0, 16);
  const рис = кар(п);
  const слайды = п.images || [];
  const план = п.status === "scheduled";

  const правки = п.status === "published" ? "" : `
      <div class="row" style="margin-top:.5rem">
        <button class="btn ghost" data-act="edit">✏️ Править</button>
        <button class="btn ghost" data-act="ask">💬 Переписать</button>
        ${слайды.length ? "" : `<button class="btn ghost" data-act="repose"
          title="Другая поза кота">🎨</button>`}
      </div>`;

  // Забрать файлами. TikTok у нас в ручном режиме, и это самый частый путь
  // публикации: папка открывается на маке, файлы приходят сюда же в чат.
  // Две кнопки, а не одна: папка собирается за доли секунды из файлов,
  // лежащих на маке, а отправка двенадцати документов в телеграм занимает
  // около минуты. За маком она не нужна вовсе — нужна с телефона.
  const забрать = (слайды.length || рис) ? `
      <div class="row" style="margin-top:.5rem">
        <button class="btn ghost" data-act="take">📂 В папку на столе</button>
        <button class="btn ghost" data-act="take-files">📤 Прислать в чат</button>
      </div>` : "";

  // Отметка ручной выкладки. Через API её не узнать: прав на «список моих
  // видео» у приложения нет, только публикация, да и ключ песочный. Без
  // отметки пост остаётся черновиком, снова попадает в «чего не хватает» и
  // врёт в сводке.
  const выложил = п.status === "published" ? "" : `
      <button class="btn wide ghost" data-act="posted"
              style="margin-top:.5rem">✅ Выложил руками</button>`;

  // Перерисовка по одному слайду. У кота бывает пять лап: пикселям всё
  // хорошо, автоматика такое не ловит, а видно сразу. Пересобирать из-за
  // одной картинки всю карусель — минуты работы и восемь новых файлов.
  const перерисовка = (слайды.length > 1 && п.status !== "published") ? `
      <div class="lbl">Перерисовать слайд</div>
      <div class="chips" id="слайды">${слайды.map((_, и) =>
        `<button class="chip" data-слайд="${и + 1}">${и + 1}</button>`).join("")}
      </div>
      <div class="row" style="margin-top:.5rem">
        <button class="btn ghost" data-act="кот-база" disabled
                title="Другая поза из библиотеки — мгновенно">🎲 Другой кот</button>
        <button class="btn ghost" data-act="кот-новый" disabled
                title="Нарисовать заново и добавить в библиотеку">✨ Нарисовать</button>
        <button class="btn ghost danger" data-act="кот-брак" disabled
                title="Эта поза бракованная, больше её не брать">🚫</button>
      </div>` : "";

  const низ = план ? `
      <div class="row снизу">
        <button class="btn primary" data-act="pub">🚀 Опубликовать сейчас</button>
      </div>
      ${правки}
      ${забрать}
      ${выложил}
      ${перерисовка}
      <div class="row" style="margin-top:.5rem">
        <button class="btn ghost" data-act="move">🕑 Перенести</button>
        <button class="btn danger" data-act="off">Снять с плана</button>
      </div>`
    : п.status === "published"
    ? `<div class="row снизу">
         ${п.link ? `<a class="btn ghost" style="text-decoration:none"
             href="${п.link}" target="_blank">↗️ Открыть</a>`
           : `<button class="btn ghost" data-act="link">🔗 Добавить ссылку</button>`}
         <button class="btn" data-act="repeat">🔁 Повторить</button>
       </div>

       ${п.views ? `<div class="hint">👁 ${п.views} просмотров${
           п.reactions ? ` · ${п.reactions} реакций и пересылок` : ""}</div>` : ""}`
    : `<div class="lbl">Когда публиковать</div>
      <div class="chips">${слоты}</div>
      <div style="height:.625rem"></div>
      <input type="datetime-local" id="своё" value="${свои}">
      <div class="row" style="margin-top:.75rem">
        <button class="btn primary" data-act="plan">🕑 Запланировать</button>
      </div>
      ${правки}
      ${забрать}
      ${выложил}
      ${перерисовка}
      <div class="row" style="margin-top:.5rem">
        <button class="btn ghost" data-act="pub">🚀 Сейчас</button>
        <button class="btn ghost" data-act="again">🔄 Другой</button>
        <button class="btn danger" data-act="drop">✖️</button>
      </div>`;

  лист(`
    <div class="meta">
      <span class="tag">${экр(п.rubric)}</span>
      ${п.shape ? `<span class="tag">${экр(п.shape)}</span>` : ""}
      ${п.when ? `<span class="tag when">${п.when}</span>` : ""}
      ${п.published ? `<span class="tag done">вышел ${п.published}</span>` : ""}
    </div>
    ${п.status === "published" ? "" : `
      <div class="lbl">Куда публикуем</div>
      <div class="куда" id="куда-${п.id}">
        ${(п.where || []).map(в =>
          `<button class="${в.выбрана ? "on" : ""}" data-куда="${в.код}"
             ${в.готова ? "" : 'title="нет ключей"'}>${экр(в.имя)}${
             в.готова ? "" : " · нет ключей"}</button>`).join("")}
      </div>`}
    <div style="height:.75rem"></div>
    ${слайды.length
      ? `<div class="лента">${слайды.map((с, и) =>
           `<img src="${с}" alt="Слайд ${и + 1} из ${слайды.length}" loading="lazy"
              width="200" height="267">`).join("")}</div>
         <div class="счётслайдов">${слайды.length} слайда, листайте вбок</div>`
      : рис ? `<img class="shot" src="${рис}" alt="Обложка: ${экр(п.title)}"
        width="360" height="203">` : ""}
    <div class="post">${п.html}</div>
    ${низ}`, п);
}

// Листы приходят и уходят из разных мест, и следить за каждым «remove»
// значит однажды забыть. Наблюдатель ловит их все разом.
if (ТГ?.MainButton) new MutationObserver(() => площадка())
  .observe(document.body, {childList: true});

function лист(нутро, п) {
  document.querySelector(".sheet")?.remove();
  const э = document.createElement("div");
  э.className = "sheet";
  // Закрыть лист можно было только промахом мимо него. Лист занимает до
  // 92% высоты — промахиваться некуда, и человек оставался внутри. Теперь
  // три выхода: крестик, «назад» и потянуть вниз за полоску.
  э.innerHTML = `<div class="in">
    <div class="ручка-листа">
      <span class="grip"></span>
      <button class="закрыть" aria-label="Закрыть"><span>✕</span></button>
    </div><div class="нутро">${нутро}</div></div>`;
  э.addEventListener("click", с => { if (с.target === э) закрытьЛист(); });
  э.querySelector(".закрыть").onclick = () => { тук(); закрытьЛист(); };
  тянуть(э);
  document.body.appendChild(э);
  if (п) действия(э, п);
  return э;
}

function закрытьЛист() {
  const э = document.querySelector(".sheet");
  if (!э) return false;
  э.remove();
  return true;
}

// Потянуть вниз за верх листа — привычный способ его убрать. Считаем только
// вертикаль и только от полоски: иначе жест перехватывал бы прокрутку
// длинного содержимого.
function тянуть(э) {
  const шапка = э.querySelector(".ручка-листа");
  const в = э.querySelector(".in");
  let старт = null;
  шапка.addEventListener("touchstart", с => { старт = с.touches[0].clientY; },
                         {passive: true});
  шапка.addEventListener("touchmove", с => {
    if (старт === null) return;
    const сдвиг = Math.max(0, с.touches[0].clientY - старт);
    в.style.transform = `translateY(${сдвиг}px)`;
    в.style.transition = "none";
  }, {passive: true});
  шапка.addEventListener("touchend", с => {
    const сдвиг = Math.max(0, (с.changedTouches[0]?.clientY || старт) - старт);
    старт = null;
    в.style.transition = "";
    в.style.transform = "";
    if (сдвиг > 70) { тук(); закрытьЛист(); }
  }, {passive: true});
}

function действия(э, п) {
  let выбран = null;

  // Номер слайда выбирается отдельно от действия: «перерисовать» без
  // указания какой — самая частая ошибка, если чип сразу что-то запускает.
  э.querySelectorAll("[data-слайд]").forEach(б => б.onclick = () => {
    тук();
    const уже = б.classList.contains("on");
    э.querySelectorAll("[data-слайд]").forEach(д => д.classList.remove("on"));
    if (!уже) б.classList.add("on");
    э.querySelectorAll('[data-act^="кот-"]').forEach(д => д.disabled = уже);
  });
  э.querySelectorAll("[data-slot]").forEach(б => б.onclick = () => {
    тук();
    э.querySelectorAll("[data-slot]").forEach(д => д.classList.remove("on"));
    б.classList.add("on");
    выбран = б.dataset.slot;
    const п_ = э.querySelector("#своё");
    if (п_) п_.value = выбран.slice(0, 16);
  });

  э.querySelectorAll("[data-куда]").forEach(б => б.onclick = async () => {
    тук();
    try {
      const о = await зов("/api/where", {id: п.id, net: б.dataset.куда});
      п.where = о.where;
      э.querySelectorAll("[data-куда]").forEach(д => {
        const в = о.where.find(x => x.код === д.dataset.куда);
        д.classList.toggle("on", !!(в && в.выбрана));
      });
    } catch (e) { сказать(e.message, true); }
  });

  const кнопки = э.querySelectorAll("[data-act]");
  const занят = (да) => кнопки.forEach(б => б.disabled = да);

  э.querySelectorAll("[data-act]").forEach(б => б.onclick = async () => {
    const что = б.dataset.act;
    тук("medium");
    try {
      занят(true);
      if (что === "pub") {
        await довести(await зов("/api/publish", {id: п.id}));
        сказать("🚀 Опубликовано");
        э.remove();
      } else if (что === "plan" || что === "move") {
        if (что === "move") { снова(п); занят(false); return; }
        const когда = выбран || э.querySelector("#своё")?.value;
        if (!когда) { сказать("Выберите время", true); занят(false); return; }
        await довести(await зов("/api/schedule", {id: п.id, when: когда}));
        сказать("🕑 Поставил на " + когда.replace("T", ", "));
        э.remove();
      } else if (что === "repeat") {
        const о = await зов("/api/repeat", {id: п.id});
        С = о.state; рисовать(); считать();
        сказать("🔁 Копия в черновиках");
        э.remove();
        открыть(о.post);
      } else if (что === "edit") {
        э.remove(); return править(п);
      } else if (что === "ask") {
        э.remove(); return спросить(п);
      } else if (что === "repose") {
        э.remove();
        const свежий = await работа("/api/repose", {id: п.id}, ШАГИ_КОТ);
        if (свежий) открыть(свежий);
        return;
      } else if (что === "take" || что === "take-files") {
        const файлами = что === "take-files";
        э.remove();
        await работа("/api/take", {id: п.id, куда: "tiktok", файлами},
                     ШАГИ_ФАЙЛЫ);
        сказать(файлами ? "📤 Файлы в чате, папка открыта на маке"
                        : "📂 Папка открыта на рабочем столе");
        return;
      } else if (что.startsWith("кот-")) {
        const слайд = +(э.querySelector("[data-слайд].on")?.dataset.слайд || 0);
        if (!слайд) return;
        э.remove();
        const свежий = await работа("/api/repose", {
          id: п.id, слайд,
          новая: что === "кот-новый",
          брак: что === "кот-брак",
        }, что === "кот-новый" ? ШАГИ_КОТ_НОВЫЙ : ШАГИ_КОТ);
        if (свежий) открыть(свежий);
        return;
      } else if (что === "again") {
        await зов("/api/drop", {id: п.id});
        э.remove();
        рубрика = п.rubric === "стрим" ? рубрика : п.rubric;
        return сочинить(п.rubric === "стрим" ? "stream"
                      : п.rubric === "карусель" ? "carousel" : "post");
      } else if (что === "posted") {
        // Ссылку спрашиваем, но не требуем: кто выкладывает на ходу, тот
        // адрес пришлёт потом или не пришлёт вовсе. Отмена окна не должна
        // отменять саму отметку, поэтому пустая строка — это тоже «да».
        const адрес = prompt("Ссылка на выложенный пост (можно пропустить):",
                             "") || "";
        const о = await зов("/api/posted", {id: п.id, link: адрес.trim()});
        С = о.state || С;
        сказать("Отметил вышедшим");
        if (о.post) открыть(о.post); else э.remove();
        return;
      } else if (что === "link") {
        const адрес = (prompt("Ссылка на этот пост:", п.link || "") || "").trim();
        if (!адрес) return;
        const о = await зов("/api/link", {id: п.id, link: адрес});
        сказать("Сохранил ссылку");
        if (о.post) открыть(о.post);
        return;
      } else if (что === "off") {
        await довести(await зов("/api/unschedule", {id: п.id}));
        сказать("Снял с плана");
        э.remove();
      } else if (что === "drop") {
        const о = await зов("/api/drop", {id: п.id});
        С = о.state || С;
        сказать("Удалил");
        э.remove();
      }
      рисовать();
      считать();
    } catch (e) {
      сказать(e.message, true);
      занят(false);
    }
  });
}

function снова(п) {
  открыть({...п, status: "draft"});
}

// ── генерация ─────────────────────────────────────────────────────────────
const ШАГИ = [["читаю", "🔗 Читаю ссылку"],
              ["пишу", "✍️ Придумываю тему и текст"],
              ["рисую", "🎨 Рисую кота и карточку"],
              ["готово", "✅ Готово"]];
const ШАГИ_КАРУСЕЛЬ = [["читаю", "🔗 Читаю ссылку"],
                       ["пишу", "✍️ Раскладываю мысль по слайдам"],
                       ["рисую", "🎨 Рисую слайды"],
                       ["готово", "✅ Готово"]];
const ШАГИ_КОТ  = [["рисую", "🎨 Рисую кота заново"], ["готово", "✅ Готово"]];
const ШАГИ_КОТ_НОВЫЙ = [["рисую", "✨ Придумываю новую позу"],
                        ["готово", "✅ Готово"]];
const ШАГИ_ФАЙЛЫ = [["собираю", "📥 Собираю файлы"], ["готово", "✅ Готово"]];
const ШАГИ_ЗАКАЗ = [["думаю", "🧠 Придумываю темы"], ["пишу", "✍️ Пишу сценарии"],
                    ["рисую", "🎨 Рисую слайды"], ["готово", "✅ Готово"]];
const ШАГИ_ПЛАН = [["пишу", "📅 Набиваю расписание"], ["готово", "✅ Готово"]];

// Долгая работа: показываем шаги, спрашиваем состояние, возвращаем готовый пост
// Действия с каналом ушли на мак заданием: сессия аккаунта только там.
// Ответ приходит не с готовым состоянием, а с ключом задания.
async function довести(ответ) {
  if (!ответ || !ответ.job) return ответ;
  for (let н = 0; н < 200; н++) {
    await new Promise(р => setTimeout(р, 1200));
    const о = await зов("/api/job", {job: ответ.job});
    if (о.state === "ошибка") throw new Error(о.error || "не получилось");
    if (о.state === "готово") { С = await зов("/api/state"); return о; }
  }
  throw new Error("слишком долго");
}

async function работа(путь, тело, шаги = ШАГИ) {
  const э = лист(`<div class="work">${шаги.map(([к, п]) =>
      `<div class="step" data-step="${к}"><span class="spin"></span>${п}</div>`).join("")}
    <div class="step live" id="live"></div></div>`);
  const шаг = к => {
    const и = шаги.findIndex(с => с[0] === к);
    э.querySelectorAll("[data-step]").forEach((д, н) => {
      д.classList.toggle("on", н === и);
      д.classList.toggle("done", н < и);
    });
    if (и < 0) э.querySelector("#live").textContent = к;   // «пост 3 из 7»
  };
  шаг(шаги[0][0]);
  try {
    const {job} = await зов(путь, тело);
    for (let н = 0; н < 600; н++) {
      await new Promise(р => setTimeout(р, 1500));
      const о = await зов("/api/job", {job});
      if (о.state === "ошибка") throw new Error(о.error || "не получилось");
      шаг(о.state);
      if (о.state === "готово") {
        тук("medium");
        С = await зов("/api/state");
        рисовать(); считать();
        э.remove();
        return о.post || null;
      }
    }
    throw new Error("слишком долго");
  } catch (e) {
    сказать(e.message, true);
    э.remove();
    return null;
  }
}

async function сочинить(вид) {
  const тело = вид === "stream" ? {stream: true}
             : вид === "carousel" ? {carousel: true, topic: тема}
             : {rubric: рубрика, topic: тема};
  const п = await работа("/api/generate", тело,
                         вид === "carousel" ? ШАГИ_КАРУСЕЛЬ : ШАГИ);
  if (п) открыть(п);
}

// ── ручная правка ─────────────────────────────────────────────────────────
function править(п) {
  const к = п.card || {};
  const э = лист(`
    <div class="lbl">Текст поста</div>
    <textarea id="p-body">${экр(п.body)}</textarea>
    <div class="hint">Разметка: **жирный**, _курсив_, \`моноширинный\`, &gt; цитата.
      Первая строка станет жирной сама, тире уберутся.
      <span id="счёт"></span></div>
    <div class="lbl">Надписи на карточке</div>
    <div class="field"><label>Сверху</label>
      <input type="text" id="c-eye" value="${экр(к.card_eyebrow)}"></div>
    <div class="field"><label>Заголовок</label>
      <input type="text" id="c-title" value="${экр(к.card_title)}"></div>
    <div class="field"><label>Пункты, по одному в строке</label>
      <textarea id="c-lines" style="min-height:6rem">${экр((к.card_lines || []).join("\n"))}</textarea></div>
    <div class="field"><label>Подпись снизу</label>
      <input type="text" id="c-foot" value="${экр(к.card_footer)}"></div>
    <div class="row" style="margin-top:.75rem">
      <button class="btn primary" id="save">💾 Сохранить</button>
      <button class="btn ghost" id="back">Назад</button>
    </div>`);

  // Предел подписи 1024. Перебрать легко, и тогда пост разорвётся надвое.
  const поле = э.querySelector("#p-body"), счёт = э.querySelector("#счёт");
  const считать_знаки = () => {
    const н = поле.value.replace(/\*\*|__|[_`>]/g, "").length;
    счёт.textContent = ` · ${н} из 1024`;
    счёт.style.color = н > 950 ? "var(--warn)" : "var(--muted)";
    счёт.style.fontWeight = н > 950 ? "600" : "400";
  };
  поле.oninput = считать_знаки;
  считать_знаки();

  э.querySelector("#back").onclick = () => { э.remove(); открыть(п); };
  э.querySelector("#save").onclick = async () => {
    тук("medium");
    const кнопка = э.querySelector("#save");
    кнопка.disabled = true;
    кнопка.textContent = "⏳ Рисую карточку…";
    try {
      // Правка уходит заданием на мак: карточку надо перерисовать браузером,
      // а это секунды. Ответ приходит с ключом задания, а не с готовым
      // состоянием, поэтому дожидаемся его через «довести», как все долгие
      // действия. Раньше здесь стояло С = о.state, и состояние обнулялось.
      const о = await довести(await зов("/api/update", {
        id: п.id,
        body: э.querySelector("#p-body").value,
        card: {
          card_eyebrow: э.querySelector("#c-eye").value,
          card_title: э.querySelector("#c-title").value,
          card_lines: э.querySelector("#c-lines").value.split("\n")
                        .map(с => с.trim()).filter(Boolean),
          card_footer: э.querySelector("#c-foot").value,
        }}));
      рисовать(); считать();
      сказать("💾 Сохранил");
      э.remove();
      открыть(о.post || п);
    } catch (e) {
      сказать(e.message, true);
      кнопка.disabled = false;
      кнопка.textContent = "💾 Сохранить";
    }
  };
}

// ── правка словами ────────────────────────────────────────────────────────
function спросить(п) {
  const э = лист(`
    <div class="lbl">Что поправить</div>
    <textarea id="что" style="min-height:5rem"
      placeholder="Сделай короче. Убери третий пункт. Добавь пример с ценой."></textarea>
    <div class="hint">Тема, рубрика и форма останутся теми же. Поменяется только
      то, о чём просите, остальное сохранится как есть.</div>
    <div class="row" style="margin-top:.75rem">
      <button class="btn primary" id="go">🔄 Переписать</button>
      <button class="btn ghost" id="back">Назад</button>
    </div>`);
  э.querySelector("#back").onclick = () => { э.remove(); открыть(п); };
  э.querySelector("#go").onclick = async () => {
    const что = э.querySelector("#что").value.trim();
    if (!что) return сказать("Напишите, что поправить", true);
    тук("medium");
    э.remove();
    const свежий = await работа("/api/rewrite", {id: п.id, instruction: что});
    if (свежий) открыть(свежий);
  };
}

// ── план вперёд ───────────────────────────────────────────────────────────
function планЛист() {
  const э = лист(`
    <div class="lbl">План вперёд</div>
    <div class="hint">Бот сочинит по посту на каждый день и расставит их по
      времени. Каждый пост занимает около минуты, так что семь дней это
      несколько минут ожидания. Всё попадёт в расписание, ничего не уйдёт в
      канал без вас.</div>
    <div class="row" style="margin-top:.875rem">
      <div class="field" style="flex:1"><label>Дней</label>
        <input type="text" id="pl-days" value="7" inputmode="numeric"></div>
      <div class="field" style="flex:1"><label>Время</label>
        <input type="text" id="pl-time" value="10:00"></div>
    </div>
    <button class="btn primary wide" id="pl-go" style="margin-top:.25rem">📅 Набить расписание</button>`);
  э.querySelector("#pl-go").onclick = async () => {
    тук("medium");
    const дней = parseInt(э.querySelector("#pl-days").value, 10) || 7;
    const время = э.querySelector("#pl-time").value.trim() || "10:00";
    э.remove();
    await работа("/api/plan", {days: дней, times: [время]}, ШАГИ_ПЛАН);
    сказать("📅 Расписание набито");
    идти("цех");
  };
}

// ── куда публикуем ────────────────────────────────────────────────────────
async function каналы() {
  const н = С.channels || {};
  const свой = (await зов("/api/access")).owner;
  const строка = (вид, подпись) => {
    const адрес = н[вид];
    const выбран = н["выбран"] === вид;
    return `<button class="pick${выбран ? " on" : ""}" data-канал="${вид}"
              ${адрес && свой ? "" : "disabled style=opacity:.5"}>
      <div class="галка">${выбран ? "✓" : ""}</div>
      <div style="flex:1;min-width:0">
        <div>${подпись}</div>
        <div class="низ">${адрес ? экр(адрес) : "адрес не задан"}</div>
      </div>
    </button>`;
  };

  const э = лист(`
    <div class="lbl">Куда публикуем</div>
    ${строка("тест", "🧪 Тестовый")}
    ${строка("основной", "📣 Основной")}
    ${свой ? `
      <div class="lbl">Адрес основного канала</div>
      <div class="field">
        <input type="text" id="к-адрес" placeholder="@имя_канала"
               value="${экр(н["основной"])}">
      </div>
      <div class="row">
        <button class="btn" id="к-проверить">🔍 Проверить</button>
        <button class="btn primary" id="к-сохранить">💾 Сохранить</button>
      </div>
      <div class="hint" id="к-ответ">Бот должен быть администратором канала с
        правом публикации сообщений. Проверка это подтвердит до того, как туда
        уйдёт первый пост.</div>`
      : `<div class="hint">Канал переключает владелец.</div>`}`);

  э.querySelectorAll("[data-канал]").forEach(б => б.onclick = async () => {
    const вид = б.dataset["канал"];
    if (вид === "основной") {
      const да = await новый_вопрос("Посты пойдут в основной канал. Уверены?");
      if (!да) return;
    }
    тук("medium");
    try {
      С = (await зов("/api/channel/pick", {kind: вид})).state;
      считать(); рисовать();
      сказать(вид === "основной" ? "📣 Пишем в основной канал"
                                 : "🧪 Пишем в тестовый");
      э.remove();
    } catch (e) { сказать(e.message, true); }
  });

  const ответ = э.querySelector("#к-ответ");
  const проверка = async () => {
    const адрес = э.querySelector("#к-адрес").value.trim();
    ответ.textContent = "⏳ Спрашиваю у Telegram…";
    try {
      const о = await зов("/api/channel/check", {address: адрес});
      ответ.textContent = (о["ок"] ? "✅ " : "⚠️ ") + о["что"];
      ответ.style.color = о["ок"] ? "var(--accent)" : "var(--warn)";
      return о["ок"];
    } catch (e) { ответ.textContent = "⚠️ " + e.message; return false; }
  };
  if (э.querySelector("#к-проверить")) {
    э.querySelector("#к-проверить").onclick = () => { тук(); проверка(); };
    э.querySelector("#к-сохранить").onclick = async () => {
      тук("medium");
      if (!await проверка()) return;
      try {
        С = (await зов("/api/channel/set",
             {kind: "основной", address: э.querySelector("#к-адрес").value.trim()})).state;
        считать();
        сказать("💾 Канал сохранён");
        э.remove(); каналы();
      } catch (e) { сказать(e.message, true); }
    };
  }
}

// Подтверждение: у Telegram своё окно, вне его обходимся обычным confirm
function новый_вопрос(текст) {
  return new Promise(готово => {
    if (ТГ?.showConfirm) ТГ.showConfirm(текст, да => готово(!!да));
    else готово(confirm(текст));
  });
}

// ── настройки ─────────────────────────────────────────────────────────────
function настройки() {
  // Обслуживание цеха: то, что делают раз в неделю. Отдельного экрана не
  // заслуживает, но и пропасть не должно — раньше эти две кнопки жили на
  // вкладке «Ещё», и вместе с ней чуть не потерялись.
  const э = лист(`
    <div class="lbl">Настройки</div>
    <button class="btn wide" id="n-access">👥 Кто может пользоваться</button>
    <div style="height:.5rem"></div>
    <button class="btn wide" id="n-stream">🔴 Анонс стрима</button>
    <div class="lbl свер">Обслуживание</div>
    <button class="btn wide ghost" id="go-week">📅 Набить план на неделю</button>
    <div style="height:.5rem"></div>
    <button class="btn wide ghost" id="go-clean">🧹 Прибраться</button>
    <div class="hint">Уборка стирает отрисовки, которые ни к какому посту
      уже не относятся.</div>`);
  э.querySelector("#n-access").onclick = () => { э.remove(); доступ(); };
  э.querySelector("#n-stream").onclick = () => { э.remove(); настройкиСтрима(); };
  подвязать();
}

async function доступ() {
  let д;
  try { д = await зов("/api/access"); } catch (e) { return сказать(e.message, true); }

  const люди = д.people.length ? д.people.map(п => `
    <div class="plat" style="display:flex;align-items:center;gap:.625rem">
      <div style="flex:1;min-width:0">
        <div>${экр(п["имя"])}</div>
        <div class="hint" style="margin:0">id ${п.id}</div>
      </div>
      ${д.owner ? `
        <select data-роль="${п.id}" style="width:auto;font-size:.75rem;padding:.375rem .5rem">
          <option value="полный"${п["роль"] === "полный" ? " selected" : ""}>публикует</option>
          <option value="готовит"${п["роль"] === "готовит" ? " selected" : ""}>готовит</option>
        </select>
        <button class="btn danger" data-убрать="${п.id}">Убрать</button>` : ""}
    </div>`).join("") : `<div class="card muted">Пока никого, кроме вас.</div>`;

  const э = лист(`
    <div class="lbl">Кто может пользоваться</div>
    ${люди}
    <div id="код"></div>
    ${д.owner ? `
      <button class="btn primary wide" id="d-code" style="margin-top:.75rem">🔑 Создать приглашение</button>
      <div class="hint">Код действует сутки и срабатывает один раз. Отправьте
        его человеку, он пришлёт код боту в личку и окажется внутри. Свой id
        человеку узнавать не нужно.</div>
      <div class="hint">Роль «публикует» это те же права, что у вас, кроме
        настроек. Роль «готовит» сочиняет и правит, но в канал не отправляет.
        О каждой чужой публикации вам придёт уведомление.</div>` : ""}`);

  э.querySelectorAll("[data-роль]").forEach(с => с.onchange = async () => {
    тук();
    try {
      await зов("/api/access/role", {id: +с.dataset["роль"], role: с.value});
      сказать(с.value === "готовит" ? "Теперь только готовит посты"
                                    : "Может публиковать");
    } catch (e) { сказать(e.message, true); }
  });
  э.querySelectorAll("[data-убрать]").forEach(б => б.onclick = async () => {
    тук("medium");
    try {
      await зов("/api/access/remove", {id: +б.dataset["убрать"]});
      сказать("Убрал");
      э.remove(); доступ();
    } catch (e) { сказать(e.message, true); }
  });

  const создать = э.querySelector("#d-code");
  if (создать) создать.onclick = async () => {
    тук("medium");
    создать.disabled = true;
    try {
      const {code} = await зов("/api/access/code");
      э.querySelector("#код").innerHTML = `
        <div class="card" style="margin-top:.75rem;text-align:center">
          <div class="hint" style="margin:0 0 .375rem">Код приглашения</div>
          <div style="font-size:1.75rem;font-weight:700;letter-spacing:.28em;
                      color:var(--accent);font-family:ui-monospace,Menlo,monospace">${code}</div>
        </div>`;
      navigator.clipboard?.writeText(code).then(() => сказать("Код скопирован"),
                                                () => сказать("Код готов"));
    } catch (e) { сказать(e.message, true); }
    создать.disabled = false;
  };
}

// ── анонс стрима ──────────────────────────────────────────────────────────
async function настройкиСтрима() {
  let н, правила = {rules: [], days: []};
  try {
    н = await зов("/api/stream");
    правила = await зов("/api/repeats");
  } catch (e) { return сказать(e.message, true); }
  const правило = (правила.rules || [])[0] || {вид: "анонс", день: 3, время: "19:00", включено: false};
  const площадки = н.площадки.map((п, и) => `
    <div class="plat">
      <div class="field"><label>Кнопка</label>
        <input type="text" data-поле="имя" data-и="${и}" value="${экр(п.имя)}"></div>
      <div class="field" style="margin:0"><label>Ссылка</label>
        <input type="url" data-поле="адрес" data-и="${и}" value="${экр(п.адрес)}"></div>
    </div>`).join("");

  const э = лист(`
    <div class="lbl">Текст анонса</div>
    <textarea id="s-text" style="min-height:12rem">${экр(н.текст)}</textarea>
    <div class="hint">Уходит в канал слово в слово каждый раз. Ссылку внутри
      текста пишут так: [Twitch](https://twitch.tv/…).</div>
    <div class="lbl">Афиша</div>
    <div class="field"><label>Надпись сверху</label>
      <input type="text" id="a-eye" value="${экр(н.афиша.надпись)}"></div>
    <div class="field"><label>Крупная надпись</label>
      <input type="text" id="a-title" value="${экр(н.афиша.заголовок)}"></div>
    <div class="field"><label>Строка под ней</label>
      <input type="text" id="a-sub" value="${экр(н.афиша.подзаголовок)}"></div>
    <div class="lbl">Площадки</div>
    ${площадки}
    <div class="lbl">Повторять анонс</div>
    <div class="row">
      <select id="п-день" style="flex:2">${
        (правила.days || []).map((д, и) =>
          `<option value="${и}"${и === (правило.день ?? 3) ? " selected" : ""}>${д}</option>`).join("")}</select>
      <input type="text" id="п-время" style="flex:1" value="${экр(правило.время || "19:00")}">
    </div>
    <label class="галка"><input type="checkbox" id="п-вкл"${правило.включено ? " checked" : ""}>
      Ставить автоматически</label>
    <div class="hint">Бот разложит ближайшие четыре повтора в отложенные
      телеграма. Они выйдут даже если мак и всё остальное выключено.</div>

    <button class="btn primary wide" id="s-save" style="margin-top:.75rem">💾 Сохранить навсегда</button>
    <div class="hint">Правка запомнится и будет применяться ко всем следующим анонсам.</div>`);

  э.querySelector("#s-save").onclick = async () => {
    тук("medium");
    const кнопка = э.querySelector("#s-save");
    кнопка.disabled = true; кнопка.textContent = "⏳ Перерисовываю афишу…";
    const площ = н.площадки.map((п, и) => ({...п}));
    э.querySelectorAll("[data-поле]").forEach(поле => {
      площ[+поле.dataset.и][поле.dataset.поле] = поле.value.trim();
    });
    try {
      await зов("/api/stream/save", {
        текст: э.querySelector("#s-text").value,
        площадки: площ,
        афиша: {надпись: э.querySelector("#a-eye").value,
                заголовок: э.querySelector("#a-title").value,
                подзаголовок: э.querySelector("#a-sub").value},
      });
      await зов("/api/repeats/save", {rules: [{
        вид: "анонс",
        день: +э.querySelector("#п-день").value,
        время: э.querySelector("#п-время").value.trim() || "19:00",
        включено: э.querySelector("#п-вкл").checked,
      }]});
      сказать("💾 Анонс запомнен");
      э.remove();
    } catch (e) {
      сказать(e.message, true);
      кнопка.disabled = false; кнопка.textContent = "💾 Сохранить навсегда";
    }
  };
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
function листЗаказа(нач = {}) {
  const станки = С.pipeline || [];
  let куда = нач.код || станок || (станки[0] || {}).код;
  let своя = нач.тема || "";
  let выбраны = нач.час ? [нач.час] : null;   // null — ещё не трогали руками
  let сколько = нач.час ? 1 : 0;              // 0 — посчитаем от пустых ячеек

  const свободные = код => смена(код).ячейки
    .filter(я => !я.п && вМинутах(я.ч) > вМинутах(С.now)).map(я => я.ч);

  const э = лист("");
  нарисовать();

  function нарисовать() {
    const н = станки.find(с => с.код === куда) || {};
    const руками = н.режим !== "сам";
    const ячейки = свободные(куда);
    if (!сколько) сколько = Math.max(1, Math.min(10, ячейки.length || 1));
    if (!выбраны) выбраны = ячейки.slice(0, сколько);
    выбраны = выбраны.filter(ч => ячейки.includes(ч));

    э.querySelector(".нутро").innerHTML = `
      <div class="t">Заказ станку</div>

      <div class="lbl свер">Сколько собрать</div>
      <div class="счётчик">
        <button id="з-мин" aria-label="Меньше"
          ${сколько <= 1 ? "disabled" : ""}>−</button>
        <div class="ч"><b>${сколько}</b>
          <span>${склонить(сколько, "карусель", "карусели", "каруселей")} ·
            около ${сколько} мин.</span></div>
        <button id="з-плюс" aria-label="Больше"
          ${сколько >= 10 ? "disabled" : ""}>＋</button>
      </div>

      <div class="lbl">На какой станок</div>
      <div class="станки">${станки.map(с => `
        <button class="${с.код === куда ? "on" : ""}" data-з-станок="${с.код}">
          <b>${экр(с.имя)}</b>
          <span>${с.режим === "сам" ? "публикует сам" : "выкладываете вы"} ·
            ${с.часов} в день</span>
        </button>`).join("")}</div>

      ${руками ? `<div class="hint">Станок выкладываете вы, поэтому время
        постам не ставится: они лягут в очередь и будут ждать в ячейках.</div>`
      : ячейки.length ? `
        <div class="lbl свер">В какие ячейки</div>
        <div class="ячч">${ячейки.map(ч =>
          `<button class="${выбраны.includes(ч) ? "on" : ""}"
             data-з-час="${экр(ч)}">${экр(ч)}</button>`).join("")}</div>
        <div class="hint">Что не поместится в выбранные — ляжет в очередь
          станка без времени.</div>`
      : `<div class="hint">Свободных ячеек на сегодня нет — соберу в очередь
          станка, время поставите сами.</div>`}

      <div class="lbl свер">Про что · можно не отвечать</div>
      <label for="з-тема" class="sr">Тема заказа</label>
      <input type="text" id="з-тема" value="${экр(своя)}" autocomplete="off"
             placeholder="Придумает сам${н.угол ? ", следующий угол — «"
               + экр(н.угол) + "»" : ""}…">
      ${(С.ideas || []).length ? `<div class="chips" style="margin-top:.5rem">
        ${(С.ideas || []).slice(0, 3).map(и =>
          `<button class="chip" data-з-идея="${экр(и.text)}"
            >💡 ${экр(и.text.slice(0, 44))}</button>`).join("")}</div>` : ""}

      <button class="btn primary wide" id="з-пуск" style="margin-top:.875rem"
        ${С.mac?.alive ? "" : "disabled"}>✨ Собрать ${сколько}</button>
      <div class="hint" style="text-align:center">Можно закрыть приложение —
        бот напишет в чат, когда всё будет готово.</div>`;
    связать();
  }

  function связать() {
    э.querySelector("#з-мин").onclick = () => { тук(); сколько--; нарисовать(); };
    э.querySelector("#з-плюс").onclick = () => { тук(); сколько++; нарисовать(); };
    э.querySelectorAll("[data-з-станок]").forEach(б => б.onclick = () => {
      тук(); куда = б.getAttribute("data-з-станок"); выбраны = null; сколько = 0; нарисовать();
    });
    э.querySelectorAll("[data-з-час]").forEach(б => б.onclick = () => {
      тук();
      const ч = б.getAttribute("data-з-час");
      выбраны = выбраны.includes(ч) ? выбраны.filter(x => x !== ч) : [...выбраны, ч];
      выбраны.sort();
      нарисовать();
    });
    э.querySelectorAll("[data-з-идея]").forEach(б => б.onclick = () => {
      тук(); своя = б.getAttribute("data-з-идея"); нарисовать();
    });
    const поле = э.querySelector("#з-тема");
    поле.oninput = () => { своя = поле.value; };
    э.querySelector("#з-пуск").onclick = async () => {
      тук("medium");
      э.remove();
      try {
        await работа("/api/order", {сколько, куда, часы: выбраны, тема: своя},
                     ШАГИ_ЗАКАЗ);
        сказать(`🎠 Собрал ${сколько}`);
      } catch (e) { сказать(e.message, true); }
    };
  }
}

function листСоздания(тема_ = "") {
  тема = тема_;
  const чипы = ["Сам выберу", ...С.rubrics].map(и => {
    const знач = и === "Сам выберу" ? "" : и;
    return `<button class="chip${(рубрика || "") === знач ? " on" : ""}"
              data-rub="${знач}">${Заглавная(и)}</button>`;
  }).join("");
  const э = лист(`
    <div class="lbl">Что делаем</div>
    <div class="row">
      <button class="btn primary" data-вид="post">✍️ Пост</button>
      <button class="btn" data-вид="carousel">🎠 Карусель</button>
    </div>
    <div class="row" style="margin-top:.375rem">
      <button class="btn ghost" data-вид="stream">🔴 Анонс стрима</button>
    </div>
    <div class="lbl">О чём</div>
    <div class="chips">${чипы}</div>
    <div style="height:.625rem"></div>
    <input type="text" id="тема" placeholder="Своя тема или ссылка на статью"
           value="${экр(тема)}">
    <div class="hint">Можно кинуть ссылку: бот откроет страницу, прочитает и
      перескажет суть своими словами.</div>`);
  э.querySelectorAll("[data-rub]").forEach(б => б.onclick = () => {
    тук(); рубрика = б.dataset.rub || null;
    э.querySelectorAll("[data-rub]").forEach(д => д.classList.remove("on"));
    б.classList.add("on");
  });
  const поле = э.querySelector("#тема");
  if (поле) поле.oninput = () => { тема = поле.value; };
  э.querySelectorAll("[data-вид]").forEach(б => б.onclick = async () => {
    тук("medium");
    э.remove();
    await сочинить(б.dataset.вид);
  });
}

// Лист площадки конвейера: включить, режим, часы.
function листКонвейера(код) {
  const п = (С.pipeline || []).find(x => x.код === код);
  if (!п) return;
  const э = лист(`
    <div class="lbl">${экр(п.имя)}</div>
    <button class="btn wide ${п.вкл ? "primary" : ""}" data-пер="auto">
      ${п.вкл ? "🤖 Сочиняет сам" : "💤 Спит"}</button>
    <div style="height:.375rem"></div>
    <button class="btn wide" data-пер="mode">
      ${п.режим === "сам" ? "🚀 Публикует сам" : "✋ Готовит, публикуете вы"}</button>
    <div class="hint">Выходит в ${п.часы.join(", ")}. Держу готовыми
      ${п.запас}, сейчас ${п.готово}. Часы и глубину плана меняйте в чате бота.</div>`);
  э.querySelectorAll("[data-пер]").forEach(б => б.onclick = async () => {
    тук("medium");
    try {
      const о = await зов("/api/pipeline", {net: код, what: б.dataset.пер});
      С.pipeline = о.pipeline;
      э.remove(); рисовать();
    } catch (e) { сказать(e.message, true); }
  });
}

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
