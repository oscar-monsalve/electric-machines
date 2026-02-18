# AGENTS.md - Electric Machines Codebase Guide

## Overview

This is a Python project for electric machine calculations (DC machines, induction motors, synchronous machines, transformers, magnetic circuits). Based on Chapman's "Electric Machinery" textbook.

## Project Structure

```
electric-machines/
├── dc_machine/           # DC machine calculations
├── induction_motor/      # Induction motor theoretical model & exercises
│   ├── theoretical_model/
│   └── exercises/
├── magnetic_circuits/    # Magnetic circuit calculations
├── synchronous_machine/   # Synchronous motor & generator
│   ├── motor/
│   └── generator/
└── transformer/          # Single-phase & three-phase transformers
    └── three_phase/
```

## Running Code

### Single Script Execution

```bash
python path/to/script.py
```

### Running Individual Exercises

```bash
# Example: transformer single-phase
cd transformer/single_phase && python main.py

# Example: induction motor exercises
cd induction_motor/exercises && python ex1.py
```

### Dependencies

Install required packages:

```bash
pip install numpy matplotlib scienceplots
```

Note: This project has **no formal test suite**. Tests would need to be added.

---

## Code Style Guidelines

### General Philosophy

- Write clear, readable code for engineering calculations
- Include units in variable names or comments (e.g., `vn1` = primary voltage in V)
- Document the source of formulas (textbook references, equations)

### Type Hints

Use type hints for function signatures:

```python
def total_resistance(power_short_circuit: float, current_short_circuit: float) -> float:
    ...
```

### Docstrings

Use docstrings for all public functions:

```python
def function_name(param: float) -> float:
    """Returns the result in watts. Description of what it does."""
    ...
```

### Naming Conventions

- **Variables**: snake_case (e.g., `power_short_circuit`, `vn1`)
- **Constants**: snake_case with descriptive names (e.g., `vacuum_permeability`)
- **Functions**: snake_case, verb-based (e.g., `calculate_flux`, `efficiency`)
- **Classes**: PascalCase if used (not common in this codebase)

### Imports

Order imports by category with blank lines between:

```python
# Standard library
import cmath
from math import acos, degrees

# Third-party libraries
import numpy as np
import matplotlib.pyplot as plt
from numpy import linspace

# Local imports
import equivalent_circuit_parameters as model
from helpers_ex1 import some_function
```

### Code Formatting

- Maximum line length: 100 characters (prefer 80)
- Use 4 spaces for indentation (no tabs)
- Use blank lines to separate logical sections
- Use f-strings for string formatting:

```python
print(f"- Efficiency -> eta: {efficiency:.2f} %.")
```

### Error Handling

Use explicit error types for invalid inputs:

```python
if connection not in ("delta", "star"):
    raise TypeError("'Connection' is not a valid input. Try with 'delta' or 'star'.")
```

Validate input ranges when critical:

```python
if load < 0:
    raise ValueError("Load must be non-negative")
```

### Numeric Precision

- Use `np.sqrt()` for square roots
- Use `np.pi` for π
- Format output with appropriate precision (typically 2 decimal places for results, 4-6 for intermediate values)
- Use NumPy functions (`np.rad2deg`, `np.deg2rad`, `np.sqrt`) for consistency

### Plotting

Use scienceplots for publication-quality figures:

```python
import matplotlib.pyplot as plt
import scienceplots
plt.style.use(["science", "notebook", "grid"])
```

### Physics/Engineering Conventions

- Use SI units throughout (watts, volts, amps, ohms, weber, tesla)
- Document assumptions about phase relationships
- Use complex numbers for AC calculations (`cmath.rect`, `cmath.polar`)
- Label plots with proper units (LaTeX formatting acceptable)

---

## Adding New Code

### Creating New Machine Models

1. Create a new directory under the appropriate category
2. Add helper functions in a `helpers.py` or `model.py` file
3. Create a `main.py` with a `main()` function that runs the calculations
4. Follow the existing structure for input parameters and output display

### Example Function Template

```python
import numpy as np
from typing import Tuple


def calculate_power(voltage: float, current: float, pf: float) -> float:
    """Returns the real power in watts.

    Args:
        voltage: Line voltage in volts
        current: Line current in amps
        pf: Power factor (0-1)

    Returns:
        Real power in watts
    """
    return np.sqrt(3) * voltage * current * pf


def efficiency_output(
    input_power: float,
    output_power: float
) -> Tuple[float, float]:
    """Returns efficiency as percentage and ratio.

    Args:
        input_power: Input power in watts
        output_power: Output power in watts

    Returns:
        Tuple of (efficiency_percent, efficiency_ratio)
    """
    eff_ratio = output_power / input_power
    eff_percent = eff_ratio * 100
    return eff_percent, eff_ratio
```

---

## Common Patterns

### Unit Conversion

```python
# RPM to rad/s
velocity_rad = velocity * (2 * np.pi) / 60

# Degrees to radians
angle_rad = np.deg2rad(angle_deg)
```

### Complex Numbers for AC

```python
import cmath

# Polar to rectangular
current = cmath.rect(magnitude, np.deg2rad(angle))

# Rectangular to polar
magnitude, angle = cmath.polar(complex_current)
```

### Plotting Multiple Curves

```python
plt.figure()
for index, parameter in enumerate(parameter_set):
    plt.plot(x_data, y_data[index], label=f"label={parameter}")
plt.xlabel(r"X label (unit)")
plt.ylabel(r"Y label (unit)")
plt.legend()
plt.grid(True)
plt.show()
```

---

## Notes for Agents

- This codebase is for educational calculations, not production software
- No CI/CD pipeline exists
- No type checking enforcement (mypy) or linting (ruff, flake8) currently configured
- If adding tests, use `pytest` as the test framework
- If adding linting, consider `ruff` for fast linting and formatting
