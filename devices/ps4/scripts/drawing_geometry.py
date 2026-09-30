"""Twelve A3 sheets projected from the original PS4 study BReps."""
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

s=d.Sheet(1,'初代斜面主机总装与近似包络',['CUH-1000A 保留平行斜面、分层腰线、亮面硬盘盖、磨砂顶壳和前部吸入式光盘入口。','Sony 发布规格约宽 275、深 305、高 53 mm，不含最大突出部；图示深度为当前模型的几何测量。'])
v=s.view_fit('ConsoleIsometric',body,(18,29,173,153),(.5,-1.6,1.25));caption(s,v,'分体上盖与斜面机身',208)
v=s.view_fit('ConsoleTop',body,(225,35,150,145),(0,0,1));d.dimension_box(s,v,['HDDCover','UpperHousing'],'x',20,published=True);d.dimension_box(s,v,body,'y',214);caption(s,v,'公开近似宽度与模型深度',208);s.save()

s=d.Sheet(2,'前部触控与原版后部接口',['前部包含吸入式盘口、两组 USB 3.0、电源及出仓触控条，通风口与连接口均切入壳体。','后部保留 HDMI、光纤、LAN、AUX 摄像头口与 AC 电源入口；接点和壳体间隙为学习近似。'])
v=s.view_fit('ConsoleFront',body,(24,28,166,72),(0,-1,0),up);d.dimension_box(s,v,['LowerHousing','UpperHousing','Foot0'],'y',14,published=True);caption(s,v,'盘口、双 USB 与触控条',119)
v=s.view_fit('ConsoleRear',body,(224,28,161,72),(0,1,0),up);caption(s,v,'数字音视频、网络与附件连接',119)
v=s.view_fit('USBFront',starts('USB0'),(29,144,148,53),(0,-1,0),up);caption(s,v,'USB 3.0 屏蔽壳、舌片与接点',211)
v=s.view_fit('RearPorts',d.keys_for(['Ports']),(225,143,160,54),(.15,1,.35),up);caption(s,v,'后接口独立组件',211);s.save()

s=d.Sheet(3,'初代 DualShock 4 与四处后壳固定',['原生曲线截面放样形成双握柄及摇杆杯，正面保留不透光触摸板、方向键、符号键和凹面摇杆帽。','CUH-ZCT1 公开尺寸约 162 × 98 × 52 mm；本页尺寸对应模型壳体，不含所有突出按键。'])
v=s.view_fit('ControllerFront',pad,(26,28,201,146),(0,0,1));d.dimension_box(s,v,['DS4Back','DS4Front'],'x',20);d.dimension_box(s,v,['DS4Back','DS4Front'],'y',15);caption(s,v,'初代触摸板、扬声器与双模拟输入',207)
v=s.view_fit('ControllerRear',pad,(252,32,122,82),(0,0,-1));caption(s,v,'四处螺钉与型号标识',132)
v=s.view_fit('ControllerPorts',starts('DS4Light','DS4USB','DS4Micro'),(257,150,117,47),(.15,1,.45),up);caption(s,v,'后灯条与 Micro-USB 充电接口',211);s.save()

s=d.Sheet(4,'吸入式光驱与可抽取硬盘托架',['光驱包含吸入滚轮、装载电机及齿轮、光头导杆、进给轴系和独立控制板，媒体用空白圆盘表示。','2.5 英寸硬盘具有分体壳、托架、盘片与读写臂示意，独立 SATA 插座连接主板，局部结构为静态近似。'])
optical=without(d.keys_for(['Optical']),'Cover','Media','Clamp')
v=s.view_fit('OpticalMechanism',optical,(20,28,175,156),(0,0,1));caption(s,v,'移开光盘与上盖后的机构',209)
v=s.view_fit('HardDrive',without(d.keys_for(['Storage']),'DiskCover'),(245,32,114,107),(0,0,1));d.dimension_box(s,v,['HDDBase'],'x',20);d.dimension_box(s,v,['HDDBase'],'y',223);caption(s,v,'托架与硬盘内部结构',155)
v=s.view_fit('Pickup',starts('Pickup','Feed','Objective','Focus'),(245,170,114,30),(.5,-1,1.3),up);caption(s,v,'光头、导杆与进给机构',211);s.save()

s=d.Sheet(5,'主机与控制器的真实实体剖面',['剖面由保存的三维实体与指定 Y 平面相交生成，填充仅表示实际切到的材料。','主机截面展示光驱、散热及分层板件；控制器截面展示壳体、接点膜、胶膜与输入件的间隙。'])
s.text(198,17,'A-A · 主机 Y=-55 光驱与风扇区域',4,'middle');v=d.section_view(s,'ConsoleSection',body,(23,34,351,56),offset=-55);caption(s,v,'媒体、散热、主板及机壳',112)
s.text(198,136,'B-B · 控制器 Y=-230 按键区域',4,'middle');v=d.section_view(s,'ControllerSection',pad,(23,155,351,40),offset=-230);caption(s,v,'按键、胶膜、接点膜及上下壳',211);s.save()

s=d.Sheet(6,'主机与控制器的分层爆炸结构',['爆炸工程保留完整实体、稳定零件标识和编号，通过展示位移区分外壳、板件、机构和输入层。','本页省略长线束及密集外观文字以便观察层次；完整工程、组件清单和三维预览保留全部零件。'])
v=s.view_fit('ConsoleExploded',without(body,'Lead','Harness','Ribbon','Flex','Legend','Mark','Badge'),(17,29,192,167),(.5,-.45,1.3),exploded=True);caption(s,v,'壳体、存储、光驱与分层板件',211)
v=s.view_fit('ControllerExploded',without(pad,'Mark','Symbol','Fixed','Pin','Label','Model','Lead','Flex'),(221,32,157,160),(.3,-.7,1.3),exploded=True);caption(s,v,'壳体、主板、胶膜与双摇杆',211);s.save()

s=d.Sheet(7,'双面主板、处理器与显存',['原生 L 形主板避让硬盘舱，APU 位于散热接触面；十六枚显存分别分布在主板两侧。','桥接、网络、音频、供电和时钟电池按首发拆解布局建立，器件封装与板料通道为非功能性示意。'])
v=s.view_fit('MainboardTop',d.keys_for(['Mainboard']),(26,32,164,141),(0,0,1));d.dimension_box(s,v,['MainPCB'],'x',20);d.dimension_box(s,v,['MainPCB'],'y',15);caption(s,v,'上侧显存、供电与主要接口',208)
v=s.view_fit('MainboardUnderside',d.keys_for(['Mainboard']),(223,32,164,141),(0,0,-1));caption(s,v,'APU、另一侧显存与热接触区域',208);s.save()

s=d.Sheet(8,'离心风扇、双热管与内部电源',['离心叶轮、风道、热界面、两根热管和鳍片分别建模，保持与板件及机壳的独立装配关系。','内置电源具有通风盖、原生板件、变压器、滤波元件与保险丝，器件和隔离布局仅供结构学习。'])
v=s.view_fit('Cooling',d.keys_for(['Cooling']),(24,32,175,151),(.3,-.6,1.8));caption(s,v,'离心叶轮、风道与热交换器',209)
v=s.view_fit('PowerSupply',without(d.keys_for(['Power']),'PSUCover'),(225,31,151,151),(0,0,1));d.dimension_box(s,v,['PSUPCB'],'x',20);caption(s,v,'内部电源板与输入结构',209);s.save()

s=d.Sheet(9,'控制器输入、触摸连接与双振动结构',['两组摇杆包含双轴支架、电位器与按下开关，方向键和面键通过硅胶回弹件连接接点膜。','触摸与充电板由排线连接主板；电池、大小不同的振动电机、偏心配重和引线分别建模。'])
v=s.view_fit('ControllerPCB',starts('DS4PCB','DS4MCU','DS4MotorDriver','DS4Joy'),(22,29,176,88),(0,0,1));caption(s,v,'原生主板与模拟输入模块',132)
v=s.view_fit('ContactFilm',['DS4ControlFilm','DS4DirectionalMembrane','DS4ActionMembrane'],(222,29,158,88),(.2,-.5,2));caption(s,v,'柔性接点膜与按键胶膜',132)
v=s.view_fit('JoystickModule',starts('DS4Joy0'),(30,151,94,46),(.5,-1,1.4),up);caption(s,v,'双轴支架、电位器及按下机构',211)
v=s.view_fit('BatteryRumble',without(starts('DS4Rumble','DS4Battery'),'Lead','Mark','Header'),(184,151,187,46),(.35,-1,1.6));caption(s,v,'电池、托架与不等尺寸振动电机',211);s.save()

s=d.Sheet(10,'原配线缆与单耳语音附件',['2013 年官方 FAQ 确认套装包含 AC、HDMI、Micro-USB 和单耳耳机，模型线缆均采用缩短展示路径。','单耳耳机侧向 MIC 开关及独立线夹参考后期同系列官方指南；内部板件、扬声器和夹簧为学习近似。'])
v=s.view_fit('ConnectionKit',d.keys_for(['Accessories']),(22,29,180,164),(0,0,1));caption(s,v,'原始套装的四组连接附件',208)
v=s.view_fit('USBAPlug',starts('USBAPlug'),(247,29,105,45),(0,1,0),up);d.dimension_box(s,v,['USBAPlugShield'],'x',20);caption(s,v,'USB-A 独立屏蔽与四枚接点',92)
v=s.view_fit('MonoMic',starts('MonoMic','MonoClip'),(247,113,105,44),(.4,-.5,1.8));caption(s,v,'MIC 开关与独立线夹',173)
v=s.view_fit('TRRSPlug',starts('MonoPlug'),(252,182,95,16),(0,0,1),(1,0,0));caption(s,v,'四段耳机插头与绝缘环',211);s.save()

s=d.Sheet(11,'组件索引与分组清单',['每个物理组件具有稳定标识、唯一编号、装配分组和显示材料，可与原生树及组件清单逐项对应。','组件条目可能包含多个实体，字符、引脚和线圈会增加实体数量；这些数量不等同于真实工厂物料表。'])
names={'Body':'斜面外壳与固定','FrontIO':'前部盘口及接口','Controls':'触控及状态指示','Ports':'后部信号及电源口','Optical':'吸入光驱及控制板','Mainboard':'L 形主板与器件','Shielding':'上下屏蔽与热界面','Frame':'中框及支承','Cooling':'离心风扇与散热','Power':'内部电源','Storage':'硬盘及独立托架','Wiring':'主机线束与排线','Controller':'初代 DualShock 4','Accessories':'线缆及单耳耳机'}
for x,t in [(12,'装配分组'),(111,'条目'),(151,'显示材料'),(268,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=33+i*11.6
 s.text(12,y,names.get(name,name),3.3);s.text(120,y,count,anchor='middle');s.text(151,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3.2);s.text(268,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.2);s.line((12,y+4),(384,y+4))
s.text(12,211,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体 · COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'版本依据、近似边界与重建入口',['本图册选择 2013 年 CUH-1000A 初代主机与 CUH-ZCT1 控制器，附件以官方原配清单为依据。','图纸是当前三维模型的快照，模型改动后需要同步更新投影、尺寸、组件清单、检查报告和网页。'])
sections=[(16,'资料与版本',['Sony 2013 发布规格给出约 275 × 305 × 53 mm 主体包络。','iFixit 首发主机与 JDM-001 控制器拆解提供结构布局依据。','2013 官方 FAQ 确认套装；后期指南仅指导单耳耳机局部外形。']),
 (67,'近似与内容边界',['Sony 主体尺寸原注为暂定、近似，且不含最大突出部。','壳体分割、壁厚、孔位、元件、机构和线束均按学习用途近似绘制。','不复现制造公差、生产电路、游戏数据或经过验证的运动。']),
 (118,'可核对的检查记录',[f"{M['design_iterations']} 轮源码 / {M['physical_components']} 组件 / {M['solids']} 实体。",'完整重建、严格实体、装配求交和 STEP 回读分别保留报告。','字体、逐页视觉、模型尺寸与原生图纸引用随交付检查。']),
 (169,'继续修改的入口',['资料：references/SOURCES.md；清单：output/COMPONENTS.csv。','主要源码：tools/cadlib/ps4.py；逐轮入口：scripts/。','检查：output/reports/；修改后同步更新 CAD、图纸与网页。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
