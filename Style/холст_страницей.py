# -*- coding: utf-8 -*-
"""Холст как страница-артефакт: `python3 холст_страницей.py <стиль>/холсты/<пост> [Имя]`

Зачем. Холсты стилей собираются помощником `seed-canvas.mjs` из скила `design`,
но в этой версии Claude Code его на диске нет (проверено 21.09.2026), и
`холст.py` стилей падает на последнем шаге, успев разложить доски `*.dc.html`.
Этот сборщик берёт готовые доски, снимает их безголовым Chrome и складывает
обычную страницу: три обложки сверху, кадры сеткой, подпись с хештегами.

Владелец на такой странице кадры не двигает, а смотрит и говорит словами —
осознанная замена, а не полноценный холст.
"""
import html
import json
import sys
from pathlib import Path

ТУТ = Path(__file__).resolve().parent
sys.path.insert(0, str(ТУТ.parent))
import браузер  # noqa: E402
from PIL import Image  # noqa: E402

Ш, В = 1080, 1440

ШАБЛОН = """<title>{имя}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
:root {{
  --грунт: #F3F2EC; --карта: #FFFFFF; --чернила: #16180F; --мягкий: #5C6152;
  --лайм: #7E9B12; --кайма: rgba(22,24,15,.12);
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --грунт: #101208; --карта: #191C10; --чернила: #F1F3EA; --мягкий: #9AA189;
    --лайм: #C7E24B; --кайма: rgba(241,243,234,.14);
  }}
}}
:root[data-theme="dark"] {{
  --грунт: #101208; --карта: #191C10; --чернила: #F1F3EA; --мягкий: #9AA189;
  --лайм: #C7E24B; --кайма: rgba(241,243,234,.14);
}}
body {{ background: var(--грунт); color: var(--чернила); margin: 0;
  font-family: Manrope, system-ui, sans-serif; font-size: 16px; line-height: 1.5; }}
.обёртка {{ max-width: 1180px; margin: 0 auto; padding-inline: 20px; padding-block: 40px 72px; }}
.метка {{ font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 12px;
  letter-spacing: .18em; text-transform: uppercase; color: var(--лайм); }}
h1 {{ font-size: clamp(28px, 5vw, 44px); font-weight: 800; letter-spacing: -.03em;
  margin: 10px 0 14px; text-wrap: balance; }}
.сводка {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 40px; }}
.факт {{ font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 12.5px;
  border: 1px solid var(--кайма); border-radius: 999px; padding: 5px 12px; color: var(--мягкий); }}
h2 {{ font-size: 20px; font-weight: 800; letter-spacing: -.02em; margin: 0 0 6px; }}
.подзаголовок {{ color: var(--мягкий); font-size: 14.5px; margin: 0 0 20px; max-width: 62ch; }}
section {{ margin-bottom: 52px; }}
.обложки {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }}
.кадры {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 18px; }}
figure {{ margin: 0; display: flex; flex-direction: column; gap: 8px; }}
figure img {{ width: 100%; display: block; border-radius: 10px; border: 1px solid var(--кайма); }}
figcaption {{ font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 11.5px;
  color: var(--мягкий); letter-spacing: .04em; }}
figcaption b {{ color: var(--чернила); font-weight: 600; }}
.подпись-поста {{ background: var(--карта); border: 1px solid var(--кайма); border-radius: 14px;
  padding: 22px; display: flex; flex-direction: column; gap: 14px; }}
.подпись-поста p {{ margin: 0; font-size: 17px; }}
.теги {{ font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 13px;
  color: var(--лайм); word-break: break-word; }}
@media (max-width: 640px) {{
  .обложки {{ grid-template-columns: 1fr; }}
  .кадры {{ grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }}
}}
</style>

<div class="обёртка">
  <header>
    <div class="метка">Холст согласования · TikTok · стиль «{стиль}»</div>
    <h1>{заголовок}</h1>
    <div class="сводка">{факты}</div>
  </header>

  <section>
    <h2>Три обложки</h2>
    <p class="подзаголовок">Три разных подхода к первому кадру. Скажи номер — он станет главным.</p>
    <div class="обложки">{обложки}</div>
  </section>

  <section>
    <h2>Кадры карусели</h2>
    <div class="кадры">{кадры}</div>
  </section>

  <section>
    <h2>Подпись</h2>
    <div class="подпись-поста">
      <p>{подпись}</p>
      <div class="теги">{теги}</div>
    </div>
  </section>
</div>
"""


def экр(т: str) -> str:
    return html.escape(т or "")


def снять(доска: Path, куда: Path) -> bool:
    """Доска снимается с `<base>` на свою папку: кот и логотип лежат рядом файлами,
    а браузер получает страницу строкой и без базы искал бы их в никуда."""
    ошибки: list = []
    html_ = доска.read_text().replace(
        "<head>", f'<head><base href="file://{доска.parent}/">', 1)
    if not браузер.снять(html_, Ш, В, куда, ошибки):
        print(доска.name, "не снялась", ошибки)
        return False
    with Image.open(куда) as и:
        и.convert("RGB").resize((Ш, В), Image.LANCZOS).save(куда)
    return True


def ужать(ис: Path, куда: Path, ширина: int = 640) -> None:
    with Image.open(ис) as и:
        и = и.convert("RGB")
        и.thumbnail((ширина, ширина * 2), Image.LANCZOS)
        к = 82
        while True:
            и.save(куда, quality=к, method=6)
            if куда.stat().st_size < 90_000 or к <= 45:
                break
            к -= 8


def main():
    папка = Path(sys.argv[1]).resolve()
    имя = sys.argv[2] if len(sys.argv) > 2 else папка.name
    стиль_имя = папка.parent.parent.name
    пост = json.loads((папка.parent.parent / "посты" / f"{папка.name}.json").read_text())

    доски = sorted(папка.glob("*.dc.html"))
    главная = [д for д in доски if д.name.startswith("Main")]
    обложки_д = [д for д in доски if д.name.startswith("Oblozhka")]
    кадры_д = [д for д in доски if not д.name.startswith(("Main", "Oblozhka"))]

    снимки = папка / "снимки"
    снимки.mkdir(exist_ok=True)
    for д in главная + кадры_д + обложки_д:
        png = снимки / f"{д.stem.replace('.dc', '')}.png"
        if not png.exists() and not снять(д, png):
            return
        ужать(png, папка / f"{png.stem}.webp")

    def карточка(файл: str, подпись: str) -> str:
        return (f'<figure><img src="{файл}" alt="{экр(подпись)}" loading="lazy">'
                f'<figcaption><b>{экр(подпись)}</b></figcaption></figure>')

    обложки = карточка("Main.webp", "Вариант 1 · главная")
    обложки += "".join(карточка(f"{д.stem.replace('.dc','')}.webp", f"Вариант {н}")
                       for н, д in enumerate(обложки_д, 2))
    кадры = карточка("Main.webp", "01 · Обложка")
    кадры += "".join(карточка(f"{д.stem.replace('.dc','')}.webp", д.stem.replace(".dc", ""))
                     for д in кадры_д)

    теги = пост.get("теги") or []
    хеш = [т for т in теги if т.startswith("#")]
    подпись = пост.get("подпись", "")
    страница = ШАБЛОН.format(
        имя=экр(имя), стиль=экр(стиль_имя),
        заголовок=экр(пост.get("название", имя)),
        факты="".join(f'<span class="факт">{экр(ф)}</span>'
                      for ф in (f"{len(кадры_д) + 1} кадров", f"стиль «{стиль_имя}»", "три обложки")),
        обложки=обложки, кадры=кадры,
        подпись=экр(подпись.split("\n")[0]),
        теги=экр(" ".join(хеш) if хеш else ""))
    (папка / "index.html").write_text(страница, encoding="utf-8")
    print("страница:", папка / "index.html", "| webp:", len(list(папка.glob("*.webp"))))


if __name__ == "__main__":
    main()
