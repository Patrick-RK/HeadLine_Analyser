import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", BASE_DIR)
DATABASE = os.path.join(DATA_DIR, "headlines.db")

SITES = {
    "rte": {
        "name": "RTÉ News",
        "url": "https://www.rte.ie/news/",
        "selector": "h3, h5",
    },
    "irishtimes": {
        "name": "Irish Times",
        "url": "https://www.irishtimes.com/news/",
        "selector": "h3",
    },
    "independent": {
        "name": "Irish Independent",
        "url": "https://www.independent.ie/irish-news/",
        "selector": "h2, h4",
    },
    "journal": {
        "name": "The Journal",
        "url": "https://www.thejournal.ie/",
        "selector": "div.title-redesign",
        "exclude_classes": [
            "daily-poll-title-redesign",
            "separator-title-redesign",
            "spotlight-title-image-container-redesign",
            "roundup-redesign-title",
        ],
    },
    "examiner": {
        "name": "Irish Examiner",
        "url": "https://www.irishexaminer.com/news/",
        "selector": "h5",
    },
    "thesun": {
        "name": "Irish Sun",
        "url": "https://www.thesun.ie/news/irish-news/",
        "selector": "h3",
    },
    "extra": {
        "name": "Extra.ie",
        "url": "https://extra.ie/news",
        "selector": "h2",
    },
}
