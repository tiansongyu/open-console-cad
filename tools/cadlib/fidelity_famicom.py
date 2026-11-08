"""HVC-001 mating grids checked against compatible hardware and PCB evidence."""
import FreeCAD as App
import Part
from .core import V
from .clamshell import _move
from .geometry import appearance
from .handheld_refinement import replace


def refine_rear_field(m):
    from .famicom import _top_tools
    outer = _top_tools(m)
    outer[-1] = m.rr(76, 55.6, 35, (0, 82.3, 40.5), 1.2)
    inner = _top_tools(m, True)
    inner[-1] = m.rr(79.4, 59.0, 35, (0, 82.3, 38.3), 1.2)
    next(o for o in m.doc.Objects if o.Label.startswith('Sloping front and rear, controller wells and stepped cartridge bed · tool')).Shape = Part.makeCompound(outer)
    cavity = m.rr(146.6, 216.6, 35.6, (0, 0, 15.2), 3.3).cut(Part.makeCompound(inner))
    next(o for o in m.doc.Objects if o.Label.startswith('Following interior ceiling leaves approximately 2.2 mm top walls · tool')).Shape = cavity


def refine_colors_and_stripes(m):
    # Uncalibrated photograph sample, not an assertion of factory pigment.
    m.colors['fccream'] = (230/255, 227.5/255, 222/255)
    m.colors['fcred'] = (150/255, 45/255, 47/255)
    m.colors['fcgold'] = (.89, .83, .65)
    m.profile['color'] = list(m.colors['fccream'])
    for obj in m.parts.values():
        if obj.MaterialDescription in ('fccream', 'fcred', 'fcgold'):
            appearance(obj, m.colors[obj.MaterialDescription])
    plaque = m.parts['FrontNameplate'].Shape
    plane = plaque.Placement
    # The original nameplate has a fine gold rule broken by the Nintendo word.
    for i, (cx, width) in enumerate([(-14, 101), (61, 7)]):
        if 'NameplateRule'+str(i) in m.parts:
            continue
        stripe = m.rr(width, .28, .018, (cx, -4.9, .105), .02)
        stripe.Placement = plane.multiply(stripe.Placement)
        m.feature('NameplateRule'+str(i), 'Photograph-fitted gold nameplate rule',
                  stripe, 'Body', 4, 'fcgold')


def add_expansion_cover(m):
    front = App.Rotation(V(1, 0, 0), 90)
    outer = m.rr(30.2, 12.4, 3.5, (98, -96, 9), 2.1, front)
    inner = m.rr(28.2, 10.4, 2.85, (98, -95.9, 9), 1.3, front)
    obj = m.feature('ExpansionDustCap', 'Removable expansion-port protective cap (displayed detached)',
                    outer.cut(inner), 'Accessories', 0, 'fcred')
    obj.Fidelity = 'Removable red cap observed in Nintendo photograph; dimensions fitted; displayed detached'


def refine_dc_interface(m):
    plug = Part.makeCylinder(2.75, 8.5, V(190.1, 55, 8), V(1, 0, 0))
    plug = plug.cut(Part.makeCylinder(1.05, 8.7, V(190.0, 55, 8), V(1, 0, 0)))
    replace(m, 'AdapterPlugMetal', plug, 'Compatible Famicom 5.5 x 2.1 mm barrel plug; original modeled axial length retained')
    replace(m, 'DCJackCenter', Part.makeCylinder(1.0, 6, V(34, 102.8, 17), V(0, 1, 0)),
            'Study contact pin leaves 0.1 mm diametral clearance in the nominal 2.1 mm plug bore')
    m.cut('RFShield', Part.makeCylinder(2.85, 10, V(34, 99, 17), V(0, 1, 0)),
          'Clear the DC barrel insertion passage through the schematic shield').Refine = False
    m.doc.recompute()


def refine_rf_interface(m):
    # Same Sky RCP-02/RCJ-01 constrain the compatible RCA mating interface.
    # The compact Nintendo overmold and axial installation remain photo fits.
    sleeve = Part.makeCylinder(4.15, 11.7, V(-29, 98, 16.8), V(0, 1, 0))
    sleeve = sleeve.cut(Part.makeCylinder(3.3, 11.9, V(-29, 97.9, 16.8), V(0, 1, 0)))
    replace(m, 'RFJackSleeve', sleeve, 'Compatible RCA jack nominal 8.30 mm exterior')
    contact = Part.makeCylinder(1.75, 7, V(-29, 101.8, 16.8), V(0, 1, 0))
    contact = contact.cut(Part.makeCylinder(1.625, 7.2, V(-29, 101.7, 16.8), V(0, 1, 0)))
    replace(m, 'RFJackContact', contact, 'Study socket clearance around a nominal 3.20 mm RCA pin')
    replace(m, 'RFPlugBody', Part.makeCylinder(4.6, 8, V(213.1, 151, 8), V(1, 0, 0)),
            'Compact RF plug overmold widened around the standard RCA sleeve; fitted outer grip')
    sleeve = Part.makeCylinder(4.5, 5.5, V(221.3, 151, 8), V(1, 0, 0))
    sleeve = sleeve.cut(Part.makeCylinder(4.175, 5.7, V(221.2, 151, 8), V(1, 0, 0)))
    replace(m, 'RFPlugSleeve', sleeve, 'Compatible RCA 9 mm sleeve, 5.5 mm exposed length; clearance estimated')
    pin = Part.makeCylinder(1.6, 11.9, V(221.3, 151, 8), V(1, 0, 0))
    pin = pin.fuse(Part.makeSphere(1.6, V(233.2, 151, 8))).removeSplitter()
    replace(m, 'RFPlugPin', pin, 'RCA pin within manufacturer 3.25 +0/-0.15 mm range, with 8 mm projection beyond sleeve')
    m.cut('RFShield', Part.makeCylinder(4.5, 11, V(-29, 98.5, 16.8), V(0, 1, 0)),
          'Open the RF mating passage through the schematic shielding').Refine = False
    m.doc.recompute()


def repair_controller_leads(m):
    from .atari2600 import _rounded_route
    from .famicom import _controller_pose
    for number, side in ((1, -1), (2, 1)):
        # Follow stage10's route around the outside of the rear shoulders.
        points = [V(side*65.3, 89.5, 43), V(side*65.3, 93.5, 43),
                  V(side*79, 98, 43), V(side*85, 112, 39),
                  V(side*79, 126, 25), V(side*66, 121, 20),
                  V(side*63, 118.7, 20), V(side*63, 112.7, 20)]
        lead = _rounded_route(points, 2.0, 1.65)
        lead.check(True)
        replace(m, 'ControllerCable'+str(number), lead,
                'Analytic rounded display lead with aligned bulkhead tangent; flexible pose and displayed length remain estimates')
        grommet = Part.makeCylinder(2.2, 5, V(side*63, 10, 6.5), V(side, 0, 0))
        grommet.Placement = _controller_pose(side).multiply(grommet.Placement)
        grommet.check(True)
        replace(m, 'P'+str(number)+'CableGrommet', grommet,
                'Restore analytic strain relief; the straight outgoing cable meets its end face without the old spline cut')


def repair_remaining_legacy_shapes(m):
    from .atari2600 import _rounded_route, _helical_spring
    for key, radius, pitch, height, wire_radius in [
            ('EjectReturnSpring', 1.35, .55, 15, .18),
            ('RFCoilWinding0', 1.65, .55, 4, .16),
            ('RFCoilWinding1', 1.65, .55, 4, .16)]:
        old = m.parts[key].Shape
        coil = _helical_spring(radius, pitch, height, wire_radius)
        coil.Placement = old.Placement
        coil.check(True)
        replace(m, key, coil, 'Split helix at native knots before sweeping; retained nominal spring parameters and placement')
    for i in range(3):
        route = [V(-36+i*1.5, -62, 38), V(-40+i*1.5, -57, 30),
                 V(-45+i, -52, 24), V(-45+i, 22, 24),
                 V(-44+i, 45, 20), V(-37+i, 52, 13)]
        wire = _rounded_route(route, 1, .27)
        wire.check(True)
        replace(m, 'PowerHarness'+str(i), wire,
                'Analytic rounded schematic power harness; endpoint positions retained')
    power = Part.makeCompound([m.parts['PowerHarness'+str(i)].Shape for i in range(3)])
    for prefix in ('Power-switch terminal entry seats', 'Power-harness entry apertures through RF shield'):
        next(o for o in m.doc.Objects if o.Label.startswith(prefix+' · tool')).Shape = power.copy()
    routes = {
        'AdapterCable': (2.5, 1.35, [(204.2,100,18),(210.5,100,18),(216,103,17),
                                    (230,87,10),(225,63,8),(221,55,8),(215.7,55,8)]),
        'RFInputCable': (2, 1.0, [(191.1,171,9),(200,171,9),(205,157,8),
                                  (208,151,8),(213,151,8)]),
        'RFTVCable': (2, 1.1, [(166,196.1,9),(166,209,9),(184,219,8),
                               (194,213,8),(201,213,8)]),
    }
    for key, (bend, radius, points) in routes.items():
        wire = _rounded_route([V(*point) for point in points], bend, radius)
        wire.check(True)
        replace(m, key, wire,
                'Analytic rounded accessory display lead with original endpoint positions and connector tangents')
    old_board = m.parts['Mainboard'].Shape.copy()
    m.parts['Mainboard'].Refine = False
    for key in ('PowerSwitchBody', 'RFShield'):
        m.parts[key].Refine = False
    m.doc.recompute()
    for residual in (old_board.cut(m.parts['Mainboard'].Shape),
                     m.parts['Mainboard'].Shape.cut(old_board)):
        assert residual.isValid() and sum(abs(s.Volume) for s in residual.Solids) < 1e-6
    for key in ('Mainboard', 'PowerSwitchBody', 'RFShield'):
        m.parts[key].Shape.check(True)


def refine_exterior(m):
    """Correct features directly visible in Nintendo's original-console photos."""
    # Thirteen slots occupy the recessed rear field. The old cut started above
    # its ceiling, leaving most of each nominal slot closed.
    refine_rear_field(m)
    vents = [m.rr(2.0, 27.0, 16, (-30 + i * 5.0, 94.0, 37.8), .45)
             for i in range(13)]
    next(o for o in m.doc.Objects if o.Label.startswith('Rear heat ventilation slots · tool')).Shape = Part.makeCompound(vents)
    for name, x in [('POWER', -40.5), ('RESET', 40.5)]:
        m.cut('UpperShell', m.rr(37, 26, 1.0, (x, -75, 52.5), 1.8),
              'Official-photo recessed ' + name + ' control field (fitted depth)')
        _move(m, name + 'Mark', (0, 0, -.5))

    # The port is offset to the right of the body centre. Nintendo's close-up
    # also shows a metal rim and a recessed amber insulator, not an empty cream
    # box. The local outline/depth are photographic fits, not OEM tolerances.
    front = App.Rotation(V(1, 0, 0), 90)

    def outline(top_width, bottom_width, height, depth, y):
        from .psp import _polygon
        points = [(-top_width/2, height/2), (top_width/2, height/2),
                  (bottom_width/2, -height/2), (-bottom_width/2, -height/2)]
        s = _polygon(points, 0, depth)
        vertical = [edge for edge in s.Edges if edge.BoundBox.ZLength > depth-.01]
        s = s.makeFillet(.8, vertical)
        s.Placement = App.Placement(V(16.5, y, 16.5), front)
        return s

    holes = []
    for row, count, z in ((0, 8, 17.92), (1, 7, 15.08)):
        for i in range(count):
            key = 'ExpansionPin' + str(row * 8 + i)
            _move(m, key, (16.5, 0, 0))
            holes.append(Part.makeCylinder(.43, 6.0,
                         V(16.5 + (i-(count-1)/2)*2.77, -100.8, z), V(0, -1, 0)))
    insulator = outline(25.9, 23.8, 8.5, 5.5, -101.0).cut(Part.makeCompound(holes))
    replace(m, 'ExpansionHousing', insulator,
            'Offset recessed insulator visible in Nintendo HVC-001 expansion-port photograph')
    m.colors['expansion_insulator'] = (.66, .60, .42)
    m.parts['ExpansionHousing'].MaterialDescription = 'expansion_insulator'
    appearance(m.parts['ExpansionHousing'], m.colors['expansion_insulator'])
    rim = outline(27.8, 25.6, 10.1, .45, -109.55).cut(outline(26.4, 24.2, 8.7, .8, -109.4))
    m.feature('ExpansionMetalRim', 'Original expansion-port metal surround', rim,
              'Ports', -2, 'metal')
    aperture = m.rr(28.4, 10.8, 12, (16.5, -98.5, 16.5), 1.0, front)
    tools = [o for o in m.doc.Objects if o.Label.startswith('Front expansion aperture · tool')]
    assert tools
    for tool in tools:
        tool.Shape = aperture.copy()
    refine_colors_and_stripes(m)
    m.doc.recompute()


def stage17(m):
    m.set_pose(180)
    # Famicom is 2.54 mm; the superficially similar NES edge uses 2.50 mm.
    # The selected GPM-02 reconstruction corroborates the 5.08 mm PCB row gap.
    channels = []
    board_holes = []
    for side in (-1, 1):
        for i in range(30):
            x = (i - 14.5) * 2.54
            y = 35 + side * 2.54
            leg = m.rr(.5, .38, 8.0, (x, y, 13.4), .02)
            foot = m.rr(.5, 1.70, .22, (x, 35 + side * 1.80, 21.1), .02)
            contact = m.rr(.5, .20, 4.1, (x, 35 + side * 1.05, 21.0), .02)
            key = 'CardContact' + str((side + 1) // 2 * 30 + i)
            replace(m, key, leg.fuse(foot).fuse(contact),
                    'Famicom 2.54 mm edge pitch and GPM-02 5.08 mm PCB row spacing; spring form estimated')
            channels.extend([m.rr(.75, .70, 8.6, (x, y, 13.1), .04),
                             m.rr(.75, 2.4, 4.6, (x, 35 + side * 1.8, 20.8), .04)])
            board_holes.append(Part.makeCylinder(.46, 2.1, V(x, y, 13.8)))
    socket = m.rr(82, 11.2, 12, (0, 35, 16.2), .8)
    socket = socket.cut(m.rr(78, 2.0, 10.6, (0, 35, 18.0), .3))
    replace(m, 'CardSocket', socket.cut(Part.makeCompound(channels)),
            'Contact channels follow corrected Famicom connector grid')
    holes = [Part.makeCylinder(1.4, 4, V(x, 35, 15.4)) for x in (-48.5, 48.5)]
    drill = next(o for o in m.doc.Objects
                 if o.Label.startswith('Cartridge connector lead and fastening holes · tool'))
    drill.Shape = Part.makeCompound(board_holes + holes)
    for face in ('Front', 'Rear'):
        for i in range(30):
            _move(m, 'GamePakContact' + face + str(i), ((i - 14.5) * .04, 0, 0))

    # Deep molded Famicom port is not a stock metal D-sub enclosure. Use the
    # compatible nominal mating grid without replacing its depth or pin form.
    for row, count, z in ((0, 8, 17.92), (1, 7, 15.08)):
        for i in range(count):
            key = 'ExpansionPin' + str(row * 8 + i)
            b = m.parts[key].Shape.optimalBoundingBox(False, False)
            _move(m, key, ((i - (count - 1) / 2) * 2.77 - b.Center.x, 0, z - b.Center.z))
            m.parts[key].Fidelity = 'Compatible nominal DA-15 mating grid; original pin diameter and depth unmeasured'
    refine_exterior(m)
    repair_controller_leads(m)
    repair_remaining_legacy_shapes(m)
    add_expansion_cover(m)
    refine_dc_interface(m)
    refine_rf_interface(m)
    m.doc.recompute()
    m.profile['stages'] = 17
    m.checkpoint(17, 'famicom_cartridge_pitch_and_expansion_grid',
                 '同步校正 Famicom 2.54 mm 卡边和 5.08 mm 焊脚排列；按官方照片修正偏右的扩展口、金属口沿与绝缘体，恢复 13 条完整散热开口及电源／复位下凹区域。局部曲率和开口尺寸为图片拟合。')
