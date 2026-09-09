"""Check declared study dimensions against saved Atari BReps and annotations."""
from pathlib import Path
import os,sys,json,math
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App
import Part

out=Path(__file__).resolve().parents[1]/'output'
m=json.loads((out/'reports/final_manifest.json').read_text())
assert m['envelope_kind']=='approximate' and 'published_envelope_mm' not in m
doc=App.openDocument(str(out/'Atari2600_Complete.FCStd'))
c={r['part_id']:doc.getObject(r['name']) for r in m['objects']};checks=[]
def check(name,value,expected,basis='Declared approximate study dimension'):
 row={'name':name,'actual_mm':value,'expected_mm':expected,'basis':basis,'passed':abs(value-expected)<1e-5}
 checks.append(row);assert row['passed'],row
b=Part.makeCompound([o.Shape for o in c.values() if o.Assembly in m['envelope_groups']]).optimalBoundingBox(False,False)
for axis,value in zip(['XLength','YLength','ZLength'],[346,232.4430001,88.30359058838891]):check('body.'+axis,getattr(b,axis),value,'Model-measured approximate envelope; not a manufacturer specification')
specs=[('Mainboard','XLength',96),('Mainboard','YLength',202),('Mainboard','ZLength',1.6),
 ('CPU','XLength',35.5),('CPU','YLength',14),('RIOT','XLength',50),('TIA','XLength',50),
 ('J1Bottom','XLength',90),('J1Bottom','YLength',90),('J1Bottom','ZLength',2),
 ('J2Bottom','XLength',90),('J2Bottom','YLength',90),
 ('J1PCB','XLength',72),('J1PCB','YLength',70),('J1PCB','ZLength',1.6),
 ('J2PCB','XLength',72),('J2PCB','YLength',70),
 ('CartBack','XLength',82),('CartBack','YLength',98),('CartBack','ZLength',1.6),
 ('Pad1Bottom','XLength',65),('Pad1Bottom','YLength',93),('Pad1PotBase','XLength',24),
 ('AdapterBack','XLength',55),('AdapterBack','YLength',65),('TVBoxBase','XLength',55),('TVBoxBase','YLength',72)]
for key,axis,value in specs:check(key+'.'+axis,getattr(c[key].Shape.optimalBoundingBox(False,False),axis),value)
board=c['Switchboard'].Shape.copy();board.rotate(App.Vector(),App.Vector(1,0,0),-math.degrees(math.atan2(36,67)))
b=board.optimalBoundingBox(False,False)
for axis,value in zip(['XLength','YLength','ZLength'],[284,66,1.6]):check('Switchboard.local.'+axis,getattr(b,axis),value)
report=json.loads((out/'reports/drawing_checks.json').read_text())
assert all(not x['published'] and x['label'].startswith('≈') for x in report['dimensions'])
report['model_measurements']=checks;report['envelope_kind']='approximate'
report['pass']=all(x['passed'] for x in checks) and all(x['value_mm']>0 for x in report['dimensions'])
(out/'reports/drawing_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':report['pass'],'measurements':len(checks),'annotations':len(report['dimensions'])}))
App.closeDocument(doc.Name)
