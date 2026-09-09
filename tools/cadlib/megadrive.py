"""Japanese HAA-2510 Model 1; original exterior with VA2 internal references."""
import math
import FreeCAD as App
import Part
from .core import V
from . import geometry as g
from .retro_common import loft_shell, fuse_feature, de9


def stage01(m):
    m.colors.update(mdblack=(.065,.070,.078),gloss=(.025,.029,.038),mdred=(.47,.15,.20),mdblue=(.12,.48,.73),letter=(.84,.79,.55))
    m.params.set('A3','Depth (Y)');m.params.set('A4','Height (Z)')
    loft_shell(m,'LowerHousing','Tapered Model 1 lower shell',
        [(270,202,8,0,0,1.5),(280,212,10,0,0,18)],
        [(266,198,6,0,0,3.5),(276,208,8,0,0,18.2)],layer=-6,material='mdblack')
    loft_shell(m,'UpperHousing','Sloping Model 1 upper shell',
        [(280,212,10,0,0,18.35),(274,206,10,0,0,49),(262,194,9,0,0,64)],
        [(276,208,8,0,0,18.15),(270,202,8,0,0,48),(258,190,7,0,0,61.8)],layer=5,material='mdblack')
    raised=Part.makeCylinder(90,5.9,V(34,7,63.8))
    raised=raised.makeFillet(1.1,[e for e in raised.Edges if e.BoundBox.ZMin>69.6])
    fuse_feature(m,'UpperHousing',raised,'Integrated circular raised cartridge deck')
    # A shallow annular insert is separate from the moulded upper housing.
    groove=Part.makeCylinder(88.6,.7,V(34,7,69.12)).cut(Part.makeCylinder(80.7,1,V(34,7,69)))
    m.cut('UpperHousing',groove,'Recess for the glossy deck ring')
    m.ring('DeckRing','Glossy annular cartridge-deck inlay',88.45,80.85,.42,(34,7,69.20),'Body',5,'gloss')
    for i,(x,y) in enumerate([(-114,-83),(114,-83),(-114,83),(114,83)]):
        m.box('Foot'+str(i),'Lower shell elastomer foot',13,9,1.4,(x,y,0),'Body',-6,'rubber',2)
    m.profile['stages']=1
    m.checkpoint(1,'native_tapered_model1_enclosure','建立初代大机型的原生剖面草图、渐变上下空心壳、偏右圆形卡带台、亮面环带和四个脚垫。')


def stage02(m):
    # Japanese cartridge opening, centered behind the 16-BIT field.
    slot=m.rr(126,20,15,(34,35,59),9)
    m.cut('UpperHousing',slot,'Cartridge insertion aperture')
    m.box('CartridgeFlap','Spring-return cartridge dust door',123.5,17.6,1.2,(34,35,67.9),'CardReader',5,'mdblack',7.8)
    for side in [-1,1]:
        m.cyl('FlapPivot'+str(side),'Dust-door hinge stub',.9,6.0,(34+side*59,43.0,66.4),'CardReader',5,'mdblack',axis=(1,0,0))
    # Lower left switches are deliberately outside the raised deck.
    m.cut('UpperHousing',m.rr(72,64,3.5,(-96,-61,61),3),'Recessed switch panel')
    m.box('ControlPanel','Glossy power/volume/reset inset',71.4,63.4,.6,(-96,-61,61.3),'Controls',5,'gloss',2.7)
    apertures=[m.rr(8.4,42,4,(-118,-59,60),.8),m.rr(27,12,4,(-87,-42,60),1.2),m.rr(25,11,4,(-87,-79,60),1.0)]
    m.cut('ControlPanel',apertures,'Three separate switch apertures')
    m.cut('UpperHousing',apertures,'Through-switch travel clearances')
    m.box('VolumeTrack','Headphone slider recess',7.8,41.5,.8,(-118,-59,59.6),'Controls',3,'black',.5)
    m.box('VolumeSlider','Headphone volume slider',7.4,9.0,2.3,(-118,-72,60.6),'Controls',6,'mdblack',.7)
    m.box('VolumeMark','Red slider index',6.8,.65,.08,(-118,-72,62.94),'Controls',6,'mdred',.1)
    m.box('PowerSlider','Cartridge-lock power slider',25.8,10.8,1.4,(-87,-42,60.6),'Controls',6,'mdblack',.9)
    m.box('PowerMark','Power slider red index',.75,8.6,.08,(-89,-42,62.04),'Controls',6,'mdred',.1)
    m.box('ResetButton','Blue RESET pushbutton',24.0,10.0,1.5,(-87,-79,60.6),'Controls',6,'mdblue',.8)
    for i in range(7):m.box('ResetGrip'+str(i),'Reset button moulded grip',1.0,7,.12,(-95+i*2.7,-79,62.15),'Controls',6,'mdblue',.15)
    for i in range(11):m.box('VolumeScale'+str(i),'Volume scale tick',2.5 if i%5==0 else 1.4,.28,.04,(-108,-79+i*3.8,61.94),'Controls',5,'white',.04)
    for key,text,size,pos in [('VolumeTitle','PHONES VOL',1.7,(-130,-90,61.94)),('ResetTitle','RESET',1.7,(-94,-89,61.94)),('PowerTitle','POWER',1.7,(-94,-63,61.94)),('LockTitle','CARTRIDGE LOCK',1.35,(-103,-58,61.94))]:
        m.label(key,text,size,pos,'Controls',5,'white')
    badge=m.rr(60,44,.25,(34,-37,69.73),3)
    m.feature('BitBadge','Black 16-bit badge',badge,'Body',5,'gloss')
    m.label('BitTitle','16-BIT',10.5,(12,-35,70.01),'Body',5,'letter')
    # Main badge and power lens are placed within the flat circular deck.
    m.label('SegaTitle','SEGA',4.8,(102,-91,64.03),'Body',5,'white')
    m.label('MegaDriveTitle','MEGA DRIVE',3.0,(66,-92,64.03),'Body',5,'white')
    m.cut('UpperHousing',Part.makeCylinder(1.6,4,V(34,-66,67)),'Power-indicator aperture')
    m.cyl('PowerLED','Original red power indicator',1.3,1.5,(34,-66,68.35),'Controls',5,'red')
    # Slots pass through the left upper wall; a second row vents the deck.
    slots=[Part.makeBox(38,2.2,8,V(-136,-8+i*4.0,59)) for i in range(24)]
    m.cut('UpperHousing',slots,'Original left cooling grille')
    m.profile['stages']=2
    m.checkpoint(2,'cartridge_deck_and_original_controls','加入日版卡带口和防尘门、耳机音量滑块、卡带锁联动电源、蓝色 RESET、16-BIT 标识及左侧贯穿散热槽。')


def stage03(m):
    front=g.rotation((0,-1,0),(0,0,1));rear=g.rotation((0,1,0),(0,0,1))
    for i,x in enumerate([-59,5],1):
        opening=de9(m,'PadPort'+str(i),(x,-99,29))
        m.cut('UpperHousing',opening,'Front controller '+str(i)+' aperture')
        m.label('PortNumber'+str(i),str(i),3,(x-1,-104.8,41),'Body',5,'white',rotation=front)
    m.cut('UpperHousing',de9(m,'ExtensionPort',(36,99,29),(0,1,0)),'Original rear extension-controller socket')
    for key,x,r in [('Headphones',-113,3.1),('PowerDC',83,3.5),('AV',-11,7.6)]:
        is_front=key=='Headphones';y=-100 if is_front else 98;axis=(0,-1,0) if is_front else (0,1,0)
        m.ring(key+'Barrel',key+' outer barrel',r,r-.5,6.5,(x,y,30),'Ports',0,'metal',axis=axis)
        m.ring(key+'Insulator',key+' insulated aperture',r-.65,1.0 if key=='PowerDC' else (1.9 if is_front else r-1.25),5.5,(x,y,30),'Ports',0,'black',axis=axis)
        m.cut('UpperHousing',Part.makeCylinder(r+.4,12,V(x,y-axis[1]*3,30),V(*axis)),key+' rear/front panel opening')
        if key=='PowerDC':m.cyl('PowerCenter','DC center contact',.75,4,(x,99,30),'Ports',0,'metal',axis=axis)
        if key=='AV':
            disc=Part.makeCylinder(6.1,2,V(x,98,30),V(*axis));holes=[]
            for i in range(8):
                a=math.radians(22.5+i*45);dx=3.8*math.cos(a);dz=3.8*math.sin(a);holes.append(Part.makeCylinder(.7,3,V(x+dx,97.5,30+dz),V(*axis)))
                m.ring('AVContact'+str(i),'DIN AV socket contact '+str(i+1),.55,.33,4,(x+dx,98.1,30+dz),'Ports',0,'gold',axis=axis)
            m.feature('AVInsert','Eight-contact DIN insulator',disc.cut(Part.makeCompound(holes)),'Ports',0,'black',True)
    # Removable expansion-bus cover on the right-hand lower edge.
    right=g.rotation((1,0,0),(0,0,1));opening=m.rr(102,13,8,(132,10,20),2,right)
    for key in ['LowerHousing','UpperHousing']:m.cut(key,opening,'Right expansion-bus cover opening')
    m.box('ExpansionCover','Removable side expansion cover',100.8,11.8,1.2,(138.0,10,20),'Body',0,'mdblack',1.5,orient=right)
    m.profile['stages']=3
    m.checkpoint(3,'de9_din_headphone_and_expansion_ports','加入两只前面 DE-9 手柄接口、后扩展 DE-9、八针 DIN AV、DC 输入、前耳机口及右侧扩展盖；接口触点独立建模。')


def _dip(m,key,title,x,y,w,h,pins,z=14.0):
    m.box(key,title+' DIP package',w,h,4.0,(x,y,z),'Mainboard',0,'black',.6,True)
    m.label(key+'Mark',title,min(2.2,w/(len(title)*.9)),(x-w/2+2,y-1,z+4.03),'Mainboard',0,'white')
    m.cyl(key+'Index','Package pin-one index',.8,.04,(x-w/2+2,y+h/2-2,z+4.03),'Mainboard',0,'white')
    leads=[]
    for side in [-1,1]:
        for i in range(pins//2):
            xx=x+(i-(pins/2-1)/2)*(w-4)/(pins/2-1);yy=y+side*(h/2+1.0)
            start=y+h/2+.04 if side==1 else yy-.21
            lead=Part.makeBox(.48,1.17,.28,V(xx-.24,start,z+1.2))
            leg=Part.makeBox(.48,.42,z+1.38-10.5,V(xx-.24,yy-.21,10.5))
            lead=lead.fuse(leg).removeSplitter()
            m.feature(key+'Lead'+str(side)+'_'+str(i),'DIP terminal',lead,'Mainboard',0,'metal',True)
            leads.append(Part.makeCylinder(.45,2,V(xx,yy,10.8)))
    return leads


def _qfp(m,key,title,x,y,size,pins,z=14.0):
    m.box(key,title+' QFP package',size,size,2.8,(x,y,z),'Mainboard',0,'black',.4,True)
    m.label(key+'Mark',title,2,(x-size/2+1,y-1,z+2.83),'Mainboard',0,'white')
    # Four banks remain physical objects with disconnected solid lead fingers.
    for side in range(4):
        fingers=[]
        for i in range(pins//4):
            finger=Part.makeBox(.28,2.0,.22,V((i-(pins/4-1)/2)*(size-2)/(pins/4-1)-.14,size/2+.05,z+.7))
            finger.rotate(V(),V(0,0,1),side*90);finger.translate(V(x,y,0));fingers.append(finger)
        m.feature(key+'Leads'+str(side),'QFP terminal bank '+str(side+1),Part.makeCompound(fingers),'Mainboard',0,'metal',True)


def stage04(m):
    board=m.rr(245,182,1.6,(0,0,11),5)
    # Local corner reliefs follow the VA2 board outline without reproducing traces.
    board=board.cut(m.rr(32,27,2,(-116,83,10.8),1.5))
    m.feature('MainPCB','VA2 photographic mainboard study',board,'Mainboard',-2,'pcb',True)
    holes=[]
    holes+=_dip(m,'CPU68000','MC68000',34,75,83,22,64)
    holes+=_dip(m,'SoundCPU','Z80',-82,42,49,15,40)
    holes+=_dip(m,'YM2612','YM2612',-80,8,34,14,24)
    holes+=_dip(m,'WorkRAM','WORK RAM',71,-3,31,14,28)
    holes+=_dip(m,'VideoRAM0','VRAM',69,-35,31,14,28)
    holes+=_dip(m,'VideoRAM1','VRAM',69,-60,31,14,28)
    holes+=_dip(m,'SoundRAM','SOUND RAM',-80,-25,28,13,24)
    holes+=_dip(m,'ROM','BOOT / LOGIC',-12,-44,35,14,28)
    _qfp(m,'VDP','SEGA VDP',-13,0,28,128)
    _qfp(m,'IOASIC','SEGA I/O',-24,-73,19,100)
    m.cut('MainPCB',holes,'DIP lead-through drillings')
    m.label('BoardRevision','MODEL 1 / VA2 STUDY',3,(-114,85,12.63),'Mainboard',-2,'white')
    m.profile['stages']=4
    m.checkpoint(4,'va2_mainboard_and_major_ics','依据初代外壳系列 VA2 拆机照片布置主板、68000、Z80、YM2612、VDP、I/O 与存储器；内部尺寸及未标定芯片布局为学习近似。')


def stage05(m):
    m.box('CardReaderHousing','64-contact cartridge connector',105,11,14,(34,35,13),'CardReader',0,'black',1,True)
    m.cut('CardReaderHousing',m.rr(98,5.6,12,(34,35,15.8),.3),'Cartridge PCB channel')
    for side in [-1,1]:
        for i in range(32):
            x=34+(i-15.5)*2.8
            # Folded leaf geometry with running space around the card tongue.
            points=[(35+side*2.4,26),(35+side*1.15,23),(35+side*1.5,19),(35+side*2.4,16)]
            segments=[]
            for (y1,z1),(y2,z2) in zip(points,points[1:]):
                v=V(0,y2-y1,z2-z1);wire=Part.makePolygon([V(x-.38,y1,z1),V(x+.38,y1,z1),V(x+.38,y2,z2),V(x-.38,y2,z2),V(x-.38,y1,z1)])
                face=Part.Face(wire);segments.append(face.extrude(V(0,.16*side,0)))
            leaf=segments[0].multiFuse(segments[1:]).removeSplitter()
            m.feature('CardLeaf'+str(side)+'_'+str(i),'Cartridge spring contact',leaf,'CardReader',0,'gold',True)
    # The upper guide and shutter sit above the electrical connector.
    guide=m.rr(127,23,11.8,(34,35,49),3).cut(m.rr(124,19.4,12.2,(34,35,48.8),2))
    m.feature('CardGuide','Upper cartridge guide frame',guide,'CardReader',3,'mdblack',True)
    # Discrete power/audio capacitors; values intentionally unspecified.
    positions=[(-115,-15,3.5,10),(-111,5,3.2,9),(-112,25,4,12),(-113,45,4,13),(-116,67,5,17),(-91,76,3.5,10),(-72,78,3.2,9),(-57,76,3,9),(96,76,4.5,14),(105,52,3,9),(112,28,3,9),(107,2,4,12),(112,-27,3.3,11),(110,-55,3.5,12),(93,-76,3,10),(-105,-54,3,10),(-87,-58,2.7,8),(-65,-72,3.2,10)]
    for i,(x,y,r,h) in enumerate(positions):
        m.cyl('Cap'+str(i),'Radial electrolytic capacitor',r,h,(x,y,13.3),'Mainboard',0,'black',internal=True)
        m.cyl('CapTop'+str(i),'Capacitor aluminium vent',r-.3,.1,(x,y,13.3+h+.03),'Mainboard',0,'metal',internal=True)
        for dx in [-.7,.7]:m.cyl('CapLead'+str(i)+'_'+str(dx),'Capacitor lead',.2,.55,(x+dx,y,12.65),'Mainboard',0,'metal',internal=True)
    # Small passive devices are grouped by the original audio/I/O regions.
    for bank,(xx,yy,amount) in enumerate([(-92,-43,10),(-55,4,12),(20,-70,12),(104,-5,10)]):
        for i in range(amount):
            x=xx+(i%5)*3.6;y=yy+(i//5)*4.5
            m.box('Passive'+str(bank)+'_'+str(i),'Discrete resistor / filter study',2.3,1.1,1,(x,y,13.0),'Mainboard',0,'thermal',.2,True)
    m.profile['stages']=5
    m.checkpoint(5,'cartridge_contact_leaves_and_discretes','加入 64 个折弯弹片卡带触点、上部导向框、电源与音频电容和分区离散元件；保留卡带插入空间。')


def _pad_outline(w,h):
    anchors=[(-76,0),(-55,32),(0,47),(55,32),(76,0),(58,-43),(33,-25),(0,-14),(-33,-25),(-58,-43)]
    tangents=[(0,17),(16,9),(23,0),(16,-9),(0,-19),(-13,0),(-11,11),(-16,0),(-11,-11),(-13,0)]
    curves=[]
    for i,a in enumerate(anchors):
        j=(i+1)%len(anchors);b=anchors[j];ta=tangents[i];tb=tangents[j]
        bez=Part.BezierCurve();bez.setPoles([V(x*w/152,y*h/90,0) for x,y in [a,(a[0]+ta[0],a[1]+ta[1]),(b[0]-tb[0],b[1]-tb[1]),b]])
        curves.append(bez.toBSpline())
    return curves


def stage06(m):
    # Detached original SJ-3500 controller, offset in front of the console.
    cy=-228
    loft_shell(m,'PadBack','Three-button controller lower shell',
        [(138,77,0,0,cy,1),(148,86,0,0,cy,6),(152,90,0,0,cy,14.8)],
        [(133,72,0,0,cy,3),(144,82,0,0,cy,7),(148,86,0,0,cy,15)],'Controller',-6,'mdblack',_pad_outline)
    loft_shell(m,'PadFront','Three-button controller upper shell',
        [(152,90,0,0,cy,15.1),(149,87,0,0,cy,22),(143,82,0,0,cy,27)],
        [(148,86,0,0,cy,14.9),(145,83,0,0,cy,21),(139,78,0,0,cy,24.7)],'Controller',5,'mdblack',_pad_outline)
    m.cut('PadFront',Part.makeCylinder(17.9,6,V(-43,cy+6,23)),'Floating disc D-pad aperture')
    m.cyl('PadDDisc','Floating directional disc',17.5,2.6,(-43,cy+6,25.1),'Controller',6,'gloss')
    cross=m.rr(29,9,1.6,(-43,cy+6,27.8),1).fuse(m.rr(9,29,1.6,(-43,cy+6,27.8),1)).removeSplitter()
    m.feature('PadDPad','Moulded cross on the directional disc',cross,'Controller',6,'mdblack')
    for i,(x,y) in enumerate([(23,-4),(41,4),(57,13)]):
        m.cut('PadFront',Part.makeCylinder(7.8,7,V(x,cy+y,23)),'ABC action button aperture')
        m.cyl('PadABC'+str(i),'Original '+chr(65+i)+' action button',7.4,3.2,(x,cy+y,25.3),'Controller',6,'mdblack')
        m.label('PadABCMark'+str(i),chr(65+i),4.4,(x-1.5,cy+y-1.8,28.53),'Controller',6,'mdred')
    m.cut('PadFront',m.rr(19,7.4,6,(27,cy+31,23),3.5),'START button aperture')
    m.box('PadStart','Blue START button',18.3,6.7,2.1,(27,cy+31,25.4),'Controller',6,'mdblue',3.2)
    m.label('PadSega','SEGA',5.6,(-11,cy+7,27.03),'Controller',5,'white')
    m.label('PadStartMark','START',2.0,(19,cy+36,27.03),'Controller',5,'white')
    m.profile['stages']=6
    m.checkpoint(6,'native_sj3500_three_button_controller','建立 SJ-3500 原生曲线剖面上下壳，加入浮动圆盘十字键、斜列 ABC 三键和蓝色 START；保留初代三键手柄轮廓。')


def stage07(m):
    # Working clearance for the separately represented dust-door pivot pins.
    m.cut('UpperHousing',[Part.makeCylinder(1.15,6.5,V(34+side*59-.25,43,66.4),V(1,0,0)) for side in [-1,1]],'Dust-door pivot running pockets')
    points=[(-118,-78),(110,-78),(-113,73),(115,72),(-70,85),(116,0)]
    posts=[];bores=[];lower=[]
    for i,(x,y) in enumerate(points):
        post=Part.makeCylinder(3.0,49,V(x,y,13.1)).cut(Part.makeCylinder(.9,16,V(x,y,13)))
        posts.append(post);bores.append(Part.makeCylinder(1.15,2,V(x,y,10.8)))
        lower += [Part.makeCylinder(1.0,12,V(x,y,.7)),Part.makeCylinder(2.0,1.6,V(x,y,.7))]
        m.ring('BoardSupport'+str(i),'Hollow lower board support',3.2,1.1,7.3,(x,y,3.6),'Internal',-4,'mdblack',internal=True)
        m.screw('CaseScrew'+str(i),(x,y,1.4),'Internal',-5,length=22.0,radius=1.7)
    fuse_feature(m,'UpperHousing',Part.makeCompound(posts),'Six integrated upper case screw posts')
    m.cut('MainPCB',bores,'Case-post through holes')
    m.cut('LowerHousing',lower,'Six underside counterbores and screw passages')
    # Original linear-regulator heat spreader; no fabricated circuit values.
    heat=m.rr(42,30,1.0,(-101,67,34.6),2)
    heat=heat.fuse(Part.makeBox(1,30,17,V(-122,52,17.8))).removeSplitter()
    m.feature('PowerHeatsink','Bent aluminium regulator heat spreader',heat,'Power',2,'metal',True)
    for i,y in enumerate([57,76]):
        m.box('Regulator'+str(i),'Linear regulator package',2.0,8,10,(-119.6,y,20),'Power',1,'black',.25,True)
        m.box('RegulatorTab'+str(i),'Regulator metal tab',.5,7,6,(-121.2,y,25),'Power',1,'metal',.1,True)
    # Simple motion parts occupy the upper volume above the board.
    m.box('VolumeMechanism','Headphone potentiometer slide body',6,43,8,(-118,-59,49),'Controls',3,'black',.5,True)
    m.box('VolumeStem','Slider coupling stem',2.2,4,3.2,(-118,-72,57.1),'Controls',4,'mdblack',.25,True)
    m.box('PowerMechanism','Power-switch mechanism',24,10,7,(-87,-42,49),'Controls',3,'black',.7,True)
    m.box('PowerStem','Power-switch coupling',3,4,4.4,(-89,-42,56.1),'Controls',4,'mdblack',.2,True)
    m.box('CartridgeLock','Sliding cartridge-retaining bar',105,3,2,(-31,-26,57.0),'Controls',3,'mdblack',.6,True)
    m.box('ResetSwitch','Reset switch base',10,8,4,(-87,-79,49),'Controls',3,'black',.5,True)
    m.cyl('ResetPlunger','Reset pushrod',2,7.4,(-87,-79,53.1),'Controls',4,'mdblack',internal=True)
    m.profile['stages']=7
    m.checkpoint(7,'case_fixings_regulator_and_control_mechanisms','补齐六处壳体紧固、支柱与主板通孔，加入折弯散热片、稳压器、音量滑块及电源/RESET 内部传动，并修正防尘门轴的运行间隙。')


def stage08(m):
    cy=-228
    polygon=[(-66,-16),(-66,24),(-40,33),(40,33),(66,24),(66,-16),(25,-11),(-25,-11)]
    wire=Part.makePolygon([V(x,cy+y,18.5) for x,y in polygon+[polygon[0]]])
    m.feature('PadPCB','SJ-3500 phenolic controller PCB',Part.Face(wire).extrude(V(0,0,1.2)),'Controller',-2,'copper',True)
    # Four directional contacts and independent ABC/START rubber domes.
    contacts=[(-43,14),(-35,6),(-43,-2),(-51,6),(23,-4),(41,4),(57,13),(27,31)]
    for i,(x,y) in enumerate(contacts):
        m.cyl('PadContact'+str(i),'Carbon printed contact',3.0,.05,(x,cy+y,19.76),'Controller',-1,'black',internal=True)
        cone=Part.makeCone(5.2,2.8,2.5,V(x,cy+y,20.1)).cut(Part.makeCone(4.2,1.8,2.25,V(x,cy+y,20.08)))
        m.feature('PadRubber'+str(i),'Silicone switch dome',cone,'Controller',1,'white',True)
        m.cyl('PadPill'+str(i),'Conductive carbon pill',1.6,.18,(x,cy+y,22.06),'Controller',1,'black',internal=True)
        if i>=4 and i<7:
            fuse_feature(m,'PadABC'+str(i-4),Part.makeCylinder(1.7,2.85,V(x,cy+y,22.65)),'Integrated action-button stem')
    m.box('PadLogic','Controller multiplexer package',16,7,2.7,(0,cy+18,20.2),'Controller',0,'black',.35,True)
    m.label('PadLogicMark','74HC157',1.8,(-6.5,cy+17,22.93),'Controller',0,'white')
    for side in [-1,1]:
        for i in range(8):m.box('PadLogicLead'+str(side)+'_'+str(i),'Multiplexer lead',.45,1.4,.3,(-7+i*2,cy+18+side*4.25,20.8),'Controller',0,'metal',.04,True)
    for i in range(8):m.box('PadResistor'+str(i),'Controller discrete resistor',3.2,1.5,1.1,(-17+i*4.7,cy,20.2),'Controller',0,'thermal',.15,True)
    posts=[];lowerholes=[];pcbholes=[]
    for i,(x,y) in enumerate([(-62,14),(62,14),(-48,-27),(48,-27),(-6,35),(6,35)]):
        posts.append(Part.makeCylinder(2.5,22.3,V(x,cy+y,4.5)).cut(Part.makeCylinder(.86,15,V(x,cy+y,4.4))))
        lowerholes += [Part.makeCylinder(1.05,15,V(x,cy+y,.4)),Part.makeCylinder(1.9,3.3,V(x,cy+y,.4)),Part.makeCylinder(2.75,12,V(x,cy+y,4.3))]
        pcbholes.append(Part.makeCylinder(2.85,2,V(x,cy+y,18.2)))
        m.screw('PadCaseScrew'+str(i),(x,cy+y,2.5),'Controller',-5,length=14.0,radius=1.6)
    fuse_feature(m,'PadFront',Part.makeCompound(posts),'Six moulded controller screw posts')
    m.cut('PadBack',lowerholes,'Six rear fixing passages and post pockets')
    m.cut('PadPCB',pcbholes,'Controller board post clearances')
    m.profile['stages']=8
    m.checkpoint(8,'controller_pcb_domelike_contacts_and_six_screws','补齐手柄电路板、八组碳膜触点与硅胶按键、复用器示意和六处后壳固定；内部组件可按装配分组单独查看。')


def stage09(m):
    from .atari2600 import _rounded_route
    # A brighter charcoal display colour makes moulding and cuts legible.
    m.colors['mdblack']=(.15,.16,.18)
    for o in m.parts.values():
        if o.MaterialDescription=='mdblack':g.appearance(o,m.colors['mdblack'])
    # Japanese red power field on the lower arc of the raised ring.
    sector=Part.makeCylinder(88.45,.35,V(34,7,69.23)).cut(Part.makeCylinder(80.85,.6,V(34,7,69.1)))
    sector=sector.common(Part.makeBox(60,22,1,V(4,-85,69)))
    m.cut('DeckRing',Part.makeBox(60.3,22.3,1,V(3.85,-85.15,69)),'Red POWER field break in the annular inlay')
    m.feature('RedPowerField','Japanese red power-field inlay',sector,'Body',5,'mdred')
    m.label('PowerOnLegend','POWER ON',1.8,(22,-77,69.64),'Body',5,'black')
    cable_points=[V(0,-184,15.3),V(0,-153,15.3),V(104,-135,12),V(152,-152,12),V(152,-185,12),V(177,-185,12)]
    cable=_rounded_route(cable_points,5,1.7);cable.check(True)
    m.feature('PadCable','Controller cable with circular swept bends',cable,'Controller',0,'black')
    grommet=Part.makeCylinder(2.6,13,V(0,-192,15.3),V(0,1,0)).cut(Part.makeCylinder(1.9,13.3,V(0,-192.15,15.3),V(0,1,0)))
    m.feature('PadGrommet','Hollow controller cable strain relief',grommet,'Controller',0,'black')
    for key in ['PadBack','PadFront']:m.cut(key,Part.makeCylinder(2.9,15,V(0,-193,15.3),V(0,1,0)),'Controller cable exit')
    # Nine-conductor pad wiring, spaced in parallel to keep routes independent.
    for i,color in enumerate(['red','white','blue','gold','led','mdred','metal','black','copper']):
        x=(i-4)*.5
        route=[V(x,-191.8,15.3),V(x,-196,15.3),V(x,-202,17.4),V(x,-207,17.4)]
        wire=_rounded_route(route,1.2,.16);wire.check(True)
        m.feature('PadWire'+str(i),'Controller conductor '+str(i+1),wire,'Controller',0,color,True)
    # Female plug is detached and shown at the end of the coiled study cable.
    right=g.rotation((1,0,0),(0,0,1))
    body=m.rr(34,15,18,(177.2,-185,12),3,right)
    body=body.cut(m.rr(26,11.8,9,(186.6,-185,12),1.4,right))
    m.feature('PadPlugBody','Moulded DE-9 controller plug',body,'Controller',0,'black')
    de9(m,'PadPlug',(187,-185,12),(1,0,0),'Controller',False)
    # Remove space for the two metal mounting ears from the plug nose.
    m.cut('PadPlugBody',m.rr(35,12,3,(186.8,-185,12),1,right),'Plug front metal frame clearance')
    relief=Part.makeCone(2.5,4,10,V(167,-185,12),V(1,0,0)).cut(Part.makeCylinder(1.9,10.4,V(166.8,-185,12),V(1,0,0)))
    m.feature('PadPlugRelief','Controller plug flex relief',relief,'Controller',0,'black')
    m.profile['stages']=9
    m.checkpoint(9,'controller_cable_plug_and_japanese_power_field','加入精确圆弧扫掠的手柄线、九芯内部导线、空心护套与母头插头，补齐日版红色电源环带，并调整深色外壳的显示明度。')


def stage10(m):
    # Detached blank learning cartridge, with no game data or third-party cover.
    front=g.rotation((0,-1,0),(0,0,1));cx=229;cy=12
    m.native('CartBack','Blank Mega Drive cartridge rear',110,69,4,7,(cx,cy,1),'Accessories',-4,'mdblack')
    m.cut('CartBack',m.rr(106,65,6,(cx,cy,3),2),'Cartridge rear internal pocket')
    m.native('CartFront','Blank Mega Drive cartridge face',110,69,4,7,(cx,cy,8.3),'Accessories',5,'mdblack')
    m.cut('CartFront',m.rr(106,65,5.3,(cx,cy,8.1),2),'Cartridge front internal pocket')
    for key in ['CartBack','CartFront']:m.cut(key,m.rr(95,12,16,(cx,cy-32,0),1),'Cartridge edge-connector mouth')
    m.box('CartPCB','Blank cartridge PCB',94,47,1.6,(cx,cy-12,7.0),'Accessories',0,'pcb',1,True)
    for side in [-1,1]:
        for i in range(32):m.box('CartFinger'+str(side)+'_'+str(i),'Cartridge gold edge contact',1.7,9,.06,(cx+(i-15.5)*2.8,cy-30,6.91 if side==-1 else 8.63),'Accessories',0,'gold',.12,True)
    m.box('CartROM','Unprogrammed cartridge ROM study',38,12,2.8,(cx,cy-9,8.75),'Accessories',1,'black',.4,True)
    m.box('CartLabel','Original blank study label',84,44,.08,(cx,cy+1,15.33),'Accessories',5,'mdred',2)
    m.label('CartLabelTitle','MD STUDY',6,(cx-21,cy+8,15.44),'Accessories',5,'white')
    m.label('CartLabelNote','BLANK CARTRIDGE',2.8,(cx-21,cy-7,15.44),'Accessories',5,'white')
    for i,x in enumerate([cx-47,cx+47]):
        m.cut('CartBack',Part.makeCylinder(1.9,8,V(x,cy+17,.7)),'Cartridge rear fixing opening')
        m.screw('CartScrew'+str(i),(x,cy+17,2),'Accessories',-3,length=9,radius=1.6)
    # External transformer-style adapter, represented as a study accessory.
    ax=229;ay=110
    m.native('AdapterLower','AC adapter lower enclosure',65,53,5,14,(ax,ay,0),'Accessories',-5,'black')
    m.cut('AdapterLower',m.rr(61,49,13,(ax,ay,2),3),'Adapter lower cavity')
    m.native('AdapterUpper','AC adapter upper enclosure',65,53,5,23,(ax,ay,14.25),'Accessories',5,'black')
    m.cut('AdapterUpper',m.rr(61,49,21,(ax,ay,14.05),3),'Adapter upper cavity')
    m.box('TransformerCore','Adapter transformer laminated core',38,32,20,(ax,ay,8),'Accessories',0,'metal',1,True)
    m.cut('TransformerCore',m.rr(17,19,21,(ax,ay,7.7),.7),'Transformer winding window')
    m.box('TransformerBobbin','Transformer insulation bobbin',16,18,21,(ax,ay,7.5),'Accessories',0,'white',1,True)
    m.box('AdapterLabel','Adapter data-label panel',49,35,.1,(ax,ay,37.28),'Accessories',5,'mdblack',1.5)
    m.label('AdapterMark','MD / DC 9V',3,(ax-18,ay+4,37.41),'Accessories',5,'white')
    m.label('AdapterStudyMark','STUDY MODEL',2.2,(ax-17,ay-6,37.41),'Accessories',5,'white')
    for i,x in enumerate([ax-6.35,ax+6.35]):m.box('ACBlade'+str(i),'Japanese AC plug blade',1.4,6,15,(x,ay,-15.2),'Accessories',-5,'metal',.1)
    m.profile['stages']=10
    m.checkpoint(10,'blank_cartridge_and_transformer_adapter','加入空白学习卡带、双面 64 个金手指、内部 ROM 示意，以及变压器式适配器外壳与内部结构；不包含游戏 ROM 或封面素材。')


def _set_tool(m,label,shape):
    objects=[o for o in m.doc.Objects if o.Label==label]
    assert len(objects)==1,(label,len(objects))
    objects[0].Shape=shape


def _move(m,key,delta):
    obj=m.parts[key];obj.Placement.Base+=V(*delta);obj.FlatPlacement=obj.Placement


def stage11(m):
    # Move the front-left case fixing out of the potentiometer's travel lane.
    points=[(-127,-18),(110,-78),(-113,73),(115,72),(-70,85),(116,0)]
    posts=[];bores=[];lower=[]
    for x,y in points:
        posts.append(Part.makeCylinder(3,49,V(x,y,13.1)).cut(Part.makeCylinder(.9,16,V(x,y,13))))
        bores.append(Part.makeCylinder(1.15,2,V(x,y,10.8)))
        lower += [Part.makeCylinder(1,12,V(x,y,.7)),Part.makeCylinder(2,1.6,V(x,y,.7))]
    _set_tool(m,'Six integrated upper case screw posts',Part.makeCompound(posts))
    _set_tool(m,'Case-post through holes · tool',Part.makeCompound(bores))
    _set_tool(m,'Six underside counterbores and screw passages · tool',Part.makeCompound(lower))
    for key in ['BoardSupport0','CaseScrew0']:_move(m,key,(-9,60,0))
    for key in ['Cap4','CapTop4','CapLead4_-0.7','CapLead4_0.7']:_move(m,key,(9,-6,0))
    for i in range(10):_move(m,'Passive3_'+str(i),(-9,-17,0))
    for i in range(2):
        _move(m,'RegulatorTab'+str(i),(.48,0,0));_move(m,'Regulator'+str(i),(.2,0,0))
    m.cut('PowerHeatsink',Part.makeCylinder(3.35,3,V(-113,73,34)),'Case-post clearance in regulator spreader')
    m.cut('VolumeTrack',m.rr(2.5,4.3,1.2,(-118,-72,59.4),.3),'Potentiometer slider-stem passage')
    cy=-228
    padpoints=[(-65,-3),(65,-3),(-48,-27),(48,-27),(-6,35),(6,35)]
    posts=[];lower=[];pcb=[]
    for x,y in padpoints:
        posts.append(Part.makeCylinder(2.5,22.3,V(x,cy+y,4.5)).cut(Part.makeCylinder(.86,15,V(x,cy+y,4.4))))
        lower += [Part.makeCylinder(1.05,15,V(x,cy+y,.4)),Part.makeCylinder(1.9,3.3,V(x,cy+y,.4)),Part.makeCylinder(2.75,12,V(x,cy+y,4.3))]
        pcb.append(Part.makeCylinder(2.85,2,V(x,cy+y,18.2)))
    _set_tool(m,'Six moulded controller screw posts',Part.makeCompound(posts))
    _set_tool(m,'Six rear fixing passages and post pockets · tool',Part.makeCompound(lower))
    _set_tool(m,'Controller board post clearances · tool',Part.makeCompound(pcb))
    _move(m,'PadCaseScrew0',(-3,-17,0));_move(m,'PadCaseScrew1',(3,-17,0))
    # Chamfer the board corners to the real free space inside the tapered shell.
    polygon=[(-66,-16),(-66,17),(-40,31),(14,31),(20,35),(35,35),(40,31),(66,17),(66,-16),(25,-11),(-25,-11)]
    wire=Part.makePolygon([V(x,cy+y,18.5) for x,y in polygon+[polygon[0]]])
    original=m.doc.getObject('PadPCB');assert original.TypeId=='Part::Feature'
    original.Shape=Part.Face(wire).extrude(V(0,0,1.2))
    m.doc.recompute()
    m.profile['stages']=11
    m.checkpoint(11,'verified_post_routes_and_board_edge_clearance','根据实体求交结果调整主机和手柄螺柱位置、主板小元件、散热片避让孔以及手柄板角轮廓，并为音量滑块传动杆留出独立通道。')


def stage12(m):
    from .atari2600 import _rounded_route
    # Keep all nine insulated conductors within the strain-relief bore.
    for i in range(9):_move(m,'PadWire'+str(i),((4-i)*.15,0,0))
    holes=[]
    for i in range(9):
        x=(i-4)*.35
        m.cyl('PadWireTerminal'+str(i),'Controller wire solder terminal',.18,1.3,(x,-207,17.5),'Controller',-1,'gold',internal=True)
        holes.append(Part.makeCylinder(.23,1.6,V(x,-207,18.3)))
    m.cut('PadPCB',holes,'Nine controller lead terminal bores')
    posts=[]
    for x in [182,276]:posts.append(Part.makeCylinder(2.8,5.8,V(x,29,9)).cut(Part.makeCylinder(.85,3.2,V(x,29,8.9))))
    fuse_feature(m,'CartFront',Part.makeCompound(posts),'Two integral cartridge fixing bosses')
    # Headphone and controller jack blocks support their floating metal barrels.
    for i,x in enumerate([-59,5],1):
        m.box('PadPortSupport'+str(i),'Controller socket rear support',32,10,12,(x,-91,23),'Ports',0,'black',1,True)
    # Detachable study version of the original mono DIN-to-RCA lead.
    route=[V(211,-100,10),V(190,-100,10),V(190,-65,10),V(250,-65,10),V(279,-90,10)]
    cable=_rounded_route(route,4,1.45);cable.check(True)
    m.feature('AVCable','Mono AV cable study',cable,'Accessories',0,'black')
    m.cyl('DINGrip','DIN plug moulded grip',6.5,19,(211.2,-100,10),'Accessories',0,'black',axis=(1,0,0))
    m.ring('DINShield','DIN plug metal barrel',6.0,5.5,9,(230.4,-100,10),'Accessories',0,'metal',axis=(1,0,0))
    insert=Part.makeCylinder(5.25,3,V(230.4,-100,10),V(1,0,0));bores=[]
    for i in range(8):
        a=math.radians(22.5+i*45);y=-100+3.5*math.cos(a);z=10+3.5*math.sin(a)
        bores.append(Part.makeCylinder(.55,3.4,V(230.2,y,z),V(1,0,0)))
        m.cyl('DINPin'+str(i),'DIN AV plug contact',.43,7.5,(230.5,y,z),'Accessories',0,'metal',axis=(1,0,0))
    m.feature('DINInsert','Keyed AV plug contact carrier',insert.cut(Part.makeCompound(bores)),'Accessories',0,'black')
    m.box('AVSplit','Mono AV lead split moulding',11,8,6,(282,-92,7),'Accessories',0,'black',2)
    for i,(y,color) in enumerate([(-83,'white'),(-103,'gold')]):
        branch=_rounded_route([V(287.6,-90-i*4,10),V(298,y,10),V(310,y,10)],1.5,.9)
        m.feature('AVBranch'+str(i),'Mono AV separated branch',branch,'Accessories',0,'black')
        m.cyl('RCAGrip'+str(i),'Audio/video RCA grip',4,15,(310.2,y,10),'Accessories',0,color,axis=(1,0,0))
        m.ring('RCAShield'+str(i),'RCA outer contact',3.25,2.65,7,(325.4,y,10),'Accessories',0,'metal',axis=(1,0,0))
        m.cyl('RCAPin'+str(i),'RCA centre pin',1.2,8.5,(325.4,y,10),'Accessories',0,'metal',axis=(1,0,0))
    # Short coiled DC lead; displayed lengths are storage poses, not specifications.
    powerroute=[V(229,136.7,20),V(229,160,20),V(170,168,12),V(164,126,12),V(184,106,12)]
    lead=_rounded_route(powerroute,4,1.5);lead.check(True)
    m.feature('AdapterLead','External 9 V adapter lead',lead,'Accessories',0,'black')
    direction=(powerroute[-1]-powerroute[-2]).normalize()
    m.cyl('DCPlugGrip','DC plug moulding',3.7,13,tuple(powerroute[-1]+direction*.2),'Accessories',0,'black',axis=tuple(direction))
    m.ring('DCPlugBarrel','DC coaxial plug barrel',2.75,1.1,8,tuple(powerroute[-1]+direction*13.4),'Accessories',0,'metal',axis=tuple(direction))
    m.profile['stages']=12
    m.checkpoint(12,'original_connection_accessories_and_solder_terminals','补齐手柄线束端子、卡带固定柱、原始 DIN 转双 RCA 单声道视频线与外接 DC 线，并保留插头、导体和护套的组件身份。')


def stage13(m):
    from .clamshell import _replace
    from .atari2600 import _rounded_route
    for i in range(9):
        _replace(m,'PadWireTerminal'+str(i),Part.makeCylinder(.14,1.22,V((i-4)*.35,-207,17.58)))
    points=[V(229,136.7,20),V(229,160,20),V(170,168,12),V(164,126,12),V(174,106,12)]
    _replace(m,'AdapterLead',_rounded_route(points,4,1.5))
    direction=(points[-1]-points[-2]).normalize()
    _replace(m,'DCPlugGrip',Part.makeCylinder(3.7,13,points[-1]+direction*.2,direction))
    barrel=Part.makeCylinder(2.75,8,points[-1]+direction*13.4,direction).cut(Part.makeCylinder(1.1,8.2,points[-1]+direction*13.3,direction))
    _replace(m,'DCPlugBarrel',barrel)
    # Cast-in passages in the splitter retain realistic insertion of the leads.
    end=V(279,-90,10);axis=(end-V(250,-65,10)).normalize()
    channels=[Part.makeCylinder(1.65,18,end-axis*10,axis)]
    for i,y in enumerate([-83,-103]):
        start=V(287.6,-90-i*4,10);axis=(V(298,y,10)-start).normalize()
        channels.append(Part.makeCylinder(1.1,10,start-axis*5,axis))
    m.cut('AVSplit',channels[0].multiFuse(channels[1:]),'Independent cable passages through the AV splitter')
    for key in ['PadCable','AdapterLead','AVCable','AVBranch0','AVBranch1']+['PadWire'+str(i) for i in range(9)]:m.parts[key].Shape.check(True)
    m.profile['stages']=13
    m.checkpoint(13,'final_cable_clearance_and_strict_swept_solids','依据整套求交检查收窄焊接端子、移开 DC 插头展示位置，并在 AV 分线护套中加工独立走线孔；所有线缆扫掠通过严格实体检查。')


STAGES={1:stage01,2:stage02,3:stage03,4:stage04,5:stage05,6:stage06,7:stage07,8:stage08,9:stage09,10:stage10,11:stage11,12:stage12,13:stage13}
