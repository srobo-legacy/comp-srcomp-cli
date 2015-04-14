from __future__ import print_function

from sr.comp.cli import add_delay
from sr.comp.cli import deploy


def command(args):
    from sr.comp.raw_compstate import RawCompstate

    hosts = deploy.get_deployments(args.compstate)
    compstate = RawCompstate(args.compstate, local_only=False)

    deploy.require_no_changes(compstate)

    if not args.no_pull:
        with deploy.exit_on_exception():
            compstate.pull_fast_forward()

    how_long, when = add_delay.command(args)

    if args.when != 'now':
        msg = "Confirm adding {0} delay at {1}".format(how_long, when)
        if not deploy.query_bool(msg, default_val=True):
            print("Leaving state with local modifications")
            exit()

    deploy.require_valid(compstate)

    with deploy.exit_on_exception(kind=RuntimeError):
        compstate.stage('schedule.yaml')
        msg = "Adding {0} delay at {1}".format(args.how_long, when)
        compstate.commit(msg)

    deploy.run_deployments(args, compstate, hosts)


def add_subparser(subparsers):
    help_msg = 'Add and deploy a delay to the competition'
    parser = subparsers.add_parser('delay', help=help_msg, description=help_msg)
    parser.add_argument('--no-pull', action='store_true',
                        help='skips updating to the latest revision')
    deploy.add_options(parser)
    parser.add_argument('compstate', help='competition state repository')
    add_delay.add_arguments(parser)
    parser.set_defaults(func=command)
