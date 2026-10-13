"""Independently reload native files and match each STEP solid to its source.

Report matched-solid numerical volume errors separately from geometry acceptance. Compound.Volume is also reported but is not the acceptance
metric: numerical integration over a far-spread compound is position-sensitive.
By default, a solid with > 1e-6 mm3 difference requires empty bidirectional
Boolean differences. This checks geometry instead of accepting mass estimates
alone. Bounding coordinates normally agree within 1e-6 mm. If an extrema
estimate differs, empty bidirectional Boolean differences can establish the
same geometry despite the numerical bounding estimate.

Pass --saved-geometry to compare the exact serialized BRep without rebuilding
the feature history. This is useful for export verification; it does not test
parameter edits or replace a separate rebuild audit.
--surface-fallback=PartID,... uses bidirectional surface-distance sampling for
explicitly named parts whose coincident-surface Boolean operations do not
converge. This confirms sampled geometry, not analytical shape equality.
"""
import json
import hashlib
import os
import sys
import time
from pathlib import Path
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
sys.path.insert(0,str(Path(os.environ.get('PATH_TO_FREECAD_LIBDIR','')).parent/'Mod'))
import FreeCAD as App
import Part
import Sketcher
import PartDesign
import Spreadsheet

out=Path(sys.argv[1]).resolve()
recompute='--saved-geometry' not in sys.argv[2:]
surface_fallback=set()
for option in sys.argv[2:]:
    if option.startswith('--surface-fallback='):
        surface_fallback.update(option.split('=',1)[1].split(','))
manifest=json.loads((out/'reports/final_manifest.json').read_text())
result={'native':[],'step':[],'pass':True,'started':time.time(),
        'native_recomputed':recompute,
        'bounding_method':'optimalBoundingBox(False, False), excludes kernel tolerance padding and display triangulation',
        'source_sha256':hashlib.sha256((out/'Switch_Complete.FCStd').read_bytes()).hexdigest(),
        'surface_fallback_part_ids':sorted(surface_fallback),
        'acceptance':{'volume_metric':'reported; geometry acceptance requires Boolean confirmation for differences > 1e-6 mm3','solid_bbox_coordinate_delta_mm':1e-6,
                      'bbox_discrepancy_confirmation':'Empty bidirectional Boolean differences establish geometry when computed extrema estimates differ.',
                      'boolean_confirmation_trigger_mm3':1e-6,'boolean_residual_volume_mm3':1e-6},
        'method':'One-to-one source/STEP solid matching by six bounding coordinates; absolute volume errors summed without cancellation; Boolean difference confirmation for discrepant solids. Compound-level volume estimate retained for transparency.',
        'numerical_reference':'https://dev.opencascade.org/doc/refman/html/class_b_rep_g_prop___gauss.html'}
docs={}
if surface_fallback:
    result['acceptance']['surface_sample_distance']='maximum stored source/STEP BRep tolerance, with a 1e-6 mm floor and a 0.02 mm upper bound'
    result['acceptance']['volume_metric']='reported; discrepant solids require Boolean confirmation, except named parts verified by bidirectional surface samples'
    result['method']+=' Named surface fallbacks check every vertex, seven samples per edge, and trimmed 7x7 UV grids on every face in both directions. Sampling is not an analytical equality proof.'
for filename,key in [('Switch_Complete.FCStd','objects'),('Switch_Exploded.FCStd','exploded_objects')]:
    print('Reloading '+filename,flush=True)
    d=App.openDocument(str(out/filename))
    if recompute:d.recompute()
    docs[key]=d
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
    print(json.dumps(result['native'][-1]),flush=True)

def bbox(s):
    b=s.optimalBoundingBox(False,False)
    return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]

def surface_samples(shape):
    points={}
    def add(point):
        points[tuple(round(v,10) for v in (point.x,point.y,point.z))]=point
    for vertex in shape.Vertexes:add(vertex.Point)
    for edge in shape.Edges:
        if edge.Length<1e-9:continue  # Degenerate pole edges are covered by vertices.
        for i in range(7):
            add(edge.valueAt(edge.FirstParameter+(edge.LastParameter-edge.FirstParameter)*i/6))
    face_counts=[]
    for face in shape.Faces:
        u0,u1,v0,v1=face.ParameterRange
        count=0
        for i in range(7):
            for j in range(7):
                point=face.valueAt(u0+(u1-u0)*(i+.5)/7,v0+(v1-v0)*(j+.5)/7)
                # UV bounds can include holes and regions outside trimmed faces.
                if face.distToShape(Part.Vertex(point))[0]<1e-7:
                    add(point);count+=1
        face_counts.append(count)
    return list(points.values()),face_counts

def confirm_surfaces(a,b):
    source_tolerance=a.getTolerance(1)
    step_tolerance=b.getTolerance(1)
    tolerance=max(1e-6,source_tolerance,step_tolerance)
    if len(a.Faces)!=len(b.Faces):
        return {'pass':False,'reason':'Face counts differ; correspondence requires manual review'}
    remaining=list(b.Faces)
    pairs=[]
    for face in a.Faces:
        bounds=bbox(face)
        index=min(range(len(remaining)),key=lambda i:sum((x-y)**2 for x,y in zip(bounds,bbox(remaining[i]))))
        target=remaining.pop(index)
        pairs.append((face,target))
    directions=[]
    for label,reverse in [('source_to_step',False),('step_to_source',True)]:
        maximum=0.;count=0;face_counts=[]
        for i,(source,target) in enumerate(pairs):
            if reverse:source,target=target,source
            points,grid_counts=surface_samples(source)
            # Restrict to the corresponding exact face: stricter than accepting
            # a nearby point elsewhere on the shell, and avoids global searches.
            maximum=max(maximum,max(target.distToShape(Part.Vertex(point))[0] for point in points))
            count+=len(points);face_counts.extend(grid_counts)
            if (i+1)%20==0:print(label+': '+str(i+1)+' faces',flush=True)
        directions.append({'direction':label,'samples':count,'face_grid_sample_counts':face_counts,'max_distance_mm':maximum,'pass':maximum<=tolerance and tolerance<=.02})
        print(json.dumps({k:v for k,v in directions[-1].items() if k!='face_grid_sample_counts'}),flush=True)
    return {'method':'one-to-one face matching by six bounding coordinates; vertices, seven points per edge, trimmed 7x7 UV grids; bidirectional distances to corresponding exact BRep faces, evaluated at the stored kernel tolerance','source_tolerance_mm':source_tolerance,'step_tolerance_mm':step_tolerance,'acceptance_mm':tolerance,'matched_faces':len(pairs),'directions':directions,'pass':all(r['pass'] for r in directions)}

handheld=[r for r in manifest['objects'] if r['assembly'] in manifest['handheld_groups']]
dock=[r for r in manifest['objects'] if r['assembly'] in ['Dock','DockInternal']]
for filename,rows,key in [('Switch_FullKit.step',manifest['objects'],'objects'),('Switch_Handheld.step',handheld,'objects'),('Switch_Dock.step',dock,'objects'),('Switch_Exploded.step',manifest['exploded_objects'],'exploded_objects')]:
    print('Comparing '+filename,flush=True)
    s=Part.read(str(out/filename))
    print('STEP read: '+str(len(s.Solids))+' solids',flush=True)
    expected_volume=sum(r['volume'] for r in rows)
    native=[(r['part_id'],r['name'],i,x) for r in rows for i,x in enumerate(docs[key].getObject(r['name']).Shape.Solids)]
    remaining=[(i,x,bbox(x)) for i,x in enumerate(s.Solids)]
    checks=[]
    for part_id,name,i,x in native:
        if not remaining:break
        xb=bbox(x)
        q,y,yb=min(remaining,key=lambda kv:sum((a-b)**2 for a,b in zip(xb,kv[2])))
        remaining=[kv for kv in remaining if kv[0]!=q]
        delta=y.Volume-x.Volume
        bd=max(abs(a-b) for a,b in zip(xb,yb))
        check={'name':name,'part_id':part_id,'source_solid':i,'step_solid':q,'bbox_max_delta_mm':bd,'volume_delta_mm3':delta,'valid':y.isValid(),'boolean_confirmation':None,'surface_confirmation':None}
        if part_id in surface_fallback:
            print('Surface confirmation: '+part_id,flush=True)
            check['surface_confirmation']=confirm_surfaces(x,y)
        elif abs(delta)>1e-6 or bd>=1e-6:
            print('Boolean confirmation: '+name+' / '+str(i)+'; delta='+str(delta),flush=True)
            diffs=[x.cut(y),y.cut(x)]
            residuals=[sum(abs(z.Volume) for z in a.Solids) for a in diffs]
            check['boolean_confirmation']={'residual_volumes_mm3':residuals,'valid':all(a.isValid() for a in diffs),'pass':all(a.isValid() for a in diffs) and max(residuals)<1e-6}
        boolean_bounds=check['boolean_confirmation'] is not None and check['boolean_confirmation']['pass']
        check['bbox_confirmation']='empty bidirectional Boolean differences' if bd>=1e-6 and boolean_bounds else None
        check['pass']=check['valid'] and (bd<1e-6 or boolean_bounds) and all(check[k] is None or check[k]['pass'] for k in ['boolean_confirmation','surface_confirmation'])
        checks.append(check)
        if len(checks)%100==0:print('Verified '+str(len(checks))+' solids',flush=True)
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
