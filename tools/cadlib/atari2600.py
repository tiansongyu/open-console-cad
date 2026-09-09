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
