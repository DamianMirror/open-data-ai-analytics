FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the data load script
COPY main.py .

# Create directories for data and reports
RUN mkdir -p /app/data /app/reports

CMD ["python", "main.py"]
