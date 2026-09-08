"""Direct PSP model dimensions, independent of the printed annotation text."""
from pathlib import Path
import json,os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App,Part
root=Path(__file__).resolve().parents[1];out=root/'output'
m=json.loads((out/'reports/final_manifest.json').read_text())
doc=App.openDocument(str(out/'PSP1000_Complete.FCStd'))
c={r['part_id']:doc.getObject(r['name']) for r in m['objects']};checks=[]
def check(name,value,expected,basis='Declared approximate model dimension'):
    row={'name':name,'actual_mm':value,'expected_mm':expected,'basis':basis,'passed':abs(value-expected)<1e-5};checks.append(row);assert row['passed'],row
body=Part.makeCompound([o.Shape for o in c.values() if o.Assembly in m['envelope_groups']]).optimalBoundingBox(False,False)
for axis,expected in zip(['XLength','YLength','ZLength'],[170,74,23]):check('body.'+axis,getattr(body,axis),expected,'Sony body envelope excluding maximum projections')
all_parts=Part.makeCompound([o.Shape for o in c.values() if o.Assembly in m['handheld_groups']]).optimalBoundingBox(False,False)
check('modeled_projection_depth',all_parts.ZLength,23.9)
for key,axis,expected in [('DisplayGlass','XLength',95.19),('DisplayGlass','YLength',53.55),('AnalogCap','XLength',11.7),('ButtonCircle','XLength',8.04),('MiniUSBShell','XLength',8.5),('ChargeJack','XLength',4.76),('MemoryReaderCage','XLength',30),('MemoryReaderCage','YLength',21.5),('BatteryPouch','XLength',30.5),('BatteryPouch','YLength',48),('Mainboard','XLength',123.5),('Mainboard','YLength',62),('MemoryStickCard','XLength',31),('MemoryStickCard','YLength',20),('MemoryStickCard','ZLength',1.6)]:
    check(key+'.'+axis,getattr(c[key].Shape.optimalBoundingBox(False,False),axis),expected,'4.3-inch 16:9 geometric conversion' if key=='DisplayGlass' else 'Declared approximate model dimension')
for key,axis,expected in [('UMDCartridge','XLength',65),('UMDCartridge','YLength',64),('UMDCartridge','ZLength',4.2),('UMDDisc','XLength',60)]:check(key+'.'+axis,getattr(c[key].Shape.optimalBoundingBox(False,False),axis),expected,'Sony published UMD outer size or disc diameter')
r=json.loads((out/'reports/drawing_checks.json').read_text());r['model_measurements']=checks;r['pass']=all(c['passed'] for c in checks) and all(d['value_mm']>0 for d in r['dimensions'])
(out/'reports/drawing_checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(dict(passed=r['pass'],model_measurements=len(checks),annotations=len(r['dimensions']))))
App.closeDocument(doc.Name)
