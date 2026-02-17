"""Data loader for HerbCalc static JSON data files.

Loads all JSON data at import time and exposes as module-level variables.
Missing or empty files return sensible defaults (empty dict or list).
"""

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent.parent / "data"


def _load(relative_path: str, default: Any = None) -> Any:
    """Load a JSON file relative to DATA_DIR with graceful fallback.

    Args:
        relative_path: Path relative to the data directory.
        default: Value to return if file is missing or empty.
                 If None, returns {} for objects, [] for arrays.

    Returns:
        Parsed JSON data, or default value on failure.
    """
    path = DATA_DIR / relative_path
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            if data is None:
                return default if default is not None else {}
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        if default is not None:
            return default
        return {}


# Unit data
METRIC = _load("units/metric.json", default=[])
AVOIRDUPOIS = _load("units/avoirdupois.json")
APOTHECARY = _load("units/apothecary.json")
HOUSEHOLD = _load("units/household.json", default=[])
HISTORICAL = _load("units/historical.json")
PHARMACY_ABBREV = _load("units/pharmacy_abbrev.json")

# Solvent data
SOLVENTS = _load("solvents/solvents.json")
AFFINITY_MATRIX = _load("solvents/affinity_matrix.json")

# Herb data
MONOGRAPHS = _load("herbs/monographs.json", default=[])
INTERACTIONS = _load("herbs/interactions.json", default=[])

# Formulation data
PREPARATION_TYPES = _load("formulation/preparation_types.json", default=[])
EXCIPIENTS = _load("formulation/excipients.json", default=[])

# Pedagogy
GLOSSARY = _load("pedagogy/glossary.json", default=[])
