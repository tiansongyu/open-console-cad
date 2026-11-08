"""LCD Deck reference dimensions and measured exterior feature positions.

Reconstructs primitives from the published Valve dimensions and sparse measured
feature facts. No Valve STEP faces, wires, meshes or drawings are embedded.
"""
import FreeCAD as App
import Part

from .core import V
from .clamshell import _move
from .handheld_refinement import replace


def _tools(m, prefix, count):
    result = [o for o in m.doc.Objects if o.Label.startswith(prefix + ' · tool')]
    assert len(result) == count, (prefix, len(result), count)
    return result


def stage17(m):
    m.set_pose(180)
    m.profile['upper_display'] = [151.7, 95.2]
    m.profile['display_dimension_basis'] = 'Valve 2022-02-02 reference drawing Rev B sheet 2; active area 151.7 x 95.2 mm, cover glass 173.7 x 106.7 mm'
    # Sheet 2 gives mechanical dimensions, superseding the exact-7-inch
    # diagonal conversion previously used for the visible display window.
    _tools(m, 'Seven-inch LCD window recess', 1)[0].Shape = m.rr(173.76, 106.76, 1.9, (0, 0, 35.5), 1.55)
    border = m.rr(173.7, 106.7, .55, (0, 0, 36.45), 1.5)
    border = border.cut(m.rr(151.82, 95.32, .8, (0, 0, 36.3), .3))
    replace(m, 'DisplaySurround', border,
            'Valve published 173.7 x 106.7 mm cover-glass perimeter; reconstructed edge radii')
    replace(m, 'DisplayGlass', m.rr(151.7, 95.2, .2, (0, 0, 36.8), .3),
            'Valve published 151.7 x 95.2 mm active display area')
    replace(m, 'TouchLayer', m.rr(151.7, 95.2, .12, (0, 0, 36.57), .25),
            'Touch layer follows the published active display area')

    microphones = _tools(m, 'Dual microphone inlet', 2)
    for i, side in enumerate((-1, 1)):
        x, y = side * 62.0, 53.819
        microphones[i].Shape = Part.makeCylinder(.382, 2, V(x, y, 35.3))
        # The reference STEP aperture is diameter .764 mm. The drawing's
        # diameter 2 mm annotation is accessory clearance, not hole diameter.
        replace(m, 'MicrophoneMesh' + str(i), Part.makeCylinder(.33, .12, V(x, y, 36.45)),
                'Microphone aperture at x +/-62, y53.819 mm in the Valve reference')
        # Package depth is not supplied by the exterior reference. Keep this
        # schematic package above the existing antenna foil with clear spacing.
        _move(m, 'MicrophonePackage' + str(i), (side * (62 - 7.5), -.181, 1.3))

    # Measured reference touchpad centers. Move the existing approximate
    # mechanism as a unit and update its matching deck and PCB mounting holes.
    track_holes = _tools(m, 'Square trackpad opening', 2)
    mounts = _tools(m, 'Trackpad mount through input PCB', 8)
    for i, side in enumerate((-1, 1)):
        delta = (side * (105.78 - 109), 1.337 + 4, 0)
        for key, obj in list(m.parts.items()):
            if obj.Assembly == 'Touchpads' and obj.Shape.BoundBox.Center.x * side > 0:
                _move(m, key, delta)
        shape = track_holes[i].Shape.copy();shape.translate(V(*delta));track_holes[i].Shape = shape
        for tool in mounts[i * 4:i * 4 + 4]:
            shape = tool.Shape.copy();shape.translate(V(*delta));tool.Shape = shape

    # These pills must move with the calibrated grille field. Their reference
    # top faces measure 15.85 x 6.10 mm; the reconstructed .2 mm edge rolls
    # give an outer 16.25 x 6.50 mm body. Original internal mechanism retained.
    key_holes = _tools(m, 'System-key seat', 4)
    stem_holes = _tools(m, 'System-button plunger passage', 4)
    for i, (key, side) in enumerate([('SteamKey', -1), ('QuickAccessKey', 1)]):
        x, y = side * 97.655, -24.092
        delta = (side * (97.655 - 103), -24.092 + 31, 0)
        cap = m.rr(16.25, 6.5, .85, (x, y, 36.3), 3.2)
        cap = cap.makeFillet(.2, [e for e in cap.Edges if e.BoundBox.ZLength < 1e-6])
        replace(m, key, cap, 'Measured Valve Steam/Quick Access key position; reconstructed pill cap')
        key_holes[i].Shape = m.rr(16.55, 6.8, 2.0, (x, y, 35.3), 3.3)
        for prefix in ('SystemSwitch', 'SystemStem'):
            _move(m, prefix + str(i), delta)
        stem_holes[i].Shape = m.parts['SystemStem' + str(i)].Shape.copy()
        for name in (['SteamMark'] if i == 0 else ['QuickDot0', 'QuickDot1', 'QuickDot2']):
            _move(m, name, delta)

    # Reference front grille topology: 4/3/3 openings, including one longer
    # inner opening in the middle row. The opposite side is mirrored.
    rows = [(-34.035, [(91.2958, 3.9246), (95.7632, 3.9246),
                      (100.2306, 3.9246), (104.6980, 3.9246)]),
            (-37.235, [(92.4129, 6.1589), (97.9974, 3.9246), (102.4648, 3.9246)]),
            (-40.435, [(91.2963, 3.9246), (95.7642, 3.9246), (100.2316, 3.9246)])]
    speaker_tools = _tools(m, 'Staggered front speaker grille', 2)
    for i, side in enumerate((-1, 1)):
        slots = [m.rr(width, 1.6931, 1.8, (side * x, y, 35.5), .8)
                 for y, row in rows for x, width in row]
        speaker_tools[i].Shape = Part.makeCompound(slots)
        for prefix in ('SpeakerMesh', 'SpeakerFrame', 'SpeakerMagnet', 'SpeakerDiaphragm', 'SpeakerFlex'):
            _move(m, prefix + str(side), (side * (98 - 103), -37.235 + 44.5, 0))

    # Eleven measured slot centers at 5 mm pitch; 56.5 mm in the drawing is
    # the accessory keepout span, not an opening to cut in the enclosure.
    top = App.Rotation(V(0, 0, 1), V(0, 1, 0))
    vent_tool = _tools(m, 'Thirteen top exhaust slots', 1)[0]
    vent_tool.Shape = Part.makeCompound([m.rr(4.4913, 8.0, 3.5, (x, 55.4, 28.461), 2.0, top)
                                        for x in range(-25, 26, 5)])
    vent_tool.Label = 'Eleven centered LCD top exhaust slots · tool'
    m.doc.recompute()

    # The drawing identifies the centerline ambient-light sensor and specifies
    # a diameter 3 mm keepout. Its actual optical window diameter is not given;
    # use an explicitly estimated 1.44 mm inset, separate from that keepout.
    tool = Part.makeCylinder(.75, .8, V(0, 52.05, 36.3))
    m.cut('DisplaySurround', tool, 'Estimated optical window for documented ambient-light sensor')
    m.cyl('AmbientLightSensorWindow', 'Ambient-light sensor optical window, local diameter estimated',
          .72, .5, (0, 52.05, 36.5), 'Display', 7, 'screen')
    m.box('AmbientLightSensorPackage', 'Ambient-light sensor package study',
          2, 2, .9, (0, 52.05, 35.2), 'Display', 3, 'black', .2, True)
    m.doc.recompute()
    m.profile['stages'] = 17
    m.checkpoint(17, 'valve_display_dimensions_audio_fields_and_exhaust',
                 '按 Valve 2022 参考图修正显示区与盖板尺寸、双麦克风位置和孔径、触控板与下方系统键位置、每侧十孔扬声器与居中十一孔排风口，补齐环境光传感器窗口。内部支承随外部接口移动，传感器孔径、局部圆角和散热内部仍为近似。')
