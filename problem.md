# Encoder Programming

## The context: We are onboarding a new data vendor.
- The data is built from market data and we assume that markets are opened on all weekdays.
- The data vendor sent us daily historical files in zip format located under the following structure `section1/historical/yyyymmdd.zip` for us to backfill
  -  He mentioned that he usually publishes one daily file at around 8:00am ET the next day.

Additionally,
- Since the mid of June 2019, our data team has been pulling the daily data updates in csv format from
the data vendor’s ftp server and saving these by setting the name of the file to the download time in
nanoseconds since Unix Epoch;
- our filesystem is structured in the following manner `section1/yyyymmdd/file_timestamp_in_nanoseconds_since_unix_epoch.csv`.
- For example, the file for the 26th of June 2019 arriving on the 27th of June 2019 at 8:19am ET would be located in `20190626/1561637940000000000.csv`
  - Note: 1561637940000000000 is the download time in nanoseconds since Unix Epoch

## The challenge: 
- Write a python application whose entry point is encoder.py which builds and continuously updates a point in time file raw_data.csv (we understand that csv is not the best format to store data like this, but for the purpose of this project we assume we store data in csv).
- This file will contain the vendor data timestamped around the time the data is or would have been received, this file could then be safely used by other users or processes for simulation or in production.
- The application should run from the command line with one input parameter only, the date we are running the application at (not the date we are retrieving the data for).
- Your application will load and write the relevant data received on that date and append it to `raw_data.csv` as if we ran it on that date.
- Your application will allow us to populate past dates as if we ran it in the past and update future dates **going forward in production**. This means it needs to be able to load historical *.zip files from vendor, or `*.csv` files downloaded by our data team historically, or `*.csv` file to be delivered in live, depending on `--date YYYYMMDD` (date argument provided to the application)
- Note that in production we will start running the application around 8:00am given the vendor’s specifications mentioned above.
