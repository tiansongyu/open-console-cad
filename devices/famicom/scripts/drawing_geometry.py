"""Twelve A3 HVC-001 sheets projected from delivered native BReps."""
from pathlib import Path
import os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
repo=Path(__file__).resolve().parents[3];sys.path.insert(0,str(repo/'tools'))
from cadlib import drawings as d
import FreeCAD as App,Part

d.init_drawing(Path(__file__).resolve().parents[1]);C=d.C;M=d.M
main=d.keys_for(d.HH);body=d.keys_for(M['envelope_groups']);up=(0,0,1)
def starts(*prefixes):return [k for k in C if k.startswith(prefixes)]
def caption(s,v,text,y):s.text(v['x'],y,text+f" · {v['scale']:.3f}:1",anchor='middle')
def legend(s,items,y=184):
 for i,(key,label) in enumerate(items):
  x=12+(i%3)*127;yy=y+(i//3)*17
  s.text(x,yy,C[key].PartNumber,3.1,fill='#1B365D');s.text(x,yy+6,label,3.1)
def controller(n,external=False):
 keys=d.keys_for(['Controller'+str(n)],not external)
 return [k for k in keys if not external or k not in ['P'+str(n)+'ShiftRegisterMark','P'+str(n)+'PCBMark']]
ext=d.keys_for(['Body','Controls','Ports'],False)+controller(1,True)+controller(2,True)+['CartridgeDustFlap','DustFlapRearRidge','CableBulkhead1','CableBulkhead2','DCJackCenter','RFJackContact']+starts('ExpansionPin')

s=d.Sheet(1,'原版红白机总装与主机包络',['HVC-001 圆形按键版本，保留两侧有线手柄、顶部卡槽盖和红色退卡把手。','主机按任天堂原始说明书的 150 × 220 × 60 mm 建模，外接线缆与附件另计。'])
v=s.view_fit('IsometricConsole',ext,(17,27,166,158),(-1,-1,2.3));caption(s,v,'红白分壳与侧置手柄',204)
v=s.view_fit('ConsoleTop',ext,(217,27,157,158),(0,0,1));d.dimension_box(s,v,body,'x',18,True);d.dimension_box(s,v,body,'y',202,True);caption(s,v,'俯视包络：宽 × 深',204);s.save()

s=d.Sheet(2,'前后接口与机身高度',['前部为 15 接点扩展口，后部为 DC 电源、TV/GAME、频道选择与 RF 输出。','图示采用主机坐标：X 为宽，Y 为前后深度，Z 为高度；线缆不参与主机尺寸。'])
v=s.view_fit('ConsoleFront',ext,(22,29,169,75),(0,-1,0),up);d.dimension_box(s,v,body,'y',12,True);caption(s,v,'正面及完整高度',119)
v=s.view_fit('ConsoleRear',ext,(217,29,166,75),(0,1,0),up);caption(s,v,'原始 RF 后面板',119)
v=s.view_fit('ExpansionPort',starts('Expansion'),(24,149,146,39),(0,-1,0),up);caption(s,v,'15 接点扩展口',206)
v=s.view_fit('DCReceptacle',starts('DCJack'),(220,145,62,48),(0,1,0),up);caption(s,v,'DC 电源口',206)
v=s.view_fit('RFReceptacle',starts('RFJack'),(316,145,62,48),(0,1,0),up);caption(s,v,'同轴 RF 输出',206);s.save()

s=d.Sheet(3,'两只原版手柄的操作差异',['一号手柄保留 START/SELECT，二号手柄使用麦克风与音量滑块。','采用熟悉的圆形 A/B 按键修订版；I/II 金色面板与外壳保持独立。'])
for n,x,normal in [(1,22,(-1,0,0)),(2,218,(1,0,0))]:
 v=s.view_fit('ControllerFace'+str(n),controller(n,True),(x,30,158,69),normal,up);d.dimension_box(s,v,['P'+str(n)+'Back'],'x',19);caption(s,v,'一号：START / SELECT' if n==1 else '二号：MIC / VOLUME',116)
v=s.view_fit('DirectionalStack',[k for k in starts('P1DPad','P1Up','P1Down','P1Left','P1Right')],(23,144,143,51),(-1,-.4,.4),up);caption(s,v,'十字键、胶垫与导电接点',208)
v=s.view_fit('MicrophoneGrille',starts('P2Mic'),(240,143,121,53),(1,0,0),up);caption(s,v,'二号手柄麦克风孔阵',208);s.save()

s=d.Sheet(4,'手柄 PCB、胶垫与麦克风组件',['两只手柄均保留独立 PCB、移位寄存器、导电胶垫和传动件。','二号手柄另有麦克风胶囊、电位器与额外导线；布线为几何示意。'])
for n,x,normal in [(1,22,(-1,0,0)),(2,218,(1,0,0))]:
 keys=[k for k in controller(n) if k!='P'+str(n)+'MicMesh' and (C[k].Fidelity.startswith('Schematic') or k.endswith(('ShiftRegisterMark','PCBMark')))]
 v=s.view_fit('ControllerInternal'+str(n),keys,(x,29,158,64),normal,up);d.dimension_box(s,v,['P'+str(n)+'PCB'],'x',18);caption(s,v,'一号 PCB 与输入件' if n==1 else '二号 PCB 与音频输入',114)
v=s.view_fit('ControllerExploded',controller(2),(20,137,355,60),(.5,-1,.4),up,exploded=True);caption(s,v,'二号手柄按自身法向展开',210);s.save()

s=d.Sheet(5,'真实实体剖面与装配层叠',['剖面由保存的实体与指定 Y 平面相交得到，浅色区域代表切到的材料。','前部展示电路板、芯片和退卡横梁，后部展示卡带接点、插座与壳体。'])
s.text(198,17,'A-A · Y=-23 主板与退卡机构',4,'middle');v=d.section_view(s,'LogicSection',body,(19,31,356,58),offset=-23);caption(s,v,'横向真实截面',107)
s.text(198,132,'B-B · Y=35 卡带连接器',4,'middle');v=d.section_view(s,'CartridgeSection',body,(19,145,356,51),offset=35);caption(s,v,'卡座、接点与两侧手柄',209);s.save()

s=d.Sheet(6,'主机与手柄的分层爆炸总览',['主机沿 Z 方向展开；两只手柄沿各自面板法向展开并横向分开。','爆炸位移来自原生装配清单，仅用于解释层次关系，不代表实际拆卸行程。'])
keys=[k for k in main if C[k].Assembly not in ['Cables','Wiring']]
v=s.view_fit('AssemblyExploded',keys,(11,23,375,166),(1.4,-1,1.1),exploded=True);caption(s,v,'原生爆炸偏移与组件编号一致',208);s.save()

s=d.Sheet(7,'主逻辑板与 60 接点卡座',['主板布局参考 HVC-CPU-GPM-02，包含 Ricoh CPU/PPU、两块 RAM 与辅助逻辑。','穿孔引脚与板底焊盘分别建模；封装和连接位置为近似研究几何。'])
v=s.view_fit('MainboardTop',d.keys_for(['Mainboard']),(24,28,176,146),(0,0,1));d.dimension_box(s,v,['Mainboard'],'x',18);d.dimension_box(s,v,['Mainboard'],'y',14);caption(s,v,'主板布局 · '+C['Mainboard'].PartNumber,189)
v=s.view_fit('CartridgeSocket',[k for k in d.keys_for(['CardReader']) if k not in ['CartridgeDustFlap','DustFlapRearRidge']],(239,31,131,59),(.4,-.8,1.8));caption(s,v,'60 接点卡座 · '+C['CardSocket'].PartNumber,111)
v=s.view_fit('DIPPackage',['CPU','CPUPins','CPUMark'],(240,136,131,42),(.3,-.6,1.7));caption(s,v,'CPU 封装 · '+C['CPU'].PartNumber,197);s.save()

s=d.Sheet(8,'电源/RF 小板与屏蔽结构',['原版通过 RF 输出连接电视，后部小板保留接口、调谐件和稳压结构。','金属罩、折弯散热片、线性稳压器与绕线分别建模，不计算电气或热性能。'])
keys=[k for k in d.keys_for(['PowerRF']) if k!='RFShield']
v=s.view_fit('PowerRFTop',keys,(21,30,183,135),(0,0,1));d.dimension_box(s,v,['PowerRFBoard'],'x',18);d.dimension_box(s,v,['PowerRFBoard'],'y',12);caption(s,v,'移除罩盖后的电源/RF 板',183)
v=s.view_fit('RFShield', ['RFShield'],(233,31,142,61),(.6,-.6,1.4));caption(s,v,'可拆金属罩',115)
v=s.view_fit('RegulatorDetail',starts('Regulator'),(244,141,117,42),(.6,1,.6),up);caption(s,v,'稳压器与散热片',206);s.save()

s=d.Sheet(9,'退卡滑架、拉杆与回位弹簧',['退卡把手经金属拉杆带动横梁和两侧抬升斜面，使卡带脱离插座。','导轨窗口为横梁提供行程空间，回位件采用实际螺旋几何。'])
keys=starts('EjectGuide','EjectCarrier','EjectLinkage','EjectReturnSpring','SpringEye','SpringAnchor')
v=s.view_fit('EjectMechanism',keys,(22,27,178,153),(.6,-.5,1.2));caption(s,v,'从机壳内侧观察退卡机构',198)
v=s.view_fit('ReturnSpring',starts('EjectReturnSpring','SpringEye','SpringAnchor'),(248,28,111,58),(.8,-.5,1));caption(s,v,'回位弹簧与固定端 · '+C['EjectReturnSpring'].PartNumber,109)
v=d.section_view(s,'GuideSection',starts('EjectGuide','EjectCarrier'),(221,146,157,39),offset=-34);caption(s,v,'C-C · Y=-34 横梁与导轨剖面',207);s.save()

s=d.Sheet(10,'空白卡带与电源、RF 附件',['卡带包含分壳、卡扣、PCB、60 接点和两块 ROM 封装示意，不包含游戏数据。','另提供电源适配器、RF 转接盒和天线转换器；附件局部尺寸均为近似值。'])
cart=starts('GamePak')
v=s.view_fit('GamePakFront',cart,(24,33,154,134),(0,0,1));d.dimension_box(s,v,['GamePakBack'],'x',21);d.dimension_box(s,v,['GamePakBack'],'y',14);caption(s,v,'独立空白 FC 卡带',184)
v=s.view_fit('PowerAdapter',starts('Adapter'),(220,28,158,72),(.5,-.7,1.5));caption(s,v,'10 V 电源与 DC 插头示意',120)
v=s.view_fit('RFBoxAndConverter',starts('RFSwitch','Antenna','RFInput','RFPlug','RFTV','Converter'),(217,142,164,51),(.2,-.3,1.6));caption(s,v,'RF 盒与 75 / 300 Ω 转换器',210);s.save()

s=d.Sheet(11,'组件、材料与装配索引',['组件编号贯穿原生文件、STEP、网页网格和零件清单。','一个组件条目可能包含多枚芯片引脚或文字实体，条目数和实体数分别统计。'])
names={'Body':'机壳与标识','Controls':'主机操作件','CardReader':'卡带连接器','Controller1':'一号有线手柄','Controller2':'二号有线手柄','Ports':'前后接口','PowerRF':'电源/RF 小板','Cables':'外接手柄线','Mainboard':'主逻辑板','Mechanism':'退卡及开关机构','Wiring':'内部线束','Internal':'安装与支承','Accessories':'卡带及电源/RF 附件'}
for x,t in [(12,'装配分组'),(111,'条目'),(153,'材质显示角色'),(270,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=35+i*12.1
 s.text(12,y,names[name]);s.text(120,y,count,anchor='middle');s.text(153,y,' / '.join(sorted(set(r['material'] for r in rows))[:3]),2.9);s.text(270,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],2.9);s.line((12,y+4),(384,y+4))
s.text(12,207,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体；详见 COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'版本、尺寸来源与验证范围',['HVC-001 原版红白机外观，采用圆形按键手柄修订版和 RF 输出形式。','本图册是当前 CAD 几何的快照；修改模型后应重新生成和检查。'])
sections=[(16,'公开规格',['任天堂原始说明书：主机宽 150、深 220、高 60 mm。','专用适配器标称 DC 10 V / 850 mA；主机耗电约 4 W。','一号手柄为 START/SELECT，二号手柄为 MIC/VOLUME。']),(67,'版本与近似范围',['主逻辑板采用 iFixit 拆机中 HVC-CPU-GPM-02 布局参考。','不代表最早的方形按键手柄或所有生产批次的电路板。','壁厚、孔位、封装、线缆、卡带与附件尺寸为近似学习值。']),(118,'验证与文件',[f"{M['design_iterations']} 轮源码；{M['physical_components']} 个组件条目参与重建核对。",'原生整机与爆炸装配、STEP 回读及实体求交分别检查。','Kami 图册包含字体、内容覆盖和逐页视觉验证。']),(169,'维护入口',['参考：references/SOURCES.md；组件清单：COMPONENTS.csv。','逐轮入口：scripts/iterNN_*.py；实现：tools/cadlib/famicom.py。','Parameters 中 Depth(Y) 与 Height(Z) 保留原有表达式别名。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
