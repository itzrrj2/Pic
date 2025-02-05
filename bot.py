import os
import requests
from telegram import Update, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Bot Token (Same as provided)
TELEGRAM_BOT_TOKEN = "7079552870:AAES8Gsl1aVirYysaoBvLf7BHpsXI5n8_rc"

# Required Channels (Change links if needed)
REQUIRED_CHANNELS = {
    "@Xstream_links2": "https://t.me/Xstream_links2",
    "@Sr_robots": "https://t.me/Sr_robots",
}

# API Endpoints
UPLOAD_API_URL = "https://ar-api-08uk.onrender.com/arhost?url="
ENHANCE_API_URL = "https://ar-api-08uk.onrender.com/remini?url="

ERROR_MESSAGE = "⚠️ Please resend the picture. If it still doesn't work, contact: @Sr_adminxbot"

async def is_user_member(update: Update, context: CallbackContext) -> bool:
    """Checks if the user is a member of all required channels."""
    user_id = update.message.from_user.id
    bot = context.bot

    for channel, link in REQUIRED_CHANNELS.items():
        try:
            chat_member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if chat_member.status in [ChatMember.LEFT, ChatMember.KICKED]:
                return False
        except Exception:
            return False  # If bot fails to check, assume user is not a member

    return True

async def send_join_message(update: Update):
    """Sends the force join message with button."""
    join_buttons = [[InlineKeyboardButton("✅ Join Now", url=link)] for channel, link in REQUIRED_CHANNELS.items()]
    reply_markup = InlineKeyboardMarkup(join_buttons)

    await update.message.reply_text(
        "🚨 **You must join the channels below to use this bot.**\n\n"
        "📢 **Channels:**\n" + "\n".join([f"- [{channel}]({link})" for channel, link in REQUIRED_CHANNELS.items()]) +
        "\n\nAfter joining, send **/start** again.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def start(update: Update, context: CallbackContext):
    """Start command handler"""
    if not await is_user_member(update, context):
        await send_join_message(update)
        return

    await update.message.reply_text("🎉 **Welcome to Remini Bot!**\nSend me an image, and I will enhance it for you.")

async def handle_photo(update: Update, context: CallbackContext):
    """Handles image upload and enhancement process"""
    if not await is_user_member(update, context):
        await send_join_message(update)
        return

    try:
        photo = update.message.photo[-1]  # Get highest quality image
        file = await context.bot.get_file(photo.file_id)  # Get file from Telegram servers
        telegram_image_url = file.file_path  # Get direct URL of the uploaded image on Telegram

        await update.message.reply_text("📤 Uploading image to processing server...")

        # Step 1: Upload the Telegram image URL to Image Hosting API
        upload_response = requests.get(UPLOAD_API_URL + telegram_image_url)

        if upload_response.status_code == 200:
            upload_data = upload_response.json()

            # Extract the uploaded image URL from the response
            if "fileurl" in upload_data:
                hosted_image_url = upload_data["fileurl"]
                await update.message.reply_text("🔄 Image uploaded successfully. Enhancing...")

                # Step 2: Send the hosted image URL to the Enhancement API
                enhance_response = requests.get(f"{ENHANCE_API_URL}{hosted_image_url}")

                if enhance_response.status_code == 200:
                    enhance_data = enhance_response.json()

                    # Extract the enhanced image URL from the response
                    if "result" in enhance_data:
                        enhanced_image_url = enhance_data["result"]

                        # Step 3: Send the final enhanced image link to the user
                        await update.message.reply_text(
                            f"✨ **Here is your enhanced image:**\n[Click to View]({enhanced_image_url})",
                            parse_mode="Markdown"
                        )
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
