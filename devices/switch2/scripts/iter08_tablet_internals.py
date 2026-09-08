# Return to the clean pre-logo rear ancestor, so old importer cutouts cannot leave ghosts.
current_rear=C['TabletRear'];ancestor=current_rear
while ancestor.TypeId=='Part::Cut':
    if '官方' in ancestor.Tool.Label:ancestor=ancestor.Base;break
    ancestor=ancestor.Base
current_rear.PhysicalPart=False;ancestor.PhysicalPart=True;C['TabletRear']=ancestor
cut('TabletRear',C['RearNintendoMark'].Shape,'精确完整标识嵌槽')
cut('TabletRear',C['RearModelMark'].Shape,'型号文字嵌槽')
# Distinct Switch 2 internal proportions: narrower battery, wider L-shaped PCB and larger fan.
a='TabletInternal';PALETTE['thermal']=(.55,.35,.30)
box('BatteryPouch','5220 mAh 电池铝塑包',54,88,4.55,(-58,6,4.60),a,-2,'battery',2.5,True)
cut('BatteryPouch',rr_shape(52.8,86.8,1.9,3.75,(-58,6,5.0)),'电池内部卷叠空间')
box('BatteryCell','电芯卷叠布局',52.4,86.4,3.4,(-58,6,5.17),a,-2,'rubber',1.7,True)
foam=rr_shape(56.0,90.0,3,.40,(-58,6,4.05)).cut(rr_shape(50,82,1.2,.6,(-58,6,3.95)))
foam=foam.cut(C['StandMount-1'].Shape)
feature('BatteryFoam','电池泡棉定位框',foam,a,-3,'black',True)
textpart('BatteryMark','NINTENDO  BEE-003',2.5,(-38,23,4.58),a,-2,'white',BACKROT)
textpart('BatteryCapacity','3.78 V  5220 mAh',2.0,(-39,16,4.58),a,-2,'white',BACKROT)
textpart('BatteryNote','INTERNAL LAYOUT STUDY',1.45,(-38,7,4.58),a,-2,'white',BACKROT)
board=rr_shape(124,108,2.0,.95,(31,0,9.30)).cut(Part.makeCylinder(22.2,1.6,vec(7,25,9.0)))
board=board.cut(rr_shape(33,22,1.0,1.5,(-20,46,9.1)))
feature('Mainboard','L 形主板 PCB 示意',board,a,-1,'pcb',True)
for tag in ['L','R']:
    cut('Mainboard',[C['ConsoleMagnet'+tag+str(j)].Shape for j in range(2)],'磁体模块配合孔')
cut('Mainboard',Part.makeCylinder(2.55,7,vec(50.2,51.5,7.1),vec(0,1,0)),'耳机模块避让')
chips=[('SoC',47,-12,28,28,2.15),('RAM1',26,-7,10,14,1.25),('RAM2',26,-25,10,14,1.25),('UFS1',44,-38,12,10,1.05),('UFS2',65,-33,12,10,1.05),('WiFi',72,22,9,12,1.10),('PMIC',78,-12,7,8,.95)]
for name,x,y,w,h,t in chips:box(name+'Package',name+' 封装布局',w,h,t,(x,y,9.15-t),a,-1,'black',.35,True)
textpart('SoCMark','NVIDIA',3.0,(55,-13,6.985),a,-1,'white',BACKROT)
# The two UFS packages are on the main board, rather than the original Switch's daughterboard.
for name,x,y,w,h in [('MemoryShield',26,-16,14,36),('PowerShield',78,-12,10,12)]:
    box(name,'金属屏蔽盖',w,h,.28,(x,y,7.30),a,-2,'metal',.7,True)
# Modern game-card cage, separate microphone module, and top-control flex.
box('GameCardCage','游戏卡插座屏蔽罩',27.4,19,3.1,(69.2,44.3,5.2),a,-2,'metal',1.0,True)
cut('GameCardCage',rr_shape(25.6,19.5,.55,2.2,(69.2,44.8,5.65)),'游戏卡插入通道')
for j in range(17):box('GameCardContact'+str(j+1),'卡槽触点',.55,6,.09,(57.0+j*1.50,42,5.70),a,-2,'gold',.04,True)
box('MicrophonePCB','数字麦克风模块小板',5,6,.65,(87,49.5,6.4),a,-2,'pcb',.4,True)
cyl('MicrophoneCapsule','数字麦克风封装',1.8,1.1,(87,49.5,5.2),a,-2,'metal',internal=True)
box('TopControlFlex','顶部按键与感应器排线',68,3.3,.12,(-61,52.5,9.9),a,-1,'copper',.5,True)
# Passives with non-overlapping ceramic centers and end terminations.
positions=[(x,-49) for x in [-22,-13,-4,5,14,23,32,41,50,59]]+[(82,y) for y in [-26,-18,-10,-2,6,14,22]]+[(-23,y) for y in [-39,-32,-25,-18,-11,-4,3]]
for i,(x,y) in enumerate(positions,1):
    box('Passive'+str(i),'主板阻容芯体',1.10,.80,.50,(x,y,8.70),a,-1,'rubber',.035,True)
    for end in [-1,1]:box(f'Passive{i}End{end}','器件端帽',.20,.84,.50,(x+end*.65,y,8.70),a,-1,'metal',.015,True)
# Cooling fan with independent blades, hub, frame and vibration-isolating grommets.
fan=Part.makeCylinder(21.0,5.3,vec(7,25,3.0)).cut(Part.makeCylinder(18.7,5.6,vec(7,25,2.85)))
feature('FanHousing','大尺寸离心风扇外壳',fan,a,-2,'black',True)
ringpart('FanCover','风扇金属盖',21,15.4,.35,(7,25,2.60),a,-2,'metal',internal=True)
cyl('FanHub','风扇中心电机',6.2,4.5,(7,25,3.3),a,-2,'black',internal=True)
for j in range(36):
    blade=Part.Face(Part.makePolygon([vec(6.65,0),vec(18.15,2.7),vec(18.02,3.04),vec(6.62,.24),vec(6.65,0)])).extrude(vec(0,0,3.70));blade.rotate(vec(),vec(0,0,1),j*10);blade.translate(vec(7,25,3.8));feature('FanBlade'+str(j+1),'离心风扇叶片',blade,a,-2,'rubber',True)
for j,(x,y) in enumerate([(-16,25),(30,25),(7,2)]):
    ringpart('FanGrommet'+str(j),'风扇减振胶套',1.75,.8,2.6,(x,y,4.2),a,-2,'rubber',internal=True)
    cyl('FanPin'+str(j),'风扇固定销',.72,3.2,(x,y,4.0),a,-2,'metal',internal=True)
# Broad continuous heatpipe, thermal contact layers and slotted fin stack.
box('SoCThermalPad','导热垫',26,26,.55,(47,-12,6.45),a,-2,'thermal',.8,True)
box('ThermalFilm','导热界面层',26,26,.05,(47,-12,6.40),a,-2,'thermal',.8,True)
box('HeatSpreader','铜质导热底座',32,31,.80,(47,-12,5.60),a,-2,'copper',1.5,True)
points=[vec(47,-12),vec(47,25),vec(37,43),vec(10,50)]
segments=[]
for p,q in zip(points,points[1:]):
    delta=q-p;shape=rr_shape(9.2,delta.Length+9.2,4.5,1.05);shape.rotate(vec(),vec(0,0,1),math.degrees(math.atan2(-delta.x,delta.y)));shape.translate((p+q)*.5+vec(0,0,4.55));segments.append(shape)
pipe=segments[0].multiFuse(segments[1:]).removeSplitter();feature('CopperHeatPipe','Switch 2 宽扁铜热管',pipe,a,-3,'copper',True)
for j in range(44):
    fin=rr_shape(.25,6.8,0,4.9,(-19+j*1.05,51.3,3.0)).cut(pipe)
    feature('CoolingFin'+str(j+1),'散热鳍片',fin,a,-2,'metal',True)
# Independent stereo enclosures and front-facing ducts.
for tag,x in [('L',-76),('R',76)]:
    box('Speaker'+tag+'Housing','立体声扬声器腔体',23,11,5.6,(x,-48.5,4.0),a,-2,'black',3.5,True)
    cut('Speaker'+tag+'Housing',rr_shape(20.2,8.2,2.5,4.5,(x,-48.5,4.6)),'扬声器内腔')
    box('Speaker'+tag+'Magnet','扬声器磁体',15,5.8,2.8,(x,-48.5,5.4),a,-2,'metal',1.8,True)
    box('Speaker'+tag+'Diaphragm','扬声器振膜',20.2,8.2,.10,(x,-48.5,9.63),a,-2,'rubber',2.5,True)
    duct=rr_shape(22,5.5,1.2,.90,(x,-51.5,9.85)).cut(rr_shape(20.6,4.1,.7,1.2,(x,-51.5,9.7)))
    feature('Speaker'+tag+'LowerDuct','扬声器水平导音道',duct,a,1,'black',True)
    duct=rr_shape(17.0,2.6,.8,3.10,(x,-55.25,10.0)).cut(rr_shape(15.6,1.3,.45,3.4,(x,-55.25,9.85)))
    feature('Speaker'+tag+'MouthDuct','扬声器前面板导音槽',duct,a,2,'black',True)
    cut('DisplayBackplate',rr_shape(17.4,3.0,1.0,.8,(x,-55.25,10.6)),'声道开孔')
# Rear heat shield with fan, stand hinge and service-fastener openings.
shield=rr_shape(190,108,2.5,.30,(0,0,1.85)).cut(Part.makeCylinder(22.5,.7,vec(7,25,1.65)))
for side in [-1,1]:shield=shield.cut(rr_shape(9,5.0,1,.7,(side*87,.7,1.65)))
for x,y in [(-93,-51),(93,-51),(-93,51),(93,51)]:shield=shield.cut(Part.makeCylinder(1.72,.7,vec(x,y,1.65)))
shield=shield.cut(rr_shape(18,24,1,.7,(-85,-22,1.65)))
feature('RearEMIShield','后部金属屏蔽散热板',shield,a,-4,'metal',True)
# PCB support posts and four fasteners pass through actual mounting holes.
for j,(x,y) in enumerate([(-26,49),(-26,-48),(88,40),(88,-40)],1):
    cut('Mainboard',Part.makeCylinder(.88,1.5,vec(x,y,9.1)),'主板安装孔')
    ringpart('BoardPost'+str(j),'主板支承柱',1.60,.84,5.6,(x,y,3.5),a,-2,'metal',internal=True)
    screw('BoardScrew'+str(j),(x,y,3.05),a,-3,radius=1.45,length=6.8,drive='cross')
# Short flex sections, battery leads and connectors stay distinct from semiconductor packages.
box('DisplayFlex','LCD 宽排线',23,14,.12,(-9,-22,10.40),a,-1,'copper',.5,True)
box('BatterySocket','电池插接座',7,4,1.8,(-21,-26,7.2),a,-1,'white',.4,True)
for j in range(4):cyl('BatteryLead'+str(j),'电池连接导线',.32,10.5,(-30.5,-27.6+j*1.05,7.0),a,-1,'blue' if j<2 else 'black',axis=(1,0,0),internal=True)
box('AntennaLeft','左侧天线板',5.5,29,.45,(-92,24,8.3),a,-1,'pcb',.6,True)
box('AntennaRight','右侧天线板',5.5,22,.45,(89,3,8.3),a,-1,'pcb',.6,True)
RESULT=stage_done(8,'switch2_internal_architecture','建立 5220 mAh 电池、L 形主板与双 UFS、36 叶片风扇、宽扁热管及 44 片散热鳍片、独立声腔和导音槽、屏蔽板及支承固定件。',views=[('internal',{'normal':(0,0,-1),'span':200,'exclude':['TabletRear','Kickstand','StandFoot-1','StandFoot1','RearNintendoMark','RearModelMark','RearEMIShield']}),('back',{'normal':(0,0,-1),'span':200}),('cooling',{'normal':(.15,-.2,-1),'target':(35,15,5),'span':118,'size':(1700,1400),'exclude':['TabletRear','Kickstand','StandFoot-1','StandFoot1','RearNintendoMark','RearModelMark','RearEMIShield']})])
print(json.dumps(RESULT,ensure_ascii=False))
