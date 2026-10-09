"""Original 2020 optical Xbox Series X: published envelope, approximate local internals."""
import math,types
import FreeCAD as App
import FreeCADGui as Gui
import Part
from .core import V
from . import geometry as g


def configure(m):
    def snapshot(self,name,normal=(.8,-1,.65),assemblies=None,exclude=(),size=(1800,1400)):
        App.setActiveDocument(self.doc.Name);Gui.activateView('Gui::View3DInventor',True)
        objs=self.visible(assemblies,exclude);up=(0,1,0) if assemblies in (['Controller'],['Accessories']) or abs(normal[0])+abs(normal[1])<=.01 else (0,0,1)
        q=g.rotation(normal,up);shape=Part.makeCompound([o.Shape for o in objs]);shape.Placement=App.Placement(V(),q.inverted()).multiply(shape.Placement)
        b=shape.optimalBoundingBox(False,False);target=q.multVec(b.Center);span=max(b.YLength,b.XLength*size[1]/size[0])*1.16
        return g.render(self.out/'previews'/(name+'.png'),normal=normal,up=up,target=tuple(target),span=span,size=size)
    m.snapshot=types.MethodType(snapshot,m)
    m.colors.update(green=(.18,.48,.025),darkpcb=(.035,.055,.04),steel=(.42,.44,.46))


def _finish(m,n,slug,summary):
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=n;m.checkpoint(n,slug,summary)


def stage01(m):
    configure(m)
    m.cyl('BaseFoot','Original permanent circular stand',60,5.1,(0,0,0),'Body',-8,'black')
    m.native('BottomPlate','Vented lower enclosure plate',150.6,150.6,.8,2,(0,0,5.25),'Body',-7,'shell')
    m.native('MainShell','Original square tower enclosure',151,151,.8,290.4,(0,0,7.4),'Body',0,'accent',expr={'Width':'Parameters.Width'})
    m.cut('MainShell',m.rr(146.2,146.2,292,(0,0,6.8),.4),'Full-height tower cavity').Refine=False
    m.cut('MainShell',m.rr(145.5,6,289.5,(0,74,7.85),.3),'Separate rear-panel aperture').Refine=False
    m.box('RearPanel','Original detachable rear enclosure',145.1,2.05,289.1,(0,74.35,8.05),'Body',1,'accent',.25)
    # Bottom intake holes surround the permanent circular pedestal.
    holes=[]
    for i in range(19):
        for j in range(19):
            x=-67.5+7.5*i;y=-67.5+7.5*j
            if x*x+y*y>63*63:holes.append(Part.makeCylinder(2.25,3,V(x,y,4.8)))
    m.cut('BottomPlate',holes,'Bottom intake perforations').Refine=False
    _finish(m,1,'original_tower_enclosure_and_permanent_stand','依据官方 151×151×301 mm 包络建立原生参数化方塔壳、独立背板、底部进风板与原版固定圆形底座；壁厚与孔距按照片近似。')


STAGES={1:stage01}


def stage02(m):
    # The bowl-shaped top is a real perforated surface; green inner walls are not LEDs.
    m.native('TopGrille','Concave original exhaust grille',151,151,.8,8.9,(0,0,292.1),'Body',10,'accent')
    dish=Part.makeSphere(410,V(0,0,702.4))
    m.cut('TopGrille',dish,'Shallow concave top dish').Refine=False
    holes=[Part.makeCylinder(4.35,12,V(-65+13*i,-65+13*j,290)) for i in range(11) for j in range(11)]
    m.cut('TopGrille',holes,'Top exhaust circular perforations').Refine=False
    m.cut('TopGrille',[m.parts['MainShell'].Shape,m.parts['RearPanel'].Shape],'Top grille enclosure shoulder seats').Refine=False
    # Local green liner is offset below the curved black surface at every hole.
    for i in range(11):
        for j in range(11):
            x=-65+13*i;y=-65+13*j
            surface=702.4-math.sqrt(410**2-x*x-y*y)
            z=min(298.7,surface-.45)
            m.ring('GreenVent%02d_%02d'%(i,j),'Green interior exhaust-hole wall',4.2,3.55,1.35,(x,y,z-1.35),'Body',9,'green')
    # Rear perforation banks, photographed with the console lying on its side.
    rearholes=[]
    for side in [-1,1]:
        for i in range(6):
            for j in range(11):rearholes.append(Part.makeCylinder(3.7,4,V(side*(25+8.1*i),72.7,20+8.1*j),V(0,1,0)))
    m.cut('RearPanel',rearholes,'Twin rear intake perforation banks').Refine=False
    m.cut('RearPanel',m.rr(40,4,5,(0,74,269),2,orient=App.Rotation()),'Rear service finger recess').Refine=False
    _finish(m,2,'concave_exhaust_green_liners_and_rear_vents','加入真实通孔的凹面顶部排风格栅、逐孔绿色内衬及背部双区进风孔；绿色结构为内壁配色，不表达照明。')

STAGES[2]=stage02


def _front_shape(m,w,h,t,x,z,y=-76):
    return m.rr(w,h,t,(0,0,0),min(1.1,w/3,h/3),App.Rotation(V(1,0,0),90)).translated(V(x,y,z))


def stage03(m):
    # Original vertical slot, separate eject, pairing, USB and illuminated power button.
    slot=_front_shape(m,3.4,127,6,-62,83,y=-71.5)
    m.cut('MainShell',slot,'Front vertical optical-disc slot').Refine=False
    for dx in [-.85,.85]:m.box('DiscBrush'+str(dx),'Optical slot flexible dust brush',.65,1.1,124,(-62+dx,-74.1,21),'Controls',1,'black',.15)
    for name,x,z,r in [('Eject',-62,154,1.8),('Pair',54,48,2.1),('Power',-59,273,4.5)]:
        m.cut('MainShell',Part.makeCylinder(r+.25,6,V(x,-78,z),V(0,1,0)),name+' front key aperture').Refine=False
        m.cyl(name+'Button',name+' circular front button',r,1.4,(x,-75.3,z),'Controls',1,'white' if name=='Power' else 'black',axis=(0,1,0))
    # Front connector metal sleeve and tongue are distinct solids with empty insertion space.
    m.cut('MainShell',_front_shape(m,13.8,6.5,6,54,29,y=-71.5),'Front USB-A aperture').Refine=False
    _port(m,'FrontUSB',54,29,13.0,5.8,9,-75.15,False,'USB-A')
    # Front Xbox emblem is a geometric approximation of the crossed arcs.
    for i,angle in enumerate([-43,43]):
        sh=m.rr(.6,7,.02,(0,0,0),.1);sh.rotate(V(),V(0,0,1),angle);sh.rotate(V(),V(1,0,0),90);sh.translate(V(-59,-75.325,273))
        m.feature('PowerCross'+str(i),'Power button crossed marking',sh,'Controls',1,'accent')
    m.cut('PowerCross1',m.parts['PowerCross0'].Shape,'Crossed marking shared stroke').Refine=False
    # Rear layout follows the original 2020 photograph, with no optical S/PDIF or Kinect port.
    for name,x,z,w,h,kind in [('RearUSB1',-5,97,6,13,'USB-A'),('RearUSB2',-5,75,6,13,'USB-A'),('Ethernet',-5,51,13.5,15,'RJ45'),('Expansion',13,60,6,32,'Storage expansion'),('HDMI',13,22,6,15,'HDMI')]:
        m.cut('RearPanel',_front_shape(m,w+.6,h+.6,6,x,z,y=77),'Rear '+kind+' aperture').Refine=False
        _port(m,name,x,z,w,h,10,75.2,True,kind)
    m.cut('RearPanel',_front_shape(m,8.5,19,6,-5,22,y=77),'Rear IEC C8 inlet aperture').Refine=False
    outer=_front_shape(m,8,18,10,-5,22,y=75.2);inner=_front_shape(m,5.8,14.5,8,-5,22,y=76)
    m.feature('ACInlet','Original figure-eight AC inlet housing',outer.cut(inner),'Ports',1,'black',True)
    for z in [18,26]:m.cyl('ACPin'+str(z),'AC inlet contact pin',.8,6,(-5,68,z),'Ports',1,'metal',axis=(0,1,0),internal=True)
    _finish(m,3,'original_front_controls_and_rear_io','补齐原版竖向吸入式光盘槽、退碟/配对/电源键、前 USB，以及后双 USB、以太网、专用存储扩展、HDMI 和八字电源入口；接口为带空腔和触点的非功能结构示意。')


def _port(m,key,x,z,w,h,depth,y,rear,kind):
    # Local extrusion points toward -Y. Rear ports grow inward; front ones are mirrored.
    rot=App.Rotation(V(1,0,0),90 if rear else -90)
    origin=V(x,y,z)
    def sh(a,b,c,offset=0):
        s=m.rr(a,b,c,(0,0,offset),min(.5,a/4,b/4));s.Placement=App.Placement(origin,rot).multiply(s.Placement);return s
    shell=sh(w,h,depth).cut(sh(w-1,h-1,depth+.3,-.1))
    m.feature(key+'Shell',kind+' metal sleeve',shell,'Ports',1,'metal',True)
    tongue=sh(max(1,w-2),max(.6,(h-2)*.27),depth-2,1.5)
    m.feature(key+'Tongue',kind+' insulating tongue',tongue,'Ports',1,'black',True)
    # Pins on the tongue surface; deliberately approximate pin count for structural visualization.
    for i in range(4):
        local=m.rr(max(.25,(w-3)/7),.08,depth-3,(-w/2+1.5+i*(w-3)/3,(h-2)*.135+.06,2),.02)
        local.Placement=App.Placement(origin,rot).multiply(local.Placement)
        m.feature(key+'Contact'+str(i),kind+' schematic contact',local,'Ports',1,'gold',True)

STAGES[3]=stage03


def stage04(m):
    m.box('CenterChassis','Central cast aluminum chassis web',3.5,133,235,(0,0,16),'Frame',0,'metal',.8,True)
    # Perforated cast web, raised perimeter rails and diagonal reinforcement.
    holes=[]
    for y in [-50,-35,35,50]:
        for z in [40,55,70,195,210,225]:holes.append(Part.makeCylinder(4.5,5,V(-2.5,y,z),V(1,0,0)))
    m.cut('CenterChassis',holes,'Cast central-web ventilation').Refine=False
    for side in [-1,1]:
        m.box('ChassisEdge'+str(side),'Central cast perimeter rib',7.8,3.2,235,(0,side*68.7,16),'Frame',0,'metal',.5,True)
    for z in [13,252]:m.box('ChassisCross'+str(z),'Central transverse cast rib',8,140,2,(0,0,z),'Frame',0,'metal',.5,True)
    for i,(y,z) in enumerate([(-58,28),(58,28),(-58,238),(58,238),(-35,100),(35,165)]):
        for side in [-1,1]:
            x=1.9 if side==1 else -6.4
            m.ring('BoardBoss%d_%d'%(i,side),'Cast motherboard mounting boss',2.5,1.15,4.5,(x,y,z),'Frame',0,'metal',axis=(1,0,0),internal=True)
    # The vented carrier under the top axial fan is independently removable.
    frame=m.rr(137,137,1.6,(0,0,254.7),4).cut(Part.makeCylinder(63,3,V(0,0,254)))
    m.feature('FanCarrier','Top fan mounting carrier',frame,'Fan',8,'metal',True)
    for x in [-65,65]:
        for y in [-65,65]:m.ring('FanPillar%s_%s'%(x,y),'Fan carrier corner pillar',2.6,1.25,6.2,(x,y,248.3),'Fan',8,'metal',internal=True)
    for key in ['CenterChassis','ChassisEdge1','ChassisCross13']:
        m.cut(key,m.rr(34,16,107,(5,70,9),.5),'Central rear IO-bank chassis clearance').Refine=False
    _finish(m,4,'central_cast_chassis_and_fan_carrier','建立贯穿主机的中央铸铝中框、通风孔、加强边梁、双面主板安装柱和顶部风扇承架；双板分置中框两侧，尺寸为拆解照片近似。')

STAGES[4]=stage04


def _yz(m,key,label,depth,w,h,x,y,z,group='Mainboard',layer=3,material='darkpcb'):
    return m.box(key,label,depth,w,h,(x,y,z-h/2),group,layer,material,min(.25,depth/4),True)


def stage05(m):
    _yz(m,'APUBoard','Original APU-side motherboard',1.4,130,224,12.5,0,134)
    # Original second board has a large asymmetric cutout around the optical-drive volume.
    _yz(m,'IOBoard','Original shaped I/O-side motherboard',1.4,130,224,-7.5,0,134,layer=-2)
    notch=m.rr(3.5,45,91,(-7.5,-37,125),1)
    m.cut('IOBoard',notch,'Original large IO-board airflow and optical clearance').Refine=False
    for key,x in [('APUBoard',12.5),('IOBoard',-7.5)]:
        holes=[]
        for i,(y,z) in enumerate([(-58,28),(58,28),(-58,238),(58,238),(-35,100),(35,165)]):
            holes.append(Part.makeCylinder(1.4,3,V(x-1.5,y,z),V(1,0,0)))
            m.ring(key+'MountPad'+str(i),'Exposed copper motherboard mounting pad',2.8,1.4,.035,(x+.74,y,z),'Mainboard',3,'copper',axis=(1,0,0),internal=True)
        m.cut(key,holes,'Motherboard fixing holes').Refine=False
    _yz(m,'APUSubstrate','Original rectangular APU substrate',.85,36,42,13.9,0,133,material='pcb')
    _yz(m,'APUDie','Exposed rectangular processor die',.45,19,24,14.6,0,133,material='metal')
    # Ten GDDR6 packages: three above, four down one side, three below.
    positions=[(-23+23*i,174) for i in range(3)]+[(36,107+17*i) for i in range(4)]+[(-23+23*i,91) for i in range(3)]
    positions[6]=(36,156)
    for i,(y,z) in enumerate(positions):
        _yz(m,'GDDR6_%02d'%i,'Original GDDR6 memory package',1.3,14,12,14.0,y,z,material='black')
        _yz(m,'GDDR6Pad_%02d'%i,'Memory thermal-putty approximation',.5,13,11,15.0,y,z,'Cooling',4,'thermal')
    _yz(m,'APUThermal','Processor thermal interface',.22,19,24,14.97,0,133,'Cooling',4,'thermal')
    _yz(m,'Southbridge','Original IO-board controller package',1.6,25,28,-9.3,25,97,layer=-3,material='black')
    for i,(y,z) in enumerate([(34,146),(8,180),(-8,74),(38,205)]):_yz(m,'IOLogic'+str(i),'IO-board auxiliary logic package',.85,6,7,-8.8,y,z,layer=-3,material='black')
    _finish(m,5,'twin_motherboards_apu_and_ten_gddr6_packages','依据原版拆解建立中框两侧独立主板、I/O 板大开口、矩形 APU、十枚 GDDR6 与导热层；芯片布局与封装为非功能近似。')

STAGES[5]=stage05


def stage06(m):
    # Two banks of nine backside inductors, seen directly in the original teardown.
    for row,y in enumerate([-36,36]):
        for i in range(9):
            z=93 if row==0 and i==2 else 175 if row==1 and i==6 else 58+i*18
            _yz(m,'VRMInductor%d_%d'%(row,i),'Backside VRM power inductor',3.1,7.5,7.5,9.9,y,z,layer=1,material='steel')
            _yz(m,'VRMStage%d_%d'%(row,i),'Backside VRM switching package',.7,5.5,5.5,11.3,y+(10 if row==0 else -10),z,layer=1,material='black')
    for i,z in enumerate([78,106,134,162,190]):
        m.cyl('VRMCap'+str(i),'Backside polymer capacitor',3.1,4,(7.5,-51,z),'Mainboard',1,'black',axis=(1,0,0),internal=True)
        m.cyl('VRMCapTop'+str(i),'Polymer capacitor metal end',2.8,.15,(7.25,-51,z),'Mainboard',1,'metal',axis=(1,0,0),internal=True)
    # Clear backside island for the removable compact M.2 2230 SSD.
    _yz(m,'SSDPCB','Original removable M.2 2230 SSD board',.8,22,30,10.9,7,42,'Storage',1,'pcb')
    _yz(m,'SSDController','SSD controller package',.65,8,8,10.1,3,35,'Storage',1,'black')
    _yz(m,'SSDNAND','SSD NAND package',.8,13,14,10.0,7,47,'Storage',1,'black')
    _yz(m,'SSDConnector','M.2 edge socket',2.5,25,3,9.8,7,25,'Storage',1,'black')
    for i in range(12):_yz(m,'SSDContact'+str(i),'M.2 schematic edge contact',.03,.7,2,10.44,-2.7+i*1.75,28,'Storage',1,'gold')
    # Connector along the upper board edge joins the two boards across the central chassis.
    _yz(m,'InterboardSocketAPU','APU-side board interconnect socket',3.5,87,5,9.6,0,244,layer=1,material='black')
    _yz(m,'InterboardSocketIO','IO-side board interconnect socket',3.2,87,5,-5.05,0,244,layer=-1,material='black')
    for board,x,ys,zs in [('APU',13.45,[-50,-42,-34,-26,-18,-10,0,10,20,30,40,50],[54,64,202,213,223]),('IO',-8.55,[-8,3,14,25,36,47],[120,131,159,170,188,222])]:
        for j,z in enumerate(zs):
            for i,y in enumerate(ys):
                key=board+'SMD%d_%d'%(j,i)
                _yz(m,key,'Approximate board discrete component',.32,1.8,1.0,x,y,z,layer=3 if board=='APU' else -3,material='thermal')
                for k,dz in enumerate([-.65,.65]):_yz(m,key+'Terminal'+str(k),'Discrete component solder terminal',.25,1.7,.22,x,y,z+dz,layer=3 if board=='APU' else -3,material='metal')
    _finish(m,6,'backside_vrm_m2_storage_and_board_discretes','加入背面两列电感/开关器件、聚合物电容、可拆 M.2 2230 固态盘、双板连接插座及独立片式元件/端头；不承诺电路或引脚功能。')

STAGES[6]=stage06


def stage07(m):
    # Copper vapor chamber and stepped fin pack occupy the APU board outer face.
    _yz(m,'VaporChamber','Original copper vapor-chamber body',2.5,114,197,17,0,137,'Cooling',5,'copper')
    _yz(m,'VaporChamberRaised','Copper chamber raised center',1.0,84,157,19,0,137,'Cooling',5,'copper')
    # 48 separated aluminum fins. Each has the photographed stepped outer profile.
    for i in range(48):
        z=40+i*4
        depth=42 if 5<=i<=41 else 35
        m.box('HeatsinkFin%02d'%i,'Stepped aluminum heatsink fin',depth,112,.38,(20.1+depth/2,0,z),'Cooling',6,'metal',.12,True)
    for y in [-49,49]:
        m.box('FinTie'+str(y),'Heatsink outer vertical tie',1.2,1,189,(63.1,y,40),'Cooling',6,'metal',.2,True)
    for i,(y,z) in enumerate([(-53,46),(53,46),(-53,228),(53,228)]):
        m.ring('HeatsinkMount'+str(i),'Long heatsink retaining post',2.1,1.1,10.5,(1.95,y,z),'Cooling',3,'steel',axis=(1,0,0),internal=True)
        for key in ['APUBoard','VaporChamber']:m.cut(key,Part.makeCylinder(2.35,20,V(1,y,z),V(1,0,0)),'Heatsink long-post clearance').Refine=False
    # Top axial exhaust fan; five curved blades share a separate rotor body.
    m.ring('FanDuct','Original top axial fan duct',65,62,25,(0,0,259),'Fan',9,'black',internal=True)
    m.cyl('FanHub','Top axial fan central rotor hub',20,18,(0,0,262.5),'Fan',9,'black',internal=True)
    for i in range(5):
        points=[]
        for r,a in [(21,0),(38,-8),(60,-3),(60,40),(39,36),(21,32)]:points.append(V(r*math.cos(math.radians(a)),r*math.sin(math.radians(a)),265))
        blade=Part.Face(Part.makePolygon(points+[points[0]])).extrude(V(0,0,2.4));blade.rotate(V(),V(0,0,1),i*360/5)
        m.feature('FanBlade'+str(i),'Approximate swept axial fan blade',blade,'Fan',9,'black',True)
    for i,a in enumerate([0,90,180,270]):
        s=m.rr(40.5,2,1.2,(41.25,0,260),.3);s.rotate(V(),V(0,0,1),a)
        m.feature('FanSupport'+str(i),'Fan motor stationary support arm',s,'Fan',9,'black',True)
    m.cyl('FanMotor','Axial fan motor rear housing',18,1.8,(0,0,259.7),'Fan',9,'steel',internal=True)
    _finish(m,7,'copper_vapor_chamber_stepped_fins_and_axial_fan','加入铜均热板、48 片阶梯散热鳍片、穿板安装柱及顶部轴流风扇；叶片曲面按结构简化为扫掠轮廓，不用于流体或热性能计算。')

STAGES[7]=stage07


def stage08(m):
    # Slot-loading optical module stands vertically on the side opposite the heatsink.
    m.box('OpticalCan','Original slot-loading optical-drive can',25,134,150,(-56.5,0,15),'Optical',-6,'steel',.8,True)
    m.cut('OpticalCan',m.rr(26,132,148,(-58,0,16),.5),'Optical mechanism cavity and removable side cover').Refine=False
    _yz(m,'OpticalCover','Removable optical-drive metal cover',.7,133,149,-69.5,0,90,'Optical',-7,'metal')
    m.cut('OpticalCan',_front_shape(m,4.5,128,8,-62,83,y=-63),'Original vertical drive loading throat').Refine=False
    for y in [-63,63]:
        m.box('OpticalRail'+str(y),'Optical mechanism folded mounting rail',17,1.3,140,(-56,y,20),'Optical',-6,'metal',.3,True)
    _yz(m,'OpticalPCB','Optical drive controller board',1.0,86,48,-45.6,17,42,'Optical',-5,'pcb')
    for i,(y,z,w,h) in enumerate([(7,42,14,14),(34,45,12,9),(-13,35,7,7)]):_yz(m,'OpticalIC'+str(i),'Optical controller IC package',.8,w,h,-46.65,y,z,'Optical',-5,'black')
    for i in range(14):_yz(m,'OpticalSMD'+str(i),'Optical board discrete component',.35,2,1.2,-46.4,-18+i*4.3,57,'Optical',-5,'thermal')
    m.cyl('SpindleMotor','Optical spindle motor',11,4,(-58,0,87),'Optical',-6,'metal',axis=(1,0,0),internal=True)
    m.cyl('SpindleClamp','Optical spindle centering hub',4.5,2.5,(-60.8,0,87),'Optical',-6,'black',axis=(1,0,0),internal=True)
    for y in [-12,12]:m.cyl('LaserRail'+str(y),'Optical pickup guide rail',1,42,(-61,y,35),'Optical',-6,'metal',internal=True)
    _yz(m,'LaserCarriage','Optical pickup sliding carriage',5,20,13,-60,0,51,'Optical',-6,'black')
    m.cyl('LaserLens','Optical pickup lens',2.8,.8,(-63.5,0,51),'Optical',-6,'blue',axis=(1,0,0),internal=True)
    # Rollers lie along the disc-slot height; their support brackets are separated.
    for i,x in enumerate([-64.3,-59.7]):m.cyl('DiscLoadRoller'+str(i),'Optical disc loading rubber roller',1.2,116,(x,-59,25),'Optical',-6,'rubber',internal=True)
    for z in [22,143]:_yz(m,'LoadRollerBracket'+str(z),'Loading roller support bracket',10,5,2,-61.8,-59,z,'Optical',-6,'black')
    for i,(y,z,r) in enumerate([(42,145,6),(27,148,4.2),(15,146,5)]):
        m.cyl('OpticalGear'+str(i),'Approximate loading transmission gear',r,2,(-60,y,z),'Optical',-6,'white',axis=(1,0,0),internal=True)
        m.cyl('OpticalGearAxle'+str(i),'Loading gear axle',.8,2,(-57.8,y,z),'Optical',-6,'metal',axis=(1,0,0),internal=True)
    m.cyl('LoadMotor','Optical loading motor',5,10,(-57,44,128),'Optical',-6,'metal',axis=(1,0,0),internal=True)
    _finish(m,8,'original_slot_loading_optical_drive','建立原版吸入式光驱的可拆金属罩、控制板、主轴电机、光学滑架/镜头、导轨、进盘胶辊与近似齿轮传动；光盘未装入，保留观察内部的空腔。')

STAGES[8]=stage08


def stage09(m):
    # Original internal PSU is above the optical drive, on the I/O-board side.
    m.box('PSUCan','Original upper internal power-supply enclosure',49,130,69,(-42,0,179),'Power',-5,'steel',.8,True)
    m.cut('PSUCan',m.rr(49,128,67,(-43.1,0,180),.5),'Power-supply internal cavity and side lid opening').Refine=False
    _yz(m,'PSUCover','Removable metal power-supply side lid',.65,129,68,-67,0,213.5,'Power',-6,'metal')
    holes=[]
    for y in range(-54,55,9):
        for z in [187,196,205,214,223,232,241]:holes.append(Part.makeCylinder(2.3,2,V(-68,y,z),V(1,0,0)))
    m.cut('PSUCover',holes,'Power-supply ventilation perforations').Refine=False
    _yz(m,'PSUPCB','Internal power-supply circuit board',1.4,119,57,-20,0,213.5,'Power',-4,'pcb')
    for i,(y,z,w,h,d) in enumerate([(-33,211,23,26,19),(0,215,24,30,20),(35,211,18,23,17)]):
        _yz(m,'PSUMagnetic'+str(i),'Approximate transformer or choke core',d,w,h,-22-d/2,y,z,'Power',-5,'black')
        _yz(m,'PSUWinding'+str(i),'Magnetic component winding band',.8,w-4,h-5,-23-d,y,z,'Power',-5,'copper')
    for i,(y,z) in enumerate([(-49,231),(-47,191),(47,231),(46,191)]):
        m.cyl('PSUCap'+str(i),'Power-supply electrolytic capacitor',5,16,(-38,y,z),'Power',-5,'black',axis=(1,0,0),internal=True)
        m.cyl('PSUCapTop'+str(i),'Capacitor metal safety-vent end',4.6,.18,(-38.25,y,z),'Power',-5,'metal',axis=(1,0,0),internal=True)
    for i,y in enumerate([-17,19]):
        _yz(m,'PSUHeatsink'+str(i),'Power transistor heat spreader',12,2,42,-29,y,213,'Power',-5,'metal')
    _finish(m,9,'upper_internal_power_supply','加入位于光驱上方的原版内置电源、独立冲孔侧盖、电路板、变压器/扼流圈示意、电容与散热片；仅表达拆解结构，不构成可用电源设计。')

STAGES[9]=stage09


def stage10(m):
    _yz(m,'IOShield','Original stamped IO-side shield',.55,124,151,-13,0,96,'Shielding',-4,'metal')
    apertures=[]
    for y in [-50,-40,40,50]:
        for z in range(35,160,12):apertures.append(Part.makeCylinder(3,2,V(-14,y,z),V(1,0,0)))
    apertures.append(m.rr(3,31,36,(-13,25,79),1))
    m.cut('IOShield',apertures,'IO shield vent and southbridge relief').Refine=False
    _yz(m,'WirelessPCB','Original separate wireless daughterboard',1,53,24,-12,0,224,'Wireless',-3,'darkpcb')
    m.cut('WirelessPCB',m.rr(3,19,11,(-12,-18,227),.7),'Wireless daughterboard L-shaped corner').Refine=False
    _yz(m,'WirelessCan','Wireless RF shield can',2.2,29,16,-13.9,7,224,'Wireless',-4,'metal')
    for i,y in enumerate([-20,20]):_yz(m,'Antenna'+str(i),'Wireless printed antenna contact region',.035,9,2,-12.54,y,214,'Wireless',-3,'copper')
    m.box('FrontUSBPCB','Original USB and pairing daughterboard',18,1,35,(54,-65.3,15),'Controls',1,'pcb',.3,True)
    m.box('PairSwitch','Pairing tactile switch housing',4.5,2,4.5,(54,-67.1,45.8),'Controls',1,'metal',.3,True)
    m.cyl('PairPlunger','Pairing button actuator',.7,5.1,(54,-73.6,48),'Controls',1,'black',axis=(0,1,0),internal=True)
    m.box('PowerPCB','Original front power-button daughterboard',15,1,14,(-59,-68.8,266),'Controls',1,'pcb',.3,True)
    m.cyl('PowerLightPipe','Power-button light guide',3.7,3,(-59,-73.6,273),'Controls',1,'white',axis=(0,1,0),internal=True)
    m.box('PowerLED','Schematic power-button LED package',2.5,1,2.5,(-59,-70.1,271.75),'Controls',1,'white',.2,True)
    _finish(m,10,'io_shield_wireless_and_front_daughterboards','补齐冲压 I/O 屏蔽片、独立 L 形无线板/屏蔽罩，以及前部 USB/配对与电源按键小板；保留独立导光件和触动机构。')

STAGES[10]=stage10


def _wire(m,key,points,r=.55,mat='black'):
    from .atari2600 import _rounded_route
    return m.feature(key,'Independent insulated wire route approximation',_rounded_route([V(*p) for p in points],max(.65,r*1.3),r),'Wiring',0,mat,True)


def stage11(m):
    # Route AC in a rear-side channel up to the PSU; explicit geometric routes only.
    for i in range(2):
        x=-20-i*2
        _wire(m,'ACLead'+str(i),[(-5+i*3,64-i*2,19-i*2),(x,61+i*2,19-i*2),(x,61+i*2,174),(-40+i*3,58+i*2,175),(-40+i*3,58+i*2,178)],.65)
    for i in range(4):
        _wire(m,'PSULead'+str(i),[(-17.2,-46+i*2,188),(-15.3,-46+i*2,188),(-15.3,-55+i*2,177),(-10.8,-55+i*2,177)],.45,'red' if i<2 else 'black')
    # Optical SATA/power ribbon crosses the free space between drive and IO shield.
    for i in range(7):
        _wire(m,'OpticalData'+str(i),[(-43.8,36+i*.9,32),(-30,36+i*.9,32),(-30,53+i*.9,69),(-15,53+i*.9,69)],.25)
    for i in range(4):
        _wire(m,'OpticalPower'+str(i),[(-43.8,45+i*1.2,45),(-34,45+i*1.2,45),(-34,46+i*1.2,86),(-15,46+i*1.2,86)],.4,'red' if i<2 else 'black')
    for i in range(4):
        _wire(m,'FanLead'+str(i),[(-66.2,-11+i*1.4,266),(-70,-11+i*1.4,266),(-70,-20+i*1.4,251),(-15,-20+i*1.4,251),(-10,-20+i*1.4,249)],.35)
    # Thin flex strips run along the front wall clear of the main thermal core.
    for i in range(8):
        _wire(m,'FrontUSBLead'+str(i),[(47+i*1.6,-66.1,18),(47+i*1.6,-70.6+i*.6,12),(18+i*1.6,-70.6+i*.6,12),(18+i*1.6,-67,25)],.2)
    for i in range(3):
        _wire(m,'PowerButtonLead'+str(i),[(-54+i*1.3,-69.6,270),(-50+i*1.3,-71+i*.8,255),(-15+i*1.3,-71+i*.8,255),(-10+i*1.3,-67,240)],.28)
    _finish(m,11,'internal_ac_dc_optical_and_front_panel_wiring','加入沿独立通道布置的交流输入、直流输出、光驱数据/电源、风扇与前面板线束；路线仅表达连接关系和几何避让，不提供电气接线或线规验证。')

STAGES[11]=stage11


def _fastener(m,key,pos,axis,length=5,r=1):
    head=Part.makeCylinder(2,.65)
    pts=[V(.8*math.cos(i*math.pi/3),.8*math.sin(i*math.pi/3),-.1) for i in range(6)]
    head=head.cut(Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,.35)))
    shape=head.fuse(Part.makeCylinder(r,length,V(0,0,.6))).removeSplitter()
    shape.Placement=App.Placement(V(*pos),App.Rotation(V(0,0,1),V(*axis)))
    return m.feature(key,'Approximate recessed assembly fastener',shape,'Frame',0,'steel',True)


def stage12(m):
    for i,(y,z) in enumerate([(-58,28),(58,28),(-58,238),(58,238),(-35,100),(35,165)]):
        m.ring('APUBoardSpacer'+str(i),'APU board extended cast standoff',2.4,1.15,5.15,(6.5,y,z),'Frame',1,'metal',axis=(1,0,0),internal=True)
        _fastener(m,'APUBoardScrew'+str(i),(14.0,y,z),(-1,0,0),11.4)
        _fastener(m,'IOBoardScrew'+str(i),(-8.9,y,z),(1,0,0),6.3)
    # Screw heads are recessed into the original rear cover, preserving its envelope.
    for i,z in enumerate([115,259]):
        m.cut('RearPanel',[Part.makeCylinder(2.2,1.3,V(0,75.6,z),V(0,-1,0)),Part.makeCylinder(1.15,6,V(0,75.6,z),V(0,-1,0))],'Rear cover fastener recess').Refine=False
        _fastener(m,'RearCoverScrew'+str(i),(0,75,z),(0,-1,0),4.1)
    # Five optical fasteners and four PSU fasteners are kept separately selectable.
    for i,(y,z) in enumerate([(-58,25),(58,25),(-58,153),(58,153),(0,157)]):
        m.cut('OpticalCover',Part.makeCylinder(1.15,2,V(-70.5,y,z),V(1,0,0)),'Optical cover screw passage').Refine=False
        _fastener(m,'OpticalScrew'+str(i),(-70.5,y,z),(1,0,0),1.1)
    for i,(y,z) in enumerate([(-59,183),(59,183),(-59,244),(59,244)]):
        m.cut('PSUCover',Part.makeCylinder(1.15,2,V(-68,y,z),V(1,0,0)),'PSU side-cover screw passage').Refine=False
        _fastener(m,'PSUScrew'+str(i),(-68,y,z),(1,0,0),1.1)
    # Exterior identification remains generic; no invented serial number or certification labels.
    rear=g.rotation((0,1,0),(0,0,1))
    for key,text,x,z,size in [('ExpansionMark','STORAGE',22,71,1.55),('HDMIMark','HDMI',22,24,1.8),('RearIdentity','XBOX SERIES X',58,124,3)]:
        m.label(key,text,size,(x,75.395,z),'Body',1,'white',rotation=rear)
    o=m.parts['ExpansionMark'];ss=o.Shape.Solids;o.Shape=ss[0].multiFuse(ss[1:]).removeSplitter();o.FlatPlacement=o.Placement
    _finish(m,12,'motherboard_spacers_fasteners_and_identification','补齐双主板隔柱、独立紧固件、背板凹入螺钉、光驱/电源盖螺钉与通用接口标记；不伪造序列号或认证标签，螺纹/驱动槽按结构简化。')

STAGES[12]=stage12


def _cp(x=0,y=0,z=0):return V(x+190,y-45,z)


def _controller_curves(sx=1,sy=1):
    right=[[(0,43),(23,43),(43,43),(57,38)],[(57,38),(70,33),(77,19),(76,6)],[(76,6),(76,-13),(69,-55),(57,-60)],[(57,-60),(47,-64),(32,-32),(21,-26)],[(21,-26),(15,-24),(7,-24),(0,-24)]]
    curves=[]
    for pts in right+[[(-x,y) for x,y in reversed(s)] for s in reversed(right)]:
        b=Part.BezierCurve();b.setPoles([V(x*sx,y*sy) for x,y in pts]);curves.append(b.toBSpline())
    return curves


def _controller_loft(m,key,profiles):
    sections=[]
    for i,(sx,sy,z) in enumerate(profiles):
        curves=_controller_curves(sx,sy)
        if key.endswith('Inner'):
            # True planar inward offsets keep a wall around the concave grip waist.
            # Homothetic shrinking crosses that concavity and opens the side wall.
            wire=Part.Wire([c.toShape() for c in curves]).makeOffset2D(-2.2)
            curves=[]
            for edge in wire.Edges:
                e=edge.toNurbs().Edges[0];c=e.Curve.copy();c.segment(e.FirstParameter,e.LastParameter);curves.append(c)
        sk=m.doc.addObject('Sketcher::SketchObject',key+'Profile'+str(i));sk.addGeometry(curves,False);sk.Placement.Base=_cp(0,0,z);m.group('Construction').addObject(sk);sections.append(sk)
    o=m.doc.addObject('Part::Loft',key);o.Sections=sections;o.Solid=True;o.Ruled=False;o.MaxDegree=3;m.doc.recompute();o.Shape.check(True)
    m.group('Construction').addObject(o)
    for sk in sections:sk.Visibility=False
    o.Visibility=False;return o


def _controller_shell(m,key,outer,inner,layer):
    a=_controller_loft(m,key+'Outer',outer);b=_controller_loft(m,key+'Inner',inner)
    o=m.doc.addObject('Part::Cut',key);o.Base=a;o.Tool=b;o.Refine=False;m.doc.recompute();o.Shape.check(True);a.Visibility=False;b.Visibility=False
    return m.register(o,key,'Controller',layer,'accent')


def stage13(m):
    m.colors.update(yellow=(.9,.7,.08),xboxgreen=(.2,.65,.06),gloss=(.025,.027,.03))
    _controller_shell(m,'PadBack',[(.87,.87,0),(.97,.97,6),(1,1,15),(1,1,20)],[(.89,.89,2),(.97,.97,6),(1,1,15),(1,1,20.2)],-4)
    _controller_shell(m,'PadFront',[(1,1,20.3),(.985,.985,29),(.945,.945,35)],[(1,1,20.1),(.985,.985,28.6),(.96,.96,33)],4)
    for i,(x,w) in enumerate([(-101,55),(46,55)]):
        mask=Part.makeBox(w,130,22,_cp(x,-80,-1))
        m.feature('PadGripCover'+str(i),'Separate Series controller rear grip panel',m.parts['PadBack'].Shape.common(mask),'Controller',-4,'accent')
        m.cut('PadBack',mask,'Separate rear grip panel boundary').Refine=False
    m.cut('PadBack',m.rr(58,34,4,tuple(_cp(0,23,-1)),3),'Dual-AA removable battery door aperture').Refine=False
    m.box('PadBatteryDoor','Series controller removable AA battery door',57.5,33.5,1.4,tuple(_cp(0,23,.15)),'Controller',-5,'accent',2.8)
    _finish(m,13,'series_controller_native_curved_shell_and_grips','依据原版 Series 手柄照片建立独立原生曲线放样前后壳、可拆后握把与双 AA 电池盖；手柄尺寸和曲率为照片指导近似，后续补齐混合圆盘方向键、Share 和 USB-C。')
    m.snapshot('13_controller_shell',assemblies=['Controller'],normal=(.3,-.5,1.8))

STAGES[13]=stage13


def stage14(m):
    sticks=[(-43,13),(24,-13)];buttons=[('Y',45,22,'yellow'),('X',32,9,'blue'),('B',58,9,'red'),('A',45,-4,'xboxgreen')]
    holes=[Part.makeCylinder(12.2,12,_cp(x,y,27)) for x,y in sticks]
    holes += [Part.makeCylinder(4.8,12,_cp(x,y,27)) for _,x,y,_ in buttons]
    holes += [Part.makeCylinder(7.1,12,_cp(0,29,27)),Part.makeCylinder(13.6,12,_cp(-24,-11,27))]
    holes += [m.rr(6.8,5.8,12,tuple(_cp(x,9,27)),2.5) for x in [-13,13]]
    holes += [m.rr(9,5.8,12,tuple(_cp(0,-1,27)),2.5)]
    holes += [m.rr(28,9,12,tuple(_cp(x,35,26)),2.5) for x in [-45,45]]
    m.cut('PadFront',holes,'Series asymmetric sticks hybrid D-pad share and face keys').Refine=False
    for i,(x,y) in enumerate(sticks):
        dome=Part.makeSphere(11.8,_cp(x,y,31.3)).common(Part.makeCylinder(12,4.8,_cp(x,y,32.2))).cut(Part.makeCylinder(3.1,6,_cp(x,y,31.5)))
        m.feature('PadStickDome'+str(i),'Series thumbstick dust dome',dome,'Controller',3,'accent',True)
        m.ring('PadStickStem'+str(i),'Hollow thumbstick neck',2.8,2,9,tuple(_cp(x,y,31.5)),'Controller',4,'accent',internal=True)
        cap=Part.makeCylinder(9.5,2.5,_cp(x,y,40.8)).cut(Part.makeSphere(23,_cp(x,y,64.9)))
        m.feature('PadStickCap'+str(i),'Concave rubber thumbstick cap',cap,'Controller',5,'rubber')
    # Original hybrid disc: a shallow concave dish with distinct four cardinal pads.
    dish=Part.makeCylinder(13.2,2.2,_cp(-24,-11,34.6)).cut(Part.makeSphere(34,_cp(-24,-11,69.4)))
    m.feature('PadDPad','Series hybrid concave directional disc',dish,'Controller',5,'gloss')
    for i,(dx,dy,w,h) in enumerate([(0,8,7,8),(8,0,8,7),(0,-8,7,8),(-8,0,8,7)]):
        m.box('PadDPadCardinal'+str(i),'Raised hybrid D-pad cardinal pad',w,h,.4,tuple(_cp(-24+dx,-11+dy,36.85)),'Controller',5,'accent',.4)
    for letter,x,y,color in buttons:
        cap=Part.makeCylinder(4.4,6.3,_cp(x,y,30.9));cap=cap.makeFillet(.6,[e for e in cap.Edges if e.BoundBox.ZLength<1e-7 and e.BoundBox.ZMax>37.1])
        m.feature('PadButton'+letter,'Series '+letter+' key',cap,'Controller',4,'gloss')
        m.label('PadButtonMark'+letter,letter,3.4,tuple(_cp(x-1.2,y-1.3,37.24)),'Controller',5,color)
    m.cyl('PadXboxButton','Series Xbox guide button',6.8,2.3,tuple(_cp(0,29,35.1)),'Controller',5,'gloss')
    m.label('PadXboxMark','X',7,tuple(_cp(-2.3,26.4,37.44)),'Controller',5,'white')
    for i,x in enumerate([-13,13]):
        m.box('PadMenuKey'+str(i),'Series View or Menu key',6.3,5.3,2.3,tuple(_cp(x,9,35.1)),'Controller',5,'accent',2.3)
        m.label('PadMenuMark'+str(i),'=' if i==0 else '#',2.1,tuple(_cp(x-.8,8.2,37.44)),'Controller',5,'white')
    m.box('PadShareKey','Dedicated Series Share key',8.5,5.3,2.3,tuple(_cp(0,-1,35.1)),'Controller',5,'accent',2.3)
    m.label('PadShareMark','^',3.2,tuple(_cp(-1.1,-2.4,37.44)),'Controller',5,'white')
    for i,x in enumerate([-45,45]):
        m.box('PadBumper'+str(i),'Series shoulder bumper',27.5,8.5,5.8,tuple(_cp(x,35,29.5)),'Controller',4,'accent',2.2)
    _finish(m,14,'hybrid_disc_share_key_and_series_controls','加入 Series 原版混合圆盘方向键、独立 Share 键、非对称凹面摇杆、ABXY 彩色字标及肩键；方向键表面与按键图形为几何近似。')
    m.snapshot('14_controller_controls',assemblies=['Controller'],normal=(.25,-.5,1.8))

STAGES[14]=stage14


def _pad_board(m,key,pts,z):
    sk=m.doc.addObject('Sketcher::SketchObject',key+'Outline');vs=[V(x,y) for x,y in pts]
    sk.addGeometry([Part.LineSegment(a,b) for a,b in zip(vs,vs[1:]+vs[:1])],False);sk.Placement.Base=_cp(0,0,z);m.group('Construction').addObject(sk)
    o=m.doc.addObject('Part::Extrusion',key+'Extrusion');o.Base=sk;o.DirMode='Normal';o.LengthFwd=1.2;o.Solid=True;m.doc.recompute();sk.Visibility=False
    return m.register(o,key,'Controller',0,'pcb',True)


def stage15(m):
    # Board topology based on Microsoft Series controller service guide, not a claimed launch PCB revision.
    rear=[(-62,31),(-67,4),(-58,-16),(-38,-23),(38,-23),(58,-16),(67,4),(62,31),(29,31),(29,3),(-29,3),(-29,31)]
    front=[(-22,38),(22,38),(25,28),(58,28),(63,10),(60,-22),(36,-27),(9,-27),(9,-23),(-50,-23),(-63,-12),(-59,4),(-24,4)]
    _pad_board(m,'PadMainPCB',rear,14)
    _pad_board(m,'PadIOPCB',front,27)
    m.cut('PadIOPCB',[Part.makeCylinder(12.5,2,_cp(x,y,26.7)) for x,y in [(-43,13),(24,-13)]],'Series stick passages through IO board').Refine=False
    for key,inner in [('PadIOPCB','PadFrontInner'),('PadMainPCB','PadBackInner')]:
        outside=Part.makeBox(250,200,60,_cp(-125,-100,0)).cut(m.doc.getObject(inner).Shape)
        m.cut(key,outside,'Native curved inner-shell board envelope').Refine=False
    m.box('PadMCU','Series controller main processor package',12,12,1.1,tuple(_cp(42,-6,12.5)),'Controller',-1,'black',.3,True)
    for side in range(4):
        for i in range(10):
            a=(i-4.5)*.95;x,y=(42+a,-6+(6.5 if side==0 else -6.5)) if side<2 else (42+(6.5 if side==2 else -6.5),-6+a)
            m.box('PadMCULead%d_%d'%(side,i),'Schematic controller processor lead',.28 if side<2 else .65,.65 if side<2 else .28,.15,tuple(_cp(x,y,13.7)),'Controller',-1,'metal',.03,True)
    m.box('PadRadioShield','Series controller RF shield',21,24,1.2,tuple(_cp(-42,-1,12.4)),'Controller',-1,'metal',.5,True)
    m.box('PadCrystal','Series controller crystal package',6,2.5,.8,tuple(_cp(-12,-14,12.9)),'Controller',-1,'metal',.3,True)
    for i,(x,y) in enumerate([(-8,-13),(44,-14)]):
        m.box('PadStackSocket'+str(i),'Controller board-stack socket',10,4.5,2,tuple(_cp(x,y,15.6)),'Controller',1,'black',.3,True)
        m.box('PadStackPlug'+str(i),'Controller board-stack plug carrier',10,4.5,1.7,tuple(_cp(x,y,24.9)),'Controller',2,'black',.3,True)
        for j in range(10):m.cyl('PadStackPin%d_%d'%(i,j),'Schematic board-stack contact',.16,6.7,tuple(_cp(x+(j-4.5)*.8,y,17.9)),'Controller',1,'gold',internal=True)
    # Independent two-axis analog modules with gimbals, potentiometer housings and terminals.
    for i,(x,y) in enumerate([(-43,13),(24,-13)]):
        frame=m.rr(16,16,9,tuple(_cp(x,y,16)),1).cut(m.rr(12.5,12.5,10,tuple(_cp(x,y,15.5)),.7))
        m.feature('PadAnalogFrame'+str(i),'Analog stick metal frame',frame,'Controller',1,'metal',True)
        m.cyl('PadGimbalX'+str(i),'Analog X pivot shaft',1.1,11,tuple(_cp(x-5.5,y,21)),'Controller',2,'metal',axis=(1,0,0),internal=True)
        m.cyl('PadGimbalY'+str(i),'Analog Y pivot shaft',1.1,11,tuple(_cp(x,y-5.5,24)),'Controller',2,'metal',axis=(0,1,0),internal=True)
        m.cyl('PadAnalogShaft'+str(i),'Analog stick upper shaft',1.7,6.5,tuple(_cp(x,y,24.3)),'Controller',3,'black',internal=True)
        m.cut('PadAnalogShaft'+str(i),m.parts['PadGimbalY'+str(i)].Shape,'Gimbal-to-shaft pivot clearance').Refine=False
        for side in [0,1]:
            xx,yy=(x+10,y) if side==0 else (x,y+10)
            m.box('PadPot%d_%d'%(i,side),'Analog potentiometer housing',3 if side==0 else 10,10 if side==0 else 3,6,tuple(_cp(xx,yy,16.5)),'Controller',1,'xboxgreen',.35,True)
            for j in range(3):
                px,py=(xx,yy+(j-1)*3) if side==0 else (xx+(j-1)*3,yy)
                m.cyl('PadPotPin%d_%d_%d'%(i,side,j),'Analog potentiometer terminal',.24,1.0,tuple(_cp(px,py,15.3)),'Controller',1,'metal',internal=True)
    _finish(m,15,'series_dual_boards_rf_and_analog_mechanisms','依据微软 Series 手柄维修资料建立 U 形主板、独立开孔 I/O 板、屏蔽区、板间连接器和双轴摇杆机构；资料用于结构拓扑，不宣称与 2020 首发 PCB 修订号完全一致。')

STAGES[15]=stage15


def stage16(m):
    for i,(dx,dy) in enumerate([(0,6),(6,0),(0,-6),(-6,0)]):
        x,y=-24+dx,-11+dy
        m.cyl('PadDPadContact'+str(i),'Hybrid directional key copper contact',2.5,.035,tuple(_cp(x,y,28.24)),'Controller',1,'gold',internal=True)
        dome=Part.makeSphere(5.5,_cp(x,y,23.35)).common(Part.makeCylinder(2.9,.65,_cp(x,y,28.32)))
        m.feature('PadDPadDome'+str(i),'Directional metal snap dome',dome,'Controller',2,'metal',True)
        m.cyl('PadDPadPlunger'+str(i),'Hybrid directional-key plunger',1.25,5.3,tuple(_cp(x,y,29.05)),'Controller',3,'black',internal=True)
    for key,x,y,r in [('A',45,-4,3.1),('B',58,9,3.1),('X',32,9,3.1),('Y',45,22,3.1),('View',-13,9,2.1),('Menu',13,9,2.1),('Share',0,-1,2.3),('Xbox',0,29,3.5)]:
        for side in range(2):
            half=Part.makeCylinder(r,.035,V(),V(0,0,1),180);half.rotate(V(),V(0,0,1),side*180);half=half.cut(Part.makeBox(2*r+1,.3,.2,V(-r-.5,-.15,-.05)));half.translate(_cp(x,y,28.24))
            m.feature('Pad'+key+'Contact'+str(side),'Split controller key contact',half,'Controller',1,'gold',True)
        m.cyl('Pad'+key+'Carbon','Conductive controller key pill',r-.3,.15,tuple(_cp(x,y,28.4)),'Controller',2,'black',internal=True)
        height=2 if key in ['A','B','X','Y'] else 5.8
        sh=Part.makeCone(r+1.1,r-.2,height,_cp(x,y,28.65)).cut(Part.makeCone(r+.65,r-.65,height+.1,_cp(x,y,28.55)))
        m.feature('Pad'+key+'Silicone','Controller silicone key diaphragm',sh,'Controller',2,'rubber',True)
    # USB-C and 3.5 mm audio distinguish this model from the early Xbox One controller.
    q=g.rotation((0,1,0),(0,0,1))
    outer=m.rr(9.2,3.7,5,tuple(_cp(0,38,24)),1.5,q)
    inner=m.rr(8.4,2.9,5.4,tuple(_cp(0,37.8,24)),1.2,q)
    m.feature('PadUSBCShell','Series controller USB-C receptacle sleeve',outer.cut(inner),'Controller',2,'metal',True)
    m.box('PadUSBCTongue','USB-C center insulating tongue',6.5,3,.5,tuple(_cp(0,40.4,23.75)),'Controller',2,'black',.2,True)
    for i in range(8):m.box('PadUSBCPin'+str(i),'USB-C schematic contact',.35,2,.05,tuple(_cp((i-3.5)*.7,40.4,24.3)),'Controller',2,'gold',.02,True)
    for key in ['PadBack','PadFront']:m.cut(key,m.rr(10,4.6,12,tuple(_cp(0,35,24)),1.6,q),'Series USB-C shell opening').Refine=False
    m.ring('PadAudioJack','Series 3.5 mm audio-jack sleeve',2.5,1.8,7,tuple(_cp(0,-23.5,18)),'Controller',1,'black',axis=(0,1,0),internal=True)
    m.ring('PadAudioRim','Audio jack conductive rim',2.3,1.8,.4,tuple(_cp(0,-24,18)),'Controller',1,'metal',axis=(0,1,0),internal=True)
    for key in ['PadBack','PadFront']:m.cut(key,Part.makeCylinder(2.75,14,_cp(0,-34,18),V(0,1,0)),'Series audio-jack enclosure opening').Refine=False
    _finish(m,16,'series_contact_layers_usb_c_and_audio','补齐混合方向键金属弹片、ABXY/View/Menu/Share/Xbox 接点与导电胶，加入 USB-C、3.5 mm 音频接口的独立空腔、舌片与接点示意。')

STAGES[16]=stage16


def stage17(m):
    carrier=m.rr(54,34,12.5,tuple(_cp(0,20.5,2.5)),2).cut(m.rr(51,32,14,tuple(_cp(0,20.5,2)),1.5))
    m.feature('PadBatteryTray','Dual-AA battery carrier frame',carrier,'Controller',-3,'black',True)
    for i,y in enumerate([12,29]):
        m.cyl('PadAA'+str(i),'Replaceable AA cell approximation',6.8,47,tuple(_cp(-23.5,y,10)),'Controller',-3,'battery',axis=(1,0,0),internal=True)
        for side in [-1,1]:
            x=-24.1 if side==-1 else 23.6
            m.cyl('PadAATerminal%d_%d'%(i,side),'AA cell terminal',2.5,.35,tuple(_cp(x,y,10)),'Controller',-3,'metal',axis=(1,0,0),internal=True)
            m.box('PadAAContact%d_%d'%(i,side),'AA compartment spring-contact approximation',.25,5,7,tuple(_cp(side*24.7,y,6.5)),'Controller',-3,'metal',.05,True)
    # Two grip motors and two smaller impulse-trigger motors, as documented in the service guide.
    for i,x in enumerate([-54,54]):
        m.cyl('PadGripMotor'+str(i),'Controller grip vibration motor',6,17,tuple(_cp(x,-33,8)),'Controller',-2,'metal',internal=True)
        weight=Part.makeCylinder(5.5,2.4,_cp(x,-33,25.3),V(0,0,1),210)
        m.feature('PadGripWeight'+str(i),'Grip motor eccentric mass',weight,'Controller',1,'steel',True)
        m.cyl('PadTriggerMotor'+str(i),'Impulse trigger vibration motor',3.6,11,tuple(_cp(x,27,8)),'Controller',-2,'metal',internal=True)
        m.cyl('PadTriggerWeight'+str(i),'Impulse motor eccentric mass',2.5,1.8,tuple(_cp(x+1,27,19.3)),'Controller',1,'steel',internal=True)
    for i,x in enumerate([-46,46]):
        trigger=m.rr(23,12,14,tuple(_cp(x,38,8)),3)
        m.feature('PadTrigger'+str(i),'Separate analog impulse trigger',trigger,'Controller',0,'accent')
        for key in ['PadBack','PadFront','PadGripCover0','PadGripCover1']:m.cut(key,m.rr(24,15,16,tuple(_cp(x,38,7)),3.2),'Trigger travel envelope opening').Refine=False
        m.cyl('PadTriggerAxle'+str(i),'Analog trigger pivot pin',1,24,tuple(_cp(x-12,34,24)),'Controller',1,'metal',axis=(1,0,0),internal=True)
        m.ring('PadTriggerSpring'+str(i),'Simplified trigger return-spring collar',2.3,1.2,3,tuple(_cp(x-1.5,34,24)),'Controller',1,'metal',axis=(1,0,0),internal=True)
    m.cut('PadMainPCB',[Part.makeCylinder(3.9,15,_cp(x,27,7)) for x in [-54,54]],'Impulse motor board-edge clearance').Refine=False
    m.cut('PadBatteryTray',[m.parts['PadBack'].Shape,m.parts['PadFront'].Shape],'Battery carrier curved-shell clearance').Refine=False
    for i in range(2):m.cut('PadTrigger'+str(i),m.parts['PadTriggerSpring'+str(i)].Shape,'Trigger return collar recess').Refine=False
    _finish(m,17,'dual_aa_cells_four_motors_and_analog_triggers','加入可拆双 AA、电池托架与触点、两组握把振动电机和两组扳机振动电机，以及独立扳机、转轴与简化回位件；电池和电机为结构示意。')

STAGES[17]=stage17


def _pad_wire(m,key,pts,r=.23):
    from .atari2600 import _rounded_route
    sh=_rounded_route([_cp(*p) for p in pts],.7,r)
    return m.feature(key,'Controller internal wire route study',sh,'Controller',-1,'black',True)


def stage18(m):
    _pad_wire(m,'PadCoax0',[(-42,-12,11.7),(-35,-17,11.7),(20,-17,11.7),(29,-5,11.7),(45,0,11.7)])
    _pad_wire(m,'PadCoax1',[(-42,5,11.7),(-56,0,11.7),(-58,-10,11.7),(-54,-20.5,11.7),(45,-20.5,11.7)])
    for i,(x,y) in enumerate([(-42,-12),(45,0),(-42,5),(45,-20.5)]):m.cyl('PadCoaxEnd'+str(i),'Coaxial board-connector approximation',.65,.2,tuple(_cp(x,y,12.05)),'Controller',-1,'gold',internal=True)
    for side in [-1,1]:
        for i in range(2):
            _pad_wire(m,'PadGripLead%d_%d'%(side,i),[(side*(54+i*.9),-33+i*1.1,7.7-i*.65),(side*(54+i*.9),-23+i*1.1,6-i*.65),(side*(30+i*.9),-19+i*1.1,12.7-i*.65)],.2)
            _pad_wire(m,'PadTriggerLead%d_%d'%(side,i),[(side*54,27+i*1.1,7.7-i*.65),(side*62,27+i*1.1,6-i*.65),(side*63,8+i*1.1,6-i*.65),(side*52,-3+i*1.1,12-i*.65)],.2)
    for i,(x,y) in enumerate([(-60,0),(60,0),(-45,-37),(45,-37),(0,20.5)]):
        ro=1.4 if i==4 else 2.0
        post=Part.makeCylinder(ro,26.5,_cp(x,y,4.5)).cut(Part.makeCylinder(1.05,27.5,_cp(x,y,4)))
        # Posts follow the native inner enclosure surfaces and leave room for separate shell walls.
        post=post.cut(Part.makeCompound([m.parts[k].Shape for k in ['PadBack','PadFront','PadGripCover0','PadGripCover1']]))
        m.feature('PadCasePost'+str(i),'Controller case screw guide post',post,'Controller',0,'accent',True)
        for key in ['PadMainPCB','PadIOPCB']:m.cut(key,Part.makeCylinder(ro+.2,18,_cp(x,y,13)),'Controller case-post board clearance').Refine=False
        m.cyl('PadCaseScrew'+str(i),'Controller case screw shaft',.85,25.2,tuple(_cp(x,y,4.7)),'Controller',0,'steel',internal=True)
        m.ring('PadCaseHead'+str(i),'Controller recessed screw head',1.35,.5,.5,tuple(_cp(x,y,3.9)),'Controller',-3,'steel',internal=True)
    # Four IO-board and two main-board screws are distinct from the case screws.
    for i,(x,y,z) in enumerate([(-52,-9,28.4),(52,-9,28.4),(-19,26,28.4),(19,26,28.4),(-40,27,15.45),(40,27,15.45)]):
        m.ring('PadBoardHead'+str(i),'Controller board fastener head',1.2,.45,.3,tuple(_cp(x,y,z)),'Controller',1,'metal',internal=True)
        m.cyl('PadBoardShaft'+str(i),'Controller board fastener shank',.55,1.1,tuple(_cp(x,y,z-1.3)),'Controller',0,'metal',internal=True)
        key='PadIOPCB' if i<4 else 'PadMainPCB';m.cut(key,Part.makeCylinder(.7,2,_cp(x,y,z-1.6)),'Controller board fastener hole').Refine=False
    _finish(m,18,'controller_coax_motor_wires_and_separate_fasteners','加入双同轴、四组电机导线、五组壳体导柱/螺钉，以及维修资料所示四枚 I/O 板和两枚主板紧固件；导线路径与接头为可检查的近似结构。')

STAGES[18]=stage18


def stage19(m):
    # Standalone included cable ends are presented clear of the console and controller.
    for key,x,y,w,h,d in [('HDMICableA',-160,-20,16,6,12),('HDMICableB',-160,35,16,6,12)]:
        m.box(key+'Grip','HDMI cable molded plug grip',w+4,d+8,h+2,(x,y,3),'Accessories',0,'black',2)
        metal=m.rr(w,h,7,(x,y+d/2+4,7),.7,g.rotation((0,1,0),(0,0,1)))
        void=m.rr(w-1,h-1,8,(x,y+d/2+3.5,7),.5,g.rotation((0,1,0),(0,0,1)))
        m.feature(key+'Sleeve','HDMI plug metal sleeve',metal.cut(void),'Accessories',0,'metal')
    from .atari2600 import _rounded_route
    cable=_rounded_route([V(-160,-30.4,7),V(-183,-45,7),V(-203,-45,7),V(-203,55,7),V(-183,55,7),V(-160,24.6,7)],7,2.3)
    m.feature('HDMICable','Schematic included HDMI cable',cable,'Accessories',0,'black')
    m.box('ACPlugBody','Generic included AC cable plug body',22,28,13,(-145,100,3),'Accessories',0,'black',3)
    m.box('C7CableGrip','Figure-eight cable appliance-end grip',15,22,10,(-190,101,3),'Accessories',0,'black',3)
    inlet=Part.makeCylinder(4,10,V(-193,112.5,8),V(0,1,0)).fuse(Part.makeCylinder(4,10,V(-187,112.5,8),V(0,1,0)))
    inlet=inlet.cut(Part.makeCompound([Part.makeCylinder(1.2,11,V(x,112,8),V(0,1,0)) for x in [-193,-187]]))
    m.feature('C7CableTip','Figure-eight appliance connector tip',inlet,'Accessories',0,'black')
    cable=_rounded_route([V(-145,85.5,8),V(-145,70,8),V(-168,65,8),V(-190,72,8),V(-190,89.5,8)],4,2)
    m.feature('ACAccessoryCable','Schematic included AC cable',cable,'Accessories',0,'black')
    for key in ['HDMICableAGrip','HDMICableBGrip']:m.cut(key,m.parts['HDMICable'].Shape,'HDMI molded cable-entry seat').Refine=False
    for key in ['ACPlugBody','C7CableGrip']:m.cut(key,m.parts['ACAccessoryCable'].Shape,'AC molded cable-entry seat').Refine=False
    _finish(m,19,'standalone_hdmi_and_ac_cable_accessories','加入独立展示的 HDMI 与八字电源线附件、带空腔的接头；墙端插头采用通用示意外形，不指定地区插脚或电气认证。')

STAGES[19]=stage19


def finalize(model):
    from .deliver import finalize as shared_finalize
    configure(model)
    previous=App.ParamGet('User parameter:BaseApp/Preferences/Mod/Part/General').GetInt('WriteSurfaceCurveMode',1)
    Part.setStaticValue('write.surfacecurve.mode',1)
    try:
        result=shared_finalize(model);report,exploded=result
        # The translated offset shell requires 3D boundary curves on STEP export;
        # redundant surface curves can reverse a face during the STEP round trip.
        import ImportGui
        Part.setStaticValue('write.surfacecurve.mode',0)
        ImportGui.export([o for o in exploded.Objects if 'PartID' in o.PropertiesList],str(model.out/'XboxSeriesX_Exploded.step'))
        Part.setStaticValue('write.surfacecurve.mode',1)
        console=model.profile['envelope_groups']
        model.snapshot('final_front',normal=(0,-1,0),assemblies=console)
        model.snapshot('final_back',normal=(0,1,0),assemblies=console)
        model.snapshot('final_console',normal=(.8,-1,.65),assemblies=console)
        model.snapshot('final_board',normal=(1,0,0),assemblies=['Mainboard','Storage'])
        model.snapshot('final_thermal',normal=(1,-.6,.5),assemblies=['Cooling','Fan'])
        model.snapshot('final_optical',normal=(-1,-.5,.45),assemblies=['Optical'],exclude=['OpticalCover'])
        model.snapshot('final_power',normal=(-1,-.3,.4),assemblies=['Power'],exclude=['PSUCover'])
        model.snapshot('final_controls',normal=(.2,-.5,1.8),assemblies=['Controller'])
        model.snapshot('final_controller_internal',normal=(.2,-.5,1.8),assemblies=['Controller'],exclude=['PadBack','PadFront','PadGripCover0','PadGripCover1','PadBatteryDoor','PadStickDome0','PadStickDome1','PadStickCap0','PadStickCap1'])
        def exploded_view(name,groups,normal,up):
            App.setActiveDocument(exploded.Name);Gui.activateView('Gui::View3DInventor',True)
            objs=[o for o in exploded.Objects if 'Assembly' in o.PropertiesList and o.Assembly in groups]
            g.set_visible_components(exploded,objs);q=g.rotation(normal,up);shape=Part.makeCompound([o.Shape for o in objs]);shape.Placement=App.Placement(V(),q.inverted()).multiply(shape.Placement)
            b=shape.optimalBoundingBox(False,False);span=max(b.YLength,b.XLength*1700/2300)*1.14
            return g.render(model.out/'previews'/(name+'.png'),normal=normal,up=up,target=tuple(q.multVec(b.Center)),span=span,size=(2300,1700))
        exploded_view('final_exploded',console,(.4,-1,.45),(0,0,1))
        exploded_view('final_exploded_body',console,(.4,-1,.45),(0,0,1))
        exploded_view('final_exploded_controller',['Controller'],(1.3,-.3,.4),(0,1,0))
        for o in exploded.Objects:
            if 'Assembly' in o.PropertiesList:o.Visibility=True
        exploded.save()
        model.snapshot('final_hero',normal=(.8,-1,.65),assemblies=console+['Controller']);model.doc.save()
        return result
    finally:Part.setStaticValue('write.surfacecurve.mode',previous)
