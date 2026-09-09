"""Twelve A3 sheets of the original DMG-01, projected from delivered BReps."""
from pathlib import Path
import os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
repo=Path(__file__).resolve().parents[3];sys.path.insert(0,str(repo/'tools'))
from cadlib import drawings as d
import FreeCAD as App,Part

d.init_drawing(Path(__file__).resolve().parents[1]);C=d.C;M=d.M
main=d.keys_for(d.HH)
ext=d.keys_for(['Body','Controls','Ports','Display'],False)+['CaseScrew'+str(i) for i in range(6)]+['CartridgeWellBacker','CartridgeLeftGuide','CartridgeRightGuide','CartridgePowerLock','SpeakerMesh']
def starts(*prefixes):return [k for k in C if k.startswith(prefixes)]
def caption(s,v,text,y):s.text(v['x'],y,text+f" · {v['scale']:.3f}:1",anchor='middle')
def legend(s,items,y=177):
 for i,(key,label) in enumerate(items):
  x=12+(i%3)*127;yy=y+(i//3)*18
  s.text(x,yy,C[key].PartNumber,3.1,fill='#1B365D');s.text(x,yy+6,label,3.1)

s=d.Sheet(1,'初代 Game Boy 正面与立体总装',['DMG-01 灰色初代外观，保留单色屏幕、十字键与酒红色 A/B 按键。','按任天堂公开的 90 × 148 × 32 mm 包络建模，局部形状和内部结构为近似值。'])
v=s.view_fit('IsometricAssembly',ext,(18,25,156,160),(-.6,-.7,2.4));caption(s,v,'外壳、单色屏幕与操作件',202)
v=s.view_fit('FrontAssembly',ext,(218,25,153,160),(0,0,1));d.dimension_box(s,v,main,'x',15,True);d.dimension_box(s,v,main,'y',204,True);caption(s,v,'正面包络',202);s.save()

s=d.Sheet(2,'后壳、电池盖与侧面接口',['背面保留卡带凹口、横向握持纹、电池盖和三角槽机壳螺钉。','侧面为对比度与音量滚轮、通信口和 DC 插孔，底部为耳机口。'])
v=s.view_fit('RearAssembly',ext,(20,25,146,135),(0,0,-1));caption(s,v,'后部卡槽与可拆电池盖',170)
v=s.view_fit('RightSide',ext,(206,26,60,135),(1,0,0));d.dimension_box(s,v,main,'x',16,True);caption(s,v,'含控制件厚度 32 mm',171)
v=s.view_fit('LeftSide',ext,(304,26,60,135),(-1,0,0));caption(s,v,'另一侧滚轮与供电接口',171)
v=s.view_fit('TopEdge',ext,(22,182,141,23),(0,1,0),(0,0,1));caption(s,v,'顶部电源滑块',212)
v=s.view_fit('BottomEdge',ext,(233,182,139,23),(0,-1,0),(0,0,1));caption(s,v,'底部耳机接口',212);s.save()

s=d.Sheet(3,'单色显示层与原始 LCD 固定结构',['显示窗口为 47 × 43 mm，原机采用非背光单色 LCD。','边框、背板、偏光层、支承卡框和焊接排线保持独立，便于观察层叠关系。'])
v=s.view_fit('DisplayFront',d.keys_for(['Display']),(23,29,175,121),(0,0,1));d.dimension_box(s,v,['DisplayGlass'],'x',18);d.dimension_box(s,v,['DisplayGlass'],'y',14);caption(s,v,'显示区与边框',163)
v=s.view_fit('DisplayExploded',d.keys_for(['Display'])+['LCDDisplayFlex'],(224,27,155,128),(1.7,-.2,-1),exploded=True);caption(s,v,'显示装配层',163)
legend(s,[('DisplayGlass','显示窗口'),('LCD','单色 LCD 模组'),('LCDPolarizer','偏光层示意'),('LCDBackplate','金属背板'),('LCDSupportFrame','固定卡框'),('LCDDisplayFlex','焊接式柔性连接')],181);s.save()

s=d.Sheet(4,'按键胶垫、导电接点与传动件',['十字键和 A/B 键分别使用连体硅胶垫，导电粒与 PCB 接点保持独立。','START/SELECT 胶键按原机的倾斜方向布置，传动柱从按键延伸到电路板。'])
dpad=starts('DPad')+['Key'+part+str(i) for part in ['Contact','Pill','Boss'] for i in range(4)]
action=starts('Button')+['ActionMembrane']+['Key'+part+str(i) for part in ['Contact','Pill','Boss'] for i in [4,5]]
v=s.view_fit('DPadTop',dpad,(23,27,148,77),(0,0,1));d.dimension_box(s,v,['DPad'],'x',17);caption(s,v,'十字键与下方传动件',119)
v=s.view_fit('ActionTop',action,(221,27,151,77),(0,0,1));d.dimension_box(s,v,['ButtonA'],'x',17);caption(s,v,'A/B 按键组件',119)
v=d.section_view(s,'DPadSection',dpad,(24,155,146,35),offset=-26);caption(s,v,'A-A · Y=-26 实体剖面',207)
v=s.view_fit('SystemButtons',[k for k in starts('System','Start','Select') if not k.endswith('Mark')],(232,153,139,41),(.6,-.5,1.8));caption(s,v,'START / SELECT 机构',207);s.save()

s=d.Sheet(5,'真实横剖面与装配层叠',['两个截面由实际 BRep 与指定平面相交得到，浅色区域为实体截面。','上部展示显示与主板层，下部展示四节 AA 电池、电池仓和前电路板。'])
s.text(198,17,'A-A · Y=35.8 屏幕与主板横剖面',4,'middle');v=d.section_view(s,'UpperSection',main,(18,31,360,57),offset=35.8);caption(s,v,'显示层、主板与卡带导向结构',106)
s.text(198,132,'B-B · Y=-40 电池仓横剖面',4,'middle');v=d.section_view(s,'BatterySection',main,(18,144,360,51),offset=-40);caption(s,v,'四节电池、隔条与前壳电路板',209);s.save()

s=d.Sheet(6,'整机分层爆炸总览',['外壳、显示、前后电路板、输入机构和电池从同一组件集合展开。','爆炸偏移用于展示装配关系，组件编号与偏移同时保存在原生文件和网页中。'])
v=s.view_fit('FullExploded',main,(12,18,372,173),(1.7,-.2,-1),exploded=True);caption(s,v,'完整主机爆炸装配',207);s.save()

s=d.Sheet(7,'主逻辑板与电源、耳机小板',['主板参考 DMG-01 拆机中的一块具体修订版，不代表所有生产批次完全相同。','CPU、两块 RAM、音频放大器、晶振、无源件与铜箔屏蔽分别建模。'])
v=s.view_fit('MainboardRear',d.keys_for(['Mainboard']),(23,25,175,139),(0,0,-1));d.dimension_box(s,v,['Mainboard'],'x',16);d.dimension_box(s,v,['Mainboard'],'y',14);caption(s,v,'主板元件面',178)
v=s.view_fit('PowerDaughterboard',d.keys_for(['Power']),(230,29,59,122),(1,0,0));caption(s,v,'侧立电源小板',169)
v=s.view_fit('HeadphoneDaughterboard',starts('Headphone'),(313,51,64,90),(.5,-.7,1.5));caption(s,v,'耳机小板与插孔',169)
s.text(14,201,'封装尺寸、引脚形状与走线用于解释布局，不定义实际电气连接或制造公差。');s.save()

s=d.Sheet(8,'四节 AA 电池与可拆电池仓',['保留原机四节 AA 供电形式，电芯、外套、极柱、接触簧和隔条分别建模。','电池图形使用通用学习标识，端子与安装间隙为本模型近似值。'])
v=s.view_fit('BatteryPack',d.keys_for(['Battery']),(23,27,187,125),(0,0,-1));d.dimension_box(s,v,['BatteryTray'],'x',17);caption(s,v,'四节电池与托盘',169)
cell=['AAWrapper0','AACell0','AANegative0','AAPositive0']
v=s.view_fit('SingleAA',cell+['AAContactSpring0','AAContactLeaf0'],(265,26,95,132),(1,0,0));d.dimension_box(s,v,cell,'x',17);d.dimension_box(s,v,cell,'y',383);caption(s,v,'单节电池与触点',176)
legend(s,[('BatteryTray','电池仓'),('AAWrapper0','通用电池外套'),('AAContactSpring0','螺旋接触簧')],190);s.save()

s=d.Sheet(9,'通信、滚轮与音频部件',['侧面通信口为初代大尺寸 Game Link，电源口与耳机口保持独立。','滚轮具有齿纹、轴和电位器，扬声器保留金属框、磁体与振膜。'])
v=s.view_fit('LinkConnector',starts('LinkPort','LinkPin'),(18,29,112,62),(1,0,0),(0,0,1));caption(s,v,'六接点通信接口',112)
v=s.view_fit('ContrastWheel',starts('Contrast'),(154,29,94,62),(.6,-.5,1.8));caption(s,v,'对比度滚轮与轴',112)
v=s.view_fit('VolumeWheel',starts('Volume'),(279,29,94,62),(-.6,-.5,1.8));caption(s,v,'音量滚轮与轴',112)
v=s.view_fit('SpeakerDetail',[k for k in starts('Speaker') if k!='SpeakerMesh' and 'Wire' not in k],(24,143,103,51),(.7,-.6,1.5));caption(s,v,'扬声器框与振膜（移除防尘网）',209)
v=s.view_fit('DCJackDetail',starts('DCJack'),(155,145,90,49),(-1,.3,.5));caption(s,v,'DC 供电插孔',209)
v=s.view_fit('HeadphoneJackDetail',starts('HeadphoneJack'),(282,145,90,49),(.3,-1,.5));caption(s,v,'耳机插孔',209);s.save()

s=d.Sheet(10,'空白 Game Pak 卡带与连接器',['独立卡带包含分壳、PCB、32 接点、ROM 封装示意、标签和背部螺钉。','本项目不包含游戏 ROM 或授权游戏封面，卡带尺寸为近似学习值。'])
cart=d.keys_for(['Accessories'])
v=s.view_fit('CartridgeFront',cart,(22,28,116,129),(0,0,1));d.dimension_box(s,v,['CartridgeFront'],'x',17);d.dimension_box(s,v,['CartridgeFront'],'y',14);caption(s,v,'卡带正面',174)
v=s.view_fit('CartridgeBack',cart,(159,29,101,127),(0,0,-1));caption(s,v,'接点与后壳',174)
v=s.view_fit('CartridgeExploded',cart,(289,27,88,132),(1.7,-.2,-1),exploded=True);caption(s,v,'卡带装配层',174)
s.text(14,198,'编号对应 COMPONENTS.csv；主机文件与卡带附件在不同装配分组中保存。');s.save()

s=d.Sheet(11,'组件、材料与装配索引',['组件编号用于关联原生工程、STEP、网页节点与零件清单。','芯片引脚组和文字可能含多个实体，实体数与组件条目数分别统计。'])
names={'Body':'机壳与标记','Display':'单色显示组件','Controls':'外部操作件','ControlsInternal':'前板与输入机构','Audio':'音频组件','Mainboard':'主逻辑板与封装','Ports':'接口','CardReader':'卡带导向与连接器','Internal':'安装与支承','Battery':'四节 AA 与电池仓','Power':'电源小板','Flex':'互连导线','Accessories':'空白卡带'}
for x,t in [(12,'装配分组'),(111,'条目'),(156,'材质显示角色'),(272,'起止编号（非连续）')]:s.text(x,17,t,4,fill='#1B365D')
s.line((12,23),(384,23))
for i,(name,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==name];y=35+i*12.1
 s.text(12,y,names[name]);s.text(120,y,count,anchor='middle');s.text(156,y,' / '.join(sorted(set(r['material'] for r in rows))[:3]),2.9);s.text(272,y,rows[0]['part_number']+' … '+rows[-1]['part_number'],2.9);s.line((12,y+4),(384,y+4))
s.text(12,207,f"合计 {M['physical_components']} 个组件条目 / {M['solids']} 个实体；详见 COMPONENTS.csv",3.5,fill='#1B365D');s.save()

s=d.Sheet(12,'版本、尺寸来源与验证范围',['采用 DMG-01 初代灰色外观，原始单色屏幕和四节 AA 供电形式。','图纸为当前 CAD 几何的版本快照，修改模型后需重新生成和核对。'])
sections=[(16,'公开规格',['任天堂 Game Boy Classic：90 × 148 × 32 mm 完整包络。','单色 LCD 显示区 47 × 43 mm；160 × 144 像素。','四节 AA 电池、对比度/音量调节、通信口与立体声耳机。']), (67,'参考与近似范围',['任天堂技术数据页与 iFixit DMG-01 拆机（指南 122657）。','主板采用所参考修订版的布局，不代表每一批次的细节。','壁厚、封装、接点、卡带和安装间隙为近似研究几何。']), (118,'验证记录',[f"{M['design_iterations']} 轮源码；{M['physical_components']} 个组件条目参与重建核对。",'原生装配、STEP 回读、组件相交和直接尺寸分别检查。','图册使用 Kami，包含字体、内容覆盖与逐页视觉检查。']), (169,'维护入口',['来源：references/SOURCES.md；零件清单：COMPONENTS.csv。','逐轮入口：scripts/iterNN_*.py；实现：tools/cadlib/gameboy.py。','网页 GLB 与原生 CAD 的身份关联见输出与网页模型清单。'])]
for y,title,lines in sections:
 s.text(12,y,title,4,fill='#1B365D')
 for i,line in enumerate(lines):s.text(12,y+11+i*8,line,3.2)
s.save();d.finish_drawing()
