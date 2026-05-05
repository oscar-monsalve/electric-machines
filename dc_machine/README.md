## Overview

`dc_machine` is a small educational module for DC machine calculations.

The current implementation includes:

- `base.py`
  - Defines the abstract `DCMachine` base class
  - Stores common electrical and operating data such as armature resistance, nominal voltage, speed, optional brush
    drop, optional compensating resistance, optional constant losses, and optional Open-Circuit Characteristic
    (OCC)/nonlinear armature-reaction data.
  - Provides shared helpers for analytic EMF validation, armature-path resistance, losses, and common machine metadata.

- `separately_excited.py`
  - Implements `SeparatelyExcitedMotorGenerator`
  - Supports motor and generator operation
  - Supports two excitation approaches:
  - Analytic model: `E = K * flux * speed_rpm`
  - OCC-based model through `MagnetizationCurve`
  - Includes helpers for:
    - Field current and field-circuit resistance
    - Induced EMF, terminal voltage, torque, and shaft speed
    - External field-adjusting resistance `R_adj`
    - Copper losses, rotational losses, input/output power, and efficiencies.
    - Fixed armature-reaction analysis using equivalent field current and OCC inversion

Supporting files used by the implemented machine are:

- `magnetization.py`
  - defines `MagnetizationCurve` for forward and inverse OCC interpolation with speed scaling.

- `utils.py`
  - Provides small utilities such as unit conversion, speed conversion, speed regulation, OCC construction, and CSV
    extraction for example data.

Planned future machine types:

- Shunt DC machine
- Series DC machine
- Compound DC machine

## Standard Execution

The standard way to run code in this module is from the project root `/electric-machines` using module execution:

```sh
uv run python -m dc_machine.examples.example_01_separately_excited_basic_calcs
uv run python -m dc_machine.examples.example_02_separately_excited_efficiency
uv run python -m dc_machine.examples.example_03_separately_excited_fixed_armature_reaction
```

This same convention should be used for tests:

```sh
uv run python -m pytest dc_machine/tests -v
```

## Running

From the project root `/electric-machines`, execute the examples:

```sh
uv run python -m dc_machine.examples.example_01_separately_excited_basic_calcs
uv run python -m dc_machine.examples.example_02_separately_excited_efficiency
uv run python -m dc_machine.examples.example_03_separately_excited_fixed_armature_reaction
```

## Testing

From the project root `/electric-machines`:

```sh
uv run python -m pytest dc_machine/tests -v
```

If working from `/electric-machines/dc_machine`, run with the project root explicitly:

```sh
uv run --project .. python -m dc_machine.examples.example_01_separately_excited_basic_calcs
uv run --project .. python -m pytest tests -v
```
