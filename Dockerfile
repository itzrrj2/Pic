# Use Python 3.10 as base image
FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Python script into the container
COPY bot.py /app/bot.py

# Set the environment variable for the bot token (optional, could be handled in other ways)
ENV BOT_TOKEN=7734597847:AAGmGMwx_TbWXWa35s3XEWkH0lenUahToO4

# Command to run the bot
CMD ["python", "bot.py"]
