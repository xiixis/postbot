# -*- coding: utf-8 -*-
"""Один живой безголовый Chrome на все кадры вместо запуска на каждый.

Раньше каждый замер и каждый снимок поднимали свой Chrome: на карусель из
десяти кадров выходило 59 запусков и 64 секунды (пост 96, 11 сентября 2026).
Через один живой браузер те же вызовы шли 4,5 секунды с теми же замерами.

У каждой рабочей нити своя вкладка. После двух минут простоя браузер гаснет
сам: на маке 16 ГБ, и держать гигабайт ради редких заказов незачем. Любой сбой
даёт None, и card рисует прежним путём через командную строку. В облачную копию
модуль не едет: там нет ни Chrome, ни websockets.
"""

import atexit
import base64
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

from websockets.sync.client import connect

import config

ПРОСТОЙ = 120        # секунд без работы, после которых браузер гаснет
ШАГ_СТОРОЖА = 15     # как часто сторож смотрит на простой
ОЖИДАНИЕ = 30        # предел на один ответ браузера

_замок = threading.Lock()
_своё = threading.local()
_браузер = {"процесс": None, "порт": None, "папка": None,
            "поколение": 0, "последний": 0.0, "в_работе": 0, "сторож": False}


def включён() -> bool:
    """ТЁПЛЫЙ_ХРОМ=0 возвращает всё на командную строку."""
    return os.getenv("ТЁПЛЫЙ_ХРОМ", "1") != "0" and bool(config.хром())


def _погасить() -> None:
    """Под замком."""
    п = _браузер["процесс"]
    if п is not None:
        п.terminate()
        try:
            п.wait(10)
        except subprocess.TimeoutExpired:
            п.kill()
    if _браузер["папка"]:
        shutil.rmtree(_браузер["папка"], ignore_errors=True)
    _браузер.update(процесс=None, порт=None, папка=None)


def _погасить_если_простаивает() -> bool:
    with _замок:
        if (_браузер["процесс"] is not None and _браузер["в_работе"] == 0
                and time.time() - _браузер["последний"] > ПРОСТОЙ):
            _погасить()
            return True
    return False


def _сторож() -> None:
    while True:
        time.sleep(ШАГ_СТОРОЖА)
        _погасить_если_простаивает()


def _поднять() -> int:
    """Под замком. Порт живого браузера; поднимает, если его нет."""
    п = _браузер["процесс"]
    if п is not None and п.poll() is None:
        return _браузер["порт"]
    _погасить()
    папка = Path(tempfile.mkdtemp(prefix="postbot-chrome-"))
    п = subprocess.Popen(
        [config.хром(), "--headless", "--remote-debugging-port=0",
         f"--user-data-dir={папка}", "--disable-gpu", "--no-sandbox",
         "--disable-dev-shm-usage", "--disable-background-networking",
         "--no-first-run", "--disable-extensions", "--disable-sync",
         "--disable-default-apps", "--mute-audio", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    файл = папка / "DevToolsActivePort"
    срок = time.time() + 15
    while time.time() < срок and п.poll() is None:
        строки = файл.read_text().split() if файл.exists() else []
        if строки:
            _браузер.update(процесс=п, порт=int(строки[0]), папка=папка,
                            поколение=_браузер["поколение"] + 1)
            if not _браузер["сторож"]:
                threading.Thread(target=_сторож, daemon=True).start()
                _браузер["сторож"] = True
            return _браузер["порт"]
        time.sleep(0.05)
    п.kill()
    shutil.rmtree(папка, ignore_errors=True)
    raise RuntimeError("безголовый Chrome не поднялся за 15 с")


class _Вкладка:
    def __init__(self, порт: int):
        запрос = urllib.request.Request(
            f"http://127.0.0.1:{порт}/json/new?about:blank", method="PUT")
        with urllib.request.urlopen(запрос, timeout=10) as ответ:
            данные = json.load(ответ)
        self.связь = connect(данные["webSocketDebuggerUrl"], max_size=None, open_timeout=10)
        self.н, self.события = 0, []
        self.позвать("Page.enable")
        self.позвать("Emulation.setDefaultBackgroundColorOverride",
                     {"color": {"r": 0x12, "g": 0x13, "b": 0x0F, "a": 1}})

    def _прочесть(self, срок: float) -> dict:
        return json.loads(self.связь.recv(timeout=max(0.05, срок - time.time())))

    def позвать(self, метод: str, параметры: dict | None = None) -> dict:
        self.н += 1
        self.связь.send(json.dumps({"id": self.н, "method": метод,
                                    "params": параметры or {}}))
        срок = time.time() + ОЖИДАНИЕ
        while True:
            м = self._прочесть(срок)
            if м.get("id") == self.н:
                if "error" in м:
                    raise RuntimeError(f"{метод}: {м['error']}")
                return м.get("result", {})
            if "method" in м:
                self.события.append(м["method"])

    def ждать(self, событие: str) -> None:
        срок = time.time() + ОЖИДАНИЕ
        while событие not in self.события:
            м = self._прочесть(срок)
            if "method" in м:
                self.события.append(м["method"])
        self.события.clear()

    def открыть(self, путь: Path, ширина: int, высота: int, масштаб: float) -> None:
        self.позвать("Emulation.setDeviceMetricsOverride",
                     {"width": ширина, "height": высота,
                      "deviceScaleFactor": масштаб, "mobile": False})
        # Командная строка прячет полосы прокрутки только у снимка.
        self.позвать("Emulation.setScrollbarsHidden", {"hidden": масштаб != 1})
        self.события.clear()
        self.позвать("Page.navigate", {"url": f"file://{путь}"})
        self.ждать("Page.loadEventFired")
        self.позвать("Runtime.evaluate", {"expression": "document.fonts.ready.then(() => 1)",
                                          "awaitPromise": True})

    def замер(self) -> dict:
        срок = time.time() + 10
        while time.time() < срок:
            р = self.позвать("Runtime.evaluate", {
                "expression": "document.body && document.body.getAttribute('data-замер')",
                "returnByValue": True})
            значение = р.get("result", {}).get("value")
            if значение:
                return json.loads(значение)
            time.sleep(0.01)
        return {}

    def снимок(self, куда: Path) -> None:
        р = self.позвать("Page.captureScreenshot", {"format": "png"})
        Path(куда).write_bytes(base64.b64decode(р["data"]))


def _работа(дело):
    if not включён():
        return None
    try:
        with _замок:
            порт = _поднять()
            вкладка = getattr(_своё, "вкладка", None)
            if вкладка is None or getattr(_своё, "поколение", -1) != _браузер["поколение"]:
                вкладка = _Вкладка(порт)
                _своё.вкладка, _своё.поколение = вкладка, _браузер["поколение"]
            _браузер["в_работе"] += 1
    except Exception:                                        # noqa: BLE001
        return None
    try:
        return дело(вкладка)
    except Exception:                                        # noqa: BLE001
        _своё.вкладка = None
        return None
    finally:
        with _замок:
            _браузер["в_работе"] -= 1
            _браузер["последний"] = time.time()


def _в_файл(страница: str) -> Path:
    config.ВЫВОД.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                     dir=config.ВЫВОД, encoding="utf-8") as f:
        f.write(страница)
    return Path(f.name)


def замерить(страница_с_замером: str, ширина: int, высота: int) -> dict | None:
    """Координаты блоков. None или {} — мерить старым путём."""
    def дело(вкладка):
        путь = _в_файл(страница_с_замером)
        try:
            вкладка.открыть(путь, ширина, высота, 1)
            return вкладка.замер()
        finally:
            путь.unlink(missing_ok=True)
    return _работа(дело)


def снять(страница: str, ширина: int, высота: int, куда: Path) -> bool:
    """Снимок в полуторном масштабе, как у командной строки. False — снять старым путём."""
    def дело(вкладка):
        путь = _в_файл(страница)
        try:
            вкладка.открыть(путь, ширина, высота, 1.5)
            вкладка.снимок(куда)
            return True
        finally:
            путь.unlink(missing_ok=True)
    return bool(_работа(дело))


@atexit.register
def _на_выходе() -> None:
    with _замок:
        _погасить()
