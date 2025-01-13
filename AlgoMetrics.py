# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
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
from pathlib import Path
from packaging.version import parse as parse_version
import json

# %%
import pandas as pd
import seaborn as sns

# %% [markdown]
# **Note:** LensKit 0.14 and earlier defaulted to using rating values to compute
# gain for nDCG. This is the primary cause of the overall shifts in NDCG in
# LensKit 2025.1 and later.

# %% [markdown]
# ## Load DVC metrics
#
# Let's load all the DVC metrics:

# %%
run_dir = Path('runs')

# %%
metrics = {}
for file in run_dir.glob('*/metrics.csv'):
    ver = file.parent.name
    metrics[ver] = pd.read_csv(file)
list(metrics.keys())

# %%
versions = [k for k in metrics.keys() if k != 'main']
versions.sort(key=parse_version)
versions.append('main')
versions

# %% [markdown]
# Now let's collect all these metrics into a frame:

# %%
mdf = pd.concat(metrics, names=['version'])
# pull version out of index
mdf.reset_index('version', inplace=True)
# drop remaining index
mdf.reset_index(drop=True, inplace=True)
# set up category and ordering
mdf = mdf.astype({'version': 'category'})
mdf['version'] = mdf['version'].cat.reorder_categories(versions)
mdf

# %% [markdown]
# And get data sets & algorithms from run keys:

# %%
mdf['data'] = mdf['run'].str.replace(r'^(\w+)-.*', r'\1', regex=True)
mdf['algo'] = mdf['run'].str.replace(r'^\w+-(.*)', r'\1', regex=True)
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
# ## Implicit BPR Results
#
# We also test BPR implementation from Implicit.

# %%
als = mdf[mdf['algo'] == 'impBPR']
sns.lineplot(x='version', y='nDCG', hue='data', data=als)

# %% [markdown]
# ## Combined Algorithm Results
#
# Let's look at all the algorithms together as a point plot:

# %%
sns.catplot(x='version', y='nDCG', hue='data', col='algo', data=mdf, kind='point')
