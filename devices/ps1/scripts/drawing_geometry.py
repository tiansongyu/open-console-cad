"""Twelve A3 sheets from the delivered Japanese PlayStation study BReps."""
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
body=d.keys_for(M['envelope_groups']);pad=without(d.keys_for(['Controller']),'Cable','Grommet','Wire','InternalLead','Plug')

s=d.Sheet(1,'日版初代灰色主机总装与近似尺寸',['SCPH-1000 保留圆形光驱盖、左右侧翼、独立 POWER / RESET / OPEN 和原始灰色外壳。','270 × 188 × 60 mm 来自 SCPH-5500 官方家族说明书，仅作为本 SCPH-1000 学习模型的近似包络。'])
v=s.view_fit('ConsoleIsometric',body,(18,29,173,153),(.5,-1.6,1.25));caption(s,v,'圆盖、侧翼与原始控制布局',208)
v=s.view_fit('ConsoleTop',body,(225,35,150,145),(0,0,1));d.dimension_box(s,v,['LowerHousing','UpperHousing'],'x',20);d.dimension_box(s,v,['LowerHousing','UpperHousing'],'y',214);caption(s,v,'保存模型的宽度与深度',208);s.save()

s=d.Sheet(2,'双层前接口与日版原始后接口',['前部两组接口分别容纳记忆卡与数字手柄，防尘门、转轴、载体和金属接点独立建模。','后部保留 S-Video、三路 RCA、RFU DC、串口、AV MULTI、并口及日式 AC；几何不定义生产电路。'])
v=s.view_fit('ConsoleFront',body,(24,28,166,72),(0,-1,0),up);d.dimension_box(s,v,['LowerHousing','UpperHousing','DiscLid','Foot0','Foot1','Foot2','Foot3'],'y',14);caption(s,v,'记忆卡与手柄的双层接口',119)
v=s.view_fit('ConsoleRear',body,(224,28,161,72),(0,1,0),up);caption(s,v,'日版专有接口与并口防尘盖',119)
v=s.view_fit('FrontConnector',starts('Port1'),(29,144,148,53),(0,-1,0),up);caption(s,v,'八接点卡槽与九位置手柄插座',211)
v=s.view_fit('OriginalSVideo',starts('SVideo'),(265,143,92,54),(0,1,0),up);caption(s,v,'初代专用 S-Video 接口',211);s.save()

s=d.Sheet(3,'原始数字手柄 · SCPH-1010',['手柄选择紧凑的日版 SCPH-1010，采用四个分离方向键、四色符号面键、SELECT / START 与双层肩键。','原生曲线截面放样形成上下壳，保留八处后部固定；本版本没有模拟摇杆，局部尺寸均为学习近似。'])
v=s.view_fit('ControllerFront',pad,(26,28,201,146),(0,0,1));d.dimension_box(s,v,['CtrlBack','CtrlFront'],'x',20);d.dimension_box(s,v,['CtrlBack','CtrlFront'],'y',15);caption(s,v,'曲面外壳与数字输入件',207)
v=s.view_fit('ControllerRear',pad,(252,32,122,82),(0,0,-1));caption(s,v,'后壳与八处固定',132)
v=s.view_fit('DirectionalKeys',starts('CtrlDPad'),(272,150,79,47),(.5,-1,1.4));caption(s,v,'分离方向键、导架与硅胶',211);s.save()

s=d.Sheet(4,'圆形光驱盖与 OPEN 释放联动',['盖板包含一体轴耳、钢轴、单侧回位弹簧、齿扇及旋转阻力件，前部锁钩由 OPEN 滑块释放。','本页表示保存模型的装配关系；齿形、弹簧和联动均为学习近似，不代表已验证的运动行程。'])
v=s.view_fit('LidGearTrain',['LidResistancePinion','LidResistanceUnit','LidHingePin1'],(25,28,143,81),(-1,.2,.4),up);caption(s,v,'移开支承后的阻力小齿轮',129)
v=s.view_fit('LidSpring',['LidHingePin1','LidTorsionSpring1'],(237,30,136,73),(.3,-1,1),up);caption(s,v,'钢轴与回位弹簧',129)
v=s.view_fit('DiscCover',['DiscLid'],(27,139,153,64),(.5,1,-1.4),up);caption(s,v,'圆盖内侧的一体轴耳、齿扇和锁钩',211)
v=s.view_fit('ReleaseSlider',['OpenReleaseSlider','OpenSliderGuide','OpenReturnSpring'],(229,151,143,45),(0,0,1));d.dimension_box(s,v,['OpenReleaseSlider'],'x',141);caption(s,v,'移开键帽后的滑块与弹簧',211);s.save()

s=d.Sheet(5,'主机与手柄的真实实体剖面',['本页将实际三维 BRep 与指定 Y 平面相交；剖面填充只表示真正切到的材料。','主机截面显示板件、屏蔽、主轴与盖板的高度关系，手柄截面显示壳体、硅胶、接点和按键。'])
s.text(198,17,'A-A · 主机 Y=4 主轴区域',4,'middle');v=d.section_view(s,'ConsoleSection',body,(23,34,351,56),offset=4);caption(s,v,'主轴、光盘仓、主板与供电层',112)
s.text(198,136,'B-B · 手柄 Y=-234 方向键区域',4,'middle');v=d.section_view(s,'ControllerSection',pad,(23,155,351,40),offset=-234);caption(s,v,'上下曲面壳、硅胶、板件与键帽',211);s.save()

s=d.Sheet(6,'主机与手柄的分层爆炸结构',['爆炸工程保留原始几何与零件编号，通过展示位移分开外壳、板件、机构和输入层。','本页省略长线束、排线和密集外观文字以便阅读，完整原生工程、STEP 与网页仍保留这些组件。'])
v=s.view_fit('ConsoleExploded',without(body,'Lead','FlexTrace','Legend','Mark','Badge'),(17,29,192,167),(.5,-.45,1.3),exploded=True);caption(s,v,'圆盖、读取机构与分层屏蔽',211)
v=s.view_fit('ControllerExploded',without(pad,'Wire','Mark','Symbol','Direction','CtrlShoulder'),(221,32,157,160),(.3,-.7,1.3),exploded=True);caption(s,v,'手柄壳、按键、膜与板件',211);s.save()

s=d.Sheet(7,'双面主板与主要电子器件 · PU-7',['主板参考实物 PU-7 1-655-322-13A，包含 CPU、GPU、SPU、内存、音视频转换及 CD 相关封装。','本页对照同一块主板的上下两面；器件、引脚与布线是结构示意，不复现生产电路或电气性能。'])
v=s.view_fit('MainboardTop',d.keys_for(['Mainboard']),(26,32,164,141),(0,0,1));d.dimension_box(s,v,['Mainboard'],'x',20);d.dimension_box(s,v,['Mainboard'],'y',15);caption(s,v,'CPU、GPU、内存与接口分区',208)
v=s.view_fit('MainboardUnderside',d.keys_for(['Mainboard']),(223,32,164,141),(0,0,-1));caption(s,v,'CD 控制、缓冲与伺服驱动所在面',208);s.save()

s=d.Sheet(8,'橡胶悬挂光驱、主轴与进给机构',['光驱由三点橡胶支承隔开主机结构，包含主轴、电机、夹盘球、双导轨光头、蜗杆、减速齿轮和齿条。','光学与传动件是学习近似，只说明形状和位置；模型不执行读写、控制闭环或机械运动仿真。'])
keys=starts('OpticalBase','OpticalPeg','OpticalGrommet','Spindle','PickupRail','PickupCarriage','Lens','Objective','Sled','FeedReductionGear','FeedGearAxle','PickupRack','OpticalMotor','OpticalTerminal')
v=s.view_fit('OpticalTransport',keys,(24,30,174,152),(0,0,1));d.dimension_box(s,v,['OpticalBase'],'x',20);caption(s,v,'移开上盖后的完整读取机构',209)
v=s.view_fit('PickupAndDrive',starts('PickupRail','PickupCarriage','Lens','Objective','Sled','FeedReductionGear','FeedGearAxle','PickupRack'),(238,28,132,77),(0,0,1));caption(s,v,'蜗杆、齿轮、齿条与光头',127)
v=s.view_fit('SpindleClamp',starts('Spindle'),(265,150,78,48),(.7,-1,1.2),up);caption(s,v,'主轴、夹盘弹簧与定位球',211);s.save()

s=d.Sheet(9,'独立电源与手柄输入层',['电源板独立设置输入滤波、保险管、变压器、整流与输出器件，通过七芯线束连接主机。','数字手柄包含棕色板件、三组硅胶膜、分离碳膜接点和两块肩键小板；所有电子结构均为学习示意。'])
v=s.view_fit('PowerSupply',without(d.keys_for(['Power']),'ACInlet','ACPin','ResetSwitch'),(24,31,93,151),(0,0,1));d.dimension_box(s,v,['PowerBoard'],'x',20);d.dimension_box(s,v,['PowerBoard'],'y',16);caption(s,v,'原始独立电源板',210)
v=s.view_fit('ControllerPCB',starts('CtrlPCB','CtrlLogic','CtrlBoardCap','CtrlDPadMembraneFixed','CtrlFaceMembraneFixed','CtrlMenuFixed'),(188,31,187,69),(0,0,1));d.dimension_box(s,v,['CtrlPCB'],'x',119);caption(s,v,'主板与固定碳膜接点',134)
v=s.view_fit('InputMembranes',['CtrlDPadMembrane','CtrlFaceMembrane','CtrlMenuMembrane'],(166,151,138,47),(.5,-1,1.4),up);caption(s,v,'三组主输入硅胶膜',211)
v=s.view_fit('ShoulderContacts',[k for k in starts('CtrlLPCB','CtrlLCarrier','CtrlL1','CtrlL2') if k not in ['CtrlL1','CtrlL2','CtrlL1Mark','CtrlL2Mark']],(332,150,45,48),(.4,1,1),up);caption(s,v,'移开键帽后的肩键接点',211);s.save()

s=d.Sheet(10,'原版记忆卡与连接附件 · SCPH-1020',['记忆卡保留滑动后盖、两处固定和八枚金手指，内部采用同型号大板家族作近似参考，日期并未确认。','附件为日式电源线、十二位置 AV MULTI 转三 RCA 线及空白 12 cm CD；线缆使用缩短的展示长度。'])
card=d.keys_for(['MemoryCard']);v=s.view_fit('MemoryCardFront',card,(27,30,63,84),(0,0,1));d.dimension_box(s,v,['CardFront','CardRear'],'x',20);d.dimension_box(s,v,['CardFront','CardRear'],'y',17);caption(s,v,'灰色卡体',128)
v=s.view_fit('MemoryCardBoard',without(card,'CardRear','CardCapacity','CardScrew'),(113,30,63,84),(0,0,-1));caption(s,v,'移开后盖的大板内构',128)
v=s.view_fit('MainsCord',starts('ACWall','ACCord','ACDevice'),(227,29,148,85),(0,0,1));caption(s,v,'两片插头与八字端头',128)
v=s.view_fit('AVConnections',starts('AVPlug','AVCable','AVSplitter','AVBranch','RCA'),(34,145,132,53),(0,0,1));caption(s,v,'AV MULTI 与三路 RCA',211)
v=s.view_fit('BlankDisc',starts('BlankDisc'),(252,152,100,43),(0,0,1));d.dimension_box(s,v,['BlankDisc'],'x',142);caption(s,v,'空白学习光盘',211);s.save()

s=d.Sheet(11,'组件与显示材料索引',['同一组件可能包含多枚触点或文字实体，因此组件条目与实体数量分开统计。','零件编号关联原生装配、STEP 和网页网格；显示材料用于区分结构，不指定真实材料牌号。'])
names={'Body':'主机壳体与外观','Optical':'圆盖与读取机构','Controls':'主机控制与传动','FrontIO':'前部卡槽与手柄接口','Ports':'原始后部接口','Power':'独立电源与供电','Wiring':'线束与软排线','Mainboard':'PU-7 主板与器件','Shield':'分层屏蔽与隔板','Internal':'主机支承与固定','Controller':'原版数字手柄','MemoryCard':'原版灰色记忆卡','Accessories':'电源、AV 与空白媒体'}
for x,t in [(12,'装配分组'),(111,'条目'),(151,'显示材料'),(268,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=34+i*13.2
 s.text(12,y,names.get(name,name),3.3);s.text(120,y,count,anchor='middle');s.text(151,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3.2);s.text(268,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.2);s.line((12,y+4),(384,y+4))
s.text(12,211,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体 · COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'版本依据、近似边界与重建入口',['外观选择日版灰色 SCPH-1000、SCPH-1010 数字手柄与 SCPH-1020 记忆卡，保留原始接口家族。','图册是保存模型的版本快照；改变三维实体后，需要同步生成投影、尺寸、验证记录与网页。'])
sections=[(16,'资料与版本',['Sony SCPH-5500 说明书仅提供同系列外形尺寸参考。','iFixit 128089、Dig and Rescue 提供原版主机与周边实物拆解。','PSX-SPX 用于核对接口家族；记忆卡大板日期不作确定归属。']),
 (67,'近似与内容边界',['270 × 188 × 60 mm 不是经实测确认的 SCPH-1000 原厂尺寸图。','手柄、记忆卡、孔位、引脚、机构和线束均按学习用途近似绘制。','不复现制造公差、生产电路、游戏数据或经过验证的运动。']),
 (118,'可核对的检查记录',[f"{M['design_iterations']} 轮源码 / {M['physical_components']} 组件 / {M['solids']} 实体。",'完整重建、严格实体、装配求交与 STEP 回读分别记录。','字体、内容、每页视觉和原生尺寸引用随交付一并检查。']),
 (169,'继续修改的入口',['资料：references/SOURCES.md；清单：output/COMPONENTS.csv。','主要源码：tools/cadlib/ps1.py；逐轮入口：scripts/。','检查：output/reports/；修改后同步更新 CAD、图纸与网页。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
