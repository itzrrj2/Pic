import telebot
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from io import BytesIO
import requests

# Replace with your Telegram bot token
BOT_TOKEN = "7734597847:AAG1Gmx_dEWgM5TR3xgljzr-_NpJnL4Jagc"
bot = telebot.TeleBot(BOT_TOKEN)

# Function to enhance the image
def enhance_image(image):
    # Convert the image to a numpy array (keep it in color)
    image_array = np.array(image)

    # Sharpen the image
    kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])  # A better sharpening kernel
    sharpened_image = cv2.filter2D(image_array, -1, kernel)

    # Convert sharpened image back to PIL Image for further enhancement
    pil_image = Image.fromarray(sharpened_image)

    # Enhance the contrast of the image
    enhancer = ImageEnhance.Contrast(pil_image)
    enhanced_image = enhancer.enhance(1.5)  # You can adjust the factor as needed (1.0 is no change)

    # Optionally, enhance brightness
    enhancer_brightness = ImageEnhance.Brightness(enhanced_image)
    enhanced_image = enhancer_brightness.enhance(1.2)  # Adjust brightness if needed

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
    response = requests.get(file_url)
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
