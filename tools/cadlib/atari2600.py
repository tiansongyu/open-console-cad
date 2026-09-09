"""Approximate 1977 CX2600 Heavy Sixer study, based on original hardware."""
import math
import FreeCAD as App
import Part
from .core import V
from . import geometry as g


def _yz_prism(points, x=-200, width=400):
    wire=Part.makePolygon([V(x,y,z) for y,z in points]+[V(x,*points[0])])
    return Part.Face(Part.Wire(wire.Edges)).extrude(V(width,0,0))


def _hump_tools(offset=0):
    return [
        _yz_prism([(-130,50.6+offset),(9,50.6+offset),(76,86.6+offset),(76,110),(-130,110)]),
        _yz_prism([(92,86.6+offset),(104,50.6+offset),(130,50.6+offset),(130,110),(92,110)]),
    ]


def stage01(m):
    m.colors.update({'atariblack':(.14,.135,.125),'wood':(.48,.23,.07),'grain':(.26,.105,.035),'orange':(.75,.35,.035),'phenolic':(.62,.44,.22)})
    m.params.set('A3','Depth (Y)');m.params.set('A4','Height (Z)')
    m.params.set('B7','10 mm');m.params.set('C7','Approximate thick lower-wall section; other shell walls differ')
    base=m.native('LowerHousing','Heavy rounded lower housing',346,231.5,18,40,(0,0,8),'Body',-6,'atariblack',expr={'Width':'Parameters.Width'})
    # Preserve an additional native edge fillet for the broad rolled lower rim.
    tip=base.Tip
    bottom=[f'Edge{i+1}' for i,e in enumerate(tip.Shape.Edges) if abs(e.BoundBox.ZMin)<1e-7 and abs(e.BoundBox.ZMax)<1e-7]
    rolled=base.newObject('PartDesign::Fillet','LowerRimRound');rolled.Base=(tip,bottom);rolled.Radius=10
    m.doc.recompute();assert rolled.Shape.isValid() and rolled.Shape.Solids
    tip.Visibility=False;base.Tip=rolled
    m.cut('LowerHousing',m.rr(326,211.5,34,(0,0,18),8),'Heavy lower housing cavity')
    m.native('TopDeck','Horizontal ribbed deck foundation',325.6,211.1,7.8,2.3,(0,0,48.15),'Body',4,'atariblack')
    m.cut('TopDeck',m.rr(305.4,90.4,4,(0,56.5,47.9),2.0),'Open deck below the raised switch enclosure')
    m.native('ControlHump','Raised sloping control enclosure',310,95,4,36,(0,56.5,50.6),'Body',4,'atariblack')
    m.cut('ControlHump',_hump_tools(),'Front control slope and steep rear return')
    inner=m.rr(305.2,90.2,34.2,(0,56.5,50.4),1.6).cut(Part.makeCompound(_hump_tools(-2.2)))
    m.cut('ControlHump',inner,'Following hollow interior of the control hump')
    # Independent front fascia; colour denotes printed wood veneer, not solid timber.
    front=g.rotation((0,-1,0),(0,0,1))
    fascia=m.native('WoodFascia','Printed woodgrain front fascia',319,27,9,.18,(0,0,0),'Body',4,'wood')
    fascia.Placement=App.Placement(V(0,-115.92,33.2),front);fascia.FlatPlacement=fascia.Placement
    for i,(x,y) in enumerate([(-137,-85),(137,-85),(-137,85),(137,85)]):
        m.cyl('Foot'+str(i),'Recessed rubber support foot',6.5,7.8,(x,y,0),'Body',-6,'rubber')
    # Broad front/rear curves and thick side walls distinguish the early heavy shell.
    m.profile['stages']=1
    m.checkpoint(1,'heavy_sixer_native_enclosure','建立原生草图与双重圆角的厚壁底壳、独立顶板、空心斜面控制台、木纹色前饰板和四个脚垫；全部尺寸标记为近似学习尺寸。')


STAGES={1:stage01}


def _control_frame():
    q=App.Rotation(V(1,0,0),math.degrees(math.atan2(36,67)))
    return App.Placement(V(0,42.5,68.6),q)


def stage02(m):
    frame=_control_frame();q=frame.Rotation
    def pos(x,y,z):return frame.multVec(V(x,y,z))
    outer=m.rr(296,65.4,.10,r=1.1)
    inner=m.rr(294.6,64,.14,pos=(0,0,-.02),r=.5)
    trim=outer.cut(inner);trim.Placement=App.Placement(pos(0,0,.08),q)
    m.feature('ControlTrim','Orange control-bezel pinstripe',trim,'Body',4,'orange')
    bezel=m.rr(294.2,63.6,.12,r=.4);bezel.Placement=App.Placement(pos(0,0,.08),q)
    m.feature('ControlBezel','Printed black control faceplate',bezel,'Body',4,'black')
    slot=m.rr(80,20,14,r=3.8);slot.Placement=App.Placement(pos(0,-10,-10),q)
    for key in ['ControlHump','ControlBezel']:m.cut(key,slot,'Sloping cartridge entry opening')
    for i,(x,title) in enumerate([(-126,'power'),(-97,'tv type'),(-68,'left'),(68,'right'),(97,'game'),(126,'game')]):
        tool=Part.makeCylinder(3.1,12,V(x,0,-8))
        tool.Placement=frame
        for key in ['ControlHump','ControlBezel']:m.cut(key,tool,'Metal switch actuator clearance')
        washer=Part.makeCylinder(5.5,.9).cut(Part.makeCylinder(2.7,1.1,V(0,0,-.1)))
        washer.Placement=App.Placement(pos(x,0,.28),q)
        m.feature('SwitchWasher'+str(i),'Switch actuator dust washer',washer,'Controls',6,'black')
        stem=Part.makeCylinder(2.35,19,V(0,0,.4)).fuse(Part.makeSphere(2.35,V(0,0,19.4)))
        stem.Placement=App.Placement(pos(x,0,.3),q)
        m.feature('SwitchLever'+str(i),'Metal '+title+' switch lever',stem,'Controls',6,'metal')
        m.label('SwitchTitle'+str(i),title,2.4,tuple(pos(x-7,19,.23)),'Body',4,'orange',rotation=q)
        lower=['on / off','color / b-w','difficulty','difficulty','select','reset'][i]
        m.label('SwitchLegend'+str(i),lower,1.7,tuple(pos(x-8,13,.23)),'Body',4,'orange',rotation=q)
        if i in [2,3]:m.label('DifficultyAB'+str(i),'a / b',1.8,tuple(pos(x+6,-7,.23)),'Body',4,'orange',rotation=q)
    m.label('SystemTitle','video computer system',3.4,tuple(pos(-40,19,.23)),'Body',4,'metal',rotation=q)
    grooves=[m.rr(311,1.5,1.2,(0,-97+i*4.0,49.65),.4) for i in range(27)]
    m.cut('TopDeck',grooves,'Closely spaced horizontal deck ribs')
    # Thin solid ribbons denote the printed grain without external image textures.
    grain=[]
    for j in range(9):
        points=[(-151+i*6.0,-10+j*2.5+.4*math.sin(i*.35+j)) for i in range(51)]
        outline=[V(x,z,0) for x,z in points]+[V(x,z+.18,0) for x,z in reversed(points)]
        wire=Part.makePolygon(outline+[outline[0]])
        grain.append(Part.Face(Part.Wire(wire.Edges)).extrude(V(0,0,.025)))
    front=g.rotation((0,-1,0),(0,0,1));printed=Part.makeCompound(grain)
    printed.Placement=App.Placement(V(0,-116.115,33.2),front)
    m.feature('WoodgrainPrint','Printed woodgrain study pattern',printed,'Body',4,'grain')
    m.label('AtariWord','ATARI',4.5,(126,-116.15,24.5),'Body',4,'metal',rotation=front)
    m.profile['stages']=2
    m.checkpoint(2,'six_switches_ribs_and_fascia','加入六个金属操作杆及各自孔位、防尘垫、斜面卡带口、橙色铭牌边线和功能标识，并补齐横向筋槽与几何木纹印刷层。')


STAGES[2]=stage02


def stage03(m):
    from .psp import _polygon
    from .famicom import _tube
    rear=g.rotation((0,1,0),(0,0,1))
    for index,x in enumerate([-35,35]):
        placement=App.Placement(V(x,104.0,30),rear)
        opening=m.rr(31.4,15.4,15,(x,103.5,30),2,rear)
        m.cut('LowerHousing',opening,'Recessed DE-9 controller opening')
        profile=[(-14,-5.5),(14,-5.5),(12,5.5),(-12,5.5)]
        inside=[(-12.6,-4.2),(12.6,-4.2),(10.9,4.2),(-10.9,4.2)]
        hood=_polygon(profile,0,11.5).cut(_polygon(inside,3.2,9))
        hood.Placement=placement
        m.feature('ControllerSocket'+str(index),'DE-9 controller socket housing',hood,'Ports',-2,'black')
        surround=m.rr(34,18,.35,(x,115.84,30),3,rear).cut(m.rr(31.5,15.5,.6,(x,115.72,30),2,rear))
        m.feature('ControllerSurround'+str(index),'Raised Heavy Sixer rear connector surround',surround,'Body',-6,'atariblack')
        for row,count,z in [(0,5,-1.4),(1,4,1.4)]:
            for i in range(count):
                local=V((i-(count-1)/2)*2.77,z,3.3)
                start=placement.multVec(local)
                m.cyl('ControllerPin'+str(index)+'_'+str(row*5+i),'DE-9 male contact',.45,7.9,tuple(start),'Ports',-2,'metal',axis=(0,1,0),internal=True)
        m.label('RearControllerMark'+str(index),'RIGHT CONTROLLER' if index else 'LEFT CONTROLLER',1.65,(x+17,116.23,42),'Body',-6,'atariblack',rotation=rear)
    m.cut('LowerHousing',m.rr(10,10,15,(0,103,30),1.4,rear),'3.5 mm power connector passage')
    socket=m.rr(9.4,9.4,11.6,(0,104.1,30),1.2,rear).cut(Part.makeCylinder(2.2,12,V(0,104,30),V(0,1,0)))
    m.feature('PowerJackBody','3.5 mm DC power jack insulator',socket,'Ports',-2,'black')
    m.ring('PowerJackContact','DC jack sleeve contact',2.1,1.76,7.6,(0,108,30),'Ports',-2,'metal',axis=(0,1,0))
    m.label('RearPowerMark','POWER ADAPTOR',1.65,(15,116.05,22.5),'Body',-6,'atariblack',rotation=rear)
    m.cut('LowerHousing',Part.makeCylinder(4.8,15,V(110,103,30),V(0,1,0)),'Fixed RF cable bulkhead')
    m.ring('RFCableGrommet','Early RF lead rubber strain relief',4.55,2.2,11.6,(110,104.1,30),'Ports',-2,'rubber',axis=(0,1,0))
    wire=_tube([(110,108,30),(110,124,30),(126,146,27),(156,150,24)],1.8,tangents=[(0,1,0),(1,0,0)])
    m.feature('RFCable','Fixed RF cable exterior segment',wire,'Cables',0,'black')
    m.label('RearRFMark','TV RF LEAD',1.7,(134,116.1,40),'Body',-6,'atariblack',rotation=rear)
    # Side banks of slots belong to the original thick base, not a later channel switch.
    vents=[m.rr(12,1.5,14,(side*150,-27+i*4,7),.55) for side in [-1,1] for i in range(9)]
    m.cut('LowerHousing',vents,'Paired underside ventilation banks')
    m.profile['stages']=3
    m.checkpoint(3,'rear_de9_power_fixed_rf_and_base_vents','加入两组 DE-9 插座与 18 个独立接点、3.5 mm 电源口、固定 RF 线及护套、凸起后部接口标识和双侧底部散热孔，保留初代后面板特征。')


STAGES[3]=stage03


def stage04(m):
    m.box('Mainboard','Original two-board 2600 main logic PCB study',96,202,1.6,(0,1,22.5),'Mainboard',-2,'pcb',1.3,True)
    m.label('MainboardMark','CX2600 MAIN / STUDY',1.8,(-42,-98,24.13),'Mainboard',-2,'white')
    frame=_control_frame()
    board=m.rr(284,66,1.6,(0,0,-16),1.2).cut(m.rr(108,46,2.0,(0,-14,-16.2),.8))
    board.Placement=frame.multiply(board.Placement)
    m.feature('Switchboard','Elevated U-shaped switch and power board',board,'Switchboard',0,'phenolic',True)
    shell=m.rr(108,158,28.5,(0,-25,18.3),2.4)
    cavity=m.rr(101,151,26.0,(0,-25,21.3),1.2)
    shell=shell.cut(cavity)
    shell=shell.cut(m.rr(97,9,7,(0,53,21.9),.8))
    m.feature('ShieldBase','Thick cast-aluminium mainboard enclosure',shell,'Shield',-3,'metal',True)
    lid=m.rr(108,158,.7,(0,-25,47.0),2.4)
    lid=lid.cut(m.rr(84,40,1.2,(0,39,46.8),1.1))
    m.feature('ShieldLid','Removable aluminium lid with cartridge clearance',lid,'Shield',1,'metal',True)
    holes=[];cast_holes=[]
    for i,(x,y) in enumerate([(-43,-93),(43,-93),(-43,43),(43,43)]):
        holes.append(Part.makeCylinder(1.35,2.1,V(x,y,22.3)))
        cast_holes.append(Part.makeCylinder(.8,5.3,V(x,y,18.2)))
        m.ring('BoardSpacer'+str(i),'Mainboard isolation spacer',3.2,1.4,1.0,(x,y,21.4),'Mainboard',-2,'white',internal=True)
        m.screw('BoardScrew'+str(i),(x,y,24.6),'Mainboard',-2,length=5.1,radius=2.1,axis=(0,0,-1))
    m.cut('Mainboard',holes,'Four main PCB mounting clearances')
    m.cut('ShieldBase',cast_holes,'Mainboard fixing pilot holes')
    # Four separate threaded ears support the removable cast lid.
    for i,(x,y) in enumerate([(-48,-84),(48,-84),(-48,12),(48,12)]):
        ear=m.rr(4,9,3,(x,y,43.7),.8).cut(Part.makeCylinder(.8,4,V(x,y,43.3)))
        m.feature('ShieldLidEar'+str(i),'Shield lid fastening ear',ear,'Shield',-3,'metal',True)
        m.cut('ShieldLid',Part.makeCylinder(1.2,1.2,V(x,y,46.8)),'Shield lid screw clearance')
        m.screw('ShieldLidScrew'+str(i),(x,y,48.0),'Shield',1,length=3.5,radius=1.7,axis=(0,0,-1))
    m.profile['stages']=4
    m.checkpoint(4,'two_boards_cast_shield_and_mounts','建立窄长主逻辑板、独立斜置 U 形开关板、厚铸铝屏蔽底座和可拆上盖，加入板件垫圈、四处安装螺钉及屏蔽罩固定耳。')


STAGES[4]=stage04


def _disc_cap(m,key,x,y,r=3.1):
    from .famicom import _board_holes
    body=Part.makeCylinder(r,1.2,V(x,y-.6,28.4),V(0,1,0))
    bores=[Part.makeCylinder(.25,5,V(x+side*1.0,y,22.2)) for side in [-1,1]]
    body=body.cut(Part.makeCompound(bores))
    m.feature(key,'Green dipped ceramic capacitor',body,'Mainboard',-2,'pcb',True)
    wires=[Part.makeCylinder(.18,4.4,V(x+side,y,22.3)) for side in [-1,1]]
    m.feature(key+'Leads','Ceramic capacitor wire pair',Part.makeCompound(wires),'Mainboard',-2,'metal',True)
    _board_holes(m,'Mainboard',bores,'Ceramic capacitor PCB clearances')


def stage05(m):
    from .famicom import _dip,_axial_resistor,_board_holes,_flush_board_holes
    # A measured 0.05 mm head/lid overlap from stage four is cleared explicitly.
    for i in range(4):
        screw=m.parts['ShieldLidScrew'+str(i)]
        screw.Placement.Base+=V(0,0,.1);screw.FlatPlacement=screw.Placement
    m._pcb_hole_batch={}
    chips=[('RIOT','6532 RIOT',-12,3,50,15.2,40),('CPU','6507 CPU',-16,-31,35.5,14,28),('TIA','TIA C010444',7,-77,50,15.2,40),('Buffer','CD4050',31,-30,19.5,6.4,16)]
    for key,label,x,y,w,h,pins in chips:
        _dip(m,key,label,x,y,w,h,pins,z=24.4,t=3.9)
        pads=[]
        for side in [-1,1]:
            for i in range(pins//2):
                xx=x+(i-(pins//2-1)/2)*(w-2)/(pins//2-1);yy=y+side*(h/2+1.1)
                pad=Part.makeCylinder(.6,.035,V(xx,yy,22.45)).cut(Part.makeCylinder(.34,.06,V(xx,yy,22.44)))
                pads.append(pad)
        m.feature(key+'SolderLands','DIP underside solder lands',Part.makeCompound(pads),'Mainboard',-2,'gold',True)
    for i,(x,y) in enumerate([(-41,15),(-40,-18),(-42,-58),(33,-8),(22,-50),(6,-55),(-14,-56),(14,18)]):
        _disc_cap(m,'DiscCap'+str(i),x,y,2.7 if i%3 else 3.1)
    for i,y in enumerate([16,10,4,-2,-8,-14,-44,-50,-56]):
        _axial_resistor(m,'RightResistor'+str(i),39,y,z=26.2)
    for i,x in enumerate([-32,-18,-4,10,24,38]):
        _axial_resistor(m,'FrontResistor'+str(i),x,-95,z=26.2)
    m.box('MasterCrystal','Metal master-oscillator crystal can',6.2,13,6,(-36,-76,24.4),'Mainboard',-2,'metal',2.2,True)
    m.label('CrystalMark','XTAL',1.6,(-38.5,-77,30.45),'Mainboard',-2,'black')
    m.ring('ColorTrimBody','Colour-adjustment trimmer body',4.7,1.7,3.0,(-39,-45,24.4),'Mainboard',-2,'white',internal=True)
    rotor=Part.makeCylinder(1.5,2.2,V(-39,-45,25.3)).cut(Part.makeBox(.45,3.4,.5,V(-39.225,-46.7,27.15)))
    m.feature('ColorTrimRotor','Slotted colour-adjustment rotor',rotor,'Mainboard',-2,'metal',True)
    for i,(x,y) in enumerate([(14,-36),(10,-46),(-23,-56)]):
        m.cyl('Transistor'+str(i),'Small-signal transistor package study',1.8,4,(x,y,25.0),'Mainboard',-2,'black',internal=True)
        pins=[Part.makeCylinder(.16,2.7,V(x+(j-1)*.9,y,22.2)) for j in range(3)]
        m.feature('TransistorPins'+str(i),'Transistor lead set',Part.makeCompound(pins),'Mainboard',-2,'metal',True)
        _board_holes(m,'Mainboard',[Part.makeCylinder(.25,2.2,V(x+(j-1)*.9,y,22.3)) for j in range(3)],'Transistor PCB holes')
    _flush_board_holes(m)
    m.profile['stages']=5
    m.checkpoint(5,'6507_riot_tia_and_discrete_components','补齐 6507、6532 RIOT、TIA 与 CD4050 封装、独立引脚和焊盘，以及陶瓷电容、电阻、晶振与色彩调节件；修正四处屏蔽盖螺钉的微小轴向干涉。')


STAGES[5]=stage05


def stage06(m):
    from .famicom import _tube
    frame=_control_frame();q=frame.Rotation
    def pose(shape):
        shape.Placement=frame.multiply(shape.Placement)
        return shape
    guide=m.rr(79.2,19.2,17,(0,-10,-20),1.8).cut(m.rr(76.8,16.8,17.4,(0,-10,-20.2),.7))
    m.feature('CartridgeGuide','Inclined cartridge entry guide',pose(guide),'CardReader',2,'black')
    socket=m.rr(76,12.8,21.4,(0,-10,-41.8),1.0)
    socket=socket.cut(m.rr(69,2.3,16.3,(0,-10,-36.2),.35))
    channels=[];vertical_bores=[];pcb_bores=[]
    for side in [-1,1]:
        for i in range(12):
            x=(i-5.5)*4.0
            spring=m.rr(.8,.20,13,(x,-10+side*1.15,-35),.02)
            foot=m.rr(.8,3.5,.25,(x,-10+side*2.8,-35),.02)
            leg=m.rr(.5,.5,6.8,(x,-10+side*4.4,-41.5),.02)
            contact=pose(spring.fuse(foot).fuse(leg))
            end=frame.multVec(V(x,-10+side*4.4,-41.5))
            tail=Part.makeCylinder(.22,end.z-22.1+.2,V(end.x,end.y,22.1))
            m.feature('CartridgeContact'+str((side+1)//2*12+i),'24-position cartridge spring contact',contact.fuse(tail),'CardReader',0,'gold',True)
            channels.extend([m.rr(1.05,.45,13.5,(x,-10+side*1.15,-35.2),.04),m.rr(1.05,4,.6,(x,-10+side*2.75,-35.15),.04),m.rr(.75,.75,7.5,(x,-10+side*4.4,-41.8),.04)])
            vertical_bores.append(Part.makeCylinder(.34,end.z-22+.5,V(end.x,end.y,22)))
            pcb_bores.append(Part.makeCylinder(.34,2.2,V(end.x,end.y,22.3)))
    socket=pose(socket.cut(Part.makeCompound(channels)))
    socket=socket.cut(Part.makeCompound(vertical_bores))
    socket=socket.cut(Part.makeBox(200,220,74.35,V(-100,-110,-50)))
    m.feature('CartridgeSocket','Inclined 24-position cartridge connector body',socket,'CardReader',0,'black',True)
    m.cut('ShieldBase',m.rr(77,8,24,(0,53,24.2),.8),'Rear casting clearance around cartridge connector')
    m.cut('Mainboard',pcb_bores,'Cartridge contact tail holes')
    # The original two boards communicate over a 12-conductor ribbon.
    m.colors['ribbon']=(.56,.62,.61)
    main_header=m.rr(27,5,2.8,(0,80,24.3),.4)
    switch_header=m.rr(27,4,2.8,(0,24,-14.2),.4)
    main_bores=[];switch_bores=[];main_pcb=[]
    for i in range(12):
        x=-11+i*2
        main_bores.append(Part.makeCylinder(.4,3.3,V(x,80,24.1)))
        switch_bores.append(Part.makeCylinder(.4,5.5,V(x,24,-16.4)))
        main_pcb.append(Part.makeCylinder(.4,2.2,V(x,80,22.3)))
        m.cyl('MainRibbonPin'+str(i),'Main ribbon connector pin',.28,5.3,(x,80,22.2),'Mainboard',-2,'metal',internal=True)
        pin=Part.makeCylinder(.28,5.1,V(x,24,-16.3))
        m.feature('SwitchRibbonPin'+str(i),'Switchboard ribbon connector pin',pose(pin),'Switchboard',0,'metal',True)
        end=frame.multVec(V(x,24,-11.2));above=frame.multVec(V(x,24,-8))
        cable=_tube([(x,80,27.5),(x,80,38),(x,88,55),tuple(above),tuple(end)],.62,tangents=[(0,0,1),tuple(q.multVec(V(0,0,-1)))])
        m.feature('RibbonWire'+str(i),'Twelve-way ribbon conductor insulation',cable,'Wiring',0,'red' if i==0 else 'ribbon',True)
    m.feature('MainRibbonHeader','Mainboard ribbon connector housing',main_header.cut(Part.makeCompound(main_bores)),'Mainboard',-2,'black',True)
    m.feature('SwitchRibbonHeader','Switchboard ribbon connector housing',pose(switch_header.cut(Part.makeCompound(switch_bores))),'Switchboard',0,'black',True)
    m.cut('Mainboard',main_pcb,'Main ribbon header plated holes')
    m.cut('Switchboard',pose(Part.makeCompound(switch_bores)),'Switchboard ribbon header holes')
    m.profile['stages']=6
    m.checkpoint(6,'24_contact_card_reader_and_twelve_way_ribbon','建立倾斜卡带导向口、24 个独立弹性接点与板端引脚，补齐双板之间的 12 芯排线、连接器和穿孔，并为卡座留出铸铝壳体空间。')


STAGES[6]=stage06


def stage07(m):
    from .famicom import _tube
    from .clamshell import _move,_replace
    frame=_control_frame();q=frame.Rotation
    def pose(shape):
        shape.Placement=frame.multiply(shape.Placement)
        return shape
    # Preserve the components while improving their installed clearances.
    for key in ['RightResistor4','RightResistor4Leads','RightResistor4Bands']:_move(m,key,(0,0,-.7))
    for i in range(12):
        x=-11+i*2;end=frame.multVec(V(x,24,-11.2));above=frame.multVec(V(x,24,-8))
        cable=_tube([(x,80,27.5),(x,96,35),(x,96,63),tuple(above),tuple(end)],.62,tangents=[(0,0,1),tuple(q.multVec(V(0,0,-1)))])
        _replace(m,'RibbonWire'+str(i),cable)
    pcb_bores=[]
    for i,x in enumerate([-126,-97,-68,68,97,126]):
        body=m.rr(20,16,10,(x,0,-14.1),.8)
        body=body.cut(Part.makeCylinder(2.7 if i>=4 else 2.0,11,V(x,0,-14.3)))
        contacts=[];channels=[]
        columns=[-3,3] if i<4 else [-4,0,4]
        for dx in columns:
            for y in [-4,4]:
                contacts.append(m.rr(.5,.5,4.5,(x+dx,y,-16.4),.02))
                channels.append(m.rr(.8,.8,3.3,(x+dx,y,-14.3),.04))
                pcb_bores.append(Part.makeCylinder(.5,2.2,V(x+dx,y,-16.3)))
        m.feature('SwitchBody'+str(i),'Six-switch contact carrier',pose(body.cut(Part.makeCompound(channels))),'Switchboard',0,'black',True)
        m.feature('SwitchContactPins'+str(i),'Switch terminal layout study',pose(Part.makeCompound(contacts)),'Switchboard',0,'gold',True)
        cover=m.rr(22,18,.4,(x,0,-3.9),1.0).cut(Part.makeCylinder(2.5,.8,V(x,0,-4.1)))
        m.feature('SwitchMetalPlate'+str(i),'Stamped switch cover plate',pose(cover),'Switchboard',0,'metal',True)
        collar=Part.makeCylinder(3.0,3.65,V(x,0,-3.4)).cut(Part.makeCylinder(2.65,3.9,V(x,0,-3.5)))
        m.feature('SwitchCollar'+str(i),'Switch guide sleeve',pose(collar),'Switchboard',0,'black',True)
        shaft=Part.makeCylinder(1.6,12.1,V(x,0,-11.5))
        m.feature('SwitchInnerShaft'+str(i),'Switch internal moving stem',pose(shaft),'Switchboard',0,'metal',True)
        if i>=4:
            helix=Part.makeHelix(.9,4.5,2.15)
            section=Part.Wire(Part.makeCircle(.13,helix.Vertexes[0].Point,helix.Edges[0].tangentAt(helix.Edges[0].FirstParameter)))
            spring=Part.Wire(helix.Edges).makePipeShell([section],True,False);spring.translate(V(x,0,-10))
            m.feature('SwitchReturnSpring'+str(i),'Select/reset compression return spring',pose(spring),'Switchboard',0,'metal',True)
    m.cut('Switchboard',pose(Part.makeCompound(pcb_bores)),'Switch terminal PCB bores')
    board_holes=[]
    for index in range(2):
        holes=[]
        for row,count in [(0,5),(1,4)]:
            for i in range(count):
                key='ControllerPin'+str(index)+'_'+str(row*5+i)
                obj=m.parts[key];shape=obj.Shape.copy();b=shape.optimalBoundingBox(False,False);x=b.Center.x;z=b.Center.z
                tail=Part.makeCylinder(.23,7.7,V(x,99.8,z),V(0,1,0)).fuse(Part.makeCylinder(.23,z-22.1+.1,V(x,99.8,22.1)))
                combined=shape.fuse(tail);obj.Placement=App.Placement();obj.Shape=combined;obj.FlatPlacement=obj.Placement
                holes.append(Part.makeCylinder(.36,8.3,V(x,99.5,z),V(0,1,0)))
                board_holes.append(Part.makeCylinder(.36,2.2,V(x,99.8,22.3)))
        m.cut('ControllerSocket'+str(index),holes,'DE-9 tail feedthrough bores')
    m.cut('Mainboard',board_holes,'DE-9 through-hole contact rows')
    m.profile['stages']=7
    m.checkpoint(7,'switch_mechanisms_and_installed_wire_clearance','补齐六个开关的金属盖、导向套、传动柱和接点，加入 SELECT/RESET 回位弹簧与 DE-9 板端引脚；下调一枚电阻并让排线绕过开关板后缘。')


STAGES[7]=stage07


def stage08(m):
    frame=_control_frame();q=frame.Rotation;bores=[]
    def pose(shape):
        shape.Placement=frame.multiply(shape.Placement)
        return shape
    def feature(key,label,shape,material='metal',layer=0):
        return m.feature(key,label,pose(shape),'PowerRF',layer,material,True)
    for i in range(6):m.parts['SwitchContactPins'+str(i)].Label='Switch terminal layout study'
    # The original manufacturer parts list specifies an axial 2200 uF / 16 V filter.
    feature('FilterCap','Axial 2200 uF 16 V filter capacitor',Part.makeCylinder(4.8,22,V(-106,20,-7.9),V(1,0,0)))
    ends=[Part.makeCylinder(4.4,.2,V(x,20,-7.9),V(1,0,0)) for x in [-106.3,-83.9]]
    feature('FilterCapSeals','Axial capacitor end seals',Part.makeCompound(ends),'black')
    wires=[]
    for side in [-1,1]:
        x=-95+side*13
        wires.append(Part.makeCylinder(.25,8.5,V(x,20,-16.3)).fuse(Part.makeCylinder(.25,1.9,V(x,20,-7.9),V(-side,0,0))))
        bores.append(Part.makeCylinder(.4,2.2,V(x,20,-16.3)))
    feature('FilterCapLeads','Axial filter capacitor leads',Part.makeCompound(wires))
    m.label('FilterCapMark','2200uF / 16V',1.7,tuple(frame.multVec(V(-104,19,-3.05))),'PowerRF',0,'black',rotation=q)
    # A finned TO-220 heatsink is independent of the regulator package and fastener.
    sink=m.rr(22,23,.8,(-126,-21,-12.5),.7)
    for x in [-136.5,-115.5]:sink=sink.fuse(m.rr(1,23,7, (x,-21,-11.7),.2))
    bolt=Part.makeCylinder(.85,4,V(-126,-14,-13.2))
    sink=sink.cut(bolt).cut(m.rr(9,6,10,(-126,-30.5,-13),.5))
    feature('RegulatorHeatsink','Finned 78M05 heat sink',sink,'black')
    feature('RegulatorBody','78M05 TO-220 regulator package',m.rr(10,12,3.2,(-126,-23,-10.8),.5),'black')
    tab=m.rr(10,6,.6,(-126,-14,-11.5),.5).cut(bolt)
    feature('RegulatorTab','Regulator mounting tab',tab)
    spacer=Part.makeCylinder(2.4,1.7,V(-126,-14,-14.3)).cut(Part.makeCylinder(.9,1.9,V(-126,-14,-14.4)))
    feature('RegulatorSpacer','Regulator mounting spacer',spacer,'white')
    bores.append(Part.makeCylinder(.85,2.2,V(-126,-14,-16.3)))
    screw=m.screw('RegulatorScrew',(-126,-14,-10.2),'PowerRF',0,length=4.0,radius=1.8,axis=(0,0,-1))
    screw.Placement=frame.multiply(screw.Placement);screw.FlatPlacement=screw.Placement
    for i,x in enumerate([-128.54,-126,-123.46]):
        lead=Part.makeCylinder(.22,6.9,V(x,-30.3,-16.3)).fuse(Part.makeCylinder(.22,1.1,V(x,-30.3,-9.4),V(0,1,0)))
        feature('RegulatorLead'+str(i),'Formed regulator lead',lead)
        bores.append(Part.makeCylinder(.35,2.2,V(x,-30.3,-16.3)))
    m.label('RegulatorMark','78M05',1.7,tuple(frame.multVec(V(-130,-23.5,-7.55))),'PowerRF',0,'white',rotation=q)
    # A removable RF cover surrounds schematic tuning components on the same board.
    can=m.rr(36,18,9.6,(108,-22,-14.1),.7).cut(m.rr(35,17,9.3,(108,-22,-14.2),.3))
    can=can.cut(Part.makeCylinder(1.25,3,V(118,-32,-12.5),V(0,1,0)))
    feature('RFCan','Removable RF modulator cover',can,layer=1)
    feature('RFCoilCore','RF tuning coil core',Part.makeCylinder(1.3,4,V(99,-22,-14.0)),'black')
    helix=Part.makeHelix(.6,3.6,2.0)
    section=Part.Wire(Part.makeCircle(.13,helix.Vertexes[0].Point,helix.Edges[0].tangentAt(helix.Edges[0].FirstParameter)))
    coil=Part.Wire(helix.Edges).makePipeShell([section],True,False);coil.translate(V(99,-22,-13.7))
    feature('RFCoilWinding','RF tuning copper winding',coil,'copper')
    feature('RFTransistor','RF transistor package study',Part.makeCylinder(1.8,3.4,V(118,-20,-14.1)),'black')
    pins=[Part.makeCylinder(.16,2.1,V(118+(i-1)*.9,-20,-16.3)) for i in range(3)]
    feature('RFTransistorPins','RF transistor lead set',Part.makeCompound(pins))
    bores.extend([Part.makeCylinder(.25,2.2,V(118+(i-1)*.9,-20,-16.3)) for i in range(3)])
    feature('RFDiscCap','RF ceramic disc',Part.makeCylinder(2,1,V(110,-25.5,-10.5),V(0,1,0)),'pcb')
    pins=[Part.makeCylinder(.16,3.6,V(110+side*.7,-25,-16.3)) for side in [-1,1]]
    feature('RFDiscCapPins','RF capacitor wire pair',Part.makeCompound(pins))
    bores.extend([Part.makeCylinder(.26,2.2,V(110+side*.7,-25,-16.3)) for side in [-1,1]])
    trim=m.rr(5,5,3,(107,-18,-14.1),.5).cut(Part.makeCylinder(1.4,1.4,V(107,-18,-12.3)))
    feature('RFTrimmer','RF adjustment trimmer',trim,'white')
    rotor=Part.makeCylinder(1.2,1,V(107,-18,-12.15)).cut(m.rr(.35,2.7,.35,(107,-18,-11.4),.03))
    feature('RFTrimmerRotor','Slotted RF trimmer rotor',rotor)
    for i,(x,y) in enumerate([(-134,20),(-119,20),(-72,20)]):
        feature('SwitchDiscCap'+str(i),'Switchboard dipped ceramic capacitor',Part.makeCylinder(2.4,1.2,V(x,y-.6,-9),V(0,1,0)),'pcb')
        pins=[Part.makeCylinder(.16,4.7,V(x+side*.7,y,-16.3)) for side in [-1,1]]
        feature('SwitchDiscCapPins'+str(i),'Switchboard capacitor wire pair',Part.makeCompound(pins))
        bores.extend([Part.makeCylinder(.26,2.2,V(x+side*.7,y,-16.3)) for side in [-1,1]])
    m.cut('Switchboard',pose(Part.makeCompound(bores)),'Power and RF component PCB lead holes')
    m.profile['stages']=8
    m.checkpoint(8,'78m05_filter_and_rf_modulator','补齐原始开关板上的 2200 µF 轴向滤波电容、78M05 与散热片、独立引脚和安装件，加入可拆 RF 金属罩、调谐线圈、晶体管和电容示意。')


STAGES[8]=stage08


def _bounded_ribbon(x,radius=.62,clearance=0):
    """G1 cubic segments keep the ribbon inside explicit control-point bounds."""
    frame=_control_frame();inv=frame.inverse();start=V(x,80,27.5+clearance)
    local=inv.multVec(start);direction=frame.Rotation.inverted().multVec(V(0,0,1))
    a=V(x,37,-34);b=V(x,37,-8);end=V(x,24,-11.2+clearance)
    groups=[]
    for poles in [[local,local+direction*6,a-V(0,0,7),a],[a,a+V(0,0,8),b-V(0,0,8),b],[b,b+V(0,0,5),end+V(0,0,8.2),end]]:
        groups.append([frame.multVec(p) for p in poles])
    shape=_cubic_pipe(groups,radius)
    assert shape.isValid() and len(shape.Solids)==1
    return shape


def stage09(m):
    from .clamshell import _replace
    for i in range(12):_replace(m,'RibbonWire'+str(i),_bounded_ribbon(-11+i*2))
    frame=_control_frame()
    bore=Part.makeCylinder(.36,28,V(-109,20,-7.9),V(1,0,0));bore.Placement=frame.multiply(bore.Placement)
    m.cut('FilterCapSeals',bore,'Axial capacitor wire feedthroughs')
    m.profile['stages']=9
    m.checkpoint(9,'bounded_ribbon_routing_and_capacitor_seals','用连续切向的分段曲线限定排线弯曲范围，绕过电路板后缘并保留机壳间隙；为轴向电容端封补齐引线穿孔。')


STAGES[9]=stage09


def _cubic_pipe(groups,radius):
    splines=[]
    for poles in groups:
        c=Part.BezierCurve();c.setPoles(poles);splines.append(c.toBSpline())
    curve=splines[0]
    for segment in splines[1:]:assert curve.join(segment)
    edge=curve.toShape();section=Part.Wire(Part.makeCircle(radius,edge.Vertexes[0].Point,edge.tangentAt(edge.FirstParameter)))
    result=Part.Wire([edge]).makePipeShell([section],True,False)
    assert result.isValid() and result.Solids
    return result


def stage10(m):
    frame=_control_frame();q=frame.Rotation
    def pose(shape):
        shape.Placement=frame.multiply(shape.Placement)
        return shape
    # Trim vertical moulded bosses to the inclined underside of the switchboard.
    above=pose(Part.makeBox(400,250,150,V(-200,-125,-16.2)))
    holes=[]
    for i,(x,v) in enumerate([(-130,-25),(130,-25),(-130,25),(130,25)]):
        point=frame.multVec(V(x,v,-16))
        boss=Part.makeCone(6,4.5,point.z-18.1+5,V(x,point.y,18.1)).cut(above)
        bore=pose(Part.makeCylinder(.9,12,V(x,v,-25)))
        m.feature('SwitchboardPost'+str(i),'Inclined switchboard support boss',boss.cut(bore),'Body',-6,'atariblack',True)
        holes.append(Part.makeCylinder(1.2,2.2,V(x,v,-16.3)))
        screw=m.screw('SwitchboardScrew'+str(i),(x,v,-13.9),'Switchboard',0,length=8,radius=2.1,axis=(0,0,-1))
        screw.Placement=frame.multiply(screw.Placement);screw.FlatPlacement=screw.Placement
    m.cut('Switchboard',pose(Part.makeCompound(holes)),'Switchboard mounting screws')
    lower_bores=[]
    for i,(x,y) in enumerate([(-150,-85),(150,-85),(-150,85),(150,85)]):
        boss=Part.makeCylinder(3.7,29.6,V(x,y,18.5)).cut(Part.makeCylinder(.9,23,V(x,y,18.3)))
        m.feature('DeckPost'+str(i),'Top-deck screw boss',boss,'Body',4,'atariblack',True)
        lower_bores.extend([Part.makeCylinder(1.05,11,V(x,y,8)),Part.makeCylinder(2.45,2.6,V(x,y,7))])
        m.screw('CaseScrew'+str(i),(x,y,7.4),'Body',-6,length=29,radius=2.3)
    for i,x in enumerate([-35,35]):
        lower_bores.extend([Part.makeCylinder(1.05,11,V(x,-42,8)),Part.makeCylinder(2.45,2.6,V(x,-42,7))])
        m.screw('CastCaseScrew'+str(i),(x,-42,7.4),'Body',-6,length=13,radius=2.3)
        m.cut('ShieldBase',Part.makeCylinder(.85,2.4,V(x,-42,18.2)),'Cast enclosure to base screw pilot')
    m.cut('LowerHousing',lower_bores,'Six recessed lower-case fastening passages')
    rf_start=frame.multVec(V(118,-29,-12.5));rf_mid=V(145,55,27);rf_end=V(110,108,30)
    wire=_cubic_pipe([[rf_start,rf_start+q.multVec(V(0,-9,0)),V(145,20,27),rf_mid],[rf_mid,V(145,75,27),V(110,98,30),rf_end]],.9)
    m.feature('InternalRFLead','Internal RF coaxial route',wire,'Wiring',0,'black',True)
    m.cut('RFCan',pose(Part.makeCylinder(1.7,4,V(118,-33,-12.5),V(0,1,0))),'RF cover cable exit')
    pcb_bores=[];jack_bores=[]
    for i,side in enumerate([-1,1]):
        start=V(side*3.1,103.7,27);a=V(-60+side,88,36);b=V(-104+side,50,32);end=frame.multVec(V(-135+side*1.3,-32,-16.6))
        wire=_cubic_pipe([[start,start+V(0,-12,0),a+V(14,0,0),a],[a,a+V(-15,0,0),b+V(0,13,0),b],[b,b+V(0,-10,0),end-q.multVec(V(0,0,8)),end]],.55)
        m.feature('InternalDCWire'+str(i),'DC input harness study',wire,'Wiring',0,'red' if i==0 else 'black',True)
        m.cyl('PowerJackTail'+str(i),'Power jack solder terminal',.26,3.3,tuple(start),'Ports',-2,'metal',axis=(0,1,0),internal=True)
        jack_bores.append(Part.makeCylinder(.4,4,V(side*3.1,103.5,27),V(0,1,0)))
        pin=Part.makeCylinder(.27,2.3,V(-135+side*1.3,-32,-16.5))
        m.feature('DCBoardTerminal'+str(i),'Switchboard power input terminal',pose(pin),'PowerRF',0,'metal',True)
        pcb_bores.append(Part.makeCylinder(.42,2.2,V(-135+side*1.3,-32,-16.3)))
    m.cut('PowerJackBody',jack_bores,'DC jack terminal feedthroughs')
    m.cut('Switchboard',pose(Part.makeCompound(pcb_bores)),'Switchboard power input holes')
    bottom=g.rotation((0,0,-1),(0,1,0))
    m.box('BottomModelLabel','Non-serial study identification label',60,28,.08,(-77,70,7.9),'Body',-6,'white',1.4,orient=bottom)
    m.label('BottomModelText','CX2600 / CAD STUDY',2.3,(-53,69,7.79),'Body',-6,'black',rotation=bottom)
    m.label('BottomVersionText','1977 HEAVY SIXER',2.0,(-53,62,7.79),'Body',-6,'black',rotation=bottom)
    front=g.rotation((0,-1,0),(0,0,1));logo=[m.rr(1.3,12,.04)]
    for side in [-1,1]:
        curve=[(side*(2.2+4.8*(i/20)**3),6-12*i/20) for i in range(21)]
        points=[V(x-.6,y,0) for x,y in curve]+[V(x+.6,y,0) for x,y in reversed(curve)]
        wire=Part.makePolygon(points+[points[0]]);logo.append(Part.Face(Part.Wire(wire.Edges)).extrude(V(0,0,.04)))
    mark=Part.makeCompound(logo);mark.Placement=App.Placement(V(139,-116.155,37.5),front)
    m.feature('FujiMark','Atari identification mark study',mark,'Body',4,'metal')
    m.profile['stages']=10
    m.checkpoint(10,'case_mounts_rf_dc_harnesses_and_identification','加入斜面主板支柱、六处机壳紧固件、内部 RF/DC 线束和端子，补齐底部学习标签及前部标识；线束仅说明空间布局，不定义电气网络。')


STAGES[10]=stage10


def stage11(m):
    from .clamshell import _replace
    for i in range(12):_replace(m,'RibbonWire'+str(i),_bounded_ribbon(-11+i*2,clearance=.15))
    frame=_control_frame();q=frame.Rotation
    start=frame.multVec(V(118,-29,-12.5));a=V(145,55,27);b=V(110,98,30);end=V(110,107.9,30)
    wire=_cubic_pipe([[start,start+q.multVec(V(0,-9,0)),V(145,20,27),a],[a,V(145,96,27),V(110,86,30),b],[b,V(110,101,30),V(110,105,30),end]],.9)
    _replace(m,'InternalRFLead',wire)
    m.profile['stages']=11
    m.checkpoint(11,'terminal_and_rf_bulkhead_clearances','为排线端部保留 0.15 mm 展示间隙，避免共面端盖造成求交歧义；将 RF 内线末段沿护套轴线拉直，核对入口配合。')


STAGES[11]=stage11


def stage12(m):
    from .clamshell import _replace
    frame=_control_frame();q=frame.Rotation
    def pose(shape):
        shape.Placement=frame.multiply(shape.Placement)
        return shape
    relief=pose(Part.makeCylinder(.55,6,V(-128.54,-30.3,-20)))
    m.cut('SwitchboardPost0',relief,'Regulator lead relief in mounting boss')
    for x in [-35,35]:m.cut('ShieldBase',Part.makeCylinder(.85,2.8,V(x,-42,18.2)),'Full shaft-depth clearance in casting pilot')
    start=frame.multVec(V(118,-29,-12.5));t=frame.multVec(V(118,-35,-12.5));c=V(145,5,28);a=V(145,55,27);b=V(110,98,30);end=V(110,107.9,30)
    groups=[[start,frame.multVec(V(118,-31,-12.5)),frame.multVec(V(118,-33,-12.5)),t],
            [t,t+q.multVec(V(0,-6,0)),c-V(12,0,0),c],
            [c,c+V(12,0,0),a-V(0,20,0),a],
            [a,V(145,96,27),V(110,86,30),b],
            [b,V(110,101,30),V(110,105,30),end]]
    _replace(m,'InternalRFLead',_cubic_pipe(groups,.9))
    for i,side in enumerate([-1,1]):
        start=V(side*3.1,103.55,27);a=V(-60,88,36+side*2);b=V(-104,50,32+side*2);c=V(-146,10,30+side*2)
        end=frame.multVec(V(-135+side*1.3,-32,-16.6))
        groups=[[start,start+V(0,-12,0),a+V(14,0,0),a],
                [a,a+V(-15,0,0),b+V(0,13,0),b],
                [b,b+V(0,-12,0),c-V(0,10,0),c],
                [c,c+V(0,8,0),end-q.multVec(V(0,0,3)),end]]
        _replace(m,'InternalDCWire'+str(i),_cubic_pipe(groups,.55))
    m.profile['stages']=12
    m.checkpoint(12,'harness_layers_and_mounting_clearance','将两条 DC 线分层并从支柱前方绕行，RF 线先平直离开电路板再沿侧壁布置；补齐支柱引脚避让和铸件螺钉孔深。')


STAGES[12]=stage12


def _rounded_route(points,bend_radius,wire_radius):
    """Round each route corner with an exact circular arc before sweeping."""
    edges=[];last=points[0]
    for previous,current,following in zip(points,points[1:],points[2:]):
        incoming=(current-previous).normalize();outgoing=(following-current).normalize()
        angle=math.acos(max(-1,min(1,incoming.dot(outgoing))))
        if angle<1e-6:continue
        trim=bend_radius*math.tan(angle/2)
        assert trim<.45*min((current-previous).Length,(following-current).Length)
        entry=current-incoming*trim;leave=current+outgoing*trim
        center=current+(outgoing-incoming).normalize()*(bend_radius/math.cos(angle/2))
        middle=center+(current-center).normalize()*bend_radius
        edges.extend([Part.makeLine(last,entry),Part.Arc(entry,middle,leave).toShape()]);last=leave
    edges.append(Part.makeLine(last,points[-1]));path=Part.Wire(edges)
    section=Part.Wire(Part.makeCircle(wire_radius,points[0],points[1]-points[0]))
    shape=path.makePipeShell([section],True,False)
    assert shape.isValid() and len(shape.Solids)==1
    return shape


def _analytic_ribbon(x):
    frame=_control_frame();start=V(x,80,27.65);local=frame.inverse().multVec(start)
    direction=frame.Rotation.inverted().multVec(V(0,0,1))
    points=[local,local+direction*6,V(x,37,-38),V(x,37,-6),V(x,24,-6),V(x,24,-11.05)]
    return _rounded_route([frame.multVec(p) for p in points],2,.62)


def stage13(m):
    from .clamshell import _replace
    frame=_control_frame();q=frame.Rotation
    prototype=_analytic_ribbon(0);prototype.check(True)
    changes={}
    for i in range(12):
        shape=prototype.copy();shape.translate(V(-11+i*2,0,0));changes['RibbonWire'+str(i)]=shape
    rf=[frame.multVec(V(118,-29,-12.5)),frame.multVec(V(118,-36,-12.5)),frame.multVec(V(118,-42,-12.5)),V(145,5,28),V(156,5,28),V(145,55,27),V(145,90,27),V(110,98,30),V(110,107.9,30)]
    changes['InternalRFLead']=_rounded_route(rf,2,.9)
    for i,side in enumerate([-1,1]):
        end=frame.multVec(V(-135-side*1.3,-32,-16.6))
        points=[V(side*3.1,103.55,27),V(side*3.1,94,27),V(-60,88,36+side*2),V(-104,50,32+side*2),V(-104,24,32+side*2),V(-146,0,30+side*2),V(-146,10,30+side*2),V(-146,18,30+side*2),end-q.multVec(V(0,0,3)),end]
        changes['InternalDCWire'+str(i)]=_rounded_route(points,1,.55)
    for key,shape in changes.items():shape.check(True)
    for key,shape in changes.items():_replace(m,key,shape)
    m.profile['stages']=13
    m.checkpoint(13,'analytic_wire_bends_and_uncrossed_dc_terminals','改用精确圆弧弯管构造排线和内部 RF/DC 线，消除扫掠曲面的自相交问题；调整 DC 末端走向，所有新线段均通过严格布尔几何检查。')


STAGES[13]=stage13


def _joystick_position(number):
    return V(-95 if number==1 else 95,-220,0)


def _place_new_parts(m,before,offset):
    transform=App.Placement(offset,App.Rotation())
    for key in set(m.parts)-before:
        obj=m.parts[key];obj.Placement=transform.multiply(obj.Placement);obj.FlatPlacement=obj.Placement


def _joystick_shell(m,number):
    from .psp import _polygon
    prefix='J'+str(number);group='Controller'+str(number);before=set(m.parts)
    m.native(prefix+'Bottom','CX10 lower cover',90,90,5,2,(0,0,2),group,-6,'atariblack')
    m.native(prefix+'Frame','CX10 hollow base frame',90,90,5,28,(0,0,4.2),group,0,'atariblack')
    m.cut(prefix+'Frame',m.rr(86,86,28.5,(0,0,4),3),'Joystick base inner cavity')
    m.native(prefix+'Top','CX10 upper face',90,90,5,2.2,(0,0,32.4),group,4,'atariblack')
    m.cut(prefix+'Top',[Part.makeCylinder(9.3,3,V(0,0,32.1)),Part.makeCylinder(7.5,3,V(-32,29,32.1))],'Stick and fire-button apertures')
    for i,(x,y) in enumerate([(-35,-35),(35,-35),(-35,35),(35,35)]):
        m.cyl(prefix+'Foot'+str(i),'Joystick bottom support',3.5,1.8,(x,y,0),group,-6,'rubber')
    octagon=[(8*math.cos(i*math.pi/4),8*math.sin(i*math.pi/4)) for i in range(8)]
    handle=_polygon(octagon,29.1,76.9).fuse(Part.makeCylinder(26,3.2,V(0,0,26)))
    handle=handle.fuse(Part.makeCylinder(5.5,10.1,V(0,0,16.1)))
    for x,y in [(0,-17),(0,17),(-17,0),(17,0)]:handle=handle.fuse(Part.makeCylinder(2.3,5.3,V(x,y,20.8)))
    hexagon=[(6.5*math.cos(i*math.pi/3),6.5*math.sin(i*math.pi/3)) for i in range(6)]
    handle=handle.cut(_polygon(hexagon,105.8,.5))
    m.feature(prefix+'Handle','Rigid CX10 handle, lower disc and spring posts',handle,group,6,'black')
    boot=Part.makeCone(27,9,14,V(0,0,35))
    for z in [36,40,44,47]:
        radius=27-(z-35)*18/14
        boot=boot.fuse(Part.makeTorus(radius,.9,V(0,0,z)))
    boot=boot.cut(Part.makeCone(25.8,8.4,14.2,V(0,0,34.9)))
    boot.check(True)
    m.feature(prefix+'Boot','Concentric flexible joystick boot',boot,group,5,'black')
    cap=Part.makeCylinder(7.2,4.5,V(-32,29,33.4))
    cap=cap.makeFillet(.5,[e for e in cap.Edges if e.BoundBox.ZMin>37.8])
    cap=cap.fuse(Part.makeCylinder(2.6,6.4,V(-32,29,27.1))).fuse(Part.makeCylinder(5.5,1.1,V(-32,29,26.1)))
    m.feature(prefix+'Fire','Long-throw red fire button and spring seat',cap,group,6,'red')
    dashes=[]
    for i in range(32):
        angle=i*360/32;theta=math.radians(angle)
        bar=m.rr(1.1,2.4,.04,r=.1)
        bar.Placement=App.Placement(V(30.8*math.cos(theta),30.8*math.sin(theta),34.7),App.Rotation(V(0,0,1),angle))
        dashes.append(bar)
    m.feature(prefix+'OrangeRing','Segmented orange direction ring',Part.makeCompound(dashes),group,4,'orange')
    badge=_polygon([(6.2*math.cos(i*math.pi/3),6.2*math.sin(i*math.pi/3)) for i in range(6)],105.9,.15)
    m.feature(prefix+'HexBadge','Original-style hexagonal stick-top badge',badge,group,6,'metal')
    m.label(prefix+'BadgeText','ATARI',1.7,(-3.0,-.65,106.08),group,6,'black')
    m.cut(prefix+'Frame',Part.makeCylinder(3.4,6,V(0,42,19),V(0,1,0)),'Rear joystick cable passage')
    m.ring(prefix+'Grommet','Joystick cable strain relief',3.1,2.05,4.5,(0,42.8,19),group,0,'rubber',axis=(0,1,0))
    _place_new_parts(m,before,_joystick_position(number))


def stage14(m):
    for number in [1,2]:_joystick_shell(m,number)
    m.profile['stages']=14
    m.checkpoint(14,'two_original_cx10_joystick_shells','建立两只 CX10 的独立原生分壳、红色长行程按钮、刚性摇杆盘与四个弹簧柱、同心橡胶防尘套、橙色方向环和顶部六角标牌，保留初代无 TOP 字样的外观。')


STAGES[14]=stage14


def _helical_spring(radius,pitch,height,wire_radius):
    # Preserve the native helix, splitting only at its spline knots so the sweep
    # does not create a single surface with internal continuity defects.
    edge=Part.makeHelix(pitch,height,radius).Edges[0];curve=edge.Curve
    knots=[edge.FirstParameter]+[k for k in curve.getKnots() if edge.FirstParameter+1e-9<k<edge.LastParameter-1e-9]+[edge.LastParameter]
    edges=[curve.toShape(a,b) for a,b in zip(knots,knots[1:])]
    section=Part.Wire(Part.makeCircle(wire_radius,edges[0].Vertexes[0].Point,edges[0].tangentAt(edges[0].FirstParameter)))
    spring=Part.Wire(edges).makePipeShell([section],True,True)
    spring.check(True)
    return spring


def _joystick_internals(m,number):
    prefix='J'+str(number);group='Controller'+str(number);before=set(m.parts);offset=_joystick_position(number)
    m.colors['actuator']=(.75,.75,.65)
    spring=_helical_spring(3.2,3.5,14,.28)
    m.box(prefix+'PCB','CX10 five-contact circuit board study',72,70,1.6,(-5,5,7),group,-2,'pcb',2,True)
    stations=[(0,-17),(0,17),(-17,0),(17,0),(-32,29)]
    plate=m.rr(72,66,.8,(-4,2,10.2),3).cut(Part.makeCylinder(8.8,1.2,V(0,0,10)))
    slots=[]
    for i,(x,y) in enumerate(stations):
        cup=Part.makeCylinder(4.8,3.2,V(x,y,10.95)).cut(Part.makeCylinder(3.7,3.1,V(x,y,11.2)))
        plate=plate.fuse(cup).fuse(Part.makeCylinder(1.2,.83,V(x,y,9.42)))
        ring=Part.makeCylinder(6.5,2,V(0,0,10)).cut(Part.makeCylinder(5.5,2.2,V(0,0,9.9)))
        ring=ring.common(Part.makeBox(20,10,3,V(-10,-10,9.8)))
        slot=Part.makeCompound([ring,m.rr(1,5,2,(-6,2.5,10),.2),m.rr(1,5,2,(6,2.5,10),.2)])
        angle=[180,0,90,-90,0][i];slot.rotate(V(),V(0,0,1),angle);slot.translate(V(x,y,0));slots.append(slot)
        wire=spring.copy();wire.translate(V(x,y,11.6))
        m.feature(prefix+'Spring'+str(i),'CX10 directional return spring' if i<4 else 'CX10 fire-button return spring',wire,group,2,'metal',True)
        pads=Part.makeCompound([m.rr(1.8,4,.05,(x+side*1.1,y,8.65),.2) for side in [-1,1]])
        m.feature(prefix+'ContactPads'+str(i),'Separated fixed switch contacts',pads,group,-2,'gold',True)
        points=[V(x-3.5,y-1.2,8.93),V(x,y-1.2,9.15),V(x+3.5,y-1.2,8.93),V(x+3.5,y-1.2,9.05),V(x,y-1.2,9.27),V(x-3.5,y-1.2,9.05)]
        outline=Part.makePolygon(points+[points[0]])
        m.feature(prefix+'ContactLeaf'+str(i),'Raised spring contact leaf',Part.Face(Part.Wire(outline.Edges)).extrude(V(0,2.4,0)),group,-2,'metal',True)
    plate=plate.cut(Part.makeCompound(slots));assert len(plate.Solids)==1
    m.feature(prefix+'ActuatorPlate','CX10 five-finger actuator plate and spring cups',plate,group,1,'actuator',True)
    holes=[]
    for i,(x,y) in enumerate([(-37,-26),(27,-26),(-37,36),(27,36)]):
        m.ring(prefix+'PCBSpacer'+str(i),'Joystick PCB spacer',2.2,1.0,2.6,(x,y,4.25),group,-3,'actuator',internal=True)
        m.screw(prefix+'PCBScrew'+str(i),(x,y,9.05),group,-2,length=4.1,radius=1.7,axis=(0,0,-1))
        holes.append(Part.makeCylinder(1.1,2.2,V(x,y,6.8)))
    bottom_holes=[]
    for i,(x,y) in enumerate([(-40,-40),(40,-40),(-40,40),(40,40)]):
        post=Part.makeCylinder(2.4,28.05,V(x,y,4.25)).cut(Part.makeCylinder(.9,21.9,V(x,y,4.1)))
        m.feature(prefix+'CasePost'+str(i),'Joystick case screw boss',post,group,0,'atariblack',True)
        m.screw(prefix+'CaseScrew'+str(i),(x,y,1.3),group,-6,length=22,radius=1.7)
        bottom_holes.append(Part.makeCylinder(1.05,2.8,V(x,y,1.8)))
        holes.append(Part.makeCylinder(2.8,2.2,V(x,y,6.8)))
    m.cut(prefix+'PCB',holes,'PCB fastening holes and case-boss corner clearance')
    bottom_tool=Part.makeCompound(bottom_holes);bottom_tool.translate(offset)
    m.cut(prefix+'Bottom',bottom_tool,'Joystick bottom case screw holes')
    _place_new_parts(m,before,offset)


def stage15(m):
    for number in [1,2]:_joystick_internals(m,number)
    m.profile['stages']=15
    m.checkpoint(15,'cx10_springs_actuator_plates_and_pcbs','加入两只 CX10 的专用 PCB、五组独立接点与回位弹簧、带柔性槽的传动板、弹簧杯和紧固结构，表现初代摇杆的内部传动方式。')


STAGES[15]=stage15


def _joystick_cable(m,number):
    from .psp import _polygon
    prefix='J'+str(number);group='Controller'+str(number);before=set(m.parts);offset=_joystick_position(number)
    m.colors.update({'wireyellow':(.65,.58,.04),'wiregreen':(.03,.35,.12)})
    colors=['red','black','white','blue','wiregreen','wireyellow'];bores=[]
    for i,x in enumerate([-10,-6,-2,2,6,10]):
        end=V([-.8,0,.8][i%3],46.9,19+(-.55 if i<3 else .55))
        points=[V(x,36.5,9.1),V(x,39.5,9.1),V(end.x,41.5,end.z),end]
        wire=_rounded_route(points,.7,.22);wire.check(True)
        m.feature(prefix+'SignalWire'+str(i),'CX10 six-wire harness conductor',wire,group,-1,colors[i],True)
        m.cyl(prefix+'HarnessPin'+str(i),'Joystick PCB solder terminal',.22,2.1,(x,36.5,6.9),group,-2,'metal',internal=True)
        bores.append(Part.makeCylinder(.35,2.2,V(x,36.5,6.8)))
    tool=Part.makeCompound(bores);tool.translate(offset)
    m.cut(prefix+'PCB',tool,'Joystick six-wire solder holes')
    route=[V(0,47.5,19),V(0,58,19),V(20,68,16),V(45,68,16),V(52,63,15),V(65.1,63,15)]
    cable=_rounded_route(route,3,1.55);cable.check(True)
    m.feature(prefix+'Cable','Stored joystick lead segment',cable,group,0,'black')
    axis=V(1,0,0);orient=g.rotation((1,0,0),(0,0,1))
    boot=Part.makeCylinder(3.4,7,V(58,63,15),axis).cut(Part.makeCylinder(1.8,7.2,V(57.9,63,15),axis))
    grooves=[]
    for i in range(6):
        grooves.append(Part.makeCylinder(3.5,.5,V(58.5+i,63,15),axis).cut(Part.makeCylinder(2.9,.7,V(58.4+i,63,15),axis)))
    m.feature(prefix+'PlugStrainRelief','Ribbed connector strain relief',boot.cut(Part.makeCompound(grooves)),group,0,'rubber')
    housing=m.rr(34,18,16,(65,63,15),3,orient).cut(Part.makeCylinder(1.8,4,V(64.8,63,15),axis))
    m.feature(prefix+'PlugBody','Original-style moulded joystick plug',housing,group,0,'black')
    nose=_polygon([(-13,-5.8),(13,-5.8),(11.5,5.8),(-11.5,5.8)],0,6)
    placement=App.Placement(V(81.2,63,15),orient);nose.Placement=placement
    holes=[]
    for row,count,z in [(0,5,-1.4),(1,4,1.4)]:
        for i in range(count):
            pin=1+row*5+i;point=placement.multVec(V((i-(count-1)/2)*2.77,z,-.3))
            holes.append(Part.makeCylinder(.8,6.5,point,axis))
            if pin in [1,2,3,4,6,8]:
                point=placement.multVec(V((i-(count-1)/2)*2.77,z,.2))
                m.ring(prefix+'PlugContact'+str(pin),'Used DE-9 female joystick contact',.7,.46,5.7,tuple(point),group,0,'metal',axis=(1,0,0),internal=True)
    m.feature(prefix+'PlugNose','Nine-position female connector insulator',nose.cut(Part.makeCompound(holes)),group,0,'black')
    m.label(prefix+'PlugMark','CX10',2.0,(68,61,24.05),group,0,'white')
    _place_new_parts(m,before,offset)


def stage16(m):
    for number in [1,2]:_joystick_cable(m,number)
    m.profile['stages']=16
    m.checkpoint(16,'cx10_six_wire_harnesses_and_de9_plugs','加入两套六芯内部线束、PCB 接线点、收纳状态的摇杆线缆和 DE-9 母插头，区分九个孔位与实际使用的六个接点；线长为展示片段。')


STAGES[16]=stage16


def stage17(m):
    for number in [1,2]:
        offset=_joystick_position(number)
        for i,x in enumerate([-10,-6,-2,2,6,10]):
            end=V((i-2.5)*.4,46.9,19+(-.55 if i%2==0 else .55))
            points=[V(x,36.5,9.15),V(x,36.5,11.5),V(x,39.5,11.5),V(end.x,41.5,end.z),end]
            wire=_rounded_route(points,.7,.22);wire.check(True);wire.translate(offset)
            obj=m.parts['J'+str(number)+'SignalWire'+str(i)]
            obj.Placement=App.Placement();obj.Shape=wire;obj.FlatPlacement=obj.Placement
    m.profile['stages']=17
    m.checkpoint(17,'cx10_ordered_wire_bundle_and_solder_clearance','将六芯线束按端点横向顺序排列并交错分层，先沿 PCB 接线针轴线抬升后再弯折，消除线间交叉和焊接端部重叠。')


STAGES[17]=stage17


def stage18(m):
    from .famicom import _dip,_radial_cap,_axial_resistor
    before=set(m.parts);group='Accessories'
    m.native('CartBack','Blank study cartridge rear cover',82,98,2.4,1.6,(0,0,0),group,-5,'atariblack')
    m.native('CartFront','Blank study cartridge front shell',82,98,2.4,18.2,(0,0,1.8),group,4,'atariblack')
    m.cut('CartFront',m.rr(78.4,94.4,16.6,(0,0,1.6),.8),'Cartridge interior cavity')
    m.cut('CartFront',m.rr(53,3.4,5,(0,-47.7,8.1),.5),'Cartridge board-edge opening')
    pcb=m.rr(60,80,1.6,(0,5,9),1.0).fuse(m.rr(50,14.1,1.6,(0,-42,9),.5))
    m.feature('CartPCB','Generic ROM cartridge PCB and edge tab',pcb,group,-2,'pcb',True)
    for side,z in [('Front',10.65),('Back',8.91)]:
        for i in range(12):m.box('CartContact'+side+str(i),'Cartridge edge contact',2.8,9,.04,((i-5.5)*4,-43,z),group,-2,'gold',.12,True)
    _dip(m,'CartROM','ROM PACKAGE',0,10,29,8,24,z=11,t=3.9,assembly=group,board='CartPCB')
    for i,(x,y) in enumerate([(-22,20),(22,-15)]):
        _radial_cap(m,'CartCap'+str(i),x,y,11,r=2,h=4,assembly=group,board='CartPCB')
        m.cut('CartCap'+str(i),[Part.makeCylinder(.28,.7,V(x+side*.8,y,10.9)) for side in [-1,1]],'Capacitor lead entry clearances')
    for i,(x,y) in enumerate([(-20,-17),(20,32)]):_axial_resistor(m,'CartResistor'+str(i),x,y,z=12.7,assembly=group,board='CartPCB')
    post=Part.makeCylinder(3,16.25,V(0,32,1.85)).cut(Part.makeCylinder(.85,12,V(0,32,1.7)))
    m.feature('CartCasePost','Cartridge central fixing boss',post,group,4,'atariblack',True)
    m.cut('CartPCB',Part.makeCylinder(3.3,2,V(0,32,8.8)),'Central case boss through PCB clearance')
    m.cut('CartBack',[Part.makeCylinder(1,1.5,V(0,32,.4)),Part.makeCylinder(1.8,.7,V(0,32,-.1))],'Recessed cartridge fixing hole')
    m.screw('CartScrew',(0,32,.15),group,-5,length=10,radius=1.7)
    for i,x in enumerate([-24,24]):m.cyl('CartPCBSupport'+str(i),'Cartridge PCB support',2.4,7.05,(x,-20,1.85),group,-3,'atariblack',internal=True)
    m.box('CartLabel','Original study label without game artwork',72,73,.08,(0,9,20.03),group,4,'black',2)
    border=m.rr(70,71,.03,(0,9,20.13),1.5).cut(m.rr(68.8,69.8,.07,(0,9,20.11),.9))
    m.feature('CartLabelBorder','Orange cartridge label border',border,group,4,'orange')
    for key,text,size,x,y in [('Title','VCS STUDY',6,-27,24),('Contacts','24 CONTACTS / CAD',2.4,-27,12),('Data','NO GAME DATA',3,-27,2)]:
        m.label('Cart'+key+'Text',text,size,(x,y,20.18),group,4,'orange' if key=='Title' else 'white')
    rear=g.rotation((0,1,0),(0,0,1))
    m.box('CartSpineLabel','Cartridge spine study label',68,12,.06,(0,49.04,10),group,4,'black',.8,orient=rear)
    m.label('CartSpineText','VCS STUDY',3,(17,49.13,9),group,4,'orange',rotation=rear)
    _place_new_parts(m,before,V(-260,-160,0))
    m.profile['stages']=18
    m.checkpoint(18,'blank_24_contact_study_cartridge','建立两片原生卡带壳、24 个金属接点、PCB、ROM 封装和固定结构，采用原创 VCS STUDY 标签；不包含游戏 ROM、封面或电路数据。')


STAGES[18]=stage18


def _paddle_position(number):
    return V(270,0 if number==1 else -120,0)


def _paddle_body(m,number):
    prefix='Pad'+str(number);group='Accessories';before=set(m.parts)
    slope=11/34.5
    outer_cut=_yz_prism([(-50,30+slope*(-50+12)),(-12,30),(-12,45),(-50,45)],-40,80)
    inner_cut=_yz_prism([(-50,27.6+slope*(-50+12)),(-12,27.6),(-12,45),(-50,45)],-40,80)
    m.native(prefix+'Bottom','CX30-04 paddle bottom cover',65,93,8,1.8,(0,0,0),group,-5,'atariblack')
    m.native(prefix+'Top','CX30-04 sloping upper shell',65,93,8,28,(0,0,2),group,4,'atariblack')
    m.cut(prefix+'Top',outer_cut,'Sloping paddle label face')
    cavity=m.rr(61.4,89.4,25.8,(0,0,1.8),6.2).cut(inner_cut)
    m.cut(prefix+'Top',cavity,'Following paddle shell interior')
    m.cut(prefix+'Top',[Part.makeCylinder(4.7,5,V(0,15,27)),Part.makeCylinder(1.8,6,V(-34,8,22),V(1,0,0)),Part.makeCylinder(3.1,6,V(0,43,15),V(0,1,0))],'Knob shaft, side fire button and cable clearances')
    m.cyl(prefix+'PotBase','Potentiometer metal base',12,.7,(0,15,8.3),group,-2,'metal',internal=True)
    can=Part.makeCylinder(12,10,V(0,15,9.1)).cut(Part.makeCylinder(10.6,10.2,V(0,15,9)))
    terminal_cut=m.rr(8.4,9.4,3.2,(14.8,15,9.1),.4)
    m.feature(prefix+'PotCan','Potentiometer case with terminal opening',can.cut(terminal_cut),group,-2,'metal',True)
    m.ring(prefix+'PotSubstrate','Potentiometer insulating substrate',10.3,3.3,.8,(0,15,9.3),group,-2,'phenolic',internal=True)
    track=Part.makeCylinder(9.6,.06,V(0,15,10.15),V(0,0,1),300).cut(Part.makeCylinder(8.4,.1,V(0,15,10.13)))
    track.rotate(V(0,15,0),V(0,0,1),30)
    m.feature(prefix+'ResistanceTrack','One-megohm paddle resistive-track study',track,group,-2,'black',True)
    m.cyl(prefix+'PotRotor','Potentiometer wiper rotor',5.8,1.2,(0,15,11),group,0,'white',internal=True)
    arm=m.rr(7,.9,.15,(5.3,15,10.45),.2)
    m.feature(prefix+'Wiper','Moving potentiometer contact arm',arm,group,0,'copper',True)
    m.ring(prefix+'PotLid','Potentiometer top plate',12,3.3,.6,(0,15,19.25),group,0,'metal',internal=True)
    m.cyl(prefix+'PotShaft','Paddle rotary shaft',3.1,24,(0,15,12.35),group,2,'metal',internal=True)
    m.ring(prefix+'PotBushing','Potentiometer mounting bushing',4.5,3.2,7,(0,15,23),group,2,'metal',internal=True)
    from .psp import _polygon
    nut=_polygon([(7*math.cos(i*math.pi/3),15+7*math.sin(i*math.pi/3)) for i in range(6)],30.3,2).cut(Part.makeCylinder(4.6,2.4,V(0,15,30.1)))
    m.feature(prefix+'MountNut','Paddle shaft hexagonal mounting nut',nut,group,4,'metal')
    knob=Part.makeCylinder(27.5,15.5,V(0,15,32.5)).cut(Part.makeCylinder(24.5,13,V(0,15,32.3)))
    hub=Part.makeCylinder(6.5,12.7,V(0,15,32.7)).cut(Part.makeCylinder(3.25,13,V(0,15,32.5)))
    knob=knob.fuse(hub)
    grips=[Part.makeCylinder(.6,13.8,V(27.55*math.cos(i*2*math.pi/48),15+27.55*math.sin(i*2*math.pi/48),33.1)) for i in range(48)]
    knob=knob.cut(Part.makeCompound(grips)).cut(Part.makeCylinder(25.5,.6,V(0,15,47.7)))
    m.feature(prefix+'Knob','Fluted paddle knob with recessed top',knob,group,6,'black')
    left=g.rotation((-1,0,0),(0,0,1))
    fire=m.rr(22,5.5,2,(-32.7,8,22),.5,left).fuse(Part.makeCylinder(1.5,7.4,V(-25.5,8,22),V(-1,0,0)))
    fire=fire.fuse(Part.makeCylinder(3,1,V(-27,8,22),V(-1,0,0)))
    m.feature(prefix+'Fire','Red side fire button and plunger',fire,group,6,'red')
    switch=m.rr(10,7,7,(-22,8,18.5),.6).cut(Part.makeCylinder(1.75,3.7,V(-28,8,22),V(1,0,0)))
    switch_holes=[Part.makeCylinder(.35,3.5,V(x,8.8,20),V(0,1,0)) for x in [-23,-20]]
    m.feature(prefix+'FireSwitch','Paddle fire microswitch body',switch.cut(Part.makeCompound(switch_holes)),group,-2,'black',True)
    for i,x in enumerate([-23,-20]):m.cyl(prefix+'SwitchTerminal'+str(i),'Fire microswitch solder terminal',.22,3,(x,9,20),group,-2,'metal',axis=(0,1,0),internal=True)
    block=m.rr(8,9,2.5,(14.8,15,9.25),.4)
    slots=[m.rr(9,.9,.5,(16,y,10.15),.1) for y in [12.2,15,17.8]]
    m.feature(prefix+'PotTerminalBlock','Potentiometer terminal insulator',block.cut(Part.makeCompound(slots)),group,-2,'phenolic',True)
    for i,y in enumerate([12.2,15,17.8]):m.box(prefix+'PotTerminal'+str(i),'Potentiometer solder tab',8.7,.6,.2,(16.15,y,10.3),group,-2,'metal',.04,True)
    m.ring(prefix+'Grommet','Paddle rear cable grommet',2.8,1.5,4,(0,44.4,15),group,0,'rubber',axis=(0,1,0))
    # Early 1977 label uses ATARI and tennis-racket graphics rather than PADDLE text.
    q=App.Rotation(V(1,0,0),math.degrees(math.atan(slope)))
    label_frame=App.Placement(V(0,-28,30-16*slope),q)
    plaque=m.rr(46,20,.06,r=1);plaque.Placement=label_frame.multiply(App.Placement(V(0,0,.08),App.Rotation()))
    m.feature(prefix+'Label','Early paddle faceplate',plaque,group,4,'black')
    border=m.rr(45,19,.025,r=.8).cut(m.rr(43.8,17.8,.06,(0,0,-.02),.3));border.Placement=label_frame.multiply(App.Placement(V(0,0,.16),App.Rotation()))
    m.feature(prefix+'LabelBorder','Paddle label border',border,group,4,'orange')
    m.label(prefix+'LabelText','ATARI',2.8,tuple(label_frame.multVec(V(-20,-6,.20))),group,4,'white',rotation=q)
    symbols=[]
    for x,angle in [(5,-25),(15,25)]:
        ring=Part.makeCylinder(3.8,.03).cut(Part.makeCylinder(3.0,.06,V(0,0,-.01)))
        handle=m.rr(1.1,5.8,.03,(0,-5.8,0),.3)
        symbol=ring.fuse(handle);symbol.rotate(V(),V(0,0,1),angle);symbol.translate(V(x,2,.2));symbols.append(symbol)
    symbol=Part.makeCompound(symbols);symbol.Placement=label_frame.multiply(symbol.Placement)
    m.feature(prefix+'Rackets','Early tennis-racket label graphics',symbol,group,4,'orange')
    _place_new_parts(m,before,_paddle_position(number))


def stage19(m):
    for number in [1,2]:_paddle_body(m,number)
    m.profile['stages']=19
    m.checkpoint(19,'original_cx30_04_paddles_and_potentiometers','建立原始 CX30-04 旋钮控制器的斜面分壳、滚花旋钮、侧面红按钮、1 MΩ 电位器内部结构和早期网球拍标识；两只控制器的共用线缆随后装配。')


STAGES[19]=stage19


def _joystick_ordered_fan(index):
    x=[-10,-6,-2,2,6,10][index];upper=index>=3
    level=14 if upper else 12;lift=40.7 if upper else 42.4
    endx=(index%3-1)*1.1;endz=19+(.55 if upper else -.55)
    points=[V(x,36.5,9.15),V(x,36.5,level),V(endx,lift,level),V(endx,lift,endz),V(endx,46.9,endz)]
    shape=_rounded_route(points,.7,.22);shape.check(True)
    return shape


def _female_de9(m,prefix,origin,used,label):
    from .psp import _polygon
    before=set(m.parts);group='Accessories';axis=V(1,0,0);orient=g.rotation((1,0,0),(0,0,1))
    boot=Part.makeCylinder(3.4,7,V(-7,0,0),axis).cut(Part.makeCylinder(1.85,7.2,V(-7.1,0,0),axis))
    m.feature(prefix+'StrainRelief','Shared cable connector strain relief',boot,group,0,'rubber')
    body=m.rr(34,18,16,(0,0,0),3,orient).cut(Part.makeCylinder(1.85,4,V(-.2,0,0),axis))
    m.feature(prefix+'Body','Moulded DE-9 cable connector',body,group,0,'black')
    nose=_polygon([(-13,-5.8),(13,-5.8),(11.5,5.8),(-11.5,5.8)],0,6)
    placement=App.Placement(V(16.2,0,0),orient);nose.Placement=placement;holes=[]
    for row,count,z in [(0,5,-1.4),(1,4,1.4)]:
        for i in range(count):
            pin=1+row*5+i;point=placement.multVec(V((i-(count-1)/2)*2.77,z,-.3))
            holes.append(Part.makeCylinder(.8,6.5,point,axis))
            if pin in used:
                point=placement.multVec(V((i-(count-1)/2)*2.77,z,.2))
                m.ring(prefix+'Contact'+str(pin),'Paddle cable female contact',.7,.46,5.7,tuple(point),group,0,'metal',axis=(1,0,0),internal=True)
    m.feature(prefix+'Nose','Nine-position cable plug insulator',nose.cut(Part.makeCompound(holes)),group,0,'black')
    m.label(prefix+'Mark',label,2,(3,-2,9.05),group,0,'white')
    _place_new_parts(m,before,origin)


def stage20(m):
    # Separate the fan-in operation from the upward bend: the two wire layers
    # lift at different rear coordinates, so neither passes through the other.
    prototypes=[_joystick_ordered_fan(i) for i in range(6)]
    for number in [1,2]:
        for i,prototype in enumerate(prototypes):
            wire=prototype.copy();wire.translate(_joystick_position(number));obj=m.parts['J'+str(number)+'SignalWire'+str(i)]
            obj.Placement=App.Placement();obj.Shape=wire;obj.FlatPlacement=obj.Placement
    for number in [1,2]:
        prefix='Pad'+str(number);offset=_paddle_position(number);before=set(m.parts);group='Accessories'
        ends=[V(-.65,47.1,14.35),V(-.65,47.1,15.65),V(.65,47.1,14.35),V(.65,47.1,15.65)]
        routes=[[V(-23,12.15,20),V(-23,32,18),V(-.65,42,14.35),ends[0]],
                [V(-20,12.15,20),V(-20,32,22),V(-.65,42,15.65),ends[1]],
                [V(20.65,12.2,10.4),V(26,12.2,10.4),V(26,33,14),V(.65,42,14.35),ends[2]],
                [V(20.65,17.8,10.4),V(24,17.8,10.4),V(24,33,18),V(.65,42,15.65),ends[3]]]
        for i,points in enumerate(routes):
            wire=_rounded_route(points,.8,.22);wire.check(True)
            m.feature(prefix+'Wire'+str(i),'Paddle internal conductor',wire,group,0,['black','white','red','blue'][i],True)
        # Extend the mounting bushing to the potentiometer lid.
        bushing=Part.makeCylinder(4.5,10,V(0,15,19.95)).cut(Part.makeCylinder(3.2,10.2,V(0,15,19.85)))
        bushing.translate(offset);obj=m.parts[prefix+'PotBushing'];obj.Placement=App.Placement();obj.Shape=bushing;obj.FlatPlacement=obj.Placement
        slope=11/34.5
        above=_yz_prism([(-50,27.5+slope*(-50+12)),(-12,27.5),(-12,45),(-50,45)],-40,80)
        holes=[]
        for i,x in enumerate([-22,22]):
            post=Part.makeCylinder(2.8,24,V(x,-30,2.05)).cut(above).cut(Part.makeCylinder(.9,15,V(x,-30,2)))
            m.feature(prefix+'CasePost'+str(i),'Paddle shell screw boss',post,group,4,'atariblack',True)
            m.screw(prefix+'CaseScrew'+str(i),(x,-30,.1),group,-5,length=12,radius=1.6)
            holes.extend([Part.makeCylinder(1.05,1.8,V(x,-30,.5)),Part.makeCylinder(1.7,.7,V(x,-30,-.1))])
        tool=Part.makeCompound(holes);tool.translate(offset);m.cut(prefix+'Bottom',tool,'Paddle lower-case fastening holes')
        _place_new_parts(m,before,offset)
    routes=[[V(270,47.5,15),V(270,57,15),V(315,65,16),V(325,-10,18),V(325,-42,18),V(334.9,-42,18)],
            [V(270,-72.5,15),V(270,-61,15),V(315,-54,16),V(325,-48,18),V(334.9,-48,18)]]
    for i,points in enumerate(routes):
        wire=_rounded_route(points,3,1.2);wire.check(True)
        m.feature('PaddleBranch'+str(i),'Paired paddle cable branch',wire,'Accessories',0,'black')
    junction=m.rr(10,14,8,(340,-45,14),1.5)
    junction=junction.cut(Part.makeCompound([Part.makeCylinder(1.4,4,V(334.8,y,18),V(1,0,0)) for y in [-42,-48]]+[Part.makeCylinder(1.75,3.3,V(342,-45,18),V(1,0,0))]))
    m.feature('PaddleYJunction','Paddle two-to-one cable junction',junction,'Accessories',0,'rubber')
    cable=_rounded_route([V(345.1,-45,18),V(351,-45,18),V(359,-25,18),V(386.1,-25,18)],3,1.6);cable.check(True)
    m.feature('PaddleSharedCable','Shared paddle controller lead',cable,'Accessories',0,'black')
    _female_de9(m,'PaddlePlug',V(386,-25,18),[3,4,5,7,8,9],'PADDLES')
    m.profile['stages']=20
    m.checkpoint(20,'paired_paddle_wiring_and_layered_joystick_fans','补齐两只旋钮控制器的内部接线、壳体固定件、Y 形分线和共用 DE-9 插头；摇杆线束采用分层收束与错位抬升，保持端部排列顺序。')


STAGES[20]=stage20


def stage21(m):
    before=set(m.parts);group='Accessories';m.colors['adaptergray']=(.42,.43,.42)
    m.native('AdapterBack','Period-style adapter rear cover',55,65,5,1.8,(0,0,0),group,-5,'adaptergray')
    m.native('AdapterFront','Period-style adapter upper shell',55,65,5,38,(0,0,2),group,4,'adaptergray')
    m.cut('AdapterFront',m.rr(51.4,61.4,35.6,(0,0,1.8),3.2),'Adapter case interior')
    blade_holes=[]
    for i,x in enumerate([-6.35,6.35]):
        m.box('AdapterBlade'+str(i),'Flat AC input blade',6,1.3,18.5,(x,10,-15.8),group,-4,'metal',.25)
        blade_holes.append(m.rr(6.5,1.8,2.2,(x,10,-.2),.35))
    m.cut('AdapterBack',blade_holes,'Input blade passages')
    core=m.rr(34,38,23,(0,0,8),1.2).cut(m.rr(16,22,23.4,(0,0,7.8),.6))
    core=core.fuse(m.rr(6,38,23,(0,0,8),.5))
    grooves=[]
    for i in range(22):
        z=8.6+i
        grooves.append(m.rr(34.4,38.4,.12,(0,0,z),1.4).cut(m.rr(33.6,37.6,.2,(0,0,z-.04),1.0)))
    m.feature('TransformerCore','Laminated transformer core geometry study',core.cut(Part.makeCompound(grooves)),group,-2,'metal',True)
    axis=g.rotation((0,1,0),(0,0,1))
    bobbin=m.rr(8,25,18,(0,-9,19.5),.7,axis).cut(m.rr(6.5,23.5,18.4,(0,-9.2,19.5),.4,axis))
    for y in [-9.5,8.9]:
        flange=m.rr(14,31,.6,(0,y,19.5),1.0,axis).cut(m.rr(6.5,23.5,.8,(0,y-.1,19.5),.4,axis))
        bobbin=bobbin.fuse(flange)
    m.feature('TransformerBobbin','Insulating transformer bobbin',bobbin,group,-2,'white',True)
    for key,start in [('Primary',-8.1),('Secondary',.76)]:
        turns=[]
        for i in range(14):
            y=start+i*.53
            turns.append(m.rr(13,29.6,.45,(0,y,19.5),.8,axis).cut(m.rr(8.4,25.4,.65,(0,y-.1,19.5),.4,axis)))
        m.feature('Transformer'+key,key+' winding volume study',Part.makeCompound(turns),group,-2,'copper',True)
    m.box('AdapterPCB','Rectifier and filter board study',46,12,1.3,(0,-24.2,4.3),group,-3,'pcb',1,True)
    pcb_holes=[]
    for i,x in enumerate([-18,-6,6,18]):
        m.cyl('AdapterDiode'+str(i),'Rectifier diode package study',.9,4,(x-2,-29,8),group,-2,'black',axis=(1,0,0),internal=True)
        leads=[]
        for side in [-1,1]:
            lead=Part.makeCylinder(.18,1.5,V(x+side*2.1,-29,8),V(side,0,0)).fuse(Part.makeCylinder(.18,4,V(x+side*3.6,-29,4.1)))
            leads.append(lead);pcb_holes.append(Part.makeCylinder(.28,1.8,V(x+side*3.6,-29,4.1)))
        m.feature('AdapterDiodeLeads'+str(i),'Rectifier formed leads',Part.makeCompound(leads),group,-2,'metal',True)
        m.ring('AdapterDiodeBand'+str(i),'Diode cathode band',.92,.9,.25,(x-1,-29,8),group,-2,'white',axis=(1,0,0),internal=True)
    cap=Part.makeCylinder(3,9,V(0,-23.5,6)).cut(Part.makeCompound([Part.makeCylinder(.3,.65,V(side*.8,-23.5,5.8)) for side in [-1,1]]))
    m.feature('AdapterFilterCap','Output filter capacitor study',cap,group,-2,'black',True)
    m.cyl('AdapterCapTop','Filter capacitor top',2.85,.12,(0,-23.5,15.03),group,-2,'metal',internal=True)
    leads=[Part.makeCylinder(.2,2.2,V(side*.8,-23.5,4.1)) for side in [-1,1]]
    m.feature('AdapterCapLeads','Filter capacitor leads',Part.makeCompound(leads),group,-2,'metal',True)
    pcb_holes.extend([Part.makeCylinder(.3,1.8,V(side*.8,-23.5,4.1)) for side in [-1,1]])
    back_holes=[]
    for i,x in enumerate([-21,21]):
        post=Part.makeCylinder(2.5,35.2,V(x,-20,2.05)).cut(Part.makeCylinder(.9,15,V(x,-20,1.95)))
        m.feature('AdapterPost'+str(i),'Adapter case screw boss',post,group,4,'adaptergray',True)
        m.screw('AdapterScrew'+str(i),(x,-20,.15),group,-5,length=12,radius=1.7)
        pcb_holes.append(Part.makeCylinder(2.8,1.8,V(x,-20,4.1)))
        back_holes.extend([Part.makeCylinder(1.05,1.7,V(x,-20,.4)),Part.makeCylinder(1.8,.7,V(x,-20,-.1))])
    m.cut('AdapterPCB',pcb_holes,'Board terminal holes and case post clearance')
    m.cut('AdapterBack',back_holes,'Adapter rear fastening holes')
    m.cut('AdapterFront',Part.makeCylinder(2.9,7,V(0,-29,12),V(0,-1,0)),'DC lead outlet')
    m.ring('AdapterGrommet','Adapter DC lead grommet',2.6,1.6,5,(0,-30,12),group,0,'rubber',axis=(0,-1,0))
    points=[V(0,-35.2,12),V(0,-45,12),V(18,-58,10),V(45,-58,10),V(54,-49,10),V(65.1,-49,10)]
    cable=_rounded_route(points,3,1.4);cable.check(True)
    m.feature('AdapterCable','Stored DC output lead',cable,group,0,'black')
    body=Part.makeCylinder(4.4,15,V(65,-49,10),V(1,0,0)).cut(Part.makeCylinder(1.6,4,V(64.8,-49,10),V(1,0,0)))
    m.feature('AdapterPlugBody','3.5 mm mono DC plug grip',body,group,0,'black')
    m.cyl('AdapterPlugSleeve','DC mono plug sleeve',1.75,7,(80.2,-49,10),group,0,'metal',axis=(1,0,0))
    m.cyl('AdapterPlugInsulator','Mono plug insulating band',1.7,.6,(87.3,-49,10),group,0,'black',axis=(1,0,0))
    tip=Part.makeCylinder(1.75,3.8,V(88,-49,10),V(1,0,0)).fuse(Part.makeSphere(1.75,V(91.8,-49,10)))
    m.feature('AdapterPlugTip','Rounded DC mono plug tip',tip,group,0,'metal')
    m.box('AdapterRatingLabel','Adapter study rating label',45,47,.08,(0,0,40.04),group,4,'white',1.5)
    for key,text,size,x,y in [('Title','AC ADAPTOR',3.7,-18,12),('Output','DC 9 V / 500 mA',2.5,-18,2),('Study','GEOMETRY STUDY',2.1,-18,-8)]:
        m.label('Adapter'+key+'Text',text,size,(x,y,40.17),group,4,'black')
    _place_new_parts(m,before,V(-260,20,16))
    m.profile['stages']=21
    m.checkpoint(21,'period_adapter_and_dc_mono_plug','建立同代灰色适配器分壳、扁脚与 3.5 mm 单声道 DC 插头，内部加入通用变压器、整流和滤波结构示意；尺寸与电路布局不代表原厂制造数据。')


STAGES[21]=stage21


def stage22(m):
    # Move the complete adapter display group clear of the console side wall.
    for key,obj in m.parts.items():
        if key.startswith(('Adapter','Transformer')):
            obj.Placement.Base+=V(-30,0,0);obj.FlatPlacement=obj.Placement
    before=set(m.parts);group='Accessories'
    m.box('TVBoxAdhesive','TV switch-box rear mounting pad',49,66,.8,(0,0,0),group,-5,'rubber',1.5)
    m.native('TVBoxBase','TV/GAME switch-box base',55,72,2,.6,(0,0,1),group,-4,'metal')
    m.native('TVBoxCover','TV/GAME switch-box metal cover',55,72,2,16.2,(0,0,1.8),group,4,'metal')
    m.cut('TVBoxCover',m.rr(54,71,15.9,(0,0,1.6),1.5),'Thin switch-box shell interior')
    m.box('TVBoxPCB','RF selector contact-board study',48,55,1.3,(0,0,4),group,-2,'phenolic',1,True)
    m.box('TVBoxLabel','TV/GAME study face label',46,59,.07,(0,0,18.04),group,4,'black',.8)
    openings=[Part.makeCylinder(4.3,2,V(x,-20,17.1)) for x in [-14,14]]+[m.rr(6.2,18.2,2,(0,8,17.2),.6)]
    for key in ['TVBoxCover','TVBoxLabel']:m.cut(key,openings,'Antenna terminal and selector openings')
    for i,x in enumerate([-14,14]):
        m.ring('TVBoxAntennaInsulator'+str(i),'Antenna screw insulating bushing',4.1,1.2,2.2,(x,-20,17),group,4,'white')
        m.ring('TVBoxAntennaPad'+str(i),'Antenna clamping washer',3.5,1.2,.25,(x,-20,19.35),group,4,'metal')
        m.ring('TVBoxAntennaStud'+str(i),'Antenna threaded standoff',1.8,.8,11,(x,-20,5.5),group,-2,'metal',internal=True)
        m.screw('TVBoxAntennaScrew'+str(i),(x,-20,20.2),group,6,length=14,radius=2.7,axis=(0,0,-1))
        m.ring('TVBoxTerminalLand'+str(i),'Antenna PCB terminal land',3,1,.05,(x,-20,5.4),group,-2,'gold',internal=True)
    m.box('TVBoxSelector','TV/GAME slide switch body',20,24,4,(0,8,5.5),group,-2,'black',.8,True)
    m.box('TVBoxSlideStem','Selector transmission stem',3,3,9.7,(0,12,9.7),group,2,'metal',.3,True)
    cap=m.rr(5.5,7,2.8,(0,12,18.4),.7).cut(m.rr(3.4,3.4,1.2,(0,12,18.25),.4))
    m.feature('TVBoxSlider','TV/GAME slider cap',cap,group,6,'black')
    for side in [-1,1]:
        for i,y in enumerate([-2,8,18]):m.box('TVBoxSwitchContact'+str(side)+'_'+str(i),'RF selector fixed contact',3,4,.05,(side*5,y,5.4),group,-2,'gold',.2,True)
    m.cut('TVBoxCover',Part.makeCylinder(3.3,9,V(0,34.8,9),V(0,1,0)),'Game RF input connector')
    m.ring('TVBoxRCAOuter','Game input RCA outer contact',3,2.25,7,(0,35.6,9),group,0,'metal',axis=(0,1,0))
    m.ring('TVBoxRCAInsulator','RCA input insulator',2.15,1.65,6,(0,35.8,9),group,0,'white',axis=(0,1,0))
    m.ring('TVBoxRCASocket','RCA input centre socket',1.55,1.25,5,(0,36.6,9),group,0,'metal',axis=(0,1,0),internal=True)
    m.ring('TVBoxRCAFlange','RCA input mounting ring',4.5,3.05,1,(0,36.2,9),group,0,'metal',axis=(0,1,0))
    leads=[]
    for side in [-1,1]:
        points=[V(27.7,side*2,8),V(45,side*2,8),V(57,side*2,7),V(78,side*2,7),V(86,side*2,7),V(92,side*7,7),V(96,side*7,7)]
        wire=_rounded_route(points,2,.8);wire.check(True);leads.append(wire)
        lug=Part.makeCylinder(2.9,.7,V(102,side*7,6.65)).cut(Part.makeCylinder(1.4,.9,V(102,side*7,6.55)))
        lug=lug.cut(m.rr(3.5,2.8,1,(103.7,side*7,6.5),.2)).fuse(m.rr(4.8,2.2,.7,(98.55,side*7,6.65),.3))
        m.feature('TVBoxFork'+str(side),'Twin-lead fork terminal',lug,group,0,'metal')
    top=[V(x,-1.4,z+.15) for x,z in [(27.7,8),(45,8),(57,7),(78,7)]]
    bottom=[V(x,-1.4,z-.15) for x,z in reversed([(27.7,8),(45,8),(57,7),(78,7)])]
    polygon=Part.makePolygon(top+bottom+[top[0]]);web=Part.Face(Part.Wire(polygon.Edges)).extrude(V(0,2.8,0))
    twin=leads[0].fuse(leads[1]).fuse(web);assert twin.isValid() and len(twin.Solids)==1
    m.feature('TVBoxTwinLead','Short flat twin-lead TV output',twin,group,0,'black')
    m.cut('TVBoxCover',[Part.makeCylinder(1.0,4,V(26,side*2,8),V(1,0,0)) for side in [-1,1]]+[m.rr(4,3.2,.6,(27,0,7.7),.1)],'Twin-lead output slot')
    for key,text,size,x,y in [('Title','TV/GAME SWITCH',2,-20,27),('TV','TV',2.4,-3,21),('Game','GAME',2.4,-6,-4),('Antenna','ANTENNA',1.8,-9,-29)]:
        m.label('TVBox'+key+'Text',text,size,(x,y,18.16),group,4,'white')
    rear=g.rotation((0,1,0),(0,0,1))
    m.label('TVBoxInputMark','GAME',1.8,(8,36.06,13),group,4,'black',rotation=rear)
    _place_new_parts(m,before,V(-290,125,0))
    # Finish the console's original fixed RF lead with a mating RCA plug.
    m.ring('RFPlugStrain','Console RF plug strain relief',3,1.95,5,(151,150,24),'Cables',0,'rubber',axis=(1,0,0))
    body=Part.makeCylinder(4.3,12,V(156.15,150,24),V(1,0,0)).cut(Part.makeCylinder(1.95,3.2,V(155.95,150,24),V(1,0,0)))
    m.feature('RFPlugBody','Console RCA plug grip',body,'Cables',0,'black')
    sleeve=Part.makeCylinder(4.1,8,V(168.3,150,24),V(1,0,0)).cut(Part.makeCylinder(3.1,8.2,V(168.2,150,24),V(1,0,0)))
    slots=[Part.makeBox(4,.6,8.6,V(172.6,149.7,19.7)),Part.makeBox(4,8.6,.6,V(172.6,145.7,23.7))]
    m.feature('RFPlugSleeve','Slotted RCA outer sleeve',sleeve.cut(Part.makeCompound(slots)),'Cables',0,'metal')
    m.ring('RFPlugInsulator','RCA plug centre insulator',2.9,1.25,5,(168.4,150,24),'Cables',0,'white',axis=(1,0,0))
    pin=Part.makeCylinder(1.15,8.7,V(168.5,150,24),V(1,0,0)).fuse(Part.makeSphere(1.15,V(177.2,150,24)))
    m.feature('RFPlugPin','RCA centre pin',pin,'Cables',0,'metal')
    m.profile['stages']=22
    m.checkpoint(22,'tv_game_switch_box_and_console_rca_plug','补齐 TV/GAME 射频切换盒、天线螺钉端子、RCA 输入和双线叉形输出，并为主机固定 RF 线加入配套插头；调整适配器展示位置以避开主机。')


STAGES[22]=stage22


def _union_into(m,key,shape,reason):
    old=m.parts[key]
    tool=g.part_feature(m.doc,key+'Fill',reason,shape);m.group('Construction').addObject(tool)
    new=m.doc.addObject('Part::Fuse',key+'Fused');new.Label=old.Label;new.Base=old;new.Tool=tool;new.Refine=True
    m.doc.recompute();assert new.Shape.isValid() and new.Shape.Solids
    old.PhysicalPart=False
    m.register(new,key,old.Assembly,old.ExplodeLayer,old.MaterialDescription,old.Fidelity.startswith('Schematic'),old.PoseGroup)
    old.Visibility=False;tool.Visibility=False


def stage23(m):
    offset=V(-290,125,0)
    for key,z,t in [('TVBoxCover',17.5,.5),('TVBoxLabel',18.04,.07)]:
        plugs=Part.makeCompound([Part.makeCylinder(4.31,t,V(x,-20,z)) for x in [-14,14]]);plugs.translate(offset)
        _union_into(m,key,plugs,'Close top holes for the end-panel antenna terminal layout')
    front=V(0,-1,0);tools=[]
    for i,x in enumerate([-13,13]):
        def ring(ro,ri,length,y,direction):
            return Part.makeCylinder(ro,length,V(x,y,9),direction).cut(Part.makeCylinder(ri,length+.2,V(x,y,9)-direction*.1,direction))
        shapes={
            'TVBoxAntennaInsulator'+str(i):ring(3.7,1.25,2.2,-35,front),
            'TVBoxAntennaPad'+str(i):ring(3.3,1.25,.25,-37.35,front),
            'TVBoxAntennaStud'+str(i):ring(1.8,.8,10.9,-34.8,V(0,1,0)),
            'TVBoxTerminalLand'+str(i):ring(2.8,1,.05,-23.8,V(0,1,0)),
        }
        screw=Part.makeCylinder(2.7,.35).fuse(Part.makeCylinder(.62,14,V(0,0,.33)))
        screw=screw.cut(Part.makeCompound([Part.makeBox(.28,4.05,.22,V(-.14,-2.025,-.02)),Part.makeBox(4.05,.28,.22,V(-2.025,-.14,-.02))]))
        screw.rotate(V(),V(0,1,0),180);screw.rotate(V(),V(1,0,0),90);screw.translate(V(x,-38.2,9))
        shapes['TVBoxAntennaScrew'+str(i)]=screw
        for key,shape in shapes.items():
            shape.translate(offset);obj=m.parts[key];obj.Placement=App.Placement();obj.Shape=shape;obj.FlatPlacement=obj.Placement
        m.parts['TVBoxTerminalLand'+str(i)].Label='Horizontal antenna terminal support washer'
        hole=Part.makeCylinder(3.9,5,V(x,-34.8,9),front);hole.translate(offset);tools.append(hole)
    m.cut('TVBoxCover',tools,'Antenna terminal openings on the metal-box end panel')
    m.colors['cx10badge']=(.025,.06,.13)
    for n in [1,2]:
        badge=m.parts['J'+str(n)+'HexBadge'];badge.MaterialDescription='cx10badge';g.appearance(badge,m.colors['cx10badge'])
        text=m.parts['J'+str(n)+'BadgeText'];text.MaterialDescription='white';g.appearance(text,m.colors['white'])
    # The working dimensions describe this approximate model, not factory specifications.
    groups=[a for a in m.groups if a not in ['Accessories','Controller1','Controller2','Cables','Construction']]
    shape=Part.makeCompound([o.Shape for o in m.parts.values() if o.Assembly in groups]);b=shape.optimalBoundingBox(False,False)
    m.profile.update(width=b.XLength,height=b.YLength,closed_depth=b.ZLength,envelope_groups=groups,envelope_kind='approximate',fidelity='Approximate exterior envelope and details; schematic major internals')
    m.profile['envelope_basis']='Model-measured study envelope, including applied body marks; external leads, detached controllers and accessories excluded. No manufacturer dimensioned drawing or physical measurement was verified.'
    for key,value in [('Width',b.XLength),('Height',b.YLength),('ClosedDepth',b.ZLength)]:
        cell=m.param_cells[key];m.params.set(cell,str(value)+' mm');m.params.set('C'+cell[1:],'Measured approximate study envelope; not factory specification')
    m.profile['stages']=23
    m.checkpoint(23,'metal_switch_box_end_panel_and_model_dimension_basis','按金属切换盒参考图调整天线端子所在端面，校正 CX10 顶标配色，并将参数表的整体尺寸改为本模型实测学习包络；不将近似尺寸标为原厂规格。')


STAGES[23]=stage23
