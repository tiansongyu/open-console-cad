"""Twelve A3 sheets projected from the original CECHA00 PS3 and motorless SIXAXIS BReps."""
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

s=d.Sheet(1,'原版 CECHA00 与拱形亮面上盖',['选择日本首发 60 GB CECHA00，保留四 USB、三格式读卡器与原版亮面拱顶。','Sony 给出约宽 325、深 274、高 98 mm，最大突出部不计；局部曲率、壁厚与孔位为学习近似。'])
v=s.view_fit('ConsoleIsometric',body,(17,28,186,154),(.4,-1.3,.9));caption(s,v,'原版横置主机',210)
v=s.view_fit('ConsoleTop',body,(230,35,151,142),(0,0,1));d.dimension_box(s,v,['GlossCrown'],'x',20,published=True);d.dimension_box(s,v,body,'y',215);caption(s,v,'参考包络与模型深度',210);s.save()

s=d.Sheet(2,'四 USB、读卡器与原版后部接口',['前部四组 USB 与三格式读卡器分别建立金属屏蔽、绝缘舌和独立接点。','后部保留 AV MULTI、HDMI、LAN、光纤音频与接地 AC 插座；内部端子均为非功能性近似。'])
v=s.view_fit('ConsoleFront',body,(20,27,176,73),(0,-1,0),up);caption(s,v,'前置盘口、控制与读卡区域',118)
v=s.view_fit('ConsoleRear',body,(221,27,165,73),(0,1,0),up);caption(s,v,'原版后部连接口',118)
v=s.view_fit('FrontIO',without(d.keys_for(['FrontIO']),'CardReaderFlap','DiscBrush'),(26,142,155,57),(.2,-.7,1.5),up);caption(s,v,'USB 与三格式读卡板',212)
v=s.view_fit('RearPorts',d.keys_for(['Ports']),(221,142,162,57),(.1,1,.3),up);caption(s,v,'分离屏蔽、绝缘和端子',212);s.save()

s=d.Sheet(3,'早期无振动 SIXAXIS 无线控制器',['曲线放样形成双握柄上下壳，保留 PS 键独立压环、Mini-B 与四个编号指示灯。','早期独立运动传感板、复位延长件与电池依据拆解建立；本页尺寸为模型测量，不是制造图。'])
v=s.view_fit('ControllerFront',pad,(22,27,205,151),(0,0,1));d.dimension_box(s,v,['SIXBack','SIXFront'],'x',20);d.dimension_box(s,v,['SIXBack','SIXFront'],'y',15);caption(s,v,'方向键、符号键与双模拟输入',210)
v=s.view_fit('ControllerRear',pad,(250,30,132,89),(0,0,-1));caption(s,v,'五组壳体固定与复位开口',139)
v=s.view_fit('ControllerPorts',starts('SIXMini','SIXPlayerLED','SIXPlayerGuide'),(250,157,132,38),(.2,1,.5),up);caption(s,v,'Mini-B 与独立导光结构',212);s.save()

s=d.Sheet(4,'吸入式光驱与可抽取硬盘托架',['加载滚轮、齿轮、导杆、光头与驱动电路板分别建模；保留光驱壳盖与支承机构。','60 GB 机型硬盘采用独立托架；局部机械与电子细节由拆解指导近似。'])
optical=without(d.keys_for(['Optical']),'DriveTopCover','DriveCoverScrew','DriveMedia','DriveClamp')
v=s.view_fit('OpticalMechanism',optical,(19,29,178,158),(0,0,1));caption(s,v,'移开壳盖与示意光盘后的加载机构',211)
v=s.view_fit('HardDrive',without(d.keys_for(['Storage']),'DiskCover'),(220,31,164,62),(0,0,1));caption(s,v,'移开盖板的硬盘与抽取托架',111)
v=s.view_fit('Pickup',starts('Pickup','Focus','Feed','Objective'),(232,145,138,51),(.4,-1,1.5),up);caption(s,v,'光头与独立进给结构',212);s.save()

s=d.Sheet(5,'真实 BRep 生成的主机与控制器剖面',['剖面由保存实体与指定 Y 平面相交形成，填充仅表示实际切到的材料。','主机剖面显示壳体、板层和内部机构；控制器剖面显示按键、膜片、支承与上下壳。'])
s.text(198,17,'A-A · 主机 Y=-55',4,'middle');v=d.section_view(s,'ConsoleSection',body,(23,34,351,58),offset=-55);caption(s,v,'机壳、板层与机构空间',114)
s.text(198,137,'B-B · SIXAXIS Y=-243（局部 Y=7）',4,'middle');v=d.section_view(s,'ControllerSection',pad,(23,156,351,39),offset=-243);caption(s,v,'输入层、板件与外壳',212);s.save()

s=d.Sheet(6,'分层爆炸总装与原生组件索引',['爆炸工程保留各独立实体与编号，以展示位移区分壳盖、板件、机械与输入结构。','本页略去部分长线和密集端子，完整原生工程、CSV 与网页保留全部零件。'])
v=s.view_fit('ConsoleExploded',without(body,'Lead','Ribbon','Coax','Contact','Tail','Mark'),(16,28,192,168),(.45,-.45,1.3),exploded=True);caption(s,v,'拱形机壳与内部总成',212)
v=s.view_fit('ControllerExploded',without(pad,'Lead','Contact','Pin','Mark','Symbol'),(221,29,162,166),(.3,-.7,1.3),exploded=True);caption(s,v,'无振动控制器的输入与无线结构',212);s.save()

s=d.Sheet(7,'双面主板与 COK-001 布局学习',['以原版维修资料及同代拆解指导布局，分别保留 Cell、RSX、内存与早期兼容芯片结构。','芯片、被动器件、插座及焊点是非功能性学习几何，不复现制造电路或精确封装图。'])
v=s.view_fit('MainboardTop',d.keys_for(['Mainboard']),(23,31,169,144),(0,0,1));d.dimension_box(s,v,['MainPCB'],'x',20);d.dimension_box(s,v,['MainPCB'],'y',15);caption(s,v,'主板上面器件与接口',210)
v=s.view_fit('MainboardBottom',d.keys_for(['Mainboard']),(220,31,169,144),(0,0,-1));caption(s,v,'背面器件、热界面与固定通道',210);s.save()

s=d.Sheet(8,'底部风扇、热管与内部金属电源',['原版冷却结构采用独立风扇叶片、热管、接触板和鳍片；线束沿板层通道布置。','电源板与壳盖分别建模，含变压器、电容、磁芯、保险管与连接端子。'])
v=s.view_fit('Cooling',d.keys_for(['Cooling']),(20,29,177,153),(.25,-.5,1.8));caption(s,v,'风扇与热交换器',210)
v=s.view_fit('PowerSupply',without(d.keys_for(['Power']),'PowerLid'),(221,29,161,153),(0,0,1));d.dimension_box(s,v,['PowerPCB'],'x',18);caption(s,v,'电源板与独立变换器件',210);s.save()

s=d.Sheet(9,'早期 SIXAXIS 输入、运动传感与电池',['双摇杆具有双轴架、电位器、触点与按下开关；按键通过硅胶穹顶和柔性接点膜传递压力。','保留早期独立三线运动传感板、610 mAh 电池与弹簧回位 L2/R2；不含振动电机。'])
v=s.view_fit('ControllerPCB',starts('SIXPCB','SIXControl','SIXCharge','SIXCrystal','SIXBypass','SIXJoy'),(22,28,174,78),(.15,-.3,-2));caption(s,v,'主板与双轴模拟输入',124)
v=s.view_fit('ContactFilm',starts('SIXFlex','SIXDPadMembrane','SIXFaceMembrane'),(221,28,160,78),(.2,-.5,2));caption(s,v,'柔性接点膜与回弹结构',124)
v=s.view_fit('Triggers',starts('SIXL2','SIXR2'),(28,145,127,51),(.7,-.4,1.2),up);caption(s,v,'转轴与独立回位弹簧',213)
v=s.view_fit('BatterySensor',starts('SIXBattery','SIXMotion'),(216,145,164,51),(.3,-.6,1.8));caption(s,v,'电池与三线运动传感板',213);s.save()

s=d.Sheet(10,'日本原版 AC、AV、USB 与 LAN 套装',['日本快速参考列出 AC、AV、USB 与 LAN 线；接地说明明确独立接地尾线。','所有线长均缩短展示；插头、金属端子、护线套分别建模，不提供电气制造数据。'])
v=s.view_fit('ConnectionKit',d.keys_for(['Accessories']),(20,27,180,164),(0,0,1));caption(s,v,'四组原配连接线',211)
v=s.view_fit('MiniB',starts('MiniBPlug'),(235,30,135,77),(.2,2,.4));caption(s,v,'Mini-B 金属壳与五接点',126)
v=s.view_fit('GroundedAC',starts('ACWall','ACEarth'),(245,151,115,38),(.3,-.6,1.5));caption(s,v,'日式双片插头与接地尾线',213);s.save()
s=d.Sheet(11,'组件分组、唯一编号与原生索引',['每个物理组件具有稳定标识、唯一编号、装配分组和显示材料，可与原生树及 COMPONENTS.csv 对应。','一个条目可能包含多个实体；字符、端子和绕组增加实体数量，这些数量不等同于工厂物料表。'])
names={'Body':'原版拱形外壳','Frame':'中框与支承','FrontIO':'前部接口与电路板','Controls':'按钮与状态指示','Ports':'原版后部连接口','Stand':'旋转底座与固定','Mainboard':'主板与主要器件','Cooling':'风扇与热管散热','Power':'内部金属电源','Optical':'吸入光驱与控制','Shielding':'上下屏蔽与固定','Storage':'硬盘与抽取托架','Wiring':'主机线束与排线','Wireless':'独立天线结构','Controller':'早期 SIXAXIS','Accessories':'原配连接线'}
for x,t in [(12,'装配分组'),(111,'条目'),(151,'显示材料'),(268,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=32+i*10.8
 s.text(12,y,names.get(name,name),3.2);s.text(120,y,count,anchor='middle');s.text(151,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3.2);s.text(268,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.2);s.line((12,y+3.8),(384,y+3.8))
s.text(12,213,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体 · COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'版本资料、近似边界与重建入口',['图册选择 CECHA00 原版 60 GB PS3 与早期 SIXAXIS；外观和原配套装以 Sony 原版手册为依据。','图纸来自当前三维实体，修改后须同步更新投影、尺寸、组件清单、检查报告及网页网格。'])
sections=[(16,'资料与版本',['Sony 日本原版手册及快速参考给出主体包络与套装清单。','Sony 维修资料与 iFixit 原版拆解提供机构及 COK-001 布局依据。','SIXAXIS 同代拆解用于无振动结构；不宣称精确制造尺寸。']),
 (67,'近似与内容边界',['325 × 274 × 98 mm 主体参考包络不含最大突出部。','曲率、壁厚、元件、孔位、线束与传动间隙均按学习用途近似。','不复现制造公差、生产电路、游戏数据或实际电气功能。']),
 (118,'可核对的检查记录',[f"{M['design_iterations']} 轮源码 / {M['physical_components']} 组件 / {M['solids']} 实体。",'源码重建、严格实体、装配求交与 STEP 回读分别保留报告。','图册字体、逐页视觉、模型尺寸与原生图纸引用随交付检查。']),
 (169,'继续修改的入口',['资料：references/SOURCES.md；清单：output/COMPONENTS.csv。','源码：tools/cadlib/ps3.py；逐轮入口：scripts/。','检查：output/reports/；修改后同步 CAD、图纸及网页。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
