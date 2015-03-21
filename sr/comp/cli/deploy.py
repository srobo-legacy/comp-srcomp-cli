from __future__ import print_function

import os.path
from paramiko import AutoAddPolicy, SSHClient
import subprocess
import yaml

DEPLOY_USER = 'srcomp'
FAIL = '\033[91m'
ENDC = '\033[0m'

def ssh_connection(host):
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(host, username = DEPLOY_USER)
    return client

def print_fail(*args, **kargs):
    msg = ' '.join(args)
    print(FAIL + msg + ENDC, **kargs)

def print_buffer(buf):
    prefix = '> '
    print(prefix + prefix.join(buf.readlines()).strip())

def deploy_to(compstate, host, revision, verbose):
    print("Deploying to {0}:".format(host))

    # Push the repo
    url = "ssh://{0}@{1}/~/compstate.git".format(DEPLOY_USER, host)
    revspec = "{0}:deploy".format(revision)
    subprocess.check_call(['git', 'push', url, revspec], cwd=compstate)

    with ssh_connection(host) as client:
        _, stdout, stderr = client.exec_command('./update')
        retcode = stdout.channel.recv_exit_status()

        if verbose or retcode != 0:
            print_buffer(stdout)

        print_buffer(stderr)

        return retcode

def command(args):
    deployments_path = os.path.join(args.compstate, "deployments.yaml")
    with open(deployments_path, 'r') as dp:
        raw_deployments = yaml.load(dp)
    hosts = raw_deployments['deployments']

    # TODO: warn the user if there are uncommitted changes in the repo

    for host in hosts:
        retcode = deploy_to(args.compstate, host, args.revision, args.verbose)
        if retcode != 0:
            # TODO: work out if it makes sense to try to rollback here?
            print_fail("Failed to deploy to '{0}' (exit status: {1}).".format(host, retcode))
            exit(retcode)

def add_subparser(subparsers):
    parser = subparsers.add_parser('deploy',
                                   help='Deploy a given competition state to all known hosts')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('compstate', help='competition state repository')
    parser.add_argument('revision', nargs='?', default='HEAD',
                        help='revision to deploy (defaults to HEAD)')
    parser.set_defaults(func=command)
