import csv
import os
from datetime import datetime

def save_data_csv(data):
    # Get today's date in 'YYYY-MM-DD' format
    today_date = datetime.today().strftime('%Y-%m-%d')
    
    # Define the directory and file path
    output_dir = '/headings/'
    csv_file = f'{output_dir}headings_output_{today_date}.csv'
    
    # Create the directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save data to CSV
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['date', 'heading', 'rev_position'])  # Write header
        writer.writerows(data)  # Write data rows
    
    print(f"CSV file '{csv_file}' has been created with the headings.")
