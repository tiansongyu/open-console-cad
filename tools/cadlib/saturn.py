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


def stage11(m):
    from .atari2600 import _rounded_route
    # HST-3200 carries its supply on the upper enclosure; dimensions are study estimates.
    cx,cy=-97.5,3.5
    m.box('PSUPCB','Upper-housing power-supply board',36,155,1.2,(cx,cy,40),'Power',3,'pcb',1,True)
    points=[(x,y) for x in [-110,-85] for y in [-66,66]]
    m.cut('PSUPCB',[Part.makeCylinder(1.1,1.6,V(x,y,39.8)) for x,y in points],'Upper-mounted PSU board fixing bores')
    m.box('PSUTransformer','Power transformer ferrite core',24,26,20,(cx,-5,42.5),'Power',3,'black',1.3,True)
    m.cut('PSUTransformer',m.rr(18.5,27,9,(cx,-5,47.5),.8),'Transformer winding seat')
    m.box('PSUWinding','Transformer insulated winding',18,26.6,8.5,(cx,-5,47.75),'Power',3,'cream',.8,True)
    m.cyl('PSUBulkCap','Primary smoothing capacitor',6,18,(-99,58,42.6),'Power',3,'black',internal=True)
    m.cyl('PSUOutputCap','Secondary smoothing capacitor',4.5,15,(-98,-43,42.6),'Power',3,'metal',internal=True)
    m.cyl('PSUOutputCoil','Secondary filter coil',5,10,(-99,-61,42.6),'Power',3,'copper',internal=True)
    m.cyl('PSUInputCoil','Input filter choke',5,9,(-99,32,42.6),'Power',3,'cream',internal=True)
    m.box('PSURectifier','Primary rectifier study',8,6,3.5,(-108,18,42.6),'Power',3,'black',.5,True)
    for i,(x,y,length,height) in enumerate([(-112,-2,34,19),(-82,-20,42,18)]):m.box('PSUHeatPlate'+str(i),'Power-device heat spreader',.8,length,height,(x,y,42.5),'Power',3,'metal',.1,True)
    m.cyl('PSUFuse','Cartridge fuse study',1.7,13,(-108,50,45),'Power',3,'metal',axis=(0,1,0),internal=True)
    for i,y in enumerate([49.5,62]):m.ring('PSUFuseClip'+str(i),'Fuse retaining clip',2.2,1.85,1.5,(-108,y,45),'Power',3,'metal',axis=(0,1,0),internal=True)
    m.box('PSUOutputSocket','Six-position supply harness socket study',14,5,3,(-97.5,-69,42.5),'Power',3,'white',.4,True)
    for i in range(6):m.box('PSUOutputPin'+str(i),'Supply harness contact study',.65,2.6,.1,(-97.5+(i-2.5)*1.9,-69,45.65),'Power',3,'gold',.07,True)
    posts=[];blank=m.doc.getObject('UpperHousingOuter').Shape.fuse(m.doc.getObject('CentralDeckCrown').Shape)
    for i,(x,y) in enumerate(points):
        post=Part.makeCylinder(2.2,28,V(x,y,41.45)).common(blank).cut(Part.makeCylinder(.8,28.4,V(x,y,41.25)));posts.append(post)
        m.screw('PSUFixing'+str(i),(x,y,39.45),'Power',3,length=7,radius=1.8)
    fuse_feature(m,'UpperHousing',Part.makeCompound(posts),'Upper-enclosure power board support columns',refine=False)
    bracket=m.rr(39,162,.45,(cx,cy,38.55),1.5).cut(m.rr(29,145,.8,(cx,cy,38.4),1))
    m.feature('PSUBracket','Power board retaining frame',bracket,'Power',3,'metal',True)
    m.box('PowerSwitch','Latching power-switch body',13,11,8,(-78,-91,67),'Controls',4,'black',1,True)
    m.box('PowerSwitchPlunger','Power-switch actuator',6,5,3,(-78,-91,75.2),'Controls',4,'white',.7,True)
    m.box('PowerSwitchInsulator','Power-switch insulating sleeve',16,14,.4,(-78,-91,66.4),'Controls',4,'cream',1.2,True)
    for i,x in enumerate([-94.7,-87.3]):
        endx=-104+i*8
        points=[V(x,107.45,47),V(x,102,47),V(endx,90,47),V(endx,77,44.4)]
        m.feature('MainsInletLead'+str(i),'Mains inlet lead study',_rounded_route(points,.6,.42),'Power',3,'black' if i==0 else 'white',True)
    m.profile['stages']=11
    m.checkpoint(11,'upper_housing_psu_transformer_and_power_switch','加入初代 HST-3200 的上壳电源板、变压器、滤波与散热器件、支承框和锁定电源开关，保留独立市电端头与线束；内部器件尺寸与电路为结构学习示意。')


def stage12(m):
    casepoints=[(x,y) for x in [-109,109] for y in [-94,94]]
    optical=[(-62,-78),(62,-78),(-62,55),(62,49)]
    lower=m.rr(236,205,.25,(0,-.5,5.6),2)
    lower=lower.cut(Part.makeCompound([Part.makeCylinder(3.8,.7,V(x,y,5.4)) for x,y in casepoints]+[Part.makeCylinder(2.8,.7,V(0,0,5.4))]))
    vents=[m.rr(15,2.7,.8,(x,y,5.3),1) for x in [-84,84] for y in range(-68,70,9)]
    m.feature('LowerShield','Lower mainboard screening plate',lower.cut(Part.makeCompound(vents)),'Shield',-3,'metal',True)
    upper=m.rr(230,199,.35,(0,-.5,31.8),2)
    holes=[Part.makeCylinder(3.2,.9,V(x,y,31.5)) for x,y in optical]+[Part.makeCylinder(3.7,.9,V(x,y,31.5)) for x,y in casepoints]
    upper=upper.cut(Part.makeCompound(holes)).cut(m.rr(28,28,.9,(92,95,31.5),2))
    vents=[m.rr(15,2.8,.9,(x,y,31.5),1) for x in [-83,83] for y in range(-68,70,9)]
    m.feature('MainShield','Upper mainboard shield with service passages',upper.cut(Part.makeCompound(vents)),'Shield',1,'metal',True)
    m.box('FrontPortBar','Controller-port retaining crossbar',160,9,.6,(0,-103.5,14.65),'Internal',0,'metal',.7,True)
    for i,x in enumerate([-73,73]):
        m.cut('FrontPortBar',Part.makeCylinder(1.1,1,V(x,-103.5,14.45)),'Controller-bar fixing bore')
        m.cut('MainPCB',Part.makeCylinder(1.1,2,V(x,-103.5,7.8)),'Controller-bar motherboard fixing bore')
        m.screw('FrontPortScrew'+str(i),(x,-103.5,16),'Internal',0,length=7,radius=1.8,axis=(0,0,-1))
    lowerposts=[];upperposts=[];blank=m.doc.getObject('UpperHousingOuter').Shape.fuse(m.doc.getObject('CentralDeckCrown').Shape)
    for i,(x,y) in enumerate(casepoints):
        post=Part.makeCylinder(3.4,27.15,V(x,y,3.85)).fuse(Part.makeCylinder(4.8,.5,V(x,y,7.2))).cut(Part.makeCylinder(.9,28,V(x,y,3.6)))
        lowerposts.append(post)
        top=Part.makeCylinder(3.1,40,V(x,y,32.2)).common(blank).cut(Part.makeCylinder(.85,40.4,V(x,y,32.0)));upperposts.append(top)
        m.cut('MainPCB',Part.makeCylinder(3.8,2,V(x,y,7.8)),'Enclosure fixing-column motherboard clearance')
        m.cut('LowerHousing',[Part.makeCylinder(1.2,35,V(x,y,1)),Part.makeCylinder(2.3,3,V(x,y,-.2))],'Enclosure screw access and head recess')
        m.cut('Foot'+str(i),Part.makeCylinder(2.3,3,V(x,y,-.2)),'Case screw access through rubber foot')
        m.screw('CaseScrew'+str(i),(x,y,.3),'Internal',-3,length=36,radius=2)
    center=Part.makeCylinder(2.5,3.85,V(0,0,3.85)).cut(Part.makeCylinder(.85,4.3,V(0,0,3.6)))
    lowerposts.append(center)
    fuse_feature(m,'LowerHousing',Part.makeCompound(lowerposts),'Lower enclosure columns and board support shoulders',refine=False)
    m.cut('LowerHousing',Part.makeCylinder(.85,4.5,V(0,0,3.6)),'Blind central mainboard screw bore')
    fuse_feature(m,'UpperHousing',Part.makeCompound(upperposts),'Upper enclosure fixing columns',refine=False)
    m.screw('MainboardCenterScrew',(0,0,10.1),'Internal',0,length=6,radius=1.8,axis=(0,0,-1))
    m.profile['stages']=12
    m.checkpoint(12,'layered_shields_case_columns_and_board_fixings','加入上下屏蔽板、通风与维修开口、手柄端口压条、上下壳螺柱和主板承托，保留螺钉、橡胶脚垫及板件的独立避让。')


def _yz_gear(x,y,z,root,outer,teeth,thickness,sector=False):
    points=[V(x,y,z)] if sector else []
    for i in range(teeth):
        for phase,r in [(0,root),(.22,root),(.3,outer),(.7,outer),(.78,root)]:
            a=(math.pi if sector else 0)+(i+phase)*(math.pi if sector else 2*math.pi)/teeth
            points.append(V(x,y+r*math.cos(a),z+r*math.sin(a)))
    if sector:points.append(V(x,y+root,z))
    return Part.Face(Part.makePolygon(points+[points[0]])).extrude(V(thickness,0,0))


def stage13(m):
    from .wii import _coil
    # The corner of the power switch needs its own pocket beyond the broad cavity.
    m.cut('UpperHousing',m.rr(17,15,10,(-78,-91,66.1),1.6),'Local power-switch and insulation pocket')
    ears=[];journals=[]
    for side in [-1,1]:
        x=side*66;y=62.5;z=78.2
        ear=Part.makeCylinder(3,8,V(x-4,y,z),V(1,0,0)).cut(Part.makeCylinder(1.1,8.4,V(x-4.2,y,z),V(1,0,0)));ears.append(ear)
        m.cut('UpperHousing',Part.makeCylinder(3.25,8.6,V(x-4.3,y,z),V(1,0,0)),'Disc-lid hinge-ear moving clearance')
        for dx in [-10,5]:
            sh=Part.makeCylinder(3.7,5,V(x+dx,y,z),V(1,0,0)).cut(Part.makeCylinder(1.1,5.4,V(x+dx-.2,y,z),V(1,0,0)));journals.append(sh)
        start=-85 if side<0 else 55
        m.cyl('LidHingePin'+str(side),'Disc-lid steel hinge pin',.95,30,(start,y,z),'Optical',4,'metal',axis=(1,0,0),internal=True)
    fuse_feature(m,'DiscLid',Part.makeCompound(ears),'Integrated rear CD-lid hinge ears',refine=False)
    fuse_feature(m,'UpperHousing',Part.makeCompound(journals),'Enclosure hinge-bearing journals',refine=False)
    spring=_coil('SaturnLidSpring',2.1,5.5,1.1,.24,(77.5,62.5,78.2),axis=(1,0,0))
    m.feature('LidReturnSpring','Right CD-lid return spring study',spring,'Optical',4,'metal',True)
    for side in [-1,1]:
        x=side*84.8
        m.ring('LidHingeWasher'+str(side),'Hinge retaining washer',1.8,1.05,.35,(x,62.5,78.2),'Optical',4,'metal',axis=(1,0,0),internal=True)
    sector=_yz_gear(-82.5,62.5,78.2,13.7,15,18,2,True).fuse(Part.makeCylinder(3,2,V(-82.5,62.5,78.2),V(1,0,0)))
    sector=sector.cut(Part.makeCylinder(1.1,2.4,V(-82.7,62.5,78.2),V(1,0,0)))
    m.feature('LidSectorGear','Left disc-lid sector gear study',sector,'Optical',4,'black',True)
    m.cut('UpperHousing',Part.makeCylinder(3.35,2.7,V(-82.85,62.5,78.2),V(1,0,0)),'Inner roof relief for sector-gear hub')
    gear=_yz_gear(-82.5,62.5,58.9,3.5,4.1,16,2).cut(Part.makeCylinder(1.0,2.4,V(-82.7,62.5,58.9),V(1,0,0)))
    m.feature('LidDampingPinion','Lid gear-train pinion study',gear,'Optical',4,'black',True)
    m.cyl('LidPinionShaft','Pinion journal pin',.85,4.6,(-83.2,62.5,58.9),'Optical',4,'metal',axis=(1,0,0),internal=True)
    plate=Part.makeBox(.6,16,26,V(-80,54.5,54))
    bores=[Part.makeCylinder(r,1,V(-80.2,y,z),V(1,0,0)) for y,z,r in [(62.5,58.9,1.1),(62.5,78.2,1.1),(56,78.8,.75),(69,78.8,.75)]]
    m.feature('LidGearBracket','Metal lid-gear retaining bracket',plate.cut(Part.makeCompound(bores)),'Optical',4,'metal',True)
    anchors=[]
    for i,y in enumerate([56,69]):
        sh=Part.makeCylinder(1.9,6,V(-77,y,77)).cut(Part.makeCylinder(.75,5,V(-80,y,78.8),V(1,0,0)));anchors.append(sh)
        screw=Part.makeCylinder(1.5,.35,V(-80.45,y,78.8),V(1,0,0)).fuse(Part.makeCylinder(.55,4.7,V(-80.12,y,78.8),V(1,0,0)))
        m.feature('LidBracketScrew'+str(i),'Lid bracket fixing',screw,'Optical',4,'metal',True)
    fuse_feature(m,'UpperHousing',Part.makeCompound(anchors),'Upper-cover lid bracket fixing bosses',refine=False)
    m.profile['stages']=13
    m.checkpoint(13,'native_lid_hinges_return_spring_and_sector_gears','加入光驱盖原生轴耳、钢轴、回位弹簧、扇形齿轮与小齿轮及金属支架，保留屋面与轴承间隙；机构用于结构观察，不代表经过验证的运动仿真。')


def stage14(m):
    from .wii import _coil
    # The original cartridge bay uses a single long dust door with a right spring.
    old=m.parts.pop('CartridgeFlap1');old.PhysicalPart=False;old.Visibility=False;m.group('Body').removeObject(old);m.group('Construction').addObject(old)
    obj=m.parts['CartridgeFlap0'];obj.Shape=m.rr(118.6,13.8,1.3,(0,81,81.2),.6);obj.FlatPlacement=obj.Placement;obj.Label='Full-width original cartridge dust door'
    ears=[]
    for x in [-54,54]:
        ear=Part.makeCylinder(1.4,5,V(x-2.5,87.8,80.7),V(1,0,0)).cut(Part.makeCylinder(.75,5.4,V(x-2.7,87.8,80.7),V(1,0,0)));ears.append(ear)
        m.cut('CartridgeDeck',Part.makeCylinder(1.65,5.6,V(x-2.8,87.8,80.7),V(1,0,0)),'Dust-door hinge ear clearance')
    fuse_feature(m,'CartridgeFlap0',Part.makeCompound(ears),'Integrated cartridge dust-door hinge ears',refine=False)
    m.cut('CartridgeDeck',Part.makeCylinder(.8,119.4,V(-59.7,87.8,80.7),V(1,0,0)),'Dust-door hinge shaft journal')
    m.cyl('CartridgeHingePin','Full-width cartridge door hinge pin',.6,118.6,(-59.3,87.8,80.7),'Ports',4,'metal',axis=(1,0,0),internal=True)
    spring=_coil('CartridgeSpring',1.15,4,1,.15,(45,87.8,80.7),axis=(1,0,0))
    m.feature('CartridgeSpring','Right cartridge dust-door return spring',spring,'Ports',4,'metal',True)
    for key in ['CartridgeDeck','CartridgeFlap0']:m.cut(key,Part.makeCylinder(1.55,4.6,V(44.7,87.8,80.7),V(1,0,0)),'Cartridge return-spring pocket')
    m.cut('UpperHousing',m.rr(24,25,12,(0,-96,60.5),2),'CD-open linkage cavity')
    fuse_feature(m,'OpenButton',Part.makeCylinder(2,9,V(0,-104,63)),'Open-key internal plunger',refine=False)
    hook=Part.makeCylinder(2,6.1,V(0,-89.5,75.4)).fuse(Part.makeBox(6,3,1.4,V(-3,-88.5,75.4)))
    fuse_feature(m,'DiscLid',hook,'Front disc-lid retaining hook',refine=False)
    slider=m.rr(8,17.8,3,(0,-92.9,64.8),.7).fuse(Part.makeBox(6,5,7.25,V(-3,-88,67.7)))
    m.feature('OpenLatchSlider','CD-lid release slider and catch',slider,'Controls',4,'white',True)
    for side in [-1,1]:m.box('OpenLatchGuide'+str(side),'Release-slider guide rail',1.5,12,4,(side*6,-93,64.1),'Controls',4,'black',.3,True)
    plate=m.rr(36,14,.4,(0,-94,63.4),1).cut(Part.makeCompound([Part.makeCylinder(1,.8,V(x,-95,63.2)) for x in [-16,16]]))
    m.feature('OpenLatchBracket','Metal release mechanism support plate',plate,'Controls',4,'metal',True)
    for i,x in enumerate([-16,16]):
        m.cut('UpperHousing',Part.makeCylinder(.8,8,V(x,-95,62)),'Release bracket screw pilot')
        m.screw('OpenBracketScrew'+str(i),(x,-95,62.5),'Controls',4,length=6.5,radius=1.8)
    m.cyl('OpenSpringPin','Release return-spring journal',.6,8,(8,-95,64),'Controls',4,'metal',internal=True)
    m.feature('OpenReturnSpring','Release torsion-coil study',_coil('OpenReturn',1.8,3,1,.2,(8,-95,68.5),axis=(0,0,1)),'Controls',4,'metal',True)
    m.ring('OpenSpringWasher','Release spring retaining washer',2.4,.8,.25,(8,-95,72.2),'Controls',4,'metal',internal=True)
    m.box('DoorSenseSwitch','Disc-door sensing switch',10,5,3.2,(-8,-89,69),'Controls',4,'black',.5,True)
    m.cyl('DoorSensePlunger','Disc-door sensing actuator',.6,1.3,(-2.8,-89,70.5),'Controls',4,'white',axis=(1,0,0),internal=True)
    m.cut('UpperHousing',m.rr(14,12,9,(78,-91,67),1.6),'Reset button switch pocket')
    m.box('ResetPCB','Separate reset switch board',10,8,.7,(78,-91,68.5),'Controls',4,'pcb',.5,True)
    m.box('ResetSwitch','Reset tactile switch',8,6,4,(78,-91,69.5),'Controls',4,'black',.5,True)
    m.cyl('ResetSwitchPlunger','Reset switch actuator',1.3,.8,(78,-91,73.7),'Controls',4,'white',internal=True)
    fuse_feature(m,'ResetButton',Part.makeCylinder(2,5.9,V(78,-91,75)),'Reset key internal stem',refine=False)
    fuse_feature(m,'PowerButton',Part.makeCylinder(2,2.8,V(-78,-91,78.4)),'Power key internal stem',refine=False)
    blank=m.doc.getObject('UpperHousingOuter').Shape.fuse(m.doc.getObject('CentralDeckCrown').Shape)
    posts=[]
    for key,x,color in [('Power',-47,'led'),('Access',47,'red')]:
        z=_height(blank,x,-104)
        m.cut('UpperHousing',Part.makeCylinder(1.3,12,V(x,-104,63)),'Indicator light-pipe well')
        m.box(key+'LampPCB','Separate '+key+' lamp board',14,8,.8,(x,-102,60),'Controls',4,'pcb',.5,True)
        m.cyl(key+'Lamp','Indicator emitter',2,2.8,(x,-104,61.0),'Controls',4,color,internal=True)
        m.cyl(key+'LightPipe','Indicator light pipe',.9,z-64.2-.7,(x,-104,64.2),'Controls',4,'white',internal=True)
        for j,xx in enumerate([x-5,x+5]):
            m.cut(key+'LampPCB',Part.makeCylinder(.85,1.2,V(xx,-100,59.8)),'Lamp board fixing bore')
            post=Part.makeCylinder(1.5,4.4,V(xx,-100,61.1)).cut(Part.makeCylinder(.75,4.8,V(xx,-100,60.9)));posts.append(post)
            m.screw(key+'LampScrew'+str(j),(xx,-100,58.9),'Controls',4,length=5,radius=1.3)
    fuse_feature(m,'UpperHousing',Part.makeCompound(posts),'Upper-cover lamp-board fixing posts',refine=False)
    m.profile['stages']=14
    m.checkpoint(14,'single_cartridge_door_lid_latch_and_control_boards','按初代拆解修正整片卡槽防尘门，加入轴销与回位弹簧；补齐光驱盖锁扣、开盖导向、门检测开关、复位键及分立指示灯板和导光件。')


def stage15(m):
    # Rear lid journals occupy local scallops in the moving lid, not the disc well.
    for x in [-66,66]:
        for dx in [-10,5]:m.cut('DiscLid',Part.makeCylinder(3.95,5.6,V(x+dx-.3,62.5,78.2),V(1,0,0)),'Fixed journal clearance inside moving disc lid')
    anchors=[]
    for i,y in enumerate([58.2,69]):
        sh=Part.makeCylinder(1.9,7,V(-77,y,76)).cut(Part.makeCylinder(.75,5,V(-80,y,77.4),V(1,0,0)));anchors.append(sh)
        screw=Part.makeCylinder(1.5,.35,V(-80.45,y,77.4),V(1,0,0)).fuse(Part.makeCylinder(.55,4.7,V(-80.12,y,77.4),V(1,0,0)))
        obj=m.parts['LidBracketScrew'+str(i)];obj.Shape=screw;obj.FlatPlacement=obj.Placement
    tool=next(o for o in m.doc.Objects if o.TypeId=='Part::Feature' and o.Label=='Upper-cover lid bracket fixing bosses');tool.Shape=Part.makeCompound(anchors)
    m.cut('DiscWell',Part.makeCylinder(2.1,7.5,V(-77,58.2,75.8)),'Local lid-bracket boss clearance at disc-well corner')
    plate=Part.makeBox(.6,16,24.7,V(-80,54.5,54))
    bores=[Part.makeCylinder(r,1,V(-80.2,y,z),V(1,0,0)) for y,z,r in [(62.5,58.9,1.1),(62.5,78.2,1.1),(58.2,77.4,.75),(69,77.4,.75)]]
    obj=m.parts['LidGearBracket'];obj.Shape=plate.cut(Part.makeCompound(bores));obj.FlatPlacement=obj.Placement
    m.profile['stages']=15
    m.checkpoint(15,'lid_journal_bracket_and_disc_well_clearances','依据装配检查为固定轴承开出盖板内部避让，降低齿轮支架和固定件，并调整光盘仓角部的支承间隙，保持外表面轮廓。')


def _saturn_pad_outline(w,h):
    anchors=[(-75,-7),(-64,26),(-39,43),(0,36),(39,43),(64,26),(75,-7),(66,-42),(53,-47.5),(25,-28),(0,-21),(-25,-28),(-53,-47.5),(-66,-42)]
    tangents=[(0,16),(9,11),(15,0),(14,0),(15,0),(9,-11),(0,-16),(-6,-9),(-8,0),(-12,9),(-10,0),(-12,-9),(-8,0),(-6,9)]
    curves=[]
    for i,a in enumerate(anchors):
        j=(i+1)%len(anchors);b=anchors[j];ta=tangents[i];tb=tangents[j]
        points=[a,(a[0]+ta[0],a[1]+ta[1]),(b[0]-tb[0],b[1]-tb[1]),b]
        bez=Part.BezierCurve();bez.setPoles([V(x*w/150,(y+2.25)*h/90.5) for x,y in points]);curves.append(bez.toBSpline())
    return curves


def stage16(m):
    from .psv import _ellipse
    from .wii import _cross_shape
    # The latch is outside the 12 cm disc sweep; give it a dedicated front-well window.
    m.cut('DiscWell',m.rr(38,21,20,(0,-94,60.2),2),'Front disc-well release mechanism window')
    cy=-215
    loft_shell(m,'PadBack','Original grey HSS-0101 rear shell',[(144,89,0,0,cy,.3),(150,95,0,0,cy,8),(150,95,0,0,cy,13)],[(140,85,0,0,cy,1.9),(146,91,0,0,cy,8),(146,91,0,0,cy,13.2)],'Controller',-6,'padgrey',_saturn_pad_outline)
    loft_shell(m,'PadFront','Original grey HSS-0101 front shell',[(150,95,0,0,cy,13.25),(146,91,0,0,cy,21),(140,85,0,0,cy,26)],[(146,91,0,0,cy,13.05),(142,87,0,0,cy,20.5),(136,81,0,0,cy,24.4)],'Controller',5,'padgrey',_saturn_pad_outline)
    m.cut('PadFront',Part.makeCylinder(18.2,9,V(-41,cy+1,21)),'Circular directional-pad opening')
    dpad=Part.makeCylinder(17.6,1.2,V(-41,cy+1,25.7)).fuse(_cross_shape(-41,cy+1,26.85,29,10.4,2.2))
    dpad=dpad.cut(Part.makeCylinder(2,.7,V(-41,cy+1,28.65)))
    m.feature('PadDPad','Floating disc and raised directional cross',dpad,'Controller',6,'black')
    arrows=[]
    for i in range(4):
        a=math.pi/4+i*math.pi/2;x=-41+14.5*math.cos(a);y=cy+1+14.5*math.sin(a)
        sh=Part.Face(Part.makePolygon([V(-.9,-.7),V(.9,-.7),V(0,1),V(-.9,-.7)])).extrude(V(0,0,.025));sh.rotate(V(),V(0,0,1),i*90-45);sh.translate(V(x,y,26.94));arrows.append(sh)
    m.feature('PadDirectionMarks','Four directional moulding marks',Part.makeCompound(arrows),'Controller',6,'metal')
    keys=[('A',27,-16,7.2,'black'),('B',43,-4,7.2,'black'),('C',56,7,7.2,'black'),('X',20,7,5.6,'saturnblue'),('Y',34,18,5.6,'saturnblue'),('Z',48,28,5.6,'saturnblue')]
    for key,x,y,r,color in keys:
        m.cut('PadFront',Part.makeCylinder(r+.35,9,V(x,cy+y,21)),'Original '+key+' key opening')
        m.cyl('Pad'+key,'Original '+key+' action key',r,2.6,(x,cy+y,25.7),'Controller',6,color)
        m.label('Pad'+key+'Mark',key,3,(x-1,cy+y-1,28.34),'Controller',6,'metal')
    m.cut('PadFront',_ellipse(11.8,6.3,21,9,0,cy-10.5),'START key opening')
    m.feature('PadStart','Original blue oval START key',_ellipse(11,5.5,25.7,1.8,0,cy-10.5),'Controller',6,'saturnblue')
    m.label('PadStartMark','START',2.0,(-5.5,cy-4.5,26.05),'Controller',5,'metal')
    m.label('PadSegaMark','SEGA',5.5,(-10,cy+25,26.05),'Controller',5,'saturnblue')
    for side in [-1,1]:
        key='L' if side<0 else 'R';x=side*42
        tool=m.rr(32,10,9,(x,cy+37,18),2.5)
        for shell in ['PadBack','PadFront']:m.cut(shell,tool,'Shoulder '+key+' opening')
        cap=m.rr(31,9,4,(x,cy+37,20.5),2.3).common(m.doc.getObject('PadFrontOuter').Shape);cap.translate(V(0,0,.2))
        m.feature('PadShoulder'+key,'Original '+key+' shoulder key',cap,'Controller',5,'padgrey')
    m.profile['stages']=16
    m.checkpoint(16,'original_grey_hss0101_controller_shell_and_six_keys','建立原版灰色 HSS-0101 手柄的原生曲线前后壳、圆盘十字键、黑色 ABC、蓝色 XYZ / START 和肩键，并补齐主机前部锁扣的光盘仓避让。')


def _pad_membrane(m,key,base,points):
    holes=[Part.makeCylinder(r*.74,1.1,V(x,y,19.3)) for x,y,r in points]
    sh=base.cut(Part.makeCompound(holes))
    for x,y,r in points:
        dome=Part.makeCone(r,r*.58,3.3,V(x,y,20)).cut(Part.makeCone(r*.82,r*.4,3.0,V(x,y,19.95)))
        sh=sh.fuse(dome)
    return m.feature(key,'Moulded silicone button membrane',sh,'Controller',1,'saturnblue',True)


def stage17(m):
    cy=-215
    m.cut('CartridgeFlap0',Part.makeCylinder(.8,119.4,V(-59.7,87.8,80.7),V(1,0,0)),'Continuous cartridge door hinge bore')
    for x in [-52,-42,42,52]:m.cut('UpperHousing',Part.makeCylinder(.75,5,V(x,-100,60.9)),'Full-depth lamp-board screw pilot')
    outline=[(-66,-24),(-66,18),(-50,34),(-29,35),(0,30),(29,35),(50,34),(66,18),(66,-24),(40,-28),(22,-22),(0,-14),(-22,-22),(-40,-28)]
    pcb=Part.Face(Part.makePolygon([V(x,cy+y,17) for x,y in outline+[outline[0]]])).extrude(V(0,0,1.1))
    m.feature('PadPCB','HSS-0101 phenolic controller board study',pcb,'Controller',0,'copper',True)
    directions=[(-41,cy+9,4.5),(-33,cy+1,4.5),(-41,cy-7,4.5),(-49,cy+1,4.5)]
    action=[(x,cy+y,4.5) for x,y in [(27,-16),(43,-4),(56,7),(20,7),(34,18),(48,28)]]
    _pad_membrane(m,'PadDPadMembrane',Part.makeCylinder(16.5,.55,V(-41,cy+1,19.5)),directions)
    boundary=[(16,-25),(38,-25),(65,0),(64,36),(42,39),(12,15)]
    base=Part.Face(Part.makePolygon([V(x,cy+y,19.5) for x,y in boundary+[boundary[0]]])).extrude(V(0,0,.55))
    _pad_membrane(m,'PadActionMembrane',base,action)
    _pad_membrane(m,'PadStartMembrane',m.rr(16,10,.55,(0,cy-10.5,19.5),2),[(0,cy-10.5,3.0)])
    contacts=directions+action+[(0,cy-10.5,3.0)]
    for i,(x,y,r) in enumerate(contacts):
        m.cyl('PadCarbon'+str(i),'Printed carbon contact',r*.6,.05,(x,y,18.24),'Controller',0,'black',internal=True)
        m.cyl('PadPill'+str(i),'Conductive silicone contact pill',r*.38,.18,(x,y,22.5),'Controller',1,'black',internal=True)
    fuse_feature(m,'PadDPad',Part.makeCompound([Part.makeCylinder(1.6,2.4,V(x,y,23.6)) for x,y,r in directions]),'Directional-pad membrane actuators',refine=False)
    for key,(x,y,r) in zip(['A','B','C','X','Y','Z'],action):fuse_feature(m,'Pad'+key,Part.makeCylinder(1.6,2.4,V(x,y,23.6)),'Action key membrane actuator',refine=False)
    fuse_feature(m,'PadStart',Part.makeCylinder(1.2,2.4,V(0,cy-10.5,23.6)),'Start key membrane actuator',refine=False)
    m.box('PadLogic','Controller I/O logic study package',8,6,2,(0,cy+17,18.5),'Controller',0,'black',.4,True)
    m.label('PadLogicMark','PAD I/O',1.2,(-3.2,cy+16.5,20.55),'Controller',0,'white')
    for side in [-1,1]:
        fingers=[Part.makeBox(.32,1.2,.18,V(-2.5+i*1.65,cy+17+side*3.25-(1.2 if side<0 else 0),19)) for i in range(4)]
        m.feature('PadLogicLeads'+str(side),'Controller logic lead bank',Part.makeCompound(fingers),'Controller',0,'metal',True)
    for i in range(8):m.box('PadPassive'+str(i),'Controller support passive',1.3,.8,.6,(-14+i*3.5,cy+28,18.3),'Controller',0,'black' if i%2 else 'cream',.08,True)
    m.box('PadCableConnector','Nine-position controller harness connector',12,5,2.6,(0,cy+25,18.5),'Controller',0,'white',.4,True)
    for side in [-1,1]:
        key='L' if side<0 else 'R';x=side*41
        m.box('PadShoulderSwitch'+key,'Shoulder microswitch',8,6,3.6,(x,cy+28.8,18.4),'Controller',1,'black',.5,True)
        m.cyl('PadShoulderActuator'+key,'Shoulder switch actuator',.8,.4,(x,cy+31.9,21),'Controller',1,'white',axis=(0,1,0),internal=True)
    points=[(-61,-22),(61,-22),(-23,33),(23,33),(17,-17)];upper=[];lower=[];blank=m.doc.getObject('PadFrontOuter').Shape
    for i,(x,yy) in enumerate(points):
        y=cy+yy
        sh=Part.makeCylinder(2.3,12.8,V(x,y,14.2)).fuse(Part.makeCylinder(3.6,.65,V(x,y,16))).common(blank).cut(Part.makeCylinder(.85,13.2,V(x,y,14)));upper.append(sh)
        lower.append(Part.makeCylinder(2.1,12,V(x,y,1.7)).cut(Part.makeCylinder(.9,12.4,V(x,y,1.5))))
        m.cut('PadPCB',Part.makeCylinder(2.6,1.5,V(x,y,16.8)),'Controller board case-column clearance')
        m.cut('PadBack',[Part.makeCylinder(1.1,25,V(x,y,0)),Part.makeCylinder(1.95,2.6,V(x,y,-.1))],'Controller rear fixing and head recess')
        m.screw('PadCaseScrew'+str(i),(x,y,.4),'Controller',-5,length=22,radius=1.7)
    m.cut('PadActionMembrane',Part.makeCylinder(2.7,5,V(17,cy-17,19.2)),'Membrane relief around central case column')
    fuse_feature(m,'PadFront',Part.makeCompound(upper),'Five native front-shell screw columns and board shoulders',refine=False)
    fuse_feature(m,'PadBack',Part.makeCompound(lower),'Rear controller screw-post receivers',refine=False)
    for x,yy in points:m.cut('PadBack',Part.makeCylinder(.9,14,V(x,cy+yy,0)),'Continuous controller screw pilot')
    m.profile['stages']=17
    m.checkpoint(17,'controller_board_silicone_inputs_and_five_fixings','补齐原版手柄的电路板、三组硅胶膜、碳膜接点、I/O 器件、肩键微动开关与五处外壳固定；同时完善主机灯板螺孔及卡槽防尘门轴孔。')


def stage18(m):
    from .atari2600 import _rounded_route
    from .ps1 import _yz_strip
    def lead(key,label,points,group,color='black',r=.16,bend=.25):
        return m.feature(key,label,_rounded_route([V(*p) for p in points],bend,r),group,2,color,True)
    # Display-length cords and wire counts are study geometry, not a circuit netlist.
    for i in range(6):
        x=-97.5+(i-2.5)*1.9;edge=-119-i*.5;row=-75-i*.7;z=47+i*.6;ex=-110+(i-2.5)*.9;ey=35+i*.3
        lead('SupplyLead'+str(i),'PSU to mainboard harness study',[(x,-69,45.95),(x,-69,z),(x,row,z),(edge,row,z),(edge,35+i*.7,26+i*.5),(ex,ey,26+i*.5),(ex,ey,13.3)],'Power','black' if i%2 else 'red',.18)
    for i in range(2):
        x=-80+i*4
        lead('PowerSwitchLead'+str(i),'Latching power-switch lead',[(x,-85.2,70),(x,-82,70),(x,-78,62),(-96+i*2,-78,62),(-106+i*1.1,-55,52),(-106+i*1.1,-52,46)],'Power','white' if i else 'black',.22)
    obj=m.parts['OpticalDataSocket'];obj.Placement.Base+=V(18,0,0);obj.FlatPlacement=obj.Placement
    points=[(-90,13.2),(-84,13.2),(-80,30.3),(-75,30.3),(-75,46.65),(-69,46.65),(-69,46.85),(-75.2,46.85),(-75.2,30.5),(-80.15,30.5),(-84.15,13.4),(-90,13.4)]
    m.feature('MainOpticalRibbon','Folded optical-unit data ribbon',_yz_strip(-9.5,15,points),'Optical',1,'white',True)
    m.cut('MainShield',m.rr(17,3,1,(-2,-75,31.5),.5),'Optical data ribbon shield passage')
    m.cut('OpticalBase',m.rr(17,3,1.5,(-2,-75,41.9),.5),'Optical data ribbon base passage')
    m.box('CDInterfaceSocket','CD-subsystem board interface connector',9,4,2,(99,69,21.3),'Optical',0,'white',.3,True)
    points=[(62,13.2),(66.2,13.2),(66.2,23.5),(69,23.5),(69,23.7),(66,23.7),(66,13.4),(62,13.4)]
    m.feature('CDInterfaceRibbon','Mainboard to CD-subsystem interconnect',_yz_strip(96.5,5,points),'Optical',0,'white',True)
    m.cut('CDSubsystemPCB',m.rr(7,2,1.5,(99,66,19.7),.3),'CD-subsystem interconnect fold passage')
    for i in range(4):
        x=106+(i-1.5)*1.2;edge=74+i*.6;row=52-i*.7;ex=37+(i-1.5)*1.1
        lead('OpticalSupplyLead'+str(i),'CD subsystem to optical-unit supply lead',[(x,59,24.6),(x,row,28+i*.4),(edge,row,28+i*.4),(edge,-65-i*.7,28+i*.4),(edge,-65-i*.7,47.5+i*.4),(ex,-65,47.5+i*.4)],'Optical','black' if i%2 else 'white')
    m.cut('MainShield',m.rr(8,6,1,(75,-66,31.5),.5),'Optical supply harness shield passage')
    for i,(key,x) in enumerate([('Power',-47),('Access',47)]):
        for j in range(2):
            n=i*2+j;sx=x+(j-.5)*1.2;edge=(-23 if i==0 else 23)+j*.6;ex=-14.5+n
            lead(key+'LampLead'+str(j),'Separate indicator-board harness lead',[(sx,-97.8,61.4),(sx,-95.5,58),(edge,-95.5,53),(edge,-95.5,14.7+n*.35),(ex,-83,14.7+n*.35),(ex,-78,13.3)],'Controls','red' if j==0 else 'black',.13)
        m.cut('MainShield',m.rr(4,3,1,((-22.7 if i==0 else 23.3),-95.5,31.5),.4),'Lamp harness shield passage')
    for i in range(2):
        x=8+i*.8;ex=15.4+i*.9
        lead('DoorSenseLead'+str(i),'Disc-door sensing harness', [(-8+i*.8,-86.3,72.4),(-8+i*.8,-92,72.4),(-8+i*.8,-92,59),(x,-90,59),(x,-90,14.7+i*.4),(ex,-89,13.3)],'Controls','white' if i else 'black',.13)
        lead('ResetLead'+str(i),'Reset board harness',[(78+i*.8,-86.8,69),(78+i*.8,-84,65),(74+i*.8,-84,34),(74+i*.8,-84,15.3+i*.4),(24+i,-84,15.3+i*.4),(17.3+i,-89,13.3)],'Controls','white' if i else 'black',.13)
    m.cut('MainShield',m.rr(4,4,1,(8.4,-90,31.5),.4),'Door-sensing harness shield passage')
    m.cut('MainShield',m.rr(4,4,1,(74.4,-84,31.5),.4),'Reset harness shield passage')
    cy=-215;side=g.rotation((1,0,0),(0,0,1))
    for key in ['PadFront','PadBack']:m.cut(key,Part.makeCylinder(3.0,16,V(0,cy+37,14),V(0,1,0)),'Controller cable exit')
    m.ring('PadGrommet','Hollow controller cable strain relief',2.6,1.95,12,(0,cy+39,14),'Controller',0,'black',axis=(0,1,0))
    for i,color in enumerate(['red','black','white','blue','led','gold','copper','white','black']):
        sx=(i-4)*.65;ex=(i-4)*.38
        lead('PadWire'+str(i),'Controller cable conductor study',[(sx,cy+25,21.35),(sx,cy+30,21.35),(ex,cy+35,14),(ex,cy+45,14),(ex,cy+51,14)],'Controller',color,.12,.18)
    cable=_rounded_route([V(0,cy+51.2,14),V(0,-141,14),V(120,-141,14),V(146,-163,14),V(175,-163,14)],8,1.7)
    m.feature('PadCable','Original controller cord display length',cable,'Controller',0,'black')
    m.ring('PadPlugRelief','Controller plug cord relief',2.7,1.9,6.5,(168.5,-163,14),'Controller',0,'black',axis=(1,0,0))
    m.box('PadPlugGrip','Saturn controller plug grip',31,12,22,(175.2,-163,14),'Controller',0,'black',2,orient=side)
    head=m.rr(27,10,11,(197.4,-163,14),.9,side).cut(m.rr(24.5,7.5,10,(199.6,-163,14),.6,side))
    m.feature('PadPlugHead','Keyed nine-position controller plug',head,'Controller',0,'black')
    m.box('PadPlugTongue','Controller plug contact carrier',24,.7,8,(200,-163,13.8),'Controller',0,'black',.2,orient=side)
    for i in range(9):m.box('PadPlugContact'+str(i),'Controller plug contact',.7,.1,6,(201,-163+(i-4)*2.55,14.3),'Controller',0,'gold',.04,orient=side)
    m.profile['stages']=18
    m.checkpoint(18,'console_harnesses_folded_ribbons_and_controller_cord','加入主机供电、光驱排线、指示灯、门检测和复位线束及屏蔽通道，补齐手柄九芯线、护线套和原始矩形插头；展示走线与线数不定义原厂电路。')


def stage19(m):
    from .atari2600 import _rounded_route
    anchors=[]
    for i,y in enumerate([65,69]):
        anchors.append(Part.makeCylinder(1.9,7,V(-77,y,76)).cut(Part.makeCylinder(.75,5,V(-80,y,77.4),V(1,0,0))))
        sh=Part.makeCylinder(1.5,.35,V(-80.45,y,77.4),V(1,0,0)).fuse(Part.makeCylinder(.55,4.7,V(-80.12,y,77.4),V(1,0,0)))
        obj=m.parts['LidBracketScrew'+str(i)];obj.Shape=sh;obj.FlatPlacement=obj.Placement
    tool=next(o for o in m.doc.Objects if o.TypeId=='Part::Feature' and o.Label=='Upper-cover lid bracket fixing bosses');tool.Shape=Part.makeCompound(anchors)
    plate=Part.makeBox(.6,16,24.7,V(-80,54.5,54));bores=[Part.makeCylinder(r,1,V(-80.2,y,z),V(1,0,0)) for y,z,r in [(62.5,58.9,1.1),(62.5,78.2,1.1),(65,77.4,.75),(69,77.4,.75)]]
    obj=m.parts['LidGearBracket'];obj.Shape=plate.cut(Part.makeCompound(bores));obj.FlatPlacement=obj.Placement
    cy=-215
    for key in ['PadShoulderSwitchR','PadShoulderActuatorR']:
        obj=m.parts[key];obj.Placement.Base+=V(-10,0,0);obj.FlatPlacement=obj.Placement
    m.cut('PadActionMembrane',m.rr(9,7,5,(31,cy+28.8,18.7),.7),'Right shoulder-switch silicone clearance')
    obj=m.parts['PadActionMembrane'];obj.Shape=obj.Shape.common(m.doc.getObject('PadFrontInner').Shape);obj.FlatPlacement=obj.Placement
    m.ring('PadDPadRim','Dark directional-pad opening liner',18.1,17.7,1.1,(-41,cy+1,25.1),'Controller',5,'black')
    for i in range(2):m.cut('OpenLatchBracket',Part.makeCylinder(.35,1.1,V(-8+i*.8,-92,63.1)),'Door-sense wiring support-plate passage')
    # Original Japanese two-blade AC cord and figure-eight device connector.
    m.box('ACWallPlug','Japanese two-blade AC plug',23,17,11,(220,100,0),'Accessories',0,'black',1.7)
    for i,x in enumerate([213.8,226.2]):m.box('ACWallBlade'+str(i),'Flat AC blade',1.4,6.2,12.5,(x,100,11.1),'Accessories',0,'metal',.1)
    points=[V(220,91.3,5.5),V(220,55,5.5),V(320,55,8),V(320,20,8),V(292.2,20,8)]
    m.feature('ACCord','Mains cord display length',_rounded_route(points,7,1.8),'Accessories',0,'black')
    m.box('ACDeviceGrip','Figure-eight connector grip',24,12,10,(280,20,3),'Accessories',0,'black',1.3)
    head=Part.makeCylinder(4,10,V(267.8,16.7,8),V(-1,0,0)).fuse(Part.makeCylinder(4,10,V(267.8,23.3,8),V(-1,0,0)))
    holes=[Part.makeCylinder(1.25,10.5,V(268,y,8),V(-1,0,0)) for y in [16.7,23.3]]
    m.feature('ACDeviceHead','C7-style two-position connector study',head.cut(Part.makeCompound(holes)),'Accessories',0,'black')
    for i,y in enumerate([16.7,23.3]):m.ring('ACDeviceContact'+str(i),'Device mains socket contact',1,.7,6,(265.5,y,8),'Accessories',0,'metal',axis=(-1,0,0))
    # AV mini-DIN to composite video and stereo RCA, all detached for inspection.
    m.cyl('AVPlugGrip','AV mini-DIN connector grip',6.6,25,(220,-28,8),'Accessories',0,'black',axis=(0,1,0))
    m.ring('AVPlugShield','AV plug metal sleeve',5.5,4.7,8.4,(220,-2.7,8),'Accessories',0,'metal',axis=(0,1,0))
    coords=[(-3.2,2),(0,2),(3.2,2),(-4,0),(-1.4,0),(1.4,0),(4,0),(-3,-2.3),(0,-2.3),(3,-2.3)]
    carrier=Part.makeCylinder(4.4,3,V(220,-2.6,8),V(0,1,0)).cut(Part.makeCompound([Part.makeCylinder(.58,3.4,V(220+dx,-2.8,8+dz),V(0,1,0)) for dx,dz in coords]))
    m.feature('AVPlugCarrier','AV plug contact insulator',carrier,'Accessories',0,'black')
    for i,(dx,dz) in enumerate(coords):m.cyl('AVPlugPin'+str(i),'AV plug contact',.4,5.9,(220+dx,-1.4,8+dz),'Accessories',0,'gold',axis=(0,1,0))
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
    m.ring('BlankDisc','Blank 12 cm optical study medium',60,7.5,1.2,(240,-300,0),'Accessories',0,'metal')
    m.ring('BlankDiscHub','Transparent disc hub study',17,7.55,.04,(240,-300,1.24),'Accessories',0,'white')
    m.label('BlankDiscMark','BLANK CD',3,(227,-277,1.30),'Accessories',0,'black')
    m.profile['stages']=19
    m.checkpoint(19,'controller_fit_original_ac_av_cords_and_blank_disc','调整盖板固定与手柄硅胶边界，补齐原版形式的日式电源线、八字端头、十接点 AV 转三 RCA 线及空白 12 cm 光盘，保留独立配件和组件编号。')


def stage20(m):
    from .atari2600 import _rounded_route
    for obj in m.doc.Objects:
        if obj.Name.startswith(('CartridgeDeck','UpperHousing')) and 'Refine' in obj.PropertiesList:obj.Refine=False
    def replace(key,points,r=.13):
        obj=m.parts[key];obj.Shape=_rounded_route([V(*p) for p in points],.25,r);obj.FlatPlacement=obj.Placement
    for i,(key,x) in enumerate([('Power',-47),('Access',47)]):
        for j in range(2):
            n=i*2+j;sx=x+(j-.5)*1.2;edge=(-23 if i==0 else 23)+j*.6;ex=-14.5+n;row=-95.5-j*.6;z=14.7+n*.35
            replace(key+'LampLead'+str(j),[(sx,-97.8,61.4),(sx,row,58+j*.6),(edge,row,53+j*.6),(edge,row,z),(ex,row,z),(ex,-83,z),(ex,-78,13.3)])
    for i in range(2):
        x=8+i*.8;ex=15.4+i*.9;row=-93.5-i*.6
        replace('DoorSenseLead'+str(i),[(-8+i*.8,-86.3,72.4+i*.3),(-8+i*.8,-92-i*.6,72.4+i*.3),(-8+i*.8,-92-i*.6,59+i*.6),(x,row,59+i*.6),(x,row,13.7+i*.3),(ex,-89,13.3)])
        row=-84-i*.6
        replace('ResetLead'+str(i),[(78+i*.8,-86.8,69),(78+i*.8,row,65+i*.5),(74+i*.8,row,34),(74+i*.8,row,15.3+i*.4),(24+i,row,15.3+i*.4),(17.3+i,-89,13.3)])
        # Keep the switch leads distinct even along the long horizontal traverse.
        x=-80+i*4
        replace('PowerSwitchLead'+str(i),[(x,-85.2,70),(x,-82,70+i*.5),(x,-78-i*.8,62+i*.6),(-96+i*2,-78-i*.8,62+i*.6),(-106+i*1.1,-55,52+i*.5),(-106+i*1.1,-52,46)],.22)
    tool=next(o for o in m.doc.Objects if o.TypeId=='Part::Feature' and o.Label.startswith('Door-sensing harness shield passage · tool'));tool.Shape=m.rr(4,4,1,(8.4,-93.8,31.5),.4)
    for obj in m.doc.Objects:
        if obj.TypeId=='Part::Feature' and obj.Label.startswith('Door-sense wiring support-plate passage · tool') and abs(obj.Shape.BoundBox.Center.x+7.2)<.01:
            obj.Shape=Part.makeCylinder(.35,1.1,V(-7.2,-92.6,63.1))
    m.doc.recompute()
    for obj in m.parts.values():obj.Shape.check(True)
    m.profile['stages']=20
    m.checkpoint(20,'separated_harness_routes_and_preserved_trim_surfaces','按装配求交分开灯板、门检测、复位和电源开关线束，调整相应通孔，并保留卡槽衬框和上壳的原始修剪曲面；全部已建组件执行严格实体检查。')


def stage21(m):
    m.cut('UpperHousing',Part.makeCylinder(1.15,30.4,V(-85.2,62.5,78.2),V(1,0,0)),'Continuous left lid-hinge shaft passage').Refine=False
    for y in [65,69]:m.cut('UpperHousing',Part.makeCylinder(.75,5.4,V(-80.4,y,77.4),V(1,0,0)),'Continuous lid-bracket fixing pilot').Refine=False
    old=m.parts['PadActionMembrane'];inner=m.doc.getObject('PadFrontInner')
    obj=m.doc.addObject('Part::Common','PadActionMembraneClipped');obj.Base=old;obj.Tool=inner;obj.Refine=False
    m.doc.recompute();obj.Shape.check(True);old.PhysicalPart=False
    m.register(obj,'PadActionMembrane','Controller',1,'saturnblue',True);obj.Label='Silicone action membrane inside controller cavity';old.Visibility=False;inner.Visibility=False
    m.doc.recompute()
    for obj in m.parts.values():obj.Shape.check(True)
    m.profile['stages']=21
    m.checkpoint(21,'continuous_lid_pilots_and_native_membrane_boundary','贯通铰链支承与支架固定孔，采用原生求交限制硅胶膜边界，使后续重算仍保留真实间隙，并复查全部组件的严格实体有效性。')


def stage22(m):
    from .atari2600 import _rounded_route
    # Place the second switch lead on the far side of the first descending bend.
    points=[V(-76,-85.2,70),V(-76,-82,70.5),V(-76,-77.2,62.6),V(-94,-77.2,62.6),V(-104.9,-55,52.5),V(-104.9,-52,46)]
    obj=m.parts['PowerSwitchLead1'];obj.Shape=_rounded_route(points,.25,.22);obj.FlatPlacement=obj.Placement
    obj.Shape.check(True)
    m.profile['stages']=22
    m.checkpoint(22,'power_switch_bend_final_clearance','移开第二根电源开关线与第一根下降弯管的局部相交，保留端头位置及相邻板件间隙。')

STAGES=[stage01,stage02,stage03,stage04,stage05,stage06,stage07,stage08,stage09,stage10,stage11,stage12,stage13,stage14,stage15,stage16,stage17,stage18,stage19,stage20,stage21,stage22]


def finalize(model):
    from .deliver import finalize as shared_finalize
    result=shared_finalize(model)
    model.snapshot('final_front',normal=(.2,-1.5,.7),assemblies=model.profile['envelope_groups'])
    model.snapshot('final_hero',normal=(.3,-.7,2.3),assemblies=result[0]['handheld_groups'])
    model.doc.save()
    return result
