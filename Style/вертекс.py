# -*- coding: utf-8 -*-
"""Доступ к Gemini через Vertex AI — на кредитах Google Cloud, а не на предоплате AI Studio.

Зачем отдельный путь. Ключ AI Studio (`generativelanguage.googleapis.com`) тратит
предоплаченные кредиты проекта, и они кончились: сервис отвечает «Your prepayment credits
are depleted». У проекта при этом остаются бесплатные кредиты Google Cloud, но они
списываются только через Vertex — другой адрес и другая авторизация.

Авторизация здесь не ключом-строкой, а сервисным аккаунтом: его JSON лежит в общем
облаке рядом с остальными ключами, приезжает в память и пишется во временный файл — иначе
`google.auth` его не прочитает. Файл убирается при выходе из процесса.

Проект и регион те же, что у конвейера 4xTube: `xtube-4x-covers`, `us-central1`.
"""
from __future__ import annotations

import atexit
import os
import sys
import subprocess
import tempfile
from pathlib import Path

ПРОЕКТ = os.getenv("GCP_PROJECT", "xtube-4x-covers")
РЕГИОН = os.getenv("GCP_REGION", "us-central1")
ПОИСКОВИК = Path("/Users/xiix/4xSoft/yt-searcher")

_временный: Path | None = None
_учётки = None


def _убрать_временный() -> None:
    if _временный:
        try:
            _временный.unlink(missing_ok=True)
        except OSError:
            pass


atexit.register(_убрать_временный)


def ключ_сервисного_аккаунта() -> str:
    """Путь к файлу сервисного ключа. Берётся из общего облака, кладётся во временный
    файл с правами только для владельца и удаляется при выходе."""
    global _временный
    if _временный and _временный.is_file():
        return str(_временный)

    уже = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if уже and Path(уже).is_file():
        return уже

    # Ключ достаёт отдельный процесс, запущенный в папке 4xTube. Так надёжнее, чем
    # импортировать его модуль к себе: постбот держит в окружении свои SUPABASE_URL и
    # SUPABASE_KEY — для файлов канала, от другой роли, — и модуль облака берёт их вместо
    # своих, после чего Supabase отвечает «No suitable key was found to decode the JWT».
    # Дочерний процесс стартует с чистым окружением и читает настройки 4xTube сам.
    чужие = {и: з for и, з in os.environ.items()
             if not и.startswith(("SUPABASE_", "GEMINI_", "ANTHROPIC_"))}
    добыча = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, '.');"
         "from app import cloud;"
         "print(next((с.get('value','') for с in cloud.team_keys()"
         " if (с.get('service') or '').lower() == 'vertex'), ''), end='')"],
        cwd=str(ПОИСКОВИК), capture_output=True, text=True, env=чужие, timeout=90)
    if добыча.returncode:
        raise SystemExit("облако не отдало ключ vertex: "
                         + добыча.stderr.strip().splitlines()[-1][:200])
    тело = добыча.stdout.strip()
    if not тело:
        raise SystemExit("в облаке нет ключа vertex — проверьте вкладку ключей в 4xTube")

    ярлык, имя = tempfile.mkstemp(prefix="4x-vertex-", suffix=".json")
    with os.fdopen(ярлык, "w", encoding="utf-8") as ф:
        ф.write(тело)
    os.chmod(имя, 0o600)
    _временный = Path(имя)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = имя
    return имя


def заголовки() -> dict:
    """Bearer-токен Vertex. Учётки берутся один раз и обновляются по сроку."""
    global _учётки
    import google.auth                                          # noqa: PLC0415
    from google.auth.transport.requests import Request          # noqa: PLC0415

    ключ_сервисного_аккаунта()
    if _учётки is None:
        _учётки, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"])
    if not _учётки.valid:
        _учётки.refresh(Request())
    return {"Authorization": f"Bearer {_учётки.token}", "Content-Type": "application/json"}


def адрес(модель: str) -> str:
    """Адрес модели. Nano Banana второго поколения (`gemini-3-*`) доступен только в
    локации global и на другом базовом хосте — в обычном регионе его просто нет, и
    Vertex отвечает 404 «model was not found». Правило подсмотрено у конвейера 4xTube."""
    if str(модель).startswith("gemini-3"):
        return (f"https://aiplatform.googleapis.com/v1/projects/{ПРОЕКТ}"
                f"/locations/global/publishers/google/models/{модель}:generateContent")
    return (f"https://{РЕГИОН}-aiplatform.googleapis.com/v1/projects/{ПРОЕКТ}"
            f"/locations/{РЕГИОН}/publishers/google/models/{модель}:generateContent")
