"""Original Series X vent count and tactile rear-port identification.

The 2020 firsthand photographs show a 12-by-12 top grid. A contemporary
hands-on measurement gives approximately 10 mm hole diameters. Pitch, dish
curvature and tactile-mark dimensions remain photographic study estimates.
"""
import math

import FreeCAD as App
import Part

from .core import V
from .handheld_refinement import replace
from . import geometry as g


TOP_GRID_COUNT = 12
TOP_GRID_PITCH = 12.0  # Photo-estimated; no manufacturer pitch drawing found.
TOP_HOLE_RADIUS = 5.0


def vent_centres():
    return tuple((i, j, (i - 5.5) * TOP_GRID_PITCH,
                  (j - 5.5) * TOP_GRID_PITCH)
                 for i in range(TOP_GRID_COUNT) for j in range(TOP_GRID_COUNT))


def _prism(origin, u_axis, v_axis, inward, points, depth, start=0):
    p, u, v, n = V(*origin), V(*u_axis), V(*v_axis), V(*inward)
    wire_points = [p + u * a + v * b + n * start for a, b in points]
    return Part.Face(Part.makePolygon(wire_points + [wire_points[0]])).extrude(n * depth)


def _block(origin, u, v, inward, width, height, depth, cu=0, cv=0, start=0):
    return _prism(origin, u, v, inward,
                  [(cu-width/2, cv-height/2), (cu+width/2, cv-height/2),
                   (cu+width/2, cv+height/2), (cu-width/2, cv+height/2)], depth, start)


def correct_port_contacts(m):
    """Replace the universal four-contact shortcut with interface topologies.

    Positions match the current console apertures. OEM connector bodies and
    solder tails are not inferred from third-party connector part numbers.
    """
    def update(key, shape, label=None):
        shape.check(True)
        if key in m.parts:
            obj = replace(m, key, shape, 'Interface-specific contact geometry from manufacturer reference')
            if label:
                obj.Label = label
        else:
            m.feature(key, label or 'Independent connector contact', shape, 'Ports', 1, 'gold', True)

    # The rear USB-A receptacles are rotated ninety degrees compared with the
    # front port. The long tongue/contact axis must rotate with the opening.
    for key, origin, u, v, inward, depth in [
            ('FrontUSB', (54, -75.15, 29), (1, 0, 0), (0, 0, 1), (0, 1, 0), 9),
            ('RearUSB1', (-5, 75.2, 97), (0, 0, 1), (1, 0, 0), (0, -1, 0), 10),
            ('RearUSB2', (-5, 75.2, 75), (0, 0, 1), (1, 0, 0), (0, -1, 0), 10)]:
        update(key+'Tongue', _block(origin, u, v, inward, 10.8, 1.2, depth-2.2,
                                    cv=.45, start=1.2), 'USB-A insulating tongue')
        for i, offset in enumerate((-3.5, -1, 1, 3.5)):
            update(key+'Contact'+str(i), _block(origin, u, v, inward, .65, .08, 3.2,
                                               cu=offset, cv=1.10, start=1.8),
                   'USB-A legacy contact '+str(i+1))
        for i in range(5):
            update(key+'Contact'+str(i+4), _block(origin, u, v, inward, .55, .08, 1.65,
                                                 cu=(i-2)*2, cv=1.10, start=6.0),
                   'USB-A SuperSpeed contact '+str(i+5))

    # The Ethernet jack has eight narrow spring contacts at nominal 1.02 mm
    # pitch, and a carrier at the cavity roof instead of a central USB tongue.
    origin, u, v, inward = (-5, 75.2, 51), (1, 0, 0), (0, 0, 1), (0, -1, 0)
    update('EthernetTongue', _block(origin, u, v, inward, 10.8, 1.0, 6.3,
                                    cv=5.0, start=2), 'Eight-contact RJ45 upper carrier')
    p, ua, va, n = V(*origin), V(*u), V(*v), V(*inward)
    for i in range(8):
        left = p + ua * ((i-3.5)*1.02-.19)
        pts = [left+n*2.2+va*1.5, left+n*8.0+va*4.35,
               left+n*8.0+va*4.43, left+n*2.2+va*1.58]
        shape = Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(ua*.38)
        update('EthernetContact'+str(i), shape, 'RJ45 spring contact '+str(i+1))

    # HDMI Type A is a keyed trapezoid with ten contacts on one tongue face
    # and nine on the other. The console's upright orientation is retained.
    origin, u, v, inward = (13, 75.2, 22), (0, 0, 1), (1, 0, 0), (0, -1, 0)
    outer = [(-7.5,2.825), (7.5,2.825), (7.5,-1.325), (6,-2.825),
             (-6,-2.825), (-7.5,-1.325)]
    inner = [(-7,2.275), (7,2.275), (7,-1.12), (5.85,-2.275),
             (-5.85,-2.275), (-7,-1.12)]
    shell = _prism(origin,u,v,inward,outer,10).cut(_prism(origin,u,v,inward,inner,10.2,-.1))
    update('HDMIShell', shell, 'Keyed HDMI Type A metal sleeve')
    update('HDMITongue', _block(origin,u,v,inward,11.3,.96,7.1,start=1.5),
           'HDMI two-sided insulating tongue')
    index = 0
    for count, cv in [(10, .53), (9, -.53)]:
        for i in range(count):
            update('HDMIContact'+str(index),
                   _block(origin,u,v,inward,.3,.06,5.7,cu=(i-(count-1)/2)*1.0,
                          cv=cv,start=2), 'HDMI Type A contact position '+str(index+1))
            index += 1

    # The printed legend follows the upright receptacle's long edge, leaving
    # the moulded tactile bar unobstructed. It is a font-based label study.
    font = m.root/'references/DejaVuSans.ttf'
    glyphs = Part.makeWireString('HDMI OUT', str(font.parent)+'/', font.name, 1.1)
    solids = [face.extrude(V(0,0,.018)) for glyph in glyphs if glyph
              for face in Part.makeFace(glyph, 'Part::FaceMakerBullseye').Faces]
    label = Part.makeCompound(solids)
    rotation = App.Rotation(V(0,1,0),90).multiply(g.rotation((0,1,0),(0,0,1)))
    label.Placement = App.Placement(V(17.6,75.395,17), rotation)
    update('HDMIMark', label, 'HDMI OUT')


def refine_seriesx(m):
    """Apply after stage 19 without renumbering existing physical components."""
    before = tuple(m.parts)
    centres = vent_centres()
    grille = m.rr(151, 151, 8.9, (0, 0, 292.1), .8)
    grille = grille.cut(Part.makeSphere(410, V(0, 0, 702.4)))
    holes = [Part.makeCylinder(TOP_HOLE_RADIUS, 12, V(x, y, 290))
             for _, _, x, y in centres]
    grille = grille.cut(Part.makeCompound(holes))
    grille = grille.cut(Part.makeCompound([m.parts['MainShell'].Shape,
                                          m.parts['RearPanel'].Shape]))
    grille.check(True)
    replace(m, 'TopGrille', grille,
            'Original 2020 12 x 12 exhaust grid; approximately 10 mm openings')
    for i, j, x, y in centres:
        surface = 702.4 - math.sqrt(410 ** 2 - x * x - y * y)
        top = min(298.7, surface - .45)
        # A thin independent colour layer preserves the original material IDs
        # while avoiding the former thick sleeves that narrowed each opening.
        liner = Part.makeCylinder(4.98, 1.35, V(x, y, top - 1.35)).cut(
            Part.makeCylinder(4.96, 1.55, V(x, y, top - 1.45)))
        liner.check(True)
        key = 'GreenVent%02d_%02d' % (i, j)
        if key in m.parts:
            replace(m, key, liner, 'Green inner-wall colour follows corrected 12 x 12 grid')
        else:
            m.feature(key, 'Green interior exhaust-hole colour layer', liner,
                      'Body', 9, 'green')

    # The original rear panel uses three dots for either USB port, two for
    # Ethernet, four for storage, one for power and a bar for HDMI. These are
    # moulded into the panel rather than floating labels or extra components.
    raised = []
    dot_sets = [('USB1', -16, 97, 3), ('USB2', -16, 75, 3),
                ('Ethernet', -16, 51, 2), ('AC', -16, 22, 1),
                ('Storage', 20.5, 60, 4)]
    for _, x, z, count in dot_sets:
        for i in range(count):
            raised.append(Part.makeSphere(.65, V(x, 74.84, z + (i - (count - 1) / 2) * 3.2)))
    raised.append(Part.makeBox(.8, .18, 6, V(20.1, 75.3, 19)))
    panel = m.parts['RearPanel'].Shape.multiFuse(raised).removeSplitter()
    panel.check(True)
    replace(m, 'RearPanel', panel,
            'Original tactile port identifiers: USB 3 dots, LAN 2, storage 4, AC 1, HDMI bar')

    correct_port_contacts(m)
    assert tuple(k for k in m.parts if k in before) == before
    assert len(m.parts) == len(before) + 57
    m.doc.recompute()
    m.profile['stages'] = 20
    return m.checkpoint(20, 'original_144_exhaust_holes_and_tactile_ports',
        '将顶部排风孔从 11×11 改为实机 12×12，并按同期实机测量采用约 10 mm 孔径；'
        '绿色内壁随孔阵列调整，补入背板接口的模塑触觉圆点和 HDMI 横条。'
        '三只 USB-A 改为 4+5 触点、RJ45 改为 8 触点，HDMI 改为梯形口与 10+9 双面触点；'
        '局部孔距、曲率、圆点和连接器外形尺寸仍有估计值。')


stage20 = refine_seriesx
