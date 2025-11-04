"""
Stock management algorithms for supply chain optimization.
"""

import math
from typing import List, Tuple
from abc import ABC, abstractmethod


class StockAlgorithm(ABC):
    """Base class for stock management algorithms."""

    @abstractmethod
    def calculate(self, *args, **kwargs):
        """Calculate stock management parameters."""
        pass


class EOQAlgorithm(StockAlgorithm):
    """
    Economic Order Quantity (EOQ) Algorithm.

    Determines the optimal order quantity that minimizes total inventory costs,
    including ordering costs and holding costs.

    Formula: EOQ = sqrt((2 * D * S) / H)
    where:
        D = Annual demand
        S = Ordering cost per order
        H = Holding cost per unit per year
    """

    def calculate(self, annual_demand: float, ordering_cost: float, holding_cost: float) -> float:
        """
        Calculate Economic Order Quantity.

        Args:
            annual_demand: Annual demand for the product
            ordering_cost: Fixed cost per order
            holding_cost: Holding cost per unit per year

        Returns:
            Optimal order quantity

        Raises:
            ValueError: If any parameter is invalid
        """
        if annual_demand <= 0:
            raise ValueError("Annual demand must be positive")
        if ordering_cost < 0:
            raise ValueError("Ordering cost cannot be negative")
        if holding_cost <= 0:
            raise ValueError("Holding cost must be positive")

        eoq = math.sqrt((2 * annual_demand * ordering_cost) / holding_cost)
        return eoq

    def calculate_total_cost(
        self, annual_demand: float, ordering_cost: float, holding_cost: float, order_quantity: float
    ) -> Tuple[float, float, float]:
        """
        Calculate total annual cost for a given order quantity.

        Args:
            annual_demand: Annual demand for the product
            ordering_cost: Fixed cost per order
            holding_cost: Holding cost per unit per year
            order_quantity: Order quantity to evaluate

        Returns:
            Tuple of (total_cost, ordering_cost_total, holding_cost_total)
        """
        if order_quantity <= 0:
            raise ValueError("Order quantity must be positive")

        number_of_orders = annual_demand / order_quantity
        total_ordering_cost = number_of_orders * ordering_cost
        total_holding_cost = (order_quantity / 2) * holding_cost
        total_cost = total_ordering_cost + total_holding_cost

        return total_cost, total_ordering_cost, total_holding_cost

    def calculate_reorder_frequency(self, annual_demand: float, eoq: float) -> float:
        """
        Calculate number of orders per year.

        Args:
            annual_demand: Annual demand for the product
            eoq: Economic order quantity

        Returns:
            Number of orders per year
        """
        return annual_demand / eoq if eoq > 0 else 0


class ReorderPointAlgorithm(StockAlgorithm):
    """
    Reorder Point (ROP) Algorithm.

    Determines when to place a new order based on lead time demand.

    Formula: ROP = (Average daily demand * Lead time in days) + Safety stock
    """

    def calculate(self, daily_demand: float, lead_time_days: int, safety_stock: float = 0) -> float:
        """
        Calculate Reorder Point.

        Args:
            daily_demand: Average daily demand
            lead_time_days: Lead time in days
            safety_stock: Safety stock level (optional)

        Returns:
            Reorder point level

        Raises:
            ValueError: If any parameter is invalid
        """
        if daily_demand < 0:
            raise ValueError("Daily demand cannot be negative")
        if lead_time_days < 0:
            raise ValueError("Lead time cannot be negative")
        if safety_stock < 0:
            raise ValueError("Safety stock cannot be negative")

        rop = (daily_demand * lead_time_days) + safety_stock
        return rop

    def calculate_from_annual(
        self,
        annual_demand: float,
        lead_time_days: int,
        safety_stock: float = 0,
        working_days: int = 365,
    ) -> float:
        """
        Calculate Reorder Point from annual demand.

        Args:
            annual_demand: Annual demand
            lead_time_days: Lead time in days
            safety_stock: Safety stock level (optional)
            working_days: Number of working days per year (default 365)

        Returns:
            Reorder point level
        """
        if working_days <= 0:
            raise ValueError("Working days must be positive")

        daily_demand = annual_demand / working_days
        return self.calculate(daily_demand, lead_time_days, safety_stock)


class SafetyStockAlgorithm(StockAlgorithm):
    """
    Safety Stock Algorithm.

    Determines the buffer stock level needed to protect against demand variability
    and supply uncertainty.

    Formula: Safety Stock = Z * σ * sqrt(L)
    where:
        Z = Service level factor (Z-score)
        σ = Standard deviation of demand
        L = Lead time
    """

    def calculate(
        self, service_level_z: float, demand_std_dev: float, lead_time_days: int
    ) -> float:
        """
        Calculate Safety Stock level.

        Args:
            service_level_z: Z-score for desired service level
                           (e.g., 1.65 for 95%, 2.33 for 99%)
            demand_std_dev: Standard deviation of daily demand
            lead_time_days: Lead time in days

        Returns:
            Safety stock level

        Raises:
            ValueError: If any parameter is invalid
        """
        if service_level_z < 0:
            raise ValueError("Service level Z-score cannot be negative")
        if demand_std_dev < 0:
            raise ValueError("Standard deviation cannot be negative")
        if lead_time_days < 0:
            raise ValueError("Lead time cannot be negative")

        safety_stock = service_level_z * demand_std_dev * math.sqrt(lead_time_days)
        return safety_stock

    @staticmethod
    def get_z_score_for_service_level(service_level_percent: float) -> float:
        """
        Get approximate Z-score for common service levels.

        Args:
            service_level_percent: Desired service level as percentage (e.g., 95, 99)

        Returns:
            Corresponding Z-score
        """
        service_levels = {
            50: 0.00,
            75: 0.67,
            80: 0.84,
            85: 1.04,
            90: 1.28,
            95: 1.65,
            97: 1.88,
            98: 2.05,
            99: 2.33,
            99.5: 2.58,
            99.9: 3.09,
        }

        if service_level_percent in service_levels:
            return service_levels[service_level_percent]

        # Find closest service level
        closest = min(service_levels.keys(), key=lambda x: abs(x - service_level_percent))
        return service_levels[closest]


class ABCAnalysisAlgorithm(StockAlgorithm):
    """
    ABC Analysis Algorithm.

    Classifies inventory items based on their value/importance:
    - A items: High value (typically 70-80% of value, 10-20% of items)
    - B items: Medium value (typically 15-25% of value, 30% of items)
    - C items: Low value (typically 5-10% of value, 50-60% of items)
    """

    def calculate(self, items: List[Tuple[str, float, float]]) -> dict:
        """
        Classify items into ABC categories.

        Args:
            items: List of tuples (product_id, unit_cost, annual_demand)

        Returns:
            Dictionary mapping product_id to category ('A', 'B', or 'C')
        """
        if not items:
            return {}

        # Calculate total value for each item
        item_values = []
        for product_id, unit_cost, annual_demand in items:
            total_value = unit_cost * annual_demand
            item_values.append((product_id, total_value))

        # Sort by value descending
        item_values.sort(key=lambda x: x[1], reverse=True)

        # Calculate cumulative percentages
        total_value = sum(value for _, value in item_values)

        classification = {}
        cumulative_value = 0

        for product_id, value in item_values:
            # Check cumulative percentage before adding current item
            current_cumulative_percent = (cumulative_value / total_value) * 100

            if current_cumulative_percent < 80:
                classification[product_id] = "A"
            elif current_cumulative_percent < 95:
                classification[product_id] = "B"
            else:
                classification[product_id] = "C"

            cumulative_value += value

        return classification
