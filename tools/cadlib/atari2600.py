"""Approximate 1977 CX2600 Heavy Sixer study, based on original hardware."""
import math
import FreeCAD as App
import Part
from .core import V
from . import geometry as g


def _yz_prism(points, x=-200, width=400):
    wire=Part.makePolygon([V(x,y,z) for y,z in points]+[V(x,*points[0])])
    return Part.Face(Part.Wire(wire.Edges)).extrude(V(width,0,0))


def _hump_tools(offset=0):
    return [
        _yz_prism([(-130,50.6+offset),(9,50.6+offset),(76,86.6+offset),(76,110),(-130,110)]),
        _yz_prism([(92,86.6+offset),(104,50.6+offset),(130,50.6+offset),(130,110),(92,110)]),
    ]


def stage01(m):
    m.colors.update({'atariblack':(.14,.135,.125),'wood':(.48,.23,.07),'grain':(.26,.105,.035),'orange':(.75,.35,.035),'phenolic':(.62,.44,.22)})
    m.params.set('A3','Depth (Y)');m.params.set('A4','Height (Z)')
    m.params.set('B7','10 mm');m.params.set('C7','Approximate thick lower-wall section; other shell walls differ')
    base=m.native('LowerHousing','Heavy rounded lower housing',346,231.5,18,40,(0,0,8),'Body',-6,'atariblack',expr={'Width':'Parameters.Width'})
    # Preserve an additional native edge fillet for the broad rolled lower rim.
    tip=base.Tip
    bottom=[f'Edge{i+1}' for i,e in enumerate(tip.Shape.Edges) if abs(e.BoundBox.ZMin)<1e-7 and abs(e.BoundBox.ZMax)<1e-7]
    rolled=base.newObject('PartDesign::Fillet','LowerRimRound');rolled.Base=(tip,bottom);rolled.Radius=10
    m.doc.recompute();assert rolled.Shape.isValid() and rolled.Shape.Solids
    tip.Visibility=False;base.Tip=rolled
    m.cut('LowerHousing',m.rr(326,211.5,34,(0,0,18),8),'Heavy lower housing cavity')
    m.native('TopDeck','Horizontal ribbed deck foundation',325.6,211.1,7.8,2.3,(0,0,48.15),'Body',4,'atariblack')
    m.cut('TopDeck',m.rr(305.4,90.4,4,(0,56.5,47.9),2.0),'Open deck below the raised switch enclosure')
    m.native('ControlHump','Raised sloping control enclosure',310,95,4,36,(0,56.5,50.6),'Body',4,'atariblack')
    m.cut('ControlHump',_hump_tools(),'Front control slope and steep rear return')
    inner=m.rr(305.2,90.2,34.2,(0,56.5,50.4),1.6).cut(Part.makeCompound(_hump_tools(-2.2)))
    m.cut('ControlHump',inner,'Following hollow interior of the control hump')
    # Independent front fascia; colour denotes printed wood veneer, not solid timber.
    front=g.rotation((0,-1,0),(0,0,1))
    fascia=m.native('WoodFascia','Printed woodgrain front fascia',319,27,9,.18,(0,0,0),'Body',4,'wood')
    fascia.Placement=App.Placement(V(0,-115.92,33.2),front);fascia.FlatPlacement=fascia.Placement
    for i,(x,y) in enumerate([(-137,-85),(137,-85),(-137,85),(137,85)]):
        m.cyl('Foot'+str(i),'Recessed rubber support foot',6.5,7.8,(x,y,0),'Body',-6,'rubber')
    # Broad front/rear curves and thick side walls distinguish the early heavy shell.
    m.profile['stages']=1
    m.checkpoint(1,'heavy_sixer_native_enclosure','建立原生草图与双重圆角的厚壁底壳、独立顶板、空心斜面控制台、木纹色前饰板和四个脚垫；全部尺寸标记为近似学习尺寸。')


STAGES={1:stage01}


def _control_frame():
    q=App.Rotation(V(1,0,0),math.degrees(math.atan2(36,67)))
    return App.Placement(V(0,42.5,68.6),q)


def stage02(m):
    frame=_control_frame();q=frame.Rotation
    def pos(x,y,z):return frame.multVec(V(x,y,z))
    outer=m.rr(296,65.4,.10,r=1.1)
    inner=m.rr(294.6,64,.14,pos=(0,0,-.02),r=.5)
    trim=outer.cut(inner);trim.Placement=App.Placement(pos(0,0,.08),q)
    m.feature('ControlTrim','Orange control-bezel pinstripe',trim,'Body',4,'orange')
    bezel=m.rr(294.2,63.6,.12,r=.4);bezel.Placement=App.Placement(pos(0,0,.08),q)
    m.feature('ControlBezel','Printed black control faceplate',bezel,'Body',4,'black')
    slot=m.rr(80,20,14,r=3.8);slot.Placement=App.Placement(pos(0,-10,-10),q)
    for key in ['ControlHump','ControlBezel']:m.cut(key,slot,'Sloping cartridge entry opening')
    for i,(x,title) in enumerate([(-126,'power'),(-97,'tv type'),(-68,'left'),(68,'right'),(97,'game'),(126,'game')]):
        tool=Part.makeCylinder(3.1,12,V(x,0,-8))
        tool.Placement=frame
        for key in ['ControlHump','ControlBezel']:m.cut(key,tool,'Metal switch actuator clearance')
        washer=Part.makeCylinder(5.5,.9).cut(Part.makeCylinder(2.7,1.1,V(0,0,-.1)))
        washer.Placement=App.Placement(pos(x,0,.28),q)
        m.feature('SwitchWasher'+str(i),'Switch actuator dust washer',washer,'Controls',6,'black')
        stem=Part.makeCylinder(2.35,19,V(0,0,.4)).fuse(Part.makeSphere(2.35,V(0,0,19.4)))
        stem.Placement=App.Placement(pos(x,0,.3),q)
        m.feature('SwitchLever'+str(i),'Metal '+title+' switch lever',stem,'Controls',6,'metal')
        m.label('SwitchTitle'+str(i),title,2.4,tuple(pos(x-7,19,.23)),'Body',4,'orange',rotation=q)
        lower=['on / off','color / b-w','difficulty','difficulty','select','reset'][i]
        m.label('SwitchLegend'+str(i),lower,1.7,tuple(pos(x-8,13,.23)),'Body',4,'orange',rotation=q)
        if i in [2,3]:m.label('DifficultyAB'+str(i),'a / b',1.8,tuple(pos(x+6,-7,.23)),'Body',4,'orange',rotation=q)
    m.label('SystemTitle','video computer system',3.4,tuple(pos(-40,19,.23)),'Body',4,'metal',rotation=q)
    grooves=[m.rr(311,1.5,1.2,(0,-97+i*4.0,49.65),.4) for i in range(27)]
    m.cut('TopDeck',grooves,'Closely spaced horizontal deck ribs')
    # Thin solid ribbons denote the printed grain without external image textures.
    grain=[]
    for j in range(9):
        points=[(-151+i*6.0,-10+j*2.5+.4*math.sin(i*.35+j)) for i in range(51)]
        outline=[V(x,z,0) for x,z in points]+[V(x,z+.18,0) for x,z in reversed(points)]
        wire=Part.makePolygon(outline+[outline[0]])
        grain.append(Part.Face(Part.Wire(wire.Edges)).extrude(V(0,0,.025)))
    front=g.rotation((0,-1,0),(0,0,1));printed=Part.makeCompound(grain)
    printed.Placement=App.Placement(V(0,-116.115,33.2),front)
    m.feature('WoodgrainPrint','Printed woodgrain study pattern',printed,'Body',4,'grain')
    m.label('AtariWord','ATARI',4.5,(126,-116.15,24.5),'Body',4,'metal',rotation=front)
    m.profile['stages']=2
    m.checkpoint(2,'six_switches_ribs_and_fascia','加入六个金属操作杆及各自孔位、防尘垫、斜面卡带口、橙色铭牌边线和功能标识，并补齐横向筋槽与几何木纹印刷层。')


STAGES[2]=stage02
