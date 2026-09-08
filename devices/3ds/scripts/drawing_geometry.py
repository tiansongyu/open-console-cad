"""Build twelve A3 vector sheets from the verified 3DS BReps."""
from pathlib import Path
import sys,os,math
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
repo=Path(__file__).resolve().parents[3];sys.path.insert(0,str(repo/'tools'))
from cadlib import drawings as d
import FreeCAD as App,Part

d.init_drawing(Path(__file__).resolve().parents[1]);C=d.C;M=d.M
main=d.keys_for(d.HH);ext=d.keys_for(d.HH,False)
upper=[k for k in main if C[k].PoseGroup=='Lid'];lower=[k for k in main if C[k].PoseGroup!='Lid']
theta=180-M['pose']['default_opening'];rot=App.Rotation(App.Vector(1,0,0),theta)
normal=tuple(rot.multVec(App.Vector(0,0,1)));up=tuple(rot.multVec(App.Vector(0,1,0)))
def caption(s,v,text,y):s.text(v['x'],y,text+f" · {v['scale']:.3f}:1",anchor='middle')
def legend(s,items,y=164,cols=3):
 for i,(key,label) in enumerate(items):
  x=10+(i%cols)*(376/cols);yy=y+(i//cols)*18
  s.text(x,yy,C[key].PartNumber,3.2,fill='#1B365D');s.text(x,yy+6,label,3.1)

s=d.Sheet(1,'Nintendo 3DS 展开总装',['CTR-001 初代；此页为 160° 展示开角。','闭合公开尺寸单独标在第 2 页，打开状态与内部细节为本模型几何。'])
v=s.view_fit('OpenFront',ext,(15,18,169,176),(0,0,1));d.dimension_box(s,v,main,'x',12,True);caption(s,v,'展开正视',207)
v=s.view_fit('OpenIsometric',ext,(207,18,179,176),(-.6,-.7,2.4));caption(s,v,'展开轴测',207);s.save()

s=d.Sheet(2,'闭合外形与接口位置',['闭合包络由官方 134 × 74 × 21 mm 建立。','闭合原生文件保留同一组组件与铰链轴，局部孔位和圆角为近似值。'])
v=s.view('ClosedTop',ext,109,62,1.2,center=(0,0,10.5),source='closed');d.dimension_box(s,v,main,'x',10,True);d.dimension_box(s,v,main,'y',18,True);caption(s,v,'闭合上视',112)
v=s.view('ClosedBottom',ext,302,62,1.2,normal=(0,0,-1),center=(0,0,10.5),source='closed');caption(s,v,'闭合底视',116)
v=s.view('ClosedRight',ext,110,163,1.0,normal=(1,0,0),center=(0,0,10.5),source='closed');d.dimension_box(s,v,main,'x',205,True);s.text(110,124,'右视 · 1:1',anchor='middle')
v=s.view('ClosedRear',ext,302,163,1.2,normal=(0,1,0),up=(0,0,1),center=(0,0,10.5),source='closed');caption(s,v,'后侧接口',189);s.save()

s=d.Sheet(3,'上下显示组件尺寸',['上屏有效显示区 76.8 × 46.08 mm，下屏为 61.44 × 46.08 mm。','显示窗口尺寸来自官方说明书；LCD 外壳、金属背板和膜层厚度为近似建模。'])
uk=d.keys_for(['LidDisplay']);lk=d.keys_for(['Display'])
v=s.view_fit('UpperDisplay',uk,(22,23,158,99),normal,up);d.dimension_box(s,v,['UpperGlass'],'x',15,True);d.dimension_box(s,v,['UpperGlass'],'y',19,True);caption(s,v,'上屏窗口',137)
v=s.view_fit('LowerDisplay',lk,(225,23,152,99),(0,0,1));d.dimension_box(s,v,['LowerGlass'],'x',15,True);d.dimension_box(s,v,['LowerGlass'],'y',391,True);caption(s,v,'下屏触控窗口',137)
v=s.view_fit('UpperDisplaySide',uk,(24,156,155,24),up,normal);caption(s,v,'上屏层叠侧视',198)
v=s.view_fit('LowerDisplaySide',lk,(225,156,151,24),(0,1,0),(0,0,1));caption(s,v,'下屏层叠侧视',198);s.save()

s=d.Sheet(4,'控制件与接口详图',['圆形滑控钮、充电口、SD 读卡器和摄像头采用独立组件。','放大视图展示当前实体几何，所有局部尺寸按近似值标注。'])
v=s.view_fit('CirclePadDetail',[k for k in C if k.startswith('CirclePad')],(14,16,104,72),(0,0,1));d.dimension_box(s,v,['CirclePadCap'],'x',10);caption(s,v,'Circle Pad',99)
v=s.view_fit('ChargeDetail',['ChargeJackShell','ChargeJackTongue'],(155,23,79,56),(0,1,0),(0,0,1));d.dimension_box(s,v,['ChargeJackShell'],'x',15);caption(s,v,'充电插孔',99)
v=s.view_fit('SDDetail',[k for k in C if k.startswith('SD') and k not in ['SDDoor','SDCard','SDFlex']],(276,16,105,72),(-1,-.15,.8));caption(s,v,'SD 卡座（取出卡片）',99)
v=s.view_fit('CameraDetail',[k for k in C if 'Camera' in k and k not in ['CameraFlex']],(14,122,105,64),(.3,-.4,-1));caption(s,v,'三摄像头组件',207)
v=s.view_fit('SpeakerDetail',['SpeakerFrame-1','SpeakerMagnet-1','SpeakerDiaphragm-1','SpeakerGasket-1'],(142,122,109,64),normal,up);caption(s,v,'单侧上屏扬声器',207)
v=s.view_fit('CardDetail',[k for k in C if k.startswith(('GameCard','CardContact'))],(276,122,105,64),(0,1,0),(0,0,1));d.dimension_box(s,v,['GameCardMouth'],'x',117);caption(s,v,'游戏卡插槽',207);s.save()

s=d.Sheet(5,'下机身与上盖真实剖面',['浅色区域由 BRep 与指定平面相交得到，不使用外观轮廓代替剖面。','上盖剖切平面随展示姿态旋转；局部厚度与安装间隙为近似设计。'])
s.text(198,15,'A-A · 下机身 Y=0 横剖面',4,'middle')
v=d.section_view(s,'LowerSection',lower,(12,27,372,50));caption(s,v,'下机身结构层',88)
pivot=App.Vector(*M['pose']['pivot_mm']);transform=App.Placement(App.Vector(),rot,pivot);n=rot.multVec(App.Vector(0,1,0));u=rot.multVec(App.Vector(0,0,1));point=transform.multVec(App.Vector(0,2*pivot.y,0));offset=n.dot(point)
s.text(198,121,'B-B · 上盖显示中心横剖面',4,'middle')
v=d.section_view(s,'UpperSection',upper,(12,133,372,49),tuple(n),tuple(u),offset);caption(s,v,'上盖、LCD 与显示窗口',204);s.save()

s=d.Sheet(6,'整机分层爆炸总览',['上下机身按原装配层展开；偏移仅用于分辨组件。','完整编号对应模型树及 COMPONENTS.csv，后续两页分别展开上下组件。'])
v=s.view_fit('CompleteExploded',main,(12,13,372,175),(1.7,-.2,-1),exploded=True);caption(s,v,'全部主机组件',207);s.save()

s=d.Sheet(7,'下机身内部与爆炸结构',['电池、主板、显示层、控制件和后盖分别展示。','电池位置及模块划分参考实机拆解，PCB 和封装尺寸为布局示意。'])
v=s.view_fit('LowerExploded',lower,(10,15,376,126),(1.7,-.2,-1),exploded=True)
legend(s,[('FrontDeck','控制面板'),('LowerGlass','下屏窗口'),('LowerLCD','下 LCD'),('Mainboard','主板'),('BatteryPouch','CTR-003 电池'),('BackCover','可拆后盖')],163);s.save()

s=d.Sheet(8,'上盖显示与光学组件爆炸',['上盖包含 LCD、立体膜层、三个摄像头及双扬声器。','卷绕排线在铰链中预留通道，展示姿态可由原生参数和宏重现。'])
v=s.view_fit('UpperExploded',upper,(10,15,376,126),(1.7,-.2,-1),exploded=True)
legend(s,[('LidBezel','上盖黑色面板'),('UpperGlass','上屏窗口'),('UpperLCD','上 LCD'),('InnerCameraPCB','内摄像头小板'),('SpeakerFrame-1','扬声器'),('LidBackCover','上盖外壳')],163);s.save()

s=d.Sheet(9,'主板与电池组件',['主要封装与 Wi-Fi、红外、SD 模块均为独立实体。','CTR-003 电池按 1300 mAh / 5 Wh 标识，内部电芯形态为示意。'])
v=s.view_fit('MotherboardDetail',d.keys_for(['Mainboard']),(20,22,225,118),(0,0,-1));d.dimension_box(s,v,['Mainboard'],'x',13);caption(s,v,'主板与子板背视',153)
v=s.view_fit('BatteryDetail',d.keys_for(['Battery']),(285,25,82,113),(0,0,-1));d.dimension_box(s,v,['BatteryPouch'],'x',14);d.dimension_box(s,v,['BatteryPouch'],'y',390);caption(s,v,'电池与端子',153)
s.text(12,178,'ARM / RAM / NAND / 电源与音频封装：近似布局');s.text(12,190,'Wi-Fi、IR、SD 小板：按实机模块划分建模');s.text(12,202,'不包含真实电路、布线、料号精度或制造公差。');s.save()

s=d.Sheet(10,'伸缩触控笔与充电底座',['触控笔包含分离的笔尖、外管、内杆与端帽。','底座为原款被动充电触点结构示意，附件尺寸均为模型近似值。'])
ck=d.keys_for(['Cradle']);sk=d.keys_for(['Accessories'])
v=s.view_fit('CradleTop',ck,(19,22,197,119),(0,0,1));d.dimension_box(s,v,ck,'x',13);d.dimension_box(s,v,ck,'y',18);caption(s,v,'充电底座俯视',153)
v=s.view_fit('CradleSide',ck,(28,166,171,22),(1,0,0),(0,0,1));caption(s,v,'底座侧视',206)
v=s.view_fit('Stylus',sk,(237,21,42,151),(0,0,1));d.dimension_box(s,v,sk,'y',296);caption(s,v,'收拢触控笔',190)
v=s.view_fit('CradleContactDetail',[k for k in C if k.startswith(('CradleContact','CradleSpring')) and k!='CradleContactCarrier'],(312,38,71,114),(.6,-1,.5));caption(s,v,'充电弹片与弹簧',172);s.save()

s=d.Sheet(11,'组件与材料索引',['组件编号贯穿原生文件、爆炸装配与零件清单。','文字字形等多实体对象作为一个组件记录，组件数与实体数分别统计。'])
names={'Body':'下机身外壳','Lid':'上盖外壳','Hinge':'铰链','Display':'下显示组件','LidDisplay':'上显示组件','Controls':'控制件','Ports':'插槽与接口','LidInternal':'上盖内部','Internal':'下机身内部','Accessories':'触控笔','Battery':'电池','Mainboard':'主板与子板','Cradle':'充电底座'}
for x,t in [(12,'装配分组'),(115,'组件数'),(164,'材质显示角色'),(282,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,22),(384,22))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=34+i*11.3
 s.text(12,y,names.get(name,name));s.text(126,y,count,anchor='middle');s.text(164,y,' / '.join(sorted(set(r['material'] for r in rows))[:3]),3.1);s.text(282,y,rows[0]['part_number']+' … '+rows[-1]['part_number']);s.line((12,y+4),(384,y+4))
s.text(12,203,f"合计 {M['physical_components']} 个组件 / {M['solids']} 个实体；完整清单见 COMPONENTS.csv",3.6,fill='#1B365D');s.save()

s=d.Sheet(12,'尺寸依据与验证索引',['官方闭合尺寸与本模型局部近似尺寸分别记录。','图纸为已保存 CAD 版本的快照，改模后需要重新生成和检查。'])
sections=[(16,'官方尺寸依据',['Nintendo 3DS CTR-001：闭合 134 × 74 × 21 mm。','上屏 76.8 × 46.08 mm；下屏 61.44 × 46.08 mm。','来源：Nintendo 官方说明书第 20–23、100–101 页。']), (67,'结构参考',['iFixit 2011 Nintendo 3DS 实机拆解。','局部外形、壁厚、孔位和内部模块为近似设计。','充电底座、触控笔与 160° 开角属于展示模型参数。']), (118,'检查证据',[f"{M['design_iterations']} 轮建模；{M['physical_components']} 个组件独立源码重建匹配。",'原生展开、闭合、爆炸文件及四份 STEP 已回读检查。','最终装配实体求交、图纸尺寸和字体检查记录见 reports/。']), (169,'维护入口',['来源链接：references/SOURCES.md。','零件索引：COMPONENTS.csv；源码：scripts/iterNN_*.py。','网页网格由同一 FreeCAD 组件导出，精确实体以 FCStd / STEP 为准。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
