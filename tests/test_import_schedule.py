
from sr.comp.cli.import_schedule import get_id_subsets, build_schedule


def test_num_ids_equasl_num_teams():
    ids = list(range(4))
    maps = list(get_id_subsets(ids, 4))

    expected = [ids]

    assert maps == expected, "Only one possible combination when same number of ids as teams"

def test_one_spare_id():
    ids = list(range(3))
    num_teams = 2

    ids_set = set(ids)

    subsets = list(get_id_subsets(ids, num_teams))

    assert len(subsets) == 3, "Should have as many maps as valid permutations"

    # Don't actually care what the mappings are, only that all are explored
    ids_omitted = []
    for subset in subsets:
        ids_used = set(subset)
        omitted = ids_set - ids_used

        assert len(omitted) == 1, "Omitted wrong number of ids"
        ids_omitted.append(omitted.pop())

    assert set(ids_omitted) == ids_set, "Should have omitted each id once"

def test_two_spare_ids():
    ids = list(range(4))
    num_teams = 2

    ids_set = set(ids)

    subsets = list(get_id_subsets(ids, num_teams))

    expected_omitted = set(["0,1", "0,2", "0,3", "1,2", "1,3", "2,3"])

    assert len(subsets) == len(expected_omitted), "Should have as many maps as valid permutations"

    # Don't actually care what the mappings are, only that all are explored
    ids_omitted = []
    for subset in subsets:
        ids_used = set(subset)
        omitted = ids_set - ids_used

        assert len(omitted) == 2, "Omitted wrong number of ids"
        ids_omitted.append(",".join(map(str, sorted(omitted))))

    assert set(ids_omitted) == expected_omitted, "Should have omitted each id pair once"

def test_build_schedule():
    lines = ['0|1|2|3', '1|2|3|4']
    teams = ['ABC', 'DEF', 'GHI']

    matches, bad = build_schedule(lines, '', teams, ['A'])

    expected_matches = {
        0: {'A':  [None, 'ABC', 'DEF', 'GHI']},
        1: {'A': ['ABC', 'DEF', 'GHI', None]},
    }

    assert expected_matches == matches, "Wrong matches"

    assert bad == [], "Should not be any 'bad' matches"

def test_build_schedule_appaerance_order():
    lines = ['3|1|0|4', '1|2|4|0']
    teams = ['ABC', 'DEF', 'GHI']

    matches, bad = build_schedule(lines, '', teams, ['A'])

    expected_matches = {
        0: {'A':  [None, 'ABC', 'DEF', 'GHI']},
        1: {'A': ['ABC', None, 'GHI', 'DEF']},
    }

    assert expected_matches == matches, "Wrong matches"

    assert bad == [], "Should not be any 'bad' matches"
