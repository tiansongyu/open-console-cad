STICK_CENTERS={'L':(-118,29.0),'R':(118,0.0)}
for tag,(x,y) in STICK_CENTERS.items():
    assembly='JoyLeft' if tag=='L' else 'JoyRight';color='blue' if tag=='L' else 'orange'
    cut('Joy'+tag+'Front',Part.makeCylinder(6.65,7.2,vec(x,y,7.1)),'摇杆运动孔')
    ringpart('Joy'+tag+'StickAccent','摇杆彩色装饰圈',7.30,6.66,.26,(x,y,13.90),assembly,4,color)
    ball=Part.makeSphere(6.45,vec(x,y,13.6)).common(Part.makeBox(14,14,6.5,vec(x-7,y-7,10.8)))
    feature('Joy'+tag+'StickBoot','摇杆防尘球罩',ball,assembly,4,'black')
    stem=cyl('Joy'+tag+'StickStem','加大摇杆颈柱',3.35,4.3,(x,y,17.3),assembly,5,'black');stem.setExpression('Height','Parameters.StickProjection - 6.5 mm')
    cap=Part.makeCylinder(8.55,3.1);cap=cap.makeFillet(.45,[e for e in cap.Edges if e.BoundBox.ZLength<1e-7]);cap=cap.cut(Part.makeSphere(45,vec(0,0,47.4)))
    cutters=[]
    for a in [0,90,180,270]:
        t=Part.makeBox(1.6,.32,.45,vec(7.25,-.16,2.75));t.rotate(vec(),vec(0,0,1),a);cutters.append(t)
    cap=cap.cut(Part.makeCompound(cutters));o=feature('Joy'+tag+'StickCap','大尺寸凹面摇杆帽',cap,assembly,5,'rubber');o.Placement.Base=vec(x,y,21.6);o.setExpression('Placement.Base.z','Parameters.BodyDepth + Parameters.StickProjection - 3.1 mm')
for tag,cx,cy in [('L',-118,-1.0),('R',118,29.3)]:
    assembly='JoyLeft' if tag=='L' else 'JoyRight';holes=[]
    for j,(dx,dy,char) in enumerate([(0,10.8,'X'),(10.8,0,'A'),(0,-10.8,'B'),(-10.8,0,'Y')]):
        x,y=cx+dx,cy+dy;holes.append(Part.makeCylinder(3.85,2.2,vec(x,y,12.2)))
        cap=Part.makeCylinder(3.70,1.85,vec(x,y,13.45));cap=cap.makeFillet(.20,[e for e in cap.Edges if e.BoundBox.ZLength<1e-7])
        feature(f'Joy{tag}FaceButton{j}','方向按键' if tag=='L' else char+' 按键',cap,assembly,5,'black')
        cyl(f'Joy{tag}ButtonStem{j}','按键传力柱',1.1,2.6,(x,y,10.85),assembly,3,'black')
        if tag=='R':textpart('Glyph'+char,char,2.7,(x-1.05,y-1.15,15.312),assembly,5,'white')
        else:
            tri=Part.Face(Part.makePolygon([vec(-1.1,-.55),vec(1.1,-.55),vec(0,1.0),vec(-1.1,-.55)])).extrude(vec(0,0,.016));tri.rotate(vec(),vec(0,0,1),-j*90);tri.translate(vec(x,y,15.312));feature('Arrow'+str(j),'方向箭头',tri,assembly,5,'white')
    cut('Joy'+tag+'Front',holes,'方向/ABXY 按键孔')
feature('MinusButton','减号按键',rr_shape(5.8,1.75,.25,1.5,(-105.5,45.2,13.4)),'JoyLeft',5,'black')
cut('JoyLFront',rr_shape(6.1,2.05,.35,2,(-105.5,45.2,12.4)),'减号孔')
plus=rr_shape(5.8,1.75,.2,1.5,(105.5,45.2,13.4)).fuse(rr_shape(1.75,5.8,.2,1.5,(105.5,45.2,13.4))).removeSplitter();feature('PlusButton','加号按键',plus,'JoyRight',5,'black')
cut('JoyRFront',[rr_shape(6.1,2.05,.3,2,(105.5,45.2,12.4)),rr_shape(2.05,6.1,.3,2,(105.5,45.2,12.4))],'加号孔')
box('CaptureButton','截图键',6.0,6.0,1.4,(-109.2,-21.5,13.4),'JoyLeft',5,'black',.7)
cut('JoyLFront',rr_shape(6.3,6.3,.85,2,(-109.2,-21.5,12.4)),'截图键孔')
ringpart('CaptureGlyph','截图键圆圈标记',1.8,1.4,.018,(-109.2,-21.5,14.818),'JoyLeft',5,'rubber')
cyl('HomeButton','HOME 按钮',3.45,1.4,(109.2,-21.5,13.4),'JoyRight',5,'black')
cut('JoyRFront',Part.makeCylinder(3.60,2,vec(109.2,-21.5,12.4)),'HOME 键孔')
house=Part.Face(Part.makePolygon([vec(-1.45,-1.2),vec(1.45,-1.2),vec(1.45,.2),vec(0,1.5),vec(-1.45,.2),vec(-1.45,-1.2)])).extrude(vec(0,0,.018));house=house.cut(Part.makeBox(.65,1.05,.1,vec(-.325,-1.22,-.02)));house.translate(vec(109.2,-21.5,14.82));feature('HomeGlyph','HOME 房屋标记',house,'JoyRight',5,'white')
box('CButton','C 聊天键',5.8,5.8,1.4,(109.2,-34.0,13.4),'JoyRight',5,'black',.7)
cut('JoyRFront',rr_shape(6.1,6.1,.85,2,(109.2,-34.0,12.4)),'C 聊天键孔')
textpart('CGlyph','C',3.0,(108.1,-35.2,14.818),'JoyRight',5,'white')
RESULT=stage_done(6,'sticks_buttons_and_c_key','完成加大摇杆及蓝/橙饰圈、方向键、ABXY、加减号、截图、HOME 和方形 C 键，摇杆伸出量可参数联动。',views=[('front',{'span':200}),('hero',{'normal':(-.4,-.4,2),'span':200}),('right_controls',{'assemblies':['JoyRight','JoyMountR'],'target':(117.5,0,10),'span':138,'size':(1100,1400)})])
print(json.dumps(RESULT,ensure_ascii=False))
