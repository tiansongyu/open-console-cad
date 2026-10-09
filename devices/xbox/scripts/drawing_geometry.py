"""Model-derived A3 study: original 2001 Xbox v1.0 and wired Duke."""
from pathlib import Path
import os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
repo=Path(__file__).resolve().parents[3];sys.path.insert(0,str(repo/'tools'))
from cadlib import drawings as d
import FreeCAD as App,Part
d.init_drawing(Path(__file__).resolve().parents[1]);C=d.C;M=d.M
console=d.keys_for(M['envelope_groups']);controller=d.keys_for(['Controller'])
def starts(*p):return [k for k in C if k.startswith(p)]
def without(keys,*p):return [k for k in keys if not any(t in k for t in p)]
def caption(s,v,t,y=212):s.text(v['x'],y,t+f" · {v['scale']:.3f}:1",anchor='middle')
s=d.Sheet(1,'2001 年原版 Xbox 与有线 Duke 总装',['代表版本为早期黑色 v1.0 主机，采用主动 GPU 散热与原版 Duke 有线控制器。','外形包络来自微软明确标为近似的规格；局部尺寸与内部布置为照片指导的非功能研究。'])
v=s.view_fit('ConsoleHero',console,(15,30,215,166),(.6,-1,1.5),(0,0,1));caption(s,v,'顶部宽 X、绿色饰牌与四个前手柄口')
v=s.view_fit('DukeHero',controller,(245,36,140,155),(.2,-.4,2));caption(s,v,'原版 Duke 与快速脱离线缆');s.save()
s=d.Sheet(2,'近似包络与原版接口布局',['微软原文采用 approximate 320 × 100 × 260 mm；本模型按 XYZ 排列为 320 × 260 × 100 mm。','以下数值读取当前模型，不等于原厂制造图；侧面格栅、接口和按钮各自保留为实体。'])
v=s.view_fit('Front',console,(20,40,173,84),(0,-1,0),(0,0,1));d.dimension_box(s,v,console,'x',25);d.dimension_box(s,v,console,'y',15);caption(s,v,'前面板、托盘、两键与四口',149)
v=s.view_fit('Rear',console,(20,157,173,47),(0,1,0),(0,0,1));caption(s,v,'Ethernet / AV / AC / 排风')
v=s.view_fit('Top',console,(220,38,150,149),(0,0,1));d.dimension_box(s,v,console,'y',390);caption(s,v,'原版顶部近似包络');s.save()
s=d.Sheet(3,'v1.0 主板与两层驱动器托架',['主板位于下部，左侧 DVD 与右侧 3.5 英寸硬盘装在独立塑料托架中。','右侧是开放式内置电源；后部风扇与 CPU 被动散热、GPU 主动散热共同占据主板后方。'])
v=s.view_fit('Internal',without(d.keys_for(['Frame','Mainboard','Cooling','Fan','Power','Optical','Storage']),'UpperShield','DVDCover','HDDCover','HDDLabel'),(17,28,178,169),(.6,-1,1.3),(0,0,1));caption(s,v,'移除顶盖与驱动器上盖')
v=s.view_fit('BareBoard',d.keys_for(['Mainboard','Cooling','Fan','Power']),(218,33,167,159),(0,0,1));caption(s,v,'取下驱动器后俯视布局');s.save()
s=d.Sheet(4,'早期主板、四枚内存与并行 ATA',['发售期拆解更正指出四枚已安装内存分布于两面；模型同时保留独立空焊位。','733 MHz CPU、NV2A、MCPX 与其他封装只表达布局；简化引脚、绕组和元件并非可用电路。'])
v=s.view_fit('BoardFront',d.keys_for(['Mainboard']),(18,29,176,170),(0,0,1));d.dimension_box(s,v,['Mainboard'],'x',18);caption(s,v,'芯片、供电与 40 针 IDE 插座')
v=s.view_fit('BoardBack',d.keys_for(['Mainboard']),(222,29,163,170),(0,0,-1));caption(s,v,'背面内存与空焊位');s.save()
s=d.Sheet(5,'实体剖面与壳内空间',['剖面由实际 BRep 与切平面相交获得；剖面材料填充不表示额外零件。','壳体、主板、屏蔽、驱动器和控制器层次均采用当前保存模型；壁厚为研究近似。'])
s.text(110,17,'A-A · 主机 Y=0',4,'middle');v=d.section_view(s,'ConsoleSection',console,(18,40,177,123),(0,1,0),(0,0,1),0);caption(s,v,'双驱动器、主板与开放电源',190)
s.text(305,17,'B-B · Duke Y=-70',4,'middle');v=d.section_view(s,'DukeSection',controller,(222,59,164,86),(0,1,0),(0,0,1),-70);caption(s,v,'双壳、单主板与操作层',190);s.save()
s=d.Sheet(6,'主机分层爆炸与稳定组件编号',['上下壳、EMI 屏蔽、主板和两个驱动器托架沿层次展开。','所有爆炸位置仅用于观察；组件编号与原生工程和 COMPONENTS.csv 保持一致。'])
v=s.view_fit('ConsoleExploded',without(console,'SMD','Terminal','Pads','Pin','Mark'),(13,25,174,175),(.6,-1,.55),(0,0,1),exploded=True);caption(s,v,'完整主机分层总览')
v=s.view_fit('DrivesExploded',without(d.keys_for(['Optical','Storage']),'LabelMark'),(209,28,176,169),(.6,-1,.7),(0,0,1),exploded=True);caption(s,v,'DVD 与硬盘分解放大');s.save()
s=d.Sheet(7,'托盘式 DVD 与 3.5 英寸 IDE 硬盘',['DVD 保留可拆上盖、空载托盘、主轴、导轨、光学滑架和并行 ATA 插座。','硬盘保留铸壳、盘片、磁头臂与下部逻辑板；不将拆解样机的物理盘容量等同于用户可用容量。'])
v=s.view_fit('DVD',without(d.keys_for(['Optical']),'DVDCover'),(20,29,174,169),(.6,-1,1.5),(0,0,1));caption(s,v,'左侧原版托盘式光驱')
v=s.view_fit('HDD',without(d.keys_for(['Storage']),'HDDCover','HDDLabel'),(223,32,162,165),(.6,-1,1.5),(0,0,1));caption(s,v,'右侧硬盘与独立托架');s.save()
s=d.Sheet(8,'主动 GPU 散热与开放式内置电源',['早期 v1.0 保留 GPU 上的小型主动风扇；后期被动 GPU 修订不作为本模型主板参考。','散热片、风扇、电源绝缘片、磁性元件与电容用于观察空间关系，不提供热性能或电气认证。'])
v=s.view_fit('Cooling',d.keys_for(['Cooling','Fan']),(20,31,174,164),(.6,-1,1.1),(0,0,1));caption(s,v,'CPU 被动、GPU 主动与后排风')
v=s.view_fit('Power',d.keys_for(['Power']),(223,31,162,164),(.6,-1,1.6),(0,0,1));caption(s,v,'开放式电源板与绝缘层');s.save()
s=d.Sheet(9,'原版 Duke 操作布局与单主板',['原版 Duke 采用非对称摇杆、六个右侧按键、Start / Back 和两个顶部存储卡口。','绿色中心饰牌为静态结构；无现代复刻 LCD、Share、USB-C 或 AA 电池。'])
v=s.view_fit('DukeFront',without(controller,'DukeCable','Breakaway','DukePlug','DukeConsolePlug'),(18,29,177,165),(.08,-.15,2));caption(s,v,'六键与大型中心静态饰牌')
v=s.view_fit('DukeBoard',without(controller,'DukeFront','DukeBack','DukeJewel','DukeStickDome','DukeStickCap','DukeCable','Breakaway','DukePlug','DukeConsolePlug'),(222,29,163,165),(.2,-.4,2));caption(s,v,'单主板、摇杆与顶部存储卡口');s.save()
s=d.Sheet(10,'Duke 接点、六穹顶方向键与线缆',['六个右键保留独立碳接点贴片与不带碳粒的硅胶层；方向键采用六个弹性穹顶。','扳机保留压缩弹簧与电位器；两侧为大小不同的振动电机，线缆包含原版快速脱离接头。'])
v=s.view_fit('DukeMechanism',starts('DukeContact','DukeCarbon','DukeKeyDome','DukeSixKey','DukeDPadCarrier','DukeDirection','DukeSystemContact','DukeSystemPill','DukeSystemDome','DukeTrigger','DukeMotor'),(18,28,177,169),(.4,-.7,1.5));caption(s,v,'接点层、扳机与双振动电机')
v=s.view_fit('Accessories',d.keys_for(['Accessories']),(222,29,163,167),(.2,-.4,2));caption(s,v,'复合 AV / RCA 与八字电源线');s.save()
s=d.Sheet(11,'组件清单、分组与身份追踪',['清单中的组件条目包含近似封装、引脚和多实体文字，不能等同于原厂采购 BOM。','每个条目的几何、分组、编号、材料和近似说明均记录在 COMPONENTS.csv。'])
for x,t in [(12,'装配分组'),(112,'条目'),(151,'显示材料'),(268,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
names={'Body':'主机外壳','Controls':'前部控制','Ports':'主机接口','Frame':'屏蔽与固定件','Mainboard':'早期主板','Cooling':'CPU / GPU 散热','Fan':'后排风','Optical':'托盘式 DVD','Storage':'IDE 硬盘','Power':'开放内置电源','Wiring':'主机线束','Controller':'有线 Duke','Accessories':'线缆附件'}
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=32+i*12;s.text(12,y,names.get(name,name),3.2);s.text(120,y,count,anchor='middle');s.text(151,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3);s.text(268,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3);s.line((12,y+3.5),(384,y+3.5))
s.text(12,213,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体",3.5,fill='#1B365D');s.save()
s=d.Sheet(12,'一手资料、修订边界与重建入口',['研究对象为 2001 年黑色原版 v1.0 与原版有线 Duke；平台销量不等于此代表型号销量。','本图册不混用 Xbox 360、Xbox One、Series 或现代 Duke 复刻的内部结构。'])
sections=[(16,'一手资料与版本选择',['微软存档 Technical Specifications：外形明确标作近似。','Van’s Hardware 2001 发售期拆解：主动 GPU、四枚内存与双驱动器。','Fictiv 原版 Duke 拆解：单主板、独立碳贴片、六穹顶方向键。']), (67,'补充参考与非功能边界',['iFixit 仅参考原版外壳与托架，不复制其后期被动 GPU 主板。','局部尺寸、壁厚、线束和器件为照片指导近似，无制造公差。','无可用电路、实际存储容量、热性能或电源安全认证。']), (118,'交付与对应关系',[f"{M['design_iterations']} 轮建模 / {M['physical_components']} 组件 / {M['solids']} 实体。",'原生工程、STEP、图册与网页共享组件身份与来源边界。','几何、干涉、源码重建、图册和网页验收记录位于 reports/。']), (169,'继续修改',['资料：references/SOURCES.md；清单：output/COMPONENTS.csv。','源码：tools/cadlib/xbox.py；逐轮入口：scripts/。','Rebuild_OriginalXbox.FCMacro 从源码生成独立重建目录。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
