# Shunt Machine Implementation Plan

## Goal

Implement `ShuntMotorGenerator` in `shunt.py` as a learning-oriented DC shunt machine model that preserves the conventions already established for `SeparatelyExcitedMotorGenerator`.

The shunt machine should support both motor and generator operation while making the topology-specific current split explicit.

## Core Topology

In a shunt DC machine, the field winding is connected in parallel with the armature terminals.

This means the field current is determined by terminal voltage, not by an external field supply:

```text
If = Vt / Rf
```

Current relationships differ by operating mode:

```text
Motor:     IL = IA + If
Generator: IA = IL + If
Generator: IL = IA - If
```

The implementation should keep `IA` and `IL` distinct. Armature equations use `IA`; terminal input/output power at the machine terminals uses `IL`.

## Existing Conventions To Preserve

- Keep calculations explicit and formula-oriented.
- Keep motor/generator sign conventions consistent with `SeparatelyExcitedMotorGenerator`.
- Keep negative armature-current rejection in simplified helpers.
- Use `brush_drop_voltage` and `compensating_resistance` consistently through the armature path.
- Prefer explicit helper names over ambiguous overloads.
- Keep analytic helpers analytic-only where that is already the convention.
- Add OCC helpers only where the excitation relationship is clear and useful.

## Required Constructor Behavior

`ShuntMotorGenerator` already inherits the base constructor.

Keep `validate_resistance()` requirements:

```text
shunt_resistance is required
shunt_resistance > 0
```

Do not require `series_resistance`; that belongs to series/compound topology.

## Proposed Public API

### Field Circuit

Implement:

```python
field_current(terminal_voltage: float) -> float
```

Formula:

```text
If = Vt / Rf
```

Validation:

```text
terminal_voltage >= 0
```

Rationale:
For a shunt machine, the argument represents terminal voltage across the shunt field branch. Avoid naming it `applied_field_voltage` in new helper docs except where required by the abstract base signature.

### Current Split Helpers

Add explicit helpers:

```python
line_current_from_armature_current(terminal_voltage: float, armature_current: float) -> float
armature_current_from_line_current(terminal_voltage: float, line_current: float) -> float
```

Formulas:

```text
Motor:     IL = IA + If
Generator: IL = IA - If

Motor:     IA = IL - If
Generator: IA = IL + If
```

Validation:

```text
terminal_voltage >= 0
armature_current >= 0
line_current >= 0
```

For generator mode, `line_current_from_armature_current(...)` should reject operating points where `IA < If`, because that would produce negative external line current in the simplified model.

For motor mode, `armature_current_from_line_current(...)` should reject operating points where `IL < If`, because that would produce negative armature current.

### Armature Electrical Equations

Implement:

```python
armature_current(terminal_voltage: float, induced_emf: float) -> float
induced_emf_from_terminal_conditions(terminal_voltage: float, armature_current: float) -> float
terminal_voltage_from_emf(armature_current: float, induced_emf: float) -> float
```

Use the same armature-path conventions as the separately excited class:

```text
R_a_path = Ra + compensating_resistance, when configured
Vb = brush_drop_voltage, or 0
```

Motor equations:

```text
IA = (Vt - E - Vb) / R_a_path
E = Vt - IA * R_a_path - Vb
Vt = E + IA * R_a_path + Vb
```

Generator equations:

```text
IA = (E - Vt - Vb) / R_a_path
E = Vt + IA * R_a_path + Vb
Vt = E - IA * R_a_path - Vb
```

Validation:

```text
terminal_voltage >= 0
armature_current >= 0 where passed directly
```

Keep `armature_current(...)` able to return a signed value, matching the current separately excited behavior. Helpers that consume an externally supplied armature current should reject negative values.

### Analytic EMF Helpers

Implement analytic-only methods mirroring the established interface:

```python
terminal_voltage(armature_current: float) -> float
induced_torque(armature_current: float) -> float
shaft_speed_rpm(terminal_voltage: float, armature_current: float) -> float
```

Use existing base analytic model:

```text
E = K * flux * speed_rpm
T = E * IA / omega
n = E / (K * flux)
```

Validation:

```text
analytic model configured
armature_current >= 0
terminal_voltage >= 0 where passed directly
```

### OCC Helpers

Add OCC helpers after the analytic baseline is stable.

Useful first helpers:

```python
induced_emf_from_terminal_voltage(terminal_voltage: float, desired_speed_rpm: float | None = None) -> float
terminal_voltage_from_field_current_not_applicable: do not add
```

For shunt machines, field current depends on terminal voltage:

```text
If = Vt / Rf
E = OCC(If) scaled to speed
```

For generator operation, solving terminal voltage from load current with OCC may require an implicit equation because `Vt` determines `If`, and `If` determines `E`. Do not hide this behind a simplistic direct helper unless a clear iterative solver is added and tested.

First implementation recommendation:

- Implement direct OCC helper for known terminal voltage.
- Defer nonlinear self-excited generator load solving to a later iteration.

## Power And Losses

Power handling must differ from separately excited operation.

In a separately excited machine, field power comes from an external supply. In a shunt machine, field power is part of terminal electrical input/output.

Add explicit shunt power helpers instead of reusing the separately excited `applied_field_voltage` API:

```python
field_copper_losses(terminal_voltage: float) -> float
copper_losses(terminal_voltage: float, armature_current: float) -> float
terminal_power(terminal_voltage: float, line_current: float) -> float
input_power(terminal_voltage: float, line_current: float, armature_current: float, induced_emf: float) -> float
output_power(terminal_voltage: float, line_current: float, armature_current: float, induced_emf: float) -> float
efficiency(terminal_voltage: float, line_current: float, armature_current: float, induced_emf: float) -> float
```

Field copper loss:

```text
Pcu,field = If^2 * Rf
```

Armature copper loss remains:

```text
Pcu,arm = IA^2 * R_a_path
```

Terminal power uses line current:

```text
Pterminal = Vt * IL
```

Converted electromagnetic power uses armature current:

```text
Pconv = E * IA
```

Suggested power-flow definitions:

```text
Motor input:      Pin = Vt * IL
Motor output:     Pout = Pconv - rotational_losses

Generator input:  Pin = Pconv + rotational_losses
Generator output: Pout = Vt * IL
```

Do not add field power separately to input or output for shunt machines, because it is already included through `Vt * IL`.

## Tests To Add

Create `dc_machine/tests/test_05_shunt.py`.

Test groups:

1. Constructor and resistance validation

```text
requires shunt_resistance
rejects zero/negative shunt_resistance
accepts positive shunt_resistance
```

2. Field current

```text
If = Vt / Rf
rejects negative terminal voltage
```

3. Current split

```text
motor IL = IA + If
generator IL = IA - If
motor IA = IL - If
generator IA = IL + If
rejects current splits that produce negative currents
```

4. Armature equations

```text
motor armature_current uses Vt - E - Vb
generator armature_current uses E - Vt - Vb
terminal_voltage_from_emf uses compensating resistance and brush drop
induced_emf_from_terminal_conditions uses compensating resistance and brush drop
```

5. Analytic helpers

```text
terminal_voltage uses analytic EMF in generator mode
induced_torque uses E * IA / omega
shaft_speed_rpm solves E / (K * flux)
negative armature-current rejection
```

6. Power and efficiency

```text
field copper losses use terminal voltage
copper losses include armature and shunt field losses
motor input uses line current
generator output uses line current
efficiency does not add external field power
```

7. OCC direct helper, if included in first implementation

```text
field current is derived from terminal voltage
OCC EMF scales with desired speed
invalid desired speed is rejected
missing magnetization curve is rejected
```

## Example To Add

Add one small example after tests pass:

```text
dc_machine/examples/example_05_shunt_machine.py
```

The example should show:

- `If = Vt / Rf`
- motor current split: `IL = IA + If`
- generator current split: `IL = IA - If`
- one power/efficiency calculation

Keep the example numeric and explicit. Do not add plotting in the first shunt implementation.

## Implementation Order

1. Add tests for constructor, field current, current split, and armature equations.
2. Implement enough `ShuntMotorGenerator` code to pass those tests.
3. Add analytic torque/speed/terminal-voltage tests.
4. Implement analytic helpers.
5. Add power/efficiency tests.
6. Implement shunt-specific power helpers.
7. Add direct OCC helper tests only if the analytic and power API are stable.
8. Implement direct OCC helper if included.
9. Add the educational example.
10. Update README with shunt status and example command.

## Verification

Run from project root:

```sh
uv run python -m pytest dc_machine/tests/test_05_shunt.py
uv run python -m pytest dc_machine/tests
uv run python -m dc_machine.examples.example_05_shunt_machine
```

## Deferred Work

Do not include these in the first implementation unless explicitly requested:

- Self-excited shunt generator voltage build-up solver.
- Iterative loaded terminal-voltage solver using OCC.
- Saturation plus armature-reaction workflow for shunt machines.
- Plot helpers for shunt machine characteristics.
- Series or compound machine implementation.
