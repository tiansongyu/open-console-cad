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
