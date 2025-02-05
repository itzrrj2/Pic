# Use a lightweight Python image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy bot script
COPY bot.py .

# Install dependencies
RUN pip install python-telegram-bot==13.7 requests

# Run the bot
CMD ["python", "bot.py"]
