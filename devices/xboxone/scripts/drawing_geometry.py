"""Twelve A3 sheets from original Xbox One 1540, 1537 controller and Kinect2 BReps."""
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
body=d.keys_for(M['envelope_groups']);pad=d.keys_for(['Controller']);kinect=d.keys_for(['Kinect'])

s=d.Sheet(1,'原版 2013 黑色 Xbox One 与分区机壳',['选择 Model 1540 / 500 GB 原版，保留左侧亮面、右侧斜格栅与前端吸入式光盘槽。','343 × 263 × 80 mm 按微软官方家族表的原版一列建立；局部曲率、孔位和机构尺寸近似。'])
v=s.view_fit('ConsoleIsometric',body,(17,28,186,154),(.4,-1.3,.9));caption(s,v,'原版亮面与通风分区',210)
v=s.view_fit('ConsoleTop',body,(230,35,151,142),(0,0,1));d.dimension_box(s,v,['BottomShell'],'x',20,published=True);d.dimension_box(s,v,body,'y',215,published=True);caption(s,v,'官方名义包络与模型投影',210);s.save()

s=d.Sheet(2,'吸入式前面板与原版 HDMI 输入输出',['主机侧面具有第三个 USB 3.0 和配对键，后部保留 HDMI 输入/输出、TOSLINK 与专用 Kinect。','接口屏蔽、绝缘、接点和外壳开口分离；不混入 One S/X 的外观或接口删减。'])
v=s.view_fit('ConsoleFront',body,(20,27,176,73),(0,-1,0),up);caption(s,v,'吸入槽与电容电源区',118)
v=s.view_fit('ConsoleRear',body,(221,27,165,73),(0,1,0),up);caption(s,v,'原版后部接口与斜向散热孔',118)
v=s.view_fit('ConsoleLeft',body,(26,143,155,56),(-1,0,0),up);caption(s,v,'侧面 USB 与无线配对',212)
v=s.view_fit('Ports',d.keys_for(['Ports']),(221,143,162,56),(.1,1,.3),up);caption(s,v,'独立连接器与内部接点',212);s.save()

s=d.Sheet(3,'原版 1537 黑色双 AA 无线控制器',['微软 C3K1537 原始照片指导双板结构、四组电机、齐平电池盖和分离后握把盖。','保持非对称摇杆、十字键、View/Menu、micro-USB 与专用耳麦口，未加入后期 3.5 mm 或 USB-C。'])
v=s.view_fit('ControllerFront',pad,(22,27,205,151),(0,0,1));d.dimension_box(s,v,['PadBack','PadFront','PadGripCover0','PadGripCover1'],'x',20);d.dimension_box(s,v,['PadBack','PadFront'],'y',15);caption(s,v,'原版控制布局与近似握柄曲面',210)
v=s.view_fit('ControllerRear',pad,(250,30,132,89),(0,0,-1));caption(s,v,'齐平电池盖和分离握把',139)
v=s.view_fit('ControllerPorts',starts('PadMicroUSB','PadHeadset','PadSync','PadIR'),(250,157,132,38),(.2,1,.5),up);caption(s,v,'micro-USB 与原版扩展接口',212);s.save()

s=d.Sheet(4,'吸入式 Blu-ray 与内置 500 GB 硬盘',['光驱分离加载滚轮、主轴、夹盘、激光滑架、导杆与控制板，未放入游戏光盘。','硬盘保留塑料托架、独立金属盖、控制板和盘片机构；内部结构近似，不表示真实数据。'])
v=s.view_fit('OpticalMechanism',without(d.keys_for(['Optical']),'OpticalCover','OpticalStudy','OpticalClamp'),(19,29,178,158),(0,0,1));caption(s,v,'吸入式加载与光学读取机构',211)
v=s.view_fit('HardDrive',without(d.keys_for(['Storage']),'HDDCover','HDDLabel','HDDMark','HDDScrew'),(220,31,164,62),(0,0,1));caption(s,v,'内置硬盘与塑料托架',111)
v=s.view_fit('Pickup',starts('Pickup'),(232,145,138,51),(.4,-1,1.5),up);caption(s,v,'光头、导杆和独立驱动件',212);s.save()

s=d.Sheet(5,'来自保存实体的主机与手柄剖面',['剖面由 BRep 与指定 Y 平面实际相交生成，填充只表示被切到的真实材料。','主机剖面显示壳板、主板与散热器；手柄剖面展示双板、输入层与曲面空腔。'])
s.text(198,17,'A-A · 主机 Y=-40',4,'middle');v=d.section_view(s,'ConsoleSection',body,(23,34,351,58),offset=-40);caption(s,v,'壳体、主板、三热管与风扇空间',114)
s.text(198,137,'B-B · 控制器 Y=-273（局部 Y=-13）',4,'middle');v=d.section_view(s,'ControllerSection',pad,(23,156,351,39),offset=-273);caption(s,v,'输入机构、双电路板和握柄外壳',212);s.save()

s=d.Sheet(6,'分层爆炸与可追溯原生装配',['爆炸工程保留稳定组件编号，以展示位移分开壳盖、板件、散热、存储和输入机构。','本页省略部分密集端子、长线与标识；完整原生文件、清单和网页保留所有组件。'])
v=s.view_fit('ConsoleExploded',without(body,'Wire','Lead','Contact','Mark'),(16,28,192,168),(.45,-.45,1.3),exploded=True);caption(s,v,'原版主机分层与内部总成',212)
v=s.view_fit('ControllerExploded',without(pad,'Wire','Contact','Pin','Mark','Lead'),(221,29,162,166),(.3,-.7,1.3),exploded=True);caption(s,v,'原版双板与四组电机手柄',212);s.save()

s=d.Sheet(7,'原版 APU、十六枚 DDR3 与双面主板',['原版实机照片指导 APU、三侧 DDR3、南桥、eMMC、供电和前后连接器位置。','背面主要保留无源器件；封装、线序和元件分布为非功能性结构近似，不是原厂电路或 BOM。'])
v=s.view_fit('MainboardTop',d.keys_for(['Mainboard']),(23,31,169,144),(0,0,1));d.dimension_box(s,v,['Mainboard'],'x',20);d.dimension_box(s,v,['Mainboard'],'y',15);caption(s,v,'APU、DDR3 与供电区',210)
v=s.view_fit('MainboardBottom',d.keys_for(['Mainboard']),(220,31,169,144),(0,0,-1));caption(s,v,'背面无源件和夹具安装孔',210);s.save()

s=d.Sheet(8,'三热管与单风扇、外置电源离心风机',['主机使用单个 112 mm 轴流风扇、三条独立铜热管、鳍片堆和背面 X 夹具。','外置电源按首发拆解保留离心风机、独立导风框与金属屏蔽；电气部分仅作机构学习。'])
v=s.view_fit('Cooling',d.keys_for(['Cooling']),(20,29,177,153),(.25,-.5,1.8));caption(s,v,'独立热管、鳍片与轴流电机',210)
v=s.view_fit('PowerSupply',without(starts('PSU'),'PSUTop','PSUShieldTop','PSUDCCable','PSUDCPlug','PSUDCRelief'),(221,29,161,153),(0,0,1));d.dimension_box(s,v,['PSUPCB'],'x',18);caption(s,v,'外置电源板与离心风机',210);s.save()

s=d.Sheet(9,'1537 双板、方向弹片与四组振动机构',['原版 U 形摇杆板和前接点板依据微软 FCC 照片，双轴输入、电位器与板间连接器分件表达。','十字键使用金属弹片，ABXY 保留导电胶；握把与扳机分别具有电机，电池为反向安装双 AA。'])
v=s.view_fit('ControllerBoards',starts('PadStickPCB','PadContactPCB','PadMCU','PadRadio','PadJoy','PadStack'),(17,28,87,78),(.15,-.3,2));caption(s,v,'前接点板与摇杆机构',124)
v=s.view_fit('ControllerRadio',starts('PadStickPCB','PadMCU','PadRadio'),(110,28,87,78),(.15,-.3,-2));caption(s,v,'背面主控与无线子板',124)
v=s.view_fit('KeyMechanisms',[k for k in starts('PadDPad','PadASilicone','PadBSilicone','PadXSilicone','PadYSilicone') if k!='PadDPad'],(221,28,160,78),(.2,-.5,2));caption(s,v,'十字键金属弹片与面键胶垫',124)
v=s.view_fit('Triggers',[k for k in starts('PadTrigger') if k not in ['PadTrigger0','PadTrigger1']],(28,145,127,51),(.7,-.4,1.2),up);caption(s,v,'移除外盖：扳机电机、轴与回位弹簧',213)
v=s.view_fit('BatteryMotors',starts('PadAA','PadGripMotor'),(216,145,164,51),(.3,-.6,1.8));caption(s,v,'双 AA 和左右偏心电机',213);s.save()

s=d.Sheet(10,'Kinect2 光学、原版耳麦与线缆',['原版 Kinect2 保留 RGB/深度光学、三分区 IR、四麦克风、后部风扇与手动俯仰底座。','聊天耳麦采用专用三键手柄适配器；HDMI 与区域 AC 线缩短陈列，附件局部尺寸均近似。'])
v=s.view_fit('KinectOptics',without(kinect,'KinectFace','KinectTop','KinectRear','KinectSide','KinectCable','KinectConsolePlug','KinectIRWindow'),(18,28,183,78),(.15,-1,.4),up);caption(s,v,'传感器、热脊与三分区红外模组',124)
v=s.view_fit('KinectComplete',without(kinect,'KinectCable','KinectConsolePlug'),(221,28,163,78),(.2,-1,.5),up);caption(s,v,'原版手动底座与传感器外观',124)
v=s.view_fit('ChatHeadset',starts('Headset'),(20,146,180,52),(0,0,1));caption(s,v,'单耳耳麦与加减音量/静音适配器',212)
v=s.view_fit('CableKit',starts('HDMIGrip','HDMIPlug','HDMICable','ACAppliance','ACWall','ACCable'),(221,146,163,52),(0,0,1));caption(s,v,'HDMI 与区域两脚 AC 展示线',212);s.save()

s=d.Sheet(11,'组件分组、唯一编号与原生清单',['每个物理组件具有稳定标识、唯一编号、装配分组和材料，可与原生树及 CSV 一一查对。','一个条目可能包含多个实体，字符与绕组会增加实体数；数量不等同于工厂物料表。'])
names={'Body':'原版分区机壳','Frame':'底盘与支承','Controls':'面板控制与状态灯','Ports':'原版连接接口','Mainboard':'APU 与 DDR3 主板','Cooling':'三热管与轴流风机','Optical':'吸入式 Blu-ray','Shielding':'金属屏蔽','Storage':'内置 500 GB 硬盘','Wiring':'内部线束与排线','Wireless':'前端无线与声音','Controller':'原版 1537 双 AA 手柄','Kinect':'原版 Kinect2 传感器','Accessories':'外置电源与配套附件'}
for x,t in [(12,'装配分组'),(111,'条目'),(151,'显示材料'),(268,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=31+i*10.2
 s.text(12,y,names.get(name,name),3.2);s.text(120,y,count,anchor='middle');s.text(151,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3.2);s.text(268,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.2);s.line((12,y+3.5),(384,y+3.5))
s.text(12,213,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体 · COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'原始资料、版本边界与继续重建',['本册选择 2013 原版 Model 1540、原版 1537 控制器及 Kinect2；资料与版本逐项核对。','投影来自当前保存实体，修改后须同步更新 CAD、图纸、尺寸、清单、报告和网页网格。'])
sections=[(16,'版本与一手资料',['微软官方家族规格表原版一列提供 343 × 263 × 80 mm 包络。','iFixit 原版主机、Kinect 与首发电源拆解指导机械分区。','微软 C3K1537 原始 FCC 照片区分原版双板和四组振动电机。']),
 (67,'近似与配套边界',['附件尺寸、曲率、壁厚、孔位、封装与线缆展示路线均近似。','普通黑色主体不复制 Day One 特别版字样与镀铬方向键。','不含游戏介质或可选充电套件；电路与光学组件不具实际功能。']),
 (118,'可查对的交付记录',[f"{M['design_iterations']} 轮源码 / {M['physical_components']} 组件 / {M['solids']} 实体。",'源码重建、严格实体、装配求交和 STEP 回读分别保留报告。','原生图纸、字体、逐页视觉、尺寸和网页随交付一起验证。']),
 (169,'继续修改入口',['资料：references/SOURCES.md；清单：output/COMPONENTS.csv。','源码：tools/cadlib/xboxone.py；逐轮入口：scripts/。','检查：output/reports/；修改后同步原生 CAD、图册和网页。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
