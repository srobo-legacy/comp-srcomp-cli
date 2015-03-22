from __future__ import print_function

import json
import os.path
from paramiko import AutoAddPolicy, SSHClient
import urllib
import yaml

from sr.comp.raw_compstate import RawCompstate
from sr.comp.validation import validate

DEPLOY_USER = 'srcomp'
BOLD = '\033[1m'
FAIL = '\033[91m'
OKBLUE = '\033[94m'
ENDC = '\033[0m'

# Cope with Python 3 renaming raw_input
try: input = raw_input
except NameError: pass

def ssh_connection(host):
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(host, username = DEPLOY_USER)
    return client

def format_fail(*args):
    msg = ' '.join(map(str, args))
    return BOLD + FAIL + msg + ENDC

def print_fail(*args, **kargs):
    print(format_fail(*args), **kargs)

def print_buffer(buf):
    prefix = '> '
    print(prefix + prefix.join(buf.readlines()).strip())

def get_input(prompt):
    # Wrapper to simplify mocking
    return input(prompt)

def query(question, options, default=None):
    if default:
        assert default in options

    options = [o.upper() if o == default else o.lower() for o in options]
    assert len(set(options)) == len(options)
    opts = '/'.join(options)

    query = format_fail("{0} [{1}]: ".format(question.rstrip(), opts))

    while True:
        # Loop until we get a suitable response from the user
        resp = get_input(query).lower()

        if resp in options:
            return resp

        # If there's a default value, use that
        if default:
            return default

def query_bool(question, default_val = None):
    options = ('y', 'n')
    if default_val is True:
        default = 'y'
    elif default_val is False:
        default = 'n'
    else:
        default = None
    return query(question, options, default) == 'y'

def query_warn(msg):
    query_msg = "Warning: {0}. Continue?".format(msg)
    if not query_bool(query_msg, False):
        exit(1)

def ref_compstate(host):
    url = "ssh://{0}@{1}/~/compstate.git".format(DEPLOY_USER, host)
    return url

def deploy_to(compstate, host, revision, verbose):
    print(BOLD + "Deploying to {0}:".format(host) + ENDC)

    # Push the repo
    url = ref_compstate(host)
    # Make a new branch for this revision so that it's visible to
    # anything which fetches the repo; use the revision id in the
    # branch name to avoid race conditions without needing to come
    # up with our own unique identifier.
    # This also means we don't need to worry about whether or not the
    # revision exists in the target, since this push will simply no-op
    # if it's already present
    revspec = "{0}:refs/heads/deploy-{0}".format(revision)
    try:
        compstate.push(url, revspec)
    except RuntimeError as re:
        print_fail(re)
        exit(1)

    with ssh_connection(host) as client:
        cmd = "./update '{0}'".format(revision)
        _, stdout, stderr = client.exec_command(cmd)
        retcode = stdout.channel.recv_exit_status()

        if verbose or retcode != 0:
            print_buffer(stdout)

        print_buffer(stderr)

        return retcode

def get_deployments(args):
    deployments_name = 'deployments.yaml'
    deployments_path = os.path.join(args.compstate, deployments_name)
    if not os.path.exists(deployments_path):
        print_fail("Cannot deploy state without a {0}.".format(deployments_name))
        exit(1)

    with open(deployments_path, 'r') as dp:
        raw_deployments = yaml.load(dp)
    hosts = raw_deployments['deployments']

    return hosts

def get_current_state(host):
    url = "http://{0}/comp-api/state".format(host)
    try:
        page = urllib.urlopen(url)
        raw_state = json.load(page)
    except:
        return None
    else:
        return raw_state['state']

def check_host_state(compstate, host, revision):
    """
    Compares the host state to the revision we want to deploy. If the
    host's state isn't in the history of the deploy revision then various
    options are presented to the user.

    Returrns whether or not to skip deploying to the host.
    """
    SKIP = True
    UPDATE = False
    state = get_current_state(host)
    if not state:
        tpl = "Failed to get state for {0}, cannot advise about history." \
              " Deploy anyway?"
        if query_bool(tpl.format(host, state), True):
            return UPDATE
        else:
            return SKIP

    if state == revision:
        print("Host {0} already has requested revision ({1})".format(host, revision[:8]))
        return SKIP

    # Ideal case:
    if compstate.has_ancestor(state):
        return UPDATE

    # Check for unknown commit
    if not compstate.has_commit(state):
        tpl = "Host {0} has unknown state '{1}'. Try to fetch it?"
        if query_bool(tpl.format(host, state), True):
            compstate.fetch('origin', quiet=True)
            compstate.fetch(ref_compstate(host), quiet=True)

    # Old revision:
    if compstate.has_descendant(state):
        tpl = "Host {0} has more recent state '{1}'. Deploy anyway?"
        if query_bool(tpl.format(host, state), True):
            return UPDATE
        else:
            return SKIP

    # Some other revision:
    if compstate.has_commit(state):
        tpl = "Host {0} has sibling state '{1}'. Deploy anyway?"
        if query_bool(tpl.format(host, state), True):
            return UPDATE
        else:
            return SKIP

    # An unknown state
    tpl = "Host {0} has unknown state '{1}'. Deploy anyway?"
    if query_bool(tpl.format(host, state), True):
        return UPDATE
    else:
        return SKIP

def require_no_changes(compstate):
    if compstate.has_changes:
        print_fail("Cannot deploy state with local changes.",
                   "Commit or remove them and re-run.")
        compstate.show_changes()
        exit(1)

def require_valid(compstate):
    try:
        comp = compstate.load()
    except Exception as e:
        print_fail("State cannot be loaded: {0}".format(e))
        exit(1)

    num_errors = validate(comp)
    if num_errors:
        query_warn("State has validation errors (see above)")

def command(args):
    hosts = get_deployments(args)
    compstate = RawCompstate(args.compstate, local_only=False)

    require_no_changes(compstate)
    require_valid(compstate)
    revision = compstate.rev_parse('HEAD')

    for host in hosts:
        if not args.skip_host_check:
            skip_host = check_host_state(compstate, host, revision)
            if skip_host:
                print(BOLD + "Skipping {0}.".format(host) + ENDC)
                continue

        retcode = deploy_to(compstate, host, revision, args.verbose)
        if retcode != 0:
            # TODO: work out if it makes sense to try to rollback here?
            print_fail("Failed to deploy to '{0}' (exit status: {1}).".format(host, retcode))
            exit(retcode)

    print(BOLD + OKBLUE + "Success" + ENDC)

def add_options(parser):
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--skip-host-check', action='store_true',
                        help='skips checking the current state of the hosts')

def add_subparser(subparsers):
    help_msg = 'Deploy a given competition state to all known hosts'
    parser = subparsers.add_parser('deploy', help=help_msg, description=help_msg)
    add_options(parser)
    parser.add_argument('compstate', help='competition state repository')
    parser.set_defaults(func=command)
