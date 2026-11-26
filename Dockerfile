FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY src/app.py ./app.py

USER 10001:10001
EXPOSE 8080
CMD ["gunicorn", "--access-logfile", "-", "app:application"]
