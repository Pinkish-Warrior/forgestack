# FLAW: unpinned base image tag — "latest" is a moving target, so the
# exact image contents (and any CVEs in it) change without anyone noticing.
FROM python:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .

EXPOSE 5000

# FLAW: no USER directive — the process runs as root inside the container,
# so a compromise of the app (e.g. via the SQLi endpoint) gives the
# attacker root inside the container rather than a restricted account.
CMD ["python", "app.py"]
