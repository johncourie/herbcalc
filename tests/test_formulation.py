"""Tests for core/formulation.py — formula building and scaling."""

import pytest

from core.formulation import (
    build_formula,
    scale_parts,
    dry_equivalent,
    tincture_from_dose,
    HerbEntry,
)


class TestBuildFormula:
    """Tests for multi-herb formula building."""

    def test_single_herb(self):
        herbs = [HerbEntry(name="Valerian", parts=1, ratio=5, alcohol_pct=45)]
        result = build_formula(herbs, target_volume_ml=100)
        assert len(result.herbs) == 1
        assert result.total_menstruum_ml == pytest.approx(100.0)
        assert result.herbs[0].weight_g == pytest.approx(20.0)  # 100/5

    def test_two_herbs_equal_parts(self):
        herbs = [
            HerbEntry(name="Valerian", parts=2, ratio=5, alcohol_pct=60),
            HerbEntry(name="Passionflower", parts=2, ratio=5, alcohol_pct=40),
        ]
        result = build_formula(herbs, target_volume_ml=100)
        assert len(result.herbs) == 2
        assert result.compromise_alcohol_pct == pytest.approx(50.0)
        assert result.herbs[0].menstruum_ml == pytest.approx(50.0)
        assert result.herbs[1].menstruum_ml == pytest.approx(50.0)

    def test_unequal_parts(self):
        herbs = [
            HerbEntry(name="Valerian", parts=3, ratio=5, alcohol_pct=60),
            HerbEntry(name="Passionflower", parts=1, ratio=5, alcohol_pct=40),
        ]
        result = build_formula(herbs, target_volume_ml=100)
        # Compromise alcohol: (3/4)*60 + (1/4)*40 = 45 + 10 = 55
        assert result.compromise_alcohol_pct == pytest.approx(55.0)
        assert result.herbs[0].menstruum_ml == pytest.approx(75.0)
        assert result.herbs[1].menstruum_ml == pytest.approx(25.0)

    def test_empty_formula(self):
        result = build_formula([])
        assert len(result.herbs) == 0
        assert len(result.warnings) > 0

    def test_default_volume_100(self):
        herbs = [HerbEntry(name="Test", parts=1, ratio=5, alcohol_pct=45)]
        result = build_formula(herbs)
        assert result.total_menstruum_ml == pytest.approx(100.0)


class TestScaleParts:
    """Tests for parts-to-weight scaling."""

    def test_equal_parts(self):
        parts = [("Valerian", 1.0), ("Skullcap", 1.0)]
        scaled = scale_parts(parts, 100)
        assert scaled[0][1] == pytest.approx(50.0)
        assert scaled[1][1] == pytest.approx(50.0)

    def test_unequal_parts(self):
        parts = [("Valerian", 3.0), ("Skullcap", 1.0)]
        scaled = scale_parts(parts, 100)
        assert scaled[0][1] == pytest.approx(75.0)
        assert scaled[1][1] == pytest.approx(25.0)

    def test_zero_parts(self):
        parts = [("A", 0.0), ("B", 0.0)]
        scaled = scale_parts(parts, 100)
        assert all(w == 0.0 for _, w in scaled)

    def test_total_matches_target(self):
        parts = [("A", 2.0), ("B", 3.0), ("C", 5.0)]
        scaled = scale_parts(parts, 200)
        total = sum(w for _, w in scaled)
        assert total == pytest.approx(200.0)


class TestDryEquivalent:
    """Tests for tincture volume -> dried herb weight conversion."""

    def test_basic_conversion(self):
        """5mL of 1:5 tincture = 1g dried herb."""
        assert dry_equivalent(5, 5) == pytest.approx(1.0)

    def test_1ml_of_1_to_5(self):
        """1mL of 1:5 = 0.2g."""
        assert dry_equivalent(1, 5) == pytest.approx(0.2)

    def test_fresh_herb_ratio(self):
        """2mL of 1:2 = 1g."""
        assert dry_equivalent(2, 2) == pytest.approx(1.0)

    def test_zero_ratio_raises(self):
        with pytest.raises(ValueError):
            dry_equivalent(5, 0)

    def test_negative_ratio_raises(self):
        with pytest.raises(ValueError):
            dry_equivalent(5, -1)


class TestTinctureFromDose:
    """Tests for target dried herb dose -> tincture volume."""

    def test_basic_conversion(self):
        """500mg dose at 1:5 ratio = 2.5mL."""
        assert tincture_from_dose(500, 5) == pytest.approx(2.5)

    def test_1g_dose_1_to_5(self):
        """1000mg = 1g at 1:5 = 5mL."""
        assert tincture_from_dose(1000, 5) == pytest.approx(5.0)

    def test_small_dose(self):
        """100mg at 1:5 = 0.5mL."""
        assert tincture_from_dose(100, 5) == pytest.approx(0.5)

    def test_roundtrip(self):
        """dose -> tincture -> dose should round-trip."""
        original_mg = 750
        ratio = 5
        tincture_ml = tincture_from_dose(original_mg, ratio)
        recovered_g = dry_equivalent(tincture_ml, ratio)
        assert recovered_g * 1000 == pytest.approx(original_mg)
