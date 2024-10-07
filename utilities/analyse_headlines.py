import csv
import os
from datetime import datetime
from typing import List, Dict
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def headline_analyser(headlines: List[str]) -> List[Dict[str, str]]:
    """
    Analyzes the sentiment of a list of headlines using VADER.
    
    Args:
        headlines (List[str]): List of news headlines to analyze.
    
    Returns:
        List[Dict[str, str]]: A list of dictionaries containing each headline and its sentiment result.
    """
    analyzer = SentimentIntensityAnalyzer()
    results = []
    
    for headline_data in headlines:
        sentiment_scores = analyzer.polarity_scores(headline_data[1])
        overall_sentiment = 'Positive' if sentiment_scores['compound'] > 0 else 'Negative' if sentiment_scores['compound'] < 0 else 'Neutral'
        results.append({
            "date": datetime.today().strftime('%Y-%m-%d'),
            "headline": headline_data[1],
            "neg": sentiment_scores['neg'],  # Negative score
            "neu": sentiment_scores['neu'],  # Neutral score
            "pos": sentiment_scores['pos'],  # Positive score
            "compound": sentiment_scores['compound'],  # Compound score
            "overall_sentiment": overall_sentiment
        })
    
    return results


def save_sentiment_analysis_to_csv(results: List[Dict[str, str]], output_dir: str = '/sentiment', file_prefix: str = 'sentiment_analysis') -> None:
    """
    Saves the sentiment analysis results to a CSV file in the specified directory.
    
    Args:
        results (List[Dict[str, str]]): The sentiment analysis results.
        output_dir (str): The directory to save the CSV file.
        file_prefix (str): The prefix for the CSV file name.
    """
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate file name
    today_date = datetime.today().strftime('%Y-%m-%d')
    file_name = f'{output_dir}/{file_prefix}_{today_date}.csv'
    
    # Save data to CSV
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['Date', 'Headline', 'Negative', 'Neutral', 'Positive', 'Compound', 'Overall Sentiment'])
        # Write each result row
        for result in results:
            writer.writerow([
                result['date'], 
                result['headline'], 
                result['neg'], 
                result['neu'], 
                result['pos'], 
                result['compound'], 
                result['overall_sentiment']
            ])
    
    print(f"CSV file '{file_name}' has been created.")
