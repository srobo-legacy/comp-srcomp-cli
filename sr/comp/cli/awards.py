from __future__ import print_function

import os.path

from sr.comp.comp import SRComp
from sr.comp.winners import Award

def command(settings):
    comp = SRComp(os.path.realpath(settings.compstate))

    def format_team(tla):
        team = comp.teams[tla]
        return '{} ({}{})'.format(tla,
                                  team.name,
                                  ' [rookie]' if team.rookie else '')

    for award in Award:
        print('~~~ {} ~~~'.format(award.value.upper()))
        recipients = comp.awards.get(award, None)
        if recipients is None:
            print('Not yet awarded.')
        elif not recipients:
            print('Awarded to nobody.')
        elif len(recipients) == 1:
            print(format_team(recipients[0]))
        else:
            print('Split between {} teams (a tie):'.format(len(recipients)))
            for recipient in recipients:
                print(format_team(recipient))

def add_subparser(subparsers):
    parser = subparsers.add_parser('awards',
                                   help='show who has been given awards')
    parser.add_argument('compstate',
                        help='competition state repo')
    parser.set_defaults(func=command)
