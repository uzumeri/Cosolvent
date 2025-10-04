FROM python:3.11-slim

# 1. Copy & install the shared library
COPY src/shared /opt/shared
WORKDIR /opt/shared
RUN pip install --no-cache-dir -e .

# 2. Copy & install the service
COPY src/services/admin_service /opt/service
WORKDIR /opt/service
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8003
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8003"]
