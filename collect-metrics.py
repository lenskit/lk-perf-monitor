"""
Collect metrics from a LensKit project.

Usage:
    collect-metrics.py -o OUT DIR
"""

from os import fspath
from pathlib import Path
from docopt import docopt
import json
import pandas as pd

from lkdemo import log


def main(args):
    out_file = Path(args['OUT'])
    dir = Path(args['DIR'])

    metrics = []
    for jsf in dir.glob('*.json'):
        _log.info("reading %s", jsf)
        with jsf.open('r') as f:
            obj = json.load(f)
            metrics.append(obj)

    df = pd.DataFrame.from_records(metrics)
    _log.info('writing to %s', out_file)
    df.to_csv(out_file, index=False)


if __name__ == '__main__':
    args = docopt(__doc__)
    _log = log.script(__file__)
    main(args)