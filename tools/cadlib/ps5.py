"""Original 2020 disc PS5: editable study geometry, staged through FreeCAD MCP."""
import FreeCAD as App
import Part
from .core import V
from . import geometry as g


def _skin_section(yf,yb,front_z,rear_z,thickness,lip=0):
    points=[V(yf,front_z),V(yf+26,front_z-5),V(yb-25,rear_z-3),V(yb,rear_z)]
    if lip:
        points=[V(yf,front_z+lip),V(yf+2,front_z+lip-5),V(yf+12,front_z),V(yf+45,front_z-1),V(yb-25,rear_z-3),V(yb,rear_z)]
    top=Part.BezierCurve();top.setPoles(points)
    bottom=Part.BezierCurve();bottom.setPoles([p-V(0,thickness) for p in reversed(points)])
    return [top.toBSpline(),Part.LineSegment(points[-1],points[-1]-V(0,thickness)),bottom.toBSpline(),Part.LineSegment(points[0]-V(0,thickness),points[0])]


def _cover(m,key,label,sections,layer):
    sketches=[]
    # Local sketch X/Y -> global Y/Z; sketch normal -> global X.
    rotation=App.Rotation(V(0,1,0),V(0,0,1),V(1,0,0),'ZXY')
    for i,(x,yf,yb,zf,zb,lip) in enumerate(sections):
        if layer<0:zf-=3.5;zb-=3.5
        sk=m.doc.addObject('Sketcher::SketchObject',key+'Section'+str(i));sk.Label=label+' · editable curved section '+str(i+1)
        sk.addGeometry(_skin_section(yf,yb,zf,zb,2.5,lip),False)
        sk.Placement=App.Placement(V(x,0,0),rotation)
        sk.setExpression('Placement.Base.x',f'Parameters.Width * {x/390:.12g}')
        m.group('Construction').addObject(sk);sketches.append(sk)
    loft=m.doc.addObject('Part::Loft',key+'Loft');loft.Label=label;loft.Sections=sketches;loft.Solid=True;loft.Ruled=False;loft.Closed=False;loft.MaxDegree=3
    m.doc.recompute();assert loft.Shape.isValid() and len(loft.Shape.Solids)==1
    loft.Shape.check(True)
    for sk in sketches:sk.Visibility=False
    return m.register(loft,key,'Body',layer,'ps5white')


def stage01(m):
    m.colors.update(ps5white=(.88,.89,.91),ps5gloss=(.025,.03,.038),ps5blue=(.08,.32,.86))
    m.params.set('A3','Depth (Y)');m.params.set('A4','Height (Z)')
    _cover(m,'UpperCover','Continuous white non-drive cover',[
        (-195,-120,120,94,91,0),(-175,-125,125,93,92,0),(-95,-119,124,89,90,0),
        (0,-114,121,86.5,88.5,0),(95,-121,123,92,94,0),(170,-128,128,101,100,0),
        (195,-130,130,104,102,0)],6)
    _cover(m,'LowerCover','Asymmetric white drive-side cover',[
        (-195,-120,120,5.5,8.5,20),(-175,-125,125,5,8.5,28),(-95,-119,124,6.5,14.5,28),
        (0,-114,121,18.5,19.5,12),(95,-121,123,21.5,19.5,.01),(170,-128,128,17.5,15.5,.01),
        (195,-130,130,13.5,13.5,.01)],-6)
    m.native('CoreFrame','Original black central chassis',358,235,15,59,(-3,0,22),'Frame',0,'ps5gloss',expr={'Width':'Parameters.Width - 32 mm'})
    m.cut('CoreFrame',m.rr(353.5,230.5,61,(-3,0,23.8),13),'Open main chassis cavity').Refine=False
    opening=[V(x,-123,z) for x,z in [(-188,21),(-188,40),(22,40),(72,21)]]
    m.cut('CoreFrame',Part.Face(Part.makePolygon(opening+[opening[0]])).extrude(V(0,20,0)),'Clearance for the raised drive-side white return').Refine=False
    m.doc.recompute();m.visible()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=1
    m.checkpoint(1,'curved_original_enclosure','建立原版横置光驱机的双曲面白色可拆罩和原生黑色中框；曲面由可编辑草图放样形成，下罩保留光驱侧非对称起伏。公开约 390×260×104 mm 包络作为比例依据，局部曲率及内部尺寸为照片指导近似，接口与内部结构待后续构建。')
    m.snapshot('01_curved_front_review',normal=(.4,-1.3,.7))


STAGES={1:stage01}


def stage02(m):
    front=g.rotation((0,-1,0),(0,0,1));rear=g.rotation((0,1,0),(0,0,1))
    # Original drive entrance is in the raised white cover return.
    slot=m.rr(132,3.4,31,(-99,-104,26.4),.55,front)
    m.cut('LowerCover',slot,'Disc entrance through the raised drive-side white skin').Refine=False
    m.cut('CoreFrame',slot,'Continue the optical path through the black frame').Refine=False
    for i,z in enumerate([24.45,28.0]):
        m.box('DiscBrush'+str(i),'Opposed disc dust brush',130,3.0,.35,(-99,-107,z),'FrontIO',1,'black',.1)
    for key,x,w,h in [('FrontUSBA',21,15.2,7.3),('FrontUSBC',-5,9.9,4.4)]:
        m.cut('CoreFrame',m.rr(w,h,12,(x,-109,58),.5,front),'Launch front '+key+' aperture').Refine=False
    for key,x in [('Power',-165),('Eject',-144)]:
        m.cut('CoreFrame',m.rr(13.2,3.9,10,(x,-111,53),.8,front),'Separate '+key+' button opening').Refine=False
        m.box(key+'Button',key+' front control',12,2,2.8,(x,-117.6,51.6),'Controls',1,'black',.5)
    specs=[('RearUSB0',-119,15.4,7.5),('RearUSB1',-86,15.4,7.5),('LAN',-48,17,15),('HDMI',0,16.6,7.6),('AC',76,21,11.8)]
    for key,x,w,h in specs:
        m.cut('CoreFrame',m.rr(w,h,13,(x,109,51.5),.5,rear),'Launch rear '+key+' connector opening').Refine=False
    cuts=[Part.makeBox(5.3,12,13,V(x,110,z)) for x in range(-166,162,9) for z in [26,64]]
    m.cut('CoreFrame',cuts,'Open rear exhaust banks with integral vertical ribs').Refine=False
    cuts=[Part.makeBox(12,5.5,40,V(170,y,32)) for y in range(-96,97,10)]
    m.cut('CoreFrame',cuts,'Open fan-end intake slots with moulded ribs').Refine=False
    # Light guides sit outside the black wall, below the upper white cover.
    m.box('FrontStatusGuide','Blue status light guide above the glossy spine',287,.55,.65,(5,-117.9,80.1),'Controls',4,'ps5blue',.12)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=2
    m.checkpoint(2,'open_vents_and_original_interfaces','加工白罩光盘口、双侧防尘唇、首发前部 USB-A/C 和独立电源/出仓按钮开口、后部接口与贯通排风栅格；灯导和孔位为照片指导近似，接插件实体后续分轮补齐。')
    m.snapshot('02_front_review',normal=(.15,-1.5,.6))
    m.snapshot('02_rear_review',normal=(.15,1.5,.55))


STAGES[2]=stage02


def _usb_a(m,key,x,y,z,front=False,superspeed=True):
    normal=(0,-1,0) if front else (0,1,0);rot=g.rotation(normal,(0,0,1));direction=normal[1]
    outer=m.rr(14.4,6.7,12,(x,y,z),.4,rot)
    inner=m.rr(13.65,5.95,12.4,(x,y-direction*.2,z),.22,rot)
    group='FrontIO' if front else 'Ports'
    m.feature(key+'Shield','USB Type-A formed metal shield',outer.cut(inner),group,0,'metal')
    m.box(key+'RearCarrier','USB rear insulator',13.1,.85,5.5,(x,y+direction*.7,z-2.75),group,0,'black',.1,True)
    m.box(key+'Tongue','USB connector tongue',12.2,8.8,1.05,(x,y+direction*6.25,z-.5),group,0,'blue' if superspeed else 'black',.15)
    for i in range(4):
        m.box(key+'Contact'+str(i),'USB legacy contact',.65,4.6,.13,(x+(i-1.5)*2.5,y+direction*8,z+.62),group,0,'gold',.04,True)
    if superspeed:
        for i in range(5):m.box(key+'SuperSpeed'+str(i),'USB additional data contact',.44,1.5,.13,(x+(i-2)*2,y+direction*4.15,z+.62),group,0,'gold',.025,True)
    for i in range(9 if superspeed else 4):
        m.box(key+'Tail'+str(i),'USB board terminal',.28,2.5,.28,(x+(i-(4 if superspeed else 1.5))*1.05,y-direction*.9,z-2.85),group,0,'gold',.025,True)

    tails=[m.parts[key+'Tail'+str(i)].Shape for i in range(9 if superspeed else 4)]
    m.cut(key+'RearCarrier',tails,'Separate moulded terminal channels').Refine=False


def stage03(m):
    front=g.rotation((0,-1,0),(0,0,1));rear=g.rotation((0,1,0),(0,0,1))
    _usb_a(m,'FrontUSB',21,-104.8,58,True,False)
    for i,x in enumerate([-119,-86]):_usb_a(m,'RearUSB'+str(i),x,104.8,51.5)
    x,y,z=-5,-107.1,58
    outer=m.rr(9.2,3.6,10,(x,y,z),1.7,front);inner=m.rr(8.5,2.9,10.4,(x,y+.2,z),1.35,front)
    m.feature('USBCTube','Front reversible USB-C shield',outer.cut(inner),'FrontIO',0,'metal')
    m.feature('USBCInsulator','USB-C rounded rear carrier',m.rr(8.1,2.6,.75,(x,y-.175,z),1.25,front),'FrontIO',0,'black',True)
    m.box('USBCTongue','USB-C central tongue',6.9,7.0,.6,(x,y-5.2,z-.3),'FrontIO',0,'black',.2)
    for side in [-1,1]:
        for i in range(12):
            m.box('USBCContact'+str(side)+'_'+str(i),'USB-C independent contact',.24,4.8,.08,(x+(i-5.5)*.5,y-6,z+(.34 if side==1 else -.42)),'FrontIO',0,'gold',.02,True)
    # Eight separate spring contacts face the cable plug in the LAN mouth.
    x,y,z=-48,104.5,51.5
    outer=m.rr(16.0,14.0,12.4,(x,y,z),.4,rear);inner=m.rr(14.5,12.4,12.7,(x,y-.15,z),.25,rear)
    m.feature('LANShield','Ethernet folded shield',outer.cut(inner),'Ports',0,'metal')
    m.box('LANCarrier','Ethernet insulating rear wall',14.1,1.0,11.6,(x,y+.6,z-5.8),'Ports',0,'black',.15,True)
    for i in range(8):
        m.box('LANContact'+str(i),'Ethernet spring contact',.35,7.5,.23,(x+(i-3.5)*1.35,y+6.5,z-3.7),'Ports',0,'gold',.04,True)
    for i,dx in enumerate([-6.2,6.2]):m.box('LANLight'+str(i),'Ethernet status indicator',1.5,1,1.5,(x+dx,116.9,z+3.8),'Ports',1,'led',.2)
    # Tapered HDMI mouth and two staggered contact rows.
    x,y,z=0,104.2,51.5
    def hdmi(w,h,depth,offset=0):
        points=[(-w/2,-h/2+1.3),(-w/2+1.3,-h/2),(w/2-1.3,-h/2),(w/2,-h/2+1.3),(w/2,h/2),(-w/2,h/2)]
        vs=[V(a,b,0) for a,b in points];sh=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,0,depth));sh.Placement=App.Placement(V(x,y+offset,z),rear);return sh
    m.feature('HDMIShield','Original HDMI formed shield',hdmi(15.6,6.6,12.8).cut(hdmi(14.85,5.85,13.2,-.2)),'Ports',0,'metal')
    m.box('HDMICarrier','HDMI back insulator',12.0,.8,4.8,(x,y+.5,z-2.4),'Ports',0,'black',.1,True)
    m.box('HDMITongue','HDMI nineteen-contact tongue',11.7,8.7,.72,(x,y+7,z-.36),'Ports',0,'black',.16)
    for side,n in [(1,10),(-1,9)]:
        for i in range(n):m.box('HDMIContact'+str(side)+'_'+str(i),'HDMI independent contact',.28,6,.09,(x+(i-(n-1)/2)*1.1,y+7.2,z+(.4 if side==1 else -.49)),'Ports',0,'gold',.025,True)
    # Figure-eight AC inlet with independent pins and recessed insulating wells.
    x,y,z=76,105,51.5
    outer=m.rr(20,10.8,12,(x,y,z),3,rear)
    wells=[Part.makeCylinder(3.25,12.4,V(x+dx,y-.2,z),V(0,1,0)) for dx in [-4.2,4.2]]
    m.feature('ACInlet','Twin-well figure-eight AC insulator',outer.cut(Part.makeCompound(wells)),'Ports',0,'black')
    for i,dx in enumerate([-4.2,4.2]):
        m.cyl('ACPin'+str(i),'Independent AC inlet pin',.8,8.7,(x+dx,y+.7,z),'Ports',0,'metal',axis=(0,1,0))
        m.box('ACTerminal'+str(i),'AC internal blade terminal',1.8,3.5,.55,(x+dx,y-2.2,z-.275),'Ports',0,'metal',.08,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=3
    m.checkpoint(3,'separate_launch_connector_parts','补齐首发前部 USB 2.0 Type-A、24 接点 Type-C、后部双 USB 3.0、八接点网口、十九接点 HDMI 和双针 AC 入口；独立屏蔽、绝缘件、接点及尾端分件，局部尺寸为结构学习近似。')
    m.snapshot('03_front_ports',normal=(.15,-1.5,.5))
    m.snapshot('03_rear_ports',normal=(.1,1.8,.3))


STAGES[3]=stage03


def _underside_z(shape,x,y):
    hits=shape.section(Part.makeLine(V(x,y,-30),V(x,y,55)))
    assert hits.Vertexes,(x,y)
    return min(v.Point.z for v in hits.Vertexes)


def stage04(m):
    import Sketcher
    cx,cy=-8,35
    body=m.doc.addObject('PartDesign::Body','StandBaseBody')
    sk=body.newObject('Sketcher::SketchObject','StandBaseCircle');sk.addGeometry(Part.Circle(V(),V(0,0,1),72),False)
    sk.addConstraint(Sketcher.Constraint('Radius',0,72));sk.addConstraint(Sketcher.Constraint('Coincident',0,3,-1,1))
    pad=body.newObject('PartDesign::Pad','StandBasePad');pad.Profile=sk;pad.Length=8
    body.Placement.Base=V(cx,cy,-20);m.doc.recompute();sk.Visibility=False
    m.register(body,'StandBase','Stand',-8,'black')
    m.cut('StandBase',m.rr(19,9,7.2,(37,cy,-20.1),2),'Underside screw storage recess').Refine=False
    m.cut('StandBase',Part.makeCylinder(7.3,5,V(cx,cy,-15)),'Central rotor socket').Refine=False
    m.feature('StandRotor','Rotating upper Base cone',Part.makeCone(69,64,5,V(cx,cy,-11.8)),'Stand',-7,'black')
    m.cut('StandRotor',Part.makeCylinder(7.3,3.4,V(cx,cy,-12)),'Upper rotor pivot recess').Refine=False
    m.cyl('StandPivot','Base central pivot',7,5.8,(cx,cy,-14.8),'Stand',-7,'black',internal=True)
    m.ring('StandFootRing','Underside non-slip ring',65,61,1.2,(cx,cy,-21.3),'Stand',-9,'rubber')
    screw=Part.makeCylinder(3,.9,V(29.5,cy,-16),V(1,0,0)).fuse(Part.makeCylinder(1.4,9,V(30.35,cy,-16),V(1,0,0)))
    screw=screw.cut(Part.makeBox(.4,6.4,.6,V(29.4,cy-3.2,-16.3)))
    m.feature('StandStoredScrew','Coin-slot vertical-mount screw stored in Base',screw,'Stand',-8,'metal')
    m.box('StandSaddle','Horizontal-position upper saddle study',105,118,4.7,(cx,cy,-6.6),'Stand',-6,'black',20)
    lower=m.parts['LowerCover'].Shape
    for i,(x,y) in enumerate([(-48,-5),(32,-5),(-48,75),(32,75)]):
        # Fit the study supports below the actual saved curved cover, with visible rubber pads.
        z=min(_underside_z(lower,x+dx,y+dy) for dx in [-7,0,7] for dy in [-8,0,8])-.15
        assert z>1
        m.box('StandSupport'+str(i),'Contoured saddle support study',14,16,z-.4,(x,y,-1.7),'Stand',-6,'black',3)
        m.box('StandPad'+str(i),'Cover contact rubber pad',13.8,15.8,2,(x,y,z-2),'Stand',-5,'rubber',3)
    for i,x in enumerate([-45,29]):
        yz=[(88,-1.6),(121,9),(127,12),(127,20),(123.5,20),(123.5,14),(118,12),(88,2.4)]
        pts=[V(x-4,y,z) for y,z in yz]
        hook=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(8,0,0))
        m.feature('StandHook'+str(i),'Rear cover edge hook',hook,'Stand',-5,'black')
        tools=[]
        for dz in [-.15,0,.15]:
            sh=lower.copy();sh.translate(V(0,0,dz));tools.append(sh)
        m.cut('StandHook'+str(i),tools,'Static hook channel around the curved rear cover edge').Refine=False
    m.box('StandHookBridge','Crossbar between the rear edge hooks',66,3.3,3,(cx,125.25,17),'Stand',-5,'black',.3)
    m.cut('CoreFrame',Part.makeCylinder(3.5,7,V(-184,0,51),V(1,0,0)),'Vertical Base mounting screw aperture').Refine=False
    m.cyl('BaseHoleCap','Removable original Base mounting-hole cap',3.2,2.8,(-182.4,0,51),'Body',0,'black',axis=(1,0,0))
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=4
    m.checkpoint(4,'rotating_base_and_rear_hooks','依据原版官方指南建立独立圆形底座、旋转上部、支撑鞍座、橡胶接触层、后缘双钩及收纳螺丝；竖置螺孔盖单独建模。当前为横置静态学习装配，局部尺寸近似，不声称运动与承载验证。')
    m.snapshot('04_base_detail',assemblies=['Stand'],normal=(.4,-.7,1.8))
    m.snapshot('04_base_underside',assemblies=['Stand'],normal=(.3,-.4,-1.8))


STAGES[4]=stage04


def _fan_guard(cx,cy,z):
    rings=[]
    for ro,ri in [(63,59),(45,42),(28,25),(12,6)]:
        rings.append(Part.makeCylinder(ro,.7,V(cx,cy,z)).cut(Part.makeCylinder(ri,1,V(cx,cy,z-.1))))
    for angle in range(0,360,60):
        spoke=Part.makeBox(2.2,59,.7,V(cx-1.1,cy,z));spoke.rotate(V(cx,cy,z),V(0,0,1),angle);rings.append(spoke)
    for dx in [-46,46]:
        for dy in [-46,46]:rings.append(Part.makeBox(12,12,.7,V(cx+dx-6,cy+dy-6,z)))
    shape=rings[0].multiFuse(rings[1:]).removeSplitter()
    holes=[Part.makeCylinder(6,1,V(cx,cy,z-.1))]+[Part.makeCylinder(1.15,1,V(cx+dx,cy+dy,z-.1)) for dx in [-47,47] for dy in [-47,47]]
    return shape.cut(Part.makeCompound(holes))


def stage05(m):
    cx,cy=105,15
    # The fan and drive are open through the lower chassis rather than intersecting a solid floor.
    m.cut('CoreFrame',Part.makeCylinder(61.5,6,V(cx,cy,20)),'Lower dual-intake fan opening').Refine=False
    m.cut('CoreFrame',m.rr(142,143,8,(-100,-39,19),6),'Optical-drive well through the lower chassis floor').Refine=False
    m.native('InnerUpperFrame','Removable original internal upper cover',350,223,12,1.8,(-3,0,74),'Frame',4,'black')
    m.cut('InnerUpperFrame',Part.makeCylinder(61.5,4,V(cx,cy,73)),'Upper dual-intake fan opening').Refine=False
    m.cut('InnerUpperFrame',m.rr(118,25,4,(94,-86,73),2),'Original empty M.2 access opening').Refine=False
    dust=[(-12,63),(35,-68)]
    for x,y in dust:m.cut('InnerUpperFrame',Part.makeCylinder(6,4,V(x,y,73)),'Original dust-cleaning access study').Refine=False
    # Six spacers and blind screw bores are kept apart from the future board layers.
    for i,(x,y) in enumerate([(-161,-100),(-20,-100),(157,-102),(-161,99),(-20,99),(157,97)]):
        m.ring('FramePost'+str(i),'Hollow internal cover standoff',3.5,1.05,49.6,(x,y,24),'Frame',0,'black',internal=True)
        m.cut('InnerUpperFrame',Part.makeCylinder(1.05,4,V(x,y,73)),'Internal-cover fastener clearance').Refine=False
        m.screw('FrameScrew'+str(i),(x,y,76.2),'Frame',5,length=5.4,radius=1.9,axis=(0,0,-1))
    m.feature('UpperFanGuard','Concentric metal intake grille with six radial spokes',_fan_guard(cx,cy,76.1),'Cooling',5,'metal')
    for i,(dx,dy) in enumerate([(a,b) for a in [-47,47] for b in [-47,47]]):
        m.cut('InnerUpperFrame',Part.makeCylinder(1.05,4,V(cx+dx,cy+dy,73)),'Intake-grille screw clearance').Refine=False
        m.screw('FanGuardScrew'+str(i),(cx+dx,cy+dy,77.15),'Cooling',6,length=4.5,radius=1.9,axis=(0,0,-1))
    for i,(x,y) in enumerate(dust):
        cup=m.rr(19,18,2.8,(x,y,71),3).cut(Part.makeCylinder(6.2,3.2,V(x,y,70.8)))
        m.feature('DustAccessCollar'+str(i),'Dust-access internal collar study',cup,'Frame',3,'black',True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=5
    m.checkpoint(5,'inner_cover_and_open_air_paths','建立原版上部内罩、上下贯通风扇口、同心金属护网、六组支柱和固定螺丝、除尘口与空 M.2 检修开口；光驱仓向下贯通，后续布置板件、风扇与光驱。内部尺寸和固定关系为学习近似。')
    m.snapshot('05_inner_frame_review',assemblies=['Frame','Cooling','FrontIO','Ports'],normal=(.3,-.5,2))


STAGES[5]=stage05


def stage06(m):
    m.native('MainPCB','Original notched double-sided mainboard',315,214,3,1.6,(-12.5,3,52),'Mainboard',0,'pcb')
    m.cut('MainPCB',Part.makeCylinder(64.5,4,V(105,15,51)),'Motherboard crescent clearance around the dual-intake fan').Refine=False
    holes=[]
    for x,y in [(-161,-100),(-20,-100),(-161,99),(-20,99)]:holes.append(Part.makeCylinder(4,4,V(x,y,51)))
    # The two right frame posts fall outside this board's outer edge.
    for key in ['RearUSB0Shield','RearUSB1Shield','LANShield','HDMIShield','ACInlet']:
        b=m.parts[key].Shape.optimalBoundingBox(False,False)
        holes.append(Part.makeBox(b.XLength+.5,b.YLength+1,4,V(b.XMin-.25,b.YMin-.5,51)))
    m.cut('MainPCB',holes,'Board mounting and original rear connector clearances').Refine=False
    holes=[Part.makeCylinder(.45,3,V(x,y,51.5)) for x in range(-150,135,15) for y in [-98,103] if not any(abs(x-a)<6 for a in [-119,-86,-48,0,76])]
    m.cut('MainPCB',holes,'Representative plated edge-via drill pattern').Refine=False
    ax,ay=-60,25
    m.box('APUSubstrate','Custom APU organic package substrate',42,42,1.05,(ax,ay,50.8),'Mainboard',-1,'pcb',.4,True)
    m.box('APUDie','Exposed APU silicon die study',20,20,.62,(ax,ay,50.05),'Mainboard',-2,'screen',.15,True)
    foam=m.rr(52,52,1.75,(ax,ay,48.9),1).cut(m.rr(45,45,2,(ax,ay,48.8),.7))
    m.feature('LiquidMetalDam','Foam containment perimeter around the APU',foam,'Cooling',-2,'black',True)
    m.box('LiquidMetalInterface','Confined liquid-metal contact layer study',19.7,19.7,.1,(ax,ay,49.88),'Cooling',-2,'metal',.15,True)
    positions=[(-91,-10,45),(-61,-18,0),(-31,-10,-45),(-19,25,0),(-31,60,45),(-61,70,0),(-91,60,-45),(-103,25,0)]
    for i,(x,y,angle) in enumerate(positions):
        base=m.rr(15,13,.35,(x,y,53.78),.15);cap=m.rr(14.4,12.4,1.05,(x,y,54.23),.2)
        for sh in [base,cap]:sh.rotate(V(x,y,0),V(0,0,1),angle)
        m.feature('GDDRSubstrate'+str(i),'GDDR6 package substrate',base,'Mainboard',1,'pcb',True)
        m.feature('GDDR6_'+str(i),'One of eight original GDDR6 packages',cap,'Mainboard',1,'black',True)
    for side in [-1,1]:
        for i,y in enumerate([-50,-21,8]):
            z=49.85 if side<0 else 53.8
            m.box('NAND'+str(side)+'_'+str(i),'Original SSD NAND package: three per board side',18,13,1.8,(-144,y,z),'Mainboard',side,'black',.3,True)
    for key,label,x,y,w,d in [('Bridge','Main I/O bridge study',-32,-55,20,20),('SSDController','Custom SSD I/O controller study',-95,-65,17,17),('NetworkPHY','Ethernet PHY package study',-47,88,12,10),('Wireless','Wireless subsystem package study',123,-79,15,14),('USBController','USB interface controller study',2,-75,13,13)]:
        m.box(key,label,w,d,1.7,(x,y,53.85),'Mainboard',1,'black',.3,True)
    # Keep the primary mounting copper lands separate from the laminate holes.
    for i,(x,y) in enumerate([(-161,-100),(-20,-100),(-161,99),(-20,99)]):
        for side,z in [('Top',53.65),('Bottom',51.85)]:
            land=Part.makeCylinder(5.2,.1,V(x,y,z)).cut(Part.makeCylinder(4.1,.3,V(x,y,z-.1)))
            land=land.cut(Part.makeBox(400,20,1,V(-200,-123.8,z-.2)))
            m.feature('GroundLand'+side+str(i),'Board mounting copper annulus',land,'Mainboard',0,'gold',True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=6
    m.checkpoint(6,'notched_board_apu_and_memory','建立绕风扇开缺口的原生双面主板、下侧 APU 封装与液金围堰、上侧八枚 GDDR6、两侧各三枚 NAND、主要控制封装及独立接地环。器件外形和位置为首发拆解照片指导的近似，不构成电路或封装尺寸规范。')
    m.snapshot('06_mainboard_top',assemblies=['Mainboard'],normal=(0,0,1))
    m.snapshot('06_mainboard_bottom',assemblies=['Mainboard','Cooling'],exclude=['UpperFanGuard']+['FanGuardScrew'+str(i) for i in range(4)],normal=(0,0,-1))


STAGES[6]=stage06


def _smd(m,key,x,y,z,w=1.8,d=.9,h=.55,material='white'):
    m.box(key+'Body','Representative discrete component body',w*.62,d,h,(x,y,z),'Mainboard',0,material,.06,True)
    for i,dx in enumerate([-w*.41,w*.41]):
        m.box(key+'End'+str(i),'Discrete component plated termination',w*.18,d,h,(x+dx,y,z),'Mainboard',0,'metal',.03,True)


def _board_socket(m,key,label,x,y,width,count):
    body=m.rr(width,5,3.8,(x,y,53.85),.3)
    body=body.cut(m.rr(width-1.4,3.6,3.3,(x,y,54.6),.15))
    m.feature(key+'Housing',label,body,'Mainboard',1,'white',True)
    m.box(key+'Latch','Connector locking bar',width-1.5,.6,.8,(x,y+1.15,57.2),'Mainboard',1,'black',.08,True)
    for i in range(count):
        px=x+(i-(count-1)/2)*(width-3)/max(1,count-1)
        m.box(key+'Contact'+str(i),'Separate socket spring contact',.3,2,.18,(px,y-.25,55.1),'Mainboard',1,'gold',.03,True)


def stage07(m):
    # Population is representative: spacing and package sizes are photo-guided, not a circuit netlist.
    for i,y in enumerate([-65,-47,-29,-11,7,25,43,61,79]):
        m.box('VRMChoke'+str(i),'Encapsulated power inductor study',7.8,7.8,5.8,(-119,y,53.9),'Mainboard',1,'thermal',.5,True)
        for j,dx in enumerate([-3.15,3.15]):
            m.box('VRMFoot'+str(i)+'_'+str(j),'Inductor solder terminal',1.1,6,.18,(-119+dx,y,53.67),'Mainboard',1,'metal',.07,True)
        m.box('VRMPowerStage'+str(i),'Power switching package study',4.8,5,1.05,(-130,y,53.9),'Mainboard',1,'black',.2,True)
        for j in range(3):_smd(m,'VRMDiscrete'+str(i)+'_'+str(j),-130+(j-1)*2.8,y+5,53.85,w=1.7,d=.8,h=.55)
    for i,y in enumerate([-65,-47,-29,-11,7,43,61,79]):
        m.cyl('VRMCapacitor'+str(i),'Polymer decoupling capacitor',2.3,4.6,(-108,y,53.9),'Mainboard',1,'metal',internal=True)
        m.cyl('VRMCapSeal'+str(i),'Capacitor top seal',2,.12,(-108,y,58.55),'Mainboard',1,'black',internal=True)
    for i,x in enumerate([-77,-72,-67,-62,-57,-52,-47,-42]):
        for j,y in enumerate([7,11,39,43]):_smd(m,'APUDecouple'+str(i)+'_'+str(j),x,y,50.05)
    for i,(x,y) in enumerate([(-91,-10),(-61,-18),(-31,-10),(-19,25),(-31,60),(-61,70),(-91,60),(-103,25)]):
        # Small packages are offset beyond each memory substrate, including rotated packages.
        for j in range(3):_smd(m,'MemoryDiscrete'+str(i)+'_'+str(j),x+(j-1)*2.6,y+12,53.85,w=1.5,d=.7,h=.45,material='black')
    cx,cy=126,-99
    m.cyl('ClockHolderFloor','Coin-cell holder floor',10.3,.6,(cx,cy,53.85),'Mainboard',1,'black',internal=True)
    m.ring('ClockHolderWall','Open coin-cell retaining rim',10.3,9.7,3.5,(cx,cy,54.5),'Mainboard',1,'black',internal=True)
    m.cyl('ClockCell','Clock backup coin-cell study',9.5,2.8,(cx,cy,54.65),'Mainboard',1,'metal',internal=True)
    m.box('ClockClip','Positive battery retaining spring',2.4,9,.25,(cx,cy-4,57.6),'Mainboard',1,'metal',.1,True)
    m.box('ClockContact','Battery holder solder lug',2.4,3,.2,(cx+11.8,cy,53.75),'Mainboard',1,'metal',.1,True)
    _board_socket(m,'OpticalFFC','Optical-drive flex socket',-149,-81,20,18)
    _board_socket(m,'FrontFFC','Front interface flex socket',-62,-95,22,20)
    _board_socket(m,'FanSocket','Four-contact fan socket',37,-63,8,4)
    _board_socket(m,'PowerSocket','Internal low-voltage power socket',15,91,20,4)
    for i,(x,y) in enumerate([(-27,-78),(-88,93),(18,-15)]):
        m.box('ClockCrystal'+str(i),'Metal oscillator package study',4,2.4,.8,(x,y,53.85),'Mainboard',1,'metal',.4,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=7
    m.checkpoint(7,'board_power_and_connectors','补充主板供电电感及独立端子、功率封装、聚合物电容、APU 与显存附近的代表性无源器件、时钟电池座及四组独立连接器。数量与局部布局用于结构学习，不构成电路复刻或器件采购清单。')
    m.snapshot('07_mainboard_top',assemblies=['Mainboard'],normal=(.1,-.2,2))
    m.snapshot('07_mainboard_bottom',assemblies=['Mainboard'],normal=(0,0,-1))


STAGES[7]=stage07


def _fan_blade():
    import math
    def p(r,a):return V(r*math.cos(math.radians(a)),r*math.sin(math.radians(a)))
    a,b,c=p(18.4,0),p(36,9),p(56.8,22)
    d,e,f=p(56.8,23.4),p(36,10.4),p(18.4,1.4)
    wire=Part.Wire([Part.Arc(a,b,c).toShape(),Part.makeLine(c,d),Part.Arc(d,e,f).toShape(),Part.makeLine(f,a)])
    return Part.Face(wire).extrude(V(0,0,39))


def stage08(m):
    import math
    cx,cy=105,15
    housing=Part.makeCylinder(60.6,45,V(cx,cy,28)).cut(Part.makeCylinder(58.5,46,V(cx,cy,27.5)))
    pieces=[Part.makeCylinder(18,1.4,V(cx,cy,28))]
    for angle in [0,120,240]:
        spoke=Part.makeBox(3,60,1.4,V(cx-1.5,cy,28));spoke.rotate(V(cx,cy,0),V(0,0,1),angle);pieces.append(spoke)
    housing=housing.multiFuse(pieces).removeSplitter()
    m.feature('FanHousing','120 mm-class dual-intake fan frame and lower motor supports',housing,'Cooling',0,'metal',True)
    m.ring('FanMotorPCB','Annular fan motor driver PCB',17,2.6,.8,(cx,cy,30.1),'Cooling',0,'pcb',internal=True)
    for i,a in enumerate([0,120,240]):
        x=cx+11*math.cos(math.radians(a));y=cy+11*math.sin(math.radians(a))
        m.box('FanDriver'+str(i),'Fan driver package study',4,3,1,(x,y,31.1),'Cooling',0,'black',.2,True)
    m.cyl('FanShaft','Central fan spindle',2.4,39.7,(cx,cy,29.55),'Cooling',0,'metal',internal=True)
    for i,z in enumerate([35,59]):m.ring('FanBearing'+str(i),'Fan bearing sleeve',7.5,2.6,3.5,(cx,cy,z),'Cooling',0,'metal',internal=True)
    m.ring('FanStatorSpine','Laminated motor stator central spine',5,2.6,15,(cx,cy,41),'Cooling',0,'metal',internal=True)
    for i in range(9):
        angle=2*math.pi*i/9;n=V(math.cos(angle),math.sin(angle),0)
        tooth=Part.makeBox(5,1.2,1.2,V(cx+4.8,cy-.6,47-.6));tooth.rotate(V(cx,cy,0),V(0,0,1),360*i/9)
        # A short tooth joins the spine at its cylindrical surface without overlap.
        tooth=tooth.cut(Part.makeCylinder(5,16,V(cx,cy,40.5)))
        m.feature('FanStatorTooth'+str(i),'Radial stator tooth study',tooth,'Cooling',0,'metal',True)
        pos=V(cx,cy,47)+n*6
        coil=Part.makeCylinder(2.1,3,pos,n).cut(Part.makeCylinder(1,3.2,pos-n*.1,n))
        m.feature('FanCoil'+str(i),'Separate insulated motor winding envelope',coil,'Cooling',0,'copper',True)
    m.ring('FanRotorMagnet','Annular permanent-magnet rotor',13,11.8,23,(cx,cy,39),'Cooling',0,'black',internal=True)
    m.ring('FanRotorHub','Open rotor drum',18,14,36,(cx,cy,33),'Cooling',0,'black',internal=True)
    m.ring('FanRotorCap','Upper impeller hub cap',18.2,2.6,1.2,(cx,cy,69.15),'Cooling',0,'black',internal=True)
    # Twenty-three curved blades illustrate one launch fan variant, not every supplier variant.
    for i in range(23):
        blade=_fan_blade()
        blade.rotate(V(),V(0,0,1),360*i/23);blade.translate(V(cx,cy,31.5))
        m.feature('FanBlade'+str(i),'Curved impeller blade study',blade,'Cooling',0,'black',True)
    for i,(dx,dy) in enumerate([(a,b) for a in [-47,47] for b in [-47,47]]):
        m.ring('FanMountBush'+str(i),'Vibration-isolating fan mounting bush',3,1.1,4.2,(cx+dx,cy+dy,69.5),'Cooling',1,'rubber',internal=True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=8
    m.checkpoint(8,'dual_intake_fan_and_motor','建立 120 mm 级双面进风风扇、独立曲面叶片、下部电机支架、驱动板、轴承、转子磁环和九组示意定子线圈。叶片数量表示首发供应商变体之一；局部间隙及绕组截面为静态学习近似。')
    m.snapshot('08_fan_and_motor',assemblies=['Cooling'],exclude=['LiquidMetalDam','LiquidMetalInterface','UpperFanGuard']+['FanGuardScrew'+str(i) for i in range(4)],normal=(.4,-.7,1.7))


STAGES[8]=stage08


def _cooling_pipe(i,radius=2.2):
    import math
    x=-80+i*8;y=[107,92,87,82,74,66][i];z=45.3
    start=V(x,6,z);corner=V(x,y-6,z);end=V(x+6,y,z)
    middle=V(x+6-6/math.sqrt(2),y-6+6/math.sqrt(2),z)
    finish=V(153 if i<4 else 34,y,z)
    if i==0:
        # Lower the rear run below the original LAN and AC connector bodies.
        radius_bend=6;theta=math.acos(.625);rise_y=2*radius_bend*math.sin(theta)
        a=V(x,64,z);b=V(x,64+rise_y/2,z-2.25);c=V(x,64+rise_y,z-4.5)
        mid1=V(x,64+radius_bend*math.sin(theta/2),z-radius_bend*(1-math.cos(theta/2)))
        mid2=V(x,c.y-radius_bend*math.sin(theta/2),c.z+radius_bend*(1-math.cos(theta/2)))
        corner.z=end.z=middle.z=finish.z=z-4.5
        edges=[Part.makeLine(start,a),Part.Arc(a,mid1,b).toShape(),Part.Arc(b,mid2,c).toShape(),Part.makeLine(c,corner),Part.Arc(corner,middle,end).toShape(),Part.makeLine(end,finish)]
    else:edges=[Part.makeLine(start,corner),Part.Arc(corner,middle,end).toShape(),Part.makeLine(end,finish)]
    path=Part.Wire(edges)
    section=Part.Wire([Part.makeCircle(radius,start,V(0,1,0))])
    return path.makePipeShell([section],True,False)


def stage09(m):
    pipes=[];clear=[]
    for i in range(6):
        sh=_cooling_pipe(i);sh.check(True);pipes.append(sh);clear.append(_cooling_pipe(i,2.28))
        m.feature('HeatPipe'+str(i),'Sealed bent heat-pipe envelope study',sh,'Cooling',-2,'copper',True)
    m.native('CopperColdplate','APU copper contact plate with native base sketch',42,42,1,2.48,(-60,25,47.3),'Cooling',-2,'copper')
    m.cut('CopperColdplate',clear,'Heat-pipe seating channels below the APU').Refine=False
    posts=[Part.makeCylinder(3.75,25,V(x,y,24)) for x,y in [(-161,-100),(-20,-100),(157,-102),(-161,99),(-20,99),(157,97)]]
    ports=[]
    for key in ['RearUSB0Shield','RearUSB1Shield','LANShield','HDMIShield','ACInlet']:
        b=m.parts[key].Shape.optimalBoundingBox(False,False)
        ports.append(Part.makeBox(b.XLength+.6,b.YLength+.6,b.ZLength+.6,V(b.XMin-.3,b.YMin-.3,b.ZMin-.3)))
    tool=Part.makeCompound(clear+posts+ports)
    for bank,x0,x1,y0,depth in [('Main',-121,34,63,47),('Far',55,153,80,30)]:
        base=Part.makeBox(x1-x0,depth,.55,V(x0,y0,24.2)).cut(Part.makeCompound(posts))
        m.feature('FinRail'+bank,'Heat exchanger lower joining rail',base,'Cooling',-3,'metal',True)
        n=int((x1-x0)/2.15)
        for i in range(n):
            x=x0+.5+i*2.15
            fin=Part.makeBox(.32,depth,22,V(x,y0,24.85)).cut(tool)
            m.feature('CoolingFin'+bank+str(i),'Separate heat exchanger lamella',fin,'Cooling',-2,'metal',True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=9
    m.checkpoint(9,'six_bent_heatpipes_and_fin_banks','加入带热管座槽的原生铜接触板、六根连续弯曲热管和两组独立散热鳍片；热管与支柱、后接口均保留独立间隙。路径和鳍片尺寸为拆解照片指导的结构近似，不表示热性能或流体计算结果。')
    m.snapshot('09_cooling_overview',assemblies=['Cooling'],exclude=['UpperFanGuard']+['FanGuardScrew'+str(i) for i in range(4)],normal=(.3,-.7,1.5))
    m.snapshot('09_heatpipes_underside',assemblies=['Cooling'],exclude=['UpperFanGuard']+['FanGuardScrew'+str(i) for i in range(4)],normal=(.2,-.5,-1.5))


STAGES[9]=stage09


def _polygon_shape(points,z,depth):
    vertices=[V(x,y,z) for x,y in points]
    return Part.Face(Part.makePolygon(vertices+[vertices[0]])).extrude(V(0,0,depth))


def _native_polygon(m,key,label,points,z,depth,assembly,layer,material):
    body=m.doc.addObject('PartDesign::Body',key+'Body')
    sk=m.doc.addObject('Sketcher::SketchObject',key+'Sketch');body.addObject(sk)
    for a,b in zip(points,points[1:]+points[:1]):sk.addGeometry(Part.LineSegment(V(*a),V(*b)),False)
    sk.Placement.Base.z=z
    pad=body.newObject('PartDesign::Pad',key+'Pad');pad.Profile=sk;pad.Length=depth
    m.doc.recompute();sk.Visibility=False;pad.Visibility=False;body.Label=label
    return m.register(body,key,assembly,layer,material,True)


def stage10(m):
    outer=[(-174,37),(34,37),(34,61),(-124,61),(-124,110),(-174,110)]
    inner=[(-172.8,38.2),(32.8,38.2),(32.8,59.8),(-125.2,59.8),(-125.2,108.8),(-172.8,108.8)]
    board=[(-171.3,39.7),(31.3,39.7),(31.3,58.3),(-126.7,58.3),(-126.7,107.3),(-171.3,107.3)]
    _native_polygon(m,'PowerHousing','Boot-shaped internal power module housing',outer,24.2,17.3,'Power',-3,'black')
    m.cut('PowerHousing',_polygon_shape(inner,25.4,17.3),'Open power module interior').Refine=False
    vents=[Part.makeBox(2.4,4,8,V(x,108,30)) for x in range(-170,-128,6)]
    m.cut('PowerHousing',vents,'Power enclosure rear ventilation').Refine=False
    _native_polygon(m,'PowerLid','Separate boot-shaped power module lid',outer,41.65,.7,'Power',-1,'black')
    slots=[Part.makeBox(1.7,12,1.2,V(x,43,41.4)) for x in range(-165,25,7)]
    m.cut('PowerLid',slots,'Power lid cooling slots').Refine=False
    _native_polygon(m,'PowerPCB','Native boot-shaped power conversion PCB',board,27.2,1.2,'Power',-2,'pcb')
    # Preserve clearance for the console's long rear-left chassis pillar.
    clearance=Part.makeCylinder(3.8,20,V(-161,99,23.5))
    for key in ['PowerHousing','PowerLid','PowerPCB']:m.cut(key,clearance,'Main chassis pillar through the power module').Refine=False
    mounts=[(-168,45),(-168,104),(-131,67),(27,54),(-75,54)]
    for i,(x,y) in enumerate(mounts):
        m.ring('PowerPost'+str(i),'Internal power module screw post',2.3,1,14.4,(x,y,25.6),'Power',-2,'black',internal=True)
        m.cut('PowerPCB',Part.makeCylinder(2.6,2,V(x,y,26.9)),'PCB pillar clearance').Refine=False
        m.cut('PowerLid',Part.makeCylinder(1,1.2,V(x,y,41.4)),'Power lid screw clearance').Refine=False
        m.screw('PowerScrew'+str(i),(x,y,42.7),'Power',-1,length=4,radius=1.7,axis=(0,0,-1))
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=10
    m.checkpoint(10,'boot_shaped_power_module_structure','建立独立靴形电源外壳、可拆通风盖板、原生草图电路板及固定柱；保留穿过该模块的主机支柱间隙。模块外形和内部层高为学习近似，后续加入变压器、电容和接线。')
    m.snapshot('10_power_structure',assemblies=['Power'],exclude=['PowerLid']+['PowerScrew'+str(i) for i in range(5)],normal=(.3,-.6,1.7))


STAGES[10]=stage10


def _power_cap(m,key,x,y,r,h):
    m.cyl(key,'Power module electrolytic capacitor',r,h,(x,y,28.7),'Power',-2,'black',internal=True)
    m.cyl(key+'Top','Capacitor pressure vent lid',r-.3,.15,(x,y,28.75+h),'Power',-2,'metal',internal=True)
    for j,dx in enumerate([-r*.45,r*.45]):
        m.cyl(key+'Lead'+str(j),'Separate capacitor lead',.32,2,(x+dx,y,26.6),'Power',-2,'metal',internal=True)
        m.cut('PowerPCB',Part.makeCylinder(.45,2,V(x+dx,y,26.8)),'Capacitor lead drilled clearance').Refine=False


def stage11(m):
    import math
    for i,x in enumerate([-160,-144]):_power_cap(m,'BulkCap'+str(i),x,79,5.6,10)
    for i,x in enumerate([-59,-48,-37]):_power_cap(m,'OutputCap'+str(i),x,49,3.5,8)
    m.box('MainsFilterCap','Mains filter capacitor package study',16,8,8,(-157,65,28.7),'Power',-2,'blue',.5,True)
    m.box('BridgeRectifier','Power bridge rectifier package',12,8,4,(-140,49,28.7),'Power',-2,'black',.4,True)
    m.cyl('MainsFuse','Cartridge fuse envelope',1.8,12,(-166,50,31.2),'Power',-2,'white',axis=(1,0,0),internal=True)
    for i,x in enumerate([-168,-154]):m.cyl('FuseCap'+str(i),'Cartridge fuse end cap',2,2,(x,50,31.2),'Power',-2,'metal',axis=(1,0,0),internal=True)
    m.ring('PowerChokeCore','Toroidal input choke core',6,3.5,4,(-117,49,31),'Power',-2,'thermal',internal=True)
    for i in range(12):
        a=math.radians(i*30);pos=V(-117+4.75*math.cos(a),49+4.75*math.sin(a),33);axis=V(-math.sin(a),math.cos(a),0)
        m.feature('PowerChokeTurn'+str(i),'Representative insulated choke winding loop',Part.makeTorus(2.65,.18,pos,axis),'Power',-2,'copper',True)
    cx,cy=-90,49
    core=m.rr(20,16,10,(cx,cy,28.7),.5).cut(m.rr(16.4,12.4,10,(cx,cy,29.5),.2))
    core=core.fuse(m.rr(5,5,10,(cx,cy,28.7),.2)).removeSplitter()
    m.feature('PowerTransformerCore','Transformer outer ferrite frame and centre leg',core,'Power',-2,'black',True)
    for i,z in enumerate([29.6,37.9]):
        bobbin=m.rr(16.1,12.1,.3,(cx,cy,z),.25).cut(m.rr(5.6,5.6,.5,(cx,cy,z-.1),.2))
        m.feature('TransformerBobbin'+str(i),'Transformer bobbin cheek',bobbin,'Power',-2,'white',True)
    winding=m.rr(15.8,11.8,7.7,(cx,cy,30),.4).cut(m.rr(6,6,8,(cx,cy,29.9),.3))
    m.feature('TransformerWinding','Insulated transformer winding envelope',winding,'Power',-2,'gold',True)
    m.box('PrimaryHeatsink','Primary switching device heat spreader',1.2,16,10,(-72,49,28.7),'Power',-2,'metal',.15,True)
    m.box('PrimarySwitch','Primary switching transistor study',3,7,3,(-67,49,28.7),'Power',-2,'black',.3,True)
    m.box('SecondaryHeatsink','Secondary rectifier heat spreader',1.4,15,10,(-20,49,28.7),'Power',-2,'metal',.15,True)
    m.box('SecondaryRectifier','Secondary rectifier package study',4,7,3,(-16,49,28.7),'Power',-2,'black',.3,True)
    for key,x,y,w in [('MainsInput',-145,94,12),('PowerOutput',15,49,16)]:
        sh=m.rr(w,7,5,(x,y,28.7),.4).cut(m.rr(w-1.8,5.2,4,(x,y,30),.2))
        m.feature(key+'Housing','Two-contact internal power connector',sh,'Power',-2,'white',True)
        for j,dx in enumerate([-w*.23,w*.23]):m.box(key+'Blade'+str(j),'Separate power connector blade',1,2.4,2.7,(x+dx,y,30.15),'Power',-2,'metal',.08,True)
    for i,(x,y) in enumerate([(-130,94),(-155,91),(-128,49),(-105,49),(-7,49)]):
        m.box('PowerControlIC'+str(i),'Representative power regulation package',4,3,1.2,(x,y,28.7),'Power',-2,'black',.2,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=11
    m.checkpoint(11,'power_conversion_components','电源模块加入独立电容及引线、保险管和端帽、整流与开关封装、环形磁芯及示意线圈、分离的变压器磁芯/骨架/绕组、散热片和板端接插件。结构用于拆解学习，不是可制造的市电电路设计。')
    m.snapshot('11_power_internals',assemblies=['Power'],exclude=['PowerLid']+['PowerScrew'+str(i) for i in range(5)],normal=(.3,-.6,1.7))


STAGES[11]=stage11


def _drive_lower_relief():
    points=[V(-126,y,z) for y,z in [(-113,-10),(-88,-10),(-88,17.5),(-113,28)]]
    return Part.Face(Part.makePolygon(points+[points[0]])).extrude(V(100,0,0))


def stage12(m):
    m.native('DriveHousing','Slot-loading optical drive lower metal enclosure',138,140,3,20,(-100,-39,17.5),'Optical',-3,'metal')
    m.cut('DriveHousing',m.rr(135.6,137.6,20,(-100,-39,18.4),2),'Open optical mechanism cavity').Refine=False
    m.cut('DriveHousing',Part.makeBox(132,5,4.8,V(-166,-111,24)),'Clear disc path behind the front brushes').Refine=False
    m.native('DriveTopCover','Removable stamped optical drive top cover',137.8,139.8,2.8,.65,(-100,-39,37.7),'Optical',1,'metal')
    m.cut('DriveTopCover',Part.makeCylinder(13,1.2,V(-100,-30,37.4)),'Magnetic clamp cup opening').Refine=False
    for key in ['DriveHousing','DriveTopCover']:
        m.cut(key,Part.makeCylinder(3.8,23,V(-161,-100,16)),'Front chassis pillar clearance through the optical bay').Refine=False
    liner=m.rr(132,132,2,(-100,-39,19),2).cut(m.rr(118,116,3,(-100,-39,18.5),1.3))
    holes=[Part.makeCylinder(r,3,V(x,y,18.5)) for x,y,r in [(-154,-72,3.8),(-46,-72,3.8),(-154,18,3.8),(-46,18,3.8),(-164,-89,2.2),(-36,-103,2.2),(-164,25,2.2),(-36,25,2.2)]]
    liner=liner.cut(Part.makeCompound(holes))
    m.feature('DriveLiner','Separate internal polymer perimeter frame',liner,'Optical',-2,'black',True)
    for i,(x,y) in enumerate([(-154,-72),(-46,-72),(-154,18),(-46,18)]):
        m.ring('DriveMountPost'+str(i),'Optical deck lower fixing post',2.1,1.05,1.9,(x,y,18.6),'Optical',-2,'metal',internal=True)
        m.ring('DriveIsolator'+str(i),'Optical deck vibration isolator',3.6,1.2,3.4,(x,y,20.7),'Optical',-1,'blue',internal=True)
        m.screw('DriveMountScrew'+str(i),(x,y,24.6),'Optical',0,length=3.5,radius=2,axis=(0,0,-1))
    for i,(x,y) in enumerate([(-164,-89),(-36,-103),(-164,25),(-36,25)]):
        for key in ['DriveHousing','DriveTopCover']:
            m.cut(key,Part.makeCylinder(1.05,23,V(x,y,16)),'Optical enclosure fastener clearance').Refine=False
        m.ring('DriveCoverPost'+str(i),'Optical enclosure cover standoff',2,1.05,17.9,(x,y,19),'Optical',-1,'metal',internal=True)
        m.screw('DriveCoverScrew'+str(i),(x,y,38.8),'Optical',1,length=4.8,radius=1.8,axis=(0,0,-1))
    for key in ['DriveHousing','DriveLiner','DriveCoverPost1']:
        m.cut(key,_drive_lower_relief(),'Raised front-right underside clearance above the curved white cover').Refine=False
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=12
    m.checkpoint(12,'slot_drive_enclosure_and_isolators','建立原版机身家族吸入式光驱的原生金属下壳、可拆上盖、光盘入口、独立塑料框架、减振件及固定柱；夹盘、读取和进出盘机构将在后续轮次补齐。局部尺寸为学习近似。')
    m.snapshot('12_optical_enclosure',assemblies=['Optical'],exclude=['DriveTopCover']+['DriveCoverScrew'+str(i) for i in range(4)],normal=(.3,-.6,1.8))


STAGES[12]=stage12


def stage13(m):
    points=[(-154,-72),(-145,-80),(-65,-80),(-46,-72),(-46,18),(-54,24),(-144,24),(-154,18)]
    _native_polygon(m,'OpticalDeck','Floating optical mechanism chassis',points,21.5,1.2,'Optical',-1,'black')
    cuts=[Part.makeCylinder(13.8,2,V(-100,-30,21.2)),m.rr(44,42,2,(-100,2,21.2),1)]
    cuts += [Part.makeCylinder(3.8,2,V(x,y,21.2)) for x,y in [(-154,-72),(-46,-72),(-154,18),(-46,18)]]
    m.cut('OpticalDeck',cuts,'Spindle, pickup travel and isolator clearances').Refine=False
    cx,cy=-100,-30
    m.ring('SpindleMotorCan','Optical spindle motor steel can',9.6,8.3,4.2,(cx,cy,19),'Optical',-2,'metal',internal=True)
    m.ring('SpindleMotorPCB','Spindle motor annular circuit board',8,1.5,.5,(cx,cy,19.2),'Optical',-2,'pcb',internal=True)
    m.box('SpindleDriver','Spindle commutation package',4,3,.6,(cx+4,cy,19.8),'Optical',-2,'black',.2,True)
    m.ring('SpindleStator','Spindle motor stator envelope',5.8,1.5,1.1,(cx,cy,20.6),'Optical',-2,'copper',internal=True)
    m.ring('SpindleRotor','Spindle permanent-magnet rotor',7.8,1.5,.9,(cx,cy,22),'Optical',-2,'black',internal=True)
    m.cyl('SpindleAxle','Optical spindle shaft',1.2,6.6,(cx,cy,19),'Optical',-1,'metal',internal=True)
    m.ring('SpindleFlange','Spindle upper motor flange',12.4,1.5,.5,(cx,cy,23.4),'Optical',-1,'metal',internal=True)
    m.ring('SpindleHub','Disc support hub',3.4,1.5,1.65,(cx,cy,23.95),'Optical',0,'black',internal=True)
    m.ring('SpindlePlatter','Disc support turntable',10.5,1.5,.5,(cx,cy,25.75),'Optical',0,'black',internal=True)
    m.cyl('DiscClamp','Magnetic disc clamp puck',11,1.2,(cx,cy,27.6),'Optical',1,'black',internal=True)
    m.cyl('ClampStem','Upper clamp centre stem',3.2,8.5,(cx,cy,28.9),'Optical',1,'metal',internal=True)
    m.ring('ClampCup','Floating clamp cup wall',12.8,11.8,8,(cx,cy,29.4),'Optical',1,'white',internal=True)
    m.ring('ClampRetainer','Clamp retaining washer below the top cover',13.5,3.4,.15,(cx,cy,37.5),'Optical',1,'metal',internal=True)
    m.ring('ClampTopRing','Clamp cup ring inside the cover opening',12.7,3.4,.4,(cx,cy,37.8),'Optical',1,'white',internal=True)
    for i,x in enumerate([-116,-84]):
        m.cyl('PickupRail'+str(i),'Optical pickup polished guide rail',1,40,(x,-15,24.3),'Optical',0,'metal',axis=(0,1,0),internal=True)
        for j,y in enumerate([-14,24]):
            block=m.rr(6,3,4,(x,y,22.9),.3).cut(Part.makeCylinder(1.2,5,V(x,y-2.5,24.3),V(0,1,0)))
            m.feature('PickupRailSupport'+str(i)+'_'+str(j),'Pickup rail support block',block,'Optical',0,'black',True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=13
    m.checkpoint(13,'floating_deck_spindle_and_clamp','光驱加入带开窗的原生浮动机构架、分离的主轴电机壳/电路板/定转子/轴、托盘轮毂、磁力夹盘及双导轨。模型保持空盘状态，媒体通道与夹持间距为近似静态表达。')
    m.snapshot('13_spindle_and_deck',assemblies=['Optical'],exclude=['DriveTopCover','DriveHousing']+['DriveCoverScrew'+str(i) for i in range(4)],normal=(.3,-.6,1.7))


STAGES[13]=stage13


def stage14(m):
    cx,cy=-100,7
    body=m.rr(36,16,3,(cx,cy,22.8),1)
    holes=[Part.makeCylinder(1.2,18,V(x,cy-9,24.3),V(0,1,0)) for x in [-116,-84]]
    holes.append(Part.makeCylinder(4.2,4,V(cx,cy,22.5)))
    holes.extend([m.rr(3.4,8.4,2.2,(x,cy,24),.3) for x in [cx-7,cx+7]])
    m.feature('PickupCarriage','Optical pickup carriage with guide bores and focus pockets',body.cut(Part.makeCompound(holes)),'Optical',0,'black',True)
    m.ring('ObjectiveBarrel','Objective lens focusing barrel',4,2.7,3.1,(cx,cy,22.9),'Optical',0,'metal',internal=True)
    lens=Part.makeCylinder(2.2,.9,V(cx,cy,24.5))
    cap=Part.makeSphere(2.5,V(cx,cy,23.6)).common(Part.makeBox(6,6,1,V(cx-3,cy-3,25.399)))
    m.feature('ObjectiveLens','Convex objective lens study',lens.fuse(cap).removeSplitter(),'Optical',0,'screen',True)
    for i,x in enumerate([cx-7,cx+7]):
        coil=m.rr(3,8,1.4,(x,cy,24.2),.25).cut(m.rr(1.6,6,1.8,(x,cy,24),.2))
        m.feature('FocusCoil'+str(i),'Objective focusing voice-coil envelope',coil,'Optical',0,'copper',True)
        m.box('FocusMagnet'+str(i),'Focusing actuator magnet',1.2,5.6,1,(x,cy,24.4),'Optical',0,'black',.1,True)
    housing=m.rr(12,10,3,(cx,cy,19.6),.5).cut(m.rr(10,8,3,(cx,cy,20.3),.3))
    m.feature('OpticalBlock','Lower optical block housing',housing,'Optical',-1,'metal',True)
    splitter=m.rr(2,2,.3,(cx,cy,21.1),.05);splitter.rotate(V(cx,cy,21.25),V(0,1,0),45)
    m.feature('BeamSplitter','Angled optical splitter plate study',splitter,'Optical',-1,'screen',True)
    m.cyl('LaserPackage','Laser diode package envelope',1.4,3,(-110,cy,21.2),'Optical',-1,'metal',axis=(1,0,0),internal=True)
    m.box('Photodiode','Optical detector package',3,3,1.2,(-92,cy,20.4),'Optical',-1,'black',.2,True)
    sx=-132
    m.cut('OpticalDeck',Part.makeCylinder(3.3,9,V(sx,20.5,24.3),V(0,1,0)),'Pickup feed motor rear clearance').Refine=False
    m.ring('PickupMotorCan','Pickup translation motor housing',3,2.2,7,(sx,21,24.3),'Optical',0,'metal',axis=(0,1,0),internal=True)
    m.cyl('PickupMotorRotor','Pickup translation motor rotor',1.9,5.8,(sx,21.5,24.3),'Optical',0,'copper',axis=(0,1,0),internal=True)
    m.cyl('PickupLeadCore','Pickup feed screw shaft',.65,38,(sx,-18,24.3),'Optical',0,'metal',axis=(0,1,0),internal=True)
    from .atari2600 import _helical_spring
    thread=_helical_spring(.9,1.2,38,.12)
    thread.rotate(V(),V(1,0,0),-90);thread.translate(V(sx,-18,24.3))
    m.feature('PickupLeadThread','Continuous helical pickup feed thread',thread,'Optical',0,'metal',True)
    nut=m.rr(5,6,3,(sx,cy,22.8),.3).cut(Part.makeCylinder(1.2,8,V(sx,cy-4,24.3),V(0,1,0)))
    m.feature('PickupFollower','Feed-screw follower nut study',nut,'Optical',0,'white',True)
    m.box('PickupFollowerArm','Link between feed nut and carriage',11.1,3,.5,(-123.75,cy,25.15),'Optical',0,'white',.2,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=14
    m.checkpoint(14,'optical_pickup_and_helical_feed','补齐光学头滑架、导孔、聚焦线圈与磁体、凸透镜、下部光学块、激光封装与检测器，并建立独立电机、连续螺旋进给丝杆和随动螺母。光学路径和传动间隙为拆解结构示意，不作光路或运动性能校准。')
    m.snapshot('14_optical_pickup',assemblies=['Optical'],exclude=['DriveTopCover','DriveHousing']+['DriveCoverScrew'+str(i) for i in range(4)],normal=(.3,-.6,1.7))


STAGES[14]=stage14
