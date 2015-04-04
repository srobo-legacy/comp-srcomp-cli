from __future__ import print_function

import argparse

TEAMS_PER_GAME = 4

def tidy(lines):
    "Strip comments and trailing whitespace"
    schedule = []
    for line in lines:
        idx = line.find('#')
        if idx > -1:
            line = line[:idx]

        line = line.strip()

        if line:
            schedule.append(line)

    return schedule

def chunks_of_size(list_, size):
    list_ = list_[:]
    assert len(list_) % size == 0
    while len(list_):
        chunk = []
        for i in range(size):
            chunk.append(list_.pop(0))
        yield chunk

def league_yaml_path(compstate_path):
    import os.path

    league_yaml = os.path.join(compstate_path, 'league.yaml')
    return league_yaml

def dump_league_yaml(matches, file_path):
    import yaml

    with open(file_path, 'w') as lfp:
        empty = dict(matches=matches)
        yaml.dump(empty, lfp)

def load_teams_areans(compstate_path):
    import os.path

    from sr.comp.comp import SRComp

    league_yaml = league_yaml_path(compstate_path)

    if not os.path.exists(league_yaml):
        # If nothing there yet create an empty schedule so the state can load
        # Assume that if it is there it's in the right format
        dump_league_yaml({}, league_yaml)

    comp = SRComp(compstate_path)
    team_ids = list(sorted(comp.teams.keys()))
    arena_ids = list(sorted(comp.arenas.keys()))

    return team_ids, arena_ids

def load_ids_schedule(schedule_lines):
    ids = set()
    schedule = []
    for match in schedule_lines:
        match_ids = match.split('|')
        uniq_match_ids = set(match_ids)
        assert len(match_ids) == len(uniq_match_ids), match_ids
        ids |= uniq_match_ids
        schedule.append(match_ids)

    ids = list(sorted(ids))

    return ids, schedule

def ignore_ids(ids, ids_to_remove):
    for i in ids_to_remove:
        ids.remove(i)

def build_matches(ids, schedule, team_ids, arena_ids):
    id_team_map = dict(zip(ids, team_ids))
    num_arenas = len(arena_ids)

    matches = {}
    for match_num, match_ids in enumerate(schedule):
        assert len(match_ids) / TEAMS_PER_GAME <= num_arenas, \
            "Match {0} has too many ids".format(match_num)
        assert len(match_ids) % TEAMS_PER_GAME == 0, \
            "Match {0} has incompatible number of ids".format(match_num)

        match_teams = [id_team_map.get(id_) for id_ in match_ids]
        games = chunks_of_size(match_teams, TEAMS_PER_GAME)

        matches[match_num] = match = dict(zip(arena_ids, games))

        # Check that the match has enough actual teams; warn if not
        for arena, teams in match.items():
            num_teams = len(set(teams) - set([None]))
            if num_teams <= 2:
                tpl = "Warning: match {0}:{1} only has {2} teams."
                print(tpl.format(arena, match_num, num_teams))

    return matches


def command(args):
    from sr.comp.stable_random import Random

    with open(args.schedule, 'r') as sfp:
        schedule_lines = tidy(sfp.readlines())

    # Collect up the ids used
    ids, schedule = load_ids_schedule(schedule_lines)

    # Ignore any ids we've been told to
    if args.ignore_ids:
        ignore_ids(ids, args.ignore_ids.split(','))

    # Grab the teams and arenas
    team_ids, arena_ids = load_teams_areans(args.compstate)

    # Sanity checks
    num_ids = len(ids)
    num_teams = len(team_ids)
    assert num_ids >= num_teams, "Not enough places in the schedule " \
                                 "(need {0}, got {1}).".format(num_ids, num_teams)

    # Semi-randomise
    random = Random()
    random.seed("".join(team_ids))
    random.shuffle(team_ids)

    # Get matches
    matches = build_matches(ids, schedule, team_ids, arena_ids)

    league_yaml = league_yaml_path(args.compstate)
    dump_league_yaml(matches, league_yaml)

def add_subparser(subparsers):
    description = """
Import a league.yaml from a schedule file.

A schedule file specifies matches one-per-line, as follows:

A 'match' consists of a number of unique identifiers separated by pipe
characters. The total number of identifiers in the file should be equal
to or greater than the number of teams in the compstate.

The number of identifiers in a given match must be a multiple of the
number of teams per game (currently 4), up to the number of arenas in
the compstate.

Whitespace (other than newlines) within the file is ignored, as is any
content to the right of a hash character (#), including the hash. As a
result hash characters may be used to start line comments.
""".strip()

    parser = subparsers.add_parser('import-schedule',
                                   help='Import a league.yaml file from a schedule file',
                                   description=description,
                                   formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-i', '--ignore-ids', help='comma separated list of ids to ignore')
    parser.add_argument('compstate', help='competition state repository')
    parser.add_argument('schedule', help='schedule to import')
    parser.set_defaults(func=command)
