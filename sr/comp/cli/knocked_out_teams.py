from __future__ import print_function

def round_name(rounds_left):
    if rounds_left == 0:
        return "Finals"
    elif rounds_left == 1:
        return "Semi Finals"
    elif rounds_left == 2:
        return "Quarter Finals"
    return ""

def command(settings):
    from sr.comp.comp import SRComp
    import os.path

    comp = SRComp(os.path.realpath(settings.compstate))

    teams_last_round = set()
    last_round_num = len(comp.schedule.knockout_rounds) - 1
    for i, matches in enumerate(comp.schedule.knockout_rounds):
        teams_this_round = set()
        for game in matches:
            teams_this_round.update(game.teams)

        print("Teams not in round {} ({})".format(i, round_name(last_round_num - i)))
        out = teams_last_round - teams_this_round
        teams_out = [t for t in out if t is not None]
        for tla in teams_out:
            print(tla, comp.teams[tla].name)
        teams_last_round = teams_this_round
        print()

def add_subparser(subparsers):
    parser = subparsers.add_parser('knocked-out-teams',
                                   help='show the teams knocked out of each knockout round')
    parser.add_argument('compstate', help='competition state repository')
    parser.set_defaults(func=command)
