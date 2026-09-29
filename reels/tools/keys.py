# Звуки клавиатуры для набора текста в роликах: python tools/keys.py
# Пишет public/sfx/key-1.wav … key-5.wav и key-space.wav.
#
# Один и тот же щелчок, повторённый пятнадцать раз с ровным шагом, звучит как метроном.
# Здесь у каждой клавиши свой тон, а нажатие собрано из трёх частей, как у настоящей:
# короткий щелчок, глухой удар о дно и тихий отскок при отпускании.
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
КУДА = Path(__file__).resolve().parent.parent / "public" / "sfx"


def затухание(длина_с: float, спад_с: float) -> np.ndarray:
    t = np.arange(int(SR * длина_с)) / SR
    return np.exp(-t / спад_с)


def шум(длина_с: float, спад_с: float, полоса, зерно: int) -> np.ndarray:
    г = np.random.default_rng(зерно)
    с = г.standard_normal(int(SR * длина_с))
    с = sosfilt(butter(2, полоса, "band", fs=SR, output="sos"), с)
    return с * затухание(длина_с, спад_с)


def тон(длина_с: float, спад_с: float, гц: float) -> np.ndarray:
    t = np.arange(int(SR * длина_с)) / SR
    # тон чуть падает за время удара: так звучит корпус, а не генератор
    фаза = 2 * np.pi * гц * (t - 0.18 * t * t / длина_с)
    return np.sin(фаза) * затухание(длина_с, спад_с)


def клавиша(гц: float, зерно: int, глубже: bool = False) -> np.ndarray:
    длина = 0.2
    звук = np.zeros(int(SR * длина))

    def положить(кусок: np.ndarray, когда_с: float, сила: float) -> None:
        а = int(SR * когда_с)
        б = min(len(звук), а + len(кусок))
        звук[а:б] += кусок[: б - а] * сила

    спад = 0.05 if глубже else 0.034
    положить(шум(0.02, 0.0035, [1800, 5200], зерно), 0.0, 0.55)            # щелчок
    положить(тон(0.16, спад, гц), 0.002, 0.9)                              # удар о дно
    положить(тон(0.08, спад * 0.4, гц * 2.63), 0.002, 0.22)                # призвук корпуса
    положить(шум(0.05, 0.012, [500, 1800], зерно + 7), 0.003, 0.3)         # глухой шорох
    отскок = 0.095 if глубже else 0.072
    положить(шум(0.015, 0.003, [2200, 6000], зерно + 13), отскок, 0.16)    # отпускание
    положить(тон(0.05, 0.014, гц * 1.4), отскок, 0.12)

    звук = sosfilt(butter(2, 7000, "low", fs=SR, output="sos"), звук)
    звук[: int(SR * 0.001)] *= np.linspace(0, 1, int(SR * 0.001))
    return звук / np.abs(звук).max() * 0.8


def записать(имя: str, звук: np.ndarray) -> None:
    КУДА.mkdir(parents=True, exist_ok=True)
    with wave.open(str(КУДА / имя), "wb") as ф:
        ф.setnchannels(1)
        ф.setsampwidth(2)
        ф.setframerate(SR)
        ф.writeframes((звук * 32767).astype("<i2").tobytes())
    print(имя, f"{len(звук) / SR:.2f} с")


if __name__ == "__main__":
    for н, гц in enumerate([212, 236, 196, 252, 224], 1):
        записать(f"key-{н}.wav", клавиша(гц, зерно=н * 11))
    записать("key-space.wav", клавиша(148, зерно=99, глубже=True))
