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
# # Metric Distributions
#
# This shows the distributiosn of metric values in different data sets.

# %% [markdown]
# ## Setup

# %%
from pathlib import Path

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# %%
from lenskit.topn import RecListAnalysis, ndcg, recip_rank


# %%
def load_recs(data, algo):
    dir = Path('runs') / f'{data}-{algo}'
    return pd.concat([
        pd.read_csv(f) for f in dir.glob('recs-*.csv.gz')
    ], ignore_index=True)


# %% [markdown]
# ## ML-20M analysis

# %% [markdown]
# Load the test data:

# %%
ml20m = Path('data-split/ml20m')
ml20m_test = pd.concat([
    pd.read_csv(f) for f in ml20m.glob('test-*.csv.gz')
], ignore_index=True)
ml20m_test.head()

# %% [markdown]
# And some recommendations:

# %%
ml20m_ii_recs = load_recs('ml20m', 'II')

# %% [markdown]
# And let's compute metrics:

# %%
rla = RecListAnalysis()
rla.add_metric(recip_rank)
rla.add_metric(ndcg)
ml20m_ii_users = rla.compute(ml20m_ii_recs, ml20m_test, include_missing=True)
ml20m_ii_users.head()

# %% [markdown]
# And let's look at these distributions:

# %%
ml20m_ii_users.describe()

# %%
sns.displot(data=ml20m_ii_users, x='ndcg')
plt.show()

# %%
