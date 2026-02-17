"""Tests for core/units.py — unit conversion engine."""

import pytest

from core.units import convert, convert_all, get_unit_info, list_units, ConversionResult


class TestGetUnitInfo:
    """Tests for unit registry lookup."""

    def test_lookup_by_canonical_name(self):
        info = get_unit_info("gram")
        assert info is not None
        assert info.unit_name == "gram"
        assert info.to_base == 1.0

    def test_lookup_by_alias(self):
        info = get_unit_info("g")
        assert info is not None
        assert info.unit_name == "gram"

    def test_lookup_by_symbol(self):
        info = get_unit_info("kg")
        assert info is not None
        assert info.unit_name == "kilogram"

    def test_lookup_case_insensitive(self):
        info = get_unit_info("Gram")
        assert info is not None
        assert info.unit_name == "gram"

    def test_lookup_unknown_returns_none(self):
        info = get_unit_info("nonexistent_unit")
        assert info is None

    def test_metric_mass_units_exist(self):
        for name in ["milligram", "gram", "kilogram"]:
            info = get_unit_info(name)
            assert info is not None, f"{name} should be registered"
            assert info.unit_type == "mass"

    def test_metric_volume_units_exist(self):
        for name in ["milliliter", "liter"]:
            info = get_unit_info(name)
            assert info is not None, f"{name} should be registered"
            assert info.unit_type == "volume"


class TestConvert:
    """Tests for unit conversion."""

    def test_gram_to_kilogram(self):
        result = convert(1000, "gram", "kilogram")
        assert result.value == pytest.approx(1.0)
        assert result.unit == "kilogram"

    def test_kilogram_to_gram(self):
        result = convert(1, "kilogram", "gram")
        assert result.value == pytest.approx(1000.0)

    def test_milligram_to_gram(self):
        result = convert(500, "milligram", "gram")
        assert result.value == pytest.approx(0.5)

    def test_gram_to_milligram(self):
        result = convert(0.5, "gram", "milligram")
        assert result.value == pytest.approx(500.0)

    def test_identity_conversion(self):
        result = convert(42, "gram", "gram")
        assert result.value == pytest.approx(42.0)

    def test_zero_value(self):
        result = convert(0, "gram", "kilogram")
        assert result.value == pytest.approx(0.0)

    def test_milliliter_to_liter(self):
        result = convert(1500, "milliliter", "liter")
        assert result.value == pytest.approx(1.5)

    def test_cross_system_ounce_to_gram(self):
        """Avoirdupois ounce to metric gram."""
        result = convert(1, "ounce", "gram")
        assert result.value == pytest.approx(28.349523, rel=1e-4)

    def test_cross_system_teaspoon_to_ml(self):
        """Household teaspoon to metric milliliter."""
        result = convert(1, "teaspoon", "milliliter")
        assert result.value == pytest.approx(4.92892, rel=1e-3)

    def test_unknown_source_unit_raises(self):
        with pytest.raises(ValueError, match="Unknown unit"):
            convert(1, "zorkmids", "gram")

    def test_unknown_target_unit_raises(self):
        with pytest.raises(ValueError, match="Unknown unit"):
            convert(1, "gram", "zorkmids")

    def test_incompatible_types_raises(self):
        """Cannot convert mass to volume."""
        with pytest.raises(ValueError, match="Cannot convert"):
            convert(1, "gram", "milliliter")

    def test_negative_value(self):
        """Negative values should convert correctly (math is valid)."""
        result = convert(-10, "gram", "kilogram")
        assert result.value == pytest.approx(-0.01)

    def test_imprecise_unit_generates_warning(self):
        """Household drops should carry a precision warning."""
        result = convert(20, "drop", "milliliter")
        assert len(result.warnings) > 0
        assert any("imprecise" in w.lower() for w in result.warnings)

    def test_apothecary_grain_to_gram(self):
        """Grain = 0.06479891g in both apothecary and avoirdupois."""
        result = convert(1, "grain", "gram")
        assert result.value == pytest.approx(0.06479891, rel=1e-4)

    def test_apothecary_scruple_to_gram(self):
        """1 scruple = 20 grains = 1.2959782g."""
        result = convert(1, "scruple", "gram")
        assert result.value == pytest.approx(1.2959782, rel=1e-4)


class TestConvertAll:
    """Tests for convert_all (multi-unit conversion)."""

    def test_returns_list(self):
        results = convert_all(100, "gram")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_all_results_are_conversion_results(self):
        results = convert_all(100, "gram")
        for r in results:
            assert isinstance(r, ConversionResult)

    def test_filter_by_system(self):
        results = convert_all(100, "gram", target_system="metric")
        for r in results:
            assert r.system == "metric"

    def test_unknown_unit_raises(self):
        with pytest.raises(ValueError):
            convert_all(100, "zorkmids")


class TestListUnits:
    """Tests for list_units."""

    def test_returns_list(self):
        units = list_units()
        assert isinstance(units, list)
        assert len(units) > 0

    def test_filter_by_type(self):
        mass_units = list_units(unit_type="mass")
        for u in mass_units:
            assert u.unit_type == "mass"

    def test_filter_by_system(self):
        metric_units = list_units(system="metric")
        for u in metric_units:
            assert u.system == "metric"

    def test_filter_by_both(self):
        metric_mass = list_units(unit_type="mass", system="metric")
        for u in metric_mass:
            assert u.unit_type == "mass"
            assert u.system == "metric"
