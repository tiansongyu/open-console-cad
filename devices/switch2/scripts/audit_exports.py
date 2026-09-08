"""Independently reload native files and match each STEP solid to its source.

Report matched-solid numerical volume errors separately from geometry acceptance. Compound.Volume is also reported but is not the acceptance
metric: numerical integration over a far-spread compound is position-sensitive.
Any solid with > 1e-6 mm3 difference additionally requires empty bidirectional
Boolean differences. This checks geometry instead of accepting mass estimates
alone. Bounding coordinates must agree within 1e-6 mm.
"""
import json
import os
import sys
import time
from pathlib import Path
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App
import Part
import Sketcher

out=Path(sys.argv[1]).resolve()
manifest=json.loads((out/'reports/final_manifest.json').read_text())
result={'native':[],'step':[],'pass':True,'started':time.time(),
        'acceptance':{'volume_metric':'reported; geometry acceptance requires Boolean confirmation for differences > 1e-6 mm3','solid_bbox_coordinate_delta_mm':1e-6,
                      'boolean_confirmation_trigger_mm3':1e-6,'boolean_residual_volume_mm3':1e-6},
        'method':'One-to-one source/STEP solid matching by six bounding coordinates; absolute volume errors summed without cancellation; Boolean difference confirmation for discrepant solids. Compound-level volume estimate retained for transparency.',
        'numerical_reference':'https://dev.opencascade.org/doc/refman/html/class_b_rep_g_prop___gauss.html'}
docs={}
for filename,key in [('Switch2_Complete.FCStd','objects'),('Switch2_Exploded.FCStd','exploded_objects')]:
    d=App.openDocument(str(out/filename));d.recompute();docs[key]=d
    rows=manifest[key]
    invalid=[o.Name for o in d.Objects if 'Invalid' in o.State]
    errors=[]
    for row in rows:
        o=d.getObject(row['name'])
        if o is None or o.Shape.isNull() or not o.Shape.isValid() or len(o.Shape.Solids)!=row['solids'] or abs(o.Shape.Volume-row['volume'])>1e-4:
            errors.append(row['name'])
    passed=not invalid and not errors
    result['native'].append({'file':filename,'components':len(rows),'invalid':invalid,'mismatched_components':errors,'pass':passed})
    result['pass'] &= passed

def bbox(s):
    b=s.optimalBoundingBox(False,False)
    return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]

handheld=[r for r in manifest['objects'] if r['assembly'] in manifest['handheld_groups']]
dock=[r for r in manifest['objects'] if r['assembly'] in ['Dock','DockInternal']]
for filename,rows,key in [('Switch2_FullKit.step',manifest['objects'],'objects'),('Switch2_Handheld.step',handheld,'objects'),('Switch2_Dock.step',dock,'objects'),('Switch2_Exploded.step',manifest['exploded_objects'],'exploded_objects')]:
    s=Part.read(str(out/filename))
    expected_volume=sum(r['volume'] for r in rows)
    native=[(r['name'],i,x) for r in rows for i,x in enumerate(docs[key].getObject(r['name']).Shape.Solids)]
    remaining=[(i,x,bbox(x)) for i,x in enumerate(s.Solids)]
    checks=[]
    for name,i,x in native:
        if not remaining:break
        xb=bbox(x)
        q,y,yb=min(remaining,key=lambda kv:sum((a-b)**2 for a,b in zip(xb,kv[2])))
        remaining=[kv for kv in remaining if kv[0]!=q]
        delta=y.Volume-x.Volume
        bd=max(abs(a-b) for a,b in zip(xb,yb))
        check={'name':name,'source_solid':i,'step_solid':q,'bbox_max_delta_mm':bd,'volume_delta_mm3':delta,'valid':y.isValid(),'boolean_confirmation':None}
        if abs(delta)>1e-6:
            diffs=[x.cut(y),y.cut(x)]
            residuals=[sum(abs(z.Volume) for z in a.Solids) for a in diffs]
            check['boolean_confirmation']={'residual_volumes_mm3':residuals,'valid':all(a.isValid() for a in diffs),'pass':all(a.isValid() for a in diffs) and max(residuals)<1e-6}
        check['pass']=check['valid'] and bd<1e-6 and (check['boolean_confirmation'] is None or check['boolean_confirmation']['pass'])
        checks.append(check)
    colors=(out/filename).read_text(errors='ignore').count('COLOUR_RGB(')
    total_abs=sum(abs(r['volume_delta_mm3']) for r in checks)
    passed=s.isValid() and len(s.Solids)==len(native)==len(checks) and all(r['pass'] for r in checks) and colors>0
    entry={'file':filename,'valid':s.isValid(),'solids':len(s.Solids),'expected_solids':len(native),
           'compound_volume_delta_mm3':s.Volume-expected_volume,
           'matched_solid_volume_delta_mm3':sum(r['volume_delta_mm3'] for r in checks),
           'sum_absolute_solid_volume_delta_mm3':total_abs,
           'max_solid_bbox_delta_mm':max(r['bbox_max_delta_mm'] for r in checks),
           'colour_entities':colors,'solid_checks':checks,'pass':passed}
    result['step'].append(entry)
    (out/'reports/export_roundtrip_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    result['pass'] &= passed
    print(json.dumps({k:v for k,v in entry.items() if k!='solid_checks'}),flush=True)
result['elapsed_seconds']=time.time()-result['started']
(out/'reports/export_roundtrip_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'pass':result['pass'],'native':result['native'],'elapsed':result['elapsed_seconds']},ensure_ascii=False),flush=True)
for d in docs.values():App.closeDocument(d.Name)
raise SystemExit(0 if result['pass'] else 1)
