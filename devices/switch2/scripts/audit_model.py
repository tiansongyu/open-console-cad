"""Independent FCStd reload and pairwise physical-component interference audit."""
import argparse
import json
import os
import sys
import time
from pathlib import Path
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App
import Part
import Sketcher

parser=argparse.ArgumentParser()
parser.add_argument('checkpoint')
parser.add_argument('report')
parser.add_argument('output')
parser.add_argument('--threshold',type=float,default=1e-6)
args=parser.parse_args()
started=time.time()
report=json.loads(Path(args.report).read_text())
d=App.openDocument(str(Path(args.checkpoint).resolve()))
d.recompute()
names=[r['name'] for r in report['objects']]
assert len(names)==len(set(names)), 'Duplicate physical objects in component list'
objects=[d.getObject(n) for n in names]
invalid=[{'name':o.Name,'error':o.getStatusString()} for o in d.Objects if 'Invalid' in o.State]
checks=[]
for o,old in zip(objects,report['objects']):
    if o is None:raise AssertionError('Missing physical object')
    s=o.Shape
    checks.append({'name':o.Name,'valid':not s.isNull() and s.isValid(),'solids':len(s.Solids),'volume':s.Volume,'volume_delta':s.Volume-old['volume']})
assert not invalid,invalid
assert all(r['valid'] and r['solids']>0 and abs(r['volume_delta'])<1e-4 for r in checks)
def overlap_box(a,b):
    ext=[min(a.XMax,b.XMax)-max(a.XMin,b.XMin),min(a.YMax,b.YMax)-max(a.YMin,b.YMin),min(a.ZMax,b.ZMax)-max(a.ZMin,b.ZMin)]
    return min(ext)>1e-7
candidates=[]
boxes=[o.Shape.BoundBox for o in objects]
for i in range(len(objects)):
    for j in range(i+1,len(objects)):
        if overlap_box(boxes[i],boxes[j]):candidates.append((i,j))
result={'file':str(Path(args.checkpoint).resolve()),'started':started,'physical_components':len(objects),'document_objects':len(d.Objects),
        'reload_valid':True,'invalid_features':invalid,'component_checks':checks,'candidate_pairs':len(candidates),'checked_pairs':0,'clashes':[],'errors':[]}
out=Path(args.output)
print(json.dumps({'state':'auditing','physical_components':len(objects),'candidate_pairs':len(candidates)}),flush=True)
for k,(i,j) in enumerate(candidates,1):
    a,b=objects[i],objects[j]
    try:
        common=a.Shape.common(b.Shape)
        vol=common.Volume
        if vol>args.threshold:
            result['clashes'].append({'a':a.Name,'a_label':a.Label,'b':b.Name,'b_label':b.Label,'volume_mm3':vol})
    except Exception as e:
        result['errors'].append({'a':a.Name,'b':b.Name,'error':str(e)})
    result['checked_pairs']=k
    if k%25==0:
        result['elapsed_seconds']=time.time()-started
        out.write_text(json.dumps(result,ensure_ascii=False,indent=2))
        print(json.dumps({'checked':k,'of':len(candidates),'clashes':len(result['clashes']),'elapsed':result['elapsed_seconds']}),flush=True)
result['elapsed_seconds']=time.time()-started
result['complete']=True
out.write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'state':'done','checked_pairs':len(candidates),'clashes':result['clashes'],'errors':result['errors'],'elapsed':result['elapsed_seconds']},ensure_ascii=False),flush=True)
App.closeDocument(d.Name)
