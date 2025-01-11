from lenskit.als import BiasedMFScorer, ImplicitMFScorer
from lenskit.knn import ItemKNNScorer, UserKNNScorer

II = ItemKNNScorer(k=20, save_nbrs=2500)
UU = UserKNNScorer(k=30)
ALS = BiasedMFScorer(features=50)
IALS = ImplicitMFScorer(features=50)

try:
    from lenskit.implicit import BPR

    impBPR = BPR(factors=50)
except ImportError:
    pass
