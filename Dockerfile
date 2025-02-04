# Use a Python base image
FROM python:3.8-slim

# Set working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install system dependencies required for OpenCV and other libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (optional, if you're running a web app, not necessary for bots)
# EXPOSE 5000

# Set the entry point for the bot (the Python script that runs the bot)
CMD ["python", "bot.py"]
