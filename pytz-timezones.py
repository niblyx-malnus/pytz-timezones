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
    # Create Hoon file for the timezone
    filename = f'{directory_name}/{zone_name.replace("/", "-").replace("_", "-").replace("+", "--").lower()}.hoon'

    # Build CSV content as a string
    csv_lines = ['Time,Offset,Name']
    for transition in transitions:
        utc_time, offset, rule_name = transition
        offset_str = format_offset(offset)
        # Zero-pad year to 4 digits (strftime %Y doesn't pad years < 1000)
        time_str = f'{utc_time.year:04d}-{utc_time.month:02d}-{utc_time.day:02d}T{utc_time.hour:02d}:{utc_time.minute:02d}:{utc_time.second:02d}'
        csv_lines.append(f'{time_str},{offset_str},{rule_name}')

    csv_content = '\n'.join(csv_lines)

    # Wrap in Hoon format with to-wain:format
    hoon_content = f"%-  to-wain:format\n'''\n{csv_content}\n'''\n"

    with open(filename, mode='w') as file:
        file.write(hoon_content)

    return filename

def main():
    # Create directory named 'pytz'
    directory_name = 'lib/pytz'
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    
    # Write the pytz version to version.hoon
    version_filename = f'{directory_name}/version.hoon'
    with open(version_filename, mode='w') as version_file:
        version_file.write(f"%-  to-wain:format\n'''\n{pytz.__version__}\n'''\n")

    # Prepare names file
    names_filename = f'{directory_name}/names.hoon'

    # Get all timezones
    timezones = pytz.all_timezones
    timezone_names = []

    for zone_name in timezones:
        transitions = get_all_dst_transitions(zone_name)
        write_transitions_to_csv(directory_name, zone_name, transitions)
        print(zone_name)
        timezone_names.append(zone_name)

    # Write names file with Hoon wrapper
    names_content = '\n'.join(timezone_names)
    with open(names_filename, mode='w') as names_file:
        names_file.write(f"%-  to-wain:format\n'''\n{names_content}\n'''\n")

if __name__ == "__main__":
    main()
