import os
import json
import yt_dlp
from telegram import Bot
from pathlib import Path

# --- CONFIGURACIÓN ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHANNELS_FILE = "channels.json"
LAST_FILE = "last_videos.json"
TMP_FILE = Path("audio.mp3")

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_latest_video(channel_url):
    ydl_opts = {"quiet": True, "extract_flat": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        entries = info.get("entries", [])
        if not entries:
            return None
        latest = entries[0]
        vid = latest.get("id")
        title = latest.get("title")
        return vid, title, f"https://www.youtube.com/watch?v={vid}"

def download_audio(video_url):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(TMP_FILE.with_suffix(".%(ext)s")),
        "quiet": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    mp3_path = TMP_FILE.with_suffix(".mp3")
    return mp3_path if mp3_path.exists() else None

def send_mp3(bot, chat_id, mp3_path, title):
    with open(mp3_path, "rb") as f:
        bot.send_audio(chat_id=chat_id, audio=f, title=title)

def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    channels = load_json(CHANNELS_FILE)
    last_videos = load_json(LAST_FILE)

    for name, url in channels.items():
        try:
            result = get_latest_video(url)
            if not result:
                print(f"No se pudo obtener vídeos de {name}")
                continue
            vid, title, video_url = result
            if last_videos.get(name) == vid:
                print(f"Sin nuevos vídeos en {name}")
                continue

            print(f"Nuevo vídeo detectado en {name}: {title}")
            mp3 = download_audio(video_url)
            if mp3:
                send_mp3(bot, CHAT_ID, mp3, title)
                mp3.unlink(missing_ok=True)
                last_videos[name] = vid
                save_json(last_videos, LAST_FILE)
        except Exception as e:
            print(f"Error con {name}: {e}")

if __name__ == "__main__":
    main()
