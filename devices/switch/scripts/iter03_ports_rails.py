YROT=App.Rotation(vec(0,0,1),vec(0,1,0))
# Top controls, audio jack, game card lid, and the five-section exhaust.
openings=[Part.makeCylinder(3.05,4,vec(-73.5,48.7,7.4),vec(0,1,0)),rr_shape(15.8,5.2,2.4,4,(-59,48.7,7.4),YROT),Part.makeCylinder(2.60,4,vec(49,48.7,7.2),vec(0,1,0)),rr_shape(26.5,8.2,2.2,4,(69,48.7,7.1),YROT)]
for j in range(5):openings.append(rr_shape(7.2,5.0,1.6,4,(4.5+j*8.0,48.7,7.3),YROT))
cut('TabletFrame',openings,'顶部控制件、耳机、卡槽与排风口')
cyl('PowerButton','电源按键',2.80,1.50,(-73.5,49.0,7.4),'Tablet',1,'black',axis=(0,1,0))
box('VolumeRocker','音量摇杆按键',15.4,4.8,1.5,(-59,49.0,7.4),'Tablet',1,'black',2.25,orient=YROT)
# Raised power and volume symbols are modeled geometry, oriented onto the top face.
pr=Part.makeCylinder(1.35,.025,vec(-73.5,50.515,7.4),vec(0,1,0)).cut(Part.makeCylinder(1.02,.06,vec(-73.5,50.50,7.4),vec(0,1,0)))
pr=pr.cut(Part.makeBox(.65,.1,1.5,vec(-73.825,50.49,7.6)))
feature('PowerSymbolRing','电源符号圆环',pr,'Tablet',1,'white')
box('PowerSymbolLine','电源符号短线',.34,1.6,.025,(-73.5,50.515,8.05),'Tablet',1,'white',.12,orient=YROT)
for x,char in [(-63.4,'-'),(-54.6,'+')]:textpart('VolumeSymbol'+str(abs(x)).replace('.','_'),char,2.3,(x-.8,50.52,8.4),'Tablet',1,'white',YROT)
ringpart('HeadphoneRim','3.5 mm 耳机插座环',2.40,1.76,5.8,(49,44.6,7.2),'Tablet',1,'black',axis=(0,1,0))
ringpart('HeadphoneContact','耳机插座内金属接点',1.74,1.58,1.2,(49,44.8,7.2),'Tablet',1,'gold',axis=(0,1,0))
box('GameCardLid','GAME CARD 橡胶防尘盖',26.1,7.8,1.0,(69,49.42,7.1),'Tablet',1,'rubber',2.05,orient=YROT)
textpart('GameCardLegend','GAME CARD',1.7,(58.4,50.43,7.9),'Tablet',1,'black',YROT)
for j in range(5):
    mesh=rr_shape(7.3,5.1,1.65,.22,(4.5+j*8,49.0,7.3),YROT)
    slots=[rr_shape(.26,4.3,.10,.4,(1.95+j*8+k*.66,48.95,7.3),YROT) for k in range(9)]
    feature('ExhaustMesh'+str(j+1),'顶部排风口金属栅网',mesh.cut(Part.makeCompound(slots)),'Tablet',1,'black')
# Bottom USB-C socket, insulator and all 24 contacts.
cut('TabletFrame',rr_shape(9.2,3.6,1.6,4,(0,-51.0,6.9),YROT),'底部 USB-C 开口')
us=rr_shape(8.8,3.2,1.45,5,(0,-50.40,6.9),YROT).cut(rr_shape(8.18,2.58,1.20,5.3,(0,-50.55,6.9),YROT))
feature('USBCShell','USB-C 金属插座壳',us,'Tablet',-1,'metal')
box('USBCTongue','USB-C 绝缘舌片',6.7,.66,3.95,(0,-50.1,6.9),'Tablet',-1,'black',.25,orient=YROT)
for row in [-1,1]:
    for j in range(12):box(f'USBCContact{row}_{j+1}','USB-C 镀金触点',.23,.065,2.8,(-2.75+j*.5,-50.02,6.9+row*.38),'Tablet',-1,'gold',.015,orient=YROT)
# Dock registration recesses on either side of the port.
for side in [-1,1]:cut('TabletFrame',Part.makeCylinder(1.65,2.5,vec(side*12,-50.8,7),vec(0,1,0)),'底座定位孔')
# Recessed console rails. The steel returns leave a channel for Joy-Con tongues.
cut('TabletFrame',[Part.makeBox(3.3,93.6,11.2,vec(83.3,-46.8,1.4)),Part.makeBox(3.3,93.6,11.2,vec(-86.6,-46.8,1.4))],'手柄导轨安装凹槽')
for side in [-1,1]:
    def mirrored(s):
        if side<0:s=s.mirror(vec(),vec(1,0,0))
        return s
    backbone=Part.makeBox(.50,92.6,8.2,vec(83.42,-46.3,3.0))
    lips=[Part.makeBox(2.63,92.6,.38,vec(83.42,-46.3,z)) for z in [3.0,10.82]]
    steel=backbone.multiFuse(lips).removeSplitter()
    feature('ConsoleRail'+str(side),'主机不锈钢滑轨',mirrored(steel),'Tablet',0,'metal')
    for j in range(10):
        pad=Part.makeBox(.09,1.8,.34,vec(83.94,-44.8,3.65+j*.63))
        feature(f'ConsoleContact{side}_{j+1}','主机滑轨触点',mirrored(pad),'Tablet',0,'gold')
RESULT=stage_done(3,'interfaces_and_rails','完成顶部五段排风格栅、音量与电源、3.5 mm 插座、卡槽盖、USB-C 的 24 触点及双侧金属滑轨。',views=[('front',{}),('top',{'normal':(0,1,.22),'up':(0,0,1),'target':(0,49,7),'span':36,'size':(2200,600)}),('bottom',{'normal':(0,-1,.18),'up':(0,0,1),'target':(0,-49,7),'span':36,'size':(2200,600)})])
