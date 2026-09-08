DOCK_Y=-208.0
# Rounded top corners and small lower corners are shared by the separate shell pieces.
def dock_outer(w,h,rt,rb,t,origin):
    shape=Part.makeBox(w,h,t,vec(-w/2,-h/2,0))
    edges=[e for e in shape.Edges if e.BoundBox.ZLength>t-1e-7 and abs(e.BoundBox.YMin-h/2)<1e-7];shape=shape.makeFillet(rt,edges)
    edges=[e for e in shape.Edges if e.BoundBox.ZLength>t-1e-7 and abs(e.BoundBox.YMin+h/2)<1e-7];shape=shape.makeFillet(rb,edges)
    shape.translate(vec(*origin));return shape
whole=dock_outer(201,113,27,7,51.2,(0,DOCK_Y+1,-25.6))
base=whole.common(Part.makeBox(205,19,46,vec(-102.5,DOCK_Y-55.5,-20.3)))
base=base.cut(Part.makeBox(193,17,39.5,vec(-96.5,DOCK_Y-52.5,-17.5)))
feature('DockBase','底座下部通风基座',base,'Dock',0,'shell')
tower=whole.common(Part.makeBox(205,94,24.7,vec(-102.5,DOCK_Y-36.5,-20.0)))
tower=tower.cut(dock_outer(196.4,108.4,24.7,4.7,23.0,(0,DOCK_Y+1,-20.1)))
feature('DockTower','底座后部电子舱壳',tower,'Dock',0,'shell')
front=whole.common(Part.makeBox(205,91,5.6,vec(-102.5,DOCK_Y-36.5,20.0)))
front=front.cut(dock_outer(196.4,108.4,24.7,4.7,3.4,(0,DOCK_Y+1,19.9)))
feature('DockFront','底座前面板',front,'Dock',4,'shell')
back=dock_outer(200.4,112.4,26.7,6.7,5.1,(0,DOCK_Y+1,-25.6))
back=back.cut(dock_outer(196.8,108.8,24.9,4.9,4.5,(0,DOCK_Y+1,-24.8)))
feature('DockBackCover','可拆底座后盖',back,'Dock',-4,'shell')
cut('DockBackCover',rr_shape(18,12,2,6,(-70,DOCK_Y-53,-25.8)),'后盖出线缺口')
# Two rubber feet form the published 2 mm contribution to total height.
for side in [-1,1]:
    box('DockFoot'+str(side),'2 mm 底座防滑脚',26,2,39,(side*79,DOCK_Y-56.5,-18),'Dock',0,'rubber',.65)
    box('DockRearGuide'+str(side),'主机后导向软垫',7.5,77,.50,(side*67,DOCK_Y+5,4.75),'Dock',1,'rubber',1.0)
    box('DockFrontGuideCore'+str(side),'前导向支承肋',7.5,76,3.2,(side*67,DOCK_Y+2,20.0),'Dock',3,'shell',1.0)
    box('DockFrontGuide'+str(side),'主机前导向软垫',7.5,76,.50,(side*67,DOCK_Y+2,19.5),'Dock',3,'rubber',1.0)
# Actual intake bores in the lower base, clear of the feet.
bores=[Part.makeCylinder(.52,3.6,vec(-59.4+col*2.7,DOCK_Y-55.7,-13.5+row*3.0),vec(0,1,0)) for row in range(11) for col in range(45)]
cut('DockBase',bores,'底部进气孔阵列')
# Left side has two USB-A ports. The rear bay has AC, HDMI and LAN, not a third USB-A.
mat=App.Matrix();mat.A11=0;mat.A21=1;mat.A31=0;mat.A12=0;mat.A22=0;mat.A32=1;mat.A13=1;mat.A23=0;mat.A33=0;SIDE_ROT=App.Rotation(mat)
for j,y in enumerate([DOCK_Y+13,DOCK_Y-7],1):
    cut('DockTower',rr_shape(14,6.4,.6,5,(-101,y,-10),SIDE_ROT),'USB-A 侧面开口')
    shape=rr_shape(13.4,5.8,.4,12,(-100.2,y,-10),SIDE_ROT).cut(rr_shape(12.5,4.9,.2,12.3,(-100.35,y,-10),SIDE_ROT))
    feature('DockSideUSB'+str(j),'USB-A 插座金属壳',shape,'DockInternal',-2,'metal',True)
    box('DockUSBTongue'+str(j),'USB-A 舌片',11.8,1.5,9,(-100.1,y,-10),'DockInternal',-2,'black',.15,True,orient=SIDE_ROT)
    for k in range(4):
        s=rr_shape(.70,.10,.02,7,(-3.75+k*2.5,.86,0));s.Placement=App.Placement(vec(-100.0,y,-10),SIDE_ROT).multiply(s.Placement);feature(f'DockUSB{j}Contact{k}','USB-A 触点',s,'DockInternal',-2,'gold',True)
# Rear connectors point toward the removable back panel.
for key,x,y,w,h,depth in [('AC',-48,DOCK_Y+21,8.8,3.2,11),('HDMI',-48,DOCK_Y-5,14.2,5.7,12),('LAN',-48,DOCK_Y-29,16.4,13.5,14)]:
    radius=1.4 if key=='AC' else .6
    metal=rr_shape(w,h,radius,depth,(x,y,-20.2)).cut(rr_shape(w-.8,h-.8,max(.2,radius-.4),depth+.3,(x,y,-20.35)))
    feature('Dock'+key+'Socket',key+' 接口壳',metal,'DockInternal',-2,'metal',True)
    if key=='LAN':
        for j in range(8):box('LANContact'+str(j),'LAN 弹片触点',.36,.15,8,(x-3.5+j,y+4.4,-19.9),'DockInternal',-2,'gold',.02,True)
    elif key=='HDMI':
        box('HDMITongue','HDMI 绝缘舌片',11.8,1.3,8,(x,y,-20.0),'DockInternal',-2,'black',.2,True)
        for j in range(19):box('HDMIContact'+str(j),'HDMI 金触点',.25,.08,6,(x-5.4+j*.6,y+.78,-19.9),'DockInternal',-2,'gold',.015,True)
    textpart('DockLabel'+key,key,2.6,(x+9,y+1,-20.24),'DockInternal',-2,'black',BACKROT)
# Front status lamp and flush official mark.
cut('DockBase',rr_shape(4.6,1.5,.3,6,(-91,DOCK_Y-49,20.0)),'TV 输出指示灯开口')
box('DockLED','底座 TV 输出灯',4.2,1.1,.5,(-91,DOCK_Y-49,25.1),'Dock',4,'led',.2)
official_logo('DockLogo',49,(0,DOCK_Y+3,25.582),'Dock',4,'black');cut('DockFront',C['DockLogo'].Shape,'底座官方标识嵌入')
RESULT=stage_done(10,'switch2_dock_shell_and_ports','建立新版大圆角底座、独立前板和后盖、2 mm 防滑脚、495 个底部进气孔、双 USB-A 及后部 AC/HDMI/LAN 接口。',views=[('dock',{'assemblies':['Dock','DockInternal'],'normal':(-.6,.3,2),'target':(0,DOCK_Y,0),'span':170}),('open_back',{'assemblies':['Dock','DockInternal'],'normal':(.45,.2,-2),'target':(0,DOCK_Y,0),'span':170,'exclude':['DockBackCover']})])
print(json.dumps(RESULT,ensure_ascii=False))
