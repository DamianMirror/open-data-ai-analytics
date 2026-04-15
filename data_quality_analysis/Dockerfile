FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the analysis script
COPY main.py .

# Create directory for reports
RUN mkdir -p /app/reports

CMD ["python", "main.py"]
