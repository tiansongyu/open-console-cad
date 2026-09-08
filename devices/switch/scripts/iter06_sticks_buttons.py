STICK_CENTERS={'L':(-103,25.3),'R':(103,-12.0)}
for tag,(x,y) in STICK_CENTERS.items():
    assembly='JoyLeft' if tag=='L' else 'JoyRight'
    cut('Joy'+tag+'Front',Part.makeCylinder(6.35,7.1,vec(x,y,7.3)),'摇杆运动开口')
    ringpart('Joy'+tag+'StickCollar','摇杆周边装饰圈',6.80,6.36,.32,(x,y,13.90),assembly,4,'black')
    ball=Part.makeSphere(6.12,vec(x,y,13.65)).common(Part.makeBox(14,14,5.2,vec(x-7,y-7,11.5)))
    feature('Joy'+tag+'StickBoot','摇杆弧形防尘罩',ball,assembly,4,'black')
    stem=cyl('Joy'+tag+'StickStem','摇杆颈柱',3.10,3.5,(x,y,16.70),assembly,5,'rubber')
    stem.setExpression('Height','Parameters.StickProjection - 5.6 mm')
    cap=Part.makeCylinder(7.90,2.8)
    cap=cap.makeFillet(.5,[e for e in cap.Edges if e.BoundBox.ZLength<1e-7])
    cap=cap.cut(Part.makeSphere(50,vec(0,0,52.25)))
    # Four shallow radial grip grooves around the rim.
    grooves=[]
    for a in [0,90,180,270]:
        tool=Part.makeBox(2.0,.32,.45,vec(6.3,-.16,2.45));tool.rotate(vec(),vec(0,0,1),a);grooves.append(tool)
    cap=cap.cut(Part.makeCompound(grooves))
    o=feature('Joy'+tag+'StickCap','凹面橡胶摇杆帽',cap,assembly,5,'rubber');o.Placement.Base=vec(x,y,20.2)
    o.setExpression('Placement.Base.z','Parameters.BodyDepth + Parameters.StickProjection - 2.8 mm')
# Independent round face buttons and inset symbols.
for tag,cx,cy in [('L',-103,-8.2),('R',103,25.1)]:
    assembly='JoyLeft' if tag=='L' else 'JoyRight';holes=[]
    for j,(dx,dy,char) in enumerate([(0,9.4,'X'),(9.4,0,'A'),(0,-9.4,'B'),(-9.4,0,'Y')]):
        x,y=cx+dx,cy+dy
        holes.append(Part.makeCylinder(3.37,2.0,vec(x,y,12.5)))
        cap=Part.makeCylinder(3.18,2.0,vec(x,y,13.35));cap=cap.makeFillet(.22,[e for e in cap.Edges if e.BoundBox.ZLength<1e-7])
        feature(f'Joy{tag}FaceButton{j}','方向键' if tag=='L' else char+' 键',cap,assembly,5,'black')
        cyl(f'Joy{tag}ButtonStem{j}','按键传力柱',1.1,2.85,(x,y,10.5),assembly,3,'black')
        if tag=='R':textpart('ButtonGlyph'+char,char,2.35,(x-.9,y-1.0,15.36),assembly,5,'white')
        else:
            pts=[vec(-1.0,-.50,0),vec(1.0,-.50,0),vec(0,.90,0),vec(-1.0,-.50,0)]
            sh=Part.Face(Part.makePolygon(pts)).extrude(vec(0,0,.018));sh.rotate(vec(),vec(0,0,1),-j*90);sh.translate(vec(x,y,15.36))
            feature('DpadArrow'+str(j),'方向箭头',sh,assembly,5,'white')
    cut('Joy'+tag+'Front',holes,'面按键孔')
# Minus and plus shaped buttons, each with a matching cutout.
minus=rr_shape(5.4,1.75,.28,1.5,(-92.5,41.1,13.3))
feature('MinusButton','减号按钮',minus,'JoyLeft',5,'black');cut('JoyLFront',rr_shape(5.7,2.05,.35,2,(-92.5,41.1,12.5)),'减号键孔')
plus=rr_shape(5.4,1.70,.20,1.5,(92.5,41.1,13.3)).fuse(rr_shape(1.70,5.4,.20,1.5,(92.5,41.1,13.3))).removeSplitter()
feature('PlusButton','加号按钮',plus,'JoyRight',5,'black')
cut('JoyRFront',[rr_shape(5.7,2.0,.25,2,(92.5,41.1,12.5)),rr_shape(2.0,5.7,.25,2,(92.5,41.1,12.5))],'加号键孔')
# Capture and HOME buttons.
cut('JoyLFront',rr_shape(5.9,5.9,.70,2,(-97.4,-34.5,12.5)),'截图键孔')
box('CaptureButton','截图按钮',5.6,5.6,1.3,(-97.4,-34.5,13.35),'JoyLeft',5,'black',.55)
ringpart('CaptureGlyph','截图符号',1.65,1.24,.018,(-97.4,-34.5,14.66),'JoyLeft',5,'rubber')
cut('JoyRFront',Part.makeCylinder(3.75,2,vec(97.4,-34.5,12.5)),'HOME 键孔')
ringpart('HomeRing','HOME 按键金属圈',3.55,2.88,.55,(97.4,-34.5,13.45),'JoyRight',5,'metal')
cyl('HomeButton','HOME 按钮',2.78,1.15,(97.4,-34.5,13.45),'JoyRight',5,'black')
house=Part.Face(Part.makePolygon([vec(-1.4,-1.2),vec(1.4,-1.2),vec(1.4,.2),vec(0,1.5),vec(-1.4,.2),vec(-1.4,-1.2)])).extrude(vec(0,0,.02))
house=house.cut(Part.makeBox(.65,1.1,.1,vec(-.325,-1.21,-.03)));house.translate(vec(97.4,-34.5,14.62));feature('HomeGlyph','HOME 房屋图标',house,'JoyRight',5,'white')
RESULT=stage_done(6,'analog_and_face_controls','完成双摇杆防尘球罩、可参数联动的颈柱与凹面帽、方向键、ABXY 实体字形、加减号、截图和 HOME 按钮。',views=[('front',{}),('hero',{'normal':(-.35,-.45,2)}),('joycon_detail',{'target':(-103,8,14),'span':105,'size':(1200,1400),'assemblies':['JoyLeft','JoyRailL']})])
