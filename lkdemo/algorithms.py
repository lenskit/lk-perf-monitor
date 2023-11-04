"""
This module defines the algorithms, and their default configurations, that
we are going to use.
"""

from lenskit.algorithms import item_knn, user_knn, als
from lenskit.algorithms import basic

Bias = basic.Bias(damping=5)
Pop = basic.Popular()
II = item_knn.ItemItem(20, save_nbrs=2500)
UU = user_knn.UserUser(30)
ALS = als.BiasedMF(50)
IALS = als.ImplicitMF(50)

try:
    from lenskit.algorithms import implicit
    impBPR = implicit.BPR(50, num_threads=1)
except ImportError:
    pass
