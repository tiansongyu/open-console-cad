"""Twelve PSP-1000 A3 sheets, projected from the saved physical component BReps."""
from pathlib import Path
import os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
repo=Path(__file__).resolve().parents[3];sys.path.insert(0,str(repo/'tools'))
from cadlib import drawings as d
import FreeCAD as App,Part

d.init_drawing(Path(__file__).resolve().parents[1]);C=d.C;M=d.M
main=d.keys_for(d.HH);ext=d.keys_for(d.HH,False);body=d.keys_for(M['envelope_groups'])
def caption(s,v,text,y):s.text(v['x'],y,text+f" · {v['scale']:.3f}:1",anchor='middle')
def legend(s,items,y=168):
 for i,(key,label) in enumerate(items):
  x=12+(i%3)*127;yy=y+(i//3)*18
  s.text(x,yy,C[key].PartNumber,3.2,fill='#1B365D');s.text(x,yy+6,label,3.1)

def starts(*prefixes):return [k for k in C if k.startswith(prefixes)]

s=d.Sheet(1,'PSP-1000 正面总装',['初代单模拟滑杆、四向键和 HOME 系统键列。','主体公开尺寸不包含最大突出部位；局部外形和内部模块为近似研究模型。'])
v=s.view_fit('FrontAssembly',ext,(22,25,350,150),(0,0,1));d.dimension_box(s,v,body,'x',15,True);d.dimension_box(s,v,body,'y',12,True);caption(s,v,'正面总装 · 主体 170 × 74 mm',198);s.save()

s=d.Sheet(2,'后部、侧面与接口布局',['主体厚度 23 mm 不包含最大突出部位。','侧视图左侧标注主体，右侧为当前模型含按键的厚度；下方分别展示顶边和底边接口。'])
v=s.view_fit('RearAssembly',ext,(18,26,177,84),(0,0,-1));caption(s,v,'后壳、电池盖与 UMD 门',120)
v=s.view_fit('RightSide',ext,(226,37,146,62),(1,0,0),(0,0,1));d.dimension_box(s,v,body,'y',214,True);d.dimension_box(s,v,main,'y',385);caption(s,v,'主体与含按键厚度',120)
v=s.view_fit('TopInterfaces',ext,(18,144,175,41),(0,1,0),(0,0,1));caption(s,v,'顶边 · 红外 / USB / OPEN',202)
v=s.view_fit('BottomInterfaces',ext,(215,144,167,41),(0,-1,0),(0,0,1));caption(s,v,'底边 · 耳机与 DC 输入',202);s.save()

s=d.Sheet(3,'宽屏与主操作件尺寸',['4.3 英寸 16:9 显示窗口换算为约 95.19 × 53.55 mm。','LCD 层厚、模拟滑杆和按钮尺寸由本模型直接测量，属于近似局部尺寸。'])
v=s.view_fit('DisplayWindow',d.keys_for(['Display']),(24,28,217,128),(0,0,1));d.dimension_box(s,v,['DisplayGlass'],'x',17);d.dimension_box(s,v,['DisplayGlass'],'y',17);caption(s,v,'宽屏显示组件',177)
v=s.view_fit('AnalogNub',starts('Analog'),(281,27,83,70),(0,0,1));d.dimension_box(s,v,['AnalogCap'],'x',16);caption(s,v,'单模拟滑杆',113)
v=s.view_fit('FaceButtons',starts('Button'),(276,141,96,50),(0,0,1));d.dimension_box(s,v,['ButtonCircle'],'x',134);caption(s,v,'几何符号面按键',207);s.save()

s=d.Sheet(4,'插槽、插孔与侧面控制详图',['Mini-USB、记忆棒、遥控耳机和 DC 输入均为分离组件。','各接口的孔位、插舌和触点尺寸为示意，放大图由对应实体生成。'])
v=s.view_fit('MiniUSBDetail',starts('MiniUSB','USBContact','USBMount'),(16,25,108,57),(0,1,0),(0,0,1));d.dimension_box(s,v,['MiniUSBShell'],'x',15);caption(s,v,'Mini-USB · 五触点',101)
v=s.view_fit('DCDetail',starts('Charge','DockContact'),(156,28,85,54),(0,-1,0),(0,0,1));caption(s,v,'DC 插孔与充电触点',101)
v=s.view_fit('MemoryReaderDetail',starts('MemoryReader','MemoryContact'),(279,25,102,57),(-1,-.2,.4),(0,0,1));caption(s,v,'记忆棒卡座 · 十触点',101)
v=s.view_fit('HeadsetDetail',['HeadphoneSocket','HeadsetRemotePort']+starts('RemoteContact'),(17,132,107,57),(0,-1,0),(0,0,1));caption(s,v,'耳机 / 遥控接口',207)
v=s.view_fit('TopControls',['IRWindow','UMDOpenSlider'],(153,135,94,54),(0,1,0),(0,0,1));caption(s,v,'红外窗与 OPEN 拨钮',207)
v=s.view_fit('CurvedSide',['PowerHoldSlider','PowerBoard'],(282,132,93,57),(1,-.25,.5),(0,0,1));caption(s,v,'曲面电源 / HOLD 控制',207);s.save()

s=d.Sheet(5,'整机与子装配真实剖面',['剖面由 BRep 与指定平面求交得到，浅色区域为实际截面。','上层 TFT、主板与后部 UMD 驱动机构采用不同装配层。'])
s.text(198,17,'A-A · 主机 Y=0 横剖面',4,'middle');v=d.section_view(s,'MainSection',main,(12,32,372,59));caption(s,v,'电池、UMD、主板与显示层',105)
s.text(99,130,'B-B · TFT 中心剖面',4,'middle');v=d.section_view(s,'DisplaySection',d.keys_for(['Display']),(20,147,164,33),offset=3.5);d.dimension_box(s,v,d.keys_for(['Display']),'y',17);caption(s,v,'LCD 层叠',201)
s.text(298,130,'C-C · 光头 X=16 纵剖面',4,'middle');v=d.section_view(s,'DriveSection',d.keys_for(['UMD']),(216,146,162,37),(1,0,0),(0,0,1),16);caption(s,v,'UMD 光头所在截面',201);s.save()

s=d.Sheet(6,'整机分层爆炸总览',['外壳、显示、控制件和电子模块按装配层展开。','UMD 子装配单独移开便于观察，所有展示位移均保存于原生爆炸文件和网页节点。'])
v=s.view_fit('ExplodedAssembly',main,(12,19,372,172),(1.7,-.2,-1),exploded=True);caption(s,v,'完整主机 · 展示偏移',207);s.save()

s=d.Sheet(7,'主板、无线与电池组件',['主板含控制侧臂，CPU、媒体引擎及存储器采用独立封装实体。','PSP-110 电池按官方 1800 mAh 标识，壳体和电芯尺寸为近似值。'])
v=s.view_fit('MainboardDetail',d.keys_for(['Mainboard']),(17,26,225,119),(0,0,1));d.dimension_box(s,v,['Mainboard'],'x',16);caption(s,v,'主板与子板',160)
v=s.view_fit('BatteryDetail',d.keys_for(['Battery']),(288,29,73,118),(0,0,-1));d.dimension_box(s,v,['BatteryPouch'],'x',17);d.dimension_box(s,v,['BatteryPouch'],'y',386);caption(s,v,'电池组件',160)
s.text(14,185,'独立模块：CPU / ME / RAM / Flash / 电源 / 音频 / 无线 / 记忆棒。');s.text(14,199,'仅表示模块和装配关系，不包含真实电路、走线或制造公差。');s.save()

s=d.Sheet(8,'光驱机构与 UMD 子装配爆炸',['光驱包含打孔底盘、主轴、导杆、丝杆、光头载架和进给机构。','驱动机构尺寸及传动关系为近似研究模型；镜头和柔性电路分别建模。'])
uk=d.keys_for(['UMD']);inside=[k for k in uk if k not in ['UMDDoor','UMDLogoRing','UMDPSPMark','UMDLabel']]
v=s.view_fit('DriveMechanism',inside,(18,25,162,123),(0,0,-1));caption(s,v,'光盘读取侧',155)
v=s.view_fit('DriveExploded',uk,(207,22,174,126),(1.7,-.2,-1),exploded=True);caption(s,v,'UMD 子装配',155)
legend(s,[('UMDChassis','打孔底盘'),('SpindleMotor','主轴电机'),('PickupCarrier','光头载架'),('PickupLens','光学镜头'),('SledMotor','进给电机'),('UMDDoor','后舱门')],176);s.save()

s=d.Sheet(9,'控制机构与系统键板',['模拟滑杆的传动轴、轴承和传感器分别保留。','四向键共用载板、导电接点、胶垫和系统键开关均可在原生模型中单独查看。'])
v=s.view_fit('AnalogMechanism',starts('Analog'),(18,23,157,89),(.6,-.4,1));caption(s,v,'单模拟滑杆机构',126)
v=s.view_fit('DPadMechanism',starts('DPad')+['Control'+prefix+str(i) for prefix in ['Contact','Pill','Rubber','Boss'] for i in range(4)],(219,23,154,89),(.6,-.4,1));caption(s,v,'四向键与接点',126)
v=s.view_fit('MenuMechanism',starts('Menu'),(22,146,350,38),(0,-1,1));caption(s,v,'七枚系统按键的支承与开关',201);s.save()

s=d.Sheet(10,'可拆介质：UMD 与记忆棒',['空白 UMD 卡壳参考官方 65 × 64 × 4.2 mm，光盘直径 60 mm。','记忆棒外形、触点和介质局部开口为近似示意，不复制游戏封面或内容。'])
uk=['UMDCartridge','UMDDisc','UMDDiscHub','UMDStudyMark']
v=s.view_fit('UMDMedia',uk,(29,28,155,129),(0,0,-1));d.dimension_box(s,v,['UMDCartridge'],'x',17,True);d.dimension_box(s,v,['UMDCartridge'],'y',18,True);caption(s,v,'UMD 读取侧',171)
v=s.view_fit('UMDSide',uk,(31,184,146,14),(1,0,0),(0,0,1));d.dimension_box(s,v,['UMDCartridge'],'y',20,True)
mk=['MemoryStickCard','MemoryCardMark']+starts('MemoryCardPad')
v=s.view_fit('MemoryMedia',mk,(257,32,105,83),(0,0,1));d.dimension_box(s,v,['MemoryStickCard'],'x',19);d.dimension_box(s,v,['MemoryStickCard'],'y',383);caption(s,v,'记忆棒示意',128)
v=s.view_fit('OpticalDisc',['UMDDisc'],(277,149,57,44),(0,0,1));d.dimension_box(s,v,['UMDDisc'],'x',142,True,label='Ø 60');caption(s,v,'独立光盘',207);s.save()

s=d.Sheet(11,'零件与材料索引',['组件编号贯穿原生文件、爆炸装配、STEP 来源清单和网页节点。','文字字形等多实体对象作为一个组件记录，组件数和实体数分别统计。'])
names={'Body':'机身外壳','Display':'显示组件','Controls':'操作件','Ports':'接口与指示灯','Internal':'内部机构','Battery':'电池','Mainboard':'主板与子板','UMD':'UMD 光驱','Accessories':'可拆介质'}
for x,t in [(12,'装配分组'),(113,'组件数'),(160,'材质显示角色'),(282,'起止编号（非连续）')]:s.text(x,19,t,4,fill='#1B365D')
s.line((12,25),(384,25))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=39+i*16
 s.text(12,y,names[name]);s.text(124,y,count,anchor='middle');s.text(160,y,' / '.join(sorted(set(r['material'] for r in rows))[:3]),3.1);s.text(282,y,rows[0]['part_number']+' … '+rows[-1]['part_number']);s.line((12,y+5),(384,y+5))
s.text(12,203,f"合计 {M['physical_components']} 个组件 / {M['solids']} 个实体；完整清单见 COMPONENTS.csv",3.6,fill='#1B365D');s.save()

s=d.Sheet(12,'尺寸来源与验证记录',['索尼公开的主体口径与局部近似值分开记录。','图纸是当前 CAD 版本的快照；改模后需要重新投影、导出并检查。'])
sections=[(16,'公开尺寸依据',['索尼 2004 年产品规格及 PSP-1000 原始说明书。','主体 170 × 74 × 23 mm，明确不含最大突出部位。','4.3 英寸 16:9 TFT；UMD 卡壳 65 × 64 × 4.2 mm，光盘 Ø60。']), (67,'结构与版本依据',['PSP-1000 说明书第 20–23 页：初代控制件与接口。','iFixit 社区实机拆解用于模块划分与相对布局参考。','曲面、孔位、排线、封装和光驱传动细节为近似值。']), (118,'检查证据',[f"{M['design_iterations']} 轮建模；{M['physical_components']} 个组件独立源码重建匹配。",'原生整机、爆炸文件和三份 STEP 回读检查通过。','最终求交、直接尺寸与原生图纸检查记录见 reports/。']), (169,'维护入口',['来源：references/SOURCES.md；零件表：COMPONENTS.csv。','逐轮入口：scripts/iterNN_*.py；共享实现：tools/cadlib/psp.py。','网页网格来自同一原生组件，精确实体以 FCStd / STEP 为准。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
