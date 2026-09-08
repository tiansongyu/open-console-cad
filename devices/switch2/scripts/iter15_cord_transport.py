# Corrected Frenet transport avoids flips at planar B-spline inflections.
for tag,x in [('L',-125),('R',125)]:
    y=-392;a='Strap'+tag
    points=[(0,-56),(2,-77),(-6,-95),(-30,-105),(-63,-100),(-78,-78),(-78,-20),(-74,30),(-67,43),(-56,43),(-50,30),(-54,-13),(-62,-66),(-52,-91),(-27,-95),(-8,-76)]
    pts=[vec(x+px,y+py,3.5) for px,py in points]
    curve=Part.BSplineCurve();curve.interpolate(Points=pts,PeriodicFlag=True)
    path=Part.Wire(curve.toShape());profile=Part.Wire(Part.makeCircle(.78,pts[0],path.Edges[0].tangentAt(path.Edges[0].FirstParameter)))
    cord=path.makePipeShell([profile],True,False)
    assert cord.isValid() and len(cord.Solids)==1
    sections=cord.slice(vec(0,0,1),3.5)
    assert len(sections)==2 and all(w.isClosed() for w in sections)
    C[a+'Cord'].Shape=cord
    current=C[a+'Frame'];base=current.Base;current.PhysicalPart=False;base.PhysicalPart=True;C[a+'Frame']=base
    cut(a+'Frame',cord,'采用稳定随动标架的织绳穿孔')
    C[a+'CordLock'].Shape=Part.makeCylinder(5.0,3.0,vec(x-62,y-66,2.0)).cut(cord)
    C[a+'Keeper'].Shape=rr_shape(17,4.5,2,3.0,(x-61.5,y+43,2.0)).cut(cord)
RESULT=stage_done(15,'stable_cord_sweep','修正周期 B 样条在曲率反转处的扫掠标架，绳圈恢复连续表面，并重做框架、圆扣和束绳扣的穿孔。每根绳在中平面形成两个闭合边界。',views=[('straps',{'assemblies':['StrapL','StrapR'],'target':(-34,-422,3.5),'span':250,'size':(2200,1400)})])
print(json.dumps(RESULT,ensure_ascii=False))
