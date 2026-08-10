import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8855627842:AAFMuQjYinyAcDE-bRTy7gw9Tv6VPlqXp1Y"

async def get_message_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.channel_post
    if msg:
        logging.info(f"--- 🎯 MESSAGE ID MIL GAYI: {msg.message_id} ---")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.ALL, get_message_id))
    
    print("Bot is running and listening for messages...")
    application.run_polling()

if __name__ == "__main__":
    main()
