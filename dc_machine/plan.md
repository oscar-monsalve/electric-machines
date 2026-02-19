# DC Machine OOP Model Plan

## Goal
Create a Python class library to model DC machines (motor and generator) with all common connection types.

## Class Hierarchy

```
DCMachine (abstract base class)
├── SeparatelyExcited
├── ShuntMotor/Generator
├── SeriesMotor/Generator
└── CompoundMotor/Generator
    ├── CumulativeCompound
    └── DifferentialCompound
```

## Key Design Decisions

### 1. Motor/Generator Modes
- **Decision**: Use a `mode` property on the base class rather than separate classes
- Reason: Same physics, just the sign of power flow changes

### 2. Field Circuit Handling
- Each subclass implements `field_current()` based on connection type
- Base class calculates `E = k * phi * speed` generically

### 3. Core Attributes per Machine
| Attribute | Symbol | Unit |
|-----------|--------|------|
| k | machine constant | V·s/rad or N·m/A |
| flux_per_pole | Φ | Wb |
| armature_resistance | Rₐ | Ω |
| field_resistance | Rf | Ω |
| supply_voltage | V | V |
| speed | n or ω | rpm or rad/s |

### 4. Core Methods
- `armature_current()` - calculate Iₐ from circuit equations
- `back_emf()` - calculate E = kΦω
- `developed_torque()` - T = kΦIₐ
- `output_power()` / `input_power()`
- `efficiency()`

## File Structure

```
dc_machine/
├── __init__.py
├── base.py          # DCMachine abstract base class
├── separately_excited.py
├── shunt.py
├── series.py
├── compound.py
└── main.py          # Example usage
```

## Implementation Order

1. **base.py**: Define abstract class with common physics
2. **separately_excited.py**: Simplest case (field current = given)
3. **shunt.py**: Field in parallel with armature
4. **series.py**: Field in series with armature
5. **compound.py**: Both series + shunt field (cumulative/differential)

---

Would you like me to adjust any of these design decisions before finalizing the plan?
