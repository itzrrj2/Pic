# Use the official Python image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for SRGAN
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Clone the SRGAN repository and install dependencies
RUN git clone https://github.com/twhui/SRGAN.git && \
    cd SRGAN && \
    pip install -r requirements.txt

# Set working directory to SRGAN
WORKDIR /app/SRGAN

# Copy the requirements.txt and bot.py into the container
COPY requirements.txt .
COPY bot.py .

# Install any Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (replace with your actual bot token)
ENV BOT_TOKEN="YOUR_BOT_TOKEN"

# Run the bot
CMD ["python", "bot.py"]
