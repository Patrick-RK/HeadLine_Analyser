![alt text](<Screenshot 2024-10-07 at 19.28.42.png>)


HeadLine_Analyser

HeadLine_Analyser is a Python tool that scrapes news headlines from websites, analyzes their sentiment using VADER, and generates visualizations that show sentiment plotted against the headline position on the page.

Features

Scrapes headlines from news websites using Selenium and BeautifulSoup.
Analyzes the sentiment of headlines.
Plots both the raw sentiment scores and moving averages of the sentiment.
Setup

Clone the Repository:
bash
Copy code
git clone https://github.com/yourusername/HeadLine_Analyser.git
cd HeadLine_Analyser
Install Dependencies:
bash
Copy code
pip install -r requirements.txt
Run the Tool: Modify main.py with your target URL and run:
bash
Copy code
python main.py
Output

The program will generate graphs showing sentiment trends and raw sentiment scores. The graphs are saved in the graphs/ folder.