"""Refresh manifest and CSV bounds from the delivered native BReps, without editing CAD."""
from pathlib import Path
import csv,hashlib,json,os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App,Part
out=Path(__file__).resolve().parents[1]/'output'
path=out/'reports/final_manifest.json';manifest=json.loads(path.read_text());changes=[];sources={};boxes={}
for filename,key in [('Switch_Complete.FCStd','objects'),('Switch_Exploded.FCStd','exploded_objects')]:
    native=out/filename;sources[filename]=hashlib.sha256(native.read_bytes()).hexdigest();doc=App.openDocument(str(native))
    for row in manifest[key]:
        obj=doc.getObject(row['name']);shape=obj.Shape;assert shape.isValid() and len(shape.Solids)==row['solids']
        b=shape.optimalBoundingBox(False,False);coords=[b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax]
        delta=max(abs(a-b) for a,b in zip(coords,row['bounds']))
        if delta>1e-7:changes.append({'file':filename,'part_id':row['part_id'],'previous_bounds':row['bounds'],'measured_bounds':coords,'max_coordinate_delta_mm':delta,'volume_delta_mm3':shape.Volume-row['volume']})
        row['bounds']=coords
        if key=='objects':boxes[row['part_id']]=[b.XLength,b.YLength,b.ZLength]
    App.closeDocument(doc.Name);assert hashlib.sha256(native.read_bytes()).hexdigest()==sources[filename]
manifest['bounds_basis']='Measured from the saved native BReps with optimalBoundingBox(False, False); refreshed after serialization.'
path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
path=out/'COMPONENTS.csv'
with path.open(encoding='utf-8-sig',newline='') as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
for row in rows:
    for field,value in zip(['X mm','Y mm','Z mm'],boxes[row['Part ID']]):row[field]=str(value)
with path.open('w',encoding='utf-8-sig',newline='') as f:writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(rows)
report={'passed':True,'cad_files_unchanged':True,'source_sha256':sources,'components':len(boxes),'method':'Saved native BRep optimal bounds; replace legacy cached or control-hull measurement records','changed_bounds':changes}
(out/'reports/measurement_refresh.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'components':len(boxes),'changed_bounds':len(changes),'cad_files_unchanged':True}))
