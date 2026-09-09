from pathlib import Path
import sys
repo=Path(globals().get('REPOSITORY',Path(__file__).resolve().parents[3]))
if str(repo/'tools') not in sys.path:sys.path.insert(0,str(repo/'tools'))
from cadlib.core import Study
from cadlib.famicom import STAGES
assert 'model' in globals(), 'Run iter01 first in the same FreeCAD namespace'
STAGES[12](model)
