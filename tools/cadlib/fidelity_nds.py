"""NTR-001 details checked against Nintendo specifications and repair evidence."""
import FreeCAD as App
import Part
from .core import V
from .geometry import appearance
from .handheld_refinement import replace


def stage17(m):
    """Keep the established envelope; correct identified physical details."""
    m.set_pose(180)
    # Nintendo's original DS/Lite comparison specifies ~75 mm long, ~4 mm
    # maximum diameter. The shaft and retention geometry remain image estimates.
    grip = m.parts['StylusGrip'].Shape.optimalBoundingBox(False, False)
    replace(m, 'StylusGrip', Part.makeCylinder(2.0, 7.0,
            V(grip.Center.x, grip.YMin, grip.Center.z), V(0, 1, 0)),
            'NTR-004 maximum diameter: approximately 4.0 mm, Nintendo DS specification')
    m.parts['StylusGrip'].Fidelity = 'Published approximate maximum stylus diameter; estimated retention profile'

    # Nintendo manual pp.8-9: the left aperture is recharge (orange), the
    # right aperture is power (green, or red for low battery). Show normal power.
    m.colors['charge_orange'] = (1.0, .40, .035)
    for key, material, label in [('StatusLED0', 'charge_orange', 'Recharge indicator (orange)'),
                                  ('StatusLED1', 'led', 'Power indicator (green)')]:
        o = m.parts[key]
        o.MaterialDescription = material
        o.Label = label
        o.Fidelity = 'Indicator function, left/right order and color from Nintendo manual pp.8-9; lens size estimated'
        appearance(o, m.colors[material])

    # Firsthand NTR-001 disassembly shows seven Y00 rear fixings. Keep the
    # existing assembly seats; only correct the visible drive, not guessed threads.
    for i in range(7):
        key = 'RearCoverScrew' + str(i)
        b = m.parts[key].Shape.optimalBoundingBox(False, False)
        fastener = Part.makeCylinder(1.28, .35).fuse(Part.makeCylinder(.62, 2.8, V(0, 0, .33)))
        slots = []
        for angle in (0, 120, 240):
            slot = Part.makeBox(.26, .97, .22, V(-.13, -.08, -.02))
            slot.rotate(V(), V(0, 0, 1), angle)
            slots.append(slot)
        fastener = fastener.cut(Part.makeCompound(slots))
        fastener.translate(V(b.Center.x, b.Center.y, b.ZMin))
        o = replace(m, key, fastener, 'Seven rear Y00 tri-point screw drives shown in NTR-001 disassembly')
        o.Label = 'Rear-case Y00 tri-point fastener'
        o.Fidelity = 'Observed tri-point drive; head, shaft and installed depth remain estimates'
    m.profile['stages'] = 17
    m.checkpoint(17, 'documented_stylus_indicators_and_rear_fixings',
                 '依据任天堂规格修正触控笔最大直径，按说明书纠正充电灯与电源灯颜色及顺序，并将七枚后盖螺钉改为拆机资料所示的 Y 形槽。')
