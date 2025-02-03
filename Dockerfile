# Use official Python runtime
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot script into the container
COPY . .

# Set environment variables (Replace this in a .env file for security)
ENV TELEGRAM_BOT_TOKEN=""

# Command to run the bot
CMD ["python", "bot.py"]
