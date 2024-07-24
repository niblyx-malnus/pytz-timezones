import os
import csv
from datetime import datetime, timezone
import pytz

def format_offset(offset):
    total_seconds = offset.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{int(hours):+03}:{int(minutes):02}"

def get_all_dst_transitions(zone_name):
    tz = pytz.timezone(zone_name)

    if not hasattr(tz, '_utc_transition_times'):
        now = datetime.now(pytz.utc)
        offset = tz.utcoffset(now)
        return [(datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone.utc), offset)]
    else:
        # Get the transitions for the specified timezone
        transitions = []
        for dt in tz._utc_transition_times:
            try:
                if dt == datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone.utc):
                    d = datetime(1800, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
                    local_time = tz.fromutc(d)
                    transitions.append((dt, local_time.utcoffset()))
                else:
                    local_time = tz.fromutc(dt)
                    transitions.append((dt, local_time.utcoffset()))
            except (OverflowError, ValueError) as e:
                print(f"Error processing transition for timezone {zone_name}: {dt}, Error: {e}")
                continue
        return transitions

def write_transitions_to_csv(directory_name, zone_name, transitions):
    # Create CSV file for the timezone
    filename = f'{directory_name}/{zone_name.replace("/", "_")}.csv'
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Offset'])
        
        for transition in transitions:
            utc_time, offset = transition
            offset_str = format_offset(offset)
            writer.writerow([utc_time.strftime('%Y-%m-%d %H:%M:%S'), offset_str])
    
    return filename

def main():
    # Create directory with pytz version
    directory_name = f"IANA_{pytz.__version__}"
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    
    # Prepare names file
    names_filename = f'{directory_name}/zone_names.txt'
    with open(names_filename, mode='w') as names_file:
        
        # Get all timezones
        timezones = pytz.all_timezones
        
        for zone_name in timezones:
            transitions = get_all_dst_transitions(zone_name)
            write_transitions_to_csv(directory_name, zone_name, transitions)
            names_file.write(f"{zone_name}\n")

if __name__ == "__main__":
    main()

