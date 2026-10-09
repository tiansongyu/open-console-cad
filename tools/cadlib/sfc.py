"""Japanese SHVC-001 / SHVC-CPU-01 with separate original sound module."""
import math
import FreeCAD as App
import Part
from .core import V
from . import geometry as g


def _outline(w,h,r):
    x=w/2;y=h/2
    seq=[]
    corners=[(x-r,-y+r,-90),(x-r,y-r,0),(-x+r,y-r,90),(-x+r,-y+r,180)]
    for i,(cx,cy,a) in enumerate(corners):
        prev=corners[(i-1)%4];px,py,pa=prev
        start=V(px+r*math.cos(math.radians(pa+90)),py+r*math.sin(math.radians(pa+90)))
        end=V(cx+r*math.cos(math.radians(a)),cy+r*math.sin(math.radians(a)))
        seq.append(Part.LineSegment(start,end))
        pts=[V(cx+r*math.cos(math.radians(a+t)),cy+r*math.sin(math.radians(a+t))) for t in [0,45,90]]
        seq.append(Part.Arc(*pts))
    return seq


def _loft(m,key,profiles):
    sketches=[]
    for i,(w,h,r,z) in enumerate(profiles):
        sk=m.doc.addObject('Sketcher::SketchObject',key+'Profile'+str(i));sk.Label='Editable rounded SHVC-001 section '+str(i+1)
        sk.addGeometry(_outline(w,h,r),False);sk.Placement.Base=V(0,0,z);m.group('Construction').addObject(sk);sketches.append(sk)
    loft=m.doc.addObject('Part::Loft',key);loft.Sections=sketches;loft.Solid=True;loft.Ruled=True
    m.doc.recompute();loft.Shape.check(True);assert len(loft.Shape.Solids)==1
    m.group('Construction').addObject(loft)
    for sk in sketches:sk.Visibility=False
    loft.Visibility=False;return loft


def _finish(m,n,slug,summary):
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=n;m.checkpoint(n,slug,summary)


def stage01(m):
    m.colors.update(sfcgray=(.72,.73,.75),sfcface=(.44,.47,.52),sfcink=(.07,.09,.12),sfcbutton=(.24,.27,.32),sfcyellow=(.90,.66,.04),sfcgreen=(.02,.50,.25),sfcred=(.76,.04,.10),sfcblue=(.05,.25,.68))
    m.params.set('A3','Depth (Y)');m.params.set('A4','Height (Z)');m.params.set('B7','1.8 mm')
    m.native('BottomShell','Editable Japanese lower enclosure',200,242,16,27,(0,0,2),'Body',-6,'sfcgray',expr={'Width':'Parameters.Width','Height':'Parameters.Height'})
    m.cut('BottomShell',m.rr(196.4,238.4,25.1,(0,0,4.1),14.2),'Lower enclosure cavity').Refine=False
    outer=_loft(m,'UpperOuter',[(200,242,16,29.2),(198,240,16,53),(190,228,14,72.5)])
    inner=_loft(m,'UpperInner',[(196.4,238.4,14.2,29.0),(194.4,236.4,14.2,52.6),(186.4,224.4,12.2,70.5)])
    shell=m.doc.addObject('Part::Cut','UpperShell');shell.Base=outer;shell.Tool=inner;shell.Refine=False;m.doc.recompute()
    m.register(shell,'UpperShell','Body',4,'sfcgray');outer.Visibility=False;inner.Visibility=False
    m.native('TopPanel','Separate dark-grey original top trim',170,160,10,1.35,(0,10,72.55),'Body',5,'sfcface')
    m.native('FrontTopPanel','Separate front white nameplate panel',157,36,3,1.0,(0,-91,72.55),'Body',5,'sfcgray')
    m.native('RearTopPanel','Separate rear white top panel',157,19,2.5,1.0,(0,103,72.55),'Body',5,'sfcgray')
    for i,(x,y) in enumerate([(-75,-94),(75,-94),(-75,94),(75,94)]):m.cyl('Foot'+str(i),'Original underside support foot',5,1.9,(x,y,0),'Body',-6,'rubber')
    _finish(m,1,'shvc001_native_curved_split_enclosure','依据日版 200 × 242 × 74 mm 包络建立原生下壳、分段曲面上壳和独立深灰顶面板/前后浅灰面板；上下壳保持间隙，壁厚与曲率为近似。74 mm 高度在操作件完成后复核。')


STAGES={1:stage01}


def stage02(m):
    # Original slot and distinct POWER / RESET / EJECT arrangement.
    for key in ['TopPanel','UpperShell']:m.cut(key,m.rr(128,19,10,(0,27,67),7),'Original cartridge dust-flap aperture').Refine=False
    m.native('CartridgeFlap','Original single grey cartridge flap',126.8,17.8,6.5,1.2,(0,27,72.7),'CartridgeInterface',5,'sfcbutton')
    for i,x in enumerate([-53,53]):m.box('FlapRidge'+str(i),'Raised flap finger ridge',1.0,11,.09,(x,27,73.91),'CartridgeInterface',5,'sfcbutton',.45)
    for name,x,w,h in [('Power',-56,25,27),('Reset',56,25,27),('Eject',0,57,25)]:
        for key in ['TopPanel','UpperShell']:m.cut(key,m.rr(w+.8,h+.8,10,(x,-43,67),3.2),'Original '+name+' control opening').Refine=False
        m.native(name+'Cap',name+' original top key',w,h,2.8,3.0,(x,-43,70.9),'Controls',6,'sfcbutton' if name!='Eject' else 'sfcface')
        m.label(name+'Mark',name.upper(),2.5,(x-len(name)*.82,-50,73.93),'Controls',6,'white')
    m.box('PowerRidge','Original raised POWER sliding grip',21,3.5,.09,(-56,-38,73.91),'Controls',6,'sfcbutton',1.2)
    m.label('PowerOnMark','ON',2.0,(-78,-35,73.92),'Body',5,'white');m.label('PowerOffMark','OFF',2.0,(-78,-42,73.92),'Body',5,'white')
    m.label('NintendoWord','Nintendo',5.0,(-69,-94,73.57),'Body',5,'sfcink')
    m.label('SuperFamicomWord','SUPER FAMICOM',3.1,(-69,-101,73.57),'Body',5,'sfcink')
    for key in ['FrontTopPanel','UpperShell']:m.cut(key,m.rr(10,4,8,(63,-98,68),1.9),'Original power indicator aperture').Refine=False
    m.box('PowerLens','Original red power-indicator lens',9.5,3.5,1.0,(63,-98,72.55),'Controls',5,'sfcred',1.6)
    m.label('PowerLampMark','POWER',1.6,(58,-94,73.57),'Body',5,'sfcink')
    # Four colored original-symbol lobes: local outline approximate.
    for i,(dx,dy,c,a) in enumerate([(-4,0,'sfcgreen',-20),(4,0,'sfcred',20),(0,4,'sfcblue',-20),(0,-4,'sfcyellow',20)]):
        shape=m.rr(5.7,2.8,.08,(66+dx,75+dy,73.92),1.3);shape.rotate(V(66+dx,75+dy,0),V(0,0,1),a)
        m.feature('FourColorMark'+str(i),'Original four-color symbol lobe',shape,'Body',5,c)
    _finish(m,2,'original_cartridge_flap_power_reset_eject_and_markings','加入单片卡槽防尘盖、左侧电源滑键/右侧复位键/中央退卡键、前端红色电源灯和原版四色标识；所有孔穿过灰色面板与上壳，按键最高点符合 74 mm 名义包络，局部形状近似。')


STAGES[2]=stage02


def stage03(m):
    back=g.rotation((0,1,0),(0,0,1));front=g.rotation((0,-1,0),(0,0,1))
    for key in ['BottomShell','UpperShell']:
        m.cut(key,m.rr(158,30,10,(-12,115.5,30),3,back),'Inset original rear interface panel aperture').Refine=False
    m.box('RearPortPanel','Inset original rear interface panel',157,29,1.5,(-12,116.5,30),'Ports',0,'sfcgray',2.8,orient=back)
    for name,x,w,h in [('AV',40,28,11),('RF',-14,9,9),('Channel',-33,7,8),('DC',-62,8,8)]:
        m.cut('RearPortPanel',m.rr(w,h,5,(x,115,30),min(2,h/2-.1),back),'Rear '+name+' aperture').Refine=False
    m.box('AVBody','Original twelve-contact MULTI OUT socket',27.4,10.4,12,(40,104.4,30),'Ports',0,'black',1.5,orient=back)
    m.cut('AVBody',m.rr(23,7,9,(40,108.1,30),1.2,back),'Multi-out mating cavity').Refine=False
    for row,z in enumerate([28.3,31.7]):
        for i in range(6):m.box('AVContact'+str(row*6+i),'MULTI OUT schematic contact',1.1,.35,6,(31.5+i*3.4,108.2,z),'Ports',0,'gold',.08,True,orient=back)
    m.ring('RFSocket','Original RF coaxial outer sleeve',4.25,3.1,9,(-14,109,30),'Ports',0,'metal',axis=(0,1,0))
    m.ring('RFInsulator','RF coaxial dielectric',3.05,1.2,6,(-14,109,30),'Ports',0,'white',axis=(0,1,0))
    m.ring('RFContact','RF center receptacle',1.1,.6,5,(-14,109,30),'Ports',0,'gold',axis=(0,1,0))
    m.box('ChannelSwitch','Original CH1 / CH2 switch body',6.6,7.6,8,(-33,108,30),'Ports',0,'black',.7,orient=back)
    m.box('ChannelSlider','Channel selector slider',2,4,1.9,(-34.2,116.1,30),'Ports',0,'sfcbutton',.4,orient=back)
    m.ring('DCSocket','Original external adapter barrel socket',3.7,2.7,9,(-62,109,30),'Ports',0,'black',axis=(0,1,0))
    m.cyl('DCCenter','DC receptacle center contact',.8,7,(-62,109,30),'Ports',0,'metal',axis=(0,1,0))
    for name,x,text in [('AV',53,'MULTI OUT'),('RF',-6,'RF OUT'),('CH',-25,'CH1  CH2'),('DC',-53,'DC IN')]:
        m.label('RearMark'+name,text,2,(x,118.03,19),'Ports',0,'sfcink',rotation=back)
    m.cut('BottomShell',m.rr(165,21,8,(0,-115,18),3.5,front),'Front controller panel aperture').Refine=False
    m.box('FrontPortPanel','Original front two-controller panel',164,20,1.1,(0,-119.8,18),'FrontPanel',-1,'sfcgray',3.2,orient=front)
    for j,x in enumerate([-43,43]):
        m.cut('FrontPortPanel',m.rr(39,10,5,(x,-118,18),4.5,front),'Original seven-contact port aperture').Refine=False
        key='ControllerSocket'+str(j+1)
        m.box(key,'Original seven-contact controller socket',38.2,9.2,9,(x,-111,18),'FrontPanel',-1,'black',4.1,orient=front)
        holes=[]
        for i,dx in enumerate([-12,-8,-4,0,6,10,14]):
            holes.append(Part.makeCylinder(1.25,7,V(x+dx,-120.1,18),V(0,1,0)))
            m.ring('ControllerContact'+str(j+1)+'_'+str(i),'Controller individual contact sleeve',.85,.5,5,(x+dx,-119.6,18),'FrontPanel',-1,'gold',axis=(0,1,0))
        m.cut(key,holes,'Seven individual controller contact bores').Refine=False
        m.label('ControllerNumber'+str(j+1),str(j+1),3,(x-1,-120.93,11),'FrontPanel',-1,'sfcink',rotation=front)
    _finish(m,3,'original_front_and_rear_interfaces','按原版背面照片布置 MULTI OUT、RF、CH1/CH2 与 DC IN；加入两只七触点手柄插座、独立接点和前后嵌入面板。接口局部尺寸近似，未声称可配接。')

STAGES[3]=stage03


def stage04(m):
    # Original passive ventilation: lower underside banks and rear vertical slots.
    tools=[]
    for x in [-78,-65,-52,52,65,78]:
        for y in [-57,-40,-23,-6,11,28]:tools.append(m.rr(8,12,4,(x,y,1),1.0))
    m.cut('BottomShell',tools,'Underside passive ventilation banks').Refine=False
    back=g.rotation((0,1,0),(0,0,1))
    tools=[m.rr(2.2,17,9,(x,113.5,56),1,back) for x in range(-78,79,6)]
    m.cut('UpperShell',tools,'Original rear vertical ventilation slots').Refine=False
    m.cut('BottomShell',m.rr(54,26,5,(0,-70,1),2.8),'Original removable expansion cover aperture').Refine=False
    m.native('ExpansionCover','Removable underside expansion-port cover',53.2,25.2,2.5,1.7,(0,-70,2),'Body',-7,'sfcgray')
    for i,x in enumerate([-13,13]):m.box('ExpansionCoverTab'+str(i),'Expansion cover retaining tab',6,3,1.4,(x,-57,4.2),'Body',-7,'sfcgray',.4)
    m.box('ExpansionSocket','Original 28-contact expansion socket body',43,10,6,(0,-70,5.3),'Ports',-4,'black',.8,True)
    m.cut('ExpansionSocket',m.rr(39,5,5,(0,-70,5.1),.4),'Underside expansion contact recess').Refine=False
    for row,y in enumerate([-71.8,-68.2]):
        for i in range(14):m.box('ExpansionContact'+str(row*14+i),'Expansion socket individual contact',1.1,.3,3,(-17.55+i*2.7,y,6.9),'Ports',-4,'gold',.07,True)
    _finish(m,4,'passive_vents_and_removable_expansion_cover','加入底部通风孔组、后部竖向通风孔和可拆扩展接口盖，独立呈现 28 个扩展接点。局部孔距/接点尺寸为学习近似；保留原版被动散热构造。')

STAGES[4]=stage04


def _plate(points,z,t):
    vs=[V(x,y,z) for x,y in points];return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,0,t))


def stage05(m):
    outline=[(-84,-87),(83,-87),(83,-46),(87,-46),(87,39),(81,39),(81,101),(23,101),(23,105),(-43,105),(-43,97),(-80,97),(-80,45),(-87,45),(-87,-24),(-84,-24)]
    m.feature('MainPCB','Early SHVC-CPU-01 shaped motherboard',_plate(outline,17,1.6),'Mainboard',-2,'pcb',True)
    mounts=[(-76,-78),(75,-78),(-78,37),(77,37),(-71,88),(72,91)]
    m.cut('MainPCB',[Part.makeCylinder(2.1,3,V(x,y,16.5)) for x,y in mounts],'Mainboard mounting holes').Refine=False
    for i,(x,y) in enumerate(mounts):m.ring('MainMountPad'+str(i),'Plated mainboard fixing annulus',3.7,2.15,.035,(x,y,18.63),'Mainboard',-2,'metal',internal=True)
    m.label('MainPCBMark','SHVC-CPU-01',3,(-14,-81,18.64),'Mainboard',-2,'white')
    m.label('MainPCBDate','Nintendo 1990',2.5,(-66,-83,18.64),'Mainboard',-2,'white')
    _finish(m,5,'early_shvc_cpu01_shaped_mainboard','依据早期主板照片建立独立 SHVC-CPU-01 基板、轮廓缺口、六处固定孔及镀层环；为后续独立声卡和分立 PPU 保留位置，板厚及孔位近似。')

STAGES[5]=stage05


def _ic(m,key,label,x,y,w,h,pins,group='Mainboard',z=19.1,t=2.0,layer=-1,qfp=True):
    m.box(key,label,w,h,t,(x,y,z),group,layer,'black',.35,True)
    counts=[pins//4]*4 if qfp else [pins//2]*2
    for side,n in enumerate(counts):
        span=(h if side<2 else w)-2.0
        for i in range(n):
            a=-span/2+i*span/(n-1)
            if side<2:
                xx=x+(-1 if side==0 else 1)*(w/2+.9);yy=y+a;ww=1.7;hh=min(.35,span/n*.55)
            else:
                xx=x+a;yy=y+(-1 if side==2 else 1)*(h/2+.9);ww=min(.35,span/n*.55);hh=1.7
            m.box(key+'Lead'+str(side)+'_'+str(i),'Individual schematic IC lead',ww,hh,.28,(xx,yy,z+.08),group,layer,'metal',.05,True)
    m.label(key+'Mark',' '.join(label) if 'RAM' in label or label=='AMP' else label,1.7,(x-w/2+1,y-1,z+t+.025),group,layer,'white')
    m.cyl(key+'Dot','IC orientation index',.55,.02,(x-w/2+1.4,y-h/2+1.4,z+t+.025),group,layer,'white',internal=True)


def stage06(m):
    _ic(m,'SCPU','S-CPU A',-52,-50,23,27,100)
    _ic(m,'PPU1','S-PPU1',5,-52,24,27,100)
    _ic(m,'PPU2','S-PPU2',5,-13,23,25,100)
    _ic(m,'WRAM','WRAM',-50,-11,29,13,64,qfp=False)
    _ic(m,'VRAM0','VRAM',49,-49,15,25,28,qfp=False)
    _ic(m,'VRAM1','VRAM',49,-12,15,25,28,qfp=False)
    _ic(m,'Encoder','S-ENC',-25,58,12,21,24,qfp=False)
    _ic(m,'Clock','CLOCK',-28,-52,6,8,14,qfp=False)
    _ic(m,'CIC','CIC',73,-35,6,10,16,qfp=False)
    m.box('MainCrystal','Original metal timing crystal',7,13,3.3,(-55,-74,18.8),'Mainboard',-1,'metal',2.5,True)
    m.box('ClockTrimmer','Original clock adjustment trimmer',5,5,3,(-36,-74,18.8),'Mainboard',-1,'sfcred',.6,True)
    m.cyl('ClockTrimmerSlot','Trimmer adjustment insert',1.5,.25,(-36,-74,21.85),'Mainboard',-1,'metal',internal=True)
    _finish(m,6,'separate_cpu_ppus_ram_and_encoder','保留早期主板独立 S-CPU、两片 S-PPU、WRAM、两片 VRAM 和 S-ENC；逐个呈现示意封装引脚、方向点及晶振/微调器，不将布局声称为可制造电路。')

STAGES[6]=stage06


def stage07(m):
    # Small-device clusters occupy observed open corridors; values/routing are not reproduced.
    locations=[(-75,-67),(-75,-59),(-75,-49),(-75,-38),(-67,-28),(-61,-28),(-54,-28),(-44,-28),(-35,-28),(-25,-25),(-24,-16),(-24,-7),(-69,3),(-60,3),(-51,3),(-42,3),(-32,3),(-12,4),(-5,4),(3,4),(12,4),(22,4),(31,4),(40,4),(49,4),(59,4),(67,4),(75,4),(29,-67),(30,-57),(30,-45),(30,-30),(30,-17),(69,-62),(70,-53),(73,-15),(-63,48),(-55,48),(-44,48),(-13,48),(-4,49),(5,48),(17,48),(27,48),(-43,66),(-43,74),(-37,85),(-29,76),(-23,76),(4,78)]
    for i,(x,y) in enumerate(locations):
        c='white' if i%3==0 else 'black'
        m.box('MainPassive'+str(i),'Photo-guided small passive package',2.3,1.2,.65,(x,y,18.85),'Mainboard',-1,c,.13,True)
        for j,dx in enumerate([-1.55,1.55]):m.box('MainPassiveEnd'+str(i)+'_'+str(j),'Separate passive termination',.6,1.15,.3,(x+dx,y,18.85),'Mainboard',-1,'metal',.08,True)
    for i,(x,y,r,h) in enumerate([(-73,58,3.4,7),(-69,73,3.4,7),(-52,72,7,20),(-14,76,3.4,7),(-4,76,3.4,7),(-13,64,3.4,7),(-4,64,3.4,7),(72,62,3,6),(73,-5,3,6)]):
        m.cyl('MainCap'+str(i),'Original electrolytic capacitor envelope',r,h,(x,y,19),'Mainboard',-1,'blue' if h>10 else 'black',internal=True)
        m.cyl('MainCapTop'+str(i),'Separate capacitor metal top',r-.15,.12,(x,y,19+h+.03),'Mainboard',-1,'metal',internal=True)
        for j,dx in enumerate([-r*.45,r*.45]):m.cyl('MainCapLead'+str(i)+'_'+str(j),'Capacitor solder lead',.3,.3,(x+dx,y,18.65),'Mainboard',-1,'metal',internal=True)
    for i,(x,y) in enumerate([(-70,-62),(-68,-35),(-31,-40),(-27,-4),(27,-60),(30,-5),(65,-53),(66,8),(-50,44),(14,68),(42,79),(63,48)]):
        m.box('MainBackPassive'+str(i),'Independent underside passive envelope',2.4,1.4,.55,(x,y,16.3),'Mainboard',-3,'white',.12,True)
        for j,dx in enumerate([-1.6,1.6]):m.box('MainBackPad'+str(i)+'_'+str(j),'Underside termination',.55,1.3,.2,(x+dx,y,16.5),'Mainboard',-3,'metal',.06,True)
    _finish(m,7,'board_passives_capacitors_and_underside','在照片可辨的主板走廊加入独立被动器件、端头、电解电容及背面小器件；大电容位于原版电源区。细部为稀疏学习表达，不包含可制造走线或完整元件表。')

STAGES[7]=stage07


def stage08(m):
    m.box('CartLowerSocket','Original motherboard 62P cartridge receptacle',126,13,9.6,(0,27,19),'CartridgeInterface',0,'black',1,True)
    m.cut('CartLowerSocket',m.rr(120,6,8.8,(0,27,20),.7),'Lower removable-connector mating channel').Refine=False
    m.box('CartUpperConnector','Original removable 62P upper connector',124.5,11.8,16,(0,27,28.8),'CartridgeInterface',1,'black',.8,True)
    m.cut('CartUpperConnector',m.rr(119,4.8,15,(0,27,30.1),.5),'Cartridge PCB mating slot').Refine=False
    for row,y in enumerate([25.1,28.9]):
        for i in range(31):
            x=-55.5+i*3.5+(2 if i>=4 else 0)+(2 if i>=27 else 0)
            m.box('CartUpperContact'+str(row*31+i),'Individual upper 62P spring-contact envelope',1.3,.35,12.8,(x,y,30.2),'CartridgeInterface',1,'gold',.08,True)
            m.box('CartLowerContact'+str(row*31+i),'Individual lower 62P mating-contact envelope',1.3,.35,7.8,(x,y,20.1),'CartridgeInterface',0,'gold',.08,True)
    for i,x in enumerate([-66,66]):
        m.box('CartConnectorEar'+str(i),'Connector mounting ear',4.5,13,2.2,(x,27,19),'CartridgeInterface',0,'black',.6,True)
        m.cut('CartConnectorEar'+str(i),Part.makeCylinder(1.2,3,V(x,27,18.7)),'Connector screw clearance').Refine=False
    _finish(m,8,'original_lower_and_removable_upper_62p_connector','依据任天堂维修手册的上下 62P 连接器拆分为两个壳体及各自独立的 62 个接点，保留两端扩展接点区间；与顶部防尘盖分件呈现。')

STAGES[8]=stage08


def stage09(m):
    m.box('SoundPCB','Original discrete SHVC-SOUND board',70,62,1.6,(48,76,36),'SoundModule',2,'pcb',2,True)
    m.feature('SoundShieldFrame','Separate original sound-module shield frame',m.rr(72,64,13.6,(48,76,35.5),2).cut(m.rr(70.8,62.8,14,(48,76,35.3),1.5)),'SoundModule',2,'metal',True)
    m.box('SoundShieldLid','Removable original sound-module shield lid',72,64,.55,(48,76,49.3),'SoundModule',4,'metal',2,True)
    m.label('SoundLidMark','SHVC-SOUND',3,(26,74,49.88),'SoundModule',4,'sfcink')
    _ic(m,'SoundSMP','S-SMP',31,84,18,18,64,'SoundModule',38.1,2.0,3)
    _ic(m,'SoundDSP','S-DSP',64,84,18,18,80,'SoundModule',38.1,2.0,3)
    _ic(m,'SoundRAM0','RAM 0',31,59,17,9,28,'SoundModule',38.1,1.8,3,False)
    _ic(m,'SoundRAM1','RAM 1',64,59,17,9,28,'SoundModule',38.1,1.8,3,False)
    _ic(m,'SoundDAC','DAC',48,68,8,6,16,'SoundModule',38.1,1.5,3,False)
    _ic(m,'SoundAmp','AMP',74,70,5,6,8,'SoundModule',38.1,1.5,3,False)
    m.box('SoundCrystal','Separate sound clock resonator',10,3,3,(49,100,37.9),'SoundModule',3,'blue',1.3,True)
    for i,(x,y) in enumerate([(20,69),(61,70)]):
        m.cyl('SoundCap'+str(i),'Sound board electrolytic capacitor',2.5,6,(x,y,37.9),'SoundModule',3,'black',internal=True)
        m.cyl('SoundCapTop'+str(i),'Sound capacitor metal top',2.3,.12,(x,y,43.95),'SoundModule',3,'metal',internal=True)
    for i,(x,y) in enumerate([(20,49),(26,49),(33,49),(40,49),(46,49),(53,49),(60,49),(68,49),(76,49),(19,101),(26,101),(33,101),(65,101),(73,101)]):
        m.box('SoundPassive'+str(i),'Separate sound-board passive',2.1,1.1,.7,(x,y,37.85),'SoundModule',3,'white' if i%2 else 'black',.1,True)
        for j,dx in enumerate([-1.4,1.4]):m.box('SoundPassiveEnd'+str(i)+'_'+str(j),'Sound-board passive termination',.5,1.0,.25,(x+dx,y,37.85),'SoundModule',3,'metal',.05,True)
    m.box('SoundBoardSocket','Motherboard sound-module connector',32,6,11.6,(48,57,19),'SoundModule',0,'black',.5,True)
    m.box('SoundModulePlug','Sound-module underside mating connector',31,5.5,5,(48,57,30.8),'SoundModule',1,'black',.5,True)
    for row,y in enumerate([55.4,58.6]):
        for i in range(12):
            x=34.25+2.5*i
            # Exposed ends are distinct from the dielectric, with separate matching bores.
            m.cyl('SoundConnectorPin'+str(row*12+i),'Sound-module individual interface pin',.3,1.0,(x,y,29.5),'SoundModule',0,'gold',internal=True)
    m.cut('SoundBoardSocket',[Part.makeCylinder(.4,1.3,V(34.25+2.5*i,y,29.4)) for y in [55.4,58.6] for i in range(12)],'Individual sound connector contact clearances').Refine=False
    _finish(m,9,'discrete_shvc_sound_module_and_shield','独立建立早期 SHVC-SOUND 子板、可拆金属屏蔽框/盖、S-SMP、S-DSP、两片 RAM、DAC、放大器、时钟和电容；保留主板与子板连接器分层关系，内部尺寸近似。')

STAGES[9]=stage09


def stage10(m):
    m.feature('RFCan','Original separate RF modulator metal enclosure',m.rr(34,26,19,(-14,94,19),1).cut(m.rr(32.8,24.8,19,(-14,94,19.6),.5)),'RF',1,'metal',True)
    m.box('RFLid','Separate RF modulator lid',34,26,.5,(-14,94,38.2),'RF',2,'metal',1,True)
    m.box('RFPCB','RF modulator internal board',31.5,23.5,1.0,(-14,94,21),'RF',1,'pcb',.4,True)
    _ic(m,'RFIC','RF',-17,94,7,6,8,'RF',22.4,1.6,1,False)
    for i,(x,y) in enumerate([(-26,87),(-20,85),(-12,85),(-4,85),(-26,101),(-18,102),(-10,102),(-3,100)]):m.box('RFPassive'+str(i),'RF internal passive envelope',2.4,1.2,.8,(x,y,22.3),'RF',1,'white',.12,True)
    m.cyl('RFCoil','RF modulator inductor envelope',2.4,5,(-5,93,22.3),'RF',1,'copper',internal=True)
    m.label('RFCanMark','RF MODULATOR',2,(-28,92,38.74),'RF',2,'sfcink')
    # Open capacitor shield: the original large capacitor remains independently visible.
    m.feature('CapacitorShield','Original capacitor and regulator shield wall',m.rr(47,56,25,(-56.5,78,18.9),1).cut(m.rr(45.8,54.8,25.4,(-56.5,78,18.7),.5)),'Power',1,'metal',True)
    m.box('RegulatorSink','Original rear vertical regulator heatsink',29,1.4,19,(-51,101.5,19),'Power',1,'metal',.3,True)
    m.box('RegulatorBody','Original voltage regulator package',8,4,9,(-51,97,19.7),'Power',1,'black',.5,True)
    m.box('RegulatorTab','Separate regulator metal tab',7,1.0,10,(-51,99.55,23),'Power',1,'metal',.4,True)
    for i,x in enumerate([-53.5,-51,-48.5]):m.box('RegulatorLead'+str(i),'Voltage regulator individual lead',.55,1.1,.65,(x,96,18.8),'Power',1,'metal',.05,True)
    m.box('PowerFuse','Original input fuse envelope',3,10,2.5,(-75,92,19),'Power',0,'white',1,True)
    for i,y in enumerate([85.8,98.2]):m.box('PowerFuseEnd'+str(i),'Input fuse end terminal',3,1.8,2.4,(-75,y,19),'Power',0,'metal',.3,True)
    m.box('InputDiode','Original DC input rectifier diode',5,3,2.2,(-62,93,19),'Power',0,'black',.5,True)
    for i,x in enumerate([-65.5,-58.5]):m.box('InputDiodeLead'+str(i),'Input diode lead',1.8,.45,.45,(x,93,19),'Power',0,'metal',.1,True)
    _finish(m,10,'rf_modulator_and_original_power_shield','补充独立 RF 调制器壳体/盖与内部板件，原版大电容屏蔽框、稳压器及后部散热片、保险件和输入二极管。保留无风扇主机的被动散热关系，电路仅作非功能结构表达。')

STAGES[10]=stage10


def stage11(m):
    from .atari2600 import _rounded_route
    m.box('FrontPCB','Original removable two-controller board',142,14,1.6,(0,-105,11.5),'FrontPanel',-2,'pcb',2,True)
    for j,x in enumerate([-43,43]):
        for i,dx in enumerate([-12,-8,-4,0,6,10,14]):m.box('FrontSocketTail'+str(j)+'_'+str(i),'Controller socket solder tail',.55,2.7,.3,(x+dx,-109.4,13.2),'FrontPanel',-1,'metal',.06,True)
    m.box('FrontFerriteFoam','Original ferrite-core adhesive foam',23,11,.8,(0,-103,4.3),'Wiring',-4,'rubber',.5,True)
    ferrite=m.rr(22,10,5,(0,-103,5.2),.6).cut(m.rr(16,3.2,12,(0,-109,7.9),.5,g.rotation((0,1,0),(0,0,1))))
    m.feature('FrontRibbonFerrite','Original rectangular ferrite core under front board',ferrite,'Wiring',-3,'black',True)
    # A folded sheet, not a round cable, following the manual's front-board route.
    strips=[Part.makeBox(13,19,.2,V(-6.5,-110,7.8)),Part.makeBox(13,.2,15.9,V(-6.5,-91.2,7.8)),Part.makeBox(13,8.2,.2,V(-6.5,-91.2,23.5)),Part.makeBox(13,.2,3.5,V(-6.5,-110,7.8))]
    ribbon=strips[0]
    for sh in strips[1:]:ribbon=ribbon.fuse(sh)
    m.feature('FrontRibbon','Original folded front-board flat ribbon study',ribbon.removeSplitter(),'Wiring',-1,'white',True)
    m.box('MainRibbonHeader','Mainboard front ribbon receptacle',17,4,4.5,(0,-83,18.8),'Wiring',-1,'white',.5,True)
    for i in range(11):m.box('MainRibbonContact'+str(i),'Individual ribbon exposed contact',.65,2.6,.05,(-6+i*1.2,-83,23.4),'Wiring',-1,'gold',.05,True)
    m.box('PowerSwitchBody','Original separate slide power switch',14,9,9,(-56,-43,58),'Power',3,'black',.6,True)
    m.box('PowerSwitchSlider','Power slide switch actuator',5,5,3.4,(-56,-43,67.2),'Power',3,'sfcgray',.5,True)
    m.box('PowerWireHeader','Polarized original two-wire motherboard header',7,5,4,(-73,44,19),'Wiring',0,'white',.5,True)
    for i,dx in enumerate([-1.7,1.7]):
        pts=[V(-56+dx,-38.3,62),V(-56+dx,-31,62),V(-89+dx,-15,48),V(-89+dx,44,35),V(-73+dx,44,24)]
        m.feature('PowerWire'+str(i),'Original red/black power-switch harness',_rounded_route(pts,1.3,.55),'Wiring',2,'red' if i==0 else 'black',True)
    _finish(m,11,'front_board_flat_ribbon_ferrite_and_power_harness','依据维修手册接线图建立独立前手柄板、折叠扁平排线、板下矩形磁芯及泡棉；保留红黑两线电源开关线束与有极性插头。线束路径为展示近似。')

STAGES[11]=stage11


def stage12(m):
    from .atari2600 import _helical_spring
    points=[(-65,14),(65,14),(65,4),(28,4),(24,-44),(-24,-44),(-28,4),(-65,4)]
    lever=_plate(points,46.5,2)
    for x in [-58,58]:
        lever=lever.fuse(m.rr(6,15,2,(x,20.5,46.5),.8)).fuse(Part.makeCylinder(2.4,3.2,V(x,27,46.5)))
        ear=m.rr(6,7,5,(x,11,48.4),1).cut(Part.makeCylinder(1.35,8,V(x-4,11,50.5),V(1,0,0)))
        lever=lever.fuse(ear)
    m.feature('EjectRocker','Original molded white cartridge eject rocker',lever.removeSplitter(),'EjectMechanism',2,'white',True)
    m.cyl('EjectPivot','Original long steel eject pivot rod',1.1,142,(-71,11,50.5),'EjectMechanism',2,'metal',axis=(1,0,0),internal=True)
    m.box('EjectStem','Original top eject-key actuator stem',16,8,22,(0,-40,48.7),'EjectMechanism',3,'sfcface',1.0,True)
    spring=_helical_spring(2.0,1.1,5,.27);spring.rotate(V(),V(0,1,0),90);spring.translate(V(-70.5,11,50.5))
    m.feature('EjectSpring','Eject return torsion-coil study',spring,'EjectMechanism',2,'metal',True)
    for i,x in enumerate([-74,74]):
        m.box('EjectBearing'+str(i),'Independent pivot support envelope',4,7,6,(x,11,47.5),'EjectMechanism',2,'sfcgray',.8,True)
        m.cut('EjectBearing'+str(i),Part.makeCylinder(1.35,5,V(x-2.5,11,50.5),V(1,0,0)),'Eject pivot clearance').Refine=False
    # Power-linked cartridge retaining slider, outside the dust-flap aperture.
    lock=m.rr(4,58,2.5,(-69,-7,64.2),.6).fuse(m.rr(18,4,2.5,(-62,-34,64.2),.6))
    m.feature('CartridgeLock','Original power-linked cartridge retaining slider study',lock.removeSplitter(),'EjectMechanism',3,'white',True)
    m.box('ResetStem','Original reset-key downward actuator',5,5,39,(56,-43,31.6),'Controls',2,'sfcbutton',.6,True)
    m.box('ResetSwitch','Original reset switch envelope',7,7,4,(56,-43,27.3),'Controls',0,'black',.5,True)
    m.cyl('FlapPivot','Cartridge flap pivot-pin study',.65,126,(-63,31,71.0),'CartridgeInterface',4,'metal',axis=(1,0,0),internal=True)
    flap_spring=_helical_spring(1.35,.85,3.4,.2);flap_spring.rotate(V(),V(0,1,0),90);flap_spring.translate(V(-48,31,71))
    m.feature('FlapSpring','Cartridge flap torsion-coil study',flap_spring,'CartridgeInterface',4,'metal',True)
    _finish(m,12,'eject_rocker_steel_rod_springs_and_power_lock','依据原版维修分解图加入白色退卡摇臂、长钢轴、回位扭簧、顶键传力杆及电源联动卡带锁；防尘盖另设转轴与扭簧。机构表达未作动力学或耐久验证。')

STAGES[12]=stage12


def _gamebit(m,key,x,y,z,length,group='Fixings',layer=-5):
    head=Part.makeCylinder(2.8,1.6,V(x,y,z))
    # External six-lobed security head, as on original Gamebit case screws.
    tool=Part.makeCompound([Part.makeCylinder(.65,1.8,V(x+2.8*math.cos(math.radians(a)),y+2.8*math.sin(math.radians(a)),z-.1)) for a in range(0,360,60)])
    head=head.cut(tool).fuse(Part.makeCylinder(1.15,length,V(x,y,z+1.55)))
    m.feature(key,'Original six-lobe gamebit case fastener study',head,group,layer,'metal',True)


def stage13(m):
    mounts=[(-76,-78),(75,-78),(-78,37),(77,37),(-71,88),(72,91)]
    m.box('BottomShield','Original full motherboard lower shield',180,204,.5,(0,7,14.4),'Shielding',-4,'metal',3,True)
    m.cut('BottomShield',[Part.makeCylinder(2.2,1,V(x,y,14.2)) for x,y in mounts]+[m.rr(15,5,1,(0,-91,14.2),.5)],'Lower shield mounting and ribbon clearances').Refine=False
    m.box('FrontShield','Original front mainboard metal shield',163,88,.6,(0,-37,26.3),'Shielding',1,'metal',2,True)
    m.cut('FrontShield',m.rr(10,10,1,(56,-43,26.1),1),'Reset actuator clearance').Refine=False
    for i,x in enumerate([-79,79]):m.box('FrontShieldWall'+str(i),'Front shield side skirt',.6,86,3.8,(x,-37,22.3),'Shielding',0,'metal',.1,True)
    for i,(x,y) in enumerate(mounts):
        m.ring('MainboardTower'+str(i),'Original lower-shell motherboard support tower',3.8,1.55,10,(x,y,4.25),'Fixings',-4,'sfcgray',internal=True)
        m.ring('MainboardStandoff'+str(i),'Mainboard spacing collar',3.6,1.6,1.9,(x,y,14.98),'Fixings',-3,'sfcgray',internal=True)
        m.screw('MainboardScrew'+str(i),(x,y,20.9),'Fixings',-1,length=7.2,radius=2.5,axis=(0,0,-1))
    case=[(-87,-91),(87,-91),(-90,4),(90,4),(-85,91),(85,91)]
    for key in ['MainPCB','BottomShield']:m.cut(key,[Part.makeCylinder(4.4,7,V(x,y,13)) for x,y in case],'Original case-post edge clearances').Refine=False
    for i,(x,y) in enumerate(case):
        m.cut('BottomShell',Part.makeCylinder(3.1,3.0,V(x,y,1.8)),'Original gamebit access hole').Refine=False
        m.ring('CaseTower'+str(i),'Case screw support tower',4.1,1.65,23,(x,y,4.3),'Fixings',-3,'sfcgray',internal=True)
        _gamebit(m,'CaseGamebit'+str(i),x,y,2.2,26)
    m.box('BottomLabel','Original underside model-label study',60,24,.04,(0,70,1.94),'Body',-7,'white',1)
    m.label('BottomModelMark','SHVC-001',4,(-22,75,1.91),'Body',-7,'sfcink',rotation=App.Rotation(V(1,0,0),180))
    _finish(m,13,'original_shields_towers_and_six_gamebit_fasteners','加入主板下方整片屏蔽板、前部屏蔽罩、主板支柱与紧固件，以及六处 Gamebit 外壳螺钉；紧固件与支柱、板件分开，底面型号铭牌为非序列号学习表达。')

STAGES[13]=stage13


def _dogbone(inset=0):
    r=29-inset;a=43
    curves=[]
    for pts in [[(a,-r),(20,-r),(20,-20+inset),(0,-20+inset)],[(0,-20+inset),(-20,-20+inset),(-20,-r),(-a,-r)]]:
        c=Part.BezierCurve();c.setPoles([V(xx,yy) for xx,yy in pts]);curves.append(c.toBSpline())
    return [Part.LineSegment(V(-a,r),V(a,r)),Part.Arc(V(a,r),V(a+r,0),V(a,-r)),*curves,Part.Arc(V(-a,-r),V(-a-r,0),V(-a,r))]


def _dogshape(x,y,z,t,inset=0):
    shape=Part.Face(Part.Wire([g.toShape() for g in _dogbone(inset)])).extrude(V(0,0,t));shape.translate(V(x,y,z));return shape


def _dogbody(m,key,x,y,z,t):
    body=m.doc.addObject('PartDesign::Body',key+'Body');sk=body.newObject('Sketcher::SketchObject',key+'Sketch');sk.addGeometry(_dogbone(),False)
    pad=body.newObject('PartDesign::Pad',key+'Pad');pad.Profile=sk;pad.Length=t;m.doc.recompute();body.Tip=pad;body.Placement.Base=V(x,y,z);sk.Visibility=False
    m.register(body,key,'Controller1',0,'sfcgray');m.doc.recompute();return body


def stage14(m):
    x=-92;y=-209
    _dogbody(m,'Pad1Bottom',x,y,2,10.5);m.cut('Pad1Bottom',_dogshape(x,y,3.5,10,1.5),'Original dogbone lower shell cavity').Refine=False
    _dogbody(m,'Pad1Top',x,y,12.7,10.3);m.cut('Pad1Top',_dogshape(x,y,12.5,9,1.5),'Original dogbone upper shell cavity').Refine=False
    m.cyl('Pad1ABXYPanel','Original dark circular four-button inset panel',25,.65,(x+43,y,23.1),'Controller1',3,'sfcface')
    m.ring('Pad1DpadRing','Original D-pad circular recess surround',19,17.8,.15,(x-43,y,23.06),'Controller1',3,'sfcgray')
    m.label('Pad1NintendoMark','Nintendo',3,(x-24,y+17,23.06),'Controller1',3,'sfcink')
    m.label('Pad1SFCMark','SUPER FAMICOM',1.9,(x-24,y+12.4,23.06),'Controller1',3,'sfcink')
    # Shoulder-button openings in the upper perimeter.
    for dx in [-41,41]:m.cut('Pad1Top',m.rr(37,7,9,(x+dx,y+27,14.4),2),'Original shoulder key opening').Refine=False
    _finish(m,14,'first_shvc005_native_dogbone_controller_shell','依据原版 SHVC-005 手柄照片建立原生草图/拉伸狗骨形上下壳、独立四键面板、方向键圆形凹区及肩键开口；控制器采用照片所示 1992 年双芯片版，外形局部尺寸近似。')

STAGES[14]=stage14


def stage15(m):
    x=-92;y=-209
    buttons=[('A',56,0,'sfcred'),('B',43,-12,'sfcyellow'),('X',43,12,'sfcblue'),('Y',30,0,'sfcgreen')]
    for name,dx,dy,c in buttons:
        for key in ['Pad1Top','Pad1ABXYPanel']:m.cut(key,Part.makeCylinder(5.6,5,V(x+dx,y+dy,20)),'Original colored action-key aperture').Refine=False
        stem=Part.makeCylinder(4.7,9.7,V(x+dx,y+dy,14.8));rim=Part.makeCylinder(5.3,1.55,V(x+dx,y+dy,23.15))
        sphere=Part.makeSphere(30,V(x+dx,y+dy,-4.8)).common(Part.makeCylinder(5.3,3,V(x+dx,y+dy,24.65)))
        m.feature('Pad1'+name,'Original convex colored '+name+' cap',stem.fuse(rim).fuse(sphere).removeSplitter(),'Controller1',4,c)
    for name,dx,dy in [('A',63,-5),('B',41,-23),('X',41,19),('Y',20,-4)]:m.label('Pad1'+name+'Mark',name,2.6,(x+dx,y+dy,23.79),'Controller1',3,'white')
    cross=m.rr(8,23,3.1,(x-43,y,23.2),.65).fuse(m.rr(23,8,3.1,(x-43,y,23.2),.65)).fuse(Part.makeCylinder(4,8.6,V(x-43,y,14.8)))
    m.feature('Pad1Dpad','Original pivoted cross direction key',cross.removeSplitter(),'Controller1',4,'sfcbutton')
    hole=m.rr(8.8,23.8,5,(x-43,y,20),.7).fuse(m.rr(23.8,8.8,5,(x-43,y,20),.7));m.cut('Pad1Top',hole,'Original cross direction-key aperture').Refine=False
    for i,(dx,dy,a) in enumerate([(0,8,0),(8,0,-90),(0,-8,180),(-8,0,90)]):
        sh=_plate([(-1.7,-1.3),(1.7,-1.3),(0,1.7)],0,.025);sh.rotate(V(),V(0,0,1),a);sh.translate(V(x-43+dx,y+dy,26.34));m.feature('Pad1DpadArrow'+str(i),'Subtle direction arrow',sh,'Controller1',4,'sfcface')
    for name,dx in [('Select',-9),('Start',8)]:
        shape=m.rr(5.2,13,2.8,(x+dx,y-5,23.15),2.4);shape.rotate(V(x+dx,y-5,0),V(0,0,1),-35)
        m.feature('Pad1'+name,'Original diagonal '+name+' key',shape,'Controller1',4,'sfcbutton')
        tool=m.rr(6,13.8,5,(x+dx,y-5,20),2.6);tool.rotate(V(x+dx,y-5,0),V(0,0,1),-35);m.cut('Pad1Top',tool,'Original '+name+' aperture').Refine=False
        m.box('Pad1'+name+'Stem','Independent key actuator',3.5,5,8.2,(x+dx,y-5,14.7),'Controller1',3,'sfcbutton',1.4,True)
        m.label('Pad1'+name+'Mark',name.upper(),1.7,(x+dx-7,y-17,23.07),'Controller1',3,'sfcink')
    # Independent carbon pellets under the three original rubber membrane families.
    membranes=[('Dpad',x-43,y,15.5,[(0,8),(8,0),(0,-8),(-8,0)]),('ABXY',x+43,y,20,[(13,0),(0,-12),(0,12),(-13,0)])]
    for key,cx,cy,r,spots in membranes:
        shape=Part.makeCylinder(r,1.1,V(cx,cy,11.45))
        for dx,dy in spots:shape=shape.fuse(Part.makeCone(3.8,2.6,2.0,V(cx+dx,cy+dy,12.5)))
        m.feature('Pad1'+key+'Membrane','Original '+key+' rubber contact membrane',shape.removeSplitter(),'Controller1',2,'rubber',True)
        for i,(dx,dy) in enumerate(spots):m.cyl('Pad1'+key+'Carbon'+str(i),'Independent conductive rubber contact',2.5,.12,(cx+dx,cy+dy,11.25),'Controller1',1,'black',internal=True)
    m.box('Pad1StartSelectMembrane','Original shared Start/Select rubber membrane',29,11,1.1,(x-.5,y-5,11.45),'Controller1',2,'rubber',3,True)
    for i,dx in enumerate([-9,8]):
        m.cyl('Pad1MenuDome'+str(i),'Start/Select rubber dome',2.7,1.8,(x+dx,y-5,12.7),'Controller1',2,'rubber',internal=True)
        m.cyl('Pad1MenuCarbon'+str(i),'Start/Select conductive contact',2.2,.12,(x+dx,y-5,11.25),'Controller1',1,'black',internal=True)
    _finish(m,15,'first_controller_convex_abxy_dpad_and_membranes','加入日版四色凸面 ABXY、十字方向键、斜置 Start/Select 和独立橡胶膜/导电触点，保持各键可单独查看；按键与上壳开孔同步建模，局部尺寸及行程近似。')

STAGES[15]=stage15


def stage16(m):
    x=-92;y=-209
    points=[(-63,-17),(63,-17),(66,-12),(66,14),(56,19),(56,23),(34,23),(34,19),(9,19),(9,22),(-9,22),(-9,19),(-34,19),(-34,23),(-56,23),(-56,19),(-66,14),(-66,-12)]
    pcb=_plate([(x+a,y+b) for a,b in points],10,1.2)
    m.feature('Pad1PCB','Original 1992-era dual-shift-register controller PCB',pcb,'Controller1',0,'pcb',True)
    holes=[(-64,-10),(64,-10),(-32,20),(32,20),(0,-15)]
    m.cut('Pad1PCB',[Part.makeCylinder(2.5,2,V(x+a,y+b,9.6)) for a,b in holes],'Controller mounting clearances').Refine=False
    for i,(dx,dy) in enumerate([(-43,8),(-35,0),(-43,-8),(-51,0),(56,0),(43,-12),(43,12),(30,0),(-9,-5),(8,-5)]):
        # Printed contact combs remain a very thin independent layer.
        for j in range(5):m.box('Pad1CarbonTrace'+str(i)+'_'+str(j),'Schematic interleaved carbon contact finger',.45,3.6,.015,(x+dx-1.4+j*.7,y+dy,11.205),'Controller1',1,'black',.04,True)
    for i,(dx,dy) in enumerate([(-20,7),(17,-7)]):
        _ic(m,'Pad1ShiftIC'+str(i),'SHIFT',x+dx,y+dy,7,10,16,'Controller1',7.5,1.8,-1,False)
        m.label('Pad1ShiftBackMark'+str(i),'SHIFT',1.7,(x+dx-2.8,y+dy+1,7.47),'Controller1',-1,'white',rotation=App.Rotation(V(1,0,0),180))
    for i,(dx,dy) in enumerate([(-10,12),(0,13),(17,10),(26,9),(-29,-13),(3,5),(23,-13)]):
        m.box('Pad1Passive'+str(i),'Controller discrete passive envelope',2.3,1.2,.6,(x+dx,y+dy,8.9),'Controller1',-1,'white',.12,True)
        for j,a in enumerate([-1.5,1.5]):m.box('Pad1PassiveEnd'+str(i)+'_'+str(j),'Controller passive termination',.5,1.1,.25,(x+dx+a,y+dy,9.4),'Controller1',-1,'metal',.05,True)
    for side,dx in [('L',-46),('R',46)]:
        for i in range(5):m.box('Pad1'+side+'ShoulderTrace'+str(i),'Original integral shoulder-tab carbon contact',.45,4,.02,(x+dx-1.4+i*.7,y+21,11.205),'Controller1',1,'black',.04,True)
    m.label('Pad1PCBMark','1992 Nintendo',2,(x-26,y+15,11.23),'Controller1',1,'white')
    _finish(m,16,'first_controller_dual_shift_register_board_and_contacts','依据 1992 年原版手柄板照片加入双移位寄存器芯片、分立器件、十组主按键碳膜触点和两端一体式肩键接触板；PCB 轮廓和安装孔单独保留，未模拟电路功能。')

STAGES[16]=stage16


def _pad_cable(m,n):
    from .atari2600 import _rounded_route
    sign=-1 if n==1 else 1;x=sign*92;group='Controller'+str(n);pre='Pad'+str(n)
    # Separate display routing, laid outside the console envelope.
    points=[V(x,-179.7,12),V(x,-155,12),V(sign*171,-155,12),V(sign*171,-124,12),V(sign*165.2,-124,12)]
    m.feature(pre+'Cable','Original wired-controller cable, shortened display route',_rounded_route(points,2,1.5),group,0,'black')
    axis=(-sign,0,0)
    m.ring(pre+'Strain','Plug cable strain-relief sleeve',2.4,1.7,4.8,(sign*165,-124,12),group,0,'black',axis=axis)
    m.box(pre+'PlugBody','Original seven-contact rectangular controller plug',36,16,10,(sign*142,-124,7),group,0,'sfcgray',2)
    back=g.rotation((0,1,0),(0,0,1))
    m.box(pre+'PlugNose','Original keyed controller plug nose',32,7.5,7,(sign*142,-115.8,12),group,0,'black',3,orient=back)
    holes=[]
    for i,dx in enumerate([-12,-8,-4,0,6,10,14]):
        holes.append(Part.makeCylinder(1.3,5,V(sign*142+dx,-112.8,12),V(0,1,0)))
        m.ring(pre+'PlugContact'+str(i),'Individual controller plug contact',.85,.5,3.8,(sign*142+dx,-112.6,12),group,0,'gold',axis=(0,1,0))
    m.cut(pre+'PlugNose',holes,'Seven individual plug contact bores').Refine=False
    for i in range(3):m.box(pre+'PlugGrip'+str(i),'Controller plug grip ridge',25,1,.15,(sign*142,-127+i*3,17.05),group,0,'sfcgray',.35)
    m.ring(pre+'CordExit','Controller cable entry strain-relief sleeve',2.4,1.7,4.5,(x,-183,12),group,0,'black',axis=(0,1,0))


def stage17(m):
    x=-92;y=-209
    for side,dx in [('L',-41),('R',41)]:
        cap=m.rr(36,5.6,6.4,(x+dx,y+27,15.3),1.9).fuse(m.rr(5,8,2,(x+(-46 if side=='L' else 46),y+24,14.7),.8))
        px=x+(-56 if side=='L' else 56)
        cap=cap.cut(Part.makeCylinder(.95,10,V(px,y+21,17.2),V(0,1,0)))
        m.feature('Pad1'+side+'Key','Original independent '+side+' shoulder key',cap.removeSplitter(),'Controller1',3,'sfcgray')
        m.cyl('Pad1'+side+'Pivot','Original shoulder pivot pin',.7,7.5,(px,y+21.5,17.2),'Controller1',2,'metal',axis=(0,1,0),internal=True)
        cx=x+(-46 if side=='L' else 46)
        m.cyl('Pad1'+side+'Rubber','Original separate shoulder rubber dome',3.4,2.7,(cx,y+21,11.45),'Controller1',2,'rubber',internal=True)
        if side=='R':m.cut('Pad1ABXYMembrane',Part.makeCylinder(3.7,4,V(cx,y+21,11.3)),'Original shoulder membrane separation').Refine=False
        m.cyl('Pad1'+side+'Carbon','Original shoulder conductive pellet',2.4,.12,(cx,y+21,11.25),'Controller1',1,'black',internal=True)
        m.label('Pad1'+side+'Mark',side,3,(x+dx-1,y+25,21.75),'Controller1',3,'sfcink')
    holes=[(-64,-10),(64,-10),(-32,20),(32,20),(0,-15)]
    for i,(dx,dy) in enumerate(holes):
        m.cut('Pad1Bottom',Part.makeCylinder(2.5,2.3,V(x+dx,y+dy,1.8)),'Controller rear cross-head access').Refine=False
        m.ring('Pad1LowerPost'+str(i),'Controller lower-shell support post',2.3,1.0,5.9,(x+dx,y+dy,3.8),'Controller1',-1,'sfcgray',internal=True)
        m.ring('Pad1UpperPost'+str(i),'Controller upper-shell threaded support post',2.2,1.0,9.6,(x+dx,y+dy,11.4),'Controller1',1,'sfcgray',internal=True)
        m.screw('Pad1Screw'+str(i),(x+dx,y+dy,2.2),'Controller1',-2,length=16.8,radius=2.0)
    # Rear-center cable aperture and short internal conductor fanout.
    m.cut('Pad1Top',Part.makeCylinder(2.65,5,V(x,y+26,12),V(0,1,0)),'Controller cable-entry upper relief').Refine=False
    m.cut('Pad1Bottom',Part.makeCylinder(2.65,5,V(x,y+26,12),V(0,1,0)),'Controller cable-entry lower relief').Refine=False
    for i in range(7):
        dx=-3+i
        m.box('Pad1CableSolder'+str(i),'Controller cable PCB solder pad',.6,2.0,.08,(x+dx,y+18,11.25),'Controller1',1,'metal',.05,True)
    _pad_cable(m,1)
    _finish(m,17,'first_controller_shoulders_five_screws_and_seven_pin_cord','完成原版 L/R 肩键、独立橡胶与枢轴、五枚后盖螺钉、出线护套及七触点有线插头。外部线缆缩短并铺开展示，不代表原线长。')

STAGES[17]=stage17


def stage18(m):
    exclude=('Pad1Cable','Pad1Plug','Pad1Strain','Pad1Cord')
    for key,o in list(m.parts.items()):
        if o.Assembly!='Controller1' or key.startswith(exclude):continue
        shape=o.Shape.copy();shape.translate(V(184,0,0))
        m.feature(key.replace('Pad1','Pad2',1),o.Label+' / second original controller',shape,'Controller2',o.ExplodeLayer,o.MaterialDescription,o.Fidelity.startswith('Schematic'))
    # PCB solder pads belong to each controller, even though external cable routing differs.
    for i in range(7):m.box('Pad2CableSolder'+str(i),'Second controller cable PCB solder pad',.6,2,.08,(92-3+i,-191,11.25),'Controller2',1,'metal',.05,True)
    _pad_cable(m,2)
    _finish(m,18,'second_original_controller_and_distinct_cable_route','按日版原装配置加入第二只同版本 SHVC-005 手柄，逐件保留独立标识；两条有线手柄线缆分别沿左右侧铺开展示，避免遮挡主机与接口。')

STAGES[18]=stage18


def stage19(m):
    from .atari2600 import _rounded_route
    x=240;y=50
    m.native('ACLower','Optional original HVC-002 lower adapter shell',52,78,4,15,(x,y,16),'Accessories',-2,'black')
    m.cut('ACLower',m.rr(48.6,74.6,14,(x,y,17.7),2.6),'Linear adapter lower cavity').Refine=False
    m.native('ACUpper','Optional original HVC-002 upper adapter shell',52,78,4,22.8,(x,y,31.2),'Accessories',4,'black')
    m.cut('ACUpper',m.rr(48.6,74.6,21.3,(x,y,31),2.6),'Linear adapter upper cavity').Refine=False
    for i,dx in enumerate([-6.35,6.35]):m.box('ACBlade'+str(i),'Original parallel Japanese AC blade study',1.4,6.3,15.8,(x+dx,y+18,0),'Accessories',-3,'metal',.12)
    frame=m.rr(34,31,27,(x,y+10,19),.8).cut(m.rr(22,19,27.4,(x,y+10,18.8),.3))
    m.feature('ACTransformerCore','Original laminated linear-transformer core envelope',frame,'Accessories',0,'metal',True)
    for i,z in enumerate([19.3,43.2]):m.box('ACBobbinFlange'+str(i),'Transformer insulating bobbin flange',21.8,18.8,.5,(x,y+10,z),'Accessories',0,'white',.3,True)
    m.box('ACWinding','Transformer winding envelope',20,17,22.5,(x,y+10,20),'Accessories',1,'copper',1,True)
    sleeve=m.rr(21.4,18.4,22.7,(x,y+10,19.9),1.1).cut(m.rr(20.3,17.3,23.1,(x,y+10,19.7),.7))
    m.feature('ACWindingTape','Original yellow transformer insulation study',sleeve,'Accessories',1,'sfcyellow',True)
    m.box('ACPCB','Original small rectifier/filter board',35,17,1.2,(x,23,20),'Accessories',0,'pcb',1,True)
    m.cyl('ACCap','Original reservoir capacitor envelope',5,18,(x-8,23,21.5),'Accessories',1,'black',internal=True)
    m.cyl('ACCapTop','Filter capacitor metal top',4.8,.13,(x-8,23,39.55),'Accessories',1,'metal',internal=True)
    for i,dy in enumerate([-5,-1.5,2,5.5]):
        m.box('ACRectifier'+str(i),'Original discrete rectifier diode envelope',5,1.8,1.6,(x+8,23+dy,21.5),'Accessories',1,'black',.5,True)
        for j,dx in enumerate([-4,4]):m.box('ACRectifierLead'+str(i)+'_'+str(j),'Individual rectifier lead',2,.35,.35,(x+8+dx,23+dy,21.5),'Accessories',1,'metal',.07,True)
    for i,(dx,dy) in enumerate([(-19,-30),(19,30)]):
        m.ring('ACCasePost'+str(i),'Adapter case fastener support',3.3,1.5,30,(x+dx,y+dy,18),'Accessories',0,'black',internal=True)
        m.cut('ACPCB',Part.makeCylinder(3.6,2,V(x+dx,y+dy,19.8)),'Adapter board post clearance').Refine=False
        m.cut('ACLower',Part.makeCylinder(3.3,3,V(x+dx,y+dy,15.8)),'Adapter screw access').Refine=False
        head=m.rr(4.4,4.4,1.3,(x+dx,y+dy,16.2),.3).cut(m.rr(2.3,2.3,.6,(x+dx,y+dy,16.1),.2));head=head.fuse(Part.makeCylinder(1.15,30,V(x+dx,y+dy,17.45)))
        m.feature('ACSecurityScrew'+str(i),'Original adapter square raised security-head screw study',head,'Accessories',-2,'metal',True)
    m.label('ACModelMark','HVC-002',4,(x-17,y+12,54.04),'Accessories',4,'white')
    m.label('ACTypeMark','AC ADAPTER',3,(x-18,y+22,54.04),'Accessories',4,'white')
    m.label('ACRatingMark','10V  850mA',2.5,(x-17,y+3,54.04),'Accessories',4,'white')
    # External DC cord is shortened, presented outside the console.
    for key in ['ACLower','ACUpper']:m.cut(key,Part.makeCylinder(2.2,6,V(x,9,31.1),V(0,1,0)),'Adapter DC cord aperture').Refine=False
    points=[V(x,10.7,31.1),V(x,-12,31.1),V(290,-12,31.1),V(290,35,31.1)]
    m.feature('ACDCCord','Optional HVC-002 shortened DC lead',_rounded_route(points,4,1.5),'Accessories',0,'black')
    m.ring('ACCordRelief','Adapter DC lead strain-relief sleeve',2.0,1.65,6,(x,6,31.1),'Accessories',0,'black',axis=(0,1,0))
    m.cyl('ACDCGrip','Original molded DC barrel-plug grip',4,16,(290,35.3,31.1),'Accessories',0,'black',axis=(0,1,0))
    m.ring('ACDCBarrel','DC plug outer barrel',2.75,1.2,9,(290,51.5,31.1),'Accessories',0,'metal',axis=(0,1,0))
    _finish(m,19,'optional_original_hvc002_linear_adapter','依据原版 HVC-002 拆机照片建立另售外置线性适配器：分离外壳、并列插片、铁芯/线包、整流滤波小板和 DC 线。仅为非功能结构学习模型；不构成电源制造图。')

STAGES[19]=stage19


def stage20(m):
    from .atari2600 import _rounded_route
    x=240;y=-90
    m.box('AVPlugBody','Optional original SHVC-008 grey MULTI OUT plug',30,25,11,(x,y,6),'Accessories',0,'sfcgray',2)
    m.box('AVPlugNose','Original keyed multi-out plug mating nose',24,12,8,(x,y+18.7,7.5),'Accessories',0,'black',1)
    m.cut('AVPlugNose',m.rr(20,5,10,(x,y+25.2,11.5),.7,g.rotation((0,-1,0),(0,0,1))),'Multi-out plug mating cavity').Refine=False
    for row,z in enumerate([9.6,13.4]):
        for i in range(6):m.box('AVPlugContact'+str(row*6+i),'Individual multi-out plug contact',1.0,6,.25,(x-8.5+i*3.4,y+20,z),'Accessories',0,'gold',.05,True)
    m.label('AVPlugMark','Nintendo',2.6,(x-11,y-2,17.04),'Accessories',0,'sfcink')
    for i in range(3):m.box('AVPlugGrip'+str(i),'Original AV plug grip ridge',24,1.1,.25,(x,y-7+i*3,17.1),'Accessories',0,'sfcgray',.35)
    # Three independently separated strands, compact display arrangement.
    for i,(dx,c) in enumerate([(-16,'sfcyellow'),(0,'white'),(16,'red')]):
        sx=x+(i-1)*3.2;ex=324-i*16
        pts=[V(sx,y-12.7,11.5),V(sx,-151+i*7,11.5),V(ex,-151+i*7,11.5),V(ex,-93,11.5)]
        m.feature('AVStrand'+str(i),'Separate composite/audio cable strand',_rounded_route(pts,2.5,1.2),'Accessories',0,'black')
        m.cyl('RCAHousing'+str(i),'Original color-coded RCA molded grip',4.5,20,(ex,-92.7,11.5),'Accessories',0,c,axis=(0,1,0))
        for j in range(5):m.ring('RCAGrip'+str(i)+'_'+str(j),'RCA grip rib',4.85,4.55,.9,(ex,-88+j*2.6,11.5),'Accessories',0,c,axis=(0,1,0))
        m.ring('RCASleeve'+str(i),'RCA outer signal-ground sleeve',4.0,3.2,8,(ex,-72.5,11.5),'Accessories',0,'metal',axis=(0,1,0))
        m.cyl('RCADielectric'+str(i),'RCA contact dielectric',3.0,3,(ex,-72.5,11.5),'Accessories',0,'white',axis=(0,1,0))
        m.cyl('RCAPin'+str(i),'RCA center signal pin',1.4,10,(ex,-69.3,11.5),'Accessories',0,'metal',axis=(0,1,0))
    _finish(m,20,'optional_shvc008_stereo_composite_av_cable','依据 SHVC-008 实物照片建立另售灰色 MULTI OUT 插头及黄色视频、白/红双声道 RCA；单独保留接点、绝缘件和护套，线束缩短铺展。主机原装双手柄与另售 AC/AV 在交付说明中分别标明。')

STAGES[20]=stage20


def stage21(m):
    # Remaining mechanical supports, kept clear of the mainboard and case wall.
    for i,(x,y) in enumerate([(-66,27),(66,27)]):
        m.ring('CartScrewWasher'+str(i),'Cartridge connector fixing washer',2.2,1.0,.35,(x,y,21.3),'Fixings',0,'metal',internal=True)
        m.cut('MainPCB',Part.makeCylinder(1.1,3,V(x,y,16.5)),'Cartridge connector fixing clearance').Refine=False
        m.screw('CartFixingScrew'+str(i),(x,y,22.1),'Fixings',0,length=5.2,radius=1.8,axis=(0,0,-1))
    for i,x in enumerate([-68,68]):
        m.ring('FrontBoardMount'+str(i),'Front controller board support',2.6,1.0,6.5,(x,-104,4.3),'Fixings',-3,'sfcgray',internal=True)
        m.cut('FrontPCB',Part.makeCylinder(1.5,2,V(x,-104,11.3)),'Front controller board screw clearance').Refine=False
        m.screw('FrontBoardScrew'+str(i),(x,-104,14.7),'Fixings',-1,length=6,radius=2.1,axis=(0,0,-1))
    m.label('RearModelMark','SHVC-001',2.1,(29,118.04,40.5),'Ports',0,'sfcink',rotation=g.rotation((0,1,0),(0,0,1)))
    _finish(m,21,'final_original_console_kit_and_mechanical_review','补齐前手柄板支承紧固、连接器固定细节与型号标记，完成早期日版 SHVC-001、两只原版 SHVC-005 手柄及另售 AC/AV 学习套件；最终将对源码重建、实体、装配、STEP、图册和网页逐项核验。')

STAGES[21]=stage21


def finalize(model):
    from .deliver import finalize as shared_finalize
    previous=App.ParamGet('User parameter:BaseApp/Preferences/Mod/Part/General').GetInt('WriteSurfaceCurveMode',1)
    Part.setStaticValue('write.surfacecurve.mode',1)
    try:
        result=shared_finalize(model)
        model.snapshot('final_front',normal=(.3,-1.2,.8),assemblies=model.profile['envelope_groups'])
        model.snapshot('final_controller',normal=(.15,-.3,2),assemblies=['Controller1'],exclude=[k for k in model.parts if k.startswith(('Pad1Cable','Pad1Plug','Pad1Strain'))])
        model.snapshot('final_hero',normal=(.25,-.7,1.8),assemblies=result[0]['handheld_groups'])
        model.doc.save();return result
    finally:Part.setStaticValue('write.surfacecurve.mode',previous)
