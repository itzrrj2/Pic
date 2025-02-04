import telebot
import torch
from PIL import Image
from io import BytesIO
import requests
import waifu2x

# Replace with your Telegram bot token
BOT_TOKEN = "7734597847:AAG1Gmx_dEWgM5TR3xgljzr-_NpJnL4Jagc"
bot = telebot.TeleBot(BOT_TOKEN)

# Function to enhance the image using Waifu2x
def enhance_image_with_waifu2x(image):
    # Convert the image to a format compatible with Waifu2x
    image = image.convert("RGB")
    
    # Enhance the image using Waifu2x
    enhanced_image = waifu2x.convert(image)
    return enhanced_image

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send me an image, and I'll enhance it using Waifu2x!")

@bot.message_handler(content_types=['photo'])
def process_image(message):
    # Get the highest resolution image
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

    # Download the image
    response = requests.get(file_url)
    image = Image.open(BytesIO(response.content))

    # Enhance the image using Waifu2x
    enhanced_image = enhance_image_with_waifu2x(image)

    # Save the enhanced image to a BytesIO object
    img_bytes = BytesIO()
    enhanced_image.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    # Send the enhanced image back to the user
    bot.send_photo(message.chat.id, img_bytes, caption="Here is your enhanced image!")

# Start the bot
bot.polling()
