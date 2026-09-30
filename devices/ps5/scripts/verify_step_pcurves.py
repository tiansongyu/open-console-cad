"""Verify PS5 trimmed-fin STEP fidelity and reject displaced or missing material.

Run with the matching FreeCAD AppRun Python environment after the final exports.
"""
import os,sys,json,hashlib
from pathlib import Path
repo=Path(__file__).resolve().parents[3]
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''));sys.path.insert(0,str(repo/'tools'))
import FreeCAD as App,Part
from cadlib.step_geometry import compare_solids,bounds
out=repo/'devices/ps5/output';native=out/'PlayStation5_Complete.FCStd';step=out/'PlayStation5_FullKit.step'
d=App.openDocument(str(native));solids=Part.read(str(step)).Solids;rows=[]
for key in ['CoolingFinMain20','CoolingFinMain21']:
 x=d.getObject(key).Shape.Solids[0];xb=bounds(x)
 y=min(solids,key=lambda s:sum((a-b)**2 for a,b in zip(xb,bounds(s))))
 check=compare_solids(x,y);differences=[x.cut(y),y.cut(x)]
 residuals=[sum(abs(s.Volume) for s in z.Solids) for z in differences]
 samples=[]
 for direction,a,b in [('native_to_step',x,y),('step_to_native',y,x)]:
  surface=Part.makeCompound(b.Faces)
  for deflection in [.01,.005]:
   points,_=a.tessellate(deflection)
   maximum=max(Part.Vertex(p).distToShape(surface)[0] for p in points)
   samples.append(dict(direction=direction,deflection_mm=deflection,sampled_points=len(points),max_surface_distance_mm=maximum,passed=maximum<1e-6))
 area_delta=abs(x.Area-y.Area)
 passed=check['pass'] and len(x.Faces)==len(y.Faces) and area_delta<1e-6 and all(s['passed'] for s in samples)
 rows.append(dict(case=key,expected_acceptance=True,check=check,residual_volumes_mm3=residuals,boolean_results_valid=[z.isValid() for z in differences],surface_area_delta_mm2=area_delta,surface_samples=samples,passed=passed))
 print(key,passed,residuals,flush=True)
x=Part.makeBox(10,10,10)
for name,y,expected in [('identical_box',Part.makeBox(10,10,10),True),('translated_box',Part.makeBox(10,10,10,App.Vector(.01,0,0)),False),('same_bounds_missing_material',x.cut(Part.makeCylinder(1,5,App.Vector(5,5,6))),False)]:
 check=compare_solids(x,y);rows.append(dict(case=name,expected_acceptance=expected,check=check,passed=check['pass']==expected))
r=dict(passed=all(x['passed'] for x in rows),cases=rows,step_has_pcurves='PCURVE(' in step.read_text(),native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),step_sha256=hashlib.sha256(step.read_bytes()).hexdigest(),basis='PS5 finalization explicitly writes trimming pcurves. The two curved pipe-cut fins have unstable invalid Boolean differences at coincident trimmed surfaces. Preserve these raw diagnostics and additionally require matching face counts, surface area within 1e-6 mm2 and bidirectional point-to-surface distance below 1e-6 mm at two tessellation deflections, alongside the unchanged per-solid volume and bounds checks. This is sampled surface verification, not an exact Boolean certificate.')
(out/'reports/step_geometry_validation.json').write_text(json.dumps(r,indent=2)+'\n');App.closeDocument(d.Name);assert r['passed'] and r['step_has_pcurves']
