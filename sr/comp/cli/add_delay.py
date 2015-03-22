from __future__ import print_function

from datetime import timedelta
from dateutil.tz import tzlocal
import os.path
import re
import timelib

from . import yaml_round_trip as rtyaml

time_parse_regex = re.compile(r'^((?P<hours>\d+?)hr)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?$')

class BadDurationException(Exception):
    def __init__(self, time_str):
        msg = "Unable to parse duration string '{0}'.".format(time_str)
        super(BadDurationException, self).__init__(msg)

def parse_duration(time_str):
    parts = time_parse_regex.match(time_str)
    if not parts:
        if not time_str.isdigit():
            raise BadDurationException(time_str)
        else:
            s = int(time_str)
            return timedelta(seconds = s)
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)

def parse_time(when_str):
    when = timelib.strtodatetime(when_str)
    # Timezone information gets ignored, and the resulting datetime is
    # timezone-unaware. However the compstate needs timezone data to be
    # present.
    # Assume that the user wants their current timezone.
    when = when.replace(tzinfo = tzlocal())
    return when

def add_delay(schedule, delay_seconds, when):
    delays = schedule.get('delays')
    if not delays:
        delays = schedule['delays'] = []
    new_delay = {
        'delay': delay_seconds,
        'time': when
    }
    delays.append(new_delay)

def command(settings):
    schedule_path = os.path.join(settings.compstate, "schedule.yaml")
    schedule = rtyaml.load(schedule_path)

    how_long = parse_duration(settings.how_long)
    how_long_seconds = how_long.seconds

    when = parse_time(settings.when)
    when = when.replace(microsecond = 0)

    add_delay(schedule, how_long_seconds, when)

    rtyaml.dump(schedule_path, schedule)

    return how_long, when

def add_arguments(parser):
    parser.add_argument('how_long',
                        help='How long to delay the competition for. ' \
                             'Specify either as a number of seconds or '\
                             'as a string of the form 1m30s.')
    parser.add_argument('when',
                        nargs='?',
                        default='now',
                        help="When the delay should occur. This can be " \
                             "anything which PHP's strtotime would be "
                             "able to parse. Assumes all times are in "
                             "the current timezone, regardless of input.")

def add_subparser(subparsers):
    parser = subparsers.add_parser('add-delay',
                                   help='Add a delay the competition state')
    parser.add_argument('compstate', help='competition state repository')
    add_arguments(parser)
    parser.set_defaults(func=command)
