"""Independently reload and intersect physical CAD components; no document edits."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, os.environ.get('PATH_TO_FREECAD_LIBDIR', ''))
import FreeCAD as App
import Part


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('native', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--profile', type=Path)
    parser.add_argument('--opening', type=float)
    parser.add_argument('--threshold', type=float, default=1e-6)
    args = parser.parse_args()
    start = time.time()
    doc = App.openDocument(str(args.native.resolve()))
    parts = [o for o in doc.Objects if 'PhysicalPart' in o.PropertiesList and o.PhysicalPart]
    assert parts, 'No traced physical components'
    assert len({o.PartID for o in parts}) == len(parts), 'Duplicate component identifiers'
    profile = json.loads(args.profile.read_text()) if args.profile else {}
    info = doc.getObject('StudyInfo')
    if info: profile = json.loads(info.ProfileJSON)
    pose = None
    if args.opening is not None:
        assert profile.get('family') == 'clamshell'
        pose = App.Placement(App.Vector(), App.Rotation(App.Vector(1, 0, 0), 180-args.opening), App.Vector(0, profile['hinge_y'], profile['hinge_z']))
    shapes = []
    rows = []
    for obj in parts:
        shape = obj.Shape.copy()
        if pose is not None:
            shape.Placement = pose.multiply(obj.FlatPlacement) if obj.PoseGroup == 'Lid' else obj.FlatPlacement
        assert not shape.isNull() and shape.isValid() and shape.Solids, obj.PartID
        shapes.append(shape)
        rows.append({'part_id': obj.PartID, 'name': obj.Name, 'valid': True, 'solids': len(shape.Solids), 'volume_mm3': shape.Volume})
    invalid = [o.Name for o in doc.Objects if 'Invalid' in o.State]
    assert not invalid, invalid
    boxes = [s.optimalBoundingBox(False, False) for s in shapes]
    pairs = [(i, j) for i in range(len(parts)) for j in range(i+1, len(parts)) if min(min(getattr(boxes[i], a+'Max'), getattr(boxes[j], a+'Max'))-max(getattr(boxes[i], a+'Min'), getattr(boxes[j], a+'Min')) for a in 'XYZ') > 1e-7]
    main_shapes = [s for o, s in zip(parts, shapes) if o.Assembly not in ['Accessories', 'Cradle']]
    bb = Part.makeCompound(main_shapes).optimalBoundingBox(False, False)
    report = {'file': str(args.native), 'opening': args.opening, 'physical_components': len(parts), 'component_checks': rows, 'invalid_features': invalid, 'measured_envelope_mm': [bb.XLength, bb.YLength, bb.ZLength], 'threshold_mm3': args.threshold, 'candidate_pairs': len(pairs), 'checked_pairs': 0, 'clashes': [], 'errors': [], 'complete': False}
    print(json.dumps({'state': 'auditing', 'components': len(parts), 'pairs': len(pairs)}), flush=True)
    for n, (i, j) in enumerate(pairs, 1):
        try:
            common = shapes[i].common(shapes[j])
            if common.Volume > args.threshold:
                report['clashes'].append({'a': parts[i].PartID, 'b': parts[j].PartID, 'volume_mm3': common.Volume})
        except Exception as exc:
            report['errors'].append({'a': parts[i].PartID, 'b': parts[j].PartID, 'error': str(exc)})
        report['checked_pairs'] = n
        if n % 100 == 0:
            args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2))
            print(json.dumps({'checked': n, 'clashes': len(report['clashes'])}), flush=True)
    report.update(complete=True, elapsed_seconds=time.time()-start, passed=not report['clashes'] and not report['errors'])
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != 'component_checks'}, ensure_ascii=False), flush=True)
    App.closeDocument(doc.Name)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
