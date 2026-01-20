"""
Simple logging configuration module.
"""

import logging


def get_logger(name):
    """
    Create and return a named logger.

    Args:
        name: Logger name (usually module name)

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
