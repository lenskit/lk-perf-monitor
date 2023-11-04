import sys
from os import fspath
from pathlib import Path
import json

from ruamel.yaml import YAML

from _jsonnet import evaluate_file
from invoke import task

ENV_BASE = Path('envs')


def _msg(fmt, *args):
    print(fmt.format(*args), file=sys.stderr)


@task
def update_pipeline(c):
    """
    Update the DVC pipeline.

    The pipeline is miantained in jsonnet files for consistency and to reduce
    repetitive code.  This task re-renders them.
    """
    yaml = YAML()
    runs = Path('runs')
    pipes = runs.glob('*/dvc.jsonnet')
    for file in pipes:
        print('processing', file, file=sys.stderr)
        config = evaluate_file(fspath(file))
        config = json.loads(config)
        yf = file.with_suffix('.yaml')
        with yf.open('w', encoding='utf8') as f:
            yaml.dump(config, f)


@task
def create_env(c, version=None, replace=False):
    """
    Create the environment for a LensKit version.
    """

    if version is not None:
        versions = [version]
    else:
        versions = [ef.stem[3:] for ef in ENV_BASE.glob('lk-*.yml')]

    for ver in versions:
        env_file = ENV_BASE / f'lk-{ver}.yml'
        env_dir = ENV_BASE / f'lk-{ver}-env'

        _msg('creating LensKit environment for {}', ver)
        _msg('environment file: {}', env_file)
        if replace:
            c.run(f'mamba env create --force -p {fspath(env_dir)} -f {fspath(env_file)}', echo=True)
        else:
            c.run(f'mamba env update -p {fspath(env_dir)} -f {fspath(env_file)}', echo=True)
