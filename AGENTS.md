# AGENTS.md

## What this repo is
- Educational Python scripts for electric-machines problems (not a packaged app).
- Main domains: `dc_machine/`, `induction_motor/`, `transformer/`, `synchronous_machine/`, `magnetic_circuits/`.

## Ground truth for tooling
- No build system, task runner, CI workflows, lint config, type-check config, or test suite is configured in this repo.
- No root Python manifest/lockfile (`pyproject.toml`, `requirements.txt`, etc.).

## Dependencies
- Install manually: `pip install numpy matplotlib scienceplots`.
- `scienceplots` is required by multiple plotting scripts.

## How to run code
- Run scripts directly, e.g. `python dc_machine/main.py`.
- Prefer direct script execution over `python -m ...`; many files use same-folder imports like `import helpers_ex1` / `from base import DCMachine`.
- There is no single app entrypoint; each exercise script is its own entrypoint.

## Known execution quirks
- `transformer/single_phase/main.py` is interactive (calls `input()` via `regulation_efficiency.py` for load/power-factor values).
- Multiple scripts open plot windows with `plt.show()` (blocking), especially in:
  - `induction_motor/theoretical_model/main.py`
  - `induction_motor/exercises/ex2_torque_speed_curve.py`
  - `synchronous_machine/motor/01_ex1_motor.py`
  - `synchronous_machine/generator/03_gen_isolated.py`
  - `synchronous_machine/parcial_2_maquinas_II/*.py`
  - `transformer/single_phase/main.py`

## Conventions to preserve
- Keep calculations explicit with engineering units in variable names/comments.
- Keep textbook/exercise context near the script (current code relies on in-file problem statements).
