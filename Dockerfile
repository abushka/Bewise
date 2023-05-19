FROM python:3.9-slim

# Установка зависимостей для psycopg2
RUN apt-get update \
    && apt-get install -y postgresql-client libpq-dev gcc

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]