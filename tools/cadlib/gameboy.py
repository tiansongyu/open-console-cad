"""Original grey DMG-01 Game Boy, native shell history and staged component geometry."""
import math
import FreeCAD as App
import Part
from .core import V
from .clamshell import _move,_replace
from .psp import _polygon


def _vertical_edges(shape,t,points):
    result=[]
    for i,e in enumerate(shape.Edges):
        if abs(e.BoundBox.ZLength-t)>1e-6 or e.BoundBox.XLength>1e-6 or e.BoundBox.YLength>1e-6:continue
        p=e.Vertexes[0].Point
        if any(abs(p.x-x)<1e-5 and abs(p.y-y)<1e-5 for x,y in points):result.append((i+1,e))
    return result


def _outline(m,w,h,small,big,z,t):
    sh=Part.makeBox(w,h,t,V(-w/2,-h/2,z))
    sh=sh.makeFillet(big,[e for _,e in _vertical_edges(sh,t,[(w/2,-h/2)])])
    return sh.makeFillet(small,[e for _,e in _vertical_edges(sh,t,[(-w/2,-h/2),(-w/2,h/2),(w/2,h/2)])])


def _native_enclosure(m,key,label,w,h,small,big,z,t,layer):
    from . import geometry as g
    body=m.doc.addObject('PartDesign::Body',key+'Body');body.Label=label
    sketch=g.rect_sketch(m.doc,key+'Sketch',w,h);body.addObject(sketch)
    pad=body.newObject('PartDesign::Pad',key+'Pad');pad.Profile=(sketch,['']);pad.Length=t;m.doc.recompute()
    large=body.newObject('PartDesign::Fillet',key+'SpeakerCorner');large.Base=(pad,['Edge'+str(i) for i,_ in _vertical_edges(pad.Shape,t,[(w/2,-h/2)])]);large.Radius=big;m.doc.recompute()
    other=body.newObject('PartDesign::Fillet',key+'OtherCorners');other.Base=(large,['Edge'+str(i) for i,_ in _vertical_edges(large.Shape,t,[(-w/2,-h/2),(-w/2,h/2),(w/2,h/2)])]);other.Radius=small;m.doc.recompute()
    assert other.Shape.isValid() and not other.Shape.isNull(),key
    body.Tip=other;body.Placement.Base=V(0,0,z)
    sketch.setExpression('Constraints.Width','Parameters.Width'+(' - 0.2 mm' if w<90 else ''))
    sketch.setExpression('Constraints.Height','Parameters.Height'+(' - 0.2 mm' if h<148 else ''))
    m.doc.recompute();sketch.Visibility=False;pad.Visibility=False;large.Visibility=False
    return m.register(body,key,'Body',layer,'dmgcase')


def _rotate_shape(shape,center,angle):
    shape.rotate(V(*center),V(0,0,1),angle);return shape


def stage01(m):
    m.colors.update({'dmgcase':(.70,.70,.67),'dmgbezel':(.25,.26,.30),'dmglcd':(.43,.50,.18),'dmgbutton':(.43,.025,.18),'dmgink':(.10,.12,.31),'dmgline':(.32,.035,.17)})
    for key,label,w,h,r,t,z,layer in [
        ('BackCover','Rear enclosure base',90,148,7,1.2,0,-6),
        ('RearShell','Rear enclosure skirt',90,148,7,15.2,1.3,-6),
        ('MainFrame','Front enclosure skirt',90,148,7,12.95,16.6,0),
        ('FrontFace','Front control and display panel',89.8,147.8,6.9,1.15,29.65,4)]:
        _native_enclosure(m,key,label,w,h,r,20 if w==90 else 19.9,z,t,layer)
    for key,z,t in [('RearShell',1.2,15.5),('MainFrame',16.5,13.2)]:
        m.cut(key,_outline(m,86.8,144.8,5.4,18.4,z,t),'Enclosure internal cavity')
    m.checkpoint(1,'dmg_native_split_enclosure','建立 90 × 148 mm 原生外壳轮廓、前后侧壁与盖板，保留经典右下大圆角和中部分壳接缝；控制件完成后核对 32 mm 总厚度。')


def stage02(m):
    # Bezel has the DMG's distinctive larger lower-right corner, independently cut.
    bezel=_outline(m,77,57.5,2.4,10.5,30.0,.76);bezel.translate(V(0,35,0))
    hole=_outline(m,77.3,57.8,2.55,10.65,29.4,1.7);hole.translate(V(0,35,0));m.cut('FrontFace',hole,'Original DMG bezel recess')
    window=m.rr(47.3,43.3,1.1,(0,35.8,29.85),.3)
    m.feature('DisplayBezel','Dark-grey display surround',bezel.cut(window),'Display',5,'dmgbezel')
    m.box('LCDBackplate','LCD backing plate',58,52,.35,(0,35.8,25.0),'Display',1,'metal',1.4,True)
    m.box('LCD','Reflective monochrome LCD module',56,50,3.5,(0,35.8,25.6),'Display',2,'black',1.2,True)
    m.box('LCDPolarizer','LCD polarizer study',47,43,.12,(0,35.8,30.38),'Display',3,'dmglcd',.25,True)
    m.box('DisplayGlass','47 x 43 mm display window',47,43,.18,(0,35.8,30.60),'Display',7,'dmglcd',.25)
    m.cyl('BatteryLED','Battery indicator lens',1.0,.12,(-32,40.0,30.60),'Display',5,'red')
    m.cut('DisplayBezel',Part.makeCylinder(1.15,1,V(-32,40,29.9)),'Battery-indicator aperture')
    m.label('BatteryLEDMark','BATTERY',1.55,(-35.7,35.6,30.778),'Display',5,'white')
    m.label('DisplayTechnologyMark','DOT MATRIX WITH STEREO SOUND',1.5,(-12,60.0,30.778),'Display',5,'white')
    for side,x,w in [('Left',-24.3,20),('Right',32.7,7.3)]:
        m.box('DisplayRedLine'+side,'Upper burgundy bezel rule',w,.28,.018,(x,61.0,30.778),'Display',5,'dmgline',.05)
        m.box('DisplayBlueLine'+side,'Lower blue bezel rule',w,.22,.018,(x,59.75,30.778),'Display',5,'dmgink',.04)
    m.label('NintendoFrontWord','Nintendo',3.4,(-38,-2.5,30.818),'Body',4,'dmgink')
    m.label('GameBoyFrontWord','GAME BOY',4.1,(-15.5,-2.5,30.818),'Body',4,'dmgink')
    m.checkpoint(2,'monochrome_lcd_and_dmg_bezel','加入 47 × 43 mm 单色显示层、非背光 LCD、灰色大圆角边框、电量指示灯与双色装饰线，记录初代文字布局。')


def stage03(m):
    x,y=-26,-26
    cross=m.rr(7,22,1.0,(x,y,30.95),.6).fuse(m.rr(22,7,1.0,(x,y,30.95),.6)).removeSplitter()
    m.feature('DPad','Original cross directional pad',cross,'Controls',6,'black')
    bore=m.rr(7.35,22.35,1.8,(x,y,29.4),.75).fuse(m.rr(22.35,7.35,1.8,(x,y,29.4),.75));m.cut('FrontFace',bore,'D-pad through aperture')
    # Four shallow tactile ridges and a center dish belong to the cap geometry.
    m.cut('DPad',Part.makeSphere(5,V(x,y,36.72)),'Directional-pad shallow center dish')
    for i,(dx,dy) in enumerate([(0,6.0),(6.0,0),(0,-6.0),(-6.0,0)]):
        m.cyl('DPadStem'+str(i),'Directional plunger',1.4,2.45,(x+dx,y+dy,28.35),'ControlsInternal',3,'black',internal=True)
        for j in [-1,1]:
            w,h=(2.8,.28) if dx==0 else (.28,2.8)
            xx,yy=x+dx+(j*.7 if dy==0 else 0),y+dy+(j*.7 if dx==0 else 0)
            m.cut('DPad',m.rr(w,h,.12,(xx,yy,31.86),.06),'Directional tactile groove')
    for key,x,y in [('A',33,-20),('B',18,-27)]:
        m.cut('FrontFace',Part.makeCylinder(5.85,1.8,V(x,y,29.4)),'Burgundy action-button aperture')
        cap=Part.makeCylinder(5.6,1.15,V(x,y,30.85));cap=cap.makeFillet(.22,[e for e in cap.Edges if e.BoundBox.ZLength<1e-6])
        m.feature('Button'+key,key+' button',cap,'Controls',6,'dmgbutton')
        m.cyl('ButtonStem'+key,'Action-button plunger',1.55,3.0,(x,y,27.65),'ControlsInternal',3,'dmgbutton',internal=True)
        m.label('ButtonMark'+key,key,2.9,(x+2.5,y-11,30.818),'Body',4,'dmgink',rotation=App.Rotation(V(0,0,1),25))
    for key,x,y in [('Select',-12,-48),('Start',4,-48)]:
        sh=_rotate_shape(m.rr(11.7,3.8,.75,(x,y,30.65),1.85),(x,y,0),25)
        bore=_rotate_shape(m.rr(12.0,4.1,1.8,(x,y,29.4),2.0),(x,y,0),25)
        m.cut('FrontFace',bore,'Angled Start/Select slot');m.feature(key+'Key',key+' rubber button',sh,'Controls',6,'rubber')
        m.label(key+'Mark',key.upper(),2.15,(x-4.7,y-7.4,30.818),'Body',4,'dmgink',rotation=App.Rotation(V(0,0,1),25))
    slots=[]
    for i in range(6):
        x,y=13+i*4.7,-64+i*2.7
        slots.append(_rotate_shape(m.rr(2.1,16.2,1.8,(x,y,29.4),1.0),(x,y,0),30))
    m.cut('FrontFace',slots,'Six diagonal speaker slots')
    m.box('SpeakerMesh','Speaker acoustic mesh',27,23,.12,(25,-56,29.35),'Audio',4,'black',4.0,True)
    m.checkpoint(3,'dpad_burgundy_buttons_and_speaker_grille','建立十字键、酒红 A/B 键、倾斜 START/SELECT 键与六条斜向扬声器开孔，保留独立按键传动柱和声学网层。')

STAGES={1:stage01,2:stage02,3:stage03}
