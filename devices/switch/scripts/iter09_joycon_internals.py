for side,tag in [(-1,'L'),(1,'R')]:
    assembly='JoyInternal'+tag;x=side*103;stick_y=STICK_CENTERS[tag][1]
    # Small controller PCB with a large mechanical opening for its analog gimbal.
    pcb=joy_outline_shape(27.8,93.4,13.2,.7,.75,(x,0,9.45),side)
    pcb=pcb.cut(rr_shape(17.4,17.4,1.1,1.2,(x,stick_y,9.2)))
    feature('Joy'+tag+'PCB','Joy-Con '+tag+' · 主控 PCB',pcb,assembly,1,'pcb',True)
    box('Joy'+tag+'Battery','Joy-Con '+tag+' · 525 mAh 电池',23.0,40.0,4.2,(x,-.5,.05),assembly,-2,'battery',1.5,True)
    textpart('Joy'+tag+'BatteryMark','525 mAh',2.1,(x+8,2.5,.025),assembly,-2,'white',BACKROT)
    textpart('Joy'+tag+'BatteryNote','CAD STUDY',1.35,(x+8,-4,.025),assembly,-2,'white',BACKROT)
    tray=rr_shape(25.2,44.0,1.8,.50,(x,-.5,4.5)).cut(rr_shape(19.0,32.0,1.3,.8,(x,-.5,4.35)))
    feature('Joy'+tag+'BatteryCradle','电池固定托架',tray,assembly,-1,'black',True)
    # Gimbal housing, crossed axes, centering spring and resistive sensor blocks.
    box('Joy'+tag+'GimbalHousing','摇杆金属万向架',16.6,16.6,4.2,(x,stick_y,7.05),assembly,2,'metal',1.0,True)
    cut('Joy'+tag+'GimbalHousing',rr_shape(14.5,14.5,.65,4.5,(x,stick_y,6.95)),'万向架中空')
    ringpart('Joy'+tag+'GimbalRing','摇杆旋转环',6.2,4.2,1.0,(x,stick_y,8.8),assembly,2,'black',internal=True)
    cyl('Joy'+tag+'GimbalX','摇杆 X 轴',.55,13.4,(x-6.7,stick_y,8.3),assembly,2,'metal',axis=(1,0,0),internal=True)
    # Y pivot is split around the crossing X axis; the axes do not occupy the same volume.
    for j,yy in enumerate([stick_y-6.7,stick_y+.9]):cyl('Joy'+tag+'GimbalY'+str(j),'摇杆 Y 半轴',.55,5.8,(x,yy,8.3),assembly,2,'metal',axis=(0,1,0),internal=True)
    for j,(dx,dy) in enumerate([(9,0),(0,9)]):box('Joy'+tag+'Pot'+str(j),'摇杆位置电位器示意',2.0 if j==0 else 10.0,10.0 if j==0 else 2.0,2.0,(x+dx,stick_y+dy,7.2),assembly,2,'rubber',.3,True)
    # Four tactile domes aligned with the visible directional or ABXY button stems.
    cy=-8.2 if tag=='L' else 25.1
    for j,(dx,dy) in enumerate([(0,9.4),(9.4,0),(0,-9.4),(-9.4,0)]):
        xx,yy=x+dx,cy+dy
        cyl(f'Joy{tag}ButtonPad{j}','按键 PCB 镀金圆盘',2.45,.06,(xx,yy,10.16),assembly,2,'gold',internal=True)
        dome=Part.makeSphere(6,vec(xx,yy,4.72)).common(Part.makeCylinder(2.20,.33,vec(xx,yy,10.22)))
        feature(f'Joy{tag}ButtonDome{j}','金属弹片触点',dome,assembly,2,'metal',True)
    box('Joy'+tag+'WirelessIC','无线控制器封装',6.0,6.0,.90,(x+side*6,-25,8.45),assembly,1,'black',.25,True)
    for j in range(12):box('Joy'+tag+'Passive'+str(j+1),'手柄 PCB 阻容器件',.9,1.5,.5,(x-9+(j%6)*3.3,-28-(j//6)*3,8.90),assembly,1,'rubber',.03,True)
    # HD rumble unit with open shell, moving mass, continuous helical coil and leaf springs.
    y=-37.5
    box('Joy'+tag+'HapticCase','HD Rumble 金属壳',19.0,11.8,5.4,(x,y,1.1),assembly,-2,'metal',1.0,True)
    cut('Joy'+tag+'HapticCase',rr_shape(17.6,10.4,.65,5.3,(x,y,.9)),'振动单元内腔')
    box('Joy'+tag+'HapticMass','振动配重',12.8,4.0,3.1,(x,y-2.0,2.1),assembly,-2,'rubber',.5,True)
    helix=Part.makeHelix(.35,14.0,1.6)
    tangent=helix.Edges[0].tangentAt(helix.Edges[0].FirstParameter)
    wire=Part.Wire(Part.makeCircle(.105,helix.Vertexes[0].Point,tangent))
    coil=Part.Wire(helix.Edges).makePipeShell([wire],True,True)
    coil.rotate(vec(),vec(0,1,0),90);coil.translate(vec(x-7.0,y+2.4,3.8))
    feature('Joy'+tag+'HapticCoil','HD Rumble 连续铜绕组',coil,assembly,-2,'copper',True)
    for j,dx in enumerate([-7.7,7.7]):box('Joy'+tag+'HapticSpring'+str(j),'振动悬置簧片',.22,7.6,3.6,(x+dx,y,1.9),assembly,-2,'metal',.02,True)
    # Ribbon interconnect follows the inner wall clear of the battery and gimbal.
    box('Joy'+tag+'RailFlex','导轨与主板排线',1.6,55,.10,(x-side*12.8,-4,8.20),assembly,0,'copper',.15,True)
    box('Joy'+tag+'HapticFlex','振动模块排线',4.0,8.0,.10,(x,-29,6.7),assembly,-1,'copper',.15,True)
    for j,(dx,yy) in enumerate([(-8,-39),(8,-26),(-6.5,22),(7,28)]):
        ringpart('Joy'+tag+'Boss'+str(j),'手柄后盖螺钉柱',1.4,.80,2.8,(x+dx,yy,-.22),assembly,-3,'shell',internal=True)
# NFC antenna on the right controller: a continuous planar four-turn trace.
pts=[]
for j in range(721):
    a=math.pi*2*4*j/720;r=10.0-3.0*j/720;pts.append(vec(103+r*math.cos(a),-12+r*math.sin(a),5.4))
curve=Part.BSplineCurve();curve.interpolate(pts);path=Part.Wire(curve.toShape());profile=Part.Wire(Part.makeCircle(.08,pts[0],path.Edges[0].tangentAt(path.Edges[0].FirstParameter)))
feature('JoyRNFCAntenna','右手柄 NFC 四匝天线',path.makePipeShell([profile],True,True),'JoyInternalR',0,'copper',True)
box('IRCameraPCB','红外相机小板',13.2,7.0,.65,(103,-45,6.5),'JoyInternalR',-1,'pcb',.4,True)
box('IRCameraSensor','红外传感器封装',5,5,2.0,(103,-46,3.9),'JoyInternalR',-2,'black',.3,True)
cyl('IRCameraLens','红外成像透镜',1.65,2.5,(103,-49.9,3.1),'JoyInternalR',-2,'screen',axis=(0,1,0),internal=True)
RESULT=stage_done(9,'joycon_internal_mechanisms','加入手柄电池与托架、镂空 PCB、万向架、交叉转轴和电位器、按键弹片、连续绕线的 HD Rumble、NFC 天线与 IR 相机模块。',views=[('controller_internals',{'normal':(0,0,-1),'exclude':['TabletRear','Kickstand','StandFoot','RearNintendoMark','RearModelMark','RearEMIShield','JoyLRear','JoyRRear']}),('left_internal',{'normal':(.2,-.15,-1),'target':(-103,0,5),'span':112,'size':(1200,1400),'assemblies':['JoyLeft','JoyRailL','JoyInternalL'],'exclude':['JoyLRear']}),('front',{})])
