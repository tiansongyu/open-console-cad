"""Build twelve A3 vector sheets from the verified original DS BReps."""
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

s=d.Sheet(1,'Nintendo DS 展开总装',['NTR-001 初代；此页为 150° 展示开角。','闭合公开尺寸单独标在第 2 页，打开状态与内部细节为本模型几何。'])
v=s.view_fit('OpenFront',ext,(15,18,169,176),(0,0,1));d.dimension_box(s,v,main,'x',12,True);caption(s,v,'展开正视',207)
v=s.view_fit('OpenIsometric',ext,(207,18,179,176),(-.6,-.7,2.4));caption(s,v,'展开轴测',207);s.save()

s=d.Sheet(2,'闭合外形与接口位置',['闭合包络由官方 148.7 × 84.7 × 28.9 mm 建立。','闭合原生文件保留同一组组件与铰链轴，局部孔位和圆角为近似值。'])
v=s.view('ClosedTop',ext,109,62,1.05,center=(0,0,14.45),source='closed');d.dimension_box(s,v,main,'x',10,True);d.dimension_box(s,v,main,'y',18,True);caption(s,v,'闭合上视',112)
v=s.view('ClosedBottom',ext,302,62,1.05,normal=(0,0,-1),center=(0,0,14.45),source='closed');caption(s,v,'闭合底视',116)
v=s.view('ClosedRight',ext,110,163,1.0,normal=(1,0,0),up=(0,0,1),center=(0,0,14.45),source='closed');d.dimension_box(s,v,main,'y',55,True);caption(s,v,'右视',189)
v=s.view('ClosedRear',ext,302,163,1.05,normal=(0,1,0),up=(0,0,1),center=(0,0,14.45),source='closed');caption(s,v,'后侧接口',189);s.save()

s=d.Sheet(3,'上下显示组件尺寸',['两块显示窗口均为 60.96 × 45.72 mm，由 3 英寸 4:3 对角线换算。','官方规格标明双 3 英寸屏幕；显示区为几何换算，LCD 外壳和层厚为近似值。'])
uk=d.keys_for(['LidDisplay']);lk=d.keys_for(['Display'])
v=s.view_fit('UpperDisplay',uk,(22,23,158,99),normal,up);d.dimension_box(s,v,['UpperGlass'],'x',15);d.dimension_box(s,v,['UpperGlass'],'y',19);caption(s,v,'上屏窗口',137)
v=s.view_fit('LowerDisplay',lk,(225,23,152,99),(0,0,1));d.dimension_box(s,v,['LowerGlass'],'x',15);d.dimension_box(s,v,['LowerGlass'],'y',391);caption(s,v,'下屏触控窗口',137)
v=s.view_fit('UpperDisplaySide',uk,(24,156,155,24),up,normal);caption(s,v,'上屏层叠侧视',198)
v=s.view_fit('LowerDisplaySide',lk,(225,156,151,24),(0,1,0),(0,0,1));caption(s,v,'下屏层叠侧视',198);s.save()

s=d.Sheet(4,'初代按键与双卡槽详图',['十字键、ABXY 与电源/系统键采用分离键帽、胶垫和触点。','Slot-1 / Slot-2、专用 AC 插孔和耳机接口均由实际 BRep 投影。'])
v=s.view_fit('DPadDetail',['DPad']+[k for k in C if k.startswith('DPadTick')],(18,20,91,69),(0,0,1));d.dimension_box(s,v,['DPad'],'x',13);caption(s,v,'十字键',104)
v=s.view_fit('ChargeDetail',['ChargeJackShell','ChargeJackTongue','ChargePin0','ChargePin1'],(155,28,79,48),(0,1,0),(0,0,1));d.dimension_box(s,v,['ChargeJackShell'],'x',17);caption(s,v,'AC 充电插孔',104)
v=s.view_fit('HeadphoneDetail',['HeadphoneSocket','HeadsetPort','HeadsetPin0','HeadsetPin1'],(279,25,98,56),(0,-1,0),(0,0,1));caption(s,v,'耳机 / 附件口',104)
v=s.view_fit('SlotOne',[k for k in C if k.startswith(('GameCard','CardContact'))],(14,133,112,52),(0,1,0),(0,0,1));d.dimension_box(s,v,['GameCardMouth'],'x',121);caption(s,v,'DS Slot-1',207)
v=s.view_fit('SlotTwo',[k for k in C if k.startswith('GBA')],(145,139,111,47),(0,-1,0),(0,0,1));d.dimension_box(s,v,['GBAMouth'],'x',125);caption(s,v,'GBA Slot-2 · 32 触点',207)
v=s.view_fit('SpeakerDetail',['SpeakerFrame-1','SpeakerMagnet-1','SpeakerDiaphragm-1','SpeakerGasket-1'],(284,129,83,59),normal,up);caption(s,v,'单侧扬声器',207);s.save()

s=d.Sheet(5,'下机身与上盖真实剖面',['浅色区域由 BRep 与指定平面相交得到，不使用外观轮廓代替剖面。','上盖剖切平面随展示姿态旋转；局部厚度与安装间隙为近似设计。'])
s.text(198,15,'A-A · 下机身 Y=0 横剖面',4,'middle')
v=d.section_view(s,'LowerSection',lower,(12,27,372,50));caption(s,v,'下机身结构层',88)
pivot=App.Vector(*M['pose']['pivot_mm']);transform=App.Placement(App.Vector(),rot,pivot);n=rot.multVec(App.Vector(0,1,0));u=rot.multVec(App.Vector(0,0,1));point=transform.multVec(App.Vector(0,84,0));offset=n.dot(point)
s.text(198,121,'B-B · 上盖显示中心横剖面',4,'middle')
v=d.section_view(s,'UpperSection',upper,(12,133,372,49),tuple(n),tuple(u),offset);caption(s,v,'上盖、LCD 与显示窗口',204);s.save()

s=d.Sheet(6,'整机分层爆炸总览',['上下机身按原装配层展开；偏移仅用于分辨组件。','完整编号对应模型树及 COMPONENTS.csv，后续两页分别展开上下组件。'])
v=s.view_fit('CompleteExploded',main,(12,13,372,175),(1.7,-.2,-1),exploded=True);caption(s,v,'全部主机组件',207);s.save()

s=d.Sheet(7,'下机身内部与爆炸结构',['电池、主板、显示层、控制件和后盖分别展示。','电池位置及模块划分参考实机拆解，PCB 和封装尺寸为布局示意。'])
v=s.view_fit('LowerExploded',lower,(10,15,376,126),(1.7,-.2,-1),exploded=True)
legend(s,[('FrontDeck','控制面板'),('LowerGlass','下屏窗口'),('LowerLCD','下 LCD'),('Mainboard','主板'),('BatteryPouch','NTR-003 电池'),('BackCover','可拆后盖')],163);s.save()

s=d.Sheet(8,'上盖显示与扬声器爆炸',['上盖包含 3 英寸 LCD、显示窗口、双扬声器、排线与天线。','卷绕排线在铰链中预留通道，展示姿态可由原生参数和宏重现。'])
v=s.view_fit('UpperExploded',upper,(10,15,376,126),(1.7,-.2,-1),exploded=True)
legend(s,[('LidBezel','银色上盖面板'),('UpperGlass','上屏窗口'),('UpperLCD','上 LCD'),('UpperLCDFlex','上屏排线'),('SpeakerFrame-1','扬声器'),('LidBackCover','上盖外壳')],163);s.save()

s=d.Sheet(9,'主板与电池组件',['ARM9、ARM7、RAM 和 Wi-Fi 子板均为独立实体。','NTR-003 电池按 850 mAh 标识，内部电芯形态为示意。'])
v=s.view_fit('MotherboardDetail',d.keys_for(['Mainboard']),(20,22,225,118),(0,0,1));d.dimension_box(s,v,['Mainboard'],'x',13);caption(s,v,'主板与子板正视',153)
v=s.view_fit('BatteryDetail',d.keys_for(['Battery']),(285,25,82,113),(0,0,-1));d.dimension_box(s,v,['BatteryPouch'],'x',14);d.dimension_box(s,v,['BatteryPouch'],'y',390);caption(s,v,'电池与端子',153)
s.text(12,178,'ARM9 / ARM7 / RAM / 电源与音频封装：近似布局');s.text(12,190,'独立 Wi-Fi 射频小板；DS 与 GBA 接口见第 4 页');s.text(12,202,'不包含真实电路、布线、料号精度或制造公差。');s.save()

s=d.Sheet(10,'触控笔与独立电池仓结构',['初代触控笔为固定长度，笔尖、笔杆和卡扣帽分别建模。','电池仓拥有独立盖板及一枚固定螺钉，组件尺寸为本模型近似值。'])
sk=d.keys_for(['Accessories'])
v=s.view_fit('Stylus',sk,(24,24,47,151),(0,0,1));d.dimension_box(s,v,sk,'y',90);caption(s,v,'75 mm 触控笔',202)
v=s.view_fit('StylusTip',['StylusTip','StylusBarrel'],(112,26,51,131),(.8,0,1));caption(s,v,'笔杆与锥形尖端',185)
v=s.view_fit('BatteryDoor',['BatteryDoor','BatteryDoorScrew'],(238,26,98,145),(0,0,-1));d.dimension_box(s,v,['BatteryDoor'],'x',17);d.dimension_box(s,v,['BatteryDoor'],'y',367);caption(s,v,'独立电池仓盖',202);s.save()

s=d.Sheet(11,'组件与材料索引',['组件编号贯穿原生文件、爆炸装配与零件清单。','文字字形等多实体对象作为一个组件记录，组件数与实体数分别统计。'])
names={'Body':'下机身外壳','Lid':'上盖外壳','Hinge':'铰链','Display':'下显示组件','LidDisplay':'上显示组件','Controls':'控制件','Ports':'插槽与接口','LidInternal':'上盖内部','Internal':'下机身内部','Accessories':'触控笔','Battery':'电池','Mainboard':'主板与子板'}
for x,t in [(12,'装配分组'),(115,'组件数'),(164,'材质显示角色'),(282,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,22),(384,22))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=34+i*11.3
 s.text(12,y,names.get(name,name));s.text(126,y,count,anchor='middle');s.text(164,y,' / '.join(sorted(set(r['material'] for r in rows))[:3]),3.1);s.text(282,y,rows[0]['part_number']+' … '+rows[-1]['part_number']);s.line((12,y+4),(384,y+4))
s.text(12,203,f"合计 {M['physical_components']} 个组件 / {M['solids']} 个实体；完整清单见 COMPONENTS.csv",3.6,fill='#1B365D');s.save()

s=d.Sheet(12,'尺寸依据与验证索引',['官方闭合尺寸与本模型局部近似尺寸分别记录。','图纸为已保存 CAD 版本的快照，改模后需要重新生成和检查。'])
sections=[(16,'官方尺寸依据',['Nintendo DS NTR-001：闭合 148.7 × 84.7 × 28.9 mm。','双 3 英寸 4:3 屏幕换算为 60.96 × 45.72 mm。','来源：Nintendo 日本官网初代 DS 产品规格页。']), (67,'结构参考',['iFixit Nintendo DS 主板更换指南及实机照片。','局部外形、壁厚、孔位和内部模块为近似设计。','触控笔、内部厚度与 150° 开角属于展示模型参数。']), (118,'检查证据',[f"{M['design_iterations']} 轮建模；{M['physical_components']} 个组件独立源码重建匹配。",'原生展开、闭合、爆炸文件及四份 STEP 已回读检查。','最终装配实体求交、图纸尺寸和字体检查记录见 reports/。']), (169,'维护入口',['来源链接：references/SOURCES.md。','零件索引：COMPONENTS.csv；源码：scripts/iterNN_*.py。','网页网格由同一 FreeCAD 组件导出，精确实体以 FCStd / STEP 为准。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
