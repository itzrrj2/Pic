import os
import logging
import asyncio
import aiohttp
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from pymongo import MongoClient
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv()

# Bot credentials
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
CHANNEL_1 = os.getenv("TELEGRAM_CHANNEL_1")
CHANNEL_2 = os.getenv("TELEGRAM_CHANNEL_2")
DEFAULT_DB_NAME = os.getenv("MONGO_DB_NAME", "telegram_bot")

# APIs for image processing
ENHANCE_V1_API = "https://ar-api-08uk.onrender.com/remini?url="
REMOVE_BG_API = "https://ar-api-08uk.onrender.com/remove?bg="

# Initialize bot and dispatcher
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client[DEFAULT_DB_NAME]
users_collection = db["users"]

# Logging setup
logging.basicConfig(level=logging.INFO)


# State machine for tracking user actions
class ImageProcessingState(StatesGroup):
    enhancing = State()
    removing_bg = State()


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
        [InlineKeyboardButton("✅ I've Joined", callback_data="check_join")]
    ])
    await bot.send_message(chat_id, "🚨 To use this bot, please join both channels first!", reply_markup=buttons)


@dp.callback_query_handler(lambda c: c.data == "check_join")
async def check_join_status(callback_query: types.CallbackQuery):
    """Check if user has joined channels after clicking the button"""
    user_id = callback_query.from_user.id
    await callback_query.answer()
    
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
    users_collection.update_one(
        {"user_id": user_id},
        {"$setOnInsert": {"user_id": user_id, "username": user_name}},
        upsert=True
    )

    # Send welcome message
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("BACKGROUND REMOVER", callback_data="remove_bg")],
        [InlineKeyboardButton("REMINI PRO FREE", callback_data="enhance_v1")]
    ])
    await message.reply(f"👋 Hey {user_name}, Welcome to the Image Enhancer Bot!\n\nChoose an option below:", reply_markup=buttons)


@dp.callback_query_handler(lambda c: c.data == "enhance_v1")
async def enhance_v1(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle Enhance Image Request"""
    await callback_query.answer()
    await state.set_state(ImageProcessingState.enhancing.state)
    await bot.send_message(callback_query.message.chat.id, "📸 Send me an image to enhance.")


@dp.callback_query_handler(lambda c: c.data == "remove_bg")
async def remove_bg(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle Background Removal Request"""
    await callback_query.answer()
    await state.set_state(ImageProcessingState.removing_bg.state)
    await bot.send_message(callback_query.message.chat.id, "📸 Send me an image to remove its background.")


async def get_file_url(file_id):
    """Retrieve Telegram file URL"""
    file = await bot.get_file(file_id)
    return f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"


async def fetch_image(url):
    """Download image from API response and determine file type"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if resp.status == 200 and "image" in content_type:
                file_extension = content_type.split("/")[-1]  # Extract file type (jpg, png, etc.)
                image_data = io.BytesIO(await resp.read())
                image_data.name = f"processed_image.{file_extension}"
                return image_data
            else:
                logging.error(f"API Error: {resp.status}, Content-Type: {content_type}, Response: {await resp.text()}")
                return None


def upload_to_tmpfiles(file_path):
    """Upload image to tmpfiles.org"""
    upload_url = 'https://tmpfiles.org/api/v1/upload'
    files = {'file': open(file_path, 'rb')}
    response = requests.post(upload_url, files=files)
    response_data = response.json()
    files.close()  # Close the file after uploading
    return response_data


@dp.message_handler(content_types=["photo"], state=ImageProcessingState.enhancing)
async def process_enhance_v1(message: types.Message, state: FSMContext):
    """Process image enhancement"""
    await state.finish()
    file_id = message.photo[-1].file_id
    file_url = await get_file_url(file_id)

    # Download image
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as resp:
            file_data = io.BytesIO(await resp.read())
            file_data.name = "temp_image.jpg"  # Temporary file name

            # Save to a local file
            with open(file_data.name, "wb") as f:
                f.write(file_data.getvalue())

    # Upload the image to tmpfiles
    tmpfiles_response = upload_to_tmpfiles(file_data.name)
    if tmpfiles_response.get('url'):
        enhanced_url = ENHANCE_V1_API + tmpfiles_response['url']
        image_data = await fetch_image(enhanced_url)
        if image_data:
            if image_data.name.endswith(".jpg"):
                await bot.send_photo(message.chat.id, image_data, caption="✅ Image enhanced successfully!")
            else:
                await bot.send_document(message.chat.id, types.InputFile(image_data), caption="✅ Image enhanced successfully!")
        else:
            await bot.send_message(message.chat.id, "❌ Enhancement failed. Try again later.")
    else:
        await bot.send_message(message.chat.id, "❌ Failed to upload image to tmpfiles.org. Try again later.")


@dp.message_handler(content_types=["photo"], state=ImageProcessingState.removing_bg)
async def process_remove_bg(message: types.Message, state: FSMContext):
    """Process background removal"""
    await state.finish()
    file_id = message.photo[-1].file_id
    file_url = await get_file_url(file_id)
    bg_removed_url = REMOVE_BG_API + file_url

    image_data = await fetch_image(bg_removed_url)
    if image_data:
        if image_data.name.endswith(".jpg"):
            await bot.send_photo(message.chat.id, image_data, caption="✅ Background removed successfully!")
        else:
            await bot.send_document(message.chat.id, types.InputFile(image_data), caption="✅ Background removed successfully!")
    else:
        await bot.send_message(message.chat.id, "❌ Failed to remove background. Try again later.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
