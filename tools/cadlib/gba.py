"""Original AGB-001 Game Boy Advance, early reflective LCD and dual-AA structure."""
import math
import FreeCAD as App
import Part
from .core import V


def _curves(sx=1,sy=1):
    # Photo-guided organic perimeter, constrained to Nintendo's nominal envelope.
    right=[[(0,41),(20,41),(45,38),(58,32)],[(58,32),(69,29),(72.25,16),(72.25,0)],[(72.25,0),(72.25,-23),(62,-31),(42,-36)],[(42,-36),(28,-39),(13,-41),(0,-41)]]
    segments=right+[[(-x,y) for x,y in reversed(s)] for s in reversed(right)]
    result=[]
    for points in segments:
        b=Part.BezierCurve();b.setPoles([V(x*sx,y*sy) for x,y in points]);result.append(b.toBSpline())
    return result


def _loft(m,key,profiles):
    sketches=[]
    for i,(sx,sy,z) in enumerate(profiles):
        sk=m.doc.addObject('Sketcher::SketchObject',key+'Profile'+str(i));sk.Label='Editable AGB-001 curved shell section '+str(i+1)
        sk.addGeometry(_curves(sx,sy),False);sk.Placement.Base=V(0,0,z)
        m.group('Construction').addObject(sk);sketches.append(sk)
    shape=m.doc.addObject('Part::Loft',key);shape.Sections=sketches;shape.Solid=True;shape.Ruled=False;shape.MaxDegree=3
    m.doc.recompute()
    # Smooth lofts can overshoot their sections. Fit the editable section poles
    # to the intended envelope rather than clipping away the curved surface.
    target_x=144.5*max(p[0] for p in profiles);target_y=82*max(p[1] for p in profiles)
    fit_x=fit_y=1.0
    for attempt in range(7):
        bounds=shape.Shape.optimalBoundingBox(False,False)
        if max(abs(bounds.XLength-target_x),abs(bounds.YLength-target_y))<1e-6:break
        fit_x*=target_x/bounds.XLength;fit_y*=target_y/bounds.YLength
        for sk,(sx,sy,z) in zip(sketches,profiles):
            for index in reversed(range(sk.GeometryCount)):sk.delGeometry(index)
            sk.addGeometry(_curves(sx*fit_x,sy*fit_y),False)
        m.doc.recompute()
    else:raise AssertionError('Shell envelope did not converge: '+key)
    shape.Shape.check(True);assert len(shape.Shape.Solids)==1
    m.group('Construction').addObject(shape)
    for sk in sketches:sk.Visibility=False
    shape.Visibility=False;return shape


def _shell(m,key,outer,inner,layer):
    a=_loft(m,key+'Outer',outer);b=_loft(m,key+'Inner',inner)
    o=m.doc.addObject('Part::Cut',key);o.Base=a;o.Tool=b;o.Refine=False;m.doc.recompute()
    o.Shape.check(True);assert len(o.Shape.Solids)==1
    a.Visibility=False;b.Visibility=False
    return m.register(o,key,'Body',layer,'indigo')


def _finish(m,n,slug,summary):
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=n
    m.checkpoint(n,slug,summary)


def stage01(m):
    m.colors.update(indigo=(.24,.22,.49),agbgray=(.48,.49,.53),agblcd=(.28,.31,.29),agbink=(.13,.13,.22),silicone=(.57,.58,.62))
    _shell(m,'BackCover',[(.92,.88,0),(.986,.98,4),(1,1,11.4)],[(.891,.846,1.5),(.953,.946,4),(.969,.962,11.6)],-6)
    _shell(m,'FrontCover',[(1,1,11.6),(.991,.983,18.7),(.957,.932,23.3)],[(.969,.962,11.4),(.956,.942,18.6),(.923,.894,21.9)],4)
    _finish(m,1,'agb001_curved_native_shell','按原版 144.5 × 82 mm 名义包络建立前后原生曲线放样壳、独立内腔与分壳间隙；24.5 mm 厚度包络待按键完成后检查，局部曲率与壁厚近似。')


STAGES={1:stage01}


def stage02(m):
    m.cut('FrontCover',m.rr(77.0,63.0,8,(0,1.5,17),7.5),'Original reflective-display lens aperture').Refine=False
    m.native('DisplayBezel','Editable original grey display-lens border',76.6,62.6,7.3,.55,(0,1.5,23.35),'Display',5,'agbgray',expr={'Width':'Parameters.Width - 67.9 mm'})
    m.cut('DisplayBezel',m.rr(61.45,41.05,1,(0,4.5,23.15),.12),'61.2 x 40.8 mm reflective TFT viewing aperture').Refine=False
    m.box('LCDMetalBack','Separate LCD metal rear plate',72,52,.3,(0,4.5,17.8),'Display',1,'metal',.5,True)
    m.box('LCDReflector','Nonilluminated LCD rear reflector',70,50,.15,(0,4.5,18.2),'Display',1,'white',.4,True)
    m.box('LCDModule','Original reflective TFT cell module',69.5,49.5,4.45,(0,4.5,18.4),'Display',2,'black',.4,True)
    m.box('LCDPolarizer','Reflective optical polarizer; no backlight',61.2,40.8,.12,(0,4.5,23.02),'Display',3,'agblcd',.08,True)
    m.box('DisplayGlass','Published 61.2 x 40.8 mm display region',61.2,40.8,.22,(0,4.5,23.32),'Display',6,'agblcd',.08)
    m.label('AdvanceMark','GAME BOY ADVANCE',2.4,(-18.5,-24.4,23.92),'Display',6,'white')
    m.label('NintendoMark','Nintendo',2.5,(-7.8,34.0,23.32),'Body',4,'agbink')
    _finish(m,2,'reflective_tft_lens_and_original_bezel','加入官方 61.2 × 40.8 mm 反射 TFT 可视区、独立玻璃/偏光片/液晶模块/反射片/金属背板和灰色原版镜框；不加入前光、背光或后装 IPS。镜框原生宽度约束关联 Parameters.Width。')


STAGES[2]=stage02


def stage03(m):
    x,y=-53,1
    cross=m.rr(6.1,20.5,1.15,(x,y,23.35),.5).fuse(m.rr(20.5,6.1,1.15,(x,y,23.35),.5)).removeSplitter()
    hole=m.rr(6.45,20.85,8,(x,y,18),.6).fuse(m.rr(20.85,6.45,8,(x,y,18),.6))
    m.cut('FrontCover',hole,'Original cross-pad aperture').Refine=False
    m.feature('DPad','Original single cross directional cap',cross.cut(Part.makeSphere(4.5,V(x,y,28.8))),'Controls',6,'agbgray')
    for i,(dx,dy) in enumerate([(0,6),(6,0),(0,-6),(-6,0)]):
        m.cyl('DPadStem'+str(i),'Separate directional plunger study',1.35,2.05,(x+dx,y+dy,21.2),'ControlsInternal',3,'agbgray',internal=True)
    for key,x,y in [('A',57,8),('B',44,0)]:
        m.cut('FrontCover',Part.makeCylinder(4.75,8,V(x,y,18)),key+' action-key aperture').Refine=False
        shape=Part.makeCylinder(4.5,2.762,V(x,y,21.7))
        shape=shape.makeFillet(.35,[e for e in shape.Edges if e.BoundBox.ZLength<1e-6 and e.BoundBox.ZMax>24.4])
        m.feature('Button'+key,key+' original circular action key',shape,'Controls',6,'agbgray')
        m.label('ButtonMark'+key,key,2.4,(x-.9,y-1,24.482),'Controls',6,'agbink')
    for key,x,y in [('Start',-47,-20),('Select',-47,-27)]:
        shape=m.rr(9.5,3.6,.95,(x,y,23.35),1.7);shape.rotate(V(x,y,0),V(0,0,1),-10)
        hole=m.rr(9.85,3.95,8,(x,y,18),1.85);hole.rotate(V(x,y,0),V(0,0,1),-10)
        m.cut('FrontCover',hole,'Original '+key+' key slot').Refine=False
        m.feature('Button'+key,key+' original grey rubber key',shape,'Controls',6,'agbgray')
        m.box('ButtonStem'+key,key+' independent plunger study',6,2.5,2.05,(x,y,21.2),'ControlsInternal',3,'silicone',1,True)
        m.label(key+'Mark',key.upper(),1.6,(x-5.3,y+2.5,23.32),'Body',4,'agbink')
    _finish(m,3,'original_dpad_ab_start_select','加入单体十字键、分离的 A/B 圆键和 Start/Select 键，保留原版两键布局、独立柱脚与真实穿壳孔；按键最高点为名义 24.5 mm，未加入后代掌机的 X/Y。')


STAGES[3]=stage03


def stage04(m):
    holes=[]
    for i in range(5):
        y=-16.5-i*2.8
        slot=m.rr(14.2,1.2,8,(51,y,18),.58);slot.rotate(V(51,y,0),V(0,0,1),18);holes.append(slot)
    m.cut('FrontCover',holes,'Five original diagonal mono-speaker grille slots').Refine=False
    m.cut('FrontCover',Part.makeCylinder(1.25,8,V(46,26,18)),'Original power-indicator aperture').Refine=False
    m.cyl('PowerLEDLens','Separate original green power-status lens',1.05,.18,(46,26,23.32),'Display',5,'led')
    m.cyl('PowerLEDGuide','Independent power-status light guide',.8,2.0,(46,26,21.2),'Display',3,'white',internal=True)
    m.label('PowerMark','POWER',1.6,(48,25.3,23.32),'Body',4,'agbink')
    for side,x in [('L',-52),('R',52)]:
        aperture=m.rr(26.4,9.4,7,(x,32.5,18),3.4)
        m.cut('FrontCover',aperture,'Independent '+side+' shoulder-key recess').Refine=False
        cap=m.rr(26,9,3.2,(x,32.5,19.8),3.2)
        cap=cap.cut(m.rr(22,5.4,1.7,(x,32.5,19.6),2.4))
        m.feature('Shoulder'+side,'Original '+side+' shoulder key',cap,'Controls',5,'agbgray')
        m.label('ShoulderMark'+side,side,2.5,(x-.8,31.2,23.02),'Controls',5,'agbink')
    _finish(m,4,'shoulders_status_and_five_speaker_slots','按原版手册加入独立 L/R 肩键、绿色电源状态窗与五条斜扬声器槽，保留上方与前面控制件的不同位置；肩键内腔与导光结构为学习近似。')


STAGES[4]=stage04


def stage05(m):
    m.cut('BackCover',m.rr(58.4,35.4,4,(0,-16,-1),3),'Separate original two-AA battery door opening').Refine=False
    m.box('BatteryDoor','Independent rear battery door',58,35,1.1,(0,-16,0),'Body',-6,'indigo',2.8)
    bay=m.rr(56,34,15,(0,-16,1.5),2.2).cut(m.rr(53,31,15.4,(0,-16,1.3),1.1))
    m.feature('AABayWalls','Separate molded two-AA compartment wall study',bay,'Battery',-4,'indigo',True)
    m.box('AABayDivider','Independent dual-AA divider study',52,.8,14,(0,-16,1.5),'Battery',-4,'indigo',.2,True)
    for i,(y,direction) in enumerate([(-24,1),(-8,-1)]):
        x=-25 if direction==1 else 25
        m.cyl('AACell'+str(i),'Oppositely installed AA cell envelope',7,49.5,(x,y,9),'Battery',-3,'battery',axis=(direction,0,0),internal=True)
        end=x+direction*49.5
        m.cyl('AAButton'+str(i),'Independent AA positive button',2.4,.35,(end+direction*.05,y,9),'Battery',-3,'metal',axis=(direction,0,0),internal=True)
        m.cyl('AANegative'+str(i),'Independent AA negative end disk',5.7,.12,(x-direction*.2,y,9),'Battery',-3,'metal',axis=(direction,0,0),internal=True)
    m.box('BatteryLatch','Separate flexible battery-door catch study',8,1.6,3.1,(0,1.1,1.2),'Battery',-5,'indigo',.35,True)
    m.cut('BackCover',m.rr(8.4,2.2,5,(0,1.1,-.2),.5),'Battery-door thumb catch recess').Refine=False
    m.cut('AABayWalls',m.rr(8.4,2.2,5,(0,1.1,-.2),.5),'Battery catch through compartment rim').Refine=False
    _finish(m,5,'rear_battery_door_and_opposed_aa_cells','建立独立背面电池盖、双 AA 舱壁/隔板与相反极性的两枚电池，分离正负端帽及卡扣；保留原版可换电池结构，不使用内置锂电池。')


STAGES[5]=stage05


def stage06(m):
    board=m.rr(132,70,1.0,(0,0,15.5),15)
    board=board.cut(m.rr(58,36,1.4,(0,-17,15.3),1.5))
    board=board.common(m.doc.getObject('FrontCoverInner').Shape)
    holes=[Part.makeCylinder(1.4,1.4,V(x,y,15.3)) for x,y in [(-57,24),(57,24),(-55,-25)]]
    board=board.cut(Part.makeCompound(holes))
    m.feature('Mainboard','Early AGB-CPU-02 U-shaped two-sided PCB study',board,'Mainboard',0,'pcb',True)
    for i,(x,y) in enumerate([(-57,24),(57,24),(-55,-25)]):
        m.ring('BoardFixingLand'+str(i),'Separate board fixing copper land',2.4,1.45,.035,(x,y,16.535),'Mainboard',0,'gold',internal=True)
    # The early board carries a leaded AGB processor and separate external RAM.
    m.box('CPU','Original AGB processor package envelope',19,16,1.0,(0,12,16.7),'Mainboard',1,'black',.3,True)
    m.box('ExternalRAM','Separate external RAM package envelope',14,12,.95,(23,12,16.7),'Mainboard',1,'black',.25,True)
    for prefix,x,y,w,h in [('CPU',0,12,19,16),('ExternalRAM',23,12,14,12)]:
        # Photo-verified early packages: rectangular QFP and two-side TSOP.
        sides=range(4) if prefix=='CPU' else [2,3]
        for side in sides:
            pins=(38 if side<2 else 26) if prefix=='CPU' else 24
            for i in range(pins):
                if side<2:
                    xx=x+(i-(pins-1)/2)*(w-1.6)/pins;yy=y+(h/2+.45)*(1 if side==0 else -1);ww,hh=.2,.72
                else:
                    xx=x+(w/2+.45)*(1 if side==2 else -1);yy=y+(i-(pins-1)/2)*(h-1.6)/pins;ww,hh=.72,.2
                m.box(prefix+'Lead'+str(side)+'_'+str(i),'Separate leaded IC terminal study',ww,hh,.12,(xx,yy,16.55),'Mainboard',0,'metal',.03,True)
    m.label('CPUCode','CPU AGB',1.8,(-6,11.8,17.72),'Mainboard',1,'white')
    m.label('BoardCode','AGB-CPU-02 / CAD',1.45,(-19,28.5,16.535),'Mainboard',0,'white')
    _finish(m,6,'early_u_shaped_board_agb_cpu_and_ram','建立早期 AGB-CPU-02 双面 U 形主板、电池避让、安装孔与焊盘，分离 AGB 主控、外部 RAM 和引脚；芯片尺寸、端子排列为布局示意，不提供功能电路。')


STAGES[6]=stage06


def stage07(m):
    m.colors['tan']=(.56,.42,.25)
    # Early CPU-02 placement follows the photographed front/back board;
    # package dimensions and passive values remain nonfunctional studies.
    for key,x,y,w,h,z,t in [('FrontPowerIC',-28,18,7,8,16.65,1),('RearPowerIC',-53,13,6,5,14.3,1),('AudioAmplifier',50,-4,7,8,14.3,1)]:
        m.box(key,'Separate early-board IC package study',w,h,t,(x,y,z),'Mainboard',0,'black',.2,True)
        for side in [-1,1]:
            for i in range(8):
                m.box(key+'Lead'+str(side)+'_'+str(i),'Independent package solder lead',.65,.3,.12,(x+side*(w/2+.4),y+(i-3.5)*.8,16.55 if z>15 else 15.25),'Mainboard',0,'metal',.03,True)
    m.box('CrystalCan','Independent early-board crystal metal can',4.8,10,1.05,(-18,18,16.65),'Mainboard',1,'metal',.8,True)
    for i,(x,y,r,h) in enumerate([(-44,-2,4.1,5),(-53,-7,3.0,3.3),(-53,-20,2.5,3.2),(42,-14,2.5,3.2)]):
        m.cyl('Electrolytic'+str(i),'Separate rear-board electrolytic envelope',r,h,(x,y,15.25-h),'Mainboard',-1,'black',internal=True)
        m.cyl('CapEnd'+str(i),'Independent aluminum capacitor end',r-.25,.12,(x,y,15.1-h),'Mainboard',-1,'metal',internal=True)
    m.cyl('PowerInductor','Independent early power inductor envelope',3.5,3.2,(-41,-21,12),'Mainboard',-1,'black',internal=True)
    # Sparse photo-guided component corridors, not an invented working netlist.
    positions=[(-34,y) for y in [4,8,12,16,20,24]]+[(x,2) for x in [-23,-18,-13,-8,-3,2,7,12,17,22,27]]+[(34,y) for y in [4,8,12,16,20,24]]
    for i,(x,y) in enumerate(positions):
        m.box('FrontPassive'+str(i),'Independent ceramic/resistor envelope',1.4,.8,.4,(x,y,16.58),'Mainboard',0,'tan' if i%3 else 'black',.08,True)
        for j,dx in enumerate([-.9,.9]):
            m.box('FrontPassiveEnd'+str(i)+'_'+str(j),'Separate passive terminal',.3,.8,.2,(x+dx,y,16.55),'Mainboard',0,'metal',.03,True)
    for i,(x,y) in enumerate([(-38,25),(-43,25),(-48,25),(-59,0),(-59,-5),(-59,-10),(-37,-8),(-37,-13),(38,22),(43,22),(48,22),(55,-12),(55,-17),(37,-7),(37,-12)]):
        m.box('RearPassive'+str(i),'Separate rear-board passive envelope',1.5,.9,.5,(x,y,14.8),'Mainboard',-1,'tan' if i%2 else 'black',.08,True)
    _finish(m,7,'early_power_audio_and_discrete_components','依 AGB-CPU-02 实物正反面加入电源器件、晶体金属壳、音频放大器、电感、电解电容和分离贴片端子；器件外形及数值为非功能布局近似，未混入后期主板。')


STAGES[7]=stage07


def stage08(m):
    groups=[('DPadMembrane',[(-53,7),(-47,1),(-53,-5),(-59,1)]),('ABMembrane',[(57,8),(44,0)]),('StartSelectMembrane',[(-47,-20),(-47,-27)])]
    for name,points in groups:
        if name=='DPadMembrane':base=Part.makeCylinder(11.3,.55,V(-53,1,17.05))
        elif name=='ABMembrane':
            base=Part.makeCylinder(7,.55,V(57,8,17.05)).fuse(Part.makeCylinder(7,.55,V(44,0,17.05))).fuse(m.rr(15,7,.55,(50,4,17.05),2))
        else:base=m.rr(11,14.5,.55,(-47,-23.5,17.05),3)
        for x,y in points:base=base.cut(Part.makeCylinder(3.1,.8,V(x,y,16.95)))
        m.feature(name,'Independent original control silicone membrane',base.removeSplitter(),'ControlsInternal',2,'silicone',True)
        for i,(x,y) in enumerate(points):
            height=3.85 if name=='ABMembrane' else 3.35
            dome=Part.makeCone(3,1.9,height,V(x,y,17.7)).cut(Part.makeCone(2.6,1.6,height-.35,V(x,y,17.65)))
            m.feature(name+'Dome'+str(i),'Separate hollow rubber contact dome study',dome,'ControlsInternal',3,'silicone',True)
            m.cyl(name+'Carbon'+str(i),'Independent conductive carbon pill',1.5,.2,(x,y,17.1),'ControlsInternal',2,'black',internal=True)
            pad=Part.makeCylinder(2.3,.035,V(x,y,16.55))
            for j,dx in enumerate([-2.4,.12]):
                half=pad.common(Part.makeBox(2.28,5,.2,V(x+dx,y-2.5,16.5)))
                m.feature(name+'Contact'+str(i)+'_'+str(j),'Independent split gold switch contact',half,'Mainboard',0,'gold',True)
    _finish(m,8,'three_membranes_and_split_gold_contacts','建立十字键、A/B、Start/Select 三组独立硅胶膜、空心按压穹顶、导电碳粒和分离金色触点；与原版按钮柱脚对齐，保留可拆卸层级，行程与胶厚近似。')


STAGES[8]=stage08


def _wire(m,key,points,r,assembly,material,layer=1):
    balls=[Part.makeSphere(r,V(*p)) for p in points]
    for a,b in zip(points,points[1:]):
        v=V(*b)-V(*a);balls.append(Part.makeCylinder(r,v.Length,V(*a),v))
    shape=balls[0].multiFuse(balls[1:]).removeSplitter()
    return m.feature(key,'Separate insulated wire routing study',shape,assembly,layer,material,True)


def stage09(m):
    x,y=49,-20
    m.cut('FrontCover',Part.makeCylinder(10.65,4.9,V(x,y,16.6)),'Internal molded mono-speaker seating pocket').Refine=False
    m.cyl('SpeakerMagnet','Independent original mono-speaker magnet',4.8,1.45,(x,y,16.7),'Audio',1,'metal',internal=True)
    basket=Part.makeCone(5.1,10.1,2.45,V(x,y,18.3)).cut(Part.makeCone(4.75,9.75,2.55,V(x,y,18.25)))
    m.feature('SpeakerBasket','Separate tapered mono-speaker basket',basket,'Audio',2,'metal',True)
    m.ring('SpeakerRim','Independent speaker mounting rim',10.4,9.85,.35,(x,y,20.8),'Audio',3,'black',internal=True)
    diaphragm=Part.makeCone(3.2,9.1,1.45,V(x,y,19.2)).cut(Part.makeCone(3.1,9.0,1.5,V(x,y,19.15)))
    m.feature('SpeakerDiaphragm','Separate thin conical mono diaphragm',diaphragm,'Audio',3,'black',True)
    m.cyl('SpeakerDustCap','Independent central diaphragm cap',3.05,.16,(x,y,19.22),'Audio',3,'agbgray',internal=True)
    for i,(xx,yy) in enumerate([(39,-18),(39,-25)]):
        m.box('SpeakerSolder'+str(i),'Separate speaker wire solder pad',1.8,2,.08,(xx,yy,16.55),'Mainboard',0,'metal',.2,True)
        _wire(m,'SpeakerWire'+str(i),[(xx,yy,16.85),(xx+1.5,yy,17.2),(43,yy,18.0)],.22,'Audio','red' if i==0 else 'black')
    _finish(m,9,'mono_speaker_and_two_soldered_wires','加入原版单声道扬声器的磁体、锥形金属架、薄振膜、中心帽、安装边缘和两根独立焊接导线，对应前壳五条斜格栅；声学尺寸与走线为拆解引导的近似。')


STAGES[9]=stage09


def stage10(m):
    for side,x in [('L',-52),('R',52)]:
        m.box('ShoulderSwitch'+side,'Independent original shoulder tactile switch',6,4,1.8,(x,28,16.65),'ControlsInternal',1,'black',.3,True)
        m.cyl('ShoulderSwitchPlunger'+side,'Separate shoulder switch plunger',1.1,.65,(x,28,18.55),'ControlsInternal',2,'agbgray',internal=True)
        m.box('ShoulderActuator'+side,'Independent shoulder actuator tab',3,3,.35,(x,28,19.3),'ControlsInternal',3,'agbgray',.2,True)
        for j,(dx,dy) in enumerate([(-2,-2.5),(2,-2.5),(-2,2.5),(2,2.5)]):
            m.box('ShoulderSwitchTerminal'+side+str(j),'Independent tactile switch terminal',.6,.7,.12,(x+dx,28+dy,16.55),'Mainboard',0,'metal',.05,True)
        m.cyl('ShoulderPivot'+side,'Independent shoulder pivot pin',.45,17,(x-8.5,32.5,20.3),'ControlsInternal',3,'metal',axis=(1,0,0),internal=True)
        for j,dx in enumerate([-9.3,8.7]):
            m.ring('ShoulderPivotSeat'+side+str(j),'Separate shoulder pivot bearing study',.85,.5,.6,(x+dx,32.5,20.3),'ControlsInternal',3,'indigo',axis=(1,0,0),internal=True)
        points=[]
        for i in range(65):
            a=4*math.pi*i/64;points.append((x-1.2+2.4*i/64,32.5+.8*math.cos(a),20.3+.8*math.sin(a)))
        _wire(m,'ShoulderReturnSpring'+side,points,.1,'ControlsInternal','metal',3)
    _finish(m,10,'shoulder_pivots_return_springs_and_switches','分离 L/R 触觉开关、焊脚、压杆、转轴、轴座和回位弹簧，肩键保留独立空腔；机械布局依据拆解，弹簧与行程为学习近似。')


STAGES[10]=stage10


def stage11(m):
    housing=m.rr(23,4.5,1.8,(-18,30.5,13.45),.35)
    housing=housing.cut(m.rr(20.8,2.2,.55,(-18,32,14.05),.1))
    m.feature('LCD40Connector','Original early-board 40-position LCD connector study',housing,'DisplayInterconnect',-1,'white',True)
    m.box('LCD40Latch','Separate original LCD connector locking bar',22,.65,1.1,(-18,27.8,13.55),'DisplayInterconnect',-1,'agbgray',.12,True)
    for i in range(40):
        x=-27.75+i*.5
        m.box('LCD40Contact'+str(i),'Independent early 40-pin LCD solder terminal',.22,1.2,.12,(x,27.7,15.32),'DisplayInterconnect',0,'metal',.025,True)
    # One continuous folded ribbon goes around the upper PCB edge, not through it.
    yz=[(31.5,14.4),(36,14.4),(36,17.5),(30.7,17.5),(30.7,17.65),(36.15,17.65),(36.15,14.25),(31.5,14.25)]
    verts=[V(-28,y,z) for y,z in yz];verts.append(verts[0])
    ribbon=Part.Face(Part.makePolygon(verts)).extrude(V(20,0,0))
    m.feature('LCDFoldedRibbon','Separate original reflective LCD folded flex study',ribbon,'DisplayInterconnect',1,'copper',True)
    for i in range(40):
        x=-27.75+i*.5
        m.box('LCDRibbonTrace'+str(i),'Separate schematic flex conductor',.15,3.8,.015,(x,33.65,14.42),'DisplayInterconnect',0,'gold',.015,True)
    _finish(m,11,'early_40pin_lcd_socket_and_folded_flex','依据 AGB-CPU-02 实物的 1/40 标记建立早期 40 位液晶插座、独立锁条、焊脚和绕过主板上缘的连续折叠软排线；未使用后期 32 位接口。')


STAGES[11]=stage11


def stage12(m):
    aperture=m.rr(14.4,12,5.4,(6,37,11.3),.6)
    for key in ['FrontCover','BackCover','Mainboard']:
        m.cut(key,aperture,'Original upper EXT connector clearance').Refine=False
    shell=m.rr(14,9,5,(6,36.5,11.5),.5).cut(m.rr(13.4,9.5,4.4,(6,36.5,11.8),.3))
    m.feature('EXTShield','Separate original six-contact EXT metal receptacle',shell,'Ports',0,'metal',True)
    m.box('EXTTongue','Independent EXT dielectric tongue',10,5,1,(6,37,13.5),'Ports',0,'black',.3,True)
    for row,z in enumerate([13.3,14.6]):
        for i in range(3):
            m.box('EXTContact'+str(row)+'_'+str(i),'Independent original EXT contact',.65,2.8,.12,(3+i*3,38,z),'Ports',0,'gold',.08,True)
    for x in [-5,17]:
        slot=m.rr(2.4,8,4,(x,39,12.2),.3)
        for key in ['FrontCover','BackCover']:
            m.cut(key,slot,'Original EXT accessory fixing slot').Refine=False
    # Rear Game Pak entry is separate from the EXT port and LCD connector.
    m.cut('BackCover',m.rr(61,15,7.8,(0,38,2.0),1.0),'Original top rear Game Pak entry').Refine=False
    socket=m.rr(58,8,6.2,(0,10,7.5),.6).cut(m.rr(54,7,2,(0,12.5,9.5),.2))
    m.feature('GamePakSocket','Independent original 32-contact Game Pak socket',socket,'CartridgeInterface',-2,'black',True)
    for i in range(32):
        x=(i-15.5)*1.6
        m.box('GamePakContact'+str(i),'Independent Game Pak spring contact study',.7,3.6,.18,(x,11.4,9.65),'CartridgeInterface',-2,'gold',.09,True)
        m.box('GamePakSolder'+str(i),'Independent Game Pak board solder terminal',.8,1.2,.12,(x,5.1,15.25),'Mainboard',0,'metal',.08,True)
    for side,x in [('L',-31.2),('R',31.2)]:
        m.box('GamePakGuide'+side,'Separate rear cartridge guide rail study',1.2,22,4.5,(x,22,3.6),'CartridgeInterface',-4,'indigo',.3,True)
    _finish(m,12,'original_ext_and_32contact_game_pak_interface','加入上方原版六触点 EXT 金属接口及两侧附件固定槽，独立建立背面 Game Pak 入口、32 个触点、焊端和导轨；接口局部尺寸为外观学习近似。')


STAGES[12]=stage12


def stage13(m):
    # Original underside: power at the left; headphone and volume at the right.
    m.cut('BackCover',m.rr(10,12,3.3,(-46,-36,7.5),.5),'Original bottom power slider opening').Refine=False
    m.cut('BackCover',m.rr(8.4,5.4,4.4,(-46,-30,6.8),.5),'Internal power switch seating pocket').Refine=False
    m.box('PowerSwitchBody','Independent original slide power switch',8,5,4,(-46,-30,7),'Ports',-2,'metal',.4,True)
    m.box('PowerSlider','Separate original underside power actuator',6,4.5,2,(-46,-35,8),'Controls',-3,'agbgray',.6)
    for i in range(4):
        m.box('PowerSwitchTerminal'+str(i),'Independent power switch terminal',.7,1.7,.2,(-49+i*2,-26.2,10.8),'Ports',-2,'metal',.07,True)
    for i in range(3):
        m.box('PowerSliderGrip'+str(i),'Separate slider grip ridge',.4,3,.3,(-47+i,-35,10.08),'Controls',-3,'black',.07)
    opening=Part.makeCylinder(3.6,14,V(35,-31,10.5),V(0,-1,0))
    for key in ['BackCover','FrontCover']:
        m.cut(key,opening,'Original 3.5 mm headphone socket opening').Refine=False
        m.cut(key,m.rr(8.4,9.4,7.4,(35,-31,6.8),.6),'Internal headphone connector seating pocket').Refine=False
    jack=m.rr(8,9,7,(35,-31,7),.6).cut(Part.makeCylinder(1.85,12,V(35,-25.5,10.5),V(0,-1,0)))
    m.feature('HeadphoneBody','Separate original stereo headphone connector body',jack,'Ports',-2,'black',True)
    m.ring('HeadphoneLip','Independent headphone socket circular mouth',3.25,1.85,1,(35,-36,10.5),'Ports',-3,'black',axis=(0,-1,0),internal=True)
    for i in range(3):
        m.ring('HeadphoneContact'+str(i),'Independent internal headphone spring contact study',1.75,1.6,.45,(35,-29-i*2,10.5),'Ports',-2,'metal',axis=(0,-1,0),internal=True)
    m.cut('BackCover',m.rr(12,10,2.4,(51,-33,8.65),.5),'Original exposed volume wheel slot').Refine=False
    m.cut('BackCover',m.rr(9.4,7.4,1.5,(51,-26,6.3),.5),'Internal volume potentiometer seating pocket').Refine=False
    m.box('VolumePotentiometer','Independent analog volume potentiometer body',9,7,1.1,(51,-26,6.5),'Ports',-2,'metal',.5,True)
    m.cyl('VolumeSpindle','Separate volume wheel spindle',1,1.1,(51,-29,7.7),'Ports',-2,'metal',internal=True)
    wheel=Part.makeCylinder(5.2,1.4,V(51,-29,9))
    notches=[]
    for i in range(40):
        a=2*math.pi*i/40;notches.append(Part.makeCylinder(.24,1.6,V(51+5.25*math.cos(a),-29+5.25*math.sin(a),8.9)))
    m.feature('VolumeWheel','Independent original knurled volume wheel',wheel.cut(Part.makeCompound(notches)),'Controls',-2,'black')
    m.ring('VolumeResistiveTrack','Independent schematic carbon volume track',4.5,3.8,.1,(51,-29,8.82),'Ports',-2,'agbgray',internal=True)
    for i in range(5):
        m.box('VolumeTerminal'+str(i),'Separate analog volume terminal',.6,1.4,.15,(47.8+i*1.6,-21.7,7.6),'Ports',-2,'metal',.05,True)
    _finish(m,13,'bottom_power_stereo_headphone_and_volume','建立底部左侧独立电源滑块、右侧 3.5 mm 耳机口与有齿模拟音量轮，分离开关/插座壳、内部触点、电位器、轴及焊端，保留原版底边布局。')


STAGES[13]=stage13


def stage14(m):
    for i,(y,negative_side) in enumerate([(-24,-1),(-8,1)]):
        m.box('AANegativePlate'+str(i),'Independent AA negative spring backing plate',.18,6,6,(negative_side*26.25,y,6),'BatteryContacts',-3,'metal',.06,True)
        points=[]
        for j in range(65):
            a=4*math.pi*j/64;r=1.8+1.0*j/64
            points.append((negative_side*(25.4+.65*j/64),y+r*math.cos(a),9+r*math.sin(a)))
        _wire(m,'AANegativeSpring'+str(i),points,.08,'BatteryContacts','metal',-3)
        m.box('AAPositivePlate'+str(i),'Independent opposite AA positive leaf contact',.18,5,6,(-negative_side*25.3,y,6),'BatteryContacts',-3,'metal',.06,True)
    # Independent small bosses retain the PCB without merging into the board.
    for i,(x,y) in enumerate([(-57,24),(57,24),(-55,-25)]):
        boss=Part.makeCylinder(2.1,2.9,V(x,y,12.4)).cut(Part.makeCylinder(.9,3.1,V(x,y,12.3)))
        m.feature('BoardBoss'+str(i),'Separate hollow mainboard fixing boss study',boss,'Fixings',-1,'indigo',True)
        m.screw('BoardScrew'+str(i),(x,y,17.1),'Fixings',1,length=3.5,radius=1.2,axis=(0,0,-1))
    _finish(m,14,'opposed_aa_contacts_and_board_fixings','建立相反极性的两组 AA 弹簧与正极簧片，分离电池端帽和接点；补充三组中空主板安装柱及穿孔螺钉，保留电池舱和板件的独立层级。')


STAGES[14]=stage14


def stage15(m):
    for i,(x,y) in enumerate([(-62,15),(62,15),(-60,-17),(60,-17),(-33,32),(33,32)]):
        m.cut('BackCover',Part.makeCylinder(1.85,2.2,V(x,y,-.2)),'Rear tri-wing screw counterbore').Refine=False
        m.cut('BackCover',Part.makeCylinder(.9,10,V(x,y,0)),'Rear case fastener bore').Refine=False
        head=Part.makeCylinder(1.55,.45,V(x,y,.45));shaft=Part.makeCylinder(.72,7.0,V(x,y,.85))
        slots=[]
        for a in [0,120,240]:
            s=Part.makeBox(1.3,.32,.22,V(x-.05,y-.16,.4));s.rotate(V(x,y,0),V(0,0,1),a);slots.append(s)
        m.feature('CaseTriWing'+str(i),'Independent original rear tri-wing screw study',head.fuse(shaft).cut(Part.makeCompound(slots)),'Fixings',-5,'metal',True)
    hole=Part.makeCylinder(.78,5,V(0,-16,1.1)).fuse(Part.makeCylinder(1.3,.8,V(0,-16,1.1)))
    m.cut('AABayDivider',hole,'Battery-compartment cross-head screw clearance').Refine=False
    m.screw('BatteryBayScrew',(0,-16,1.3),'Fixings',-5,length=3.0,radius=1.15)
    # A shallow recess with a cross-bar represents the original wrist-strap eye.
    pocket=m.rr(5,6,4,(61,-21,3),1)
    m.cut('BackCover',pocket,'Original rear wrist-strap recess').Refine=False
    m.cyl('WristStrapBar','Independent wrist-strap retaining cross-bar',.7,4.5,(58.8,-21,5),'Body',-4,'indigo',axis=(1,0,0))
    rear_rotation=App.Rotation(V(0,1,0),180)
    m.cut('BackCover',m.rr(42.4,10.4,.4,(0,19,-.1),.8),'Shallow rear identification label recess').Refine=False
    m.box('RearModelLabel','Separate rear regulatory study label',42,10,.08,(0,19,.1),'Markings',-6,'agbgray',.7)
    m.label('RearModelCode','AGB-001 / CAD STUDY',1.7,(18,19.5,.08),'Markings',-6,'black',rotation=rear_rotation)
    m.label('RearSerialBoundary','NOT A SERIAL NUMBER',1.1,(14,16.5,.08),'Markings',-6,'black',rotation=rear_rotation)
    m.label('BatteryPolarity0','+  AA  -',1.8,(-7,-10,1.13),'Battery',-5,'agbink')
    m.label('BatteryPolarity1','-  AA  +',1.8,(-7,-25,1.13),'Battery',-5,'agbink')
    _finish(m,15,'case_triwing_fixings_strap_eye_and_rear_labels','加入六枚独立三翼外壳螺钉、一枚电池舱十字螺钉、腕带固定孔与明确标为 CAD STUDY 的背面标签；不伪造序列号，后壳孔位和固定结构近似。')


STAGES[15]=stage15


def stage16(m):
    for side,x in [('L',-73),('R',61)]:
        region=Part.makeBox(12,40,1.4,V(x,-20,9.65))
        strip=m.parts['BackCover'].Shape.common(region)
        assert strip.Solids,side
        m.feature('SideInsert'+side,'Independent original grey side trim study',strip,'Body',-2,'agbgray')
        m.cut('BackCover',Part.makeBox(12.1,40.2,1.6,V(x-.05,-20.1,9.55)),'Separate side trim seating clearance').Refine=False
    foam=m.rr(72,52,.2,(0,4.5,17.45),.5).cut(m.rr(69,49,.4,(0,4.5,17.35),.5))
    m.feature('LCDRearFoam','Independent reflective LCD rear support foam frame',foam,'Display',1,'rubber',True)
    m.box('PowerLEDEmitter','Separate board-mounted status emitter',1.5,1.5,.6,(46,26,16.65),'Mainboard',0,'led',.15,True)
    m.cyl('PowerLEDOpticalStem','Separate status light guide extension',.65,3.55,(46,26,17.5),'Display',2,'white',internal=True)
    arrows=[]
    for angle in [0,90,180,270]:
        p=[V(-54,7,24.32),V(-52,7,24.32),V(-53,9,24.32)]
        tri=Part.Face(Part.makePolygon(p+[p[0]])).extrude(V(0,0,.3));tri.rotate(V(-53,1,0),V(0,0,1),angle);arrows.append(tri)
    m.cut('DPad',arrows,'Original directional triangle engravings').Refine=False
    _finish(m,16,'side_inserts_lcd_foam_and_final_control_detail','补充可拆卸灰色侧边装饰、LCD 背面泡棉框、主板状态 LED 与导光柱，并刻出十字键方向三角。原版基本套件包含双 AA 示意电池；未把选购卡带或联机线宣称为标配。')


STAGES[16]=stage16


def stage17(m):
    cx=110
    m.native('StudyCartBack','Editable optional blank Game Pak rear shell',60,34,1.8,.8,(cx,0,0),'Accessories',-3,'black')
    wall=m.rr(60,34,5.9,(cx,0,.9),1.8).cut(m.rr(57,31,6.1,(cx,0,.8),.8))
    m.feature('StudyCartWall','Independent optional Game Pak perimeter wall',wall,'Accessories',-1,'black')
    m.native('StudyCartFront','Editable optional blank Game Pak front shell',60,34,1.8,.8,(cx,0,6.9),'Accessories',3,'black')
    window=m.rr(54,7,6,(cx,-15,2),.2)
    for key in ['StudyCartBack','StudyCartWall','StudyCartFront']:m.cut(key,window,'Open optional cartridge contact edge').Refine=False
    board=m.rr(54,29,.8,(cx,-1,3),.7).cut(Part.makeCylinder(3.2,1.2,V(cx,13.6,2.8)))
    m.feature('StudyCartPCB','Separate early AGB-E06-inspired study cartridge board',board,'Accessories',0,'pcb',True)
    for i in range(32):
        m.box('StudyCartEdge'+str(i),'Independent Game Pak gold edge contact',1.0,4,.035,(cx+(i-15.5)*1.65,-13.2,3.85),'Accessories',0,'gold',.08,True)
    for key,x,y,w,h,pins in [('RAM',cx-15,2,9,18,14),('ROM',cx+15,2,11,19,22),('Supervisor',cx,6,5,4,4)]:
        m.box('StudyCart'+key,'Independent nonfunctional '+key+' package envelope',w,h,1.25,(x,y,4.1),'Accessories',1,'black',.2,True)
        for side in [-1,1]:
            for i in range(pins):
                m.box('StudyCart'+key+'Lead'+str(side)+'_'+str(i),'Independent cartridge package terminal',.75,.3,.12,(x+side*(w/2+.5),y+(i-(pins-1)/2)*(h-1)/pins,3.85),'Accessories',0,'metal',.035,True)
    for i,(x,y) in enumerate([(cx-4,-2),(cx+5,-5),(cx-4,8),(cx+4,10)]):
        m.box('StudyCartPassive'+str(i),'Independent cartridge passive study',1.2,.8,.4,(x,y,3.9),'Accessories',1,'tan',.07,True)
    for i,(x,y) in enumerate([(cx+2,-4),(cx+25,6)]):
        m.box('StudyCartBatteryPad'+str(i),'Separate depopulated battery solder pad',3,3,.08,(x,y,3.86),'Accessories',0,'metal',.3,True)
    m.box('StudyCartLabel','Independent blank study label',43,21,.08,(cx,-1,7.75),'Accessories',4,'agbgray',1.2)
    for key,text,size,x,y in [('StudyCartTitle','GAME PAK',2.7,cx-13,2),('StudyCartNotice','NO GAME DATA',1.5,cx-11,-4),('StudyCartTop','ADVANCE / STUDY',1.7,cx-16,12.5)]:
        m.label(key,text,size,(x,y,7.86 if key!='StudyCartTop' else 7.73),'Accessories',4,'white')
    # Battery shown removed, as in the referenced PCB photograph, without a ROM.
    m.cyl('StudyCartCR1616','Separate removed cartridge backup-cell envelope',8,1.6,(cx,-30,1),'Accessories',0,'metal',internal=True)
    m.label('StudyCartBatteryCode','CR1616',1.2,(cx-3.7,-30.5,2.64),'Accessories',1,'black')
    _finish(m,17,'optional_blank_game_pak_and_removed_backup_cell','另附明确标为 NO GAME DATA 的空白 Game Pak 学习件，参考 2001 年 AGB-E06-01 实物的 ROM/SRAM/监控器、32 触点和已移除备用电池布局；壳体尺寸为近似，不含游戏数据，也不宣称是掌机标配。')


STAGES[17]=stage17
