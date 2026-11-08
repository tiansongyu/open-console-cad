"""RVL-001 rear-panel and RVL-003 remote corrections from Nintendo diagrams."""
import Part
from .core import V
from .clamshell import _move
from .retro_common import fuse_feature
from .geometry import rotation, appearance
from .handheld_refinement import replace

REAR = rotation((0, 1, 0), (0, 0, 1))
FRONT = rotation((0, -1, 0), (0, 0, 1))


def _tools(m, label, expected):
    objects = [o for o in m.doc.Objects if o.Label.startswith(label + ' · tool')]
    assert len(objects) == expected, (label, len(objects))
    return objects


def calibrate_front(m):
    """Fit the original front's cover proportion, narrow controls and logo pose."""
    if m.profile.get('front_calibrated_iteration16'):
        return
    _tools(m, 'Front SD and synchronization door recess', 1)[0].Shape = m.rr(62.2, 13.4, 5.2, (0, -103, 10.7), .7, FRONT)
    replace(m, 'SDFlap', m.rr(61.5, 12.7, 1.35, (0, -106.2, 10.7), .6, FRONT),
            'Original front diagram cover-to-body proportion; local width fitted')
    _move(m, 'SDHinge-31', (3.5, 0, 0));_move(m, 'SDHinge31', (-6.5, 0, 0))
    for key, x, width, height in [('Power', -60.5, 5.2, 13.0),
                                  ('Reset', -47.5, 3.8, 12.5), ('Eject', 62, 6.2, 12.0)]:
        _tools(m, key + ' button aperture', 1)[0].Shape = m.rr(width + .7, height + .7, 5, (x, -103.5, 11.5), .8, FRONT)
        replace(m, key + 'Button', m.rr(width, height, 1.7, (x, -106.2, 11.5), .6, FRONT),
                'Original narrow faceplate key proportions fitted from the Nintendo front diagram')
    # Wii lettering reads horizontally in the standing orientation; in this
    # horizontal console model it must rotate with the original faceplate.
    shape = m.parts['WiiFrontMark'].Shape.copy()
    shape.rotate(shape.optimalBoundingBox(False, False).Center, V(0, -1, 0), 90)
    replace(m, 'WiiFrontMark', shape, 'Correct original faceplate wordmark orientation in the horizontal model')
    m.doc.recompute()
    m.profile['front_calibrated_iteration16'] = True


def calibrate_remote_front(m):
    """Fit original front controls to the official near-orthographic photograph."""
    if m.profile.get('remote_front_calibrated_iteration16'):
        return
    cx, cy = -25, -235
    changes = [('DPad', (0, 41), (0, 50), 'Cross-shaped directional-pad aperture'),
               ('A', (0, 18), (0, 28.5), 'A key aperture'),
               ('Minus', (-10.5, -4), (-10.5, 3.5), 'Minus key aperture'),
               ('Home', (0, -4), (0, 3.5), 'Home key aperture'),
               ('Plus', (10.5, -4), (10.5, 3.5), 'Plus key aperture'),
               ('One', (0, -43), (0, -35.5), 'One key aperture'),
               ('Two', (0, -56), (0, -48.5), 'Two key aperture'),
               ('Power', (-10.5, 60.5), (-9.5, 67), 'Power key aperture')]
    for key, old, new, label in changes:
        delta = (new[0] - old[0], new[1] - old[1], 0)
        for name in ['Remote' + key, 'Remote' + key + 'Mark', 'Remote' + key + 'Carbon', 'Remote' + key + 'Rubber']:
            if name in m.parts:
                _move(m, name, delta)
        for tool in _tools(m, label, 1):
            shape = tool.Shape.copy();shape.translate(V(*delta));tool.Shape = shape
        if key in ('Home', 'Power'):
            _move(m, 'Remote' + key + 'Symbol', delta)
    grille = _tools(m, 'RVL-003 three-column six-row speaker grille', 1)[0]
    shape = grille.Shape.copy();shape.translate(V(0, 7, 0));grille.Shape = shape
    for key in ('RemoteSpeaker', 'RemoteSpeakerMagnet', 'RemoteSpeakerCone'):
        _move(m, key, (0, 7, 0))
    # This package's former approximate location conflicts with the corrected
    # speaker. Move it within the existing PCB; no factory PCB layout claimed.
    _move(m, 'RemoteEEPROM', (3, 0, 0))
    led_tools = sorted(_tools(m, 'Player indicator light-pipe aperture', 4), key=lambda o: o.Shape.BoundBox.Center.x)
    for i, (old_x, new_x, tool) in enumerate(zip((-9, -3, 3, 9), (-9.75, -3.25, 3.25, 9.75), led_tools), 1):
        delta = (new_x - old_x, 7.5, 0)
        _move(m, 'RemoteLED' + str(i), delta)
        shape = tool.Shape.copy();shape.translate(V(*delta));tool.Shape = shape
        dots = []
        for j in range(i):
            x = cx + new_x + (j - (i - 1) / 2) * .74
            ring = Part.makeCylinder(.27, .018, V(x, cy - 55.4, 29.59))
            ring = ring.cut(Part.makeCylinder(.14, .05, V(x, cy - 55.4, 29.57)))
            dots.append(ring)
        mark = replace(m, 'RemoteLEDMark' + str(i), Part.makeCompound(dots),
                       'Original player identification uses one through four outlined dots above the lamps')
        mark.Label = 'Original player ' + str(i) + ' dot identification'
    mark = m.label('RemoteWiiMark', 'Wii', 6.3, (0, 0, 0), 'Controller', 4, 'wiigrey')
    b = mark.Shape.optimalBoundingBox(False, False)
    mark.Placement.Base += V(cx - b.Center.x, cy - 67 - b.Center.y, 29.59 - b.ZMin)
    mark.FlatPlacement = mark.Placement
    mark.Label = 'Original bottom Wii wordmark, typeface approximation'
    finish_remote_surface(m)
    m.doc.recompute()
    m.profile['remote_front_calibrated_iteration16'] = True


def finish_remote_surface(m):
    if m.profile.get('remote_surface_finished_iteration16'):
        return
    cx, cy = -25, -235
    top = m.parts['RemoteDPad'].Shape.optimalBoundingBox(False, False).ZMax
    grooves = [m.rr(.30, 2.8, .18, (cx, cy + 50 + dy, top - .12), .06) for dy in (-5, 5)]
    grooves += [m.rr(2.8, .30, .18, (cx + dx, cy + 50, top - .12), .06) for dx in (-5, 5)]
    before = m.parts['RemoteDPad'].Shape.Volume
    existing = [o for o in m.doc.Objects if o.Label.startswith('Original directional cross molded tick grooves · tool')]
    if existing:
        assert len(existing) == 1
        existing[0].Shape = Part.makeCompound(grooves);m.doc.recompute()
    else:
        m.cut('RemoteDPad', grooves, 'Original directional cross molded tick grooves')
    assert before - m.parts['RemoteDPad'].Shape.Volume > .01, 'Directional grooves must remove actual cap material'
    for key, radius in [('A', .85), ('Minus', .30), ('Home', .30), ('Plus', .30),
                        ('One', .35), ('Two', .35), ('Power', .25)]:
        shape = m.parts['Remote' + key].Shape.copy()
        top = shape.optimalBoundingBox(False, False).ZMax
        edges = [e for e in shape.Edges if e.BoundBox.ZLength < 1e-6 and abs(e.BoundBox.ZMax - top) < 1e-6]
        replace(m, 'Remote' + key, shape.makeFillet(radius, edges),
                'Rounded original key edge fitted from Nintendo photograph; radius estimated')
    for name, text, x, y in [('RemotePowerLegend', 'POWER', cx - 9.5, cy + 61.4),
                             ('RemoteHomeLegend', 'HOME', cx, cy - 1.5)]:
        obj = m.label(name, text, 1.2, (0, 0, 0), 'Controller', 4, 'wiigrey')
        b = obj.Shape.optimalBoundingBox(False, False)
        obj.Placement.Base += V(x - b.Center.x, y - b.Center.y, 29.59 - b.ZMin)
        obj.FlatPlacement = obj.Placement
    for i in range(1, 5):
        m.parts['RemoteLEDMark' + str(i)].Label = 'Original player ' + str(i) + ' dot identification'
    m.doc.recompute()
    m.profile['remote_surface_finished_iteration16'] = True


def stage16(m):
    m.set_pose(180)
    m.colors.update(wiiwhite=(.90, .91, .90), wiigrey=(.67, .68, .68),
                    slotblue=(.12, .56, .92), cream=(.82, .81, .72),
                    sensor_orange=(.95, .32, .08))
    m.parts['AVShell'].MaterialDescription = 'black'
    appearance(m.parts['AVShell'], m.colors['black'])
    for key in ('SensorSocket', 'SensorPlugTip'):
        m.parts[key].MaterialDescription = 'sensor_orange'
        appearance(m.parts[key], m.colors['sensor_orange'])
    calibrate_front(m)
    # Nintendo's RVL-001 setup diagram shows a five-by-five rectangular
    # exhaust field. Keep the existing fan axis; local pitch/width are fitted.
    vents = [m.rr(6.2, 6.2, 6.0, (-9 + col * 6.8, 103.5, 22.5 + row * 6.8), .15, REAR)
             for row in range(-2, 3) for col in range(-2, 3)]
    for tool in _tools(m, 'Rear parallel exhaust grille', 2):
        tool.Shape = Part.makeCompound(vents)
        tool.Label = 'RVL-001 five-by-five rear exhaust field · tool'

    # The rear sockets form a close double bank. The original 17 mm spacing
    # stretched them across almost the whole 44 mm thickness. 8.5 mm is a
    # diagram fit, not a released Nintendo connector dimension.
    for key in list(m.parts):
        if key.startswith('USB1'):
            _move(m, key, (0, 0, -8.5))
    for tool in _tools(m, 'USB-A 2 rear opening', 2):
        shape = tool.Shape.copy();shape.translate(V(0, 0, -8.5));tool.Shape = shape

    cx, cy = -25, -235
    radii = [.30, .45, .60, .60, .45, .30]
    holes = [Part.makeCylinder(radius, 3.0, V(cx + column * 2.5, cy - 22 + (2.5 - row) * 2.5, 27))
             for row, radius in enumerate(radii) for column in (-1, 0, 1)]
    grille = _tools(m, 'Remote loudspeaker grille', 1)[0]
    grille.Shape = Part.makeCompound(holes)
    grille.Label = 'RVL-003 three-column six-row speaker grille · tool'
    m.doc.recompute()

    # The red SYNC control is visible under the removable battery cover, below
    # the cell ends. Mount its switch against the existing main PCB back side;
    # its package dimensions and depth remain schematic.
    x, y = cx - 10.5, cy - 56.0
    m.cyl('RemoteSyncButton', 'RVL-003 red battery-compartment SYNC button',
          1.45, .8, (x, y, 18.7), 'Controller', -2, 'red', internal=True)
    m.box('RemoteSyncSwitch', 'Rear-facing SYNC switch package study',
          3.6, 3.6, 1.6, (x, y, 19.65), 'Controller', -1, 'black', .3, True)

    # The lanyard loop belongs to the original remote housing. Reconstruct an
    # integral molded bridge with a connected rear-to-bottom passage, without
    # inventing a separate component or selecting a later wrist-strap revision.
    rear_entry = m.rr(3.2, 4.0, 6.5, (cx, cy - 67.0, -.1), .6)
    bottom_entry = Part.makeCylinder(1.10, 10.0, V(cx, cy - 66.0, 5.5), V(0, -1, 0))
    passage = rear_entry.fuse(bottom_entry).removeSplitter()
    # Keep the block strictly inside the existing outer loft. Intersecting a
    # reinforcing block with the outer skin before fusing creates coincident
    # trimmed spline faces that fail OCCT's strict curve-on-surface check.
    block = m.rr(6.2, 7.0, 4.0, (cx, cy - 68, 4.5), .65)
    assert block.cut(m.doc.getObject('RemoteBackOuter').Shape).Volume < 1e-6
    assert block.isValid() and block.Solids
    fuse_feature(m, 'RemoteBack', block, 'Reconstructed integral original lanyard bridge')
    m.cut('RemoteBack', passage, 'Original remote connected rear and bottom lanyard passage')
    assert len(m.parts['RemoteBack'].Shape.Solids) == 1, 'The lanyard bridge must remain integral with the rear shell'
    calibrate_remote_front(m)
    m.doc.recompute()
    for key in ('LowerHousing', 'UpperHousing', 'FrontBezel', 'RemoteFront', 'RemoteBack', 'RemoteDPad', 'USB1Shell'):
        m.parts[key].Shape.check(True)
    m.profile['stages'] = 16
    m.checkpoint(16, 'documented_rear_panel_and_remote_service_details',
                 '按官方正背面图修正前盖比例、窄长控制键、横放字标方向、五乘五后排风和双USB间距；按RVL-003照片校准控件、十八孔扬声器、玩家点阵及印字，补齐SYNC键和一体挂绳通道。局部尺寸为图像拟合，未加入后期腕带或硅胶套。')
