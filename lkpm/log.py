"""
Utilities for configuring and using logging.
"""

import logging
import os
import pathlib
import sys
from importlib.metadata import version

try:
    import lenskit
except ImportError:
    pass

try:
    from sandal.cli import setup_logging
except ImportError:

    def setup_logging(verbose: bool, log_file: str | None):
        ch = logging.StreamHandler(sys.stderr)
        ch.setLevel(logging.DEBUG if verbose else logging.INFO)
        ch.setFormatter(_simple_format)

        root = logging.getLogger()
        root.addHandler(ch)
        root.setLevel(logging.INFO)

        if log_file is not None:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(_simple_format)
            root.addHandler(fh)


_simple_format = logging.Formatter("{levelname} {asctime} {name} {message}", style="{")


def setup(debug=False, log_file=None):
    setup_logging(debug, log_file)
    logging.getLogger("dvc").setLevel(logging.ERROR)
    logging.getLogger("lenskit").setLevel(logging.DEBUG)
    logging.getLogger(__name__).debug("log system configured")


def script(file, **kwargs):
    """
    Initialize logging and get a logger for a script.

    Args:
        file(str): The ``__file__`` of the script being run.
        debug(bool): whether to enable debug logging to the console
    """

    setup(**kwargs)
    name = pathlib.Path(file).stem
    logger = logging.getLogger(name)
    try:
        logger.info("starting script on %s", os.uname().nodename)
    except AttributeError:
        logger.info("starting script")

    logger.info("Python version: %s", sys.version)
    logger.info("LensKit version: %s", version("lenskit"))

    return logger
