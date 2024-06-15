"""
Utilities for configuring and using logging.
"""

import sys
import os
import logging
import pathlib
try:
    import lenskit
except ImportError:
    pass

_simple_format = logging.Formatter('{levelname} {asctime} {name} {message}', style='{')


def setup(debug=False, log_file=None):
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.DEBUG if debug else logging.INFO)
    ch.setFormatter(_simple_format)

    root = logging.getLogger()
    root.addHandler(ch)
    root.setLevel(logging.INFO)

    if log_file is not None:
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(_simple_format)
        root.addHandler(fh)

    logging.getLogger('dvc').setLevel(logging.ERROR)
    logging.getLogger('lenskit').setLevel(logging.DEBUG)
    root.debug('log system configured')


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
        logger.info('starting script on %s', os.uname().nodename)
    except AttributeError:
        logger.info('starting script')

    logger.info("Python version: %s", sys.version)
    try:
        logger.info("LensKit version: %s", lenskit.__version__)
    except NameError:
        logger.warn("LensKit not installed")
    except AttributeError:
        logger.warn("LensKit version unavailable")

    return logger
