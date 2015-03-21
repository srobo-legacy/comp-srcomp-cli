
try:
    from sr.comp.http import update
except ImportError:
    update = None

COMMAND_NAME = 'update'

def fail(args):
    exit("Install sr.comp.http to enable the '{0}' command.".format(COMMAND_NAME))

def add_subparser(subparsers):
    global update
    if update:
        parser = subparsers.add_parser(COMMAND_NAME, help=update.__doc__)
        update.add_arguments(parser)
        parser.set_defaults(func=update.run_update)
    else:
        parser = subparsers.add_parser(COMMAND_NAME,
                                       help="Updates a compstate repo (unavailable)")
        parser.set_defaults(func=fail)
