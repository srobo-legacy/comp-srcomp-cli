"""srcomp command-line interface."""

from __future__ import print_function

import argparse
import sys

from . import add_delay
from . import awards
from . import delay
from . import deploy
from . import import_schedule
from . import import_teams
from . import knocked_out_teams
from . import match_order_teams
from . import midi_show_control_interface
from . import list_midi_ports
from . import print_schedule
from . import schedule_league
from . import scorer
from . import shift_matches
from . import show_schedule
from . import summary
from . import validate
from . import yaml_round_trip


def add_list_commands(subparsers):
    def command(settings):
        commands = subparsers.choices.keys()
        print(" ".join(commands))

    help_text = 'Lists the available commands; useful for adding ' \
                'auto-completion of command names'

    parser = subparsers.add_parser('list-commands', help=help_text)
    parser.set_defaults(func=command)


def argument_parser():
    """A parser for CLI tool command line arguments, from argparse."""
    parser = argparse.ArgumentParser(description='srcomp command-line interface')
    subparsers = parser.add_subparsers(title='commands')
    add_list_commands(subparsers)

    add_delay.add_subparser(subparsers)
    awards.add_subparser(subparsers)
    delay.add_subparser(subparsers)
    deploy.add_subparser(subparsers)
    import_schedule.add_subparser(subparsers)
    import_teams.add_subparser(subparsers)
    knocked_out_teams.add_subparser(subparsers)
    list_midi_ports.add_subparser(subparsers)
    match_order_teams.add_subparser(subparsers)
    midi_show_control_interface.add_subparser(subparsers)
    print_schedule.add_subparser(subparsers)
    schedule_league.add_subparser(subparsers)
    scorer.add_subparser(subparsers)
    shift_matches.add_subparser(subparsers)
    show_schedule.add_subparser(subparsers)
    summary.add_subparser(subparsers)
    validate.add_subparser(subparsers)
    yaml_round_trip.add_subparser(subparsers)

    return parser


def main(args=None):
    """Run as the CLI tool."""
    if args is None:
        args = sys.argv[1:]
    parser = argument_parser()
    settings = parser.parse_args(args)
    if 'func' in settings:
        settings.func(settings)
    else:
        parser.print_help()
