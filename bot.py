import os
import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot credentials
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_1 = os.getenv("TELEGRAM_CHANNEL_1")  # First channel
CHANNEL_2 = os.getenv("TELEGRAM_CHANNEL_2")  # Second channel

# Initialize bot and dispatcher
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client["telegram_bot"]
users_collection = db["users"]

# Image Processing APIs
ENHANCE_V1_API = "https://prompt.ashlynn.workers.dev/enhance?imgurl="
REMOVE_BG_API = "https://prompt.ashlynn.workers.dev/removebg?imgurl="

# Logging setup
logging.basicConfig(level=logging.INFO)


async def is_user_in_channel(user_id):
    """Check if user is subscribed to both channels"""
    try:
        chat_member1 = await bot.get_chat_member(CHANNEL_1, user_id)
        chat_member2 = await bot.get_chat_member(CHANNEL_2, user_id)

        return chat_member1.status in ["member", "administrator", "creator"] and \
               chat_member2.status in ["member", "administrator", "creator"]
    except:
        return False


async def force_join_channels(chat_id):
    """Force user to join channels before using the bot"""
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Join Channel 1 ✅", url=f"https://t.me/{CHANNEL_1[1:]}")],
        [InlineKeyboardButton("Join Channel 2 ✅", url=f"https://t.me/{CHANNEL_2[1:]}")],
        [InlineKeyboardButton("Join Channel 3 ✅", url=f"https://t.me/+FHydfS-U4H01YzBl")],
        [InlineKeyboardButton("✅ I've Joined", callback_data="check_join")]
    ])
    await bot.send_message(chat_id, "🚨 To use this bot, please join both channels first!", reply_markup=buttons)


@dp.callback_query_handler(lambda c: c.data == "check_join")
async def check_join_status(callback_query: types.CallbackQuery):
    """Check if user has joined channels after clicking the button"""
    user_id = callback_query.from_user.id
    if await is_user_in_channel(user_id):
        await bot.send_message(user_id, "✅ You have successfully joined the channels! Now you can use the bot.")
        await start_command(callback_query.message)
    else:
        await bot.send_message(user_id, "⚠️ You haven't joined both channels yet. Please join and try again.")


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    """Handle /start command and enforce force join"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    if not await is_user_in_channel(user_id):
        await force_join_channels(message.chat.id)
        return

    # Save user to MongoDB if not already added
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({"user_id": user_id, "username": user_name})

    # Send welcome message
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Remove BG", callback_data="remove_bg")],
        [InlineKeyboardButton("Enhance V1 ✅", callback_data="enhance_v1")],
        [InlineKeyboardButton("Enhance V2 (Coming Soon) 🚧", callback_data="enhance_v2")]
    ])
    await message.reply(f"👋 Hey {user_name}, Welcome to the Remini Image Enhancer Bot!\n\nChoose an option below:", reply_markup=buttons)


@dp.callback_query_handler(lambda c: c.data == "enhance_v1")
async def enhance_v1(callback_query: types.CallbackQuery):
    """Handle Enhance V1"""
    await bot.send_message(callback_query.message.chat.id, "📸 Send me an image to enhance.")

    @dp.message_handler(content_types=["photo"])
    async def process_enhance_v1(message: types.Message):
        file_id = message.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"

        # Call enhance API
        enhanced_url = ENHANCE_V1_API + file_url
        await bot.send_photo(message.chat.id, enhanced_url, caption="✅ Image enhanced successfully!")


@dp.callback_query_handler(lambda c: c.data == "enhance_v2")
async def enhance_v2(callback_query: types.CallbackQuery):
    """Notify user that Enhance V2 is under development"""
    await bot.send_message(callback_query.message.chat.id, "🚧 We are working on Enhance V2. Currently, only Enhance V1 is available.")


@dp.callback_query_handler(lambda c: c.data == "remove_bg")
async def remove_bg(callback_query: types.CallbackQuery):
    """Handle background removal"""
    await bot.send_message(callback_query.message.chat.id, "📸 Send me an image to remove its background.")

    @dp.message_handler(content_types=["photo"])
    async def process_remove_bg(message: types.Message):
        file_id = message.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"

        # Call Remove BG API
        bg_removed_url = REMOVE_BG_API + file_url
        await bot.send_photo(message.chat.id, bg_removed_url, caption="✅ Background removed successfully!")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
