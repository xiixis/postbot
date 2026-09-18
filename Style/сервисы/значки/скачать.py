"""Значки сервисов в полном размере: favicon сайта (gstatic, до 256 px), для мелких — иконка приложения из App Store.

python3 скачать.py — кладёт <имя>.png рядом; векторные (github, n8n, notebooklm, sheets) не трогает.
"""
import io, json, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image

ТУТ = Path(__file__).parent
UA = {"User-Agent": "Mozilla/5.0"}
САЙТЫ = {
    "chatgpt": "chatgpt.com", "perplexity": "perplexity.ai", "claude": "claude.ai", "gemini": "gemini.google.com",
    "zapier": "zapier.com", "make": "make.com", "activepieces": "activepieces.com",
    "veo": "deepmind.google", "kling": "klingai.com", "opusclip": "opus.pro",
    "did": "d-id.com", "canva": "canva.com",
    "leonardo": "leonardo.ai", "midjourney": "midjourney.com", "krea": "krea.ai", "higgsfield": "higgsfield.ai",
    "wan": "wan.video", "cursor": "cursor.com", "replit": "replit.com", "devin": "devin.ai",
    "scraperapi": "scraperapi.com", "rapidapi": "rapidapi.com", "apify": "apify.com",
    # пост «31 ИИ для монтажа», 17.09.2026; vidyo, timebolt, adobepodcast, auphonic, lumen5 отдают 32–64 px —
    # список.py рисует их буквой, крупнее значка у них нет ни на сайте, ни в App Store
    "descript": "descript.com", "wisecut": "wisecut.video", "autopod": "autopod.fm", "runway": "runwayml.com",
    "nova": "wearenova.ai", "kamua": "kamua.com", "cleanvoice": "cleanvoice.ai", "lalal": "lalal.ai",
    "moises": "moises.ai", "audiostrip": "audiostrip.com", "rask": "rask.ai", "colourlab": "colourlab.ai",
    "fylm": "fylm.ai", "topaz": "topazlabs.com", "nanobanana": "gemini.google.com",
    "vidyo": "quso.ai", "timebolt": "timebolt.io", "adobepodcast": "podcast.adobe.com", "auphonic": "auphonic.com",
    "lumen5": "lumen5.com",
}
# Сайты отдают favicon 48–64 px — берём иконку приложения (512 px) по запросу в App Store.
ПРИЛОЖЕНИЯ = {"capcut": "CapCut", "heygen": "HeyGen", "zeemo": "Zeemo"}  # Wan: в App Store только чужие приложения с тем же словом — значок с сайта, 64 px


def взять(адрес: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(адрес, headers=UA), timeout=30).read()


for имя, сайт in САЙТЫ.items():
    и = Image.open(io.BytesIO(взять("https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON"
                                   f"&fallback_opts=TYPE,SIZE,URL&url=https://{сайт}&size=256"))).convert("RGBA")
    и.save(ТУТ / f"{имя}.png", optimize=True)
    print(имя, и.size)
for имя, запрос in ПРИЛОЖЕНИЯ.items():
    ответ = json.loads(взять("https://itunes.apple.com/search?entity=software&limit=3&term=" + urllib.parse.quote(запрос)))
    for р in ответ.get("results", []):
        print(" ", имя, "→", р.get("trackName"), "|", р.get("sellerName"))
    if ответ.get("results"):
        р = ответ["results"][0]
        и = Image.open(io.BytesIO(взять(р["artworkUrl512"]))).convert("RGBA")
        и.save(ТУТ / f"{имя}.png", optimize=True)
        print(имя, и.size, "из App Store:", р.get("trackName"))
