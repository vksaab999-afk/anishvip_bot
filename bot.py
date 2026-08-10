import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

# Apna Bot Token yahan daalein
BOT_TOKEN = "8855627842:AAFMuQjYinyAcDE-bRTy7gw9Tv6VPlqXp1Y"

# Keep-Alive Web Server taaki Render par bot active rahe
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ID Finder Bot is Live!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

async def get_message_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.channel_post
    if msg:
        logging.info(f"--- 🎯 MESSAGE ID MIL GAYI: {msg.message_id} ---")

def main():
    Thread(target=run_web_server, daemon=True).start()

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.ALL, get_message_id))
    
    application.run_polling()

if __name__ == "__main__":
    main()
