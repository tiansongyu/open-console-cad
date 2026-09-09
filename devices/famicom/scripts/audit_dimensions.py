"""Measure the saved HVC-001 BReps independently of drawing annotations."""
from pathlib import Path
import json,os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App,Part
out=Path(__file__).resolve().parents[1]/'output';m=json.loads((out/'reports/final_manifest.json').read_text())
doc=App.openDocument(str(out/'Famicom_Complete.FCStd'));c={r['part_id']:doc.getObject(r['name']) for r in m['objects']};checks=[]
def check(name,value,expected,basis='Declared approximate model dimension'):
 row={'name':name,'actual_mm':value,'expected_mm':expected,'basis':basis,'passed':abs(value-expected)<1e-5};checks.append(row);assert row['passed'],row
b=Part.makeCompound([o.Shape for o in c.values() if o.Assembly in m['envelope_groups']]).optimalBoundingBox(False,False)
for axis,expected in zip(['XLength','YLength','ZLength'],[150,220,60]):check('console_body.'+axis,getattr(b,axis),expected,'Nintendo original-manual HVC-001 body envelope; external cables excluded')
for key,axis,expected in [('Mainboard','XLength',104),('Mainboard','YLength',137),('Mainboard','ZLength',1.6),('PowerRFBoard','XLength',96),('PowerRFBoard','YLength',57),('CardSocket','XLength',82),('CardSocket','YLength',11.2),('CardSocket','ZLength',12),('P1Back','YLength',126),('P1Back','ZLength',52),('P2Back','YLength',126),('P2Back','ZLength',52),('P1PCB','YLength',121),('P1PCB','ZLength',47.2),('P2PCB','YLength',121),('P2PCB','ZLength',47.2),('CPU','XLength',49),('CPU','YLength',14),('PPU','XLength',49),('GamePakBack','XLength',108),('GamePakBack','YLength',72),('AdapterShell','XLength',63),('AdapterShell','YLength',49),('RFSwitchBack','XLength',56),('RFSwitchBack','YLength',44)]:
 check(key+'.'+axis,getattr(c[key].Shape.optimalBoundingBox(False,False),axis),expected)
r=json.loads((out/'reports/drawing_checks.json').read_text());r['model_measurements']=checks;r['pass']=all(x['passed'] for x in checks) and all(d['value_mm']>0 for d in r['dimensions'])
(out/'reports/drawing_checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':r['pass'],'model_measurements':len(checks),'annotations':len(r['dimensions'])}))
App.closeDocument(doc.Name)
