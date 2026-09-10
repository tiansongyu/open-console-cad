"""Twelve A3 sheets projected from the delivered original Wii study BReps."""
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
body=d.keys_for(M['envelope_groups'])
outer=body
remote=without(d.keys_for(['Controller'],False),'CaseScrew')
nunchuk=without(d.keys_for(['Nunchuk'],False),'Cable','Plug','Relief','CaseScrew')

s=d.Sheet(1,'初代白色主机总装与尺寸参考',['RVL-001 保留吸入式光盘槽、蓝色导光件、前 SD 门及 GameCube 接口仓。','官方主体参考为竖放 44 × 157 × 215.4 mm；本模型按横放坐标绘制，局部尺寸为学习近似。'])
v=s.view_fit('ConsoleIsometric',outer,(18,30,169,155),(.5,-1.6,1.3));caption(s,v,'白色机壳与独立前面板',205)
v=s.view_fit('ConsoleTop',outer,(220,32,156,151),(0,0,1));d.dimension_box(s,v,['LowerHousing','FrontBezel'],'x',20);d.dimension_box(s,v,['LowerHousing','FrontBezel'],'y',210);caption(s,v,'横放坐标的宽度与深度',205);s.save()

s=d.Sheet(2,'原始前后接口与 GameCube 兼容仓',['前面板包含电源、重置、同步、SD 和退盘控制；背面保留双 USB、Multi AV、感应条及电源口。','四个 GameCube 手柄口和两个存储卡槽属于初代 RVL-001；触点与孔位不作为制造公差使用。'])
v=s.view_fit('Front',outer,(26,29,165,61),(0,-1,0),up);d.dimension_box(s,v,['FrontBezel','LowerHousing','UpperHousing']+starts('Foot'),'y',18);caption(s,v,'前面板与机身厚度',108)
v=s.view_fit('Rear',outer,(224,29,158,61),(0,1,0),up);caption(s,v,'双 USB、排风与供电接口',108)
v=s.view_fit('GameCubeBay',d.keys_for(['GameCube']),(20,147,228,52),(-1,0,0),up);caption(s,v,'四个六接点端口与双十二接点卡槽',211)
v=s.view_fit('USBDetail',starts('USB0'),(290,148,74,49),(0,1,0),up);d.dimension_box(s,v,['USB0Shell'],'x',137);caption(s,v,'USB 接口的独立接触件',211);s.save()

s=d.Sheet(3,'原版遥控器的外壳与内部结构',['RVL-003 使用红外指向窗口、十字键、A/B 键、HOME 和四个玩家指示灯。','本模型保留原版轮廓，不增加 MotionPlus 结构；电池、相机、扬声器和振动器均独立建模。'])
v=s.view_fit('RemoteTop',remote,(27,31,69,163),(0,0,1));d.dimension_box(s,v,['RemoteFront'],'x',20);d.dimension_box(s,v,['RemoteFront'],'y',17);caption(s,v,'原版遥控器正面',210)
v=s.view_fit('RemoteBack',['RemoteBack','RemoteBatteryDoor','RemoteB']+starts('RemoteCaseScrew'),(150,31,65,163),(0,0,-1));caption(s,v,'电池门与背部 B 键',210)
inside=[k for k in d.keys_for(['Controller']) if k not in remote and not k.startswith('RemoteCaseScrew') and k not in ['RemoteBPCB','RemoteBSwitch']]
v=s.view_fit('RemoteInternal',inside,(260,31,103,161),(.3,-.5,-2.4));caption(s,v,'两节 AA 与控制器内构',210);s.save()

s=d.Sheet(4,'双节棍曲面壳与模拟摇杆',['RVL-004 使用曲面握柄、模拟摇杆和前侧 C/Z 触发键，通过六接点扩展线连接遥控器。','贝塞尔轮廓转换为原生样条草图后放样；电位器、板件和固定点为学习几何。'])
v=s.view_fit('NunchukTop',nunchuk,(35,31,111,155),(0,0,1));d.dimension_box(s,v,['NunchukBack'],'x',21);d.dimension_box(s,v,['NunchukBack'],'y',22);caption(s,v,'曲线外壳与凹面摇杆帽',207)
v=s.view_fit('NunchukMechanism',starts('NunchukStick','NunchukThumb','NunchukPot'),(230,30,144,78),(.7,-1,1.3),up);caption(s,v,'双轴模拟控制机构',128)
v=s.view_fit('NunchukBoard',starts('NunchukPCB','NunchukController','NunchukAccelerometer','NunchukPassive','NunchukTriggerPCB','NunchukCSwitch','NunchukZSwitch'),(248,136,104,63),(0,0,1));caption(s,v,'控制板与独立触发接点',211);s.save()

s=d.Sheet(5,'光驱与散热区的实体剖面',['剖面由交付的真实 BRep 与给定 Y 平面相交生成，填充区域表示实际切到的材料。','两处截面分别说明光驱与主板的层次，以及主芯片、散热器和顶壳的间隙。'])
s.text(198,17,'A-A · Y=-31 光驱主轴区域',4,'middle');v=d.section_view(s,'DriveSection',body,(20,35,354,57),offset=-31);caption(s,v,'主轴、光驱底架与屏蔽层',111)
s.text(198,134,'B-B · Y=66 芯片与散热区域',4,'middle');v=d.section_view(s,'CoolingSection',body,(20,151,354,45),offset=66);caption(s,v,'芯片封装、导热材料与鳍片',212);s.save()

s=d.Sheet(6,'分层装配与控制器爆炸视图',['交付的爆炸位移保持组件几何及零件编号，不表示经过验证的实际拆卸路径。','为看清壳体和板件，本页省略长线缆、排线和插头；原生完整装配仍包含这些组件。'])
v=s.view_fit('ConsoleExploded',without(body,'Cable','Wire','Ribbon'),(15,28,249,163),(1,-.25,.5),exploded=True);caption(s,v,'主机壳体、光驱、板件与支承',211)
v=s.view_fit('ControllersExploded',without(d.keys_for(['Controller','Nunchuk']),'Cable','Plug','Relief'),(276,33,107,157),(1,-.25,.5),exploded=True);caption(s,v,'遥控器与双节棍',211);s.save()

s=d.Sheet(7,'主板、处理器与分区电子器件',['Broadway 和 Hollywood 封装、存储器、视频编码及独立无线模块构成这份主板学习布局。','参考照片包含 RVL-CPU-40 等初代外壳系列板件，不宣称复刻首批主板、走线或原厂电路。'])
v=s.view_fit('Mainboard',d.keys_for(['Mainboard']),(24,29,174,154),(0,0,1));d.dimension_box(s,v,['MainPCB'],'x',19);d.dimension_box(s,v,['MainPCB'],'y',13);caption(s,v,'主板 · '+C['MainPCB'].PartNumber,207)
v=s.view_fit('Processors',[k for k in starts('Broadway','Hollywood') if C[k].Assembly=='Mainboard'],(233,32,140,70),(0,0,1));d.dimension_box(s,v,['Hollywood'],'x',20);caption(s,v,'主要处理器封装示意',121)
v=s.view_fit('MEM2Package',starts('MEM2'),(236,149,57,49),(0,0,1));caption(s,v,'MEM2 存储器',211)
v=s.view_fit('NANDPackage',starts('NAND'),(311,149,64,49),(0,0,1));caption(s,v,'NAND 与外围引脚',211);s.save()

s=d.Sheet(8,'吸入式光驱的传送与拾取机构',['光盘通过双滚轮进入光驱，内部包括齿轮、主轴、压盘、双导轨光头和螺旋进给件。','本模型说明机构层次，局部齿形、导轨、线束和装配尺寸均为学习近似，不执行运动仿真。'])
keys=without(d.keys_for(['Optical']),'Wire','Ribbon');keys=[k for k in keys if k not in ['DriveTopShield','DrivePCB','DriveController']]
v=s.view_fit('OpticalMechanism',keys,(22,31,175,148),(0,0,1));d.dimension_box(s,v,['DriveBase'],'x',20);caption(s,v,'移开上部屏蔽后的光驱',207)
v=s.view_fit('PickupDetail',starts('Pickup','Sled'),(239,32,123,78),(0,0,1));d.dimension_box(s,v,['PickupRail0'],'y',228);caption(s,v,'双导轨与螺旋进给',127)
v=s.view_fit('Spindle',starts('Spindle','Turntable','DiscClamp','Clamp'),(257,153,91,42),(.6,-1,1.0),up);caption(s,v,'主轴、定位与磁性压盘',211);s.save()

s=d.Sheet(9,'散热、无线模块与供电结构',['主机使用共用鳍片散热器和后排风扇，并保留独立 Wi-Fi、蓝牙板及两条侧面天线。','外置电源适配器的内部器件是结构示意，不定义可制造电路、电气安全或性能参数。'])
v=s.view_fit('Cooling',without(d.keys_for(['Cooling']),'Wire'),(20,30,176,84),(.6,-.8,1.1),up);caption(s,v,'鳍片、导热垫与轴流风扇',133)
v=s.view_fit('WifiModule',without([k for k in starts('Wifi') if C[k].Assembly=='Wireless'],'Cable','Antenna','Shield'),(221,32,70,80),(0,0,1));caption(s,v,'Wi-Fi 板，移开金属罩',133)
v=s.view_fit('BluetoothModule',without(starts('Bluetooth'),'Shield'),(305,32,72,80),(0,0,1));caption(s,v,'蓝牙板，移开金属罩',133)
v=s.view_fit('PowerBoard',starts('AdapterPCB','AdapterTransformer','AdapterWinding','AdapterBulkCap','AdapterOutput','AdapterInput','AdapterRectifier','AdapterHeatPlate'),(22,146,175,53),(.4,-.8,1.1),up);caption(s,v,'RVL-002 内部结构学习示意',211)
v=s.view_fit('SensorEmitters',starts('SensorPCB-1','SensorEmitter-1_','SensorLead-1_'),(232,161,144,37),(0,-1,0),up);caption(s,v,'单侧五灯组件，两端对称',211);s.save()

s=d.Sheet(10,'感应条、支架与连接附件',['感应条、两种支架、电源与 AV 插头按原始接口家族绘制，线缆采用便于展示的收纳长度。','12 cm 与 8 cm 光盘均为空白学习媒体，不包含游戏数据或第三方游戏图像。'])
v=s.view_fit('SensorBar',starts('SensorLower','SensorUpper','SensorWindow'),(22,33,172,57),(0,-1,1),up);d.dimension_box(s,v,['SensorLower'],'x',21);caption(s,v,'RVL-014 感应条',112)
v=s.view_fit('Adapter',starts('AdapterLower','AdapterUpper','AdapterMark'),(244,30,119,67),(0,0,1));d.dimension_box(s,v,['AdapterUpper'],'x',21);caption(s,v,'外置电源适配器',112)
v=s.view_fit('VerticalStand',['ConsoleStand'],(25,150,94,47),(1,0,0),up);d.dimension_box(s,v,['ConsoleStand'],'y',18);caption(s,v,'斜面竖放支架',211)
v=s.view_fit('BlankMedia',starts('WiiDisc','GCDisc'),(148,157,112,40),(0,0,1));caption(s,v,'两种空白光盘',211)
v=s.view_fit('RCAConnections',starts('RCAGrip','RCAColor','RCAGround','RCAPin'),(294,160,79,36),(0,0,1));caption(s,v,'复合视频与立体声 RCA',211);s.save()

s=d.Sheet(11,'组件、显示材料与装配索引',['同一组件可包含多枚引脚或文字实体，组件条目与实体数量分别统计。','零件编号贯穿原生工程、STEP 与网页网格，显示材料仅用于区分结构，不指定材料牌号。'])
names={'Body':'主机外壳与标识','Controls':'前面板控制与灯光','Ports':'主机连接端口','GameCube':'GameCube 接口仓','Mainboard':'主板和电子器件','Cooling':'主机散热与风扇','Wireless':'无线板与天线','Optical':'吸入光驱与线束','Shield':'上下金属屏蔽','Internal':'主机支柱及固定','Controller':'RVL-003 遥控器','Nunchuk':'RVL-004 双节棍','Accessories':'感应条、支架与连接附件'}
for x,t in [(12,'装配分组'),(111,'条目'),(151,'显示材料'),(268,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=34+i*12.8
 s.text(12,y,names.get(name,name),3.3);s.text(120,y,count,anchor='middle');s.text(151,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3.1);s.text(268,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.1);s.line((12,y+4),(384,y+4))
s.text(12,211,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体 · COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'版本依据、近似边界与重建入口',['研究对象为白色初代 RVL-001、原版 RVL-003 遥控器及 RVL-004 双节棍。','图册是保存模型的版本快照，修改三维几何后需要同步重建投影、尺寸、验证报告和网页。'])
sections=[(16,'来源与版本',['任天堂硬件页和说明书：尺寸、原始接口、配件与控制器家族。','iFixit 与 Dig and Rescue：主机、光驱及内部组件实物照片。','板件照片含 RVL-CPU-40，模型不宣称复刻首批电路板。']),
 (67,'尺寸与内容边界',['主机按横放坐标绘制，公开主体包络不包括外伸件和连接线。','壁厚、孔位、接点、器件布局及机制细节为原创学习近似。','空白光盘无游戏数据；电源与电子封装不作为电路设计依据。']),
 (118,'可核对的验证记录',[f"{M['design_iterations']} 轮源码 / {M['physical_components']} 组件 / {M['solids']} 实体。",'原生实体、严格 BRep、完整重建、装配求交及 STEP 回读分别记录。','图册检查字体、内容覆盖、每页视觉与原生可测量尺寸引用。']),
 (169,'继续修改的入口',['资料：references/SOURCES.md；清单：output/COMPONENTS.csv。','源码：tools/cadlib/wii.py；逐轮入口位于 scripts/。','检查：output/reports/；修改后同步更新 CAD、图纸与网页。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
