import json
import sys
from os import fspath
from pathlib import Path

from _jsonnet import evaluate_file
from invoke import task
from ruamel.yaml import YAML

ENV_BASE = Path("envs")


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
    runs = Path("runs")
    pipes = runs.glob("*/dvc.jsonnet")
    for file in pipes:
        print("processing", file, file=sys.stderr)
        config = evaluate_file(fspath(file))
        config = json.loads(config)
        yf = file.with_suffix(".yaml")
        with yf.open("w", encoding="utf8") as f:
            yaml.dump(config, f)
