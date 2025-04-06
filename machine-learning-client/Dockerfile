FROM python:3.10

WORKDIR /app

# Install system packages (MediaPipe needs these)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY Pipfile Pipfile.lock ./

# Install pipenv and dependencies
RUN pip install pipenv && pipenv install --system

# Copy source code
COPY . .

# Run your hand tracking script
CMD ["python", "main.py"]
