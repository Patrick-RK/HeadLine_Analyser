FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download transformer models so first scrape doesn't timeout
RUN python -c "from transformers import pipeline; \
    pipeline('sentiment-analysis', model='cardiffnlp/twitter-roberta-base-sentiment-latest'); \
    pipeline('sentiment-analysis', model='siebert/sentiment-roberta-large-english')"

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "--timeout", "300", "--workers", "1", "app:app"]
