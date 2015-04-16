import argparse
from datetime import datetime, timedelta
from pathlib import Path

import yaml

from sr.comp.yaml_loader import load as load_yaml


def command(args):
    schedule = load_yaml(str(args.compstate / 'schedule.yaml'))

    old_start = schedule['match_periods'][args.focus][0]['start_time']
    new_start = datetime.now(old_start.tzinfo)
    # round to 1-2 minutes ahead
    new_start -= timedelta(seconds=new_start.second,
                           microseconds=new_start.microsecond)
    new_start += timedelta(minutes=2)

    dt = new_start - old_start

    for group in schedule['match_periods'].values():
        for entry in group:
            entry['start_time'] += dt
            entry['end_time'] += dt
            if 'max_end_time' in entry:
                entry['max_end_time'] += dt

    with (args.compstate / 'schedule.yaml').open('w') as f:
        yaml.dump(schedule, f, default_flow_style=False)
    with (args.compstate / '.update-pls').open('w'):
        pass
    print('Shifted matches by {}'.format(dt))


def add_subparser(subparsers):
    parser = subparsers.add_parser('shift-matches', help='Shift matches up')
    parser.add_argument('compstate', type=Path,
                        help='competition state repository')
    parser.add_argument('focus', choices=('league', 'knockout'),
                        help='match period to focus')
    parser.set_defaults(func=command)
