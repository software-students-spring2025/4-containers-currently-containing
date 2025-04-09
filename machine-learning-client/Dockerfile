# Use a Python base image that supports mediapipe (3.10 or 3.11)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libgl1 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --upgrade pip
RUN pip install mediapipe opencv-python-headless numpy

# Copy your app code into the container
WORKDIR /app
COPY main.py .

# Default command
CMD ["python", "main.py"]
