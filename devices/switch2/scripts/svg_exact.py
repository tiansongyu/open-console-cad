"""Convert the official SVG path commands into exact planar FreeCAD edges."""
import math,re,xml.etree.ElementTree as ET

def svg_faces(path):
    wires=[]
    def point(p):return App.Vector(p[0],p[1],0)
    def arc(p0,p1,rx,ry,phi,large,sweep):
        rx,ry=abs(rx),abs(ry)
        if rx<1e-12 or ry<1e-12:return Part.makeLine(point(p0),point(p1))
        phi=math.radians(phi);cp,sp=math.cos(phi),math.sin(phi)
        dx=(p0[0]-p1[0])/2;dy=(p0[1]-p1[1])/2
        xp=cp*dx+sp*dy;yp=-sp*dx+cp*dy;lam=xp*xp/(rx*rx)+yp*yp/(ry*ry)
        if lam>1:rx*=math.sqrt(lam);ry*=math.sqrt(lam)
        denom=rx*rx*yp*yp+ry*ry*xp*xp
        coeff=(-1 if bool(large)==bool(sweep) else 1)*math.sqrt(max(0,(rx*rx*ry*ry-denom)/denom)) if denom>1e-25 else 0
        cxp=coeff*rx*yp/ry;cyp=-coeff*ry*xp/rx
        cx=cp*cxp-sp*cyp+(p0[0]+p1[0])/2;cy=sp*cxp+cp*cyp+(p0[1]+p1[1])/2
        u=((xp-cxp)/rx,(yp-cyp)/ry);v=((-xp-cxp)/rx,(-yp-cyp)/ry)
        start=math.atan2(u[1],u[0]);delta=math.atan2(u[0]*v[1]-u[1]*v[0],u[0]*v[0]+u[1]*v[1])
        if not sweep and delta>0:delta-=2*math.pi
        if sweep and delta<0:delta+=2*math.pi
        angle=phi
        if ry>rx:start-=math.pi/2;angle+=math.pi/2
        start%=2*math.pi
        ellipse=Part.Ellipse(App.Vector(cx,cy,0),max(rx,ry),min(rx,ry))
        if delta>0:edge=Part.ArcOfEllipse(ellipse,start,start+delta).toShape()
        else:edge=Part.ArcOfEllipse(ellipse,start+delta,start).toShape();edge.reverse()
        edge.rotate(App.Vector(cx,cy,0),App.Vector(0,0,1),math.degrees(angle));return edge
    for node in ET.parse(path).getroot().iter():
        if not node.tag.endswith('path'):continue
        tokens=re.findall(r'[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?',node.get('d',''));i=0;cmd=None;current=(0.,0.);start=current;edges=[]
        def finish():
            nonlocal edges
            if edges:
                if math.dist(current,start)>1e-8:edges.append(Part.makeLine(point(current),point(start)))
                wires.append(Part.Wire(edges));edges=[]
        while i<len(tokens):
            if tokens[i].isalpha():cmd=tokens[i];i+=1
            op=cmd.upper();relative=cmd.islower()
            if op=='Z':
                if math.dist(current,start)>1e-9:edges.append(Part.makeLine(point(current),point(start)))
                current=start;finish();cmd=None;continue
            sizes={'M':2,'L':2,'H':1,'V':1,'C':6,'A':7};count=sizes[op];values=[float(x) for x in tokens[i:i+count]];i+=count
            def absolute(x,y):return(x+current[0],y+current[1]) if relative else(x,y)
            if op=='M':
                if edges:finish()
                current=absolute(*values);start=current;cmd='l' if relative else 'L';continue
            if op=='L':end=absolute(*values);edge=Part.makeLine(point(current),point(end)) if math.dist(current,end)>1e-9 else None
            elif op=='H':end=(values[0]+current[0] if relative else values[0],current[1]);edge=Part.makeLine(point(current),point(end)) if math.dist(current,end)>1e-9 else None
            elif op=='V':end=(current[0],values[0]+current[1] if relative else values[0]);edge=Part.makeLine(point(current),point(end)) if math.dist(current,end)>1e-9 else None
            elif op=='C':
                p1=absolute(*values[:2]);p2=absolute(*values[2:4]);end=absolute(*values[4:]);curve=Part.BezierCurve();curve.setPoles([point(current),point(p1),point(p2),point(end)]);edge=curve.toShape()
            elif op=='A':
                end=absolute(*values[5:]);edge=arc(current,end,*values[:5]) if math.dist(current,end)>1e-9 else None
            if edge:edges.append(edge)
            current=end
        finish()
    assert wires and all(w.isClosed() for w in wires),('Open SVG subpath',[(i,len(w.Edges),w.Vertexes[0].Point,w.Vertexes[-1].Point) for i,w in enumerate(wires) if not w.isClosed()])
    face=Part.makeFace(wires,'Part::FaceMakerBullseye')
    assert face.isValid()
    # Rounded SVG endpoints can leave sub-pixel zero-area slivers after even-odd filling.
    face=Part.makeCompound([f for f in face.Faces if f.Area>1e-4])
    face=face.mirror(App.Vector(),App.Vector(0,1,0))
    return face
