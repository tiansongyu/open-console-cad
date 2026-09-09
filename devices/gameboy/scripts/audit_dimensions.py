"""Measure saved DMG-01 BReps independently of the drawing annotations."""
from pathlib import Path
import json,os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App,Part
out=Path(__file__).resolve().parents[1]/'output';m=json.loads((out/'reports/final_manifest.json').read_text())
doc=App.openDocument(str(out/'GameBoy_Complete.FCStd'));c={r['part_id']:doc.getObject(r['name']) for r in m['objects']};checks=[]
def check(name,value,expected,basis='Declared approximate model dimension'):
 row={'name':name,'actual_mm':value,'expected_mm':expected,'basis':basis,'passed':abs(value-expected)<1e-5};checks.append(row);assert row['passed'],row
b=Part.makeCompound([o.Shape for o in c.values() if o.Assembly in m['handheld_groups']]).optimalBoundingBox(False,False)
for axis,expected in zip(['XLength','YLength','ZLength'],[90,148,32]):check('complete_handheld.'+axis,getattr(b,axis),expected,'Nintendo nominal Game Boy Classic envelope')
for key,axis,expected in [('DisplayGlass','XLength',47),('DisplayGlass','YLength',43),('DPad','XLength',22),('DPad','YLength',22),('ButtonA','XLength',11.2),('ButtonB','XLength',11.2),('DisplayBezel','XLength',77),('DisplayBezel','YLength',57.5),('CartridgeFront','XLength',57),('CartridgeFront','YLength',65),('Mainboard','XLength',79),('Mainboard','YLength',80),('FrontPCB','XLength',81),('FrontPCB','YLength',127),('BatteryTray','XLength',70),('BatteryTray','YLength',62),('LinkPortShell','YLength',12.4),('LinkPortShell','ZLength',4.8),('SpeakerFrame','XLength',24.4),('CartridgePCB','XLength',51),('CartridgePCB','YLength',58)]:
 check(key+'.'+axis,getattr(c[key].Shape.optimalBoundingBox(False,False),axis),expected,'Nintendo display-area specification' if key=='DisplayGlass' else 'Declared approximate model dimension')
b=Part.makeCompound([c[k].Shape for k in ['AAWrapper0','AACell0','AANegative0','AAPositive0']]).optimalBoundingBox(False,False)
check('AA_cell.XLength',b.XLength,14.3);check('AA_cell.YLength',b.YLength,50.2)
r=json.loads((out/'reports/drawing_checks.json').read_text());r['model_measurements']=checks;r['pass']=all(x['passed'] for x in checks) and all(d['value_mm']>0 for d in r['dimensions'])
(out/'reports/drawing_checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps({'passed':r['pass'],'model_measurements':len(checks),'annotations':len(r['dimensions'])}))
App.closeDocument(doc.Name)
