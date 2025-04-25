# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable for Telegram Bot Token
ENV TELEGRAM_BOT_TOKEN=7079552870:AAEHPQId2oaLw2c4dgZEUlJggctM5_fCwQw

# Run bot when the container starts
CMD ["python", "bot.py"]
