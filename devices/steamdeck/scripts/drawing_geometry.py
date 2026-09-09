"""Twelve A3 sheets of the original 2022 LCD Steam Deck from actual BReps."""
from pathlib import Path
import os,sys,re
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
repo=Path(__file__).resolve().parents[3];sys.path.insert(0,str(repo/'tools'))
from cadlib import drawings as d
import FreeCAD as App,Part

d.init_drawing(Path(__file__).resolve().parents[1]);C=d.C;M=d.M
main=d.keys_for(d.HH);ext=d.keys_for(d.HH,False)+[f'RearScrew{i}' for i in range(8)]
def caption(s,v,text,y):s.text(v['x'],y,text+f" · {v['scale']:.3f}:1",anchor='middle')
def starts(*p):return [k for k in C if k.startswith(p)]
def legend(s,items,y=174):
 for i,(key,label) in enumerate(items):
  x=12+(i%3)*127;yy=y+(i//3)*18
  s.text(x,yy,C[key].PartNumber,3.1,fill='#1B365D');s.text(x,yy+6,label,3.1)
right_stick=[k for k in starts('Stick') if '-1' not in k]
left_pad=[k for k in starts('Trackpad','Haptic') if re.match(r'^(?:Trackpad[A-Za-z]*|Haptic[A-Za-z]*)-1(?:_|$)',k)]

s=d.Sheet(1,'初代 LCD 正面总装与完整包络',['本模型采用 2022 年 LCD 版、黑色电源键与双方形触控板。','298 × 117 × 49 mm 为含控制件的完整包络；局部结构为近似学习模型。'])
v=s.view_fit('FrontAssembly',ext,(22,25,350,145),(0,0,1));d.dimension_box(s,v,main,'x',15,True);d.dimension_box(s,v,main,'y',12,True);caption(s,v,'完整主机正面',196);s.save()

s=d.Sheet(2,'背部握把、四枚背键与边缘接口',['后部包含曲面握把、L4/L5/R4/R5 背键、进风格栅和八枚维修螺钉。','顶部为排风、耳机、音量、电源和 USB-C，底边为 microSD。'])
v=s.view_fit('RearAssembly',ext,(18,26,181,88),(0,0,-1));caption(s,v,'背部握持与进风结构',125)
v=s.view_fit('RightSide',ext,(227,38,143,60),(1,0,0),(0,0,1));d.dimension_box(s,v,main,'y',385,True);caption(s,v,'含摇杆完整厚度 49 mm',125)
v=s.view_fit('TopPorts',ext,(18,146,175,39),(0,1,0),(0,0,1));caption(s,v,'顶部排风与接口',202)
v=s.view_fit('BottomPorts',ext,(215,146,168,39),(0,-1,0),(0,0,1));caption(s,v,'底部 microSD 入口',202);s.save()

s=d.Sheet(3,'七英寸显示层与主操作件尺寸',['7 英寸 16:10 显示窗口换算为约 150.77 × 94.23 mm。','双电容感应摇杆、十字键与 ABXY 独立建模，局部标注取自模型。'])
v=s.view_fit('LCDWindow',d.keys_for(['Display']),(25,28,216,130),(0,0,1));d.dimension_box(s,v,['DisplayGlass'],'x',17);d.dimension_box(s,v,['DisplayGlass'],'y',17);caption(s,v,'LCD、触控层与显示窗口',180)
v=s.view_fit('StickDetail',right_stick,(280,30,86,66),(0,0,1));d.dimension_box(s,v,['StickCap1'],'x',18);caption(s,v,'凹面电容感应摇杆',115)
v=s.view_fit('FaceButtons',starts('Button'),(280,142,86,48),(0,0,1));d.dimension_box(s,v,['ButtonY'],'x',132);caption(s,v,'ABXY 面按键',207);s.save()

s=d.Sheet(4,'触控板分层与音圈反馈机构',['触控表面、电极、压力承托、PCB、音圈、磁体和弹片保持独立。','此处表达压力传递与装配关系，不模拟实际反馈波形或触控电路。'])
v=s.view_fit('TrackpadFace',left_pad,(22,29,158,112),(0,0,1));d.dimension_box(s,v,['TrackpadSurface-1'],'x',18);d.dimension_box(s,v,['TrackpadSurface-1'],'y',13);caption(s,v,'单侧 32.5 mm 方形触控板',158)
v=s.view_fit('TrackpadExploded',left_pad,(221,24,155,126),(1.7,-.2,-1),exploded=True);caption(s,v,'传感与反馈层展开',158)
legend(s,[('TrackpadSurface-1','触控表面'),('TrackpadFoil-1','电极层'),('TrackpadCarrier-1','压力承托板'),('TrackpadPCB-1','传感板'),('HapticCoil-1','反馈音圈'),('TrackpadSpring-1_1','压力弹片')],177);s.save()

s=d.Sheet(5,'真实剖面与前后装配层叠',['剖面由 BRep 与指定平面相交得到，浅色区域为实体截面。','机壳、显示、电子模块与背键机构按实际模型高度投影。'])
s.text(198,17,'A-A · 主机 Y=0 横剖面',4,'middle');v=d.section_view(s,'MainSection',main,(12,32,372,61));caption(s,v,'主机、触控板与曲面握把',109)
s.text(101,135,'B-B · 摇杆 Y=33',4,'middle');v=d.section_view(s,'StickSection',right_stick,(24,152,151,37),offset=33);caption(s,v,'摇杆轴、壳体和固定件',207)
s.text(298,135,'C-C · 散热 Y=25',4,'middle');v=d.section_view(s,'ThermalSection',d.keys_for(['Thermal']),(218,152,156,37),offset=25);caption(s,v,'风机与铜热管截面',207);s.save()

s=d.Sheet(6,'整机装配分层爆炸总览',['外壳、显示、控制机构、主板、电池与散热层从同一组件集合展开。','每个爆炸节点记录组件编号与位移，位移只用于展示装配关系。'])
v=s.view_fit('ExplodedAssembly',main,(12,18,372,173),(1.7,-.2,-1),exploded=True);caption(s,v,'完整主机爆炸装配',207);s.save()

s=d.Sheet(7,'早期 LCD 主板、存储与电池布局',['采用早期黑色主板与银色罩的结构参考，分离 APU、内存和功能封装。','M.2 2230 模块、屏蔽套及 40 Wh L 形电池作为独立装配组。'])
v=s.view_fit('MainboardDetail',[k for k in d.keys_for(['Mainboard','Storage']) if k not in ['EMIShield','SSDShield','MicroSDCarrier','IOBoard','AudioJackPCB'] and not k.startswith('MicroSD')],(20,29,207,120),(0,0,-1));d.dimension_box(s,v,['SSDPCB'],'y',12);caption(s,v,'APU / LPDDR5 / M.2 2230',162)
v=s.view_fit('BatteryDetail',[k for k in d.keys_for(['Battery']) if not k.startswith('BatteryAdhesive')],(252,40,126,103),(0,0,-1));d.dimension_box(s,v,['BatteryPouch'],'x',25);d.dimension_box(s,v,['BatteryPouch'],'y',391);caption(s,v,'40 Wh / 5200 mAh 电池布局',162)
s.text(14,186,'外观封装、板形、接点和电芯尺寸为近似值；不包含真实线路与制造公差。');s.text(14,201,'原始机型为 2022 LCD，不引入 OLED 或后期黑色主板罩结构。');s.save()

s=d.Sheet(8,'离心风机、热管与排风鳍片',['左图移开鳍片底板，展示风机、铜热管、APU 冷板与排风鳍片。','散热件的壁厚、叶片与接触间隙为结构示意，不表示实际热性能。'])
thermal=[k for k in d.keys_for(['Thermal']) if k not in ['IntakeMesh','FanCable','FanConnector','FinBase']]
v=s.view_fit('ThermalAssembly',thermal,(18,28,229,123),(0,0,-1));caption(s,v,'铜热管与单风机散热路径',166)
v=s.view_fit('FanDetail',[k for k in starts('Fan') if k not in ['FanRearPlate','FanCable','FanConnector']],(281,33,94,93),(0,0,-1));d.dimension_box(s,v,['FanHousing'],'x',18);caption(s,v,'离心叶轮与壳体',149)
legend(s,[('ColdPlate','APU 冷板'),('Heatpipe','压扁铜热管'),('FanHousing','离心风机壳体'),('FinBase','鳍片底板'),('HeatFin0','独立排风鳍片'),('EMIShield','早期银色主板罩')],181);s.save()

s=d.Sheet(9,'模块化输入、扳机与背键传动',['可拆摇杆与左右操作板分组，面按键的导电粒、胶垫和传动柱保持独立。','扳机含支架、轴销、复位弹簧和角度传感器，背键保留曲面与传动柱。'])
v=s.view_fit('ControllerBoards',d.keys_for(['ControlsInternal']),(16,21,364,99),(0,0,1));caption(s,v,'左右输入机构',131)
v=s.view_fit('TriggerDetail',[k for k in starts('Trigger') if '-1' in k and k!='Trigger-1'],(23,151,144,39),(.6,-.5,1));caption(s,v,'扳机轴、支架与弹簧（移开外壳）',207)
v=s.view_fit('RearKeys',[k for k in starts('RearPaddle','RearKey','RearButton') if '-1' in k],(229,151,143,39),(1.5,-.3,1));caption(s,v,'曲面背键与传动件',207);s.save()

s=d.Sheet(10,'接口、音频模块与电源附件',['USB-C 接口和 microSD 插槽保留独立外壳、绝缘件和接点。','独立 45 W 电源附件为通用尺寸示意，不对应特定地区插头认证。'])
v=s.view_fit('USBCDetail',starts('USBTypeC','USBContact'),(21,29,145,51),(0,1,0),(0,0,1));d.dimension_box(s,v,['USBTypeCShell'],'x',18);caption(s,v,'USB-C 接口',101)
v=s.view_fit('MicroSDDetail',starts('MicroSD'),(220,28,151,55),(.6,-.9,1));caption(s,v,'microSD 入口与卡座',101)
v=s.view_fit('SpeakerDetail',[k for k in starts('Speaker') if '-1' in k],(29,140,130,52),(.6,-.5,1));caption(s,v,'单侧扬声器',207)
v=s.view_fit('AdapterDetail',d.keys_for(['Accessories']),(215,136,165,58),(0,0,1));d.dimension_box(s,v,['AdapterBody'],'x',125);caption(s,v,'独立 USB-C 电源附件正面',207);s.save()

s=d.Sheet(11,'组件、装配分组与材料索引',['组件编号贯穿原生文件、STEP、爆炸装配、清单和网页预览节点。','文字字形可含多个实体；组件数与实体数分别记录。'])
names={'Body':'机身外壳','Display':'LCD 与前触控','Controls':'外部操作件','Internal':'安装与互连','Ports':'边缘接口','Audio':'音频模块','Touchpads':'双触控板与反馈','Battery':'电池','Mainboard':'主板与封装','ControlsInternal':'输入与传动机构','Storage':'存储模块','Thermal':'散热组件','Accessories':'电源附件'}
for x,t in [(12,'装配分组'),(113,'组件数'),(160,'材质显示角色'),(282,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=35+i*12.1
 s.text(12,y,names[name]);s.text(124,y,count,anchor='middle');s.text(160,y,' / '.join(sorted(set(r['material'] for r in rows))[:3]),3.0);s.text(282,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.0);s.line((12,y+4),(384,y+4))
s.text(12,207,f"合计 {M['physical_components']} 个组件 / {M['solids']} 个实体；完整清单见 COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'尺寸来源、近似范围与验证入口',['公开整机尺寸、显示区换算和局部近似值分别记录。','图纸为当前版本 BRep 快照，修改原生模型后应重新生成投影。'])
sections=[(16,'公开规格与版本',['Valve 2022 LCD：整机 298 × 117 × 49 mm，包含控制件。','7 英寸 16:10 LCD；40 Wh 电池；45 W USB-C 供电。','本模型采用早期银色罩与黑色电源键，不使用 OLED 版布局。']), (67,'参考与近似范围',['Valve 原始产品技术规格与 iFixit 原始 LCD 拆机照片。','维修指南中的后期修订图像仅用于辨别，不混入当前版本。','局部曲面、壁厚、孔位、电芯、接点和排线均为近似研究几何。']), (118,'检查记录',[f"{M['design_iterations']} 轮源码构建；{M['physical_components']} 个组件重建匹配。",'原生整机与爆炸、三份 STEP 回读和组件求交检查。','模型尺寸、原生图纸参考、字体与逐页检查见 reports/。']), (169,'维护入口',['来源：references/SOURCES.md；清单：COMPONENTS.csv。','逐轮入口：scripts/iterNN_*.py；实现：tools/cadlib/steamdeck.py。','网页来自同一组 BRep，精确实体以 FCStd / STEP 为准。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
