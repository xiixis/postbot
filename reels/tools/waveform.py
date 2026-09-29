# Форма волны музыки для дорожки звука: python tools/waveform.py <музыка> <столбиков> <куда.ts>
# Громкость считается по настоящей записи: дорожка в ролике показывает ту музыку, что в нём звучит.
import subprocess
import sys

import numpy as np

музыка, столбиков, куда = sys.argv[1], int(sys.argv[2]), sys.argv[3]
сырое = subprocess.run(["ffmpeg", "-v", "error", "-i", музыка, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                       check=True, capture_output=True).stdout
звук = np.frombuffer(сырое, dtype=np.int16).astype(np.float64) / 32768
части = np.array_split(звук[: 8000 * 15], столбиков)
сила = np.array([np.sqrt(np.mean(ч ** 2)) for ч in части])
сила = (сила / сила.max()) ** 0.7
with open(куда, "w", encoding="utf-8") as ф:
    ф.write("// Громкость музыки ролика по столбикам, от 0 до 1. Посчитана из записи: tools/waveform.py.\n")
    ф.write("export const WAVE = [" + ", ".join(f"{с:.2f}" for с in сила) + "];\n")
print(куда, len(сила), "столбиков; тише всего", f"{сила.min():.2f}", "громче всего", f"{сила.max():.2f}")
