"""Correct Model 1 AV mating geometry from the DIN-8 262-degree interface.

The compatible SD-81 manufacturer drawing establishes the pin topology, pin
diameter, centre-pin offset and male mating-barrel diameter. It does not identify
the original SEGA connector supplier. Board placement, contact depth, socket
clearance and cable hood remain study dimensions; see the reference JSON.
"""
import math

import Part

from .core import V
from .handheld_refinement import replace


OUTER_PIN_RADIUS = 4.25  # Scaled from the drawing; not a dimension callout.
OUTER_PIN_ANGLES = (139.0, 180.0, 225.0, 270.0, 315.0, 0.0, 41.0)
CENTRE_PIN_OFFSET = 0.9
MALE_PIN_RADIUS = 0.75
MALE_BARREL_RADIUS = 6.6


def contact_centres():
    """Return symmetric face coordinates, with the polarising key at the top.

    The indices retain the old component IDs; they are position indices, not
    electrical DIN pin numbers. The seventh-to-first gap is 98 degrees, giving
    the 262-degree horseshoe, and the eighth contact is above the centre.
    """
    return tuple((OUTER_PIN_RADIUS * math.cos(math.radians(a)),
                  OUTER_PIN_RADIUS * math.sin(math.radians(a)))
                 for a in OUTER_PIN_ANGLES) + ((0.0, CENTRE_PIN_OFFSET),)


def _tube(outer_radius, inner_radius, length, origin, axis):
    p, n = V(*origin), V(*axis)
    return Part.makeCylinder(outer_radius, length, p, n).cut(
        Part.makeCylinder(inner_radius, length + 0.2, p - n * 0.1, n))


def repair_saved_geometry(m):
    """Repair five legacy solids discovered by this iteration's strict reload.

    Four text compounds contain touching glyph solids. Unioning those solids
    keeps their contours while removing the duplicate contact boundaries. The
    cable splitter is regenerated from its existing dimensions and routes to
    remove invalid saved curve-on-surface data.
    """
    for key in ('WorkRAMMark', 'VideoRAM0Mark', 'VideoRAM1Mark', 'SoundRAMMark'):
        old = m.parts[key].Shape
        shape = old.Solids[0].multiFuse(old.Solids[1:]).removeSplitter()
        shape.check(True)
        assert abs(shape.Volume - old.Volume) < 1e-6, key
        replace(m, key, shape, 'Unite touching glyph solids; original text contour retained')
    end = V(279, -90, 10)
    axis = (end - V(250, -65, 10)).normalize()
    channels = [Part.makeCylinder(1.65, 18, end - axis * 10, axis)]
    for i, y in enumerate((-83, -103)):
        start = V(287.6, -90 - i * 4, 10)
        axis = (V(298, y, 10) - start).normalize()
        channels.append(Part.makeCylinder(1.1, 10, start - axis * 5, axis))
    shape = m.rr(11, 8, 6, (282, -92, 7), 2).cut(
        channels[0].multiFuse(channels[1:]))
    shape.check(True)
    assert abs(shape.Volume - m.parts['AVSplit'].Shape.Volume) < 1e-6
    replace(m, 'AVSplit', shape, 'Regenerate the original splitter dimensions and cable passages')


def refine_megadrive(m):
    """Apply after stage 13, retaining physical IDs, order and previous solids."""
    ids_before = tuple(m.parts)
    points = contact_centres()
    changed = []

    def update(key, shape, reason):
        shape.check(True)
        obj = replace(m, key, shape, reason)
        changed.append(key)
        return obj

    reason = ('Model 1 compatible DIN-8 262-degree interface: seven outer '
              'contacts and one contact 0.9 mm above centre; Same Sky SD-81 p3')
    # Socket faces +Y. Retain its shell seat and rear termination plane; the
    # insertion bore now admits the 13.2 mm male barrel with study clearance.
    update('AVBarrel', _tube(7.6, 6.75, 6.5, (-11, 98, 30), (0, 1, 0)),
           '13.2 mm mating barrel plus 0.15 mm radial study clearance')
    keyway = Part.makeBox(2.3, 5.9, 1.8, V(-12.15, 97.8, 35.2))
    insulator = _tube(6.65, 6.1, 5.5, (-11, 98, 30), (0, 1, 0))
    update('AVInsulator', insulator.cut(keyway),
           'Top polarising channel aligned with the male barrel key')
    insert = Part.makeCylinder(6.1, 2, V(-11, 98, 30), V(0, 1, 0))
    holes = []
    for i, (u, v) in enumerate(points):
        holes.append(Part.makeCylinder(1.0, 2.4,
                     V(-11 + u, 97.8, 30 + v), V(0, 1, 0)))
        update('AVContact' + str(i),
               _tube(0.95, 0.78, 4, (-11 + u, 98.1, 30 + v), (0, 1, 0)),
               reason)
    update('AVInsert', insert.cut(Part.makeCompound(holes)).cut(keyway), reason)

    # The detached plug faces +X. The 262-degree face is mirror-symmetric, so
    # mapping face U to Y and V to Z preserves the mating pattern and top key.
    shield = _tube(MALE_BARREL_RADIUS, 6.1, 9,
                   (230.4, -100, 10), (1, 0, 0))
    key_rib = Part.makeBox(9, 2.0, 1.0, V(230.4, -101, 15.4))
    update('DINShield', shield.fuse(key_rib).removeSplitter(),
           'SD-81 13.2 mm mating barrel and 2 mm top key; depth remains estimated')
    insert = Part.makeCylinder(5.85, 3, V(230.4, -100, 10), V(1, 0, 0))
    holes = []
    for i, (u, v) in enumerate(points):
        holes.append(Part.makeCylinder(0.8, 3.4,
                     V(230.2, -100 + u, 10 + v), V(1, 0, 0)))
        update('DINPin' + str(i), Part.makeCylinder(MALE_PIN_RADIUS, 7.5,
               V(230.5, -100 + u, 10 + v), V(1, 0, 0)), reason)
    plug_keyway = Part.makeBox(3.4, 2.2, 1.0, V(230.2, -101.1, 15.3))
    update('DINInsert', insert.cut(Part.makeCompound(holes)).cut(plug_keyway),
           'Rebuilt eight-bore carrier with central contact and top key clearance')

    assert tuple(m.parts) == ids_before, 'Physical part order changed'
    assert len(changed) == 21, changed
    repair_saved_geometry(m)
    assert tuple(m.parts) == ids_before, 'Physical part order changed during repair'
    m.doc.recompute()
    m.profile['stages'] = 14
    return m.checkpoint(14, 'din8_262_contact_pattern_and_key',
        '依据兼容连接器厂商图纸，将 AV 插座与插头的八等分圆周触点改为 '
        '262° 七外一内排列，修正 1.5 mm 插针、13.2 mm 插头配合外径和顶部定位键；'
        '保持组件标识与顺序，并修复旧 RAM 字形接触边界与分线护套曲面数据。'
        '孔距半径、插座间隙及轴向结构仍为图样拟合或学习尺寸。')


stage14 = refine_megadrive
