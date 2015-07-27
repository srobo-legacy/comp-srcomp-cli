from __future__ import print_function

MAX_MATCHES = 15
DISPLAY_NAME_WIDTH = 18

def first(iterable):
    return next(i for i in iterable)

def command(settings):
    import os.path
    from datetime import datetime, timedelta

    from sr.comp.comp import SRComp

    comp = SRComp(os.path.realpath(settings.compstate))

    matches = comp.schedule.matches
    now = datetime.now(comp.timezone)
    current_matches = list(comp.schedule.matches_at(now))

    if not settings.all:
        time = now - timedelta(minutes=10)

        matches = [slot for slot in matches
                        if first(slot.values()).start_time >= time]

        matches = matches[:int(settings.limit)]

    def teams_str(teams):
        return ':'.join(tla.center(5) if tla else '-' for tla in teams)

    def print_col(text, last=False):
        print(text, end='|')

    empty_teams = teams_str(' ' * 4)
    teams_len = len(empty_teams)

    print_col(' Num Time  ')
    map(print_col, (a.display_name.center(teams_len)
                    for a in comp.arenas.values()))
    print_col('Display Name'.center(DISPLAY_NAME_WIDTH))
    print()

    arena_ids = comp.arenas.keys()
    for slot in matches:
        m = first(slot.values())
        print_col(" {0:>3} {1:%H:%M} ".format(m.num, m.start_time))

        for a_id in arena_ids:
            if a_id in slot:
                print_col(teams_str(slot[a_id].teams))
            else:
                print_col(empty_teams)

        print_col(m.display_name.center(DISPLAY_NAME_WIDTH))

        if m in current_matches:
            print(' *')
        else:
            print()

def add_subparser(subparsers):
    parser = subparsers.add_parser('show-schedule',
                                   help='show the match schedule')
    parser.add_argument('compstate',
                        help='competition state repo')
    parser.add_argument('--all', action='store_true',
                        help='show all matches, not just the upcoming ones (ignores --limit)')
    parser.add_argument('--limit', default=MAX_MATCHES,
                        help='how many matches to show (default: {0})'.format(MAX_MATCHES))
    parser.set_defaults(func=command)
