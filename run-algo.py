# -*- coding: utf-8 -*-
"""
Run an algorithm to produce predictions and recommendations.

Usage:
    run-algo.py [options] ALGO 

Options:  
    --splits input  directory for split train-test pairs [default: data-split]
    -o output       destination directory [default: output]
    -n N            number of recommendations for a unique user [default: 100]
    -m MODULE       import algorithms from MODULE [default: lkdemo.algorithms]
    -M FILE         write metrics to FILE
    --no-predict    turn off rating prediction
    --log-file FILE write logs to FILE
    ALGO            name of algorithm to load 
"""

import os
import multiprocessing
from docopt import docopt
from pathlib import Path
from lenskit.algorithms import Recommender, Predictor
from lenskit.topn import RecListAnalysis, ndcg
from lenskit.metrics.predict import rmse
from lenskit import batch, util
from lkdemo import log, datasets

import json
import importlib
import pandas as pd
import numpy as np

def main(args):
    mod_name = args.get('-m')
    input = args.get('--splits')
    output = args.get('-o')
    n_recs = int(args.get('-n'))
    model = args.get('ALGO')

    _log.info(f'importing from module {mod_name}')
    algorithms = importlib.import_module(mod_name)

    algo = getattr(algorithms, model)
    algo = Recommender.adapt(algo)

    path = Path(input)
    dest = Path(output)
    dest.mkdir(exist_ok=True , parents=True)

    ds_def = getattr(datasets, path.name, None)

    metric_file = args.get('-M')

    all_topnm = []
    all_preds = []
    all_times = []

    for file in path.glob("test-*"):
        _log.info('loading %s', file)
        test = pd.read_csv(file, sep=',')
        suffix = file.name[5:]
        train_file = path / f'train-{suffix}'
        timer = util.Stopwatch()
        
        if 'index' in test.columns:
            _log.info('setting test index')
            test = test.set_index('index')
        else:
            _log.warn('no index column found in %s', file.name)

        if train_file.exists():
            _log.info('[%s] loading training data from %s', timer, train_file)
            train = pd.read_csv(path / f'train-{suffix}', sep=',')
        elif ds_def is not None:
            _log.info('[%s] extracting training data from data set %s', timer, path.name)
            train = datasets.ds_diff(ds_def.ratings, test)
            train.reset_index(drop=True, inplace=True)
        else:
            _log.error('could not find training data for %s', file.name)
            continue

        _log.info('[%s] Fitting the model', timer)
        tr_time = util.Stopwatch()
        fittable = util.clone(algo)
        model = fittable.fit(train)
        all_times.append(tr_time.elapsed())
        try:
            users = test['user'].unique()
            _log.info('[%s] generating recommendations for %d unique users', timer, len(users))
            recs = batch.recommend(model, users, n_recs)
            _log.info('[%s] writing recommendations to %s', timer, dest)
            recs.to_csv(dest / f'recs-{suffix}', index=False)

            if metric_file:
                rla = RecListAnalysis()
                rla.add_metric(ndcg)
                um = rla.compute(recs, test, include_missing=True)
                all_topnm.append(um)
            
            if isinstance(algo, Predictor) and not args['--no-predict']:
                _log.info('[%s] generating predictions for user-item', timer)
                preds = batch.predict(model, test)
                preds.to_csv(dest / f'pred-{suffix}', index=False)

                if metric_file:
                    all_preds.append(preds)
        finally:
            if hasattr(model, 'close'):
                model.close()

    if metric_file:
        _log.info('computing metrics')
        topn_m = pd.concat(all_topnm, ignore_index=True)
        metrics = {
            'nDCG': topn_m['ndcg'].mean(),
            'TrainTime': np.median(all_times),
            'train_times': all_times,
        }
        _log.info('nDCG: %.3f', metrics['nDCG'])
        if all_preds:
            preds = pd.concat(all_preds, ignore_index=True)
            metrics['GRMSE'] = rmse(preds['prediction'], preds['rating'])
            _log.info('Global RMSE: %.3f', metrics['GRMSE'])
        Path(metric_file).write_text(json.dumps(metrics))


if __name__ == '__main__':
    args = docopt(__doc__)
    _log = log.script(__file__, log_file=args['--log-file'])
    main(args)
