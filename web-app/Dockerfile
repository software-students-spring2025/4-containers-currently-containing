FROM python:3.10

WORKDIR /app

# Copy requirements
COPY Pipfile Pipfile.lock ./

# Install pipenv and dependencies
RUN pip install pipenv && pipenv install --system

# Copy source code
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]