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
    m.params.set('A3','Depth (Y)');m.params.set('C3','Nintendo nominal front-to-back depth; alias Height')
    m.params.set('A4','Height (Z)');m.params.set('C4','Nintendo nominal overall height; alias ClosedDepth')
    m.params.set('B7','2.2 mm');m.params.set('C7','Nominal upper-shell wall; local features vary')
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
        # Original controller II has a broad perforated microphone field above the center.
        mic=[Part.makeCylinder(.9,3.0,V((i-(count-1)/2)*4.8,7+row*2.7,11.2)) for row in range(5) for count in [5 if row%2==0 else 4] for i in range(count)]
        m.box(prefix+'MicField','Raised microphone grille',25,17,.45,(0,12.5,12.98),group,4,'fcred',1.8)
        for key in [prefix+'Front',prefix+'MicField']:m.cut(key,mic,'Player-II microphone perforations')
        m.box(prefix+'MicMesh','Player-II microphone backing',23.5,15.8,.20,(0,12.5,11.1),group,2,'black',.6,True)
        # Volume is above the D-pad, not between the action buttons.
        m.cut(prefix+'GoldPlate',m.rr(21,9,1,(-35,18,12.8),1.0),'Original volume-label plate notch')
        m.cut(prefix+'Front',m.rr(18.5,3.4,3,(-35,18,11.3),.5),'Player-II volume slider slot')
        m.box(prefix+'VolumeTrack','Microphone volume track',18,3,.25,(-35,18,11.2),group,2,'black',.4,True)
        m.box(prefix+'VolumeSlider','Player-II microphone volume knob',7,2.9,1.4,(-38,18,13.2),group,6,'black',.4)
        for i in range(6):m.cut(prefix+'VolumeSlider',m.rr(.25,2.7,.18,(-40.5+i,18,14.48),.04),'Slider grip groove')
        m.label(prefix+'MicMark','MIC.',2.0,(-3.8,.6,13.12),group,4,'fcink')
        m.label(prefix+'VolumeMark','VOLUME',1.8,(-26,8.8,13.12),group,4,'fcink')
    for index,(x,y) in enumerate([(-52,-17),(52,-17),(-52,17),(52,17)]):
        bore=Part.makeCylinder(.85,4,V(x,y,-.1)).fuse(Part.makeCylinder(1.45,.8,V(x,y,-.1)))
        m.cut(prefix+'Back',bore,'Controller rear fastening hole')
        m.screw(prefix+'Screw'+str(index),(x,y,.2),group,-5,length=2.5,radius=1.35)
    cable_side=-1 if number==1 else 1
    m.cyl(prefix+'CableGrommet','Wired-controller strain relief',2.2,5,(cable_side*63,10,6.5),group,0,'black',axis=(cable_side,0,0))
    # Store upright with the face pointing outward in the corresponding side well.
    mat=App.Matrix();mat.A11,mat.A21,mat.A31=0,side,0;mat.A12,mat.A22,mat.A32=0,0,1;mat.A13,mat.A23,mat.A33=side,0,0
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


def _port_cut(m,tool,reason):
    for key in ['UpperShell','LowerShell']:m.cut(key,tool,reason)


def _tube(points,radius,tangents=None):
    curve=Part.BSplineCurve();options={} if tangents is None else {'InitialTangent':V(*tangents[0]),'FinalTangent':V(*tangents[1])}
    curve.interpolate([V(*p) for p in points],**options);edge=curve.toShape();path=Part.Wire([edge])
    profile=Part.Wire(Part.makeCircle(radius,edge.Vertexes[0].Point,edge.tangentAt(edge.FirstParameter)))
    return path.makePipeShell([profile],True,False)


def stage04(m):
    from . import geometry as g
    from .psp import _polygon
    rear=g.rotation((0,1,0),(0,0,1));front=g.rotation((0,-1,0),(0,0,1))
    # Rear panel coordinates are viewed from the front of the console (AC at +X).
    _port_cut(m,m.rr(11.2,12.2,14,(34,98,17),.7,rear),'DC input rectangular panel opening')
    body=m.rr(10.6,11.6,11.7,(34,98,17),.5,rear).cut(Part.makeCylinder(2.8,12,V(34,98,17),V(0,1,0)))
    m.feature('DCJackBody','Original AC-adapter DC receptacle',body,'Ports',-2,'black')
    m.cyl('DCJackCenter','DC center contact',.75,6.0,(34,102.8,17),'Ports',-2,'metal',axis=(0,1,0),internal=True)
    _port_cut(m,Part.makeCylinder(4.5,13,V(-29,98,16.8),V(0,1,0)),'RF output shell opening')
    m.ring('RFJackSleeve','RF coaxial outer contact',4.1,3.3,11.7,(-29,98,16.8),'Ports',-2,'metal',axis=(0,1,0))
    m.ring('RFJackInsulator','RF jack dielectric',3.15,1.8,8,(-29,101.6,16.8),'Ports',-2,'white',axis=(0,1,0))
    m.ring('RFJackContact','RF center socket',1.65,1.1,7,(-29,101.8,16.8),'Ports',-2,'metal',axis=(0,1,0))
    for name,x in [('TVGame',8),('Channel',-14)]:
        _port_cut(m,m.rr(10.8,4.6,12,(x,98.5,16.0),.5,rear),name+' selector opening')
        m.box(name+'Switch','Original '+name+' slide switch',11.8,8.0,4.8,(x,100.0,13.6),'PowerRF',-2,'metal',.45,True)
        m.box(name+'Slider','Rear '+name+' selector',3.5,3.8,3.4,(x+1.8,106.3,16.0),'Ports',0,'black',.3,orient=rear)
    plaque=m.rr(94,5.3,.06,(0,110.05,26.7),.3,rear)
    m.feature('RearPortPlate','Black rear interface label strip',plaque,'Body',4,'black')
    for key,word,x in [('DC','AC ADAPTER',44),('Mode','TV / GAME',16),('CH','CH1 / CH2',-6),('RF','RF SWITCH',-25)]:
        pos=V(x,110.14,25.4);m.label('Rear'+key+'Mark',word,1.8,tuple(pos),'Body',4,'white',rotation=rear)
    # Fifteen-position expansion connector with two staggered rows and separate pins.
    profile=[(-17,-4),(17,-4),(15.5,5.5),(-15.5,5.5)]
    outer=_polygon(profile,0,10.5);outer.Placement=App.Placement(V(0,-99.3,16.0),front)
    bore=_polygon([(-15.2,-2.5),(15.2,-2.5),(14.0,4),(-14.0,4)],0,8.8);bore.Placement=App.Placement(V(0,-101.2,16),front)
    m.feature('ExpansionHousing','Fifteen-pin expansion receptacle',outer.cut(bore),'Ports',-2,'fccream')
    _port_cut(m,m.rr(35.6,11.4,12,(0,-98.5,16),1.0,front),'Front expansion aperture')
    for row,count,z in [(0,8,18.4),(1,7,14.6)]:
        for i in range(count):m.cyl('ExpansionPin'+str(row*8+i),'Expansion male contact',.38,7.4,((i-(count-1)/2)*3.5,-101.8,z),'Ports',-2,'gold',axis=(0,-1,0),internal=True)
    # Controller leads loop behind the stored handsets and enter the rear bulkhead.
    for number,side in [(1,-1),(2,1)]:
        x=side*65.3;z=43
        _port_cut(m,Part.makeCylinder(5.2,9,V(side*63,103,20),V(0,1,0)),'Wired controller bulkhead passage')
        m.ring('CableBulkhead'+str(number),'Rear controller cable grommet',4.8,2.2,6.8,(side*63,105.7,20),'Cables',0,'rubber',axis=(0,1,0))
        shape=_tube([(x,89.5,z),(x,99,z),(side*67,119,z-4),(side*70,126,29),(side*67,120,20),(side*63,112.7,20)],1.65)
        m.feature('ControllerCable'+str(number),'Attached controller cable loop',shape,'Cables',0,'black')
    m.profile['stages']=4
    m.checkpoint(4,'rf_dc_expansion_and_attached_cables','加入后部电源口、RF 同轴口、TV/GAME 与频道滑块、前部 15 接点扩展口和两条固定手柄线；接口按原始后面板布局布置。')


STAGES[4]=stage04


def _board_holes(m,board,holes,reason):
    batch=getattr(m,'_pcb_hole_batch',None)
    if batch is None:m.cut(board,holes,reason)
    else:batch.setdefault(board,[]).extend(holes)


def _flush_board_holes(m):
    batch=m._pcb_hole_batch;del m._pcb_hole_batch
    for board,holes in batch.items():m.cut(board,holes,'Batch of component through-hole lead bores')


def _dip(m,key,label,x,y,w,h,pins,z=16.1,t=3.9,assembly='Mainboard',board='Mainboard'):
    m.box(key,label,w,h,t,(x,y,z),assembly,-2,'black',.35,True)
    n=pins//2;leads=[];holes=[]
    for side in [-1,1]:
        for i in range(n):
            xx=x+(i-(n-1)/2)*(w-2)/(n-1);yy=y+side*(h/2+1.1)
            leg=m.rr(.38,.38,4.1,(xx,yy,z-2.1),.02)
            foot=m.rr(.38,1.65,.24,(xx,y+side*(h/2+.90),z+1.8),.02)
            leads.append(leg.fuse(foot));holes.append(Part.makeCylinder(.34,3.5,V(xx,yy,z-2.4)))
    m.feature(key+'Pins','Through-hole DIP leadframe study',Part.makeCompound(leads),assembly,-2,'metal',True)
    if board:_board_holes(m,board,holes,label+' lead holes')
    m.label(key+'Mark',label,min(2.2,w/(len(label)*.65)),(x-w/2+1,y-.7,z+t+.02),assembly,-2,'white')


def stage05(m):
    m.box('Mainboard','HVC-CPU-GPM-02 layout reference PCB',104,137,1.6,(0,-21,14.0),'Mainboard',-2,'pcb',1.5,True)
    m.box('PowerRFBoard','Separate rear power/RF circuit board',96,57,1.6,(0,77,9.5),'PowerRF',-3,'pcb',1.1,True)
    m.label('BoardRevision','HVC-CPU-GPM-02',2.0,(-49,-84,15.62),'Mainboard',-2,'white')
    # The original 60-position connector has a narrow card slot between two contact rows.
    socket=m.rr(82,11.2,12,(0,35,16.2),.8)
    socket=socket.cut(m.rr(78,2.0,10.6,(0,35,18.0),.3))
    carrier=m.rr(104,15,2.0,(0,35,16.2),3.0).cut(m.rr(83,12,2.6,(0,35,15.9),1.0))
    holes=[Part.makeCylinder(1.4,4,V(x,35,15.4)) for x in [-48.5,48.5]]
    m.feature('CardSocketCarrier','Blue cartridge connector mounting frame',carrier.cut(Part.makeCompound(holes)),'CardReader',0,'blue',True)
    channels=[];board_holes=[]
    for side in [-1,1]:
        for i in range(30):
            x=(i-14.5)*2.5;y=35+side*4.2
            leg=m.rr(.5,.38,8.0,(x,y,13.4),.02)
            foot=m.rr(.5,3.2,.22,(x,35+side*2.55,21.1),.02)
            contact=m.rr(.5,.20,4.1,(x,35+side*1.05,21.0),.02)
            m.feature('CardContact'+str((side+1)//2*30+i),'Cartridge spring contact study',leg.fuse(foot).fuse(contact),'CardReader',0,'gold',True)
            channels.extend([m.rr(.75,.70,8.6,(x,y,13.1),.04),m.rr(.75,4.2,4.6,(x,35+side*2.7,20.8),.04)])
            board_holes.append(Part.makeCylinder(.46,2.1,V(x,y,13.8)))
    m.feature('CardSocket','60-position cartridge socket body',socket.cut(Part.makeCompound(channels)),'CardReader',0,'black',True)
    m.cut('Mainboard',board_holes+holes,'Cartridge connector lead and fastening holes')
    for i,x in enumerate([-48.5,48.5]):
        m.screw('CardMountScrew'+str(i),(x,35,18.9),'CardReader',0,length=3.8,radius=2.0,axis=(0,0,-1))
    # Board-side detachable plugs correspond to the permanently attached external leads.
    for number,x,count in [(1,-43,5),(2,43,6)]:
        m.box('ControllerHeader'+str(number),'Controller motherboard header',count*2.0+2,5,3.1,(x,-70,15.9),'Mainboard',-2,'black',.4,True)
        for i in range(count):m.box('ControllerHeaderPin'+str(number)+'_'+str(i),'Controller board contact',.45,3.8,.20,(x+(i-(count-1)/2)*2,-70,19.2),'Mainboard',-2,'gold',.02,True)
    m.profile['stages']=5
    m.checkpoint(5,'logic_board_rf_board_and_sixty_contact_socket','建立主逻辑板、独立电源/RF 板、蓝色卡座支架与 60 个独立弹性接点，并加入两组板端手柄连接器和卡座安装孔。')


def stage06(m):
    # Sliding eject frame: two side arms, two crossbars and a pair of lifting ramps.
    parts=[]
    for side in [-1,1]:
        x=side*49.5
        channel=m.rr(6.0,90,10,(x,-3,29.3),.8).cut(m.rr(3.2,92,5.8,(x,-3,32.5),.45))
        m.feature('EjectGuide'+str(side),'Fixed eject-frame guide',channel,'Mechanism',1,'fccream',True)
        parts.append(m.rr(2.5,77,3.8,(x,-3,33.0),.4))
        ramp=_yz_prism([(22,33.0),(35,33.0),(35,39.3),(32,39.3),(22,35.0)],x-1.25,2.5)
        parts.append(ramp)
    for y in [-34,-19]:parts.append(Part.makeCylinder(2.7,99,V(-49.5,y,35.8),V(1,0,0)))
    frame=parts[0]
    for part in parts[1:]:frame=frame.fuse(part)
    m.feature('EjectCarrier','Sliding crossbar frame with lifting ramps',frame.removeSplitter(),'Mechanism',2,'fccream',True)
    rod=Part.makeCylinder(.65,37,V(0,-70,42.3),V(0,1,0))
    blade=m.rr(1.6,1.5,8.8,(0,-61,42.5),.12)
    catch=m.rr(1.4,1.5,3.6,(0,-34,38.8),.12)
    m.feature('EjectLinkage','Metal pull rod and handle transmission blade',rod.fuse(blade).fuse(catch),'Mechanism',3,'metal',True)
    # Actual helix rather than a solid cylinder; loops and wire are presentation geometry.
    helix=Part.makeHelix(.55,15.0,1.35)
    circle=Part.Wire(Part.makeCircle(.18,helix.Vertexes[0].Point,helix.Edges[0].tangentAt(helix.Edges[0].FirstParameter)))
    spring=Part.Wire(helix.Edges).makePipeShell([circle],True,False)
    spring.Placement=App.Placement(V(0,-87,42.3),App.Rotation(V(0,0,1),V(0,1,0)))
    m.feature('EjectReturnSpring','Eject mechanism helical return spring',spring,'Mechanism',3,'metal',True)
    for key,y in [('Front',-88.6),('Rear',-70.4)]:m.ring('SpringEye'+key,'Spring attachment eye',1.1,.68,.4,(-.2,y,42.3),'Mechanism',3,'metal',axis=(1,0,0),internal=True)
    m.box('SpringAnchor','Front spring anchoring tab',3.2,2.0,2.3,(0,-90.3,40.8),'Mechanism',1,'fccream',.4,True)
    m.box('PowerSwitchBody','Original latching power switch',13,20,8.0,(-38,-70,37.5),'Mechanism',2,'metal',.8,True)
    m.box('PowerSwitchPlunger','Power-cap transmission sleeve',4.5,5.0,7.1,(-38,-75,45.6),'Mechanism',3,'black',.5,True)
    m.box('ResetSwitchBody','Reset contact switch',9,9,3.0,(38,-75,35.8),'Mechanism',2,'black',.5,True)
    m.box('ResetPlunger','Reset-cap transmission sleeve',4.5,4.5,14,(38,-75,39.0),'Mechanism',3,'fccream',.4,True)
    for i,x in enumerate([-47,-29]):
        m.box('PowerSwitchEar'+str(i),'Power-switch mounting ear',4.5,8,.8,(x,-70,41.0),'Mechanism',2,'metal',.5,True)
        m.cut('PowerSwitchEar'+str(i),Part.makeCylinder(1,1.4,V(x,-70,40.8)),'Power-switch fastening hole')
        m.screw('PowerSwitchScrew'+str(i),(x,-70,42.5),'Mechanism',2,length=3.5,radius=1.5,axis=(0,0,-1))
    m.profile['stages']=6
    m.checkpoint(6,'eject_frame_return_spring_and_power_linkage','加入两侧退卡导轨、横梁滑架、抬升斜面、真实螺旋回位弹簧与金属拉杆，并建立电源开关、复位传动柱和固定耳。')


STAGES.update({5:stage05,6:stage06})


def _radial_cap(m,key,x,y,z,r=2.1,h=5.2,assembly='Mainboard',board='Mainboard'):
    m.cyl(key,'Radial electrolytic capacitor',r,h,(x,y,z),assembly,-2,'black',internal=True)
    m.cyl(key+'Top','Capacitor aluminum vent face',r-.15,.12,(x,y,z+h+.04),assembly,-2,'metal',internal=True)
    pins=[Part.makeCylinder(.20,2.8,V(x+side*.8,y,z-2.4)) for side in [-1,1]]
    m.feature(key+'Leads','Radial component leads',Part.makeCompound(pins),assembly,-2,'metal',True)
    _board_holes(m,board,[Part.makeCylinder(.30,3,V(x+side*.8,y,z-2.5)) for side in [-1,1]],'Radial capacitor lead bores')


def _axial_resistor(m,key,x,y,z=17.4,assembly='Mainboard',board='Mainboard'):
    m.colors['fcresistor']=(.57,.44,.23)
    m.cyl(key,'Axial resistor body study',.70,3.4,(x-1.7,y,z),assembly,-2,'fcresistor',axis=(1,0,0),internal=True)
    leads=[]
    for side in [-1,1]:
        wire=Part.makeCylinder(.17,1.9,V(x+side*1.8,y,z),V(side,0,0))
        vertical=Part.makeCylinder(.17,3.9,V(x+side*3.7,y,z-3.8))
        leads.append(wire.fuse(vertical))
    m.feature(key+'Leads','Formed axial component leads',Part.makeCompound(leads),assembly,-2,'metal',True)
    bands=[Part.makeCylinder(.725,.20,V(x+xx,y,z),V(1,0,0)).cut(Part.makeCylinder(.70,.22,V(x+xx-.01,y,z),V(1,0,0))) for xx in [-.85,-.20,.45]]
    m.feature(key+'Bands','Resistor band geometry study',Part.makeCompound(bands),assembly,-2,'black',True)
    _board_holes(m,board,[Part.makeCylinder(.28,3,V(x+side*3.7,y,z-3.9)) for side in [-1,1]],'Axial resistor lead bores')


def stage07(m):
    m._pcb_hole_batch={}
    chips=[('CPU','RP2A03G',-2,-48,49,14,40),('PPU','RP2C02G-0',-5,-23,49,14,40),('VRAM','LH5216D',-21,4,29,8,24),('RAM','LH5216D',20,4,29,8,24),('Buffer0','TC40H368P',-20,-72,20,6.2,16),('Buffer1','TC40H368P',12,-72,20,6.2,16),('Decoder','74LS139',36,-46,19,6.2,16),('Latch','74LS373',36,-22,20,7.0,20)]
    for key,label,x,y,w,h,pins in chips:
        _dip(m,key,label,x,y,w,h,pins)
        pads=[]
        for side in [-1,1]:
            for i in range(pins//2):
                xx=x+(i-(pins//2-1)/2)*(w-2)/(pins//2-1);yy=y+side*(h/2+1.1)
                pad=Part.makeCylinder(.61,.035,V(xx,yy,13.96)).cut(Part.makeCylinder(.34,.05,V(xx,yy,13.95)))
                pads.append(pad)
        m.feature(key+'SolderPads','Underside through-hole solder lands',Part.makeCompound(pads),'Mainboard',-2,'gold',True)
    m.box('MasterCrystal','Master oscillator metal can',6.2,13,4.0,(-42,-22,16.2),'Mainboard',-2,'metal',2.1,True)
    m.label('CrystalMark','XTAL',1.8,(-44.5,-22.7,20.24),'Mainboard',-2,'black')
    for i,(x,y) in enumerate([(-42,-46),(-41,3),(-43,18),(-28,19),(-13,19),(4,19),(20,19),(36,19),(46,3)]):
        _radial_cap(m,'LogicCap'+str(i),x,y,16.1,r=2.0,h=4.8 if i%2 else 6.0)
    for i,x in enumerate([-28,-17,-6,5,16,27,39]):_axial_resistor(m,'FrontResistor'+str(i),x,-83)
    for i,x in enumerate([-36,-24,-12,0,12,24,36]):_axial_resistor(m,'LogicResistor'+str(i),x,-35)
    for i,x in enumerate([-30,-12,6,24,42]):
        # Upright ceramic-disc capacitors are separate from their pair of leads.
        m.cyl('CeramicCap'+str(i),'Ceramic disc capacitor',1.45,.65,(x,-60,17.8),'Mainboard',-2,'fcresistor',axis=(0,1,0),internal=True)
        wires=[Part.makeCylinder(.16,3.9,V(x+side*.6,-59.7,13.6)) for side in [-1,1]]
        m.feature('CeramicLeads'+str(i),'Ceramic capacitor leads',Part.makeCompound(wires),'Mainboard',-2,'metal',True)
        _board_holes(m,'Mainboard',[Part.makeCylinder(.25,2.2,V(x+side*.6,-59.7,13.8)) for side in [-1,1]],'Ceramic capacitor lead bores')
    _flush_board_holes(m)
    m.profile['stages']=7
    m.checkpoint(7,'ricoh_cpu_ppu_memory_and_through_hole_parts','补齐 Ricoh CPU/PPU、两块静态 RAM、总线缓冲器、译码器、锁存器、晶振与穿孔无源件，保留独立引脚和板底焊盘；布局参考指定主板修订版。')


STAGES[7]=stage07


def stage08(m):
    m._pcb_hole_batch={}
    from . import geometry as g
    front=g.rotation((0,-1,0),(0,0,1))
    # Power/RF section remains a separate PCB and removable thin metal cover.
    shield=m.rr(92,54,.45,(0,77,29.35),1.2)
    skirt=m.rr(92,54,18,(0,77,11.4),1.2).cut(m.rr(91.1,53.1,18.4,(0,77,11.2),.75))
    shield=shield.fuse(skirt)
    shield=shield.cut(m.rr(27,21,23,(25,61.5,10.9),1.0))
    shield=shield.cut(Part.makeCylinder(2.0,2,V(-8,78,29)))
    for key in ['DCJackBody','DCJackCenter','RFJackSleeve','RFJackInsulator','RFJackContact','TVGameSwitch','ChannelSwitch']:
        shield=shield.cut(m.parts[key].Shape)
    m.feature('RFShield','Removable power/RF metal enclosure',shield,'PowerRF',1,'metal',True)
    heatsink=m.rr(25,12,.65,(25,62,11.4),.5).fuse(m.rr(25,.65,20,(25,56.3,11.4),.25))
    bolt=Part.makeCylinder(1.0,8,V(25,62,28.0),V(0,-1,0));heatsink=heatsink.cut(bolt)
    m.feature('RegulatorHeatsink','Folded regulator heat spreader',heatsink,'PowerRF',0,'metal',True)
    m.box('RegulatorBody','Linear 5 V regulator package study',10,10,3,(25,60,20),'PowerRF',0,'black',.45,True,orient=front)
    tab=m.rr(10,6,.7,(25,59.5,28.2),.5,front).cut(bolt)
    m.feature('RegulatorTab','Regulator metal mounting tab',tab,'PowerRF',0,'metal',True)
    fast=m.screw('RegulatorScrew',(0,0,0),'PowerRF',0,length=4.8,radius=1.6)
    fast.Placement=App.Placement(V(25,60.0,28.0),front);fast.FlatPlacement=fast.Placement
    for i,x in enumerate([22.5,25,27.5]):
        m.box('RegulatorLead'+str(i),'Regulator formed lead',.50,.40,4.5,(x,58.5,10.1),'PowerRF',0,'metal',.02,True)
        m.cut('PowerRFBoard',Part.makeCylinder(.40,2.0,V(x,58.5,9.3)),'Regulator lead bore')
    for i,(x,y) in enumerate([(-30,60),(-11,60),(-31,78),(-7,87),(19,91),(38,81)]):
        _radial_cap(m,'RFCap'+str(i),x,y,11.6,r=2.9 if i in [0,2] else 2.0,h=10.0 if i in [0,2] else 6.0,assembly='PowerRF',board='PowerRFBoard')
    for i,(x,y) in enumerate([(-19,69),(0,70),(11,80)]):
        m.cyl('RFTransistor'+str(i),'RF transistor case study',1.7,3.8,(x,y,11.6),'PowerRF',-2,'black',internal=True)
        leads=[Part.makeCylinder(.15,2.9,V(x+(j-1)*.9,y,9.0)) for j in range(3)]
        m.feature('RFTransistorLeads'+str(i),'Transistor through-hole pins',Part.makeCompound(leads),'PowerRF',-2,'metal',True)
        m.cut('PowerRFBoard',[Part.makeCylinder(.25,2,V(x+(j-1)*.9,y,9.3)) for j in range(3)],'Transistor lead holes')
    for i,(x,y) in enumerate([(-7,78),(11,63)]):
        m.cyl('RFCoilCore'+str(i),'RF tuning coil ferrite core',1.0,5.0,(x,y,11.7),'PowerRF',-2,'black',internal=True)
        helix=Part.makeHelix(.55,4.0,1.65);wire=Part.Wire(Part.makeCircle(.16,helix.Vertexes[0].Point,helix.Edges[0].tangentAt(helix.Edges[0].FirstParameter)))
        coil=Part.Wire(helix.Edges).makePipeShell([wire],True,False);coil.translate(V(x,y,12.1))
        m.feature('RFCoilWinding'+str(i),'RF tuning coil winding',coil,'PowerRF',-2,'copper',True)
    for i,(x,y) in enumerate([(-34,94),(-20,92),(-5,95),(34,94)]):_axial_resistor(m,'RFResistor'+str(i),x,y,z=12.9,assembly='PowerRF',board='PowerRFBoard')
    # Two short bridges show the board interface without claiming a netlist.
    for side in [-1,1]:
        for i in range(3):
            x=side*(39+i*2.0)
            wire=_tube([(x,44,13.0),(x,47.7,12.5),(x,50.5,10.8),(x,53,10.8)],.18)
            m.feature('RFBoardBridge'+str(side)+'_'+str(i),'Board-to-board interconnect study',wire,'Wiring',-2,'metal',True)
            _board_holes(m,'Mainboard',[Part.makeCylinder(.28,3,V(x,44,13.0))],'Logic board bridge via')
            _board_holes(m,'PowerRFBoard',[Part.makeCylinder(.28,2,V(x,53,9.3))],'RF board bridge via')
    _flush_board_holes(m)
    m.profile['stages']=8
    m.checkpoint(8,'rf_modulator_regulator_and_shield','建立独立 RF/电源板的金属罩、线性稳压器与折弯散热片、调谐线圈、晶体管及穿孔元件，并用独立线段说明板间互连。')


STAGES[8]=stage08


def _controller_pose(side):
    mat=App.Matrix();mat.A11,mat.A21,mat.A31=0,side,0;mat.A12,mat.A22,mat.A32=0,0,1;mat.A13,mat.A23,mat.A33=side,0,0
    return App.Placement(V(side*58.8,21.5,33),App.Rotation(mat))


def _controller_electronics(m,number,side):
    m._pcb_hole_batch={}
    prefix='P'+str(number);group='Controller'+str(number);before=set(m.parts);q=_controller_pose(side)
    m.colors['fcmembrane']=(.61,.64,.52)
    board=prefix+'PCB';m.box(board,'Controller '+str(number)+' phenolic PCB study',121,47.2,1.0,(0,0,3.4),group,-2,'pcb',2.7,True)
    mounts=[Part.makeCylinder(2.25,1.6,V(x,y,3.1)) for x in [-52,52] for y in [-17,17]]
    m.cut(board,mounts,'Controller board mounting-post clearances')
    for i,(x,y) in enumerate([(x,y) for x in [-52,52] for y in [-17,17]]):m.ring(prefix+'Post'+str(i),'Controller case fastening post',2.1,.90,9.9,(x,y,1.4),group,0,'fcred',internal=True)
    # Connected silicone mats, separate conductive pills, PCB contacts and cap stems.
    m.cyl(prefix+'DPadMat','Directional silicone mat',11.0,.75,(-44,-6,5.1),group,1,'fcmembrane',internal=True)
    buttons=[('Up',-44,0),('Right',-38,-6),('Down',-44,-12),('Left',-50,-6),('B',29,-8),('A',47,-8)]
    action=Part.makeCylinder(7.0,.8,V(29,-8,5.1)).fuse(Part.makeCylinder(7,.8,V(47,-8,5.1))).fuse(m.rr(18,4,.8,(38,-8,5.1),.6))
    m.feature(prefix+'ActionMat','Connected action-button silicone mat',action,group,1,'fcmembrane',True)
    for key,x,y in buttons:
        r=2.5 if key not in ['A','B'] else 3.6
        m.cyl(prefix+key+'Contact','PCB button contact',r+.35,.045,(x,y,4.46),group,-2,'gold',internal=True)
        m.cyl(prefix+key+'Pill','Conductive rubber pill',r,.32,(x,y,4.60),group,1,'black',internal=True)
        m.cyl(prefix+key+'Stem','Button transmission stem',1.4 if key not in ['A','B'] else 3.4,7.35,(x,y,5.95),group,3,'fcmembrane',internal=True)
    if number==1:
        m.box(prefix+'SystemMat','Connected system-button mat',36,8,.8,(-3.5,-8,5.1),group,1,'fcmembrane',2.0,True)
        for name,x in [('Select',-14),('Start',7)]:
            m.box(prefix+name+'Contact','System-button contact',8.3,3.4,.045,(x,-8,4.46),group,-2,'gold',1.0,True)
            m.box(prefix+name+'Pill','System-button conductive rubber',8.0,3.1,.32,(x,-8,4.60),group,1,'black',.9,True)
            m.box(prefix+name+'Stem','System-button transmission stem',6.8,2.7,7.25,(x,-8,5.95),group,3,'fcmembrane',.8,True)
        _dip(m,prefix+'ShiftRegister','4021',0,14,20,6.2,16,z=4.8,t=2.9,assembly=group,board=board)
    else:
        _dip(m,prefix+'ShiftRegister','4021',28,15,20,6.2,16,z=4.8,t=2.9,assembly=group,board=board)
        m.cyl(prefix+'Microphone','Player-II electret microphone capsule',6.6,4.8,(0,12.5,5.1),group,1,'metal',internal=True)
        m.cyl(prefix+'MicDiaphragm','Microphone diaphragm',5.7,.15,(0,12.5,9.96),group,2,'black',internal=True)
        m.box(prefix+'VolumePot','Microphone sliding potentiometer',20,4.2,3.4,(-35,18,4.8),group,1,'black',.6,True)
        m.box(prefix+'VolumeLink','Volume-slider transmission tab',5.8,2.7,4.45,(-38,18,8.6),group,3,'fcmembrane',.3,True)
    # The two internal plug/wire sets differ by the extra microphone conductor.
    cable_side=-1 if number==1 else 1;count=5 if number==1 else 6
    m.box(prefix+'CableHeader','Controller cable termination',count*1.7+2,3.1,2.0,(cable_side*43,17.5,4.8),group,-2,'black',.4,True)
    for i in range(count):
        y=8.6+i*.5;endx=cable_side*43+(i-(count-1)/2)*1.7
        path=_tube([(cable_side*61,y,6.5),(cable_side*54,y+1,6.1),(endx,13.8,6.0),(endx,15.8,6.0)],.15)
        m.feature(prefix+'CableWire'+str(i),'Controller cable conductor study',path,group,-2,['red','white','black','blue','gold','copper'][i],True)
    for i,(x,y) in enumerate([(-24,11),(-16,19),(18,-18)]):
        m.box(prefix+'Passive'+str(i),'Controller passive component',2.8,1.4,1.3,(x,y,4.8),group,-2,'black',.15,True)
        m.feature(prefix+'PassiveEnds'+str(i),'Controller passive terminations',Part.makeCompound([m.rr(.35,1.3,1.2,(x+side*1.65,y,4.8),.02) for side in [-1,1]]),group,-2,'metal',True)
    m.label(prefix+'PCBMark','CONTROLLER '+str(number),1.6,(-15,-21,4.44),group,-2,'white')
    _flush_board_holes(m)
    for key in set(m.parts)-before:
        obj=m.parts[key];obj.Placement=q.multiply(obj.Placement);obj.FlatPlacement=obj.Placement


def stage09(m):
    _controller_electronics(m,1,-1);_controller_electronics(m,2,1)
    m.profile['stages']=9
    m.checkpoint(9,'controller_pcbs_membranes_and_microphone','建立两块手柄 PCB、移位寄存器、连体硅胶垫、导电粒与传动柱，并为二号手柄加入麦克风胶囊、电位器和独立线束。')


STAGES[9]=stage09


def stage10(m):
    from .clamshell import _replace,_move
    from . import geometry as g
    # Route stored-controller cables around the rear shoulders with explicit wire clearances.
    for number,side in [(1,-1),(2,1)]:
        x=side*65.3
        route=[(x,89.5,43),(side*68,93,43),(side*79,98,43),(side*85,112,39),(side*79,126,25),(side*66,121,20),(side*63,112.7,20)]
        shape=_tube(route,1.65);_replace(m,'ControllerCable'+str(number),shape)
        m.cut('UpperShell',m.rr(21,13,60,(side*67,92,6.3),2.2),'Rear continuation of controller cable storage channel')
        m.cut('P'+str(number)+'CableGrommet',shape,'Controller cable seating recess in strain relief')
    m.cut('P2GoldPlate',m.parts['P2MicField'].Shape,'Gold faceplate clearance around raised microphone field')
    m.cut('Mainboard',[Part.makeCylinder(1.4,6,V(x,35,13.7)) for x in [-48.5,48.5]],'Cartridge fastener bores through full PCB thickness')
    for side in [-1,1]:
        x=side*49.5
        guide=m.rr(6,90,10,(x,-3,29.3),.8).cut(m.rr(3.2,92,16,(x,-3,32.5),.45))
        _replace(m,'EjectGuide'+str(side),guide)
    # The pull rod and its eye form one physical bent-metal piece.
    eye=m.parts.pop('SpringEyeRear');_replace(m,'EjectLinkage',m.parts['EjectLinkage'].Shape.fuse(eye.Shape))
    eye.PhysicalPart=False;eye.Visibility=False
    m.cut('SpringAnchor',m.parts['SpringEyeFront'].Shape,'Spring-eye anchoring seat')
    for key in list(m.parts):
        if key.startswith(('LogicCap','RFCap')) and key+'Leads' in m.parts:
            m.cut(key,m.parts[key+'Leads'].Shape,'Radial leads seated within capacitor package')
        if key.startswith('RFTransistor') and key[len('RFTransistor'):].isdigit():
            m.cut(key,m.parts['RFTransistorLeads'+key[len('RFTransistor'):]].Shape,'Transistor lead encapsulation seats')
        if key.startswith('CeramicCap') and key[len('CeramicCap'):].isdigit():
            m.cut(key,m.parts['CeramicLeads'+key[len('CeramicCap'):]].Shape,'Ceramic capacitor lead seats')
    rear=g.rotation((0,1,0),(0,0,1))
    m.cut('UpperShell',m.rr(94.5,5.8,.55,(0,109.7,26.7),.4,rear),'Flush rear specification-label recess')
    for key in ['RearPortPlate','RearDCMark','RearModeMark','RearCHMark','RearRFMark']:
        _move(m,key,(0,-.2,0))
    m.profile['envelope_groups']=[a for a in m.groups if a not in ['Cables','Wiring','Accessories','Construction']]
    m.profile['stages']=10
    m.checkpoint(10,'cable_routing_and_mechanism_service_clearances','根据实体求交修正线缆绕行、卡座孔深、退卡导轨开口与回位弹簧接口；分离封装和引脚占据的空间，并将后部标识嵌入机壳基准。')


STAGES[10]=stage10


def stage11(m):
    m._pcb_hole_batch={}
    from .clamshell import _replace,_move
    _move(m,'BoardRevision',(0,-3.0,0))
    # Six outer-case fasteners and six mainboard mounts remain separately traceable.
    for side in [-1,1]:
        for j,(y,top) in enumerate([(-94,42.2),(-10,50.5),(98,44.8)]):
            x=side*55.5;key='CaseBoss'+str(side)+'_'+str(j)
            m.ring(key,'Case fastening post',2.3,.85,top-4.8,(x,y,4.8),'Internal',0,'fccream',internal=True)
            m.cut('UpperShell',m.parts[key].Shape,'Case-post seating into upper enclosure')
            bore=Part.makeCylinder(.90,3,V(x,y,2.1)).fuse(Part.makeCylinder(2.25,1.1,V(x,y,2.1)))
            m.cut('BottomCover',bore,'Recessed outer-case screw access')
            m.screw('CaseScrew'+str(side)+'_'+str(j),(x,y,2.65),'Body',-6,length=5.5,radius=2.1)
        for j,y in enumerate([-82,-8,43]):
            x=side*48
            m.ring('BoardPost'+str(side)+'_'+str(j),'Mainboard mounting spacer',2.4,.85,8.95,(x,y,4.8),'Internal',-3,'fccream',internal=True)
            _board_holes(m,'Mainboard',[Part.makeCylinder(.90,2.3,V(x,y,13.7))],'Mainboard service screw through-hole')
            m.ring('BoardWasher'+str(side)+'_'+str(j),'Mainboard mounting washer',2.7,1.0,.30,(x,y,15.9),'Mainboard',-2,'metal',internal=True)
            m.screw('BoardScrew'+str(side)+'_'+str(j),(x,y,16.9),'Mainboard',-2,length=4.8,radius=2.1,axis=(0,0,-1))
        for j,y in enumerate([53,100]):
            x=side*42
            m.ring('RFPost'+str(side)+'_'+str(j),'Rear board mounting spacer',2.3,.85,4.4,(x,y,4.8),'Internal',-3,'fccream',internal=True)
            _board_holes(m,'PowerRFBoard',[Part.makeCylinder(.9,2.1,V(x,y,9.3))],'Rear board mounting hole')
            m.screw('RFScrew'+str(side)+'_'+str(j),(x,y,12.5),'PowerRF',-3,length=4.0,radius=1.8,axis=(0,0,-1))
    for i,side in [(0,-1),(1,1),(2,-1),(3,1)]:
        shape=m.parts['RubberFoot'+str(i)].Shape.copy();shape.translate(V(-side*20,0,0));_replace(m,'RubberFoot'+str(i),shape)
    vents=[m.rr(1.5,22,3,(-27.3+i*4.2,-50,2.1),.45) for i in range(14)]
    m.cut('BottomCover',vents,'Bottom-cover ventilation grille')
    # Insulated internal harnesses follow the side corridors, above board components.
    for number,side in [(1,-1),(2,1)]:
        route=[(side*63,104.5,20),(side*54,96,20),(side*51,81,20),(side*51,-48,20),(side*49,-59,20),(side*43,-63.5,20)]
        m.feature('InternalCable'+str(number),'Internal controller cable harness',_tube(route,.65),'Wiring',-2,'black',True)
        for i in range(5 if number==1 else 6):
            x=side*43+(i-2)*1.2
            wire=_tube([(x,-63.7,20),(x,-65.5,19.8),(x,-67.1,19.3)],.15)
            m.feature('HeaderWire'+str(number)+'_'+str(i),'Controller header conductor',wire,'Wiring',-2,['red','white','black','blue','gold','copper'][i],True)
    for i in range(3):
        wire=_tube([(-36+i*1.5,-62,38),(-40+i*1.5,-57,30),(-45+i,-52,24),(-45+i,22,24),(-44+i,45,20),(-37+i,52,13)],.27)
        m.feature('PowerHarness'+str(i),'Power-switch wire study',wire,'Wiring',-2,['red','white','black'][i],True)
    _flush_board_holes(m)
    m.profile['stages']=11
    m.checkpoint(11,'service_posts_fasteners_and_internal_harnesses','补齐六处机壳螺钉、六处主板安装位、后部板架与垫片，调整脚垫位置并加入底部散热槽、固定手柄内线和电源线束。')


STAGES[11]=stage11


def stage12(m):
    from .psp import _polygon
    from .clamshell import _replace
    x=165.0;group='Accessories';m._pcb_hole_batch={}
    m.native('GamePakBack','Blank Famicom cartridge rear half',108,72,3.4,1.2,(x,0,0),group,-5,'fcred')
    m.native('GamePakFrame','Cartridge clip enclosure',108,72,3.4,13.2,(x,0,1.3),group,0,'fcred')
    m.cut('GamePakFrame',m.rr(104.4,68.4,13.6,(x,0,1.1),1.6),'Cartridge board cavity')
    m.native('GamePakFront','Cartridge face half',107.8,71.8,3.3,1.2,(x,0,14.6),group,4,'fcred')
    for key,z,t in [('GamePakFront',14.4,2),('GamePakBack',-.2,2),('GamePakFrame',1.1,14)]:
        m.cut(key,m.rr(98,12,t,(x,-32,z),1.2),'Open cartridge edge-connector mouth')
    outline=[(-50,-29),(-43,-29),(-43,-33.5),(43,-33.5),(43,-29),(50,-29),(50,14),(-50,14)]
    board=_polygon([(x+xx,y) for xx,y in outline],6.5,1.0)
    m.feature('GamePakPCB','Blank sixty-contact ROM cartridge PCB',board,group,-2,'pcb',True)
    for face,z in [('Front',7.55),('Rear',6.42)]:
        for i in range(30):m.box('GamePakContact'+face+str(i),'Cartridge edge contact',1.4,6.8,.05,(x+(i-14.5)*2.5,-29.6,z),group,-2,'gold',.07,True)
    _dip(m,'GamePakPRG','PRG STUDY',x-24,-2,35,10,28,z=7.9,t=3.9,assembly=group,board='GamePakPCB')
    _dip(m,'GamePakCHR','CHR STUDY',x+24,-2,35,10,28,z=7.9,t=3.9,assembly=group,board='GamePakPCB')
    _flush_board_holes(m)
    for i,(xx,y) in enumerate([(-51.2,-16),(-51.2,17),(51.2,-16),(51.2,17)]):
        m.box('GamePakClip'+str(i),'Cartridge retaining clip',1.4,3,5.8,(x+xx,y,8.65),group,3,'fcred',.3,True)
    for i in range(17):m.cut('GamePakFront',m.rr(.55,4.2,.25,(x-40+i*5,31,15.62),.13),'Cartridge finger-grip groove')
    m.box('GamePakLabel','Blank study label',87,41,.10,(x,5.5,15.84),group,4,'white',1.3)
    m.label('GamePakTitle','FAMICOM STUDY',4.4,(x-37,13,15.98),group,4,'black')
    m.label('GamePakSubtitle','60 CONTACTS / CAD',2.6,(x-30,2,15.98),group,4,'black')
    m.label('GamePakNoROM','NO GAME DATA',2.8,(x-24,-9,15.98),group,4,'black')
    # Roman controller identifiers match the original I/II markings.
    for number,side,word in [(1,-1,'I'),(2,1,'II')]:
        key='P'+str(number)+'Number';old=m.parts.pop(key);old.PhysicalPart=False;old.Visibility=False
        obj=m.label(key,word,4.0,(-55,13.5,13.12),'Controller'+str(number),4,'fcink')
        obj.Placement=_controller_pose(side).multiply(obj.Placement);obj.FlatPlacement=obj.Placement
    m.profile['stages']=12
    m.checkpoint(12,'blank_sixty_contact_game_pak','建立独立空白 FC 卡带的分壳、卡扣、60 个接点、PCB 和 PRG/CHR 封装示意，使用学习标签；同时将手柄编号修正为原版 I/II。')


def stage13(m):
    group='Accessories';x,y=165,100
    # HVC-002-type 10 V adapter exterior; internal transformer is a dimensional study.
    m.native('AdapterFront','AC adapter front half',63,49,4.0,1.3,(x,y,0),group,-5,'black')
    m.native('AdapterShell','AC adapter casing',63,49,4.0,32.4,(x,y,1.4),group,0,'black')
    m.cut('AdapterShell',m.rr(59.4,45.4,32.8,(x,y,1.2),2.2),'Adapter internal cavity')
    m.native('AdapterBack','AC adapter back half',62.8,48.8,3.9,1.2,(x,y,33.9),group,4,'black')
    for i,xx in enumerate([-6.3,6.3]):
        blade=m.rr(5.9,1.2,13.6,(x+xx,y,-13.5),.2)
        blade=blade.cut(Part.makeCylinder(1.3,2,V(x+xx,y-1,-10.0),V(0,1,0)))
        m.feature('AdapterACBlade'+str(i),'Parallel AC blade study',blade,group,-5,'metal')
        m.cut('AdapterFront',m.rr(6.2,1.5,2,(x+xx,y,-.2),.2),'AC blade seating slot')
    core=m.rr(43,29,22,(x,y,4.0),.8).cut(m.rr(24,18,23,(x,y,3.8),.5))
    core=core.fuse(m.rr(43,29,1.5,(x,y,3.9),.8)).fuse(m.rr(11,7,21,(x,y,5.3),.4))
    m.feature('AdapterTransformerCore','Transformer core envelope study',core,group,0,'metal',True)
    coil=m.rr(22,16,19.5,(x,y,5.7),1.2).cut(m.rr(12,8,20,(x,y,5.5),.8))
    m.feature('AdapterTransformerWinding','Transformer winding volume study',coil,group,0,'copper',True)
    m.box('AdapterPCB','Adapter secondary-side board study',44,32,1.1,(x,y,27.0),group,1,'pcb',1.0,True)
    m.box('AdapterRectifier','Rectifier envelope study',12,8,3.4,(x-11,y,28.3),group,2,'black',.6,True)
    m.cyl('AdapterFilterCap','Filter capacitor study',4.0,4.7,(x+11,y,28.3),group,2,'black',internal=True)
    m.box('AdapterLabel','Adapter rating label',45,26,.10,(x,y,35.15),group,4,'white',1.0)
    for key,text,size,xx,yy in [('Model','HVC-002 STUDY',2.6,-19,6),('Output','DC 10 V / 850 mA',2.1,-19,-1),('Type','GEOMETRY ONLY',1.9,-16,-8)]:m.label('Adapter'+key,text,size,(x+xx,y+yy,35.29),group,4,'black')
    m.cyl('AdapterStrainRelief','Adapter cable strain relief',2.7,7.5,(196.6,100,18),group,0,'black',axis=(1,0,0))
    route=[(204.2,100,18),(216,103,17),(230,87,10),(225,63,8),(215.7,55,8)]
    m.feature('AdapterCable','Adapter output-cable segment',_tube(route,1.35),group,0,'black')
    m.cyl('AdapterPlugRelief','DC plug strain relief',2.1,9.6,(206,55,8),group,0,'black',axis=(1,0,0))
    m.cyl('AdapterPlugBody','DC barrel plug grip',3.4,7,(198.8,55,8),group,0,'black',axis=(1,0,0))
    m.ring('AdapterPlugMetal','DC barrel contact',2.5,.95,8.5,(190.1,55,8),group,0,'metal',axis=(1,0,0))
    # Original cream RF switch box with exposed antenna clamp terminals.
    x,y=165,176
    m.native('RFSwitchBack','RF switch-box bottom',56,44,4,1.2,(x,y,0),group,-5,'fccream')
    m.native('RFSwitchShell','RF switch-box shell',56,44,4,14.0,(x,y,1.3),group,0,'fccream')
    m.cut('RFSwitchShell',m.rr(52.4,40.4,14.4,(x,y,1.1),2.2),'RF switch-box cavity')
    m.native('RFSwitchFace','RF switch-box terminal face',55.8,43.8,3.9,1.2,(x,y,15.4),group,4,'fccream')
    for i,(xx,yy) in enumerate([(144,184),(158,184),(151,168)]):
        plate=m.rr(8,8,.30,(xx,yy,16.68),.5).cut(Part.makeCylinder(.9,.6,V(xx,yy,16.5)))
        m.feature('AntennaClamp'+str(i),'Antenna terminal clamp plate',plate,group,4,'metal')
        m.cyl('AntennaTerminal'+str(i),'Antenna screw-terminal post',.75,12,(xx,yy,4.4),group,0,'metal',internal=True)
        m.cut('RFSwitchFace',Part.makeCylinder(1.0,2,V(xx,yy,15.2)),'Antenna screw-terminal opening')
        m.ring('AntennaNut'+str(i),'Knurled antenna terminal nut',2.4,.9,1.5,(xx,yy,17.15),group,5,'metal')
    m.box('RFSwitchLabel','RF switch routing label',23,35,.10,(178,176,16.7),group,4,'fcgold',1.0)
    m.label('RFSwitchTitle','RF SWITCH',2.2,(168,186,16.84),group,4,'black')
    m.label('RFSwitchTV','TV / VHF',1.9,(170,177,16.84),group,4,'black')
    m.label('RFSwitchAntenna','ANTENNA',1.9,(168,166,16.84),group,4,'black')
    m.feature('RFInputCable','Console-to-RF-switch cable segment',_tube([(193.2,171,9),(203,168,9),(209,158,8),(213,151,8)],1.0),group,0,'black')
    m.cyl('RFPlugBody','RF male-plug grip',3.0,8,(213.1,151,8),group,0,'black',axis=(1,0,0))
    m.ring('RFPlugSleeve','RF male outer sleeve',2.8,2.1,5,(221.3,151,8),group,0,'metal',axis=(1,0,0))
    m.cyl('RFPlugPin','RF male center pin',.85,6.7,(221.3,151,8),group,0,'metal',axis=(1,0,0))
    m.feature('RFTVCable','RF switch television lead segment',_tube([(166,198.2,9),(166,209,9),(184,219,8),(201,213,8)],1.1),group,0,'black')
    # The supplied 75/300-ohm converter is shown with its fork-ended twin lead.
    m.box('AntennaConverter','75 / 300 ohm converter body study',18,12,10,(232,186,0),group,0,'black',1.7)
    m.label('ConverterMark','300',2.6,(227,184.7,10.04),group,0,'white')
    for side in [-1,1]:
        xx=232+side*5
        m.cyl('ConverterLead'+str(side),'Converter twin lead',.60,21,(xx,192.2,6),group,0,'black',axis=(0,1,0))
        fork=m.rr(4.5,7,.35,(xx,216.8,5.8),.5).cut(m.rr(1.7,4.6,.7,(xx,218.5,5.6),.7))
        m.feature('ConverterFork'+str(side),'Fork antenna terminal',fork,group,0,'metal')
    m.profile['stages']=13
    m.checkpoint(13,'ac_adapter_rf_switch_and_antenna_converter','加入 10 V 电源适配器、直流插头、RF 转接盒、天线压线端子和 75/300 Ω 转换器；附件尺寸和内部体块均为近似学习示意。')


STAGES.update({12:stage12,13:stage13})


def stage14(m):
    from .clamshell import _replace,_move
    # Keep the button stems below the separate caps and open the volume-track slot.
    for number,side in [(1,-1),(2,1)]:
        q=_controller_pose(side)
        for letter,x in [('B',29),('A',47)]:
            stem=Part.makeCylinder(3.4,7.25,V(x,-8,5.95));stem.Placement=q.multiply(stem.Placement)
            _replace(m,'P'+str(number)+letter+'Stem',stem)
        cable_side=-1 if number==1 else 1;count=5 if number==1 else 6
        for i in range(count):
            z=6.5+(i-(count-1)/2)*.45;endx=cable_side*43+(i-(count-1)/2)*1.7
            path=_tube([(cable_side*61,9.8,z),(cable_side*54,10.3,z),(endx,13.0,z),(endx,15.8,z)],.15)
            path.Placement=q.multiply(path.Placement);_replace(m,'P'+str(number)+'CableWire'+str(i),path)
    m.cut('P2VolumeTrack',m.parts['P2VolumeLink'].Shape,'Volume transmission slot through the track backing')
    q=_controller_pose(1);delta=q.Rotation.multVec(V(-4,0,0))
    for key in ['P2ShiftRegister','P2ShiftRegisterPins','P2ShiftRegisterMark']:_move(m,key,tuple(delta))
    holes=[]
    for side in [-1,1]:
        for i in range(8):
            tool=Part.makeCylinder(.34,1.8,V(24+(i-3.5)*18/7,15+side*4.2,3.1));tool.Placement=q.multiply(tool.Placement);holes.append(tool)
    m.cut('P2PCB',holes,'Revised shift-register lead locations clear the cable header')
    # The frame crossbars need openings in the inner guide cheeks.
    for side in [-1,1]:
        windows=[m.rr(3.2,13.5,6.6,(side*47.4,y,32.8),.4) for y in [-34,-19]]
        m.cut('EjectGuide'+str(side),windows,'Crossbar travel windows in fixed guide cheeks')
    m.cut('RegulatorHeatsink',[Part.makeCylinder(.45,1.6,V(x,58.5,11.1)) for x in [22.5,25,27.5]],'Regulator leads clear folded heat-spreader foot')
    for key in ['RFCoilCore1','RFCoilWinding1']:_move(m,key,(-1,0,0))
    bridges=[o.Shape for k,o in m.parts.items() if k.startswith('RFBoardBridge')]
    m.cut('PowerRFBoard',bridges,'Angled board-interconnect lead passages')
    # Rear motherboard screws sit just beyond the cartridge-carrier edge.
    for side in [-1,1]:
        for prefix in ['BoardPost','BoardWasher','BoardScrew']:_move(m,prefix+str(side)+'_2',(0,1.8,0))
    m.cut('Mainboard',[Part.makeCylinder(.9,2.3,V(x,44.8,13.7)) for x in [-48,48]],'Revised rear motherboard fastening holes')
    power=[m.parts['PowerHarness'+str(i)].Shape for i in range(3)]
    m.cut('PowerSwitchBody',power,'Power-switch terminal entry seats')
    m.cut('RFShield',power,'Power-harness entry apertures through RF shield')
    for number,side in [(1,-1),(2,1)]:
        route=[(side*63,112.45,20),(side*63,104.5,20),(side*63,95.5,20),(side*54,91,20),(side*51,80,20),(side*51,-48,20),(side*49,-59,20),(side*43,-63.5,20)]
        _replace(m,'InternalCable'+str(number),_tube(route,.65))
        for i in range(5 if number==1 else 6):_move(m,'HeaderWire'+str(number)+'_'+str(i),(0,-.7,0))
    m.profile.update(main_step_suffix='Console',controls_groups=['Controls','Mechanism','Controller1','Controller2'],explode_axes={'Controller1':[-1,0,0],'Controller2':[1,0,0]},explode_group_offsets={'Controller1':[-360,0,0],'Controller2':[360,0,0]})
    m.profile['internal_exclude']=['UpperShell','CartridgeDustFlap','DustFlapRearRidge','FrontNameplate','FamilyComputerWord','NintendoWord','POWERMark','RESETMark','EjectMark','RearPortPlate','RearDCMark','RearModeMark','RearCHMark','RearRFMark','RFShield']
    m.profile['internal_normal']=[.4,-.3,2.4]
    m.profile['stages']=14
    m.checkpoint(14,'controller_wire_fanout_and_guide_crossbar_clearance','分开手柄导线层并调整二号寄存器位置，修正按键柱、音量传动槽、导轨横梁开口及稳压器引脚间隙，记录主机与手柄各自的爆炸方向。')


STAGES[14]=stage14



def stage15(m):
    from .clamshell import _replace
    # End tangents align the flexible cable faces with their cylindrical terminations.
    cable=_tube([(204.2,100,18),(216,103,17),(230,87,10),(225,63,8),(215.7,55,8)],1.35,[(1,0,0),(-1,0,0)])
    _replace(m,'AdapterCable',cable)
    _replace(m,'AdapterStrainRelief',Part.makeCylinder(2.7,8.3,V(195.8,100,18),V(1,0,0)))
    m.cut('AdapterShell',Part.makeCylinder(2.85,1.4,V(195.4,100,18),V(1,0,0)),'Adapter strain-relief mounting aperture')
    rf=_tube([(191.1,171,9),(200,171,9),(205,157,8),(208,151,8),(213.0,151,8)],1.0,[(1,0,0),(1,0,0)])
    _replace(m,'RFInputCable',rf)
    m.cut('RFSwitchShell',Part.makeCylinder(1.15,2.6,V(190.9,171,9),V(1,0,0)),'RF input cable inlet')
    tv=_tube([(166,196.1,9),(166,209,9),(184,219,8),(201,213,8)],1.1,[(0,1,0),(1,0,0)])
    _replace(m,'RFTVCable',tv)
    m.cut('RFSwitchShell',Part.makeCylinder(1.25,2.5,V(166,196.0,9),V(0,1,0)),'RF television lead inlet')
    m.profile['stages']=15
    m.checkpoint(15,'aligned_accessory_cable_terminations','约束附件线缆的端部切线，使电源和 RF 插头接线方向一致，并补齐适配器与 RF 盒的线缆入口和护套安装孔。')


STAGES[15]=stage15


def stage16(m):
    from .clamshell import _replace
    # Keep a solid floor under the original circular concavity, rather than piercing the cap.
    for number,side in [(1,-1),(2,1)]:
        q=_controller_pose(side)
        for letter,x in [('B',29),('A',47)]:
            cap=Part.makeCylinder(5.3,1.35,V(x,-8,13.25)).cut(Part.makeSphere(8,V(x,-8,22.0)))
            cap.Placement=q.multiply(cap.Placement)
            assert cap.isInside(q.multVec(V(x,-8,13.6)),1e-6,True)
            assert not cap.isInside(q.multVec(V(x,-8,14.4)),1e-6,True)
            _replace(m,'P'+str(number)+letter,cap)
    m.profile['stages']=16
    m.checkpoint(16,'solid_floors_under_concave_action_buttons','修正四枚 A/B 键的凹面深度，保留帽底实体，并以凹面内外取样点核对按键帽的真实剖面。')


STAGES[16]=stage16
