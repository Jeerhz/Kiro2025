# Kiro2025 - Stock Management Algorithms

Concours de Recherche Opérationnelle organisé par le laboratoire CERMICS et l'entreprise Califrais

This project provides a Python framework for testing and comparing various algorithms for stock management in supply chain operations. It implements classical inventory optimization techniques including Economic Order Quantity (EOQ), Reorder Point (ROP), Safety Stock calculations, and ABC Analysis.

## Features

- **Data Models**: Robust data structures for Inventory, Orders, and Demand
- **Algorithms**:
  - Economic Order Quantity (EOQ) - Optimize order quantities
  - Reorder Point (ROP) - Determine when to order
  - Safety Stock - Calculate buffer inventory levels
  - ABC Analysis - Classify inventory by value
- **Testing Framework**: Comprehensive test suite with pytest
- **Examples**: Ready-to-use examples demonstrating algorithm usage

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/Jeerhz/Kiro2025.git
cd Kiro2025

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Quick Start

### Basic Usage

```python
from src.stock_management import EOQAlgorithm, Inventory, Order

# Calculate Economic Order Quantity
eoq_algo = EOQAlgorithm()
optimal_order = eoq_algo.calculate(
    annual_demand=1000,
    ordering_cost=50,
    holding_cost=2
)
print(f"Optimal order quantity: {optimal_order:.2f} units")

# Manage inventory
inventory = Inventory(
    product_id="PROD-001",
    current_stock=150,
    holding_cost_per_unit=2.5,
    min_stock_level=50
)

# Check if reorder needed
if inventory.is_below_minimum():
    print("Time to reorder!")
```

### Running Examples

```bash
python examples/basic_usage.py
```

## Project Structure

```
Kiro2025/
├── src/
│   └── stock_management/
│       ├── __init__.py
│       ├── models.py          # Data models (Inventory, Order, Demand)
│       └── algorithms.py      # Stock management algorithms
├── tests/
│   ├── test_models.py         # Tests for data models
│   └── test_algorithms.py     # Tests for algorithms
├── examples/
│   └── basic_usage.py         # Usage examples
├── requirements.txt           # Project dependencies
├── setup.py                   # Package setup
└── README.md
```

## Algorithms

### Economic Order Quantity (EOQ)

Determines the optimal order quantity that minimizes total inventory costs.

**Formula**: `EOQ = √((2 × D × S) / H)`
- D = Annual demand
- S = Ordering cost per order
- H = Holding cost per unit per year

### Reorder Point (ROP)

Determines when to place a new order based on lead time demand.

**Formula**: `ROP = (Daily Demand × Lead Time) + Safety Stock`

### Safety Stock

Calculates buffer inventory to protect against demand variability.

**Formula**: `Safety Stock = Z × σ × √L`
- Z = Service level factor (Z-score)
- σ = Standard deviation of demand
- L = Lead time

### ABC Analysis

Classifies inventory items by value:
- **A items**: High value (70-80% of value, 10-20% of items)
- **B items**: Medium value (15-25% of value, 30% of items)
- **C items**: Low value (5-10% of value, 50-60% of items)

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/stock_management tests/

# Run specific test file
pytest tests/test_algorithms.py
```

## Development

### Installing Development Dependencies

```bash
pip install -r requirements.txt
```

### Code Style

The project uses standard Python formatting tools:

```bash
# Format code with black
black src/ tests/ examples/

# Check code style with flake8
flake8 src/ tests/ examples/

# Type checking with mypy
mypy src/
```

## Contributing

Contributions are welcome! This project is part of an operational research competition, and we're exploring various approaches to stock management optimization.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- CERMICS Laboratory
- Califrais
- KIRO Competition organizers
