FROM python:3.11-slim

WORKDIR /service

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY url_checker_backend ./url_checker_backend

ENV PORT=8000

# Use the runtime PORT provided by the deployment platform when available.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
