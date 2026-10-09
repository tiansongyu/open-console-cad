"""Original 2001 black Xbox v1.0 and wired Duke: approximate structural study."""
import math,types
import FreeCAD as App
import FreeCADGui as Gui
import Part
from .core import V
from . import geometry as g


def configure(m):
    def snapshot(self,name,normal=(.6,-1,1.5),assemblies=None,exclude=(),size=(1800,1400)):
        App.setActiveDocument(self.doc.Name);Gui.activateView('Gui::View3DInventor',True)
        objs=self.visible(assemblies,exclude)
        up=(0,1,0) if abs(normal[0])+abs(normal[1])<.01 or assemblies in (['Controller'],['Accessories']) else (0,0,1)
        if abs(V(*normal).cross(V(*up)).Length)<.001:up=(0,0,1)
        q=g.rotation(normal,up);sh=Part.makeCompound([o.Shape for o in objs]);sh.Placement=App.Placement(V(),q.inverted()).multiply(sh.Placement)
        b=sh.optimalBoundingBox(False,False);return g.render(self.out/'previews'/(name+'.png'),normal=normal,up=up,target=tuple(q.multVec(b.Center)),span=max(b.YLength,b.XLength*size[1]/size[0])*1.16,size=size)
    m.snapshot=types.MethodType(snapshot,m)
    m.colors.update(green=(.18,.48,.025),jewel=(.16,.38,.035),steel=(.4,.42,.43),cream=(.7,.64,.47),yellow=(.85,.68,.08))


def _finish(m,n,slug,summary):
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=n;m.checkpoint(n,slug,summary)


def _poly(points,z,t):
    vs=[V(x,y,z) for x,y in points];return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,0,t))


def _cut(m,key,tools,why):return m.cut(key,tools,why)


def stage01(m):
    configure(m)
    m.native('LowerShell','Original Xbox lower enclosure',320,260,4,89,(0,0,3),'Body',-5,'accent',expr={'Width':'Parameters.Width'})
    _cut(m,'LowerShell',m.rr(315,255,90,(0,0,6),2),'Open interior cavity').Refine=False
    # Front and rear fascia are separate native bodies rather than painted rectangles.
    _cut(m,'LowerShell',[m.rr(314,7,90,(0,-128,5),1),m.rr(310,7,90,(0,128,5),1)],'Independent front and rear fascia seats').Refine=False
    m.native('FrontFascia','Original front fascia',313,2.3,.7,85,(0,-128.7,6),'Body',0,'accent')
    m.native('RearFascia','Original rear fascia',309,2.3,.7,85,(0,128.7,6),'Body',0,'accent')
    m.native('TopCover','Original removable upper enclosure',319.5,259.5,4,5.4,(0,0,92.3),'Body',7,'accent')
    _cut(m,'TopCover',m.rr(314,254,3.4,(0,0,91.9),2),'Upper shell underside relief').Refine=False
    for i,(x,y) in enumerate([(-147,-116),(147,-116),(-147,116),(147,116)]):m.box('RubberFoot'+str(i),'Original rubber foot over case screw',22,16,2.8,(x,y,.1),'Body',-6,'rubber',4)
    _finish(m,1,'original_black_enclosure_and_four_feet','采用微软明确标作近似的 320×260×100 mm 包络，建立可编辑下壳、独立前后面板、上盖及四个橡胶脚；局部壁厚和曲率为照片指导近似。')


STAGES={1:stage01}


def stage02(m):
    # Broad molded diagonal X, with its center hidden under a separate green jewel.
    pts=[(-158,-126),(-32,-126),(0,-105),(32,-126),(158,-126),(62,0),(158,126),(32,126),(0,105),(-32,126),(-158,126),(-62,0)]
    cross=_poly(pts,97.8,1.9).cut(Part.makeCylinder(36.5,3,V(0,0,97.4)))
    m.feature('TopMoldedX','Original broad X-shaped raised top ribs',cross,'Body',8,'black')
    m.cyl('TopJewelBase','Green original center jewel',36,1.8,(0,0,97.85),'Body',9,'jewel')
    m.label('TopXboxMark','XBOX',14,(-22,-5,99.68),'Body',10,'black')
    for side in [-1,1]:
        holes=[m.rr(5,2.8,74,(side*159,-110+6.5*i,13),.4) for i in range(35)]
        _cut(m,'LowerShell',holes,'Original side vertical ventilation slots').Refine=False
        grooves=[]
        for i in range(35):
            y=-110+6.5*i;edge=64+abs(y)*96/126;width=max(2,156-edge)
            grooves.append(m.rr(width,2.8,3.5,(side*(edge+width/2),y,94.7),.4))
        _cut(m,'TopCover',grooves,'Ribbed triangular top ventilation banks').Refine=False
    # Front: tray on left, two control keys on center seam, four controller ports below.
    _cut(m,'FrontFascia',m.rr(133,5,24,(-76,-128.7,62),.7),'DVD tray front aperture').Refine=False
    m.box('DVDTrayFace','Original DVD tray fascia',132,2.1,23,(-76,-129.15,62.5),'Controls',1,'black',.6)
    q=App.Rotation(V(1,0,0),90)
    m.label('TrayXboxMark','XBOX',5,(-90,-130.23,73),'Controls',2,'white',rotation=q)
    for name,z,r in [('Eject',55,7.8),('Power',31,4.8)]:
        _cut(m,'FrontFascia',Part.makeCylinder(r+.3,6,V(0,-132,z),V(0,1,0)),name+' button aperture').Refine=False
        m.cyl(name+'Button','Original '+name+' front key',r,2,(0,-130,z),'Controls',2,'black',axis=(0,1,0))
    m.ring('EjectGreenRing','Original eject status ring',8.25,7.95,.3,(0,-130.02,55),'Controls',3,'green',axis=(0,1,0))
    _cut(m,'FrontFascia',Part.makeCylinder(8.6,4,V(0,-131,55),V(0,1,0)),'Separate illuminated eject ring seat').Refine=False
    _finish(m,2,'raised_x_green_jewel_side_vents_and_front_controls','补齐原版顶部宽 X 形筋、绿色圆形饰牌、侧面竖向通风槽和顶盖三角格栅、左侧 DVD 托盘面、中央退碟键与电源键；饰牌为静态结构，不含现代显示屏。')

STAGES[2]=stage02


def _front_port(m,key,x,z,w,h,depth,group='Ports',kind='Original controller'):
    # Front-facing receptacle: local Z extrusion rotated toward +Y.
    q=App.Rotation(V(1,0,0),-90)
    def sh(a,b,c,y):return m.rr(a,b,c,(x,y,z),min(a/2-.1,b/2-.1),q)
    sleeve=sh(w,h,depth,-129.4).cut(sh(w-1,h-1,depth+.3,-129.55))
    m.feature(key+'Sleeve',kind+' receptacle sleeve',sleeve,group,0,'metal',True)
    m.box(key+'Tongue',kind+' insulating tongue',w-3,depth-3,1.1,(x,-123.5,z-.55),group,0,'black',.2,True)
    for i in range(5):m.box(key+'Pin'+str(i),kind+' schematic contact',.65,depth-4,.12,(x+(i-2)*2.2,-123.5,z+.6),group,0,'gold',.04,True)


def stage03(m):
    for i,x in enumerate([-119,-65,65,119]):
        _cut(m,'FrontFascia',m.rr(24.6,6,13.6,(x,-128.5,19.2),1.5),'Controller connector fascia opening').Refine=False
        _front_port(m,'ControllerPort'+str(i),x,26,24,13,13)
        m.label('PortNumber'+str(i),str(i+1),4,(x-1.1,-130.04,42),'Controls',1,'white',rotation=App.Rotation(V(1,0,0),90))
    # Rear Ethernet, proprietary A/V and two-pin mains; no HDMI or modern USB.
    q=App.Rotation(V(1,0,0),90)
    for key,x,z,w,h in [('Ethernet',-117,24,16,14),('AV',-73,24,32,13)]:
        _cut(m,'RearFascia',m.rr(w+.6,6,h+.6,(x,128.5,z-h/2-.3),.6),'Original rear '+key+' aperture').Refine=False
        shell=m.rr(w,h,12,(x,129.6,z),.8,q).cut(m.rr(w-1,h-1,12.4,(x,129.8,z),.5,q))
        m.feature(key+'Shell','Original rear '+key+' receptacle',shell,'Ports',0,'metal',True)
        m.box(key+'Tongue','Original '+key+' connector insulating tongue',w-3,8,1,(x,123.2,z-.5),'Ports',0,'black',.2,True)
        for i in range(8):m.box(key+'Pin'+str(i),'Original rear schematic connector contact',.5,6,.1,(x+(i-3.5)*(w-4)/8,123.2,z+.55),'Ports',0,'gold',.03,True)
    _cut(m,'RearFascia',m.rr(19,6,10,(127,128.5,21),1.2),'Original AC appliance inlet opening').Refine=False
    sh=m.rr(18,9,11,(127,129.6,26),2,q).cut(m.rr(14,5.5,10,(127,130,26),2,q))
    m.feature('ACInlet','Original two-pin AC inlet body',sh,'Ports',0,'black',True)
    for i,x in enumerate([123,131]):m.cyl('ACContact'+str(i),'AC inlet contact pin',.9,7,(x,121,26),'Ports',0,'metal',axis=(0,1,0),internal=True)
    holes=[]
    for i in range(11):
        for j in range(9):holes.append(Part.makeCylinder(2.9,5,V(-10+6.5*i,126,21+6.5*j),V(0,1,0)))
    _cut(m,'RearFascia',holes,'Rear exhaust perforation field').Refine=False
    _finish(m,3,'four_original_controller_ports_and_rear_connections','加入四个原版前控制器口及独立触点、后以太网、专用 A/V 与交流电源入口，并建立后置风扇通风孔；不混用 HDMI 或现代 USB 接口。')

STAGES[3]=stage03


def stage04(m):
    m.native('LowerShield','Original lower EMI tray floor',308,244,2,.55,(0,0,7.1),'Frame',-4,'metal')
    for side in [-1,1]:m.box('ShieldSide'+str(side),'Lower EMI tray folded side',.5,241,62,(side*153.6,0,7.8),'Frame',-3,'metal',.05,True)
    m.box('ShieldRear','Lower EMI tray rear lip',304,.5,11,(0,121.4,7.8),'Frame',-3,'metal',.05,True)
    _cut(m,'ShieldRear',[m.parts[k].Shape for k in ['EthernetShell','AVShell']],'Rear receptacle shield clearances').Refine=False
    m.native('UpperShield','Original upper stamped EMI lid',307,243,2,.5,(0,0,92),'Frame',6,'metal')
    holes=[m.rr(40,19,1,(x,y,91.8),1) for x in [-105,-35,35,105] for y in [-87,-29,29,87]]
    _cut(m,'UpperShield',holes,'Stamped upper shield ventilation slots').Refine=False
    for i,(x,y) in enumerate([(-140,-105),(-30,-105),(79,-105),(-140,14),(79,14),(-140,106),(-30,106),(79,106)]):
        m.ring('MainboardPost'+str(i),'Motherboard screw standoff',3.2,1.35,4,(x,y,7.9),'Frame',-2,'metal',internal=True)
    _finish(m,4,'lower_and_upper_emi_shields_and_board_posts','建立上下冲压 EMI 屏蔽、折边与主板隔柱；上盖通风孔为照片指导的结构近似，所有隔柱和板件独立可查。')

STAGES[4]=stage04


def _chip(m,key,w,h,t,x,y,z,color='black'):
    return m.box(key,'Original motherboard '+key+' package study',w,h,t,(x,y,z),'Mainboard',0,color,.2,True)


def stage05(m):
    m.native('Mainboard','Original v1.0 main logic board',226,221,1,1.5,(-30.5,.5,12),'Mainboard',-1,'pcb')
    holes=[Part.makeCylinder(1.65,2,V(x,y,11.8)) for x,y in [(-140,-105),(-30,-105),(79,-105),(-140,14),(79,14),(-140,106),(-30,106),(79,106)]]
    _cut(m,'Mainboard',holes,'Original motherboard mounting holes').Refine=False
    _chip(m,'CPUCarrier',31,31,1.15,30,57,13.65,'pcb');_chip(m,'CPUDie',11,13,.5,30,57,14.9,'metal')
    _chip(m,'GPUCarrier',35,35,1.2,-35,48,13.65);_chip(m,'GPUDie',17,17,.5,-35,48,14.95,'metal')
    _chip(m,'MCPX',25,25,1.6,-98,-8,13.65)
    # Four occupied RAM packages: two front and two back, with separate empty footprints.
    for i,(x,y) in enumerate([(-67,80),(-41,-3)]):
        _chip(m,'RAMFront'+str(i),23,11,1.4,x,y,13.65)
        _chip(m,'RAMBack'+str(i),23,11,1.4,x,y,10.4)
    for i,(x,y) in enumerate([(-93,67),(-3,-4)]):
        for side in [0,1]:
            z=13.56 if side==0 else 11.93
            for j in range(10):
                for row in [-1,1]:m.box('EmptyRAMPads%d_%d_%d_%d'%(i,side,j,row),'Unpopulated original RAM footprint pad',1.2,1.8,.04,(x+(j-4.5)*2.1,y+row*6.2,z),'Mainboard',0,'gold',.03,True)
    for key,x,y,w,h in [('Flash',-104,-63,15,9),('VideoEncoder',-106,89,13,13),('EthernetPHY',-127,55,10,10),('ClockLogic',-10,-58,8,8)]:_chip(m,key,w,h,1.2,x,y,13.65)
    _finish(m,5,'original_v1_motherboard_cpu_gpu_mcpx_and_four_ram','加入 v1.0 主板、733 MHz 处理器与 NV2A/MCPX 封装示意；四枚已装内存分布两面，同时保留空焊位，避免把空焊位误当成内存升级。')

STAGES[5]=stage05


def stage06(m):
    # Through-hole regulator capacitors are distributed along the original CPU power side.
    for i,(x,y,r,h) in enumerate([(64,61,5,22),(64,77,5,22),(64,93,5,22),(10,25,5,22),(25,25,5,22),(40,25,5,22),(-9,90,3.5,12),(-108,23,3.5,12),(-124,-30,3.5,12),(-23,-50,3.5,12)]):
        m.cyl('BoardCap'+str(i),'Original cylindrical regulator capacitor',r,h,(x,y,13.7),'Mainboard',0,'black',internal=True)
        m.cyl('BoardCapTop'+str(i),'Capacitor top vent face',r-.3,.1,(x,y,13.85+h),'Mainboard',1,'metal',internal=True)
    for i,(x,y) in enumerate([(9,5),(29,5),(49,5)]):
        m.ring('BoardToroid'+str(i),'Approximate toroidal regulator inductor core',5,2.5,4,(x,y,14),'Mainboard',0,'black',internal=True)
        # Discrete turns lie above the core rather than intersecting its solid material.
        for j in range(7):
            a=j*2*math.pi/7
            m.cyl('ToroidTurn%d_%d'%(i,j),'Schematic inductor winding segment',.5,4,(x+3.75*math.cos(a),y+3.75*math.sin(a),18.1),'Mainboard',1,'copper',internal=True)
    for i in range(24):
        x=-127+(i%12)*17.2;y=-87+(i//12)*23
        for j in range(4):
            xx=x+(j%2)*4;yy=y+(j//2)*5
            if (-113<xx<-95 and -69<yy<-57) or (-16<xx<-4 and -64<yy<-52):continue
            m.box('SMD%d_%d'%(i,j),'Schematic motherboard passive body',1.6,.8,.5,(xx,yy,13.6),'Mainboard',0,'cream',.05,True)
            for side in [-1,1]:m.box('SMDTerm%d_%d_%d'%(i,j,side),'Schematic passive end termination',.22,.85,.55,(xx+side*.95,yy,13.58),'Mainboard',0,'metal',.03,True)
    # Main IDE is a 2x20 header. Optical drive has a separate power harness.
    m.box('IDEHeader','Original 40-pin parallel ATA header',52,6,6,(-26,-99,13.7),'Mainboard',1,'black',.5,True)
    _cut(m,'IDEHeader',m.rr(49,3.8,5.5,(-26,-99,14.5),.2),'Open IDE header cavity').Refine=False
    for row in [-1,1]:
        for i in range(20):m.box('IDEPin%d_%d'%(row,i),'Parallel ATA header pin',.55,.55,4,(-26+(i-9.5)*2.54,-99+row*1.27,15),'Mainboard',1,'gold',.02,True)
    m.box('ATXHeader','Original v1.0 motherboard power connector',24,9,7,(63,-25,13.7),'Mainboard',1,'white',.5,True)
    _cut(m,'ATXHeader',[Part.makeBox(3,3,6,V(53+i*4,-27.5,15.2)) for i in range(5)],'Power connector socket wells').Refine=False
    for i in range(5):m.box('ATXPin'+str(i),'Schematic board power contact',.5,.5,4,(54.5+i*4,-26,15.3),'Mainboard',1,'gold',.02,True)
    # Small front USB daughterboard is specific to early original motherboard arrangement.
    m.box('FrontUSBBoard','Original v1.0 front controller daughterboard',36,23,1.2,(-85,-78,19),'Mainboard',1,'pcb',1,True)
    m.box('FrontUSBLogic','Front controller interface package',9,9,1,(-85,-78,20.4),'Mainboard',1,'black',.3,True)
    _finish(m,6,'v1_regulators_board_discretes_and_parallel_ata_header','补充圆柱电容、环形电感、离散封装、40 针并行 ATA 插座、主板供电插座及早期前控制器小板；元件数量、引脚及线路不构成可用电路。')

STAGES[6]=stage06


def _fan(m,key,center,r,depth,axis,group='Fan',layer=3):
    # Axisymmetric frame and five separate swept-looking blade studies.
    origin=V(*center);q=App.Rotation(V(0,0,1),V(*axis))
    def put(sh):sh.Placement=App.Placement(origin,q).multiply(sh.Placement);return sh
    m.feature(key+'Duct','Original fan cylindrical support frame',put(Part.makeCylinder(r,depth).cut(Part.makeCylinder(r-2,depth+.2,V(0,0,-.1)))),group,layer,'black',True)
    m.feature(key+'Hub','Fan rotor hub',put(Part.makeCylinder(r*.3,depth*.6,V(0,0,depth*.2))),group,layer,'black',True)
    for i in range(5):
        pts=[(r*.32,-r*.08),((r-2.5)*.94,-(r-2.5)*.3),((r-2.5)*.94,r*.12),(r*.34,r*.13)]
        sh=_poly(pts,depth*.43,.65);sh.rotate(V(),V(0,0,1),i*72)
        m.feature(key+'Blade'+str(i),'Approximate original fan blade',put(sh),group,layer,'black',True)
    for i in range(4):
        sh=Part.makeBox(r*.69-2.2,.9,.7,V(r*.31,-.45,depth*.1));sh.rotate(V(),V(0,0,1),i*90)
        m.feature(key+'Strut'+str(i),'Stationary fan motor support',put(sh),group,layer,'black',True)


def stage07(m):
    m.box('CPUInterface','CPU nonfunctional thermal interface',11,13,.1,(30,57,15.45),'Cooling',0,'thermal',.1,True)
    m.box('CPUHeatsinkBase','Original passive CPU aluminum heatsink base',51,49,2,(30,57,15.7),'Cooling',1,'metal',.6,True)
    for i in range(17):m.box('CPUFin'+str(i),'Original CPU extruded heatsink fin',1,48,35,(6+i*3,57,17.8),'Cooling',2,'metal',.12,True)
    for side in [-1,1]:m.box('CPUClip'+str(side),'Simplified CPU heatsink retention clip',1.2,59,1.2,(30+side*27,57,19),'Cooling',1,'steel',.2,True)
    m.box('GPUInterface','GPU nonfunctional thermal interface',17,17,.1,(-35,48,15.5),'Cooling',0,'thermal',.1,True)
    m.box('GPUHeatsinkBase','Original v1.0 active GPU heatsink base',52,52,1.8,(-35,48,15.75),'Cooling',1,'metal',.6,True)
    for i in range(18):m.box('GPUFin'+str(i),'Original GPU heatsink fin',.8,51,14,(-59.65+i*2.9,48,17.7),'Cooling',2,'metal',.1,True)
    _fan(m,'GPUFan',(-35,48,32.2),22.5,8,(0,0,1),'Cooling',3)
    _fan(m,'RearFan',(27,96,51),35,25,(0,1,0),'Fan',3)
    for i,(x,z) in enumerate([(-7,17),(61,17),(-7,85),(61,85)]):m.ring('RearFanMount'+str(i),'Rear exhaust fan mounting eye',2.7,1.1,3,(x,119,z),'Fan',3,'black',axis=(0,1,0),internal=True)
    _cut(m,'ShieldRear',[Part.makeCylinder(2.9,4,V(x,118.7,17),V(0,1,0)) for x in [-7,61]],'Rear fan lower mounting-eye seats').Refine=False
    _finish(m,7,'passive_cpu_active_v1_gpu_and_rear_exhaust','建立早期原版的大 CPU 被动散热器、小 GPU 主动散热器与后排风扇，避免混用后期无 GPU 风扇的修订；叶形、导热层和压片仅为结构近似。')

STAGES[7]=stage07


def stage08(m):
    m.box('PSUInsulator','Original open power-supply insulating floor',61,204,.7,(120,14,8.2),'Power',-2,'cream',1,True)
    m.native('PSUBoard','Original open power-supply PCB',58,194,1,1.4,(120,12,12),'Power',-1,'pcb')
    for i,(x,y) in enumerate([(96,-78),(144,-78),(96,103),(144,103)]):
        _cut(m,'PSUBoard',Part.makeCylinder(1.3,2,V(x,y,11.8)),'Power board mounting hole').Refine=False
        m.ring('PSUPost'+str(i),'Power board insulated standoff',2.5,1.3,2.6,(x,y,9.1),'Power',-2,'cream',internal=True)
    for i,(x,y,w,h,ht) in enumerate([(121,0,30,27,28),(111,67,18,22,20),(133,-51,15,18,16)]):
        m.box('PSUMagnetic'+str(i),'Original power magnetic component',w,h,ht,(x,y,13.6),'Power',0,'black',1,True)
        m.box('PSUWinding'+str(i),'Simplified insulated transformer winding',w*.7,h*.7,.6,(x,y,14+ht),'Power',1,'copper',1,True)
    for i,(x,y,r,h) in enumerate([(110,39,7,29),(133,39,7,29),(104,-32,4,16),(119,-64,4,16),(134,83,4,16)]):
        m.cyl('PSUCap'+str(i),'Original power supply capacitor',r,h,(x,y,13.6),'Power',0,'black',internal=True)
        m.cyl('PSUCapTop'+str(i),'Power capacitor top',r-.4,.15,(x,y,13.85+h),'Power',1,'metal',internal=True)
    for i,(x,y) in enumerate([(96,10),(144,68)]):
        m.box('PSUHeat'+str(i),'Original power heatsink',1,36,24,(x,y,13.6),'Power',0,'metal',.1,True)
    for i in range(8):m.box('PSUDiode'+str(i),'Power rectifier package study',3,4,2,(100+(i%4)*11,-77+(i//4)*95,13.6),'Power',0,'black',.2,True)
    _finish(m,8,'open_internal_power_supply_board_and_magnetics','加入原版右侧开放式内置电源板、绝缘片、变压器、电容和散热片；几何仅用于布局观察，不构成电气安全或功能电路设计。')

STAGES[8]=stage08


def stage09(m):
    # Drive caddies are separate polymer frames above the logic board.
    tray=m.rr(153,185,3,(-72,-18,42),2).cut(m.rr(140,171,4,(-72,-18,41.5),1))
    m.feature('DVDCarrier','Original optical drive plastic carrier',tray,'Optical',1,'black',True)
    for i,(x,y) in enumerate([(-146,-96),(2.3,-96),(-146,59),(0,59)]):m.box('DVDCarrierPost'+str(i),'Optical carrier vertical support',4,5,27,(x,y,14.5),'Optical',0,'black',.5,True)
    body=m.rr(146,178,38,(-72,-18,46),1).cut(m.rr(143.8,175.8,39,(-72,-18,47),.4))
    m.feature('DVDChassis','Original tray-loading DVD chassis',body,'Optical',2,'metal',True)
    m.box('DVDCover','Original removable DVD upper cover',146,178,.7,(-72,-18,84.3),'Optical',5,'metal',1,True)
    m.box('DVDPCB','Original optical drive underside logic PCB',100,60,1.2,(-72,34,48),'Optical',2,'pcb',1,True)
    for i,(x,y) in enumerate([(-100,34),(-76,34),(-52,34)]):m.box('DVDLogic'+str(i),'Optical drive control package',13,12,1.5,(x,y,49.4),'Optical',2,'black',.3,True)
    loading=m.rr(135,153,2,(-72,-28,68),2).cut(Part.makeCylinder(60,3,V(-72,-26,67.5)))
    m.feature('DVDLoadingTray','Original sliding DVD loading tray with empty disc seat',loading,'Optical',3,'black',True)
    _cut(m,'DVDChassis',m.rr(137,5,9,(-72,-107,65),.6),'Sliding tray front travel opening').Refine=False
    m.cyl('DVDSpindle','Original optical spindle motor',10,8,(-72,-26,51),'Optical',2,'metal',internal=True)
    m.cyl('DVDSpindleHub','Optical disc centering hub',7,6,(-72,-26,59.3),'Optical',3,'black',internal=True)
    for i,x in enumerate([-87,-57]):m.cyl('DVDGuide'+str(i),'Optical pickup guide rail',1.4,83,(x,-14,57),'Optical',3,'metal',axis=(0,1,0),internal=True)
    m.box('DVDPickup','Original optical pickup carriage',22,16,7,(-72,12,53),'Optical',3,'black',1,True)
    m.cyl('DVDLens','Schematic optical pickup objective',2.3,.7,(-72,12,60.2),'Optical',3,'blue',internal=True)
    for i,(x,y,r) in enumerate([(-125,-69,7),(-125,-51,9),(-125,-29,11)]):m.cyl('DVDGear'+str(i),'Simplified loading gear',r,2.5,(x,y,56),'Optical',3,'white',internal=True)
    m.box('DVDIDE','Optical drive parallel ATA connector',51,8,6,(-73,67,74),'Optical',4,'black',.4,True)
    m.box('DVDPower','Original optical drive power header',17,8,6,(-120,67,74),'Optical',4,'white',.4,True)
    _cut(m,'DVDChassis',[m.parts[k].Shape for k in ['DVDIDE','DVDPower']],'Rear IDE and power connector chassis openings').Refine=False
    _finish(m,9,'original_dvd_carrier_tray_spindle_and_pickup','建立独立塑料光驱托架、金属罩、空载滑出托盘、主轴、光学滑架、导轨、齿轮、控制板及并行 ATA/供电插座；没有现代吸入式机构。')

STAGES[9]=stage09


def stage10(m):
    carrier=m.rr(110,155,3,(77,-29,53.5),2).cut(m.rr(99,144,4,(77,-29,53),1))
    m.feature('HDDCarrier','Original hard drive plastic carrier',carrier,'Storage',1,'black',True)
    for i,(x,y) in enumerate([(24,-98),(130,-98),(24,24),(130,18)]):m.box('HDDCarrierPost'+str(i),'Hard drive carrier support',4,4,12,(x,y,41),'Storage',0,'black',.4,True)
    base=m.rr(101.6,147,24,(77,-29,58),1.5).cut(m.rr(96.6,142,24,(77,-29,60),1))
    m.feature('HDDBase','Original 3.5-inch hard drive lower casting',base,'Storage',2,'metal',True)
    m.box('HDDCover','Original removable hard drive stamped cover',101.6,147,.8,(77,-29,82.3),'Storage',5,'metal',1.5,True)
    m.box('HDDLabel','Generic drive identification paper; no counterfeit serial',57,102,.05,(77,-29,83.2),'Storage',6,'white',.4)
    m.label('HDDLabelMark','IDE HDD',7,(57,-30,83.27),'Storage',7,'black')
    m.ring('HDDPlatter','Schematic hard disk platter',44,10,1,(77,-40,67),'Storage',3,'metal',internal=True)
    m.cyl('HDDHub','Hard disk spindle hub',9,4,(77,-40,65),'Storage',3,'metal',internal=True)
    m.cyl('HDDActuator','Hard drive actuator pivot',7,6,(111,19,63),'Storage',3,'metal',internal=True)
    arm=_poly([(106,17),(77,-4),(78,-8),(113,12)],70,1.1)
    m.feature('HDDArm','Simplified hard drive actuator arm',arm,'Storage',4,'metal',True)
    m.box('HDDHead','Nonfunctional disk read-head block',2.5,3,1,(77,-7,68.7),'Storage',3,'black',.2,True)
    m.box('HDDPCB','Original drive underside logic board',89,58,1.1,(77,7,56.3),'Storage',1,'pcb',1,True)
    m.box('HDDIDE','Hard drive parallel ATA socket',51,7,6,(65,45,72),'Storage',4,'black',.4,True)
    m.box('HDDPower','Original four-pin drive power connector',18,7,7,(106,45,71),'Storage',4,'white',.6,True)
    _cut(m,'HDDBase',[m.parts[k].Shape for k in ['HDDIDE','HDDPower']],'Rear drive connector casting reliefs').Refine=False
    _finish(m,10,'original_hard_drive_carrier_casting_platter_and_actuator','加入独立 3.5 英寸硬盘托架、铸壳、可拆顶盖、盘片、主轴和磁头臂示意；标签不伪造序列号，实体结构不表达实际可用容量。')

STAGES[10]=stage10


def _wire(m,key,pts,r=.4,color='black',group='Wiring',layer=2):
    from .atari2600 import _rounded_route
    return m.feature(key,'Independent original cable route study',_rounded_route([V(*p) for p in pts],max(.7,1.5*r),r),group,layer,color,True)


def stage11(m):
    # Solid folded ribbon; the thin film and folds are geometry, not a painted stripe.
    yz=[(-99,20.5),(-108,20.5),(-113,25),(-113,87),(-109,89),(76,89),(76,80),(70,80),(70,80.5),(75.5,80.5),(75.5,88.5),(-109,88.5),(-112.5,86.5),(-112.5,25),(-107.5,21),(-99,21)]
    vs=[V(-51.2,y,z) for y,z in yz];sh=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(51,0,0))
    m.feature('IDERibbonMotherboard','Folded original motherboard-to-optical IDE ribbon',sh,'Wiring',4,'rubber',True)
    m.box('IDERibbonAcross','Original shared IDE ribbon over drive caddies',90,45,.5,(45,47.5,88.5),'Wiring',4,'rubber',.05,True)
    yz=[(70,88.5),(70,88),(51,88),(51,78),(49,78),(49,77.5),(51.5,77.5),(51.5,87.5),(70.5,87.5),(70.5,88.5)]
    vs=[V(40,y,z) for y,z in yz];sh=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(50,0,0))
    m.feature('IDERibbonHDD','Folded hard-drive IDE ribbon termination',sh,'Wiring',4,'rubber',True)
    for i in range(5):
        y=-27.8+i*.9
        _wire(m,'BoardPowerLead'+str(i),[(54.5+i*4,y,21),(54.5+i*4,y,28),(87,y,28),(101,y,23)],.3,'yellow' if i%2 else 'black')
    for i in range(4):
        x=102+i*2.5
        _wire(m,'HDDPowerLead'+str(i),[(x,50,75),(x,55,75),(137+i*2.5,57,53),(137+i*2.5,20,49)],.35,'red' if i==0 else 'yellow' if i==3 else 'black')
    for i in range(6):
        _wire(m,'DVDPowerLead'+str(i),[(-125+i*1.5,72,78),(-125+i*1.5,81,78),(-140+i*1.5,82,36),(-140+i*1.5,-87,35),(-126+i*1.5,-92,22)],.28,'yellow' if i%2 else 'black')
    for i in range(2):
        _wire(m,'GPUFanLead'+str(i),[(-59,48+i*1.2,38),(-66,48+i*1.2,35),(-76,48+i*1.2,23),(-77,48+i*1.2,16)],.25,'red' if i==0 else 'black')
        _wire(m,'RearFanLead'+str(i),[(62.5,98,48+i),(73,94,44+i),(76,85,37+i),(76,64,16+i)],.25,'red' if i==0 else 'black')
    for i,x in enumerate([-119,-65,65,119]):
        _wire(m,'FrontControllerLead'+str(i),[(x,-114.5,26),(x,-114.5,36+i*2),(x,-123,36+i*2),(-85+i*3,-123,36+i*2),(-85+i*3,-90,22)],.6)
    for i in range(2):_wire(m,'FrontKeyLead'+str(i),[(7.5+i*1.5,-124,45),(7.5+i*1.5,-119,43),(7.5+i*1.5,-96,23)],.3,'red' if i==0 else 'black')
    _cut(m,'DVDChassis',m.parts['IDERibbonMotherboard'].Shape,'Rear parallel ATA ribbon exit').Refine=False
    _finish(m,11,'folded_shared_ide_ribbon_and_separate_power_harnesses','加入共享并行 ATA 折叠排线、硬盘/光驱电源束、GPU 与后风扇导线和前部控制线；所有线路为独立可检查的非功能路线近似。')

STAGES[11]=stage11


def stage12(m):
    # Six long original case screws: four below feet, two below labels.
    locations=[(-147,-116),(147,-116),(-147,116),(147,116),(15,-116),(-50,116)]
    for i,(x,y) in enumerate(locations):
        post=Part.makeCylinder(3.7,80,V(x,y,8)).cut(Part.makeCylinder(1.6,81,V(x,y,7.5)))
        # The screw guide belongs to the case but does not consume occupied component volumes.
        m.feature('CasePost'+str(i),'Original long case screw guide',post,'Frame',0,'accent',True)
        shaft=Part.makeCylinder(1.2,81,V(x,y,7));m.feature('CaseShaft'+str(i),'Original long case fastener shank',shaft,'Frame',0,'steel',True)
        m.ring('CaseHead'+str(i),'Original recessed Torx-head approximation',2.5,.9,.7,(x,y,5.1),'Frame',-5,'steel',internal=True)
        _cut(m,'LowerShell',Part.makeCylinder(3,4,V(x,y,3)),'Hidden original case fastener recess').Refine=False
        for key in ['LowerShield','UpperShield','PSUInsulator']:_cut(m,key,Part.makeCylinder(4,100,V(x,y,0)),'Original case-guide shield passage').Refine=False
    for i,(x,y) in enumerate([(-140,-105),(-30,-105),(79,-105),(-140,14),(79,14),(-140,106),(-30,106),(79,106)]):
        m.ring('BoardHead'+str(i),'Motherboard screw head',2.2,.7,.5,(x,y,13.7),'Frame',0,'metal',internal=True)
        m.cyl('BoardShaft'+str(i),'Motherboard screw shank',1,4,(x,y,9.5),'Frame',0,'metal',internal=True)
    q=App.Rotation(V(1,0,0),180)
    for i,(x,y) in enumerate([(15,-108),(-50,108)]):m.box('BaseLabel'+str(i),'Generic underside information sticker',60,30,.08,(x,y,2.83),'Body',-6,'white',.5)
    m.label('RearXboxMark','XBOX',6,(-128,130.01,76),'Body',1,'white',rotation=g.rotation((0,1,0),(0,0,1)))
    _finish(m,12,'six_hidden_case_screws_board_fasteners_and_labels','补齐四脚与两处标签下的六枚长壳体紧固件、主板螺钉及通用识别标记；驱动槽和螺纹简化，不伪造序列号或监管认证。')

STAGES[12]=stage12


def _cp(x=0,y=0,z=0):return V(x+285,y-70,z)


def _duke_curves(sx=1,sy=1):
    right=[[(0,51),(20,53),(50,50),(65,41)],[(65,41),(85,35),(92,15),(89,-5)],[(89,-5),(87,-30),(77,-65),(63,-69)],[(63,-69),(49,-70),(44,-50),(30,-45)],[(30,-45),(20,-49),(7,-49),(0,-49)]]
    curves=[]
    for pts in right+[[(-x,y) for x,y in reversed(s)] for s in reversed(right)]:
        b=Part.BezierCurve();b.setPoles([V(x*sx,y*sy) for x,y in pts]);curves.append(b.toBSpline())
    return curves


def _duke_loft(m,key,profiles,inside=False):
    sections=[]
    for i,(sx,sy,z) in enumerate(profiles):
        curves=_duke_curves(sx,sy)
        if inside:
            wire=Part.Wire([c.toShape() for c in curves]).makeOffset2D(-2.2);curves=[]
            for edge in wire.Edges:
                e=edge.toNurbs().Edges[0];c=e.Curve.copy();c.segment(e.FirstParameter,e.LastParameter);curves.append(c)
        sk=m.doc.addObject('Sketcher::SketchObject',key+'Profile'+str(i));sk.addGeometry(curves,False);sk.Placement.Base=_cp(0,0,z);m.group('Construction').addObject(sk);sections.append(sk)
    o=m.doc.addObject('Part::Loft',key);o.Sections=sections;o.Solid=True;o.Ruled=False;o.MaxDegree=3;m.doc.recompute();o.Shape.check(True);m.group('Construction').addObject(o)
    for sk in sections:sk.Visibility=False
    o.Visibility=False;return o


def _duke_shell(m,key,outer,inner,layer):
    a=_duke_loft(m,key+'Outer',outer);b=_duke_loft(m,key+'Inner',inner,True)
    o=m.doc.addObject('Part::Cut',key);o.Base=a;o.Tool=b;o.Refine=False;m.doc.recompute();o.Shape.check(True);a.Visibility=False;b.Visibility=False
    return m.register(o,key,'Controller',layer,'accent')


def stage13(m):
    _duke_shell(m,'DukeBack',[(.88,.88,0),(.98,.98,8),(1,1,22)],[(.9,.9,2.2),(.98,.98,8),(1,1,22.2)],-4)
    _duke_shell(m,'DukeFront',[(1,1,22.3),(.99,.99,31),(.94,.94,39)],[(1,1,22.1),(.99,.99,31),(.96,.96,36.8)],4)
    # Two stacked memory-card slots at the upper edge are an original Duke feature.
    for z in [14,29]:
        hole=m.rr(49,20,8,tuple(_cp(0,47,z-4)),1)
        for key in ['DukeBack','DukeFront']:_cut(m,key,hole,'Original stacked memory-card port opening').Refine=False
    _cut(m,'DukeFront',Part.makeCylinder(27,5,_cp(0,13,37.5)),'Original circular decorative jewel seat').Refine=False
    m.cyl('DukeJewel','Original static translucent center jewel approximation',26.6,1.3,tuple(_cp(0,13,38.1)),'Controller',5,'black')
    for i,angle in enumerate([-36,36]):
        sh=m.rr(4,30,.04,(0,0,0),1);sh.rotate(V(),V(0,0,1),angle);sh.translate(_cp(0,19,39.43))
        m.feature('DukeJewelX'+str(i),'Static green jewel cross marking',sh,'Controller',6,'green')
    _cut(m,'DukeJewelX1',m.parts['DukeJewelX0'].Shape,'Static jewel shared cross stroke').Refine=False
    m.label('DukeJewelMark','XBOX',6,tuple(_cp(-12,-2,39.46)),'Controller',6,'green')
    _finish(m,13,'original_duke_native_curved_shell_and_static_jewel','依据原版 Duke 实物建立宽大曲线放样前后壳、双层记忆卡口与静态绿色饰窗；不采用现代复刻 LCD、无线、电池或 Share 部件。')
    m.snapshot('13_duke_shell',assemblies=['Controller'],normal=(.2,-.4,2))

STAGES[13]=stage13


DUKE_STICKS=[(-57,11),(45,-29)]
DUKE_KEYS=[('White',47,31,'white'),('Black',64,27,'black'),('Y',47,13,'yellow'),('B',64,9,'red'),('X',47,-5,'blue'),('A',64,-9,'green')]


def stage14(m):
    holes=[Part.makeCylinder(13,15,_cp(x,y,29)) for x,y in DUKE_STICKS]
    holes += [Part.makeCylinder(5.2,15,_cp(x,y,29)) for _,x,y,_ in DUKE_KEYS]
    holes += [Part.makeCylinder(14.2,15,_cp(-39,-27,29))]
    holes += [m.rr(8.5,6.3,15,tuple(_cp(x,-36,29)),2.5) for x in [-12,12]]
    _cut(m,'DukeFront',holes,'Original asymmetric sticks six face buttons and D-pad apertures').Refine=False
    for i,(x,y) in enumerate(DUKE_STICKS):
        sh=Part.makeSphere(12.5,_cp(x,y,35)).common(Part.makeCylinder(13,5.4,_cp(x,y,35.5))).cut(Part.makeCylinder(3.1,8,_cp(x,y,34)))
        m.feature('DukeStickDome'+str(i),'Original analog stick dust dome',sh,'Controller',3,'black',True)
        m.ring('DukeStickStem'+str(i),'Original hollow thumbstick neck',2.8,2,9,tuple(_cp(x,y,35)),'Controller',4,'black',internal=True)
        sh=Part.makeCylinder(10,3,_cp(x,y,44.2)).cut(Part.makeSphere(22,_cp(x,y,68)))
        m.feature('DukeStickCap'+str(i),'Original concave analog thumbstick cap',sh,'Controller',5,'black')
    for key,x,y,color in DUKE_KEYS:
        sh=Part.makeCylinder(4.8,7.5,_cp(x,y,33));sh=sh.makeFillet(.8,[e for e in sh.Edges if e.BoundBox.ZLength<1e-7 and e.BoundBox.ZMax>40.4])
        m.feature('DukeButton'+key,'Original Duke '+key+' face button',sh,'Controller',4,color)
        if len(key)==1:m.label('DukeMark'+key,key,3.3,tuple(_cp(x-1.2,y-1.2,40.54)),'Controller',5,'white')
    m.cyl('DukeDPadDisc','Original circular D-pad lower web',13.7,1.4,tuple(_cp(-39,-27,38.1)),'Controller',4,'black')
    a=m.rr(7,23,2.5,tuple(_cp(-39,-27,39.65)),2);b=m.rr(23,7,2.5,tuple(_cp(-39,-27,39.65)),2)
    m.feature('DukeDPadCross','Original glossy raised directional cross',a.fuse(b).removeSplitter(),'Controller',5,'black')
    for i,(x,label) in enumerate([(-12,'BACK'),(12,'START')]):
        m.box('DukeSystemKey'+str(i),'Original '+label+' key',8,5.8,3,tuple(_cp(x,-36,37.8)),'Controller',4,'black',2.5)
        m.label('DukeSystemMark'+str(i),label,2,tuple(_cp(x-3.5,-32,39.2)),'Controller',5,'white')
    _finish(m,14,'duke_six_original_face_keys_asymmetric_sticks_and_dpad','加入原版六键 White/Black/Y/B/X/A、非对称摇杆、圆盘十字键及 Start/Back；按键颜色、曲率和文字用几何近似表达。')

STAGES[14]=stage14


def stage15(m):
    # A single main PCB with upper connector cutout, not the later Series dual-board layout.
    pts=[(-70,39),(-78,14),(-75,-36),(-29,-38),(-22,-44),(22,-44),(29,-38),(75,-36),(78,14),(70,39),(25,39),(25,17),(-25,17),(-25,39)]
    sk=m.doc.addObject('Sketcher::SketchObject','DukeBoardOutline');vs=[V(x,y) for x,y in pts];sk.addGeometry([Part.LineSegment(a,b) for a,b in zip(vs,vs[1:]+vs[:1])],False);sk.Placement.Base=_cp(0,0,21);m.group('Construction').addObject(sk)
    o=m.doc.addObject('Part::Extrusion','DukeMainPCB');o.Base=sk;o.DirMode='Normal';o.LengthFwd=1.3;o.Solid=True;m.doc.recompute();sk.Visibility=False;m.register(o,'DukeMainPCB','Controller',0,'pcb',True)
    outside=Part.makeBox(250,220,65,_cp(-125,-110,-1)).cut(m.doc.getObject('DukeBackInner').Shape)
    _cut(m,'DukeMainPCB',outside,'Native curved inner-shell PCB envelope').Refine=False
    m.box('DukeMCU','Original controller processing package study',12,12,1.5,tuple(_cp(0,-7,19.3)),'Controller',-1,'black',.3,True)
    for side in [-1,1]:
        for i in range(12):m.box('DukeMCUPin%d_%d'%(side,i),'Controller package lead approximation',.4,1.5,.16,tuple(_cp((i-5.5)*.9,-7+side*6.85,20.75)),'Controller',0,'metal',.03,True)
    for i,(x,y) in enumerate([(-17,-12),(17,-12)]):m.box('DukeCrystal'+str(i),'Original controller crystal can study',8,3,2,tuple(_cp(x,y,22.5)),'Controller',1,'metal',1.2,True)
    for i,(x,y) in enumerate(DUKE_STICKS):
        frame=m.rr(21,21,8,tuple(_cp(x,y,22.5)),1).cut(m.rr(18,18,9,tuple(_cp(x,y,22.2)),.6))
        m.feature('DukeAnalogFrame'+str(i),'Original two-axis analog module metal frame',frame,'Controller',1,'metal',True)
        m.ring('DukeGimbalX'+str(i),'Analog gimbal outer cradle',7,5,2,tuple(_cp(x,y,26)),'Controller',2,'black',internal=True)
        m.cyl('DukeGimbalY'+str(i),'Analog transverse pivot',1.1,17,tuple(_cp(x-8.5,y,29.2)),'Controller',2,'metal',axis=(1,0,0),internal=True)
        m.cyl('DukeAnalogShaft'+str(i),'Original analog stick pivot shaft',1.6,10,tuple(_cp(x,y,30.3)),'Controller',3,'black',internal=True)
        for j,(dx,dy,w,h) in enumerate([(12,0,2.5,16),(0,12,16,2.5)]):m.box('DukePot%d_%d'%(i,j),'Analog stick potentiometer',w,h,7,tuple(_cp(x+dx,y+dy,22.5)),'Controller',1,'green',.5,True)
    for i in range(28):
        x=-64+(i%7)*19;y=-17+(i//7)*8
        if any((x-a)**2+(y-b)**2<19**2 for a,b in DUKE_STICKS) or -26<x<26 and y>12:continue
        if 38<x<73 and -19<y<41:continue
        m.box('DukePassive'+str(i),'Schematic controller passive component',1.8,.9,.5,tuple(_cp(x,y,22.5)),'Controller',1,'cream',.1,True)
    _finish(m,15,'duke_single_mainboard_and_analog_mechanisms','建立原版单主板、中央接口开口、控制芯片、晶振及两组带框架/万向支架/电位器的摇杆；封装和离散器件为结构研究近似。')

STAGES[15]=stage15


def stage16(m):
    # Six-key conductive carbon sheet is separate from the plain silicone keymat.
    for key,x,y,color in DUKE_KEYS:
        for side in [0,1]:
            sh=Part.makeCylinder(3.8,.04,V(),V(0,0,1),180);sh.rotate(V(),V(0,0,1),side*180);sh=sh.cut(Part.makeBox(9,.3,.2,V(-4.5,-.15,-.05)));sh.translate(_cp(x,y,22.36))
            m.feature('DukeContact'+key+str(side),'Original six-key split PCB contact',sh,'Controller',1,'gold',True)
        m.ring('DukeCarbonSheet'+key,'Original separate carbon-sticker contact layer',4.2,1.1,.07,tuple(_cp(x,y,22.45)),'Controller',1,'black',internal=True)
        diaphragm=Part.makeCone(4.4,2.7,7,_cp(x,y,23.25)).cut(Part.makeCone(3.9,2.2,7.2,_cp(x,y,23.15)))
        m.feature('DukeKeyDome'+key,'Original plain silicone key diaphragm',diaphragm,'Controller',2,'rubber',True)
        m.cyl('DukeKeyStem'+key,'Original button underside actuator',2.1,2.4,tuple(_cp(x,y,30.4)),'Controller',3,'black',internal=True)
    web=m.rr(31,56,.5,tuple(_cp(55.5,11,22.65)),6)
    web=web.cut(Part.makeCompound([Part.makeCylinder(4.6,1,_cp(x,y,22.4)) for _,x,y,_ in DUKE_KEYS]))
    web=web.cut(Part.makeCompound([m.parts[k].Shape for k in ['DukeFront','DukePot1_1']]))
    m.feature('DukeSixKeyMat','Original connected six-key silicone web',web,'Controller',2,'rubber',True)
    # Original D-pad assembly is self-contained, with six rubber domes visible in teardown.
    m.cyl('DukeDPadCarrier','Original separate D-pad contact carrier',13.5,.9,tuple(_cp(-39,-27,30.1)),'Controller',2,'black',internal=True)
    for i in range(6):
        a=2*math.pi*i/6;x=-39+7.7*math.cos(a);y=-27+7.7*math.sin(a)
        m.cyl('DukeDirectionContact'+str(i),'D-pad carrier conductive contact',2,.05,tuple(_cp(x,y,31.1)),'Controller',2,'gold',internal=True)
        sh=Part.makeCone(2.6,1.5,3.5,_cp(x,y,31.35)).cut(Part.makeCone(2.1,1,3.7,_cp(x,y,31.25)))
        m.feature('DukeDirectionDome'+str(i),'Original D-pad rubber dome',sh,'Controller',3,'rubber',True)
        m.cyl('DukeDirectionStem'+str(i),'D-pad underside actuator',1.2,3,tuple(_cp(x,y,35)),'Controller',3,'black',internal=True)
    m.cyl('DukeDPadPivot','D-pad central pivot post',1.5,5.8,tuple(_cp(-39,-27,32)),'Controller',3,'black',internal=True)
    for i,x in enumerate([-12,12]):
        m.cyl('DukeSystemContact'+str(i),'Original Start Back conductive contact',2.5,.05,tuple(_cp(x,-36,22.36)),'Controller',1,'gold',internal=True)
        m.cyl('DukeSystemPill'+str(i),'Start Back conductive rubber pill',2,.15,tuple(_cp(x,-36,22.5)),'Controller',1,'black',internal=True)
        sh=Part.makeCone(3.5,2,7,_cp(x,-36,22.9)).cut(Part.makeCone(3,1.5,7.2,_cp(x,-36,22.8)))
        m.feature('DukeSystemDome'+str(i),'Original Start Back silicone diaphragm',sh,'Controller',2,'rubber',True)
        m.cyl('DukeSystemStem'+str(i),'Start Back actuator stem',1.7,7.5,tuple(_cp(x,-36,30.1)),'Controller',3,'black',internal=True)
    q=App.Rotation(V(1,0,0),90)
    for i,z in enumerate([14,29]):
        shell=m.rr(48,7,20,tuple(_cp(0,53,z)),1,q).cut(m.rr(45,4.5,20.4,tuple(_cp(0,53.2,z)),.7,q))
        m.feature('DukeMemorySlot'+str(i),'Original stacked memory-card connector housing',shell,'Controller',1,'black',True)
        for j in range(8):m.box('DukeMemoryPin%d_%d'%(i,j),'Memory-card schematic connector contact',1,10,.12,tuple(_cp((j-3.5)*3,42,z-.1)),'Controller',1,'gold',.03,True)
    _finish(m,16,'duke_carbon_sheet_silicone_dpad_and_memory_slots','补齐原版独立碳接点膜、无导电粒的六键硅胶层、自成一体的六胶碗十字键机构、Start/Back 胶件及双层记忆卡插座；不把后代双板结构移植到 Duke。')

STAGES[16]=stage16


def stage17(m):
    # Original two grip motors; unequal eccentric masses, not four later impulse motors.
    for i,(x,y,r) in enumerate([(-62,-48,9),(62,-48,7)]):
        m.cyl('DukeMotor'+str(i),'Original grip vibration motor',r,12,tuple(_cp(x,y,11.3)),'Controller',-1,'metal',internal=True)
        weight=Part.makeCylinder(r-1,4,_cp(x,y,7)).cut(Part.makeBox(2*r+2,r+1,5,_cp(x-r-1,y,6.5)))
        m.feature('DukeWeight'+str(i),'Original eccentric vibration weight',weight,'Controller',-2,'metal',True)
        m.box('DukeMotorBracket'+str(i),'Original motor retaining strap',r*2+4,2,1.2,tuple(_cp(x,y-3,23.6)),'Controller',0,'metal',.2,True)
        m.box('DukeMotorConnector'+str(i),'Original white PH motor-wire connector',8,5,4,tuple(_cp(-69 if i==0 else 69,-23,22.5)),'Controller',1,'white',.4,True)
        for j in range(2):
            pts=[tuple(_cp(x+j*.9,y,23.55)),tuple(_cp(x+j*.9,-33,26)),tuple(_cp((-69 if i==0 else 69)+j*.9,-26,26))]
            _wire(m,'DukeMotorWire%d_%d'%(i,j),pts,.22,'red' if j==0 else 'black','Controller',1)
    from .atari2600 import _helical_spring
    for i,x in enumerate([-54,54]):
        m.box('DukeTrigger'+str(i),'Original underside analog trigger',20,16,11,tuple(_cp(x,31,3)),'Controller',-2,'black',3)
        m.cyl('DukeTriggerAxle'+str(i),'Original trigger pivot pin',1.2,22,tuple(_cp(x-11,34,16)),'Controller',-1,'metal',axis=(1,0,0),internal=True)
        m.box('DukeTriggerPot'+str(i),'Original trigger potentiometer',7,9,5,tuple(_cp(x,20,14)),'Controller',0,'green',.8,True)
        spring=_helical_spring(2.1,1.5,6,.3);spring.translate(_cp(x,28,14.4))
        m.feature('DukeTriggerSpring'+str(i),'Original analog trigger compression spring approximation',spring,'Controller',0,'metal',True)
        for key in ['DukeBack','DukeFront']:_cut(m,key,m.rr(21,18,17,tuple(_cp(x,31,-1)),3),'Original trigger travel aperture').Refine=False
    for i,(x,y) in enumerate([(-72,30),(72,30),(-78,-8),(78,-8),(-64,-62),(64,-62),(0,-40)]):
        post=Part.makeCylinder(2.4,31,_cp(x,y,4.8)).cut(Part.makeCylinder(1.2,32,_cp(x,y,4.3)))
        post=post.cut(Part.makeCompound([m.parts[k].Shape for k in ['DukeBack','DukeFront']]))
        m.feature('DukeCasePost'+str(i),'Original controller case screw guide',post,'Controller',0,'accent',True)
        _cut(m,'DukeMainPCB',Part.makeCylinder(2.6,2,_cp(x,y,20.8)),'Original controller screw-guide board clearance').Refine=False
        m.cyl('DukeCaseShaft'+str(i),'Original Duke case screw shaft',.9,30,tuple(_cp(x,y,4.9)),'Controller',0,'steel',internal=True)
        m.ring('DukeCaseHead'+str(i),'Original Duke screw head',1.7,.55,.5,tuple(_cp(x,y,4.1)),'Controller',-3,'steel',internal=True)
        _cut(m,'DukeSixKeyMat',Part.makeCylinder(2.6,2,_cp(x,y,22.1)),'Silicone screw guide clearance').Refine=False
        for shell in ['DukeBack','DukeFront']:
            _cut(m,shell,Part.makeCylinder(1.05,38,_cp(x,y,-1)),'Original controller screw bore').Refine=False
        _cut(m,'DukeBack',Part.makeCylinder(1.9,5.9,_cp(x,y,-1)),'Original controller screw head recess').Refine=False
    _finish(m,17,'duke_dual_motors_analog_trigger_springs_and_screws','补充两枚不等偏心块握把电机、PH 接头导线、模拟扳机及压缩回位弹簧、七组壳体固定件；扳机和弹簧按原版结构重构，不表达寿命或力学性能。')

STAGES[17]=stage17


def stage18(m):
    # Wired Duke cable and its detachable breakaway are part of the original kit.
    q=App.Rotation(V(1,0,0),-90)
    m.cyl('DukeCableGrommet','Original Duke cable strain relief',3.3,14,tuple(_cp(0,49,7)),'Controller',0,'black',axis=(0,1,0))
    for key in ['DukeBack','DukeFront']:_cut(m,key,Part.makeCylinder(3.6,15,_cp(0,48,7),V(0,1,0)),'Original wired cable exit').Refine=False
    pts=[tuple(_cp(0,63.5,7)),tuple(_cp(0,87,7)),tuple(_cp(80,104,7)),tuple(_cp(112,87,7)),tuple(_cp(112,-55,7)),tuple(_cp(101,-77,7)),tuple(_cp(37.6,-84,7))]
    _wire(m,'DukeCable',pts,1.7,'black','Controller',0)
    m.box('DukeBreakaway','Original detachable cable breakaway body',28,13,10,tuple(_cp(23,-84,2)),'Controller',0,'black',3)
    m.box('DukeBreakawayMate','Original short breakaway mating sleeve',15,12,9,tuple(_cp(-.5,-84,2.5)),'Controller',0,'black',2.5)
    _wire(m,'DukePlugLead',[tuple(_cp(-8.1,-84,7)),tuple(_cp(-28,-84,7)),tuple(_cp(-32,-104,7)),tuple(_cp(32.4,-104,7))],1.7,'black','Controller',0)
    m.box('DukeConsolePlug','Original proprietary controller cable plug grip',23,15,11,tuple(_cp(44,-104,1.5)),'Controller',0,'black',3)
    sh=m.rr(21,10,10,tuple(_cp(55.7,-104,7)),3,App.Rotation(V(0,0,1),V(1,0,0)))
    void=m.rr(19.6,8.6,10.3,tuple(_cp(55.6,-104,7)),2.5,App.Rotation(V(0,0,1),V(1,0,0)))
    m.feature('DukePlugMetal','Original controller cable hollow metal plug',sh.cut(void),'Controller',0,'metal')
    # Standalone composite A/V cable: original proprietary plug and three RCA ends.
    m.box('AVCableGrip','Original composite A/V cable console-end grip',33,19,11,(-220,25,2),'Accessories',0,'black',3)
    orient=g.rotation((0,-1,0),(0,0,1))
    metal=m.rr(29,8,11,(-220,15.3,7.5),1.5,orient)
    void=m.rr(27.6,6.6,11.2,(-220,15.4,7.5),1,orient)
    m.feature('AVCableMetal','Original proprietary AV cable hollow plug sleeve',metal.cut(void),'Accessories',0,'metal')
    for i,(y,color) in enumerate([(-35,'yellow'),(-13,'white'),(9,'red')]):
        m.cyl('RCAPlugGrip'+str(i),'Composite video or stereo audio molded RCA grip',5,22,(-270,y,7),'Accessories',0,color,axis=(1,0,0))
        m.ring('RCAPlugSleeve'+str(i),'RCA return sleeve',4,3.2,9,(-248,y,7),'Accessories',0,'metal',axis=(1,0,0))
        m.cyl('RCAPlugPin'+str(i),'RCA center signal pin',1.2,11,(-248,y,7),'Accessories',0,'metal',axis=(1,0,0))
        _wire(m,'AVCableBranch'+str(i),[(-271.2,y,7),(-277,y,7+i*4),(-283-i*6,y,7+i*4),(-283-i*6,54+i*6,7+i*4),(-225+i*5,54+i*6,7+i*4),(-225+i*5,35.7,7)],1.1,'black','Accessories',0)
    m.box('ACPlug','Generic original AC cable wall-end body',23,25,13,(-224,105,2),'Accessories',0,'black',3)
    m.box('C7Grip','Original two-pin appliance connector grip',18,23,10,(-274,105,2),'Accessories',0,'black',3)
    _wire(m,'ACAccessory',[(-224,92,7),(-224,76,7),(-274,74,7),(-274,93,7)],1.7,'black','Accessories',0)
    tip=Part.makeCylinder(4,10,V(-277,117,7),V(0,1,0)).fuse(Part.makeCylinder(4,10,V(-271,117,7),V(0,1,0)))
    tip=tip.cut(Part.makeCompound([Part.makeCylinder(1.3,11,V(x,116.5,7),V(0,1,0)) for x in [-277,-271]]))
    m.feature('C7Tip','Original two-pin appliance plug with contact wells',tip,'Accessories',0,'black')
    _finish(m,18,'wired_duke_breakaway_composite_av_and_ac_accessories','完成原版 Duke 有线线缆、可分离接头、专用主机插头及独立复合视频/左右声道 RCA 与交流线缆；墙端仅为通用示意，不指定地区插脚或认证。')

STAGES[18]=stage18


def finalize(model):
    from .deliver import finalize as shared_finalize
    import ImportGui
    configure(model)
    previous=App.ParamGet('User parameter:BaseApp/Preferences/Mod/Part/General').GetInt('WriteSurfaceCurveMode',1)
    Part.setStaticValue('write.surfacecurve.mode',1)
    try:
        report,exploded=shared_finalize(model);console=model.profile['envelope_groups']
        Part.setStaticValue('write.surfacecurve.mode',0)
        ImportGui.export([o for o in exploded.Objects if 'PartID' in o.PropertiesList],str(model.out/'OriginalXbox_Exploded.step'))
        Part.setStaticValue('write.surfacecurve.mode',1)
        model.snapshot('final_hero',assemblies=console+['Controller'])
        model.snapshot('final_console',assemblies=console)
        model.snapshot('final_front',assemblies=console,normal=(0,-1,0))
        model.snapshot('final_back',assemblies=console,normal=(0,1,0))
        model.snapshot('final_internal',assemblies=['Frame','Mainboard','Cooling','Fan','Power','Optical','Storage','Wiring'],exclude=['UpperShield','DVDCover','HDDCover','HDDLabel','HDDLabelMark'])
        model.snapshot('final_board',assemblies=['Mainboard'],normal=(0,0,1))
        model.snapshot('final_thermal',assemblies=['Cooling','Fan'])
        model.snapshot('final_optical',assemblies=['Optical'],exclude=['DVDCover'])
        model.snapshot('final_storage',assemblies=['Storage'],exclude=['HDDCover','HDDLabel','HDDLabelMark'])
        model.snapshot('final_power',assemblies=['Power'])
        model.snapshot('final_controls',assemblies=['Controller'],normal=(.2,-.4,2))
        model.snapshot('final_controller_internal',assemblies=['Controller'],exclude=['DukeFront','DukeBack','DukeJewel','DukeJewelX0','DukeJewelX1','DukeJewelMark','DukeStickDome0','DukeStickDome1','DukeStickCap0','DukeStickCap1','DukeCable','DukePlugLead','DukeBreakaway','DukeBreakawayMate','DukeConsolePlug','DukePlugMetal'],normal=(.2,-.4,2))
        def exploded_view(name,groups,normal,up):
            App.setActiveDocument(exploded.Name);Gui.activateView('Gui::View3DInventor',True)
            objs=[o for o in exploded.Objects if 'Assembly' in o.PropertiesList and o.Assembly in groups]
            g.set_visible_components(exploded,objs);q=g.rotation(normal,up);shape=Part.makeCompound([o.Shape for o in objs]);shape.Placement=App.Placement(V(),q.inverted()).multiply(shape.Placement)
            b=shape.optimalBoundingBox(False,False);span=max(b.YLength,b.XLength*1700/2300)*1.14
            return g.render(model.out/'previews'/(name+'.png'),normal=normal,up=up,target=tuple(q.multVec(b.Center)),span=span,size=(2300,1700))
        exploded_view('final_exploded',console,(.6,-1,.7),(0,0,1))
        exploded_view('final_exploded_body',console,(.6,-1,.7),(0,0,1))
        exploded_view('final_exploded_controller',['Controller'],(1.3,-.3,.4),(0,1,0))
        for o in exploded.Objects:
            if 'Assembly' in o.PropertiesList:o.Visibility=True
        exploded.save();model.doc.save();return report,exploded
    finally:Part.setStaticValue('write.surfacecurve.mode',previous)
