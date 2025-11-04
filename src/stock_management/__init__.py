"""
Stock Management Algorithms for Supply Chain Optimization

This package provides various algorithms for stock management in supply chains,
including Economic Order Quantity (EOQ), Reorder Point (ROP), Safety Stock,
and other inventory optimization techniques.
"""

from .models import Inventory, Order, Demand
from .algorithms import (
    EOQAlgorithm,
    ReorderPointAlgorithm,
    SafetyStockAlgorithm,
    ABCAnalysisAlgorithm,
)

__version__ = "0.1.0"

__all__ = [
    "Inventory",
    "Order",
    "Demand",
    "EOQAlgorithm",
    "ReorderPointAlgorithm",
    "SafetyStockAlgorithm",
    "ABCAnalysisAlgorithm",
]
