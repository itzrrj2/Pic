import os
import requests
from telegram import Update, ChatMember
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Replace with your Telegram bot token
TELEGRAM_BOT_TOKEN = "7079552870:AAEn1PNl4onkz2R_N8KRhmxZTTAuJ0qycmU"

# Required Channels
REQUIRED_CHANNELS = ["@Xstream_links2", "@Sr_robots"]  # Replace with your actual channel usernames

# API Endpoints
UPLOAD_API_URL = "https://ar-api-08uk.onrender.com/arhost?url="
ENHANCE_API_URL = "https://ar-api-08uk.onrender.com/remini?url="

ERROR_MESSAGE = "⚠️ Please resend the picture. If it still doesn't work, contact: @Sr_adminxbot"

async def is_user_member(update: Update, context: CallbackContext) -> bool:
    """Checks if the user is a member of all required channels."""
    user_id = update.message.from_user.id
    bot = context.bot

    for channel in REQUIRED_CHANNELS:
        try:
            chat_member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if chat_member.status in [ChatMember.LEFT, ChatMember.KICKED]:
                return False
        except Exception:
            return False  # If an error occurs (e.g., bot not an admin), assume user is not a member

    return True

async def start(update: Update, context: CallbackContext):
    """Start command handler"""
    if not await is_user_member(update, context):
        channels_list = "\n".join([f"- {channel}" for channel in REQUIRED_CHANNELS])
        await update.message.reply_text(
            f"🚨 To use this bot, please join the following channels:\n{channels_list}\n\nAfter joining, send /start again."
        )
        return

    await update.message.reply_text("WELCOME TO REMINI BOT,\nSend me an image, I Will Make It Better And Send It Back To You")

async def handle_photo(update: Update, context: CallbackContext):
    """Handles image upload and enhancement process"""
    if not await is_user_member(update, context):
        channels_list = "\n".join([f"- {channel}" for channel in REQUIRED_CHANNELS])
        await update.message.reply_text(
            f"🚨 To use this bot, please join the following channels:\n CHANNEL LINK- https://t.me/+LZ5rFtholpI5ZDY1\n{channels_list}\n\nAfter joining, send /start again."
        )
        return

    try:
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
                hosted_image_url = upload_data["fileurl"]
                await update.message.reply_text("Image uploaded successfully. Processing enhancement...")

                # Step 2: Send the hosted image URL to the Enhancement API
                enhance_response = requests.get(f"{ENHANCE_API_URL}{hosted_image_url}")

                if enhance_response.status_code == 200:
                    enhance_data = enhance_response.json()

                    # Extract the enhanced image URL from the response
                    if "result" in enhance_data:
                        enhanced_image_url = enhance_data["result"]

                        # Step 3: Send the final enhanced image link to the user
                        await update.message.reply_text(f"Here is your enhanced image (CLICK ON LINK AND SAVE THE PICTURE):\n{enhanced_image_url}")
                    else:
                        await update.message.reply_text(ERROR_MESSAGE)
                else:
                    await update.message.reply_text(ERROR_MESSAGE)
            else:
                await update.message.reply_text(ERROR_MESSAGE)
        else:
            await update.message.reply_text(ERROR_MESSAGE)
    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
        await update.message.reply_text(ERROR_MESSAGE)

def main():
    """Main function to start the bot"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    application.run_polling()

if __name__ == "__main__":
    main()
