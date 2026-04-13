import sys
from pathlib import Path

DC_MACHINE_DIR = Path(__file__).resolve().parents[1]  # .../dc_machine
if str(DC_MACHINE_DIR) not in sys.path:
    sys.path.insert(0, str(DC_MACHINE_DIR))
