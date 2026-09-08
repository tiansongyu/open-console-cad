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
