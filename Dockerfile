# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set environment variables (optional - for safety use .env in docker-compose)
ENV PYTHONUNBUFFERED=1

# Run bot
CMD ["python", "main.py"]
