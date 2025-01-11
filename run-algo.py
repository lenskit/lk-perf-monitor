#!/usr/bin/env python3
"""
Run an algorithm to produce predictions and recommendations.

Usage:
    run-algo.py [options] ALGO

Options:
    --splits input  directory for split train-test pairs [default: data-split]
    -o output       destination directory [default: output]
    -n N            number of recommendations for a unique user [default: 100]
    -M FILE         write metrics to FILE
    --no-predict    turn off rating prediction
    --log-file FILE write logs to FILE
    ALGO            name of algorithm to load
"""

from docopt import docopt

from lkpm import log


def main(args):
    try:
        from lkpm import runner
    except ImportError:
        from lkpm.legacy import runner

    runner.run_algo(args)


if __name__ == "__main__":
    args = docopt(__doc__)
    _log = log.script(__file__, log_file=args["--log-file"])
    main(args)
