# DC Machine Implementation Plan

This document captures the agreed next steps before continuing with the full physics implementations of shunt, series, and compound DC machines.

## Guiding Principle

Keep a clear separation between:

- structural machine data stored on the machine object
- operating-point data used only for a specific calculation

This keeps `DCMachine` clean and avoids mixing permanent machine parameters with temporary analysis inputs.

## 1. Compensating Winding Resistance

Add a new optional constructor parameter to `dc_machine/base.py`:

- `compensating_resistance: float | None = None`

Reasoning:

- In the intended equivalent circuit, the compensating or auxiliary winding contributes an extra resistance in series with the armature path.
- This behavior is common to any machine connection, so it belongs in the base class.
- It should remain distinct from `series_resistance`.

Terminology decision:

- Prefer `compensating_resistance`
- Do not reuse `series_resistance`
- Do not use a vague name such as `auxiliary_resistance`

Validation rule:

- if provided, `compensating_resistance` must be positive and non-zero

Implementation direction:

- store it in `DCMachine`
- add a helper such as `_armature_path_resistance() -> float`
- define:
  - `R_a_total = armature_resistance + compensating_resistance`
- update armature-path equations to use `R_a_total`

Why this should happen first:

- all future topology implementations will reuse the armature-path resistance
- it reduces duplicated resistance handling in shunt, series, and compound machines

## 2. Efficiency and Loss Modeling

Efficiency support should be added soon, but not by making every loss parameter mandatory in the constructor.

Recommended constructor fields:

- `mechanical_losses: float | None = None`
- `core_losses: float | None = None`
- `misc_losses: float | None = None`

Validation rule:

- if provided, each loss must be non-negative

Calculation rule:

- omitted loss values behave as `0.0`

Reasoning:

- winding resistances and brush drop are structural machine parameters
- mechanical/core/misc losses are usually modeling assumptions or operating-condition data
- keeping them optional preserves flexibility for educational problems

### Power and Loss Helpers

Instead of implementing only one monolithic efficiency formula, first add reusable power-flow helpers.

Recommended helpers:

- `copper_losses(armature_current: float, field_current: float | None = None) -> float`
- `brush_losses(armature_current: float) -> float`
- `rotational_losses() -> float`
- `electromagnetic_power(armature_current: float, induced_emf: float) -> float`
- `input_power(...)`
- `output_power(...)`

These helpers should make the power flow explicit and reusable across machine types.

### Copper Losses

Common losses to include:

- armature copper loss:
  - `P_cu_arm = Ia^2 * R_a_total`
- brush loss:
  - `P_brush = Vb * Ia`
- field copper loss for separately excited machines:
  - `P_cu_field = If^2 * Rf`
  - equivalently `P_cu_field = Vf * If`

Important note:

- for separately excited machines, total copper loss is not only armature copper loss

### Efficiency Methods

Two efficiency methods are desired:

- `overall_efficiency(...)`
- `armature_side_efficiency(...)`

Interpretation:

- `overall_efficiency(...)` includes the full machine balance, including field-supply power where applicable
- `armature_side_efficiency(...)` focuses only on the armature-side conversion path

This is especially important for separately excited machines.

### Suggested Physics Structure

For a motor:

- electrical input consists of armature input and, if applicable, field input
- electromagnetic converted power:
  - `P_dev = E * Ia`
- shaft output:
  - `P_out = P_dev - P_mech - P_core - P_misc`

For a generator:

- shaft input is the mechanical input
- electromagnetic converted power:
  - `P_dev = E * Ia`
- terminal electrical output is reduced by electrical losses
- overall efficiency should be explicit about whether field excitation power is included

## 3. Nonlinear Analysis With Armature Reaction

This is the most physics-heavy addition and should be implemented after the resistance and efficiency groundwork is in place.

The agreed direction is to support nonlinear OCC-based analysis without overloading the existing analytic-only API.

### Core Data Needed

Add field-turn information:

- `field_turns: float | None = None`

This will support equivalent-field-current calculations based on magnetomotive force.

### Armature-Reaction Input Model

Do not start with only one fixed armature-reaction value in ampere-turns unless a very simplified model is intentionally desired.

Preferred design is to support one or both of these models:

1. constant armature-reaction coefficient
- `armature_reaction_at_per_a: float | None = None`
- then:
  - `F_ar = armature_reaction_at_per_a * Ia`

2. armature-reaction curve
- a separate object, analogous to `MagnetizationCurve`
- maps armature current to armature-reaction mmf

Reasoning:

- armature reaction is normally load dependent
- a coefficient or curve is more realistic than one fixed constructor value

### Nonlinear Helper Methods

Stay consistent with the current design direction:

- keep existing analytic methods analytic-only
- add explicit nonlinear or OCC-aware helper methods

Candidate helpers:

- `equivalent_field_current(...)`
- `induced_emf_from_equivalent_field_current(...)`
- `induced_emf_with_armature_reaction(...)`
- `terminal_voltage_from_field_voltage_with_armature_reaction(...)`

### Separately Excited Generator Workflow

For a separately excited generator, the intended nonlinear workflow is:

1. compute actual field current `If`
2. compute field mmf:
   - `F_field = N_F * If`
3. compute armature-reaction mmf from load:
   - `F_ar`
4. compute net mmf:
   - `F_net = F_field - F_ar`
5. compute equivalent field current:
   - `If* = F_net / N_F`
6. obtain `E_A0` from the magnetization curve at reference speed
7. scale to actual speed using:
   - `E_A = E_A0 * n_m / n_o`

This matches the intended physical model and generalizes cleanly later.

## Recommended Order of Implementation

Implement the next steps in this order:

1. Add common armature-path resistance support
- add `compensating_resistance`
- validate it
- add `_armature_path_resistance()`
- update separately excited equations to use total armature-path resistance

2. Add loss and power-flow primitives
- add optional constant-loss fields
- add helpers for copper, brush, rotational, and electromagnetic power
- add `overall_efficiency(...)`
- add `armature_side_efficiency(...)`

3. Add armature-reaction abstractions
- add `field_turns`
- decide between coefficient-only support or coefficient plus curve support
- add explicit nonlinear helper methods

4. Continue with full physics implementations for shunt, series, and compound machines

## Things to Avoid

- do not merge compensating-winding resistance into `series_resistance`
- do not make all loss values mandatory constructor arguments
- do not model armature reaction only as a fixed constant unless a simplified mode is explicitly desired
- do not overload the existing analytic-only methods with nonlinear OCC behavior

## Summary of Agreed Decisions

- add `compensating_resistance` to the base class
- treat it as part of the armature path, distinct from `series_resistance`
- add reusable loss and power-flow helpers before implementing efficiency formulas only
- support two efficiency views:
  - `overall_efficiency(...)`
  - `armature_side_efficiency(...)`
- keep nonlinear armature-reaction analysis in explicit OCC-aware helpers
- implement these foundations before the full shunt, series, and compound machine physics
