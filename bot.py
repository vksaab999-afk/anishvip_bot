import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "APNA_BOT_TOKEN_YAHAN_DALO"

async def get_message_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Yeh function aapke channel ya source chat se aane wale message ki ID seedha Render ke logs me print kar dega
    msg = update.message or update.channel_post
    if msg:
        logging.info(f"--- 🎯 MESSAGE ID MIL GAYI: {msg.message_id} ---")
        await msg.reply_text(f"Is message ki ID hai: {msg.message_id}")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Ye sabhi tarah ke messages (Text, Photo, Video, Audio) ko sun kar unki ID logs me de dega
    application.add_handler(MessageHandler(filters.ALL, get_message_id))
    
    application.run_polling()

if __name__ == "__main__":
    main()
