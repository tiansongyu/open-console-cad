"""Twelve A3 sheets projected from the original disc PS5 and DualSense BReps."""
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
body=d.keys_for(M['envelope_groups']);pad=d.keys_for(['Controller'])

s=d.Sheet(1,'首发光驱版 PS5 与双曲面可拆白罩',['选择 2020 年 CFI-1000A 系列原版光驱机，双白罩、中框和光驱侧非对称起伏均保留原生构造。','Sony 首发 FAQ 给出约宽 390、深 260、高 104 mm 主体包络，不含底座；局部曲率为照片指导近似。'])
v=s.view_fit('ConsoleIsometric',body,(17,28,186,154),(.4,-1.3,.9));caption(s,v,'横置原版光驱机',210)
v=s.view_fit('ConsoleTop',body,(230,35,151,142),(0,0,1));d.dimension_box(s,v,['UpperCover','LowerCover'],'x',20,published=True);d.dimension_box(s,v,body,'y',215);caption(s,v,'主体宽度与模型深度',210);s.save()

s=d.Sheet(2,'原版前后接口与贯通通风结构',['前部为 USB-A、USB-C、电源及出仓按钮、吸入式光盘口和蓝色状态导光结构。','后部为双 USB-A、LAN、HDMI 和 AC；本页仅对应首发机型，插座内部接点和孔位为学习近似。'])
v=s.view_fit('ConsoleFront',body,(20,27,176,73),(0,-1,0),up);d.dimension_box(s,v,['UpperCover','LowerCover'],'y',15);caption(s,v,'原版盘口与前置接口',118)
v=s.view_fit('ConsoleRear',body,(221,27,165,73),(0,1,0),up);caption(s,v,'后部五组连接与排风栅格',118)
v=s.view_fit('FrontUSB',[k for k in d.keys_for(['FrontIO']) if k.startswith(('FrontUSB','USBC'))],(26,142,155,57),(0,-1,0),up);caption(s,v,'前置 USB-A 与可逆 USB-C',212)
v=s.view_fit('RearPorts',d.keys_for(['Ports']),(221,142,162,57),(.1,1,.3),up);caption(s,v,'独立屏蔽、绝缘和接点',212);s.save()

s=d.Sheet(3,'初代 DualSense 与分离的中央饰板',['原生曲线放样形成双握柄白壳，黑色可拆饰板环绕双摇杆，保留白色触摸板和蓝色边缘导光。','Sony 首发 FAQ 给出 DualSense 约 160 × 106 × 66 mm；本页尺寸为当前曲面壳体的模型测量。'])
v=s.view_fit('ControllerFront',pad,(22,27,205,151),(0,0,1));d.dimension_box(s,v,['SenseBack','SenseFront'],'x',20);d.dimension_box(s,v,['SenseBack','SenseFront'],'y',15);caption(s,v,'方向键、触摸板、符号键与静音键',210)
v=s.view_fit('ControllerRear',pad,(250,30,132,89),(0,0,-1));caption(s,v,'后壳、四组固定与声学开口',139)
v=s.view_fit('ControllerPorts',starts('SenseUSB','SenseAudio','SenseCharge'),(250,157,132,38),(.2,1,.5),up);caption(s,v,'USB-C、耳机与充电触点',212);s.save()

s=d.Sheet(4,'光驱装载机构与原版空 M.2 仓',['吸入滚轮、加载齿轮、凸轮、光头导杆、连续螺旋进给轴和独立光驱控制板分别建模。','M.2 仓保持原始未加装 SSD 状态，含独立盖板、安装座、收纳螺丝和带键插座；局部尺寸为学习近似。'])
optical=without(d.keys_for(['Optical']),'DriveHousing','DriveTopCover','DriveCoverScrew','OpticalDeck')
v=s.view_fit('OpticalMechanism',optical,(19,29,178,158),(0,0,1));caption(s,v,'移开壳盖与机构架后的驱动结构',211)
v=s.view_fit('M2Expansion',without(d.keys_for(['Storage']),'M2Cover'),(220,31,164,62),(0,0,1));d.dimension_box(s,v,['M2Bay'],'x',17);d.dimension_box(s,v,['M2Bay'],'y',214);caption(s,v,'带键连接器与空扩展仓',111)
v=s.view_fit('Pickup',starts('Pickup','Focus','Feed','Objective'),(232,145,138,51),(.4,-1,1.5),up);caption(s,v,'光头和独立进给部件',212);s.save()

s=d.Sheet(5,'保存实体生成的主机与手柄剖面',['剖面由保存的真实 BRep 实体与指定 Y 平面相交形成，填充只表示实际切到的材料。','剖面用于核对光驱、主板、冷却层与机壳，以及手柄按键、胶膜、板件和白色外壳之间的关系。'])
s.text(198,17,'A-A · 主机 Y=-55',4,'middle');v=d.section_view(s,'ConsoleSection',body,(23,34,351,58),offset=-55);caption(s,v,'光驱、板层与散热空间',114)
s.text(198,137,'B-B · DualSense Y=-261（局部 Y=24）',4,'middle');v=d.section_view(s,'ControllerSection',pad,(23,156,351,39),offset=-261);caption(s,v,'面键、回弹膜、接点膜与支架',212);s.save()

s=d.Sheet(6,'分层爆炸总装与原生零件标识',['爆炸工程保留独立实体、稳定标识和编号，以展示位移区分白罩、内框、板件、机构和输入层。','本页省略部分长线束与密集接点，完整工程、组件清单和三维预览保留全部零件。'])
v=s.view_fit('ConsoleExploded',without(body,'Harness','Ribbon','Coax','Contact','Tail','Mark'),(16,28,192,168),(.45,-.45,1.3),exploded=True);caption(s,v,'双罩、中框与内部总成',212)
v=s.view_fit('ControllerExploded',without(pad,'Lead','Ribbon','Contact','Pin','Mark','Symbol','Fixed'),(221,29,162,166),(.3,-.7,1.3),exploded=True);caption(s,v,'白壳、饰板、反馈和输入层',212);s.save()

s=d.Sheet(7,'双面主板、APU、显存与 NAND',['主板风扇缺口、后接口和固定柱开孔保留原生历史，APU 位于下侧液金接触区域。','八枚 GDDR6、双面 NAND、供电器件、桥接和无线封装按拆解布局建立，局部电路与封装为非功能性示意。'])
v=s.view_fit('MainboardTop',d.keys_for(['Mainboard']),(23,31,169,144),(0,0,1));d.dimension_box(s,v,['MainPCB'],'x',20);d.dimension_box(s,v,['MainPCB'],'y',15);caption(s,v,'显存、供电与线束插座',210)
v=s.view_fit('MainboardBottom',d.keys_for(['Mainboard']),(220,31,169,144),(0,0,-1));caption(s,v,'APU、NAND 与热界面',210);s.save()

s=d.Sheet(8,'双面进风、六根热管与靴形电源',['风扇框、23 片叶片、转子、轴承、定子齿和线圈保持独立，APU 接触板和六根弯曲热管连接两组鳍片。','原生靴形电源包含电容、变压器、环形磁芯、保险管与独立插座，内部结构为非功能性学习模型。'])
v=s.view_fit('Cooling',without(d.keys_for(['Cooling']),'UpperFanGuard'),(20,29,177,153),(.25,-.5,1.8));caption(s,v,'双面进风风扇与热交换器',210)
v=s.view_fit('PowerSupply',without(d.keys_for(['Power']),'PowerLid'),(221,29,161,153),(0,0,1));d.dimension_box(s,v,['PowerPCB'],'x',18);caption(s,v,'原生电源板与变换器件',210);s.save()

s=d.Sheet(9,'手柄输入、自适应扳机与音圈反馈',['双摇杆保留金属笼、双轴支架、电位器和按下开关，面键通过硅胶穹顶与柔性接点膜输入。','扳机电机、蜗杆、阻力凸轮与音圈执行器分别建模；传动间隙与内部截面为静态学习近似。'])
v=s.view_fit('ControllerPCB',starts('SensePCB','SenseMCU','SenseJoy'),(22,28,174,78),(0,0,1));caption(s,v,'主板与双轴模拟输入',124)
v=s.view_fit('ContactFilm',['SenseContactFilm','SenseDirectionMembrane','SenseActionMembrane'],(221,28,160,78),(.2,-.5,2));caption(s,v,'接点膜与回弹穹顶',124)
v=s.view_fit('AdaptiveTrigger',without(starts('SenseRight'),'Haptic'),(28,145,127,51),(.7,-.4,1.2),up);caption(s,v,'电机、蜗杆与独立传感器板',213)
v=s.view_fit('BatteryHaptics',without(starts('SenseBattery','SenseLeftHaptic','SenseRightHaptic'),'Lead','Socket','Contact','Mark'),(216,145,164,51),(.3,-.6,1.8));caption(s,v,'1500 mAh 电池与双音圈反馈',213);s.save()

s=d.Sheet(10,'原版旋转底座与三组连接线',['首发原配为底座、DualSense、AC 电源线、HDMI 和 USB-A 至 USB-C 线，不含耳机。','底座保留旋转盘、后缘挂钩、橡胶支承与螺丝收纳；线缆采用缩短展示路径，插头局部尺寸为近似。'])
v=s.view_fit('ConnectionKit',d.keys_for(['Accessories']),(20,27,180,164),(0,0,1));caption(s,v,'AC、十九接点 HDMI 与 USB-A/C',211)
v=s.view_fit('OriginalBase',d.keys_for(['Stand']),(235,30,135,77),(.35,-.8,1.8));caption(s,v,'旋转盘、双后钩与收纳结构',126)
v=s.view_fit('USBCPlug',starts('USBCPlug'),(245,151,115,38),(0,1,0),up);d.dimension_box(s,v,['USBCPlugShield'],'x',144);caption(s,v,'USB-C 金属壳、绝缘轨与独立触点',213);s.save()

s=d.Sheet(11,'组件分组、唯一编号与原生索引',['每个物理组件具有稳定标识、唯一编号、装配分组和显示材料，可与原生树及 COMPONENTS.csv 对应。','一个条目可能包含多个实体；字符、端子和绕组增加实体数量，这些数量不等同于工厂物料表。'])
names={'Body':'双曲面白色外罩','Frame':'中框与支承','FrontIO':'前部接口与电路板','Controls':'按钮与状态指示','Ports':'原版后部连接口','Stand':'旋转底座与固定','Mainboard':'主板与主要器件','Cooling':'双面风扇与散热','Power':'靴形内部电源','Optical':'吸入光驱与控制','Shielding':'上下屏蔽与固定','Storage':'空 M.2 扩展仓','Wiring':'主机线束与排线','Wireless':'独立天线结构','Controller':'初代 DualSense','Accessories':'原配连接线'}
for x,t in [(12,'装配分组'),(111,'条目'),(151,'显示材料'),(268,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=32+i*10.8
 s.text(12,y,names.get(name,name),3.2);s.text(120,y,count,anchor='middle');s.text(151,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3.1);s.text(268,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.1);s.line((12,y+3.8),(384,y+3.8))
s.text(12,213,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体 · COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'版本资料、近似边界与重建入口',['图册选择 CFI-1000A 系列原版光驱 PS5 与初代 DualSense；外观和原配套装以 Sony 首发资料为依据。','图纸来自当前三维实体，修改后须同步更新投影、尺寸、组件清单、检查报告及网页网格。'])
sections=[(16,'资料与版本',['Sony 2020 首发 FAQ 给出主机、DualSense 的近似尺寸和套装清单。','Sony 官方拆机与 iFixit 首发拆解提供整体结构及器件布局依据。','光驱维修资料仅用于原版外壳家族结构，不断言精确首批板号。']),
 (67,'近似与内容边界',['390 × 260 × 104 mm 主体参考包络不含原版底座。','曲率、壁厚、元件、孔位、线束与传动间隙均按学习用途近似。','不复现制造公差、生产电路、游戏数据或经过验证的力反馈。']),
 (118,'可核对的检查记录',[f"{M['design_iterations']} 轮源码 / {M['physical_components']} 组件 / {M['solids']} 实体。",'源码重建、严格实体、装配求交与 STEP 回读分别保留报告。','图册字体、逐页视觉、模型尺寸与原生图纸引用随交付检查。']),
 (169,'继续修改的入口',['资料：references/SOURCES.md；清单：output/COMPONENTS.csv。','源码：tools/cadlib/ps5.py；逐轮入口：scripts/。','检查：output/reports/；修改后同步 CAD、图纸及网页。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
