# Using Python 3.13 as base image
FROM python:3.13-slim

# Set working directory in container
WORKDIR /app

# Copy requirements file (if you have one)
COPY requirements.txt .

# Install Python dependencies
RUN uv install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose port (adjust as needed)
EXPOSE 8000

# Command to run your application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]