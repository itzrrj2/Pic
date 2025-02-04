import telebot
import os
import subprocess
from PIL import Image
from io import BytesIO
import requests

# Your Bot Token from BotFather
BOT_TOKEN = '7734597847:AAG1Gmx_dEWgM5TR3xgljzr-_NpJnL4Jagc'

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

# Function to save image from URL
def save_image_from_url(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.save("input.jpg")
    return "input.jpg"

# Function to run GFPGAN model on the image
def enhance_image():
    try:
        # Run GFPGAN model via Docker command
        subprocess.run(["docker", "run", "--rm", "-v", os.getcwd() + ":/GFPGAN", "gfpgan", "python", "inference_gfpgan.py", "--input", "/GFPGAN/input.jpg", "--output", "/GFPGAN/output.jpg", "--model_path", "/GFPGAN/experiments/pretrained_models/gfpgan.pth"])

        # Return the path to the enhanced image
        return "output.jpg"
    except Exception as e:
        print(f"Error running GFPGAN: {e}")
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Respond to the /start command with a welcome message."""
    bot.reply_to(message, "Hello! Send me a photo, and I'll enhance it using GFPGAN!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """Handle received photo and send back enhanced version."""
    try:
        # Get the photo file
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}'

        # Download and save the image
        image_path = save_image_from_url(file_url)

        # Enhance the image using GFPGAN
        enhanced_image_path = enhance_image()

        if enhanced_image_path:
            # Send the enhanced image back to the user
            with open(enhanced_image_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
        else:
            bot.reply_to(message, "Sorry, there was an error processing your image. Please try again.")
    
    except Exception as e:
        bot.reply_to(message, "Sorry, there was an error processing your image. Please try again.")
        print(f"Error: {e}")

# Polling the bot to keep it running
bot.polling(none_stop=True)
