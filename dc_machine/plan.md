# Step 3 Plan: Nonlinear Analysis With Armature Reaction

## Goal

Implement a first nonlinear OCC-based armature-reaction workflow for
`SeparatelyExcitedMotorGenerator` using a fixed demagnetizing MMF in
ampere-turns.

## Scope

This first implementation will support:

- separately excited machine only
- fixed armature-reaction MMF
- OCC / magnetization-curve-based nonlinear analysis only
- both forward and inverse nonlinear OCC calculations for the separately excited machine
- voltage-restoration exercises where field current or `R_adj` must be solved

It will not support yet:

- load-dependent armature reaction
- armature-reaction coefficient per ampere
- armature-reaction curve
- shunt, series, or compound nonlinear workflows

## Required Data

For nonlinear analysis, the user must provide:

- `magnetization_curve`
- `field_turns`
- `armature_reaction_mmf`

Where:

- `field_turns` is the number of shunt-field turns `N_F`
- `armature_reaction_mmf` is a fixed demagnetizing MMF in ampere-turns

Important rule:

- nonlinear analysis requires OCC data
- `magnetization_curve` remains optional for the machine in general, but it is
  mandatory for nonlinear armature-reaction methods

## Physics Model

For the separately excited machine:

1. compute actual field current:
   - `If = Vf / Rf`
2. compute field MMF:
   - `F_field = N_F * If`
3. use the user-supplied demagnetizing MMF:
   - `F_ar = armature_reaction_mmf`
4. compute net MMF:
   - `F_net = F_field - F_ar`
5. compute equivalent field current:
   - `If* = F_net / N_F`
6. obtain induced emf from OCC at machine speed:
   - `E_A = OCC(If*, n_m)`

Since `MagnetizationCurve.emf_from_field_current(...)` already scales with
speed, step 6 can reuse that directly.

For the first version, a machine with effective compensating windings can be
represented by setting:

- `armature_reaction_mmf = 0.0`

This lets the same nonlinear helper workflow cover both:

- compensated operation: no demagnetizing armature reaction
- uncompensated operation: fixed demagnetizing MMF provided explicitly

## Constructor-Level Additions

Add optional fields to `dc_machine/base.py`:

- `field_turns: float | None = None`
- `armature_reaction_mmf: float | None = None`

Validation:

- if provided, `field_turns > 0`
- if provided, `armature_reaction_mmf >= 0`

Store:

- `self.field_turns`
- `self.armature_reaction_mmf`

Update `__str__()` to show, when configured:

- `Field turns:`
- `Armature reaction MMF:`

## Shared Helpers In `base.py`

Add validation helpers:

- `_validate_field_turns() -> None`
- `_validate_armature_reaction_mmf() -> None`

Behavior:

- `_validate_field_turns()` raises if `field_turns` is missing or invalid
- `_validate_armature_reaction_mmf()` raises if `armature_reaction_mmf` is missing or invalid

Add public helper:

- `armature_reaction_mmf_value() -> float`

Behavior:

- validates presence
- returns the configured demagnetizing MMF in ampere-turns

## Nonlinear Helpers In `separately_excited.py`

Extend constructor pass-through with:

- `field_turns`
- `armature_reaction_mmf`

Add these methods:

### 1. `field_mmf(applied_field_voltage: float) -> float`

Purpose:

- compute shunt-field MMF

Formula:

- `F_field = N_F * If`

Requires:

- `field_turns`

### 2. `equivalent_field_current_with_armature_reaction(applied_field_voltage: float) -> float`

Purpose:

- compute equivalent field current after demagnetization

Formula:

- `If* = (N_F * If - F_ar) / N_F`

Requires:

- `field_turns`
- `armature_reaction_mmf`

Error behavior:

- raise `ValueError` if `F_net < 0`
- equivalently if `If* < 0`

Do not clamp to zero.

### 3. `induced_emf_from_equivalent_field_current(equivalent_field_current: float) -> float`

Purpose:

- map equivalent field current to OCC emf at the current machine speed

Requires:

- `magnetization_curve`

Implementation:

- use `self.magnetization_curve.emf_from_field_current(..., desired_speed_rpm=self.speed_rpm)`

### 4. `induced_emf_with_armature_reaction(applied_field_voltage: float) -> float`

Purpose:

- full nonlinear induced-emf helper for the fixed-demagnetization workflow

Requires:

- `magnetization_curve`
- `field_turns`
- `armature_reaction_mmf`

Flow:

1. compute equivalent field current
2. compute emf from OCC at current speed

### 5. `terminal_voltage_from_field_voltage_with_armature_reaction(armature_current: float, applied_field_voltage: float) -> float`

Purpose:

- nonlinear terminal-voltage helper using OCC plus fixed armature reaction

Requires:

- `magnetization_curve`
- `field_turns`
- `armature_reaction_mmf`

Flow:

1. compute induced emf with armature reaction
2. reuse existing `terminal_voltage_from_emf(...)`

### 6. `equivalent_field_current_from_emf(emf: float) -> float`

Purpose:

- inverse OCC helper at the current machine speed
- recover the equivalent field current that would produce a desired induced emf

Requires:

- `magnetization_curve`

Implementation:

- use `self.magnetization_curve.field_current_from_emf(..., desired_speed_rpm=self.speed_rpm)`

### 7. `field_current_required_for_emf_with_armature_reaction(emf: float) -> float`

Purpose:

- determine the actual field current required to produce a desired induced emf
- include the fixed demagnetizing armature-reaction MMF

Requires:

- `magnetization_curve`
- `field_turns`
- `armature_reaction_mmf`

Flow:

1. obtain equivalent field current from inverse OCC
2. convert it back to actual field current by adding the demagnetizing MMF term

Formula:

- `If = If* + F_ar / N_F`

### 8. `field_adjusting_resistance_required_for_field_current(applied_field_voltage: float, field_current: float) -> float`

Purpose:

- determine the required external field-adjusting resistance to obtain a target
  field current from a fixed external field supply

Requires:

- `shunt_resistance`

Formula:

- `R_adj = (V_f / I_f) - R_f`

Error behavior:

- raise `ValueError` if `field_current <= 0`
- raise `ValueError` if the computed `R_adj < 0`

### 9. `field_adjusting_resistance_required_for_emf_with_armature_reaction(emf: float, applied_field_voltage: float) -> float`

Purpose:

- solve the voltage-restoration problem directly
- determine the external field-adjusting resistance required to achieve a target
  induced emf when armature reaction is present

Requires:

- `magnetization_curve`
- `field_turns`
- `armature_reaction_mmf`

Flow:

1. compute required field current for the target emf with armature reaction
2. convert that field current to the required `R_adj`

## OCC Requirement Rule

Nonlinear analysis must require OCC data.

Implementation rule:

- nonlinear methods raise `ValueError` if `magnetization_curve is None`

Suggested error message:

- `ValueError("Nonlinear armature-reaction analysis requires a magnetization curve.")`

## API Rule

Do not change the meaning of the current linear / analytic methods.

Keep unchanged:

- `induced_emf_from_field_voltage(...)`
- `terminal_voltage_from_field_voltage(...)`
- other existing analytic-only methods

Add separate explicit nonlinear helpers instead.

This first nonlinear implementation should be able to support a textbook-style
generator exercise with the following structure:

1. no-load terminal voltage at reduced speed with a given `R_adj`
2. loaded terminal voltage with compensating windings
3. loaded terminal voltage without compensating windings and with a specified fixed armature-reaction MMF
4. conceptual voltage restoration by adjusting excitation
5. quantitative restoration by solving required field current and required `R_adj`

## Docstrings To Update

### `DCMachine`

Mention optional:

- `field_turns`
- `armature_reaction_mmf`

and that they are intended for nonlinear OCC workflows.

### `SeparatelyExcitedMotorGenerator`

Mention that nonlinear OCC analysis is available only when:

- `magnetization_curve`
- `field_turns`
- `armature_reaction_mmf`

are configured.

### New nonlinear helper methods

Each docstring should state:

- units
- physical meaning
- required configuration
- whether OCC data is required

## Minimal Tests Later

Keep them lean.

### `test_01_base_constructor.py`

Add:

1. reject `field_turns <= 0`
2. reject negative `armature_reaction_mmf`

### `test_03_separately_excited.py`

Add only the essentials:

1. `field_mmf(...)`
2. `equivalent_field_current_with_armature_reaction(...)`
3. `induced_emf_with_armature_reaction(...)`
4. `terminal_voltage_from_field_voltage_with_armature_reaction(...)`
5. `equivalent_field_current_from_emf(...)`
6. `field_current_required_for_emf_with_armature_reaction(...)`
7. `field_adjusting_resistance_required_for_field_current(...)`
8. `field_adjusting_resistance_required_for_emf_with_armature_reaction(...)`
9. one missing-OCC error test
10. one negative-net-MMF / negative-equivalent-field-current error test

## Suggested Implementation Order

1. add `field_turns` and `armature_reaction_mmf` to `DCMachine`
2. add validation and `__str__()` support
3. add base validation helpers
4. extend `SeparatelyExcitedMotorGenerator.__init__`
5. add nonlinear MMF and equivalent-field-current helpers
6. add inverse nonlinear OCC helpers for emf restoration
7. add nonlinear OCC EMF helper
8. add nonlinear terminal-voltage helper
9. add field-current / `R_adj` restoration helpers
10. add minimal tests


### Exercise statement to add later

A separately excited dc generator is rated at 172 kW, 430 V, 400 A, and 1800 r/min. A magnetization curve is available.
This machine has the following characteristics:

R_A = 0.05 ohms         V_F = 430 V
R_F = 20 ohms           N_F = 1000 turns per pole
R_adj = 0 to 300 ohms

a) If the variable resistor R_adj in this generator's field circuit is adjusted to 63 ohms, and the genertor's prime
mover is driving it at 1600 r/min, what is this generator's no-load terminal voltage?
b) What would its voltage be if a 360 A load were connected to its terminals? Assume that the generator has compensating
windings.
c) What would its voltage be if a 360 A load were connected to its terminals but the generator does not have compensating
windings? Assume its armature reaction at this load is 450 A-turns.
d) What adjustment could be made to the generator to restore its terminal voltage to the value found in part a?
e) How much field current would be needed to retore the terminal voltage to its no-load value? (Assume that the
machine has compensating windings). What is the required value for te resistor R_adj to accomplish this?
