"""Smart Clinic Package

A professional multi-interface healthcare triage, appointment scheduling,
and patient queue management system developed for Samsung Innovation Campus (SIC).
"""

__version__ = "2.0.0"

from . import core
from . import cli

__all__ = ["core", "cli", "__version__"]
