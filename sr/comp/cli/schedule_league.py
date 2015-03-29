from __future__ import print_function, division

def max_possible_match_periods(sched_db):
    from datetime import timedelta

    # Compute from the contents of a schedule.yaml the number of league periods
    match_period_length = sched_db['match_slot_lengths']['total']
    total_league_time = sum((period['end_time'] - period['start_time']
                              for period in sched_db['match_periods']['league']),
                             timedelta())
    return int(total_league_time.total_seconds() // match_period_length)

def command(args):
    from multiprocessing import Pool
    import os.path
    import random
    import sys
    import yaml

    from sr.comp.cli.league_scheduler import Scheduler

    with open(os.path.join(args.compstate, 'arenas.yaml')) as f:
        arenas_db = yaml.load(f)
        arenas = arenas_db['arenas'].keys()
        num_corners = len(arenas_db['corners'])

    with open(os.path.join(args.compstate, 'teams.yaml')) as f:
        teams = yaml.load(f)['teams'].keys()

    with open(os.path.join(args.compstate, 'schedule.yaml')) as f:
        sched_db = yaml.load(f)
        max_periods = max_possible_match_periods(sched_db)

    base_matches = []
    for n in range(args.reschedule_from):
        match_slot = []
        for arena in arenas:
            match_slot.extend(sched_db['matches'][n][arena])
        base_matches.append(match_slot)

    scheduler = Scheduler(teams=teams,
                          max_match_periods=max_periods,
                          arenas=arenas,
                          num_corners=num_corners,
                          separation=args.spacing,
                          max_matchups=args.max_repeated_matchups,
                          appearances_per_round=args.appearances_per_round,
                          base_matches=base_matches,
                          enable_lcg=args.lcg)
    if args.parallel > 1:
        scheduler.lprint('Using {} threads'.format(args.parallel))
        pool = Pool(args.parallel)
        def get_output(data):
            yaml.dump({'matches': data}, sys.stdout)
            pool.terminate()
        for n in range(args.parallel):
            scheduler.random = random.Random()
            scheduler.tag = '[Thread {}] '.format(n)
            pool.apply_async(scheduler.run,
                             callback=get_output)
        pool.close()
        pool.join()
    else:
        output_data = scheduler.run()
        yaml.dump({'matches': output_data}, sys.stdout)


def add_subparser(subparsers):
    parser = subparsers.add_parser('schedule-league',
                                   help='generate a schedule for a league')
    parser.add_argument('compstate',
                        type=str,
                        help='competition state git repository')
    parser.add_argument('-s', '--spacing',
                        type=int,
                        default=2,
                        help='number of matches between any two appearances by a team')
    parser.add_argument('-r', '--max-repeated-matchups',
                        type=int,
                        default=2,
                        help='maximum times any team can face any given other team')
    parser.add_argument('-a', '--appearances-per-round',
                        type=int,
                        default=1,
                        help='number of times each team appears in each round')
    parser.add_argument('--lcg',
                        action='store_true',
                        dest='lcg',
                        help='enable LCG permutation')
    parser.add_argument('--parallel',
                        type=int,
                        default=1,
                        help='number of parallel threads')
    parser.add_argument('-f', '--reschedule-from',
                        type=int,
                        default=0,
                        help='first match to reschedule from')
    parser.set_defaults(func=command)
