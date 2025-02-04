import telebot
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import requests
from io import BytesIO

# Your Bot Token from BotFather
BOT_TOKEN = '7734597847:AAG1Gmx_dEWgM5TR3xgljzr-_NpJnL4Jagc'

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

def enhance_image(image_path):
    """Enhance image quality using Pillow and OpenCV."""
    # Open the image with Pillow
    pil_image = Image.open(image_path)

    # Enhance sharpness using Pillow
    enhancer = ImageEnhance.Sharpness(pil_image)
    pil_image = enhancer.enhance(2.0)  # Increase sharpness (you can tweak this value)

    # Convert the enhanced image back to a format that OpenCV can use
    open_cv_image = np.array(pil_image)
    open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)

    # Use OpenCV to enhance contrast (optional step)
    lab = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2Lab)
    l, a, b = cv2.split(lab)
    l = cv2.equalizeHist(l)
    lab = cv2.merge([l, a, b])
    enhanced_image = cv2.cvtColor(lab, cv2.COLOR_Lab2BGR)

    return enhanced_image

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
