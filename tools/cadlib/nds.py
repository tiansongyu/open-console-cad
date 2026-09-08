"""Original NTR-001 Nintendo DS: thick silver body, dual 4:3 screens and GBA slot."""
from .core import V


def stage01(m):
    p=m.profile;w,h=p['width'],p['height'];fz=p['base_depth']-.8
    m.native('BackCover','NTR-001 rear cover',w-1.8,h-1.8,9.2,1.25,(0,0,0),layer=-6)
    m.native('MainFrame','Original DS deep lower frame',w,h,10.0,16.2,(0,0,1.3),layer=0,expr={'Width':'Parameters.Width','Height':'Parameters.Height'})
    m.cut('MainFrame',m.rr(w-4.0,h-4.0,17.0,(0,0,1.15),8.2),'Lower electronics cavity')
    m.native('FrontDeck','Original DS control deck',w-.7,h-.7,9.65,1.05,(0,0,fz-1.05),layer=4)
    seam=m.rr(w-.5,h-.5,.03,(0,0,17.51),9.65).cut(m.rr(w-4.2,h-4.2,.15,(0,0,17.45),7.8))
    m.feature('LowerCaseSeam','Lower case parting line',seam,layer=0,material='black')
    m.checkpoint(1,'ntr001_deep_enclosure','按 NTR-001 初代厚机身建立银色下壳、主框架、控制面板、原生尺寸约束与内部空腔。')

STAGES={1:stage01}

import math
import Part
import FreeCAD as App
from .clamshell import _move,_replace


def stage02(m):
    p=m.profile;hy,hz=p['hinge_y'],p['hinge_z'];cy=2*hy;backz=2*hz-p['closed_depth'];w,h=p['lid_width'],p['lid_height']
    m.parts['BackCover'].MaterialDescription='black'
    from .geometry import appearance
    appearance(m.parts['BackCover'],m.colors['black'])
    m.native('LidBackCover','Original DS upper outer cover',w,h,7.2,1.0,(0,cy,backz),'Lid',-6,'accent','Lid')
    m.native('LidFrame','Upper display support frame',w-.4,h-.4,7.0,hz-backz-1.50,(0,cy,backz+1.05),'Lid',0,'accent','Lid')
    m.cut('LidFrame',m.rr(w-4,h-4,9.5,(0,cy,backz+.95),5.4),'Upper electronics cavity')
    m.box('LidBezel','Silver speaker and display bezel',w-.85,h-.85,.4,(0,cy,hz-.4),'Lid',5,'accent',6.9,pose='Lid')
    bore=Part.makeCylinder(3.65,146,V(-73,hy,hz),V(1,0,0))
    for key in ['MainFrame','FrontDeck','LidFrame','LidBezel']:m.cut(key,bore,'Hinge-bar clearance')
    for key,x,length,pose in [('LeftHingeSleeve',-35,6,'Base'),('CenterHingeSleeve',-28.5,57,'Lid'),('RightHingeSleeve',29,6,'Base')]:m.ring(key,'Original DS hinge sleeve',3.5,1.55,length,(x,hy,hz),'Hinge',0,'shell',axis=(1,0,0),pose=pose)
    for key,x,length in [('LeftHingeAxle',-35,13),('RightHingeAxle',14,21)]:m.cyl(key,'Hinge axle',1.4,length,(x,hy,hz),'Hinge',0,'metal',axis=(1,0,0),internal=True)
    for side in [-1,1]:m.ring('HingeWasher'+str(side),'Hinge end spacer',3.3,1.47,.35,(side*28.75-.175,hy,hz),'Hinge',0,'metal',axis=(1,0,0))
    # Display fields are both 3 inches at 4:3, unlike the wider upper 3DS screen.
    for name,yy,z,pose,assembly in [('Lower',4.0,p['base_depth']-.8,'Base','Display'),('Upper',84.0,hz,'Lid','LidDisplay')]:
        ww,hh=60.96,45.72
        frame=m.rr(72.0,56.0,.48,(0,yy,z-.28),1.3).cut(m.rr(ww+.12,hh+.12,.8,(0,yy,z-.4),.15))
        base='FrontDeck' if name=='Lower' else 'LidBezel'
        m.cut(base,m.rr(72.3,56.3,1.7,(0,yy,z-1.2),1.4),'Display-bezel inset')
        m.feature(name+'DisplaySurround',name+' black screen border',frame,assembly,5,'bezel',False,pose)
        m.box(name+'LCD',name+' 3-inch LCD',67.5,50.5,2.65,(0,yy,z-3.3),assembly,2,'black',.8,True,pose)
        m.box(name+'LCDBackplate',name+' LCD steel backplate',67.5,50.5,.25,(0,yy,z-3.60),assembly,1,'metal',.8,True,pose)
        if name=='Lower':m.box('LowerTouchDigitizer','Resistive touch panel',ww,hh,.07,(0,yy,z-.07),assembly,6,'screen',.15,False,pose)
        m.box(name+'Glass',name+' display cover',ww,hh,.14,(0,yy,z+.005),assembly,7,'screen',.15,False,pose)
    p['lower_display_y']=4.0;p['upper_display_y']=84.0
    m.checkpoint(2,'equal_displays_and_hinge','建立两块 3 英寸 4:3 屏幕、黑色边框、下屏触控层及中央分段铰链，保留独立上盖结构。')


def stage03(m):
    fz=m.profile['base_depth']-.8
    # Recessed control fields are characteristic of the original thick DS front.
    for side in [-1,1]:
        x=side*54
        m.cut('FrontDeck',m.rr(31.6,63.8,.55,(x,2.5,fz-.32),2.6),'Recessed control-field seat')
        m.box('ControlField'+str(side),'Inset control field',31.2,63.4,.37,(x,2.5,fz-.28),'Body',4,'accent',2.4)
    x,y=-53,5
    cross=m.rr(6.1,19.0,1.1,(x,y,fz-.4),.7).fuse(m.rr(19,6.1,1.1,(x,y,fz-.4),.7)).removeSplitter()
    m.feature('DPad','Original DS directional cross',cross,'Controls',6,'black')
    hole=m.rr(6.4,19.3,2.0,(x,y,fz-1.1),.8).fuse(m.rr(19.3,6.4,2.0,(x,y,fz-1.1),.8))
    for key in ['FrontDeck','ControlField-1']:m.cut(key,hole,'D-pad movement opening')
    for j,(dx,dy) in enumerate([(0,7),(7,0),(0,-7),(-7,0)]):
        mark=m.rr(.45,2.0,.018,(x+dx,y+dy,fz+.715),.08)
        if dx:mark.rotate(V(x+dx,y+dy,0),V(0,0,1),90)
        m.feature('DPadTick'+str(j),'Direction tick',mark,'Controls',6,'rubber')
    for dx,dy,ch in [(0,7.2,'X'),(7.2,0,'A'),(0,-7.2,'B'),(-7.2,0,'Y')]:
        x,y=53+dx,5+dy;hole=Part.makeCylinder(3.55,2.0,V(x,y,fz-1))
        for key in ['FrontDeck','ControlField1']:m.cut(key,hole,'Face-button opening')
        cap=Part.makeCylinder(3.38,1.12,V(x,y,fz-.42));cap=cap.makeFillet(.18,[e for e in cap.Edges if e.BoundBox.ZLength<1e-6])
        m.feature('Button'+ch,ch+' button',cap,'Controls',6,'black');m.label('ButtonMark'+ch,ch,2.2,(x-.88,y-.95,fz+.715),'Controls',6,'rubber')
        m.cyl('ButtonStem'+ch,'Face-button plunger',1.3,2.45,(x,y,fz-2.9),'Controls',3,'black',internal=True)
    for key,text,x,y,ww in [('PowerKey','POWER',-53,29,10),('SelectKey','SELECT',48,29,8),('StartKey','START',61,29,8)]:
        tool=m.rr(ww+.3,3.9,1.7,(x,y,fz-.9),.8)
        for base in ['FrontDeck','ControlField'+str(-1 if x<0 else 1)]:m.cut(base,tool,'System-button inset')
        m.box(key,text+' button',ww,3.6,.95,(x,y,fz-.4),'Controls',6,'black',.7)
        m.label(key+'Legend',text,1.25,(x-3.5,y+3.0,fz+.025),'Body',4,'shell')
    m.label('DSModelLegend','NINTENDO DS',1.7,(10,-26.5,fz+.025),'Body',4,'shell')
    m.checkpoint(3,'recessed_controls','加入初代凹入式控制区域、十字键、ABXY、左上电源键及右上 SELECT/START，按钮和安装孔分别建模。')


def stage04(m):
    p=m.profile;fy=p['height']/2;ry=App.Rotation(V(0,0,1),V(0,1,0));minusy=App.Rotation(V(0,0,1),V(0,-1,0))
    m.cut('MainFrame',m.rr(36.6,5.0,3.4,(0,fy-2.5,8.0),.8,ry),'Rear DS-card slot')
    cage=m.rr(36,30,3.6,(0,fy-15.1,6.2),1.0).cut(m.rr(34.2,31,2.65,(0,fy-14.9,6.65),.6))
    m.feature('GameCardCage','DS Slot-1 metal cage',cage,'Ports',0,'metal',True)
    lip=m.rr(36.2,4.6,.3,(0,fy-.31,8.0),.65,ry).cut(m.rr(34.0,3.1,.55,(0,fy-.42,8.0),.4,ry))
    m.feature('GameCardMouth','Slot-1 rear lip',lip,'Ports',0,'black')
    for j in range(17):m.box('CardContact'+str(j),'DS-card contact',.62,6,.08,(-12+j*1.5,fy-18,6.76),'Ports',0,'gold',.02,True)
    # GBA Slot-2 occupies the broad front opening and runs to the central connector.
    m.cut('MainFrame',m.rr(64.8,9.2,3.4,(0,-fy-.2,7.7),1.0,ry),'Front Game Boy Advance slot')
    channel=m.rr(63.7,39.7,7.5,(0,-22.1,3.05),.8).cut(m.rr(61.5,40.0,7.4,(0,-22.1,3.48),.5))
    m.feature('GBAChannel','GBA cartridge guide channel',channel,'Ports',-2,'black',True)
    mouth=m.rr(64.4,8.8,.25,(0,-fy+.28,7.7),.9,minusy).cut(m.rr(61.8,6.6,.55,(0,-fy+.42,7.7),.5,minusy))
    m.feature('GBAMouth','Slot-2 front surround',mouth,'Ports',0,'black')
    connector=m.rr(60.5,9.0,4.6,(0,-7.5,5.65),.5).cut(m.rr(57.7,9.3,2.3,(0,-7.7,6.8),.3))
    m.feature('GBAConnector','32-pin GBA receptacle',connector,'Ports',-1,'black',True)
    for j in range(32):m.box('GBAContact'+str(j),'GBA edge contact',.65,6.3,.10,(-23.25+j*1.5,-7.5,7.03),'Ports',-1,'gold',.02,True)
    # Charging port and the combined headphone/accessory interface.
    m.cut('MainFrame',m.rr(8.9,4.5,4.0,(-33,fy-3,8.2),.8,ry),'AC charging port opening')
    shell=m.rr(8.4,4.0,5.0,(-33,fy-5.05,8.2),.65,ry).cut(m.rr(6.7,2.4,5.3,(-33,fy-5.15,8.2),.4,ry))
    m.feature('ChargeJackShell','NTR charging socket',shell,'Ports',0,'metal')
    m.box('ChargeJackTongue','Charge jack insulator',5.8,.8,3.9,(-33,fy-4.6,8.2),'Ports',0,'black',.2,orient=ry)
    m.cut('MainFrame',Part.makeCylinder(2.5,4,V(53,-fy-.1,9),V(0,1,0)),'Headphone aperture')
    m.ring('HeadphoneSocket','3.5 mm headphone jack',2.36,1.76,5.6,(53,-fy+.04,9),'Ports',0,'metal',axis=(0,1,0))
    m.box('HeadsetPort','Headset accessory interface',7.0,3.3,.25,(44,-fy+.27,9),'Ports',0,'black',.45,orient=minusy)
    m.cut('MainFrame',m.parts['HeadsetPort'].Shape,'Headset accessory-port seat')
    for j in range(2):m.box('HeadsetPin'+str(j),'Accessory contact',.5,.7,.04,(42.5+j*3,-fy+.03,9),'Ports',0,'gold',.02,orient=minusy)
    m.box('VolumeSlider','Front volume slider',11.5,3.1,.45,(-53,-fy+.46,9),'Controls',0,'black',.5,orient=minusy)
    m.cut('MainFrame',m.parts['VolumeSlider'].Shape,'Volume-slider track')
    m.checkpoint(4,'ds_and_gba_slots','建立 Slot-1 与 17 触点、前方 Slot-2 导槽与 32 针 GBA 接口、专用充电口、耳机/附件口及前置音量滑块。')


def stage05(m):
    p=m.profile;hy,hz=p['hinge_y'],p['hinge_z'];cy=2*hy
    for side in [-1,1]:
        x,y=side*52,67.0
        holes=[Part.makeCylinder(.58,.8,V(x+(col-3)*3.3,y+(row-1.5)*3.3,hz-.55)) for col in range(7) for row in range(4)]
        m.cut('LidBezel',holes,'Original DS stereo-speaker perforations')
        m.ring('SpeakerFrame'+str(side),'Upper speaker frame',8.2,6.9,2.5,(x,y,hz-4.8),'LidInternal',0,'metal',internal=True,pose='Lid')
        m.cyl('SpeakerMagnet'+str(side),'Speaker magnet',4.7,1.9,(x,y,hz-4.4),'LidInternal',0,'metal',internal=True,pose='Lid')
        m.cyl('SpeakerDiaphragm'+str(side),'Speaker diaphragm',6.8,.10,(x,y,hz-2.14),'LidInternal',1,'black',internal=True,pose='Lid')
        gasket=m.rr(22,17,.35,(x,y,hz-1.35),2.0).cut(m.rr(20.5,14.5,.6,(x,y,hz-1.48),1.5))
        m.feature('SpeakerGasket'+str(side),'Speaker perforation gasket',gasket,'LidInternal',2,'black',True,'Lid')
    for i,(x,y) in enumerate([(-45,cy+31),(45,cy+31),(-45,cy-26),(45,cy-26)]):
        pad=m.rr(3.8,3.2,.22,(x,y,hz-.07),.55);m.cut('LidBezel',pad,'Four upper screw-cover pads');m.feature('LidBumper'+str(i),'Upper screw-cover pad',pad,'Lid',6,'rubber',False,'Lid')
    m.cut('FrontDeck',m.rr(1.5,2.4,1.6,(-27,-32,17.35),.35),'Lower microphone aperture')
    m.box('MicrophoneMesh','Microphone inlet',1.25,2.15,.12,(-27,-32,18.15),'Ports',4,'black',.3)
    m.label('MicrophoneLabel','MIC',1.15,(-24.8,-32.7,18.625),'Body',4,'shell')
    for j,(x,mat) in enumerate([(27,'led'),(31,'red')]):
        led=m.rr(1.2,2.0,.18,(x,-32,18.5),.25);m.cut('FrontDeck',led,'Power and charge indicator inset');m.feature('StatusLED'+str(j),'Status indicator',led,'Ports',4,mat)
    for side in [-1,1]:
        x=side*65
        cap=m.rr(18.1,8.0,4.4,(x,p['height']/2-4.1,13.0),2.0)
        m.feature('Shoulder'+str(side),'L/R shoulder',cap,'Controls',0,'shell');m.cut('MainFrame',cap,'Shoulder-button seat')
        m.cyl('ShoulderPin'+str(side),'Shoulder pivot',.65,14,(x-7,p['height']/2-7,14.3),'Internal',0,'metal',axis=(1,0,0),internal=True)
        m.cut('Shoulder'+str(side),m.parts['ShoulderPin'+str(side)].Shape,'Shoulder pivot bore')
    m.checkpoint(5,'speakers_microphone_and_shoulders','增加双扬声器孔阵列、四个上盖螺钉垫、下机身麦克风、状态灯与 L/R 肩键；保留初代无摄像头结构。')

STAGES.update({2:stage02,3:stage03,4:stage04,5:stage05})


def stage06(m):
    # The original DS has a small independent battery hatch, not a full rear lid.
    door=m.rr(33.0,58.0,1.10,(-49,0,.06),1.7)
    m.cut('BackCover',m.rr(33.35,58.35,1.5,(-49,0,-.1),1.85),'Independent NTR battery-hatch opening')
    m.feature('BatteryDoor','NTR battery compartment hatch',door,'Body',-6,'black')
    for i,(x,y) in enumerate([(-68,-31),(68,-31),(-68,30),(68,30),(0,-34),(0,35),(32,4)]):
        bore=Part.makeCylinder(.75,3.4,V(x,y,-.1));seat=Part.makeCylinder(1.42,.50,V(x,y,-.03))
        m.cut('BackCover',[bore,seat],'Seven rear-case fastener seats')
        m.screw('RearCoverScrew'+str(i),(x,y,.055),'Body',-6,length=2.8,radius=1.28)
    m.cut('BatteryDoor',[Part.makeCylinder(.74,2.8,V(-49,25,-.1)),Part.makeCylinder(1.38,.42,V(-49,25,-.03))],'Captive battery-door screw')
    m.screw('BatteryDoorScrew',(-49,25,.055),'Body',-6,length=2.4,radius=1.22)
    rear=App.Rotation(V(0,1,0),180)
    m.label('RearModelMark','NTR-001  /  CAD STUDY',1.8,(27,-26,.025),'Body',-6,'white',rotation=rear)
    m.cut('BackCover',m.parts['RearModelMark'].Shape,'Rear model-mark inlay')
    # Non-telescoping original DS stylus: published overall length about 75 mm.
    x,y,z=-87,-36,4
    m.cyl('StylusBarrel','Original DS plastic stylus',1.45,65,(x,y+3,z),'Accessories',0,'black',axis=(0,1,0))
    m.cyl('StylusGrip','Stylus retention cap',1.70,7,(x,y+68,z),'Accessories',1,'black',axis=(0,1,0))
    m.feature('StylusTip','Stylus tapered tip',Part.makeCone(.16,1.45,3,V(x,y,z),V(0,1,0)),'Accessories',-1,'black')
    # Storage is along the right rear edge, outside the board and cartridge path.
    m.ring('StylusTube','Stylus storage guide',1.75,1.52,69,(69.7,-30,5.0),'Internal',-4,'black',axis=(0,1,0),internal=True)
    m.cut('MainFrame',Part.makeCylinder(1.90,5,V(69.7,38,5),V(0,1,0)),'Rear stylus entrance')
    m.ring('StylusEntrance','Stylus entrance collar',1.83,1.50,1.3,(69.7,39.0,5),'Ports',0,'black',axis=(0,1,0))
    m.checkpoint(6,'battery_hatch_and_original_stylus','完成独立电池仓盖、七枚后壳螺钉、机型标识、触控笔收纳导管及约 75 mm 的初代非伸缩触控笔。')


def stage07(m):
    # Approximate NTR-003 package at the battery side of the board.
    m.box('BatteryPouch','NTR-003 battery enclosure',31,54,6.0,(-49,0,2.1),'Battery',-4,'battery',1.1,True)
    m.cut('BatteryPouch',m.rr(29.5,52.5,4.9,(-49,0,2.65),.7),'Battery cell volume')
    m.box('BatteryCell','Battery cell-stack study',29.2,52.2,4.55,(-49,0,2.8),'Battery',-4,'rubber',.6,True)
    tray=m.rr(32.1,55.1,.3,(-49,0,1.64),1.2).cut(m.rr(29.4,52.4,.6,(-49,0,1.5),.7))
    m.feature('BatteryTray','Battery locating lip',tray,'Battery',-5,'black',True)
    m.box('BatteryConnector','Battery terminal carrier',9,2.2,2.1,(-49,-28.3,2.5),'Battery',-4,'white',.25,True)
    for j in range(3):m.box('BatteryContact'+str(j),'Battery terminal',.75,1.9,.10,(-51.4+j*2.4,-28.3,4.65),'Battery',-4,'gold',.02,True)
    rear=App.Rotation(V(0,1,0),180)
    m.label('BatteryType','NTR-003',2.4,(-39,12,2.075),'Battery',-4,'white',rotation=rear)
    m.label('BatteryCapacity','850 mAh',2.0,(-40,3,2.075),'Battery',-4,'white',rotation=rear)
    m.label('BatteryStudy','LAYOUT STUDY',1.45,(-38,-9,2.075),'Battery',-4,'white',rotation=rear)
    for i,(x,y,w,h) in enumerate([(36,-28,2,18),(-26,25,2,18),(23,26,2,16),(46,29,22,1.5)]):
        m.box('RearRib'+str(i),'Rear shell locating rib',w,h,.8,(x,y,1.4),'Internal',-5,'shell',.25,True)
    m.checkpoint(7,'ntr003_battery','建立 NTR-003 电池外壳、内部电芯、定位边、三端接点与容量标识，并补充后壳定位肋。')


def stage08(m):
    m.box('Mainboard','NTR-CPU board outline study',139,75,.75,(0,0,10.90),'Mainboard',-2,'pcb',4.2,True)
    # Main packages are on the display-facing side; connectors and RF below.
    for key,x,y,w,h,t in [('ARM9',-15,6,17,17,1.1),('ARM7',7,8,15,15,1.0),('RAM',8,-10,13,9,.85),('PMIC',38,-20,7,7,.75),('AudioIC',-31,-23,6,6,.7)]:
        m.box(key+'Package',key+' package study',w,h,t,(x,y,11.85),'Mainboard',-2,'black',.3,True)
        m.label(key+'Label',key,1.55,(x-w*.37,y-.6,11.88+t),'Mainboard',-2,'white')
    m.box('WiFiBoard','Removable RF module PCB',27,24,.55,(44,17,8.3),'Mainboard',-3,'pcb',.8,True)
    shield=m.rr(25.5,22.5,1.15,(44,17,7.05),.7).cut(m.rr(24.5,21.5,1.05,(44,17,7.35),.4))
    m.feature('WiFiShield','RF module metal can',shield,'Mainboard',-3,'metal',True)
    m.box('WiFiChip','RF package study',10,10,.65,(44,17,7.53),'Mainboard',-3,'black',.3,True)
    m.box('WiFiConnector','RF daughterboard connector',10,2,1.55,(44,3.6,8.65),'Mainboard',-3,'white',.2,True)
    rear=App.Rotation(V(0,1,0),180)
    m.label('BoardMark','NTR-CPU  /  LAYOUT',1.8,(27,-28,10.87),'Mainboard',-2,'white',rotation=rear)
    points=[(-58,-20),(-48,-20),(-40,-31),(-21,-29),(-10,-29),(0,-29),(11,-29),(22,-29),(45,-30),(57,-26),(-30,24),(-18,29),(0,29),(16,29),(37,29),(54,29),(38,-3),(46,-3),(56,-3),(-35,-4)]
    for i,(x,y) in enumerate(points):
        m.box('Passive'+str(i),'SMD passive body',1.1,.75,.5,(x,y,11.80),'Mainboard',-2,'rubber',.02,True)
        for side in [-1,1]:m.box(f'Passive{i}End{side}','Passive solder end',.22,.81,.52,(x+side*.68,y,11.79),'Mainboard',-2,'metal',.015,True)
    m.checkpoint(8,'dual_arm_mainboard_and_rf','建立 NTR 主板轮廓、ARM9/ARM7/RAM 与电源音频封装、独立射频子板和屏蔽罩，按功能区域布置阻容器件。')


def stage09(m):
    # Separate button membranes, conducting pills and board contact discs.
    positions=[(-53,12.0),(-46,5),(-53,-2),(-60,5),(53,12.2),(60.2,5),(53,-2.2),(45.8,5)]
    for j,(x,y) in enumerate(positions):
        m.cyl('ButtonGoldPad'+str(j),'Button PCB contact',2.1,.06,(x,y,11.72),'Internal',0,'gold',internal=True)
        m.cyl('ButtonPill'+str(j),'Conducting contact pill',1.5,.15,(x,y,12.0),'Internal',1,'black',internal=True)
        m.cyl('ButtonRubber'+str(j),'Button silicone cup',2.6,2.25,(x,y,12.35),'Internal',1,'rubber',internal=True)
        m.cyl('ButtonLift'+str(j),'Button membrane upper boss',1.3,1.15,(x,y,14.64),'Internal',2,'rubber',internal=True)
    for i,(x,y,w) in enumerate([(-53,29,10),(48,29,8),(61,29,8)]):
        m.box('SystemSwitch'+str(i),'System-key tactile switch',w-1,3.3,1.0,(x,y,12.05),'Internal',1,'metal',.3,True)
        m.box('SystemStem'+str(i),'System-key transmission post',3,2.4,4.8,(x,y,13.15),'Internal',2,'black',.25,True)
    m.box('MicrophonePCB','Microphone carrier',5,5,.45,(-27,-32,12.3),'Internal',1,'pcb',.4,True)
    m.cyl('MicrophoneCapsule','Microphone capsule',1.9,2.6,(-27,-32,13.0),'Internal',2,'metal',internal=True)
    for j,x in enumerate([27,31]):m.box('LEDPackage'+str(j),'Indicator emitter',1.4,2.2,.7,(x,-32,13.2),'Internal',2,'white',.15,True)
    for side in [-1,1]:
        m.box('ShoulderSwitch'+str(side),'L/R tactile switch',5,3.2,2.0,(side*62,31.5,11.95),'Internal',1,'metal',.25,True)
        m.box('ShoulderActuator'+str(side),'L/R actuator tongue',3,3,1.0,(side*62,34.5,13.15),'Internal',1,'black',.2,True)
    # Spatially separated ribbon layers; the rolled segment remains in the hollow hinge.
    m.box('LowerLCDFlex','Lower LCD ribbon',18,11,.10,(-43,-21,14.8),'Internal',2,'copper',.25,True)
    m.box('LowerLCDZIF','Lower LCD locking connector',20,3,1.0,(-43,-27.3,13.55),'Internal',1,'black',.3,True)
    m.box('TouchFlex','Resistive touchscreen flex',4,13,.08,(33,-23,14.6),'Internal',2,'copper',.2,True)
    m.box('TouchZIF','Touchscreen flex latch',6,3,.7,(33,-30.5,13.55),'Internal',1,'white',.2,True)
    m.box('UpperLCDFlex','Upper LCD flex routing study',17,22,.10,(0,58,13.0),'LidInternal',-1,'copper',.3,True,'Lid')
    m.ring('HingeFlex','Rolled upper-display flex',1.24,1.08,18,(-18,38.5,19.5),'Internal',0,'copper',axis=(1,0,0),internal=True)
    for side in [-1,1]:m.box('SpeakerFlex'+str(side),'Speaker flex conductor study',27,2.2,.09,(side*40,54,13.0),'LidInternal',-1,'copper',.25,True,'Lid')
    m.box('UpperAntenna','Upper lid antenna strip',28,2.5,.10,(43,109,12.3),'LidInternal',-2,'gold',.2,True,'Lid')
    m.checkpoint(9,'button_membranes_and_display_flex','加入独立按键胶垫、导电粒和主板触点，系统键/肩键开关、麦克风、指示灯，以及双屏排线和中空铰链内的卷曲排线段。')


def stage10(m):
    mounts=[(-67,-30),(67,-30),(-67,28),(67,28),(0,-34),(0,35),(30,3)]
    for i,(x,y) in enumerate(mounts):
        m.ring('BoardPost'+str(i),'Mainboard locating post',1.7,.76,8.85,(x,y,1.65),'Internal',-3,'black',internal=True)
        bore=Part.makeCylinder(.78,1.3,V(x,y,10.7));m.cut('Mainboard',bore,'Mainboard mounting hole')
        m.screw('BoardScrew'+str(i),(x,y,12.15),'Mainboard',-2,length=3.2,radius=1.28,axis=(0,0,-1))
    # The upper LCD is supported by four screw towers under the visible pads.
    for i,(x,y) in enumerate([(-45,108),(45,108),(-45,51),(45,51)]):
        m.ring('LidPost'+str(i),'Upper cover screw tower',1.65,.74,6.6,(x,y,11.35),'LidInternal',-1,'shell',internal=True,pose='Lid')
        m.screw('LidScrew'+str(i),(x,y,19.05),'LidInternal',4,length=3.0,radius=1.18,pose='Lid',axis=(0,0,-1))
        m.cut('LidBezel',Part.makeCylinder(1.3,.65,V(x,y,18.7)),'Hidden upper screw recess')
    # A light steel LCD carrier preserves the large open cartridge passage below.
    plate=m.rr(72,56,.28,(0,4,14.60),1.1)
    plate=plate.cut(m.rr(60,44,.50,(0,4,14.5),.8))
    m.feature('LCDCarrier','Lower display carrier rim',plate,'Internal',1,'metal',True)
    shield=m.rr(48,35,.40,(0,4,13.4),1.0)
    m.feature('EMIShield','Main package shielding plate study',shield,'Internal',-1,'metal',True)
    m.checkpoint(10,'mounts_and_lcd_carrier','补齐主板定位柱与紧固螺钉、上盖四处螺钉塔、下屏金属承托边和主封装屏蔽板，进入实体配合检查。')

STAGES.update({6:stage06,7:stage07,8:stage08,9:stage09,10:stage10})
