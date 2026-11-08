"""HST-3200 exterior and mating-interface corrections from primary evidence.

Card-edge dimensions come from a working cartridge PCB. Other local housings,
clearances and the nonstandard mini-DIN key are fitted study geometry.
"""
import FreeCAD as App
import Part
from .core import V
from . import geometry as g
from .handheld_refinement import replace

CARTRIDGE_CENTRES=tuple([i-37.5 for i in range(1,37)]+[i-37.5 for i in range(44,75)])
C8_CONTACT_PITCH=8.6
CONTROLLER_STUDY_PITCH=2.55


def _replace(m,key,shape,reason):
    shape.check(True)
    return replace(m,key,shape,reason)


def _tool(m,label):
    found=[o for o in m.doc.Objects if o.Label.startswith(label+' · tool')]
    assert len(found)==1,(label,len(found))
    return found[0]


def _figure8(origin,normal,depth,clearance=0):
    # Volex nominal C7 front profile: 16.0 x 7.85, 8.6 mm contact centres.
    # The waist curve and local fit clearance are construction estimates.
    rx,ry=3.7+clearance,3.925+clearance
    lobes=[]
    for x in [-4.3,4.3]:
        ellipse=Part.Ellipse(V(),ry,rx).toShape();ellipse.rotate(V(),V(0,0,1),90);ellipse.translate(V(x,0,0))
        lobes.append(Part.Face(Part.Wire([ellipse])).extrude(V(0,0,depth)))
    bridge=Part.makeBox(2.2+2*clearance,3+2*clearance,depth,V(-1.1-clearance,-1.5-clearance,0))
    shape=lobes[0].fuse(bridge).fuse(lobes[1]).removeSplitter()
    shape.Placement=App.Placement(V(*origin),g.rotation(normal,(0,0,1)))
    return shape


def _inlet_plate(m,clearance=0,depth=3,y=111.5):
    rear=g.rotation((0,1,0),(0,0,1))
    head=m.rr(31.2+2*clearance,17.2+2*clearance,depth,(-91,y,49.5),1.7,rear)
    stem=m.rr(15.5+2*clearance,8+2*clearance,depth,(-91,y,37.1),.5,rear)
    return head.fuse(stem).removeSplitter()


def refine_saturn(m):
    before=tuple(m.parts)
    # The working USB-cartridge design uses two 67-contact rows: 36 + 31,
    # 1 mm pitch, with an 8 mm centre separation across its 6 mm board notch.
    reader=m.rr(83.4,13,14,(0,81,65),1.1).cut(m.rr(75.4,2.4,12.7,(0,81,66.5),.3))
    key=m.rr(5.6,2.4,12.5,(2.5,81,66.4),.15)
    reader=reader.fuse(key).removeSplitter()
    _replace(m,'CartridgeReader',reader,'134-position 1.0 mm card-edge opening with estimated clearances around the 6 mm locating notch')
    for side in [-1,1]:
        contacts=[Part.makeBox(.55,.16,10.4,V(x-.275,81+side*.95-.08,68)) for x in CARTRIDGE_CENTRES]
        _replace(m,'CartridgeContactBank'+str(side),Part.makeCompound(contacts),
                 '67 contact springs per face at 1.0 mm pitch, with the 36/31 keyed split')

    # The original rear power plate has a descending centre stem, and the
    # third fixing is below the left ear rather than centred under the inlet.
    plate=_inlet_plate(m).cut(_figure8((-91,111,47),(0,1,0),4,.2))
    _replace(m,'ACInlet',plate,'HST-3200 photograph-fitted T-shaped plate and compatible C8 mating mouth')
    _tool(m,'Upper-housing mains inlet aperture').Shape=_inlet_plate(m,.35,12,106)
    for i,x in enumerate([-91-4.3,-91+4.3]):
        _replace(m,'ACInletPin'+str(i),Part.makeCylinder(.9,6,V(x,107.7,47),V(0,1,0)),
                 'C8 contact centres at 8.6 mm; study pin diameter retained')
    shape=m.parts['ACFixing2'].Shape.copy();shape.translate(V(12,0,5.5))
    _replace(m,'ACFixing2',shape,'Lower-left rear inlet fixing position fitted from HST-3200 photograph')
    tool=_tool(m,'Lower inlet bracket fixing recess');shape=tool.Shape.copy();shape.translate(V(12,0,5.5));tool.Shape=shape
    # Keep the displayed cord end consistent with its console mating inlet.
    head=_figure8((267.8,20,8),(-1,0,0),10.5)
    holes=[Part.makeCylinder(1.45,10.9,V(268,y,8),V(-1,0,0)) for y in [15.7,24.3]]
    _replace(m,'ACDeviceHead',head.cut(Part.makeCompound(holes)),
             'C7 compatible nominal 16 x 7.85 mm nose, 8.6 mm contact spacing; local waist and bores estimated')
    _replace(m,'ACDeviceGrip',m.rr(24,19,10,(280,20,3),1.3),'Cord grip clears the corrected 16 mm C7 nose')
    for i,y in enumerate([15.7,24.3]):
        contact=Part.makeCylinder(1.3,6,V(265.5,y,8),V(-1,0,0)).cut(Part.makeCylinder(1.05,6.2,V(265.6,y,8),V(-1,0,0)))
        _replace(m,'ACDeviceContact'+str(i),contact,'C7 study receptacle leaves radial clearance around the retained C8 pin')

    # Original Saturn uses a nonstandard keyed mini-DIN-10, not full-size DIN.
    # The nominal male sleeve is 9.5 mm; the socket clearance is estimated.
    # Retain the existing 3/4/3 contact study pattern, updating both key halves.
    x,z=-91,17
    outer=Part.makeCylinder(5.1,11,V(x,103.3,z),V(0,1,0))
    cavity=Part.makeCylinder(4.8,11.4,V(x,103.1,z),V(0,1,0)).common(Part.makeBox(12,12,12,V(x-6,103,z-4.5)))
    _replace(m,'AVShell',outer.cut(cavity),'Mini-DIN receptacle sleeve with flat lower mating stop; local socket clearance estimated')
    _tool(m,'Ten-position AV mini-DIN aperture').Shape=Part.makeCylinder(5.4,13,V(x,103,z),V(0,1,0))
    points=[(-3.2,2),(0,2),(3.2,2),(-4,0),(-1.4,0),(1.4,0),(4,0),(-3,-2.3),(0,-2.3),(3,-2.3)]
    carrier=Part.makeCylinder(4.4,3,V(x,108,z),V(0,1,0)).fuse(Part.makeBox(1.2,3,.95,V(x-.6,108,z+3.8)))
    carrier=carrier.cut(Part.makeCompound([Part.makeCylinder(.7,3.4,V(x+dx,107.8,z+dz),V(0,1,0)) for dx,dz in points]))
    _replace(m,'AVCarrier',carrier,'Photograph-fitted upper orientation key on the original off-standard Saturn socket')
    refine_av_plug(m,points)

    # The existing cable and console previously had different pitches. Keep
    # the cable's study pitch for both until an OEM drawing is available.
    for port,x in enumerate([-39,39],1):
        for i in range(9):
            _replace(m,f'ControllerContact{port}_{i}',m.rr(.9,7,.12,(x+(i-4)*CONTROLLER_STUDY_PITCH,-109,21.45),.08),
                     'Matched controller/plug study pitch, 2.55 mm; not verified as an OEM dimension')
    add_case_overlap(m)
    m.doc.recompute();assert tuple(m.parts)==before
    m.profile['stages']=23
    return m.checkpoint(23,'keyed_134_contact_cartridge_and_original_rear_interfaces',
        '依据可制造卡带 PCB 修正为双面各 67 接点、1 mm 节距和 36/31 防呆分段；按 HST-3200 实机图修正后电源 T 形面板与下侧固定点，'
        'C7/C8 配对端采用 8.6 mm 接点间距，mini-DIN 配对端加入方向键及 9.5 mm 插头套筒，手柄接口与插头采用一致的示意节距。局部壳形、间隙与非标准接点位置仍为估计。')

def add_case_overlap(m):
    """Estimated internal lip closes the see-through 0.25 mm shell seam."""
    from .retro_common import fuse_feature
    if getattr(m.parts['LowerHousing'],'FidelityOverlapLip',False):return
    old=m.parts['LowerHousing'];number=getattr(old,'PartNumber',None)
    flange=m.rr(258,228,.4,(0,0,24.6),7).cut(m.rr(253.4,223.4,.6,(0,0,24.5),4.8))
    lip=m.rr(255.8,225.8,2.6,(0,0,24.6),6.2).cut(m.rr(253.4,223.4,2.8,(0,0,24.5),4.8))
    lip=flange.fuse(lip).removeSplitter()
    labels=['Side cooling slots','Rear battery and expansion service opening','Controller 1 front opening','Controller 2 front opening']
    for label in labels:
        tool=next(o for o in m.doc.Objects if o.Label.startswith(label+' · tool'))
        lip=lip.cut(tool.Shape)
    fuse_feature(m,'LowerHousing',lip,'Estimated internal seam-overlap lip with port, service-cover and vent clearances')
    obj=m.parts['LowerHousing'];obj.addProperty('App::PropertyBool','FidelityOverlapLip','Revision');obj.FidelityOverlapLip=True
    if number is not None:obj.addProperty('App::PropertyString','PartNumber','Study');obj.PartNumber=number


def refine_av_plug(m,points):
    outer=Part.makeCylinder(4.75,8.4,V(220,-2.7,8),V(0,1,0)).common(Part.makeBox(12,10,12,V(214,-3,3.6)))
    inside=Part.makeCylinder(4.5,8.8,V(220,-2.9,8),V(0,1,0)).common(Part.makeBox(12,10,12,V(214,-3,3.9)))
    shell=outer.cut(inside).cut(Part.makeBox(1.5,10,2,V(219.25,-3,11.6)))
    _replace(m,'AVPlugShield',shell,'Nominal 9.5 mm mini-DIN sleeve with continuous flat lower metal wall and upper key slot')
    carrier=Part.makeCylinder(4.4,3,V(220,-2.6,8),V(0,1,0)).common(Part.makeBox(12,4,12,V(214,-2.8,4.0)))
    carrier=carrier.cut(Part.makeBox(1.5,4,2,V(219.25,-2.8,11.6)))
    carrier=carrier.cut(Part.makeCompound([Part.makeCylinder(.58,3.4,V(220+dx,-2.8,8+dz),V(0,1,0)) for dx,dz in points]))
    _replace(m,'AVPlugCarrier',carrier,'Cable insert clears the keyed sleeve and original Saturn socket; contact positions remain a study')


stage23=refine_saturn
