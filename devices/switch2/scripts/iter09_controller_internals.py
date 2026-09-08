for side,tag,color in [(-1,'L','blue'),(1,'R','orange')]:
    a='JoyInternal'+tag;x=side*117.5;sx,sy=STICK_CENTERS[tag]
    pcb=joy_outline_shape(29,100,23.8,.6,.80,(x,0,9.30),side).cut(Part.makeCylinder(9.45,1.2,vec(sx,sy,9.1)))
    feature('Joy'+tag+'PCB','Joy-Con 2 主板',pcb,a,1,'pcb',True)
    box('Joy'+tag+'Battery','500 mAh 手柄电池',22.4,46,4.35,(x,-4.5,0.0),a,-2,'battery',1.6,True)
    textpart('Joy'+tag+'BatteryMark','500 mAh',2.2,(x+8.3,-1.5,-.018),a,-2,'white',BACKROT)
    textpart('Joy'+tag+'BatteryNote','LAYOUT STUDY',1.3,(x+8.5,-8,-.018),a,-2,'white',BACKROT)
    tray=rr_shape(24.8,49,2,.50,(x,-4.5,4.60)).cut(rr_shape(20,42,1.2,.8,(x,-4.5,4.45)))
    feature('Joy'+tag+'BatteryCradle','手柄电池托架',tray,a,-1,'black',True)
    # Larger circular gimbal carrier with crossed axes and potentiometer modules.
    ringpart('Joy'+tag+'GimbalHousing','加大摇杆塑料框架',9.0,7.7,4.4,(sx,sy,6.6),a,2,color,internal=True)
    ringpart('Joy'+tag+'GimbalRing','摇杆内转环',6.2,4.7,.90,(sx,sy,8.4),a,2,'black',internal=True)
    cyl('Joy'+tag+'GimbalX','摇杆横轴',.55,13.8,(sx-6.9,sy,7.8),a,2,'metal',axis=(1,0,0),internal=True)
    for j,yy in enumerate([sy-6.9,sy+.8]):cyl('Joy'+tag+'GimbalY'+str(j),'摇杆纵向半轴',.55,6.1,(sx,yy,7.8),a,2,'metal',axis=(0,1,0),internal=True)
    for j,(dx,dy,w,h) in enumerate([(10.4,0,2.0,9.6),(0,10.4,9.6,2.0)]):box('Joy'+tag+'Pot'+str(j),'位置电位器示意',w,h,2.0,(sx+dx,sy+dy,7.0),a,2,'rubber',.35,True)
    cy=-1.0 if tag=='L' else 29.3
    for j,(dx,dy) in enumerate([(0,10.8),(10.8,0),(0,-10.8),(-10.8,0)]):
        xx,yy=side*118+dx,cy+dy
        cyl(f'Joy{tag}ButtonPad{j}','面按键金接点',2.80,.06,(xx,yy,10.15),a,2,'gold',internal=True)
        dome=Part.makeSphere(6.4,vec(xx,yy,4.20)).common(Part.makeCylinder(2.55,.34,vec(xx,yy,10.24)))
        feature(f'Joy{tag}ButtonDome{j}','按键金属弹片',dome,a,2,'metal',True)
    box('Joy'+tag+'WirelessIC','手柄无线控制封装',6.0,7.0,.95,(side*112,-37,8.30),a,1,'black',.25,True)
    for j in range(10):box('Joy'+tag+'Passive'+str(j),'手柄阻容器件',1.1,1.4,.48,(x-8.5+(j%5)*3.2,-29-(j//5)*3.0,8.78),a,1,'rubber',.035,True)
    # HD rumble 2: metal can, separate cover, moving mass, coil and leaf springs.
    hx=side*113;hy=-42
    box('Joy'+tag+'HapticCase','HD Rumble 2 金属壳',18,15,5.0,(hx,hy,.20),a,-2,'metal',.9,True)
    cut('Joy'+tag+'HapticCase',rr_shape(16.8,13.8,.55,5.0,(hx,hy,.55)),'振动模块开腔')
    box('Joy'+tag+'HapticLid','振动单元盖板',18,15,.30,(hx,hy,5.30),a,-1,'metal',.9,True)
    box('Joy'+tag+'HapticMass','振动配重',12.8,5.4,3.1,(hx,-45,1.0),a,-2,'rubber',.55,True)
    helix=Part.makeHelix(.50,12.0,1.40);wire=Part.Wire(Part.makeCircle(.10,helix.Vertexes[0].Point,helix.Edges[0].tangentAt(helix.Edges[0].FirstParameter)))
    coil=Part.Wire(helix.Edges).makePipeShell([wire],True,True);coil.rotate(vec(),vec(0,1,0),90);coil.translate(vec(hx-6,-39.1,2.85))
    feature('Joy'+tag+'HapticCoil','连续铜绕组示意',coil,a,-2,'copper',True)
    for j,dx in enumerate([-7.25,7.25]):box('Joy'+tag+'HapticSpring'+str(j),'振动悬置簧片',.15,12.0,3.4,(hx+dx,hy,.90),a,-2,'metal',.02,True)
    # Optical mouse sensor module lies directly behind its window in the colored spine.
    def mirrored(s):return s.mirror(vec(),vec(1,0,0)) if side<0 else s
    cavity=rr_shape(4.5,6.4,.6,3.8,(95.05,12.2,7),XROT)
    cut('Joy'+tag+'MagneticSpine',mirrored(cavity),'鼠标镜头与小板容置槽')
    board=rr_shape(4.2,6.0,.4,.65,(98.0,12.2,7),XROT);feature('Joy'+tag+'MousePCB','光学鼠标感应小板',mirrored(board),a,0,'pcb',True)
    chip=rr_shape(3.6,3.8,.35,1.1,(96.8,12.2,7),XROT);feature('Joy'+tag+'MouseSensor','鼠标光电传感器',mirrored(chip),a,0,'black',True)
    lens=Part.makeCylinder(1.15,1.3,vec(95.4,12.2,7),vec(1,0,0));feature('Joy'+tag+'MouseLens','鼠标光学透镜',mirrored(lens),a,0,'screen',True)
    # Release lever and colored rib interconnect are mechanically separate parts.
    box('Joy'+tag+'ReleaseLever','磁吸分离传力杆',3.2,17.0,1.1,(side*104.7,34.5,2.0),a,-2,'black',.65,True)
    box('Joy'+tag+'SpineFlex','连接脊与主板软排线',3,45,.12,(side*102.8,4,8.25),a,0,'copper',.4,True)
    box('Joy'+tag+'HapticFlex','振动单元软排线',4.5,8,.10,(hx,-30.5,6.3),a,-1,'copper',.2,True)
    for j,yy in enumerate([47,-50]):ringpart('Joy'+tag+'RearBoss'+str(j),'手柄后壳螺钉柱',1.35,.83,3.2,(side*104,yy,-.75),a,-3,'shell',internal=True)
# Right controller NFC loop, modeled as a continuous 4-turn planar conductor.
pts=[]
for j in range(301):
    angle=2*math.pi*4*j/300;radius=9.2-2.4*j/300;pts.append(vec(118+radius*math.cos(angle),radius*math.sin(angle),5.7))
curve=Part.BSplineCurve();curve.interpolate(pts);path=Part.Wire(curve.toShape());profile=Part.Wire(Part.makeCircle(.07,pts[0],path.Edges[0].tangentAt(path.Edges[0].FirstParameter)))
feature('JoyRNFCAntenna','右 Joy-Con 2 NFC 天线示意',path.makePipeShell([profile],True,True),'JoyInternalR',0,'copper',True)
RESULT=stage_done(9,'joycon2_internal_mechanisms','加入 500 mAh 手柄电池、主板与触点、圆形摇杆框架、电位器、HD Rumble 2 绕组与配重、鼠标传感器小板及右手柄 NFC 天线。',views=[('all_internal',{'normal':(0,0,-1),'span':200,'exclude':['TabletRear','Kickstand','StandFoot-1','StandFoot1','RearNintendoMark','RearModelMark','RearEMIShield','JoyLRear','JoyRRear']}),('joy_internal',{'normal':(.3,-.15,-1),'target':(116,0,5),'span':138,'size':(1200,1500),'assemblies':['JoyRight','JoyMountR','JoyInternalR'],'exclude':['JoyRRear','JoyRHapticLid']}),('front',{'span':200})])
print(json.dumps(RESULT,ensure_ascii=False))
