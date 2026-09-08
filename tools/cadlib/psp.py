"""First-generation PSP-1000: rounded black body, silver rim and UMD layout."""
from .core import V


def stage01(m):
    p=m.profile;w,h=p['width'],p['height']
    m.native('BackCover','PSP-1000 rear enclosure blank',w-1,h-1,30.5,1.2,(0,0,0),layer=-6)
    m.native('MainFrame','Original PSP structural perimeter',w,h,31.0,20.4,(0,0,1.3),layer=0,expr={'Width':'Parameters.Width','Height':'Parameters.Height'})
    m.cut('MainFrame',m.rr(w-3.4,h-3.4,20.8,(0,0,1.1),29.3),'Board, battery and UMD interior cavity')
    m.native('FrontBezel','Glossy PSP front face blank',w-.4,h-.4,30.8,1.2,(0,0,21.8),layer=4)
    trim=m.rr(w-.02,h-.02,1.0,(0,0,11.0),30.99).cut(m.rr(w-.6,h-.6,1.3,(0,0,10.85),30.7))
    m.feature('PerimeterTrim','Silver perimeter trim',trim,'Body',0,'metal')
    m.cut('MainFrame',trim,'Flush silver-trim seating recess')
    m.checkpoint(1,'psp1000_enclosure','按 PSP-1000 的 170 × 74 × 23 mm 主体尺寸建立圆端机身、内部空腔、独立前后外壳及银色周缘饰条。')


STAGES={1:stage01}

import math
import Part
import FreeCAD as App
from .clamshell import _move, _replace


def stage02(m):
    w,h=m.profile['upper_display'];y=3.5
    m.profile['display_y']=y
    m.profile['envelope_groups']=['Body']
    m.profile['envelope_basis']='Published body dimensions excluding maximum projections; controls and interface projections reported separately.'
    m.cut('FrontBezel',m.rr(102.3,60.8,1.7,(0,y,21.6),.9),'LCD and window-surround recess')
    surround=m.rr(102.0,60.5,.35,(0,y,22.6),.8).cut(m.rr(w+.12,h+.12,.6,(0,y,22.5),.2))
    m.feature('DisplaySurround','Wide LCD black surround',surround,'Display',5,'bezel')
    m.box('LCDBackplate','LCD steel backplate',99.4,58.4,.30,(0,y,18.9),'Display',1,'metal',.7,True)
    m.box('LCD','4.3-inch TFT display module',99.0,58.0,3.10,(0,y,19.3),'Display',2,'black',.6,True)
    m.box('BacklightFilm','LCD optical diffuser study',94.8,53.2,.10,(0,y,22.47),'Display',3,'screen',.2,True)
    m.box('DisplayGlass','Wide display window',w,h,.20,(0,y,22.80),'Display',7,'screen',.2)
    m.checkpoint(2,'wide_tft_display','建立 4.3 英寸 16:9 显示窗口、独立 LCD 模块、金属背板、光学膜层与黑色屏框，分别记录主体与突出部位的尺寸口径。')


def _polygon(points,z,t):
    wire=Part.makePolygon([V(x,y,z) for x,y in points]+[V(*points[0],z)])
    return Part.Face(Part.Wire(wire.Edges)).extrude(V(0,0,t))


def _ps_symbol(m,key,ch,x,y,z):
    if ch=='Triangle':
        sh=_polygon([(x,y+1.75),(x-1.8,y-1.3),(x+1.8,y-1.3)],z,.025).cut(_polygon([(x,y+1.15),(x-1.28,y-.99),(x+1.28,y-.99)],z-.01,.05))
    elif ch=='Circle':sh=Part.makeCylinder(1.6,.025,V(x,y,z)).cut(Part.makeCylinder(1.31,.05,V(x,y,z-.01)))
    elif ch=='Square':sh=m.rr(3.0,3.0,.025,(x,y,z),.05).cut(m.rr(2.45,2.45,.06,(x,y,z-.01),.02))
    else:
        bars=[]
        for angle in [-45,45]:
            s=m.rr(.32,3.9,.025,(x,y,z),.04);s.rotate(V(x,y,z),V(0,0,1),angle);bars.append(s)
        sh=bars[0].fuse(bars[1]).removeSplitter()
    m.feature(key,ch+' button symbol',sh,'Controls',6,'white')


def stage03(m):
    x,y=-65,10
    for key,angle in [('Up',0),('Right',-90),('Down',180),('Left',90)]:
        pts=[(-2.4,1.2),(2.4,1.2),(3.25,5.8),(0,8.5),(-3.25,5.8)]
        sh=_polygon([(x+xx,y+yy) for xx,yy in pts],22.6,.95);sh.rotate(V(x,y,0),V(0,0,1),angle)
        hole=_polygon([(x+xx*1.065,y+yy*1.065) for xx,yy in pts],21.65,2.15);hole.rotate(V(x,y,0),V(0,0,1),angle)
        m.cut('FrontBezel',hole,'Directional-key opening');m.feature('DPad'+key,key+' directional key',sh,'Controls',6,'black')
        a=math.radians(angle);xx=x-5.0*math.sin(a);yy=y+5.0*math.cos(a)
        m.cyl('DPadStem'+key,'Directional-key stem',1.65,1.2,(xx,yy,21.35),'Controls',3,'black',internal=True)
        m.cut('FrontBezel',m.parts['DPadStem'+key].Shape,'Directional stem passage')
        tick=_polygon([(xx,yy+1.0),(xx-.8,yy-.6),(xx+.8,yy-.6)],23.56,.025)
        tick.rotate(V(xx,yy,0),V(0,0,1),angle);m.feature('DPadArrow'+key,'Direction arrow',tick,'Controls',6,'white')
    m.cyl('DPadCarrier','Directional-key common carrier',8.7,.35,(x,y,20.94),'Internal',3,'black',internal=True)
    for dx,dy,ch in [(0,7.5,'Triangle'),(7.5,0,'Circle'),(0,-7.5,'Cross'),(-7.5,0,'Square')]:
        xx,yy=65+dx,9+dy;m.cut('FrontBezel',Part.makeCylinder(4.22,2.6,V(xx,yy,21.4)),'Face-button bore')
        cap=Part.makeCylinder(4.02,1.15,V(xx,yy,22.5));cap=cap.makeFillet(.22,[e for e in cap.Edges if e.BoundBox.ZLength<1e-6])
        m.feature('Button'+ch,ch+' button',cap,'Controls',6,'black');_ps_symbol(m,'ButtonSymbol'+ch,ch,xx,yy,23.66)
        m.cyl('ButtonStem'+ch,'Face-button plunger',1.65,2.4,(xx,yy,20.05),'Controls',3,'black',internal=True)
    xx,yy=-65,-16
    m.cut('FrontBezel',Part.makeCylinder(6.85,2.4,V(xx,yy,21.5)),'Single analog slider opening')
    m.ring('AnalogBezel','Analog-pad annular surround',6.65,5.98,.3,(xx,yy,22.85),'Controls',5,'black')
    cap=Part.makeCylinder(5.85,.80,V(xx,yy,23.10))
    lines=[]
    for q in range(-8,9):
        lines.append(Part.makeBox(.13,12,.15,V(xx+q*.65-.065,yy-6,23.79)))
        lines.append(Part.makeBox(12,.13,.15,V(xx-6,yy+q*.65-.065,23.79)))
    cap=cap.cut(Part.makeCompound(lines));m.feature('AnalogCap','Textured single analog nub',cap,'Controls',6,'rubber')
    m.cyl('AnalogStem','Analog nub transmission shaft',2.0,2.95,(xx,yy,20.10),'Internal',3,'black',internal=True)
    menu=[('Home','HOME',-44,12),('VolumeMinus','-',-31,5),('VolumePlus','+',-23,5),('Display','',13,5),('Sound','',23,5),('Select','SELECT',35,10),('Start','START',47,10)]
    for key,text,xx,ww in menu:
        m.cut('FrontBezel',m.rr(ww+.3,4.1,1.8,(xx,-30.6,21.6),1.8),'Front system-key seat')
        m.box(key+'Key',key+' system key',ww,3.8,.9,(xx,-30.6,22.5),'Controls',6,'black',1.7)
        if text:m.label(key+'Legend',text,1.15 if len(text)>1 else 2.0,(xx-(len(text)*.38 if len(text)>1 else .65),-31.1,23.42),'Controls',6,'white')
    icon=m.rr(2.4,1.8,.025,(13,-30.6,23.42),.1).cut(m.rr(1.95,1.35,.05,(13,-30.6,23.41),.05));m.feature('DisplayIcon','Display-brightness icon',icon,'Controls',6,'white')
    m.label('SoundIcon','♪',1.7,(22.3,-31.2,23.42),'Controls',6,'white')
    m.label('PSPFrontMark','PSP',3.5,(-5.2,-31.5,23.025),'Body',4,'white')
    m.label('SonyFrontMark','SONY',2.4,(55,28.2,23.025),'Body',4,'white')
    m.label('PlayStationFrontMark','PS',2.4,(-71,28.2,23.025),'Body',4,'white')
    m.checkpoint(3,'original_controls_and_analog_nub','加入四向键面、白色几何符号面按键、纹理模拟滑杆，以及 HOME、音量、显示、声音、SELECT/START 的初代底部键列。')


def stage04(m):
    m.colors['yellow']=(.90,.63,.06)
    top=App.Rotation(V(0,0,1),V(0,1,0));bottom=App.Rotation(V(0,0,1),V(0,-1,0))
    # Five-pin mini-USB at the top center.
    m.cut('MainFrame',m.rr(9.0,4.3,4.0,(0,34,14.5),.7,top),'Top Mini-USB aperture')
    shell=m.rr(8.5,3.8,5.8,(0,30.8,14.5),.65,top).cut(m.rr(6.8,2.45,6.1,(0,30.7,14.5),.35,top))
    m.feature('MiniUSBShell','Five-pin Mini-USB shell',shell,'Ports',0,'metal')
    m.box('MiniUSBTongue','Mini-USB tongue',6,.55,4.8,(0,31.5,14.4),'Ports',0,'black',.15,orient=top)
    for i in range(5):m.box('USBContact'+str(i),'Mini-USB contact',.40,.10,3.2,(-2+i,32.6,14.82),'Ports',0,'gold',.02,orient=top)
    for side in [-1,1]:m.ring('USBMount'+str(side),'USB accessory thread collar',1.35,.68,1.0,(side*8.2,35.7,14.5),'Ports',0,'metal',axis=(0,1,0))
    for key in ['MiniUSBShell','USBMount-1','USBMount1']:m.cut('MainFrame',m.parts[key].Shape,'USB connector mounting seat')
    m.box('IRWindow','Original PSP top infrared window',14,4.4,.42,(-31,36.35,14.6),'Ports',0,'screen',.7,orient=top)
    m.cut('MainFrame',m.parts['IRWindow'].Shape,'Infrared window inset')
    m.box('UMDOpenSlider','Top UMD opening slider',13,3.9,.45,(38,36.4,14.5),'Controls',0,'black',.7,orient=top)
    m.cut('MainFrame',m.parts['UMDOpenSlider'].Shape,'UMD release slider track')
    # Headset and DC input at the lower corners, inside the body envelope in XY.
    m.ring('HeadphoneSocket','3.5 mm headset jack',2.7,1.78,5.5,(-66,-34.4,10.0),'Ports',0,'metal',axis=(0,1,0))
    m.cut('MainFrame',Part.makeCylinder(2.9,7,V(-66,-35.2,10),V(0,1,0)),'Headset-jack opening')
    m.box('HeadsetRemotePort','Remote-control connector body',6.5,2.9,3.2,(-58,-36.05,10),'Ports',0,'black',.45,orient=top)
    m.cut('MainFrame',m.parts['HeadsetRemotePort'].Shape,'Headset-remote connector seat')
    for j in range(3):m.box('RemoteContact'+str(j),'Remote contact',.4,.6,.08,(-60+j*2,-36.08,10),'Ports',0,'gold',.02,orient=bottom)
    carrier=m.rr(8,8,1.0,(66,-34.35,11.3),1.0,top).cut(Part.makeCylinder(2.45,2,V(66,-34.8,11.3),V(0,1,0)))
    m.feature('ChargeCarrier','Yellow DC and charging-terminal carrier',carrier,'Ports',0,'yellow')
    m.ring('ChargeJack','DC IN barrel socket',2.38,1.95,5.2,(66,-34.1,11.3),'Ports',0,'metal',axis=(0,1,0))
    m.cyl('ChargeCenterPin','DC center contact',.60,3.8,(66,-33.1,11.3),'Ports',0,'gold',axis=(0,1,0))
    m.cut('MainFrame',[m.parts[k].Shape for k in ['ChargeCarrier','ChargeJack']],'DC-jack mounting seat')
    for i,x in enumerate([63.6,68.4]):
        m.box('DockContact'+str(i),'External charge contact',1.45,1.5,.08,(x,-34.37,8.2),'Ports',0,'gold',.15,orient=bottom)
        m.cut('ChargeCarrier',m.parts['DockContact'+str(i)].Shape,'Charge-contact rebate')
    # Curved Memory Stick cover follows the left side instead of floating off it.
    w,h=170,74
    band=m.rr(w-.04,h-.04,5.1,(0,0,12.9),30.98).cut(m.rr(w-1.4,h-1.4,5.4,(0,0,12.8),30.3))
    door=band.common(Part.makeBox(4,26,6,V(-85,-13,12.5)))
    m.feature('MemoryStickDoor','Curved Memory Stick Duo cover',door,'Ports',0,'black');m.cut('MainFrame',door,'Memory Stick side cover seat')
    for key,side,y,z in [('WLANSlider',-1,-19,14),('PowerHoldSlider',1,-14,14)]:
        # A curved seating region keeps these controls flush to the rounded ends.
        sh=m.rr(170-.03,74-.03,3.4,(0,0,z-1.7),30.985).cut(m.rr(168.7,72.7,3.8,(0,0,z-1.9),30.35))
        sh=sh.common(Part.makeBox(9,7,4,V(-85 if side<0 else 76,y-3.5,z-2)))
        m.feature(key,key,sh,'Controls',0,'black');m.cut('MainFrame',sh,'Side slider seat')
    m.checkpoint(4,'mini_usb_memory_stick_and_power','建立 Mini-USB、红外窗、UMD 开盖滑块、耳机与遥控接口、黄色 DC 插座及充电触点，并加入沿曲面贴合的记忆棒盖和左右侧滑块。')


def stage05(m):
    for side in [-1,1]:
        x=side*62
        hole=m.rr(8.5,2.25,1.7,(x,-28.6,21.5),.75);m.cut('FrontBezel',hole,'Original lower front speaker outlet')
        m.box('SpeakerMesh'+str(side),'Front speaker grille insert',8.1,1.85,.16,(x,-28.6,22.35),'Ports',4,'black',.65)
        slots=[m.rr(.35,1.35,.4,(x+(j-4)*.8,-28.6,22.2),.10) for j in range(9)]
        m.cut('SpeakerMesh'+str(side),slots,'Speaker mesh slot array')
        m.ring('SpeakerFrame'+str(side),'Stereo speaker frame',4.9,4.0,2.0,(x,-28.6,18.0),'Internal',1,'metal',internal=True)
        m.cyl('SpeakerMagnet'+str(side),'Speaker magnet',2.7,1.55,(x,-28.6,18.1),'Internal',1,'metal',internal=True)
        m.cyl('SpeakerDiaphragm'+str(side),'Speaker diaphragm',3.9,.1,(x,-28.6,20.1),'Internal',2,'black',internal=True)
        cap=m.rr(22.0,8.0,5.0,(side*61,30.1,18.3),3.0)
        m.feature('Shoulder'+str(side),'L/R shoulder button',cap,'Controls',5,'metal')
        for frame in ['MainFrame','FrontBezel']:m.cut(frame,cap,'Shoulder button seating recess')
        m.cyl('ShoulderPin'+str(side),'Shoulder pivot pin',.7,17,(side*61-8.5,28.0,19.7),'Internal',2,'metal',axis=(1,0,0),internal=True)
        m.cut('Shoulder'+str(side),m.parts['ShoulderPin'+str(side)].Shape,'Shoulder pivot bore')
        m.label('ShoulderLegend'+str(side),'L' if side<0 else 'R',2.5,(side*61-.8,30.0,23.32),'Controls',6,'white')
    for key,x,y,mat in [('MemoryLED',-75,-7,'red'),('WirelessLED',-75,-11,'led'),('PowerLED',75,-11,'led')]:
        led=m.rr(2.0,.85,.14,(x,y,22.93),.25);m.cut('FrontBezel',led,'Status light window');m.feature(key,key,led,'Ports',4,mat)
    m.label('PowerLegend','POWER',1.45,(69,-8.5,23.025),'Body',4,'led')
    m.label('HoldLegend','HOLD',1.3,(70,-19.0,23.025),'Body',4,'white')
    # Twin lower-rail acoustic slots and the strap eye are distinct initial-model details.
    bottom=App.Rotation(V(0,0,1),V(0,-1,0))
    for side in [-1,1]:
        sh=m.rr(6.8,1.1,.3,(side*48,-36.95,12.4),.35,bottom);m.cut('MainFrame',sh,'Lower rail acoustic slot')
        m.feature('RailSpeakerSlot'+str(side),'Lower rail acoustic opening',sh,'Ports',0,'black')
    eye=m.rr(8,6.5,2.4,(-66,-29.3,15.0),2.5).cut(m.rr(5.8,3.7,2.8,(-66,-29.3,14.8),1.5))
    m.feature('StrapEye','Left lower strap eye',eye,'Body',0,'metal')
    m.cut('MainFrame',eye,'Strap-eye mounting seat')
    m.checkpoint(5,'speakers_shoulders_and_indicators','补齐初代前下方和底边扬声器出口、独立扬声器、L/R 肩键与轴销、状态灯、POWER/HOLD 标识及腕带环。')


STAGES.update({2:stage02,3:stage03,4:stage04,5:stage05})


def stage06(m):
    # Separate the curved battery grip and central UMD door from the rear shell.
    rear=m.parts['BackCover'].Shape.copy()
    hatch=rear.common(Part.makeBox(42,80,1.6,V(-85,-40,-.1)))
    m.feature('BatteryDoor','Curved removable battery cover',hatch,'Body',-6,'accent')
    m.cut('BackCover',Part.makeBox(42.25,80,1.6,V(-85,-40,-.1)),'Battery-grip separation')
    m.cut('BackCover',m.rr(69.3,66.3,1.6,(0,0,-.1),4.25),'Central UMD door opening')
    m.box('UMDDoor','UMD rear loading door',69.0,66.0,1.02,(0,0,.10),'UMD',-6,'accent',4.1)
    ring=Part.makeCylinder(21.2,.23,V(0,0,.085)).cut(Part.makeCylinder(18.55,.4,V(0,0,.02)))
    m.feature('UMDLogoRing','Wide brushed-metal PSP rear ring',ring,'UMD',-6,'metal');m.cut('UMDDoor',ring,'Rear ring inset')
    reverse=App.Rotation(V(0,1,0),180)
    m.label('UMDPSPMark','PSP',4.0,(5,-1.5,.118),'UMD',-6,'white',rotation=reverse)
    m.label('UMDLabel','UMD',1.8,(3,26,.118),'UMD',-6,'white',rotation=reverse)
    for k in ['UMDPSPMark','UMDLabel']:m.cut('UMDDoor',m.parts[k].Shape,'UMD-door marking inlay')
    m.label('RearModelMark','PSP-1000  /  CAD',1.5,(73,16,.018),'Body',-6,'white',rotation=reverse);m.cut('BackCover',m.parts['RearModelMark'].Shape,'Rear model inlay')
    grooves=[m.rr(.35,5.2,.18,(-46-i*.8,-17,-.01),.12) for i in range(5)]
    m.cut('BatteryDoor',grooves,'Battery-cover finger grooves')
    for side in [-1,1]:
        m.box('UMDHingeTab'+str(side),'UMD-door hinge tab',5.0,4.0,1.2,(side*25,-30.5,1.3),'UMD',-5,'black',.5,True)
        m.cyl('UMDHingePin'+str(side),'UMD door pivot',.65,5.5,(side*25-2.75,-30.5,2.0),'UMD',-5,'metal',axis=(1,0,0),internal=True)
        m.cut('UMDHingeTab'+str(side),m.parts['UMDHingePin'+str(side)].Shape,'UMD hinge bore')
    m.box('UMDDoorLatch','UMD-door latch tongue',7,3.1,1.6,(0,30.5,1.35),'UMD',-5,'black',.4,True)
    m.checkpoint(6,'battery_grip_and_umd_door','将后壳分出曲面电池盖和中央 UMD 舱门，加入初代宽金属环、标识、指槽、铰链销与锁舌。')


def stage07(m):
    m.box('BatteryPouch','PSP-110 battery enclosure',30.5,48,10.3,(-65,0,2.0),'Battery',-4,'battery',2.5,True)
    m.cut('BatteryPouch',m.rr(29.2,46.7,8.7,(-65,0,2.65),1.9),'Battery-cell cavity')
    m.box('BatteryCell','Battery-cell stack study',28.9,46.4,8.3,(-65,0,2.85),'Battery',-4,'rubber',1.7,True)
    tray=m.rr(32,49.5,.35,(-65,0,1.5),2.8).cut(m.rr(29.7,47.2,.6,(-65,0,1.4),2.0))
    m.feature('BatteryTray','Battery locating rim',tray,'Battery',-5,'black',True)
    m.box('BatteryConnector','Three-terminal battery connector',8.5,2.7,2.0,(-65,25.7,8.5),'Battery',-4,'white',.3,True)
    for i in range(3):m.box('BatteryContact'+str(i),'Battery contact',.8,2,.12,(-67.5+i*2.5,25.7,10.65),'Battery',-4,'gold',.02,True)
    reverse=App.Rotation(V(0,1,0),180)
    for key,text,size,pos in [('BatteryType','PSP-110',2.3,(-55,12,1.98)),('BatteryCapacity','1800 mAh',2.0,(-54,3,1.98)),('BatteryStudy','LAYOUT STUDY',1.3,(-54,-10,1.98))]:m.label(key,text,size,pos,'Battery',-4,'white',rotation=reverse)
    m.checkpoint(7,'psp110_battery','建立 PSP-110 电池外壳、内部电芯、定位托边、三端连接器及 1800 mAh 标识，电池与记忆棒模块分层布置。')


def stage08(m):
    board=m.rr(100,62,.8,(-1,0,14.6),2.5).fuse(m.rr(25,49,.8,(60,4,14.6),2.2)).removeSplitter()
    m.feature('Mainboard','PSP mainboard with control-side arm',board,'Mainboard',-2,'pcb',True)
    for key,x,y,w,h,t in [('CPU',-16,6,19,19,1.65),('MediaEngine',9,6,17,17,1.4),('RAM',-12,-17,15,10,1.15),('Flash',15,-17,12,9,1.0),('PMIC',37,8,8,8,.85),('AudioIC',34,-12,6,7,.75)]:
        m.box(key+'Package',key+' package study',w,h,t,(x,y,15.55),'Mainboard',-2,'black',.35,True)
        title={'MediaEngine':'ME','AudioIC':'AUD'}.get(key,key)
        m.label(key+'Mark',title,1.7,(x-w*.33,y-.6,15.58+t),'Mainboard',-2,'white')
    # Memory Stick occupies a frontward layer above the left-side battery.
    m.box('MemoryReaderPCB','Memory Stick reader board',31.0,23,.6,(-67.3,0,12.95),'Mainboard',-3,'pcb',1.0,True)
    cage=m.rr(30,21.5,2.15,(-67.3,0,13.7),.65).cut(m.rr(31,19.8,1.45,(-67.5,0,14.05),.4))
    m.feature('MemoryReaderCage','Memory Stick Duo socket cage',cage,'Mainboard',-3,'metal',True)
    for i in range(10):m.box('MemoryContact'+str(i),'Memory Stick terminal',4.6,.62,.1,(-55, -7.65+i*1.7,14.15),'Mainboard',-3,'gold',.02,True)
    m.box('WiFiBoard','Wireless daughterboard',39,32,.55,(58,0,7.7),'Mainboard',-4,'pcb',1.1,True)
    shield=m.rr(36.8,29.8,.9,(58,0,6.65),.8).cut(m.rr(35.8,28.8,.75,(58,0,6.9),.5))
    m.feature('WiFiShield','Wireless RF shield',shield,'Mainboard',-4,'metal',True)
    m.box('WiFiChip','Wireless package study',12,10,.65,(58,0,6.99),'Mainboard',-4,'black',.3,True)
    m.box('IRBoard','Top infrared board',18,6,.55,(-31,29,15.1),'Mainboard',-2,'pcb',.6,True)
    m.box('IRReceiver','Infrared optical module',8,3,1.7,(-31,32.1,15.8),'Mainboard',-2,'black',.4,True)
    m.box('PowerBoard','Power switch daughterboard',11,21,.6,(75,-6,15.2),'Mainboard',-2,'pcb',.7,True)
    points=[(-43,-22),(-34,-24),(-23,-28),(-6,-28),(10,-28),(25,-28),(41,-23),(-43,23),(-32,27),(-17,28),(0,28),(17,28),(34,26),(48,25),(58,25),(65,-17),(52,-17),(34,-1),(-38,1),(26,12)]
    for i,(x,y) in enumerate(points):
        m.box('Passive'+str(i),'SMD passive',1.15,.8,.55,(x,y,15.55),'Mainboard',-2,'rubber',.02,True)
        for side in [-1,1]:m.box(f'Passive{i}End{side}','Solder terminal',.22,.86,.57,(x+side*.71,y,15.54),'Mainboard',-2,'metal',.015,True)
    m.checkpoint(8,'mainboard_memory_and_rf','建立带侧臂主板、CPU/媒体引擎/存储封装、记忆棒卡座及十触点、无线子板与屏蔽罩、红外与电源小板和独立阻容器件。')


def stage09(m):
    # Independent approximate UMD drive: perforated chassis, spindle and pickup.
    plate=m.rr(65.5,62,.55,(0,0,7.6),3.0)
    holes=[]
    for x,y,r in [(-24,22,3.0),(-16,22,2.3),(-6,23,2.6),(4,23,2.0),(23,23,2.6),(-25,11,2.4),(-24,-2,3.6),(-24,-16,2.9),(-16,-25,2.4),(-5,-26,2.0),(8,-25,3.0),(23,-24,2.2),(27,10,2.0)]:holes.append(Part.makeCylinder(r,1,V(x,y,7.4)))
    holes += [m.rr(16,18,1,(16,-4,7.4),1.0),Part.makeCylinder(7.2,1,V(0,-3,7.4))]
    m.feature('UMDChassis','Perforated UMD mechanism chassis',plate.cut(Part.makeCompound(holes)),'UMD',-2,'metal',True)
    frame=m.rr(67,63,5.4,(0,0,2.0),3.4).cut(m.rr(64,60,5.8,(0,0,1.8),2.0))
    m.feature('UMDFrame','UMD drive perimeter support',frame,'UMD',-3,'black',True)
    m.cyl('SpindleMotor','UMD spindle motor',6.8,2.5,(0,-3,8.3),'UMD',-1,'metal',internal=True)
    m.cyl('SpindleShaft','UMD spindle shaft',1.6,3.2,(0,-3,5.0),'UMD',-2,'metal',internal=True)
    m.ring('SpindleTable','UMD disc support table',5.2,1.7,.70,(0,-3,4.2),'UMD',-3,'black',internal=True)
    m.cyl('SpindleHub','UMD locating hub',1.62,.9,(0,-3,3.2),'UMD',-3,'metal',internal=True)
    for key,x,r in [('PickupGuide',9,.85),('PickupLeadScrew',23,.65)]:m.cyl(key,'Optical-pickup guide or drive shaft',r,29,(x,-18,5.7),'UMD',-3,'metal',axis=(0,1,0),internal=True)
    carriage=m.rr(17,11,3.0,(16,-4,4.1),.9)
    for x,r in [(9,1.0),(23,.80)]:carriage=carriage.cut(Part.makeCylinder(r,13,V(x,-10.5,5.7),V(0,1,0)))
    m.feature('PickupCarrier','Optical pickup sliding carrier',carriage,'UMD',-3,'metal',True)
    m.ring('PickupLensHolder','Optical lens barrel',2.65,1.75,1.0,(16,-4,3.0),'UMD',-4,'black',internal=True)
    m.cyl('PickupLens','UMD pickup lens',1.65,.22,(16,-4,3.08),'UMD',-4,'screen',internal=True)
    m.box('LaserDiode','Laser diode package study',3.5,2.5,1.5,(15,-4,8.2),'UMD',-1,'black',.3,True)
    m.cyl('SledMotor','Pickup sled motor',4.4,3.0,(-13,20,8.3),'UMD',-1,'metal',internal=True)
    m.ring('SledGear','Pickup-drive gear wheel',4.8,1.0,.55,(-13,20,6.6),'UMD',-2,'white',internal=True)
    m.box('PickupFlex','Optical pickup flexible circuit',8,16,.10,(21,-14,8.5),'UMD',-1,'copper',.4,True)
    for i,(x,y) in enumerate([(-28,-26),(28,-26),(-28,26),(28,26)]):
        m.ring('UMDPost'+str(i),'Drive mounting post',1.65,.76,5.6,(x,y,1.5),'UMD',-4,'black',internal=True)
        m.screw('UMDScrew'+str(i),(x,y,8.7),'UMD',-1,length=3.8,radius=1.15,axis=(0,0,-1))
        m.cut('UMDChassis',Part.makeCylinder(.78,1,V(x,y,7.4)),'UMD chassis mounting bore')
    m.checkpoint(9,'umd_optical_mechanism','补齐 UMD 打孔底盘、支架、主轴电机与托盘、光头导杆和丝杆、镜头载架、进给电机、排线及四处紧固件。')


def stage10(m):
    m.box('DPadPCB','Left directional-key board',19.5,23,.50,(-65,10,16.5),'Internal',1,'pcb',1.0,True)
    points=[(-65,15),(-60,10),(-65,5),(-70,10),(65,16.5),(72.5,9),(65,1.5),(57.5,9)]
    for i,(x,y) in enumerate(points):
        z=17.06 if i<4 else 15.48
        m.cyl('ControlContact'+str(i),'PCB button contact',2.15,.06,(x,y,z),'Internal',1,'gold',internal=True)
        m.cyl('ControlPill'+str(i),'Conducting contact pill',1.45,.16,(x,y,z+.18),'Internal',1,'black',internal=True)
        m.cyl('ControlRubber'+str(i),'Silicone button cup',2.6,2.0,(x,y,z+.55),'Internal',2,'rubber',internal=True)
        m.cyl('ControlBoss'+str(i),'Silicone transmission boss',1.25,1.35 if i<4 else 1.65,(x,y,z+2.6),'Internal',3,'rubber',internal=True)
    m.box('AnalogPCB','Analog slider sensor PCB',17.5,17.5,.45,(-65,-16,16.8),'Internal',1,'pcb',1.3,True)
    housing=m.rr(16.5,16.5,2.35,(-65,-16,17.45),1.4).cut(Part.makeCylinder(2.25,3,V(-65,-16,17.2)))
    m.feature('AnalogHousing','Single analog slider housing',housing,'Internal',2,'black',True)
    m.ring('AnalogBearing','Analog-slider bearing',5.5,2.25,.30,(-65,-16,19.90),'Internal',3,'metal',internal=True)
    for i,(x,y,w,h) in enumerate([(-65,-8.2,9,1.1),(-72.8,-16,1.1,9)]):m.box('AnalogSensor'+str(i),'Analog position sensor study',w,h,.65,(x,y,19.95),'Internal',3,'rubber',.2,True)
    m.box('MenuPCB','Lower system-button board',103,6.3,.5,(0,-30.6,18.5),'Internal',2,'pcb',1.0,True)
    for i,x in enumerate([-44,-31,-23,13,23,35,47]):
        m.box('MenuSwitch'+str(i),'Menu tactile switch',3.8,3.0,.9,(x,-30.6,19.2),'Internal',2,'metal',.35,True)
        m.cyl('MenuStem'+str(i),'System-key transmission stem',.9,2.2,(x,-30.6,20.2),'Internal',3,'black',internal=True)
    for side in [-1,1]:m.box('ShoulderSwitch'+str(side),'L/R switch',6.0,3.0,1.4,(side*61,26.8,16.0),'Internal',2,'metal',.3,True)
    m.box('LCDMainFlex','LCD main flexible circuit',22,7,.10,(5,-22,18.1),'Internal',1,'copper',.35,True)
    m.box('LCDPowerFlex','LCD backlight flexible circuit',4,8,.08,(-20,-23,18.0),'Internal',1,'copper',.25,True)
    for key,x,y,w in [('LCDConnector',5,-25,24),('BacklightConnector',-20,-27,6)]:m.box(key,'Display FPC connector',w,2.5,.75,(x,y,16.65),'Mainboard',-2,'white',.25,True)
    m.box('MemoryFlex','Memory-reader interconnect',5,10,.10,(-51,12,16.1),'Internal',1,'copper',.25,True)
    m.box('WiFiFlex','Wireless module interconnect',8,8,.10,(39,-15,11.0),'Internal',-3,'copper',.25,True)
    for side in [-1,1]:m.box('SpeakerFlex'+str(side),'Speaker flexible conductor',12,2,.09,(side*53,-27.5,17.4),'Internal',1,'copper',.25,True)
    m.box('AntennaStrip','Top wireless antenna study',24,2.4,.12,(58,26.8,15.0),'Mainboard',-2,'gold',.3,True)
    # LCD carrier has an open central field and no solid plate blocking all ICs.
    carrier=m.rr(105,63,.35,(0,3,18.25),1.1).cut(m.rr(96,55,1,(0,3,18.0),.7))
    m.feature('LCDCarrier','LCD locating carrier rim',carrier,'Internal',1,'metal',True)
    m.checkpoint(10,'control_mechanisms_and_flex','加入方向键小板、胶垫与触点、模拟滑杆传感机构、底部系统键小板及开关、显示排线、无线/记忆棒互连、天线和 LCD 承托边。')


STAGES.update({6:stage06,7:stage07,8:stage08,9:stage09,10:stage10})


def stage11(m):
    board_mounts=[(-43,-27),(-43,27),(47,-27),(47,27),(67,-20),(67,20)]
    for i,(x,y) in enumerate(board_mounts):
        m.ring('BoardPost'+str(i),'Mainboard locating post',1.65,.76,12.9,(x,y,1.3),'Internal',-3,'black',internal=True)
        m.cut('Mainboard',Part.makeCylinder(.78,1.3,V(x,y,14.35)),'Mainboard mounting hole')
        m.screw('BoardScrew'+str(i),(x,y,16.0),'Mainboard',-2,length=5.0,radius=1.2,axis=(0,0,-1))
    rear_mounts=[(-40,-29),(-40,29),(40,-29),(40,29),(72,-16),(72,16),(0,-35)]
    for i,(x,y) in enumerate(rear_mounts):
        m.cut('BackCover',[Part.makeCylinder(.73,2,V(x,y,-.1)),Part.makeCylinder(1.32,.52,V(x,y,-.05))],'Rear-case screw bore and counterbore')
        m.screw('RearScrew'+str(i),(x,y,.05),'Body',-6,length=3.1,radius=1.18)
        m.ring('RearPost'+str(i),'Rear-case screw boss',1.55,.74,3.5,(x,y,1.3),'Internal',-5,'black',internal=True)
    # Four padded carrier tabs hold the TFT, independently of the optical drive.
    for i,(x,y) in enumerate([(-48,-24),(48,-24),(-48,29),(48,29)]):
        m.box('LCDPad'+str(i),'LCD corner support pad',3.0,3.0,.20,(x,y,18.65),'Internal',1,'rubber',.5,True)
    # Blank UMD and Memory Stick study accessories; no game artwork is copied.
    x=112.0
    case=Part.makeCylinder(32,4.2,V(x,0,0)).fuse(m.rr(65,40,4.2,(x,12,0),4.5)).removeSplitter()
    case=case.cut(Part.makeCylinder(30.6,3.1,V(x,0,.6)))
    case=case.cut(m.rr(15,31,.85,(x,-10,-.05),1.5))
    m.feature('UMDCartridge','Blank UMD cartridge shell',case,'Accessories',0,'white')
    m.ring('UMDDisc','60 mm optical disc',30,7.5,.6,(x,0,1.8),'Accessories',1,'metal')
    m.ring('UMDDiscHub','Optical-disc hub study',7.25,3.0,1.2,(x,0,1.5),'Accessories',1,'black')
    m.label('UMDStudyMark','UMD  /  CAD STUDY',1.7,(x-13,17,4.182),'Accessories',0,'shell')
    m.cut('UMDCartridge',m.parts['UMDStudyMark'].Shape,'Cartridge label inlay')
    m.box('MemoryStickCard','Memory Stick Duo study card',31,20,1.6,(x,-55,0),'Accessories',0,'blue',1.2)
    for i in range(10):
        m.box('MemoryCardPad'+str(i),'Card gold terminal',3.1,1.0,.02,(x-12,-62.65+i*1.7,1.58),'Accessories',0,'gold',.08)
        m.cut('MemoryStickCard',m.parts['MemoryCardPad'+str(i)].Shape,'Memory-card terminal inlay')
    m.label('MemoryCardMark','DUO',2.2,(x-2,-56,1.582),'Accessories',0,'white');m.cut('MemoryStickCard',m.parts['MemoryCardMark'].Shape,'Memory-card label inlay')
    m.checkpoint(11,'mounts_and_removable_media','补齐主板与后壳紧固件、LCD 支承垫，并制作独立空白 UMD 卡壳、60 mm 光盘和记忆棒附件，准备整机配合检查。')

STAGES[11]=stage11
