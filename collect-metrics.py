#!/usr/bin/env python3
"""
Collect metrics from a LensKit project.

Usage:
    collect-metrics.py -o OUT DIR
"""

import json
import re
from pathlib import Path

import pandas as pd
from docopt import docopt

from lkpm import log

_run_re = re.compile(r"^(\w+)-(.*)$")


def main(args):
    out_file = Path(args["OUT"])
    dir = Path(args["DIR"])

    metrics = []
    for jsf in dir.glob("*.json"):
        _log.info("reading %s", jsf)

        with jsf.open("r") as f:
            obj = json.load(f)
            obj["run"] = jsf.stem
            metrics.append(obj)

    df = pd.DataFrame.from_records(metrics)
    _log.info("writing to %s", out_file)
    df.to_csv(out_file, index=False)


if __name__ == "__main__":
    args = docopt(__doc__)
    _log = log.script(__file__)
    main(args)
