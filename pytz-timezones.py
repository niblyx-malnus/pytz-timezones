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
        offset = tz.utcoffset(JAN_1_2000)
        rule_name = tz.tzname(JAN_1_2000)
        return [(JAN_1_1, offset, rule_name)]
    else:
        transitions = []
        for dt in tz._utc_transition_times:
            try:
                local_time = tz.fromutc(dt)
                transitions.append((dt, local_time.utcoffset(), local_time.tzname()))
            except (OverflowError, ValueError) as e:
                assert dt == JAN_1_1, "invalid transition is not January 1, 0001"
                continue
        return transitions

def write_transitions_to_file(file, zone_name, transitions):
    rows = []

    for transition in transitions:
        utc_time, offset, rule_name = transition
        offset_str = format_offset(offset)
        rows.append([utc_time.strftime('%Y-%m-%dT%H:%M:%S'), offset_str, rule_name])
    
    file.write(f'{len(rows)} {zone_name}\n')
    writer = csv.writer(file, lineterminator='\n')
    writer.writerows(rows)

def main():
    # Create directory named 'lib/pytz'
    directory_name = 'lib'
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    
    # Open the pytz-data.txt file
    output_filename = f'{directory_name}/pytz-data.txt'
    with open(output_filename, mode='w', newline='') as output_file:
        # Write the pytz version
        output_file.write(f'{pytz.__version__}\n')
        
        # Write transitions for each timezone
        for zone_name in pytz.all_timezones:
            transitions = get_all_dst_transitions(zone_name)
            write_transitions_to_file(output_file, zone_name, transitions)

if __name__ == "__main__":
    main()
