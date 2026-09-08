"""Presentation offsets: major layers are separated enough to inspect each module."""
def exploded_offset(key,src):
    a=src.Assembly;l=src.ExplodeLayer
    if a in ['Tablet','Display','TabletInternal']:
        z=0
        if a=='TabletInternal':z=-120
        if key in ['TabletRear','RearNintendoMark','RearModelMark']:z=-590
        if key in ['Kickstand','StandFoot','StandHinge0','StandHinge1','StandHinge2','StandHingePin']:z=-710
        if key=='RearEMIShield':z=-470
        if key.startswith('Battery'):z=-240
        if key.startswith(('Fan','CoolingFin')) or key in ['HeatSpreader','CopperHeatPipe','SoCThermalPad','HeatPipeBridge']:z=-350
        z={'DisplayGlass':500,'FrontBezel':380,'LCDModule':260,'DisplayBackplate':140}.get(key,z)
        return vec(0,0,z)
    if a.startswith('Joy'):
        left=a in ['JoyLeft','JoyRailL','JoyInternalL'];dx=-157 if left else 157
        z={-5:-170,-4:-130,-3:-90,-2:-60,-1:-20,0:0,1:20,2:35,3:65,4:90,5:140}.get(l,l*28)
        if key in ['JoyLPCB','JoyRPCB']:z=25
        return vec(dx,-220,z)
    if a in ['Dock','DockInternal']:
        z=-170 if a=='DockInternal' else 0
        if key=='DockBackCover' or key.startswith('DockScrew'):z=-350
        if key in ['DockFront','DockLogo','DockLED']:z=170
        if key.startswith('DockGuideFront'):z=125
        if key.startswith(('DockPlug','DockUSBCPlug','DockGuidePin')):z=80
        if key=='DockConnectorMount':z=40
        return vec(-110,-268,z)
    if a=='Grip':
        dx=-83
        if key.startswith('GripHandle'):dx+=-32 if '-1' in key else 32
        elif key.startswith('GripRail'):dx+=-18 if '-1' in key else 18
        return vec(dx,-271,l*23)
    return vec(0,-300,l*25)

EXPLODED_CAMERAS={
'exploded_handheld':dict(assemblies=HANDHELD_GROUPS,normal=(1.7,-.2,-1),target=(0,-95,-90),span=560,size=(3200,1600)),
'exploded_tablet':dict(assemblies=['Tablet','Display','TabletInternal'],normal=(1.7,-.2,-1),target=(0,0,-100),span=440,size=(3400,1300)),
'exploded_joy_left':dict(assemblies=['JoyLeft','JoyRailL','JoyInternalL'],normal=(.9,-.15,1.2),target=(-260,-220,-15),span=250,size=(1800,1500)),
'exploded_joy_right':dict(assemblies=['JoyRight','JoyRailR','JoyInternalR'],normal=(-.9,-.15,1.2),target=(260,-220,-15),span=250,size=(1800,1500)),
'exploded_dock':dict(assemblies=['Dock','DockInternal'],normal=(1.5,-.2,-1),target=(-110,-450,-60),span=325,size=(2600,1400)),
'exploded_grip':dict(assemblies=['Grip'],normal=(.7,-.25,1.5),target=(130,-450,0),span=160,size=(2000,1300))}
