"""Twelve A3 model-derived sheets for the original DK-52 study."""
from pathlib import Path
import sys,os
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
repo=Path(__file__).resolve().parents[3];sys.path.insert(0,str(repo/'tools'))
from cadlib import drawings as d
import FreeCAD as App,Part

d.init_drawing(Path(__file__).resolve().parents[1]);C=d.C;M=d.M
main=d.keys_for(M['handheld_groups']);upper=[k for k in main if C[k].PoseGroup=='Lid'];lower=[k for k in main if C[k].PoseGroup!='Lid']
rot=App.Rotation(App.Vector(1,0,0),180-M['pose']['default_opening']);normal=tuple(rot.multVec(App.Vector(0,0,1)));up=tuple(rot.multVec(App.Vector(0,1,0)))
def starts(*p):return [k for k in C if k.startswith(p)]
def without(keys,*p):return [k for k in keys if not any(v in k for v in p)]
def caption(s,v,t,y):s.text(v['x'],y,t+f" · {v['scale']:.3f}:1",anchor='middle')

s=d.Sheet(1,'1982 年原版 Donkey Kong DK-52 展开总装',['橙色双屏原机，展示开角 170°；两屏为固定游戏反射式 LCD，无背光或触控。','整体参考馆藏实测，局部尺寸、图形与内部结构为近似；不是现代纪念版或可运行游戏。'])
v=s.view_fit('OpenFront',main,(20,26,165,168),(0,0,1));caption(s,v,'原版双屏与独立控制件',212)
v=s.view_fit('OpenIso',main,(218,28,165,165),(.4,-.6,2));caption(s,v,'铰链、中央排线与前卡扣',212);s.save()

s=d.Sheet(2,'合拢外壳、标题金属板与电池盖',['Museums Victoria 馆藏 HT38633 合拢实测 115 × 73 × 23 mm；不是工厂制造规格。','本页尺寸来自当前模型，含近似细脊与铭文；原电池盖依据存留实物照片重建。'])
v=s.view_fit('ClosedTop',main,(19,31,169,90),(0,0,1),source='closed');d.dimension_box(s,v,main,'x',20);d.dimension_box(s,v,main,'y',215);caption(s,v,'横纹金属板与原版铭牌',139)
v=s.view_fit('ClosedRear',main,(226,31,160,90),(0,0,-1),(0,-1,0),source='closed');caption(s,v,'五枚下壳螺钉与独立电池盖',139)
v=s.view_fit('ClosedSide',main,(23,159,355,33),(1,0,0),(0,0,1),source='closed');d.dimension_box(s,v,main,'y',393);caption(s,v,'闭合侧面与卡扣层次',212);s.save()

s=d.Sheet(3,'两屏反射式 LCD 分层与固定图形',['每屏分别保留反射片、偏光层、两片玻璃、液晶间隙、固定图形膜和周边压框。','前偏光层以周边示意表达便于观察；红钢架、梯子、蓝建筑与黑色液晶段为几何重绘。'])
v=s.view_fit('LowerDisplay',d.keys_for(['Display']),(23,28,171,103),(0,0,1));d.dimension_box(s,v,['LowerLCDGlassFront'],'x',18);caption(s,v,'下屏固定游戏图形与 LCD 层',150)
v=s.view_fit('UpperDisplay',d.keys_for(['LidDisplay']),(225,28,159,103),normal,up);caption(s,v,'上屏城市、钢架和吊钩示意',150)
v=s.view_fit('LCDSide',d.keys_for(['Display']),(25,173,354,23),(0,1,0),(0,0,1));caption(s,v,'玻璃、薄膜和导电胶的侧向层次',212);s.save()

s=d.Sheet(4,'原版十字键、JUMP 与系统键',['十字键和圆形 JUMP 为独立塑料致动件，下方保留胶膜、碳接点与主板印刷触点。','GAME A / GAME B / TIME 竖排；ALARM 与 ACL 是凹入的金属接点。'])
v=s.view_fit('DPad',starts('DPad'),(23,29,152,91),(.1,-.4,2));d.dimension_box(s,v,['DPad'],'x',18);caption(s,v,'原版十字方向键',142)
v=s.view_fit('SystemKeys',starts('GameA','GameB','Time','Alarm','ACL','JumpKey','JumpStem'),(225,29,151,91),(.2,-.4,2));caption(s,v,'JUMP 和系统操作件',142)
v=s.view_fit('Membranes',d.keys_for(['ControlsInternal']),(25,167,354,31),(.1,-.3,2));caption(s,v,'独立胶膜、弹性凸台与碳接点',212);s.save()

s=d.Sheet(5,'上下机身真实 BRep 剖面',['剖面由保存的实体与指定平面相交生成，浅色填充对应被切到的实体材料。','上盖剖切平面随展示角度旋转，不能把展示姿态的投影长度当作工厂尺寸。'])
s.text(198,17,'A-A · 下机身 Y=-1.5',4,'middle');v=d.section_view(s,'LowerSection',lower,(23,35,351,57),offset=-1.5);caption(s,v,'后壳、主板、LCD 与控制面板',115)
pivot=App.Vector(*M['pose']['pivot_mm']);transform=App.Placement(App.Vector(),rot,pivot);n=rot.multVec(App.Vector(0,1,0));u=rot.multVec(App.Vector(0,0,1));point=transform.multVec(App.Vector(0,70,0))
s.text(198,137,'B-B · 上屏中心横剖面',4,'middle');v=d.section_view(s,'UpperSection',upper,(23,156,351,39),tuple(n),tuple(u),n.dot(point));caption(s,v,'上壳、冲压压板、LCD 和压框',212);s.save()

s=d.Sheet(6,'分层爆炸与十九枚原版固定件',['五枚下壳长螺钉、四枚上盖外螺钉、五枚主板小螺钉和五枚上屏压板小螺钉。','爆炸位移仅用于展示结构，稳定编号对应 CSV；完整文件保留全部导体与薄膜。'])
v=s.view_fit('LowerExploded',without(lower,'Trace','Finger','Pin','Legend','Mark','Conductor','Clock'),(18,28,174,168),(.6,-.3,-1.5),(0,-1,0),exploded=True);caption(s,v,'下机身、主板和按键分层',212)
v=s.view_fit('UpperExploded',without(upper,'Trace','Stripe','Window','Mark','Ridge'),(222,28,161,168),(.6,-.3,-1.5),(0,-1,0),exploded=True);caption(s,v,'上盖、金属压板和屏幕分层',212);s.save()

s=d.Sheet(7,'原版酚醛主板、SM510 与分立器件',['主板背面保留菱形控制器、圆柱晶体、两枚电容与少量分立件；正面为绿色印刷控制面。','SM510 的身份依据 MAME 原始逆向源码；封装尺寸、引脚与走线是非功能性结构近似。'])
v=s.view_fit('BoardRear',d.keys_for(['Mainboard']),(22,32,172,143),(0,0,-1),(0,-1,0));d.dimension_box(s,v,['Mainboard'],'x',20);caption(s,v,'背面控制器、晶体和元件',212)
v=s.view_fit('BoardFront',d.keys_for(['Mainboard']),(224,32,160,143),(0,0,1));caption(s,v,'绿色控制侧与独立碳接点',212);s.save()

s=d.Sheet(8,'上屏冲压压板与外露印刷排线',['压板包含中央窗口、压筋和五个固定点；两侧铰链采用橙色分段套筒与钢轴。','中央白底黑导体排线分桥段和上下引出段表达；开合间隙检查不等于柔性疲劳认证。'])
v=s.view_fit('Retainer',starts('UpperRetainer','UpperPressedRib','Retainer'),(22,29,173,119),normal,up);caption(s,v,'原版上屏冲压金属压板',169)
v=s.view_fit('HingeFlex',d.keys_for(['Hinge','Wiring']), (221,30,161,63),(.1,-.6,1.5));caption(s,v,'两侧铰链与中央印刷桥段',117)
v=s.view_fit('UpperTail',starts('UpperRibbon'),(222,151,159,44),normal,up);caption(s,v,'上屏独立排线引出片',212);s.save()

s=d.Sheet(9,'双纽扣电池、接点与独立电池盖',['原机后盖标示 LR44 或 SR44 ×2、DC3V；保留两只圆形电池仓与独立金属接点。','电池内部为非功能示意；盖板局部卡扣和滑动箭头参考原机照片，不作为制造配合数据。'])
v=s.view_fit('Battery',d.keys_for(['Battery']),(24,32,168,143),(.15,-.3,2));caption(s,v,'两只纽扣电池与接点',212)
v=s.view_fit('BatteryDoor',starts('BatteryDoor'),(232,31,139,112),(0,0,-1),(0,-1,0));d.dimension_box(s,v,['BatteryDoor'],'x',18);caption(s,v,'独立滑盖、保持片和方向指示',171)
s.text(224,192,'电源为两枚纽扣电池；无 USB 或 AC 接口。',3.1);s.save()

s=d.Sheet(10,'后壳压电发声片与两根导线',['原机在后壳固定一片压电音片，两根红色导线连接至主板。','黄铜片、陶瓷层和电极分别建模；无现代扬声器磁路、背光电源或振动马达。'])
v=s.view_fit('Piezo',d.keys_for(['Audio']),(24,32,170,141),(.2,-.4,2));caption(s,v,'压电片、电极与独立红线',212)
v=s.view_fit('RearInterior',['BackCover']+d.keys_for(['Audio']), (222,33,160,138),(0,0,1));caption(s,v,'后壳中的定位环和接线槽',212);s.save()

s=d.Sheet(11,'稳定组件编号、材料与分组索引',['组件编号贯穿原生工程、STEP、爆炸视图、网页和 CSV 清单。','文字或多段印刷条目可含多个实体，因此条目数不等于实体数，也不是原厂 BOM。'])
names={'Body':'下壳与铭牌','Lid':'上壳与标题板','Hinge':'两侧铰链','Display':'下屏 LCD 和图形','LidDisplay':'上屏 LCD 和图形','Controls':'原版控制件','ControlsInternal':'胶膜与碳接点','Mainboard':'主板与元件','Battery':'双纽扣电池和接点','Audio':'压电片与导线','LidInternal':'上屏压板和支承','Internal':'下机身内部支承','Fixings':'独立固定螺钉','Wiring':'中央排线桥段'}
for x,t in [(12,'装配分组'),(112,'条目'),(151,'显示材料'),(268,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=32+i*11.2;s.text(12,y,names.get(name,name),3.2);s.text(120,y,count,anchor='middle');s.text(151,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3.0);s.text(268,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.0);s.line((12,y+3.5),(384,y+3.5))
s.text(12,213,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体 · COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'资料依据、近似边界与继续重建',['代表版本为 1982 年橙色 Donkey Kong DK-52；Game & Watch 平台销量不等于此机型销量。','保存的 CAD、图纸和网页共享组件身份；修改后应重新生成并核对所有交付。'])
sections=[(16,'一手结构与尺寸资料',['Museums Victoria HT38633：合拢实测 115 × 73 × 23 mm。','Damn Technology 58 张拆解照片及 Duddyfinger 维修照片。','Toy Heaven 原机照片补充存留电池盖；完整链接见 SOURCES.md。']), (67,'近似与非功能边界',['馆藏尺寸是实物测量，不冒充原厂制造规格。','局部壁厚、孔位、元件、导线和图形为近似结构示意。','无游戏 ROM、工作电路、配合公差或排线疲劳寿命保证。']), (118,'可查对的独立记录',[f"{M['design_iterations']} 轮源码 / {M['physical_components']} 组件 / {M['solids']} 实体。",'原生重建、严格实体、多姿态装配和 STEP 回读分别核验。','12 页 PDF、原生尺寸、逐页视觉和网页检查保留报告。']), (169,'继续修改入口',['资料：references/SOURCES.md；清单：output/COMPONENTS.csv。','源码：tools/cadlib/gamewatch.py；逐轮入口：scripts/。','检查：output/reports/；精确实体以 FCStd / STEP 为准。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
