"""Calibrate HAC-015/HAC-016 controls against Nintendo front and rail views.

Local dimensions are image-derived estimates. Preserve the already supported
7.6 mm round caps, 15.8 mm stick caps, +/- keys and shoulder/release geometry.
"""
CONTROL_TARGETS = {
    'HomeOuterDiameter': 8.4, 'HomePressDiameter': 6.1,
    'HomeRingInnerDiameter': 6.3, 'CaptureWidth': 6.3,
    'CaptureSymbolDiameter': 4.1, 'SystemKeyX': 96.6,
    'ActionGlyphHeight': 3.05, 'RailKeyLength': 8.2,
    'RailKeyWidth': 3.6, 'RailUpperY': 23.5,
    'RailLowerY': -18.0, 'SyncDiameter': 3.1, 'SyncY': -6.0,
}
for row, (alias, value) in enumerate(CONTROL_TARGETS.items(), 22):
    PARAM.set('A' + str(row), alias)
    PARAM.set('B' + str(row), str(value) + ' mm')
    PARAM.setAlias('B' + str(row), alias)
    PARAM.set('C' + str(row), '图像拟合目标记录；修改几何需调整本轮源码并重建，非原厂公差')


def control_revision(key, shape, reason):
    saved_appearance = C[key].ViewObject.ShapeAppearance
    result = exterior_revision(key, shape, reason)
    result.ViewObject.ShapeAppearance = saved_appearance
    return result


def current_cut_tools(key):
    obj = C[key]
    while obj.TypeId == 'Part::Cut':
        yield obj.Tool
        obj = obj.Base


# The old glyphs were sized for the former 6.36 mm caps. Fit actual glyph
# height independently, then center each glyph on its current 7.6 mm cap.
for j, letter in enumerate(['X', 'A', 'B', 'Y']):
    key = 'ButtonGlyph' + letter
    shape = C[key].Shape.copy()
    b = shape.optimalBoundingBox(False, False)
    shape.translate(vec(-b.Center.x, -b.Center.y, -b.ZMin))
    shape.scale(CONTROL_TARGETS['ActionGlyphHeight'] / b.YLength)
    cap = C['JoyRFaceButton' + str(j)].Shape.optimalBoundingBox(False, False)
    shape.translate(vec(cap.Center.x, cap.Center.y, 15.36))
    control_revision(key, shape, 'ABXY 实际字高约 3.05 mm，按键帽中心居中；官方图像拟合')

for j in range(4):
    shape = Part.Face(Part.makePolygon([
        vec(-1.3, -1.1), vec(1.3, -1.1), vec(0, 1.1), vec(-1.3, -1.1)
    ])).extrude(vec(0, 0, .018))
    shape.rotate(vec(), vec(0, 0, 1), -j * 90)
    cap = C['JoyLFaceButton' + str(j)].Shape.optimalBoundingBox(False, False)
    shape.translate(vec(cap.Center.x, cap.Center.y, 15.36))
    control_revision('DpadArrow' + str(j), shape, '方向三角约 2.6 × 2.2 mm，按键帽中心居中')

# HOME has a larger light ring around a separate pressable grey center.
x, y = CONTROL_TARGETS['SystemKeyX'], -22.0
home_ring = Part.makeCylinder(4.2, .55, vec(x, y, 13.45)).cut(
    Part.makeCylinder(3.15, .75, vec(x, y, 13.35)))
control_revision('HomeRing', home_ring, 'HOME 外圈 8.4 mm、内孔 6.3 mm；图像拟合')
control_revision('HomeButton', Part.makeCylinder(3.05, 1.15, vec(x, y, 13.45)),
                 'HOME 可按中心 6.1 mm，与外圈分开测量')
exterior_move('HomeGlyph', (-.8, 0, 0))
appearance(C['HomeButton'], (.31, .32, .33), metal=.10, gloss=32)
appearance(C['HomeGlyph'], (.055, .06, .065), metal=.05, gloss=28)

capture = rr_shape(6.3, 6.3, .65, 1.3, (-x, y, 13.35))
control_revision('CaptureButton', capture, '截图键方形外轮廓 6.3 mm，中心向导轨移 0.8 mm')
capture_symbol = Part.makeCylinder(2.05, .018, vec(-x, y, 14.66)).cut(
    Part.makeCylinder(1.68, .038, vec(-x, y, 14.65)))
control_revision('CaptureGlyph', capture_symbol, '截图圆图案外径约 4.1 mm')

# V17 copied the original tools into a new front-shell chain. Edit those
# live copied tools, not the disconnected V6 openings; this also fills back
# the old system-key apertures when their centers move toward the rail.
for side, tag in [(-1, 'L'), (1, 'R')]:
    cx = side * 101.9
    stick_y, cluster_y = (25.3, -3.3) if tag == 'L' else (-3.3, 25.3)
    face_holes = [Part.makeCylinder(3.95, 2.5,
                  vec(cx + ux * 7.7, cluster_y + uy * 7.7, 12))
                  for ux, uy in [(0, 1), (1, 0), (0, -1), (-1, 0)]]
    openings = [Part.makeCylinder(6.35, 8, vec(cx, stick_y, 7.1))] + face_holes
    if side < 0:
        openings += [rr_shape(6.6, 6.6, .8, 2.5, (-x, y, 12)),
                     rr_shape(5.7, 2.05, .35, 2.5, (-92.5, 41.1, 12))]
    else:
        openings += [Part.makeCylinder(4.4, 2.5, vec(x, y, 12)),
                     rr_shape(5.7, 2, .25, 2.5, (92.5, 41.1, 12)),
                     rr_shape(2, 5.7, .25, 2.5, (92.5, 41.1, 12))]
    full_count = face_count = 0
    for tool in current_cut_tools('Joy' + tag + 'Front'):
        if tool.Label.startswith('参考图校准后的全部前面板按键孔'):
            tool.Shape = Part.makeCompound(openings)
            full_count += 1
        elif tool.Label.startswith('扩大面键孔，保持原中心位置'):
            tool.Shape = Part.makeCompound(face_holes)
            face_count += 1
    assert (full_count, face_count) == (1, 1), (tag, full_count, face_count)


def rail_letter_cut(shape, word, side, center_y):
    # Moulded recessed letters remain part of the button, rather than adding
    # a separate physical part to the bill of materials.
    font = ROOT / 'references/DejaVuSans.ttf'
    faces = [Part.makeFace(w, 'Part::FaceMakerBullseye')
             for w in Part.makeWireString(word, str(font.parent) + '/', font.name, 2.2) if w]
    letters = Part.makeCompound([f.extrude(vec(0, 0, .10)) for f in faces])
    bb = letters.optimalBoundingBox(False, False)
    letters.translate(vec(-bb.Center.x, -bb.Center.y, 0))
    letters.Placement = App.Placement(vec(side * 84.13, center_y, 7.4),
                                     rotation(normal=(-side, 0, 0), up=(0, 0, 1))).multiply(letters.Placement)
    result = shape.cut(letters)
    assert result.isValid() and len(result.Solids) == 1
    return result


for side, tag in [(-1, 'L'), (1, 'R')]:
    inward = App.Rotation(vec(0, 0, 1), vec(-side, 0, 0))
    outward = App.Rotation(vec(0, 0, 1), vec(side, 0, 0))
    # Viewed upright from the rail: L has SL above SR; R has SR above SL.
    positions = [('SL', 23.5), ('SR', -18.0)] if tag == 'L' else [('SR', 23.5), ('SL', -18.0)]
    for word, center_y in positions:
        shape = rr_shape(3.6, 8.2, 1.0, .75, (side * 84.8, center_y, 7.4), inward)
        shape = rail_letter_cut(shape, word, side, center_y)
        control_revision('Joy' + tag + word, shape, 'SL/SR 约 3.6 × 8.2 mm；校正右手柄上下键身份并补凹字')
    holes = [t for t in current_cut_tools('Joy' + tag + 'RailTongue')
             if t.Label.startswith('SL/SR 活动孔')]
    assert len(holes) == 2
    # Tool order is newest first; the union is independent of that order.
    for tool, center_y in zip(holes, [23.5, -18.0]):
        tool.Shape = rr_shape(3.9, 8.5, 1.1, 1.95, (side * 83.25, center_y, 7.4), outward)
    sync = Part.makeCylinder(1.55, .65, vec(side * 84.75, -6, 7.4), vec(-side, 0, 0))
    control_revision('Joy' + tag + 'Sync', sync, 'SYNC 约 3.1 mm，位于四灯下方，中心 Y=-6 mm')
    for j, center_y in enumerate([12.0, 8.0, 4.0, 0.0], 1):
        key = 'Joy' + tag + 'LED' + str(j)
        bb = C[key].Shape.optimalBoundingBox(False, False)
        exterior_move(key, (0, center_y - bb.Center.y, 7.4 - bb.Center.z))
    apertures = [C['Joy' + tag + 'Sync'].Shape] + [C['Joy' + tag + 'LED' + str(j)].Shape for j in range(1, 5)]
    apertures.append(Part.makeCylinder(2.75, .35, vec(side * 84.05, -6, 7.4), vec(side, 0, 0)))
    tool = next(t for t in current_cut_tools('Joy' + tag + 'RailTongue')
                if t.Label.startswith('SYNC 与灯窗安装位'))
    tool.Shape = Part.makeCompound(apertures)

    # Accessory actuator and guide-window positions follow their mating
    # controls. Accessory dimensions remain schematic, not manufacturer data.
    for j, center_y in enumerate([12.0, 8.0, 4.0, 0.0]):
        key = 'GripLEDWindow' + str(side) + '_' + str(j)
        bb = C[key].Shape.optimalBoundingBox(False, False)
        exterior_move(key, (0, GRIP_Y + center_y - bb.Center.y, 0))
    for j, center_y in enumerate([-18.0, 23.5]):
        key = 'Strap' + tag + 'Button' + str(j)
        bb = C[key].Shape.optimalBoundingBox(False, False)
        exterior_move(key, (0, -327 + center_y - bb.Center.y, 0))

D.recompute()
for obj in C.values():
    assert obj.Shape.isValid() and not obj.Shape.isNull(), obj.PartID
    obj.ViewObject.DisplayMode = 'Shaded'
RESULT = stage_done(18, 'control_proportions',
    '逐项核对 Joy-Con 26 个操作件：修正 HOME/截图键和字样比例，侧键尺寸与位置、右侧 SL/SR 身份、SYNC 及灯列；保留参考支持的摇杆、圆面键、加减键和肩键尺寸。局部数值为图像拟合。',
    views=[('front', {'assemblies': HANDHELD_GROUPS, 'span': 136, 'size': (2400, 1400)}),
           ('left_controls', {'assemblies': ['JoyLeft','JoyRailL'], 'target': (-103,0,14), 'span': 108, 'size': (700,1300)}),
           ('right_controls', {'assemblies': ['JoyRight','JoyRailR'], 'target': (103,0,14), 'span': 108, 'size': (700,1300)}),
           ('left_rail', {'assemblies': ['JoyLeft','JoyRailL'], 'normal': (1,0,0), 'target': (-84,0,7.4), 'span': 108, 'size': (700,1300)}),
           ('right_rail', {'assemblies': ['JoyRight','JoyRailR'], 'normal': (-1,0,0), 'target': (84,0,7.4), 'span': 108, 'size': (700,1300)})],
    extra={'basis': 'references/control_calibration.json', 'factory_equivalence_verified': False,
           'retained': 'round cap and stick diameters, +/- and shoulder/trigger/release profiles',
           'local_control_tolerance': 'Image interpretation uncertainty approximately 0.3-0.5 mm; not a physical manufacturing tolerance'})
