"""
Utilities for configuring and using logging.
"""

import logging
import os
import pathlib
import sys

try:
    from importlib.metadata import version
except ImportError:
    try:
        from importlib_metadata import version
    except ImportError:
        version = None

try:
    from lenskit.logging import LoggingConfig

    def setup_logging(verbose: bool, log_file):
        lc = LoggingConfig()
        if verbose:
            lc.set_verbose(True)
        if log_file:
            lc.set_log_file(log_file)
        lc.apply()

except ImportError:

    def setup_logging(verbose: bool, log_file):
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
    if version is None:
        logger.warn("cannog find LensKit version")
    else:
        logger.info("LensKit version: %s", version("lenskit"))

    return logger
