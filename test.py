import os
import shutil
import subprocess
import pandas as pd
from datetime import datetime, timedelta

# global
workspace_path = os.getcwd()

# Generate sample data for testing
def generate_sample_data():
    pass # assume sample data will be given

# Clean up sample data
def cleanup_sample_data():
    # shutil.rmtree('workspace')
    pass

# Run encoder.py for a specific date
def run_encoder(date):
    date_str = date.strftime('%Y%m%d')
    subprocess.run(['python3', 'encoder.py', '--date', date_str])

# Check if raw_data.csv is correctly updated
def check_raw_data(date):
    date_str = date.strftime('%Y%m%d')
    raw_data_path = workspace_path + '/raw_data.csv'
    if not os.path.exists(raw_data_path):
        return False
    raw_data = pd.read_csv(raw_data_path)
    return any(raw_data['date'] == int(date_str))

def get_last_weekday(date):
    date -= timedelta(days=1)  # Start from the previous day
    while date.weekday() >= 5:  # 5 and 6 represent Saturday and Sunday
        date -= timedelta(days=1)
    return date

if __name__ == "__main__":
    # Set up sample data
    generate_sample_data()

    # Run encoder.py for each date and check if raw_data.csv is correctly updated
    start_date = datetime.strptime("20190517", "%Y%m%d")
    end_date = datetime.strptime("20190716", "%Y%m%d")

    date = start_date
    while date <= end_date:
        run_encoder(date)
        last_date = get_last_weekday(date)
        if last_date.strftime("%Y%m%d") != "20190711":
            assert check_raw_data(last_date), f"Data for {last_date.strftime('%Y%m%d')} is not correctly updated in raw_data.csv."
        date += timedelta(days=1)
        
    # Clean up sample data
    cleanup_sample_data()
