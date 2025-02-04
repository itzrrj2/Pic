import telebot
import torch
from PIL import Image
from io import BytesIO
import requests
from realesrgan import RealESRGAN

# Replace with your Telegram bot token
BOT_TOKEN = "YOUR_BOT_TOKEN"
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize RealESRGAN model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = RealESRGAN(device, scale=4)
model.load_weights("Real-ESRGAN/weights/RealESRGAN_x4.pth")  # Path to your model weights

# Function to enhance the image using RealESRGAN
def enhance_image_with_realesrgan(image):
    # Convert the image to a format compatible with RealESRGAN
    image = image.convert("RGB")
    
    # Upscale the image with RealESRGAN
    enhanced_image = model.predict(image)
    return enhanced_image

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send me an image, and I'll enhance it using RealESRGAN!")

@bot.message_handler(content_types=['photo'])
def process_image(message):
    # Get the highest resolution image
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

    # Download the image
    response = requests.get(file_url)
    image = Image.open(BytesIO(response.content))

    # Enhance the image using RealESRGAN
    enhanced_image = enhance_image_with_realesrgan(image)

    # Save the enhanced image to a BytesIO object
    img_bytes = BytesIO()
    enhanced_image.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    # Send the enhanced image back to the user
    bot.send_photo(message.chat.id, img_bytes, caption="Here is your enhanced image!")

# Start the bot
bot.polling()
