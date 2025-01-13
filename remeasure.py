"""
Remeasure a run.

Usage:
    remeasure.py [-v] [-o FILE] -s FILE RUNDIR

Options:
    -v, --verbose
        Enable verobse logging output
    -s FILE, --splits=FILE
        directory containing split train-test pairs [default: data-split]
    -o FILE, --output=FILE
        write metrics to FILE
    RUNDIR
        directory containing recommendation outputs
"""

from os import fspath
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
from docopt import docopt

from lenskit.data import ItemListCollection
from lenskit.logging import LoggingConfig, get_logger
from lenskit.metrics import NDCG, RBP, RecipRank, RunAnalysis

_log = get_logger("lkpm.remeasure")


def main(opts):
    lc = LoggingConfig()
    if opts["--verbose"]:
        lc.set_verbose(True)
    lc.apply()

    splits = Path(opts["--splits"])
    runs = Path(opts["RUNDIR"])

    _log.info("reading test data", dir=splits)
    test = ItemListCollection(["user_id"])
    for f in splits.glob("*.csv.gz"):
        df = pd.read_csv(f)
        df = df.drop(columns=["index"], errors="ignore")
        df = df.rename(columns={"user": "user_id", "item": "item_id"})
        ilc = ItemListCollection.from_df(df, ["user_id"])
        _log.info("read %d pairs", len(ilc), dir=splits, file=f.name)
        test.add_from(ilc)

    _log.info("reading recommendations")
    recs = ItemListCollection(["user_id"])
    for f in runs.glob("recs*.parquet"):
        schema = pq.read_schema(fspath(f))
        if "items" in schema.names:
            _log.info("reading modern recommendation file", file=f)
            ilc = ItemListCollection.load_parquet(f)
        else:
            _log.info("reading legacy recommendation file", file=f)
            df = pd.read_parquet(f)
            ilc = ItemListCollection.from_df(df, ["user_id"])
        _log.info("read %d recommendation lists", len(ilc), file=f)
        recs.add_from(ilc)

    _log.info("measuring recommendations")
    analyzer = RunAnalysis()
    analyzer.add_metric(NDCG)
    analyzer.add_metric(RBP)
    analyzer.add_metric(RecipRank)
    analyzer.add_metric(NDCG(gain="rating"), "RateNDCG")
    result = analyzer.compute(recs, test)
    print(result.list_summary())


if __name__ == "__main__":
    opts = docopt(__doc__ or "")
    main(opts)
