"""Measure the saved NTR-001 model independently of its drawing labels."""
from pathlib import Path
import json
import os
import sys
sys.path.insert(0, os.environ.get('PATH_TO_FREECAD_LIBDIR', ''))
import FreeCAD as App
import Part

root = Path(__file__).resolve().parents[1]
out = root/'output'
manifest = json.loads((out/'reports/final_manifest.json').read_text())
doc = App.openDocument(str(out/'NintendoDS_Complete.FCStd'))
closed = App.openDocument(str(out/'NintendoDS_Closed.FCStd'))
parts = {r['part_id']: doc.getObject(r['name']) for r in manifest['objects']}
checks = []

def check(name, actual, expected, basis='declared approximate model dimension'):
    row = dict(name=name, actual_mm=actual, expected_mm=expected, basis=basis, passed=abs(actual-expected)<1e-5)
    checks.append(row)
    assert row['passed'], row

bb = Part.makeCompound([closed.getObject(r['name']).Shape for r in manifest['objects'] if r['assembly'] in manifest['handheld_groups']]).optimalBoundingBox(False, False)
for axis, expected in zip(['XLength','YLength','ZLength'], [148.7,84.7,28.9]):
    check('closed.'+axis, getattr(bb,axis), expected, 'Nintendo published NTR-001 closed envelope')
for key in ['UpperGlass','LowerGlass']:
    shape = parts[key].Shape.copy()
    shape.Placement = parts[key].FlatPlacement
    bb = shape.optimalBoundingBox(False, False)
    check(key+'.width', bb.XLength, 60.96, '3-inch diagonal at 4:3, geometric conversion')
    check(key+'.height', bb.YLength, 45.72, '3-inch diagonal at 4:3, geometric conversion')
for key, axis, expected in [('DPad','XLength',19),('GameCardMouth','XLength',36.2),('GBAMouth','XLength',64.4),('ChargeJackShell','XLength',8.4),('Mainboard','XLength',139),('Mainboard','YLength',75),('BatteryPouch','XLength',31),('BatteryPouch','YLength',54),('BatteryDoor','XLength',33),('BatteryDoor','YLength',58)]:
    check(key+'.'+axis, getattr(parts[key].Shape.optimalBoundingBox(False,False),axis), expected)
stylus = Part.makeCompound([o.Shape for o in parts.values() if o.Assembly=='Accessories']).optimalBoundingBox(False,False)
check('stylus.length', stylus.YLength, 75, 'Approximate 75 mm original stylus specification')
report = json.loads((out/'reports/drawing_checks.json').read_text())
report['model_measurements'] = checks
report['pass'] = all(r['passed'] for r in checks) and all(d['value_mm']>0 for d in report['dimensions'])
(out/'reports/drawing_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(dict(passed=report['pass'], model_measurements=len(checks), annotations=len(report['dimensions']))))
App.closeDocument(doc.Name)
App.closeDocument(closed.Name)
