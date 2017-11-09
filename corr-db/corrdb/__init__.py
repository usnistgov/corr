"""Python module, `corrdb`, for CoRR.
"""
import os
import corrdb.common

def get_version():
    """Get the version of the code from egg_info.

    Returns:
      the package version number
    """
    from pkg_resources import get_distribution, DistributionNotFound

    try:
        version = get_distribution(__name__).version
    except DistributionNotFound:
        version = "unknown, try running `python setup.py egg_info`"

    return version

__version__ = get_version()