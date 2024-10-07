# __init__.py for utilities package

# External libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Internal utilities
from .add_reverse_index import add_reverse_column
from .fetch_website import fetch_website_with_selenium 
from .clean_html import strip_html
from .save_csv_today import save_data_csv
from .analyse_headlines import save_sentiment_analysis_to_csv, headline_analyser
from .sentiment_plot import plot_gradient_sentiment_line, plot_moving_averages
from .moving_averages import calculate_moving_averages

# Optional: Define __all__ for wildcard imports
__all__ = [
    'webdriver', 'Service', 'By', 'BeautifulSoup',
    'add_reverse_column', 'fetch_website_with_selenium', 'strip_html',
    'save_data_csv', 'save_sentiment_analysis_to_csv', 'headline_analyser',
    'plot_gradient_sentiment_line', 'plot_moving_averages', 'calculate_moving_averages'
]
