"""Reload saved study and STEP; check validity, bounds and volume, not factory fidelity."""
import sys,os,json,hashlib
from pathlib import Path
if os.environ.get('PATH_TO_FREECAD_LIBDIR'):
 sys.path.insert(0,os.environ['PATH_TO_FREECAD_LIBDIR'])
import FreeCAD as App,Part,Sketcher,Spreadsheet
root=Path(__file__).resolve().parent
f=root/'Switch_Public_Reference_Study.FCStd';d=App.openDocument(str(f.resolve()))
invalid=[o.Name for o in d.Objects if 'Invalid' in o.State]
keys=['FrontV16','FrontCandidate','RearV16','RearCandidate']
source=[d.getObject(k).Shape for k in keys]
step=Part.Shape();step.read(str((root/'Switch_Exterior_Envelopes.step').resolve()))
rows=[]
for name,s,t in zip(keys,source,step.Solids):
 a=s.optimalBoundingBox(False,False);b=t.optimalBoundingBox(False,False)
 bounds=max(abs(getattr(a,k)-getattr(b,k)) for k in ['XMin','XMax','YMin','YMax','ZMin','ZMax'])
 relative=abs(s.Volume-t.Volume)/s.Volume
 rows.append({'name':name,'native_valid':s.isValid(),'step_valid':t.isValid(),'bounds_error_mm':bounds,'volume_relative_error':relative,'passed':s.isValid() and t.isValid() and bounds<.01 and relative<1e-5})
r={'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'native_reloaded':True,'full_recompute_tested':False,'step_sha256':hashlib.sha256((root/'Switch_Exterior_Envelopes.step').read_bytes()).hexdigest(),'exported_envelopes':len(source),'step_solids':len(step.Solids),'checks':rows,'invalid_features':invalid,'scope':'Saved native/STEP validity, volume and bounds; not assembly interference, surface identity or physical-device accuracy','passed':len(step.Solids)==4 and not invalid and all(v['passed'] for v in rows)}
(root/'export-checks.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2));assert r['passed']
