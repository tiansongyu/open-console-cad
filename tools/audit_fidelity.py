"""Read-only, hash-bound baseline of saved CAD geometry and fidelity gaps.

Run with the matching FreeCAD Python runtime, for example:
    AppRun python tools/audit_fidelity.py

This opens each final Complete.FCStd without recomputing or saving it. It does
not certify hardware equivalence, run interference checks, or infer electrical
function from connector geometry. Connector checks count explicitly identified
mating contacts, excluding separately modelled PCB terminal tails.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time

sys.path.insert(0, os.environ.get('PATH_TO_FREECAD_LIBDIR', ''))
import FreeCAD as App
import Part
import Sketcher  # Register native types while loading saved documents.

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'hdmi_a': {
        'url': 'https://www.te.com/en/product-2007435-1.html',
        'basis': 'Manufacturer standard HDMI connector: 19 positions',
    },
    'usb3_a': {
        'url': 'https://www.te.com/en/product-1932258-1.html',
        'basis': 'Manufacturer USB 3.0 Type-A receptacle: 9 positions',
    },
    'ethernet_8p8c': {
        'url': 'https://www.te.com/en/product-5406443-1.html',
        'basis': 'Manufacturer RJ45 jack: 8 positions and 8 loaded positions',
    },
    'seriesx_ports': {
        'url': 'https://www.xbox.com/en-US/consoles/xbox-series-x',
        'basis': 'Carbon Black optical model: HDMI, three USB 3.1 Gen 1 ports and gigabit Ethernet',
    },
}


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def bounds(shape):
    b = shape.optimalBoundingBox(False, False)
    return [b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax]


def envelope(shapes):
    if not shapes:
        return None
    b = Part.makeCompound(shapes).optimalBoundingBox(False, False)
    return {'bounds_mm': [b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax],
            'size_mm': [b.XLength, b.YLength, b.ZLength]}


def connector_checks(slug, parts):
    """Rules use reviewed PartID families, not broad name-based pin guesses."""
    rules = []
    if slug == 'seriesx':
        rules.extend([
            ('HDMI', r'HDMIContact\d+', 19, 'hdmi_a'),
            ('Ethernet', r'EthernetContact\d+', 8, 'ethernet_8p8c'),
        ])
        for key in ['FrontUSB', 'RearUSB1', 'RearUSB2']:
            rules.append((key, key + r'(?:Contact|Legacy|SuperSpeed)\d+', 9, 'usb3_a'))
    if slug == 'ps4':
        for key in ['USB0', 'USB1']:
            rules.append((key, key + r'(?:Contact|Legacy|SuperSpeed)\d+', 9, 'usb3_a'))
    if slug in ['ps5', 'xboxone']:
        for key in ['RearUSB0', 'RearUSB1'] + (['SideUSB'] if slug == 'xboxone' else []):
            rules.append((key, key + r'(?:Contact|Legacy|SuperSpeed)\d+', 9, 'usb3_a'))
    # HDMI mating-contact layouts have different row suffixes across builders.
    hdmi = {'switch': ['HDMI'], 'switch2': ['HDMI'], 'ps3': ['HDMI'],
            'ps4': ['HDMI'], 'ps5': ['HDMI'], 'wiiu': ['HDMI'],
            'xboxone': ['HDMIOut', 'HDMIIn']}
    for key in hdmi.get(slug, []):
        rules.append((key, key + r'Contact-?\d+(?:_\d+)?', 19, 'hdmi_a'))
    output = []
    for connector, pattern, expected, source in rules:
        matched = [(key, obj) for key, obj in parts.items() if re.fullmatch(pattern, key)]
        solid_counts = {key: len(obj.Shape.Solids) for key, obj in matched}
        # One component per mating contact is established for these builders.
        # A compound is reported as indeterminate instead of conflating solids
        # and contact count; a rebuilt connector may legitimately group them.
        determinate = bool(matched) and all(n == 1 for n in solid_counts.values())
        actual = len(matched) if determinate else None
        output.append({
            'connector': connector, 'part_id_pattern': pattern,
            'expected_mating_contacts': expected, 'actual_mating_contacts': actual,
            'matched_part_ids': [key for key, _ in matched],
            'solid_counts': solid_counts,
            'status': ('count_matches' if actual == expected else 'count_mismatch')
                      if determinate else 'needs_manual_review',
            'source_keys': [source] + (['seriesx_ports'] if slug == 'seriesx' else []),
            'scope': 'Mating contact count only; connector shape, pitch and electrical routing remain unverified',
        })
    return output


def audit(entry, tolerance):
    slug = entry['id']
    folder = ROOT / 'devices' / slug
    manifest_path = folder / 'output/reports/final_manifest.json'
    manifest = json.loads(manifest_path.read_text())
    native = folder / 'output' / manifest['native_files'][0]
    source_paths = {'native': native, 'manifest': manifest_path}
    if (folder / 'profile.json').exists():
        source_paths['profile'] = folder / 'profile.json'
    hashes_before = {key: sha(path) for key, path in source_paths.items()}
    doc = App.openDocument(str(native))
    try:
        objects = [o for o in doc.Objects if getattr(o, 'PhysicalPart', False)]
        ids = Counter(o.PartID for o in objects)
        duplicates = sorted(key for key, n in ids.items() if n > 1)
        parts = {o.PartID: o for o in objects}
        expected = {row['part_id']: row for row in manifest['objects']}
        profile_obj = doc.getObject('StudyInfo')
        profile = json.loads(profile_obj.ProfileJSON) if profile_obj and hasattr(profile_obj, 'ProfileJSON') else {}
        measurements = []
        invalid = []
        mismatches = []
        for obj in objects:
            shape = obj.Shape
            null = shape.isNull()
            valid = not null and shape.isValid() and bool(shape.Solids)
            coordinates = bounds(shape) if not null else None
            solids = len(shape.Solids) if not null else 0
            volume = shape.Volume if not null else None
            row = expected.get(obj.PartID)
            bbox_delta = max(abs(a-b) for a, b in zip(coordinates, row['bounds'])) if row and coordinates else None
            volume_delta = volume-row['volume'] if row and volume is not None else None
            agrees = bool(row and valid and solids == row['solids'] and bbox_delta <= tolerance and abs(volume_delta) <= 1e-4)
            if not valid:
                invalid.append(obj.PartID)
            if not agrees:
                mismatches.append(obj.PartID)
            measurements.append({
                'part_id': obj.PartID, 'name': obj.Name, 'assembly': obj.Assembly,
                'fidelity': getattr(obj, 'Fidelity', ''), 'valid': bool(valid),
                'solids': solids, 'volume_mm3': volume, 'bounds_mm': coordinates,
                'manifest_bbox_max_delta_mm': bbox_delta,
                'manifest_volume_delta_mm3': volume_delta, 'manifest_matches': agrees,
            })
        groups = manifest.get('envelope_groups', manifest['handheld_groups'])
        pose = 'closed' if entry['family'] == 'clamshell' else 'saved'
        transform = None
        if pose == 'closed':
            transform = App.Placement(App.Vector(), App.Rotation(App.Vector(1, 0, 0), 180),
                                      App.Vector(0, profile['hinge_y'], profile['hinge_z']))
        shapes = []
        for obj in objects:
            if obj.Assembly not in groups or obj.Shape.isNull():
                continue
            shape = obj.Shape.copy()
            if transform is not None:
                shape.Placement = transform.multiply(obj.FlatPlacement) if obj.PoseGroup == 'Lid' else obj.FlatPlacement
            shapes.append(shape)
        measured = envelope(shapes)
        reference = manifest.get('published_envelope_mm', manifest.get('reference_envelope_mm', manifest.get('published_handheld_mm')))
        delta = [a-b for a, b in zip(measured['size_mm'], reference)] if measured and reference else None
        counts = Counter(getattr(obj, 'Fidelity', '') for obj in objects)
        internal_count = sum(n for label, n in counts.items() if label.startswith('Schematic'))
        invalid_features = [o.Name for o in doc.Objects if 'Invalid' in o.State]
        checks = connector_checks(slug, parts)
        hashes_after = {key: sha(path) for key, path in source_paths.items()}
        unchanged = hashes_before == hashes_after
        missing = sorted(set(expected)-set(parts))
        extra = sorted(set(parts)-set(expected))
        geometry_passed = unchanged and not (duplicates or invalid or invalid_features or mismatches or missing or extra)
        geometry_passed = geometry_passed and len(objects) == manifest['physical_components']
        return {
            'device': slug, 'model': entry['model'],
            'inputs': {key: {'path': str(path.relative_to(ROOT)), 'sha256': hashes_before[key]} for key, path in source_paths.items()},
            'inputs_unchanged': unchanged,
            'counts': {'physical_components': len(objects), 'solids': sum(x['solids'] for x in measurements),
                       'schematic_internal_components': internal_count,
                       'other_fidelity_components': len(objects)-internal_count,
                       'fidelity_labels': dict(counts), 'assemblies': dict(Counter(o.Assembly for o in objects))},
            'geometry_passed': bool(geometry_passed), 'invalid_parts': invalid,
            'invalid_features': invalid_features, 'duplicate_part_ids': duplicates,
            'missing_part_ids': missing, 'extra_part_ids': extra, 'manifest_mismatches': mismatches,
            'envelope': {'pose': pose, 'groups': groups, 'measured': measured,
                         'reference_mm': reference, 'delta_from_reference_mm': delta,
                         'basis': manifest.get('envelope_basis', manifest.get('bounds_basis')),
                         'interpretation': 'Reference scope and protrusion exclusions must be verified before treating a delta as a dimensional defect'},
            'saved_profile': profile,
            'connector_checks': checks,
            'connector_count_mismatches': [x['connector'] for x in checks if x['status'] == 'count_mismatch'],
            'factory_equivalence_verified': False,
            'components': measurements,
        }
    finally:
        App.closeDocument(doc.Name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/fidelity_baseline_audit.json')
    parser.add_argument('--devices', nargs='+', help='Optional catalog device IDs; default all, NDS first')
    parser.add_argument('--bbox-tolerance-mm', type=float, default=1e-5)
    args = parser.parse_args()
    catalog_path = ROOT / 'site/src/catalog.json'
    catalog = json.loads(catalog_path.read_text())
    by_id = {entry['id']: entry for entry in catalog}
    selected = args.devices or ['nds'] + [e['id'] for e in catalog if e['id'] != 'nds']
    if set(selected)-set(by_id) or len(selected) != len(set(selected)):
        parser.error('Device IDs must be unique members of the current catalog')
    if not 0 <= args.bbox_tolerance_mm < float('inf'):
        parser.error('--bbox-tolerance-mm must be finite and nonnegative')
    started = time.time()
    report = {
        'schema_version': 1, 'complete': False, 'geometry_passed': False,
        'started_unix': started, 'freecad_version': App.Version(),
        'scope': 'Saved Complete.FCStd physical BReps; no recompute, save, interference, STEP or hardware metrology',
        'catalog_sha256': sha(catalog_path), 'audit_script_sha256': sha(Path(__file__)),
        'selected_devices': selected, 'bbox_tolerance_mm': args.bbox_tolerance_mm,
        'volume_tolerance_mm3': 1e-4, 'sources_checked_date': '2026-11-08',
        'connector_reference_sources': SOURCES,
        'factory_equivalence_verified': False, 'devices': [], 'errors': [],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for slug in selected:
        try:
            row = audit(by_id[slug], args.bbox_tolerance_mm)
            report['devices'].append(row)
            print(json.dumps({'device': slug, 'geometry_passed': row['geometry_passed'],
                              'components': row['counts']['physical_components'],
                              'contact_count_mismatches': row['connector_count_mismatches']}), flush=True)
        except Exception as exc:
            report['errors'].append({'device': slug, 'error': repr(exc)})
            print(json.dumps({'device': slug, 'error': repr(exc)}), flush=True)
        report['elapsed_seconds'] = time.time()-started
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    report['complete'] = len(report['devices']) == len(selected) and not report['errors']
    report['geometry_passed'] = report['complete'] and all(row['geometry_passed'] for row in report['devices'])
    report['total_components'] = sum(row['counts']['physical_components'] for row in report['devices'])
    report['connector_count_mismatches'] = [
        {'device': row['device'], **check} for row in report['devices']
        for check in row['connector_checks'] if check['status'] == 'count_mismatch']
    report['elapsed_seconds'] = time.time()-started
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({key: report[key] for key in ['complete', 'geometry_passed', 'total_components', 'elapsed_seconds']}), flush=True)
    # Known hardware-detail gaps are findings, not an error in this baseline run.
    return 0 if report['geometry_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
