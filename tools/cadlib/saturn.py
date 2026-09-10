"""Original Japanese grey HST-3200 Saturn study; local dimensions approximate."""
import math
import FreeCAD as App
import Part
from .core import V
from . import geometry as g
from .retro_common import native_loft,loft_shell,fuse_feature

FRONT=g.rotation((0,-1,0),(0,0,1))
REAR=g.rotation((0,1,0),(0,0,1))


def stage01(m):
    m.colors.update(cream=(.82,.81,.72),saturngrey=(.43,.48,.48),saturnblue=(.12,.30,.60),darkpanel=(.035,.05,.06),padgrey=(.55,.58,.57))
    m.params.set('A3','Depth (Y)');m.params.set('A4','Study height (Z)')
    m.native('LowerHousing','HST-3200 lower enclosure',260,230,8,23,(0,0,2),'Body',-6,'saturngrey')
    m.cut('LowerHousing',m.rr(256.4,226.4,23,(0,0,4),6.3),'Lower shell cavity with 2 mm floor')
    outer=[(260,230,8,0,0,25.25),(258,228,8,0,0,52),(246,218,8,0,0,66)]
    inner=[(256.4,226.4,6.3,0,0,25.05),(254.4,224.4,6.3,0,0,51.5),(242.4,214.4,6.3,0,0,64.1)]
    loft_shell(m,'UpperHousing','Tapered grey upper shell',outer,inner,'Body',5,'saturngrey')
    crown=native_loft(m,'CentralDeckCrown',[(202,216,12,0,0,65.8),(196,210,12,0,0,73),(186,192,14,0,0,83)])
    old=m.parts['UpperHousing'];obj=m.doc.addObject('Part::Fuse','UpperHousingCrown');obj.Base=old;obj.Tool=crown;obj.Refine=False;m.doc.recompute();obj.Shape.check(True)
    old.PhysicalPart=False;m.register(obj,'UpperHousing','Body',5,'saturngrey');obj.Label='Raised central deck and sloped side shoulders';old.Visibility=False;crown.Visibility=False
    m.cut('UpperHousing',m.rr(181,186,20,(0,0,61),11),'Raised deck inner cavity')
    for i,(x,y) in enumerate([(x,y) for x in [-104,104] for y in [-94,94]]):m.box('Foot'+str(i),'Lower rubber support',17,12,2,(x,y,0),'Body',-6,'rubber',2.8)
    m.profile['stages']=1
    m.checkpoint(1,'native_tapered_shell_and_raised_central_deck','按 HST-3200 灰色初代照片建立独立上下空心壳、倾斜侧肩与原生多截面抬高中央台；260 × 230 × 83 mm 仅作为近似学习包络，家族规格依据另行注明。')


def _lid_outline(w,h):
    sx=w/164;sy=h/153
    def pt(x,y):return V(x*sx,y*sy)
    return [Part.LineSegment(pt(-70,70),pt(70,70)),Part.Arc(pt(70,70),pt(79,67),pt(82,58)),Part.LineSegment(pt(82,58),pt(82,-35)),Part.Arc(pt(82,-35),pt(0,-83),pt(-82,-35)),Part.LineSegment(pt(-82,-35),pt(-82,58)),Part.Arc(pt(-82,58),pt(-79,67),pt(-70,70))]


def _lid_volume(w,h,z,t):
    sh=Part.Face(Part.Wire([e.toShape() for e in _lid_outline(w,h)])).extrude(V(0,0,t));sh.translate(V(0,-9,z));return sh


def stage02(m):
    m.cut('UpperHousing',_lid_volume(165.2,154.2,74,12),'Top-loading disc-lid opening')
    outer=[(164,153,0,0,-9,79.1),(162.5,151.5,0,0,-9,82.9)]
    inner=[(159.2,148.2,0,0,-9,78.9),(157.7,146.7,0,0,-9,81.2)]
    loft_shell(m,'DiscLid','Native curved-front Saturn disc lid',outer,inner,'Body',6,'saturngrey',outline=_lid_outline)
    well=_lid_volume(159,148,60.5,17.8).cut(_lid_volume(155.8,144.8,62.1,18.1))
    hole=Part.makeCylinder(18,4,V(0,-9,59.8)).fuse(Part.makeBox(23,65,4,V(-11.5,-9,59.8)))
    m.feature('DiscWell','Deep optical-disc well and pickup passage',well.cut(hole),'Optical',4,'black',True)
    # Rear expansion cartridge bay is separate from the CD lid.
    m.cut('UpperHousing',m.rr(125,20,14,(0,81,72),2),'Rear cartridge-bay opening')
    rim=m.rr(124,19,3.4,(0,81,79.4),1.8).cut(m.rr(119.5,14.5,4,(0,81,79.1),1.0))
    m.feature('CartridgeDeck','Rear cartridge-bay black liner',rim,'Ports',4,'black')
    for i,x in enumerate([-29.8,29.8]):m.box('CartridgeFlap'+str(i),'Spring-loaded cartridge dust flap',59,13.8,1.3,(x,81,81.2),'Body',5,'saturngrey',.6)
    m.label('LidSega','SEGA',7,(-13,30,82.94),'Body',6,'wiigrey' if 'wiigrey' in m.colors else 'metal')
    m.label('SaturnTitle','SEGA SATURN',6.3,(-31,-24,82.94),'Body',6,'white')
    # Dark reflective lid accent is geometric; no third-party bitmap is embedded.
    strip=Part.Face(Part.Wire([Part.Arc(V(-2,1),V(31,9),V(66,2)).toShape(),Part.makeLine(V(66,2),V(-2,1))])).extrude(V(0,0,.035));strip.translate(V(0,0,82.95))
    m.feature('LidAccent','Dark curved disc-lid accent',strip,'Body',6,'darkpanel')
    for i in range(3):
        groove=m.rr(1.2,8,.12,(-10+i*9,-66,82.95),.5);groove.rotate(V(-10+i*9,-66,82.95),V(0,0,1),-25)
        m.feature('LidGripMark'+str(i),'Three short lid grip marks',groove,'Body',6,'saturngrey')
    m.profile['stages']=2
    m.checkpoint(2,'curved_disc_lid_well_and_rear_cartridge_bay','加入带弧形前缘的原生光驱盖、深光盘仓与光头通道、后部卡槽衬框及防尘门，补齐灰色初代的顶盖文字和深色弧形装饰。')


def _top_skin(shape,depth):
    lower=shape.copy();lower.translate(V(0,0,-depth));return shape.cut(lower)


def _height(shape,x,y):
    section=shape.section(Part.makeLine(V(x,y,45),V(x,y,100)))
    assert section.Vertexes,(x,y)
    return max(v.Point.z for v in section.Vertexes)


def stage03(m):
    from .psv import _ellipse
    blank=m.doc.getObject('UpperHousingOuter').Shape.fuse(m.doc.getObject('CentralDeckCrown').Shape)
    pts=[V(-98,-63),V(-98,-105),V(-90,-113),V(90,-113),V(98,-105),V(98,-63)]
    edges=[Part.makeLine(pts[0],pts[1]),Part.Arc(pts[1],V(-96,-111),pts[2]).toShape(),Part.makeLine(pts[2],pts[3]),Part.Arc(pts[3],V(96,-111),pts[4]).toShape(),Part.makeLine(pts[4],pts[5]),Part.Arc(pts[5],V(0,-95),pts[0]).toShape()]
    mask=Part.Face(Part.Wire(edges)).extrude(V(0,0,23));mask.translate(V(0,0,62))
    plate=_top_skin(blank,.65).common(mask)
    m.cut('UpperHousing',plate,'Curved dark front-control inset')
    m.feature('ControlPanel','Dark curved front control panel',plate,'Body',5,'darkpanel')
    for key,x,y,w,h,angle in [('Power',-78,-91,27,13,28),('Reset',78,-91,27,13,28),('Open',0,-104,43,12,0)]:
        if key=='Open':
            opening=m.rr(w+.8,h+.8,35,(x,y,55),2);area=m.rr(w,h,35,(x,y,55),1.7)
        else:
            opening=_ellipse(w+.8,h+.8,55,35,x,y);area=_ellipse(w,h,55,35,x,y)
            opening.rotate(V(x,y,0),V(0,0,1),angle);area.rotate(V(x,y,0),V(0,0,1),angle)
        for shell in ['UpperHousing','ControlPanel']:m.cut(shell,opening,key+' control opening')
        cap=_top_skin(blank,2.4).common(area);cap.translate(V(0,0,.3));m.feature(key+'Button','Original blue '+key+' key',cap,'Controls',5,'saturnblue')
        z=_height(blank,x,y)+.35
        m.label(key+'Mark',key.upper(),2.8,(x-w*.27,y-1,z),'Controls',5,'saturngrey')
    for key,x,y,color,title in [('Power',-47,-104,'led','POWER'),('Access',47,-104,'red','ACCESS')]:
        z=_height(blank,x,y)
        hole=Part.makeCylinder(1.35,12,V(x,y,z-8))
        for shell in ['UpperHousing','ControlPanel']:m.cut(shell,hole,key+' indicator opening')
        m.cyl(key+'Lens','Front '+key+' indicator lens',1.1,1,(x,y,z-.5),'Controls',5,color)
        m.label(key+'Caption',title,2.5,(x-7,y+3,z+.04),'Body',5,'white')
    m.profile['stages']=3
    m.checkpoint(3,'curved_black_control_panel_and_blue_oval_keys','沿原生顶壳曲面分出深色控制面板，加入蓝色椭圆 POWER / RESET、中央 OPEN 键及双指示灯；按钮保留独立实体和外壳开孔。')


def _conformal_mark(m,key,base):
    obj=m.parts[key];low=obj.Shape.BoundBox.ZMin
    faces=[f for f in obj.Shape.Faces if f.BoundBox.ZLength<1e-6 and abs(f.CenterOfMass.z-low)<1e-5]
    assert faces,key
    mask=Part.makeCompound([f.extrude(V(0,0,50)) for f in faces]);mask.translate(V(0,0,-30))
    text=_top_skin(m.parts[base].Shape,.035).common(mask);text.translate(V(0,0,.05));assert text.Solids,key
    obj.Shape=text;obj.FlatPlacement=obj.Placement


def stage04(m):
    for key,base in [('PowerMark','PowerButton'),('ResetMark','ResetButton'),('OpenMark','OpenButton'),('PowerCaption','ControlPanel'),('AccessCaption','ControlPanel')]:_conformal_mark(m,key,base)
    for i,x in enumerate([-39,39],1):
        for shell in ['LowerHousing','UpperHousing']:m.cut(shell,m.rr(32,13,10,(x,-108,22),1.5,FRONT),'Controller '+str(i)+' front opening')
        case=m.rr(31,12,14,(x,-100.8,22),1.2,FRONT).cut(m.rr(28.4,9.4,11,(x,-104.2,22),.8,FRONT))
        m.feature('ControllerPort'+str(i),'Original Saturn nine-position controller socket',case,'Ports',0,'black',True)
        m.box('ControllerTongue'+str(i),'Controller contact carrier',26.5,8,.9,(x,-109,20.4),'Ports',0,'black',.3,True)
        for j in range(9):m.box(f'ControllerContact{i}_{j}','Controller spring contact',.9,7,.12,(x+(j-4)*2.7,-109,21.45),'Ports',0,'gold',.08,True)
        m.label('ControllerIndex'+str(i),str(i),4,(x-1,-115.03,32),'Body',4,'metal',rotation=FRONT)
    m.profile['stages']=4
    m.checkpoint(4,'dual_controller_ports_and_conformal_control_labels','补齐原版双手柄端口、绝缘载体与九位触点；将面板和按键文字投到实际曲面上，避免平面字片埋入斜面。接点尺寸为学习示意。')


def stage05(m):
    # Original AC inlet is in the upper shell, above the AV DIN connector.
    x=-91;z=47
    m.cut('UpperHousing',m.rr(32,23,12,(x,106,z),2,REAR),'Upper-housing mains inlet aperture')
    face=m.rr(31.2,22.2,3,(x,111.5,z),1.7,REAR)
    holes=Part.makeCylinder(3.7,4,V(x-3.7,111,z),V(0,1,0)).fuse(Part.makeCylinder(3.7,4,V(x+3.7,111,z),V(0,1,0)))
    face=face.cut(holes)
    m.feature('ACInlet','Original figure-eight mains inlet',face,'Power',3,'black',True)
    for i,xx in enumerate([x-3.7,x+3.7]):m.cyl('ACInletPin'+str(i),'Mains inlet pin study',.9,6,(xx,107.7,z),'Power',3,'metal',axis=(0,1,0),internal=True)
    # Two visible fixing heads plus lower bracket access reproduce the original family layout.
    for i,(xx,zz) in enumerate([(x-12,z),(x+12,z),(x,z-17)]):
        if i==2:m.cut('UpperHousing',Part.makeCylinder(2,5,V(xx,110,zz),V(0,1,0)),'Lower inlet bracket fixing recess')
        sh=Part.makeCylinder(1.6,.6,V(xx,114.65,zz),V(0,1,0)).cut(Part.makeBox(2.1,1,.4,V(xx-1.05,114.5,zz-.2)))
        m.feature('ACFixing'+str(i),'Rear mains-inlet fixing head',sh,'Power',3,'metal',True)
    x=-91;z=17
    m.cut('LowerHousing',Part.makeCylinder(7,13,V(x,103,z),V(0,1,0)),'Ten-position AV mini-DIN aperture')
    m.ring('AVShell','AV mini-DIN metal sleeve',6.6,5.8,11,(x,103.3,z),'Ports',0,'metal',axis=(0,1,0),internal=True)
    carrier=Part.makeCylinder(5.5,3,V(x,108,z),V(0,1,0));points=[(-3.2,2),(0,2),(3.2,2),(-4,0),(-1.4,0),(1.4,0),(4,0),(-3,-2.3),(0,-2.3),(3,-2.3)]
    carrier=carrier.cut(Part.makeCompound([Part.makeCylinder(.7,3.4,V(x+dx,107.8,z+dz),V(0,1,0)) for dx,dz in points]));m.feature('AVCarrier','AV contact insulator',carrier,'Ports',0,'black',True)
    for i,(dx,dz) in enumerate(points):m.ring('AVContact'+str(i),'AV mini-DIN socket contact',.61,.37,4.5,(x+dx,108.2,z+dz),'Ports',0,'gold',axis=(0,1,0),internal=True)
    x=-51;z=17
    m.cut('LowerHousing',m.rr(25,10,12,(x,104,z),1,REAR),'Rear communication connector aperture')
    sh=m.rr(24.2,9.2,10,(x,104.5,z),.8,REAR).cut(m.rr(22.8,7.8,10.4,(x,104.3,z),.5,REAR));m.feature('CommunicationShell','Rear communication connector shield',sh,'Ports',0,'metal',True)
    m.box('CommunicationTongue','Communication port insulator',21,7,.7,(x,110,16),'Ports',0,'black',.3,True)
    for i in range(9):m.box('CommunicationPin'+str(i),'Communication connector study contact',.75,6,.1,(x+(i-4)*2.2,110,16.85),'Ports',0,'gold',.05,True)
    for shell in ['LowerHousing','UpperHousing']:m.cut(shell,m.rr(93,33,10,(62,107,23),2,REAR),'Rear battery and expansion service opening')
    m.box('ServiceDoor','Removable rear battery / expansion cover',92.2,32.2,1.4,(62,113.5,23),'Body',-4,'saturngrey',1.6,orient=REAR)
    vents=[Part.makeBox(8,2.8,16,V(x,y,14)) for x in [-134,126] for y in range(-78,83,8)]
    for shell in ['LowerHousing','UpperHousing']:m.cut(shell,Part.makeCompound(vents),'Side cooling slots')
    floor=[m.rr(16,2.6,4,(x,y,1),1) for x in [-68,68] for y in range(-72,73,8)]
    m.cut('LowerHousing',Part.makeCompound(floor),'Underside ventilation slots')
    m.profile['stages']=5
    m.checkpoint(5,'rear_mains_av_communication_and_service_cover','补齐上壳八字电源座、下壳 AV 与通信接口、独立后部电池扩展盖，以及侧面和底部通风槽；接口触点与局部尺寸保留学习近似说明。')


def stage06(m):
    from .megadrive import _qfp
    from .n64 import _sop
    m.box('MainPCB','MAIN VA0.5-inspired Saturn mainboard',238,209,1.6,(0,-.5,8),'Mainboard',0,'pcb',2,True)
    points=[(x,y) for x in [-109,109] for y in [-94,94]]+[(-62,-78),(62,-78),(-62,55),(62,52),(0,0)]
    m.cut('MainPCB',[Part.makeCylinder(1.45,2,V(x,y,7.8)) for x,y in points],'Mainboard and optical-support mounting bores')
    for key,title,x,y,size,pins in [('SH2A','SH-2 A',65,66,20,100),('SH2B','SH-2 B',65,32,20,100),('VDP1','VDP1',-40,40,28,160),('VDP2','VDP2',0,40,28,160),('SCU','SCU',-30,-15,25,144),('SCSP','SCSP',-77,-58,24,128),('Sound68000','68EC000',-78,-21,18,64),('SMPC','SMPC',85,-62,18,100)]:_qfp(m,key,title,x,y,size,pins,z=10.0)
    for key,title,x,y,w,h,pins in [('BIOS','IPL ROM',27,-62,40,13,40),('WorkRAM0','WORK RAM',48,6,23,10,28),('WorkRAM1','WORK RAM',78,6,23,10,28),('SoundRAM','SOUND RAM',-82,-94,24,7,28),('BackupRAM','BACKUP RAM',65,86,22,9,28),('VideoEncoder','VIDEO',-74,75,20,13,24),('AudioDAC','AUDIO DAC',-91,44,12,7,20)]:_sop(m,key,title,x,y,w,h,pins,z=10,height=1.8)
    for i,(x,y) in enumerate([(-47,-47),(-13,-47),(-47,-67),(-13,-67)]):_sop(m,'VideoRAM'+str(i),'VRAM',x,y,26,10,28,z=10,height=1.8)
    for i,(x,y) in enumerate([(-94,95),(-82,95),(-70,95),(-104,-88),(-104,-73),(99,10),(100,25)]):
        m.cyl('Electrolytic'+str(i),'Mainboard filter capacitor',3.1,8,(x,y,10),'Mainboard',0,'metal',internal=True)
        m.cyl('ElectrolyticTop'+str(i),'Capacitor vent cap',2.6,.05,(x,y,18.04),'Mainboard',0,'black',internal=True)
    for bank,(bx,by,nx,ny,dx,dy) in enumerate([(-105,-3,4,7,3.5,4),(-107,63,4,6,3.6,4),(14,-36,8,5,4,4),(-16,81,8,4,4,4),(39,-94,8,3,4,4),(82,-31,6,4,4,4)]):
        for ix in range(nx):
            for iy in range(ny):m.box(f'Passive{bank}_{ix}_{iy}','Photographic-layout passive study',1.5,.8,.6,(bx+ix*dx,by+iy*dy,9.85),'Mainboard',0,'cream' if (ix+iy)%3 else 'black',.08,True)
    m.box('ClockCan','Metal clock oscillator',12,6,3,(-40,88,10),'Mainboard',0,'metal',1,True)
    for key,x,y,w,h in [('OpticalDataSocket',-20,-90,26,5),('PowerSocket',-99,10,9,6),('CDSubsystemSocket',99,62,9,5),('DoorSensorSocket',17,-89,8,5),('LampSocket',-13,-78,7,4)]:m.box(key,'Board harness connector study',w,h,3,(x,y,10),'Mainboard',0,'white',.4,True)
    m.label('MainboardCaption','HST-3200 / MAIN VA0.5 STUDY',3,(-49,16,9.65),'Mainboard',0,'white')
    m.profile['stages']=6
    m.checkpoint(6,'va05_mainboard_dual_sh2_graphics_sound_and_memory','依据 MAIN VA0.5 拆解布局建立主板、双 SH-2、两组图形处理器、SCU、音频处理、系统管理与分区存储，并加入电容、时钟、无源件与线束插座；引脚和电路布局为学习近似。')


def _optical_package(m,kind,*args,**kw):
    from .megadrive import _qfp
    from .n64 import _sop
    before=set(m.parts);(_qfp if kind=='qfp' else _sop)(m,*args,**kw)
    for key in set(m.parts)-before:
        obj=m.parts[key];m.group('Mainboard').removeObject(obj);m.group('Optical').addObject(obj);obj.Assembly='Optical'


def stage07(m):
    m.box('CDSubsystemPCB','Separate original CD-subsystem board',94,98,.9,(70,38,20),'Optical',0,'pcb',1.3,True)
    mounts=[(30,-4),(110,-4),(30,80),(110,80)]
    m.cut('CDSubsystemPCB',[Part.makeCylinder(1.2,1.3,V(x,y,19.8)) for x,y in mounts]+[Part.makeCylinder(3.2,1.3,V(62,52,19.8))],'CD board mounting and optical-support passages')
    for i,(x,y) in enumerate(mounts):
        m.cut('MainPCB',Part.makeCylinder(1,2,V(x,y,7.8)),'CD-subsystem support screw bore')
        sh=Part.makeCylinder(2.2,7,V(x,y,12.8)).cut(Part.makeCylinder(.8,7.4,V(x,y,12.6)))
        m.feature('CDStandoff'+str(i),'CD-subsystem board support',sh,'Optical',0,'white',True)
        m.screw('CDScrew'+str(i),(x,y,21.4),'Optical',0,length=7,radius=1.8,axis=(0,0,-1))
    _optical_package(m,'qfp','CDSH1','SH-1',44,40,23,100,z=21.3)
    _optical_package(m,'qfp','CDController','CD CONTROL',83,34,25,128,z=21.3)
    _optical_package(m,'sop','CDBufferRAM','CD BUFFER',77,73,28,11,28,z=21.3,height=1.7)
    m.box('CDClockCan','CD-subsystem clock oscillator',10,5,2,(43,72,21.3),'Optical',0,'metal',.8,True)
    m.box('CDDriveRibbonSocket','Optical transport data connector',28,5,2.2,(70,-4,21.3),'Optical',0,'white',.4,True)
    m.box('CDPowerSocket','CD-subsystem supply connector',8,5,3,(106,59,21.3),'Optical',0,'white',.3,True)
    for i in range(14):m.box('CDPassive'+str(i),'CD-subsystem support passive',1.4,.8,.5,(33+(i%7)*3.7,7+(i//7)*4,21.1),'Optical',0,'cream',.08,True)
    # Coin-cell access is retained behind the independent rear service cover.
    x,y=92,95
    m.cyl('BatteryHolderBase','CR2032 rear holder base',11.8,1,(x,y,10),'Internal',0,'black',internal=True)
    m.ring('BatteryHolderRim','Coin-cell locating rim',11.8,10.35,4.4,(x,y,11.15),'Internal',0,'black',internal=True)
    m.cyl('ClockBattery','Replaceable CR2032 cell',10,3.2,(x,y,11.4),'Internal',0,'metal',internal=True)
    m.label('ClockBatteryMark','CR2032',2,(x-5,y-1,14.64),'Internal',0,'black')
    m.box('BatterySpringContact','Coin-cell retaining spring strip',3,21,.18,(x+5,y,15.7),'Internal',0,'metal',.15,True)
    m.box('ClockResetSwitch','Rear backup-memory reset switch',5,5,3.6,(42,94,10),'Mainboard',0,'black',.4,True)
    m.cyl('ClockResetPlunger','Backup reset plunger',1.4,.8,(42,94,13.7),'Mainboard',0,'saturnblue',internal=True)
    reader=m.rr(123,13,14,(0,81,65),1.1).cut(m.rr(113,2.4,12.7,(0,81,66.5),.5))
    m.feature('CartridgeReader','Two-sided cartridge-edge connector study',reader,'Ports',3,'black',True)
    for side in [-1,1]:
        fingers=[Part.makeBox(.55,.16,10.4,V((i-32.5)*1.65-.275,81+side*.95-.08,68)) for i in range(66)]
        m.feature('CartridgeContactBank'+str(side),'Cartridge contact bank study',Part.makeCompound(fingers),'Ports',3,'gold',True)
    m.profile['stages']=7
    m.checkpoint(7,'separate_cd_subsystem_rear_coin_cell_and_cartridge_reader','加入原版独立 CD 子系统板、SH-1 与 CD 控制封装、缓存和支承，补齐后部可换 CR2032 电池、备份复位键及双面卡槽触点；局部引脚与连接尺寸为学习近似。')


def _spaced_label(m,key,text,size,pos):
    # Independent glyph advances avoid coincident R/A kerning edges in the CAD font.
    font=m.root/'references/DejaVuSans.ttf';glyphs=[];cursor=0
    for char in text:
        if char==' ':cursor+=size*.5;continue
        faces=[]
        for wires in Part.makeWireString(char,str(font.parent)+'/',font.name,size):
            if wires:faces.extend(Part.makeFace(wires,'Part::FaceMakerBullseye').Faces)
        sh=Part.makeCompound([f.extrude(V(0,0,.018)) for f in faces]);b=sh.BoundBox;sh.translate(V(cursor-b.XMin,0,0));glyphs.append(sh);cursor+=b.XLength+size*.15
    sh=Part.makeCompound(glyphs);sh.translate(V(*pos));sh.check(True)
    obj=m.parts[key];obj.Shape=sh;obj.FlatPlacement=obj.Placement


def stage08(m):
    obj=m.parts['PowerSocket'];obj.Placement.Base+=V(-11,25,0);obj.FlatPlacement=obj.Placement
    # Place the right rear optical support between the two SH-2 lead banks.
    for obj in m.doc.Objects:
        if obj.TypeId=='Part::Feature' and obj.Label.startswith(('Mainboard and optical-support mounting bores · tool','CD board mounting and optical-support passages · tool')):
            solids=[]
            for solid in obj.Shape.Solids:
                sh=solid.copy();c=sh.BoundBox.Center
                if abs(c.x-62)<.01 and abs(c.y-52)<.01:sh.translate(V(0,-3,0))
                solids.append(sh)
            obj.Shape=Part.makeCompound(solids)
    rows=[('WorkRAM0Mark','WORK RAM',23,48,6),('WorkRAM1Mark','WORK RAM',23,78,6),('SoundRAMMark','SOUND RAM',24,-82,-94),('BackupRAMMark','BACKUP RAM',22,65,86)]
    rows += [('VideoRAM'+str(i)+'Mark','VRAM',26,x,y) for i,(x,y) in enumerate([(-47,-47),(-13,-47),(-47,-67),(-13,-67)])]
    for key,text,w,x,y in rows:_spaced_label(m,key,text,min(1.7,w/(len(text)*.8)),(x-w/2+1,y-.7,11.83))
    m.doc.recompute()
    for obj in m.parts.values():obj.Shape.check(True)
    m.profile['stages']=8
    m.checkpoint(8,'mainboard_socket_clearance_and_strict_glyph_geometry','移开主板电源插座以避让无源器件，并调整光驱支承孔；采用独立字形间距修复微小 CAD 文字的自交，对全部已建组件执行严格实体检查。')


def stage09(m):
    from .atari2600 import _helical_spring
    points=[(-62,-78),(62,-78),(-62,55),(62,49)]
    for i,(x,y) in enumerate(points):
        post=Part.makeCone(3.6,2.2,31.8,V(x,y,10.3)).cut(Part.makeCylinder(.85,32.2,V(x,y,10.1)))
        m.feature('OpticalPost'+str(i),'Tall white optical-unit support',post,'Internal',1,'white',True)
        m.ring('OpticalBush'+str(i),'Optical-unit isolation ring',4.4,2.4,.8,(x,y,41.3),'Optical',1,'rubber',internal=True)
        m.screw('OpticalPostScrew'+str(i),(x,y,7.2),'Internal',0,length=4.5,radius=1.8)
        m.screw('OpticalMountScrew'+str(i),(x,y,44.65),'Optical',1,length=5.5,radius=1.8,axis=(0,0,-1))
    boardpoints=[(x,y) for x in [-45,45] for y in [-68,49]]
    base=m.rr(132,144,.8,(0,-10,42.3),2).cut(Part.makeCompound([Part.makeCylinder(1.3,1.3,V(x,y,42.1)) for x,y in points+boardpoints]))
    m.feature('OpticalBase','Optical transport mounting base',base,'Optical',1,'metal',True)
    m.box('OpticalPCB','Original optical-unit control board study',106,129,.9,(0,-9,43.3),'Optical',1,'pcb',1.4,True)
    m.cut('OpticalPCB',[Part.makeCylinder(1.1,1.3,V(x,y,43.1)) for x,y in boardpoints],'Transport PCB fixing holes')
    for i,(x,y) in enumerate(boardpoints):m.screw('OpticalPCBScrew'+str(i),(x,y,44.65),'Optical',1,length=3,radius=1.7,axis=(0,0,-1))
    frame=m.rr(80,100,8,(0,8,47),2).cut(m.rr(76,96,8.4,(0,8,46.8),1))
    m.feature('OpticalFrame','Black pickup transport frame',frame,'Optical',2,'black',True)
    top=m.rr(80,100,1,(0,8,55.2),2).cut(m.rr(42,81,1.4,(0,17,55),1.2)).cut(Part.makeCylinder(18,1.4,V(0,-17,55)))
    m.feature('OpticalBridge','Open optical pickup bridge',top,'Optical',3,'black',True)
    for i,x in enumerate([-17,17]):
        m.cyl('PickupRail'+str(i),'Optical pickup guide rod',1.4,73,(x,-10,52),'Optical',2,'metal',axis=(0,1,0),internal=True)
        m.cut('OpticalFrame',Part.makeCylinder(1.6,108,V(x,-44,52),V(0,1,0)),'Guide-rod frame passage')
    carriage=m.rr(39,22,5,(0,20,49.8),1.5).cut(Part.makeCompound([Part.makeCylinder(1.55,23,V(x,8.5,52),V(0,1,0)) for x in [-17,17]]))
    m.feature('PickupCarriage','Guided optical pickup carriage',carriage,'Optical',2,'metal',True)
    m.box('PickupBlock','Optical pickup lens body',24,20,3,(0,20,54.95),'Optical',3,'black',1.2,True)
    m.ring('PickupLensRing','Optical lens retaining ring',4,2.9,.6,(0,20,58.05),'Optical',3,'metal',internal=True)
    m.cyl('PickupLens','Blue optical lens study',2.7,.6,(0,20,58.05),'Optical',3,'blue',internal=True)
    m.cyl('SpindleMotor','Disc spindle motor',10,5.5,(0,-17,45),'Optical',2,'metal',internal=True)
    m.cyl('SpindleShaft','Disc spindle shaft',2.2,7.6,(0,-17,50.7),'Optical',2,'metal',internal=True)
    m.cyl('Turntable','Disc turntable',16,1.45,(0,-17,58.55),'Optical',3,'black',internal=True)
    m.feature('SpindleCone','Disc-centering cone',Part.makeCone(6,4.3,3,V(0,-17,60.1)),'Optical',3,'black',True)
    thread=_helical_spring(.86,2,69,.16);thread.rotate(V(),V(1,0,0),-90);thread.translate(V(23,-10,51.5))
    shaft=Part.makeCylinder(.75,71,V(23,-11,51.5),V(0,1,0));m.feature('SledLeadScrew','Optical sled screw and helical thread',shaft.fuse(thread).removeSplitter(),'Optical',2,'metal',True)
    m.cut('OpticalFrame',Part.makeCylinder(1.15,108,V(23,-44,51.5),V(0,1,0)),'Sled lead-screw frame passage')
    m.box('SledNut','Optical carriage drive nut',5,6,4,(23,20,49.5),'Optical',2,'white',.5,True)
    m.cut('SledNut',Part.makeCylinder(1.12,6.4,V(23,16.8,51.5),V(0,1,0)),'Lead-screw clearance through drive nut')
    m.cyl('SledMotor','Optical sled motor',7,12,(23,-34,51.5),'Optical',2,'metal',axis=(0,1,0),internal=True)
    m.cyl('SledMotorShaft','Optical sled motor shaft',1,9,(23,-21.8,51.5),'Optical',2,'metal',axis=(0,1,0),internal=True)
    outline=[]
    for i in range(16):
        for phase,r in [(0,3.5),(.25,3.5),(.3,4.2),(.7,4.2),(.75,3.5)]:
            a=(i+phase)*2*math.pi/16;outline.append(V(23+r*math.cos(a),-12.5,51.5+r*math.sin(a)))
    gear=Part.Face(Part.makePolygon(outline+[outline[0]])).extrude(V(0,1,0)).cut(Part.makeCylinder(1.1,1.4,V(23,-12.7,51.5),V(0,1,0)))
    m.feature('SledGear','Sled drive gear study',gear,'Optical',2,'white',True)
    _optical_package(m,'qfp','OpticalDriver','DRIVE CTRL',-33,-58,16,64,z=44.4)
    m.box('OpticalUnitDataSocket','Optical-unit flat-cable socket',20,4,2,(0,-69,44.4),'Optical',1,'white',.4,True)
    m.box('OpticalPowerSocket','Optical-unit supply connector',8,5,2.7,(40,-65,44.4),'Optical',1,'white',.4,True)
    for i,(x,y) in enumerate([(35,-54),(45,-45)]):m.cyl('OpticalCap'+str(i),'Transport-board capacitor',3,7,(x,y,44.4),'Optical',1,'metal',internal=True)
    for i in range(12):m.box('OpticalPassive'+str(i),'Transport-board passive',1.4,.8,.5,(-6+(i%4)*3.8,-57+(i//4)*3.5,44.3),'Optical',1,'cream',.08,True)
    m.cut('OpticalBridge',m.rr(17,18,2,(23,-28,54.9),2),'Sled motor bridge relief')
    m.profile['stages']=9
    m.checkpoint(9,'white_optical_supports_spindle_and_guided_pickup','加入四支白色长支座、独立光驱控制板、主轴与定位台、双导轨光头、螺旋进给件和电机，保留机架、固定件与光盘仓的装配间隙。')


def stage10(m):
    obj=m.parts['OpticalPowerSocket'];obj.Placement.Base+=V(-3,0,0);obj.FlatPlacement=obj.Placement
    m.cut('OpticalBridge',m.rr(9.4,3.4,2,(23,-12,54.9),.7),'Sled drive-gear upper-bridge relief')
    m.doc.recompute()
    for obj in m.parts.values():obj.Shape.check(True)
    m.profile['stages']=10
    m.checkpoint(10,'optical_connector_and_drive_gear_fit','根据装配求交避让光驱板固定螺钉，并补充进给齿轮的顶架开口；复查全部已建组件的严格实体有效性。')

STAGES=[stage01,stage02,stage03,stage04,stage05,stage06,stage07,stage08,stage09,stage10]
