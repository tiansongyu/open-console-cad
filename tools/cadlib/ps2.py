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
    _board_fpc(m,'UnderRearFlex',25,72,24,14,underside=True,side=-1)
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
    cuts += [m.rr(22,8,1.1,(-18,-66,3.4),.5),m.rr(18,8,1.1,(25,72,3.4),.5)]
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


def rear_snapshot(m,name='rear_review',assemblies=None,exclude=(),normal=(.2,1.8,.45)):
    """Keep +Z upright while inspecting the positive-Y rear face."""
    import FreeCADGui as Gui
    up=(0,0,1);q=g.rotation(normal,up)
    App.setActiveDocument(m.doc.Name);Gui.activateView('Gui::View3DInventor',True)
    objects=m.visible(assemblies,exclude);shape=Part.makeCompound([o.Shape for o in objects])
    shape.Placement=App.Placement(V(),q.inverted()).multiply(shape.Placement)
    b=shape.optimalBoundingBox(False,False);size=(1800,1400);span=max(b.YLength,b.XLength*size[1]/size[0])*1.16
    return g.render(m.out/'previews'/(name+'.png'),normal=normal,up=up,target=tuple(q.multVec(b.Center)),span=span,size=size)
