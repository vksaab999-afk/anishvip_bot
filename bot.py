import os
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram import Client, filters
from pyrogram.types import Message

# Logging setup
logging.basicConfig(level=logging.INFO)

# API Credentials (Apna API_ID aur API_HASH yahan check kar lena agar zaroorat ho)
API_ID = 29949646
API_HASH = "8e9b4662d55e8250005d54aefcb5168e"
BOT_TOKEN = "8855627842:AAFMuQjYinyAcDE-bRTy7gw9Tv6VPlqXp1Y"

# Updated MongoDB Connection URI (Authentication fixed)
MONGO_URI = "mongodb+srv://itsrealvijay1_db_user:vijay@786482@cluster0.91gd3jb.mongodb.net/?appName=Cluster0"

# Initialize Pyrogram Bot
app = Client(
    "broadcast_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Initialize MongoDB Client
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client["cluster0"]
users_collection = db["users"]

@app.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Check if user already exists in database
    existing_user = await users_collection.find_one({"user_id": user_id})
    if not existing_user:
        await users_collection.insert_one({"user_id": user_id, "name": user_name})
    
    await message.reply_text(f"Hello {user_name}! Aapka swagat hai. Database successfully connected hai!")

@app.on_message(filters.command("broadcast") & filters.user(2062534062)) # Apni Admin ID yahan daal lena agar alag ho
async def broadcast_handler(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Kripya us message ko reply karein jise broadcast karna hai!")
        return
        
    broadcast_msg = message.reply_to_message
    users = users_collection.find({})
    success = 0
    failed = 0
    
    status_msg = await message.reply_text("Broadcast shuru ho gaya hai...")
    
    async for user in users:
        try:
            await broadcast_msg.copy(chat_id=user["user_id"])
            success += 1
            await asyncio.sleep(0.3) # Floodwait se bachne ke liye
        except Exception:
            failed += 1
            
    await status_msg.edit_text(f"Broadcast poora ho gaya!\n\nSuccess: {success}\nFailed: {failed}")

# Run the bot
if __name__ == "__main__":
    print("Bot start ho raha hai...")
    app.run()
