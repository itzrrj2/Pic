import telebot
import torch
from PIL import Image
from io import BytesIO
import requests
from srgan import SRGAN  # Assuming SRGAN is installed via requirements.txt

# Replace with your Telegram bot token
BOT_TOKEN = "7734597847:AAG1Gmx_dEWgM5TR3xgljzr-_NpJnL4Jagc"
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize SRGAN model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SRGAN(device)
model.load_weights("SRGAN/weights/srgan_model.h5")  # Path to SRGAN model weights

# Function to enhance the image using SRGAN
def enhance_image_with_srgan(image):
    # Convert the image to a format compatible with SRGAN
    image = image.convert("RGB")
    
    # Enhance the image with SRGAN
    enhanced_image = model.predict(image)
    return enhanced_image

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send me an image, and I'll enhance it using SRGAN!")

@bot.message_handler(content_types=['photo'])
def process_image(message):
    # Get the highest resolution image
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

    # Download the image
    response = requests.get(file_url)
    image = Image.open(BytesIO(response.content))

    # Enhance the image using SRGAN
    enhanced_image = enhance_image_with_srgan(image)

    # Save the enhanced image to a BytesIO object
    img_bytes = BytesIO()
    enhanced_image.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    # Send the enhanced image back to the user
    bot.send_photo(message.chat.id, img_bytes, caption="Here is your enhanced image!")

# Start the bot
bot.polling()
