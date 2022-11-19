from argparse import ArgumentParser
from typing import Iterable


def create_args_from_argparse(service_list: Iterable[str]):
    parser = ArgumentParser()
    parser.add_argument('--udp-bind-address', required=True)
    parser.add_argument('--udp-bind-port', required=True, type=int)
    parser.add_argument('--http-bind-address', required=True)
    parser.add_argument('--http-bind-port', required=True, type=int)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--services', required=True, help="""
    Comma-separated list of services to load. Available options: %s""" % ','.join(service_list))
    return parser.parse_args()
