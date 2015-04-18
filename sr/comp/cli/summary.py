from __future__ import print_function

def first(iterable):
    return next(i for i in iterable)

def counter_to_string(cntr):
    string = ", ".join("{1} {0}".format(*item) for item in cntr.items())
    return string

def command(args):
    from collections import Counter

    from sr.comp.comp import SRComp

    comp = SRComp(args.compstate)

    print("Number of arenas:", len(comp.arenas), \
            "({0})".format(", ".join(comp.arenas.keys())))

    print("Number of teams:", len(comp.teams),
            "({0} rookies)".format(sum(1 for t in comp.teams.values() if t.rookie)))

    slots_by_type = Counter(first(slot.values()).type.value \
                                for slot in comp.schedule.matches)
    slots_by_type_str = counter_to_string(slots_by_type)

    assert sum(slots_by_type.values()) == len(comp.schedule.matches)

    print("Number of match slots:", len(comp.schedule.matches),
            "({0})".format(slots_by_type_str))

    games_by_type = Counter(game.type.value \
                                for slot in comp.schedule.matches \
                                for game in slot.values())
    games_by_type_str = counter_to_string(games_by_type)

    print("Number of games:", sum(games_by_type.values()),
            "({0})".format(games_by_type_str))

def add_subparser(subparsers):
    help_msg = "Show summary data about a compstate"

    parser = subparsers.add_parser('summary', help=help_msg, description=help_msg)
    parser.add_argument('compstate', help='competition state repository')
    parser.set_defaults(func=command)
