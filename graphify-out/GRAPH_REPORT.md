# Graph Report -   (2026-09-08)

## Corpus Check
- 78 files · ~154,887 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 926 nodes · 1273 edges · 37 communities detected
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 135 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]

## God Nodes (most connected - your core abstractions)
1. `главное()` - 85 edges
2. `_Связь` - 61 edges
3. `_пункт()` - 56 edges
4. `хром()` - 41 edges
5. `звук_выключен()` - 31 edges
6. `_стоп()` - 30 edges
7. `_вызвать()` - 29 edges
8. `_поля()` - 28 edges
9. `С — общее состояние приложения` - 27 edges
10. `Слайд` - 24 edges

## Surprising Connections (you probably didn't know these)
- `Карточка — другой угол той же темы` --semantically_similar_to--> `Обложка как половина работы`  [INFERRED] [semantically similar]
  README.md → ПЛАН.md
- `main()` --calls--> `подготовить()`  [INFERRED]
  bot.py → vercel/ideas.py
- `Форма поста: список, разбор, схема, история` --semantically_similar_to--> `Явный выбор каркаса карусели`  [INFERRED] [semantically similar]
  README.md → ПЛАН.md
- `card.py — карточка и афиша через Chrome` --shares_data_with--> `Базовые пакеты: requests, python-dotenv, pydantic, pillow, numpy`  [INFERRED]
  README.md → requirements.txt
- `Копилка идей` --semantically_similar_to--> `Свой свайп-файл механик`  [INFERRED] [semantically similar]
  README.md → ПЛАН.md

## Hyperedges (group relationships)
- **Конвейер: угол по кругу превращается в карусель и встаёт в план** — readme_konveyer, readme_ugly_po_krugu, readme_karusel, readme_karusel_tiktok_otlichiya, readme_raspisanie_utc, readme_worker_py [EXTRACTED 1.00]
- **Путь заметки: голосовое или сообщение раздваивается в копилку идей и в факты, и уходит в задание писателю** — readme_zametka_tri_sposoba, readme_voice_py, readme_whisper_na_make, readme_ideas_py, readme_facts_py, readme_writer_py [EXTRACTED 1.00]
- **Разделение труда: приложение на Vercel кладёт задание, мак делает тяжёлое, пост уходит в отложенные Telegram, всё через Supabase** — readme_vercel, readme_mak, readme_ochered_zadanij, readme_telegram_otlozhennye, readme_supabase, readme_userbot_py [EXTRACTED 1.00]
- **Одобрение черновика: карточка ждёт, выбор часа, /api/approve, отметка card.ячейка, смена показывает ячейку занятой** — index_ekran_stanok, index_pochemu_kartochka_zhdet, index_api_approve, index_pochemu_odobrit, index_pole_card_yacheyka, index_pochemu_otmetka_na_poste, index_smena, index_pole_drafts [EXTRACTED 1.00]
- **Заказ станку: лист заказа, /api/order, ключ задания, опрос /api/job по ШАГИ_ЗАКАЗ, /api/state, полоска хода** — index_list_zakaza, index_api_order, index_rabota, index_shagi, index_api_job, index_api_state, index_hod_rabot, index_pole_raboty [EXTRACTED 1.00]
- **Ручная выкладка: смена даёт готовые посты, /api/take по одному, ШАГИ_ФАЙЛЫ, файлы в чате и папка на маке** — index_smena, index_pochemu_zabrat_iz_ceha, index_api_take, index_pochemu_zabrat_faylami, index_rabota, index_pole_mac, index_ekran_ceh [EXTRACTED 1.00]

## Communities

### Community 0 - "Community 0"

Cohesion: 0.03
Nodes (78): свои(), Одноразовый код на сутки. Дольше он и не нужен, а лежать вечно опасно., Гасит код и впускает человека. Код одноразовый: второй раз не сработает., Ключ личной ссылки. Заводится сам при первом обращении., Кто пришёл по личной ссылке. Ноль, если ключ не тот.      Сравнение постоянное п, {id: {'имя': …, 'когда': …}}. Владельца в списке нет, он есть всегда., Сколько часов осталось. Ноль означает «закрыто»., Что человеку позволено. У владельца всегда полный доступ. (+70 more)

### Community 1 - "Community 1"

Cohesion: 0.03
Nodes (98): АДРЕСА и хеш-адреса (#shop, #stock, #m-код), POST /api/approve, POST /api/facts/drop, POST /api/facts/save, POST /api/ideas/add, POST /api/ideas/drop, POST /api/order, POST /api/pipeline (+90 more)

### Community 2 - "Community 2"

Cohesion: 0.03
Nodes (76): BaseModel, Слайд, mascot_склад(), Текст плюс отрисованные слайды. Возвращает (карусель, ссылки на картинки)., Какая из фраз достанется этой карусели.      Выбор считается от темы, а не берёт, Числа прошлых постов — только той площадке, к которой они относятся.      Охват, Приёмы из свайп-файла. Пусто, пока владелец ничего туда не положил., Список поз, которые реально лежат на диске, с человеческим пояснением. (+68 more)

### Community 3 - "Community 3"

Cohesion: 0.03
Nodes (59): BaseHTTPRequestHandler, _модель(), Версии поста для площадок. Считаются один раз и остаются в карточке., Схема ответа. Заводится по требованию: pydantic есть только на маке, а     включ, Где вообще заданы ключи. Кнопку без ключей показывать незачем., _Связь, Ошибки, после которых соединение годится только выбросить., Отпускает соединение этой нити. Нужно только при остановке. (+51 more)

### Community 4 - "Community 4"

Cohesion: 0.03
Nodes (76): Аудит качества каруселей 06.09.2026, Чему научились у чужих каруселей, Creator Search Insights и вкладка «пробелы», Длина работает на нас, пока каждый слайд что-то добавляет, Досвайп: уход с первого слайда на второй, Откуда берём материал, Явный выбор каркаса карусели, Обложка как половина работы (+68 more)

### Community 5 - "Community 5"

Cohesion: 0.03
Nodes (64): главное(), Всё вместе: собрать, открыть папку, прислать в чат., Есть ли чем сочинять. Без этого половина бота не работает., Готовое содержимое для площадки: картинки и текст.      Считается один раз и жив, Момент, раньше которого не читаем, в UTC., Окружение для CLI: с полным PATH и без ключей от платного API., Придирки к самим слайдам: длина, однообразие, количество., Человеческая запись начала окна → момент времени.      Понимает «04.09 14:00», « (+56 more)

### Community 6 - "Community 6"

Cohesion: 0.04
Nodes (48): _пункт(), Кегли для видов считаются от базовых, чтобы не заводить их трижды., Слово в *звёздочках* становится лаймовым.      Тег в содержимое пускать нельзя:, Кегли для видов считаются от базовых, чтобы не заводить их трижды., Разметка одного вида. `з` это его содержимое, у каждого своё., Кегль заголовка под его длину.      Раньше длинное просто обрезалось многоточием, Слово в *звёздочках* становится лаймовым.      Тег в содержимое пускать нельзя:, Обрезает список под вёрстку и говорит, если что-то отрезал.      Молчаливая обре (+40 more)

### Community 7 - "Community 7"

Cohesion: 0.05
Nodes (39): _запросить(), Углы должны быть тем самым синим.      Модель иногда игнорирует требование фона, Новая поза под конкретный пост. None, если не вышло., Рисует новую позу и кладёт её в библиотеку насовсем.      До сих пор библиотека, Не обрезан ли персонаж рамкой самой картинки.      Фон снимается по силуэту, поэ, Позы, которые владелец отверг вручную.      Автоматика ловит обрезанных котов, н, Больше эту позу не берём., {ключ: путь} по тому, что реально лежит на диске.      По умолчанию отдаёт тольк (+31 more)

### Community 8 - "Community 8"

Cohesion: 0.06
Nodes (46): POST /api/drop, POST /api/generate, POST /api/job, POST /api/plan, POST /api/publish, POST /api/repeat, POST /api/repose, POST /api/rewrite (+38 more)

### Community 9 - "Community 9"

Cohesion: 0.05
Nodes (42): POST /api/cleanup, POST /api/repeats, POST /api/repeats/save, POST /api/stream, POST /api/stream/save, Лист настроек, Лист анонса стрима (настройкиСтрима), Почему обслуживание в настройках — вкладка «Ещё» чуть не потеряла эти кнопки (+34 more)

### Community 10 - "Community 10"

Cohesion: 0.05
Nodes (38): Афиша стрима: своя вёрстка, Анонс стримов правится и запоминается, assets/mascot — позы кота-маскота, card.py — карточка и афиша через Chrome, Что проверено, а что нет, DATABASE_URL и перенос накопленного, Dockerfile — питон и Chromium, Дублирование постов в X и Threads (+30 more)

### Community 11 - "Community 11"

Cohesion: 0.06
Nodes (32): POST /api/access, POST /api/access/code, POST /api/access/remove, POST /api/access/role, POST /api/channel/check, POST /api/channel/pick, POST /api/channel/set, Лист доступа — кто может пользоваться (+24 more)

### Community 12 - "Community 12"

Cohesion: 0.06
Nodes (29): _поля(), Пост-листалка: несколько слайдов в одном стиле под общей подписью.      Хранится, Правит существующий пост по указанию владельца. Номер остаётся тем же.      Номе, Ручная правка: текст поста и надписи на карточке.      Карточка перерисовывается, После правки посчитанные варианты площадок становятся ложью.      Вариант считае, Кот для перерисовки. Берём того же, что уже стоит на карточке.      Рисовать нов, Новая поза кота под тот же текст. Модель каждый раз рисует иначе., Пересобирает слайды по сохранённому тексту, ничего не сочиняя заново.      Нужно (+21 more)

### Community 13 - "Community 13"

Cohesion: 0.08
Nodes (26): _стоп(), m_видео(), Ставит кнопку приложения всем своим, а не только владельцу.      Адрес туннеля м, Конвейер. Одна строка на площадку: включён ли и насколько полон план., Настройки одной площадки внутри конвейера., Кнопки под черновиком: сначала куда, потом когда.      Порядок не случайный. «Ку, Раздел «Конвейер»: площадки, их темп и разовая сборка., Правка поста из чата: заменой текста или указанием переписать.      Номер поста (+18 more)

### Community 14 - "Community 14"

Cohesion: 0.08
Nodes (25): access.py — доступ, коды приглашений, роли, bot.py — цикл опроса, меню, кнопки, расписание, Редактор 4xTube: бот для постов в канал, Claude Code по подписке вместо ANTHROPIC_API_KEY, core.py — общее для чата и приложения, Длинный опрос вместо вебхука, Три пути к теме: рубрика, своя тема, ссылка, Коды приглашений на сутки (+17 more)

### Community 15 - "Community 15"

Cohesion: 0.11
Nodes (20): кар() — адрес карточки с подписью, КЛЮЧ и AUTH — пропуск в API, Почему у всплывашки aria-live — без неё чтец экрана её не видит, Почему карточка из хранилища открывается только по подписи, Почему вне телеграма пропуском служит ключ из адреса, сказать() — всплывашка об итоге, зов() — POST-обёртка над fetch, Цех: верхний экран со станками (+12 more)

### Community 16 - "Community 16"

Cohesion: 0.16
Nodes (20): Глиф: стилизованная цифра 4 / четырёхлучевая вертушка, Светло-серая грань верхнего луча (объём знака), Риск: серая грань почти пропадает на светлом фоне, Лаймовая заливка знака (#C7E24B, бренд-акцент), Фирменный знак 4xTube (логотип для тёмных подложек), Прозрачный фон 512×512 RGBA, рассчитан на тёмную подложку, 3D-маскот: чёрный кот с лаймовыми глазами и швами, Мини-знак 4x в левом нижнем углу карточки (+12 more)

### Community 17 - "Community 17"

Cohesion: 0.17
Nodes (12): TikTok не принимает PNG: только JPEG или WebP до 1080p, Правила постбота: почему сделано именно так, Дедуп по сути, а не по заголовкам: одну мысль легко переупаковать, Кот на слайде живёт в своей колонке и уступает место тексту, а не наоборот, Правка поста сбрасывает посчитанные варианты площадок, Конвейер, остановившись, докладывает владельцу: тишина хуже сбоя, Первая строка описания это весь пост: до «ещё» видно около ста символов, Модель зовётся только по подписке через claude -p, платный API запрещён (+4 more)

### Community 18 - "Community 18"

Cohesion: 1.0
Nodes (2): Почему у анонса стримов своя вёрстка, Почему картинка не пересказывает пост

### Community 19 - "Community 19"

Cohesion: 1.0
Nodes (0): 

### Community 20 - "Community 20"

Cohesion: 1.0
Nodes (0): 

### Community 21 - "Community 21"

Cohesion: 1.0
Nodes (1): Три места: Vercel, мак, Telegram, Supabase

### Community 22 - "Community 22"

Cohesion: 1.0
Nodes (1): Очередь заданий связывает приложение и мак

### Community 23 - "Community 23"

Cohesion: 1.0
Nodes (1): Углы контента: закрытый список, идут по кругу

### Community 24 - "Community 24"

Cohesion: 1.0
Nodes (1): X и Threads: текст переписывается под площадку

### Community 25 - "Community 25"

Cohesion: 1.0
Nodes (1): TikTok берёт картинки только с подтверждённого домена

### Community 26 - "Community 26"

Cohesion: 1.0
Nodes (1): Почему разметка переводится в HTML

### Community 27 - "Community 27"

Cohesion: 1.0
Nodes (1): Почему карточку рисует браузер, а не нейросеть

### Community 28 - "Community 28"

Cohesion: 1.0
Nodes (1): Почему не выдумываются цифры

### Community 29 - "Community 29"

Cohesion: 1.0
Nodes (1): Почему публикуем от аккаунта, а не от бота

### Community 30 - "Community 30"

Cohesion: 1.0
Nodes (1): Опоздание больше трёх часов: пост в черновики

### Community 31 - "Community 31"

Cohesion: 1.0
Nodes (1): Время в UTC, зона именем, а не смещением

### Community 32 - "Community 32"

Cohesion: 1.0
Nodes (1): Второй проход по голосу: как это звучит

### Community 33 - "Community 33"

Cohesion: 1.0
Nodes (1): Копилка идей: материал днём, пишут вечером

### Community 34 - "Community 34"

Cohesion: 1.0
Nodes (1): Коды приглашений вместо зашитых id

### Community 35 - "Community 35"

Cohesion: 1.0
Nodes (1): Тестовый и основной канал, проверка прав на месте

### Community 36 - "Community 36"

Cohesion: 1.0
Nodes (1): Ничего не уходит в канал само

## Ambiguous Edges - Review These
- `Проверка подписи initData секретом из токена` → `Отдача слайдов через /api/slide`  [AMBIGUOUS]
  README.md · relation: conceptually_related_to
- `Светло-серая грань верхнего луча (объём знака)` → `Читаемость знака в мелком размере (16–64 px фавикон)`  [AMBIGUOUS]
  webapp/logo.png · relation: conceptually_related_to
- `Плашка «ПРЯМОЙ ЭФИР» с красной точкой` → `Красная точка эфира: rust #E2703A или чистый красный?`  [AMBIGUOUS]
  assets/stream_card.png · relation: conceptually_related_to
- `Лист доступа — кто может пользоваться` → `Terms of Service 4xTube Publisher`  [AMBIGUOUS]
  webapp/terms.html · relation: conceptually_related_to

## Knowledge Gaps
- **546 isolated node(s):** `Возвращает id пользователя, если подпись настоящая и свежая.`, `Выполняет одно задание. Возвращает номер поста, если он появился.`, `Набивает расписание вперёд: по посту на день в заданное время.`, `Спрашивает у телеграма, сколько людей увидело недавние посты.      Раз в полчаса`, `Одна строка о том, что работа началась. Остальное скажет «готово».` (+541 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 18`** (2 nodes): `Почему у анонса стримов своя вёрстка`, `Почему картинка не пересказывает пост`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `content.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `content.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `Три места: Vercel, мак, Telegram, Supabase`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `Очередь заданий связывает приложение и мак`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `Углы контента: закрытый список, идут по кругу`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `X и Threads: текст переписывается под площадку`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `TikTok берёт картинки только с подтверждённого домена`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `Почему разметка переводится в HTML`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `Почему карточку рисует браузер, а не нейросеть`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `Почему не выдумываются цифры`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `Почему публикуем от аккаунта, а не от бота`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `Опоздание больше трёх часов: пост в черновики`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Время в UTC, зона именем, а не смещением`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `Второй проход по голосу: как это звучит`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `Копилка идей: материал днём, пишут вечером`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `Коды приглашений вместо зашитых id`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `Тестовый и основной канал, проверка прав на месте`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `Ничего не уходит в канал само`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.