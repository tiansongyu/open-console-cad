"""Independently measure the revised VCS card edge in saved native geometry."""
import hashlib
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, os.environ.get('PATH_TO_FREECAD_LIBDIR', ''))
import FreeCAD as App
import Part

REPO = Path(__file__).resolve().parents[3]
OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO/'devices/atari2600/output'
native = OUT/'Atari2600_Complete.FCStd'
doc = App.openDocument(str(native))
parts = {o.PartID:o for o in doc.Objects if getattr(o,'PhysicalPart',False)}
manifest = json.loads((OUT/'reports/final_manifest.json').read_text())
checks, failures, pitch_rows = {}, [], {}
for key,obj in parts.items():
    try:
        obj.Shape.check(True)
    except Exception as exc:
        failures.append({'part_id':key,'error':str(exc)})
checks['strict_saved_brep'] = not failures
checks['component_count'] = len(parts) == 684
checks['manifest_ids'] = set(parts) == {r['part_id'] for r in manifest['objects']}
checks['manifest_numbers'] = all(parts[r['part_id']].PartNumber==r['part_number'] for r in manifest['objects'])
for row in range(2):
    xs = [parts['CartridgeContact'+str(row*12+i)].Shape.optimalBoundingBox(False,False).Center.x for i in range(12)]
    pitch_rows['reader_'+str(row)] = xs
    checks['reader_pitch_'+str(row)] = all(abs(b-a-2.54)<1e-6 for a,b in zip(xs,xs[1:]))
for side in ['Front','Back']:
    bounds = [parts['CartContact'+side+str(i)].Shape.optimalBoundingBox(False,False) for i in range(12)]
    xs = [b.Center.x for b in bounds]
    pitch_rows['cartridge_'+side] = xs
    checks['cartridge_pitch_'+side] = all(abs(b-a-2.54)<1e-6 for a,b in zip(xs,xs[1:]))
    checks['finger_size_'+side] = all(abs(b.XLength-1.524)<1e-6 and abs(b.YLength-6.35)<1e-6 for b in bounds)
    checks['contact_span_'+side] = abs(xs[-1]-xs[0]-27.94)<1e-6
probe = Part.makeBox(100,.2,2,App.Vector(-310,-205.1,8.8))
tab = parts['CartPCB'].Shape.common(probe)
checks['mating_tab_width'] = not tab.isNull() and abs(tab.optimalBoundingBox(False,False).XLength-32.512)<1e-6
for index in range(2):
    upper=[parts['ControllerPin'+str(index)+'_'+str(i)].Shape.optimalBoundingBox(False,False) for i in range(5)]
    lower=[parts['ControllerPin'+str(index)+'_'+str(i)].Shape.optimalBoundingBox(False,False) for i in range(5,9)]
    checks['rear_five_upper_'+str(index)]=all(abs(b.ZMax-upper[0].ZMax)<1e-6 for b in upper) and all(abs(upper[0].ZMax-b.ZMax-2.84)<1e-6 for b in lower)
    checks['rear_contact_pitch_'+str(index)]=all(abs(abs(b.Center.x-a.Center.x)-2.77)<1e-6 for a,b in zip(upper,upper[1:]))
    b=parts['ControllerSurround'+str(index)].Shape.optimalBoundingBox(False,False)
    checks['rear_surround_width_'+str(index)]=abs(b.XLength-24)<1e-6
for prefix,upper_id,lower_id in [('J1PlugContact',1,6),('J2PlugContact',1,6),('PaddlePlugContact',3,7)]:
    a=parts[prefix+str(upper_id)].Shape.optimalBoundingBox(False,False).Center.z
    b=parts[prefix+str(lower_id)].Shape.optimalBoundingBox(False,False).Center.z
    checks[prefix+'_keying']=abs(a-b-2.84)<1e-6
for nose,body in [('J1PlugNose','J1PlugBody'),('J2PlugNose','J2PlugBody'),('PaddlePlugNose','PaddlePlugBody')]:
    a=parts[nose].Shape.optimalBoundingBox(False,False)
    b=parts[body].Shape.optimalBoundingBox(False,False)
    checks[nose+'_assembly_position']=abs(a.XMin-b.XMax-.2)<1e-6
checks['fuji_word_alignment']=abs(parts['FujiMark'].Shape.optimalBoundingBox(False,False).Center.x-parts['AtariWord'].Shape.optimalBoundingBox(False,False).Center.x)<1e-6
invalid = [o.Name for o in doc.Objects if 'Invalid' in o.State]
checks['native_feature_states'] = not invalid
modules = ['tools/cadlib/fidelity_atari2600.py','tools/cadlib/atari2600.py',
           'devices/atari2600/scripts/iter24_verified_254_cartridge_pitch_and_mating_tab.py']
report = {'device':'atari2600','iteration':24,'source_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),
          'module_sha256':{p:hashlib.sha256((REPO/p).read_bytes()).hexdigest() for p in modules},
          'checks':checks,'strict_brep_errors':failures,'invalid_features':invalid,
          'contact_centres_x_mm':pitch_rows,'factory_match_verified':False,'passed':all(checks.values())}
(OUT/'reports/fidelity_geometry.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
App.closeDocument(doc.Name)
raise SystemExit(0 if report['passed'] else 1)
