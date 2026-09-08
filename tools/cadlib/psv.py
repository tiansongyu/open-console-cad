"""Original PCH-1000 Wi-Fi OLED Vita: native rounded enclosure and later stages."""
from .core import V


def stage01(m):
    p=m.profile;w,h,t=p['width'],p['height'],p['base_depth']
    p['envelope_groups']=['Body']
    p['envelope_basis']='Published PCH-1000 body envelope, excluding maximum projections.'
    m.native('BackCover','Original Vita rear shell blank',w-2.4,h-2.4,34.8,1.15,(0,0,0),layer=-6)
    m.native('MainFrame','PCH-1000 structural perimeter',w,h,36.0,t-2.65,(0,0,1.2),layer=0,expr={'Width':'Parameters.Width','Height':'Parameters.Height'})
    m.cut('MainFrame',m.rr(w-3.2,h-3.2,t-2.1,(0,0,1.05),34.4),'OLED, mainboard and battery interior cavity')
    m.native('FrontFace','Glossy Vita front face blank',w-.4,h-.4,35.8,1.30,(0,0,t-1.30),layer=4)
    rim=m.rr(w-.02,h-.02,1.45,(0,0,15.65),35.99).cut(m.rr(w-.8,h-.8,1.7,(0,0,15.52),35.6))
    m.feature('SilverRim','Original OLED-model silver perimeter rim',rim,'Body',0,'metal')
    m.cut('MainFrame',rim,'Silver perimeter rim seating recess')
    m.checkpoint(1,'pch1000_native_enclosure','按 PCH-1000 Wi-Fi OLED 初代的 182 × 83.5 × 18.6 mm 主体尺寸建立圆端壳体、内部空腔、独立前后面板及银色周缘。')


STAGES={1:stage01}

import math
import Part
import FreeCAD as App
from .psp import _polygon,_ps_symbol
from .clamshell import _move,_replace


def _ellipse(w,h,z,t,x=0,y=0):
    curve=Part.Ellipse(V(0,0,z),max(w,h)/2,min(w,h)/2).toShape()
    shape=Part.Face(Part.Wire([curve])).extrude(V(0,0,t))
    if h>w:shape.rotate(V(0,0,z),V(0,0,1),90)
    shape.translate(V(x,y,0));return shape


def _field(m,side,z,t,gap=0):
    a=Part.makeCylinder(11.1+gap,t,V(side*73,16,z))
    b=Part.makeCylinder(8.8+gap,t,V(side*71.5,-8.5,z))
    neck=m.rr(7+2*gap,12+2*gap,t,(side*72.5,2,z),2)
    return a.fuse(neck).fuse(b).removeSplitter()


def stage02(m):
    w,h=m.profile['upper_display'];y=3.0;m.profile['display_y']=y
    m.cut('FrontFace',m.rr(116.3,67.3,1.9,(0,y,17.05),1.0),'OLED and touch-window opening')
    frame=m.rr(116,67,.35,(0,y,18.12),.9).cut(m.rr(w+.12,h+.12,.7,(0,y,17.98),.2))
    m.feature('DisplaySurround','OLED window surround',frame,'Display',5,'bezel')
    m.box('OLEDBackplate','OLED module backplate',114.5,65.5,.30,(0,y,12.7),'Display',1,'metal',.7,True)
    m.box('OLED','5-inch OLED module study',114,65,3.8,(0,y,13.15),'Display',2,'black',.6,True)
    m.box('FrontTouchLayer','Front capacitive touch layer',w,h,.15,(0,y,17.08),'Display',3,'screen',.2,True)
    m.box('DisplayGlass','5-inch front display window',w,h,.25,(0,y,18.35),'Display',7,'screen',.2)
    m.checkpoint(2,'oled_and_front_touch','建立 5 英寸 OLED、金属背板、前电容触控层、显示窗口及独立黑色屏框。')


def stage03(m):
    for side in [-1,1]:
        m.cut('FrontFace',_field(m,side,17.0,1.9,.15),'Figure-eight control-field recess')
        m.feature('ControlField'+str(side),'Vita directional / stick control field',_field(m,side,18.1,.45),'Body',4,'shell')
    cross=m.rr(5.6,18,1.1,(-73,16,18.25),.55).fuse(m.rr(18,5.6,1.1,(-73,16,18.25),.55)).removeSplitter()
    m.feature('DPad','Connected four-way directional key',cross,'Controls',6,'black')
    hole=m.rr(5.95,18.35,2.0,(-73,16,17.1),.65).fuse(m.rr(18.35,5.95,2.0,(-73,16,17.1),.65))
    for key in ['FrontFace','ControlField-1']:m.cut(key,hole,'Directional cross opening')
    for i,(dx,dy,angle) in enumerate([(0,5.5,0),(5.5,0,-90),(0,-5.5,180),(-5.5,0,90)]):
        x,y=-73+dx,16+dy
        sh=_polygon([(x,y+.75),(x-.65,y-.5),(x+.65,y-.5)],19.362,.018);sh.rotate(V(x,y,0),V(0,0,1),angle)
        m.feature('DPadArrow'+str(i),'Directional arrow',sh,'Controls',6,'white')
        m.cyl('DPadStem'+str(i),'D-pad plunger',1.4,3,(x,y,15.2),'Controls',3,'black',internal=True)
        for key in ['FrontFace','ControlField-1']:m.cut(key,m.parts['DPadStem'+str(i)].Shape,'Directional plunger bore')
    for dx,dy,ch in [(0,7.1,'Triangle'),(7.1,0,'Circle'),(0,-7.1,'Cross'),(-7.1,0,'Square')]:
        x,y=73+dx,16+dy;tool=Part.makeCylinder(3.72,2.3,V(x,y,17.0))
        for key in ['FrontFace','ControlField1']:m.cut(key,tool,'Action-button opening')
        cap=Part.makeCylinder(3.55,1,V(x,y,18.3));cap=cap.makeFillet(.16,[e for e in cap.Edges if e.BoundBox.ZLength<1e-6])
        m.feature('Button'+ch,ch+' action button',cap,'Controls',6,'black');_ps_symbol(m,'ButtonSymbol'+ch,ch,x,y,19.315)
        m.cyl('ButtonStem'+ch,'Action-button plunger',1.3,3,(x,y,15.25),'Controls',3,'black',internal=True)
    for side in [-1,1]:
        x,y=side*71.5,-8.5
        for key in ['FrontFace','ControlField'+str(side)]:m.cut(key,Part.makeCylinder(8.55,2.6,V(x,y,16.7)),'Analog-stick opening')
        m.ring('StickBezel'+str(side),'Analog-stick annular bezel',8.4,6.85,.55,(x,y,18.2),'Controls',5,'metal')
        m.cyl('StickStem'+str(side),'Analog-stick shaft',2.4,6.6,(x,y,15.9),'Internal',3,'black',internal=True)
        m.cyl('StickNeck'+str(side),'Stick cap support neck',3.4,.30,(x,y,22.55),'Controls',6,'black')
        cap=Part.makeCylinder(6.2,1.2,V(x,y,22.85));cap=cap.makeFillet(.25,[e for e in cap.Edges if e.BoundBox.ZLength<1e-6]);cap=cap.cut(Part.makeSphere(20,V(x,y,43.8)))
        m.feature('StickCap'+str(side),'Concave analog thumb cap',cap,'Controls',7,'rubber')
    for key,x,w,h in [('PSKey',-73,12,5.8),('SelectKey',67.2,7.3,4.3),('StartKey',77,7.3,4.3)]:
        m.cut('FrontFace',_ellipse(w+.3,h+.3,17.15,1.7,x,-27.3),'Oval system-key opening')
        m.feature(key,key,_ellipse(w,h,18.05,.75,x,-27.3),'Controls',6,'black')
    m.label('PSKeyMark','PS',2.0,(-74.5,-28.1,18.818),'Controls',6,'white')
    for key,text,x in [('SelectMark','SELECT',67.2),('StartMark','START',77)]:m.label(key,text,.95,(x-2.3,-27.8,18.818),'Controls',6,'white')
    for key,text,size,pos in [('SonyMark','SONY',2.0,(-78,31,18.582)),('VitaMark','PS VITA',3.0,(-11.5,-36,18.582))]:
        m.label(key,text,size,pos,'Body',4,'white');m.cut('FrontFace',m.parts[key].Shape,'Flush front wordmark inlay')
    m.checkpoint(3,'dual_sticks_and_vita_controls','建立双凹面摇杆、连体四向键、几何符号按键、椭圆 PS/SELECT/START 键及初代八字形操作区，前部标识采用齐平嵌入。')


def stage04(m):
    # Widen the metallic side band to match the original OLED unit's exposed rail.
    rim=m.rr(181.98,83.48,8.5,(0,0,7.4),35.99).cut(m.rr(181.2,82.7,8.8,(0,0,7.25),35.6))
    _replace(m,'SilverRim',rim)
    next(o for o in m.doc.Objects if o.Label.startswith('Silver perimeter rim seating recess · tool')).Shape=rim.copy()
    m.doc.recompute()
    top=App.Rotation(V(0,0,1),V(0,1,0));bottom=App.Rotation(V(0,0,1),V(0,-1,0))
    def cut_both(shape,label):
        for key in ['MainFrame','SilverRim']:m.cut(key,shape,label)
    for key,x,w in [('GameCardDoor',-30,37),('AccessoryDoor',11.5,38)]:
        cover=m.rr(w,7.2,.55,(x,41.2,11.4),.8,top);cut_both(cover,'Top card / accessory cover seat')
        m.feature(key,key,cover,'Ports',0,'metal')
    for key,x,r in [('PowerKey',-58,2.9),('VolumeMinusKey',39,2.7),('VolumePlusKey',53.5,2.7)]:
        hole=Part.makeCylinder(r+.18,2.2,V(x,40.1,11.4),V(0,1,0));cut_both(hole,'Top round control opening')
        m.cyl(key,key,r,.8,(x,40.95,11.4),'Controls',0,'metal',axis=(0,1,0))
    # Top engravings use the top-face orientation, with Z as the readable up axis.
    from .geometry import rotation
    q=rotation((0,1,0),(0,0,1))
    for key,text,x in [('VolumeMinusMark','-',39),('VolumePlusMark','+',53.5)]:m.label(key,text,2.0,(x+.65,41.768,10.7),'Controls',0,'shell',rotation=q)
    # Main multi-use connector: a shell, an insulating tongue and separate contacts.
    mouth=m.rr(21,6,4,(0,-42,10.2),.65,top);cut_both(mouth,'Multi-use port open mouth')
    shell=m.rr(20.5,5.5,5.2,(0,-41.7,10.2),.6,top).cut(m.rr(18.9,3.7,5.5,(0,-41.8,10.2),.35,top))
    m.feature('MultiPortShell','Proprietary Vita multi-use port shell',shell,'Ports',0,'metal')
    m.box('MultiPortTongue','Multi-use connector insulator',18,.8,3.8,(0,-40.7,10.4),'Ports',0,'black',.2,orient=top)
    for i in range(20):m.box('MultiPortContact'+str(i),'Multi-use connector contact study',.34,.06,3.0,(-7.79+i*.82,-40.5,10.85),'Ports',0,'gold',.015,orient=top)
    for side in [-1,1]:
        x=side*17;cut_both(Part.makeCylinder(1.45,3.6,V(x,-42,10.2),V(0,1,0)),'Connector-side fastener seat')
        s=Part.makeCylinder(1.3,.35).fuse(Part.makeCylinder(.60,2.5,V(0,0,.33)))
        s=s.cut(Part.makeCompound([Part.makeBox(.25,1.8,.22,V(-.125,-.9,-.02)),Part.makeBox(1.8,.25,.22,V(-.9,-.125,-.02))]))
        s.Placement=App.Placement(V(x,-41.78,10.2),top);m.feature('PortScrew'+str(side),'Multi-port flanking screw',s,'Ports',0,'metal')
    cut_both(Part.makeCylinder(2.75,6,V(31.5,-42,10.5),V(0,1,0)),'Headphone aperture')
    m.ring('HeadphoneSocket','3.5 mm audio socket',2.50,1.76,5,(31.5,-41.65,10.5),'Ports',0,'metal',axis=(0,1,0))
    m.ring('HeadphoneLip','Audio-jack black lip',2.7,2.54,.25,(31.5,-41.80,10.5),'Ports',0,'black',axis=(0,1,0))
    band=m.rr(181.98,83.48,5.5,(0,0,2.2),35.99).cut(m.rr(180.8,82.3,5.8,(0,0,2.05),35.4))
    cover=band.common(Part.makeBox(25,5,6,V(45,-42,2)));m.feature('MemoryDoor','Curved proprietary memory-card cover',cover,'Ports',0,'black');cut_both(cover,'Memory-card cover seat')
    m.checkpoint(4,'original_proprietary_interfaces','建立顶部双槽盖、电源和音量圆键、底部专用多功能接口及触点、两侧固定螺钉、耳机孔和沿壳体曲面贴合的专用存储卡盖。')


def stage05(m):
    for side in [-1,1]:
        # Small perforations sit beside the sticks, not in the lower strap eyes.
        x,y=side*83.0,-9.0
        holes=[Part.makeCylinder(.48,1.8,V(x+(col-1)*2.2,y+(row-.5)*2.6,17.05)) for col in range(3) for row in range(2)]
        m.cut('FrontFace',holes,'Six-hole stereo-speaker outlet')
        m.box('SpeakerMesh'+str(side),'Speaker acoustic mesh backing',6.8,4.4,.12,(x,y,17.18),'Internal',4,'black',.5,True)
        # Shoulder caps are trimmed to the outer silhouette and kept clear of the OLED.
        cap=m.rr(23,5.3,4.2,(side*67,35.5,14.8),1.7).common(m.rr(182,83.5,4.2,(0,0,14.8),36))
        m.feature('Shoulder'+str(side),'L/R shoulder cap',cap,'Controls',5,'metal')
        for key in ['MainFrame','FrontFace','SilverRim']:m.cut(key,cap,'Shoulder-cap recess')
        m.cyl('ShoulderPin'+str(side),'Shoulder pivot pin',.65,15,(side*67-7.5,34.8,16.0),'Internal',2,'metal',axis=(1,0,0),internal=True)
        m.cut('Shoulder'+str(side),m.parts['ShoulderPin'+str(side)].Shape,'Shoulder pivot bore')
        # Front-visible lower corner strap loops follow the curved body boundary.
        eye=m.rr(22,7.8,1.5,(side*70,-35.8,16.9),3.4).cut(m.rr(18.0,4.4,1.9,(side*70,-35.8,16.7),2.0))
        eye=eye.common(m.rr(182,83.5,2.0,(0,0,16.7),36));m.feature('StrapEye'+str(side),'Lower corner strap eye',eye,'Body',4,'metal')
        opening=m.rr(18.0,4.4,3.5,(side*70,-35.8,16.4),2.0)
        for key in ['FrontFace','MainFrame','SilverRim']:m.cut(key,[eye,opening],'Strap-eye seat and through opening')
    m.cut('FrontFace',Part.makeCylinder(2.42,1.9,V(61.5,28,17.0)),'Front VGA camera window')
    m.ring('FrontCameraRing','Front camera annular surround',2.25,1.65,.28,(61.5,28,18.24),'Optics',5,'metal')
    m.cyl('FrontCameraGlass','Front camera glass',1.58,.14,(61.5,28,18.34),'Optics',5,'screen')
    m.cut('BackCover',Part.makeCylinder(2.70,1.5,V(0,35,-.1)),'Rear VGA camera aperture')
    m.ring('RearCameraRing','Rear camera black surround',2.55,1.80,.24,(0,35,.025),'Optics',-6,'black')
    m.cyl('RearCameraGlass','Rear camera glass',1.72,.13,(0,35,.035),'Optics',-6,'screen')
    # Tiny bottom microphone inlet is offset from the larger audio jack.
    tool=m.rr(1.4,1.7,2.4,(18,-42,5.0),.25,App.Rotation(V(0,0,1),V(0,1,0)))
    for key in ['MainFrame','SilverRim']:m.cut(key,tool,'Bottom microphone inlet')
    m.box('MicrophoneMesh','Microphone inlet mesh',1.1,1.4,.12,(18,-41.74,5.0),'Ports',0,'black',.2,orient=App.Rotation(V(0,0,1),V(0,1,0)))
    m.checkpoint(5,'cameras_speakers_and_strap_eyes','加入前后独立摄像头窗口、摇杆两侧扬声器孔、L/R 肩键、角部腕带环与底部麦克风入口。')

STAGES.update({2:stage02,3:stage03,4:stage04,5:stage05})


def _tiny_symbol(m,kind,x,y,z):
    t=.009
    if kind==0:return _polygon([(x,y+.65),(x-.65,y-.48),(x+.65,y-.48)],z,t).cut(_polygon([(x,y+.38),(x-.42,y-.33),(x+.42,y-.33)],z-.01,.04))
    if kind==1:return Part.makeCylinder(.6,t,V(x,y,z)).cut(Part.makeCylinder(.44,.03,V(x,y,z-.01)))
    if kind==2:
        a=m.rr(.15,1.4,t,(x,y,z),.015);b=a.copy();a.rotate(V(x,y,z),V(0,0,1),45);b.rotate(V(x,y,z),V(0,0,1),-45);return a.fuse(b).removeSplitter()
    return m.rr(1.1,1.1,t,(x,y,z),.04).cut(m.rr(.78,.78,.03,(x,y,z-.01),.02))


def stage06(m):
    # A separate touch surface and understated symbol print identify the OLED rear.
    m.cut('BackCover',m.rr(121.3,58.3,1.6,(0,0,-.1),6.65),'Rear capacitive panel opening')
    m.box('RearTouchPanel','Rear capacitive touch surface',121,58,.23,(0,0,.02),'RearTouch',-7,'black',6.5)
    symbols=[_tiny_symbol(m,(col+row)%4,(col-15)*3.5,5+(row-5.5)*3.5,.006) for row in range(12) for col in range(31)]
    m.feature('RearTouchPattern','Simplified rear touchpad symbol print',Part.makeCompound(symbols),'RearTouch',-7,'rubber')
    reverse=App.Rotation(V(0,1,0),180)
    for key,text,size,pos in [('RearSonyMark','SONY',2.1,(5,-19,.038)),('RearModelMark','PCH-1000 Wi-Fi  /  CAD STUDY',1.3,(27,-25,.038))]:
        m.label(key,text,size,pos,'RearTouch',-7,'white',rotation=reverse);m.cut('RearTouchPanel',m.parts[key].Shape,'Rear-panel wordmark inlay')
    for side in [-1,1]:
        pad=_ellipse(22,44,0,.18,side*73,-1);m.cut('BackCover',pad,'Oval rear grip inset');m.feature('RearGrip'+str(side),'Oval rear grip pad',pad,'Body',-6,'rubber')
    m.box('RearTouchFoil','Rear capacitive electrode foil',111,52,.12,(0,0,1.3),'RearTouch',-6,'copper',4.5,True)
    m.box('RearTouchShield','Rear touchpad support sheet',120,57,.40,(0,0,1.65),'RearTouch',-5,'metal',6.0,True)
    m.box('RearTouchPCB','Rear touch controller carrier',15,5,.45,(0,-29,2.2),'RearTouch',-4,'pcb',.5,True)
    m.box('RearTouchController','Rear capacitive controller package',4.0,3.4,.7,(0,-29,2.8),'RearTouch',-4,'black',.25,True)
    m.box('RearTouchFlex','Rear touchpad ribbon',8,12,.09,(16,-24,2.1),'RearTouch',-4,'copper',.3,True)
    m.checkpoint(6,'rear_touch_and_oval_grips','建立独立后触控面板、简化几何符号印纹、椭圆握持垫、触控电极层、支承片及触控控制器。')


def stage07(m):
    m.box('BatteryPouch','SP65M battery enclosure study',94,49,4.4,(0,0,2.4),'Battery',-4,'battery',2.0,True)
    m.cut('BatteryPouch',m.rr(92.6,47.6,3.5,(0,0,2.85),1.4),'Battery-cell cavity')
    m.box('BatteryCell','Lithium-ion cell-stack study',92.3,47.3,3.15,(0,0,3.0),'Battery',-4,'rubber',1.25,True)
    tray=m.rr(96,51,.30,(0,0,2.08),2.8).cut(m.rr(93,48,.60,(0,0,1.95),1.7))
    for side in [-1,1]:tray=tray.fuse(m.rr(7,10,.30,(side*51,0,2.08),1.0))
    for side in [-1,1]:tray=tray.cut(Part.makeCylinder(1.75,.8,V(side*51,0,1.9)))
    m.feature('BatteryTray','Battery tray with two mounting ears',tray.removeSplitter(),'Battery',-5,'metal',True)
    for side in [-1,1]:
        x=side*51
        m.ring('BatteryPost'+str(side),'Battery mounting post',1.6,.76,4.75,(x,0,2.05),'Battery',-4,'black',internal=True)
        clip=m.rr(8,6,.35,(side*49,0,6.9),.6).cut(Part.makeCylinder(1.35,.7,V(x,0,6.75)))
        m.feature('BatteryClip'+str(side),'Battery retaining tab',clip,'Battery',-3,'metal',True)
        m.screw('BatteryScrew'+str(side),(x,0,7.3),'Battery',-3,length=4.0,radius=1.2,axis=(0,0,-1))
    m.box('BatteryConnector','Battery terminal carrier',10,2.7,1.5,(-39,-26.7,4.8),'Battery',-4,'white',.3,True)
    for i in range(3):m.box('BatteryContact'+str(i),'Battery terminal',.75,1.8,.08,(-41.5+i*2.5,-26.7,6.35),'Battery',-4,'gold',.02,True)
    m.box('BatteryFlex','Battery connection ribbon',5,8,.10,(-39,-27,7.1),'Battery',-3,'copper',.25,True)
    reverse=App.Rotation(V(0,1,0),180)
    for key,text,size,pos in [('BatteryType','SP65M',2.2,(12,12,2.375)),('BatteryCapacity','2210 mAh  /  3.7 V',1.9,(20,3,2.375)),('BatteryStudy','LAYOUT STUDY',1.6,(15,-10,2.375))]:m.label(key,text,size,pos,'Battery',-4,'white',rotation=reverse)
    m.checkpoint(7,'battery_and_retaining_tabs','建立 2210 mAh 电池、电芯、两处固定耳与螺钉、接点和连接排线，保持电池与前后触控结构分层。')


def stage08(m):
    board=m.rr(113,65,.8,(0,0,8.3),2.0)
    board=board.cut(m.rr(30,32,1.2,(-47,-20,8.1),1.0))
    board=board.fuse(m.rr(27,11,.8,(0,-34,8.3),1.0)).removeSplitter()
    m.feature('Mainboard','Wi-Fi model mainboard outline study',board,'Mainboard',-2,'pcb',True)
    m.cut('Mainboard',m.parts['MultiPortShell'].Shape,'Mainboard multi-use connector relief')
    packages=[('CPU',-3,12,18,18,1.2),('NAND',30,11,15,12,1.0),('PowerIC',-7,-13,13,12,1.0),('Wireless',-44,1,8,6,.7),('Audio',25,-15,5.5,6,.75),('Gyro',43,-14,4,4,.6),('Accelerometer',43,-22,3,3,.6),('FrontTouch',-28,-15,5,5,.6)]
    for key,x,y,w,h,t in packages:m.box(key+'Package',key+' package layout study',w,h,t,(x,y,9.25),'Mainboard',-2,'black',.3,True)
    m.box('MemoryStack','Processor memory-stack study',17,17,.35,(-3,12,10.6),'Mainboard',-2,'black',.3,True)
    m.label('CPUMark','CPU / RAM',1.7,(-10,11.3,10.97),'Mainboard',-2,'white')
    m.label('NANDMark','NAND',1.8,(25.5,10.3,10.27),'Mainboard',-2,'white')
    # Separate control PCBs follow the curved outer enclosure.
    for side in [-1,1]:
        shape=m.rr(177.8,79.3,.6,(0,0,11),33.9).common(m.rr(31,60,.6,(side*72.5,0,11),4.3))
        m.feature('ControlPCB'+str(side),'Left / right modular control PCB',shape,'ControlsInternal',1,'pcb',True)
    # Card holders are mechanical layout studies, with contact arrays kept distinct.
    cage=m.rr(27.4,31,2.9,(-31,26.2,9.35),.8).cut(m.rr(25.6,32,2.1,(-31,26.3,9.75),.5))
    m.feature('GameCardCage','Vita game-card socket',cage,'CardReaders',0,'metal',True)
    for i in range(20):m.box('GameCardContact'+str(i),'Game-card contact study',.50,6,.07,(-41+i*1.05,23.0,9.86),'CardReaders',0,'gold',.02,True)
    memory=m.rr(14.5,14,2.3,(54,-32,4.4),.5).cut(m.rr(12.7,15,1.5,(54,-32.1,4.8),.3))
    m.feature('MemoryCardCage','Proprietary Vita memory-card socket',memory,'CardReaders',-3,'metal',True)
    for i in range(8):m.box('MemoryCardContact'+str(i),'Proprietary memory contact study',.6,4.7,.07,(49.8+i*1.2,-31.5,4.9),'CardReaders',-3,'gold',.02,True)
    m.box('MemoryReaderPCB','Memory reader carrier board',16.2,16,.45,(54,-32,7.0),'CardReaders',-3,'pcb',.6,True)
    # Shared Wi-Fi/Bluetooth electronics only; no cellular modem, SIM or GPS board.
    for side in [-1,1]:m.box('WiFiAntenna'+str(side),'Wi-Fi antenna strip study',17,2.5,.10,(side*48,34,10.7),'Mainboard',-2,'gold',.3,True)
    points=[(-50,7),(-49,17),(-51,28),(-39,30),(-16,30),(9,30),(26,29),(43,29),(50,21),(49,10),(46,0),(32,-4),(15,-5),(6,-28),(20,-28),(31,-28),(-18,-28),(-27,-25),(-27,-8),(-18,-2)]
    for i,(x,y) in enumerate(points):
        m.box('Passive'+str(i),'Surface-mount passive',1.0,.72,.45,(x,y,9.3),'Mainboard',-2,'rubber',.02,True)
        for side in [-1,1]:m.box(f'Passive{i}End{side}','SMD solder end',.21,.78,.47,(x+side*.65,y,9.29),'Mainboard',-2,'metal',.015,True)
    m.checkpoint(8,'wifi_mainboard_and_modular_controls','建立 Wi-Fi 型主板、处理器与存储封装、传感器、独立左右按键板、专用卡座及接点阵列；不加入 3G/SIM/GPS 模块。')


def stage09(m):
    for side in [-1,1]:
        x,y=side*71.5,-8.5
        house=m.rr(15,15,3.7,(x,y,12),1.6).cut(Part.makeCylinder(2.8,4.2,V(x,y,11.8)))
        m.feature('StickHousing'+str(side),'Analog-stick mechanism housing',house,'ControlsInternal',2,'black',True)
        m.ring('StickBearing'+str(side),'Analog-stick bearing',5.8,2.75,.30,(x,y,15.85),'ControlsInternal',3,'metal',internal=True)
        m.ring('StickGimbal'+str(side),'Analog gimbal support',5.5,2.65,.5,(x,y,16.25),'ControlsInternal',3,'black',internal=True)
        m.ring('StickBoot'+str(side),'Analog-stick dust skirt',6.75,2.7,.95,(x,y,17.1),'ControlsInternal',3,'rubber',internal=True)
        for i,(dx,dy,w,h) in enumerate([(8.1,0,1.0,8),(0,8.1,8,1.0)]):m.box(f'StickSensor{side}_{i}','Analog position-sensor study',w,h,1.4,(x+dx,y+dy,14.15),'ControlsInternal',2,'rubber',.2,True)
    m.cyl('DPadCarrier','Directional key common carrier',8.4,.4,(-73,16,14.7),'ControlsInternal',3,'black',internal=True)
    positions=[(-73,21.5),(-67.5,16),(-73,10.5),(-78.5,16),(73,23.1),(80.1,16),(73,8.9),(65.9,16)]
    for i,(x,y) in enumerate(positions):
        m.cyl('KeyContact'+str(i),'Button PCB contact',1.8,.06,(x,y,11.7),'ControlsInternal',1,'gold',internal=True)
        m.cyl('KeyPill'+str(i),'Conducting contact pill',1.2,.12,(x,y,11.95),'ControlsInternal',1,'black',internal=True)
        m.cyl('KeyRubber'+str(i),'Silicone key cup',2.4,1.4,(x,y,12.2),'ControlsInternal',2,'rubber',internal=True)
        m.cyl('KeyBoss'+str(i),'Silicone transmission boss',1.1,1.05 if i<4 else 1.55,(x,y,13.65),'ControlsInternal',3,'rubber',internal=True)
    for i,x in enumerate([-73,67.2,77]):
        m.box('SystemSwitch'+str(i),'System-key switch',4,3,1.3,(x,-27.3,11.8),'ControlsInternal',2,'metal',.3,True)
        m.cyl('SystemStem'+str(i),'System-key stem',1,4.85,(x,-27.3,13.15),'ControlsInternal',3,'black',internal=True)
        m.cut('FrontFace',m.parts['SystemStem'+str(i)].Shape,'System-key transmission bore')
    for side in [-1,1]:m.box('ShoulderSwitch'+str(side),'L/R tactile switch',5,3,1.4,(side*66,32.5,12.4),'ControlsInternal',2,'metal',.3,True)
    m.box('FrontCameraPCB','Front VGA camera PCB',8,7,.5,(61.5,28,13.1),'Optics',1,'pcb',.4,True)
    m.box('FrontCameraSensor','Front camera sensor package',4,4,.6,(61.5,28,13.7),'Optics',2,'black',.3,True)
    m.ring('FrontCameraBarrel','Front camera optical barrel',2.15,1.5,3.8,(61.5,28,14.4),'Optics',3,'black',internal=True)
    m.box('RearCameraPCB','Rear VGA camera PCB',9,7,.5,(0,35,2.4),'Optics',-4,'pcb',.4,True)
    m.box('RearCameraSensor','Rear camera sensor package',4.5,4.5,.6,(0,35,1.7),'Optics',-5,'black',.3,True)
    m.ring('RearCameraBarrel','Rear camera optical barrel',2.25,1.66,1.25,(0,35,.3),'Optics',-5,'black',internal=True)
    for side in [-1,1]:
        x,y=side*83,-9
        frame=m.rr(6.8,10.8,3,(x,y,13.0),1.1).cut(m.rr(5.4,9.4,2.8,(x,y,13.35),.7))
        m.feature('SpeakerFrame'+str(side),'Stereo speaker frame',frame,'Audio',2,'metal',True)
        m.cyl('SpeakerMagnet'+str(side),'Speaker magnet',2.0,1.65,(x,y,13.45),'Audio',2,'metal',internal=True)
        m.box('SpeakerDiaphragm'+str(side),'Speaker diaphragm',5,8.5,.10,(x,y,16.1),'Audio',3,'black',.6,True)
        for j,dx in enumerate([-1.5,1.5]):
            m.cyl(f'SpeakerPad{side}_{j}','Speaker PCB contact pad',.55,.05,(x+dx,-15.1,11.65),'Audio',1,'gold',internal=True)
            m.cyl(f'SpeakerSpring{side}_{j}','Speaker pressure contact study',.35,1.0,(x+dx,-15.1,11.8),'Audio',2,'gold',internal=True)
            m.box(f'SpeakerLeaf{side}_{j}','Speaker spring contact leaf',.8,1.3,.08,(x+dx,-15.1,12.88),'Audio',2,'gold',.1,True)
    m.box('MicrophonePCB','Bottom microphone carrier',5.0,4.2,.45,(18,-36.9,3.3),'Audio',-3,'pcb',.4,True)
    m.box('MicrophoneCapsule','Microphone capsule',3.2,3.2,2,(18,-36.9,4),'Audio',-3,'metal',.4,True)
    m.ring('MicrophoneDuct','Microphone acoustic duct',1.0,.55,2.0,(18,-40.5,5),'Audio',-3,'black',axis=(0,1,0),internal=True)
    m.checkpoint(9,'analog_mechanisms_cameras_and_audio','补齐双摇杆机构、胶垫与接点、系统键传动、两套摄像头 PCB/镜筒、压力接点式扬声器和麦克风组件。')


def stage10(m):
    mounts=[(-29,-28),(-53,30),(53,30),(36,-28),(-6,28.8)]
    for i,(x,y) in enumerate(mounts):
        m.ring('BoardPost'+str(i),'Mainboard mounting post',1.6,.76,6.7,(x,y,1.3),'Internal',-3,'black',internal=True)
        m.cut('Mainboard',Part.makeCylinder(.78,1.3,V(x,y,8.1)),'Mainboard mounting hole')
        m.cut('RearTouchShield',Part.makeCylinder(1.8,.8,V(x,y,1.5)),'Support-sheet post clearance')
        m.screw('BoardScrew'+str(i),(x,y,10.0),'Mainboard',-2,length=4.0,radius=1.2,axis=(0,0,-1))
    for side in [-1,1]:
        for i,(xx,y) in enumerate([(62,24),(84,10),(82,-21)]):
            x=side*xx
            m.ring(f'ControlPost{side}_{i}','Controller PCB locating post',1.45,.74,9.4,(x,y,1.3),'Internal',-3,'black',internal=True)
            m.cut('ControlPCB'+str(side),Part.makeCylinder(.77,1.0,V(x,y,10.8)),'Controller-board mounting hole')
            m.screw(f'ControlScrew{side}_{i}',(x,y,12.5),'ControlsInternal',1,length=3.8,radius=1.1,axis=(0,0,-1))
    rear=[(-85,23),(85,23),(-85,-24),(85,-24)]
    for i,(x,y) in enumerate(rear):
        m.cut('BackCover',[Part.makeCylinder(.73,2,V(x,y,-.1)),Part.makeCylinder(1.32,.45,V(x,y,-.03))],'Rear service screw seat')
        m.screw('RearScrew'+str(i),(x,y,.05),'Body',-6,length=3.1,radius=1.15)
    for i,x in enumerate([-2,25]):
        m.screw('AccessoryCoverScrew'+str(i),(x,35.0,13.0),'Internal',1,length=3.5,radius=1.1,axis=(0,0,-1))
    # Shields and ribbons represent separate modules, rather than a single solid fill.
    shield=m.rr(28,26,.25,(-3,12,11.25),1.4)
    m.feature('ProcessorShield','Processor EMI shield sheet',shield,'Mainboard',-1,'metal',True)
    m.box('PowerShield','Power-management shielding sheet',20,20,.25,(-7,-13,10.75),'Mainboard',-1,'metal',1.0,True)
    carrier=m.rr(117,68,.35,(0,3,12.15),1.0).cut(m.rr(108,59,.65,(0,3,12.0),.7))
    m.feature('OLEDCarrier','OLED locating carrier rim',carrier,'Internal',1,'metal',True)
    for key,w,h,pos in [('OLEDMainFlex',23,9,(4,-27,11.7)),('FrontTouchFlex',5,11,(-25,-26,11.6)),('ControlFlexLeft',12,5,(-55,0,10.25)),('ControlFlexRight',12,5,(55,-1,10.25)),('RearCameraFlex',6,10,(-8,30,3.05))]:m.box(key,key,w,h,.09,pos,'Flex',0,'copper',.25,True)
    for key,w,h,pos in [('OLEDConnector',25,2.5,(4,-30,9.6)),('FrontTouchConnector',7,2.8,(-25,-31,9.6)),('ControlConnectorLeft',3,8,(-53.5,0,9.6)),('ControlConnectorRight',3,8,(53.5,-1,9.6))]:m.box(key,key,w,h,.8,pos,'Mainboard',-2,'white',.25,True)
    m.box('AccessoryPortShell','Original top accessory socket',22,5.0,5.5,(11.5,36.0,11.0),'Ports',0,'metal',.6,True,orient=App.Rotation(V(0,0,1),V(0,1,0)))
    m.cut('AccessoryPortShell',m.rr(19.7,3.0,5.8,(11.5,35.9,11),.35,App.Rotation(V(0,0,1),V(0,1,0))),'Accessory socket opening')
    m.checkpoint(10,'fasteners_shields_and_flex','增加主板与左右按键板安装件、后部维修螺钉、处理器/电源屏蔽片、OLED 承托边、显示与控制排线及顶部附件接口。')

STAGES.update({6:stage06,7:stage07,8:stage08,9:stage09,10:stage10})


def stage11(m):
    # Expose the lower strap openings through the case and seat their rims flush.
    tools=[o for o in m.doc.Objects if o.Label.startswith('Strap-eye seat and through opening · tool')]
    for j,side in enumerate([-1,1]):
        eye=m.rr(22,7.8,1.7,(side*70,-35.8,16.9),3.4).cut(m.rr(18,4.4,2.1,(side*70,-35.8,16.7),2.0))
        eye=eye.common(m.rr(182,83.5,2.0,(0,0,16.7),36));_replace(m,'StrapEye'+str(side),eye)
        opening=m.rr(18,4.4,20,(side*70,-35.8,-.1),2.0)
        for tool in tools[j*3:j*3+3]:tool.Shape=Part.makeCompound([eye,opening])
        m.cut('BackCover',opening,'Strap-eye rear through-opening')
    # Front lens trim is compact; the rear unit has the characteristic oval bezel.
    _replace(m,'FrontCameraRing',Part.makeCylinder(1.85,.28,V(61.5,28,18.24)).cut(Part.makeCylinder(1.37,.5,V(61.5,28,18.1))))
    _replace(m,'FrontCameraGlass',Part.makeCylinder(1.3,.14,V(61.5,28,18.34)))
    _replace(m,'FrontCameraBarrel',Part.makeCylinder(1.75,3.8,V(61.5,28,14.4)).cut(Part.makeCylinder(1.2,4,V(61.5,28,14.3))))
    next(o for o in m.doc.Objects if o.Label.startswith('Front VGA camera window · tool')).Shape=Part.makeCylinder(2.03,1.9,V(61.5,28,17))
    rear=_ellipse(11.5,6.8,.025,.24,0,35).cut(Part.makeCylinder(1.8,.5,V(0,35,-.05)))
    _replace(m,'RearCameraRing',rear)
    next(o for o in m.doc.Objects if o.Label.startswith('Rear VGA camera aperture · tool')).Shape=_ellipse(11.8,7.1,-.1,1.5,0,35)
    top=App.Rotation(V(0,0,1),V(0,1,0))
    for key in ['MainFrame','SilverRim']:
        m.cut(key,m.rr(28,3.4,4.6,(-31,38.0,10.8),.6,top),'Open game-card passage behind cover')
        m.cut(key,m.rr(22.4,5.4,8,(11.5,34.5,11),.7,top),'Open accessory socket behind cover')
    m.cut('GameCardCage',m.parts['GameCardDoor'].Shape,'Game-card cover seating rebate')
    m.cut('AccessoryPortShell',m.parts['AccessoryDoor'].Shape,'Accessory-port cover rebate')
    from .geometry import rotation
    q=rotation((0,1,0),(0,0,1))
    m.label('GameDoorMark','PS VITA',2.3,(-22,41.732,10.5),'Ports',0,'shell',rotation=q);m.cut('GameCardDoor',m.parts['GameDoorMark'].Shape,'Top game-card label inlay')
    # Blank proprietary media, modeled independently of their internal readers.
    x=126
    card=m.rr(22.5,30.5,1.9,(x,15,0),1.0).cut(Part.makeBox(2.8,3.5,2.4,V(x+9.5,27.5,-.2)))
    m.feature('VitaGameCard','Blank proprietary Vita game card',card,'Accessories',0,'black')
    for i in range(20):
        pad=m.rr(.65,4.5,.025,(x+(i-9.5)*.94,25.2,1.875),.04)
        m.feature('VitaGamePad'+str(i),'Game-card terminal study',pad,'Accessories',0,'gold');m.cut('VitaGameCard',pad,'Game-card terminal inlay')
    m.label('VitaGameMark','VITA',2.4,(x-4.0,10,1.882),'Accessories',0,'white');m.cut('VitaGameCard',m.parts['VitaGameMark'].Shape,'Blank game-card wordmark')
    m.box('VitaMemoryCard','Proprietary Vita memory-card study',12.5,15,1.6,(x,-30,0),'Accessories',0,'black',.7)
    for i in range(8):
        pad=m.rr(.75,3,.025,(x+(i-3.5)*1.25,-25.5,1.575),.04)
        m.feature('VitaMemoryPad'+str(i),'Memory-card terminal study',pad,'Accessories',0,'gold');m.cut('VitaMemoryCard',pad,'Memory-card terminal inlay')
    m.label('VitaMemoryMark','MEM',1.5,(x-2.8,-32,1.582),'Accessories',0,'white');m.cut('VitaMemoryCard',m.parts['VitaMemoryMark'].Shape,'Blank memory-card wordmark')
    m.profile['internal_exclude']=['FrontFace','ControlField-1','ControlField1','DisplaySurround','OLEDBackplate','OLED','FrontTouchLayer','DisplayGlass','SonyMark','VitaMark']
    m.profile['internal_normal']=[.15,-.3,2.5]
    m.doc.recompute()
    m.checkpoint(11,'interface_visibility_and_media','完善腕带环贯通开口、前后镜头外观及卡槽盖后的真实通道，加入空白专用游戏卡和存储卡，准备装配配合检查。')

STAGES[11]=stage11


def stage12(m):
    # Keep shoulder caps out of the OLED and its surround, and preserve wordmarks.
    block=Part.makeBox(117,100,8,V(-58.5,-50,13))
    seats=[o for o in m.doc.Objects if o.Label.startswith('Shoulder-cap recess · tool')]
    for j,side in enumerate([-1,1]):
        o=m.parts['Shoulder'+str(side)];cap=o.Base.Shape.cut(block);o.Base.Shape=cap
        for tool in seats[j*3:j*3+3]:tool.Shape=cap.copy()
    _move(m,'SonyMark',(0,-.3,0))
    next(o for o in m.doc.Objects if o.Label.startswith('Flush front wordmark inlay · tool')).Shape=m.parts['SonyMark'].Shape.copy()
    # Accessory-cover screws enter from the top edge, not through the OLED plate.
    into=App.Rotation(V(0,0,1),V(0,-1,0))
    for i,x in enumerate([-2,25]):
        shape=Part.makeCylinder(1.1,.35).fuse(Part.makeCylinder(.62,3.5,V(0,0,.33)))
        shape=shape.cut(Part.makeCompound([Part.makeBox(.25,1.6,.22,V(-.125,-.8,-.02)),Part.makeBox(1.6,.25,.22,V(-.8,-.125,-.02))]))
        shape.Placement=App.Placement(V(x,41.0,11.2),into);_replace(m,'AccessoryCoverScrew'+str(i),shape)
        bores=[Part.makeCylinder(1.25,1.8,V(x,39.5,11.2),V(0,1,0)),Part.makeCylinder(.77,4.6,V(x,36.8,11.2),V(0,1,0))]
        for key in ['MainFrame','SilverRim']:m.cut(key,bores,'Top accessory-cover fastener pocket')
    # A bent rear touch ribbon passes below the shield, then rises beyond its edge.
    flex=m.rr(8,12,.09,(16,-24,1.48),.2).fuse(m.rr(8,.10,.68,(16,-29.92,1.48),.02)).fuse(m.rr(21,2,.09,(10.5,-29,2.07),.2)).removeSplitter()
    _replace(m,'RearTouchFlex',flex)
    pcb=m.parts['MemoryReaderPCB'].Shape.common(m.rr(177.8,79.3,.45,(0,0,7),33.9));_replace(m,'MemoryReaderPCB',pcb)
    _replace(m,'WiFiAntenna-1',m.rr(12,2.5,.10,(-60,29,10.7),.3))
    for key in ['Passive3','Passive3End-1','Passive3End1']:_move(m,key,(0,-21,0))
    # Mirror the right sensor inward, clear of the pressure-contact speaker.
    _move(m,'StickSensor1_0',(-16.2,0,0))
    for side in [-1,1]:
        _move(m,'ShoulderSwitch'+str(side),(side*3,0,0))
        base=m.parts['ControlPCB'+str(side)]
        while base.TypeId=='Part::Cut':base=base.Base
        tab=m.rr(8,7,.6,(side*69,30.5,11),.8).common(m.rr(177.8,79.3,.6,(0,0,11),33.9))
        base.Shape=base.Shape.fuse(tab).removeSplitter()
    for key in ['MainFrame','SilverRim']:m.cut(key,Part.makeCylinder(1.15,3.7,V(18,-41.9,5),V(0,1,0)),'Microphone duct clearance')
    # Move one mainboard post clear of the rear-camera flex and update both bores.
    for key in ['BoardPost4','BoardScrew4']:_move(m,key,(12.5,0,0))
    boardholes=[o for o in m.doc.Objects if o.Label.startswith('Mainboard mounting hole · tool')]
    shieldholes=[o for o in m.doc.Objects if o.Label.startswith('Support-sheet post clearance · tool')]
    boardholes[4].Shape=Part.makeCylinder(.78,1.3,V(6.5,28.8,8.1));shieldholes[4].Shape=Part.makeCylinder(1.8,.8,V(6.5,28.8,1.5))
    # Rear screws sit completely on the curved cover; lower ones share PCB pillars.
    old=[(-85,23),(85,23),(-85,-24),(85,-24)];new=[(-82,23),(82,23),(-82,-21),(82,-21)]
    holes=[o for o in m.doc.Objects if o.Label.startswith('Rear service screw seat · tool')]
    for i,((a,b),(x,y)) in enumerate(zip(old,new)):
        _move(m,'RearScrew'+str(i),(x-a,y-b,0));holes[i].Shape=Part.makeCompound([Part.makeCylinder(.73,2,V(x,y,-.1)),Part.makeCylinder(1.32,.45,V(x,y,-.03))])
        if i<2:m.ring('RearBoss'+str(i),'Upper rear-cover screw boss',1.55,.75,3.5,(x,y,1.3),'Internal',-5,'black',internal=True)
    _move(m,'OLEDCarrier',(0,0,.2))
    m.cut('OLEDCarrier',m.rr(23,6,8,(11.5,34.5,11),.8,App.Rotation(V(0,0,1),V(0,1,0))),'OLED carrier accessory-port notch')
    for side in ['Left','Right']:m.cut('ControlConnector'+side,m.parts['ControlFlex'+side].Shape,'Control FPC insertion slot')
    m.doc.recompute()
    m.checkpoint(12,'measured_assembly_refinement','依据实体求交修正肩键、顶部螺钉、后触控排线、存储卡小板、传感器、麦克风导管、安装柱与 OLED 支架，并对齐后盖紧固件。')

STAGES[12]=stage12


def stage13(m):
    # Tilt the closed strap eyes along the curved lower corners. The previous
    # horizontal trim reached the outer silhouette and left an open U shape.
    seats=[o for o in m.doc.Objects if o.Label.startswith('Strap-eye seat and through opening · tool')]
    rearholes=[o for o in m.doc.Objects if o.Label.startswith('Strap-eye rear through-opening · tool')]
    for j,side in enumerate([-1,1]):
        x,y=side*70,-34
        outer=_ellipse(21,6.4,16.9,1.7,x,y);inner=_ellipse(17.2,3.5,-.1,20,x,y)
        outer.rotate(V(x,y,0),V(0,0,1),side*28);inner.rotate(V(x,y,0),V(0,0,1),side*28)
        eye=outer.cut(inner);_replace(m,'StrapEye'+str(side),eye)
        for tool in seats[j*3:j*3+3]:tool.Shape=Part.makeCompound([eye,inner])
        rearholes[j].Shape=inner.copy()
        m.cut('ControlPCB'+str(side),inner,'Controller-board strap-eye notch')
    m.doc.recompute();m.profile['stages']=13
    m.checkpoint(13,'closed_corner_strap_eyes','将腕带孔改为沿机身曲线倾斜的闭合椭圆环，同步调整机壳与按键板让位，消除角部开口越出轮廓的问题。')

STAGES[13]=stage13


def stage14(m):
    # Move the eyes slightly inward/downward and raise the larger PS key so all
    # three outlines remain closed and separate within the curved corners.
    seats=[o for o in m.doc.Objects if o.Label.startswith('Strap-eye seat and through opening · tool')]
    rearholes=[o for o in m.doc.Objects if o.Label.startswith('Strap-eye rear through-opening · tool')]
    pcbholes=[o for o in m.doc.Objects if o.Label.startswith('Controller-board strap-eye notch · tool')]
    for j,side in enumerate([-1,1]):
        x,y=side*68.7,-35.15
        outer=_ellipse(21,6.4,16.9,1.7,x,y);inner=_ellipse(17.2,3.5,-.1,20,x,y)
        outer.rotate(V(x,y,0),V(0,0,1),side*28);inner.rotate(V(x,y,0),V(0,0,1),side*28)
        eye=outer.cut(inner);_replace(m,'StrapEye'+str(side),eye)
        for tool in seats[j*3:j*3+3]:tool.Shape=Part.makeCompound([eye,inner])
        rearholes[j].Shape=inner.copy();pcbholes[j].Shape=inner.copy()
    for key in ['PSKey','PSKeyMark','SystemSwitch0','SystemStem0']:_move(m,key,(0,.8,0))
    next(o for o in m.doc.Objects if o.Label.startswith('Oval system-key opening · tool')).Shape=_ellipse(12.3,6.1,17.15,1.7,-73,-26.5)
    next(o for o in m.doc.Objects if o.Label.startswith('System-key transmission bore · tool')).Shape=m.parts['SystemStem0'].Shape.copy()
    m.doc.recompute();m.profile['stages']=14
    m.checkpoint(14,'strap_and_system_key_clearance','调整闭合腕带环与 PS/START 键的边界，保留角部轮廓并同步移动 PS 键传动和安装孔，完成相邻外观件的间隙修正。')

STAGES[14]=stage14
