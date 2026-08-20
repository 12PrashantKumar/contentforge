FROM python:3.12-slim

# don't write .pyc, don't buffer stdout (so logs show up live in Cloud Run)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# install deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the app
COPY . .

# Cloud Run provides $PORT (usually 8080). uvicorn must bind to it, on 0.0.0.0.
# Using shell form so $PORT expands.
CMD uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080}