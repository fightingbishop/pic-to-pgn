# Use a lightweight, official Python base image
FROM python:3.9-slim

# Install the Tesseract OCR software into the Linux operating system
RUN apt-get update && apt-get install -y tesseract-ocr && rm -rf /var/lib/apt/lists/*

# Set the working directory for our app
WORKDIR /app

# Copy our requirements file and install the Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy our actual API code into the container
COPY main.py .

# Tell the server how to start our FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]