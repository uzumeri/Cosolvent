FROM python:3.11-slim
# Environment
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="/app"

WORKDIR /app

# Install system dependencies (ntpdate)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ntpsec-ntpdate && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY src/services/profile_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/services/profile_service/ .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Expose service port
EXPOSE 5000

# Entrypoint
ENTRYPOINT ["./entrypoint.sh"]
