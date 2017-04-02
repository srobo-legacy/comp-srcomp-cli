from __future__ import print_function

__description__ = "Summaries the teams scoring the most match points"

def command(settings):
    from collections import defaultdict, Counter
    from functools import partial
    from itertools import chain
    import os.path
    from pprint import pprint

    from sr.comp.comp import SRComp

    comp = SRComp(os.path.realpath(settings.compstate))

    all_scores = (comp.scores.tiebreaker, comp.scores.knockout, comp.scores.league)
    all_points = dict(chain.from_iterable(s.game_points.items() for s in all_scores))

    points_map = defaultdict(partial(defaultdict, list))

    for match, points in all_points.items():
        for tla, team_points in points.items():
            points_map[team_points][tla].append(match)

    for points, team_info in sorted(points_map.items()):
        print("{0:>3} teams scored {1}".format(len(team_info), points))

    max_points = max(points_map.keys())
    max_points_infos = points_map[max_points]

    print()
    print("The following team(s) scored {0} points:".format(max_points))
    for tla, matches in max_points_infos.items():
        print("{0} in match(es): {1}".format(tla, ", ".join(
            "{0}{1}".format(*x) for x in matches
        )))


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        'top-match-points',
        help=__description__,
        description=__description__,
    )
    parser.add_argument('compstate',
                        help='competition state repo')
    parser.set_defaults(func=command)
