# ./src/services/user_management_service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install service dependencies
COPY src/services/search_service/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code
COPY src/shared ./src/shared

# Copy application source code
COPY src/services/search_service/src ./src
COPY src/services/search_service/entrypoint.sh ./

# Ensure entrypoint is executable
RUN chmod +x entrypoint.sh

# Set Python path
ENV PYTHONPATH=/app/src

# Expose FastAPI port
EXPOSE 8000

# Launch via entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
