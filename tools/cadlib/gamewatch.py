"""Original orange 1982 DK-52: measured museum envelope, approximate local geometry."""
import math
import FreeCAD as App
import Part
from .core import V
from . import geometry as g


def _finish(m,n,slug,summary):
    m.doc.recompute()
    for o in m.parts.values():o.Shape.check(True)
    m.profile['stages']=n;m.checkpoint(n,slug,summary)


def _poly(points,z,t):
    vs=[V(x,y,z) for x,y in points];return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,0,t))


def stage01(m):
    m.colors.update(orange=(.78,.28,.055),foil=(.65,.62,.45),lcd=(.57,.61,.48),ink=(.08,.085,.075),phenolic=(.43,.22,.10),artred=(.48,.09,.055),artblue=(.10,.39,.46),silicone=(.40,.41,.35))
    m.native('BackCover','Original orange lower rear shell',115,72,1.7,5.4,(0,-.5,0),'Body',-6,'orange',expr={'Width':'Parameters.Width'})
    m.cut('BackCover',m.rr(112.4,69.4,5,(0,-.5,1.25),1),'Lower case inner cavity').Refine=False
    m.native('MainFrame','Original orange control-side frame',115,72,1.7,4.55,(0,-.5,5.55),'Body',0,'orange')
    m.cut('MainFrame',m.rr(112.4,69.4,5,(0,-.5,5.4),1),'Lower control frame cavity').Refine=False
    m.native('FrontDeck','Orange lower control deck',114.6,71.6,1.5,.9,(0,-.5,10.15),'Body',4,'orange')
    m.cut('FrontDeck',m.rr(55,37,2,(0,-1.5,9.8),.65),'Original lower LCD opening').Refine=False
    # Metal faceplates are full side panels with orange painted areas, not isolated gold rectangles.
    for side in [-1,1]:
        x=side*43.4
        m.cut('FrontDeck',m.rr(23.7,65.2,.5,(x,-.5,10.77),.6),'Inset full painted metal panel').Refine=False
        m.box('ControlPlate'+str(side),'Original painted metal control faceplate',23.3,64.8,.17,(x,-.5,10.8),'Body',5,'foil',.5)
        m.box('ControlPaint'+str(side),'Orange printed upper faceplate area',23.1,32,.018,(x,15.7,10.99),'Body',5,'orange',.4)
        border=m.rr(22.4,30.8,.018,(x,-16.9,10.99),.4).cut(m.rr(21.5,29.9,.04,(x,-16.9,10.98),.3))
        m.feature('ControlBorder'+str(side),'Orange printed lower panel border',border,'Body',5,'orange')
    _finish(m,1,'original_orange_lower_enclosure','依据馆藏实测参考包络建立原生橙色分体下壳、空腔、控制面板和两片整幅喷漆金属饰板；局部形状与壁厚近似。')


STAGES={1:stage01}


def stage02(m):
    cy=69.25
    m.native('LidBackCover','Original upper outer shell',115,66.5,1.7,5.2,(0,cy,.25),'Lid',-6,'orange','Lid')
    m.cut('LidBackCover',m.rr(112.4,63.9,5,(0,cy,1.5),1),'Upper shell interior').Refine=False
    m.native('LidFrame','Upper LCD support frame',114.7,66.2,1.55,4.55,(0,cy,5.6),'Lid',0,'orange','Lid')
    m.cut('LidFrame',m.rr(112.1,63.6,5,(0,cy,5.5),.9),'Upper LCD cavity').Refine=False
    m.native('LidBezel','Upper orange display face',114.6,66.1,1.5,.9,(0,cy,10.2),'Lid',5,'orange','Lid')
    m.cut('LidBezel',m.rr(55,37,2,(0,70,9.9),.65),'Upper LCD aperture').Refine=False
    for side in [-1,1]:
        x=side*43.5
        m.cut('LidBezel',m.rr(22,62,.5,(x,69.3,10.77),.3),'Original upper side recess').Refine=False
        m.box('UpperSideDivider'+str(side),'Upper panel transverse molded rib',21.7,.7,.29,(x,64,10.8),'Lid',5,'orange',.1,pose='Lid')
    # Separate interleaved barrel sections and two axles, center left open for printed flex.
    bore=Part.makeCylinder(2.65,117,V(-58.5,34,11.5),V(1,0,0))
    for key in ['BackCover','MainFrame','FrontDeck','LidBackCover','LidFrame','LidBezel','ControlPlate-1','ControlPlate1','ControlPaint-1','ControlPaint1']:m.cut(key,bore,'Hinge barrel circular clearance').Refine=False
    for name,x,length,pose in [('LeftBase',-57.5,11,'Base'),('LeftLid',-46.2,11.2,'Lid'),('RightLid',35,11.2,'Lid'),('RightBase',46.5,11,'Base')]:
        m.ring('Hinge'+name,'Original orange hinge barrel',2.5,.85,length,(x,34,11.5),'Hinge',0,'orange',axis=(1,0,0),pose=pose)
    for i,x in enumerate([-57.3,35.1]):m.cyl('HingePin'+str(i),'Original hinge steel pin',.75,22.1,(x,34,11.5),'Hinge',0,'metal',axis=(1,0,0),internal=True)
    m.box('FrontClasp','Upper front retaining clasp',11,2,2.6,(0,103.5,7.5),'Lid',5,'orange',.35,pose='Lid')
    m.cut('FrontClasp',m.rr(8.5,2.5,.9,(0,103.5,8.6),.25),'Clasp flexible opening').Refine=False
    m.cut('BackCover',m.rr(12,2,4,(0,-36.3,3),.4),'Front clasp receiving recess').Refine=False
    m.box('LowerCatch','Lower clasp retaining ledge',8,.7,.45,(0,-35.3,3.1),'Body',-6,'orange',.12)
    m.cut('BackCover',m.parts['LowerCatch'].Shape,'Lower catch molded ledge seat').Refine=False
    _finish(m,2,'upper_case_hinges_and_original_clasp','加入独立上壳、显示面框、两侧分段铰链/钢轴与中央前卡扣；原生上盖可绕铰链转动，保留原版侧面凹框。')

STAGES[2]=stage02


def stage03(m):
    # Both displays are reflective fixed-segment LCD stacks; no modern backlight or touch layer.
    for name,y,pose,assembly in [('Lower',-1.5,'Base','Display'),('Upper',70,'Lid','LidDisplay')]:
        m.box(name+'Reflector',name+' LCD rear reflecting sheet',59,41,.18,(0,y,7.1),assembly,1,'metal',.4,True,pose)
        m.box(name+'RearPolarizer',name+' rear polarizing sheet',59,41,.06,(0,y,7.33),assembly,2,'lcd',.4,True,pose)
        m.box(name+'LCDGlassRear',name+' rear LCD glass substrate',59,41,.55,(0,y,7.44),assembly,2,'lcd',.4,True,pose)
        m.box(name+'LCDGap',name+' schematic liquid-crystal cell',58.7,40.7,.045,(0,y,8.04),assembly,2,'lcd',.35,True,pose)
        m.box(name+'LCDGlassFront',name+' front LCD glass substrate',59,41,.55,(0,y,8.14),assembly,3,'lcd',.4,True,pose)
        m.box(name+'ArtworkFilm',name+' fixed-color graphic carrier',58.7,40.7,.045,(0,y,8.74),assembly,3,'lcd',.35,False,pose)
        # The outer polarizer is shown as a perimeter sheet so the reconstructed artwork remains visible.
        polar=m.rr(59,41,.065,(0,y,8.83),.4).cut(m.rr(53.7,35.7,.2,(0,y,8.8),.3))
        m.feature(name+'FrontPolarizer',name+' front polarizer perimeter study',polar,assembly,5,'ink',False,pose)
        gasket=m.rr(60.6,42.6,.5,(0,y,8.94),.7).cut(m.rr(54.6,36.6,.8,(0,y,8.8),.5))
        m.feature(name+'DisplayGasket',name+' black LCD border gasket',gasket,assembly,5,'black',False,pose)
        for side in [-1,1]:
            m.box(name+'Stabilizer'+str(side),name+' transparent stabilizing strip',.65,40,.4,(side*30.9,y,8.95),assembly,5,'white',.15,True,pose)
        m.box(name+'ContactStrip',name+' original LCD elastomeric contact',46,1.0,.7,(0,y+22.5,7.6),assembly,2,'silicone',.15,True,pose)
        for i in range(32):m.box(name+'ContactStripe'+str(i),'LCD elastomer conductive lamination',.22,1.02,.68,(-21.7+i*1.4,y+22.5,7.61),assembly,2,'ink',.02,True,pose)
        # Stripe slivers are laminated inserts, so remove their volumes from the rubber carrier.
        m.cut(name+'ContactStrip',[m.parts[name+'ContactStripe'+str(i)].Shape for i in range(32)],'Individual contact-lamination seats').Refine=False
    _finish(m,3,'two_reflective_lcd_layer_stacks','依据拆解建立两组独立反射片、后偏光层、LCD 玻璃/液晶间隙、固定图形载体、边缘偏光示意、压边和导电胶条。前偏光层按周边框表达，便于观察结构；无背光或触控。')

STAGES[3]=stage03


def _line(m,key,x1,y1,x2,y2,width,z,mat,assembly,pose):
    dx,dy=x2-x1,y2-y1;length=math.hypot(dx,dy)
    s=m.rr(length,width,.018,((x1+x2)/2,(y1+y2)/2,z),min(.05,width/3))
    s.rotate(V((x1+x2)/2,(y1+y2)/2,z),V(0,0,1),math.degrees(math.atan2(dy,dx)))
    return m.feature(key,'Reconstructed fixed screen artwork',s,assembly,5,mat,False,pose)


def stage04(m):
    # Reconstructed geometric artwork follows the photographed girder/ladder arrangement.
    for name,cy,pose,assembly in [('Lower',-1.5,'Base','Display'),('Upper',70,'Lid','LidDisplay')]:
        z=8.91
        levels=[(-15,-23,22,2),(0,-23,21,-2),(15,-22,22,1)] if name=='Lower' else [(-16,-22,22,1),(-7,-19,8,0),(8,-26,-20,0)]
        for k,(yy,x1,x2,slope) in enumerate(levels):
            y1=cy+yy;y2=y1+slope
            # one compound per printed girder avoids artificial overlap at connected truss strokes
            strokes=[]
            def stroke(a,b,c,d,w):
                dx,dy=c-a,d-b;s=m.rr(math.hypot(dx,dy),w,.018,((a+c)/2,(b+d)/2,z),.03);s.rotate(V((a+c)/2,(b+d)/2,z),V(0,0,1),math.degrees(math.atan2(dy,dx)));strokes.append(s)
            stroke(x1,y1,x2,y2,.6);stroke(x1,y1+2.3,x2,y2+2.3,.55)
            steps=max(1,int((x2-x1)/3.7))
            for j in range(steps):
                xa=x1+(x2-x1)*j/steps;xb=x1+(x2-x1)*(j+1)/steps;ya=y1+slope*j/steps;yb=y1+slope*(j+1)/steps;stroke(xa,ya,xb,yb+2.3,.38)
            sh=strokes[0].multiFuse(strokes[1:]).removeSplitter();m.feature(name+'Girder'+str(k),'Reconstructed fixed red girder',sh,assembly,5,'artred',False,pose)
        for k,(x,y1,y2) in enumerate([(-20,-12,-1),(17,3,14)] if name=='Lower' else [(-21,-13,-3)]):
            strokes=[m.rr(.45,y2-y1,.018,(x+dx,cy+(y1+y2)/2,z),.03) for dx in [-1.35,1.35]]
            for yy in range(int(y1)+1,int(y2),2):strokes.append(m.rr(2.8,.4,.018,(x,cy+yy,z),.03))
            m.feature(name+'Ladder'+str(k),'Reconstructed fixed ladder',strokes[0].multiFuse(strokes[1:]).removeSplitter(),assembly,5,'artred',False,pose)
        if name=='Upper':
            for i,(x,h) in enumerate([(-13,7),(-6,10),(1,7),(8,11),(15,7)]):
                m.box('Building'+str(i),'Reconstructed fixed blue building',5.5,h,.018,(x,cy+1+h/2,z),assembly,5,'artblue',.05,False,pose)
                for j in range(int(h/1.5)-1):m.box('BuildingWindow'+str(i)+'_'+str(j),'Building window stripe',4.3,.35,.018,(x,cy+2+j*1.5,z+.035),assembly,5,'lcd',.03,False,pose)
            hook=Part.makeCylinder(1.5,.018,V(12,cy+15,z)).cut(Part.makeCylinder(.95,.06,V(12,cy+15,z-.02)))
            hook=hook.cut(Part.makeBox(3,2,.08,V(12,cy+15,z-.03))).fuse(m.rr(.65,3.2,.018,(11,cy+17,z),.1))
            m.feature('UpperHook','Schematic fixed crane hook',hook,assembly,5,'ink',False,pose)
        else:
            # Three suspended platform markings are schematic, not copied bitmap game art.
            for i,(x,y) in enumerate([(-11,10),(14,7),(1,-5)]):
                m.box('HangingPlatform'+str(i),'Fixed suspended platform',7,2.5,.018,(x,cy+y,z),assembly,5,'artred',.1)
                _line(m,'PlatformCable'+str(i),x,cy+y+1.3,x,cy+y+4,.25,z,'artred',assembly,pose)
    m.cut('PlatformCable2',m.parts['LowerGirder1'].Shape,'Connected printed stroke boundary').Refine=False
    m.cut('HangingPlatform1',m.parts['LowerLadder1'].Shape,'Connected printed artwork boundary').Refine=False
    _finish(m,4,'reconstructed_fixed_screen_girders_ladders_and_city','以原机照片为参考重绘两屏红色钢架、梯子、上屏蓝色建筑和吊钩；图形为独立矢量实体的结构示意，不是精确游戏图像或 ROM。')

STAGES[4]=stage04


def stage05(m):
    x,y=-43.4,-18
    cross=m.rr(5.4,17,1.3,(x,y,10),.5).fuse(m.rr(17,5.4,1.3,(x,y,10),.5)).removeSplitter()
    hole=m.rr(6,17.6,3,(x,y,9.5),.6).fuse(m.rr(17.6,6,3,(x,y,9.5),.6))
    for key in ['FrontDeck','ControlPlate-1']:m.cut(key,hole,'Original cross-key opening').Refine=False
    m.feature('DPad','Original raised black directional cross',cross,'Controls',6,'black')
    m.cyl('DPadPivot','D-pad pivot stem',1.3,1.6,(x,y,8.35),'Controls',3,'black',internal=True)
    # Jump and three vertically arranged game/time buttons.
    for name,x,y,w,h in [('Jump',43.4,-18,9.2,9.2),('GameA',40.5,24,6.2,3.4),('GameB',40.5,16.5,6.2,3.4),('Time',40.5,9,6.2,3.4)]:
        hole=m.rr(w+.65,h+.65,3,(x,y,9.5),min(w,h)/2-.01)
        for key in ['FrontDeck','ControlPlate1','ControlPaint1']:
            if key=='ControlPaint1' and name=='Jump':continue
            m.cut(key,hole,'Original '+name+' key opening').Refine=False
        m.box(name+'Key',name+' original black key',w,h,1.35,(x,y,9.95),'Controls',6,'black',min(w,h)/2-.03)
        m.cyl(name+'Stem',name+' actuator stem',1.1,1.5,(x,y,8.35),'Controls',3,'black',internal=True)
    for name,y in [('Alarm',20.5),('ACL',13)]:
        for key in ['FrontDeck','ControlPlate1','ControlPaint1']:m.cut(key,Part.makeCylinder(.85,3,V(49,y,9.5)),name+' recessed metal contact aperture').Refine=False
        m.cyl(name+'Disc',name+' original recessed metal disc',.7,.35,(49,y,10.45),'Controls',5,'metal')
        m.cyl(name+'Stem',name+' contact stem',.4,2,(49,y,8.3),'Controls',3,'metal',internal=True)
    # Source photographs show a separate D-pad membrane and round jump diaphragm.
    for name,x,y in [('Dpad',-43.4,-18),('Jump',43.4,-18)]:
        rr=8.5 if name=='Dpad' else 5.5
        m.cyl(name+'Membrane',name+' silicone contact membrane',rr,.35,(x,y,7.3),'ControlsInternal',2,'silicone',internal=True)
        centers=[(0,4.5),(4.5,0),(0,-4.5),(-4.5,0)] if name=='Dpad' else [(0,0)]
        for i,(dx,dy) in enumerate(centers):
            m.cyl(name+'Dome'+str(i),'Rubber switch dome',2.3,.6,(x+dx,y+dy,7.7),'ControlsInternal',3,'silicone',internal=True)
            m.cyl(name+'Carbon'+str(i),'Conductive switch carbon',1.9,.18,(x+dx,y+dy,7.06),'ControlsInternal',2,'ink',internal=True)
    m.box('MenuRubber','Three-button system silicone carrier',9,22,.35,(40.5,16.5,7.3),'ControlsInternal',2,'silicone',1,True)
    for i,y in enumerate([24,16.5,9]):
        m.cyl('MenuDome'+str(i),'System button rubber dome',2.0,.6,(40.5,y,7.7),'ControlsInternal',3,'silicone',internal=True)
        m.cyl('MenuCarbon'+str(i),'System button carbon contact',1.6,.18,(40.5,y,7.06),'ControlsInternal',2,'ink',internal=True)
    _finish(m,5,'original_dpad_jump_system_keys_and_membranes','加入原版十字键、圆形 JUMP、竖排 GAME A/B/TIME、凹入金属 ALARM/ACL 触点以及独立导电胶；开孔、按钮与内部碳接点分别建模。')

STAGES[5]=stage05


def stage06(m):
    # External metal title plate faces outward when the unit is closed.
    rot=App.Rotation(V(1,0,0),180)
    m.box('OuterTitlePlate','Ridged outer metal title plate',110,61,.20,(0,69.25,.0),'Lid',-6,'foil',.6,pose='Lid')
    for i,y in enumerate([43.2,46.5,50.2,54,82,86,89.5,93,96]):m.box('OuterTitleRidge'+str(i),'Horizontal title-plate embossed ridge',107,.4,.03,(0,y,-.035),'Lid',-6,'metal',.08,pose='Lid')
    # These outer markings point toward -Z in the flat construction pose.
    m.box('OuterTitlePill','Outer black Donkey Kong nameplate',43,6,.035,(0,67,-.045),'Lid',-6,'black',2.8,pose='Lid')
    m.label('OuterTitleText','DONKEY KONG',3.0,(-19,68,-.075),'Lid',-6,'white','Lid',rot)
    for i,(text,x,y,size) in enumerate([('GAME',-50,47,3.2),('& WATCH',-50,51,2.5),('Nintendo',-50,55,1.7),('MULTI SCREEN',19,96,2.4)]):m.label('OuterMark'+str(i),text,size,(x,y,-.035),'Lid',-6,'ink','Lid',rot)
    m.box('UpperTitlePill','Upper inner black Donkey Kong nameplate',32,5.5,.04,(0,96,11.15),'Lid',6,'black',2.5,pose='Lid')
    m.label('UpperTitleText','DONKEY KONG',2.6,(-14.5,95,11.21),'Lid',6,'white','Lid')
    m.box('LowerNintendoRim','Lower Nintendo silver nameplate rim',29,5.4,.04,(0,-29,11.1),'Body',5,'foil',2.5)
    m.box('LowerNintendoPill','Lower Nintendo black nameplate',27.7,4.4,.035,(0,-29,11.17),'Body',5,'black',2)
    m.label('LowerNintendoText','Nintendo',2.9,(-9,-30.1,11.23),'Body',5,'white')
    m.box('GameWatchBadge','Metallic Game and Watch badge',14,13,.03,(-43.4,21,11.04),'Body',5,'foil',.6)
    for i,(text,y,size) in enumerate([('GAME',24,2.8),('&',20.6,2.8),('WATCH',17.2,2.6)]):m.label('GameWatchWord'+str(i),text,size,(-49.5 if text!='&' else -44.5,y,11.09),'Body',5,'ink')
    for i,(text,x,y,size) in enumerate([('CONTROLLER',-53,-29,1.65),('JUMP',39,-28,2),('START',38.5,-9,1.4),('GAME A',35.5,20.1,1.5),('GAME B',35.5,12.6,1.5),('TIME',37.5,5.1,1.5),('ALARM',46.5,18,1),('ACL',47.5,10.5,1)]):m.label('ControlLegend'+str(i),text,size,(x,y,11.09),'Body',5,'ink')
    # Rear molded regulatory panel; use generic study serial instead of copying a specimen identity.
    for i,(text,y,size) in enumerate([('MODEL NO. DK-52',19,2),('DC3V  LR44 / SR44 x2',14.5,1.8),('Nintendo 1982',10,2),('MADE IN JAPAN',5.5,1.8)]):m.label('RearLegend'+str(i),text,size,(-21,y,-.025),'Body',-6,'orange',rotation=rot)
    _finish(m,6,'original_inner_and_outer_labels_and_ridged_plate','完成外侧横纹金属标题板、开盖后 DONKEY KONG / Nintendo 铭牌、GAME & WATCH 标识与原版按键文字；背面标注两枚 LR44/SR44 和 DC3V，不复制馆藏序列号。')

STAGES[6]=stage06


def stage07(m):
    pts=[(-53,-32),(53,-32),(53,31),(-34,31),(-34,2),(-53,2)]
    m.feature('Mainboard','Original shaped phenolic controller PCB',_poly(pts,5.8,.65),'Mainboard',-2,'phenolic',True)
    # Green copper-side finish is a separate thin layer on the control-facing side.
    m.feature('BoardMask','Green control-side solder mask',_poly(pts,6.49,.025),'Mainboard',-2,'pcb',True)
    sh=m.rr(12.5,12.5,1.5,(4,1,4.15),.35);sh.rotate(V(4,1,0),V(0,0,1),45)
    m.feature('MCUPackage','SM510 diamond-oriented flat package',sh,'Mainboard',-3,'black',True)
    for side in range(4):
        for i in range(16):
            shape=m.rr(.32,1.6,.12,(-1.625+i*.75,7.8,5.55),.03)
            shape.rotate(V(4,1,0),V(0,0,1),side*90+45)
            m.feature('MCUPin'+str(side*16+i),'Approximate flat-pack lead geometry',shape,'Mainboard',-3,'metal',True)
    m.cut('MCUPackage',[m.parts['MCUPin'+str(i)].Shape for i in range(64)],'Individual package lead exits').Refine=False
    rot=App.Rotation(V(1,0,0),180)
    m.label('MCUMark','SM510',2.0,(.3,1.5,4.11),'Mainboard',-3,'white',rotation=rot)
    for i,(text,x,y,size) in enumerate([('Nintendo',-15,23,2.5),('4.3 mm SCREW',12,-19,1.8),('DK-52 STUDY',-18,-27,1.8)]):m.label('BoardRearMark'+str(i),text,size,(x,y,5.77),'Mainboard',-2,'white',rotation=rot)
    # Separate carbon fingers follow physical control locations, nonfunctional schematic pattern.
    contacts=[(-43.4,-13.5),(-38.9,-18),(-43.4,-22.5),(-47.9,-18),(43.4,-18),(40.5,24),(40.5,16.5),(40.5,9)]
    for i,(x,y) in enumerate(contacts):
        for j in range(6):m.box('SwitchFinger'+str(i)+'_'+str(j),'Interdigitated carbon switch finger',.28,3.4,.03,(x-1.25+j*.5,y,6.56),'Mainboard',-2,'ink',.03,True)
    for i,y in enumerate([20.5,13]):m.ring('MetalButtonPad'+str(i),'Alarm or ACL copper contact pad',1.1,.45,.035,(49,y,6.56),'Mainboard',-2,'copper',internal=True)
    _finish(m,7,'phenolic_board_sm510_and_control_contacts','按原机照片建立带电池缺口的酚醛主板、绿色控制面、菱形 SM510 封装和独立引脚/碳接点。器件身份参照 MAME 原始逆向源码，局部封装与布线为非功能近似。')

STAGES[7]=stage07


def stage08(m):
    # Original discrete timing and supply components on the rear face.
    for i,(x,y,r,length,mat) in enumerate([(-28,11,1.8,5.5,'blue'),(-28,3,1.35,4.2,'pcb')]):
        m.cyl('CapBody'+str(i),'Original discrete capacitor body',r,length,(x-length/2,y,3.6),'Mainboard',-3,mat,axis=(1,0,0),internal=True)
        for j,xx in enumerate([x-length/2-.45,x+length/2+.45]):
            m.cyl('CapLead'+str(i)+'_'+str(j),'Capacitor axial lead',.17,1.65,(xx,y,3.8),'Mainboard',-3,'metal',internal=True)
    m.cyl('CrystalCan','Original cylindrical watch timing crystal',1.2,6,(23,0,3.8),'Mainboard',-3,'metal',axis=(1,0,0),internal=True)
    for i,y in enumerate([-1.1,1.1]):m.cyl('CrystalLead'+str(i),'Crystal lead',.15,1.6,(29.5,y,4.1),'Mainboard',-3,'metal',internal=True)
    for i,(x,y,mat) in enumerate([(29,8,'foil'),(30,-7,'foil'),(45,-3,'blue')]):
        if i<2:m.box('DiscreteBody'+str(i),'Original ceramic discrete body',3.5,2.2,1.4,(x,y,3.7),'Mainboard',-3,mat,.7,True)
        else:m.cyl('DiscreteBody'+str(i),'Original axial resistor body',.85,4.5,(x,y-2.25,4.2),'Mainboard',-3,mat,axis=(0,1,0),internal=True)
        for j,dy in enumerate([-2.9,2.9]):m.cyl('DiscreteLead'+str(i)+'_'+str(j),'Discrete component wire lead',.15,1.45,(x,y+dy,4.2),'Mainboard',-3,'metal',internal=True)
    # Each solder termination is separate and matched by a clearance bore through the PCB.
    leadkeys=[k for k in m.parts if k.startswith(('CapLead','CrystalLead','DiscreteLead'))]
    holes=[]
    for i,key in enumerate(leadkeys):
        b=m.parts[key].Shape.BoundBox;x,y=b.Center.x,b.Center.y;holes.append(Part.makeCylinder(.24,1.2,V(x,y,5.5)))
        m.ring('SolderJoint'+str(i),'Through-hole solder annulus',.48,.25,.10,(x,y,6.57),'Mainboard',-2,'metal',internal=True)
    for key in ['Mainboard','BoardMask']:m.cut(key,holes,'Discrete lead through holes').Refine=False
    _finish(m,8,'original_crystal_capacitors_and_axial_components','补入背面圆柱时钟晶体、两枚电容、陶瓷/轴向分立件和独立引线焊点；布置参照拆解照片，电气参数和精确电路不作复刻。')

STAGES[8]=stage08


def stage09(m):
    m.cut('BackCover',m.rr(16,29.5,1.6,(-46,17,-.1),.35),'Original removable button-cell cover opening').Refine=False
    m.box('BatteryDoor','Original orange sliding battery cover',15.6,29.1,.9,(-46,17,.1),'Body',-6,'orange',.25)
    for i,y in enumerate([3.2,30.8]):m.box('BatteryDoorTab'+str(i),'Battery cover retaining tab',10,1,.3,(-46,y,1.03),'Body',-6,'orange',.1)
    for j,y in enumerate([10.2,23.4]):
        m.ring('CellWell'+str(j),'Original round button-cell well',6.4,5.98,5.85,(-46,y,1.4),'Battery',-4,'orange',internal=True)
        m.ring('CellCan'+str(j),'LR44/SR44 metal cell can',5.8,5.43,5.1,(-46,y,1.8),'Battery',-4,'metal',internal=True)
        m.cyl('CellBottom'+str(j),'Button-cell negative end',5.36,.25,(-46,y,1.8),'Battery',-4,'metal',internal=True)
        m.cyl('CellCore'+str(j),'Schematic nonfunctional cell core',5.25,4.35,(-46,y,2.1),'Battery',-4,'battery',internal=True)
        m.ring('CellSeal'+str(j),'Button-cell insulating gasket',5.39,4.85,.25,(-46,y,6.55),'Battery',-4,'black',internal=True)
        m.cyl('CellPositive'+str(j),'Button-cell positive cap',4.8,.32,(-46,y,6.58),'Battery',-4,'metal',internal=True)
        m.box('CellRearSpring'+str(j),'Original rear spring contact strip',3,9,.16,(-46,y,1.54),'Battery',-5,'metal',.12,True)
        m.box('CellFrontContact'+str(j),'Original front contact strip',3,10,.16,(-46,y,7.04),'Battery',-4,'metal',.12,True)
        m.label('CellMark'+str(j),'LR44',1.7,(-48.5,y-.7,6.94),'Battery',-4,'ink')
        # individual strips enter PCB at the right edge of the wells
        m.box('CellTerminal'+str(j),'Button-cell terminal tail',7,.9,.16,(-38.9,y,7.04),'Battery',-4,'metal',.08,True)
        m.cut('CellWell'+str(j),m.parts['CellTerminal'+str(j)].Shape,'Cell terminal exit notch').Refine=False
    arrow=_poly([(-49,17),(-44,17),(-44,19),(-42,16),(-44,13),(-44,15),(-49,15)],.06,.018)
    m.feature('BatteryDoorArrow','Molded battery-cover slide direction',arrow,'Body',-6,'orange')
    _finish(m,9,'two_original_button_cells_wells_contacts_and_cover','加入两枚 LR44/SR44 学习电池、独立金属杯/端盖/密封圈、圆形电池仓和接点，并据存留原机照片建立滑动电池盖及方向箭头。')

STAGES[9]=stage09


def _wire(points,r):
    vs=[V(*p) for p in points];segments=[]
    for a,b in zip(vs,vs[1:]):segments.append(Part.makeCylinder(r,(b-a).Length,a,(b-a).normalize()))
    for p in vs[1:-1]:segments.append(Part.makeSphere(r,p))
    return segments[0].multiFuse(segments[1:]).removeSplitter()


def stage10(m):
    m.ring('PiezoSeat','Rear-case piezo locating ring',13.6,13.1,.8,(1,-17,1.3),'Audio',-5,'orange',internal=True)
    m.cyl('PiezoBrass','Original rear-case brass piezo disk',13,.22,(1,-17,1.4),'Audio',-5,'foil',internal=True)
    m.cyl('PiezoCeramic','Piezo ceramic element',9.7,.24,(1,-17,1.67),'Audio',-5,'white',internal=True)
    m.cyl('PiezoElectrode','Piezo silver electrode face',8.5,.03,(1,-17,1.96),'Audio',-5,'metal',internal=True)
    routes=[[(7,-17,2.23),(11,-22,2.23),(21,-25,2.23),(39,-25,3.1),(45,-26,5.6)],[(11,-18,1.97),(15,-22,2.05),(24,-22,2.1),(40,-22,3.1),(47,-24,5.6)]]
    for i,pts in enumerate(routes):
        m.feature('PiezoWire'+str(i),'Original piezo red lead',_wire(pts,.18),'Audio',-4,'red',True)
        x,y,z=pts[-1];m.cyl('PiezoSolder'+str(i),'Piezo wire solder pad',.55,.12,(x,y,5.65),'Audio',-3,'metal',internal=True)
        m.cut('PiezoSolder'+str(i),m.parts['PiezoWire'+str(i)].Shape,'Solder termination wire seat').Refine=False
    m.cut('PiezoSeat',[m.parts['PiezoWire'+str(i)].Shape for i in range(2)],'Two piezo lead exit grooves').Refine=False
    for o in m.parts.values():
        if o.Assembly=='Audio':
            place=o.Placement;place.Base+=V(0,3.5,0);o.Placement=place;o.FlatPlacement=place
    _finish(m,10,'original_rear_piezo_disk_and_two_red_leads','建立后壳压电音片的黄铜基片、陶瓷层、电极和两根独立红色导线；原机为压电发声结构，不混用现代扬声器或振动马达。')

STAGES[10]=stage10


def stage11(m):
    plate=m.rr(106,59,.27,(0,69.25,6.5),.5).cut(m.rr(50,27,.6,(0,70,6.35),1.5))
    m.feature('UpperRetainer','Original stamped upper LCD retaining plate',plate,'LidInternal',1,'metal',True,'Lid')
    for i,(x,y,w,h) in enumerate([(-27.4,70,.6,30),(27.4,70,.6,30),(0,85.3,53,.6),(0,54.7,53,.6),(-41,70,.6,47),(41,70,.6,47)]):
        m.box('UpperPressedRib'+str(i),'Retainer pressed stiffening rib',w,h,.25,(x,y,6.8),'LidInternal',1,'metal',.15,True,'Lid')
    for i,(x,y) in enumerate([(-48,92),(48,92),(0,97),(-47,44),(47,44)]):
        m.ring('RetainerPost'+str(i),'Upper retainer screw boss',1.7,.76,4.8,(x,y,1.6),'LidInternal',0,'orange',internal=True,pose='Lid')
        m.cut('UpperRetainer',Part.makeCylinder(.85,1,V(x,y,6.3)),'Retainer screw clearance').Refine=False
        m.screw('RetainerScrew'+str(i),(x,y,7.14),'LidInternal',1,length=3.7,radius=1.25,pose='Lid',axis=(0,0,-1))
    # Molded locating ledges around the two display stacks keep the glass and gasket separable.
    for name,cy,pose,assembly in [('Lower',-1.5,'Base','Internal'),('Upper',70,'Lid','LidInternal')]:
        for side in [-1,1]:m.box(name+'GlassGuide'+str(side),'LCD lateral locating ledge',.7,39,1.9,(side*32,cy,7.25),assembly,2,'orange',.12,True,pose)
    _finish(m,11,'stamped_upper_retainer_and_lcd_guides','建立原版上屏冲压金属压板、窗口、压筋及五枚独立小螺钉/螺柱，并补入两屏玻璃定位边；压板不是一块替代屏幕的封闭金属片。')

STAGES[11]=stage11


def stage12(m):
    lower=[(-35,27),(35,27),(-35,-28),(0,-29),(35,-28)]
    for i,(x,y) in enumerate(lower):
        bore=Part.makeCylinder(.78,12,V(x,y,-.1));seat=Part.makeCylinder(1.55,.72,V(x,y,-.05))
        m.cut('BackCover',[bore,seat],'Five original lower-case fastener seats').Refine=False
        for key in ['Mainboard','BoardMask']:m.cut(key,Part.makeCylinder(.9,1.1,V(x,y,5.6)),'Long case fastener PCB clearance').Refine=False
        m.ring('LowerCaseBoss'+str(i),'Lower case screw guide',1.8,.8,4.1,(x,y,1.35),'Internal',-4,'orange',internal=True)
        m.ring('UpperCaseBoss'+str(i),'Control deck threaded boss',1.8,.70,3.5,(x,y,6.58),'Internal',0,'orange',internal=True)
        m.screw('CaseScrew'+str(i),(x,y,.20),'Fixings',-6,length=8.2,radius=1.4)
    for i,(x,y) in enumerate([(-29,94),(29,94),(-42,44),(42,44)]):
        bore=Part.makeCylinder(.78,7,V(x,y,4.7));seat=Part.makeCylinder(1.6,.7,V(x,y,10.57))
        m.cut('LidBezel',[bore,seat],'Four original upper-face screw seats').Refine=False
        m.cut('UpperRetainer',Part.makeCylinder(1.95,1,V(x,y,6.3)),'Upper cover fastening boss clearance').Refine=False
        m.ring('UpperExternalBoss'+str(i),'Upper outer case threaded boss',1.8,.7,8.45,(x,y,1.6),'LidInternal',0,'orange',internal=True,pose='Lid')
        m.screw('UpperCaseScrew'+str(i),(x,y,11.0),'Fixings',5,length=5.2,radius=1.4,pose='Lid',axis=(0,0,-1))
    for i,(x,y) in enumerate([(-29,-24),(28,-24),(0,27),(-30,25),(30,25)]):
        for key in ['Mainboard','BoardMask']:m.cut(key,[Part.makeCylinder(.85,1.2,V(x,y,5.6)),Part.makeCylinder(1.3,.35,V(x,y,5.75))],'Five original PCB fastener bores').Refine=False
        m.ring('PCBPost'+str(i),'Original PCB mounting post',1.6,.72,3.5,(x,y,6.65),'Internal',0,'orange',internal=True)
        m.screw('PCBScrew'+str(i),(x,y,5.65),'Fixings',-2,length=3.7,radius=1.2)
    m.cut('LowerDisplayGasket',[m.parts['PCBPost'+str(i)].Shape for i in range(5)],'LCD gasket screw-post clearance').Refine=False
    m.cut('MenuRubber',m.parts['UpperCaseBoss1'].Shape,'System membrane screw-post clearance').Refine=False
    _finish(m,12,'nineteen_original_external_and_internal_fasteners','补齐五枚下壳长螺钉、四枚上盖外螺钉、五枚主板小螺钉，加上前轮五枚压板螺钉共十九枚；保留各自孔、沉座和独立螺柱。')

STAGES[12]=stage12


def stage13(m):
    # Printed film over the central hinge, with independent stationary/upper tails.
    # The rolled bridge is a pose-clearance study, not a validated fatigue/bend-radius design.
    m.ring('HingeRibbon','White printed inter-screen flex bridge',1.60,1.51,66,(-33,34,11.5),'Wiring',0,'white',axis=(1,0,0),internal=True)
    for i in range(40):m.ring('HingeConductor'+str(i),'Printed black flex conductor',1.625,1.607,.65,(-32+i*1.63,34,11.5),'Wiring',0,'ink',axis=(1,0,0),internal=True)
    for name,y,pose,assembly in [('Lower',28,'Base','Wiring'),('Upper',40,'Lid','LidInternal')]:
        m.box(name+'RibbonTail',name+' inter-screen printed film tail',66,8,.08,(0,y,9.68),assembly,3,'white',.15,True,pose)
        for i in range(40):m.box(name+'RibbonTrace'+str(i),'Individual printed conductor',.65,7.8,.018,(-32+i*1.63,y,9.79),assembly,3,'ink',.025,True,pose)
        deck='FrontDeck' if name=='Lower' else 'LidBezel'
        m.cut(deck,m.rr(67,4,2.1,(0,32.2 if name=='Lower' else 36.8,9.4),.3),'Original center flex exit').Refine=False
        if name=='Upper':m.cut('LidFrame',m.rr(67,9,1,(0,40,9.4),.3),'Upper flex feed through frame').Refine=False
        # Tail has physical post clearance, as photographed around upper retainer posts.
        tools=[]
        for o in m.parts.values():
            if o.PartID.startswith('PCBPost' if name=='Lower' else 'RetainerPost'):
                b=o.Shape.BoundBox;tools.append(Part.makeCylinder(1.85,4,V(b.Center.x,b.Center.y,7)))
        if tools:
            for key in [name+'RibbonTail']+[name+'RibbonTrace'+str(i) for i in range(40)]:
                if any(m.parts[key].Shape.common(t).Volume>1e-8 for t in tools):m.cut(key,tools,'Flex routing around screw posts').Refine=False
    _finish(m,13,'white_printed_hinge_flex_and_separate_tails','加入中央外露白色印刷排线、四十条黑色导体和上下独立引出片；排线绕开固定柱，卷曲桥段用于开合间隙示意，不作为柔性寿命或电路认证。')

STAGES[13]=stage13


def stage14(m):
    # A few independent dark segments distinguish a fixed-game LCD from a generic blank display.
    # Stylized geometry, not exact Nintendo artwork or a playable screen state.
    z=8.975
    for k,(x,y,pose,assembly) in enumerate([(-12,-10,'Base','Display'),(-24,84,'Lid','LidDisplay')]):
        parts=[Part.makeCylinder(.8,.018,V(x,y+3,z)),m.rr(1.7,2.5,.018,(x,y+1.1,z),.25),m.rr(1.5,.6,.018,(x+.15,y+3.7,z),.12)]
        for dx in [-1,1]:
            parts.append(_poly([(x+dx*.35,y+.5),(x+dx*1.3,y-.9),(x+dx*1.7,y-.8),(x+dx*.75,y+1)],z,.018))
            parts.append(_poly([(x+dx*.6,y+1.5),(x+dx*1.6,y+2.3),(x+dx*1.9,y+2),(x+dx*.7,y+1)],z,.018))
        shape=parts[0].multiFuse(parts[1:]).removeSplitter();m.feature('LCDPlayer'+str(k),'Schematic fixed-game character segments',shape,assembly,6,'ink',False,pose)
    for k,(x,y) in enumerate([(9,-10),(-1,7)]):
        sh=Part.makeCylinder(1.4,.018,V(x,y,z)).cut(Part.makeCylinder(.9,.05,V(x,y,z-.01)))
        sh=sh.fuse(m.rr(.4,2.6,.018,(x,y,z),.03)).removeSplitter();m.feature('LCDBarrel'+str(k),'Schematic barrel segment',sh,'Display',6,'ink')
    m.label('LCDClock','12:00',2.25,(14,-18,8.975),'Display',6,'ink')
    # Original small raised ridges immediately above lower screen and on inner rim.
    m.box('LowerScreenRidge','Molded lower-screen upper ridge',53,.55,.14,(0,26,11.09),'Body',5,'orange',.13)
    for i,x in enumerate([-54.5,54.5]):m.box('LowerSideLip'+str(i),'Fine molded side lip',.4,60,.12,(x,-.5,11.09),'Body',5,'orange',.08)
    _finish(m,14,'fixed_game_segments_and_final_surface_details','补入少量独立黑色液晶人物/桶/时钟段和面壳细脊，明确是按原机视觉重构的非功能示意，保留双屏固定游戏的外观。')

STAGES[14]=stage14


def stage15(m):
    carrier=m.rr(61,43,.32,(0,-1.5,6.7),.65).cut(m.rr(53,35,.6,(0,-1.5,6.55),.4))
    tools=[]
    for o in m.parts.values():
        if o.PartID.startswith('PCBPost'):
            b=o.Shape.BoundBox;tools.append(Part.makeCylinder(1.85,1,V(b.Center.x,b.Center.y,6.4)))
    carrier=carrier.cut(Part.makeCompound(tools));m.feature('LowerLCDCarrier','Original lower LCD insulating support rim',carrier,'Internal',1,'silicone',True)
    for name,cy,pose,assembly in [('Lower',-1.5,'Base','Internal'),('Upper',70,'Lid','LidInternal')]:
        for side in [-1,1]:m.box(name+'LCDStop'+str(side),'LCD transverse locating stop',48,.55,.6,(0,cy+side*21.6,8.0),assembly,2,'orange',.1,True,pose)
    _finish(m,15,'lcd_support_rim_and_final_original_assembly','补齐下屏绝缘支承框与上下屏横向定位止口；保留原版电池供电、反射式双 LCD 和机械开合结构，进入独立重建及多姿态完整核验。')

STAGES[15]=stage15


def finalize(model):
    from .deliver import finalize as shared_finalize
    previous=App.ParamGet('User parameter:BaseApp/Preferences/Mod/Part/General').GetInt('WriteSurfaceCurveMode',1)
    Part.setStaticValue('write.surfacecurve.mode',1)
    try:
        result=shared_finalize(model)
        # Rear-facing markings need -Y camera up to remain readable.
        def rear_snapshot(name,normal,assemblies,exclude=()):
            objects=model.visible(assemblies,exclude)
            q=g.rotation(normal,(0,-1,0));shape=Part.makeCompound([o.Shape for o in objects])
            shape.Placement=App.Placement(V(),q.inverted()).multiply(shape.Placement)
            b=shape.optimalBoundingBox(False,False)
            return g.render(model.out/'previews'/(name+'.png'),normal=normal,up=(0,-1,0),target=tuple(q.multVec(b.Center)),span=max(b.YLength,b.XLength*1400/1800)*1.16,size=(1800,1400))
        rear_snapshot('final_board',(0,0,-1),['Mainboard'])
        rear_snapshot('final_internal',(.2,-.3,-2),model.profile['internal_groups'],model.profile.get('internal_exclude',[]))
        model.snapshot('final_controls',normal=(.15,-.4,2),assemblies=['Controls','ControlsInternal'])
        model.snapshot('final_battery',normal=(.2,-.3,2),assemblies=['Battery'])
        model.snapshot('final_hinge',normal=(.2,-.5,1.5),assemblies=['Hinge','Wiring'])
        model.doc.save();return result
    finally:Part.setStaticValue('write.surfacecurve.mode',previous)
