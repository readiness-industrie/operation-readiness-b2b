FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends clamav ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt requirements.lock ./
RUN pip install --upgrade pip && pip install -r requirements.lock
COPY . .
RUN export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')" \
    && export FIELD_ENCRYPTION_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')" \
    && export BACKUP_ENCRYPTION_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')" \
    && DEBUG=false ALLOWED_HOSTS=build.invalid python manage.py collectstatic --noinput

USER 10001:10001
EXPOSE 10000
CMD ["sh", "-c", "gunicorn readiness.wsgi:application --bind 0.0.0.0:${PORT:-10000} --workers ${WEB_CONCURRENCY:-2} --threads 2 --timeout 60 --access-logfile - --error-logfile -"]
