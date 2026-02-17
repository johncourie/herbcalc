"""Solvent system calculations for HerbCalc.

Provides menstruum calculation, Pearson's square alcohol dilution,
ethanol density lookup with interpolation, and percentage convention
conversion (w/w, w/v, v/v).
"""

from dataclasses import dataclass, field
from typing import Optional

from core.data_loader import SOLVENTS


@dataclass
class MenstruumResult:
    """Result of a menstruum calculation."""
    total_volume_ml: float
    ethanol_ml: float
    water_ml: float
    glycerin_ml: float
    herb_weight_g: float
    ratio: float
    target_alcohol_pct: float
    ethanol_source_pct: float
    glycerin_pct: float
    solvent_mode: str
    warnings: list[str] = field(default_factory=list)

    @property
    def ethanol_source_ml(self) -> float:
        """Volume of source alcohol (e.g., Everclear) needed."""
        if self.ethanol_source_pct <= 0:
            return 0.0
        return self.ethanol_ml / (self.ethanol_source_pct / 100.0)

    @property
    def added_water_ml(self) -> float:
        """Water to add (total water minus water already in ethanol source)."""
        water_in_source = self.ethanol_source_ml - self.ethanol_ml
        return max(0.0, self.water_ml - water_in_source)


@dataclass
class DilutionResult:
    """Result of a Pearson's square dilution calculation."""
    total_volume_ml: float
    source_volume_ml: float
    diluent_volume_ml: float
    source_concentration: float
    target_concentration: float
    warnings: list[str] = field(default_factory=list)


def _get_density_table() -> list[dict]:
    """Get the ethanol-water density table from loaded data."""
    if isinstance(SOLVENTS, dict):
        return SOLVENTS.get("ethanol_water_density_table", [])
    return []


def lookup_ethanol_density(ethanol_pct_vv: float) -> float:
    """Interpolate ethanol-water mixture density from density table.

    Args:
        ethanol_pct_vv: Ethanol percentage by volume (0-100).

    Returns:
        Density in g/mL at 20C.

    Raises:
        ValueError: If percentage is out of range.
    """
    if ethanol_pct_vv < 0 or ethanol_pct_vv > 100:
        raise ValueError(
            f"Ethanol percentage must be 0-100, got {ethanol_pct_vv}."
        )

    table = _get_density_table()
    if not table:
        # Fallback: linear interpolation between water (1.0) and ethanol (0.789)
        return 1.0 - (ethanol_pct_vv / 100.0) * (1.0 - 0.7893)

    # Find bracketing entries
    lower = None
    upper = None
    for entry in table:
        pct = entry["ethanol_pct_vv"]
        if pct == ethanol_pct_vv:
            return entry["density_g_ml"]
        if pct < ethanol_pct_vv:
            if lower is None or pct > lower["ethanol_pct_vv"]:
                lower = entry
        if pct > ethanol_pct_vv:
            if upper is None or pct < upper["ethanol_pct_vv"]:
                upper = entry

    if lower is None and upper is not None:
        return upper["density_g_ml"]
    if upper is None and lower is not None:
        return lower["density_g_ml"]
    if lower is None and upper is None:
        return 1.0

    # Linear interpolation
    fraction = ((ethanol_pct_vv - lower["ethanol_pct_vv"])
                / (upper["ethanol_pct_vv"] - lower["ethanol_pct_vv"]))
    return (lower["density_g_ml"]
            + fraction * (upper["density_g_ml"] - lower["density_g_ml"]))


def density_correct(volume_ml: float, substance: str) -> float:
    """Convert volume to weight using substance density.

    Args:
        volume_ml: Volume in milliliters.
        substance: Substance identifier (e.g., "ethanol", "glycerin", "water").

    Returns:
        Weight in grams.
    """
    densities = {
        "water": 1.0,
        "ethanol": 0.789,
        "glycerin": 1.261,
        "acetic_acid": 1.049,
        "honey": 1.42,
        "olive_oil": 0.913,
    }

    # Try loaded solvent data first
    if isinstance(SOLVENTS, dict):
        for solvent in SOLVENTS.get("solvents", []):
            if solvent.get("id") == substance:
                return volume_ml * solvent.get("density_g_ml", 1.0)

    density = densities.get(substance, 1.0)
    return volume_ml * density


def calculate_menstruum(
    herb_weight_g: float,
    ratio: float,
    ethanol_source_pct: float,
    target_alcohol_pct: float,
    glycerin_pct: float = 0.0,
    solvent_mode: str = "hydroethanolic",
) -> MenstruumResult:
    """Core menstruum calculation.

    Calculates the volumes of each solvent component needed for an
    herbal extraction based on herb weight, extraction ratio, ethanol
    source concentration, target alcohol percentage, and optional
    glycerin percentage.

    The algorithm (proven over 7 years in the original herbcalc.php):
    1. Total menstruum volume = herb_weight * ratio
    2. Glycerin volume = total * (glycerin_pct / 100)
    3. Ethanol volume (pure) = total * (target_alcohol_pct / 100)
    4. Water volume = total - glycerin - ethanol

    Args:
        herb_weight_g: Weight of herb material in grams.
        ratio: Extraction ratio (e.g., 5 for 1:5).
        ethanol_source_pct: Concentration of ethanol source (e.g., 95 for Everclear).
        target_alcohol_pct: Desired alcohol % in final menstruum.
        glycerin_pct: Desired glycerin % in final menstruum (default 0).
        solvent_mode: Solvent system type.

    Returns:
        MenstruumResult with all volume breakdowns.
    """
    warnings: list[str] = []

    total_volume = herb_weight_g * ratio

    # Glycerin volume
    glycerin_ml = total_volume * (glycerin_pct / 100.0)

    # Pure ethanol volume needed in the final menstruum
    ethanol_ml = total_volume * (target_alcohol_pct / 100.0)

    # Water is the remainder
    water_ml = total_volume - glycerin_ml - ethanol_ml

    if water_ml < 0:
        warnings.append(
            f"Glycerin ({glycerin_pct}%) + alcohol ({target_alcohol_pct}%) "
            f"exceed 100% of the menstruum. Reduce one or both."
        )
        water_ml = 0.0

    return MenstruumResult(
        total_volume_ml=total_volume,
        ethanol_ml=ethanol_ml,
        water_ml=water_ml,
        glycerin_ml=glycerin_ml,
        herb_weight_g=herb_weight_g,
        ratio=ratio,
        target_alcohol_pct=target_alcohol_pct,
        ethanol_source_pct=ethanol_source_pct,
        glycerin_pct=glycerin_pct,
        solvent_mode=solvent_mode,
        warnings=warnings,
    )


def pearson_square(
    source_concentration: float,
    target_concentration: float,
    total_volume_ml: float,
) -> DilutionResult:
    """Alcohol dilution via Pearson's square method.

    Calculates how much of a source alcohol and how much water (0%)
    to combine to achieve a target concentration at a desired total volume.

    The Pearson's square:
        source_conc
                        target_conc - 0 = target_conc (parts source)
        target_conc
                        source_conc - target_conc (parts diluent)
        0 (diluent)

    Args:
        source_concentration: Alcohol % of source (e.g., 95).
        target_concentration: Desired alcohol % (e.g., 40).
        total_volume_ml: Desired total volume in mL.

    Returns:
        DilutionResult with source and diluent volumes.

    Raises:
        ValueError: If target exceeds source concentration.
    """
    warnings: list[str] = []

    if source_concentration <= 0:
        raise ValueError("Source concentration must be greater than 0%.")

    if target_concentration > source_concentration:
        raise ValueError(
            f"Target concentration ({target_concentration}%) exceeds source "
            f"({source_concentration}%). You cannot concentrate alcohol by "
            f"dilution. Use a higher-proof source or lower your target."
        )

    if target_concentration < 0:
        raise ValueError("Target concentration cannot be negative.")

    if target_concentration == 0:
        return DilutionResult(
            total_volume_ml=total_volume_ml,
            source_volume_ml=0.0,
            diluent_volume_ml=total_volume_ml,
            source_concentration=source_concentration,
            target_concentration=0.0,
            warnings=warnings,
        )

    # Pearson's square
    parts_source = target_concentration  # target - 0
    parts_diluent = source_concentration - target_concentration
    total_parts = parts_source + parts_diluent

    source_volume = total_volume_ml * (parts_source / total_parts)
    diluent_volume = total_volume_ml * (parts_diluent / total_parts)

    return DilutionResult(
        total_volume_ml=total_volume_ml,
        source_volume_ml=source_volume,
        diluent_volume_ml=diluent_volume,
        source_concentration=source_concentration,
        target_concentration=target_concentration,
        warnings=warnings,
    )


def convert_percentage(
    value: float,
    from_convention: str,
    to_convention: str,
    substance: str = "ethanol",
    ethanol_pct_vv: Optional[float] = None,
) -> float:
    """Convert between w/w, w/v, and v/v percentage expressions.

    Uses density corrections for the specified substance.

    Conventions:
    - v/v: volume of solute per volume of solution (standard for ethanol)
    - w/v: weight of solute per volume of solution
    - w/w: weight of solute per weight of solution

    Args:
        value: Percentage value to convert.
        from_convention: Source convention ("vv", "wv", "ww").
        to_convention: Target convention ("vv", "wv", "ww").
        substance: Substance for density lookup (default "ethanol").
        ethanol_pct_vv: If substance is ethanol, the v/v % for mixture
                        density lookup. If None, uses value as approximation.

    Returns:
        Converted percentage value.
    """
    if from_convention == to_convention:
        return value

    # Get substance and solution densities
    substance_densities = {
        "ethanol": 0.7893,
        "glycerin": 1.261,
        "water": 1.0,
    }
    substance_density = substance_densities.get(substance, 1.0)

    # For ethanol-water mixtures, get mixture density
    if substance == "ethanol":
        ref_pct = ethanol_pct_vv if ethanol_pct_vv is not None else value
        mixture_density = lookup_ethanol_density(ref_pct)
    else:
        mixture_density = 1.0  # approximate for non-ethanol

    # Convert through v/v as intermediary
    # Step 1: convert from_convention to v/v
    if from_convention == "vv":
        vv_value = value
    elif from_convention == "wv":
        # w/v = (substance_density * v/v)
        # v/v = w/v / substance_density
        vv_value = value / substance_density
    elif from_convention == "ww":
        # w/w = (substance_density * v/v) / (mixture_density * 100) * 100
        # Simplified: w/w = (substance_density * v/v) / mixture_density
        # v/v = w/w * mixture_density / substance_density
        vv_value = value * mixture_density / substance_density
    else:
        raise ValueError(f"Unknown convention: {from_convention}. Use 'vv', 'wv', or 'ww'.")

    # Step 2: convert v/v to target
    if to_convention == "vv":
        return vv_value
    elif to_convention == "wv":
        return vv_value * substance_density
    elif to_convention == "ww":
        return vv_value * substance_density / mixture_density
    else:
        raise ValueError(f"Unknown convention: {to_convention}. Use 'vv', 'wv', or 'ww'.")
