"""Read-only RVL-001/RVL-003 feature checks; image-fit dimensions stay estimates."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.environ.get('PATH_TO_FREECAD_LIBDIR', ''))
import FreeCAD as App
import Part

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path)
args = parser.parse_args()
out = args.output or Path(__file__).resolve().parents[1] / 'output'
source = out / 'Wii_Complete.FCStd'
doc = App.openDocument(str(source.resolve()))
parts = {o.PartID: o for o in doc.Objects if getattr(o, 'PhysicalPart', False)}
profile = json.loads(doc.getObject('StudyInfo').ProfileJSON)
checks = []


def check(name, actual, expected, basis):
    checks.append({'name': name, 'actual': actual, 'expected': expected,
                   'basis': basis, 'passed': abs(actual - expected) < 1e-5})


core = Part.makeCompound([parts[k].Shape for k in ('LowerHousing', 'UpperHousing', 'FrontBezel')])
b = core.optimalBoundingBox(False, False)
check('plastic.width', b.XLength, 157, 'Nintendo horizontal body-axis convention')
check('plastic.depth', b.YLength, 215.4, 'Nintendo horizontal body-axis convention excluding controls')
console = Part.makeCompound([o.Shape for o in parts.values() if o.Assembly in profile['envelope_groups']])
cb = console.optimalBoundingBox(False, False)
vent = [o for o in doc.Objects if o.Label.startswith('RVL-001 five-by-five rear exhaust field · tool')]
for i, tool in enumerate(vent):
    check('rear_grille' + str(i) + '.cells', len(tool.Shape.Solids), 25, 'Nintendo original body diagram, printed pages 26-27')
remote = [o for o in doc.Objects if o.Label.startswith('RVL-003 three-column six-row speaker grille · tool')]
if len(remote) == 1:
    solids = remote[0].Shape.Solids
    check('remote_speaker.holes', len(solids), 18, 'Nintendo RVL-003 manual and original product photograph')
    centers = [s.optimalBoundingBox(False, False).Center for s in solids]
    check('remote_speaker.columns', len(set(round(p.x, 5) for p in centers)), 3, 'Documented hole arrangement')
    check('remote_speaker.rows', len(set(round(p.y, 5) for p in centers)), 6, 'Documented hole arrangement')
z0 = parts['USB0Shell'].Shape.optimalBoundingBox(False, False).Center.z
z1 = parts['USB1Shell'].Shape.optimalBoundingBox(False, False).Center.z
check('usb_pair.center_spacing', z1 - z0, 8.5, 'Image-fit parameter, not a manufacturer connector dimension')
check('rear_lanyard_shell.solids', len(parts['RemoteBack'].Shape.Solids), 1, 'The retaining bridge is integral with the rear molding')
check('front_sd_cover.width', parts['SDFlap'].Shape.optimalBoundingBox(False, False).XLength, 61.5,
      'Original front-image proportion fit; not a factory dimension')
word = parts['WiiFrontMark'].Shape.optimalBoundingBox(False, False)
check('front_wordmark.vertical_orientation', int(word.ZLength > word.XLength), 1,
      'The original upright-console wordmark rotates with the horizontal console')
for key, x, y in [('RemoteDPad', 0, 50), ('RemoteA', 0, 28.5),
                   ('RemoteMinus', -10.5, 3.5), ('RemoteHome', 0, 3.5), ('RemotePlus', 10.5, 3.5),
                   ('RemoteOne', 0, -35.5), ('RemoteTwo', 0, -48.5), ('RemotePower', -9.5, 67),
                   ('RemoteSpeaker', 0, -15)]:
    center = parts[key].Shape.optimalBoundingBox(False, False).Center
    check(key + '.local_x', center.x + 25, x, 'Nintendo original photograph fit; not factory dimensions')
    check(key + '.local_y', center.y + 235, y, 'Nintendo original photograph fit; not factory dimensions')
for i in range(1, 5):
    check('player' + str(i) + '.dot_count', len(parts['RemoteLEDMark' + str(i)].Shape.Solids), i,
          'Original player marking uses one through four outlined dots')
strict = {}
strict_keys = ['LowerHousing', 'UpperHousing', 'FrontBezel', 'RemoteFront', 'RemoteBack', 'RemoteDPad', 'USB1Shell']
strict_keys += ['Remote' + k for k in ('A', 'Minus', 'Home', 'Plus', 'One', 'Two', 'Power')]
strict_keys += ['RemoteWiiMark', 'RemotePowerLegend', 'RemoteHomeLegend'] + ['RemoteLEDMark' + str(i) for i in range(1, 5)]
for key in strict_keys:
    try:
        parts[key].Shape.check(True)
        strict[key] = True
    except Exception as exc:
        strict[key] = str(exc)
invalid = [key for key, obj in parts.items() if obj.Shape.isNull() or not obj.Shape.isValid() or not obj.Shape.Solids]
report = {'device': 'wii', 'iteration': 16,
          'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'checks': checks, 'invalid_parts': invalid, 'strict_changed_breps': strict,
          'sync_parts_present': all(k in parts for k in ('RemoteSyncButton', 'RemoteSyncSwitch')),
          'original_legends_present': all(k in parts for k in ('RemoteWiiMark', 'RemotePowerLegend', 'RemoteHomeLegend')),
          'color_roles': {'av': parts['AVShell'].MaterialDescription,
                          'sensor': parts['SensorSocket'].MaterialDescription},
          'envelope_conventions': {'published_horizontal_mm': [157, 215.4, 44],
                                   'plastic_core_mm': [b.XLength, b.YLength, b.ZLength],
                                   'modeled_console_including_feet_and_controls_mm': [cb.XLength, cb.YLength, cb.ZLength],
                                   'note': 'The inherited model splits Z into 42.5 mm plastic plus 1.5 mm feet. Exact manufacturer protrusion exclusion and local molding remain unverified; this iteration does not rescale that construction.'},
          'factory_equivalence_verified': False,
          'scope': 'Saved geometry, documented feature topology and fitted spacing; no factory-tolerance assertion'}
report['passed'] = (len(vent) == 2 and len(remote) == 1 and not invalid
                    and report['sync_parts_present'] and report['original_legends_present'] and all(v is True for v in strict.values())
                    and report['color_roles'] == {'av': 'black', 'sensor': 'sensor_orange'}
                    and all(c['passed'] for c in checks))
(out / 'reports/fidelity_detail_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
App.closeDocument(doc.Name)
raise SystemExit(0 if report['passed'] else 1)
