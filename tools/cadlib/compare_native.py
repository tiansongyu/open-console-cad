"""Compare traced component geometry in two FreeCAD files without editing them.

Run with FreeCAD's Python environment:
    python tools/cadlib/compare_native.py original.FCStd rebuilt.FCStd report.json

Matching volume and bounding boxes alone do not establish equivalence: a hole
can move while both stay unchanged. Nonidentical BReps therefore receive a
bidirectional Boolean difference check, with an explicit volume tolerance.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, os.environ.get('PATH_TO_FREECAD_LIBDIR', ''))
import FreeCAD as App


def compare_shapes(left, right, tolerance=1e-6):
    if left.isNull() or right.isNull() or not left.Solids or not right.Solids:
        return {'passed': False, 'error': 'Null or non-solid physical component'}
    if not left.isValid() or not right.isValid() or left.Volume <= 0 or right.Volume <= 0:
        return {'passed': False, 'error': 'Invalid physical component'}
    identical = left.exportBrepToString() == right.exportBrepToString()
    removed = added = 0.0
    if not identical:
        removed = abs(left.cut(right).Volume)
        added = abs(right.cut(left).Volume)
    counts_match = len(left.Solids) == len(right.Solids)
    return {
        'passed': counts_match and removed <= tolerance and added <= tolerance,
        'identical_brep': identical,
        'original_solids': len(left.Solids),
        'rebuilt_solids': len(right.Solids),
        'removed_mm3': removed,
        'added_mm3': added,
    }


def traced_parts(doc):
    parts = [o for o in doc.Objects if 'PhysicalPart' in o.PropertiesList and o.PhysicalPart]
    if not parts:
        raise ValueError('No traced physical components')
    if len({o.PartID for o in parts}) != len(parts):
        raise ValueError('Duplicate PartID in document')
    return {o.PartID: o for o in parts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('rebuilt', type=Path)
    parser.add_argument('report', type=Path)
    parser.add_argument('--tolerance', type=float, default=1e-6, help='Boolean difference volume in mm³')
    args = parser.parse_args()
    if not 0 <= args.tolerance < float('inf'):
        parser.error('--tolerance must be finite and nonnegative')
    hashes = {key: hashlib.sha256(path.read_bytes()).hexdigest()
              for key, path in [('original', args.original), ('rebuilt', args.rebuilt)]}
    opened = []
    try:
        left_doc = App.openDocument(str(args.original.resolve())); opened.append(left_doc.Name)
        right_doc = App.openDocument(str(args.rebuilt.resolve())); opened.append(right_doc.Name)
        left, right = traced_parts(left_doc), traced_parts(right_doc)
        missing, extra = sorted(left.keys() - right.keys()), sorted(right.keys() - left.keys())
        checks = []
        for key in sorted(left.keys() & right.keys()):
            try:
                row = compare_shapes(left[key].Shape, right[key].Shape, args.tolerance)
                row['assembly_matches'] = left[key].Assembly == right[key].Assembly
                row['passed'] = row['passed'] and row['assembly_matches']
            except Exception as exc:
                row = {'passed': False, 'error': str(exc)}
            checks.append({'part_id': key, **row})
        invalid = {name: [o.Name for o in doc.Objects if 'Invalid' in o.State]
                   for name, doc in [('original', left_doc), ('rebuilt', right_doc)]}
        unchanged = all(hashlib.sha256(path.read_bytes()).hexdigest() == hashes[key]
                        for key, path in [('original', args.original), ('rebuilt', args.rebuilt)])
        result = {
            'passed': unchanged and not missing and not extra and not any(invalid.values()) and all(r['passed'] for r in checks),
            'source_sha256': hashes,
            'inputs_unchanged': unchanged,
            'boolean_tolerance_mm3': args.tolerance,
            'missing_in_rebuild': missing,
            'extra_in_rebuild': extra,
            'invalid_features': invalid,
            'checks': checks,
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'passed': result['passed'], 'compared': len(checks), 'report': str(args.report)}))
        return 0 if result['passed'] else 1
    finally:
        for name in reversed(list(dict.fromkeys(opened))):
            if name in App.listDocuments():
                App.closeDocument(name)


if __name__ == '__main__':
    raise SystemExit(main())
