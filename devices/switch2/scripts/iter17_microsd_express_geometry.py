"""Nominal microSD envelope and the two-row SD7.1 contact arrangement.

11 x 15 x 1 mm comes from the SD Association form-factor diagram. The
16-contact option follows its SD7.1 illustration; an optional seventeenth
1.2 V contact is not assumed. Keying, pad lengths and reader clearances are
diagram-fitted study geometry, not a manufacturer tolerance drawing.
"""


def replace_micro_part(key, shape, reason):
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
points = [vec(-85+x, -22.4+y, 1.96) for x, y in outline]
card = Part.Face(Part.makePolygon(points+[points[0]])).extrude(vec(0, 0, 1.0))
pad_shapes = []
for i in range(8):
    # Legacy contact pitch is 1.1 mm in the Hirose DM3 drawing. Remaining pad
    # dimensions are fitted to the SDA drawing rather than claimed exact.
    pad_shapes.append(rr_shape(.68, 3.0, .04, .025,
                               (-85+(i-3.5)*1.1, -17.0, 2.935)))
for i in range(8):
    pad_shapes.append(rr_shape(.58, 1.65, .04, .025,
                               (-85+(i-3.5)*1.0, -20.1, 2.935)))
card = card.cut(Part.makeCompound(pad_shapes))
replace_micro_part('MicroSDCard', card,
                   'SDA nominal 11 x 15 x 1 mm card; diagram-fitted keying and flush contacts')
for i, shape in enumerate(pad_shapes):
    key = 'MicroSDPad'+str(i)
    if key in C:
        obj = replace_micro_part(key, shape, 'Flush legacy-row microSD Express card contact')
    else:
        obj = feature(key, 'microSD Express second-row card contact', shape,
                      'TabletInternal', -3, 'gold', True)
    obj.Label = 'microSD Express '+('legacy' if i < 8 else 'PCIe')+' card pad '+str(i+1)

# Accommodate the corrected 1 mm card with 0.06 / 0.08 mm vertical clearance.
# The reader remains a structural approximation, not an identified connector.
cage = rr_shape(13, 16, .5, 1.4, (-85, -22, 1.75))
channel = rr_shape(11.5, 16.4, .25, 1.14, (-85, -22, 1.90))
replace_micro_part('MicroSDCage', cage.cut(channel),
                   'Card channel enlarged for nominal 1 mm microSD thickness')
D.recompute()
assert len([key for key in C if key.startswith('MicroSDPad')]) == 16
card_bound = C['MicroSDCard'].Shape.optimalBoundingBox(False, False)
assert max(abs(a-b) for a, b in zip(
    [card_bound.XLength, card_bound.YLength, card_bound.ZLength], [11, 15, 1])) < 1e-6
RESULT = stage_done(
    17, 'microsd_express_geometry',
    '按 SD Association 资料将示意 microSD Express 卡修正为 11×15×1 mm、两排共 16 个接点，增加防误插轮廓并扩充卡座净空；局部轮廓和接点尺寸为图示拟合。',
    views=[('card', {'normal': (0, 0, 1), 'target': (-85, -22.4, 2.5),
                     'span': 18, 'size': (1400, 1200), 'assemblies': ['TabletInternal'],
                     'exclude': [key for key in C if key != 'MicroSDCard' and not key.startswith('MicroSDPad')]}),
           ('reader', {'normal': (.2, -.3, -2), 'target': (-85, -22, 2.5),
                       'span': 25, 'assemblies': ['TabletInternal'],
                       'exclude': [key for key in C if not key.startswith('MicroSD')]})],
    extra={'nominal_card_mm': [11, 15, 1], 'contact_rows': [8, 8],
           'optional_1v2_contact_modeled': False, 'factory_equivalence_verified': False})
print(json.dumps(RESULT, ensure_ascii=False))
