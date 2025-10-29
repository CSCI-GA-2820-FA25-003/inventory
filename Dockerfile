FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv && pipenv install --system --deploy

COPY . .
EXPOSE 8080
CMD ["gunicorn","-b","0.0.0.0:8080","wsgi:app"]
