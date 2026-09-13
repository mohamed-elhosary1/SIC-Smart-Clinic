"""Smart Clinic Web Package

Reflex web interface integration for Smart Clinic.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
from .state import State
from . import styles

__all__ = ["State", "styles"]
