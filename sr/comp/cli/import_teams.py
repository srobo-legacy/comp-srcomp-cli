import yaml
import os.path

from six.moves.urllib.parse import urljoin
import requests

def format_team(entry):
    if 'team_name' in entry:
        name = entry['team_name']
    else:
        name = entry['college']['name']
    rookie = False  # Temporary
    return {'name': name,
            'rookie': rookie}

def command(settings):
    teams_yaml = os.path.join(settings.compstate, 'teams.yaml')
    target = urljoin(settings.server, 'teams-data.php')
    data = requests.get(target)
    with open(teams_yaml, 'w') as f:
        yaml.dump({'teams': {tla: format_team(team)
                               for tla, team in data.json().items()}},
                  f, default_flow_style=False)

def add_subparser(subparsers):
    parser = subparsers.add_parser('import-teams',
                                   help='import a teams.yaml from an SR server')
    parser.add_argument('compstate', help='competition state repository')
    parser.add_argument('-s', '--server', help='srweb instance',
                        default='https://www.studentrobotics.org/')
    parser.set_defaults(func=command)
