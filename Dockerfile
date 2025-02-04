# Use the official Python image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for RealESRGAN
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Clone RealESRGAN repo and install dependencies
RUN git clone https://github.com/xinntao/Real-ESRGAN.git && \
    cd Real-ESRGAN && \
    pip install -r requirements.txt

# Download the pre-trained model for RealESRGAN (example model)
RUN cd Real-ESRGAN && \
    wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4.pth -P weights/

# Set working directory to RealESRGAN
WORKDIR /app/Real-ESRGAN

# Copy the requirements.txt and bot.py into the container
COPY requirements.txt .
COPY bot.py .

# Install any Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (replace with your actual bot token)
ENV BOT_TOKEN="7734597847:AAG1Gmx_dEWgM5TR3xgljzr-_NpJnL4Jagc"

# Run the bot
CMD ["python", "bot.py"]
