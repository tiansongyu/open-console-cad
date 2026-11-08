"""Nominal microSD UHS-I card envelope, keying and flush card contacts.

11 x 15 x 1 mm comes from the SD Association form-factor diagram. The
eight-contact legacy option is retained for HAC-001. Keying, pad lengths and
reader clearances are diagram-fitted study geometry, not a tolerance drawing.
"""


def replace_revision_part(key, shape, reason):
    previous = C[key]
    order = list(C.items())
    previous.PhysicalPart = False
    result = feature(key, previous.Label, shape, previous.Assembly,
                     previous.ExplodeLayer, previous.MaterialDescription, True)
    result.addProperty('App::PropertyLink', 'PreviousRevision', 'Revision')
    result.PreviousRevision = previous
    result.addProperty('App::PropertyString', 'RevisionReason', 'Revision')
    result.RevisionReason = reason
    if 'PartNumber' in previous.PropertiesList:
        result.addProperty('App::PropertyString', 'PartNumber', 'CAD study')
        result.PartNumber = previous.PartNumber
    result.ViewObject.ShapeAppearance = previous.ViewObject.ShapeAppearance
    previous.Visibility = False
    C.clear()
    C.update((part_id, result if part_id == key else obj) for part_id, obj in order)
    return result


# Contact end points toward +Y. The outline keeps the SDA nominal envelope;
# asymmetric keying is fitted to Figure 2 in the SDA June 2020 white paper.
outline = [(-4.25, 7.5), (5.15, 7.5), (5.5, 7.15), (5.5, -7.15),
           (5.15, -7.5), (-5.15, -7.5), (-5.5, -7.15), (-5.5, -2.25),
           (-4.9, -1.65), (-4.9, -.45), (-5.5, -.45), (-5.5, 1.0),
           (-4.25, 2.25)]
points = [vec(65+x, -38.8+y, 1.96) for x, y in outline]
card = Part.Face(Part.makePolygon(points+[points[0]])).extrude(vec(0, 0, 1.0))
pad_shapes = []
for i in range(8):
    # Legacy contact pitch is 1.1 mm in the Hirose DM3 drawing. Remaining pad
    # dimensions are fitted to the SDA drawing rather than claimed exact.
    pad_shapes.append(rr_shape(.68, 3.0, .04, .025,
                               (65+(i-3.5)*1.1, -33.4, 2.935)))
card = card.cut(Part.makeCompound(pad_shapes))
replace_revision_part('MicroSDCard', card,
                   'SDA nominal 11 x 15 x 1 mm card; diagram-fitted keying and flush contacts')
for i, shape in enumerate(pad_shapes):
    key = 'MicroSDPad'+str(i)
    obj = replace_revision_part(key, shape, 'Flush legacy-row microSD UHS-I card contact')
    obj.Label = 'microSD UHS-I card pad '+str(i+1)

# Accommodate the corrected 1 mm card with 0.06 / 0.08 mm vertical clearance.
# Increase the cage height to retain a roof around the corrected card.
# The reader remains a structural approximation, not an identified connector.
cage = rr_shape(13.4, 13.8, .4, 1.5, (65, -39, 1.7))
channel = rr_shape(11.5, 13.9, .20, 1.14, (65, -39, 1.90))
replace_revision_part('MicroSDCage', cage.cut(channel),
                   'Card channel enlarged for nominal 1 mm microSD thickness')


def repair_delta(before, after, allow_invalid_legacy_residual=False):
    assert before.isValid() and after.isValid() and before.Solids and after.Solids
    volumes, valid, null, errors = [], [], [], []
    for left, right in [(before, after), (after, before)]:
        try:
            residual = left.cut(right)
            empty = residual.isNull()
            # OCCT can represent an empty difference as a null shape.
            volumes.append(0.0 if empty else sum(abs(solid.Volume) for solid in residual.Solids))
            valid.append(empty or residual.isValid())
            null.append(empty)
            errors.append(None)
        except Exception as error:
            if not allow_invalid_legacy_residual:
                raise
            volumes.append(None)
            valid.append(False)
            null.append(None)
            errors.append(str(error))
    if not allow_invalid_legacy_residual:
        assert all(valid)
    return {'removed_added_mm3': volumes, 'residual_valid': valid,
            'residual_null': null, 'boolean_errors': errors}


STRICT_REPAIRS = []
# Unite overlapping text solids instead of counting their overlapping volumes
# twice. Bidirectional material differences are required to be empty.
old = C['TegraMark'].Shape.copy()
letters = old.Solids
united = letters[0].multiFuse(letters[1:]).removeSplitter()
united.check(True)
delta = repair_delta(old, united)
assert max(delta['removed_added_mm3']) <= 1e-6, delta
replace_revision_part('TegraMark', united, 'Union intersecting glyphs; verified empty bidirectional material difference')
STRICT_REPAIRS.append({'part_id': 'TegraMark', 'method': 'glyph union',
                       **delta, 'material_equivalent': True})

# Keep the unrefined cut: refinement creates an invalid edge/p-curve pair on
# these small speaker shells. Preserve the editable Boolean history.
for key in ['SpeakerLHousing', 'SpeakerRHousing']:
    obj = C[key]
    old = obj.Shape.copy()
    assert obj.TypeId == 'Part::Cut', key
    obj.Refine = False
    D.recompute()
    obj.Shape.check(True)
    delta = repair_delta(old, obj.Shape)
    assert max(delta['removed_added_mm3']) <= 1e-6, (key, delta)
    STRICT_REPAIRS.append({'part_id': key, 'method': 'unrefined Boolean',
                           **delta, 'material_equivalent': True})

# Rebuild the original pitch/radius/wire dimensions with separate sweep faces
# at spline knots. This removes the single face's internal C0 seam. The old
# defective sweep is not exactly equivalent: retain its measured differences.
helix_edge = Part.makeHelix(.35, 14.0, 1.6).Edges[0]
curve = helix_edge.Curve
knots = ([helix_edge.FirstParameter]
         + [k for k in curve.getKnots()
            if helix_edge.FirstParameter+1e-9 < k < helix_edge.LastParameter-1e-9]
         + [helix_edge.LastParameter])
edges = [curve.toShape(a, b) for a, b in zip(knots, knots[1:])]
section = Part.Wire(Part.makeCircle(.105, edges[0].Vertexes[0].Point,
                                    edges[0].tangentAt(edges[0].FirstParameter)))
coil = Part.Wire(edges).makePipeShell([section], True, True)
coil.check(True)
for key in ['JoyLHapticCoil', 'JoyRHapticCoil']:
    old = C[key].Shape.copy()
    shape = coil.copy()
    shape.Placement = old.Placement
    shape.check(True)
    # The defective legacy sweep can itself yield invalid Boolean remnants;
    # retain that diagnostic, never turn it into an equivalence assertion.
    delta = repair_delta(old, shape, allow_invalid_legacy_residual=True)
    replace_revision_part(key, shape, 'Same-parameter segmented helix sweep; explicit nonzero differences from legacy C0 surface')
    STRICT_REPAIRS.append({'part_id': key, 'method': 'split helix at spline knots',
                           **delta, 'material_equivalent': all(delta['residual_valid']) and max(delta['removed_added_mm3']) <= 1e-6,
                           'comparison_limit': 'Legacy C0 sweep is not certified equivalent; invalid Boolean remnants are recorded when encountered',
                           'radius_pitch_height_wire_radius_mm': [1.6, .35, 14.0, .105]})

D.recompute()
assert len([key for key in C if key.startswith('MicroSDPad')]) == 8
card_bound = C['MicroSDCard'].Shape.optimalBoundingBox(False, False)
assert max(abs(a-b) for a, b in zip(
    [card_bound.XLength, card_bound.YLength, card_bound.ZLength], [11, 15, 1])) < 1e-6
RESULT = stage_done(
    19, 'microsd_nominal_geometry',
    '修正 microSD 标称尺寸、防误插轮廓及齐平接点；合并重叠字形、保留扬声器未精化布尔，并按原参数分段重建绕组。卡片局部轮廓仍为图示拟合，四个曲面壳的严格检查问题另行保留。',
    views=[('card', {'normal': (0, 0, 1), 'target': (65, -38.8, 2.5),
                     'span': 18, 'size': (1400, 1200), 'assemblies': ['TabletInternal'],
                     'exclude': [key for key in C if key != 'MicroSDCard' and not key.startswith('MicroSDPad')]}),
           ('reader', {'normal': (.2, -.3, -2), 'target': (65, -39, 2.5),
                       'span': 25, 'assemblies': ['TabletInternal'],
                       'exclude': [key for key in C if not key.startswith('MicroSD')]})],
    extra={'nominal_card_mm': [11, 15, 1], 'contact_rows': [8],
           'strict_repairs': STRICT_REPAIRS,
           'strict_unresolved_parts': ['JoyLFront', 'JoyRFront', 'JoyLRear', 'JoyRRear'],
           'factory_equivalence_verified': False})
print(json.dumps(RESULT, ensure_ascii=False))
