App.setActiveDocument(D.Name)
# Resolve the last repeated interface families from the stage-11 audit.
shift('WiFiPackage',(9,-2,0));shift('JoyRWirelessIC',(0,-3,0))
for tag in ['L','R']:
    for suffix in ['HapticCase','HapticMass','HapticCoil','HapticSpring0','HapticSpring1']:shift('Joy'+tag+suffix,(3.0,0,0))
for row in [-1,1]:
    for j in range(12):shift(f'DockPlugContact{row}_{j}',(0,0,-row*.65))
box('DockPlugInsulator','底座 USB-C 插头绝缘芯',6.6,1.10,4.6,(0,DOCK_Y-38.4,11.4),'DockInternal',2,'black',.3,True,orient=YROT)
# Eight console rail screws with a recessed head and isolated mounting bosses.
for side in [-1,1]:
    for j,y in enumerate([-37,-10,10,37],1):
        axis=(-side,0,0);p=vec(side*84.0,y,7.15)
        cut('ConsoleRail'+str(side),[Part.makeCylinder(1.37,.52,p+vec(side*.08,0,0),vec(*axis)),Part.makeCylinder(.85,4.5,p,vec(*axis))],'导轨紧固螺钉孔')
        screw(f'RailScrew{side}_{j}',(side*84.0,y,7.15),'Tablet',0,radius=1.22,length=3.4,axis=axis,drive='cross')
        ringpart(f'RailBoss{side}_{j}','导轨螺钉安装柱',1.55,.84,2.8,(side*83.2,y,7.15),'TabletInternal',0,'shell',axis=axis,internal=True)
# Edge softening is inserted before the opening operations in each native shell body.
for tag in ['L','R']:
    body=D.getObject('Joy'+tag+'FrontBlank');tip=body.Tip
    top=tip.Shape.BoundBox.ZMax
    edges=[f'Edge{i+1}' for i,e in enumerate(tip.Shape.Edges) if e.BoundBox.ZLength<1e-7 and abs(e.BoundBox.ZMax-top)<1e-7]
    f=body.newObject('PartDesign::Fillet','Joy'+tag+'EdgeSoftening');f.Base=(tip,edges);f.Radius=.18;body.Tip=f;D.recompute();tip.Visibility=False
    assert not f.Shape.isNull() and f.Shape.isValid()
# Accessory cord attachment loops complete the strap-to-rail transition.
for side,tag in [(-1,'L'),(1,'R')]:
    y=-327;x=side*105
    feature('Strap'+tag+'CordAnchor','腕带绳固定环',Part.makeTorus(1.65,.55,vec(x,y-50.1,6),vec(1,0,0)),'Strap'+tag,0,'black')
    cut('Strap'+tag+'Body',Part.makeTorus(1.70,.61,vec(x,y-50.1,6),vec(1,0,0)),'腕带锚环安装槽')
# Publish envelope checks from the actual shape union bounds.
handheld=[o for o in C.values() if o.Assembly in HANDHELD_GROUPS]
h=Part.makeCompound([o.Shape for o in handheld]).BoundBox
dock=Part.makeCompound([o.Shape for o in C.values() if o.Assembly in ['Dock','DockInternal']]).BoundBox
RESULT=stage_done(12,'final_fit_and_edge_finish','完成剩余芯片、振动单元和底座插头配合，增加八颗导轨螺钉、安装柱、手柄边缘微圆角及腕带固定环。',views=[('front',{'assemblies':HANDHELD_GROUPS}),('hero',{'assemblies':HANDHELD_GROUPS,'normal':(-.45,-.4,2)}),('back',{'assemblies':HANDHELD_GROUPS,'normal':(0,0,-1)}),('dock',{'assemblies':['Dock','DockInternal'],'normal':(-.6,.3,2),'target':(0,DOCK_Y,0),'span':150})],extra={'handheld_envelope_mm':[h.XLength,h.YLength,h.ZLength],'dock_envelope_mm':[dock.XLength,dock.YLength,dock.ZLength]})
