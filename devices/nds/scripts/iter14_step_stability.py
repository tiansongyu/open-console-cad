from pathlib import Path
import sys
repo=Path(globals().get('REPOSITORY',Path(__file__).resolve().parents[3]))
if str(repo/'tools') not in sys.path:sys.path.insert(0,str(repo/'tools'))
from cadlib.core import Study
from cadlib.nds import STAGES
STAGES[14](model)
