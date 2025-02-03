import os
import requests
from telethon import TelegramClient, events
from telethon.tl.types import InputFile
from telethon.sessions import StringSession

# Set your API credentials and token
API_ID = '19593445'  # Obtain from https://my.telegram.org/auth
API_HASH = 'f78a8ae025c9131d3cc57d9ca0fbbc30'  # Obtain from https://my.telegram.org/auth
BOT_TOKEN = '7734597847:AAGmGMwx_TbWXWa35s3XEWkH0lenUahToO4'  # Obtain from @BotFather

UPLOAD_URL = 'https://tmpfiles.org/api/v1/upload'
ENHANCE_API_URL = 'https://ar-api-08uk.onrender.com/remini?url='

# Create the Telethon client
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Function to upload image to tmpfiles.org
def upload_to_tmpfiles(file_url):
    # Download the file from Telegram
    response = requests.get(file_url)
    
    if response.status_code == 200:
        # Send the image data to tmpfiles.org
        files = {'file': ('image.jpg', response.content, 'image/jpeg')}
        upload_response = requests.post(UPLOAD_URL, files=files)
        
        if upload_response.status_code == 200:
            # Extract the URL from the response
            data = upload_response.json()
            return data.get("data", {}).get("url")
    return None

# Function to enhance image using the enhancement API
def enhance_image(uploaded_url):
    response = requests.get(ENHANCE_API_URL + uploaded_url)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('image_url')
    return None

# Function to download image from the URL
def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return response.content
    return None

# Handler for the /start command
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("<b>Welcome! Send me an image to enhance.</b>", parse_mode='html')

# Handler for received images
@client.on(events.NewMessage(pattern='photo'))
async def handle_photo(event):
    # Get the largest photo available
    photo = event.message.photo
    file_id = photo.id
    
    # Get the file URL from Telegram
    file = await client.download_media(photo)
    
    # Upload to tmpfiles.org
    uploaded_url = upload_to_tmpfiles(file)
    
    if uploaded_url:
        await event.reply("<b>Enhancing your image...</b>", parse_mode='html')
        
        # Enhance the image using the API
        enhanced_image_url = enhance_image(uploaded_url)
        
        if enhanced_image_url:
            # Download the enhanced image
            enhanced_image_data = download_image(enhanced_image_url)
            
            if enhanced_image_data:
                # Send the enhanced image back to the user
                await event.reply_photo(enhanced_image_data, caption="Here is your enhanced image!")
            else:
                await event.reply("<b>Failed to download the enhanced image.</b>", parse_mode='html')
        else:
            await event.reply("<b>Failed to enhance the image.</b>", parse_mode='html')
    else:
        await event.reply("<b>Failed to upload the image. Please try again.</b>", parse_mode='html')

# Run the bot
client.run_until_disconnected()
