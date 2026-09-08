"""Original 3DS / original DS structures, built in flat hinge coordinates."""
import math
import Part
import FreeCAD as App
from .core import V


def stage01(m):
    p=m.profile;w,h,B=p['width'],p['height'],p['base_depth'];fz=B-.8
    m.native('BackCover','Removable lower rear cover',w-1.2,h-1.2,5.0,1.0,(0,0,0),layer=-6)
    m.native('MainFrame','Lower structural side frame',w,h,5.6,B-2.9,(0,0,1.05),layer=0,expr={'Width':'Parameters.Width','Height':'Parameters.Height'})
    m.cut('MainFrame',m.rr(w-3.2,h-3.2,B,(0,0,.95),4.1),'Main electronics cavity')
    m.native('FrontDeck','Control deck',w-.4,h-.4,5.4,1.0,(0,0,fz-1.0),layer=4)
    # Dark perimeter joint and the original stepped side-wall outline.
    seam=m.rr(w-.15,h-.15,.055,(0,0,fz-1.07),5.45).cut(m.rr(w-3.4,h-3.4,.2,(0,0,fz-1.14),3.9))
    m.feature('LowerCaseSeam','Lower case parting line',seam,layer=0,material='black')
    m.checkpoint(1,'lower_enclosure','建立原生草图、凸台和圆角驱动的下机身、空腔、控制面板与分型缝。')


def stage02(m):
    p=m.profile;hy,hz=p['hinge_y'],p['hinge_z'];cy=2*hy;w,h=p['lid_width'],p['lid_height'];backz=2*hz-p['closed_depth']
    m.native('LidBackCover','Upper outer cover',w,h,5.0,.90,(0,cy,backz),'Lid',-6,'accent','Lid')
    m.native('LidFrame','Upper display frame',w-.25,h-.25,4.85,hz-backz-1.25,(0,cy,backz+.95),'Lid',0,'accent','Lid')
    m.cut('LidFrame',m.rr(w-3.2,h-3.2,hz-backz,(0,cy,backz+.85),3.5),'Upper display cavity')
    m.box('LidBezel','Black upper display bezel',w-.9,h-.9,.25,(0,cy,hz-.25),'Lid',5,'bezel',4.6,pose='Lid')
    # The rotation axis is common to all separate hinge sleeves.
    bore=Part.makeCylinder(3.02,p['width']+2,V(-p['width']/2-1,hy,hz),V(1,0,0))
    for key in ['MainFrame','FrontDeck','LidFrame','LidBezel']:m.cut(key,bore,'Hinge sleeve clearance')
    for key,x,length,pose in [('LeftHingeSleeve',-65.2,9.0,'Base'),('CenterHingeSleeve',-51.0,102.0,'Lid'),('RightHingeSleeve',56.2,9.0,'Base')]:
        m.ring(key,'Hinge knuckle',2.90,1.42,length,(x,hy,hz),'Hinge',0,'accent',axis=(1,0,0),pose=pose)
    m.cyl('HingeAxle','Continuous hinge pin',1.32,127.5,(-63.75,hy,hz),'Hinge',0,'metal',axis=(1,0,0),internal=True)
    for side in [-1,1]:m.ring('HingeWasher'+str(side),'Hinge end bearing washer',2.7,1.38,.45,(side*53.8-.225,hy,hz),'Hinge',0,'black',axis=(1,0,0))
    # Two different physical display sizes, including the resistive lower touch layer.
    for name,ww,hh,yy,z,pose,assembly in [('Lower',*p['lower_display'],p['lower_display_y'],p['base_depth']-.8,'Base','Display'),('Upper',*p['upper_display'],p['upper_display_y'],hz,'Lid','LidDisplay')]:
        if name=='Lower':
            m.cut('FrontDeck',m.rr(ww+10.4,hh+9.4,1.8,(0,yy,z-1.2),1.3),'Lower display surround seat')
            frame=m.rr(ww+10.1,hh+9.1,.50,(0,yy,z-.35),1.2).cut(m.rr(ww+.10,hh+.10,.8,(0,yy,z-.5),.2))
            m.feature('LowerDisplaySurround','Lower touch-panel frame',frame,assembly,5,'bezel',False,pose)
        else:m.cut('LidBezel',m.rr(ww+.12,hh+.12,.5,(0,yy,z-.35),.3),'Upper 3D LCD aperture')
        m.box(name+'LCD','LCD module',ww+6.0,hh+5.0,2.65,(0,yy,z-3.3),assembly,2,'black',1.0,True,pose)
        m.box(name+'LCDBackplate','LCD metal backplate',ww+6.0,hh+5.0,.24,(0,yy,z-3.60),assembly,1,'metal',1.0,True,pose)
        if name=='Lower':
            m.box('LowerTouchDigitizer','Resistive touch layer',ww,hh,.075,(0,yy,z-.07),assembly,6,'screen',.15,False,pose)
            m.box('LowerGlass','Lower screen cover',ww,hh,.125,(0,yy,z+.005),assembly,7,'screen',.15,False,pose)
        else:
            m.box('ParallaxBarrier','3D parallax film layout',ww,hh,.04,(0,yy,z-.245),assembly,6,'screen',.2,True,pose)
            m.box('UpperGlass','Upper display window',ww,hh,.165,(0,yy,z-.195),assembly,7,'screen',.2,False,pose)
    m.checkpoint(2,'dual_displays_and_hinge','建立铰链套、通轴和轴承垫，加入上下 LCD、金属背板、下屏触控层及上屏立体显示膜层。')


def stage03(m):
    p=m.profile;fz=p['base_depth']-.8
    # Circle Pad is a distinctive 3DS control; its cap is recessed into a dedicated bezel.
    m.cut('FrontDeck',Part.makeCylinder(9.1,3,V(-50,14,fz-1.6)),'Circle Pad clearance')
    m.ring('CirclePadBezel','Circle Pad black annular surround',9.0,7.05,.55,(-50,14,fz-.35),'Controls',5,'black')
    cap=Part.makeCylinder(6.85,.80,V(-50,14,fz-.05));cap=cap.makeFillet(.25,[e for e in cap.Edges if e.BoundBox.ZLength<1e-6])
    m.feature('CirclePadCap','Circle Pad rubber cap',cap,'Controls',6,'white')
    m.cyl('CirclePadStem','Circle Pad transmission stem',2.3,2.8,(-50,14,fz-3.0),'Controls',3,'black',internal=True)
    # One connected D-pad with separately modeled rubber and switch contacts below.
    x,y=-50,-13
    cross=m.rr(6.0,17.0,1.45,(x,y,fz-.72),.65).fuse(m.rr(17.0,6.0,1.45,(x,y,fz-.72),.65)).removeSplitter()
    m.feature('DPad','Directional cross',cross,'Controls',6,'black')
    tool=m.rr(6.35,17.35,2.2,(x,y,fz-1.1),.7).fuse(m.rr(17.35,6.35,2.2,(x,y,fz-1.1),.7))
    m.cut('FrontDeck',tool,'Directional pad opening')
    for j,(dx,dy) in enumerate([(0,5.9),(5.9,0),(0,-5.9),(-5.9,0)]):
        bar=m.rr(.40,2.2,.018,(x+dx,y+dy,fz+.745),.08)
        if dx:bar.rotate(V(x+dx,y+dy,0),V(0,0,1),90)
        m.feature('DPadMark'+str(j),'Directional key tick',bar,'Controls',6,'rubber')
    for j,(dx,dy,ch) in enumerate([(0,6.8,'X'),(6.8,0,'A'),(0,-6.8,'B'),(-6.8,0,'Y')]):
        x,y=49+dx,4+dy;m.cut('FrontDeck',Part.makeCylinder(3.47,2.2,V(x,y,fz-1.1)),'Face key bore')
        cap=Part.makeCylinder(3.30,1.35,V(x,y,fz-.65));cap=cap.makeFillet(.18,[e for e in cap.Edges if e.BoundBox.ZLength<1e-6])
        m.feature('Button'+ch,ch+' button',cap,'Controls',6,'black')
        m.label('ButtonMark'+ch,ch,2.25,(x-.9,y-1.0,fz+.716),'Controls',6,'white')
        m.cyl('ButtonStem'+ch,'Face key plunger',1.4,2.45,(x,y,fz-3.15),'Controls',3,'black',internal=True)
    for i,(x,label) in enumerate([(-21,'SELECT'),(0,'HOME'),(21,'START')]):
        m.cut('FrontDeck',m.rr(16.4,4.1,1.6,(x,-32.0,fz-.95),.65),'Menu key seat')
        m.box('MenuKey'+str(i),label+' menu key',16,3.7,.88,(x,-32.0,fz-.45),'Controls',6,'accent',.5)
        m.label('MenuLabel'+str(i),label,1.4,(x-4.6,-32.65,fz+.445),'Controls',6,'white')
    m.cut('FrontDeck',m.rr(5.0,4.7,1.5,(48,-28.5,fz-.95),.9),'Power key seat')
    m.box('PowerKey','Power key',4.7,4.4,1.05,(48,-28.5,fz-.55),'Controls',6,'black',.8)
    m.label('PowerLegend','POWER',1.2,(51.4,-29.0,fz+.025),'Body',4,'white')
    m.checkpoint(3,'circle_pad_and_controls','完成圆形滑控钮、十字键、ABXY、SELECT/HOME/START 和电源键，各按键与安装孔分离建模。')


def stage04(m):
    p=m.profile;w,h=p['width'],p['height'];fy=h/2;fz=p['base_depth']-.8
    ry=App.Rotation(V(0,0,1),V(0,1,0));rx=App.Rotation(V(0,0,1),V(1,0,0))
    # Rear charging jack and two exposed dock contacts.
    m.cut('MainFrame',m.rr(8.8,4.1,3.8,(39,fy-2.0,7.5),.9,ry),'Charge-jack opening')
    shell=m.rr(8.25,3.65,5.0,(39,fy-5.0,7.5),.7,ry).cut(m.rr(6.65,2.1,5.3,(39,fy-5.1,7.5),.4,ry))
    m.feature('ChargeJackShell','Proprietary charging socket',shell,'Ports',0,'metal')
    m.box('ChargeJackTongue','Charging socket insulator',5.7,.8,3.9,(39,fy-4.6,7.5),'Ports',0,'black',.2,orient=ry)
    for i,x in enumerate([32.1,45.9]):
        pad=m.rr(1.7,3.3,.25,(x,fy-.20,7.5),.3,ry);m.cut('MainFrame',pad,'Charging cradle contact recess');m.feature('DockContact'+str(i),'External charging contact',pad,'Ports',0,'gold')
    # Game-card cage sits below the hinge; 17 independent contacts inside.
    m.cut('MainFrame',m.rr(35.4,4.6,3.3,(0,fy-2,6.3),.8,ry),'Game-card mouth')
    cage=m.rr(35.0,24,3.1,(0,fy-12.1,4.72),1.2).cut(m.rr(33.2,25,2.0,(0,fy-11.9,5.22),.7))
    m.feature('GameCardCage','Game-card socket cage',cage,'Ports',0,'metal',True)
    m.box('GameCardMouth','Black game-card lip',34.8,4.2,.24,(0,fy-.28,6.3),'Ports',0,'black',.6,orient=ry)
    m.cut('GameCardMouth',m.rr(32.8,2.7,.6,(0,fy-.38,6.3),.45,ry),'Card insertion slot')
    for j in range(17):m.box('CardContact'+str(j),'Game-card gold contact',.55,6,.09,(-12+j*1.5,fy-15,5.30),'Ports',0,'gold',.02,True)
    # Infrared window and telescoping stylus entrance beside the card slot.
    m.box('IRWindow','Infrared window',8.5,3.5,.4,(-39,fy-.4,7.2),'Ports',0,'screen',.6,orient=ry)
    m.cut('MainFrame',m.parts['IRWindow'].Shape,'Infrared window seat')
    m.cut('MainFrame',Part.makeCylinder(2.25,4,V(-25,fy-3,7.1),V(0,1,0)),'Stylus entrance')
    m.ring('StylusEntrance','Stylus slot mouth',2.12,1.55,1.0,(-25,fy-1.05,7.1),'Ports',0,'black',axis=(0,1,0))
    # Bottom 3.5 mm audio socket and tiny indicator windows.
    m.cut('MainFrame',Part.makeCylinder(2.45,4,V(0,-fy-1,6.0),V(0,1,0)),'Headphone socket hole')
    m.ring('HeadphoneSocket','3.5 mm audio socket',2.30,1.76,5.4,(0,-fy+.05,6),'Ports',0,'metal',axis=(0,1,0))
    m.ring('HeadphoneInsulator','Audio connector insulator',1.72,1.55,1.0,(0,-fy+.2,6),'Ports',0,'black',axis=(0,1,0))
    for i,(x,color) in enumerate([(56,'blue'),(61,'red')]):
        window=m.rr(2.5,1.0,.35,(x,-fy+.35,7.2),.18,App.Rotation(V(0,0,1),V(0,-1,0)))
        m.cut('MainFrame',window,'Front-edge LED window');m.feature('StatusLED'+str(i),'Status indicator window',window,'Ports',0,color)
    # Side SD door, volume slider and right wireless switch.
    m.box('SDDoor','SD card side door',5.7,29,.65,(-w/2+.05,-13,6.0),'Ports',0,'accent',.9,orient=rx)
    m.cut('MainFrame',m.parts['SDDoor'].Shape,'SD card cover recess')
    m.box('VolumeSlider','Volume side slider',2.8,9,.75,(-w/2+.05,16,7),'Controls',0,'black',.7,orient=rx)
    m.cut('MainFrame',m.parts['VolumeSlider'].Shape,'Volume slider recess')
    m.box('WirelessSlider','Wireless side switch',2.8,7,.75,(w/2-.8,-12,7),'Controls',0,'black',.7,orient=rx)
    m.cut('MainFrame',m.parts['WirelessSlider'].Shape,'Wireless slider recess')
    m.checkpoint(4,'connectors_and_card_slots','加入充电插孔与底座触点、卡槽与 17 触点、红外窗、触控笔入口、耳机孔、指示灯和侧面开关。')


def stage05(m):
    p=m.profile;hy,hz=p['hinge_y'],p['hinge_z'];cy=2*hy;backz=2*hz-p['closed_depth']
    # The original 3DS has five visible holes in each stereo speaker cluster.
    for side in [-1,1]:
        x=side*51;y=cy
        holes=[Part.makeCylinder(.62,.7,V(x+dx,y+dy,hz-.45)) for dx,dy in [(-1.7,1.7),(1.7,1.7),(0,0),(-1.7,-1.7),(1.7,-1.7)]]
        m.cut('LidBezel',holes,'Five-hole stereo speaker cluster')
        m.ring('SpeakerFrame'+str(side),'Upper stereo speaker housing',6.7,5.5,2.0,(x,y,hz-3.7),'LidInternal',0,'metal',internal=True,pose='Lid')
        m.cyl('SpeakerMagnet'+str(side),'Speaker magnet',3.8,1.50,(x,y,hz-3.45),'LidInternal',0,'metal',internal=True,pose='Lid')
        m.cyl('SpeakerDiaphragm'+str(side),'Speaker diaphragm',5.45,.10,(x,y,hz-1.62),'LidInternal',0,'black',internal=True,pose='Lid')
        m.box('SpeakerGasket'+str(side),'Speaker acoustic gasket',14.2,14.2,.35,(x,y,hz-1.2),'LidInternal',2,'rubber',2.0,True,'Lid')
        m.cut('SpeakerGasket'+str(side),Part.makeCylinder(5.4,.6,V(x,y,hz-1.3)),'Speaker outlet')
    front_y=cy+p['lid_height']/2-7.3
    m.cut('LidBezel',Part.makeCylinder(2.28,.7,V(0,front_y,hz-.5)),'Inner camera aperture')
    m.ring('InnerCameraRing','Inner camera ring',2.12,1.60,.27,(0,front_y,hz-.28),'Lid',5,'black',pose='Lid')
    m.cyl('InnerCameraLens','Inner camera glass',1.55,.14,(0,front_y,hz-.16),'Lid',5,'screen',pose='Lid')
    for side in [-1,1]:
        x=side*17.5
        m.cut('LidBackCover',Part.makeCylinder(2.28,1.3,V(x,front_y,backz-.15)),'Stereo outer camera bore')
        m.ring('OuterCameraRing'+str(side),'Outer stereo camera ring',2.15,1.60,.30,(x,front_y,backz+.02),'Lid',-6,'black',pose='Lid')
        m.cyl('OuterCameraLens'+str(side),'Outer stereo camera glass',1.55,.14,(x,front_y,backz+.035),'Lid',-6,'screen',pose='Lid')
    # 3D slider on the right edge of the upper bezel; microphone on lower deck.
    m.cut('LidBezel',m.rr(2.6,14,.6,(61,cy-12,hz-.45),.7),'3D control slider track')
    m.box('DepthSliderTrack','3D slider track',2.3,13.7,.22,(61,cy-12,hz-.3),'Lid',5,'black',.65,pose='Lid')
    m.box('DepthSlider','3D depth thumb slider',3.4,4.6,.65,(61,cy-14,hz-.12),'Lid',6,'metal',.8,pose='Lid')
    m.label('DepthLegend','3D',1.5,(59.7,cy-3,hz+.02),'Lid',6,'white','Lid')
    m.label('DepthOffLegend','OFF',1.0,(59.2,cy-21,hz+.02),'Lid',6,'white','Lid')
    m.cut('FrontDeck',Part.makeCylinder(.55,1.5,V(34,-25,p['base_depth']-2)),'Microphone aperture')
    m.cyl('MicrophoneMesh','Microphone inlet mesh',.48,.12,(34,-25,p['base_depth']-1.0),'Ports',4,'black')
    m.checkpoint(5,'stereo_cameras_speakers_and_3d_slider','增加两组五孔扬声器、内侧摄像头和双外摄像头、3D 强度滑块及麦克风入口。')

STAGES={1:stage01,2:stage02,3:stage03,4:stage04,5:stage05}


def stage06(m):
    p=m.profile;w,h=p['width'],p['height'];B=p['base_depth'];hy,hz=p['hinge_y'],p['hinge_z']
    # Removable back cover, rear support plate and four captive service fasteners.
    support=m.rr(w-3.6,h-3.6,.50,(0,0,1.14),4.0).cut(m.rr(35.4,55.4,.8,(43,-1,1.0),1.2))
    m.feature('RearSupportPlate','Rear support plate with battery opening',support,'Internal',-5,'metal',True)
    for i,x in enumerate([-54,-34,34,54]):
        y=30.3
        bore=Part.makeCylinder(.72,4,V(x,y,-.1));head=Part.makeCylinder(1.38,.48,V(x,y,-.05))
        m.cut('BackCover',[bore,head],'Captive rear-cover screw seat');m.cut('RearSupportPlate',bore,'Service-screw clearance')
        m.screw('RearCoverScrew'+str(i),(x,y,.05),'Body',-6,length=2.8,radius=1.24)
    for i,(x,y) in enumerate([(-57,-28),(57,-28),(-57,24),(57,24)]):
        pad=m.rr(5.0,2.8,.15,(x,y,.025),.55);m.cut('BackCover',pad,'Rear rubber pad inset');m.feature('RearPad'+str(i),'Rear rubber contact pad',pad,'Body',-6,'black')
    m.label('RearModelMark','CTR-001  /  CAD STUDY',1.65,(24,-15,.024),'Body',-6,'white',rotation=App.Rotation(V(0,1,0),180))
    m.cut('BackCover',m.parts['RearModelMark'].Shape,'Rear marking inlay')
    # L/R shoulders and their separate pivot pins.
    for side in [-1,1]:
        x=side*57.5
        bumper=m.rr(17.7,7.0,4.0,(x,h/2-3.6,7.3),1.8)
        m.feature('Shoulder'+str(side),'L/R shoulder cap',bumper,'Controls',0,'accent')
        m.cut('MainFrame',bumper,'Shoulder-button seat')
        m.cyl('ShoulderPin'+str(side),'Shoulder pivot',.62,13,(x-6.5,h/2-6.5,8.8),'Internal',0,'metal',axis=(1,0,0),internal=True)
        m.label('ShoulderMark'+str(side),'L' if side<0 else 'R',2.0,(x-.7,h/2-3.8,11.315),'Controls',0,'white')
    # Retracted telescoping stylus, shown as a separate accessory.
    x=-86;y=-36.0
    m.ring('StylusOuter','Telescoping stylus barrel',1.5,1.13,47,(x,y,3.2),'Accessories',0,'metal',axis=(0,1,0))
    m.cyl('StylusInner','Telescoping inner rod',1.05,20,(x,y+47,3.2),'Accessories',1,'metal',axis=(0,1,0))
    m.cyl('StylusGrip','Stylus cap',1.7,5,(x,y+67,3.2),'Accessories',1,'black',axis=(0,1,0))
    cone=Part.makeCone(.16,1.5,3,V(x,y-3,3.2),V(0,1,0));m.feature('StylusTip','Stylus tip',cone,'Accessories',-1,'black')
    m.checkpoint(6,'rear_cover_and_stylus','补齐后盖、带电池开口的支承板、固定螺钉、防滑垫、L/R 肩键及独立伸缩触控笔。')


def stage07(m):
    # CTR-003 sits vertically along the right side when viewed from the front.
    m.box('BatteryPouch','CTR-003 battery pouch',33.6,52.6,4.85,(43,-1,1.85),'Battery',-4,'battery',1.3,True)
    m.cut('BatteryPouch',m.rr(32.3,51.3,4.15,(43,-1,2.20),.9),'Battery cell cavity')
    m.box('BatteryCell','Battery cell stack layout',32.0,51.0,3.85,(43,-1,2.35),'Battery',-4,'rubber',.75,True)
    tray=m.rr(35.0,54.0,.25,(43,-1,1.68),1.1).cut(m.rr(31.4,50.4,.45,(43,-1,1.58),.6))
    m.feature('BatteryTray','Battery locating tray',tray,'Battery',-5,'black',True)
    m.box('BatteryConnector','Battery connector body',10.5,2.8,1.7,(43,-29.0,2.3),'Battery',-4,'white',.3,True)
    for j in range(3):m.box('BatteryContact'+str(j),'Battery terminal',.85,2.0,.08,(40.5+j*2.5,-28.8,4.03),'Battery',-4,'gold',.02,True)
    rear=App.Rotation(V(0,1,0),180)
    m.label('BatteryType','CTR-003',2.3,(53,10,1.83),'Battery',-4,'white',rotation=rear)
    m.label('BatteryCapacity','1300 mAh  /  5 Wh',1.7,(56,3,1.83),'Battery',-4,'white',rotation=rear)
    m.label('BatteryStudy','LAYOUT STUDY',1.45,(54,-8,1.83),'Battery',-4,'white',rotation=rear)
    # Additional rear stiffening ribs avoid the battery aperture.
    for i,(x,y,ww,hh) in enumerate([(-48,18,2.0,27),(-48,-17,2.0,20),(-13,-29,65,1.5),(10,17,1.5,27)]):
        m.box('RearRib'+str(i),'Rear support rib',ww,hh,.65,(x,y,1.7),'Internal',-5,'shell',.25,True)
    m.checkpoint(7,'battery_and_rear_support','加入竖置 CTR-003 电池、内层电芯、定位托架、三端接点及后部支承肋，按拆解布局保留电池开口。')


def stage08(m):
    board=m.rr(126.0,64.0,.75,(0,0,6.95),2.0)
    board=board.cut(m.rr(24,24,1.2,(-55,17,6.75),2.0))
    board=board.cut(m.rr(36.4,25.3,1.2,(0,25.0,6.75),1.4))
    for key in ['HeadphoneSocket','ChargeJackShell']:board=board.cut(m.parts[key].Shape)
    m.feature('Mainboard','CTR mainboard outline study',board,'Mainboard',-2,'pcb',True)
    chips=[('ARM',-11,8,18,18,1.15),('RAM',13,9,13,13,1.00),('NAND',-31,-17,14,14,.95),('PMIC',-6,-19,8,8,.80),('AudioIC',15,-23,5,6,.65)]
    for key,x,y,w,h,t in chips:m.box(key+'Package',key+' package',w,h,t,(x,y,6.85-t),'Mainboard',-2,'black',.35,True)
    rear=App.Rotation(V(0,1,0),180)
    m.label('ARMLabel','ARM',2.1,(-6,7,5.68),'Mainboard',-2,'white',rotation=rear)
    m.box('WiFiBoard','Removable Wi-Fi module PCB',20,18,.50,(-40,-12,4.1),'Mainboard',-3,'pcb',.7,True)
    m.box('WiFiShield','Wi-Fi module shield',18.6,16.6,.35,(-40,-12,3.67),'Mainboard',-3,'metal',.7,True)
    m.box('IRBoard','Infrared daughterboard',9,6,.5,(-39,30,5.0),'Mainboard',-2,'pcb',.4,True)
    m.box('IRReceiver','Infrared receiver',5.5,3.0,1.1,(-39,33.5,5.65),'Mainboard',-2,'black',.35,True)
    m.box('SDReaderPCB','Removable SD-reader daughterboard',24,29,.60,(-51,-12,2.7),'Mainboard',-3,'pcb',.7,True)
    cage=m.rr(22,26,2.35,(-51,-12,3.38),.7).cut(m.rr(23,24.2,1.7,(-51.5,-12,3.70),.35))
    m.feature('SDReaderCage','SD card-reader metal cage',cage,'Mainboard',-3,'metal',True)
    m.box('SDCard','SD memory-card study',20.7,23.5,1.25,(-51.6,-12,3.95),'Mainboard',-3,'blue',.35,True)
    for j in range(9):m.box('SDContact'+str(j),'SD-reader terminal',.65,3.7,.08,(-59+j*1.9,-2,3.79),'Mainboard',-3,'gold',.02,True)
    # Components are distributed in clear board regions; no decorative random fill.
    points=[(x,-29) for x in [-51,-42,-30,-21,-12,-3,7,17]]+[(x,28) for x in [-49,-39,27,37,47,57]]+[(x,-5) for x in [-24,-15,-6,5,16]]+[(22,y) for y in [-22,-13,6,17]]
    for i,(x,y) in enumerate(points):
        m.box('Passive'+str(i),'Surface-mount passive body',1.15,.80,.52,(x,y,6.29),'Mainboard',-2,'rubber',.025,True)
        for side in [-1,1]:m.box(f'Passive{i}End{side}','Solder termination',.23,.86,.55,(x+side*.72,y,6.28),'Mainboard',-2,'metal',.015,True)
    m.checkpoint(8,'mainboard_and_daughterboards','建立带缺口的主板、ARM/RAM/NAND 和电源音频封装、独立 Wi-Fi/红外/SD 模块，以及可分辨的阻容器件和端帽。')


def stage09(m):
    p=m.profile;fz=p['base_depth']-.8;hy,hz=p['hinge_y'],p['hinge_z'];cy=2*hy
    m.ring('CirclePadHousing','Circle Pad mechanism housing',8.7,3.0,2.5,(-50,14,8.1),'Internal',2,'black',internal=True)
    m.ring('CirclePadBearing','Circle Pad sliding bearing',6.1,2.65,.30,(-50,14,10.65),'Internal',3,'metal',internal=True)
    m.box('CirclePadPCB','Circle Pad sensor PCB',19.0,19.0,.45,(-50,14,7.50),'Internal',1,'pcb',1.3,True)
    m.cut('CirclePadPCB',Part.makeCylinder(2.6,.8,V(-50,14,7.3)),'Stick shaft passage')
    for j,(x,y,w,h) in enumerate([(-50,23.8,10,1.2),(-59.8,14,1.2,10)]):m.box('CirclePadSensor'+str(j),'Analog position sensor study',w,h,1.2,(x,y,8.2),'Internal',2,'rubber',.25,True)
    # The D-pad and face buttons have separate silicone pads and conducting pills.
    for key,positions in [('DPad',[(-50, -13+5.9),(-50+5.9,-13),(-50,-13-5.9),(-50-5.9,-13)]),('Face',[(49,10.8),(55.8,4),(49,-2.8),(42.2,4)])]:
        for j,(x,y) in enumerate(positions):
            m.cyl(key+'Rubber'+str(j),'Button silicone cup',2.5,.8,(x,y,8.45),'Internal',1,'rubber',internal=True)
            m.cyl(key+'Pill'+str(j),'Button contact pill',1.55,.16,(x,y,8.20),'Internal',1,'black',internal=True)
            m.cyl(key+'GoldPad'+str(j),'PCB button contact',2.05,.055,(x,y,7.84),'Internal',0,'gold',internal=True)
    # Upper lid camera boards and the shared flex follow the visible lenses.
    camera_y=cy+p['lid_height']/2-7.3;backz=2*hz-p['closed_depth']
    for key,x,z in [('Inner',0,hz-2.0),('OuterLeft',-17.5,backz+1.2),('OuterRight',17.5,backz+1.2)]:
        m.box(key+'CameraPCB','Camera sensor board',5.6,5.6,.40,(x,camera_y,z),'LidInternal',1,'pcb',.5,True,'Lid')
        m.box(key+'CameraSensor','Camera sensor package',4.1,4.1,.7,(x,camera_y,z+.45),'LidInternal',1,'black',.35,True,'Lid')
    m.box('CameraFlex','Shared camera flexible circuit',42,2.7,.09,(0,camera_y,8.85),'LidInternal',1,'copper',.3,True,'Lid')
    for side in [-1,1]:m.box('SpeakerFlex'+str(side),'Upper speaker flexible circuit',37,2.6,.08,(side*30,cy-29,8.75),'LidInternal',0,'copper',.3,True,'Lid')
    m.box('UpperAntenna','Upper wireless antenna strip',23,3.0,.10,(-44,cy+29,8.7),'LidInternal',0,'gold',.3,True,'Lid')
    m.box('UpperLCDDriver','Upper LCD driver flex',47,4.2,.10,(0,cy-28,9.45),'LidInternal',1,'copper',.3,True,'Lid')
    m.box('LowerLCDFlex','Lower display ribbon',18,8,.10,(4,-25,8.12),'Internal',1,'copper',.25,True)
    m.box('CirclePadFlex','Circle Pad flex tail',3.5,15,.10,(-38,13,8.0),'Internal',1,'copper',.25,True)
    m.box('SDFlex','SD-reader flex tail',8,7,.08,(-44,-29,6.76),'Internal',0,'copper',.3,True)
    m.box('BatteryFlex','Battery terminal interconnect',4,5,.10,(43,-29,4.4),'Internal',-3,'copper',.25,True)
    # Flex through the hollow hinge is represented by an annular rolled segment.
    m.ring('HingeFlex','Rolled hinge flex routing study',1.23,1.08,18,(-45,hy,hz),'Internal',0,'copper',axis=(1,0,0),internal=True)
    m.checkpoint(9,'control_mechanisms_and_flex','补齐滑控钮机构、硅胶按键与导电接点、三摄像头小板、扬声器/显示排线及穿过空心铰链的卷绕排线。')


def stage10(m):
    p=m.profile;hy,hz=p['hinge_y'],p['hinge_z'];cy=2*hy
    # Structural mounting posts and corresponding PCB bores.
    for i,(x,y) in enumerate([(-59,-28),(-23,-27),(20,-28),(59,-28),(-57,29),(24,29),(58,29)]):
        m.cut('Mainboard',Part.makeCylinder(.72,1.2,V(x,y,6.7)),'Mainboard mounting hole')
        m.ring('BoardPost'+str(i),'Mainboard support post',1.50,.70,3.5,(x,y,3.15),'Internal',-2,'shell',internal=True)
        m.screw('BoardScrew'+str(i),(x,y,2.70),'Internal',-3,length=4.0,radius=1.25)
        if 'RearSupportPlate' in m.parts:m.cut('RearSupportPlate',Part.makeCylinder(1.5,.9,V(x,y,1.0)),'Rear plate boss clearance')
    # A thin grounded shield leaves battery, daughterboard and rear connector clear.
    shield=m.rr(72,54,.22,(-10,-1,3.0),1.8)
    for key in ['WiFiShield','WiFiBoard','SDReaderCage','SDReaderPCB','HeadphoneSocket']:shield=shield.cut(m.parts[key].Shape)
    shield=shield.cut(m.rr(28,24,.5,(-41,-13,2.9),1.0))
    m.feature('EMIShield','Lower EMI shield layout',shield,'Internal',-4,'metal',True)
    # Display mounting lugs and screws are beneath the upper front bezel.
    positions=[(-60,cy-28),(60,cy-28),(-60,cy+28),(-29,cy+28),(29,cy+28),(60,cy+28)]
    for i,(x,y) in enumerate(positions):
        m.ring('LidPost'+str(i),'Upper display mounting post',1.45,.69,3.0,(x,y,8.7),'LidInternal',0,'shell',internal=True,pose='Lid')
        m.screw('LidScrew'+str(i),(x,y,12.30),'LidInternal',1,length=3.0,radius=1.18,pose='Lid',axis=(0,0,-1))
    m.box('MicrophonePCB','Microphone PCB',4.2,5.0,.5,(34,-25,7.85),'Internal',1,'pcb',.3,True)
    m.cyl('MicrophoneCapsule','Microphone capsule',1.5,1.1,(34,-25,8.40),'Internal',2,'metal',internal=True)
    # Elastomer pads between the display frames and their case supports.
    for side in [-1,1]:
        m.box('LowerScreenFoam'+str(side),'Lower LCD side foam',1.2,43,.25,(side*34.5,-2,9.0),'Internal',2,'black',.2,True)
        m.box('UpperScreenFoam'+str(side),'Upper LCD side foam',1.3,42,.25,(side*42.5,cy,9.35),'LidInternal',2,'black',.2,True,'Lid')
    m.checkpoint(10,'fasteners_shielding_and_mounts','建立主板孔与支柱、上下层紧固件、上屏安装柱、EMI 屏蔽片、麦克风组件和显示缓冲垫。')

STAGES.update({6:stage06,7:stage07,8:stage08,9:stage09,10:stage10})


def _replace(m,key,shape):
    assert shape.isValid() and not shape.isNull() and shape.Solids,key
    o=m.parts[key];o.Shape=shape;o.FlatPlacement=o.Placement


def _move(m,key,delta):
    o=m.parts[key];p=o.FlatPlacement;p.Base=p.Base+V(*delta);o.FlatPlacement=p;o.Placement=p


def fit_hinge(m):
    m.set_pose(180)
    p=m.profile;oldhy=p['hinge_y'];hy=oldhy-.9;hz=p['hinge_z']
    # The published height includes the hinge radius, so its axis must be inset.
    for key,o in list(m.parts.items()):
        if o.Assembly=='Hinge' or key=='HingeFlex':_move(m,key,(0,-.9,0))
        elif o.PoseGroup=='Lid':_move(m,key,(0,-1.8,0))
    p['hinge_y']=hy;p['upper_display_y']-=1.8
    cylinder=Part.makeCylinder(3.04,p['width']+2,V(-p['width']/2-1,hy,hz),V(1,0,0))
    for key in ['MainFrame','FrontDeck','LidFrame','LidBezel']:m.cut(key,cylinder,'Revised hinge-axis clearance')
    # Sampled rotational clearance volume of the closed lower-console envelope.
    # It removes only the leading-edge material that enters the lower case.
    swept=[]
    base=Part.makeBox(p['width']+.04,p['height']+.04,12.92,V(-p['width']/2-.02,-p['height']/2-.02,-.1))
    for theta in range(20,181,10):
        t=App.Placement(V(),App.Rotation(V(1,0,0),theta),V(0,hy,hz)).inverse()
        tool=base.copy();tool.Placement=t.multiply(tool.Placement);swept.append(tool)
    clearance=swept[0].multiFuse(swept[1:]).removeSplitter();assert clearance.isValid()
    for key in ['LidFrame','LidBackCover','LidBezel']:m.cut(key,clearance,'Upper-case rotational leading-edge clearance')
    fz=p['base_depth']-.8
    seam=m.rr(p['width']-.15,p['height']-.15,.030,(0,0,fz-1.04),5.45).cut(m.rr(p['width']-3.4,p['height']-3.4,.15,(0,0,fz-1.09),3.9))
    _replace(m,'LowerCaseSeam',seam);m.cut('LowerCaseSeam',cylinder,'Hinge gap in parting strip')
    for side in [-1,1]:
        key='Shoulder'+str(side);m.cut(key,[cylinder,m.parts['ShoulderPin'+str(side)].Shape],'Shoulder hinge and pivot bores')
        for frame in ['FrontDeck','LowerCaseSeam','Mainboard']:m.cut(frame,m.parts[key].Shape,'Rear shoulder seat clearance')
        o=m.parts['ShoulderMark'+str(side)];place=App.Placement(V(side*57.5-.7,p['height']/2-.09,9.5),App.Rotation(V(1,0,0),-90));o.FlatPlacement=place;o.Placement=place
    # Split the otherwise continuous shaft where the camera/display flex is rolled.
    m.cut('HingeAxle',Part.makeCylinder(1.38,19.0,V(-45.5,hy,hz),V(1,0,0)),'Hollow flex-routing section between hinge axles')
    m.parts['HingeAxle'].Label='Split hinge axle pair around flex conduit'


def fit_electronics(m):
    # Place the wireless board in its own rear layer, clear of the SD reader.
    for key in ['WiFiBoard','WiFiShield']:_move(m,key,(22,0,0))
    m.cut('Mainboard',m.rr(20.0,20.0,1.2,(-50,14,6.8),1.4),'Circle Pad daughterboard clearance')
    # Room for the lower microphone beside the display, not through the LCD edge.
    for key in ['MicrophoneMesh','MicrophonePCB','MicrophoneCapsule']:_move(m,key,(4,0,0))
    m.cut('FrontDeck',Part.makeCylinder(.55,2.0,V(38,-25,10.5)),'Repositioned microphone inlet')
    for side in [-1,1]:
        key='OuterLeft' if side<0 else 'OuterRight';o=m.parts[key+'CameraSensor'];o.Shape=m.rr(4.1,4.1,.70,(side*17.5,2*m.profile['hinge_y']+m.profile['lid_height']/2-7.3,5.25),.35);o.FlatPlacement=o.Placement
    # The inner camera carrier is notched where it meets the upper LCD frame.
    m.cut('InnerCameraPCB',m.parts['UpperLCD'].Shape,'Upper-camera PCB display-frame clearance')
    # Button plungers enter actual bores in their silicone cups.
    for j,ch in enumerate(['X','A','B','Y']):m.cut('FaceRubber'+str(j),m.parts['ButtonStem'+ch].Shape,'Plunger locating bore')
    # Card lip overlaps the cage only at its mounting rebate.
    m.cut('GameCardCage',m.parts['GameCardMouth'].Shape,'Card-mouth mounting rebate')
    for key in ['ARMPackage','RAMPackage']:m.cut('GameCardCage',m.parts[key].Shape,'Card-cage package clearance')
    m.cut('LidBezel',m.parts['DepthSlider'].Shape,'3D slider thumb travel opening')
    m.cut('DepthSliderTrack',m.parts['DepthSlider'].Shape,'3D slider carriage seat')
    # Battery tray supports the pouch without penetrating its outer skin.
    m.cut('BatteryTray',m.parts['BatteryPouch'].Shape,'Battery pouch locating rebate')
    m.cut('BatteryPouch',m.parts['BatteryFlex'].Shape,'Battery terminal-flex recess')
    for key in ['BoardPost3','BoardScrew3']:_move(m,key,(3,-2,0))
    m.cut('Mainboard',Part.makeCylinder(.73,1.2,V(62,-30,6.8)),'Relocated battery-side mounting hole')
    for key in ['Passive1','Passive1End-1','Passive1End1']:_move(m,key,(0,2.5,0))
    for key in ['Passive13','Passive13End-1','Passive13End1']:_move(m,key,(-3,0,0))
    m.cut('EMIShield',[m.parts[k].Shape for k in ['BoardPost1','BoardScrew1','BoardPost2','BoardScrew2']],'Shield mounting-fastener clearances')


def stage11(m):
    fit_hinge(m);fit_electronics(m)
    m.checkpoint(11,'verified_interface_refinement','按实体求交结果调整铰链轴与上盖旋转空间，修正肩键、卡槽、滑块、电池、主板、排线和安装件配合。')

STAGES[11]=stage11


def stage12(m):
    p=m.profile;hy,hz=p['hinge_y'],p['hinge_z'];cy=2*hy
    # Resolve the remaining measured interfaces and keep the public closed envelope.
    for i in range(2):
        key='DockContact'+str(i);_move(m,key,(0,-.06,0));m.cut('MainFrame',m.parts[key].Shape,'Flush charging-contact seat')
    for side in [-1,1]:
        key='ShoulderMark'+str(side);_move(m,key,(0,.072,0));m.cut('MainFrame',m.parts[key].Shape,'Flush rear L/R legend')
    for key in ['Passive1','Passive1End-1','Passive1End1']:_move(m,key,(0,3.0,0))
    for side in [-1,1]:
        key='OuterLeft' if side<0 else 'OuterRight'
        _move(m,key+'CameraPCB',(0,0,.75))
        _replace(m,key+'CameraSensor',m.rr(4.1,4.1,.70,(side*17.5,cy+p['lid_height']/2-7.3,5.90),.35))
        m.ring(key+'CameraBarrel','Outer camera optical barrel',1.5,.90,.66,(side*17.5,cy+p['lid_height']/2-7.3,5.18),'LidInternal',1,'black',internal=True,pose='Lid')
    m.ring('InnerCameraBarrel','Inner camera optical barrel',1.5,.90,.44,(0,cy+p['lid_height']/2-7.3,hz-.78),'LidInternal',3,'black',internal=True,pose='Lid')
    for side in [-1,1]:
        pad=m.rr(3.0,1.5,.20,(side*61,cy+29,hz-.04),.4)
        m.cut('LidBezel',pad,'Lid rubber bumper inset');m.feature('LidBumper'+str(side),'Lid rubber bumper',pad,'Lid',6,'rubber',False,'Lid')
    # Original 3DS charging cradle: approximate enclosure, passive contacts and jack.
    y=-133.0;a='Cradle'
    m.native('CradleBase','Charging cradle base',144,84,8.0,6.0,(0,y,0),a,0,'black')
    m.cut('CradleBase',m.rr(134.8,74.8,4.0,(0,y,3.0),6.0),'Closed-console support recess')
    m.box('CradleRearBar','Cradle rear contact support',122,5.8,12.0,(0,y+38.4,5.6),a,0,'black',1.3)
    m.box('CradleContactCarrier','Cradle passive contact carrier',20,2.0,6.0,(39,y+38.0,7.7),a,1,'rubber',.5)
    for i,x in enumerate([32.1,45.9]):
        # Springs sit behind separated flat gold contact leaves.
        m.box('CradleContact'+str(i),'Cradle gold spring contact',1.55,3.10,.18,(x,y+37.15,10.7),a,2,'gold',.2,orient=App.Rotation(V(0,0,1),V(0,-1,0)))
        spring=Part.makeHelix(.65,1.95,.48);profile=Part.Wire(Part.makeCircle(.09,spring.Vertexes[0].Point,spring.Edges[0].tangentAt(spring.Edges[0].FirstParameter)))
        shape=Part.Wire(spring.Edges).makePipeShell([profile],True,False);shape.rotate(V(),V(1,0,0),-90);shape.translate(V(x,y+37.4,10.7))
        m.feature('CradleSpring'+str(i),'Charging contact spring',shape,a,1,'metal',True)
        m.cut('CradleContactCarrier',Part.makeCylinder(.64,3.0,V(x,y+37.2,10.7),V(0,1,0)),'Contact spring bore')
        m.cut('CradleRearBar',Part.makeCylinder(.65,3.2,V(x,y+37.1,10.7),V(0,1,0)),'Contact spring rear clearance')
    m.cut('CradleRearBar',m.parts['CradleContactCarrier'].Shape,'Passive contact carrier seat')
    orient=App.Rotation(V(0,0,1),V(0,1,0))
    jack=m.rr(8.1,3.5,5.0,(0,y+36.5,9.0),.6,orient).cut(m.rr(6.5,2.0,5.4,(0,y+36.3,9.0),.35,orient))
    m.feature('CradleChargeJack','Cradle charging socket',jack,a,0,'metal')
    m.cut('CradleRearBar',m.rr(8.5,3.9,6,(0,y+36.2,9.0),.7,orient),'Cradle charging socket mouth')
    for i,(x,yy) in enumerate([(-55,y-28),(55,y-28),(-55,y+28),(55,y+28)]):
        pad=m.rr(7,5,.18,(x,yy,.035),1);m.cut('CradleBase',pad,'Cradle foot inset');m.feature('CradleFoot'+str(i),'Cradle rubber foot',pad,a,0,'rubber')
    for side in [-1,1]:m.box('CradleSupportPad'+str(side),'Cradle console support pad',18,7,.20,(side*45,y-18,3.02),a,1,'rubber',1.0)
    m.checkpoint(12,'service_details_and_charging_cradle','完成剩余接触面修正、摄像头镜筒、合盖缓冲垫，以及原款 3DS 的被动触点充电底座示意。')

STAGES[12]=stage12


def stage13(m):
    m.cut('CradleBase',m.parts['CradleRearBar'].Shape,'Rear-support tongue seated in cradle base')
    y=-133.0
    m.cut('CradleRearBar',Part.makeBox(21.0,5.0,6.4,V(28.5,y+34.5,7.5)),'Open contact-carrier access window')
    m.cut('CradleContactCarrier',[m.parts['CradleContact'+str(i)].Shape for i in range(2)],'Gold contact-leaf seats')
    # Persist hinge geometry with the model, so pose macros need no session state.
    for key,cell in [('HingeY','B8'),('HingeZ','B9')]:
        m.params.set('A'+cell[1:],key);m.params.set(cell,str(m.profile['hinge_y' if key=='HingeY' else 'hinge_z'])+' mm')
        if not m.params.getAlias(cell):m.params.setAlias(cell,key)
        m.param_cells[key]=cell
    m.profile['stages']=13
    m.checkpoint(13,'cradle_contact_fit','完成底座后支承座与充电弹片配合，保存可复现的铰链轴参数，准备最终原生文件与图纸。')

STAGES[13]=stage13
