"""Original white RVL-001 Wii: native shells and version-specific study internals.

The console is built in its supported horizontal orientation (X = 157 mm,
Y = 215.4 mm, Z = 44 mm). Local details are photographic approximations.
"""
import math
import FreeCAD as App
import Part
from .core import V
from . import geometry as g
from .retro_common import fuse_feature

FRONT=g.rotation((0,-1,0),(0,0,1))
REAR=g.rotation((0,1,0),(0,0,1))
SIDE=g.rotation((-1,0,0),(0,0,1))


def stage01(m):
    m.colors.update(wiiwhite=(.90,.91,.90),wiigrey=(.67,.68,.68),slotblue=(.12,.56,.92),cream=(.82,.81,.72))
    m.params.set('A3','Depth (Y)');m.params.set('A4','Thickness (Z)')
    m.native('LowerHousing','RVL-001 lower enclosure',157,210.4,.8,19.5,(0,2.5,1.5),'Body',-6,'wiiwhite',expr={'Width':'Parameters.Width','Height':'Parameters.Height - 5 mm'})
    m.cut('LowerHousing',m.rr(153.8,207.2,19,(0,2.5,3.1),.5),'Open lower shell with 1.6 mm study walls')
    m.native('UpperHousing','RVL-001 upper enclosure',157,210.4,.8,22.75,(0,2.5,21.25),'Body',6,'wiiwhite',expr={'Width':'Parameters.Width','Height':'Parameters.Height - 5 mm'})
    m.cut('UpperHousing',m.rr(153.8,207.2,21.4,(0,2.5,21.1),.5),'Open upper shell and separate top skin')
    bezel=g.rounded_body(m.doc,'FrontBezelBody','Separate original Wii faceplate',157,42.5,.8,4.75,(0,-102.95,22.75),orient=FRONT,color=m.colors['wiiwhite'])
    m.register(bezel,'FrontBezel','Body',5,'wiiwhite')
    m.cut('FrontBezel',m.rr(153.8,39.3,3.1,(0,-102.8,22.75),.5,FRONT),'Hollow faceplate with independent front skin')
    for i,(x,y) in enumerate([(-67,-87),(67,-87),(-67,89),(67,89)]):m.box('Foot'+str(i),'Horizontal placement rubber pad',8,15,1.5,(x,y,0),'Body',-6,'rubber',1.2)
    # The shell seam is kept as a real 0.25 mm clearance, not a painted stripe.
    m.profile['stages']=1
    m.checkpoint(1,'native_white_enclosure_and_separate_faceplate','建立初代白色 RVL-001 的原生草图、拉伸与圆角外壳，独立前面板及四个横放脚垫；按 157 × 215.4 × 44 mm 横放坐标建模。')


def stage02(m):
    opening=m.rr(131,7.4,6,(0,-102.5,33.4),3.65,FRONT)
    m.cut('FrontBezel',opening,'Rounded slot-loading optical-disc aperture')
    guide=m.rr(130.5,6.9,1.45,(0,-106.15,33.4),3.4,FRONT)
    guide=guide.cut(m.rr(127.4,4.0,2,(0,-106,33.4),1.98,FRONT))
    m.feature('DiscLightGuide','Blue optical slot illumination guide',guide,'Controls',5,'slotblue')
    frame=m.rr(128,4.6,2.8,(0,-103,33.4),2.2,FRONT).cut(m.rr(126.8,3.4,3.2,(0,-102.8,33.4),1.6,FRONT))
    m.feature('DiscSlotFrame','Dark internal disc-slot frame',frame,'Optical',4,'black',True)
    for i,x in enumerate([-68.7,68.7]):
        m.box('SlotLEDPCB'+str(i),'Slot indicator end board',4.5,15,.7,(x,-103.7,29),'Controls',4,'pcb',.4,True,orient=FRONT)
        m.box('SlotLED'+str(i),'Blue light source package',2.5,2.5,.6,(x,-104.5,33.4),'Controls',4,'slotblue',.3,True,orient=FRONT)
    for key,x,w in [('Power',-60.5,5.6),('Reset',-47.5,4.8),('Eject',62,5.6)]:
        m.cut('FrontBezel',m.rr(w+.7,10.7,5,(x,-103.5,11.5),.8,FRONT),key+' button aperture')
        m.box(key+'Button',key+' original faceplate key',w,10,1.7,(x,-106.2,11.5),'Controls',5,'wiiwhite',.6,orient=FRONT)
        m.box(key+'Switch',key+' tactile switch housing',4,5,1.5,(x,-103.2,11.5),'Controls',4,'black',.4,True,orient=FRONT)
        m.label(key+'Mark',{'Power':'P','Reset':'R','Eject':'E'}[key],2.7,(x-1.1,-107.94,10.4),'Controls',5,'wiigrey',rotation=FRONT)
    m.cyl('PowerIndicator','Green power-state lens',.8,.04,(-60.5,-107.96,7.7),'Controls',5,'led',axis=(0,-1,0))
    m.label('WiiFrontMark','Wii',6.8,(67,-107.74,21),'Body',5,'wiigrey',rotation=FRONT)
    m.cut('FrontBezel',m.rr(71,13.4,5.2,(0,-103,10.7),.7,FRONT),'Front SD and synchronization door recess')
    m.box('SDFlap','Removable front SD and SYNC cover',70.3,12.7,1.35,(0,-106.2,10.7),'Body',5,'wiiwhite',.6,orient=FRONT)
    for x in [-31,31]:m.cyl('SDHinge'+str(x),'SD door hinge journal',.7,3,(x,-105.2,4.6),'Controls',4,'wiiwhite',axis=(1,0,0))
    m.box('SDPortPCB','SD and synchronization support board',61,12,1,(-2,-94,7.5),'Ports',0,'pcb',.8,True)
    socket=m.rr(28,6,13,(5,-91,12),.6,FRONT).cut(m.rr(25,3.2,13.4,(5,-90.8,12.7),.4,FRONT))
    m.feature('SDPort','Nine-contact SD reader cage',socket,'Ports',0,'metal',True)
    m.cut('LowerHousing',m.rr(28.6,6.6,5,(5,-99.5,12),.6,FRONT),'SD reader passage through front return wall')
    m.box('SDInsulator','SD contact carrier',24,10,.5,(5,-96,11.3),'Ports',0,'black',.3,True)
    for i in range(9):m.box('SDContact'+str(i),'SD card spring contact',.8,7,.13,(5+(i-4)*2.5,-95,11.85),'Ports',0,'gold',.08,True)
    m.box('SyncSwitch','Pairing button switch',5,6,3,(-26,-96,8.55),'Controls',0,'black',.6,True)
    m.box('SyncButton','Red synchronization button',6,5,1.2,(-26,-104,11.4),'Controls',4,'red',.5,orient=FRONT)
    m.profile['stages']=2
    m.checkpoint(2,'blue_disc_slot_controls_sd_and_sync','加入真实贯穿的吸入式光盘槽、蓝色导光件、独立电源与重置/退盘键、前门、九接点 SD 卡座及红色同步键。')



def _front_symbols(m):
    ring=Part.makeCylinder(1.65,.035).cut(Part.makeCylinder(1.25,.07,V(0,0,-.01)))
    ring=ring.cut(Part.makeBox(1.15,2,.1,V(-.575,.7,-.02)))
    power=ring.fuse(Part.makeBox(.32,2,.035,V(-.16,.3,0)))
    power.Placement=App.Placement(V(-60.5,-107.94,12.4),FRONT)
    m.parts['PowerMark'].Shape=power;m.parts['PowerMark'].FlatPlacement=m.parts['PowerMark'].Placement;m.parts['PowerMark'].Label='Power symbol'
    tri=Part.Face(Part.makePolygon([V(-1.5,-.2),V(1.5,-.2),V(0,1.7),V(-1.5,-.2)])).extrude(V(0,0,.035))
    eject=Part.makeCompound([tri,Part.makeBox(3,.4,.035,V(-1.5,-1,0))]);eject.Placement=App.Placement(V(62,-107.94,12.2),FRONT)
    m.parts['EjectMark'].Shape=eject;m.parts['EjectMark'].FlatPlacement=m.parts['EjectMark'].Placement;m.parts['EjectMark'].Label='Eject symbol'
    old=m.parts.pop('ResetMark');old.PhysicalPart=False;old.Visibility=False
    vertical=FRONT.multiply(App.Rotation(V(0,0,1),90))
    for key,x in [('Power',-55.7),('Reset',-43.3),('Eject',58.0)]:m.label(key+'Label',key.upper(),1.5,(x,-107.74,7.6),'Controls',5,'wiigrey',rotation=vertical)


def _rear_opening(m,shape,reason):
    for key in ['LowerHousing','UpperHousing']:m.cut(key,shape,reason)


def stage03(m):
    _front_symbols(m)
    # Rear USB receptacles follow the original console's paired sockets across its thickness.
    for i,z in enumerate([13,30]):
        x=-57
        opening=m.rr(15.3,7.1,8,(x,102,z),.6,REAR);_rear_opening(m,opening,'USB-A '+str(i+1)+' rear opening')
        cage=m.rr(14.7,6.5,13,(x,94.3,z),.5,REAR).cut(m.rr(13.3,5.1,13.4,(x,94.1,z),.3,REAR))
        m.feature('USB'+str(i)+'Shell','USB-A receptacle shield',cage,'Ports',0,'metal',True)
        m.box('USB'+str(i)+'Tongue','USB-A insulating tongue',11.5,9,1.35,(x,100.9,z-1.9),'Ports',0,'black',.3,True)
        for j in range(4):m.box('USB'+str(i)+'Contact'+str(j),'USB-A spring contact',.7,7,.12,(x+(j-1.5)*2.5,101.2,z-.49),'Ports',0,'gold',.07,True)
    # Original Multi AV connector: two banks of eight positions.
    opening=m.rr(24,11,8,(35,102,13.2),1.1,REAR);_rear_opening(m,opening,'Sixteen-position Multi AV rear opening')
    housing=m.rr(23.4,10.4,13,(35,94.3,13.2),.9,REAR).cut(m.rr(20.6,7.6,13.4,(35,94.1,13.2),.5,REAR))
    m.feature('AVShell','Multi AV insulated rear housing',housing,'Ports',0,'wiigrey',True)
    m.box('AVTongue','Multi AV contact tongue',19.3,9,1.35,(35,100.5,12.2),'Ports',0,'black',.3,True)
    for row in range(2):
        for i in range(8):m.box('AVContact'+str(row)+'_'+str(i),'Multi AV contact',.55,7,.12,(35+(i-3.5)*2.35,100.9,12.03 if row==0 else 13.6),'Ports',0,'gold',.06,True)
    for key,x,w,h,zz,material in [('Sensor',35,9,6,32,'red'),('DC',61,15,11,22,'cream')]:
        opening=m.rr(w+.7,h+.7,9,(x,101.7,zz),.7,REAR);_rear_opening(m,opening,key+' rear opening')
        socket=m.rr(w,h,12.4,(x,94.8,zz),.6,REAR).cut(m.rr(w-2.5,h-2.5,10,(x,98.2,zz),.4,REAR))
        m.feature(key+'Socket',key+' keyed two-contact socket',socket,'Ports',0,material,True)
        for i,dx in enumerate([-w/5,w/5]):m.box(key+'Pin'+str(i),key+' connector pin',.8,6,.6,(x+dx,102.8,zz-.2),'Ports',0,'gold',.1,True)
    # Rear exhaust sits above the lower connector bank in the horizontal pose.
    slots=[m.rr(2.5,33,6,(x,103.5,22.5),.7,REAR) for x in range(-31,15,5)]
    _rear_opening(m,Part.makeCompound(slots),'Rear parallel exhaust grille')
    for x in range(-70,73,7):m.cut('LowerHousing',Part.makeBox(2.4,3.8,8,V(x,102.6,2.5)),'Lower rear intake slot')
    m.label('RearDCMark','12V',1.9,(59,107.74,31),'Body',6,'wiigrey',rotation=REAR)
    m.profile['stages']=3
    m.checkpoint(3,'rear_usb_multi_av_sensor_and_power','补齐双 USB、十六位 Multi AV、感应条和直流电源接口的独立触点及背部排气格栅，同时细化前面板电源/退盘符号。')


def _side_opening(m,shape,reason):
    for key in ['LowerHousing','UpperHousing']:m.cut(key,shape,reason)


def stage04(m):
    # On the original RVL-001 the left side in horizontal pose holds GameCube I/O.
    for key,cy,depth in [('GameCube',-33,125),('Memory',66,63)]:
        cut=m.rr(depth,32,7,(-73,cy,24),1.1,SIDE);_side_opening(m,cut,key+' removable side door')
        m.box(key+'Door',key+' white side cover',depth-.6,31.4,1.35,(-77,cy,24),'Body',6,'wiiwhite',.8,orient=SIDE)
        # The cover is a separate part; exact hinge dimensions are study values.
        for i,y in enumerate([cy-depth/2+5,cy+depth/2-5]):m.cyl(key+'Hinge'+str(i),'Side cover hinge journal',.65,3,(-75.7,y,39.5),'Controls',6,'wiiwhite',axis=(0,1,0))
    for i,y in enumerate([-79,-49,-19,11],1):
        rim=Part.makeCylinder(8.0,2,V(-74.6,y,21),V(-1,0,0))
        cup=Part.makeCylinder(7.4,13,V(-61.3,y,21),V(-1,0,0)).fuse(rim)
        cup=cup.cut(Part.makeCylinder(6.1,13,V(-65,y,21),V(-1,0,0)))
        m.feature('GCPort'+str(i),'GameCube controller socket '+str(i),cup,'GameCube',0,'black',True)
        shield=m.rr(17,17,10.5,(-59,y,21),.6,SIDE).cut(m.rr(15.8,15.8,11,(-58.8,y,21),.35,SIDE))
        m.feature('GCShield'+str(i),'Controller connector metal shield',shield,'GameCube',0,'metal',True)
        carrier=Part.makeCylinder(5.7,2,V(-65,y,21),V(-1,0,0));holes=[]
        for row in range(2):
            for j in range(3):
                yy=y+(j-1)*3;zz=21+(row-.5)*3
                holes.append(Part.makeCylinder(.63,2.4,V(-64.8,yy,zz),V(-1,0,0)))
                m.cyl('GCPin'+str(i)+'_'+str(row)+'_'+str(j),'GameCube six-position pin',.45,8,(-65.1,yy,zz),'GameCube',0,'gold',axis=(-1,0,0),internal=True)
        m.feature('GCInsert'+str(i),'Six-pin insulating carrier',carrier.cut(Part.makeCompound(holes)),'GameCube',0,'black',True)
    for i,z in enumerate([14,29],1):
        y=66
        socket=m.rr(25,8,18,(-56.7,y,z),.6,SIDE).cut(m.rr(22.4,5.2,18.4,(-56.5,y,z),.3,SIDE))
        m.feature('GCMemory'+str(i),'GameCube memory-card socket '+str(i),socket,'GameCube',0,'metal',True)
        m.box('GCMemoryCarrier'+str(i),'Memory-card contact carrier',15,21,1.0,(-66,y,z-2.3),'GameCube',0,'black',.3,True)
        for j in range(12):m.box('GCMemoryPin'+str(i)+'_'+str(j),'Memory-card twelve-position contact',11,.65,.12,(-67,y+(j-5.5)*1.65,z-1.23),'GameCube',0,'gold',.07,True)
    # Right-side intake. Individual rectangular holes remain editable cut history.
    slots=[Part.makeBox(6,2.2,22,V(75,y,10)) for y in range(-82,87,6)]
    _side_opening(m,Part.makeCompound(slots),'Opposite-side intake ventilation')
    m.profile['stages']=4
    m.checkpoint(4,'gamecube_four_ports_two_cards_and_side_doors','加入初代特有的四个六接点 GameCube 手柄接口、两个十二接点存储卡槽及独立侧盖，补齐相对侧的进气孔。')



def _package(m,key,title,x,y,w,h,capw,caph):
    m.box(key+'Substrate',title+' package substrate',w,h,.9,(x,y,7.72),'Mainboard',0,'pcb',.35,True)
    m.box(key,title+' metallic package cover',capw,caph,1.35,(x,y,8.68),'Mainboard',0,'metal',.5,True)
    balls=[Part.makeSphere(.22,V(x+dx,y+dy,7.45)) for dx in [-w*.34,-w*.17,0,w*.17,w*.34] for dy in [-h*.34,-h*.17,0,h*.17,h*.34]]
    m.feature(key+'Interconnect','Schematic package interconnect field',Part.makeCompound(balls),'Mainboard',0,'metal',True)
    m.label(key+'Mark',title,min(1.4,capw/(len(title)*.8)),(x-capw/2+1,y-.6,10.05),'Mainboard',0,'black')


def _sop(m,key,title,x,y,w,h,pins):
    m.box(key,title+' package',w,h,1.35,(x,y,7.7),'Mainboard',0,'black',.3,True)
    m.label(key+'Mark',title,min(1.3,w/(len(title)*.8)),(x-w/2+.6,y-.5,9.07),'Mainboard',0,'wiigrey')
    for side in [-1,1]:
        fingers=[Part.makeBox(.23,1.6,.15,V(x+(i-(pins/2-1)/2)*(w-1.1)/(pins/2-1)-.115,y+side*(h/2+.85)-.8,7.42)) for i in range(pins//2)]
        m.feature(key+'Leads'+str(side),'Package contact bank',Part.makeCompound(fingers),'Mainboard',0,'metal',True)


def stage05(m):
    # Body and interfaces follow RVL-001; local board geometry is a study layout.
    m.box('MainPCB','Wii motherboard with separate module interfaces',144,186,1.2,(0,4,6),'Mainboard',0,'pcb',1.5,True)
    holes=[Part.makeCylinder(1.3,1.5,V(x,y,5.85)) for x,y in [(-65,-79),(65,-79),(-65,29),(55,37),(-35,89),(44,89),(12,-72)]]
    m.cut('MainPCB',holes,'Motherboard mechanical mounting bores')
    # Exposed peripheral ground strips remain above the board surface.
    for side in [-1,1]:
        strip=m.rr(3.2,174,.03,(side*69.2,4,7.23),.2)
        m.feature('GroundStrip'+str(side),'Peripheral grounding strip',strip,'Mainboard',0,'gold',True)
    _package(m,'Hollywood','HOLLYWOOD',-7,66,33,33,28,28)
    _package(m,'Broadway','BROADWAY',31,66,20,20,16,16)
    _sop(m,'NAND','NAND',25,-48,17,10.5,48)
    _sop(m,'AVEncoder','AV ENCODER',55,61,10,8,32)
    m.box('MEM2','External memory study package',12,15,1.3,(-13,30,7.65),'Mainboard',0,'black',.3,True)
    m.label('MEM2Mark','MEM2',1.7,(-17,29,8.98),'Mainboard',0,'wiigrey')
    for i,(x,y) in enumerate([(53,26),(53,10),(53,-6)]):
        m.box('Regulator'+str(i),'Switching regulator study package',6.2,6.2,1.25,(x,y,7.7),'Mainboard',0,'black',.4,True)
        m.box('Inductor'+str(i),'Power conversion inductor',7,7,3.6,(x+9,y,7.65),'Mainboard',0,'thermal',1.0,True)
        m.cyl('Cap'+str(i),'Power smoothing capacitor',2.9,6.1,(x-8,y,7.65),'Mainboard',0,'metal',internal=True)
        m.cyl('CapTop'+str(i),'Electrolytic capacitor insulating top',2.6,.07,(x-8,y,13.8),'Mainboard',0,'black',internal=True)
    for i,x in enumerate([-28,-17,-6,5,16,27]):
        m.cyl('RearCap'+str(i),'Rear-side smoothing capacitor',2.6,5.4,(x,90,7.65),'Mainboard',0,'metal',internal=True)
        m.cyl('RearCapTop'+str(i),'Capacitor top vent mark',2.2,.06,(x,90,13.08),'Mainboard',0,'black',internal=True)
    # Distinct study banks leave socket, fixing and drive clearances visible.
    for bank,(bx,by,nx,ny) in enumerate([(-29,-66,9,3),(-30,-34,8,3),(-28,-4,8,3),(11,1,6,3),(27,-72,6,2)]):
        for ix in range(nx):
            for iy in range(ny):
                x=bx+ix*3.7;y=by+iy*3.9;key=f'SMD{bank}_{ix}_{iy}'
                m.box(key,'Study passive component',1.5,.8,.5,(x,y,7.42),'Mainboard',0,'cream' if (ix+iy)%3 else 'black',.1,True)
    for key,x,y,w,h in [('DriveData',-21,-55,20,5),('DrivePower',38,-64,12,6),('BluetoothSocket',-35,-83,18,4),('WifiSocket',-36,19,19,4)]:
        m.box(key,key+' connector housing',w,h,2.3,(x,y,7.65),'Mainboard',0,'cream',.4,True)
        m.box(key+'Latch',key+' retaining flap',w-1,h*.4,.55,(x,y,10.01),'Mainboard',0,'black',.2,True)
    m.label('PCBMark','RVL-001 STUDY',2.2,(11,-28,7.24),'Mainboard',0,'white')
    m.profile['stages']=5
    m.checkpoint(5,'mainboard_broadway_hollywood_memory_and_power','加入主板、Broadway/Hollywood 封装、存储器、视频编码和分区电源器件，保留光驱与无线模块连接器；内部布置及互连数量明确作为学习近似。')



def stage06(m):
    # Shared finned sink, rear axial fan and two independently removable radios.
    for key,x,w in [('Hollywood',-7,28),('Broadway',31,16)]:m.box(key+'ThermalPad','Processor thermal interface study',w,w,.55,(x,66,10.12),'Cooling',1,'thermal',.5,True)
    base=m.rr(69,41,1.4,(9.5,66,10.85),1.2)
    fins=[Part.makeBox(.65,40.4,14,V(-23+i*3.8,45.8,12.2)) for i in range(18)]
    sink=base.multiFuse(fins).removeSplitter()
    bores=[Part.makeCylinder(1.4,18,V(x,y,10.5)) for x in [-22,41] for y in [48,84]]
    m.feature('Heatsink','Common finned processor heatsink',sink.cut(Part.makeCompound(bores)),'Cooling',2,'metal',True)
    frame=m.rr(38,38,8.5,(-9,96,22.5),2.2,REAR).cut(Part.makeCylinder(17.2,9,V(-9,95.8,22.5),V(0,1,0)))
    screwbores=[Part.makeCylinder(1.15,9,V(-9+dx,95.8,22.5+dz),V(0,1,0)) for dx in [-15.5,15.5] for dz in [-15.5,15.5]]
    m.feature('FanFrame','Rear axial fan frame',frame.cut(Part.makeCompound(screwbores)),'Cooling',1,'black',True)
    hub=Part.makeCylinder(6.2,6,V(-9,97,22.5),V(0,1,0));blades=[]
    for i in range(7):
        a=2*math.pi*i/7
        points=[V(-9+r*math.cos(a+t),99,22.5+r*math.sin(a+t)) for r,t in [(5.6,-.24),(16.3,-.08),(16.3,.21),(5.6,.25)]]
        blades.append(Part.Face(Part.makePolygon(points+[points[0]])).extrude(V(0,1.4,0)))
    m.feature('FanRotor','Seven-blade axial rotor',hub.multiFuse(blades).removeSplitter(),'Cooling',1,'black',True)
    m.cyl('FanMotorPCB','Fan motor support disc',6.5,.65,(-9,95.5,22.5),'Cooling',1,'pcb',axis=(0,1,0),internal=True)
    for i in range(4):
        arm=Part.makeBox(10.3,.4,1,V(-2.4,96.7,22));arm.rotate(V(-9,96.7,22.5),V(0,1,0),90*i)
        m.feature('FanStrut'+str(i),'Motor support strut',arm,'Cooling',1,'black',True)
    m.box('WifiPCB','Removable Wi-Fi board',25,31.5,.8,(-43,19,10.75),'Wireless',1,'pcb',.7,True)
    m.box('WifiIC','Radio chipset study package',8,8,1.3,(-43,16,11.7),'Wireless',1,'black',.3,True)
    rf=m.rr(22,21,3.2,(-43,16,11.65),.6).cut(m.rr(20.8,19.8,2.8,(-43,16,11.6),.4))
    m.feature('WifiShield','Wi-Fi radio shield can',rf,'Wireless',2,'metal',True)
    for i,x in enumerate([-50,-36]):
        m.ring('WifiCoax'+str(i),'Wi-Fi miniature coax socket',1.5,.8,.8,(x,30,11.6),'Wireless',1,'gold',internal=True)
    m.box('BluetoothPCB','Removable Bluetooth module',27,19,.8,(-38,-79,11.1),'Wireless',1,'pcb',.7,True)
    m.box('BluetoothIC','Bluetooth chipset study package',6,7,1.2,(-35,-77,12.03),'Wireless',1,'black',.3,True)
    bt=m.rr(12,12,2.7,(-35,-77,12),.6).cut(m.rr(10.8,10.8,2.35,(-35,-77,11.95),.4))
    m.feature('BluetoothShield','Bluetooth module shield can',bt,'Wireless',2,'metal',True)
    traces=[m.rr(.5,10,.035,(-48+i*1.5,-79,11.95),.1) for i in range(4)]
    m.feature('BluetoothAntenna','Printed antenna study traces',Part.makeCompound(traces),'Wireless',1,'gold',True)
    # Move the faceplate lettering within the actual enclosure width.
    word=m.parts['WiiFrontMark'];word.Placement.Base=word.Placement.Base+V(-2,0,0);word.FlatPlacement=word.Placement
    m.profile['stages']=6
    m.checkpoint(6,'finned_heatsink_rear_fan_and_wireless_modules','加入共用铝制鳍片散热器、七叶后排风扇、独立 Wi-Fi 与蓝牙模块及屏蔽罩，留出后部接口与光驱的装配空间。')



def _gear(m,key,x,y,z,root,outer,teeth):
    from .ps1 import _gear as tooth_outline
    shape=tooth_outline(m,x,y,z,root,outer,1.1,teeth).cut(Part.makeCylinder(1,1.4,V(x,y,z-.1)))
    return m.feature(key,'Disc transport study gear',shape,'Optical',3,'cream',True)


def stage07(m):
    base=m.rr(130,134,.7,(7,-31,24.2),1.5)
    bores=[Part.makeCylinder(1.35,1,V(x,y,24.05)) for x in [-52,66] for y in [-92,30]]
    m.feature('DriveBase','Stamped optical-drive base',base.cut(Part.makeCompound(bores)),'Optical',2,'metal',True)
    surround=m.rr(130,134,11.7,(7,-31,24.95),1.5).cut(m.rr(127.6,131.6,12,(7,-31,24.8),.8))
    surround=surround.cut(m.rr(127,5.4,5,(7,-95.5,33.4),2,FRONT))
    m.feature('DriveFrame','Optical mechanism side frame',surround,'Optical',3,'black',True)
    m.cyl('SpindleMotor','Disc spindle motor',10.6,6.2,(7,-31,25.05),'Optical',2,'metal',internal=True)
    m.cyl('SpindleShaft','Spindle drive shaft',2.2,2.05,(7,-31,31.35),'Optical',3,'metal',internal=True)
    m.ring('Turntable','Disc centering turntable',13,2.35,1.4,(7,-31,33.55),'Optical',3,'black',internal=True)
    m.cyl('TurntablePilot','Disc center pilot',7.2,1.7,(7,-31,35),'Optical',3,'black',internal=True)
    # Twin guide rails and an independently bored pickup carriage.
    for i,x in enumerate([-7,17]):m.cyl('PickupRail'+str(i),'Optical pickup linear guide',.7,42,(x,-83,29.2),'Optical',3,'metal',axis=(0,1,0),internal=True)
    pickup=m.rr(29,16,4,(5,-65,27.1),1.2)
    holes=[Part.makeCylinder(.9,17,V(x,-73.5,29.2),V(0,1,0)) for x in [-7,17]]
    m.feature('PickupCarriage','Optical pickup carriage with guide bores',pickup.cut(Part.makeCompound(holes)),'Optical',3,'black',True)
    m.box('PickupPCB','Pickup sensor board',18,12,.65,(5,-65,31.2),'Optical',3,'pcb',.6,True)
    m.ring('LensHolder','Objective lens support',4.4,3.0,1.2,(5,-64,31.95),'Optical',3,'black',internal=True)
    m.cyl('PickupLens','Blue optical objective',2.8,.6,(5,-64,32.25),'Optical',3,'blue',internal=True)
    m.cyl('SledScrew','Pickup lead-screw shaft',.9,40,(24,-82,29.2),'Optical',3,'metal',axis=(0,1,0),internal=True)
    from .atari2600 import _helical_spring
    helix=_helical_spring(1.2,2,38,.2)
    helix.Placement=App.Placement(V(24,-81,29.2),App.Rotation(V(0,0,1),V(0,1,0)))
    m.feature('SledThread','Helical pickup-feed thread',helix,'Optical',3,'metal',True)
    nut=m.rr(5.4,5.3,4.6,(24,-65,26.9),.5).cut(Part.makeCylinder(1.5,6,V(24,-68,29.2),V(0,1,0)))
    m.feature('SledNut','Clearance nut for optical carriage',nut,'Optical',3,'cream',True)
    m.cyl('SledMotor','Pickup transport motor',3.4,8,(24,-40.8,29.2),'Optical',3,'metal',axis=(0,1,0),internal=True)
    # Slot-loading rollers accommodate a disc without a sliding drawer.
    m.cyl('LoadShaft','Slot transport common axle',.85,120,(-54,-92.5,32.5),'Optical',3,'metal',axis=(1,0,0),internal=True)
    for i,x in enumerate([-49,16]):m.ring('LoadRoller'+str(i),'Rubber disc-loading roller',2.6,1.05,41,(x,-92.5,32.5),'Optical',3,'rubber',axis=(1,0,0),internal=True)
    for i,x in enumerate([-55.5,65]):m.ring('LoadBearing'+str(i),'Roller axle support',2,1.05,1.3,(x,-92.5,32.5),'Optical',3,'cream',axis=(1,0,0),internal=True)
    for i,(y,root,outer,teeth) in enumerate([(-83,3.25,4,14),(-71,6.1,7,24),(-58,4.2,5,18),(-47,3.2,4,14)]):
        _gear(m,'LoadGear'+str(i),61,y,29.9,root,outer,teeth)
        m.cyl('LoadGearAxle'+str(i),'Transport gear shaft',.75,3.6,(61,y,27.8),'Optical',3,'metal',internal=True)
    m.cyl('LoadingMotor','Disc-loading motor',3.8,4.5,(61,-47,25.1),'Optical',2,'metal',internal=True)
    # Opposed disc-detection / guiding arms are distinct articulated study pieces.
    for i,side in enumerate([-1,1]):
        x=7+side*46;y=-52
        arm=Part.makeBox(3.2,40,1.2,V(x-1.6,y-20,34.1)).fuse(Part.makeCylinder(3.8,1.2,V(x,y+20,34.1)))
        arm=arm.cut(Part.makeCylinder(1.1,1.5,V(x,y+20,34.0)))
        m.feature('DiscGuideArm'+str(i),'Disc-size guide lever',arm,'Optical',4,'cream',True)
        m.cyl('GuidePivot'+str(i),'Guide lever pivot',.8,2.5,(x,y+20,33.6),'Optical',3,'metal',internal=True)
        m.cyl('GuideWheel'+str(i),'Disc edge guide wheel',3.1,1.6,(x,y-17,35.45),'Optical',4,'cream',internal=True)
    top=m.rr(130,134,.6,(7,-31,38.65),1.5)
    openings=[Part.makeCylinder(18,.9,V(7,-31,38.5)),m.rr(13,44,.9,(-42,-58,38.5),4),m.rr(13,44,.9,(48,-58,38.5),4),Part.makeCylinder(11,.9,V(-34,8,38.5)),Part.makeCylinder(11,.9,V(48,8,38.5))]
    m.feature('DriveTopShield','Perforated optical-drive upper plate',top.cut(Part.makeCompound(openings)),'Optical',5,'metal',True)
    m.cyl('DiscClamp','Upper magnetic disc clamp',11.5,.8,(7,-31,37.55),'Optical',4,'black',internal=True)
    bridge=m.rr(43,7,.7,(7,-31,39.4),1.1).cut(Part.makeCylinder(2.1,.9,V(7,-31,39.3)))
    m.feature('ClampBridge','Clamp retaining bridge',bridge,'Optical',5,'metal',True)
    m.cyl('ClampPin','Clamp retaining pin',1.8,2.3,(7,-31,38.4),'Optical',5,'metal',internal=True)
    m.box('DrivePCB','Optical drive control board',48,36,.8,(6,-49,21.6),'Optical',1,'pcb',1.0,True)
    m.box('DriveController','Drive controller package',13,13,1.2,(6,-49,22.5),'Optical',1,'black',.4,True)
    m.profile['stages']=7
    m.checkpoint(7,'slot_loading_drive_pickup_gears_and_clamp','建立吸入式光驱的底架、双滚轮、齿轮、主轴与压盘件，并加入双导轨光头、螺旋进给丝杆和独立光驱控制板。')



def stage08(m):
    # Clearances follow the measured assembly check, and retain native cut history.
    m.cut('MainPCB',m.rr(41,9,1.6,(-9,98.9,5.8),.8),'Rear fan frame and support clearance')
    for key,obj in m.parts.items():
        if key.startswith('Wifi'):
            obj.Placement.Base=obj.Placement.Base+V(0,-15,0);obj.FlatPlacement=obj.Placement
    for key in ['Regulator0','Inductor0','Cap0','CapTop0']:
        obj=m.parts[key];obj.Placement.Base=obj.Placement.Base+V(0,-4,0);obj.FlatPlacement=obj.Placement
    m.cut('LoadingMotor',Part.makeCylinder(.9,5,V(61,-47,25)),'Output shaft bore in disc-loading motor')
    # Formed shield layers, with actual apertures around taller assemblies.
    pcb_points=[(-65,-79),(65,-79),(-65,29),(55,37),(-35,89),(44,89),(12,-72)]
    drive_points=[(x,y) for x in [-52,66] for y in [-92,30]]
    case_points=[(x,y) for x in [-74,74] for y in [-97,100]]
    lower=m.rr(146,190,.45,(0,3,4),1.1)
    clearance=[m.rr(41,10,.8,(-9,99,3.8),.7)]+[Part.makeCylinder(2.8,1,V(x,y,3.8)) for x,y in pcb_points+drive_points+case_points]
    m.feature('LowerShield','Lower stamped electromagnetic shield',lower.cut(Part.makeCompound(clearance)),'Shield',-4,'metal',True)
    top=m.rr(143,174,.4,(0,2,18),1.0)
    openings=[m.rr(72,44,1,(9.5,66,17.8),1.2),m.rr(24,132,1,(-66,-33,17.8),1),m.rr(27,65,1,(-66,66,17.8),1)]
    openings += [Part.makeCylinder(3,1,V(x,y,17.8)) for x,y in drive_points]
    m.feature('MainShield','Mainboard upper shield with drive and cooler apertures',top.cut(Part.makeCompound(openings)),'Shield',1,'metal',True)
    board_posts=[]
    for i,(x,y) in enumerate(pcb_points):
        post=Part.makeCylinder(2.5,2.8,V(x,y,3.05)).cut(Part.makeCylinder(.85,3.1,V(x,y,2.95)))
        board_posts.append(post);m.screw('PCBMount'+str(i),(x,y,7.65),'Internal',0,length=3,radius=1.8,axis=(0,0,-1))
    # Drive standoffs pass through cleared motherboard/ground-strip holes.
    for key in ['MainPCB','GroundStrip1','GroundStrip-1']:
        m.cut(key,[Part.makeCylinder(2.9,2,V(x,y,5.7)) for x,y in drive_points],'Optical drive pillar clearance')
    for i,(x,y) in enumerate(drive_points):
        post=Part.makeCylinder(2.6,21,V(x,y,3.05)).cut(Part.makeCylinder(.85,22,V(x,y,2.9)))
        board_posts.append(post);m.screw('DriveMount'+str(i),(x,y,25.3),'Internal',2,length=4,radius=2,axis=(0,0,-1))
    fuse_feature(m,'LowerHousing',Part.makeCompound(board_posts),'Integrated board and optical-drive support pillars')
    upper_posts=[]
    for i,(x,y) in enumerate(case_points):
        post=Part.makeCylinder(2.1,38.2,V(x,y,4.4)).cut(Part.makeCylinder(.85,39,V(x,y,4.2)))
        upper_posts.append(post)
        m.cut('LowerHousing',[Part.makeCylinder(.95,9,V(x,y,1.3)),Part.makeCylinder(2.2,.7,V(x,y,1.3))],'Case fixing shaft passage and recessed head')
        m.screw('CaseMount'+str(i),(x,y,1.65),'Internal',-6,length=7,radius=2)
    fuse_feature(m,'UpperHousing',Part.makeCompound(upper_posts),'Four integrated upper-cover screw columns')
    m.profile['stages']=8
    m.checkpoint(8,'layered_shields_fixings_and_fan_clearances','补齐上下屏蔽板、主板与光驱支柱和机壳螺钉；通过主板后缘缺口及无线板位置调整消除风扇与支柱干涉。')



def _cross_shape(cx,cy,z,span=15.2,stem=4.8,height=3.2):
    return Part.makeBox(span,stem,height,V(cx-span/2,cy-stem/2,z)).fuse(Part.makeBox(stem,span,height,V(cx-stem/2,cy-span/2,z))).removeSplitter()


def stage09(m):
    from .retro_common import loft_shell
    cx,cy=-25,-235
    loft_shell(m,'RemoteBack','Original RVL-003 curved rear shell',[(29,139,7,cx,cy,1),(34,145,6,cx,cy,4.5),(36.2,148,3,cx,cy,14.8)],[(26,135,6,cx,cy,2.7),(31,141,5,cx,cy,5.2),(33.1,144.8,2,cx,cy,15.1)],'Controller',-4,'wiiwhite')
    m.native('RemoteFront','Original RVL-003 front shell',36.2,148,3,14.5,(cx,cy,15.05),'Controller',4,'wiiwhite')
    m.cut('RemoteFront',m.rr(33.2,144.8,13.1,(cx,cy,14.9),1.8),'Remote upper-shell cavity')
    m.cut('RemoteFront',m.rr(30.5,11.3,6,(cx,cy+70,22.3),2,REAR),'Infrared pointing-camera window')
    m.box('RemoteIRWindow','Dark infrared-transmissive nose window',29.9,10.7,1.0,(cx,cy+72.9,22.3),'Controller',4,'black',1.7,orient=REAR)
    m.cut('RemoteFront',_cross_shape(cx,cy+41,26.8,16,5.5,4),'Cross-shaped directional-pad aperture')
    m.feature('RemoteDPad','White directional cross',_cross_shape(cx,cy+41,27.2),'Controller',4,'wiiwhite')
    keys=[('Power',cx-10.5,cy+60.5,2.5,'',2.0),('A',cx,cy+18,6.1,'A',3.2),('Minus',cx-10.5,cy-4,2.8,'-',2.7),('Home',cx,cy-4,2.8,'',2.7),('Plus',cx+10.5,cy-4,2.8,'+',2.7),('One',cx,cy-43,3.3,'1',2.7),('Two',cx,cy-56,3.3,'2',2.7)]
    for key,x,y,r,mark,h in keys:
        m.cut('RemoteFront',Part.makeCylinder(r+.3,4,V(x,y,26.5)),key+' key aperture')
        m.cyl('Remote'+key,'Original Remote '+key+' key',r,h,(x,y,27.5),'Controller',4,'wiiwhite')
        if mark:m.label('Remote'+key+'Mark',mark,3.4 if key=='A' else 2.2,(x-1.1,y-1.2,27.5+h+.04),'Controller',4,'wiigrey')
    ring=Part.makeCylinder(1.6,.03).cut(Part.makeCylinder(1.22,.06,V(0,0,-.01)))
    symbol=ring.cut(Part.makeBox(1.1,2,.1,V(-.55,.7,-.02))).fuse(Part.makeBox(.32,1.8,.03,V(-.16,.4,0)))
    symbol.translate(V(cx-10.5,cy+60.5,29.54));m.feature('RemotePowerSymbol','Red power symbol',symbol,'Controller',4,'red')
    house=[(-1.7,0),(0,1.6),(1.7,0),(1.2,0),(1.2,-1.2),(-1.2,-1.2),(-1.2,0)]
    shape=Part.Face(Part.makePolygon([V(x,y) for x,y in house+[house[0]]])).extrude(V(0,0,.03));shape.translate(V(cx,cy-4,30.24))
    m.feature('RemoteHomeSymbol','Blue HOME symbol',shape,'Controller',4,'slotblue')
    holes=[Part.makeCylinder(.55,3,V(cx+(i-(n-1)/2)*2.2,cy-16-row*2.4,27)) for row,n in enumerate([3,5,5,5,3]) for i in range(n)]
    m.cut('RemoteFront',holes,'Remote loudspeaker grille')
    for i,x in enumerate([cx-9,cx-3,cx+3,cx+9],1):
        m.cut('RemoteFront',m.rr(2.1,1.9,3,(x,cy-66,27),.3),'Player indicator light-pipe aperture')
        m.box('RemoteLED'+str(i),'Player indicator lens '+str(i),1.7,1.5,1.3,(x,cy-66,28.35),'Controller',4,'slotblue',.25)
        m.label('RemoteLEDMark'+str(i),str(i),1.4,(x-.4,cy-70,29.59),'Controller',4,'wiigrey')
    m.cut('RemoteBack',m.rr(27,72,4,(cx,cy-26,0),3),'Removable rear battery-door opening')
    m.box('RemoteBatteryDoor','Rear two-AA battery cover',26.2,71.2,1.2,(cx,cy-26,1.1),'Controller',-4,'wiiwhite',2.8)
    m.cut('RemoteBack',m.rr(15,23,8,(cx,cy+31,-.3),5.5),'Rear B-trigger aperture')
    m.box('RemoteB','Rear B trigger',14.3,22.3,4.2,(cx,cy+31,.4),'Controller',-4,'wiiwhite',5.2)
    for key in ['RemoteFront','RemoteBack']:m.cut(key,m.rr(18.8,8.4,8,(cx,cy-68,17),.8,FRONT),'Six-contact expansion connector opening')
    housing=m.rr(18.2,7.8,5.7,(cx,cy-68,17),.7,FRONT).cut(m.rr(15.6,5.2,6.1,(cx,cy-67.8,17),.4,FRONT))
    m.feature('RemoteExtension','Six-contact expansion connector housing',housing,'Controller',0,'wiigrey',True)
    m.box('RemoteExtensionTongue','Expansion connector tongue',14,4,.8,(cx,cy-70.5,16),'Controller',0,'black',.3,True)
    for i in range(6):m.box('RemoteExtensionPin'+str(i),'Expansion connector contact',.65,3,.10,(cx+(i-2.5)*2.2,cy-70.5,16.86),'Controller',0,'gold',.06,True)
    m.profile['stages']=9
    m.checkpoint(9,'original_rvl003_remote_shell_and_controls','建立原版 RVL-003 遥控器的曲面后壳、正面按键、红外窗口、扬声器孔、四个指示灯、背部 B 键和六接点扩展接口，不加入 MotionPlus 外形。')



def _coil(key,radius,height,pitch,wire,origin,axis=(0,1,0)):
    from .atari2600 import _helical_spring
    shape=_helical_spring(radius,pitch,height,wire)
    shape.Placement=App.Placement(V(*origin),App.Rotation(V(0,0,1),V(*axis)))
    shape.check(True)
    return shape


def stage10(m):
    cx,cy=-25,-235
    m.box('RemotePCB','Original Remote main control board',29,134,.8,(cx,cy,21.4),'Controller',0,'pcb',1.2,True)
    fixing=[(cx-11,cy-61),(cx+11,cy-61),(cx-11,cy+55),(cx+11,cy+55)]
    m.cut('RemotePCB',[Part.makeCylinder(1,1.1,V(x,y,21.25)) for x,y in fixing],'Remote circuit-board mounting holes')
    m.box('RemoteBluetooth','Remote Bluetooth control package',9,9,1.2,(cx,cy+5,22.3),'Controller',0,'black',.3,True)
    m.box('RemoteAccelerometer','Three-axis accelerometer package',4,4,1,(cx+8,cy+28,22.3),'Controller',0,'black',.3,True)
    m.box('RemoteEEPROM','Remote calibration-memory package',4,5,1,(cx+8,cy-9,22.3),'Controller',0,'black',.3,True)
    for i in range(12):m.box('RemotePassive'+str(i),'Remote support passive',1.4,.7,.45,(cx-11+(i%3)*2,cy+1+(i//3)*4,22.3),'Controller',0,'cream',.1,True)
    m.box('RemoteIRBoard','Infrared camera daughterboard',12,9,.65,(cx,cy+63,22.4),'Controller',0,'pcb',.5,True)
    m.box('RemoteIRCamera','Infrared pointing-camera package',6,5,3,(cx,cy+64,24),'Controller',0,'black',.5,True)
    m.cyl('RemoteIRLens','Infrared camera lens',2.0,1.6,(cx,cy+68.0,24.8),'Controller',0,'black',axis=(0,1,0),internal=True)
    m.ring('RemoteSpeaker','Speaker outer frame',7.5,6.4,3.2,(cx,cy-22,22.8),'Controller',0,'black',internal=True)
    m.cyl('RemoteSpeakerMagnet','Loudspeaker magnet',4.7,1.9,(cx,cy-22,23),'Controller',0,'metal',internal=True)
    m.cyl('RemoteSpeakerCone','Speaker diaphragm',6.1,.2,(cx,cy-22,25.35),'Controller',0,'thermal',internal=True)
    m.cyl('RemoteMotor','Vibration motor',4.3,16,(cx-5,cy+28,13),'Controller',0,'metal',axis=(0,1,0),internal=True)
    weight=Part.makeCylinder(3.8,2,V(cx-5,cy+45,13),V(0,1,0),180)
    m.feature('RemoteEccentric','Eccentric vibration weight',weight,'Controller',0,'metal',True)
    m.cyl('RemoteMotorShaft','Vibration motor shaft',.8,.8,(cx-5,cy+44.1,13),'Controller',0,'metal',axis=(0,1,0),internal=True)
    for i,side in enumerate([-1,1]):
        x=cx+side*7.5;direction=(0,1,0) if i==0 else (0,-1,0);start=cy-48 if i==0 else cy+2.2
        m.cyl('RemoteAA'+str(i),'AA cell envelope',7,50.2,(x,start,10.4),'Controller',-2,'battery',axis=direction,internal=True)
        m.cyl('RemoteAANegative'+str(i),'AA negative end cap',6.5,.3,(x,cy-48.35 if i==0 else cy+2.55,10.4),'Controller',-2,'metal',axis=direction,internal=True)
        m.cyl('RemoteAAPositive'+str(i),'AA positive terminal',2,.8,(x,cy+2.3 if i==0 else cy-48.1,10.4),'Controller',-2,'metal',axis=direction,internal=True)
        coil=_coil('AA'+str(i),2.4,3.65,.9,.18,(x,cy-52.2 if i==0 else cy+6.55,10.4),direction)
        m.feature('RemoteAASpring'+str(i),'AA coil contact spring',coil,'Controller',-2,'metal',True)
        m.box('RemoteAARail'+str(i),'Battery side support rail',.5,59,12.5,(cx+side*15,cy-23,6.3),'Controller',-2,'wiiwhite',.1,True)
    m.box('RemoteAASeparator','Battery compartment center divider',.55,58,14,(cx,cy-23,3),'Controller',-2,'wiiwhite',.1,True)
    # Carbon pads and elastomer domes remain distinct from the plastic controls.
    contacts=[('DPad',cx,cy+41,8.1),('A',cx,cy+18,5.8),('Minus',cx-10.5,cy-4,2.5),('Home',cx,cy-4,2.5),('Plus',cx+10.5,cy-4,2.5),('One',cx,cy-43,3),('Two',cx,cy-56,3),('Power',cx-10.5,cy+60.5,2.1)]
    for key,x,y,r in contacts:
        m.cyl('Remote'+key+'Carbon','Conductive carbon contact',r*.55,.09,(x,y,24.7),'Controller',1,'black',internal=True)
        m.ring('Remote'+key+'Rubber','Silicone key dome',r,r*.57,.6,(x,y,24.85),'Controller',1,'rubber',internal=True)
        top=27.25 if key=='DPad' else 27.55
        fuse_feature(m,'Remote'+key,Part.makeCylinder(min(1.8,r*.4),top-25.55,V(x,y,25.55)),'Integrated button stem')
    m.box('RemoteBPCB','Rear trigger switch board',17,25,.8,(cx,cy+31,7.05),'Controller',-2,'pcb',2,True)
    m.box('RemoteBSwitch','Rear trigger tactile switch',7,9,1.6,(cx,cy+31,5.25),'Controller',-2,'black',1,True)
    # A separate cable and case-fixing pass follows with the remaining kit.
    m.profile['stages']=10
    m.checkpoint(10,'remote_optical_sensor_speaker_rumble_and_aa_cells','补齐遥控器控制板、红外相机、三轴加速度计、扬声器、偏心振动机构、两节 AA 电池及弹簧触点，加入按键导电接点和 B 键小板。')



def _nunchuk_outline(width,depth):
    sx,sy=width/38.2,depth/113
    curves=[Part.LineSegment(V(-11*sx,56.5*sy),V(11*sx,56.5*sy))]
    segments=[[(11,56.5),(18,56.5),(19.1,43),(19.1,25)],[(19.1,25),(19.1,-2),(15.5,-36),(10.8,-44)],[(10.8,-44),(7,-51),(4,-56.5),(0,-56.5)],[(0,-56.5),(-4,-56.5),(-7,-51),(-10.8,-44)],[(-10.8,-44),(-15.5,-36),(-19.1,-2),(-19.1,25)],[(-19.1,25),(-19.1,43),(-18,56.5),(-11,56.5)]]
    for points in segments:
        curve=Part.BezierCurve();curve.setPoles([V(x*sx,y*sy) for x,y in points]);curves.append(curve.toBSpline())
    return curves


def _console_fit(m):
    # Measured clearance corrections retain the existing editable construction tools.
    obj=m.parts['SMD2_0_2'];obj.Placement.Base+=V(0,3.2,0);obj.FlatPlacement=obj.Placement
    for obj in m.doc.Objects:
        if obj.TypeId=='Part::Feature' and obj.Label.startswith('Case fixing shaft passage and recessed head · tool'):
            sh=obj.Shape.copy();sh.translate(V(.3 if sh.BoundBox.Center.x>0 else -.3,0,0));obj.Shape=sh
    for i in range(4):
        obj=m.parts['CaseMount'+str(i)];obj.Placement.Base+=V(.3 if obj.Shape.BoundBox.Center.x>0 else -.3,0,0);obj.FlatPlacement=obj.Placement
    posts=[Part.makeCylinder(2.1,38.2,V(x,y,4.4)).cut(Part.makeCylinder(.85,39,V(x,y,4.2))) for x in [-74.3,74.3] for y in [-97,100]]
    m.parts['UpperHousing'].Tool.Shape=Part.makeCompound(posts)
    m.doc.recompute()


def stage11(m):
    from .retro_common import loft_shell
    from .atari2600 import _rounded_route
    _console_fit(m)
    cx,cy=72,-234
    loft_shell(m,'NunchukBack','Curved Nunchuk lower shell',[(19,86,1,cx,cy-7,1.5),(32,107,1,cx,cy-1,5),(38.2,113,1,cx,cy,18)],[(16,83,1,cx,cy-7,3),(29,103.8,1,cx,cy-1,6),(35,110,1,cx,cy,18.2)],'Nunchuk',-4,'wiiwhite',outline=_nunchuk_outline)
    loft_shell(m,'NunchukFront','Curved Nunchuk upper shell',[(38.2,113,1,cx,cy,18.25),(35,107,1,cx,cy,27.5),(30,90,1,cx,cy+4,30)],[(35,110,1,cx,cy,18.1),(31.8,103.8,1,cx,cy,26),(27,86.8,1,cx,cy+4,28.4)],'Nunchuk',4,'wiiwhite',outline=_nunchuk_outline)
    m.cut('NunchukFront',Part.makeCylinder(5.1,12,V(cx,cy+24,25)),'Analog-stick shaft opening')
    m.cyl('NunchukStick','Analog control-stick stem',3.6,12.6,(cx,cy+24,22.55),'Nunchuk',3,'wiiwhite')
    cap=Part.makeCylinder(8.7,2.3,V(cx,cy+24,35.2)).cut(Part.makeSphere(15,V(cx,cy+24,51.5)))
    m.feature('NunchukThumb','Concave analog-stick thumb cap',cap,'Nunchuk',4,'wiigrey')
    for key,w,h,z in [('C',13.5,7.5,25),('Z',20,11,14.3)]:
        hole=m.rr(w+.7,h+.7,11,(cx,cy+47,z),2.5,REAR)
        for shell in ['NunchukBack','NunchukFront']:m.cut(shell,hole,key+' trigger opening')
        m.box('Nunchuk'+key,key+' trigger cap',w,h,1.5,(cx,cy+55,z),'Nunchuk',4,'wiiwhite',2.3,orient=REAR)
        m.label('Nunchuk'+key+'Mark',key,3,(cx+1,cy+56.55,z-1.1),'Nunchuk',4,'wiigrey',rotation=REAR)
    wire=Part.Wire([c.toShape() for c in _nunchuk_outline(25,81)])
    board=Part.Face(wire).extrude(V(0,0,.8));board.translate(V(cx,cy+4,12.6))
    m.feature('NunchukPCB','Nunchuk control board',board,'Nunchuk',0,'pcb',True)
    m.box('NunchukStickBase','Analog mechanism housing',14,14,8,(cx,cy+24,14.4),'Nunchuk',1,'black',1.1,True)
    m.box('NunchukPotX','X-axis potentiometer study',4.2,9,5,(cx+9.4,cy+24,16),'Nunchuk',1,'cream',.6,True)
    m.box('NunchukPotY','Y-axis potentiometer study',9,4.2,5,(cx,cy+33.4,16),'Nunchuk',1,'cream',.6,True)
    m.box('NunchukController','Nunchuk control package',5,7,1,(cx,cy-15,13.5),'Nunchuk',0,'black',.3,True)
    m.box('NunchukAccelerometer','Nunchuk three-axis accelerometer',3.5,3.5,1,(cx,cy-29,13.5),'Nunchuk',0,'black',.3,True)
    for i in range(8):m.box('NunchukPassive'+str(i),'Nunchuk support passive',1.2,.7,.4,(cx-7+(i%2)*3,cy-20+(i//2)*4,13.5),'Nunchuk',0,'cream',.1,True)
    m.box('NunchukTriggerPCB','Nunchuk C/Z switch board',17,21,.7,(cx,cy+45,19),'Nunchuk',0,'pcb',.8,True,orient=REAR)
    for key,z in [('C',25),('Z',14.3)]:m.box('Nunchuk'+key+'Switch',key+' trigger contact',7,5,2.1,(cx,cy+46,z),'Nunchuk',1,'black',.5,True,orient=REAR)
    for shell in ['NunchukBack','NunchukFront']:m.cut(shell,Part.makeCylinder(3.2,19,V(cx,cy-47,14),V(0,-1,0)),'Cable strain-relief opening')
    m.cyl('NunchukRelief','Rear cable strain relief',3,12,(cx,cy-52,14),'Nunchuk',0,'wiiwhite',axis=(0,-1,0))
    points=[V(cx,cy-64,14),V(cx,-319,14),V(43,-342,14),V(-25,-342,17),V(-25,-328,17)]
    m.feature('NunchukCable','Nunchuk expansion cable display length',_rounded_route(points,3,1.4),'Nunchuk',0,'wiiwhite')
    m.box('NunchukPlug','Expansion plug grip',23,15,12,(-25,-320,11),'Nunchuk',0,'wiiwhite',1.8)
    head=m.rr(17.8,7.3,3.2,(-25,-312.4,17),.6,REAR).cut(m.rr(15.4,4.9,3.6,(-25,-312.6,17),.3,REAR))
    m.feature('NunchukPlugHead','Expansion plug contact shell',head,'Nunchuk',0,'metal')
    for i in range(6):m.box('NunchukPlugPin'+str(i),'Expansion plug contact',.65,2.5,.12,(-25+(i-2.5)*2.2,-310.5,16.2),'Nunchuk',0,'gold',.06)
    m.profile['stages']=11
    m.checkpoint(11,'curved_nunchuk_controls_and_expansion_cable','加入原生贝塞尔轮廓的 Nunchuk 曲面外壳、模拟摇杆、C/Z 键、控制板与扩展线；同时按干涉报告调整主机外壳支柱与无线接口周边间隙。')



def _vertical_stand(m,cx,cy):
    import Sketcher
    body=m.doc.addObject('PartDesign::Body','ConsoleStandBody')
    sketch=m.doc.addObject('Sketcher::SketchObject','ConsoleStandProfile');body.addObject(sketch)
    points=[(-112.8,0),(112.8,0),(110,42),(-110,8)]
    sketch.addGeometry([Part.LineSegment(V(*a),V(*b)) for a,b in zip(points,points[1:]+points[:1])],False)
    for i in range(4):sketch.addConstraint(Sketcher.Constraint('Block',i))
    pad=body.newObject('PartDesign::Pad','ConsoleStandPad');pad.Profile=(sketch,['']);pad.Length=55.4
    body.Placement=App.Placement(V(cx-27.7,cy,0),g.rotation((1,0,0),(0,0,1)))
    m.doc.recompute();sketch.Visibility=False
    m.register(body,'ConsoleStand','Accessories',0,'wiigrey')
    m.cut('ConsoleStand',m.rr(44.8,216,45,(cx,cy,6),1.2),'Vertical console cradle opening')


def stage12(m):
    from .atari2600 import _rounded_route
    cy=152
    m.native('SensorLower','RVL-014 sensor bar lower shell',240,23.4,1.2,3.2,(0,cy,0),'Accessories',-3,'wiigrey')
    m.cut('SensorLower',m.rr(237.8,21.2,2.4,(0,cy,1.1),.6),'Sensor bar lower cavity')
    m.native('SensorUpper','RVL-014 sensor bar upper shell',240,23.4,1.2,5.95,(0,cy,3.45),'Accessories',3,'wiigrey')
    m.cut('SensorUpper',m.rr(237.8,21.2,4.9,(0,cy,3.3),.6),'Sensor bar upper cavity')
    for side in [-1,1]:
        x=side*90
        opening=m.rr(44.8,6.4,5,(x,cy-9,4.7),.8,FRONT)
        for shell in ['SensorLower','SensorUpper']:m.cut(shell,opening,'Infrared emitter window')
        m.box('SensorWindow'+str(side),'Dark infrared-pass window',44.2,5.8,.7,(x,cy-11.1,4.7),'Accessories',3,'black',.6,orient=FRONT)
        m.box('SensorPCB'+str(side),'Five-emitter circuit board',44,10,.7,(x,cy-3.5,1.2),'Accessories',0,'pcb',.6,True)
        for i in range(5):
            xx=x+(i-2)*7
            m.cyl('SensorEmitter'+str(side)+'_'+str(i),'Infrared emitter',1.4,2.7,(xx,cy-7.7,4.7),'Accessories',0,'red',axis=(0,-1,0),internal=True)
            for leg,dx in enumerate([-.5,.5]):
                sh=Part.makeCylinder(.17,2.7,V(xx+dx,cy-6.8,2.0)).fuse(Part.makeCylinder(.17,.65,V(xx+dx,cy-6.8,4.7),V(0,-1,0)))
                m.feature('SensorLead'+str(side)+'_'+str(i)+'_'+str(leg),'Formed infrared emitter lead',sh,'Accessories',0,'metal',True)
    for shell in ['SensorLower','SensorUpper']:m.cut(shell,Part.makeCylinder(1.0,9,V(0,cy+7,4.7),V(0,1,0)),'Sensor bar power-cable exit')
    wire=_rounded_route([V(0,cy+11.9,4.7),V(0,184,4.7),V(145,184,4.7),V(145,135.3,4.7)],3,.8)
    m.feature('SensorCable','Sensor-bar power cable display length',wire,'Accessories',0,'black')
    m.box('SensorPlug','Sensor-bar two-pin plug',6,10,5.6,(145,130,1.9),'Accessories',0,'black',.7)
    m.box('SensorPlugTip','Sensor-bar keyed plug nose',4.4,4,3.2,(145,122.8,3.1),'Accessories',0,'red',.4)
    for i,x in enumerate([143.9,146.1]):m.box('SensorPlugPin'+str(i),'Sensor-bar power contact',.45,3,.5,(x,122.4,4.4),'Accessories',0,'gold',.06)
    m.box('SensorStandBase','RVL-016 sensor-bar stand base',70,26.1,3,(0,205,0),'Accessories',0,'wiigrey',7)
    m.box('SensorStandPost','Sensor-bar stand support',26,10,17.2,(0,205,3.2),'Accessories',0,'wiigrey',2)
    m.box('SensorStandCradle','Sensor-bar locating cradle',28,11,.8,(0,205,20.4),'Accessories',0,'wiigrey',1.5)
    _vertical_stand(m,220,-5)
    m.box('StandAuxPlate','RVL-019 auxiliary stand plate',120,109,7.7,(220,170,0),'Accessories',0,'wiigrey',24)
    m.cut('StandAuxPlate',m.rr(56.3,44,6.4,(220,170,1.5),4),'Stand locating recess')
    for i,(x,y) in enumerate([(174,133),(266,133),(174,207),(266,207)]):m.box('StandPad'+str(i),'Auxiliary plate rubber pad',8,10,.7,(x,y,-.7),'Accessories',0,'rubber',2)
    m.profile['stages']=12
    m.checkpoint(12,'original_sensor_bar_and_vertical_stands','加入原版双五灯感应条、两芯插头与感应条支架，并用原生斜面草图和拉伸制作竖放支架，补齐辅助底板。')



def _wii_av_accessory(m):
    from .atari2600 import _rounded_route
    m.box('AVPlug','Wii Multi AV plug grip',24,20,12,(330,-190,2),'Accessories',0,'wiigrey',2)
    head=m.rr(20.2,7.4,6,(330,-200.2,8),.8,FRONT).cut(m.rr(18,5.2,6.4,(330,-200,8),.5,FRONT))
    m.feature('AVPlugShell','Wii AV plug contact shroud',head,'Accessories',0,'metal')
    m.box('AVPlugTongue','AV plug insulating tongue',17,5,.8,(330,-203,7),'Accessories',0,'black',.3)
    for row in range(2):
        for i in range(8):m.box('AVPlugPin'+str(row)+'_'+str(i),'AV plug contact',.55,4,.1,(330+(i-3.5)*2.1,-203,6.84 if row==0 else 7.86),'Accessories',0,'gold',.06)
    trunk=_rounded_route([V(330,-179.8,8),V(330,-175,8),V(348,-165,8),V(368,-182,8),V(373.8,-182,8)],2,1.65)
    m.feature('AVCable','AV cable main jacket display length',trunk,'Accessories',0,'black')
    m.box('AVSplitter','AV cable three-way strain relief',12,8,10,(380,-182,3),'Accessories',0,'black',1.2)
    for i,(x,color) in enumerate([(350,'yellow'),(380,'wiiwhite'),(410,'red')]):
        points=[V(377+i*3,-177.8,8),V(377+i*3,-174.8,8),V(x,-161,8),V(x,-153.3,8)] if i!=1 else [V(380,-177.8,8),V(380,-153.3,8)]
        m.feature('AVBranch'+str(i),'Individual RCA cable',_rounded_route(points,2,1.1),'Accessories',0,'black')
        m.cyl('RCAGrip'+str(i),'Composite / stereo RCA grip',4.5,20,(x,-153,8),'Accessories',0,'black',axis=(0,1,0))
        m.ring('RCAColor'+str(i),'RCA function color ring',5.0,4.55,3,(x,-142,8),'Accessories',0,color,axis=(0,1,0))
        m.ring('RCAGround'+str(i),'RCA outer ground sleeve',3.6,2.5,6,(x,-132.8,8),'Accessories',0,'metal',axis=(0,1,0))
        m.cyl('RCAPin'+str(i),'RCA center signal pin',.9,7,(x,-132.6,8),'Accessories',0,'gold',axis=(0,1,0))


def stage13(m):
    from .atari2600 import _rounded_route
    m.colors['yellow']=(.91,.73,.10)
    cx,cy=220,-170
    m.native('AdapterLower','RVL-002 power adapter lower shell',136,55,3,21.3,(cx,cy,0),'Accessories',-4,'wiigrey')
    m.cut('AdapterLower',m.rr(132.4,51.4,20,(cx,cy,1.8),1.7),'Adapter lower cavity')
    m.native('AdapterUpper','RVL-002 power adapter upper shell',136,55,3,21.45,(cx,cy,21.55),'Accessories',4,'wiigrey')
    m.cut('AdapterUpper',m.rr(132.4,51.4,19.8,(cx,cy,21.4),1.7),'Adapter upper cavity')
    m.box('AdapterPCB','Adapter structural study board',125,43,1,(cx,cy,6.5),'Accessories',0,'pcb',1.2,True)
    m.box('AdapterTransformer','Power transformer core and bobbin',28,28,24,(cx,cy,9),'Accessories',0,'black',2,True)
    m.box('AdapterWinding','Transformer winding insulation',22,29,10,(cx,cy,15),'Accessories',0,'cream',1,True)
    # A real recess separates the winding envelope from the ferrite core.
    m.cut('AdapterTransformer',m.rr(22.5,30,10.5,(cx,cy,14.75),1.2),'Transformer winding recess')
    m.cyl('AdapterBulkCap','Primary smoothing capacitor',7.2,22,(cx-43,cy-9,9),'Accessories',0,'black',internal=True)
    m.cyl('AdapterOutputCap','Secondary smoothing capacitor',5.2,15,(cx+41,cy+8,9),'Accessories',0,'metal',internal=True)
    m.cyl('AdapterOutputCoil','Output filter inductor',6.2,10,(cx+38,cy-11,9),'Accessories',0,'copper',internal=True)
    m.cyl('AdapterInputCoil','Input filter coil',6,8,(cx-53,cy+10,9),'Accessories',0,'cream',internal=True)
    m.box('AdapterRectifier','Rectifier package',12,7,3,(cx-37,cy+14,9),'Accessories',0,'black',.6,True)
    m.box('AdapterHeatPlate','Power-device metal heat spreader',1,23,21,(cx+20,cy,9),'Accessories',0,'metal',.1,True)
    points=[(cx+x,cy+y) for x in [-57,57] for y in [-17,17]]
    m.cut('AdapterPCB',[Part.makeCylinder(1.15,1.4,V(x,y,6.3)) for x,y in points],'Adapter board fixing holes')
    posts=[]
    for i,(x,y) in enumerate(points):
        posts.append(Part.makeCylinder(2.1,4.6,V(x,y,1.7)).cut(Part.makeCylinder(.8,5,V(x,y,1.5))))
        m.screw('AdapterScrew'+str(i),(x,y,8.05),'Accessories',0,length=3.2,radius=1.8,axis=(0,0,-1))
    fuse_feature(m,'AdapterLower',Part.makeCompound(posts),'Adapter board support posts')
    for shell in ['AdapterLower','AdapterUpper']:
        m.cut(shell,Part.makeCylinder(2.5,10,V(cx-73,cy,13.5),V(1,0,0)),'AC cable exit')
        m.cut(shell,Part.makeCylinder(2.7,10,V(cx+63,cy,25),V(1,0,0)),'DC cable exit')
    m.label('AdapterMark','RVL-002 STUDY',4,(cx-29,cy-2,43.04),'Accessories',4,'black')
    ac=_rounded_route([V(151.8,cy,13.5),V(135,cy,13.5),V(115,-183,6),V(115,-202.3,6)],2.5,2.0)
    m.feature('AdapterACCable','Fixed AC cord display length',ac,'Accessories',0,'black')
    m.box('AdapterACPlug','Japanese two-blade AC plug',23,15,12,(115,-210,0),'Accessories',0,'black',2)
    for i,x in enumerate([108.8,121.2]):m.box('AdapterACBlade'+str(i),'Flat AC plug blade',1.4,6.2,13,(x,-210,12.1),'Accessories',0,'metal',.12)
    dc=_rounded_route([V(288.2,cy,25),V(315,cy,25),V(315,-100,25),V(305,-90,12),V(288.2,-90,12)],2.5,1.8)
    m.feature('AdapterDCCable','Fixed DC cord display length',dc,'Accessories',0,'black')
    m.box('AdapterDCPlug','Wii DC plug grip',20,12,8,(278,-90,8),'Accessories',0,'wiigrey',1.4)
    head=m.rr(10,7,8,(267.8,-90,12),.6,SIDE).cut(m.rr(7.5,4.5,8.4,(268,-90,12),.4,SIDE))
    m.feature('AdapterDCHead','Wii two-position DC plug head',head,'Accessories',0,'cream')
    for i,y in enumerate([-92,-88]):m.box('AdapterDCPin'+str(i),'DC plug contact',5,.7,.5,(263.5,y,11.75),'Accessories',0,'gold',.06)
    _wii_av_accessory(m)
    for key,x,y,r in [('WiiDisc',215,-300,60),('GCDisc',320,-295,40)]:
        m.ring(key,'Blank '+('12 cm Wii' if r==60 else '8 cm GameCube')+' optical medium',r,7.5,1.2,(x,y,0),'Accessories',0,'metal')
        m.ring(key+'Hub','Transparent disc center region',17,7.55,.04,(x,y,1.24),'Accessories',0,'wiigrey')
        m.label(key+'Mark','BLANK STUDY',3.5,(x-14,y+21,1.25),'Accessories',0,'black')
    m.profile['stages']=13
    m.checkpoint(13,'power_adapter_av_connections_and_blank_media','加入原版电源适配器的结构示意、日式电源插头、双芯直流插头、十六位 AV 转三 RCA 线，以及不含游戏数据的 12 cm 与 8 cm 空白光盘。')



def _tri_fastener(m,key,x,y,z,tip,group):
    head=Part.makeCylinder(1.7,.45,V(x,y,z)).fuse(Part.makeCylinder(.6,tip-z-.43,V(x,y,z+.43)))
    slots=[]
    for i in range(3):
        sh=Part.makeBox(.32,1.3,.23,V(x-.16,y-.08,z-.02));sh.rotate(V(x,y,z),V(0,0,1),i*120);slots.append(sh)
    return m.feature(key,'Tri-point enclosure fastener',head.cut(Part.makeCompound(slots)),group,-3,'metal',True)


def _controller_fixings(m):
    cx,cy=-25,-235;posts=[]
    for i,(x,y) in enumerate([(cx-11,cy-61),(cx+11,cy-61),(cx-11,cy+55),(cx+11,cy+55)]):
        z=3.3 if i<2 else 2.0
        m.cut('RemoteBack',[Part.makeCylinder(.9,12,V(x,y,z-.3)),Part.makeCylinder(1.95,.75,V(x,y,z-.2))],'Remote rear fastener passage')
        _tri_fastener(m,'RemoteCaseScrew'+str(i),x,y,z,25.6,'Controller')
        posts.append(Part.makeCylinder(2,5.8,V(x,y,22.35)).cut(Part.makeCylinder(.8,6,V(x,y,22.25))))
    fuse_feature(m,'RemoteFront',Part.makeCompound(posts),'Four upper-cover fixing bosses')
    cx,cy=72,-234;posts=[]
    for i,y in enumerate([cy-38,cy+37]):
        z=2.2 if i==0 else 3.0
        m.cut('NunchukBack',[Part.makeCylinder(.9,12,V(cx,y,z-.3)),Part.makeCylinder(1.95,.75,V(cx,y,z-.2))],'Nunchuk rear fastener passage')
        m.cut('NunchukPCB',Part.makeCylinder(1.0,1.2,V(cx,y,12.4)),'Nunchuk board fastener passage')
        _tri_fastener(m,'NunchukCaseScrew'+str(i),cx,y,z,24.0,'Nunchuk')
        post=Part.makeCylinder(2,12,V(cx,y,19.5)).common(m.doc.getObject('NunchukFrontOuter').Shape)
        post=post.cut(Part.makeCylinder(.8,12.2,V(cx,y,19.4)));posts.append(post)
    fuse_feature(m,'NunchukFront',Part.makeCompound(posts),'Roof-clipped Nunchuk fixing bosses')


def _console_harness(m):
    from .atari2600 import _rounded_route
    from .ps1 import _yz_strip
    # The real separate faceplate closes the open front of the two main shells.
    front=m.rr(149,38,5,(0,-100,23),1,FRONT)
    for key in ['LowerHousing','UpperHousing']:m.cut(key,front,'Open front return for optical path and faceplate wiring')
    m.parts['DrivePCB'].Placement.Base+=V(-12,0,0);m.parts['DrivePCB'].FlatPlacement=m.parts['DrivePCB'].Placement
    polygon=[(-55,10.65),(-60,10.65),(-64.15,14.5),(-64.15,20.9),(-60,21.4),(-60,21.2),(-63.95,20.7),(-63.95,14.7),(-59.95,10.85),(-55,10.85)]
    m.feature('DriveRibbon','Folded optical-drive data ribbon',_yz_strip(-30,18,polygon),'Optical',1,'copper',True)
    m.cut('MainShield',m.rr(22,10,1,(-21,-62,17.7),.7),'Drive data ribbon shield passage')
    m.cut('MainShield',m.rr(10,11,1,(11.5,-75.7,17.7),.7),'Drive power harness shield passage')
    for i in range(6):
        x=35.5+i;end=9+i;row=-73-i*1.1
        points=[V(x,-64,10.9),V(x,-64,14.8),V(x,row,14.8),V(end,row,14.8),V(end,row,20.9),V(end,-66,20.9)]
        m.feature('DriveWire'+str(i),'Optical-drive individual power lead',_rounded_route(points,.7,.22),'Optical',1,'wiiwhite' if i%2 else 'black',True)
    m.box('FrontLEDSocket','Faceplate light harness connector',6,5,2,(50.6,-85.4,7.6),'Mainboard',0,'cream',.4,True)
    for i in range(2):
        x=68.25+i*.9
        points=[V(x,-103.5,32),V(x,-101.5,32),V(x,-101.5,18),V(70+i*.6,-98,16),V(70+i*.6,-88-i*.8,14),V(50+i*1.2,-85-i*.8,12),V(50+i*1.2,-85-i*.8,9.9)]
        m.feature('FrontLEDWire'+str(i),'Faceplate illumination lead',_rounded_route(points,.35,.17),'Controls',1,'red' if i==0 else 'black',True)
    m.box('FanSocket','Rear fan harness connector',6,4,2,(49.5,85,7.4),'Mainboard',0,'cream',.4,True)
    for i in range(2):
        points=[V(-8.5+i,95.25,22.5+i),V(-8.5+i,94,22.5+i),V(-8.5+i,94,16+i),V(49+i,94,16+i),V(49+i,87,12),V(49+i,85,9.7)]
        m.feature('FanWire'+str(i),'Fan power harness lead',_rounded_route(points,.3,.18),'Cooling',1,'red' if i==0 else 'black',True)
    for i,(startx,end_y,end_z) in enumerate([(-50,-75,31),(-36,69,28)]):
        y=37+i*2.2;z=15.5+i*.9
        points=[V(startx,15,12.7),V(startx,15,z),V(startx,y,z),V(73.4,y,z),V(73.4,end_y,z),V(73.4,end_y,end_z)]
        m.feature('WifiCable'+str(i),'Radio miniature coax cable',_rounded_route(points,.7,.35),'Wireless',1,'black' if i==0 else 'wiiwhite',True)
        m.box('WifiAntenna'+str(i),'Case-side Wi-Fi antenna substrate',23,7,.6,(74.5,end_y,end_z+3),'Wireless',2,'pcb',.6,True,orient=SIDE)
        traces=[m.rr(.65,4,.035,(73.85,end_y+(j-2)*3,end_z+3),.1,SIDE) for j in range(5)]
        m.feature('WifiAntennaTrace'+str(i),'Antenna conductor study',Part.makeCompound(traces),'Wireless',2,'gold',True)


def stage14(m):
    # Fit the front trigger board inside the curved Nunchuk roof.
    m.parts['NunchukTriggerPCB'].Shape=m.rr(15,17,.7,(72,-234+45,19),.8,REAR)
    m.cut('SensorPlugTip',[m.rr(.7,5,.75,(x,122.4,4.3),.06) for x in [143.9,146.1]],'Two separate sensor plug contact channels')
    _controller_fixings(m)
    _console_harness(m)
    m.profile['stages']=14
    m.checkpoint(14,'harness_antenna_case_bosses_and_final_fit','补齐光驱排线与供电线、前灯和风扇线束、两条 Wi-Fi 天线线及遥控器/双节棍三翼螺钉，修正小板与接点间隙，并打开主机前缘的光盘与走线通道。')



def stage15(m):
    from .atari2600 import _rounded_route
    # Move the front Nunchuk fixing away from the Y potentiometer.
    m.parts['NunchukBack'].Tool.Shape=m.parts['NunchukBack'].Tool.Shape.translated(V(0,3,0))
    m.parts['NunchukPCB'].Tool.Shape=m.parts['NunchukPCB'].Tool.Shape.translated(V(0,3,0))
    screw=m.parts['NunchukCaseScrew1'];screw.Placement.Base+=V(0,3,0);screw.FlatPlacement=screw.Placement
    outer=m.doc.getObject('NunchukFrontOuter').Shape;posts=[]
    for y in [-234-38,-234+40]:
        post=Part.makeCylinder(2,12,V(72,y,19.5)).common(outer).cut(Part.makeCylinder(.8,12.2,V(72,y,19.4)));posts.append(post)
    m.parts['NunchukFront'].Tool.Shape=Part.makeCompound(posts)
    # Route around the rear-left optical-drive pillar rather than through it.
    points=[V(-50,15,12.7),V(-50,15,15.5),V(-46,20,15.5),V(-46,37,15.5),V(73.4,37,15.5),V(73.4,-75,15.5),V(73.4,-75,31)]
    m.parts['WifiCable0'].Shape=_rounded_route(points,.7,.35)
    # Separate the two faceplate leads in height through the tight bend.
    points=[V(69.15,-103.5,32),V(69.15,-101.5,32),V(69.15,-101.5,18.7),V(70.6,-98,16.7),V(70.6,-88,14.7),V(51.2,-85.8,12.7),V(51.2,-85.8,9.9)]
    m.parts['FrontLEDWire1'].Shape=_rounded_route(points,.35,.17)
    m.doc.recompute()
    for obj in m.parts.values():obj.Shape.check(True)
    m.profile['stages']=15
    m.checkpoint(15,'verified_routing_and_strict_brep_final_fit','依据全装配求交结果移动双节棍前固定点、避让光驱支柱并分开前灯线束的转弯高度，逐一执行全部组件的严格 BRep 检查。')

STAGES=[stage01,stage02,stage03,stage04,stage05,stage06,stage07,stage08,stage09,stage10,stage11,stage12,stage13,stage14,stage15]


def finalize(model):
    """Shared deliverables plus views suited to the Wii's horizontal enclosure."""
    from .deliver import finalize as shared_finalize
    result=shared_finalize(model);manifest=result[0]
    main=manifest['handheld_groups'];body=manifest['envelope_groups']
    model.snapshot('final_front',normal=(.2,-1.5,.65),assemblies=body)
    model.snapshot('final_internal',normal=(.2,-.5,2.4),assemblies=body,exclude=model.profile['internal_exclude'])
    model.snapshot('final_hero',normal=(.5,-1.6,1.4),assemblies=main)
    model.doc.save()
    return result
