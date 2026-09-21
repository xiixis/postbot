# -*- coding: utf-8 -*-
"""Новые позы кота под кадры «до-после»: python3 кот.py <имя> ["поза по-английски"]

Эталон и хромакей — те же, что у `postbot/mascot.py` (лист ракурсов reference.png и
синий #0047FF), но запрос идёт через Vertex, как у `картинка.py`: у ключа AI Studio
кончилась предоплата. Кот ложится в `коты/<имя>.png` уже вырезанным.
"""
import sys
import time
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent.parent))
import config  # noqa: E402
import mascot  # noqa: E402
import картинка  # noqa: E402

ПОЗЫ = {
    "над-краем": ("Peeking over a horizontal ledge from below: only the head, the top of the "
                  "shoulders and both front paws resting on the ledge are visible, looking down to "
                  "the left with curious big eyes. The body below the ledge is not drawn: the "
                  "character is cut off by a perfectly straight horizontal line at shoulder level."),
    "с-телефоном": ("Standing, happy, holding a smartphone in its left paw with the back of the phone "
                    "towards the viewer (dark grey back, no logo), and pointing to the left with the "
                    "right paw, full body."),
}


def main():
    имя = sys.argv[1]
    описание = sys.argv[2] if len(sys.argv) > 2 else ПОЗЫ[имя]
    папка = ТУТ / "коты"
    папка.mkdir(exist_ok=True)
    for попытка in range(3):
        сырое = папка / f"{имя}-сырое-{попытка}.png"
        сырое.write_bytes(картинка.нарисовать(mascot.ЭТАЛОН + описание, "1:1",
                                              [config.МАСКОТ / "reference.png"], "2K"))
        if not mascot._фон_чистый(сырое):
            print("фон не чистый, заново", flush=True)
            continue
        готово = mascot._снять_фон(сырое)
        готово.rename(папка / f"{имя}.png")
        print(папка / f"{имя}.png", flush=True)
        return
        time.sleep(20)
    print("не вышло:", имя, flush=True)


if __name__ == "__main__":
    main()
