"""Twelve A3 sheets from the delivered original Japanese Saturn study BReps."""
from pathlib import Path
import os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
repo=Path(__file__).resolve().parents[3];sys.path.insert(0,str(repo/'tools'))
from cadlib import drawings as d
import FreeCAD as App,Part

d.init_drawing(Path(__file__).resolve().parents[1]);C=d.C;M=d.M;up=(0,0,1)
def starts(*prefixes):return [k for k in C if k.startswith(prefixes)]
def without(keys,*words):return [k for k in keys if not any(w in k for w in words)]
def caption(s,v,t,y):s.text(v['x'],y,t+f" · {v['scale']:.3f}:1",anchor='middle')
body=d.keys_for(M['envelope_groups']);pad=without(d.keys_for(['Controller']),'Cable','Grommet','Wire','Plug')

s=d.Sheet(1,'日版初代灰色主机总装与近似尺寸',['HST-3200 采用灰色斜肩外壳、弧形光驱盖、深色前面板与蓝色 POWER / RESET / OPEN 键。','260 × 230 × 83 mm 来自 HST-3210 官方家族规格，仅作为本 HST-3200 学习模型的近似包络。'])
v=s.view_fit('ConsoleIsometric',body,(18,29,173,153),(.5,-1.6,1.25));caption(s,v,'灰色外壳与原始控制布局',208)
v=s.view_fit('ConsoleTop',body,(225,35,150,145),(0,0,1));d.dimension_box(s,v,['LowerHousing','UpperHousing'],'x',20);d.dimension_box(s,v,['LowerHousing','UpperHousing'],'y',214);caption(s,v,'保存模型的宽度与深度',208);s.save()

s=d.Sheet(2,'原始前后接口与服务盖',['前侧保留两组手柄端口，后侧包括上壳电源座、AV、通信接口与可拆电池扩展盖。','插头、弹性触点、绝缘载体与金属套分开建模；接点和孔位是模型学习几何，不定义原厂引脚电路。'])
v=s.view_fit('ConsoleFront',body,(24,28,166,72),(0,-1,0),up);d.dimension_box(s,v,['LowerHousing','UpperHousing','Foot0','Foot1','Foot2','Foot3'],'y',14);caption(s,v,'双手柄接口与前部控制',119)
v=s.view_fit('ConsoleRear',body,(224,28,161,72),(0,1,0),up);caption(s,v,'后部连接与维修开口',119)
v=s.view_fit('ControllerPort',starts('ControllerPort1','ControllerTongue1','ControllerContact1'),(27,151,153,42),(0,-1,0),up);caption(s,v,'单排九接点手柄端口',211)
v=s.view_fit('AVSocket',starts('AVShell','AVCarrier','AVContact'),(257,142,93,61),(0,1,0),up);caption(s,v,'十接点 AV 连接器',211);s.save()

s=d.Sheet(3,'原版六键手柄的曲面外壳',['HSS-0101 选择原始灰色外观，ABC 为黑色，XYZ 与 START 为蓝色，并保留左右肩键和圆盘十字键。','前后壳由原生样条截面放样建立；外形、壁厚、孔位与下面的测量值均为学习近似。'])
v=s.view_fit('PadFront',pad,(26,28,201,146),(0,0,1));d.dimension_box(s,v,['PadBack','PadFront'],'x',20);d.dimension_box(s,v,['PadBack','PadFront'],'y',15);caption(s,v,'灰色六键手柄正面',207)
v=s.view_fit('PadRear',pad,(252,32,122,82),(0,0,-1));caption(s,v,'后壳握柄与五处固定',132)
v=s.view_fit('DirectionalPad',starts('PadDPad','PadDirectionMarks'),(273,151,77,45),(.6,-1,1.5));caption(s,v,'浮动圆盘与凸起十字',211);s.save()

s=d.Sheet(4,'光驱盖与卡槽防尘机构',['光驱盖包含一体轴耳、钢轴、右侧回位弹簧、左侧扇形齿轮和支架，卡槽采用整片防尘门。','本页说明装配关系和局部避让；齿形、弹簧及释放联动为学习近似，不代表已验证的运动行程。'])
v=s.view_fit('LidGearTrain',starts('LidSector','LidDamping','LidGearBracket','LidPinion','LidBracketScrew'),(28,29,141,78),(-1,.2,.2),up);caption(s,v,'盖板扇形齿轮与支架',129)
v=s.view_fit('LidSpring',['LidHingePin1','LidReturnSpring','LidHingeWasher1'],(238,30,137,69),(.3,-1,1),up);caption(s,v,'右侧钢轴与回位弹簧',129)
keys=without(starts('OpenLatch','OpenReturn','OpenSpring','OpenBracket','DoorSense'),'Lead')
v=s.view_fit('ReleaseMechanism',keys,(38,150,131,45),(.6,-1,1.2),up);caption(s,v,'导向、锁扣与检测开关',211)
v=s.view_fit('CartridgeDoor',['CartridgeFlap0','CartridgeDeck','CartridgeHingePin','CartridgeSpring'],(225,150,150,24),(0,0,1));d.dimension_box(s,v,['CartridgeFlap0'],'x',142);caption(s,v,'整片卡槽防尘门',184)
v=s.view_fit('CartridgeSpringDetail',['CartridgeSpring'],(312,190,50,14),(.3,-1,1),up);caption(s,v,'右侧回位弹簧',211);s.save()

s=d.Sheet(5,'主机与手柄的真实实体剖面',['本页将交付的实际三维 BRep 与指定 Y 平面相交，填充只表示真正切到的材料。','主机截面说明上壳电源、屏蔽与光驱的高度关系，手柄截面说明曲面壳、输入件与电路板。'])
s.text(198,17,'A-A · 主机 Y=-17 主轴区域',4,'middle');v=d.section_view(s,'ConsoleSection',body,(23,34,351,56),offset=-17);caption(s,v,'主轴、光盘仓、屏蔽与供电层',112)
s.text(198,136,'B-B · 手柄 Y=-214 十字键区域',4,'middle');v=d.section_view(s,'PadSection',pad,(23,155,351,40),offset=-214);caption(s,v,'上下曲面壳、硅胶、板件与按键',211);s.save()

s=d.Sheet(6,'主机和手柄分层爆炸结构',['爆炸工程保留原始几何与零件编号，按展示位移分开壳体、板件、机构及接点。','本页省略长线束和排线以便阅读；完整原生装配、STEP 与网页仍包含这些组件。'])
v=s.view_fit('ConsoleExploded',without(body,'Lead','Ribbon'),(17,29,192,167),(.5,-.45,1.3),exploded=True);caption(s,v,'外壳、光驱、电源与分层屏蔽',211)
v=s.view_fit('PadExploded',without(pad,'Wire','Cable'),(221,32,157,160),(.3,-.7,1.3),exploded=True);caption(s,v,'六键手柄的独立装配层',211);s.save()

s=d.Sheet(7,'双处理器主板与独立光驱控制板',['主板包含双 SH-2、图形、系统与音频处理器及分区存储，另设 CD 子系统板、控制芯片与缓存。','布局参考 MAIN VA0.5 及原版拆解照片；元件、引脚与互连数量只描述本模型，不复现生产电路。'])
v=s.view_fit('Mainboard',d.keys_for(['Mainboard']),(25,30,177,150),(0,0,1));d.dimension_box(s,v,['MainPCB'],'x',20);d.dimension_box(s,v,['MainPCB'],'y',15);caption(s,v,'主板与分区器件布局',209)
v=s.view_fit('TwinSH2',starts('SH2A','SH2B'),(250,30,100,70),(0,0,1));caption(s,v,'两个主处理器封装',121)
keys=without(starts('CDSubsystemPCB','CDSH1','CDController','CDBuffer','CDClock','CDPassive'),'Socket')
v=s.view_fit('CDSubsystem',keys,(246,150,113,47),(0,0,1));d.dimension_box(s,v,['CDSubsystemPCB'],'x',141);caption(s,v,'独立 CD 控制与缓存板',211);s.save()

s=d.Sheet(8,'光盘主轴与双导轨光头',['光驱包含独立控制板、白色长支座、主轴、定位台、双导轨光头、螺旋进给件与电机。','局部齿形和光头结构是学习近似；镜片只用于表示位置，模型不执行光学读写或运动仿真。'])
keys=['OpticalBase','OpticalPCB','OpticalFrame','OpticalBridge']+starts('Pickup','Spindle','Turntable','Sled','OpticalDriver','OpticalPassive','OpticalCap','OpticalUnitDataSocket','OpticalPowerSocket')
v=s.view_fit('OpticalTransport',keys,(24,30,174,152),(0,0,1));d.dimension_box(s,v,['OpticalBase'],'x',20);caption(s,v,'移开光盘仓后的读取机构',209)
v=s.view_fit('PickupDetail',starts('Pickup','SledLeadScrew','SledNut'),(241,28,127,76),(0,0,1));d.dimension_box(s,v,['PickupRail0'],'y',229);caption(s,v,'双导轨、螺旋进给与光头',124)
v=s.view_fit('SpindleDetail',starts('Spindle','Turntable'),(268,150,68,47),(.7,-1,1.2),up);caption(s,v,'主轴电机与定位台',211);s.save()

s=d.Sheet(9,'控制板、硅胶按键与上壳电源',['HST-3200 的电源位于上壳，变压器、滤波件与支承独立建模；后部保留 CR2032 备份电池。','手柄使用独立硅胶输入膜与碳膜接点；元件和电源只说明结构层次，不构成可制造或安全验证的电路。'])
v=s.view_fit('UpperPSU',without(starts('PSU'),'Bracket'),(24,30,92,151),(0,0,1));d.dimension_box(s,v,['PSUPCB'],'x',20);d.dimension_box(s,v,['PSUPCB'],'y',16);caption(s,v,'上壳电源板',210)
v=s.view_fit('PadBoard',starts('PadPCB','PadLogic','PadPassive','PadCableConnector','PadShoulderSwitch','PadCarbon'),(190,31,187,73),(0,0,1));d.dimension_box(s,v,['PadPCB'],'x',118);caption(s,v,'六键手柄板件与接点',134)
v=s.view_fit('SiliconeInputs',starts('PadDPadMembrane','PadActionMembrane','PadStartMembrane'),(176,150,129,47),(.5,-1,1.4),up);caption(s,v,'三组输入硅胶膜',211)
v=s.view_fit('BackupCell',starts('BatteryHolder','ClockBattery'),(326,153,49,45),(0,0,1));caption(s,v,'电池（移开压片）',211);s.save()

s=d.Sheet(10,'原版连接线与空白媒体',['连接附件包括日式两片电源插头、八字设备端头，以及 AV 转复合视频和立体声 RCA 的连接线。','线缆使用便于展示的长度；12 cm 光盘为空白学习媒体，不含游戏数据、第三方游戏画面或可运行内容。'])
v=s.view_fit('MainsCord',starts('ACWall','ACCord','ACDevice'),(24,30,174,79),(0,0,1));caption(s,v,'电源线与八字端头',127)
v=s.view_fit('AVConnections',starts('AVPlug','AVCable','AVSplitter','AVBranch','RCA'),(230,29,141, 81),(0,0,1));caption(s,v,'AV 与三路 RCA',127)
v=s.view_fit('BlankDisc',starts('BlankDisc'),(35,151,124,45),(0,0,1));d.dimension_box(s,v,['BlankDisc'],'x',140);caption(s,v,'空白 12 cm 光盘',211)
v=s.view_fit('ControllerPlug',starts('PadPlugGrip','PadPlugHead','PadPlugTongue','PadPlugContact'),(249,151,103,45),(1,0,0),up);caption(s,v,'原始九接点手柄插头',211);s.save()

s=d.Sheet(11,'组件与显示材料索引',['同一组件可能包含多枚触点或文字实体，因此组件条目与实体数量分开统计。','同一零件编号关联原生装配、STEP 和网页网格；显示材料用于区分结构，不指定真实材料牌号。'])
names={'Body':'主机壳体与盖板','Controls':'控制机构、灯光与线束','Ports':'原始连接与卡槽','Mainboard':'主板及电子器件','Optical':'CD 子系统与光驱机构','Power':'上壳电源与内部线束','Shield':'上下金属屏蔽','Internal':'主机支承与固定','Controller':'原版六键手柄','Accessories':'电源、AV 与空白媒体'}
for x,t in [(12,'装配分组'),(111,'条目'),(151,'显示材料'),(268,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=35+i*16.5
 s.text(12,y,names.get(name,name),3.3);s.text(120,y,count,anchor='middle');s.text(151,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3.1);s.text(268,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.1);s.line((12,y+4),(384,y+4))
s.text(12,211,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体 · COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'版本依据、近似边界与重建入口',['外观选择日版灰色 HST-3200 与灰色 HSS-0101 六键手柄，保留原版控制与接口家族。','图册是保存模型的版本快照；改变三维实体后，需要同步生成投影、尺寸、验证记录和网页。'])
sections=[(16,'资料与版本',['世嘉官方家族及周边资料：型号、接口和原始配件类别。','Dig and Rescue：HST-3200 及 HSS-0101 实物拆解。','手柄内构照片含浅色家族版本，外观依据原始灰色照片。']),
 (67,'近似与内容边界',['HST-3210 的 260 × 230 × 83 mm 仅作为家族包络参考。','本 HST-3200 模型的局部尺寸、引脚、机构与线束均为学习近似。','未复现生产电路、制造公差、光盘数据或经过验证的运动。']),
 (118,'可核对的检查记录',[f"{M['design_iterations']} 轮源码 / {M['physical_components']} 组件 / {M['solids']} 实体。",'完整重建、严格实体、装配求交与 STEP 回读分别记录。','字体、内容、每页视觉和原生尺寸引用随交付一并检查。']),
 (169,'继续修改的入口',['资料：references/SOURCES.md；清单：output/COMPONENTS.csv。','主要源码：tools/cadlib/saturn.py；逐轮入口：scripts/。','检查：output/reports/；修改后同步更新 CAD、图纸与网页。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
