#!/usr/bin/env python3
"""
Operate on environments for LensKit projects.

Usage:
    envtool.py --run VER SCRIPT ARGS...
"""

from os import fspath
from pathlib import Path
import subprocess as sp
from docopt import docopt

from lkdemo import log

ENV_BASE = Path('envs')

def cmd_run(args):
    script = args['SCRIPT']
    script_args = args['ARGS']
    ver = args['VER']
    env_dir = ENV_BASE / f'lk-{ver}-env'

    sp.check_call(['conda', 'run', '-p', fspath(env_dir), '--no-capture-output', 'python', script] + script_args)


def main(args):
    if args['--run']:
        cmd_run(args)


if __name__ == '__main__':
    args = docopt(__doc__, options_first=True)
    _log = log.script(__file__)
    main(args)
