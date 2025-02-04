import telebot
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from io import BytesIO
import requests  # Add this import

# Replace with your Telegram bot token
BOT_TOKEN = "YOUR_BOT_TOKEN"
bot = telebot.TeleBot(BOT_TOKEN)

# Function to enhance the image
def enhance_image(image):
    # Convert the image to a numpy array
    image_array = np.array(image)
    
    # Convert the image to grayscale (optional)
    gray_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    
    # Sharpen the image
    kernel = np.array([[-1, -1, -1], [-1, 9,-1], [-1, -1, -1]])  # Sharpening kernel
    sharpened_image = cv2.filter2D(gray_image, -1, kernel)

    # Convert back to RGB
    sharpened_image_rgb = cv2.cvtColor(sharpened_image, cv2.COLOR_GRAY2RGB)

    # Enhance the contrast
    pil_image = Image.fromarray(sharpened_image_rgb)
    enhancer = ImageEnhance.Contrast(pil_image)
    enhanced_image = enhancer.enhance(1.5)  # Adjust the factor to control contrast

    return enhanced_image

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send me an image, and I'll enhance it!")

@bot.message_handler(content_types=['photo'])
def process_image(message):
    # Get the highest resolution image
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

    # Download the image
    response = requests.get(file_url)  # Now 'requests' is correctly imported
    image = Image.open(BytesIO(response.content))

    # Enhance the image
    enhanced_image = enhance_image(image)

    # Save the enhanced image to a BytesIO object
    img_bytes = BytesIO()
    enhanced_image.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    # Send the enhanced image back to the user
    bot.send_photo(message.chat.id, img_bytes, caption="Here is your enhanced image!")

# Start the bot
bot.polling()
