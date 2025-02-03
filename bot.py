import os
import requests
from pyrogram import Client, filters
from pyrogram.types import InputFile  # Corrected import
from pyrogram.types import Message

# Set your bot token and API URLs
API_TOKEN = '7734597847:AAGmGMwx_TbWXWa35s3XEWkH0lenUahToO4'
UPLOAD_URL = 'https://tmpfiles.org/api/v1/upload'
ENHANCE_API_URL = 'https://ar-api-08uk.onrender.com/remini?url='

# Create the Pyrogram client
app = Client("enhance_bot", bot_token=API_TOKEN)

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

# Handler for /start command
@app.on_message(filters.command('start'))
async def start(client, message: Message):
    await message.reply("<b>Welcome! Send me an image to enhance.</b>", parse_mode='html')

# Handler for received images
@app.on_message(filters.photo)
async def handle_photo(client, message: Message):
    # Get the largest photo available
    photo = message.photo
    file_id = photo.file_id
    
    # Get the file URL from Telegram
    file_info = await client.get_file(file_id)
    file_url = file_info.file_url
    
    # Upload to tmpfiles.org
    uploaded_url = upload_to_tmpfiles(file_url)
    
    if uploaded_url:
        await message.reply("<b>Enhancing your image...</b>", parse_mode='html')
        
        # Enhance the image using the API
        enhanced_image_url = enhance_image(uploaded_url)
        
        if enhanced_image_url:
            # Download the enhanced image
            enhanced_image_data = download_image(enhanced_image_url)
            
            if enhanced_image_data:
                # Send the enhanced image back to the user
                await message.reply_photo(InputFile(enhanced_image_data), caption="Here is your enhanced image!")
            else:
                await message.reply("<b>Failed to download the enhanced image.</b>", parse_mode='html')
        else:
            await message.reply("<b>Failed to enhance the image.</b>", parse_mode='html')
    else:
        await message.reply("<b>Failed to upload the image. Please try again.</b>", parse_mode='html')

# Run the bot
app.run()
