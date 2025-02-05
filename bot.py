import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Replace with your Telegram bot token
TELEGRAM_BOT_TOKEN = "7734597847:AAG1Gmx_dEWgM5TR3xgljzr-_NpJnL4Jagc"

# API Endpoints
UPLOAD_API_URL = "https://ar-api-08uk.onrender.com/arhost?url="
ENHANCE_API_URL = "https://ar-api-08uk.onrender.com/remini?url="

async def start(update: Update, context: CallbackContext):
    """Start command handler"""
    await update.message.reply_text("Send me an image, and I'll enhance its quality for you!")

async def handle_photo(update: Update, context: CallbackContext):
    """Handles image upload and enhancement process"""
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    # Create downloads directory if it doesn't exist
    os.makedirs("downloads", exist_ok=True)
    file_path = f"downloads/{photo.file_id}.jpg"

    # Download the photo
    await file.download_to_drive(file_path)

    with open(file_path, "rb") as img_file:
        files = {"file": img_file}
        response = requests.post(UPLOAD_API_URL, files=files)

    if response.status_code == 200:
        data = response.json()
        if "fileurl" in data:
            uploaded_url = data["fileurl"]
            enhance_response = requests.post(ENHANCE_API_URL, json={"url": uploaded_url})

            if enhance_response.status_code == 200:
                enhance_data = enhance_response.json()
                if "result" in enhance_data:
                    enhanced_image_url = enhance_data["result"]
                    await update.message.reply_text(f"Here is your enhanced image:\n{enhanced_image_url}")
                else:
                    await update.message.reply_text("Error: Failed to enhance the image.")
            else:
                await update.message.reply_text("Error: Failed to process the image enhancement.")
        else:
            await update.message.reply_text("Error: Failed to upload the image.")
    else:
        await update.message.reply_text("Error: Failed to upload the image to the API.")

    # Remove downloaded file after processing
    os.remove(file_path)

def main():
    """Main function to start the bot"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Start polling
    application.run_polling()

if __name__ == "__main__":
    main()
