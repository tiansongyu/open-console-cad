for side,tag,color in [(-1,'L','blue'),(1,'R','orange')]:
    assembly='JoyLeft' if side<0 else 'JoyRight';mount='JoyMount'+tag;x=side*117.5
    def mirrored(shape):return shape.mirror(vec(),vec(1,0,0)) if side<0 else shape
    shoulder=joy_outline_shape(36.8,115.8,28.9,1.7,1.65,(x,0,12.30),side).cut(joy_outline_shape(32.8,111.8,26.9,.6,2.0,(x,0,12.1),side))
    shoulder=shoulder.common(Part.makeBox(40,30,3,vec(x-20,28,12.0)))
    shoulder=shoulder.cut(Part.makeBox(3,31,3,vec(99 if side>0 else -102,27.5,12.0)))
    feature('Joy'+tag+'Bumper',tag+' 弧形肩键',shoulder,assembly,5,'black');cut('Joy'+tag+'Front',shoulder,'肩键安装轮廓')
    trigger=joy_outline_shape(35.4,115.4,28.0,1.4,6.2,(x,0,-6.0),side).common(Part.makeBox(40,24,7,vec(x-20,34,-6.1)))
    feature('Joy'+tag+'Trigger','Z'+tag+' 后扳机',trigger,assembly,-5,'black');cut('Joy'+tag+'Rear',trigger,'后扳机容置区')
    cyl('Joy'+tag+'TriggerPin','扳机支承销',.65,12.0,(x-6,34.1,1.30),assembly,-3,'metal',axis=(1,0,0))
    box('Joy'+tag+'Release','磁吸手柄释放键',7.7,6.2,1.65,(side*104.7,40.8,-3.50),assembly,-5,'black',1.65)
    cut('Joy'+tag+'Rear',rr_shape(8.0,6.5,1.8,2.2,(side*104.7,40.8,-3.65)),'释放键孔')
    cut('Joy'+tag+'Trigger',rr_shape(8.0,6.5,1.8,2.3,(side*104.7,40.8,-3.70)),'释放键与扳机避让')
    for j,y in enumerate([40.8,29.2]):
        pad=rr_shape(3.5,4.2,1.0,.75,(94.65,y,7.0),XROT)
        feature('Joy'+tag+'Ejector'+str(j),'磁吸分离顶脚',mirrored(pad),mount,0,'black')
        cut('Joy'+tag+'MagneticSpine',mirrored(rr_shape(3.7,4.4,1.1,1.1,(94.45,y,7.0),XROT)),'顶脚滑动孔')
    for j,y in enumerate([28.0,-29.0]):
        shape=rr_shape(5.9,20.4,1.5,1.3,(94.66,y,7.0),XROT)
        feature('Joy'+tag+('SL' if j==0 else 'SR'),'SL 侧键' if j==0 else 'SR 侧键',mirrored(shape),mount,0,color)
        cut('Joy'+tag+'MagneticSpine',mirrored(rr_shape(6.2,20.7,1.6,1.6,(94.45,y,7.0),XROT)),'侧键活动孔')
    sensor=rr_shape(4.0,4.5,.75,.5,(94.64,12.2,7.0),XROT)
    feature('Joy'+tag+'MouseWindow','光学鼠标窗口',mirrored(sensor),mount,0,'screen')
    cut('Joy'+tag+'MagneticSpine',mirrored(rr_shape(4.3,4.8,.9,.85,(94.45,12.2,7.0),XROT)),'鼠标感应窗孔')
    feature('Joy'+tag+'Sync','SYNC 同步键',mirrored(Part.makeCylinder(1.25,.85,vec(94.65,-13.0,7.0),vec(1,0,0))),mount,0,color)
    cut('Joy'+tag+'MagneticSpine',mirrored(Part.makeCylinder(1.4,1.2,vec(94.45,-13,7),vec(1,0,0))),'同步键活动孔')
    for j,y in enumerate([47.0,-47.0]):
        skate=rr_shape(7.2,7.4,3.4,.20,(94.60,y,7.0),XROT)
        feature('Joy'+tag+'MouseSkate'+str(j),'鼠标滑动脚垫',mirrored(skate),mount,0,color)
        cut('Joy'+tag+'MagneticSpine',mirrored(rr_shape(7.35,7.55,3.45,.35,(94.5,y,7.0),XROT)),'鼠标脚垫嵌入位')
    for j in range(4):
        yy=6-j*4.0;shape=Part.makeBox(1.2,1.25,.18,vec(97.0,yy-.625,11.93))
        feature('Joy'+tag+'LED'+str(j+1),'玩家指示灯',mirrored(shape),mount,1,'led' if j==0 else 'rubber')
    holes=[]
    for j,y in enumerate([47.0,-50.0]):
        xx=side*104.0;holes.extend([Part.makeCylinder(1.35,.55,vec(xx,y,-2.0)),Part.makeCylinder(.82,1.4,vec(xx,y,-2.0))]);screw('Joy'+tag+'Screw'+str(j),(xx,y,-1.86),assembly,-4,radius=1.20,length=3.0)
    cut('Joy'+tag+'Rear',holes,'手柄后壳三翼螺钉孔')
    textpart('TriggerLegend'+tag,'Z'+tag,2.5,(x+2.3,42,-5.988),assembly,-5,'rubber',BACKROT);cut('Joy'+tag+'Trigger',C['TriggerLegend'+tag].Shape,'扳机标记凹嵌')
RESULT=stage_done(7,'mouse_sensors_and_release','完成弧形 L/R 肩键、后扳机、磁吸释放键与顶脚、SL/SR、光学鼠标窗、滑动脚垫、玩家灯及后壳紧固件。',views=[('front',{'span':200}),('back',{'normal':(.3,-.2,-2),'span':200}),('inner_side',{'normal':(1,0,0),'target':(-114,0,9),'span':135,'size':(1100,1400),'assemblies':['JoyLeft','JoyMountL']})])
print(json.dumps(RESULT,ensure_ascii=False))
