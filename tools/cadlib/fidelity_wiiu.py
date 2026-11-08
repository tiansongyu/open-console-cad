"""WUP-001/WUP-010 front, rear and control-layout fits to Nintendo part images."""
import FreeCAD as App
import Part

from .core import V
from .geometry import rotation, appearance
from .clamshell import _move
from .handheld_refinement import replace
from .retro_common import fuse_feature

FRONT = rotation((0, -1, 0), (0, 0, 1))
REAR = rotation((0, 1, 0), (0, 0, 1))


def _tools(m, label, count=1):
    found = [o for o in m.doc.Objects if o.Label.startswith(label + ' · tool')]
    assert len(found) == count, (label, len(found), count)
    return found


def _move_tools(m, label, delta, count=1):
    for tool in _tools(m, label, count):
        shape = tool.Shape.copy();shape.translate(V(*delta));tool.Shape = shape


def _move_keys(m, keys, delta):
    for key in keys:
        if key in m.parts:
            _move(m, key, delta)


def _pad_button(m, key, old_xy, new_xy):
    delta = (new_xy[0] - old_xy[0], new_xy[1] - old_xy[1], 0)
    _move_keys(m, ['Pad' + key, 'Pad' + key + 'Mark', 'Pad' + key + 'Carbon', 'Pad' + key + 'Dome'], delta)
    _move_tools(m, key + ' button opening', delta)
    return delta


def _centered_label(m, key, text, size, x, y):
    obj = m.label(key, text, size, (0, 0, 0), 'Controller', 5, 'wiigrey')
    # Unite touching glyph solids before the final transform; BATTERY contains
    # outline contacts in this font that otherwise fail the strict BOP check.
    solids = obj.Shape.Solids
    if len(solids) > 1:
        obj.Shape = solids[0].multiFuse(solids[1:]).removeSplitter()
    b = obj.Shape.optimalBoundingBox(False, False)
    obj.Placement.Base += V(x - b.Center.x, y - b.YMin, 41.002 - b.ZMin)
    obj.FlatPlacement = obj.Placement


def close_rear_usb_spacing(m):
    """Fit the close stacked pair rather than spreading it across the rear."""
    tools = _tools(m, 'Rear stacked USB-A aperture', 4)
    for i, target in enumerate((13.5, 22.0)):
        current = m.parts['RearUSB' + str(i)].Shape.optimalBoundingBox(False, False).Center.z
        delta = target - current
        if abs(delta) < 1e-8:
            continue
        for key in list(m.parts):
            if key in ('RearUSB' + str(i), 'RearUSBTongue' + str(i)) or key.startswith('RearUSBPin' + str(i) + '_'):
                _move(m, key, (0, 0, delta))
        matching = [t for t in tools if abs(t.Shape.BoundBox.Center.z - current) < .01]
        assert len(matching) == 2
        for tool in matching:
            shape = tool.Shape.copy();shape.translate(V(0, 0, delta));tool.Shape = shape
    m.doc.recompute()


def correct_gamepad_edge_features(m):
    """Separate the bottom contacts and top TV IR window from rear-face details."""
    cy = -275.0
    # The manual's bottom view places the two contacts beside the accessory
    # connector. Their span is fitted to the drawing, not a connector datasheet.
    for side in (-1, 1):
        body = m.parts['PadBack'].Shape
        mask = m.rr(5.0, 2.8, 8, (side * 16.5, cy - 61, 20.9), .2, FRONT)
        inner = body.copy();inner.translate(V(0, .10, 0))
        skin = body.common(mask).cut(inner).removeSplitter()
        assert skin.isValid() and len(skin.Solids) == 1 and skin.Volume > .1
        m.cut('PadBack', skin, 'Bottom-facing cradle contact inset ' + str(side))
        replace(m, 'PadDockPad' + str(side), skin,
                'Manual bottom view: charging contacts face the bottom edge beside the accessory connector')

    # This TV-control window is separate from the front camera/sensor bar.
    # Reconstruct a 1.2 mm cover following the existing two lofted outer walls;
    # span the shell seam so it remains one connected optical part.
    x0, width = -27.25, 13.5
    z0, z1 = 13.5, 27.5
    y0 = cy + 59.5 + (z0 - 10) * 7.2 / 12.5
    y1 = cy + 66.7 - (z1 - 22.75) * 2.7 / 13.75
    outer = [(y0, z0), (cy + 66.7, 22.5), (cy + 66.7, 22.75), (y1, z1)]
    points = [V(x0, y, z) for y, z in outer]
    points += [V(x0, y - 1.2, z) for y, z in reversed(outer)]
    lens = Part.Face(Part.makePolygon(points + [points[0]])).extrude(V(width, 0, 0))
    mask = m.rr(width, z1 - z0, 12, (-20.5, cy + 58, (z0 + z1) / 2), .7, REAR)
    lens = lens.common(mask).removeSplitter()
    assert lens.isValid() and len(lens.Solids) == 1
    for key in ('PadBack', 'PadFront'):
        m.cut(key, lens, 'Top-edge television infrared window aperture')
    m.feature('PadTVIRWindow', 'Separate top-edge television infrared window, image-fitted cover',
              lens, 'Controller', 4, 'black')
    m.doc.recompute()


def _rebuild_adapter(m, prefix, model, center, size):
    """Regenerate the existing primitive recipe while retaining identities."""
    from .wiiu import _power_adapter
    suffixes = ['Lower', 'Upper', 'PCB', 'Transformer', 'Winding', 'BulkCap',
                'OutputCap', 'InputCoil', 'OutputCoil', 'Rectifier', 'HeatPlate',
                'Screw0', 'Screw1', 'Screw2', 'Screw3', 'Mark', 'Relief-1', 'Relief1']
    order = list(m.parts.items())
    old = {prefix + suffix: m.parts.pop(prefix + suffix) for suffix in suffixes}
    for obj in old.values():
        obj.PhysicalPart = False;obj.Visibility = False
    _power_adapter(m, prefix, model, *center, *size)
    rebuilt = dict(m.parts)
    for key, previous in old.items():
        obj = rebuilt[key]
        obj.addProperty('App::PropertyLink', 'PreviousRevision', 'Revision');obj.PreviousRevision = previous
        obj.addProperty('App::PropertyString', 'RevisionReason', 'Revision')
        obj.RevisionReason = 'Nintendo published adapter enclosure dimensions; internal primitive recipe remains schematic'
        if 'PartNumber' in previous.PropertiesList:
            obj.addProperty('App::PropertyString', 'PartNumber', 'Study');obj.PartNumber = previous.PartNumber
    m.parts.clear();m.parts.update((key, rebuilt[key]) for key, _ in order)


def _rear_and_accessories(m, cy):
    # Rear-view photographs reverse X relative to the front. The former model
    # placed charging on the wrong side and centered the headphone connector.
    _move(m, 'PadVolume', (91.5, 1, 0))
    _move_tools(m, 'Top-edge volume-slider opening', (91.5, 0, 0))
    _move(m, 'PadAudioJack', (-49, 0, 0))
    _move_tools(m, 'Headphone-jack aperture', (-49, 0, 0))
    _move_keys(m, ['PadChargeSocket', 'PadChargePin0', 'PadChargePin1'], (-97.5, 0, 0))
    _move_tools(m, 'GamePad charging connector opening', (-97.5, 0, 0))

    # The rear SYNC control is explicitly identified by Nintendo. Extract the
    # local molded surface, then inset the cap a little; do not change the body
    # envelope or pretend to reproduce an unmeasured internal switch package.
    tool = Part.makeCylinder(1.55, 24, V(20, cy - 57, 0))
    cap = m.parts['PadBack'].Shape.common(tool)
    assert cap.isValid() and cap.Solids and cap.Volume > .01
    m.cut('PadBack', tool, 'Original GamePad rear SYNC button opening')
    cap.translate(V(0, 0, .25))
    m.feature('PadSyncButton', 'Recessed original rear SYNC button, internal switch not reproduced',
              cap, 'Controller', -5, 'red')

    # Empty holder corresponds to the stylus displayed separately. Both the
    # guide's internal shape and its rear opening are reconstructed estimates.
    outside = Part.makeCylinder(2.8, 98.5, V(86, cy - 41.8, 13), V(0, 1, 0))
    bore = Part.makeCylinder(2.35, 99, V(86, cy - 42, 13), V(0, 1, 0))
    assert outside.cut(m.doc.getObject('PadBackOuter').Shape).Volume < 1e-5
    fuse_feature(m, 'PadBack', outside, 'Reconstructed integral original stylus guide', refine=False)
    opening = m.rr(8.8, 13.2, 8.5, (86, cy + 50, 9.5), 1.3)
    m.cut('PadBack', [bore, opening], 'Original stylus holder and rear withdrawal opening')

    # Nintendo's WUP-015 specification gives 5.4 x 8.4 x 97.9 mm. The cap is
    # a flattened pull tab, not the previous six-millimeter circular end.
    replace(m, 'StylusBarrel', Part.makeCylinder(2.2, 76.2, V(180, cy - 45, 5), V(0, 1, 0)),
            'Stylus shaft length follows the 97.9 mm published overall envelope')
    replace(m, 'StylusCap', m.rr(8.4, 5.4, 12.5, (180, cy + 31.4, 5), 1.2, REAR),
            'WUP-015 flattened cap fitted within the published 8.4 x 5.4 mm transverse envelope')

    _rebuild_adapter(m, 'ConsoleAC', 'WUP-002', (255, 70), (150, 70, 49))
    _rebuild_adapter(m, 'GamePadAC', 'WUP-011', (235, -110), (100, 35, 28))
    from .atari2600 import _rounded_route
    routes = {
        'ConsoleACCord': [V(172.7, 70, 14.7), V(145, 70, 14.7), V(145, 125, 14.7),
                          V(265, 125, 14.7), V(265, 148, 5.5), V(265, 155.3, 5.5)],
        'ConsoleACDCCord': [V(337.3, 70, 26.46), V(368, 70, 26.46), V(368, -10, 26.46),
                            V(318, -10, 10), V(290.2, -10, 10)],
        'GamePadACCord': [V(177.7, -110, 8.4), V(155, -110, 8.4), V(155, -155, 8.4),
                         V(230, -155, 8.4), V(230, -173.2, 5.5)],
        'GamePadACDCCord': [V(292.3, -110, 15.12), V(330, -110, 15.12), V(330, -50, 15.12),
                           V(291, -50, 10), V(272.2, -50, 10)]}
    for key, points in routes.items():
        replace(m, key, _rounded_route(points, 2, 1.5 if 'DCCord' in key else 1.8),
                'Display-length cable starts at the corrected adapter strain relief; external plug retained')


def stage23(m):
    m.set_pose(180)
    m.colors.update(wiiuwhite=(.9, .91, .9), wiigrey=(.65, .66, .67),
                    ublue=(.04, .55, .77), cream=(.82, .81, .72), yellow=(.94, .72, .08))

    # Front/rear console fits use Nintendo's WUP-001 pictures, retaining the
    # published plastic envelope. All local fitted coordinates remain estimates.
    for key in ('Power', 'Eject'):
        _move_keys(m, [key + 'Button', key + 'Symbol', key + 'Mark'], (-5, 0, 0))
        _move_tools(m, key + ' control aperture', (-5, 0, 0))
    for key in ('PowerLED', 'DiscLED'):
        _move(m, key, (-5, 0, 0));_move_tools(m, key + ' light aperture', (-5, 0, 0))
    _move_keys(m, ['SyncButton', 'SyncMark'], (-4, 0, 0))
    _move_tools(m, 'Sync control aperture', (-4, 0, 0))
    replace(m, 'EjectButton', m.rr(10.6, 6.0, 1.5, (-73, -132.9, 32.7), 2.95, FRONT),
            'Nintendo original front image shows a horizontal capsule eject key')
    _tools(m, 'Eject control aperture')[0].Shape = m.rr(11.2, 6.6, 5, (-73, -130, 32.7), 3.2, FRONT)
    replace(m, 'FrontFlap', m.rr(82.4, 14.4, 1.25, (11, -132.9, 11.7), 1.2, FRONT),
            'Front SD/USB cover fitted to the original front image')
    _tools(m, 'Front SD and USB compartment opening')[0].Shape = m.rr(83, 15, 5.5, (11, -129.2, 11.7), 1.4, FRONT)
    for key in list(m.parts):
        if key.startswith('FrontUSB') or key in ('SDPort', 'SDTongue') or key.startswith('SDContact'):
            _move(m, key, (-4.8, 0, 0))
        if key.startswith('RearUSB'):
            _move(m, key, (8, 0, 0))
    _move_tools(m, 'Rear stacked USB-A aperture', (8, 0, 0), 4)
    close_rear_usb_spacing(m)
    grille = [m.rr(11.8, 4.0, 6, (-35.5 + column * 13, 130, 5.6 + row * 5.8), .4, REAR)
              for column in range(3) for row in range(7)]
    for tool in _tools(m, 'Three-column rear cooling grille', 2):
        tool.Shape = Part.makeCompound(grille)
    _move_keys(m, ['FanFrame', 'FanRotor', 'FanMotor'] + ['FanStrut' + str(i) for i in range(4)], (3.5, 0, 0))
    for name in ('AirDuctOuter', 'AirDuctInner'):
        for index, delta in [(1, 1.75), (2, 3.5)]:
            profile = m.doc.getObject(name + 'Profile' + str(index))
            placement = profile.Placement;placement.Base.x += delta;profile.Placement = placement
    # Keep the original motherboard connector endpoints; shift only the final
    # fan-side reach with the reconstructed duct/fan assembly.
    from .atari2600 import _rounded_route
    for i in range(2):
        x, yy, z = -70 + i * .9, 117 + i * .8, 14.5 + i * .5
        points = [V(x, 106, 10.55), V(x, 106, z), V(x, yy, z),
                  V(-49 - i * .8, yy, z), V(-49 - i * .8, yy, 23 + i),
                  V(-49 - i * .8, 126, 23 + i), V(-42.9, 126, 23 + i)]
        replace(m, 'FanLead' + str(i), _rounded_route(points, .3, .16),
                'Schematic fan-side lead follows the corrected rear exhaust position')

    cy = -275.0
    # The front IR/camera bar was markedly too short. Keep the glass lens size,
    # add its visible annular surround and broaden the common dark cover.
    bar = m.rr(72.2, 8.6, 1.0, (0, cy + 54, 40), 4.1)
    bar = bar.cut(Part.makeCylinder(3.12, 1.4, V(0, cy + 54, 39.8)))
    replace(m, 'CameraIRWindow', bar, 'Wider camera/IR strip from Nintendo original GamePad front image')
    _tools(m, 'Camera and infrared window opening')[0].Shape = m.rr(72.8, 9.2, 7, (0, cy + 54, 37), 4.4)
    m.ring('CameraOuterRing', 'Camera lens annular surround', 3.0, 2.2, .28,
           (0, cy + 54, 40.70), 'Controller', 5, 'metal')

    for side, prefix in [(-1, 'LStick'), (1, 'RStick')]:
        delta = (side * 7.2, 3, 0)
        _move_keys(m, [key for key in m.parts if key.startswith(prefix)], delta)
        x, y = side * 105.2, cy + 35
        _tools(m, prefix + ' circular opening')[0].Shape = Part.makeCylinder(9.3, 10, V(x, y, 35))
        rim = Part.makeCylinder(10.8, .5, V(x, y, 41.03)).cut(Part.makeCylinder(9.4, .8, V(x, y, 40.9)))
        replace(m, prefix + 'Rim', rim, 'Original front-image analog opening proportions; local radii fitted')
        cap = Part.makeCylinder(8.2, 2.4, V(x, y, 46.1)).cut(Part.makeSphere(24, V(x, y, 71.3)))
        replace(m, prefix + 'Cap', cap, 'Reduced thumb-cap diameter from original front-image proportions')

    # Move complete key/plunger stacks and their apertures, not just the artwork.
    for key in ('A', 'B', 'X', 'Y'):
        _move_keys(m, ['Pad' + key, 'Pad' + key + 'Mark', 'Pad' + key + 'Carbon', 'Pad' + key + 'Dome'], (-2.5, 11.5, 0))
        _move_tools(m, key + ' button opening', (-2.5, 11.5, 0))
    _move(m, 'PadCarrierABXY', (-2.5, 11.5, 0))
    _pad_button(m, 'Plus', (96, -31), (84.5, -20.5))
    _pad_button(m, 'Minus', (96, -44), (84.5, -33))
    _pad_button(m, 'TV', (50, -53), (54, -54))
    _pad_button(m, 'Power', (72, -53), (66.5, -54))
    _move(m, 'PadPowerSymbol', (-5.5, -1, 0))
    _pad_button(m, 'Home', (0, -53), (0, -54))
    _move_keys(m, ['HomeLightRing', 'HomeSymbol'], (0, -1, 0))
    _move_tools(m, 'HOME light-ring recess', (0, -1, 0))
    m.parts['HomeLightRing'].MaterialDescription = 'wiigrey'
    m.parts['HomeLightRing'].Label = 'HOME notification-light diffuser, unlit'
    appearance(m.parts['HomeLightRing'], m.colors['wiigrey'])
    tv = m.rr(5.8, 5.8, 2.7, (54, cy - 54, 40.1), 1.1)
    tv = tv.fuse(Part.makeCylinder(1.0, 4, V(54, cy - 54, 36.2))).removeSplitter()
    replace(m, 'PadTV', tv, 'Original GamePad television key is a rounded square')
    _tools(m, 'TV button opening')[0].Shape = m.rr(6.4, 6.4, 7, (54, cy - 54, 37), 1.35)

    x, y = -94.5, cy + 6.5
    cross = m.rr(23, 7.5, 3.4, (x, y, 39.5), .4).fuse(m.rr(7.5, 23, 3.4, (x, y, 39.5), .4)).removeSplitter()
    cross = cross.fuse(Part.makeCylinder(1.8, 3.4, V(x, y, 36.2))).removeSplitter()
    grooves = [m.rr(.35, 3.1, .22, (x + dx, y + dy, 42.75), .07)
               for dx, dy in [(0, 7.4), (0, -7.4)]]
    grooves += [m.rr(3.1, .35, .22, (x + dx, y, 42.75), .07) for dx in (-7.4, 7.4)]
    replace(m, 'PadDPad', cross.cut(Part.makeCompound(grooves)),
            'Larger correctly positioned original cross and four molded direction grooves')
    aperture = m.rr(23.6, 8.1, 7, (x, y, 36.8), .5).fuse(m.rr(8.1, 23.6, 7, (x, y, 36.8), .5))
    _tools(m, 'Directional-pad cross aperture')[0].Shape = aperture
    _move_keys(m, ['PadDPadCarbon', 'PadDPadDome', 'PadCarrierDirection'], (3.5, 13.5, 0))
    # Reconstructed board outlines accommodate the relocated contacts while
    # keeping the existing stick modules and board-flex endpoints clear.
    replace(m, 'PadButtonPCB-1', m.rr(27, 54, .7, (-96.5, cy - 4, 30.1), 2),
            'Schematic button-board outline follows corrected directional contact position')
    board = m.rr(32, 60, .7, (96.5, cy - 5.5, 30.1), 2)
    board = board.cut(Part.makeCompound([Part.makeCylinder(2.7, 1.1, V(113, cy + y, 29.9))
                                         for y in (-20, 15)]))
    replace(m, 'PadButtonPCB1', board,
            'Schematic button board supports the corrected face and START/SELECT contacts')

    # Restore the bilateral speaker locations. The old right speaker had been
    # moved outwards to avoid the incorrectly positioned SELECT mechanism.
    speaker_tools = sorted(_tools(m, 'Front stereo speaker opening', 2), key=lambda o: o.Shape.BoundBox.Center.x)
    for side, tool in zip((-1, 1), speaker_tools):
        sx = side * 84.5
        tool.Shape = m.rr(4.2, 2, 5, (sx, cy - 54, 37), .9)
        replace(m, 'SpeakerOpening' + str(side), m.rr(3.8, 1.6, .35, (sx, cy - 54, 40.6), .7),
                'Symmetric original single-oval stereo outlet from Nintendo front image')
        old_x, old_y = (-99, -49) if side < 0 else (107, -43)
        _move_keys(m, ['PadSpeaker' + str(side), 'PadSpeakerCone' + str(side), 'PadSpeakerMagnet' + str(side)],
                   (sx - old_x, -51 - old_y, 0))

    for key, delta in [('MicHole', (5, -1, 0)), ('BatteryLamp', (6.5, -1, 0))]:
        _move(m, key + 'Insert', delta);_move_tools(m, key + ' aperture', delta)
    _move(m, 'PadMicrophone', (5, -1, 0))
    m.parts['BatteryLampInsert'].MaterialDescription = 'black'
    appearance(m.parts['BatteryLampInsert'], m.colors['black'])
    # Correct the NFC area position and its two overlapping rounded outlines.
    x, y = -94.5, cy - 25.5
    plate = m.rr(11, 7.5, .025, (x, y, 41.002), .85)
    a = plate.cut(m.rr(10.35, 6.85, .08, (x, y, 40.98), .55))
    b = m.rr(11, 7.5, .025, (x + .85, y + .85, 41.002), .85).cut(m.rr(10.35, 6.85, .08, (x + .85, y + .85, 40.98), .55))
    b = b.cut(m.rr(11, 7.5, .08, (x, y, 40.98), .85))
    replace(m, 'NFCMark', a.fuse(b).removeSplitter(), 'Original paired NFC-area outline and photo-fitted position')
    _move_keys(m, ['PadNFCPCB', 'PadNFCIC', 'PadNFCAntenna'], (3.5, 8.5, 0))

    # Re-route only the changed acoustic endpoints; the motherboard endpoints
    # and conductor count remain the existing schematic design.
    for side in (-1, 1):
        for i in range(2):
            sx, edge = side * 65, side * (82 + i * .8)
            yy = cy - 18 - i * .7 if side < 0 else cy - 14 - i * .7
            ey, z, endz = cy - 51 + i * .65, 27.5 + i * .35, 34.9 + i * .25
            points = [V(sx, yy, z), V(edge, yy, z), V(edge, ey, z),
                      V(side * (90 + i * .8), ey, z), V(side * (90 + i * .8), ey, endz), V(side * 84.5, ey, endz)]
            replace(m, 'PadSpeakerLead' + str(side) + '_' + str(i), _rounded_route(points, .2, .13),
                    'Schematic speaker route follows the corrected acoustic module')
    for i in range(2):
        points = [V(-15 + i * .7, cy - 54, 36.2), V(-15 + i * .7, cy - 49, 36.2),
                  V(-15 + i * .7, cy - 49, 29.15), V(5 + i * .7, cy - 49, 29.15), V(5 + i * .7, cy - 53, 29.15)]
        replace(m, 'PadMicrophoneLead' + str(i), _rounded_route(points, .2, .11),
                'Schematic microphone route follows the corrected inlet')
    _rear_and_accessories(m, cy)
    correct_gamepad_edge_features(m)
    for key, text, size, x, y in [('PadStartLegend', 'START', 1.45, 84.5, -26.6),
                                 ('PadSelectLegend', 'SELECT', 1.45, 84.5, -39.1),
                                 ('PadMicLegend', 'MIC', 1.35, -15, -60),
                                 ('PadHomeLegend', 'HOME', 1.35, 0, -60),
                                 ('PadBatteryLegend', 'BATTERY', 1.35, 40.5, -60),
                                 ('PadTVLegend', 'TV CONTROL', 1.15, 54, -60),
                                 ('PadPowerLegend', 'POWER', 1.35, 66.5, -60)]:
        _centered_label(m, key, text, size, x, cy + y)
    m.doc.recompute()
    m.profile['stages'] = 23
    m.checkpoint(23, 'official_front_rear_and_gamepad_layout_calibration',
                 '对照任天堂正背面图校准主机退盘键、前部接口和后USB位置；重排GamePad方向键、ABXY、摇杆、系统键和对称扬声器，扩展摄像头红外条，补齐镜头圈、NFC双框和印字。同步孔位、传力件与示意板件/音频线，尺寸为公开图像拟合。')
