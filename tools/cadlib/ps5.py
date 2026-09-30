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


def stage15(m):
    from .ps1 import _gear
    m.cut('OpticalDeck',Part.makeCylinder(4.8,10,V(-151,-62,18.4)),'Loading motor clearance in the floating deck').Refine=False
    m.ring('LoadingMotorCan','Optical loading motor steel housing',4.5,3.7,8,(-151,-62,18.8),'Optical',-1,'metal',internal=True)
    m.cyl('LoadingMotorRotor','Loading motor rotor envelope',3.3,6.6,(-151,-62,19.4),'Optical',-1,'copper',internal=True)
    m.cyl('LoadingMotorShaft','Loading motor output shaft',.65,1.5,(-151,-62,27),'Optical',0,'metal',internal=True)
    gears=[(-151,-62,2,2.5,12),(-151,-71,5.8,6.3,26),(-151,-84,5.8,6.3,26),(-156,-93,1.9,2.4,12)]
    for i,(x,y,root,outer,n) in enumerate(gears):
        sh=_gear(m,x,y,27.4,root,outer,1.3,n).cut(Part.makeCylinder(.85,2,V(x,y,27.1)))
        m.feature('LoadingGear'+str(i),'Separate schematic loading spur gear',sh,'Optical',0,'white',True)
        if i:m.cyl('LoadingGearAxle'+str(i),'Loading gear pivot',.65,1.9 if i==3 else 3.5,(x,y,27 if i==3 else 25.4),'Optical',0,'metal',internal=True)
    m.cyl('FeedRollerShaft','Lower optical feed roller shaft',.7,112,(-157,-93,23.35),'Optical',0,'metal',axis=(1,0,0),internal=True)
    for i,x in enumerate([-142,-128,-114,-100,-86,-72]):
        m.ring('FeedRoller'+str(i),'Segmented rubber disc-loading roller',2.8,.9,10,(x,-93,23.35),'Optical',0,'rubber',axis=(1,0,0),internal=True)
    for i,x in enumerate([-154.5,-48.5]):
        block=Part.makeBox(3,7,6,V(x,-96.5,20.5)).cut(Part.makeCylinder(.95,4,V(x-.5,-93,23.35),V(1,0,0)))
        m.feature('FeedBearing'+str(i),'Lower roller bearing block',block,'Optical',0,'white',True)
    sh=_gear(m,0,0,0,2.6,3.2,1.5,16).cut(Part.makeCylinder(.95,2,V(0,0,-.2)))
    sh.rotate(V(),V(0,1,0),90);sh.translate(V(-156.5,-93,23.35))
    m.feature('FeedTransferGear','Orthogonal roller transfer gear study',sh,'Optical',0,'white',True)
    m.cyl('PinchShaft','Upper disc pinch-roller shaft',.5,98,(-149,-93,28.25),'Optical',0,'metal',axis=(1,0,0),internal=True)
    for i,x in enumerate([-143,-119,-95,-71]):
        m.ring('PinchRoller'+str(i),'Upper disc pinch roller',1.8,.7,12,(x,-93,28.25),'Optical',0,'rubber',axis=(1,0,0),internal=True)
    for i,x in enumerate([-148,-52]):
        arm=m.rr(4,6,9.9,(x,-93,20.5),.4)
        if i==0:arm=arm.cut(Part.makeCylinder(6.5,1.8,V(-151,-84,27.2)))
        cuts=[Part.makeCylinder(r,5,V(x-2.5,-93,z),V(1,0,0)) for r,z in [(1,23.35),(.75,28.25)]]
        m.feature('PinchSupport'+str(i),'Pinch roller support arm',arm.cut(Part.makeCompound(cuts)),'Optical',0,'black',True)
    m.box('PinchBridge','Upper pinch-roller support bridge',104,4,.7,(-100,-93,30.5),'Optical',0,'metal',.4,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=15
    m.checkpoint(15,'slot_loading_motor_and_rollers','加入吸入/退出电机、独立齿轮和轴、分段橡胶进盘辊、上压辊及支架；齿形和传动间隙仅为静态结构示意，不声称运动学啮合验证。')
    m.snapshot('15_loading_mechanism',assemblies=['Optical'],exclude=['DriveTopCover','DriveHousing']+['DriveCoverScrew'+str(i) for i in range(4)],normal=(.3,-.6,1.7))


STAGES[15]=stage15


def stage16(m):
    m.native('DriveControllerPCB','Optical-drive controller PCB',84,18,1,.8,(-100,-52,18.6),'Optical',-2,'pcb')
    for i,(x,y) in enumerate([(-137,-58),(-137,-46),(-63,-58),(-63,-46)]):
        m.cut('DriveControllerPCB',Part.makeCylinder(2,2,V(x,y,18.1)),'Controller board fixing post clearance').Refine=False
        m.ring('DrivePCBPost'+str(i),'Controller board screw post',1.8,.9,2,(x,y,18.5),'Optical',-2,'white',internal=True)
        m.screw('DrivePCBScrew'+str(i),(x,y,21.25),'Optical',-1,length=2.2,radius=1.7,axis=(0,0,-1))
    for key,x,w,d in [('DriveController',-104,12,9),('DriveRAM',-82,9,8),('DriveMotorIC',-125,6,6),('DriveInterfaceIC',-67,6,6)]:
        m.box(key,'Optical-drive electronic package study',w,d,1.3,(x,-52,19.6),'Optical',-1,'black',.25,True)
    for i,x in enumerate([-130,-124,-118,-112,-92,-86,-80,-74]):
        for j,y in enumerate([-59.7,-44.4]):
            m.box('DriveDiscrete'+str(i)+'_'+str(j),'Representative drive-board discrete',1.4,.7,.45,(x,y,19.6),'Optical',-1,'white',.05,True)
    sh=m.rr(12,3,1.3,(-101,-58.5,19.6),.2).cut(m.rr(10.6,1.8,1,(-101,-58.5,20.1),.1))
    m.feature('DriveFlexSocket','Optical controller flex connector',sh,'Optical',-1,'white',True)
    for i in range(12):m.box('DriveFlexContact'+str(i),'Drive flex connector contact',.25,1.2,.12,(-105.4+i*.8,-58.5,20.35),'Optical',-1,'gold',.02,True)
    # A cam plate and limit switch show the loading sequence's independent mechanical pieces.
    cam=Part.makeCylinder(7,1.2,V(-151,-47,23.3)).cut(Part.makeCylinder(1,2,V(-151,-47,23)))
    cam=cam.cut(m.rr(2,6,2,(-148,-47,23),.6))
    m.feature('LoadingCam','Slotted loading sequence cam study',cam,'Optical',0,'white',True)
    m.cyl('LoadingCamAxle','Loading cam pivot',.75,2.4,(-151,-47,23),'Optical',0,'metal',internal=True)
    m.box('CamFollowerArm','Loading cam follower link',12,3,.5,(-140,-47,24.7),'Optical',0,'white',.4,True)
    m.ring('CamFollowerPivot','Follower retaining washer',2,1,.5,(-135,-47,25.3),'Optical',0,'metal',internal=True)
    m.box('DriveLimitPCB','Optical mechanism limit-switch board',10,7,.7,(-148,-39,18.6),'Optical',-2,'pcb',.3,True)
    m.box('DriveLimitSwitch','Loading position switch',4,3,1.5,(-148,-39,19.5),'Optical',-1,'black',.3,True)
    m.box('DriveSensorPCB','Disc-entry detector board',6,5,.8,(-147,-99,22.9),'Optical',0,'pcb',.3,True)
    sensor=m.rr(3,5,4,(-147,-99,24),.2).cut(Part.makeBox(1.6,6,1.9,V(-147.8,-102,25.5)))
    m.feature('DiscEntrySensor','Disc-entry optical interrupter housing',sensor,'Optical',0,'black',True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=16
    m.checkpoint(16,'drive_electronics_cam_and_detection','光驱加入原生控制板、主要芯片、连接器及触点、加载顺序凸轮、随动连杆、限位开关和入口光电检测件。逻辑电路与控制时序为结构示意，排线与线束将在整机接线轮次补齐。')
    m.snapshot('16_optical_complete_mechanisms',assemblies=['Optical'],exclude=['DriveTopCover','DriveHousing']+['DriveCoverScrew'+str(i) for i in range(4)],normal=(.3,-.6,1.7))


STAGES[16]=stage16


def stage17(m):
    upper_z,lower_z=56.55,48.1
    m.native('UpperEMIShield','Upper stamped motherboard shield',313,212,3,.5,(-12.5,3,upper_z),'Shielding',2,'metal')
    m.native('LowerEMIShield','Lower stamped motherboard shield',313,212,3,.4,(-12.5,3,lower_z),'Shielding',-2,'metal')
    holes=[Part.makeCylinder(65,12,V(105,15,47))]
    holes += [Part.makeCylinder(4,12,V(x,y,47)) for x,y in [(-161,-100),(-20,-100),(-161,99),(-20,99)]]
    for key in ['RearUSB0Shield','RearUSB1Shield','LANShield','HDMIShield','ACInlet']:
        b=m.parts[key].Shape.optimalBoundingBox(False,False)
        holes.append(Part.makeBox(b.XLength+.8,b.YLength+.8,12,V(b.XMin-.4,b.YMin-.4,47)))
    for key in ['UpperEMIShield','LowerEMIShield']:m.cut(key,holes,'Shield apertures around fan, pillars and rear connectors').Refine=False
    upper=[m.rr(34,165,2,(-120,8,56),2),Part.makeCylinder(10.7,2,V(126,-99,56))]
    for key in ['OpticalFFCHousing','FrontFFCHousing','FanSocketHousing','PowerSocketHousing']:
        b=m.parts[key].Shape.optimalBoundingBox(False,False)
        upper.append(Part.makeBox(b.XLength+.8,b.YLength+.8,2,V(b.XMin-.4,b.YMin-.4,56)))
    m.cut('UpperEMIShield',upper,'Tall power components, clock cell and cable socket access').Refine=False
    m.cut('LowerEMIShield',m.rr(54,54,2,(-60,25,47.8),2),'Open APU and liquid-metal containment perimeter').Refine=False
    for i,(x,y,angle) in enumerate([(-91,-10,45),(-61,-18,0),(-31,-10,-45),(-19,25,0),(-31,60,45),(-61,70,0),(-91,60,-45),(-103,25,0)]):
        sh=m.rr(13.8,11.8,1,(x,y,55.38),.2);sh.rotate(V(x,y,0),V(0,0,1),angle)
        m.feature('MemoryThermalPad'+str(i),'Memory-to-shield thermal pad study',sh,'Cooling',2,'thermal',True)
    for side,z,h in [('Top',55.7,.8),('Bottom',48.6,1.15)]:
        for i,y in enumerate([-50,-21,8]):
            m.box('NANDThermal'+side+str(i),'NAND thermal pad study',17.4,12.4,h,(-144,y,z),'Cooling',2 if side=='Top' else -2,'thermal',.2,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=17
    m.checkpoint(17,'board_shields_and_thermal_contacts','加入上下两块原生可编辑屏蔽板、风扇/APU/高器件和接口开口，以及八组显存和双面 NAND 导热垫；局部接触层厚度与冲压细节为结构近似。')
    m.snapshot('17_shield_and_memory_interfaces',assemblies=['Mainboard','Shielding','Cooling'],exclude=['UpperFanGuard']+['FanGuardScrew'+str(i) for i in range(4)],normal=(.3,-.6,1.7))


STAGES[17]=stage17


def stage18(m):
    from .ps1 import _add_shape
    m.native('M2Bay','Original empty expansion bay metal tray',116,23.2,1.2,11.7,(94,-86,61.5),'Storage',2,'metal')
    m.cut('M2Bay',m.rr(114,21.2,11.5,(94,-86,62.2),.6),'Empty original expansion cavity').Refine=False
    m.cut('M2Bay',m.rr(20,19,3.5,(35,-68,70.7),3.3),'Upper corner clearance around the dust-access collar').Refine=False
    m.native('M2Cover','Removable expansion bay cover',118,25,2,.8,(94,-86,76),'Storage',5,'metal')
    _add_shape(m,'M2Cover',Part.makeCylinder(3.2,.8,V(155,-86,76)),'Expansion cover screw tab').Refine=False
    m.cut('M2Cover',Part.makeCylinder(1.05,1.4,V(155,-86,75.7)),'Expansion cover screw clearance').Refine=False
    m.cut('InnerUpperFrame',Part.makeCylinder(1.05,3,V(155,-86,73.5)),'Expansion cover screw clearance through the inner cover').Refine=False
    m.ring('M2CoverBoss','Expansion cover fixing boss',2.3,1.05,11,(155,-86,62.7),'Storage',3,'black',internal=True)
    m.screw('M2CoverScrew',(155,-86,77.2),'Storage',6,length=5.4,radius=1.8,axis=(0,0,-1))
    for i,x in enumerate([70,82,100,120,149]):
        m.ring('M2Mount'+str(i),'Alternative module-length mounting seat study',1.7,.85,2.1,(x,-86,62.35),'Storage',3,'metal',internal=True)
    m.ring('M2StoredSpacer','Stored module fixing spacer',1.9,.9,.6,(149,-86,64.6),'Storage',3,'metal',internal=True)
    m.screw('M2StoredScrew',(149,-86,65.65),'Storage',4,length=3,radius=1.7,axis=(0,0,-1))
    socket=m.rr(6,20.8,4.4,(40.2,-86,62.4),.25)
    socket=socket.cut(Part.makeBox(5,19.8,1.2,V(39,-95.9,64.6)))
    key=m.rr(4.2,1.6,1.2,(41.5,-92,64.6),.06)
    socket=socket.fuse(key).removeSplitter()
    m.feature('M2Socket','Keyed M.2 expansion socket housing study',socket,'Storage',3,'black',True)
    for side,count,z in [('Lower',38,64.72),('Upper',37,65.55)]:
        for i in range(count):
            if i in [5,6,7,8]:continue
            m.box('M2Contact'+side+str(i),'Separate expansion socket spring contact',3.1,.22,.1,(41.75,-95.25+i*.5,z),'Storage',3,'gold',.025,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=18
    m.checkpoint(18,'empty_original_m2_expansion_bay','建立原版空 M.2 扩展仓、可拆盖板及固定螺钉、不同长度的示意固定座、收纳螺丝/垫柱和含 67 个独立触点的带键连接器。保持原包装未加装 SSD 的状态；座位与接点尺寸为学习近似。')
    m.snapshot('18_empty_m2_bay',assemblies=['Storage'],exclude=['M2Cover','M2CoverScrew'],normal=(.3,-.6,1.7))


STAGES[18]=stage18


def stage19(m):
    m.native('FrontInterfacePCB','Original front USB interface PCB study',52,12.4,1,.6,(7,-108.6,54),'FrontIO',1,'pcb')
    m.cut('FrontInterfacePCB',Part.makeCylinder(3.8,1.2,V(-20,-100,53.7)),'Front chassis pillar clearance beside the interface board').Refine=False
    for i,(x,y) in enumerate([(-15,-113),(31,-106)]):
        m.cut('FrontInterfacePCB',Part.makeCylinder(1.8,1.2,V(x,y,53.7)),'Front interface fixing post clearance').Refine=False
        m.ring('FrontPCBPost'+str(i),'Front interface PCB fixing post',1.6,.8,1.9,(x,y,53.9),'FrontIO',1,'black',internal=True)
        m.screw('FrontPCBScrew'+str(i),(x,y,56.2),'FrontIO',2,length=2,radius=1.3,axis=(0,0,-1))
    for i,(x,y,w,d) in enumerate([(-15,-108,4,4),(6,-107,6,4),(8,-113,5,3)]):
        m.box('FrontInterfaceIC'+str(i),'Front interface logic package study',w,d,.9,(x,y,54.8),'FrontIO',1,'black',.2,True)
    terminals=[]
    for row,y,z in [('Lower',-106.3,57.58),('Upper',-104.9,58.34)]:
        for i in range(12):
            x=-5+(i-5.5)*.5
            foot=Part.makeBox(.18,1,.16,V(x-.09,y-.5,54.7))
            stem=Part.makeBox(.18,.18,z+.08-54.8,V(x-.09,y-.09,54.8))
            arm=Part.makeBox(.18,y+.09+110.6,.08,V(x-.09,-110.6,z))
            sh=foot.fuse(stem).fuse(arm).removeSplitter()
            m.feature('USBCBoardTail'+row+str(i),'Separate formed USB-C PCB terminal',sh,'FrontIO',1,'gold',True);terminals.append(sh)
    m.cut('USBCInsulator',terminals,'Moulded channels for the independent USB-C board terminals').Refine=False
    socket=m.rr(8,2.4,1.4,(-12,-104.6,54.8),.2).cut(m.rr(6.8,1.3,1.2,(-12,-104.6,55.3),.1))
    m.feature('FrontBoardSocket','Front interface ribbon socket',socket,'FrontIO',1,'white',True)
    for i in range(12):m.box('FrontBoardContact'+str(i),'Front interface ribbon contact',.22,1,.1,(-14.75+i*.5,-104.6,55.45),'FrontIO',1,'gold',.02,True)
    front=g.rotation((0,-1,0),(0,0,1))
    m.box('ButtonPCB','Separate power and eject switch board',39,8,.8,(-154.5,-111.5,53),'Controls',1,'pcb',.5,True,orient=front)
    for key,x in [('Power',-165),('Eject',-144)]:
        m.box(key+'Switch','Front tactile switch package',4,2.2,3,(x,-113.8,51.5),'Controls',1,'metal',.3,True)
        m.cyl(key+'Plunger','Tactile switch plunger',.7,.7,(x,-115.8,53),'Controls',1,'black',axis=(0,1,0),internal=True)
        m.cyl(key+'Stem','Separate front button actuator stem',.6,.6,(x,-116.5,53),'Controls',1,'black',axis=(0,1,0),internal=True)
        for i,dx in enumerate([-2.7,2.7]):
            for j,z in enumerate([51.8,54]):m.box(key+'SwitchTerminal'+str(i)+'_'+str(j),'Tactile switch solder tab',.25,.9,.25,(x+dx,-113.3,z),'Controls',1,'gold',.03,True)
    m.box('ButtonController','Front control logic package study',6,2,3.2,(-154.5,-113.4,51.4),'Controls',1,'black',.2,True)
    m.box('ButtonConnector','Button-board cable connector study',5,3,3,(-154.5,-110,51.5),'Controls',1,'white',.3,True)
    m.native('StatusLightPCB','Status-light emitter strip study',285,3,.7,.8,(5,-112,78.4),'Controls',4,'pcb')
    for i,x in enumerate([-110,-55,0,55,110]):
        m.box('StatusLED'+str(i),'Blue status emitter package',1.4,1.2,.35,(x,-112,79.35),'Controls',4,'ps5blue',.1,True)
        m.cut('CoreFrame',Part.makeBox(3.4,8,.9,V(x-1.7,-118,79.7)),'Status light transmission aperture').Refine=False
        m.box('StatusLightPipe'+str(i),'Status light internal guide',3,6,.5,(x,-114.6,79.9),'Controls',4,'ps5blue',.12,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=19
    m.checkpoint(19,'front_boards_switches_and_status_lighting','补齐前置 USB 电路板与独立 Type-C 成形端子、电源/出仓按钮电路板和触动件，以及状态灯条、电路板和透光通道。电子封装、局部尺寸与连接方式为结构学习近似。')
    m.snapshot('19_front_electronics',assemblies=['FrontIO','Controls'],normal=(.3,-.8,1.8))


STAGES[19]=stage19


def _folded_ribbon(points,width,thickness=.16):
    parts=[]
    points=[V(*p) for p in points]
    for a,b in zip(points,points[1:]):
        delta=b-a;normal=V(0,-delta.z,delta.y)
        assert normal.Length>1e-7
        normal.normalize();wide=V(width/2,0,0);thin=normal*(thickness/2)
        corners=[a-wide-thin,a+wide-thin,a+wide+thin,a-wide+thin]
        parts.append(Part.Face(Part.makePolygon(corners+[corners[0]])).extrude(delta))
    sh=parts[0].multiFuse(parts[1:]).removeSplitter()
    assert len(sh.Solids)==1 and sh.isValid()
    sh.check(True);return sh


def stage20(m):
    from .atari2600 import _rounded_route
    m.cut('DriveFlexSocket',Part.makeBox(6.6,1.8,.7,V(-104.3,-60.8,20.3)),'Drive ribbon exit through the connector lip').Refine=False
    m.cut('DriveHousing',Part.makeBox(6,9,.6,V(-171,-90,30.7)),'Optical ribbon exit at the left enclosure edge').Refine=False
    m.cut('OpticalFFCHousing',Part.makeBox(6.6,1.8,3.2,V(-152.3,-84.3,55.15)),'Optical ribbon entry lip clearance').Refine=False
    optical=[(-101,-58.5,20.65),(-101,-62,20.65),(-137,-88,20.65),(-137,-88,31),(-175,-85,31),(-175,-85,58.2),(-149,-90,58.2),(-149,-84,58.2),(-149,-82.7,55.45)]
    m.feature('OpticalRibbon','Continuous drive-to-mainboard signal ribbon study',_folded_ribbon(optical,6,.16),'Wiring',1,'white',True)
    m.cut('FrontFFCHousing',Part.makeBox(6.6,1.5,3,V(-65.3,-98,55.35)),'Front interface ribbon entry lip clearance').Refine=False
    m.cut('UpperEMIShield',Part.makeBox(7,7.1,2,V(-65.5,-99.2,56)),'Front ribbon approach through the upper shield').Refine=False
    front=[(-12,-104.6,55.7),(-12,-105.3,58),(-62,-106.2,58),(-62,-99,58),(-62,-96.5,55.6)]
    m.feature('FrontInterfaceRibbon','Front USB board signal ribbon study',_folded_ribbon(front,6,.16),'Wiring',2,'white',True)
    socket=m.rr(5,3,2.8,(-34,-87,54),.25).cut(m.rr(3.8,1.8,2.5,(-34,-87,54.9),.12))
    m.feature('ButtonMainSocket','Mainboard front-button wire socket',socket,'Mainboard',1,'white',True)
    m.cut('ButtonMainSocket',Part.makeBox(3.1,1,2,V(-35.55,-88.8,55.2)),'Button harness entry through the socket lip').Refine=False
    m.cut('UpperEMIShield',m.rr(5.8,3.8,2,(-34,-87,56),.3),'Button harness socket clearance').Refine=False
    for i,dx in enumerate([-.8,0,.8]):
        m.box('ButtonMainContact'+str(i),'Button harness socket contact',.2,1.2,.15,(-34+dx,-87,55.1),'Mainboard',1,'gold',.03,True)
        points=[(-154.5+dx,-107.85,53),(-154.5+dx,-106.3+(i-1)*.7,61.2-i*.7),(-36+dx,-102+(i-1)*.7,61.2-i*.7),(-34+dx,-90,61.2-i*.7),(-34+dx,-88,56),(-34+dx,-87.5,55.5)]
        m.feature('ButtonHarness'+str(i),'Separate insulated front-button wire study',_rounded_route([V(*p) for p in points],.35,.22),'Wiring',2,'red' if i==0 else 'black',True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=20
    m.checkpoint(20,'optical_front_and_button_signal_routes','建立绕过主板边缘的连续光驱排线、前置 USB 板排线及按钮线束，并加工对应壳体、连接器及屏蔽层开口。排线路径避开空盘通道，折线过渡和线径为静态学习近似。')
    m.snapshot('20_signal_routes',assemblies=['Mainboard','FrontIO','Controls','Wiring'],normal=(.3,-.6,1.7))


STAGES[20]=stage20


def stage21(m):
    from .atari2600 import _rounded_route
    def cable(key,label,points,r,material):
        sh=_rounded_route([V(*p) for p in points],.7 if r>.3 else .35,r)
        sh.check(True)
        return m.feature(key,label,sh,'Wiring',2,material,True)
    m.cut('MainPCB',Part.makeBox(24,9,3,V(64,98,51.4)),'AC lead departure clearance behind the rear inlet').Refine=False
    for i,(startx,endx) in enumerate([(71.8,-147.76),(80.2,-142.24)]):
        y=90.5+i*1.3;z=49.3+i*1.6
        for key in ['LowerEMIShield','PowerLid']:
            m.cut(key,Part.makeCylinder(.9,20,V(endx,94,33)),'Insulated mains lead feedthrough').Refine=False
        cable('MainsHarness'+str(i),'Independent insulated mains lead study',[(startx,100.25,51.5),(startx,y,z),(endx,y,z),(endx,94,z),(endx,94,33.6)],.55,'black')
    for i,x in enumerate([11.32,18.68]):
        for key in ['PowerLid','LowerEMIShield','MainPCB','UpperEMIShield']:
            m.cut(key,Part.makeCylinder(1.05,35,V(x,49,32)),'Insulated low-voltage power feedthrough').Refine=False
        targetx=15+(-1.5 if i==0 else 1.5)*17/3
        m.cut('PowerSocketHousing',Part.makeBox(2.2,3,4,V(targetx-1.1,87,54.5)),'Low-voltage lead connector entry').Refine=False
        cable('DCHarness'+str(i),'Independent low-voltage supply lead study',[(x,49,33.65),(x,49,60.5),(targetx,83,60.5),(targetx,87.5,60.5),(targetx,90,56.15)],.65,'red' if i==0 else 'black')
    m.cut('FanHousing',Part.makeBox(4,7,.85,V(103,-49,29.32)),'Fan motor cable exit below the rotating impeller').Refine=False
    m.cut('FanSocketHousing',Part.makeBox(6.1,3.5,4,V(33.95,-67,55)),'Fan harness entry through the front connector lip').Refine=False
    for i in range(4):
        dx=(i-1.5)*.55;enddx=(i-1.5)*5/3;y=-47.5+(i-1.5)*.65
        cable('FanHarness'+str(i),'Separate four-wire fan lead study',[(105+dx,0,29.75),(105+dx,y,29.75),(105+dx,y,58.8+(i-1.5)*.6),(37+enddx,-68-(i-1.5)*.65,58.8+(i-1.5)*.6),(37+enddx,-64.5,58.8+(i-1.5)*.6),(37+enddx,-63.25,55.65)],.18,['red','black','blue','white'][i])
    socket=m.rr(5,3,2.8,(-6,-87,54),.25).cut(m.rr(3.8,1.8,2.5,(-6,-87,54.9),.12))
    m.feature('StatusMainSocket','Mainboard status-light wire socket',socket,'Mainboard',1,'white',True)
    m.cut('StatusMainSocket',Part.makeBox(3.1,1,2,V(-7.55,-88.8,55.2)),'Status lead entry through the socket lip').Refine=False
    m.cut('UpperEMIShield',m.rr(5.8,3.8,2,(-6,-87,56),.3),'Status-light socket clearance').Refine=False
    m.cut('InnerUpperFrame',Part.makeBox(5,3,5,V(2.5,-110.4,73)),'Status strip harness passage through the upper frame').Refine=False
    for i,dx in enumerate([-.8,0,.8]):
        m.box('StatusMainContact'+str(i),'Status harness socket contact',.2,1.2,.15,(-6+dx,-87,55.1),'Mainboard',1,'gold',.03,True)
        cable('StatusHarness'+str(i),'Independent status-light lead study',[(5+dx,-110,78),(5+dx,-108+(i-1)*.65,60),(-6+dx,-94+(i-1)*.65,60),(-6+dx,-90,60),(-6+dx,-88,56),(-6+dx,-87.5,55.5)],.2,'blue' if i==0 else 'black')
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=21
    m.checkpoint(21,'power_fan_and_status_harnesses','加入市电输入、低压供电、四线风扇及状态灯的独立绝缘线束，并加工穿板孔及接插件入口。线束走向、截面和内部连接为静态拆解学习近似。')
    m.snapshot('21_console_harnesses',assemblies=['Wiring','Power','Mainboard','Controls'],exclude=['PowerLid'],normal=(.3,-.6,1.7))


STAGES[21]=stage21


def stage22(m):
    from .atari2600 import _rounded_route
    for i,(x,y) in enumerate([(-164,-25),(-10,-30),(0,75),(140,88)]):
        for key in ['MainPCB','UpperEMIShield','LowerEMIShield']:
            m.cut(key,Part.makeCylinder(3,12,V(x,y,47)),'Through-stack shield fixing clearance').Refine=False
        m.ring('BoardStackPost'+str(i),'Mainboard and EMI shield spacing post',2.8,.85,9.5,(x,y,48),'Shielding',1,'metal',internal=True)
        m.screw('BoardStackScrew'+str(i),(x,y,58.1),'Shielding',3,length=7.8,radius=1.7,axis=(0,0,-1))
    for i,(x,y) in enumerate([(-173,-40),(169,-58)]):
        m.native('AntennaPCB'+str(i),'Separate wireless antenna substrate study',7.2,24,.7,.55,(x,y,77.1),'Wireless',4,'pcb')
        pattern=m.rr(5.8,21,.08,(x,y,77.8),.4).cut(m.rr(3.8,16,.2,(x,y,77.75),.3))
        m.feature('AntennaTrace'+str(i),'Wireless printed radiator envelope study',pattern,'Wireless',4,'gold',True)
        m.cut('InnerUpperFrame',Part.makeCylinder(.7,5,V(x,y-10,73)),'Wireless coaxial lead passage').Refine=False
    paths=[[(121,-79,55.95),(121,-79,60),(121,-104.1,60),(121,-104.1,62),(-173,-104.1,62),(-173,-50,62),(-173,-50,77)],[(125,-79,55.95),(125,-69,60.3),(169,-69,60.3),(169,-68,77)]]
    for i,path in enumerate(paths):
        sh=_rounded_route([V(*p) for p in path],.4,.22);sh.check(True)
        m.feature('AntennaCoax'+str(i),'Wireless antenna coaxial lead study',sh,'Wiring',3,'black',True)
        passage=_rounded_route([V(*p) for p in path],.4,.42)
        m.cut('UpperEMIShield',passage,'Antenna cable insulated shield passage').Refine=False
    # Short independent retainers show the removable cover's sliding engagement.
    for i,(x,y,z) in enumerate([(-145,-105,79),(-90,102,80),(12,103,80),(128,-106,83)]):
        hook=m.rr(5,3,3,(x,y,z),.35).fuse(m.rr(5,5,.7,(x,y+1,z+2.8),.25)).removeSplitter()
        m.feature('UpperCoverHook'+str(i),'Upper white-cover sliding hook study',hook,'Frame',5,'ps5white',True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=22
    m.checkpoint(22,'board_fixings_antennas_and_cover_retainers','补充屏蔽层与主板的贯穿固定柱/螺钉、两片独立天线与同轴线、上罩滑扣；孔位、天线图案和局部固定方式为静态结构近似。')
    m.snapshot('22_console_detail_review',assemblies=['Frame','Shielding','Wireless','Wiring'],normal=(.3,-.6,1.7))


STAGES[22]=stage22


def _sense_point(x,y,z):return V(x,y-285,z)


def _sense_curves(sx,sy):
    points=[(0,49),(31,49),(47,45),(63,35),(75,11),(80,-14),(77,-40),(70,-57),(62,-51),(47,-21),(30,-11),(0,-11)]
    tangents=[(1,0),(1,0),(1,-.3),(.7,-.7),(.2,-1),(0,-1),(-.2,-1),(-1,0),(-.55,.8),(-.6,.8),(-1,0),(-1,0)]
    nodes=[V(x,y) for x,y in points];directions=[V(x,y).normalize() for x,y in tangents]
    lengths=[.30*min((p-nodes[i-1]).Length if i else (nodes[1]-p).Length,(nodes[i+1]-p).Length if i+1<len(nodes) else (p-nodes[i-1]).Length) for i,p in enumerate(nodes)]
    segments=[[a,a+directions[i]*lengths[i],b-directions[i+1]*lengths[i+1],b] for i,(a,b) in enumerate(zip(nodes,nodes[1:]))]
    segments += [[V(-p.x,p.y) for p in reversed(seg)] for seg in reversed(segments)]
    curves=[]
    for seg in segments:
        c=Part.BezierCurve();c.setPoles([V(p.x*sx,p.y*sy) for p in seg]);curves.append(c.toBSpline())
    return curves


def _sense_loft(m,key,profiles):
    sketches=[]
    for i,(sx,sy,z) in enumerate(profiles):
        sk=m.doc.addObject('Sketcher::SketchObject',key+'Section'+str(i));sk.Label='DualSense editable curved section '+str(i+1)
        sk.addGeometry(_sense_curves(sx,sy),False);sk.Placement=App.Placement(_sense_point(0,0,z),App.Rotation())
        m.group('Construction').addObject(sk);sketches.append(sk)
    loft=m.doc.addObject('Part::Loft',key);loft.Sections=sketches;loft.Solid=True;loft.Ruled=False;loft.Closed=False;loft.MaxDegree=3
    m.doc.recompute();assert loft.Shape.isValid() and len(loft.Shape.Solids)==1;loft.Shape.check(True)
    m.group('Construction').addObject(loft)
    for sk in sketches:sk.Visibility=False
    loft.Visibility=False;return loft


def _sense_shell(m,key,outer,inner,layer):
    a=_sense_loft(m,key+'Outer',outer);b=_sense_loft(m,key+'Inner',inner)
    o=m.doc.addObject('Part::Cut',key);o.Base=a;o.Tool=b;o.Refine=False
    m.doc.recompute();assert o.Shape.isValid() and len(o.Shape.Solids)==1;o.Shape.check(True)
    a.Visibility=False;b.Visibility=False
    return m.register(o,key,'Controller',layer,'ps5white')


def stage23(m):
    from .ps1 import _add_shape
    _sense_shell(m,'SenseBack',[(.88,.89,1),(.96,.97,9),(1,1,21),(1,1,28)],[(.84,.85,3),(.925,.932,10),(.970,.965,21),(.970,.965,28.3)],-4)
    _sense_shell(m,'SenseFront',[(1,1,28.3),(.982,.982,39),(.94,.94,47)],[(.970,.965,28.1),(.947,.943,39),(.913,.900,44.6)],4)
    back=[];back_inner=[]
    for x in [-28,28]:
        back.append(Part.makeCylinder(16.7,16,_sense_point(x,-12,12)))
        back_inner.append(Part.makeCylinder(14.9,14.4,_sense_point(x,-12,13.8)))
    _add_shape(m,'SenseBack',back[0].fuse(back[1]),'Integrated lower analogue-stick pods').Refine=False
    m.cut('SenseBack',back_inner,'Hollow lower analogue-stick pods').Refine=False
    # Black central removable trim follows the front shell and extends around both stick cups.
    poly=[(-71,-56),(-47,-15),(-38,12),(38,12),(47,-15),(71,-56),(61,-56),(42,-22),(30,-16),(-30,-16),(-42,-22),(-61,-56)]
    p=[_sense_point(x,y,27.8) for x,y in poly];mask=Part.Face(Part.makePolygon(p+[p[0]])).extrude(V(0,0,24))
    trim=m.parts['SenseFront'].Shape.common(mask)
    pods=[Part.makeCylinder(16.7,20.7,_sense_point(x,-12,28.3)) for x in [-28,28]]
    trim=trim.multiFuse(pods).removeSplitter()
    cavities=[Part.makeCylinder(14.9,18.5,_sense_point(x,-12,28.1)) for x in [-28,28]]
    openings=[Part.makeCylinder(12,4,_sense_point(x,-12,46.4)) for x in [-28,28]]
    trim=trim.cut(Part.makeCompound(cavities+openings))
    m.feature('SenseTrim','Removable black central trim and upper stick cups',trim,'Controller',5,'black')
    m.cut('SenseFront',mask,'Separate removable black central trim boundary').Refine=False
    m.cut('SenseFront',pods,'Upper stick-pod boundary in the white face').Refine=False
    m.cut('SenseFront',m.rr(62,33,13,tuple(_sense_point(0,29,39)),4),'Large white touchpad and edge-light aperture').Refine=False
    m.doc.recompute()
    for key in ['SenseBack','SenseFront','SenseTrim']:
        sh=m.parts[key].Shape;sh.check(True);assert len(sh.Solids)==1,(key,len(sh.Solids))
    m.profile['stages']=23
    m.checkpoint(23,'dualsense_native_white_shell_and_black_trim','建立初代 DualSense 独立原生曲面上下白壳、长握柄、可拆黑色中央饰板与双摇杆杯。轮廓与内部壳厚为照片指导近似，后续补齐按键和反馈机构。')
    m.snapshot('23_dualsense_shell',assemblies=['Controller'],normal=(.2,-.5,2))


STAGES[23]=stage23


def stage24(m):
    from .ps2 import _ds2_symbol
    m.colors.update(senseclear=(.68,.72,.76),sensegrey=(.25,.28,.32),sensegrip=(.075,.08,.09))
    m.cut('SenseFront',m.rr(26,26,2.4,tuple(_sense_point(-50,24,43)),2),'Directional rocker underside clearance').Refine=False
    for i,(x,y) in enumerate([(-50,33.5),(-59.5,24),(-50,14.5),(-40.5,24)]):
        w,h=(6.2,8) if i in [0,2] else (8,6.2)
        m.cut('SenseFront',m.rr(w+.5,h+.5,9,tuple(_sense_point(x,y,41)),1),'Directional key through aperture').Refine=False
        m.box('SenseDirection'+str(i),'Translucent directional key',w,h,6,tuple(_sense_point(x,y,45.3)),'Controller',5,'senseclear',.9)
    m.box('SenseDirectionLinkX','Directional rocker horizontal link',23,4,.7,tuple(_sense_point(-50,24,43.7)),'Controller',3,'white',.4,True)
    m.box('SenseDirectionLinkY','Directional rocker vertical link',4,23,.7,tuple(_sense_point(-50,24,44.5)),'Controller',3,'white',.4,True)
    for kind,x,y in [('Triangle',50,33.5),('Circle',59.5,24),('Cross',50,14.5),('Square',40.5,24)]:
        m.cut('SenseFront',Part.makeCylinder(4.85,9,_sense_point(x,y,41)),'Action button through aperture').Refine=False
        m.cut('SenseFront',Part.makeCylinder(5.7,4.3,_sense_point(x,y,41)),'Action button retaining flange relief').Refine=False
        cap=Part.makeCylinder(4.6,6.2,_sense_point(x,y,45)).fuse(Part.makeCylinder(5.5,.7,_sense_point(x,y,44.4)))
        m.feature('SenseButton'+kind,'Translucent '+kind+' face key',cap,'Controller',5,'senseclear')
        _ds2_symbol(m,'SenseSymbol'+kind,kind,x,y-45,51.225,'sensegrey')
    m.box('SenseTouchLight','Blue light guide around the touch surface',61.5,32.5,.75,tuple(_sense_point(0,29,47.2)),'Controller',5,'ps5blue',3.8)
    m.box('SenseTouchpad','Large white capacitive touch surface',60.3,31.3,2.2,tuple(_sense_point(0,29,48.05)),'Controller',6,'ps5white',3.3)
    m.native('SenseTouchPCB','Native touch-sensing circuit board',57.5,28.5,2.5,.75,tuple(_sense_point(0,29,45.2)),'Controller',4,'pcb')
    for key,x in [('Create',-35),('Options',35)]:
        m.cut('SenseFront',m.rr(3.4,8.6,8,tuple(_sense_point(x,36,41)),1.4),key+' key aperture').Refine=False
        m.box('Sense'+key,key+' slim key',2.9,8.1,4.5,tuple(_sense_point(x,36,46.1)),'Controller',5,'ps5white',1.25)
    for key,w,h,y in [('PS',5.8,5.8,-.5),('Mute',8,2.5,-7)]:
        m.cut('SenseTrim',m.rr(w+.5,h+.5,8,tuple(_sense_point(0,y,42)),.8),key+' control opening').Refine=False
        m.box('Sense'+key,key+' system control',w,h,3.6,tuple(_sense_point(0,y,46.4)),'Controller',6,'sensegrey' if key=='PS' else 'white',.7)
    m.label('SensePSMark','PS',2.2,tuple(_sense_point(-2,-1.8,50.025)),'Controller',7,'black')
    m.box('SenseMuteLED','Mute indicator window',4.5,.45,.1,tuple(_sense_point(0,-7,50.025)),'Controller',7,'gold',.1)
    holes=[Part.makeCylinder(.55,8,_sense_point(x,y,41)) for x in [-4.5,-1.5,1.5,4.5] for y in [5,7.5,10]]
    m.cut('SenseTrim',holes,'Open speaker grille in the removable centre trim').Refine=False
    for i,x in enumerate([-28,28]):
        dome=Part.makeSphere(12.2,_sense_point(x,-12,54)).common(Part.makeBox(27,27,9.15,_sense_point(x-13.5,-25.5,53)))
        stem=Part.makeCylinder(2.2,18.5,_sense_point(x,-12,35.8))
        m.feature('SenseStickDome'+str(i),'Analogue thumbstick dome and shaft',dome.fuse(stem),'Controller',6,'black')
        cap=Part.makeCylinder(10.6,3.6,_sense_point(x,-12,62.3)).cut(Part.makeSphere(11.5,_sense_point(x,-12,76.7)))
        m.feature('SenseStickCap'+str(i),'Concave textured-rubber thumb cap study',cap,'Controller',7,'sensegrip')
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=24
    m.checkpoint(24,'dualsense_touchpad_translucent_controls_and_sticks','补齐白色触摸板、蓝色边缘导光、灰色符号透明按键、CREATE/OPTIONS、PS 与静音键、扬声器贯通孔，以及独立凹面摇杆帽。透明材质以浅灰学习模型表达。')
    m.snapshot('24_dualsense_controls',assemblies=['Controller'],normal=(.2,-.5,2))


STAGES[24]=stage24


def stage25(m):
    from .ps1 import _add_shape
    from .ps4 import _ds4_joystick
    m.colors.update(sensepcb=(.075,.22,.18),ctrlcream=(.72,.73,.70))
    m.native('SensePCB','Native original DualSense circuit-board layout study',106,50,1.5,1.1,tuple(_sense_point(0,15,21)),'Controller',0,'sensepcb')
    _add_shape(m,'SensePCB',Part.makeCompound([Part.makeCylinder(14.3,1.1,_sense_point(x,-12,21)) for x in [-28,28]]),'Integral analogue module board lobes').Refine=False
    m.cut('SenseBack',m.rr(108,52,1.7,tuple(_sense_point(0,15,20.7)),1.8),'Mainboard passage through the rear stick-pod walls').Refine=False
    for key,x,y,w,h in [('MCU',0,25,10,10),('Wireless',-19,23,7,7),('Motion',17,24,5,5),('Audio',-7,8,5,4),('HapticDriver',33,22,5,5),('TriggerDriver',-34,21,5,5)]:
        m.box('Sense'+key,key+' electronic package study',w,h,1.1,tuple(_sense_point(x,y,22.3)),'Controller',1,'black',.2,True)
    for i,x in enumerate([-38,-31,-24,-17,17,24,31,38]):
        for j,y in enumerate([33,37]):m.box('SenseBypass'+str(i)+'_'+str(j),'Controller representative discrete',1.7,.85,.55,tuple(_sense_point(x,y,22.3)),'Controller',1,'metal',.07,True)
    m.box('SenseCrystal','Controller oscillator package',3.6,2.6,.8,tuple(_sense_point(8,23,22.3)),'Controller',1,'metal',.2,True)
    holes=[]
    # DualSense retains this potentiometer/gimbal architecture; relocate and relabel the shared mechanism.
    for i,x in enumerate([-28,28]):
        before=set(m.parts);bores=_ds4_joystick(m,i,x,-12)
        for key in set(m.parts)-before:
            o=m.parts.pop(key);newkey=key.replace('DS4Joy','SenseJoy');o.PartID=newkey;m.parts[newkey]=o
            place=o.Placement;place.Base+=V(0,-40,8);o.Placement=place;o.FlatPlacement=place
        for sh in bores:sh.translate(V(0,-40,8));holes.append(sh)
        m.cut('SenseStickDome'+str(i),Part.makeCylinder(1.9,2.5,_sense_point(x,-12,35.6)),'Keyed analogue shaft cavity in the thumbstick stem').Refine=False
    m.cut('SensePCB',holes,'Joystick anchor and potentiometer terminal bores').Refine=False
    for i,(x,y) in enumerate([(-44,5),(44,5),(0,37)]):
        m.cut('SensePCB',Part.makeCylinder(1,1.6,_sense_point(x,y,20.8)),'Main controller board fixing bore').Refine=False
        m.ring('SenseBoardGround'+str(i),'Controller mounting ground annulus',2,1.1,.05,tuple(_sense_point(x,y,22.12)),'Controller',0,'gold',internal=True)
        m.ring('SenseBoardPost'+str(i),'Controller mainboard spacing pillar',2,.8,6.5,tuple(_sense_point(x,y,14.3)),'Controller',-1,'ctrlcream',internal=True)
        m.screw('SenseBoardScrew'+str(i),tuple(_sense_point(x,y,23.1)),'Controller',1,length=6,radius=1.5,axis=(0,0,-1))
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=25
    m.checkpoint(25,'dualsense_board_gimbals_and_control_electronics','加入初代 DualSense 主板、逻辑/无线/音频/反馈驱动封装、两组双轴摇杆笼与电位器、L3/R3 开关、独立穿板端子及固定件。电子布局和封装为非功能性结构近似。')
    m.snapshot('25_dualsense_mainboard',assemblies=['Controller'],exclude=['SenseFront','SenseBack','SenseTrim','SenseTouchpad','SenseTouchLight','SenseTouchPCB','SenseStickDome0','SenseStickDome1','SenseStickCap0','SenseStickCap1'],normal=(.2,-.5,2))


STAGES[25]=stage25


def stage26(m):
    m.colors.update(senseflex=(.16,.33,.22),sensesilicone=(.64,.67,.69))
    carrier=m.rr(108,14,1.6,tuple(_sense_point(0,24,36.5)),1)
    film=m.rr(106,12,.12,tuple(_sense_point(0,24,38.3)),.8)
    for x in [-50,50]:
        carrier=carrier.fuse(Part.makeCylinder(18.5,1.6,_sense_point(x,24,36.5)))
        film=film.fuse(Part.makeCylinder(17.7,.12,_sense_point(x,24,38.3)))
    carrier=carrier.fuse(m.rr(20,28,1.6,tuple(_sense_point(0,11,36.5)),1))
    film=film.fuse(m.rr(18,27,.12,tuple(_sense_point(0,11,38.3)),.7))
    opening=m.rr(15,8,4,tuple(_sense_point(0,8.2,36)),1)
    shoulders=Part.makeCompound([m.rr(20,12,10,tuple(_sense_point(x,45,35)),1) for x in [-52,52]])
    m.feature('SenseContactCarrier','Moulded button-film support carrier',carrier.cut(opening).common(m.doc.getObject('SenseFrontInner').Shape).cut(shoulders),'Controller',2,'ctrlcream',True)
    m.feature('SenseContactFilm','Flexible directional and action contact film',film.cut(opening).common(m.doc.getObject('SenseFrontInner').Shape).cut(shoulders),'Controller',3,'senseflex',True)
    groups=[('Direction',-50,24,[(-50,33.5),(-59.5,24),(-50,14.5),(-40.5,24)]),('Action',50,24,[(50,33.5),(59.5,24),(50,14.5),(40.5,24)]),('System',0,-.5,[(0,-.5)])]
    for name,cx,cy,keys in groups:
        membrane=Part.makeCylinder(16.8 if len(keys)>1 else 4.3,.6,_sense_point(cx,cy,38.7))
        for i,(x,y) in enumerate(keys):
            membrane=membrane.cut(Part.makeCylinder(3.4,.9,_sense_point(x,y,38.55)))
            dome=Part.makeCone(4,2.6,3.8,_sense_point(x,y,39.3)).cut(Part.makeCone(3.5,2.15,3.45,_sense_point(x,y,39.25)))
            membrane=membrane.fuse(dome)
            m.cyl('Sense'+name+'Carbon'+str(i),'Moving carbon contact pill',1.8,.15,tuple(_sense_point(x,y,42.52)),'Controller',4,'black',internal=True)
            fixed=Part.makeCylinder(2.5,.05,_sense_point(x,y,38.46)).cut(Part.makeBox(.3,6,.15,_sense_point(x-.15,y-3,38.41)))
            m.feature('Sense'+name+'Fixed'+str(i),'Split fixed conductive film contact',fixed,'Controller',3,'black',True)
        m.feature('Sense'+name+'Membrane','Hollow silicone button-return domes',membrane.common(m.doc.getObject('SenseFrontInner').Shape).cut(shoulders),'Controller',4,'sensesilicone',True)
    for key,x,y,w,h in [('Create',-35,36,3.5,5),('Options',35,36,3.5,5),('Mute',0,-7,6,2.2)]:
        m.box('Sense'+key+'Switch','Small controller tactile switch',w,h,1.5,tuple(_sense_point(x,y,41)),'Controller',3,'black',.3,True)
        m.box('Sense'+key+'Actuator','Tactile switch independent actuator',w*.6,h*.6,3.4,tuple(_sense_point(x,y,42.6)),'Controller',4,'ctrlcream',.25,True)
    basket=m.rr(13,6,4.6,tuple(_sense_point(0,8.2,39)),.9).cut(m.rr(11.5,4.5,4.1,tuple(_sense_point(0,8.2,39.7)),.6))
    m.feature('SenseSpeakerBasket','Controller loudspeaker basket',basket,'Controller',3,'metal',True)
    m.box('SenseSpeakerMagnet','Loudspeaker magnetic circuit',10,3.5,1.1,tuple(_sense_point(0,8.2,39.85)),'Controller',3,'black',.5,True)
    m.box('SenseSpeakerDiaphragm','Thin loudspeaker diaphragm',11.2,4.2,.08,tuple(_sense_point(0,8.2,43.3)),'Controller',4,'black',.5,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=26
    m.checkpoint(26,'dualsense_contact_film_membranes_and_speaker','加入独立按键接点膜、支架、空心硅胶回弹结构和碳粒、控制轻触开关，以及扬声器篮架、磁路和振膜。保持未按下接点的静态间隙。')
    m.snapshot('26_dualsense_contacts',assemblies=['Controller'],exclude=['SenseFront','SenseBack','SenseTrim','SenseTouchpad','SenseTouchLight','SenseTouchPCB','SenseStickDome0','SenseStickDome1','SenseStickCap0','SenseStickCap1'],normal=(.2,-.5,2))


STAGES[26]=stage26


def stage27(m):
    front=g.rotation((0,1,0),(0,0,1))
    for side,name in [(-1,'Left'),(1,'Right')]:
        x=side*52;key='Sense'+name
        aperture=m.rr(21,34,20,tuple(_sense_point(x,33,25)),2,front)
        for shell in ['SenseFront','SenseBack']:
            m.cut(shell,aperture,'Shoulder trigger and bumper opening').Refine=False
        m.cut('SensePCB',m.rr(20,26,2,tuple(_sense_point(x,30,20.6)),1),'Adaptive-trigger module board-edge clearance').Refine=False
        # Narrow vertical side carrier leaves the gear train and trigger pivot separately removable.
        housing=m.rr(9,23,25,tuple(_sense_point(x,31.5,10)),1).cut(m.rr(6.8,20.8,25.5,tuple(_sense_point(x,31.5,10.7)),.6))
        housing=housing.cut(Part.makeCylinder(1.05,14,_sense_point(x-7,41,24),V(1,0,0)))
        housing=housing.cut(m.rr(10,10,4,tuple(_sense_point(x,39.5,31.3)),.4))
        housing=housing.cut(m.rr(10,3,13,tuple(_sense_point(x,43.2,13.5)),.25))
        m.feature(key+'TriggerCarrier','Adaptive-trigger mechanism open carrier',housing,'Controller',0,'black',True)
        cap=m.rr(17,12,6,tuple(_sense_point(x,42,20)),2,front).cut(m.rr(14.4,9.4,4.8,tuple(_sense_point(x,41.8,20)),1.2,front))
        arms=[m.rr(2,4,4,tuple(_sense_point(x+dx,41,22)),.35) for dx in [-7,7]]
        cap=cap.multiFuse(arms).removeSplitter().cut(Part.makeCylinder(1.05,20,_sense_point(x-10,41,24),V(1,0,0)))
        m.feature(key+'Trigger','Independent adaptive-trigger finger paddle',cap,'Controller',4,'black')
        m.cyl(key+'TriggerAxle','Trigger steel pivot axle',.85,19,tuple(_sense_point(x-9.5,41,24)),'Controller',2,'metal',axis=(1,0,0),internal=True)
        for j,dx in enumerate([-9.3,8.8]):m.ring(key+'PivotWasher'+str(j),'Trigger pivot retaining washer',1.7,1.05,.35,tuple(_sense_point(x+dx,41,24)),'Controller',2,'metal',axis=(1,0,0),internal=True)
        bumper=m.rr(18,7,7,tuple(_sense_point(x,40,38)),1.7,front)
        m.feature(key+'Bumper','Independent L1/R1 shoulder button',bumper,'Controller',5,'black')
        m.box(key+'BumperStem','Shoulder button force-transfer stem',3,7,.45,tuple(_sense_point(x,40,33.95)),'Controller',3,'white',.4,True)
        m.box(key+'BumperSwitch','Shoulder tactile switch body',5,4,1.7,tuple(_sense_point(x,38,31.8)),'Controller',2,'black',.4,True)
        m.box(key+'BumperActuator','Shoulder switch actuator',2.6,2.6,.3,tuple(_sense_point(x,38,33.6)),'Controller',3,'white',.3,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=27
    m.checkpoint(27,'dualsense_trigger_carriers_paddles_and_shoulders','建立左右自适应扳机的独立安装架、带转轴孔的指托、钢轴和限位垫圈，以及 L1/R1 按键、传力杆和开关。扳机驱动齿轮及电机下一轮补齐。')
    m.snapshot('27_dualsense_shoulders',assemblies=['Controller'],normal=(.2,.6,1.6))


STAGES[27]=stage27


def stage28(m):
    from .ps1 import _gear
    from .atari2600 import _helical_spring
    for side,name in [(-1,'Left'),(1,'Right')]:
        x=side*52;key='Sense'+name;q=App.Rotation(V(0,0,1),V(1,0,0))
        def axial(shape,y,z,xoffset=0):
            sh=shape.copy();sh.Placement=App.Placement(_sense_point(x+xoffset,y,z),q).multiply(sh.Placement);return sh
        for target in [key+'TriggerCarrier']:
            m.cut(target,Part.makeCylinder(1.1,12,_sense_point(x-6,31,23),V(1,0,0)),'Adaptive gear axle passage').Refine=False
            m.cut(target,Part.makeCylinder(.8,6,_sense_point(x,18,14.7),V(0,1,0)),'Trigger motor spindle entry').Refine=False
        gear=axial(_gear(m,0,0,0,6.3,6.8,2,24).cut(Part.makeCylinder(1.1,2.4,V(0,0,-.2))),31,23,-1)
        m.feature(key+'ReductionGear','Adaptive-trigger reduction gear study',gear,'Controller',2,'white',True)
        m.cyl(key+'GearAxle','Adaptive gear independent pivot',.85,9,tuple(_sense_point(x-4.5,31,23)),'Controller',1,'metal',axis=(1,0,0),internal=True)
        # Worm uses a segmented exact helix with a continuous central core.
        worm=_helical_spring(.65,1.4,12,.15).fuse(Part.makeCylinder(.55,12)).removeSplitter()
        worm.Placement=App.Placement(_sense_point(x,25.1,14.7),App.Rotation(V(0,0,1),V(0,1,0)))
        m.feature(key+'Worm','Helical adaptive-trigger worm study',worm,'Controller',1,'white',True)
        m.ring(key+'MotorCan','Adaptive-trigger motor can',3.5,3.1,8.2,tuple(_sense_point(x,11.2,14.7)),'Controller',0,'metal',axis=(0,1,0),internal=True)
        m.ring(key+'MotorMagnet','Trigger motor permanent-magnet ring',2.95,2.55,7,tuple(_sense_point(x,12,14.7)),'Controller',0,'black',axis=(0,1,0),internal=True)
        m.ring(key+'MotorCoil','Trigger motor winding envelope',2.4,2.2,6.5,tuple(_sense_point(x,12.2,14.7)),'Controller',0,'copper',axis=(0,1,0),internal=True)
        m.ring(key+'MotorRotor','Trigger motor rotor core',2.1,.6,7,tuple(_sense_point(x,12,14.7)),'Controller',0,'metal',axis=(0,1,0),internal=True)
        m.cyl(key+'MotorShaft','Trigger motor output spindle',.45,14,tuple(_sense_point(x,11,14.7)),'Controller',0,'metal',axis=(0,1,0),internal=True)
        for j,y in enumerate([10.6,19.5]):m.ring(key+'MotorEnd'+str(j),'Trigger motor end bearing cap',3.45,.7,.4,tuple(_sense_point(x,y,14.7)),'Controller',0,'black',axis=(0,1,0),internal=True)
        # A separate cam and follower illustrate the variable-resistance force path.
        cam=Part.makeCylinder(5,1.3).cut(Part.makeCylinder(1.1,1.6,V(0,0,-.1)))
        cam=cam.cut(Part.makeBox(12,5,2,V(-6,-6,-.2)))
        m.feature(key+'ResistanceCam','Adaptive resistance cam study',axial(cam,31,23,1.3),'Controller',2,'black',True)
        arm=m.rr(1.2,7,.9,tuple(_sense_point(x+2,37,27.5)),.25)
        m.feature(key+'FeedbackArm','Trigger resistance follower arm study',arm,'Controller',3,'white',True)
        spring=_helical_spring(1.5,.5,1.4,.15)
        spring=axial(spring,41,24,-2.8)
        clearance=Part.makeCylinder(1.9,2.1,_sense_point(x-3.1,41,24),V(1,0,0))
        for target in [key+'Trigger',key+'TriggerCarrier']:m.cut(target,clearance,'Torsion-return spring seat clearance').Refine=False
        m.feature(key+'ReturnSpring','Trigger torsion-return spring study',spring,'Controller',3,'metal',True)
        # The side sensing board is independently removable from the gear carrier.
        m.box(key+'SensorPCB','Adaptive trigger sensing PCB',14,19,.7,tuple(_sense_point(x+6.4,31,23)),'Controller',2,'sensepcb',.5,True,orient=g.rotation((1,0,0),(0,0,1)))
        m.ring(key+'AngleSensor','Trigger angle sensor housing study',3.3,1.15,1.5,tuple(_sense_point(x+4.7,31,23)),'Controller',2,'black',axis=(1,0,0),internal=True)
        m.cyl(key+'SensorRotor','Angle sensor internal rotor',.95,1.1,tuple(_sense_point(x+4.9,31,23)),'Controller',2,'white',axis=(1,0,0),internal=True)
        for j,(y,z) in enumerate([(26,16),(31,16),(32.5,30)]):
            m.box(key+'SensorIC'+str(j),'Trigger-board electronic package study',3,2,.8,tuple(_sense_point(x+7.3,y,z)),'Controller',2,'black',.2,True,orient=g.rotation((1,0,0),(0,0,1)))
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=28
    m.checkpoint(28,'dualsense_adaptive_trigger_motors_worms_and_sensors','补齐左右自适应扳机电机、独立转子/线圈/磁体、连续螺旋蜗杆、减速齿轮、阻力凸轮、随动臂、回位弹簧和传感器板。齿形、传动间隙与布置为静态学习示意，不声称完成运动学或力反馈验证。')
    m.snapshot('28_dualsense_adaptive_triggers',assemblies=['Controller'],exclude=['SenseFront','SenseBack','SenseTrim','SenseTouchpad','SenseTouchLight','SenseTouchPCB'],normal=(.2,.5,1.7))


STAGES[28]=stage28


def stage29(m):
    from .atari2600 import _rounded_route
    m.native('SenseBatteryTray','Native rechargeable-cell support tray',52,34,2,13.2,tuple(_sense_point(0,20,4.2)),'Controller',-3,'ctrlcream')
    m.cut('SenseBatteryTray',m.rr(49.8,31.8,13,tuple(_sense_point(0,20,5.2)),1.5),'Open battery cradle').Refine=False
    m.cut('SenseBatteryTray',[Part.makeCylinder(17.1,14,_sense_point(x,-12,4)) for x in [-28,28]]+[Part.makeCylinder(2.3,4,_sense_point(0,37,13.8))],'Battery cradle clearance around stick pods and rear board post').Refine=False
    m.native('SenseBattery','1500 mAh original battery envelope study',48,30,2,10.5,tuple(_sense_point(0,20,5.4)),'Controller',-2,'battery')
    m.label('SenseBatteryMark','1500 mAh STUDY',2,tuple(_sense_point(-19,19,15.925)),'Controller',-1,'white')
    m.box('SenseBatteryStrap','Battery retaining strap study',5,29,.4,tuple(_sense_point(0,20,16.2)),'Controller',-1,'black',.3,True)
    socket=m.rr(5,3,2.5,tuple(_sense_point(25,10,22.3)),.3).cut(m.rr(3.8,1.8,2.2,tuple(_sense_point(25,10,23)),.15))
    m.feature('SenseBatterySocket','Controller battery connector body',socket,'Controller',1,'white',True)
    for i,dx in enumerate([-.6,.6]):
        m.box('SenseBatteryContact'+str(i),'Separate battery socket contact',.25,1,.15,tuple(_sense_point(25+dx,10,23.25)),'Controller',1,'gold',.03,True)
        m.cut('SensePCB',Part.makeCylinder(.5,2,_sense_point(25+dx,9,20.5)),'Battery lead insulated board passage').Refine=False
        m.cut('SenseBatterySocket',Part.makeCylinder(.5,2,_sense_point(25+dx,9,22)),'Battery lead passage into the connector').Refine=False
        points=[_sense_point(22+dx,30,16.2),_sense_point(25+dx,30,18.5),_sense_point(25+dx,9,18.5),_sense_point(25+dx,9,23.8)]
        sh=_rounded_route(points,.5,.3);sh.check(True)
        m.feature('SenseBatteryLead'+str(i),'Insulated rechargeable-cell lead',sh,'Controller',0,'red' if i==0 else 'black',True)
    for side,name in [(-1,'Left'),(1,'Right')]:
        key='Sense'+name+'Haptic';n=V(side*.25,-.95,-.18);n.normalize();p=_sense_point(side*55,-9,20)
        def pos(t):return tuple(p+n*t)
        axis=tuple(n)
        m.ring(key+'Can','Voice-coil haptic actuator outer can',6.9,6.5,22.8,pos(.6),'Controller',-2,'metal',axis=axis,internal=True)
        for j,t in enumerate([0,23.5]):m.cyl(key+'End'+str(j),'Haptic actuator end plate',6.7,.5,pos(t),'Controller',-2,'metal',axis=axis,internal=True)
        m.ring(key+'Magnet','Haptic actuator magnetic circuit',5.8,3.8,18,pos(3),'Controller',-2,'black',axis=axis,internal=True)
        m.ring(key+'Coil','Haptic voice-coil winding envelope',3.5,2.5,13,pos(5),'Controller',-2,'copper',axis=axis,internal=True)
        m.cyl(key+'Mass','Independent haptic moving mass study',2.2,13.8,pos(5),'Controller',-2,'metal',axis=axis,internal=True)
        for j,t in enumerate([2,22]):m.ring(key+'Spring'+str(j),'Haptic suspension diaphragm study',5.9,2.3,.12,pos(t),'Controller',-2,'metal',axis=axis,internal=True)
        for j,t in enumerate([6,17]):m.ring(key+'Band'+str(j),'Haptic actuator damping band',7.3,7,1.4,pos(t),'Controller',-2,'rubber',axis=axis,internal=True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=29
    m.checkpoint(29,'dualsense_battery_and_two_voice_coil_haptics','加入原版 1500 mAh 电池包络、原生托架、固定带和独立接线；两侧握柄建立音圈反馈执行器、磁路、线圈、动子、悬置片和减振圈。内部截面为工作原理学习近似。')
    m.snapshot('29_dualsense_power_haptics',assemblies=['Controller'],exclude=['SenseBack','SenseFront','SenseTrim','SenseTouchpad','SenseTouchLight','SenseTouchPCB'],normal=(.2,-.5,2))


STAGES[29]=stage29


def stage30(m):
    rear=g.rotation((0,1,0),(0,0,1));front=g.rotation((0,-1,0),(0,0,1))
    aperture=m.rr(10,4.5,12,tuple(_sense_point(0,39,29)),1.8,rear)
    for key in ['SenseFront','SenseBack']:m.cut(key,aperture,'Rear USB-C receptacle opening').Refine=False
    shield=m.rr(9.2,3.6,8,tuple(_sense_point(0,41,29)),1.7,rear).cut(m.rr(8.5,2.9,8.4,tuple(_sense_point(0,40.8,29)),1.35,rear))
    m.feature('SenseUSBShield','Controller USB-C metal receptacle',shield,'Controller',2,'metal')
    m.box('SenseUSBCarrier','USB-C rear insulating carrier',8.1,2.6,.7,tuple(_sense_point(0,41,29)),'Controller',2,'black',1.2,True,orient=rear)
    m.box('SenseUSBTongue','Controller reversible USB-C tongue',6.9,5.7,.6,tuple(_sense_point(0,45,28.7)),'Controller',2,'black',.2)
    for side in [-1,1]:
        for i in range(12):
            m.box('SenseUSBContact'+str(side)+'_'+str(i),'Separate controller USB-C contact',.24,3.8,.08,tuple(_sense_point((i-5.5)*.5,45.8,29.34 if side==1 else 28.54)),'Controller',2,'gold',.02,True)
    m.native('SenseUSBPCB','Rear interface board envelope study',16,9,1,.8,tuple(_sense_point(0,40,24)),'Controller',1,'sensepcb')
    for i,x in enumerate([-5.6,5.6]):
        m.box('SenseUSBMount'+str(i),'USB receptacle mounting foot',.45,2.2,2.1,tuple(_sense_point(x,41,24.9)),'Controller',1,'metal',.08,True)
    jack=m.rr(6,6,9,tuple(_sense_point(0,-5,29)),.8,front).cut(Part.makeCylinder(1.85,9.5,_sense_point(0,-4.8,29),V(0,-1,0)))
    m.feature('SenseAudioJack','Controller four-pole headset socket',jack,'Controller',1,'black',True)
    m.ring('SenseAudioRim','Headset socket front rim',2.6,1.85,1.1,tuple(_sense_point(0,-15.2,29)),'Controller',2,'metal',axis=(0,1,0))
    for key in ['SenseFront','SenseBack','SenseTrim']:
        m.cut(key,m.rr(6.5,6.5,12,tuple(_sense_point(0,-4,29)),1,front),'Headset socket front-edge aperture').Refine=False
    for i,(x,z) in enumerate([(-1.4,29),(1.4,29),(0,27.6),(0,30.4)]):
        m.cyl('SenseAudioContact'+str(i),'Independent headset spring-contact tip',.15,1.3,tuple(_sense_point(x,-12.8+i*1.8,z)),'Controller',1,'gold',axis=(0,1,0),internal=True)
    for i,x in enumerate([-5,5]):
        m.cut('SenseBack',m.rr(2,3.2,3,tuple(_sense_point(x,-10,28.8)),.3,front),'Charging contact aperture').Refine=False
        m.box('SenseChargeContact'+str(i),'Bottom charging contact',1.5,.3,2.5,tuple(_sense_point(x,-12.4,27.5)),'Controller',2,'gold',.1)
    for i,(x,y,z) in enumerate([(0,-4.5,43.8),(14,5,3.25)]):
        m.box('SenseMicrophone'+str(i),'Controller MEMS microphone study',2,2,.6,tuple(_sense_point(x,y,z)),'Controller',2,'metal',.2,True)
    m.cut('SenseTrim',Part.makeCylinder(.4,7,_sense_point(0,-4.5,43)),'Front microphone acoustic opening').Refine=False
    m.cut('SenseBack',Part.makeCylinder(.45,3.3,_sense_point(14,5,0)),'Underside microphone acoustic opening').Refine=False
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=30
    m.checkpoint(30,'dualsense_usbc_audio_charging_and_microphones','补齐手柄 USB-C 外壳、舌片与 24 个独立触点、接口板及安装脚、耳机插座及弹片、底部充电触点和前后麦克风开口。接口内部尺寸与板层为学习近似。')
    m.snapshot('30_dualsense_interfaces',assemblies=['Controller'],normal=(.2,.6,1.6))


STAGES[30]=stage30


def stage31(m):
    from .atari2600 import _rounded_route
    def socket(key,x,y,width,count,z=22.3):
        body=m.rr(width,3,2.4,tuple(_sense_point(x,y,z)),.25).cut(m.rr(width-1.2,1.8,2,tuple(_sense_point(x,y,z+.7)),.12))
        m.feature(key,'Separate controller harness socket',body,'Controller',2,'white',True)
        for i in range(count):
            m.box(key+'Contact'+str(i),'Independent controller socket contact',.2,1,.15,tuple(_sense_point(x+(i-(count-1)/2)*(width-2)/max(1,count-1),y,z+.85)),'Controller',2,'gold',.02,True)
    socket('SenseTouchMainSocket',0,32,8,8)
    socket('SenseFilmMainSocket',-10,30,7,6)
    touch=[(0,32,23.65),(0,32,34),(0,44,34),(0,44,43.3),(0,42,44.8)]
    film=[(-10,30,23.65),(-10,30,34),(-10,24,35.8)]
    for key,points,width,endx,endy,z in [('Touch',touch,6,0,42,42.7),('Film',film,4.8,-10,24,34.0)]:
        world=[tuple(_sense_point(*p)) for p in points]
        m.feature('Sense'+key+'Ribbon','Continuous controller '+key.lower()+' flex study',_folded_ribbon(world,width,.14),'Controller',3,'white',True)
        socket('Sense'+key+'EndSocket',endx,endy,width+1.5,6,z)
        m.cut('Sense'+key+'EndSocket',_folded_ribbon(world,width+.5,.5),'Controller ribbon approach clearance').Refine=False
    for side,name in [(-1,'Left'),(1,'Right')]:
        socket('Sense'+name+'TriggerSocket',side*39,29,7,6)
        points=[(side*39,29,23.65),(side*39,29,35.5),(side*52+8.5,29,35.5),(side*52+8.5,29,28.5),(side*52+7.5,29,28.5)]
        world=[_sense_point(*p) for p in points]
        ribbon=_folded_ribbon([(p.y,-p.x,p.z) for p in world],4,.14);ribbon.rotate(V(),V(0,0,1),90)
        m.feature('Sense'+name+'TriggerRibbon','Adaptive-trigger signal flex study',ribbon,'Controller',3,'white',True)
        passage=_folded_ribbon([(p.y,-p.x,p.z) for p in world],4.4,.4);passage.rotate(V(),V(0,0,1),90)
        m.cut('Sense'+name+'TriggerSocket',passage,'Trigger flex entry clearance').Refine=False
        socket('Sense'+name+'HapticSocket',side*40,4.5,5,2)
        for i,dx in enumerate([-.6,.6]):
            z=31.2+i*.7
            points=[_sense_point(side*55+dx,-8,27.6),_sense_point(side*55+dx,-3+side*(i-.5)*.7,z),_sense_point(side*40+dx,2.5+side*(i-.5)*.7,z),_sense_point(side*40+dx,2.5+side*(i-.5)*.7,25.4),_sense_point(side*40+dx,4.5,25.4),_sense_point(side*40+dx,4.5,23.65)]
            sh=_rounded_route(points,.4,.22);sh.check(True)
            m.feature('Sense'+name+'HapticLead'+str(i),'Separate insulated haptic actuator lead',sh,'Controller',2,'red' if i==0 else 'black',True)
    # The small interface-board flex approaches the main PCB from its clear central rear edge.
    points=[tuple(_sense_point(6.5,40,23.7)),tuple(_sense_point(6.5,40,22.9)),tuple(_sense_point(6.5,37.5,22.9))]
    m.feature('SenseUSBBoardFlex','Rear interface board interconnect study',_folded_ribbon(points,2.5,.12),'Controller',1,'white',True)
    # Keep screw heads in exposed local pockets; preserve all housing construction history.
    for i,(x,y,z) in enumerate([(-67,-40,15),(67,-40,15),(-39,37,12),(39,37,12)]):
        hole=Part.makeCylinder(1,22,_sense_point(x,y,z-1))
        for key in ['SenseBack','SenseFront']:m.cut(key,hole,'Controller case fixing shaft clearance').Refine=False
        m.cut('SenseBack',Part.makeCylinder(1.9,z+.8,_sense_point(x,y,0)),'Rear screw-head access counterbore').Refine=False
        m.ring('SenseCasePost'+str(i),'Controller case screw post',2.2,.85,6,tuple(_sense_point(x,y,z+1)),'Controller',-2,'ctrlcream',internal=True)
        m.screw('SenseCaseScrew'+str(i),tuple(_sense_point(x,y,z+.35)),'Controller',-3,length=6.2,radius=1.65)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=31
    m.checkpoint(31,'dualsense_flexes_haptic_leads_and_case_fixings','补齐触摸板、按键膜、左右扳机和接口板排线、板端插座与独立触点、音圈线束及四组外壳固定件。线路径与固定细节为静态结构学习近似。')
    m.snapshot('31_dualsense_connected_internals',assemblies=['Controller'],exclude=['SenseBack','SenseFront','SenseTrim','SenseTouchpad','SenseTouchLight'],normal=(.2,-.5,2))


STAGES[31]=stage31


def stage32(m):
    from .atari2600 import _rounded_route
    from .wiiu import _hdmi_shape
    rear=g.rotation((0,1,0),(0,0,1))
    m.box('ACWallPlug','Two-flat-blade AC plug study',23,17,11,(220,100,0),'Accessories',0,'black',1.7)
    for i,x in enumerate([213.8,226.2]):m.box('ACWallBlade'+str(i),'Flat AC blade study',1.4,6.2,12.5,(x,100,11.1),'Accessories',0,'metal',.1)
    points=[V(220,91.3,5.5),V(220,55,5.5),V(320,55,8),V(320,20,8),V(292.2,20,8)]
    m.feature('ACCord','Mains cord display length',_rounded_route(points,7,1.8),'Accessories',0,'black')
    m.box('ACDeviceGrip','Figure-eight connector grip',24,12,10,(280,20,3),'Accessories',0,'black',1.3)
    lobes=[Part.makeCylinder(3.15,10,V(267.8,y,8),V(-1,0,0)) for y in [15.8,24.2]]
    bridge=Part.makeBox(1.2,8.4,5.4,V(266.6,15.8,5.3))
    head=bridge.multiFuse(lobes)
    holes=[Part.makeCylinder(1.25,10.5,V(268,y,8),V(-1,0,0)) for y in [15.8,24.2]]
    m.feature('ACDeviceHead','C7-style two-position connector study',head.cut(Part.makeCompound(holes)),'Accessories',0,'black')
    for i,y in enumerate([15.8,24.2]):m.ring('ACDeviceContact'+str(i),'Device mains socket contact study',1.15,1.02,6,(265.5,y,8),'Accessories',0,'metal',axis=(-1,0,0))
    points=[V(250,-258.2,6),V(250,-337,6),V(350,-337,6),V(350,-258.2,6)]
    m.feature('HDMICable','HDMI cable display length',_rounded_route(points,14,2.4),'Accessories',0,'black')
    for i,x in enumerate([250,350]):
        m.box('HDMIGrip'+str(i),'HDMI connector overmould',20,24,10,(x,-246,1),'Accessories',0,'black',2)
        m.cyl('HDMIRelief'+str(i),'HDMI cable strain relief',2.7,6,(x,-258.1,6),'Accessories',0,'black',axis=(0,-1,0))
        m.cut('HDMIRelief'+str(i),Part.makeCylinder(2.45,6.4,V(x,-257.9,6),V(0,-1,0)),'Strain-relief cable bore').Refine=False
        outer=_hdmi_shape(14,5,9);inner=_hdmi_shape(12.8,3.8,9.4);inner.translate(V(0,0,-.2))
        shape=outer.cut(inner);shape.Placement=App.Placement(V(x,-233.8,6),rear)
        m.feature('HDMIHead'+str(i),'HDMI Type A metal plug shell',shape,'Accessories',0,'metal')
        m.box('HDMIPlugTongue'+str(i),'HDMI plug contact carrier',10.9,7,.6,(x,-229,5.7),'Accessories',0,'black',.2)
        for row,n in enumerate([10,9]):
            for j in range(n):m.box(f'HDMIPlugPin{i}_{row}_{j}','HDMI Type A plug contact',.32,5,.06,(x+(j-(n-1)/2)*1.02,-229,5.56 if row==0 else 6.39),'Accessories',0,'gold',.03)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=32
    m.checkpoint(32,'original_ac_cord_and_nineteen_contact_hdmi_cable','补齐原配双片电源插头与八字设备端、两端十九接点 HDMI 连接线及独立护线套。沿用已验证的同系列连接结构，并使电源端示意针距与本机插口一致；线长为展示近似。')
    m.snapshot('32_ac_hdmi_accessories_review',assemblies=['Accessories'],normal=(.2,-.5,2))



STAGES[32]=stage32


def stage33(m):
    from .atari2600 import _rounded_route
    rear=g.rotation((0,1,0),(0,0,1))
    points=[V(230,-91.7,6),V(230,-177,6),V(270,-177,6),V(270,-91.7,6)]
    m.feature('USBChargeCable','Original USB-A to USB-C cable display length',_rounded_route(points,7,1.5),'Accessories',0,'black')
    m.box('USBAPlugGrip','USB-A cable overmould',18,23,10,(230,-80,1),'Accessories',0,'black',1.6)
    m.box('USBCPlugGrip','USB-C cable overmould',12,19,8,(270,-82,2),'Accessories',0,'black',1.3)
    for i,x in enumerate([230,270]):
        sh=Part.makeCylinder(1.9,6,V(x,-91.6,6),V(0,-1,0)).cut(Part.makeCylinder(1.55,6.4,V(x,-91.4,6),V(0,-1,0)))
        m.feature('USBChargeRelief'+str(i),'Charging cable strain-relief sleeve',sh,'Accessories',0,'black')
    sh=m.rr(12,4.5,12,(230,-68.3,6),.3,rear).cut(m.rr(11.4,3.9,12.4,(230,-68.5,6),.15,rear))
    m.feature('USBAPlugShield','USB-A cable plug metal shell',sh,'Accessories',0,'metal')
    m.box('USBAPlugStop','USB-A rear insulating stop',10.8,.65,3.3,(230,-67.9,4.35),'Accessories',0,'black',.15,True)
    m.box('USBAPlugTongue','USB-A four-contact tongue',9.2,7,1,(230,-62.7,5),'Accessories',0,'black',.15)
    for i in range(4):m.box('USBAPlugContact'+str(i),'Separate USB-A plug contact',.85,5,.1,(230+(i-1.5)*2,-62.7,6.1),'Accessories',0,'gold',.05,True)
    sh=m.rr(8.3,2.5,7,(270,-72.3,6),1.2,rear).cut(m.rr(7.7,1.9,7.4,(270,-72.5,6),.9,rear))
    m.feature('USBCPlugShield','Reversible USB-C cable plug shell',sh,'Accessories',0,'metal')
    m.box('USBCPlugStop','USB-C plug rear insulator',7.3,1.5,.65,(270,-71.9,6),'Accessories',0,'black',.65,True,orient=rear)
    for side,z,cz in [('Lower',5.15,5.5),('Upper',6.55,6.42)]:
        m.box('USBCPlugRail'+side,'USB-C plug insulating contact rail',6.3,4.8,.3,(270,-68.4,z),'Accessories',0,'black',.1,True)
        for i in range(12):m.box('USBCPlugContact'+side+str(i),'Separate USB-C cable plug contact',.21,3.8,.08,(270+(i-5.5)*.5,-68.4,cz),'Accessories',0,'gold',.02,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=33
    m.checkpoint(33,'original_usb_a_to_usb_c_accessory','加入原配 USB-A 至 USB-C 连接线，建立双端包胶、护线套、独立金属壳、绝缘件和 4/24 个分离触点。原版套装包含底座、DualSense、AC、HDMI 和 USB 线；不加入未附送的耳机。线长为缩短展示近似。')
    m.snapshot('33_original_connection_kit',assemblies=['Accessories'],normal=(.2,-.5,2))


STAGES[33]=stage33


def finalize(model):
    from .deliver import finalize as shared_finalize
    # Preserve trimming pcurves: otherwise two thin, pipe-cut fins lose STEP fidelity.
    settings=App.ParamGet('User parameter:BaseApp/Preferences/Mod/Part/General')
    previous=settings.GetInt('WriteSurfaceCurveMode',1)
    Part.setStaticValue('write.surfacecurve.mode',1)
    try:
        result=shared_finalize(model)
        model.snapshot("final_front",normal=(.2,-1.5,.7),assemblies=model.profile["envelope_groups"])
        model.snapshot("final_hero",normal=(.3,-.7,2.3),assemblies=result[0]["handheld_groups"])
        model.doc.save()
        return result
    finally:
        Part.setStaticValue('write.surfacecurve.mode',previous)


def stage34(m):
    from .atari2600 import _rounded_route
    tails=[]
    for row,y,z in [('Lower',40.4,28.54),('Upper',39.6,29.34)]:
        for i in range(12):
            x=(i-5.5)*.5
            foot=Part.makeBox(.18,.6,.14,_sense_point(x-.09,y-.3,24.95))
            stem=Part.makeBox(.18,.18,z+.06-25.03,_sense_point(x-.09,y-.09,25.03))
            arm=Part.makeBox(.18,43.8-y+.09,.08,_sense_point(x-.09,y-.09,z))
            sh=foot.fuse(stem).fuse(arm).removeSplitter()
            m.feature('SenseUSBTail'+row+str(i),'Separate formed USB-C board terminal',sh,'Controller',2,'gold',True);tails.append(sh)
    m.cut('SenseUSBCarrier',tails,'USB-C board-terminal moulded channels').Refine=False
    m.cut('SenseTouchLight',m.rr(58,29,1.1,tuple(_sense_point(0,29,47)),2.8),'Open central touch-click mechanism inside the edge light guide').Refine=False
    m.box('SenseTouchClickSwitch','Touchpad tactile-click switch',6,4,1,tuple(_sense_point(0,29,46.1)),'Controller',4,'black',.4,True)
    m.cyl('SenseTouchClickActuator','Touchpad click actuator',.8,.5,tuple(_sense_point(0,29,47.2)),'Controller',5,'white',internal=True)
    for i,x in enumerate([-30,30]):m.box('SenseTouchLED'+str(i),'Touchpad edge-light emitter study',.8,2,.5,tuple(_sense_point(x,29,46.3)),'Controller',4,'ps5blue',.1,True)
    socket=m.rr(4,3,2.4,tuple(_sense_point(0,8,22.3)),.25).cut(m.rr(2.8,1.8,2,tuple(_sense_point(0,8,23)),.12))
    m.feature('SenseSpeakerSocket','Controller speaker wire socket',socket,'Controller',2,'white',True)
    passages=[]
    for i,x in enumerate([-1,1]):
        m.box('SenseSpeakerContact'+str(i),'Independent speaker socket contact',.2,1,.15,tuple(_sense_point(x,8,23.15)),'Controller',2,'gold',.02,True)
        points=[_sense_point(x,4.8,41),_sense_point(x,3.5,36),_sense_point(x,3.5,25),_sense_point(x,8,23.8)]
        sh=_rounded_route(points,.35,.18);sh.check(True)
        m.feature('SenseSpeakerLead'+str(i),'Separate insulated loudspeaker lead',sh,'Controller',2,'red' if i==0 else 'black',True)
        passages.append(_rounded_route(points,.55,.42))
    for key in ['SenseContactCarrier','SenseContactFilm','SenseSpeakerSocket']:m.cut(key,passages,'Loudspeaker lead passage through the button carrier and socket').Refine=False
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=34
    m.checkpoint(34,'dualsense_terminal_tails_touch_click_and_speaker_connection','补齐 USB-C 成形焊接端子、触摸板按下开关、边缘发光器件和独立扬声器线束，并加工接点膜支架的穿线通道。完成主机、底座、DualSense 与原配连接线的结构建模，随后执行完整交付验证。')
    m.snapshot('34_dualsense_complete',assemblies=['Controller'],normal=(.2,-.5,2.4))


STAGES[34]=stage34
