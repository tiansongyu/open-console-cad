"""Verify saved Vita dimensions independently of drawing labels."""
from pathlib import Path
import json,os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App,Part
out=Path(__file__).resolve().parents[1]/'output'
m=json.loads((out/'reports/final_manifest.json').read_text())
doc=App.openDocument(str(out/'PSVita_Complete.FCStd'))
c={r['part_id']:doc.getObject(r['name']) for r in m['objects']};checks=[]
def check(name,value,expected,basis='Declared approximate model dimension'):
    row={'name':name,'actual_mm':value,'expected_mm':expected,'basis':basis,'passed':abs(value-expected)<1e-5};checks.append(row);assert row['passed'],row
b=Part.makeCompound([o.Shape for o in c.values() if o.Assembly in m['envelope_groups']]).optimalBoundingBox(False,False)
for axis,expected in zip(['XLength','YLength','ZLength'],[182,83.5,18.6]):check('body.'+axis,getattr(b,axis),expected,'Published body envelope excluding maximum projections')
b=Part.makeCompound([o.Shape for o in c.values() if o.Assembly in m['handheld_groups']]).optimalBoundingBox(False,False);check('modeled_projection_depth',b.ZLength,24.05)
for key,axis,expected in [('DisplayGlass','XLength',110.69),('DisplayGlass','YLength',62.26),('RearTouchPanel','XLength',121),('RearTouchPanel','YLength',58),('StickCap1','XLength',12.4),('ButtonCircle','XLength',7.1),('FrontCameraRing','XLength',3.7),('RearCameraRing','XLength',11.5),('RearCameraRing','YLength',6.8),('MultiPortShell','XLength',20.5),('BatteryPouch','XLength',94),('BatteryPouch','YLength',49),('BatteryPouch','ZLength',4.4),('Mainboard','XLength',113),('Mainboard','YLength',72),('VitaGameCard','XLength',22.5),('VitaGameCard','YLength',30.5),('VitaGameCard','ZLength',1.9),('VitaMemoryCard','XLength',12.5),('VitaMemoryCard','YLength',15),('VitaMemoryCard','ZLength',1.6)]:
    check(key+'.'+axis,getattr(c[key].Shape.optimalBoundingBox(False,False),axis),expected,'5-inch 16:9 geometric conversion' if key=='DisplayGlass' else 'Declared approximate model dimension')
r=json.loads((out/'reports/drawing_checks.json').read_text());r['model_measurements']=checks;r['pass']=all(x['passed'] for x in checks) and all(d['value_mm']>0 for d in r['dimensions'])
(out/'reports/drawing_checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(dict(passed=r['pass'],model_measurements=len(checks),annotations=len(r['dimensions']))))
App.closeDocument(doc.Name)
