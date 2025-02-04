# Use official Python base image
FROM python:3.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    python3-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory to GFPGAN repo
WORKDIR /GFPGAN

# Clone GFPGAN repository
RUN git clone https://github.com/TencentARC/GFPGAN.git .

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download pre-trained GFPGAN model
RUN wget https://github.com/TencentARC/GFPGAN/releases/download/v1.0.0/gfpgan.pth -P ./experiments/pretrained_models

# Expose port (optional)
EXPOSE 5000

# Command to run GFPGAN for image enhancement
CMD ["python", "inference_gfpgan.py", "--input", "input.jpg", "--output", "output.jpg", "--model_path", "experiments/pretrained_models/gfpgan.pth"]
