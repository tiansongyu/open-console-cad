# Major internal architecture based on the firsthand teardown; local dimensions schematic.
assembly='TabletInternal'
box('BatteryPouch','主机电池铝塑软包',72,85,5.7,(-43,-1,2.95),assembly,-2,'battery',2.0,True)
cut('BatteryPouch',rr_shape(70.6,83.6,1.4,4.6,(-43,-1,3.50)),'电芯内部容积')
box('BatteryCell','电芯卷叠布局示意',70.2,83.2,4.2,(-43,-1,3.70),assembly,-2,'rubber',1.2,True)
foam=rr_shape(73.4,86.4,2.2,.48,(-43,-1,2.38)).cut(rr_shape(68,80,1,.7,(-43,-1,2.25)))
feature('BatteryFoam','电池周边泡棉',foam,assembly,-3,'black',True)
textpart('BatteryTitle','NINTENDO  HAC-003',3.0,(-16,14,2.925),assembly,-2,'white',BACKROT)
textpart('BatteryEnergy','Li-ion   3.7 V   4310 mAh',2.0,(-17,7,2.925),assembly,-2,'white',BACKROT)
textpart('BatteryCaution','INTERNAL LAYOUT STUDY',1.8,(-15,-2,2.925),assembly,-2,'white',BACKROT)
# Main board with fan relief, edge notches and raised connector interfaces.
board=rr_shape(78,88,2.0,1.0,(40,0,8.9))
fanvoid=Part.makeCylinder(17.0,2,vec(17,23,8.5))
board=board.cut(fanvoid).cut(rr_shape(12,12,1,2,(7,-41,8.5)))
feature('Mainboard','主机主板 PCB · 布局示意',board,assembly,-1,'pcb',True)
# Surface-mounted SoC, memory, PMIC and wireless packages on the rear face.
chips=[('Tegra',48,-4,20,20,1.5),('RAM1',28,-5,10,14,1.1),('RAM2',28,-21,10,14,1.1),('PMIC',57,-28,8,9,.9),('WiFi',68,22,10,12,1.0),('AudioIC',64,-8,6,6,.8)]
for name,x,y,w,h,t in chips:
    box(name+'Package',name+' 封装示意',w,h,t,(x,y,8.82-t),assembly,-1,'black',.35,True)
    if name=='Tegra':textpart('TegraMark','TEGRA',2.4,(54,-5,7.30),assembly,-1,'white',BACKROT)
# Memory daughterboard and game-card connector are separate replaceable modules.
box('EMMCBoard','eMMC 存储子板',25,14,.75,(60,15,6.8),assembly,-2,'pcb',.8,True)
box('EMMCPackage','eMMC 封装',17,11,1.1,(60,15,5.6),assembly,-2,'black',.4,True)
box('CardReaderBoard','游戏卡与音频接口子板',38,22,.70,(60,34,8.0),assembly,-2,'pcb',1,True)
box('GameCardCage','游戏卡金属卡座',29.2,17,3.2,(65,35,4.55),assembly,-2,'metal',.8,True)
cut('GameCardCage',rr_shape(27.4,17.5,.45,2.3,(65,35.5,5.0)),'游戏卡插入空间')
for j in range(17):box('GameCardContact'+str(j+1),'游戏卡连接器金触片',.55,6,.1,(53+j*1.48,35,5.10),assembly,-2,'gold',.05,True)
# Component array is distributed around the occupied board zones, with explicit gaps.
for i,(x,y) in enumerate([(x,y) for x in [40,44,48,52,56,60,64,68,72] for y in [-36,-40]]+[(x,y) for x in [72,75] for y in [-25,-21,-17,-13,0,4,8]],1):
    box('Passive'+str(i),'主板阻容器件',1.6,.9,.65,(x,y,8.20),assembly,-1,'rubber',.06,True)
    for end in [-1,1]:box(f'Passive{i}Terminal{end}','器件焊端',.25,.94,.65,(x+end*.80,y,8.20),assembly,-1,'metal',.02,True)
# Fan: thin housing, rim, hub, twenty-four individual swept vane solids and outlet.
fc=(17,23)
fan=Part.makeCylinder(16.4,4.9,vec(*fc,3.2)).cut(Part.makeCylinder(14.4,5.1,vec(*fc,3.1)))
feature('FanHousing','离心风扇壳体',fan,assembly,-2,'black',True)
ringpart('FanTopPlate','风扇金属盖板',16.4,11.9,.35,(*fc,2.82),assembly,-2,'metal',internal=True)
cyl('FanHub','风扇电机轮毂',4.5,4.2,(*fc,3.50),assembly,-2,'black',internal=True)
for j in range(24):
    pts=[vec(5.1,0),vec(13.9,2.0),vec(13.75,2.35),vec(5.05,.28),vec(5.1,0)]
    vane=Part.Face(Part.makePolygon(pts)).extrude(vec(0,0,3.4));vane.rotate(vec(),vec(0,0,1),j*15);vane.translate(vec(*fc,3.75))
    feature('FanVane'+str(j+1),'离心叶轮叶片',vane,assembly,-2,'rubber',True)
# Copper heat-spreader shoe and routed, flattened heat pipe to the top fin stack.
box('SoCThermalPad','SoC 导热垫',19,19,.42,(48,-4,6.84),assembly,-2,'rubber',.3,True)
box('HeatSpreader','铜质均热底座',24,24,.60,(48,-4,6.20),assembly,-2,'copper',1.0,True)
path=[vec(48,-4,0),vec(48,22,0),vec(40,39,0),vec(21,43.5,0)]
# Rounded chain links fuse into one continuous flattened pipe, with exact endpoint overlap.
pipe=[]
for a,b in zip(path,path[1:]):
    direction=b-a;length=direction.Length
    seg=rr_shape(6.4,length+6.4,3.1,1.2,(0,0,0));seg.rotate(vec(),vec(0,0,1),math.degrees(math.atan2(-direction.x,direction.y)));seg.translate((a+b)*.5+vec(0,0,4.95));pipe.append(seg)
pipe=pipe[0].multiFuse(pipe[1:]).removeSplitter();feature('CopperHeatPipe','连续扁铜热管',pipe,assembly,-3,'copper',True)
# Heat pipe must mate to the copper shoe through a defined bridge.
box('HeatPipeBridge','热管接触铜桥',6.4,10,.65,(48,-4,6.15),assembly,-2,'copper',.8,True)
for j in range(34):box('CoolingFin'+str(j+1),'排风散热翅片',.25,6.2,4.3,(2.7+j*1.05,45.1,3.2),assembly,-2,'metal',0,True)
# Speakers sit at the bottom corners; their diaphragms face front openings through ducts.
for tag,x in [('L',-73),('R',73)]:
    box('Speaker'+tag+'Housing','立体声扬声器腔体',17,9,4.4,(x,-40.5,5.1),assembly,-2,'black',3.0,True)
    cut('Speaker'+tag+'Housing',rr_shape(13,5.5,2.5,3.5,(x,-40.5,5.55)),'声学腔')
    box('Speaker'+tag+'Magnet','扬声器磁体',10,4.3,2.0,(x,-40.5,6.3),assembly,-2,'metal',1.8,True)
    box('Speaker'+tag+'Diaphragm','扬声器振膜',13.2,5.7,.1,(x,-40.5,9.15),assembly,-2,'rubber',2.6,True)
# Internal ground shield with cooling and card-reader service openings.
shield=rr_shape(165,92,1.8,.28,(0,0,1.85))
shield=shield.cut(Part.makeCylinder(17.2,.6,vec(17,23,1.7))).cut(rr_shape(23,21,1,.6,(65,-38,1.7)))
feature('RearEMIShield','主机后部 EMI 屏蔽板',shield,assembly,-4,'metal',True)
# Two FPC interconnects and battery lead bundle, kept separate from active packages.
box('DisplayFlex','显示模组 FPC',12,24,.14,(5,-23,10.15),assembly,-1,'copper',.3,True)
box('CardFlex','游戏卡排线',8,9,.12,(77,19,7.75),assembly,-1,'copper',.2,True)
for j,yy in enumerate([-26,-24.7,-23.4]):
    feature('BatteryLead'+str(j),'电池线束',Part.makeCylinder(.40,9.8,vec(-6.6,yy,8.1),vec(1,0,0)),assembly,-1,'red' if j==0 else 'black',True)
RESULT=stage_done(8,'tablet_internal_layout','加入电池软包与电芯、主板及封装、存储和卡槽子板、24 叶片风扇、连续扁热管、34 片散热鳍片、双扬声器、屏蔽板及排线。',views=[('internal',{'normal':(0,0,-1),'exclude':['TabletRear','Kickstand','StandFoot','RearNintendoMark','RearModelMark','RearEMIShield']}),('shield',{'normal':(0,0,-1),'exclude':['TabletRear','Kickstand','StandFoot','RearNintendoMark','RearModelMark']}),('front',{})])
