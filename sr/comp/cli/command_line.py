"""srcomp command-line interface."""
import sys
import argparse

from . import print_schedule
from . import knocked_out_teams
from . import validate

def argument_parser():
    """A parser for CLI tool command line arguments, from argparse."""
    parser = argparse.ArgumentParser(description='srcomp command-line interface')
    subparsers = parser.add_subparsers(title='commands')
    print_schedule.add_subparser(subparsers)
    knocked_out_teams.add_subparser(subparsers)
    validate.add_subparser(subparsers)
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
