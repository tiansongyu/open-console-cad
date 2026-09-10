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
