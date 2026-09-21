# -*- coding: utf-8 -*-
"""Холст согласования: `python3 холст.py посты/<пост>.json` → холсты/<пост>/

Собирает страницу-артефакт: три обложки, кадры карусели, подпись с хештегами и
список того, что проверено. Кадры ужимаются в webp, чтобы страница осталась лёгкой.

Помощника `seed-canvas.mjs` из скила `design` в этой версии Claude Code нет
(проверено 21.09.2026), поэтому холст — обычная страница, а не доски, которые
владелец двигает мышью. Он смотрит и говорит словами, что менять.
"""
import html
import json
import sys
from pathlib import Path

from PIL import Image

ТУТ = Path(__file__).parent

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
button {{ align-self: flex-start; font: inherit; font-weight: 700; font-size: 14px;
  background: var(--лайм); color: var(--грунт); border: 0; border-radius: 8px;
  padding: 9px 16px; cursor: pointer; }}
button:focus-visible {{ outline: 2px solid var(--чернила); outline-offset: 2px; }}
ul.проверки {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 9px; }}
ul.проверки li {{ display: flex; gap: 10px; align-items: baseline; font-size: 15px; }}
ul.проверки li::before {{ content: "✓"; color: var(--лайм); font-weight: 800; }}
.источник {{ font-size: 14px; color: var(--мягкий); border-left: 2px solid var(--лайм);
  padding-left: 14px; }}
@media (max-width: 640px) {{
  .обложки {{ grid-template-columns: 1fr; }}
  .кадры {{ grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }}
}}
</style>

<div class="обёртка">
  <header>
    <div class="метка">Холст согласования · TikTok · стиль «сводка»</div>
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
    <p class="подзаголовок">{про_кадры}</p>
    <div class="кадры">{кадры}</div>
  </section>

  <section>
    <h2>Подпись</h2>
    <div class="подпись-поста">
      <p>{подпись}</p>
      <div class="теги">{теги}</div>
      <button id="копировать" type="button">Скопировать подпись</button>
    </div>
  </section>

  <section>
    <h2>Что проверено</h2>
    <ul class="проверки">{проверки}</ul>
  </section>

  <section>
    <h2>Откуда взято</h2>
    <p class="источник">{источник}</p>
  </section>
</div>

<script>
  document.getElementById("копировать").addEventListener("click", async (е) => {{
    const текст = {подпись_js};
    try {{
      await navigator.clipboard.writeText(текст);
      е.target.textContent = "Скопировано";
      setTimeout(() => (е.target.textContent = "Скопировать подпись"), 1800);
    }} catch {{
      е.target.textContent = "Скопировать не вышло, выдели вручную";
    }}
  }});
</script>
"""


def экр(т: str) -> str:
    return html.escape(т or "")


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
    файл = Path(sys.argv[1])
    П = json.loads(файл.read_text())
    исходные = ТУТ / "картинки" / файл.stem
    папка = ТУТ / "холсты" / файл.stem
    папка.mkdir(parents=True, exist_ok=True)

    кадры_ф = sorted(п for п in исходные.glob("*.png") if not п.stem.startswith("oblozhka"))
    обложки_ф = sorted(исходные.glob("oblozhka*.png"))
    for п in кадры_ф + обложки_ф:
        ужать(п, папка / f"{п.stem}.webp")

    подписи = ["01 · Обложка"] + [f"{н:02d} · {с['рубрика']}" for н, с in enumerate(П["кадры"], 2)]
    подписи.append(f"{len(П['кадры']) + 2:02d} · Финал")
    кадры = "".join(
        f'<figure><img src="{п.stem}.webp" alt="{экр(подписи[н])}" loading="lazy">'
        f'<figcaption><b>{подписи[н].split(" · ")[0]}</b> · '
        f'{экр(подписи[н].split(" · ", 1)[1])}</figcaption></figure>'
        for н, п in enumerate(кадры_ф) if н < len(подписи))

    имена_обложек = ["Вариант 1 · главная"] + [
        f"Вариант {н} · {з['рубрика']}" for н, з in enumerate(П.get("запасные_обложки") or [], 2)]
    обложки = (f'<figure><img src="{кадры_ф[0].stem}.webp" alt="Обложка 1">'
               f'<figcaption><b>{имена_обложек[0]}</b></figcaption></figure>')
    обложки += "".join(
        f'<figure><img src="{п.stem}.webp" alt="{экр(имена_обложек[н])}">'
        f'<figcaption><b>{экр(имена_обложек[н])}</b></figcaption></figure>'
        for н, п in enumerate(обложки_ф, 1) if н < len(имена_обложек))

    х = П.get("холст", {})
    страница = ШАБЛОН.format(
        имя=экр(х.get("имя") or П["название"]),
        заголовок=экр(П["обложка"]["заголовок"]),
        факты="".join(f'<span class="факт">{экр(ф)}</span>' for ф in х.get("факты", [])),
        обложки=обложки, кадры=кадры,
        про_кадры=экр(х.get("про_кадры", "")),
        подпись=экр(П["подпись"]), теги=экр(" ".join(П["хештеги"])),
        подпись_js=json.dumps(П["подпись"] + "\n\n" + " ".join(П["хештеги"]), ensure_ascii=False),
        проверки="".join(f"<li>{экр(п)}</li>" for п in х.get("проверки", [])),
        источник=экр(х.get("источник", "")))

    (папка / "index.html").write_text(страница, encoding="utf-8")
    print("холст:", папка / "index.html", "| файлов:", len(list(папка.glob("*.webp"))))


if __name__ == "__main__":
    main()
