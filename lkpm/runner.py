import json
import logging
import re
from pathlib import Path

import numpy as np
import pandas as pd

from lenskit import batch, util
from lenskit.data import ItemListCollection
from lenskit.metrics import NDCG, RMSE, RunAnalysis
from lenskit.pipeline import topn_pipeline
from lenskit.splitting import TTSplit
from lkpm import datasets, models

_fn_suffix = re.compile(r"\..*$")
_log = logging.getLogger(__name__)


def run_algo(args):
    input = args.get("--splits")
    output = args.get("-o")
    n_recs = int(args.get("-n"))
    model = args.get("ALGO")

    algo = getattr(models, model)
    pipe = topn_pipeline(algo, predicts_ratings=not args["--no-predict"])

    path = Path(input)
    dest = Path(output)
    dest.mkdir(exist_ok=True, parents=True)

    ds_def = getattr(datasets, path.name)

    metric_file = args.get("-M")

    all_topnm = []
    all_test = ItemListCollection(["user_id"])
    all_preds = ItemListCollection(["user_id"])
    all_times = []

    for file in path.glob("test-*"):
        _log.info("loading %s", file)
        test = pd.read_csv(file, sep=",").rename(
            {
                "user": "user_id",
                "item": "item_id",
            }
        )
        suffix = file.name[5:]
        out_sfx = _fn_suffix.sub(".parquet", suffix)
        timer = util.Stopwatch()

        data = ds_def()
        test = ItemListCollection.from_df(test, ["user_id"])
        all_test.add_from(test)
        pair = TTSplit.from_src_and_test(data, test)

        _log.info("[%s] Fitting the model", timer)
        tr_time = util.Stopwatch()
        fittable = pipe.clone()
        fittable.train(pair.train)
        all_times.append(tr_time.elapsed())

        users = list(test.keys())
        _log.info("[%s] generating recommendations for %d unique users", timer, len(users))
        recs = batch.recommend(model, users, n_recs)
        recf = dest / f"recs-{out_sfx}"
        _log.info("[%s] writing recommendations to %s", timer, recf)
        recs.save_parquet(recf)

        if metric_file:
            rla = RunAnalysis()
            rla.add_metric(NDCG())
            res = rla.compute(recs, test)
            all_topnm.append(res.list_metrics()["NDCG"])

        if not args["--no-predict"]:
            _log.info("[%s] generating predictions for user-item", timer)
            preds = batch.predict(model, test)
            predf = dest / f"pred-{out_sfx}"
            _log.info("[%s] saving predictions to %s", timer, predf)
            preds.save_parquet(predf)

            if metric_file:
                all_preds.add_from(preds)

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
            ra = RunAnalysis()
            ra.add_metric(RMSE())
            metrics["GRMSE"] = ra.compute(all_preds, all_test).global_metrics()["RMSE"]
            _log.info("Global RMSE: %.3f", metrics["GRMSE"])
        Path(metric_file).write_text(json.dumps(metrics))
