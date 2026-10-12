FROM python:3.12-slim

WORKDIR /app

# System deps for pandas/scikit-learn/bcrypt wheels to build cleanly on slim images
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production
EXPOSE 5000

# gunicorn, not the Flask dev server — this is the same entry point
# run.py exposes locally, just served properly for a container.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "run:app"]
