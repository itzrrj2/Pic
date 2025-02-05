import requests
import telebot

# Telegram Bot Token
BOT_TOKEN = "7734597847:AAG1Gmx_dEWgM5TR3xgljzr-_NpJnL4Jagc"
bot = telebot.TeleBot(BOT_TOKEN)

# Function to upload image to Telegraph
def upload_to_telegraph(image_path):
    with open(image_path, 'rb') as img:
        files = {'file': img}
        response = requests.post('https://telegra.ph/upload', files=files)
    
    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and 'src' in result[0]:
            return f"https://telegra.ph{result[0]['src']}"
    return None

# Handle photo messages
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # Get highest quality photo
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

        # Download image locally
        img_data = requests.get(file_url).content
        image_path = "temp.jpg"
        with open(image_path, "wb") as img_file:
            img_file.write(img_data)

        # Upload to Telegraph
        telegraph_url = upload_to_telegraph(image_path)
        if not telegraph_url:
            bot.reply_to(message, "❌ Failed to upload image to Telegraph.")
            return

        # Send to AI enhancement API
        enhancement_api_url = f"https://ar-api-08uk.onrender.com/remini?url={telegraph_url}"
        response = requests.get(enhancement_api_url)

        # Check if enhancement was successful
        if response.status_code == 200:
            api_response = response.json()
            enhanced_image_url = api_response.get("image_url")  # Assuming API returns {"image_url": "https://tmpfiles.org/dl/.../example.png"}

            if enhanced_image_url:
                # Download enhanced image from tmpfiles.org
                enhanced_img_data = requests.get(enhanced_image_url).content
                enhanced_image_path = "enhanced.jpg"
                with open(enhanced_image_path, "wb") as img_file:
                    img_file.write(enhanced_img_data)

                # Send enhanced image to user
                with open(enhanced_image_path, "rb") as img_file:
                    bot.send_photo(message.chat.id, img_file, caption="✨ Here is your enhanced image!")

            else:
                bot.reply_to(message, "❌ Enhancement failed, no image URL received.")
        else:
            bot.reply_to(message, f"❌ API Error: {response.status_code}")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Start polling for messages
bot.polling()
