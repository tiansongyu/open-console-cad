# Semantic fit corrections from the independent stage-10 interference audit.
exec('def visible'+(ROOT/'scripts/common.py').read_text().split('def visible',1)[1])
def revise(key,shape,reason):
    old=C[key];old.PhysicalPart=False
    new=feature(key,old.Label,shape,old.Assembly,old.ExplodeLayer,old.MaterialDescription,old.Fidelity.startswith('Schematic'))
    new.addProperty('App::PropertyLink','PreviousRevision','CAD study');new.PreviousRevision=old
    new.addProperty('App::PropertyString','RevisionReason','CAD study');new.RevisionReason=reason;old.Visibility=False
    return new

def shift(key,v):C[key].Placement.Base=C[key].Placement.Base+vec(*v)

# Clearances are modeled as real pockets rather than ignored interference pairs.
cut('TabletFrame',[rr_shape(7.48,5.28,1.74,4,(4.5+j*8,48.7,7.3),YROT) for j in range(5)],'排风网安装余量')
cut('TabletFrame',C['StandRecess'].Shape,'支架收纳槽定位空间')
shift('BottomLabel',(0,-.04,0));shift('BottomLabelText',(0,-.06,0))
for key in ['GameCardLegend','BumperLegendL','BumperLegendR']:
    s=C[key].Shape.copy();s.rotate(s.BoundBox.Center,vec(0,1,0),180);revise(key,s,'顶部字样方向校正')
s=C['BottomLabelText'].Shape.copy();s.rotate(s.BoundBox.Center,vec(1,0,0),180);revise('BottomLabelText',s,'底部字样面向读者')
cut('CardReaderBoard',Part.makeCylinder(2.55,7,vec(49,43.8,7.2),vec(0,1,0)),'耳机座连接器避让')
for side,tag in [(-1,'L'),(1,'R')]:
    # Recess the SL/SR and sync controls inside the sliding channel.
    for key in ['Joy'+tag+'SL','Joy'+tag+'SR']:shift(key,(side*.60,0,0))
    shift('Joy'+tag+'Sync',(side*1.10,0,0))
    for j in range(1,5):shift('Joy'+tag+'LED'+str(j),(side*.72,0,0))
    railback=Part.makeBox(.60,90.2,7.36,vec(85.90,-45.1,3.40))
    if side<0:railback=railback.mirror(vec(),vec(1,0,0))
    revise('Joy'+tag+'RailBack',railback,'与主机导轨上唇保持 0.06 mm 间隙')
    cut('Joy'+tag+'RailTongue',[C['Joy'+tag+'Sync'].Shape]+[C['Joy'+tag+'LED'+str(j)].Shape for j in range(1,5)],'SYNC 与灯窗安装位')
    nose=Part.makeBox(.48,1.1,7.0,vec(83.6,-46.2,3.6))
    if side<0:nose=nose.mirror(vec(),vec(1,0,0))
    feature('Joy'+tag+'EndConnector','手柄导轨端部绝缘鼻','bad' if False else nose,'JoyRail'+tag,0,'black')
    pocket=Part.makeBox(.65,1.25,7.2,vec(83.50,-46.3,3.5))
    if side<0:pocket=pocket.mirror(vec(),vec(1,0,0))
    cut('ConsoleRail'+str(side),pocket,'手柄端连接器避让')
    # Countersinks, shoulder markings, hinge bearings and release-button pockets.
    holes=[Part.makeCylinder(1.40,.62,vec(side*103+dx,yy,-1.43)) for dx,yy in [(-8,-39),(8,-26),(-6.5,22),(7,28)]]
    cut('Joy'+tag+'Rear',holes,'沉头孔深度修正')
    cut('Joy'+tag+'Front',C['BumperLegend'+tag].Shape,'肩部字样分离')
    cut('Joy'+tag+'Trigger',[Part.makeCylinder(.70,14,vec(side*103-7,35.4,.65),vec(1,0,0)),rr_shape(3.5,5.1,.9,2.0,(side*89.3,36.1,-2.7))],'扳机轴承与释放键间隙')
    # Printed trigger letters are recessed flush to the published 28.4 mm envelope.
    shift('TriggerLegend'+tag,(0,0,.038))
    cut('Joy'+tag+'Trigger',C['TriggerLegend'+tag].Shape,'扳机字样凹嵌')
    # Metal domes and stems retain a small unpressed travel gap.
    for j in range(4):
        C[f'Joy{tag}ButtonStem{j}'].Placement.Base.z=10.64;C[f'Joy{tag}ButtonStem{j}'].Height=2.71
        shift(f'Joy{tag}ButtonPad{j}',(0,0,.06));shift(f'Joy{tag}ButtonDome{j}',(0,0,.06))
    # The gimbal side blocks seat outside the metal frame; bearings clear the axes.
    shift('Joy'+tag+'Pot0',(1.55,0,0));shift('Joy'+tag+'Pot1',(0,1.55,0))
    cut('Joy'+tag+'GimbalRing',[Part.makeCylinder(.58,15,vec(side*103-7.5,STICK_CENTERS[tag][1],8.3),vec(1,0,0)),Part.makeCylinder(.58,15,vec(side*103,STICK_CENTERS[tag][1]-7.5,8.3),vec(0,1,0))],'万向环轴承孔')
    shift('Joy'+tag+'WirelessIC',(0,4.0,0))
    # Reposition the haptic unit slightly inward, clear of the rear screw boss.
    for suffix in ['HapticCase','HapticMass','HapticCoil','HapticSpring0','HapticSpring1']:shift('Joy'+tag+suffix,(0,3.0,0))
cut('JoyRBumper',C['PlusButton'].Shape,'加号键与肩键间隙')
# Stand hinge and rear shield mounting apertures.
cut('StandRecess',Part.makeCylinder(1.06,23,vec(53.5,7.3,1.8),vec(1,0,0)),'支架铰链容置槽')
shield_tools=[Part.makeCylinder(1.13,23,vec(53.5,7.3,1.8),vec(1,0,0))]
for x,y in [(-80.5,-45.2),(80.5,-45.2),(-80.5,45.2),(80.5,45.2)]:shield_tools.append(Part.makeCylinder(1.72,.65,vec(x,y,1.65)))
cut('RearEMIShield',shield_tools,'屏蔽板铰链与螺钉避让')
# Battery length is reduced within the same schematic cell family to clear the speaker bay.
pouch=rr_shape(72,77,2,5.7,(-43,3,2.95)).cut(rr_shape(70.6,75.6,1.4,4.6,(-43,3,3.50)))
revise('BatteryPouch',pouch,'电池下缘与扬声器分区')
revise('BatteryCell',rr_shape(70.2,75.2,1.2,4.2,(-43,3,3.70)),'电池内部与外软包同步')
foam=rr_shape(73.4,78.4,2.2,.48,(-43,3,2.38)).cut(rr_shape(68,72,1,.7,(-43,3,2.25)))
revise('BatteryFoam',foam,'泡棉随电池分区更新')
cut('Mainboard',rr_shape(18.4,10.5,3.1,1.5,(73,-40.5,8.7)),'扬声器 PCB 边缘缺口')
shift('WiFiPackage',(-9,-13,0))
# Terminations occupy end caps of the resistor body, not duplicate the same volume.
for j in range(1,33):
    o=C['Passive'+str(j)];b=o.Shape.BoundBox;center=b.Center
    revise('Passive'+str(j),rr_shape(1.32,.9,.05,.65,(center.x,center.y,b.ZMin)),'阻容陶瓷芯体与金属焊端分区')
for j in range(14,19):
    for suffix in ['', 'Terminal-1','Terminal1']:shift('Passive'+str(j)+suffix,(0,7.0,0))
# Heat-transfer interfaces touch along surfaces, and the fin stack has pipe seating notches.
revise('HeatPipeBridge',rr_shape(6.4,10,.8,.05,(48,-4,6.15)),'热管与均热片之间的薄铜连接')
for j in range(16,35):cut('CoolingFin'+str(j),C['CopperHeatPipe'].Shape,'散热片热管配合槽')
for tag,x in [('L',-73),('R',73)]:
    C['Speaker'+tag+'Diaphragm'].Placement.Base.z=9.52
    # Gasketed duct feeds the four visible speaker slits around the LCD module edge.
    duct=rr_shape(24,3.4,1.0,2.8,(x+ (7 if x<0 else -7),-44,10.0)).cut(rr_shape(22.5,2.0,.6,3.1,(x+ (7 if x<0 else -7),-44,9.85)))
    feature('Speaker'+tag+'Duct','前面板扬声器导音槽',duct,'TabletInternal',2,'black',True)
    cut('DisplayBackplate',rr_shape(24.4,3.8,1.2,.8,(x+ (7 if x<0 else -7),-44,10.70)),'前扬声器导音通道')
# Coaxial IR optics sit in a bored sensor carrier.
revise('IRCameraSensor',rr_shape(5,5,.3,4.4,(103,-46,.9)),'传感器壳体与红外光轴对齐')
cut('IRCameraSensor',Part.makeCylinder(1.70,3.0,vec(103,-50.0,3.1),vec(0,1,0)),'红外透镜安装孔')
C['IRWindow'].Placement.Base.y=-51.0
# Rear brand marks are flush inlays and do not add to the body thickness.
C['RearNintendoMark'].Placement.Base.z=.018;cut('TabletRear',C['RearNintendoMark'].Shape,'后盖品牌嵌层')
C['RearModelMark'].Placement.Base.z=.012;cut('TabletRear',C['RearModelMark'].Shape,'后盖文字嵌层')
# Dock, grip and strap interfaces get actual mating sockets.
cut('DockFloor',[C[k].Shape for k in ['DockGuideBack-1','DockGuideFront-1','DockGuideBack1','DockGuideFront1','DockConnectorMount']],'底座导垫与浮动插座安装位')
cut('GripBridge',[C['GripHandle-1'].Shape,C['GripHandle1'].Shape],'握把桥壳与侧柄搭接座')
for side in [-1,1]:cut('GripHandle'+str(side),C['GripRail'+str(side)].Shape,'握把导轨安装面')
for tag in ['L','R']:
    cut('Strap'+tag+'Body',C['Strap'+tag+'Lock'].Shape,'腕带锁扣滑动槽')
    cut('Strap'+tag+'CordLock',C['Strap'+tag+'Cord'].Shape,'织绳穿孔')
C['DockLogo'].Placement.Base.z=26.982;cut('DockFront',C['DockLogo'].Shape,'底座标识凹嵌')
# Dock assembly fixings and all twenty-four docking plug contacts.
for j,(x,y) in enumerate([(-76,DOCK_Y-40),(76,DOCK_Y-40),(-76,DOCK_Y+40),(76,DOCK_Y+40)],1):
    cut('DockBackCover',[Part.makeCylinder(1.74,.95,vec(x,y,-27.1)),Part.makeCylinder(.86,5.1,vec(x,y,-27.1))],'底座后盖螺钉沉孔')
    screw('DockScrew'+str(j),(x,y,-26.96),'Dock',-4,radius=1.60,length=4.8,drive='cross')
    ringpart('DockBoss'+str(j),'底座后盖螺钉柱',2.1,.85,7.4,(x,y,-26.1),'DockInternal',-3,'shell',internal=True)
for row in [-1,1]:
    for j in range(12):box(f'DockPlugContact{row}_{j}','底座 USB-C 插头触点',.23,.075,3.7,(-2.75+j*.5,DOCK_Y-37.7,11.4+row*1.26),'DockInternal',2,'gold',.015,True,orient=YROT)
# Slightly lighter graphite distinguishes molded surfaces and black rubber in the CAD view.
PALETTE['shell']=(.17,.18,.19);PALETTE['screen']=(.060,.073,.085)
for o in C.values():appearance(o,PALETTE[o.MaterialDescription],metal=.32 if o.MaterialDescription in ['metal','gold','copper'] else .18,gloss=45)
HANDHELD_GROUPS=['Tablet','Display','TabletInternal','JoyLeft','JoyRight','JoyRailL','JoyRailR','JoyInternalL','JoyInternalR']
RESULT=stage_done(11,'assembly_fit_refinement','按逐对求交结果修正导轨、支架、内置器件、热管与散热片、扬声器、手柄机构和附件配合；补齐导音槽、底座紧固件和插头触点。',views=[('front',{'assemblies':HANDHELD_GROUPS}),('hero',{'assemblies':HANDHELD_GROUPS,'normal':(-.45,-.4,2)}),('internal',{'assemblies':HANDHELD_GROUPS,'normal':(0,0,-1),'exclude':['TabletRear','Kickstand','StandFoot','RearNintendoMark','RearModelMark','RearEMIShield','JoyLRear','JoyRRear']}),('dock',{'assemblies':['Dock','DockInternal'],'normal':(-.6,.3,2),'target':(0,DOCK_Y,0),'span':150}),('grip',{'assemblies':['Grip'],'normal':(-.6,-.3,2),'target':(GRIP_X,GRIP_Y,0),'span':145})])
