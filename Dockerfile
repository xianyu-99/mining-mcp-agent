FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for pdfplumber or lxml)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default command
CMD ["python", "src/agent/client.py"]
