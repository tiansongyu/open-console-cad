"""Measure the saved Deck BReps independently of the drawing labels."""
from pathlib import Path
import json,os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App,Part
out=Path(__file__).resolve().parents[1]/'output'
m=json.loads((out/'reports/final_manifest.json').read_text())
doc=App.openDocument(str(out/'SteamDeck_Complete.FCStd'))
c={r['part_id']:doc.getObject(r['name']) for r in m['objects']};checks=[]
def check(name,value,expected,basis='Declared approximate model dimension'):
    row={'name':name,'actual_mm':value,'expected_mm':expected,'basis':basis,'passed':abs(value-expected)<1e-5};checks.append(row);assert row['passed'],row
b=Part.makeCompound([o.Shape for o in c.values() if o.Assembly in m['handheld_groups']]).optimalBoundingBox(False,False)
for axis,expected in zip(['XLength','YLength','ZLength'],[298,117,49]):check('complete_handheld.'+axis,getattr(b,axis),expected,'Valve published complete envelope including controls')
for key,axis,expected in [('DisplayGlass','XLength',150.77),('DisplayGlass','YLength',94.23),('TrackpadSurface-1','XLength',32.5),('TrackpadSurface-1','YLength',32.5),('TrackpadSurface1','XLength',32.5),('StickCap1','XLength',16.4),('ButtonA','XLength',8.0),('DPad','XLength',19),('USBTypeCShell','XLength',9.0),('USBTypeCShell','ZLength',3.7),('HeadphoneSocket','XLength',5.0),('SSDPCB','XLength',22),('SSDPCB','YLength',30),('SSDPCB','ZLength',.6),('BatteryPouch','XLength',107),('BatteryPouch','YLength',88.2),('BatteryPouch','ZLength',8.4),('FanHousing','XLength',52),('FinBase','XLength',63),('Heatpipe','ZLength',1.96),('AdapterBody','XLength',52),('AdapterBody','YLength',46),('AdapterBody','ZLength',27)]:
    check(key+'.'+axis,getattr(c[key].Shape.optimalBoundingBox(False,False),axis),expected,'7-inch 16:10 geometric conversion' if key=='DisplayGlass' else 'Declared approximate model dimension')
r=json.loads((out/'reports/drawing_checks.json').read_text());r['model_measurements']=checks;r['pass']=all(x['passed'] for x in checks) and all(d['value_mm']>0 for d in r['dimensions'])
(out/'reports/drawing_checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(dict(passed=r['pass'],model_measurements=len(checks),annotations=len(r['dimensions']))))
App.closeDocument(doc.Name)
