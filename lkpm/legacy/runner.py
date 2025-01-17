import json
import logging
import re
from pathlib import Path

import numpy as np
import pandas as pd

from lenskit import batch, util
from lenskit.algorithms import Predictor, Recommender
from lenskit.algorithms.basic import Bias, Fallback
from lenskit.metrics.predict import rmse
from lenskit.topn import RecListAnalysis, ndcg
from lkpm.legacy import algorithms, datasets

_fn_suffix = re.compile(r"\..*$")
_log = logging.getLogger(__name__)


def run_algo(args):
    input = args.get("--splits")
    output = args.get("-o")
    n_recs = int(args.get("-n"))
    model = args.get("ALGO")

    scorer = getattr(algorithms, model)

    path = Path(input)
    dest = Path(output)
    dest.mkdir(exist_ok=True, parents=True)

    ds_def = getattr(datasets, path.name, None)

    metric_file = args.get("-M")

    all_topnm = []
    all_preds = []
    all_times = []

    for file in path.glob("test-*"):
        _log.info("loading %s", file)
        test = pd.read_csv(file, sep=",")
        suffix = file.name[5:]
        out_sfx = _fn_suffix.sub(".parquet", suffix)
        train_file = path / f"train-{suffix}"
        timer = util.Stopwatch()

        if "index" in test.columns:
            _log.info("setting test index")
            test = test.set_index("index")
        else:
            _log.warn("no index column found in %s", file.name)

        if train_file.exists():
            _log.info("[%s] loading training data from %s", timer, train_file)
            train = pd.read_csv(path / f"train-{suffix}", sep=",")
        elif ds_def is not None:
            _log.info("[%s] extracting training data from data set %s", timer, path.name)
            train = datasets.ds_diff(ds_def.ratings, test)
            train.reset_index(drop=True, inplace=True)
        else:
            _log.error("could not find training data for %s", file.name)
            continue

        _log.info("[%s] Fitting the model", timer)
        tr_time = util.Stopwatch()
        fittable = util.clone(scorer)
        recommender = Recommender.adapt(fittable)
        recommender.fit(train)

        all_times.append(tr_time.elapsed())
        users = test["user"].unique()
        _log.info("[%s] generating recommendations for %d unique users", timer, len(users))
        recs = batch.recommend(recommender, users, n_recs)
        recf = dest / f"recs-{out_sfx}"
        _log.info("[%s] writing recommendations to %s", timer, recf)
        recs.to_parquet(recf, index=False, compression="zstd")

        if metric_file:
            rla = RecListAnalysis()
            rla.add_metric(ndcg)
            um = rla.compute(recs, test, include_missing=True)
            all_topnm.append(um)

        if isinstance(scorer, Predictor) and not args["--no-predict"]:
            _log.debug("training fallback")
            fallback = Bias()
            fallback.fit(train)
            predictor = Fallback(fittable, fallback)
            _log.info("[%s] generating predictions for user-item", timer)
            preds = batch.predict(predictor, test)
            predf = dest / f"pred-{out_sfx}"
            _log.info("[%s] saving predictions to %s", timer, predf)
            preds.to_parquet(predf, index=False, compression="zstd")

            if metric_file:
                all_preds.append(preds)

    if metric_file:
        _log.info("computing metrics")
        topn_m = pd.concat(all_topnm, ignore_index=True)
        metrics = {
            "nDCG": topn_m["ndcg"].mean(),
            "TrainTime": np.median(all_times),
            "train_times": all_times,
        }
        _log.info("nDCG: %.3f", metrics["nDCG"])
        if all_preds:
            preds = pd.concat(all_preds, ignore_index=True)
            metrics["GRMSE"] = rmse(preds["prediction"], preds["rating"])
            _log.info("Global RMSE: %.3f", metrics["GRMSE"])
        Path(metric_file).write_text(json.dumps(metrics))
