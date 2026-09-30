"""Twelve A3 sheets projected from the delivered original PS2 study BReps."""
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
body=d.keys_for(M['envelope_groups'])
pad=without(d.keys_for(['Controller']),'Cable','Plug','Wire')

s=d.Sheet(1,'日版初代主机总装与公开包络',['SCPH-10000 采用宽上壳、非对称阶梯底壳、七层横向沟槽和前置盘托，保留初代日版接口。','Sony 原版说明书给出主体宽 301、深 182、高 78 mm；外伸接口、标识与所有局部尺寸另作学习近似。'])
v=s.view_fit('ConsoleIsometric',body,(18,29,173,153),(.5,-1.6,1.25));caption(s,v,'阶梯壳体与前置盘托',208)
v=s.view_fit('ConsoleTop',body,(225,35,150,145),(0,0,1));d.dimension_box(s,v,['UpperHousing'],'x',20,published=True);d.dimension_box(s,v,['UpperHousing'],'y',214,published=True);caption(s,v,'主体宽度与深度',208);s.save()

s=d.Sheet(2,'双层前接口与初代 PC CARD 后接口',['前部包含两组记忆卡和手柄插座、蓝色双 USB 与四接点 i.LINK 面板，以及复位和出仓控制键。','后部保留初代 Type III 卡槽、68 接点导向笼、保护盖、弹出机构、AV MULTI、光纤和内部电源入口。'])
v=s.view_fit('ConsoleFront',body,(24,28,166,72),(0,-1,0),up);d.dimension_box(s,v,['LowerHousing','UpperHousing','Foot0'],'y',14,published=True);caption(s,v,'双层卡槽、手柄插座和蓝色接口区',119)
v=s.view_fit('ConsoleRear',body,(224,28,161,72),(0,1,0),up);caption(s,v,'初代卡槽与后部连接',119)
v=s.view_fit('FrontConnector',starts('Port1'),(29,144,148,53),(0,-1,0),up);caption(s,v,'八接点卡槽与九位置控制器接口',211)
v=s.view_fit('CardCage',without(starts('PCCard'),'Protector','Label'),(238,143,130,54),(.6,1,1.2),up);caption(s,v,'卡槽导向与弹出机构',211);s.save()

s=d.Sheet(3,'双模拟控制器外观与六处后壳固定',['上下壳由可编辑曲线截面放样形成，包含圆形按键面、双摇杆杯形舱、两层肩键及模式指示灯。','手柄尺寸为照片指导的学习近似；后期同型号拆解仅提供家族结构参考，不据此确定首发批次板型。'])
v=s.view_fit('ControllerFront',pad,(26,28,201,146),(0,0,1));d.dimension_box(s,v,['DS2Back','DS2Front'],'x',20);d.dimension_box(s,v,['DS2Back','DS2Front'],'y',15);caption(s,v,'联动方向键、面键与双模拟摇杆',207)
v=s.view_fit('ControllerRear',pad,(252,32,122,82),(0,0,-1));caption(s,v,'六处固定与后部型号标识',132)
v=s.view_fit('DirectionalKeys',starts('DS2DPad'),(272,150,79,47),(.5,-1,1.4));caption(s,v,'方向键、支点、胶膜与碳接点',211);s.save()

s=d.Sheet(4,'原始盘托、装载传动与读取机构',['独立光驱包含纵向导轨、盘托齿条、皮带减速、主轴电机、光头导杆及丝杆进给结构。','结构保留初代独立 RF 板与光头家族布局；齿形、隔振件及光学内部只表示静态学习关系。'])
optical=without(d.keys_for(['Optical']),'Cover','Clamp','Tray','Mark','Label')
v=s.view_fit('OpticalMechanism',optical,(20,28,175,156),(0,0,1));caption(s,v,'移开盘托与上盖后的机构',209)
v=s.view_fit('Tray',['DiscTray','TrayBezel'],(228,30,146,81),(0,0,1));d.dimension_box(s,v,['DiscTray'],'x',20);caption(s,v,'盘托开口与媒体凹槽',127)
v=s.view_fit('Pickup',starts('Pickup','Feed','OpticalBlock','Objective','Focus'),(245,151,110,45),(.5,-1,1.3),up);caption(s,v,'光头、导杆与进给丝杆',211);s.save()

s=d.Sheet(5,'主机与控制器的真实实体剖面',['剖面由保存的三维实体与指定 Y 平面相交生成，填充仅表示实际切到的材料。','主机截面展示机壳、屏蔽、板件及光驱高度关系；控制器截面展示壳体、按键膜与输入件的间隙。'])
s.text(198,17,'A-A · 主机 Y=-18 光驱主轴区域',4,'middle');v=d.section_view(s,'ConsoleSection',body,(23,34,351,56),offset=-18);caption(s,v,'主轴、读取机构、主板与机壳',112)
s.text(198,136,'B-B · 控制器 Y=-233 按键区域',4,'middle');v=d.section_view(s,'ControllerSection',pad,(23,155,351,40),offset=-233);caption(s,v,'按键、胶膜、接点膜与上下壳',211);s.save()

s=d.Sheet(6,'主机与控制器的分层爆炸结构',['爆炸工程保留完整实体、稳定零件标识和编号，通过展示位移区分外壳、板件、机构和输入层。','为提高图纸可读性，本页省略长线束及密集外观文字；完整工程、组件清单和三维预览保留全部零件。'])
v=s.view_fit('ConsoleExploded',without(body,'Lead','Harness','Ribbon','Flex','Legend','Mark','Badge'),(17,29,192,167),(.5,-.45,1.3),exploded=True);caption(s,v,'外壳、光驱、供电与分层板件',211)
v=s.view_fit('ControllerExploded',without(pad,'Mark','Symbol','Fixed','Pill','Pin','Label','Model'),(221,32,157,160),(.3,-.7,1.3),exploded=True);caption(s,v,'壳体、主板、胶膜与双摇杆',211);s.save()

s=d.Sheet(7,'双面主板与主要封装',['主板正面包含 EE、GS、双 RDRAM、IOP、音频区、供电调节元件和时钟电池。','背面封装、排线座、焊盘与穿板孔为结构示意，无法确认的器件保留描述性标识，不提供电气网络。'])
v=s.view_fit('MainboardTop',d.keys_for(['Mainboard']),(26,32,164,141),(0,0,1));d.dimension_box(s,v,['Mainboard'],'x',20);d.dimension_box(s,v,['Mainboard'],'y',15);caption(s,v,'主要处理器、内存与供电分区',208)
v=s.view_fit('MainboardUnderside',d.keys_for(['Mainboard']),(223,32,164,141),(0,0,-1));caption(s,v,'背面封装、热界面及排线连接',208);s.save()

s=d.Sheet(8,'中框、双热管散热与内部电源',['原生中框提供主板、光驱和电源分区及固定支柱，处理器热界面连接均热板、弯曲热管和鳍片组。','后排轴流风扇与内部电源板各自独立，变压器、电感、滤波电容和保险丝只表示非功能性结构。'])
v=s.view_fit('FrameCooling',d.keys_for(['Frame','Cooling']),(24,32,175,151),(.3,-.6,1.8));caption(s,v,'中框支承、双热管、鳍片与后排风扇',209)
v=s.view_fit('PowerSupply',d.keys_for(['Power']),(225,31,151,151),(0,0,1));d.dimension_box(s,v,['PowerPCB'],'x',20);caption(s,v,'独立内部电源板与输入结构',209);s.save()

s=d.Sheet(9,'模拟输入、压力接点与双振动结构',['两个摇杆分别建立金属框架、双轴万向支架、电位器与按下开关；按钮采用独立硅胶膜和动静接点。','两侧不同尺寸电机带独立偏心配重、转轴和支座，线束绕过中央螺钉柱并避开接点膜折翼。'])
v=s.view_fit('ControllerPCB',starts('DS2PCB','DS2MCU','DS2MotorDriver','DS2FilmSocket','DS2Joy'),(22,29,176,88),(0,0,1));caption(s,v,'原生主板与两组模拟输入模块',132)
v=s.view_fit('ContactFilm',['DS2Flex','DS2DPadMembrane','DS2FaceMembrane','DS2MenuMembrane'],(222,29,158,88),(.2,-.5,2));caption(s,v,'柔性接点膜与三组按键胶膜',132)
v=s.view_fit('JoystickModule',starts('DS2Joy0'),(30,151,94,46),(.5,-1,1.4),up);caption(s,v,'万向支架与双电位器',211)
v=s.view_fit('RumbleMotors',without(starts('DS2Rumble'),'Wire'),(184,151,187,46),(.35,-1,1.6));caption(s,v,'不同尺寸电机与偏心配重',211);s.save()

s=d.Sheet(10,'记忆卡与原始连接附件',['黑色记忆卡包含分体外壳、卡扣、定位柱、带键槽主板、八枚金手指和同系列 NAND / 控制器示意封装。','日式 AC 电源线、AV MULTI 转三 RCA 线采用缩短展示路径，空白光盘只表示介质，不含软件或复制图案。'])
card=d.keys_for(['MemoryCard']);v=s.view_fit('MemoryCard',card,(25,29,89,139),(0,0,1));d.dimension_box(s,v,['CardFront','CardRear'],'x',20);d.dimension_box(s,v,['CardFront','CardRear'],'y',15);caption(s,v,'SCPH-10020 家族黑色记忆卡',208)
v=s.view_fit('MemoryCardBoard',without(card,'Front','Rear','Arrow','Family','Capacity','MemoryMark','MagicGate','Sony','Model'),(140,33,84,137),(0,0,1));caption(s,v,'带键槽主板与八枚金手指',208)
v=s.view_fit('ConnectionKit',d.keys_for(['Accessories']),(247,28,133,158),(0,0,1));caption(s,v,'电源、复合视频与空白介质',208);s.save()

s=d.Sheet(11,'组件索引与分组清单',['每个物理组件具有稳定标识、唯一编号、装配分组和显示材料，可与原生树及组件清单逐项对应。','组件条目可能包含多个实体，字符、引脚和线圈会增加实体数量；这些数量不等同于真实工厂物料表。'])
names={'Body':'阶梯外壳与固定','FrontIO':'前部卡槽及接口','Controls':'主机按键与指示','Ports':'后部接口与卡槽','Optical':'光驱机构及 RF 板','Mainboard':'GH-001 主板与器件','Shielding':'下部屏蔽','Frame':'中框及支承','Cooling':'热界面与散热','Power':'内部电源','Wiring':'主机线束与排线','Controller':'DualShock 2','MemoryCard':'8 MB 记忆卡','Accessories':'电源、AV 与介质'}
for x,t in [(12,'装配分组'),(111,'条目'),(151,'显示材料'),(268,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=33+i*11.6
 s.text(12,y,names.get(name,name),3.3);s.text(120,y,count,anchor='middle');s.text(151,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3.2);s.text(268,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.2);s.line((12,y+4),(384,y+4))
s.text(12,211,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体 · COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'版本依据、近似边界与重建入口',['本图册选择初代日版 SCPH-10000 主机、SCPH-10010 控制器家族和 SCPH-10020 记忆卡家族。','图纸是当前三维模型的快照，模型改动后需要同步更新投影、尺寸、组件清单、检查报告和网页。'])
sections=[(16,'资料与版本',['Sony SCPH-10000 原版说明书提供 301 × 182 × 78 mm 主体包络。','Dig and Rescue 与 Secret Base Manager 提供初代主机拆解。','awgs Foundry 与 RHMVY 提供后期同系列手柄和记忆卡照片。']),
 (67,'近似与内容边界',['控制器与记忆卡的局部尺寸及内部板型不能作为首发批次证明。','壳体分割、壁厚、孔位、元件、机构和线束均按学习用途近似绘制。','不复现制造公差、生产电路、游戏数据或经过验证的运动。']),
 (118,'可核对的检查记录',[f"{M['design_iterations']} 轮源码 / {M['physical_components']} 组件 / {M['solids']} 实体。",'完整重建、严格实体、装配求交和 STEP 回读分别保留报告。','字体、逐页视觉、模型尺寸与原生图纸引用随交付检查。']),
 (169,'继续修改的入口',['资料：references/SOURCES.md；清单：output/COMPONENTS.csv。','主要源码：tools/cadlib/ps2.py；逐轮入口：scripts/。','检查：output/reports/；修改后同步更新 CAD、图纸与网页。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
