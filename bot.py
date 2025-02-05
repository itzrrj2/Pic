import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Replace with your Telegram bot token
TELEGRAM_BOT_TOKEN = "7734597847:AAG1Gmx_dEWgM5TR3xgljzr-_NpJnL4Jagc"

# API Endpoints
UPLOAD_API_URL = "https://ar-api-08uk.onrender.com/arhost?url="
ENHANCE_API_URL = "https://ar-api-08uk.onrender.com/remini"

async def start(update: Update, context: CallbackContext):
    """Start command handler"""
    await update.message.reply_text("Send me an image, and I'll enhance its quality for you!")

async def handle_photo(update: Update, context: CallbackContext):
    """Handles image upload and enhancement process"""
    photo = update.message.photo[-1]  # Get highest quality image
    file = await context.bot.get_file(photo.file_id)  # Get file from Telegram servers
    telegram_image_url = file.file_path  # Get direct URL of the uploaded image on Telegram

    await update.message.reply_text("Uploading image to processing server...")

    # Step 1: Upload the Telegram image URL to Image Hosting API
    upload_response = requests.get(UPLOAD_API_URL + telegram_image_url)

    if upload_response.status_code == 200:
        upload_data = upload_response.json()

        # Extract the uploaded image URL from the response
        if "fileurl" in upload_data:
            hosted_image_url = upload_data["fileurl"]  # Extracted URL without quotes
            await update.message.reply_text("Image uploaded successfully. Processing enhancement...")

            # Step 2: Send the hosted image URL to the Enhancement API
            enhance_response = requests.post(
                ENHANCE_API_URL,
                headers={"Content-Type": "application/json"},
                json={"url": hosted_image_url}  # Send the URL as a raw string without quotes
            )

            print("Enhancement API Response:", enhance_response.status_code, enhance_response.text)  # Debugging line

            if enhance_response.status_code == 200:
                enhance_data = enhance_response.json()

                # Extract the enhanced image URL from the response
                if "result" in enhance_data:
                    enhanced_image_url = enhance_data["result"]

                    # Step 3: Send the final enhanced image link to the user
                    await update.message.reply_text(f"Here is your enhanced image:\n{enhanced_image_url}")
                else:
                    await update.message.reply_text(f"Error: Enhancement API did not return a valid image link. Response: {enhance_data}")
            else:
                await update.message.reply_text(f"Error: Failed to process image enhancement. Status: {enhance_response.status_code}, Response: {enhance_response.text}")
        else:
            await update.message.reply_text("Error: Image Uploading API did not return a valid file URL.")
    else:
        await update.message.reply_text(f"Error: Failed to upload the image. Status: {upload_response.status_code}")

def main():
    """Main function to start the bot"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    application.run_polling()

if __name__ == "__main__":
    main()
