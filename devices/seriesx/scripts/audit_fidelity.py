"""Reload and check the original vent grid and interface contact correction."""
import hashlib
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, os.environ.get('PATH_TO_FREECAD_LIBDIR', ''))
import FreeCAD as App

REPO = Path(__file__).resolve().parents[3]
OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO / 'devices/seriesx/output'
native = OUT / 'XboxSeriesX_Complete.FCStd'
doc = App.openDocument(str(native))
parts = {o.PartID: o for o in doc.Objects if getattr(o, 'PhysicalPart', False)}
manifest = json.loads((OUT / 'reports/final_manifest.json').read_text())
checks, failures = {}, []
for key, obj in parts.items():
    try:
        obj.Shape.check(True)
    except Exception as exc:
        failures.append({'part_id': key, 'error': str(exc)})
checks['strict_saved_brep'] = not failures
checks['component_count'] = len(parts) == 1104
checks['manifest_ids'] = set(parts) == {r['part_id'] for r in manifest['objects']}
checks['manifest_part_numbers'] = all(parts[r['part_id']].PartNumber == r['part_number']
                                      for r in manifest['objects'])
green = [o for k, o in parts.items() if k.startswith('GreenVent')]
checks['green_layers_144'] = len(green) == 144
xs = sorted({round(o.Shape.BoundBox.Center.x, 5) for o in green})
ys = sorted({round(o.Shape.BoundBox.Center.y, 5) for o in green})
checks['grid_12_by_12'] = len(xs) == len(ys) == 12
checks['grid_symmetry'] = all(abs(a+b) < 1e-6 for a, b in zip(xs, reversed(xs)))
hole_faces = [f for f in parts['TopGrille'].Shape.Faces
              if type(f.Surface).__name__ == 'Cylinder' and abs(f.Surface.Radius-5) < 1e-6]
checks['144_cylindrical_10mm_holes'] = len(hole_faces) == 144
contact_counts = {}
for key, count in [('FrontUSB',9), ('RearUSB1',9), ('RearUSB2',9), ('Ethernet',8), ('HDMI',19)]:
    prefix = key+'Contact'
    contacts = [o for k, o in parts.items() if k.startswith(prefix) and k[len(prefix):].isdigit()]
    contact_counts[key] = len(contacts)
    checks[key+'_contact_count'] = len(contacts) == count
for key in ['RearUSB1', 'RearUSB2']:
    b = parts[key+'Tongue'].Shape.optimalBoundingBox(False, False)
    checks[key+'_tongue_orientation'] = b.ZLength > 10 and b.XLength < 1.3
hdmi_faces = [parts['HDMIContact'+str(i)].Shape.BoundBox.Center.x for i in range(19)]
checks['hdmi_opposed_10_and_9'] = (sum(x > 13 for x in hdmi_faces) == 10
                                  and sum(x < 13 for x in hdmi_faces) == 9)
spherical_faces = [f for f in parts['RearPanel'].Shape.Faces
                   if type(f.Surface).__name__ == 'Sphere' and abs(f.Surface.Radius-.65) < 1e-6]
checks['rear_tactile_13_dots'] = len(spherical_faces) == 13
modules = ['tools/cadlib/fidelity_seriesx.py', 'tools/cadlib/seriesx.py',
           'devices/seriesx/scripts/iter20_original_144_exhaust_holes_and_tactile_ports.py']
report = {'device':'seriesx', 'iteration':20,
          'source_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),
          'module_sha256':{p:hashlib.sha256((REPO/p).read_bytes()).hexdigest() for p in modules},
          'checks':checks, 'strict_brep_errors':failures,
          'top_hole_faces':len(hole_faces), 'contact_counts':contact_counts,
          'grid_x_coordinates_mm':xs, 'grid_y_coordinates_mm':ys,
          'factory_match_verified':False, 'passed':all(checks.values())}
(OUT/'reports/fidelity_geometry.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
App.closeDocument(doc.Name)
raise SystemExit(0 if report['passed'] else 1)
