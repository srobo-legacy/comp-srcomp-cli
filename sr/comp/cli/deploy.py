from __future__ import print_function

import os.path
from paramiko import AutoAddPolicy, SSHClient
import sys
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

def query_warn(msg):
    query = format_fail("Warning: {0}. Continue? [y/N]: ".format(msg))
    if input(query).lower() != 'y':
        exit(1)

def deploy_to(compstate, host, revision, verbose):
    print(BOLD + "Deploying to {0}:".format(host) + ENDC)

    # Push the repo
    url = "ssh://{0}@{1}/~/compstate.git".format(DEPLOY_USER, host)
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

def command(args):
    hosts = get_deployments(args)
    compstate = RawCompstate(args.compstate, local_only=False)

    if compstate.has_changes:
        print_fail("Cannot deploy state with local changes.",
                   "Commit or remove them and re-run.")
        compstate.show_changes()
        exit(1)

    try:
        comp = compstate.load()
    except Exception as e:
        print_fail("State cannot be loaded: {0}".format(e))
        exit(1)

    num_errors = validate(comp)
    if num_errors:
        query_warn("State has validation errors (see above)")

    revision = compstate.rev_parse('HEAD')

    for host in hosts:
        retcode = deploy_to(compstate, host, revision, args.verbose)
        if retcode != 0:
            # TODO: work out if it makes sense to try to rollback here?
            print_fail("Failed to deploy to '{0}' (exit status: {1}).".format(host, retcode))
            exit(retcode)

    print(BOLD + OKBLUE + "Success" + ENDC)

def add_subparser(subparsers):
    parser = subparsers.add_parser('deploy',
                                   help='Deploy a given competition state to all known hosts')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('compstate', help='competition state repository')
    parser.set_defaults(func=command)
