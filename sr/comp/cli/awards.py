from __future__ import print_function

def command(settings):
    import os.path

    from sr.comp.comp import SRComp
    from sr.comp.winners import Award

    comp = SRComp(os.path.realpath(settings.compstate))

    def format_team(tla):
        team = comp.teams[tla]
        return u'{} ({}{})'.format(tla, team.name,
                                   ' [rookie]' if team.rookie else '')

    award_order = (Award.image, Award.web, Award.committee,
                   Award.rookie, Award.movement,
                   Award.third, Award.second, Award.first
                   )

    missing = set(Award) - set(award_order)
    assert not missing, "Awards missed!: {0}".format(", ".join(map(str, missing)))

    for award in award_order:
        print('### {}'.format(award.value.upper()))
        recipients = comp.awards.get(award, None)
        if recipients is None:
            print('  Not yet awarded.')
        elif not recipients:
            print('  Awarded to nobody.')
        elif len(recipients) == 1:
            print(" ", format_team(recipients[0]))
        else:
            print('  Split between {} teams (a tie):'.format(len(recipients)))
            for recipient in recipients:
                print("  ", format_team(recipient))
        print()

def add_subparser(subparsers):
    parser = subparsers.add_parser('awards',
                                   help='show who has been given awards')
    parser.add_argument('compstate',
                        help='competition state repo')
    parser.set_defaults(func=command)
