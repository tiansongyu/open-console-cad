"""Original Japanese SCPH-10000: native stepped enclosure and staged internals."""
import FreeCAD as App
import Part
from .core import V
from . import geometry as g


def _line_mark(points,width,z):
    strips=[]
    for a,b in zip(points,points[1:]):
        if a[1]==b[1]:strips.append(Part.makeBox(abs(b[0]-a[0])+width,width,.018,V(min(a[0],b[0])-width/2,a[1]-width/2,z)))
        else:strips.append(Part.makeBox(width,abs(b[1]-a[1])+width,.018,V(a[0]-width/2,min(a[1],b[1])-width/2,z)))
    shape=strips[0].multiFuse(strips[1:]).removeSplitter()
    shape.rotate(V(5,1,0),V(0,0,1),-90);shape.translate(V(-5,-1,0));shape.check(True)
    return shape


def stage01(m):
    m.colors.update({'ps2black':(.14,.15,.17),'ps2word':(.22,.24,.26),'ps2blue':(.20,.49,.79),'ps2cyan':(.25,.65,.76)})
    m.params.set('A3','Depth (Y)');m.params.set('A4','Height (Z)')
    # The complete envelope is official; the asymmetric step is photo estimated.
    m.native('LowerHousing','Asymmetric stepped lower enclosure',261,171,1.0,31.5,(-14,0,1.4),'Body',-5,'ps2black')
    m.cut('LowerHousing',m.rr(257.8,167.8,31.2,(-14,0,3.0),.6),'Open lower enclosure cavity').Refine=False
    m.native('UpperHousing','Original wide upper enclosure',301,182,.8,44.7,(0,0,33.3),'Body',5,'ps2black',expr={'Width':'Parameters.Width','Height':'Parameters.Height'})
    m.cut('UpperHousing',m.rr(297.8,178.8,43.5,(0,0,32.9),.4),'Open upper enclosure with 1.6 mm top skin').Refine=False
    grooves=[]
    for i in range(7):
        z=35.6+i*6.2
        grooves.append(Part.makeBox(301.4,.8,1.25,V(-150.7,-91.2,z)))
        for x in [-150.7,149.9]:grooves.append(Part.makeBox(.8,181.6,1.25,V(x,-90.4,z)))
    m.cut('UpperHousing',grooves,'Seven horizontal moulded-groove levels across the front and sides').Refine=False
    for i,(x,y) in enumerate([(-135,-72),(106,-72),(-135,72),(106,72)]):
        m.box('Foot'+str(i),'Rectangular rubber case pad',8,11,1.4,(x,y,0),'Body',-5,'rubber',.5)
    for key,points,color in [('P',[(-45,-12),(-45,4),(-15,4),(-15,14),(-45,14)],'ps2blue'),('S',[(-12,-12),(6,-12),(6,14),(22,14)],'ps2cyan'),('2',[(25,14),(55,14),(55,4),(25,4),(25,-12),(55,-12)],'ps2blue')]:
        m.feature('TopPS2'+key,'Geometric PS2 '+key+' mark study',_line_mark(points,1.05,78.025),'Body',6,color)
    word=m.label('TopWordmark','PlayStation 2',4.4,(0,0,0),'Body',6,'ps2word')
    width=word.Shape.BoundBox.XLength;word.Placement=App.Placement(V(-20,width/2,78.025),App.Rotation(V(0,0,1),-90));word.FlatPlacement=word.Placement
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=1
    m.checkpoint(1,'original_stepped_enclosure_and_horizontal_ribs','根据 SCPH-10000 官方包络建立原生上下空心壳、非对称底部阶梯、七层横向沟槽、四个脚垫与几何化顶面标识；局部壳体分割、壁厚和条纹为照片指导的学习近似。')


STAGES={1:stage01}


def stage02(m):
    from .ps1 import _add_shape
    from .atari2600 import _helical_spring
    front=g.rotation((0,-1,0),(0,0,1))
    m.profile['envelope_groups']=list(dict.fromkeys(m.profile['envelope_groups']+['FrontIO']))
    m.native('FrontPortPCB','Original shared controller and memory-card board',124,21,.8,1.3,(-77,-63.5,40.5),'FrontIO',0,'pcb')
    pcb_bores=[]
    for n,x in [(1,-104),(2,-50)]:
        key='Port'+str(n)
        m.cut('UpperHousing',[m.rr(49,9.3,4,(x,-88.9,63.5),.8,front),m.rr(43.4,9,4,(x,-88.9,48.8),1.5,front)],'Original card and controller apertures '+str(n)).Refine=False
        outer=m.rr(48,27,16.65,(x,-72.5,56),1.3,front)
        inner=m.rr(45.5,24.5,16,(x,-74,56),.6,front)
        m.feature(key+'Case','Original dual-level connector housing',outer.cut(inner),'FrontIO',1,'ps2black',True)
        door=m.rr(44,7.5,.8,(x,-90.9,63.5),.4,front)
        ears=[Part.makeCylinder(.7,1.6,V(x+dx,-90.4,67.15),V(1,0,0)) for dx in [-21.6,19.9]]
        door=door.multiFuse(ears).cut(Part.makeCylinder(.43,46,V(x-23,-90.4,67.15),V(1,0,0)))
        door=door.cut(Part.makeBox(2.8,3,2.3,V(x-20,-92,66.15)))
        m.feature(key+'Shutter','Memory-card shutter with integral hinge ears',door,'FrontIO',4,'ps2black')
        supports=[]
        for dx in [-23.7,22.5]:
            ring=Part.makeCylinder(.8,1.2,V(x+dx,-90.4,67.15),V(1,0,0))
            tab=Part.makeBox(1.2,1.7,1.6,V(x+dx,-90.6,66.35))
            supports.append(ring.fuse(tab).cut(Part.makeCylinder(.48,1.6,V(x+dx-.2,-90.4,67.15),V(1,0,0))))
        _add_shape(m,key+'Case',Part.makeCompound(supports),'Integral shutter-pivot carriers').Refine=False
        m.cyl(key+'ShutterPin','Memory-card shutter steel pivot',.34,47.6,(x-23.8,-90.4,67.15),'FrontIO',3,'metal',axis=(1,0,0),internal=True)
        spring=_helical_spring(.60,.40,1.8,.10)
        spring.Placement=App.Placement(V(x-19.6,-90.4,67.15),App.Rotation(V(0,0,1),V(1,0,0)))
        m.feature(key+'ShutterSpring','Shutter return spring study',spring,'FrontIO',3,'metal',True)
        m.box(key+'CardTongue','Eight-contact memory-card support tongue',40,10,.8,(x,-84,60.8),'FrontIO',2,'black',.3,True)
        wall_bores=[]
        for i in range(8):
            xx=x+(i-3.5)*4.5
            finger=Part.makeBox(1.2,10.7,.22,V(xx-.6,-89.2,61.65))
            run=Part.makeBox(.4,14.4,.22,V(xx-.2,-79,61.65))
            leg=Part.makeBox(.4,.4,20.24,V(xx-.2,-64.8,41.6))
            contact=finger.fuse(run).fuse(leg).removeSplitter()
            m.feature(key+'CardContact'+str(i),'Card contact with rear route and PCB leg',contact,'FrontIO',1,'gold',True)
            wall_bores.append(m.rr(.9,.8,2.1,(xx,-72.3,61.76),.1,front))
            pcb_bores.append(Part.makeCylinder(.45,1.8,V(xx,-64.6,40.3)))
        for block in range(3):
            bx=x+(block-1)*13
            bores=[Part.makeCylinder(.70,5.4,V(bx+(i-1)*3.6,-86.5,48.8),V(0,-1,0)) for i in range(3)]
            insert=m.rr(12.4,5.4,4.8,(bx,-86.8,48.8),1.25,front)
            m.feature(key+'Triplet'+str(block),'Three-position controller socket insulator',insert.cut(Part.makeCompound(bores)),'FrontIO',2,'black')
            for i in range(3):
                xx=bx+(i-1)*3.6;idx=block*3+i
                sleeve=Part.makeCylinder(.62,5.1,V(xx,-86.2,48.8),V(0,-1,0)).cut(Part.makeCylinder(.41,5.5,V(xx,-86.0,48.8),V(0,-1,0)))
                run=Part.makeBox(.44,19.7,.44,V(xx+.28,-86.4,48.58))
                leg=Part.makeBox(.44,.44,7.4,V(xx+.28,-66.9,41.6))
                m.feature(key+'ControllerContact'+str(idx),'Controller socket contact and PCB leg',sleeve.fuse(run).fuse(leg).removeSplitter(),'FrontIO',1,'gold',True)
                wall_bores.append(m.rr(1.3,1.1,2.1,(xx+.50,-72.3,48.8),.1,front))
                pcb_bores.append(Part.makeCylinder(.56,1.8,V(xx+.50,-66.68,40.3)))
        m.cut(key+'Case',wall_bores,'Card and controller terminal passages').Refine=False
        m.label(key+'MemoryLegend','MEMORY CARD',1.8,(x-11.6,-91.025,70.2),'Body',5,'white',rotation=front)
        m.label(key+'Number',str(n),2.5,(x-1,-91.025,55.9),'Body',5,'white',rotation=front)
    m.cut('FrontPortPCB',pcb_bores,'Thirty-four plated terminal clearances').Refine=False
    m.doc.recompute()
    m.profile['stages']=2
    m.checkpoint(2,'original_dual_memory_card_and_controller_interfaces','建立两组原版记忆卡与手柄接口、共享 PCB、带轴耳的独立防尘门和回位弹簧，以及八接点卡槽和九位置手柄插座；金属端子带独立穿板脚，并保留原生外壳开口。')


STAGES[2]=stage02


def stage03(m):
    front=g.rotation((0,-1,0),(0,0,1))
    m.colors['io_blue']=(.06,.35,.78)
    panel=m.rr(48,27.5,.08,(-119,-85.53,18.5),.6,front)
    cuts=[m.rr(15.1,7.5,4,(-128,-83.2,z),.6,front) for z in [13.2,24.2]]
    cuts.append(m.rr(8.3,6.3,4,(-106,-83.2,13.2),.6,front))
    m.feature('BlueIOPanel','Original blue USB and i.LINK field',panel.cut(Part.makeCompound(cuts)),'FrontIO',1,'io_blue')
    m.cut('LowerHousing',cuts,'Original two USB and four-pin i.LINK apertures').Refine=False
    for n,z in enumerate([13.2,24.2]):
        key='USB'+str(n);x=-128
        shell=m.rr(14.3,6.7,11,(x,-75,z),.45,front).cut(m.rr(13.5,5.9,11.4,(x,-74.8,z),.2,front))
        m.feature(key+'Shield','USB Type-A metal receptacle shell',shell,'FrontIO',0,'metal')
        carrier=m.rr(13.2,5.6,1,(x,-75.3,z),.15,front)
        tongue=m.rr(12.4,1.4,8.9,(x,-76.1,z-1.25),.12,front)
        holes=[]
        for i in range(4):
            xx=x+(i-1.5)*2.5;end_y=-72.3+n*2.8
            finger=Part.makeBox(.7,6.8,.18,V(xx-.35,-83.8,z-.42))
            run=Part.makeBox(.4,end_y+77.3,.18,V(xx-.2,-77.1,z-.42))
            leg=Part.makeBox(.4,.4,z-7.34,V(xx-.2,end_y,7.1))
            m.feature(key+'Contact'+str(i),'USB contact and plated-through-board leg',finger.fuse(run).fuse(leg).removeSplitter(),'FrontIO',0,'gold',True)
            holes.append(m.rr(.8,.7,1.8,(xx,-75.1,z-.33),.07,front))
        m.feature(key+'Tongue','USB carrier and insulating tongue',carrier.fuse(tongue).cut(Part.makeCompound(holes)),'FrontIO',0,'black',True)
    # The four signal contacts occupy one row below the insulating tongue.
    x,z=-106,13.2
    shield=m.rr(7.6,5.6,11,(x,-75,z),.45,front).cut(m.rr(6.8,4.8,11.4,(x,-74.8,z),.25,front))
    m.feature('ILinkShield','Four-pin i.LINK receptacle shield',shield,'FrontIO',0,'metal')
    carrier=m.rr(6.4,4.4,1,(x,-75.3,z),.2,front)
    tongue=m.rr(4.4,1.2,8.9,(x,-76.1,14.1),.1,front)
    key=m.rr(1.8,.8,8.9,(x,-76.1,11.35),.2,front)
    holes=[]
    for i in range(4):
        xx=x+(i-1.5)*.8
        finger=Part.makeBox(.28,6.8,.15,V(xx-.14,-83.8,13.26))
        run=Part.makeBox(.25,7.4,.15,V(xx-.125,-77.1,13.26))
        leg=Part.makeBox(.25,.30,6.30,V(xx-.125,-69.9,7.1))
        m.feature('ILinkContact'+str(i),'i.LINK signal contact and PCB leg',finger.fuse(run).fuse(leg).removeSplitter(),'FrontIO',0,'gold',True)
        holes.append(m.rr(.5,.5,1.8,(xx,-75.1,13.335),.05,front))
    m.feature('ILinkCarrier','Keyed i.LINK insulator with four-contact tongue',carrier.multiFuse([tongue,key]).cut(Part.makeCompound(holes)),'FrontIO',0,'black',True)
    m.label('USBLabel','USB',1.8,(-131.5,-85.635,29.8),'FrontIO',2,'white',rotation=front)
    m.label('ILinkLabel','i.LINK',1.65,(-111,-85.635,27.8),'FrontIO',2,'white',rotation=front)
    m.label('S400Label','S400',2.0,(-110,-85.635,20.5),'FrontIO',2,'white',rotation=front)
    vents=[m.rr(13,2.0,4,(x,-83.0,z),.25,front) for x in [-73+15.2*i for i in range(12)] for z in [12+3.2*j for j in range(6)]]
    m.cut('LowerHousing',vents,'Original lower-front horizontal intake grille').Refine=False
    m.profile['stages']=3
    m.checkpoint(3,'blue_usb_ilink_panel_and_lower_intake_grille','补齐初代蓝色双 USB / 四接点 i.LINK 面板、金属外套、绝缘舌片与穿板脚，并在下壳加工真正贯通的分段进风栅格；局部接口尺寸为学习近似。')


STAGES[3]=stage03


def _front_badge(m):
    from .psp import _polygon
    scale=.43
    def poly(points):return _polygon([(x*scale,(y+22)*scale) for x,y in points],0,.018)
    def ellipse(rx,ry):return Part.Face(Part.Wire(Part.Ellipse(V(0,-3*scale,0),rx*scale,ry*scale).toShape())).extrude(V(0,0,.018))
    red=poly([(-1.4,-27.1),(-1.4,-15),(3.1,-16.2),(5.6,-17.8),(5.8,-21.5),(4,-22.7),(1,-21.8),(1,-27.8)])
    red=red.cut(poly([(1,-18),(3.3,-18.6),(3.3,-20.7),(1,-20)]))
    ring=ellipse(9,3).cut(ellipse(5.58,1.86))
    yellow=ring.common(Part.makeBox(5,8,.1,V(-5,-4,-.02))).cut(red)
    green=ring.common(Part.makeBox(5,8,.1,V(0,-4,-.02))).cut(red)
    brown=ellipse(5.5,1.4).cut(red)
    front=g.rotation((0,-1,0),(0,0,1))
    for key,shape,mat in [('Red',red,'red'),('Yellow',yellow,'yellow'),('Green',green,'emblemgreen'),('Brown',brown,'emblembrown')]:
        shape.Placement=App.Placement(V(-14.5,-92.225,58),front)
        m.feature('FrontBadge'+key,'Swivel PS emblem colour study',shape,'Controls',6,mat)


def stage04(m):
    from .ps1 import _add_shape
    from .psp import _polygon
    front=g.rotation((0,-1,0),(0,0,1))
    m.colors.update({'yellow':(.90,.73,.12),'emblemgreen':(.10,.52,.30),'emblembrown':(.34,.24,.12)})
    m.profile['envelope_groups']=list(dict.fromkeys(m.profile['envelope_groups']+['Optical','Controls']))
    m.cut('UpperHousing',m.rr(131,13,5.5,(61.5,-88.8,58),.9,front),'Original tray-front opening').Refine=False
    m.native('DiscTray','Native optical-disc loading tray',128,144,1.6,2.5,(61.5,-17,54.5),'Optical',3,'ps2black')
    m.cut('DiscTray',[Part.makeCylinder(60.2,1.5,V(61.5,-18,55.8)),Part.makeCylinder(17,3.1,V(61.5,-18,54.2))],'Twelve-centimetre media recess and spindle opening').Refine=False
    _add_shape(m,'DiscTray',Part.makeCompound([Part.makeBox(6,2.4,3,V(x-3,-91.2,55)) for x in [24,99]]),'Tray front-cover attachment tabs').Refine=False
    m.box('TrayBezel','Separate ribbed optical-tray front cover',130,12,1.7,(61.5,-91.2,58),'Optical',4,'ps2black',.65,orient=front)
    m.cut('TrayBezel',[Part.makeBox(131,.7,1,V(-4,-93.1,z)) for z in [54.2,60.4]],'Tray moulding lines aligned with the enclosure').Refine=False
    m.label('TrayFamilyLabel','PlayStation 2',1.9,(72,-92.925,56.5),'Optical',5,'ps2word',rotation=front)
    m.box('ControlPCB','Original narrow power and eject board',15,35,1,(139,-77,57.5),'Controls',1,'pcb',.4,True,orient=front)
    for key,z,mat,caption in [('Power',69.5,'led','RESET'),('Eject',44.5,'blue','OPEN')]:
        m.cut('UpperHousing',m.rr(16,9.5,5,(139,-88.5,z),1,front),key+' button opening').Refine=False
        cap=m.rr(14,7.5,2.2,(139,-90,z),.65,front)
        stem=m.rr(4,3.5,10.2,(138,-80,z),.3,front)
        cap=cap.fuse(stem).cut(Part.makeCylinder(.95,4,V(143.4,-89.3,z),V(0,-1,0)))
        m.feature(key+'Button',caption+' button with internal operating stem',cap,'Controls',5,'ps2black')
        m.cyl(key+'Lens',key+' status light-guide study',.8,2.7,(143.4,-89.8,z),'Controls',5,mat,axis=(0,-1,0))
        if key=='Power':m.label(key+'Caption','RESET',1.3,(134,-92.225,z-.5),'Controls',6,'white',rotation=front)
        else:
            triangle=_polygon([(-1.8,-1.3),(1.8,-1.3),(0,1.6)],0,.018).cut(_polygon([(-1.18,-.98),(1.18,-.98),(0,.93)],-.01,.05))
            triangle.Placement=App.Placement(V(137.7,-92.225,z),front);m.feature('EjectSymbol','Outlined eject triangle',triangle,'Controls',6,'ps2blue')
        switch=m.rr(6,6,1.4,(138,-78.05,z),.3,front).fuse(Part.makeCylinder(1.2,.45,V(138,-79.4,z),V(0,-1,0)))
        m.feature(key+'Switch','Tactile switch and actuator study',switch,'Controls',2,'metal',True)
        pads=[m.rr(.7,1.1,.025,(138+sx,-78.025,z+sz),.08,front) for sx in [-3.5,3.5] for sz in [-1.8,1.8]]
        m.feature(key+'SwitchPads','Four tactile-switch PCB lands',Part.makeCompound(pads),'Controls',1,'gold',True)
    rotor=Part.makeCylinder(4.5,.75,V(-14.5,-91.45,58),V(0,-1,0)).fuse(Part.makeCylinder(.8,4.5,V(-14.5,-87,58),V(0,-1,0)))
    m.feature('EmblemRotor','Rotatable front emblem disc and axle study',rotor,'Controls',5,'ps2black')
    m.cut('UpperHousing',Part.makeCylinder(1.05,4,V(-14.5,-88.2,58),V(0,-1,0)),'Front emblem axle clearance').Refine=False
    _front_badge(m)
    m.profile['stages']=4
    m.checkpoint(4,'disc_tray_power_eject_board_and_swivel_emblem','建立原生盘托、独立前盖、出仓与复位键及传动柱、原始小控制板和指示灯，并加入带轴的前侧四色标识；机构只表示装配关系，不模拟运动。')


STAGES[4]=stage04


def stage05(m):
    rear=g.rotation((0,1,0),(0,0,1))
    m.profile['envelope_groups']=list(dict.fromkeys(m.profile['envelope_groups']+['Ports','Power']))
    x,z=-118,44.4
    inlet=m.rr(25.2,14,11.1,(x,80.8,z),1.8,rear)
    cavities=[Part.makeCylinder(4.2,10.4,V(x+dx,82,z),V(0,1,0)) for dx in [-4,4]]
    bores=[Part.makeCylinder(1.05,2.2,V(x+dx,80.3,z),V(0,1,0)) for dx in [-4,4]]
    m.feature('ACInlet','Original nonpolarized figure-eight AC inlet',inlet.cut(Part.makeCompound(cavities+bores)),'Power',1,'black')
    for i,dx in enumerate([-4,4]):
        pin=Part.makeCylinder(.9,9.5,V(x+dx,80.5,z),V(0,1,0)).fuse(Part.makeSphere(.9,V(x+dx,90,z)))
        m.feature('ACPin'+str(i),'Rounded AC inlet pin',pin,'Power',1,'metal',True)
    m.cut('UpperHousing',m.rr(26,14.8,4,(x,88.5,z),2.1,rear),'AC inlet rear opening').Refine=False
    frame=m.rr(23.5,13,13,(x,79,64),1.1,rear).cut(m.rr(20.5,10,11.2,(x,81.2,64),.7,rear))
    term_holes=[m.rr(2.7,1,2.9,(x+dx,78.7,64),.1,rear) for dx in [-4,4]]
    m.feature('MainsSwitchHousing','Rear mains-rocker support frame',frame.cut(Part.makeCompound(term_holes)),'Power',1,'black')
    m.cut('UpperHousing',m.rr(24.3,13.8,4,(x,88.5,64),1.2,rear),'Mains-rocker rear opening').Refine=False
    rocker=m.rr(19.8,9,4,(x,87.9,64),.6,rear)
    turn=App.Placement(V(),App.Rotation(V(1,0,0),8),V(x,89.9,64));rocker.Placement=turn.multiply(rocker.Placement)
    m.feature('MainsRocker','Original tilted mains rocker',rocker,'Power',4,'ps2black')
    for i,(text,zz) in enumerate([('I',65.2),('O',61.0)]):
        obj=m.label('MainsSymbol'+str(i),text,2,(x+.6,91.925,zz),'Power',5,'white',rotation=rear);obj.Placement=turn.multiply(obj.Placement);obj.FlatPlacement=obj.Placement
    for i,dx in enumerate([-4,4]):m.box('MainsTerminal'+str(i),'Mains switch terminal study',2.3,.6,4.2,(x+dx,75.0,64),'Power',0,'metal',.08,True,orient=rear)
    x,z=-116,19.2
    shell=m.rr(18.8,8,11,(x,75.3,z),.6,rear).cut(m.rr(17.8,7,11.4,(x,75.1,z),.3,rear))
    m.feature('AVMultiShell','Twelve-position AV MULTI output shell',shell,'Ports',1,'metal')
    m.box('AVMultiTongue','AV MULTI insulating tongue',16.2,1.35,8.8,(x,76.5,18.6),'Ports',1,'black',.2,True,orient=rear)
    for i in range(12):m.box('AVMultiContact'+str(i),'AV MULTI signal contact '+str(i+1),.5,.16,7.4,(x+(i-5.5)*1.2,78,19.5),'Ports',1,'gold',.03,True,orient=rear)
    m.cut('LowerHousing',m.rr(19.5,8.7,4.5,(x,82.8,z),.8,rear),'AV MULTI lower-rear opening').Refine=False
    x,z=-88,19.2
    housing=m.rr(8.8,9.4,11,(x,75.2,z),.5,rear).cut(m.rr(5.8,6.6,7,(x,79.6,z),.5,rear))
    pin_bores=[Part.makeCylinder(.4,1.8,V(x+dx,76.6,14.2)) for dx in [-2,0,2]]
    m.feature('OpticalOutputHousing','Square optical digital-output module',housing.cut(Part.makeCompound(pin_bores)),'Ports',1,'black')
    m.box('OpticalOutputDoor','Optical-output dust shutter',5.5,5.5,.3,(x,85.8,z),'Ports',2,'ps2black',.3,orient=rear)
    m.cyl('OpticalOutputLens','Optical-emitter window study',1,.3,(x,80.5,z),'Ports',1,'red',axis=(0,1,0),internal=True)
    for i,dx in enumerate([-2,0,2]):m.cyl('OpticalOutputPin'+str(i),'Optical-module board pin',.25,8.2,(x+dx,76.6,7.1),'Ports',0,'metal',internal=True)
    m.cut('LowerHousing',m.rr(9.6,10.2,4.5,(x,82.8,z),.6,rear),'Optical digital-output opening').Refine=False
    vents=[m.rr(16.4,2.7,9.2,(x,83.0,z),.3,rear) for x in [-71,-51,-31] for z in [20+4.4*i for i in range(12)]]
    for key in ['UpperHousing','LowerHousing']:m.cut(key,vents,'Rear fan grille across the stepped enclosure').Refine=False
    for key,text,size,x,y,z in [('RearAC','AC IN',1.6,-118,91.025,34.7),('RearMains','MAIN POWER',1.4,-118,91.025,73.8),('RearAV','AV MULTI OUT',1.6,-116,85.525,10.8),('RearOptical','DIGITAL OUT',1.25,-88,85.525,10.8)]:
        m.label(key,text,size,(x+len(text)*size*.28,y,z),'Body',5,'ps2word',rotation=rear)
    m.profile['stages']=5
    m.checkpoint(5,'original_rear_av_optical_mains_and_fan_grille','加入原版十二位置 AV MULTI、光纤数字输出、非极性 AC 输入和后部主电源翘板，并加工跨越阶梯外壳的风扇栅格；保留独立外套、绝缘载体与信号接点。')


STAGES[5]=stage05


def stage06(m):
    rear=g.rotation((0,1,0),(0,0,1));x=67
    outer=m.rr(55.8,83,13.6,(x,41.5,12.2),.6)
    inner=m.rr(54.6,84,12.4,(x,41.5,12.8),.3)
    feet=[m.rr(5,10,.6,(xx,yy,11.8),.5) for xx in [38,96] for yy in [7,74]]
    cage=outer.cut(inner).multiFuse(feet)
    holes=[Part.makeCylinder(1.3,1.3,V(xx,yy,11.6)) for xx in [38,96] for yy in [7,74]]
    holes.append(Part.makeCylinder(1.1,1.5,V(95.5,3.2,11.5)))
    m.feature('PCCardCage','Type III PC CARD metal guide cage and mounting feet',cage.cut(Part.makeCompound(holes)),'Ports',0,'metal',True)
    block=m.rr(52,8.8,7.6,(x,-3.2,19),.6,rear);bores=[]
    for row,z in enumerate([18.1,19.9]):
        end_y=-6.0-row*2.4
        for i in range(34):
            xx=x+(i-16.5)*1.27;index=row*34+i
            pin=m.rr(.36,.24,11.2,(xx,-2.9,z),.03,rear)
            run=Part.makeBox(.36,-2.7-end_y,.24,V(xx-.18,end_y,z-.12))
            leg=Part.makeBox(.36,.36,z-7.0,V(xx-.18,end_y,7.1))
            m.feature('PCCardContact'+str(index),'PC CARD contact '+str(index+1)+' and board leg',pin.fuse(run).fuse(leg).removeSplitter(),'Ports',0,'gold',True)
            bores.append(m.rr(.68,.56,8.1,(xx,-3.4,z),.09,rear))
    m.feature('PCCardHeader','Two-row 68-position PC CARD insulating header',block.cut(Part.makeCompound(bores)),'Ports',0,'black',True)
    protector=m.rr(54.2,10.4,1.5,(x,84.8,20),.6,rear)
    arms=[Part.makeBox(1,76,2,V(x+dx-.5,9,18.6)) for dx in [-25,25]]
    protector=protector.multiFuse(arms).removeSplitter()
    m.feature('PCCardProtector','Original PC CARD protector with internal guide arms',protector,'Ports',3,'ps2black')
    m.cut('LowerHousing',m.rr(58,13,5,(x,82.8,20),.9,rear),'Original Type III PC CARD rear mouth').Refine=False
    guide=m.rr(4,5,74,(101,6,20),.5,rear).cut(Part.makeCylinder(1.5,74.4,V(101,5.8,20),V(0,1,0)))
    m.feature('PCCardEjectGuide','PC CARD eject-rod guide',guide,'Ports',0,'ps2black',True)
    rod=Part.makeCylinder(1.25,78.7,V(101,5.2,20),V(0,1,0))
    head=Part.makeCylinder(1.8,.8,V(101,5.0,20),V(0,1,0))
    drop=Part.makeBox(1.2,2.4,8.5,V(100.4,3.0,11.5))
    m.feature('PCCardEjectRod','PC CARD push rod and driving finger',rod.multiFuse([head,drop]).removeSplitter(),'Ports',0,'metal',True)
    m.box('PCCardEjectButton','Original PC CARD eject button',4.5,7,3,(101,84,20),'Ports',3,'ps2black',.6,orient=rear)
    m.cut('LowerHousing',m.rr(5.4,8,5,(101,82.8,20),.7,rear),'PC CARD eject-button opening').Refine=False
    cam=m.rr(32,4,.6,(86,3.2,10.7),.7).cut(Part.makeCylinder(1.1,1,V(95.5,3.2,10.5)))
    m.feature('PCCardEjectLever','Under-cage eject lever study',cam,'Ports',-1,'metal',True)
    m.cyl('PCCardEjectPivot','Eject-lever pivot pin',.8,3,(95.5,3.2,9.4),'Ports',-1,'metal',internal=True)
    m.label('PCCardLabel','PC CARD',1.8,(70.5,85.525,8.8),'Body',5,'ps2word',rotation=rear)
    m.profile['stages']=6
    m.checkpoint(6,'type_iii_pc_card_cage_contacts_and_eject_mechanism','加入初代 PC CARD Type III 金属导向笼、两排 68 接点、原版保护盖与导向臂，以及弹出按钮、推杆和下部杠杆；此处保留 PC CARD 架构，局部几何为学习近似。')


STAGES[6]=stage06


def _spaced_text_shape(m,text,size):
    """Explicit glyph spacing avoids touching A/M outlines in small legends."""
    font=m.root/'references/DejaVuSans.ttf';shapes=[];cursor=0
    for char in text:
        if char==' ':cursor+=size*.55;continue
        wires=Part.makeWireString(char,str(font.parent)+'/',font.name,size)
        faces=[face for glyph in wires if glyph for face in Part.makeFace(glyph,'Part::FaceMakerBullseye').Faces]
        shape=Part.makeCompound([face.extrude(V(0,0,.018)) for face in faces]);bounds=shape.BoundBox
        shape.translate(V(cursor-bounds.XMin,0,0));shapes.append(shape);cursor+=bounds.XLength+size*.16
    result=Part.makeCompound(shapes);result.check(True);return result


def _bga_package(m,key,caption,x,y,w,h,grid,void,metal_lid=True):
    m.box(key+'Substrate',caption+' package substrate',w,h,.95,(x,y,9.45),'Mainboard',1,'packagegreen',.45,True)
    m.box(key+'Body',caption+' moulded package',w-1.2,h-1.2,2.30,(x,y,10.45),'Mainboard',1,'black',.5,True)
    if metal_lid:m.box(key+'Lid',caption+' metal heat spreader',w-2.2,h-2.2,.70,(x,y,12.80),'Mainboard',2,'metal',.4,True)
    count,pitch=grid;balls=[];pads=[];low=(count-void)//2
    for i in range(count):
        for j in range(count):
            if low<=i<low+void and low<=j<low+void:continue
            xx=x+(i-(count-1)/2)*pitch;yy=y+(j-(count-1)/2)*pitch
            balls.append(Part.makeSphere(.28,V(xx,yy,9.13)))
            pads.append(Part.makeCylinder(.31,.025,V(xx,yy,8.825)))
    m.feature(key+'Balls',caption+' schematic BGA ball array',Part.makeCompound(balls),'Mainboard',0,'metal',True)
    m.feature(key+'Pads',caption+' schematic board land array',Part.makeCompound(pads),'Mainboard',0,'gold',True)
    m.label(key+'Mark',caption,min(2.4,(w-4)/(len(caption)*.65)),(x-w/2+2,y-1.2,13.525 if metal_lid else 12.775),'Mainboard',2,'ps2word' if metal_lid else 'white')


def stage07(m):
    from .psp import _polygon
    m.colors.update({'packagegreen':(.12,.24,.18),'boardtan':(.43,.47,.25)})
    m.profile['envelope_groups']=list(dict.fromkeys(m.profile['envelope_groups']+['Mainboard']))
    m.native('Mainboard','GH-001 original-family main circuit board',248,157,1.2,1.6,(-10,0,7.2),'Mainboard',0,'boardtan')
    notch=_polygon([(-18,79.5),(-14,74.3),(10,74.3),(14,79.5)],7,2)
    holes=[notch]
    mounts=[(-129,73),(110,-72),(-120,-58),(-85.5,37.8),(-36,55.3),(-36,-.8),(-75.5,-31.6),(-10,-72),(34,73)]
    holes += [Part.makeCylinder(1.6,2,V(x,y,7)) for x,y in mounts]
    holes += [Part.makeCylinder(1.3,2,V(x,y,7)) for x in [38,96] for y in [7,74]]
    # Keep every existing terminal on its own drilled entry into the main PCB.
    for n in range(2):
        for i in range(4):holes.append(Part.makeCylinder(.46,2,V(-128+(i-1.5)*2.5,-72.1+n*2.8,7)))
    for i in range(4):holes.append(Part.makeCylinder(.36,2,V(-106+(i-1.5)*.8,-69.75,7)))
    for row in range(2):
        for i in range(34):holes.append(Part.makeCylinder(.42,2,V(67+(i-16.5)*1.27,-6-row*2.4+.18,7)))
    for dx in [-2,0,2]:holes.append(Part.makeCylinder(.40,2,V(-88+dx,76.6,7)))
    for i in range(12):
        xx=-116+(i-5.5)*1.2;obj=m.parts['AVMultiContact'+str(i)]
        run=Part.makeBox(.4,4.7,.16,V(xx-.2,73.5,19.42))
        leg=Part.makeBox(.4,.35,12.48,V(xx-.2,73.5,7.1))
        obj.Shape=obj.Shape.fuse(run).fuse(leg).removeSplitter();obj.FlatPlacement=obj.Placement
        holes.append(Part.makeCylinder(.44,2,V(xx,73.675,7)))
    m.cut('Mainboard',holes,'GH-001 edge notch, mounting and connector-terminal holes').Refine=False
    for i,(x,y) in enumerate(mounts):m.ring('MainGround'+str(i),'Mainboard mounting ground land',2.65,1.7,.025,(x,y,8.825),'Mainboard',0,'copper',internal=True)
    _bga_package(m,'EE','EE / CXD9542GB',-66.5,-6.5,45,42.5,(24,1.45),6)
    _bga_package(m,'GS','GS / CXD2934GB',-61,42,40.5,40,(22,1.3),10)
    for i,y in enumerate([8,-19]):
        x=-108;key='RDRAM'+str(i)
        m.box(key,'RDRAM package study',17,13,1.1,(x,y,9.45),'Mainboard',1,'black',.35,True)
        m.box(key+'Spread','RDRAM heat-spreader study',13.5,10,.45,(x,y,10.6),'Mainboard',2,'metal',.25,True)
        balls=[Part.makeSphere(.22,V(x+(a-3.5)*1.45,y+(b-3.5)*1.1,9.12)) for a in range(8) for b in range(8)]
        pads=[Part.makeCylinder(.25,.025,V(x+(a-3.5)*1.45,y+(b-3.5)*1.1,8.825)) for a in range(8) for b in range(8)]
        m.feature(key+'Balls','Schematic RDRAM ball array',Part.makeCompound(balls),'Mainboard',0,'metal',True)
        m.feature(key+'Pads','Schematic RDRAM landing array',Part.makeCompound(pads),'Mainboard',0,'gold',True)
        mark=_spaced_text_shape(m,'RDRAM',1.2);mark.translate(V(x-3,y-.4,11.075))
        m.feature(key+'Mark','RDRAM',mark,'Mainboard',2,'ps2word')
    m.label('MainboardMark','GH-001 / SCPH-10000 STUDY',2.1,(-51,-67,8.85),'Mainboard',0,'copper')
    m.profile['stages']=7
    m.checkpoint(7,'gh001_native_mainboard_ee_gs_and_rdram','建立 GH-001 原生主板、安装地环与已有接口穿板孔，加入 EE、GS 金属顶盖封装及两片 RDRAM；BGA 数量和排布仅描述结构学习模型，不构成引脚网络。')


STAGES[7]=stage07


def _board_ic(m,key,caption,x,y,w,h,pins,qfp=False,angle=0,underside=False):
    """Reuse formed-lead construction at this board's 8.8 mm top datum."""
    from .ps1 import _ic_package
    before=set(m.parts)
    m.colors.setdefault('psdark',(.12,.13,.15))
    _ic_package(m,key,caption,caption,x,y,w,h,pins,height=1.8,qfp=qfp,angle=angle)
    if h<=6:
        dot=Part.makeCylinder(.25,.015,V(x-w/2+.6,y+h/2-.6,12.225))
        if angle:dot.rotate(V(x,y,9.2),V(0,0,1),angle)
        obj=m.parts[key+'PinOne'];obj.Shape=dot;obj.FlatPlacement=obj.Placement
    if 'RAM' in caption:
        obj=m.parts[key+'Mark'];placement=obj.Placement
        obj.Shape=_spaced_text_shape(m,caption,min(1.3,(w-2)/(len(caption)*.85)));obj.Placement=placement;obj.FlatPlacement=placement
    for name in set(m.parts)-before:
        obj=m.parts[name];obj.Placement.Base.z-=1.2;obj.FlatPlacement=obj.Placement
        if underside:
            turn=App.Placement(V(),App.Rotation(V(1,0,0),180),V(x,y,8.0))
            obj.Placement=turn.multiply(obj.Placement);obj.FlatPlacement=obj.Placement


def _board_cap(m,key,x,y,r=3.1,h=4.2,mark=''):
    from .ps1 import _smd_cap
    before=set(m.parts);_smd_cap(m,key,x,y,r,h,mark)
    for name in set(m.parts)-before:
        obj=m.parts[name];obj.Placement.Base.z-=1.2;obj.FlatPlacement=obj.Placement


def _board_passive(m,key,x,y,material='thermal'):
    from .ps1 import _passive
    before=set(m.parts);_passive(m,key,x,y,material)
    for name in set(m.parts)-before:
        obj=m.parts[name];obj.Placement.Base.z-=1.2;obj.FlatPlacement=obj.Placement


def stage08(m):
    # Positions follow the photographed GH-001 component face. Small package
    # lead arrays represent construction, not an electrical pin map or BOM.
    _bga_package(m,'IOP','IOP',-73,-52,26,26,(18,1.1),6,metal_lid=False)
    for data in [
        ('IOPRAM','IOP RAM',-110,-46,28,10,40,False,0),
        ('SPU2','SPU2',55,-55,22,22,100,True,0),
        ('SPURAM','AUDIO RAM',55,-30,26,10,40,False,0),
        ('ROMStudy','ROM STUDY',87,-48,29,12,40,False,90),
        ('VideoEncoder','VIDEO',-123,50,10,10,48,True,0),
        ('VideoDAC','DAC',-99,39,8,8,32,True,0),
    ]:_board_ic(m,*data)
    m.colors.update({'inductorblue':(.09,.27,.42),'capviolet':(.43,.31,.61),'ceramic':(.66,.52,.33)})
    inductors=[(-12,31),(20,33),(6,50),(-17,-25),(21,-25),(-2,-15),(10,-15)]
    for i,(x,y) in enumerate(inductors):
        key='BuckInductor'+str(i);r=4.5 if i in [5,6] else 5.2
        m.box(key+'Base','Voltage-regulator inductor moulded base',2*r+1,2*r+1,.6,(x,y,8.98),'Mainboard',1,'black',.65,True)
        m.cyl(key+'Drum','Shielded regulator inductor study',r,5.0,(x,y,9.65),'Mainboard',1,'inductorblue',internal=True)
        m.cyl(key+'Top','Inductor ferrite top',r-.55,.2,(x,y,14.7),'Mainboard',1,'black',internal=True)
        m.label(key+'Mark','100',1.25,(x-1.6,y-.6,14.925),'Mainboard',2,'white')
        ends=[Part.makeBox(.7,2,.12,V(x+side*(r+.4)-.35,y-1,8.85)) for side in [-1,1]]
        m.feature(key+'Ends','Inductor solder terminals',Part.makeCompound(ends),'Mainboard',0,'metal',True)
    for i,(x,y) in enumerate([(-1,18),(11,18),(23,18),(-4,-28),(9,-28)]):
        key='BuckBulk'+str(i);_board_cap(m,key,x,y,3.8,4.8)
        m.colors.setdefault('capviolet',(.43,.31,.61))
        g.appearance(m.parts[key+'Top'],m.colors['capviolet']);m.parts[key+'Top'].MaterialDescription='capviolet'
    small=[(-17,9),(-8,7),(1,7),(10,7),(25,3),(-19,-6),(20,-9),(27,52),(20,63),(-19,52),(-19,-38),(30,-39)]
    small += [(-125,64),(-115,64),(-105,64),(-104,54),(-115,31),(-127,25),(-127,36)]
    for i,(x,y) in enumerate(small):_board_cap(m,'FilterCap'+str(i),x,y,2.5,3.5)
    for i,(x,y) in enumerate([(-2,37),(21,45),(-2,-38),(10,-38),(23,-38)]):
        _board_ic(m,'Regulator'+str(i),'REG',x,y,5.5,4.5,8)
    locations=[(x,y) for x in [-31,-25] for y in [-47,-40,-33,-25,-18,-10,3,12,21,31,41,50,62]]
    locations += [(x,y) for x in [-127,-122] for y in [-29,-19,-9,1,10,18]]
    locations += [(x,y) for x in [38,72,103] for y in [-66,-58,-50,-42,-18]]
    for i,(x,y) in enumerate(locations):_board_passive(m,'BoardDecoupling'+str(i),x,y,'black' if i%3==0 else 'ceramic')
    # Retained coin cell and separate contact tabs; no simulated electrical use.
    x,y=20,-61
    holder=Part.makeCylinder(11.2,1.0,V(x,y,8.95)).fuse(Part.makeCylinder(11.2,3.1,V(x,y,9.9)).cut(Part.makeCylinder(10.4,3.3,V(x,y,9.8))))
    holder=holder.cut(Part.makeBox(25,3.2,4,V(x-12.5,y-1.6,9.7)))
    holder=holder.cut(Part.makeCompound([Part.makeBox(1.5,2.6,1.3,V(x+side*11.4-.75,y-1.3,8.8)) for side in [-1,1]]))
    m.feature('RTCStock','Coin-cell holder with access for opposing contacts',holder,'Mainboard',1,'black',True)
    m.cyl('RTCCell','CR2032 clock battery study',10,3.2,(x,y,10.03),'Mainboard',2,'metal',internal=True)
    m.label('RTCMark','CR2032',1.7,(x-4.5,y-.7,13.255),'Mainboard',2,'ps2word')
    bores=[]
    for i,side in enumerate([-1,1]):
        xx=x+side*11.4
        tab=Part.makeBox(1.1,2.2,4.3,V(xx-.55,y-1.1,9.15))
        top=Part.makeBox(2.7,2.2,.18,V(x+side*10.0-1.35,y-1.1,13.27))
        leg=Part.makeBox(.5,.6,2.2,V(xx-.25,y-.3,7.0))
        m.feature('RTCContact'+str(i),'Clock battery retaining terminal',tab.fuse(top).fuse(leg).removeSplitter(),'Mainboard',1,'metal',True)
        bores.append(Part.makeCylinder(.5,2.1,V(xx,y,6.95)))
    x,y=-12,64
    housing=m.rr(22,10,8,(x,y,8.95),.7).cut(m.rr(20,8,6.1,(x,y,11),.4))
    for i in range(4):
        xx=x+(i-1.5)*5
        housing=housing.cut(Part.makeBox(1.5,1.5,8.4,V(xx-.75,y-.75,8.75)))
        pin=Part.makeBox(1.2,1.2,15.2,V(xx-.6,y-.6,7.0))
        m.feature('PSUBoardContact'+str(i),'Mainboard power-header blade study',pin,'Mainboard',2,'metal',True)
        bores.append(Part.makeCylinder(.95,2.1,V(xx,y,6.95)))
    m.feature('PSUBoardSocket','Four-position motherboard power header',housing,'Mainboard',1,'white',True)
    m.cut('Mainboard',bores,'RTC terminal and four power-header board passages').Refine=False
    m.profile['stages']=8
    m.checkpoint(8,'gh001_iop_audio_regulators_and_clock_battery','补齐 GH-001 可见面的 IOP、音频和存储封装，中央调节器、电感和滤波电容，CR2032 电池座及四位电源连接器；小封装和元件排布为照片指导的结构示意，不提供电气网络。')


STAGES[8]=stage08


def _board_fpc(m,key,x,y,pins,width,underside=False,side=-1):
    before=set(m.parts)
    housing=m.rr(width+3,4.8,2.4,(x,y,8.98),.35)
    mouth=m.rr(width+1,3.0,.65,(x,y+side*1.5,10.1),.1)
    m.feature(key,'Flat-circuit connector housing study',housing.cut(mouth),'Mainboard',0,'white',True)
    m.box(key+'Latch','Separate flat-circuit connector lock',width+1,1,.45,(x,y+side*3.0,10.82),'Mainboard',0,'black',.12,True)
    contacts=[];pads=[]
    for i in range(pins):
        xx=x+(i-(pins-1)/2)*(width-.8)/(pins-1)
        contacts.append(Part.makeBox(.22,2.6,.09,V(xx-.11,y-1.3,10.17)))
        pads.append(Part.makeBox(.28,.75,.025,V(xx-.14,y-side*2.85-.375,8.835)))
    # Separate contact slots retain positive clearance from the insulating body.
    slots=[Part.makeBox(.38,2.8,.26,V(x+(i-(pins-1)/2)*(width-.8)/(pins-1)-.19,y-1.4,10.08)) for i in range(pins)]
    m.cut(key,slots,'Individual flat-circuit contact slots').Refine=False
    m.feature(key+'Contacts','Flat-circuit connector contact comb',Part.makeCompound(contacts),'Mainboard',0,'gold',True)
    m.feature(key+'Pads','Flat-circuit connector board lands',Part.makeCompound(pads),'Mainboard',0,'gold',True)
    if underside:
        turn=App.Placement(V(),App.Rotation(V(1,0,0),180),V(x,y,8.0))
        for name in set(m.parts)-before:
            obj=m.parts[name];obj.Placement=turn.multiply(obj.Placement);obj.FlatPlacement=obj.Placement


def stage09(m):
    # Opposite-face locations follow Dig and Rescue photo004. Its package
    # identities cannot all be read, so labels deliberately remain descriptive.
    for data in [
        ('UnderLogicA','LOGIC A',70,60,28,16,64,False,0),
        ('UnderLogicB','LOGIC B',53,30,13,13,64,True,0),
        ('UnderLogicC','LOGIC C',8,27,14,12,48,True,0),
        ('UnderLogicD','LOGIC D',-4,3,11,11,48,True,0),
        ('UnderLogicE','LOGIC E',-108,54,13,13,64,True,0),
        ('UnderLogicF','LOGIC F',-72,-55,25,23,100,True,0),
        ('UnderBuffer','BUFFER STUDY',24,61,18,7,28,False,0),
    ]:_board_ic(m,*data,underside=True)
    m.colors['thermalpink']=(.73,.54,.59)
    for i,(x,y,w,h) in enumerate([(70,60,26,14),(8,27,12,10),(-72,-55,23,21)]):
        m.box('UnderThermal'+str(i),'Underside package thermal pad study',w,h,.55,(x,y,4.35),'Mainboard',-1,'thermalpink',.3,True)
    _board_fpc(m,'UnderRearFlex',22,72,24,14,underside=True,side=-1)
    _board_fpc(m,'UnderFrontFlex',-18,-66,30,18,underside=True,side=1)
    _board_fpc(m,'TopDriveFlex',35,-5,20,12,side=-1)
    _board_fpc(m,'TopControlFlex',-48,-72,18,11,side=1)
    _board_fpc(m,'TopOpticalFlex',-10,-52,24,14,side=-1)
    points=[(x,y) for x in [33,37] for y in [-48,-37,-25,-12,0,12,24,39,49]]
    points += [(x,y) for x in [-43,-49] for y in [-34,-23,-12,0,12,25,38,49]]
    for i,(x,y) in enumerate(points):
        before=set(m.parts);_board_passive(m,'UnderPassive'+str(i),x,y,'black' if i%3==0 else 'ceramic')
        turn=App.Placement(V(),App.Rotation(V(1,0,0),180),V(x,y,8.0))
        for name in set(m.parts)-before:
            obj=m.parts[name];obj.Placement=turn.multiply(obj.Placement);obj.FlatPlacement=obj.Placement
    # Three-position fan header, as visible in the close-up source photo006.
    x,y=-28,70
    block=m.rr(5.3,4.8,4.2,(x,y,9.0),.35).cut(m.rr(3.9,3.4,3.4,(x,y,10),.2))
    bores=[]
    for i,dx in enumerate([-1.15,0,1.15]):
        block=block.cut(Part.makeCylinder(.42,4.6,V(x+dx,y,8.8)))
        m.cyl('FanHeaderPin'+str(i),'Fan supply connector terminal study',.28,6.6,(x+dx,y,7.0),'Mainboard',1,'metal',internal=True)
        bores.append(Part.makeCylinder(.42,2.1,V(x+dx,y,6.95)))
    m.feature('FanHeader','Three-position fan-power header',block,'Mainboard',1,'white',True)
    m.cut('Mainboard',bores,'Three fan-connector terminal passages').Refine=False
    m.box('TimingCan','Low-profile timing oscillator can study',7,3.8,1.3,(-43,-46,8.98),'Mainboard',1,'metal',1.0,True)
    m.profile['stages']=9
    m.checkpoint(9,'opposite_board_face_thermal_pads_and_flex_connectors','依据背面照片加入七组逻辑封装、三处导热垫与背面阻容，补充上下表面排线插座、风扇电源座和时钟罐体；无法从照片确认的背面芯片仅使用位置描述标识。')


STAGES[9]=stage09


def stage10(m):
    from .ps1 import _add_shape
    m.profile['envelope_groups']=list(dict.fromkeys(m.profile['envelope_groups']+['Shielding']))
    m.native('LowerShield','Native lower EMI enclosure sheet',244,153,1.4,.45,(-10,0,3.65),'Shielding',-3,'metal')
    fingers=[]
    for x in range(-126,109,13):
        for y in [-76.55,76.2]:fingers.append(Part.makeBox(4,.35,2.45,V(x-2,y,3.95)))
    for y in range(-64,65,13):
        for x in [-132.05,111.7]:fingers.append(Part.makeBox(.35,4,2.45,V(x,y-2,3.95)))
    _add_shape(m,'LowerShield',Part.makeCompound(fingers),'Turned-up peripheral shield contact fingers').Refine=False
    mounts=[(-128,71),(-127,-68),(108,71),(108,-68)]
    cuts=[Part.makeCylinder(1.1,1.1,V(x,y,3.4)) for x,y in mounts]
    cuts += [m.rr(22,8,1.1,(-18,-66,3.4),.5),m.rr(18,8,1.1,(22,72,3.4),.5)]
    m.cut('LowerShield',cuts,'Four shield fixing holes and underside flex access windows').Refine=False
    for i,(x,y,w,h) in enumerate([(70,60,26,14),(8,27,12,10),(-72,-55,23,21)]):
        _add_shape(m,'LowerShield',m.rr(w-2,h-2,.3,(x,y,4.0),.4),'Shallow thermal contact emboss '+str(i)).Refine=False
    for i,(x,y) in enumerate(mounts):
        m.ring('ShieldSupport'+str(i),'Lower-shell shield support boss',2.2,.8,.6,(x,y,3.0),'Shielding',-4,'ps2black',internal=True)
        m.screw('ShieldScrew'+str(i),(x,y,4.6),'Shielding',-2,length=2.5,radius=2.0,axis=(0,0,-1))
    m.cut('LowerHousing',[Part.makeCylinder(.8,1.7,V(x,y,1.65)) for x,y in mounts],'Blind bores for the four lower shield fasteners').Refine=False
    m.profile['stages']=10
    m.checkpoint(10,'native_lower_shield_fingers_and_four_fixings','建立原生下部屏蔽板、周边折起接触指、排线检修开口及三处浅压凸接触区，加入四组支座与盲孔螺钉；板料和折边尺寸为装配学习近似。')


STAGES[10]=stage10


BOARD_MOUNTS=[(-129,73),(110,-72),(-120,-58),(-85.5,37.8),(-36,55.3),(-36,-.8),(-75.5,-31.6),(-10,-72),(34,73)]


def stage11(m):
    from .ps1 import _add_shape
    m.profile['envelope_groups']=list(dict.fromkeys(m.profile['envelope_groups']+['Frame']))
    m.native('MiddleFrame','Native original-family middle frame',292,172,1.4,2.2,(0,0,33.8),'Frame',2,'ps2black')
    openings=[m.rr(127,156,2.7,(-75,0,33.55),1.0),m.rr(135,156,2.7,(65,0,33.55),1.0)]
    m.cut('MiddleFrame',openings,'Separate power and optical carrier bays').Refine=False
    # Cross ties and nine pillars belong to the frame, with clear screw bores.
    ties=[]
    for i,(x,y) in enumerate(BOARD_MOUNTS):
        r=2.7 if i<3 else 2.35
        post=Part.makeCylinder(r,25,V(x,y,8.9)).cut(Part.makeCylinder(1.15,25.3,V(x,y,8.75)))
        ties.append(post)
        edge=-142 if x<0 else 140
        ties.append(Part.makeBox(abs(edge-x)+1.4,3.2,1.7,V(min(x,edge)-.7,y-1.6,34.1)))
    _add_shape(m,'MiddleFrame',Part.makeCompound(ties),'Nine board pillars and radial frame ties').Refine=False
    # The rear axial fan, front connector block and original power connector
    # retain explicit frame openings; no solid plate covers the cooling path.
    cuts=[Part.makeBox(61,20,24,V(-81.5,67,20)),m.rr(25,15,4,(-12,64,33.5),1)]
    cuts += [Part.makeCylinder(1.15,27,V(x,y,8.7)) for x,y in BOARD_MOUNTS]
    cuts.append(Part.makeBox(5.4,10.4,1,V(35.3,68.8,11.6)))
    cuts.append(Part.makeCylinder(2.4,5.1,V(38,74,8.65)))
    m.cut('MiddleFrame',cuts,'Rear fan relief, power-header route and pillar pilot holes').Refine=False
    for i,(x,y) in enumerate(BOARD_MOUNTS):
        m.screw('MainboardScrew'+str(i),(x,y,6.8),'Frame',0,length=6.2,radius=2.5 if i<3 else 2.05)
    for i,(x,y) in enumerate([(38,7),(96,7),(38,74),(96,74)]):
        m.ring('PCCageSpacer'+str(i),'PC CARD cage mounting spacer',2.15,1.1,2.8,(x,y,8.9),'Frame',0,'metal',internal=True)
        if i==1:m.cut('PCCageSpacer1',Part.makeBox(6,2,3.2,V(93,3.35,8.7)),'Flat side beside the eject lever').Refine=False
        m.screw('PCCageScrew'+str(i),(x,y,12.95),'Frame',1,length=5.7,radius=2.15,axis=(0,0,-1))
    m.cut('PCCardCage',[Part.makeCylinder(2.35,.8,V(x,y,12.5)) for x,y in [(38,7),(96,7),(38,74),(96,74)]],'Cage wall relief beside mounting screw heads').Refine=False
    m.profile['stages']=11
    m.checkpoint(11,'native_middle_frame_board_pillars_and_card_fixings','建立原生中框及电源与光驱分区，补充九个主板安装柱、由底面固定的螺钉和 PC CARD 笼支撑件；局部支柱和筋条按当前装配关系构建。')


STAGES[11]=stage11


def stage12(m):
    from .ps1 import _add_shape
    from .atari2600 import _rounded_route
    m.profile['envelope_groups']=list(dict.fromkeys(m.profile['envelope_groups']+['Cooling']))
    for key,x,y,w,h in [('EE',-66.5,-6.5,39,36.5),('GS',-61,42,34.5,34)]:
        m.box(key+'Thermal','Processor-to-spreader thermal interface',w,h,1.75,(x,y,13.56),'Cooling',1,'thermalpink',.45,True)
    for i,y in enumerate([8,-19]):
        m.box('RDRAMThermal'+str(i),'Memory-to-spreader thermal interface',12,9,4.2,(-108,y,11.1),'Cooling',1,'thermalpink',.35,True)
    m.native('HeatSpreader','Native processor heat-spreader plate',96,143,1.1,.65,(-81,0,15.4),'Cooling',2,'metal')
    openings=[Part.makeCylinder(3.2,1.2,V(x,y,15.15)) for x,y in BOARD_MOUNTS]
    openings += [Part.makeCylinder(.6,1.2,V(-128+(i-1.5)*2.5,-69.3,15.15)) for i in range(4)]
    m.cut('HeatSpreader',openings,'Mainboard pillar clearance through thermal spreader').Refine=False
    # Paired curved heat pipes follow the original folded-plate arrangement;
    # their local route and section are an assembly study, not thermal sizing.
    for i,x in enumerate([-99,-93]):
        path=([V(x,56,18.5),V(x,-28,18.5),V(x+22,-43,18.5),V(-37,-43,18.5)] if i==0 else
              [V(x,56,18.5),V(x,-14,18.5),V(-68,-29,18.5),V(-37,-37,18.5)])
        pipe=_rounded_route(path,7,1.65)
        m.feature('HeatPipe'+str(i),'Curved original-family heat-pipe study',pipe,'Cooling',2,'metal',True)
    m.native('FinBase','Native front heat-sink collector',111,21,1.0,2.2,(-81,-45.5,21.0),'Cooling',3,'metal')
    saddles=[Part.makeBox(5,4,3.0,V(x,y,18.1)) for x in [-65,-45] for y in [-45,-39]]
    pipe_relief=[m.parts['HeatPipe'+str(i)].Shape for i in range(2)]
    saddle=Part.makeCompound(saddles).cut(Part.makeCompound(pipe_relief))
    _add_shape(m,'FinBase',saddle,'Collector saddle blocks around heat pipes').Refine=False
    # Fins stand above the collector, immediately behind the front port board.
    fins=[Part.makeBox(.7,20,12.5,V(-134+i*3.15,-55.5,23.15)) for i in range(35)]
    _add_shape(m,'FinBase',Part.makeCompound(fins),'Thirty-five upright heat-sink fins').Refine=False
    m.cut('FinBase',[Part.makeCylinder(1.1,3.5,V(x,-57.2,24),V(0,1,0)) for x in [-107,-44]],'Two heat-sink fixing pilot holes').Refine=False
    m.cut('FinBase',[Part.makeCylinder(3.0,18.5,V(x,y,17.5)) for x,y in BOARD_MOUNTS],'Heat-sink pillar clearance').Refine=False
    for i,x in enumerate([-107,-44]):
        bracket=Part.makeBox(8,.7,9.9,V(x-4,-56.8,16.1))
        bracket=bracket.cut(Part.makeCylinder(1.1,1.2,V(x,-57,24),V(0,1,0)))
        m.feature('SinkBracket'+str(i),'Heat-sink shield attachment tab',bracket,'Cooling',3,'metal',True)
        washer=Part.makeCylinder(2.35,.3,V(x,-57.2,24),V(0,-1,0)).cut(Part.makeCylinder(1.15,.5,V(x,-57.1,24),V(0,-1,0)))
        m.feature('SinkWasher'+str(i),'Heat-sink attachment washer',washer,'Cooling',3,'metal',True)
        screw=Part.makeCylinder(1.85,.6,V(x,-58.1,24),V(0,1,0)).fuse(Part.makeCylinder(.85,2.2,V(x,-57.6,24),V(0,1,0)))
        slot=Part.makeBox(.38,.4,2.7,V(x-.19,-58.2,22.65))
        m.feature('SinkScrew'+str(i),'Heat-sink shield fixing study',screw.cut(slot),'Cooling',3,'metal',True)
    m.profile['stages']=12
    m.checkpoint(12,'processor_spreader_paired_heat_pipes_and_fins','加入 EE、GS 和内存导热界面、原生金属均热板、成对弯曲热管、前侧鳍片组及两组带垫圈的固定结构；热管及鳍片尺寸为结构学习近似。')


STAGES[12]=stage12


def stage13(m):
    import math
    from .ps1 import _add_shape
    rear=g.rotation((0,1,0),(0,0,1));x,y,z=-51,69.2,44
    outer=m.rr(58,58,14.4,(x,y,z),2.8,rear)
    bore=Part.makeCylinder(27.2,14.8,V(x,y-.2,z),V(0,1,0))
    bores=[Part.makeCylinder(1.35,15,V(x+dx,y-.3,z+dz),V(0,1,0)) for dx in [-24.7,24.7] for dz in [-24.7,24.7]]
    m.feature('RearFanFrame','Original-family rear axial fan casing',outer.cut(bore).cut(Part.makeCompound(bores)),'Cooling',3,'black',True)
    hub=Part.makeCylinder(10,8,V(x,72.4,z),V(0,1,0));blades=[]
    for i in range(7):
        a=2*math.pi*i/7
        points=[V(x+r*math.cos(a+t),76,z+r*math.sin(a+t)) for r,t in [(9.5,-.28),(26.35,-.12),(26.35,.24),(9.5,.33)]]
        blades.append(Part.Face(Part.makePolygon(points+[points[0]])).extrude(V(0,1.1,0)))
    m.feature('RearFanRotor','Seven-blade rear fan rotor study',hub.multiFuse(blades).removeSplitter(),'Cooling',3,'black',True)
    pcb=Part.makeCylinder(9.1,.65,V(x,70.3,z),V(0,1,0)).cut(Part.makeCylinder(1.1,1,V(x,70.1,z),V(0,1,0)))
    m.feature('RearFanPCB','Fan motor support circuit board',pcb,'Cooling',3,'pcb',True)
    arms=[]
    for i in range(4):
        arm=Part.makeBox(19,.7,1.8,V(x+8.5,71.15,z-.9));arm.rotate(V(x,71.15,z),V(0,1,0),90*i);arms.append(arm)
    _add_shape(m,'RearFanFrame',Part.makeCompound(arms),'Four radial motor support struts').Refine=False
    m.cyl('FanAxle','Fan rotor axle study',.8,6.8,(x,69.5,z),'Cooling',3,'metal',axis=(0,1,0),internal=True)
    # Keep the axle inside a genuine bore in the rotor.
    m.cut('RearFanRotor',Part.makeCylinder(1.0,8.5,V(x,72.2,z),V(0,1,0)),'Rotor axle clearance').Refine=False
    m.cut('HeatSpreader',Part.makeBox(61,5,1.4,V(-81.5,68.8,15.1)),'Rear-fan lower frame clearance').Refine=False
    m.cut('HeatSpreader',Part.makeBox(7.4,3.0,1.4,V(-79.4,66.5,15.1)),'Lower fan mounting ear clearance').Refine=False
    for i,(dx,dz) in enumerate([(-24.7,-24.7),(24.7,24.7)]):
        xx,zz=x+dx,z+dz
        foot=m.rr(7,7,2.3,(xx,66.7,zz),1.0,rear).cut(Part.makeCylinder(1.1,2.8,V(xx,66.4,zz),V(0,1,0)))
        m.feature('FanMount'+str(i),'Rear fan supporting mounting ear',foot,'Frame',3,'ps2black',True)
        shaft=Part.makeCylinder(.9,16.4,V(xx,66.6,zz),V(0,1,0))
        head=Part.makeCylinder(2.2,.65,V(xx,66.0,zz),V(0,1,0))
        m.feature('FanFixing'+str(i),'Rear fan through-fixing study',shaft.fuse(head),'Cooling',3,'metal',True)
    m.profile['stages']=13
    m.checkpoint(13,'rear_axial_fan_rotor_motor_support_and_mounts','建立后排七叶轴流风扇、带安装孔的框体、独立转子与轴孔、电机支板和四根支撑臂，并加入两处固定耳及穿孔螺钉。')


STAGES[13]=stage13


def _psu_cap(m,key,x,y,r,h,holes,blue=False):
    m.cyl(key+'Seal','Radial capacitor lower seal',r-.4,.7,(x,y,40.8),'Power',3,'black',internal=True)
    m.cut(key+'Seal',[Part.makeCylinder(.43,1,V(x+dx,y,40.65)) for dx in [-r*.35,r*.35]],'Capacitor lead insulation passages').Refine=False
    m.cyl(key,'Radial electrolytic capacitor study',r,h,(x,y,41.6),'Power',3,'psublue' if blue else 'metal',internal=True)
    cap=Part.makeCylinder(r-.5,.15,V(x,y,41.78+h))
    cap=cap.cut(Part.makeBox(.3,1.5*r,.09,V(x-.15,y-.75*r,41.87+h)))
    m.feature(key+'Top','Scored capacitor top seal',cap,'Power',4,'metal',True)
    for i,dx in enumerate([-r*.35,r*.35]):
        m.cyl(key+'Leg'+str(i),'Capacitor board lead',.28,2.65,(x+dx,y,38.8),'Power',2,'metal',internal=True)
        holes.append(Part.makeCylinder(.43,2.1,V(x+dx,y,38.75)))


def stage14(m):
    from .ps1 import _add_shape
    m.colors.update({'psutan':(.57,.39,.19),'psublue':(.08,.35,.58),'transformercream':(.85,.80,.59)})
    m.native('PowerPCB','Native original-family internal power-supply board',110,100,1.2,1.6,(-74,9,39),'Power',3,'psutan')
    _add_shape(m,'PowerPCB',m.rr(23,14,1.6,(-11.5,62,39),.5),'Rear corner tab for motherboard power coupling').Refine=False
    mounts=[(-125,55),(-125,-37),(-23,55),(-23,-37)]
    holes=[Part.makeCylinder(1.5,2.1,V(x,y,38.75)) for x,y in mounts]
    for i,y in enumerate([-18,31]):_psu_cap(m,'PrimaryBulk'+str(i),-101,y,10,20,holes,True)
    for i,y in enumerate([-28,-10,8,26,44]):_psu_cap(m,'SecondaryFilter'+str(i),-26,y,4.7,16,holes)
    for i,y in enumerate([-13,23]):
        x=-120;key='LineChoke'+str(i)
        m.box(key+'Base','Input choke insulating carrier',14,19,1.2,(x,y,40.8),'Power',3,'black',.6,True)
        core=m.rr(13,17,12,(x,y,42.1),1.2).cut(m.rr(8,11,12.4,(x,y,41.9),.8))
        m.feature(key+'Core','Input choke ferrite frame',core,'Power',3,'black',True)
        for row,xx in enumerate([x-4.8,x+4.8]):
            loops=[]
            for turn in range(6):
                zz=42.8+turn*1.6
                loop=m.rr(5.8,12,.65,(xx,y,zz),1.8).cut(m.rr(4.4,10.6,1.1,(xx,y,zz-.2),1.1))
                # Coil clears the ferrite with a study insulation gap.
                loops.append(loop.cut(core))
            m.feature(key+'Winding'+str(row),'Input-filter copper winding study',Part.makeCompound(loops),'Power',3,'copper',True)
        for k,(dx,dy) in enumerate([(-4,-7),(4,-7),(-4,7),(4,7)]):
            m.cyl(key+'Leg'+str(k),'Choke board terminal',.4,2.1,(x+dx,y+dy,38.8),'Power',2,'metal',internal=True)
            holes.append(Part.makeCylinder(.55,2.1,V(x+dx,y+dy,38.75)))
        m.cut(key+'Base',[Part.makeCylinder(.55,1.6,V(x+dx,y+dy,40.6)) for dx,dy in [(-4,-7),(4,-7),(-4,7),(4,7)]],'Choke terminal passages').Refine=False
    x,y=-60,-17
    m.box('TransformerBobbin','Switching transformer bobbin',26,30,2,(x,y,40.9),'Power',3,'black',1.2,True)
    outer=m.rr(24,27,20,(x,y,43),1.1);inner=m.rr(15,19,20.4,(x,y,42.8),.7)
    m.feature('TransformerCore','Power transformer ferrite core',outer.cut(inner),'Power',3,'black',True)
    m.box('TransformerWrap','Insulated transformer winding pack',14,18,18,(x,y,44),'Power',3,'transformercream',1.4,True)
    mark=_spaced_text_shape(m,'TRANSFORMER',1.1);mark.translate(V(x-6.1,y-1,62.025))
    m.feature('TransformerMark','TRANSFORMER',mark,'Power',4,'black')
    for row,dy in enumerate([-13,13]):
        for i in range(5):
            xx=x+(i-2)*4.2
            m.cyl('TransformerPin'+str(row*5+i),'Transformer pin study',.4,3.0,(xx,y+dy,38.8),'Power',2,'metal',internal=True)
            holes.append(Part.makeCylinder(.55,2.1,V(xx,y+dy,38.75)))
    m.cut('TransformerBobbin',[Part.makeCylinder(.55,2.4,V(x+(i-2)*4.2,y+dy,40.7)) for dy in [-13,13] for i in range(5)],'Transformer terminal insulation passages').Refine=False
    for i,x in enumerate([-82,-38]):
        plate=Part.makeBox(1.0,91,26,V(x-.5,-38,41.0))
        foot=Part.makeBox(7,91,.7,V(x-3.5,-38,40.8))
        m.feature('PSUHeatSink'+str(i),'Power transistor vertical heat-sink plate',plate.fuse(foot),'Power',4,'metal',True)
    # Original corner coupling is represented as four individual long sockets.
    x,y=-12,64
    housing=m.rr(22,10,20.8,(x,y,18.05),.7);bores=[]
    for i in range(4):
        xx=x+(i-1.5)*5
        housing=housing.cut(Part.makeBox(2.4,2.4,21.2,V(xx-1.2,y-1.2,17.9)))
        sleeve=Part.makeBox(1.9,1.9,21.7,V(xx-.95,y-.95,18.95)).cut(Part.makeBox(1.35,1.35,22.1,V(xx-.675,y-.675,18.75)))
        m.feature('PowerCouplingContact'+str(i),'Four-way motherboard coupling socket',sleeve,'Power',2,'metal',True)
        holes.append(Part.makeCylinder(1.45,2.1,V(xx,y,38.75)))
    m.feature('PowerCouplingHousing','Motherboard power-coupling insulating housing',housing,'Power',2,'white',True)
    m.cut('PowerPCB',holes,'Power board mounting and individually drilled terminal holes').Refine=False
    support_tabs=[]
    for i,(x,y) in enumerate(mounts):
        anchor=-143 if x<-100 else -8
        tab=Part.makeBox(abs(anchor-x)+6,6,1.2,V(min(x,anchor)-3,y-3,35.85))
        support_tabs.append(tab.cut(Part.makeCylinder(1.0,1.6,V(x,y,35.65))))
        m.ring('PSUSpacer'+str(i),'Power-board insulating standoff',2.5,1.0,1.75,(x,y,37.1),'Frame',3,'ps2black',internal=True)
        m.screw('PSUScrew'+str(i),(x,y,41.1),'Power',4,length=5.0,radius=2.4,axis=(0,0,-1))
    _add_shape(m,'MiddleFrame',Part.makeCompound(support_tabs),'Four raised power-board mounting shelves').Refine=False
    m.cut('MiddleFrame',[Part.makeCylinder(1.0,3.4,V(x,y,33.9)) for x,y in mounts],'Power-board fixing pilot holes through existing ties').Refine=False
    m.profile['stages']=14
    m.checkpoint(14,'native_power_board_chokes_transformer_and_filter_caps','建立原版布局指导的独立电源板、两组输入扼流圈、双大电容、变压器、两片竖直散热板及五个输出滤波电容，并加入四位主板耦合接点和安装件。')


STAGES[14]=stage14


def stage15(m):
    from .ps1 import _power_control_ic
    m.colors['fuseglass']=(.55,.67,.70);holes=[]
    for i,(x,y) in enumerate([(-62,23),(-61,40)]):
        before=set(m.parts);local=[];_power_control_ic(m,'PowerControl'+str(i),x,y,8,local)
        for name in set(m.parts)-before:
            obj=m.parts[name];obj.Placement.Base.z+=27.2;obj.FlatPlacement=obj.Placement
        for shape in local:shape.translate(V(0,0,27.2));holes.append(shape)
    for i,(x,y) in enumerate([(-70,9),(-53,9),(-70,52)]):_psu_cap(m,'PowerSmallCap'+str(i),x,y,2.5,6,holes)
    x,y,z=-105,52,45
    m.ring('PowerFuseGlass','Input fuse glass barrel',1.8,1.5,15.6,(x,y,z),'Power',3,'fuseglass',axis=(1,0,0),internal=True)
    m.cyl('PowerFuseWire','Fuse element study',.07,15.8,(x-.1,y,z),'Power',3,'metal',axis=(1,0,0),internal=True)
    for i,xx in enumerate([x-2.2,x+15.8]):
        m.cyl('PowerFuseCap'+str(i),'Fuse metal end cap',1.85,2,(xx,y,z),'Power',3,'metal',axis=(1,0,0),internal=True)
        xx+=1
        cradle=Part.makeCylinder(2.25,.65,V(xx-.325,y,z),V(1,0,0)).cut(Part.makeCylinder(1.9,.9,V(xx-.45,y,z),V(1,0,0)))
        cradle=cradle.common(Part.makeBox(1,5,3.3,V(xx-.5,y-2.5,z-3.4)))
        leg=Part.makeBox(.35,.45,4.0,V(xx-.175,y-.225,38.8))
        m.feature('PowerFuseClip'+str(i),'Fuse cradle and through-board terminal',cradle.fuse(leg),'Power',3,'metal',True)
        holes.append(Part.makeCylinder(.45,2.1,V(xx,y,38.75)))
    # Input socket and two primary heat-sink mounted devices.
    x,y=-117,52
    housing=m.rr(10,7,5.5,(x,y,40.8),.7).cut(m.rr(8,5,4.2,(x,y,42.3),.4))
    for i,dx in enumerate([-2.5,2.5]):
        housing=housing.cut(Part.makeCylinder(.55,5.9,V(x+dx,y,40.6)))
        m.cyl('PowerInputPin'+str(i),'Power input board pin',.4,7.5,(x+dx,y,38.8),'Power',3,'metal',internal=True)
        holes.append(Part.makeCylinder(.55,2.1,V(x+dx,y,38.75)))
    m.feature('PowerInputSocket','Two-position AC input connector',housing,'Power',3,'white',True)
    for i,(x,y,side) in enumerate([(-84.5,8,-1),(-35.5,9,1),(-35.5,34,1)]):
        case=m.rr(8,10,2,(x,y,46.6),.5,g.rotation((side,0,0),(0,0,1)))
        m.feature('PowerSwitchDevice'+str(i),'Heat-sink mounted power-device package',case,'Power',4,'black',True)
        for pin in range(3):
            yy=y+(pin-1)*2.3
            leg=Part.makeBox(.45,.45,2.7,V(x-.225,yy-.225,38.8))
            m.feature('PowerDeviceLead'+str(i)+'_'+str(pin),'Power device board terminal',leg,'Power',3,'metal',True)
            holes.append(Part.makeCylinder(.55,2.1,V(x,yy,38.75)))
        m.cut('PSUHeatSink'+str(0 if i==0 else 1),[Part.makeCylinder(.55,1.2,V(x,y+(pin-1)*2.3,40.6)) for pin in range(3)],'Power-device lead clearance through heat-sink foot').Refine=False
    for i,(x,y) in enumerate([(-73,1),(-68,34),(-54,34),(-52,52)]):
        m.cyl('PowerResistor'+str(i),'Axial resistor body study',1.0,5,(x-2.5,y,43.4),'Power',3,'transformercream',axis=(1,0,0),internal=True)
        for end,side in enumerate([-1,1]):
            xx=x+side*4.0
            lead=Part.makeCylinder(.2,1.35,V(x+side*2.6,y,43.4),V(side,0,0)).fuse(Part.makeCylinder(.2,4.6,V(xx,y,38.8)))
            m.feature('PowerResistorLead'+str(i)+'_'+str(end),'Formed resistor lead',lead,'Power',3,'metal',True)
            holes.append(Part.makeCylinder(.35,2.1,V(xx,y,38.75)))
    m.cut('PowerPCB',holes,'Fuse, control IC, input and power-device terminal holes').Refine=False
    m.label('PowerBoardMark','SCPH-10000 / PSU STUDY',1.5,(-78,56.3,40.625),'Power',3,'white')
    m.profile['stages']=15
    m.checkpoint(15,'power_input_fuse_control_and_switching_components','补齐独立电源板的玻璃保险丝与夹座、输入连接器、控制封装、小电容、散热板侧功率器件和轴向电阻；接点保持独立穿板孔，电路为非功能性结构示意。')


STAGES[15]=stage15


def stage16(m):
    from .ps1 import _add_shape
    front=g.rotation((0,-1,0),(0,0,1));x=61.5
    m.native('DriveHousing','Native original-family optical drive housing',136,164,1.3,29.8,(x,-1,37.4),'Optical',3,'ps2black')
    m.cut('DriveHousing',m.rr(132.8,160.8,29.1,(x,-1,38.9),.7),'Open optical mechanism cavity').Refine=False
    cuts=[m.rr(130,8,6,(x,-79,56.5),.5,front),Part.makeBox(13,21,5.8,V(-10.5,53.5,37.1))]
    m.cut('DriveHousing',cuts,'Tray mouth and original power-coupling corner relief').Refine=False
    # The early tray has a long keyhole rather than only a spindle bore.
    keyhole=Part.makeCylinder(22.5,3.5,V(x,-18,54.1)).fuse(Part.makeBox(45,66,3.5,V(x-22.5,-18,54.1)))
    m.cut('DiscTray',keyhole,'Original tray pickup and spindle access opening').Refine=False
    for i,xx in enumerate([-.2,123.2]):
        rail=Part.makeBox(2.8,137,2.1,V(xx-1.4,-79,51.9))
        m.feature('TrayGuideRail'+str(i),'Longitudinal tray support rail',rail,'Optical',3,'ps2black',True)
        shoe=m.rr(3.5,10,1.8,(xx,-45,54.3),.4)
        m.feature('TrayGuideShoe'+str(i),'Tray sliding guide shoe',shoe,'Optical',4,'white',True)
    m.cut('DiscTray',[m.rr(4,10.6,2.2,(xx,-45,54.1),.5) for xx in [-.2,123.2]],'Tray guide-shoe locating pockets').Refine=False
    # Four compliant supports isolate the stamped optical deck from the case.
    mounts=[(21,-35),(103,-35),(21,62),(103,62)]
    for i,(xx,yy) in enumerate(mounts):
        m.ring('DriveIsolator'+str(i),'Optical deck elastomer isolator',4.0,1.2,3.5,(xx,yy,39.05),'Optical',3,'rubber',internal=True)
        m.ring('DriveMountSleeve'+str(i),'Optical deck mounting sleeve',1.0,.65,4.2,(xx,yy,39.1),'Optical',3,'metal',internal=True)
    m.native('OpticalDeck','Native stamped pickup and spindle deck',91,108,1.2,1.2,(62,13.5,42.7),'Optical',4,'metal')
    openings=[m.rr(58,62,1.7,(61.5,25,42.45),.8),Part.makeCylinder(14,1.7,V(61.5,-18,42.45))]
    openings += [Part.makeCylinder(1.4,1.7,V(xx,yy,42.45)) for xx,yy in mounts]
    m.cut('OpticalDeck',openings,'Deck pickup well, spindle aperture and isolator fixing holes').Refine=False
    for i,(xx,yy) in enumerate(mounts):
        m.screw('DeckScrew'+str(i),(xx,yy,44.5),'Optical',4,length=4.6,radius=2.5,axis=(0,0,-1))
    # Two original case fixing ears and four cover fixings remain separate.
    ears=[]
    for xx,yy in [(-9.5,-59),(132.5,47)]:
        ear=m.rr(9,12,2.0,(xx,yy,37.5),.7).cut(Part.makeCylinder(1.3,2.5,V(xx,yy,37.25)));ears.append(ear)
    _add_shape(m,'DriveHousing',Part.makeCompound(ears),'Two optical drive mounting ears').Refine=False
    m.profile['stages']=16
    m.checkpoint(16,'native_optical_housing_keyhole_tray_and_isolated_deck','建立原生光驱外壳、初代长钥匙孔盘托、纵向托盘导轨与滑块、带窗口的金属光学底架及四组隔振安装件，并保留两处整机固定耳。')


STAGES[16]=stage16


def stage17(m):
    from .atari2600 import _helical_spring
    from .ps1 import _gear
    # Spindle axis is the same as the native tray recess; the pickup sits aft.
    x,y=61.5,-18
    pcb=Part.makeCylinder(16,.65,V(x,y,44.05)).cut(Part.makeCylinder(3.1,1,V(x,y,43.9)))
    m.feature('SpindlePCB','Original-family spindle motor circuit board',pcb,'Optical',4,'pcb',True)
    motor=Part.makeCylinder(12.8,5.6,V(x,y,44.85)).cut(Part.makeCylinder(1.15,6,V(x,y,44.65)))
    m.feature('SpindleMotor','Optical disc spindle motor can',motor,'Optical',4,'metal',True)
    m.cyl('SpindleShaft','Spindle motor shaft',.85,9.8,(x,y,46.1),'Optical',4,'metal',internal=True)
    hub=Part.makeCylinder(13,5.75,V(x,y,51.0)).fuse(Part.makeCone(8,6.8,1.4,V(x,y,56.7)))
    hub=hub.cut(Part.makeCylinder(1.05,7.8,V(x,y,50.8)))
    m.feature('DiscTurntable','Disc support turntable and centring cone',hub,'Optical',5,'black',True)
    m.ring('DiscGripRing','Disc support elastomer ring',12.5,8.3,.5,(x,y,56.8),'Optical',5,'rubber',internal=True)
    for i,xx in enumerate([33,91]):
        m.cyl('PickupGuide'+str(i),'Polished optical pickup guide rod',1.5,74,(xx,-12,48.5),'Optical',4,'metal',axis=(0,1,0),internal=True)
        for j,yy in enumerate([-12,62]):
            bracket=m.rr(8,8,7,(xx,yy,44.1),.7).cut(Part.makeCylinder(1.75,9,V(xx,yy-4.5,48.5),V(0,1,0)))
            bracket=bracket.cut(Part.makeCylinder(.95,7.5,V(xx+2.5,yy,43.9)))
            m.feature('GuideBracket'+str(i)+'_'+str(j),'Guide rod end bearing support',bracket,'Optical',4,'black',True)
    # A bridged carriage provides two bored guide sleeves and a central optic.
    carrier=m.rr(53,24,3,(62,20,49.2),1.1)
    sleeves=[]
    for xx in [33,91]:
        sleeves.append(Part.makeCylinder(2.6,21,V(xx,9.5,48.5),V(0,1,0)).cut(Part.makeCylinder(1.7,21.4,V(xx,9.3,48.5),V(0,1,0))))
    bridges=[Part.makeBox(9,5,2.3,V(xx,yy,49.3)) for xx in [32.5,83] for yy in [10,25]]
    carriage=carrier.multiFuse(sleeves+bridges)
    carriage=carriage.cut(Part.makeBox(17,15,3.6,V(53,12.5,49)))
    carriage=carriage.cut(Part.makeCompound([Part.makeCylinder(1.7,25,V(xx,7.5,48.5),V(0,1,0)) for xx in [33,91]]))
    carriage=carriage.cut(Part.makeCylinder(2.7,5.1,V(61.5,27.8,50),V(0,1,0)))
    m.feature('PickupCarriage','KHS-400A-family pickup carriage study',carriage,'Optical',5,'metal',True)
    m.box('PickupPCB','Optical pickup local circuit board',24,21,.55,(61.5,20,46.5),'Optical',4,'pcb',.7,True)
    optic=m.rr(15.8,13.8,4,(61.5,20,48.6),.9).cut(Part.makeCylinder(3.6,4.5,V(61.5,20,48.4)))
    m.feature('OpticalBlock','Pickup optical block and objective aperture',optic,'Optical',5,'black',True)
    lens=Part.makeSphere(4.6,V(61.5,20,52.1)).common(Part.makeCylinder(3.3,1.2,V(61.5,20,55.25)))
    m.feature('ObjectiveLens','Convex objective lens study',lens,'Optical',6,'blue',True)
    m.ring('ObjectiveHolder','Objective lens suspension ring',4.2,3.45,1.4,(61.5,20,53.8),'Optical',6,'black',internal=True)
    for i,dx in enumerate([-6.3,6.3]):
        m.box('FocusMagnet'+str(i),'Focus actuator magnet',2.1,8,2,(61.5+dx,20,52.8),'Optical',5,'black',.2,True)
        for j,dy in enumerate([-4.5,4.5]):
            m.cyl('FocusSuspension'+str(i)+'_'+str(j),'Objective suspension wire',.1,3.4,(61.5+dx,20+dy,53.5),'Optical',5,'metal',axis=(-1 if dx>0 else 1,0,0),internal=True)
    m.cyl('PickupLaserCan','Enclosed laser diode package study',2.5,4.5,(61.5,28,50.0),'Optical',5,'metal',axis=(0,1,0),internal=True)
    m.label('PickupMark','KHS-400A STUDY',1.1,(37.5,9,52.225),'Optical',5,'black')
    # Separate feed motor, threaded shaft and the carriage follower.
    m.cyl('FeedMotor','Pickup feed motor can',4.5,12,(103,65.5,48.5),'Optical',4,'metal',axis=(0,1,0),internal=True)
    m.cyl('FeedShaft','Pickup feed screw core',.65,69.5,(103,-4,48.5),'Optical',4,'metal',axis=(0,1,0),internal=True)
    helix=_helical_spring(.85,2.1,51,.15);helix.Placement=App.Placement(V(103,-2,48.5),App.Rotation(V(0,0,1),V(0,1,0)))
    m.feature('FeedThread','Helical pickup feed screw thread',helix,'Optical',4,'metal',True)
    follower=m.rr(9,6,3.5,(98.5,20,46.75),.6).cut(Part.makeCylinder(1.25,6.5,V(103,16.75,48.5),V(0,1,0)))
    m.feature('FeedFollower','Carriage feed-screw follower arm',follower,'Optical',5,'white',True)
    m.profile['stages']=17
    m.checkpoint(17,'spindle_motor_pickup_guides_optics_and_feed_screw','加入主轴电机与盘片定心台、两根光头导杆、带导套的光头滑架、镜片与悬挂件，以及独立进给电机、螺旋丝杆和随动臂；KHS-400A 封装内部为结构示意。')


STAGES[17]=stage17


def stage18(m):
    from .ps1 import _gear,_add_shape
    m.cyl('LoadMotor','Tray loading motor can',5.4,7.4,(20,-66,39.1),'Optical',3,'metal',internal=True)
    m.cyl('LoadMotorAxle','Tray loading motor shaft',.65,4.5,(20,-66,46.6),'Optical',4,'metal',internal=True)
    for i,x in enumerate([20,102]):
        pulley=Part.makeCylinder(2.55,.9,V(x,-66,49.7))
        pulley=pulley.multiFuse([Part.makeCylinder(3.4,.2,V(x,-66,49.45)),Part.makeCylinder(3.4,.2,V(x,-66,50.65))])
        # A short hub connects the flanges, leaving the belt channel recessed.
        pulley=pulley.fuse(Part.makeCylinder(1.6,1.4,V(x,-66,49.45))).cut(Part.makeCylinder(.9,1.8,V(x,-66,49.3)))
        m.feature('LoadPulley'+str(i),'Grooved tray-loading belt pulley',pulley,'Optical',4,'white',True)
    belt=m.rr(88.4,6.4,.8,(61,-66,49.75),3.19).cut(m.rr(87.4,5.4,1.2,(61,-66,49.55),2.69))
    m.feature('LoadBelt','Tray motor rubber drive belt',belt,'Optical',4,'rubber',True)
    for i,x in enumerate([102,115.7]):
        gear=_gear(m,x,-66,46.75,6.4,7.1,1.5,30)
        if i:gear.rotate(V(x,-66,0),V(0,0,1),6)
        hub=Part.makeCylinder(1.9,1.2,V(x,-66,48.15))
        gear=gear.fuse(hub).cut(Part.makeCylinder(1.0,4.3,V(x,-66,46.5)))
        m.feature('LoadGear'+str(i),'Tray loading reduction gear study',gear,'Optical',4,'white',True)
        m.cyl('LoadGearAxle'+str(i),'Loading gear pivot pin',.75,13.8,(x,-66,39.05),'Optical',3,'metal',internal=True)
    pinion=_gear(m,115.7,-66,50.85,2.8,3.5,1.3,14).cut(Part.makeCylinder(1.0,1.7,V(115.7,-66,50.65)))
    m.feature('TrayPinion','Tray rack drive pinion',pinion,'Optical',5,'white',True)
    backbone=Part.makeBox(1.2,117,3.7,V(119.8,-73,50.9))
    teeth=[Part.makeBox(1.2,.6,1.2,V(118.6,-72.7+i*1.6,50.9)) for i in range(73)]
    _add_shape(m,'DiscTray',backbone.multiFuse(teeth),'Original tray longitudinal underside rack').Refine=False
    # End-position microswitch with an independent spring lever.
    m.box('TrayEndSwitch','Tray end-position switch body',8,5,3,(12,-53,39.1),'Optical',3,'black',.5,True)
    lever=Part.makeBox(.35,12,.3,V(14.4,-58,42.25))
    m.feature('TrayEndLever','Tray position-sensing spring lever',lever,'Optical',4,'metal',True)
    for i,xx in enumerate([9.5,12,14.5]):m.cyl('TrayEndPin'+str(i),'Tray limit-switch solder terminal',.23,2.0,(xx,-55.7,39.3),'Optical',3,'metal',internal=True)
    m.cut('TrayEndSwitch',[Part.makeCylinder(.35,2.5,V(xx,-55.7,39.0)) for xx in [9.5,12,14.5]],'Limit-switch terminal passages').Refine=False
    m.profile['stages']=18
    m.checkpoint(18,'tray_loading_motor_belt_reduction_gears_and_rack','加入盘托装载电机、带槽皮带轮、橡胶传动带、减速齿轮与盘托下方纵向齿条，并补充行程检测开关和弹片；齿形为静态装配学习近似。')


STAGES[18]=stage18


def _move_optical_electronics(m,names,z_offset,flip_center=None):
    for key in names:
        obj=m.parts[key];m.group('Mainboard').removeObject(obj);m.group('Optical').addObject(obj);obj.Assembly='Optical';obj.ExplodeLayer=3
        obj.Placement.Base.z+=z_offset
        if flip_center:
            obj.Placement=App.Placement(V(),App.Rotation(V(1,0,0),180),V(*flip_center)).multiply(obj.Placement)
        obj.FlatPlacement=obj.Placement


def stage19(m):
    # Early A-chassis retains the separate GM-038 RF board. Package pin
    # geometry and board outline remain schematic, as with the main PCB.
    m.native('DriveRFPCB','Native GM-038-family optical RF board',52,38,.8,.8,(63,31,41.1),'Optical',3,'pcb')
    mounts=[(40,15),(86,15),(40,47),(86,47)]
    m.cut('DriveRFPCB',[Part.makeCylinder(1.1,1.3,V(x,y,40.85)) for x,y in mounts],'Optical RF board mounting holes').Refine=False
    before=set(m.parts);_board_ic(m,'DriveRFAmp','CXA2605R',63,30,9,9,48,qfp=True)
    _move_optical_electronics(m,set(m.parts)-before,33.1,(63,30,41.5))
    m.cut('DriveHousing',m.rr(14,14,2.1,(63,30,37.2),.5),'Original RF amplifier thermal window').Refine=False
    m.box('DriveRFThermal','RF amplifier thermal pad',8,8,1.0,(63,30,37.8),'Optical',2,'thermalpink',.3,True)
    for key,x,y,pins,width,side in [('RFMainFlex',63,43,24,14,-1),('RFPickupFlex',63,16,16,10,1)]:
        before=set(m.parts);_board_fpc(m,key,x,y,pins,width,side=side)
        _move_optical_electronics(m,set(m.parts)-before,33.1)
    for i,(x,y) in enumerate([(x,y) for x in [44,82] for y in [22,28,34,40]]):
        before=set(m.parts);_board_passive(m,'RFPassive'+str(i),x,y,'black' if i%2 else 'ceramic')
        _move_optical_electronics(m,set(m.parts)-before,33.1)
    for i,(x,y) in enumerate(mounts):
        m.ring('RFBoardPillar'+str(i),'RF board mounting standoff',1.9,.8,1.8,(x,y,39.1),'Optical',3,'ps2black',internal=True)
        m.screw('RFBoardScrew'+str(i),(x,y,42.4),'Optical',4,length=2.6,radius=1.8,axis=(0,0,-1))
    m.label('DriveRFMark','GM-038 STUDY',1.35,(52,47.1,41.925),'Optical',3,'white')
    m.profile['stages']=19
    m.checkpoint(19,'separate_gm038_rf_board_and_thermal_interface','加入初代 GM-038 独立光驱板、底面 CXA2605R 放大器封装及热窗口、导热垫、两组排线插座和周边阻容元件，保留独立安装柱与螺钉。')


STAGES[19]=stage19


def stage20(m):
    from .ps1 import _add_shape
    x=61.5;mounts=[(-2,-76),(125,-76),(-2,74),(125,74)]
    m.native('DriveCover','Native grid-ribbed original optical cover',136,164,1.2,1.4,(x,-1,68.0),'Optical',7,'ps2black')
    cuts=[Part.makeCylinder(15.3,1.9,V(x,-18,67.75))]
    cuts += [Part.makeCylinder(1.2,1.9,V(xx,yy,67.75)) for xx,yy in mounts]
    label_field=m.rr(78,26,1,(x,52,68.9),.7)
    grid=[Part.makeBox(.35,161,.45,V(xx,-81.5,69.15)) for xx in range(-2,127,10)]
    grid += [Part.makeBox(133,.35,.45,V(-5,yy,69.15)) for yy in range(-76,76,10)]
    cuts.append(Part.makeCompound(grid).cut(label_field))
    m.cut('DriveCover',cuts,'Original grid pattern, clamp opening and four lid screw holes').Refine=False
    pillars=[]
    for i,(xx,yy) in enumerate(mounts):
        pillar=Part.makeCylinder(2.4,7.3,V(xx,yy,60.5)).cut(Part.makeCylinder(.9,7.7,V(xx,yy,60.3)))
        edge=-5.9 if xx<0 else 128.9
        bridge=Part.makeBox(abs(edge-xx)+1.0,3.6,5,V(min(xx,edge)-.5,yy-1.8,60.5))
        pillars.append(pillar.fuse(bridge).cut(Part.makeCylinder(.9,7.7,V(xx,yy,60.3))))
        m.screw('DriveCoverScrew'+str(i),(xx,yy,70),'Optical',8,length=6.2,radius=2.3,axis=(0,0,-1))
    _add_shape(m,'DriveHousing',Part.makeCompound(pillars),'Four cover support pillars and side ties').Refine=False
    m.ring('ClampSeat','Optical cover clamp locating ring',15,10,.8,(x,-18,68.1),'Optical',7,'black',internal=True)
    cap=Part.makeCylinder(15.5,.8,V(x,-18,69.65)).cut(Part.makeCylinder(1.1,1.2,V(x,-18,69.45)))
    m.feature('ClampTopCap','Circular optical-cover clamp cap',cap,'Optical',8,'black')
    clamp=Part.makeCylinder(13,1.8,V(x,-18,58.9)).cut(Part.makeCylinder(1.15,2.2,V(x,-18,58.7)))
    m.feature('MagneticClamp','Optical disc magnetic clamping disc',clamp,'Optical',6,'black',True)
    m.ring('ClampGrip','Clamp lower grip ring',12.7,8,.25,(x,-18,58.6),'Optical',6,'rubber',internal=True)
    m.ring('ClampMagnet','Disc clamp magnet',6,1.05,.7,(x,-18,60.75),'Optical',6,'metal',internal=True)
    m.ring('ClampHub','Clamp support hub',4,1.0,6.45,(x,-18,61.5),'Optical',7,'black',internal=True)
    m.cyl('ClampAxle','Clamp locating axle',.85,8.8,(x,-18,60.8),'Optical',7,'metal',internal=True)
    m.label('DriveCoverLabel','OPTICAL DRIVE',1.7,(48,53,69.425),'Optical',8,'ps2word')
    m.label('DriveMediaLabel','DVD / CD',2.2,(51,47.5,69.425),'Optical',8,'ps2word')
    for i,(xx,yy) in enumerate([(-9.5,-59),(132.5,47)]):
        m.ring('DriveCaseSpacer'+str(i),'Drive-to-middle-frame spacer',2.5,.9,1.3,(xx,yy,36.1),'Frame',3,'ps2black',internal=True)
        m.screw('DriveCaseScrew'+str(i),(xx,yy,40.05),'Optical',4,length=5.5,radius=2.4,axis=(0,0,-1))
    m.cut('MiddleFrame',[Part.makeCylinder(.85,2.7,V(xx,yy,33.8)) for xx,yy in [(-9.5,-59),(132.5,47)]],'Two optical assembly fixing pilots').Refine=False
    m.profile['stages']=20
    m.checkpoint(20,'native_grid_cover_magnetic_clamp_and_drive_fixings','建立带原版网格纹理的原生光驱上盖、四个盖板固定件和独立盘片磁性夹持结构，补充两组光驱到中框的安装件；装配保持关闭托盘的静态展示位置。')


STAGES[20]=stage20


def _fit_one_mark(m,key,body_key,margin=.8):
    obj=m.parts[key];shape=obj.Shape;box=shape.optimalBoundingBox(False,False)
    body=m.parts[body_key].Shape.optimalBoundingBox(False,False)
    scale=min(1,(body.XLength-2*margin)/box.XLength,(body.YLength-2*margin)/box.YLength)
    matrix=App.Matrix();matrix.A11=scale;matrix.A22=scale
    matrix.A14=body.Center.x-scale*box.Center.x;matrix.A24=body.Center.y-scale*box.Center.y
    fitted=shape.transformGeometry(matrix);fitted.check(True);obj.Shape=fitted;obj.FlatPlacement=obj.Placement


def stage21(m):
    from .atari2600 import _rounded_route
    from .ps1 import _add_shape
    _fit_one_mark(m,'DriveRFAmpMark','DriveRFAmp')
    # Move the provisional board header forward to clear the plugged cable.
    for key in ['FanHeader','FanHeaderPin0','FanHeaderPin1','FanHeaderPin2']:
        obj=m.parts[key];obj.Placement.Base.y-=5;obj.FlatPlacement=obj.Placement
    for obj in m.doc.Objects:
        if obj.TypeId=='Part::Feature' and 'fan-connector terminal passages' in obj.Label:
            shape=obj.Shape.copy();shape.translate(V(0,-5,0));obj.Shape=shape
    m.profile['envelope_groups']=list(dict.fromkeys(m.profile['envelope_groups']+['Wiring']))
    m.colors['wiregray']=(.48,.49,.47)
    # Three-position fan connector and a parallel, routed motor harness.
    plug=m.rr(3.4,2.9,6,(-28,65,10.15),.25)
    for i,dx in enumerate([-1.15,0,1.15]):
        plug=plug.cut(Part.makeCylinder(.48,6.4,V(-28+dx,65,9.95)))
        m.ring('FanPlugContact'+str(i),'Fan harness socket terminal',.40,.31,4.9,(-28+dx,65,10.25),'Wiring',1,'metal',internal=True)
        points=[V(-28+dx,65,16.5),V(-28+dx,60,18),V(-27+dx,61,24),V(-32+dx,63,31),V(-48+dx,64,43),V(-51+dx,70.1,48)]
        m.feature('FanHarness'+str(i),'Rear fan motor harness lead',_rounded_route(points,.75,.22),'Wiring',2,'wiregray',True)
    m.feature('FanHarnessPlug','Fan cable plug insulator',plug,'Wiring',1,'white',True)
    # A seven-way button/light harness follows the side of the drive and
    # passes through a dedicated frame aperture and retained ferrite bead.
    rear=g.rotation((0,1,0),(0,0,1))
    board_socket=m.rr(8,3.8,4,(104,-63,9),.4)
    control_socket=m.rr(8,4,3.2,(139,-76.7,57.5),.4,rear);holes=[]
    for i in range(7):
        dx=(i-3)*.7;bundle=(i-3)*.45
        board_socket=board_socket.cut(Part.makeCylinder(.27,4.4,V(104+dx,-63,8.8)))
        control_socket=control_socket.cut(Part.makeCylinder(.27,3.7,V(139+dx,-76.9,57.5),V(0,1,0)))
        m.cyl('ControlMainPin'+str(i),'Button harness mainboard terminal',.16,6.3,(104+dx,-63,7),'Wiring',0,'metal',internal=True)
        m.cyl('ControlBoardPin'+str(i),'Button board harness terminal',.16,3.5,(139+dx,-76.8,57.5),'Wiring',2,'metal',axis=(0,1,0),internal=True)
        holes.append(Part.makeCylinder(.30,2.2,V(104+dx,-63,6.8)))
        points=[V(139+dx,-73.15,57.5),V(140+bundle,-70,57.5),V(140+bundle,-63+bundle,50),V(140+bundle,-63+bundle,34.6),V(110+bundle,-63+bundle,34.6),V(110+bundle,-63+bundle,20),V(104+dx,-63,13.4)]
        m.feature('ControlHarness'+str(i),'Power/eject and status-light harness lead',_rounded_route(points,.7,.12),'Wiring',2,'wiregray',True)
    m.feature('ControlMainSocket','Seven-position control harness mainboard socket',board_socket,'Wiring',1,'white',True)
    m.feature('ControlBoardSocket','Power/eject board cable socket',control_socket,'Wiring',2,'white',True)
    m.cut('Mainboard',holes,'Control harness terminal holes').Refine=False
    m.cut('MiddleFrame',m.rr(6,5,3.0,(140,-63,33.4),.7),'Control harness passage beside optical drive').Refine=False
    m.cut('MiddleFrame',m.rr(34,5,1.4,(125,-63,33.9),.4),'Horizontal control harness channel through frame').Refine=False
    m.ring('ControlFerrite','Retained control-harness ferrite bead',3.3,2.2,5,(140,-63,38.5),'Wiring',2,'black',internal=True)
    posts=[Part.makeCylinder(1.2,4.1,V(x,y,35.9)) for x in [136,144] for y in [-67.5,-58.5]]
    _add_shape(m,'MiddleFrame',Part.makeCompound(posts),'Four harness retention guide posts').Refine=False
    paths=[
        [(-114,80.15,44.4),(-109,73,43),(-110,64,44),(-114.5,58,48),(-114.5,52,47)],
        [(-122,80.15,44.4),(-132,73,46),(-134,70,58),(-122,74.4,64)],
        [(-114,74.4,64),(-104,69,63),(-110,61,60),(-119.5,57,54),(-119.5,52,47)],
    ]
    for i,path in enumerate(paths):m.feature('InternalACHarness'+str(i),'AC inlet, rocker and PSU connection study',_rounded_route([V(*p) for p in path],.6,.4),'Wiring',3,'wiregray',True)
    m.profile['stages']=21
    m.checkpoint(21,'fan_control_and_mains_harnesses_with_frame_guides','补齐风扇、电源与出仓控制及内部 AC 连接线束，加入独立端子、绝缘插头、磁环和四个导向柱；同时将光驱 RF 芯片文字限制在封装表面内。')


STAGES[21]=stage21


def _flat_ribbon(points,width,thickness=.12,bend=.3):
    """Thin ruled strip with constant X width and rounded Y/Z-plane bends.

    Skew X runs are allowed, but no segment may run only along X. This keeps
    the section orientation explicit instead of twisting a wide pipe profile.
    """
    import math
    points=[V(*p) for p in points];edges=[];last=points[0]
    for previous,current,following in zip(points,points[1:],points[2:]):
        incoming=(current-previous).normalize();outgoing=(following-current).normalize()
        angle=math.acos(max(-1,min(1,incoming.dot(outgoing))))
        if angle<1e-6:continue
        trim=bend*math.tan(angle/2);assert trim<.45*min((current-previous).Length,(following-current).Length)
        entry=current-incoming*trim;leave=current+outgoing*trim
        center=current+(outgoing-incoming).normalize()*(bend/math.cos(angle/2))
        middle=center+(current-center).normalize()*bend
        edges.extend([Part.makeLine(last,entry),Part.Arc(entry,middle,leave).toShape()]);last=leave
    edges.append(Part.makeLine(last,points[-1]));sections=[]
    for ei,edge in enumerate(edges):
        count=4 if isinstance(edge.Curve,Part.Circle) else 1
        for i in range(count+1):
            if ei and i==0:continue
            parameter=edge.FirstParameter+(edge.LastParameter-edge.FirstParameter)*i/count
            center=edge.valueAt(parameter);tangent=edge.tangentAt(parameter)
            normal=V(0,-tangent.z,tangent.y);assert normal.Length>1e-7;normal.normalize()
            wide=V(width/2,0,0);thin=normal*(thickness/2)
            corners=[center-wide-thin,center+wide-thin,center+wide+thin,center-wide+thin]
            sections.append(Part.Wire(Part.makePolygon(corners+[corners[0]]).Edges))
    shape=Part.makeLoft(sections,True,True);assert shape.isValid() and shape.Solids
    shape.check(True);return shape


def _change_electronics_group(m,names,assembly,z=0,flip=None):
    for key in names:
        obj=m.parts[key];m.group(obj.Assembly).removeObject(obj);m.group(assembly).addObject(obj);obj.Assembly=assembly
        obj.Placement.Base.z+=z
        if flip:obj.Placement=App.Placement(V(),App.Rotation(V(1,0,0),180),V(*flip)).multiply(obj.Placement)
        obj.FlatPlacement=obj.Placement


def stage22(m):
    before=set(m.parts);_board_fpc(m,'FrontPortFlex',-48,-58,18,11,side=1)
    _change_electronics_group(m,set(m.parts)-before,'FrontIO',33.0)
    controller=[(-48,-56.5,43.42),(-48,-51,43.42),(-48,-51,40.3),(-48,-80,40.3),(-48,-80,12.2),(-48,-66.5,12.2),(-48,-66.5,10.45),(-48,-70.5,10.45)]
    m.feature('ControllerRibbon','Shared controller/card board flat cable',_flat_ribbon(controller,10.2),'Wiring',2,'white',True)
    m.cut('MiddleFrame',m.rr(12,3,3.0,(-48,-80,33.4),.5),'Front interface ribbon route through frame').Refine=False
    before=set(m.parts);_board_fpc(m,'PickupFlex',63,24,16,10,side=1)
    _change_electronics_group(m,set(m.parts)-before,'Optical',38.25,(63,24,46.775))
    pickup=[(63,17,43.55),(63,20,43.55),(63,20,44.92),(63,22.6,44.92)]
    m.feature('PickupRibbon','Pickup-to-GM-038 flat cable',_flat_ribbon(pickup,9.4,bend=.25),'Wiring',4,'white',True)
    main=[(63,41,43.55),(63,37,43.55),(82,10,43.55),(82,10,31),(-10,-40,31),(-10,-46,15),(-10,-58,15),(-10,-58,10.45),(-10,-52.8,10.45)]
    m.feature('OpticalMainRibbon','GM-038-to-mainboard flat cable study',_flat_ribbon(main,13.4,bend=.5),'Wiring',2,'white',True)
    m.cut('DriveHousing',m.rr(15,5,2.2,(82,10,37.1),.5),'Optical board ribbon passage below drive').Refine=False
    m.profile['stages']=22
    m.checkpoint(22,'controller_and_optical_flat_cables_with_real_passages','加入共享手柄接口板排线、光头到 GM-038 的短排线及光驱板到主板的长排线，补齐连接器与穿过中框和光驱底壳的实际通道。')


STAGES[22]=stage22


CASE_FIXINGS=[(-135,-72),(106,-72),(-135,72),(106,72),(-15,76),(-80,-79),(-15,-79),(62,-79),(20,79),(112,79)]


def stage23(m):
    from .ps1 import _add_shape
    # Separate the rear shield fixing from the original foot-position case screw.
    for key in ['ShieldSupport2','ShieldScrew2']:
        obj=m.parts[key];obj.Placement.Base+=V(2,-4,0);obj.FlatPlacement=obj.Placement
    for obj in m.doc.Objects:
        if obj.TypeId=='Part::Feature' and obj.Label.startswith(('Four shield fixing holes and underside flex access windows','Blind bores for the four lower shield fasteners')):
            shapes=list(obj.Shape.Solids)
            for shape in shapes:
                center=shape.BoundBox.Center
                if abs(center.x-108)<1e-5 and abs(center.y-71)<1e-5:shape.translate(V(2,-4,0))
            obj.Shape=Part.makeCompound(shapes)
    posts=[];floor_tools=[];board_tools=[]
    for i,(x,y) in enumerate(CASE_FIXINGS):
        long=i in [2,4];radius=1.6 if long else 1.25;height=45 if long else 31.8
        post=Part.makeCylinder(radius,height,V(x,y,3.2)).cut(Part.makeCylinder(.8,height+.4,V(x,y,3.0)))
        rear=82 if y>0 else -82
        bridge=Part.makeBox(4,abs(rear-y)+1,1.2,V(x-2,min(y,rear)-.5,33.8))
        posts.append(post.fuse(bridge).cut(Part.makeCylinder(.8,46,V(x,y,3.0))))
        m.screw('CaseScrew'+str(i),(x,y,1.6),'Body',-4,length=42 if long else 28,radius=2.1)
        floor_tools += [Part.makeCylinder(.95,2.3,V(x,y,1.2)),Part.makeCylinder(2.3,1.05,V(x,y,1.2))]
        board_tools.append(Part.makeCylinder(radius+.2,2.2,V(x,y,7.0)))
        if i>=4:m.cyl('CasePlug'+str(i),'Removable lower case screw cover',2.55,.95,(x,y,.35),'Body',-5,'ps2black')
    _add_shape(m,'MiddleFrame',Part.makeCompound(posts),'Ten case attachment pillars and perimeter ties').Refine=False
    m.cut('MiddleFrame',[Part.makeCylinder(.8,46,V(x,y,3.0)) for x,y in CASE_FIXINGS],'Case screw pilot bores through existing frame ties').Refine=False
    m.cut('LowerHousing',floor_tools,'Ten lower case screw bores and head recesses').Refine=False
    m.cut('Mainboard',board_tools,'Outer case pillar passages at mainboard edges').Refine=False
    m.cut('LowerShield',[Part.makeCylinder((1.6 if i in [2,4] else 1.25)+.2,3.4,V(x,y,3.4)) for i,(x,y) in enumerate(CASE_FIXINGS)],'Outer case pillar passages through lower shielding').Refine=False
    # Native upper-shell snap tongues engage the middle-frame perimeter.
    clips=[]
    for side in [-1,1]:
        for y in [-40,40]:
            beam=Part.makeBox(4,6,1,V(145,y-3,39.5))
            stem=Part.makeBox(1,4,6.2,V(145,y-2,33.4))
            hook=Part.makeBox(2,4,.3,V(144,y-2,33.4))
            clip=beam.multiFuse([stem,hook])
            if side<0:clip.rotate(V(),V(0,0,1),180)
            clips.append(clip)
    _add_shape(m,'UpperHousing',Part.makeCompound(clips),'Four upper-shell snap tongues').Refine=False
    m.cut('MiddleFrame',[m.rr(1.4,5,4.4,(side*145.5,y,33.1),.25) for side in [-1,1] for y in [-40,40]],'Snap-tongue clearance notches').Refine=False
    m.profile['stages']=23
    m.checkpoint(23,'ten_case_fixings_screw_covers_and_native_snap_tongues','补齐十组底部机壳固定件和内部支柱，其中后侧两根较长；四个脚垫位置保留，另加六个螺钉盖，并在原生上壳加入四个卡扣与中框避让槽。')


STAGES[23]=stage23


def stage24(m):
    from .atari2600 import _rounded_route
    starts=[
        [(46.5,-18,44.95),(46.5,-43,45),(110,-44,45)],
        [(76.5,-18,44.95),(78,-41,45.5),(111,-42,45.5)],
        [(101,78,48.5),(112,78,48.5),(114,70,42.3),(114,-22,42.3)],
        [(105,78.3,49),(113,78.3,49),(115,69,42.8),(115,-21,42.8)],
        [(17.5,-66,46.85),(13,-60,47),(13,-47,44),(108,-45,43.5)],
        [(22.5,-66,46.85),(25,-59,47),(25,-45,44.5),(109,-43,44.5)],
    ]
    for i,start in enumerate(starts):
        x=109+i*.6;y=-26+i;dx=(1+i*3-9.5)*11.2/19
        path=start+[(x,y,40+i*.8),(x,y,30),(35+dx,-12,20),(35+dx,-11,10.5),(35+dx,-6,10.5)]
        m.feature('DriveMotorHarness'+str(i),'Spindle, feed and tray motor harness study',_rounded_route([V(*p) for p in path],.45,.16),'Wiring',3,'wiregray',True)
    m.cut('DriveHousing',m.rr(6,9,2.2,(110.5,-23.5,37.1),.4),'Drive motor harness outlet below mechanism').Refine=False
    bottom=g.rotation((0,0,-1),(0,1,0));m.colors['labelblack']=(.09,.10,.11)
    m.box('BottomStudyLabel','Lower-housing model identification label',110,36,.05,(-45,0,1.35),'Body',-5,'labelblack',1,orient=bottom)
    m.label('BottomModelMark','SCPH-10000 / CAD STUDY',2.2,(-10,-4,1.275),'Body',-5,'white',rotation=bottom)
    m.label('BottomStudyMark','OPEN CONSOLE CAD',1.8,(-20,4,1.275),'Body',-5,'white',rotation=bottom)
    m.profile['stages']=24
    m.checkpoint(24,'optical_motor_harness_and_model_identification','补齐主轴、光头进给和装载电机到主板的示意线束及底壳型号标签；连接数量和布线作为非功能性结构学习模型，标识明确注明 CAD STUDY。')


STAGES[24]=stage24


def rear_snapshot(m,name='rear_review',assemblies=None,exclude=(),normal=(.2,1.8,.45)):
    """Keep +Z upright while inspecting the positive-Y rear face."""
    import FreeCADGui as Gui
    up=(0,0,1);q=g.rotation(normal,up)
    App.setActiveDocument(m.doc.Name);Gui.activateView('Gui::View3DInventor',True)
    objects=m.visible(assemblies,exclude);shape=Part.makeCompound([o.Shape for o in objects])
    shape.Placement=App.Placement(V(),q.inverted()).multiply(shape.Placement)
    b=shape.optimalBoundingBox(False,False);size=(1800,1400);span=max(b.YLength,b.XLength*size[1]/size[0])*1.16
    return g.render(m.out/'previews'/(name+'.png'),normal=normal,up=up,target=tuple(q.multVec(b.Center)),span=span,size=size)
