"""
Convert a CWL tool and workflow description to its WDL representation
"""

__version__ = "undefined"
try:
    from . import _version
    __version__ = _version.version
except ImportError:
    pass
