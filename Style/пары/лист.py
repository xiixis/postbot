"""Лист кадров для глаз: python3 лист.py кадры/<пост> [куда.png]"""
import sys
from pathlib import Path
from PIL import Image
папка = Path(sys.argv[1]); кадры = sorted(папка.glob("[0-9][0-9].png"))
ш, в, отступ = 405, 540, 16
лист = Image.new("RGB", (4 * (ш + отступ) + отступ, ((len(кадры) + 3) // 4) * (в + отступ) + отступ), (60, 60, 60))
for н, к in enumerate(кадры):
    with Image.open(к) as и:
        лист.paste(и.convert("RGB").resize((ш, в), Image.LANCZOS), (отступ + н % 4 * (ш + отступ), отступ + н // 4 * (в + отступ)))
куда = Path(sys.argv[2]) if len(sys.argv) > 2 else папка / "лист.png"
лист.save(куда); print(куда)
