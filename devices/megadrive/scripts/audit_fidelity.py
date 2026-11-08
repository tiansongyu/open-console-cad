"""Independently reload the interface corrections and run strict solid checks.

Run with FreeCAD's Python runtime, optionally passing a candidate output folder.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

sys.path.insert(0, os.environ.get('PATH_TO_FREECAD_LIBDIR', ''))
import FreeCAD as App
import Part

REPO = Path(__file__).resolve().parents[3]
OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO / 'devices/megadrive/output'
native = OUT / 'MegaDrive_Complete.FCStd'
doc = App.openDocument(str(native))
parts = {o.PartID: o for o in doc.Objects if getattr(o, 'PhysicalPart', False)}
manifest = json.loads((OUT / 'reports/final_manifest.json').read_text())
checks = {}
errors = []
for key, obj in parts.items():
    try:
        obj.Shape.check(True)
    except Exception as exc:
        errors.append({'part_id': key, 'error': str(exc)})
checks['strict_saved_brep'] = not errors
checks['component_count'] = len(parts) == 825
checks['manifest_ids'] = set(parts) == {r['part_id'] for r in manifest['objects']}
checks['part_numbers'] = all(parts[r['part_id']].PartNumber == r['part_number']
                             for r in manifest['objects'])
centres = []
for i in range(8):
    bounds = parts['DINPin' + str(i)].Shape.optimalBoundingBox(False, False)
    centres.append([bounds.Center.y + 100, bounds.Center.z - 10])
    checks['pin_diameter_' + str(i)] = (abs(bounds.YLength - 1.5) < 1e-6
                                        and abs(bounds.ZLength - 1.5) < 1e-6)
checks['offset_contact'] = abs(centres[7][0]) < 1e-6 and abs(centres[7][1] - .9) < 1e-6
checks['seven_outer_contacts'] = all(abs(math.hypot(*p) - 4.25) < 1e-6 for p in centres[:7])
bounds = parts['DINShield'].Shape.optimalBoundingBox(False, False)
checks['male_barrel_diameter'] = abs(bounds.YLength - 13.2) < 1e-6 and abs(bounds.ZLength - 13.2) < 1e-6
modules = ['tools/cadlib/fidelity_megadrive.py', 'tools/cadlib/megadrive.py',
           'devices/megadrive/scripts/iter14_din8_262_contact_pattern_and_key.py']
if manifest['design_iterations'] >= 15:
    expected_x={'PadPort1Shield':54,'PadPort2Shield':86.5,'HeadphonesBarrel':-86.5,
                'ExtensionPortShield':-29.7,'AVBarrel':-71.3,'PowerDCBarrel':-91.8}
    for key,target in expected_x.items():
        checks[key+'_location']=abs(parts[key].Shape.optimalBoundingBox(False,False).Center.x-target)<1e-6
    for key in ['PadPort1','PadPort2','ExtensionPort','PadPlug']:
        rows=[parts[key+'Pin'+str(i)].Shape.optimalBoundingBox(False,False) for i in range(9)]
        axis='y' if key=='PadPlug' else 'x'
        checks[key+'_horizontal_pitch']=all(abs(abs(getattr(b.Center,axis)-getattr(a.Center,axis))-2.77)<1e-6 for a,b in zip(rows[:5],rows[1:5]))
        checks[key+'_row_spacing']=all(abs(rows[0].Center.z-b.Center.z-2.84)<1e-6 for b in rows[5:])
        if key in ['ExtensionPort','PadPlug']:
            checks[key+'_female']=all(any(type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Radius-.52)<1e-6 for f in parts[key+'Pin'+str(i)].Shape.Faces) for i in range(9))
    for key in ['PadPort1Shield','PadPort2Shield']:
        b=parts[key].Shape.optimalBoundingBox(False,False)
        checks[key+'_photo_profile']=abs(b.XLength-18.4)<1e-6 and abs(b.ZLength-10)<1e-6
        checks[key+'_black_housing']=parts[key].MaterialDescription=='black'
    for prefix in ['CardLeaf','CartFinger']:
        for side in [-1,1]:
            xs=[parts[prefix+str(side)+'_'+str(i)].Shape.optimalBoundingBox(False,False).Center.x for i in range(32)]
            checks[prefix+str(side)+'_254_pitch']=all(abs(b-a-2.54)<1e-6 for a,b in zip(xs,xs[1:]))
    shell=parts['UpperHousing'].Shape
    def wall_length(x,y0,y1,z):
        return shell.common(Part.makeLine(App.Vector(x,y0,z),App.Vector(x,y1,z))).Length
    for x in [-59,5]:
        checks['old_front_opening_closed_'+str(x)]=wall_length(x,-108,-98,29)>.5
    for x in [54,86.5]:
        checks['new_front_opening_clear_'+str(x)]=wall_length(x,-108,-98,29)<1e-6
    for x in [36,-11,83]:
        checks['old_rear_opening_closed_'+str(x)]=wall_length(x,98,108,30)>.5
    for x in [-29.7,-71.3,-91.8]:
        checks['new_rear_opening_clear_'+str(x)]=wall_length(x,98,108,30)<1e-6
    radii={round(f.Surface.Radius,6) for f in parts['DCPlugBarrel'].Shape.Faces if type(f.Surface).__name__=='Cylinder'}
    checks['DC_plug_55_21']=radii=={2.75,1.05}
    lower=parts['LowerHousing']
    checks['case_overlap_lip']=getattr(lower,'FidelityOverlapLip',False)
    checks['case_seam_baffle']=lower.Shape.isInside(App.Vector(136.7,80,18.2),1e-6,True)
    checks['expansion_access_preserved']=not lower.Shape.isInside(App.Vector(136.7,10,18.2),1e-6,True)
    modules+=['tools/cadlib/fidelity_megadrive_interfaces.py',
              'devices/megadrive/scripts/iter15_official_port_layout_and_matched_interfaces.py']
report = {'device': 'megadrive', 'iteration': manifest['design_iterations'],
          'source_sha256': hashlib.sha256(native.read_bytes()).hexdigest(),
          'module_sha256': {s: hashlib.sha256((REPO / s).read_bytes()).hexdigest() for s in modules},
          'checks': checks, 'strict_brep_errors': errors, 'contact_centres_mm': centres,
          'passed': all(checks.values()), 'factory_match_verified': False}
(OUT / 'reports/fidelity_geometry.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
App.closeDocument(doc.Name)
raise SystemExit(0 if report['passed'] else 1)
