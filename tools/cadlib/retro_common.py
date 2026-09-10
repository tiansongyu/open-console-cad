"""Native rounded lofts and connector geometry for original console studies."""
import math
import FreeCAD as App
import Part
import Sketcher
from .core import V
from . import geometry as g


def rounded_outline(width, depth, radius):
    a, b, r = width / 2, depth / 2, radius
    q = r / math.sqrt(2)
    points = [(-a+r,-b),(a-r,-b),(a,-b+r),(a,b-r),
              (a-r,b),(-a+r,b),(-a,b-r),(-a,-b+r)]
    mids = [(a-r+q,-b+r-q),(a-r+q,b-r+q),
            (-a+r-q,b-r+q),(-a+r-q,-b+r-q)]
    curves = []
    for i in range(4):
        curves.append(Part.LineSegment(V(*points[2*i]), V(*points[2*i+1])))
        curves.append(Part.Arc(V(*points[2*i+1]), V(*mids[i]), V(*points[(2*i+2)%8])))
    return curves


def native_loft(m, key, sections, outline=None):
    sketches = []
    for i, (width, depth, radius, x, y, z) in enumerate(sections):
        sk = m.doc.addObject('Sketcher::SketchObject', key+'Section'+str(i))
        sk.Label = key+' · section '+str(i+1)
        curves = rounded_outline(width, depth, radius) if outline is None else outline(width, depth)
        sk.addGeometry(curves, False)
        for n in range(len(curves)):
            sk.addConstraint(Sketcher.Constraint('Block',n))
        sk.Placement.Base = V(x,y,z)
        m.group('Construction').addObject(sk)
        sketches.append(sk)
    loft = m.doc.addObject('Part::Loft',key)
    loft.Sections = sketches
    loft.Solid = True
    loft.Ruled = True
    loft.Closed = False
    m.group('Construction').addObject(loft)
    m.doc.recompute()
    for sk in sketches: sk.Visibility=False
    assert loft.Shape.Solids and loft.Shape.Volume>0 and loft.Shape.isValid(), key
    loft.Shape.check(True)
    return loft


def loft_shell(m,key,label,outer,inner,assembly='Body',layer=0,material='accent',outline=None):
    outside=native_loft(m,key+'Outer',outer,outline)
    inside=native_loft(m,key+'Inner',inner,outline)
    shell=g.boolean_cut(m.doc,key,label,outside,inside)
    shell.Shape.check(True)
    return m.register(shell,key,assembly,layer,material)


def fuse_feature(m,key,shape,label,refine=True):
    old=m.parts[key]
    tool=g.part_feature(m.doc,key+'AddTool',label,shape)
    m.group('Construction').addObject(tool)
    obj=m.doc.addObject('Part::Fuse',key+'Fuse');obj.Base=old;obj.Tool=tool;obj.Refine=refine
    m.doc.recompute();assert obj.Shape.isValid() and obj.Shape.Solids,key
    obj.Shape.check(True);old.PhysicalPart=False
    m.register(obj,key,old.Assembly,old.ExplodeLayer,old.MaterialDescription)
    obj.Label=old.Label;old.Visibility=False;tool.Visibility=False
    return obj


def d_profile(w,h,z=0):
    p=[(-w/2+2,-h/2),(w/2-2,-h/2),(w/2,h/2),(-w/2,h/2)]
    return Part.Face(Part.makePolygon([V(x,y,z) for x,y in p+[p[0]]]))


def de9(m,key,pos,normal=(0,-1,0),assembly='Ports',male=True):
    rotation=g.rotation(normal,(0,0,1));p=V(*pos)
    def place(shape):
        shape.Placement=App.Placement(p,rotation);return shape
    frame=d_profile(25.0,10.6).extrude(V(0,0,7.0)).cut(d_profile(22.8,8.4,-.1).extrude(V(0,0,7.2)))
    m.feature(key+'Shield','DE-9 trapezoidal metal shell',place(frame),assembly,0,'metal',True)
    points=[((i-2)*2.75,2.0) for i in range(5)]+[((i-1.5)*2.75,-2.0) for i in range(4)]
    insulator=d_profile(22.2,7.8).extrude(V(0,0,3.0))
    holes=[Part.makeCylinder(.67,3.4,V(x,y,-.2)) for x,y in points]
    m.feature(key+'Insert','DE-9 insulating contact support',place(insulator.cut(Part.makeCompound(holes))),assembly,0,'black',True)
    for i,(x,y) in enumerate(points):
        pin=Part.makeCylinder(.49,5.8,V(x,y,.1))
        if not male:pin=pin.cut(Part.makeCylinder(.30,6,V(x,y,0)))
        m.feature(key+'Pin'+str(i),'DE-9 contact '+str(i+1),place(pin),assembly,0,'gold',True)
    for side in [-1,1]:
        tab=g.rr_shape(4,10.6,.8,1.0,(side*15,0,0)).cut(Part.makeCylinder(1.45,1.4,V(side*15,0,-.2)))
        m.feature(key+'Tab'+str(side),'Connector mounting ear',place(tab),assembly,0,'metal',True)
    return place(d_profile(25.8,11.4,-1).extrude(V(0,0,10)))
