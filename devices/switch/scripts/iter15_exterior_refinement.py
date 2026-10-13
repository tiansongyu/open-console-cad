"""HAC-001 exterior revision, measured against Nintendo's orthographic images.

Run after iteration 14. Overall dimensions are published; the local surface
radii and image-derived control locations are estimates, not factory CAD.
"""

REFINEMENT_CHANGED = set()


def exterior_revision(key, shape, reason):
    old = C[key]
    old.PhysicalPart = False
    new = feature(key, old.Label, shape, old.Assembly, old.ExplodeLayer,
                  old.MaterialDescription, old.Fidelity.startswith('Schematic'))
    new.addProperty('App::PropertyLink', 'PreviousRevision', 'Revision')
    new.PreviousRevision = old
    new.addProperty('App::PropertyString', 'RevisionReason', 'Revision')
    new.RevisionReason = reason
    if 'PartNumber' in old.PropertiesList:
        new.addProperty('App::PropertyString', 'PartNumber', 'CAD study')
        new.PartNumber = old.PartNumber
    old.Visibility = False
    REFINEMENT_CHANGED.add(key)
    return new


def exterior_move(key, delta):
    obj = C[key]
    obj.Placement.Base = obj.Placement.Base + vec(*delta)
    REFINEMENT_CHANGED.add(key)


def roll_face(shape, z, radius):
    edges = [e for e in shape.Edges if e.BoundBox.ZLength < 1e-6
             and abs(e.BoundBox.ZMin - z) < 1e-6]
    assert edges, 'No perimeter edges at requested height'
    result = shape.makeFillet(radius, edges)
    assert result.isValid() and len(result.Solids) == 1
    return result


# Exposed driving dimensions remain editable in the native feature history.
for row, (alias, value, note) in enumerate([
    ('JoyOuterRadius', 20.5, '官方正视图拟合；非原厂尺寸'),
    ('JoyInnerRadius', .65, '贴轨侧小圆角；图像估计'),
    ('JoyFrontRoll', 1.8, '前壳厚度方向圆角；图像估计'),
    ('JoyRearRoll', 3.1, '后壳厚度方向圆角；图像估计'),
    ('TabletRearRoll', 2.8, '主机背面周边滚圆；图像估计'),
    ('FaceButtonPitch', 7.7, '正视图按钮中心距；图像估计'),
], 12):
    PARAM.set('A' + str(row), alias)
    PARAM.set('B' + str(row), str(value) + ' mm')
    PARAM.setAlias('B' + str(row), alias)
    PARAM.set('C' + str(row), note)
D.recompute()


def native_joy_shell(tag, side, front):
    key = 'Joy' + tag + ('Front' if front else 'Rear')
    old = C[key]
    z, depth, roll = (7.5, 6.4, 1.8) if front else (-1.3, 8.6, 3.1)
    body = rounded_body(D, key + 'Contour15', old.Label + ' · 曲面原坯',
                        33, 102, 0, depth, (side * 103, 0, z),
                        color=PALETTE['blue' if side < 0 else 'red'],
                        expr={'Height': 'Parameters.JoyHeight'})
    tip = body.Tip
    for label, x, radius, alias in [
        ('Outer', side * 16.5, 20.5, 'JoyOuterRadius'),
        ('RailSide', -side * 16.5, .65, 'JoyInnerRadius'),
    ]:
        names = ['Edge%d' % (i + 1) for i, e in enumerate(tip.Shape.Edges)
                 if e.BoundBox.ZLength > depth - 1e-6
                 and abs(e.BoundBox.XMin - x) < 1e-6]
        fillet = body.newObject('PartDesign::Fillet', key + label + '15')
        fillet.Base = (tip, names)
        fillet.Radius = radius
        fillet.setExpression('Radius', 'Parameters.' + alias)
        body.Tip = fillet
        D.recompute()
        tip.Visibility = False
        tip = fillet
        assert not tip.Shape.isNull() and tip.Shape.isValid(), key + label
    level = depth if front else 0
    names = ['Edge%d' % (i + 1) for i, e in enumerate(tip.Shape.Edges)
             if e.BoundBox.ZLength < 1e-6
             and abs(e.BoundBox.ZMin - level) < 1e-6]
    fillet = body.newObject('PartDesign::Fillet', key + 'PerimeterRoll15')
    fillet.Base = (tip, names)
    fillet.Radius = roll
    fillet.setExpression('Radius', 'Parameters.' + ('JoyFrontRoll' if front else 'JoyRearRoll'))
    body.Tip = fillet
    D.recompute()
    tip.Visibility = False
    assert fillet.Shape.isValid() and len(fillet.Shape.Solids) == 1, key
    old.PhysicalPart = False
    register(body, key, old.Assembly, old.ExplodeLayer, old.MaterialDescription)
    if 'PartNumber' in old.PropertiesList:
        body.addProperty('App::PropertyString', 'PartNumber', 'CAD study')
        body.PartNumber = old.PartNumber
    body.addProperty('App::PropertyLink', 'PreviousRevision', 'Revision')
    body.PreviousRevision = old
    old.Visibility = False
    cavity = joy_outline_shape(30.4, 99.4, 19.2, .5,
                              5.5 if front else 7.8,
                              (side * 103, 0, 7.25 if front else -.15), side)
    cavity = roll_face(cavity, 12.75 if front else -.15, .7 if front else 2.0)
    cut(key, cavity, '等壁厚圆润内腔')
    REFINEMENT_CHANGED.add(key)
    return body.Shape.copy()


# Control positions from the official 102 mm high Joy-Con front view.
for side, tag in [(-1, 'L'), (1, 'R')]:
    dx = -side * 1.1
    dy = 0 if tag == 'L' else 8.7
    for suffix in ['StickCollar', 'StickBoot', 'StickStem', 'StickCap',
                   'GimbalHousing', 'GimbalRing', 'GimbalX', 'GimbalY0',
                   'GimbalY1', 'Pot0', 'Pot1']:
        exterior_move('Joy' + tag + suffix, (dx, dy, 0))
    if tag == 'R':
        exterior_move('JoyRNFCAntenna', (dx, dy, 0))
    cy = -3.3 if tag == 'L' else 25.3
    old_cy = -8.2 if tag == 'L' else 25.1
    for j, (ux, uy) in enumerate([(0, 1), (1, 0), (0, -1), (-1, 0)]):
        delta = (dx + ux * (7.7 - 9.4), cy - old_cy + uy * (7.7 - 9.4), 0)
        for suffix in ['FaceButton', 'ButtonStem', 'ButtonPad', 'ButtonDome']:
            exterior_move('Joy' + tag + suffix + str(j), delta)
        exterior_move('DpadArrow' + str(j) if tag == 'L' else
                      'ButtonGlyph' + ['X', 'A', 'B', 'Y'][j], delta)
    for key in (['CaptureButton', 'CaptureGlyph'] if tag == 'L' else
                ['HomeRing', 'HomeButton', 'HomeGlyph']):
        exterior_move(key, (0, 12.5, 0))

D.recompute()
JOY_ENVELOPES = {}
for side, tag in [(-1, 'L'), (1, 'R')]:
    (OUT / 'reports/refinement_progress.json').write_text(json.dumps({'stage': 'shell', 'side': tag}))
    x = side * 103
    assembly = 'JoyLeft' if side < 0 else 'JoyRight'
    front_envelope = native_joy_shell(tag, side, True)
    rear_envelope = native_joy_shell(tag, side, False)
    JOY_ENVELOPES[tag] = (front_envelope, rear_envelope)
    # A fine recessed joint follows the revised outline, with no square ledge.
    seam = joy_outline_shape(32.8, 101.8, 20.4, .55, .16, (x, 0, 7.32), side)
    seam = seam.cut(joy_outline_shape(30.4, 99.4, 19.2, .5, .4, (x, 0, 7.2), side))
    exterior_revision('Joy' + tag + 'Seam', seam, '新轮廓连续分型缝')

    # A narrow shoulder rim replaces the old broad black rectangle.
    outer = joy_outline_shape(33, 102, 20.5, .65, 2.6, (x, 0, 10.2), side)
    inner = joy_outline_shape(30.0, 99.0, 19.0, .5, 3.0, (x, 0, 10.0), side)
    band = outer.cut(inner)
    clip = Part.makeBox(28, 18, 4, vec(92 if side > 0 else -120, 33.5, 10))
    bumper = band.common(clip)
    bumper = roll_face(bumper, 12.8, .28)
    exterior_revision('Joy' + tag + 'Bumper', bumper, '沿外轮廓弯曲的窄肩键')
    shoulder_tool = joy_outline_shape(33.6, 102.6, 20.8, .65, 5, (x, 0, 9.95), side)
    shoulder_tool = shoulder_tool.cut(joy_outline_shape(29.65, 98.65, 18.825, .45, 5.4, (x, 0, 9.8), side)).common(
        Part.makeBox(28.35, 18.5, 5.5, vec(91.825 if side > 0 else -120.175, 33.25, 9.8)))
    cut('Joy' + tag + 'Front', shoulder_tool, '弧形肩键运动间隙')

    # Rounded crescent trigger with an organic inner edge and a rail-side land.
    p = [(92.0, 49.6), (99.0, 49.6), (116.9, 36.4),
         (113.0, 37.0), (107.0, 40.4), (98.5, 42.0), (92.0, 44.1)]
    edges = [Part.makeLine(vec(*p[0]), vec(*p[1])),
             Part.Arc(vec(*p[1]), vec(110.2, 46.0), vec(*p[2])).toShape()]
    curve = Part.BSplineCurve()
    curve.interpolate([vec(*q) for q in p[2:]])
    edges += [curve.toShape(), Part.makeLine(vec(*p[-1]), vec(*p[0]))]
    trigger = Part.Face(Part.Wire(edges)).extrude(vec(0, 0, 6.9))
    trigger.translate(vec(0, 0, -5.4))
    trigger = roll_face(trigger, -5.4, .9)
    trigger = roll_face(trigger, 1.5, .65)
    if side < 0:
        trigger = trigger.mirror(vec(), vec(1, 0, 0))
    exterior_revision('Joy' + tag + 'Trigger', trigger, 'ZL/ZR 弯月形双面滚圆扳机')
    # A moulded seat extends into the rear shell without a rectangular cutout.
    (OUT / 'reports/refinement_progress.json').write_text(json.dumps({'stage': 'trigger seat', 'side': tag}))
    seat = trigger.makeOffsetShape(.18, .01)
    cut('Joy' + tag + 'Rear', seat, '弯曲扳机容置与活动间隙')
    axle = C['Joy' + tag + 'TriggerAxle']
    exterior_move('Joy' + tag + 'TriggerAxle', (0, 7.4, 0))
    cut('Joy' + tag + 'Trigger', axle.Shape, '扳机枢轴配合')
    cut('Joy' + tag + 'Rear', axle.Shape, '扳机枢轴穿孔')

    # Recessed round release buttons, rather than protruding rectangular blocks.
    release = Part.makeCylinder(2.35, 1.4, vec(side * 90.9, 38.0, -1.65))
    release = roll_face(release, -1.65, .22)
    exterior_revision('Joy' + tag + 'Release', release, '圆形释放键，官方背视图位置')
    cut('Joy' + tag + 'Rear', Part.makeCylinder(2.53, 2.4, vec(side * 90.9, 38, -1.9)), '圆形释放按钮孔')

    # Correct the rear screw pattern; bosses move with their matching fasteners.
    old = [(-8, -39), (8, -26), (-6.5, 22), (7, 28)]
    new = [(side * 90.6, -46), (side * 113.7, -38.4),
           (side * 90.5, 47.0), (side * 115.4, 31.8)]
    holes = []
    for j, ((ox, oy), (nx, ny)) in enumerate(zip(old, new)):
        delta = (nx - (x + ox), ny - oy, 0)
        exterior_move('Joy' + tag + 'Screw' + str(j + 1), delta)
        exterior_move('Joy' + tag + 'Boss' + str(j), delta)
        holes += [Part.makeCylinder(1.42, .62, vec(nx, ny, -1.4)),
                  Part.makeCylinder(.84, 2.0, vec(nx, ny, -1.4))]
    cut('Joy' + tag + 'Rear', holes, '修正后三翼螺钉沉孔')

    # Recreate the front apertures at the measured control locations.
    cx = x - side * 1.1
    sy = 25.3 if tag == 'L' else -3.3
    cy = -3.3 if tag == 'L' else 25.3
    openings = [Part.makeCylinder(6.35, 8, vec(cx, sy, 7.1))]
    for ux, uy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        openings.append(Part.makeCylinder(3.37, 2.5, vec(cx + ux * 7.7, cy + uy * 7.7, 12)))
    if side < 0:
        openings += [rr_shape(5.9, 5.9, .7, 2.5, (-97.4, -22, 12)),
                     rr_shape(5.7, 2.05, .35, 2.5, (-92.5, 41.1, 12))]
    else:
        openings += [Part.makeCylinder(3.75, 2.5, vec(97.4, -22, 12)),
                     rr_shape(5.7, 2, .25, 2.5, (92.5, 41.1, 12)),
                     rr_shape(2, 5.7, .25, 2.5, (92.5, 41.1, 12))]
    cut('Joy' + tag + 'Front', openings, '参考图校准后的全部前面板按键孔')

    # Keep schematic internals inside the more curved silhouette, and update
    # the board opening rather than leaving the old analogue-stick hole.
    pcb = joy_outline_shape(27.8, 93.4, 18.0, .7, .75, (x, 0, 9.45), side)
    pcb = pcb.cut(rr_shape(17.4, 17.4, 1.1, 1.2, (cx, sy, 9.2)))
    exterior_revision('Joy' + tag + 'PCB', pcb, 'PCB 随新外形及摇杆位置更新')

    # Shoulder legends are placed on their actual exposed surfaces.
    for key, text, size, pos, orient in [
        ('BumperLegend' + tag, tag, 1.8, (x - 1, 50.5, 10.7), YROT),
        ('TriggerLegend' + tag, 'Z' + tag, 2.0, (side * 101.0 + 2, 44.8, -5.385), BACKROT),
    ]:
        temp = printed_text(D, key + '15Glyph', text, text, size, pos, orient,
                            PALETTE['rubber'])
        exterior_revision(key, temp.Shape.copy(), '肩键标识随曲面位置更新')
        D.removeObject(temp.Name)
    cut('Joy' + tag + 'Trigger', C['TriggerLegend' + tag].Shape, '扳机浅色标记嵌层')

(OUT / 'reports/refinement_progress.json').write_text(json.dumps({'stage': 'tablet'}))
# The right IR insert follows the curved base, within the 102 mm envelope.
ir_tool = rr_shape(14.4, 6.2, .95, 1.5, (96.5, -49.5, 3.1), YROT)
ir = ir_tool.common(JOY_ENVELOPES['R'][1])
exterior_revision('IRWindow', ir, '红外窗口嵌入下缘曲面，不超出手柄包络')
cut('JoyRRear', ir_tool, '红外透镜曲面嵌位')

# Rounded tablet edges are taken from a shared continuous outer envelope.
envelope = rr_shape(173, 101, 3.8, 13.9)
envelope = roll_face(envelope, 0, 2.8)
envelope = roll_face(envelope, 13.9, .75)
for key in ['TabletFrame', 'TabletRear']:
    exterior_revision(key, C[key].Shape.common(envelope), '主机前后边缘连续滚圆')

# Set back the front glass to expose a narrow graphite rim, as on HAC-001.
bezel = rr_shape(171.0, 99.0, 3.1, .7, (0, 0, 13.2))
bezel = roll_face(bezel, 13.9, .16)
active_h = 6.2 * 25.4 / math.sqrt(16 * 16 + 9 * 9) * 9
active_w = active_h * 16 / 9
bezel = bezel.cut(rr_shape(active_w + .14, active_h + .14, .35, 1.2, (0, 0, 13.0)))
for side in [-1, 1]:
    for j in range(2):
        x = side * (57.5 + j * 11.5)
        bezel = bezel.cut(rr_shape(9.4, 1.0, .45, 1.1, (x, -44, 13.0)))
bezel = bezel.cut(Part.makeCylinder(.8, 1, vec(-76.6, -29.2, 13.0)))
exterior_revision('FrontBezel', bezel, '黑色面板细圆角及与机框之间的细边')

# Dark moulded direction / HOME symbols and natural neon body colours.
PALETTE.update(blue=(.00, .69, .84), red=(1.0, .24, .22),
               shell=(.18, .19, .20), bezel=(.032, .037, .043),
               screen=(.065, .080, .093), rubber=(.16, .17, .18))
for key, obj in C.items():
    colour = PALETTE[obj.MaterialDescription]
    if key.startswith('DpadArrow') or key == 'HomeGlyph':
        colour = (.10, .105, .11)
    appearance(obj, colour, metal=.32 if obj.MaterialDescription in ['metal', 'gold', 'copper'] else .23, gloss=38)
    obj.ViewObject.DisplayMode = 'Flat Lines'
    obj.ViewObject.Deviation = .035
    obj.ViewObject.AngularDeflection = 6
D.recompute()
(OUT / 'reports/refinement_progress.json').write_text(json.dumps({'stage': 'validate and save'}))
RESULT = stage_done(15, 'exterior_refinement',
    '对照 Nintendo HAC-001 官方正背侧视图重做 Joy-Con 20.5 mm 外侧圆弧、前后滚圆和窄肩键，'
    '更新弯月形扳机、圆释放键、螺钉分布、摇杆与面键布局，并软化主机边缘。局部尺寸为图像拟合。',
    views=[('front', {'assemblies': HANDHELD_GROUPS, 'span': 136, 'size': (2400, 1400)}),
           ('hero', {'assemblies': HANDHELD_GROUPS, 'normal': (-.38, .50, 1.5), 'span': 145, 'size': (2400, 1400)}),
           ('back', {'assemblies': HANDHELD_GROUPS, 'normal': (0, 0, -1), 'span': 136, 'size': (2400, 1400)}),
           ('edge', {'assemblies': HANDHELD_GROUPS, 'normal': (-.9, -.55, 1.8), 'target': (-104, -28, 7), 'span': 57, 'size': (1500, 1500)})],
    extra={'local_dimensions': 'Image-derived estimates, not manufacturer measurements',
           'changed_part_ids': sorted(REFINEMENT_CHANGED)})
