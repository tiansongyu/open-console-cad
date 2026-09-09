"""Original Japanese SCPH-1000: editable grey enclosure and later staged internals."""
import FreeCAD as App
import Part
import Sketcher
from .core import V
from . import geometry as g


def stage01(m):
    m.colors.update({'psgrey':(.59,.60,.62),'psdark':(.27,.28,.30),'psgreen':(.10,.56,.42),'psblue':(.24,.48,.72)})
    m.params.set('A3','Depth (Y)');m.params.set('A4','Height (Z)')
    m.native('LowerHousing','Original grey lower housing',270,188,4.2,12.6,(0,0,1.4),'Body',-6,'psgrey',expr={'Width':'Parameters.Width','Height':'Parameters.Height'})
    m.cut('LowerHousing',m.rr(266.4,184.4,12.0,(0,0,3.2),2.4),'Lower enclosure interior')
    m.native('UpperHousing','Original grey upper enclosure',270,188,4.2,42.72,(0,0,14.18),'Body',5,'psgrey',expr={'Width':'Parameters.Width','Height':'Parameters.Height'})
    m.cut('UpperHousing',m.rr(266.4,184.4,40.8,(0,0,14.0),2.4),'Hollow upper enclosure with top skin')
    # Shallow moulding lines divide the central top field and the two side wings.
    grooves=[m.rr(.7,183.8,1.3,(x,0,55.7),.10) for x in [-88,88]]
    grooves += [m.rr(.7,1.3,39,(x,-93.85,15),.10) for x in [-88,88]]
    m.cut('UpperHousing',grooves,'Side-wing and front-face moulding lines')
    for i,(x,y) in enumerate([(-112,-73),(112,-73),(-112,73),(112,73)]):
        m.cyl('Foot'+str(i),'Rubber support foot',4.5,1.2,(x,y,0),'Body',-6,'rubber')
    m.profile['stages']=1
    m.checkpoint(1,'original_grey_native_enclosure','建立 270 × 188 mm 原生参数草图、上下空心壳、侧翼分界和四个脚垫；包络依据为同系列后期说明书，SCPH-1000 的尺寸明确标记为学习近似。')


def _native_disc(m):
    body=m.doc.addObject('PartDesign::Body','DiscLidBody');body.Label='Circular hinged disc lid'
    sketch=body.newObject('Sketcher::SketchObject','DiscLidSketch')
    sketch.addGeometry(Part.Circle(V(),V(0,0,1),85),False)
    sketch.addConstraint(Sketcher.Constraint('Coincident',0,3,-1,1))
    sketch.addConstraint(Sketcher.Constraint('Radius',0,85))
    pad=body.newObject('PartDesign::Pad','DiscLidPad');pad.Profile=sketch;pad.Length=3
    m.doc.recompute()
    rim=body.newObject('PartDesign::Fillet','DiscLidRim');rim.Base=(pad,[f'Edge{i+1}' for i,e in enumerate(pad.Shape.Edges) if e.BoundBox.ZLength<1e-7 and e.BoundBox.ZMax>2.9]);rim.Radius=1.0
    m.doc.recompute();assert rim.Shape.isValid() and rim.Shape.Solids
    body.Tip=rim;pad.Visibility=False;sketch.Visibility=False;body.Placement=App.Placement(V(0,4,57),App.Rotation())
    return m.register(body,'DiscLid','Optical',8,'psgrey')


def stage02(m):
    m.cut('UpperHousing',Part.makeCylinder(85.35,5,V(0,4,53.8)),'Circular disc-holder opening')
    _native_disc(m)
    m.cut('DiscLid',Part.makeCylinder(82.8,1.85,V(0,4,56.8)),'Shallow underside of the disc cover')
    # Raised circular opening/closing controls, with a smaller separate reset key.
    for key,x,y,r,caption,color in [('Power',-110,-58,16.2,'POWER','psgreen'),('Open',110,-58,16.2,'OPEN','psblue'),('Reset',-110,-24,7.4,'RESET','psdark')]:
        m.cut('UpperHousing',Part.makeCylinder(r+.35,5,V(x,y,53.0)),key+' button opening')
        cap=Part.makeCylinder(r,2.3,V(x,y,54.85))
        edges=[e for e in cap.Edges if e.BoundBox.ZLength<1e-7 and e.BoundBox.ZMax>57]
        cap=cap.makeFillet(.45,edges)
        m.feature(key+'Button',caption+' button',cap,'Controls',6,'psgrey')
        m.label(key+'Legend',caption,2.1 if key!='Reset' else 1.4,(x-(len(caption)*(.70 if key!='Reset' else .46)),y-.8,57.17),'Controls',6,color)
    m.cut('UpperHousing',m.rr(2.4,9.5,2.2,(-110,-88.5,55.0),.2),'Power indicator window')
    m.box('PowerLens','Narrow power indicator',2.0,9.1,.5,(-110,-88.5,56.3),'Controls',5,'psgreen',.15)
    # The tall side slots are real cuts through the upper wall.
    slots=[Part.makeBox(4.0,1.8,34.8,V(x,y,18.0)) for x in [-136,132] for y in [-85+i*4 for i in range(43)]]
    m.cut('UpperHousing',slots,'Paired side cooling-slot arrays')
    m.label('SonyMark','SONY',4.0,(-9.0,56.0,60.025),'Optical',8,'psdark')
    m.label('PlayStationMark','PlayStation',3.3,(-13.0,-32.0,60.025),'Optical',8,'psdark')
    m.profile['stages']=2
    m.checkpoint(2,'disc_lid_controls_and_side_vents','加入原生圆形光盘盖、上盖开口、POWER/RESET/OPEN 三键和标识、狭长电源灯，以及两侧贯穿散热槽；保留独立可编辑圆盖与圆角历史。')


STAGES={1:stage01,2:stage02}


def stage03(m):
    front=g.rotation((0,-1,0),(0,0,1))
    m.profile['envelope_groups']=list(dict.fromkeys(m.profile['envelope_groups']+['FrontIO']))
    m.native('FrontPortPCB','Shared controller and memory-card PCB',131,18,1.0,1.3,(0,-74,14.7),'FrontIO',1,'pcb')
    lead_bores=[]
    for n,x in [(1,-36.5),(2,36.5)]:
        key='Port'+str(n)
        m.cut('UpperHousing',m.rr(50.0,29.0,5,(x,-90.0,29.0),3.4,front),'Front dual-level port aperture')
        outer=m.rr(49.4,28.4,3,(x,-91.1,29.0),3.2,front)
        openings=[m.rr(44.6,8.7,3.5,(x,-90.9,36.75),.65,front),m.rr(42,8.8,3.5,(x,-90.9,22.5),2.3,front)]
        m.feature(key+'Frame','Controller '+str(n)+' and memory-card front frame',outer.cut(Part.makeCompound(openings)),'FrontIO',2,'psgrey')
        case=m.rr(47,25.8,14.9,(x,-76,29),2.0,front).cut(m.rr(44.6,23.4,15.0,(x,-77.1,29),1.0,front))
        m.feature(key+'Case','Insulated dual connector housing',case,'FrontIO',1,'psdark',True)
        m.box(key+'Shutter','Memory-card hinged dust shutter',44,7.4,.8,(x,-90.8,36.5),'FrontIO',2,'psgrey',.45,orient=front)
        m.label(key+'CardMark','MEMORY CARD',2.2,(x-11.5,-91.64,35.7),'FrontIO',2,'psdark',rotation=front)
        m.cyl(key+'ShutterPin','Memory-card shutter pivot',.36,43.6,(x-21.8,-90.4,40.7),'FrontIO',1,'metal',axis=(1,0,0),internal=True)
        m.box(key+'CardTongue','Eight-contact memory-card tongue',40,10,.8,(x,-84,33.8),'FrontIO',1,'psgrey',.35,True)
        for i in range(8):
            m.box(key+'CardContact'+str(i),'Memory-card contact '+str(i+1),1.25,10.7,.22,(x+(i-3.5)*4.5,-84,34.62),'FrontIO',1,'gold',.08,True)
        case_bores=[]
        for block in range(3):
            bx=x+(block-1)*13
            insert=m.rr(12.4,5.4,4,(bx,-87,22.5),1.4,front)
            bores=[Part.makeCylinder(.72,4.4,V(bx+(i-1)*3.6,-86.8,22.5),V(0,-1,0)) for i in range(3)]
            m.feature(key+'Triplet'+str(block),'Three-way controller socket insulator',insert.cut(Part.makeCompound(bores)),'FrontIO',2,'psgrey')
            for i in range(3):
                xx=bx+(i-1)*3.6;idx=block*3+i
                sleeve=Part.makeCylinder(.64,4.6,V(xx,-85.9,22.5),V(0,-1,0)).cut(Part.makeCylinder(.42,4.8,V(xx,-85.8,22.5),V(0,-1,0)))
                run=Part.makeBox(.44,17.12,.44,V(xx+.28,-86.1,22.28))
                leg=Part.makeBox(.44,.44,8.12,V(xx+.28,-69.2,14.6))
                contact=sleeve.fuse(run).fuse(leg).removeSplitter()
                m.feature(key+'ControllerContact'+str(idx),'Controller contact '+str(idx+1)+' with PCB leg',contact,'FrontIO',1,'gold',True)
                case_bores.append(m.rr(1.3,1.1,4,(xx+.45,-74.8,22.5),.15,front))
                lead_bores.append(Part.makeCylinder(.60,2,V(xx+.5,-68.98,14.4)))
        m.cut(key+'Case',case_bores,'Controller terminal passages through the rear wall')
        m.label('ControllerNumber'+str(n),str(n),4,(x-1.3,-94.025,46),'Body',5,'psdark',rotation=front)
        for side in [-1,1]:
            m.box(key+'ShutterGrip'+str(side),'Shutter finger marking',.32,4.8,.03,(x+side*20,-91.64,36.5),'FrontIO',2,'psdark',.05,orient=front)
    m.cut('FrontPortPCB',lead_bores,'Eighteen controller solder-leg bores')
    m.profile['stages']=3
    m.checkpoint(3,'dual_controller_and_memory_card_ports','建立共享前接口 PCB、两个独立记忆卡防尘门、8 接点卡槽，以及按三组三孔分区的 9 接点手柄插座；插针带真实 PCB 腿并预留穿板和外壳孔。')


STAGES[3]=stage03


def _rect_rear_port(m,key,x,pins):
    rear=g.rotation((0,1,0),(0,0,1))
    outer=m.rr(19.4,8.8,12,(x,82.1,25),1.0,rear)
    inner=m.rr(18.5,7.9,12.4,(x,81.9,25),.65,rear)
    m.feature(key+'Shell',key+' rectangular connector shell',outer.cut(inner),'Ports',0,'metal')
    m.box(key+'Tongue',key+' insulating tongue',16.2,1.35,8.8,(x,83.6,24.4),'Ports',0,'black',.2,True,orient=rear)
    pitch=13.2/(pins-1)
    for i in range(pins):
        m.box(key+'Contact'+str(i),key+' contact '+str(i+1),.50,.16,7.4,(x+(i-(pins-1)/2)*pitch,84.8,25.2),'Ports',0,'gold',.025,True,orient=rear)
    m.cut('UpperHousing',m.rr(20,9.4,5,(x,90,25),1.2,rear),key+' rear-panel opening')


def stage04(m):
    rear=g.rotation((0,1,0),(0,0,1))
    m.colors['yellow']=(.86,.65,.12)
    # Correct the front panel width from the firsthand photographs. Editing the
    # original cutting tool preserves its place in the native feature history.
    tools=[o for o in m.doc.Objects if o.Label=='Side-wing and front-face moulding lines · tool']
    assert len(tools)==1
    grooves=[m.rr(.7,183.8,1.3,(x,0,55.7),.10) for x in [-64,64]]
    grooves += [m.rr(.7,1.3,39,(x,-93.85,15),.10) for x in [-64,64]]
    tools[0].Shape=Part.makeCompound(grooves);m.doc.recompute()
    for n,x in [(1,-36.5),(2,36.5)]:
        m.cut('Port'+str(n)+'Case',Part.makeCylinder(.48,44.2,V(x-22.1,-90.4,40.7),V(1,0,0)),'Shutter-pivot clearance in the connector roof')
    m.cut('UpperHousing',m.rr(122,25,1.4,(0,92.7,27.5),2.0,rear),'Original recessed rear connection panel')
    _rect_rear_port(m,'Serial',45,8)
    _rect_rear_port(m,'MultiAV',-48,12)
    for key,x,color in [('AudioR',25,'red'),('AudioL',10,'white'),('Video',-11,'yellow')]:
        support=m.rr(12.4,12,7.8,(x,81.6,24.7),1.1,rear).cut(Part.makeCylinder(4.9,13,V(x,81,24.7),V(0,1,0)))
        m.feature(key+'Housing',key+' RCA jack support',support,'Ports',0,'black',True)
        m.ring(key+'Barrel',key+' RCA outer shield',4.6,4.03,9.0,(x,85.4,24.7),'Ports',0,'metal',axis=(0,1,0))
        m.ring(key+'Insulator',key+' RCA colour insulator',4.0,1.65,6.4,(x,88.3,24.7),'Ports',0,color,axis=(0,1,0))
        m.ring(key+'Contact',key+' RCA centre socket',1.5,1.05,10.4,(x,84.4,24.7),'Ports',0,'metal',axis=(0,1,0))
        m.cut('UpperHousing',Part.makeCylinder(5.0,5,V(x,90,24.7),V(0,1,0)),'Dedicated RCA rear opening')
    m.ring('RFUDCHousing','RFU 2.5 mm DC socket housing',2.5,1.65,8.4,(-1,85.8,30.3),'Ports',0,'psgrey',axis=(0,1,0))
    m.ring('RFUDCContact','RFU DC socket contact',1.48,1.03,8.2,(-1,85.6,30.3),'Ports',0,'metal',axis=(0,1,0))
    m.cut('UpperHousing',Part.makeCylinder(2.8,5,V(-1,90,30.3),V(0,1,0)),'RFU DC rear opening')
    sx=-27
    m.ring('SVideoShield','SCPH-1000 dedicated S-video shield',5.8,5.35,11.6,(sx,82.4,25),'Ports',0,'metal',axis=(0,1,0))
    insert=Part.makeCylinder(5.1,6,V(sx,87,25),V(0,1,0))
    pins=[(-2.0,1.4),(2.0,1.4),(-2.6,-1.1),(2.6,-1.1)]
    holes=[Part.makeCylinder(.56,6.8,V(sx+dx,86.8,25+dz),V(0,1,0)) for dx,dz in pins]
    holes += [m.rr(2.5,1.3,6.8,(sx,86.8,21.5),.1,rear),m.rr(1.2,1.5,6.8,(sx,86.8,30),.1,rear)]
    m.feature('SVideoInsulator','Keyed four-pin S-video insulator',insert.cut(Part.makeCompound(holes)),'Ports',0,'psgrey')
    for i,(dx,dz) in enumerate(pins):
        m.ring('SVideoContact'+str(i),'S-video socket contact '+str(i+1),.48,.31,6.3,(sx+dx,86.2,25+dz),'Ports',0,'gold',axis=(0,1,0))
    m.cut('UpperHousing',Part.makeCylinder(6.05,5,V(sx,90,25),V(0,1,0)),'Original dedicated S-video aperture')
    # Original 68-contact parallel connector under its removable grey cover.
    pc=m.rr(60,14.4,9,(100,83,24),1.3,rear).cut(m.rr(57.6,12,9.4,(100,84.1,24),.6,rear))
    m.feature('ParallelHousing','68-contact parallel expansion housing',pc,'Ports',0,'black',True)
    m.box('ParallelTongue','Parallel connector centre tongue',56,2.8,7.4,(100,84.3,24),'Ports',0,'black',.3,True,orient=rear)
    for row,dz in enumerate([-2.2,2.2]):
        for i in range(34):
            m.box('ParallelContact'+str(row*34+i),'Parallel I/O contact '+str(row*34+i+1),.45,.23,6.7,(100+(i-16.5)*1.6,84.9,24+dz),'Ports',0,'gold',.025,True,orient=rear)
    m.cut('UpperHousing',m.rr(62,19,5,(100,90.5,24),1.6,rear),'Parallel I/O and cover opening')
    m.box('ParallelCover','Removable parallel I/O dust cover',61.4,18.4,1.0,(100,93.1,24),'Body',5,'psgrey',1.3,orient=rear)
    m.label('ParallelCoverArrow','<',3.5,(73.5,94.15,20.5),'Body',5,'psdark',rotation=rear)
    # Nonpolarized figure-eight inlet belongs to the Japanese version.
    ax=-100
    cavities=[Part.makeCylinder(4.35,10.5,V(ax+dx,85,24),V(0,1,0)) for dx in [-4.05,4.05]]
    inlet=m.rr(24.8,14.6,10,(ax,84,24),2.2,rear).cut(cavities[0].fuse(cavities[1]))
    m.feature('ACInlet','Japanese two-pin nonpolarized AC inlet',inlet,'Power',0,'black')
    for i,dx in enumerate([-4.05,4.05]):
        pin=Part.makeCylinder(.92,6.7,V(ax+dx,85.2,24),V(0,1,0)).fuse(Part.makeSphere(.92,V(ax+dx,91.9,24)))
        m.feature('ACPin'+str(i),'AC inlet contact '+str(i+1),pin,'Power',0,'metal',True)
    m.cut('UpperHousing',m.rr(25.4,15.2,5,(ax,90,24),2.4,rear),'AC inlet mounting aperture')
    for key,x,caption in [('Serial',45,'SERIAL'),('AudioR',25,'R'),('AudioL',10,'L'),('RFU',-1,'DC'),('Video',-11,'VIDEO'),('SVideo',-27,'S-VIDEO'),('MultiAV',-48,'AV MULTI'),('Parallel',100,'PARALLEL I/O'),('AC',-100,'AC IN')]:
        m.label('Rear'+key+'Legend',caption,1.75,(x+len(caption)*.52,94.025,40.5),'Body',5,'psdark',rotation=rear)
    vents=[Part.makeBox(1.25,4,3.2,V(-58+i*4,91,45.0)) for i in range(30)]
    m.cut('UpperHousing',vents,'Rear ventilation strip above the connection panel')
    m.profile['stages']=4
    m.checkpoint(4,'original_rear_outputs_and_parallel_cover','修正中央面板比例与防尘门轴配合，补齐初代专有 S-Video、三路 RCA、RFU DC、串行/多功能 AV、68 接点并口与防尘盖，以及日版非极性 AC 输入；功能标识使用英语便于学习。')


STAGES[4]=stage04


def _add_shape(m,key,shape,reason):
    old=m.parts[key]
    tool=g.part_feature(m.doc,key+'Addition',reason+' · additive tool',shape)
    m.group('Construction').addObject(tool)
    result=m.doc.addObject('Part::Fuse',key+'Fuse');result.Base=old;result.Tool=tool;result.Refine=True;result.Label=old.Label
    m.doc.recompute();assert result.Shape.isValid() and result.Shape.Solids
    old.PhysicalPart=False
    m.register(result,key,old.Assembly,old.ExplodeLayer,old.MaterialDescription,old.Fidelity.startswith('Schematic'),old.PoseGroup)
    old.Visibility=False;tool.Visibility=False
    return result


def stage05(m):
    from .atari2600 import _helical_spring
    from .psp import _polygon
    well=Part.makeCylinder(84.8,14.6,V(0,4,42)).cut(Part.makeCone(79.0,83.35,13,V(0,4,43.8)))
    well=well.cut(m.rr(110,83,13,(0,25,41.8),7))
    m.feature('DiscWell','Tapered disc recess with optical-mechanism opening',well,'Optical',5,'psgrey')
    for i,x in enumerate([-46,46]):
        tab=m.rr(3,14,8.8,(x+1.9,72.5,50.2),.55)
        _add_shape(m,'DiscLid',tab,'Integrated rear disc-lid hinge lug')
        bore=Part.makeCylinder(1.03,20,V(x-10,78,51.8),V(1,0,0))
        m.cut('DiscLid',bore,'Disc-lid hinge-pin bore')
        bracket=m.rr(16,11,11.5,(x,78,41.5),.7).cut(m.rr(7.4,12,7.3,(x,78,46.5),.35))
        bracket=bracket.cut(Part.makeCylinder(1.03,20,V(x-10,78,51.8),V(1,0,0)))
        m.feature('HingeBracket'+str(i),'Fixed disc-cover hinge support',bracket,'Optical',5,'psgrey',True)
        m.cyl('LidHingePin'+str(i),'Disc-cover steel pivot',.88,15.6,(x-7.8,78,51.8),'Optical',6,'metal',axis=(1,0,0),internal=True)
        spring=_helical_spring(1.4,.6,2.4,.17)
        spring.Placement=App.Placement(V(x-3.3,78,51.8),App.Rotation(V(0,0,1),V(1,0,0)))
        m.feature('LidTorsionSpring'+str(i),'Disc-cover return spring study',spring,'Optical',6,'metal',True)
        clearance=m.rr(17,17,18,(x,75.5,40.8),.7)
        m.cut('UpperHousing',clearance,'Integrated hinge assembly clearance')
        m.cut('DiscWell',clearance,'Disc-well hinge assembly clearance')
    # Underside hook, release slider and guides are discrete mechanical objects.
    _add_shape(m,'DiscLid',m.rr(4.4,6,5.8,(65,-46,53.2),.4),'Integrated lid latch hook')
    m.cut('DiscLid',m.rr(7,6.5,1.9,(66,-46,53),.3),'Underside latch engagement step')
    release=Part.makeBox(47,4,2,V(65,-48,51.2)).fuse(Part.makeBox(4,16,2,V(108,-60,51.2)))
    release=release.fuse(Part.makeBox(5.6,3.4,1.4,V(64.4,-47.7,53.2)))
    release=release.fuse(Part.makeCylinder(1.8,1.65,V(110,-58,53.2))).removeSplitter()
    m.feature('OpenReleaseSlider','L-shaped OPEN button and latch transmission',release,'Controls',4,'psdark',True)
    guide=m.rr(8,10,5,(93,-46,49.5),.6).cut(m.rr(9,4.8,2.7,(93,-46,50.9),.3))
    m.feature('OpenSliderGuide','Latch-slider guide channel',guide,'Controls',4,'psgrey',True)
    return_spring=_helical_spring(3.0,.6,1.1,.17);return_spring.translate(V(110,-58,53.5))
    m.feature('OpenReturnSpring','OPEN button compression return spring',return_spring,'Controls',4,'metal',True)
    m.cut('DiscWell',m.rr(50,18,4.8,(88,-51.5,50.7),.4),'Release linkage clearance under the disc well')
    # Approximate four-colour badge, built from solid outlines rather than a bitmap.
    red=_polygon([(-1.4,-27.1),(-1.4,-15),(3.1,-16.2),(5.6,-17.8),(5.8,-21.5),(4,-22.7),(1,-21.8),(1,-27.8)],60.025,.018)
    red=red.cut(_polygon([(1,-18),(3.3,-18.6),(3.3,-20.7),(1,-20)],60.02,.04))
    ring=Part.makeCylinder(1,.018).cut(Part.makeCylinder(.62,.05,V(0,0,-.01)))
    transform=App.Matrix();transform.A11=9;transform.A22=3;ring=ring.transformGeometry(transform);ring.translate(V(0,-25,60.025))
    yellow=ring.common(Part.makeBox(12,10,.1,V(-12,-30,60))).cut(red)
    green=ring.common(Part.makeBox(12,10,.1,V(0,-30,60))).cut(red)
    m.feature('PSBadgeRed','Original-family red P badge study',red,'Optical',8,'red')
    m.feature('PSBadgeYellow','Original-family yellow badge band',yellow,'Optical',8,'yellow')
    m.feature('PSBadgeGreen','Japanese-family green badge band',green,'Optical',8,'psgreen')
    m.profile['stages']=5
    m.checkpoint(5,'disc_well_hinges_and_release_linkage','加入锥形光盘仓、盖板一体轴耳、钢轴与回位弹簧、底部锁钩和 OPEN 联动滑块，并用独立几何轮廓补充初代彩色标识；为铰链与联动预留真实空隙。')


STAGES[5]=stage05


def _yz_strip(x,width,points):
    wire=Part.makePolygon([V(x,y,z) for y,z in points]+[V(x,*points[0])])
    return Part.Face(Part.Wire(wire.Edges)).extrude(V(width,0,0))


def _gear(m,x,y,z,root,outer,height,teeth):
    import math
    from .psp import _polygon
    outline=[]
    for i in range(teeth):
        for fraction,r in [(0,root),(.22,root),(.32,outer),(.68,outer),(.78,root)]:
            a=2*math.pi*(i+fraction)/teeth;outline.append((x+r*math.cos(a),y+r*math.sin(a)))
    return _polygon(outline,z,height)


def stage06(m):
    import math
    from .atari2600 import _helical_spring,_rounded_route
    m.colors.update({'flex':(.84,.37,.10),'psbrown':(.32,.24,.14)})
    # The Japanese launch-family badge contains a brownish field inside the S.
    field=Part.makeCylinder(1,.018);scale=App.Matrix();scale.A11=5.5;scale.A22=1.4
    field=field.transformGeometry(scale);field.translate(V(0,-25,60.025));field=field.cut(m.parts['PSBadgeRed'].Shape)
    m.feature('PSBadgeBrown','Japanese-family brown badge field',field,'Optical',8,'psbrown')
    m.native('OpticalBase','Suspended optical-drive base',106,79,6,2.4,(0,28,28.8),'Optical',1,'black')
    base_cuts=[Part.makeCylinder(10.2,3,V(0,4,28.5)),m.rr(30,48,3,(0,39,28.5),2.5)]
    supports=[(-44,-4),(44,8),(-42,62)]
    for i,(x,y) in enumerate(supports):
        peg=Part.makeCylinder(4,1.0,V(x,y,23)).fuse(Part.makeCylinder(2,10.5,V(x,y,24)))
        m.feature('OpticalPeg'+str(i),'Optical-drive steel support peg',peg,'Optical',0,'metal',True)
        def annulus(ro,z,h):return Part.makeCylinder(ro,h,V(x,y,z)).cut(Part.makeCylinder(2.25,h+.2,V(x,y,z-.1)))
        rubber=annulus(5,27,1.6).fuse(annulus(3.8,28.4,3.0)).fuse(annulus(5,31.4,1.6)).removeSplitter()
        m.feature('OpticalGrommet'+str(i),'Grooved rubber suspension grommet',rubber,'Optical',1,'rubber',True)
        base_cuts.append(Part.makeCylinder(4.0,3.1,V(x,y,28.4)))
    base_cuts.append(Part.makeCylinder(5.7,20,V(34,49.7,35),V(0,1,0)))
    m.cut('OpticalBase',base_cuts,'Optical motor, pickup, grommet and sled-motor clearances')
    m.cyl('SpindleMotor','Spindle motor casing',9,12.8,(0,4,25.3),'Optical',1,'metal',internal=True)
    m.cyl('SpindleMotorCap','Spindle motor end cap',9,.6,(0,4,38.2),'Optical',2,'metal',internal=True)
    m.cyl('SpindleShaft','Spindle motor shaft',1.0,6.0,(0,4,38.9),'Optical',2,'metal',internal=True)
    hub=Part.makeCylinder(10.6,1.8,V(0,4,44.2)).cut(Part.makeCylinder(1.2,2.2,V(0,4,44)))
    m.feature('SpindleHub','Disc-support spindle flange',hub,'Optical',3,'black')
    crown=Part.makeCylinder(7.4,2.4,V(0,4,46)).cut(Part.makeCylinder(6.1,2.6,V(0,4,45.9)))
    for i in range(3):
        a=2*math.pi*i/3;x,y=7.2*math.cos(a),4+7.2*math.sin(a)
        crown=crown.cut(Part.makeSphere(.96,V(x,y,47.2)))
        m.cyl('SpindleClipSpring'+str(i),'Spindle clip spring seat',.35,.55,(x*.86,4+(y-4)*.86,47.2),'Optical',3,'metal',axis=(math.cos(a),math.sin(a),0),internal=True)
        m.feature('SpindleBall'+str(i),'Disc retaining ball',Part.makeSphere(.82,V(x,y,47.2)),'Optical',3,'metal')
    m.feature('SpindleCrown','Three-point disc centring crown',crown,'Optical',3,'black')
    deck=m.rr(101,75,1.3,(0,28,40.5),6).cut(m.rr(28,51,1.8,(0,39,40.3),3))
    deck=deck.cut(Part.makeCylinder(11.2,2,V(0,4,40.2)))
    m.feature('OpticalDeck','Optical-drive upper cover with pickup window',deck,'Optical',3,'black')
    m.cut('DiscWell',m.rr(104,84,5,(0,30,40.2),6),'Optical-drive upper-cover clearance')
    for side in [-1,1]:
        m.cyl('PickupRail'+str(side),'Optical pickup guide rail',1.05,45,(side*13,18,37.6),'Optical',2,'metal',axis=(0,1,0),internal=True)
    carriage=m.rr(23.6,18,6.8,(0,39,33.5),2)
    for side in [-1,1]:
        carriage=carriage.fuse(Part.makeCylinder(2.1,15,V(side*13,31.5,37.6),V(0,1,0)))
        carriage=carriage.cut(Part.makeCylinder(1.24,51,V(side*13,14,37.6),V(0,1,0)))
    m.feature('PickupCarriage','Optical pickup carriage and rail sleeves',carriage.removeSplitter(),'Optical',2,'metal',True)
    m.box('LensHolder','Laser pickup lens holder',11,12,2.8,(0,39,40.6),'Optical',3,'black',1.3,True)
    m.ring('LensBarrel','Objective lens retaining barrel',3.0,2.0,1.3,(0,39,43.5),'Optical',3,'black')
    lens=Part.makeSphere(2.1,V(0,39,44)).common(Part.makeCylinder(1.85,1.6,V(0,39,44.5)))
    m.feature('ObjectiveLens','Convex optical pickup objective',lens,'Optical',3,'psblue')
    m.cyl('SledMotor','Horizontal pickup-feed motor',5.4,18,(34,50,35),'Optical',1,'metal',axis=(0,1,0),internal=True)
    m.cyl('SledMotorCap','Pickup-feed motor end cap',5.4,.8,(34,68.1,35),'Optical',1,'black',axis=(0,1,0),internal=True)
    m.cyl('SledMotorShaft','Pickup-feed motor shaft',.7,6.8,(34,43,35),'Optical',2,'metal',axis=(0,1,0),internal=True)
    worm=_helical_spring(1.55,1.35,5.4,.48).fuse(Part.makeCylinder(1.1,5.4))
    worm=worm.cut(Part.makeCylinder(.79,5.8,V(0,0,-.2)));worm.Placement=App.Placement(V(34,43.8,35),App.Rotation(V(0,0,1),V(0,1,0)))
    m.feature('SledWorm','Pickup-feed helical worm study',worm,'Optical',2,'white',True)
    gear=_gear(m,29,46.5,32,4.8,5.4,.85,24).fuse(_gear(m,29,46.5,34.4,2.3,2.9,1.1,16))
    gear=gear.fuse(Part.makeCylinder(1.4,3.5,V(29,46.5,32))).cut(Part.makeCylinder(.87,4,V(29,46.5,31.8)))
    m.feature('FeedReductionGear','Compound pickup reduction gear',gear,'Optical',2,'white',True)
    m.cyl('FeedGearAxle','Pickup reduction-gear axle',.70,4.5,(29,46.5,31.4),'Optical',1,'metal',internal=True)
    rack=Part.makeBox(1,43,.9,V(22,20,32))
    teeth=[Part.makeBox(.55,.6,.9,V(23,20+i*1.2,32)) for i in range(36)]
    rack=rack.multiFuse(teeth+[Part.makeBox(12.2,4,.75,V(10,37,32.05)),Part.makeBox(1.5,4,1.8,V(10,37,32.2))]).removeSplitter()
    m.feature('PickupRack','Pickup feed rack and carriage arm',rack,'Optical',2,'white',True)
    m.cut('PickupCarriage',m.rr(2,5,1,(10.8,39,33.4),.2),'Rack-arm attachment seat')
    m.box('OpticalMotorPCB','Optical motor terminal board',6,17,1.0,(44,56,35.5),'Optical',2,'pcb',.5,True)
    m.box('OpticalTerminal','Four-way motor connector',4.3,5,2,(44,60,36.7),'Optical',2,'white',.35,True)
    for i in range(4):m.box('OpticalTerminalPin'+str(i),'Optical motor connector pin',.32,2.8,.18,(42.65+i*.9,60,38.75),'Optical',2,'metal',.02,True)
    m.box('LaserWarningLabel','Optical pickup caution label',13,8,.035,(31,33,41.83),'Optical',3,'yellow',.15)
    m.label('LaserWarningText','LASER',1.25,(28.2,32.5,41.89),'Optical',3,'black')
    ribbon=_yz_strip(-6,12,[(32,33.2),(18,33.2),(18,12.6),(8,12.6),(8,12.4),(18.2,12.4),(18.2,33),(32,33)])
    m.feature('PickupFlex','Folded optical-pickup flexible circuit',ribbon,'Wiring',1,'flex',True)
    for i in range(10):
        trace=_yz_strip(-5+i*1.05,.55,[(32,33.225),(17.975,33.225),(17.975,12.625),(8,12.625),(8,12.647),(17.953,12.647),(17.953,33.247),(32,33.247)])
        m.feature('PickupFlexTrace'+str(i),'Optical flex conductor '+str(i+1),trace,'Wiring',1,'copper',True)
    for i,dx in enumerate([-.8,.8]):
        path=[V(34+dx,69.1,35),V(34+dx,74,35),V(56+dx,74,26),V(56+dx,31,12.5)]
        lead=_rounded_route(path,1.4,.45)
        m.feature('OpticalPowerLead'+str(i),'Optical motor power lead',lead,'Wiring',0,'white' if i==0 else 'psdark',True)
    m.profile['stages']=6
    m.checkpoint(6,'suspended_optical_drive_and_laser_pickup','建立三点橡胶悬挂光驱、主轴电机与夹盘球、双导轨激光头和透镜、进给电机/蜗杆/减速轮/齿条，以及光驱端子板、折叠软排线和独立铜导体。')


STAGES[6]=stage06


def stage07(m):
    import math
    from .clamshell import _replace,_move
    from .atari2600 import _rounded_route
    latch_space=m.rr(5.2,6.8,6.8,(65,-46,52.9),.45)
    for key in ['UpperHousing','DiscWell']:m.cut(key,latch_space,'Full latch-hook travel and seating relief')
    spring_bores=[]
    for i in range(3):
        a=2*math.pi*i/3;direction=V(math.cos(a),math.sin(a),0)
        seat=Part.makeCylinder(.22,.32,V(5.9*math.cos(a),4+5.9*math.sin(a),47.2),direction)
        _replace(m,'SpindleClipSpring'+str(i),seat)
        spring_bores.append(Part.makeCylinder(.32,1.1,V(5.75*math.cos(a),4+5.75*math.sin(a),47.2),direction))
    m.cut('SpindleCrown',spring_bores,'Retaining-ball spring-seat bores')
    _move(m,'SledMotor',(0,3,0));_move(m,'SledMotorCap',(0,3,0))
    _replace(m,'SledMotorShaft',Part.makeCylinder(.7,9.8,V(34,43,35),V(0,1,0)))
    # Turn the outer lead first, then keep distinct routes at the gear motor.
    for i,dx in enumerate([-.8,.8]):
        y=80-3*i;z=26+1.2*i
        path=[V(34+dx,72.1,35),V(34+dx,y,35),V(56+dx,y,z),V(56+dx,31,12.5)]
        lead=_rounded_route(path,1.4,.45);lead.check(True)
        _replace(m,'OpticalPowerLead'+str(i),lead)
    m.profile['stages']=7
    m.checkpoint(7,'latch_spindle_and_feed_clearance','依据整机布尔求交结果修正锁钩、三组夹盘球弹簧座、进给电机与减速轮的间隙；重新安排两根光驱电源线的先后转弯和高度，保持可核对的实体配合。')


STAGES[7]=stage07


def _ic_package(m,key,caption,role,x,y,w,h,pins,height=2.3,qfp=False,underside=False,angle=0):
    before=set(m.parts);z=10.4
    m.box(key,role+' package',w,h,height,(x,y,z),'Mainboard',0,'black',.4,True)
    pin_shapes=[];pad_shapes=[]
    sides=[0,90,180,270] if qfp else [0,180]
    per=pins//len(sides)
    for side_angle in sides:
        width,extent=(w,h/2) if side_angle in [0,180] else (h,w/2)
        for i in range(per):
            xx=(i-(per-1)/2)*(width-2)/(per-1)
            lead=_yz_strip(xx-.14,.28,[(extent+.02,11.55),(extent+.75,11.55),(extent+1.2,10.25),(extent+1.9,10.25),(extent+1.9,10.07),(extent+1.04,10.07),(extent+.60,11.37),(extent+.02,11.37)])
            lead.rotate(V(),V(0,0,1),side_angle);lead.translate(V(x,y,0));pin_shapes.append(lead)
            pad=Part.makeBox(.40,.78,.02,V(xx-.2,extent+1.10,10.025))
            pad.rotate(V(),V(0,0,1),side_angle);pad.translate(V(x,y,0));pad_shapes.append(pad)
    m.feature(key+'Leads',str(pins)+' formed package leads',Part.makeCompound(pin_shapes),'Mainboard',0,'metal',True)
    m.feature(key+'Pads',str(pins)+' package landing pads',Part.makeCompound(pad_shapes),'Mainboard',0,'gold',True)
    size=min(1.3,(w-2)/(len(caption)*.65))
    m.label(key+'Mark',caption,size,(x-w/2+1,y-.3,z+height+.025),'Mainboard',0,'white')
    m.cyl(key+'PinOne','Package pin-one mark',.42,.015,(x-w/2+1,y+h/2-1,z+height+.025),'Mainboard',0,'psdark',internal=True)
    if angle:
        turn=App.Placement(V(),App.Rotation(V(0,0,1),angle),V(x,y,9.2))
        for name in set(m.parts)-before:
            obj=m.parts[name];obj.Placement=turn.multiply(obj.Placement);obj.FlatPlacement=obj.Placement
    if underside:
        transform=App.Placement(V(),App.Rotation(V(1,0,0),180),V(x,y,9.2))
        for name in set(m.parts)-before:
            obj=m.parts[name];obj.Placement=transform.multiply(obj.Placement);obj.FlatPlacement=obj.Placement


def stage08(m):
    # The photo reference is a PU-7 1-655-322-13A board from the SCPH-1000 family.
    m.native('Mainboard','PU-7 two-sided main circuit board',210,174,2.4,1.6,(24,1,8.4),'Mainboard',-2,'pcb')
    mounts=[(-75,-80),(123,-80),(-75,81),(123,81),(53,-80),(123,15)]
    holes=[Part.makeCylinder(1.55,2.2,V(x,y,8.1)) for x,y in mounts]
    holes += [Part.makeCylinder(5.5,2.2,V(47,3,8.1)),m.rr(16,10,2.2,(-9,-85,8.1),1.3)]
    m.cut('Mainboard',holes,'PU-7 mounting holes, centre opening and front-edge notch')
    for i,(x,y) in enumerate(mounts):
        m.ring('BoardMountPad'+str(i),'Mainboard mounting ground land',2.8,1.7,.025,(x,y,10.025),'Mainboard',-1,'gold',internal=True)
    packages=[
        ('CPU','CXD8530BQ','R3000 CPU',103,-14,28,28,208,3.2,True),
        ('GPU','CXD8514Q','Early 160-pin GPU',61,-22,30,30,160,3.0,True),
        ('SPU','CXD2922Q','Sound processing unit',17,36,24,20,100,2.4,True),
        ('CDDecoder','CXD1199BQ','CD decoder and FIFO',-15,40,23,20,100,2.4,True),
        ('CDSignalDSP','CXD2516Q','CD digital signal processor',-49,24,24,20,100,2.4,True),
        ('BootROM','M534032C-02','Original forty-pin boot-ROM package',100,26,28,11,40,2.3,False),
        ('VRAM0','KM4216V256G-60','Dual-ported video RAM',20,-12,27,11,64,2.2,False),
        ('VRAM1','KM4216V256G-60','Dual-ported video RAM',20,-38,27,11,64,2.2,False),
        ('AudioRAM','KM416V256ALLT-8','Sound RAM',20,63,26,11,40,2.1,False),
        ('VideoDAC','CXD2923AR','Digital video RGB converter',-7,-26,11,11,64,1.8,True),
        ('VideoEncoder','CXA1645M','Composite and S-video encoder',-10,-50,18,8,24,2.0,False),
        ('AudioDAC','AK4309VM','Stereo audio digital-to-analogue converter',44,23,8.5,5.5,24,1.6,False),
    ]
    for data in packages:_ic_package(m,*data)
    for row,y in enumerate([-56,-70]):
        for col,x in enumerate([90,113]):
            _ic_package(m,'MainRAM'+str(row*2+col),'KM48V514BJ-6','Main DRAM',x,y,18,9,28,1.9)
    for data in [
        ('CDSubCPU','424660','CD controller MCU',-58,42,15,15,80,2.2,True),
        ('CDBuffer','HM62W256LFP-7T','CD buffer SRAM',-24,43,18,9,28,1.7,False),
        ('MotorDriver','BA6398FP','Four-channel motor driver',-30,-16,19,10,28,2.0,False),
        ('ServoAmplifier','CXA1782BR','Optical servo amplifier',-60,-14,10,10,48,1.8,True),
    ]:_ic_package(m,*data,underside=True,angle=90 if data[0]=='MotorDriver' else 0)
    m.label('MainboardRevision','PU-7  /  1-655-322-13A',3.1,(-61,-73,10.025),'Mainboard',-1,'white')
    m.label('MainboardStudyMark','SCPH-1000 STUDY',2.0,(-58,-78,10.025),'Mainboard',-1,'white')
    m.profile['stages']=8
    m.checkpoint(8,'pu7_processor_memory_and_cd_electronics','建立双面 PU-7 主板与安装孔，加入 208 脚 CPU、160 脚 GPU、SPU、四片主内存、双显存、40 脚 ROM、音频/视频转换和 CD 芯片；底面保留 CD 控制器、缓冲 RAM 与电机/伺服驱动，封装带独立引脚与焊盘。')


STAGES[8]=stage08


def _fit_package_marks(m):
    from .clamshell import _replace
    for key,body in list(m.parts.items()):
        if key+'Mark' not in m.parts or key+'Leads' not in m.parts:continue
        mark=m.parts[key+'Mark'];b=body.Shape.optimalBoundingBox(False,False);old=mark.Shape
        bb=old.optimalBoundingBox(False,False)
        scale=min(1,(b.XLength-1.6)/bb.XLength,(b.YLength-1.6)/bb.YLength)
        matrix=App.Matrix();matrix.A11=scale;matrix.A22=scale
        matrix.A14=b.Center.x-scale*bb.Center.x;matrix.A24=b.Center.y-scale*bb.Center.y
        fitted=old.transformGeometry(matrix);fb=fitted.optimalBoundingBox(False,False)
        assert abs(fb.Center.x-b.Center.x)<1e-6 and abs(fb.Center.y-b.Center.y)<1e-6
        assert abs(fb.ZMin-bb.ZMin)<1e-6 and abs(fb.ZMax-bb.ZMax)<1e-6
        _replace(m,key+'Mark',fitted)


def _smd_cap(m,key,x,y,r=3.1,h=4.2,mark='220'):
    m.box(key+'Base','Surface-mount capacitor base',2*r+.8,2*r+.8,.5,(x,y,10.2),'Mainboard',0,'black',.35,True)
    m.cyl(key+'Can','Electrolytic capacitor can',r,h,(x,y,10.78),'Mainboard',0,'metal',internal=True)
    m.cyl(key+'Top','Capacitor end seal',r-.12,.12,(x,y,10.82+h),'Mainboard',0,'metal',internal=True)
    terminals=Part.makeCompound([Part.makeBox(.55,1.7,.14,V(x+side*(r+.68)-.275,y-.85,10.035)) for side in [-1,1]])
    m.feature(key+'Terminals','Capacitor solder terminals',terminals,'Mainboard',0,'metal',True)
    if mark:m.label(key+'Mark',mark,.92,(x-1.25,y-.40,10.98+h),'Mainboard',0,'black')


def _passive(m,key,x,y,material='thermal'):
    m.box(key,'Chip resistor' if material=='black' else 'Ceramic decoupling capacitor',1.4,1.2,.6,(x,y,10.18),'Mainboard',0,material,.08,True)
    ends=Part.makeCompound([Part.makeBox(.38,1.2,.55,V(x+side*.91-.19,y-.6,10.2)) for side in [-1,1]])
    m.feature(key+'Ends','Surface-mount metal end caps',ends,'Mainboard',0,'metal',True)


def _fpc_socket(m,key,x,y,pins,side=1):
    shell=m.rr(14,5.2,3.2,(x,y,10.1),.55)
    shell=shell.cut(m.rr(12.8,4,.6,(x,y+side*2.3,12.2),.10))
    m.feature(key,'Flat flexible-circuit connector',shell,'Mainboard',0,'white',True)
    pitch=10.0/(pins-1)
    for i in range(pins):
        m.box(key+'Contact'+str(i),'FPC contact '+str(i+1),.45,2.4,.08,(x+(i-(pins-1)/2)*pitch,y+side*1.5,12.69),'Mainboard',0,'gold',.025,True)


def stage09(m):
    _fit_package_marks(m)
    for row,y in enumerate([63,75]):
        for col,x in enumerate([-67,-55,-39,-27]):_smd_cap(m,'RearFilter'+str(row*4+col),x,y)
    for i,(x,y) in enumerate([(36,39),(44,39),(36,47),(44,47),(53,48)]):_smd_cap(m,'AudioFilter'+str(i),x,y,1.65,3.0,mark='')
    locations=[(x,y) for x in [82,124] for y in [-26,-18,-10,-2]]
    locations += [(x,y) for x in [42,80] for y in [-32,-23,-14]]
    locations += [(x,y) for x in [-68,-31] for y in [17,25,33]]
    for i,(x,y) in enumerate(locations):_passive(m,'Decoupling'+str(i),x,y)
    for row,y in enumerate([50,61]):
        for col,x in enumerate([66,73,80,87,94,101,108,115]):_passive(m,'ParallelResistor'+str(row*8+col),x,y,'black')
    for key,x,y,caption in [('CPUClock',86,-38,'67.737'),('GPUClock',50,-46,'53.69')]:
        m.box(key+'Base','Clock-can insulating base',8.2,5.2,.4,(x,y,10.2),'Mainboard',0,'black',.5,True)
        m.box(key,'Crystal oscillator can',8,5,2.1,(x,y,10.68),'Mainboard',0,'metal',.8,True)
        m.label(key+'Mark',caption,.9,(x-2.7,y-.4,12.81),'Mainboard',0,'black')
    _fpc_socket(m,'PickupSocket',0,6,10)
    _fpc_socket(m,'FrontPortSocket',38,-53,12,side=-1)
    ribbon=_yz_strip(32,12,[(-65.4,16.25),(-60,16.25),(-60,12.6),(-54.5,12.6),(-54.5,12.4),(-60.2,12.4),(-60.2,16.05),(-65.4,16.05)])
    m.feature('FrontPortFlex','Shared front-port flexible circuit',ribbon,'Wiring',1,'flex',True)
    for i in range(12):
        trace=_yz_strip(32.75+i*.93,.5,[(-65.4,16.275),(-59.975,16.275),(-59.975,12.625),(-54.5,12.625),(-54.5,12.647),(-59.953,12.647),(-59.953,16.297),(-65.4,16.297)])
        m.feature('FrontPortFlexTrace'+str(i),'Front-port flex conductor '+str(i+1),trace,'Wiring',1,'copper',True)
    socket=m.rr(6.6,5,4,(56,29.5,10.1),.55)
    for i,dx in enumerate([-.8,.8]):
        y=80-3*i;z=26+1.2*i;axis=(V(56+dx,31,12.5)-V(56+dx,y,z)).normalize();end=V(56+dx,31,12.5)
        socket=socket.cut(Part.makeCylinder(.74,6,end-axis*3,axis))
        m.ring('OpticalPowerContact'+str(i),'Motor-power connector contact sleeve',.63,.49,1.2,tuple(end-axis*.3),'Mainboard',0,'metal',axis=tuple(axis),internal=True)
    m.feature('OpticalPowerSocket','Two-way motor-power connector',socket,'Mainboard',0,'white',True)
    m.profile['stages']=9
    m.checkpoint(9,'filters_discretes_and_flexible_circuit_headers','按功能区域加入滤波电容、去耦器件、并口电阻与时钟封装，补齐光驱和前接口排线连接座；按实际几何边界缩放、居中小型芯片标识。')


STAGES[9]=stage09


def _power_radial(m,key,x,y,r,h,holes):
    body=Part.makeCylinder(r,h,V(x,y,14.2));base=Part.makeCylinder(r-.15,.6,V(x,y,13.5))
    leads=[]
    for side in [-1,1]:
        xx=x+side*min(3.75,r*.42)
        bore=Part.makeCylinder(.58,1.3,V(xx,y,13.3));body=body.cut(bore);base=base.cut(bore)
        leads.append(Part.makeCylinder(.43,2.9,V(xx,y,11.4)))
        holes.append(Part.makeCylinder(.64,2.3,V(xx,y,11.3)))
    m.feature(key,'Power-board radial capacitor',body,'Power',1,'black',True)
    m.feature(key+'Seal','Radial capacitor base seal',base,'Power',1,'rubber',True)
    m.feature(key+'Leads','Radial capacitor formed leads',Part.makeCompound(leads),'Power',1,'metal',True)
    top=Part.makeCylinder(r-.15,.20,V(x,y,14.25+h))
    top=top.cut(Part.makeCompound([Part.makeBox(.22,1.2*r,.11,V(x-.11,y-.6*r,14.37+h)),Part.makeBox(1.2*r,.22,.11,V(x-.6*r,y-.11,14.37+h))]))
    m.feature(key+'Vent','Scored capacitor end cover',top,'Power',1,'metal',True)


def _power_control_ic(m,key,x,y,pins,holes):
    m.box(key,'Power-control package study',5.2,4.2,1.8,(x,y,13.8),'Power',1,'black',.35,True)
    feet=[]
    for side in [-1,1]:
        for i in range(pins//2):
            xx=x+(i-(pins//2-1)/2)*1.05;yy=y+side*3.1
            foot=Part.makeBox(.35,.35,2.8,V(xx-.175,yy-.175,11.4))
            run=Part.makeBox(.35,1.0,.24,V(xx-.175,min(yy,y+side*2.2),13.97))
            feet.append(foot.fuse(run));holes.append(Part.makeCylinder(.44,2.3,V(xx,yy,11.3)))
    m.feature(key+'Pins','Power-control package leads',Part.makeCompound(feet),'Power',1,'metal',True)


def stage10(m):
    from .atari2600 import _rounded_route
    m.colors.update({'phenolic':(.61,.41,.16),'glass':(.58,.72,.73),'coil':(.81,.43,.18)})
    m.native('PowerBoard','Separate Japanese power-supply PCB',44,163,1.5,1.6,(-107,.5,11.8),'Power',-1,'phenolic')
    holes=[]
    # Extend the two already-modelled AC contacts to their through-board tails.
    inlet_bores=[]
    for i,dx in enumerate([-4.05,4.05]):
        xx=-100+dx
        tail=Part.makeBox(.75,8,.75,V(xx-.375,77.5,23.625)).fuse(Part.makeBox(.75,.75,12.7,V(xx-.375,77.5,11.4)))
        _add_shape(m,'ACPin'+str(i),tail,'Bent AC contact tail')
        inlet_bores.append(Part.makeBox(1.25,5,1.25,V(xx-.625,80.8,23.375)))
        holes.append(Part.makeCylinder(.72,2.3,V(xx,77.875,11.3)))
    m.cut('ACInlet',inlet_bores,'Rear AC contact-tail exits')
    m.ring('InputFuseGlass','Input fuse glass tube',2.1,1.75,17.8,(-122,56.1,17),'Power',1,'glass',axis=(0,1,0),internal=True)
    for i,y in enumerate([53.8,74]):m.cyl('InputFuseCap'+str(i),'Input fuse metal end cap',2.15,2.2,(-122,y,17),'Power',1,'metal',axis=(0,1,0),internal=True)
    m.cyl('InputFuseElement','Fuse filament study',.09,17.9,(-122,56.05,17),'Power',1,'metal',axis=(0,1,0),internal=True)
    for i,y in enumerate([54.75,75.25]):
        cradle=Part.makeCylinder(2.7,.9,V(-122,y-.45,17),V(0,1,0)).cut(Part.makeCylinder(2.2,1.1,V(-122,y-.55,17),V(0,1,0)))
        cradle=cradle.common(Part.makeBox(8,2,5,V(-126,y-1,12)))
        clip=cradle.fuse(Part.makeBox(.5,.5,3,V(-122.25,y-.25,11.4)))
        m.feature('FuseClip'+str(i),'Fuse spring cradle and solder leg',clip,'Power',1,'metal',True)
        holes.append(Part.makeCylinder(.48,2.3,V(-122,y,11.3)))
    # The photographed input choke uses two bobbins on a rectangular ferrite core.
    cx,cy=-104,58
    core_shape=m.rr(14,18,5,(cx,cy,14.5),.35).cut(m.rr(10,14,5.4,(cx,cy,14.3),.15))
    m.feature('InputChokeCore','Rectangular common-mode choke ferrite',core_shape,'Power',1,'psdark',True)
    for bank,sign in enumerate([-1,1]):
        yy=cy+sign*8
        bobbin=m.rr(9,2.4,5.4,(cx,yy,14.3),.08).cut(m.rr(9.4,2.1,5.1,(cx,yy,14.45),.04))
        m.feature('InputChokeBobbin'+str(bank),'Input-filter insulating bobbin',bobbin,'Power',1,'white',True)
        turns=[]
        for xx in [-3.6,-1.8,0,1.8,3.6]:
            points=[V(cx+xx,yy,14),V(cx+xx,yy-1.6,14),V(cx+xx,yy-1.6,20),V(cx+xx,yy+1.6,20),V(cx+xx,yy+1.6,14),V(cx+xx,yy,14)]
            turns.append(_rounded_route(points,.5,.25))
        m.feature('InputChokeWinding'+str(bank),'Common-mode winding study',Part.makeCompound(turns),'Power',1,'copper' if bank==0 else 'coil',True)
    _power_radial(m,'PrimaryBulkCap',-108,32,9,24,holes)
    m.label('PrimaryBulkCapRating','150 uF',1.3,(-112,30,38.50),'Power',1,'black')
    for i,(x,y) in enumerate([(-94,70),(-94,59),(-120,41),(-120,29)]):
        m.cyl('Rectifier'+str(i),'Input rectifier diode',1.0,4,(x,y-2,15.5),'Power',1,'black',axis=(0,1,0),internal=True)
        m.ring('RectifierBand'+str(i),'Diode polarity band',1.05,1.015,.45,(x,y-1.55,15.5),'Power',1,'metal',axis=(0,1,0),internal=True)
        legs=[]
        for side in [-1,1]:
            yy=y+side*5.2
            horizontal=Part.makeCylinder(.26,3.1,V(x,min(yy,y+side*2.1),15.5),V(0,1,0))
            vertical=Part.makeCylinder(.26,4.2,V(x,yy,11.4));legs.append(horizontal.fuse(vertical))
            holes.append(Part.makeCylinder(.45,2.3,V(x,yy,11.3)))
        m.feature('RectifierLeads'+str(i),'Rectifier bent leads',Part.makeCompound(legs),'Power',1,'metal',True)
    # Ferrite, bobbin and the two winding packs remain separate inspectable shapes.
    tx,ty=-108,0
    ferrite=m.rr(27,26,2,(tx,ty,14.5),.5)
    ferrite=ferrite.fuse(m.rr(6,16,19,(tx,ty,16.5),.25))
    for side in [-1,1]:ferrite=ferrite.fuse(m.rr(4,16,19,(tx+side*11.5,ty,16.5),.25))
    ferrite=ferrite.fuse(m.rr(27,26,2,(tx,ty,35.5),.5)).removeSplitter()
    m.feature('TransformerCore','Closed transformer ferrite core',ferrite,'Power',1,'psdark',True)
    bobbin=m.rr(10,20,18.4,(tx,ty,16.8),.2).cut(m.rr(6.6,16.6,19,(tx,ty,16.5),.1))
    for z in [16.7,25,34.2]:
        flange=m.rr(18.8,24.8,.6,(tx,ty,z),.25).cut(m.rr(6.6,16.6,.9,(tx,ty,z-.1),.1));bobbin=bobbin.fuse(flange)
    m.feature('TransformerBobbin','Three-flange transformer bobbin',bobbin.removeSplitter(),'Power',1,'white',True)
    for key,z,mat in [('Primary',17.4,'copper'),('Secondary',26,'coil')]:
        winding=m.rr(18,24,7.2,(tx,ty,z),.5).cut(m.rr(10.6,20.6,7.6,(tx,ty,z-.2),.3))
        m.feature('Transformer'+key,'Transformer '+key.lower()+' winding pack',winding,'Power',1,mat,True)
    points=[(-14.2,13.8),(-14.2,38.2),(14.2,38.2),(14.2,13.8),(13.8,13.8),(13.8,37.8),(-13.8,37.8),(-13.8,13.8)]
    wire=Part.makePolygon([V(tx+x,-1.15,z) for x,z in points]+[V(tx+points[0][0],-1.15,points[0][1])])
    m.feature('TransformerClip','Transformer retaining strap',Part.Face(Part.Wire(wire.Edges)).extrude(V(0,2.3,0)),'Power',1,'metal',True)
    m.label('TransformerMark','T001',2,(-114,4,37.53),'Power',1,'white')
    for i,(x,y,r,h) in enumerate([(-121,-32,4,12),(-108,-39,5,14),(-95,-34,4,12),(-121,-48,3,8),(-94,-49,3.5,10)]):_power_radial(m,'OutputCap'+str(i),x,y,r,h,holes)
    _power_control_ic(m,'PowerControlIC',-122,-64,8,holes)
    _power_control_ic(m,'FeedbackOptocoupler',-94,-20,4,holes)
    # A small power transistor and folded radiator correspond to the board photo.
    front=g.rotation((0,-1,0),(0,0,1))
    transistor=m.rr(9,10,3,(-118,20.8,22.5),.5,front)
    leads=[]
    for dx in [-2.2,0,2.2]:
        xx=-118+dx;bore=Part.makeCylinder(.57,1.2,V(xx,18.5,17.2));transistor=transistor.cut(bore)
        leads.append(Part.makeBox(.5,.5,6.6,V(xx-.25,18.25,11.4)));holes.append(Part.makeCylinder(.5,2.3,V(xx,18.5,11.3)))
    m.feature('PowerTransistor','Power transistor package study',transistor,'Power',1,'black',True)
    m.feature('PowerTransistorLeads','Power transistor leads',Part.makeCompound(leads),'Power',1,'metal',True)
    tab=Part.makeBox(9,.5,14,V(-122.5,21,18)).cut(Part.makeCylinder(.85,2,V(-118,20.5,30),V(0,1,0)))
    radiator=Part.makeBox(14,.6,21,V(-125,21.6,14)).fuse(Part.makeBox(14,8,.6,V(-125,13.8,14)))
    radiator=radiator.cut(Part.makeCylinder(.85,2,V(-118,21,30),V(0,1,0)))
    m.feature('PowerTransistorTab','Power transistor heat-transfer tab',tab,'Power',1,'metal',True)
    m.feature('PowerRadiator','Folded power-transistor radiator',radiator,'Power',1,'metal',True)
    screw=Part.makeCylinder(1.4,.6,V(-118,17.35,30),V(0,1,0)).fuse(Part.makeCylinder(.65,4.9,V(-118,17.9,30),V(0,1,0)))
    screw=screw.cut(Part.makeCompound([Part.makeBox(.30,.35,1.8,V(-118.15,17.3,29.1)),Part.makeBox(1.8,.35,.3,V(-118.9,17.3,29.85))]))
    m.feature('PowerRadiatorScrew','Power-transistor retaining screw',screw,'Power',1,'metal',True)
    m.cut('PowerBoard',holes,'Power-board through-hole lead clearances')
    m.label('PowerBoardMark','PSU STUDY',1.2,(-127,-15,13.425),'Power',-1,'white')
    m.profile['stages']=10
    m.checkpoint(10,'separate_power_supply_and_filtering','建立日版独立电源板、输入保险管、矩形磁芯双绕组滤波器、整流器、大电容、分体变压器、输出滤波与功率器件；为引脚和 AC 接点预留穿板、穿壳孔，电气布局明确为学习示意。')


STAGES[10]=stage10


def stage11(m):
    from .atari2600 import _rounded_route
    m.colors['lightpipe']=(.40,.68,.46)
    holes=[]
    switch=m.rr(12,12,12,(-110,-58,13.8),.8)
    pins=[]
    for x in [-115,-105]:
        for y in [-63,-53]:
            switch=switch.cut(Part.makeCylinder(.61,1.2,V(x,y,13.5)))
            pins.append(Part.makeBox(.55,.55,3,V(x-.275,y-.275,11.4)))
            holes.append(Part.makeCylinder(.61,2.3,V(x,y,11.3)))
    m.feature('PowerSwitch','Latching power-switch housing',switch,'Power',1,'black',True)
    m.feature('PowerSwitchPins','Power-switch through-board terminals',Part.makeCompound(pins),'Power',1,'metal',True)
    m.cyl('PowerSwitchPusher','Power-switch actuator',2.3,5.1,(-110,-58,25.9),'Controls',3,'white',internal=True)
    m.cyl('PowerButtonStem','Long power-button transmission stem',2.0,23.65,(-110,-58,31.1),'Controls',4,'psgrey',internal=True)
    m.box('ResetSwitch','Reset-switch package study',5.5,5.5,4,(-110,-24,13.8),'Power',1,'black',.4,True)
    m.cyl('ResetPusher','Reset-switch actuator',1.3,.7,(-110,-24,17.9),'Controls',3,'white',internal=True)
    m.cyl('ResetStem','Reset-button transmission stem',1.1,36.0,(-110,-24,18.7),'Controls',4,'psgrey',internal=True)
    m.cyl('PowerLEDBase','Power LED insulating base',2.8,3.3,(-110,-76,13.5),'Power',1,'black',internal=True)
    led=Part.makeSphere(2.8,V(-110,-76,16.9)).common(Part.makeCylinder(2.75,3.0,V(-110,-76,16.9)))
    m.feature('PowerLED','Power-indicator LED lens',led,'Power',1,'psgreen',True)
    light=Part.makeBox(1.8,3,36,V(-110.9,-90,20)).fuse(Part.makeBox(1.8,14,1.8,V(-110.9,-89.25,20)))
    m.feature('PowerLightGuide','Bent power-indicator light guide',light,'Controls',4,'lightpipe',True)
    # Seven conductors are retained for this early power-board family. The
    # colours distinguish study geometry, not an electrical wiring prescription.
    psu=m.rr(10,16,6.3,(-91,-65,13.7),.65).cut(Part.makeBox(8,14.8,3.2,V(-93,-72.4,15.4)))
    board=m.rr(6,17,4,(-72,-65,10.1),.6)
    for i in range(7):
        y=-71+2*i
        board=board.cut(Part.makeCylinder(.74,8,V(-76,y,12.5),V(1,0,0)))
        m.ring('PSUOutputContact'+str(i),'Early PSU connector contact '+str(i+1),.63,.48,6.2,(-92,y,17),'Power',1,'metal',axis=(1,0,0),internal=True)
        m.ring('MainPowerContact'+str(i),'Mainboard power connector contact '+str(i+1),.63,.49,3.5,(-74.6,y,12.5),'Mainboard',0,'metal',axis=(1,0,0),internal=True)
        route=[V(-85.7,y,17),V(-82.8,y,17),V(-79,y,12.5),V(-74,y,12.5),V(-71.5,y,12.5)]
        wire=_rounded_route(route,.65,.43)
        m.feature('PowerHarness'+str(i),'Seven-core power/reset harness conductor '+str(i+1),wire,'Wiring',0,['white','psdark','coil','psgrey','white','red','psdark'][i],True)
    m.feature('PSUOutputConnector','Seven-position PSU connector',psu,'Power',1,'white',True)
    m.feature('MainPowerConnector','Seven-position mainboard power connector',board,'Mainboard',0,'white',True)
    m.cut('PowerBoard',holes,'Power-switch solder-terminal bores')
    m.profile['stages']=11
    m.checkpoint(11,'seven_wire_supply_and_system_actuators','补齐早期七芯电源/复位线束和两端插座、POWER/RESET 传动杆、功率开关及指示灯导光件；线束按固定间距分开布置，颜色仅用于区分学习模型。')


STAGES[11]=stage11


def stage12(m):
    from .clamshell import _replace
    from .psp import _polygon
    import math
    m.cut('UpperHousing',m.rr(2.2,3.4,1.1,(-110,-88.5,54.5),.2),'Light-guide passage through the roof')
    m.cut('PowerRadiator',m.rr(6,1.3,1.1,(-118,18.5,13.8),.2),'Power-device lead clearance in the radiator foot')
    m.box('LowerShield','Lower mainboard shield',204,169,.6,(24,1,4.3),'Shield',-4,'metal',1.5,True)
    m.box('PowerInsulator','Power-board insulating sheet',43,161,.45,(-107,.5,10.7),'Power',-2,'thermal',1.3,True)
    shield=m.rr(207,171,.7,(24,1,22.3),2.0)
    clearances=[m.rr(134,20,1.4,(0,-84,22),1.0),m.rr(122,14,1.4,(0,87.8,22),1.0),m.rr(64.5,11,1.4,(100,88,22),1.0),m.rr(13.4,1.2,1.4,(0,18.08,22),.25),m.rr(8,14,1.4,(56,65,22),.7)]
    shield=shield.cut(Part.makeCompound(clearances))
    m.feature('MainShield','Raised mainboard shield with interface and cable clearances',shield,'Shield',2,'metal',True)
    guard=Part.makeBox(.6,170,21,V(-82,-84,4.5)).cut(Part.makeBox(1.2,18,7,V(-82.3,-74,11.5)))
    m.feature('PowerGuard','Power-board side shield and harness aperture',guard,'Shield',1,'metal',True)
    all_mounts=[(-75,-80),(123,-80),(-75,81),(123,81),(53,-80),(123,15),(78,75)]
    tall=[p for p in all_mounts if p!=(53,-80)]
    m.cut('Mainboard',Part.makeCylinder(1.55,2.3,V(78,75,8.1)),'Additional shield mounting hole')
    m.ring('BoardMountPad6','Shield fixing ground land',2.8,1.7,.025,(78,75,10.025),'Mainboard',-1,'gold',internal=True)
    lower_holes=[];upper_holes=[]
    for i,(x,y) in enumerate(all_mounts):
        m.ring('BoardPedestal'+str(i),'Mainboard lower insulating pedestal',3.0,1.0,5.0,(x,y,3.3),'Internal',-3,'psgrey',internal=True)
        lower_holes.append(Part.makeCylinder(3.25,1.2,V(x,y,4.0)))
        if (x,y) in tall:
            radius=1.8 if (x,y)==(123,81) else 2.6
            m.ring('ShieldSpacer'+str(i),'Mainboard shield spacer',radius,.9,11.8,(x,y,10.2),'Internal',1,'metal',internal=True)
            m.ring('ShieldWasher'+str(i),'Shield screw washer',1.9,.85,.15,(x,y,23.03),'Internal',2,'metal',internal=True)
            m.screw('ShieldScrew'+str(i),(x,y,23.55),'Internal',2,length=19,radius=1.7,axis=(0,0,-1))
            upper_holes.append(Part.makeCylinder(1.15,1.4,V(x,y,22)))
        else:
            m.ring('FrontBoardWasher','Low front mounting washer',2.3,.85,.10,(x,y,10.08),'Internal',-1,'metal',internal=True)
            m.screw('FrontBoardScrew',(x,y,10.6),'Internal',-1,length=6,radius=1.7,axis=(0,0,-1))
    for i,(x,y) in enumerate([(-44,-4),(44,8),(-42,62)]):
        _add_shape(m,'OpticalPeg'+str(i),Part.makeCylinder(1.0,1.35,V(x,y,21.7)),'Optical support stud through the shield')
        upper_holes.append(Part.makeCylinder(1.2,1.4,V(x,y,22)))
        pts=[(x+2.05*math.cos(math.pi*j/3),y+2.05*math.sin(math.pi*j/3)) for j in range(6)]
        nut=_polygon(pts,21.3,.8).cut(Part.makeCylinder(1.12,1.2,V(x,y,21.1)))
        m.feature('OpticalPegNut'+str(i),'Optical support retaining nut',nut,'Internal',1,'metal',True)
    m.cut('LowerShield',lower_holes+[Part.makeCylinder(5.8,1.2,V(47,3,4.0))],'Pedestal and centre clearances in the lower shield')
    m.cut('MainShield',upper_holes,'Shield fixing and optical stud holes')
    # The separate front interface cover has five retaining positions.
    front=m.rr(125,16,.6,(0,-82.5,42.0),1.0)
    front=front.fuse(Part.makeBox(.6,16,25.6,V(-62.5,-90.5,17))).fuse(Part.makeBox(.6,16,25.6,V(61.9,-90.5,17)))
    front_mounts=[(-63.5,-86.5),(-63.5,-77),(63.5,-86.5),(63.5,-77),(0,-80)]
    front_holes=[];post_clear=[]
    _add_shape(m,'LowerHousing',Part.makeCompound([Part.makeCylinder(1.8,38.8,V(x,y,3.0)) for x,y in front_mounts]),'Front connector-cover fixing posts')
    m.cut('LowerHousing',[Part.makeCylinder(.85,38,V(x,y,4.0)) for x,y in front_mounts],'Front cover screw-pilot holes')
    for i,(x,y) in enumerate(front_mounts):
        front=front.fuse(Part.makeCylinder(2.3,.6,V(x,y,42)))
        front_holes.append(Part.makeCylinder(.95,1.1,V(x,y,41.8)))
        post_clear.append(Part.makeCylinder(2.05,20,V(x,y,3.8)))
        m.ring('FrontShieldWasher'+str(i),'Front-cover screw washer',1.8,.85,.12,(x,y,42.63),'Internal',3,'metal',internal=True)
        m.screw('FrontShieldScrew'+str(i),(x,y,43.15),'Internal',3,length=38,radius=1.6,axis=(0,0,-1))
    front=front.cut(Part.makeCompound(front_holes))
    m.feature('FrontIOShield','Folded controller and memory-card shielding cover',front,'Shield',3,'metal',True)
    for key in ['Mainboard','LowerShield','FrontPortPCB']:m.cut(key,post_clear,'Front connector-cover post clearances')
    m.cut('DiscWell',m.rr(126.2,16.8,1,(0,-82.5,41.8),1.0),'Front interface-cover seat under the disc well')
    power_mounts=[(-125,-76),(-89,-76),(-125,78),(-89,78)]
    board_holes=[];insulator_holes=[]
    for i,(x,y) in enumerate(power_mounts):
        m.ring('PowerPedestal'+str(i),'Power-board insulating support',2.4,.95,8.2,(x,y,3.3),'Internal',-2,'psgrey',internal=True)
        board_holes.append(Part.makeCylinder(1.15,2.3,V(x,y,11.5)))
        insulator_holes.append(Part.makeCylinder(2.65,1.1,V(x,y,10.4)))
        if y>0:
            m.ring('PowerWasher'+str(i),'Power-board retaining washer',2,.85,.1,(x,y,13.45),'Internal',1,'metal',internal=True)
            m.screw('PowerScrew'+str(i),(x,y,13.95),'Internal',1,length=9,radius=1.6,axis=(0,0,-1))
    m.cut('PowerBoard',board_holes,'Power-board support and retaining holes')
    m.cut('PowerInsulator',insulator_holes,'Power-board pedestal clearance in the insulation')
    for i,(x,y) in enumerate([(-112,-73),(112,-73),(-112,73),(112,73)]):
        _replace(m,'Foot'+str(i),m.rr(18,11.2,1.2,(x,y,0),1.0))
        collar=m.rr(22,15.2,.9,(x,y,.7),1.3).cut(m.rr(18.4,11.6,1.1,(x,y,.6),1.1))
        _add_shape(m,'LowerHousing',collar,'Raised rectangular foot surround')
    m.profile['envelope_groups']=list(dict.fromkeys(m.profile['envelope_groups']+['Internal']))
    m.profile['stages']=12
    m.checkpoint(12,'shield_layers_supports_and_rectangular_feet','补齐上下主板屏蔽、电源隔板、前接口折弯罩与独立绝缘支撑，建立六处主罩固定、五处前罩固定和两处电源固定；为线束、排线和支柱开孔，并按参考改为矩形支脚。')


STAGES[12]=stage12


def stage13(m):
    # The five front-cover posts also need relief in the folded side walls.
    front_mounts=[(-63.5,-86.5),(-63.5,-77),(63.5,-86.5),(63.5,-77),(0,-80)]
    m.cut('FrontIOShield',[Part.makeCylinder(2.05,25,V(x,y,16.8)) for x,y in front_mounts],'Side-wall clearance around front-cover posts')
    # Six asymmetric case positions follow the bottom-view reference. Their
    # study coordinates, diameters and screw lengths are intentionally approximate.
    case_mounts=[(-126,87),(128,68),(128,27),(-126,-85),(0,-88),(126,-85)]
    upper_clear=[];lower_clear=[]
    reverse=g.rotation((0,0,-1),(0,1,0))
    _add_shape(m,'UpperHousing',Part.makeCompound([Part.makeCylinder(2.4,49.15,V(x,y,5.8)) for x,y in case_mounts]),'Upper enclosure screw bosses')
    m.cut('UpperHousing',[Part.makeCylinder(.92,14.4,V(x,y,5.6)) for x,y in case_mounts],'Upper enclosure screw-pilot bores')
    _add_shape(m,'LowerHousing',Part.makeCompound([Part.makeCylinder(2.8,4.2,V(x,y,1.4)) for x,y in case_mounts]),'Recessed case-screw seats')
    case_bores=[shape for x,y in case_mounts for shape in [Part.makeCylinder(.98,5.2,V(x,y,1.2)),Part.makeCylinder(2.2,2,V(x,y,1.2))]]
    m.cut('LowerHousing',case_bores,'Case-screw shaft bores and recessed head seats')
    for i,(x,y) in enumerate(case_mounts):
        m.screw('CaseScrew'+str(i),(x,y,2.6),'Internal',-6,length=12,radius=1.75)
        screw=m.parts['CaseScrew'+str(i)];screw.MaterialDescription='black';g.appearance(screw,m.colors['black'])
        m.label('CaseScrewArrow'+str(i),'↑',3.0,(x+1.0,y-6,1.35),'Body',-6,'psdark',rotation=reverse)
        upper_clear.append(Part.makeCylinder(2.7,24,V(x,y,3.8)))
        lower_clear.append(Part.makeCylinder(3.1,1.2,V(x,y,4.0)))
    for key in ['Mainboard','MainShield','FrontPortPCB','FrontIOShield','PowerBoard','PowerInsulator']:m.cut(key,upper_clear,'Case-boss clearance through the installed layer')
    m.cut('LowerShield',lower_clear,'Case-screw seat clearance in the lower shield')
    vents=[m.rr(20.5,1.7,6,(x,-21+6*j,1),.65) for x in [70,104] for j in range(11)]
    vents += [m.rr(14.5,1.7,6,(x,-50+6*j,1),.65) for x in [-18,-43] for j in range(6)]
    for key in ['LowerHousing','LowerShield']:m.cut(key,vents,'Two large and two small underside ventilation banks')
    m.box('BottomLabel','Original-family underside label study',80,34,.06,(0,55,1.36),'Body',-6,'black',1.0,orient=reverse)
    m.label('BottomSony','SONY',4.2,(30,63,1.275),'Body',-6,'white',rotation=reverse)
    m.label('BottomModel','SCPH-1000',3.0,(30,54,1.275),'Body',-6,'white',rotation=reverse)
    m.label('BottomStudy','OPEN CONSOLE CAD',1.65,(32,43,1.275),'Body',-6,'white',rotation=reverse)
    # The opened original lid has one toothed hinge/rotary-resistance mechanism;
    # the other side is a plain retained pivot, without a second return spring.
    spring=m.parts.pop('LidTorsionSpring0');spring.PhysicalPart=False;spring.Visibility=False
    sector=_gear(m,0,0,0,5.4,6.0,1.8,24)
    sector.Placement=App.Placement(V(49.9,78,51.8),App.Rotation(V(0,0,1),V(1,0,0)))
    sector=sector.common(Part.makeBox(4,16,9,V(49,70,44.5)))
    sector=sector.fuse(Part.makeCylinder(1.4,2.8,V(48.9,78,51.8),V(1,0,0)))
    _add_shape(m,'DiscLid',sector,'Integral toothed lid hinge sector')
    m.cut('DiscLid',Part.makeCylinder(1.03,5,V(48,78,51.8),V(1,0,0)),'Hinge-sector pivot bore')
    m.cut('HingeBracket1',Part.makeCylinder(6.35,2.6,V(49.5,78,51.8),V(1,0,0)),'Hinge-sector running clearance')
    _add_shape(m,'HingeBracket1',m.rr(6,9,1.8,(55,78,40),.4),'Rotary resistance-unit mounting shelf')
    m.cut('HingeBracket1',[Part.makeCylinder(.9,4,V(51.8,78,43.7),V(1,0,0)),Part.makeCylinder(3,3.3,V(54.2,78,43.7),V(1,0,0))],'Resistance-unit shaft and housing seat')
    pinion=_gear(m,0,0,0,1.55,2.0,1.7,12)
    pinion.Placement=App.Placement(V(50,78,43.7),App.Rotation(V(0,0,1),V(1,0,0)))
    pinion=pinion.fuse(Part.makeCylinder(.65,3.4,V(51.6,78,43.7),V(1,0,0)))
    m.feature('LidResistancePinion','Lid resistance-unit pinion and spindle',pinion,'Optical',6,'black',True)
    m.ring('LidResistanceUnit','Rotary lid-resistance housing study',2.8,.9,2.7,(54.4,78,43.7),'Optical',5,'black',axis=(1,0,0),internal=True)
    m.profile['stages']=13
    m.checkpoint(13,'case_fixings_underside_and_toothed_lid_hinge','根据初代底面补齐六处非对称机壳固定、沉孔、箭头、通风槽和学习铭牌；增加单侧盖板齿扇及旋转阻力单元，并修正前接口罩与固定支柱的避让。')


STAGES[13]=stage13


def stage14(m):
    m.cut('MainShield',m.rr(134,8,1.4,(0,-70.5,22),.7),'Extended front-terminal and solder-leg clearance')
    m.cut('DiscWell',Part.makeCylinder(2.1,1,V(0,-80,42.5)),'Centre front-cover screw-head pocket')
    case_mounts=[(-126,87),(128,68),(128,27),(-126,-85),(0,-88),(126,-85)]
    m.cut('FrontIOShield',[Part.makeCylinder(2.7,46,V(x,y,3.8)) for x,y in case_mounts],'Full-height case-boss clearance through the front shield')
    m.profile['stages']=14
    m.checkpoint(14,'front_terminal_and_case_boss_fit','根据装配求交扩大前接口焊接脚的屏蔽开口，增加中央前罩螺钉沉槽，并将机壳固定柱的前罩避让延伸到完整高度。')


STAGES[14]=stage14


def stage15(m):
    m.cut('HingeBracket1',Part.makeCylinder(2.25,2.2,V(49.7,78,43.7),V(1,0,0)),'Rotary pinion running pocket')
    m.profile['stages']=15
    m.checkpoint(15,'rotary_pinion_running_clearance','为单侧开盖阻力齿轮增加完整转动口袋，清除小齿轮与固定铰链座底部的接触体积。')


STAGES[15]=stage15


def _controller_point(x,y,z):
    return V(x,y-240,z)


def _controller_outline(inset=0):
    # Photographic outline of the compact original digital controller. These
    # are study control points, not measured production coordinates.
    right=[(0,27),(24,27),(27,31),(45,32),(59,25),(67,12),(69,-3),(65,-19),(67,-39),(60,-51),(50,-51),(42,-43),(29,-23),(23,-17),(0,-16)]
    points=right+[(-x,y) for x,y in reversed(right[1:-1])]
    if not inset:return points
    shifted=[]
    for i,(x,y) in enumerate(points):
        previous=V(*points[i-1],0);here=V(x,y,0);following=V(*points[(i+1)%len(points)],0)
        a=(here-previous).normalize();b=(following-here).normalize()
        na=V(a.y,-a.x,0);nb=V(b.y,-b.x,0);direction=(na+nb).normalize()
        point=here+direction*(inset/direction.dot(na));shifted.append((point.x,point.y))
    return shifted


def _controller_loft(m,key,profiles):
    sketches=[]
    for i,(sx,sy,z) in enumerate(profiles):
        sk=m.doc.addObject('Sketcher::SketchObject',key+'Profile'+str(i));sk.Label=key+' · editable closed outline '+str(i+1)
        for curve in _controller_profile_curves(sx,sy,1.2 if 'InnerLoft' in key else 0):sk.addGeometry(curve,False)
        sk.Placement=App.Placement(_controller_point(0,0,z),App.Rotation())
        m.group('Construction').addObject(sk);sketches.append(sk)
    loft=m.doc.addObject('Part::Loft',key);loft.Sections=sketches;loft.Solid=True;loft.Ruled=False;loft.Closed=False;loft.MaxDegree=3
    m.doc.recompute();assert not loft.Shape.isNull() and loft.Shape.isValid() and len(loft.Shape.Solids)==1 and loft.Shape.Volume>0,key
    loft.Shape.check(True)
    m.group('Construction').addObject(loft)
    for sk in sketches:sk.Visibility=False
    loft.Visibility=False
    return loft


def _controller_profile_curves(sx,sy,inset):
    # A symmetric chain with explicit horizontal bridge segments. Local tangent
    # directions avoid the long-span oscillation of a single interpolating curve.
    points=[(0,27),(24,27),(31,31),(47,31),(68,7),(64,-19),(66,-39),(54,-52),(42,-43),(27,-20),(20,-16),(0,-16)]
    tangents=[(1,0),(1,0),(1,0),(1,-.25),(0,-1),(0,-1),(-.3,-1),(-1,0),(-.6,.8),(-.7,.7),(-1,0),(-1,0)]
    nodes=[V(x,y,0) for x,y in points];directions=[V(x,y,0).normalize() for x,y in tangents]
    lengths=[]
    for i,p in enumerate(nodes):
        before=(p-nodes[i-1]).Length if i else (nodes[1]-p).Length
        after=(nodes[i+1]-p).Length if i+1<len(nodes) else before
        lengths.append(.32*min(before,after))
    segments=[]
    for i in range(len(nodes)-1):
        a,b=nodes[i],nodes[i+1];ta,tb=directions[i],directions[i+1]
        na,nb=V(ta.y,-ta.x,0)*inset,V(tb.y,-tb.x,0)*inset
        poles=[a+na,a+ta*lengths[i]+na,b-tb*lengths[i+1]+nb,b+nb]
        segments.append(poles)
    segments += [[V(-p.x,p.y,0) for p in reversed(poles)] for poles in reversed(segments)]
    curves=[]
    for poles in segments:
        bezier=Part.BezierCurve();bezier.setPoles([V(p.x*sx,p.y*sy,0) for p in poles]);curves.append(bezier.toBSpline())
    return curves


def _controller_shell(m,key,outer,inner,layer):
    outside=_controller_loft(m,key+'OuterLoft',outer);inside=_controller_loft(m,key+'InnerLoft',inner)
    shell=m.doc.addObject('Part::Cut',key);shell.Base=outside;shell.Tool=inside;shell.Refine=True;shell.Label=key+' · hollow ergonomic shell'
    m.doc.recompute();assert not shell.Shape.isNull() and shell.Shape.isValid() and len(shell.Shape.Solids)==1 and shell.Shape.Volume>0,key
    shell.Shape.check(True)
    outside.Visibility=False;inside.Visibility=False
    return m.register(shell,key,'Controller',layer,'psgrey')


def stage16(m):
    _controller_shell(m,'CtrlBack',[(.89,.90,1),(.96,.96,4),(1,1,11),(1,1,17.8)],[(.83,.84,3.3),(.92,.92,6),(.967,.966,12),(.967,.966,18.05)],-5)
    _controller_shell(m,'CtrlFront',[(1,1,18.1),(.994,.992,23),(.960,.955,28)],[(.966,.966,17.95),(.957,.950,23),(.935,.925,25.7)],4)
    cheeks=[];front_hoods=[];rear_hoods=[]
    for side in [-1,1]:
        x=side*43
        cheek=Part.makeCylinder(22.7,2.0,_controller_point(x,6,27.7))
        edges=[e for e in cheek.Edges if e.BoundBox.ZLength<1e-7 and e.BoundBox.ZMax>29.6]
        cheek=cheek.makeFillet(.8,edges);cheeks.append(cheek)
        front_hoods.append(m.rr(22,12,10,tuple(_controller_point(x,31.5,18.1)),2))
        rear_hoods.append(m.rr(22,12,7.2,tuple(_controller_point(x,31.5,10.6)),2))
    additions=cheeks[0].multiFuse(cheeks[1:]+front_hoods).removeSplitter();additions.check(True)
    _add_shape(m,'CtrlFront',additions,'Integral circular control faces and upper shoulder housings')
    _add_shape(m,'CtrlBack',Part.makeCompound(rear_hoods),'Integral lower shoulder housings')
    # Keep a visible parting gap between the two editable lofted covers.
    m.profile['stages']=16
    m.checkpoint(16,'scph1010_native_lofted_controller_shell','建立初代 SCPH-1010 数字手柄的原生闭合曲线草图、上下空心放样壳、圆形按键面和分层肩键罩；手柄尺寸为照片指导的学习近似，不加入模拟摇杆。')


STAGES[16]=stage16


def _controller_symbol(m,key,kind,x,y,z,material):
    from .psp import _polygon
    x,y,z=tuple(_controller_point(x,y,z))
    if kind=='Triangle':
        shape=_polygon([(x,y+2.15),(x-2,y-1.5),(x+2,y-1.5)],z,.025).cut(_polygon([(x,y+1.48),(x-1.42,y-1.18),(x+1.42,y-1.18)],z-.01,.05))
    elif kind=='Circle':shape=Part.makeCylinder(2,.025,V(x,y,z)).cut(Part.makeCylinder(1.7,.05,V(x,y,z-.01)))
    elif kind=='Square':shape=m.rr(3.7,3.7,.025,(x,y,z),.08).cut(m.rr(3.1,3.1,.05,(x,y,z-.01),.04))
    else:
        strips=[]
        for angle in [-45,45]:
            strip=m.rr(.32,4.8,.025,(x,y,z),.04);strip.rotate(V(x,y,z),V(0,0,1),angle);strips.append(strip)
        shape=strips[0].fuse(strips[1])
    m.feature(key,kind+' face-button symbol',shape,'Controller',6,material)


def stage17(m):
    from .psp import _polygon
    m.colors.update({'ctrlcyan':(.20,.69,.63),'ctrlcoral':(.79,.34,.29),'ctrlblue':(.20,.51,.77),'ctrlpurple':(.74,.35,.60)})
    apertures=[]
    points=[(-2.8,2.4),(2.8,2.4),(3.6,9),(0,11),(-3.6,9)]
    pivot=_controller_point(-43,6,0)
    for name,angle in [('Up',0),('Right',-90),('Down',180),('Left',90)]:
        shape=_polygon([(-43+x,-234+y) for x,y in points],29.05,2.25)
        edges=[e for e in shape.Edges if e.BoundBox.ZLength>2.24];shape=shape.makeFillet(.4,edges)
        shape=shape.fuse(Part.makeCylinder(1.7,3.65,_controller_point(-43,12.2,25.5)))
        shape.rotate(pivot,V(0,0,1),angle)
        m.feature('CtrlDPad'+name,'Original separated '+name.lower()+' directional key',shape,'Controller',5,'black')
        hole=_polygon([(-43+x*1.085,-234+y*1.085) for x,y in points],25.2,6.8);hole.rotate(pivot,V(0,0,1),angle);apertures.append(hole)
        mark=_polygon([(-44.1,-218),(-43.8,-218.2),(-43,-217.2),(-42.2,-218.2),(-41.9,-218),(-43,-216.8)],29.735,.025)
        mark.rotate(pivot,V(0,0,1),angle);m.feature('CtrlDirection'+name,'Directional-key embossed marker',mark,'Controller',6,'psdark')
    for name,dx,dy,mat in [('Triangle',0,10,'ctrlcyan'),('Circle',10,0,'ctrlcoral'),('Cross',0,-10,'ctrlblue'),('Square',-10,0,'ctrlpurple')]:
        x,y=43+dx,6+dy;pos=_controller_point(x,y,29.1)
        cap=Part.makeCylinder(4.35,2.4,pos)
        cap=cap.makeFillet(.35,[e for e in cap.Edges if e.BoundBox.ZLength<1e-7 and e.BoundBox.ZMax>31.4])
        cap=cap.fuse(Part.makeCylinder(1.5,3.7,_controller_point(x,y,25.5)))
        m.feature('CtrlButton'+name,name+' digital face button',cap,'Controller',5,'black')
        _controller_symbol(m,'CtrlSymbol'+name,name,x,y,31.535,mat)
        apertures.append(Part.makeCylinder(4.65,6.3,_controller_point(x,y,25.7)))
    select=m.rr(6.2,3.6,1.4,tuple(_controller_point(-9.5,-7.5,27.6)),.65)
    select=select.fuse(Part.makeCylinder(1.2,2.45,_controller_point(-9.5,-7.5,25.3)))
    m.feature('CtrlSelect','SELECT button and plunger',select,'Controller',5,'black')
    apertures.append(m.rr(6.7,4.1,4.6,tuple(_controller_point(-9.5,-7.5,25.0)),.75))
    start=_polygon([(7.1,-249.4),(7.1,-245.6),(12.5,-247.5)],27.6,1.4)
    start=start.fuse(Part.makeCylinder(1.0,2.45,_controller_point(9.0,-7.5,25.3)))
    m.feature('CtrlStart','Triangular START button and plunger',start,'Controller',5,'black')
    apertures.append(_polygon([(6.8,-249.8),(6.8,-245.2),(13,-247.5)],25.0,4.6))
    m.cut('CtrlFront',apertures,'Directional, face-button and menu apertures')
    m.label('CtrlSelectMark','SELECT',1.25,tuple(_controller_point(-14.5,-13,28.04)),'Controller',6,'psdark')
    m.label('CtrlStartMark','START',1.25,tuple(_controller_point(5,-13,28.04)),'Controller',6,'psdark')
    m.label('CtrlSonyMark','SONY',3.7,tuple(_controller_point(-9,17,28.04)),'Controller',6,'psdark')
    m.label('CtrlPSMark','PS',3.4,tuple(_controller_point(-3.5,6,28.04)),'Controller',6,'psdark')
    m.label('CtrlPlayStationMark','PlayStation',1.6,tuple(_controller_point(-8.5,1.8,28.04)),'Controller',6,'psdark')
    rear=g.rotation((0,1,0),(0,0,1))
    for side in [-1,1]:
        x=side*43;name='L' if side<0 else 'R'
        for tier,z in [(1,23.5),(2,14)]:
            shell='CtrlFront' if tier==1 else 'CtrlBack'
            m.cut(shell,m.rr(18.2,6.8,6,tuple(_controller_point(x,32.8,z)),.85,rear),'Shoulder button '+name+str(tier)+' aperture')
            m.box('Ctrl'+name+str(tier),name+str(tier)+' shoulder key',17.6,6.2,2,tuple(_controller_point(x,35.8,z)),'Controller',4,'black',.75,orient=rear)
            m.label('Ctrl'+name+str(tier)+'Mark',str(tier),2,tuple(_controller_point(x+.5,37.84,z-.7)),'Controller',5,'psgrey',rotation=rear)
        m.label('CtrlShoulder'+name,name,2.3,tuple(_controller_point(x-.8,32.7,28.14)),'Controller',5,'psdark')
    m.profile['stages']=17
    m.checkpoint(17,'digital_keys_and_two_tier_shoulders','补齐四个独立方向键、四色几何符号面键、SELECT/START 与上下两层 L/R 肩键；为真实凸出的键帽和传动杆开设对应孔位。')


STAGES[17]=stage17


def _controller_membrane(m,key,centres,central,base_radius,roof=25.4):
    shapes=[Part.makeCylinder(base_radius,.45,_controller_point(x,y,22.05)) for x,y in centres]
    shape=shapes[0].multiFuse(shapes[1:]+[Part.makeCylinder(central[2],.45,_controller_point(central[0],central[1],22.05))])
    for i,(x,y) in enumerate(centres):
        shape=shape.cut(Part.makeCylinder(4.1,.8,_controller_point(x,y,21.9)))
        cone=Part.makeCone(4.3,3.0,2.6,_controller_point(x,y,22.5)).fuse(Part.makeCylinder(3,.3,_controller_point(x,y,25.1)))
        cone=cone.cut(Part.makeCone(3.7,2.4,2.72,_controller_point(x,y,22.38)))
        shape=shape.fuse(cone)
        m.cyl(key+'Pill'+str(i),'Moving carbon switch contact',2.0,.20,tuple(_controller_point(x,y,24.85)),'Controller',2,'black',internal=True)
        pad=Part.makeCylinder(2.3,.04,_controller_point(x,y,21.75)).cut(Part.makeBox(.35,5,.10,_controller_point(x-.175,y-2.5,21.72)))
        m.feature(key+'Fixed'+str(i),'Split fixed carbon contact',pad,'Controller',1,'black',True)
    m.feature(key,'Four-key silicone membrane',shape.removeSplitter(),'Controller',2,'rubber',True)


def stage18(m):
    from .psp import _polygon
    outline=[(-57,22),(-27,22),(-23,23),(23,23),(27,22),(57,22),(61,9),(58,-10),(25,-10),(22,-12),(-22,-12),(-25,-10),(-58,-10),(-61,9)]
    pcb=_polygon([(x,y-240) for x,y in outline],20.5,1.2)
    m.feature('CtrlPCB','Original-family phenolic controller board',pcb,'Controller',0,'phenolic',True)
    dpad=[(-43,12.2),(-36.8,6),(-43,-.2),(-49.2,6)]
    face=[(43,16),(53,6),(43,-4),(33,6)]
    _controller_membrane(m,'CtrlDPadMembrane',dpad,(-43,6,4),5.1)
    _controller_membrane(m,'CtrlFaceMembrane',face,(43,6,7.3),5.1)
    guide=Part.makeCylinder(3,.45,_controller_point(-43,6,26.15)).cut(Part.makeCylinder(1.3,.7,_controller_point(-43,6,26)))
    arms=[]
    for a in [45,-45]:
        arm=m.rr(1.2,21,.45,tuple(_controller_point(-43,6,26.15)),.1);arm.rotate(_controller_point(-43,6,0),V(0,0,1),a);arms.append(arm)
    guide=guide.multiFuse(arms).removeSplitter()
    m.feature('CtrlDPadGuide','Rigid diagonal directional-key guide',guide,'Controller',3,'black',True)
    m.cut('CtrlFront',Part.makeCylinder(12,1.3,_controller_point(-43,6,25.7)),'Directional guide pocket below the front face')
    menu=m.rr(26,8,.45,tuple(_controller_point(0,-7.5,22.05)),1.5)
    for i,x in enumerate([-9.5,9.0]):
        menu=menu.cut(Part.makeCylinder(2.25,.8,_controller_point(x,-7.5,21.9)))
        dome=Part.makeCone(2.5,1.7,2.3,_controller_point(x,-7.5,22.5)).fuse(Part.makeCylinder(1.7,.4,_controller_point(x,-7.5,24.8)))
        dome=dome.cut(Part.makeCone(2.0,1.2,2.4,_controller_point(x,-7.5,22.4)))
        menu=menu.fuse(dome)
        m.cyl('CtrlMenuPill'+str(i),'Menu-key moving carbon pill',1.1,.18,tuple(_controller_point(x,-7.5,24.58)),'Controller',2,'black',internal=True)
        pad=Part.makeCylinder(1.6,.04,_controller_point(x,-7.5,21.75)).cut(Part.makeBox(.3,4,.1,_controller_point(x-.15,-9.5,21.72)))
        m.feature('CtrlMenuFixed'+str(i),'Menu-key fixed carbon contacts',pad,'Controller',1,'black',True)
    m.feature('CtrlMenuMembrane','SELECT and START silicone membrane',menu.removeSplitter(),'Controller',2,'rubber',True)
    m.box('CtrlLogicPackage','Controller logic package study',8,9,1.6,tuple(_controller_point(0,10,21.95)),'Controller',1,'black',.3,True)
    terminals=[]
    for side in [-1,1]:
        for i in range(8):terminals.append(Part.makeBox(.3,.8,.18,_controller_point(-3.25+i*.93,10+side*5.0-.4,21.82)))
    m.feature('CtrlLogicLeads','Controller logic-package lead study',Part.makeCompound(terminals),'Controller',1,'metal',True)
    m.cyl('CtrlBoardCap','Controller board capacitor package',1.2,7,tuple(_controller_point(-13,17,18.25)),'Controller',0,'black',axis=(1,0,0),internal=True)
    m.feature('CtrlBoardCapEnds','Controller capacitor end caps',Part.makeCompound([Part.makeCylinder(1.21,.3,_controller_point(x,17,18.25),V(1,0,0)) for x in [-13.4,-5.9]]),'Controller',0,'metal',True)
    rear=g.rotation((0,1,0),(0,0,1))
    for side in [-1,1]:
        x=side*43;name='L' if side<0 else 'R'
        cavity=m.rr(19.6,15.4,8.5,tuple(_controller_point(x,26,19)),.6,rear)
        for shell in ['CtrlBack','CtrlFront']:m.cut(shell,cavity,'Shoulder assembly interior')
        m.box('Ctrl'+name+'PCB','Two-level shoulder contact board',16.8,14,.8,tuple(_controller_point(x,30,19)),'Controller',1,'phenolic',.3,True,orient=rear)
        carrier=m.rr(18.4,15.2,1.2,tuple(_controller_point(x,27.6,19)),.5,rear).cut(m.rr(14,11.8,1.6,tuple(_controller_point(x,27.4,19)),.3,rear))
        m.feature('Ctrl'+name+'Carrier','Shoulder contact-board retainer',carrier,'Controller',0,'psgrey',True)
        for tier,z in [(1,23.5),(2,14)]:
            pos=_controller_point(x,31.4,z)
            rubber=Part.makeCone(2.4,1.4,1.75,pos,V(0,1,0)).fuse(Part.makeCylinder(1.4,.30,_controller_point(x,33.15,z),V(0,1,0)))
            rubber=rubber.cut(Part.makeCone(1.9,.9,1.9,_controller_point(x,31.25,z),V(0,1,0)))
            m.feature('Ctrl'+name+str(tier)+'Dome','Shoulder-key silicone dome',rubber,'Controller',2,'rubber',True)
            m.cyl('Ctrl'+name+str(tier)+'Pill','Shoulder-key moving carbon pill',.8,.16,tuple(_controller_point(x,32.88,z)),'Controller',2,'black',axis=(0,1,0),internal=True)
            m.cyl('Ctrl'+name+str(tier)+'Pad','Shoulder-key fixed carbon contact',1.8,.04,tuple(_controller_point(x,30.86,z)),'Controller',1,'black',axis=(0,1,0),internal=True)
            stem=m.rr(3,2.8,2.35,tuple(_controller_point(x,33.55,z)),.2,rear)
            _add_shape(m,'Ctrl'+name+str(tier),stem,'Shoulder-key internal plunger')
    m.profile['stages']=18
    m.checkpoint(18,'controller_boards_membranes_and_contact_mechanisms','加入棕色主板、分离碳接点、硅胶按键穹顶、方向键导架、菜单键胶垫与两侧肩键小板及传动柱；控制逻辑封装仅作结构示意。')


STAGES[18]=stage18


def stage19(m):
    from .atari2600 import _rounded_route
    mounts=[(-55,20),(-27,24),(-27,-5),(-57,-40),(27,24),(55,20),(27,-5),(57,-40)]
    _add_shape(m,'CtrlFront',Part.makeCompound([Part.makeCylinder(2.1,20.6,_controller_point(x,y,5.5)) for x,y in mounts]),'Eight controller case fixing posts')
    m.cut('CtrlFront',[Part.makeCylinder(.85,16.5,_controller_point(x,y,5.3)) for x,y in mounts],'Controller screw-pilot bores')
    m.cut('CtrlPCB',[Part.makeCylinder(2.4,2,_controller_point(x,y,20.2)) for x,y in mounts],'Controller case-post clearances in the board')
    rear_tools=[]
    for i,(x,y) in enumerate(mounts):
        rear_tools.extend([Part.makeCylinder(1.0,18,_controller_point(x,y,.5)),Part.makeCylinder(1.85,3.2,_controller_point(x,y,.5)),Part.makeCylinder(2.4,12.5,_controller_point(x,y,5.3))])
        m.screw('CtrlCaseScrew'+str(i),tuple(_controller_point(x,y,3.0)),'Controller',-5,length=15.5,radius=1.5)
    m.cut('CtrlBack',rear_tools,'Eight recessed rear screw seats and upper-post reliefs')
    grommet=Part.makeCylinder(2.8,12,_controller_point(0,24,17.5),V(0,1,0))
    for i in range(5):grommet=grommet.fuse(Part.makeCylinder(3.1,.5,_controller_point(0,29+i*1.2,17.5),V(0,1,0)))
    grommet=grommet.cut(Part.makeCylinder(1.9,12.4,_controller_point(0,23.8,17.5),V(0,1,0)))
    m.feature('CtrlCableGrommet','Ribbed controller cable strain relief',grommet,'Controller',0,'black',True)
    for shell in ['CtrlBack','CtrlFront']:m.cut(shell,Part.makeCylinder(3.3,15,_controller_point(0,23,17.5),V(0,1,0)),'Central controller cable exit')
    path=[_controller_point(*p) for p in [(0,36.2,17.5),(0,49,17.5),(60,65,12),(91,39,11),(91,-5,10),(120,-5,10)]]
    m.feature('CtrlCable','Original digital-controller cable study',_rounded_route(path,6,1.75),'Controller',0,'black')
    # Internal seven-wire termination; unused motor/interrupt positions are not populated.
    wire_holes=[]
    for i,mat in enumerate(['ctrlcyan','ctrlcoral','white','psdark','coil','ctrlblue','yellow']):
        sx=(i-3)*.55;tx=(i-3)*1.1
        points=[_controller_point(sx,23.8,17.5),_controller_point(sx,21.5,17.5),_controller_point(tx,18,19.7),_controller_point(tx,16,20.35)]
        m.feature('CtrlInternalLead'+str(i),'Digital-controller internal lead '+str(i+1),_rounded_route(points,.4,.20),'Controller',0,mat,True)
        axis=(points[-1]-points[-2]).normalize();wire_holes.append(Part.makeCylinder(.32,2.3,points[-1]-axis*.4,axis))
    m.cut('CtrlPCB',wire_holes,'Wire solder-entry clearances')
    for side in [-1,1]:
        name='L' if side<0 else 'R'
        for i in range(3):
            points=[_controller_point(side*(43+(i-1)*1.2),29.8,19),_controller_point(side*(54+.9*i),24-.8*i,17),_controller_point(side*(58+.6*i),2+i,17),_controller_point(side*(58+.6*i),-7,17),_controller_point(side*(55+.8*i),-7,20.2)]
            m.feature('Ctrl'+name+'Wire'+str(i),'Shoulder contact-board wire',_rounded_route(points,.45,.18),'Controller',0,'black',True)
    # Detached nine-position plug, with the seven digital-controller contacts.
    normal=g.rotation((1,0,0),(0,0,1))
    body=m.rr(42,12,20,tuple(_controller_point(122,-5,10)),2,normal)
    body=body.cut(m.rr(39,9,18,tuple(_controller_point(123,-5,10)),1.2,normal))
    body=body.cut(m.rr(40.3,7.5,4,tuple(_controller_point(140.8,-5,10)),1.4,normal))
    m.feature('CtrlPlugBody','Original rectangular controller plug housing',body,'Controller',0,'psgrey')
    relief=Part.makeCone(2.4,4.8,11.8,_controller_point(110,-5,10),V(1,0,0)).cut(Part.makeCylinder(1.85,12.2,_controller_point(109.8,-5,10),V(1,0,0)))
    m.feature('CtrlPlugRelief','Plug cable strain relief',relief,'Controller',0,'black')
    active={0,1,3,4,5,6,8}
    for group in range(3):
        yy=-5+(group-1)*13
        nose=m.rr(12.2,5.2,5,tuple(_controller_point(141.5,yy,10)),1.3,normal)
        for i in range(3):
            y=yy+(i-1)*3.6;number=group*3+i
            nose=nose.cut(Part.makeCylinder(.55,6,_controller_point(141,y,10),V(1,0,0)))
            if number in active:m.cyl('CtrlPlugPin'+str(number),'Controller plug pin '+str(number+1),.38,7.3,tuple(_controller_point(140.8,y,10)),'Controller',0,'metal',axis=(1,0,0),internal=True)
        m.feature('CtrlPlugTriplet'+str(group),'Three-position plug nose',nose,'Controller',0,'black')
    m.label('CtrlPlugMark','SONY',2.1,tuple(_controller_point(127,-9,16.035)),'Controller',1,'psdark')
    reverse=g.rotation((0,0,-1),(0,1,0))
    m.label('CtrlRearModel','SCPH-1010',1.8,tuple(_controller_point(9,5,.96)),'Controller',-5,'psdark',rotation=reverse)
    m.profile['stages']=19
    m.checkpoint(19,'controller_fasteners_and_seven_wire_plug','加入八处后壳螺钉、固定柱、主线与肩键线束、应力释放套及九位置七接点插头；保留初代数字控制器的空缺接点与型号标识。')


STAGES[19]=stage19
