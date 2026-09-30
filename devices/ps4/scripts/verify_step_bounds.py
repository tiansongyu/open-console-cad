"""Read-only regression checks for the PS4 trimmed-shell STEP bound discrepancy.

Run with the matching FreeCAD AppRun Python runtime.
"""
import os,sys,json
from pathlib import Path
repo=Path(__file__).resolve().parents[3]
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''));sys.path.insert(0,str(repo/'tools'))
import FreeCAD as App,Part
from cadlib.step_geometry import compare_solids
out=repo/'devices/ps4/output';d=App.openDocument(str((out/'PlayStation4_Complete.FCStd').resolve()));x=next(o.Shape.copy() for o in d.Objects if getattr(o,'PhysicalPart',False) and getattr(o,'PartID','')=='DS4Back');y=Part.read(str(out/'PlayStation4_FullKit.step')).Solids[645]
rows=[]
for name,a,b,expected in [('actual_trimmed_shell',x,y,True),('identical_box',Part.makeBox(10,10,10),Part.makeBox(10,10,10),True),('translated_box',Part.makeBox(10,10,10),Part.makeBox(10,10,10,App.Vector(.01,0,0)),False),('same_bounds_missing_material',Part.makeBox(10,10,10),Part.makeBox(10,10,10).cut(Part.makeCylinder(1,5,App.Vector(5,5,6))),False)]:
 r=compare_solids(a,b);rows.append({'case':name,'expected_acceptance':expected,'check':r,'passed':r['pass']==expected});print(name,r['pass'],expected,flush=True)
j={'passed':all(r['passed'] for r in rows),'cases':rows};(out/'reports/step_geometry_validation.json').write_text(json.dumps(j,indent=2)+'\n');assert j['passed']
