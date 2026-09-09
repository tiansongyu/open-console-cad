"""Twelve A3 study sheets projected from the delivered Atari native BReps."""
from pathlib import Path
import os,sys,math
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
repo=Path(__file__).resolve().parents[3];sys.path.insert(0,str(repo/'tools'))
from cadlib import drawings as d
import FreeCAD as App,Part

d.init_drawing(Path(__file__).resolve().parents[1]);C=d.C;M=d.M;up=(0,0,1)
def starts(*prefixes):return [k for k in C if k.startswith(prefixes)]
def caption(s,v,text,y):s.text(v['x'],y,text+f" · {v['scale']:.3f}:1",anchor='middle')
def controller(n,external=False):
 keys=d.keys_for(['Controller'+str(n)],not external)
 if external:keys+=starts('J'+str(n)+'PlugContact')
 return list(dict.fromkeys(keys))
body=d.keys_for(M['envelope_groups'])
main=d.keys_for(d.HH)
external=d.keys_for(['Body','Controls','Ports'],False)+['CartridgeGuide']+starts('ControllerPin')
external=list(dict.fromkeys(external))

s=d.Sheet(1,'六开关主机总装与学习包络',['CX2600 Heavy Sixer 学习模型，保留木纹前脸、六开关和厚壁圆弧底壳。','主机工作包络由当前实体测得，线缆、独立手柄与附件另计；全部尺寸为近似学习值。'])
v=s.view_fit('ConsoleIsometric',external,(17,30,170,157),(-.7,-1.3,1.7));caption(s,v,'木纹六开关主机',206)
v=s.view_fit('ConsoleTop',external,(219,32,157,150),(0,0,1));d.dimension_box(s,v,body,'x',19);d.dimension_box(s,v,body,'y',207);caption(s,v,'宽 × 深，包含表面标识',206);s.save()

s=d.Sheet(2,'前后接口与主体高度',['后部包含两组 DE-9、3.5 mm 电源接口及固定 RF 线；主机前部保留木纹饰板。','尺寸按 X 宽、Y 深、Z 高记录；接口与孔位均为当前模型的学习几何。'])
v=s.view_fit('ConsoleFront',external,(22,30,169,69),(0,-1,0),up);d.dimension_box(s,v,body,'y',12);caption(s,v,'正面与主体高度',116)
v=s.view_fit('ConsoleRear',external,(217,30,166,69),(0,1,0),up);caption(s,v,'原始后面板接口',116)
v=s.view_fit('DE9Rear',starts('ControllerSocket0','ControllerPin0_','ControllerSurround0'),(20,147,110,45),(0,1,0),up);caption(s,v,'DE-9 手柄接口',204)
v=s.view_fit('DCPower',starts('PowerJack'),(159,143,66,52),(0,1,0),up);caption(s,v,'3.5 mm 电源口',204)
v=s.view_fit('RFPlug',starts('RFPlug'),(264,148,112,41),(.5,-1,.6),up);caption(s,v,'固定 RF 线末端 RCA 插头',204);s.save()

s=d.Sheet(3,'初代 CX10 外观与刚性摇杆',['两只 CX10 均使用单红按钮、橙色方向环和顶部六角标牌，保留初代无 TOP 字样的外观。','刚性摇杆盘、弹簧柱、橡胶防尘套与机壳独立建模；分层视图用于说明装配关系。'])
v=s.view_fit('CX10Isometric',controller(1,True),(19,28,175,154),(.7,-1.3,1.5));caption(s,v,'CX10 独立操控器',203)
v=s.view_fit('CX10Side',controller(2,True),(224,28,152,76),(1,0,0),up);d.dimension_box(s,v,['J2Bottom','J2Handle','J2HexBadge','J2BadgeText']+starts('J2Foot'),'y',216);caption(s,v,'摇杆总高',119)
v=s.view_fit('CX10Top',['J1Bottom','J1Frame','J1Top','J1Boot','J1OrangeRing','J1Fire','J1Handle','J1HexBadge','J1BadgeText'],(235,143,131,53),(0,0,1));d.dimension_box(s,v,['J1Bottom'],'x',136);caption(s,v,'90 mm 基座学习尺寸',211);s.save()

s=d.Sheet(4,'摇杆 CX10 的弹簧与传动机构',['每只 CX10 具有四个方向弹簧及一个发射按钮弹簧，作用于独立的五指传动板。','PCB 接点、叶簧、弹簧杯与六芯线束分开记录；电气连接不作为可制造电路使用。'])
inner=starts('J1PCB','J1Actuator','J1Spring','J1Contact','J1Harness','J1Signal')
v=s.view_fit('CX10Internal',inner,(23,31,159,93),(0,0,1));d.dimension_box(s,v,['J1PCB'],'x',20);d.dimension_box(s,v,['J1PCB'],'y',12);caption(s,v,'PCB 与五指传动板',139)
v=s.view_fit('CX10Spring',['J1Spring0'],(256,33,79,87),(1,0,0),up);d.dimension_box(s,v,['J1Spring0'],'y',243);caption(s,v,'原生螺旋弹簧',139)
keys=[k for k in controller(1) if not any(t in k for t in ['Cable','SignalWire','Plug'])]
v=s.view_fit('CX10Exploded',keys,(20,158,356,42),(1,0,.2),exploded=True);caption(s,v,'操控器分层爆炸 · 原生位移横向展开',211);s.save()

s=d.Sheet(5,'主机实体剖面与层叠关系',['剖面由保存的 BRep 实体与给定 Y 平面相交生成，浅色填充为被切到的材料。','两个截面分别说明主逻辑区与卡带连接器区域；图示不是测绘得到的原厂截面。'])
s.text(198,17,'A-A · Y=-31 主逻辑区域',4,'middle');v=d.section_view(s,'MainSection',body,(18,31,358,62),offset=-31);caption(s,v,'机壳、屏蔽罩与芯片层叠',109)
s.text(198,136,'B-B · Y=43 卡带连接器',4,'middle');v=d.section_view(s,'CardSection',body,(18,149,358,44),offset=43);caption(s,v,'卡座与双板区域的真实实体截面',209);s.save()

s=d.Sheet(6,'主机与双摇杆的爆炸总览',['爆炸装配沿组件清单中的层次展开，几何来自随项目交付的原生爆炸文件。','位移用于区分观察层次，不表示真实拆卸路径；长线缆在此视图中省略。'])
keys=[k for k in main if C[k].Assembly not in ['Cables','Wiring'] and not any(t in k for t in ['SignalWire','Plug','Cable'])]
v=s.view_fit('FullConsoleExploded',keys,(12,25,372,169),(1,-1,.9),up,exploded=True);caption(s,v,'整机、屏蔽与两只 CX10',210);s.save()

s=d.Sheet(7,'主逻辑板与 24 接点卡座',['窄长主板包括 6507、6532 RIOT、TIA 与 CD4050 封装示意，并保留穿孔引脚和焊盘。','卡带接口具有两排共 24 个接点；芯片位置、封装和 PCB 尺寸均为学习近似。'])
v=s.view_fit('LogicPCB',d.keys_for(['Mainboard']),(24,28,169,154),(0,0,1));d.dimension_box(s,v,['Mainboard'],'x',18);d.dimension_box(s,v,['Mainboard'],'y',13);caption(s,v,'主板 · '+C['Mainboard'].PartNumber,202)
v=s.view_fit('CardReader',[k for k in d.keys_for(['CardReader']) if k!='CartridgeGuide'],(233,31,142,64),(.6,-1,1.2));caption(s,v,'移开导向口后的 24 接点卡座',116)
v=s.view_fit('CPUDetail',['CPU','CPUPins','CPUMark','CPUSolderLands'],(238,145,132,44),(.3,-.8,1.7));caption(s,v,'6507 封装 · '+C['CPU'].PartNumber,209);s.save()

s=d.Sheet(8,'独立开关板、电源与 RF 模块',['六开关版本采用独立开关板，12 芯排线连接主板；电源和 RF 部件位于开关板上。','稳压器、滤波电容、调谐线圈和可拆金属罩分别表示，不计算电气或热性能。'])
theta=math.atan2(36,67);normal=(0,-math.sin(theta),math.cos(theta))
keys=d.keys_for(['Switchboard','PowerRF']);keys=[k for k in keys if k!='RFCan']
v=s.view_fit('SwitchboardPlane',keys,(20,34,182,121),normal,up);d.dimension_box(s,v,['Switchboard'],'x',20);d.dimension_box(s,v,['Switchboard'],'y',12);caption(s,v,'U 形开关板 · '+C['Switchboard'].PartNumber,174)
v=s.view_fit('Regulator',starts('Regulator'),(247,31,112,63),normal,up);caption(s,v,'78M05 与散热片',112)
v=s.view_fit('RFModule',starts('RFCoil','RFTransistor','RFDisc','RFTrimmer'),(246,143,116,43),(.9,-1.1,1),up);caption(s,v,'调谐线圈与离散器件',204);s.save()

s=d.Sheet(9,'旋钮 CX30-04 与电位器结构',['两只旋钮控制器通过 Y 形线缆共用一个插头，保留早期 ATARI 与网球拍标识。','电位器内部分为外壳、阻值轨道、转子和轴，标称阻值依据原厂维修手册的 1 MΩ 记录。'])
v=s.view_fit('PaddleExterior',starts('Pad1'),(23,28,149,113),(0,0,1));d.dimension_box(s,v,['Pad1Bottom'],'x',18);caption(s,v,'早期旋钮控制器俯视',159)
pot=starts('Pad1Pot','Pad1Resistance','Pad1Wiper');pot=[k for k in pot if k not in ['Pad1PotCan','Pad1PotLid']]
v=s.view_fit('Potentiometer',pot,(225,28,152,87),(.5,-.8,1.5));caption(s,v,'1 MΩ 电位器内部示意',136)
v=s.view_fit('SharedPaddleLead',starts('PaddleY','PaddleShared','PaddlePlug'),(44,168,310,36),(0,0,1));caption(s,v,'共用 Y 接头与 DE-9 插头',212);s.save()

s=d.Sheet(10,'学习卡带、适配器与电视切换盒',['空白卡带包含 24 接点和 ROM 封装示意，使用原创标签，不包含游戏数据或封面。','适配器内部为通用结构示意；TV/GAME 切换盒按同代接口关系建模，尺寸并非原厂制造数据。'])
v=s.view_fit('BlankCartridge',[k for k in starts('Cart') if C[k].Assembly=='Accessories'],(24,28,148,137),(0,0,1));d.dimension_box(s,v,['CartBack'],'x',18);d.dimension_box(s,v,['CartBack'],'y',12);caption(s,v,'空白卡带 · 24 接点',186)
v=s.view_fit('PowerAdapter',starts('Adapter','Transformer'),(217,29,164,62),(.5,-.8,1.5));caption(s,v,'9 V / 500 mA 适配器示意',111)
v=s.view_fit('TVGameBox',starts('TVBox'),(221,146,157,42),(.3,-1,1.5));caption(s,v,'天线端子、RCA 与双线输出',208);s.save()

s=d.Sheet(11,'组件、显示材料与装配索引',['组件编号贯穿原生工程、STEP 与组件清单；同一条目可包含多枚引脚或文字实体。','材料名称表示显示角色，不指定材料牌号或物理性能；组件数和实体数分别统计。'])
names={'Body':'机壳与标识','Controls':'主机操作件','Ports':'主机接口','Cables':'外接 RF 线','Mainboard':'主逻辑板','Switchboard':'开关板及机构','Shield':'主板屏蔽结构','CardReader':'卡带连接器','Wiring':'内部线束','PowerRF':'电源与 RF 模块','Controller1':'一号 CX10','Controller2':'二号 CX10','Accessories':'旋钮、卡带、电源及 RF 附件'}
for x,t in [(12,'装配分组'),(111,'条目'),(153,'材质显示角色'),(270,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=35+i*12.1
 s.text(12,y,names[name]);s.text(120,y,count,anchor='middle');s.text(153,y,' / '.join(sorted(set(r['material'] for r in rows))[:3]),2.9);s.text(270,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],2.7);s.line((12,y+4),(384,y+4))
s.text(12,207,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体；详见 COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'版本、近似尺寸与验证范围',['研究对象为 1977 年 Heavy Sixer、CX10 及早期 CX30-04；附件局部结构为学习示意。','本图册是当前 CAD 的版本快照，修改模型后需重新生成投影、尺寸与验证记录。'])
sections=[(16,'资料与版本',['原厂维修手册：双电路板、12 芯排线与主要元件类别。','1977 年用户说明书：主机、双摇杆、旋钮对及电视连接附件。','实物照片：厚壁底壳、CX10 顶标及 CX30-04 早期标签。']),
 (67,'尺寸与内容边界',['本模型主体实测约 346 × 232.443 × 88.304 mm。','整体与局部尺寸均为近似值；没有核实原厂尺寸图或实机测量。','卡带无 ROM；适配器及开关内部不定义电气网络或制造参数。']),
 (118,'验证记录',[f"{M['design_iterations']} 轮源码；{M['physical_components']} 个组件与 {M['solids']} 个实体。",'重建、原生实体、装配求交及 STEP 回读分别保存检查报告。','图册另有字体、内容覆盖、逐页视觉和原生尺寸核对。']),
 (169,'维护入口',['资料：references/SOURCES.md；部件索引：COMPONENTS.csv。','逐轮源码：scripts/iterNN_*.py；实现：tools/cadlib/atari2600.py。','原生图页与 PDF 需随几何更新；检查记录位于 output/reports/。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
