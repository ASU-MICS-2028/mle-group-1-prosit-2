# NkwaPay loan demo (app/). Build context is limited by .dockerignore / .gcloudignore to src/, app/ and the fitted model.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ src/
COPY app/ app/
COPY data/models/scorer.joblib data/models/scorer.joblib
ENV PYTHONPATH=/srv PORT=8080
CMD exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
