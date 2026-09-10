"""Twelve A3 pages projected from the delivered Nintendo 64 native BReps."""
from pathlib import Path
import os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
repo=Path(__file__).resolve().parents[3];sys.path.insert(0,str(repo/'tools'))
from cadlib import drawings as d
import FreeCAD as App,Part

d.init_drawing(Path(__file__).resolve().parents[1]);C=d.C;M=d.M;up=(0,0,1)
def starts(*prefixes):return [k for k in C if k.startswith(prefixes)]
def caption(s,v,text,y):s.text(v['x'],y,text+f" · {v['scale']:.3f}:1",anchor='middle')
body=d.keys_for(M['envelope_groups'])
outer=list(dict.fromkeys(d.keys_for(['Body','Controls','CardReader','Power','Memory'],False)+d.keys_for(['Ports'])))
pad=['PadBack','PadFront','PadDPad','PadStart','PadA','PadB','PadCUp','PadCRight','PadCDown','PadCLeft','PadL','PadR','StickGuide','StickShaft','StickCap','PadNintendo','PadStartMark','PadAMark','PadBMark']+starts('PadArrow')

s=d.Sheet(1,'初代灰色主机总装与尺寸参考',['NUS-001 保留横向拱形上盖、四角低台、四个手柄口及对开的灰色卡槽防尘门。','官方主体参考为 260 × 190 × 73 mm，图示尺寸来自模型，局部孔位、曲面和内构为学习近似。'])
v=s.view_fit('ConsoleIsometric',outer,(18,30,169,155),(-.6,-1.3,1.3));caption(s,v,'拱形主机与原始接口',205)
v=s.view_fit('ConsoleTop',outer,(220,33,156,148),(0,0,1));d.dimension_box(s,v,['LowerHousing'],'x',20);d.dimension_box(s,v,['LowerHousing'],'y',208);caption(s,v,'四角低台外缘宽度与深度',205);s.save()

s=d.Sheet(2,'四路控制端口与后部连接',['正面四个控制端口各有三路触点，后面保留 Multi Out 和可拆电源模块。','接点、壳体和绝缘支承分别建模，插头与孔位为近似设计，不作为制造公差使用。'])
v=s.view_fit('ConsoleFront',outer,(30,31,158,66),(0,-1,0),up);d.dimension_box(s,v,outer,'y',20);caption(s,v,'正面与主机模型高度',115)
v=s.view_fit('ConsoleRear',outer,(221,31,158,66),(0,1,0),up);caption(s,v,'后面板与可拆电源',115)
v=s.view_fit('ThreeContactPort',starts('PortCup1','PortInsert1','PortContact1','PortDot1'),(26,149,100,47),(0,-1,0),up);d.dimension_box(s,v,['PortCup1'],'x',138);caption(s,v,'三接点手柄端口',207)
v=s.view_fit('MultiOut',starts('MultiOutHousing','MultiOutTongue','MultiOutContact'),(166,146,78,50),(0,1,0),up);caption(s,v,'十二接点 Multi Out',207)
v=s.view_fit('PowerConnector',starts('PowerSocket','PowerContact'),(292,146,76,50),(0,1,0),up);caption(s,v,'六位电源连接器',207);s.save()

s=d.Sheet(3,'原始三叉手柄与彩色按键',['NUS-005 采用三叉握柄，保留十字键、红色 START、蓝 A 绿 B、四颗黄色 C 键和八角摇杆口。','上下壳由闭合曲线剖面放样生成，后部包含九处主壳固定和两处扩展接口固定。'])
v=s.view_fit('ControllerIsometric',pad,(19,29,170,153),(.6,-.9,1.8));caption(s,v,'三叉曲线壳与八角导向',205)
v=s.view_fit('ControllerTop',pad,(230,31,142,80),(0,0,1));d.dimension_box(s,v,['PadBack'],'x',21);d.dimension_box(s,v,['PadBack'],'y',212);caption(s,v,'手柄学习包络',130)
v=s.view_fit('ControllerRear',['PadBack','PadZ']+starts('PadCaseScrew'),(244,144,115,58),(0,0,-1));caption(s,v,'背部 Z 键及固定孔',213);s.save()

s=d.Sheet(4,'光学摇杆、回中弹簧与 Z 键',['摇杆使用回中弹簧、交叉支承、开槽编码轮和独立光电元件，区别于电位器式结构。','本图展示组件关系，局部齿形、支承及电子布局为学习近似，不进行动态或电气性能验证。'])
optical=starts('Stick','Encoder');optical=[k for k in optical if k not in ['StickHousing','StickGuide'] and not k.startswith('EncoderWire')]
v=s.view_fit('OpticalStick',optical,(22,29,174,121),(.8,-1,1.0),up);caption(s,v,'移开外罩后的光学机构',169)
v=s.view_fit('CenteringSpring',['StickSpring'],(254,31,91,69),(1,0,0),up);d.dimension_box(s,v,['StickSpring'],'y',244);caption(s,v,'原生螺旋弹簧包络',117)
v=s.view_fit('ZTrigger',starts('PadZ','ZPCB','ZRubber','ZContact','ZPill'),(255,150,88,47),(1,0,.2),up);caption(s,v,'独立 Z 键、小板与硅胶',209);s.save()

s=d.Sheet(5,'主机与摇杆位置的实体剖面',['截面由保存的实体与给定 Y 平面相交生成，填充区域表示实际切到的材料。','主机截面解释卡座和壳体间隙，控制器截面显示弹簧、摇杆与三叉壳体的层次。'])
s.text(198,17,'A-A · Y=42 主机卡槽区域',4,'middle');v=d.section_view(s,'ConsoleSection',body,(18,33,358,57),offset=42);caption(s,v,'主机、连接器与屏蔽层',108)
s.text(198,134,'B-B · Y=-265 手柄摇杆区域',4,'middle');v=d.section_view(s,'ControllerSection',d.keys_for(['Controller']),(30,149,336,47),offset=-265);caption(s,v,'真实实体剖面 · 全部局部尺寸近似',211);s.save()

s=d.Sheet(6,'主机与手柄的分层爆炸总览',['爆炸装配使用交付文件中的组件位移，保持几何与零件编号的一一对应。','长线缆从此总览中省略，位移只用于观察分层，不表示真实拆卸路径。'])
keys=[k for k in d.keys_for(d.HH) if not any(t in k for t in ['Cable','Wire','Plug','Grommet'])]
v=s.view_fit('CompleteExploded',keys,(12,25,372,168),(1,-1,.8),exploded=True);caption(s,v,'机壳、板件、支承与控制器',211);s.save()

s=d.Sheet(7,'主板与主要芯片（NUS-CPU-04）',['内部参考 NUS-CPU-04 实物照片，表示 CPU、RCP、两片 RDRAM 及音视频和接口封装。','该板件参考属于初代外壳系列中的一个版本，不宣称复刻首批主板或原厂电路。'])
v=s.view_fit('Mainboard',d.keys_for(['Mainboard']),(24,29,174,153),(0,0,1));d.dimension_box(s,v,['MainPCB'],'x',18);d.dimension_box(s,v,['MainPCB'],'y',13);caption(s,v,'主板 · '+C['MainPCB'].PartNumber,204)
v=s.view_fit('ProcessorDetail',[k for k in starts('CPU') if C[k].Assembly=='Mainboard'],(248,29,116,72),(0,0,1));d.dimension_box(s,v,['CPU'],'x',20);caption(s,v,'CPU 封装与引脚',121)
v=s.view_fit('RDRAMDetail',starts('RDRAM'),(237,151,137,43),(0,0,1));caption(s,v,'两片 RDRAM 封装',209);s.save()

s=d.Sheet(8,'卡带总线与原始 Jumper Pak 终端',['Game Pak 插座包含两排共五十个接点，内存扩展接口包含三十六个接点。','Jumper Pak 是原始终端模块，内部使用终端电阻示意，没有增加额外 RAM。'])
v=s.view_fit('GamePakConnector',starts('GamePakSocket','GamePakContact','GamePakMount'),(23,34,169,73),(0,0,1));d.dimension_box(s,v,['GamePakSocket'],'x',20);caption(s,v,'五十位 Game Pak 接口',128)
v=s.view_fit('MemoryConnector',starts('MemorySocket','MemoryContact'),(230,34,143,71),(0,0,1));d.dimension_box(s,v,['MemorySocket'],'x',20);caption(s,v,'三十六位内存扩展口',128)
v=s.view_fit('JumperPak',starts('Jumper'),(38,151,147,44),(.7,-.9,1.2),up);caption(s,v,'原始黑色终端模块',210)
v=s.view_fit('JumperInternal',starts('JumperPCB','JumperFinger','JumperResistor'),(239,151,126,44),(0,1,0),up);caption(s,v,'金手指与终端板示意',210);s.save()

s=d.Sheet(9,'屏蔽、导热块与可拆电源',['主机保留上下金属屏蔽、三个独立导热块和折弯横梁，并分别表示紧固孔和螺钉。','电源模块的内部变压器、板件及电容为结构学习示意，不定义可制造电路或性能参数。'])
v=s.view_fit('ShieldStack',['LowerShield','CPUHeatBlock','RCPHeatBlock','RAMHeatBlock','CPUThermalPad','RCPThermalPad','RAMThermalPad'],(21,29,174,127),(.6,-1,1.3),up);caption(s,v,'下屏蔽与三处芯片导热块',177)
v=s.view_fit('PSUExterior',['PSULower','PSUUpper','PSURelease'],(236,33,135,62),(.5,-.8,1.4),up);caption(s,v,'可拆 NUS-002 电源模块',116)
v=s.view_fit('PSUInterior',[k for k in d.keys_for(['Power']) if k not in ['PSUUpper','PSURelease']],(245,149,116,45),(.5,-.8,1.4),up);caption(s,v,'供电模块内部示意',209);s.save()

s=d.Sheet(10,'空白卡带、存储卡与连接附件',['空白 Game Pak 包含双面金手指和两层金属屏蔽，可选 Controller Pak 包含电池及 SRAM 示意。','原始 AC 与立体声视频线展示连接关系，标签由项目原创，线长为收纳展示长度。'])
v=s.view_fit('BlankGamePak',[k for k in starts('Cart') if C[k].Assembly=='Accessories'],(25,30,163,91),(0,0,1));d.dimension_box(s,v,['CartBack'],'x',19);caption(s,v,'弧顶空白卡带 · 无游戏数据',140)
v=s.view_fit('ControllerPak',starts('MemPak'),(249,30,103,90),(0,0,1));d.dimension_box(s,v,['MemPakBack'],'x',19);caption(s,v,'可选电池备份存储卡',140)
v=s.view_fit('StereoLead',starts('VideoLead','VideoPlug','VideoSplit','RCABranch','RCAGrip','RCAShield','RCAPin'),(32,163,209,35),(0,0,1));caption(s,v,'立体声 Multi Out 转三 RCA',212)
v=s.view_fit('ACPlug',['ACPlug']+starts('ACBlade'),(293,164,65,33),(.6,-.7,1),up);caption(s,v,'日式双片插头',212);s.save()

s=d.Sheet(11,'组件、材料显示与装配索引',['零件编号贯穿原生工程、STEP 和网页网格，同一个组件可包含多枚引脚或文字实体。','显示材料用于区分结构，不指定材料牌号，组件条目和实体数量分别统计。'])
names={'Body':'机壳与标识','Controls':'主机控制件','Ports':'主机接口','CardReader':'卡座与防尘门','Power':'可拆供电模块','Mainboard':'主板和电子封装','Memory':'内存接口与终端','Shield':'屏蔽与散热','Internal':'主机支承与固定','Controller':'NUS-005 手柄','Accessories':'卡带、存储卡与线缆'}
for x,t in [(12,'装配分组'),(111,'条目'),(151,'显示材料'),(268,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=35+i*14.7
 s.text(12,y,names.get(name,name));s.text(120,y,count,anchor='middle');s.text(151,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3.2);s.text(268,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.2);s.line((12,y+4),(384,y+4))
s.text(12,210,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体 · COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'版本依据与可复现交付范围',['研究对象为初代灰色 NUS-001、NUS-005 手柄及原始 Jumper Pak，内部以 NUS-CPU-04 为参考。','图册是保存模型的版本快照，改变三维几何后需要同步重建投影、尺寸和验证报告。'])
sections=[(16,'来源与版本',['任天堂原始硬件页：主体尺寸、灰色控制器及接口说明。','iFixit 74923 与 Dig and Rescue：机身、控制器和附件实物照片。','NUS-CPU-04 是内部布局参考，不宣称复刻首批电路板。']),
 (67,'尺寸与内容边界',['官方主体参考为 260 × 190 × 73 mm，图中近似值来自实际模型。','孔位、壁厚、曲面与内部结构为学习设计，外伸线缆及附件另计。','卡带和存储卡无游戏数据，电源与电子封装不作为电路设计依据。']),
 (118,'可核对的验证记录',[f"{M['design_iterations']} 轮源码 / {M['physical_components']} 组件 / {M['solids']} 实体。",'原生实体、严格 BRep、完整重建、装配求交及 STEP 回读分别记录。','图册另外检查字体、内容覆盖、每页视觉以及原生尺寸引用。']),
 (169,'继续修改的入口',['资料：references/SOURCES.md；清单：output/COMPONENTS.csv。','源码：tools/cadlib/n64.py；各轮入口位于 scripts/。','检查：output/reports/；修改后同步更新 CAD、图纸与网页。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
