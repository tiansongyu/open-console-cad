for obj in D.Objects:
    if '镁合金' in obj.Label:obj.Label=obj.Label.replace('镁合金','金属')
# Top: capsule power/volume keys, brightness sensor, three exhaust mouths, upper USB-C, audio, card and mic.
openings=[rr_shape(7.0,4.0,1.8,3.0,(-81,56,7.1),YROT),rr_shape(15.8,3.8,1.7,3,(-66.4,56,7.1),YROT),Part.makeCylinder(1.65,3,vec(-41.4,56,7.1),vec(0,1,0)),Part.makeCylinder(2.62,3,vec(50.2,56,7.1),vec(0,1,0)),rr_shape(26,8.3,1.8,3,(69.2,56,7.1),YROT),rr_shape(.9,2.5,.4,3,(87.0,56,7.1),YROT)]
for j,x in enumerate([-12.2,4.6,21.4]):openings.append(rr_shape(15.0,4.7,2.15,3,(x,56,7.1),YROT))
cut('TabletFrame',openings,'Switch 2 顶部接口与排风口')
box('PowerButton','电源胶囊按键',6.65,3.65,1.1,(-81,56.85,7.1),'Tablet',1,'black',1.65,orient=YROT)
box('VolumeRocker','音量按键',15.4,3.45,1.1,(-66.4,56.85,7.1),'Tablet',1,'black',1.5,orient=YROT)
for x,char in [(-70.8,'-'),(-61.9,'+')]:textpart('VolumeGlyph'+str(x).replace('-','N').replace('.','_'),char,2.0,(x-.65,57.967,8.0),'Tablet',1,'white',YROT)
cyl('BrightnessSensor','顶部亮度感应窗',1.5,.6,(-41.4,57.3,7.1),'Tablet',1,'screen',axis=(0,1,0))
ringpart('HeadphoneRim','3.5 mm 耳机麦克风插座',2.40,1.76,5.8,(50.2,52.0,7.1),'Tablet',1,'black',axis=(0,1,0))
ringpart('HeadphoneContact','四极耳机插座接触环',1.74,1.58,1.0,(50.2,52.2,7.1),'Tablet',1,'gold',axis=(0,1,0))
box('GameCardLid','游戏卡防尘盖',25.6,7.9,1.1,(69.2,56.8,7.1),'Tablet',1,'shell',1.6,orient=YROT)
textpart('GameCardLegend','GAME CARD',1.75,(58.0,57.92,8.0),'Tablet',1,'black',YROT)
box('MicrophoneMesh','顶部麦克风网',.66,2.15,.2,(87,57.5,7.1),'Tablet',1,'black',.3,orient=YROT)
for j,x in enumerate([-12.2,4.6,21.4]):
    mesh=rr_shape(14.6,4.3,2.0,.22,(x,57.05,7.1),YROT)
    cuts=[rr_shape(.28,3.5,.1,.4,(x-6.2+k*.57,56.95,7.1),YROT) for k in range(23)]
    feature('ExhaustMesh'+str(j+1),'顶部金属排风格栅',mesh.cut(Part.makeCompound(cuts)),'Tablet',1,'black')
# Both USB-C sockets have separate metal shells, tongues and twenty-four contact strips.
for label,x,y,normal in [('Upper',37.8,57.85,(0,-1,0)),('Lower',0,-57.85,(0,1,0))]:
    orient=App.Rotation(vec(0,0,1),vec(*normal));outward=vec(x,y,6.95)-vec(*normal)*.35
    cut('TabletFrame',rr_shape(9.25,3.65,1.65,5.7,tuple(outward),orient),'USB-C 开口 '+label)
    metal=rr_shape(8.8,3.2,1.45,5.4,(x,y,6.95),orient).cut(rr_shape(8.18,2.58,1.20,5.8,tuple(outward),orient))
    feature('USB'+label+'Shell','USB-C 金属插座 '+label,metal,'Tablet',0,'metal')
    box('USB'+label+'Tongue','USB-C 舌片 '+label,6.7,.66,4.4,(x,y+normal[1]*.25,6.95),'Tablet',0,'black',.25,orient=orient)
    for row in [-1,1]:
        for j in range(12):box(f'USB{label}Contact{row}_{j+1}','USB-C 镀金触点',.23,.06,3.0,(x-2.75+j*.5,y+normal[1]*.4,6.95+row*.375),'Tablet',0,'gold',.015,orient=orient)
# Bottom intake banks and dock registration recesses.
for side in [-1,1]:
    x=side*40.8
    cut('TabletFrame',rr_shape(41.0,5.2,1.5,3.0,(x,-58.5,4.9),YROT),'底部进风口')
    mesh=rr_shape(40.6,4.8,1.3,.24,(x,-57.80,4.9),YROT)
    holes=[Part.makeCylinder(.40,.5,vec(x-18.8+j*.95,-57.95,3.50+row*.93),vec(0,1,0)) for row in range(4) for j in range(40)]
    feature('IntakeMesh'+str(side),'底部进风蜂孔网',mesh.cut(Part.makeCompound(holes)),'Tablet',0,'black')
    cut('TabletFrame',Part.makeCylinder(1.65,2.8,vec(side*16.3,-58.3,7.0),vec(0,1,0)),'底座定位孔')
RESULT=stage_done(3,'dual_usb_and_cooling_ports','完成上、下 USB-C 与 48 触点、三段排风、双进风蜂孔网、顶部麦克风与亮度传感器、耳机插座和游戏卡盖。',views=[('top',{'normal':(0,1,.2),'up':(0,0,1),'target':(0,56,7),'span':42,'size':(2200,600)}),('bottom',{'normal':(0,-1,.2),'up':(0,0,1),'target':(0,-56,7),'span':42,'size':(2200,600)}),('front',{'span':185})])
print(json.dumps(RESULT,ensure_ascii=False))
