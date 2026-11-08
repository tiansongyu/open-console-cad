"""Read saved PSP battery and original remote-interface geometry."""
from pathlib import Path
import hashlib
import json
import os
import sys
sys.path.insert(0, os.environ.get('PATH_TO_FREECAD_LIBDIR', ''))
import FreeCAD as App
import Part

root = Path(__file__).resolve().parents[1]
source = root / 'output/PSP1000_Complete.FCStd'
doc = App.openDocument(str(source))
c = {o.PartID: o for o in doc.Objects if getattr(o, 'PhysicalPart', False)}
checks = []


def check(name, actual, expected, basis):
    passed = abs(actual - expected) < 1e-5 if isinstance(expected, (float, int)) else actual == expected
    checks.append(dict(name=name, actual=actual, expected=expected, basis=basis, passed=passed))


b = c['BatteryPouch'].Shape.optimalBoundingBox(False, False)
for axis, expected in zip('XYZ', (36.0, 52.0, 12.5)):
    check('battery.installed_' + axis + '_mm', getattr(b, axis + 'Length'), expected,
          'Sony 2004-10-27 release p.3; approximate envelope excluding projections')
contacts = [o for key, o in c.items() if key.startswith('RemoteContact')]
check('original_HPRM_contact_count', len(contacts), 6, 'Firsthand original PSP remote-interface documentation')
rows = {}
for o in contacts:
    center = o.Shape.optimalBoundingBox(False, False).Center
    rows.setdefault(round(center.z, 5), []).append(center.x)
check('original_HPRM_row_population', sorted(len(row) for row in rows.values()), [3, 3],
      'Original PSP-1000 two-row connector; not PSP-2000 video connector')
check('hold_flag_present', 'HoldIndicator' in c, True, 'Sony original parts guide pp.20-21')
check('hold_flag_state', c['HoldIndicator'].MaterialDescription, 'black', 'Unlocked display state; mechanical flag')
check('memory_access_tint', c['MemoryLED'].MaterialDescription, 'access_orange',
      'Firsthand LED replacement guide; illustrative RGB, not measured chromaticity')
body = Part.makeCompound([o.Shape for o in c.values() if o.Assembly == 'Body']).optimalBoundingBox(False, False)
for axis, expected in zip('XYZ', (170.0, 74.0, 23.0)):
    check('published_body_' + axis + '_mm', getattr(body, axis + 'Length'), expected,
          'Sony body convention excludes maximum projections')
invalid = [key for key, o in c.items() if o.Shape.isNull() or not o.Shape.isValid() or not o.Shape.Solids]
report = dict(device='psp', iteration=16, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              physical_components=len(c), checks=checks, invalid_components=invalid,
              passed=not invalid and all(row['passed'] for row in checks), factory_equivalence_verified=False)
(root / 'output/reports/fidelity_detail_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report))
App.closeDocument(doc.Name)
raise SystemExit(0 if report['passed'] else 1)
