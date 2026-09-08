a='DockInternal'
box('DockPCB','底座接口主板',148,77,.95,(-5,DOCK_Y+9,-1.60),a,-1,'pcb',2.0,True)
for key,x,y,w,h in [('USBController',-30,12,14,14),('VideoBridge',-8,-10,16,16),('PowerController',-60,-13,10,12),('LANController',14,29,10,11),('FanDriver',58,32,8,8)]:
    box('Dock'+key,key+' 封装',w,h,1.5,(x,DOCK_Y+y,-3.20),a,-2,'black',.35,True)
for i,(x,y) in enumerate([(x,y) for x in [-65,-45,-25,-5,15,35,55] for y in [40,-22]],1):
    box('DockPassive'+str(i),'底座阻容芯体',1.20,.90,1.1,(x,DOCK_Y+y,-2.80),a,-1,'rubber',.05,True)
    for side in [-1,1]:box(f'DockPassive{i}End{side}','器件端帽',.20,.95,1.1,(x+side*.70,DOCK_Y+y,-2.80),a,-1,'metal',.02,True)
# Active dock cooling, vent ducts and rear grille openings.
fc=(40,DOCK_Y-9)
ringpart('DockFanHousing','底座主动散热风扇壳',17.0,15.1,6.2,(fc[0],fc[1],-14.6),a,-2,'black',internal=True)
ringpart('DockFanCover','底座风扇金属盖',17.0,12.3,.30,(fc[0],fc[1],-15.0),a,-3,'metal',internal=True)
cyl('DockFanHub','底座风扇轮毂',4.5,5.0,(fc[0],fc[1],-14.0),a,-2,'black',internal=True)
for j in range(24):
    blade=Part.Face(Part.makePolygon([vec(5,0),vec(14.4,2.4),vec(14.3,2.7),vec(4.98,.23),vec(5,0)])).extrude(vec(0,0,4.2));blade.rotate(vec(),vec(0,0,1),j*15);blade.translate(vec(fc[0],fc[1],-13.5));feature('DockFanBlade'+str(j),'底座风扇叶片',blade,a,-2,'rubber',True)
exhaust=rr_shape(24,39,3,3.7,(40,DOCK_Y+28,-17.5)).cut(rr_shape(21.5,39.4,2,2.4,(40,DOCK_Y+28,-16.85)))
feature('DockExhaustDuct','底座后部排风风道',exhaust,a,-3,'black',True)
slots=[rr_shape(1.8,11,.65,6.5,(31+j*3,DOCK_Y+47,-26.0)) for j in range(7)]
slots += [rr_shape(2.0,13,.65,6.5,(-81+j*5.4,DOCK_Y-43,-26.0)) for j in range(19)]
cut('DockBackCover',slots,'后盖排风格栅')
# Floating USB-C carriage supported by four springs and guide rods.
carrier=rr_shape(30,4.5,1,13,(0,DOCK_Y-38,6))
for side in [-1,1]:carrier=carrier.fuse(rr_shape(4.2,4.5,.9,3.8,(side*16.3,DOCK_Y-38,10.475)))
feature('DockFloatingCarriage','弹簧浮动插头托架',carrier.removeSplitter(),a,1,'black',True)
box('DockSpringPlatform','插接机构固定座',39,2.0,13,(0,DOCK_Y-42,6),a,0,'metal',.90,True)
for j,(x,z) in enumerate([(-9,8.5),(9,8.5),(-9,16.3),(9,16.3)],1):
    cut('DockFloatingCarriage',Part.makeCylinder(1.06,5,vec(x,DOCK_Y-40.4,z),vec(0,1,0)),'浮动弹簧容置孔')
    cut('DockSpringPlatform',Part.makeCylinder(1.06,.55,vec(x,DOCK_Y-41.4,z),vec(0,1,0)),'弹簧底座孔')
    helix=Part.makeHelix(.70,4.20,.82);wire=Part.Wire(Part.makeCircle(.13,helix.Vertexes[0].Point,helix.Edges[0].tangentAt(helix.Edges[0].FirstParameter)))
    spring=Part.Wire(helix.Edges).makePipeShell([wire],True,True);spring.rotate(vec(),vec(1,0,0),-90);spring.translate(vec(x,DOCK_Y-41,z));feature('DockSpring'+str(j),'插头浮动压缩弹簧',spring,a,1,'metal',True)
    cyl('DockSpringRod'+str(j),'浮动导杆',.30,7,(x,DOCK_Y-42.6,z),a,1,'metal',axis=(0,1,0),internal=True)
plug=rr_shape(8.2,2.5,1.15,5.1,(0,DOCK_Y-35.5,12.375),YROT).cut(rr_shape(7.3,1.6,.70,5.4,(0,DOCK_Y-35.65,12.375),YROT))
feature('DockUSBCPlug','底座 USB-C 插头金属壳',plug,a,2,'metal',True)
ins=rr_shape(7.2,1.5,.65,4.6,(0,DOCK_Y-35.3,12.375),YROT).cut(rr_shape(5.8,.90,.4,4.9,(0,DOCK_Y-35.45,12.375),YROT))
feature('DockPlugInsulator','USB-C 环形绝缘芯',ins,a,2,'black',True)
for row in [-1,1]:
    for j in range(12):box(f'DockPlugContact{row}_{j}','USB-C 插头触点',.22,.04,3.4,(-2.75+j*.5,DOCK_Y-35.0,12.375+row*.425),a,2,'gold',.015,True,orient=YROT)
for side in [-1,1]:cyl('DockGuidePin'+str(side),'底座定位销',1.10,4.7,(side*16.3,DOCK_Y-35.5,12.375),a,2,'black',axis=(0,1,0),internal=True)
# Rear cover and PCB assembly fasteners, kept clear of connectors and the fan.
for j,(x,y) in enumerate([(-84,DOCK_Y+30),(84,DOCK_Y+30),(-86,DOCK_Y-31),(84,DOCK_Y-31)],1):
    cut('DockBackCover',[Part.makeCylinder(1.65,.9,vec(x,y,-25.8)),Part.makeCylinder(.85,5.4,vec(x,y,-25.8))],'后盖固定孔')
    screw('DockScrew'+str(j),(x,y,-25.56),'Dock',-4,radius=1.5,length=5.1,drive='cross')
    ringpart('DockBoss'+str(j),'底座后盖安装柱',2.0,.86,7.0,(x,y,-24.6),a,-3,'shell',internal=True)
RESULT=stage_done(11,'active_dock_and_floating_plug','加入底座主板与芯片、24 叶片主动风扇、排风通道、四弹簧浮动 USB-C 插头、环形绝缘芯与 24 触点，以及后盖紧固件。',views=[('dock_open',{'assemblies':['Dock','DockInternal'],'normal':(.55,.2,-2),'target':(0,DOCK_Y,0),'span':175,'exclude':['DockBackCover']}),('spring_detail',{'assemblies':['DockInternal'],'normal':(.3,-.8,1.4),'target':(0,DOCK_Y-38,12),'span':55,'size':(1500,1100)}),('dock',{'assemblies':['Dock','DockInternal'],'normal':(-.6,.3,2),'target':(0,DOCK_Y,0),'span':175})])
print(json.dumps(RESULT,ensure_ascii=False))
