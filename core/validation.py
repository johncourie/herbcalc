"""Input validation with pedagogical error messages for HerbCalc.

Provides range checking and menstruum-specific validation that
explains WHY something is wrong, not just that it is.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    """Result of a validation check."""
    valid: bool
    field_name: str
    message: Optional[str] = None
    severity: str = "error"  # "error", "warning", "info"


def validate_range(
    value: float,
    min_val: float,
    max_val: float,
    field_name: str,
) -> ValidationResult:
    """Range check with pedagogical error message.

    Args:
        value: Value to validate.
        min_val: Minimum allowed value.
        max_val: Maximum allowed value.
        field_name: Human-readable field name for error messages.

    Returns:
        ValidationResult indicating whether the value is in range.
    """
    if value < min_val:
        return ValidationResult(
            valid=False,
            field_name=field_name,
            message=(
                f"{field_name} ({value}) is below the minimum ({min_val}). "
                f"Please enter a value between {min_val} and {max_val}."
            ),
            severity="error",
        )
    if value > max_val:
        return ValidationResult(
            valid=False,
            field_name=field_name,
            message=(
                f"{field_name} ({value}) exceeds the maximum ({max_val}). "
                f"Please enter a value between {min_val} and {max_val}."
            ),
            severity="error",
        )
    return ValidationResult(valid=True, field_name=field_name)


def validate_menstruum_inputs(
    herb_g: float,
    ratio: float,
    ethanol_source: float,
    target_alc: float,
    glycerin_pct: float,
) -> list[ValidationResult]:
    """Full validation suite for menstruum calculator.

    Checks:
    - Positive herb weight
    - Ratio >= 1
    - Target alcohol % <= ethanol source %
    - Glycerin + alcohol don't exceed total menstruum
    - Warns if alcohol % is unusually high/low for typical tinctures

    Error messages are pedagogical — they explain the herbalism context.

    Args:
        herb_g: Herb weight in grams.
        ratio: Extraction ratio (e.g., 5 for 1:5).
        ethanol_source: Concentration of ethanol source (%).
        target_alc: Target alcohol percentage in final menstruum.
        glycerin_pct: Glycerin percentage in final menstruum.

    Returns:
        List of ValidationResult objects. Empty list means all valid.
    """
    results = []

    # Herb weight must be positive
    if herb_g <= 0:
        results.append(ValidationResult(
            valid=False,
            field_name="Herb weight",
            message=(
                f"Herb weight must be greater than zero. You entered {herb_g}g. "
                "Enter the weight of dried (or fresh) herb material you're extracting."
            ),
            severity="error",
        ))

    # Ratio must be >= 1
    if ratio < 1:
        results.append(ValidationResult(
            valid=False,
            field_name="Extraction ratio",
            message=(
                f"Extraction ratio must be at least 1 (you entered {ratio}). "
                "The ratio represents parts of menstruum per part of herb. "
                "A 1:5 tincture uses 5 parts menstruum — enter 5, not 1:5. "
                "Fresh herb tinctures typically use 1:1 or 1:2."
            ),
            severity="error",
        ))

    # Ethanol source must be positive
    if ethanol_source <= 0:
        results.append(ValidationResult(
            valid=False,
            field_name="Ethanol source",
            message=(
                "Ethanol source concentration must be greater than 0%. "
                "Common sources: 95% (Everclear 190 proof), 75.5% (Everclear 151), "
                "40% (vodka/brandy 80 proof)."
            ),
            severity="error",
        ))

    # Target alcohol can't exceed source
    if target_alc > ethanol_source > 0:
        results.append(ValidationResult(
            valid=False,
            field_name="Target alcohol %",
            message=(
                f"Target alcohol ({target_alc}%) exceeds your ethanol source "
                f"({ethanol_source}%). "
                "You cannot concentrate alcohol by dilution. Use a higher-proof "
                "source or lower your target percentage. "
                f"With {ethanol_source}% ethanol, your maximum achievable "
                f"menstruum concentration is {ethanol_source}%."
            ),
            severity="error",
        ))

    # Target alcohol can't be negative
    if target_alc < 0:
        results.append(ValidationResult(
            valid=False,
            field_name="Target alcohol %",
            message="Target alcohol percentage cannot be negative.",
            severity="error",
        ))

    # Glycerin can't be negative
    if glycerin_pct < 0:
        results.append(ValidationResult(
            valid=False,
            field_name="Glycerin %",
            message="Glycerin percentage cannot be negative.",
            severity="error",
        ))

    # Glycerin + alcohol can't exceed 100%
    if glycerin_pct + target_alc > 100:
        results.append(ValidationResult(
            valid=False,
            field_name="Solvent percentages",
            message=(
                f"Glycerin ({glycerin_pct}%) + alcohol ({target_alc}%) = "
                f"{glycerin_pct + target_alc}%, which exceeds 100%. "
                "The remaining percentage is water. Together, alcohol + "
                "glycerin cannot exceed 100% of the menstruum."
            ),
            severity="error",
        ))

    # Warning: unusually high alcohol for typical tinctures
    if 0 < target_alc > 70 and not any(not r.valid for r in results):
        results.append(ValidationResult(
            valid=True,
            field_name="Target alcohol %",
            message=(
                f"Target alcohol of {target_alc}% is higher than most tinctures "
                "(typically 25-65%). High alcohol is appropriate for resins "
                "and volatile oils but may denature proteins and not extract "
                "water-soluble constituents well. Verify this matches your "
                "herb's monograph recommendation."
            ),
            severity="warning",
        ))

    # Warning: very low alcohol for preservation
    if 0 < target_alc < 20 and not any(not r.valid for r in results):
        results.append(ValidationResult(
            valid=True,
            field_name="Target alcohol %",
            message=(
                f"Target alcohol of {target_alc}% is below the typical "
                "preservation threshold (~20%). The finished tincture may "
                "have a shorter shelf life and require refrigeration. "
                "Consider whether a glycerite or vinegar extract might "
                "be more appropriate for low-alcohol preparations."
            ),
            severity="warning",
        ))

    return results
