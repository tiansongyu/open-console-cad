"""Reproduce the rejected left-shell fit trial; does not modify either CAD file.

Run in the FreeCAD Python environment. This deliberately records failures as
data; it is a diagnostic, not an acceptance test for the delivered V16 assembly.
"""
import hashlib
import json
import math
import os
import sys
from pathlib import Path
if os.environ.get('PATH_TO_FREECAD_LIBDIR'):
    sys.path.insert(0, os.environ['PATH_TO_FREECAD_LIBDIR'])
import FreeCAD as App
import Part
import PartDesign
import Sketcher
import Spreadsheet

HERE = Path(__file__).resolve().parent
source_path = HERE.parents[1] / 'output/Switch_Complete.FCStd'
study_path = HERE / 'Switch_Public_Reference_Study.FCStd'
source = App.openDocument(str(source_path))
study = App.openDocument(str(study_path))
parts = {o.PartID: o for o in source.Objects if getattr(o, 'PhysicalPart', False)}
vec = App.Vector


def inner_outline(width, height, radius, x, z):
    shape = Part.makeBox(width, height, .2, vec(-width/2, -height/2, 0))
    edges = [e for e in shape.Edges if e.BoundBox.ZLength > .2-1e-7
             and abs(e.BoundBox.XMin+width/2) < 1e-7]
    shape = shape.makeFillet(radius, edges)
    edges = [e for e in shape.Edges if e.BoundBox.ZLength > .2-1e-7
             and abs(e.BoundBox.XMin-width/2) < 1e-7]
    shape = shape.makeFillet(.1, edges)
    shape.translate(vec(x, 0, z))
    return min(shape.Faces, key=lambda f: abs(f.CenterOfMass.z-z)).OuterWire


results = []
for front, center in [(True, -25), (False, 75)]:
    tag = 'Front' if front else 'Rear'
    key = 'JoyL' + tag
    envelope = study.getObject(tag+'Candidate').Shape.copy()
    envelope.translate(vec(-center, 0, 0))
    if not front:
        envelope.rotate(vec(0, 0, 6.3), vec(0, 1, 0), 180)
    envelope.translate(vec(-103, 0, 0))
    radius, tip, base, direction = (2.35, 12.75, 7.25, 1) if front else (4.85, -.15, 7.65, -1)
    start = tip-direction*radius
    levels = [base, start] + [start+direction*radius*math.sin(math.radians(a))
                              for a in [10, 20, 30, 40, 50, 60, 70, 78, 84, 88, 90]]
    wires = []
    for z in sorted(set(levels), reverse=not front):
        distance = abs(tip-z)
        inset = (radius-math.sqrt(max(0, radius**2-(radius-distance)**2))
                 if distance < radius else 0)
        wires.append(inner_outline(30.4-inset, 99.4-2*inset, 19.2-inset, -103+inset/2, z))
    cavity = Part.makeLoft(wires, True, False)
    shell = envelope.cut(cavity)
    stages = [{'stage': 'envelope', 'valid': envelope.isValid()},
              {'stage': 'fitted cavity', 'valid': cavity.isValid()},
              {'stage': 'envelope minus cavity', 'valid': shell.isValid()}]
    obj = parts[key]
    while obj.TypeId == 'Part::Cut':
        if not obj.Tool.Label.startswith('等壁厚圆润内腔'):
            shell = shell.cut(obj.Tool.Shape)
            stages.append({'stage': obj.Tool.Label, 'valid': shell.isValid()})
        obj = obj.Base
    row = {'key': key, 'valid': shell.isValid(), 'solids': len(shell.Solids),
           'stages': stages, 'interference_scan_performed': shell.isValid(), 'clashes': []}
    if row['valid']:
        for part_id, obj in parts.items():
            if obj.Assembly not in ['JoyLeft', 'JoyInternalL', 'JoyRailL'] or part_id in ['JoyLFront', 'JoyLRear']:
                continue
            if shell.BoundBox.intersect(obj.Shape.BoundBox):
                common = shell.common(obj.Shape)
                if common.Volume > .001:
                    row['clashes'].append({'part': part_id, 'label': obj.Label,
                                           'volume_mm3': common.Volume})
    results.append(row)
report = {
    'accepted_for_assembly': False,
    'baseline_source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
    'study_source_sha256': hashlib.sha256(study_path.read_bytes()).hexdigest(),
    'scope': 'Left Joy-Con pilot only; fitted cavity plus existing V16 opening tools; right side not tested',
    'cavity_assumptions_mm': {'width': 30.4, 'height': 99.4, 'plan_radius': 19.2,
                             'front_inner_roll': 2.35, 'rear_inner_roll': 4.85,
                             'front_inner_face_z': 12.75, 'rear_inner_face_z': -.15},
    'interference_volume_threshold_mm3': .001,
    'results': results,
    'notes': ['Invalid shells skip interference scanning; an empty list does not mean a pass.',
              'Trial shells are excluded from delivered native/STEP files.',
              'Existing internals are schematic. No factory fit is established.'],
}
(HERE/'assembly-trial.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
App.closeDocument(study.Name)
App.closeDocument(source.Name)
