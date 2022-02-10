"""
Operate on environments for LensKit projects.

Usage:
    envtool.py --create [VERSION]
    envtool.py --run VER SCRIPT ARGS...
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
    sp.check_call(['conda', 'env', 'update', '-p', fspath(env_dir), '-f', fspath(env_file)])


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


def cmd_run(args):
    script = args['SCRIPT']
    script_args = args['ARGS']
    ver = args['VER']
    env_dir = ENV_BASE / f'lk-{ver}-env'

    sp.check_call(['conda', 'run', '-p', fspath(env_dir), '--no-capture-output', 'python', script] + script_args)


def main(args):
    if args['--create']:
        cmd_create(args)
    if args['--run']:
        cmd_run(args)


if __name__ == '__main__':
    args = docopt(__doc__, options_first=True)
    _log = log.script(__file__)
    main(args)
