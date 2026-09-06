# -*- coding: utf-8 -*-
"""Расшифровка голосовых заметок.

Идея приходит на ходу, и надиктовать её проще, чем набрать. Бот скачивает
голосовое, распознаёт речь и дальше обращается с ней как с обычным текстом.

Два пути, и первый лучше. Whisper работает прямо на маке: бесплатно, без сети
и заметно точнее на русском. Если его нет (например, бот подняли на чужой
машине), заметку слушает Gemini тем же ключом, что рисует картинки.

Модель держим загруженной между вызовами: она поднимается три секунды, а сама
расшифровка занимает две.
"""

import base64
import os
import tempfile
from pathlib import Path

import requests

import config

РАЗМЕР = os.getenv("WHISPER_MODEL", "small").strip()
_модель = None
_нет_whisper = False

API = "https://generativelanguage.googleapis.com/v1beta/models/{модель}:generateContent"
ЗАПАСНАЯ = os.getenv("VOICE_MODEL", "gemini-2.5-flash").strip()

ЗАДАЧА = ("Это голосовая заметка на русском языке. Запиши её текстом дословно, "
          "без пересказа и без комментариев. Убери только слова-паразиты и "
          "оговорки, если человек поправил сам себя. В ответ верни ТОЛЬКО текст "
          "заметки.")


def _whisper():
    """Ленивая загрузка модели. None, если whisper недоступен."""
    global _модель, _нет_whisper
    if _модель is not None or _нет_whisper:
        return _модель
    try:
        from faster_whisper import WhisperModel
        _модель = WhisperModel(РАЗМЕР, device="cpu", compute_type="int8")
    except Exception:                                        # noqa: BLE001
        _нет_whisper = True
    return _модель


def доступна() -> bool:
    return bool(config.КЛЮЧ_GEMINI) or _whisper() is not None


def _местным(файл: Path) -> str | None:
    модель = _whisper()
    if модель is None:
        return None
    try:
        куски, _ = модель.transcribe(str(файл), language="ru", beam_size=5)
        return " ".join(к.text.strip() for к in куски).strip() or None
    except Exception:                                        # noqa: BLE001
        return None


def _через_сеть(звук: bytes, тип: str) -> str | None:
    if not config.КЛЮЧ_GEMINI:
        return None
    тело = {"contents": [{"role": "user", "parts": [
        {"text": ЗАДАЧА},
        {"inlineData": {"mimeType": тип,
                        "data": base64.b64encode(звук).decode()}}]}]}
    try:
        о = requests.post(API.format(модель=ЗАПАСНАЯ),
                          headers={"x-goog-api-key": config.КЛЮЧ_GEMINI,
                                   "Content-Type": "application/json"},
                          json=тело, timeout=180)
        о.raise_for_status()
        части = о.json()["candidates"][0]["content"]["parts"]
        return " ".join(ч.get("text", "") for ч in части).strip() or None
    except Exception:                                        # noqa: BLE001
        return None


def расшифровать(звук: bytes, тип: str = "audio/ogg") -> str | None:
    """Текст голосового или None, если не вышло ни одним способом."""
    if not звук:
        return None
    хвост = ".oga" if "ogg" in тип else ".m4a" if "mp4" in тип else ".wav"
    with tempfile.NamedTemporaryFile(suffix=хвост, delete=False) as f:
        f.write(звук)
        путь = Path(f.name)
    try:
        return _местным(путь) or _через_сеть(звук, тип)
    finally:
        путь.unlink(missing_ok=True)
