GRIP_X=246.0;GRIP_Y=-208.0
box('GripBridge','Joy-Con 2 非充电握把中桥',46,116,15.5,(GRIP_X,GRIP_Y,-1.6),'Grip',0,'shell',1.8)
cut('GripBridge',rr_shape(41.8,111.8,.8,13.0,(GRIP_X,GRIP_Y,-1.5)),'握把中桥内腔')
# Smooth palm supports are bounded to the published 144 × 116 × 40.8 envelope.
sections=[]
for y,rx,rz in [(-58,8,11),(-50,15,16),(-25,18,20.4),(10,20,18),(25,17,13),(34,9,7)]:
    edge=Part.Ellipse(vec(),max(rx,rz),min(rx,rz)).toShape()
    if rz>rx:edge.rotate(vec(),vec(0,0,1),90)
    wire=Part.Wire(edge);wire.rotate(vec(),vec(1,0,0),90);wire.translate(vec(52,y,0));sections.append(wire)
handle=Part.makeLoft(sections,True,False)
handle=handle.fuse(rr_shape(26,16,4,24,(35,25,-12))).removeSplitter()
bb=handle.optimalBoundingBox(False,False);sx=50/(bb.XMax-22);sz=40.8/bb.ZLength
matrix=App.Matrix();matrix.A11=sx;matrix.A33=sz;matrix.A14=22-22*sx;matrix.A34=-bb.Center.z*sz
handle=handle.transformGeometry(matrix);bb=handle.optimalBoundingBox(False,False);handle.translate(vec(0,-58-bb.YMin,0))
for side in [-1,1]:
    h=handle.copy()
    if side<0:h=h.mirror(vec(),vec(1,0,0))
    h.translate(vec(GRIP_X,GRIP_Y,0));feature('GripHandle'+str(side),'握把人体握持柄',h,'Grip',0,'black')
    cut('GripBridge',h,'侧柄与中桥配合座')
    # Passive magnetic receptacles reproduce the controller attachment geometry.
    well=rr_shape(10.4,104,5,4.9,(18.25,0,7.0),XROT)
    liner=rr_shape(9.9,103.5,4.75,.20,(18.35,0,7.0),XROT)
    if side<0:well=well.mirror(vec(),vec(1,0,0));liner=liner.mirror(vec(),vec(1,0,0))
    well.translate(vec(GRIP_X,GRIP_Y,0));liner.translate(vec(GRIP_X,GRIP_Y,0));cut('GripBridge',well,'握把磁吸槽')
    feature('GripLiner'+str(side),'握把磁吸槽彩色内衬',liner,'Grip',0,'blue' if side<0 else 'orange')
    for j,y in enumerate([-27,27]):
        magnet=rr_shape(6.4,18,.9,2.6,(15.6,y,7),XROT)
        if side<0:magnet=magnet.mirror(vec(),vec(1,0,0))
        magnet.translate(vec(GRIP_X,GRIP_Y,0));feature('GripMagnet'+str(side)+'_'+str(j),'握把磁体示意',magnet,'Grip',0,'metal')
    for j in range(4):box(f'GripLight{side}_{j}','握把玩家灯导光窗',1.0,1.25,.13,(GRIP_X+side*20.6,GRIP_Y+6-j*4,13.91),'Grip',1,'white',.12)
official_logo('GripLogo',28,(GRIP_X,GRIP_Y+3,13.882),'Grip',1,'black');cut('GripBridge',C['GripLogo'].Shape,'握把标识嵌入')
# A matching pair of thin open-frame straps with mouse skates and real cord passage.
for side,tag,color in [(-1,'L','blue'),(1,'R','orange')]:
    x=side*125;y=-392;a='Strap'+tag
    frame=rr_shape(16.4,116,7.5,7.0,(x,y,0)).cut(rr_shape(11.2,98,5.5,7.4,(x,y+1.7,-.2)))
    feature(a+'Frame','Joy-Con 2 腕带框架',frame,a,0,color)
    upper=rr_shape(14.4,12.5,5.8,.35,(x,y+50.5,0))
    lower=rr_shape(14.4,14,6.8,.35,(x,y-50.5,0)).cut(rr_shape(8.5,11,4,.5,(x,y-47.2,-.05)))
    feature(a+'UpperSole','腕带上鼠标脚垫',upper,a,1,'black');feature(a+'LowerSole','腕带下鼠标脚垫',lower,a,1,'black')
    cut(a+'Frame',[upper,lower],'鼠标脚垫嵌槽')
    for j in range(4):box(a+'Light'+str(j),'腕带指示灯导光窗',.8,1.20,.10,(x+7.05,y+6-j*4,6.9),a,1,'white',.1)
    points=[(0,-56),(2,-77),(-6,-95),(-30,-105),(-63,-100),(-78,-78),(-78,-20),(-74,30),(-67,43),(-56,43),(-50,30),(-54,-13),(-62,-66),(-52,-91),(-27,-95),(-8,-76)]
    pts=[vec(x+px,y+py,3.5) for px,py in points]
    curve=Part.BSplineCurve();curve.interpolate(Points=pts,PeriodicFlag=True)
    path=Part.Wire(curve.toShape());wire=Part.Wire(Part.makeCircle(.78,pts[0],path.Edges[0].tangentAt(path.Edges[0].FirstParameter)))
    cord=path.makePipeShell([wire],True,True);feature(a+'Cord','腕带闭合织绳示意',cord,a,0,'black')
    cut(a+'Frame',rr_shape(3.2,4.8,1,7.5,(x,y-56.0,-.2)),'腕带穿绳槽')
    lock=Part.makeCylinder(5.0,3.0,vec(x-62,y-66,2.0)).cut(cord)
    feature(a+'CordLock','腕带圆形调节扣',lock,a,0,'rubber')
    # Top keeper joins the two cord sides at the far end of the wrist loop.
    keeper=rr_shape(17,4.5,2,3.0,(x-61.5,y+43,2.0)).cut(cord)
    feature(a+'Keeper','腕带顶端束绳扣',keeper,a,0,'black')
# Verify public accessory envelopes separately from their deliberately free cord paths.
gb=Part.makeCompound([o.Shape for o in C.values() if o.Assembly=='Grip']).optimalBoundingBox(False,False)
RESULT=stage_done(12,'magnetic_grip_and_mouse_straps','完成 144 mm 宽磁吸握把、蓝/橙磁吸槽与玩家灯、两套开口腕带框架、鼠标脚垫、闭合绳路和圆形调节扣。',views=[('grip',{'assemblies':['Grip'],'normal':(-.55,-.3,2),'target':(GRIP_X,GRIP_Y,0),'span':155}),('straps',{'assemblies':['StrapL','StrapR'],'target':(-34,-422,3.5),'span':250,'size':(2200,1400)}),('handheld',{'assemblies':['Tablet','Display','TabletInternal','JoyLeft','JoyRight','JoyMountL','JoyMountR','JoyInternalL','JoyInternalR'],'span':200})],extra={'grip_envelope_mm':[gb.XLength,gb.YLength,gb.ZLength]})
print(json.dumps(RESULT,ensure_ascii=False))
