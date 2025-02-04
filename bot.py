import telebot
from PIL import Image
import requests
import cv2
import numpy as np
from io import BytesIO

# Your Bot Token from BotFather
BOT_TOKEN = '7734597847:AAG1Gmx_dEWgM5TR3xgljzr-_NpJnL4Jagc'

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

def enhance_image(image_path):
    """Enhance image quality by upscaling using OpenCV without reducing quality."""
    # Read the image using OpenCV
    img = cv2.imread(image_path)

    # Increase the size of the image (upscale with a different interpolation method for better quality)
    width = int(img.shape[1] * 2)  # Double the width
    height = int(img.shape[0] * 2)  # Double the height
    dim = (width, height)

    # Use cv2.INTER_CUBIC for better interpolation (it gives smoother results)
    enhanced_img = cv2.resize(img, dim, interpolation=cv2.INTER_CUBIC)

    return enhanced_img

def save_image_from_url(url):
    """Download image from URL and save it to a local file."""
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.save("input_image.jpg")
    return "input_image.jpg"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Respond to the /start command with a welcome message."""
    bot.reply_to(message, "Hello! Send me a photo and I'll enhance its quality for you.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """Handle received photo and send back enhanced version."""
    # Get the photo file
    file_info = bot.get_file(message.photo[-1].file_id)
    file_url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}'

    # Download and save the image
    image_path = save_image_from_url(file_url)

    # Enhance the image
    enhanced_image = enhance_image(image_path)

    # Save the enhanced image to a file
    enhanced_image_path = "enhanced_image.jpg"
    cv2.imwrite(enhanced_image_path, enhanced_image)

    # Send the enhanced image back to the user
    with open(enhanced_image_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)

# Polling the bot to keep it running
bot.polling(none_stop=True)
