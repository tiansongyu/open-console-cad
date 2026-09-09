"""Original red/cream HVC-001 Famicom with round-button wired controllers."""
import math
import FreeCAD as App
import Part
from .core import V


def _yz_prism(points,x=-90,width=180):
    wire=Part.makePolygon([V(x,y,z) for y,z in points]+[V(x,*points[0])])
    return Part.Face(Part.Wire(wire.Edges)).extrude(V(width,0,0))


def _top_tools(m,inside=False):
    dz=-2.2 if inside else 0;grow=1.7 if inside else 0
    tools=[_yz_prism([(-112,28+dz),(-85,53+dz),(-85,70),(-112,70)]),
           _yz_prism([(86,53+dz),(112,40+dz),(112,70),(86,70)])]
    for side in [-1,1]:
        tools.append(m.rr(21+2*grow,137+2*grow,60,(side*67,21.5,20+dz),2.2+grow))
    tools.append(m.rr(121+2*grow,38+2*grow,35,(0,35,46+dz),1.8+grow))
    tools.append(m.rr(76+2*grow,40+2*grow,35,(0,74.5,40.5+dz),1.2+grow))
    return tools


def stage01(m):
    m.colors.update({'fccream':(.78,.77,.66),'fcred':(.48,.025,.045),'fcgold':(.75,.65,.38),'fcink':(.035,.028,.024)})
    m.native('BottomCover','Burgundy bottom cover',150,220,5,2.2,(0,0,2.4),'Body',-6,'fcred',expr={'Width':'Parameters.Width','Height':'Parameters.Height'})
    m.native('LowerShell','Burgundy lower enclosure skirt',150,220,5,10.6,(0,0,4.7),'Body',-6,'fcred')
    m.cut('LowerShell',m.rr(146.4,216.4,11,(0,0,4.5),3.2),'Lower-shell cavity')
    m.native('UpperShell','Sloping cream upper enclosure',150,220,5,37.6,(0,0,15.4),'Body',4,'fccream',expr={'Width':'Parameters.Width','Height':'Parameters.Height'})
    m.cut('UpperShell',_top_tools(m),'Sloping front and rear, controller wells and stepped cartridge bed')
    inside=m.rr(146.6,216.6,35.6,(0,0,15.2),3.3).cut(Part.makeCompound(_top_tools(m,True)))
    m.cut('UpperShell',inside,'Following interior ceiling leaves approximately 2.2 mm top walls')
    for i,(x,y) in enumerate([(-59,-92),(59,-92),(-59,90),(59,90)]):
        m.cyl('RubberFoot'+str(i),'Bottom support foot',4.4,2.2,(x,y,0),'Body',-6,'rubber')
    m.checkpoint(1,'native_sloping_red_cream_shell','建立 150 × 220 mm 红白分壳、原生草图与圆角、前后斜面、两侧手柄收纳槽和阶梯卡带区域；退卡与控制件完成后核对 60 mm 总高。')


def stage02(m):
    # Closed cartridge dust flap and its native aperture; hinge parts follow later.
    m.cut('UpperShell',m.rr(117.6,30,10,(0,35,42),1.0),'Cartridge dust-flap opening')
    m.native('CartridgeDustFlap','Burgundy cartridge dust flap',116.6,28.8,1.0,1.6,(0,35,46.2),'CardReader',4,'fcred')
    m.box('DustFlapRearRidge','Cartridge-flap hinge ridge',115.6,1.4,1.0,(0,48.1,47.9),'CardReader',4,'fcred',.4)
    # Eject well is a separate thin tray below the cutout in the upper shell.
    m.cut('UpperShell',m.rr(41,64,6,(0,-43,48.1),1.6),'Eject slider well')
    m.box('EjectWellFloor','Eject well floor',40.4,63.4,1.2,(0,-43,49.0),'Controls',2,'fccream',1.3)
    m.cut('EjectWellFloor',m.rr(2.1,46,2,(0,-39,48.8),.5),'Eject linkage travel slot')
    lever=_yz_prism([(-74,51.4),(-60,51.4),(-60,53.5),(-65,60),(-68.5,60),(-71.5,54),(-74,54)],-18.5,37)
    m.feature('EjectLever','Raised burgundy eject handle',lever,'Controls',6,'fcred')
    for name,x in [('Power',-38),('Reset',38)]:
        m.cut('UpperShell',m.rr(16.2,17.2,5,(x,-75,49),1.1),name+' control aperture')
        m.native(name+'Cap',name+' burgundy cap',15.6,16.6,.8,1.5,(x,-75,53.2),'Controls',6,'fcred')
    m.box('PowerFingerRidge','Power slide raised grip',14.0,3.0,2.4,(-38,-77,54.85),'Controls',6,'fcred',.5)
    # Front nameplate follows the same analytic plane as the shell front.
    angle=math.degrees(math.atan2(25,27));q=App.Rotation(V(1,0,0),angle)
    center=V(0,-98,28+14*25/27)+q.multVec(V(0,0,.14))
    plaque=m.rr(130,16,.10);plaque.Placement=App.Placement(center,q)
    m.feature('FrontNameplate','Famicom burgundy nameplate',plaque,'Body',4,'fcred')
    origin=center+q.multVec(V(-45,-1.8,.12))
    m.label('FamilyComputerWord','FAMILY COMPUTER',4.8,tuple(origin),'Body',4,'fcgold',rotation=q)
    origin=center+q.multVec(V(42,-4.2,.12))
    m.label('NintendoWord','Nintendo',2.0,tuple(origin),'Body',4,'fcgold',rotation=q)
    for name,x in [('POWER',-55),('RESET',48)]:
        m.label(name+'Mark',name,2.0,(x,-76,53.018),'Body',4,'fccream')
    m.label('EjectMark','EJECT',2.0,(-5.0,-79,53.018),'Body',4,'fccream')
    # Thin rear ceiling with an ordered ventilation grille.
    vents=[m.rr(1.5,23,12,(-29+i*4.15,95,42),.35) for i in range(15)]
    m.cut('UpperShell',vents,'Rear heat ventilation slots')
    m.checkpoint(2,'top_controls_and_cartridge_cover','加入红色卡槽防尘盖、退卡滑槽与抬高把手、POWER/RESET 独立按钮、随斜面放置的铭牌，以及后部散热槽。')


STAGES={1:stage01,2:stage02}


def _controller(m,number,side):
    from .psp import _polygon
    group='Controller'+str(number);prefix='P'+str(number);before=set(m.parts)
    back=m.native(prefix+'Back','Controller '+str(number)+' rear cover',126,52,5,1.2,(0,0,0),group,-5,'fcred')
    m.native(prefix+'Frame','Controller middle shell',126,52,5,10.2,(0,0,1.3),group,0,'fcred')
    m.cut(prefix+'Frame',m.rr(122.4,48.4,10.6,(0,0,1.1),3.2),'Controller inner cavity')
    m.native(prefix+'Front','Controller front cover',125.8,51.8,4.9,1.3,(0,0,11.6),group,4,'fcred')
    plate=_polygon([(-59,-22),(59,-22),(59,6),(-15,6),(-15,22),(-59,22)],12.98,.12)
    m.feature(prefix+'GoldPlate','Gold control faceplate',plate,group,4,'fcgold')
    cross=m.rr(7.2,20,1.0,(-44,-6,13.4),.65).fuse(m.rr(20,7.2,1.0,(-44,-6,13.4),.65)).removeSplitter()
    cross=cross.cut(Part.makeSphere(4,V(-44,-6,18.10)))
    m.feature(prefix+'DPad','Controller cross directional pad',cross,group,6,'black')
    bore=m.rr(7.7,20.5,4,(-44,-6,11.2),.8).fuse(m.rr(20.5,7.7,4,(-44,-6,11.2),.8))
    for key in [prefix+'Front',prefix+'GoldPlate']:m.cut(key,bore,'Directional cross opening')
    for letter,x in [('B',29),('A',47)]:
        tool=Part.makeCylinder(6.2,4,V(x,-8,11.2))
        for key in [prefix+'Front',prefix+'GoldPlate']:m.cut(key,tool,'Round action-button aperture')
        m.ring(prefix+letter+'Rim','Burgundy action-button rim',6.1,5.5,.65,(x,-8,13.12),group,4,'fcred')
        cap=Part.makeCylinder(5.3,1.35,V(x,-8,13.25)).cut(Part.makeSphere(8,V(x,-8,21.0)))
        m.feature(prefix+letter,'Round '+letter+' button',cap,group,6,'black')
        m.label(prefix+letter+'Mark',letter,2.7,(x-1.0,.6,13.12),group,4,'fcink')
    m.label(prefix+'Number',str(number),4.0,(-55,13.5,13.12),group,4,'fcink')
    if number==1:
        m.cut(prefix+'GoldPlate',m.rr(40,13,1,(-3.5,-8,12.8),5.5),'Start/select red faceplate recess')
        for name,x in [('Select',-14),('Start',7)]:
            m.cut(prefix+'Front',m.rr(10.8,5,3,(x,-8,11.3),2.1),name+' control opening')
            m.box(prefix+name,name+' rubber button',10.2,4.4,1.1,(x,-8,13.3),group,6,'black',2.0)
            m.label(prefix+name+'Mark',name.upper(),2.0,(x-5.0,.8,13.12),group,4,'fcink')
    else:
        holes=[m.rr(.65,4.0,3,(-12+i*1.8,-7.5,11.3),.28) for i in range(4)]
        for key in [prefix+'Front',prefix+'GoldPlate']:m.cut(key,holes,'Player-II microphone grille')
        m.box(prefix+'MicMesh','Player-II microphone backing',8.0,5.0,.20,(-9.3,-7.5,11.1),group,2,'black',.4,True)
        for key in [prefix+'Front',prefix+'GoldPlate']:m.cut(key,m.rr(22.5,4.6,3,(12,-8,11.3),.8),'Player-II volume slider slot')
        m.box(prefix+'VolumeTrack','Microphone volume track',22,4.1,.25,(12,-8,11.2),group,2,'black',.6,True)
        m.box(prefix+'VolumeSlider','Player-II microphone volume knob',4.4,3.8,1.4,(12,-8,13.2),group,6,'black',.5)
        m.label(prefix+'MicMark','MIC.',2.0,(-15,.8,13.12),group,4,'fcink')
        m.label(prefix+'VolumeMark','VOLUME',1.8,(1,.8,13.12),group,4,'fcink')
    for index,(x,y) in enumerate([(-52,-17),(52,-17),(-52,17),(52,17)]):
        bore=Part.makeCylinder(.85,4,V(x,y,-.1)).fuse(Part.makeCylinder(1.45,.8,V(x,y,-.1)))
        m.cut(prefix+'Back',bore,'Controller rear fastening hole')
        m.screw(prefix+'Screw'+str(index),(x,y,.2),group,-5,length=2.5,radius=1.35)
    m.cyl(prefix+'CableGrommet','Wired-controller strain relief',2.2,5,(-63,10,6.5),group,0,'black',axis=(-1,0,0))
    # Store upright with the face pointing outward in the corresponding side well.
    mat=App.Matrix();mat.A11,mat.A21,mat.A31=0,-1,0;mat.A12,mat.A22,mat.A32=0,0,-side;mat.A13,mat.A23,mat.A33=side,0,0
    transform=App.Placement(V(side*58.8,21.5,33),App.Rotation(mat))
    for key in set(m.parts)-before:
        obj=m.parts[key];obj.Placement=transform.multiply(obj.Placement);obj.FlatPlacement=obj.Placement


def stage03(m):
    # Deep original storage channels allow full-height controllers to sit beside the body.
    for side in [-1,1]:
        well=m.rr(21,137,60,(side*67,21.5,6.3),2.2)
        m.cut('UpperShell',well,'Deep upright controller storage channel')
        m.cut('LowerShell',well,'Controller channel descends into lower shell')
        m.box('ControllerSeat'+str(side),'Lower controller support shelf',14.4,132,1.2,(side*65.9,21.5,5.3),'Body',-6,'fcred',1.2)
    _controller(m,1,-1);_controller(m,2,1)
    m.profile['stages']=3
    m.checkpoint(3,'distinct_round_button_wired_controllers','建立两只独立的圆形按键手柄、金色面板、分壳与螺钉；一号配置 START/SELECT，二号配置麦克风格栅和音量滑块，并竖放在两侧收纳槽中。')


STAGES[3]=stage03
