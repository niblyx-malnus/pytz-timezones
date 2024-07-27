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
        rule_name = tz.tzname(now)
        return [(datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone.utc), offset, rule_name)]
    else:
        # Get the transitions for the specified timezone
        transitions = []
        for dt in tz._utc_transition_times:
            try:
                local_time = tz.fromutc(dt)
                transitions.append((dt, local_time.utcoffset(), local_time.tzname()))
            except (OverflowError, ValueError) as e:
                print(f"Error processing transition for timezone {zone_name}: {dt}, Error: {e}")
                continue
        return transitions

def write_transitions_to_csv(directory_name, zone_name, transitions):
    # Create CSV file for the timezone
    filename = f'{directory_name}/{zone_name.replace("/", "-").replace("_", "-").replace("+", "--").lower()}.hoon'
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file, lineterminator='\n')
        # Write the header
        file.write("%-  to-wain:format\n'''\n")
        writer.writerow(['Time', 'Offset', 'Name'])
        
        for transition in transitions:
            utc_time, offset, rule_name = transition
            offset_str = format_offset(offset)
            writer.writerow([utc_time.strftime('%Y-%m-%dT%H:%M:%S'), offset_str, rule_name])
        
        # Write the footer
        file.write("'''\n")
    
    return filename

def main():
    # Create directory named 'pytz'
    directory_name = 'lib/pytz'
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    
    # Write the pytz version to version.hoon
    version_filename = f'{directory_name}/version.hoon'
    with open(version_filename, mode='w', newline='') as version_file:
        version_file.write("%-  to-wain:format\n'''\n")
        version_file.write(pytz.__version__)
        version_file.write("\n'''\n")
    
    # Prepare names file
    names_filename = f'{directory_name}/names.hoon'
    with open(names_filename, mode='w', newline='') as names_file:
        names_file.write("%-  to-wain:format\n'''\n")
        
        # Get all timezones
        timezones = pytz.all_timezones
        
        for zone_name in timezones:
            transitions = get_all_dst_transitions(zone_name)
            write_transitions_to_csv(directory_name, zone_name, transitions)
            names_file.write(f"{zone_name}\n")
        
        names_file.write("'''\n")

if __name__ == "__main__":
    main()
