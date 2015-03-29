from __future__ import print_function

def command(settings):
    from sr.comp.comp import SRComp
    import os.path

    comp = SRComp(os.path.realpath(settings.compstate))

    teams_last_round = set()
    for i, matches in enumerate(comp.schedule.knockout_rounds):
        teams_this_round = set()
        for game in matches:
            teams_this_round.update(game.teams)

        print("Teams not in round {}".format(i))
        out = teams_last_round - teams_this_round
        print(", ".join(t for t in out if t is not None))
        teams_last_round = teams_this_round
        print()

def add_subparser(subparsers):
    parser = subparsers.add_parser('knocked-out-teams',
                                   help='show the teams knocked out of each knockout round')
    parser.add_argument('compstate', help='competition state repository')
    parser.set_defaults(func=command)
