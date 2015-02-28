from __future__ import print_function

import ruamel.yaml as ryaml

from sr.comp.yaml_loader import add_time_constructor

add_time_constructor(ryaml.RoundTripLoader)

def load(yaml_file):
    with open(yaml_file, 'r') as yf:
        return ryaml.load(yf, ryaml.RoundTripLoader)

def dump(yaml_file, data):
    yaml = ryaml.dump(data, Dumper=ryaml.RoundTripDumper)
    yaml = "\n".join(l.rstrip() for l in yaml.splitlines())
    with open(yaml_file, 'w') as yf:
        print(yaml, file=yf)

def command(settings):
    fp = settings.file_path
    dump(fp, load(fp))

def add_subparser(subparsers):
    parser = subparsers.add_parser('round-trip',
                                   help='Round-trip a yaml file using compstate loading')
    parser.add_argument('file_path', help='target file to round trip')
    parser.set_defaults(func=command)
