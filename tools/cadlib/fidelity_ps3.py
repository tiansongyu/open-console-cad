"""CECHA00 exterior layout from Sony's original manual and firsthand photographs.

Positions and local profiles are fitted studies, not factory dimensions. The
rear view reverses world X: its right-hand connectors occupy negative X.
"""
import math
import FreeCAD as App
import Part
from .core import V
from . import geometry as g
from .handheld_refinement import replace
from .atari2600 import _rounded_route

REAR_CENTRES={'HDMI':(-32,34),'LAN':(-51,31),'OpticalAudio':(-71,32),
              'AVMulti':(-96,31.5),'ACInlet':(-134,16)}
TOUCH_X={'Power':130,'Eject':75}


def _tool(m,label):
    found=[o for o in m.doc.Objects if o.Label.startswith(label+' · tool')]
    assert len(found)==1,(label,len(found))
    return found[0]


def _replace(m,key,shape,reason):
    shape.check(True)
    return replace(m,key,shape,reason)


def _move(m,key,dx,dz,reason):
    shape=m.parts[key].Shape.copy();shape.translate(V(dx,0,dz))
    return _replace(m,key,shape,reason)


def _rear_vents():
    # Firsthand CECHA-family rear photograph: six columns in each bank;
    # rear-left bank has five rows except the outer column's lower two rows.
    # Slot dimensions/spacing are photographic estimates.
    slots=[]
    for column,x in enumerate([12,27,42,57,72,87]):
        for row,z in enumerate([6.4,11.4,16.4,21.4,26.4]):
            if column==5 and row<2:continue
            slots.append(Part.makeBox(13,12,2.2,V(x-6.5,117,z)))
    for x in [-24,-39,-54,-69,-84,-99]:
        for z in [5.3,9.8,14.3,18.8]:
            slots.append(Part.makeBox(13,12,2.2,V(x-6.5,117,z)))
    return Part.makeCompound(slots)


def refine_ps3(m):
    before=tuple(m.parts)
    rear=g.rotation((0,1,0),(0,0,1))
    for key,old_x,prefixes in [('HDMI',9,('HDMI',)),('LAN',33,('LANShield','LANBack','LANContact','LANLight')),
                              ('OpticalAudio',57,('OpticalSocket','OpticalShutter','OpticalEmitter')),
                              ('AVMulti',82,('AVShield','AVBack','AVTongue','AVContact')),
                              ('ACInlet',124,('ACSocket','ACBlade'))]:
        x,z=REAR_CENTRES[key]
        for part in list(m.parts):
            if part.startswith(prefixes):
                _move(m,part,x-old_x,z-22,'Sony CECHA00 rear-view location, fitted from original manual')
        tool=_tool(m,'Original rear '+key+' opening');shape=tool.Shape.copy();shape.translate(V(x-old_x,0,z-22));tool.Shape=shape
    _move(m,'MasterSwitch',-258,-2.6,'Rear master switch sits above the relocated grounded AC inlet')
    tool=_tool(m,'Rear master switch aperture');shape=tool.Shape.copy();shape.translate(V(-258,0,-2.6));tool.Shape=shape
    _tool(m,'Rear exhaust slots through the lower shell').Shape=_rear_vents()

    # Compatible HDMI Type A geometry: 19 contacts in two staggered rows.
    x,z=REAR_CENTRES['HDMI'];y=110.8
    def hdmi(w,h,length,dy=0):
        pts=[(-w/2,-h/2+1.5),(-w/2+1.5,-h/2),(w/2-1.5,-h/2),(w/2,-h/2+1.5),(w/2,h/2),(-w/2,h/2)]
        points=[V(a,b) for a,b in pts];shape=Part.Face(Part.makePolygon(points+[points[0]])).extrude(V(0,0,length));shape.Placement=App.Placement(V(x,y+dy,z),rear);return shape
    _replace(m,'HDMIShield',hdmi(15,5.65,12).cut(hdmi(14,4.55,12.4,-.2)),
             'HDMI Type A compatible 15 x 5.65 mm sleeve; axial length remains estimated')
    _replace(m,'HDMIBack',m.rr(11,.7,3.6,(x,y+.5,z-1.8),.1),'HDMI rear carrier follows reduced mating profile')
    _replace(m,'HDMITongue',m.rr(11.3,8,.96,(x,y+6.5,z-.48),.1),'HDMI two-sided tongue')
    for side,count in [(1,10),(-1,9)]:
        for i in range(count):
            _replace(m,'HDMIContact'+str(side)+'_'+str(i),m.rr(.3,6,.06,(x+(i-(count-1)/2),y+6.8,z+(.50 if side==1 else -.56)),.02),
                     'HDMI Type A contact row at 1.0 mm pitch; opposing row staggered 0.5 mm')
    _tool(m,'Original rear HDMI opening').Shape=m.rr(15.8,6.4,16,(x,111,z),.65,rear)
    x,z=REAR_CENTRES['LAN']
    for i in range(8):
        _replace(m,'LANContact'+str(i),m.rr(.35,7.5,.22,(x+(i-3.5)*1.02,116.9,z-3.7),.03),
                 'Eight-contact modular receptacle at manufacturer nominal 1.02 mm pitch')

    # Match the existing single-row 12-contact AV cable instead of two rows.
    x,z=REAR_CENTRES['AVMulti'];y=110.5
    shell=m.rr(19,7.8,12.4,(x,y,z),.8,rear).cut(m.rr(18,6.8,12.8,(x,y-.2,z),.5,rear))
    _replace(m,'AVShield',shell,'Single-row PlayStation AV MULTI receptacle matched to the study cable')
    _replace(m,'AVBack',m.rr(17.5,.65,6.3,(x,y+.5,z-3.15),.2),'Reduced AV MULTI rear carrier')
    _replace(m,'AVTongue',m.rr(16.4,8.7,1.1,(x,y+6.9,z-.55),.2),'Single-row AV MULTI insulating tongue')
    for index,(side,i) in enumerate((side,i) for side in [-1,1] for i in range(6)):
        _replace(m,'AVContact'+str(side)+'_'+str(i),m.rr(.5,6.8,.14,(x+(index-5.5)*1.25,y+7,z+.62),.03),
                 'Twelve contacts in one row; 1.25 mm pitch retained from the compatible study plug')
    _tool(m,'Original rear AVMulti opening').Shape=m.rr(19.8,8.6,16,(x,111,z),.65,rear)

    # Rebuild the grounded inlet and its three display harness paths. Existing
    # board/shield Boolean tools are moved with the harness, closing old holes.
    x,z=REAR_CENTRES['ACInlet'];y=109.5
    shell=m.rr(24,17.6,13.3,(x,y,z),2,rear).cut(m.rr(20.4,14.1,12.2,(x,y+1.4,z),1.7,rear))
    for i,(sx,sz,end) in enumerate([(x-5,z-2.675,-26),(x,z+3.825,-22),(x+5,z-2.675,-18)]):
        yy=104+2*i;top=51.8+i*1.4
        path=[V(sx,111.8,sz),V(sx,yy,sz),V(sx,yy,top),V(end,yy,top),V(end,85,top),V(end,81.6,50.95)]
        wire=_rounded_route(path,1.2,.55);clearance=_rounded_route(path,1.2,.77)
        _replace(m,'ACInternalLead'+str(i),wire,'Rerouted three-wire AC study to the corrected rear inlet')
        found=[o for o in m.doc.Objects if o.Label.startswith('Insulated harness passage: ACInternalLead'+str(i)+' · tool')]
        assert len(found)==4,(i,len(found))
        for tool in found:tool.Shape=clearance
        shell=shell.cut(clearance)
    _replace(m,'ACSocket',shell,'Relocated grounded AC inlet with revised harness passages')

    # Power/eject icons occupy distinct positions along the front lip. Keep the
    # existing FFC connection, widening its illustrative sensing board locally.
    for key,x in TOUCH_X.items():
        _move(m,key+'TouchSurface',x-145,0,'Separated front power/eject positions in Sony manual and first-hand top photograph')
    _replace(m,'ControlPCB',m.rr(75,10,1,(102.5,-111,35),1),'Photo-guided control-board envelope accommodates the separated touch electrodes')
    for index,(old_x,new_x) in enumerate([(104,75),(126,130)]):
        for prefix in ['TouchController','TouchCopper']:
            _move(m,prefix+str(index),new_x-old_x,0,'Sensing parts follow the separate power/eject touch positions')
    refine_fit(m)
    m.doc.recompute()
    assert tuple(m.parts)==before
    m.profile['stages']=31
    return m.checkpoint(31,'official_exterior_layout_and_matched_av_interface',
        '按 Sony CECHA00 原版说明书和 CECHA01 实机后视图修正后排接口侧别、高度及两组横向风口，'
        '同步壳体开孔与 AC 三线束；分开前沿电源/出仓触点与传感板，AV MULTI 改为与附件匹配的 12 接点单排，'
        'HDMI 与 LAN 采用兼容接口节距。局部坐标、壳体细节、接插件深度与内部线路仍为构造估计。')

def refine_fit(m):
    """Keep changed controls and grounded inlet clear of the study supports."""
    x,z=REAR_CENTRES['HDMI']
    _replace(m,'HDMIBack',m.rr(11,.7,3.6,(x,111.3,z-1.8),.1),
             'Rear carrier clears the bevels of the compatible HDMI sleeve')
    tool=_tool(m,'Optical electronics, front controls, posts and harness access')
    shapes=[]
    for shape in tool.Shape.Solids:
        b=shape.optimalBoundingBox(False,False)
        if abs(b.XLength-53)<1e-6 and abs(b.YLength-15)<1e-6:
            shapes.append(m.rr(78,15,1,(102.5,-110,36.8),1))
        else:shapes.append(shape)
    tool.Shape=Part.makeCompound(shapes)
    # The former corner post occupied the corrected AC cavity. Move the whole
    # illustrative fastening stack inward and move all three board bores too.
    if not getattr(m.parts['CasePillar1'],'FidelityRelocated',False):
        for key in ['CasePillar1','CaseUpperSpacer1','CaseFixing1']:
            shape=m.parts[key].Shape.copy();shape.translate(V(0,-20,0));obj=_replace(m,key,shape,'Rear fixing stack moves inward to clear the actual AC port side')
            obj.addProperty('App::PropertyBool','FidelityRelocated','Revision');obj.FidelityRelocated=True
        for tool in [o for o in m.doc.Objects if o.Label.startswith('Outer fixing-stack clearance · tool')]:
            shapes=[]
            for shape in tool.Shape.Solids:
                b=shape.optimalBoundingBox(False,False)
                if abs(b.Center.x+145)<1e-6 and abs(b.Center.y-115)<1e-6:
                    shape=shape.copy();shape.translate(V(0,-20,0))
                shapes.append(shape)
            tool.Shape=Part.makeCompound(shapes)
    closure=m.rr(302,2,10.5,(0,129.4,40.5),.7).cut(m.parts['InnerHood'].Shape)
    closure=max(closure.Solids,key=lambda shape:shape.Volume)
    _replace(m,'RearFascia',closure,
             'Estimated rear closure skirt follows the hood underside and masks the former open gap')


stage31=refine_ps3
