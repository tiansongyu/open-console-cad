"""Original white Xenon Xbox 360: editable staged structure study."""
import FreeCAD as App
import Part
from .core import V
from . import geometry as g


def _strict_changed(m,prior):
    """Check new/replaced shapes per stage; saved whole-assembly audits run separately."""
    m.doc.recompute()
    for key,obj in m.parts.items():
        if prior.get(key)!=obj.Name:obj.Shape.check(True)


def _curved_panel(m,key,label,width,depth,end,mid,thickness,y,layer):
    # Analytic circular arcs keep through-hole intersections stable in OCCT.
    # This remains a photo-guided curvature approximation, not a measured radius.
    a,b,c=V(-width/2,end),V(0,mid),V(width/2,end);dt=V(0,thickness)
    sk=m.doc.addObject('Sketcher::SketchObject',key+'Section');sk.Label=label+' · editable curved section'
    sk.addGeometry([Part.Arc(a,b,c),Part.LineSegment(c,c+dt),Part.Arc(c+dt,b+dt,a+dt),Part.LineSegment(a+dt,a)],False)
    sk.Placement=App.Placement(V(0,y,0),App.Rotation(V(1,0,0),90));m.group('Construction').addObject(sk)
    ex=m.doc.addObject('Part::Extrusion',key+'Extrusion');ex.Label=label;ex.Base=sk;ex.DirMode='Normal';ex.LengthFwd=depth;ex.Solid=True
    m.doc.recompute();sk.Visibility=False
    return m.register(ex,key,'Body',layer,'ivory')


def stage01(m):
    prior={k:o.Name for k,o in m.parts.items()}
    m.colors.update(ivory=(.80,.81,.78),ventgray=(.45,.48,.46),chrome=(.65,.69,.70),xboxgreen=(.33,.70,.10))
    m.params.set('A3','Depth (Y)');m.params.set('A4','Height (Z)')
    _curved_panel(m,'UpperShell','Original white concave upper shell',304,253.5,82.8,76.3,-2.1,127,7)
    _curved_panel(m,'LowerShell','Original white concave lower shell',304,253.5,.2,6.7,2.1,127,-7)
    a,b,c=V(-154.5,83),V(0,76.5),V(154.5,83);d,e,f=V(154.5,0),V(0,6.5),V(-154.5,0)
    sk=m.doc.addObject('Sketcher::SketchObject','FaceplateOutline');sk.Label='Removable curved front faceplate · editable outline'
    sk.addGeometry([Part.Arc(a,b,c),Part.LineSegment(c,d),Part.Arc(d,e,f),Part.LineSegment(f,a)],False)
    sk.Placement=App.Placement(V(0,-127,0),App.Rotation(V(1,0,0),90));m.group('Construction').addObject(sk)
    ex=m.doc.addObject('Part::Extrusion','FaceplateExtrusion');ex.Label='Original removable white faceplate';ex.Base=sk;ex.DirMode='Normal';ex.LengthFwd=2;ex.Solid=True
    m.doc.recompute();sk.Visibility=False;m.register(ex,'Faceplate','Body',2,'ivory')
    m.doc.recompute()
    _strict_changed(m,prior)
    m.profile['stages']=1
    m.checkpoint(1,'native_concave_white_enclosure','根据原版白色 Xenon 外观建立独立的上下凹曲面壳和可拆前面板，均保留草图曲线与原生拉伸；309×258×83 mm 为暂定学习包络，局部曲率为照片指导近似。开孔、侧格栅、内部机构与无线控制器后续分轮加入。')
    m.snapshot('01_concave_enclosure',normal=(.35,-1.4,.85))


STAGES={1:stage01}


def stage02(m):
    prior={k:o.Name for k,o in m.parts.items()}
    front=g.rotation((0,-1,0),(0,0,1))
    openings=[(-65,58,144,17,6),(-110,30,44,10,4),(-56,30,44,10,4),(129,42,32,13,5),(-143,31,8,16,3)]
    for i,(x,z,w,h,r) in enumerate(openings):m.cut('Faceplate',m.rr(w+.7,h+.7,7,(x,-125,z),r+.25,front),'Original front opening '+str(i+1)).Refine=False
    for key,x,z,r in [('Power',78,42,16.7),('Sync',22,30,3.8),('Eject',-144,58,5)]:
        m.cut('Faceplate',Part.makeCylinder(r,7,V(x,-125,z),V(0,-1,0)),'Original '+key+' button opening').Refine=False
    m.box('DVDTrayFace','Original Premium chrome DVD tray face',144,17,1.2,(-65,-128.6,58),'Optical',3,'chrome',6,orient=front)
    for i,x in enumerate([-110,-56]):m.box('MemoryDoor'+str(i),'Separate original memory-unit door',44,10,1.2,(x,-128.6,30),'Controls',2,'ivory',4,orient=front)
    m.box('USBFrontDoor','Original dual-USB access flap',32,13,1.2,(129,-128.6,42),'Controls',2,'ivory',5,orient=front)
    m.box('IRWindow','Separate infrared receiver window',8,16,1.2,(-143,-128.6,31),'Controls',2,'black',3,orient=front)
    m.cyl('PowerButton','Original circular console power button',12.8,1.1,(78,-128.7,42),'Controls',2,'ivory',axis=(0,-1,0))
    m.ring('PowerRingCarrier','Ring-of-light separator carrier',16.35,13.1,1,(78,-128.65,42),'Controls',2,'ventgray',axis=(0,-1,0))
    for i in range(4):
        arc=Part.makeCylinder(15.8,.65,V(),V(0,0,1),83).cut(Part.makeCylinder(13.65,1,V(0,0,-.1)))
        arc.rotate(V(),V(0,0,1),i*90+3.5);arc.Placement=App.Placement(V(78,-129.72,42),front).multiply(arc.Placement)
        m.feature('PowerQuadrant'+str(i),'Separate player-status light quadrant',arc,'Controls',3,'xboxgreen')
    m.cyl('SyncButton','Original wireless synchronisation button',3.4,1.1,(22,-128.7,30),'Controls',2,'ivory',axis=(0,-1,0))
    m.cyl('EjectButton','Original drive eject button',4.6,1.1,(-144,-128.7,58),'Controls',2,'chrome',axis=(0,-1,0))
    m.label('TrayMark','XBOX 360',3.8,(-94,-129.82,56.5),'Optical',3,'ventgray',rotation=front)
    for i,x in enumerate([-110,-56]):m.label('MemoryMark'+str(i),'MEMORY UNIT',1.65,(x-14,-129.82,29.4),'Controls',3,'ventgray',rotation=front)
    # Power symbol is a separate shallow marking, outside the button's front face.
    symbol=Part.makeCylinder(4.3,.018,V(),V(0,0,1),290).cut(Part.makeCylinder(3.8,.04,V(0,0,-.01)))
    symbol.rotate(V(),V(0,0,1),125);symbol.Placement=App.Placement(V(78,-129.82,42),front).multiply(symbol.Placement)
    m.feature('PowerMarkArc','Power-button ring marking',symbol,'Controls',3,'ventgray')
    m.box('PowerMarkStem','Power-button stem marking',.5,4.6,.018,(78,-129.82,45),'Controls',3,'ventgray',.1,orient=front)
    m.doc.recompute()
    _strict_changed(m,prior)
    m.profile['stages']=2
    m.checkpoint(2,'original_faceplate_doors_and_ring_of_light','加工原版 DVD 托盘、双记忆单元门、双 USB 翻门、红外窗、配对与出盘键，建立独立电源键及四分区导光。Premium 镀铬托盘和细标识独立建模；门后插座和电子板后续补齐。')
    m.snapshot('02_original_faceplate',normal=(.25,-1.6,.7))


STAGES[2]=stage02


def stage03(m):
    prior={k:o.Name for k,o in m.parts.items()}
    end=g.rotation((1,0,0),(0,0,1))
    for side,x in [('Left',-153.9),('Right',152.5)]:
        key=side+'EndGrille'
        m.box(key,'Separate original gray end ventilation grille',250,78,1.4,(x,0,41.5),'Body',-1 if side=='Left' else 1,'ventgray',16,orient=end)
        holes=[Part.makeCylinder(1.65,2.2,V(x-.4,y,z),V(1,0,0)) for y in range(-114,115,6) for z in [14.5+6*j for j in range(10)]]
        m.cut(key,holes,'Through-hole field in original molded end grille').Refine=False
    holes=[Part.makeCylinder(1.65,90,V(x,y,-3)) for x in [-143,-137,-131,131,137,143] for y in range(-105,106,7)]
    for key in ['UpperShell','LowerShell']:m.cut(key,holes,'Three rows of open circular inlet holes at each broad-panel end').Refine=False
    # Separate feet on the horizontal lower side; side feet will follow with HDD mounting details.
    for i,(x,y) in enumerate([(-135,-97),(-135,97),(135,-97),(135,97)]):
        z=.2+6.5*(1-(x/152)**2)
        m.box('Foot'+str(i),'Independent lower rubber support',12,10,1.4,(x,y,z-2.2),'Frame',-8,'rubber',2.5)
    m.doc.recompute()
    _strict_changed(m,prior)
    m.profile['stages']=3
    m.checkpoint(3,'perforated_end_grilles_and_shell_inlets','加入左右独立灰色圆孔格栅，壳体两端三列圆孔为真实贯穿几何，补充横置橡胶支脚；孔距、数量和材料厚度按原机照片作结构学习近似。')
    m.snapshot('03_original_ventilation',normal=(.5,-1.2,.75))


STAGES[3]=stage03


def stage04(m):
    prior={k:o.Name for k,o in m.parts.items()}
    sk=m.doc.addObject('Sketcher::SketchObject','RearCaseOutline');sk.Label='Original rear closure · editable curved outline'
    sk.addGeometry(m.doc.getObject('FaceplateOutline').Geometry,False)
    sk.Placement=App.Placement(V(0,129,0),App.Rotation(V(1,0,0),90));m.group('Construction').addObject(sk)
    ex=m.doc.addObject('Part::Extrusion','RearCaseExtrusion');ex.Label='Original non-HDMI rear closure';ex.Base=sk;ex.DirMode='Normal';ex.LengthFwd=1.8;ex.Solid=True
    m.doc.recompute();sk.Visibility=False;m.register(ex,'RearCase','Body',1,'ivory')
    rear=g.rotation((0,1,0),(0,0,1))
    for key,x,z,w,h in [('DC',126,25,28,24),('AV',-88,27,36,14),('LANUSB',-130,29,20,29)]:
        m.cut('RearCase',m.rr(w,h,6,(x,125,z),2,rear),'Original Xenon rear '+key+' opening').Refine=False
    vents=[Part.makeCylinder(2,6,V(x,125,z),V(0,1,0)) for x in range(-59,98,6) for z in range(18,67,6)]
    m.cut('RearCase',vents,'Twin rear exhaust fan ventilation field').Refine=False
    m.box('RearStudyPlate','Rear identification study plate',41,13,.08,(122,129.05,58),'Body',1,'white',.5,orient=rear)
    m.label('RearStudyMark','XENON / CAD',2.2,(138,129.15,58),'Body',1,'ventgray',rotation=rear)
    m.doc.recompute()
    _strict_changed(m,prior)
    m.profile['stages']=4
    m.checkpoint(4,'xenon_rear_ports_and_twin_fan_exhaust','闭合后部原生曲面，加工外置 DC、原版 AV、叠置 LAN/USB 开口与双风扇排风圆孔；明确不加入后期 HDMI 接口。后部标识为 CAD 学习标识，不复制实机序列号。')
    m.snapshot('04_original_rear',normal=(.3,1.5,.7))


STAGES[4]=stage04


def stage05(m):
    prior={k:o.Name for k,o in m.parts.items()}
    from .ps1 import _add_shape
    m.native('Chassis','Editable folded steel chassis floor',288,240,2,1,(0,1,10.7),'Frame',-5,'metal',expr={'Width':'Parameters.Width - 21 mm'})
    walls=[m.rr(1,240,60.5,(x,1,11.5),.15) for x in [-143.4,143.4]]
    walls+=[m.rr(288,1,27.5,(0,-118.4,11.5),.15),m.rr(288,1,60.5,(0,120.4,11.5),.15)]
    _add_shape(m,'Chassis',walls[0].multiFuse(walls[1:]).removeSplitter(),'Folded front rear and side walls').Refine=False
    rear=g.rotation((0,1,0),(0,0,1));front=g.rotation((0,-1,0),(0,0,1))
    for key,x,z,w,h in [('DC',126,25,29,25),('AV',-88,27,37,15),('LANUSB',-130,29,21,30)]:
        m.cut('Chassis',m.rr(w,h,5,(x,118,z),2,rear),'Metal rear '+key+' aperture').Refine=False
    m.cut('Chassis',[Part.makeCylinder(2.25,5,V(x,118,z),V(0,1,0)) for x in range(-59,98,6) for z in range(18,67,6)],'Aligned steel rear exhaust perforations').Refine=False
    m.cut('Chassis',[m.rr(45,12,5,(x,-116,30),4,front) for x in [-110,-56]]+[m.rr(33,15,5,(129,-116,42),4,front),m.rr(10,18,5,(-143,-116,31),2,front)],'Front memory USB and infrared clearances').Refine=False
    mounts=[(-125,-93),(-125,90),(-55,-93),(15,-93),(110,-93),(130,20),(110,92),(25,70),(-55,65)]
    m.cut('Chassis',[Part.makeCylinder(.95,3,V(x,y,10)) for x,y in mounts],'Motherboard retaining fastener passages').Refine=False
    for i,(x,y) in enumerate(mounts):
        m.ring('BoardStandoff'+str(i),'Separate motherboard support and screw guide',3.0,1.15,5,(x,y,11.7),'Frame',-4,'metal')
        m.screw('BoardScrew'+str(i),(x,y,10.15),'Frame',-5,length=7.5,radius=1.7)
    m.doc.recompute()
    _strict_changed(m,prior)
    m.profile['stages']=5
    m.checkpoint(5,'native_steel_chassis_and_board_supports','建立带宽度表达式的原生金属底盘、折边、对齐后排风孔、前后接口通道及九组分离支承/紧固件。金属板厚、固定位置与间隙为学习近似；保留底盘尺寸和布尔加工历史。')
    m.snapshot('05_metal_chassis',assemblies=['Frame'],normal=(.4,-.7,1.8))


STAGES[5]=stage05


def _board_mounts():
    return [(-125,-93),(-125,90),(-55,-93),(15,-93),(110,-93),(130,20),(110,92),(25,70),(-55,65)]


def stage06(m):
    prior={k:o.Name for k,o in m.parts.items()}
    m.native('MainPCB','Original Xenon mainboard outline study',274,226,2,1.4,(0,1,17.1),'Mainboard',-1,'pcb')
    m.cut('MainPCB',Part.makeBox(142,37,3,V(-62,82,16.5)),'Rear twin-fan recess between AV and DC connector wings').Refine=False
    holes=[Part.makeCylinder(1.3,2.5,V(x,y,16.6)) for x,y in _board_mounts()]
    holes += [Part.makeCylinder(1.8,2.5,V(cx+dx,-20+dy,16.6)) for cx in [-37,45] for dx in [-27,27] for dy in [-27,27]]
    m.cut('MainPCB',holes,'Board retention and separate CPU GPU clamp passages').Refine=False
    for i,(x,y) in enumerate(_board_mounts()):m.ring('BoardMountLand'+str(i),'Independent plated mounting land study',2.3,1.4,.06,(x,y,18.52),'Mainboard',-1,'gold')
    m.label('BoardStudyMark','XENON / CAD',2.4,(-19,-104,18.52),'Mainboard',-1,'white')
    m.doc.recompute()
    _strict_changed(m,prior)
    m.profile['stages']=6
    m.checkpoint(6,'native_xenon_board_outline_and_mounting','建立原生 Xenon 主板与后部双风扇凹口，保留九组机壳固定孔、CPU/GPU 独立夹具通道及安装焊盘。板外形和孔位为照片指导近似，不提供制造 Gerber 或实际电路。')
    m.snapshot('06_xenon_board_outline',assemblies=['Mainboard'],normal=(0,0,1))


STAGES[6]=stage06


def _bga_package(m,key,label,x,y,w,h,thickness,z=19.0,material='black',layer=0):
    m.box(key,label,w,h,thickness,(x,y,z),'Mainboard',layer,material,.3,True)
    # Simplified visible attachment grid, deliberately not the actual electrical pinout.
    balls=[Part.makeSphere(.19,V(x+(i-3.5)*(w-5)/7,y+(j-3.5)*max(h-5,3.0)/7,z-.24)) for i in range(8) for j in range(8)]
    m.feature(key+'SolderGrid','Simplified BGA support balls; not a physical pinout',Part.makeCompound(balls),'Mainboard',layer,'metal',True)


def stage07(m):
    prior={k:o.Name for k,o in m.parts.items()}
    _bga_package(m,'XenonCPU','Separate Xenon CPU package envelope',45,-20,34,34,1.1,material='ventgray')
    m.box('CPUExposedDie','Xenon exposed die study',18,18,1.2,(45,-20,20.15),'Mainboard',1,'metal',.2,True)
    _bga_package(m,'XenosGPU','Separate Xenos GPU and eDRAM package envelope',-37,-20,42,39,1.1,material='ventgray')
    m.box('GPUExposedDie','Xenos main die study',22,22,1.1,(-37,-26,20.15),'Mainboard',1,'metal',.2,True)
    m.box('EDRAMDie','Separate eDRAM die on Xenos package',12,7,1.1,(-37,-8,20.15),'Mainboard',1,'metal',.15,True)
    ram=[(-79,-12),(-79,-44),(-48,-68),(-16,-68)]
    for i,(x,y) in enumerate(ram):
        _bga_package(m,'RAMTop'+str(i),'Upper-side GDDR3 package study',x,y,13,11,1.1)
        m.box('RAMBottom'+str(i),'Reverse-side GDDR3 package study',13,11,1.1,(x,y,15.5),'Mainboard',-2,'black',.2,True)
        pads=[Part.makeSphere(.17,V(x+(a-2.5)*1.75,y+(b-2)*1.7,16.83)) for a in range(6) for b in range(5)]
        m.feature('RAMBottomSolder'+str(i),'Simplified reverse memory attachment grid',Part.makeCompound(pads),'Mainboard',-2,'metal',True)
    m.doc.recompute()
    _strict_changed(m,prior)
    m.profile['stages']=7
    m.checkpoint(7,'xenon_xenos_edram_and_double_sided_memory','按原版主板照片分离 Xenon CPU、Xenos GPU 与同封装 eDRAM，加入主板正反各四枚 GDDR3 包络。焊球网格仅展示连接层，不宣称真实球数、引脚排列或生产封装尺寸。')
    m.snapshot('07_processor_and_memory',assemblies=['Mainboard'],normal=(.25,-.6,1.8))


STAGES[7]=stage07


def _tsop(m,key,x,y,w,h,pins_per_side=24):
    m.box(key,'NAND flash package study',w,h,1.05,(x,y,19.0),'Mainboard',0,'black',.25,True)
    for side in [-1,1]:
        for i in range(pins_per_side):
            yy=y+(i-(pins_per_side-1)/2)*.7
            # Make one continuous formed lead with a clear gap from the package envelope.
            sh=Part.makeBox(.76,.28,.16,V(w/2+.06,-.14,19.22))
            sh=sh.fuse(Part.makeBox(.16,.28,.64,V(w/2+.7,-.14,18.74))).fuse(Part.makeBox(.82,.28,.16,V(w/2+.7,-.14,18.72))).removeSplitter()
            if side<0:sh.rotate(V(),V(0,0,1),180)
            sh.translate(V(x,yy,0))
            m.feature(key+'Lead'+str(side)+'_'+str(i),'Separate formed flash lead study',sh,'Mainboard',0,'metal',True)


def stage08(m):
    prior={k:o.Name for k,o in m.parts.items()}
    for key,label,x,y,w,h in [('Southbridge','Original Xenon southbridge',-105,25,26,26),('ANA','Original ANA analog video encoder',-55,53,16,16),('EthernetPHY','Ethernet controller study',-120,72,12,10),('AudioDAC','Separate audio DAC study',-98,73,8,8),('SMC','System management package study',-10,55,12,12),('USBLogic','Front USB support package study',20,33,10,8),('HDDLogic','Storage support package study',-103,-79,8,6),('MemoryLogic','Memory-unit support package study',-77,-84,8,8)]:
        _bga_package(m,key,label,x,y,w,h,1.05)
    _tsop(m,'NANDFlash',-105,-49,11,20)
    m.box('ClockCrystal','Separate oscillator can',8,3,2.4,(-75,48,19.05),'Mainboard',1,'metal',.7,True)
    m.box('ClockFoot','Oscillator insulating foot',8.5,3.5,.3,(-75,48,18.6),'Mainboard',0,'black',.3,True)
    for key,text,x,y,z in [('CPUMark','XENON',32,-33,20.12),('GPUMark','XENOS',-55,-36,20.12),('ANAMark','ANA',-59,52,20.12),('NANDMark','NAND',-109,-49,20.07)]:
        m.label(key,text,1.8,(x,y,z),'Mainboard',1,'white')
    m.doc.recompute()
    _strict_changed(m,prior)
    m.profile['stages']=8
    m.checkpoint(8,'original_ana_southbridge_nand_and_io_logic','加入原版 ANA 模拟视频编码器、系统桥、16 MB NAND 外形与独立成形引脚，补齐以太网、音频、系统管理和时钟器件。布局及封装为非功能性近似，明确不混入后期 HDMI/HANA 方案。')
    m.snapshot('08_xenon_logic_layout',assemblies=['Mainboard'],normal=(0,0,1))


STAGES[8]=stage08


def stage09(m):
    prior={k:o.Name for k,o in m.parts.items()}
    import math
    coils=[(100,-78),(100,-44),(100,-10),(100,24),(75,58),(45,58)]
    for i,(x,y) in enumerate(coils):
        m.ring('VRMCore'+str(i),'Independent toroidal regulator core',5,2.8,4,(x,y,19.35),'Mainboard',1,'gold',internal=True)
        for j in range(16):
            a=j*2*math.pi/16;center=V(x+3.9*math.cos(a),y+3.9*math.sin(a),21.35);axis=V(-math.sin(a),math.cos(a),0)
            m.feature('VRMTurn'+str(i)+'_'+str(j),'Separate insulated regulator winding loop',Part.makeTorus(2.45,.15,center,axis),'Mainboard',1,'copper',True)
    caps=[(126,y) for y in [-80,-58,-36,-14,8,30,52,74,95]]+[(112,-92),(112,-66),(112,-32),(112,2),(112,40),(110,76),(83,77),(66,77),(48,77),(30,77),(12,77),(-5,77),(89,45),(89,14)]
    for i,(x,y) in enumerate(caps):
        m.cyl('VRMCap'+str(i),'Separate bulk capacitor envelope',4.1,14,(x,y,19.15),'Mainboard',1,'battery',internal=True)
        m.cyl('VRMCapTop'+str(i),'Independent capacitor vent face',3.8,.12,(x,y,33.22),'Mainboard',2,'metal',internal=True)
        for j,dx in enumerate([-1.5,1.5]):m.cyl('VRMCapLead'+str(i)+'_'+str(j),'Separate capacitor board termination',.3,.5,(x+dx,y,18.6),'Mainboard',0,'metal',internal=True)
    for i,(x,y) in enumerate([(85,-62),(85,-30),(85,0),(84,30),(66,45),(35,45)]):
        m.box('VRMPowerDevice'+str(i),'Regulator power-device package envelope',5,6,1.25,(x,y,19.0),'Mainboard',0,'black',.15,True)
        m.box('VRMPowerPad'+str(i),'Separate power-device attachment pad',4.5,5.5,.1,(x,y,18.65),'Mainboard',0,'metal',.1,True)
    # Distribute a bounded set of schematic passives across free board regions.
    # Bounding-box keepouts preserve separation from the source-specific major packages.
    occupied=[o.Shape.BoundBox for k,o in m.parts.items() if o.Assembly=='Mainboard' and k!='MainPCB' and o.Shape.BoundBox.ZMax>18.51]
    pcb=m.parts['MainPCB'].Shape;candidates=[]
    reserved=[(-130,108,24,25),(-88,108,42,28),(126,107,30,28),(-110,-111,46,22),(-56,-111,46,22),(129,-110,34,24)]
    for y in range(-101,79,9):
        for x in range(-125,132,8):
            if any(abs(x-cx)<w/2+2 and abs(y-cy)<h/2+2 for cx,cy,w,h in reserved):continue
            if not all(pcb.isInside(V(x+dx,y+dy,17.8),1e-6,True) for dx in [-1.9,1.9] for dy in [-.8,.8]):continue
            if any(b.XMin-2<x<b.XMax+2 and b.YMin-1.1<y<b.YMax+1.1 for b in occupied):continue
            candidates.append((x,y))
    count=min(96,len(candidates))
    selected=[candidates[int(i*(len(candidates)-1)/max(1,count-1))] for i in range(count)]
    for i,(x,y) in enumerate(selected):
        m.box('PassiveBody'+str(i),'Schematic resistor or ceramic body',2.2,1.0,.55,(x,y,18.72),'Mainboard',0,'black' if i%3==0 else 'thermal',.1,True)
        for j,side in enumerate([-1,1]):m.box('PassiveEnd'+str(i)+'_'+str(j),'Separate passive termination',.45,1.04,.59,(x+side*1.36,y,18.7),'Mainboard',0,'metal',.05,True)
    m.doc.recompute()
    _strict_changed(m,prior)
    m.profile['stages']=9
    m.checkpoint(9,'original_regulator_coils_bulk_caps_and_passives','加入右侧及后部供电器件，独立磁芯、绕组、圆柱电容、端子和功率封装；分布式小器件避开主芯片、孔位及接口。所有数量与电气连接仅为非功能性布局示意，不是原厂 BOM 或电路。')
    m.snapshot('09_xenon_power_layout',assemblies=['Mainboard'],normal=(.3,-.5,1.8))


STAGES[9]=stage09


def _socket(m,key,x,y,z,w,h,depth,front=False,material='metal',wall=.45):
    """Open rectangular connector; y is the inner end, facing away from the board."""
    sign=-1 if front else 1
    orient=g.rotation((0,sign,0),(0,0,1))
    outer=m.rr(w,h,depth,(x,y,z),min(1,h/5),orient)
    inner=m.rr(w-2*wall,h-2*wall,depth+.4,(x,y-sign*.2,z),min(.5,h/7),orient)
    m.feature(key+'Shell','Independent open connector housing',outer.cut(inner),'Ports',1,material,True)
    m.box(key+'Back','Separate connector rear insulator',w-2*wall-.15,h-2*wall-.15,.6,(x,y+sign*.2,z),'Ports',0,'black',.5,True,orient=orient)
    return y+sign*depth/2


def stage10(m):
    prior={k:o.Name for k,o in m.parts.items()}
    # Three original USB-A receptacles: two behind the front door, one under LAN.
    for key,x,y,z,front in [('FrontUSB0',120.6,-111,41,True),('FrontUSB1',135.4,-111,41,True),('RearUSB',-130,107,22.3,False)]:
        cy=_socket(m,key,x,y,z,13.4,6.5,17,front)
        m.box(key+'Tongue','USB-A insulating tongue',10.5,12,1.0,(x,cy,z-.5),'Ports',1,'black',.15,True)
        for i in range(4):m.box(key+'Contact'+str(i),'Separate USB 2.0 contact',.65,10,.12,(x+(i-1.5)*2.35,cy,z+.57),'Ports',1,'gold',.04,True)
    cy=_socket(m,'Ethernet',-130,107,35,17,14,20)
    for i in range(8):m.box('EthernetContact'+str(i),'Separate eight-position LAN spring contact',.35,15,.2,(-130+(i-3.5)*1.3,cy,31.1),'Ports',1,'gold',.03,True)
    for i,x in enumerate([-136.4,-123.6]):m.box('EthernetLens'+str(i),'LAN status light lens',1.1,1.0,1.3,(x,126.2,39.5),'Ports',1,'led',.15,True)
    cy=_socket(m,'AnalogAV',-88,107,27,35,12.5,21)
    m.box('AVTongue','Original analog AV tongue study',30,17,1.2,(-88,cy,26.4),'Ports',1,'black',.2,True)
    for side in [-1,1]:
        for i in range(15):m.box('AVContact'+str(side)+'_'+str(i),'Separate original AV contact study',.65,13,.1,(-88+(i-7)*1.8,cy,27+(.67 if side==1 else -.77)),'Ports',1,'gold',.03,True)
    # Keying/contact arrangement is schematic; it is not a wiring or mating drawing.
    cy=_socket(m,'DCInput',126,106,27.5,27,17,22,material='black',wall=1)
    for i,(dx,dz) in enumerate([(-7,-4),(0,-4),(7,-4),(-7,4),(0,4),(7,4)]):
        m.cyl('DCPowerContact'+str(i),'Separate DC power terminal study',1.35,16,(126+dx,109,27.5+dz),'Ports',1,'metal',axis=(0,1,0),internal=True)
    for i,dx in enumerate([-3,3]):m.cyl('DCSenseContact'+str(i),'Separate small DC contact study',.55,13,(126+dx,110,27.5),'Ports',1,'metal',axis=(0,1,0),internal=True)
    for j,x in enumerate([-110,-56]):
        cy=_socket(m,'MemorySocket'+str(j),x,-107,30,42,9,18,True)
        m.box('MemoryTongue'+str(j),'Original memory-unit slot insulator',36,13,1.1,(x,cy,29.45),'Ports',1,'black',.3,True)
        for i in range(12):m.box('MemoryContact'+str(j)+'_'+str(i),'Separate memory-unit contact study; not a pinout',1.0,10,.12,(x+(i-5.5)*2.7,cy,30.62),'Ports',1,'gold',.04,True)
    _strict_changed(m,prior)
    m.profile['stages']=10
    m.checkpoint(10,'original_memory_usb_lan_av_and_dc_connectors','加入前双 USB、双记忆单元插座、后 LAN/USB、原版模拟 AV 和外置电源 DC 接口；屏蔽、绝缘、舌片与接点独立建模。接点排列和键位仅为结构示意，不可用于接线或制造配对插头。')
    m.snapshot('10_original_connectors',assemblies=['Mainboard','Ports'],normal=(.25,1,1.5))


STAGES[10]=stage10


def stage11(m):
    prior={k:o.Name for k,o in m.parts.items()}
    import math
    rear=g.rotation((0,1,0),(0,0,1))
    m.box('RFBoard','Separate original front RF ring-of-light and pairing board',94,38,1.2,(63,-123,42),'Wireless',2,'pcb',2,True,orient=rear)
    for i,(x,z) in enumerate([(52,27),(104,27),(52,57),(104,57)]):
        m.cut('RFBoard',Part.makeCylinder(1.1,2,V(x,-123.4,z),V(0,1,0)),'RF board mounting hole').Refine=False
        m.ring('RFMountLand'+str(i),'RF board plated mounting annulus',1.9,1.2,.06,(x,-123.09,z),'Wireless',2,'gold',axis=(0,1,0),internal=True)
    m.box('RFChip','Wireless transceiver package envelope',10,10,1.3,(70,-121.6,42),'Wireless',2,'black',.2,True,orient=rear)
    shield=m.rr(17,17,1.6,(70,-121.7,42),.5,rear).cut(m.rr(16.4,16.4,1.5,(70,-121.8,42),.3,rear))
    m.feature('RFShield','Separate open-back RF shield can',shield,'Wireless',3,'metal',True)
    m.box('RFCrystal','Wireless board oscillator envelope',6,2.4,1.4,(87,-121.6,41),'Wireless',2,'metal',.5,True,orient=rear)
    for i,(x,z) in enumerate([(59,31),(66,30),(74,30),(82,30),(92,32),(96,45),(88,52),(76,54),(61,54)]):
        m.box('RFPassive'+str(i),'Schematic RF board discrete device',2.5,1.2,.6,(x,-121.6,z),'Wireless',2,'black',.1,True,orient=rear)
    # Antenna meander separated from board and metal can; schematic, not RF artwork.
    antenna=[Part.makeBox(1,.08,5,V(97,-121.7,50)),Part.makeBox(5,.08,1,V(97,-121.7,55)),Part.makeBox(1,.08,5,V(101,-121.7,51))]
    m.feature('RFAntenna','Schematic copper antenna trace',antenna[0].multiFuse(antenna[1:]).removeSplitter(),'Wireless',2,'copper',True)
    for i in range(4):
        a=math.radians(45+90*i);x=78+14.5*math.cos(a);z=42+14.5*math.sin(a)
        m.box('RingLED'+str(i),'Separate quadrant LED package',2.4,2.4,.7,(x,-124.7,z),'Wireless',2,'led',.25,True,orient=rear)
        m.cyl('RingLightGuide'+str(i),'Separate quadrant light-guide stem',.95,3.2,(x,-128.1,z),'Wireless',3,'white',axis=(0,1,0),internal=True)
    m.box('PowerTactile','Independent console power tactile switch',6,6,1.2,(78,-124.6,42),'Wireless',2,'metal',.4,True,orient=rear)
    m.cyl('PowerPlunger','Separate console power actuator',1.6,2.6,(78,-127.5,42),'Controls',2,'ivory',axis=(0,1,0),internal=True)
    for key,x,z,w in [('IR',-143,31,8)]:
        m.box(key+'Daughterboard','Front control/sensor board study',w,12,1,(x,-123,z),'Wireless',2,'pcb',.6,True,orient=rear)
    m.box('SyncTactile','Separate pairing tactile switch',5,5,1.1,(22,-124.3,30),'Wireless',2,'metal',.3,True,orient=rear)
    m.cyl('SyncPlunger','Pairing-button actuator',1.2,3.0,(22,-127.5,30),'Controls',2,'ivory',axis=(0,1,0),internal=True)
    m.box('IRReceiver','Infrared receiver package behind dark window',5.5,6,1.5,(-143,-125,31),'Wireless',2,'black',.6,True,orient=rear)
    _strict_changed(m,prior)
    m.profile['stages']=11
    m.checkpoint(11,'front_rf_board_ring_light_and_ir_controls','分离前端 RF 板、屏蔽罩、四象限 LED 与导光柱、电源/配对触点及红外接收器。无线器件、天线和小板形状为结构示意，不提供射频设计或实际电路。')
    m.snapshot('11_original_rf_controls',assemblies=['Wireless','Controls'],exclude=['MemoryDoor0','MemoryDoor1','USBFrontDoor'],normal=(.2,-1,.6))


STAGES[11]=stage11


def _cpu_heatpipe(radius):
    path=Part.Wire([Part.makeLine(V(30,-20,23.5),V(69,-20,23.5)),Part.Arc(V(69,-20,23.5),V(75.364,-20,26.136),V(78,-20,32.5)).toShape(),Part.makeLine(V(78,-20,32.5),V(78,-20,59)),Part.Arc(V(78,-20,59),V(75.364,-20,65.364),V(69,-20,68)).toShape(),Part.makeLine(V(69,-20,68),V(30,-20,68))])
    return path.makePipeShell([Part.Wire([Part.makeCircle(radius,V(30,-20,23.5),V(1,0,0))])],True,False)


def stage12(m):
    prior={k:o.Name for k,o in m.parts.items()}
    m.box('CPUThermal','Separate CPU thermal-interface study',18,18,.16,(45,-20,21.38),'Cooling',1,'thermal',.15,True)
    m.box('GPUThermal','Separate GPU thermal-interface study',22,22,.16,(-37,-26,21.28),'Cooling',1,'thermal',.15,True)
    m.box('EDRAMThermal','Separate eDRAM thermal-interface study',12,7,.16,(-37,-8,21.28),'Cooling',1,'thermal',.15,True)
    pipe=_cpu_heatpipe(1.8);clear=_cpu_heatpipe(1.95)
    m.feature('CPUHeatpipe','Original-style CPU copper heatpipe; photo-guided routing',pipe,'Cooling',3,'copper',True)
    m.native('CPUColdplate','Editable original CPU heatsink base',58,58,.7,2,(45,-20,21.6),'Cooling',2,'copper')
    m.cut('CPUColdplate',clear,'Independent heatpipe passage in CPU coldplate').Refine=False
    for i in range(25):
        x=20.4+i*2.0
        fin=m.rr(.6,54,44,(x,-20,24),.08).cut(clear)
        m.feature('CPUFin'+str(i),'Separate upright CPU cooling fin',fin,'Cooling',3,'metal',True)
    m.native('GPUColdplate','Editable original low-profile GPU heatsink base',64,58,.7,2,(-37,-20,21.5),'Cooling',2,'metal')
    for i in range(29):m.box('GPUFin'+str(i),'Separate original short GPU cooling fin',.7,54,14,(-66.4+i*2.1,-20,23.65),'Cooling',3,'metal',.08,True)
    # Separate posts and underside X-clamps. The original low GPU sink has no later auxiliary arm.
    for name,cx in [('CPU',45),('GPU',-37)]:
        holes=[]
        for i,(dx,dy) in enumerate([(-27,-27),(-27,27),(27,-27),(27,27)]):
            x,y=cx+dx,-20+dy
            holes.append(Part.makeCylinder(1.7,4,V(x,y,20.7)))
            m.cyl(name+'ClampPost'+str(i),'Independent heatsink retention post',1.35,8.5,(x,y,12.6),'Cooling',-2,'metal',internal=True)
            m.ring(name+'ClampWasher'+str(i),'Separate insulating clamp washer',2.8,1.5,.4,(x,y,16.5),'Cooling',-2,'black',internal=True)
        m.cut(name+'Coldplate',holes,'Separate heatsink retention passages').Refine=False
        arms=[]
        for angle in [-45,45]:
            arm=m.rr(80,5,.9,(0,0,0),2)
            arm.rotate(V(),V(0,0,1),angle);arm.translate(V(cx,-20,12.1));arms.append(arm)
        clamp=arms[0].fuse(arms[1]).removeSplitter()
        clamp=clamp.cut(Part.makeCompound([Part.makeCylinder(1.55,2,V(cx+dx,-20+dy,11.7)) for dx in [-27,27] for dy in [-27,27]]))
        m.feature(name+'XClamp','Separate underside X-shaped spring retention study',clamp,'Cooling',-3,'metal',True)
    _strict_changed(m,prior)
    m.profile['stages']=12
    m.checkpoint(12,'original_cpu_tower_gpu_low_sink_and_x_clamps','建立早期 CPU 立式鳍片、独立铜热管和低矮 GPU 铝鳍片，加入三块导热界面、支柱与背面 X 夹具；热管具有分离通道，明确不加入后期 GPU 延伸热管。局部尺寸、鳍片数量及夹具形状为照片指导近似。')
    m.snapshot('12_original_thermal_hardware',assemblies=['Cooling','Mainboard'],normal=(.5,-.7,1.5))


STAGES[12]=stage12


def stage13(m):
    prior={k:o.Name for k,o in m.parts.items()}
    import math
    rear=g.rotation((0,1,0),(0,0,1))
    for j,cx in enumerate([-28,36]):
        key='RearFan'+str(j);cz=43
        frame=m.rr(60,60,20,(cx,98,cz),3,rear).cut(Part.makeCylinder(26.5,21,V(cx,97.5,cz),V(0,1,0)))
        for dx in [-25,25]:
            for dz in [-25,25]:frame=frame.cut(Part.makeCylinder(1.7,21,V(cx+dx,97.5,cz+dz),V(0,1,0)))
        m.feature(key+'Frame','Separate rear axial fan frame',frame,'Cooling',4,'black',True)
        for k,angle in enumerate([0,120,240]):
            spoke=Part.makeBox(18,.7,1.3,V(9,0,-.65));spoke.rotate(V(),V(0,1,0),angle);spoke.translate(V(cx,116.7,cz))
            spoke=spoke.common(Part.makeCylinder(26.35,1,V(cx,116.5,cz),V(0,1,0)))
            m.feature(key+'Spoke'+str(k),'Separate fan motor support spoke',spoke,'Cooling',4,'black',True)
        m.ring(key+'MotorPCB','Separate annular fan driver board',8,1,.7,(cx,100,cz),'Cooling',4,'pcb',axis=(0,1,0),internal=True)
        m.cyl(key+'Shaft','Separate axial fan shaft',.8,17.2,(cx,99.5,cz),'Cooling',4,'metal',axis=(0,1,0),internal=True)
        for k,y in enumerate([101,112]):m.ring(key+'Bearing'+str(k),'Independent fan bearing sleeve',2,1,1.5,(cx,y,cz),'Cooling',4,'metal',axis=(0,1,0),internal=True)
        m.ring(key+'Stator','Separate fan stator core envelope',3.2,2.2,5,(cx,104,cz),'Cooling',4,'metal',axis=(0,1,0),internal=True)
        for k in range(3):
            a=2*math.pi*k/3
            m.ring(key+'Coil'+str(k),'Independent fan winding envelope',1.2,.5,4,(cx+5*math.cos(a),104.5,cz+5*math.sin(a)),'Cooling',4,'copper',axis=(0,1,0),internal=True)
        m.ring(key+'Magnet','Separate fan rotor magnet',7.2,6.3,9,(cx,102.5,cz),'Cooling',4,'black',axis=(0,1,0),internal=True)
        m.ring(key+'Hub','Independent fan rotor drum',9,7.5,13,(cx,101.5,cz),'Cooling',4,'black',axis=(0,1,0),internal=True)
        m.ring(key+'Cap','Separate impeller hub cap',9,1,.7,(cx,114.8,cz),'Cooling',4,'black',axis=(0,1,0),internal=True)
        for k in range(7):
            wires=[]
            for depth,twist in [(0,0),(9,17)]:
                points=[]
                for radius,angle in [(10,-18),(25,-11),(25,11),(10,18)]:
                    a=math.radians(angle+twist+360*k/7);points.append(V(radius*math.cos(a),radius*math.sin(a),depth))
                wires.append(Part.Wire(Part.makePolygon(points+[points[0]]).Edges))
            blade=Part.makeLoft(wires,True,False);blade.Placement=App.Placement(V(cx,102,cz),rear)
            m.feature(key+'Blade'+str(k),'Separate twisted axial impeller blade study',blade,'Cooling',4,'black',True)
    _strict_changed(m,prior)
    m.profile['stages']=13
    m.checkpoint(13,'twin_rear_axial_fans_and_separate_motors','加入双后置轴流风扇，分离开孔框架、扭转叶片、转子、轴、轴承、定子、线圈与驱动板；风扇内部为学习示意，叶片与厂家变体不作精确等同。')
    m.snapshot('13_twin_rear_fans',assemblies=['Cooling'],normal=(.25,1,1.2))


STAGES[13]=stage13


def _open_duct(sections,wall=1):
    wires=[]
    for y,left,right,top,bottom in sections:
        points=[V(left,y,bottom),V(left,y,top),V(right,y,top),V(right,y,bottom),V(right-wall,y,bottom),V(right-wall,y,top-wall),V(left+wall,y,top-wall),V(left+wall,y,bottom)]
        wires.append(Part.Wire(Part.makePolygon(points+[points[0]]).Edges))
    return Part.makeLoft(wires,True,True)


def stage14(m):
    prior={k:o.Name for k,o in m.parts.items()}
    gpu=_open_duct([(11,-70,-4,40,34.5),(54,-67,-2,40,34.5),(96,-58,2,73.15,34.5)])
    cpu=_open_duct([(11,15,75,71.5,34.5),(96,7,66,73.15,34.5)])
    m.feature('GPUAirDuct','Separate low GPU branch of original white open-bottom air shroud',gpu,'Cooling',5,'ivory',True)
    m.feature('CPUAirDuct','Separate tall CPU branch of original white open-bottom air shroud',cpu,'Cooling',5,'ivory',True)
    for i,(x,y,z) in enumerate([(-58,94,60),(66,94,60)]):
        m.box('AirDuctClip'+str(i),'Separate rear shroud retention tab',3,2,.7,(x,y,z),'Cooling',5,'ivory',.2,True)
        m.cut('GPUAirDuct' if i==0 else 'CPUAirDuct',m.rr(3.3,2.3,1,(x,y,z-.15),.2),'Separate shroud clip clearance').Refine=False
    _strict_changed(m,prior)
    m.profile['stages']=14
    m.checkpoint(14,'original_white_open_bottom_air_shroud','加入 CPU 与 GPU 两支白色开放底部导风罩，低支路预留上方 DVD 空间，后段抬升接近双风扇入口；分离卡扣与安装间隙。风道形状为装配关系示意，不提供热流性能结论。')
    m.snapshot('14_original_air_path',assemblies=['Mainboard','Cooling'],normal=(.35,-.8,1.6))


STAGES[14]=stage14


def stage15(m):
    prior={k:o.Name for k,o in m.parts.items()}
    m.native('DVDBase','Editable tray-loading optical drive lower pan',138,164,1.5,.6,(-65,-35,43.5),'Optical',3,'metal')
    sides=[m.rr(.65,164,27.7,(x,-35,44.3),.1) for x in [-133.65,3.65]]
    sides += [m.rr(136,.65,27.7,(-65,46.6,44.3),.1),m.rr(136,.65,27.7,(-65,-116.6,44.3),.1)]
    case=sides[0].multiFuse(sides[1:]).removeSplitter()
    front=g.rotation((0,-1,0),(0,0,1))
    case=case.cut(m.rr(130,20,3,(-65,-115.5,58),1.5,front))
    m.feature('DVDSides','Folded optical drive walls with open tray mouth',case,'Optical',4,'metal',True)
    m.native('DVDTop','Editable removable optical drive top cover',138,164,1.5,.6,(-65,-35,72.5),'Optical',6,'metal')
    m.ring('DVDTopEmboss','Separate stamped circular optical-cover reinforcement study',61,59.7,.18,(-65,-33,73.17),'Optical',6,'metal',internal=True)
    m.box('DVDStudyPlate','Optical drive study identification plate',44,18,.08,(-65,-31,73.4),'Optical',6,'white',.7,True)
    m.label('DVDStudyMark','DVD / CAD',3.2,(-80,-32,73.51),'Optical',6,'black')
    for i,(x,y) in enumerate([(-127,-107),(-3,-107),(-127,37),(-3,37)]):
        m.cut('DVDTop',Part.makeCylinder(.9,2,V(x,y,72.0)),'Optical cover screw passage').Refine=False
        m.screw('DVDTopScrew'+str(i),(x,y,73.65),'Optical',6,length=2.8,radius=1.5,axis=(0,0,-1))
        m.ring('DVDMountBush'+str(i),'Separate optical-drive mounting isolator',3.2,1.2,1,(x,y,42.3),'Optical',2,'rubber',internal=True)
    _strict_changed(m,prior)
    m.profile['stages']=15
    m.checkpoint(15,'tray_loading_optical_drive_native_enclosure','建立托盘式 DVD 光驱下盘、开口折边、可拆上盖、压筋、盖板螺钉及隔振支承。供应商光驱存在变体，本模型仅表示原版装配层次，不宣称特定型号的精确尺寸或内部 BOM。')
    m.snapshot('15_dvd_enclosure',assemblies=['Optical','Cooling'],normal=(.3,-.6,1.6))


STAGES[15]=stage15


def stage16(m):
    prior={k:o.Name for k,o in m.parts.items()}
    m.native('DVDTray','Editable sliding optical disc tray',128,147,2,2,(-65,-43.5,55),'Optical',4,'black')
    m.cut('DVDTray',Part.makeCylinder(61,2,V(-65,-33,55.8)),'Recessed twelve-centimetre disc seat').Refine=False
    m.cut('DVDTray',[m.rr(33,49,4,(-65,-69,54),2),Part.makeCylinder(9,4,V(-65,-33,54))],'Pickup scan and spindle clearance in tray').Refine=False
    for i,x in enumerate([-130.8,.8]):
        m.box('DVDTrayRail'+str(i),'Separate optical tray slide rail',2.2,145,2,(x,-43.5,54.8),'Optical',4,'white',.35,True)
    m.ring('DVDMedia','Blank 120 mm optical-media dimensional reference',60,7.5,1.2,(-65,-33,58.2),'Optical',5,'metal',internal=True)
    m.cyl('DVDSpindleMotor','Separate optical spindle motor envelope',7.1,6.4,(-65,-33,48),'Optical',3,'metal',internal=True)
    m.cut('DVDSpindleMotor',Part.makeCylinder(1.35,7,V(-65,-33,47.7)),'Independent spindle shaft clearance').Refine=False
    m.cyl('DVDSpindleShaft','Separate optical spindle shaft',1.1,10,(-65,-33,48.2),'Optical',4,'metal',internal=True)
    m.ring('DVDSpindleHub','Separate disc-support hub',7.2,1.3,3.4,(-65,-33,54.6),'Optical',4,'black',internal=True)
    m.ring('DVDClamp','Separate magnetic disc clamp',13,2,1.5,(-65,-33,59.6),'Optical',5,'white',internal=True)
    m.ring('DVDClampMagnet','Separate clamp magnet',6,2.2,1,(-65,-33,61.25),'Optical',5,'black',internal=True)
    for i,x in enumerate([-82,-48]):m.cyl('DVDPickupRail'+str(i),'Separate optical pickup guide rod',1.0,47,(x,-92,52),'Optical',3,'metal',axis=(0,1,0),internal=True)
    m.box('DVDPickup','Separate optical pickup sled envelope',29,16,4,(-65,-70,49.5),'Optical',3,'black',1,True)
    for i,x in enumerate([-82,-48]):m.ring('DVDPickupBearing'+str(i),'Separate pickup guide sleeve',2.1,1.15,10,(x,-75,52),'Optical',3,'white',axis=(0,1,0),internal=True)
    m.box('DVDLensCarrier','Separate optical objective actuator',10,10,1,(-65,-70,53.7),'Optical',4,'metal',.7,True)
    m.ring('DVDLensBarrel','Separate objective barrel',3.4,2.6,1.8,(-65,-70,54.85),'Optical',4,'black',internal=True)
    m.cyl('DVDLens','Separate objective lens study',2.45,.5,(-65,-70,56.1),'Optical',4,'blue',internal=True)
    _strict_changed(m,prior)
    m.profile['stages']=16
    m.checkpoint(16,'dvd_tray_spindle_blank_disc_and_pickup','建立开槽光盘托盘、独立滑轨、空白 120 mm 介质、主轴电机/轴/轮毂、磁性夹盘、光头导杆与镜片。内部行程位置和机械细节为非功能性近似，不包含游戏内容。')
    m.snapshot('16_dvd_mechanism',assemblies=['Optical'],exclude=['DVDTop','DVDTopEmboss','DVDStudyPlate','DVDStudyMark','DVDMedia','DVDClamp','DVDClampMagnet'],normal=(.3,-.6,1.6))


STAGES[16]=stage16


def stage17(m):
    prior={k:o.Name for k,o in m.parts.items()}
    from .ps3 import _study_gear,_planar_ribbon
    m.native('DVDPCB','Editable optical drive controller board study',118,141,2,1.0,(-65,-35,44.5),'Optical',3,'pcb')
    for i,(x,y,w,h) in enumerate([(-98,-39,17,17),(-27,-35,15,12),(-102,7,12,10),(-28,12,9,9)]):
        m.box('DVDLogic'+str(i),'Separate drive controller package study',w,h,1.1,(x,y,45.7),'Optical',3,'black',.3,True)
        for j in range(12):
            for side in [-1,1]:m.box('DVDLogicLead'+str(i)+'_'+str(side)+'_'+str(j),'Separate optical logic formed-contact study',.7,.32,.15,(x+side*(w/2+.45),y+(j-5.5)*.65,45.7),'Optical',3,'metal',.03,True)
    for i,(x,y) in enumerate([(-109,-74),(-24,-82),(-110,21),(-22,26)]):
        m.cyl('DVDCap'+str(i),'Separate optical-drive capacitor',2.2,2.5,(x,y,45.75),'Optical',3,'battery',internal=True)
    m.cyl('DVDLoadMotor','Separate tray-loading motor envelope',3.8,5,(-122,-101,48),'Optical',3,'metal',internal=True)
    m.cut('DVDLoadMotor',Part.makeCylinder(.8,6,V(-122,-101,47.5)),'Independent loading-motor shaft passage').Refine=False
    m.cyl('DVDLoadShaft','Separate tray-loading shaft',.55,7.0,(-122,-101,47.6),'Optical',3,'metal',internal=True)
    m.ring('DVDLoadPulley','Separate loading-motor pulley',1.8,.8,1.2,(-122,-101,53.3),'Optical',4,'white',internal=True)
    belt=m.rr(14.8,4.8,.7,(-117,-101,53.6),2.39).cut(m.rr(14,4,1,(-117,-101,53.45),1.99))
    m.feature('DVDLoadBelt','Separate tray-loading belt loop',belt,'Optical',4,'rubber',True)
    for i,x in enumerate([-112,-102.6,-93.2]):
        m.feature('DVDLoadGear'+str(i),'Separate loading reduction gear study',_study_gear(4.6,16,1.4,(x,-101,51.5),.8),'Optical',3,'white',True)
        m.cyl('DVDLoadGearAxle'+str(i),'Separate loading reduction axle',.6,3.8,(x,-101,49.4),'Optical',3,'metal',internal=True)
    m.ring('DVDDrivenPulley','Separate belt-driven reduction pulley',1.8,.8,1.0,(-112,-101,53.25),'Optical',4,'white',internal=True)
    m.box('DVDLoadingRack','Separate molded tray loading rack study',2.2,70,1.1,(-88,-79,53.65),'Optical',4,'white',.25,True)
    for i in range(25):m.box('DVDLoadingTooth'+str(i),'Separate illustrative rack tooth',.8,.8,.75,(-89.6,-111+i*2.5,53.8),'Optical',4,'white',.08,True)
    ribbon=_planar_ribbon([(-65,-80,48),(-65,-87,48),(-42,-87,48),(-42,-68,48)],7,.14,4)
    m.feature('DVDPickupFFC','Separate optical pickup flex path study',ribbon,'Optical',3,'copper',True)
    for i,(x,y) in enumerate([(-65,-80),(-42,-68)]):m.box('DVDFFCLatch'+str(i),'Separate pickup flex latch study',8,2,.8,(x,y,47.0),'Optical',3,'black',.2,True)
    # Rear seven-contact SATA data and separate drive-power connectors.
    for key,x,w,pins in [('DVDData',-103,14,7),('DVDPower',-79,18,12)]:
        rear=g.rotation((0,1,0),(0,0,1))
        body=m.rr(w,6,8,(x,39,49.5),.4,rear).cut(m.rr(w-1.2,4.8,8,(x,40,49.5),.2,rear))
        m.feature(key+'Socket','Separate optical drive rear connector housing',body,'Optical',3,'black',True)
        for i in range(pins):m.box(key+'Contact'+str(i),'Separate drive connector terminal study',.5,5,.15,(x+(i-(pins-1)/2)*(1.5 if pins==7 else 1.25),43,49.4),'Optical',3,'gold',.03,True)
    m.cut('DVDSides',[m.rr(w+1,7,3,(x,45.5,49.5),.4,g.rotation((0,1,0),(0,0,1))) for x,w in [(-103,14),(-79,18)]],'Rear optical-drive connector passages').Refine=False
    _strict_changed(m,prior)
    m.profile['stages']=17
    m.checkpoint(17,'dvd_logic_loading_drive_and_flex_connections','补齐光驱控制板与独立封装接点、托盘电机、皮带、齿轮与齿条、光头柔性线及后部 SATA/电源插座；传动齿形、数量和连线均为非功能性学习示意。')
    m.snapshot('17_dvd_loading_and_logic',assemblies=['Optical'],exclude=['DVDTop','DVDTopEmboss','DVDStudyPlate','DVDStudyMark','DVDMedia','DVDClamp','DVDClampMagnet','DVDTray'],normal=(.3,-.7,1.8))


STAGES[17]=stage17


def stage18(m):
    prior={k:o.Name for k,o in m.parts.items()}
    end=g.rotation((-1,0,0),(0,0,1))
    m.box('HDDCaddy','Removable original Premium hard-drive end housing',210,75,20,(-155.2,0,41.5),'Storage',2,'ventgray',20,True,orient=end)
    m.cut('HDDCaddy',m.rr(204,71,17.2,(-155.0,0,41.5),18,end),'Open console-side hard-drive housing cavity').Refine=False
    m.box('HDDTrim','Independent chrome end-housing insert',146,33,.2,(-175.3,0,41.5),'Storage',3,'chrome',15,True,orient=end)
    m.label('HDDCapacityMark','20 GB',4,(-175.55,12,40),'Storage',3,'ventgray',rotation=end)
    m.box('HDDRelease','Separate removable-drive release button',14,16,1,(-175.35,-94,41.5),'Storage',2,'ventgray',5,True,orient=end)
    m.cut('HDDCaddy',m.rr(14.8,16.8,7,(-171,-94,41.5),5.4,end),'Independent hard-drive release actuator opening').Refine=False
    for i,y in enumerate([-82,86]):
        m.box('HDDDockLatch'+str(i),'Separate removable-drive docking hook study',8,10,1.5,(-154.9,y,41.5),'Storage',1,'metal',1,True,orient=end)
    # 2.5-inch drive body inside the removable end housing; all local placement is approximate.
    m.box('HDDMetalBase','Separate 2.5-inch hard-drive metal base study',100,69.85,6.5,(-159,0,41.5),'Storage',2,'metal',2,True,orient=end)
    m.cut('HDDMetalBase',m.rr(98,67.8,6,(-159.7,0,41.5),1.3,end),'Open hard-drive platter and actuator cavity').Refine=False
    m.box('HDDMetalCover','Separate removable hard-drive metal cover',100,69.85,.6,(-165.8,0,41.5),'Storage',3,'metal',2,True,orient=end)
    m.box('HDDDriveLabel','Blank hard-drive study label',72,45,.06,(-166.5,0,41.5),'Storage',3,'white',1,True,orient=end)
    m.label('HDDDriveMark','20 GB / CAD',3.2,(-166.61,23,40),'Storage',3,'black',rotation=end)
    m.box('HDDPCB','Independent hard-drive controller board',88,59,.8,(-157.8,0,41.5),'Storage',1,'pcb',2,True,orient=end)
    for i,(y,z,w,h) in enumerate([(-19,39,19,19),(18,52,12,9),(20,24,11,10)]):
        m.box('HDDChip'+str(i),'Separate hard-drive controller package study',w,h,.9,(-156.7,y,z),'Storage',1,'black',.3,True,orient=end)
    for i,(y,z) in enumerate([(-42,12),(-42,71),(42,12),(42,71)]):
        m.cut('HDDMetalCover',Part.makeCylinder(.8,1.5,V(-165.5,y,z),V(-1,0,0)),'Hard-drive cover fastener hole').Refine=False
        m.cyl('HDDCoverFastener'+str(i),'Separate hard-drive cover screw head study',1.3,.25,(-166.5,y,z),'Storage',3,'metal',axis=(-1,0,0),internal=True)
    _strict_changed(m,prior)
    m.profile['stages']=18
    m.checkpoint(18,'removable_twenty_gigabyte_hdd_carrier_and_drive','加入原版 Premium 可拆 20 GB 端部硬盘组件、镀铬嵌件、释放键/挂钩及内部 2.5 英寸盘体、独立盖板和控制板。外部硬盘会超出主机本体近似包络；外壳曲率和驱动器布局不代表制造规格。')
    m.snapshot('18_original_removable_hard_drive',assemblies=['Storage'],normal=(-1,.3,.6))


STAGES[18]=stage18


def stage19(m):
    prior={k:o.Name for k,o in m.parts.items()}
    end=g.rotation((-1,0,0),(0,0,1))
    m.ring('HDDPlatter','Separate hard-drive platter study',30.5,8.3,.65,(-161,-15,41.5),'Storage',2,'metal',axis=(-1,0,0),internal=True)
    m.cyl('HDDSpindle','Independent hard-drive spindle hub',8,1.6,(-159.8,-15,41.5),'Storage',2,'metal',axis=(-1,0,0),internal=True)
    m.cyl('HDDPivot','Separate voice-coil actuator pivot',4.5,2.6,(-160,35,26),'Storage',2,'metal',axis=(-1,0,0),internal=True)
    # Actuator outline lies in YZ; its disk-facing side clears the platter plane.
    pts=[V(-162.8,y,z) for y,z in [(35,29),(6,56),(-3,58),(-6,54),(30,23)]]
    arm=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(-.65,0,0))
    m.feature('HDDActuatorArm','Separate hard-drive head actuator arm study',arm,'Storage',3,'metal',True)
    m.box('HDDHead','Separate magnetic-head envelope',2.6,2,.35,(-162.25,-4,55),'Storage',3,'black',.25,True,orient=end)
    coil=m.rr(15,12,.6,(-163.0,34,45),2,end).cut(m.rr(11,8,1,(-162.8,34,45),1.5,end))
    m.feature('HDDVoiceCoil','Separate actuator voice-coil envelope',coil,'Storage',3,'copper',True)
    m.box('HDDActuatorMagnet','Separate actuator magnet envelope',15,12,.65,(-164,34,45),'Storage',3,'black',2,True,orient=end)
    outer=m.rr(24,8,5,(-151.8,67,41.5),.7,end);inner=m.rr(22.8,6.8,5.5,(-151.55,67,41.5),.4,end)
    m.feature('HDDDockSocket','Separate proprietary removable-drive dock housing study',outer.cut(inner),'Storage',1,'black',True)
    m.box('HDDDockTongue','Separate removable-drive dock tongue study',20,1.2,4,(-152.2,67,41.5),'Storage',1,'black',.2,True,orient=end)
    for i in range(16):m.box('HDDDockContact'+str(i),'Separate illustrative docking contact; not a pinout',.6,.12,3,(-152.8,67+(i-7.5)*1.1,42.18),'Storage',1,'gold',.03,True,orient=end)
    m.cut('LeftEndGrille',m.rr(25,9,6,(-151,67,41.5),1,end),'Removable-drive docking port through left end grille').Refine=False
    m.box('HDDDriveConnector','Separate drive-edge cable carrier study',3,6,14,(-156.5,47,34.5),'Storage',1,'black',.4,True)
    m.box('HDDShortFlex','Separate removable-drive internal flex study',18,12,.18,(-157.2,59.5,41.5),'Storage',1,'copper',.5,True,orient=end)
    _strict_changed(m,prior)
    m.profile['stages']=19
    m.checkpoint(19,'hard_drive_platter_actuator_and_removable_dock','分离硬盘盘片、主轴、磁头执行器、音圈/磁体和连接软排，建立端部可拆接口及格栅贯通开口。磁盘数量、磁头和接点排列为结构示意，不代表原厂引脚定义、容量计算或存储数据。')
    m.snapshot('19_hard_drive_internal',assemblies=['Storage'],exclude=['HDDCaddy','HDDTrim','HDDCapacityMark','HDDMetalCover','HDDDriveLabel','HDDDriveMark'],normal=(-1,.3,.6))


STAGES[19]=stage19


def _board_header(m,key,x,y,width,pins):
    outer=m.rr(width,7,4,(x,y,19.7),.4)
    inner=m.rr(width-1.2,5.8,3.6,(x,y,20.6),.2)
    m.feature(key+'Header','Separate internal board header study',outer.cut(inner),'Wiring',1,'black',True)
    for i in range(pins):m.cyl(key+'HeaderPin'+str(i),'Separate illustrative board-header contact',.22,2.6,(x+(i-(pins-1)/2)*(width-3)/max(1,pins-1),y,21),'Wiring',1,'gold',internal=True)


def stage20(m):
    prior={k:o.Name for k,o in m.parts.items()}
    from .atari2600 import _rounded_route
    def wire(key,points,radius,color,targets=()):
        pts=[V(*p) for p in points];bend=2 if radius>.5 else 1.1
        m.feature(key,'Independent internal cable route study',_rounded_route(pts,bend,radius),'Wiring',2,color,True)
        if targets:
            tool=_rounded_route(pts,bend,radius+.22)
            for target in targets:m.cut(target,tool,'Insulated cable passage: '+key).Refine=False
    _board_header(m,'SATAData',-110,55,15,7)
    wire('DVDDataCable',[(-103,47.2,49.5),(-103,55,49.5),(-110,55,49.5),(-110,55,24.1)],1.0,'red')
    _board_header(m,'DVDPower',-87,65,18,12)
    for i in range(4):
        d=(i-1.5)*.8
        wire('DVDPowerWire'+str(i),[(-79+d,47.2,49.5),(-79+d,65,49.5),(-87+d,65,49.5),(-87+d,65,24.1)],.25,'black' if i%2 else 'white')
    _board_header(m,'RFLink',35,-103,10,4)
    rear=g.rotation((0,1,0),(0,0,1))
    m.box('RFLinkBoardPlug','Separate RF board interconnect carrier study',7,7,2,(35,-121.5,44),'Wireless',2,'white',.3,True,orient=rear)
    for i in range(4):
        x=34+i*.7
        wire('RFLinkWire'+str(i),[(x,-119.2,44),(x,-111,44),(x,-103,31),(x,-103,24.1)],.18,'white')
    _board_header(m,'IRLink',-131,-102,10,3)
    for i in range(3):
        x=-142+i*.8;end=-132+i*.8
        wire('IRLinkWire'+str(i),[(x,-121.7,31),(x,-110,31),(end,-102,31),(end,-102,24.1)],.18,'black')
    for j,(cx,endx) in enumerate([(-28,-73),(36,90)]):
        endy=84 if j==0 else 89
        _board_header(m,'FanLink'+str(j),endx,endy,10,3)
        for i in range(3):
            z=42+(i-1)*.8;yy=94-i*.8;xx=endx+(i-1)*.8
            wire('FanWire'+str(j)+'_'+str(i),[(cx+7,99.7,z),(cx+7,yy,z),(xx,yy,z),(xx,endy,z),(xx,endy,24.1)],.18,['black','red','white'][i],['GPUAirDuct' if j==0 else 'CPUAirDuct'])
    _board_header(m,'HDDLink',-130,58,10,6)
    wire('HDDInternalCable',[(-151.5,67,41.5),(-139,67,41.5),(-130,58,41.5),(-130,58,24.1)],1.05,'black',['Chassis'])
    _strict_changed(m,prior)
    m.profile['stages']=20
    m.checkpoint(20,'internal_dvd_rf_ir_fan_and_hdd_harnesses','补齐光驱数据/电源、前端 RF/红外、双风扇与可拆硬盘内部线束，分离主板插座及接点，并加工绝缘导线的底盘/风罩通道。线色、芯数、路径和端点为静态结构示意，不提供真实电气接线。')
    m.snapshot('20_internal_harnesses',assemblies=['Mainboard','Wiring','Wireless','Cooling'],exclude=['GPUAirDuct','CPUAirDuct'],normal=(.25,-.6,1.8))


STAGES[20]=stage20


def stage21(m):
    prior={k:o.Name for k,o in m.parts.items()}
    import math
    shield=_curved_panel(m,'UpperShield','Editable curved upper electromagnetic shield',288,237,79.5,73.9,-.25,119.5,6)
    m.group('Body').removeObject(shield);m.register(shield,'UpperShield','Shielding',6,'metal',True)
    holes=[Part.makeCylinder(1.65,15,V(x,y,70)) for x in [-143,-137,-131,131,137,143] for y in range(-105,106,7)]
    m.cut('UpperShield',holes,'Ventilation passages aligned with the upper shell').Refine=False
    mounts=[(x,y) for x in [-139.8,139.8] for y in [-94,94]]
    for i,(x,y) in enumerate(mounts):
        m.ring('CasePillar'+str(i),'Separate case screw guide sleeve',1.8,.85,66.2,(x,y,12.1),'Frame',2,'ivory',internal=True)
        m.ring('CaseLowerSupport'+str(i),'Separate lower case support boss',2.0,1.6,5.7,(x,y,4.0),'Frame',-4,'ivory',internal=True)
        m.screw('CaseLongScrew'+str(i),(x,y,10.15),'Frame',-4,length=68,radius=1.4)
    m.cut('Chassis',[Part.makeCylinder(.95,2,V(x,y,10.3)) for x,y in mounts],'Long case screw passages through chassis').Refine=False
    m.cut('UpperShield',[Part.makeCylinder(1.4,5,V(x,y,76)) for x,y in mounts],'Upper case retention clearances').Refine=False
    radius=(152**2+6.5**2)/13
    for i,(letter,x) in enumerate(zip('XBOX360',[-30,-22,-14,-6,10,18,26])):
        mid=x+3;slope=mid/math.sqrt(radius**2-mid**2)
        z=76.3+radius-math.sqrt(radius**2-mid**2)-3*slope+.06
        m.label('CaseWordmark'+str(i),letter,8,(x,-4,z),'Body',8,'ivory',rotation=g.rotation((-slope,0,1),(0,1,0)))
    for i,(x,y,z) in enumerate([(x,y,z) for x in [-149,149] for y in [-115,115] for z in [20,55]]):
        m.box('ShellClip'+str(i),'Separate internal case retention tab study',1.5,5,3,(x,y,z),'Frame',1,'ivory',.35,True)
    _strict_changed(m,prior)
    m.profile['stages']=21
    m.checkpoint(21,'curved_upper_shield_case_fasteners_and_embossed_mark','补齐原生曲面金属上屏蔽、对齐通风孔、独立机壳长紧固件/导向柱/卡扣及顺曲面排列的外壳字样。固定数量、位置和分离间隙为装配学习近似。')
    m.snapshot('21_complete_console_structure',assemblies=['Body','Controls','Ports','Storage','Frame'],normal=(.4,-1.1,.8))


STAGES[21]=stage21


def _pad_point(x,y,z):
    return V(x,y-260,z)


def _pad_curves(sx=1,sy=1):
    right=[[(0,42),(20,42),(34,42),(49,40)],[(49,40),(65,38),(77,28),(77,10)],[(77,10),(75,-17),(68,-60),(54,-63)],[(54,-63),(42,-63),(30,-33),(20,-25)],[(20,-25),(13,-21),(7,-22),(0,-22)]]
    outline=right+[[(-x,y) for x,y in reversed(segment)] for segment in reversed(right)]
    curves=[]
    for segment in outline:
        curve=Part.BezierCurve();curve.setPoles([V(x*sx,y*sy) for x,y in segment]);curves.append(curve.toBSpline())
    return curves


def _pad_loft(m,key,profiles):
    sketches=[]
    for i,(sx,sy,z) in enumerate(profiles):
        sk=m.doc.addObject('Sketcher::SketchObject',key+'Profile'+str(i));sk.Label='Wireless controller editable grip section '+str(i+1)
        sk.addGeometry(_pad_curves(sx,sy),False);sk.Placement=App.Placement(_pad_point(0,0,z),App.Rotation())
        m.group('Construction').addObject(sk);sketches.append(sk)
    obj=m.doc.addObject('Part::Loft',key);obj.Sections=sketches;obj.Solid=True;obj.Ruled=False;obj.Closed=False;obj.MaxDegree=3
    m.doc.recompute();obj.Shape.check(True);assert len(obj.Shape.Solids)==1
    m.group('Construction').addObject(obj)
    for sk in sketches:sk.Visibility=False
    obj.Visibility=False;return obj


def _pad_shell(m,key,outer,inner,layer):
    a=_pad_loft(m,key+'Outer',outer);b=_pad_loft(m,key+'Inner',inner)
    obj=m.doc.addObject('Part::Cut',key);obj.Base=a;obj.Tool=b;obj.Refine=False;m.doc.recompute()
    obj.Shape.check(True);assert len(obj.Shape.Solids)==1
    a.Visibility=False;b.Visibility=False
    return m.register(obj,key,'Controller',layer,'ivory')


def stage22(m):
    prior={k:o.Name for k,o in m.parts.items()}
    _pad_shell(m,'PadBack',[(.86,.87,1),(.95,.95,7),(1,1,16),(1,1,21.7)],[(.82,.83,3.2),(.912,.911,7),(.966,.966,16),(.966,.966,21.9)],-4)
    _pad_shell(m,'PadFront',[(1,1,22),(.985,.981,28),(.95,.95,33)],[(.966,.966,21.8),(.952,.948,27.5),(.914,.914,30.8)],4)
    m.cut('PadBack',m.rr(37,55,25,tuple(_pad_point(0,9,-18)),3),'Open rear bay for removable two-AA holder').Refine=False
    _strict_changed(m,prior)
    m.profile['stages']=22
    m.checkpoint(22,'wireless_controller_native_grip_shell_and_aa_bay','建立白色无线控制器的上下原生曲线放样壳、分缝及背面双 AA 电池座开口。外形参考 Microsoft 同家族手柄规格和原版照片，曲率与内部间隙为学习近似；不混入后期变形十字键或 USB-C。')
    m.snapshot('22_wireless_controller_shell',assemblies=['Controller'],normal=(.3,-.6,1.9))


STAGES[22]=stage22


def stage23(m):
    prior={k:o.Name for k,o in m.parts.items()}
    m.colors.update(yellow=(.9,.68,.06))
    holes=[Part.makeCylinder(r,9,_pad_point(x,y,27)) for x,y,r in [(-43,16,12.1),(25,-10,12.1),(-24,-7,15.5),(0,17,10)]]
    buttons=[('Y',46,22,'yellow'),('X',33,9,'blue'),('B',59,9,'red'),('A',46,-4,'xboxgreen')]
    holes += [Part.makeCylinder(4.8,9,_pad_point(x,y,27)) for _,x,y,_ in buttons]
    holes += [m.rr(6.8,4.8,9,tuple(_pad_point(x,16,27)),2.2) for x in [-17,17]]
    holes += [m.rr(28,11,10,tuple(_pad_point(x,34,26)),3) for x in [-47,47]]
    m.cut('PadFront',holes,'Original asymmetric stick D-pad ABXY guide menu and bumper openings').Refine=False
    for i,(x,y) in enumerate([(-43,16),(25,-10)]):
        dome=Part.makeSphere(11.6,_pad_point(x,y,29)).common(Part.makeCylinder(12,5,_pad_point(x,y,29.5)))
        dome=dome.cut(Part.makeCylinder(3,6,_pad_point(x,y,29)))
        m.feature('PadStickDome'+str(i),'Separate original analog-stick dust dome',dome,'Controller',3,'ventgray',True)
        m.cyl('PadStickStem'+str(i),'Separate analog-stick shaft',2.6,12.2,tuple(_pad_point(x,y,29)),'Controller',3,'ventgray',internal=True)
        cap=Part.makeCylinder(9.9,2.6,_pad_point(x,y,41.4)).cut(Part.makeSphere(24,_pad_point(x,y,66.5)))
        m.feature('PadStickCap'+str(i),'Concave original rubber thumb cap',cap,'Controller',5,'rubber')
        for j,(dx,dy) in enumerate([(-8.9,0),(8.9,0),(0,-8.9),(0,8.9)]):m.cyl('PadStickNub'+str(i)+'_'+str(j),'Separate thumb-cap tactile dot study',.6,.15,tuple(_pad_point(x+dx,y+dy,44.05)),'Controller',5,'rubber')
    m.cyl('PadDPadDish','Separate original fixed circular D-pad carrier',14.5,1.7,tuple(_pad_point(-24,-7,31.6)),'Controller',4,'ventgray')
    m.ring('PadDPadRim','Separate fixed D-pad perimeter rim',15.2,14.7,1.7,tuple(_pad_point(-24,-7,31.6)),'Controller',4,'ventgray')
    cross=m.rr(6,25,2,tuple(_pad_point(-24,-7,33.5)),1.5).fuse(m.rr(25,6,2,tuple(_pad_point(-24,-7,33.5)),1.5)).removeSplitter()
    m.feature('PadDPadCross','Original fixed cross; no later transforming mechanism',cross,'Controller',5,'ventgray')
    for letter,x,y,color in buttons:
        cap=Part.makeCylinder(4.3,7,_pad_point(x,y,28.5))
        cap=cap.makeFillet(.7,[e for e in cap.Edges if e.BoundBox.ZLength<1e-7 and e.BoundBox.ZMax>35.49])
        m.feature('PadButton'+letter,'Separate colored '+letter+' button',cap,'Controller',4,color)
        m.label('PadButtonMark'+letter,letter,3.5,tuple(_pad_point(x-1.3,y-1.25,35.56)),'Controller',5,'white')
    m.cyl('PadGuide','Separate original Xbox Guide button',8.1,3,tuple(_pad_point(0,17,31.5)),'Controller',4,'chrome')
    m.ring('PadGuideCarrier','Separate four-sector player ring carrier',9.7,8.4,1,tuple(_pad_point(0,17,32.1)),'Controller',4,'ventgray')
    for i in range(4):
        arc=Part.makeCylinder(9.4,.5,V(),V(0,0,1),82).cut(Part.makeCylinder(8.8,.7,V(0,0,-.1)))
        arc.rotate(V(),V(0,0,1),i*90+4);arc.translate(_pad_point(0,17,33.35))
        m.feature('PadGuideQuadrant'+str(i),'Separate controller player-light sector',arc,'Controller',4,'xboxgreen')
    m.label('PadGuideMark','X',10,tuple(_pad_point(-3.4,13.4,34.57)),'Controller',5,'xboxgreen')
    for i,x in enumerate([-17,17]):
        m.box('PadMenuButton'+str(i),'Separate Back or Start button',6,4,3.5,tuple(_pad_point(x,16,30.5)),'Controller',4,'ivory',1.8)
        m.label('PadMenuMark'+str(i),'<' if i==0 else '>',2.2,tuple(_pad_point(x-.8,15.2,34.07)),'Controller',5,'ventgray')
    for i,x in enumerate([-47,47]):
        m.box('PadBumper'+str(i),'Separate original left or right bumper',27,10,6.5,tuple(_pad_point(x,34,28)),'Controller',4,'ivory',2.8)
        m.label('PadBumperMark'+str(i),'LB' if i==0 else 'RB',3,tuple(_pad_point(x-3,33,34.57)),'Controller',5,'ventgray')
    _strict_changed(m,prior)
    m.profile['stages']=23
    m.checkpoint(23,'original_asymmetric_sticks_fixed_dpad_abxy_and_guide','加工原版非对称双摇杆、固定十字键、彩色 ABXY、Guide 四分区灯环、Back/Start 和肩键开口；独立按键、凹面拇指帽与触点凸粒分件表达，后续补齐摇杆、导电胶和扳机内部。')
    m.snapshot('23_original_wireless_controls',assemblies=['Controller'],normal=(.2,-.45,2))


STAGES[23]=stage23


def stage24(m):
    prior={k:o.Name for k,o in m.parts.items()}
    points=[(-62,33),(-68,3),(-54,-28),(-39,-28),(-30,-20),(30,-20),(39,-28),(54,-28),(68,3),(62,33),(21,33),(21,37),(-21,37),(-21,33)]
    sk=m.doc.addObject('Sketcher::SketchObject','PadPCBOutline');sk.Label='Original wireless controller editable mainboard outline'
    vectors=[V(x,y) for x,y in points]
    sk.addGeometry([Part.LineSegment(a,b) for a,b in zip(vectors,vectors[1:]+vectors[:1])],False)
    sk.Placement=App.Placement(_pad_point(0,0,19),App.Rotation());m.group('Construction').addObject(sk)
    pcb=m.doc.addObject('Part::Extrusion','PadPCBExtrusion');pcb.Base=sk;pcb.DirMode='Normal';pcb.LengthFwd=1.2;pcb.Solid=True
    m.doc.recompute();sk.Visibility=False;m.register(pcb,'PadPCB','Controller',0,'pcb',True)
    holes=[Part.makeCylinder(1.6,2,_pad_point(x,y,18.7)) for x,y in [(-59,23),(59,23),(0,-16),(-35,-22),(35,-22)]]
    holes.append(m.rr(21,9,2,tuple(_pad_point(0,34.5,18.7)),.5))
    m.cut('PadPCB',holes,'Controller board fixings and original charge-connector recess').Refine=False
    for i,(x,y) in enumerate([(-59,23),(59,23),(0,-16),(-35,-22),(35,-22)]):m.ring('PadPCBMountLand'+str(i),'Separate controller board fixing land',2.5,1.7,.05,tuple(_pad_point(x,y,20.23)),'Controller',0,'gold',internal=True)
    m.box('PadBaseband','Early controller leaded baseband package study',20,20,1.2,tuple(_pad_point(-12,4,17.1)),'Controller',-1,'black',.4,True)
    for side in range(4):
        for i in range(16):
            a=-8.25+i*1.1
            x,y=(-12+a,4+10.7) if side==0 else ((-12+a,4-10.7) if side==1 else ((-12+10.7,4+a) if side==2 else (-12-10.7,4+a)))
            m.box('PadBasebandLead'+str(side)+'_'+str(i),'Separate illustrative QFP lead',.3 if side<2 else .8,.8 if side<2 else .3,.25,tuple(_pad_point(x,y,18.4)),'Controller',-1,'metal',.03,True)
    m.box('PadRFPCB','Separate early controller radio daughterboard',24,24,.65,tuple(_pad_point(16,8,16.4)),'Controller',-2,'pcb',.5,True)
    frame=m.rr(25.5,25.5,2.3,tuple(_pad_point(16,8,13.8)),.6).cut(m.rr(24.7,24.7,2.6,tuple(_pad_point(16,8,13.65)),.3))
    m.feature('PadRFShieldFrame','Separate early radio shield frame',frame,'Controller',-2,'metal',True)
    m.box('PadRFShieldLid','Separate removable radio shield lid',25.5,25.5,.2,tuple(_pad_point(16,8,13.5)),'Controller',-3,'metal',.6,True)
    m.box('PadRFChip','Separate original-family radio package envelope',8,8,1.4,tuple(_pad_point(16,5,14.5)),'Controller',-2,'black',.25,True)
    m.box('PadRFClock','Separate radio reference resonator',8,2.5,1.5,tuple(_pad_point(16,15,14.4)),'Controller',-2,'metal',.5,True)
    for i in range(12):m.cyl('PadRFBoardPin'+str(i),'Separate radio daughterboard attachment contact',.2,1.4,tuple(_pad_point(5.8,8+(i-5.5)*1.7,17.3)),'Controller',-1,'gold',internal=True)
    m.box('PadPowerContactCarrier','Separate battery/recharge contact carrier study',15,6,2.6,tuple(_pad_point(0,-10,14.4)),'Controller',-2,'white',.5,True)
    for i in range(6):m.box('PadPowerContact'+str(i),'Separate rechargeable-pack interface contact study',1.2,3.5,.12,tuple(_pad_point((i-2.5)*2.1,-10,14.2)),'Controller',-3,'gold',.08,True)
    m.box('PadClock','Separate main controller reference crystal',11,3,1.6,tuple(_pad_point(-4,0,20.5)),'Controller',1,'metal',.6,True)
    m.label('PadPCBMark','2005 RF / CAD',1.7,tuple(_pad_point(-11,-5,20.25)),'Controller',1,'white')
    _strict_changed(m,prior)
    m.profile['stages']=24
    m.checkpoint(24,'early_wireless_controller_board_baseband_and_rf_module','按 2005 年 FCC 样品建立原生主板、引脚式主控、分离射频子板/可拆屏蔽罩、晶振及电池/充电接点。主板与局部封装为学习近似，明确区别后续 WC01 无线芯片组改款；引脚数量不构成原厂电路。')
    m.snapshot('24_early_wireless_controller_board',assemblies=['Controller'],exclude=['PadFront','PadBack'],normal=(.2,-.5,1.8))


STAGES[24]=stage24


def _pad_contact(m,key,x,y,radius):
    for i in range(2):
        half=Part.makeCylinder(radius,.05,V(),V(0,0,1),180)
        half.rotate(V(),V(0,0,1),i*180)
        half=half.cut(Part.makeBox(radius*2+2,.4,.3,V(-radius-1,-.2,-.1)))
        half.translate(_pad_point(x,y,20.28))
        m.feature(key+'Contact'+str(i),'Separate split controller button contact study',half,'Controller',1,'gold',True)


def stage25(m):
    prior={k:o.Name for k,o in m.parts.items()}
    face=[('Y',46,22,5,3,6.5,3.1),('X',33,9,5,3,6.5,3.1),('B',59,9,5,3,6.5,3.1),('A',46,-4,5,3,6.5,3.1),('Guide',0,17,7,6,9.3,4.8),('Back',-17,16,3.4,2.4,8.4,2.2),('Start',17,16,3.4,2.4,8.4,2.2)]
    solids=[m.rr(82,10,.5,tuple(_pad_point(21,12,21.2)),2),m.rr(4,30,.5,tuple(_pad_point(46,9,21.2)),1)];cavities=[]
    for key,x,y,base,top,height,contact in face:
        _pad_contact(m,'Pad'+key,x,y,contact)
        solids += [Part.makeCylinder(base+.3,.7,_pad_point(x,y,21)),Part.makeCone(base,top,height,_pad_point(x,y,21.6))]
        cavities.append(Part.makeCone(base-.6,top-.6,height+.1,_pad_point(x,y,20.9)))
        m.cyl('Pad'+key+'Carbon','Separate conductive elastomer pill',contact-.45,.3,tuple(_pad_point(x,y,20.45)),'Controller',1,'black',internal=True)
    membrane=solids[0].multiFuse(solids[1:]).removeSplitter().cut(Part.makeCompound(cavities))
    m.feature('PadFaceMembrane','Separate common ABXY Guide and menu silicone membrane',membrane,'Controller',2,'rubber',True)
    solids=[Part.makeCylinder(12.8,.7,_pad_point(-24,-7,21))];cavities=[]
    for i,(x,y) in enumerate([(-24,-.5),(-17.5,-7),(-24,-13.5),(-30.5,-7)]):
        _pad_contact(m,'PadDPad'+str(i),x,y,3.1)
        solids.append(Part.makeCone(4.4,3.2,8.8,_pad_point(x,y,21.6)))
        cavities.append(Part.makeCone(3.8,2.6,8.9,_pad_point(x,y,20.9)))
        m.cyl('PadDPadCarbon'+str(i),'Separate directional carbon contact',2.65,.3,tuple(_pad_point(x,y,20.45)),'Controller',1,'black',internal=True)
        m.cyl('PadDPadPushrod'+str(i),'Separate fixed-cross pressure pad study',2.5,.8,tuple(_pad_point(x,y,30.6)),'Controller',3,'ventgray',internal=True)
    membrane=solids[0].multiFuse(solids[1:]).removeSplitter().cut(Part.makeCompound(cavities))
    m.feature('PadDPadMembrane','Separate four-direction silicone membrane',membrane,'Controller',2,'rubber',True)
    _strict_changed(m,prior)
    m.profile['stages']=25
    m.checkpoint(25,'controller_split_contacts_and_separate_silicone_membranes','补齐主板分离接点、ABXY/Guide/菜单共用导电胶与四方向独立胶垫，分别建立弹性锥壁、碳粒和十字键压力垫；保留接点与静止碳粒之间的间隙。该机构为静态结构学习，不模拟实际力学或电路。')
    m.snapshot('25_controller_contact_stack',assemblies=['Controller'],exclude=['PadFront','PadBack','PadFaceMembrane','PadDPadMembrane'],normal=(.2,-.4,2))


STAGES[25]=stage25


# Reuse the established schematic two-axis module construction with Xbox placement.
def _pad_joystick(m,index,x,y):
    from .atari2600 import _helical_spring
    key='PadJoy'+str(index);y-=260;holes=[]
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
    m.feature(key+'OuterGimbal','X-axis gimbal and potentiometer axle',outer,'Controller',2,'ivory',True)
    inner=m.rr(9.5,8.5,1.5,(x,y,19.15),.4).cut(m.rr(7,6.2,1.9,(x,y,18.95),.2))
    inner=inner.multiFuse([Part.makeCylinder(.75,4.8,V(x,y-7.9,19.9),V(0,1,0)),Part.makeCylinder(.75,7.3,V(x,y+3.05,19.9),V(0,1,0))])
    inner=inner.cut(Part.makeCylinder(1.0,11,V(x-5.5,y,20),V(1,0,0)))
    m.feature(key+'InnerGimbal','Y-axis gimbal and potentiometer axle',inner,'Controller',2,'ivory',True)
    shaft=Part.makeSphere(2.2,V(x,y,20.8)).fuse(Part.makeCylinder(1.75,8.55,V(x,y,21.3)))
    shaft=shaft.fuse(Part.makeCylinder(.8,9.2,V(x-4.6,y,20),V(1,0,0)))
    m.feature(key+'Shaft','Joystick pivot ball, cross pin and cap shaft',shaft,'Controller',3,'metal',True)
    spring=_helical_spring(1.2,.6,1.8,.12);spring.translate(V(x,y,15.8))
    m.feature(key+'ClickSpring','Joystick push-click return spring study',spring,'Controller',1,'metal',True)
    m.box(key+'ClickSwitch','Left/right stick click switch body',3,3,1.5,(x-5,y,15.8),'Controller',1,'black',.3,True)
    m.cyl(key+'ClickActuator','Left/right stick switch actuator',.8,.4,(x-5,y,17.4),'Controller',2,'black',internal=True)
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
        m.feature(key+suffix+'Rotor','Potentiometer rotor disc',rotor,'Controller',2,'ivory',True)
        m.ring(key+suffix+'Track','Potentiometer resistive track',2.25,1.7,.035,tuple(center+normal*10.68),'Controller',2,'black',axis=axis,internal=True)
        wiper=m.rr(.35,2.6,.05,tuple(center+normal*10.80),.05,q)
        m.feature(key+suffix+'Wiper','Potentiometer moving wiper study',wiper,'Controller',2,'metal',True)
    return holes


def stage26(m):
    prior={k:o.Name for k,o in m.parts.items()}
    holes=[]
    for i,(x,y) in enumerate([(-43,16),(25,-10)]):
        before=set(m.parts)
        bores=_pad_joystick(m,i,x,y)
        for key in set(m.parts)-before:
            obj=m.parts[key];placement=obj.Placement;placement.Base.z+=6.2;obj.Placement=placement;obj.FlatPlacement=obj.Placement
        for bore in bores:bore.translate(V(0,0,6.2));holes.append(bore)
        m.cut('PadStickStem'+str(i),Part.makeCylinder(2,8,_pad_point(x,y,28.8)),'Independent metal joystick shaft inside rubber cap neck').Refine=False
    m.cut('PadPCB',holes,'Joystick frame anchors and independent potentiometer and click terminals').Refine=False
    _strict_changed(m,prior)
    m.profile['stages']=26
    m.checkpoint(26,'asymmetric_two_axis_joysticks_pots_and_click_switches','补齐非对称双摇杆的金属笼架、双轴万向支架、球轴、电位器壳/转子/电阻轨道/滑片和按下开关，加入独立弹簧、穿板端子及拇指帽颈部轴孔。机构尺寸与轨道为学习近似。')
    m.snapshot('26_wireless_analog_mechanisms',assemblies=['Controller'],exclude=['PadFront','PadBack','PadFaceMembrane','PadDPadMembrane','PadStickCap0','PadStickCap1','PadStickDome0','PadStickDome1'],normal=(.4,-.7,1.8))


STAGES[26]=stage26


def stage27(m):
    prior={k:o.Name for k,o in m.parts.items()}
    from .atari2600 import _helical_spring
    holes=[]
    for i,side in enumerate([-1,1]):
        x=side*47;axis=V(side,0,0);orient=g.rotation((side,0,0),(0,0,1))
        m.cut('PadBack',m.rr(25,17.2,19,tuple(_pad_point(x,33,4)),3),'Independent analog trigger opening').Refine=False
        trigger=m.rr(24,16,10,tuple(_pad_point(x,33,7.5)),3).cut(m.rr(20,12,10,tuple(_pad_point(x,33,9)),2))
        trigger=trigger.cut(Part.makeCylinder(1.0,27,_pad_point(x-13.5,31,16),V(1,0,0)))
        m.feature('PadTrigger'+str(i),'Separate original white analog trigger',trigger,'Controller',-3,'ivory')
        bracket=m.rr(19,1.2,.6,tuple(_pad_point(x,31,18.1)),.1)
        walls=[m.rr(.7,5,6.7,tuple(_pad_point(x+dx,31,12)),.1) for dx in [-8.8,8.8]]
        bracket=bracket.multiFuse(walls).removeSplitter()
        bracket=bracket.cut(Part.makeCylinder(1.1,21,_pad_point(x-10.5,31,16),V(1,0,0)))
        bracket=bracket.cut(m.rr(6.6,6.6,3,tuple(_pad_point(x+side*5.4,31,16)),.5,orient))
        m.feature('PadTriggerBracket'+str(i),'Separate early black trigger bracket study',bracket,'Controller',-2,'black',True)
        m.cyl('PadTriggerAxle'+str(i),'Separate analog trigger pivot axle',.75,25,tuple(_pad_point(x-12.5,31,16)),'Controller',-2,'metal',axis=(1,0,0),internal=True)
        spring=_helical_spring(1.35,.7,4.2,.15);spring.rotate(V(),V(0,1,0),90);spring.translate(_pad_point(x-2.1,31,16))
        m.feature('PadTriggerSpring'+str(i),'Separate trigger return coil study',spring,'Controller',-2,'metal',True)
        center=_pad_point(x,31,16)
        pot=m.rr(6,6,2.3,tuple(center+axis*5.7),.4,orient)
        pot=pot.cut(Part.makeCylinder(2.5,1.6,center+axis*6.8,axis)).cut(Part.makeCylinder(1.0,3,center+axis*5.4,axis))
        pinbores=[]
        for j,dy in enumerate([-1.8,0,1.8]):
            px=x+side*7.1;py=31+dy
            m.cyl('PadTriggerPotPin'+str(i)+'_'+str(j),'Separate trigger potentiometer terminal',.18,2.35,tuple(_pad_point(px,py,18.55)),'Controller',-1,'metal',internal=True)
            pinbores.append(Part.makeCylinder(.3,1,_pad_point(px,py,18.4)))
            holes.append(Part.makeCylinder(.3,1.7,_pad_point(px,py,18.8)))
        m.feature('PadTriggerPot'+str(i),'Separate trigger potentiometer housing',pot.cut(Part.makeCompound(pinbores)),'Controller',-2,'black',True)
        m.ring('PadTriggerRotor'+str(i),'Separate trigger potentiometer rotor',2.25,1.0,.25,tuple(center+axis*7.0),'Controller',-2,'ivory',axis=(side,0,0),internal=True)
        m.ring('PadTriggerTrack'+str(i),'Separate trigger resistive track study',2.2,1.65,.035,tuple(center+axis*7.4),'Controller',-2,'black',axis=(side,0,0),internal=True)
        m.box('PadTriggerWiper'+str(i),'Separate trigger moving contact study',.3,1,.04,tuple(center+axis*7.65+V(0,0,1.65)),'Controller',-2,'metal',.03,True,orient=orient)
        m.box('PadBumperSwitch'+str(i),'Separate bumper tactile switch',4,3,2,tuple(_pad_point(side*57,30,20.5)),'Controller',1,'metal',.3,True)
        m.cyl('PadBumperPlunger'+str(i),'Separate bumper pressure-transfer stem',.7,5,tuple(_pad_point(side*57,30,22.7)),'Controller',2,'ivory',internal=True)
        m.label('PadTriggerMark'+str(i),'LT' if side<0 else 'RT',3,tuple(_pad_point(x+3,32,7.42)),'Controller',-4,'ventgray',rotation=g.rotation((0,0,-1),(0,1,0)))
    m.cut('PadPCB',holes,'Separate original trigger potentiometer through-board terminals').Refine=False
    _strict_changed(m,prior)
    m.profile['stages']=27
    m.checkpoint(27,'early_white_triggers_black_brackets_return_springs_and_pots','加入原版白色扳机、早期黑色支架、独立轴与回位线圈、扳机电位器内部件和穿板端子，补齐肩键触点及传力柱；机构参考 2005 年样品，不用后期黑色手柄的白色支架代替。')
    m.snapshot('27_original_trigger_mechanisms',assemblies=['Controller'],exclude=['PadBack','PadFront','PadRFShieldLid'],normal=(.35,.7,-1.8))


STAGES[27]=stage27


def stage28(m):
    prior={k:o.Name for k,o in m.parts.items()}
    import math
    from .atari2600 import _helical_spring,_rounded_route
    for j,(x,radius,height) in enumerate([(-51,9,9),(51,7.5,8)]):
        motor_prior=set(m.parts)
        z=16-height;cy=-42
        m.ring('PadRumbleCan'+str(j),'Separate unequal rumble motor metal can',radius,radius-.55,height,tuple(_pad_point(x,cy,z)),'Controller',-2,'metal',internal=True)
        for k,zz in enumerate([z-.6,16.2]):m.ring('PadRumbleEnd'+str(j)+'_'+str(k),'Separate rumble motor end bell',radius,.9,.4,tuple(_pad_point(x,cy,zz)),'Controller',-2,'metal',internal=True)
        m.ring('PadRumbleMagnet'+str(j),'Separate motor magnet envelope',radius-.9,radius-2.4,height-1.2,tuple(_pad_point(x,cy,z+.3)),'Controller',-2,'black',internal=True)
        m.ring('PadRumbleRotor'+str(j),'Separate motor armature core',1.8,.9,height-1.5,tuple(_pad_point(x,cy,z+.4)),'Controller',-2,'metal',internal=True)
        for k in range(3):
            a=k*2*math.pi/3;rr=3.5 if j==0 else 3.0;ro=1.25 if j==0 else .9
            m.ring('PadRumbleCoil'+str(j)+'_'+str(k),'Separate armature winding envelope',ro,ro*.45,height-2.2,tuple(_pad_point(x+rr*math.cos(a),cy+rr*math.sin(a),z+.75)),'Controller',-2,'copper',internal=True)
        m.cyl('PadRumbleShaft'+str(j),'Separate rumble motor shaft',.7,20.7-(z-.4),tuple(_pad_point(x,cy,z-.4)),'Controller',-1,'metal',internal=True)
        weight=Part.makeCylinder(radius,2.4,_pad_point(x,cy,17.6),V(0,0,1),180).cut(Part.makeCylinder(1.1,3,_pad_point(x,cy,17.3)))
        m.feature('PadRumbleWeight'+str(j),'Separate eccentric semicircular vibration mass',weight,'Controller',0,'metal',True)
        m.ring('PadRumbleCradle'+str(j),'Separate motor-retaining grip cradle',radius+.7,radius+.25,height+.5,tuple(_pad_point(x,cy,z-.2)),'Controller',-2,'ivory',internal=True)
        m.box('PadRumblePlug'+str(j),'Separate two-wire motor connector carrier',6,4,1.7,tuple(_pad_point(-50 if j==0 else 50,-24,16.5)),'Controller',-1,'white',.4,True)
        for i in range(2):
            sx=x+(-2.6 if i==0 else 2.6);ex=(-50 if j==0 else 50)+(i-.5)*.8
            points=[_pad_point(sx,-44,16.9),_pad_point(sx,-31,16.9),_pad_point(ex,-28,16.9),_pad_point(ex,-26.3,16.9)]
            m.feature('PadRumbleWire'+str(j)+'_'+str(i),'Separate rumble motor lead',_rounded_route(points,.5,.12),'Controller',-1,'red' if i else 'black',True)
        if j==0:
            for key in set(m.parts)-motor_prior:
                obj=m.parts[key];placement=obj.Placement;placement.Base.z+=.8;obj.Placement=placement;obj.FlatPlacement=obj.Placement
    m.box('PadAAHolder','Removable original two-AA battery holder',37,55,18.2,tuple(_pad_point(0,9,-17.1)),'Controller',-5,'ivory',3)
    m.cut('PadAAHolder',m.rr(35,53,18,tuple(_pad_point(0,9,-15.6)),2.2),'Open two-cell battery cradle').Refine=False
    m.box('PadAADivider','Separate battery cradle center divider',1.2,51.5,14.8,tuple(_pad_point(0,9,-15.3)),'Controller',-4,'ivory',.2,True)
    rear=g.rotation((0,1,0),(0,0,1))
    m.box('PadAALatch','Separate battery-pack release catch',14,9,1.3,tuple(_pad_point(0,36.7,-7.5)),'Controller',-4,'ivory',2,True,orient=rear)
    pcbholes=[]
    for i,x in enumerate([-8.1,8.1]):
        sign=1 if i==0 else -1;start=-15.5 if i==0 else 33.7
        m.cyl('PadAA'+str(i),'Independent AA LR6 cell dimensional envelope',7.1,49.2,tuple(_pad_point(x,start,-7.5)),'Controller',-4,'battery',axis=(0,sign,0),internal=True)
        pos=start+sign*49.4
        m.cyl('PadAAPositive'+str(i),'Separate AA positive button',2.5,.5,tuple(_pad_point(x,pos,-7.5)),'Controller',-4,'metal',axis=(0,sign,0),internal=True)
        m.cyl('PadAANegative'+str(i),'Separate AA flat negative terminal',6.7,.15,tuple(_pad_point(x,start-sign*.15,-7.5)),'Controller',-4,'metal',axis=(0,-sign,0),internal=True)
        spring=_helical_spring(2.2,.5,1.0,.15);spring.rotate(V(),V(1,0,0),-90 if sign==1 else 90);spring.translate(_pad_point(x,-17.2 if sign==1 else 35.3,-7.5))
        m.feature('PadAASpring'+str(i),'Separate AA holder compression spring',spring,'Controller',-4,'metal',True)
        m.box('PadAAPositiveLeaf'+str(i),'Separate AA holder positive leaf',5,.18,5,tuple(_pad_point(x,34.7 if sign==1 else -16.5,-10)),'Controller',-4,'metal',.06,True)
        m.label('PadAAMark'+str(i),'AA / LR6',2,tuple(_pad_point(x+1,-10,-.32)),'Controller',-3,'white',rotation=App.Rotation(V(0,0,1),90))
        # Separated contact stack illustrates the removable holder-to-board connection.
        cx=x+(-2.1 if x<0 else 2.1)
        m.box('PadAAContactLeaf'+str(i),'Separate holder-to-board contact leaf study',1,.3,10.2,tuple(_pad_point(cx,-14,1.5)),'Controller',-3,'metal',.08,True)
        m.box('PadAAContactSeat'+str(i),'Separate battery contact spring seat',4.8,4.8,.1,tuple(_pad_point(cx,-14,11.72)),'Controller',-2,'metal',.3,True)
        spring=_helical_spring(2,.75,6,.12);spring.translate(_pad_point(cx,-14,12))
        m.feature('PadAABoardSpring'+str(i),'Separate board-side AA contact spring study',spring,'Controller',-2,'metal',True)
        m.cyl('PadAABoardPin'+str(i),'Separate battery through-board contact',.25,2.25,tuple(_pad_point(cx,-14,18.35)),'Controller',-1,'metal',internal=True)
        pcbholes.append(Part.makeCylinder(.4,1.8,_pad_point(cx,-14,18.7)))
    m.cut('PadPCB',pcbholes,'Independent AA supply contact passages').Refine=False
    _strict_changed(m,prior)
    m.profile['stages']=28
    m.checkpoint(28,'unequal_rumble_motors_and_removable_two_aa_holder','加入两只不同尺寸的偏心振动电机及分离转子、磁体、线圈、轴、配重和双线接口；补齐可拆 AA 电池座、两枚反向安装的 LR6 电池、释放键与独立弹簧/触片。电机内部和电池接触堆叠为非功能性结构示意。')
    m.snapshot('28_rumble_and_aa_supply',assemblies=['Controller'],exclude=['PadBack','PadFront','PadRFShieldLid'],normal=(.3,.5,-1.8))


STAGES[28]=stage28


def _pad_grip_mask():
    curves=_pad_curves();edges=[curves[i].toShape() for i in [3,4,5,6]]
    upper=[]
    for edge in reversed(edges):
        edge=edge.copy();edge.translate(V(0,3,0));edge.reverse();upper.append(edge)
    outline=Part.Wire(edges+[Part.makeLine(V(-54,-63),V(-54,-60))]+upper+[Part.makeLine(V(54,-60),V(54,-63))])
    mask=Part.Face(outline).extrude(V(0,0,13.6));mask.translate(_pad_point(0,0,8));return mask


def stage29(m):
    prior={k:o.Name for k,o in m.parts.items()}
    import math
    rear=g.rotation((0,1,0),(0,0,1));front=g.rotation((0,-1,0),(0,0,1))
    charge_hole=m.rr(21,8,10,tuple(_pad_point(0,34,21.5)),1.4,rear)
    sync_hole=Part.makeCylinder(2.6,10,_pad_point(20,34,23.3),V(0,1,0))
    for key in ['PadBack','PadFront']:m.cut(key,[charge_hole,sync_hole],'Original charge and pairing interface openings').Refine=False
    shell=m.rr(20.2,6.8,7.5,tuple(_pad_point(0,35,21.5)),1.1,rear).cut(m.rr(19.2,5.8,8,tuple(_pad_point(0,34.8,21.5)),.7,rear))
    m.feature('PadChargeShell','Separate original proprietary charge-port shield',shell,'Controller',1,'metal',True)
    m.box('PadChargeBack','Separate charge-port rear insulator',18.8,5.4,.6,tuple(_pad_point(0,35.2,21.5)),'Controller',1,'black',.7,True,orient=rear)
    m.box('PadChargeTongue','Separate proprietary charge-port tongue',16,1,6,tuple(_pad_point(0,36,21.5)),'Controller',1,'black',.2,True,orient=rear)
    for i in range(8):m.box('PadChargeContact'+str(i),'Separate illustrative proprietary charge contact; not USB',.5,5,.12,tuple(_pad_point((i-3.5)*1.8,39,22.08)),'Controller',1,'gold',.03,True)
    m.cyl('PadSyncButton','Separate controller pairing button',2.2,1.2,tuple(_pad_point(20,41.6,23.3)),'Controller',2,'ivory',axis=(0,1,0))
    m.cyl('PadSyncPlunger','Separate pairing-button stem',.6,5.4,tuple(_pad_point(20,36,23.3)),'Controller',1,'ivory',axis=(0,1,0),internal=True)
    m.box('PadSyncSwitch','Separate pairing tactile switch',3,3,1.2,tuple(_pad_point(20,34.5,23.3)),'Controller',1,'metal',.3,True,orient=rear)
    m.cut('PadBack',m.rr(29,7.2,9,tuple(_pad_point(0,-17,14.5)),1.3,front),'Original 2.5 mm headset and expansion-port aperture').Refine=False
    body=m.rr(28,6.5,4.7,tuple(_pad_point(0,-17.5,14.5)),1,front)
    cuts=[Part.makeCylinder(1.9,5.5,_pad_point(0,-17.2,14.5),V(0,-1,0))]
    cuts += [m.rr(5,2.6,5.5,tuple(_pad_point(x,-17.2,14.5)),.6,front) for x in [-9,9]]
    m.feature('PadExpansionBody','Original combined headset and accessory receptacle',body.cut(Part.makeCompound(cuts)),'Controller',-1,'black',True)
    m.ring('PadHeadsetSleeve','Separate 2.5 mm headset socket sleeve',1.7,1.3,3.8,tuple(_pad_point(0,-18,14.5)),'Controller',-1,'metal',axis=(0,-1,0),internal=True)
    for side,x in enumerate([-9,9]):
        for i in range(3):m.box('PadExpansionContact'+str(side)+'_'+str(i),'Separate illustrative accessory contact',.4,.12,3.5,tuple(_pad_point(x+(i-1)*1.2,-18.2,14.0)),'Controller',-1,'gold',.03,True,orient=front)
    mask=_pad_grip_mask();trim=m.parts['PadBack'].Shape.common(mask)
    m.feature('PadGripTrim','Separate original gray lower grip insert',trim,'Controller',-2,'ventgray')
    m.cut('PadBack',trim,'Native back-shell separation for gray grip insert').Refine=False
    mounts=[(-59,23),(59,23),(-51,-55),(51,-55),(-67,-7),(67,-7),(0,-16)]
    for i,(x,y) in enumerate(mounts):
        m.ring('PadCaseBoss'+str(i),'Separate controller case screw guide',1.45,.85,21.4,tuple(_pad_point(x,y,8)),'Controller',0,'ivory',internal=True)
        screw=Part.makeCylinder(1.35,.6,_pad_point(x,y,5.5)).fuse(Part.makeCylinder(.62,23.25,_pad_point(x,y,6.05)))
        recess=Part.makeCylinder(.45,.4,_pad_point(x,y,5.45))
        for j in range(6):
            a=math.pi*j/3;recess=recess.fuse(Part.makeCylinder(.2,.4,_pad_point(x+.42*math.cos(a),y+.42*math.sin(a),5.45)))
        screw=screw.cut(recess).fuse(Part.makeCylinder(.1,.4,_pad_point(x,y,5.55))).removeSplitter()
        m.feature('PadCaseScrew'+str(i),'Separate six-lobe security fastener study',screw,'Controller',-3,'metal',True)
    for key in ['PadBack','PadFront']:m.cut(key,[Part.makeCylinder(1.65,22,_pad_point(x,y,8)) for x,y in mounts],'Independent controller screw-guide passages').Refine=False
    m.cut('PadBack',[Part.makeCylinder(2.7,8,_pad_point(x,y,-1)) for x,y in mounts],'Seven recessed rear fastener access wells').Refine=False
    m.cut('PadPCB',[Part.makeCylinder(1.65,2,_pad_point(x,y,18.7)) for x,y in mounts],'Case screws crossing or clearing controller board').Refine=False
    pcb=m.parts['PadPCB'].Shape
    occupied=[o.Shape.BoundBox for k,o in m.parts.items() if o.Assembly=='Controller' and k not in ['PadPCB','PadBack','PadFront'] and o.Shape.BoundBox.ZMin<20.95 and o.Shape.BoundBox.ZMax>20.22]
    candidates=[]
    for y in range(-17,31,6):
        for x in range(-58,59,6):
            p=_pad_point(x,y,19.6)
            if not all(pcb.isInside(p+V(dx,dy,0),1e-6,True) for dx in [-1.2,1.2] for dy in [-.6,.6]):continue
            if any(b.XMin-1.3<p.x<b.XMax+1.3 and b.YMin-.7<p.y<b.YMax+.7 for b in occupied):continue
            candidates.append((x,y))
    for i,(x,y) in enumerate(candidates[:32]):
        m.box('PadPassive'+str(i),'Schematic controller discrete device',1.4,.8,.35,tuple(_pad_point(x,y,20.45)),'Controller',1,'black',.08,True)
        for j,side in enumerate([-1,1]):m.box('PadPassiveEnd'+str(i)+'_'+str(j),'Separate controller discrete termination',.3,.84,.39,tuple(_pad_point(x+side*.95,y,20.43)),'Controller',1,'metal',.03,True)
    _strict_changed(m,prior)
    m.profile['stages']=29
    m.checkpoint(29,'original_charge_headset_ports_gray_trim_and_seven_fasteners','补齐原版充电/配对、2.5 mm 耳机与扩展接口、分离灰色握柄嵌件、七处背面六瓣防拆紧固件及示意小器件。接口接点仅表达结构，未加入原套装没有的 Windows 接收器、USB 线或充电电池包。')
    m.snapshot('29_complete_original_wireless_controller',assemblies=['Controller'],normal=(.2,-.45,2))


STAGES[29]=stage29


def _psu_point(x,y,z):
    return V(x+280,y-20,z)


def stage30(m):
    prior={k:o.Name for k,o in m.parts.items()}
    # Original 203 W envelope and forced-air architecture; local dimensions are approximate.
    m.native('BrickBottom','Editable ribbed 203 W supply lower enclosure',75,215,4,27.7,tuple(_psu_point(0,0,0)),'Accessories',-5,'ventgray')
    m.cut('BrickBottom',m.rr(71,211,28,tuple(_psu_point(0,0,2)),3),'Open lower power-brick cavity').Refine=False
    m.native('BrickTop','Editable ribbed 203 W supply upper enclosure',75,215,4,27.1,tuple(_psu_point(0,0,27.9)),'Accessories',5,'ventgray')
    m.cut('BrickTop',m.rr(71,211,25,tuple(_psu_point(0,0,27.7)),3),'Open upper power-brick cavity').Refine=False
    topcuts=[];bottomcuts=[]
    for y in range(-88,89,5):
        topcuts.append(m.rr(80,1.5,2,tuple(_psu_point(0,y,53.8)),.25))
        bottomcuts.append(m.rr(80,1.5,1.4,tuple(_psu_point(0,y,-.2)),.25))
        for x in [-37,37]:
            topcuts.append(m.rr(2,1.5,23,tuple(_psu_point(x,y,30)),.2))
            bottomcuts.append(m.rr(2,1.5,23,tuple(_psu_point(x,y,2)),.2))
    m.cut('BrickTop',topcuts,'Native power-supply cooling ribs').Refine=False
    m.cut('BrickBottom',bottomcuts,'Native lower and side cooling ribs').Refine=False
    for key in ['BrickBottom','BrickTop']:
        holes=[Part.makeCylinder(1.4,5,_psu_point(x,y,z),V(0,1,0)) for y in [-109,104] for z in [7,12,43,48] for x in range(-27,28,6)]
        m.cut(key,holes,'Separate end-face ventilation holes').Refine=False
    holes=[]
    for i,(x,y) in enumerate([(-29,-96),(29,-96),(-29,96),(29,96)]):
        m.cyl('BrickFoot'+str(i),'Separate power-brick rubber foot',4.2,1.3,tuple(_psu_point(x,y,-1.4)),'Accessories',-6,'rubber')
        m.ring('BrickCaseBoss'+str(i),'Separate power-brick screw pillar',2.8,1.2,47,tuple(_psu_point(x,y,3)),'Accessories',0,'ventgray',internal=True)
        m.screw('BrickScrew'+str(i),tuple(_psu_point(x,y,1.6)),'Accessories',-5,47,2)
        holes.append(Part.makeCylinder(3.0,49.7,_psu_point(x,y,1.4)))
    for key in ['BrickBottom','BrickTop']:m.cut(key,holes,'Independent power-brick case fastening passages').Refine=False
    # End input recess and output cord aperture remain separate from the shell.
    front=g.rotation((0,-1,0),(0,0,1))
    ac=m.rr(29,21,8,tuple(_psu_point(0,-103,27.5)),2,front)
    dc=Part.makeCylinder(5,10,_psu_point(0,102,27.5),V(0,1,0))
    led=Part.makeCylinder(2.6,8,_psu_point(-23,103,27.5),V(0,1,0))
    for key in ['BrickBottom','BrickTop']:m.cut(key,[ac,dc,led],'AC inlet, captive DC cord and status light apertures').Refine=False
    m.box('BrickLabel','Separate power-supply study label',49,47,.06,tuple(_psu_point(0,0,55.08)),'Accessories',6,'black',1)
    m.label('BrickLabelMark','203 W / XBOX 360',3.2,tuple(_psu_point(-22,5,55.16)),'Accessories',6,'white')
    m.label('BrickLabelStudy','STRUCTURE STUDY',2.8,tuple(_psu_point(-20,-7,55.16)),'Accessories',6,'white')
    m.cyl('BrickLightPipe','Separate supply status light pipe',2.2,2,tuple(_psu_point(-23,106,27.5)),'Accessories',2,'led',axis=(0,1,0))
    m.box('BrickLEDPCB','Separate status indicator daughterboard',7,7,.7,tuple(_psu_point(-23,103,27.5)),'Accessories',0,'pcb',.5,True,orient=g.rotation((0,1,0),(0,0,1)))
    m.cyl('BrickLED','Separate indicator LED envelope',1.5,1.5,tuple(_psu_point(-23,104,27.5)),'Accessories',1,'led',axis=(0,1,0),internal=True)
    _strict_changed(m,prior)
    m.profile['stages']=30
    m.checkpoint(30,'ribbed_203w_power_brick_shell_and_status_indicator','建立原版 203W 外置电源的可编辑双半壳、横向散热肋、端部通风、四处紧固、AC/DC 开口及独立状态灯；约 75 × 215 × 55 mm 外壳和内部安装尺寸为学习近似，不冒充厂商尺寸。')
    m.snapshot('30_external_203w_power_supply',assemblies=['Accessories'],normal=(.5,-.8,2))


STAGES[30]=stage30


def stage31(m):
    prior={k:o.Name for k,o in m.parts.items()}
    import math
    # Separation and topology study, not an electrical replica of a supplier-specific PSU.
    mounts=[(-28,-78),(28,-78),(-28,78),(28,78)]
    m.native('BrickPCB','Editable original-class supply board study',66,176,1.5,1.6,tuple(_psu_point(0,0,19.5)),'Accessories',0,'pcb')
    m.cut('BrickPCB',[Part.makeCylinder(1.2,2.3,_psu_point(x,y,19.2)) for x,y in mounts],'Independent supply-board fastener passages').Refine=False
    m.box('BrickShieldFloor','Separate lower supply shield and heat spreader',68,180,.35,tuple(_psu_point(0,0,18.8)),'Accessories',-2,'metal',1,True)
    m.cut('BrickShieldFloor',[Part.makeCylinder(2.2,1,_psu_point(x,y,18.5)) for x,y in mounts],'Board supports through lower shield').Refine=False
    for i,(x,y) in enumerate(mounts):
        m.ring('BrickBoardSupport'+str(i),'Separate PSU board support',2,1.05,13,tuple(_psu_point(x,y,6)),'Accessories',-2,'ventgray',internal=True)
        m.screw('BrickBoardScrew'+str(i),tuple(_psu_point(x,y,5.2)),'Accessories',-3,15.8,1.5)
    for i,x in enumerate([-34.2,34.2]):m.box('BrickShieldWall'+str(i),'Separate supply shield side wall',.4,180,29.5,tuple(_psu_point(x,0,19.2)),'Accessories',2,'metal',.08,True)
    m.box('BrickShieldTop','Separate perforated upper supply shield',68,180,.35,tuple(_psu_point(0,0,49)),'Accessories',4,'metal',1,True)
    m.cut('BrickShieldTop',[Part.makeCylinder(2.2,1,_psu_point(x,y,48.8)) for x in range(-24,25,8) for y in range(-72,73,8)],'Original-class shield air passages; approximate field').Refine=False
    # Large split transformer envelope with separately traceable core, bobbin and coils.
    m.box('BrickTransformerBobbin','Separate transformer insulating bobbin',26,22,16.8,tuple(_psu_point(0,-34,24.2)),'Accessories',1,'ivory',2,True)
    m.cut('BrickTransformerBobbin',m.rr(13,11,18,tuple(_psu_point(0,-34,23)),1),'Transformer center-limb passage').Refine=False
    m.box('BrickTransformerLimb','Separate ferrite center limb',12,10,16.8,tuple(_psu_point(0,-34,24.2)),'Accessories',1,'black',.8,True)
    for i,z in enumerate([21.6,41.2]):m.box('BrickTransformerCore'+str(i),'Separate transformer ferrite crossbar',32,28,2.4,tuple(_psu_point(0,-34,z)),'Accessories',1,'black',1,True)
    for i,x in enumerate([-16,16]):m.box('BrickTransformerOuterLimb'+str(i),'Separate transformer outer ferrite limb',2,28,16.8,tuple(_psu_point(x,-34,24.2)),'Accessories',1,'black',.3,True)
    for i,z in enumerate([25.2,27.2,29.2,31.2,33.2,35.2,37.2,39.2]):
        coil=m.rr(28.4,24.4,.9,tuple(_psu_point(0,-34,z)),2.2).cut(m.rr(26.4,22.4,1.2,tuple(_psu_point(0,-34,z-.1)),2))
        m.feature('BrickTransformerTurn'+str(i),'Separate illustrative transformer winding layer',coil,'Accessories',1,'copper',True)
    for i,(x,y,r,h) in enumerate([(-12,-66,7,24),(12,-66,7,24),(-10,15,4.8,17),(10,15,4.8,17),(-10,31,4.8,17),(10,31,4.8,17)]):
        m.cyl('BrickCap'+str(i),'Independent power-supply electrolytic envelope',r,h,tuple(_psu_point(x,y,21.8)),'Accessories',1,'black',internal=True)
        m.cyl('BrickCapTop'+str(i),'Separate capacitor end seal',r-.35,.08,tuple(_psu_point(x,y,21.8+h+.03)),'Accessories',1,'metal',internal=True)
        m.box('BrickCapVent'+str(i),'Separate capacitor vent marking',r*.9,.13,.02,tuple(_psu_point(x,y,21.8+h+.13)),'Accessories',1,'black',.02,True)
        for j,dx in enumerate([-1.3,1.3]):m.cyl('BrickCapLead'+str(i)+'_'+str(j),'Separate illustrative capacitor terminal',.3,.4,tuple(_psu_point(x+dx,y,21.2)),'Accessories',0,'metal',internal=True)
    # Standalone toroidal magnetic component, with separated copper loop envelopes.
    m.ring('BrickChoke','Separate supply output toroidal core',8,4,6,tuple(_psu_point(0,61,22.5)),'Accessories',1,'black',internal=True)
    for i in range(16):
        a=math.pi*2*i/16;normal=V(-math.sin(a),math.cos(a),0);center=_psu_point(6*math.cos(a),61+6*math.sin(a),25.5)
        path=Part.Wire([Part.makeCircle(4.1,center,normal)]);section=Part.Wire([Part.makeCircle(.28,path.Vertexes[0].Point,path.Edges[0].tangentAt(0))])
        m.feature('BrickChokeTurn'+str(i),'Separate illustrative toroidal copper winding',path.makePipeShell([section],True,False),'Accessories',1,'copper',True)
    for i,x in enumerate([-26,26]):
        m.box('BrickHeatBase'+str(i),'Separate PSU heat-sink base rail',3.5,103,2,tuple(_psu_point(x,-13,22)),'Accessories',1,'metal',.3,True)
        for j in range(3):m.box('BrickHeatFin'+str(i)+'_'+str(j),'Separate PSU heat-sink fin',.5,103,22,tuple(_psu_point(x+(j-1)*1.15,-13,24.2)),'Accessories',2,'metal',.08,True)
        for j,y in enumerate([-9,5,19,33]):
            m.box('BrickPowerPackage'+str(i)+'_'+str(j),'Separate power semiconductor package study',5,8,7,tuple(_psu_point(x+(-5 if i==0 else 5),y,24)),'Accessories',1,'black',.4,True)
    m.box('BrickStandbyTransformer','Separate auxiliary transformer envelope',17,15,12,tuple(_psu_point(0,-5,22)),'Accessories',1,'ivory',1.5,True)
    m.box('BrickFuse','Separate input fuse envelope',19,5,5,tuple(_psu_point(0,-83,22)),'Accessories',1,'white',1,True)
    m.box('BrickInputFilter','Separate input suppression component envelope',9,7,12,tuple(_psu_point(0,-75,22)),'Accessories',1,'black',1,True)
    m.label('BrickBoardMark','203W / CAD',2.5,tuple(_psu_point(-14,77,21.18)),'Accessories',0,'white')
    _strict_changed(m,prior)
    m.profile['stages']=31
    m.checkpoint(31,'203w_supply_board_shields_transformer_and_heat_sinks','补齐 203W 原版级别的电源板、上下屏蔽、分离磁芯/绕组、大电容和散热器。依据原版分析确认强制风冷架构；内部排布和器件数量为明确标注的非功能结构示意，不复制 175W 后期板型。')
    m.snapshot('31_power_supply_structural_internals',assemblies=['Accessories'],exclude=['BrickTop','BrickShieldTop'],normal=(.4,-.8,2))


STAGES[31]=stage31


def stage32(m):
    prior={k:o.Name for k,o in m.parts.items()}
    import math
    from .atari2600 import _rounded_route
    # A schematic miniature centrifugal fan expresses the documented forced-air PSU.
    def fp(x,y,z):return _psu_point(x,63+y,z)
    m.ring('BrickFanFrame','Separate miniature supply blower frame study',23,21.5,9,tuple(fp(0,0,6)),'Accessories',-3,'black',internal=True)
    m.ring('BrickFanFloor','Separate blower lower support',23,1.1,.5,tuple(fp(0,0,5.3)),'Accessories',-3,'black',internal=True)
    m.ring('BrickFanRotor','Separate blower impeller base',20,1.1,.5,tuple(fp(0,0,6.7)),'Accessories',-3,'black',internal=True)
    m.cyl('BrickFanShaft','Separate supply blower shaft',.6,10,tuple(fp(0,0,5)),'Accessories',-3,'metal',internal=True)
    m.ring('BrickFanBearing','Separate blower bearing sleeve',1,.7,7,tuple(fp(0,0,7.4)),'Accessories',-3,'metal',internal=True)
    m.ring('BrickFanHub','Separate blower hub shell',7,6.2,6.5,tuple(fp(0,0,7.5)),'Accessories',-3,'black',internal=True)
    m.ring('BrickFanMagnet','Separate blower rotor magnet',5.8,4.9,5.2,tuple(fp(0,0,7.8)),'Accessories',-3,'black',internal=True)
    m.ring('BrickFanStator','Separate blower stator envelope',2.7,1.2,4.5,tuple(fp(0,0,8.2)),'Accessories',-3,'metal',internal=True)
    for i in range(3):
        a=2*math.pi*i/3;m.ring('BrickFanCoil'+str(i),'Separate blower winding envelope',.7,.3,4,tuple(fp(3.7*math.cos(a),3.7*math.sin(a),8.4)),'Accessories',-3,'copper',internal=True)
    m.ring('BrickFanPCB','Separate supply-fan driver board',6.2,.8,.5,tuple(fp(0,0,14.5)),'Accessories',-2,'pcb',internal=True)
    for i in range(24):
        blade=m.rr(10,.45,6,(14.5,0,7.5),.12);blade.rotate(V(14.5,0,0),V(0,0,1),20);blade.rotate(V(),V(0,0,1),i*15);blade.translate(fp(0,0,0))
        m.feature('BrickFanBlade'+str(i),'Separate centrifugal impeller vane study',blade,'Accessories',-3,'black',True)
    # Original three-position grounded supply inlet; dimensions are illustrative.
    front=g.rotation((0,-1,0),(0,0,1))
    body=m.rr(28,20,8,tuple(_psu_point(0,-101,27.5)),2,front)
    body=body.cut(m.rr(25,17,7,tuple(_psu_point(0,-102.5,27.5)),1.5,front))
    m.feature('BrickACInlet','Separate grounded appliance inlet insulator',body,'Accessories',0,'black')
    for i,(x,z) in enumerate([(-6,25),(6,25),(0,32)]):m.box('BrickACPin'+str(i),'Separate inlet power or earth terminal study',1.4,4,5,tuple(_psu_point(x,-103,z)),'Accessories',0,'metal',.12,True,orient=front)
    # Captive cable and proprietary Xenon-compatible output connector displayed unplugged.
    m.ring('BrickDCRelief','Separate captive DC cable strain relief',4.5,3.1,14,tuple(_psu_point(0,104,27.5)),'Accessories',1,'ventgray',axis=(0,1,0))
    pts=[_psu_point(0,102,27.5),V(280,132,27.5),V(368,132,13),V(368,37,13)]
    m.feature('BrickDCCord','Captive original-class DC cable; shortened display route',_rounded_route(pts,8,2.8),'Accessories',0,'ventgray')
    m.box('BrickDCGrip','Separate proprietary DC plug overmould',28,35,21,(368,19,2.5),'Accessories',0,'ventgray',3)
    metal=m.rr(24,16,12,(368,1,13),1.5,front).cut(m.rr(22.8,14.8,12.4,(368,1.2,13),1.1,front))
    m.feature('BrickDCShield','Separate early DC connector metal sleeve',metal,'Accessories',0,'metal')
    m.box('BrickDCCarrier','Separate eight-position DC contact carrier study',22,13.5,1.5,(368,.6,13),'Accessories',0,'black',1,True,orient=front)
    for row,z in enumerate([9.5,16.5]):
        for col in range(3):m.ring('BrickDCPower'+str(row)+'_'+str(col),'Separate DC power socket terminal',1.4,1.0,8,(368+(col-1)*6,-1.2,z),'Accessories',0,'metal',axis=(0,-1,0),internal=True)
    for i,x in enumerate([365,371]):m.ring('BrickDCControl'+str(i),'Separate DC control socket terminal study',.65,.4,8,(x,-1.2,13),'Accessories',0,'metal',axis=(0,-1,0),internal=True)
    for i,x in enumerate([352.8,383.2]):m.box('BrickDCLatch'+str(i),'Separate DC plug release latch',1.7,15,7,(x,10,9.5),'Accessories',0,'black',.6)
    # Limited visible low-voltage routing, without claiming the actual electrical netlist.
    for i,x in enumerate([-3,0,3]):
        pts=[_psu_point(x,88,22),_psu_point(x,95,22),_psu_point(x,101,27.5)]
        m.feature('BrickOutputLead'+str(i),'Separate illustrative low-voltage lead',_rounded_route(pts,1,.35),'Accessories',0,'black' if i==0 else 'red',True)
    _strict_changed(m,prior)
    m.profile['stages']=32
    m.checkpoint(32,'power_brick_blower_grounded_inlet_and_captive_dc_output','补齐外置电源的独立微型风机内部件、三位接地 AC 入口、固定式输出电缆与早期专用 DC 插头。微型风机和八位端子布局为非功能示意，展示线长缩短，不提供接线或电源制造说明。')
    m.snapshot('32_psu_fan_and_captive_output',assemblies=['Accessories'],exclude=['BrickTop','BrickBottom','BrickShieldFloor','BrickShieldTop','BrickPCB'],normal=(.4,-.6,-2))


STAGES[32]=stage32


def stage33(m):
    prior={k:o.Name for k,o in m.parts.items()}
    from .atari2600 import _rounded_route
    # Original single-ear wired headset, with the large controller-end volume/mute adapter.
    band=Part.makeCylinder(75,9,V(-300,-240,8),V(0,0,1),180).cut(Part.makeCylinder(72,10,V(-300,-240,7.5),V(0,0,1),180))
    band=band.common(Part.makeBox(160,80,12,V(-380,-215,7)))
    m.feature('HeadsetBand','Separate curved original single-ear headband study',band,'Accessories',0,'ventgray')
    for i,x in enumerate([-369.5,-230.5]):
        m.box('HeadsetSlider'+str(i),'Separate adjustable headset end arm',4.5,17,8,(x,-223.8,8.5),'Accessories',0,'ivory',1)
        for j in range(5):m.box('HeadsetDetent'+str(i)+'_'+str(j),'Separate adjustment detent marker',3,.4,.1,(x,-227+j*2,16.6),'Accessories',1,'ventgray',.1)
    m.box('HeadsetTemple','Opposite-side cushioned temple support',14,27,6,(-230.5,-246,7),'Accessories',0,'ventgray',6)
    m.box('HeadsetTemplePad','Separate soft temple pad',13,25,2.5,(-230.5,-246,13.2),'Accessories',1,'rubber',5.5)
    cx=-369.5;cy=-252
    cup=Part.makeCylinder(19,7,V(cx,cy,3)).cut(Part.makeCylinder(17.5,6,V(cx,cy,4.5)))
    m.feature('HeadsetCup','Separate single-ear speaker shell',cup,'Accessories',0,'ivory')
    m.ring('HeadsetDriverBasket','Separate speaker basket',15,13.5,3, (cx,cy,5),'Accessories',0,'metal',internal=True)
    m.cyl('HeadsetMagnet','Separate speaker magnet envelope',5,2.5,(cx,cy,5.1),'Accessories',0,'black',internal=True)
    m.ring('HeadsetVoiceCoil','Separate speaker voice-coil envelope',6.5,5.8,2.1,(cx,cy,5.5),'Accessories',0,'copper',internal=True)
    cone=Part.makeCone(13,3,2,V(cx,cy,8.2)).cut(Part.makeCone(12.7,2.7,2,V(cx,cy,8.3)))
    m.feature('HeadsetDiaphragm','Separate speaker diaphragm study',cone,'Accessories',0,'black',True)
    m.ring('HeadsetCushion','Separate single-ear soft cushion',19.5,11.5,6,(cx,cy,10.5),'Accessories',1,'rubber')
    grille=Part.makeCylinder(11,.12,V(cx,cy,10.26))
    holes=[Part.makeCylinder(.55,.4,V(cx+x,cy+y,10.1)) for x in range(-8,9,3) for y in range(-8,9,3) if x*x+y*y<90]
    m.feature('HeadsetGrille','Separate perforated speaker grille',grille.cut(Part.makeCompound(holes)),'Accessories',1,'ventgray',True)
    m.cyl('HeadsetBoomPivot','Separate reversible microphone pivot',4,2,(cx,cy,16.8),'Accessories',1,'ivory')
    pts=[V(cx+4.2,cy,18.2),V(-330,-261,18.2),V(-299,-285,18.2)]
    m.feature('HeadsetBoom','Separate adjustable microphone boom study',_rounded_route(pts,5,1.5),'Accessories',1,'ventgray')
    mic=m.rr(17,8,6,(-290,-289,14.8),3).cut(m.rr(14,5,5,(-290,-289,16),2))
    m.feature('HeadsetMicShell','Separate microphone capsule shell',mic,'Accessories',1,'ivory')
    m.cyl('HeadsetMicCapsule','Separate electret microphone envelope',2.2,2,(-290,-289,16.2),'Accessories',1,'metal',internal=True)
    m.box('HeadsetMicMesh','Separate microphone opening mesh envelope',12,4,.1,(-290,-289,20.9),'Accessories',2,'ventgray',1.5)
    # Cable shortened and laid out to keep both ends independently visible.
    pts=[V(cx,cy-19.2,7),V(cx,-310,7),V(-270,-340,7),V(-214,-340,7)]
    m.feature('HeadsetCable','Separate original mono headset cable display route',_rounded_route(pts,7,.9),'Accessories',0,'ventgray')
    m.box('HeadsetAdapterBottom','Original controller-end volume/mute adapter lower shell',31,23,5,(-198,-340,2),'Accessories',0,'ivory',4)
    m.cut('HeadsetAdapterBottom',m.rr(28,20,5,(-198,-340,3.4),3),'Headset adapter internal cavity').Refine=False
    m.box('HeadsetAdapterTop','Separate headset adapter lid',31,23,1.2,(-198,-340,7.2),'Accessories',1,'ivory',4)
    m.box('HeadsetAdapterPCB','Separate headset adapter board study',25,16,.6,(-198,-340,3.8),'Accessories',0,'pcb',2,True)
    m.box('HeadsetMuteSwitch','Separate headset mute switch',6,4,2,(-190,-338,4.6),'Accessories',0,'black',.6,True)
    m.box('HeadsetMuteButton','Separate original adapter mute slider',6,4,1.2,(-190,-338,8.6),'Accessories',2,'ventgray',1)
    m.cut('HeadsetAdapterTop',m.rr(7,5,2,(-190,-338,7),1),'Original headset mute control opening').Refine=False
    m.ring('HeadsetVolumeWheel','Separate adapter volume wheel',5.5,1,2,(-202,-346,7.6),'Accessories',2,'ventgray')
    m.cut('HeadsetAdapterTop',Part.makeCylinder(5.9,3,V(-202,-346,7)),'Separate volume wheel travel clearance').Refine=False
    m.cyl('HeadsetVolumeAxle','Separate volume-control axle',.75,4.1,(-202,-346,5.3),'Accessories',1,'metal',internal=True)
    m.box('HeadsetVolumePot','Separate volume potentiometer envelope',8,7,.6,(-202,-346,4.6),'Accessories',0,'black',.5,True)
    # 2.5 mm three-conductor tip/ring/sleeve, separated by two insulating bands.
    for i,(y,length,mat,r) in enumerate([(-328.3,4,'metal',1.25),(-324.2,.5,'black',1.25),(-323.6,2,'metal',1.25),(-321.5,.5,'black',1.25),(-320.9,2,'metal',1.2)]):
        m.cyl('HeadsetPlugSegment'+str(i),'Separate 2.5 mm headset plug segment',r,length,(-198,y,5.5),'Accessories',0,mat,axis=(0,1,0))
    _strict_changed(m,prior)
    m.profile['stages']=33
    m.checkpoint(33,'original_single_ear_headset_and_controller_volume_adapter','依据 2005 安装手册补齐单耳头戴耳机、独立扬声器内部件、可调麦克风和原版手柄端音量/静音适配器。区分 2007 手册中的后期小插头版本；内部音频结构与局部曲率均为学习示意。')
    m.snapshot('33_original_wired_headset',assemblies=['Accessories'],exclude=[k for k in m.parts if k.startswith('Brick')],normal=(.3,-.5,2))


STAGES[33]=stage33


def stage34(m):
    prior={k:o.Name for k,o in m.parts.items()}
    from .atari2600 import _rounded_route
    m.colors['yellow']=(.9,.72,.08);m.colors['videogreen']=(.12,.52,.22)
    rear=g.rotation((0,1,0),(0,0,1));front=g.rotation((0,-1,0),(0,0,1))
    m.box('ComponentGrip','Original Component HD AV plug body',36,35,20,(220,-175,1),'Accessories',0,'ventgray',3)
    m.cut('ComponentGrip',m.rr(32,31,17.2,(220,-175,2.3),2),'Independent AV plug internal cavity').Refine=False
    shield=m.rr(32,9,11,(220,-157,11),1,rear).cut(m.rr(30.8,7.8,11.4,(220,-157.2,11),.6,rear))
    m.feature('ComponentShield','Separate original wide AV connector sleeve',shield,'Accessories',0,'metal')
    m.box('ComponentStop','Separate AV plug rear contact insulator',30,7,.4,(220,-156.8,11),'Accessories',0,'black',.5,True,orient=rear)
    m.box('ComponentTongue','Separate original AV contact tongue',29,1.5,9,(220,-156.1,11),'Accessories',0,'black',.2,True,orient=rear)
    for row,z in enumerate([10.1,11.9]):
        for i in range(15):m.box('ComponentContact'+str(row)+'_'+str(i),'Separate illustrative original AV plug contact',.65,7,.12,(220+(i-7)*1.8,-151.5,z),'Accessories',0,'gold',.03,True)
    m.box('ComponentPCB','Separate AV switch and optical board study',28,23,.7,(220,-177,6),'Accessories',0,'pcb',1,True)
    m.cut('ComponentGrip',m.rr(12,6,3,(226,-171,19.5),1),'TV HDTV selector opening').Refine=False
    m.box('ComponentSelector','Separate original TV / HDTV selector',10,4,1.2,(226,-171,20),'Accessories',1,'black',.8)
    m.label('ComponentTVMark','TV  HDTV',2,(210,-166,21.1),'Accessories',1,'black')
    m.cut('ComponentGrip',m.rr(11,11,8,(211,-187,13),1,front),'Original Toslink digital-audio socket aperture').Refine=False
    opt=m.rr(10,10,6,(211,-187.5,13),.8,front).cut(m.rr(7,7,6.5,(211,-187.7,13),.5,front))
    m.feature('ComponentOpticalSocket','Separate original Toslink-style optical output',opt,'Accessories',0,'black')
    m.box('ComponentOpticalDoor','Separate optical-output dust flap',6.5,6.5,.5,(211,-192.6,13),'Accessories',0,'ventgray',.4,orient=front)
    m.cyl('ComponentOpticalEmitter','Separate optical transmitter envelope',2,1,(211,-186,13),'Accessories',0,'led',axis=(0,-1,0),internal=True)
    m.cut('ComponentGrip',Part.makeCylinder(2.5,6,V(227,-188,7.7),V(0,-1,0)),'AV cable outlet through plug shell').Refine=False
    pts=[V(227,-189,7.7),V(227,-230,8),V(300,-230,8),V(300,-259.8,8)]
    m.feature('ComponentCable','Separate six-channel AV cable; shortened display route',_rounded_route(pts,7,2.1),'Accessories',0,'ventgray')
    m.box('ComponentSplitter','Separate six-way AV fan-out moulding',20,10,10,(300,-265,3),'Accessories',0,'ventgray',1.8)
    colors=['videogreen','blue','red','yellow','white','red'];marks=['Y','Pb','Pr','VIDEO','L','R']
    for i,(x,color) in enumerate(zip([240,264,288,312,336,360],colors)):
        sx=292.5+i*3;pts=[V(sx,-270.2,8),V(sx,-276-min(i,5-i)*8,8),V(x,-300,8),V(x,-308.8,8)]
        m.feature('ComponentBranch'+str(i),'Separate RCA cable branch '+marks[i],_rounded_route(pts,2,.95),'Accessories',0,'ventgray')
        m.cyl('ComponentRCAGrip'+str(i),'Separate RCA overmould '+marks[i],4.8,20,(x,-309,8),'Accessories',0,'ventgray' if i<3 else color,axis=(0,-1,0))
        m.ring('ComponentRCAColor'+str(i),'Separate RCA function band '+marks[i],5.2,4.85,3,(x,-321,8),'Accessories',0,color,axis=(0,-1,0))
        m.ring('ComponentRCAGround'+str(i),'Separate RCA outer ground sleeve',3.7,2.5,7,(x,-329.2,8),'Accessories',0,'metal',axis=(0,-1,0))
        m.cyl('ComponentRCASignal'+str(i),'Separate RCA center signal pin',.9,9,(x,-329.2,8),'Accessories',0,'gold',axis=(0,-1,0))
    _strict_changed(m,prior)
    m.profile['stages']=34
    m.checkpoint(34,'original_component_hd_av_six_rca_optical_and_tv_selector','补齐原配六 RCA Component HD AV 线，分离 Y/Pb/Pr、黄色复合视频和红白音频，保留宽 AV 端、TV/HDTV 选择器与 Toslink 光纤口。接点布局和线长为展示近似，不混入后期 HDMI 或五 RCA 改款。')
    m.snapshot('34_original_six_rca_component_cable',assemblies=['Accessories'],exclude=[k for k in m.parts if not k.startswith('Component')],normal=(.2,-.5,2))


STAGES[34]=stage34


def stage35(m):
    prior={k:o.Name for k,o in m.parts.items()}
    from .atari2600 import _rounded_route
    m.colors['clearplug']=(.68,.72,.72)
    points=[V(215,-379.4,6),V(215,-431,6),V(290,-431,6),V(290,-379.4,6)]
    m.feature('LANCable','Original bundled LAN cable shortened display path',_rounded_route(points,8,1.65),'Accessories',0,'ventgray')
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
        m.box(key+'Boot','Moulded modular-plug cable boot',12.4,10,9,(x,-374.2,1.5),'Accessories',0,'ventgray',1)
        relief=Part.makeCylinder(2.05,6,V(x,-379.3,6),V(0,-1,0)).cut(Part.makeCylinder(1.7,6.4,V(x,-379.1,6),V(0,-1,0)))
        m.feature(key+'Relief','Independent LAN cable strain relief',relief,'Accessories',0,'ventgray')
    # North-American grounded cord selection; the Nordic SCART/dual cord kit is excluded.
    m.box('ACDeviceGrip','Separate grounded appliance connector overmould',28,30,20,(430,-48,2),'Accessories',0,'ventgray',2)
    outline=[(-12,-8),(12,-8),(12,4),(8,9),(-8,9),(-12,4)]
    points=[V(430+x,-32.8,12+z) for x,z in outline]
    head=Part.Face(Part.Wire(Part.makePolygon(points+[points[0]]).Edges)).extrude(V(0,10,0))
    cuts=[]
    for i,(x,z) in enumerate([(424,9),(436,9),(430,17)]):
        cuts.append(Part.makeBox(2.6,10.5,4.8,V(x-1.3,-33,z-2.4)))
        contact=Part.makeBox(2.2,6,4.4,V(x-1.1,-30,z-2.2)).cut(Part.makeBox(1.5,6.4,3.6,V(x-.75,-30.2,z-1.8)))
        m.feature('ACDeviceContact'+str(i),'Separate grounded appliance spring socket',contact,'Accessories',0,'metal',True)
    m.feature('ACDeviceHead','Separate three-position grounded appliance head study',head.cut(Part.makeCompound(cuts)),'Accessories',0,'ventgray')
    pts=[V(430,-63.2,12),V(430,-108,12),V(485,-108,10),V(485,44.8,10)]
    m.feature('ACCord','Separate grounded North-American AC cord display route',_rounded_route(pts,8,2.3),'Accessories',0,'ventgray')
    m.box('ACWallPlug','Separate North-American three-prong wall plug study',26,22,18,(485,56,1),'Accessories',0,'ventgray',3)
    rear=g.rotation((0,1,0),(0,0,1))
    for i,x in enumerate([478.65,491.35]):m.box('ACWallBlade'+str(i),'Separate flat wall-plug terminal',1.5,6.3,15,(x,67.2,7),'Accessories',0,'metal',.1,orient=rear)
    m.cyl('ACWallEarth','Separate wall-plug grounding pin',2.1,17,(485,67.2,15),'Accessories',0,'metal',axis=(0,1,0))
    _strict_changed(m,prior)
    m.profile['stages']=35
    m.checkpoint(35,'bundled_ethernet_and_north_american_grounded_ac_cord','补齐原配网线的双端八触点与独立包胶/卡扣，选择北美三脚接地电源线版本；地区范围明确，不加入北欧 SCART、第二根区域电源线或限时赠送遥控器。电缆为缩短展示长度。')
    m.snapshot('35_complete_connection_kit',assemblies=['Accessories'],normal=(.3,-.6,2))


STAGES[35]=stage35


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
