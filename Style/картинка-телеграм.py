# -*- coding: utf-8 -*-
"""Картинка к посту в Telegram-канал: python3 картинка-телеграм.py <файл.json> [куда.jpg]

Формат 1280×720: Telegram показывает превью поста широким, вертикаль он обрезает.
Рисуется тем же безголовым Chrome, что и кадры каруселей, шрифты и лайм — из `стиль.py`.

Файл описания (JSON): `над`, `заголовок`, `под`, `метка`, `кот` ({поза, высота, left/right/bottom}).
"""
import json
import sys
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ))
import стиль  # noqa: E402
sys.path.insert(0, str(стиль.ПОСТБОТ))
import браузер  # noqa: E402

Ш, В = 1280, 720
ГРУНТ, ТЕКСТ, ТИХИЙ = "#0B0C0A", "#F1F3EA", "#9DA291"
К = "font-family: Onest, sans-serif; font-weight: 800; letter-spacing: -0.03em"
Т = "font-family: Golos, sans-serif"


def волна(столбиков: int = 42) -> str:
    """Звуковая дорожка: высоты повторяемые, чтобы картинка не менялась от запуска к запуску."""
    import hashlib
    куски = []
    for i in range(столбиков):
        высота = 16 + int(hashlib.sha1(f"волна{i}".encode()).hexdigest()[:4], 16) % 78
        куски.append(f'<span style="flex:1;height:{высота}px;border-radius:5px;background:{стиль.ЛАЙМ};'
                     f'opacity:{.3 + высота / 160:.2f}"></span>')
    return "".join(куски)


def страница(о: dict) -> str:
    кот = стиль.кот(о["кот"]["поза"], о["кот"]["высота"],
                    **{к: v for к, v in о["кот"].items() if к in ("left", "right", "top", "bottom")})
    return f"""<!doctype html><meta charset=utf-8><style>
{стиль.фейсы(("Onest", "onest-800", 800), ("Golos", "golos-400", 400), ("Golos", "golos-700", 700))}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{Ш}px;height:{В}px;background:{ГРУНТ};color:{ТЕКСТ};overflow:hidden}}
.свет{{position:absolute;inset:0;background:
  radial-gradient(60% 70% at 78% 40%, rgba(199,226,75,.20), transparent 70%),
  radial-gradient(50% 60% at 10% 90%, rgba(255,255,255,.05), transparent 70%)}}
/* Левая колонка — поток, а не слои: блоки раздвигают друг друга и не могут наехать. */
.колонка{{position:absolute;left:80px;top:74px;bottom:74px;width:660px;display:flex;
  flex-direction:column;align-items:flex-start;gap:22px}}
.над{{{Т};font-weight:700;font-size:26px;letter-spacing:.14em;
  text-transform:uppercase;color:{стиль.ЛАЙМ}}}
.заголовок{{{К};font-size:70px;line-height:1.04}}
.под{{{Т};font-size:29px;line-height:1.35;color:{ТИХИЙ}}}
.метка{{margin-top:auto;display:inline-flex;align-items:center;gap:18px;
  padding:16px 30px;border-radius:999px;background:{стиль.ЛАЙМ};color:#16200A;{Т};font-weight:700;font-size:30px}}
.волна{{align-self:stretch;display:flex;align-items:center;gap:6px;height:62px}}
.кот{{position:absolute;z-index:2}}
.знак{{position:absolute;right:70px;top:70px;height:44px;opacity:.9}}
</style><body>
<div class=свет></div>
<div class=колонка>
  <div class=над>{о['над']}</div>
  <div class=заголовок>{о['заголовок']}</div>
  <div class=под>{о['под']}</div>
  <div class=волна>{волна()}</div>
  <div class=метка>🎙 {о['метка']}</div>
</div>
{кот}
<img class=знак src="{стиль.ЛОГО}">
</body>"""


def main():
    описание = json.loads(Path(sys.argv[1]).read_text())
    куда = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.home() / "Desktop" / "картинка.jpg"
    временный = куда.with_suffix(".png")
    if not браузер.снять(страница(описание), Ш, В, временный):
        raise SystemExit("картинка не вышла")
    from PIL import Image
    with Image.open(временный) as и:
        и.convert("RGB").resize((Ш, В), Image.LANCZOS).save(куда, quality=92)
    временный.unlink(missing_ok=True)
    print(куда, f"{куда.stat().st_size // 1024} КБ", flush=True)


if __name__ == "__main__":
    main()
