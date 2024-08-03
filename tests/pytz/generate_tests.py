import pytz
import random
import pandas as pd
from datetime import datetime, timedelta
import os


# Set the seed for reproducibility
random.seed(927)

# Ensure the data directory exists
output_dir = 'data'
os.makedirs(output_dir, exist_ok=True)

# Function to generate a random datetime in a given year
def generate_random_datetime(year):
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31, 23, 59, 59)
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

# Function to perform the conversion and format datetime
def convert_timezones(input_dt, tz):
    utc_to_tz = None
    tz_to_utc = None
    
    try:
        utc_dt = input_dt.replace(tzinfo=pytz.utc)
        utc_to_tz = utc_dt.astimezone(pytz.timezone(tz)).strftime('%Y-%m-%dT%H:%M:%S')
    except Exception as e:
        pass
    
    try:
        local_dt = pytz.timezone(tz).localize(input_dt)
        tz_to_utc = local_dt.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S')
    except Exception as e:
        pass
    
    return utc_to_tz, tz_to_utc

# Generate the data
years = list(range(1800, 2100 + 1))
timezones = pytz.all_timezones

for tz in timezones:
    data = []
    for year in years:
        for _ in range(10):
            input_dt = generate_random_datetime(year)
            input_dt_str = input_dt.strftime('%Y-%m-%dT%H:%M:%S')
            utc_to_tz, tz_to_utc = convert_timezones(input_dt, tz)
            data.append({
                "Input": input_dt_str,
                "UTCtoTZ": utc_to_tz,
                "TZtoUTC": tz_to_utc
            })

    # Create DataFrame and handle null values
    df = pd.DataFrame(data)

    # Format the filename
    formatted_tz = tz.replace("/", "-").replace("_", "-").replace("+", "--").lower()
    filename = f'{output_dir}/{formatted_tz}.csv'

    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"CSV file generated for timezone: {tz} as {filename}")

print("All CSV files generated successfully.")

