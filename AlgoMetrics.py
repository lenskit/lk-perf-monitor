# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.12.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Algorithm Metrics
#
# This notebook shows algorithm metrics over the release branches.

# %%
import re
import subprocess
from packaging.version import parse as parse_version
import json

# %%
import pandas as pd
import seaborn as sns

# %% [markdown]
# ## Load DVC metrics
#
# Let's load all the DVC metrics:

# %%
proc = subprocess.run(['dvc', 'metrics', 'show', '-a', '--show-json'], stdout=subprocess.PIPE, text=True)
metrics = json.loads(proc.stdout)
list(metrics.keys())

# %%
versions = [v.replace(r'versions/', '') for v in metrics.keys() if v != 'main']
versions.sort(key=parse_version)
versions.append('main')
versions

# %% [markdown]
# Now let's define a function that can traverses the metric structure and yields individual rows for a table:

# %%
_mfn_re = re.compile(r'^runs/(\w+)-(.*)\.json$')
def metric_rows(metrics):
    for v, data in metrics.items():
        v = v.replace('versions/', '')
        for fn, vals in data['data'].items():
            fn = fn.replace('\\', '/')
            m = _mfn_re.match(fn)
            if m:
                data = m.group(1)
                algo = m.group(2)
                row = {
                    'version': v,
                    'algo': algo,
                    'data': data,
                }
                row.update(vals['data'])
                yield row


# %% [markdown]
# And compute a full data frame:

# %%
mdf = pd.DataFrame.from_records(metric_rows(metrics))
mdf = mdf.astype({'version': 'category'})
mdf['version'] = mdf['version'].cat.reorder_categories(versions)
mdf

# %% [markdown]
# ## ALS Results
#
# Let's first look at biased MF from ALS:

# %%
als = mdf[mdf['algo'] == 'ALS']
sns.lineplot(x='version', y='GRMSE', hue='data', data=als)

# %%
als = mdf[mdf['algo'] == 'ALS']
sns.lineplot(x='version', y='nDCG', hue='data', data=als)

# %% [markdown]
# ## Item-Item Results
#
# Now the item-item results:

# %%
ii_exp = mdf[mdf['algo'] == 'II']
sns.lineplot(x='version', y='GRMSE', hue='data', data=ii_exp)

# %%
ii_exp = mdf[mdf['algo'] == 'II']
sns.lineplot(x='version', y='nDCG', hue='data', data=ii_exp)

# %% [markdown]
# ## User-User Results
#

# %%
uu_exp = mdf[mdf['algo'] == 'UU']
sns.lineplot(x='version', y='GRMSE', hue='data', data=uu_exp)

# %%
uu_exp = mdf[mdf['algo'] == 'UU']
sns.lineplot(x='version', y='nDCG', hue='data', data=uu_exp)

# %% [markdown]
# ## IALS Results
#
# Let's first look at biased MF from Implicit ALS:

# %%
als = mdf[mdf['algo'] == 'IALS']
sns.lineplot(x='version', y='nDCG', hue='data', data=als)

# %% [markdown]
# ## Combined Algorithm Results
#
# Let's look at all the algorithms together as a bar plot:

# %%
sns.catplot(x='version', y='nDCG', hue='data', col='algo', data=mdf, kind='bar')

# %%
