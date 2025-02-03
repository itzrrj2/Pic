import os
import httpx
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Replace with your Telegram bot token
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# API URLs
IMAGE_UPLOAD_API = "https://tmpfiles.org/api/v1/upload"
ENHANCE_API = "https://ar-api-08uk.onrender.com/remini?url="

async def upload_to_tmpfiles(file_path: str) -> str:
    """Uploads the image to tmpfiles.org and returns the public link."""
    try:
        with open(file_path, "rb") as file:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(IMAGE_UPLOAD_API, files={"file": file})

                if response.status_code == 200 and response.json().get("data"):
                    return response.json()["data"]["url"]  # Extracts public URL

    except Exception as e:
        print(f"Upload Error: {e}")
    return None

async def enhance_photo_and_send_link(file_path: str, chat_id: int):
    """Uploads the image, enhances it using the API, and sends the result."""
    try:
        # Step 1: Upload the image to tmpfiles.org
        uploaded_url = await upload_to_tmpfiles(file_path)
        if not uploaded_url:
            await bot.send_message(chat_id, "<b>Failed to upload image. Please try again.</b>", parse_mode="html")
            return

        # Step 2: Send the uploaded URL to the enhancement API
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(ENHANCE_API + uploaded_url)
            if response.status_code == 200 and response.json().get("image_url"):
                enhanced_image_url = response.json()["image_url"]
                await bot.send_message(chat_id, f"<b>Enhanced photo: </b> {enhanced_image_url}", parse_mode="html")
            else:
                await bot.send_message(chat_id, "<b>Failed to enhance the image.</b>", parse_mode="html")

    except Exception as e:
        await bot.send_message(chat_id, f"<b>Error:</b> {str(e)}", parse_mode="html")

    finally:
        # Remove the file to free up space
        if os.path.exists(file_path):
            os.remove(file_path)

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    dev_button = InlineKeyboardButton("Dev 👨‍💻", url="https://t.me/TheSmartBisnu")
    update_button = InlineKeyboardButton("Update ✅", url="https://t.me/PremiumNetworkTeam")
    keyboard.add(dev_button, update_button)

    await bot.send_message(
        message.chat.id,
        "<b>Welcome! I am a Smart Enhancer BOT. Please send me a photo to enhance.</b>",
        parse_mode="html",
        reply_markup=keyboard
    )

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_path = os.path.join(os.getcwd(), f"{photo.file_unique_id}.jpg")

    await bot.download_file(file_info.file_path, file_path)
    await bot.send_message(message.chat.id, "<b>Enhancing your photo...</b>", parse_mode="html")

    await enhance_photo_and_send_link(file_path, message.chat.id)

@dp.message_handler()
async def handle_invalid_message(message: types.Message):
    await bot.send_message(message.chat.id, "<b>Please send only photos.</b>", parse_mode="html")

if __name__ == "__main__":
    asyncio.run(dp.start_polling())
