# Use the official Python image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for OpenCV, Pillow, and other required libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgthread-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot script into the container
COPY bot.py .

# Set environment variables (replace with your actual bot token)
ENV BOT_TOKEN="7734597847:AAG1Gmx_dEWgM5TR3xgljzr-_NpJnL4Jagc"

# Run the bot
CMD ["python", "bot.py"]
