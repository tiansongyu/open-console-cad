"""Twelve PCH-1000 Wi-Fi OLED A3 sheets from the delivered component BReps."""
from pathlib import Path
import os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
repo=Path(__file__).resolve().parents[3];sys.path.insert(0,str(repo/'tools'))
from cadlib import drawings as d
import FreeCAD as App,Part

d.init_drawing(Path(__file__).resolve().parents[1]);C=d.C;M=d.M
main=d.keys_for(d.HH);ext=d.keys_for(d.HH,False)+['StickStem-1','StickStem1'];body=d.keys_for(M['envelope_groups'])
def caption(s,v,text,y):s.text(v['x'],y,text+f" · {v['scale']:.3f}:1",anchor='middle')
def starts(*p):return [k for k in C if k.startswith(p)]
def legend(s,items,y=174):
 for i,(key,label) in enumerate(items):
  x=12+(i%3)*127;yy=y+(i//3)*18
  s.text(x,yy,C[key].PartNumber,3.1,fill='#1B365D');s.text(x,yy+6,label,3.1)
right_stick=[k for k in starts('Stick') if '-1' not in k]

s=d.Sheet(1,'PS Vita 初代正面总装',['PCH-1000 Wi-Fi OLED，保留双模拟摇杆、独立按键区和前摄像头。','主体公开尺寸不包含最大突出部位；局部尺寸和内部模块为近似研究模型。'])
v=s.view_fit('FrontAssembly',ext,(22,25,350,150),(0,0,1));d.dimension_box(s,v,body,'x',15,True);d.dimension_box(s,v,body,'y',12,True);caption(s,v,'正面总装 · 主体 182 × 83.5 mm',198);s.save()

s=d.Sheet(2,'后部触控、侧面与接口位置',['后部保留椭圆握持垫、触控区域和独立后摄像头。','侧视图左侧标注主体 18.6 mm，右侧为当前模型含摇杆的厚度。'])
v=s.view_fit('RearAssembly',ext,(18,26,177,89),(0,0,-1));caption(s,v,'后触控板与椭圆握持垫',125)
v=s.view_fit('RightSide',ext,(225,38,147,60),(1,0,0),(0,0,1));d.dimension_box(s,v,body,'y',214,True);d.dimension_box(s,v,main,'y',386);caption(s,v,'主体与含摇杆厚度',125)
v=s.view_fit('TopPorts',ext,(18,146,175,39),(0,1,0),(0,0,1));caption(s,v,'顶部控制键与双槽盖',202)
v=s.view_fit('BottomPorts',ext,(215,146,168,39),(0,-1,0),(0,0,1));caption(s,v,'底部专用接口与耳机孔',202);s.save()

s=d.Sheet(3,'五英寸 OLED 与摇杆窗口尺寸',['5 英寸 16:9 显示窗口换算为约 110.69 × 62.26 mm。','双摇杆的凹面帽、轴承和防尘裙分别建模，局部尺寸由实体测量。'])
v=s.view_fit('OLEDWindow',d.keys_for(['Display']),(25,27,215,129),(0,0,1));d.dimension_box(s,v,['DisplayGlass'],'x',17);d.dimension_box(s,v,['DisplayGlass'],'y',17);caption(s,v,'OLED 与前电容触控层',178)
v=s.view_fit('StickDetail',right_stick,(280,28,86,70),(0,0,1));d.dimension_box(s,v,['StickCap1'],'x',16);caption(s,v,'右模拟摇杆',114)
v=s.view_fit('FaceButtons',starts('Button'),(279,140,89,51),(0,0,1));d.dimension_box(s,v,['ButtonCircle'],'x',134);caption(s,v,'几何符号面按键',207);s.save()

s=d.Sheet(4,'后触控面板与电极层爆炸',['后面板、简化符号印纹、电极层、支承片和控制器保持独立。','印纹为本模型的简化几何图案，触控电子结构仅表达模块和装配关系。'])
rk=d.keys_for(['RearTouch'])
v=s.view_fit('RearTouchFace',['RearTouchPanel','RearTouchPattern','RearSonyMark','RearModelMark'],(20,29,178,115),(0,0,-1));d.dimension_box(s,v,['RearTouchPanel'],'x',18);d.dimension_box(s,v,['RearTouchPanel'],'y',13);caption(s,v,'后触控面板',159)
v=s.view_fit('RearTouchExploded',rk,(213,26,166,120),(1.7,-.2,-1),exploded=True);caption(s,v,'触控与支承层',159)
legend(s,[('RearTouchPanel','触控表面'),('RearTouchFoil','电极层'),('RearTouchShield','金属支承片'),('RearTouchPCB','控制器小板'),('RearTouchController','触控芯片'),('RearTouchFlex','弯折连接排线')],177);s.save()

s=d.Sheet(5,'真实剖面与层叠关系',['截面来自 BRep 与指定平面相交，浅色区域为实体截面。','显示、主板、电池和后触控层保持不同高度，局部间隙为近似设计。'])
s.text(198,17,'A-A · 主机 Y=0 横剖面',4,'middle');v=d.section_view(s,'MainSection',main,(12,32,372,58));caption(s,v,'OLED、主板、电池与后触控层',104)
s.text(101,130,'B-B · 前摄像头 Y=28',4,'middle');v=d.section_view(s,'FrontCameraSection',starts('FrontCamera'),(25,145,152,38),offset=28);caption(s,v,'镜筒与传感器',202)
s.text(298,130,'C-C · 右摇杆 Y=-8.5',4,'middle');v=d.section_view(s,'StickSection',right_stick,(221,144,152,40),offset=-8.5);caption(s,v,'凹面帽、轴承与防尘裙',202);s.save()

s=d.Sheet(6,'整机分层爆炸总览',['外壳、显示、操作件、电子模块、电池和后触控结构按装配层展开。','爆炸位移仅用于展示，来源组件和偏移均保存在原生文件与网页节点中。'])
v=s.view_fit('ExplodedAssembly',main,(12,18,372,173),(1.7,-.2,-1),exploded=True);caption(s,v,'完整主机装配层',207);s.save()

s=d.Sheet(7,'无线主板与电池固定结构',['主板、处理器与存储器、Wi-Fi/Bluetooth、传感器和电源音频封装分别建模。','本项目为 Wi-Fi 型号，不包括蜂窝通信、SIM 或 GPS 模块。'])
v=s.view_fit('MainboardDetail',[k for k in d.keys_for(['Mainboard']) if k not in ['ProcessorShield','PowerShield']],(20,27,215,117),(0,0,1));d.dimension_box(s,v,['Mainboard'],'x',17);caption(s,v,'Wi-Fi 型主板',158)
v=s.view_fit('BatteryDetail',d.keys_for(['Battery']),(253,43,124,83),(0,0,-1));d.dimension_box(s,v,['BatteryPouch'],'x',26);d.dimension_box(s,v,['BatteryPouch'],'y',391);caption(s,v,'电池与两处固定耳',158)
s.text(14,184,'电池采用官方 2210 mAh / 3.7 V 标识；壳体与电芯几何为近似值。');s.text(14,199,'封装和模块布局不包含真实电路、布线、材料密度或制造公差。');s.save()

s=d.Sheet(8,'模块化操作板与传动组件',['左右操作板分离，双摇杆与按键传动结构可分别观察。','胶垫、导电粒和主板接点保持独立，卡接或压合处使用本模型的装配间隙。'])
v=s.view_fit('ControllerBoards',d.keys_for(['ControlsInternal']),(16,22,364,101),(0,0,1));caption(s,v,'左右操作板与接点',132)
v=s.view_fit('AnalogAssembly',right_stick,(23,150,141,41),(.6,-.4,1));caption(s,v,'单侧摇杆机构',207)
v=s.view_fit('DirectionalAssembly',starts('DPad')+['Key'+prefix+str(i) for prefix in ['Contact','Pill','Rubber','Boss'] for i in range(4)],(231,150,137,41),(.6,-.4,1));caption(s,v,'四向键与胶垫',207);s.save()

s=d.Sheet(9,'前后光学与音频组件',['前后摄像头分别由窗口、镜筒、传感器和 PCB 组成。','扬声器采用独立压力接点，麦克风含载板、胶囊和通向底边的导管。'])
v=s.view_fit('FrontCameraDetail',starts('FrontCamera'),(20,28,105,69),(.5,-.6,1));caption(s,v,'前摄像头',117)
v=s.view_fit('RearCameraDetail',starts('RearCamera'),(148,28,103,69),(.5,-.6,-1));caption(s,v,'后摄像头',117)
sp=[k for k in C if k.startswith('Speaker') and ('-1' in k)]
v=s.view_fit('SpeakerDetail',sp,(278,28,99,69),(.6,-.4,1));caption(s,v,'单侧扬声器与压力接点',117)
v=s.view_fit('MicrophoneDetail',starts('Microphone'),(25,146,110,42),(.6,-1,.7));caption(s,v,'麦克风与导管',207)
v=s.view_fit('RearControllerDetail',['RearTouchPCB','RearTouchController'],(170,146,97,42),(0,0,1));caption(s,v,'后触控控制器',207)
v=s.view_fit('FrontControllerDetail',['FrontTouchPackage'],(303,146,50,42),(0,0,1));caption(s,v,'前触控控制器',207);s.save()

s=d.Sheet(10,'专用接口与空白可拆介质',['底部多功能接口和卡槽按初代专用接口建模。','介质、接点与局部开口尺寸为视觉学习示意，不作为电气引脚定义。'])
v=s.view_fit('MultiPortDetail',starts('MultiPort','PortScrew'),(20,25,157,58),(0,-1,0),(0,0,1));caption(s,v,'多功能接口与固定螺钉',104)
v=s.view_fit('ReaderDetail',d.keys_for(['CardReaders']),(218,24,158,59),(.2,-.6,1));caption(s,v,'独立卡座组件',104)
v=s.view_fit('GameMedia',['VitaGameCard','VitaGameMark']+starts('VitaGamePad'),(33,132,102,68),(0,0,1));d.dimension_box(s,v,['VitaGameCard'],'x',122);d.dimension_box(s,v,['VitaGameCard'],'y',23);caption(s,v,'空白游戏卡',211)
v=s.view_fit('MemoryMedia',['VitaMemoryCard','VitaMemoryMark']+starts('VitaMemoryPad'),(260,143,82,48),(0,0,1));d.dimension_box(s,v,['VitaMemoryCard'],'x',130);d.dimension_box(s,v,['VitaMemoryCard'],'y',368);caption(s,v,'专用存储卡示意',211);s.save()

s=d.Sheet(11,'组件与材料索引',['组件编号贯穿原生模型、爆炸装配、组件清单和网页节点。','重复印纹与文字字形按一个组件记录，多实体数量与组件数量分开统计。'])
names={'Body':'机身外壳','Display':'OLED 与前触控','Controls':'操作件','Internal':'安装与支承件','Ports':'接口与盖板','Optics':'摄像头','RearTouch':'后触控组件','Battery':'电池','Mainboard':'主板与封装','ControlsInternal':'左右操作板','CardReaders':'专用卡座','Audio':'音频组件','Flex':'互连排线','Accessories':'可拆介质'}
for x,t in [(12,'装配分组'),(113,'组件数'),(160,'材质显示角色'),(282,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=34+i*11.3
 s.text(12,y,names[name]);s.text(124,y,count,anchor='middle');s.text(160,y,' / '.join(sorted(set(r['material'] for r in rows))[:3]),3.0);s.text(282,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],3.0);s.line((12,y+4),(384,y+4))
s.text(12,205,f"合计 {M['physical_components']} 个组件 / {M['solids']} 个实体；完整清单见 COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'尺寸依据与验证范围',['公开主体尺寸、显示区几何换算及局部近似值分别记录。','图纸是当前 CAD 版本的快照，改模后需重新投影和检查。'])
sections=[(16,'公开规格与版本',['Sony PCH-1000 系列：主体 182 × 83.5 × 18.6 mm。','5 英寸 16:9 OLED，前后电容触控，前后摄像头。','用户指定 Wi-Fi OLED；不包括 3G、SIM 或 GPS 硬件。']), (67,'参考与近似范围',['索尼原始产品规格及 PCH-1000/PCH-1100 快速入门指南。','iFixit 3G 型拆解仅用于共有模块和结构的照片参考。','孔位、壁厚、封装、接点、印纹和排线均为近似研究几何。']), (118,'检查记录',[f"{M['design_iterations']} 轮源码构建；{M['physical_components']} 个组件重建匹配。",'原生整机、爆炸和三份 STEP 回读，最终组件求交检查。','直接模型尺寸、原生图纸参考与字体检查记录见 reports/。']), (169,'维护入口',['来源：references/SOURCES.md；清单：COMPONENTS.csv。','逐轮入口：scripts/iterNN_*.py；实现：tools/cadlib/psv.py。','网页来自同一组 BRep，精确实体以 FCStd / STEP 为准。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
