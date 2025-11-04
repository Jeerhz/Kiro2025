"""
Core data models for stock management system.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Demand:
    """Represents demand for a product over time."""

    product_id: str
    quantity: float
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.quantity < 0:
            raise ValueError("Demand quantity cannot be negative")


@dataclass
class Order:
    """Represents a purchase order for inventory replenishment."""

    product_id: str
    quantity: float
    order_cost: float
    lead_time_days: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Order quantity must be positive")
        if self.order_cost < 0:
            raise ValueError("Order cost cannot be negative")
        if self.lead_time_days < 0:
            raise ValueError("Lead time cannot be negative")

    @property
    def total_cost(self) -> float:
        """Calculate the total cost of the order."""
        return self.order_cost


@dataclass
class Inventory:
    """Represents current inventory state for a product."""

    product_id: str
    current_stock: float
    holding_cost_per_unit: float
    unit_cost: float = 0.0
    min_stock_level: float = 0.0
    max_stock_level: Optional[float] = None

    def __post_init__(self):
        if self.current_stock < 0:
            raise ValueError("Current stock cannot be negative")
        if self.holding_cost_per_unit < 0:
            raise ValueError("Holding cost cannot be negative")
        if self.unit_cost < 0:
            raise ValueError("Unit cost cannot be negative")
        if self.min_stock_level < 0:
            raise ValueError("Minimum stock level cannot be negative")
        if self.max_stock_level is not None and self.max_stock_level < self.min_stock_level:
            raise ValueError("Maximum stock level cannot be less than minimum")

    def add_stock(self, quantity: float) -> None:
        """Add stock to inventory."""
        if quantity <= 0:
            raise ValueError("Quantity to add must be positive")
        self.current_stock += quantity

    def remove_stock(self, quantity: float) -> None:
        """Remove stock from inventory."""
        if quantity <= 0:
            raise ValueError("Quantity to remove must be positive")
        if quantity > self.current_stock:
            raise ValueError(
                f"Cannot remove {quantity} units. Only {self.current_stock} available."
            )
        self.current_stock -= quantity

    def is_below_minimum(self) -> bool:
        """Check if current stock is below minimum level."""
        return self.current_stock < self.min_stock_level

    def is_above_maximum(self) -> bool:
        """Check if current stock is above maximum level."""
        if self.max_stock_level is None:
            return False
        return self.current_stock > self.max_stock_level

    def calculate_holding_cost(self) -> float:
        """Calculate the holding cost for current stock."""
        return self.current_stock * self.holding_cost_per_unit
