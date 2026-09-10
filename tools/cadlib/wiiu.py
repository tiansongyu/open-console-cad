"""Launch white Wii U Basic study with a rounded constant-section enclosure."""
import math
import FreeCAD as App
import Part
from .core import V
from . import geometry as g
from .retro_common import fuse_feature

FRONT=g.rotation((0,-1,0),(0,0,1))
REAR=g.rotation((0,1,0),(0,0,1))


def stage01(m):
    m.colors.update(wiiuwhite=(.9,.91,.9),wiigrey=(.65,.66,.67),ublue=(.04,.55,.77),cream=(.82,.81,.72))
    m.params.set('A3','Depth (Y)');m.params.set('A4','Plastic body height (Z)')
    blank=g.rounded_body(m.doc,'BodyBlank','Rounded WUP-001 plastic envelope',172,46,9,263.5,(0,-129.25,23),orient=REAR,color=m.colors['wiiuwhite'])
    m.group('Construction').addObject(blank)
    inner=g.part_feature(m.doc,'BodyCavityTool','Rounded inner enclosure cavity',m.rr(168.8,42.8,261.9,(0,-129.4,23),7.4,REAR));m.group('Construction').addObject(inner)
    shell=g.boolean_cut(m.doc,'BodyShell','Open-front rounded enclosure',blank,inner);m.group('Construction').addObject(shell)
    for key,z,height,layer in [('LowerHousing',-.1,22.1,-6),('UpperHousing',22.25,24,6)]:
        tool=g.part_feature(m.doc,key+'SplitTool','Native horizontal shell split',Part.makeBox(180,280,height,V(-90,-140,z)));m.group('Construction').addObject(tool)
        obj=m.doc.addObject('Part::Common',key);obj.Base=shell;obj.Tool=tool;obj.Refine=True;m.doc.recompute();obj.Shape.check(True)
        m.register(obj,key,'Body',layer,'wiiuwhite');obj.Label='WUP-001 '+('lower' if layer<0 else 'upper')+' rounded shell'
        tool.Visibility=False
    bezel=g.rounded_body(m.doc,'FrontBezelBody','Separate rounded Wii U faceplate',172,46,9,4.75,(0,-129.5,23),orient=FRONT,color=m.colors['wiiuwhite'])
    m.register(bezel,'FrontBezel','Body',5,'wiiuwhite')
    m.cut('FrontBezel',m.rr(168.8,42.8,3.25,(0,-129.3,23),7.4,FRONT),'Hollow faceplate with 1.7 mm front skin')
    blank.Visibility=False;inner.Visibility=False;shell.Visibility=False
    for i,(x,y) in enumerate([(-69,-110),(69,-110),(-69,110),(69,110)]):m.box('Foot'+str(i),'Rubber placement pad',8,15,1.2,(x,y,-1.2),'Body',-6,'rubber',1.4)
    m.profile['stages']=1
    m.checkpoint(1,'native_rounded_wup001_enclosure','按 172 × 268.5 × 46 mm 塑料主体建立原生圆角截面、长向拉伸、空心壳及上下分件，保留独立前面板和外伸脚垫。')


def stage02(m):
    m.cut('FrontBezel',m.rr(132,6.9,6,(7,-129,32.7),3.4,FRONT),'Slot-loading optical disc opening')
    slot=m.rr(131.4,6.3,1.3,(7,-132.75,32.7),3.1,FRONT).cut(m.rr(129.3,3.8,1.7,(7,-132.55,32.7),1.85,FRONT))
    m.feature('DiscSlotTrim','Dark optical slot liner',slot,'Optical',4,'black')
    for key,x,z,r in [('Power',-68,11.5,4.6),('Eject',-68,32.7,4.6),('Sync',-34.5,11.5,2.7)]:
        shape=Part.makeCylinder(r+.3,5,V(x,-130,z),V(0,-1,0))
        m.cut('FrontBezel',shape,key+' control aperture')
        m.cyl(key+'Button',key+' faceplate control',r,1.5,(x,-132.9,z),'Controls',5,'red' if key=='Sync' else 'wiiuwhite',axis=(0,-1,0))
    for key,x,z,color in [('PowerLED',-68,19.8,'ublue'),('DiscLED',-68,40.3,'wiigrey')]:
        m.cut('FrontBezel',Part.makeCylinder(.75,3,V(x,-132,z),V(0,-1,0)),key+' light aperture')
        m.cyl(key,'Front indicator lens',.6,.3,(x,-134.1,z),'Controls',5,color,axis=(0,-1,0))
    ring=Part.makeCylinder(2.5,.03).cut(Part.makeCylinder(2.05,.06,V(0,0,-.01)))
    symbol=ring.cut(Part.makeBox(1.2,3,.1,V(-.6,.9,-.02))).fuse(Part.makeBox(.4,2.6,.03,V(-.2,.5,0)))
    symbol.Placement=App.Placement(V(-68,-134.44,11.5),FRONT);m.feature('PowerSymbol','Power icon',symbol,'Controls',5,'wiigrey')
    points=[(-2,-.2),(2,-.2),(0,2)];tri=Part.Face(Part.makePolygon([V(x,y) for x,y in points+[points[0]]])).extrude(V(0,0,.03))
    tri=Part.makeCompound([tri,Part.makeBox(4,.45,.03,V(-2,-1.3,0))]);tri.Placement=App.Placement(V(-68,-134.44,32.7),FRONT)
    m.feature('EjectSymbol','Optical eject icon',tri,'Controls',5,'wiigrey')
    for key,text,size,pos in [('PowerMark','POWER',1.8,(-72,-134.29,4.8)),('EjectMark','EJECT',1.8,(-72,-134.29,25.7)),('SyncMark','SYNC',1.8,(-38,-134.29,4.8)),('WiiUWord','Wii U',6,(60,-134.29,10))]:m.label(key,text,size,pos,'Body',5,'wiigrey',rotation=FRONT)
    m.cut('FrontBezel',m.rr(87,15,5.5,(14,-129.2,11.7),1.4,FRONT),'Front SD and USB compartment opening')
    m.box('FrontFlap','Front SD and dual-USB cover',86.4,14.4,1.25,(14,-132.9,11.7),'Body',5,'wiiuwhite',1.2,orient=FRONT)
    m.box('FrontIOPCB','Front SD and USB interface board',84,18,1.0,(14,-118,6.0),'Ports',0,'pcb',.8,True)
    card=m.rr(28,6.4,14,(-7,-116,12),.6,FRONT).cut(m.rr(25.4,3.8,14.4,(-7,-115.8,12),.4,FRONT))
    m.feature('SDPort','Front nine-contact SD reader',card,'Ports',0,'metal',True)
    m.box('SDTongue','SD contact carrier',24,10,.6,(-7,-123,10.25),'Ports',0,'black',.2,True)
    for i in range(9):m.box('SDContact'+str(i),'SD reader spring contact',.75,8,.1,(-7+(i-4)*2.5,-123,10.93),'Ports',0,'gold',.06,True)
    for i,x in enumerate([24,46]):
        frame=m.rr(15,7,13.8,(x,-116,12),.5,FRONT).cut(m.rr(13.8,5.8,14.2,(x,-115.8,12),.3,FRONT))
        m.feature('FrontUSB'+str(i),'Front USB-A shield',frame,'Ports',0,'metal',True)
        m.box('FrontUSBTongue'+str(i),'USB contact tongue',11.8,9,1,(x,-123,10.6),'Ports',0,'black',.3,True)
        for j in range(4):m.box('FrontUSBPin'+str(i)+'_'+str(j),'USB-A spring contact',.7,7,.1,(x+(j-1.5)*2.5,-123,11.67),'Ports',0,'gold',.06,True)
    m.profile['stages']=2
    m.checkpoint(2,'front_disc_slot_controls_sd_and_dual_usb','加入吸入式光盘槽、电源与退盘控制、外露红色同步键，以及独立前门内的九接点 SD 卡座与双 USB 接口。')



def _rear_cut(m,shape,label):
    for key in ['LowerHousing','UpperHousing']:m.cut(key,shape,label)


def _hdmi_shape(w,h,t):
    points=[(-w/2,h/2),(w/2,h/2),(w/2,-h/2+1.8),(w/2-2.4,-h/2),(-w/2+2.4,-h/2),(-w/2,-h/2+1.8)]
    return Part.Face(Part.makePolygon([V(x,y) for x,y in points+[points[0]]])).extrude(V(0,0,t))


def stage03(m):
    m.colors['yellow']=(.94,.72,.08)
    for key,x,z,w,h,color in [('DC',65,10.5,14,11,'yellow'),('Sensor',40,27,10,7,'red')]:
        _rear_cut(m,m.rr(w+.7,h+.7,8,(x,128.8,z),.8,REAR),key+' rear opening')
        socket=m.rr(w,h,13.8,(x,120,z),.7,REAR).cut(m.rr(w-2.5,h-2.5,10.5,(x,124.5,z),.4,REAR))
        m.feature(key+'Socket',key+' two-contact keyed connector',socket,'Ports',0,color,True)
        for i,dx in enumerate([-w/5,w/5]):m.cyl(key+'Contact'+str(i),'Power connector contact',.55,7,(x+dx,126,z),'Ports',0,'gold',axis=(0,1,0),internal=True)
    _rear_cut(m,m.rr(26.5,12.5,8,(40,128.8,10),1.2,REAR),'Wii AV Multi Out opening')
    av=m.rr(26,12,14,(40,119.8,10),1,REAR).cut(m.rr(23.2,9.2,14.4,(40,119.6,10),.6,REAR))
    m.feature('AVSocket','Original sixteen-contact AV Multi Out',av,'Ports',0,'black',True)
    m.box('AVTongue','AV contact tongue',21.5,10,1.3,(40,127,9.0),'Ports',0,'black',.3,True)
    for row in range(2):
        for i in range(8):m.box('AVContact'+str(row)+'_'+str(i),'AV Multi Out contact',.65,8,.1,(40+(i-3.5)*2.6,127,8.83 if row==0 else 10.36),'Ports',0,'gold',.06,True)
    opening=_hdmi_shape(17.6,7.1,8);opening.Placement=App.Placement(V(12,128.8,9.6),REAR);_rear_cut(m,opening,'HDMI Type A trapezoidal aperture')
    outer=_hdmi_shape(17,6.5,12.4);inside=_hdmi_shape(15.8,5.3,12.8);inside.translate(V(0,0,-.2));cage=outer.cut(inside);cage.Placement=App.Placement(V(12,121.4,9.6),REAR)
    m.feature('HDMIShield','HDMI Type A formed metal shell',cage,'Ports',0,'metal',True)
    m.box('HDMITongue','HDMI insulating contact tongue',13.2,8,.8,(12,127,9.1),'Ports',0,'black',.3,True)
    for row,n in enumerate([10,9]):
        for i in range(n):m.box('HDMIContact'+str(row)+'_'+str(i),'HDMI Type A contact',.35,6,.08,(12+(i-(n-1)/2)*1.25,127,8.96 if row==0 else 9.95),'Ports',0,'gold',.04,True)
    for i,z in enumerate([10.5,23]):
        x=-66;_rear_cut(m,m.rr(15.7,7.4,8,(x,128.8,z),.6,REAR),'Rear stacked USB-A aperture')
        frame=m.rr(15.1,6.8,13.8,(x,120,z),.5,REAR).cut(m.rr(13.9,5.6,14.2,(x,119.8,z),.3,REAR))
        m.feature('RearUSB'+str(i),'Rear stacked USB-A shield',frame,'Ports',0,'metal',True)
        m.box('RearUSBTongue'+str(i),'USB-A contact carrier',11.9,9,1,(x,127,z-1.1),'Ports',0,'black',.3,True)
        for j in range(4):m.box('RearUSBPin'+str(i)+'_'+str(j),'USB-A contact',.7,7,.1,(x+(j-1.5)*2.5,127,z-.03),'Ports',0,'gold',.06,True)
    grille=[m.rr(10.8,3.7,6,(-39+col*13,130,5.2+row*5.3),.4,REAR) for col in range(3) for row in range(7)]
    _rear_cut(m,Part.makeCompound(grille),'Three-column rear cooling grille')
    for key,text,x,z in [('DCTitle','AC ADAPTER',73,20),('AVTitle','AV MULTI OUT',53,21),('HDMITitle','HDMI OUT',20,18),('SensorTitle','SENSOR BAR',48,33)]:m.label(key,text,1.6,(x,134.29,z),'Body',6,'wiigrey',rotation=REAR)
    sidecuts=[Part.makeBox(7,2.5,19,V(x,y,12)) for x in [-89,82] for y in range(-95,102,7)]
    for key in ['LowerHousing','UpperHousing']:m.cut(key,Part.makeCompound(sidecuts),'Side ventilation slots')
    m.profile['stages']=3
    m.checkpoint(3,'rear_hdmi_av_stacked_usb_and_cooling_grille','补齐背面 HDMI 十九接点、AV 十六接点、感应条与供电口，以及堆叠双 USB、三列排风格栅和两侧通风槽。')



def stage04(m):
    from .wii import _sop
    old=m.parts.pop('FrontIOPCB');old.PhysicalPart=False;old.Visibility=False
    m.box('MainPCB','WUP-001 Basic motherboard',158,240,1.2,(0,-2,6),'Mainboard',0,'pcb',1.5,True)
    mount=[(-70,-109),(70,-109),(-70,-14),(70,-14),(-65,100),(66,100),(29,13)]
    m.cut('MainPCB',[Part.makeCylinder(1.25,1.6,V(x,y,5.8)) for x,y in mount],'Mainboard mounting bores')
    m.box('MCMSubstrate','Multi-chip CPU/GPU carrier',46,46,.9,(0,55,7.65),'Mainboard',0,'pcb',1.1,True)
    balls=[Part.makeSphere(.2,V(x,y,7.43)) for x in [-18,-9,0,9,18] for y in [37,46,55,64,73]]
    m.feature('MCMInterconnect','Schematic package interconnect field',Part.makeCompound(balls),'Mainboard',0,'metal',True)
    m.box('GPUDie','AMD-based graphics die study',17,17,1,(-7,50,8.7),'Mainboard',0,'black',.4,True)
    m.box('CPUDie','IBM-based processor die study',9,9,1,(12,63,8.7),'Mainboard',0,'black',.3,True)
    m.label('GPUCaption','GPU',2.3,(-11,49,9.74),'Mainboard',0,'wiigrey')
    m.label('CPUCaption','CPU',1.7,(9.5,62,9.74),'Mainboard',0,'wiigrey')
    cover=m.rr(44,44,4.1,(0,55,8.8),3).cut(m.rr(41.6,41.6,2.6,(0,55,8.7),2.3))
    m.feature('MCMCover','Common CPU/GPU heat spreader',cover,'Cooling',1,'metal',True)
    m.label('MCMMark','CPU + GPU',3,(-13,53,12.94),'Cooling',1,'black')
    for i,(x,y) in enumerate([(-54,38),(-54,61),(-21,-4),(3,-4)]):
        m.box('DDR3_'+str(i),'DDR3L memory package',10.5,14,1.3,(x,y,7.7),'Mainboard',0,'black',.3,True)
        m.label('DDR3Mark'+str(i),'DDR3',1.8,(x-3.5,y-.7,9.04),'Mainboard',0,'wiigrey')
    m.box('EMMC8GB','Basic-model 8 GB eMMC study package',14,14,1.3,(46,-96,7.7),'Mainboard',0,'black',.3,True)
    m.label('EMMCMark','8 GB',2.0,(42,-97,9.04),'Mainboard',0,'wiigrey')
    _sop(m,'HDMIController','HDMI',39,92,13,13,64)
    _sop(m,'SystemController','DRH-WUP',-45,-49,11,11,48)
    _sop(m,'AudioCodec','AUDIO',52,52,9,8,32)
    for i,(x,y) in enumerate([(49,2),(49,22),(49,-38),(-26,-76)]):
        m.box('Regulator'+str(i),'Power regulator study package',6,6,1.3,(x,y,7.7),'Mainboard',0,'black',.4,True)
        m.box('PowerInductor'+str(i),'Power conversion inductor',8,8,4.5,(x+11,y,7.7),'Mainboard',0,'thermal',1,True)
        m.cyl('PowerCap'+str(i),'Power smoothing capacitor',3.1,6,(x-8,y,7.7),'Mainboard',0,'metal',internal=True)
    for i,y in enumerate([71,82,93,104]):m.cyl('RearPowerCap'+str(i),'Rear power smoothing capacitor',2.8,6,(68,y,7.7),'Mainboard',0,'metal',internal=True)
    for bank,(bx,by,nx,ny) in enumerate([(-56,-103,8,3),(-48,-76,5,3),(-55,-20,6,3),(-5,-47,8,3),(20,-96,5,3),(28,-63,7,3)]):
        for ix in range(nx):
            for iy in range(ny):m.box(f'SMD{bank}_{ix}_{iy}','Study passive component',1.5,.8,.5,(bx+ix*3.7,by+iy*4.0,7.4),'Mainboard',0,'cream' if (ix+iy)%3 else 'black',.1,True)
    for key,x,y,w,h in [('DriveData',-35,-108,24,5),('DrivePower',-62,-112,11,5),('FanSocket',-70,106,6,4)]:
        m.box(key,key+' connector body',w,h,2.2,(x,y,7.6),'Mainboard',0,'cream',.4,True)
        m.box(key+'Latch',key+' connector latch',w-1,h*.4,.5,(x,y,9.9),'Mainboard',0,'black',.2,True)
    m.label('BoardTitle','WUP-001 BASIC STUDY',2.5,(-23,-30,7.24),'Mainboard',0,'white')
    m.profile['stages']=4
    m.checkpoint(4,'basic_mainboard_mcm_four_memories_and_emmc','加入 Basic 主板、CPU/GPU 多芯片载板、四片 DDR3L 与 8 GB eMMC 封装，补齐视频、系统及分区供电器件；内部电路布置明确作为学习近似。')



def stage05(m):
    for key in ['SMD1_3_0','SMD1_4_0']:
        obj=m.parts[key];obj.Placement.Base+=V(0,-7,0);obj.FlatPlacement=obj.Placement
    # Three removable radio boards on the underside of the main motherboard.
    for key,title,x,y,w,h in [('Wifi','Wireless LAN module',-52,-80,31,24),('Stream','GamePad video-link radio',50,-64,34,25),('Bluetooth','Bluetooth controller radio',-52,65,28,22)]:
        m.box(key+'PCB',title+' PCB',w,h,.6,(x,y,4.0),'Wireless',-2,'pcb',.7,True)
        m.box(key+'Connector',title+' board connector',12,3,1.1,(x,y+h/2-3,4.7),'Wireless',-1,'cream',.3,True)
        m.box(key+'IC',title+' chipset package',8,8,1.1,(x,y,2.8),'Wireless',-2,'black',.3,True)
        can=m.rr(w-4,h-5,1.8,(x,y,2.0),.6).cut(m.rr(w-5.2,h-6.2,1.65,(x,y,2.3),.4))
        m.feature(key+'Shield',title+' lower shield can',can,'Wireless',-3,'metal',True)
        for i,xx in enumerate([x-w/2+3,x+w/2-3]):m.ring(key+'Coax'+str(i),'Miniature coax socket',1.25,.65,.65,(xx,y+h/2-3,3.25),'Wireless',-2,'gold',internal=True)
    m.box('CompatibilityNAND','512 MB compatibility NAND study package',12,15,1.35,(43,-99,4.45),'Mainboard',-1,'black',.3,True)
    m.profile['stages']=5
    m.checkpoint(5,'underside_radio_modules_and_compatibility_memory','补齐主板背面的三块独立无线模块、屏蔽罩、微型同轴端口和兼容模式存储器，并调整两枚器件以消除与电容的干涉。')


def _duct_loft(m,key,sections):
    import Sketcher
    from .retro_common import rounded_outline
    sketches=[]
    for i,(x,y,z,w,h,r) in enumerate(sections):
        sk=m.doc.addObject('Sketcher::SketchObject',key+'Profile'+str(i));curves=rounded_outline(w,h,r);sk.addGeometry(curves,False)
        for j in range(len(curves)):sk.addConstraint(Sketcher.Constraint('Block',j))
        sk.Placement=App.Placement(V(x,y,z),REAR);m.group('Construction').addObject(sk);sketches.append(sk)
    obj=m.doc.addObject('Part::Loft',key);obj.Sections=sketches;obj.Solid=True;obj.Ruled=True;m.group('Construction').addObject(obj);m.doc.recompute();obj.Shape.check(True)
    for sk in sketches:sk.Visibility=False
    return obj


def stage06(m):
    m.box('MCMThermal','MCM thermal interface pad',41,41,.3,(0,55,13.05),'Cooling',1,'thermal',1,True)
    base=m.rr(58,58,1.5,(0,55,13.5),1.5)
    fins=[Part.makeBox(.65,56,21.8,V(-27+i*3.2,27,14.95)) for i in range(18)]
    sink=base.multiFuse(fins).removeSplitter()
    holes=[Part.makeCylinder(1.4,25,V(x,y,13.3)) for x in [-25,25] for y in [30,80]]
    m.feature('Heatsink','Common finned MCM heatsink',sink.cut(Part.makeCompound(holes)),'Cooling',2,'metal',True)
    frame=m.rr(40,40,9,(-26,122,23),2,REAR).cut(Part.makeCylinder(18.2,9.4,V(-26,121.8,23),V(0,1,0)))
    holes=[Part.makeCylinder(1.2,9.4,V(-26+dx,121.8,23+dz),V(0,1,0)) for dx in [-16.5,16.5] for dz in [-16.5,16.5]]
    m.feature('FanFrame','Rear axial cooling fan frame',frame.cut(Part.makeCompound(holes)),'Cooling',1,'black',True)
    hub=Part.makeCylinder(6,6,V(-26,123,23),V(0,1,0));blades=[]
    for i in range(7):
        a=i*2*math.pi/7
        p=[V(-26+r*math.cos(a+t),125,23+r*math.sin(a+t)) for r,t in [(5.6,-.23),(17.3,-.08),(17.3,.2),(5.6,.24)]]
        blades.append(Part.Face(Part.makePolygon(p+[p[0]])).extrude(V(0,1.3,0)))
    m.feature('FanRotor','Seven-blade cooling rotor',hub.multiFuse(blades).removeSplitter(),'Cooling',1,'black',True)
    m.cyl('FanMotor','Fan motor support disc',6.3,.7,(-26,122,23),'Cooling',1,'pcb',axis=(0,1,0),internal=True)
    for i in range(4):
        arm=Part.makeBox(10.7,.35,.8,V(-19.5,122.3,22.6));arm.rotate(V(-26,122.3,23),V(0,1,0),i*90)
        m.feature('FanStrut'+str(i),'Cooling fan support strut',arm,'Cooling',1,'black',True)
    outer=_duct_loft(m,'AirDuctOuter',[(-3,84.4,25,53,25,2),(-15,101,24,46,32,2),(-26,121.5,23,40,40,2)])
    inner=_duct_loft(m,'AirDuctInner',[(-3,84.1,25,50.6,22.6,1),(-15,101,24,43.6,29.6,1),(-26,121.8,23,37.6,37.6,1)])
    shell=g.boolean_cut(m.doc,'AirDuct','Offset processor-to-fan air duct',outer,inner);shell.Shape.check(True);m.register(shell,'AirDuct','Cooling',2,'black',True);outer.Visibility=False;inner.Visibility=False
    m.profile['stages']=6
    m.checkpoint(6,'mcm_heatsink_axial_fan_and_offset_air_duct','加入多芯片封装的共用鳍片散热器、后部轴流风扇及原生剖面放样风道，保持散热层与外壳、端口和主板分离。')



def stage07(m):
    from .wii import stage07 as transport_study
    before=set(m.parts);checkpoint=m.checkpoint
    try:
        m.checkpoint=lambda *args:None
        transport_study(m)
    finally:m.checkpoint=checkpoint
    # Reuse the transport primitives inside a separately sized Wii U drive.
    for key in set(m.parts)-before:
        obj=m.parts[key];obj.Placement.Base+=V(0,-26,0);obj.FlatPlacement=obj.Placement
    bores=[Part.makeCylinder(1.35,1,V(x,y,24.05)) for x in [-54,68] for y in [-120,19]]
    base=m.rr(134,151,.7,(7,-50.5,24.2),1.5).cut(Part.makeCompound(bores))
    frame=m.rr(134,151,11.7,(7,-50.5,24.95),1.5).cut(m.rr(131.6,148.6,12,(7,-50.5,24.8),.8))
    frame=frame.cut(m.rr(129.8,5.7,6,(7,-122,32.7),2.5,FRONT))
    top=m.rr(134,151,.6,(7,-50.5,38.65),1.5)
    holes=[Part.makeCylinder(18,.9,V(7,-57,38.5)),Part.makeCylinder(9,.9,V(-33,9,38.5)),Part.makeCylinder(9,.9,V(47,9,38.5))]
    for key,shape in [('DriveBase',base),('DriveFrame',frame),('DriveTopShield',top.cut(Part.makeCompound(holes)))]:
        obj=m.parts[key];obj.Shape=shape;obj.FlatPlacement=obj.Placement
    m.cut('LoadingMotor',Part.makeCylinder(.9,5,V(61,-73,25)),'Optical loading-motor shaft clearance')
    for i,x in enumerate([-39,-14,11,36,61]):
        rib=m.rr(4,72,.6,(x,-7,39.3),1.8)
        m.feature('DriveLidRib'+str(i),'Pressed upper drive stiffening rib',rib,'Optical',5,'metal',True)
    for i,(x,y) in enumerate([(x,y) for x in [-54,68] for y in [-120,19]]):
        m.ring('DriveBush'+str(i),'Optical drive mounting bushing',3.1,1.4,1,(x,y,23.0),'Optical',2,'rubber',internal=True)
    m.profile['stages']=7
    m.checkpoint(7,'wiiu_slot_drive_pickup_and_pressed_cover','以共用传送机构原语建立 Wii U 吸入式光驱，重新确定机架尺寸、上盖加强筋和安装点，保留主轴、滚轮、齿轮及导轨光头。')



def stage08(m):
    m.cut('AirDuct',Part.makeBox(200,280,7.5,V(-100,-140,0)),'Open-bottom shroud clears the motherboard')
    for key,x,y,w,h in [('Wifi',-52,-80,31,24),('Stream',50,-64,34,25),('Bluetooth',-52,65,28,22)]:
        holes=[Part.makeCylinder(1.5,2.2,V(xx,y+h/2-3,1.9)) for xx in [x-w/2+3,x+w/2-3]]
        m.cut(key+'Shield',holes,'Coax connector reliefs in radio shield')
    for i,x in enumerate([-39,-14,11,36,61]):
        obj=m.parts['DriveLidRib'+str(i)];obj.Shape=m.rr(4,64,.6,(x,-10,39.3),1.8);obj.FlatPlacement=obj.Placement
    pcb_points=[(-70,-109),(70,-109),(-70,-14),(70,-14),(-65,100),(66,100),(29,13)]
    drive_points=[(x,y) for x in [-54,68] for y in [-120,19]]
    lower=m.rr(148,234,.15,(0,-2,1.7),1)
    holes=[Part.makeCylinder(2.8,.5,V(x,y,1.5)) for x,y in pcb_points+drive_points]
    m.feature('LowerShield','Lower motherboard shielding sheet',lower.cut(Part.makeCompound(holes)),'Shield',-4,'metal',True)
    top=m.rr(150,234,.4,(0,-2,16),1)
    holes=[m.rr(62,62,1,(0,55,15.8),1.5),m.rr(65,46,1,(-18,105,15.8),1.5)]
    holes += [Part.makeCylinder(2.9,1,V(x,y,15.8)) for x,y in drive_points]
    m.feature('MainShield','Upper motherboard shield with cooling aperture',top.cut(Part.makeCompound(holes)),'Shield',1,'metal',True)
    posts=[]
    for i,(x,y) in enumerate(pcb_points):
        posts.append(Part.makeCylinder(2.3,4.35,V(x,y,1.5)).cut(Part.makeCylinder(.85,4.8,V(x,y,1.3))))
        m.screw('PCBMount'+str(i),(x,y,7.65),'Internal',0,length=4,radius=1.7,axis=(0,0,-1))
    m.cut('MainPCB',[Part.makeCylinder(2.8,1.6,V(x,y,5.8)) for x,y in drive_points],'Optical-drive support passages')
    for i,(x,y) in enumerate(drive_points):
        posts.append(Part.makeCylinder(2.5,21.35,V(x,y,1.5)).cut(Part.makeCylinder(.85,22,V(x,y,1.3))))
        m.screw('DriveMount'+str(i),(x,y,25.3),'Internal',2,length=4,radius=1.9,axis=(0,0,-1))
    fuse_feature(m,'LowerHousing',Part.makeCompound(posts),'Motherboard and optical-drive support columns')
    outer=m.doc.getObject('BodyBlank').Shape;upperposts=[]
    for i,(x,y) in enumerate([(x,y) for x in [-79,79] for y in [-117,113]]):
        post=Part.makeCylinder(2.2,27,V(x,y,20)).common(outer).cut(Part.makeCylinder(.85,27.4,V(x,y,19.8)));upperposts.append(post)
        m.cut('LowerHousing',[Part.makeCylinder(.95,22,V(x,y,-.2)),Part.makeCylinder(2.1,1,V(x,y,-.2))],'Case shaft passage and recessed screw head')
        m.screw('CaseMount'+str(i),(x,y,.15),'Internal',-6,length=24,radius=1.85)
    fuse_feature(m,'UpperHousing',Part.makeCompound(upperposts),'Roof-clipped upper-shell fastening columns')
    m.profile['stages']=8
    m.checkpoint(8,'shield_layers_support_columns_and_clearances','加入上下屏蔽板、主板和光驱支柱及机壳螺钉；修正无线接口罩和风道底部的实际装配间隙，避免螺柱超出圆角外形。')



def stage09(m):
    from .retro_common import loft_shell,native_loft
    cy=-275
    loft_shell(m,'PadBack','WUP-010 curved rear enclosure',[(242,119,29,0,cy,10),(255.4,133.4,31,0,cy,22.5)],[(238.8,115.8,27.4,0,cy,11.6),(252.2,130.2,29.4,0,cy,22.7)],'Controller',-5,'wiiuwhite')
    for side in [-1,1]:
        x=side*97
        grip=native_loft(m,'GripOuter'+str(side),[(36,80,17,x,cy-8,0),(46,91,21,x,cy-8,6),(49,94,22,side*96,cy-8,12.5)])
        fuse_feature(m,'PadBack',grip.Shape,'Integrated curved palm grip')
        cavity=native_loft(m,'GripInner'+str(side),[(32.6,76.6,15.3,x,cy-8,1.7),(42.6,87.6,19.3,x,cy-8,7),(45.6,90.6,20.3,side*96,cy-8,13.2)])
        m.cut('PadBack',cavity.Shape,'Hollow palm-grip interior');grip.Visibility=False;cavity.Visibility=False
    loft_shell(m,'PadFront','WUP-010 curved front enclosure',[(255.4,133.4,31,0,cy,22.75),(250,128,31,0,cy,36.5),(242,120,30,0,cy,41)],[(252.2,130.2,29.4,0,cy,22.5),(246.8,124.8,29.4,0,cy,35),(238.8,116.8,28.4,0,cy,39.4)],'Controller',5,'wiiuwhite')
    m.cut('PadFront',m.rr(146,86,8,(0,cy+2,35),2),'6.2-inch display aperture')
    m.box('LCDBackplate','Display rear metal plate',145,85,.6,(0,cy+2,34),'Display',0,'metal',1.5,True)
    frame=m.rr(145,85,3.7,(0,cy+2,34.7),1.5).cut(m.rr(139.8,79.8,3.9,(0,cy+2,34.6),1.0))
    m.feature('LCDFrame','LCD perimeter support frame',frame,'Display',1,'black',True)
    m.box('LCDPanel','6.2-inch 16:9 LCD active-area study',137.3,77.2,1.2,(0,cy+2,38.6),'Display',3,'screen',.8)
    m.box('TouchLayer','Resistive touch front layer',145.3,85.3,.3,(0,cy+2,39.85),'Display',4,'screen',1.3)
    bezel=m.rr(145.3,85.3,.45,(0,cy+2,40.3),1.3).cut(m.rr(137.4,77.3,.7,(0,cy+2,40.2),.7))
    m.feature('DisplayBezel','Thin display-edge bezel',bezel,'Display',4,'black')
    m.profile['stages']=9
    m.checkpoint(9,'native_gamepad_curved_grips_and_touch_display','建立 GamePad 原生曲面前后壳、空心握柄和 6.2 英寸显示层，保留金属背板、LCD 支承、触摸层和黑色细边框的独立组件。')



def stage10(m):
    from .wii import _cross_shape
    cy=-275
    for side in [-1,1]:
        x=side*98;y=cy+32;key='LStick' if side<0 else 'RStick'
        m.cut('PadFront',Part.makeCylinder(11.6,10,V(x,y,35)),key+' circular opening')
        m.ring(key+'Rim','Analog-stick opening rim',13,11.7,.5,(x,y,41.03),'Controller',5,'wiiuwhite')
        m.cyl(key+'Pivot','Visible analog-stick pivot',8,3,(x,y,38.8),'Controller',4,'wiigrey')
        m.cyl(key+'Stem','Analog-stick stem',3.4,4.1,(x,y,41.9),'Controller',5,'wiiuwhite')
        cap=Part.makeCylinder(10.7,2.4,V(x,y,46.1)).cut(Part.makeSphere(24,V(x,y,71.3)))
        m.feature(key+'Cap','Concave analog thumb cap',cap,'Controller',6,'wiiuwhite')
    m.cut('PadFront',_cross_shape(-98,cy-7,36.8,18.8,6.7,7.0),'Directional-pad cross aperture')
    m.feature('PadDPad','GamePad directional cross',_cross_shape(-98,cy-7,39.5,18,6,3.4),'Controller',5,'wiiuwhite')
    for key,x,y,r,mark in [('A',108,cy-6,4.3,'A'),('B',98,cy-16,4.3,'B'),('X',98,cy+4,4.3,'X'),('Y',88,cy-6,4.3,'Y'),('Plus',96,cy-31,2.8,'+'),('Minus',96,cy-44,2.8,'-'),('Home',0,cy-53,4.0,''),('TV',50,cy-53,2.8,'TV'),('Power',72,cy-53,2.8,'')]:
        m.cut('PadFront',Part.makeCylinder(r+.3,7,V(x,y,37)),key+' button opening')
        m.cyl('Pad'+key,key+' control cap',r,2.7,(x,y,40.1),'Controller',5,'wiiuwhite')
        if mark:m.label('Pad'+key+'Mark',mark,2.7 if key not in ['TV'] else 1.9,(x-1,y-1,42.84),'Controller',5,'ublue' if key=='TV' else 'wiigrey')
    m.cut('PadFront',Part.makeCylinder(5.3,3,V(0,cy-53,39.5)),'HOME light-ring recess')
    m.ring('HomeLightRing','Blue HOME surround',5.1,4.15,.3,(0,cy-53,41.03),'Controller',5,'ublue')
    roof=[(-2.2,0),(0,2.1),(2.2,0),(1.6,0),(1.6,-1.7),(-1.6,-1.7),(-1.6,0)]
    symbol=Part.Face(Part.makePolygon([V(x,y) for x,y in roof+[roof[0]]])).extrude(V(0,0,.03));symbol.translate(V(0,cy-53,42.84));m.feature('HomeSymbol','HOME icon',symbol,'Controller',5,'wiigrey')
    power=Part.makeCylinder(1.7,.03).cut(Part.makeCylinder(1.3,.07,V(0,0,-.01))).cut(Part.makeBox(1.1,2.4,.1,V(-.55,.6,-.02)))
    power=power.fuse(Part.makeBox(.3,2,.03,V(-.15,.25,0)));power.translate(V(72,cy-53,42.84));m.feature('PadPowerSymbol','GamePad power icon',power,'Controller',5,'red')
    m.cut('PadFront',m.rr(50,7.3,7,(0,cy+54,37),3.5),'Camera and infrared window opening')
    strip=m.rr(49.4,6.7,1.0,(0,cy+54,40),3.2).cut(Part.makeCylinder(2.3,1.4,V(0,cy+54,39.8)))
    m.feature('CameraIRWindow','Dark camera and infrared window',strip,'Controller',5,'black')
    m.cyl('CameraLens','Front-facing camera lens',2.1,.75,(0,cy+54,40.15),'Controller',5,'screen')
    nfc=m.rr(12,10,.025,(-98,cy-34,41.04),1.1).cut(m.rr(11,9,.06,(-98,cy-34,41.02),.65))
    m.feature('NFCMark','NFC tap-area outline',nfc,'Controller',5,'wiigrey')
    m.label('PadBrand','Wii U',4.2,(-77,cy-55,41.04),'Controller',5,'wiigrey')
    for key,x,y,r in [('MicHole',-20,cy-53,.55),('BatteryLamp',34,cy-53,.65)]:
        m.cut('PadFront',Part.makeCylinder(r+.2,5,V(x,y,37)),key+' aperture')
        m.cyl(key+'Insert','Microphone / battery indicator insert',r,.4,(x,y,40.65),'Controller',5,'black' if key=='MicHole' else 'red')
    for side in [-1,1]:
        m.cut('PadFront',m.rr(4.2,2.0,5,(side*99,cy-50,37),.9),'Front stereo speaker opening')
        m.box('SpeakerOpening'+str(side),'Dark stereo speaker grille',3.8,1.6,.35,(side*99,cy-50,40.6),'Controller',5,'black',.7)
    m.profile['stages']=10
    m.checkpoint(10,'gamepad_dual_sticks_buttons_camera_and_nfc','补齐双摇杆、ABXY、十字键、START/SELECT、HOME 蓝色环、TV 和电源控制，加入前摄像头、红外窗口、NFC 标记及立体声开口。')



def stage11(m):
    cy=-275
    m.cut('MainShield',m.rr(76,48,1,(-10,105,15.8),1.5),'Complete angled-duct shield clearance')
    m.cut('MainPCB',[Part.makeCylinder(1.0,1.6,V(x,y,5.8)) for x in [-79,79] for y in [-117,113]],'Case-screw edge clearances')
    m.cut('PadBack',m.rr(85,48,5,(0,cy-8,8.8),4),'Rear battery access opening')
    m.box('PadBatteryDoor','Removable GamePad battery cover',84.2,47.2,1.2,(0,cy-8,10.1),'Controller',-5,'wiiuwhite',3.6)
    for side in [-1,1]:
        x=side*102;key='L' if side<0 else 'R'
        m.cut('PadFront',m.rr(22,10,8,(x,cy+52,36),3.7),key+' shoulder-button aperture')
        m.box('Pad'+key,key+' shoulder key',21.3,9.3,3,(x,cy+52,40.2),'Controller',5,'wiiuwhite',3.4)
        m.label('Pad'+key+'Mark',key,3,(x-1,cy+51,43.24),'Controller',5,'wiigrey')
        m.cut('PadBack',m.rr(27,15,12,(side*103,cy+43,5),4.5),'Rear Z'+key+' trigger aperture')
        m.box('PadZ'+key,'Rear Z'+key+' trigger',26.2,14.2,4.0,(side*103,cy+43,7.5),'Controller',-4,'wiiuwhite',4.1)
    m.cut('PadFront',m.rr(22,4.8,7,(-35,cy+60,27),1,REAR),'Top-edge volume-slider opening')
    m.box('PadVolume','Top volume slider',7,3.9,1.1,(-35,cy+64.2,27),'Controller',4,'wiigrey',.7,orient=REAR)
    m.cut('PadFront',Part.makeCylinder(2.8,9,V(0,cy+58,27),V(0,1,0)),'Headphone-jack aperture')
    m.ring('PadAudioJack','3.5 mm headphone socket',2.5,1.8,7.2,(0,cy+58.2,27),'Controller',1,'black',axis=(0,1,0),internal=True)
    m.cut('PadFront',m.rr(9.2,5.6,9,(35,cy+58,27),.8,REAR),'GamePad charging connector opening')
    charge=m.rr(8.6,5,7.2,(35,cy+58.2,27),.6,REAR).cut(m.rr(6.4,2.8,7.6,(35,cy+58,27),.3,REAR))
    m.feature('PadChargeSocket','GamePad two-contact charging socket',charge,'Controller',1,'wiigrey',True)
    for i,x in enumerate([33.4,36.6]):m.cyl('PadChargePin'+str(i),'GamePad charging contact',.35,5,(x,cy+60,27),'Controller',1,'gold',axis=(0,1,0),internal=True)
    m.cut('PadBack',m.rr(26,7,9,(0,cy-60,17),1,FRONT),'Bottom accessory-port aperture')
    ext=m.rr(25.4,6.4,6,(0,cy-60,17),.8,FRONT).cut(m.rr(23,4,6.4,(0,cy-59.8,17),.4,FRONT))
    m.feature('PadExtension','Bottom accessory connector',ext,'Controller',0,'black',True)
    m.box('PadExtensionTongue','Accessory connector tongue',20,4,.65,(0,cy-63,16.4),'Controller',0,'black',.2,True)
    for i in range(12):m.box('PadExtensionPin'+str(i),'Accessory connector study contact',.55,3,.08,((i-5.5)*1.6,cy-63,17.12),'Controller',0,'gold',.05,True)
    for side in [-1,1]:
        m.box('PadDockPad'+str(side),'Bottom charging-cradle contact',6,3,.08,(side*22,cy-59.4,10.15),'Controller',-4,'gold',.2)
    m.profile['stages']=11
    m.checkpoint(11,'gamepad_shoulders_battery_door_and_edge_ports','加入 L/R 与 ZL/ZR、可拆电池盖、音量滑块、耳机与充电端口、底部扩展口及充电触点，同时完善主机螺钉和风道的避让。')



def _poly(points,z,height):
    return Part.Face(Part.makePolygon([V(x,y,z) for x,y in points+[points[0]]])).extrude(V(0,0,height))


def stage12(m):
    cy=-275;back=g.rotation((0,0,-1),(0,1,0))
    outline=[(-80,52),(80,52),(80,-17),(55,-17),(55,10),(-56,10),(-56,-25),(-80,-25)]
    m.feature('PadMainPCB','GamePad main control board',_poly([(x,cy+y) for x,y in outline],26,1),'PadInternal',0,'pcb',True)
    for key,title,x,y,w,h in [('UIC','UIC-WUP',-29,32,11,11),('DRC','DRC-WUP',2,32,15,15),('TouchIC','TSC2046',30,36,6,6),('PadAudioIC','AIC3012',55,25,6,8),('PadGyro','GYRO',-48,34,4,4)]:
        m.box(key,title+' study package',w,h,1.8,(x,cy+y,24.05),'PadInternal',0,'black',.3,True)
        m.label(key+'Mark',title,min(1.5,w/(len(title)*.8)),(x+w/2-.5,cy+y-.6,24.01),'PadInternal',0,'wiigrey',rotation=back)
    for i in range(18):m.box('PadSMD'+str(i),'GamePad support passive',1.3,.7,.45,(-45+(i%6)*3.3,cy+15+(i//6)*3.5,25.4),'PadInternal',0,'cream',.1,True)
    m.box('PadRadioPCB','GamePad video-link radio board',25,33,.7,(-67,cy-3,23.7),'PadInternal',-1,'pcb',.7,True)
    m.box('PadRadioIC','BCM4319-family radio study package',8,8,1.4,(-67,cy-3,22.1),'PadInternal',-1,'black',.3,True)
    can=m.rr(22,26,2.9,(-67,cy-3,20.6),.7).cut(m.rr(20.8,24.8,2.6,(-67,cy-3,21.05),.4))
    m.feature('PadRadioShield','GamePad radio shield',can,'PadInternal',-2,'metal',True)
    m.box('PadNFCPCB','NFC controller board',22,20,.6,(-98,cy-34,27.6),'PadInternal',0,'pcb',.6,True)
    m.box('PadNFCIC','NFC controller package',6,6,1,(-98,cy-34,26.45),'PadInternal',0,'black',.3,True)
    loops=[]
    for i in range(3):
        loops.append(m.rr(20-i*1.5,18-i*1.5,.035,(-98,cy-34,28.25),2).cut(m.rr(19.45-i*1.5,17.45-i*1.5,.08,(-98,cy-34,28.23),1.75)))
    m.feature('PadNFCAntenna','Three-turn NFC antenna study',Part.makeCompound(loops),'PadInternal',1,'copper',True)
    frame=m.rr(159,98,1.4,(0,cy+2,31.4),4)
    windows=[]
    for sx in [-1,1]:
        for sy in [-1,1]:
            points=[(sx*7,cy+2+sy*6),(sx*72,cy+2+sy*6),(sx*72,cy+2+sy*41)]
            windows.append(_poly(points,31.2,1.8))
            points=[(sx*6,cy+2+sy*8),(sx*6,cy+2+sy*42),(sx*67,cy+2+sy*42)]
            windows.append(_poly(points,31.2,1.8))
    m.feature('DisplaySupport','Windowed display support frame',frame.cut(Part.makeCompound(windows)),'Display',-1,'wiiuwhite',True)
    m.box('PadBattery','Original 1500 mAh battery envelope',54,34,7,(0,cy-8,12.8),'PadInternal',-3,'battery',2,True)
    m.box('PadBatteryLabel','Battery label panel',47,28,.03,(0,cy-8,12.74),'PadInternal',-3,'white',1,True)
    m.label('PadBatteryText','3.7V 1500mAh',2.2,(18,cy-9,12.70),'PadInternal',-3,'black',rotation=back)
    for side in [-1,1]:
        m.box('PadButtonPCB'+str(side),'Separate directional / ABXY button board',23,54,.7,(side*98,cy-4,30.1),'PadInternal',1,'pcb',2,True)
        m.ring('PadSpeaker'+str(side),'Stereo speaker frame',7.0,5.8,3,(side*99,cy-49,35.6),'PadInternal',2,'black',internal=True)
        m.cyl('PadSpeakerCone'+str(side),'Stereo speaker diaphragm',5.5,.2,(side*99,cy-49,38),'PadInternal',2,'thermal',internal=True)
        m.cyl('PadSpeakerMagnet'+str(side),'Stereo speaker magnet',4.6,1.7,(side*99,cy-49,35.8),'PadInternal',2,'metal',internal=True)
    m.box('PadBottomPCB','HOME, TV and power control board',92,11,.7,(36,cy-53,30.0),'PadInternal',1,'pcb',1.2,True)
    m.box('PadCameraPCB','Front camera board',12,8,.65,(0,cy+54,34.1),'PadInternal',2,'pcb',.5,True)
    m.box('PadCamera','Front camera package',6,6,3,(0,cy+54,34.9),'PadInternal',2,'black',.6,True)
    for side in [-1,1]:m.box('PadIREmitter'+str(side),'Built-in infrared emitter module',5,4,1.4,(side*18,cy+54,36.5),'PadInternal',2,'black',.5,True)
    m.cyl('PadMicrophone','Microphone capsule',2.4,2,(-20,cy-53,36.5),'PadInternal',2,'metal',internal=True)
    m.profile['stages']=12
    m.checkpoint(12,'gamepad_boards_nfc_display_support_and_battery','补齐 GamePad 主板、无线和 NFC 模块、镂空显示支架、原版 1500 mAh 电池、独立按键板、相机、麦克风与立体声扬声器。')



def stage13(m):
    from .atari2600 import _helical_spring
    cy=-275
    for side in [-1,1]:
        x=side*98;y=cy+32;key='LStick' if side<0 else 'RStick'
        housing=m.rr(17.8,17.8,7,(x,y,29),2).cut(Part.makeCylinder(5.5,6.2,V(x,y,30)))
        m.feature(key+'Housing','Analog mechanism housing',housing,'PadInternal',2,'black',True)
        m.box(key+'PotX','X-axis analog potentiometer study',4.2,10,7,(x+11,y,29),'PadInternal',2,'cream',.7,True)
        m.box(key+'PotY','Y-axis analog potentiometer study',10,4.2,7,(x,y+12,29),'PadInternal',2,'cream',.7,True)
        spring=_helical_spring(3,1,4,.22);spring.translate(V(x,y,30.7));m.feature(key+'Spring','Analog centering spring',spring,'PadInternal',2,'metal',True)
        yoke=m.rr(12,12,1.3,(x,y,36.2),1).cut(Part.makeCylinder(3.7,1.6,V(x,y,36.1)))
        m.feature(key+'Yoke','Analog cross support',yoke,'PadInternal',3,'metal',True)
        m.cyl(key+'PivotPin','Analog pivot pin',1.2,14,(x-7,y,38.1),'PadInternal',3,'metal',axis=(1,0,0),internal=True)
        for part in [key+'Yoke',key+'Pivot']:m.cut(part,Part.makeCylinder(1.35,14.6,V(x-7.3,y,38.1),V(1,0,0)),'Analog pivot shaft passage')
    groups=[('DPad',-98,cy-7,8),('A',108,cy-6,4),('B',98,cy-16,4),('X',98,cy+4,4),('Y',88,cy-6,4),('Plus',96,cy-31,2.5),('Minus',96,cy-44,2.5),('Home',0,cy-53,3.7),('TV',50,cy-53,2.5),('Power',72,cy-53,2.5)]
    for key,x,y,r in groups:
        m.cyl('Pad'+key+'Carbon','Conductive button pill',r*.55,.08,(x,y,35.23),'PadInternal',2,'black',internal=True)
        m.ring('Pad'+key+'Dome','Silicone button dome',r,r*.58,.6,(x,y,35.4),'PadInternal',2,'rubber',internal=True)
        target='Pad'+key;top=39.6 if key=='DPad' else 40.2
        fuse_feature(m,target,Part.makeCylinder(min(1.8,r*.4),top-36.2,V(x,y,36.2)),'Integrated control-button stem')
    for key,x,y,w,h in [('Direction',-98,cy-7,22,23),('ABXY',98,cy-6,30,32)]:
        carrier=m.rr(w,h,4,(x,y,31.1),2).cut(m.rr(w-2,h-2,3.6,(x,y,30.9),1.3))
        m.feature('PadCarrier'+key,'Button carrier and support frame',carrier,'PadInternal',1,'wiiuwhite',True)
    for side in [-1,1]:
        x=side*99
        m.box('PadShoulderPCB'+str(side),'Shoulder button board',17,9,.7,(x,cy+50,29),'PadInternal',1,'pcb',1,True)
        m.box('PadShoulderSwitch'+str(side),'Shoulder tactile contact',6,5,2,(x,cy+50,30),'PadInternal',2,'black',.5,True)
        m.box('PadRearTriggerPCB'+str(side),'Rear trigger board',17,10,.7,(side*103,cy+43,14),'PadInternal',-2,'pcb',1,True)
        m.box('PadRearTriggerSwitch'+str(side),'Rear trigger tactile contact',7,6,1.8,(side*103,cy+43,12),'PadInternal',-2,'black',.7,True)
    m.cyl('PadRumbleMotor','GamePad vibration motor',4.2,18,(43,cy-28,22),'PadInternal',0,'metal',axis=(0,1,0),internal=True)
    m.feature('PadRumbleWeight','Eccentric vibration weight',Part.makeCylinder(3.7,2,V(43,cy-8,22),V(0,1,0),180),'PadInternal',0,'metal',True)
    for side in [-1,1]:
        obj=m.parts['PadDockPad'+str(side)];obj.Placement.Base+=V(0,0,-.3);obj.FlatPlacement=obj.Placement
    m.profile['stages']=13
    m.checkpoint(13,'gamepad_analog_modules_button_domes_and_feedback','加入双模拟摇杆的回中弹簧、支承和电位器、按键硅胶与推杆、肩键小板及偏心振动机构，保留可独立查看的机械和电子组件。')



def stage14(m):
    from .wii import _tri_fastener
    cy=-275;points=[(x,cy+y) for x in [-113,113] for y in [-20,15]]+[(x,cy+y) for x in [-75,75] for y in [-53,53]]
    tools=[Part.makeCylinder(2.7,20,V(x,y,24)) for x,y in points]
    for key in ['PadMainPCB','DisplaySupport']:m.cut(key,tools,'GamePad enclosure-column passages')
    posts=[];outer=m.doc.getObject('PadFrontOuter').Shape
    for i,(x,y) in enumerate(points):
        z=.2 if abs(x)>100 else 10.2
        m.cut('PadBack',[Part.makeCylinder(.95,31,V(x,y,z-.3)),Part.makeCylinder(1.9,.7,V(x,y,z-.2))],'Rear tri-point screw access')
        _tri_fastener(m,'PadCaseScrew'+str(i),x,y,z,29,'Controller')
        post=Part.makeCylinder(2.4,18,V(x,y,24)).common(outer).cut(Part.makeCylinder(.85,19,V(x,y,23.8)));posts.append(post)
    fuse_feature(m,'PadFront',Part.makeCompound(posts),'Eight roof-clipped GamePad fixing columns')
    ledge=m.rr(88,51,1.3,(0,cy-8,11.4),4.4).cut(m.rr(65,37,1.6,(0,cy-8,11.2),3))
    holes=[Part.makeCylinder(.85,1.7,V(x,cy-8,11.2)) for x in [-36,36]]
    fuse_feature(m,'PadBack',ledge.cut(Part.makeCompound(holes)),'Battery compartment retaining ledge')
    for i,x in enumerate([-36,36]):
        m.cut('PadBatteryDoor',[Part.makeCylinder(.85,3,V(x,cy-8,9.7)),Part.makeCylinder(1.8,.8,V(x,cy-8,9.7))],'Battery cover fixing hole and head recess')
        m.screw('PadBatteryScrew'+str(i),(x,cy-8,9.9),'Controller',-5,length=2.5,radius=1.6)
    for i,(x,y) in enumerate([(-71,cy+45),(71,cy+45),(-69,cy-13),(67,cy-8)]):
        m.cut('PadMainPCB',Part.makeCylinder(1,1.4,V(x,y,25.8)),'GamePad mainboard fixing bore')
        m.screw('PadBoardScrew'+str(i),(x,y,24.9),'PadInternal',0,length=5.5,radius=1.7)
        boss=Part.makeCylinder(2.2,4.1,V(x,y,27.2)).cut(Part.makeCylinder(.85,4.5,V(x,y,27.0)))
        m.feature('PadBoardStandoff'+str(i),'Control-board mounting standoff',boss,'PadInternal',1,'wiiuwhite',True)
    # The original stylus is supplied beside the controller for easy inspection.
    m.cyl('StylusBarrel','WUP-015 stylus barrel',2.2,88,(180,cy-45,5),'Accessories',0,'wiiuwhite',axis=(0,1,0))
    tip=Part.makeCone(.45,2.2,9,V(180,cy-54,5),V(0,1,0));m.feature('StylusTip','Rounded stylus tip study',tip,'Accessories',0,'wiiuwhite')
    m.cyl('StylusCap','Stylus end cap',3,3,(180,cy+43.2,5),'Accessories',0,'wiiuwhite',axis=(0,1,0))
    m.profile['stages']=14
    m.checkpoint(14,'gamepad_fixing_columns_battery_retainer_and_stylus','补齐 GamePad 外壳和主板固定点、电池盖螺钉与内部承托边框，并加入独立 WUP-015 触控笔学习模型。')



def stage15(m):
    cy=-275
    # Separate the right speaker from SELECT and keep its opening aligned.
    for key in ['PadSpeaker1','PadSpeakerCone1','PadSpeakerMagnet1']:
        obj=m.parts[key];obj.Placement.Base+=V(8,6,0);obj.FlatPlacement=obj.Placement
    tools=[o for o in m.doc.Objects if o.TypeId=='Part::Feature' and o.Label.startswith('Front stereo speaker opening · tool') and o.Shape.BoundBox.Center.x>0]
    assert len(tools)==1
    tools[0].Shape=m.rr(4.2,2.0,5,(107,cy-44,37),.9)
    obj=m.parts['SpeakerOpening1'];obj.Shape=m.rr(3.8,1.6,.35,(107,cy-44,40.6),.7);obj.FlatPlacement=obj.Placement
    for side in [-1,1]:
        for prefix in ['PadShoulderPCB','PadShoulderSwitch']:
            obj=m.parts[prefix+str(side)];obj.Placement.Base+=V(0,4,0);obj.FlatPlacement=obj.Placement
    m.profile['stages']=15
    m.checkpoint(15,'speaker_select_and_shoulder_clearances','根据装配求交结果分开右扬声器与 SELECT 推杆，并同步调整扬声器开口；移开肩键小板，使其避让模拟摇杆电位器。')



def stage16(m):
    cy=-275
    for obj in m.doc.Objects:
        if obj.Name.startswith('LowerHousing') and 'Refine' in obj.PropertiesList:obj.Refine=False
    # Keep the lower pair of shell bosses clear of TV / POWER and the bottom board.
    changed=[]
    for obj in m.doc.Objects:
        if obj.TypeId=='Part::Feature' and obj.Label.startswith('Rear tri-point screw access · tool'):
            center=obj.Shape.BoundBox.Center
            if abs(center.y-(cy-53))<.1 and abs(abs(center.x)-75)<.1:
                sh=obj.Shape.copy();sh.translate(V(-15 if center.x>0 else 15,0,0));obj.Shape=sh;changed.append(obj.Name)
    assert len(changed)==2,changed
    for i,dx in [(4,15),(6,-15)]:
        obj=m.parts['PadCaseScrew'+str(i)];obj.Placement.Base+=V(dx,0,0);obj.FlatPlacement=obj.Placement
    points=[(x,cy+y) for x in [-113,113] for y in [-20,15]]+[(-60,cy-53),(-75,cy+53),(60,cy-53),(75,cy+53)]
    outer=m.doc.getObject('PadFrontOuter').Shape
    posts=[Part.makeCylinder(2.4,18,V(x,y,24)).common(outer).cut(Part.makeCylinder(.85,19,V(x,y,23.8))) for x,y in points]
    m.parts['PadFront'].Tool.Shape=Part.makeCompound(posts)
    m.cut('PadBottomPCB',Part.makeCylinder(2.7,2,V(60,cy-53,29.7)),'Lower shell column passage through button board')
    m.cut('PadCarrierABXY',Part.makeCylinder(2.7,5,V(113,cy-20,30.9)),'ABXY carrier clearance around case column')
    m.doc.recompute()
    for obj in m.parts.values():obj.Shape.check(True)
    m.profile['stages']=16
    m.checkpoint(16,'case_column_fit_and_native_surface_continuity','依据全装配求交移动下部螺柱并补齐按键板和支承框的通孔；保留壳体分段曲面以避免自动合并损坏曲线，并执行全部组件严格实体检查。')

STAGES=[stage01,stage02,stage03,stage04,stage05,stage06,stage07,stage08,stage09,stage10,stage11,stage12,stage13,stage14,stage15,stage16]
