"""Independently reload and intersect physical CAD components; no document edits."""
import argparse
import hashlib
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
    parser.add_argument('--resume', action='store_true', help='Resume a saved audit only if its input SHA-256 and settings match')
    parser.add_argument('--max-pairs', type=int, help='Process at most this many candidate pairs in this invocation')
    args = parser.parse_args()
    if args.max_pairs is not None and args.max_pairs < 1:parser.error('--max-pairs must be positive')
    start = time.time()
    source_hash = hashlib.sha256(args.native.resolve().read_bytes()).hexdigest()
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
    report = {'file': str(args.native), 'opening': args.opening, 'physical_components': len(parts), 'component_checks': rows, 'invalid_features': invalid, 'measured_envelope_mm': [bb.XLength, bb.YLength, bb.ZLength], 'threshold_mm3': args.threshold, 'candidate_pairs': len(pairs), 'checked_pairs': 0, 'clashes': [], 'errors': [], 'complete': False, 'source_sha256': source_hash, 'chunks': [], 'elapsed_seconds': 0.0}
    if args.resume:
        previous = json.loads(args.output.read_text())
        assert previous.get('source_sha256') == source_hash, 'Cannot resume: native file identity changed or is missing'
        assert previous['opening'] == args.opening and previous['threshold_mm3'] == args.threshold, 'Cannot resume: settings changed'
        assert previous['candidate_pairs'] == len(pairs), 'Cannot resume: candidate set changed'
        assert [r['part_id'] for r in previous['component_checks']] == [r['part_id'] for r in rows], 'Cannot resume: component order changed'
        assert 0 <= previous['checked_pairs'] <= len(pairs)
        report = previous
    prior_elapsed = report.get('elapsed_seconds', 0.0)
    first = report['checked_pairs']
    stop = min(len(pairs), first + args.max_pairs) if args.max_pairs else len(pairs)
    print(json.dumps({'state': 'auditing', 'components': len(parts), 'pairs': len(pairs)}), flush=True)
    for n, (i, j) in enumerate(pairs[first:stop], first + 1):
        try:
            common = shapes[i].common(shapes[j])
            if common.Volume > args.threshold:
                report['clashes'].append({'a': parts[i].PartID, 'b': parts[j].PartID, 'volume_mm3': common.Volume})
        except Exception as exc:
            report['errors'].append({'a': parts[i].PartID, 'b': parts[j].PartID, 'error': str(exc)})
        report['checked_pairs'] = n
        if n % 100 == 0:
            report['elapsed_seconds'] = prior_elapsed + time.time() - start
            args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2))
            print(json.dumps({'checked': n, 'clashes': len(report['clashes'])}), flush=True)
    complete = report['checked_pairs'] == len(pairs)
    report.setdefault('chunks', []).append({'from_pair': first + 1, 'through_pair': stop, 'seconds': time.time()-start})
    report.update(complete=complete, elapsed_seconds=prior_elapsed + time.time()-start, passed=complete and not report['clashes'] and not report['errors'])
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != 'component_checks'}, ensure_ascii=False), flush=True)
    App.closeDocument(doc.Name)
    # A clean partial batch exits normally; only complete=True / passed=True certifies the assembly.
    return 0 if not report['clashes'] and not report['errors'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
