import requests # type: ignore
from telegram import Bot, Update # type: ignore
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext # type: ignore
import threading
import time

# Configuracion
TOKEN = "7193589103:AAGK8lFn1lQ6Xbmupc9zc6RMcDAqKWxPayM"  # Reemplaza con tu token de @BotFather
CHAT_ID = "5397929116"   # Envía /start a @RawDataBot para obtenerlo

bot = Bot(token=TOKEN)
monitored_urls = {}  # Diccionario para guardar URLs a monitorear

# --- COMANDOS DEL BOT ---
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🎟️ **Bienvenido a TicketHunter**\n\n"
        "Envíame el link de un evento SOLD OUT y lo monitorearé cada 3 segundos.\n"
        "Comandos:\n"
        "/status → Ver estado del bot\n"
        "/monitor [URL] → Añadir evento\n"
        "/stop → Dejar de monitorear"
    )

def status(update: Update, context):
    update.message.reply_text("✅ **Bot activo!** Monitoreando eventos cada 3 segundos.")

def monitor(update: Update, context):
    url = " ".join(context.args)
    if not url.startswith("http"):
        update.message.reply_text("⚠️ ¡Debes enviar una URL válida! Ej: /monitor https://ra.com/evento123")
        return
    
    chat_id = update.message.chat_id
    monitored_urls[chat_id] = url  # Guarda la URL para este chat
    update.message.reply_text(f"🔍 **Monitoreando:** {url}")

    # Inicia el hilo de monitoreo
    threading.Thread(target=check_availability, args=(chat_id, url)).start()

def stop(update: Update, context):
    chat_id = update.message.chat_id
    if chat_id in monitored_urls:
        del monitored_urls[chat_id]
        update.message.reply_text("⏹️ **Monitoreo detenido.**")
    else:
        update.message.reply_text("❌ No hay eventos en monitoreo.")

# --- MONITOREO EN TIEMPO REAL ---
def check_availability(chat_id, url):
    while chat_id in monitored_urls:  # Solo si sigue activo
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=5)
            
            if "Tickets for this event are sold out" not in response.text.lower():
                bot.send_message(
                    chat_id=chat_id,
                    text=f"🚨 **¡ENTRADAS DISPONIBLES!** 🎟️\n{url}"
                )
                del monitored_urls[chat_id]  # Deja de monitorear
                break
            
            time.sleep(3)  # Espera 3 segundos entre checks
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

# --- INICIAR BOT ---
updater = Updater(token=TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(MessageHandler(filters.TEXT, otro_metodo))
updater.dispatcher.add_handler(CommandHandler("status", status))
updater.dispatcher.add_handler(CommandHandler("monitor", monitor))
updater.dispatcher.add_handler(CommandHandler("stop", stop))
updater.start_polling()
print("🤖 Bot activo! Usa /start en Telegram.")
updater.idle()
