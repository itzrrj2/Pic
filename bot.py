import os
import httpx
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load bot token from environment variables (for security)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# API URLs
IMAGE_UPLOAD_API = "https://tmpfiles.org/api/v1/upload"
ENHANCE_API = "https://ar-api-08uk.onrender.com/remini?url="

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

async def upload_to_tmpfiles(file_path: str) -> str:
    """Uploads an image to tmpfiles.org and returns the public link."""
    try:
        with open(file_path, "rb") as file:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(IMAGE_UPLOAD_API, files={"file": file})

                if response.status_code == 200 and response.json().get("data"):
                    return response.json()["data"]["url"]  # Extract public URL
    except Exception as e:
        print(f"Upload Error: {e}")
    return None

async def enhance_photo_and_send_link(file_path: str, chat_id: int):
    """Uploads the image, enhances it using the API, and sends the result."""
    try:
        uploaded_url = await upload_to_tmpfiles(file_path)
        if not uploaded_url:
            await bot.send_message(chat_id, "<b>Failed to upload image. Please try again.</b>")
            return

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(ENHANCE_API + uploaded_url)
            if response.status_code == 200 and response.json().get("image_url"):
                enhanced_image_url = response.json()["image_url"]
                await bot.send_message(chat_id, f"<b>Enhanced photo: </b> {enhanced_image_url}")
            else:
                await bot.send_message(chat_id, "<b>Failed to enhance the image.</b>")
    except Exception as e:
        await bot.send_message(chat_id, f"<b>Error:</b> {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@dp.message(Command("start"))
async def start_command(message: Message):
    """Handles the /start command."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Dev 👨‍💻", url="https://t.me/TheSmartBisnu")],
        [InlineKeyboardButton(text="Update ✅", url="https://t.me/PremiumNetworkTeam")]
    ])

    await message.answer(
        "<b>Welcome! I am a Smart Enhancer BOT. Please send a photo to enhance.</b>",
        reply_markup=keyboard
    )

@dp.message()
async def handle_photo(message: Message):
    """Handles user messages and processes photos."""
    if message.photo:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        file_path = os.path.join(os.getcwd(), f"{photo.file_unique_id}.jpg")

        await bot.download_file(file_info.file_path, file_path)
        await bot.send_message(message.chat.id, "<b>Enhancing your photo...</b>")

        await enhance_photo_and_send_link(file_path, message.chat.id)
    else:
        await bot.send_message(message.chat.id, "<b>Please send only photos.</b>")

async def main():
    """Main function to start the bot."""
    dp.include_router(start_command)  # Register handlers
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
