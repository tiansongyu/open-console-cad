"""Twelve model-derived A3 sheets: original 2020 optical Xbox Series X."""
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
def caption(s,v,t,y):s.text(v['x'],y,t+f" · {v['scale']:.3f}:1",anchor='middle')

s=d.Sheet(1,'2020 年原版光驱 Xbox Series X 总装',['代表版本为黑色 1 TB、带吸入式光驱的原版机；不是后期白色数字版或 2 TB 版本。','主机采用官方外形包络，控制器和局部内部尺寸均为照片指导近似；所有零件为非功能结构研究。'])
v=s.view_fit('ConsoleHero',console,(17,27,190,170),(.8,-1,.65),(0,0,1));caption(s,v,'方塔主机、凹面顶部排风与固定底座',212)
v=s.view_fit('ControllerHero',controller,(225,50,157,124),(.2,-.5,1.8));caption(s,v,'Series 原版布局控制器',212);s.save()

s=d.Sheet(2,'官方包络与前后接口位置',['微软 Disc design 规格为 151 × 151 × 301 mm；局部孔位、壁厚和接口轮廓为近似。','尺寸标注读取当前 CAD 投影；前 USB、配对、退碟、电源与背部接口保持独立零件。'])
v=s.view_fit('Front',console,(23,33,91,158),(0,-1,0),(0,0,1));d.dimension_box(s,v,console,'x',18);d.dimension_box(s,v,console,'y',15);caption(s,v,'原版前面板',212)
v=s.view_fit('Rear',console,(151,33,90,158),(0,1,0),(0,0,1));caption(s,v,'双 USB / LAN / 存储扩展 / HDMI / AC',212)
v=s.view_fit('Top',console,(278,54,96,110),(0,0,1));d.dimension_box(s,v,console,'y',390);caption(s,v,'顶部真实通孔与绿色内壁',187);s.save()

s=d.Sheet(3,'中央铸件、双主板与散热路径',['原版两块主板位于中央铸铝中框两侧，APU 一侧接铜均热板和阶梯鳍片。','另一侧布置光驱与上部电源；顶部轴流风扇向上排风，绿色格栅不是照明。'])
v=s.view_fit('CoreThermal',d.keys_for(['Frame','Mainboard','Storage','Cooling','Fan']), (18,27,178,169),(1,-.6,.5),(0,0,1));caption(s,v,'中框、双板与散热侧',212)
v=s.view_fit('CoreDrive',d.keys_for(['Frame','Mainboard','Optical','Power','Fan']), (220,27,162,169),(-1,-.5,.5),(0,0,1));caption(s,v,'光驱与上置电源侧',212);s.save()

s=d.Sheet(4,'双主板、十枚 GDDR6 与 2230 固态盘',['APU 为矩形裸晶/封装示意，十枚显存分布于其周围；背面保留供电器件与可拆固态盘。','I/O 板的大开口与独立无线板参考原版拆解；封装、接点、芯片数量不构成电路设计。'])
main=without(d.keys_for(['Mainboard','Storage']),'IOBoard','IOLogic','Southbridge','InterboardSocketIO')
v=s.view_fit('APUFront',main,(20,30,174,158),(1,0,0),(0,0,1));d.dimension_box(s,v,['APUBoard'],'y',15);caption(s,v,'APU 与十枚显存',212)
v=s.view_fit('APUBack',main,(223,30,162,158),(-1,0,0),(0,0,1));caption(s,v,'背面供电与 M.2 2230 存储',212);s.save()

s=d.Sheet(5,'实体剖面与空间层次',['剖面由保存的 BRep 与切平面相交产生；填充表示被切到的材料，不是绘制的示意轮廓。','切面贯穿主机与控制器的指定位置，尺寸和壁厚仅属于本学习模型。'])
s.text(110,17,'A-A · 主机 Y=0',4,'middle');v=d.section_view(s,'TowerSection',console,(22,33,166,155),(0,1,0),(0,0,1),0);caption(s,v,'中央铸件、双板、驱动器与散热侧',212)
s.text(304,17,'B-B · 控制器 Y=-45',4,'middle');v=d.section_view(s,'PadSection',controller,(223,53,160,90),(0,1,0),(0,0,1),-45);caption(s,v,'前后壳、双板与操作层',169);s.save()

s=d.Sheet(6,'主机分层爆炸与稳定编号',['主板、均热板、光驱、电源和屏蔽片沿中框两侧分开；风扇与壳体单独展示。','位移仅用于观察，编号与原生树和 CSV 相同；爆炸位置不是安装尺寸。'])
v=s.view_fit('ConsoleExploded',without(console,'SMD','Terminal','Contact','Lead','Mark','GreenVent'),(12,27,126,168),(.4,-1,.45),(0,0,1),exploded=True);caption(s,v,'完整爆炸总览',212)
core=[k for k in console if C[k].Assembly not in ['Body','Fan','Controls','Ports','Wiring']]
v=s.view_fit('CoreExplodedDetail',without(core,'SMD','Terminal','Contact','Lead','Mark'),(147,44,237,134),(.4,-1,.45),(0,0,1),exploded=True);caption(s,v,'中框两侧主板、光驱、电源与散热放大',212);s.save()

s=d.Sheet(7,'原版吸入式光驱与上部电源',['光驱保留独立金属罩、控制板、进盘胶辊、主轴和光学滑架；本模型不装入光盘。','电源采用独立带孔侧盖、PCB、磁性元件、电容和散热片；均为非功能结构。'])
v=s.view_fit('Optical',without(d.keys_for(['Optical']),'OpticalCover'),(20,33,174,155),(-1,-.5,.45),(0,0,1));caption(s,v,'光驱机制与独立控制板',212)
v=s.view_fit('Power',without(d.keys_for(['Power']),'PSUCover'),(223,41,162,139),(-1,-.3,.4),(0,0,1));caption(s,v,'上置内置电源内部',212);s.save()

s=d.Sheet(8,'铜均热板、阶梯鳍片与五叶风扇',['散热板和薄片各自保留为实体；原版顶部风扇依据拆解照片重构五片叶片。','叶片曲面、导热材料与小间隙为可观察的近似，不用于热仿真或性能计算。'])
v=s.view_fit('Cooling',d.keys_for(['Cooling']),(20,28,175,164),(1,-.5,.4),(0,0,1));caption(s,v,'铜均热板与 48 片阶梯鳍片',212)
v=s.view_fit('Fan',d.keys_for(['Fan']),(228,39,150,117),(.2,-.4,2));d.dimension_box(s,v,['FanDuct'],'x',18);caption(s,v,'顶置轴流风扇与安装承架',185);s.save()

s=d.Sheet(9,'Series 控制器、Share 与双板结构',['原版外观包含混合圆盘方向键、非对称摇杆、Share、USB-C 和 3.5 mm 音频口。','内部双板结构依据微软 Series 维修资料，不宣称与 2020 首发 PCB 修订完全相同。'])
v=s.view_fit('PadFront',controller,(18,35,177,140),(.08,-.15,2));caption(s,v,'Series 原版操作布局',212)
v=s.view_fit('PadBoards',without(controller,'PadBack','PadFront','GripCover','BatteryDoor','StickDome','StickCap','PadTrigger0','PadTrigger1'),(221,35,164,140),(.2,-.5,1.8));caption(s,v,'U 形主板、I/O 板与摇杆机制',212);s.save()

s=d.Sheet(10,'双 AA、四组电机、线束与附件',['控制器保留两枚 AA、两组握把电机、两组扳机电机、双同轴与独立紧固件。','附件包括 HDMI 与八字电源线；墙端插头采用通用结构示意，不指定地区插脚或认证。'])
v=s.view_fit('PadPower',starts('PadAA','PadBatteryTray','PadGripMotor','PadGripWeight','PadTriggerMotor','PadTriggerWeight'),(18,31,176,146),(.2,-.4,2));caption(s,v,'双 AA 与四组振动电机',212)
v=s.view_fit('Accessories',d.keys_for(['Accessories']),(222,34,162,143),(.2,-.4,2));caption(s,v,'独立线缆与带空腔接头',212);s.save()

s=d.Sheet(11,'组件编号、材料与分组清单',['编号贯穿原生工程、STEP、图册与网页；多实体文字条目不等同于原厂零件。','完整 COMPONENTS.csv 记录每个条目的几何、分组、材料和近似说明。'])
names={'Body':'主机外壳','Controls':'前部控制小板','Ports':'主机接口','Frame':'中框与固定件','Mainboard':'双主板与元件','Storage':'固态盘','Cooling':'均热板与鳍片','Fan':'顶部风扇','Optical':'吸入式光驱','Power':'内置电源','Shielding':'屏蔽结构','Wireless':'无线板','Wiring':'主机线束','Controller':'Series 控制器','Accessories':'线缆附件'}
for x,t in [(12,'装配分组'),(112,'条目'),(151,'显示材料'),(268,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=32+i*10.8;s.text(12,y,names.get(name,name),3.2);s.text(120,y,count,anchor='middle');s.text(151,y,' / '.join(sorted({r['material'] for r in rows})[:3]),3);s.text(268,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3);s.line((12,y+3.5),(384,y+3.5))
s.text(12,213,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'资料、模型边界与重建入口',['主机选择 2020 原版黑色 1 TB 光驱机；平台销量不等于此代表型号销量。','保存的实体、图册和网页共享组件身份，所有局部尺寸均应结合来源与近似说明阅读。'])
sections=[(16,'一手资料与版本范围',['微软官方 Disc design：151 × 151 × 301 mm 外形包络。','iFixit 2020 年原机拆解：34 张照片核对双板、光驱与散热结构。','微软 2023 Series 控制器维修手册：结构参考，不保证首发板号。']), (67,'近似与非功能边界',['壁厚、孔位、器件、线路和手柄曲率均为照片指导近似。','无可用电路、制造公差、热性能或电源安全认证。','参考照片不作为自产图像分发，所有模型图由 CAD 生成。']), (118,'可查对的交付记录',[f"{M['design_iterations']} 轮建模 / {M['physical_components']} 组件 / {M['solids']} 实体。",'原生重建、严格实体、装配干涉和 STEP 回读分别检查。','12 页 A3 图册、原生尺寸与网页检查均附独立记录。']), (169,'继续修改',['资料：references/SOURCES.md；清单：output/COMPONENTS.csv。','源码：tools/cadlib/seriesx.py；逐轮入口：scripts/。','原生文件保留参数与历史，精确实体以 FCStd / STEP 为准。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
