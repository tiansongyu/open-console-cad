"""Audit saved HAC-001 Joy-Con controls against declared image-fit targets.

Run in FreeCAD's Python environment (including its Mod path)::

    python audit_controls.py --output path/to/candidate/output

The output directory must contain Switch_Complete.FCStd. No manifest is
required. This reads serialized BReps without recomputing or saving the CAD
document. The numerical tolerance checks model consistency, not accuracy
against physical hardware or a manufacturer's production tolerances.
"""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys


AXES = ("x", "y", "z")
MODEL_TOLERANCE_MM = 1e-5
EXPECTED_PHYSICAL_COMPONENTS = 654
HANDHELD_GROUPS = {
    "Tablet", "Display", "TabletInternal", "JoyLeft", "JoyRight",
    "JoyRailL", "JoyRailR", "JoyInternalL", "JoyInternalR",
}
FITTED_BASIS = "Declared public-image fit; not a manufacturer dimension"
RETAINED_BASIS = "Retained V17 model geometry; not a hardware measurement"
PUBLIC_BASIS = "Nintendo published nominal overall envelope"


def control_targets():
    """Return all 26 operating controls; rings, glyphs and LEDs are separate."""
    targets = {}

    def add(key, size, center, basis=FITTED_BASIS, press_axis="z"):
        targets[key] = {
            "size_mm": dict(zip(AXES, size)),
            "center_mm": dict(zip(AXES, center)),
            "press_axis": press_axis,
            "basis": basis,
        }

    for tag, side in [("L", -1), ("R", 1)]:
        cx = side * 101.9
        stick_y = 25.3 if tag == "L" else -3.3
        cluster_y = -3.3 if tag == "L" else 25.3
        add(f"Joy{tag}StickCap", (15.8, 15.8, 2.8),
            (cx, stick_y, 21.6), RETAINED_BASIS)
        for j, (ux, uy) in enumerate([(0, 1), (1, 0), (0, -1), (-1, 0)]):
            add(f"Joy{tag}FaceButton{j}", (7.6, 7.6, 2.0),
                (cx + ux * 7.7, cluster_y + uy * 7.7, 14.35), RETAINED_BASIS)
        # Curved shoulders use axis-aligned bounds, not band width or pivot position.
        add(f"Joy{tag}Bumper", (27.27929989067327, 17.5, 2.6),
            (side * 105.63964994533663, 42.25, 11.5), RETAINED_BASIS)
        add(f"Joy{tag}Trigger", (24.9, 13.22993294843657, 6.9),
            (side * 104.45, 42.98711714353128, -1.95), RETAINED_BASIS)
        add(f"Joy{tag}Release", (4.7, 4.7, 1.4),
            (side * 90.9, 38.0, -.95), RETAINED_BASIS)
        top_key, bottom_key = ("SL", "SR") if tag == "L" else ("SR", "SL")
        for suffix, y in [(top_key, 23.5), (bottom_key, -18.0)]:
            add(f"Joy{tag}{suffix}", (.75, 8.2, 3.6),
                (side * 84.425, y, 7.4), press_axis="x")
        add(f"Joy{tag}Sync", (.65, 3.1, 3.1),
            (side * 84.425, -6.0, 7.4), press_axis="x")

    add("MinusButton", (5.4, 1.75, 1.5), (-92.5, 41.1, 14.05), RETAINED_BASIS)
    add("PlusButton", (5.4, 5.4, 1.5), (92.5, 41.1, 14.05), RETAINED_BASIS)
    add("CaptureButton", (6.3, 6.3, 1.3), (-96.6, -22.0, 14.0))
    add("HomeButton", (6.1, 6.1, 1.15), (96.6, -22.0, 14.025))
    assert len(targets) == 26
    return targets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().parents[1] / "output",
                        help="Directory containing Switch_Complete.FCStd and reports/")
    parser.add_argument("--tolerance", type=float, default=MODEL_TOLERANCE_MM,
                        help="Numerical model comparison tolerance in mm, not hardware accuracy")
    args = parser.parse_args()
    if not math.isfinite(args.tolerance) or args.tolerance <= 0:
        parser.error("--tolerance must be finite and positive")

    library = os.environ.get("PATH_TO_FREECAD_LIBDIR")
    if library:
        sys.path.insert(0, library)
        sys.path.insert(0, str(Path(library).parent / "Mod"))
    import FreeCAD as App
    import Part
    import PartDesign  # Restore native construction types, even without recomputing.
    import Sketcher
    import Spreadsheet

    output = args.output.resolve()
    source = output / "Switch_Complete.FCStd"
    repo = Path(__file__).resolve().parents[3]
    report = {
        "model": "Nintendo Switch HAC-001 / original Joy-Con",
        "source": source.relative_to(repo).as_posix() if source.is_relative_to(repo) else source.name,
        "geometry_evaluation": "Read-only saved BRep; no feature-history recompute",
        "scope": "Consistency with declared image-fit targets and published overall envelopes",
        "factory_equivalence_verified": False,
        "physical_hardware_accuracy_verified": False,
        "numerical_tolerance_mm": args.tolerance,
        "tolerance_scope": "CAD arithmetic only; not a manufacturing or physical-device tolerance",
        "expected_operating_controls": 26,
        "expected_physical_components": EXPECTED_PHYSICAL_COMPONENTS,
        "checks": [],
        "operating_controls": [],
    }
    doc = None
    checks = report["checks"]

    def check(name, actual, expected, basis):
        delta = abs(actual - expected)
        checks.append({"name": name, "actual_mm": actual, "expected_mm": expected,
                       "absolute_error_mm": delta, "basis": basis,
                       "passed": math.isfinite(actual) and delta <= args.tolerance})

    def error(name, exc):
        checks.append({"name": name, "error": str(exc), "passed": False})

    try:
        report["source_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
        doc = App.openDocument(str(source))
        physical = [obj for obj in doc.Objects if getattr(obj, "PhysicalPart", False)]
        parts = {}
        duplicates = []
        invalid = []
        solids = 0
        for obj in physical:
            key = getattr(obj, "PartID", "")
            if not key or key in parts:
                duplicates.append({"name": obj.Name, "part_id": key})
            parts[key] = obj
            try:
                shape = obj.Shape
                valid = not shape.isNull() and bool(shape.Solids) and shape.isValid() and shape.Volume > 0
                solids += len(shape.Solids)
            except Exception:
                valid = False
            if not valid:
                invalid.append({"name": obj.Name, "part_id": key})
        report.update(physical_components_checked=len(physical), physical_solids=solids,
                      duplicate_or_missing_part_ids=duplicates, invalid_physical_components=invalid)

        def geometry(key):
            box = parts[key].Shape.optimalBoundingBox(False, False)
            return ({axis: getattr(box, axis.upper() + "Length") for axis in AXES},
                    dict(zip(AXES, [box.Center.x, box.Center.y, box.Center.z])))

        def inspect(key, size=None, center=None, basis=FITTED_BASIS):
            dimensions, position = geometry(key)
            for axis, expected in (size or {}).items():
                check(key + ".size." + axis, dimensions[axis], expected, basis)
            for axis, expected in (center or {}).items():
                check(key + ".bbox_center." + axis, position[axis], expected, basis)
            return dimensions, position

        for key, target in control_targets().items():
            try:
                dimensions, position = inspect(key, target["size_mm"], target["center_mm"], target["basis"])
                report["operating_controls"].append({
                    "part_id": key, "object": parts[key].Name,
                    "size_xyz_mm": dimensions, "bbox_center_xyz_mm": position,
                    "press_axis": target["press_axis"],
                    "axis_note": "Rail controls: Y/Z are face dimensions, X is axial thickness"
                                 if target["press_axis"] == "x" else "Z is model depth",
                })
            except Exception as exc:
                error(key, exc)

        for tag in "LR":
            try:
                centers = [geometry(f"Joy{tag}FaceButton{j}")[1] for j in range(4)]
                check(f"Joy{tag}.face_cluster_horizontal_pitch", abs(centers[1]["x"] - centers[3]["x"]) / 2,
                      7.7, RETAINED_BASIS)
                check(f"Joy{tag}.face_cluster_vertical_pitch", abs(centers[0]["y"] - centers[2]["y"]) / 2,
                      7.7, RETAINED_BASIS)
            except Exception as exc:
                error(f"Joy{tag}.face_cluster_pitch", exc)

        for key, size, center in [
            ("HomeRing", {"x": 8.4, "y": 8.4, "z": .55}, {"x": 96.6, "y": -22.0, "z": 13.725}),
            ("CaptureGlyph", {"x": 4.1, "y": 4.1}, {"x": -96.6, "y": -22.0}),
        ]:
            try:
                inspect(key, size, center)
            except Exception as exc:
                error(key, exc)
        try:
            # Planar ring bounds give its outside diameter. Cylindrical surfaces
            # separately establish the hole diameter without confusing a fillet.
            radii = [face.Surface.Radius for face in parts["HomeRing"].Shape.Faces
                     if isinstance(face.Surface, Part.Cylinder)]
            if len(radii) < 2:
                raise ValueError("HomeRing must expose inner and outer cylindrical surfaces")
            check("HomeRing.inner_diameter", 2 * min(radii), 6.3, FITTED_BASIS)
        except Exception as exc:
            error("HomeRing.inner_diameter", exc)

        for j, char in enumerate(["X", "A", "B", "Y"]):
            for key, face, size in [
                ("ButtonGlyph" + char, f"JoyRFaceButton{j}", {"y": 3.05}),
                (f"DpadArrow{j}", f"JoyLFaceButton{j}",
                 {"x": 2.6, "y": 2.2} if j % 2 == 0 else {"x": 2.2, "y": 2.6}),
            ]:
                try:
                    center = geometry(face)[1]
                    inspect(key, size, {axis: center[axis] for axis in ("x", "y")})
                except Exception as exc:
                    error(key, exc)
        for tag in "LR":
            for j, y in enumerate([12.0, 8.0, 4.0, 0.0], 1):
                try:
                    inspect(f"Joy{tag}LED{j}", center={"y": y, "z": 7.4})
                except Exception as exc:
                    error(f"Joy{tag}LED{j}", exc)

        # Bounds alone also pass for a completely unlettered key. Independently
        # construct the declared blank and measure the two recessed characters.
        # This does not import or execute the modeling stage being audited.
        for tag, side in [("L", -1), ("R", 1)]:
            positions = [("SL", 23.5), ("SR", -18.0)] if tag == "L" else [("SR", 23.5), ("SL", -18.0)]
            for word, center_y in positions:
                key = "Joy" + tag + word
                try:
                    blank = Part.makeBox(3.6, 8.2, .75, App.Vector(-1.8, -4.1, 0))
                    blank = blank.makeFillet(1.0, [edge for edge in blank.Edges
                                                  if edge.BoundBox.ZLength > .74])
                    blank.Placement = App.Placement(
                        App.Vector(side * 84.8, center_y, 7.4),
                        App.Rotation(App.Vector(0, 0, 1), App.Vector(-side, 0, 0)),
                    )
                    actual = parts[key].Shape
                    removed, added = blank.cut(actual), actual.cut(blank)
                    has_recesses = bool(removed.Solids) and removed.isValid()
                    bounds = removed.optimalBoundingBox(False, False) if has_recesses else None
                    depth = bounds.XLength if bounds is not None else None
                    center = [bounds.Center.x, bounds.Center.y, bounds.Center.z] if bounds is not None else None
                    volume_tolerance = 1e-6
                    expected_center = [side * 84.09, center_y, 7.4]
                    checks.append({
                        "name": key + ".engraving",
                        "basis": "Declared recessed SL/SR lettering; model geometry check only",
                        "method": "Independent rounded-box blank; subtract saved key and reverse-subtract blank",
                        "blank_volume_mm3": blank.Volume,
                        "actual_volume_mm3": actual.Volume,
                        "removed_volume_mm3": removed.Volume,
                        "added_volume_mm3": added.Volume,
                        "volume_tolerance_mm3": volume_tolerance,
                        "removed_solids": len(removed.Solids),
                        "expected_removed_solids": 2,
                        "actual_depth_mm": depth,
                        "expected_depth_mm": .08,
                        "removed_bbox_center_xyz_mm": center,
                        "expected_removed_bbox_center_xyz_mm": expected_center,
                        "passed": (
                            has_recesses and removed.Volume > volume_tolerance
                            and added.Volume <= volume_tolerance
                            and len(removed.Solids) == 2
                            and abs(depth - .08) <= args.tolerance
                            and all(abs(a - b) <= args.tolerance for a, b in zip(center, expected_center))
                        ),
                    })
                except Exception as exc:
                    error(key + ".engraving", exc)

        for name, groups, expected in [
            ("handheld", HANDHELD_GROUPS, (239.0, 102.0, 28.4)),
            ("joy_left", {"JoyLeft", "JoyRailL", "JoyInternalL"}, (35.9, 102.0, 28.4)),
            ("joy_right", {"JoyRight", "JoyRailR", "JoyInternalR"}, (35.9, 102.0, 28.4)),
        ]:
            try:
                shapes = [obj.Shape for obj in parts.values() if obj.Assembly in groups]
                if not shapes:
                    raise ValueError("No components in requested assembly groups")
                box = Part.makeCompound(shapes).optimalBoundingBox(False, False)
                for axis, nominal in zip(AXES, expected):
                    check(name + ".envelope." + axis, getattr(box, axis.upper() + "Length"), nominal, PUBLIC_BASIS)
            except Exception as exc:
                error(name + ".envelope", exc)
    except Exception as exc:
        error("document", exc)
    finally:
        if doc is not None:
            App.closeDocument(doc.Name)

    report["inputs_unchanged"] = source.exists() and (
        hashlib.sha256(source.read_bytes()).hexdigest() == report.get("source_sha256"))
    report["passed"] = (
        report["inputs_unchanged"]
        and report.get("physical_components_checked") == EXPECTED_PHYSICAL_COMPONENTS
        and not report.get("duplicate_or_missing_part_ids")
        and not report.get("invalid_physical_components")
        and len(report["operating_controls"]) == 26
        and bool(checks) and all(row["passed"] for row in checks)
    )
    report_path = output / "reports" / "control_calibration_audit.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"passed": report["passed"], "operating_controls": len(report["operating_controls"]),
                      "checks": len(checks), "failed_checks": sum(not row["passed"] for row in checks),
                      "report": str(report_path)}, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
