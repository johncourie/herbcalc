"""Tests for core/validation.py — input validation with pedagogical messages."""

import pytest

from core.validation import validate_range, validate_menstruum_inputs, ValidationResult


class TestValidateRange:
    """Tests for generic range validation."""

    def test_value_in_range(self):
        result = validate_range(50, 0, 100, "Test field")
        assert result.valid is True
        assert result.message is None

    def test_value_at_minimum(self):
        result = validate_range(0, 0, 100, "Test field")
        assert result.valid is True

    def test_value_at_maximum(self):
        result = validate_range(100, 0, 100, "Test field")
        assert result.valid is True

    def test_value_below_minimum(self):
        result = validate_range(-1, 0, 100, "Test field")
        assert result.valid is False
        assert "below the minimum" in result.message

    def test_value_above_maximum(self):
        result = validate_range(101, 0, 100, "Test field")
        assert result.valid is False
        assert "exceeds the maximum" in result.message

    def test_error_includes_field_name(self):
        result = validate_range(-1, 0, 100, "Herb weight")
        assert "Herb weight" in result.message


class TestValidateMenstruumInputs:
    """Tests for menstruum-specific validation."""

    def test_valid_defaults(self):
        """Standard defaults should pass all validation."""
        results = validate_menstruum_inputs(100, 5, 94, 40, 0)
        errors = [r for r in results if not r.valid]
        assert len(errors) == 0

    def test_zero_herb_weight(self):
        results = validate_menstruum_inputs(0, 5, 94, 40, 0)
        errors = [r for r in results if not r.valid]
        assert len(errors) >= 1
        assert any("Herb weight" in r.field_name for r in errors)

    def test_negative_herb_weight(self):
        results = validate_menstruum_inputs(-10, 5, 94, 40, 0)
        errors = [r for r in results if not r.valid]
        assert len(errors) >= 1

    def test_ratio_below_one(self):
        results = validate_menstruum_inputs(100, 0.5, 94, 40, 0)
        errors = [r for r in results if not r.valid]
        assert len(errors) >= 1
        assert any("ratio" in r.field_name.lower() for r in errors)

    def test_target_exceeds_source(self):
        """Target 70% with vodka (40%) source — impossible."""
        results = validate_menstruum_inputs(100, 5, 40, 70, 0)
        errors = [r for r in results if not r.valid]
        assert len(errors) >= 1
        # Should explain WHY
        msg = " ".join(r.message for r in errors if r.message)
        assert "cannot concentrate" in msg.lower() or "exceeds" in msg.lower()

    def test_glycerin_plus_alcohol_over_100(self):
        results = validate_menstruum_inputs(100, 5, 94, 60, 50)
        errors = [r for r in results if not r.valid]
        assert len(errors) >= 1
        assert any("exceed" in r.message.lower() for r in errors if r.message)

    def test_negative_target_alcohol(self):
        results = validate_menstruum_inputs(100, 5, 94, -5, 0)
        errors = [r for r in results if not r.valid]
        assert len(errors) >= 1

    def test_negative_glycerin(self):
        results = validate_menstruum_inputs(100, 5, 94, 40, -10)
        errors = [r for r in results if not r.valid]
        assert len(errors) >= 1

    def test_high_alcohol_warning(self):
        """Target >70% should warn (but not error)."""
        results = validate_menstruum_inputs(100, 5, 94, 80, 0)
        warnings = [r for r in results if r.valid and r.severity == "warning"]
        assert len(warnings) >= 1
        assert any("higher than most" in r.message.lower() for r in warnings)

    def test_low_alcohol_warning(self):
        """Target <20% should warn about preservation."""
        results = validate_menstruum_inputs(100, 5, 94, 15, 0)
        warnings = [r for r in results if r.valid and r.severity == "warning"]
        assert len(warnings) >= 1
        assert any("preservation" in r.message.lower() for r in warnings)

    def test_pedagogical_messages_explain_why(self):
        """Error messages should contain explanatory context, not just 'invalid'."""
        results = validate_menstruum_inputs(100, 5, 40, 70, 0)
        errors = [r for r in results if not r.valid]
        for error in errors:
            # Message should be longer than a simple "invalid value"
            assert len(error.message) > 50, (
                f"Error message too terse — should be pedagogical: {error.message}"
            )
