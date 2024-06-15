"""
This module defines the algorithms, and their default configurations, that
we are going to use.
"""

try:
    from lenskit.algorithms.knn.item import ItemItem
except ImportError:
    from lenskit.algorithms.item_knn import ItemItem
try:
    from lenskit.algorithms.knn.user import UserUser
except ImportError:
    from lenskit.algorithms.user_knn import UserUser

from lenskit.algorithms import als, basic

Bias = basic.Bias(damping=5)
Pop = basic.Popular()
II = ItemItem(20, save_nbrs=2500)
UU = UserUser(30)
ALS = als.BiasedMF(50)
IALS = als.ImplicitMF(50)

try:
    from lenskit.algorithms import implicit

    impBPR = implicit.BPR(50)
except ImportError:
    pass
