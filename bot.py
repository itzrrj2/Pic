import os
import logging
import random
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# MongoDB Configuration
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = "teraxbot"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["users"]
broadcasts_collection = db["broadcasts"]

# Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []
REQUIRED_CHANNELS = os.getenv('REQUIRED_CHANNELS', '').split(',')
UPLOAD_API = os.getenv('UPLOAD_API')
ENHANCE_API = os.getenv('ENHANCE_API')

# Customizable messages
WELCOME_MESSAGE = """
✨ *Welcome to Image Enhancer Pro Bot* ✨

Send me any photo or document image and I'll:
• Enhance the quality automatically
• Remove noise and artifacts
• Improve sharpness and clarity
"""

PROCESSING_MESSAGES = [
    "🔍 Analyzing your image...",
    "✨ Working some magic...",
    "🛠 Enhancing details...",
    "🎨 Adjusting colors...",
    "⚡ Final touches..."
]

async def store_user_data(user_data: dict):
    """Store or update user data in MongoDB."""
    try:
        users_collection.update_one(
            {"user_id": user_data["user_id"]},
            {"$set": user_data},
            upsert=True
        )
    except PyMongoError as e:
        logger.error(f"Error storing user data: {e}")

async def get_all_users():
    """Retrieve all users from database."""
    try:
        return list(users_collection.find({}, {"user_id": 1, "first_name": 1}))
    except PyMongoError as e:
        logger.error(f"Error fetching users: {e}")
        return []

async def store_broadcast(message: str, admin_id: int):
    """Store broadcast message in database."""
    try:
        broadcast_data = {
            "message": message,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow(),
            "status": "sent"
        }
        broadcasts_collection.insert_one(broadcast_data)
        return True
    except PyMongoError as e:
        logger.error(f"Error storing broadcast: {e}")
        return False

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

async def get_file_url_from_update(update: Update, context: CallbackContext):
    """Extract file URL from either photo or document."""
    try:
        if update.message.photo:
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            return file.file_path
        elif update.message.document and 'image' in update.message.document.mime_type:
            doc = update.message.document
            file = await context.bot.get_file(doc.file_id)
            return file.file_path
        return None
    except Exception as e:
        logger.error(f"Error getting file URL: {e}")
        return None

async def enhance_image_process(file_url: str):
    """Complete image enhancement workflow."""
    try:
        # Step 1: Upload to hosting service
        upload_url = UPLOAD_API.format(URL1=file_url)
        upload_response = requests.get(upload_url, timeout=30)
        upload_response.raise_for_status()
        upload_data = upload_response.json()
        
        if "data" not in upload_data:
            raise ValueError("Invalid response from hosting API")
            
        hosted_url = upload_data["data"]
        
        # Step 2: Enhance image
        enhance_url = ENHANCE_API.format(URL2=hosted_url)
        enhance_response = requests.get(enhance_url, timeout=60)
        enhance_response.raise_for_status()
        enhance_data = enhance_response.json()
        
        if "result" not in enhance_data or "resultImageUrl" not in enhance_data["result"]:
            raise ValueError("Invalid response from enhance API")
            
        return enhance_data["result"]["resultImageUrl"]
        
    except Exception as e:
        logger.error(f"Image enhancement error: {e}")
        raise

async def start(update: Update, context: CallbackContext):
    """Handle /start command with user registration."""
    try:
        if not update.message:
            return
            
        user = update.message.from_user
        user_data = {
            "user_id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "join_date": datetime.utcnow(),
            "last_active": datetime.utcnow(),
            "enhancement_count": 0
        }
        
        await store_user_data(user_data)
        
        if not await check_membership(user.id, context.bot):
            await prompt_to_join(update, context)
            return
            
        await update.message.reply_text(WELCOME_MESSAGE, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Start command error: {e}")
        await error_handler(update, context)

async def handle_image(update: Update, context: CallbackContext):
    """Handle image processing with enhancement."""
    try:
        user = update.message.from_user
        
        # Check membership
        if not await check_membership(user.id, context.bot):
            await prompt_to_join(update, context)
            return
            
        # Get file URL
        file_url = await get_file_url_from_update(update, context)
        if not file_url:
            await update.message.reply_text("⚠️ Please send a valid image file")
            return
            
        # Update user stats
        users_collection.update_one(
            {"user_id": user.id},
            {"$inc": {"enhancement_count": 1}, "$set": {"last_active": datetime.utcnow()}},
            upsert=True
        )
        
        # Show processing message
        processing_msg = await update.message.reply_text(random.choice(PROCESSING_MESSAGES))
        
        # Enhance image
        enhanced_url = await enhance_image_process(file_url)
        
        # Send result
        await processing_msg.delete()
        await update.message.reply_photo(
            photo=enhanced_url,
            caption="✅ *Enhancement Complete!*\nYour image has been successfully enhanced",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Enhance Another", callback_data="enhance_another")],
                [InlineKeyboardButton("⭐ Rate Us", url="https://t.me/sr_robots")]
            ])
        )
        
    except Exception as e:
        logger.error(f"Image handling error: {e}")
        await update.message.reply_text(
            "❌ *Enhancement Failed*\nPlease try again with a different image",
            parse_mode="Markdown"
        )

async def broadcast(update: Update, context: CallbackContext):
    """Admin broadcast command with confirmation."""
    try:
        if update.message.from_user.id not in ADMIN_IDS:
            await update.message.reply_text("🚫 Admin access required")
            return
            
        if not context.args:
            await update.message.reply_text("Usage: /broadcast Your message here")
            return
            
        message = ' '.join(context.args)
        total_users = users_collection.count_documents({})
        
        keyboard = [
            [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_broadcast:{message}")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast")]
        ]
        
        await update.message.reply_text(
            f"📢 Broadcast to {total_users} users:\n\n{message}\n\nConfirm?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Broadcast command error: {e}")
        await error_handler(update, context)

async def confirm_broadcast(update: Update, context: CallbackContext):
    """Handle broadcast confirmation."""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id not in ADMIN_IDS:
        await query.edit_message_text("🚫 Unauthorized")
        return
        
    if query.data.startswith("confirm_broadcast:"):
        message = query.data.split(":", 1)[1]
        admin_id = query.from_user.id
        
        if await store_broadcast(message, admin_id):
            users = await get_all_users()
            success = 0
            failed = 0
            
            await query.edit_message_text("📤 Sending broadcast...")
            
            for user in users:
                try:
                    await context.bot.send_message(
                        chat_id=user["user_id"],
                        text=f"📢 Announcement:\n\n{message}"
                    )
                    success += 1
                except Exception:
                    failed += 1
                    continue
                    
            await query.edit_message_text(
                f"✅ Broadcast sent!\nSuccess: {success}\nFailed: {failed}"
            )

async def prompt_to_join(update: Update, context: CallbackContext):
    """Prompt user to join required channels."""
    buttons = [
        [InlineKeyboardButton(f"Join {channel}", url=f"https://t.me/{channel}")]
        for channel in REQUIRED_CHANNELS
    ]
    buttons.append([InlineKeyboardButton("✅ Verify Join", callback_data="verify_join")])
    
    await update.message.reply_text(
        "📢 Please join our channels to use this bot:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def error_handler(update: object, context: CallbackContext):
    """Handle errors gracefully."""
    logger.error(msg="Exception while handling update:", exc_info=context.error)
    
    if isinstance(update, Update):
        if update.message:
            await update.message.reply_text("⚠️ An error occurred. Please try again.")
        elif update.callback_query:
            await update.callback_query.message.reply_text("⚠️ An error occurred.")

def main():
    """Start the bot with all handlers."""
    try:
        # Verify MongoDB connection
        client.admin.command('ping')
        logger.info("Connected to MongoDB")
        
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("broadcast", broadcast))
        
        # Message handlers
        application.add_handler(MessageHandler(filters.PHOTO, handle_image))
        application.add_handler(MessageHandler(filters.Document.IMAGE, handle_image))
        
        # Callback handlers
        application.add_handler(CallbackQueryHandler(confirm_broadcast, pattern="^(confirm|cancel)_broadcast"))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        logger.info("Bot is running...")
        application.run_polling()
        
    except PyMongoError as e:
        logger.error(f"MongoDB connection failed: {e}")
    except Exception as e:
        logger.error(f"Bot startup failed: {e}")

if __name__ == "__main__":
    main()
