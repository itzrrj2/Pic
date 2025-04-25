import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7079552870:AAEHPQId2oaLw2c4dgZEUlJggctM5_fCwQw')
REQUIRED_CHANNELS = ["Xstream_links2", "SR_robots", "sr_robots_backup"]
UPLOAD_API = "https://hosting.ashlynn-repo.workers.dev/?url={URL1}"
ENHANCE_API = "https://reminisrbot.shresthstakeyt.workers.dev/?url={URL2}&tool=enhance"

async def error_handler(update: object, context: CallbackContext) -> None:
    """Log errors and send user-friendly messages."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    if isinstance(update, Update):
        if update.message:
            await update.message.reply_text("⚠️ An error occurred. Please try again or contact support.")
        elif update.callback_query:
            await update.callback_query.message.reply_text("⚠️ An error occurred. Please try again.")

async def check_membership(user_id: int, bot) -> bool:
    """Check if user is member of all required channels."""
    try:
        for channel in REQUIRED_CHANNELS:
            chat_member = await bot.get_chat_member(f"@{channel}", user_id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                return False
        return True
    except Exception as e:
        logger.error(f"Membership check failed: {e}")
        return False

async def start(update: Update, context: CallbackContext):
    """Handle /start command with channel verification."""
    try:
        if not update.message:
            return
            
        user_id = update.message.from_user.id
        
        if not await check_membership(user_id, context.bot):
            keyboard = [
                [InlineKeyboardButton(f"Join {channel}", url=f"https://t.me/{channel}")]
                for channel in REQUIRED_CHANNELS
            ]
            keyboard.append([InlineKeyboardButton("✅ Verify Join", callback_data="verify_join")])
            await update.message.reply_text(
                "📢 Please join our channels to use this bot:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
            
        await update.message.reply_text(
            "🌟 Welcome to Image Enhancer Bot!\n"
            "Send me an image and I'll enhance it for you."
        )
    except Exception as e:
        logger.error(f"Start command error: {e}")
        await error_handler(update, context)

async def verify_join(update: Update, context: CallbackContext):
    """Verify channel membership after user clicks button."""
    try:
        query = update.callback_query
        await query.answer()
        
        if await check_membership(query.from_user.id, context.bot):
            await query.message.edit_text("✅ Verified! Now send me an image to enhance.")
        else:
            await query.answer("❌ You haven't joined all channels yet!", show_alert=True)
    except Exception as e:
        logger.error(f"Verify join error: {e}")
        await error_handler(update, context)

async def handle_image(update: Update, context: CallbackContext):
    """Process the image enhancement workflow."""
    try:
        if not update.message or not update.message.photo:
            return
            
        user_id = update.message.from_user.id
        bot = context.bot
        
        # Check channel membership
        if not await check_membership(user_id, bot):
            await start(update, context)
            return
            
        # Get highest quality image
        photo = update.message.photo[-1]
        file = await bot.get_file(photo.file_id)
        telegram_url = file.file_path
        
        # Step 1: Upload to hosting service
        msg = await update.message.reply_text("⬆️ Uploading image to hosting service...")
        
        upload_url = UPLOAD_API.format(URL1=telegram_url)
        upload_response = requests.get(upload_url, timeout=30)
        upload_response.raise_for_status()
        upload_data = upload_response.json()
        
        if "data" not in upload_data:
            raise ValueError("Invalid response from hosting API")
            
        hosted_url = upload_data["data"]
        await msg.edit_text("🔍 Processing image enhancement...")
        
        # Step 2: Enhance image
        enhance_url = ENHANCE_API.format(URL2=hosted_url)
        enhance_response = requests.get(enhance_url, timeout=60)
        enhance_response.raise_for_status()
        enhance_data = enhance_response.json()
        
        if "result" not in enhance_data or "resultImageUrl" not in enhance_data["result"]:
            raise ValueError("Invalid response from enhance API")
            
        enhanced_url = enhance_data["result"]["resultImageUrl"]
        
        # Step 3: Send enhanced image
        await msg.delete()
        await update.message.reply_photo(
            photo=enhanced_url,
            caption="✅ Here's your enhanced image!"
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        await update.message.reply_text("⚠️ Service unavailable. Please try again later.")
    except Exception as e:
        logger.error(f"Image processing error: {e}")
        await update.message.reply_text("❌ Failed to process image. Please try again or contact support.")

def main():
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(CallbackQueryHandler(verify_join, pattern="^verify_join$"))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
