"""Original Japanese SCPH-1000: editable grey enclosure and later staged internals."""
import FreeCAD as App
import Part
import Sketcher
from .core import V


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
