"""Measure the saved NTR-001 iteration 17; no recompute or document writes."""
from pathlib import Path
import hashlib
import json
import math
import os
import sys
sys.path.insert(0, os.environ.get('PATH_TO_FREECAD_LIBDIR', ''))
import FreeCAD as App
import Part

root = Path(__file__).resolve().parents[1]
source = root / 'output/NintendoDS_Complete.FCStd'
doc = App.openDocument(str(source))
c = {o.PartID: o for o in doc.Objects if getattr(o, 'PhysicalPart', False)}
checks = []


def check(name, actual, expected, basis):
    passed = abs(actual - expected) < 1e-5 if isinstance(expected, (float, int)) else actual == expected
    checks.append(dict(name=name, actual=actual, expected=expected, basis=basis, passed=passed))


stylus = Part.makeCompound([c[k].Shape for k in ('StylusTip', 'StylusBarrel', 'StylusGrip')]).optimalBoundingBox(False, False)
check('stylus.length_mm', stylus.YLength, 75.0, 'Nintendo published approximate length')
check('stylus.maximum_diameter_mm', stylus.XLength, 4.0, 'Nintendo published approximate diameter')
check('left_indicator_role', c['StatusLED0'].MaterialDescription, 'charge_orange', 'Nintendo manual pp.8-9')
check('right_indicator_role', c['StatusLED1'].MaterialDescription, 'led', 'Nintendo manual pp.8-9, normal powered state')
check('indicator_left_to_right', c['StatusLED0'].Shape.BoundBox.Center.x < c['StatusLED1'].Shape.BoundBox.Center.x, True, 'Nintendo component diagram')
for i in range(7):
    s = c['RearCoverScrew' + str(i)].Shape
    b = s.optimalBoundingBox(False, False)
    # At a plane within the drive, check three empty rays interleaved with
    # three intact head sectors. This distinguishes the Y recess from a cross.
    states = []
    for angle in (90, 150, 210, 270, 330, 30):
        a = math.radians(angle)
        point = App.Vector(b.Center.x + .65 * math.cos(a), b.Center.y + .65 * math.sin(a), b.ZMin + .10)
        states.append(s.isInside(point, 1e-7, True))
    check('rear_screw_%d_three_arm_recess' % i, states, [False, True, False, True, False, True], 'Firsthand Y00 rear screw evidence; geometric section test')
invalid = [k for k, o in c.items() if o.Shape.isNull() or not o.Shape.isValid() or not o.Shape.Solids]
report = dict(device='nds', iteration=17, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              checks=checks, invalid_components=invalid,
              passed=not invalid and all(r['passed'] for r in checks), factory_equivalence_verified=False,
              method='Read-only saved BRep, material roles and head-recess point classification')
(root / 'output/reports/fidelity_detail_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report))
App.closeDocument(doc.Name)
raise SystemExit(0 if report['passed'] else 1)
