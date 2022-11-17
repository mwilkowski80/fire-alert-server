from argparse import ArgumentParser


def create_args_from_argparse():
    parser = ArgumentParser()
    parser.add_argument('--udp-bind-address', required=True)
    parser.add_argument('--udp-bind-port', required=True, type=int)
    parser.add_argument('--http-bind-address', required=True)
    parser.add_argument('--http-bind-port', required=True, type=int)
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()
