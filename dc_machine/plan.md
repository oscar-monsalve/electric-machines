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
5. one missing-OCC error test
6. one negative-net-MMF / negative-equivalent-field-current error test

## Suggested Implementation Order

1. add `field_turns` and `armature_reaction_mmf` to `DCMachine`
2. add validation and `__str__()` support
3. add base validation helpers
4. extend `SeparatelyExcitedMotorGenerator.__init__`
5. add nonlinear MMF and equivalent-field-current helpers
6. add nonlinear OCC EMF helper
7. add nonlinear terminal-voltage helper
8. add minimal tests
