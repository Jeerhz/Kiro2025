"""
Tests for stock management algorithms.
"""

import pytest
import math
from src.stock_management.algorithms import (
    EOQAlgorithm,
    ReorderPointAlgorithm,
    SafetyStockAlgorithm,
    ABCAnalysisAlgorithm,
)


class TestEOQAlgorithm:
    """Tests for Economic Order Quantity algorithm."""

    def test_calculate_eoq(self):
        """Test basic EOQ calculation."""
        eoq_algo = EOQAlgorithm()
        eoq = eoq_algo.calculate(annual_demand=1000, ordering_cost=50, holding_cost=2)
        expected = math.sqrt((2 * 1000 * 50) / 2)
        assert abs(eoq - expected) < 0.01
        assert eoq > 0

    def test_eoq_with_high_demand(self):
        """Test EOQ with high demand."""
        eoq_algo = EOQAlgorithm()
        eoq = eoq_algo.calculate(annual_demand=10000, ordering_cost=100, holding_cost=5)
        assert eoq > 0
        assert eoq == pytest.approx(632.45, rel=0.01)

    def test_negative_demand_raises_error(self):
        """Test that negative demand raises ValueError."""
        eoq_algo = EOQAlgorithm()
        with pytest.raises(ValueError, match="must be positive"):
            eoq_algo.calculate(annual_demand=-1000, ordering_cost=50, holding_cost=2)

    def test_zero_holding_cost_raises_error(self):
        """Test that zero holding cost raises ValueError."""
        eoq_algo = EOQAlgorithm()
        with pytest.raises(ValueError, match="must be positive"):
            eoq_algo.calculate(annual_demand=1000, ordering_cost=50, holding_cost=0)

    def test_calculate_total_cost(self):
        """Test total cost calculation."""
        eoq_algo = EOQAlgorithm()
        total, ordering, holding = eoq_algo.calculate_total_cost(
            annual_demand=1000, ordering_cost=50, holding_cost=2, order_quantity=100
        )
        assert total == ordering + holding
        assert ordering == (1000 / 100) * 50
        assert holding == (100 / 2) * 2

    def test_calculate_reorder_frequency(self):
        """Test reorder frequency calculation."""
        eoq_algo = EOQAlgorithm()
        frequency = eoq_algo.calculate_reorder_frequency(annual_demand=1000, eoq=100)
        assert frequency == 10  # 10 orders per year


class TestReorderPointAlgorithm:
    """Tests for Reorder Point algorithm."""

    def test_calculate_rop_without_safety_stock(self):
        """Test basic ROP calculation without safety stock."""
        rop_algo = ReorderPointAlgorithm()
        rop = rop_algo.calculate(daily_demand=10, lead_time_days=5, safety_stock=0)
        assert rop == 50

    def test_calculate_rop_with_safety_stock(self):
        """Test ROP calculation with safety stock."""
        rop_algo = ReorderPointAlgorithm()
        rop = rop_algo.calculate(daily_demand=10, lead_time_days=5, safety_stock=20)
        assert rop == 70

    def test_calculate_from_annual_demand(self):
        """Test ROP calculation from annual demand."""
        rop_algo = ReorderPointAlgorithm()
        rop = rop_algo.calculate_from_annual(
            annual_demand=3650, lead_time_days=5, safety_stock=20, working_days=365
        )
        assert rop == 70  # (3650/365)*5 + 20 = 50 + 20

    def test_negative_daily_demand_raises_error(self):
        """Test that negative daily demand raises ValueError."""
        rop_algo = ReorderPointAlgorithm()
        with pytest.raises(ValueError, match="cannot be negative"):
            rop_algo.calculate(daily_demand=-10, lead_time_days=5, safety_stock=0)

    def test_negative_lead_time_raises_error(self):
        """Test that negative lead time raises ValueError."""
        rop_algo = ReorderPointAlgorithm()
        with pytest.raises(ValueError, match="cannot be negative"):
            rop_algo.calculate(daily_demand=10, lead_time_days=-5, safety_stock=0)


class TestSafetyStockAlgorithm:
    """Tests for Safety Stock algorithm."""

    def test_calculate_safety_stock(self):
        """Test basic safety stock calculation."""
        ss_algo = SafetyStockAlgorithm()
        safety_stock = ss_algo.calculate(service_level_z=1.65, demand_std_dev=5, lead_time_days=4)
        expected = 1.65 * 5 * math.sqrt(4)
        assert abs(safety_stock - expected) < 0.01
        assert safety_stock > 0

    def test_safety_stock_with_zero_std_dev(self):
        """Test safety stock with zero standard deviation."""
        ss_algo = SafetyStockAlgorithm()
        safety_stock = ss_algo.calculate(service_level_z=1.65, demand_std_dev=0, lead_time_days=4)
        assert safety_stock == 0

    def test_get_z_score_for_service_level(self):
        """Test Z-score lookup for common service levels."""
        assert SafetyStockAlgorithm.get_z_score_for_service_level(95) == 1.65
        assert SafetyStockAlgorithm.get_z_score_for_service_level(99) == 2.33
        assert SafetyStockAlgorithm.get_z_score_for_service_level(90) == 1.28

    def test_get_z_score_for_uncommon_service_level(self):
        """Test Z-score lookup for uncommon service levels (returns closest)."""
        z_score = SafetyStockAlgorithm.get_z_score_for_service_level(96)
        assert z_score in [1.65, 1.88]  # Should return closest match

    def test_negative_z_score_raises_error(self):
        """Test that negative Z-score raises ValueError."""
        ss_algo = SafetyStockAlgorithm()
        with pytest.raises(ValueError, match="cannot be negative"):
            ss_algo.calculate(service_level_z=-1.65, demand_std_dev=5, lead_time_days=4)


class TestABCAnalysisAlgorithm:
    """Tests for ABC Analysis algorithm."""

    def test_abc_analysis_basic(self):
        """Test basic ABC analysis."""
        abc_algo = ABCAnalysisAlgorithm()
        items = [
            ("P001", 100, 1000),  # High value: 100,000
            ("P002", 10, 500),  # Medium value: 5,000
            ("P003", 5, 200),  # Low value: 1,000
        ]
        classification = abc_algo.calculate(items)

        assert classification["P001"] == "A"
        assert classification["P002"] in ["B", "C"]
        assert classification["P003"] == "C"

    def test_abc_analysis_empty_list(self):
        """Test ABC analysis with empty list."""
        abc_algo = ABCAnalysisAlgorithm()
        classification = abc_algo.calculate([])
        assert classification == {}

    def test_abc_analysis_single_item(self):
        """Test ABC analysis with single item."""
        abc_algo = ABCAnalysisAlgorithm()
        items = [("P001", 100, 1000)]
        classification = abc_algo.calculate(items)

        assert classification["P001"] == "A"

    def test_abc_analysis_multiple_items(self):
        """Test ABC analysis with multiple items."""
        abc_algo = ABCAnalysisAlgorithm()
        items = [
            ("P001", 1000, 100),  # 100,000
            ("P002", 500, 50),  # 25,000
            ("P003", 200, 100),  # 20,000
            ("P004", 50, 200),  # 10,000
            ("P005", 10, 500),  # 5,000
            ("P006", 5, 100),  # 500
        ]
        classification = abc_algo.calculate(items)

        # High value items should be A
        assert classification["P001"] == "A"
        # Verify all items are classified
        assert len(classification) == 6
        # Verify only A, B, C categories
        assert all(cat in ["A", "B", "C"] for cat in classification.values())
