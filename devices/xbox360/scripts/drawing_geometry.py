"""Twelve A3 sheets projected from the original Xenon Xbox 360 and its early wireless controller BReps."""
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

s=d.Sheet(1,'原版 Xenon 白色主机与凹曲面机壳',['选择北美普通 Premium 20 GB / Xenon，保留原版白壳、镀铬盘口和侧置可拆硬盘。','309 × 258 × 83 mm 为近似工作包络，外置硬盘与突出部另计；本页尺寸均为模型测量。'])
v=s.view_fit('ConsoleIsometric',body,(17,28,186,154),(.4,-1.3,.9));caption(s,v,'原版横置主机与可拆硬盘',210)
v=s.view_fit('ConsoleTop',body,(230,35,151,142),(0,0,1));d.dimension_box(s,v,['Faceplate'],'x',20);d.dimension_box(s,v,body,'y',215);caption(s,v,'近似包络与模型深度',210);s.save()

s=d.Sheet(2,'原版前部接口与无 HDMI 后面板',['前部保留双记忆单元口、双 USB、配对键与四象限状态环；后部保留原版 AV 和专用 DC。','插座金属壳、绝缘件和接点独立建模；不混入后期 HDMI 接口，接点布局为非功能示意。'])
v=s.view_fit('ConsoleFront',body,(20,27,176,73),(0,-1,0),up);caption(s,v,'可拆面板与原版前部控制',118)
v=s.view_fit('ConsoleRear',body,(221,27,165,73),(0,1,0),up);caption(s,v,'双风扇排风与原版接口',118)
v=s.view_fit('FrontRadio',d.keys_for(['Wireless']),(26,142,155,57),(.2,-.7,1.5),up);caption(s,v,'前置无线与红外结构',212)
v=s.view_fit('Ports',d.keys_for(['Ports']),(221,142,162,57),(.1,1,.3),up);caption(s,v,'分离屏蔽、绝缘与端子',212);s.save()

s=d.Sheet(3,'原版白色双 AA 无线控制器',['曲线放样形成双握柄上下壳，保留不对称摇杆、Guide 环、专用充电口与七处背面紧固。','2005 年 FCC 原始申请及 Microsoft 手册指导结构；手柄局部曲率、机构与尺寸为学习近似。'])
v=s.view_fit('ControllerFront',pad,(22,27,205,151),(0,0,1));d.dimension_box(s,v,['PadBack','PadFront'],'x',20);d.dimension_box(s,v,['PadBack','PadFront'],'y',15);caption(s,v,'双摇杆、方向键与 ABXY',210)
v=s.view_fit('ControllerRear',pad,(250,30,132,89),(0,0,-1));caption(s,v,'可拆 AA 电池座与背壳',139)
v=s.view_fit('ControllerPorts',starts('PadCharge','PadSync'),(250,157,132,38),(.2,1,.5),up);caption(s,v,'原版专用充电口与配对键',212);s.save()

s=d.Sheet(4,'托盘式 DVD 与可拆 20 GB 硬盘',['托盘、加载传动、导杆、光头和独立控制板分别建模，空白光盘仅用于结构展示。','侧置硬盘保留卡扣、外壳、2.5 英寸驱动器及盘片结构；各内部尺寸均由照片指导近似。'])
optical=without(d.keys_for(['Optical']),'DVDTop','DVDMedia','DVDStudy','DVDClamp')
v=s.view_fit('OpticalMechanism',optical,(19,29,178,158),(0,0,1));caption(s,v,'托盘式加载与读取机构',211)
v=s.view_fit('HardDrive',without(d.keys_for(['Storage']),'HDDCaddy','HDDTrim','HDDCapacityMark','HDDMetalCover','HDDDriveLabel','HDDDriveMark','HDDCoverFastener'),(220,31,164,62),(-1,0,0),up);caption(s,v,'可拆硬盘内部结构',111)
v=s.view_fit('Pickup',starts('DVDPickup','DVDGuide','DVDFeed','DVDObjective'),(232,145,138,51),(.4,-1,1.5),up);caption(s,v,'光头、导杆与进给机构',212);s.save()

s=d.Sheet(5,'真实 BRep 生成的主机与控制器剖面',['剖面由保存实体与指定 Y 平面相交形成，填充只表示实际切到的材料。','主机剖面显示机壳、板层与热交换器；手柄剖面显示按键、输入机构、板件与上下壳。'])
s.text(198,17,'A-A · 主机 Y=-20',4,'middle');v=d.section_view(s,'ConsoleSection',body,(23,34,351,58),offset=-20);caption(s,v,'机壳、板层与处理器散热空间',114)
s.text(198,137,'B-B · 控制器 Y=-267（局部 Y=-7）',4,'middle');v=d.section_view(s,'ControllerSection',pad,(23,156,351,39),offset=-267);caption(s,v,'输入层、主板与握柄外壳',212);s.save()

s=d.Sheet(6,'分层爆炸总装与原生组件索引',['爆炸工程保留各独立实体与编号，以展示位移区分壳盖、板件、机械与输入结构。','本页略去部分长线和密集端子，完整原生工程、CSV 与网页保留全部零件。'])
v=s.view_fit('ConsoleExploded',without(body,'Wire','Lead','Ribbon','Contact','Mark'),(16,28,192,168),(.45,-.45,1.3),exploded=True);caption(s,v,'主机壳体与内部总成',212)
v=s.view_fit('ControllerExploded',without(pad,'Wire','Contact','Pin','Mark','Lead'),(221,29,162,166),(.3,-.7,1.3),exploded=True);caption(s,v,'双 AA 手柄的输入与无线结构',212);s.save()

s=d.Sheet(7,'原版 Xenon 双面主板与器件布局',['原版 Xenon 实机照片指导 CPU、GPU / eDRAM、双面内存、南桥与 ANA 布局。','芯片、被动器件、插座及焊点是非功能性学习几何，不复现制造电路或精确封装图。'])
v=s.view_fit('MainboardTop',d.keys_for(['Mainboard']),(23,31,169,144),(0,0,1));d.dimension_box(s,v,['MainPCB'],'x',20);d.dimension_box(s,v,['MainPCB'],'y',15);caption(s,v,'主板上面器件与电源调节',210)
v=s.view_fit('MainboardBottom',d.keys_for(['Mainboard']),(220,31,169,144),(0,0,-1));caption(s,v,'背面内存、焊点与安装孔',210);s.save()

s=d.Sheet(8,'早期双风扇散热与外置 203 W 电源',['早期 CPU 高鳍片与铜热管、GPU 低散热器和双后风扇分别建模，不加入后期 GPU 延伸热管。','电源强制风冷架构有原版拆解文字依据；内部排布、风机和磁性件为非功能性结构示意。'])
v=s.view_fit('Cooling',without(d.keys_for(['Cooling']),'AirDuct'),(20,29,177,153),(.25,-.5,1.8));caption(s,v,'原版双处理器热交换器',210)
v=s.view_fit('PowerSupply',without(starts('Brick'),'BrickTop','BrickLabel','BrickShieldTop','BrickDCCord','BrickDCGrip','BrickDCShield','BrickDCCarrier','BrickDCPower','BrickDCControl','BrickDCLatch','BrickDCRelief'),(221,29,161,153),(0,0,1));d.dimension_box(s,v,['BrickPCB'],'x',18);caption(s,v,'外置电源板与分离变换部件',210);s.save()

s=d.Sheet(9,'原版无线手柄的输入、射频和双 AA 供电',['双摇杆具有双轴架、电位器与按下开关；黑色扳机支架、独立回位弹簧与导电胶分别建模。','早期主板保留分离射频子板；两种尺寸的偏心电机与反向安装的两枚 AA 电池独立可查。'])
v=s.view_fit('ControllerPCB',starts('PadPCB','PadBaseband','PadRF','PadJoy'),(17,28,87,78),(.15,-.3,2));caption(s,v,'正面双轴输入',124)
v=s.view_fit('ControllerRadio',starts('PadPCB','PadBaseband','PadRF','PadJoy'),(110,28,87,78),(.15,-.3,-2));caption(s,v,'背面主控与射频子板',124)
v=s.view_fit('Membranes',starts('PadFaceMembrane','PadDPadMembrane'),(221,28,160,78),(.2,-.5,2));caption(s,v,'共用面键膜与独立方向膜',124)
v=s.view_fit('Triggers',starts('PadTrigger'),(28,145,127,51),(.7,-.4,1.2),up);caption(s,v,'转轴、电位器与回位弹簧',213)
v=s.view_fit('BatteryMotors',starts('PadAA','PadRumble'),(216,145,164,51),(.3,-.6,1.8));caption(s,v,'两种偏心电机与双 AA 电池座',213);s.save()

s=d.Sheet(10,'原配单耳耳机与六 RCA 连接套装',['北美普通套装含单耳耳机、六 RCA Component HD AV、网线及接地 AC 线，线长均缩短展示。','保留耳机原版音量/静音适配器和 AV 插头的光纤口；不加入限时遥控器或另售充电附件。'])
v=s.view_fit('Headset',starts('Headset'),(20,28,180,78),(0,0,1));caption(s,v,'头戴式单耳耳机与原版适配器',124)
v=s.view_fit('ConnectionKit',starts('Component','LAN','AC'),(221,28,163,78),(0,0,1));caption(s,v,'视频、网线与接地 AC',124)
v=s.view_fit('HeadsetAdapter',starts('HeadsetAdapter','HeadsetVolume','HeadsetMute','HeadsetPlug'),(36,147,143,46),(.3,-.7,2));caption(s,v,'手柄端音量与静音控制',212)
v=s.view_fit('ComponentPlug',without(starts('Component'),'Cable','Branch','Splitter','RCA'),(237,146,128,48),(.3,-1,.8),up);caption(s,v,'宽 AV 插头与数字光纤口',212);s.save()

s=d.Sheet(11,'组件分组、唯一编号与原生索引',['每个物理组件具有稳定标识、唯一编号、装配分组和显示材料，可与原生树及 COMPONENTS.csv 对应。','一个条目可能包含多个实体；字符、端子和绕组增加实体数量，这些数量不等同于工厂物料表。'])
names={'Body':'凹曲面原版机壳','Frame':'金属底盘与支承','Controls':'面板控制与状态环','Ports':'原版连接接口','Mainboard':'Xenon 主板与器件','Cooling':'双风扇与处理器散热','Optical':'托盘光驱与控制','Shielding':'屏蔽与固定','Storage':'可拆 20 GB 硬盘','Wiring':'主机线束与排线','Wireless':'前置无线与红外','Controller':'原版双 AA 无线手柄','Accessories':'外置电源与原配附件'}
for x,t in [(12,'装配分组'),(111,'条目'),(151,'显示材料'),(268,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=32+i*10.8
 s.text(12,y,names.get(name,name),3.2);s.text(120,y,count,anchor='middle');s.text(151,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3.2);s.text(268,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.2);s.line((12,y+3.8),(384,y+3.8))
s.text(12,213,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体 · COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'版本资料、近似边界与重建入口',['图册选择普通 Premium 20 GB / Xenon 和 2005 年原版无线手柄；版本与配件据原始手册交叉核对。','图纸来自当前三维实体，修改后须同步更新投影、尺寸、组件清单、检查报告及网页网格。'])
sections=[(16,'资料与版本',['Microsoft 2005 手册和首发公告确定原版功能及套装范围。','Copetti、Ben Heck 的原版实机照片指导 Xenon 机构布局。','2005 FCC 原始手柄照片与后期变更说明用于区分板型。']),
 (67,'近似与内容边界',['309 × 258 × 83 mm 是近似工作包络，外置硬盘和突出部另计。','曲率、壁厚、元件、孔位、线束与传动间隙均按学习用途近似。','203 W 电源内部为结构示意，不复现制造公差或实际电气功能。']),
 (118,'可核对的检查记录',[f"{M['design_iterations']} 轮源码 / {M['physical_components']} 组件 / {M['solids']} 实体。",'源码重建、严格实体、装配求交与 STEP 回读分别保留报告。','图册字体、逐页视觉、模型尺寸与原生图纸引用随交付检查。']),
 (169,'继续修改的入口',['资料：references/SOURCES.md；清单：output/COMPONENTS.csv。','源码：tools/cadlib/xbox360.py；逐轮入口：scripts/。','检查：output/reports/；修改后同步 CAD、图纸及网页。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
