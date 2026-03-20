from datetime import datetime


def add_reverse_column(headings):
    data = []
    today_date = datetime.today().strftime('%Y-%m-%d')
    seen_headings = set()

    for heading in headings:
        text_content = heading.strip()

        if text_content not in seen_headings:
            seen_headings.add(text_content)
            data.append([today_date, text_content, 0])

    # Assign gap-free reverse positions after dedup
    total = len(data)
    for i, row in enumerate(data):
        row[2] = total - i - 1

    return data
