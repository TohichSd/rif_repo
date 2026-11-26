FROM python:3.12-slim-bookworm AS build
WORKDIR /build
COPY src/ ./src/
RUN python -m zipapp src -m app:main -o app.pyz

FROM python:3.12-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/app.pyz \
    PORT=8080
WORKDIR /app
COPY requirements-runtime.txt ./
RUN python -m pip install --no-cache-dir -r requirements-runtime.txt
COPY --from=build /build/app.pyz ./
COPY alembic.ini ./
COPY migrations/ ./migrations/

FROM runtime AS heroku-release
ENV PGSSLMODE=require
USER 10001:10001
CMD ["python", "-m", "alembic", "upgrade", "head"]

FROM runtime AS web
USER 10001:10001
EXPOSE 8080
CMD ["gunicorn", "--access-logfile", "-", "app:application"]
