# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot script into the container
COPY . .

# Set environment variables for security (replace values in a .env file)
ENV TELEGRAM_BOT_TOKEN="7734597847:AAGmGMwx_TbWXWa35s3XEWkH0lenUahToO4"
ENV IMAGE_UPLOAD_API="https://tmpfiles.org/api/v1/upload"
ENV ENHANCE_API="https://ar-api-08uk.onrender.com/remini?url="

# Command to run the bot
CMD ["python", "bot.py"]
