
from datetime import datetime

def add_reverse_column(headings):
    data = []
    total_headings = len(headings)
    today_date = datetime.today().strftime('%Y-%m-%d')


    # Loop through all headings and create a reverse position for each
    for i, heading in enumerate(headings):
        text_content = heading.strip()  # Get the text and strip any extra spaces
        reverse_position = total_headings - i - 1  # Calculate reverse position (N-1, N-2,...)
        data.append([today_date, text_content, reverse_position])
    
    return data
