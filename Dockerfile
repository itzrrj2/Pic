# Use the official Python image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download the Real-ESRGAN model
RUN mkdir -p models && \
    wget -O models/RealESRGAN_x4.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4.pth

# Copy the bot script
COPY bot.py .

# Set environment variables (replace with your actual bot token)
ENV BOT_TOKEN="7734597847:AAG1Gmx_dEWgM5TR3xgljzr-_NpJnL4Jagc"

# Run the bot
CMD ["python", "bot.py"]
