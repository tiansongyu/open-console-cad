"""Read saved HVC-001 mating grids and photo-fitted exterior features."""
import hashlib
import json
import os
from pathlib import Path
import sys
sys.path.insert(0, os.environ.get('PATH_TO_FREECAD_LIBDIR', ''))
import FreeCAD as App
import Part

root = Path(__file__).resolve().parents[1]
source = root / 'output/Famicom_Complete.FCStd'
doc = App.openDocument(str(source))
parts = {o.PartID: o for o in doc.Objects if getattr(o, 'PhysicalPart', False)}
profile = json.loads(doc.getObject('StudyInfo').ProfileJSON)
checks = []


def check(name, actual, expected, basis):
    passed = abs(actual-expected) < 1e-5 if isinstance(expected, (float, int)) else actual == expected
    checks.append(dict(name=name, actual=actual, expected=expected, basis=basis, passed=passed))


def box(key):
    return parts[key].Shape.optimalBoundingBox(False, False)


body = Part.makeCompound([o.Shape for o in parts.values() if o.Assembly in profile['envelope_groups']]).optimalBoundingBox(False, False)
for axis, expected in zip('XYZ', (150., 220., 60.)):
    check('body.'+axis+'_mm', getattr(body, axis+'Length'), expected, 'Nintendo original body specification; loose accessories and cables excluded')
for row in range(2):
    centers = [box('CardContact'+str(row*30+i)).Center.x for i in range(30)]
    check('reader.row%d_pitch_mm' % row, (centers[-1]-centers[0])/29, 2.54, 'Famicom-compatible hardware and GPM-02 footprint')
    check('reader.row%d_span_mm' % row, centers[-1]-centers[0], 73.66, '29 intervals at 2.54 mm')
for face in ('Front', 'Rear'):
    centers = [box('GamePakContact'+face+str(i)).Center.x for i in range(30)]
    check('cartridge.'+face+'_pitch_mm', (centers[-1]-centers[0])/29, 2.54, 'Famicom-compatible card edge')
slab = Part.makeBox(200, 200, .05, App.Vector(-100, -100, 14.7))
rows = [parts['CardContact'+str(i)].Shape.common(slab).BoundBox.Center.y for i in (0, 30)]
check('reader.solder_row_gap_mm', rows[1]-rows[0], 5.08, 'GPM-02 reconstruction footprint')
for row, count in ((0, 8), (1, 7)):
    centers = [box('ExpansionPin'+str(row*8+i)).Center for i in range(count)]
    check('expansion.row%d_pitch_mm' % row, (centers[-1].x-centers[0].x)/(count-1), 2.77,
          'Compatible DA-15 nominal mating grid; OEM tolerance unverified')
check('expansion.row_gap_mm', box('ExpansionPin0').Center.z-box('ExpansionPin8').Center.z, 2.84, 'Compatible DA-15 nominal grid')
check('expansion.center_x_mm', box('ExpansionMetalRim').Center.x, 16.5, 'Official photograph fit; not a factory datum')
# Count actual openings through the continuous rear-field material at Z=40.
states = [not parts['UpperShell'].Shape.isInside(App.Vector(-32+i*.25, 94, 40), 1e-7, True) for i in range(257)]
openings = sum(opened and (i == 0 or not states[i-1]) for i, opened in enumerate(states))
check('rear_field.through_openings', openings, 13, 'Nintendo original-console photograph')
for name, x in [('power', -55), ('reset', 55)]:
    line = Part.makeLine(App.Vector(x, -70, 45), App.Vector(x, -70, 56))
    top = max(v.Point.z for v in line.common(parts['UpperShell'].Shape).Vertexes)
    check(name+'.recess_top_mm', top, 52.5, 'Fitted 0.5 mm control-field recess')
check('protective_cap_present', 'ExpansionDustCap' in parts, True, 'Removable red cap visible in Nintendo hero photograph')
check('protective_cap_separate_display', parts['ExpansionDustCap'].Assembly, 'Accessories', 'Documented detached presentation')
check('dc_plug.outer_diameter_mm', box('AdapterPlugMetal').YLength, 5.5, 'Famicom-compatible DC connector')
dc_cylinders = [f.Surface.Radius*2 for f in parts['AdapterPlugMetal'].Shape.Faces if isinstance(f.Surface, Part.Cylinder)]
check('dc_plug.bore_diameter_mm', min(dc_cylinders), 2.1, 'Famicom-compatible DC connector')
check('rf_jack.outer_diameter_mm', box('RFJackSleeve').XLength, 8.3, 'Compatible manufacturer RCA jack drawing')
check('rf_plug.pin_diameter_mm', box('RFPlugPin').YLength, 3.2, 'Within RCP-02 manufacturer 3.25 +0/-0.15 mm range')
check('rf_plug.pin_projection_mm', box('RFPlugPin').XMax-box('RFPlugSleeve').XMax, 8., 'Compatible RCA plug drawing')
invalid = [key for key, obj in parts.items() if obj.Shape.isNull() or not obj.Shape.isValid() or not obj.Shape.Solids]
report = dict(device='famicom', iteration=17, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              physical_components=len(parts), checks=checks, invalid_components=invalid,
              passed=not invalid and all(row['passed'] for row in checks), factory_equivalence_verified=False,
              method='Saved BRep bounds, sections and material-point classification; fitted coordinates are model targets, not factory tolerances')
(root/'output/reports/fidelity_detail_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(report))
App.closeDocument(doc.Name)
raise SystemExit(0 if report['passed'] else 1)
