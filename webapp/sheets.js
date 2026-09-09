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
             href="${п.link}" target="_blank">↗️ Открыть</a>` : ""}
         <button class="btn" data-act="repeat">🔁 Повторить</button>
       </div>

       <div class="lbl" style="margin-top:.75rem">Ссылка на пост</div>
       <div class="row">
         <input id="ссылка-поста" type="url" inputmode="url"
                placeholder="https://www.tiktok.com/@…"
                value="${п.link ? экр(п.link) : ""}" style="flex:1">
         <button class="btn ghost" data-act="link">Сохранить</button>
       </div>
       <div class="hint">Пост выкладывали руками, поэтому адрес знает только
         человек. Можно оставить пустым.</div>

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
        // Ссылку не спрашиваем окном: prompt в мини-приложении телеграма не
        // показывается вовсе — нажатие выглядело как «ничего не произошло».
        // Отмечаем сразу, а поле для адреса появляется на карточке вышедшего.
        const о = await зов("/api/posted", {id: п.id, link: ""});
        С = о.state || С;
        сказать("Отметил вышедшим");
        if (о.post) открыть(о.post); else э.remove();
        return;
      } else if (что === "link") {
        // Своё поле вместо prompt, по той же причине.
        const поле = э.querySelector("#ссылка-поста");
        if (!поле) return;
        const адрес = (поле.value || "").trim();
        if (!адрес) { поле.focus(); return; }
        if (!/^https?:\/\//i.test(адрес)) {
          сказать("Ссылка должна начинаться с http", true);
          поле.focus();
          return;
        }
        const о = await зов("/api/link", {id: п.id, link: адрес});
        С = о.state || С;
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

