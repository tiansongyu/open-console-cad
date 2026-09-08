for side,tag in [(-1,'L'),(1,'R')]:
    assembly='JoyLeft' if side<0 else 'JoyRight';x=side*103;railassembly='JoyRail'+tag
    # L/R bumpers follow the outside molded contour, with a separate ZL/ZR trigger.
    bumper=joy_outline_shape(32.5,101.5,15.55,1.65,2.4,(x,0,11.4),side).common(Part.makeBox(40,7.9,3,vec(x-20,42.85,11.3)))
    feature('Joy'+tag+'Bumper',tag+' 肩键',bumper,assembly,5,'black')
    bumper_void=joy_outline_shape(32.8,101.8,15.7,1.8,3.0,(x,0,11.1),side).common(Part.makeBox(40,8.3,3.2,vec(x-20,42.6,11.0)))
    cut('Joy'+tag+'Front',bumper_void,'肩键活动间隙')
    trigger=joy_outline_shape(31.6,101.4,15.1,1.4,6.1,(x,0,-5.4),side).common(Part.makeBox(40,14.9,7,vec(x-20,35.8,-5.5)))
    feature('Joy'+tag+'Trigger','Z'+tag+' 扳机',trigger,assembly,-5,'black')
    void=joy_outline_shape(32.0,101.8,15.3,1.6,6.6,(x,0,-5.6),side).common(Part.makeBox(40,15.4,7,vec(x-20,35.5,-5.6)))
    cut('Joy'+tag+'Rear',void,'后扳机活动间隙')
    # Trigger pivots and separate release latch button on the back near the rail.
    cyl('Joy'+tag+'TriggerAxle','扳机转轴',.65,13,(x-6.5,35.4,.65),assembly,-3,'metal',axis=(1,0,0))
    release_x=side*89.3
    cut('Joy'+tag+'Rear',rr_shape(3.7,5.3,1.0,2,(release_x,36.1,-1.45)),'手柄释放键开口')
    box('Joy'+tag+'Release','手柄释放按钮',3.3,4.9,1.5,(release_x,36.1,-2.5),assembly,-5,'black',.85)
    # The inner SL/SR keys sit along the recessed metal rail and are visible detached.
    inward=App.Rotation(vec(0,0,1),vec(-side,0,0))
    for j,y in enumerate([22,-22]):
        # Local width maps to Z; local height remains Y.
        sh=rr_shape(3.1,7.4,.8,.75,(side*84.20,y,7.4),inward)
        feature('Joy'+tag+('SL' if j==0 else 'SR'),'SL 键' if j==0 else 'SR 键',sh,railassembly,0,'blue' if side<0 else 'red')
        cut('Joy'+tag+'RailTongue',rr_shape(3.4,7.7,.9,1.95,(side*83.25,y,7.4),App.Rotation(vec(0,0,1),vec(side,0,0))),'SL/SR 活动孔')
    # Sync button and four player LEDs are individual modeled pieces.
    cyl('Joy'+tag+'Sync','SYNC 配对按钮',1.0,.65,(side*83.65,0,7.4),railassembly,0,'black',axis=(-side,0,0))
    for j in range(4):
        y=-7.5+j*5.0
        box('Joy'+tag+'LED'+str(j+1),'玩家指示灯',.8,1.35,.12,(side*83.45,y,4.25),railassembly,0,'led' if j==0 else 'rubber',.1,orient=inward)
    # Back shell tri-point hardware.
    holes=[]
    for j,(dx,y) in enumerate([(-8.0,-39),(8.0,-26),(-6.5,22),(7.0,28)],1):
        xx=x+dx
        holes.extend([Part.makeCylinder(1.39,.5,vec(xx,y,-1.4)),Part.makeCylinder(.81,1.5,vec(xx,y,-1.4))])
        screw('Joy'+tag+'Screw'+str(j),(xx,y,-1.27),assembly,-4,radius=1.25,length=2.5)
    cut('Joy'+tag+'Rear',holes,'手柄后壳三翼螺钉孔')
    # Shoulder letter markings on the top and back surfaces.
    textpart('BumperLegend'+tag,tag,2.5,(x-1.0,50.78,12.1),assembly,5,'white',YROT)
    textpart('TriggerLegend'+tag,'Z'+tag,2.4,(x+2.2,43.4,-5.42),assembly,-5,'white',App.Rotation(vec(0,1,0),180))
# Right IR camera window at the bottom edge, not present on the left Joy-Con.
cut('JoyRRear',rr_shape(14.8,6.6,1.1,2.6,(103,-51.4,3.1),YROT),'右手柄红外相机窗口')
box('IRWindow','右 Joy-Con 红外透镜窗',14.4,6.2,.68,(103,-51.03,3.1),'JoyRight',-2,'screen',.95,orient=YROT)
# Refine lower/front corners with a restrained edge break in the original CAD shell.
RESULT=stage_done(7,'shoulders_and_rail_controls','完成 L/R 肩键、ZL/ZR 扳机、释放键、SL/SR、SYNC、四灯阵列、后壳螺钉和右手柄红外窗口。',views=[('front',{}),('back',{'normal':(.2,-.4,-2)}),('top',{'normal':(.2,1,.4),'up':(0,0,1),'target':(0,44,5),'span':50,'size':(2200,650)}),('right_ir',{'normal':(.1,-1,-.2),'up':(0,0,1),'target':(103,-50,3),'span':25,'size':(1400,700)})])
