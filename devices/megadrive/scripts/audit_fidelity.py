"""Independently reload the DIN correction and run strict solid checks.

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
report = {'device': 'megadrive', 'iteration': 14,
          'source_sha256': hashlib.sha256(native.read_bytes()).hexdigest(),
          'module_sha256': {s: hashlib.sha256((REPO / s).read_bytes()).hexdigest() for s in modules},
          'checks': checks, 'strict_brep_errors': errors, 'contact_centres_mm': centres,
          'passed': all(checks.values()), 'factory_match_verified': False}
(OUT / 'reports/fidelity_geometry.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
App.closeDocument(doc.Name)
raise SystemExit(0 if report['passed'] else 1)
