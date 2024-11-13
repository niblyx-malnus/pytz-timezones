import os
import csv
from datetime import datetime
import pytz

JAN_1_1 = datetime(1, 1, 1, 0, 0, 0)
JAN_1_2000 = datetime(2000, 1, 1, 0, 0, 0)

def format_offset(offset):
    total_seconds = offset.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{int(hours):+03}:{int(minutes):02}"

def get_all_dst_transitions(zone_name):
    tz = pytz.timezone(zone_name)

    if not hasattr(tz, '_utc_transition_times'):
        # In the case where the timezone has no transitions, it is a timezone
        # defined by a single offset; get the offset from the arbitrary date
        # January 1st, 2000 but record as starting on what the IANA tzdb considers
        # to be the beginning of time: January 1st, 1
        offset = tz.utcoffset(JAN_1_2000)
        rule_name = tz.tzname(JAN_1_2000)
        return [(JAN_1_1, offset, rule_name)]
    else:
        # Get the transitions for the specified timezone
        transitions = []
        for dt in tz._utc_transition_times:
            try:
                local_time = tz.fromutc(dt)
                transitions.append((dt, local_time.utcoffset(), local_time.tzname()))
            except (OverflowError, ValueError) as e:
                assert dt == JAN_1_1, "invalid transition is not January 1, 0001"
                continue
        return transitions

def write_transitions_to_csv(directory_name, zone_name, transitions):
    # Create CSV file for the timezone
    filename = f'{directory_name}/{zone_name.replace("/", "-").replace("_", "-").replace("+", "--").lower()}.txt'
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerow(['Time', 'Offset', 'Name'])
        
        for transition in transitions:
            utc_time, offset, rule_name = transition
            offset_str = format_offset(offset)
            writer.writerow([utc_time.strftime('%Y-%m-%dT%H:%M:%S'), offset_str, rule_name])
    
    return filename

def main():
    # Create directory named 'pytz'
    directory_name = 'lib/pytz'
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    
    # Write the pytz version to version.hoon
    version_filename = f'{directory_name}/version.txt'
    with open(version_filename, mode='w', newline='') as version_file:
        version_file.write(pytz.__version__)
    
    # Prepare names file
    names_filename = f'{directory_name}/names.txt'
    with open(names_filename, mode='w', newline='') as names_file:
        # Get all timezones
        timezones = pytz.all_timezones
        
        for zone_name in timezones:
            transitions = get_all_dst_transitions(zone_name)
            write_transitions_to_csv(directory_name, zone_name, transitions)
            print(zone_name)
            names_file.write(f"{zone_name}\n")

if __name__ == "__main__":
    main()
