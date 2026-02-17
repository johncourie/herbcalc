"""Unit conversion engine for HerbCalc.

Provides cross-system conversion between metric, avoirdupois, apothecary,
household, and historical measurement units. All conversions route through
a base unit intermediary (gram for mass, milliliter for volume).
"""

from dataclasses import dataclass, field
from typing import Optional

from core.data_loader import (
    METRIC, AVOIRDUPOIS, APOTHECARY, HOUSEHOLD, HISTORICAL,
)


@dataclass
class UnitInfo:
    """Metadata for a registered unit."""
    unit_name: str
    symbol: str
    system: str
    unit_type: str  # "mass" or "volume"
    to_base: float
    base_unit: str
    aliases: list[str] = field(default_factory=list)
    precise: bool = True
    variance_note: Optional[str] = None
    disambiguation: Optional[str] = None
    equivalence: Optional[str] = None


@dataclass
class ConversionResult:
    """Result of a unit conversion."""
    value: float
    unit: str
    symbol: str
    system: str
    unit_type: str
    precision: int = 6
    warnings: list[str] = field(default_factory=list)

    @property
    def formatted(self) -> str:
        """Human-readable formatted value."""
        if self.value == 0:
            return f"0 {self.symbol}"
        # Use adaptive precision
        if abs(self.value) >= 100:
            return f"{self.value:,.2f} {self.symbol}"
        elif abs(self.value) >= 1:
            return f"{self.value:,.4f} {self.symbol}"
        else:
            return f"{self.value:.6g} {self.symbol}"


# Module-level unit registry: name/alias -> UnitInfo
_REGISTRY: dict[str, UnitInfo] = {}


def _register_units(units_data: list[dict], source_system: str = None) -> None:
    """Register a list of unit dicts into the flat lookup registry."""
    for entry in units_data:
        info = UnitInfo(
            unit_name=entry["unit_name"],
            symbol=entry.get("symbol", entry["unit_name"]),
            system=entry.get("system", source_system or "unknown"),
            unit_type=entry.get("type", "mass"),
            to_base=entry["to_base"],
            base_unit=entry.get("base_unit", "gram"),
            aliases=entry.get("aliases", []),
            precise=entry.get("precise", True),
            variance_note=entry.get("variance_note"),
            disambiguation=entry.get("disambiguation"),
            equivalence=entry.get("equivalence"),
        )
        # Register by canonical name
        _REGISTRY[info.unit_name.lower()] = info
        # Register by all aliases
        for alias in info.aliases:
            alias_lower = alias.lower()
            if alias_lower not in _REGISTRY:
                _REGISTRY[alias_lower] = info


def _build_registry() -> None:
    """Build the unit registry from all loaded data files."""
    _REGISTRY.clear()

    # Metric units
    if isinstance(METRIC, list):
        _register_units(METRIC, "metric")

    # Avoirdupois units
    if isinstance(AVOIRDUPOIS, dict):
        _register_units(AVOIRDUPOIS.get("units", []), "avoirdupois")
    elif isinstance(AVOIRDUPOIS, list):
        _register_units(AVOIRDUPOIS, "avoirdupois")

    # Apothecary units
    if isinstance(APOTHECARY, dict):
        _register_units(APOTHECARY.get("units", []), "apothecary")
    elif isinstance(APOTHECARY, list):
        _register_units(APOTHECARY, "apothecary")

    # Household units
    if isinstance(HOUSEHOLD, list):
        _register_units(HOUSEHOLD, "household")

    # Historical units
    if isinstance(HISTORICAL, dict):
        _register_units(HISTORICAL.get("units", []), "historical")
    elif isinstance(HISTORICAL, list):
        _register_units(HISTORICAL, "historical")


# Build registry at import time
_build_registry()


def get_unit_info(unit_name: str) -> Optional[UnitInfo]:
    """Return metadata for a unit by name or alias.

    Args:
        unit_name: Unit name, symbol, or alias (case-insensitive).

    Returns:
        UnitInfo if found, None otherwise.
    """
    return _REGISTRY.get(unit_name.lower())


def list_units(unit_type: Optional[str] = None,
               system: Optional[str] = None) -> list[UnitInfo]:
    """List all registered units, optionally filtered by type and/or system.

    Args:
        unit_type: Filter by "mass" or "volume".
        system: Filter by system name (e.g., "metric", "apothecary").

    Returns:
        List of unique UnitInfo objects matching filters.
    """
    seen = set()
    results = []
    for info in _REGISTRY.values():
        if info.unit_name in seen:
            continue
        if unit_type and info.unit_type != unit_type:
            continue
        if system and info.system != system:
            continue
        seen.add(info.unit_name)
        results.append(info)
    return sorted(results, key=lambda u: u.to_base)


def convert(value: float, from_unit: str, to_unit: str) -> ConversionResult:
    """Convert between any two registered units of the same type.

    Conversion path: source unit -> base unit (gram or mL) -> target unit.
    Works across systems (apothecary drams -> metric grams -> household teaspoons).

    Args:
        value: Numeric value to convert.
        from_unit: Source unit name, symbol, or alias.
        to_unit: Target unit name, symbol, or alias.

    Returns:
        ConversionResult with converted value, unit metadata, and warnings.

    Raises:
        ValueError: If units are unknown or incompatible types.
    """
    from_info = get_unit_info(from_unit)
    to_info = get_unit_info(to_unit)

    if from_info is None:
        raise ValueError(
            f"Unknown unit: '{from_unit}'. Check spelling or try an alias. "
            f"Example units: gram, ounce, teaspoon, scruple."
        )
    if to_info is None:
        raise ValueError(
            f"Unknown unit: '{to_unit}'. Check spelling or try an alias. "
            f"Example units: gram, ounce, teaspoon, scruple."
        )
    if from_info.unit_type != to_info.unit_type:
        raise ValueError(
            f"Cannot convert {from_info.unit_type} ({from_unit}) to "
            f"{to_info.unit_type} ({to_unit}). "
            f"You can only convert between units of the same type "
            f"(mass-to-mass or volume-to-volume)."
        )

    # Convert: source -> base -> target
    base_value = value * from_info.to_base
    result_value = base_value / to_info.to_base

    warnings = []
    if not from_info.precise:
        warnings.append(
            f"'{from_info.unit_name}' is an imprecise measure. "
            f"{from_info.variance_note or 'Values are approximate.'}"
        )
    if not to_info.precise:
        warnings.append(
            f"'{to_info.unit_name}' is an imprecise measure. "
            f"{to_info.variance_note or 'Values are approximate.'}"
        )

    return ConversionResult(
        value=result_value,
        unit=to_info.unit_name,
        symbol=to_info.symbol,
        system=to_info.system,
        unit_type=to_info.unit_type,
        warnings=warnings,
    )


def convert_all(value: float, from_unit: str,
                target_system: Optional[str] = None) -> list[ConversionResult]:
    """Convert to all units of the same type, optionally filtered by system.

    Args:
        value: Numeric value to convert.
        from_unit: Source unit name, symbol, or alias.
        target_system: If provided, only return units from this system.

    Returns:
        List of ConversionResult for each matching target unit.

    Raises:
        ValueError: If source unit is unknown.
    """
    from_info = get_unit_info(from_unit)
    if from_info is None:
        raise ValueError(f"Unknown unit: '{from_unit}'.")

    targets = list_units(unit_type=from_info.unit_type, system=target_system)
    results = []
    for target in targets:
        if target.unit_name == from_info.unit_name:
            continue
        result = convert(value, from_unit, target.unit_name)
        results.append(result)
    return results
