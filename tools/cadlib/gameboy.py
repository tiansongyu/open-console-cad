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


def stage04(m):
    # A disk's exposed knurled arc is flush with the nominal 90 mm envelope.
    for name,x,y,z,assembly in [('Contrast',-39.8,35,20.7,'ControlsInternal'),('Volume',39.8,19,10.7,'Mainboard')]:
        sh=Part.makeCylinder(5.2,1.55,V(x,y,z))
        teeth=[]
        for i in range(40):
            a=2*math.pi*i/40;teeth.append(Part.makeCylinder(.19,1.8,V(x+5.12*math.cos(a),y+5.12*math.sin(a),z-.1)))
        m.feature(name+'Wheel',name+' adjustment wheel',sh.cut(Part.makeCompound(teeth)),'Controls',0,'black')
        clearance=Part.makeCylinder(5.38,1.9,V(x,y,z-.15))
        m.cut('MainFrame' if name=='Contrast' else 'RearShell',clearance,name+' thumbwheel clearance')
        m.cyl(name+'Spindle','Potentiometer spindle',.8,3,(x,y,z-1.2),assembly,1,'metal',internal=True)
        m.box(name+'Pot','Rotary potentiometer body',7.5,7.5,1.9,(x,y,z+1.85),assembly,1,'black',1.0,True)
        m.cut(name+'Wheel',Part.makeCylinder(.95,2,V(x,y,z-.1)),'Potentiometer spindle clearance')
    right=App.Rotation(V(0,0,1),V(1,0,0));left=App.Rotation(V(0,0,1),V(-1,0,0));bottom=App.Rotation(V(0,0,1),V(0,-1,0))
    # Link port rectangular section, with six contacts and a separate insulator.
    outer=m.rr(12.4,4.8,5.5,(39.4,42,8.5),.8,right)
    inner=m.rr(10.4,2.8,6,(39.2,42,8.5),.35,right)
    m.feature('LinkPortShell','Original large Game Link receptacle',outer.cut(inner),'Ports',-2,'metal')
    m.cut('RearShell',m.rr(12.8,5.2,6,(39.2,42,8.5),.9,right),'Game Link side opening')
    m.box('LinkPortTongue','Link port insulator',8.4,.6,4.3,(40.4,42,8.5),'Ports',-2,'black',.15,orient=right)
    for i in range(6):m.box('LinkPin'+str(i),'Game Link contact study',.55,.10,3.2,(41.1,38.25+i*1.5,8.9),'Ports',-2,'gold',.02,orient=right)
    m.cut('RearShell',Part.makeCylinder(2.75,6,V(-39.2,35,8.6),V(-1,0,0)),'DC adapter inlet')
    m.ring('DCJack','6 V DC adapter socket',2.5,1.65,5.4,(-39.5,35,8.6),'Ports',-2,'black',axis=(-1,0,0))
    m.cyl('DCJackContact','DC socket center contact',.55,3.7,(-40.6,35,8.6),'Ports',-2,'metal',axis=(-1,0,0),internal=True)
    m.cut('RearShell',Part.makeCylinder(2.7,6,V(0,-68.4,9.3),V(0,-1,0)),'Stereo headphone outlet')
    m.ring('HeadphoneJack','Bottom 3.5 mm headphone socket',2.5,1.77,5.5,(0,-68.5,9.3),'Ports',-4,'black',axis=(0,-1,0))
    top=App.Rotation(V(0,0,1),V(0,1,0))
    cap=m.rr(11.5,4,.7,(-27,73.3,22),.75,top)
    m.feature('PowerSlider','Top on-off slider',cap,'Controls',0,'black');m.cut('MainFrame',cap,'Power slider seat')
    m.box('PowerSwitchBody','Slide power switch',12,5,3.2,(-27,67.5,18.6),'ControlsInternal',1,'metal',.55,True)
    m.box('PowerSwitchLink','Power switch transmission tab',3.2,3.8,1.3,(-27,71.9,21.2),'ControlsInternal',1,'black',.4,True)
    for i,x in enumerate([-30.5,-28.75,-27,-25.25,-23.5]):
        m.cut('PowerSlider',m.rr(.35,3,.15,(x,73.9,22),.05,top),'Power slider grip groove')
    m.label('PowerMark','OFF  -  ON',1.9,(-35,70.0,30.818),'Body',4,'dmgcase')
    m.cut('FrontFace',m.rr(82,.4,.25,(0,67.7,30.60),.12),'Upper enclosure seam detail')
    # Cover the whole slanted grille, while respecting the curved case boundary.
    mesh=m.rr(35,34,.12,(25,-57,29.35),2).common(_outline(m,86.8,144.8,5.4,18.4,29.35,.12))
    _replace(m,'SpeakerMesh',mesh)
    m.checkpoint(4,'dmg_wheels_link_power_and_audio_ports','加入对比度与音量滚轮、原始大尺寸通信口、6V 电源口、耳机口和顶部电源滑块，同时补齐扬声器网层的覆盖范围。')


def _tri_screw(m,key,x,y,z,length,layer=-6):
    sh=Part.makeCylinder(1.75,.55).fuse(Part.makeCylinder(.8,length,V(0,0,.50)))
    cuts=[]
    for angle in [0,120,240]:
        tool=Part.makeBox(.35,1.6,.35,V(-.175,-.1,-.01));tool.rotate(V(),V(0,0,1),angle);cuts.append(tool)
    sh=sh.cut(Part.makeCompound(cuts));sh.translate(V(x,y,z))
    return m.feature(key,'Tri-point case fastener',sh,'Body',layer,'metal',True)


def stage05(m):
    # Rear cartridge cutout exposes the top of the otherwise internal cartridge channel.
    m.cut('BackCover',m.rr(61,28,1.5,(0,60.1,-.1),1.0),'Rear cartridge entry cutout')
    m.cut('RearShell',m.rr(61,7,8.0,(0,72.5,.2),.8),'Open top of cartridge well')
    m.cut('BackCover',m.rr(70.4,62.4,1.5,(0,-40,-.1),3.2),'Removable battery cover opening')
    door=m.rr(70,62,.9,(0,-40,.15),3.0)
    latch=m.rr(9,4,2.7,(0,-8.9,.55),.6)
    door=door.fuse(latch).removeSplitter()
    for x in [-22,22]:door=door.fuse(m.rr(6,2.5,1.0,(x,-71.2,.35),.4))
    m.feature('BatteryDoor','Four-AA battery cover and latch',door.removeSplitter(),'Body',-6,'dmgcase')
    for i,(x,y) in enumerate([(-36,61),(36,61),(-36,11),(36,11),(-34,-66),(34,-66)]):
        m.cut('BackCover',[Part.makeCylinder(.95,2,V(x,y,-.1)),Part.makeCylinder(2.1,.8,V(x,y,-.1))],'Rear case fastener seat')
        _tri_screw(m,'CaseScrew'+str(i),x,y,.10,7.4)
        m.ring('CaseBoss'+str(i),'Rear case screw boss',2.9,.95,7.5,(x,y,1.3),'Internal',-4,'dmgcase',internal=True)
    reverse=App.Rotation(V(0,1,0),180)
    for key,text,size,pos in [('RearModel','MODEL NO. DMG-01',2.6,(29,34,.018)),('RearNintendo','Nintendo GAME BOY',2.25,(29,28,.018)),('RearRating','DC 6V  /  4 x AA',2.25,(29,22,.018)),('RearStudy','1989  /  CAD STUDY',2.0,(29,16,.018))]:
        m.label(key,text,size,pos,'Body',-6,'dmgbezel',rotation=reverse);m.cut('BackCover',m.parts[key].Shape,'Rear information inlay')
    # Continuous transverse grooves are shared by the cover and rear-case edges.
    grooves=[m.rr(94,.32,.20,(0,5-i*3.5,-.05),.1) for i in range(21)]
    m.cut('BackCover',grooves,'Rear grip groove array')
    door_grooves=[m.rr(74,.32,.15,(0,5-i*3.5,.13),.1) for i in range(21)]
    m.cut('BatteryDoor',door_grooves,'Battery cover grip groove array')
    sidecuts=[Part.makeBox(.3,.32,15.0,V(x,5-i*3.5-.16,1.4)) for x in [-45.1,44.8] for i in range(21)]
    m.cut('RearShell',sidecuts,'Rear grip side grooves')
    m.box('CartridgeLeftGuide','Cartridge guide rail',2.2,62,7.4,(-30.4,42,1.4),'CardReader',-4,'dmgcase',.5,True)
    m.box('CartridgeRightGuide','Cartridge guide rail',2.2,62,7.4,(30.4,42,1.4),'CardReader',-4,'dmgcase',.5,True)
    m.box('CartridgeStop','Cartridge lower stop',58,2.0,2.0,(0,11.2,2.0),'CardReader',-4,'dmgcase',.4,True)
    m.box('CartridgePowerLock','Power-linked cartridge retention tab',3.0,6.0,2.2,(-26,69,5.0),'CardReader',-4,'black',.4,True)
    m.checkpoint(5,'rear_cartridge_bay_battery_door_and_fasteners','建立后部卡带入口、滑动导轨、电池盖与卡扣、六枚三角槽机壳螺钉、安装柱和后壳横向防滑纹。')


def stage06(m):
    # Orient the side receptacle's long dimension along Y and its short one along Z.
    from .geometry import rotation
    right=rotation((1,0,0),(0,0,1))
    outer=m.rr(12.4,4.8,5.5,(39.4,42,8.5),.8,right)
    inner=m.rr(10.4,2.8,6,(39.2,42,8.5),.35,right)
    _replace(m,'LinkPortShell',outer.cut(inner))
    _replace(m,'LinkPortTongue',m.rr(8.4,.6,4.3,(40.4,42,8.5),.15,right))
    for i in range(6):_replace(m,'LinkPin'+str(i),m.rr(.55,.10,3.2,(41.1,38.25+i*1.5,8.9),.02,right))
    next(o for o in m.doc.Objects if o.Label.startswith('Game Link side opening · tool')).Shape=m.rr(12.8,5.2,6,(39.2,42,8.5),.9,right)
    tray=m.rr(70,62,15.5,(0,-40,1.4),3.0).cut(m.rr(67,59,15.0,(0,-40,1.2),1.5))
    m.feature('BatteryTray','Four-AA cell compartment',tray,'Battery',-4,'dmgcase',True)
    for x in [-16,0,16]:m.box('BatterySeparator'+str(x),'Battery separator rib',.65,56,3.0,(x,-40,13.15),'Battery',-4,'dmgcase',.25,True)
    for i,x in enumerate([-24,-8,8,24]):
        axis=V(0,1 if i%2==0 else -1,0);origin=V(x,-65.25 if i%2==0 else -14.75,8.75)
        # The wrapper is an annulus around a separate metal cell, with end caps.
        tube=Part.makeCylinder(7.15,48.8,origin+axis*.8,axis).cut(Part.makeCylinder(6.95,49.1,origin+axis*.65,axis))
        m.feature('AAWrapper'+str(i),'AA cell outer sleeve study',tube,'Battery',-4,'rubber',True)
        m.cyl('AACell'+str(i),'AA cell metal can',6.88,49.0,tuple(origin+axis*.7),'Battery',-4,'metal',axis=tuple(axis),internal=True)
        m.cyl('AANegative'+str(i),'AA negative end cap',6.9,.45,tuple(origin+axis*.15),'Battery',-4,'metal',axis=tuple(axis),internal=True)
        m.cyl('AAPositive'+str(i),'AA positive terminal',2.5,.55,tuple(origin+axis*49.8),'Battery',-4,'gold',axis=tuple(axis),internal=True)
        # Separate spring and leaf contacts, placed outside the 50.5 mm nominal cell.
        spring_y=-67.5 if i%2==0 else -12.5
        helix=Part.makeHelix(.6,1.8,2.7)
        circle=Part.Wire(Part.makeCircle(.16,helix.Vertexes[0].Point,helix.Edges[0].tangentAt(helix.Edges[0].FirstParameter)))
        spring=Part.Wire(helix.Edges).makePipeShell([circle],True,False)
        spring.Placement=App.Placement(V(x,spring_y,8.75),App.Rotation(V(0,0,1),V(0,1 if i%2==0 else -1,0)))
        m.feature('AAContactSpring'+str(i),'Battery helical contact spring',spring,'Battery',-4,'metal',True)
        leaf_y=-13.5 if i%2==0 else -66.5
        m.box('AAContactLeaf'+str(i),'Battery leaf contact',6.5,.35,8.0,(x,leaf_y,4.6),'Battery',-4,'metal',.1,True)
        # Rear-facing generic markings are solid glyphs, not branded cell artwork.
        m.label('AAMark'+str(i),'AA',2.4,(x+1.8,-41,1.55),'Battery',-4,'white',rotation=App.Rotation(V(0,1,0),180))
    m.checkpoint(6,'four_aa_cells_and_battery_contacts','建立四节 AA 电池的独立外套、金属筒、正负极与触点，并补充电池仓隔条；不加入现代锂电改装件。')

STAGES.update({4:stage04,5:stage05,6:stage06})


def stage07(m):
    # DMG main PCB sits in the upper rear half; the front board also carries controls.
    m.box('Mainboard','DMG main logic PCB study',79,80,.8,(0,31,12.8),'Mainboard',-2,'pcb',2.0,True)
    front=_outline(m,81,127,3.5,15,23.0,.65)
    front=front.cut(Part.makeCylinder(13.1,1.0,V(27,-55,22.8)))
    m.feature('FrontPCB','LCD and button circuit board',front,'ControlsInternal',1,'pcb',True)
    from .geometry import rotation
    side=rotation((1,0,0),(0,0,1))
    m.box('PowerPCB','Vertical DC power daughterboard',55,8,.65,(-40.5,-39,8),'Power',-3,'pcb',.45,True,orient=side)
    m.box('HeadphonePCB','Separate headphone jack board',29,9,.6,(-3,-68.5,17.5),'Audio',-3,'pcb',.7,True)
    socket=m.rr(60,13,6.5,(0,4,5.4),1.3).cut(m.rr(52,9,2.0,(0,6.2,7.7),.4))
    m.feature('CartridgeSocket','32-contact cartridge connector housing',socket,'CardReader',-3,'black',True)
    for i in range(32):
        x=-23.25+i*1.5
        m.box('CartContact'+str(i),'Cartridge connector spring contact study',.7,6,.12,(x,6.1,9.9),'CardReader',-3,'gold',.05,True)
        m.box('CartSolderTail'+str(i),'Cartridge connector solder tail',.65,2.4,.12,(x,-2.4,12.5),'CardReader',-2,'metal',.04,True)
    # Front-board socket and a wide interconnect ribbon bridge the two case halves.
    m.box('BoardLinkSocket','Front/rear board ribbon connector',28,4.6,1.8,(0,57,20.8),'Flex',1,'white',.6,True)
    m.box('BoardLinkContactBar','Ribbon connector contact strip',25,1.2,.12,(0,57,20.55),'Flex',1,'gold',.1,True)
    m.box('BoardRibbon','Front/rear board ribbon study',25,15,.13,(0,59,17.2),'Flex',0,'copper',.6,True)
    for x in [-36,36]:
        for y in [-7,64]:
            m.cut('Mainboard',Part.makeCylinder(1.05,1.2,V(x,y,12.6)),'Mainboard screw clearance')
            m.ring(f'MainboardBoss{x}_{y}','Mainboard mounting spacer',2.4,1.05,3.0,(x,y,9.5),'Internal',-3,'dmgcase',internal=True)
            m.screw(f'MainboardScrew{x}_{y}',(x,y,14.2),'Mainboard',-2,length=4.2,radius=1.7,axis=(0,0,-1))
    m.checkpoint(7,'separate_logic_display_power_and_audio_boards','建立上部主板、整块显示/按键板、侧立电源板与底部耳机小板，并加入 32 接点卡座、板间排线和主板固定件。')


def _smd(m,key,x,y,z,w=.95,h=.65,t=.45,assembly='Mainboard',layer=-2):
    m.box(key,'SMD passive body study',w,h,t,(x,y,z),assembly,layer,'rubber',.03,True)
    ends=[m.rr(.20,h+.04,t+.02,(x+side*(w/2+.12),y,z-.01),.02) for side in [-1,1]]
    m.feature(key+'Ends','SMD solder terminations',Part.makeCompound(ends),assembly,layer,'metal',True)


def _package(m,key,label,x,y,z,w,h,t,pins,quad=False):
    m.box(key,label,w,h,t,(x,y,z),'Mainboard',-2,'black',.30,True)
    frames=[]
    if quad:
        n=pins//4
        for side in [-1,1]:
            for i in range(n):
                yy=y+(i-(n-1)/2)*(h-2)/(n-1)
                frames.append(m.rr(1.75,.38,.22,(x+side*(w/2+.925),yy,12.4),.02))
                xx=x+(i-(n-1)/2)*(w-2)/(n-1)
                frames.append(m.rr(.38,1.75,.22,(xx,y+side*(h/2+.925),12.4),.02))
    else:
        n=pins//2
        for side in [-1,1]:
            for i in range(n):
                xx=x+(i-(n-1)/2)*(w-1.7)/(n-1)
                frames.append(m.rr(.38,1.55,.22,(xx,y+side*(h/2+.825),12.4),.02))
    m.feature(key+'Leadframe','IC leadframe geometry study',Part.makeCompound(frames),'Mainboard',-2,'metal',True)


def stage08(m):
    _package(m,'CPU','DMG CPU / LR35902 package study',-9,45,10.6,22,20,2.0,80,True)
    _package(m,'VRAM','8 KB video RAM package study',22,47,11.1,12,21,1.5,28)
    _package(m,'WRAM','8 KB work RAM package study',9,24,11.1,22,11,1.5,28)
    _package(m,'Amplifier','IR3R40 audio amplifier package study',28,16.5,11.3,9,7,1.3,18)
    reverse=App.Rotation(V(0,1,0),180)
    for key,txt,size,x,y,z in [('CPUText','DMG CPU',2.5,-1,44,10.58),('VRAMText','VRAM',1.6,25,46,11.08),('WRAMText','WRAM',1.7,14,23,11.08),('AmpText','AMP',1.2,30,16,11.28)]:m.label(key,txt,size,(x,y,z),'Mainboard',-2,'white',rotation=reverse)
    m.box('Crystal','4.194304 MHz crystal can study',4.5,10,2.0,(-29,34,10.6),'Mainboard',-2,'metal',1.2,True)
    m.label('ClockMark','4.19',1.4,(-27,33,10.58),'Mainboard',-2,'black',rotation=reverse)
    for i,(x,y) in enumerate([(-33,63),(34,31),(33,12)]):
        m.cyl('MainCap'+str(i),'Electrolytic capacitor body',2.7,4.0,(x,y,8.5),'Mainboard',-2,'black',internal=True)
        m.cyl('MainCapTop'+str(i),'Capacitor aluminum end',2.45,.10,(x,y,8.34),'Mainboard',-2,'metal',internal=True)
    positions=[(-31,y) for y in [16,23,45,53]]+[(-23,y) for y in [17,25,60,66]]+[(x,64) for x in [-15,-7,3,12,21,29]]+[(34,y) for y in [38,46,54,62]]+[(x,14) for x in [-15,-8,0,8,16]]+[(x,33) for x in [8,16,25]]
    for i,(x,y) in enumerate(positions):_smd(m,'MainPassive'+str(i),x,y,12.0)
    # Thin copper foil on the front of the rear PCB follows the photographic layout.
    shield=m.rr(61,42,.12,(-2,27,13.8),2.0)
    for x,y,r in [(-27,11,3.0),(25,11,3.0),(-27,43,2.8),(25,43,2.8)]:shield=shield.cut(Part.makeCylinder(r,.4,V(x,y,13.65)))
    m.feature('MainboardCopperFoil','Mainboard copper shield foil study',shield,'Mainboard',-1,'copper',True)
    m.box('PowerInductor','Power-board inductor block',2.8,7.0,4.4,(-37.9,-43,5.8),'Power',-3,'black',.4,True)
    for i,y in enumerate([-55,-31,-22]):m.cyl('PowerCap'+str(i),'Power-board capacitor study',1.5,2.4,(-39.6,y,7.8),'Power',-3,'metal',axis=(1,0,0),internal=True)
    m.box('PowerRegulator','Power-board regulator package study',2.6,5,2.3,(-38.0,-14,7.2),'Power',-3,'black',.3,True)
    m.checkpoint(8,'dmg_cpu_ram_amplifier_and_power_components','补齐 DMG CPU、两块 8KB RAM、音频放大器、晶振、无源件、电源器件与主板铜箔罩；引脚保持独立材质但不定义真实电路。')

STAGES.update({7:stage07,8:stage08})


def stage09(m):
    m.colors['dmgmembrane']=(.35,.66,.53)
    # Correct the long-axis lead rows of the vertical video-RAM package.
    pins=[m.rr(1.55,.38,.22,(22+side*6.825,47+(i-6.5)*19.3/13,12.4),.02) for side in [-1,1] for i in range(14)]
    _replace(m,'VRAMLeadframe',Part.makeCompound(pins))
    for i in range(32):_move(m,'CartContact'+str(i),(0,0,-.35))
    dpos=[(-26,-20),(-20,-26),(-26,-32),(-32,-26)]
    membrane=m.rr(21,4,.45,(-26,-26,24.15),1.2).fuse(m.rr(4,21,.45,(-26,-26,24.15),1.2))
    for x,y in dpos:
        dome=Part.makeCylinder(4.1,2.75,V(x,y,24.15)).cut(Part.makeCylinder(3.3,2.4,V(x,y,24.05)))
        membrane=membrane.fuse(dome)
    m.feature('DPadMembrane','Connected four-direction silicone membrane',membrane.removeSplitter(),'ControlsInternal',2,'dmgmembrane',True)
    m.cyl('DPadCarrier','Directional-pad carrier',9.0,.4,(-26,-26,27.75),'ControlsInternal',3,'black',internal=True)
    action=m.rr(20,3.5,.45,(25.5,-23.5,24.15),1.1);action.rotate(V(25.5,-23.5,0),V(0,0,1),25)
    for x,y in [(33,-20),(18,-27)]:
        dome=Part.makeCylinder(5.0,2.85,V(x,y,24.15)).cut(Part.makeCylinder(3.4,2.35,V(x,y,24.05)))
        action=action.fuse(dome)
    m.feature('ActionMembrane','Joined A/B silicone membrane',action.removeSplitter(),'ControlsInternal',2,'dmgmembrane',True)
    for i,(x,y) in enumerate(dpos+[(33,-20),(18,-27)]):
        m.cyl('KeyContact'+str(i),'Gold button contact',2.6,.06,(x,y,23.75),'ControlsInternal',1,'gold',internal=True)
        m.cyl('KeyPill'+str(i),'Conducting carbon pill',1.7,.12,(x,y,24.0),'ControlsInternal',2,'black',internal=True)
        m.cyl('KeyBoss'+str(i),'Silicone transmission boss',1.1,.6 if i<4 else .45,(x,y,27.0),'ControlsInternal',3,'dmgmembrane',internal=True)
    for i,x in enumerate([-12,4]):
        m.cyl('SystemContact'+str(i),'Start/Select contact',2.0,.06,(x,-48,23.75),'ControlsInternal',1,'gold',internal=True)
        m.cyl('SystemPill'+str(i),'Start/Select conducting pill',1.2,.12,(x,-48,24.0),'ControlsInternal',2,'black',internal=True)
        m.box('SystemRubber'+str(i),'Start/Select silicone base',3.5,3.5,1.8,(x,-48,24.3),'ControlsInternal',2,'dmgmembrane',.8,True)
        m.cyl('SystemStem'+str(i),'Start/Select plunger',1.2,4.2,(x,-48,26.25),'ControlsInternal',3,'rubber',internal=True)
    frame=m.rr(61,55,.9,(0,35.8,24.0),1.2).cut(m.rr(57,51,1.2,(0,35.8,23.8),.6))
    for x in [-32,32]:
        for y in [13.8,57.8]:frame=frame.fuse(Part.makeCylinder(2.4,.9,V(x,y,24)))
    frame=frame.cut(m.rr(43,5,1.3,(0,8.5,23.8),.2))
    m.feature('LCDSupportFrame','LCD clip frame with four fixing ears',frame.removeSplitter(),'Display',1,'white',True)
    for i,(x,y) in enumerate([(x,y) for x in [-32,32] for y in [13.8,57.8]]):
        tool=Part.makeCylinder(1.05,3,V(x,y,22.8))
        for key in ['LCDSupportFrame','FrontPCB']:m.cut(key,tool,'LCD frame fixing hole')
        m.screw('LCDScrew'+str(i),(x,y,25.6),'Display',1,length=3.8,radius=1.6,axis=(0,0,-1))
    m.box('LCDDisplayFlex','Soldered LCD flexible connection study',40,8,.12,(0,9,24.15),'Flex',1,'copper',.35,True)
    m.box('LCDDriver','LCD driver package study',14,7,1.2,(0,1,24.0),'Display',1,'black',.4,True)
    m.ring('SpeakerFrame','Circular speaker frame',12.2,10.7,3.0,(27,-55,24.5),'Audio',2,'metal',internal=True)
    m.cyl('SpeakerBack','Speaker backing disc',12.2,.2,(27,-55,24.1),'Audio',2,'metal',internal=True)
    m.cyl('SpeakerMagnet','Speaker magnet',6.0,2.4,(27,-55,24.8),'Audio',2,'black',internal=True)
    m.cyl('SpeakerDiaphragm','Speaker diaphragm',10.5,.12,(27,-55,27.65),'Audio',3,'rubber',internal=True)
    for i,x in enumerate([18,21]):
        m.box('SpeakerWire'+str(i),'Soldered speaker lead study',.6,11,.12,(x,-44,22.2),'Audio',1,'gold',.2,True)
        m.cyl('SpeakerSolder'+str(i),'Speaker solder pad',.7,.12,(x,-38.4,22.5),'Audio',1,'metal',internal=True)
    m.checkpoint(9,'silicone_controls_lcd_frame_and_speaker','加入成组按键胶垫、导电粒和传动柱、LCD 卡框与固定螺钉、焊接排线和圆形扬声器，并调整卡座触点与纵向 RAM 引脚布局。')


def stage10(m):
    # The display PCB has ten service screws, in addition to the separate LCD clips.
    points=[(-36,60),(36,60),(-36,42),(36,42),(-36,8),(36,8),(-36,-27),(36,-39),(-19,-60),(10,-58)]
    for i,(x,y) in enumerate(points):
        m.cut('FrontPCB',Part.makeCylinder(.85,1.1,V(x,y,22.8)),'Display PCB service-screw hole')
        m.screw('FrontBoardScrew'+str(i),(x,y,22.55),'ControlsInternal',1,length=4.8,radius=1.45)
        m.ring('FrontBoardBoss'+str(i),'Front case board mounting boss',2.0,.85,5.5,(x,y,24.0),'Internal',2,'dmgcase',internal=True)
    for key,host in [('ContrastPot','MainFrame'),('VolumePot','RearShell')]:m.cut(host,m.parts[key].Shape,'Potentiometer body mounting relief')
    m.cut('FrontPCB',m.parts['ContrastPot'].Shape,'Contrast potentiometer board notch')
    m.cut('Mainboard',m.parts['VolumePot'].Shape,'Volume potentiometer board notch')
    # LCD-board rear components sit above the battery tray and mainboard shielding.
    for i,(x,y) in enumerate([(-25,13),(27,16),(-24,-10),(20,-7),(-16,-47),(11,-36)]):
        m.cyl('FrontCap'+str(i),'Display-board capacitor study',1.7,2.2,(x,y,20.5),'ControlsInternal',0,'black',internal=True)
        m.cyl('FrontCapEnd'+str(i),'Capacitor end cap',1.55,.08,(x,y,20.35),'ControlsInternal',0,'metal',internal=True)
    for i,(x,y) in enumerate([(-31,2),(-22,2),(-10,3),(10,3),(28,-11),(27,-37),(-9,-57),(10,-47)]):_smd(m,'FrontPassive'+str(i),x,y,22.4,assembly='ControlsInternal',layer=0)
    m.box('DisplayAmplifier','LCD-board control package study',9,9,1.3,(3,21,21.3),'ControlsInternal',0,'black',.3,True)
    # Routed power/jack bundles are separate conductors rather than board geometry.
    for i in range(3):
        m.cyl('PowerWireUpper'+str(i),'Power board upper lead study',.28,6.5,(-38+i*.8,-11.5,12.3),'Flex',-2,'black',axis=(0,1,0),internal=True)
        m.box('PowerWireLower'+str(i),'Power-to-jack wire study',22,.55,.30,(-24,-69.0+i*.8,16.9),'Flex',-2,'black',.14,True)
    m.box('HeadphoneSwitch','Headphone insertion switch study',5.0,4.0,1.8,(7,-69.0,14.8),'Audio',-3,'black',.4,True)
    m.cut('PowerSlider',m.parts['PowerSwitchLink'].Shape,'Power slider transmission recess')
    m.cut('MainFrame',m.parts['PowerSwitchLink'].Shape,'Power linkage passage')
    m.checkpoint(10,'pcb_service_mounts_and_interconnects','补齐显示板十处维修螺钉、前壳安装柱、背面电子件、电源与耳机走线，并为滚轮电位器和电源传动件增加安装让位。')

STAGES.update({9:stage09,10:stage10})


def stage11(m):
    # An unbranded cartridge accompanies the handheld; it is not a game ROM release.
    cx,cy=106,22
    m.native('CartridgeBack','Game Pak rear shell study',57,65,2.0,1.0,(cx,cy,0),'Accessories',-2,'dmgcase')
    m.native('CartridgeWall','Game Pak perimeter shell',57,65,2.0,5.6,(cx,cy,1.1),'Accessories',0,'dmgcase')
    m.cut('CartridgeWall',m.rr(54,62,6,(cx,cy,1),.8),'Cartridge electronics cavity')
    m.native('CartridgeFront','Game Pak front shell',57,65,2.0,1.1,(cx,cy,6.8),'Accessories',3,'dmgcase')
    window=m.rr(51,10,8.3,(cx,-5.4,-.1),.5)
    for key in ['CartridgeBack','CartridgeWall','CartridgeFront']:m.cut(key,window,'Cartridge connector-edge opening')
    m.box('CartridgePCB','Cartridge PCB study',51,58,.8,(cx,23,3.3),'Accessories',1,'pcb',.6,True)
    for i in range(32):m.box('GamePakPad'+str(i),'Game Pak edge contact',1.0,4.6,.06,(cx-23.25+i*1.5,-3.5,4.2),'Accessories',1,'gold',.04,True)
    m.box('CartridgeROM','ROM package placeholder',18,9,1.4,(cx,23,4.55),'Accessories',2,'black',.3,True)
    leadframe=[m.rr(.45,1.4,.15,(cx+(i-6.5)*1.13,23+side*5.25,4.42),.03) for side in [-1,1] for i in range(14)]
    m.feature('CartridgeROMLeads','ROM package leadframe study',Part.makeCompound(leadframe),'Accessories',1,'metal',True)
    m.box('CartridgeLabel','Blank study-cartridge label',45,42,.10,(cx,22,7.9),'Accessories',4,'white',1.3)
    for key,txt,size,x,y in [('CartridgeTitle','GAME PAK',3.7,cx-15,31),('CartridgeCaption','DMG STUDY',2.5,cx-12,20),('CartridgeNotice','NO GAME DATA',2.0,cx-13,10)]:
        m.label(key,txt,size,(x,y,7.982),'Accessories',4,'dmgink');m.cut('CartridgeLabel',m.parts[key].Shape,'Cartridge printed label inset')
    grip=[m.rr(.65,7,.2,(cx-24+i*3,50,7.75),.2) for i in range(17)]
    m.cut('CartridgeFront',grip,'Cartridge finger-grip ribbing')
    m.cut('CartridgeBack',[Part.makeCylinder(.85,1.4,V(cx,5,-.1)),Part.makeCylinder(1.8,.7,V(cx,5,-.1))],'Cartridge rear screw seat')
    m.cut('CartridgePCB',Part.makeCylinder(.85,1.2,V(cx,5,3.1)),'Cartridge screw passage')
    m.screw('CartridgeScrew',(cx,5,.12),'Accessories',-2,length=3.7,radius=1.6)
    m.profile['internal_exclude']=['FrontFace','DisplayBezel','DisplayGlass','LCD','LCDPolarizer','LCDBackplate','NintendoFrontWord','GameBoyFrontWord','PowerMark','BatteryLED','BatteryLEDMark','DisplayTechnologyMark']+[k for k in m.parts if k.startswith(('DisplayRedLine','DisplayBlueLine','ButtonMark','StartMark','SelectMark'))]
    m.profile['internal_normal']=[.2,-.3,2]
    m.checkpoint(11,'blank_game_pak_cartridge','建立独立空白 Game Pak 卡带的分壳、PCB、32 接点、ROM 封装示意、指握纹与螺钉，标识为学习模型而不包含游戏数据。')

STAGES[11]=stage11


def stage12(m):
    # Refit the battery tray to the actual asymmetric enclosure, then add service seats.
    _replace(m,'BatteryTray',m.parts['BatteryTray'].Shape.common(_outline(m,86.6,144.6,5.3,18.3,1.0,16.5)))
    for key in ['BackCover','RearShell','BatteryTray']:
        m.cut(key,m.parts['BatteryDoor'].Shape,'Battery-cover latch and tongue seats')
    m.cut('BatteryTray',Part.makeCylinder(2.8,6.5,V(0,-68.3,9.3),V(0,-1,0)),'Headphone passage below battery cells')
    for i in [4,5]:
        x=-34 if i==4 else 34;y=-66
        _move(m,'CaseScrew'+str(i),(0,0,1.2))
        m.cut('CaseBoss'+str(i),Part.makeCylinder(1.9,.8,V(x,y,1.2)),'Recessed battery-bay screw head')
        m.cut('BatteryTray',Part.makeCylinder(3.05,8.5,V(x,y,1.1)),'Battery-tray case-boss clearance')
    for key,x in [('CartridgeLeftGuide',-30.4),('CartridgeRightGuide',30.4)]:_replace(m,key,m.rr(2.2,61,7.4,(x,41.5,1.4),.5))
    for i,(x,y) in enumerate([(-28,63),(34,31),(35,4)]):
        _replace(m,'MainCap'+str(i),Part.makeCylinder(2.7,3.2,V(x,y,9.4)))
        _replace(m,'MainCapTop'+str(i),Part.makeCylinder(2.45,.10,V(x,y,9.24)))
    for key in ['MainPassive17','MainPassive17Ends']:_move(m,key,(-3,0,0))
    _replace(m,'HeadphonePCB',m.rr(29,8,.6,(-3,-68.2,17.5),.7))
    _move(m,'HeadphoneSwitch',(0,0,3.5))
    holes=[o for o in m.doc.Objects if o.Label.startswith('Display PCB service-screw hole · tool')]
    fixes=[(6,(-36,-39),(0,-12,0)),(7,(36,-36),(0,3,0)),(9,(4,-58),(-6,0,0))]
    for index,(x,y),delta in fixes:
        for prefix in ['FrontBoardScrew','FrontBoardBoss']:_move(m,prefix+str(index),delta)
        holes[index].Shape=Part.makeCylinder(.85,1.1,V(x,y,22.8))
    for i in range(3):
        x,y=-32+i*.8,-12-i*.8;z=12.3
        a,b,c,d=V(-39.4,y,z),V(x-1,y,z),V(x,y+1,z),V(x,-5,z)
        path=Part.Wire([Part.makeLine(a,b),Part.Arc(b,V(x-.292893218,y+.292893218,z),c).toShape(),Part.makeLine(c,d)])
        wire=Part.Wire(Part.makeCircle(.28,a,V(1,0,0)))
        _replace(m,'PowerWireUpper'+str(i),path.makePipeShell([wire],True,False))
    m.profile['internal_exclude']=['BackCover','RearShell','BatteryDoor','RearModel','RearNintendo','RearRating','RearStudy']+['CaseScrew'+str(i) for i in range(6)]
    m.profile['internal_normal']=[.2,-.3,-2]
    m.doc.recompute();m.profile['stages']=12
    m.checkpoint(12,'verified_service_and_electronics_clearances','根据实体求交修正电池盖卡扣、仓内螺钉、圆角电池托盘、耳机通道、安装柱、电容与走线，并从后侧展示主要内部结构。')

STAGES[12]=stage12


def stage13(m):
    passages=[Part.makeCylinder(.38,3.0,V(-35.6,-12-i*.8,12.3),V(1,0,0)) for i in range(3)]
    m.cut('BatteryTray',passages,'Power harness passage through battery-tray wall')
    m.profile['stages']=13
    m.checkpoint(13,'power_harness_tray_passages','为电源线束增加电池托盘侧壁穿线孔，提供侧向装配间隙并保留可追溯的独立线束。')

STAGES[13]=stage13


def stage14(m):
    # The empty cartridge recess must reveal its plastic backing, not exposed logic ICs.
    m.box('CartridgeWellBacker','Cartridge-well internal backing',59.2,27.6,.35,(0,60.1,8.9),'CardReader',-4,'dmgcase',.7,True)
    m.cut('RearShell',m.parts['CartridgeWellBacker'].Shape,'Cartridge backing upper-edge seat')
    _replace(m,'MainCapTop0',Part.makeCylinder(2.45,.10,V(-28,63,9.28)))
    m.cut('BackCover',m.rr(12,7,1.6,(0,-7,-.1),1.0),'Battery latch thumb recess')
    m.profile['internal_exclude'].append('CartridgeWellBacker')
    m.profile['stages']=14
    m.checkpoint(14,'cartridge_backing_and_battery_latch_detail','补齐空卡槽的内侧塑料背板，避免从外部直接看到芯片，并加入电池盖拇指释放凹口，完成后部外观修正。')

STAGES[14]=stage14



def stage15(m):
    passages=[Part.makeCylinder(.38,3.0,V(-32+i*.8,-11,12.3),V(0,1,0)) for i in range(3)]
    m.cut('BatteryTray',passages,'Power harness exit through upper battery-tray wall')
    m.profile['stages']=15
    m.checkpoint(15,'power_harness_upper_exit','为转弯后的三根电源线增加托盘上壁出口，与侧壁穿线孔组成完整的线束通路。')

STAGES[15]=stage15


def _repair_stage16_legacy_shapes(m):
    """Repair legacy topology without asserting equivalence of defective sweeps."""
    from .handheld_refinement import replace
    records = []
    for key in ['BatteryLEDMark', 'VRAMText', 'WRAMText']:
        before = m.parts[key].Shape.copy()
        after = before.Solids[0].multiFuse(before.Solids[1:]).removeSplitter()
        after.check(True)
        differences = [before.cut(after), after.cut(before)]
        volumes = [0.0 if x.isNull() else sum(abs(s.Volume) for s in x.Solids)
                   for x in differences]
        assert all(x.isNull() or x.isValid() for x in differences)
        assert max(volumes) < 1e-6, (key, volumes)
        replace(m, key, after, 'Unite intersecting glyphs with empty bidirectional material difference')
        records.append({'part_id': key, 'method': 'glyph union',
                        'removed_added_mm3': volumes, 'material_equivalent': True})
    # Retain the original radius2.7, pitch0.6, height1.8 and wire radius0.16mm.
    # Split the sweep at spline knots so no single face spans an internal C0 seam.
    edge = Part.makeHelix(.6, 1.8, 2.7).Edges[0]
    curve = edge.Curve
    knots = [edge.FirstParameter] + [k for k in curve.getKnots()
            if edge.FirstParameter+1e-9 < k < edge.LastParameter-1e-9] + [edge.LastParameter]
    edges = [curve.toShape(a, b) for a, b in zip(knots, knots[1:])]
    circle = Part.Wire(Part.makeCircle(.16, edges[0].Vertexes[0].Point,
                                      edges[0].tangentAt(edges[0].FirstParameter)))
    spring = Part.Wire(edges).makePipeShell([circle], True, False)
    spring.check(True)
    for i in range(4):
        key = 'AAContactSpring'+str(i)
        before = m.parts[key].Shape.copy()
        after = spring.copy()
        after.Placement = before.Placement
        after.check(True)
        replace(m, key, after, 'Original spring parameters with segmented sweep; legacy C0 equivalence unproven')
        records.append({'part_id': key, 'method': 'segmented helix sweep',
                        'radius_pitch_height_wire_radius_mm': [2.7, .6, 1.8, .16],
                        'material_equivalent': None,
                        'limitation': 'Legacy C0 Boolean comparison is unreliable; nominal parameters retained, no exact material-equivalence claim'})
    m.doc.recompute()
    return records


def stage16(m):
    """Photo-calibrate the original exterior and correct documented interfaces.

    Exterior positions, slot dimensions and cap geometry are fitted to
    first-hand DMG photographs. Connector row topology and the nominal power
    plug dimensions have independent documented references.
    """
    from .geometry import rotation
    from .handheld_refinement import replace

    def tool(label, host=None):
        found = [o for o in m.doc.Objects
                 if o.Label.startswith(label+' · tool')
                 and (host is None or o.Name.startswith(host))]
        assert len(found) == 1, (label, host, len(found))
        return found[0]

    right = rotation((1, 0, 0), (0, 0, 1))
    left = rotation((-1, 0, 0), (0, 0, 1))

    # The photographed DC jack is about 21 mm nearer the top than the contrast
    # wheel. The earlier model incorrectly put both at the same Y coordinate.
    for key in ['ContrastWheel', 'ContrastSpindle', 'ContrastPot']:
        _move(m, key, (0, -6.5, -1.8))
    for key in ['DCJack', 'DCJackContact']:
        _move(m, key, (0, 14.5, 2.4))
    contrast_cavity = Part.makeCylinder(5.38, 1.9, V(-39.8, 28.5, 18.75))
    contrast_mouth = m.rr(11.2, 2.0, 4.0, (-42, 28.5, 19.675), .45, left)
    tool('Contrast thumbwheel clearance').Shape = contrast_cavity.fuse(contrast_mouth)
    tool('DC adapter inlet').Shape = Part.makeCylinder(2.75, 6, V(-39.2, 49.5, 11.0), V(-1, 0, 0))
    tool('Potentiometer body mounting relief', 'MainFrame').Shape = m.parts['ContrastPot'].Shape.copy()
    tool('Contrast potentiometer board notch').Shape = m.parts['ContrastPot'].Shape.copy()
    # 3.5 mm is the mating plug diameter. The extra 0.1 mm is an explicitly
    # estimated model clearance, not a measured production socket tolerance.
    m.cut('DCJack', Part.makeCylinder(1.8, 6, V(-39.4, 49.5, 11.0), V(-1, 0, 0)),
          'Clearance for documented 3.5 mm DMG power plug').Refine = False

    # The volume thumbwheel is visibly thicker than the contrast thumbwheel.
    # Retain its photographed position and rebuild the associated openings.
    wheel = Part.makeCylinder(5.2, 3.0, V(39.8, 19, 11.975))
    teeth = [Part.makeCylinder(.19, 3.3,
             V(39.8+5.12*math.cos(2*math.pi*i/40),
               19+5.12*math.sin(2*math.pi*i/40), 11.825)) for i in range(40)]
    wheel = wheel.cut(Part.makeCompound(teeth)).cut(Part.makeCylinder(.95, 3.4, V(39.8, 19, 11.8)))
    replace(m, 'VolumeWheel', wheel, 'Photo-fitted 3 mm volume wheel; contrast wheel retains its thin profile')
    _move(m, 'VolumePot', (0, 0, 2.725))
    replace(m, 'VolumeSpindle', Part.makeCylinder(.8, 3.725, V(39.8, 19, 11.5)),
            'Spindle follows the thicker volume wheel and relocated pot body')
    volume_cavity = Part.makeCylinder(5.38, 3.4, V(39.8, 19, 11.775))
    volume_mouth = m.rr(11.2, 3.4, 4.0, (42, 19, 13.475), .45, right)
    tool('Volume thumbwheel clearance').Shape = volume_cavity.fuse(volume_mouth)
    tool('Potentiometer body mounting relief', 'RearShell').Shape = m.parts['VolumePot'].Shape.copy()
    tool('Volume potentiometer board notch').Shape = Part.makeCompound([
        m.parts['VolumePot'].Shape, Part.makeCylinder(5.4, 2.4, V(39.8, 19, 12.6))])

    def keyed_section(w, h, depth, origin, corner):
        points = [(-w/2, h/2), (w/2, h/2), (w/2, -h/2+corner),
                  (w/2-corner, -h/2), (-w/2+corner, -h/2), (-w/2, -h/2+corner)]
        shape = _polygon(points, 0, depth)
        shape.Placement = App.Placement(V(*origin), right)
        return shape

    # Original large Game Link has chamfered lower corners and two rows of
    # three contacts; it is not a six-contact single-row socket.
    outer = keyed_section(14.0, 6.4, 5.5, (39.4, 42, 11.0), 1.2)
    inner = keyed_section(13.3, 5.7, 6.0, (39.2, 42, 11.0), 1.0)
    replace(m, 'LinkPortShell', outer.cut(inner), 'Photographed keyed large Game Link shell; local wall thickness fitted')
    tool('Game Link side opening').Shape = keyed_section(14.4, 6.8, 6.0, (39.2, 42, 11.0), 1.25)
    replace(m, 'LinkPortTongue', m.rr(9.6, .85, 4.3, (40.4, 42, 11.0), .15, right),
            'Photo-fitted large connector tongue within the chamfered shield')
    for i in range(6):
        row, column = divmod(i, 3)
        z = 11.55 if row == 0 else 10.45
        replace(m, 'LinkPin'+str(i), m.rr(.55, .10, 3.2, (41.1, 39.5+column*2.5, z), .02, right),
                'Documented 2-by-3 Game Link topology; contact positions are fitted')
    m.doc.recompute()
    m.cut('MainFrame', m.parts['VolumePot'].Shape, 'Volume potentiometer clearance across the case split').Refine = False
    m.cut('Mainboard', Part.makeBox(7, 15, 2, V(39.1, 34.5, 12.4)),
          'Schematic board-edge clearance for the correctly elevated Game Link shell').Refine = False

    # Six molded grooves are visible, but only five pierce the original case.
    # The lowest/leftmost groove is blind, visible in both reference photographs.
    slots = []
    for i in range(6):
        x, y = 15.5+i*4.5, -63.5+i*2.6
        # Keep the long molded recess, then open a shorter narrow slit in five
        # of its floors. The dark opening is not the entire visible groove.
        groove = _rotate_shape(m.rr(2.1, 16.2, .5, (x, y, 30.45), 1.0), (x, y, 0), 23)
        if i:
            opening = m.rr(1.2, 12.4, 1.2, (x-.30, y, 29.4), .58)
            groove = groove.fuse(_rotate_shape(opening, (x, y, 0), 23)).removeSplitter()
        slots.append(groove)
    tool('Six diagonal speaker slots').Shape = Part.makeCompound(slots)
    m.doc.recompute()

    # Raised case arrows sit outside the original black D-pad.
    arrows = []
    for angle in [0, 90, 180, 270]:
        arrow = _polygon([(-26-.85, -13.9), (-26+.85, -13.9), (-26, -12.5)], 30.795, .065)
        arrow.rotate(V(-26, -26, 0), V(0, 0, 1), angle)
        arrows.append(arrow)
    replace(m, 'FrontFace', m.parts['FrontFace'].Shape.multiFuse(arrows).removeSplitter(),
            'Restore the four molded directional arrows and the photographed six-groove grille')

    # The original removable port cover is shown detached with the study cart.
    # The cover is photographed, but these local dimensions are fitted.
    cb = m.parts['CartridgeBack'].Shape.optimalBoundingBox(False, False)
    cx, cy = cb.Center.x, cb.YMin-12
    flange = m.rr(14.0, 6.4, .45, (cx, cy, .2), .75)
    plug = m.rr(10.8, 3.2, 2.7, (cx, cy, .6), .45)
    hollow = m.rr(9.4, 1.8, 2.8, (cx, cy, 1.05), .3)
    m.feature('LinkPortCover', 'Original removable Game Link cover study', flange.fuse(plug).cut(hollow),
              'Accessories', 0, 'dmgcase')

    # The optional original-style Game Pak uses an external six-lobe line head.
    sb = m.parts['CartridgeScrew'].Shape.optimalBoundingBox(False, False)
    center = V(sb.Center.x, sb.Center.y, sb.ZMin)
    head = Part.makeCylinder(1.8, .38, center)
    scallops = [Part.makeCylinder(.32, .6,
                center+V(1.8*math.cos(i*math.pi/3), 1.8*math.sin(i*math.pi/3), -.1)) for i in range(6)]
    screw = head.cut(Part.makeCompound(scallops)).fuse(Part.makeCylinder(.65, 3.7, center+V(0, 0, .36)))
    replace(m, 'CartridgeScrew', screw, 'Original-style 3.6 mm line-head family, commonly called 3.8 mm Gamebit; local drive profile fitted')
    m.cut('CartridgeBack', Part.makeCylinder(2.0, .72, V(center.x, center.y, -.02)),
          'Estimated service clearance around the line-head cartridge screw').Refine = False

    # Common molded markings follow the photographed case. Regulatory logos
    # and individual serial numbers are not inferred from a different region.
    from .geometry import appearance
    font = m.root/'references/DejaVuSans.ttf'

    def lettering(text, size, pos, orient=App.Rotation(), centered=False):
        faces = []
        for char in Part.makeWireString(text, str(font.parent)+'/', font.name, size):
            if char:
                faces.extend(Part.makeFace(char, 'Part::FaceMakerBullseye').Faces)
        solids = [face.extrude(V(0, 0, .018)) for face in faces]
        shape = solids[0].multiFuse(solids[1:]).removeSplitter()
        if centered:
            shape.translate(V(-shape.optimalBoundingBox(False, False).Center.x, 0, 0))
        shape.Placement = App.Placement(V(*pos), orient).multiply(shape.Placement)
        shape.check(True)
        return shape

    old_marks = ['RearModel', 'RearNintendo', 'RearRating', 'RearStudy']
    inlay_tools = [o for o in m.doc.Objects if o.Label.startswith('Rear information inlay · tool')]
    assert len(inlay_tools) == 4
    reverse = App.Rotation(V(0, 1, 0), 180)
    rows = [('RearModel', 'MODEL NO. DMG-01', 2.1, 29),
            ('RearNintendo', '©1989 Nintendo', 1.9, 25.3),
            ('RearRating', 'RATING: DC6V 0.7W', 2.0, 21.6),
            ('RearStudy', 'BATTERY: SUM-3(AA,R6)X4', 1.8, 17.9)]
    for key, text, size, y in rows:
        prior = m.parts[key].Shape.optimalBoundingBox(False, False)
        original_tool = min(inlay_tools, key=lambda o: abs(o.Shape.optimalBoundingBox(False, False).Center.y-prior.Center.y))
        new = replace(m, key, lettering(text, size, (20.5, y, .20), reverse),
                      'Restore common original rear-case wording; layout and lettering fitted')
        new.Label = text
        new.MaterialDescription = 'dmgcase'
        appearance(new, m.colors['dmgcase'])
        original_tool.Shape = new.Shape.copy()
        inlay_tools.remove(original_tool)
    m.feature('RearOrigin', 'MADE IN JAPAN', lettering('MADE IN JAPAN', 1.8, (20.5, 14.2, .20), reverse),
              'Body', -6, 'dmgcase')
    m.cut('BackCover', m.rr(46, 20, .22, (0, 22, -.02), .6),
          'Photo-fitted recessed rear identification panel').Refine = False

    m.cut('MainFrame', m.rr(17, 8.6, .3, (-45.1, 28.5, 22.7), 1, right),
          'Contrast thumbwheel molded recess and legend field').Refine = False
    m.cut('MainFrame', m.rr(13.3, 4.1, .3, (45.1, 19, 19), .9, left),
          'Volume molded legend field').Refine = False
    m.cut('MainFrame', m.rr(18, 3.8, .3, (45.1, 42, 18.9), .8, left),
          'Original EXT CONNECTOR molded legend field').Refine = False
    m.cut('RearShell', m.rr(22, 4.9, .3, (-45.1, 28.5, 14), .7, right),
          'Original external-power molded legend field').Refine = False
    for key, text, size, pos, orient, layer in [
        ('ContrastLegend', 'CONTRAST', 1.55, (-44.8, 28.5, 22.4), left, 0),
        ('VolumeLegend', 'VOL', 1.5, (44.8, 19, 18.1), right, 0),
        ('LinkLegend', 'EXT. CONNECTOR', 1.2, (44.8, 42, 18.2), right, 0),
    ]:
        m.feature(key, text, lettering(text, size, pos, orient, True), 'Body', layer, 'dmgcase')
    power_words = Part.makeCompound([
        lettering('USE ONLY DMG-03.-05', 1.05, (-44.8, 28.5, 14.4), left, True),
        lettering('DC 6V', 1.1, (-44.8, 28.5, 12.5), left, True)])
    power_words.check(True)
    m.feature('PowerSideLegend', 'Original external-power wording', power_words, 'Body', -6, 'dmgcase')
    m.profile['internal_exclude'].extend(k for k in ['RearOrigin', 'PowerSideLegend']
                                          if k not in m.profile['internal_exclude'])

    # The PHONES word, headphone pictogram and three bottom ribs are visible
    # on the original front face. Recess depth and stroke sizes are fitted.
    m.cut('FrontFace', m.rr(15.8, 3.3, .15, (0, -70.8, 30.69), 1.5),
          'Original front PHONES molded capsule').Refine = False
    word = lettering('PHONES', 1.4, (2.0, -71.4, 30.69), centered=True)
    arch = Part.makeCylinder(1.15, .018, V(-5, -70.9, 30.69)).cut(
           Part.makeCylinder(.85, .04, V(-5, -70.9, 30.68)))
    arch = arch.common(Part.makeBox(3, 1.3, .1, V(-6.5, -70.9, 30.65)))
    cups = [m.rr(.5, .9, .018, (-5+side*.95, -71.35, 30.69), .15) for side in [-1, 1]]
    icon = arch.multiFuse(cups).removeSplitter()
    m.feature('PhonesLegend', 'PHONES and headphone pictogram', Part.makeCompound([word, icon]), 'Body', 4, 'dmgcase')
    ribs = [m.rr(.5, 1.2, .06, (x, -73.2, 30.78), .15) for x in [-1, 0, 1]]
    replace(m, 'FrontFace', m.parts['FrontFace'].Shape.multiFuse(ribs).removeSplitter(),
            'Restore the three small molded ribs below PHONES')
    m.doc.recompute()
    m.profile['stages'] = 16
    m.strict_repairs = _repair_stage16_legacy_shapes(m)
    m.checkpoint(16, 'photo_calibrated_sides_grille_and_link',
        '按原机六面照片校准 DC/对比度/音量与通信口位置和轮廓，区分六条扬声器凹槽及五个窄通孔；补齐接口盖、壳体箭头与常见模压标记，移除非实机后盖字样，并校正卡带安全螺钉。局部尺寸、曲率和字形为照片拟合。')


STAGES[16] = stage16
