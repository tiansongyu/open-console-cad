"""2022 LCD Steam Deck: native shell and hollow curved grip studies."""
from .core import V
import FreeCAD as App
import Part


def _ellipsoid(rx,ry,rz,center):
    transform=App.Matrix();transform.A11=rx;transform.A22=ry;transform.A33=rz
    shape=Part.makeSphere(1).transformGeometry(transform)
    shape.translate(V(*center));return shape


def stage01(m):
    p=m.profile;w,h=p['width'],p['height']
    p['envelope_basis']='Published complete handheld envelope includes controls; 37 mm shell datum is a model construction parameter.'
    m.native('RearPlate','LCD model rear shell bridge',w-1.4,h-1.4,17.3,1.2,(0,0,13.7),layer=-6)
    m.native('MainFrame','Steam Deck structural perimeter',w,h,18.0,20.7,(0,0,15.0),layer=0,expr={'Width':'Parameters.Width','Height':'Parameters.Height'})
    m.cut('MainFrame',m.rr(w-3.4,h-3.4,21.1,(0,0,14.8),16.3),'Main electronics cavity')
    m.native('FrontFace','LCD model control and display face blank',w-.4,h-.4,17.8,1.2,(0,0,35.8),layer=4)
    lower=Part.makeBox(320,140,14.65,V(-160,-70,-1))
    for side in [-1,1]:
        center=(side*119,-7,18)
        outer=_ellipsoid(30,50,18,center).common(lower)
        inner=_ellipsoid(28.5,48.5,16.5,center)
        m.feature('RearGrip'+str(side),'Hollow curved rear grip',outer.cut(inner),'Body',-6,'accent')
        m.cut('RearPlate',inner,'Grip cavity opening in rear shell bridge')
    m.checkpoint(1,'lcd_shell_and_hollow_grips','建立 2022 LCD 版的大尺寸机身、原生前面板与周框、后壳桥板和中空曲面握把；49 mm 总厚度将在控制件完成后核对。')


STAGES={1:stage01}

import math
from .clamshell import _move,_replace
from .psp import _polygon
from .psv import _ellipse


def stage02(m):
    w,h=m.profile['upper_display']
    m.cut('FrontFace',m.rr(165,104,1.9,(0,0,35.5),1.7),'Seven-inch LCD window recess')
    surround=m.rr(164.6,103.6,.55,(0,0,36.15),1.5).cut(m.rr(w+.15,h+.15,.8,(0,0,36.0),.35))
    m.feature('DisplaySurround','LCD model wide black bezel',surround,'Display',5,'bezel')
    m.box('LCDBackplate','LCD metal backplate',160.4,100.4,.35,(0,0,32.35),'Display',1,'metal',1.0,True)
    m.box('LCD','7-inch 16:10 LCD module',160,100,3.65,(0,0,32.8),'Display',2,'black',.9,True)
    m.box('TouchLayer','Front capacitive touch layer',w,h,.12,(0,0,36.57),'Display',3,'screen',.25,True)
    m.box('DisplayGlass','Seven-inch display window',w,h,.20,(0,0,36.8),'Display',7,'screen',.3)
    for side in [-1,1]:
        x,y=side*109,-4
        m.cut('FrontFace',m.rr(35.3,35.3,2.0,(x,y,35.4),4.0),'Square trackpad opening')
        rim=m.rr(35,35,.6,(x,y,36.2),3.9).cut(m.rr(32.7,32.7,1,(x,y,36.0),3.1))
        m.feature('TrackpadRim'+str(side),'Trackpad surround',rim,'Touchpads',5,'black')
        m.box('TrackpadSurface'+str(side),'32.5 mm touchpad surface',32.5,32.5,1.15,(x,y,35.85),'Touchpads',6,'rubber',3.0)
        m.box('TrackpadFoil'+str(side),'Trackpad electrode foil',31.5,31.5,.1,(x,y,35.65),'Touchpads',4,'copper',2.6,True)
        m.box('TrackpadCarrier'+str(side),'Trackpad pressure plate',33,33,.45,(x,y,35.0),'Touchpads',3,'metal',3.0,True)
    m.checkpoint(2,'lcd_and_dual_trackpads','建立 7 英寸 LCD、触控层和双 32.5 mm 方形触控板，保留独立电极与压力承托层。')


def stage03(m):
    cross=m.rr(6.4,19,1.35,(-129,35,36.35),.65).fuse(m.rr(19,6.4,1.35,(-129,35,36.35),.65)).removeSplitter()
    m.feature('DPad','Directional cross',cross,'Controls',6,'black')
    hole=m.rr(6.75,19.35,2.0,(-129,35,35.5),.75).fuse(m.rr(19.35,6.75,2.0,(-129,35,35.5),.75));m.cut('FrontFace',hole,'Directional-pad clearance')
    for i,(dx,dy,angle) in enumerate([(0,5.8,0),(5.8,0,-90),(0,-5.8,180),(-5.8,0,90)]):
        x,y=-129+dx,35+dy;arrow=_polygon([(x,y+.8),(x-.7,y-.55),(x+.7,y-.55)],37.718,.018);arrow.rotate(V(x,y,0),V(0,0,1),angle)
        m.feature('DPadArrow'+str(i),'Directional arrow',arrow,'Controls',6,'white')
        m.cyl('DPadStem'+str(i),'Directional plunger',1.55,3.2,(x,y,33.05),'Controls',3,'black',internal=True);m.cut('FrontFace',m.parts['DPadStem'+str(i)].Shape,'Directional stem bore')
    for dx,dy,ch in [(0,7.4,'Y'),(7.4,0,'B'),(0,-7.4,'A'),(-7.4,0,'X')]:
        x,y=128+dx,34+dy;m.cut('FrontFace',Part.makeCylinder(4.2,2.2,V(x,y,35.5)),'ABXY key bore')
        cap=Part.makeCylinder(4,1.15,V(x,y,36.9));cap=cap.makeFillet(.18,[e for e in cap.Edges if e.BoundBox.ZLength<1e-6])
        m.feature('Button'+ch,ch+' key',cap,'Controls',6,'black');m.label('ButtonMark'+ch,ch,2.4,(x-.85,y-1,38.067),'Controls',6,'white')
        m.cyl('ButtonStem'+ch,'ABXY plunger',1.5,3.4,(x,y,33.4),'Controls',3,'black',internal=True)
    for side in [-1,1]:
        x,y=side*105,33
        m.cut('FrontFace',Part.makeCylinder(11.55,2.5,V(x,y,35.1)),'Capacitive thumbstick opening')
        m.ring('StickBezel'+str(side),'Thumbstick annular base',11.4,9.7,.6,(x,y,36.65),'Controls',5,'metal')
        m.cyl('StickStem'+str(side),'Thumbstick shaft',3.3,11.2,(x,y,36.1),'Controls',3,'black')
        cap=Part.makeCylinder(8.2,1.6,V(x,y,47.4));cap=cap.makeFillet(.35,[e for e in cap.Edges if e.BoundBox.ZLength<1e-6]);cap=cap.cut(Part.makeSphere(25,V(x,y,73.75)))
        m.feature('StickCap'+str(side),'Concave capacitive thumb cap',cap,'Controls',7,'rubber')
        m.ring('StickBoot'+str(side),'Thumbstick dust skirt',9.5,3.55,1.1,(x,y,35.45),'ControlsInternal',3,'rubber',internal=True)
        # The capacitive cap connection is represented as a separate internal lead.
        m.box('StickTouchLead'+str(side),'Capacitive thumb sensor lead study',.35,.35,8.0,(x+3.7,y,37.3),'ControlsInternal',3,'copper',.06,True)
    for key,x,w in [('SteamKey',-103,16),('QuickAccessKey',103,13.5),('ViewKey',-111,7),('MenuKey',111,7)]:
        y=-31 if key in ['SteamKey','QuickAccessKey'] else 52.7
        m.cut('FrontFace',m.rr(w+.3,5.1,2,(x,y,35.3),2.4),'System-key seat')
        m.box(key,key,w,4.8,.85,(x,y,36.3),'Controls',6,'black',2.3)
    m.label('SteamMark','STEAM',1.45,(-107.8,-31.6,37.168),'Controls',6,'white')
    for i,x in enumerate([101,103,105]):m.cyl('QuickDot'+str(i),'Quick-access dot',.42,.018,(x,-31,37.168),'Controls',6,'white')
    for j,y in enumerate([51.8,52.7,53.6]):m.box('MenuBar'+str(j),'Menu icon bar',2.4,.18,.018,(111,y,37.168),'Controls',6,'white',.02)
    for j,(x,y) in enumerate([(-111.5,53),(-110.7,52.4)]):
        frame=m.rr(2.0,1.4,.018,(x,y,37.168),.05).cut(m.rr(1.65,1.05,.04,(x,y,37.158),.03));m.feature('ViewIcon'+str(j),'View icon',frame,'Controls',6,'white')
    m.checkpoint(3,'sticks_dpad_and_system_keys','加入双电容感应摇杆、十字键、ABXY、Steam/快捷访问/View/Menu 键；摇杆最高面控制在 49 mm 总厚度内。')


def stage04(m):
    top=App.Rotation(V(0,0,1),V(0,1,0));bottom=App.Rotation(V(0,0,1),V(0,-1,0))
    m.cut('MainFrame',m.rr(9.4,4.1,4.5,(48,55,25),1.7,top),'Top USB-C opening')
    shell=m.rr(9.0,3.7,6.1,(48,52.0,25),1.65,top).cut(m.rr(7.8,2.5,6.4,(48,51.9,25),1.1,top))
    m.feature('USBTypeCShell','USB-C receptacle shell',shell,'Ports',0,'metal')
    m.box('USBTypeCTongue','USB-C insulator tongue',7.2,.55,4.9,(48,53.1,25),'Ports',0,'black',.18,orient=top)
    for row in [-1,1]:
        for i in range(12):m.box(f'USBContact{row}_{i}','USB-C contact study',.28,.05,3.3,(45.25+i*.5,54.2,25+row*.34),'Ports',0,'gold',.01,orient=top)
    m.cut('MainFrame',Part.makeCylinder(2.7,6,V(-73,53.0,25),V(0,1,0)),'Top headphone aperture')
    m.ring('HeadphoneSocket','3.5 mm headset jack',2.5,1.76,5.2,(-73,53.05,25),'Ports',0,'metal',axis=(0,1,0))
    for key,x in [('VolumeMinus',-94),('VolumePlus',-83.5),('PowerKey',73)]:
        cap=m.rr(7.8,3.8,.7,(x,57.8,25),1.2,top);m.cut('MainFrame',cap,'Top control seat');m.feature(key,key,cap,'Controls',0,'black')
    m.box('PowerLED','White power indicator',1.2,.8,.15,(63.5,58.35,25),'Ports',0,'white',.2,orient=top);m.cut('MainFrame',m.parts['PowerLED'].Shape,'Power LED inset')
    # Original LCD: black power key and one broad top exhaust row.
    vents=[m.rr(3.0,9.5,3.5,(-63+i*5.4,55.4,25),1.2,top) for i in range(13)]
    m.cut('MainFrame',vents,'Thirteen top exhaust slots')
    m.cut('MainFrame',m.rr(16.0,2.8,3.5,(-72,-59,23),.5,top),'Bottom microSD slot opening')
    lip=m.rr(15.5,2.4,.35,(-72,-58.25,23),.4,bottom).cut(m.rr(13.7,1.2,.8,(-72,-58.0,23),.25,bottom))
    m.feature('MicroSDMouth','Bottom microSD slot lip',lip,'Ports',0,'black')
    for i,x in enumerate([-7.5,7.5]):
        m.cut('FrontFace',Part.makeCylinder(.48,2,V(x,54,35.3)),'Dual microphone inlet')
        m.cyl('MicrophoneMesh'+str(i),'Front microphone mesh',.40,.12,(x,54,36.45),'Audio',4,'black')
    for side in [-1,1]:
        # The LCD front speaker fields have staggered short slots below the buttons.
        slots=[]
        for row in range(4):
            for col in range(3):slots.append(m.rr(3.8,1.2,1.8,(side*103+(col-1)*5.5+(row%2)*1.2,-40-row*3,35.5),.45))
        m.cut('FrontFace',slots,'Staggered front speaker grille')
        m.box('SpeakerMesh'+str(side),'Speaker grille mesh backing',19,12,.12,(side*103,-44.5,35.5),'Audio',4,'black',1.0,True)
    m.checkpoint(4,'usb_c_audio_and_exhaust','建立 USB-C 与接点、顶部耳机/音量/黑色电源键、13 孔排风口、底部 microSD 插槽、双麦克风和前置扬声器格栅。')


def stage05(m):
    # Bumpers sit along the front top edge; triggers project toward the rear.
    for side in [-1,1]:
        x=side*123
        cap=m.rr(39,8.0,6.0,(x,52.4,31.1),3.0).common(m.rr(298,117,6.0,(0,0,31.1),18))
        m.feature('Bumper'+str(side),'L1 / R1 bumper',cap,'Controls',4,'black')
        for key in ['MainFrame','FrontFace']:m.cut(key,cap,'Bumper seating recess')
        # Curved shell of the L2 / R2 trigger, with its own hinge shaft.
        outer=m.rr(29,24,14,(side*130,43.5,15.2),6.0)
        inner=m.rr(25.5,20.5,12,(side*130,43.5,16.2),4.5)
        trigger=outer.cut(inner).common(m.rr(298,117,15,(0,0,14.8),18))
        m.feature('Trigger'+str(side),'L2 / R2 hollow trigger',trigger,'Controls',0,'black')
        for key in ['MainFrame','RearPlate']:m.cut(key,outer,'Rear trigger envelope clearance')
        m.cyl('TriggerPin'+str(side),'Trigger pivot shaft',1.0,23,(side*130-11.5,38.0,24.0),'ControlsInternal',0,'metal',axis=(1,0,0),internal=True)
        m.cut('Trigger'+str(side),m.parts['TriggerPin'+str(side)].Shape,'Trigger hinge passage')
    # Rear paddles follow the curved grip rather than being flat blocks outside it.
    for side in [-1,1]:
        center=(side*119,-7,18)
        band=_ellipsoid(30,50,18,center).cut(_ellipsoid(28.8,48.8,16.8,center))
        for j,yy in enumerate([9,-20]):
            region=Part.makeBox(22,18,14.7,V(side*119-11,yy-9,-.1))
            paddle=band.common(region)
            key=f'RearPaddle{side}_{j}';m.feature(key,'L4/L5 or R4/R5 rear paddle',paddle,'Controls',-6,'black')
            m.cut('RearGrip'+str(side),paddle,'Rear paddle seating cut')
    m.checkpoint(5,'bumpers_triggers_and_rear_paddles','加入前缘肩键、中空后扳机及轴销，并沿曲面握把分出四枚背键，保留独立装配组件。')

STAGES.update({2:stage02,3:stage03,4:stage04,5:stage05})


def _fastener(m,key,pos,axis,length,assembly='Body',layer=-6,radius=1.25):
    shape=Part.makeCylinder(radius,.38).fuse(Part.makeCylinder(.62,length,V(0,0,.35)))
    shape=shape.cut(Part.makeCompound([Part.makeBox(.26,1.8,.23,V(-.13,-.9,-.02)),Part.makeBox(1.8,.26,.23,V(-.9,-.13,-.02))]))
    shape.Placement=App.Placement(V(*pos),App.Rotation(V(0,0,1),V(*axis)))
    return m.feature(key,'Cross-head service fastener',shape,assembly,layer,'metal',True)


def stage06(m):
    slots=[m.rr(2.4,29,1.9,(30+i*5.6,10,13.5),1.1) for i in range(6)]
    m.cut('RearPlate',slots,'Original rear intake slot array')
    m.box('IntakeMesh','Rear intake dust mesh',36,32,.15,(44,10,15.1),'Thermal',-5,'black',1.0,True)
    reverse=App.Rotation(V(0,1,0),180)
    m.label('ValveRearMark','VALVE',4.0,(-8,-2,13.718),'Body',-6,'shell',rotation=reverse)
    m.label('RearModelMark','STEAM DECK  /  LCD 2022',2.0,(37,-45,13.718),'Body',-6,'shell',rotation=reverse)
    for key in ['ValveRearMark','RearModelMark']:m.cut('RearPlate',m.parts[key].Shape,'Rear marking inlay')
    for i,(x,y) in enumerate([(-83,51),(83,51),(-16,-55.2),(16,-55.2)]):
        m.cut('RearPlate',[Part.makeCylinder(.76,2,V(x,y,13.5)),Part.makeCylinder(1.4,.6,V(x,y,13.6))],'Bridge rear screw seat')
        _fastener(m,'RearScrew'+str(i),(x,y,13.73),(0,0,1),5.8)
        m.ring('RearBoss'+str(i),'Rear bridge screw boss',1.7,.76,5.5,(x,y,15.0),'Internal',-4,'black',internal=True)
    index=4
    for side in [-1,1]:
        for y in [23,-38]:
            x=side*128;dx=x-side*119;dy=y+7;z=18-18*math.sqrt(1-(dx/30)**2-(dy/50)**2)
            n=V(-dx/(30*30),-dy/(50*50),(18-z)/(18*18));n.normalize();p=V(x,y,z)
            m.cut('RearGrip'+str(side),[Part.makeCylinder(.76,10,p-n*.1,n),Part.makeCylinder(1.4,.62,p-n*.07,n)],'Curved grip screw seat')
            _fastener(m,'RearScrew'+str(index),tuple(p+n*.04),tuple(n),9.5);index+=1
    # Face labels on the top controls remain separate from the black LCD power key.
    from .geometry import rotation
    q=rotation((0,1,0),(0,0,1))
    for key,text,x in [('VolumeMinusMark','-',-94),('VolumePlusMark','+',-83.5)]:
        m.label(key,text,1.8,(x+.65,58.482,24.35),'Controls',0,'white',rotation=q)
        m.cut(key.replace('Mark',''),m.parts[key].Shape,'Volume symbol inlay')
    m.checkpoint(6,'rear_intake_and_service_fasteners','建立后进风格栅、机型标识与八枚维修螺钉，握把螺钉沿曲面法向安装，保留早期 LCD 外观与黑色电源键。')


def stage07(m):
    outer=m.rr(107,45,8.4,(-45,-31,17.2),2.0).fuse(m.rr(37,50,8.4,(-80,16.2,17.2),2.0)).removeSplitter()
    inner=[m.rr(104,42,7.1,(-45,-31,17.85),1.4),m.rr(34,46,7.1,(-80,16.2,17.85),1.4)]
    m.feature('BatteryPouch','Original 40 Wh L-shaped battery pack',outer.cut(Part.makeCompound(inner)),'Battery',-4,'battery',True)
    m.box('BatteryCellLower','Lower battery-cell layout',103.6,41.6,6.6,(-45,-31,18.10),'Battery',-4,'rubber',1.2,True)
    m.box('BatteryCellUpper','Upper battery-cell layout',33.6,45.6,6.6,(-80,16.2,18.10),'Battery',-4,'rubber',1.2,True)
    m.box('BatteryAdhesiveLower','Lower battery adhesive pad',95,34,.15,(-45,-31,16.95),'Battery',-5,'black',1.0,True)
    m.box('BatteryAdhesiveUpper','Upper battery adhesive pad',26,39,.15,(-80,16.2,16.95),'Battery',-5,'black',1.0,True)
    m.box('BatteryProtectionPCB','Battery protection board study',18,10,.55,(4,-32,25.8),'Battery',-3,'pcb',.7,True)
    m.box('BatteryConnector','Battery connector body',9,5,2.2,(13,-28,20.5),'Battery',-3,'white',.4,True)
    for i in range(4):m.box('BatteryTerminal'+str(i),'Battery terminal study',.8,3,.08,(10+i*2,-28,22.8),'Battery',-3,'gold',.03,True)
    m.box('BatteryLead','Battery connection ribbon study',8,9,.12,(8,-24,23.15),'Battery',-3,'copper',.4,True)
    reverse=App.Rotation(V(0,1,0),180)
    for key,text,size,pos in [('BatteryType','STEAM DECK LCD',2.8,(-11,-22,17.19)),('BatteryCapacity','40 Wh  /  5200 mAh',2.4,(-10,-33,17.19)),('BatteryStudy','LAYOUT STUDY',1.8,(-19,-43,17.19))]:m.label(key,text,size,pos,'Battery',-4,'white',rotation=reverse)
    m.checkpoint(7,'forty_wh_l_shaped_battery','建立 40 Wh 的 L 形电池组、两处电芯、胶垫、保护板与接点，保留独立电池安装层。')


def stage08(m):
    m.colors['deckpcb']=(.055,.060,.065)
    board=m.rr(82,97,.8,(51,0,24.0),2.4).fuse(m.rr(28,15,.8,(48,50,24.0),1.2)).removeSplitter()
    m.feature('Mainboard','Early LCD mainboard outline study',board,'Mainboard',-2,'deckpcb',True)
    m.cut('Mainboard',m.parts['USBTypeCShell'].Shape,'USB-C board-edge mounting relief')
    m.box('APUPackage','AMD APU package study',22,22,2.0,(45,13,21.8),'Mainboard',-2,'black',.45,True)
    reverse=App.Rotation(V(0,1,0),180)
    m.label('APUMark','AMD APU',2.3,(52,12,21.78),'Mainboard',-2,'white',rotation=reverse)
    for i,(x,y) in enumerate([(24,24),(24,8),(72,24),(72,8)]):
        m.box('RAMPackage'+str(i),'LPDDR5 package study',12,10,1.3,(x,y,22.5),'Mainboard',-2,'black',.3,True)
        m.label('RAMMark'+str(i),'RAM',1.6,(x+3,y-.5,22.48),'Mainboard',-2,'white',rotation=reverse)
    for key,x,y,w,h in [('PMIC',24,-15,10,10),('Audio',78,-17,7,7),('USBController',62,44,7,7),('Wireless',55,-28,10,10)]:m.box(key+'Package',key+' package study',w,h,1.0,(x,y,22.8),'Mainboard',-2,'black',.3,True)
    m.box('SSDPCB','M.2 2230 storage PCB',22,30,.6,(55,-27,21.1),'Storage',-3,'deckpcb',.65,True)
    m.box('SSDPackage','Storage package study',14,16,1.0,(55,-27,20.0),'Storage',-3,'black',.3,True)
    shield=m.rr(23.4,31.4,2.6,(55,-27,19.4),.8).cut(m.rr(22.6,30.6,2.2,(55,-27,19.6),.5))
    m.feature('SSDShield','SSD interference shield sleeve',shield,'Storage',-3,'metal',True)
    m.box('SSDConnector','M.2 storage connector',23,3.4,2.0,(55,-10.2,21.8),'Storage',-2,'black',.35,True)
    for i in range(12):m.box('SSDContact'+str(i),'M.2 connector contact study',.60,2.8,.05,(46.2+i*1.6,-11.2,21.0),'Storage',-3,'gold',.02,True)
    m.box('IOBoard','Early LCD audio/volume daughterboard',22,9,.6,(-88,51,25.0),'Mainboard',-2,'deckpcb',.8,True)
    m.box('AudioJackPCB','Headset connector carrier',14,8,.6,(-73,50,23.1),'Mainboard',-2,'deckpcb',.6,True)
    for side in [-1,1]:
        pcb=m.rr(58,105,.8,(side*116.5,0,26.5),5.0).common(m.rr(293.6,112.6,.8,(0,0,26.5),15.8))
        pcb=pcb.cut(m.rr(28,28,1.3,(side*105,33,26.3),2.0))
        m.feature('ControlPCB'+str(side),'Left/right button input board',pcb,'ControlsInternal',1,'deckpcb',True)
        m.box('StickPCB'+str(side),'Replaceable thumbstick PCB',27,27,.6,(side*105,33,27.0),'ControlsInternal',1,'deckpcb',2.2,True)
    points=[(16,y) for y in [-35,-23,-5,13,31,43]]+[(84,y) for y in [-38,-27,-4,16,35]]+[(x,-44) for x in [26,39,51,66,79]]+[(x,39) for x in [26,37,49,73]]+[(39,-10),(33,-27),(71,-9),(74,-35)]
    for i,(x,y) in enumerate(points):
        m.box('Passive'+str(i),'SMD passive body',1.3,.85,.65,(x,y,23.1),'Mainboard',-2,'rubber',.03,True)
        for side in [-1,1]:m.box(f'Passive{i}End{side}','SMD solder termination',.25,.91,.67,(x+side*.79,y,23.09),'Mainboard',-2,'metal',.02,True)
    m.checkpoint(8,'lcd_mainboard_storage_and_inputs','建立早期 LCD 黑色主板、APU/内存与电源音频封装、M.2 2230 模块及屏蔽套、独立音频小板和左右输入/摇杆板。')


def stage09(m):
    for side in [-1,1]:
        x,y=side*105,33
        housing=m.rr(22,22,7.5,(x,y,27.8),2).cut(Part.makeCylinder(3.55,8,V(x,y,27.6))).cut(Part.makeCylinder(7.1,5.7,V(x,y,29.8)))
        m.feature('StickHousing'+str(side),'Replaceable thumbstick mechanism',housing,'ControlsInternal',2,'black',True)
        m.ring('StickGimbal'+str(side),'Thumbstick gimbal support',6.3,3.45,1.3,(x,y,34.0),'ControlsInternal',3,'metal',internal=True)
        _replace(m,'StickStem'+str(side),Part.makeCylinder(3.3,13,V(x,y,34.3)))
        for i,(dx,dy,w,h) in enumerate([(12.2,0,2.2,10),(0,12.2,10,2.2)]):m.box(f'StickSensor{side}_{i}','Thumbstick position sensor',w,h,4.2,(x+dx,y+dy,29),'ControlsInternal',2,'rubber',.4,True)
        m.cyl('StickClick'+str(side),'Thumbstick press switch',1.3,.5,(x,y,27.75),'ControlsInternal',1,'metal',internal=True)
        for i,(dx,dy) in enumerate([(-11.7,-11.7),(11.7,-11.7),(0,11.9)]):
            m.cut('StickPCB'+str(side),Part.makeCylinder(.76,1.0,V(x+dx,y+dy,26.8)),'Thumbstick PCB fastener hole')
            m.screw(f'StickScrew{side}_{i}',(x+dx,y+dy,28.3),'ControlsInternal',1,length=3.4,radius=1.1,axis=(0,0,-1))
    positions=[(-129,40.8),(-123.2,35),(-129,29.2),(-134.8,35),(128,41.4),(135.4,34),(128,26.6),(120.6,34)]
    m.cyl('DPadCarrier','D-pad transmission carrier',9.1,.35,(-129,35,32.65),'ControlsInternal',3,'black',internal=True)
    for i,(x,y) in enumerate(positions):
        m.cyl('KeyContact'+str(i),'Button board gold contact',2.1,.08,(x,y,27.4),'ControlsInternal',1,'gold',internal=True)
        m.cyl('KeyPill'+str(i),'Conducting contact pill',1.4,.15,(x,y,27.65),'ControlsInternal',1,'black',internal=True)
        m.cyl('KeyRubber'+str(i),'Silicone button cup',2.7,3.0,(x,y,27.95),'ControlsInternal',2,'rubber',internal=True)
        m.cyl('KeyBoss'+str(i),'Button transmission boss',1.2,1.5 if i<4 else 2.3,(x,y,31.0),'ControlsInternal',3,'rubber',internal=True)
    for i,(x,y) in enumerate([(-103,-31),(103,-31),(-111,52.7),(111,52.7)]):
        m.box('SystemSwitch'+str(i),'System-button tactile switch',5.5,3.8,1.2,(x,y,27.6),'ControlsInternal',1,'metal',.4,True)
        m.cyl('SystemStem'+str(i),'System-button plunger',1.2,7.3,(x,y,28.9),'ControlsInternal',3,'black',internal=True)
        m.cut('FrontFace',m.parts['SystemStem'+str(i)].Shape,'System-button plunger passage')
    m.checkpoint(9,'replaceable_sticks_and_button_mechanisms','补齐可拆摇杆机构、位置传感器、压按开关、安装螺钉及按钮胶垫、导电粒和系统键传动柱。')


def stage10(m):
    for side in [-1,1]:
        x,y=side*109,-4
        m.box('TrackpadPCB'+str(side),'Trackpad sensor PCB',33,33,.6,(x,y,29.0),'Touchpads',1,'deckpcb',2.5,True)
        m.ring('HapticCoil'+str(side),'Trackpad haptic voice-coil study',4.0,2.7,.6,(x,y,30.0),'Touchpads',2,'copper',internal=True)
        m.cyl('HapticMagnet'+str(side),'Trackpad haptic magnet',2.5,1.5,(x,y,30.65),'Touchpads',2,'metal',internal=True)
        m.box('HapticArmature'+str(side),'Haptic moving armature',12,10,.25,(x,y,32.25),'Touchpads',2,'metal',1.0,True)
        # Two planar spring paths are modeled as continuous thin steel parts.
        for edge in [-1,1]:
            xx=x+edge*16.9
            path=[(xx,y-18),(xx,y-12),(xx-edge*2,y-10),(xx-edge*2,y+10),(xx,y+12),(xx,y+18)]
            bars=[]
            for a,b in zip(path,path[1:]):
                va,vb=V(*a,33.8),V(*b,33.8);length=(vb-va).Length
                sh=m.rr(.65,length+.1,.22,(0,0,0),.15);sh.Placement=App.Placement((va+vb)*.5,App.Rotation(V(0,1,0),vb-va));bars.append(sh)
            m.feature(f'TrackpadSpring{side}_{edge}','Touchpad pressure spring',bars[0].multiFuse(bars[1:]).removeSplitter(),'Touchpads',3,'metal',True)
        for i,(dx,dy) in enumerate([(-17,-17),(17,-17),(-17,17),(17,17)]):
            m.screw(f'TrackpadScrew{side}_{i}',(x+dx,y+dy,30.4),'Touchpads',1,length=4.0,radius=1.1,axis=(0,0,-1))
        tx=side*130
        bracket=m.rr(25,20,1.8,(tx,43.5,16.3),3.5)
        for dx in [-10.3,10.3]:bracket=bracket.fuse(m.rr(2.5,6,7,(tx+dx,38,18.1),.5))
        bracket=bracket.cut(m.parts['TriggerPin'+str(side)].Shape)
        m.feature('TriggerBracket'+str(side),'Trigger hinge bracket',bracket.removeSplitter(),'ControlsInternal',0,'black',True)
        helix=Part.makeHelix(.8,5.5,1.6);wire=Part.Wire(Part.makeCircle(.20,helix.Vertexes[0].Point,helix.Edges[0].tangentAt(helix.Edges[0].FirstParameter)))
        spring=Part.Wire(helix.Edges).makePipeShell([wire],True,False);spring.translate(V(tx,44,18.5))
        m.feature('TriggerSpring'+str(side),'Trigger return spring',spring,'ControlsInternal',0,'metal',True)
        m.box('TriggerSensor'+str(side),'Trigger-angle sensor study',2.5,3.5,1.1,(tx,29.5,27.5),'ControlsInternal',1,'black',.3,True)
        for j,yy in enumerate([9,-20]):
            m.box(f'RearButtonSwitch{side}_{j}','Rear button switch carrier',9,6,1.2,(side*119,yy,11.5),'ControlsInternal',-4,'deckpcb',.6,True)
    m.checkpoint(10,'trackpad_haptics_and_trigger_springs','建立双触控板的独立传感板、音圈与衔铁、压力弹片，以及扳机支架、复位弹簧、角度传感器和四枚背键开关。')

STAGES.update({6:stage06,7:stage07,8:stage08,9:stage09,10:stage10})



def stage11(m):
    # Early LCD cooling: one centrifugal fan, flattened copper heatpipe, silver shield.
    fx,fy=-33.5,25.0
    case=m.rr(52,51,9,(fx,fy,21.0),8.0).cut(Part.makeCylinder(23.4,10,V(fx,fy,20.8)))
    case=case.cut(m.rr(31,14,8,(fx,49,21.8),.5))
    m.feature('FanHousing','LCD centrifugal blower housing',case,'Thermal',-1,'black',True)
    plate=m.rr(51,50,.35,(fx,fy,20.55),7.5).cut(Part.makeCylinder(18.6,.8,V(fx,fy,20.35)))
    m.feature('FanRearPlate','Blower inlet metal plate',plate,'Thermal',-2,'metal',True)
    m.cyl('FanRotorBase','Fan rotor backing disc',21.8,.35,(fx,fy,28.7),'Thermal',0,'black',internal=True)
    m.cyl('FanHub','Blower motor hub',6.5,6.6,(fx,fy,21.8),'Thermal',-1,'black',internal=True)
    # Curved blades use an annular sector, separately traceable from the hub.
    for i in range(30):
        angle=i*12
        blade=Part.makeCylinder(21.4,5.9,V(fx,fy,22.2),V(0,0,1),1.7).cut(Part.makeCylinder(7.0,6.3,V(fx,fy,22.0)))
        blade.rotate(V(fx,fy,0),V(0,0,1),angle)
        m.feature('FanBlade'+str(i),'Centrifugal impeller blade study',blade,'Thermal',-1,'rubber',True)
    m.ring('FanFrontRing','Blower front retainer',23.2,21.9,.35,(fx,fy,29.2),'Thermal',0,'metal',internal=True)
    for i,(x,y) in enumerate([(-56,4),(-11,5),(-56,46)]):
        bore=Part.makeCylinder(.76,10,V(x,y,20.2))
        for key in ['FanHousing','FanRearPlate']:m.cut(key,bore,'Blower mounting hole')
        m.screw('FanScrew'+str(i),(x,y,20.1),'Thermal',-2,length=5.0,radius=1.15)
    m.box('ColdPlate','APU copper cold plate',29,29,1.0,(45,13,20.3),'Thermal',-3,'copper',2.0,True)
    m.box('ThermalPaste','APU thermal interface study',20.5,20.5,.18,(45,13,21.48),'Thermal',-2,'metal',.3,True)
    # Smooth 90-degree bend; Z flattening keeps the copper pipe below the fan inlet.
    a,b,c,d,e=V(45,13,0),V(45,38,0),V(35,48,0),V(-32,48,0),V(-32,54,0)
    edges=[Part.makeLine(a,b),Part.Arc(b,V(42.0710678,45.0710678,0),c).toShape(),Part.makeLine(c,d)]
    path=Part.Wire(edges);profile=Part.Wire(Part.makeCircle(2.8,a,V(0,1,0)))
    pipe=path.makePipeShell([profile],True,False)
    flatten=App.Matrix();flatten.A33=.35;pipe=pipe.transformGeometry(flatten);pipe.translate(V(0,0,19.2))
    m.feature('Heatpipe','Flattened copper heatpipe study',pipe,'Thermal',-3,'copper',True)
    m.box('FinBase','Copper exhaust fin base',63,7.0,.35,(-31,53.1,19.8),'Thermal',-2,'copper',.3,True)
    for i in range(39):
        m.box('HeatFin'+str(i),'Exhaust heat exchanger fin',.35,7.0,8.8,(-61.4+i*1.6,53.1,20.25),'Thermal',-1,'metal',.05,True)
    # A thin stamped early-model silver cover, with turned-up perimeter flanges.
    shield=m.rr(81,95,.35,(51,0,17.0),3.0)
    flange=m.rr(81,95,1.7,(51,0,17.35),3.0).cut(m.rr(80.3,94.3,2.1,(51,0,17.2),2.65))
    shield=shield.fuse(flange).removeSplitter()
    m.feature('EMIShield','Original silver mainboard shield',shield,'Mainboard',-4,'metal',True)
    for i,(x,y) in enumerate([(14,-43),(88,-43),(87,43)]):
        hole=Part.makeCylinder(.76,3,V(x,y,16.8));m.cut('EMIShield',hole,'Shield screw clearance')
        m.screw('ShieldScrew'+str(i),(x,y,16.5),'Mainboard',-4,length=4.5,radius=1.25)
        m.ring('ShieldBoss'+str(i),'Shield mounting spacer',1.75,.76,2.4,(x,y,18.0),'Internal',-3,'black',internal=True)
    m.box('FanConnector','Four-pin fan cable socket',6.0,3.3,1.3,(18,42,22.45),'Thermal',-2,'white',.3,True)
    m.box('FanCable','Fan cable routing study',14,2.5,.18,(3,42,23.0),'Thermal',-2,'copper',.3,True)
    m.checkpoint(11,'lcd_blower_heatpipe_and_silver_shield','建立早期 LCD 离心风机、独立叶片、压扁铜热管、APU 冷板、排风鳍片和银色屏蔽罩，保留可分解的散热装配层。')


def stage12(m):
    # Audio modules sit ahead of the input PCBs, directly behind the front grilles.
    for side in [-1,1]:
        x,y=side*103,-44.5
        frame=m.rr(20,14,5.8,(x,y,28.1),2.2).cut(m.rr(16.4,10.4,6.2,(x,y,27.9),1.5))
        m.feature('SpeakerFrame'+str(side),'Stereo acoustic enclosure',frame,'Audio',2,'black',True)
        m.box('SpeakerMagnet'+str(side),'Speaker magnet',9,6,2.8,(x,y,28.3),'Audio',2,'metal',1.1,True)
        m.box('SpeakerDiaphragm'+str(side),'Speaker diaphragm',16,10,.12,(x,y,34.2),'Audio',3,'rubber',1.3,True)
        m.box('SpeakerFlex'+str(side),'Speaker connection flex',7,2,.1,(x-side*11,y,28.6),'Audio',1,'copper',.25,True)
    for i,x in enumerate([-7.5,7.5]):
        m.box('MicrophonePackage'+str(i),'Dual microphone package',2.5,2.0,1.0,(x,54,31.0),'Audio',1,'metal',.3,True)
    m.box('MicroSDCarrier','microSD slot carrier',16.8,15,2.3,(-72,-49,21.9),'Storage',-2,'black',.8,True)
    m.cut('MicroSDCarrier',m.rr(12.0,14,1.15,(-72,-51,22.6),.4),'microSD insertion cavity')
    # Visible plug-in edge contacts remain independent of the slot housing.
    for i in range(8):m.box('MicroSDContact'+str(i),'microSD contact',.65,2.5,.06,(-76.2+i*1.2,-44,22.8),'Storage',-2,'gold',.04,True)
    for key,x,y,w in [('LCDConnector',48,-47,18),('TouchConnector',70,-47,8),('LeftInputConnector',17,-2,10),('RightInputConnector',86,-2,10)]:
        m.box(key,'Flex connector body',w,3,1.0,(x,y,25.0),'Mainboard',0,'white',.3,True)
    for key,w,h,x,y,z in [('LCDRibbon',16,18,48,-39,30.2),('TouchRibbon',6,18,70,-39,30.5),('LeftInputRibbon',88,7,-29,-2,30.7),('RightInputRibbon',18,7,91,-2,28.3)]:
        m.box(key,'Flexible interconnect routing study',w,h,.12,(x,y,z),'Internal',1,'copper',.5,True)
    # Mainboard attachment and metal standoffs have explicit clearance bores.
    for i,(x,y) in enumerate([(14,-45),(89,-45),(14,45),(88,45),(51,46)]):
        bore=Part.makeCylinder(.78,1.3,V(x,y,23.8));m.cut('Mainboard',bore,'Mainboard screw bore')
        m.screw('MainboardScrew'+str(i),(x,y,25.2),'Mainboard',0,length=3.8,radius=1.2,axis=(0,0,-1))
        m.ring('MainboardSpacer'+str(i),'Mainboard fixing spacer',1.7,.78,2.1,(x,y,21.6),'Internal',-2,'metal',internal=True)
    for side in [-1,1]:
        for j,y in enumerate([9,-20]):
            x=side*119;bottom=18-18*math.sqrt(1-((y+7)/50)**2)
            m.cyl(f'RearKeyPlunger{side}_{j}','Rear paddle transmission post',1.5,10.0-(bottom+1.4),(x,y,bottom+1.4),'ControlsInternal',-5,'black',internal=True)
            m.box(f'RearKeyDome{side}_{j}','Rear button tactile dome',4.2,4.2,.3,(x,y,10.8),'ControlsInternal',-4,'metal',.9,True)
    # Detached generic 45 W USB-C accessory is a scale study, not a specific region plug.
    m.native('AdapterBody','45 W USB-C power adapter study',52,46,5,27,(0,-110,0),'Accessories',0,'black')
    m.label('AdapterMark','45 W  USB-C',3,(-18,-110,27.018),'Accessories',0,'white')
    for i,x in enumerate([-6.3,6.3]):m.box('AdapterPin'+str(i),'Power-adapter plug blade study',1.5,6.0,14,(x,-110,-14.1),'Accessories',0,'metal',.15)
    # Reusable CAD primitive cable path, outside the handheld envelope.
    path=Part.Wire([Part.makeLine(V(26,-110,13),V(44,-110,13)),Part.Arc(V(44,-110,13),V(65,-101,13),V(65,-84,13)).toShape()])
    profile=Part.Wire(Part.makeCircle(1.3,V(26,-110,13),V(1,0,0)))
    m.feature('AdapterCable','USB-C adapter cable segment',path.makePipeShell([profile],True,False),'Accessories',0,'rubber')
    m.box('AdapterPlugGrip','USB-C cable grip',10,18,5,(65,-73.9,10.5),'Accessories',0,'black',1.5)
    top=App.Rotation(V(0,0,1),V(0,1,0))
    m.box('AdapterPlug','USB-C cable plug',8.3,2.6,6.5,(65,-64.7,13),'Accessories',0,'metal',1.2,orient=top)
    m.profile['internal_exclude']=['RearPlate','RearGrip-1','RearGrip1','RearPaddle-1_0','RearPaddle-1_1','RearPaddle1_0','RearPaddle1_1','ValveRearMark','RearModelMark','EMIShield','IntakeMesh']+[f'RearScrew{i}' for i in range(8)]
    m.profile['internal_normal']=[.2,-.3,-2]
    m.checkpoint(12,'audio_interconnects_and_power_accessory','补齐扬声器、麦克风、microSD 机构、显示/输入排线、主板安装柱、背键传动件与独立 45 W USB-C 电源附件。')

STAGES.update({11:stage11,12:stage12})



def stage13(m):
    # Correct the measured stage-9 stack clashes, keeping the source history replayable.
    _replace(m,'LCD',m.rr(160,100,3.15,(0,0,32.8),.9))
    _move(m,'MicroSDMouth',(0,.1,0))
    m.cut('ViewIcon0',m.parts['ViewIcon1'].Shape,'Overlapping window icon knockout')
    top=App.Rotation(V(0,0,1),V(0,1,0))
    m.cut('Mainboard',m.rr(9.2,3.9,6.5,(48,51.9,25),1.7,top),'Full USB-C receptacle board-edge relief')
    m.cut('Mainboard',m.rr(90,3,1.4,(51,58.1,23.7),.2),'Upper PCB to perimeter clearance')
    m.cut('AudioJackPCB',m.parts['HeadphoneSocket'].Shape,'Headphone carrier mounting relief')
    seats=[o for o in m.doc.Objects if o.Label.startswith('Bumper seating recess · tool')]
    triggers=[o for o in m.doc.Objects if o.Label.startswith('Rear trigger envelope clearance · tool')]
    for j,side in enumerate([-1,1]):
        cap=m.rr(39,5,5.2,(side*123,56,30.5),2.0).common(m.rr(298,117,6,(0,0,30.0),18))
        _replace(m,'Bumper'+str(side),cap)
        for tool in seats[j*2:j*2+2]:tool.Shape=cap.copy()
        for prefix in ['Trigger','TriggerPin','TriggerBracket','TriggerSpring']:_move(m,prefix+str(side),(0,0,-3.5))
        clearance=m.rr(29,24,14,(side*130,43.5,11.7),6.0)
        for tool in triggers[j*2:j*2+2]:tool.Shape=clearance.copy()
        m.cut('RearGrip'+str(side),clearance,'Lower trigger clearance in curved grip')
        for i,(dx,dy) in enumerate([(-11.7,-11.7),(11.7,-11.7),(0,11.9)]):
            x,y=side*105+dx,33+dy
            sh=Part.makeCylinder(1.1,.35).fuse(Part.makeCylinder(.62,2.2,V(0,0,.33)))
            cuts=[Part.makeBox(.28,1.65,.22,V(-.14,-.825,-.02)),Part.makeBox(1.65,.28,.22,V(-.825,-.14,-.02))]
            sh=sh.cut(Part.makeCompound(cuts));sh.rotate(V(),V(0,1,0),180);sh.translate(V(x,y,28.3))
            _replace(m,f'StickScrew{side}_{i}',sh)
            m.cut('StickHousing'+str(side),[Part.makeCylinder(.76,3,V(x,y,25.5)),Part.makeCylinder(1.2,.6,V(x,y,27.85))],'Thumbstick fastener head clearance')
    _move(m,'StickSensor1_0',(-24.4,0,0))
    for i in [2,3]:m.cut('MainFrame',m.parts['RearBoss'+str(i)].Shape,'Rear boss perimeter seat')
    _move(m,'BatteryLead',(0,0,3.35))
    m.cut('SSDShield',m.rr(26,3,4,(55,-11.5,19.0),.1),'Open SSD sleeve connector end')
    # Separate curved-front grip fields follow the inward-sloping LCD shell seam.
    for side in [-1,1]:
        points=[(side*x,y) for x,y in [(146,19),(158,19),(158,-65),(107,-65),(111,-55),(131,-29),(137,13)]]
        region=_polygon(points,35.8,1.2)
        patch=region.common(m.parts['FrontFace'].Shape)
        m.feature('FrontGripField'+str(side),'Sloped front grip field',patch,'Body',4,'accent')
        m.cut('FrontFace',region,'Separate front grip contour')
    m.doc.recompute();m.profile['stages']=13
    m.checkpoint(13,'input_stack_and_shell_clearances','根据实体相交结果修正 LCD/边框层叠、USB 接口让位、后移扳机、摇杆螺钉长度、SSD 屏蔽套开口和相邻键位，并加入前部斜向握把分界。')

STAGES[13]=stage13
