"""Correct the original VCS cartridge interface to its 2.54 mm contact pitch.

The pitch is confirmed by working cartridge-reader hardware. The optional blank
cartridge's edge-tab and pad dimensions follow a demonstrated compatible PCB,
not a claim to reproduce any original game's complete circuit board.
"""
import FreeCAD as App
import Part

from .core import V
from .handheld_refinement import replace
from . import geometry as g
from .retro_common import d_profile


CONTACT_PITCH = 2.54
EDGE_TAB_WIDTH = 32.512
PAD_WIDTH = 1.524
PAD_LENGTH = 6.35
SLOT_WIDTH = 33.2  # Study assembly clearance around the compatible edge tab.


def _unique_tool(m, label):
    found = [o for o in m.doc.Objects if o.Label.startswith(label+' · tool')]
    assert len(found) == 1, (label, len(found))
    return found[0]


def repair_legacy_solids(m):
    """Remove saved continuity/glyph defects found by the strict reload audit."""
    from .atari2600 import _helical_spring, _rounded_route

    for key, radius, pitch, height in [('SwitchReturnSpring4',2.15,.9,4.5),
                                       ('SwitchReturnSpring5',2.15,.9,4.5),
                                       ('RFCoilWinding',2.0,.6,3.6)]:
        old = m.parts[key].Shape
        shape = _helical_spring(radius,pitch,height,.13)
        shape.Placement = old.Placement
        shape.check(True)
        replace(m,key,shape,'Split the original helix at spline knots before sweeping; keep radius, pitch and placement')
    route = [V(110,108,30),V(110,124,30),V(126,146,27),V(150,150,24),V(156,150,24)]
    cable = _rounded_route(route,4,1.8)
    cable.check(True)
    replace(m,'RFCable',cable,'Analytic rounded storage route with original endpoints and connector tangents; displayed lead length remains approximate')
    old = m.parts['CartROMMark'].Shape
    shape = old.Solids[0].multiFuse(old.Solids[1:]).removeSplitter()
    shape.check(True)
    # A compound sums overlapping glyph volumes. Equality of that sum would
    # reject a correct union; verify the represented material in both directions.
    for residual in [old.cut(shape),shape.cut(old)]:
        assert residual.isValid() and sum(abs(s.Volume) for s in residual.Solids) < 1e-6
    replace(m,'CartROMMark',shape,'Unite touching glyph solids without changing the ROM study legend')


def refine_exterior(m):
    """Match the photographed rear connector orientation and visible proportions."""
    rear=g.rotation((0,1,0),(0,0,1))
    openings=[o for o in m.doc.Objects if o.Label.startswith('Recessed DE-9 controller opening · tool')]
    assert len(openings)==2
    for index,x in enumerate((-35,35)):
        frame=App.Placement(V(x,104,30),rear)
        def placed(shape):
            shape.Placement=frame.multiply(shape.Placement)
            return shape
        hood=d_profile(20.8,10.5).extrude(V(0,0,11.5)).cut(
            d_profile(18.4,8.1,3.2).extrude(V(0,0,9)))
        # A wider flange sits in the inner cavity, behind the thick rear wall,
        # so the installation clearance does not expose boards through the rim.
        hood=hood.fuse(d_profile(23.2,12.7).extrude(V(0,0,1.3))).removeSplitter()
        hood=placed(hood);tail_holes=[]
        # Five contacts sit at the wide upper edge in the original rear photo.
        for row,count,z in [(0,5,1.42),(1,4,-1.42)]:
            for i in range(count):
                point=frame.multVec(V((i-(count-1)/2)*2.77,z,3.3))
                pin=Part.makeCylinder(.45,7.9,point,V(0,1,0))
                tail=Part.makeCylinder(.23,7.7,V(point.x,99.8,point.z),V(0,1,0)).fuse(
                    Part.makeCylinder(.23,point.z-22.1+.1,V(point.x,99.8,22.1)))
                replace(m,'ControllerPin'+str(index)+'_'+str(row*5+i),pin.fuse(tail),
                        'Original rear connector: five upper / four lower contacts, 2.77 x 2.84 mm pitch')
                tail_holes.append(Part.makeCylinder(.36,8.3,V(point.x,99.5,point.z),V(0,1,0)))
        hood=hood.cut(Part.makeCompound(tail_holes));hood.check(True)
        replace(m,'ControllerSocket'+str(index),hood,
                'Upright D-shaped original port housing; local envelope fitted to Heavy Sixer rear photo')
        opening=d_profile(21.4,11.1).extrude(V(0,0,15))
        opening.Placement=App.Placement(V(x,103.5,30),rear);openings[index].Shape=opening
        surround=m.rr(24,14,.35,(x,115.84,30),2.4,rear)
        inside=d_profile(21.6,11.3).extrude(V(0,0,.6))
        inside.Placement=App.Placement(V(x,115.72,30),rear)
        replace(m,'ControllerSurround'+str(index),surround.cut(inside),
                'Smaller raised rear surround with matching D-shaped opening, from firsthand photograph')
        mark=m.parts['RearControllerMark'+str(index)].Shape.copy()
        mark.translate(V(x-mark.optimalBoundingBox(False,False).Center.x,0,0))
        replace(m,'RearControllerMark'+str(index),mark,'Centre the raised legend over its revised rear port')

    # Match the detached CX10 and paddle plugs to the corrected console keying.
    for prefix,nose_key,used,origin in [('J1','J1PlugNose',[1,2,3,4,6,8],(-13.8,-157,15)),
                                       ('J2','J2PlugNose',[1,2,3,4,6,8],(176.2,-157,15)),
                                       ('PaddlePlug','PaddlePlugNose',[3,4,5,7,8,9],(402.2,-25,18))]:
        # The old booleans baked part of their placement into the BRep. Reuse
        # the source assembly datums, not the partial Shape.Placement field.
        frame=App.Placement(V(*origin),g.rotation((1,0,0),(0,0,1)))
        nose=d_profile(17.6,7.6).extrude(V(0,0,6));nose.Placement=frame
        holes=[]
        for row,count,z in [(0,5,1.42),(1,4,-1.42)]:
            for i in range(count):
                pin=1+row*5+i
                point=frame.multVec(V((i-(count-1)/2)*2.77,z,-.3))
                holes.append(Part.makeCylinder(.8,6.5,point,V(1,0,0)))
                if pin in used:
                    point=frame.multVec(V((i-(count-1)/2)*2.77,z,.2))
                    contact=Part.makeCylinder(.7,5.7,point,V(1,0,0)).cut(
                        Part.makeCylinder(.46,5.9,point-V(.1,0,0),V(1,0,0)))
                    key=prefix+('Contact' if prefix=='PaddlePlug' else 'PlugContact')+str(pin)
                    replace(m,key,contact,'Female connector contact aligned with upper five / lower four hole pattern')
        nose=nose.cut(Part.makeCompound(holes));nose.check(True)
        replace(m,nose_key,nose,'Narrower upright female nose fitted to the console opening; unused holes retained')

    # The old Fuji mark was already present, but offset from the word below and
    # built from visibly faceted strips. Use smooth study curves and align it.
    solids=[]
    for side in [-1,1]:
        def curve(points):
            c=Part.BezierCurve();c.setPoles([V(side*x,y,0) for x,y in points]);return c.toBSpline().toShape()
        edges=[Part.makeLine(V(side*3.2,14,0),V(side*1.7,14,0)),
               curve([(1.7,14),(1.7,5.3),(2.6,.7),(9.25,0)]),
               Part.makeLine(V(side*9.25,0,0),V(side*9.25,1.5,0)),
               curve([(9.25,1.5),(4.6,2.2),(3.2,5.5),(3.2,14)])]
        solids.append(Part.Face(Part.Wire(edges)).extrude(V(0,0,.04)))
    solids.append(Part.makeBox(1.5,14,.04,V(-.75,0,0)))
    mark=Part.makeCompound(solids)
    centre=m.parts['AtariWord'].Shape.optimalBoundingBox(False,False).Center.x
    mark.Placement=App.Placement(V(centre,-116.155,30.5),g.rotation((0,-1,0),(0,0,1)))
    mark.check(True)
    replace(m,'FujiMark',mark,'Smooth three-prong photo study aligned with the existing ATARI word; not a factory logo drawing')
    m.doc.recompute()


def refine_atari2600(m):
    """Apply after stage23; keep every physical component ID and number."""
    from .atari2600 import _control_frame

    before = tuple(m.parts)
    frame = _control_frame()
    channels, vertical_bores, pcb_bores = [], [], []
    for side in [-1, 1]:
        for i in range(12):
            key = 'CartridgeContact'+str((side+1)//2*12+i)
            old_x = (i-5.5)*4.0
            x = (i-5.5)*CONTACT_PITCH
            shape = m.parts[key].Shape.copy()
            assert abs(shape.BoundBox.Center.x-old_x) < 1e-5, key
            shape.translate(V(x-old_x,0,0))
            shape.check(True)
            replace(m,key,shape,'Correct VCS 24-contact card edge from 4.0 to 2.54 mm pitch')
            end = frame.multVec(V(x,-10+side*4.4,-41.5))
            channels.extend([
                m.rr(1.05,.45,13.5,(x,-10+side*1.15,-35.2),.04),
                m.rr(1.05,4,.6,(x,-10+side*2.75,-35.15),.04),
                m.rr(.75,.75,7.5,(x,-10+side*4.4,-41.8),.04)])
            vertical_bores.append(Part.makeCylinder(.34,end.z-22+.5,V(end.x,end.y,22)))
            pcb_bores.append(Part.makeCylinder(.34,2.2,V(end.x,end.y,22.3)))

    # Rebuild the existing socket body with the revised channels. Its exterior
    # and tilt retain the photographed Heavy Sixer construction parameters.
    socket = m.rr(76,12.8,21.4,(0,-10,-41.8),1.0)
    socket = socket.cut(m.rr(SLOT_WIDTH,2.3,16.3,(0,-10,-36.2),.35))
    socket = socket.cut(Part.makeCompound(channels))
    socket.Placement = frame.multiply(socket.Placement)
    socket = socket.cut(Part.makeCompound(vertical_bores))
    socket = socket.cut(Part.makeBox(200,220,74.35,V(-100,-110,-50)))
    socket.check(True)
    replace(m,'CartridgeSocket',socket,
            'Matched 2.54 mm spring channels, board tails and 33.2 mm study insertion slot')
    _unique_tool(m,'Cartridge contact tail holes').Shape = Part.makeCompound(pcb_bores)

    # The blank accessory keeps its own enclosure and internal study board.
    # Only its mating tab and contacts adopt the compatible PCB measurements.
    cx, cy = -260.0, -160.0
    for side,z in [('Front',10.65),('Back',8.91)]:
        for i in range(12):
            shape = m.rr(PAD_WIDTH,PAD_LENGTH,.04,
                         (cx+(i-5.5)*CONTACT_PITCH,cy-45.748,z),0)
            replace(m,'CartContact'+side+str(i),shape,
                    'Compatible Atari PCB reference: 2.54 mm pitch, 1.524 x 6.35 mm gold finger')
    board = m.parts['CartPCB'].Shape.copy()
    cutters = [Part.makeBox(50,14.2,2.2,V(cx-EDGE_TAB_WIDTH/2-50,cy-49.1,8.7)),
               Part.makeBox(50,14.2,2.2,V(cx+EDGE_TAB_WIDTH/2,cy-49.1,8.7))]
    board = board.cut(Part.makeCompound(cutters))
    board.check(True)
    replace(m,'CartPCB',board,'32.512 mm mating tab from a demonstrated original-case-compatible PCB')
    # This cutter belongs to the local cartridge construction, before the
    # complete accessory is translated to its detached display position.
    _unique_tool(m,'Cartridge board-edge opening').Shape = m.rr(
        SLOT_WIDTH,3.4,5,(0,-47.7,8.1),.5)

    m.doc.recompute()
    repair_legacy_solids(m)
    refine_exterior(m)
    assert tuple(m.parts) == before
    assert abs(m.parts['CartFront'].Shape.BoundBox.Center.x-cx) < 1e-5
    m.profile['stages'] = 24
    return m.checkpoint(24,'verified_254_cartridge_pitch_and_mating_tab',
        '将主机卡座与空白卡带的两排 24 接点从 4.0 mm 节距修正为 2.54 mm，'
        '同步弹片通道和主板孔位；卡带金手指采用兼容 PCB 的 1.524×6.35 mm 尺寸，'
        '配合板舌宽度改为 32.512 mm，并同步外壳开口；按实物照片校正后 DE-9 的朝向、针排、边框和配套插头，'
        '对齐并平滑已有 Fuji 标记，修复旧线圈、RF 展示线与 ROM 字形的严格实体错误。'
        '卡座外壳、内部线路与配合间隙仍为近似。')


stage24 = refine_atari2600
