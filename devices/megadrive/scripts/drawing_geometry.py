"""Twelve A3 sheets from the saved Mega Drive BReps and exact sections."""
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
outer=list(dict.fromkeys(d.keys_for(['Body','Controls','CardReader'],False)+d.keys_for(['Ports'])))
padouter=['PadBack','PadFront','PadDDisc','PadDPad','PadABC0','PadABC1','PadABC2','PadABCMark0','PadABCMark1','PadABCMark2','PadStart','PadStartMark','PadSega']

s=d.Sheet(1,'初代日版主机总装与尺寸参考',['HAA-2510 大机型保留偏右圆形卡带台、耳机滑块、蓝色 RESET 与左侧通风槽。','官方主体尺寸为 280 × 212 × 70 mm，图示局部测量为近似模型值，外伸接头和标识另计。'])
v=s.view_fit('ConsoleIsometric',outer,(17,30,172,155),(-.7,-1.2,1.5));caption(s,v,'日版 Model 1 外观',205)
v=s.view_fit('ConsoleTop',outer,(220,33,157,149),(0,0,1));d.dimension_box(s,v,['LowerHousing'],'x',20);d.dimension_box(s,v,['LowerHousing'],'y',207);caption(s,v,'底壳宽度与前后深度',205);s.save()

s=d.Sheet(2,'前后接口与接点细节',['前方包含两只 DE-9 手柄接口和耳机口，后方保留扩展控制接口、音视频与电源输入。','金属外壳、绝缘支架与触点分别记录，接口孔位和配合尺寸为当前学习模型的近似值。'])
v=s.view_fit('ConsoleFront',outer,(22,29,168,68),(0,-1,0),up);d.dimension_box(s,v,outer,'y',18);caption(s,v,'正面接口与模型高度',115)
v=s.view_fit('ConsoleRear',outer,(220,29,160,68),(0,1,0),up);caption(s,v,'后面板原始接口',115)
v=s.view_fit('ControllerDE9',starts('PadPort1Shield','PadPort1Insert','PadPort1Pin','PadPort1Tab'),(26,150,104,44),(0,-1,0),up);d.dimension_box(s,v,['PadPort1Shield'],'x',139);caption(s,v,'DE-9 手柄端口',207)
v=s.view_fit('DINAV',starts('AVBarrel','AVInsulator','AVInsert','AVContact'),(165,145,65,53),(0,1,0),up);caption(s,v,'八接点 DIN 音视频口',207)
v=s.view_fit('PowerDC',starts('PowerDC','PowerCenter'),(286,146,78,49),(0,1,0),up);caption(s,v,'同轴 DC 电源口',207);s.save()

s=d.Sheet(3,'初代 SJ-3500 三键手柄外观',['初代手柄采用双握柄弧形壳体、浮动方向圆盘和斜列 ABC 三个动作键。','上下壳保留原生曲线剖面，蓝色 START 与六处后壳固定均独立建模。'])
v=s.view_fit('PadIsometric',padouter,(20,29,170,151),(.5,-.8,1.9));caption(s,v,'原生曲线放样手柄',203)
v=s.view_fit('PadTop',padouter,(222,34,151,88),(0,0,1));d.dimension_box(s,v,['PadBack'],'x',22);d.dimension_box(s,v,['PadBack'],'y',211);caption(s,v,'手柄俯视与学习尺寸',143)
v=s.view_fit('PadRear',['PadBack']+starts('PadCaseScrew'),(238,160,127,35),(0,0,-1));caption(s,v,'六处后壳螺钉',211);s.save()

s=d.Sheet(4,'手柄触点、板件与线束',['控制器包含主板、复用器封装、八组碳膜接点、独立硅胶圆顶和九芯内部导线。','硅胶、接点、按键柱和线束端子分开表示，局部结构不作为可制造电路或开关性能依据。'])
inner=starts('PadPCB','PadContact','PadRubber','PadPill','PadLogic','PadResistor','PadWire')
v=s.view_fit('PadInternal',inner,(22,31,167,109),(0,0,1));d.dimension_box(s,v,['PadPCB'],'x',20);d.dimension_box(s,v,['PadPCB'],'y',12);caption(s,v,'板件与独立碳膜按键',160)
v=s.view_fit('RubberDetail',['PadContact4','PadRubber4','PadPill4','PadABC0'],(252,30,94,98),(1,0,.25),up);caption(s,v,'动作键与硅胶圆顶',149)
v=s.view_fit('PadExploded',[k for k in d.keys_for(['Controller']) if not any(t in k for t in ['Cable','Plug','Wire','Grommet'])],(31,172,338,26),(1,0,.25),exploded=True);caption(s,v,'手柄层叠爆炸',212);s.save()

s=d.Sheet(5,'主体剖面与卡带插入空间',['剖面由保存的真实实体与给定切割平面相交得到，填充区域表示被切到的材料。','两个平面分别经过主逻辑与卡槽区域，显示上下壳、板件和连接器之间的实际模型间隙。'])
s.text(198,17,'A-A · Y=0 主板区域',4,'middle');v=d.section_view(s,'LogicSection',body,(19,33,356,60),offset=0);caption(s,v,'壳体、板件与芯片层叠',111)
s.text(198,135,'B-B · Y=35 卡槽区域',4,'middle');v=d.section_view(s,'CartridgeSection',body,(19,151,356,44),offset=35);caption(s,v,'卡带导向口与两排触点',211);s.save()

s=d.Sheet(6,'主机与手柄的分层装配',['爆炸视图使用交付文件保存的组件位移，原始几何与零件身份保持对应。','长线缆从此总览中省略，便于阅读主机上下壳、主板、卡槽和三键手柄的层次。'])
keys=[k for k in d.keys_for(d.HH) if not any(t in k for t in ['Cable','Wire','Plug','Grommet'])]
v=s.view_fit('ConsoleExploded',keys,(12,24,372,170),(1,-1,.8),exploded=True);caption(s,v,'组件层次与原生爆炸位移',211);s.save()

s=d.Sheet(7,'主板与主要集成电路（VA2）',['本模型采用初代外壳系列中的 VA2 拆机照片作为内部参考，并明确区别于首批 VA0 电路。','主要封装包括 68000、Z80、音源、图形与接口处理器，以及存储器和穿孔引脚。'])
v=s.view_fit('Mainboard',d.keys_for(['Mainboard']),(22,31,178,151),(0,0,1));d.dimension_box(s,v,['MainPCB'],'x',19);d.dimension_box(s,v,['MainPCB'],'y',12);caption(s,v,'主板 · '+C['MainPCB'].PartNumber,204)
v=s.view_fit('CPU68000Detail',starts('CPU68000'),(244,31,126,64),(0,0,1));d.dimension_box(s,v,['CPU68000'],'x',21);caption(s,v,'68000 双列直插封装',119)
v=s.view_fit('VDPDetail',starts('VDP'),(252,146,110,49),(.3,-.6,2));caption(s,v,'图形处理器封装示意',211);s.save()

s=d.Sheet(8,'卡带触点、散热片与控制传动',['卡带座保留两排共 64 个弹片，防尘门、导向框和电源锁结构分别建模。','折弯散热片与稳压器位于内部，音量、电源和 RESET 的简化传动用于说明空间关系。'])
v=s.view_fit('CardReaderDetail',[k for k in d.keys_for(['CardReader']) if k not in ['CartridgeFlap','CardGuide']],(27,28,163,86),(0,0,1));d.dimension_box(s,v,['CardReaderHousing'],'x',18);caption(s,v,'两排 64 接点插座',133)
v=s.view_fit('RegulatorAssembly',d.keys_for(['Power']),(246,33,114,68),(.8,-1,1.3),up);caption(s,v,'线性稳压器与折弯散热片',133)
v=s.view_fit('ControlMechanisms',starts('VolumeMechanism','VolumeStem','PowerMechanism','PowerStem','CartridgeLock','ResetSwitch','ResetPlunger'),(43,160,313,36),(.2,-.7,1.2),up);caption(s,v,'三个控制件的内部传动',212);s.save()

s=d.Sheet(9,'空白卡带与外接适配器',['卡带采用原创学习标签，包含双面金手指、板件与 ROM 封装示意，不附带游戏数据。','适配器保留空心上下壳、变压器芯和绝缘骨架，内部不定义电气网络或安全认证。'])
v=s.view_fit('BlankCart',[k for k in starts('Cart') if C[k].Assembly=='Accessories'],(22,32,155,143),(0,0,1));d.dimension_box(s,v,['CartBack'],'x',20);d.dimension_box(s,v,['CartBack'],'y',12);caption(s,v,'原创标签与 64 个金手指',204)
v=s.view_fit('AdapterExternal',['AdapterLower','AdapterUpper','AdapterLabel','AdapterMark','AdapterStudyMark']+starts('ACBlade'),(233,31,135,72),(.5,-.8,1.4));caption(s,v,'外接变压器式适配器',126)
v=s.view_fit('AdapterInternal',['AdapterLower','TransformerCore','TransformerBobbin'],(249,153,101,43),(.6,-.8,1.5));caption(s,v,'变压器内部学习示意',211);s.save()

s=d.Sheet(10,'原始连接线与插头结构',['原始单声道连接方式使用 DIN 转双 RCA，主机电源采用独立 DC 适配器。','线缆由圆弧与直线扫掠，展示的是收纳位置和短线段，不代表原装线长。'])
keys=starts('AVCable','AVSplit','AVBranch','DINGrip','DINShield','DINInsert','DINPin','RCAGrip','RCAShield','RCAPin')
v=s.view_fit('MonoAVLead',keys,(22,30,170,142),(0,0,1));caption(s,v,'DIN 转音频 / 视频双 RCA',198)
v=s.view_fit('PadPlugDetail',starts('PadPlug'),(239,28,127,67),(.5,-.8,1.3),up);caption(s,v,'手柄 DE-9 母头与护套',116)
v=s.view_fit('DCPlugDetail',starts('DCPlug'),(240,150,125,44),(.7,-.6,1),up);caption(s,v,'同轴 DC 插头',211);s.save()

s=d.Sheet(11,'组件与显示材料索引',['零件编号贯穿原生装配、STEP、网页网格与清单，可在不同格式中核对同一个组件。','材质名称仅表示显示角色，组件条目和实体数量分别统计，不指定生产材料牌号。'])
names={'Body':'机壳与标识','Controls':'主机控制与传动','Ports':'主机连接接口','Mainboard':'主板及电子封装','CardReader':'卡座与防尘结构','Internal':'支承与紧固件','Power':'稳压及散热片','Controller':'SJ-3500 三键手柄','Accessories':'卡带、电源与线缆'}
for x,t in [(12,'装配分组'),(105,'条目'),(144,'显示材料'),(270,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=37+i*17.2
 s.text(12,y,names.get(name,name));s.text(114,y,count,anchor='middle');s.text(144,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3.2);s.text(270,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.2);s.line((12,y+5),(384,y+5))
s.text(12,209,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体 · COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'版本依据、近似边界与验证入口',['研究对象为日版初代 HAA-2510 外壳系列和 SJ-3500 三键手柄，内部参考明确标为 VA2。','图纸是已保存模型的版本快照，修改几何后应同步重新生成投影、尺寸和验证记录。'])
sections=[(16,'来源与版本',['SEGA 官方硬件资料：初代主机外形、接口与整体尺寸。','Dig and Rescue：HAA-2510 VA2 与 SJ-3500 的实物拆装照片。','同一机型包含多种板件版本，本模型不宣称复刻首批 VA0 电路。']),
 (67,'尺寸与内容边界',['官方主体参考 280 × 212 × 70 mm，图中近似尺寸来自模型。','局部孔位、壁厚、板件及附件为学习设计，外伸接头另计。','卡带不含游戏数据，适配器和电子封装不作为电路设计依据。']),
 (118,'可核对的交付记录',[f"{M['design_iterations']} 轮源码 / {M['physical_components']} 组件 / {M['solids']} 实体。",'源码重建、实体求交、原生保存及 STEP 回读分别记录。','图册另有字体、内容覆盖、逐页视觉和原生尺寸检查。']),
 (169,'继续修改与复现',['资料：references/SOURCES.md；索引：output/COMPONENTS.csv。','实现：tools/cadlib/megadrive.py；按轮次入口位于 scripts/。','检查报告：output/reports/；修改后需重新生成网页与图纸。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
