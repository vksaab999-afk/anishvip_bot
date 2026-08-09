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

# Logging Setup
logging.basicConfig(level=logging.INFO)

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8855627842:AAFMuQjYinyAcDE-bRTy7gw9Tv6VPlqXp1Y" 
ADMIN_CHAT_ID = 5785924075  # Aapki Admin Telegram ID

# MongoDB Atlas URI (Aapka banaya hua link)
MONGO_URI = "mongodb+srv://itsrealvijay1_db_user:vijay@786482@cluster0.91gd3jb.mongodb.net/?appName=Cluster0"

# Jis Channel se media copy karna hai uski Chat ID (Jahan aap content rakhoge)
SOURCE_CHAT_ID = 5785924075  
WELCOME_MSG_ID = 12      # Text Welcome Message ID
VIDEO_MSG_ID = 20        # Tutorial Video Message ID
AUDIO_MSG_ID = 22        # Audio Note Message ID

REGISTRATION_LINK = "https://dhaniwin77.com/register?inviteCode=MZP7BDN&from=web"
# =======================================================

# --- MONGODB SETUP ---
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["telegram_bot_db"]
users_collection = db["users"]

def save_user_to_mongo(user_id, first_name, username):
    try:
        users_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "first_name": first_name,
                    "username": username
                }
            },
            upsert=True
        )
    except Exception as e:
        logging.error(f"MongoDB Error: {e}")

# --- KEEP-ALIVE WEB SERVER (24x7 Uptime) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Live and 24x7 Active!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

# --- WELCOME CONTENT SENDER FUNCTION ---
async def send_welcome_content(context: ContextTypes.DEFAULT_TYPE, user_id: int, first_name: str):
    try:
        welcome_text = (
            f"Welcome {first_name} ❤️‍🔥\n\n"
            f"Yrr aapne colour trading me aaj tak kitna bhi loss kia ho no problem sab recover ho jayega\n\n"
            f"100%\n\n"
            f"Niche ka video pura dekho or paisa chapo💸\n"
            f"⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️"
        )
        await context.bot.send_message(chat_id=user_id, text=welcome_text)

        keyboard = [
            [InlineKeyboardButton("Download Vip Hack 📥", callback_data="download_hack")],
            [InlineKeyboardButton("Registration Link 🔗", url=REGISTRATION_LINK)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Video Message Copy
        sent_msg = await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=SOURCE_CHAT_ID,
            message_id=VIDEO_MSG_ID,
            reply_markup=reply_markup
        )

        # Pin Video Message
        try:
            if sent_msg and hasattr(sent_msg, 'message_id'):
                await context.bot.pin_chat_message(
                    chat_id=user_id,
                    message_id=sent_msg.message_id
                )
        except Exception as pin_err:
            logging.error(f"Pin error: {pin_err}")

        # Audio Message Copy
        await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=SOURCE_CHAT_ID,
            message_id=AUDIO_MSG_ID
        )
    except Exception as e:
        logging.error(f"Could not send welcome content to user {user_id}: {e}")

# --- JOIN REQUEST HANDLER (Works for Any Channel where bot is Admin) ---
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    user = request.from_user
    
    save_user_to_mongo(user.id, user.first_name, user.username)
    await send_welcome_content(context, user.id, user.first_name)
    
    try:
        await request.approve()
    except Exception:
        pass

# --- ADMIN STATS COMMAND ---
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_CHAT_ID:
        return
    
    total_users = users_collection.count_documents({})
    await update.message.reply_text(f"📊 **Bot Statistics:**\n\nTotal Users in Database: `{total_users}`", parse_mode="Markdown")

# --- UNIVERSAL BROADCAST SYSTEM FOR ADMIN ---
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_CHAT_ID:
        return

    # Agar admin ne koi command bheji hai (jaise /stats), toh broadcast mat karo
    if update.message.text and update.message.text.startswith("/"):
        return

    all_users = users_collection.find({}, {"user_id": 1})
    success_count = 0
    fail_count = 0

    for user in all_users:
        target_id = user["user_id"]
        try:
            # Admin jo bhi bhejega (Photo, Video, Text, Audio, Document), wo sab copy ho jayega
            await context.bot.copy_message(
                chat_id=target_id,
                from_chat_id=ADMIN_CHAT_ID,
                message_id=update.message.message_id
            )
            success_count += 1
            await asyncio.sleep(0.05)  # Telegram flood limit bachane ke liye chota gap
        except Exception:
            fail_count += 1

    await update.message.reply_text(f"✅ Broadcast Complete!\n\nSuccessful: {success_count}\nFailed: {fail_count}")

# --- MAIN FUNCTION ---
def main():
    # Start Keep-Alive Server in Background
    server_thread = Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(ChatJoinRequestHandler(handle_join_request))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.Chat(ADMIN_CHAT_ID) & ~filters.COMMAND, admin_broadcast))

    logging.info("Bot is starting with 24x7 Web Server...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
