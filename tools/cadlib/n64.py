"""Original charcoal Nintendo 64 study with an arched native enclosure."""
import math
import FreeCAD as App
import Part
from .core import V
from . import geometry as g
from .retro_common import fuse_feature


def _arched_roof(m,key,radius):
    old=m.parts[key]
    tool=m.doc.addObject('Part::Cylinder',key+'RoofCylinder')
    tool.Label='Editable transverse roof radius'
    tool.Radius=radius;tool.Height=240
    tool.Placement=App.Placement(V(0,-120,-227),App.Rotation(V(0,0,1),V(0,1,0)))
    m.group('Construction').addObject(tool)
    obj=m.doc.addObject('Part::Common',key+'Arched');obj.Base=old;obj.Tool=tool;obj.Refine=True
    m.doc.recompute();assert obj.Shape.isValid() and obj.Shape.Solids
    obj.Shape.check(True);old.PhysicalPart=False
    m.register(obj,key,old.Assembly,old.ExplodeLayer,old.MaterialDescription)
    obj.Label=old.Label;old.Visibility=False;tool.Visibility=False


def stage01(m):
    m.colors.update(n64grey=(.19,.20,.22),portgrey=(.69,.70,.72),padgrey=(.73,.74,.74),nblue=(.10,.27,.69),ngreen=(.07,.53,.26),nyellow=(.91,.75,.12))
    m.params.set('A3','Depth (Y)');m.params.set('A4','Height (Z)')
    pods=[(x,y) for x in [-108,108] for y in [-73,73]]
    m.native('LowerHousing','Rounded lower enclosure with corner pods',244,178,18,24,(0,0,2),'Body',-6,'n64grey',expr={'Width':'Parameters.Width - 16 mm','Height':'Parameters.Height - 12 mm'})
    fuse_feature(m,'LowerHousing',Part.makeCompound([Part.makeCylinder(22,24,V(x,y,2)) for x,y in pods]),'Four moulded corner pods')
    inner=m.rr(240,174,23,(0,0,4),16)
    inner=inner.multiFuse([Part.makeCylinder(19.8,23,V(x,y,4)) for x,y in pods]).removeSplitter()
    m.cut('LowerHousing',inner,'Lower enclosure and pod cavities')
    m.native('UpperHousing','Original transverse arched upper enclosure',244,178,20,49,(0,0,26.3),'Body',5,'n64grey',expr={'Width':'Parameters.Width - 16 mm','Height':'Parameters.Height - 12 mm'})
    fuse_feature(m,'UpperHousing',Part.makeCompound([Part.makeCylinder(22,10.7,V(x,y,26.3)) for x,y in pods]),'Low upper corner pod shoulders')
    _arched_roof(m,'UpperHousing',300)
    inner=m.rr(240,174,49,(0,0,26.1),18).common(Part.makeCylinder(297.7,240,V(0,-120,-227),V(0,1,0)))
    inner=inner.multiFuse([Part.makeCylinder(19.8,8.6,V(x,y,26.1)) for x,y in pods]).removeSplitter()
    m.cut('UpperHousing',inner,'Constant-radius roof interior and corner cavities')
    for i,(x,y) in enumerate(pods):m.cyl('Foot'+str(i),'Corner support foot',16,1.7,(x,y,0),'Body',-6,'rubber')
    m.profile['stages']=1
    m.checkpoint(1,'native_arch_and_four_corner_pods','建立 260 × 190 mm 整体范围的上下空心壳、四角低台与脚垫，使用可编辑圆柱曲面生成初代 N64 的横向拱形顶盖。')


def _d_socket(width,height,depth):
    left=V(-width/2,-height/2,0);right=V(width/2,-height/2,0);top=V(0,height/2,0)
    wire=Part.Wire([Part.makeLine(left,right),Part.Arc(right,top,left).toShape()])
    return Part.Face(wire).extrude(V(0,0,depth))


def stage02(m):
    front=g.rotation((0,-1,0),(0,0,1))
    for i,x in enumerate([-76,-43,43,76],1):
        for key in ['LowerHousing','UpperHousing']:
            m.cut(key,Part.makeCylinder(13.2,22,V(x,-71,27),V(0,-1,0)),'Controller '+str(i)+' round front-panel opening')
        outer=Part.makeCylinder(12.8,16.3,V(x,-73,27),V(0,-1,0))
        flange=Part.makeCylinder(13.5,1.6,V(x,-89.15,27),V(0,-1,0))
        cup=outer.fuse(flange).cut(Part.makeCylinder(11.4,16.9,V(x,-73.3,27),V(0,-1,0)))
        opening=_d_socket(19,14,3);opening.Placement=App.Placement(V(x,-88.5,28),front)
        cup=cup.cut(opening)
        m.feature('PortCup'+str(i),'Controller '+str(i)+' grey socket body',cup,'Ports',0,'portgrey')
        insert=_d_socket(18.4,13.4,4.3);insert.Placement=App.Placement(V(x,-85,28),front)
        holes=[Part.makeCylinder(1.65,5,V(x+dx,-84.8,25.5),V(0,-1,0)) for dx in [-4.8,0,4.8]]
        m.feature('PortInsert'+str(i),'Three-position connector insert',insert.cut(Part.makeCompound(holes)),'Ports',0,'portgrey',True)
        for j,dx in enumerate([-4.8,0,4.8]):m.ring('PortContact'+str(i)+'_'+str(j),'Three-wire controller socket contact',1.4,1.05,6,(x+dx,-83.4,25.5),'Ports',0,'gold',axis=(0,-1,0),internal=True)
        # Moulded dots identify controllers without relying on printed numerals.
        for j in range(i):m.cyl('PortDot'+str(i)+'_'+str(j),'Controller index dot',.55,.08,(x+(j-(i-1)/2)*2.3,-90.8,17.4),'Ports',0,'portgrey',axis=(0,-1,0))
    m.box('FrontBadge','Central black front badge',58,30,.45,(0,-89.06,54),'Body',5,'black',6,orient=front)
    m.label('Nintendo64Title','NINTENDO 64',3.7,(-24,-89.54,59.3),'Body',5,'white',rotation=front)
    # Geometric colour mark indicates the N64 family without bitmap artwork.
    parts=[([(-12,-8),(-7,-8),(-7,3),(3,-8),(8,-8),(8,10),(3,10),(3,-1),(-7,10),(-12,10)],'ngreen'),
           ([(8,-8),(12,-5),(12,13),(8,10)],'nblue'),
           ([(-12,10),(-8,13),(-3,13),(-7,10)],'nyellow')]
    for i,(points,color) in enumerate(parts):
        wire=Part.makePolygon([V(x,y,0) for x,y in points+[points[0]]]);shape=Part.Face(wire).extrude(V(0,0,.04));shape.Placement=App.Placement(V(0,-89.55,45),front)
        m.feature('ColourMark'+str(i),'N64 colour study mark',shape,'Body',5,color)
    m.cut('LowerHousing',m.rr(8.4,3.2,4,(0,-87,16),1.5,front),'Front red indicator aperture')
    m.box('PowerLens','Small front power indicator',7.6,2.5,.5,(0,-89.05,16),'Controls',0,'red',1.2,orient=front)
    m.profile['stages']=2
    m.checkpoint(2,'four_three_contact_controller_ports','加入四个圆形灰色手柄接口、三路触点与定位圆点，补齐正面徽标和独立电源指示灯，保留上下壳的接口开孔历史。')


def _deck_outline(z,height):
    a=V(-73,82,z);b=V(-73,24,z);c=V(73,24,z);d=V(73,82,z)
    wire=Part.Wire([Part.makeLine(a,b),Part.Arc(b,V(0,-24,z),c).toShape(),Part.makeLine(c,d),Part.makeLine(d,a)])
    return Part.Face(wire).extrude(V(0,0,height))


def stage03(m):
    outer_radius=Part.makeCylinder(299.9,240,V(0,-120,-227),V(0,1,0))
    inner_radius=Part.makeCylinder(298.2,240,V(0,-120,-227),V(0,1,0))
    deck=_deck_outline(62.5,13).common(outer_radius).cut(inner_radius)
    m.cut('UpperHousing',_deck_outline(61.8,15),'Separate curved cartridge-deck opening')
    m.feature('CartridgeDeck','D-shaped curved top cartridge insert',deck,'Body',5,'n64grey')
    slot=m.rr(125,20.2,17,(0,42,59),4.5)
    m.cut('CartridgeDeck',slot,'Top Game Pak insertion opening')
    for i,y in enumerate([37.1,46.9]):
        m.box('DustFlap'+str(i),'Opposed grey cartridge dust door',122,9.4,1.2,(0,y,63.2),'CardReader',5,'portgrey',2.0)
        for side in [-1,1]:m.box('FlapMark'+str(i)+'_'+str(side),'Cartridge door moulding line',.24,8.2,.025,(side*48,y,64.43),'CardReader',5,'n64grey',.05)
    slots=[]
    for x in range(-60,61,8):
        bottom=55.5-math.sqrt(79.5**2-x*x)+4
        slots.append(m.rr(3.2,20-bottom,20,(x,(bottom+20)/2,57),.6))
    m.cut('CartridgeDeck',slots,'Curved array of cartridge-deck ventilation slots')
    # Short raised lettering follows only the almost-flat centre of the roof.
    m.label('TopNintendo','Nintendo',3.1,(-12,70,73.04),'Body',5,'black')
    # A removable cover follows the same transverse arch over the Jumper Pak.
    pocket=m.rr(67,44,18,(0,-59,58),5)
    m.cut('UpperHousing',pocket,'Memory expansion compartment opening')
    cover=m.rr(66.2,43.2,18,(0,-59,58),4.6).common(outer_radius).cut(inner_radius)
    m.feature('MemoryCover','Curved memory expansion cover',cover,'Body',5,'n64grey')
    m.cut('MemoryCover',m.rr(12,4,17,(0,-36.5,59),1),'Expansion-cover finger notch')
    m.label('MemoryTitle','MEMORY EXPANSION',1.9,(-16,-71,72.98),'Body',5,'black')
    for i in range(4):m.cyl('MemoryDot'+str(i),'Memory-cover finger index',.6,.04,(-6+i*4,-48,73.03),'Body',5,'black')
    # Ovoid POWER and RESET controls sit in deeper roof recesses.
    for key,x in [('Power',-72),('Reset',72)]:
        hole=m.rr(19,40,16,(x,-60,57),9)
        m.cut('UpperHousing',hole,key+' oval control recess')
        m.box(key+'Well',key+' recessed switch surround',18.4,39.4,1,(x,-60,57.3),'Controls',3,'black',8.8)
        m.box(key+'Button',key+' control cap',15.3,31,3.5,(x,-60,58.4),'Controls',5,'n64grey',7.4)
        m.label(key+'Title',key.upper(),2.2,(x-6,-68,61.93),'Controls',5,'black')
    m.box('PowerGrip','Power slider raised grip',13,3.7,2,(-72,-56,61.93),'Controls',5,'n64grey',1.5)
    m.profile['stages']=3
    m.checkpoint(3,'curved_cartridge_deck_and_memory_cover','加入随拱形上盖弯曲的卡带台和内存扩展盖，补齐对开灰色防尘门、弧形通风槽、椭圆 POWER/RESET 按键及顶部标识。')


def stage04(m):
    rear=g.rotation((0,1,0),(0,0,1))
    # The original removable PSU occupies the back-right corner.
    pocket=m.rr(63,41,53,(88,77,5),3)
    for key in ['LowerHousing','UpperHousing']:m.cut(key,pocket,'Rear-right detachable power-supply bay')
    m.native('PSULower','Removable NUS-002 power module lower shell',61.8,39.8,2.5,21,(88,77,5.4),'Power',-3,'black')
    m.cut('PSULower',m.rr(58.2,36.2,20,(88,77,7.2),1.1),'Power-module lower cavity')
    m.native('PSUUpper','Removable NUS-002 power module upper shell',61.8,39.8,2.5,25,(88,77,26.7),'Power',3,'black')
    m.cut('PSUUpper',m.rr(58.2,36.2,23.4,(88,77,26.5),1.1),'Power-module upper cavity')
    m.box('PSURelease','Power module release latch',13,10,1.2,(88,92,52),'Power',3,'n64grey',1.4)
    # Nintendo Multi Out; a rectangle with a separate contact tongue.
    x=-58
    opening=m.rr(26.5,10.6,10,(x,84,23),2,rear)
    for key in ['LowerHousing','UpperHousing']:m.cut(key,opening,'Original Multi Out rear opening')
    housing=m.rr(26,10,9,(x,80,23),1.7,rear).cut(m.rr(23.6,7.6,9.3,(x,80.8,23),1,rear))
    m.feature('MultiOutHousing','Nintendo Multi Out insulated housing',housing,'Ports',0,'black')
    m.box('MultiOutTongue','Multi Out contact tongue',21.8,6.5,1.1,(x,84.5,21.8),'Ports',0,'black',.5,True)
    for row in range(2):
        for i in range(6):m.box('MultiOutContact'+str(row)+'_'+str(i),'Multi Out contact',1.4,5.8,.10,(x+(i-2.5)*3.0,84.5,21.65 if row==0 else 23.0),'Ports',0,'gold',.08,True)
    m.label('MultiOutTitle','MULTI OUT',2.3,(-71,89.03,32),'Body',5,'portgrey',rotation=rear)
    # Original right-angle six-position power connector inside the bay.
    m.box('PowerSocket','Six-position power connector body',24,8,12,(88,49,14),'Ports',0,'black',1.0,True)
    holes=[]
    for row in range(2):
        for i in range(3):
            xx=88+(i-1)*6.2;z=17+row*5
            holes.append(Part.makeCylinder(1.1,9,V(xx,44.5,z),V(0,1,0)))
            m.ring('PowerContact'+str(row)+'_'+str(i),'Detachable PSU socket contact',.9,.6,7.8,(xx,45,z),'Ports',0,'gold',axis=(0,1,0),internal=True)
    m.cut('PowerSocket',holes,'Six power-connector contact bores')
    # Side ventilation is cut through both walls, grouped for a compact history.
    slots=[Part.makeBox(8,2.6,13,V(x,y,9)) for x in [-125,117] for y in range(-45,62,7)]
    m.cut('LowerHousing',slots,'Paired lower side ventilation arrays')
    m.profile['stages']=4
    m.checkpoint(4,'multi_out_and_removable_rear_power_module','加入原始 Multi Out 十二接点接口、后右侧可拆电源模块、六位电源连接器和两侧通风孔，保留电源模块上下空心壳。')


def _sop(m,key,title,x,y,w,h,pins,z=11.2,height=1.8):
    m.box(key,title+' low-profile package',w,h,height,(x,y,z),'Mainboard',0,'black',.35,True)
    m.label(key+'Mark',title,min(1.7,w/(len(title)*.8)),(x-w/2+1,y-.7,z+height+.03),'Mainboard',0,'white')
    for side in [-1,1]:
        fingers=[]
        for i in range(pins//2):
            xx=x+(i-(pins/2-1)/2)*(w-2)/(pins/2-1)
            fingers.append(Part.makeBox(.28,1.4,.20,V(xx-.14,y+h/2+.04 if side==1 else y-h/2-1.44,z+.45)))
        m.feature(key+'Leads'+str(side),'SOP lead bank',Part.makeCompound(fingers),'Mainboard',0,'metal',True)


def stage05(m):
    from .megadrive import _qfp
    from .atari2600 import _rounded_route
    # Keep the removable power supply below the original unbroken roof skin.
    roof=Part.makeCylinder(297.5,240,V(0,-120,-227),V(0,1,0))
    bay=m.rr(63,41,53,(88,77,5),3).common(roof)
    tools=[o for o in m.doc.Objects if o.Label.startswith('Rear-right detachable power-supply bay · tool')];assert len(tools)==2,[(o.Name,o.Label) for o in tools]
    for o in tools:o.Shape=bay
    inside=m.rr(58.2,36.2,23.4,(88,77,26.5),1.1).common(Part.makeCylinder(295.2,240,V(0,-120,-227),V(0,1,0)))
    tools=[o for o in m.doc.Objects if o.Label=='Power-module upper cavity · tool'];assert len(tools)==1;tools[0].Shape=inside
    m.doc.recompute();_arched_roof(m,'PSUUpper',297)
    board=m.rr(166,146,1.6,(0,4,8.5),2)
    board=board.cut(m.rr(50,42,2,(77,77,8.3),1))
    board=board.fuse(m.rr(30,20,1.6,(86,46,8.5),2)).removeSplitter()
    m.feature('MainPCB','NUS-CPU-04 reference mainboard study',board,'Mainboard',-2,'pcb',True)
    _qfp(m,'CPU','CPU-NUS',-38,-3,31,120,z=11.2)
    _qfp(m,'RCP','RCP-NUS',6,11,36,160,z=11.2)
    for i,y in enumerate([-25,-40]):_sop(m,'RDRAM'+str(i),'RDRAM18',6,y,23,11,32)
    for key,title,x,y,w,h,pins in [('VideoDAC','VDC-NUS',45,14,11,17,24),('VideoAmp','VIDEO AMP',62,17,8,11,14),('AudioDAC','AUDIO DAC',62,-8,9,12,16),('PIF','PIF-NUS',56,-41,16,11,28),('ClockBuffer','CLOCK',38,-14,8,6,8),('CICLogic','LOGIC',69,-58,7,7,16)]:_sop(m,key,title,x,y,w,h,pins)
    m.label('BoardRevision','NUS-CPU-04 / STUDY',2.3,(-74,70,10.13),'Mainboard',-2,'white')
    # Add the real right-angle route from each socket contact to its PCB leg.
    holes=[]
    for i,x in enumerate([-76,-43,43,76],1):
        cutouts=[]
        for j,dx in enumerate([-4.8,0,4.8]):
            xx=x+dx+1.15
            lead=_rounded_route([V(xx,-83.5,25.5),V(xx,-68,25.5),V(xx,-68,8.3)],1.8,.24)
            fuse_feature(m,'PortContact'+str(i)+'_'+str(j),lead,'Integrated controller socket PCB leg')
            holes.append(Part.makeCylinder(.5,2,V(xx,-68,8.3)))
            cutouts.append(Part.makeCylinder(.6,2,V(xx,-73.5,25.5),V(0,1,0)))
        m.cut('PortCup'+str(i),cutouts,'Three controller lead passages through the socket back')
    m.cut('MainPCB',holes,'Controller connector solder-leg holes')
    m.profile['stages']=5
    m.checkpoint(5,'cpu_rcp_rdram_and_formed_controller_leads','加入参考 NUS-CPU-04 的主板、CPU/RCP、两片 RDRAM 及音视频和接口封装，补齐手柄接口穿板引脚，并让后部电源模块保持在拱形顶盖下方。')


def _leaf_contacts(m,key,cx,cy,count,pitch,z,assembly):
    for side in [-1,1]:
        for i in range(count//2):
            x=cx+(i-(count/2-1)/2)*pitch
            a=V(x,cy+side*2.6,z);b=V(x,cy+side*1.15,z+4);c=V(x,cy+side*2.4,z+8)
            # One continuous bent spring, extruded across its strip width.
            points=[V(a.x-.35,a.y,a.z),V(b.x-.35,b.y,b.z),V(c.x-.35,c.y,c.z),V(c.x-.35,c.y+side*.18,c.z),V(b.x-.35,b.y+side*.18,b.z),V(a.x-.35,a.y+side*.18,a.z)]
            face=Part.Face(Part.makePolygon(points+[points[0]]))
            m.feature(key+str(side)+'_'+str(i),'Edge-connector leaf contact',face.extrude(V(.7,0,0)),assembly,0,'gold',True)


def stage06(m):
    # Fifty positions for the Game Pak bus, in two rows of twenty-five.
    m.box('GamePakSocket','Game Pak connector housing',83,10,13,(0,42,11.6),'CardReader',0,'black',.7,True)
    m.cut('GamePakSocket',m.rr(78,6,10,(0,42,15),.35),'Card contact spring channel')
    _leaf_contacts(m,'GamePakContact',0,42,50,2.8,15.8,'CardReader')
    m.box('GamePakMount','Cartridge connector mounting plate',106,14,.7,(0,42,11),'CardReader',-1,'metal',1.4,True)
    for x in [-48,48]:m.cut('GamePakMount',Part.makeCylinder(1.8,1,V(x,42,10.8)),'Cartridge connector fastening hole')
    guide=m.rr(125,24,10,(0,42,51),4).cut(m.rr(122.8,21.8,10.4,(0,42,50.8),3))
    m.feature('GamePakGuide','Upper cartridge guide beneath the shutters',guide,'CardReader',3,'black',True)
    # Original Jumper Pak terminates the memory bus; it contains no extra RAM.
    m.box('MemorySocket','36-position memory expansion connector',48,10,13,(0,-56,11.6),'Memory',0,'black',.65,True)
    m.cut('MemorySocket',m.rr(44,6,10,(0,-56,15),.3),'Memory connector leaf-contact channel')
    _leaf_contacts(m,'MemoryContact',0,-56,36,2.25,15.8,'Memory')
    m.box('JumperPCB','Original terminator PCB',42,1.2,24,(0,-56,22),'Memory',1,'pcb',.15,True)
    # A shallow fitted shell surrounds the exposed terminator board above its edge.
    body=m.rr(46,10,24,(0,-56,28),2).cut(m.rr(42.8,6.8,23,(0,-56,27.8),.7))
    m.feature('JumperShell','Original black Jumper Pak shell',body,'Memory',3,'black')
    m.box('JumperLid','Jumper Pak upper cap',45.5,9.5,1.2,(0,-56,52.2),'Memory',3,'black',1.8)
    for side in [-1,1]:
        for i in range(18):m.box('JumperFinger'+str(side)+'_'+str(i),'Terminator PCB edge contact',1.3,.055,8,( (i-8.5)*2.25,-56+side*.655,22.3),'Memory',1,'gold',.03,True)
    for i,x in enumerate([-13,-4.3,4.3,13]):
        m.box('JumperResistor'+str(i),'Terminator resistor network',6,1.0,4,(x,-54.82,38),'Memory',2,'black',.15,True)
    m.label('JumperTitle','JUMPER PAK',2,(-12,-55.5,53.43),'Memory',3,'n64grey')
    m.profile['stages']=6
    m.checkpoint(6,'game_pak_bus_and_original_jumper_pak','加入两排 50 位卡带连接器、36 位内存接口及原始 Jumper Pak，分别表示弹片、终端板、金手指和电阻网络，避免混用后期扩展内存模块。')


def stage07(m):
    # Low-profile electrolytics and filters leave space below the metal shield.
    positions=[(-71,39),(-60,36),(-26,29),(37,32),(56,31),(74,30),(76,11),(74,-6),(71,-22),(48,-21),(75,-38),(75,-49),(44,-60),(-55,-33),(-53,-51),(-69,-55),(-70,-9),(-67,13),(-34,-52)]
    for i,(x,y) in enumerate(positions):
        m.cyl('Electrolytic'+str(i),'Low-profile electrolytic capacitor',2.9,5.8,(x,y,10.65),'Mainboard',0,'black',internal=True)
        m.cyl('ElectrolyticTop'+str(i),'Aluminium capacitor top',2.65,.08,(x,y,16.48),'Mainboard',0,'metal',internal=True)
        for side in [-1,1]:m.box('ElectrolyticTerminal'+str(i)+'_'+str(side),'Capacitor terminal',1.0,1.2,.3,(x+side*2.2,y,10.2),'Mainboard',0,'metal',.1,True)
    for i,(x,y) in enumerate([(38,-31),(38,-49)]):
        m.box('Crystal'+str(i),'Metal clock crystal can',5.2,12,2.1,(x,y,10.8),'Mainboard',0,'metal',2.3,True)
    for bank,(x,y,n) in enumerate([(-64,23,8),(-70,-29,10),(30,-1,8),(45,3,8),(59,-26,8)]):
        for i in range(n):m.box('Filter'+str(bank)+'_'+str(i),'Discrete filter component',1.9,1.0,.7,(x+(i%4)*3.2,y+(i//4)*3,10.6),'Mainboard',0,'thermal',.13,True)
    lower=m.rr(178,146,.65,(0,3,6.7),3).cut(m.rr(50,44,1,(77,77,6.5),1))
    m.feature('LowerShield','Lower motherboard metal shield',lower,'Shield',-4,'metal',True)
    top=m.rr(178,120,.7,(0,-1,23.4),3)
    cutouts=[m.rr(95,18,1.1,(0,42,23.2),1.2),m.rr(66,24,1.1,(0,-56,23.2),1.2),m.rr(28,18,1.1,(88,49,23.2),1)]
    m.feature('MainShield','Upper shield with cartridge and memory openings',top.cut(Part.makeCompound(cutouts)),'Shield',2,'metal',True)
    # Three individual aluminium spacers sit over the processor and RAM packages.
    blocks=[('CPU',-38,-3,31,31,14.25),('RCP',6,11,36,36,14.25),('RAM',6,-32.5,29,29,13.25)]
    for key,x,y,w,h,z in blocks:
        m.box(key+'ThermalPad','Chip thermal interface',w-.6,h-.6,.10,(x,y,z-.14),'Shield',1,'thermal',.3,True)
        m.box(key+'HeatBlock','Separate aluminium chip heat block',w,h,23.05-z,(x,y,z),'Shield',1,'metal',.5,True)
        m.box(key+'TopThermal','Shield thermal interface',w-.6,h-.6,.20,(x,y,23.13),'Shield',2,'thermal',.3,True)
    spreader=m.rr(160,84,.9,(0,-2,24.35),2)
    walls=[Part.makeBox(160,.9,7,V(-80,y,25.2)) for y in [-44,39.1]]
    spreader=spreader.multiFuse(walls).removeSplitter()
    m.feature('HeatCrossbar','Bent transverse heatsink crossbar',spreader,'Shield',3,'metal',True)
    screws=[(-47,-11),(-29,-11),(-38,6),(-3,3),(15,3),(6,20),(-3,-41),(15,-41),(-3,-25),(15,-25)]
    bores=[Part.makeCylinder(.85,6,V(x,y,20)) for x,y in screws]
    for key in ['MainShield','HeatCrossbar']+[prefix+suffix for prefix in ['CPU','RCP','RAM'] for suffix in ['HeatBlock','TopThermal']]:m.cut(key,bores,'Ten heatsink fastening clearances')
    for i,(x,y) in enumerate(screws):m.screw('HeatScrew'+str(i),(x,y,25.7),'Shield',3,length=4.7,radius=1.4,axis=(0,0,-1))
    m.profile['stages']=7
    m.checkpoint(7,'layered_shields_and_three_chip_heat_blocks','补齐低矮电容与时钟件、上下屏蔽、CPU/RCP/内存三块导热金属块及折弯横梁，并加入十处独立散热紧固件和配合孔。')


def stage08(m):
    from .megadrive import _move
    _move(m,'GamePakMount',(0,0,-.15))
    # Move the PSU inward to preserve the rear corner fixing and original depth.
    for name in ['PSULowerBody','PSUUpperBody']:
        obj=m.doc.getObject(name);obj.Placement.Base.x=73;obj.Placement.Base.y=75
    for o in m.doc.Objects:
        if o.Label.startswith('Rear-right detachable power-supply bay · tool'):
            o.Shape=m.rr(63,41,53,(73,75,5),3).common(Part.makeCylinder(297.5,240,V(0,-120,-227),V(0,1,0)))
        elif o.Label=='Power-module lower cavity · tool':o.Shape=m.rr(58.2,36.2,20,(73,75,7.2),1.1)
        elif o.Label=='Power-module upper cavity · tool':o.Shape=m.rr(58.2,36.2,23.4,(73,75,26.5),1.1).common(Part.makeCylinder(295.2,240,V(0,-120,-227),V(0,1,0)))
    _move(m,'PSURelease',(-15,-2,0))
    for key in ['PowerSocket']+[k for k in m.parts if k.startswith('PowerContact')]:_move(m,key,(-15,-2,0))
    m.doc.recompute()
    m.cut('MainPCB',[m.rr(70,48,2,(73,78,8.3),1),m.rr(20,24,2,(94,46,8.3),1)],'Revised PCB outline around the fitted power module')
    m.cut('LowerShield',m.rr(64,45,1.1,(73,76,6.5),1),'Lower shield power-module bay clearance')
    m.cut('MainShield',[m.rr(28,18,1.1,(73,47,23.2),1),m.rr(65,17,1.1,(73,61.5,23.2),1)],'Fitted power connector and module clearance')
    # Compact isolated power-board representation inside the removable enclosure.
    m.box('PSUBoard','NUS-002 power-board study',53,30,1.1,(73,75,9.6),'Power',-1,'pcb',1.3,True)
    core=m.rr(22,19,19,(72,75,13),1.1).cut(m.rr(18.6,15.6,19.4,(72,75,12.8),.7))
    m.feature('PSUTransformerCore','Transformer magnetic core',core,'Power',0,'metal',True)
    bobbin=m.rr(17.6,14.6,18,(72,75,13.4),.6).cut(m.rr(16,13,18.4,(72,75,13.2),.35))
    m.feature('PSUTransformerBobbin','Transformer insulating bobbin',bobbin,'Power',0,'white',True)
    coil=m.rr(15.6,12.6,16,(72,75,14),.35).cut(m.rr(11,8,16.4,(72,75,13.8),.2))
    m.feature('PSUTransformerWinding','Transformer winding envelope',coil,'Power',0,'copper',True)
    for i,(x,y,r,h) in enumerate([(51,68,3.5,12),(52,83,3.3,10),(92,65,3,9),(92,81,3.5,12)]):
        m.cyl('PSUCap'+str(i),'Power-board capacitor',r,h,(x,y,11.1),'Power',0,'black',internal=True)
        m.cyl('PSUCapTop'+str(i),'Power capacitor top',r-.25,.08,(x,y,11.14+h),'Power',0,'metal',internal=True)
    m.box('PSUControl','Power-controller package study',7,7,2.5,(90,73,11.2),'Power',0,'black',.3,True)
    # Six original enclosure fasteners; all four corner feet have matching bores.
    points=[(-108,-73),(-108,73),(108,-73),(108,73),(0,-85),(0,85)]
    posts=[];holes=[]
    for i,(x,y) in enumerate(points):
        roof=math.sqrt(300**2-x*x)-227
        post=Part.makeCylinder(3.3,roof-4.5,V(x,y,4.2)).cut(Part.makeCylinder(.9,22,V(x,y,4.0)))
        posts.append(post);holes.extend([Part.makeCylinder(1.0,4.4,V(x,y,.2)),Part.makeCylinder(2.1,2.5,V(x,y,.2))])
        m.screw('CaseScrew'+str(i),(x,y,1.1),'Internal',-5,length=18,radius=1.8)
        if i<4:m.cut('Foot'+str(i),Part.makeCylinder(2.1,2.5,V(x,y,-.2)),'Foot fixing access')
    # Preserve the split trim faces on the cylindrical roof. Automatic face
    # refinement otherwise creates invalid p-curves around the rear bay.
    for obj in m.doc.Objects:
        if obj.Name.startswith('UpperHousingCut') and 'Refine' in obj.PropertiesList:obj.Refine=False
    m.doc.recompute()
    fuse_feature(m,'UpperHousing',Part.makeCompound(posts),'Six integrated enclosure fixing columns',refine=False)
    m.cut('LowerHousing',holes,'Six lower case screw holes and head recesses')
    board_points=[(-74,60),(-74,-60),(30,63),(73,-60),(-68,3),(73,52)]
    for i,(x,y) in enumerate(board_points):
        m.ring('BoardBoss'+str(i),'Mainboard support standoff',2.6,.85,4.1,(x,y,4.2),'Internal',-3,'n64grey',internal=True)
        m.screw('BoardScrew'+str(i),(x,y,10.8),'Internal',-1,length=3.8,radius=1.35,axis=(0,0,-1))
    m.cut('MainPCB',[Part.makeCylinder(.85,2,V(x,y,8.3)) for x,y in board_points],'Six mainboard fastening bores')
    m.cut('LowerShield',[Part.makeCylinder(2.85,1.1,V(x,y,6.5)) for x,y in board_points],'Board-standoff passages through the lower shield')
    m.profile['stages']=8
    m.checkpoint(8,'fitted_power_board_and_six_case_fixings','将可拆电源模块收进后角支柱以内，补齐模块内部变压器示意、六处机壳固定及六处主板支承，并修正卡座安装片和板件避让。')


def _controller_outline(w,h):
    anchors=[(-80,21),(-64,52),(-29,58),(-26,70),(26,70),(29,58),(64,52),(80,21),(71,-70),(55,-77),(43,-55),(33,0),(23,-6),(17,-73),(0,-88),(-17,-73),(-23,-6),(-33,0),(-43,-55),(-55,-77),(-71,-70)]
    tangent=[(0,23),(15,6),(4,2),(12,2),(12,-2),(4,-2),(15,-6),(0,-23),(-4,-8),(-9,0),(-4,15),(-7,1),(-2,-10),(-7,-9),(-10,0),(-7,9),(-2,10),(-7,-1),(-4,-15),(-9,0),(-4,8)]
    curves=[]
    for i,a in enumerate(anchors):
        j=(i+1)%len(anchors);b=anchors[j];ta=tangent[i];tb=tangent[j]
        bez=Part.BezierCurve();bez.setPoles([V(x*w/160,y*h/158,0) for x,y in [a,(a[0]+ta[0],a[1]+ta[1]),(b[0]-tb[0],b[1]-tb[1]),b]])
        curves.append(bez.toBSpline())
    return curves


def stage09(m):
    from .retro_common import loft_shell
    cy=-250
    loft_shell(m,'PadBack','Original three-prong controller rear shell',
        [(153,150,0,0,cy,1),(160,158,0,0,cy,15.6)],
        [(149,146,0,0,cy,3.1),(156,154,0,0,cy,15.8)],'Controller',-6,'padgrey',_controller_outline)
    loft_shell(m,'PadFront','Original three-prong controller front shell',
        [(160,158,0,0,cy,15.9),(158,156,0,0,cy,25),(153,150,0,0,cy,32)],
        [(156,154,0,0,cy,15.7),(154,152,0,0,cy,24.3),(149,146,0,0,cy,29.7)],'Controller',5,'padgrey',_controller_outline)
    cross=m.rr(26,8,3.2,(-48,cy+27,30.5),1.1).fuse(m.rr(8,26,3.2,(-48,cy+27,30.5),1.1)).removeSplitter()
    m.cut('PadFront',m.rr(27,9,7,(-48,cy+27,28),1.4).fuse(m.rr(9,27,7,(-48,cy+27,28),1.4)),'Controller D-pad cross aperture')
    m.feature('PadDPad','Black directional cross',cross,'Controller',6,'n64grey')
    buttons=[('Start',0,23,6.7,'red'),('A',43,5,7.1,'nblue'),('B',31,22,7.1,'ngreen'),('CUp',53,44.5,5.5,'nyellow'),('CRight',63.5,34,5.5,'nyellow'),('CDown',53,23.5,5.5,'nyellow'),('CLeft',42.5,34,5.5,'nyellow')]
    for key,x,y,r,color in buttons:
        m.cut('PadFront',Part.makeCylinder(r+.35,7,V(x,cy+y,28)),key+' button aperture')
        m.cyl('Pad'+key,key+' controller button',r,3.5,(x,cy+y,30.3),'Controller',6,color)
        if key in ['A','B']:m.label('Pad'+key+'Mark',key,3.6,(x-1.25,cy+y-1.6,33.83),'Controller',6,'padgrey')
    m.label('PadStartMark','START',1.6,(-4.3,cy+22.4,33.83),'Controller',6,'padgrey')
    m.label('PadNintendo','Nintendo',3.1,(-11.5,cy+57,32.04),'Controller',5,'n64grey')
    # Octagonal guide frame and concentric thumb cap are characteristic of NUS-005.
    points=[(15.5*math.cos(math.radians(22.5+i*45)),15.5*math.sin(math.radians(22.5+i*45))) for i in range(8)]
    face=Part.Face(Part.makePolygon([V(x,cy-15+y,0) for x,y in points+[points[0]]]))
    opening=face.extrude(V(0,0,8));opening.translate(V(0,0,28));m.cut('PadFront',opening,'Octagonal control-stick guide opening')
    frame=face.extrude(V(0,0,2));frame.translate(V(0,0,31));frame=frame.cut(Part.makeCylinder(11.6,3,V(0,cy-15,30.5)))
    m.feature('StickGuide','Octagonal original stick guide',frame,'Controller',5,'n64grey')
    m.cyl('StickShaft','Control-stick shaft',3.3,17,(0,cy-15,32.5),'Controller',6,'padgrey')
    m.cyl('StickCap','Concentric textured thumb cap',8.4,4.2,(0,cy-15,49.6),'Controller',6,'padgrey')
    rings=[Part.makeCylinder(r,.45,V(0,cy-15,53.5)).cut(Part.makeCylinder(r-.5,.7,V(0,cy-15,53.4))) for r in [6.5,4.8,3.1]]
    m.cut('StickCap',rings,'Concentric grooves on the thumb cap')
    for key,x in [('L',-53),('R',53)]:
        m.cut('PadFront',m.rr(31,9,11,(x,cy+56.5,23),3.5),key+' shoulder aperture')
        m.box('Pad'+key,'Original '+key+' shoulder key',30,8,6,(x,cy+56.5,25.2),'Controller',6,'padgrey',3.3)
    # Back-side Z trigger and accessory socket are completed in later stages.
    m.profile['stages']=9
    m.checkpoint(9,'native_three_prong_nus005_controller','建立初代 NUS-005 三叉曲线手柄上下壳，加入黑色十字键、红色 START、蓝 A 绿 B、四颗黄色 C 键、八角摇杆导向和肩键。')


def stage10(m):
    from .megadrive import _move
    from .clamshell import _replace
    # Assembly diagnostics: central columns must clear both lower wall and lids.
    points=[(-108,-73),(-108,73),(108,-73),(108,73),(0,-85),(0,85)]
    posts=[]
    for i,(x,y) in enumerate(points):
        top=math.sqrt(300**2-x*x)-227
        posts.append(Part.makeCylinder(3.3 if i<4 else 2.0,top-4.5,V(x,y,4.2)).cut(Part.makeCylinder(.9,22,V(x,y,4))))
    objects=[o for o in m.doc.Objects if o.Label=='Six integrated enclosure fixing columns'];assert len(objects)==1
    objects[0].Shape=Part.makeCompound(posts)
    for i in range(8):
        _move(m,'Filter3_'+str(i),(0,-7,0));_move(m,'Filter4_'+str(i),(0,-3,0))
    m.cut('HeatCrossbar',m.rr(95,18,10,(0,42,24),1.2),'Cartridge-socket clearance through the heatsink crossbar')
    cy=-250
    for key,x in [('L',-53),('R',53)]:
        objects=[o for o in m.doc.Objects if o.Label==key+' shoulder aperture · tool'];assert len(objects)==1
        objects[0].Shape=m.rr(31,7,7,(x,cy+54,21),3)
        _replace(m,'Pad'+key,m.rr(30,6,5.2,(x,cy+54,22),2.8))
    polygon=[(-68,12),(-68,42),(-49,52),(-24,52),(-21,60),(21,60),(24,52),(49,52),(68,42),(68,12),(25,5),(19,10),(-19,10),(-25,5)]
    face=Part.Face(Part.makePolygon([V(x,cy+y,20) for x,y in polygon+[polygon[0]]]))
    m.feature('PadPCB','Original controller phenolic PCB study',face.extrude(V(0,0,1.2)),'Controller',-2,'copper',True)
    positions=[('DUp',-48,34),('DRight',-41,27),('DDown',-48,20),('DLeft',-55,27),('Start',0,23),('A',43,5),('B',31,22),('CUp',53,44.5),('CRight',63.5,34),('CDown',53,23.5),('CLeft',42.5,34)]
    d_stems=[]
    for key,x,y in positions:
        m.cyl('PadContact'+key,'Printed carbon button contact',2.7,.05,(x,cy+y,21.25),'Controller',-1,'black',internal=True)
        rubber=Part.makeCone(4.7,2.6,4.3,V(x,cy+y,21.6)).cut(Part.makeCone(3.9,1.8,4.05,V(x,cy+y,21.55)))
        m.feature('PadRubber'+key,'Silicone button dome',rubber,'Controller',1,'white',True)
        m.cyl('PadPill'+key,'Conductive carbon pill',1.6,.15,(x,cy+y,25.35),'Controller',1,'black',internal=True)
        stem=Part.makeCylinder(1.7,4.7,V(x,cy+y,26))
        if key.startswith('D'):d_stems.append(stem)
        else:fuse_feature(m,'Pad'+key,stem,'Integrated controller button stem')
    fuse_feature(m,'PadDPad',Part.makeCompound(d_stems),'Four directional button stems')
    m.box('PadLogic','Controller logic package study',12,8,2.6,(0,cy+39,21.7),'Controller',0,'black',.4,True)
    for side in [-1,1]:
        for i in range(8):m.box('PadLogicLead'+str(side)+'_'+str(i),'Controller ASIC terminal',.35,1.2,.2,(-5+i*1.4,cy+39+side*4.65,22.2),'Controller',0,'metal',.05,True)
    for i,x in enumerate([-18,18]):
        m.cyl('PadCap'+str(i),'Controller capacitor',2.5,5,(x,cy+42,21.7),'Controller',0,'black',internal=True)
        m.cyl('PadCapTop'+str(i),'Controller capacitor metal top',2.2,.08,(x,cy+42,26.73),'Controller',0,'metal',internal=True)
    # Direction triangles are modeled solids on the four yellow C buttons.
    for key,x,y,angle in [('CUp',53,44.5,0),('CRight',63.5,34,-90),('CDown',53,23.5,180),('CLeft',42.5,34,90)]:
        face=Part.Face(Part.makePolygon([V(-1.7,-1,0),V(1.7,-1,0),V(0,1.8,0),V(-1.7,-1,0)]));shape=face.extrude(V(0,0,.025));shape.rotate(V(),V(0,0,1),angle);shape.translate(V(x,cy+y,33.84))
        m.feature('PadArrow'+key,'C-button directional marking',shape,'Controller',6,'n64grey')
    m.doc.recompute();m.parts['UpperHousing'].Shape.check(True)
    m.profile['stages']=10
    m.checkpoint(10,'controller_pcb_and_silicone_contacts','加入手柄主板、十一组硅胶和碳膜接点、按钮传动柱及黄色方向标识，同时修正主机中心支柱、离散元件和横梁配合，并收紧肩键外形。')


def _encoder_wheel():
    wheel=Part.makeCylinder(5.2,1.2).cut(Part.makeCylinder(.85,1.6,V(0,0,-.2)))
    slots=[];teeth=[]
    for i in range(16):
        slot=Part.makeBox(.55,2,1.6,V(-.275,2.6,-.2));slot.rotate(V(),V(0,0,1),i*22.5);slots.append(slot)
        tooth=Part.makeBox(.65,.6,1.2,V(-.325,5,0));tooth.rotate(V(),V(0,0,1),i*22.5);teeth.append(tooth)
    return wheel.cut(Part.makeCompound(slots)).multiFuse(teeth).removeSplitter()


def stage11(m):
    from .atari2600 import _helical_spring
    from .clamshell import _replace
    cy=-250;sy=cy-15
    # The original stick uses a spring, crossed supports and optical wheels.
    points=[(14.2*math.cos(math.radians(22.5+i*45)),14.2*math.sin(math.radians(22.5+i*45))) for i in range(8)]
    wire=Part.makePolygon([V(x,sy+y,4.1) for x,y in points+[points[0]]])
    housing=Part.Face(wire).extrude(V(0,0,24.8)).cut(Part.makeCylinder(11.5,24,V(0,sy,6)))
    m.feature('StickHousing','Octagonal optical stick module housing',housing,'Controller',0,'black',True)
    seats=Part.makeCylinder(8,2,V(0,sy,6.2)).cut(Part.makeCylinder(5,2.3,V(0,sy,6.05)))
    m.feature('StickSpringSeat','Spring lower locating seat',seats,'Controller',0,'black',True)
    spring=_helical_spring(6.5,2.3,12,.45);spring.translate(V(0,sy,9))
    m.feature('StickSpring','Original stick centering spring',spring,'Controller',1,'metal',True)
    m.ring('StickWasher','White centering washer',8.2,4.5,1,(0,sy,21.7),'Controller',2,'white',internal=True)
    xoke=Part.makeCylinder(10.2,2,V(0,sy,23)).cut(Part.makeCylinder(6.7,2.4,V(0,sy,22.8)))
    xoke=xoke.multiFuse([Part.makeCylinder(1.3,5,V(-13.8,sy,24),V(1,0,0)),Part.makeCylinder(1.3,5,V(8.8,sy,24),V(1,0,0))]).removeSplitter()
    xoke=xoke.cut(Part.makeCylinder(1.3,23,V(0,sy-11.5,25.2),V(0,1,0)))
    m.feature('StickYokeX','Outer tilt support with transverse pivots',xoke,'Controller',2,'black',True)
    m.cut('StickHousing',Part.makeCylinder(1.6,32,V(-16,sy,24),V(1,0,0)),'Outer gimbal pivot bores')
    yoke=Part.makeCylinder(6.3,2,V(0,sy,24.2)).cut(Part.makeCylinder(4.5,2.4,V(0,sy,24)))
    yoke=yoke.multiFuse([Part.makeCylinder(1,3.7,V(0,sy-9.3,25.2),V(0,1,0)),Part.makeCylinder(1,3.7,V(0,sy+5.6,25.2),V(0,1,0))]).removeSplitter()
    yoke=yoke.cut(Part.makeCylinder(1.3,14,V(-7,sy,26),V(1,0,0)))
    m.feature('StickYokeY','Inner tilt support with shaft bearings',yoke,'Controller',3,'black',True)
    lower=Part.makeCylinder(2.5,16.6,V(0,sy,16)).fuse(Part.makeSphere(3.8,V(0,sy,26))).fuse(Part.makeCylinder(1,12.8,V(-6.4,sy,26),V(1,0,0))).removeSplitter()
    fuse_feature(m,'StickShaft',lower,'Lower stick pivot and cross pin')
    supports=[m.rr(3.3,6,8,(14.15,sy,13),.3),m.rr(6,3.3,8,(0,cy-.85,13),.3)]
    fuse_feature(m,'StickHousing',Part.makeCompound(supports),'Optical wheel bearing supports')
    for i,(pos,axis) in enumerate([((16.2,sy,17),(1,0,0)),((0,cy+1.2,17),(0,1,0))]):
        wheel=_encoder_wheel();wheel.Placement=App.Placement(V(*pos),App.Rotation(V(0,0,1),V(*axis)));wheel.check(True)
        m.feature('EncoderWheel'+str(i),'Slotted optical wheel with rim teeth',wheel,'Controller',1,'black',True)
        start=V(*pos)-V(*axis)*3.4
        m.cyl('EncoderAxle'+str(i),'Optical wheel axle',.65,6.2,tuple(start),'Controller',1,'metal',axis=axis,internal=True)
        m.cut('StickHousing',Part.makeCylinder(.95,7.2,start-V(*axis)*.5,V(*axis)),'Encoder bearing running clearance')
    for side in [-1,1]:
        m.box('EncoderXSensor'+str(side),'X-axis optical emitter / receiver',1,2.2,2,(15.1 if side==-1 else 18.4,sy+4.4,16),'Controller',1,'black',.2,True)
        m.box('EncoderYSensor'+str(side),'Y-axis optical emitter / receiver',2.2,1,2,(4.4,cy+.1 if side==-1 else cy+3.5,16),'Controller',1,'black',.2,True)
    tabs=[m.rr(8,6,1.2,(x,sy,24),1) for x in [-16.5,16.5]]+[m.rr(6,12,1.2,(0,cy-32,24),1)]
    fuse_feature(m,'StickHousing',Part.makeCompound(tabs),'Three stick-module mounting tabs')
    m.cut('StickHousing',[Part.makeCylinder(.85,2,V(x,cy+y,23.8)) for x,y in [(-18,-15),(18,-15),(0,-35)]],'Three stick-module screw bores')
    for i,(x,y) in enumerate([(-18,-15),(18,-15),(0,-35)]):m.screw('StickModuleScrew'+str(i),(x,cy+y,25.7),'Controller',3,length=3.2,radius=1.2,axis=(0,0,-1))
    # Dedicated back-side Z board and rubber pad.
    back=g.rotation((0,0,-1),(0,1,0))
    m.cut('PadBack',m.rr(12,18,4.3,(0,cy+5,4),2,back),'Back-side Z-trigger opening')
    m.box('PadZ','Back-side Z trigger',10.8,16.8,2,(0,cy+5,1.5),'Controller',-6,'n64grey',1.5,orient=back)
    fuse_feature(m,'PadZ',Part.makeCylinder(1.8,4.1,V(0,cy+5,1.4)),'Z-trigger inner pushrod')
    m.box('ZPCB','Separate Z-trigger PCB',13,17,.8,(0,cy+9,8.3),'Controller',-3,'copper',.8,True)
    rubber=Part.makeCone(3.5,2.2,1.9,V(0,cy+5,8),V(0,0,-1)).cut(Part.makeCone(2.7,1.4,1.6,V(0,cy+5,8.02),V(0,0,-1)))
    m.feature('ZRubber','Z-trigger silicone contact dome',rubber,'Controller',-4,'white',True)
    m.cyl('ZContact','Z-trigger printed carbon contact',2.1,.05,(0,cy+5,8.22),'Controller',-3,'black',internal=True)
    m.cyl('ZPill','Z-trigger moving carbon pill',1.2,.12,(0,cy+5,6.48),'Controller',-4,'black',internal=True)
    m.doc.recompute()
    m.profile['stages']=11
    m.checkpoint(11,'optical_stick_spring_and_back_z_trigger','加入原生螺旋回中弹簧、双向支承、开槽光学编码轮与独立光电元件，并补齐背部 Z 键、推杆和专用小板；机构尺寸为学习近似。')


def stage12(m):
    from .atari2600 import _rounded_route
    cy=-250;rear=g.rotation((0,1,0),(0,0,1));right=g.rotation((1,0,0),(0,0,1))
    # Extend the controller PCB under A without entering the central grip opening.
    polygon=[(-68,12),(-68,42),(-49,52),(-24,52),(-21,60),(21,60),(24,52),(49,52),(68,42),(68,12),(62,-2),(40,-2),(32,5),(25,5),(19,10),(-19,10),(-25,5)]
    m.doc.getObject('PadPCB').Shape=Part.Face(Part.makePolygon([V(x,cy+y,20) for x,y in polygon+[polygon[0]]])).extrude(V(0,0,1.2))
    opening=m.rr(34.4,10.4,18,(0,cy+56,16),1.5,rear)
    for key in ['PadBack','PadFront']:m.cut(key,opening,'Controller Pak accessory-port opening')
    metal=m.rr(33.2,9.2,10,(0,cy+60,16),1.1,rear).cut(m.rr(31.6,7.6,10.2,(0,cy+60.6,16),.5,rear))
    m.feature('PadAccessoryShield','32-position accessory-port metal housing',metal,'Controller',0,'metal',True)
    m.box('PadAccessoryBack','Accessory connector insulator',31,6.8,3,(0,cy+60.8,16),'Controller',0,'black',.4,True,orient=rear)
    m.box('PadAccessoryTongue','Accessory connector contact tongue',28.8,5.6,1,(0,cy+66.7,15.5),'Controller',0,'black',.3,True)
    for side in [-1,1]:
        for i in range(16):m.box('PadAccessoryContact'+str(side)+'_'+str(i),'Controller Pak connector contact',.8,5.2,.08,((i-7.5)*1.7,cy+66.7,15.35 if side==-1 else 16.55),'Controller',0,'gold',.06,True)
    # Nine main case screws and the two smaller connector-side fixings.
    points=[(-65,24),(65,24),(-63,-49),(63,-49),(-26,50),(26,50),(-15,-42),(15,-42),(0,-75),(-21,64),(21,64)]
    columns=[];backholes=[];boardholes=[]
    for i,(x,y) in enumerate(points):
        r=2.3 if i<9 else 1.9
        columns.append(Part.makeCylinder(r,27,V(x,cy+y,4.5)).cut(Part.makeCylinder(.85,17,V(x,cy+y,4.3))))
        backholes.extend([Part.makeCylinder(1.0,15.8,V(x,cy+y,.5)),Part.makeCylinder(1.9 if i<9 else 1.6,3.2,V(x,cy+y,.5)),Part.makeCylinder(r+.3,12,V(x,cy+y,4.3))])
        boardholes.append(Part.makeCylinder(r+.35,1.6,V(x,cy+y,19.8)))
        m.screw('PadCaseScrew'+str(i),(x,cy+y,2),'Controller',-5,length=15.2,radius=1.65 if i<9 else 1.35)
    fuse_feature(m,'PadFront',Part.makeCompound(columns),'Controller case and connector fixing columns')
    m.cut('PadBack',backholes,'Controller rear fixing recesses and post clearances')
    m.cut('PadPCB',boardholes,'Controller board fixing clearances')
    # Original three-conductor JoyBus lead and strain relief.
    route=[V(0,cy+77.2,27.5),V(0,-140,27.5),V(95,-120,13),V(160,-145,13),V(163,-195,13),V(210,-195,13)]
    cable=_rounded_route(route,5,1.6);cable.check(True)
    m.feature('PadCable','Three-wire controller cable study',cable,'Controller',0,'black')
    m.ring('PadGrommet','Controller cable flex relief',2.6,1.9,11,(0,cy+66,27.5),'Controller',0,'black',axis=(0,1,0))
    for key in ['PadBack','PadFront']:m.cut(key,Part.makeCylinder(2.9,14,V(0,cy+64,27.5),V(0,1,0)),'Controller cable exit bore')
    for i,color in enumerate(['red','white','black']):
        x=(i-1)*.6;wire=_rounded_route([V(x,cy+66.1,27.5),V(x,cy+60,27.5),V(x,cy+54,27),V(x,cy+46,21.45)],1,.2)
        wire.check(True);m.feature('PadMainWire'+str(i),'JoyBus cable conductor',wire,'Controller',0,color,True)
    m.box('PadPlugBody','Original controller plug grip',27,19,20,(210.2,-195,13),'Controller',0,'padgrey',7,orient=right)
    nose=_d_socket(18.4,13.4,5.5);nose.Placement=App.Placement(V(230.4,-195,13),right)
    holes=[]
    for i,dx in enumerate([-4.8,0,4.8]):
        holes.append(Part.makeCylinder(1.15,6,V(230.2,-195+dx,11.5),V(1,0,0)))
        m.cyl('PadPlugPin'+str(i),'Controller plug contact',.95,6,(231,-195+dx,11.5),'Controller',0,'metal',axis=(1,0,0))
    m.feature('PadPlugNose','Keyed three-position controller plug nose',nose.cut(Part.makeCompound(holes)),'Controller',0,'padgrey')
    relief=Part.makeCone(2.5,4.5,11,V(199,-195,13),V(1,0,0)).cut(Part.makeCylinder(1.9,11.3,V(198.9,-195,13),V(1,0,0)))
    m.feature('PadPlugRelief','Controller plug cable relief',relief,'Controller',0,'black')
    # Vertical encoder board, six-way connector and an ordered parallel harness.
    m.box('EncoderPCB','Optical encoder circuit board study',20,14,.8,(0,cy-30.5,15),'Controller',0,'copper',1,True,orient=rear)
    m.box('EncoderHeader','Stick module six-way connector',7,1.2,4,(7,cy-31.4,18),'Controller',1,'nblue',.3,True)
    m.box('PadEncoderHeader','Main PCB six-way stick connector',10,4,3,(24,cy+15,21.6),'Controller',1,'nblue',.3,True)
    route=[V(21.5,cy+13,24.8),V(21.5,cy+6,29.3),V(10.5,cy,29.3),V(10.5,cy-32,29.3),V(4.5,cy-32,29.3),V(4.5,cy-32,22.2)]
    for i in range(6):
        wire=_rounded_route([p+V(i,0,0) for p in route],.7,.16);wire.check(True)
        m.feature('EncoderWire'+str(i),'Optical module harness conductor',wire,'Controller',1,'portgrey',True)
    m.doc.recompute()
    m.profile['stages']=12
    m.checkpoint(12,'controller_pak_port_fasteners_and_joybus_cable','补齐 32 位手柄扩展接口、九处主壳及两处接口固定、三芯线和专用插头，并加入编码小板与六芯模块线束。')


def _cartridge_outline(w,h):
    def p(x,y):return V(x*w/116,y*h/74,0)
    a,b,c,d,e,f=[p(x,y) for x,y in [(-58,-30),(-58,25),(58,25),(58,-30),(51,-37),(-51,-37)]]
    return [Part.LineSegment(a,b),Part.Arc(b,p(0,37),c),Part.LineSegment(c,d),Part.Arc(d,p(56,-35),e),Part.LineSegment(e,f),Part.Arc(f,p(-56,-35),a)]


def stage13(m):
    from .retro_common import loft_shell
    from .megadrive import _move
    from .clamshell import _replace
    cy=-250
    m.cut('StickHousing',Part.makeCylinder(1.6,46,V(-23,cy-15,24),V(1,0,0)),'Gimbal running bore continued through the mounting tabs')
    for i,dx in [(0,-.4),(1,.4)]:_move(m,'StickModuleScrew'+str(i),(dx,0,0))
    tools=[o for o in m.doc.Objects if o.Label=='Three stick-module screw bores · tool'];assert len(tools)==1
    tools[0].Shape=Part.makeCompound([Part.makeCylinder(.85,2,V(x,cy+y,23.8)) for x,y in [(-18.4,-15),(18.4,-15),(0,-35)]])
    # Keep the accessory socket's centre clear for the card edge.
    rails=[m.rr(28.8,5.6,.6,(0,cy+66.7,z),.25) for z in [14.7,16.68]]
    _replace(m,'PadAccessoryTongue',Part.makeCompound(rails));m.parts['PadAccessoryTongue'].Label='Accessory contact support rails'
    # Blank, original-profile Game Pak; front and rear native shells are editable.
    cx=235;ay=25
    loft_shell(m,'CartBack','Blank Game Pak rear shell',[(116,74,0,cx,ay,1),(116,74,0,cx,ay,8)],[(112,70,0,cx,ay,3),(112,70,0,cx,ay,8.2)],'Accessories',-4,'padgrey',_cartridge_outline)
    loft_shell(m,'CartFront','Blank Game Pak bowed-top front shell',[(116,74,0,cx,ay,8.3),(114,72,0,cx,ay,17)],[(112,70,0,cx,ay,8.1),(110,68,0,cx,ay,15)],'Accessories',5,'padgrey',_cartridge_outline)
    for key in ['CartBack','CartFront']:m.cut(key,m.rr(88,14,18,(cx,ay-33,0),1.2),'Game Pak edge-connector opening')
    m.box('CartPCB','Blank Game Pak PCB',86,50,1.2,(cx,ay-9,7),'Accessories',0,'pcb',1,True)
    for side in [-1,1]:
        for i in range(25):m.box('CartContact'+str(side)+'_'+str(i),'Game Pak edge contact',1.7,8.8,.06,(cx+(i-12)*2.8,ay-29,6.91 if side==-1 else 8.23),'Accessories',0,'gold',.1,True)
    m.box('CartROM','Unprogrammed Game Pak ROM study',29,12,3,(cx,ay-9,8.35),'Accessories',1,'black',.4,True)
    m.box('CartLowerShield','Cartridge lower metal shield',94,47,.45,(cx,ay-1,5.9),'Accessories',-1,'metal',1.5,True)
    m.box('CartUpperShield','Cartridge upper metal shield',94,47,.45,(cx,ay-1,12),'Accessories',2,'metal',1.5,True)
    m.box('CartLabel','Original N64 study label',92,45,.08,(cx,ay+5,17.04),'Accessories',5,'nblue',2.5)
    m.label('CartTitle','N64 STUDY',6.2,(cx-24,ay+12,17.15),'Accessories',5,'white')
    m.label('CartNote','BLANK GAME PAK',2.8,(cx-21,ay-5,17.15),'Accessories',5,'white')
    posts=[]
    for i,x in enumerate([cx-48,cx+48]):
        posts.append(Part.makeCylinder(2.4,11.8,V(x,ay+17,4.5)).cut(Part.makeCylinder(.85,10,V(x,ay+17,4.3))))
        m.cut('CartBack',Part.makeCylinder(1.9,3.2,V(x,ay+17,.5)),'Cartridge rear screw head access')
        m.screw('CartScrew'+str(i),(x,ay+17,2),'Accessories',-3,length=11,radius=1.6)
    fuse_feature(m,'CartFront',Part.makeCompound(posts),'Two Game Pak enclosure screw columns')
    # Optional battery-backed Controller Pak, shown as a separate study accessory.
    ay=-87
    m.native('MemPakBack','Controller Pak lower shell',56,61,5,11,(cx,ay,1),'Accessories',-4,'padgrey')
    m.cut('MemPakBack',m.rr(52,57,10,(cx,ay,3),3),'Controller Pak rear cavity')
    m.native('MemPakFront','Controller Pak upper shell',56,61,5,10,(cx,ay,12.3),'Accessories',5,'padgrey')
    m.cut('MemPakFront',m.rr(52,57,8.4,(cx,ay,12.1),3),'Controller Pak front cavity')
    for key in ['MemPakBack','MemPakFront']:m.cut(key,m.rr(30,13,24,(cx,ay-27,0),1),'Controller Pak card-edge opening')
    m.box('MemPakPCB','Controller Pak circuit board study',45,55,1,(cx,ay-3,10.5),'Accessories',0,'pcb',1,True)
    for side in [-1,1]:
        for i in range(16):m.box('MemPakContact'+str(side)+'_'+str(i),'Controller Pak edge contact',.8,9,.05,(cx+(i-7.5)*1.7,ay-25,10.42 if side==-1 else 11.53),'Accessories',0,'gold',.06,True)
    m.box('MemPakSRAM','Battery-backed SRAM package study',18,12,2.7,(cx,ay+4,11.8),'Accessories',1,'black',.35,True)
    m.cyl('MemPakBattery','Coin-cell backup battery study',10,3.2,(cx,ay+5,7),'Accessories',-1,'metal',internal=True)
    m.ring('MemPakHolder','Coin-cell locating holder',11,10.3,3.5,(cx,ay+5,6.8),'Accessories',-1,'black',internal=True)
    m.box('MemPakClip','Backup battery contact clip',23,3,.15,(cx,ay+5,10.33),'Accessories',-1,'metal',.3,True)
    m.box('MemPakLabel','Controller Pak study label',42,35,.08,(cx,ay+5,22.34),'Accessories',5,'n64grey',1.5)
    m.label('MemPakTitle','CONTROLLER PAK',2.8,(cx-20,ay+11,22.45),'Accessories',5,'white')
    m.label('MemPakNote','32 KiB / STUDY',2.4,(cx-16,ay,22.45),'Accessories',5,'white')
    posts=[];bores=[]
    for i,x in enumerate([cx-22,cx+22]):
        posts.append(Part.makeCylinder(2.3,16.7,V(x,ay+20,4.5)).cut(Part.makeCylinder(.85,13,V(x,ay+20,4.3))))
        m.cut('MemPakBack',[Part.makeCylinder(1.9,3.2,V(x,ay+20,.5)),Part.makeCylinder(2.6,8,V(x,ay+20,4.3))],'Controller Pak rear fixing passages')
        bores.append(Part.makeCylinder(2.6,1.5,V(x,ay+20,10.3)))
        m.screw('MemPakScrew'+str(i),(x,ay+20,2),'Accessories',-3,length=14,radius=1.6)
    fuse_feature(m,'MemPakFront',Part.makeCompound(posts),'Controller Pak front fixing columns')
    m.cut('MemPakPCB',bores,'Controller Pak mounting clearances')
    m.doc.recompute()
    m.profile['stages']=13
    m.checkpoint(13,'blank_game_pak_and_optional_controller_pak','加入弧顶空白卡带、双面金手指、金属屏蔽和可选 Controller Pak，补齐存储卡电池示意，并修正摇杆安装页和扩展接口的插入空间。')


def stage14(m):
    from .atari2600 import _rounded_route
    from .clamshell import _replace
    cy=-250
    # Stagger the return corners so translated horizontal wire runs cannot cross.
    for i in range(6):
        y=cy-33-i*.45
        route=[V(21.5+i,cy+13,24.8),V(21.5+i,cy+6,29.3),V(10.5+i,cy,29.3),V(10.5+i,y,29.3),V(4.5+i,y,29.3),V(4.5+i,y,22.2),V(4.5+i,cy-31.8,22.2)]
        wire=_rounded_route(route,.4,.16);wire.check(True);_replace(m,'EncoderWire'+str(i),wire)
    for key in ['CartLowerShield','CartUpperShield']:
        m.cut(key,[Part.makeCylinder(2.7,10,V(x,42,5)) for x in [187,283]],'Cartridge case-column shield clearances')
    for i,x in enumerate([195,275]):
        hole=Part.makeCylinder(.85,8,V(x,31,5.5))
        for key in ['CartLowerShield','CartUpperShield','CartPCB']:m.cut(key,hole,'Cartridge board and shield fastening hole')
        m.screw('CartBoardScrew'+str(i),(x,31,12.9),'Accessories',2,length=8.2,radius=1.2,axis=(0,0,-1))
    m.cut('MemPakPCB',[m.rr(17,13,1.4,(235+side*22,-116,10.3),.5) for side in [-1,1]],'Narrow Controller Pak PCB tongue')
    # Original fixed AC cord, displayed in a short storage pose.
    route=[V(73,98.9,19),V(73,145,19),V(0,165,14),V(-68,141,12),V(-73,110,12),V(-115,110,12)]
    cord=_rounded_route(route,5,1.55);cord.check(True)
    m.feature('ACLead','NUS-002 AC cable study',cord,'Accessories',0,'black')
    m.ring('ACGrommet','Power-module cable relief',2.7,1.8,9,(73,89.8,19),'Accessories',0,'black',axis=(0,1,0))
    m.cut('PSULower',Part.makeCylinder(3,11,V(73,89,19),V(0,1,0)),'Fixed AC cable exit')
    left=g.rotation((-1,0,0),(0,0,1))
    m.box('ACPlug','Japanese two-blade AC plug body',22,14,24,(-115.2,110,12),'Accessories',0,'black',4,orient=left)
    for i,side in enumerate([-1,1]):m.feature('ACBlade'+str(i),'Flat AC plug blade',Part.makeBox(16,1.4,6,V(-155.5,110+side*6.35-.7,9)),'Accessories',0,'metal')
    # Stereo Multi Out lead: three RCA branches and an empty connector channel.
    right=g.rotation((1,0,0),(0,0,1))
    route=[V(250,155,14),V(210,155,14),V(197,195,14),V(260,213,14),V(290,187,14)]
    lead=_rounded_route(route,4,1.5);lead.check(True)
    m.feature('VideoLead','Stereo Multi Out cable study',lead,'Accessories',0,'black')
    m.box('VideoPlugGrip','Nintendo Multi Out plug grip',28,12,20,(250.2,155,14),'Accessories',0,'black',3,orient=right)
    nose=m.rr(22,8,7,(270.4,155,14),1.3,right).cut(m.rr(20,5.5,7.3,(271.2,155,14),.6,right))
    m.feature('VideoPlugNose','Keyed Multi Out plug channel',nose,'Accessories',0,'black')
    for row in [-1,1]:
        for i in range(6):m.feature('VideoPlugContact'+str(row)+'_'+str(i),'Multi Out cable contact',Part.makeBox(6,.8,.25,V(271.3,155+(i-2.5)*2.7-.4,14+row*1.8-.125)),'Accessories',0,'gold')
    m.box('VideoSplit','Stereo audio/video cable splitter',12,10,8,(290,187,10),'Accessories',0,'black',2)
    axis=(route[-1]-route[-2]).normalize();channels=[Part.makeCylinder(1.8,19,route[-1]-axis*10,axis)]
    for i,(y,color) in enumerate([(173,'white'),(188,'nyellow'),(203,'red')]):
        start=V(296.2,184+i*3,14);middle=V(314,y,14);end=V(324,y,14)
        wire=_rounded_route([start,middle,end],1.3,.85);wire.check(True)
        m.feature('RCABranch'+str(i),'Separated stereo AV branch',wire,'Accessories',0,'black')
        direction=(middle-start).normalize();channels.append(Part.makeCylinder(1.1,9,start-direction*4,direction))
        m.cyl('RCAGrip'+str(i),'Colour-coded RCA plug grip',4,14,(324.2,y,14),'Accessories',0,color,axis=(1,0,0))
        m.ring('RCAShield'+str(i),'RCA outer contact',3.25,2.65,7,(338.4,y,14),'Accessories',0,'metal',axis=(1,0,0))
        m.cyl('RCAPin'+str(i),'RCA centre contact',1.2,8.5,(338.4,y,14),'Accessories',0,'metal',axis=(1,0,0))
    m.cut('VideoSplit',channels[0].multiFuse(channels[1:]),'Separate lead passages through the splitter')
    m.doc.recompute()
    m.profile['stages']=14
    m.checkpoint(14,'ac_and_stereo_av_connections','加入固定 AC 线及日式插头、Multi Out 转立体声三 RCA 线，修正六芯回路线避免交叉，并补齐卡带屏蔽固定和存储卡插入舌部。')


def stage15(m):
    from .clamshell import _replace
    # Retain correct trim surfaces instead of automatically merging p-curves.
    prefixes=('CartridgeDeckCut','MemoryCoverCut','StickHousingCut','StickHousingFuse','VideoSplitCut')
    for obj in m.doc.Objects:
        if obj.Name.startswith(prefixes) and 'Refine' in obj.PropertiesList:obj.Refine=False
    # Union touching glyph solids while preserving the original RDRAM18 marking.
    for key in ['RDRAM0Mark','RDRAM1Mark']:
        solids=m.parts[key].Shape.Solids
        _replace(m,key,solids[0].multiFuse(solids[1:]))
    # Keep the fixing columns entirely below the arched exterior surface.
    roof=Part.makeCylinder(299.8,240,V(0,-120,-227),V(0,1,0));columns=[]
    for i,(x,y) in enumerate([(-108,-73),(-108,73),(108,-73),(108,73),(0,-85),(0,85)]):
        top=math.sqrt(300**2-x*x)-227
        column=Part.makeCylinder(3.3 if i<4 else 2,top-4.5,V(x,y,4.2)).common(roof)
        columns.append(column.cut(Part.makeCylinder(.9,22,V(x,y,4))))
    tools=[o for o in m.doc.Objects if o.Label=='Six integrated enclosure fixing columns'];assert len(tools)==1
    tools[0].Shape=Part.makeCompound(columns)
    m.doc.recompute()
    for key,obj in m.parts.items():
        try:obj.Shape.check(True)
        except Exception as exc:raise AssertionError('Strict BOP failed for '+key+': '+str(exc)) from exc
    m.profile['stages']=15
    m.checkpoint(15,'strict_brep_and_clean_roof_finalization','保留曲面与开孔的有效分段边界，合并相接的存储器文字实体，并将四角固定柱完全修整到拱形外表面以下；全部物理组件执行严格 BRep 检查。')


STAGES={1:stage01,2:stage02,3:stage03,4:stage04,5:stage05,6:stage06,7:stage07,8:stage08,9:stage09,10:stage10,11:stage11,12:stage12,13:stage13,14:stage14,15:stage15}
