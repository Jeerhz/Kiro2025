"""
Tests for stock management data models.
"""

import pytest
from datetime import datetime
from src.stock_management.models import Inventory, Order, Demand


class TestDemand:
    """Tests for Demand model."""
    
    def test_create_demand(self):
        """Test creating a valid demand."""
        demand = Demand(product_id="P001", quantity=100)
        assert demand.product_id == "P001"
        assert demand.quantity == 100
        assert isinstance(demand.timestamp, datetime)
    
    def test_negative_demand_raises_error(self):
        """Test that negative demand raises ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            Demand(product_id="P001", quantity=-10)


class TestOrder:
    """Tests for Order model."""
    
    def test_create_order(self):
        """Test creating a valid order."""
        order = Order(product_id="P001", quantity=50, order_cost=100, lead_time_days=5)
        assert order.product_id == "P001"
        assert order.quantity == 50
        assert order.order_cost == 100
        assert order.lead_time_days == 5
        assert isinstance(order.timestamp, datetime)
    
    def test_order_total_cost(self):
        """Test order total cost calculation."""
        order = Order(product_id="P001", quantity=50, order_cost=100)
        assert order.total_cost == 100
    
    def test_zero_quantity_raises_error(self):
        """Test that zero quantity raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            Order(product_id="P001", quantity=0, order_cost=100)
    
    def test_negative_order_cost_raises_error(self):
        """Test that negative order cost raises ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            Order(product_id="P001", quantity=50, order_cost=-100)
    
    def test_negative_lead_time_raises_error(self):
        """Test that negative lead time raises ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            Order(product_id="P001", quantity=50, order_cost=100, lead_time_days=-1)


class TestInventory:
    """Tests for Inventory model."""
    
    def test_create_inventory(self):
        """Test creating a valid inventory."""
        inventory = Inventory(
            product_id="P001",
            current_stock=100,
            holding_cost_per_unit=2.5,
            unit_cost=10.0,
            min_stock_level=20,
            max_stock_level=200
        )
        assert inventory.product_id == "P001"
        assert inventory.current_stock == 100
        assert inventory.holding_cost_per_unit == 2.5
        assert inventory.unit_cost == 10.0
    
    def test_add_stock(self):
        """Test adding stock to inventory."""
        inventory = Inventory(
            product_id="P001",
            current_stock=100,
            holding_cost_per_unit=2.5
        )
        inventory.add_stock(50)
        assert inventory.current_stock == 150
    
    def test_add_zero_stock_raises_error(self):
        """Test that adding zero stock raises ValueError."""
        inventory = Inventory(
            product_id="P001",
            current_stock=100,
            holding_cost_per_unit=2.5
        )
        with pytest.raises(ValueError, match="must be positive"):
            inventory.add_stock(0)
    
    def test_remove_stock(self):
        """Test removing stock from inventory."""
        inventory = Inventory(
            product_id="P001",
            current_stock=100,
            holding_cost_per_unit=2.5
        )
        inventory.remove_stock(30)
        assert inventory.current_stock == 70
    
    def test_remove_too_much_stock_raises_error(self):
        """Test that removing more than available stock raises ValueError."""
        inventory = Inventory(
            product_id="P001",
            current_stock=100,
            holding_cost_per_unit=2.5
        )
        with pytest.raises(ValueError, match="Cannot remove"):
            inventory.remove_stock(150)
    
    def test_is_below_minimum(self):
        """Test checking if stock is below minimum."""
        inventory = Inventory(
            product_id="P001",
            current_stock=15,
            holding_cost_per_unit=2.5,
            min_stock_level=20
        )
        assert inventory.is_below_minimum() is True
        
        inventory.add_stock(10)
        assert inventory.is_below_minimum() is False
    
    def test_is_above_maximum(self):
        """Test checking if stock is above maximum."""
        inventory = Inventory(
            product_id="P001",
            current_stock=250,
            holding_cost_per_unit=2.5,
            max_stock_level=200
        )
        assert inventory.is_above_maximum() is True
        
        inventory.remove_stock(60)
        assert inventory.is_above_maximum() is False
    
    def test_calculate_holding_cost(self):
        """Test calculating holding cost."""
        inventory = Inventory(
            product_id="P001",
            current_stock=100,
            holding_cost_per_unit=2.5
        )
        assert inventory.calculate_holding_cost() == 250
    
    def test_negative_current_stock_raises_error(self):
        """Test that negative current stock raises ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            Inventory(
                product_id="P001",
                current_stock=-10,
                holding_cost_per_unit=2.5
            )
    
    def test_invalid_max_stock_raises_error(self):
        """Test that max stock less than min stock raises ValueError."""
        with pytest.raises(ValueError, match="cannot be less than minimum"):
            Inventory(
                product_id="P001",
                current_stock=100,
                holding_cost_per_unit=2.5,
                min_stock_level=100,
                max_stock_level=50
            )
