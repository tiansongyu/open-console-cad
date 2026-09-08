import json

import math

import time

from pathlib import Path

import FreeCAD as App

import FreeCADGui as Gui

import Part

import Sketcher

from pivy import coin

def vec(x=0,y=0,z=0):
    return App.Vector(x,y,z)

def rotation(normal=(0,0,1), up=(0,1,0)):
    z=vec(*normal); z.normalize()
    x=vec(*up).cross(z); x.normalize()
    y=z.cross(x)
    m=App.Matrix()
    m.A11,m.A21,m.A31=x.x,x.y,x.z
    m.A12,m.A22,m.A32=y.x,y.y,y.z
    m.A13,m.A23,m.A33=z.x,z.y,z.z
    return App.Rotation(m)

def camera(normal=(0,0,1), up=(0,1,0), target=(0,0,3.9), span=175):
    gd=Gui.activeDocument()
    views=gd.mdiViewsOfType('Gui::View3DInventor')
    if not views:
        gd.createView('Gui::View3DInventor');views=gd.mdiViewsOfType('Gui::View3DInventor')
    v=views[0]
    c=v.getCameraNode()
    r=rotation(normal,up)
    p=vec(*target)+r.multVec(vec(0,0,350))
    c.orientation.setValue(coin.SbRotation(*r.Q))
    c.position.setValue(p.x,p.y,p.z)
    c.focalDistance.setValue(350)
    c.height.setValue(span)
    v.redraw()
    Gui.updateGui()
    return v

def render(path, normal=(0,0,1), up=(0,1,0), target=(0,0,3.9), span=175, size=(1600,1200), hide=None):
    Gui.Selection.clearSelection()
    doc=App.ActiveDocument
    hidden={name:doc.getObject(name).Visibility for name in (hide or []) if doc.getObject(name)}
    try:
        for name in hidden:doc.getObject(name).Visibility=False
        v=camera(normal,up,target,span)
        v.saveImage(str(path),*size,'White')
    finally:
        for name,value in hidden.items():doc.getObject(name).Visibility=value
    return str(path)

def appearance(obj, color=(.3,.4,.7), metal=0.35, gloss=45, transparency=0):
    vo=obj.ViewObject
    if hasattr(vo,'ShapeAppearance'):
        material=vo.ShapeAppearance[0]
        material.DiffuseColor=tuple(color)
        material.AmbientColor=tuple(v*.45 for v in color)
        material.SpecularColor=(metal,metal,metal)
        material.Shininess=gloss
        material.Transparency=transparency/100.0
        vo.ShapeAppearance=[material]
    elif hasattr(vo,'ShapeColor'):
        vo.ShapeColor=tuple(color)
    if hasattr(vo,'LineColor'): vo.LineColor=tuple(v*.55 for v in color)
    if hasattr(vo,'LineWidth'): vo.LineWidth=1.0
    if hasattr(vo,'Deviation'): vo.Deviation=.04
    if hasattr(vo,'AngularDeflection'): vo.AngularDeflection=10
    if hasattr(vo,'Transparency'): vo.Transparency=transparency
    if hasattr(vo,'DisplayMode'):
        try: vo.DisplayMode='Flat Lines'
        except Exception: pass
    return obj

def shape_report(obj):
    s=obj.Shape
    bb=s.optimalBoundingBox(False,False)
    return {'name':obj.Name,'label':obj.Label,'type':obj.TypeId,'valid':s.isValid(),
            'null':s.isNull(),'solids':len(s.Solids),'faces':len(s.Faces),
            'volume':s.Volume,'bounds':[bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax],
            'state':list(obj.State)}

def audit_objects(objects):
    rows=[shape_report(o) for o in objects]
    bad=[r for r in rows if r['null'] or not r['valid'] or r['solids']==0 or r['volume']<=0 or 'Invalid' in r['state']]
    if bad: raise AssertionError(json.dumps(bad,ensure_ascii=False))
    return rows

def rr_shape(width,height,radius,depth,origin=(0,0,0),orient=None):
    """Transient rounded prism used for validating tools and complex cuts."""
    base=Part.makeBox(width,height,depth,vec(-width/2,-height/2,0))
    if radius:
        edges=[e for e in base.Edges if len(e.Vertexes)==2 and abs(e.BoundBox.ZLength-depth)<1e-7]
        base=base.makeFillet(radius,edges)
    base.Placement=App.Placement(vec(*origin),orient or App.Rotation())
    assert base.isValid() and len(base.Solids)==1
    return base

def rect_sketch(doc,name,width,height):
    sk=doc.addObject('Sketcher::SketchObject',name)
    p=[(-width/2,-height/2),(width/2,-height/2),(width/2,height/2),(-width/2,height/2)]
    sk.addGeometry([Part.LineSegment(vec(*p[i]),vec(*p[(i+1)%4])) for i in range(4)],False)
    for i in range(4): sk.addConstraint(Sketcher.Constraint('Coincident',i,2,(i+1)%4,1))
    for i in [0,2]: sk.addConstraint(Sketcher.Constraint('Horizontal',i))
    for i in [1,3]: sk.addConstraint(Sketcher.Constraint('Vertical',i))
    for constraint,name in [(Sketcher.Constraint('Distance',0,width),'Width'),
                            (Sketcher.Constraint('Distance',1,height),'Height'),
                            (Sketcher.Constraint('DistanceX',0,1,-width/2),'Left'),
                            (Sketcher.Constraint('DistanceY',0,1,-height/2),'Bottom')]:
        idx=sk.addConstraint(constraint);sk.renameConstraint(idx,name)
    sk.setExpression('Constraints.Left','-Constraints.Width / 2')
    sk.setExpression('Constraints.Bottom','-Constraints.Height / 2')
    doc.recompute()
    assert sk.solve()==0
    return sk

def rounded_body(doc,name,label,width,height,radius,depth,origin=(0,0,0),orient=None,color=(.3,.4,.7),group=None,expr=None):
    b=doc.addObject('PartDesign::Body',name); b.Label=label
    sk=rect_sketch(doc,name+'Sketch',width,height);b.addObject(sk)
    sk.Label=label+' · 轮廓'
    pad=b.newObject('PartDesign::Pad',name+'Pad');pad.Profile=(sk,['']);pad.Length=depth
    doc.recompute()
    tip=pad
    if radius>0:
        edge_names=[f'Edge{i+1}' for i,e in enumerate(pad.Shape.Edges) if len(e.Vertexes)==2 and abs(e.BoundBox.ZLength-depth)<1e-7]
        assert len(edge_names)==4
        fillet=b.newObject('PartDesign::Fillet',name+'CornerFillet');fillet.Base=(pad,edge_names);fillet.Radius=radius
        doc.recompute();tip=fillet;pad.Visibility=False
    b.Tip=tip
    sk.Visibility=False;tip.Visibility=True
    b.Placement=App.Placement(vec(*origin),orient or App.Rotation())
    if group: group.addObject(b)
    if expr:
        for key,value in expr.items():
            if key in ['Width','Height']:sk.setExpression('Constraints.'+key,value)
            elif key=='Depth':pad.setExpression('Length',value)
            elif key=='Radius' and radius>0:tip.setExpression('Radius',value)
            elif key in ['X','Y','Z']:b.setExpression('Placement.Base.'+key.lower(),value)
    doc.recompute()
    appearance(b,color)
    assert tip.Shape.isValid() and not tip.Shape.isNull(), name
    return b

def part_feature(doc,name,label,shape,color=(.3,.4,.7),group=None):
    o=doc.addObject('PartDesign::Feature' if group and group.TypeId=='PartDesign::Body' else 'Part::Feature',name)
    o.Label=label;o.Shape=shape
    if group:group.addObject(o)
    appearance(o,color)
    return o

def boolean_cut(doc,name,label,base,tool,color=None,group=None):
    o=doc.addObject('Part::Cut',name);o.Label=label;o.Base=base;o.Tool=tool;o.Refine=True
    if group:group.addObject(o)
    doc.recompute();base.Visibility=False;tool.Visibility=False
    if color:appearance(o,color)
    assert o.Shape.isValid() and not o.Shape.isNull(),name
    return o

def set_visible_components(doc,objects):
    visible={o.Name for o in objects}
    owners={child.Name:body for body in doc.Objects if body.TypeId=='PartDesign::Body' for child in body.Group}
    for o in doc.Objects:
        if o.TypeId=='App::Part':
            o.Visibility=True
            o.Origin.Visibility=False
        elif o.Name.startswith(('Origin','X_Axis','Y_Axis','Z_Axis','XY_Plane','XZ_Plane','YZ_Plane')):
            o.Visibility=False
        elif hasattr(o,'Shape'):
            if o.Name in owners:
                b=owners[o.Name]
                o.Visibility=b.Name in visible and b.Tip==o
            else:
                o.Visibility=o.Name in visible
    for o in objects:o.Visibility=True
    Gui.updateGui()
