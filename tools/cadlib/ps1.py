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
