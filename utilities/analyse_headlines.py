from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def headline_analyser(headlines):
    """
    Analyzes the sentiment of a list of headlines using VADER.

    Args:
        headlines: List of [date, text, reverse_position] lists from add_reverse_column.

    Returns:
        List of dicts with headline text and sentiment scores.
    """
    analyzer = SentimentIntensityAnalyzer()
    results = []

    for headline_data in headlines:
        text = headline_data[1]
        sentiment_scores = analyzer.polarity_scores(text)
        overall = (
            'Positive' if sentiment_scores['compound'] > 0
            else 'Negative' if sentiment_scores['compound'] < 0
            else 'Neutral'
        )
        results.append({
            "date": datetime.today().strftime('%Y-%m-%d'),
            "headline": text,
            "position": headline_data[2],
            "neg": sentiment_scores['neg'],
            "neu": sentiment_scores['neu'],
            "pos": sentiment_scores['pos'],
            "compound": sentiment_scores['compound'],
            "overall_sentiment": overall,
        })

    return results
