"""Path-independent persistence helper for data and reports."""

from pathlib import Path

# Project Root is 4 levels up: src/smart_clinic/core/persistence.py -> src -> REPO_ROOT
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = REPO_ROOT / "data"


def get_data_path(filename: str = "clinic_data.json") -> Path:
    """Return the absolute path to a data file, checking data/ then repo root."""
    target = DATA_DIR / filename
    if target.exists():
        return target
    root_target = REPO_ROOT / filename
    if root_target.exists():
        return root_target
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return target


def get_report_path(filename: str = "daily_report.txt") -> Path:
    """Return the absolute path for report outputs."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / filename
