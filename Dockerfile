# Use the official Python image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for Waifu2x
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install required Python dependencies
RUN pip install torch==1.13.1+cpu \
    Pillow==9.2.0 \
    numpy==1.21.5 \
    requests==2.28.1 \
    waifu2x==1.0.4 \
    && rm -rf /var/lib/apt/lists/*

# Copy the bot.py into the container
COPY bot.py .

# Set environment variables (replace with your actual bot token)
ENV BOT_TOKEN="7734597847:AAG1Gmx_dEWgM5TR3xgljzr-_NpJnL4Jagc"

# Run the bot
CMD ["python", "bot.py"]
