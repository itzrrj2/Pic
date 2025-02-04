import telebot
import cv2
import numpy as np
import requests
from io import BytesIO
from realesrgan import RealESRGAN

# Replace with your Telegram bot token
BOT_TOKEN = "7734597847:AAG1Gmx_dEWgM5TR3xgljzr-_NpJnL4Jagc"

bot = telebot.TeleBot(BOT_TOKEN)

# Load the Real-ESRGAN model
model_path = "RealESRGAN_x4.pth"  # Make sure you have this model file
model = RealESRGAN(device="cpu")
model.load_weights(model_path)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send me an image, and I'll enhance it!")

@bot.message_handler(content_types=['photo'])
def enhance_image(message):
    # Get the highest resolution image
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

    # Download the image
    response = requests.get(file_url)
    image = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)

    # Enhance the image
    enhanced_image = model.enhance(image, outscale=4)

    # Convert back to bytes
    _, img_encoded = cv2.imencode('.jpg', enhanced_image)
    img_bytes = BytesIO(img_encoded.tobytes())

    # Send the enhanced image back
    bot.send_photo(message.chat.id, img_bytes, caption="Here is your enhanced image!")

# Start the bot
bot.polling()
