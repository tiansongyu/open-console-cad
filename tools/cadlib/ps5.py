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
