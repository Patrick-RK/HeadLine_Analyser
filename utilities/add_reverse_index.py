from datetime import datetime

def add_reverse_column(headings):
    data = []
    total_headings = len(headings)
    today_date = datetime.today().strftime('%Y-%m-%d')
    seen_headings = set()  # Set to track seen headings

    # Loop through all headings and create a reverse position for each
    for i, heading in enumerate(headings):
        text_content = heading.strip()  # Get the text and strip any extra spaces
        
        # Only add if this heading hasn't been seen before
        if text_content not in seen_headings:
            reverse_position = total_headings - i - 1  # Calculate reverse position (N-1, N-2,...)
            data.append([today_date, text_content, reverse_position])
            seen_headings.add(text_content)  # Add to the seen set to avoid duplicates
    
    return data
