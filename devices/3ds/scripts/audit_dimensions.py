"""Direct measurements against published and declared model dimensions."""
from pathlib import Path
import os,sys,json
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App,Part
root=Path(__file__).resolve().parents[1];out=root/'output';m=json.loads((out/'reports/final_manifest.json').read_text())
doc=App.openDocument(str(out/'Nintendo3DS_Complete.FCStd'));closed=App.openDocument(str(out/'Nintendo3DS_Closed.FCStd'))
c={r['part_id']:doc.getObject(r['name']) for r in m['objects']};cc={r['part_id']:closed.getObject(r['name']) for r in m['objects']};checks=[]
def check(name,actual,expected):
 row={'name':name,'actual_mm':actual,'expected_mm':expected,'pass':abs(actual-expected)<1e-5};checks.append(row);assert row['pass'],row
sh=Part.makeCompound([cc[k].Shape for k,o in c.items() if o.Assembly in m['handheld_groups']]);b=sh.optimalBoundingBox(False,False)
for axis,ex in zip(['XLength','YLength','ZLength'],[134,74,21]):check('closed.'+axis,getattr(b,axis),ex)
for key,w,h in [('UpperGlass',76.8,46.08),('LowerGlass',61.44,46.08)]:
 sh=c[key].Shape.copy()
 if key=='UpperGlass':sh.Placement=App.Placement(App.Vector(),App.Rotation(App.Vector(1,0,0),-20)).multiply(sh.Placement)
 b=sh.optimalBoundingBox(False,False);check(key+'.width',b.XLength,w);check(key+'.height',b.YLength,h)
for key,axis,expected in [('CirclePadCap','XLength',13.7),('GameCardMouth','XLength',34.8),('ChargeJackShell','XLength',8.25),('BatteryPouch','XLength',33.6),('BatteryPouch','YLength',52.6),('Mainboard','XLength',126),('Mainboard','YLength',64),('CradleBase','XLength',144),('CradleBase','YLength',84)]:check(key+'.'+axis,getattr(c[key].Shape.optimalBoundingBox(False,False),axis),expected)
report=json.loads((out/'reports/drawing_checks.json').read_text());report['model_measurements']=checks;report['pass']=all(r['pass'] for r in checks) and len(report['dimensions'])==17
(out/'reports/drawing_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'pass':report['pass'],'model_measurements':len(checks),'annotations':len(report['dimensions'])}))
App.closeDocument(doc.Name);App.closeDocument(closed.Name)
