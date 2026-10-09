"""Twelve A3 sheets from saved Japanese SHVC-001 and original SHVC-005 BReps."""
from pathlib import Path
import os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
repo=Path(__file__).resolve().parents[3];sys.path.insert(0,str(repo/'tools'))
from cadlib import drawings as d
import FreeCAD as App,Part

d.init_drawing(Path(__file__).resolve().parents[1]);C=d.C;M=d.M;up=(0,0,1)
def starts(*p):return [k for k in C if k.startswith(p)]
def without(keys,*p):return [k for k in keys if not any(v in k for v in p)]
def caption(s,v,t,y):s.text(v['x'],y,t+f" · {v['scale']:.3f}:1",anchor='middle')
body=d.keys_for(M['envelope_groups']);pad=without(d.keys_for(['Controller1']),'Pad1Cable','Pad1Plug','Pad1Strain')

s=d.Sheet(1,'日版 SHVC-001 原版外壳与名义包络',['选择早期 SHVC-CPU-01 与独立 SHVC-SOUND，保留浅灰曲面外壳和独立深灰顶面板。','200 × 242 × 74 mm 依据日版说明书规格；局部曲率、壁厚、孔位及机构尺寸为近似。'])
v=s.view_fit('ConsoleIso',body,(18,29,181,157),(.35,-1.0,1.2));caption(s,v,'原版 POWER / EJECT / RESET 布局',210)
v=s.view_fit('ConsoleTop',body,(230,34,150,145),(0,0,1));d.dimension_box(s,v,['BottomShell'],'x',20,published=True);d.dimension_box(s,v,body,'y',215,published=True);caption(s,v,'日版原机顶面与名义尺寸',210);s.save()

s=d.Sheet(2,'双手柄接口与原版后部连接区',['前面板保留两只七触点控制器插座，底部具有独立可拆的 28 接点扩展口盖。','背面按原版照片布置 MULTI OUT、RF OUT、CH1/CH2 与 DC IN；各连接器接点独立。'])
v=s.view_fit('ConsoleFront',body,(21,29,175,75),(0,-1,0),up);caption(s,v,'前部控制器插座与状态灯',122)
v=s.view_fit('ConsoleRear',body,(220,29,166,75),(0,1,0),up);caption(s,v,'原版后置接口和竖向通风孔',122)
v=s.view_fit('ConsoleBottom',without(body,'BottomLabel','BottomModelMark'),(22,148,171,48),(0,0,-1));caption(s,v,'被动通风、扩展盖和外壳螺钉',213)
v=s.view_fit('Ports',d.keys_for(['Ports','FrontPanel']),(222,147,160,49),(.1,-1,.5),up);caption(s,v,'独立接口与前板结构',213);s.save()

s=d.Sheet(3,'原版 SHVC-005 狗骨形有线手柄',['选择实物照片所示 1992 年双移位寄存器板；日版主机配两只同型手柄。','保留四色凸面 ABXY、十字方向键、斜置 Start/Select 与 L/R 肩键，局部尺寸近似。'])
v=s.view_fit('PadFront',pad,(24,35,203,127),(0,0,1));d.dimension_box(s,v,['Pad1Bottom','Pad1Top'],'x',20);d.dimension_box(s,v,['Pad1Bottom','Pad1Top'],'y',15);caption(s,v,'四色键、肩键和原版轮廓',211)
v=s.view_fit('PadBack',pad,(249,35,135,78),(0,0,-1));caption(s,v,'五枚后盖螺钉与分离壳体',132)
v=s.view_fit('PadPlug',starts('Pad1Plug','Pad1Strain'),(251,156,132,40),(.2,.8,1.1));caption(s,v,'七接点插头与护套',212);s.save()

s=d.Sheet(4,'62P 上下连接器与退卡机构',['任天堂维修手册将卡带连接区列为上下两个 62P 连接器，模型保留可拆上下壳体。','防尘盖、钢轴、回位扭簧、白色退卡摇臂及电源联动锁分别表达；未作动力学验证。'])
v=s.view_fit('CartConnector',without(d.keys_for(['CartridgeInterface']),'CartridgeFlap','FlapRidge','FlapPivot','FlapSpring'),(19,31,177,91),(.25,-.6,1.7));caption(s,v,'上下连接壳体和独立 62P 接点',140)
v=s.view_fit('EjectMechanism',d.keys_for(['EjectMechanism']),(220,31,164,91),(.2,-.5,1.5));caption(s,v,'摇臂、长钢轴与电源联动锁',140)
v=s.view_fit('CartFlap',starts('CartridgeFlap','FlapRidge','FlapPivot','FlapSpring'),(22,165,171,31),(.1,-.4,1.3));caption(s,v,'单片防尘盖和独立扭簧',213)
v=s.view_fit('TopControls',starts('PowerCap','ResetCap','EjectCap','PowerSwitch','ResetStem','ResetSwitch'),(222,165,159,31),(.1,-.5,1.7));caption(s,v,'顶端控制和传力件',213);s.save()

s=d.Sheet(5,'由保存实体生成的主机与手柄剖面',['剖面由 BRep 与指定 Y 平面实际相交生成，剖面填充只对应切到的真实材料。','主机展示卡槽/板件/外壳层次；手柄展示上下壳、PCB、橡胶膜及按键柱。'])
s.text(198,17,'A-A · 主机 Y=27',4,'middle');v=d.section_view(s,'ConsoleSection',body,(23,34,351,58),offset=27);caption(s,v,'卡槽连接区和主板支承层次',114)
s.text(198,137,'B-B · 第一只手柄 Y=-209',4,'middle');v=d.section_view(s,'PadSection',pad,(23,156,351,39),offset=-209);caption(s,v,'狗骨形壳腔与输入机构',212);s.save()

s=d.Sheet(6,'原生分层爆炸与两只独立手柄',['原生爆炸工程保留稳定组件编号、材料和展示位移，各组可与 CSV 清单对应。','本页省略部分密集引脚、线缆与标识；完整原生文件及网页保留全部组件。'])
v=s.view_fit('ConsoleExploded',without(body,'Lead','Contact','Mark','Wire','Passive'),(16,28,192,168),(.45,-.45,1.3),exploded=True);caption(s,v,'原版主机壳体、屏蔽与内部板件',212)
v=s.view_fit('PadExploded',without(pad,'Trace','Lead','Mark','Contact','Passive'),(221,29,162,166),(.3,-.7,1.3),exploded=True);caption(s,v,'原版手柄壳体与输入分层',212);s.save()

s=d.Sheet(7,'早期 SHVC-CPU-01 主板与分立芯片',['依据原版拆机照片保留 S-CPU、两片 S-PPU、WRAM、两片 VRAM 与独立视频编码器。','主板轮廓、被动器件和背面小器件为照片指导的学习近似，不是完整电路或原厂 BOM。'])
v=s.view_fit('MainboardTop',d.keys_for(['Mainboard']),(23,31,169,144),(0,0,1));d.dimension_box(s,v,['MainPCB'],'x',20);d.dimension_box(s,v,['MainPCB'],'y',15);caption(s,v,'独立 CPU / PPU / 存储器',210)
v=s.view_fit('MainboardBack',d.keys_for(['Mainboard']),(220,31,169,144),(0,0,-1));caption(s,v,'板背结构与安装避让孔',210);s.save()

s=d.Sheet(8,'独立 SHVC-SOUND 与 RF / 稳压区域',['早期主板采用独立屏蔽声卡，包含 S-SMP、S-DSP、两片 RAM、DAC 与放大器。','RF 调制器、大电容屏蔽框和稳压散热片保留原版位置关系；电气功能不在模型范围内。'])
v=s.view_fit('SoundModule',without(d.keys_for(['SoundModule']),'SoundShieldLid','SoundLidMark','SoundAmpMark'),(20,30,176,145),(0,0,1));d.dimension_box(s,v,['SoundPCB'],'x',20);caption(s,v,'打开屏蔽盖的独立声卡',211)
v=s.view_fit('RFPower',without(d.keys_for(['RF','Power']),'RFLid','RFCanMark','PowerSwitch') + [k for k in starts('MainCap') if C[k].Shape.CenterOfMass.y > 45 and C[k].Shape.CenterOfMass.x < 0],(221,30,160,75),(.1,-.4,2));caption(s,v,'RF 与电容/稳压屏蔽结构',124)
v=s.view_fit('FrontRibbon',starts('FrontPCB','FrontRibbon','FrontFerrite','MainRibbon'),(221,145,160,52),(.3,-.6,1.5));caption(s,v,'前板扁平排线、磁芯及泡棉',213);s.save()

s=d.Sheet(9,'手柄双芯片板、导电胶与肩键机构',['控制器内部依据原版 1992 年 PCB 照片，保留两片移位寄存器和一体式肩键板端。','十字键、ABXY、Start/Select 与 L/R 橡胶接触件分别呈现；线路与行程仅为结构近似。'])
v=s.view_fit('PadPCBTop',starts('Pad1PCB','Pad1CarbonTrace','Pad1LShoulderTrace','Pad1RShoulderTrace'),(19,29,178,72),(0,0,1));caption(s,v,'主按键与肩键印刷接点',122)
v=s.view_fit('PadPCBBack',starts('Pad1PCB','Pad1Shift','Pad1Passive'),(221,29,160,72),(0,0,-1),(0,-1,0));caption(s,v,'两片移位寄存器及背面器件',122)
v=s.view_fit('PadRubber',starts('Pad1DpadMembrane','Pad1ABXYMembrane','Pad1StartSelectMembrane','Pad1MenuDome','Pad1MenuCarbon','Pad1DpadCarbon','Pad1ABXYCarbon'),(21,146,176,50),(.1,-.4,1.7));caption(s,v,'独立橡胶膜与导电触点',213)
v=s.view_fit('PadShoulders',starts('Pad1LKey','Pad1RKey','Pad1LPivot','Pad1RPivot','Pad1LRubber','Pad1RRubber','Pad1LCarbon','Pad1RCarbon'),(221,146,160,50),(.2,-.5,1.4));caption(s,v,'肩键、枢轴和独立胶帽',213);s.save()

s=d.Sheet(10,'另售 HVC-002 线性适配器与 SHVC-008',['日版原装主机含两只控制器，HVC-002 AC 适配器和 SHVC-008 AV 线另售。','实物照片指导线性变压器、整流滤波板和灰色 MULTI OUT / 三色 RCA；线缆缩短展示。'])
v=s.view_fit('AdapterOutside',starts('AC'),(20,29,176,74),(.25,-.5,1.7));caption(s,v,'另售原版线性适配器和 DC 插头',124)
v=s.view_fit('AdapterInside',without(starts('AC'),'ACUpper','ACModelMark','ACTypeMark','ACRatingMark','ACDCCord','ACDCGrip','ACDCBarrel','ACCordRelief'),(221,29,160,74),(0,0,1));caption(s,v,'铁芯、绝缘线包和整流滤波板',124)
v=s.view_fit('AVCable',starts('AVPlug','AVStrand','RCA'),(23,146,355,50),(.1,-.5,1.8));caption(s,v,'MULTI OUT 与黄 / 白 / 红 RCA 独立接点',213);s.save()

s=d.Sheet(11,'组件分组、唯一编号与原生清单',['每个物理组件具有稳定标识、唯一编号、分组与材料，可与原生树及 CSV 一一核对。','字符等条目可能含多个实体，组件与实体数量不等同于原厂物料表。'])
names={'Body':'日版原版外壳','Controls':'操作键与指示件','Mainboard':'早期主板与芯片','CartridgeInterface':'卡槽上下连接器','SoundModule':'独立屏蔽声卡','Power':'开关与原版电源区','RF':'RF 调制模块','Ports':'后置与扩展接口','FrontPanel':'前板与手柄接口','Wiring':'线束、排线及磁芯','EjectMechanism':'退卡与锁定机构','Shielding':'原版金属屏蔽','Fixings':'螺钉与支柱','Controller1':'第一只 SHVC-005','Controller2':'第二只 SHVC-005','Accessories':'另售 AC / AV 学习件'}
for x,t in [(12,'装配分组'),(111,'条目'),(151,'显示材料'),(268,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=31+i*10.2
 s.text(12,y,names.get(name,name),3.2);s.text(120,y,count,anchor='middle');s.text(151,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3.2);s.text(268,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.2);s.line((12,y+3.5),(384,y+3.5))
s.text(12,213,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体 · COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'资料、版本边界与继续重建',['本册选择早期日版 SHVC-001、独立声卡与 1992 年原版 SHVC-005 手柄板。','所有投影来自保存的实体，修改后须同步 CAD、图纸、尺寸、清单、报告和网页网格。'])
sections=[(16,'一手资料与版本选择',['日版使用说明书规格提供 200 × 242 × 74 mm 包络及原装双手柄配置。','任天堂 1992 年维修手册指导上下 62P 连接器、排线磁芯和退卡结构。','早期主板、声卡、原版手柄与 HVC-002 拆机照片指导机械分件。']),
 (67,'近似及附件边界',['局部曲率、孔位、封装、机构尺寸及线缆展示路线均近似。','采用有独立声卡的早期主板，不混入后期 1CHIP 或迷你复刻版。','AC / AV 为另售学习件；电路、线缆与电源均非功能性模型。']),
 (118,'可查对的交付记录',[f"{M['design_iterations']} 轮源码 / {M['physical_components']} 组件 / {M['solids']} 实体。",'源码重建、严格实体、装配求交及 STEP 回读分别保留报告。','原生图纸、字体、逐页视觉、尺寸和网页随交付一起核对。']),
 (169,'继续修改入口',['资料：references/SOURCES.md；清单：output/COMPONENTS.csv。','源码：tools/cadlib/sfc.py；逐轮入口：scripts/。','检查：output/reports/；修改后同步 CAD、图册与网页。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
