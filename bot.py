import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8855627842:AAFMuQjYinyAcDE-bRTy7gw9Tv6VPlqXp1Y"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ID Finder Live")

def run_web_server():
    server = HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8080))), SimpleHTTPRequestHandler)
    server.serve_forever()

async def get_message_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.channel_post
    if msg:
        logging.info(f"--- 🎯 MESSAGE ID MIL GAYI: {msg.message_id} ---")

def main():
    Thread(target=run_web_server, daemon=True).start()
    
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(MessageHandler(filters.ALL, get_message_id))
    app.run_polling()

if __name__ == "__main__":
    main()
