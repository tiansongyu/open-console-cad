# Accessories are separate assemblies positioned below the handheld for a clean kit layout.
DOCK_Y=-182.0
# Dock rear tower, removable back cover, front wall and bottom bridge.
box('DockTower','底座后部壳体',173,103.4,25,(0,DOCK_Y+.3,-22),'Dock',0,'shell',3.0)
cut('DockTower',rr_shape(168.6,99.6,1.5,23.2,(0,DOCK_Y,-22.1)),'底座电子舱')
box('DockBackCover','底座后盖',171.6,102.6,4.4,(0,DOCK_Y+.3,-27),'Dock',-4,'shell',2.7)
cut('DockBackCover',rr_shape(168.6,99.6,1.5,3.8,(0,DOCK_Y,-26.35)),'底座后盖内腔')
# Rear cable routing notch is open at the bottom of the cover.
cut('DockBackCover',rr_shape(20,12,2,5,(51,DOCK_Y-48,-27.1)),'后盖出线口')
box('DockFront','底座正面壳体',173,86.4,6.9,(0,DOCK_Y-8.2,20.1),'Dock',4,'shell',3.0)
cut('DockFront',rr_shape(168.6,82.6,1.5,5.1,(0,DOCK_Y-8.5,20.0)),'正面板内腔')
box('DockFloor','底座底部连接梁',167.0,8.8,17.0,(0,DOCK_Y-47.0,3.05),'Dock',0,'shell',1.0)
# Soft guide pads protect the screen; opposing ribs define a 14.5 mm slot.
for side in [-1,1]:
    box('DockGuideBack'+str(side),'主机后导向垫',8.0,73,1.1,(side*59,DOCK_Y-7,3.05),'Dock',1,'rubber',1.0)
    box('DockGuideFront'+str(side),'主机前导向垫',8.0,63,1.1,(side*59,DOCK_Y-12,18.65),'Dock',3,'rubber',1.0)
    box('DockFoot'+str(side),'底座防滑脚',41,.6,37,(side*52,DOCK_Y-51.7,-21),'Dock',0,'rubber',.2)
# USB-C docking plug is vertical in Y and mounted on a floating support.
box('DockConnectorMount','浮动插接支座',28,4.0,12,(0,DOCK_Y-40.7,5.3),'DockInternal',1,'black',1.4,True)
plug=rr_shape(8.2,2.5,1.15,5.1,(0,DOCK_Y-38.7,11.4),YROT).cut(rr_shape(7.3,1.6,.70,5.5,(0,DOCK_Y-38.9,11.4),YROT))
feature('DockUSBCPlug','底座 USB-C 插头',plug,'DockInternal',2,'metal',True)
for side in [-1,1]:cyl('DockGuidePin'+str(side),'底座定位柱',1.15,4,(side*12,DOCK_Y-38.7,11.4),'DockInternal',2,'black',axis=(0,1,0),internal=True)
# Dock PCB in the rear tower, populated on its rear-facing surface.
box('DockPCB','底座接口 PCB',132,70,1.2,(0,DOCK_Y-4,-7),'DockInternal',-1,'pcb',2.0,True)
for key,x,y,w,h in [('Controller',-15,5,12,12),('VideoBridge',10,5,13,13),('PowerIC',36,-8,8,9),('USBHub',-40,-8,10,10)]:
    box('Dock'+key,'底座芯片 '+key,w,h,1.2,(x,DOCK_Y+y,-8.3),'DockInternal',-2,'black',.4,True)
# USB-A sockets: two on the left side and one in the rear bay.
def usba(key,pos,orient,assembly='DockInternal'):
    outer=rr_shape(13.4,5.8,.45,12,pos,orient);inner=rr_shape(12.5,4.9,.25,12.3,pos,orient)
    feature(key+'Shell','USB-A 接口金属壳',outer.cut(inner),assembly,-2,'metal',True)
    ins=rr_shape(11.8,1.7,.15,9,(0,0,0));ins.Placement=App.Placement(vec(*pos),orient);feature(key+'Tongue','USB-A 绝缘舌片',ins,assembly,-2,'black',True)
    for j in range(4):
        sh=rr_shape(.7,.12,.02,6,(-3.75+j*2.5,.98,0));sh.Placement=App.Placement(vec(*pos),orient).multiply(sh.Placement);feature(key+'Contact'+str(j),'USB-A 触点',sh,assembly,-2,'gold',True)
# Side ports have width in the local Y direction of the dock and height in Z.
SIDE_ROT=App.Rotation(vec(1,0,0),vec(0,1,0),vec(0,0,1),'ZXY')
SIDE_ROT=App.Rotation(vec(0,1,0),vec(0,0,1),vec(1,0,0),'ZXY')
# Its basis is local X -> global Y, local Y -> global Z, local Z -> global X.
mat=App.Matrix();mat.A11=0;mat.A21=1;mat.A31=0;mat.A12=0;mat.A22=0;mat.A32=1;mat.A13=1;mat.A23=0;mat.A33=0;SIDE_ROT=App.Rotation(mat)
for j,y in enumerate([DOCK_Y-24,DOCK_Y-6],1):
    cut('DockTower',rr_shape(14,6.4,.6,5,(-87,y,-12),SIDE_ROT),'左侧 USB 接口孔')
    usba('DockSideUSB'+str(j),(-86.2,y,-12),SIDE_ROT)
# Back bay has three labeled connectors exposed after removing the rear cover.
backorient=App.Rotation()
usba('DockRearUSB',(-12,DOCK_Y-15,-21.9),backorient)
usbcp=rr_shape(8.8,3.2,1.45,10,(-40,DOCK_Y-15,-21.9)).cut(rr_shape(8.1,2.5,1.1,10.3,(-40,DOCK_Y-15,-22.0)))
feature('DockACSocket','底座 AC USB-C 电源接口',usbcp,'DockInternal',-2,'metal',True)
hdmi=rr_shape(14.2,5.7,.8,10,(20,DOCK_Y-15,-21.9)).cut(rr_shape(12.7,4.2,.4,10.3,(20,DOCK_Y-15,-22.0)))
feature('DockHDMI','HDMI 接口金属壳',hdmi,'DockInternal',-2,'metal',True)
box('DockHDMITongue','HDMI 绝缘舌片',11.8,1.3,7.5,(20,DOCK_Y-15,-21.7),'DockInternal',-2,'black',.25,True)
for j in range(19):box('HDMIContact'+str(j+1),'HDMI 触点',.25,.09,5.5,(14.6+j*.6,DOCK_Y-14.2,-21.5),'DockInternal',-2,'gold',.015,True)
for text,x in [('AC ADAPTER',-52),('USB',-16),('HDMI OUT',9)]:textpart('DockLabel'+text.replace(' ',''),text,2.0,(x,DOCK_Y-8,-22.02),'DockInternal',-2,'white',BACKROT)
# Status light and official logo on the front face.
cut('DockFront',rr_shape(4.8,1.5,.3,7,(-77,DOCK_Y-44,20.0)),'TV 输出灯开口')
box('DockLED','TV 输出状态指示灯',4.3,1.1,.8,(-77,DOCK_Y-44,26.1),'Dock',4,'led',.2)
official_logo('DockLogo',43,(0,DOCK_Y-7,27.015),'Dock',4,'black')
# Passive Joy-Con grip, in its own nearby assembly; not a charging grip.
GRIP_X=213;GRIP_Y=-179
box('GripBridge','Joy-Con 握把中桥',52,101,12,(GRIP_X,GRIP_Y,-2),'Grip',0,'shell',2.0)
cut('GripBridge',rr_shape(47,95,1.2,9.5,(GRIP_X,GRIP_Y,-1.6)),'握把内腔')
for side in [-1,1]:
    # Hand rest blends tapered ellipsoidal sections in an editable Part loft.
    wires=[]
    for yy,rx,rz in [(GRIP_Y-57,7,9),(GRIP_Y-44,13,17),(GRIP_Y-17,13,18),(GRIP_Y+17,8,12),(GRIP_Y+30,4,5)]:
        ellipse=Part.Ellipse(vec(),max(rx,rz),min(rx,rz)).toShape()
        if rz>rx:ellipse.rotate(vec(),vec(0,0,1),90)
        w=Part.Wire(ellipse)
        w.rotate(vec(),vec(1,0,0),90);w.translate(vec(GRIP_X+side*37,yy,-7));wires.append(w)
    solid=Part.makeLoft(wires,True,False)
    feature('GripHandle'+str(side),'人体握持侧柄',solid,'Grip',0,'black')
    box('GripRail'+str(side),'握把滑轨',2.4,92,7.5,(GRIP_X+side*27.2,GRIP_Y,3.0),'Grip',1,'metal',.45)
    for j in range(4):box(f'GripLEDWindow{side}_{j}','握把玩家灯导光窗',1.0,1.3,.12,(GRIP_X+side*20,GRIP_Y+7.5-j*5,10.02),'Grip',1,'white',.1)
official_logo('GripLogo',25,(GRIP_X,GRIP_Y,10.02),'Grip',1,'black')
# Two removable strap rails, lock sliders, buttons, and closed cord loops.
for side in [-1,1]:
    x=side*105;y=-327;assembly='StrapL' if side<0 else 'StrapR'
    box(assembly+'Body','腕带滑轨壳',14.6,101,13.9,(x,y,0),assembly,0,'black',3.0)
    cut(assembly+'Body',rr_shape(7.0,91,1,9,(x+side*5.0,y,2.5)),'腕带导轨槽')
    for j,yy in enumerate([y-22,y+22]):box(assembly+'Button'+str(j),'腕带 SL/SR 加长键',11.7,9,1.1,(x,yy,13.9),assembly,1,'rubber',1.2)
    box(assembly+'Lock','腕带白色锁扣',9,5,3,(x,y-44,12.7),assembly,1,'white',1.0)
    # A closed planar racetrack cord loop is generated from a swept circular section.
    loop=Part.Wire(Part.Ellipse(vec(x,y-84,6),31,18).toShape());loop.rotate(vec(x,y-84,6),vec(0,0,1),90)
    profile=Part.Wire(Part.makeCircle(.85,loop.Vertexes[0].Point,loop.Edges[0].tangentAt(loop.Edges[0].FirstParameter)))
    feature(assembly+'Cord','腕带闭合织绳',loop.makePipeShell([profile],True,True),assembly,0,'black')
    box(assembly+'CordLock','腕带调节扣',5.2,7,4,(x,y-56,4),assembly,0,'rubber',1.0)
RESULT=stage_done(10,'dock_grip_straps','完成独立底座及可拆后盖、三路 USB、HDMI 和电源接口、插接导向与内部 PCB；增加非充电握把及两套腕带。',views=[('handheld',{'assemblies':['Tablet','Display','TabletInternal','JoyLeft','JoyRight','JoyRailL','JoyRailR','JoyInternalL','JoyInternalR']}),('dock',{'assemblies':['Dock','DockInternal'],'normal':(-.65,.3,2),'target':(0,DOCK_Y,0),'span':145}),('dock_open',{'assemblies':['Dock','DockInternal'],'normal':(-.55,.2,-2),'target':(0,DOCK_Y,0),'span':150,'exclude':['DockBackCover']}),('grip',{'assemblies':['Grip'],'normal':(-.7,-.3,2),'target':(GRIP_X,GRIP_Y,0),'span':145}),('straps',{'assemblies':['StrapL','StrapR'],'target':(0,-350,6),'span':150})])
