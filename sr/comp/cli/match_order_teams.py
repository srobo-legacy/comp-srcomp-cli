from __future__ import print_function

def command(args):
    from sr.comp.comp import SRComp

    comp = SRComp(args.compstate)
    matches = comp.schedule.matches

    remaining_teams = dict(comp.teams)

    for slot in matches:
        for arena, match in slot.items():
            print("## Match #{0} in Arena {1} (at {2:%H:%M})"
                  .format(match.num, arena, match.start_time))
            for tla in match.teams:
                team = remaining_teams.get(tla)
                if team:
                    print("  - {tla}: {name}".format(**team._asdict()))
                    remaining_teams.pop(tla)

            if remaining_teams:
                print()
            else:
                return
        if remaining_teams:
            print()
        else:
            return

def add_subparser(subparsers):
    help_msg = "Shows a list of teams, ordered by their first matches."
    description = help_msg + " Output is markdown, and can be converted " \
            " to PDF by piping through 'pandoc -V geometry:margin=1in'."

    parser = subparsers.add_parser('match-order-teams',
                                   help=help_msg,
                                   description=description)
    parser.add_argument('compstate', help='competition state repository')
    parser.set_defaults(func=command)
