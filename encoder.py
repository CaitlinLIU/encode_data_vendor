
import sys
import os
import time
import argparse
import numpy as np
import pandas as pd
import zipfile
from datetime import datetime, timedelta

# global
workspace_path = os.getcwd()

def print_log(log_str):
    """Log printer

    Args:
        log_str (string): print some log information locally
    """
    log = "["+ datetime.now().strftime("%Y-%m-%d %H%:%M:%S.%f") + "][LOG]: " + log_str
    print(log)

def check_date_valid(date_str):
    '''Check if the format of input_date valid
    
    Args:
        date_str (string): input_date parsed from command line
    '''
    try:
        datetime.strptime(date_str, '%Y%m%d')
        print_log(f"{date_str} is a valid date.")
    except ValueError:
        print_log(f"{date_str} is not a valid date. Exiting.")
        sys.exit(1)
    
def get_last_weekday(date_str):
    '''Obtain the data_date from input_date
    
    Args:
        date_str (string): input_date parsed from command line
    return:
        date_str (string): data_date (last trading date of input_date)
    '''
    date = datetime.strptime(date_str, '%Y%m%d')
    date -= timedelta(days=1)  # Start from the previous day
    while date.weekday() >= 5:  # 5 and 6 represent Saturday and Sunday
        date -= timedelta(days=1)
    return date.strftime("%Y%m%d")

def check_data_exist(file_date):
    '''Check the existence of the data file
    
    Args:
        file_date (string): data_date (last trading date of input_date)
    return:
        flag (string): get the file type in CSV or ZIP
    '''
    flag = ""
    if file_date >= '20190617':
        # Check if it exists every 30 seconds, but will cancel if more than 240 times (2 hours)
        csv_dir = workspace_path + f'/{file_date}/'
        max_attempts = 240
        attempts = 0
        while attempts < max_attempts:
            if os.path.exists(csv_dir) and os.listdir(csv_dir):
                print_log(f"{file_date} csv detected.")
                flag = "CSV"
                break
            else:
                print_log(f"{file_date} csv folder does not exist or is empty. Attampt [{attempts}]. Waiting for 30 seconds...")
                time.sleep(30)
                attempts += 1
        else:
            print_log(f"{file_date} csv folder was not found or remained empty after {max_attempts} attempts. Exiting.")
            sys.exit(1)
    else:
        zip_path = workspace_path + f'/historical/{file_date}.zip'
        if os.path.exists(zip_path):
            print_log(f"{file_date} zip detected.")
            flag = "ZIP"
        else:
            print_log(f"{file_date} zip was not found. Exiting.")
            sys.exit(1)
    return flag
    
def load_latest_csv_data(csv_dir):    
    '''Load the historical or upcoming CSV files
    
    Args:
        csv_dir (string): the csv directory of data_date (last trading date of input_date)
    '''
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    latest_file = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(csv_dir, f)))
    latest_file_path = os.path.join(csv_dir, latest_file)
    latest_csv_data = pd.read_csv(latest_file_path)
    latest_csv_data.insert(0, "time", latest_file.replace(".csv", ""))
    return latest_csv_data 
    
def load_zip_data(zip_path):   
    '''Load the historical ZIP files
    
    Args:
        zip_path (string): the zip file path of data_date (last trading date of input_date)
    '''
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_name = zip_ref.namelist()[0]
        with zip_ref.open(file_name) as file:
            zip_data = pd.read_csv(file)
            zip_data.insert(0, "time", np.nan)
            return zip_data

def load_file_data(file_date, file_type):
    '''Load the CSV/ZIP files
    
    Args:
        file_date (string): data_date (last trading date of input_date)
        file_type (string): ZIP or CSV
    '''
    print_log(f"loading data for {file_date} in {file_type}...")
    if file_type == "CSV":
        csv_dir = workspace_path + f'/{file_date}/'
        data = load_latest_csv_data(csv_dir)
    elif file_type == "ZIP":
        zip_path = workspace_path + f'/historical/{file_date}.zip'
        data = load_zip_data(zip_path)
    return data
        
def append_to_raw_data(file_data, raw_data_path):
    '''Build/Append raw_data.csv
    
    Args:
        file_data (DataFrame): raw data of data_date
        raw_data_path (string): output path
    '''
    print_log("Saving raw_data.csv...")
    if not os.path.exists(raw_data_path):
        file_data.to_csv(raw_data_path, mode='a', header=True, index=False)
    else:
        raw_data = pd.read_csv(raw_data_path, index_col=None)
        raw_data_append = pd.concat([raw_data, file_data], sort=False)
        raw_data_append = raw_data_append.drop_duplicates(subset=['time', 'date', 'unique_id'])
        raw_data_append.to_csv(raw_data_path, header=True, index=False)
        
    
    
if __name__ == "__main__":
    
    print("=====================")
    
    # 1. Parse the command-line argument to get the date.
    parser = argparse.ArgumentParser(description='Append data from a data vendor to raw_data.csv')
    parser.add_argument('--date', type=str, default=datetime.today().strftime('%Y%m%d'), help='Date in YYYYMMDD format')
    args = parser.parse_args()
    date_str = args.date  
    print_log(f"Date input: {date_str}")
    
    # 2. Check if the format of <input_date> valid.
    check_date_valid(date_str)
    
    # 3. Obtain the <data_date> and determine if the <data_date> is in the past, present, or future
    file_date = get_last_weekday(date_str)
    if file_date == "20190711": 
        file_date = get_last_weekday(file_date)
    print_log(f"Retrieve the data of {file_date}.")
    
    # 4. Check the existence of the data file:
    file_type = check_data_exist(file_date)

    # 3. retreive file data
    file_data = load_file_data(file_date, file_type)

    # 4. build/append output
    raw_data_path = workspace_path + "/raw_data.csv"
    append_to_raw_data(file_data, raw_data_path)
    
    print_log(f"Program finished on {file_date}.")
