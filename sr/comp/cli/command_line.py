"""srcomp command-line interface."""

from __future__ import print_function

import sys
import argparse

from . import print_schedule
from . import knocked_out_teams
from . import validate
from . import schedule_league
from . import import_teams
from . import awards
from . import scorer

def add_list_commands(subparsers):
    def command(settings):
        commands = subparsers.choices.keys()
        print(" ".join(commands))

    parser = subparsers.add_parser('list-commands',
                                   help='Lists the available commands; useful for adding auto-completion of command names')
    parser.set_defaults(func=command)

def argument_parser():
    """A parser for CLI tool command line arguments, from argparse."""
    parser = argparse.ArgumentParser(description='srcomp command-line interface')
    subparsers = parser.add_subparsers(title='commands')
    add_list_commands(subparsers)
    print_schedule.add_subparser(subparsers)
    knocked_out_teams.add_subparser(subparsers)
    validate.add_subparser(subparsers)
    schedule_league.add_subparser(subparsers)
    import_teams.add_subparser(subparsers)
    awards.add_subparser(subparsers)
    scorer.add_subparser(subparsers)
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
