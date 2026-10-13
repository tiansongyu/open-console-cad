"""Build an isolated exterior study in the FreeCAD GUI from retained V16 history.

Run with exec(compile(path.read_bytes(), str(path), 'exec'), {'__file__': str(path)}).
The solids are exterior envelopes, NOT hollow production shells or replacements
for the verified assembly. The loft uses unequal outer/rail-side edge setbacks.
"""
from pathlib import Path
import hashlib
import json
import math
import FreeCAD as App
import FreeCADGui as Gui
import Part

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'output/Switch_Complete.FCStd'
helper = {'__file__': str(ROOT / 'scripts/cad_base.py'),
          'PROJECT_ROOT': str(ROOT), 'PROJECT_OUTPUT': str(HERE), 'Gui': Gui}
exec(compile((ROOT / 'scripts/cad_base.py').read_bytes(), 'cad_base.py', 'exec'), helper)
vec = App.Vector
source = next((d for d in App.listDocuments().values()
               if Path(d.FileName).resolve() == SOURCE.resolve()), None)
owned = source is None
if owned:
    source = App.openDocument(str(SOURCE))
name = 'Switch_Public_Reference_Study'
if name in App.listDocuments():
    raise RuntimeError('Close the existing study before rebuilding it.')
doc = App.newDocument(name)
doc.Label = 'Switch · 公开资料外缘校准样件（非装配）'
params = doc.addObject('Spreadsheet::Sheet', 'ReferenceParameters')
params.Label = '拟合参数 · 需运行源码重建'
for row, (label, value, basis) in enumerate([
    ('Shell width', 33, 'V16 housing, excluding rail'),
    ('Shell height', 102, 'V16 envelope retained'),
    ('Plan radius', 20.5, 'V16 retained; photo fit approx. 21.2'),
    ('Front outer setback', 3.5, 'D819642 Fig.3 image estimate'),
    ('Rear outer setback', 6.0, 'D819642 Fig.4 image estimate'),
    ('Rail-side setback', .65, 'Narrow rail edge; approximate'),
    ('Face button diameter', 7.6, 'Photo approx.7.7; patent approx.7.5'),
], 1):
    params.set('A' + str(row), label)
    params.set('B' + str(row), str(value) + ' mm')
    params.set('C' + str(row), basis)
params.setColumnWidth('A', 180)
params.setColumnWidth('C', 330)
params.set('A10', 'Exterior envelopes only; no cavities, fits or factory tolerances.')
params.set('A11', 'Study values are source-generation inputs, not live expressions.')


def outline(inset, rail, z):
    outer, inner = 119.5 - inset, 86.5 + rail
    width, height = outer - inner, 102 - 2 * inset
    thickness = .2
    shape = Part.makeBox(width, height, thickness,
                         vec(-outer, -height / 2, z))
    edges = [e for e in shape.Edges if e.BoundBox.ZLength > thickness - 1e-7
             and abs(e.BoundBox.XMin + outer) < 1e-7]
    shape = shape.makeFillet(20.5 - inset, edges)
    edges = [e for e in shape.Edges if e.BoundBox.ZLength > thickness - 1e-7
             and abs(e.BoundBox.XMin + inner) < 1e-7]
    shape = shape.makeFillet(max(.1, .65 - rail), edges)
    return min(shape.Faces, key=lambda f: abs(f.CenterOfMass.z - z)).OuterWire


def setback(radius, distance):
    return (radius - math.sqrt(max(0, radius * radius - (radius - distance) ** 2))
            if distance < radius else 0.)


def transformed(shape, center, front):
    result = shape.copy()
    result.translate(vec(103, 0, 0))
    if not front:
        result.rotate(vec(0, 0, 6.3), vec(0, 1, 0), 180)
    result.translate(vec(center, 0, 0))
    return result


def add_shape(name, label, shape, color, shown=True):
    obj = doc.addObject('Part::Feature', name)
    obj.Label, obj.Shape = label, shape
    helper['appearance'](obj, color, metal=.18, gloss=35)
    obj.ViewObject.DisplayMode = 'Shaded'
    obj.ViewObject.Deviation = .02
    obj.Visibility = shown
    return obj


rows, deliverables = [], []
for front in [True, False]:
    tag = 'Front' if front else 'Rear'
    base_center, candidate_center = (-75, -25) if front else (25, 75)
    original = source.getObject('JoyL' + tag + 'Contour15').Shape.copy()
    baseline = add_shape(tag + 'V16', tag + ' · 已推送 V16 外包络',
                         transformed(original, base_center, front), (.25, .40, .57))
    deliverables.append(baseline)
    r, ri = (3.5 if front else 6.0), .65
    tip, base = (13.9, 7.5) if front else (-1.3, 7.3)
    direction = 1 if front else -1
    start = tip - direction * r
    # Constrain the straight band as well as the roundover. Two widely spaced
    # identical sections alone let the spline bow inward between them.
    levels = [base + (start-base)*i/8 for i in range(9)]
    for angle in [10, 20, 30, 40, 50, 60, 70, 78, 84, 88, 90]:
        levels.append(start + direction * r * math.sin(math.radians(angle)))
    levels += [tip + direction * ri * (-1 + math.sin(math.radians(a)))
               for a in [0, 30, 60, 80]]
    levels = sorted(set(levels), reverse=not front)
    sections = []
    for i, z in enumerate(levels):
        distance = abs(tip - z)
        wire = outline(setback(r, distance), setback(ri, distance), z)
        obj = add_shape(tag + 'Section' + str(i), tag + ' 曲面截线 ' + str(i),
                        transformed(wire, candidate_center, front), (.6, .6, .6), False)
        sections.append(obj)
    loft = doc.addObject('Part::Loft', tag + 'UnequalEdgeLoft')
    loft.Label = tag + ' · 外侧宽、导轨侧窄的外包络放样'
    loft.Sections, loft.Solid, loft.Ruled = sections, True, False
    doc.recompute()
    assert not loft.Shape.isNull() and loft.Shape.isValid(), tag
    # Constrain the small interpolation overshoot with an axis-aligned envelope.
    # The tool extends beyond both end caps to avoid coincident cap faces.
    epsilon = 1e-6  # Avoid coincident sliver faces; front rail boundary remains exact.
    limit = add_shape(tag + 'PlanLimit', tag + ' · 名义 33 × 102 mm 包络限制',
                      Part.makeBox(33+(epsilon if front else 2*epsilon), 102+2*epsilon, 30,
                                   vec(candidate_center-16.5-epsilon, -51-epsilon, -10)),
                      (.6, .6, .6), False)
    candidate = doc.addObject('Part::Common', tag + 'Candidate')
    candidate.Base, candidate.Tool, candidate.Refine = loft, limit, False
    doc.recompute()
    candidate.Label = tag + ' · 曲率校准样件（实心外包络）'
    assert candidate.Shape.isValid() and len(candidate.Shape.Solids) == 1, tag
    helper['appearance'](candidate, (.90, .47, .19), metal=.18, gloss=35)
    candidate.ViewObject.DisplayMode = 'Shaded'
    candidate.ViewObject.Deviation = .02
    candidate.addProperty('App::PropertyString', 'Scope', 'Reference')
    candidate.Scope = 'Exterior envelope study; NOT a hollow shell or verified assembly'
    candidate.addProperty('App::PropertyString', 'SourceReference', 'Reference')
    candidate.SourceReference = 'USD819642S1 Fig.3 / Fig.4, cross-check Nintendo product images'
    deliverables.append(candidate)
    for obj in sections + [loft, limit]:
        obj.Visibility = False
    bb = candidate.Shape.optimalBoundingBox(False, False)
    distances = []
    for i in range(201):
        z = base + (tip-base)*i/200
        distance = abs(tip - z)
        for x in [-119.5 + setback(r, distance), -86.5 - setback(ri, distance)]:
            point = transformed(Part.Vertex(vec(x, 0, z)), candidate_center, front)
            distances.append(point.distToShape(Part.makeCompound(candidate.Shape.Faces))[0])
    rows.append({'surface': tag, 'valid': candidate.Shape.isValid(),
                 'solids': len(candidate.Shape.Solids),
                 'bounds_mm': [bb.XLength, bb.YLength, bb.ZLength],
                 'sections': len(sections), 'chosen_outer_setback_mm': r,
                 'chosen_rail_setback_mm': ri,
                 'analytic_section_max_deviation_mm': max(distances),
                 'deviation_scope': 'Full straight band and roundover versus chosen sections; NOT physical-device error'})
    for center, text in [(base_center, tag.upper() + ' / V16'),
                         (candidate_center, tag.upper() + ' / STUDY')]:
        helper['printed_text'](doc, tag + 'Label', text, text, 2.3,
                               (center - 17, -61, 14), color=(.15, .18, .23))

# A separate, explicit diameter specimen shows the supported face-button change.
for center, radius, label, color in [(-18, 3.18, 'V16  6.36 mm', (.25, .40, .57)),
                                      (18, 3.8, 'STUDY  7.60 mm', (.90, .47, .19))]:
    shape = Part.makeCylinder(radius, 2, vec(center, -77, 12))
    shape = shape.makeFillet(.22, [e for e in shape.Edges if e.BoundBox.ZLength < 1e-7])
    add_shape('ButtonSpecimen', '面键直径对照 · ' + label, shape, color)
    helper['printed_text'](doc, 'ButtonLabel', label, label, 2.1,
                           (center - 13, -85, 14), color=(.15, .18, .23))
helper['printed_text'](doc, 'Title', '公开资料外缘校准',
                       'SWITCH / PUBLIC REFERENCE CALIBRATION', 3.3,
                       (-96, 66, 14), color=(.15, .18, .23))
helper['printed_text'](doc, 'ScopeLabel', '外包络样件，并非原厂 CAD',
                       'EXTERIOR ENVELOPES / IMAGE ESTIMATES / NOT FACTORY CAD', 2.0,
                       (-96, 58, 14), color=(.30, .33, .38))
doc.recompute()
App.setActiveDocument(doc.Name)
Gui.activeDocument().activeView().setCameraType('Orthographic')
helper['render'](HERE / 'comparison.png', normal=(-.20, .28, 2),
                 target=(0, -8, 7), span=182, size=(2400, 1600))
helper['render'](HERE / 'front-comparison.png', target=(0, -8, 7),
                 span=180, size=(2400, 1600))
helper['camera']((-.20, .28, 2), target=(0, -8, 7), span=182)
native = HERE / 'Switch_Public_Reference_Study.FCStd'
doc.saveAs(str(native))
Part.export(deliverables, str(HERE / 'Switch_Exterior_Envelopes.step'))
report = {'baseline_source': str(SOURCE.relative_to(ROOT.parents[1])),
          'baseline_source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'study_source_sha256': hashlib.sha256(native.read_bytes()).hexdigest(),
          'scope': 'Four solid exterior envelopes plus two button-diameter specimens; no production shell or complete assembly',
          'study_is_complete_assembly': False,
          'profile_integration_revision': 17,
          'integration_report': '../../output/reports/17_interference_audit.json',
          'envelope_check_tolerance_mm': .001,
          'section_sampling_tolerance_mm': .02,
          'envelopes': rows,
          'passed': all(r['valid'] and r['solids'] == 1 and
                        max(abs(a-b) for a, b in zip(r['bounds_mm'][:2], [33, 102])) < .001
                        and r['analytic_section_max_deviation_mm'] < .02 for r in rows)}
(HERE / 'study-checks.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
assert report['passed'], report
if owned:
    App.closeDocument(source.Name)
print(json.dumps(report, ensure_ascii=False))
