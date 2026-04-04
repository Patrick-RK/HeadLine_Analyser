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


def _run_gpt(texts):
    """Run GPT/Claude API sentiment analysis.

    TODO: Drop in API key via GPT_API_KEY env var and uncomment the
    implementation below.  The function should return a list of dicts
    with 'score' (float, -1 to 1) and 'sentiment' (Positive/Negative/Neutral).
    """
    # import os, json, requests
    # api_key = os.environ.get("GPT_API_KEY")
    # if not api_key:
    #     return [{"score": None, "sentiment": None}] * len(texts)
    #
    # prompt = (
    #     "Rate the sentiment of each headline below as a JSON array. "
    #     "Each entry should have 'score' (-1.0 to 1.0) and 'sentiment' "
    #     "(Positive, Negative, or Neutral).\n\n"
    #     + "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))
    # )
    # resp = requests.post(
    #     "https://api.openai.com/v1/chat/completions",
    #     headers={"Authorization": f"Bearer {api_key}"},
    #     json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]},
    # )
    # return json.loads(resp.json()["choices"][0]["message"]["content"])

    return [{"score": None, "sentiment": None}] * len(texts)



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
    gpt_results = _run_gpt(texts)

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
            # GPT (placeholder until API key is set)
            "gpt_score": gpt_results[i]["score"],
            "gpt_sentiment": gpt_results[i]["sentiment"],
        })

    return results
