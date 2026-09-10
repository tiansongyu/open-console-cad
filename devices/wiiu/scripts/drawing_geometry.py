"""Twelve A3 sheets projected from the delivered launch Wii U study BReps."""
from pathlib import Path
import os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
repo=Path(__file__).resolve().parents[3];sys.path.insert(0,str(repo/'tools'))
from cadlib import drawings as d
import FreeCAD as App,Part

d.init_drawing(Path(__file__).resolve().parents[1]);C=d.C;M=d.M;up=(0,0,1)
def starts(*prefixes):return [k for k in C if k.startswith(prefixes)]
def caption(s,v,t,y):s.text(v['x'],y,t+f" · {v['scale']:.3f}:1",anchor='middle')
def without(keys,*words):return [k for k in keys if not any(w in k for w in words)]
body=d.keys_for(M['envelope_groups']);pad=d.keys_for(['Controller','Display','PadInternal'])

s=d.Sheet(1,'首发白色 Basic 主机总装与尺寸',['WUP-001 Basic 采用白色圆角主机、8 GB 存储与独立的前置 SD / USB 盖板。','公开塑料主体为 172 × 268.5 × 46 mm；外伸脚垫、按钮与线缆另计，局部尺寸为学习近似。'])
v=s.view_fit('ConsoleIsometric',body,(18,29,169,158),(.5,-1.6,1.3));caption(s,v,'圆角长壳与独立前面板',208)
v=s.view_fit('ConsoleTop',body,(221,32,154,150),(0,0,1));d.dimension_box(s,v,['LowerHousing','FrontBezel'],'x',20);d.dimension_box(s,v,['LowerHousing','FrontBezel'],'y',210);caption(s,v,'主机宽度与深度',208);s.save()

s=d.Sheet(2,'前后接口与独立前门',['主机前侧保留光盘槽、同步键、SD 和双 USB，背侧包括 HDMI、AV、电源与另两组 USB。','HDMI 接点、端口壁厚和孔位是模型学习几何；屏蔽壳、绝缘载体与触点可在三维工程中分开检查。'])
v=s.view_fit('FrontPorts',[k for k in body if k!='FrontFlap'],(21,28,166,76),(0,-1,0),up);d.dimension_box(s,v,['FrontBezel'],'y',13);caption(s,v,'打开前门后的控制与接口',118)
v=s.view_fit('RearPorts',body,(222,28,161,76),(0,1,0),up);caption(s,v,'排风格栅与背面接口',118)
v=s.view_fit('HDMIDetail',starts('HDMIShield','HDMITongue','HDMIContact'),(33,147,145,47),(0,1,0),up);caption(s,v,'十九接点 HDMI Type A',209)
v=s.view_fit('SDDetail',starts('SDPort','SDTongue','SDContact'),(229,149,145,46),(0,-1,0),up);caption(s,v,'九接点 SD 卡座',209);s.save()

s=d.Sheet(3,'原版 GamePad 外壳与显示层',['WUP-010 GamePad 采用双握柄、6.2 英寸触摸屏、两个模拟摇杆及相机、NFC 和立体声扬声器。','公开主体为 255.4 × 133.4 × 41 mm，不含摇杆等外伸件；曲面壳采用原生轮廓和放样保留编辑历史。'])
v=s.view_fit('GamePadFront',pad,(26,27,213,144),(0,0,1));d.dimension_box(s,v,['PadBack','PadFront'],'x',20);d.dimension_box(s,v,['PadBack','PadFront'],'y',16);caption(s,v,'完整 GamePad 正面',188)
v=s.view_fit('GamePadSide',pad,(262,30,118,43),(0,1,0),up);d.dimension_box(s,v,['PadBack','PadFront'],'y',251);caption(s,v,'塑料主体厚度',94)
v=s.view_fit('DisplayLayers',['LCDBackplate','LCDFrame','LCDPanel','TouchLayer','DisplayBezel'],(262,123,116,65),(1,-.25,.5),exploded=True);caption(s,v,'背板、显示与触摸层',199);s.save()

s=d.Sheet(4,'双摇杆、按钮与原版电池',['双摇杆保留回中弹簧、电位器、轴承和帽盖；ABXY 与十字键由独立按钮板、硅胶和推杆构成。','原版电池为 1500 mAh；局部回中机构、线数和按钮行程仅作结构学习，不执行运动或电路仿真。'])
v=s.view_fit('AnalogModule',['LStickSpring','LStickYoke','LStickPivotPin','LStickPotX','LStickPotY'],(28,28,154,83),(.6,-1.1,1),up);caption(s,v,'回中弹簧、支承与双轴反馈',131)
v=s.view_fit('ButtonAssembly',[k for k in C if k in ['PadA','PadB','PadX','PadY','PadCarrierABXY'] or any(k==f'Pad{a}{b}' for a in ['A','B','X','Y'] for b in ['Carbon','Dome'])],(240,31,125,80),(.6,-1.2,1.1),up);caption(s,v,'独立 ABXY 按键与支承',131)
v=s.view_fit('BatteryPack',[k for k in starts('PadBattery') if k not in ['PadBatteryDoor','PadBatteryScrew0','PadBatteryScrew1']],(37,151,130,47),(0,0,-1));d.dimension_box(s,v,['PadBattery'],'x',143);caption(s,v,'原版电池与插接线束',211)
v=s.view_fit('RearTriggers',['PadZL','PadRearTriggerPCB-1','PadRearTriggerSwitch-1'],(244,150,120,48),(.7,-1,1),up);caption(s,v,'左侧后触发键与小板',211);s.save()

s=d.Sheet(5,'主机与 GamePad 的真实实体剖面',['本页将保存的三维实体与指定 Y 平面相交，剖面填充只表示实际切到的材料。','主机截面说明光驱、屏蔽和主板层次；GamePad 截面说明显示、支承、电池与背壳，均不是装配运动路径。'])
s.text(198,17,'A-A · 主机 Y=-57 光驱区域',4,'middle');v=d.section_view(s,'ConsoleSection',body,(22,35,352,54),offset=-57);caption(s,v,'光驱主轴、屏蔽与下层主板',111)
s.text(198,136,'B-B · GamePad Y=-283 电池区域',4,'middle');v=d.section_view(s,'GamePadSection',pad,(22,153,352,42),offset=-283);caption(s,v,'显示层、支承、电池与曲面壳',211);s.save()

s=d.Sheet(6,'主机与 GamePad 分层爆炸结构',['爆炸工程保留每个零件的几何、编号与装配分组，通过展示位移分开原本叠合的结构层。','本页省略较长线束以便观察壳体和板件；完整 CAD、STEP 与网页仍包含这些连接组件。'])
v=s.view_fit('ConsoleExploded',without(body,'Lead','Ribbon'),(15,29,190,167),(1,-.25,.5),exploded=True);caption(s,v,'主机外壳、光驱与散热层',211)
v=s.view_fit('GamePadExploded',without(pad,'Lead','Flex'),(215,29,167,167),(1,-.25,.5),exploded=True);caption(s,v,'GamePad 控制、显示与电池层',211);s.save()

s=d.Sheet(7,'主机主板、多芯片封装与无线模块',['主机以 CPU / GPU 共用载板和散热盖、四枚 DDR3L、Basic 8 GB eMMC 及三块独立无线模块说明布局。','内部参考 WUP-CPU-01 拆解照片，元件、接点与互连数量只描述本模型，不宣称复现原厂电路板。'])
v=s.view_fit('Mainboard',d.keys_for(['Mainboard']),(25,31,170,152),(0,0,1));d.dimension_box(s,v,['MainPCB'],'x',20);d.dimension_box(s,v,['MainPCB'],'y',14);caption(s,v,'主板与分区电子器件',209)
v=s.view_fit('MCM',starts('MCMSubstrate','GPUDie','CPUDie','GPUCaption','CPUCaption'),(241,28,115,77),(0,0,1));d.dimension_box(s,v,['MCMSubstrate'],'x',117);caption(s,v,'双芯片共用载板',133)
for x,key,title in [(225,'Wifi','无线网络'),(282,'Stream','GamePad 链路'),(339,'Bluetooth','控制器蓝牙')]:
 v=s.view_fit(key+'Module',starts(key+'PCB',key+'IC',key+'Coax'),(x,152,49,45),(0,0,-1));caption(s,v,title,211)
s.save()

s=d.Sheet(8,'吸入式光驱与处理器散热',['光驱包含传送滚轮、齿轮、主轴、压盘、双导轨和螺旋进给光头；外形按 Wii U 主机内腔单独布置。','共用散热器通过偏置风道连接后部轴流风扇，模型保留鳍片、导热垫与风扇支承，不进行气流或热仿真。'])
keys=[k for k in without(d.keys_for(['Optical']),'Lead','Ribbon','LidRib') if k not in ['DriveTopShield','DrivePCB','DriveController']]
v=s.view_fit('DriveMechanism',keys,(23,29,173,150),(0,0,1));d.dimension_box(s,v,['DriveBase'],'x',20);caption(s,v,'移开上盖后的光盘传送机构',209)
v=s.view_fit('Cooling',without(d.keys_for(['Cooling']),'Lead'),(231,29,144,74),(.6,1,1.1),up);caption(s,v,'共用散热器与后部风道',121)
v=s.view_fit('OpticalPickup',starts('Pickup','Sled'),(244,153,120,45),(0,0,1));d.dimension_box(s,v,['PickupRail0'],'y',233);caption(s,v,'导轨光头与进给件',211);s.save()

s=d.Sheet(9,'手柄主板、无线与连接层次',['GamePad 主板、按键板、无线板和 NFC 板均独立建模，宽软排线与细导线分别连接显示、输入和供电结构。','本页从背部观察电路封装和支承间隙；型号文字用于识别布局角色，不定义引脚分配或可工作的电路。'])
v=s.view_fit('GamePadBoards',d.keys_for(['PadInternal']),(23,31,174,151),(0,0,-1));caption(s,v,'背侧电子、线束与原版电池',210)
v=s.view_fit('PadMainboard',['PadMainPCB']+starts('UIC','DRC','TouchIC','PadAudioIC','PadGyro','PadSMD'),(231,30,145,73),(0,0,-1));d.dimension_box(s,v,['PadMainPCB'],'x',119);caption(s,v,'主控制板与主要器件',134)
v=s.view_fit('PadNFC',starts('PadNFCPCB','PadNFCAntenna'),(244,152,55,43),(0,0,1));caption(s,v,'NFC 线圈',211)
v=s.view_fit('PadRadio',starts('PadRadioPCB','PadRadioIC'),(320,150,55,46),(0,0,-1));caption(s,v,'无线链路小板',211);s.save()

s=d.Sheet(10,'两块电源、HDMI 与独立触控笔',['Basic 套装包括 WUP-002 主机电源、WUP-011 GamePad 电源、HDMI 和 WUP-015 触控笔。','两块电源的尺寸与内部件为照片近似；线缆采用展示长度。内部器件不提供电气安全、制造或性能依据。'])
v=s.view_fit('PowerAdapters',starts('ConsoleACLower','ConsoleACUpper','ConsoleACMark','GamePadACLower','GamePadACUpper','GamePadACMark'),(25,30,167,151),(0,0,1));d.dimension_box(s,v,['ConsoleACUpper'],'x',21);caption(s,v,'主机与 GamePad 分立电源',210)
v=s.view_fit('AdapterInterior',starts('ConsoleACPCB','ConsoleACTransformer','ConsoleACWinding','ConsoleACBulkCap','ConsoleACOutput','ConsoleACInput','ConsoleACRectifier','ConsoleACHeatPlate'),(235,30,145,73),(.4,-.7,1.3),up);caption(s,v,'电源内部结构学习示意',122)
v=s.view_fit('HDMIPlug',starts('HDMIGrip0','HDMIHead0','HDMIPlugTongue0','HDMIPlugPin0'),(240,150,66,49),(0,1,1),up);caption(s,v,'HDMI 插头与触点',211)
v=s.view_fit('Stylus',starts('Stylus'),(338,149,35,49),(0,0,1));caption(s,v,'独立触控笔',211);s.save()

s=d.Sheet(11,'组件、显示材料与装配索引',['同一组件可能包含多枚引脚或文字实体，因此组件条目与实体数量分开统计。','零件编号贯穿原生装配、STEP 和网页网格；显示材料仅用于辨认结构，不指定真实材料牌号。'])
names={'Body':'主机外壳与标识','Controls':'前面板控制与灯光','Ports':'主机连接端口','Mainboard':'主板和电子器件','Cooling':'主机散热与风道','Wireless':'三组无线模块与天线','Optical':'吸入光驱与线束','Shield':'上下金属屏蔽','Internal':'主机支承及固定','Controller':'GamePad 外壳与控制件','Display':'显示、触摸与支承','PadInternal':'GamePad 电子和内部机构','Accessories':'两块电源、HDMI 与触控笔'}
for x,t in [(12,'装配分组'),(111,'条目'),(151,'显示材料'),(268,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=34+i*12.8
 s.text(12,y,names.get(name,name),3.3);s.text(120,y,count,anchor='middle');s.text(151,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3.1);s.text(268,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.1);s.line((12,y+4),(384,y+4))
s.text(12,211,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体 · COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'版本依据、近似边界与重建入口',['研究对象为首发白色 WUP-001 Basic 8 GB、原版 WUP-010 GamePad 与 Basic 配套附件。','图册是保存模型的版本快照；修改三维实体后，应同步重建投影、尺寸、验证报告和网页预览。'])
sections=[(16,'来源与版本',['任天堂硬件、各部功能及 2012 年首发说明：主体、端口与套装。','iFixit 11796 拆解：主机、GamePad 板件和装配层次。','任天堂原装电源照片：独立适配器与对应的专用插头。']),
 (67,'尺寸与内容边界',['两个主体的公开包络不包括外伸按钮、脚垫和连接线。','孔位、器件、接点、线数、机构及附件尺寸为学习近似。','Basic 不混入 Premium 支架，原版 1500 mAh 电池保持独立。']),
 (118,'可核对的检查记录',[f"{M['design_iterations']} 轮源码 / {M['physical_components']} 组件 / {M['solids']} 实体。",'完整源码重建、严格实体、装配求交和 STEP 回读分别记录。','图册校验内容、字体、每页视觉和可回读的原生尺寸。']),
 (169,'继续修改的入口',['资料：references/SOURCES.md；清单：output/COMPONENTS.csv。','源码：tools/cadlib/wiiu.py；逐轮入口位于 scripts/。','检查：output/reports/；修改后同步更新 CAD、图纸和网页。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
