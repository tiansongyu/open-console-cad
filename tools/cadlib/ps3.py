"""CECHA00 exterior / early 60 GB family internals: staged editable study."""
import FreeCAD as App
import Part
from .core import V
from . import geometry as g


def _arch_curve(depth,front,rear,crown):
    curve=Part.BezierCurve()
    curve.setPoles([V(-depth/2,front),V(0,2*crown-(front+rear)/2),V(depth/2,rear)])
    return curve


def _crown(m,key,label,width,depth,front,rear,crown,thickness,layer,material):
    rotation=App.Rotation(V(0,1,0),V(0,0,1),V(1,0,0),'ZXY')
    sections=[]
    for i,(x,inset,drop) in enumerate([(-width/2,9,4),(-width/2+11,0,0),(0,0,0),(width/2-11,0,0),(width/2,9,4)]):
        c=_arch_curve(depth-inset*2,front-drop,rear-drop,crown-drop)
        poles=c.getPoles();inner=Part.BezierCurve();inner.setPoles([p-V(0,thickness) for p in reversed(poles)])
        sk=m.doc.addObject('Sketcher::SketchObject',key+'Section'+str(i));sk.Label=label+' · editable arched section'
        sk.addGeometry([c.toBSpline(),Part.LineSegment(poles[-1],poles[-1]-V(0,thickness)),inner.toBSpline(),Part.LineSegment(poles[0]-V(0,thickness),poles[0])],False)
        sk.Placement=App.Placement(V(x,0,0),rotation);sk.setExpression('Placement.Base.x',f'Parameters.Width * {x/325:.12g}')
        m.group('Construction').addObject(sk);sections.append(sk)
    loft=m.doc.addObject('Part::Loft',key+'Loft');loft.Label=label;loft.Sections=sections;loft.Solid=True;loft.Ruled=True;loft.MaxDegree=3
    m.doc.recompute();loft.Shape.check(True)
    for sk in sections:sk.Visibility=False
    return m.register(loft,key,'Body',layer,material)


def _end_wall(m,key,x):
    # Separate moulded end wall with an editable curved outline and extrusion.
    c=_arch_curve(247,47.5,45.5,90)
    pts=c.getPoles();z=42.5
    sk=m.doc.addObject('Sketcher::SketchObject',key+'Outline')
    sk.addGeometry([c.toBSpline(),Part.LineSegment(pts[-1],V(pts[-1].x,z)),Part.LineSegment(V(pts[-1].x,z),V(pts[0].x,z)),Part.LineSegment(V(pts[0].x,z),pts[0])],False)
    sk.Placement=App.Placement(V(x,0,0),App.Rotation(V(0,1,0),V(0,0,1),V(1,0,0),'ZXY'))
    sk.setExpression('Placement.Base.x',f'Parameters.Width * {x/325:.12g}');m.group('Construction').addObject(sk)
    ex=m.doc.addObject('Part::Extrusion',key+'Extrusion');ex.Base=sk;ex.DirMode='Normal';ex.LengthFwd=1.8;ex.Solid=True
    m.doc.recompute();sk.Visibility=False
    return m.register(ex,key,'Frame',1,'black')


def stage01(m):
    m.colors.update(ps3gloss=(.095,.10,.115),black=(.065,.07,.08),chrome=(.66,.68,.72))
    m.params.set('A3','Depth (Y)');m.params.set('A4','Height (Z)')
    m.native('LowerCase','Original stepped lower case',309,247,10,42,(0,0,0),'Body',-5,'black',expr={'Width':'Parameters.Width - 16 mm'})
    m.cut('LowerCase',m.rr(304.5,242.5,43,(0,0,2.3),8),'Open lower enclosure interior').Refine=False
    _crown(m,'GlossCrown','Removable continuous glossy arched top',325,274,55,53,98,2,7,'ps3gloss')
    _crown(m,'InnerHood','Separate arched inner enclosure',318,265,51.2,49.2,94.1,1.8,5,'black')
    _end_wall(m,'LeftEndWall',-154.2);_end_wall(m,'RightEndWall',152.4)
    m.native('FrontFascia','Upper slot-loading front fascia',302,2.0,.7,12,(0,-133.8,40.5),'Frame',3,'ps3gloss')
    m.native('RearFascia','Upper rear closure',302,2.0,.7,4,(0,129.4,40.5),'Frame',1,'black')
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=1
    m.checkpoint(1,'native_arched_launch_enclosure','以日本 CECHA00 首发 60GB 外观建立 325×274×98 mm 参考包络，独立亮面弧形顶盖、内罩、原生下壳和端壁；曲面采用可编辑草图放样，局部曲率和壁厚为照片指导近似。后续加工四 USB、读卡盖、吸入盘口和后部接口。')
    m.snapshot('01_original_enclosure_review',normal=(.4,-1.4,1.0))


STAGES={1:stage01}


def stage02(m):
    front=g.rotation((0,-1,0),(0,0,1));rear=g.rotation((0,1,0),(0,0,1))
    # Card-reader flap is cut from the same native arched skin, retaining its curvature.
    skin=m.parts['GlossCrown'].Shape.copy()
    lid_tool=Part.makeBox(121.4,52.4,110,V(-147.2,-138,0))
    lid=skin.common(Part.makeBox(120.8,52.1,110,V(-146.9,-138,0)))
    m.cut('GlossCrown',lid_tool,'Separate original 60 GB card-reader cover').Refine=False
    m.feature('CardReaderFlap','Original curved card-reader flap',lid,'FrontIO',8,'ps3gloss')
    m.cut('InnerHood',Part.makeBox(118,49,110,V(-145.5,-135,0)),'Reader access opening under the hinged flap').Refine=False
    m.box('FrontChrome','Original chrome front edge',300,1.5,4,(0,-135.8,38.8),'Frame',4,'chrome',.35)
    slot=m.rr(127,3.2,14,(77,-126,47.7),.6,front)
    m.cut('FrontFascia',slot,'Original slot-loading Blu-ray entrance').Refine=False
    for i,z in enumerate([46.4,48.55]):m.box('DiscBrush'+str(i),'Opposed slot dust lip',125,2,.5,(77,-132.7,z),'FrontIO',2,'black',.1)
    for i,x in enumerate([-119,-96,-73,-50]):
        m.cut('LowerCase',m.rr(15.3,7.8,15,(x,-113,22),.55,front),'Four original USB apertures '+str(i+1)).Refine=False
    for key,x,w,h in [('HDMI',9,16.3,7.4),('LAN',33,17,15),('OpticalAudio',57,12,11.5),('AVMulti',82,28,11),('ACInlet',124,25,18.5)]:
        m.cut('LowerCase',m.rr(w,h,16,(x,111,22),.65,rear),'Original rear '+key+' opening').Refine=False
    m.cut('LowerCase',m.rr(20,8,14,(124,113,36),.7,rear),'Rear master switch aperture').Refine=False
    m.cut('LowerCase',Part.makeBox(14,101,20,V(-159,-94,8)),'Side removable hard-drive tray opening').Refine=False
    m.box('HDDDoor','Separate side HDD access door',1.5,99,18.6,(-154.1,-43.5,8.6),'Body',-1,'black',.5)
    vents=[Part.makeBox(3.2,10,10,V(x,118,z)) for x in range(-131,-2,7) for z in [9,26]]
    m.cut('LowerCase',vents,'Rear exhaust slots through the lower shell').Refine=False
    vents=[Part.makeBox(12,3.6,22,V(148,y,11)) for y in range(-101,105,8)]
    m.cut('LowerCase',vents,'Open right-side inlet grille').Refine=False
    vents=[Part.makeBox(3,11,7,V(x,-128,9)) for x in range(-19,138,6)]
    m.cut('LowerCase',vents,'Lower front ventilation grille').Refine=False
    # Separate touch surfaces on the front-right lip, rather than mechanical push buttons.
    for key,x,z in [('Power',145,50.2),('Eject',145,44.3)]:
        m.box(key+'TouchSurface',key+' capacitive-control marking plate',5.8,.3,2.1,(x,-135, z),'Controls',4,'chrome',.3)
    for i,(x,material) in enumerate([(-31,'led'),(-25,'red')]):m.box('FrontStatus'+str(i),'Original front status-light window',1.7,.4,1.2,(x,-123.8,22),'Controls',1,material,.25)
    for i,(x,y) in enumerate([(-119,-92),(119,-92),(-119,92),(119,92)]):m.box('Foot'+str(i),'Separate rubber enclosure foot',16,12,1.2,(x,y,-1.2),'Frame',-7,'rubber',3)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=2
    m.checkpoint(2,'launch_card_flap_ports_and_open_vents','从原生弧形上盖分出首发读卡盖，加入镀铬前缘、吸入盘口与防尘唇、触控面和状态窗；加工四 USB、原版后部接口、侧置 HDD 仓及贯通前/侧/后通风孔。局部尺寸为结构近似，接插件和内部器件分轮补齐。')
    m.snapshot('02_original_front',normal=(.25,-1.6,.65))
    m.snapshot('02_original_back',normal=(.3,1.6,.65))


STAGES[2]=stage02


def stage03(m):
    from .ps5 import _usb_a
    rear=g.rotation((0,1,0),(0,0,1))
    for i,x in enumerate([-119,-96,-73,-50]):_usb_a(m,'FrontUSB'+str(i),x,-110.5,22,True,False)
    # HDMI: independent metal shell, back wall, tongue and nineteen contacts.
    x,y,z=9,110.8,22
    def hdmi(w,h,length,dy=0):
        points=[(-w/2,-h/2+1.1),(-w/2+1.1,-h/2),(w/2-1.1,-h/2),(w/2,-h/2+1.1),(w/2,h/2),(-w/2,h/2)]
        vs=[V(a,b) for a,b in points];sh=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,0,length));sh.Placement=App.Placement(V(x,y+dy,z),rear);return sh
    m.feature('HDMIShield','Nineteen-contact HDMI metal shield',hdmi(15.5,6.6,12).cut(hdmi(14.8,5.9,12.4,-.2)),'Ports',0,'metal')
    m.box('HDMIBack','HDMI rear insulator',12,.7,4.7,(x,y+.5,z-2.35),'Ports',0,'black',.1,True)
    m.box('HDMITongue','HDMI insulating tongue',11.7,8,.65,(x,y+6.5,z-.325),'Ports',0,'black',.1)
    for side,n in [(1,10),(-1,9)]:
        for i in range(n):m.box('HDMIContact'+str(side)+'_'+str(i),'Separate HDMI connector contact',.27,6,.08,(x+(i-(n-1)/2)*1.08,y+6.8,z+(.38 if side==1 else -.46)),'Ports',0,'gold',.02,True)
    x,y,z=33,110.5,22
    outer=m.rr(16,14,12.2,(x,y,z),.45,rear);inner=m.rr(14.6,12.6,12.6,(x,y-.2,z),.22,rear)
    m.feature('LANShield','Ethernet folded shield',outer.cut(inner),'Ports',0,'metal')
    m.box('LANBack','Ethernet rear carrier',14.2,.75,11.8,(x,y+.5,z-5.9),'Ports',0,'black',.15,True)
    for i in range(8):m.box('LANContact'+str(i),'Independent Ethernet spring contact',.35,7.5,.22,(x+(i-3.5)*1.34,y+6.4,z-3.7),'Ports',0,'gold',.03,True)
    for i,dx in enumerate([-6.2,6.2]):m.box('LANLight'+str(i),'Ethernet indicator lens',1.45,.65,1.45,(x+dx,123.1,z+3.9),'Ports',1,'led',.2)
    x,y,z=57,111,22
    shell=m.rr(11.2,10.7,11.7,(x,y,z),.5,rear).cut(m.rr(8.5,8,11.2,(x,y+1,z),.3,rear))
    m.feature('OpticalSocket','Digital optical socket body',shell,'Ports',0,'black')
    m.box('OpticalShutter','Optical connector spring shutter',7.9,.35,7.4,(x,122.5,z-3.7),'Ports',1,'black',.4)
    m.cyl('OpticalEmitter','Optical output lens',1.2,.4,(x,112.5,z),'Ports',0,'red',axis=(0,1,0),internal=True)
    x,y,z=82,110.5,22
    shell=m.rr(27,10.2,12.4,(x,y,z),2,rear).cut(m.rr(25.4,8.6,12.8,(x,y-.2,z),1.4,rear))
    m.feature('AVShield','Original AV MULTI connector shield',shell,'Ports',0,'metal')
    m.box('AVBack','AV MULTI rear insulator',23.8,.65,7.5,(x,y+.5,z-3.75),'Ports',0,'black',.2,True)
    m.box('AVTongue','AV MULTI insulating tongue',21.6,8.7,1.1,(x,y+6.9,z-.55),'Ports',0,'black',.3)
    for side in [-1,1]:
        for i in range(6):m.box('AVContact'+str(side)+'_'+str(i),'Independent AV MULTI terminal',.75,6.8,.16,(x+(i-2.5)*3.1,y+7,z+(.62 if side==1 else -.78)),'Ports',0,'gold',.04,True)
    x,y,z=124,109.5,22
    shell=m.rr(24,17.6,13.3,(x,y,z),2,rear).cut(m.rr(20.4,14.1,12.2,(x,y+1.4,z),1.7,rear))
    m.feature('ACSocket','Grounded AC inlet insulating shell',shell,'Ports',0,'black')
    for i,(dx,dz) in enumerate([(-5,-3),(5,-3),(0,3.5)]):m.box('ACBlade'+str(i),'Separate AC inlet blade',2.2,8.8,.65,(x+dx,y+6.9,z+dz),'Ports',0,'metal',.1,True)
    m.box('MasterSwitch','Original rear master rocker switch',18.8,4.5,6.8,(124,122.4,32.6),'Controls',1,'black',.7)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=3
    m.checkpoint(3,'four_usb_and_original_rear_connectors','补齐四个 USB 2.0 接口、十九接点 HDMI、八接点 LAN、带门光纤音频、十二接点 AV MULTI、三片式 AC 入口与后部主电源开关；各屏蔽、绝缘件、舌片和接点独立建模，不替换为后期主机接口。')
    m.snapshot('03_rear_interfaces',normal=(.15,1.8,.55))


STAGES[3]=stage03


def stage04(m):
    front=g.rotation((0,-1,0),(0,0,1))
    m.native('CardReaderPCB','Original separate three-format card-reader board',118,29,1.7,1.2,(-86,-111.5,50.6),'FrontIO',3,'pcb')
    holes=[Part.makeCylinder(1.3,2,V(x,y,50.2)) for x in [-143.2,-29] for y in [-123,-100]]
    m.cut('CardReaderPCB',holes,'Card-reader board mounting holes').Refine=False
    for i,(x,y) in enumerate([(x,y) for x in [-143.2,-29] for y in [-123,-100]]):
        m.ring('ReaderPost'+str(i),'Card-reader mounting standoff',2.7,1.35,4,(x,y,46.3),'FrontIO',2,'black',internal=True)
        m.screw('ReaderScrew'+str(i),(x,y,52.4),'FrontIO',3,length=4.5,radius=2,axis=(0,0,-1))
    x,y,z=-118,-101,54.8
    shell=m.rr(46,5.2,24,(x,y,z),.55,front).cut(m.rr(44.6,3.8,24.4,(x,y+.2,z),.25,front))
    m.feature('CFShield','CompactFlash folded metal guide',shell,'FrontIO',4,'metal')
    m.box('CFCarrier','CompactFlash dual-row connector carrier',42,.8,3.2,(x,y-.6,z-1.6),'FrontIO',3,'black',.2,True)
    for row,dz in enumerate([-.8,.8]):
        for i in range(25):m.cyl('CFPin'+str(row)+'_'+str(i),'Separate CompactFlash contact pin',.22,6,(x+(i-12)*1.27,y-1.1,z+dz),'FrontIO',4,'gold',axis=(0,-1,0),internal=True)
    m.box('CFEjectRod','CompactFlash side eject rod',1.5,23,1.2,(-93.1,-112.5,53.8),'FrontIO',4,'metal',.15,True)
    m.box('CFEjectButton','CompactFlash eject button',2.1,3,2.7,(-93.1,-126.2,53),'FrontIO',4,'black',.35)
    for key,x,w,n,pitch in [('SD',-77,27,9,2.5),('MemoryStick',-43,22,10,1.7)]:
        y=-101;z=54.2
        shell=m.rr(w,3.7,24,(x,y,z),.4,front).cut(m.rr(w-1.2,2.5,24.4,(x,y+.2,z),.18,front))
        m.feature(key+'Shield',key+' card guide shield',shell,'FrontIO',4,'metal')
        m.box(key+'Carrier',key+' insulating back carrier',w-2,.7,1.7,(x,y-.55,z-.85),'FrontIO',3,'black',.1,True)
        m.box(key+'Bed',key+' card-slot contact bed',w-2,20,.4,(x,-112.5,53.1),'FrontIO',3,'black',.2,True)
        for i in range(n):m.box(key+'Contact'+str(i),'Separate '+key+' spring terminal',.55,11,.16,(x+(i-(n-1)/2)*pitch,-112.4,53.6),'FrontIO',4,'gold',.025,True)
    # Two independent hinge barrels and pins under the curved lid's rear edge.
    for i,x in enumerate([-139,-39]):
        m.ring('ReaderHinge'+str(i),'Card-cover hinge barrel',1.45,.82,4,(x,-89,76),'FrontIO',6,'black',axis=(1,0,0))
        m.cyl('ReaderHingePin'+str(i),'Separate card-cover hinge pin',.68,6,(x-1,-89,76),'FrontIO',6,'metal',axis=(1,0,0))
    m.box('ReaderController','Card-reader controller IC study',9,7,1.1,(-113,-113,49.3),'FrontIO',2,'black',.4,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=4
    m.checkpoint(4,'three_format_reader_board_and_card_contacts','建立首发 60GB 独立读卡板、四组固定件、CompactFlash 双排 50 针与推出杆、SD 九接点及 Memory Stick 十接点，并加入独立读卡盖铰链。布局依据原版快速参考及拆解，连接器局部尺寸为近似。')
    m.snapshot('04_card_reader_open_review',assemblies=['Body','Frame','FrontIO','Controls'],exclude=['CardReaderFlap','GlossCrown','InnerHood'],normal=(.2,-1.1,1.5))


STAGES[4]=stage04


def stage05(m):
    cx,cy=-115,-42
    # Removable 2.5-inch drive study; local dimensions are estimates, not a drive drawing.
    m.native('HDDBase','2.5-inch hard-drive aluminium enclosure',69.8,100,.65,6,(cx,cy,14),'Storage',2,'metal')
    m.cut('HDDBase',m.rr(66.8,97,5.6,(cx,cy,15),.7),'Open HDD mechanism cavity').Refine=False
    m.box('DiskCover','Thin hard-drive metal lid',69.4,99.6,.45,(cx,cy,20.15),'Storage',5,'metal',.6)
    m.ring('HDDPlatter','Blank magnetic storage platter',30.8,6,.42,(cx,cy-9,16.4),'Storage',3,'metal',internal=True)
    m.cyl('HDDMotor','Disk spindle motor',8,1.1,(cx,cy-9,15.1),'Storage',2,'metal',internal=True)
    m.cyl('HDDHub','Platter hub',5.7,1.2,(cx,cy-9,16.3),'Storage',3,'metal',internal=True)
    for i in range(6):
        import math
        a=i*math.pi/3
        m.cyl('HDDHubScrew'+str(i),'Spindle clamp fixing',.55,.3,(cx+3.6*math.cos(a),cy-9+3.6*math.sin(a),17.55),'Storage',4,'metal',internal=True)
    px,py=cx-21,cy+31
    m.cyl('HDDPivot','Actuator pivot carrier',4.1,2,(px,py,15.2),'Storage',2,'metal',internal=True)
    armpts=[(px-3,py+3),(px+3,py+3),(cx-10,cy+12),(cx-13,cy+10),(px-3,py-3)]
    verts=[V(x,y,17.35) for x,y in armpts]
    arm=Part.Face(Part.makePolygon(verts+[verts[0]])).extrude(V(0,0,.4))
    m.feature('HDDActuator','Single-platter actuator arm study',arm,'Storage',4,'metal',True)
    m.box('HDDHead','Read-write head study',1.2,1.7,.2,(cx-11.4,cy+12,17.05),'Storage',3,'black',.12,True)
    m.box('HDDMagnet','Actuator magnet enclosure',16,15,2,(cx-18,cy+38,15.2),'Storage',2,'metal',1,True)
    m.cut('HDDMagnet',Part.makeCylinder(4.35,2.4,V(px,py,15)),'Actuator pivot relief').Refine=False
    m.native('HDDPCB','Hard-drive underside controller board',64,36,.7,1,(cx,cy+28,12.6),'Storage',0,'pcb')
    for key,x,y,w,d,t in [('Controller',cx-12,cy+24,11,11,1),('Cache',cx+12,cy+23,12,8,.85),('MotorDriver',cx,cy+38,8,8,.8)]:
        m.box('HDD'+key,'Disk '+key+' package study',w,d,t,(x,y,12.45-t),'Storage',-1,'black',.2,True)
    # SATA connector shares the rear edge of the drive, with separate 7/15 contact groups.
    for key,x,w,count in [('Data',cx-13,14,7),('Power',cx+11,25,15)]:
        m.cut('HDDBase',m.rr(w+1,8,3.8,(x,cy+49,12.2),.2),'SATA connector recess').Refine=False
        m.box('SATA'+key+'Carrier','SATA '+key+' keyed insulator',w,6,2.6,(x,cy+49,12.8),'Storage',0,'black',.15,True)
        for i in range(count):
            m.box('SATA'+key+str(i),'SATA '+key+' contact',.55,4,.12,(x+(i-(count-1)/2)*1.25,cy+49.4,15.45),'Storage',1,'gold',.02,True)
    m.native('HDDCaddy','Removable hard-drive tray base',74,104,.7,.6,(cx,cy,10.4),'Storage',-2,'metal')
    m.cut('HDDCaddy',m.rr(53,75,1,(cx,cy-5,10.2),3),'Large underside drive-tray relief').Refine=False
    for side in [-1,1]:
        m.box('HDDCaddySide'+str(side),'Folded hard-drive tray side',.7,102,10,(cx+side*36.4,cy,11.05),'Storage',0,'metal',.12)
        for i,dy in enumerate([-35,35]):
            x=cx+side*36.4;y=cy+dy
            bore=Part.makeCylinder(1.2,5,V(x-side*2.5,y,17),V(side,0,0))
            m.cut('HDDCaddySide'+str(side),bore,'Drive retaining screw clearance').Refine=False
            m.cut('HDDBase',Part.makeCylinder(1.0,4,V(cx+side*35.4,y,17),V(-side,0,0)),'Blind drive-side mounting hole').Refine=False
            shaft=Part.makeCylinder(.8,4.0,V(cx+side*37.2,y,17),V(-side,0,0))
            head=Part.makeCylinder(2.2,.65,V(cx+side*37.1,y,17),V(side,0,0))
            m.feature('HDDMount'+str(side)+'_'+str(i),'Drive caddy retaining screw',shaft.fuse(head),'Storage',1,'metal',True)
    m.box('HDDPullTab','Drive tray extraction tab',1.0,15,2.2,(cx-37.8,cy,15.5),'Storage',0,'metal',.4)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=5
    m.checkpoint(5,'side_removable_60gb_drive_and_caddy','建立可侧向取出的 2.5 英寸硬盘与托架，保留四组安装件、拉片、SATA 7/15 接点、控制板、壳体和薄盖。盘片、磁头臂及芯片为通用单盘片学习示意，不断言实机供应商或 60GB 盘片配置。')
    m.snapshot('05_storage_internals',assemblies=['Storage'],exclude=['DiskCover'],normal=(.2,-.5,2))


STAGES[5]=stage05


def stage06(m):
    m.native('MainPCB','COK-001-family mainboard study',292,224,2,1.6,(0,-4,29.7),'Mainboard',0,'pcb')
    mounts=[(-138,-97),(138,-97),(-138,99),(138,99),(0,84),(0,-89),(-75,43),(75,43)]
    m.cut('MainPCB',[Part.makeCylinder(1.65,2,V(x,y,29.5)) for x,y in mounts],'Mainboard mounting holes').Refine=False
    for i,(x,y) in enumerate(mounts):
        for side,z in [('Top',31.34),('Bottom',29.6)]:m.ring('Ground'+side+str(i),'Separate exposed board ground annulus',3.0,1.8,.05,(x,y,z),'Mainboard',0,'gold',internal=True)
    # Cell and RSX face the underside cooling system. Packages retain separate caps/dies.
    for key,x,y,w in [('Cell',-36,-4,46),('RSX',36,-4,52)]:
        m.box(key+'Substrate',key+' package substrate study',w,w,2,(x,y,27.4),'Mainboard',-1,'pcb',.5,True)
        capw=w-4
        cap=m.rr(capw,capw,2,(x,y,25),1.2).cut(m.rr(capw-3,capw-3,1.5,(x,y,25.75),.7))
        m.feature(key+'HeatSpreader',key+' independent integrated heat spreader',cap,'Mainboard',-2,'metal',True)
        m.box(key+'Die',key+' silicon die study',16,16,1.2,(x,y,25.9),'Mainboard',-2,'black',.15,True)
        if key=='RSX':
            for i,(dx,dy,ww,hh) in enumerate([(-15.8,0,9,12),(15.8,0,9,12),(0,-15.8,12,9),(0,15.8,12,9)]):m.box('RSXMemory'+str(i),'RSX under-cap memory package study',ww,hh,1.0,(x+dx,y+dy,26.1),'Mainboard',-2,'black',.1,True)
    for i,(x,y) in enumerate([(-100,-15),(-77,-15),(-100,5),(-77,5)]):m.box('XDRMemory'+str(i),'XDR system-memory package study',14,10,1.1,(x,y,28.3),'Mainboard',-1,'black',.2,True)
    m.box('EEGSSubstrate','Original EE+GS compatibility processor substrate',31,31,1.5,(111,-34,27.9),'Mainboard',-1,'pcb',.4,True)
    m.box('EEGSHeatSpreader','EE+GS metal package face',27,27,.7,(111,-34,27),'Mainboard',-2,'metal',.9,True)
    m.box('Southbridge','Early-family system bridge study',24,24,1.6,(-14,71,27.8),'Mainboard',-1,'black',.4,True)
    m.box('BridgeLid','System bridge metal cap',20,20,.5,(-14,71,27.1),'Mainboard',-2,'metal',.5,True)
    for key,x,y,w,h in [('Flash0',-112,68,16,10),('Flash1',-88,68,16,10),('VideoEncoder',49,76,16,16),('LANLogic',18,92,12,12),('USBLogic',-81,-77,12,12),('SystemControl',94,69,17,17),('Clock',-111,31,9,6)]:m.box(key,key+' package study',w,h,1.1,(x,y,31.55),'Mainboard',1,'black',.2,True)
    for i,x in enumerate([-113,-91,-69]):m.box('CompatibilityRAM'+str(i),'Compatibility-subsystem memory study',14,9,1.1,(x,91,31.55),'Mainboard',1,'black',.2,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=6
    m.checkpoint(6,'native_early_board_cell_rsx_and_ee_gs','建立 COK-001 同代布局学习主板及安装孔，区分朝下的 Cell、RSX 基板/硅片/金属盖、RSX 盖下显存、XDR 系统内存、首发 EE+GS 兼容处理器和系统桥；上面加入闪存和接口逻辑。封装内部与局部位置为非功能性示意。')
    m.snapshot('06_mainboard_upper',assemblies=['Mainboard'],normal=(0,0,1))
    m.snapshot('06_mainboard_lower',assemblies=['Mainboard'],normal=(0,0,-1))


STAGES[6]=stage06


def _top_socket(m,key,x,y,width,count):
    outer=m.rr(width,5,3,(x,y,31.55),.35)
    inner=m.rr(width-1.2,3.8,2.6,(x,y,32.15),.15)
    m.feature(key+'Housing',key+' board connector carrier',outer.cut(inner),'Mainboard',2,'black',True)
    for i in range(count):m.box(key+'Contact'+str(i),'Separate '+key+' board contact',.25,2.9,.17,(x+(i-(count-1)/2)*(width-2)/count,y,32.3),'Mainboard',2,'gold',.02,True)


def stage07(m):
    for i,x in enumerate([-128,-107,-86,-65,-44,-23,-2]):
        m.box('CellChoke'+str(i),'Cell supply regulation inductor study',10,10,4.3,(x,-39,31.55),'Mainboard',1,'metal',.6,True)
        m.box('CellPowerStage'+str(i),'Cell regulator switching package',7,7,1.2,(x,-55,31.55),'Mainboard',1,'black',.2,True)
        m.cyl('CellSupplyCap'+str(i),'Cell regulation capacitor',2.8,5.2,(x,-21,31.55),'Mainboard',1,'metal',internal=True)
    for i,x in enumerate([35,57,79,101]):
        m.box('RSXChoke'+str(i),'RSX supply regulation inductor study',8,8,4.0,(x,16,31.55),'Mainboard',1,'metal',.5,True)
        m.box('RSXPowerStage'+str(i),'RSX regulator switching package',6,6,1.1,(x,3,31.55),'Mainboard',1,'black',.2,True)
        m.cyl('RSXSupplyCap'+str(i),'RSX regulation capacitor',2.8,5.2,(x,33,31.55),'Mainboard',1,'metal',internal=True)
    for key,x,y,w,h in [('Flash0',-112,68,16,10),('Flash1',-88,68,16,10)]:
        for side in [-1,1]:
            for i in range(24):m.box(key+'Lead'+str(side)+'_'+str(i),'Separate flash-package gull-wing lead study',.26,1,.16,(x+(i-11.5)*.62,y+side*(h/2+.66),31.45),'Mainboard',1,'metal',.02,True)
    for key,x,y,w,h in [('VideoEncoder',49,76,16,16),('LANLogic',18,92,12,12),('USBLogic',-81,-77,12,12),('SystemControl',94,69,17,17)]:
        for side in [-1,1]:
            for i in range(10):
                m.box(key+'LeadX'+str(side)+'_'+str(i),'Separate interface-package lead study',1,.28,.16,(x+side*(w/2+.65),y+(i-4.5)*.95,31.45),'Mainboard',1,'metal',.02,True)
                m.box(key+'LeadY'+str(side)+'_'+str(i),'Separate interface-package lead study',.28,1,.16,(x+(i-4.5)*.95,y+side*(h/2+.65),31.45),'Mainboard',1,'metal',.02,True)
    for key,x,y,w,n in [('ControlLink',-91,-98,28,20),('WirelessLink',-48,-98,23,18),('CardLink',-126,-67,18,12),('OpticalLink',78,-78,29,24),('PowerLink',-90,20,16,6),('FanLink',127,82,10,3)]:_top_socket(m,key,x,y,w,n)
    # Small bypass packages placed in clear perimeter bands, each checked against populated footprints.
    candidates=[(x,y) for y in [-89,-66,48,57] for x in range(-128,135,12)]
    occupied=[o.Shape.optimalBoundingBox(False,False) for o in m.parts.values() if o.Assembly=='Mainboard' and o.Shape.optimalBoundingBox(False,False).ZMax>31.4]
    count=0
    for x,y in candidates:
        if any(b.XMin-1.4<x<b.XMax+1.4 and b.YMin-1<y<b.YMax+1 for b in occupied):continue
        m.box('BoardBypass'+str(count),'Separate board bypass package study',1.7,.85,.55,(x,y,31.55),'Mainboard',1,'metal',.1,True);count+=1
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=7
    m.checkpoint(7,'cell_rsx_regulation_and_board_connector_detail','加入 Cell / RSX 两组独立供电电感、功率级与电容、闪存和接口逻辑引脚、触控/无线/读卡/光驱/电源/风扇板端插座及避让后的分立旁路器件。器件数量与引脚布局只表达结构层次，不复刻电路。')
    m.snapshot('07_populated_mainboard',assemblies=['Mainboard'],normal=(.2,-.4,2))


STAGES[7]=stage07


def stage08(m):
    holes=[]
    for j,x in enumerate([-119,-96,-73,-50]):
        for i in range(4):
            px=x+(i-1.5)*1.05;py=-109.6
            holes.append(Part.makeCylinder(.36,2,V(px,py,29.5)))
            m.box('USBBoardPin'+str(j)+'_'+str(i),'Independent USB terminal riser to the motherboard',.28,.28,12.12,(px,py,19.43),'FrontIO',0,'metal',.02,True)
            m.ring('USBPad'+str(j)+'_'+str(i),'USB through-hole solder annulus study',.49,.38,.05,(px,py,31.34),'Mainboard',0,'gold',internal=True)
    m.cut('MainPCB',holes,'Sixteen independent original USB board terminals').Refine=False
    m.native('WirelessPCB','Separate launch-family wireless assembly board',99,40,1.5,1.2,(-83,-77,38),'Wireless',3,'pcb')
    mounts=[(-129,-93),(-37,-93),(-129,-61),(-37,-61)]
    m.cut('WirelessPCB',[Part.makeCylinder(1.2,1.6,V(x,y,37.8)) for x,y in mounts],'Wireless-board mounting holes').Refine=False
    for i,(x,y) in enumerate(mounts):
        m.ring('WirelessPost'+str(i),'Wireless board mounting spacer',2.3,1.25,3.4,(x,y,34.3),'Wireless',2,'black',internal=True)
        m.screw('WirelessScrew'+str(i),(x,y,39.8),'Wireless',4,length=4.5,radius=1.8,axis=(0,0,-1))
    m.box('WirelessChip','WLAN / Bluetooth package study',13,13,1.4,(-95,-77,39.45),'Wireless',4,'black',.3,True)
    m.box('WirelessMemory','Wireless control memory study',11,7,1.1,(-72,-78,39.45),'Wireless',4,'black',.2,True)
    m.box('WirelessCrystal','Wireless module crystal',7,4,1.5,(-72,-67,39.45),'Wireless',4,'metal',.4,True)
    rf=m.rr(62,27,4.5,(-88,-77,39.45),1).cut(m.rr(60.6,25.6,4.9,(-88,-77,39.25),.6))
    m.feature('WirelessShieldFrame','Separate RF shield wall',rf,'Wireless',4,'metal',True)
    m.box('WirelessShieldLid','Removable RF shield lid',62,27,.35,(-88,-77,44.1),'Wireless',5,'metal',1,True)
    sock=m.rr(15,6,2.8,(-46.5,-77,39.45),.3).cut(m.rr(13.8,4.8,2.5,(-46.5,-77,40.05),.12))
    m.feature('WirelessFFCSocket','Wireless assembly ribbon connector',sock,'Wireless',4,'white',True)
    for i in range(18):m.box('WirelessFFCContact'+str(i),'Separate wireless FFC contact',.25,3.8,.15,(-46.5+(i-8.5)*.68,-77,40.2),'Wireless',4,'gold',.02,True)
    m.ring('WirelessCoaxSocket','Wireless board coaxial socket',1.6,.8,1.7,(-125,-76,39.45),'Wireless',4,'metal',internal=True)
    m.native('AntennaPCB','Separate small RF antenna carrier',9,23,.7,1,(146.7,51,42),'Wireless',3,'pcb')
    m.cut('AntennaPCB',Part.makeCylinder(1.1,1.4,V(146.7,58,41.8)),'Single antenna mounting hole').Refine=False
    m.screw('AntennaScrew',(146.7,58,43.5),'Wireless',4,length=3,radius=1.8,axis=(0,0,-1))
    m.box('AntennaFoil','Separate antenna foil study',6,8,.12,(146.7,46,43.2),'Wireless',4,'gold',.3,True)
    m.native('ControlPCB','Original power and eject touch-control board study',50,10,1,1,(116,-111,35),'Controls',2,'pcb')
    for i,x in enumerate([104,126]):
        m.box('TouchController'+str(i),'Touch-control sensing package study',5,4,1.1,(x,-111,36.2),'Controls',3,'black',.25,True)
        m.box('TouchCopper'+str(i),'Separate capacitive sensing electrode study',7,4,.08,(x,-111,34.8),'Controls',2,'gold',.3,True)
    m.box('ControlFFC','Control-board ribbon connector study',12,4,2,(116,-107.5,36.2),'Controls',3,'white',.3,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=8
    m.checkpoint(8,'usb_board_terminals_wireless_module_and_touch_board','将四 USB 的十六端子独立接入主板通孔，加入首发无线板、独立 RF 屏蔽、FFC 接点、同轴插座、小型天线板及电源/出仓触控板。独立板件分布依据拆解，射频形状和传感电路为结构示意。')
    m.snapshot('08_front_electronics',assemblies=['FrontIO','Wireless','Controls'],exclude=['CardReaderFlap','WirelessShieldLid'],normal=(.2,-.6,2))


STAGES[8]=stage08


def _launch_fan_vane(height=12):
    import math
    def p(r,a):return V(r*math.cos(math.radians(a)),r*math.sin(math.radians(a)))
    a,b,c=p(24,0),p(47,14),p(73.5,29)
    d,e,f=p(73.5,30),p(47,15),p(24,1)
    return Part.Face(Part.Wire([Part.Arc(a,b,c).toShape(),Part.makeLine(c,d),Part.Arc(d,e,f).toShape(),Part.makeLine(f,a)])).extrude(V(0,0,height))


def stage09(m):
    # The service exploded view puts the fan below the dual-processor heat exchanger.
    cx,cy=26,0
    m.ring('FanFrame','Large original-family cooling fan frame study',77.5,75.5,14.7,(cx,cy,4.5),'Cooling',-6,'black',internal=True)
    rotor=Part.makeCylinder(24,13.2,V(cx,cy,5.2))
    vanes=[]
    for i in range(19):
        s=_launch_fan_vane(12);s.rotate(V(),V(0,0,1),i*360/19);s.translate(V(cx,cy,5.8));vanes.append(s)
    rotor=rotor.multiFuse(vanes).cut(Part.makeCylinder(17.2,12.4,V(cx,cy,4.5))).cut(Part.makeCylinder(2.15,16,V(cx,cy,4))).removeSplitter()
    assert len(rotor.Solids)==1
    m.feature('FanRotor','Nineteen curved vanes: selected fan study, not all production variants',rotor,'Cooling',-5,'black',True)
    m.ring('FanStator','Separate fan stator and bearing envelope',16.5,2.4,11.8,(cx,cy,4.8),'Cooling',-6,'metal',internal=True)
    m.cyl('FanAxle','Fan rotor shaft',2,12.5,(cx,cy,4.7),'Cooling',-5,'metal',internal=True)
    for i,angle in enumerate([0,120,240]):
        import math
        x=cx+81.2*math.cos(math.radians(angle));y=cy+81.2*math.sin(math.radians(angle))
        m.ring('FanLug'+str(i),'Independent fan mounting ear study',3.5,1.3,1.2,(x,y,4.5),'Cooling',-6,'black',internal=True)
        m.screw('FanScrew'+str(i),(x,y,6.1),'Cooling',-5,length=2.5,radius=2,axis=(0,0,-1))
    m.native('CoolingCarrier','Heat-exchanger carrier with fan opening',200,171,3,.45,(26,-.5,20.0),'Cooling',-4,'metal')
    m.cut('CoolingCarrier',Part.makeCylinder(69,.9,V(cx,cy,19.8)),'Open air passage above fan').Refine=False
    for key,x,w in [('Cell',-36,43),('RSX',36,49)]:
        m.box(key+'Thermal','Separate processor thermal interface layer study',w-2,w-2,.16,(x,-4,24.81),'Cooling',-2,'thermal',.4,True)
        m.native(key+'Coldplate',key+' copper heat-spreader',w,w,1,2.65,(x,-4,22.1),'Cooling',-3,'copper')
    # Four independent heat pipes; clearance cuts are kept as real native features.
    from .atari2600 import _rounded_route
    clear=[]
    for i,x in enumerate([-51,-21,21,51]):
        points=[V(x,-20,22),V(x,76,22),V(x,82,16.5),V(x,103,16.5)]
        pipe=_rounded_route(points,2.5,1.5)
        m.feature('HeatPipe'+str(i),'Independent sealed heat-pipe envelope study',pipe,'Cooling',-4,'copper',True)
        clear.append(_rounded_route(points,2.5,1.68))
    tool=Part.makeCompound(clear)
    m.cut('CoolingCarrier',tool,'Open heat-pipe bends through the cooling carrier').Refine=False
    m.cut('FanFrame',tool,'Fan frame relief at heat-pipe bend').Refine=False
    for key in ['CellColdplate','RSXColdplate']:m.cut(key,tool,'Separated heat-pipe channels under processor spreader').Refine=False
    for i in range(90):
        x=-72+2.2*i
        s=Part.makeBox(.32,22,20.5,V(x,86,3.7)).cut(tool)
        m.feature('CoolingFin'+str(i),'Independent rear heat-exchanger lamella',s,'Cooling',-5,'metal',True)
    m.box('FinLowerRail','Rear fin-pack bottom rail',197,22,.4,(26.1,97,3.1),'Cooling',-6,'metal',.2,True)
    m.box('CompatibilityThermal','Legacy compatibility processor interface study',24,24,.15,(111,-34,26.8),'Cooling',-2,'thermal',.3,True)
    m.box('CompatibilityPlate','Compatibility processor heat-spreader study',27,27,1.8,(111,-34,24.7),'Cooling',-3,'metal',.6,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=9
    m.checkpoint(9,'large_lower_fan_dual_processor_heat_pipes_and_fins','建立位于主板下方的大型风扇、独立定子/轴/固定耳、双处理器铜板及接触层、四根独立热管和九十片独立鳍片。风扇采用十九叶结构示意，不声称所有首发机风扇相同；局部尺寸、热管路径和兼容芯片散热接触为学习近似。')
    m.snapshot('09_cooling_review',assemblies=['Cooling'],normal=(.3,-.6,2))


STAGES[9]=stage09


def stage10(m):
    m.colors['powerpcb']=(.46,.36,.12)
    m.native('PowerCase','Separate launch-family metal power-supply enclosure',138,116,1,28,(-73,24,43),'Power',3,'metal')
    m.cut('PowerCase',m.rr(136.4,114.4,28,(-73,24,43.8),.5),'Open folded power-supply case').Refine=False
    slots=[Part.makeBox(.0+2,4,5,V(-143,y,z)) for y in range(-26,74,9) for z in [49,59]]
    slots += [Part.makeBox(5,3,5,V(x,80,z)) for x in range(-133,-12,10) for z in [49,59]]
    m.cut('PowerCase',slots,'Real side and rear power-supply vents').Refine=False
    m.native('PowerPCB','Separate internal switching-power board study',128,106,1,1.4,(-73,24,46),'Power',4,'powerpcb')
    mounts=[(x,y) for x in [-134,-12] for y in [-25,73]]
    m.cut('PowerPCB',[Part.makeCylinder(1.2,1.8,V(x,y,45.8)) for x,y in mounts],'Power board mounting holes').Refine=False
    for i,(x,y) in enumerate(mounts):
        m.ring('PowerPost'+str(i),'Power board insulating spacer',2.5,1.25,1.9,(x,y,44),'Power',3,'black',internal=True)
        m.screw('PowerScrew'+str(i),(x,y,48),'Power',5,length=3.5,radius=1.8,axis=(0,0,-1))
    for key,x,y,w,d,h in [('Main',-107,21,24,27,18),('Standby',-80,49,14,18,13)]:
        m.box('Power'+key+'Core','Power transformer ferrite-core envelope',w,d,h,(x,y,47.7),'Power',5,'black',.8,True)
        m.box('Power'+key+'Wrap','Separate transformer winding wrap study',w-3,d-3,.45,(x,y,47.9+h),'Power',5,'powerpcb',.5,True)
    for i,y in enumerate([8,40]):
        m.cyl('PowerBulk'+str(i),'Primary filter capacitor envelope',8,19,(-43,y,47.7),'Power',5,'battery',internal=True)
        m.cyl('PowerBulkVent'+str(i),'Primary capacitor metal end',7.65,.2,(-43,y,66.8),'Power',5,'metal',internal=True)
    for i,x in enumerate([-120,-104,-88]):
        m.cyl('PowerOutputCap'+str(i),'Output filter capacitor study',4,13,(x,-16,47.7),'Power',5,'battery',internal=True)
        m.cyl('PowerOutputVent'+str(i),'Output capacitor vent cap',3.7,.15,(x,-16,60.8),'Power',5,'metal',internal=True)
    for i,x in enumerate([-126,-86,-62]):
        m.box('PowerHeatSink'+str(i),'Separate aluminium power-device heat sink',2.5,28,19,(x,21,47.7),'Power',5,'metal',.2,True)
        m.box('PowerSwitch'+str(i),'Power-semiconductor package study',3,10,13,(x+4,21,47.7),'Power',5,'black',.3,True)
    m.box('PowerInputChoke','Input common-mode choke envelope',13,15,13,(-20,48,47.7),'Power',5,'copper',.8,True)
    m.box('PowerRectifier','Input rectifier package study',11,8,8,(-20,25,47.7),'Power',5,'black',.3,True)
    m.cyl('PowerFuse','Ceramic cartridge fuse',2,17,(-30,65,50.2),'Power',5,'white',axis=(1,0,0),internal=True)
    for i,x in enumerate([-31,-12.6]):m.cyl('PowerFuseCap'+str(i),'Separate fuse end cap',2.1,.8,(x,65,50.2),'Power',5,'metal',axis=(1,0,0),internal=True)
    m.box('PowerController','Switching controller IC study',10,7,1.2,(-102,55,47.7),'Power',5,'black',.2,True)
    for i in range(8):
        for side in [-1,1]:m.box('PowerICLead'+str(side)+'_'+str(i),'Separate controller IC lead',.3,1.2,.15,(-102+(i-3.5)*1.1,55+side*4.2,47.6),'Power',5,'metal',.02,True)
    # Small passives remain independent bodies with visible board clearance.
    for i,x in enumerate([-126,-116,-106,-96,-86,-76,-66,-56]):m.box('PowerPassive'+str(i),'Separate regulation passive package',3.5,2,1.1,(x,68,47.7),'Power',5,'metal',.2,True)
    m.cut('PowerCase',Part.makeBox(19,9,9,V(-85,-37,47)),'Low-voltage harness exit').Refine=False
    sock=m.rr(18,7,5,(-75.5,-26,47.7),.4).cut(m.rr(16.4,5.4,4.7,(-75.5,-26,48.3),.2))
    m.feature('PowerOutputSocket','Five-position power-control harness carrier',sock,'Power',5,'white',True)
    for i in range(5):m.box('PowerOutputContact'+str(i),'Separate power-control socket contact',.6,4,.3,(-75.5+(i-2)*3,-26,48.6),'Power',5,'metal',.05,True)
    m.cut('PowerCase',Part.makeBox(16,6,9,V(-28,79,47)),'Internal AC harness exit').Refine=False
    m.box('PowerACHeader','Internal AC harness carrier',14,5,7,(-22,76,47.7),'Power',5,'white',.4,True)
    for i,x in enumerate([-26,-22,-18]):m.box('PowerACTerminal'+str(i),'Separate AC header contact study',.65,2.5,.5,(x,80,50.7),'Power',5,'metal',.05,True)
    m.native('PowerLid','Separate perforated metal power-supply lid',138,116,1,.6,(-73,24,71.2),'Power',7,'metal')
    holes=[m.rr(4.2,4.2,1,(x,y,71),.4) for x in range(-132,-11,10) for y in [-25,-15,63,73]]
    m.cut('PowerLid',holes,'Power-supply lid ventilation openings').Refine=False
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=10
    m.checkpoint(10,'metal_power_enclosure_transformers_filters_and_terminals','加入首发金属罩电源、独立原生电路板与安装件、变压器、滤波电容、功率器件/散热片、保险丝及五位控制线束端口。上下盖及侧面通风孔真实贯通，内部电子元件为非功能性结构示意。')
    m.snapshot('10_power_review',assemblies=['Power'],exclude=['PowerLid'],normal=(.3,-.6,2))


STAGES[10]=stage10


def stage11(m):
    m.native('DriveChassis','Original slot-loading optical-drive chassis study',140,160,1,14.8,(72,-27,39.2),'Optical',3,'metal')
    m.cut('DriveChassis',m.rr(138.4,158.4,14.6,(72,-27,40),.6),'Open thin-floor optical chassis').Refine=False
    m.cut('DriveChassis',m.rr(128,3.3,8,(77,-103,47.7),.45,g.rotation((0,-1,0),(0,0,1))),'Disc path aligned with original front fascia').Refine=False
    m.native('DriveTopCover','Separate stamped optical-drive upper lid',139.5,159.5,.8,.5,(72,-27,54.2),'Optical',7,'metal')
    m.native('DrivePCB','Separate BMD-family optical control board study',132,152,.8,1.2,(72,-27,37.3),'Optical',2,'pcb')
    mounts=[(x,y) for x in [9,134] for y in [-100,46]]
    holes=[Part.makeCylinder(1.25,20,V(x,y,36.5)) for x,y in mounts]
    for key in ['DrivePCB','DriveChassis','DriveTopCover']:m.cut(key,holes,'Optical-drive through mounting holes').Refine=False
    for i,(x,y) in enumerate(mounts):
        m.ring('DriveMount'+str(i),'Optical chassis insulating support spacer',2.4,1.3,2.1,(x,y,34.9),'Optical',1,'rubber',internal=True)
        m.screw('DriveScrew'+str(i),(x,y,55.1),'Optical',7,length=19.3,radius=2,axis=(0,0,-1))
    for key,x,y,w,d in [('Control',74,-45,20,20),('Motor',103,-68,12,12),('Memory',43,-68,16,9)]:m.box('Drive'+key+'IC','Separate optical control-board package study',w,d,1.3,(x,y,35.8),'Optical',1,'black',.3,True)
    for i,x in enumerate(range(20,130,10)):m.box('DriveBypass'+str(i),'Optical control-board bypass package',2,1,.6,(x,-91,36.5),'Optical',1,'metal',.15,True)
    m.ring('DriveMedia','Blank 120 mm disc for loaded-pose study',60,7.5,1.2,(77,-23,47.2),'Optical',5,'white',internal=True)
    m.cyl('DriveSpindleMotor','Optical spindle motor envelope',11,4.2,(77,-23,40.3),'Optical',3,'metal',internal=True)
    m.cyl('DriveSpindleHub','Separate disc-centering spindle',7,3.7,(77,-23,44.7),'Optical',4,'black',internal=True)
    m.ring('DriveMediaSeat','Media support annulus',10,7.2,.6,(77,-23,46.5),'Optical',4,'rubber',internal=True)
    m.cyl('DriveClamp','Separate magnetic upper disc clamp',14,.65,(77,-23,48.5),'Optical',6,'metal',internal=True)
    m.cyl('DriveClampMagnet','Disc-clamp magnet study',7,1,(77,-23,49.3),'Optical',6,'black',internal=True)
    upper=m.rr(132,142,1,(72,-25,51.5),.8).cut(m.rr(121,130,1.4,(72,-25,51.3),.5))
    m.feature('DriveUpperFrame','Independent open upper mechanism frame',upper.cut(Part.makeCompound(holes)),'Optical',6,'black',True)
    for i,x in enumerate([15,139]):m.box('DiscEntranceGuide'+str(i),'Slot entrance side guide study',2.2,23,2.1,(x,-119.3,46.65),'Optical',4,'black',.35,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=11
    m.profile['internal_exclude']=list(dict.fromkeys(m.profile.get('internal_exclude',[])+['DriveMedia','DriveClamp','DriveClampMagnet']))
    m.checkpoint(11,'original_optical_chassis_control_board_spindle_and_clamp','分开原版吸入式光驱的上下金属件、下方控制板及元件、安装件、主轴电机/夹盘与空白光盘，并使进盘平面对齐前面板。板型与静态机构尺寸依据爆炸图近似，光盘仅用于表达装载状态。')
    m.snapshot('11_drive_stack',assemblies=['Optical'],exclude=['DriveTopCover'],normal=(.2,-.5,2))


STAGES[11]=stage11


def stage12(m):
    clear=[]
    for i,x in enumerate([54,100]):
        m.cyl('PickupRail'+str(i),'Independent optical-pickup guide rod',1,53,(x,-82,43.4),'Optical',3,'metal',axis=(0,1,0),internal=True)
        m.ring('PickupBearing'+str(i),'Separate optical-pickup sliding sleeve',1.8,1.15,12,(x,-71,43.4),'Optical',4,'white',axis=(0,1,0),internal=True)
        clear.append(Part.makeCylinder(2,22,V(x,-76,43.4),V(0,1,0)))
        for j,y in enumerate([-84,-30]):
            m.ring('PickupRailEnd'+str(i)+'_'+str(j),'Optical guide end support',1.6,1.15,3,(x,y,43.4),'Optical',3,'black',axis=(0,1,0),internal=True)
            m.box('PickupRailFoot'+str(i)+'_'+str(j),'Optical-guide pedestal study',4.4,3,1.5,(x,y+1.5,40.1),'Optical',3,'black',.25,True)
    sh=m.rr(51,19,4,(77,-65,40.8),.8).cut(Part.makeCompound(clear))
    m.feature('PickupCarriage','Guide-bored optical pickup carriage study',sh,'Optical',4,'metal',True)
    m.box('ObjectiveCarrier','Single-objective KEM400-family carrier study',10,10,1,(77,-61,45),'Optical',4,'black',.4,True)
    frame=m.rr(12,12.5,.6,(77,-61,46.1),.4).cut(Part.makeCylinder(3.1,1,V(77,-61,45.9)))
    m.feature('ObjectiveFrame','Separate focus suspension frame',frame,'Optical',5,'metal',True)
    m.cyl('ObjectiveLens','Single optical objective lens envelope',2.6,.55,(77,-61,46.3),'Optical',5,'blue',internal=True)
    for i,x in enumerate([69,85]):m.box('ObjectiveCoil'+str(i),'Focus actuator coil envelope',1.2,9,1.3,(x,-61,45.1),'Optical',5,'copper',.2,True)
    for i,y in enumerate([-69,-60]):m.cyl('PickupLaser'+str(i),'Separate optical emitter package study',1.1,4.5,(59,y,46),'Optical',4,'black',axis=(1,0,0),internal=True)
    m.box('PickupPrism','Optical-path prism housing envelope',3,3,1.6,(66,-65,45),'Optical',4,'black',.2,True)
    m.cyl('PickupFeedMotor','Optical-pickup feed motor',3.3,11,(114,-80,43.7),'Optical',3,'metal',axis=(0,1,0),internal=True)
    m.cut('PickupFeedMotor',Part.makeCylinder(.9,12,V(114,-80.5,43.7),V(0,1,0)),'Independent feed shaft clearance').Refine=False
    m.cyl('PickupFeedShaft','Optical feed motor shaft',.65,14,(114,-79,43.7),'Optical',4,'metal',axis=(0,1,0),internal=True)
    m.cyl('PickupFeedScrew','Pickup lead-screw envelope study',.8,35,(114,-64.8,43.7),'Optical',4,'metal',axis=(0,1,0),internal=True)
    nut=m.rr(6,7,3.3,(114,-62,42.05),.4).cut(Part.makeCylinder(1,8,V(114,-66,43.7),V(0,1,0)))
    m.feature('PickupFeedNut','Independent feed nut with shaft clearance',nut,'Optical',4,'white',True)
    m.box('PickupFeedLink','Feed-nut to carriage connecting tongue',7.8,4,1,(106.8,-65,42.3),'Optical',4,'white',.2,True)
    m.cyl('IntakeShaft','Front intake roller shaft',.85,122,(15,-95.5,44.6),'Optical',4,'metal',axis=(1,0,0),internal=True)
    for i,x in enumerate([19,85]):m.ring('IntakeRoller'+str(i),'Separate rubber disc-intake roller',2.4,1.05,46,(x,-95.5,44.6),'Optical',4,'rubber',axis=(1,0,0),internal=True)
    for i,x in enumerate([16,72,134]):m.ring('IntakeBearing'+str(i),'Separate loading roller bearing',2.6,1.05,1.8,(x,-95.5,44.6),'Optical',4,'white',axis=(1,0,0),internal=True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=12
    m.checkpoint(12,'single_objective_pickup_feed_guides_and_intake_rollers','加入首发单物镜光头结构示意、独立导杆与滑套、物镜/焦点框/线圈、发光封装、进给电机/螺杆/螺母以及吸入滚轮。几何运动副保留间隙，光学路径和运动尺寸不作工作机构验证。')
    m.snapshot('12_drive_mechanism',assemblies=['Optical'],exclude=['DriveTopCover','DriveMedia','DriveClamp','DriveClampMagnet','DriveUpperFrame'],normal=(.2,-.5,2))


STAGES[12]=stage12


def stage13(m):
    mounts=[(-138,-97),(138,-97),(-138,99),(138,99),(0,84),(0,-89),(-75,43),(75,43)]
    m.native('LowerBoardShield','Separate lower mainboard shield with processor windows',292,221,2,.35,(0,-3,26.3),'Shielding',-2,'metal')
    apertures=[m.rr(w,h,1,(x,y,26),1) for x,y,w,h in [(-36,-4,50,50),(36,-4,56,56),(111,-34,34,34),(-14,71,27,27)]]
    apertures += [Part.makeCylinder(1.5,1,V(x,y,26)) for x,y in mounts]
    apertures += [Part.makeCylinder(.5,1,V(x+(i-1.5)*1.05,-109.6,26)) for x in [-119,-96,-73,-50] for i in range(4)]
    m.cut('LowerBoardShield',apertures,'Processor and independent terminal clearances').Refine=False
    m.native('UpperBoardShield','Separate upper shield and equipment mounting frame',292,222,2,.35,(0,-3,37),'Shielding',2,'metal')
    tools=[m.rr(140,159,1,(72,-27,36.8),1),m.rr(53,15,1,(116,-110,36.8),1)]
    tools += [Part.makeCylinder(2.65,1,V(x,y,36.8)) for x,y in [(-129,-93),(-37,-93),(-129,-61),(-37,-61),(9,-100),(134,-100),(9,46),(134,46)]]
    tools += [Part.makeCylinder(1.5,1,V(x,y,36.8)) for x,y in mounts]
    tools += [m.rr(58,12,1,(x,-4,36.8),2) for x in [-36,36]]
    # Connector-access openings are distinct from broad mechanical apertures.
    tools += [m.rr(w,10,1,(x,y,36.8),.7) for x,y,w in [(-91,-98,30),(-48,-98,25),(-126,-67,20),(-90,20,18),(127,82,12)]]
    m.cut('UpperBoardShield',tools,'Optical electronics, front controls, posts and harness access').Refine=False
    m.cut('DrivePCB',[Part.makeCylinder(2.35,2,V(x,y,37.1)) for x,y in [(75,43),(138,-97)]],'Mainboard fastener clearance below optical board').Refine=False
    for i,(x,y) in enumerate(mounts):
        m.ring('BoardLowerPost'+str(i),'Mainboard lower support spacer',2.2,1.25,2.5,(x,y,26.85),'Frame',-1,'metal',internal=True)
        m.ring('BoardUpperPost'+str(i),'Mainboard upper shield spacer',2.2,1.25,5.3,(x,y,31.5),'Frame',1,'metal',internal=True)
        m.screw('BoardStackScrew'+str(i),(x,y,37.9),'Frame',3,length=10,radius=2,axis=(0,0,-1))
    for i,(x,y) in enumerate([(x,y) for x in [-100,-77] for y in [-15,5]]):m.box('XDRThermal'+str(i),'Separate XDR-to-shield thermal pad study',13,10,1.35,(x,y,26.8),'Cooling',-1,'thermal',.4,True)
    for key,x in [('Cell',-36),('RSX',36)]:
        # Open two-armed leaf clamp above each processor, separated from components below.
        strap=m.rr(55,9,.7,(x,-4,35.9),3).cut(Part.makeCylinder(3.5,1,V(x,-4,35.7)))
        m.feature(key+'LeafClamp',key+' spring clamp envelope study',strap,'Shielding',3,'metal',True)
        for i,dx in enumerate([-23,23]):
            m.ring(key+'ClampWasher'+str(i),'Processor clamp retaining washer',2.3,1.1,.3,(x+dx,-4,36.75),'Shielding',3,'metal',internal=True)
    m.cyl('RTCModule','Separate wrapped RTC coin-cell envelope',10,3.2,(124,69,38.1),'Mainboard',3,'battery',internal=True)
    m.box('RTCConnector','RTC two-wire board plug study',5,4,2,(108,69,31.55),'Mainboard',1,'white',.3,True)
    m.ring('SystemBuzzer','Mainboard buzzer enclosure',4.2,1.3,3,(119,94,31.55),'Mainboard',1,'black',internal=True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=13
    m.checkpoint(13,'board_shields_spacers_thermal_pads_and_retention','加入上下主板屏蔽、芯片/端子真实开窗、八处独立固定堆叠、XDR 接触垫、双处理器弹簧压片及 RTC/蜂鸣器示意。屏蔽孔避让光驱下方板件和前端模块；局部机构尺寸为学习近似。')
    m.snapshot('13_shield_stack',assemblies=['Shielding','Frame','Cooling'],normal=(.2,-.6,2))


STAGES[13]=stage13


def _study_gear(radius,teeth,height,center,bore=.9):
    import math
    pts=[]
    for i in range(teeth*4):
        r=radius if i%4 in [1,2] else radius-.7
        a=2*math.pi*i/(teeth*4);pts.append(V(r*math.cos(a),r*math.sin(a)))
    sh=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,height))
    sh=sh.cut(Part.makeCylinder(bore,height+.2,V(0,0,-.1)));sh.translate(V(*center));return sh


def stage14(m):
    # Original loading-block exploded views show separate motor, reduction train,
    # side cams, front arms and a toothed transmission belt. Teeth are illustrative.
    m.cyl('LoadMotor','Separate slot-loading motor envelope',3,12,(20,-40,44),'Optical',4,'metal',axis=(0,1,0),internal=True)
    m.cut('LoadMotor',Part.makeCylinder(.9,13,V(20,-40.5,44),V(0,1,0)),'Loading-motor shaft clearance').Refine=False
    m.cyl('LoadMotorShaft','Loading motor output shaft',.65,18,(20,-46,44),'Optical',4,'metal',axis=(0,1,0),internal=True)
    m.ring('LoadWorm','Loading-motor worm envelope study',1.5,.85,6,(20,-47,44),'Optical',4,'white',axis=(0,1,0),internal=True)
    for i,(x,y,r,n) in enumerate([(17,-55,5.5,18),(17,-67,5.5,18),(17,-79,5.5,18),(36,-88,6.7,22),(118,-88,6.7,22)]):
        m.feature('LoadGear'+str(i),'Separate loading gear with approximate teeth',_study_gear(r,n,1.6,(x,y,48.8)),'Optical',5,'white',True)
        m.cyl('LoadGearAxle'+str(i),'Separate loading-gear pin',.7,2.5,(x,y,48.4),'Optical',5,'metal',internal=True)
    # Thin independent loop preserves belt/gear separation in the static study.
    belt=m.rr(94,15,.8,(76,-88,52.7),7.4).cut(m.rr(92.8,13.8,1.2,(76,-88,52.5),6.8))
    m.feature('LoadingBelt','Independent front-arm transmission belt study',belt,'Optical',6,'rubber',True)
    for i,x in enumerate([11,133]):
        cam=m.rr(3.5,67,3.2,(x,-30,42),.5).cut(m.rr(1.3,24,3.6,(x,-24,41.8),.4))
        m.feature('SideLoadingCam'+str(i),'Separate side sliding cam envelope',cam,'Optical',4,'white',True)
        m.box('SideCamRail'+str(i),'Guide strip for loading cam',.75,19,2.7,(x,-24,42.25),'Optical',4,'metal',.2,True)
    for i,(x,angle) in enumerate([(36,-28),(118,28)]):
        arm=m.rr(7,31,.65,(x,-73,49.45),2).fuse(Part.makeCylinder(4,.65,V(x,-88,49.45)))
        arm=arm.cut(Part.makeCylinder(1.05,1,V(x,-88,49.2)));arm.rotate(V(x,-88,0),V(0,0,1),angle)
        # Arms sit above the media and are separated from the lower reduction gears.
        arm.translate(V(0,0,1.2));m.feature('FrontLoadingArm'+str(i),'Independent articulated front loading arm study',arm,'Optical',6,'black',True)
        m.ring('FrontArmPivot'+str(i),'Front arm pivot sleeve',1.8,1.1,.5,(x,-88,51.5),'Optical',6,'white',internal=True)
    m.box('MediaSensorPCB','Separate loading-state sensor board study',15,8,.7,(23,29,41),'Optical',3,'pcb',.5,True)
    for i,x in enumerate([19,27]):m.box('MediaSensor'+str(i),'Media-state optical sensor envelope',3.2,4,3,(x,29,41.9),'Optical',4,'black',.3,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=14
    m.checkpoint(14,'loading_motor_reduction_belt_side_cams_and_front_arms','依据首发光驱爆炸图补充吸入电机、独立减速齿轮和轴销、前臂传动带、左右滑动凸轮、前装载臂及介质状态传感板。齿形、传动关系与动作位置仅作静态机构示意。')
    m.snapshot('14_loading_mechanism',assemblies=['Optical'],exclude=['DriveTopCover','DriveMedia','DriveClamp','DriveClampMagnet','DriveUpperFrame'],normal=(.2,-.5,2))


STAGES[14]=stage14


def _planar_ribbon(points,width,t=.12,r=6):
    """Constant-width XY strip with circular bends and a positive inner radius."""
    import math
    points=[V(*p) for p in points]
    assert len(points)>=2 and 0<width<2*r and t>0
    assert all(abs(p.z-points[0].z)<1e-7 for p in points)
    edges=[];last=points[0]
    for prev,cur,nxt in zip(points,points[1:],points[2:]):
        inc=(cur-prev).normalize();out=(nxt-cur).normalize()
        angle=math.acos(max(-1,min(1,inc.dot(out))))
        if angle<1e-6:continue
        trim=r*math.tan(angle/2)
        assert trim<min((cur-last).Length,(nxt-cur).Length/2)
        entry=cur-inc*trim;leave=cur+out*trim
        center=cur+(out-inc).normalize()*(r/math.cos(angle/2))
        middle=center+(cur-center).normalize()*r
        edges.extend([Part.makeLine(last,entry),Part.Arc(entry,middle,leave).toShape()]);last=leave
    edges.append(Part.makeLine(last,points[-1]));path=Part.Wire(edges)
    tangent=(points[1]-points[0]).normalize()
    wide=V(-tangent.y,tangent.x,0)*width/2;thin=V(0,0,t/2);p=points[0]
    corners=[p-wide-thin,p+wide-thin,p+wide+thin,p-wide+thin]
    section=Part.Wire(Part.makePolygon(corners+[corners[0]]).Edges)
    shape=path.makePipeShell([section],True,False)
    shape.check(True)
    assert shape.isValid() and len(shape.Solids)==1
    return shape


def stage15(m):
    from .ps2 import _flat_ribbon
    from .atari2600 import _rounded_route
    m.colors['flex']=(.52,.29,.085)
    def socket(key,x,y,z,w,count,assembly):
        outer=m.rr(w,5,2.2,(x,y,z),.3);inner=m.rr(w-1.2,3.8,2,(x,y,z+.5),.15)
        m.feature(key+'Socket',key+' independent FFC carrier',outer.cut(inner),assembly,3,'white',True)
        for i in range(count):m.box(key+'Contact'+str(i),'Separate FFC terminal study',.25,3,.12,(x+(i-(count-1)/2)*(w-2)/count,y,z+.7),assembly,3,'gold',.02,True)
    socket('ReaderFFC',-125,-110,47.2,14,12,'FrontIO')
    socket('DriveMainFFC',78,-86,35,27,24,'Optical')
    # Turn the simple touch-board connector envelope into a genuinely open mouth.
    m.cut('ControlFFC',m.rr(10.6,2.8,1.8,(116,-107.5,36.7),.15),'Touch-board FFC cavity').Refine=False
    for i in range(12):m.box('ControlFFCContact'+str(i),'Separate control-board flex terminal',.25,2,.12,(116+(i-5.5)*.75,-107.5,36.9),'Controls',3,'gold',.02,True)
    routes=[
      ('WirelessRibbon',10.8,[(-48,-98,32.65),(-48,-103,32.65),(-48,-103,43),(-46.5,-77,43),(-46.5,-77,40.55)],'white'),
      ('ControlRibbon',9.8,None,'white'),
      ('ReaderRibbon',10,None,'white'),
      ('OpticalMainRibbon',22,[(78,-78,32.65),(78,-83,32.65),(78,-83,35.95),(78,-86,35.95)],'white')]
    for key,width,path,color in routes:
        def ribbon(w,t):
            if key=='ReaderRibbon':
                start=_flat_ribbon([(-126,-67,32.65),(-126,-67,35),(-126,-70,35)],w,t,.3)
                lower=_planar_ribbon([(-126,-69,35),(-126,-77,35),(-141,-77,35),(-141,-53.5,35)],w,t)
                rise=_flat_ribbon([(-141,-54,35),(-141,-53,35),(-141,-53,48.5),(-141,-54.5,48.5)],w,t,.3)
                upper=_planar_ribbon([(-141,-54,48.5),(-141,-95,48.5),(-125,-95,48.5),(-125,-110,48.5)],w,t)
                result=start.fuse(lower).fuse(rise).fuse(upper).removeSplitter()
                result.check(True)
                assert len(result.Solids)==1
                return result
            if key!='ControlRibbon':return _flat_ribbon(path,w,t,.3)
            start=_flat_ribbon([(-91,-98,32.65),(-91,-114,32.65),(-91,-114,43.5),(-91,-115,43.5)],w,t,.3)
            middle=_planar_ribbon([(-91,-114.5,43.5),(-91,-125,43.5),(116,-125,43.5),(116,-109,43.5)],w,t)
            end=_flat_ribbon([(116,-109.5,43.5),(116,-107.5,43.5),(116,-107.5,37.2)],w,t,.3)
            result=start.fuse(middle).fuse(end).removeSplitter()
            result.check(True)
            assert len(result.Solids)==1
            return result
        sh=ribbon(width,.12)
        m.feature(key,'Independent routed '+key+' study',sh,'Wiring',3,color,True)
        clearance=ribbon(width+.5,.5)
        # Only enclosure and carrier materials get explicit cable passages.
        families={'WirelessRibbon':['WirelessLinkHousing','UpperBoardShield','WirelessFFCSocket'],
                  'ControlRibbon':['ControlLinkHousing','UpperBoardShield','ControlFFC'],
                  'ReaderRibbon':['CardLinkHousing','UpperBoardShield','ReaderFFCSocket'],
                  'OpticalMainRibbon':['OpticalLinkHousing','DriveMainFFCSocket']}
        for target in families[key]:m.cut(target,clearance,'Separated flex-cable mouth and passage: '+key).Refine=False
    # Route the antenna lead around the front and right edges of the optical drive.
    path=[(-125,-76,41.55),(-125,-76,45.7),(-140,-80,45.7),(-140,-113,45.7),(146.7,-113,45.7),(146.7,51,45.7),(146.7,51,44.05)]
    m.feature('AntennaCoax','Independent wireless antenna coaxial cable study',_rounded_route([V(*p) for p in path],.7,.4),'Wiring',4,'black',True)
    m.ring('AntennaTerminal','Separate antenna-end coaxial termination',.75,.45,.6,(146.7,51,43.35),'Wireless',4,'metal',internal=True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=15
    m.checkpoint(15,'separate_board_flexes_and_routed_wireless_antenna','连接无线、触控、读卡和光驱的四条独立弯折排线，加入端部插座和接点，并在屏蔽及插座材料上保留真实通道；天线同轴线绕过光驱。路径、宽度与接点数量为静态连接示意。')
    m.snapshot('15_board_interconnects',assemblies=['Wiring','Wireless','FrontIO','Controls'],exclude=['CardReaderFlap','WirelessShieldLid'],normal=(.2,-.5,2))


STAGES[15]=stage15


def stage16(m):
    from .atari2600 import _rounded_route
    m.colors['wiregreen']=(.08,.34,.12)
    def wire(key,points,radius,color,targets=()):
        pts=[V(*p) for p in points];bend=.6 if key.startswith('RTC') else (.65 if radius<.4 else 1.2);sh=_rounded_route(pts,bend,radius)
        m.feature(key,'Independent routed '+key+' study',sh,'Wiring',2,color,True)
        if targets:
            tool=_rounded_route(pts,bend,radius+.22)
            for name in targets:m.cut(name,tool,'Insulated harness passage: '+key).Refine=False
    # The original PSU service drawing specifies a five-position control harness.
    o=m.parts.pop('PowerLinkContact5');m.doc.removeObject(o.Name)
    for i in range(5):
        o=m.parts['PowerLinkContact'+str(i)]
        sh=m.rr(.25,2.9,.17,(-90+(i-2)*2.8,20,32.3),.02)
        o.Shape=sh;o.Placement=sh.Placement;o.FlatPlacement=o.Placement
        start=-75.5+(i-2)*3;end=-90+(i-2)*2.8
        path=[(start,-26,49.3),(start,-39,49.3),(start,-39,39.6),(end,20,39.6),(end,20,32.8)]
        wire('PowerControlLead'+str(i),path,.3,['white','white','red','black','black'][i],['PowerOutputSocket','UpperBoardShield'])
    # Independent fan wires travel under the fan and rise through matching board holes.
    for i in range(3):
        yy=(i-1)*.8;xx=112+i;end=127+(i-1)*8/3;top=34.8+i*.45
        path=[(42.7,yy,8),(42.7,yy,3),(xx,yy,3),(xx,yy,top),(xx,73+2*i,top),(end,82,top),(end,82,32.8)]
        wire('FanLead'+str(i),path,.15,['black','red','white'][i],['CoolingCarrier','LowerBoardShield','MainPCB'])
    # Grounded AC harness: independent paths from the inlet to the PSU rear header.
    for i,(x,z,end) in enumerate([(119,19.325,-26),(124,25.825,-22),(129,19.325,-18)]):
        yy=104+2*i
        path=[(x,111.8,z),(x,yy,z),(x,yy,51.8+i*1.4),(end,yy,51.8+i*1.4),(end,85,51.8+i*1.4),(end,81.6,50.95)]
        if i==0:path=[(x,111.5,z),(120.6,109.5,z),(120.6,yy,z),(120.6,yy,51.8),(end,yy,51.8),(end,85,51.8),(end,81.6,50.95)]
        wire('ACInternalLead'+str(i),path,.55,['black','wiregreen','white'][i],['ACSocket','LowerBoardShield','MainPCB','UpperBoardShield'])
    # Low-current RTC harness remains separate from the five-position PSU bundle.
    for i in range(2):
        y=68.4+i*1.2;x=107+2*i
        m.ring('RTCTerminal'+str(i),'Separate RTC plug terminal',.45,.25,.6,(x,69,33.7),'Mainboard',2,'metal',internal=True)
        lane=67 if i==0 else 71
        path=[(113.5,y,39.3),(113.5,y,41),(111.8,lane,41),(x,lane,41),(x,69,41),(x,69,34.45)]
        wire('RTCLead'+str(i),path,.17,'red' if i else 'black',['UpperBoardShield'])
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=16
    m.checkpoint(16,'power_control_ac_fan_and_rtc_harnesses','补齐五位电源控制线、三线风扇、接地 AC 内线和 RTC 两线，并在板料及屏蔽材料上保留独立绝缘穿越孔。端点、路径与颜色为结构学习示意，不定义真实电气接线。')
    m.snapshot('16_power_and_fan_wiring',assemblies=['Wiring','Power','Cooling'],exclude=['PowerLid'],normal=(.2,-.5,2))


STAGES[16]=stage16


def _outer_apron(m,key,x):
    c=_arch_curve(256,49,47,91.85);p=c.getPoles();bottom=42.4
    sk=m.doc.addObject('Sketcher::SketchObject',key+'Outline')
    sk.addGeometry([c.toBSpline(),Part.LineSegment(p[-1],V(p[-1].x,bottom)),Part.LineSegment(V(p[-1].x,bottom),V(p[0].x,bottom)),Part.LineSegment(V(p[0].x,bottom),p[0])],False)
    sk.Placement=App.Placement(V(x,0,0),App.Rotation(V(0,1,0),V(0,0,1),V(1,0,0),'ZXY'))
    m.group('Construction').addObject(sk)
    ex=m.doc.addObject('Part::Extrusion',key+'Wall');ex.Base=sk;ex.DirMode='Normal';ex.LengthFwd=1.3;ex.Solid=True
    m.doc.recompute();sk.Visibility=False
    return m.register(ex,key,'Body',5,'ps3gloss')


def stage17(m):
    # Outer curved end aprons close the roof-edge gap while retaining the inset inner walls.
    _outer_apron(m,'LeftOuterApron',-162.15);_outer_apron(m,'RightOuterApron',160.85)
    side_vents=[Part.makeBox(4,3.5,17,V(160,y,48)) for y in range(-100,101,9)]
    m.cut('RightOuterApron',side_vents,'Upper right-side cooling grille').Refine=False
    for i,(x,y) in enumerate([(x,y) for x in [-145,145] for y in [-115,115]]):
        m.ring('CasePillar'+str(i),'Separate lower case fixing pillar study',3.2,1.25,23.5,(x,y,2.5),'Frame',-4,'black',internal=True)
        m.ring('CaseUpperSpacer'+str(i),'Case-to-frame support sleeve',2.5,1.25,10,(x,y,26.8),'Frame',0,'black',internal=True)
        m.screw('CaseFixing'+str(i),(x,y,38.6),'Frame',3,length=34,radius=2.2,axis=(0,0,-1))
    mounts=[(x,y) for x in [-145,145] for y in [-115,115]]
    for key,z,h,r in [('MainPCB',29.5,2,2.8),('UpperBoardShield',36.8,1,1.5),('LowerBoardShield',26.1,1,1.5)]:
        m.cut(key,[Part.makeCylinder(r,h,V(x,y,z)) for x,y in mounts],'Outer fixing-stack clearance').Refine=False
    m.label('TopWordmark','PLAYSTATION 3',9,(-44,-3,98.1),'Body',8,'chrome')
    bottom=g.rotation((0,0,-1),(0,1,0))
    m.box('BottomModelPlate','Separate lower model-identification label',110,34,.05,(-10,22,-.02),'Body',-6,'black',1,orient=bottom)
    m.label('BottomModelMark','CECHA00 / CAD STUDY',2.5,(18,20,-.085),'Body',-6,'white',rotation=bottom)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=17
    m.checkpoint(17,'curved_outer_aprons_case_fixings_and_model_marks','补齐弧形外端裙、上侧贯通通风、四处独立机壳固定堆叠以及型号学习标识。原生端裙与上盖保持分件，局部轮廓和固定位置为照片指导近似。')
    m.snapshot('17_complete_console_exterior',assemblies=['Body','Frame','FrontIO','Ports','Controls'],normal=(.25,-1.6,.85))


STAGES[17]=stage17


def _six_point(x,y,z):
    return V(x,y-250,z)


def _six_loft(m,key,profiles):
    from .ps1 import _controller_profile_curves
    sketches=[]
    for i,(sx,sy,z) in enumerate(profiles):
        sk=m.doc.addObject('Sketcher::SketchObject',key+'Profile'+str(i));sk.Label='SIXAXIS editable shell section '+str(i+1)
        for curve in _controller_profile_curves(sx*1.09,sy*1.07,1.2 if 'Inner' in key else 0):sk.addGeometry(curve,False)
        sk.Placement=App.Placement(_six_point(0,0,z),App.Rotation());m.group('Construction').addObject(sk);sketches.append(sk)
    loft=m.doc.addObject('Part::Loft',key);loft.Sections=sketches;loft.Solid=True;loft.Ruled=False;loft.Closed=False;loft.MaxDegree=3
    m.doc.recompute();assert loft.Shape.isValid() and len(loft.Shape.Solids)==1 and loft.Shape.Volume>0;loft.Shape.check(True)
    m.group('Construction').addObject(loft)
    for sk in sketches:sk.Visibility=False
    loft.Visibility=False;return loft


def _six_shell(m,key,outer,inner,layer):
    a=_six_loft(m,key+'Outer',outer);b=_six_loft(m,key+'Inner',inner)
    obj=m.doc.addObject('Part::Cut',key);obj.Base=a;obj.Tool=b;obj.Refine=False
    m.doc.recompute();assert obj.Shape.isValid() and len(obj.Shape.Solids)==1 and obj.Shape.Volume>0;obj.Shape.check(True)
    a.Visibility=False;b.Visibility=False
    return m.register(obj,key,'Controller',layer,'sixblack')


def stage18(m):
    from .ps1 import _add_shape
    m.colors['sixblack']=(.09,.10,.115)
    _six_shell(m,'SIXBack',[(.89,.90,1),(.96,.96,5),(1,1,12),(1,1,19.8)],[(.83,.84,3.3),(.92,.92,7),(.967,.966,13),(.967,.966,20.05)],-4)
    _six_shell(m,'SIXFront',[(1,1,20.1),(.994,.992,26),(.960,.955,31)],[(.966,.966,19.95),(.957,.950,26),(.935,.925,28.7)],4)
    front=[];back=[];inner_front=[];inner_back=[];openings=[]
    for side in [-1,1]:
        x=side*23
        back.append(Part.makeCylinder(17,15.8,_six_point(x,-23,4)))
        front.append(Part.makeCylinder(17,12.4,_six_point(x,-23,20.1)))
        inner_back.append(Part.makeCylinder(15.5,14.7,_six_point(x,-23,5.5)))
        inner_front.append(Part.makeCylinder(15.5,11.25,_six_point(x,-23,19.95)))
        openings.append(Part.makeCylinder(12.1,2.6,_six_point(x,-23,30.8)))
        face=Part.makeCylinder(24,2.0,_six_point(side*47,7,30.7))
        face=face.makeFillet(.7,[e for e in face.Edges if e.BoundBox.ZLength<1e-7 and e.BoundBox.ZMax>32.6]);front.append(face)
        front.append(m.rr(23,13,11,tuple(_six_point(side*47,34,20.1)),2))
        back.append(m.rr(23,13,7.8,tuple(_six_point(side*47,34,12.0)),2))
    _add_shape(m,'SIXBack',Part.makeCompound(back),'Integral lower analogue-stick cups and shoulder housings').Refine=False
    m.cut('SIXBack',inner_back,'Hollow lower analogue-stick cups').Refine=False
    _add_shape(m,'SIXFront',front[0].multiFuse(front[1:]).removeSplitter(),'Integral upper analogue-stick pods and circular control faces').Refine=False
    m.cut('SIXFront',inner_front+openings,'Analogue-stick pod cavities and real stick openings').Refine=False
    m.snapshot('18_sixaxis_shell',assemblies=['Controller'],normal=(.3,-.6,2))
    m.profile['stages']=18
    m.checkpoint(18,'sixaxis_native_shell_and_analogue_pods','建立 SIXAXIS 的上下原生曲线放样壳、双摇杆杯形舱、圆形按键面与两层肩键罩；保留壳体分缝和真正贯穿的摇杆开孔，局部尺寸为照片指导的学习近似。')


STAGES[18]=stage18


def _six_symbol(m,key,kind,x,y,z,material):
    from .psp import _polygon
    x,y,z=tuple(_six_point(x,y,z))
    if kind=='Triangle':
        shape=_polygon([(x,y+3),(x-2.8,y-2.1),(x+2.8,y-2.1)],z,.025).cut(_polygon([(x,y+2.22),(x-2.15,y-1.72),(x+2.15,y-1.72)],z-.01,.05))
    elif kind=='Circle':shape=Part.makeCylinder(3,.025,V(x,y,z)).cut(Part.makeCylinder(2.6,.05,V(x,y,z-.01)))
    elif kind=='Square':shape=m.rr(5.6,5.6,.025,(x,y,z),.08).cut(m.rr(4.8,4.8,.05,(x,y,z-.01),.04))
    else:
        strips=[]
        for angle in [-45,45]:
            strip=m.rr(.42,7,.025,(x,y,z),.06);strip.rotate(V(x,y,z),V(0,0,1),angle);strips.append(strip)
        shape=strips[0].fuse(strips[1])
    m.feature(key,kind+' face-button symbol',shape,'Controller',6,material)




def stage19(m):
    from .psp import _polygon
    from .ps1 import _add_shape
    m.colors.update({'buttonblack':(.17,.18,.20),'ctrlcyan':(.20,.69,.63),'ctrlcoral':(.79,.34,.29),'ctrlblue':(.27,.57,.84),'ctrlpurple':(.74,.35,.60),'stickrubber':(.10,.11,.12)})
    _add_shape(m,'SIXFront',m.rr(16,13,10.9,tuple(_six_point(0,-18,20.1)),1),'Central analogue-button bridge').Refine=False
    m.cut('SIXFront',m.rr(13,10,8.75,tuple(_six_point(0,-18,19.95)),.7),'Central bridge interior').Refine=False
    _add_shape(m,'SIXBack',m.rr(16,13,15.8,tuple(_six_point(0,-18,4)),1),'Lower central bridge').Refine=False
    m.cut('SIXBack',m.rr(13,10,14.7,tuple(_six_point(0,-18,5.5)),.7),'Lower bridge interior').Refine=False
    caps=[];holes=[];pivot=_six_point(-47,7,0)
    outline=[(-3,2.4),(3,2.4),(4.1,9.5),(0,12),(-4.1,9.5)]
    for name,angle in [('Up',0),('Right',-90),('Down',180),('Left',90)]:
        cap=_polygon([(-47+x,-243+y) for x,y in outline],32.05,2.75)
        cap=cap.makeFillet(.4,[e for e in cap.Edges if e.BoundBox.ZLength>2.74])
        cap=cap.fuse(Part.makeCylinder(1.8,5.7,_six_point(-47,13.8,26.5)))
        cap.rotate(pivot,V(0,0,1),angle);caps.append(cap)
        hole=_polygon([(-47+x*1.09,-243+y*1.09) for x,y in outline],28.4,7);hole.rotate(pivot,V(0,0,1),angle);holes.append(hole)
    cross=Part.makeBox(5,23,.8,_six_point(-49.5,-4.5,26.6)).fuse(Part.makeBox(23,5,.8,_six_point(-58.5,4.5,26.6)))
    cross=cross.fuse(Part.makeCylinder(2.4,1.4,_six_point(-47,7,25.3)))
    m.feature('SIXDPad','Linked four-way directional rocker',cross.multiFuse(caps),'Controller',5,'buttonblack')
    for name,dx,dy,mat in [('Triangle',0,11,'ctrlcyan'),('Circle',11,0,'ctrlcoral'),('Cross',0,-11,'ctrlblue'),('Square',-11,0,'ctrlpurple')]:
        x,y=47+dx,7+dy
        cap=Part.makeCylinder(4.5,5.4,_six_point(x,y,29.3))
        cap=cap.makeFillet(.35,[e for e in cap.Edges if e.BoundBox.ZLength<1e-7 and e.BoundBox.ZMax>34.6])
        cap=cap.fuse(Part.makeCylinder(1.55,2.9,_six_point(x,y,26.5)))
        cap=cap.multiFuse([Part.makeBox(1.7,2,.6,_six_point(x+3.8,y-1,29.4)),Part.makeBox(1.7,2,.6,_six_point(x-5.5,y-1,29.4))])
        m.feature('SIXButton'+name,name+' pressure-button cap and locating ears',cap,'Controller',5,'buttonblack')
        _six_symbol(m,'SIXSymbol'+name,name,x,y,34.735,mat)
        holes += [Part.makeCylinder(4.8,7.3,_six_point(x,y,28.2)),Part.makeCylinder(5.8,2.2,_six_point(x,y,28.3))]
    for key,x,y,w,h in [('Select',-11.5,4,7,3.8)]:
        cap=m.rr(w,h,1.5,tuple(_six_point(x,y,30.8)),.6).fuse(Part.makeCylinder(1.2,4.4,_six_point(x,y,26.5)))
        m.feature('SIX'+key,key.upper()+' button',cap,'Controller',5,'buttonblack')
        holes.append(m.rr(w+.6,h+.6,7.1 if key=='Analog' else 5.2,tuple(_six_point(x,y,26.1 if key=='Analog' else 28)),.7))
    cap=_polygon([(8.2,-248.1),(8.2,-243.9),(14.4,-246)],30.8,1.5).fuse(Part.makeCylinder(1.2,4.4,_six_point(11.0,4,26.5)))
    m.feature('SIXStart','Triangular START button',cap,'Controller',5,'buttonblack')
    holes.append(_polygon([(7.9,-248.5),(7.9,-243.5),(15.0,-246)],28,5.2))
    cap=Part.makeCylinder(3.9,1.6,_six_point(0,-11,30.8)).fuse(Part.makeCylinder(1.2,4.4,_six_point(0,-11,26.5)))
    m.feature('SIXPSButton','Original round PS button',cap,'Controller',5,'buttonblack')
    holes += [Part.makeCylinder(4.25,7,_six_point(0,-11,28)),Part.makeCylinder(5.2,1.8,_six_point(0,-11,28.5))]
    m.ring('SIXPSRetainer','Separate PS-button retaining ring',4.9,4.3,1,tuple(_six_point(0,-11,29)),'Controller',4,'white',internal=True)
    m.label('SIXPSMark','PS',1.8,tuple(_six_point(-1.4,-11.7,32.435)),'Controller',6,'white')
    m.cut('SIXFront',holes,'Directional, face, menu and indicator openings').Refine=False
    for key,text,size,x,y in [('Sony','SONY',3.6,-9,22),('Select','SELECT',1.25,-18,-1.7),('Start','START',1.25,7,-1.7)]:
        m.label('SIX'+key+'Mark',text,size,tuple(_six_point(x,y,31.025)),'Controller',6,'white')
    rear=g.rotation((0,1,0),(0,0,1))
    for side in [-1,1]:
        x=side*47;name='L' if side<0 else 'R'
        for tier,z in [(1,25.5)]:
            shell='SIXFront' if tier==1 else 'SIXBack'
            m.cut(shell,m.rr(19.2,7.2,16,tuple(_six_point(x,27.1,z)),.85,rear),name+str(tier)+' shoulder actuator opening').Refine=False
            cap=m.rr(18.4,6.4,2.2,tuple(_six_point(x,39,z)),.75,rear)
            stem=m.rr(4,3,8.1,tuple(_six_point(x,31,z)),.25,rear)
            m.feature('SIX'+name+str(tier),name+str(tier)+' shoulder key and stem',cap.fuse(stem),'Controller',5,'buttonblack')
            m.label('SIX'+name+str(tier)+'Mark',str(tier),2,tuple(_six_point(x+.5,41.225,z-.7)),'Controller',6,'white',rotation=rear)
        m.label('SIXShoulder'+name,name,2.0,tuple(_six_point(x-.7,36,31.125)),'Controller',6,'white')
    for i,x in enumerate([-23,23]):
        center=_six_point(x,-23,25)
        dome=Part.makeSphere(12,center).cut(Part.makeSphere(10.6,center)).common(Part.makeBox(30,30,9.6,_six_point(x-15,-38,22.5)))
        dome=dome.multiFuse([Part.makeCylinder(10,.45,_six_point(x,-23,31.9)),Part.makeCylinder(3,9.3,_six_point(x,-23,24))])
        dome=dome.cut(Part.makeCylinder(2.0,6.3,_six_point(x,-23,23.8)))
        m.feature('SIXStickDome'+str(i),'Analogue stick hard dome and keyed stem study',dome,'Controller',5,'buttonblack')
        crown=Part.makeSphere(16,_six_point(x,-23,22.8)).common(Part.makeCylinder(11.05,5,_six_point(x,-23,34.4)))
        cap=Part.makeCylinder(10.7,1,_six_point(x,-23,33.5)).fuse(crown)
        m.feature('SIXStickCap'+str(i),'Convex rubber analogue thumb cap',cap,'Controller',6,'stickrubber')
    m.snapshot('19_sixaxis_controls',assemblies=['Controller'],normal=(.2,-.5,2))
    m.profile['stages']=19
    m.checkpoint(19,'sixaxis_directional_face_ps_and_analogue_controls','建立早期 SIXAXIS 的方向/四符号面键、SELECT / START、圆形 PS 键及独立限位环、L1/R1 与双摇杆球罩和凸面帽；无线指示、Mini-B 和转轴式 L2/R2 在后续轮次补齐，保留首发无振动结构。')


STAGES[19]=stage19




def stage20(m):
    from .ps1 import _add_shape
    from .psp import _polygon
    m.colors.update(ctrlcream=(.79,.80,.66),ctrlflex=(.16,.47,.37))
    m.native('SIXPCB','Early SIXAXIS mainboard layout study',84,30,.8,.8,tuple(_six_point(0,8,13)),'Controller',0,'pcb')
    extensions=[m.rr(10,12,.8,tuple(_six_point(0,-13,13)),.4),m.rr(12,5,.8,tuple(_six_point(0,23.5,13)),.4)]
    for x in [-23,23]:extensions += [Part.makeCylinder(12,.8,_six_point(x,-23,13)),m.rr(24,19,.8,tuple(_six_point(x,-15.5,13)),.5)]
    _add_shape(m,'SIXPCB',extensions[0].multiFuse(extensions[1:]).removeSplitter(),'Analogue module lobes and Mini-B mounting tongue').Refine=False
    mounts=[(-35,18),(35,18),(-35,-4),(35,-4),(0,18)]
    m.cut('SIXPCB',[Part.makeCylinder(1,1.3,_six_point(x,y,12.75)) for x,y in mounts],'Carrier locating and retaining holes').Refine=False
    m.box('SIXControlIC','Wireless-controller processing package study',12,12,1.5,tuple(_six_point(-16,10,11.2)),'Controller',-1,'black',.3,True)
    for side in [-1,1]:
        for i in range(11):
            m.box('SIXControlLeadX'+str(side)+'_'+str(i),'Independent controller IC lead study',1,.28,.15,tuple(_six_point(-16+side*6.65,10+(i-5)*.9,12.5)),'Controller',0,'metal',.02,True)
            m.box('SIXControlLeadY'+str(side)+'_'+str(i),'Independent controller IC lead study',.28,1,.15,tuple(_six_point(-16+(i-5)*.9,10+side*6.65,12.5)),'Controller',0,'metal',.02,True)
    m.box('SIXChargeIC','Battery-charge control package study',7,7,1.1,tuple(_six_point(26,10,11.6)),'Controller',-1,'black',.2,True)
    m.box('SIXCrystal','Wireless controller crystal study',5,3,1,tuple(_six_point(6,17,11.7)),'Controller',-1,'metal',.2,True)
    for i,(x,y) in enumerate([(-30,8),(-26,8),(-7,8),(-3,8),(8,8),(12,8),(27,-4),(32,-2)]):m.box('SIXBypass'+str(i),'Separate controller bypass component',1.8,.9,.5,tuple(_six_point(x,y,12.3)),'Controller',-1,'metal',.1,True)
    outline=[(-55,26),(55,26),(64,17),(63,-5),(56,-11),(38,-11),(34,-17),(11,-17),(5,-13),(5,-20),(-5,-20),(-5,-13),(-11,-17),(-34,-17),(-38,-11),(-56,-11),(-63,-5),(-64,17)]
    carrier=_polygon([(x,y-250) for x,y in outline],20.5,1.2)
    wells=[Part.makeCylinder(17.4,1.8,_six_point(x,-23,20.2)) for x in [-23,23]]
    m.feature('SIXCarrier','Early SIXAXIS button carrier with separate sensor location',carrier.cut(Part.makeCompound(wells)),'Controller',1,'black',True)
    posts=[]
    for i,(x,y) in enumerate(mounts):
        post=Part.makeCylinder(2.4 if i==4 else 1.6,6.6,_six_point(x,y,13.95))
        if i==4:post=post.cut(Part.makeCylinder(.9,8,_six_point(x,y,13.7)))
        else:post=post.fuse(Part.makeCylinder(.8,1.3,_six_point(x,y,12.8)))
        posts.append(post)
    _add_shape(m,'SIXCarrier',Part.makeCompound(posts),'Carrier support posts and mainboard locating pins').Refine=False
    m.cut('SIXCarrier',Part.makeCylinder(.9,8.5,_six_point(0,18,13.5)),'Mainboard retaining screw pilot').Refine=False
    m.screw('SIXBoardScrew',tuple(_six_point(0,18,11.9)),'Controller',0,length=8.5,radius=1.7)
    film=_polygon([(x*.985,(y-8)*.985+8-250) for x,y in outline],21.83,.08)
    film=film.cut(Part.makeCompound([Part.makeCylinder(17.6,.5,_six_point(x,-23,21.6)) for x in [-23,23]]))
    m.feature('SIXFlex','Separate pressure-button contact film study',film,'Controller',2,'ctrlflex',True)
    m.native('SIXMotionPCB','Early separate motion-sensor board study',8,12,.6,.7,tuple(_six_point(0,18,23)),'Controller',2,'pcb')
    m.box('SIXMotionIC','Motion-sensor package envelope',3.5,3.5,.8,tuple(_six_point(0,18,23.9)),'Controller',3,'black',.25,True)
    for i,x in enumerate([-2.5,0,2.5]):m.box('SIXMotionTerminal'+str(i),'Separate three-wire sensor terminal',.7,1.3,.12,tuple(_six_point(x,12.8,23.9)),'Controller',3,'gold',.1,True)
    case=m.rr(42,30,5.5,tuple(_six_point(0,9,5.3)),1.5).cut(m.rr(40.8,28.8,4.3,tuple(_six_point(0,9,5.85)),1))
    m.feature('SIXBatteryCase','LIP1359-family 3.7 V / 610 mAh pack enclosure study',case,'Controller',-2,'battery',True)
    m.box('SIXBatteryCell','Separate rechargeable cell envelope',39,27,3.1,tuple(_six_point(0,9,6.2)),'Controller',-2,'metal',1,True)
    m.box('SIXBatteryProtectionPCB','Battery protection-board envelope',30,4,.4,tuple(_six_point(0,20,9.5)),'Controller',-1,'pcb',.3,True)
    m.box('SIXBatteryProtectionIC','Pack protection component study',3,2,.15,tuple(_six_point(0,20,9.95)),'Controller',-1,'black',.15,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.cut('SIXBack',[m.rr(25,20,1.5,tuple(_six_point(x,-15.5,12.65)),.5) for x in [-23,23]]+[m.rr(11,12.5,1.5,tuple(_six_point(0,-13,12.65)),.4)],'PCB lobe passages into the lower stick cups').Refine=False
    m.profile['stages']=20
    m.checkpoint(20,'sixaxis_native_board_contact_film_motion_board_and_battery','建立早期 SIXAXIS 主板、控制/充电封装、按键承托与柔性接点膜、独立运动传感器小板及 3.7V / 610mAh 电池包结构。电池参数据原版手册，局部板型与器件为照片指导示意，无振动电机。')
    m.snapshot('20_sixaxis_electronics',assemblies=['Controller'],exclude=['SIXFront','SIXBack','SIXBatteryCase'],normal=(.2,-.5,2))


STAGES[20]=stage20


def _six_membrane(m,key,centres,web,material,small=False):
    radius=4.2 if small else 5.2;outer=3.2 if small else 4.6;top=2.2 if small else 3.0
    disks=[Part.makeCylinder(radius,.4,_six_point(x,y,22.1)) for x,y in centres]
    base=disks[0].multiFuse(disks[1:]+web)
    domes=[]
    for i,(x,y) in enumerate(centres):
        base=base.cut(Part.makeCylinder(outer-.2,.8,_six_point(x,y,21.95)))
        dome=Part.makeCone(outer,top,3.5,_six_point(x,y,22.48)).fuse(Part.makeCylinder(top,.45,_six_point(x,y,25.95)))
        dome=dome.cut(Part.makeCone(outer-.6,top-.6,3.55,_six_point(x,y,22.3)));domes.append(dome)
        m.cyl(key+'Pill'+str(i),'Moving carbon button contact',1.5 if small else 2.0,.2,tuple(_six_point(x,y,25.6)),'Controller',3,'black',internal=True)
        fixed=Part.makeCylinder(1.8 if small else 2.3,.04,_six_point(x,y,21.95)).cut(Part.makeBox(.3,5,.1,_six_point(x-.15,y-2.5,21.92)))
        m.feature(key+'Fixed'+str(i),'Split fixed film contact',fixed,'Controller',2,'black',True)
    shape=base.multiFuse(domes).removeSplitter()
    if key=='SIXDPadMembrane':shape=shape.cut(Part.makeCylinder(2.0,1.0,_six_point(-47,7,21.9)))
    m.feature(key,'Shaped silicone button membrane',shape,'Controller',3,material,True)


def stage21(m):
    from .ps1 import _add_shape
    m.colors.update({'ctrlmint':(.58,.76,.67),'ctrlpad':(.82,.75,.49)})
    dpad=[(-47,13.8),(-40.2,7),(-47,.2),(-53.8,7)]
    face=[(47,18),(58,7),(47,-4),(36,7)]
    _six_membrane(m,'SIXDPadMembrane',dpad,[Part.makeCylinder(4.5,.4,_six_point(-47,7,22.1))],'ctrlpad')
    _six_membrane(m,'SIXFaceMembrane',face,[Part.makeCylinder(8,.4,_six_point(47,7,22.1))],'ctrlmint')
    web=[Part.makeBox(30,4,.4,_six_point(-15,2,22.1)),Part.makeBox(4,15,.4,_six_point(-2,-11,22.1))]
    _six_membrane(m,'SIXMenuMembrane',[(-11.5,4),(11,4),(0,-11)],web,'rubber',True)
    pivot=Part.makeCylinder(1.8,2.45,_six_point(-47,7,21.75)).fuse(Part.makeCylinder(2.7,1.05,_six_point(-47,7,24.1)))
    m.feature('SIXDPadPivot','Directional rocker pivot support',pivot,'Controller',3,'ctrlcream',True)
    rear=g.rotation((0,1,0),(0,0,1));supports=[];film_tabs=[]
    for side in [-1,1]:
        x=side*47;name='L' if side<0 else 'R'
        supports.append(m.rr(11,18,.45,tuple(_six_point(x,25.6,20.75)),.5,rear))
        tab=m.rr(10,17,.08,tuple(_six_point(x,26.1,20.75)),.4,rear)
        tab=tab.fuse(Part.makeBox(10,.68,.08,_six_point(x-5,25.5,21.83)));film_tabs.append(tab)
        for tier,z in [(1,25.5),(2,16)]:
            key='SIXShoulder'+name+str(tier)
            base=Part.makeCylinder(3.7,.25,_six_point(x,26.35,z),V(0,1,0)).cut(Part.makeCylinder(2.9,.7,_six_point(x,26.2,z),V(0,1,0)))
            dome=Part.makeCone(3.1,2.6,3.62,_six_point(x,26.58,z),V(0,1,0)).fuse(Part.makeCylinder(2.6,.65,_six_point(x,30.15,z),V(0,1,0)))
            dome=dome.cut(Part.makeCone(2.65,2.15,3.75,_six_point(x,26.5,z),V(0,1,0)))
            m.feature(key+'Membrane','Shoulder-key silicone dome',base.fuse(dome),'Controller',3,'ctrlpad',True)
            m.cyl(key+'Pill','Shoulder moving carbon contact',1.8,.18,tuple(_six_point(x,30,z)),'Controller',3,'black',axis=(0,1,0),internal=True)
            fixed=Part.makeCylinder(1.9,.04,_six_point(x,26.23,z),V(0,1,0)).cut(Part.makeBox(.3,.1,5,_six_point(x-.15,26.20,z-2.5)))
            m.feature(key+'Fixed','Shoulder fixed film contact',fixed,'Controller',2,'black',True)
    _add_shape(m,'SIXCarrier',Part.makeCompound(supports),'Two vertical shoulder-contact supports').Refine=False
    _add_shape(m,'SIXFlex',Part.makeCompound(film_tabs),'Folded contact-film shoulder wings').Refine=False
    from .psp import _polygon
    pivot=_six_point(-47,7,0);root_tools=[]
    outline=[(-3.5,1.9),(3.5,1.9),(4.7,10),(0,12.7),(-4.7,10)]
    for angle in [0,-90,180,90]:
        tool=_polygon([(-47+x,-243+y) for x,y in outline],31.8,3.5)
        tool.rotate(pivot,V(0,0,1),angle);root_tools.append(tool)
    m.cut('SIXFront',root_tools,'Separate directional rocker root clearances').Refine=False
    # Allow the real membrane carrier and PCB lobes inside the curved shell.
    m.cut('SIXFront',[m.rr(13,19,8.8,tuple(_six_point(0,-14,19.95)),.7),m.rr(17,6,2.7,tuple(_six_point(0,-13,19.95)),.4)]+[m.rr(12,3.4,18.8,tuple(_six_point(x,26.2,11)),.5) for x in [-47,47]],'Menu membrane and shoulder-film support clearances').Refine=False
    m.cut('SIXFlex',Part.makeCylinder(2.0,.5,_six_point(-47,7,21.6)),'Directional rocker pivot passage through film').Refine=False
    m.cut('SIXCarrier',[Part.makeBox(12,1.0,.3,_six_point(x-6,25.4,21.75)) for x in [-47,47]],'Shoulder-film fold seats').Refine=False
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=21
    m.checkpoint(21,'sixaxis_silicone_membranes_and_pressure_contacts','建立方向键、面键与菜单键硅胶膜及独立动静碳接点，加入方向键支点、两侧肩键竖向支架、接点膜折翼和四个肩键胶碗。')



STAGES[21]=stage21


def _six_joystick(m,index,x,y):
    from .atari2600 import _helical_spring
    key='SIXJoy'+str(index);y-=250;holes=[]
    m.box(key+'Base','Joystick insulating base',16,16,1.4,(x,y,14.1),'Controller',1,'black',.6,True)
    cage=m.rr(17.5,17.5,6.4,(x,y,15.6),.7).cut(m.rr(16.3,16.3,6.8,(x,y,15.4),.2))
    roof=m.rr(17.5,17.5,.55,(x,y,21.45),.7).cut(Part.makeCylinder(6.2,1,V(x,y,21.2)))
    feet=[Part.makeBox(.6,.6,2.9,V(x+dx-.3,y+dy-.3,12.85)) for dx in [-7.9,7.9] for dy in [-7.9,7.9]]
    cage=cage.multiFuse([roof]+feet)
    cage=cage.cut(Part.makeCompound([Part.makeCylinder(1.15,21,V(x-10,y,19.2),V(1,0,0)),Part.makeCylinder(.95,21,V(x,y-10,19.9),V(0,1,0))]))
    m.feature(key+'Frame','Stamped joystick cage, cap and board legs',cage,'Controller',2,'metal',True)
    outer=m.rr(13,11,2,(x,y,18.2),.45).cut(m.rr(10.8,8.8,2.4,(x,y,18),.3))
    outer=outer.multiFuse([Part.makeCylinder(1,3.5,V(x-8.6,y,19.2),V(1,0,0)),Part.makeCylinder(1,5.25,V(x+5.1,y,19.2),V(1,0,0))])
    outer=outer.cut(Part.makeCylinder(.95,21,V(x,y-10,19.9),V(0,1,0)))
    m.feature(key+'OuterGimbal','X-axis gimbal and potentiometer axle',outer,'Controller',2,'ctrlcream',True)
    inner=m.rr(9.5,8.5,1.5,(x,y,19.15),.4).cut(m.rr(7,6.2,1.9,(x,y,18.95),.2))
    inner=inner.multiFuse([Part.makeCylinder(.75,4.8,V(x,y-7.9,19.9),V(0,1,0)),Part.makeCylinder(.75,7.3,V(x,y+3.05,19.9),V(0,1,0))])
    inner=inner.cut(Part.makeCylinder(1.0,11,V(x-5.5,y,20),V(1,0,0)))
    m.feature(key+'InnerGimbal','Y-axis gimbal and potentiometer axle',inner,'Controller',2,'ctrlcream',True)
    shaft=Part.makeSphere(2.2,V(x,y,20.8)).fuse(Part.makeCylinder(1.75,8.55,V(x,y,21.3)))
    shaft=shaft.fuse(Part.makeCylinder(.8,9.2,V(x-4.6,y,20),V(1,0,0)))
    m.feature(key+'Shaft','Joystick pivot ball, cross pin and cap shaft',shaft,'Controller',3,'metal',True)
    spring=_helical_spring(1.2,.6,1.8,.12);spring.translate(V(x,y,15.8))
    m.feature(key+'ClickSpring','Joystick push-click return spring study',spring,'Controller',1,'metal',True)
    m.box(key+'ClickSwitch','L3/R3 click switch body',3,3,1.5,(x-5,y,15.8),'Controller',1,'black',.3,True)
    m.cyl(key+'ClickActuator','L3/R3 switch actuator',.8,.4,(x-5,y,17.4),'Controller',2,'black',internal=True)
    m.box(key+'ClickLever','Joystick click transfer lever',6,1.2,.2,(x-2.5,y,17.9),'Controller',2,'metal',.12,True)
    base_bores=[]
    for dx in [-7.9,7.9]:
        for dy in [-7.9,7.9]:
            holes.append(Part.makeCylinder(.5,1.4,V(x+dx,y+dy,12.7)))
            base_bores.append(Part.makeCylinder(.55,1.9,V(x+dx,y+dy,13.9)))
    for i,dx in enumerate([-6.7,-3.3]):
        m.cyl(key+'ClickPin'+str(i),'Click-switch board terminal',.2,3.15,(x+dx,y,12.85),'Controller',1,'metal',internal=True)
        holes.append(Part.makeCylinder(.35,1.4,V(x+dx,y,12.7)));base_bores.append(Part.makeCylinder(.35,1.9,V(x+dx,y,13.9)))
    m.cut(key+'Base',base_bores,'Joystick anchor and click terminal passages').Refine=False
    m.colors['potcyan']=(.06,.52,.59)
    for axis,z in [((1,0,0),19.2),((0,1,0),19.9)]:
        suffix='X' if axis[0] else 'Y';normal=V(*axis);q=g.rotation(axis,(0,0,1));origin=V(x,y,18.95)+normal*8.95
        body=m.rr(6.8,6.4,2.3,tuple(origin),.4,q)
        center=V(x,y,z)
        body=body.cut(Part.makeCylinder(2.65,1.5,center+normal*10.0,normal)).cut(Part.makeCylinder(1.15,2.9,center+normal*8.7,normal))
        pinholes=[]
        for i,offset in enumerate([-2.2,0,2.2]):
            xx=x+10.2 if axis[0] else x+offset;yy=y+offset if axis[0] else y+10.2
            m.cyl(key+suffix+'Pin'+str(i),'Potentiometer board terminal',.2,3.1,(xx,yy,12.85),'Controller',1,'metal',internal=True)
            holes.append(Part.makeCylinder(.35,1.4,V(xx,yy,12.7)));pinholes.append(Part.makeCylinder(.35,.8,V(xx,yy,15.5)))
        m.feature(key+suffix+'Pot','Cyan potentiometer housing',body.cut(Part.makeCompound(pinholes)),'Controller',2,'potcyan',True)
        rotor=Part.makeCylinder(2.3,.25,center+normal*10.35,normal).cut(Part.makeCylinder(1.05,.5,center+normal*10.2,normal))
        m.feature(key+suffix+'Rotor','Potentiometer rotor disc',rotor,'Controller',2,'ctrlcream',True)
        m.ring(key+suffix+'Track','Potentiometer resistive track',2.25,1.7,.035,tuple(center+normal*10.68),'Controller',2,'black',axis=axis,internal=True)
        wiper=m.rr(.35,2.6,.05,tuple(center+normal*10.80),.05,q)
        m.feature(key+suffix+'Wiper','Potentiometer moving wiper study',wiper,'Controller',2,'metal',True)
    return holes


def stage22(m):
    holes=[]
    for i,x in enumerate([-23,23]):holes += _six_joystick(m,i,x,-23)
    m.cut('SIXPCB',holes,'Analogue-module anchors, potentiometer and click-switch terminal holes').Refine=False
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=22
    m.checkpoint(22,'sixaxis_two_axis_gimbals_potentiometers_and_clicks','建立两个摇杆的金属框架、双轴万向支架、球轴与摇杆杆、两侧电位器、电阻轨道和触点，并加入 L3/R3 按下开关、回位弹簧及独立穿板端子。')



STAGES[22]=stage22


def stage23(m):
    from .atari2600 import _helical_spring
    rear=g.rotation((0,1,0),(0,0,1))
    for side in [-1,1]:
        x=side*47;key='SIX'+('L' if side<0 else 'R')+'2'
        # A curved finger lever around a separate transverse axle; the study is static.
        profile=[(35,18.5),(40.5,18.5),(43.5,14),(43,11.4),(39,12),(35,14)]
        points=[_six_point(x-9.2,y,z) for y,z in profile]
        cap=Part.Face(Part.Wire(Part.makePolygon(points+[points[0]]).Edges)).extrude(V(18.4,0,0))
        cap=cap.fuse(Part.makeCylinder(1.4,18.4,_six_point(x-9.2,35,17),V(1,0,0)))
        cap=cap.fuse(m.rr(4,4.9,2.5,tuple(_six_point(x,33.25,14.75)),.3))
        cap=cap.cut(Part.makeCylinder(.85,20,_six_point(x-10,35,17),V(1,0,0)))
        cap=cap.cut(Part.makeCylinder(2.1,4.2,_six_point(x-2.1,35,17),V(1,0,0)))
        m.feature(key,'Pivoted analogue '+key[-2:]+' finger lever study',cap,'Controller',4,'buttonblack')
        bars=[m.rr(2,8,8.4,tuple(_six_point(x+dx,34,11.1)),.35) for dx in [-11.4,11.4]]
        bracket=bars[0].fuse(bars[1]).fuse(m.rr(24.8,2,1,tuple(_six_point(x,31,11.1)),.25))
        bracket=bracket.cut(Part.makeCylinder(.9,27,_six_point(x-13.5,35,17),V(1,0,0)))
        m.feature(key+'Bracket','Separate trigger axle support bracket',bracket,'Controller',2,'black',True)
        m.cyl(key+'Axle','Independent transverse trigger hinge pin',.7,25,tuple(_six_point(x-12.5,35,17)),'Controller',3,'metal',axis=(1,0,0),internal=True)
        spring=_helical_spring(1.7,.55,3.2,.14);spring.rotate(V(),V(0,1,0),90);spring.translate(_six_point(x-1.6,35,17))
        m.feature(key+'Spring','Independent trigger return-coil study',spring,'Controller',3,'metal',True)
        m.cut('SIXBack',m.rr(26,11.5,19,tuple(_six_point(x,25.5,16)),1,rear),'Independent pivoted trigger and bracket passage').Refine=False
        m.label(key+'Mark','2',2,tuple(_six_point(x+.5,43.52,13.2)),'Controller',6,'white',rotation=rear)
        m.cut('SIXFront',m.rr(19.4,1.8,1.1,tuple(_six_point(x,39,20.05)),.25),'Separate shoulder-divider seat').Refine=False
        m.box(key+'Separator','Separate L1/L2 or R1/R2 divider',19,1.4,.8,tuple(_six_point(x,39,20.15)),'Controller',4,'black',.25)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=23
    m.checkpoint(23,'sixaxis_pivoted_l2_r2_and_return_springs','补齐 SIXAXIS 的转轴式 L2/R2、独立支架、金属轴、回位簧及肩键分隔件；压敏接点承接前轮胶膜，铰接和弹簧几何为静态机构学习近似。')
    m.snapshot('23_sixaxis_trigger_mechanism',assemblies=['Controller'],exclude=['SIXFront','SIXBack'],normal=(.3,1,1.5))


STAGES[23]=stage23


def stage24(m):
    from .ps1 import _add_shape
    rear=g.rotation((0,1,0),(0,0,1))
    def prism(outline,y,depth):
        pts=[_six_point(x,y,19.6+z) for x,z in outline]
        return Part.Face(Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges)).extrude(V(0,depth,0))
    shell=prism([(-3.8,-1.7),(3.8,-1.7),(4,1.4),(-4,1.4)],25,6)
    shell=shell.cut(prism([(-3.52,-1.43),(3.52,-1.43),(3.7,1.13),(-3.7,1.13)],24.8,6.4))
    feet=[m.rr(.3,.6,5.5,tuple(_six_point(x,25.4,12.8)),.03) for x in [-3.7,3.7]]
    shell=shell.multiFuse(feet).removeSplitter()
    m.feature('SIXMiniBShell','Original five-contact Mini-B metal receptacle and board tabs',shell,'Controller',2,'metal',True)
    carrier=m.rr(6.5,2.3,1.5,tuple(_six_point(0,25,19.5)),.25,rear)
    tongue=m.rr(5.5,3.4,.55,tuple(_six_point(0,28.1,18.9)),.15)
    carrier=carrier.fuse(tongue);channels=[]
    for i in range(5):
        x=(i-2)*.8
        foot=m.rr(.32,1.5,.12,tuple(_six_point(x,23.8,13.95)),.03)
        stem=m.rr(.32,.32,5.6,tuple(_six_point(x,24.1,14.0)),.03)
        arm=m.rr(.32,5.65,.10,tuple(_six_point(x,26.775,19.49)),.03)
        m.feature('SIXMiniBContact'+str(i),'Independent formed Mini-B contact and solder tail',foot.fuse(stem).fuse(arm).removeSplitter(),'Controller',2,'gold',True)
        channels.append(m.rr(.45,2,.3,tuple(_six_point(x,25.8,19.4)),.03))
    m.feature('SIXMiniBCarrier','Separate Mini-B insulating carrier and tongue',carrier.cut(Part.makeCompound(channels)),'Controller',2,'black',True)
    m.cut('SIXPCB',[Part.makeCylinder(.46,1.4,_six_point(x,25.4,12.7)) for x in [-3.7,3.7]],'Mini-B shell anchor holes').Refine=False
    for key in ['SIXFront','SIXBack']:m.cut(key,m.rr(8.8,4.4,10,tuple(_six_point(0,23,19.5)),.5,rear),'Open rear Mini-B receptacle').Refine=False
    _add_shape(m,'SIXPCB',m.rr(20,5,.8,tuple(_six_point(13,24,13)),.6),'Rear four-indicator board tongue').Refine=False
    m.cut('SIXPCB',[Part.makeCylinder(.46,1.4,_six_point(x,25.4,12.7)) for x in [-3.7,3.7]],'Preserve connector anchor holes through the indicator tongue').Refine=False
    for key in ['SIXCarrier','SIXFlex']:m.cut(key,m.rr(9,4,4.8,tuple(_six_point(0,25.5,17.6)),.4),'Rear Mini-B clearance through the button carrier').Refine=False
    guides=[];windows=[]
    for i,x in enumerate([8,11,14,17],1):
        m.box('SIXPlayerLED'+str(i),'Independent red player-index emitter',.8,1.2,.6,tuple(_six_point(x,25.5,14.0)),'Controller',1,'red',.1,True)
        guide=m.rr(.7,.7,7.05,tuple(_six_point(x,25.5,14.75)),.1).fuse(m.rr(.7,4,.7,tuple(_six_point(x,27.2,21.45)),.1))
        m.feature('SIXPlayerGuide'+str(i),'Separate player-index light guide',guide,'Controller',3,'white',True)
        guides.append(m.rr(1.1,1.2,9,tuple(_six_point(x,25.5,14.3)),.1))
        windows.append(m.rr(1.2,1.2,9,tuple(_six_point(x,24,21.8)),.15,rear))
        m.label('SIXPlayerNumber'+str(i),str(i),1.1,tuple(_six_point(x-.4,24,31.025)),'Controller',6,'white')
    for key in ['SIXCarrier','SIXFlex']:m.cut(key,guides,'Individual player-light guide passages').Refine=False
    m.cut('SIXFront',windows,'Four separate rear player-indicator windows').Refine=False
    m.box('SIXResetSwitch','Recessed controller reset switch',3,3,1,tuple(_six_point(25,18,11.7)),'Controller',-1,'black',.3,True)
    m.cyl('SIXResetSwitchTip','Reset switch plunger',.55,.4,tuple(_six_point(25,18,11.2)),'Controller',-1,'white',internal=True)
    reset=Part.makeCylinder(.65,7.1,_six_point(25,18,3.8)).fuse(Part.makeCylinder(1.4,.7,_six_point(25,18,3.2)))
    m.feature('SIXResetExtension','Separate early SIXAXIS reset extension piece',reset,'Controller',-2,'white',True)
    m.cut('SIXBack',Part.makeCylinder(1.6,3.3,_six_point(25,18,.6)),'Recessed reset access and extension-piece seat').Refine=False
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=24
    m.checkpoint(24,'sixaxis_mini_b_player_indicators_and_reset_extension','补齐五接点 Mini-B 金属壳、绝缘舌与成形焊脚、四个独立编号指示灯和导光件，以及早期 SIXAXIS 可分离的复位延长件；接口与导光通道真实贯通。')
    m.snapshot('24_sixaxis_rear_interfaces',assemblies=['Controller'],normal=(.3,1,.9))


STAGES[24]=stage24


def stage25(m):
    from .ps1 import _add_shape
    from .ps2 import _flat_ribbon
    from .atari2600 import _rounded_route
    def socket(key,x,y,z,w,h,count,pitch):
        body=m.rr(w,h,2.1,tuple(_six_point(x,y,z)),.3).cut(m.rr(w-1.2,h-1.2,2,tuple(_six_point(x,y,z+.5)),.15))
        m.feature(key,'Separate controller wire/film socket',body,'Controller',1,'white',True)
        for i in range(count):m.box(key+'Contact'+str(i),'Independent socket terminal study',.25,1.3,.12,tuple(_six_point(x+(i-(count-1)/2)*pitch,y,z+.7)),'Controller',1,'gold',.02,True)
    socket('SIXFilmSocket',18,12,14,20,5,18,1)
    path=[tuple(_six_point(*p)) for p in [(18,12,15.25),(18,18,15.25),(18,18,22.4),(18,20,22.4),(18,20,21.88)]]
    tail=_flat_ribbon(path,18,bend=.14)
    m.cut('SIXCarrier',m.rr(18.6,.9,2.2,tuple(_six_point(18,18,20.3)),.2),'Folded button-film tail passage').Refine=False
    m.cut('SIXFlex',m.rr(18.6,.9,.4,tuple(_six_point(18,18,21.7)),.2),'Film-tail fold slit').Refine=False
    _add_shape(m,'SIXFlex',tail,'Connected flexible-film tail to the board socket').Refine=False
    m.cut('SIXFilmSocket',_flat_ribbon(path,18.3,.22,.14),'Real film-connector mouth').Refine=False
    socket('SIXMotionSocket',0,5,14,8,4,3,2.5)
    sensor_passages=[]
    for i,x in enumerate([-2.5,0,2.5]):
        path=[_six_point(*p) for p in [(x,12.8,24.3),(x,10.5,24.3),(x,10.5,17.4),(x,5,17.4),(x,5,15.5)]]
        m.feature('SIXMotionLead'+str(i),'Independent early three-wire motion-sensor lead',_rounded_route(path,.5,.15),'Controller',2,['red','white','black'][i],True)
        sensor_passages.append(Part.makeCylinder(.4,3,_six_point(x,10.5,20)))
    for key in ['SIXCarrier','SIXFlex']:m.cut(key,sensor_passages,'Three separated motion-sensor wire passages').Refine=False
    body=m.rr(4,6,3.4,tuple(_six_point(27,0,9.1)),.3).cut(m.rr(2.8,4.8,3,tuple(_six_point(27,0,9.6)),.15))
    paths=[]
    for i,y in enumerate([-1.2,1.2]):
        m.box('SIXBatteryTerminal'+str(i),'Separate two-pin battery connector contact',.3,.6,.12,tuple(_six_point(27,y,9.73)),'Controller',-1,'gold',.02,True)
        path=[_six_point(*p) for p in [(20.8,y,8.5),(24,y,8.5),(24,y,10.1),(27,y,10.1)]]
        m.feature('SIXBatteryLead'+str(i),'Independent insulated battery-pack lead',_rounded_route(path,.5,.22),'Controller',-1,'red' if i else 'black',True)
        paths.append(_rounded_route(path,.5,.42))
    m.feature('SIXBatterySocket','Two-position battery power socket',body.cut(Part.makeCompound(paths)),'Controller',-1,'white',True)
    m.cut('SIXBatteryCase',paths,'Battery-pack insulated lead exits').Refine=False
    reverse=g.rotation((0,0,-1),(0,1,0))
    m.label('SIXBatteryRating','3.7 V / 610 mAh',1.8,tuple(_six_point(13,3,5.25)),'Controller',-3,'white',rotation=reverse)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=25
    m.checkpoint(25,'sixaxis_film_tail_motion_sensor_and_battery_connections','连接按键薄膜折尾、独立运动传感板的三条引线及电池双线与插座，分别保留载架和电池外壳穿线通道。端点、颜色与接点数量是非功能性结构示意。')
    m.snapshot('25_sixaxis_interconnects',assemblies=['Controller'],exclude=['SIXFront','SIXBack'],normal=(.3,-.5,2))


STAGES[25]=stage25


def stage26(m):
    from .ps1 import _add_shape
    mounts=[(-61,17),(61,17),(0,-21),(-58,-43),(58,-43)]
    posts=[Part.makeCylinder(2.1,24.2,_six_point(x,y,5.5)) for x,y in mounts]
    _add_shape(m,'SIXFront',Part.makeCompound(posts),'Five original controller fixing pillars').Refine=False
    m.cut('SIXFront',[Part.makeCylinder(.85,23,_six_point(x,y,5.3)) for x,y in mounts],'Five blind controller screw pilots').Refine=False
    for key in ['SIXPCB','SIXCarrier','SIXFlex']:m.cut(key,[Part.makeCylinder(2.4,25,_six_point(x,y,5)) for x,y in mounts],'Five case-pillar passages').Refine=False
    bores=[]
    for i,(x,y) in enumerate(mounts):
        bores += [Part.makeCylinder(1,18,_six_point(x,y,.5)),Part.makeCylinder(1.9,3.2,_six_point(x,y,.5)),Part.makeCylinder(2.4,14.6,_six_point(x,y,5.3))]
        m.screw('SIXCaseScrew'+str(i),tuple(_six_point(x,y,3)),'Controller',-5,length=22,radius=1.5)
    m.cut('SIXBack',bores,'Five rear screw recesses and upper-pillar seats').Refine=False
    reverse=g.rotation((0,0,-1),(0,1,0))
    m.label('SIXRearModel','SIXAXIS / CAD STUDY',1.3,tuple(_six_point(13,3,.96)),'Controller',-5,'white',rotation=reverse)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=26
    m.checkpoint(26,'sixaxis_five_case_fixings_and_rear_identification','补齐首发无线控制器的五组后壳螺钉与上壳固定柱、穿板通道和型号学习标识；保留无振动电机的握把空间，随后核验整套静态装配。')
    m.snapshot('26_sixaxis_complete',assemblies=['Controller'],normal=(.2,-.5,2.4))


STAGES[26]=stage26


def stage27(m):
    from .atari2600 import _rounded_route
    # Original single-row twelve-contact AV MULTI plug, not a DIN connector.
    front=g.rotation((0,1,0),(0,0,1))
    m.box('AVPlugGrip','PlayStation AV MULTI connector grip',20.8,10,25,(220,-28,8),'Accessories',0,'black',1.2,orient=front)
    shield=m.rr(17.8,6.6,8.4,(220,-2.7,8),.65,front).cut(m.rr(16.8,5.6,9,(220,-2.9,8),.35,front))
    m.feature('AVPlugShield','Rectangular AV MULTI metal sleeve',shield,'Accessories',0,'metal')
    m.box('AVPlugCarrier','AV MULTI insulating tongue',16,1.3,6.3,(220,-2.6,8),'Accessories',0,'black',.15,True,orient=front)
    for i in range(12):
        m.box('AVPlugContact'+str(i),'AV MULTI contact '+str(i+1),.5,.14,6,(220+(i-5.5)*1.25,-1.8,8.78),'Accessories',0,'gold',.03,True,orient=front)
    points=[V(220,-28.2,8),V(220,-65,8),V(310,-65,8),V(310,-119.8,8)]
    m.feature('AVCable','AV cable display length',_rounded_route(points,7,1.9),'Accessories',0,'black')
    m.box('AVSplitter','Three-way AV cable splitter',14,8,10,(310,-124,3),'Accessories',0,'black',1)
    m.colors['yellow']=(.92,.75,.12)
    for i,(x,color) in enumerate([(282,'yellow'),(310,'white'),(338,'red')]):
        sx=307+i*3;points=[V(sx,-128.2,8),V(sx,-137,8),V(x,-146,8),V(x,-157.8,8)]
        m.feature('AVBranch'+str(i),'Individual RCA lead',_rounded_route(points,2,1.1),'Accessories',0,'black')
        m.cyl('RCAGrip'+str(i),'RCA connector grip',4.8,20,(x,-158,8),'Accessories',0,'black',axis=(0,-1,0))
        m.ring('RCAColor'+str(i),'RCA function-color ring',5.2,4.85,3,(x,-170,8),'Accessories',0,color,axis=(0,-1,0))
        m.ring('RCAGround'+str(i),'RCA ground sleeve',3.7,2.5,7,(x,-178.2,8),'Accessories',0,'metal',axis=(0,-1,0))
        m.cyl('RCACenter'+str(i),'RCA signal contact',.9,9,(x,-178.2,8),'Accessories',0,'gold',axis=(0,-1,0))
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=27
    m.checkpoint(27,'original_av_multi_to_three_rca_cable','加入原配 AV MULTI 至三 RCA 线，保留十二接点设备端和独立红白黄复合视频/音频端子；线长为缩短展示近似。')


STAGES[27]=stage27


def stage28(m):
    from .atari2600 import _rounded_route
    m.colors['wiregreen']=(.08,.34,.12)
    m.box('ACWallPlug','Original Japanese two-blade AC plug study',23,17,11,(220,130,0),'Accessories',0,'black',1.7)
    for i,x in enumerate([213.8,226.2]):m.box('ACWallBlade'+str(i),'Flat mains-plug blade',1.4,6.2,12.5,(x,130,11.1),'Accessories',0,'metal',.1)
    points=[V(220,121.3,5.5),V(220,55,5.5),V(350,55,8),V(350,100,8),V(302.2,100,8)]
    m.feature('ACCord','Original grounded AC cord display route',_rounded_route(points,7,1.8),'Accessories',0,'black')
    m.box('ACDeviceGrip','Three-position appliance connector overmould',24,21,15,(290,100,.5),'Accessories',0,'black',1.5)
    yz=[(-10,-6),(10,-6),(10,3),(6,7),(-6,7),(-10,3)]
    points=[V(277.8,100+y,8+z) for y,z in yz]
    head=Part.Face(Part.Wire(Part.makePolygon(points+[points[0]]).Edges)).extrude(V(-10,0,0))
    holes=[]
    for i,(y,z) in enumerate([(95,6),(105,6),(100,12)]):
        holes.append(Part.makeBox(10.6,2.3,4.5,V(267.5,y-1.15,z-2.25)))
        contact=Part.makeBox(6,1.85,4,V(269,y-.925,z-2)).cut(Part.makeBox(6.4,1.15,3.3,V(268.8,y-.575,z-1.65)))
        m.feature('ACDeviceContact'+str(i),'Independent appliance socket spring-contact envelope',contact,'Accessories',0,'metal',True)
    m.feature('ACDeviceHead','Three-position C13-family insulating head study',head.cut(Part.makeCompound(holes)),'Accessories',0,'black')
    points=[V(208.3,130,5.5),V(192,130,5.5),V(192,164,5.5),V(199,164,5.5)]
    m.feature('ACEarthLead','Separate Japanese earthing pigtail study',_rounded_route(points,3,.8),'Accessories',0,'wiregreen')
    fork=Part.makeCylinder(3,.4,V(205,164,5.3)).cut(Part.makeCylinder(1.4,.8,V(205,164,5.1)))
    fork=fork.cut(Part.makeBox(4,2.8,.8,V(205,162.6,5.1))).fuse(Part.makeBox(4.2,2,.4,V(199.2,163,5.3)))
    m.feature('ACEarthFork','Independent earthing fork terminal study',fork,'Accessories',0,'metal')
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=28
    m.checkpoint(28,'japanese_grounded_ac_cord_and_three_position_device_plug','依据日本原版快速参考的接地线说明，补齐两片日式电源插头、独立接地尾线及三位设备端插座；电缆为缩短展示路径，不提供电气制造数据。')


STAGES[28]=stage28


def stage29(m):
    from .atari2600 import _rounded_route
    rear=g.rotation((0,1,0),(0,0,1))
    points=[V(215,-264.2,6),V(215,-324,6),V(285,-324,6),V(285,-264.2,6)]
    m.feature('USBChargeCable','Original USB-A to Mini-B cable display length',_rounded_route(points,7,1.5),'Accessories',0,'black')
    m.box('USBAPlugGrip','USB-A cable overmould',18,23,10,(215,-252.5,1),'Accessories',0,'black',1.6)
    m.box('MiniBPlugGrip','Mini-B cable overmould',12,19,8,(285,-254.5,2),'Accessories',0,'black',1.3)
    for i,x in enumerate([215,285]):
        shape=Part.makeCylinder(1.9,6,V(x,-264.1,6),V(0,-1,0)).cut(Part.makeCylinder(1.55,6.4,V(x,-263.9,6),V(0,-1,0)))
        m.feature('USBChargeRelief'+str(i),'Cable strain-relief sleeve',shape,'Accessories',0,'black')
    shape=m.rr(12,4.5,12,(215,-240.8,6),.3,rear).cut(m.rr(11.4,3.9,12.4,(215,-241,6),.15,rear))
    m.feature('USBAPlugShield','USB-A plug metal shell',shape,'Accessories',0,'metal')
    m.box('USBAPlugStop','USB-A rear insulating stop',10.8,.65,3.3,(215,-240.4,4.35),'Accessories',0,'black',.15,True)
    m.box('USBAPlugTongue','Four-contact USB-A tongue',9.2,7,1,(215,-235.2,5),'Accessories',0,'black',.15)
    for i in range(4):m.box('USBAPlugContact'+str(i),'Independent USB-A plug contact',.85,5,.1,(215+(i-1.5)*2,-235.2,6.1),'Accessories',0,'gold',.05,True)
    def prism(outline,y,length):
        points=[V(285+x,y,6+z) for x,z in outline]
        return Part.Face(Part.Wire(Part.makePolygon(points+[points[0]]).Edges)).extrude(V(0,length,0))
    shell=prism([(-3.45,-1.65),(3.45,-1.65),(3.8,1.35),(-3.8,1.35)],-244.8,8)
    shell=shell.cut(prism([(-3.16,-1.38),(3.16,-1.38),(3.49,1.08),(-3.49,1.08)],-245,8.4))
    m.feature('MiniBPlugShield','Original Mini-B cable plug metal sleeve',shell,'Accessories',0,'metal')
    m.box('MiniBPlugStop','Mini-B rear insulating stop',6.2,1,.7,(285,-244.4,5.9),'Accessories',0,'black',.2,True,orient=rear)
    m.box('MiniBPlugRail','Mini-B five-contact insulating rail',5.3,5.5,.65,(285,-240.7,5.4),'Accessories',0,'black',.1,True)
    for i in range(5):m.box('MiniBPlugContact'+str(i),'Separate Mini-B cable plug contact',.3,4.8,.08,(285+(i-2)*.8,-240.7,6.12),'Accessories',0,'gold',.02,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=29
    m.checkpoint(29,'original_usb_a_to_mini_b_connection_cable','补齐原配 USB-A 至 Mini-B 线，分别建立双端包胶、护线套、金属壳、绝缘件及 4/5 个独立触点；保留原版控制器接口，不混入后续 USB-C。')


STAGES[29]=stage29


def stage30(m):
    from .atari2600 import _rounded_route
    m.colors['clearplug']=(.68,.72,.72)
    points=[V(215,-379.4,6),V(215,-431,6),V(290,-431,6),V(290,-379.4,6)]
    m.feature('LANCable','Original bundled LAN cable shortened display path',_rounded_route(points,8,1.65),'Accessories',0,'black')
    for end,x in enumerate([215,290]):
        key='LANPlug'+str(end)
        body=m.rr(11.7,22,8,(x,-358,2),.6)
        channels=[]
        for i in range(8):
            xx=x+(i-3.5)*1.016
            channels.append(m.rr(.68,5.3,.7,(xx,-349,9.3),.04))
            m.box(key+'Contact'+str(i),'Independent 8P8C plug contact',.5,4.2,.30,(xx,-349,9.45),'Accessories',0,'gold',.04,True)
        body=body.cut(Part.makeCompound(channels))
        # Integral cantilever latch, separated above the housing along its free span.
        outline=[(-367,9.8),(-365.8,9.8),(-352.5,11),(-352.5,11.7),(-366,10.6)]
        vertices=[V(x-2.4,y,z) for y,z in outline]
        latch=Part.Face(Part.Wire(Part.makePolygon(vertices+[vertices[0]]).Edges)).extrude(V(4.8,0,0))
        m.feature(key+'Housing','Eight-position modular plug with integral latch',body.fuse(latch).removeSplitter(),'Accessories',0,'clearplug')
        m.box(key+'Boot','Moulded modular-plug cable boot',12.4,10,9,(x,-374.2,1.5),'Accessories',0,'black',1)
        relief=Part.makeCylinder(2.05,6,V(x,-379.3,6),V(0,-1,0)).cut(Part.makeCylinder(1.7,6.4,V(x,-379.1,6),V(0,-1,0)))
        m.feature(key+'Relief','Independent LAN cable strain relief',relief,'Accessories',0,'black')
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=30
    m.checkpoint(30,'bundled_lan_cable_eight_contacts_and_integral_latches','补齐原版随附 LAN 线的双端 8P8C 插头、十六个分离金属触点、卡扣、包胶与护线套，完成原配 AC / AV / USB / LAN 展示套装。线长及内部端子为结构学习近似。')
    m.snapshot('30_original_connection_kit',assemblies=['Accessories'],normal=(.2,-.5,2))


STAGES[30]=stage30


def finalize(model):
    from .deliver import finalize as shared_finalize
    settings=App.ParamGet('User parameter:BaseApp/Preferences/Mod/Part/General')
    previous=settings.GetInt('WriteSurfaceCurveMode',1)
    Part.setStaticValue('write.surfacecurve.mode',1)
    try:
        result=shared_finalize(model)
        model.snapshot('final_front',normal=(.2,-1.5,.7),assemblies=model.profile['envelope_groups'])
        model.snapshot('final_controller',assemblies=['Controller'],normal=(.2,-.5,2.4))
        model.snapshot('final_hero',normal=(.3,-.7,2.3),assemblies=result[0]['handheld_groups'])
        model.doc.save()
        return result
    finally:
        Part.setStaticValue('write.surfacecurve.mode',previous)
