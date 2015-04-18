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
    """
    Converts an iterable of strings containing pipe-separated ids into
    a tuple: ``(ids, schedule)``. The ``ids`` is a list of unique ids
    in the order which they first appear, the ``schedule`` is a list of
    lists of ids in each line.
    """

    ids = list()
    schedule = []
    for match in schedule_lines:
        match_ids = match.split('|')
        uniq_match_ids = set(match_ids)
        assert len(match_ids) == len(uniq_match_ids), match_ids
        schedule.append(match_ids)

        for id_ in match_ids:
            if id_ not in ids:
                ids.append(id_)

    return ids, schedule

def ignore_ids(ids, ids_to_remove):
    for i in ids_to_remove:
        ids.remove(i)

def get_id_subsets(ids, limit):
    num_ids = len(ids)

    extra = num_ids - limit

    if extra == 0:
        # Only one posibility -- use all of them
        yield ids

    elif extra == 1:
        for idx in range(len(ids)):
            ids_clone = ids[:]
            ids_clone.pop(idx)
            yield ids_clone

    elif extra == 2:
        for idx1 in range(len(ids)):
            for idx2 in range(idx1+1, len(ids)):
                ids_clone = ids[:]
                ids_clone.pop(idx2)
                ids_clone.pop(idx1)
                yield ids_clone

    elif extra == 3:
        for idx1 in range(len(ids)):
            for idx2 in range(idx1+1, len(ids)):
                for idx3 in range(idx2+1, len(ids)):
                    ids_clone = ids[:]
                    ids_clone.pop(idx3)
                    ids_clone.pop(idx2)
                    ids_clone.pop(idx1)
                    yield ids_clone

    else:
        # TODO: consider generalising the above or adding more handling
        raise Exception("Too many empty slots to compensate for ({0}).".format(extra))

def build_id_team_maps(ids, team_ids):
    # If there are more ids than team_ids we want to ensure that we minimize
    # the number of matches which have empty places and also the number of
    # empty places in any given match.
    # This function generates possible mappings of ids to teams as needed
    # in order to explore excluding different ids.
    #
    # Note: this function does _not_ explore mapping the same subset of
    # ids to the given teams since that doesn't achieve any changes in
    # which matches have empty spaces.

    for id_subset in get_id_subsets(ids, len(team_ids)):
        yield dict(zip(id_subset, team_ids))

def build_matches(id_team_map, schedule, arena_ids):
    from collections import namedtuple
    BadMatch = namedtuple('BadMatch', ['arena', 'num', 'num_teams'])

    num_arenas = len(arena_ids)

    matches = {}
    bad_matches = []
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
                bad_matches.append(BadMatch(arena, match_num, num_teams))

    return matches, bad_matches

def are_better_matches(best, new):
    from collections import Counter
    def get_empty_places_map(bad_matches):
        empty_places_map = Counter()
        for bad_match in bad_matches:
            num_empty = TEAMS_PER_GAME - bad_match.num_teams
            empty_places_map[num_empty] += 1
        return empty_places_map

    best_map = get_empty_places_map(best)
    new_map  = get_empty_places_map(new)

    possible_empty_places = set(list(best_map.keys()) + list(new_map.keys()))

    # Even single matches with lots of empty slots are bad
    for num_empty_places in sorted(possible_empty_places, reverse=True):
        if new_map[num_empty_places] < best_map[num_empty_places]:
            return True

    return False


def get_best_fit(ids, team_ids, schedule, arena_ids):
    best = None
    for id_team_map in build_id_team_maps(ids, team_ids):
        matches, bad_matches = build_matches(id_team_map, schedule, arena_ids)

        if len(bad_matches) == 0:
            # Nothing bad about these, ship them
            return matches, bad_matches

        if best is None or are_better_matches(best[1], bad_matches):
            best = (matches, bad_matches)

    assert best is not None

    return best


def order_teams(compstate_path, team_ids):
    """
    Order teams either randomly or, if there's a layout available, by location.
    """
    import os.path
    import yaml

    from sr.comp.stable_random import Random

    layout_yaml = os.path.join(compstate_path, 'layout.yaml')
    if not os.path.exists(layout_yaml):
        # No layout; go random
        random = Random()
        random.seed("".join(team_ids))
        random.shuffle(team_ids)
        return team_ids

    with open(layout_yaml, 'r') as lf:
        layout_raw = yaml.load(lf)
        layout = layout_raw['layout']

    ordered_teams = []
    for group in layout:
        ordered_teams += next(iter(group.values()))

    layout_teams = set(ordered_teams)
    assert len(layout_teams) == len(ordered_teams), "Some teams appear twice in the layout!"

    all_teams = set(team_ids)
    missing = all_teams - layout_teams
    assert not missing, "Some teams not in layout: {0}.".format(", ".join(missing))

    all_teams = set(team_ids)
    extra = layout_teams - all_teams
    if extra:
        print("WARNING: Extra teams in layout will be ignoreed: {0}."
                    .format(", ".join(extra)))
        for tla in extra:
            ordered_teams.remove(tla)

    return ordered_teams


def build_schedule(schedule_lines, ids_to_ignore, team_ids, arena_ids):
    # Collect up the ids used
    ids, schedule = load_ids_schedule(schedule_lines)

    # Ignore any ids we've been told to
    if ids_to_ignore:
        ignore_ids(ids, args.ignore_ids.split(','))

    # Sanity checks
    num_ids = len(ids)
    num_teams = len(team_ids)
    assert num_ids >= num_teams, "Not enough places in the schedule " \
                                 "(need {0}, got {1}).".format(num_ids, num_teams)

    # Get matches
    matches, bad_matches = get_best_fit(ids, team_ids, schedule, arena_ids)

    return matches, bad_matches


def command(args):
    with open(args.schedule, 'r') as sfp:
        schedule_lines = tidy(sfp.readlines())

    # Grab the teams and arenas
    try:
        team_ids, arena_ids = load_teams_areans(args.compstate)
    except Exception as e:
        print("Failed to load existing state ({0}).".format(e))
        print("Make it valid (consider removing the league.yaml) and try again.")
        exit(1)

    # Semi-randomise
    team_ids = order_teams(args.compstate, team_ids)

    matches, bad_matches = build_schedule(schedule_lines, args.ignore_ids,
                                          team_ids, arena_ids)

    # Print any warnings about the matches
    for bad_match in bad_matches:
        tpl = "Warning: match {arena}:{num} only has {num_teams} teams."
        print(tpl.format(**bad_match._asdict()))

    # Save the matches to the file
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
