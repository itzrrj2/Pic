import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

# Replace with your Telegram bot token
TELEGRAM_BOT_TOKEN = "7079552870:AAHr1vrLw_g3Hc_EcUeECDTS3baXESC2mJo"

# Replace with your channel usernames (without '@')
REQUIRED_CHANNEL_1 = "Xstream_links2"
REQUIRED_CHANNEL_2 = "SR_robots"

# API Endpoints
UPLOAD_API_URL = "https://ar-api-08uk.onrender.com/arhost?url="
ENHANCE_API_URL = "https://reminisrbot.shresthstakeyt.workers.dev/?url={URL}&tool=enhance"

async def check_membership(user_id: int, bot) -> bool:
    try:
        chat_member_1 = await bot.get_chat_member(f"@{REQUIRED_CHANNEL_1}", user_id)
        chat_member_2 = await bot.get_chat_member(f"@{REQUIRED_CHANNEL_2}", user_id)
        allowed_statuses = ["member", "administrator", "creator"]
        return chat_member_1.status in allowed_statuses and chat_member_2.status in allowed_statuses
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    bot = context.bot

    if not await check_membership(user_id, bot):
        keyboard = [
            [InlineKeyboardButton("Join Channel 1", url=f"https://t.me/{REQUIRED_CHANNEL_1}")],
            [InlineKeyboardButton("Join Channel 2", url=f"https://t.me/{REQUIRED_CHANNEL_2}")],
            [InlineKeyboardButton("Join Channel 3", url=f"https://t.me/+LZ5rFtholpI5ZDY1")],
            [InlineKeyboardButton("✅ I Have Joined ✅", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("⚠️ You must join both channels to use this bot!", reply_markup=reply_markup)
        return

    await update.message.reply_text("Hello, Welcome To Remini Bot,\nWe Will Enhance The Image Quality And Send It Back To You.")

async def check_join(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    bot = context.bot

    if await check_membership(user_id, bot):
        await query.message.edit_text("✅ You have successfully joined! Now send me an image to enhance.")
    else:
        await query.answer("❌ You haven't joined both channels yet!", show_alert=True)

async def handle_photo(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    bot = context.bot

    if not await check_membership(user_id, bot):
        keyboard = [
            [InlineKeyboardButton("Join Channel 1", url=f"https://t.me/{REQUIRED_CHANNEL_1}")],
            [InlineKeyboardButton("Join Channel 2", url=f"https://t.me/{REQUIRED_CHANNEL_2}")],
            [InlineKeyboardButton("Join Channel 3", url=f"https://t.me/+LZ5rFtholpI5ZDY1")],
            [InlineKeyboardButton("✅ I Have Joined ✅", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("⚠️ You must join both channels to use this bot!", reply_markup=reply_markup)
        return

    photo = update.message.photo[-1]
    file = await bot.get_file(photo.file_id)
    telegram_image_url = file.file_path

    await update.message.reply_text("Uploading image to processing server...")

    upload_response = requests.get(UPLOAD_API_URL + telegram_image_url)

    if upload_response.status_code == 200:
        upload_data = upload_response.json()
        if "fileurl" in upload_data:
            hosted_image_url = upload_data["fileurl"]
            await update.message.reply_text("Image uploaded successfully. Processing enhancement...")

            # ✅ FIXED: Proper formatting of enhancement URL
            enhance_response = requests.get(ENHANCE_API_URL.format(URL=hosted_image_url))

            if enhance_response.status_code == 200:
                enhance_data = enhance_response.json()
                if "result" in enhance_data:
                    enhanced_image_url = enhance_data["result"]
                    await update.message.reply_text(f"Here is your enhanced image:\n{enhanced_image_url}")
                else:
                    await update.message.reply_text("Please Resend Your Image (IF STILL NOT WORKING THEN CONTACT - @SR_adminxbot)")
            else:
                await update.message.reply_text("Please Resend Your Image (IF STILL NOT WORKING THEN CONTACT - @SR_adminxbot)")
        else:
            await update.message.reply_text("Please Resend Your Image (IF STILL NOT WORKING THEN CONTACT - @SR_adminxbot)")
    else:
        await update.message.reply_text("Please Resend Your Image (IF STILL NOT WORKING THEN CONTACT - @SR_adminxbot)")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(check_join, pattern="check_membership"))

    application.run_polling()

if __name__ == "__main__":
    main()
