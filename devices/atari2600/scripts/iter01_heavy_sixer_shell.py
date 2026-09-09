from pathlib import Path
import sys
repo=Path(globals().get('REPOSITORY',Path(__file__).resolve().parents[3]))
if str(repo/'tools') not in sys.path:sys.path.insert(0,str(repo/'tools'))
from cadlib.core import Study
from cadlib.atari2600 import STAGES
model=Study(repo,'atari2600')
STAGES[1](model)
