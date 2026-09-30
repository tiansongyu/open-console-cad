"""CUH-1000A launch-family PS4: staged, editable approximation."""
import FreeCAD as App
import Part
from .core import V
from . import geometry as g

SLOPE=18.0/53.0


def _prism_yz(points, xmin=-160, width=320):
    vertices=[V(xmin,y,z) for y,z in points]
    return Part.Face(Part.makePolygon(vertices+[vertices[0]])).extrude(V(width,0,0))


def _slant_tools():
    # Continuous oblique front/rear planes; envelope is 305 mm over 53 mm high.
    return [_prism_yz([(-180,-2),(-152.5-2*SLOPE,-2),(-152.5+55*SLOPE,55),(-180,55)]),
            _prism_yz([(134.5-2*SLOPE,-2),(180,-2),(180,55),(134.5+55*SLOPE,55)])]


def _cavity(xmin,xmax,zmin,zmax,inset=1.6):
    return _prism_yz([(-152.5+zmin*SLOPE+inset,zmin),(134.5+zmin*SLOPE-inset,zmin),
                      (134.5+zmax*SLOPE-inset,zmax),(-152.5+zmax*SLOPE+inset,zmax)],xmin,xmax-xmin)


def stage01(m):
    m.colors.update(ps4matte=(.095,.10,.11),ps4gloss=(.045,.05,.06),ps4blue=(.12,.35,.8))
    m.params.set('A3','Depth (Y)');m.params.set('A4','Height (Z)')
    m.native('LowerHousing','Original oblique lower enclosure',275,305,.25,21.7,(0,0,1.5),'Body',-5,'ps4matte',expr={'Width':'Parameters.Width','Height':'Parameters.Height'})
    m.cut('LowerHousing',_slant_tools(),'Front and rear oblique case faces').Refine=False
    m.cut('LowerHousing',_cavity(-135.9,135.9,3.1,24),'Open lower tray with 1.6 mm skin').Refine=False
    # 2.4 mm separation accommodates the original top indicator channel.
    for key,label,xmin,xmax,material in [
        ('HDDCover','Removable glossy hard-drive cover',-137.5,-47.2,'ps4gloss'),
        ('UpperHousing','Original matte upper enclosure',-44.8,137.5,'ps4matte')]:
        m.native(key,label,xmax-xmin,305,.25,24,((xmin+xmax)/2,0,29),'Body',5,material)
        m.cut(key,_slant_tools(),'Matching oblique upper faces').Refine=False
        # Adjacent edges have no artificial full-height divider wall.
        inner_min=xmin+1.6 if xmin==-137.5 else xmin-.3
        inner_max=xmax-1.6 if xmax==137.5 else xmax+.3
        m.cut(key,_cavity(inner_min,inner_max,28.7,51.4),'Open upper skin and outer edge returns').Refine=False
    g.appearance(m.parts['HDDCover'],m.colors['ps4gloss'],metal=.65,gloss=85)
    m.native('MiddleFrame','Recessed inter-layer perimeter',271,300,.25,4.4,(0,0,23.8),'Frame',0,'black')
    m.cut('MiddleFrame',_slant_tools(),'Oblique belt ends').Refine=False
    m.cut('MiddleFrame',_cavity(-133,133,23.6,28.4,4.0),'Open belt centre').Refine=False
    for i,(x,y,w,d) in enumerate([(-46,-111,7,15),(-46,97,7,15),(111,99,8,13)]):
        m.box('Foot'+str(i),'Rubber support pad',w,d,1.5,(x,y,0),'Body',-6,'rubber',.5)
    m.box('IndicatorLens','Recessed blue top status light guide',1.35,236,.85,(-46,7,51.95),'Controls',6,'ps4blue',.2)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=1
    m.checkpoint(1,'original_slanted_enclosure','建立原生下壳、亮面硬盘盖、磨砂上盖、内凹中框、脚垫及顶面状态灯；保持公开近似包络，斜角、分割及壁厚为照片指导的学习估计。接口及内部结构尚待后续构建。')


STAGES={1:stage01}


def stage02(m):
    front=g.rotation((0,-1,0),(0,0,1))
    # Front ports are recessed into the horizontal belt, not pasted on its face.
    slot=m.rr(127,3.3,9,(-67,-136,26),.5,front)
    m.cut('MiddleFrame',slot,'Optical media entrance through the recessed belt').Refine=False
    for i,z in enumerate([24.5,27.05]):
        m.box('DiscBrush'+str(i),'Opposed media dust brush study',126,2.2,.35,(-67,-141.4,z),'FrontIO',1,'black',.12)
    for n,x in enumerate([30,74]):
        key='USB'+str(n)
        opening=m.rr(15.3,7.8,19,(x,-127,26.1),.3,front)
        for case in ['LowerHousing','UpperHousing','MiddleFrame']:
            m.cut(case,opening,'Recessed USB 3.0 port '+str(n+1)).Refine=False
        outer=m.rr(14.4,7,14,(x,-129.5,26.1),.35,front)
        inner=m.rr(13.65,6.25,14.4,(x,-129.3,26.1),.18,front)
        m.feature(key+'Shield','USB Type-A stamped metal shell',outer.cut(inner),'FrontIO',0,'metal')
        m.box(key+'Carrier','USB rear insulating carrier',13.2,1.1,5.8,(x,-130.4,23.2),'FrontIO',0,'black',.12,True)
        m.box(key+'Tongue','Nine-contact USB 3.0 insulator',12.5,9.7,1.15,(x,-136.2,25.1),'FrontIO',1,'black',.12)
        for i in range(4):
            m.box(key+'Legacy'+str(i),'USB legacy contact',.68,5.0,.14,(x+(i-1.5)*2.5,-138.4,26.30),'FrontIO',1,'gold',.05,True)
        for i in range(5):
            m.box(key+'SuperSpeed'+str(i),'USB additional SuperSpeed contact',.48,2.0,.14,(x+(i-2)*2.0,-134.5,26.30),'FrontIO',1,'gold',.04,True)
        # Nine independent terminal tails; future board stage includes clearances.
        for i in range(9):
            m.box(key+'Tail'+str(i),'USB solder terminal tail',.30,3.3,.30,(x+(i-4)*1.05,-127.6,24.0),'FrontIO',0,'gold',.02,True)
    angled=g.rotation((0,-1,SLOPE),(0,0,1))
    for key,z,length in [('Power',42,11),('Eject',13,9)]:
        yy=-152.5+z*SLOPE
        if key=='Eject':
            m.cut('LowerHousing',m.rr(2.1,length+1,4,(-46,yy+1.5,z),.2,angled),'Lower touch-button seating pocket').Refine=False
        m.box(key+'Button',key+' capacitive front strip',1.3,length,.8,(-46,yy-.05,z),'Controls',2,'black',.18,orient=angled)
    # Shallow dark lettering follows the oblique front plane.
    for key,text,size,x,z in [('FrontSony','SONY',3.2,-127,42),('FrontPS4','PS4',4.6,106,42)]:
        m.label(key,text,size,(x,-152.5+z*SLOPE-.045,z),'Body',6,'black',rotation=angled)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=2
    m.checkpoint(2,'recessed_media_usb_and_touch_controls','在内凹横向接缝加工吸入式光盘入口和双 USB 3.0 开口，加入金属壳、绝缘舌片、九接点及独立端子；补齐初代纵向电源与出仓触控条和前部标识。局部尺寸和电气布局为学习近似。')
    m.snapshot('02_front_interfaces_review',normal=(.7,-1,.65))


STAGES[2]=stage02


def _keyed_rear_port(w,h,depth,x,y,z,chamfer):
    points=[(-w/2,-h/2+chamfer),(-w/2+chamfer,-h/2),(w/2-chamfer,-h/2),(w/2,-h/2+chamfer),(w/2,h/2),(-w/2,h/2)]
    vertices=[V(a,b,0) for a,b in points]
    shape=Part.Face(Part.makePolygon(vertices+[vertices[0]])).extrude(V(0,0,depth))
    shape.Placement=App.Placement(V(x,y,z),g.rotation((0,1,0),(0,0,1)))
    return shape


def stage03(m):
    rear=g.rotation((0,1,0),(0,0,1))
    # Repeated openings leave real vertical ribs and horizontal crossbars.
    for case,zs in [('LowerHousing',[8.5,16.5]),('HDDCover',[35.5,44]),('UpperHousing',[35.5,44])]:
        xs=[-125+12.5*i for i in range(21)]
        if case=='LowerHousing':xs=[x for x in xs if not 88<x<120]
        else:xs=[x for x in xs if x<-27 or x>95]
        cuts=[m.rr(9.3,6.4,25,(x,133,z),.25,rear) for x in xs for z in zs]
        m.cut(case,cuts,'Open rear exhaust grid with integral crossbars').Refine=False
    for case,x,zs in [('LowerHousing',-137,[12,18]),('LowerHousing',137,[12,18]),('HDDCover',-137,[33,39]),('UpperHousing',137,[33,39])]:
        cuts=[Part.makeBox(5,6.6,2.6,V(x-2.5,y,z)) for y in [-119+9*i for i in range(28)] for z in zs]
        m.cut(case,cuts,'Side intake slots with moulded ribs').Refine=False
    # Rear signal cluster in the upper tier; AC inlet in the lower tier.
    specs=[('Optical',72,10,10),('HDMI',46,15.5,6.4),('Ethernet',20,16,13.7),('AUX',-7,11.5,7.2)]
    for key,x,w,h in specs:
        aperture=m.rr(w+1.1,h+1.1,23,(x,131,39),.35,rear)
        m.cut('UpperHousing',aperture,'Rear '+key+' connector opening').Refine=False
        if key=='Optical':
            shell=m.rr(w,h,10,(x,138,39),.4,rear).cut(m.rr(w-2,h-2,10.4,(x,137.8,39),.25,rear))
            m.feature(key+'Body','Optical audio receptacle body',shell,'Ports',0,'black')
            m.box(key+'Shutter','Optical port dust shutter',7.5,.6,7.5,(x,147.15,35.25),'Ports',1,'black',.25)
            m.cyl(key+'Lens','Optical transmission lens study',1.6,1,(x,139.3,39),'Ports',0,'red',axis=(0,1,0),internal=True)
        else:
            shell=m.rr(w,h,12,(x,135.7,39),.35,rear).cut(m.rr(w-.8,h-.8,12.4,(x,135.5,39),.18,rear))
            if key=='HDMI':
                shell=_keyed_rear_port(w,h,12,x,135.7,39,1.6).cut(_keyed_rear_port(w-.8,h-.8,12.4,x,135.5,39,1.3))
            m.feature(key+'Shield','Rear '+key+' connector metal shell',shell,'Ports',0,'metal')
            if key=='HDMI':
                m.feature(key+'Rear','HDMI keyed insulating stop',_keyed_rear_port(w-1.3,h-1.3,1,x,135.95,39,1.3),'Ports',0,'black',True)
            else:
                m.box(key+'Rear','Rear '+key+' insulating stop',w-1.1,1,h-1.1,(x,136.45,39-(h-1.1)/2),'Ports',0,'black',.12,True)
            if key=='Ethernet':
                for i in range(8):
                    sh=Part.makeBox(.28,6,.25,V(x+(i-3.5)*1.25-.14,138.0,42.4))
                    sh.rotate(V(x,138,42.4),V(1,0,0),-20)
                    m.feature(key+'Contact'+str(i),'LAN spring contact study',sh,'Ports',1,'gold',True)
            else:
                m.box(key+'Tongue',key+' keyed insulating tongue',w-2,7.5,1.25,(x,141.4,38.4),'Ports',1,'black',.12)
                count=19 if key=='HDMI' else 14
                for i in range(count):
                    row=i%2;col=i//2;xx=x+(col-(count//2)/2)*(.65 if key=='HDMI' else .85)
                    m.box(key+'Contact'+str(i),key+' signal contact study',.25,4,.12,(xx,142,39.72 if row else 38.2),'Ports',1,'gold',.02,True)
    x,z=104,12
    ac=m.rr(18,10,21,(x,127,z),3,rear)
    m.cut('LowerHousing',ac,'Lower-tier AC inlet opening').Refine=False
    body=m.rr(17,9,12,(x,130,z),3,rear)
    bores=[Part.makeCylinder(3.3,12.5,V(x+dx,129.8,z),V(0,1,0)) for dx in [-4.1,4.1]]
    m.feature('ACInlet','Non-polarised two-lobe AC inlet',body.cut(Part.makeCompound(bores)),'Power',0,'black')
    for i,dx in enumerate([-4.1,4.1]):m.cyl('ACPin'+str(i),'AC inlet contact pin',.92,7.5,(x+dx,131.5,z),'Power',0,'metal',axis=(0,1,0))
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=3
    m.checkpoint(3,'rear_signal_ac_and_open_vent_grids','建立原版后侧光纤、HDMI、LAN、AUX 与下层 AC 插座，加入独立绝缘件和金属接点；加工上下层排风格栅及两侧进风槽。接口局部形状和针脚排布为示意，不作为生产规格。')
    m.snapshot('03_rear_interfaces_review',normal=(-.4,1,.8))


STAGES[3]=stage03


def stage04(m):
    cx,cy=-91,-77
    # Removable 2.5-inch drive study; local dimensions are estimates, not a drive drawing.
    m.native('HDDBase','2.5-inch hard-drive aluminium enclosure',69.8,100,.65,6,(cx,cy,42),'Storage',2,'metal')
    m.cut('HDDBase',m.rr(66.8,97,5.6,(cx,cy,43),.7),'Open HDD mechanism cavity').Refine=False
    m.box('DiskCover','Thin hard-drive metal lid',69.4,99.6,.45,(cx,cy,48.15),'Storage',5,'metal',.6)
    m.ring('HDDPlatter','Blank magnetic storage platter',30.8,6,.42,(cx,cy-9,44.4),'Storage',3,'metal',internal=True)
    m.cyl('HDDMotor','Disk spindle motor',8,1.1,(cx,cy-9,43.1),'Storage',2,'metal',internal=True)
    m.cyl('HDDHub','Platter hub',5.7,1.2,(cx,cy-9,44.3),'Storage',3,'metal',internal=True)
    for i in range(6):
        import math
        a=i*math.pi/3
        m.cyl('HDDHubScrew'+str(i),'Spindle clamp fixing',.55,.3,(cx+3.6*math.cos(a),cy-9+3.6*math.sin(a),45.55),'Storage',4,'metal',internal=True)
    px,py=cx-21,cy+31
    m.cyl('HDDPivot','Actuator pivot carrier',4.1,2,(px,py,43.2),'Storage',2,'metal',internal=True)
    armpts=[(px-3,py+3),(px+3,py+3),(cx-10,cy+12),(cx-13,cy+10),(px-3,py-3)]
    verts=[V(x,y,45.35) for x,y in armpts]
    arm=Part.Face(Part.makePolygon(verts+[verts[0]])).extrude(V(0,0,.4))
    m.feature('HDDActuator','Single-platter actuator arm study',arm,'Storage',4,'metal',True)
    m.box('HDDHead','Read-write head study',1.2,1.7,.2,(cx-11.4,cy+12,45.05),'Storage',3,'black',.12,True)
    m.box('HDDMagnet','Actuator magnet enclosure',16,15,2,(cx-18,cy+38,43.2),'Storage',2,'metal',1,True)
    m.cut('HDDMagnet',Part.makeCylinder(4.35,2.4,V(px,py,43)),'Actuator pivot relief').Refine=False
    m.native('HDDPCB','Hard-drive underside controller board',64,36,.7,1,(cx,cy+28,40.6),'Storage',0,'pcb')
    for key,x,y,w,d,t in [('Controller',cx-12,cy+24,11,11,1),('Cache',cx+12,cy+23,12,8,.85),('MotorDriver',cx,cy+38,8,8,.8)]:
        m.box('HDD'+key,'Disk '+key+' package study',w,d,t,(x,y,40.45-t),'Storage',-1,'black',.2,True)
    # SATA connector shares the rear edge of the drive, with separate 7/15 contact groups.
    for key,x,w,count in [('Data',cx-13,14,7),('Power',cx+11,25,15)]:
        m.cut('HDDBase',m.rr(w+1,8,3.8,(x,cy+49,40.2),.2),'SATA connector recess').Refine=False
        m.box('SATA'+key+'Carrier','SATA '+key+' keyed insulator',w,6,2.6,(x,cy+49,40.8),'Storage',0,'black',.15,True)
        for i in range(count):
            m.box('SATA'+key+str(i),'SATA '+key+' contact',.55,4,.12,(x+(i-(count-1)/2)*1.25,cy+49.4,43.45),'Storage',1,'gold',.02,True)
    m.native('HDDCaddy','Removable hard-drive tray base',74,104,.7,.6,(cx,cy,38.4),'Storage',-2,'metal')
    m.cut('HDDCaddy',m.rr(53,75,1,(cx,cy-5,38.2),3),'Large underside drive-tray relief').Refine=False
    for side in [-1,1]:
        m.box('HDDCaddySide'+str(side),'Folded hard-drive tray side',.7,102,10,(cx+side*36.4,cy,39.05),'Storage',0,'metal',.12)
        for i,dy in enumerate([-35,35]):
            x=cx+side*36.4;y=cy+dy
            bore=Part.makeCylinder(1.2,5,V(x-side*2.5,y,45),V(side,0,0))
            m.cut('HDDCaddySide'+str(side),bore,'Drive retaining screw clearance').Refine=False
            m.cut('HDDBase',Part.makeCylinder(1.0,4,V(cx+side*35.4,y,45),V(-side,0,0)),'Blind drive-side mounting hole').Refine=False
            shaft=Part.makeCylinder(.8,4.0,V(cx+side*37.2,y,45),V(-side,0,0))
            head=Part.makeCylinder(2.2,.65,V(cx+side*37.1,y,45),V(side,0,0))
            m.feature('HDDMount'+str(side)+'_'+str(i),'Drive caddy retaining screw',shaft.fuse(head),'Storage',1,'metal',True)
    m.box('HDDPullTab','Drive tray extraction tab',14,6,.7,(cx,cy-54,39),'Storage',0,'metal',.4)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=4
    m.checkpoint(4,'removable_hard_drive_and_storage_mechanism','补齐亮面盖下独立硬盘托架、原生硬盘壳体、薄盖、盘片与主轴、磁头臂、底面控制板、SATA 两组接点和四组安装件。硬盘内部为单盘片学习示意，不声称复刻实机盘片配置。')
    m.snapshot('04_storage_internal',assemblies=['Storage'],exclude=['DiskCover'],normal=(.2,-.4,2))


STAGES[4]=stage04


def stage05(m):
    m.native('MainPCB','Original launch-family L-shaped mainboard',260,257,1.5,1.6,(0,3.5,30),'Mainboard',0,'pcb')
    m.cut('MainPCB',m.rr(89,109,2,(-88,-71.5,29.8),1),'Front-left hard-drive and optical bay relief').Refine=False
    mounting=[(-121,122),(121,122),(121,-115),(-34,-115),(-34,-7),(-121,0),(12,76),(105,63)]
    m.cut('MainPCB',[Part.makeCylinder(1.7,2,V(x,y,29.8)) for x,y in mounting],'Mainboard mounting bores').Refine=False
    for i,(x,y) in enumerate(mounting):
        for side,z in [('Top',31.62),('Bottom',29.92)]:
            m.ring('BoardGround'+side+str(i),'Exposed PCB ground annulus',3.2,1.8,.06,(x,y,z),'Mainboard',0,'gold',internal=True)
    m.box('APUSubstrate','AMD Jaguar / Radeon APU substrate study',40,40,2.4,(60,20,27.4),'Mainboard',-1,'pcb',.3,True)
    m.box('APUDie','APU exposed silicon die study',20,20,.85,(60,20,26.4),'Mainboard',-2,'black',.15,True)
    for side in [-1,1]:
        for i in range(8):
            m.box('APUCap'+str(side)+'_'+str(i),'APU package bypass capacitor',1.7,.9,.35,(47.4+i*3.6,20+side*16,26.95),'Mainboard',-2,'metal',.08,True)
    ram=[(x,y) for y in [-14,54] for x in [40,60,80]]+[(100,10),(100,30)]
    for i,(x,y) in enumerate(ram):
        m.box('GDDR5Bottom'+str(i),'512 MB GDDR5 package, underside study',16,12,1.2,(x,y,28.55),'Mainboard',-1,'black',.22,True)
        m.box('GDDR5Top'+str(i),'512 MB GDDR5 package, upper side study',16,12,1.2,(x,y,31.85),'Mainboard',1,'black',.22,True)
    for key,label,x,y,w,h in [
        ('Secondary','Low-power network processor',-58,37,22,22),
        ('DDR3','Secondary processor memory',-90,39,15,11),
        ('Flash','Serial flash package',-106,72,11,8),
        ('EthernetLogic','Ethernet controller',17,103,14,14),
        ('HDMILogic','HDMI communication package',49,102,14,14),
        ('WirelessLogic','WLAN / Bluetooth package',-84,99,12,12),
        ('USBHub','USB 3.0 hub controller',48,-104,12,12)]:
        m.box(key,label+' study',w,h,1.4,(x,y,31.85),'Mainboard',1,'black',.18,True)
    for i,x in enumerate([-11,11,33,55,77,99]):
        m.box('VRMChoke'+str(i),'APU power regulation inductor',10,10,5.5,(x,-77,31.85),'Mainboard',1,'metal',.6,True)
        m.box('VRMPower'+str(i),'Power stage package',6,7,1.3,(x,-94,31.85),'Mainboard',1,'black',.16,True)
        m.cyl('VRMCap'+str(i),'Power regulation capacitor',3.2,6,(x,-59,31.85),'Mainboard',1,'metal',internal=True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=5
    m.checkpoint(5,'native_l_shaped_board_apu_memory_and_power','建立原生 L 形主板、安装孔和接地环、朝下的 APU 基板与裸片、正反共十六枚显存封装、主要接口逻辑及供电元件。内部位置、封装与高度为原版拆解指导的结构示意，不复制电路或布线。')
    m.snapshot('05_mainboard_top',assemblies=['Mainboard'],normal=(0,0,1))
    m.snapshot('05_mainboard_bottom',assemblies=['Mainboard'],normal=(0,0,-1))


STAGES[5]=stage05


def stage06(m):
    mounting=[(-121,122),(121,122),(121,-115),(-34,-115),(-34,-7),(-121,0),(12,76),(105,63)]
    for key,label,z in [('LowerShield','Lower mainboard EMI and thermal plate',25.7),('UpperShield','Upper perforated motherboard shield',40.0)]:
        m.native(key,label,260,257,1.2,.45,(0,3.5,z),'Shielding',-3 if key=='LowerShield' else 3,'metal')
        cuts=[m.rr(89,109,1,(-88,-71.5,z-.2),1)]
        if key=='LowerShield':cuts.append(m.rr(24,24,1,(60,20,z-.2),.8))
        else:
            for x in [-18,12,42,72,102]:
                for y in [-103,-52,-1,50,101]:
                    cuts.append(m.rr(11,3.5,1,(x,y,z-.2),1.1))
        cuts.extend(Part.makeCylinder(1.35,1,V(x,y,z-.2)) for x,y in mounting)
        m.cut(key,cuts,'Shield bay relief, thermal/perforation openings and fixings').Refine=False
    for i,(x,y) in enumerate(mounting):
        m.ring('BoardStandoff'+str(i),'Lower shield mainboard spacer',3.35,.9,3.6,(x,y,26.2),'Frame',-1,'metal',internal=True)
        m.screw('BoardScrew'+str(i),(x,y,32.1),'Frame',1,length=5.2,radius=1.25,axis=(0,0,-1))
        m.ring('UpperShieldSpacer'+str(i),'Upper shield sleeve',3.35,1.55,7.7,(x,y,32.2),'Frame',2,'metal',internal=True)
    # Thermal interfaces sit below eight underside memory devices, above the lower plate.
    ram=[(x,y) for y in [-14,54] for x in [40,60,80]]+[(100,10),(100,30)]
    for i,(x,y) in enumerate(ram):m.box('MemoryThermal'+str(i),'GDDR5 thermal pad study',14,10,2.3,(x,y,26.2),'Cooling',-2,'thermal',.3,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=6
    m.profile['internal_exclude']=list(dict.fromkeys(m.profile.get('internal_exclude',[])+['UpperShield','DiskCover']))
    m.checkpoint(6,'native_emi_plates_spacers_and_memory_thermal_interfaces','补齐原生上下屏蔽板、硬盘区避让、APU 热窗口、通孔与散热开口、八组主板固定结构和显存导热垫；结构厚度、紧固件及局部开孔为学习近似。')
    m.snapshot('06_shielding_review',assemblies=['Shielding','Frame'],normal=(.2,-.6,2))


STAGES[6]=stage06


def _blower_blade(height=12.0):
    import math
    def p(r,a):return V(r*math.cos(math.radians(a)),r*math.sin(math.radians(a)),0)
    a,b,c=p(17,0),p(28,12),p(42.3,25)
    d,e,f=p(42.3,26.1),p(28,13.1),p(17,1.1)
    wire=Part.Wire([Part.Arc(a,b,c).toShape(),Part.makeLine(c,d),Part.Arc(d,e,f).toShape(),Part.makeLine(f,a)])
    return Part.Face(wire).extrude(V(0,0,height))


def stage07(m):
    from .ps1 import _add_shape
    cx,cy=65,-42
    m.native('BlowerHousing','Centrifugal blower volute and discharge duct',94,96,.8,17.5,(cx,cy,4.5),'Cooling',-4,'black')
    _add_shape(m,'BlowerHousing',m.rr(31,87,17.5,(113.5,5.5,4.5),.7),'Integral rearward blower duct').Refine=False
    cavity=Part.makeCylinder(44,18,V(cx,cy,4.3)).fuse(m.rr(26,85,18,(113,7.5,4.3),.7))
    m.cut('BlowerHousing',cavity,'Open volute and discharge passage').Refine=False
    assert len(m.parts['BlowerHousing'].Shape.Solids)==1, 'Disconnected blower housing'
    m.box('BlowerPlate','Blower lower metal bracket',93.4,95.4,.35,(cx,cy,4.05),'Cooling',-5,'metal',.8,True)
    disc=Part.makeCylinder(42.4,.65,V(cx,cy,5.5))
    hub=Part.makeCylinder(14,12.6,V(cx,cy,5.5))
    blades=[]
    for i in range(29):
        blade=_blower_blade();blade.rotate(V(),V(0,0,1),i*360/29);blade.translate(V(cx,cy,6.05));blades.append(blade)
    rotor=disc.fuse(hub).multiFuse(blades).cut(Part.makeCylinder(10,12.4,V(cx,cy,4.3))).removeSplitter()
    assert len(rotor.Solids)==1, 'Disconnected impeller vanes'
    m.feature('BlowerImpeller','Approximately 85 mm curved-vane impeller study',rotor,'Cooling',-3,'black',True)
    m.ring('BlowerStator','Blower motor stator envelope',9.5,2.8,11.8,(cx,cy,4.45),'Cooling',-4,'metal',internal=True)
    m.cyl('BlowerAxle','Blower motor steel shaft',2.3,11.9,(cx,cy,4.65),'Cooling',-3,'metal',internal=True)
    m.box('APUThermal','APU thermal interface study',20,20,1.7,(60,20,24.7),'Cooling',-2,'thermal',.2,True)
    m.box('CopperColdplate','APU copper heat-spreader plate',40,40,2.5,(60,20,22.2),'Cooling',-3,'copper',1,True)
    pipes=[]
    for i,x in enumerate([45,75]):
        shape=Part.makeCylinder(2.2,52,V(x,20,20),V(0,1,0))
        m.feature('HeatPipe'+str(i),'Sealed heat-pipe envelope study',shape,'Cooling',-4,'copper',True);pipes.append(Part.makeCylinder(2.35,56,V(x,18,20),V(0,1,0)))
    m.box('FinBase','Heat exchanger lower rail',94,28,.6,(73,64,3.4),'Cooling',-5,'metal',.3,True)
    tool=Part.makeCompound(pipes)
    for i in range(52):
        x=26.9+i*1.8
        fin=Part.makeBox(.3,26,21.4,V(x,51,4.0)).cut(tool)
        m.feature('CoolingFin'+str(i),'Separate heat exchanger lamella',fin,'Cooling',-4,'metal',True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=7
    m.checkpoint(7,'centrifugal_blower_apu_interface_and_heat_exchanger','建立约 85 mm 离心叶轮、弯曲叶片、蜗壳风道、定子与轴、APU 接触层、铜板、双热管包络及独立散热鳍片。叶片数量、风道、热管路径与间隙为学习近似，不作热流体仿真。')
    m.snapshot('07_cooling_review',assemblies=['Cooling'],normal=(.3,-.5,1.8))


STAGES[7]=stage07


def stage08(m):
    m.colors['powerpcb']=(.46,.36,.12)
    m.native('PSUCase','Original internal power-supply lower enclosure',256,51,.8,20,(0,106.5,3.3),'Power',-5,'black')
    m.cut('PSUCase',m.rr(253,48,20,(0,106.5,4.5),.5),'Open power supply enclosure').Refine=False
    m.cut('PSUCase',m.rr(19,17,12,(104,135,6.7),1),'AC inlet case relief').Refine=False
    m.native('PSUPCB','Internal switching power board',240,46,.6,1.3,(0,107,6.2),'Power',-3,'powerpcb')
    mounts=[(x,y) for x in [-114,114] for y in [88,125]]
    m.cut('PSUPCB',[Part.makeCylinder(1.2,1.7,V(x,y,6.0)) for x,y in mounts],'Four power board mounting holes').Refine=False
    for i,(x,y) in enumerate(mounts):
        m.ring('PSUPost'+str(i),'Power board insulating spacer',2.5,.8,1.5,(x,y,4.55),'Power',-4,'black',internal=True)
        m.screw('PSUScrew'+str(i),(x,y,8),'Power',-2,length=2.7,radius=1.2,axis=(0,0,-1))
    for key,x,y,w,d,h in [('Main',-28,107,24,28,12),('Standby',-72,111,12,16,10)]:
        m.box('PSU'+key+'Core','Switching transformer ferrite core',w,d,h,(x,y,7.65),'Power',-2,'black',1,True)
        # Thin winding cover is separate, with no overlap into the ferrite envelope.
        m.box('PSU'+key+'Wrap','Transformer winding insulation cover',w-3,d-3,.45,(x,y,7.75+h),'Power',-1,'powerpcb',.4,True)
    for i,y in enumerate([93,112]):
        m.cyl('PSUBulk'+str(i),'Horizontal primary bulk capacitor',6.8,24,(52,y,14.6),'Power',-2,'battery',axis=(1,0,0),internal=True)
        m.cyl('PSUBulkEnd'+str(i),'Primary capacitor metal end',6.55,.25,(76.1,y,14.6),'Power',-1,'metal',axis=(1,0,0),internal=True)
    for i,x in enumerate([-105,-87,-69,-51]):
        m.cyl('PSUOutputCap'+str(i),'Secondary filter capacitor',4,12,(x,91,7.65),'Power',-2,'battery',internal=True)
        m.cyl('PSUOutputVent'+str(i),'Filter capacitor aluminium vent',3.65,.2,(x,91,19.75),'Power',-1,'metal',internal=True)
    m.box('PSUInputChoke','Input common-mode choke envelope',12,15,11.5,(98,101,7.65),'Power',-2,'copper',1,True)
    m.box('PSUBridge','Input rectifier package',12,8,8,(98,120,7.65),'Power',-2,'black',.3,True)
    m.cyl('PSUFuse','Cartridge fuse ceramic body',2,16,(91,86,10.2),'Power',-2,'white',axis=(1,0,0),internal=True)
    for i,x in enumerate([90,107.4]):m.cyl('PSUFuseCap'+str(i),'Fuse metal end cap',2.15,.7,(x,86,10.2),'Power',-2,'metal',axis=(1,0,0),internal=True)
    for i,x in enumerate([-44,-3]):
        m.box('PSUHeatSink'+str(i),'Power semiconductor aluminium heat sink',3,22,12,(x,110,7.65),'Power',-2,'metal',.3,True)
        m.box('PSUSwitch'+str(i),'Power switch package study',4,8,10,(x-6,110,7.65),'Power',-2,'black',.2,True)
    for i,x in enumerate([-105,-98]):
        m.box('PSUOutputBus'+str(i),'Low-voltage output bus contact',3.5,5,.8,(x,126,14),'Power',-1,'copper',.2,True)
        m.box('PSUOutputLeg'+str(i),'Output bus vertical leg',3.5,.6,6.2,(x,124,7.7),'Power',-2,'copper',.1,True)
    m.native('PSUCover','Perforated internal power-supply cover',255,50,.7,.6,(0,106.5,23.5),'Power',2,'black')
    holes=[m.rr(8,2.5,1,(x,y,23.3),.6) for x in [-115+12*i for i in range(20)] for y in [91,102,113,124]]
    m.cut('PSUCover',holes,'Power supply ventilation slots').Refine=False
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=8
    m.profile['internal_exclude']=list(dict.fromkeys(m.profile.get('internal_exclude',[])+['PSUCover']))
    m.checkpoint(8,'internal_power_supply_board_and_filter_components','补齐内置电源壳体、原生电源板、变压器、输入滤波与保险丝、整流和功率封装、横卧主电容、输出滤波及通风盖。元件与隔离布局为学习示意，不作为可通电电路或制造依据。')
    m.snapshot('08_power_supply_review',assemblies=['Power'],exclude=['PSUCover'],normal=(.1,-.5,2))


STAGES[8]=stage08


def stage09(m):
    # Refine the vertical stack now that the slot-loading disc plane is established.
    # This is a study assembly placement, not a measured factory stack dimension.
    elevated={'APUThermal','CopperColdplate','HeatPipe0','HeatPipe1'}
    for key,o in m.parts.items():
        if o.Assembly in ['Mainboard','Shielding'] or key in elevated or key.startswith(('BoardStandoff','BoardScrew','UpperShieldSpacer','MemoryThermal')):
            place=o.Placement;place.Base=place.Base+V(0,0,3);o.Placement=place;o.FlatPlacement=place
    tool=Part.makeCompound([Part.makeCylinder(2.35,56,V(x,18,23),V(0,1,0)) for x in [45,75]])
    for i in range(52):m.parts['CoolingFin'+str(i)].Shape=Part.makeBox(.3,26,24.4,V(26.9+i*1.8,51,4)).cut(tool)
    m.native('OpticalTray','Slot-loading optical mechanism chassis',146,145,.7,23.4,(-57,-55.5,4.6),'Optical',-4,'metal')
    m.cut('OpticalTray',m.rr(143,142,23.2,(-57,-55.5,5.9),.5),'Open optical chassis with thin floor').Refine=False
    front=g.rotation((0,-1,0),(0,0,1))
    m.cut('OpticalTray',m.rr(125,4,16,(-66,-123,26),.45,front),'Media path aligned with the front slot').Refine=False
    m.native('DriveCover','Optical drive pressed upper lid',145,144,.6,.5,(-57,-55.5,28.1),'Optical',3,'metal')
    m.ring('DriveMedia','Blank 120 mm utility disc',60,7.5,1.2,(-57,-55,25.4),'Optical',1,'white',internal=True)
    m.cyl('SpindleMotor','Optical spindle motor envelope',12,5.8,(-57,-55,11),'Optical',-3,'metal',internal=True)
    m.cyl('SpindleCarrier','Spindle bearing carrier',11,6.4,(-57,-55,17),'Optical',-2,'black',internal=True)
    m.cyl('SpindleHub','Disc centring spindle',7,2.9,(-57,-55,23.5),'Optical',0,'black',internal=True)
    m.ring('SpindleSeat','Media support annulus',10,7.2,.8,(-57,-55,24.45),'Optical',0,'rubber',internal=True)
    m.cyl('DriveClamp','Magnetic upper disc clamp',15,.6,(-57,-55,26.65),'Optical',2,'metal',internal=True)
    m.cyl('DriveClampMagnet','Clamp magnet envelope',8,.45,(-57,-55,27.35),'Optical',2,'black',internal=True)
    for i,(x,y) in enumerate([(x,y) for x in [-124,10] for y in [-121,10]]):
        m.ring('DriveMount'+str(i),'Optical chassis support spacer',2.4,1.1,1.35,(x,y,3.15),'Optical',-5,'rubber',internal=True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=9
    m.profile['internal_exclude']=list(dict.fromkeys(m.profile.get('internal_exclude',[])+['DriveCover','DriveMedia','DriveClamp','DriveClampMagnet']))
    m.checkpoint(9,'optical_stack_chassis_spindle_and_blank_medium','调整主板和屏蔽层安装高度，使光盘中心平面与前吸入口对齐；补齐原生光驱框架、上盖、主轴与夹盘以及空白介质。安装高度和局部机构尺寸仍为学习近似。')
    m.snapshot('09_optical_stack_review',assemblies=['Optical'],exclude=['DriveCover'],normal=(.2,-.5,2))


STAGES[9]=stage09


def stage10(m):
    rails=[]
    for i,x in enumerate([-80,-34]):
        m.cyl('PickupRail'+str(i),'Optical pickup guide rod',1.35,63,(x,-116,17),'Optical',-2,'metal',axis=(0,1,0),internal=True)
        rails.append(Part.makeCylinder(2.65,24,V(x,-100,17),V(0,1,0)))
        m.ring('PickupBearing'+str(i),'Pickup sliding guide sleeve',2.5,1.6,13,(x,-94.5,17),'Optical',-1,'white',axis=(0,1,0),internal=True)
        for j,y in enumerate([-118,-54]):
            m.ring('RailEnd'+str(i)+'_'+str(j),'Fixed optical rail support',2.5,1.6,4,(x,y,17),'Optical',-2,'black',axis=(0,1,0),internal=True)
            m.box('RailFoot'+str(i)+'_'+str(j),'Guide support pedestal',6,4,8.2,(x,y+2,6.1),'Optical',-3,'black',.3,True)
    carriage=m.rr(52,22,7,(-57,-88,12),1).cut(Part.makeCompound(rails))
    m.feature('OpticalCarriage','Optical pickup carriage with guide bores',carriage,'Optical',-1,'metal',True)
    m.box('ObjectiveBase','BD/DVD objective support',13,11,2.8,(-57,-84,19.2),'Optical',0,'black',.5,True)
    frame=m.rr(9,9,.9,(-57,-84,22.15),.5).cut(m.rr(5.8,5.8,1.2,(-57,-84,22),.5))
    m.feature('FocusFrame','Objective focus suspension frame study',frame,'Optical',1,'metal',True)
    m.cyl('ObjectiveLens','Optical objective lens envelope',2.6,.8,(-57,-84,23.2),'Optical',2,'blue',internal=True)
    for i,y in enumerate([-89,-79]):m.box('FocusCoil'+str(i),'Focus actuator coil envelope',9,.7,1,(-57,y,22.1),'Optical',1,'copper',.15,True)
    for i,(x,y,color) in enumerate([(-74,-93,'blue'),(-74,-82,'red')]):
        m.cyl('LaserPackage'+str(i),'BD/DVD laser package study',1.6,5,(x,y,21),'Optical',0,color,axis=(1,0,0),internal=True)
    m.box('OpticalPrism','Optical path prism housing study',3.5,4,2,(-66,-88,20),'Optical',0,'black',.2,True)
    m.cyl('FeedMotor','Pickup feed motor envelope',6,14,(-20,-111,18),'Optical',-2,'metal',axis=(0,1,0),internal=True)
    m.cut('FeedMotor',Part.makeCylinder(1.3,15,V(-20,-111.5,18),V(0,1,0)),'Feed shaft axial clearance').Refine=False
    m.cyl('FeedShaft','Feed motor shaft',.9,17,(-20,-110,18),'Optical',-1,'metal',axis=(0,1,0),internal=True)
    m.cyl('FeedScrew','Pickup feed screw envelope',1.1,41,(-20,-93,18),'Optical',-1,'metal',axis=(0,1,0),internal=True)
    m.ring('FeedCoupler','Feed shaft coupling sleeve',2.2,1.3,3,(-20,-95.5,18),'Optical',-1,'white',axis=(0,1,0),internal=True)
    nut=m.rr(6,9,6,(-20,-88,15),.4).fuse(m.rr(9,7,2,(-26.5,-88,16.5),.3))
    nut=nut.cut(Part.makeCylinder(1.4,11,V(-20,-93.5,18),V(0,1,0)))
    m.feature('FeedNut','Pickup drive nut and carriage link',nut,'Optical',-1,'white',True)
    m.cyl('LoadingShaft','Slot-loading roller shaft',.85,110,(-124,-123,23.1),'Optical',0,'metal',axis=(1,0,0),internal=True)
    for i,x in enumerate([-118,-64]):m.ring('LoadingRoller'+str(i),'Media intake rubber roller',2.2,1.1,43,(x,-123,23.1),'Optical',0,'rubber',axis=(1,0,0),internal=True)
    for i,x in enumerate([-125,-70,-15]):m.ring('LoadingBearing'+str(i),'Intake roller bearing support',2.3,1.05,1.5,(x,-123,23.1),'Optical',0,'white',axis=(1,0,0),internal=True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=10
    m.checkpoint(10,'optical_pickup_guides_feed_and_loading_rollers','补齐双导杆、滑动轴套、光头座、物镜与焦点框架、BD/DVD 发光封装、进给电机与轴系、螺杆包络和前部吸入滚轮。运动副、齿形及光路为静态学习示意。')
    m.snapshot('10_optical_mechanism_review',assemblies=['Optical'],exclude=['DriveCover','DriveMedia','DriveClamp','DriveClampMagnet'],normal=(.2,-.5,2))


STAGES[10]=stage10


def _small_fpc(m,key,x,y,z,width,count,assembly):
    m.box(key+'Body','Flat-flex connector insulating body',width,3,1.4,(x,y,z),assembly,1,'white',.15,True)
    slot=m.rr(width-2,1.6,.5,(x,y+.9,z+.55),.1)
    m.cut(key+'Body',slot,'Flat-flex cable mouth').Refine=False
    m.box(key+'Latch','Flat-flex connector locking bar',width-1,1.2,.35,(x,y-.5,z+1.5),assembly,2,'black',.1,True)
    for i in range(count):m.box(key+'Pad'+str(i),'Flat-flex solder pad',.28,2.5,.1,(x+(i-(count-1)/2)*.6,y+2.75,z-.2),assembly,0,'gold',.02,True)


def stage11(m):
    m.profile['envelope_groups']=list(dict.fromkeys(m.profile['envelope_groups']+['Controls','Shielding']))
    m.native('DrivePCB','Separate optical controller board',134,22,.7,1.1,(-57,3,6.2),'Optical',-3,'pcb')
    mounts=[(x,y) for x in [-118,3] for y in [-3,10]]
    bores=[Part.makeCylinder(1.05,4,V(x,y,4.4)) for x,y in mounts]
    m.cut('DrivePCB',bores,'Optical controller board mounting clearances').Refine=False
    m.cut('OpticalTray',bores,'Optical controller screw holes through chassis floor').Refine=False
    for i,(x,y) in enumerate(mounts):m.screw('DriveBoardScrew'+str(i),(x,y,8),'Optical',-2,length=2,radius=1.2,axis=(0,0,-1))
    for key,label,x,y,w,h in [('OpticalControl','Optical control processor',-91,4,13,11),('MotorDriver','Optical motor driver',-59,7,14,8),('DriveLogic','Drive logic package',-38,1,8,8)]:
        m.box(key,label+' study',w,h,1.3,(x,y,7.5),'Optical',-2,'black',.2,True)
    _small_fpc(m,'PickupFlex',-72,-4,7.55,16,18,'Optical')
    _small_fpc(m,'DriveMainFlex',-13,5,7.55,22,24,'Optical')
    for i,x in enumerate([-109,-105,-101,-97,-93,-89,-85,-81]):
        m.box('DrivePassive'+str(i),'Optical board passive package study',1.8,.85,.6,(x,-4.8,7.45),'Optical',-2,'metal',.08,True)
    for i,x in enumerate([-56,-51,-46]):
        m.cyl('DriveFilter'+str(i),'Optical board filter capacitor',1.5,2.7,(x,-4.8,7.45),'Optical',-2,'metal',internal=True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=11
    m.checkpoint(11,'separate_optical_logic_board_and_flat_flex_interfaces','补齐独立原生光驱控制板、安装孔与螺钉、控制和电机驱动封装、两组带锁扣排线座及独立焊盘和滤波元件。封装、针数与局部电气布局为学习示意。')
    m.snapshot('11_optical_board_review',assemblies=['Optical'],exclude=['DriveCover','DriveMedia','DriveClamp','DriveClampMagnet'],normal=(.2,-.5,2))


STAGES[11]=stage11


def stage12(m):
    from .ps2 import _flat_ribbon
    m.colors['flex']=(.52,.29,.085)
    for key,o in m.parts.items():
        if key.startswith('PickupFlex'):
            place=o.Placement;place.Base=place.Base+V(15,0,0);o.Placement=place;o.FlatPlacement=place
    for i,(old,new) in enumerate(zip([-56,-51,-46],[-108,-104,-100])):
        o=m.parts['DriveFilter'+str(i)];place=o.Placement;place.Base=place.Base+V(new-old,13.8,0);o.Placement=place;o.FlatPlacement=place
    _small_fpc(m,'MainOpticalFlex',-13,29,34.85,22,24,'Mainboard')
    _small_fpc(m,'PickupEndFlex',-57,-98,19.6,14,18,'Optical')
    m.cut('OpticalTray',m.rr(20,5,1,(-13,16,7.9),.2),'Optical controller ribbon exit').Refine=False
    m.cut('LowerShield',m.rr(20,1.2,1.2,(-13,19,28.4),.2),'Optical ribbon passage through lower shield').Refine=False
    m.cut('MainPCB',m.rr(20,1.2,2.2,(-13,19,32.7),.2),'Optical ribbon passage through mainboard study').Refine=False
    main=[(-13,5.3,8.35),(-13,19,8.35),(-13,19,36.9),(-13,34,36.9),(-13,34,35.65),(-13,29.9,35.65)]
    pickup=[(-57,-3.2,8.35),(-57,1.5,8.35),(-57,1.5,10.5),(-57,-104,10.5),(-57,-104,22),(-57,-95.5,22),(-57,-95.5,20.4),(-57,-97.2,20.4)]
    m.feature('OpticalMainRibbon','Optical drive to mainboard routed ribbon study',_flat_ribbon(main,18.8),'Wiring',0,'white',True)
    m.feature('PickupRibbon','Optical head flexible cable study',_flat_ribbon(pickup,11.2),'Wiring',0,'flex',True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=12
    m.checkpoint(12,'optical_ribbons_and_verified_frame_passages','建立光驱到主板和光头到驱动板的独立弯折排线、末端锁扣插座，并在光驱壳体、屏蔽板和主板学习模型上加工对应通道。走线、针数和通道位置为静态装配近似。')
    m.snapshot('12_optical_ribbons_review',assemblies=['Optical','Wiring'],exclude=['DriveCover','DriveMedia','DriveClamp','DriveClampMagnet'],normal=(.2,-.5,2))


STAGES[12]=stage12


def stage13(m):
    from .atari2600 import _rounded_route
    # Three blower leads rise outside the volute through matching plate/board holes.
    ys=[-43,-42,-41]
    m.cut('BlowerHousing',[Part.makeCylinder(.45,8,V(107,y,4.9),V(1,0,0)) for y in ys],'Three motor lead exits').Refine=False
    for key,z in [('LowerShield',28.5),('MainPCB',32.8)]:
        m.cut(key,[Part.makeCylinder(.55,2.1,V(114,y,z)) for y in ys],'Blower lead vertical passages').Refine=False
    body=m.rr(4,5,3.5,(114,-42,35),.3)
    body=body.cut(Part.makeCompound([Part.makeCylinder(.5,4,V(114,y,34.8)) for y in ys]))
    m.feature('FanHeader','Three-position blower connector study',body,'Mainboard',1,'white',True)
    for i,y in enumerate(ys):
        m.ring('FanContact'+str(i),'Blower header terminal sleeve',.4,.26,2.8,(114,y,34.7),'Mainboard',1,'metal',internal=True)
        path=[V(75,y,4.9),V(114,y,4.9),V(114,y,35.9)]
        m.feature('FanLead'+str(i),'Routed blower lead',_rounded_route(path,.65,.23),'Wiring',0,['black','red','white'][i],True)
    for family,xs in [('Spindle',[-70,-71]),('Feed',[-28,-29])]:
        mid=sum(xs)/2
        carrier=m.rr(5,3,2.5,(mid,-3.5,7.6),.2)
        holes=[Part.makeCylinder(.45,3.4,V(x,-5.2,8.6),V(0,1,0)) for x in xs]
        m.feature(family+'Header','Two-position optical motor connector study',carrier.cut(Part.makeCompound(holes)),'Optical',0,'white',True)
        for i,x in enumerate(xs):
            m.ring(family+'Terminal'+str(i),'Optical motor connector contact',.4,.26,2,(x,-4.5,8.6),'Optical',0,'metal',axis=(0,1,0),internal=True)
            points=[(-69.5-i,-55,12),(x,-45,8.6),(x,-3.8,8.6)] if family=='Spindle' else [(-26.5-i,-104,18),(x,-97,10),(x,-28,10),(x,-7,8.6),(x,-3.8,8.6)]
            m.feature(family+'Lead'+str(i),'Routed optical '+family.lower()+' motor lead',_rounded_route([V(*p) for p in points],.6,.23),'Wiring',0,'red' if i else 'black',True)
    for i,x in enumerate([-105,-98]):
        for key,z,t in [('PSUCover',23.3,1.1),('LowerShield',28.5,1.1),('MainPCB',32.8,2.1)]:
            m.cut(key,m.rr(4,2.5,t,(x,126,z),.2),'Low-voltage bus passage '+str(i)).Refine=False
        m.box('DCBus'+str(i),'Power-to-mainboard bus bar study',3,1.5,20.9,(x,126,14.9),'Power',0,'copper',.15,True)
        guide=m.rr(5,4,3.5,(x,126,34.8),.3).cut(m.rr(3.5,2,4,(x,126,34.6),.2))
        m.feature('DCGuide'+str(i),'Mainboard power bus insulating guide',guide,'Mainboard',1,'black',True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=13
    m.checkpoint(13,'blower_motor_harnesses_and_power_bus_passages','建立风扇三线、光驱两组电机线束、独立插座接点及主板供电铜排，并加工所有对应壳体和板料穿越通道。端子、走线和供电结构均为静态学习示意。')
    m.snapshot('13_wiring_review',assemblies=['Wiring','Power','Mainboard'],exclude=['PSUCover'],normal=(.2,-.5,2))


STAGES[13]=stage13


def stage14(m):
    from .ps1 import _add_shape
    m.native('HDDBayRail','Hard-drive bay retaining support rail',85,10,.5,.6,(-90,-19,40.8),'Frame',2,'metal')
    _add_shape(m,'HDDCaddySide1',m.rr(12,8,.8,(-50,-23,46.8),.4),'Integral hard-drive tray retaining ear').Refine=False
    m.cut('HDDCaddySide1',Part.makeCylinder(1.3,1.2,V(-50,-23,46.6)),'Single tray retaining screw bore').Refine=False
    m.ring('HDDRetainerPost','Drive tray anchor spacer',2.5,.85,5.2,(-50,-23,41.45),'Frame',2,'metal',internal=True)
    m.screw('HDDRetainerScrew',(-50,-23,48.1),'Storage',4,length=5,radius=1.5,axis=(0,0,-1))
    for key,x,w,count in [('Data',-104,14,7),('Power',-80,25,15)]:
        m.cut('HDDBayRail',m.rr(w+3,9,1,(x,-21.8,40.6),.3),'SATA host connector bay relief').Refine=False
        outer=m.rr(w+2.5,8,5.3,(x,-21.8,39.5),.4)
        pocket=m.rr(w+.8,10,3.2,(x,-23.6,40.6),.2)
        terminal_cuts=[];rail_cuts=[];shield_cuts=[]
        for i in range(count):
            xx=x+(i-(count-1)/2)*1.25
            terminal_cuts.append(Part.makeBox(.65,4,.45,V(xx-.325,-20,43.4)))
            rail_cuts.append(Part.makeBox(.65,.65,1,V(xx-.325,-15.525,40.6)))
            shield_cuts.append(Part.makeBox(.65,.65,1,V(xx-.325,-15.525,42.8)))
            finger=Part.makeBox(.30,13.5,.12,V(xx-.15,-28.5,43.57))
            leg=Part.makeBox(.30,.30,8.97,V(xx-.15,-15.35,34.7))
            m.feature('SATAHost'+key+'Contact'+str(i),'SATA host contact and board leg',finger.fuse(leg),'Mainboard',1,'gold',True)
            m.box('SATAHost'+key+'Pad'+str(i),'SATA motherboard solder pad',.65,1.3,.05,(xx,-15.2,34.62),'Mainboard',0,'gold',.04,True)
        m.feature('SATAHost'+key+'Body','SATA host keyed socket study',outer.cut(pocket).cut(Part.makeCompound(terminal_cuts)),'Mainboard',2,'black',True)
        m.cut('HDDBayRail',rail_cuts,'SATA contact legs through bay rail').Refine=False
        m.cut('UpperShield',shield_cuts,'SATA contact legs through upper shield').Refine=False
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=14
    m.checkpoint(14,'hard_drive_retainer_and_sata_host_contacts','补齐硬盘托架单颗固定螺钉、支承轨和主板侧 SATA 数据与供电插座，加入独立接点、焊盘及金属板穿越通道。保留 7/15 接点分组，局部构造与安装高度为学习近似。')
    m.snapshot('14_hard_drive_connection_review',assemblies=['Storage','Mainboard','Frame'],normal=(.2,-.5,2))


STAGES[14]=stage14


def stage15(m):
    import math
    from .ps1 import _add_shape
    # Original family has four rear security fasteners; local boss locations are estimates.
    for i,(x,z,case) in enumerate([(-132,12,'LowerHousing'),(0,12,'LowerHousing'),(132,12,'LowerHousing'),(-40,39,'UpperHousing')]):
        rear=134.5+z*SLOPE
        boss=Part.makeCylinder(3.1,5.8,V(x,rear-5.8,z),V(0,1,0))
        _add_shape(m,case,boss,'Integral rear fixing boss '+str(i)).Refine=False
        holes=[Part.makeCylinder(1.0,8,V(x,rear-7,z),V(0,1,0)),Part.makeCylinder(2.15,1.6,V(x,rear-1.2,z),V(0,1,0))]
        m.cut(case,holes,'Rear security screw pilot and counterbore '+str(i)).Refine=False
        if case=='LowerHousing':
            m.cut('PSUCase',Part.makeCylinder(1.1,8,V(x,rear-7,z),V(0,1,0)),'Rear fixing clearance '+str(i)).Refine=False
        head=Part.makeCylinder(1.9,.6,V(x,rear-.5,z),V(0,-1,0))
        shaft=Part.makeCylinder(.8,5.8,V(x,rear-1.0,z),V(0,-1,0))
        lobes=[Part.makeCylinder(.28,.28,V(x+.52*math.cos(j*math.pi/3),rear-.48,z+.52*math.sin(j*math.pi/3)),V(0,-1,0)) for j in range(6)]
        recess=Part.makeCylinder(.56,.28,V(x,rear-.48,z),V(0,-1,0)).multiFuse(lobes)
        pin=Part.makeCylinder(.12,.28,V(x,rear-.48,z),V(0,-1,0))
        m.feature('RearSecurityScrew'+str(i),'Six-lobe security rear case screw study',head.fuse(shaft).cut(recess.cut(pin)),'Body',-3,'metal',True)
    g.appearance(m.parts['FrontSony'],m.colors['white']);m.parts['FrontSony'].MaterialDescription='white'
    bottom=g.rotation((0,0,-1),(0,1,0))
    m.box('BottomStudyLabel','Original-family study identification',94,26,.045,(0,5,1.46),'Body',-6,'black',.7,orient=bottom)
    m.label('BottomModelMark','CUH-1000A / CAD STUDY',2.0,(34,1,1.395),'Body',-6,'white',rotation=bottom)
    m.label('BottomStudyMark','OPEN CONSOLE CAD',1.8,(29,9,1.395),'Body',-6,'white',rotation=bottom)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=15
    m.checkpoint(15,'rear_security_fixings_and_study_identification','加入四组后部防拆螺钉、原生壳体连接柱、导孔与沉孔；修正前部 SONY 标识颜色并补齐明确标为 CAD STUDY 的底部型号标签。固定柱位置和螺纹为近似结构示意。')
    m.snapshot('15_rear_fixing_review',normal=(-.3,1,.5))


STAGES[15]=stage15


def _ds4_point(x,y,z):
    return V(x,y-245,z)


def _ds4_curves(sx,sy):
    points=[(0,42),(33,42),(48,44),(64,39),(81,17),(78,-9),(73,-42),(62,-54),(49,-44),(35,-19),(19,-11),(0,-11)]
    tangents=[(1,0),(1,0),(1,0),(1,-.5),(0,-1),(-.15,-1),(-.3,-1),(-1,0),(-.65,.8),(-.6,.8),(-1,0),(-1,0)]
    nodes=[V(x,y,0) for x,y in points];directions=[V(x,y,0).normalize() for x,y in tangents]
    lengths=[]
    for i,p in enumerate(nodes):
        before=(p-nodes[i-1]).Length if i else (nodes[1]-p).Length
        after=(nodes[i+1]-p).Length if i+1<len(nodes) else before
        lengths.append(.32*min(before,after))
    segments=[]
    for i in range(len(nodes)-1):
        a,b=nodes[i],nodes[i+1];segments.append([a,a+directions[i]*lengths[i],b-directions[i+1]*lengths[i+1],b])
    segments += [[V(-p.x,p.y,0) for p in reversed(poles)] for poles in reversed(segments)]
    curves=[]
    for poles in segments:
        curve=Part.BezierCurve();curve.setPoles([V(p.x*sx,p.y*sy,0) for p in poles]);curves.append(curve.toBSpline())
    return curves


def _ds4_loft(m,key,profiles):
    sketches=[]
    for i,(sx,sy,z) in enumerate(profiles):
        sk=m.doc.addObject('Sketcher::SketchObject',key+'Profile'+str(i));sk.Label='DualShock 4 editable shell section '+str(i+1)
        for curve in _ds4_curves(sx,sy):sk.addGeometry(curve,False)
        sk.Placement=App.Placement(_ds4_point(0,0,z),App.Rotation());m.group('Construction').addObject(sk);sketches.append(sk)
    loft=m.doc.addObject('Part::Loft',key);loft.Sections=sketches;loft.Solid=True;loft.Ruled=False;loft.Closed=False;loft.MaxDegree=3
    m.doc.recompute();assert loft.Shape.isValid() and len(loft.Shape.Solids)==1 and loft.Shape.Volume>0;loft.Shape.check(True)
    m.group('Construction').addObject(loft)
    for sk in sketches:sk.Visibility=False
    loft.Visibility=False;return loft


def _ds4_shell(m,key,outer,inner,layer):
    a=_ds4_loft(m,key+'Outer',outer);b=_ds4_loft(m,key+'Inner',inner)
    obj=m.doc.addObject('Part::Cut',key);obj.Base=a;obj.Tool=b;obj.Refine=False
    m.doc.recompute();assert obj.Shape.isValid() and len(obj.Shape.Solids)==1 and obj.Shape.Volume>0;obj.Shape.check(True)
    a.Visibility=False;b.Visibility=False
    return m.register(obj,key,'Controller',layer,'ps4matte')


def stage16(m):
    from .ps1 import _add_shape
    _ds4_shell(m,'DS4Back',[(.88,.88,1),(.96,.96,7),(1,1,16),(1,1,22)],[(.84,.84,3),(.925,.925,8),(.971,.97,16),(.971,.97,22.3)],-4)
    _ds4_shell(m,'DS4Front',[(1,1,22.3),(.99,.99,29),(.955,.955,35)],[(.971,.97,22.1),(.954,.951,29),(.929,.925,32.8)],4)
    front=[];back=[];inner_front=[];inner_back=[];openings=[]
    for side in [-1,1]:
        x=side*27
        back.append(Part.makeCylinder(16.2,13,_ds4_point(x,-17,9)))
        front.append(Part.makeCylinder(16.2,16.2,_ds4_point(x,-17,22.3)))
        inner_back.append(Part.makeCylinder(14.5,11.4,_ds4_point(x,-17,10.8)))
        inner_front.append(Part.makeCylinder(14.5,14.2,_ds4_point(x,-17,22.1)))
        openings.append(Part.makeCylinder(11.6,3,_ds4_point(x,-17,36.2)))
        face=Part.makeCylinder(22.2,2.4,_ds4_point(side*51,15,34.6))
        face=face.makeFillet(.6,[e for e in face.Edges if e.BoundBox.ZLength<1e-7 and e.BoundBox.ZMax>36.9]);front.append(face)
    _add_shape(m,'DS4Back',Part.makeCompound(back),'Integrated lower stick pods').Refine=False
    m.cut('DS4Back',inner_back,'Hollow lower stick pods').Refine=False
    _add_shape(m,'DS4Front',front[0].multiFuse(front[1:]).removeSplitter(),'Integrated upper stick pods and round control faces').Refine=False
    m.cut('DS4Front',inner_front+openings,'Upper stick cavities and through openings').Refine=False
    m.cut('DS4Front',m.rr(58,31,10,tuple(_ds4_point(0,22,30)),3),'Original touchpad aperture').Refine=False
    m.doc.recompute()
    for key in ['DS4Front','DS4Back']:assert len(m.parts[key].Shape.Solids)==1,key
    m.profile['stages']=16
    m.checkpoint(16,'dualshock4_native_lofted_shell_and_stick_pods','建立初代 DualShock 4 原生可编辑上下曲面壳、双握柄、圆形控制面、摇杆杯与触摸板开口；轮廓和壳厚采用照片指导的近似。')
    m.snapshot('16_dualshock4_shell_review',assemblies=['Controller'],normal=(.2,-.5,2))


STAGES[16]=stage16


def stage17(m):
    from .ps1 import _add_shape
    from .ps2 import _ds2_symbol
    m.colors.update(ds4pink=(.78,.37,.54),ds4green=(.25,.65,.53),ds4red=(.82,.28,.32),ds4cyan=(.34,.58,.77),ds4rubber=(.075,.078,.085))
    # Separate button apertures retain the central web of the directional control.
    dpad=[(-51,25),(-61,15),(-51,5),(-41,15)]
    m.cut('DS4Front',m.rr(26,26,3.4,tuple(_ds4_point(-51,15,31.5)),2),'Underside directional rocker clearance').Refine=False
    cap_shapes=[]
    for i,(x,y) in enumerate(dpad):
        w,h=(6.8,8.6) if i in [0,2] else (8.6,6.8)
        m.cut('DS4Front',m.rr(w+.45,h+.45,8,tuple(_ds4_point(x,y,32)),1.1),'Directional key aperture '+str(i)).Refine=False
        cap_shapes.append(m.rr(w,h,5.6,tuple(_ds4_point(x,y,33.8)),.9))
    link=m.rr(23,5,.8,tuple(_ds4_point(-51,15,33.2)),.5).fuse(m.rr(5,23,.8,tuple(_ds4_point(-51,15,33.2)),.5))
    m.feature('DS4DPad','Four-key linked directional rocker',link.multiFuse(cap_shapes),'Controller',5,'black')
    for kind,x,y,material in [('Triangle',51,25,'ds4green'),('Circle',61,15,'ds4red'),('Cross',51,5,'ds4cyan'),('Square',41,15,'ds4pink')]:
        m.cut('DS4Front',Part.makeCylinder(5.2,8,_ds4_point(x,y,32)),'Face button '+kind+' through bore').Refine=False
        m.cut('DS4Front',Part.makeCylinder(6.4,3,_ds4_point(x,y,32)),'Face button '+kind+' retaining-flange relief').Refine=False
        cap=Part.makeCylinder(4.95,5.4,_ds4_point(x,y,33.8)).fuse(Part.makeCylinder(6.15,.6,_ds4_point(x,y,33.7)))
        m.feature('DS4Button'+kind,kind+' action button with retaining flange',cap,'Controller',5,'black')
        _ds2_symbol(m,'DS4Symbol'+kind,kind,x,y-5,39.22,material)
    m.box('DS4Touchpad','Original opaque capacitive touchpad cover',57.4,30.4,2.2,tuple(_ds4_point(0,22,34.2)),'Controller',5,'black',2.8)
    m.native('DS4TouchPCB','Native touch-sensing circuit plate',53,26,1.8,.7,tuple(_ds4_point(0,22,32.7)),'Controller',3,'pcb')
    for name,x in [('Share',-34),('Options',34)]:
        m.cut('DS4Front',m.rr(3.3,9.6,7,tuple(_ds4_point(x,27,31)),1.2),name+' aperture').Refine=False
        m.box('DS4'+name,name.upper()+' slim key',2.8,9.1,3.7,tuple(_ds4_point(x,27,33.8)),'Controller',5,'black',1.1)
    m.cut('DS4Front',Part.makeCylinder(4.8,8,_ds4_point(0,-5,30)),'Central PS button aperture').Refine=False
    m.cyl('DS4PSButton','Central system button',4.5,4,tuple(_ds4_point(0,-5,33.5)),'Controller',5,'black')
    m.label('DS4PSMark','PS',2.1,tuple(_ds4_point(-1.9,-6,37.525)),'Controller',6,'white')
    speaker_holes=[Part.makeCylinder(.65,7,_ds4_point(x,y,30)) for x in [-6,-3,0,3,6] for y in [1,3.5,6]]
    m.cut('DS4Front',speaker_holes,'Fifteen open loudspeaker grille holes').Refine=False
    for i,x in enumerate([-27,27]):
        center=_ds4_point(x,-17,40)
        dome=Part.makeSphere(11.2,center).common(Part.makeBox(25,25,9.2,_ds4_point(x-12.5,-29.5,39.2)))
        stem=Part.makeCylinder(2.2,14,_ds4_point(x,-17,26))
        m.feature('DS4StickDome'+str(i),'Analogue stick dome and keyed shaft study',dome.fuse(stem),'Controller',5,'black')
        cap=Part.makeCylinder(10.5,3.5,_ds4_point(x,-17,48.5)).cut(Part.makeSphere(11,_ds4_point(x,-17,61.7)))
        m.feature('DS4StickCap'+str(i),'Concave rubber analogue thumb cap',cap,'Controller',6,'ds4rubber')
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=17
    m.checkpoint(17,'dualshock4_touchpad_face_controls_and_concave_sticks','补齐初代不透光触摸板与原生感应板、独立方向键、四枚带符号按键、SHARE / OPTIONS、PS 键、真实扬声器开孔和凹面摇杆帽。')
    m.snapshot('17_dualshock4_controls_review',assemblies=['Controller'],normal=(.2,-.5,2))


STAGES[17]=stage17


def _ds4_joystick(m,index,x,y):
    from .atari2600 import _helical_spring
    key='DS4Joy'+str(index);y-=245;holes=[]
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



def stage18(m):
    from .ps1 import _add_shape
    m.colors.update(ds4pcb=(.075,.19,.32),ctrlcream=(.7,.72,.69))
    m.native('DS4PCB','Native first-generation JDM-001 layout study',108,47,.8,1,tuple(_ds4_point(0,13,19)),'Controller',0,'ds4pcb')
    wings=[Part.makeCylinder(14,1,_ds4_point(x,-17,19)) for x in [-27,27]]
    _add_shape(m,'DS4PCB',Part.makeCompound(wings),'Integral analogue-module board lobes').Refine=False
    for key,x,y,w,h in [('MCU',0,21,9,9),('Wireless',-19,20,7,7),('Motion',16,21,5,5),('Audio',-6,5,5,4),('MotorDriver',32,16,5,5)]:
        m.box('DS4'+key,key+' package study',w,h,1.0,tuple(_ds4_point(x,y,20.2)),'Controller',1,'black',.15,True)
    for i,x in enumerate([-38,-31,-24,-17,17,24,31,38]):
        m.box('DS4Bypass'+str(i),'Controller bypass capacitor study',1.8,.9,.65,tuple(_ds4_point(x,32,20.2)),'Controller',1,'metal',.08,True)
    m.box('DS4Crystal','Controller oscillator package study',3.6,2.6,.8,tuple(_ds4_point(8,21,20.2)),'Controller',1,'metal',.2,True)
    holes=[]
    for i,x in enumerate([-27,27]):
        before=set(m.parts)
        bores=_ds4_joystick(m,i,x,-17)
        for key in set(m.parts)-before:
            obj=m.parts[key];place=obj.Placement;place.Base+=V(0,0,6.2);obj.Placement=place;obj.FlatPlacement=place
        for tool in bores:tool.translate(V(0,0,6.2));holes.append(tool)
        m.cut('DS4StickDome'+str(i),[Part.makeCylinder(2.5,4.8,_ds4_point(x,-17,25.8)),Part.makeCylinder(1.9,6,_ds4_point(x,-17,30.4))],'Joystick shaft and pivot clearance').Refine=False
    m.cut('DS4PCB',holes,'Analogue module anchor and electrical pin bores').Refine=False
    for i,(x,y) in enumerate([(-45,7),(45,7),(0,35)]):
        m.cut('DS4PCB',Part.makeCylinder(1.0,1.5,_ds4_point(x,y,18.8)),'Controller board mount '+str(i)).Refine=False
        m.ring('DS4BoardGround'+str(i),'Controller board mounting ground',2,1.1,.05,tuple(_ds4_point(x,y,20.02)),'Controller',0,'gold',internal=True)
        m.ring('DS4BoardPost'+str(i),'Controller board mounting spacer',2,.8,5.5,tuple(_ds4_point(x,y,13.4)),'Controller',-1,'ctrlcream',internal=True)
        m.screw('DS4BoardScrew'+str(i),tuple(_ds4_point(x,y,21)),'Controller',1,length=5,radius=1.5,axis=(0,0,-1))
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=18
    m.checkpoint(18,'dualshock4_native_board_two_axis_gimbals_and_electronics','补齐初代 JDM-001 布局指导的原生主板、主要逻辑封装、两组金属摇杆笼、双轴支架、电位器、L3/R3 开关及真实穿板端子与固定件。电气结构为非功能性示意。')
    m.snapshot('18_dualshock4_board_review',assemblies=['Controller'],exclude=['DS4Front','DS4Back','DS4Touchpad','DS4TouchPCB','DS4DPad','DS4StickDome0','DS4StickDome1','DS4StickCap0','DS4StickCap1'],normal=(.2,-.5,2))


STAGES[18]=stage18


def stage19(m):
    m.colors.update(ds4flex=(.12,.33,.17),ds4silicone=(.57,.61,.63))
    carrier=m.rr(114,14,1.6,tuple(_ds4_point(0,15,27.8)),1)
    film=m.rr(112,12,.12,tuple(_ds4_point(0,15,29.5)),.7)
    for x in [-51,51]:
        carrier=carrier.fuse(Part.makeCylinder(20,1.6,_ds4_point(x,15,27.8)))
        film=film.fuse(Part.makeCylinder(18.7,.12,_ds4_point(x,15,29.5)))
    carrier=carrier.fuse(m.rr(20,19,1.6,tuple(_ds4_point(0,1.5,27.8)),1))
    film=film.fuse(m.rr(18,18,.12,tuple(_ds4_point(0,1.5,29.5)),.7))
    speaker_passage=m.rr(15,7,2.4,tuple(_ds4_point(0,3.5,27.5)),1)
    carrier=carrier.cut(speaker_passage);film=film.cut(speaker_passage)
    m.feature('DS4ControlCarrier','Moulded button-film support carrier study',carrier,'Controller',2,'ctrlcream',True)
    m.feature('DS4ControlFilm','Flexible directional and action contact film',film,'Controller',3,'ds4flex',True)
    groups=[('Directional',-51,15,[(-51,25),(-61,15),(-51,5),(-41,15)]),('Action',51,15,[(51,25),(61,15),(51,5),(41,15)]),('System',0,-5,[(0,-5)])]
    for name,cx,cy,keys in groups:
        membrane=Part.makeCylinder(17.8 if len(keys)>1 else 4.4,.6,_ds4_point(cx,cy,29.9))
        for i,(x,y) in enumerate(keys):
            membrane=membrane.cut(Part.makeCylinder(3.4,.9,_ds4_point(x,y,29.75)))
            dome=Part.makeCone(4.0,2.6,2.6,_ds4_point(x,y,30.5)).cut(Part.makeCone(3.5,2.15,2.25,_ds4_point(x,y,30.45)))
            membrane=membrane.fuse(dome)
            m.cyl('DS4'+name+'Carbon'+str(i),'Moving carbon contact pill',1.8,.15,tuple(_ds4_point(x,y,32.52)),'Controller',4,'black',internal=True)
            fixed=Part.makeCylinder(2.5,.05,_ds4_point(x,y,29.65)).cut(Part.makeBox(.3,6,.15,_ds4_point(x-.15,y-3,29.6)))
            m.feature('DS4'+name+'Fixed'+str(i),'Split fixed conductive film contact',fixed,'Controller',3,'black',True)
        m.feature('DS4'+name+'Membrane','Hollow silicone return dome membrane',membrane,'Controller',4,'ds4silicone',True)
    for name,x in [('Share',-34),('Options',34)]:
        m.box('DS4'+name+'Switch','Small tactile switch body',3.6,5.5,2.0,tuple(_ds4_point(x,27,30.3)),'Controller',3,'black',.3,True)
        m.box('DS4'+name+'Actuator','Small tactile switch actuator',1.8,3.4,1.3,tuple(_ds4_point(x,27,32.4)),'Controller',4,'ctrlcream',.25,True)
    speaker=m.rr(14,6,2.4,tuple(_ds4_point(0,3.5,30)),1).cut(m.rr(12,4,2,tuple(_ds4_point(0,3.5,30.7)),.7))
    m.feature('DS4SpeakerFrame','Controller loudspeaker basket',speaker,'Controller',3,'metal',True)
    m.box('DS4SpeakerMagnet','Loudspeaker magnetic circuit',10,3.4,.6,tuple(_ds4_point(0,3.5,30.75)),'Controller',3,'black',.6,True)
    m.box('DS4SpeakerDiaphragm','Thin loudspeaker diaphragm',11.8,3.8,.08,tuple(_ds4_point(0,3.5,32.3)),'Controller',4,'black',.6,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=19
    m.checkpoint(19,'dualshock4_contact_film_return_membranes_and_loudspeaker','补齐控制膜支架、独立柔性接点膜、空心硅胶回弹穹顶和碳粒、SHARE / OPTIONS 轻触开关及扬声器篮架、磁路与振膜。保持静态未按下的接点间隙。')
    m.snapshot('19_dualshock4_membranes_review',assemblies=['Controller'],exclude=['DS4Front','DS4Back','DS4Touchpad','DS4TouchPCB','DS4DPad','DS4StickDome0','DS4StickDome1','DS4StickCap0','DS4StickCap1'],normal=(.2,-.5,2))


STAGES[19]=stage19


def stage20(m):
    from .atari2600 import _helical_spring
    m.cut('DS4Back',m.rr(108.6,47.6,1.5,tuple(_ds4_point(0,13,18.8)),.7),'Mainboard edge passages across the lower stick cups').Refine=False
    for side,name in [(-1,'L'),(1,'R')]:
        x=side*51
        cavity=m.rr(28,15,33,tuple(_ds4_point(x,38,10.5)),1)
        for key in ['DS4Front','DS4Back']:m.cut(key,cavity,'Two-tier shoulder key bay '+name).Refine=False
        m.cut('DS4PCB',m.rr(28,12,1.5,tuple(_ds4_point(x,38,18.8)),.5),'Trigger mechanism board relief '+name).Refine=False
        for key in ['DS4ControlCarrier','DS4ControlFilm']:
            m.cut(key,m.rr(26,10,3,tuple(_ds4_point(x,37,27.5)),.5),'Trigger travel clearance '+name).Refine=False
        m.box('DS4'+name+'1',name+'1 shoulder key',22,8,5.7,tuple(_ds4_point(x,40,35)),'Controller',5,'black',1.8)
        m.label('DS4'+name+'1Mark',name+'1',2.5,tuple(_ds4_point(x-2,38.5,40.725)),'Controller',6,'white')
        yz=[(33,30),(43,30),(44,25),(43,15),(38,12),(34,16)]
        hollow=[(34.6,28.5),(41.5,28.5),(42.4,24.8),(41.5,16),(38,14),(35.5,17)]
        trigger=_prism_yz([(y-245,z) for y,z in yz],x-11,22)
        trigger=trigger.cut(_prism_yz([(y-245,z) for y,z in hollow],x-9.5,19))
        trigger=trigger.cut(Part.makeCylinder(1.3,23,_ds4_point(x-11.5,36,24),V(1,0,0)))
        trigger=trigger.cut(Part.makeCylinder(2.1,5,_ds4_point(x-2.5,36,24),V(1,0,0)))
        m.feature('DS4'+name+'2',name+'2 hollow hinged trigger study',trigger,'Controller',4,'black')
        m.cyl('DS4'+name+'2Pin','Trigger pivot axle',1.0,26,tuple(_ds4_point(x-13,36,24)),'Controller',3,'metal',axis=(1,0,0),internal=True)
        for j,dx in enumerate([-12.8,11.4]):
            m.ring('DS4'+name+'2Bearing'+str(j),'Trigger pivot support study',2.2,1.15,1.4,tuple(_ds4_point(x+dx,36,24)),'Controller',2,'ctrlcream',axis=(1,0,0),internal=True)
        spring=_helical_spring(1.6,.42,3.5,.16);spring.Placement=App.Placement(_ds4_point(x-1.75,36,24),App.Rotation(V(0,0,1),V(1,0,0)))
        m.feature('DS4'+name+'2Spring','Trigger torsion return spring coil study',spring,'Controller',3,'metal',True)
        m.box('DS4'+name+'1Switch','Shoulder button contact housing',8,3.5,2,tuple(_ds4_point(x,33,31)),'Controller',3,'black',.4,True)
        m.cyl('DS4'+name+'1Actuator','Shoulder button actuator',1.2,1.5,tuple(_ds4_point(x,33,33.2)),'Controller',4,'ds4silicone',internal=True)
        m.box('DS4'+name+'2Switch','Trigger pressure-contact housing study',7,3,1.5,tuple(_ds4_point(x,29,26)),'Controller',3,'black',.4,True)
        m.cyl('DS4'+name+'2Actuator','Trigger pressure actuator study',1.2,2.3,tuple(_ds4_point(x,30.6,26.5)),'Controller',4,'ds4silicone',axis=(0,1,0),internal=True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=20
    m.checkpoint(20,'dualshock4_shoulder_buttons_hinged_triggers_and_springs','建立双层 L1/R1 肩键、空心 L2/R2 扳机、转轴、轴承、扭簧线圈与接点机构，并加工上下壳和主板的对应避让。扳机局部截面与弹簧为静态结构近似。')
    m.snapshot('20_dualshock4_trigger_review',assemblies=['Controller'],exclude=['DS4Back'],normal=(-.3,1,1.1))


STAGES[20]=stage20


def stage21(m):
    from .atari2600 import _rounded_route
    from .ps1 import _add_shape
    _add_shape(m,'DS4PCB',Part.makeCompound([m.rr(15,8,1,tuple(_ds4_point(x,-7,19)),.6) for x in [-57,57]]),'Integral motor connection board wings').Refine=False
    carrier=m.rr(42,33,1.5,tuple(_ds4_point(0,16,5.6)),1.2)
    walls=[m.rr(1.1,33,9.3,tuple(_ds4_point(x,16,7.1)),.25) for x in [-20.4,20.4]]
    walls += [m.rr(40,1,9.3,tuple(_ds4_point(0,y,7.1)),.25) for y in [0,32]]
    carrier=carrier.multiFuse(walls)
    carrier=carrier.cut(Part.makeCompound([Part.makeCylinder(.5,3,_ds4_point(-22,y,12),V(1,0,0)) for y in [14,16]]))
    m.feature('DS4BatteryCarrier','Central moulded battery cradle',carrier,'Controller',-2,'black',True)
    m.box('DS4Battery','Original 3.7 V 1000 mAh battery envelope study',38,28,8.3,tuple(_ds4_point(0,16,7.4)),'Controller',-1,'battery',1.3,True)
    m.label('DS4BatteryMark','3.7 V / 1000 mAh',1.4,tuple(_ds4_point(-15,15,15.725)),'Controller',0,'white')
    body=m.rr(4,5,3.2,tuple(_ds4_point(-36,15,20.25)),.3)
    for i,y in enumerate([14,16]):
        x=-35.5-i
        bore=Part.makeCylinder(.5,3.6,_ds4_point(x,y,20.1));body=body.cut(bore)
        m.cut('DS4PCB',Part.makeCylinder(.5,1.5,_ds4_point(x,y,18.8)),'Battery lead board passage '+str(i)).Refine=False
        m.ring('DS4BatteryContact'+str(i),'Battery connector terminal sleeve',.4,.25,2.7,tuple(_ds4_point(x,y,20.25)),'Controller',1,'metal',internal=True)
        path=[_ds4_point(-19.25,y,12),_ds4_point(x,y,12),_ds4_point(x,y,21.8)]
        m.feature('DS4BatteryLead'+str(i),'Routed battery lead',_rounded_route(path,.6,.20),'Controller',0,'red' if i else 'black',True)
    m.feature('DS4BatteryHeader','Two-position battery socket study',body,'Controller',1,'white',True)
    for i,(x,radius) in enumerate([(-59,8.2),(59,6.2)]):
        key='DS4Rumble'+str(i);axis=V(0,-1,0)
        def point(y):return _ds4_point(x,y,13.5)
        can=Part.makeCylinder(radius,17,point(-13),axis).cut(Part.makeCylinder(radius-.6,17.4,point(-12.8),axis))
        m.feature(key+'Can','Unequal rumble motor can',can,'Controller',-1,'metal',True)
        for name,y in [('Front',-12.7),('Rear',-30.05)]:
            cap=Part.makeCylinder(radius-.05,.25,point(y),axis).cut(Part.makeCylinder(1.0,.5,point(y+.1),axis))
            m.feature(key+name+'Cap','Motor bearing end cap',cap,'Controller',-1,'metal',True)
        m.cyl(key+'Shaft','Rumble motor shaft',.8,26,tuple(point(-11)),'Controller',-1,'metal',axis=(0,-1,0),internal=True)
        m.ring(key+'Magnet','Motor stator magnet study',radius-.85,radius-2.0,14,tuple(point(-14)),'Controller',-1,'black',axis=(0,-1,0),internal=True)
        m.ring(key+'Rotor','Motor armature study',radius-2.3,1.0,10,tuple(point(-16)),'Controller',-1,'copper',axis=(0,-1,0),internal=True)
        weight=Part.makeCylinder(radius,4,point(-32),axis).cut(Part.makeCylinder(1.0,4.4,point(-31.8),axis))
        weight=weight.cut(Part.makeBox(radius*2+2,5,radius+1,_ds4_point(x-radius-1,-36.5,13.5)))
        m.feature(key+'Weight','Eccentric rumble counterweight',weight,'Controller',-1,'metal',True)
        saddle=Part.makeCylinder(radius+1.2,9,point(-17),axis).cut(Part.makeCylinder(radius+.2,9.4,point(-16.8),axis))
        saddle=saddle.cut(Part.makeBox(radius*2+4,10,radius+2,_ds4_point(x-radius-2,-26.5,13.5)))
        m.feature(key+'Saddle','Lower grip motor saddle study',saddle,'Controller',-2,'ctrlcream',True)
        for j,dx in enumerate([-2,2]):
            path=[_ds4_point(x+dx,-12.5,13.5),_ds4_point(x+dx,-8,13.5),_ds4_point(x+dx,-8,20.4)]
            m.feature(key+'Lead'+str(j),'Rumble motor power lead study',_rounded_route(path,.6,.2),'Controller',0,'red' if j else 'black',True)
            m.cut('DS4PCB',Part.makeCylinder(.45,1.5,_ds4_point(x+dx,-8,18.8)),'Rumble lead board hole '+str(i)+' '+str(j)).Refine=False
            m.ring(key+'Pad'+str(j),'Rumble motor solder pad study',.7,.3,.05,tuple(_ds4_point(x+dx,-8,20.02)),'Controller',1,'gold',internal=True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=21
    m.checkpoint(21,'dualshock4_battery_cradle_and_unequal_rumble_motors','加入初代 3.7 V / 1000 mAh 电池近似包络、托架和两线接头，以及双握柄不同尺寸的振动电机、定转子示意、偏心重块、鞍座与引线。')
    m.snapshot('21_dualshock4_battery_motor_review',assemblies=['Controller'],exclude=['DS4Front','DS4Back'],normal=(.2,-.5,2))


STAGES[21]=stage21


def stage22(m):
    rear=g.rotation((0,1,0),(0,0,1));front=g.rotation((0,-1,0),(0,0,1))
    for key in ['DS4Back','DS4Front']:
        m.cut(key,m.rr(60,12.2,8,tuple(_ds4_point(0,38,18.5)),1,rear),'Original rear light-bar window').Refine=False
    lens=_keyed_rear_port(58,11,1.2,0,42-245,18.5,4)
    m.feature('DS4LightLens','Original rear light-bar lens',lens,'Controller',0,'ps4blue')
    guide=_keyed_rear_port(54,9.6,2.0,0,39.6-245,18.5,3)
    m.feature('DS4LightGuide','Rear status-light optical guide study',guide,'Controller',0,'white',True)
    m.native('DS4USBPCB','Native charging and light-bar daughterboard',36,9,.7,.8,tuple(_ds4_point(0,33,24.5)),'Controller',1,'ds4pcb')
    for i,x in enumerate([-14,0,14]):
        m.box('DS4StatusLED'+str(i),'Status LED package study',2.5,2,.8,tuple(_ds4_point(x,36,23.5)),'Controller',1,'white',.2,True)
    m.cut('DS4Front',m.rr(8.8,4,9,tuple(_ds4_point(0,36,29)),.5,rear),'Original Micro-USB charging port').Refine=False
    outer=_keyed_rear_port(8,3.3,5,0,37-245,29,.8)
    inner=_keyed_rear_port(7.4,2.7,5.4,0,36.8-245,29,.6)
    m.feature('DS4USBShield','Micro-USB stamped socket shield',outer.cut(inner),'Controller',2,'metal')
    m.box('DS4USBStop','Micro-USB insulating rear stop',6.8,.65,2.1,tuple(_ds4_point(0,37.4,27.95)),'Controller',1,'black',.15,True)
    m.box('DS4USBTongue','Micro-USB insulating tongue',6,3.6,.5,tuple(_ds4_point(0,40,28.7)),'Controller',2,'black',.1)
    for i in range(5):
        x=(i-2)*.65
        finger=Part.makeBox(.25,4.0,.1,_ds4_point(x-.125,36.5,29.3))
        leg=Part.makeBox(.25,.25,3.85,_ds4_point(x-.125,36.5,25.4))
        # Small vertical link joins the contact plane and board leg.
        link=Part.makeBox(.25,.25,.2,_ds4_point(x-.125,36.5,29.15))
        m.feature('DS4USBContact'+str(i),'Micro-USB contact and daughterboard leg',finger.multiFuse([leg,link]),'Controller',2,'gold',True)
        m.cut('DS4USBStop',Part.makeBox(.4,1,.3,_ds4_point(x-.2,36.9,29.2)),'Micro-USB contact passage '+str(i)).Refine=False
        m.box('DS4USBPad'+str(i),'Charging board solder pad',.4,1,.05,tuple(_ds4_point(x,36.6,25.32)),'Controller',1,'gold',.03,True)
    # The front headphone and extension sockets sit between the analogue pods.
    m.cut('DS4Back',m.rr(8,6.8,10,tuple(_ds4_point(7,-3,12)),.5,front),'Headset connector case opening').Refine=False
    body=m.rr(7.4,8,6,tuple(_ds4_point(7,-6.4,9)),.5)
    bore=Part.makeCylinder(1.85,9,_ds4_point(7,-2.2,12),V(0,-1,0))
    m.feature('DS4HeadsetBody','3.5 mm headset socket body',body.cut(bore),'Controller',0,'black',True)
    m.ring('DS4HeadsetRing','Headset socket mouth',2.8,1.85,.45,tuple(_ds4_point(7,-10.45,12)),'Controller',0,'metal',axis=(0,-1,0))
    for i,y in enumerate([-8.8,-6.8,-4.8,-3.1]):
        sh=Part.makeCylinder(2.05,.25,_ds4_point(7,y,12),V(0,-1,0)).cut(Part.makeCylinder(1.85,.45,_ds4_point(7,y+.1,12),V(0,-1,0)))
        m.feature('DS4HeadsetContact'+str(i),'Headset jack spring contact study',sh,'Controller',0,'metal',True)
        m.cut('DS4HeadsetBody',Part.makeCylinder(2.15,.4,_ds4_point(7,y+.075,12),V(0,-1,0)),'Headset internal contact seat '+str(i)).Refine=False
    m.cut('DS4Back',m.rr(9,4.8,9,tuple(_ds4_point(-5,-3,12)),.4,front),'Extension socket case aperture').Refine=False
    ext=m.rr(8.2,4,6,tuple(_ds4_point(-5,-4.8,12)),.35,front).cut(m.rr(7.5,3.3,6.4,tuple(_ds4_point(-5,-4.6,12)),.2,front))
    m.feature('DS4EXTShield','Original extension socket shell study',ext,'Controller',0,'metal')
    m.box('DS4EXTTongue','Extension connector insulating tongue',6.2,4,.65,tuple(_ds4_point(-5,-8.5,11.65)),'Controller',0,'black',.15)
    for i in range(8):
        m.box('DS4EXTContact'+str(i),'Extension socket contact study',.32,3,.08,tuple(_ds4_point(-5+(i-3.5)*.7,-8.5,12.4)),'Controller',0,'gold',.03,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=22
    m.checkpoint(22,'dualshock4_original_light_bar_micro_usb_headset_and_extension','补齐初代后部灯条与导光件、原生充电小板、Micro-USB 五接点插座、3.5 mm 耳机口和 EXT 扩展口。EXT 接点和内部电气连接采用示意，不声明实机针脚映射。')
    m.snapshot('22_dualshock4_rear_interfaces_review',assemblies=['Controller'],normal=(.3,1,1))


STAGES[22]=stage22


def _transform_new_parts(m,before,transform):
    for key in set(m.parts)-before:
        obj=m.parts[key];place=transform.multiply(obj.Placement);obj.Placement=place;obj.FlatPlacement=place


def stage23(m):
    from .ps2 import _flat_ribbon
    from .atari2600 import _rounded_route
    for key,y,z in [('DS4ChargeMain',28,20.25),('DS4ChargeDaughter',32,25.5)]:
        before=set(m.parts)
        _small_fpc(m,key,0,y-245,z,10,10,'Controller')
        rotation=App.Placement(V(),App.Rotation(V(0,0,1),180),_ds4_point(0,y,z))
        _transform_new_parts(m,before,rotation)
    path=[(27.7,21.05),(26,21.05),(26,27.5),(30,27.5),(30,26.3),(31.7,26.3)]
    m.feature('DS4ChargeRibbon','Charging and light-board flex cable study',_flat_ribbon([tuple(_ds4_point(0,y,z)) for y,z in path],6.0),'Controller',2,'white',True)
    _small_fpc(m,'DS4TouchMain',-22.5,25-245,20.25,8,8,'Controller')
    before=set(m.parts);_small_fpc(m,'DS4TouchEnd',0,0,0,8,8,'Controller')
    _transform_new_parts(m,before,App.Placement(_ds4_point(-22.5,22,32.45),App.Rotation(V(1,0,0),180)))
    path=[(25.3,21.05),(29,21.05),(29,30),(18,30),(18,31.65),(21.7,31.65)]
    m.feature('DS4TouchRibbon','Touch-sensor to mainboard folded flex study',_flat_ribbon([tuple(_ds4_point(-22.5,y,z)) for y,z in path],4.4),'Controller',2,'flex',True)
    _small_fpc(m,'DS4FilmMain',22,27-245,20.25,12,14,'Controller')
    path=[(21.4,29.56),(24,29.56),(24,22.5),(29,22.5),(29,21.05),(27.3,21.05)]
    m.feature('DS4FilmRibbon','Button contact film tail to mainboard study',_flat_ribbon([tuple(_ds4_point(22,y,z)) for y,z in path],8.8),'Controller',2,'ds4flex',True)
    for i,side in enumerate([-1,1]):
        x=side*9
        for key,z,h in [('DS4ControlCarrier',27.6,2),('DS4ControlFilm',29.4,.4),('DS4PCB',18.8,1.5)]:
            m.cut(key,Part.makeCylinder(.35,h,_ds4_point(x,-2,z)),'Speaker lead passage '+str(i)).Refine=False
        path=[_ds4_point(side*7.3,3.5,31.2),_ds4_point(x,3.5,31.2),_ds4_point(x,-2,31.2),_ds4_point(x,-2,20.1)]
        m.feature('DS4SpeakerLead'+str(i),'Loudspeaker lead study',_rounded_route(path,.55,.18),'Controller',2,'red' if i else 'black',True)
        m.ring('DS4SpeakerPad'+str(i),'Loudspeaker solder pad',.55,.3,.05,tuple(_ds4_point(x,-2,20.02)),'Controller',1,'gold',internal=True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=23
    m.checkpoint(23,'dualshock4_charging_touch_control_flexes_and_speaker_leads','建立充电小板、触摸板与按键接点膜的独立弯折排线及对应插座，并补齐扬声器引线与载体、接点膜和主板上的真实通道。排线针数与电气映射为非功能性学习示意。')
    m.snapshot('23_dualshock4_flexes_review',assemblies=['Controller'],exclude=['DS4Front','DS4Back','DS4Touchpad','DS4TouchPCB'],normal=(.3,-.5,2))


STAGES[23]=stage23


def stage24(m):
    from .ps1 import _add_shape
    mounts=[(-42,28),(42,28),(-61,-42),(61,-42)]
    posts=[Part.makeCylinder(2.3,30.3,_ds4_point(x,y,4.5)) for x,y in mounts]
    _add_shape(m,'DS4Front',Part.makeCompound(posts),'Four integral controller fixing pillars').Refine=False
    m.cut('DS4Front',[Part.makeCylinder(.85,29.5,_ds4_point(x,y,4.3)) for x,y in mounts],'Four blind controller screw pilots').Refine=False
    m.cut('DS4Back',[Part.makeCylinder(2.55,18.1,_ds4_point(x,y,4.3)) for x,y in mounts],'Controller pillar rear-shell clearance').Refine=False
    m.cut('DS4Back',[Part.makeCylinder(1.1,4,_ds4_point(x,y,.8)) for x,y in mounts]+[Part.makeCylinder(1.85,2.3,_ds4_point(x,y,.8)) for x,y in mounts],'Four rear fixing bores and recessed heads').Refine=False
    holes=[Part.makeCylinder(2.55,18,_ds4_point(x,y,18.5)) for x,y in mounts]
    for key in ['DS4PCB','DS4ControlCarrier','DS4ControlFilm','DS4DirectionalMembrane','DS4ActionMembrane']:
        m.cut(key,holes,'Controller fixing pillar passages').Refine=False
    for i,(x,y) in enumerate(mounts):
        m.screw('DS4CaseScrew'+str(i),tuple(_ds4_point(x,y,2.2)),'Controller',-5,length=30,radius=1.5)
    m.box('DS4TouchClickSwitch','Touchpad click-switch housing study',4,4,1.2,tuple(_ds4_point(0,18,30)),'Controller',3,'black',.4,True)
    m.cyl('DS4TouchClickActuator','Touchpad click-switch actuator',1,1.2,tuple(_ds4_point(0,18,31.35)),'Controller',4,'ctrlcream',internal=True)
    reverse=g.rotation((0,0,-1),(0,1,0))
    m.box('DS4ModelLabel','Controller model identification label',73,13,.035,tuple(_ds4_point(0,12,.965)),'Controller',-5,'black',.5,orient=reverse)
    m.label('DS4ModelMark','CUH-ZCT1 / CAD STUDY',2,tuple(_ds4_point(27,9,.90)),'Controller',-5,'white',rotation=reverse)
    m.label('DS4StudyMark','OPEN CONSOLE CAD',1.5,tuple(_ds4_point(22,15,.90)),'Controller',-5,'white',rotation=reverse)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    assert len(m.parts['DS4Front'].Shape.Solids)==1
    m.profile['stages']=24
    m.checkpoint(24,'dualshock4_four_case_fixings_touch_click_and_identification','补齐四组控制器壳体固定柱、后部沉孔与螺钉，贯穿主板、接点膜和胶膜的真实柱孔，以及触摸板按下开关和明确标识 CAD STUDY 的背面型号标签。')
    m.snapshot('24_dualshock4_complete_review',assemblies=['Controller'],normal=(.2,-.5,2))


STAGES[24]=stage24


def stage25(m):
    from .atari2600 import _rounded_route
    x,y=-83,73
    m.cyl('RTCBase','Coin-cell insulating support',11,.4,(x,y,34.85),'Mainboard',1,'black',internal=True)
    holder=Part.makeCylinder(11,3.8,V(x,y,35.25)).cut(Part.makeCylinder(10.2,4.2,V(x,y,35.05)))
    holder=holder.cut(m.rr(1.2,3,4.4,(x+10.6,y,35.05),.1))
    m.feature('RTCHolder','Open coin-cell retention ring study',holder,'Mainboard',2,'black',True)
    m.cyl('RTCCell','RTC backup coin-cell envelope study',10,3.2,(x,y,35.3),'Mainboard',2,'metal',internal=True)
    leg=Part.makeBox(.25,2.5,3.5,V(x+10.475,y-1.25,35.3))
    arm=Part.makeBox(2.8,2.5,.15,V(x+8,y-1.25,38.75))
    m.feature('RTCClip','Coin-cell retaining contact study',leg.fuse(arm),'Mainboard',3,'metal',True)
    m.label('RTCMark','RTC',2.2,(x-3,y-1,38.525),'Mainboard',3,'black')
    angled=g.rotation((0,-1,SLOPE),(0,0,1))
    for name,z,inset,endx,endy in [('Power',42,1.2,-39,-119),('Eject',13,2,-41,-120)]:
        yy=-152.5+z*SLOPE+inset
        m.box(name+'Sensor','Front capacitive electrode study',1.2,7,.12,(-46,yy,z),'Controls',1,'copper',.12,True,orient=angled)
        path=[V(-46,yy+.18,z),V(endx,-132,z)]
        if name=='Eject':path += [V(endx,-132,35.8),V(endx,endy,35.8)]
        else:path += [V(endx,endy,z)]
        path += [V(endx,endy,34.85)]
        m.feature(name+'SensorLead','Front control lead study',_rounded_route(path,.25,.15),'Wiring',0,'black',True)
        m.box(name+'SensorPad','Front-control board connection pad study',1,1,.05,(endx,endy,34.65),'Mainboard',1,'gold',.1,True)
    m.native('StatusPCB','Native top-status indicator strip board',1.1,16,.2,.5,(-46,-20,49.1),'Controls',3,'pcb')
    m.box('StatusLED','Top status LED package study',.8,1.2,.2,(-46,-20,49.65),'Controls',4,'white',.1,True)
    m.box('StatusGuide','Internal status-light guide study',.9,14,1.9,(-46,-20,49.85),'Controls',5,'white',.15,True)
    for i,(xx,yy) in enumerate([(-39,-20),(-40,-21)]):
        m.cut('UpperShield',Part.makeCylinder(.35,1,V(xx,yy,42.8)),'Status-light lead shield passage '+str(i)).Refine=False
        path=[V(xx,yy,34.85),V(xx,yy,48.9),V(-46,yy,48.9)]
        m.feature('StatusLead'+str(i),'Status-light board lead study',_rounded_route(path,.35,.08),'Wiring',0,'red' if i else 'black',True)
        m.box('StatusPad'+str(i),'Status-light mainboard pad study',.65,.65,.05,(xx,yy,34.65),'Mainboard',1,'gold',.08,True)
    for i,xx in enumerate([99.9,108.1]):
        path=[V(xx,131.2,12),V(xx,127,12),V(xx,127,8.5),V(xx,126,7.9)]
        m.feature('ACInputLead'+str(i),'AC inlet to power-board connection study',_rounded_route(path,.35,.25),'Wiring',-2,'white' if i else 'black',True)
        m.box('ACInputPad'+str(i),'Input power board solder pad study',1.4,1.4,.05,(xx,126,7.55),'Power',-2,'gold',.1,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=25
    m.checkpoint(25,'rtc_retention_front_touch_status_and_ac_connections','补齐主板 RTC 电池包络与卡座、前部电容触控电极和引线、顶灯原生小板与导光件，以及 AC 插座到电源板的结构示意连接。电气位置与走线均为近似，不构成电路设计。')
    m.snapshot('25_console_electrical_review',assemblies=['Mainboard','Controls','Wiring','Power'],exclude=['PSUCover'],normal=(.2,-.5,2))


STAGES[25]=stage25


def stage26(m):
    from .saturn import _yz_gear
    from .atari2600 import _rounded_route
    motor=Part.makeCylinder(5,14,V(-3,-113,15),V(1,0,0)).cut(Part.makeCylinder(.9,14.4,V(-3.2,-113,15),V(1,0,0)))
    m.feature('LoadingMotor','Media-loading drive motor envelope study',motor,'Optical',-2,'metal',True)
    m.cyl('LoadingMotorShaft','Loading motor output shaft',.6,10,(-12,-113,15),'Optical',-1,'metal',axis=(1,0,0),internal=True)
    m.parts['LoadingShaft'].Shape=Part.makeCylinder(.85,116,V(-124,-123,23.1),V(1,0,0))
    for i,(y,z,root,outer,teeth,bore) in enumerate([(-113,15,2.2,2.7,14,.9),(-117.2,19.1,2.5,3,16,.9),(-123,23.1,3.5,4,20,1.1)]):
        gear=_yz_gear(-11,y,z,root,outer,teeth,1.6)
        gear=gear.cut(Part.makeCylinder(bore,2,V(-11.2,y,z),V(1,0,0)))
        m.feature('LoadingGear'+str(i),'Loading drive gear study with static tip clearance',gear,'Optical',0,'white',True)
    m.cut('OpticalTray',Part.makeCylinder(4.3,2,V(-11.2,-123,23.1),V(1,0,0)),'Intake gear front-wall relief').Refine=False
    support=m.rr(3,5,11.9,(-7.6,-117.2,6.1),.4).fuse(Part.makeCylinder(1.6,3,V(-9.1,-117.2,19.1),V(1,0,0)))
    support=support.cut(Part.makeCylinder(.85,3.4,V(-9.3,-117.2,19.1),V(1,0,0)))
    m.feature('LoadingIdlerSupport','Loading idler pedestal and bearing',support,'Optical',-2,'black',True)
    m.cyl('LoadingIdlerPin','Loading idler axle',.6,6,(-11.6,-117.2,19.1),'Optical',-1,'metal',axis=(1,0,0),internal=True)
    body=m.rr(4.8,3,2.5,(8,-3.5,7.6),.2)
    for i,x in enumerate([7,9]):
        body=body.cut(Part.makeCylinder(.45,3.4,V(x,-5.2,8.6),V(0,1,0)))
        m.ring('LoadingContact'+str(i),'Loading motor connector terminal',.4,.26,2,(x,-4.5,8.6),'Optical',0,'metal',axis=(0,1,0),internal=True)
        yy=-14+2*i;xx=13+.6*i
        points=[V(11.2,-112-i,15),V(xx,-112-i,15),V(xx,yy,9.7),V(x,yy,9.7),V(x,-7,8.6),V(x,-3.8,8.6)]
        m.feature('LoadingLead'+str(i),'Loading motor routed lead study',_rounded_route(points,.35,.2),'Wiring',0,'red' if i else 'black',True)
        m.box('LoadingPad'+str(i),'Loading motor board pad study',.65,1.1,.05,(x,-2.1,7.35),'Optical',0,'gold',.05,True)
    m.feature('LoadingHeader','Two-position intake-motor connector study',body,'Optical',0,'white',True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=26
    m.checkpoint(26,'optical_loading_motor_gear_train_and_harness','补齐吸入滚轮驱动电机、输出轴、三级齿轮示意、惰轮支座与轴销，延伸滚轮轴并加工前壁齿轮避让；加入驱动板连接器与两根引线。齿形、传动比和运动均不作为实机设计或运动仿真。')
    m.snapshot('26_optical_loading_review',assemblies=['Optical','Wiring'],exclude=['DriveCover','DriveMedia','DriveClamp','DriveClampMagnet'],normal=(.2,-.5,2))


STAGES[26]=stage26


def stage27(m):
    from .atari2600 import _rounded_route
    from .wiiu import _hdmi_shape
    rear=g.rotation((0,1,0),(0,0,1))
    m.box('ACWallPlug','Two-flat-blade AC plug study',23,17,11,(220,100,0),'Accessories',0,'black',1.7)
    for i,x in enumerate([213.8,226.2]):m.box('ACWallBlade'+str(i),'Flat AC blade study',1.4,6.2,12.5,(x,100,11.1),'Accessories',0,'metal',.1)
    points=[V(220,91.3,5.5),V(220,55,5.5),V(320,55,8),V(320,20,8),V(292.2,20,8)]
    m.feature('ACCord','Mains cord display length',_rounded_route(points,7,1.8),'Accessories',0,'black')
    m.box('ACDeviceGrip','Figure-eight connector grip',24,12,10,(280,20,3),'Accessories',0,'black',1.3)
    lobes=[Part.makeCylinder(3.15,10,V(267.8,y,8),V(-1,0,0)) for y in [15.9,24.1]]
    bridge=Part.makeBox(1.2,8.2,5.4,V(266.6,15.9,5.3))
    head=bridge.multiFuse(lobes)
    holes=[Part.makeCylinder(1.25,10.5,V(268,y,8),V(-1,0,0)) for y in [15.9,24.1]]
    m.feature('ACDeviceHead','C7-style two-position connector study',head.cut(Part.makeCompound(holes)),'Accessories',0,'black')
    for i,y in enumerate([15.9,24.1]):m.ring('ACDeviceContact'+str(i),'Device mains socket contact study',1.15,1.02,6,(265.5,y,8),'Accessories',0,'metal',axis=(-1,0,0))
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
    m.profile['stages']=27
    m.checkpoint(27,'original_ac_cord_and_nineteen_contact_hdmi_cable','补齐原配双片电源插头与八字设备端、两端十九接点 HDMI 连接线及独立护线套。沿用已验证的同系列连接结构，并使电源端示意针距与本机插口一致；线长为展示近似。')
    m.snapshot('27_ac_hdmi_accessories_review',assemblies=['Accessories'],normal=(.2,-.5,2))


STAGES[27]=stage27


def stage28(m):
    from .atari2600 import _rounded_route
    rear=g.rotation((0,1,0),(0,0,1))
    points=[V(190,-91.7,6),V(190,-177,6),V(220,-177,6),V(220,-91.7,6)]
    m.feature('USBChargeCable','USB-A to Micro-B cable display length',_rounded_route(points,7,1.5),'Accessories',0,'black')
    m.box('USBAPlugGrip','USB-A charging-cable overmould',18,23,10,(190,-80,1),'Accessories',0,'black',1.6)
    m.box('MicroUSBPlugGrip','Micro-B charging-cable overmould',12,19,8,(220,-82,2),'Accessories',0,'black',1.3)
    for i,x in enumerate([190,220]):
        relief=Part.makeCylinder(1.9,6,V(x,-91.6,6),V(0,-1,0)).cut(Part.makeCylinder(1.55,6.4,V(x,-91.4,6),V(0,-1,0)))
        m.feature('USBChargeRelief'+str(i),'Charging cable strain-relief sleeve',relief,'Accessories',0,'black')
    shield=m.rr(12,4.5,12,(190,-68.3,6),.3,rear).cut(m.rr(11.4,3.9,12.4,(190,-68.5,6),.15,rear))
    m.feature('USBAPlugShield','USB-A plug metal shell',shield,'Accessories',0,'metal')
    m.box('USBAPlugStop','USB-A rear insulating stop',10.8,.65,3.3,(190,-67.9,4.35),'Accessories',0,'black',.15,True)
    m.box('USBAPlugTongue','USB-A four-contact tongue',9.2,7,1,(190,-62.7,5),'Accessories',0,'black',.15)
    for i in range(4):m.box('USBAPlugContact'+str(i),'USB-A charging-cable contact',.85,5,.1,(190+(i-1.5)*2,-62.7,6.1),'Accessories',0,'gold',.05,True)
    outer=_keyed_rear_port(7.1,2.4,7,220,-72.3,6,.6)
    inner=_keyed_rear_port(6.5,1.8,7.4,220,-72.5,6,.45)
    m.feature('MicroUSBPlugShield','Micro-B keyed plug shell',outer.cut(inner),'Accessories',0,'metal')
    m.feature('MicroUSBPlugStop','Micro-B insulating rear stop',_keyed_rear_port(6,1.3,.65,220,-71.9,6,.3),'Accessories',0,'black',True)
    m.box('MicroUSBPlugTongue','Micro-B contact carrier',5.8,4,.45,(220,-68.5,5.65),'Accessories',0,'black',.1)
    for i in range(5):m.box('MicroUSBPlugContact'+str(i),'Micro-B charging-cable contact',.25,3.5,.08,(220+(i-2)*.65,-68.3,6.2),'Accessories',0,'gold',.025,True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=28
    m.checkpoint(28,'original_usb_a_to_micro_b_charging_cable','加入原配 USB-A 至 Micro-B 充电线、双端包胶与护线套、独立金属壳和绝缘件、四及五接点。插头和线长为缩短展示的结构近似。')
    m.snapshot('28_usb_charging_accessory_review',assemblies=['Accessories'],normal=(.2,-.5,2))


STAGES[28]=stage28


def stage29(m):
    from .atari2600 import _rounded_route,_helical_spring
    cup=Part.makeCylinder(6.5,7,V(310,-30,8)).fuse(Part.makeCylinder(2,9,V(310,-35,11),V(0,-1,0)))
    cup=cup.cut(Part.makeCylinder(5.5,6.3,V(310,-30,9))).cut(Part.makeCylinder(1,9.4,V(310,-34.9,11),V(0,-1,0)))
    m.feature('MonoEarCase','Single-ear speaker housing and cable stem study',cup,'Accessories',0,'black')
    m.cyl('MonoEarMagnet','Earbud magnetic circuit study',3.4,2,(310,-30,9.15),'Accessories',0,'metal',internal=True)
    m.ring('MonoEarFrame','Earbud speaker frame',5.2,4.85,3.3,(310,-30,11.2),'Accessories',0,'metal',internal=True)
    m.ring('MonoEarCoil','Earbud voice-coil envelope study',2.5,2.25,1.5,(310,-30,13),'Accessories',0,'copper',internal=True)
    m.cyl('MonoEarDiaphragm','Earbud diaphragm',4.8,.12,(310,-30,14.6),'Accessories',0,'black',internal=True)
    grille=Part.makeCylinder(6.2,.7,V(310,-30,15.2))
    grille=grille.cut(Part.makeCompound([Part.makeCylinder(.45,1,V(310+x,-30+y,15.05)) for x in [-3,-1.5,0,1.5,3] for y in [-3,-1.5,0,1.5,3]]))
    m.feature('MonoEarGrille','Perforated single-ear grille',grille,'Accessories',0,'black')
    m.ring('MonoEarRim','Soft earbud perimeter',7.1,6.45,1,(310,-30,15.1),'Accessories',0,'rubber')
    upper=[V(310,-44.2,11),V(310,-62,11),V(300,-72,7),V(300,-80.8,7)]
    m.feature('MonoUpperCord','Earbud to microphone cable display length',_rounded_route(upper,3,.8),'Accessories',0,'black')
    m.native('MonoMicCase','Native inline microphone and switch case',7,24,1.4,5,(300,-93,4),'Accessories',0,'black')
    m.cut('MonoMicCase',m.rr(5,22,4.3,(300,-93,5),1),'Open inline microphone cavity').Refine=False
    m.cut('MonoMicCase',Part.makeBox(2.0,7.4,4,V(295.6,-100.7,5.5)),'Side microphone switch aperture').Refine=False
    m.box('MonoMicLid','Inline microphone cover',6.8,23.8,.55,(300,-93,9.15),'Accessories',0,'black',1.2)
    m.cut('MonoMicLid',Part.makeCylinder(.7,.9,V(300,-88,9)),'Microphone acoustic opening').Refine=False
    m.native('MonoMicPCB','Native inline microphone circuit plate study',4.6,20,.4,.6,(300,-93,5.2),'Accessories',0,'pcb')
    m.cyl('MonoMicrophone','Electret microphone capsule envelope',1.5,1,(300,-88,7.3),'Accessories',0,'metal',internal=True)
    switch=m.rr(4,4,1.2,(300,-97,6),.3).cut(Part.makeBox(4.5,1.7,.7,V(297.8,-97.85,6.2)))
    m.feature('MonoMicSwitch','Microphone slide-switch body study',switch,'Accessories',0,'black',True)
    slider=Part.makeBox(.8,5,3.2,V(295.9,-99.5,5.8)).fuse(Part.makeBox(3.9,1.2,.35,V(296.6,-97.6,6.35)))
    m.feature('MonoMicSlider','Side MIC switch slider and actuator',slider,'Accessories',0,'black')
    m.label('MonoMicMark','MIC',1,(298.7,-85.4,9.725),'Accessories',0,'white')
    lower=[V(300,-105.2,7),V(300,-134,7),V(338,-144,7),V(338,-173.8,7)]
    m.feature('MonoLowerCord','Microphone to four-pole plug cable display length',_rounded_route(lower,4,.8),'Accessories',0,'black')
    m.cyl('MonoPlugGrip','Four-pole headset plug overmould',3.2,19,(338,-174,7),'Accessories',0,'black',axis=(0,-1,0))
    m.ring('MonoPlugRelief','Headset plug strain-relief sleeve',1.3,.85,5,(338,-173.9,7),'Accessories',0,'black',axis=(0,1,0))
    contacts=[('Sleeve',-193.2,3.3),('Ring2',-197.35,2.4),('Ring1',-200.6,2.4),('Tip',-203.85,2.4)]
    for name,y,length in contacts:
        shape=Part.makeCylinder(1.65,length,V(338,y,7),V(0,-1,0))
        if name=='Tip':shape=shape.makeFillet(.6,[e for e in shape.Edges if e.BoundBox.YLength<1e-6 and e.BoundBox.YMin<-206.2])
        m.feature('MonoPlug'+name,'Headset '+name.lower()+' contact study',shape,'Accessories',0,'metal')
    for i,y in enumerate([-196.6,-199.85,-203.1]):m.cyl('MonoPlugInsulator'+str(i),'Four-pole plug insulating separator',1.65,.65,(338,y,7),'Accessories',0,'black',axis=(0,-1,0))
    # A separate cable clip follows the official family-guide arrangement.
    upper_jaw=m.rr(8,18,1,(306,-119,8.2),.7)
    cable_ring=Part.makeCylinder(1.3,6,V(300,-122,7),V(0,1,0)).cut(Part.makeCylinder(.85,6.4,V(300,-122.2,7),V(0,1,0)))
    neck=Part.makeBox(2,4,.7,V(301,-120,6.3));tab=Part.makeBox(1.2,4,2.5,V(302,-120,5.8))
    upper_hinge=Part.makeCylinder(1.8,3.4,V(304.3,-111,5.5),V(1,0,0)).fuse(Part.makeBox(3.4,3,1.5,V(304.3,-112.5,7)))
    upper_jaw=upper_jaw.multiFuse([cable_ring,neck,tab,upper_hinge])
    upper_jaw=upper_jaw.cut(Part.makeCylinder(.7,3.8,V(304.1,-111,5.5),V(1,0,0))).cut(Part.makeCylinder(1.5,1.6,V(305.2,-111,5.5),V(1,0,0)))
    m.feature('MonoClipUpper','Cable clip upper jaw and bored cord clamp',upper_jaw,'Accessories',0,'black')
    lower_jaw=_prism_yz([(-128,7.5),(-112,3.5),(-110,3.5),(-110,2.5),(-128,6.5)],302,8)
    for x in [302,308]:
        lug=Part.makeCylinder(1.8,2,V(x,-111,5.5),V(1,0,0)).fuse(Part.makeBox(2,3,1,V(x,-112.5,3.4)))
        lower_jaw=lower_jaw.fuse(lug)
    lower_jaw=lower_jaw.cut(Part.makeCylinder(.7,8.4,V(301.8,-111,5.5),V(1,0,0)))
    m.feature('MonoClipLower','Cable clip opposing tapered jaw',lower_jaw,'Accessories',0,'black')
    m.cyl('MonoClipPin','Cable clip hinge pin',.55,8.4,(301.8,-111,5.5),'Accessories',0,'metal',axis=(1,0,0),internal=True)
    spring=_helical_spring(1,.35,1.2,.10);spring.Placement=App.Placement(V(305.4,-111,5.5),App.Rotation(V(0,0,1),V(1,0,0)))
    m.feature('MonoClipSpring','Cable clip spring-coil study',spring,'Accessories',0,'metal',True)
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=29
    m.checkpoint(29,'mono_headset_speaker_mic_switch_clip_and_four_pole_plug','补齐单耳扬声器分件、带侧向 MIC 开关的原生麦克风线控、独立铰接线夹与弹簧、四段接点插头和缩短线缆。套装身份依据 2013 官方 FAQ；耳机局部构造以较晚同系列官方示意为指导，内部尺寸为学习近似。')
    m.snapshot('29_complete_accessories_review',assemblies=['Accessories'],normal=(.2,-.5,2))


STAGES[29]=stage29


def finalize(model):
    from .deliver import finalize as shared_finalize
    result=shared_finalize(model)
    model.snapshot("final_front",normal=(.2,-1.5,.7),assemblies=model.profile["envelope_groups"])
    model.snapshot("final_hero",normal=(.3,-.7,2.3),assemblies=result[0]["handheld_groups"])
    model.doc.save()
    return result
