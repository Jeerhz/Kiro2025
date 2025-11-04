"""
Basic usage examples for stock management algorithms.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.stock_management import (
    Inventory,
    Order,
    Demand,
    EOQAlgorithm,
    ReorderPointAlgorithm,
    SafetyStockAlgorithm,
)


def example_eoq():
    """Example: Economic Order Quantity calculation."""
    print("=" * 60)
    print("Economic Order Quantity (EOQ) Example")
    print("=" * 60)

    eoq_algo = EOQAlgorithm()

    # Parameters
    annual_demand = 1000  # units per year
    ordering_cost = 50  # cost per order
    holding_cost = 2  # cost per unit per year

    # Calculate EOQ
    eoq = eoq_algo.calculate(annual_demand, ordering_cost, holding_cost)

    print("\nInput Parameters:")
    print(f"  Annual Demand: {annual_demand} units")
    print(f"  Ordering Cost: ${ordering_cost} per order")
    print(f"  Holding Cost: ${holding_cost} per unit per year")

    print("\nResults:")
    print(f"  Optimal Order Quantity (EOQ): {eoq:.2f} units")

    # Calculate costs
    total_cost, ordering_cost_total, holding_cost_total = eoq_algo.calculate_total_cost(
        annual_demand, ordering_cost, holding_cost, eoq
    )

    print(f"  Total Annual Cost: ${total_cost:.2f}")
    print(f"    - Ordering Cost: ${ordering_cost_total:.2f}")
    print(f"    - Holding Cost: ${holding_cost_total:.2f}")

    # Reorder frequency
    frequency = eoq_algo.calculate_reorder_frequency(annual_demand, eoq)
    print(f"  Number of Orders per Year: {frequency:.2f}")
    print(f"  Days between Orders: {365/frequency:.2f}")


def example_reorder_point():
    """Example: Reorder Point calculation."""
    print("\n" + "=" * 60)
    print("Reorder Point (ROP) Example")
    print("=" * 60)

    rop_algo = ReorderPointAlgorithm()

    # Parameters
    daily_demand = 10  # units per day
    lead_time_days = 5  # days
    safety_stock = 20  # units

    # Calculate ROP
    rop = rop_algo.calculate(daily_demand, lead_time_days, safety_stock)

    print("\nInput Parameters:")
    print(f"  Daily Demand: {daily_demand} units")
    print(f"  Lead Time: {lead_time_days} days")
    print(f"  Safety Stock: {safety_stock} units")

    print("\nResults:")
    print(f"  Reorder Point: {rop:.2f} units")
    print(f"  When inventory reaches {rop:.2f} units, place a new order!")


def example_safety_stock():
    """Example: Safety Stock calculation."""
    print("\n" + "=" * 60)
    print("Safety Stock Example")
    print("=" * 60)

    ss_algo = SafetyStockAlgorithm()

    # Parameters
    service_level_percent = 95  # 95% service level
    demand_std_dev = 5  # standard deviation of daily demand
    lead_time_days = 4  # days

    # Get Z-score for service level
    z_score = ss_algo.get_z_score_for_service_level(service_level_percent)

    # Calculate safety stock
    safety_stock = ss_algo.calculate(z_score, demand_std_dev, lead_time_days)

    print("\nInput Parameters:")
    print(f"  Desired Service Level: {service_level_percent}%")
    print(f"  Z-score: {z_score}")
    print(f"  Demand Std Dev: {demand_std_dev} units")
    print(f"  Lead Time: {lead_time_days} days")

    print("\nResults:")
    print(f"  Safety Stock Level: {safety_stock:.2f} units")


def example_inventory_management():
    """Example: Complete inventory management scenario."""
    print("\n" + "=" * 60)
    print("Complete Inventory Management Example")
    print("=" * 60)

    # Create inventory
    inventory = Inventory(
        product_id="WIDGET-001",
        current_stock=150,
        holding_cost_per_unit=2.5,
        unit_cost=10.0,
        min_stock_level=50,
        max_stock_level=300,
    )

    print("\nInitial Inventory State:")
    print(f"  Product ID: {inventory.product_id}")
    print(f"  Current Stock: {inventory.current_stock} units")
    print(f"  Holding Cost: ${inventory.calculate_holding_cost():.2f}")
    print(f"  Below Minimum? {inventory.is_below_minimum()}")

    # Simulate demand
    print("\nSimulating Demand...")
    demand = Demand(product_id="WIDGET-001", quantity=60)
    print(f"  Demand: {demand.quantity} units")
    inventory.remove_stock(demand.quantity)
    print(f"  Stock after demand: {inventory.current_stock} units")
    print(f"  Below Minimum? {inventory.is_below_minimum()}")

    # Calculate optimal order
    eoq_algo = EOQAlgorithm()
    annual_demand = 1200
    ordering_cost = 100

    eoq = eoq_algo.calculate(annual_demand, ordering_cost, inventory.holding_cost_per_unit)
    print("\nOptimal Order Calculation:")
    print(f"  EOQ: {eoq:.2f} units")

    # Place order
    if inventory.is_below_minimum():
        order = Order(
            product_id="WIDGET-001", quantity=eoq, order_cost=ordering_cost, lead_time_days=5
        )
        print("\nPlacing Order:")
        print(f"  Order Quantity: {order.quantity:.2f} units")
        print(f"  Order Cost: ${order.total_cost:.2f}")
        print(f"  Lead Time: {order.lead_time_days} days")

        # Simulate order arrival
        inventory.add_stock(order.quantity)
        print(f"\nStock after order arrival: {inventory.current_stock:.2f} units")
        print(f"  Holding Cost: ${inventory.calculate_holding_cost():.2f}")


def main():
    """Run all examples."""
    example_eoq()
    example_reorder_point()
    example_safety_stock()
    example_inventory_management()
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
