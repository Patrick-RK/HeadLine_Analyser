from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Lazy-loaded transformer models (heavy imports, load once on first use)
_roberta_pipe = None
_siebert_pipe = None
def _get_roberta():
    global _roberta_pipe
    if _roberta_pipe is None:
        from transformers import pipeline
        _roberta_pipe = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            top_k=None,
            truncation=True,
        )
    return _roberta_pipe


def _get_siebert():
    global _siebert_pipe
    if _siebert_pipe is None:
        from transformers import pipeline
        _siebert_pipe = pipeline(
            "sentiment-analysis",
            model="siebert/sentiment-roberta-large-english",
            truncation=True,
        )
    return _siebert_pipe



def _run_roberta(texts):
    """Run CardiffNLP RoBERTa on a list of texts."""
    pipe = _get_roberta()
    batch_results = pipe(texts, batch_size=16)
    out = []
    for result in batch_results:
        # result is a list of dicts: [{'label': 'positive', 'score': 0.9}, ...]
        scores = {r["label"].lower(): r["score"] for r in result}
        pos = scores.get("positive", 0)
        neg = scores.get("negative", 0)
        compound = pos - neg  # simple compound: range [-1, 1]
        if pos > neg and pos > scores.get("neutral", 0):
            sentiment = "Positive"
        elif neg > pos and neg > scores.get("neutral", 0):
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        out.append({"score": round(compound, 4), "sentiment": sentiment})
    return out


def _run_siebert(texts):
    """Run SiEBERT on a list of texts."""
    pipe = _get_siebert()
    batch_results = pipe(texts, batch_size=16)
    out = []
    for result in batch_results:
        label = result["label"].upper()
        conf = result["score"]
        compound = conf if label == "POSITIVE" else -conf
        sentiment = "Positive" if label == "POSITIVE" else "Negative"
        out.append({"score": round(compound, 4), "sentiment": sentiment})
    return out



def headline_analyser(headlines):
    """
    Analyzes the sentiment of headlines using VADER + transformer models.

    Args:
        headlines: List of [date, text, reverse_position] lists from add_reverse_column.

    Returns:
        List of dicts with headline text and sentiment scores from all models.
    """
    vader = SentimentIntensityAnalyzer()
    texts = [h[1] for h in headlines]

    # Run all models
    roberta_results = _run_roberta(texts)
    siebert_results = _run_siebert(texts)

    results = []
    for i, headline_data in enumerate(headlines):
        text = headline_data[1]
        vs = vader.polarity_scores(text)
        overall = (
            "Positive" if vs["compound"] > 0
            else "Negative" if vs["compound"] < 0
            else "Neutral"
        )
        results.append({
            "date": datetime.today().strftime("%Y-%m-%d"),
            "headline": text,
            "position": headline_data[2],
            # VADER
            "neg": vs["neg"],
            "neu": vs["neu"],
            "pos": vs["pos"],
            "compound": vs["compound"],
            "overall_sentiment": overall,
            # RoBERTa
            "roberta_score": roberta_results[i]["score"],
            "roberta_sentiment": roberta_results[i]["sentiment"],
            # SiEBERT
            "siebert_score": siebert_results[i]["score"],
            "siebert_sentiment": siebert_results[i]["sentiment"],
        })

    return results
