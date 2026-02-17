"""Multi-herb formulation logic for HerbCalc.

Provides formula building, parts scaling, and dry-extract
bidirectional conversion calculations.
"""

from dataclasses import dataclass, field
from typing import Optional

from core.data_loader import MONOGRAPHS


@dataclass
class HerbEntry:
    """A single herb in a multi-herb formula."""
    name: str
    parts: float
    ratio: float = 5.0  # e.g., 5 for 1:5
    alcohol_pct: float = 45.0
    notes: Optional[str] = None


@dataclass
class ScaledEntry:
    """A herb entry scaled to absolute weights."""
    name: str
    parts: float
    weight_g: float
    menstruum_ml: float
    ratio: float
    alcohol_pct: float


@dataclass
class FormulaResult:
    """Result of a multi-herb formula calculation."""
    herbs: list[ScaledEntry]
    total_herb_weight_g: float
    total_menstruum_ml: float
    compromise_alcohol_pct: float
    per_herb_details: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _lookup_monograph(herb_name: str) -> Optional[dict]:
    """Look up a herb in the monographs data."""
    if not isinstance(MONOGRAPHS, list):
        return None
    for m in MONOGRAPHS:
        if (m.get("common_name", "").lower() == herb_name.lower()
                or m.get("latin_name", "").lower() == herb_name.lower()):
            return m
    return None


def build_formula(
    herbs: list[HerbEntry],
    target_volume_ml: Optional[float] = None,
    bottle_size_ml: Optional[float] = None,
) -> FormulaResult:
    """Multi-herb formula calculation.

    Each HerbEntry has name, parts, ratio, and alcohol_pct.
    Calculates per-herb weights and a compromise solvent composition
    weighted by the proportion of each herb in the formula.

    Args:
        herbs: List of HerbEntry objects defining the formula.
        target_volume_ml: If provided, scale formula to this total volume.
        bottle_size_ml: If provided, scale to fill this bottle size.

    Returns:
        FormulaResult with per-herb weights and compromise menstruum.
    """
    if not herbs:
        return FormulaResult(
            herbs=[],
            total_herb_weight_g=0.0,
            total_menstruum_ml=0.0,
            compromise_alcohol_pct=0.0,
            warnings=["No herbs in formula."],
        )

    warnings: list[str] = []
    total_parts = sum(h.parts for h in herbs)

    if total_parts <= 0:
        return FormulaResult(
            herbs=[],
            total_herb_weight_g=0.0,
            total_menstruum_ml=0.0,
            compromise_alcohol_pct=0.0,
            warnings=["Total parts must be greater than zero."],
        )

    # Determine target volume for scaling
    effective_volume = target_volume_ml or bottle_size_ml or 100.0

    # Calculate compromise alcohol % weighted by parts
    compromise_alcohol = sum(
        h.alcohol_pct * (h.parts / total_parts) for h in herbs
    )

    # Scale each herb
    scaled_herbs = []
    total_herb_weight = 0.0
    total_menstruum = 0.0

    for herb in herbs:
        proportion = herb.parts / total_parts
        herb_menstruum_ml = effective_volume * proportion
        herb_weight_g = herb_menstruum_ml / herb.ratio

        scaled = ScaledEntry(
            name=herb.name,
            parts=herb.parts,
            weight_g=herb_weight_g,
            menstruum_ml=herb_menstruum_ml,
            ratio=herb.ratio,
            alcohol_pct=herb.alcohol_pct,
        )
        scaled_herbs.append(scaled)
        total_herb_weight += herb_weight_g
        total_menstruum += herb_menstruum_ml

    return FormulaResult(
        herbs=scaled_herbs,
        total_herb_weight_g=total_herb_weight,
        total_menstruum_ml=total_menstruum,
        compromise_alcohol_pct=compromise_alcohol,
        warnings=warnings,
    )


def scale_parts(
    parts: list[tuple[str, float]],
    target_total_g: float,
) -> list[tuple[str, float]]:
    """Convert parts notation to absolute weights.

    Args:
        parts: List of (name, parts) tuples.
        target_total_g: Desired total weight in grams.

    Returns:
        List of (name, weight_g) tuples scaled to target total.
    """
    total_parts = sum(p for _, p in parts)
    if total_parts <= 0:
        return [(name, 0.0) for name, _ in parts]

    return [
        (name, (p / total_parts) * target_total_g)
        for name, p in parts
    ]


def dry_equivalent(tincture_ml: float, ratio: float) -> float:
    """Convert tincture volume to equivalent dried herb weight.

    A 1:5 tincture means 1g herb per 5mL menstruum.
    So tincture_ml / ratio = grams of dried herb equivalent.

    Args:
        tincture_ml: Volume of tincture in mL.
        ratio: Extraction ratio (e.g., 5 for 1:5).

    Returns:
        Equivalent dried herb weight in grams.
    """
    if ratio <= 0:
        raise ValueError(
            "Extraction ratio must be positive. "
            "A ratio of 5 means 1:5 (1g herb to 5mL menstruum)."
        )
    return tincture_ml / ratio


def tincture_from_dose(target_herb_mg: float, ratio: float) -> float:
    """Calculate tincture volume needed for a target dried herb dose.

    Args:
        target_herb_mg: Desired dose of dried herb equivalent in mg.
        ratio: Extraction ratio (e.g., 5 for 1:5).

    Returns:
        Required tincture volume in mL.
    """
    if ratio <= 0:
        raise ValueError(
            "Extraction ratio must be positive. "
            "A ratio of 5 means 1:5 (1g herb to 5mL menstruum)."
        )
    target_herb_g = target_herb_mg / 1000.0
    return target_herb_g * ratio
