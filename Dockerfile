# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot script into the container
COPY bot.py .

# Set environment variable to avoid buffer issues
ENV PYTHONUNBUFFERED=1

# Command to run the bot
CMD ["python", "bot.py"]
