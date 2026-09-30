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
