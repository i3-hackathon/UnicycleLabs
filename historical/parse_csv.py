import csv
import fileinput
import json

from dateutil import parser as dateutil_parser
from dateutil import tz

from models import all_models

TZ_GERMANY = tz.gettz('Europe/Berlin')
TZ_UTC = tz.tzutc()

def main(infile, day_of_month, hour_of_day):
    reader = csv.reader(infile)
    reader.next()
    latlngs = []
    days = set()
    hours = set()
    for row in reader:
        pickup_dt = parse_utc_datetime(row[2])
        if pickup_dt.hour == hour_of_day and pickup_dt.day == day_of_month:
            latlngs.append(all_models.LatLng({'lat': row[5], 'lng': row[6]}))
    raw_latlngs = [ll.raw for ll in latlngs]
    print json.dumps(raw_latlngs, sort_keys=True, indent=4, separators=(',', ': '))

def parse_utc_datetime(dt_str, local_tz=TZ_GERMANY):
    return dateutil_parser.parse(dt_str, dayfirst=True).replace(tzinfo=TZ_UTC).astimezone(local_tz)

if __name__ == '__main__':
    day_of_month = 12
    hour_of_day = 13
    main(fileinput.input(), day_of_month, hour_of_day)
