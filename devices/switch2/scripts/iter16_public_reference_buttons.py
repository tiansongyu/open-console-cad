from pathlib import Path
import sys,importlib
repo=Path(PROJECT_ROOT).resolve().parents[1]
if str(repo/"tools") not in sys.path:sys.path.insert(0,str(repo/"tools"))
from cadlib import handheld_refinement
importlib.reload(handheld_refinement)
RESULT=handheld_refinement.refine_switch2(globals())
