"""Measure the saved LCD Deck against published dimensions and reference features."""
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
file = out / 'SteamDeck_Complete.FCStd'
doc = App.openDocument(str(file.resolve()))
parts = {o.PartID: o for o in doc.Objects if getattr(o, 'PhysicalPart', False)}
checks = []


def check(name, actual, expected, basis):
    checks.append({'name': name, 'actual': actual, 'expected': expected,
                   'basis': basis, 'passed': abs(actual - expected) < 1e-5})


def bounds(key):
    return parts[key].Shape.optimalBoundingBox(False, False)


body = Part.makeCompound([o.Shape for o in parts.values() if o.Assembly != 'Accessories'])
bb = body.optimalBoundingBox(False, False)
for axis, expected in [('XLength', 298), ('YLength', 117), ('ZLength', 49)]:
    check('complete.' + axis, getattr(bb, axis), expected, 'Valve rounded public product specification including controls')
for key, width, height in [('DisplayGlass', 151.7, 95.2), ('DisplaySurround', 173.7, 106.7)]:
    b = bounds(key)
    check(key + '.width', b.XLength, width, 'Valve reference drawing Rev B sheet 2')
    check(key + '.height', b.YLength, height, 'Valve reference drawing Rev B sheet 2')
for side in (-1, 1):
    b = bounds('TrackpadSurface' + str(side))
    check('trackpad' + str(side) + '.x', b.Center.x, side * 105.78, 'Measured reference CAD top-face center')
    check('trackpad' + str(side) + '.y', b.Center.y, 1.337, 'Measured reference CAD top-face center')
for i, side in enumerate((-1, 1)):
    b = bounds('MicrophoneMesh' + str(i))
    check('microphone' + str(i) + '.x', b.Center.x, side * 62, 'Measured reference CAD microphone cylinder')
    check('microphone' + str(i) + '.y', b.Center.y, 53.819, 'Measured reference CAD microphone cylinder')
mic_tools = [o for o in doc.Objects if o.Label.startswith('Dual microphone inlet · tool')]
for i, tool in enumerate(mic_tools):
    check('microphone_aperture' + str(i) + '.diameter', tool.Shape.optimalBoundingBox(False, False).XLength,
          .764, 'Measured physical cylinder; the drawing diameter 2 annotation is accessory keepout')
for key, side in [('SteamKey', -1), ('QuickAccessKey', 1)]:
    b = bounds(key)
    check(key + '.x', b.Center.x, side * 97.655, 'Measured reference CAD key-face center')
    check(key + '.y', b.Center.y, -24.092, 'Measured reference CAD key-face center')
speaker_tools = [o for o in doc.Objects if o.Label.startswith('Staggered front speaker grille · tool')]
for i, tool in enumerate(speaker_tools):
    check('speaker' + str(i) + '.openings', len(tool.Shape.Solids), 10,
          'Valve reference three-row topology, including the longer inner opening')
vents = [o for o in doc.Objects if o.Label.startswith('Eleven centered LCD top exhaust slots · tool')]
if len(vents) == 1:
    check('top_exhaust.openings', len(vents[0].Shape.Solids), 11, 'Valve reference exterior slot count')
    centers = sorted(s.optimalBoundingBox(False, False).Center.x for s in vents[0].Shape.Solids)
    for i, (actual, expected) in enumerate(zip(centers, range(-25, 26, 5))):
        check('top_exhaust.center' + str(i), actual, expected, 'Measured reference CAD 5 mm slot-center pitch')
invalid = [key for key, obj in parts.items() if obj.Shape.isNull() or not obj.Shape.isValid() or not obj.Shape.Solids]
report = {'device': 'steamdeck', 'iteration': 17,
          'source_sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
          'checks': checks, 'invalid_parts': invalid,
          'ambient_sensor_window_present': 'AmbientLightSensorWindow' in parts,
          'reference_feature_tool_counts': {'microphones': len(mic_tools), 'speaker_fields': len(speaker_tools), 'exhaust_fields': len(vents)},
          'factory_equivalence_verified': False,
          'scope': 'Saved BRep consistency with published/measured public-reference facts. Sensor window size, local edge geometry and internal layout remain approximate.'}
report['passed'] = (not invalid and len(mic_tools) == len(speaker_tools) == 2 and len(vents) == 1
                    and report['ambient_sensor_window_present'] and all(c['passed'] for c in checks))
(out / 'reports/fidelity_detail_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
App.closeDocument(doc.Name)
raise SystemExit(0 if report['passed'] else 1)
