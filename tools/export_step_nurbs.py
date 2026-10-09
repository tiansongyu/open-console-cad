"""Re-export selected problematic STEP surfaces as exact NURBS, preserving native CAD.

Run in FreeCAD's Python environment and call export_device(repo, device, part_ids).
The conversion must pass the same Boolean geometry comparison as the final STEP
round-trip audit. It does not relax that audit or modify the native documents.
"""
import hashlib
import json
import tempfile
import Part
from pathlib import Path
import FreeCAD as App
import ImportGui
from cadlib.step_geometry import compare_solids


def export_device(repo, device, part_ids, output_dir=None):
    out = Path(output_dir) if output_dir is not None else Path(repo) / 'devices' / device / 'output'
    manifest = json.loads((out / 'reports/final_manifest.json').read_text())
    prefix = manifest['prefix']
    conversions = []
    exports = [
        (prefix + '_FullKit.step', 'Complete', manifest['objects']),
        (manifest['main_step_file'], 'Complete', [r for r in manifest['objects'] if r['assembly'] in manifest['handheld_groups']]),
        (prefix + '_Exploded.step', 'Exploded', manifest['exploded_objects']),
    ]
    for filename, variant, rows in exports:
        native = out / f'{prefix}_{variant}.FCStd'
        digest = hashlib.sha256(native.read_bytes()).hexdigest()
        doc = next((d for d in App.listDocuments().values() if Path(d.FileName) == native), None)
        opened = doc is None
        if opened:
            doc = App.openDocument(str(native))
        temporary = App.newDocument('STEPConversion')
        objects = []
        try:
            for row in rows:
                source = doc.getObject(row['name'])
                if row['part_id'] not in part_ids:
                    objects.append(source)
                    continue
                # OCCT can leave invalid edge tolerances immediately after toNurbs.
                # STEP serialization/reload rebuilds these; accept only the valid,
                # geometrically verified result, never the intermediate shape.
                with tempfile.TemporaryDirectory(prefix='cad-step-nurbs-') as folder:
                    probe = str(Path(folder) / 'converted.step')
                    source.Shape.toNurbs().exportStep(probe)
                    shape = Part.read(probe)
                assert len(source.Shape.Solids) == len(shape.Solids)
                checks = [compare_solids(a, b) for a, b in zip(source.Shape.Solids, shape.Solids)]
                assert all(c['pass'] for c in checks), (row['part_id'], checks)
                proxy = temporary.addObject('PartDesign::Feature', source.Name)
                proxy.Label = source.Label
                proxy.Shape = shape
                proxy.ViewObject.ShapeAppearance = source.ViewObject.ShapeAppearance
                objects.append(proxy)
                conversions.append(dict(file=filename, part_id=row['part_id'], checks=checks))
            temporary.recompute()
            ImportGui.export(objects, str(out / filename))
            assert digest == hashlib.sha256(native.read_bytes()).hexdigest()
        finally:
            App.closeDocument(temporary.Name)
            if opened:
                App.closeDocument(doc.Name)
    report = dict(passed=True, method='Exact NURBS surface conversion for selected STEP export proxies; native CAD remains unchanged. Final exported files require independent full round-trip audit.', conversions=conversions)
    (out / 'reports/step_surface_conversion.json').write_text(json.dumps(report, indent=2) + '\n')
    return report
