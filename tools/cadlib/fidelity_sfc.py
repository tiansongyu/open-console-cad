"""Original SHVC-001 interface grids and photograph-based exterior correction."""
import FreeCAD as App
import Part
from .core import V
from .handheld_refinement import replace
from . import geometry as g


def _shift(m, key, delta, reason):
    s = m.parts[key].Shape.copy(); s.translate(V(*delta)); return replace(m, key, s, reason)


def _d_body(cx, y, z, width, height, depth, rounded_left):
    r = height / 2
    center = cx + (-width / 2 + r if rounded_left else width / 2 - r)
    left = center if rounded_left else cx - width / 2
    block = Part.makeBox(width-r, depth, height, V(left, y, z-r))
    return block.fuse(Part.makeCylinder(r, depth, V(center,y,z),V(0,1,0))).removeSplitter()


def stage22(m):
    # Sanni's footprint has 31 positions per bank: 2.50 mm pitch, with two
    # 7.50 mm adjacent-centre gaps. Existing contact height/form is schematic.
    for row in range(2):
        for i in range(31):
            x = -42.5 + 2.5*i + (5 if i >= 4 else 0) + (5 if i >= 27 else 0)
            for prefix in ('CartUpperContact', 'CartLowerContact'):
                key = prefix + str(row*31+i)
                old = m.parts[key].Shape.BoundBox.Center.x
                _shift(m,key,(x-old,0,0),'2.50 mm cartridge grid with two 7.50 mm centre gaps; spring form remains schematic')
    for key, w, h, z, depth, channel_w, channel_h, bottom in [
            ('CartLowerSocket',126,13,19,9.6,91,6,20),
            ('CartUpperConnector',124.5,11.8,28.8,16,90,4.8,30.1)]:
        shell = m.rr(w,h,depth,(0,27,z),.8)
        slot = m.rr(channel_w,channel_h,depth,(0,27,bottom),.5)
        # Keep the observed three-bank separation; keyed wall dimensions are
        # fitted estimates, not inferred directly from a solder-pad footprint.
        keys = [m.rr(4.5,channel_h+1,depth+.2,(x,27,bottom-.1),.3) for x in (-31.25,31.25)]
        slot = slot.cut(Part.makeCompound(keys))
        replace(m,key,shell.cut(slot),'Narrowed active channel and estimated dividing keys around corrected 62-contact grid')
    calibrate_front(m)
    # Original POWER has a substantial raised ridge above the recessed cap.
    replace(m,'PowerCap',m.rr(25,27,.8,(-56,-43,70.9),2.8),'Lower POWER face to leave room for raised sliding grip')
    _shift(m,'PowerMark',(0,0,-2.2),'POWER legend follows recessed cap face')
    replace(m,'PowerRidge',m.rr(21,3.5,2.28,(-56,-38,71.72),1.2),'Photograph-fitted raised POWER grip, retaining 74 mm overall height')
    for name,x in [('Power',-56),('Reset',56)]:
        ring=m.rr(28.4,30.4,.08,(x,-43,73.91),4.4).cut(m.rr(25.8,27.8,.3,(x,-43,73.8),3.2))
        m.feature(name+'LightSurround','Original light control-aperture surround, photograph fit',ring,'Controls',5,'sfcgray')
    # Move the complete optical opening, not just the lens over a stale hole.
    for obj in m.doc.Objects:
        if obj.Label.startswith('Original power indicator aperture · tool'):
            s=obj.Shape.copy();s.translate(V(-9,3,0));obj.Shape=s
    _shift(m,'PowerLens',(-9,3,0),'Power indicator centre fitted to original SHVC-001 top photograph')
    _shift(m,'PowerLampMark',(-9,3,0),'Legend follows corrected optical window')
    # Compatible HVC-002 barrel and RCA interface data constrain mating sizes.
    replace(m,'DCCenter',Part.makeCylinder(1,7,V(-62,109,30),V(0,1,0)),'2.0 mm estimated contact leaves clearance in nominal 2.1 mm DC bore')
    dc=Part.makeCylinder(3.7,9,V(-62,109,30),V(0,1,0)).cut(Part.makeCylinder(2.85,9.2,V(-62,108.9,30),V(0,1,0)))
    replace(m,'DCSocket',dc,'Clearance for nominal 5.5 mm compatible HVC-002 plug')
    dc=Part.makeCylinder(2.75,9,V(290,51.5,31.1),V(0,1,0)).cut(Part.makeCylinder(1.05,9.2,V(290,51.4,31.1),V(0,1,0)))
    replace(m,'ACDCBarrel',dc,'Compatible original HVC-002 nominal 5.5 x 2.1 mm barrel')
    rf=Part.makeCylinder(4.15,9,V(-14,109,30),V(0,1,0)).cut(Part.makeCylinder(3.3,9.2,V(-14,108.9,30),V(0,1,0)))
    replace(m,'RFSocket',rf,'Compatible RCA jack 8.30 mm outer diameter')
    ins=Part.makeCylinder(3.25,6,V(-14,109,30),V(0,1,0)).cut(Part.makeCylinder(1.8,6.2,V(-14,108.9,30),V(0,1,0)))
    replace(m,'RFInsulator',ins,'RCA dielectric around compatible central receptacle')
    contact=Part.makeCylinder(1.75,5,V(-14,109,30),V(0,1,0)).cut(Part.makeCylinder(1.625,5.2,V(-14,108.9,30),V(0,1,0)))
    replace(m,'RFContact',contact,'Estimated RCA spring envelope around 3.2 mm plug pin')
    for i in range(3):
        ex=324-i*16;origin=V(ex,-72.5,11.5);axis=V(0,1,0)
        sleeve=Part.makeCylinder(4.5,5.5,origin,axis).cut(Part.makeCylinder(4.175,5.7,V(ex,-72.6,11.5),axis))
        replace(m,'RCASleeve'+str(i),sleeve,'Compatible RCA sleeve: 9 mm diameter and 5.5 mm exposed length')
        pin=Part.makeCylinder(1.6,8.7,V(ex,-69.3,11.5),axis).fuse(Part.makeSphere(1.6,V(ex,-60.6,11.5))).removeSplitter()
        replace(m,'RCAPin'+str(i),pin,'Compatible RCA 3.20 mm pin with 8 mm projection beyond sleeve')
    refine_graphics(m)
    m.doc.recompute()
    from .sfc import _finish
    _finish(m,22,'original_keyed_interfaces_and_exterior_controls','校正 62 接点卡座的 2.50 mm 节距与分区、左右手柄口及插头的朝向、外侧圈号、POWER 凸起与浅色边框、电源灯位置及兼容 DC/RCA 配合尺寸；照片拟合尺寸与内部结构仍为近似。')


def calibrate_front(m):
    front = g.rotation((0,-1,0),(0,0,1))
    offsets = [-12,-8,-4,0,6,10,14]
    for n,cx in [(1,-34),(2,34)]:
        left = n == 1
        dxs = [-x for x in offsets] if left else offsets
        body = _d_body(cx,-120,18,38.2,9.2,9,left)
        holes = [Part.makeCylinder(1.25,7,V(cx+dx,-120.1,18),V(0,1,0)) for dx in dxs]
        body = body.cut(Part.makeCompound(holes))
        for mid,width in ([(-10,14),(7.5,19)] if left else [(-7.5,19),(10,14)]):
            body=body.cut(m.rr(width,7.8,.65,(cx+mid,-119.45,18),3.2,front))
        obj = replace(m,'ControllerSocket'+str(n),body,'Original handed D-profile: left port three-plus-four, right port four-plus-three')
        obj.MaterialDescription='sfcgray';g.appearance(obj,m.colors['sfcgray'])
        for i,dx in enumerate(dxs):
            key=f'ControllerContact{n}_{i}';old=m.parts[key].Shape.BoundBox.Center.x
            obj=_shift(m,key,(cx+dx-old,0,0),'Mirrored contact bank in original left controller socket')
            obj.MaterialDescription='metal';g.appearance(obj,m.colors['metal'])
        # Raised circled numbers sit outside the sockets, not underneath them.
        target = -64 if left else 64
        key='ControllerNumber'+str(n);old=m.parts[key].Shape.BoundBox
        obj=_shift(m,key,(target-old.Center.x,0,18-old.Center.z),'Outboard raised original port number, fitted to original photograph')
        obj.MaterialDescription='sfcgray';g.appearance(obj,m.colors['sfcgray'])
        ring=Part.makeCylinder(5.2,.08,V(target,-120.94,18),V(0,-1,0)).cut(Part.makeCylinder(4.65,.1,V(target,-120.93,18),V(0,-1,0)))
        if 'ControllerNumberRing'+str(n) in m.parts:replace(m,'ControllerNumberRing'+str(n),ring,'Photograph-fitted outboard port-number surround')
        else:m.feature('ControllerNumberRing'+str(n),'Photograph-fitted raised port-number surround',ring,'FrontPanel',-1,'sfcgray')
        # The detached matching plug is rolled to the corresponding port.
        pcx = -142 if left else 142
        plug = _d_body(pcx,-115.8,12,32,7.5,7,left)
        holes=[Part.makeCylinder(1.3,5,V(pcx+dx,-112.8,12),V(0,1,0)) for dx in dxs]
        replace(m,f'Pad{n}PlugNose',plug.cut(Part.makeCompound(holes)),'Handed original controller-plug nose; local envelope retained')
        for i,dx in enumerate(dxs):
            key=f'Pad{n}PlugContact{i}';old=m.parts[key].Shape.BoundBox.Center.x
            _shift(m,key,(pcx+dx-old,0,0),'Matching seven-contact plug bank for original socket orientation')
    panel=m.rr(148,20,1.1,(0,-119.8,18),9.8,front)
    apertures=[_d_body(cx,-123,18,39,10,6,n==1) for n,cx in [(1,-34),(2,34)]]
    replace(m,'FrontPortPanel',panel.cut(Part.makeCompound(apertures)),'Photo-calibrated 148 mm capsule panel and 68 mm socket centre spacing; estimated dimensions')
    for obj in m.doc.Objects:
        if obj.Label.startswith('Front controller panel aperture · tool'):
            obj.Shape=m.rr(149,21,8,(0,-115,18),9.9,front)


def _fit_xy(shape, x, y, width, height):
    b=shape.BoundBox;matrix=App.Matrix();matrix.A11=width/b.XLength;matrix.A22=height/b.YLength
    matrix.A14=x-matrix.A11*b.XMin;matrix.A24=y-matrix.A22*b.YMin
    fitted=shape.transformGeometry(matrix)
    if len(fitted.Solids)>1:fitted=fitted.Solids[0].multiFuse(fitted.Solids[1:]).removeSplitter()
    fitted.check(True)
    return fitted


def refine_graphics(m):
    for key,x,y,w,h in [('NintendoWord',-69,-91,47,6.9),('SuperFamicomWord',-69,-99,68,4.8)]:
        replace(m,key,_fit_xy(m.parts[key].Shape,x,y,w,h),'Original front wordmark proportions fitted from hardware photograph; glyph outlines remain approximate')
    if 'FourColorSurround' not in m.parts:
        for i in range(4):
            key='FourColorMark'+str(i);s=m.parts[key].Shape.copy();matrix=App.Matrix();matrix.A11=1.35;matrix.A22=1.35;matrix.A14=62-1.35*66;matrix.A24=72-1.35*75
            replace(m,key,s.transformGeometry(matrix),'Photo-fitted original four-color symbol, local outline remains approximate')
        m.ring('FourColorSurround','Photo-fitted circular surround of original four-color mark',12,11.5,.07,(62,72,73.92),'Body',5,'sfcface')
    if 'FlapInstruction' not in m.parts:
        obj=m.label('FlapInstruction','USE CASSETTE WITH SUPER FAMICOM MARK ONLY',2,(0,30,73.92),'CartridgeInterface',5,'white')
        replace(m,'FlapInstruction',_fit_xy(obj.Shape,-44,30,88,1.6),'Original cartridge-flap instruction, fitted typography')
        points=[V(-5,25,73.92),V(0,22.2,73.92),V(5,25,73.92),V(4.5,25.65,73.92),V(0,23.1,73.92),V(-4.5,25.65,73.92)]
        arrow=Part.Face(Part.makePolygon(points+[points[0]])).extrude(V(0,0,.06))
        m.feature('FlapArrow','Original downward cartridge insertion arrow, photograph-fitted',arrow,'CartridgeInterface',5,'sfcbutton')
