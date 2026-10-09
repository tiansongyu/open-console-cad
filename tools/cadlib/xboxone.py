"""Original 2013 Xbox One 1540: staged native structure study."""
import FreeCAD as App
import Part
from .core import V
from . import geometry as g


def _finish(m,n,slug,summary,normal=(.45,-1.2,.8)):
    m.doc.recompute()
    for obj in m.parts.values():
        assert obj.Shape.isValid() and obj.Shape.Solids,obj.PartID
        obj.Shape.check(True)
    m.profile['stages']=n
    m.checkpoint(n,slug,summary)
    m.snapshot(f'{n:02}_{slug}',normal=normal)


def stage01(m):
    m.colors.update(gloss=(.11,.115,.12),matte=(.17,.175,.18),chrome=(.65,.67,.69))
    m.params.set('A3','Depth (Y)');m.params.set('A4','Height (Z)')
    m.native('BottomShell','Original lower case · editable width',343,263,1.2,1.8,(0,0,2),'Body',-7,'matte',expr={'Width':'Parameters.Width'})
    m.native('GlossTop','Separate glossy left top panel',170.8,262.6,.5,1.8,(-85.7,0,78.2),'Body',7,'gloss')
    m.native('VentTop','Separate matte right top grille panel',171.6,262.6,.5,1.8,(85.5,0,78.2),'Body',7,'matte')
    for key,x in [('LeftSide',-170.4),('RightSide',170.4)]:
        m.box(key,'Original separate side grille wall',2.2,258.2,74.2,(x,0,3.9),'Body',0,'matte',.3)
    m.box('FrontFascia','Original front fascia',338.2,2.2,74.2,(0,-130.4,3.9),'Body',1,'gloss',.3)
    m.box('RearFascia','Original rear closure',338.2,2.2,74.2,(0,130.4,3.9),'Body',1,'matte',.3)
    for i,(x,y) in enumerate([(-151,-111),(151,-111),(-151,111),(151,111)]):
        m.box('Foot'+str(i),'Independent lower rubber foot',14,10,2,(x,y,0),'Frame',-8,'rubber',2)
    _finish(m,1,'original_native_split_black_enclosure','采用 Microsoft 官方原版一列 343×263×80 mm 包络建立原生底壳、分离的左侧亮面顶盖与右侧通风顶盖、侧壁、前后面板及四个支脚；保留可编辑草图与拉伸。局部几何为结构学习近似，通风、接口与内部构造后续逐轮加入。')


STAGES={1:stage01}


def stage02(m):
    front=g.rotation((0,-1,0),(0,0,1))
    m.cut('FrontFascia',m.rr(146,4.8,4,(-84,-128.8,41),.8,front),'Original slot-loading optical opening').Refine=False
    # Thin trims sit inside the slot so the opening remains through the shell.
    for key,z in [('SlotUpperTrim',43.05),('SlotLowerTrim',38.95)]:
        m.box(key,'Separate silver optical slot lip',145,.5,.6,(-84,-130.8,z),'Optical',2,'chrome',.15,orient=front)
    m.cut('FrontFascia',Part.makeCylinder(7.65,4,V(146,-128.8,55),V(0,-1,0)),'Capacitive power light aperture').Refine=False
    m.cyl('PowerLight','Front capacitive power light',7.5,.12,(146,-131.3,55),'Controls',2,'white',axis=(0,-1,0))
    # Generic X mark is a shallow mechanical study marking.
    marks=[]
    for i,angle in enumerate([45,-45]):
        mark=m.rr(2,13.1,.018,(0,0,0),.25);mark.rotate(V(),V(0,0,1),angle)
        mark.Placement=App.Placement(V(146,-131.441,55),front).multiply(mark.Placement)
        marks.append(mark)
    m.feature('PowerX','Power light cross study marking',marks[0].fuse(marks[1]).removeSplitter(),'Controls',3,'gloss')
    m.box('EjectTouch','Separate capacitive eject marker',3.5,3,.018,(-6,-131.47,42),'Controls',2,'chrome',.3,orient=front)
    m.cut('FrontFascia',m.parts['EjectTouch'].Shape,'Inlaid eject marking').Refine=False
    # Fine lower seam is a real shallow recess, not a second intersecting panel.
    m.cut('FrontFascia',m.rr(336,.6,.45,(0,-131.65,25),.1,g.rotation((0,1,0),(0,0,1))),'Original lower front fascia seam').Refine=False
    m.label('TopStudyMark','XBOX ONE',4.1,(-158,-117,79.982),'Body',8,'chrome')
    m.cut('GlossTop',m.parts['TopStudyMark'].Shape,'Inlaid top study marking').Refine=False
    _finish(m,2,'slot_loading_front_and_capacitive_controls','建立左侧吸入式光盘槽、独立银色槽边、电容出盘标识与右侧电源导光；亮面顶盖文字为结构学习标识，前面板下部接缝采用真实浅切槽。')


STAGES[2]=stage02


def stage03(m):
    # Photo-guided diagonal grille pitch; openings are real through cuts.
    inset=m.rr(163.6,254.6,5,(85.5,0,77),.3)
    slots=[]
    for y in range(-225,226,4):
        tool=m.rr(340,1.7,4,(85.5,y,77.2),.15)
        tool.rotate(V(85.5,0,0),V(0,0,1),-30)
        clipped=tool.common(inset)
        if clipped.Solids:slots.append(clipped)
    m.cut('VentTop',slots,'Diagonal open upper grille field').Refine=False
    for key,x in [('LeftSide',-173),('RightSide',168.6)]:
        side=[]
        for y in range(-111,112,5):
            if key=='LeftSide' and y<-62:continue
            tool=Part.makeBox(5,1.8,50,V(x,y-.9,14))
            tool.rotate(V(x,y,39),V(1,0,0),22)
            side.append(tool)
        m.cut(key,side,'Original diagonal side ventilation').Refine=False
    rear=[]
    for x in range(-88,159,6):
        points=[V(x-4,128,53),V(x-2.1,128,53),V(x+5.9,128,70),V(x+4,128,70)]
        rear.append(Part.Face(Part.makePolygon(points+[points[0]])).extrude(V(0,5,0)))
    m.cut('RearFascia',rear,'Original upper rear diagonal exhaust grille').Refine=False
    _finish(m,3,'diagonal_top_side_and_rear_ventilation','右侧顶盖、两侧面与后部上缘的斜向通风孔均为贯穿实体几何；孔距和肋宽按原版照片作近似，左侧前部保留 USB 与配对区域。')


STAGES[3]=stage03


def _rear_openings(m):
    rear=g.rotation((0,1,0),(0,0,1))
    return [m.rr(w+.8,h+.8,9,(x,123.4,z),.4,rear) for x,z,w,h in [(134,28,23,12),(105,26,15.6,6.6),(80,31,12,12),(55,26,15.6,6.6),(27,23,14.4,6.7),(27,35,14.4,6.7),(3,28,18,13),(-32,28,9,9),(-61,28,16,14)]]


def stage04(m):
    from .ps5 import _usb_a
    from .ps4 import _keyed_rear_port
    rear=g.rotation((0,1,0),(0,0,1));y=118.3
    m.cut('RearFascia',_rear_openings(m),'Original rear connector apertures').Refine=False
    for key,x in [('HDMIOut',105),('HDMIIn',55)]:
        z=26
        outer=_keyed_rear_port(15.6,6.6,12.5,x,y,z,1.3)
        inner=_keyed_rear_port(14.85,5.85,12.9,x,y-.2,z,1.05)
        m.feature(key+'Shield',key+' formed shield',outer.cut(inner),'Ports',0,'metal')
        m.box(key+'Carrier',key+' insulating back',12,.8,4.8,(x,y+.5,z-2.4),'Ports',0,'black',.15,True)
        m.box(key+'Tongue',key+' contact tongue',11.7,8.7,.72,(x,y+7,z-.36),'Ports',0,'black',.1,True)
        for row,num in enumerate([10,9]):
            for i in range(num):m.box(key+'Contact'+str(row)+'_'+str(i),'Separate HDMI contact',.28,6,.09,(x+(i-(num-1)/2)*1.1,y+7.1,z+(.4 if row==0 else -.49)),'Ports',0,'gold',.02,True)
    for i,z in enumerate([23,35]):_usb_a(m,'RearUSB'+str(i),27,118.8,z)
    x,z=-61,28
    m.feature('LANShield','Ethernet formed shield',m.rr(16,14,12.5,(x,y,z),.4,rear).cut(m.rr(14.5,12.4,12.9,(x,y-.2,z),.2,rear)),'Ports',0,'metal')
    m.box('LANCarrier','Ethernet rear insulator',14.1,1,11.6,(x,y+.7,z-5.8),'Ports',0,'black',.2,True)
    for i in range(8):m.box('LANContact'+str(i),'Ethernet spring terminal',.35,7.5,.23,(x+(i-3.5)*1.35,y+6.5,z-3.7),'Ports',0,'gold',.04,True)
    for i,dx in enumerate([-6.2,6.2]):m.box('LANLight'+str(i),'Ethernet status light',1.5,1,1.5,(x+dx,131,z+3.8),'Ports',1,'led',.2)
    x,z=80,31
    m.feature('OpticalSocket','TOSLINK square receptacle',m.rr(12,12,12,(x,118.8,z),.4,rear).cut(m.rr(9,9,12.4,(x,118.6,z),.2,rear)),'Ports',0,'matte')
    m.box('OpticalShutter','Independent TOSLINK dust flap',8.6,.4,8.6,(x,130.4,z-4.3),'Ports',1,'black',.15)
    m.cyl('OpticalEmitter','Separate optical emitter envelope',1.2,1,(x,119.8,z),'Ports',0,'red',axis=(0,1,0),internal=True)
    m.ring('IRSocket','Separate IR-out barrel receptacle',4.3,1.85,9,(-32,121.8,28),'Ports',0,'matte',axis=(0,1,0))
    m.ring('IRSocketContact','Independent IR-out sleeve',1.75,1.5,7,(-32,123.5,28),'Ports',0,'metal',axis=(0,1,0),internal=True)
    dc=m.rr(23,12,11,(134,119.8,28),3,rear)
    dc=dc.cut(Part.makeCompound([Part.makeCylinder(3.6,11.4,V(x,119.6,28),V(0,1,0)) for x in [128.5,139.5]]))
    m.feature('DCInlet','Original external-supply DC inlet',dc,'Ports',0,'matte')
    for i,x in enumerate([128.5,139.5]):m.ring('DCPowerContact'+str(i),'Separate original DC contact envelope',1.7,.75,7,(x,123,28),'Ports',0,'metal',axis=(0,1,0),internal=True)
    x,z=3,28
    mouth=m.rr(18,13,12,(x,118.8,z),1.4,rear)
    cavities=[m.rr(14.8,4.2,12.4,(x,118.6,z+3),.25,rear),m.rr(14.8,5,12.4,(x,118.6,z-2.8),.3,rear)]
    m.feature('KinectSocket','Original divided Kinect proprietary receptacle',mouth.cut(Part.makeCompound(cavities)),'Ports',0,'matte')
    # Visible 5 + 8 contact grouping; schematic, not electrical pin assignment.
    for row,num in enumerate([5,4,4]):
        for i in range(num):m.box('KinectPortContact'+str(row)+'_'+str(i),'Separate Kinect contact envelope',.5,6,.18,(x+(i-(num-1)/2)*2.4,125.5,z+[3,-1.2,-4.3][row]),'Ports',0,'gold',.03,True)
    for key,text,x in [('HDMIOutMark','HDMI OUT',116),('HDMIInMark','HDMI IN',64),('KinectMark','KINECT',12),('LANMark','LAN',-57)]:
        m.label(key,text,1.8,(x,131.46,43),'Body',1,'chrome',rotation=rear)
        m.cut('RearFascia',m.parts[key].Shape,'Inlaid rear port study legend').Refine=False
    _finish(m,4,'original_rear_io_and_separate_contacts','按原版背面照片加入 DC、HDMI 输出与输入、光纤音频、双 USB 3.0、专用 Kinect、IR 与网口；独立接口内腔、触点、光纤挡片及状态灯均不与外壳重叠。Kinect 为 5+8 触点分区学习近似，不作为电气引脚图。',normal=(-.4,1.2,.6))


STAGES[4]=stage04


def stage05(m):
    from .ps5 import _usb_a
    prior=set(m.parts)
    _usb_a(m,'SideUSB',0,0,31)
    # Rotate a standard upward-facing rear mouth onto the physical left wall.
    turn=App.Placement(V(-159.2,-83,0),App.Rotation(V(0,0,1),90))
    for key in set(m.parts)-prior:
        obj=m.parts[key];obj.Placement=turn.multiply(obj.Placement);obj.FlatPlacement=obj.Placement
    side=g.rotation((-1,0,0),(0,0,1))
    m.cut('LeftSide',m.rr(15.4,7.7,7,(-166,-83,31),.5,side),'Original side USB 3.0 opening').Refine=False
    m.cut('LeftSide',m.rr(5.5,12.5,5,(-168,-109,38),1.4,side),'Original side pairing button opening').Refine=False
    m.box('PairingKey','Separate original side wireless pairing key',5,12,.55,(-170.85,-109,38),'Controls',1,'matte',1.2,orient=side)
    m.native('ChassisFloor','Native sheet-metal chassis floor',330,250,.7,.7,(0,0,5),'Frame',-5,'metal')
    for key,x in [('ChassisLeft',-164.65),('ChassisRight',164.65)]:
        m.box(key,'Separate bent chassis side wall',.7,247,63,(x,0,5.8),'Frame',0,'metal',.1,True)
    for key,y in [('ChassisFront',-124.65),('ChassisRear',124.65)]:
        m.box(key,'Separate bent chassis end wall',328,.7,63,(0,y,5.8),'Frame',0,'metal',.1,True)
    m.cut('ChassisFront',m.rr(147,5.8,5,(-84,-122.8,41),1,g.rotation((0,-1,0),(0,0,1))),'Optical path through chassis').Refine=False
    m.cut('ChassisRear',_rear_openings(m)+[m.rr(270,22,5,(28,123,62),.3,g.rotation((0,1,0),(0,0,1)))],'Rear I/O and airflow through chassis').Refine=False
    m.cut('ChassisLeft',m.rr(16,8.3,9,(-159,-83,31),.5,side),'Side USB through metal').Refine=False
    for key,x in [('ChassisLeft',-165.2),('ChassisRight',164.1)]:
        holes=[Part.makeBox(1.5,3,36,V(x,y,22)) for y in range(-60,115,7)]
        m.cut(key,holes,'Side chassis air slots').Refine=False
    for i,(x,y) in enumerate([(-145,-103),(-145,100),(145,-103),(145,100),(0,-103),(0,100)]):
        m.ring('BoardStandoff'+str(i),'Independent motherboard support',2.6,1.2,6.15,(x,y,5.8),'Frame',-3,'metal',internal=True)
    _finish(m,5,'side_usb_pairing_and_native_chassis','补齐原版左侧 USB 3.0 与配对键，加入原生底板、四片折边框壁和主板支座；接口、光盘路径与通风均切穿塑料和金属层。')


STAGES[5]=stage05


def stage06(m):
    mounts=[(-145,-103),(-145,100),(145,-103),(145,100),(0,-103),(0,100)]
    board=m.rr(315,237,1.6,(0,0,12.1),2)
    board=board.cut(Part.makeCompound([Part.makeCylinder(1.5,2,V(x,y,11.9)) for x,y in mounts]))
    m.feature('Mainboard','Original 1540 green motherboard laminate',board,'Mainboard',0,'pcb',True)
    for i,(x,y) in enumerate(mounts):m.ring('BoardMountLand'+str(i),'Independent motherboard mounting land',2.7,1.55,.035,(x,y,13.735),'Mainboard',0,'gold',internal=True)
    for key,x,y,w,h,t in [('APU',80,-40,48,48,2.5),('Southbridge',-20,60,24,24,2.2),('EMMC',-48,70,14,18,1.3),('FlashController',-74,70,10,10,1.1)]:
        m.box(key+'Substrate','Separate '+key+' BGA substrate',w,h,.6,(x,y,14.05),'Mainboard',0,'pcb',.3,True)
        m.box(key,key+' package envelope',w-1,h-1,t,(x,y,14.75),'Mainboard',1,'black',.3,True)
        m.label(key+'Mark',key,2,(x-w/2+2,y-1,14.75+t+.02),'Mainboard',1,'white')
    m.box('APUThermal','Independent APU thermal interface',30,30,.3,(80,-40,17.35),'Cooling',2,'thermal',.5,True)
    # Sixteen DDR3 packages appear around three sides of the original APU.
    positions=[(37,-75+i*18) for i in range(5)]+[(123,-75+i*18) for i in range(5)]+[(47+i*13.2,12) for i in range(6)]
    for i,(x,y) in enumerate(positions):
        m.box('DDR3Substrate'+str(i),'Separate original DDR3 BGA carrier',11.5,14.5,.3,(x,y,14),'Mainboard',0,'pcb',.2,True)
        m.box('DDR3'+str(i),'Original sixteen-package DDR3 memory envelope',11.1,14.1,1.1,(x,y,14.4),'Mainboard',1,'black',.2,True)
    _finish(m,6,'original_apu_sixteen_ddr3_and_bridge','按原版主板照片加入原生机架内独立 PCB、APU、十六枚 DDR3、南桥及 eMMC/闪存控制器封装；封装与基板分离、散热界面独立，未套用 One S/X 的芯片布局。')


STAGES[6]=stage06


def stage07(m):
    # Power devices follow the open right and rear board regions in the teardown.
    for i,(x,y) in enumerate([(145,-70),(145,-40),(145,-10),(98,43),(72,43),(46,43)]):
        m.box('VRMInductor'+str(i),'Separate regulator inductor enclosure',9,9,5,(x,y,14.1),'Mainboard',1,'thermal',.5,True)
        m.box('VRMPackage'+str(i),'Separate regulator power-stage package',6,7,1.3,(x-11,y,14.1),'Mainboard',1,'black',.2,True)
        for j,dy in enumerate([-4,4]):m.box('VRMTerminal'+str(i)+'_'+str(j),'Independent inductor termination',6,1,.3,(x,y+dy,13.75),'Mainboard',0,'metal',.1,True)
    for i,(x,y) in enumerate([(151,-89),(151,-56),(151,-24),(151,9),(116,42),(86,58),(60,58),(34,58)]):
        m.cyl('BulkCap'+str(i),'Separate power-filter capacitor',3.2,8,(x,y,14.1),'Mainboard',1,'black',internal=True)
        m.cyl('BulkCapTop'+str(i),'Independent capacitor vent top',2.9,.12,(x,y,22.25),'Mainboard',1,'metal',internal=True)
        for j,dx in enumerate([-1.1,1.1]):m.cyl('BulkCapLead'+str(i)+'_'+str(j),'Separate capacitor lead',.23,.27,(x+dx,y,13.77),'Mainboard',0,'metal',internal=True)
    occupied=[o.Shape.BoundBox for k,o in m.parts.items() if o.Assembly=='Mainboard' and k!='Mainboard']
    candidates=[]
    for y in range(-106,106,10):
        for x in range(-145,150,11):
            if any(b.XMin-2.4<x<b.XMax+2.4 and b.YMin-1.3<y<b.YMax+1.3 for b in occupied):continue
            if 12<x<151 and -99<y<23:continue # sink posts and primary signal region
            if abs(x)<14 and y>65:continue # cable-header corridor
            candidates.append((x,y))
    for i,(x,y) in enumerate(candidates[::3]):
        m.box('Passive'+str(i),'Photo-guided schematic passive body',2,1,.5,(x,y,13.85),'Mainboard',0,'thermal' if i%3 else 'black',.08,True)
        for j,dx in enumerate([-1.3,1.3]):m.box('PassiveEnd'+str(i)+'_'+str(j),'Separate passive termination',.45,1.04,.55,(x+dx,y,13.83),'Mainboard',0,'metal',.04,True)
    for i,(x,y) in enumerate([(x,y) for x in range(-125,136,26) for y in [-80,-50,30,70]]):
        if 45<x<115 and -80<y<0:continue
        m.box('RearPassive'+str(i),'Independent backside passive body',2.2,1.1,.55,(x,y,11.4),'Mainboard',-1,'thermal',.08,True)
        for j,dx in enumerate([-1.4,1.4]):m.box('RearPassiveEnd'+str(i)+'_'+str(j),'Independent backside passive termination',.4,1.14,.6,(x+dx,y,11.38),'Mainboard',-1,'metal',.03,True)
    _finish(m,7,'mainboard_power_stages_and_two_sided_passives','补充供电电感、功率封装、圆柱电容和双面分布的分离无源件，避开主要封装、固定孔及散热器区域；数量、器件尺寸与分布为照片指导的布局学习，不声称原厂 BOM 或电路。')
    m.snapshot('07_mainboard_detail',assemblies=['Mainboard'],normal=(.2,-.4,1.8))


STAGES[7]=stage07


def _heatpipe(y,radius):
    # Three horizontal U routes under the fin field, matching the visible copper bends.
    x0,x1=29,131;z=22.4
    edges=[Part.makeLine(V(x0,y,z),V(x1,y,z)),Part.Arc(V(x1,y,z),V(x1+6,y+6,z),V(x1,y+12,z)).toShape(),Part.makeLine(V(x1,y+12,z),V(x0,y+12,z))]
    path=Part.Wire(edges)
    return path.makePipeShell([Part.Wire([Part.makeCircle(radius,V(x0,y,z),V(1,0,0))])],True,False)


def stage08(m):
    m.native('APUColdplate','Native shared APU heatsink base',111,98,.6,3.8,(80,-40,17.85),'Cooling',2,'metal')
    clears=[]
    for i,y in enumerate([-80,-50,-20]):
        m.feature('APUHeatpipe'+str(i),'Separate original three-route copper heatpipe study',_heatpipe(y,1.65),'Cooling',3,'copper',True)
        clears.append(_heatpipe(y,1.8))
    clear=Part.makeCompound(clears)
    m.cut('APUColdplate',clear,'Separate heatpipe grooves in native coldplate').Refine=False
    for i in range(48):
        fin=m.rr(.65,96,26,(28.3+i*2.2,-40,21.8),.08).cut(clear)
        m.feature('APUFin'+str(i),'Separate original heatsink fin study',fin,'Cooling',3,'metal',True)
    posts=[(45,-75),(45,-5),(115,-75),(115,-5)]
    holes=[Part.makeCylinder(1.55,15,V(x,y,10)) for x,y in posts]
    m.cut('Mainboard',holes,'Four independent heatsink clamp passages').Refine=False
    m.cut('APUColdplate',holes,'Heatsink mounting post clearance').Refine=False
    for i,(x,y) in enumerate(posts):
        m.cyl('APUClampPost'+str(i),'Separate heatsink clamp post',1.3,10,(x,y,10),'Cooling',-2,'metal',internal=True)
        m.ring('APUClampWasher'+str(i),'Independent insulating clamp washer',2.2,1.5,.35,(x,y,11.6),'Cooling',-1,'black',internal=True)
    arms=[]
    for a in [-45,45]:
        arm=m.rr(102,5,.8,(0,0,0),1.5);arm.rotate(V(),V(0,0,1),a);arm.translate(V(80,-40,9));arms.append(arm)
    clamp=arms[0].fuse(arms[1]).removeSplitter().cut(Part.makeCompound([Part.makeCylinder(1.55,2,V(x,y,8.5)) for x,y in posts]))
    m.feature('APUXClamp','Separate original underside X spring clamp',clamp,'Cooling',-3,'metal',True)
    _finish(m,8,'three_heatpipes_fin_stack_and_underside_x_clamp','加入原生 APU 底座、三条铜热管、独立鳍片、导热界面和背面 X 形夹具；热管与金属件采用真实分离通道，支柱穿过主板孔。鳍片数量及局部弯管路径为结构学习近似。')
    m.snapshot('08_cooling_stack',assemblies=['Cooling'],normal=(.5,-.7,1.3))


STAGES[8]=stage08


def stage09(m):
    import math
    x,y,z=80,-40,49
    frame=m.rr(112,112,25,(x,y,z),5).cut(Part.makeCylinder(53.5,25.4,V(x,y,z-.2)))
    for dx in [-50,50]:
        for dy in [-50,50]:frame=frame.cut(Part.makeCylinder(1.6,25.4,V(x+dx,y+dy,z-.2)))
    m.feature('MainFanFrame','Original 112 mm axial-fan frame study',frame,'Cooling',4,'matte',True)
    for i,a in enumerate([45,135,225,315]):
        bar=m.rr(38,2,1.5,(34,0,0),.4);bar.rotate(V(),V(0,0,1),a);bar.translate(V(x,y,72.1))
        m.feature('FanSupport'+str(i),'Independent fan motor-support arm',bar,'Cooling',4,'matte',True)
    m.ring('FanDriverPCB','Separate fan driver board',13,1.2,.7,(x,y,50),'Cooling',4,'pcb',internal=True)
    m.cyl('FanShaft','Separate fan shaft',.9,23,(x,y,49.4),'Cooling',4,'metal',internal=True)
    for i,zz in enumerate([51,68]):m.ring('FanBearing'+str(i),'Independent fan bearing',2.5,1.15,2,(x,y,zz),'Cooling',4,'metal',internal=True)
    m.ring('FanStator','Separate fan stator core',4.2,2.8,11,(x,y,54),'Cooling',4,'metal',internal=True)
    for i in range(6):
        a=i*math.pi/3
        m.ring('FanCoil'+str(i),'Separate fan stator winding envelope',1.8,.75,9,(x+7*math.cos(a),y+7*math.sin(a),55),'Cooling',4,'copper',internal=True)
    m.ring('FanRotorMagnet','Separate rotor magnet ring',11.7,10.2,15,(x,y,53),'Cooling',4,'black',internal=True)
    m.ring('FanHub','Separate axial fan rotor hub',15,12.2,19,(x,y,51.6),'Cooling',4,'matte',internal=True)
    m.ring('FanHubCap','Separate fan hub top cap',15,1.2,1,(x,y,70.8),'Cooling',4,'matte',internal=True)
    for i in range(7):
        wires=[]
        for zz,twist in [(53,0),(68,21)]:
            pts=[]
            for r,a in [(15.3,-13),(51,-11),(51,10),(15.3,13)]:
                angle=math.radians(a+twist+i*360/7);pts.append(V(x+r*math.cos(angle),y+r*math.sin(angle),zz))
            wires.append(Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges))
        m.feature('FanBlade'+str(i),'Separate twisted axial fan blade study',Part.makeLoft(wires,True,False).cut(Part.makeCylinder(15.15,30,V(x,y,48))),'Cooling',4,'matte',True)
    _finish(m,9,'single_112mm_fan_and_separate_motor','加入原版单个 112 mm 轴流风扇，框架、扭转叶片、支架、轴承、转轴、转子、磁环、定子线圈与驱动板逐件分离；叶片曲率和电机尺寸为示意，不作为动平衡或气动设计。')
    m.snapshot('09_single_fan',assemblies=['Cooling'],normal=(.4,-.6,1.2))


STAGES[9]=stage09


def stage10(m):
    x,y=-83,-40
    shell=m.rr(145,167,23,(x,y,29),2).cut(m.rr(142.8,164.8,23.4,(x,y,28.8),1.3))
    shell=shell.cut(m.rr(146,5.5,5,(x,-125,41),.8,g.rotation((0,1,0),(0,0,1))))
    m.feature('OpticalFrame','Separate slot-load Blu-ray side enclosure',shell,'Optical',2,'metal',True)
    m.box('OpticalFloor','Separate optical-drive bottom plate',142.4,164.4,.6,(x,y,28.2),'Optical',1,'metal',1.2,True)
    m.box('OpticalCover','Independent Blu-ray upper metal lid',145,167,.65,(x,y,52.2),'Optical',4,'metal',2,True)
    m.box('OpticalStudyLabel','Blank optical-drive study label',62,40,.06,(x-13,y+33,52.92),'Optical',4,'white',.8,True)
    m.label('OpticalStudyMark','BD / CAD STUDY',3,(x-39,y+30,53.01),'Optical',4,'black')
    m.box('OpticalPCB','Separate optical-drive controller PCB',132,153,.8,(x,y,29.1),'Optical',1,'pcb',1,True)
    for i,(dx,dy,w,h) in enumerate([(-42,47,19,19),(36,40,13,13),(36,-38,11,8)]):m.box('OpticalIC'+str(i),'Independent optical controller package',w,h,1.3,(x+dx,y+dy,30.15),'Optical',1,'black',.4,True)
    for i,dx in enumerate([-64,64]):
        m.box('OpticalDeckRail'+str(i),'Independent stamped drive mechanism rail',4,143,1,(x+dx,y,32),'Optical',2,'metal',.5,True)
    m.cyl('OpticalSpindleMotor','Independent optical spindle motor',12,3.5,(x,y-20,33.2),'Optical',2,'metal',internal=True)
    m.cut('OpticalSpindleMotor',Part.makeCylinder(1.3,4,V(x,y-20,33)),'Independent spindle-shaft bore').Refine=False
    m.cyl('OpticalSpindleShaft','Separate spindle shaft',1.1,8,(x,y-20,33),'Optical',2,'metal',internal=True)
    m.ring('OpticalSpindleTable','Separate disc support table; no media included',16,1.4,1.2,(x,y-20,39),'Optical',3,'matte',internal=True)
    m.ring('OpticalClamp','Independent magnetic disc clamp',13,1.4,1.2,(x,y-20,45),'Optical',3,'matte',internal=True)
    for i,dx in enumerate([-18,18]):m.cyl('PickupGuide'+str(i),'Independent optical pickup guide rod',1.15,67,(x+dx,y-8,35),'Optical',2,'metal',axis=(0,1,0),internal=True)
    m.box('PickupCarriage','Separate optical pickup carriage',29,21,4,(x,y+26,33),'Optical',2,'matte',1,True)
    m.ring('PickupLensBarrel','Separate optical pickup lens barrel',4,2.7,2,(x,y+26,37.2),'Optical',3,'matte',internal=True)
    m.cyl('PickupLens','Independent optical lens envelope',2.5,.55,(x,y+26,39.35),'Optical',3,'blue',internal=True)
    m.cyl('PickupLeadScrew','Separate optical sled leadscrew',1.15,69,(x+24,y-9,35),'Optical',2,'metal',axis=(0,1,0),internal=True)
    m.cyl('PickupMotor','Independent optical sled motor',4.3,10,(x+24,y+61,35),'Optical',2,'metal',axis=(0,1,0),internal=True)
    for i,z in enumerate([37,44.9]):
        m.cyl('LoadingRoller'+str(i),'Separate slot-loading rubber roller',2.4,119,(x-59.5,-113,z),'Optical',3,'rubber',axis=(1,0,0),internal=True)
        m.cyl('LoadingAxle'+str(i),'Independent loading-roller axle end',.85,6,(x+60,-113,z),'Optical',3,'metal',axis=(1,0,0),internal=True)
    m.cyl('LoadingMotor','Separate slot-loading drive motor',4,14,(-135,-88,38),'Optical',2,'metal',axis=(0,1,0),internal=True)
    for i,(dx,dy,r) in enumerate([(-52,-60,4),(-46,-60,1.8),(-42,-60,1.8)]):m.cyl('LoadingGear'+str(i),'Separate slot-loading gear envelope',r,1.1,(x+dx,y+dy,42),'Optical',3,'white',internal=True)
    m.box('PickupFlex','Independent optical pickup flex ribbon',13,43,.14,(x+42,y+12,32),'Optical',2,'copper',.5,True)
    _finish(m,10,'slot_load_bluray_pickup_and_loading_mechanism','建立吸入式 Blu-ray 机构的分离盖板、底板、控制板、主轴、夹盘、激光滑架、导杆、丝杆、驱动电机与上下进盘滚轮；未放入光盘，机构位置与齿轮为学习近似。')
    m.snapshot('10_optical_mechanism',assemblies=['Optical'],exclude=['OpticalCover','OpticalStudyLabel','OpticalStudyMark'],normal=(.4,-.6,1.5))


STAGES[10]=stage10


def stage11(m):
    x,y=82,77
    tray=m.rr(108,79,3,(x,y,43),2).cut(m.rr(102,73,3.4,(x,y,42.8),1.3))
    m.feature('HDDTray','Separate original plastic hard-drive cradle',tray,'Storage',3,'matte',True)
    m.box('HDDBottomSupport','Independent hard-drive support plate',105,76,.6,(x,y,42),'Storage',2,'matte',1,True)
    base=m.rr(100,69.85,6.1,(x,y,47.7),2).cut(m.rr(97.6,67.4,6.4,(x,y,47.5),1.2))
    m.feature('HDDBase','Original 500 GB 2.5-inch drive side frame',base,'Storage',3,'metal',True)
    m.box('HDDFloor','Independent hard-drive floor',97.2,67,.55,(x,y,47),'Storage',3,'metal',1.1,True)
    m.box('HDDCover','Independent hard-drive metal lid',100,69.85,.6,(x,y,54),'Storage',4,'metal',2,True)
    m.box('HDDLabel','Blank drive-study label',76,49,.05,(x,y,54.65),'Storage',4,'white',1,True)
    m.label('HDDMark','500 GB / CAD',3.5,(x-28,y-1,54.73),'Storage',4,'black')
    m.box('HDDPCB','Separate hard-drive control PCB',90,61,.8,(x,y,43.5),'Storage',2,'pcb',1,True)
    for i,(dx,dy,w,h) in enumerate([(-26,-15,17,17),(16,-12,13,10),(26,16,9,9)]):m.box('HDDChip'+str(i),'Separate HDD controller envelope',w,h,1.15,(x+dx,y+dy,44.55),'Storage',2,'black',.3,True)
    m.ring('HDDPlatter','Independent disk platter envelope',30,7.4,.6,(x-16,y,49.8),'Storage',3,'metal',internal=True)
    m.cyl('HDDSpindle','Independent hard-drive spindle',7,2.3,(x-16,y,48.1),'Storage',3,'metal',internal=True)
    m.cyl('HDDActuatorPivot','Independent head actuator pivot',4.2,2.5,(x+31,y-17,48.1),'Storage',3,'metal',internal=True)
    pts=[V(x+a,y+b,51) for a,b in [(30,-20),(33,-14),(-2,12),(-8,14),(-10,10)]]
    m.feature('HDDActuatorArm','Independent head actuator arm study',Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,.6)),'Storage',4,'metal',True)
    m.box('HDDHead','Independent head slider envelope',2,2,.3,(x-8,y+12,50.6),'Storage',3,'black',.2,True)
    m.feature('HDDVoiceCoil','Separate hard-drive actuator coil',m.rr(12,13,.65,(x+31,y+11,51),2).cut(m.rr(8,9,1,(x+31,y+11,50.8),1)),'Storage',4,'copper',True)
    m.box('HDDMagnet','Independent actuator magnet',13,14,.8,(x+31,y+11,52),'Storage',4,'black',2,True)
    for i,(dx,dy) in enumerate([(-44,-28),(-44,28),(44,-28),(44,28)]):
        m.cyl('HDDScrew'+str(i),'Separate drive cover screw-head envelope',1.3,.3,(x+dx,y+dy,54.8),'Storage',4,'metal',internal=True)
    _finish(m,11,'internal_500gb_hard_drive_and_cradle','建立内置 500 GB 硬盘及塑料托架，分离金属框、盖板、底板、控制板、盘片、主轴、磁头臂、音圈与磁体；盘片数量和磁头仅为机构学习示意，不表示真实数据或容量计算。')
    m.snapshot('11_hard_drive_open',assemblies=['Storage'],exclude=['HDDCover','HDDLabel','HDDMark'],normal=(.3,-.6,1.6))


STAGES[11]=stage11


def stage12(m):
    front=g.rotation((0,-1,0),(0,0,1))
    m.box('FrontRFPCB','Separate original front RF/UI circuit board',119,17,1, (92,-125.3,57),'Wireless',2,'pcb',.8,True,orient=front)
    for i,(x,z,w,h) in enumerate([(54,57,12,9),(81,57,8,8),(113,57,6,6)]):m.box('FrontRFIC'+str(i),'Independent front-board IC envelope',w,h,1,(x,-126.55,z),'Wireless',2,'black',.3,True,orient=front)
    m.cyl('PowerGuideRear','Separate front power light-guide stem',2,3,(146,-126.65,55),'Wireless',2,'white',axis=(0,-1,0),internal=True)
    m.box('PowerSensePad','Separate capacitive power electrode study',10,10,.035,(146,-126.45,55),'Wireless',2,'copper',2,True,orient=front)
    m.cut('PowerSensePad',Part.makeCylinder(2.2,1,V(146,-126,55),V(0,-1,0)),'Light path through sensing electrode').Refine=False
    m.box('WirelessPCB','Independent top-mounted Wi-Fi daughterboard',54,28,.8,(-114,74,75.4),'Wireless',5,'pcb',1,True)
    for i,(x,y,w,h) in enumerate([(-126,74,12,12),(-107,74,10,10)]):m.box('WirelessIC'+str(i),'Separate wireless IC envelope',w,h,.75,(x,y,76.4),'Wireless',5,'black',.3,True)
    for i,x in enumerate([-137,-91]):m.box('WirelessAntenna'+str(i),'Independent antenna conductor study',4,20,.04,(x,74,76.27),'Wireless',5,'gold',.2,True)
    m.ring('SpeakerBasket','Separate original console piezo/speaker basket',10,8.5,5,(-138,24,68),'Wireless',4,'matte',internal=True)
    m.cyl('SpeakerDiaphragm','Separate console sound diaphragm',8.2,.2,(-138,24,72),'Wireless',4,'metal',internal=True)
    m.cyl('SpeakerMagnet','Separate sound-transducer magnet study',4,2,(-138,24,68.5),'Wireless',4,'black',internal=True)
    m.feature('SpeakerBracket','Independent speaker holder',m.rr(25,25,1,(-138,24,67),2).cut(Part.makeCylinder(8.4,1.4,V(-138,24,66.8))),'Wireless',4,'matte',True)
    _finish(m,12,'front_rf_ui_wifi_and_separate_speaker','加入长条前端 RF/UI 板、电容电源感应层、导光杆、上方无线子板和独立扬声器机构；天线、屏蔽与局部器件为原版照片指导的非功能性结构。')


STAGES[12]=stage12


def _header(m,key,x,y,z,w,pins,group='Wiring'):
    m.feature(key+'Housing','Independent internal cable header',m.rr(w,6,4,(x,y,z),.4).cut(m.rr(w-1.2,4.8,3.5,(x,y,z+.7),.2)),group,1,'matte',True)
    for i in range(pins):m.cyl(key+'Pin'+str(i),'Independent schematic header contact',.22,2.5,(x+(i-(pins-1)/2)*(w-2.6)/max(1,pins-1),y,z+1),group,1,'gold',internal=True)


def stage13(m):
    from .atari2600 import _rounded_route
    def wire(key,pts,r,color):m.feature(key,'Independent insulated cable route study',_rounded_route([V(*p) for p in pts],max(.7,r+.3),r),'Wiring',2,color,True)
    _header(m,'OpticalDataHeader',0,80,15,13,7)
    _header(m,'OpticalPowerHeader',-20,93,15,16,4)
    m.box('OpticalDataPlug','Independent optical SATA data plug',12,4,4,(-95,46,34),'Wiring',2,'matte',.5,True)
    m.box('OpticalPowerPlug','Independent optical power plug',15,4,4,(-73,46,34),'Wiring',2,'matte',.5,True)
    wire('OpticalDataCable',[(-95,49,36),(-95,53,41),(-95,61,41),(0,80,41),(0,80,19.5)],1,'red')
    for i in range(4):
        d=(i-1.5)*1.8
        wire('OpticalPowerWire'+str(i),[(-73+d,48.2,36),(-73+d,70,36),(-20+d,93,36),(-20+d,93,19.5)],.3,'black' if i%2 else 'gold')
    _header(m,'HDDDataHeader',0,100,15,13,7)
    _header(m,'HDDPowerHeader',-21,108,15,16,4)
    m.box('HDDDataPlug','Independent hard-drive SATA data plug',12,4,4,(48,114.2,49),'Wiring',3,'matte',.5,True)
    m.box('HDDPowerPlug','Independent hard-drive SATA power plug',18,4,6,(66,114.2,47),'Wiring',3,'matte',.5,True)
    wire('HDDDataCable',[(48,116.5,51),(48,120,51),(12,120,51),(0,100,51),(0,100,19.5)],.8,'red')
    for i in range(4):
        d=(i-1.5)*2
        wire('HDDPowerWire'+str(i),[(66+d,116.5,47.5+i*.8),(66+d,121.5,47.5+i*.8),(14+d,121.5,47.5+i*.8),(-21+d,108,39+i*.8),(-21+d,108,19.5)],.25,'black' if i%2 else 'gold')
    _header(m,'FanHeader',144,26,15,11,4)
    for i in range(4):
        d=(i-1.5)*.9
        wire('FanWire'+str(i),[(137,-25+d,64),(154,-25+d,64),(154,26+d,64),(144+d,26,55),(144+d,26,19.5)],.22,['black','red','gold','blue'][i])
    _header(m,'WirelessHeader',-52,95,15,12,6)
    wire('WirelessCable',[(-86,74,76),(-77,74,76),(-52,95,67),(-52,95,19.5)],.6,'black')
    _header(m,'FrontRFHeader',13,-105,15,12,6)
    wire('FrontRFCable',[(38,-124,57),(24,-119,57),(13,-105,40),(13,-105,19.5)],.55,'black')
    m.cut('ChassisFront',_rounded_route([V(38,-124,57),V(24,-119,57),V(13,-105,40),V(13,-105,19.5)],1,.8),'Insulated front RF cable passage').Refine=False
    for i in range(2):
        x=-138+i*1.1
        wire('SpeakerWire'+str(i),[(x,34.5,70),(x,44,70),(-132+i*1.1,63,70),(-132+i*1.1,63,75)],.22,'red' if i==0 else 'black')
    _finish(m,13,'optical_hdd_fan_rf_and_wireless_harnesses','补齐光驱与硬盘的 SATA/电源线、风扇、前端 RF、无线板及扬声器线束；分离主板插座和接点，路线与芯数为静态机构示意，不提供实际电气引脚或维修接线。')
    m.snapshot('13_internal_harnesses',assemblies=['Mainboard','Wiring','Wireless'],normal=(.4,-.6,1.5))


STAGES[13]=stage13


def stage14(m):
    # Upper shield stays below the top plastic and accommodates the axial fan.
    shield=m.rr(329,249,.55,(0,0,74.2),.8)
    holes=[Part.makeCylinder(56.8,1.2,V(80,-40,74))]
    for x in range(-143,145,7):
        for y in [96,107]:holes.append(m.rr(3.6,6,1.2,(x,y,74),.3))
    holes.extend([m.rr(64,40,1.2,(-114,74,74),1),m.rr(26,26,1.2,(-138,24,74),2)])
    shield=shield.cut(Part.makeCompound(holes))
    from .atari2600 import _rounded_route
    shield=shield.cut(_rounded_route([V(-86,74,76),V(-77,74,76),V(-52,95,67),V(-52,95,19.5)],1,.9))
    m.feature('UpperShield','Independent perforated upper EMI shield',shield,'Shielding',5,'metal',True)
    # Eight long cover fasteners, located in the perimeter towers, as photographed.
    m.cut('Mainboard',[Part.makeCylinder(3.2,3,V(x,y,11.5)) for x,y in [(-160,-116),(-160,108),(160,-116),(160,108),(-5,-116),(-5,108),(-160,0),(160,0)]],'Perimeter guide-tower clearance through board').Refine=False
    for i,(x,y) in enumerate([(-160,-116),(-160,108),(160,-116),(160,108),(-5,-116),(-5,108),(-160,0),(160,0)]):
        m.ring('CoverTower'+str(i),'Independent long cover screw guide tower',3,1.25,64,(x,y,7),'Frame',1,'matte',internal=True)
        m.cyl('CoverShaft'+str(i),'Separate long cover screw shaft study',1.05,64,(x,y,7.3),'Frame',1,'metal',internal=True)
        head=Part.makeCylinder(2.1,.7,V(x,y,71.5))
        pts=[V(x+.9*__import__('math').cos(a*__import__('math').pi/3),y+.9*__import__('math').sin(a*__import__('math').pi/3),71.95) for a in range(6)]
        head=head.cut(Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,.4)))
        m.feature('CoverHead'+str(i),'Independent recessed fastener head study',head,'Frame',5,'metal',True)
    for i,(x,y) in enumerate([(-145,-103),(-145,100),(145,-103),(145,100),(0,-103),(0,100)]):
        m.cyl('BoardScrewShaft'+str(i),'Separate motherboard mounting screw shank',1.05,6.5,(x,y,7.5),'Frame',-2,'metal',internal=True)
        m.ring('BoardScrewHead'+str(i),'Independent motherboard mounting head',2.2,.75,.65,(x,y,14.05),'Frame',0,'metal',internal=True)
    _finish(m,14,'upper_shield_and_eight_long_cover_fasteners','补齐上层屏蔽板、风扇与无线板开口、八组长盖螺钉导柱、分離的杆/头与主板紧固件；螺纹和工具槽简化为可检查的机构示意，后续统一进行装配体积检查。')


STAGES[14]=stage14


def _pad_point(x,y,z):return V(x,y-260,z)


def _pad_curves(sx=1,sy=1):
    right=[[(0,45),(26,45),(46,45),(56,40)],[(56,40),(71,36),(78,20),(77,8)],[(77,8),(76,-13),(69,-57),(57,-63)],[(57,-63),(47,-68),(31,-33),(21,-27)],[(21,-27),(14,-24),(6,-24),(0,-24)]]
    result=[]
    for pts in right+[[(-x,y) for x,y in reversed(s)] for s in reversed(right)]:
        b=Part.BezierCurve();b.setPoles([V(x*sx,y*sy) for x,y in pts]);result.append(b.toBSpline())
    return result


def _pad_loft(m,key,profiles):
    sketches=[]
    for i,(sx,sy,z) in enumerate(profiles):
        sk=m.doc.addObject('Sketcher::SketchObject',key+'Profile'+str(i));sk.addGeometry(_pad_curves(sx,sy),False);sk.Placement.Base=_pad_point(0,0,z)
        m.group('Construction').addObject(sk);sketches.append(sk)
    obj=m.doc.addObject('Part::Loft',key);obj.Sections=sketches;obj.Solid=True;obj.Ruled=False;obj.MaxDegree=3
    m.doc.recompute();obj.Shape.check(True);assert len(obj.Shape.Solids)==1
    m.group('Construction').addObject(obj)
    for sk in sketches:sk.Visibility=False
    obj.Visibility=False;return obj


def _pad_shell(m,key,outer,inner,layer):
    a=_pad_loft(m,key+'Outer',outer);b=_pad_loft(m,key+'Inner',inner)
    obj=m.doc.addObject('Part::Cut',key);obj.Base=a;obj.Tool=b;obj.Refine=False;m.doc.recompute()
    obj.Shape.check(True);a.Visibility=False;b.Visibility=False
    return m.register(obj,key,'Controller',layer,'matte')


def stage15(m):
    m.colors.update(yellow=(.9,.68,.06),xboxgreen=(.14,.68,.2),ivory=(.75,.76,.76))
    _pad_shell(m,'PadBack',[(.87,.87,0),(.97,.97,6),(1,1,15),(1,1,20)],[(.82,.82,2),(.93,.93,6),(.965,.965,15),(.965,.965,20.2)],-4)
    _pad_shell(m,'PadFront',[(1,1,20.3),(.98,.98,29),(.94,.94,35)],[(.965,.965,20.1),(.946,.946,28.6),(.905,.905,33)],4)
    for i,(x,w) in enumerate([(-101,56),(45,56)]):
        mask=Part.makeBox(w,135,22,_pad_point(x,-80,-1))
        grip=m.parts['PadBack'].Shape.common(mask)
        m.feature('PadGripCover'+str(i),'Separate original removable rear grip panel',grip,'Controller',-4,'matte')
        m.cut('PadBack',mask,'Separate rear grip panel boundary').Refine=False
    m.cut('PadBack',m.rr(58,36,4,tuple(_pad_point(0,24,-1)),3),'Original flush AA battery-door aperture').Refine=False
    m.box('PadBatteryDoor','Separate original flush dual-AA battery door',57.5,35.5,1.4,tuple(_pad_point(0,24,.15)),'Controller',-5,'matte',2.8)
    _finish(m,15,'original_1537_native_shell_and_grip_panels','依据 C3K1537 原版照片建立前后原生曲线放样壳、分离的后握把面板和齐平双 AA 电池盖；曲率与尺寸为照片指导近似，明确保留原版无 3.5 mm 耳机孔的外观。')
    m.snapshot('15_original_controller_shell',assemblies=['Controller'],normal=(.3,-.5,1.8))


STAGES[15]=stage15


def stage16(m):
    sticks=[(-43,15),(25,-13)];buttons=[('Y',46,23,'yellow'),('X',33,10,'blue'),('B',59,10,'red'),('A',46,-3,'xboxgreen')]
    holes=[Part.makeCylinder(12.2,12,_pad_point(x,y,27)) for x,y in sticks]
    holes += [Part.makeCylinder(4.8,12,_pad_point(x,y,27)) for _,x,y,_ in buttons]
    holes += [Part.makeCylinder(8.2,12,_pad_point(0,29,27)),m.rr(26,6.8,12,tuple(_pad_point(-25,-12,27)),.7),m.rr(6.8,26,12,tuple(_pad_point(-25,-12,27)),.7)]
    holes += [m.rr(6.8,5.8,12,tuple(_pad_point(x,10,27)),2.5) for x in [-15,15]]
    holes += [m.rr(28,10,12,tuple(_pad_point(x,37,26)),2.5) for x in [-46,46]]
    m.cut('PadFront',holes,'Original asymmetric sticks ABXY cross-pad and top keys').Refine=False
    for i,(x,y) in enumerate(sticks):
        dome=Part.makeSphere(11.8,_pad_point(x,y,31.3)).common(Part.makeCylinder(12,4.8,_pad_point(x,y,32.2))).cut(Part.makeCylinder(3.1,6,_pad_point(x,y,31.5)))
        m.feature('PadStickDome'+str(i),'Independent original thumbstick dust dome',dome,'Controller',3,'matte',True)
        m.ring('PadStickStem'+str(i),'Independent hollow thumbstick neck',2.8,2,9,tuple(_pad_point(x,y,31.5)),'Controller',4,'matte',internal=True)
        cap=Part.makeCylinder(9.5,2.5,_pad_point(x,y,40.8)).cut(Part.makeSphere(23,_pad_point(x,y,64.9)))
        m.feature('PadStickCap'+str(i),'Original concave rubber thumb cap',cap,'Controller',5,'rubber')
    cross=m.rr(25.5,6.3,2,tuple(_pad_point(-25,-12,35.2)),.6).fuse(m.rr(6.3,25.5,2,tuple(_pad_point(-25,-12,35.2)),.6)).removeSplitter()
    m.feature('PadDPad','Independent original glossy cross directional key',cross,'Controller',5,'gloss')
    for letter,x,y,color in buttons:
        cap=Part.makeCylinder(4.4,6.3,_pad_point(x,y,30.9));cap=cap.makeFillet(.6,[e for e in cap.Edges if e.BoundBox.ZLength<1e-7 and e.BoundBox.ZMax>37.1])
        m.feature('PadButton'+letter,'Original black '+letter+' key with colored legend',cap,'Controller',4,'gloss')
        m.label('PadButtonMark'+letter,letter,3.4,tuple(_pad_point(x-1.2,y-1.3,37.24)),'Controller',5,color)
    m.cyl('PadXboxButton','Independent original Xbox guide key',7.9,2.3,tuple(_pad_point(0,29,35.1)),'Controller',5,'chrome')
    m.label('PadXboxMark','X',8,tuple(_pad_point(-2.7,26.1,37.44)),'Controller',5,'gloss')
    for i,x in enumerate([-15,15]):
        m.box('PadMenuKey'+str(i),'Original View or Menu key',6.3,5.3,2.3,tuple(_pad_point(x,10,35.1)),'Controller',5,'matte',2.3)
        m.label('PadMenuMark'+str(i),'=' if i==0 else '#',2.1,tuple(_pad_point(x-.8,9.2,37.44)),'Controller',5,'chrome')
    for i,x in enumerate([-46,46]):
        m.box('PadBumper'+str(i),'Independent original bumper key',27.5,9.5,5.8,tuple(_pad_point(x,37,29.5)),'Controller',4,'gloss',2.2)
        m.label('PadBumperMark'+str(i),'LB' if i==0 else 'RB',2.4,tuple(_pad_point(x-2.6,36,35.34)),'Controller',5,'chrome')
    _finish(m,16,'1537_asymmetric_sticks_cross_dpad_and_keys','加入原版非对称摇杆、凹面拇指帽、十字键、黑色 ABXY 与彩色字标、View/Menu、Xbox 键和肩键；不采用后期手柄的圆盘十字键、Share 键或 USB-C。')
    m.snapshot('16_controller_controls',assemblies=['Controller'],normal=(.25,-.5,1.8))


STAGES[16]=stage16


def _pad_board(m,key,pts,z):
    sk=m.doc.addObject('Sketcher::SketchObject',key+'Outline');vecs=[V(x,y) for x,y in pts]
    sk.addGeometry([Part.LineSegment(a,b) for a,b in zip(vecs,vecs[1:]+vecs[:1])],False);sk.Placement.Base=_pad_point(0,0,z)
    m.group('Construction').addObject(sk)
    obj=m.doc.addObject('Part::Extrusion',key+'Extrusion');obj.Base=sk;obj.DirMode='Normal';obj.LengthFwd=1.2;obj.Solid=True
    m.doc.recompute();sk.Visibility=False;return m.register(obj,key,'Controller',0,'pcb',True)


def stage17(m):
    rear=[(-63,33),(-68,5),(-58,-16),(-38,-23),(38,-23),(58,-16),(68,5),(63,33),(30,33),(30,4.5),(-30,4.5),(-30,33)]
    front=[(-22,38),(22,38),(25,29),(57,29),(64,11),(61,-22),(38,-27),(8,-27),(8,-23),(-50,-23),(-63,-12),(-60,5),(-24,5)]
    _pad_board(m,'PadStickPCB',rear,14)
    _pad_board(m,'PadContactPCB',front,27)
    stickholes=[Part.makeCylinder(12.5,2,_pad_point(x,y,26.7)) for x,y in [(-43,15),(25,-13)]]
    m.cut('PadContactPCB',stickholes,'Original two-stick passages through front contact PCB').Refine=False
    m.cut('PadContactPCB',m.parts['PadFront'].Shape,'Front board perimeter clearance inside curved case').Refine=False
    m.box('PadMCU','Original 1537 leaded controller IC study',16,16,1.1,tuple(_pad_point(44,-6,12.5)),'Controller',-1,'black',.3,True)
    for side in range(4):
        for i in range(12):
            a=(i-5.5)*1.1;x,y=(44+a,-6+(8.55 if side==0 else -8.55)) if side<2 else (44+(8.55 if side==2 else -8.55),-6+a)
            m.box('PadMCULead'+str(side)+'_'+str(i),'Independent schematic controller IC lead',.3 if side<2 else .7,.7 if side<2 else .3,.17,tuple(_pad_point(x,y,13.7)),'Controller',-1,'metal',.03,True)
    m.box('PadRadioPCB','Original 1537 separate wireless daughterboard',23,28,.6,tuple(_pad_point(-43,-2,12.6)),'Controller',-1,'pcb',.5,True)
    m.box('PadRadioChip','Independent controller radio package',9,9,.9,tuple(_pad_point(-43,-4,11.5)),'Controller',-2,'black',.3,True)
    m.box('PadRadioClock','Independent controller radio resonator',7,3,1,tuple(_pad_point(-43,6,11.4)),'Controller',-2,'metal',.4,True)
    for j,(x,y) in enumerate([(-8,-13),(44,-13)]):
        # Two separated board-to-board headers, as visible in the FCC photos.
        m.box('PadStackSocket'+str(j),'Independent controller board-stack socket',11,5,2,tuple(_pad_point(x,y,15.6)),'Controller',1,'matte',.3,True)
        m.box('PadStackPlug'+str(j),'Independent controller board-stack mating carrier',11,5,1.7,tuple(_pad_point(x,y,24.9)),'Controller',2,'matte',.3,True)
        for i in range(10):m.cyl('PadStackPin'+str(j)+'_'+str(i),'Independent schematic board-stack contact',.18,6.7,tuple(_pad_point(x+(i-4.5)*.9,y,17.9)),'Controller',1,'gold',internal=True)
    from .xbox360 import _pad_joystick
    bores=[]
    for i,(x,y) in enumerate([(-43,15),(25,-13)]):
        before=set(m.parts);holes=_pad_joystick(m,i,x,y)
        for k in set(m.parts)-before:
            o=m.parts[k];o.Placement.Base.z+=1.2;o.FlatPlacement=o.Placement
        for h in holes:h.translate(V(0,0,1.2));bores.append(h)
    m.cut('PadStickPCB',bores,'Separate joystick anchor and terminal holes').Refine=False
    _finish(m,17,'fcc1537_two_boards_radio_and_analog_modules','依据微软 C3K1537 六页内部照片建立 U 形摇杆板 X860641 与前接点板 X860655，加入无线子板、引脚主控、两组板间连接器及双轴摇杆机构。采用原版双板结构，局部封装和接点数量为非功能性示意。')
    m.snapshot('17_original_two_boards',assemblies=['Controller'],exclude=['PadBack','PadFront','PadGripCover0','PadGripCover1','PadBatteryDoor','PadStickDome0','PadStickDome1','PadStickCap0','PadStickCap1'],normal=(.4,-.5,1.6))


STAGES[17]=stage17


def stage18(m):
    # Original directional switches are metal domes, distinct from the ABXY rubber sheet.
    for i,(dx,dy) in enumerate([(0,6.5),(6.5,0),(0,-6.5),(-6.5,0)]):
        x,y=-25+dx,-12+dy
        m.cyl('PadDPadLand'+str(i),'Independent directional copper contact',2.6,.035,tuple(_pad_point(x,y,28.24)),'Controller',1,'gold',internal=True)
        dome=Part.makeSphere(5.5,_pad_point(x,y,23.35)).common(Part.makeCylinder(2.9,.65,_pad_point(x,y,28.32)))
        m.feature('PadDPadDome'+str(i),'Independent original directional metal dome',dome,'Controller',2,'metal',True)
        m.cyl('PadDPadPlunger'+str(i),'Independent cross-key plunger study',1.4,6,tuple(_pad_point(x,y,29.05)),'Controller',3,'matte',internal=True)
    m.ring('PadDPadRetainer','Separate original metal D-pad retaining ring',14.1,12.9,.4,tuple(_pad_point(-25,-12,32.3)),'Controller',3,'metal',internal=True)
    m.cut('PadFront',Part.makeCylinder(14.3,.8,_pad_point(-25,-12,32.1)),'Directional metal retainer pocket').Refine=False
    for key,x,y,r in [('A',46,-3,3.1),('B',59,10,3.1),('X',33,10,3.1),('Y',46,23,3.1),('View',-15,10,2.1),('Menu',15,10,2.1),('Xbox',0,29,3.5)]:
        for side in range(2):
            half=Part.makeCylinder(r,.035,V(),V(0,0,1),180);half.rotate(V(),V(0,0,1),side*180)
            half=half.cut(Part.makeBox(2*r+1,.3,.2,V(-r-.5,-.15,-.05)));half.translate(_pad_point(x,y,28.24))
            m.feature('Pad'+key+'Contact'+str(side),'Independent split key contact',half,'Controller',1,'gold',True)
        m.cyl('Pad'+key+'Carbon','Separate conductive key pill',r-.3,.15,tuple(_pad_point(x,y,28.4)),'Controller',2,'black',internal=True)
        height=2 if key in ['A','B','X','Y'] else 5.8
        wall=Part.makeCone(r+1.1,r-.2,height,_pad_point(x,y,28.65)).cut(Part.makeCone(r+.65,r-.65,height+.1,_pad_point(x,y,28.55)))
        m.feature('Pad'+key+'Silicone','Independent silicone key dome study',wall,'Controller',2,'rubber',True)
    for i,x in enumerate([-35,35]):
        m.box('PadBumperSwitch'+str(i),'Independent bumper switch carrier',5,5,3,tuple(_pad_point(x,28,23.3)),'Controller',2,'matte',.4,True)
        m.cyl('PadBumperActuator'+str(i),'Independent bumper-switch actuator',1.3,1.4,tuple(_pad_point(x,28,26.5)),'Controller',3,'matte',internal=True)
        m.cut('PadContactPCB',Part.makeCylinder(1.5,2,_pad_point(x,28,26.7)),'Separate bumper actuator passage').Refine=False
    # Five-contact micro-USB on the original top edge, proprietary bottom headset interface.
    rear=g.rotation((0,1,0),(0,0,1));front=g.rotation((0,-1,0),(0,0,1))
    for key,x,y,z,w,h,d,q,pins in [('PadMicroUSB',0,37.5,25,8,3.5,6,rear,5),('PadHeadset',0,-26,20,16,6,5,front,9)]:
        shell=m.rr(w,h,d,tuple(_pad_point(x,y,z)),.6,q).cut(m.rr(w-.7,h-.7,d+.4,tuple(_pad_point(x,y+(-.2 if y>0 else .2),z)),.3,q))
        m.feature(key+'Shell','Separate original controller connector shield',shell,'Controller',2,'metal',True)
        sign=1 if y>0 else -1
        m.box(key+'Tongue','Independent original connector tongue',w-1.7,3,.65,tuple(_pad_point(x,y+sign*3,z-.3)),'Controller',2,'matte',.15,True)
        for i in range(pins):m.box(key+'Contact'+str(i),'Independent schematic connector contact',.35,2.3,.08,tuple(_pad_point(x+(i-(pins-1)/2)*(w-2.4)/pins,y+sign*3.3,z+.43)),'Controller',2,'gold',.02,True)
        hole=m.rr(w+.8,h+.8,12,tuple(_pad_point(x,y-sign*3,z)),.7,q)
        for case in ['PadBack','PadFront']:m.cut(case,hole,'Original micro-USB or proprietary expansion opening').Refine=False
    _finish(m,18,'1537_metal_domes_silicone_micro_usb_and_expansion','补齐原版十字键金属弹片、ABXY/Menu/View/Xbox 分离接点和导电胶，加入顶端五接点 micro-USB 与底部专用耳麦扩展口；原版不加入后期 3.5 mm 耳机孔，专用口接点仅作结构示意。')


STAGES[18]=stage18


def stage19(m):
    from .atari2600 import _helical_spring
    bay=m.rr(56,38,13.7,tuple(_pad_point(0,24,1.9)),2).cut(m.rr(53,35,14.1,tuple(_pad_point(0,24,1.7)),1))
    bay=bay.common(m.doc.getObject('PadBackInner').Shape)
    m.feature('PadAABay','Independent original two-AA compartment wall',bay,'Controller',-3,'matte',True)
    m.box('PadAADivider','Separate double-AA divider',52,.8,13.5,tuple(_pad_point(0,26,2)),'Controller',-3,'matte',.2,True)
    for i,(y,direction) in enumerate([(18,1),(34,-1)]):
        x=-24.7 if direction==1 else 24.7
        m.cyl('PadAA'+str(i),'Independent opposed-polarity AA cell',6.8,49.4,tuple(_pad_point(x,y,8.7)),'Controller',-2,'battery',axis=(direction,0,0),internal=True)
        m.cyl('PadAAPositive'+str(i),'Separate AA positive button',2.4,.5,tuple(_pad_point(x+direction*49.5,y,8.7)),'Controller',-2,'metal',axis=(direction,0,0),internal=True)
        m.cyl('PadAANegative'+str(i),'Separate AA negative cap',5.6,.12,tuple(_pad_point(x-direction*.2,y,8.7)),'Controller',-2,'metal',axis=(direction,0,0),internal=True)
        spring=_helical_spring(1.8,.8,1.3,.14);spring.rotate(V(),V(0,1,0),90*direction);spring.translate(_pad_point(-26.5 if direction==1 else 26.5,y,8.7))
        m.feature('PadAAContactSpring'+str(i),'Independent AA negative contact spring',spring,'Controller',-3,'metal',True)
    # Open routes for contact strips; electrical assignment is intentionally omitted.
    for i,y in enumerate([18,34]):
        for j,x in enumerate([-27.1,27.1]):
            m.box('PadBatteryContact'+str(i)+'_'+str(j),'Independent battery compartment metal contact',.25,5,7,tuple(_pad_point(x,y,5.2)),'Controller',-3,'metal',.06,True)
    m.cut('PadAABay',[m.rr(2,6,9,tuple(_pad_point(x,y,4.5)),.2) for x in [-27,27] for y in [18,34]],'Battery contact passages in AA compartment').Refine=False
    for i,(x,y) in enumerate([(-56,25),(56,25),(-54,-51),(54,-51),(0,1)]):
        # Small independent local supports; original fixing count and outline schematic.
        m.ring('PadScrewBoss'+str(i),'Independent controller case screw boss',2.3,1,5,tuple(_pad_point(x,y,5.5)),'Controller',-2,'matte',internal=True)
        m.cyl('PadCaseScrew'+str(i),'Separate controller case screw envelope',.8,5.7,tuple(_pad_point(x,y,5.1)),'Controller',-2,'metal',internal=True)
    _finish(m,19,'original_two_aa_bay_contacts_and_fixings','加入原版双 AA 电池舱、反向安装的电池及独立端帽、弹簧、金属接片和壳体固定件；未把可选充电套件或内置锂电池作为首发标准结构。')


STAGES[19]=stage19


def _motor(m,key,x,y,z,r,length,weight,axis=(0,1,0)):
    direction=V(*axis);origin=_pad_point(x,y,z)
    m.ring(key+'Can','Separate vibration motor metal can',r,r-.5,length,tuple(origin),'Controller',0,'metal',axis=axis,internal=True)
    m.ring(key+'End','Separate vibration motor end cap',r-.1,.7,.6,tuple(origin-direction*.8),'Controller',0,'matte',axis=axis,internal=True)
    m.cyl(key+'Shaft','Independent vibration-motor shaft',.5,length+3.8,tuple(origin-direction*.2),'Controller',1,'metal',axis=axis,internal=True)
    m.ring(key+'Rotor','Independent vibration rotor core',r*.43,.7,length-1,tuple(origin+direction*.4),'Controller',0,'metal',axis=axis,internal=True)
    m.ring(key+'Winding','Independent vibration winding envelope',r*.65,r*.48,length-1.3,tuple(origin+direction*.5),'Controller',0,'copper',axis=axis,internal=True)
    m.ring(key+'Magnet','Independent vibration stator-magnet ring',r-.8,r*.72,length-1,tuple(origin+direction*.4),'Controller',0,'black',axis=axis,internal=True)
    eccentric=Part.makeCylinder(weight,2.1,V(),V(0,0,1),175).cut(Part.makeCylinder(.7,2.5,V(0,0,-.2)))
    eccentric.Placement=App.Placement(origin+direction*(length+1),g.rotation(axis,(0,0,1)))
    m.feature(key+'Eccentric','Separate asymmetric vibration eccentric weight',eccentric,'Controller',1,'metal',True)


def stage20(m):
    from .atari2600 import _helical_spring,_rounded_route
    # Original impulse triggers: two grip motors plus a smaller motor at each trigger.
    _motor(m,'PadGripMotorL',-51,-45,12,8.2,18,6.5)
    _motor(m,'PadGripMotorR',51,-45,12,8.2,18,8.2)
    for i,x in enumerate([-49,49]):
        trigger=m.rr(25,19,13,tuple(_pad_point(x,40,13)),3).cut(m.rr(22,16,10.8,tuple(_pad_point(x,40,12.8)),2))
        m.feature('PadTrigger'+str(i),'Independent original impulse trigger cap',trigger,'Controller',2,'gloss')
        m.cyl('PadTriggerAxle'+str(i),'Separate trigger pivot axle',.8,24,tuple(_pad_point(x-12,40,24)),'Controller',2,'metal',axis=(1,0,0),internal=True)
        m.cut('PadTrigger'+str(i),Part.makeCylinder(1,26,_pad_point(x-13,40,24),V(1,0,0)),'Independent trigger pivot passage').Refine=False
        for case in ['PadBack','PadFront','PadGripCover0','PadGripCover1','PadStickPCB']:
            m.cut(case,m.rr(26,20,15,tuple(_pad_point(x,40,12)),3.2),'Original trigger travel aperture').Refine=False
        _motor(m,'PadTriggerMotor'+str(i),x,35,18,3.6,9,3.4)
        spring=_helical_spring(1.8,.7,4,.18);spring.rotate(V(),V(0,1,0),90);spring.translate(_pad_point(x-2,40,24))
        m.feature('PadTriggerSpring'+str(i),'Independent trigger return spring',spring,'Controller',2,'metal',True)
        m.cut('PadTrigger'+str(i),Part.makeCylinder(2.2,4.4,_pad_point(x-2.2,40,24),V(1,0,0)),'Independent trigger return-spring clearance').Refine=False
        m.box('PadTriggerMagnet'+str(i),'Independent magnetic trigger sensor target',3,3,1,tuple(_pad_point(x+6,34,21)),'Controller',1,'black',.3,True)
        m.box('PadTriggerHall'+str(i),'Independent trigger Hall-sensor package',3,3,.9,tuple(_pad_point(x+6,29,15.6)),'Controller',1,'black',.3,True)
    for j,x in enumerate([-51,51]):
        sign=-1 if x<0 else 1
        for i in range(2):
            d=0;z=12+i*.6
            pts=[_pad_point(x+d,-46.2,z),_pad_point(x+d,-49,z),_pad_point(sign*61.5+d,-49,z),_pad_point(sign*61.5+d,-6,z),_pad_point(sign*60+d,-6,13.1+i*.6)]
            m.feature('PadMotorWire'+str(j)+'_'+str(i),'Independent grip-motor rear lead',_rounded_route(pts,.5,.18),'Controller',1,'red' if i==0 else 'black',True)
    for j,x in enumerate([-49,49]):
        endx=-59 if x<0 else 59
        for i in range(2):
            d=0
            pts=[_pad_point(x+d,34,18+i*.9),_pad_point(x+d,29,23+i*.9),_pad_point(endx+d,27,16+i*.9)]
            m.feature('PadMotorWire'+str(j+2)+'_'+str(i),'Independent impulse-trigger motor lead',_rounded_route(pts,.7,.18),'Controller',1,'red' if i==0 else 'black',True)
            m.cut('PadTrigger'+str(j),_rounded_route(pts,.7,.4),'Insulated trigger motor cable passage').Refine=False
    _finish(m,20,'four_original_rumble_motors_and_impulse_triggers','按原版 FCC 照片加入左右握把电机及两枚独立扳机电机，分离转轴、转子、绕组、磁环与偏心块；扳机另设轴、回位弹簧、磁体和传感器。几何为静态机构示意，不模拟振动或信号。')
    m.snapshot('20_four_rumble_motors',assemblies=['Controller'],exclude=['PadBack','PadFront','PadGripCover0','PadGripCover1','PadBatteryDoor'],normal=(.4,-.6,1.4))


STAGES[20]=stage20


def stage21(m):
    front=g.rotation((0,-1,0),(0,0,1))
    # Accessory dimensions are photo-guided, not part of the published console envelope.
    m.native('KinectBottom','Native original Kinect2 lower shell',249,66,1.2,1.5,(0,260,19),'Kinect',-2,'matte')
    m.box('KinectTop','Independent Kinect2 top cover',249,66,1.5,(0,260,78.5),'Kinect',5,'matte',1.2)
    m.box('KinectRear','Independent Kinect2 rear cover',246,1.6,57.7,(0,292.2,20.65),'Kinect',3,'matte',.5)
    for i,x in enumerate([-123.7,123.7]):
        m.box('KinectSide'+str(i),'Independent vented Kinect end cap',1.6,62.6,57.7,(x,260,20.65),'Kinect',3,'matte',.4)
        vents=[]
        for yy in range(235,288,4):
            v=Part.makeBox(3,1.6,46,V(x-1.5,yy,26));v.rotate(V(x,yy,49),V(1,0,0),18);vents.append(v)
        m.cut('KinectSide'+str(i),vents,'Real diagonal sensor end-cap ventilation').Refine=False
    m.box('KinectFace','Separate glossy Kinect front fascia',246,57.7,1.3,(0,228.1,49.5),'Kinect',4,'gloss',.5,orient=front)
    openings=[Part.makeCylinder(r,3,V(x,229,z),V(0,-1,0)) for x,z,r in [(-94,52,11),(-49,52,9.2),(101,53,6.3)]]
    openings.append(m.rr(63,20,3,(0,229,52),1,front))
    m.cut('KinectFace',openings,'Independent color depth IR and status optical paths').Refine=False
    for key,x,r in [('RGBWindow',-94,10.7),('DepthWindow',-49,8.9)]:m.cyl('Kinect'+key,'Independent Kinect optical protective window',r,.35,(x,227.8,52),'Kinect',4,'screen',axis=(0,-1,0))
    m.box('KinectIRWindow','Separate three-field IR protective window',62.5,19.5,.35,(0,227.8,52),'Kinect',4,'screen',.8,orient=front)
    m.cyl('KinectStatusWindow','Separate original Kinect status guide',6,.3,(101,227.8,53),'Kinect',4,'white',axis=(0,-1,0))
    m.label('KinectStatusMark','X',6,(103,227.4,50.8),'Kinect',5,'gloss',rotation=front)
    m.cut('KinectFace',m.parts['KinectStatusMark'].Shape,'Inlaid status marking at optical-window border').Refine=False
    m.box('KinectMicBar','Separate lower four-microphone bar',239,10,8,(0,230,6),'Kinect',-3,'matte',1)
    m.cut('KinectMicBar',m.rr(237,8,8,(0,230,6.8),.6),'Separate microphone bar inner channel').Refine=False
    m.box('KinectFoot','Independent tilt-stand ground foot',99,43,3.2,(0,270,0),'Kinect',-5,'matte',3)
    m.feature('KinectTiltStand','Separate manual-tilt U stand',m.rr(93,35,4,(0,268,5),2).cut(m.rr(78,24,4.4,(0,268,4.8),1)),'Kinect',-4,'matte',True)
    for i,x in enumerate([-39,39]):
        m.box('KinectStandArm'+str(i),'Separate manual-tilt stand support',6,8,9,(x,267,9.2),'Kinect',-3,'matte',1,True)
        m.cyl('KinectTiltAxle'+str(i),'Independent manual-tilt pivot',1.6,7,(x-3.5,267,17.3),'Kinect',-2,'metal',axis=(1,0,0),internal=True)
        m.cut('KinectStandArm'+str(i),Part.makeCylinder(1.8,8,V(x-4,267,17.3),V(1,0,0)),'Separate tilt axle passage').Refine=False
    _finish(m,21,'kinect2_glossy_sensor_shell_and_manual_stand','加入原版 Kinect2 的原生底板、分离前后盖、斜向端部格栅、三类光学窗口、四麦克风横梁和手动俯仰底座；不加入 Kinect360 的电动底座，附件尺寸与壳体局部比例为照片指导近似。')
    m.snapshot('21_kinect_sensor_shell',assemblies=['Kinect'],normal=(.4,-1,.6))


STAGES[21]=stage21


def stage22(m):
    front=g.rotation((0,-1,0),(0,0,1))
    m.box('KinectMainPCB','Separate Kinect2 main processing board',224,45,1.2,(0,278,50),'Kinect',1,'pcb',1,True,orient=front)
    m.box('KinectSensorPCB','Independent Kinect2 sensor board',219,38,1,(0,255,50),'Kinect',2,'pcb',1,True,orient=front)
    for key,x,z,w,h in [('Processor',25,50,23,23),('RAM',-14,51,12,20),('USBController',69,53,13,13),('Flash',-79,42,12,10)]:
        m.box('Kinect'+key,'Separate Kinect processing package study',w,h,1.4,(x,276.4,z),'Kinect',1,'black',.4,True,orient=front)
    m.box('KinectThermalBar','Separate sensor aluminum thermal spine',216,3,34,(0,258,33),'Kinect',2,'metal',1,True)
    for i,(x,z) in enumerate([(-88,49),(-49,50),(2,50),(78,50)]):m.box('KinectThermalPad'+str(i),'Independent Kinect thermal interface',17,17,.7,(x,256.3,z),'Kinect',2,'thermal',.5,True,orient=front)
    for key,x,r in [('RGB',-94,9.5),('Depth',-49,7.8)]:
        m.ring('Kinect'+key+'Barrel','Independent color or depth lens barrel',r,r-1.4,17,(x,253.6,52),'Kinect',3,'matte',axis=(0,-1,0),internal=True)
        for i,(yy,rr) in enumerate([(250,r-1.7),(243,r-1.8),(236.2,r-1.7)]):m.cyl('Kinect'+key+'Lens'+str(i),'Separate optical element envelope',rr,.45,(x,yy,52),'Kinect',3,'blue',axis=(0,-1,0),internal=True)
        m.box('Kinect'+key+'Imager','Independent sensor package envelope',r*1.05,r*1.05,1,(x,253.8,52),'Kinect',2,'black',.4,True,orient=front)
    m.box('KinectIRBoard','Independent triple IR-emitter daughterboard',65,26,1,(0,250.5,52),'Kinect',2,'pcb',.6,True,orient=front)
    m.box('KinectIRSink','Separate IR module metal backplate',64,25,2,(0,252.8,52),'Kinect',2,'metal',.6,True,orient=front)
    for i,x in enumerate([-20,0,20]):
        m.ring('KinectIREmitterFrame'+str(i),'Independent IR emitter cell frame',6,4.7,4,(x,249,52),'Kinect',3,'metal',axis=(0,-1,0),internal=True)
        m.cyl('KinectIREmitter'+str(i),'Separate IR emitter envelope',4.4,1,(x,248.7,52),'Kinect',3,'red',axis=(0,-1,0),internal=True)
        m.box('KinectIRFilter'+str(i),'Independent rectangular IR optical filter',18,15,.45,(x,237,52),'Kinect',3,'blue',.4,True,orient=front)
    for i,x in enumerate([-93,-31,31,93]):
        m.box('KinectMicPCB'+str(i),'Separate microphone local board',9,6,.6,(x,230,7),'Kinect',-2,'pcb',.4,True)
        m.cyl('KinectMic'+str(i),'Independent microphone capsule',2,2,(x,230,7.8),'Kinect',-2,'metal',internal=True)
        m.cut('KinectMicBar',Part.makeCylinder(2.3,9,V(x,230,5.5)),'Real microphone capsule and acoustic bore').Refine=False
    m.box('KinectLEDPCB','Separate Kinect status LED daughterboard',19,19,.6,(101,240,53),'Kinect',3,'pcb',.4,True,orient=front)
    m.cyl('KinectLED','Independent Kinect status emitter',2,2,(101,239,53),'Kinect',3,'white',axis=(0,-1,0),internal=True)
    _finish(m,22,'kinect_rgb_depth_triple_ir_and_four_microphones','依据 Kinect2 拆解加入主处理板、传感器板、金属热脊、导热垫、RGB/深度光学组件、三分区 IR 模组和四枚麦克风；镜片、传感器与红外窗口为独立学习实体，不提供光学标定或功能仿真。')
    m.snapshot('22_kinect_optics',assemblies=['Kinect'],exclude=['KinectFace','KinectTop','KinectRear','KinectSide0','KinectSide1','KinectIRWindow'],normal=(.35,-1,.5))


STAGES[22]=stage22


def stage23(m):
    import math
    from .atari2600 import _rounded_route
    rear=g.rotation((0,1,0),(0,0,1))
    x,y,z=0,280,52
    m.cut('KinectRear',m.rr(39,39,4,(x,290,z),2,rear),'Original rear fan exhaust aperture').Refine=False
    frame=m.rr(38,38,10,(x,y,z),2,rear).cut(Part.makeCylinder(17,10.4,V(x,y-.2,z),V(0,1,0)))
    m.feature('KinectFanFrame','Separate Kinect rear axial fan frame',frame,'Kinect',3,'matte',True)
    m.ring('KinectFanHub','Independent rear fan hub',6,1,7,(x,y+1,z),'Kinect',3,'matte',axis=(0,1,0),internal=True)
    m.cyl('KinectFanShaft','Separate rear fan shaft',.7,8,(x,y+.5,z),'Kinect',3,'metal',axis=(0,1,0),internal=True)
    for i in range(7):
        pts=[]
        for r,a in [(6.5,-12),(16,-10),(16,9),(6.5,12)]:
            angle=math.radians(a+360*i/7);pts.append(V(r*math.cos(angle),r*math.sin(angle),0))
        blade=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,4));blade.Placement=App.Placement(V(x,y+2,z),rear)
        m.feature('KinectFanBlade'+str(i),'Separate sensor cooling fan blade study',blade,'Kinect',3,'matte',True)
    grille=m.rr(41,41,1.3,(0,293.2,52),1.5,rear)
    cuts=[m.rr(34,1.7,1.7,(0,293.0,52+d),.2,rear) for d in range(-15,16,4)]
    m.feature('KinectFanGrille','Separate Kinect fan outlet grille',grille.cut(Part.makeCompound(cuts)),'Kinect',4,'matte')
    for i in range(3):
        pts=[V(20,283,50+i),V(28,283,50+i),V(35,278.3,60+i)]
        m.feature('KinectFanWire'+str(i),'Independent sensor fan lead',_rounded_route(pts,1,.18),'Kinect',2,['black','red','gold'][i],True)
    # Separate short flexible interconnects between stacked boards.
    for i,x in enumerate([-75,70]):
        m.box('KinectBoardFlex'+str(i),'Independent sensor-board flex interconnect',10,14,.15,(x,266,70),'Kinect',3,'copper',.4,True)
    m.box('KinectStatusFlex','Independent LED-board interconnect',5,12,.15,(99,248,66),'Kinect',3,'copper',.3,True)
    m.cut('KinectRear',m.rr(12,10,5,(67,289,35),.8,rear),'Removable proprietary sensor cable opening').Refine=False
    m.box('KinectCablePlug','Independent original sensor cable plug',11,11,8,(67,294,31),'Kinect',3,'matte',1,True)
    route=[V(67,300,35),V(67,313,35),V(140,313,35),V(155,300,25),V(155,190,25),V(139,190,25)]
    m.feature('KinectCable','Separate coiled-display sensor cable study',_rounded_route(route,5.5,2.5),'Kinect',0,'black',True)
    m.box('KinectConsolePlug','Independent Kinect console-end overmold',21,27,12,(128,190,19),'Kinect',0,'matte',2)
    for i in range(4):m.ring('KinectCableRelief'+str(i),'Independent molded cable relief rib',3.3,2.65,.7,(139+i,190,25),'Kinect',0,'matte',axis=(1,0,0),internal=True)
    _finish(m,23,'kinect_rear_fan_flexes_and_removable_cable','加入 Kinect 后部独立风扇/格栅、板间软排和可拆专用线缆；风道与光学模组分区，线缆按陈列路线缩短，不声称实际线长、引脚或电气规格。')


STAGES[23]=stage23


def stage24(m):
    cx=320
    m.native('PSUBottom','Native original external power-supply lower shell',200,75,2,1.6,(cx,0,2),'Accessories',-4,'matte')
    m.box('PSUTop','Separate external power-supply top cover',200,75,1.6,(cx,0,53),'Accessories',4,'matte',2)
    for key,y in [('PSUFront',-36.7),('PSURear',36.7)]:m.box(key,'Independent external power-supply long wall',196.4,1.6,49,(cx,y,3.8),'Accessories',0,'matte',.4,True)
    for key,x in [('PSUACEnd',220.8),('PSUDCEnd',419.2)]:m.box(key,'Independent external power-supply end wall',1.6,71.4,49,(x,0,3.8),'Accessories',0,'matte',.4,True)
    for i,(x,y) in enumerate([(235,-25),(405,-25),(235,25),(405,25)]):m.box('PSUFoot'+str(i),'Separate original power-brick rubber foot',13,9,1.8,(x,y,0),'Accessories',-5,'rubber',2)
    vents=[Part.makeBox(3,2.2,32,V(417.5,y,12)) for y in range(-29,30,5)]
    m.cut('PSUDCEnd',vents,'Real original power-brick cooling outlets').Refine=False
    m.box('PSUShieldFloor','Independent external-supply lower metal shield',192,67,.45,(cx,0,6),'Accessories',-3,'metal',1,True)
    m.box('PSUPCB','Independent external-supply PCB; nonfunctional study',188,63,1.6,(cx,0,9),'Accessories',-2,'pcb',1,True)
    m.box('PSUTransformerCore','Separate power-transformer ferrite frame study',29,32,25,(285,0,12),'Accessories',0,'black',1,True)
    m.cut('PSUTransformerCore',m.rr(24,33,16,(285,0,16.5),.5),'Transformer coil window').Refine=False
    m.box('PSUTransformerBobbin','Separate transformer insulating bobbin',15,27,15,(285,0,17),'Accessories',0,'yellow',.7,True)
    m.feature('PSUTransformerWinding','Independent transformer winding envelope',m.rr(23,25,13,(285,0,18),1).cut(m.rr(15.5,27,13.4,(285,0,17.8),.5)),'Accessories',0,'copper',True)
    for i,(x,y,r,h) in enumerate([(240,-19,6,24),(240,19,6,24),(325,-20,4.5,18),(325,-7,4.5,18),(325,7,4.5,18),(325,20,4.5,18)]):
        m.cyl('PSUCap'+str(i),'Separate original supply capacitor envelope',r,h,(x,y,11),'Accessories',0,'black',internal=True)
        m.cyl('PSUCapTop'+str(i),'Independent supply capacitor vent',r-.4,.12,(x,y,11+h+.1),'Accessories',1,'metal',internal=True)
    for i,x in enumerate([258,310]):
        m.box('PSUHeatsink'+str(i),'Separate power-stage aluminum heatsink',2,51,27,(x,0,11),'Accessories',1,'metal',.25,True)
        for j,y in enumerate([-16,0,16]):m.box('PSUPowerDevice'+str(i)+'_'+str(j),'Independent insulated power-switch package',1.5,9,11,(x+2,y,13),'Accessories',0,'black',.2,True)
    m.ring('PSUChokeCore','Separate filter choke core envelope',7.5,4,9,(347,-17,12),'Accessories',0,'thermal',internal=True)
    import math
    for i in range(12):
        a=math.pi*i/6;center=V(347+5.75*math.cos(a),-17+5.75*math.sin(a),16.5)
        m.feature('PSUChokeTurn'+str(i),'Independent insulated filter winding',Part.makeTorus(5.2,.12,center,V(-math.sin(a),math.cos(a),0)),'Accessories',0,'copper',True)
    m.box('PSUShieldTop','Independent supply upper metal screen',132,64,.4,(290,0,40),'Accessories',2,'metal',1,True)
    _finish(m,24,'original_external_power_brick_and_internal_board','按首发电源拆解建立独立外置电源原生壳、四脚垫、屏蔽板、非功能主板、变压器、电容、散热片及滤波磁芯；不把电源移入主机，局部尺寸与器件仅用于结构学习。')
    m.snapshot('24_external_power_supply',assemblies=['Accessories'],exclude=['PSUTop','PSUShieldTop'],normal=(.4,-.6,1.4))


STAGES[24]=stage24


def stage25(m):
    import math
    from .atari2600 import _rounded_route
    x,y,z=386,0,38
    shroud=m.rr(53,57,13,(x,y,z),2).cut(Part.makeCylinder(22.2,13.4,V(x,y,z-.2)))
    shroud=shroud.cut(Part.makeBox(14,20,14,V(x+18,y-10,z-.5)))
    m.feature('PSUBlowerShroud','Independent original centrifugal blower duct',shroud,'Accessories',3,'matte',True)
    m.ring('PSUBlowerDisc','Independent centrifugal impeller disk',21,.95,.6,(x,y,z+1),'Accessories',3,'matte',internal=True)
    m.ring('PSUBlowerHub','Independent centrifugal impeller hub',6,3,9,(x,y,z+1.9),'Accessories',3,'matte',internal=True)
    m.cyl('PSUBlowerShaft','Separate blower motor shaft',.7,12,(x,y,z-.5),'Accessories',3,'metal',internal=True)
    m.ring('PSUBlowerStator','Separate blower stator core',2.6,.95,6,(x,y,z+2.5),'Accessories',3,'metal',internal=True)
    m.ring('PSUBlowerPCB','Independent blower driver board',11,1,.7,(x,y,z-.9),'Accessories',2,'pcb',internal=True)
    for i in range(35):
        blade=m.rr(5,.65,8,(18,0,0),.1);blade.rotate(V(),V(0,0,1),i*360/35+12);blade.translate(V(x,y,z+1.9))
        m.feature('PSUBlowerBlade'+str(i),'Independent centrifugal impeller blade study',blade,'Accessories',3,'matte',True)
    for i in range(2):
        points=[V(387,i*.9,36.8),V(364,i*.9,34),V(347,16+i*.9,20)]
        m.feature('PSUFanWire'+str(i),'Independent blower supply lead',_rounded_route(points,2,.22),'Accessories',1,'black' if i==0 else 'red',True)
    # AC inlet is a separate regional two-pin study, distinct from the console's DC input.
    side=g.rotation((-1,0,0),(0,0,1))
    inlet=m.rr(22,14,9,(229,0,22),3,side).cut(m.rr(18,10,9.4,(229.2,0,22),2,side))
    m.feature('PSUACSocket','Independent original two-pin AC appliance inlet',inlet,'Accessories',0,'matte',True)
    m.cut('PSUACEnd',m.rr(23,15,4,(223,0,22),3.4,side),'Separate AC inlet shell opening').Refine=False
    for i,y in enumerate([-4.5,4.5]):m.cyl('PSUACContact'+str(i),'Independent appliance inlet contact',1,5,(226,y,22),'Accessories',0,'metal',axis=(-1,0,0),internal=True)
    m.cut('PSUDCEnd',Part.makeCylinder(3.5,5,V(417,24,23),V(1,0,0)),'DC output cable strain-relief opening').Refine=False
    m.ring('PSUDCRelief','Independent molded DC output strain relief',3.2,2.5,10,(417,24,23),'Accessories',1,'matte',axis=(1,0,0),internal=True)
    route=[V(416,24,23),V(437,24,23),V(452,9,23),V(452,-61,16),V(432,-78,16),V(370,-78,16)]
    m.feature('PSUDCCable','Separate external DC display cable',_rounded_route(route,6,2.3),'Accessories',0,'black',True)
    m.box('PSUDCPlug','Independent console DC plug overmold',27,18,12,(355,-78,10),'Accessories',0,'matte',2)
    m.cut('PSUFront',m.rr(6,3,4,(339,-35,27),.6,g.rotation((0,-1,0),(0,0,1))),'Separate PSU status window').Refine=False
    m.box('PSUStatusLens','Independent original power-brick status lens',5.5,.5,2.5,(339,-37.25,25.75),'Accessories',1,'led',.4)
    _finish(m,25,'centrifugal_psu_blower_ac_dc_and_status_light','补齐首发外置电源的离心风机、独立叶轮/风罩、两线风机引线、AC 插座、DC 固定线与状态窗；风机类型与独立导光依据拆解实拍，线缆展示长度和电气部件均不作为接线或维修规格。')


STAGES[25]=stage25


def stage26(m):
    from .atari2600 import _rounded_route
    # Original single-ear wired headset, with the large controller-end volume/mute adapter.
    band=Part.makeCylinder(75,9,V(-300,-240,8),V(0,0,1),180).cut(Part.makeCylinder(72,10,V(-300,-240,7.5),V(0,0,1),180))
    band=band.common(Part.makeBox(160,80,12,V(-380,-215,7)))
    m.feature('HeadsetBand','Separate curved original single-ear headband study',band,'Accessories',0,'matte')
    for i,x in enumerate([-369.5,-230.5]):
        m.box('HeadsetSlider'+str(i),'Separate adjustable headset end arm',4.5,17,8,(x,-223.8,8.5),'Accessories',0,'matte',1)
        for j in range(5):m.box('HeadsetDetent'+str(i)+'_'+str(j),'Separate adjustment detent marker',3,.4,.1,(x,-227+j*2,16.6),'Accessories',1,'matte',.1)
    m.box('HeadsetTemple','Opposite-side cushioned temple support',14,27,6,(-230.5,-246,7),'Accessories',0,'matte',6)
    m.box('HeadsetTemplePad','Separate soft temple pad',13,25,2.5,(-230.5,-246,13.2),'Accessories',1,'rubber',5.5)
    cx=-369.5;cy=-252
    cup=Part.makeCylinder(19,7,V(cx,cy,3)).cut(Part.makeCylinder(17.5,6,V(cx,cy,4.5)))
    m.feature('HeadsetCup','Separate single-ear speaker shell',cup,'Accessories',0,'matte')
    m.ring('HeadsetDriverBasket','Separate speaker basket',15,13.5,3, (cx,cy,5),'Accessories',0,'metal',internal=True)
    m.cyl('HeadsetMagnet','Separate speaker magnet envelope',5,2.5,(cx,cy,5.1),'Accessories',0,'black',internal=True)
    m.ring('HeadsetVoiceCoil','Separate speaker voice-coil envelope',6.5,5.8,2.1,(cx,cy,5.5),'Accessories',0,'copper',internal=True)
    cone=Part.makeCone(13,3,2,V(cx,cy,8.2)).cut(Part.makeCone(12.7,2.7,2,V(cx,cy,8.3)))
    m.feature('HeadsetDiaphragm','Separate speaker diaphragm study',cone,'Accessories',0,'black',True)
    m.ring('HeadsetCushion','Separate single-ear soft cushion',19.5,11.5,6,(cx,cy,10.5),'Accessories',1,'rubber')
    grille=Part.makeCylinder(11,.12,V(cx,cy,10.26))
    holes=[Part.makeCylinder(.55,.4,V(cx+x,cy+y,10.1)) for x in range(-8,9,3) for y in range(-8,9,3) if x*x+y*y<90]
    m.feature('HeadsetGrille','Separate perforated speaker grille',grille.cut(Part.makeCompound(holes)),'Accessories',1,'matte',True)
    m.cyl('HeadsetBoomPivot','Separate reversible microphone pivot',4,2,(cx,cy,16.8),'Accessories',1,'matte')
    pts=[V(cx+4.2,cy,18.2),V(-330,-261,18.2),V(-299,-285,18.2)]
    m.feature('HeadsetBoom','Separate adjustable microphone boom study',_rounded_route(pts,5,1.5),'Accessories',1,'matte')
    mic=m.rr(17,8,6,(-290,-289,14.8),3).cut(m.rr(14,5,5,(-290,-289,16),2))
    m.feature('HeadsetMicShell','Separate microphone capsule shell',mic,'Accessories',1,'matte')
    m.cyl('HeadsetMicCapsule','Separate electret microphone envelope',2.2,2,(-290,-289,16.2),'Accessories',1,'metal',internal=True)
    m.box('HeadsetMicMesh','Separate microphone opening mesh envelope',12,4,.1,(-290,-289,20.9),'Accessories',2,'matte',1.5)
    # Cable shortened and laid out to keep both ends independently visible.
    pts=[V(cx,cy-19.2,7),V(cx,-310,7),V(-270,-340,7),V(-214,-340,7)]
    m.feature('HeadsetCable','Separate original mono headset cable display route',_rounded_route(pts,7,.9),'Accessories',0,'matte')
    m.box('HeadsetAdapterBottom','Original Xbox One headset control adapter',36,24,7,(-195,-340,2),'Accessories',0,'matte',3)
    m.cut('HeadsetAdapterBottom',m.rr(33,21,6,(-195,-340,3.4),2),'Separate headset adapter electronics cavity').Refine=False
    m.box('HeadsetAdapterTop','Separate original headset adapter lid',36,24,1.2,(-195,-340,9.2),'Accessories',1,'matte',3)
    m.box('HeadsetAdapterPCB','Independent headset control circuit board',30,18,.6,(-195,-340,4),'Accessories',0,'pcb',1,True)
    m.box('HeadsetAdapterIC','Separate headset control package',7,7,1,(-195,-340,4.8),'Accessories',0,'black',.3,True)
    for i,(x,y,label) in enumerate([(-206,-340,'-'),(-184,-340,'+'),(-195,-346,'M')]):
        m.box('HeadsetSwitch'+str(i),'Independent mute or volume switch',4,4,2,(x,y,4.8),'Accessories',0,'black',.4,True)
        m.box('HeadsetButton'+str(i),'Separate original mute or volume key',5,5,1.4,(x,y,9.4),'Accessories',2,'matte',.9)
        m.cut('HeadsetAdapterTop',m.rr(5.6,5.6,2,(x,y,9),1.1),'Headset control-key travel aperture').Refine=False
        m.label('HeadsetMark'+str(i),label,2,(x-.65,y-.8,10.84),'Accessories',2,'white')
    rear=g.rotation((0,1,0),(0,0,1))
    m.box('HeadsetExpansionPlug','Independent original proprietary controller plug',15.5,5.5,5,(-195,-327.8,6),'Accessories',0,'matte',.4,orient=rear)
    for i in range(9):m.box('HeadsetExpansionContact'+str(i),'Independent schematic expansion contact',.5,3,.1,(-195+(i-4)*1.3,-325.3,6.2),'Accessories',0,'gold',.03,True)
    m.cut('HeadsetExpansionPlug',[m.parts['HeadsetExpansionContact'+str(i)].Shape for i in range(9)],'Separate exposed headset contact channels').Refine=False
    _finish(m,26,'original_mono_chat_headset_and_three_key_adapter','加入首发单耳聊天耳麦、独立扬声器内部件、柔性麦杆、线缆及手柄端加/减音量与静音三键适配器；使用原版专用扩展插头，未套用 Xbox360 的 2.5 mm 插头和滚轮控音结构。')
    m.snapshot('26_chat_headset',assemblies=['Accessories'],exclude=[k for k in m.parts if not k.startswith('Headset')],normal=(.3,-.5,1.8))


STAGES[26]=stage26


def stage27(m):
    from .atari2600 import _rounded_route
    from .ps4 import _keyed_rear_port
    rear=g.rotation((0,1,0),(0,0,1))
    for j,x in enumerate([220,390]):
        m.box('HDMIGrip'+str(j),'Separate original HDMI cable overmold',22,32,15,(x,-190,4.5),'Accessories',0,'matte',2)
        tube=_keyed_rear_port(14.2,5.5,11,x,-173.5,12,1.1).cut(_keyed_rear_port(13.3,4.6,11.4,x,-173.7,12,.85))
        m.feature('HDMIPlugShield'+str(j),'Independent HDMI plug formed shield',tube,'Accessories',0,'metal')
        m.box('HDMIPlugTongue'+str(j),'Independent HDMI plug insulator',11.8,7,.8,(x,-167.5,11.6),'Accessories',0,'matte',.2,True)
        for row,num in enumerate([10,9]):
            for i in range(num):m.box('HDMIPlugContact'+str(j)+'_'+str(row)+'_'+str(i),'Independent HDMI cable contact',.3,5,.09,(x+(i-(num-1)/2)*1.05,-167.5,12.45 if row==0 else 11.45),'Accessories',0,'gold',.02,True)
    pts=[V(220,-206.3,12),V(220,-260,12),V(390,-260,12),V(390,-206.3,12)]
    m.feature('HDMICable','Independent bundled HDMI cable display route',_rounded_route(pts,10,2.3),'Accessories',0,'black')
    m.box('ACApplianceGrip','Separate two-pin appliance cable grip',18,27,14,(300,-320,3),'Accessories',0,'matte',2)
    front=g.rotation((0,1,0),(0,0,1))
    carrier=m.rr(20,13,9,(300,-306,10),3,front)
    carrier=carrier.cut(Part.makeCompound([Part.makeCylinder(2.6,9.4,V(x,-306.2,10),V(0,1,0)) for x in [295.5,304.5]]))
    m.feature('ACApplianceSocket','Independent two-pole appliance cable socket study',carrier,'Accessories',0,'matte')
    for i,x in enumerate([295.5,304.5]):m.ring('ACApplianceContact'+str(i),'Separate appliance cable contact sleeve',2.3,1.25,6,(x,-304.5,10),'Accessories',0,'metal',axis=(0,1,0),internal=True)
    m.box('ACWallPlug','Separate regional two-flat-pin AC plug study',28,22,14,(410,-350,0),'Accessories',0,'matte',3)
    for i,x in enumerate([403.6,416.4]):m.box('ACWallBlade'+str(i),'Independent regional flat mains blade envelope',6,1.5,12,(x,-350,14.2),'Accessories',1,'metal',.2)
    pts=[V(300,-333.8,10),V(300,-385,10),V(410,-385,10),V(410,-361.3,10)]
    m.feature('ACCable','Independent regional AC cable display route',_rounded_route(pts,7,2.5),'Accessories',0,'black')
    # Security lock opening is present on the original rear-right blank region.
    m.cut('RearFascia',m.rr(3.2,7.5,5,(-119,128,28),.5,rear),'Original rear security-lock aperture').Refine=False
    m.cut('ChassisRear',m.rr(3.2,7.5,5,(-119,123,28),.5,rear),'Security-lock aperture through metal frame').Refine=False
    _finish(m,27,'hdmi_regional_ac_cable_and_complete_original_kit','补齐双端 HDMI 线、区域两脚 AC 电源线及原版后部防盗锁孔，形成主机、1537 手柄、双 AA、Kinect2、聊天耳麦与外置电源的结构学习套装；线长、端子局部形状和附件尺寸近似，不含游戏介质或可选充电套件。')


STAGES[27]=stage27


def finalize(model):
    from .deliver import finalize as shared_finalize
    settings=App.ParamGet('User parameter:BaseApp/Preferences/Mod/Part/General');previous=settings.GetInt('WriteSurfaceCurveMode',1)
    Part.setStaticValue('write.surfacecurve.mode',1)
    try:
        result=shared_finalize(model)
        model.snapshot('final_front',normal=(.25,-1.3,.7),assemblies=model.profile['envelope_groups'])
        model.snapshot('final_controller',assemblies=['Controller'],normal=(.2,-.5,2))
        model.snapshot('final_kinect',assemblies=['Kinect'],normal=(.4,-1,.6))
        model.snapshot('final_hero',normal=(.3,-.7,1.8),assemblies=result[0]['handheld_groups'])
        model.doc.save();return result
    finally:Part.setStaticValue('write.surfacecurve.mode',previous)


def stage28(m):
    rear=g.rotation((0,1,0),(0,0,1))
    aperture=m.rr(5.7,4.7,9,tuple(_pad_point(20,37,25)),1.5,rear)
    for case in ['PadBack','PadFront']:m.cut(case,aperture,'Original controller pairing-key aperture').Refine=False
    m.box('PadSyncKey','Separate original controller pairing key',5.2,4.2,1,tuple(_pad_point(20,42,25)),'Controller',3,'matte',1.3,orient=rear)
    m.box('PadSyncSwitch','Independent original pairing-switch envelope',4,3,2,tuple(_pad_point(20,36,23)),'Controller',1,'black',.3,True)
    for i,x in enumerate([-8,8]):
        m.cyl('PadIRLED'+str(i),'Independent original controller IR emitter',1,1.8,tuple(_pad_point(x,35.5,28.6)),'Controller',2,'black',internal=True)
        m.box('PadIRWindow'+str(i),'Separate dark IR-transmitting top window',4,4,.3,tuple(_pad_point(x,43.1,31.5)),'Controller',3,'gloss',1,orient=rear)
        for case in ['PadBack','PadFront']:m.cut(case,m.rr(4.5,4.5,9,tuple(_pad_point(x,37,31.5)),1.2,rear),'Independent original controller IR window').Refine=False
    # Populate only free laminate areas; these stand for photo-visible small devices,
    # not an electrical netlist or a reconstructed manufacturer's bill of materials.
    occupied=[o.Shape.BoundBox for k,o in m.parts.items() if o.Assembly=='Controller' and not any(v in k for v in ['PadFront','PadBack','PadGripCover','PadBatteryDoor','PCB'])]
    candidates=[]
    board=m.parts['PadStickPCB'].Shape
    for yy in range(-17,30,6):
        for xx in range(-59,60,7):
            x,y,z=xx,yy-260,13.1
            if not all(board.isInside(V(x+dx,y+dy,14.6),1e-6,True) for dx in [-1.3,1.3] for dy in [-.6,.6]):continue
            if any(b.XMin-1.4<x<b.XMax+1.4 and b.YMin-.7<y<b.YMax+.7 and b.ZMin<14 and b.ZMax>12.5 for b in occupied):continue
            candidates.append((x,y))
    for i,(x,y) in enumerate(candidates[::2]):
        m.box('PadPassive'+str(i),'Photo-guided independent controller passive body',1.5,.7,.4,(x,y,13.35),'Controller',-1,'thermal',.06,True)
        for j,dx in enumerate([-.98,.98]):m.box('PadPassiveEnd'+str(i)+'_'+str(j),'Independent controller passive termination',.35,.75,.45,(x+dx,y,13.33),'Controller',-1,'metal',.03,True)
    _finish(m,28,'original_pairing_ir_windows_and_controller_passives','补齐 1537 顶端配对键、双 IR 发射件/窗口以及原版主板背面小器件；器件避让真实机构，板面分布和数量仅代表照片可见的结构层级，不声明原厂电路或 BOM。')


STAGES[28]=stage28
