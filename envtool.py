"""
Operate on environments for LensKit projects.

Usage:
    envtool.py --create [VERSION]
"""

from os import fspath
from pathlib import Path
import subprocess as sp
from docopt import docopt

from lkdemo import log

ENV_BASE = Path('envs')


def update_env(ver):
    env_file = ENV_BASE / f'lk-{ver}.yml'
    env_dir = ENV_BASE / f'lk-{ver}-env'

    _log.info('creating LensKit environment for %s', ver)
    _log.info('environment file: %s', env_file)
    sp.check_call(['mamba', 'env', 'update', '-p', fspath(env_dir), '-f', fspath(env_file)])


def cmd_create(args):
    "Create an environment"
    version = args.get('VERSION')
    if version:
        update_env(version)
    else:
        _log.info('scanning all versions')
        for ef in ENV_BASE.glob('lk-*.yml'):
            ver = ef.stem[3:]
            update_env(ver)


def main(args):
    if args['--create']:
        cmd_create(args)


if __name__ == '__main__':
    args = docopt(__doc__)
    _log = log.script(__file__)
    main(args)
