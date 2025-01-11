"""
This module defines the data sets that we are going to work with.
"""

from lenskit.data import load_movielens


def ml20m():
    return load_movielens("data/ml-20m")


def mlsmall():
    return load_movielens("data/ml-latest-small")


def ml100k():
    return load_movielens("data/ml-100k")


def ml1m():
    return load_movielens("data/ml-1m")


def ml10m():
    return load_movielens("data/ml-10m.zip")


# if hasattr(ds, 'BookCrossing'):
#     bx = ds.BookCrossing('data/bx')
