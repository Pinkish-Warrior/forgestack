# FIX: pinned to an exact version+variant tag instead of "latest", so the
# base image contents are reproducible and reviewed deliberately.
FROM python:3.12.6-slim-bookworm

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

RUN chown -R appuser:appuser /app

# FIX: drop to a non-root user before running the app, so a compromise of
# the app doesn't hand the attacker root inside the container.
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
