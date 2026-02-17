"""Tests for core/solvents.py — solvent calculations."""

import pytest

from core.solvents import (
    calculate_menstruum,
    pearson_square,
    lookup_ethanol_density,
    density_correct,
    convert_percentage,
)


class TestCalculateMenstruum:
    """Tests for the core menstruum calculation."""

    def test_default_herbcalc_regression(self):
        """Regression test: original herbcalc.php defaults.

        100g herb, 1:5 ratio, 94% ethanol source, 40% target, 0% glycerin.
        Expected: 500mL total, 212.77mL source alcohol, 287.23mL water.
        """
        result = calculate_menstruum(
            herb_weight_g=100,
            ratio=5,
            ethanol_source_pct=94,
            target_alcohol_pct=40,
            glycerin_pct=0,
        )
        assert result.total_volume_ml == pytest.approx(500.0)
        # Pure ethanol needed: 500 * 0.40 = 200mL
        assert result.ethanol_ml == pytest.approx(200.0)
        # Water: 500 - 200 = 300mL
        assert result.water_ml == pytest.approx(300.0)
        assert result.glycerin_ml == pytest.approx(0.0)
        # Source alcohol volume: 200 / 0.94 = 212.766mL
        assert result.ethanol_source_ml == pytest.approx(212.766, rel=1e-2)
        # Added water: 300 - (212.766 - 200) = 300 - 12.766 = 287.234mL
        assert result.added_water_ml == pytest.approx(287.234, rel=1e-2)

    def test_with_glycerin(self):
        """Test menstruum with glycerin component."""
        result = calculate_menstruum(
            herb_weight_g=100,
            ratio=5,
            ethanol_source_pct=95,
            target_alcohol_pct=40,
            glycerin_pct=10,
        )
        assert result.total_volume_ml == pytest.approx(500.0)
        assert result.glycerin_ml == pytest.approx(50.0)  # 10% of 500
        assert result.ethanol_ml == pytest.approx(200.0)  # 40% of 500
        assert result.water_ml == pytest.approx(250.0)  # remainder

    def test_zero_alcohol(self):
        """Pure water menstruum (e.g., for cold infusion)."""
        result = calculate_menstruum(
            herb_weight_g=50,
            ratio=10,
            ethanol_source_pct=95,
            target_alcohol_pct=0,
            glycerin_pct=0,
        )
        assert result.total_volume_ml == pytest.approx(500.0)
        assert result.ethanol_ml == pytest.approx(0.0)
        assert result.water_ml == pytest.approx(500.0)

    def test_glycerite(self):
        """Full glycerite (no alcohol)."""
        result = calculate_menstruum(
            herb_weight_g=100,
            ratio=5,
            ethanol_source_pct=95,
            target_alcohol_pct=0,
            glycerin_pct=60,
        )
        assert result.glycerin_ml == pytest.approx(300.0)
        assert result.water_ml == pytest.approx(200.0)
        assert result.ethanol_ml == pytest.approx(0.0)

    def test_fresh_herb_ratio(self):
        """1:2 fresh herb ratio."""
        result = calculate_menstruum(
            herb_weight_g=200,
            ratio=2,
            ethanol_source_pct=95,
            target_alcohol_pct=75,
            glycerin_pct=0,
        )
        assert result.total_volume_ml == pytest.approx(400.0)
        assert result.ethanol_ml == pytest.approx(300.0)

    def test_overconstrained_warns(self):
        """Glycerin + alcohol > 100% should produce warning."""
        result = calculate_menstruum(
            herb_weight_g=100,
            ratio=5,
            ethanol_source_pct=95,
            target_alcohol_pct=60,
            glycerin_pct=50,
        )
        assert len(result.warnings) > 0
        assert result.water_ml == 0.0  # clamped to zero


class TestPearsonSquare:
    """Tests for Pearson's square alcohol dilution."""

    def test_basic_dilution(self):
        """95% source -> 40% target, 1000mL total."""
        result = pearson_square(95, 40, 1000)
        assert result.source_volume_ml == pytest.approx(421.05, rel=1e-2)
        assert result.diluent_volume_ml == pytest.approx(578.95, rel=1e-2)
        assert result.source_volume_ml + result.diluent_volume_ml == pytest.approx(1000.0)

    def test_no_dilution_needed(self):
        """Target equals source — all source, no diluent."""
        result = pearson_square(95, 95, 500)
        assert result.source_volume_ml == pytest.approx(500.0)
        assert result.diluent_volume_ml == pytest.approx(0.0)

    def test_target_zero(self):
        """Target 0% — all water."""
        result = pearson_square(95, 0, 500)
        assert result.source_volume_ml == pytest.approx(0.0)
        assert result.diluent_volume_ml == pytest.approx(500.0)

    def test_target_exceeds_source_raises(self):
        with pytest.raises(ValueError, match="exceeds source"):
            pearson_square(40, 95, 500)

    def test_zero_source_raises(self):
        with pytest.raises(ValueError, match="greater than 0"):
            pearson_square(0, 40, 500)

    def test_vodka_dilution(self):
        """Vodka (40%) -> 25% target."""
        result = pearson_square(40, 25, 500)
        assert result.source_volume_ml == pytest.approx(312.5, rel=1e-2)
        assert result.diluent_volume_ml == pytest.approx(187.5, rel=1e-2)


class TestLookupEthanolDensity:
    """Tests for ethanol-water density interpolation."""

    def test_pure_water(self):
        density = lookup_ethanol_density(0)
        assert density == pytest.approx(1.0, rel=1e-3)

    def test_pure_ethanol(self):
        density = lookup_ethanol_density(100)
        assert density == pytest.approx(0.7893, rel=1e-3)

    def test_40_percent(self):
        density = lookup_ethanol_density(40)
        assert density == pytest.approx(0.9352, rel=1e-3)

    def test_interpolation_midpoint(self):
        """22.5% should interpolate between 20% and 25%."""
        d20 = lookup_ethanol_density(20)
        d25 = lookup_ethanol_density(25)
        d22_5 = lookup_ethanol_density(22.5)
        expected = (d20 + d25) / 2
        assert d22_5 == pytest.approx(expected, rel=1e-3)

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError):
            lookup_ethanol_density(-1)
        with pytest.raises(ValueError):
            lookup_ethanol_density(101)


class TestDensityCorrect:
    """Tests for volume-to-weight density correction."""

    def test_water(self):
        weight = density_correct(100, "water")
        assert weight == pytest.approx(100.0)

    def test_ethanol(self):
        weight = density_correct(100, "ethanol")
        assert weight == pytest.approx(78.9, rel=1e-2)

    def test_glycerin(self):
        weight = density_correct(100, "glycerin")
        assert weight == pytest.approx(126.1, rel=1e-2)


class TestConvertPercentage:
    """Tests for percentage convention conversion."""

    def test_identity(self):
        assert convert_percentage(40, "vv", "vv") == pytest.approx(40.0)
        assert convert_percentage(40, "wv", "wv") == pytest.approx(40.0)
        assert convert_percentage(40, "ww", "ww") == pytest.approx(40.0)

    def test_vv_to_wv_ethanol(self):
        """v/v to w/v: multiply by substance density."""
        result = convert_percentage(40, "vv", "wv", "ethanol")
        # 40% v/v * 0.7893 ≈ 31.57% w/v
        assert result == pytest.approx(31.57, rel=1e-2)

    def test_roundtrip_vv_wv(self):
        """v/v -> w/v -> v/v should return original."""
        wv = convert_percentage(40, "vv", "wv", "ethanol")
        vv = convert_percentage(wv, "wv", "vv", "ethanol")
        assert vv == pytest.approx(40.0, rel=1e-2)
