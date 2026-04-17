FROM python:3.11-slim

WORKDIR /service

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY url_checker_backend ./url_checker_backend

ENV PORT=8000

# Intentionally wrong module path for runtime failure practice.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
