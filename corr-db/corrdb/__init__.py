"""Python module, `corrdb`, for CoRR.
"""
import os
import nose
from nose.tools import nottest
import corrdb.common
import corrdb.test

@nottest
def test_all():
    r"""
    Run all the doctests available.
    """
    path = os.path.split(__file__)[0]
    print "Path: %s"%path
    nose.main(argv=['-w', path, '--with-doctest'])


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

__all__ = ['__version__',
           'test']
