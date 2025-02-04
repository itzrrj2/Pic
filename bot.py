import telebot
import requests
import cv2
import numpy as np
from io import BytesIO
from PIL import Image, ImageEnhance

# Initialize the bot
bot_token = '7734597847:AAG1Gmx_dEWgM5TR3xgljzr-_NpJnL4Jagc'
bot = telebot.TeleBot(bot_token)

# Option 1: Enhance the image using Pillow (Sharpness)
def enhance_image_pillow(img):
    # Convert to RGB if the image is in another mode (like RGBA)
    img = img.convert("RGB")

    # Enhance sharpness (improves details without changing colors)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)  # Increase sharpness by 2x (adjustable)

    return img

# Option 2: Enhance the image using OpenCV (Sharpening Filter)
def enhance_image_opencv(img):
    # Convert to numpy array
    img = np.array(img)

    # Define a sharpening kernel
    kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])

    # Apply filter using OpenCV to sharpen the image
    enhanced_img = cv2.filter2D(img, -1, kernel)

    return enhanced_img

@bot.message_handler(content_types=['photo'])
def process_image(message):
    # Get the image file
    file_info = bot.get_file(message.photo[-1].file_id)
    file_url = f'https://api.telegram.org/file/bot{bot_token}/{file_info.file_path}'
    
    # Download the image
    response = requests.get(file_url)
    img = Image.open(BytesIO(response.content))

    # Choose between Pillow or OpenCV enhancement
    # Uncomment the enhancement option you want to use:

    # Using Pillow for sharpness enhancement
    enhanced_img = enhance_image_pillow(img)

    # OR, using OpenCV for sharpening
    # enhanced_img = enhance_image_opencv(img)

    # Save the enhanced image
    output_image_path = "enhanced_image.png"
    enhanced_img.save(output_image_path)

    # Send the enhanced image back to the user
    with open(output_image_path, 'rb') as enhanced_image:
        bot.send_photo(message.chat.id, enhanced_image)

# Start polling
bot.polling()
