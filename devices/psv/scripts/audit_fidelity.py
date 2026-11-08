"""Read-only checks of original Vita media dimensions and retained identities."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.environ.get('PATH_TO_FREECAD_LIBDIR', ''))
import FreeCAD as App
import Part

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path)
args = parser.parse_args()
out = args.output or Path(__file__).resolve().parents[1] / 'output'
source = out / 'PSVita_Complete.FCStd'
doc = App.openDocument(str(source.resolve()))
parts = {o.PartID: o for o in doc.Objects if getattr(o, 'PhysicalPart', False)}
profile = json.loads(doc.getObject('StudyInfo').ProfileJSON)
checks = []


def check(name, actual, expected, basis):
    passed = abs(actual - expected) < 1e-5
    checks.append({'name': name, 'actual': actual, 'expected': expected,
                   'basis': basis, 'passed': passed})


for prefix, expected in [('GameCardContact', 10), ('VitaGamePad', 10),
                         ('MemoryCardContact', 9), ('VitaMemoryPad', 9)]:
    check(prefix + '.count', sum(bool(re.fullmatch(prefix + r'\d+', k)) for k in parts),
          expected, 'Primary hardware pinout documentation and game-card teardown')
b = parts['VitaMemoryCard'].Shape.optimalBoundingBox(False, False)
for axis, expected in [('XLength', 15), ('YLength', 12.5), ('ZLength', 1.6)]:
    check('memory_card.' + axis, getattr(b, axis), expected,
          'Sony original memory-card specification: width 15, height 12.5, thickness 1.6 mm')
body = Part.makeCompound([o.Shape for o in parts.values() if o.Assembly == 'Body'])
b = body.optimalBoundingBox(False, False)
for axis, expected in [('XLength', 182), ('YLength', 83.5), ('ZLength', 18.6)]:
    check('body.' + axis, getattr(b, axis), expected, 'Sony published body envelope excluding projections')
baseline = profile['part_number_baseline']
retired = set(profile['retired_part_ids'])
reserved = set(profile['retired_part_numbers'])
mismatches = [k for k, n in baseline.items() if k not in retired and parts[k].PartNumber != n]
numbers = [o.PartNumber for o in parts.values()]
identity_pass = not mismatches and not retired.intersection(parts) and not reserved.intersection(numbers) and len(set(numbers)) == len(numbers)
invalid = [k for k, o in parts.items() if o.Shape.isNull() or not o.Shape.isValid() or not o.Shape.Solids]
report = {'device': 'psv', 'iteration': 16,
          'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'checks': checks, 'invalid_parts': invalid,
          'part_identity': {'passed': identity_pass, 'baseline_components': len(baseline),
                            'preserved_existing_numbers': len(baseline) - len(retired),
                            'retired_part_ids': sorted(retired), 'retired_part_numbers': sorted(reserved),
                            'mismatches': mismatches},
          'access_indicator_present': 'GameCardAccessLens' in parts,
          'factory_equivalence_verified': False,
          'scope': 'Saved BRep envelope, contact counts and traceable identity; no electrical or manufacturing certification'}
report['passed'] = identity_pass and not invalid and report['access_indicator_present'] and all(x['passed'] for x in checks)
(out / 'reports/fidelity_detail_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
App.closeDocument(doc.Name)
raise SystemExit(0 if report['passed'] else 1)
