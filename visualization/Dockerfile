FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the visualization script
COPY main.py .

# Create directory for plots
RUN mkdir -p /app/plots

CMD ["python", "main.py"]
