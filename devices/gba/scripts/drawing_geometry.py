"""Twelve A3 sheets projected from original AGB-001 study BReps."""
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
body=d.keys_for(M['handheld_groups'])

s=d.Sheet(1,'原版横向掌机与官方外包络',['选择 Indigo AGB-001 与早期 AGB-CPU-02，保留反射式液晶、双 AA 电池和原版按钮布局。','官方外包络 144.5 × 82 × 24.5 mm；壳体曲率、壁厚、孔位与内部尺寸为学习近似。'])
v=s.view_fit('Front',body,(29,36,204,132),(0,0,1));d.dimension_box(s,v,body,'x',20);d.dimension_box(s,v,body,'y',17);caption(s,v,'原版十字键、A/B 与独立肩键',211)
v=s.view_fit('Hero',body,(253,51,127,105),(.4,-.7,2));caption(s,v,'前后壳、灰色镜框与侧饰',211);s.save()

s=d.Sheet(2,'背面电池盖与顶底边接口',['背面保留可拆电池盖、三翼固定件和腕带孔，上缘区分 Game Pak 卡槽与六触点 EXT。','底部按原版手册排列电源滑块、3.5 mm 耳机口和音量轮；不加入 USB 或内置充电接口。'])
v=s.view_fit('Rear',body,(25,35,183,145),(0,0,-1));caption(s,v,'背壳、双 AA 电池盖与学习标签',211)
v=s.view_fit('Top',body,(233,39,146,48),(0,1,0),up);caption(s,v,'上缘 EXT 与背面卡槽',110)
v=s.view_fit('Bottom',body,(233,145,146,38),(0,-1,0),up);d.dimension_box(s,v,body,'y',225);caption(s,v,'原版底边接口与整体厚度',211);s.save()

s=d.Sheet(3,'分层爆炸装配与独立零件',['每个实体以装配分组、稳定标识和唯一编号追溯，爆炸位移只用于观察层级。','本页省略密集端子和字符以保留可读性；完整原生工程、CSV 清单和网页保留所有组件。'])
v=s.view_fit('MainExploded',without(body,'Lead','Contact','Trace','Code','Mark','Passive','Wire','Spring'),(21,20,225,179),(.5,-.6,1.5),exploded=True);caption(s,v,'曲面壳体、屏幕、按键与双面主板',211)
v=s.view_fit('ControlExploded',d.keys_for(['Controls','ControlsInternal']),(267,31,109,163),(.2,-.6,1.5),exploded=True);caption(s,v,'独立控制件与胶膜',211);s.save()

s=d.Sheet(4,'真实实体截取的机身剖面',['剖面由已保存 BRep 与指定 Y 平面求交，填充仅表示真实切到的模型材料。','上部剖面显示液晶、处理器与卡槽空间，下部剖面区分电池舱、按键及扬声器。'])
s.text(198,17,'A-A · Y=12 mm',4,'middle');v=d.section_view(s,'UpperSection',body,(24,38,348,57),offset=12);caption(s,v,'反射 LCD、主板与背面插槽',115)
s.text(198,139,'B-B · Y=-20 mm',4,'middle');v=d.section_view(s,'LowerSection',body,(24,159,348,34),offset=-20);caption(s,v,'双 AA 电池舱与内部输入结构',212);s.save()

s=d.Sheet(5,'反射式液晶与早期四十针排线',['官方可视区域为 61.2 × 40.8 mm；本机使用无照明反射 TFT，不添加前光、背光或改装 IPS。','早期 AGB-CPU-02 实物的 1/40 标记指导插座选择，折叠排线绕过主板上缘而非穿过板件。'])
v=s.view_fit('DisplayWindow',starts('DisplayBezel','DisplayGlass','AdvanceMark'),(25,39,170,142),(0,0,1));d.dimension_box(s,v,['DisplayGlass'],'x',22);d.dimension_box(s,v,['DisplayGlass'],'y',15);caption(s,v,'官方屏幕可视尺寸',211)
v=s.view_fit('LCDStack',without(d.keys_for(['Display']),'Power'),(225,26,153,99),(.3,-.5,1.5),exploded=True);caption(s,v,'玻璃、偏光片、液晶与反射片',141)
v=s.view_fit('LCDConnector',d.keys_for(['DisplayInterconnect']),(236,158,139,38),(.2,-1,-1.5));caption(s,v,'40 位插座、锁条与排线',212);s.save()

s=d.Sheet(6,'早期双面主板与独立器件',['主板的 U 形电池避让、CPU AGB、外部 RAM、晶体和电源/音频器件依据早期实机照片布局。','芯片、引脚与被动器件为非功能性结构学习，模型不复现电路网络或制造封装公差。'])
board=d.keys_for(['Mainboard','DisplayInterconnect','CartridgeInterface','Ports'])
v=s.view_fit('BoardFront',board,(26,35,170,143),(0,0,1));d.dimension_box(s,v,['Mainboard'],'x',21);caption(s,v,'处理器、RAM 与按键金触点',211)
v=s.view_fit('BoardBack',board,(220,35,168,143),(0,0,-1));caption(s,v,'卡槽、LCD 接口与音频电源',211);s.save()

s=d.Sheet(7,'三组导电胶与肩键回位机构',['十字键、A/B 和 Start/Select 保留三组独立硅胶膜，空心穹顶、碳粒和分离金触点可分别查看。','L/R 肩键区分帽壳、转轴、轴座、回位弹簧、触觉开关与压杆；行程和胶厚为学习近似。'])
v=s.view_fit('Membranes',starts('DPadMembrane','ABMembrane','StartSelectMembrane'),(19,29,183,144),(.2,-.3,2));caption(s,v,'三组按键膜与金色分离触点',212)
v=s.view_fit('ShoulderMechanism',starts('Shoulder'),(226,35,155,65),(.2,-.7,1.8));caption(s,v,'分离左右肩键与回位部件',121)
v=s.view_fit('ShoulderDetail',starts('ShoulderSwitchL','ShoulderPivotL','ShoulderPivotSeatL','ShoulderReturnSpringL','ShoulderActuatorL'),(242,149,130,44),(.5,-.8,1.5));caption(s,v,'左肩键内部机构放大',212);s.save()

s=d.Sheet(8,'可更换双 AA 电池与极性接点',['两枚 AA 采用相反方向安装，独立正极端帽、负极端片、压缩弹簧和簧片保留可核对间隙。','电池舱、隔板、盖板和卡扣与主板分离，不使用后代掌机的内置锂电池方案。'])
v=s.view_fit('CellsAndContacts',starts('AACell','AAButton','AANegative','AAPositive'),(23,31,173,148),(.2,-.4,2));caption(s,v,'反向安装的双 AA 与独立接点',211)
v=s.view_fit('BatteryCompartment',starts('AABay','BatteryDoor','BatteryLatch','BatteryBayScrew'),(225,32,156,147),(.4,-.5,1.7),exploded=True);caption(s,v,'舱壁、隔板、盖板与卡扣',211);s.save()

s=d.Sheet(9,'扬声器、模拟音量与原版插座',['原版单声道扬声器包含独立磁体、锥架、薄振膜和两根焊线，对应前壳五条斜格栅。','金属屏蔽、绝缘壳、接点及模拟电位器分别建模，孔位和电气功能仅作非功能性结构说明。'])
v=s.view_fit('Speaker',d.keys_for(['Audio']),(23,30,166,74),(.3,-.6,1.6));caption(s,v,'单声道扬声器分层',121)
v=s.view_fit('EXT',starts('EXT'),(226,30,152,74),(.3,1,.5),up);caption(s,v,'六触点 EXT 屏蔽与舌片',121)
v=s.view_fit('VolumeHeadphone',starts('Volume','Headphone'),(24,146,167,48),(.2,-1,.8),up);caption(s,v,'模拟音量轮与耳机接点',212)
v=s.view_fit('CardReader',d.keys_for(['CartridgeInterface']),(226,146,150,48),(.3,1,1.2),up);caption(s,v,'32 触点 Game Pak 卡槽',212);s.save()

s=d.Sheet(10,'另附空白卡带与移除的备用电池',['空白 Game Pak 是额外学习件，参考 2001 年 AGB-E06-01 的 ROM、SRAM、监控器和电池焊盘关系。','外壳明确标为 NO GAME DATA，不包含商业游戏；CR1616 独立展示，卡带并非原版掌机标配。'])
v=s.view_fit('StudyCartridge',starts('StudyCart'),(22,34,172,135),(0,0,1));d.dimension_box(s,v,['StudyCartBack'],'x',21);caption(s,v,'空白学习标签与分离备用电池',211)
v=s.view_fit('CartridgeInternals',without(starts('StudyCart'),'Back','Wall','Front','Label','Title','Notice','Top','CR1616','BatteryCode'),(221,38,166,66),(0,0,1));caption(s,v,'双面板、32 触点与独立 IC',121)
v=s.view_fit('CartridgeExploded',without(starts('StudyCart'),'Lead','Edge','CR1616','BatteryCode'),(235,144,141,53),(.4,-.5,1.5),exploded=True);caption(s,v,'前后壳与内部层级',212);s.save()

s=d.Sheet(11,'组件分组与原生编号索引',['物理组件具备稳定标识、唯一编号、装配分组与材料属性，可与原生树和 CSV 清单交叉核对。','一个条目可以包含多个实体；字符及机构细节增加实体数，这些数量不等同于工厂物料表。'])
names={'Body':'原版曲面壳体与侧饰','Display':'反射液晶与状态导光','Controls':'外部按钮与音量轮','ControlsInternal':'胶膜与肩键机构','Battery':'双 AA 电池舱','Mainboard':'早期主板与器件','Audio':'单声道扬声器','DisplayInterconnect':'四十针液晶接口','Ports':'原版外部连接器','CartridgeInterface':'Game Pak 卡槽','BatteryContacts':'双 AA 极性接点','Fixings':'独立机械固定件','Markings':'背面学习标签','Accessories':'另附空白学习卡带'}
for x,t in [(12,'装配分组'),(111,'条目'),(151,'显示材料'),(268,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=32+i*11
 s.text(12,y,names.get(name,name),3.2);s.text(120,y,count,anchor='middle');s.text(151,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3.2);s.text(268,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.2);s.line((12,y+3.8),(384,y+3.8))
s.text(12,213,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体 · COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'资料、版本边界与继续修改入口',['官方原版规格与使用手册确定外部功能，早期实机正反面照片用于指导内部版本选择。','修改原生模型后，应同步重建尺寸、剖面、组件清单、导出件和网页，并重新执行几何检查。'])
sections=[(16,'资料与版本',['Nintendo 原始规格：144.5 × 82 × 24.5 mm，无照明反射 TFT。','Nintendo 原版使用手册：外部控制、接口和双 AA 电池。','iFixit 与 Gekkio 贡献者实物：AGB-CPU-02、40 针 LCD 与早期卡带。']),
 (67,'近似与内容边界',['屏幕可视区域采用官方 61.2 × 40.8 mm；曲率及壁厚近似。','元件、触点、弹簧与走线为非功能结构，不提供制造电路或公差。','另附空白 Game Pak 无游戏数据，外壳与内部尺寸为学习近似。']),
 (118,'交付与可核对记录',[f"{M['design_iterations']} 轮源码 / {M['physical_components']} 组件 / {M['solids']} 实体。",'源码重建、严格实体、装配求交、STEP 回读分别保留报告。','图册字体、逐页视觉、尺寸和原生图纸引用随交付检查。']),
 (169,'继续修改入口',['资料：references/SOURCES.md；清单：output/COMPONENTS.csv。','源码：tools/cadlib/gba.py；逐轮入口：scripts/。','检查：output/reports/；模型修改后同步图册与网页网格。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
