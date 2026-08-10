import os
import logging
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ChatJoinRequestHandler,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8855627842:AAFMuQjYinyAcDE-bRTy7gw9Tv6VPlqXp1Y" 
ADMIN_CHAT_ID = 5785924075  
MONGO_URI = "mongodb+srv://itsrealvijay1_db_user:vijay786482@cluster0.91gd3jb.mongodb.net/?appName=Cluster0"

SOURCE_CHAT_ID = 5785924075  
WELCOME_MSG_ID = 31      
VIDEO_MSG_ID = 33        
AUDIO_MSG_ID = 35        

REGISTRATION_LINK = "https://6club77.com/#/register?invitationCode=134575773989"
# =======================================================

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["telegram_bot_db"]
users_collection = db["users"]

def save_user_to_mongo(user_id, first_name, username):
    try:
        users_collection.update_one({"user_id": user_id}, {"$set": {"user_id": user_id, "first_name": first_name, "username": username}}, upsert=True)
    except Exception as e:
        logging.error(f"MongoDB Error: {e}")

# Keep-Alive
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Live!")

def run_web_server():
    server = HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8080))), SimpleHTTPRequestHandler)
    server.serve_forever()

# --- WELCOME CONTENT SENDER (Pehle wala working logic) ---
async def send_welcome_content(context: ContextTypes.DEFAULT_TYPE, user_id: int, first_name: str):
    try:
        welcome_text = f"Welcome {first_name} ❤️‍🔥\n\nLoss recover hoga... niche video dekho 💸"
        await context.bot.send_message(chat_id=user_id, text=welcome_text)

        keyboard = [[InlineKeyboardButton("Registration Link 🔗", url=REGISTRATION_LINK)]]
        
        sent_msg = await context.bot.copy_message(chat_id=user_id, from_chat_id=SOURCE_CHAT_ID, message_id=VIDEO_MSG_ID, reply_markup=InlineKeyboardMarkup(keyboard))
        await context.bot.pin_chat_message(chat_id=user_id, message_id=sent_msg.message_id)
        await context.bot.copy_message(chat_id=user_id, from_chat_id=SOURCE_CHAT_ID, message_id=AUDIO_MSG_ID)
    except Exception as e:
        logging.error(f"Error: {e}")

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    save_user_to_mongo(user.id, user.first_name, user.username)
    await send_welcome_content(context, user.id, user.first_name)
    # Request approve nahi kar rahe

# --- ADMIN COMMANDS ---
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_CHAT_ID:
        count = users_collection.count_documents({})
        await update.message.reply_text(f"📊 Total Users: {count}")

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_CHAT_ID and not update.message.text: # Agar message text nahi (video/photo) hai
        all_users = users_collection.find()
        for user in all_users:
            try:
                await context.bot.copy_message(chat_id=user["user_id"], from_chat_id=ADMIN_CHAT_ID, message_id=update.message.message_id)
            except: continue
        await update.message.reply_text("Broadcast Done!")

def main():
    Thread(target=run_web_server, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(handle_join_request))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(MessageHandler(filters.Chat(ADMIN_CHAT_ID) & ~filters.COMMAND, admin_broadcast))
    app.run_polling()

if __name__ == "__main__":
    main()
