import os
import feedparser
import telebot

# Leer las variables secretas desde GitHub Actions
BOT_TOKEN = os.getenv(TELEGRAM_BOT_TOKEN)
CHANNEL_RSS = "https://www.youtube.com/feeds/videos.xml?channel_id=UCBYyJBCtCvgqA4NwtoPMwpQ"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Variable global para recordar el último vídeo procesado
last_video = None

def check_new_video():
    global last_video
    feed = feedparser.parse(CHANNEL_RSS)
    latest = feed.entries[0]
    video_id = latest.yt_videoid
    title = latest.title
    link = latest.link

    # Si hay un vídeo nuevo
    if video_id != last_video:
        last_video = video_id
        # Envía el aviso a tu chat (más adelante puedes añadir filtros por duración)
        bot.send_message(YOUR_CHAT_ID, f"🎥 Nuevo vídeo: {title}\n{link}")

# Prueba básica
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hola 👋, estaré pendiente del canal de Jordi Wild.")

bot.polling()
