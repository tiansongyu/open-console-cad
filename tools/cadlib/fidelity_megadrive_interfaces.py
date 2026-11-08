"""Model 1 port layout fitted to SEGA's front/rear photographs, plus pin pitch.

Published body width calibrates the photographs. Local positions and housing
profiles remain estimates; standard contact arrays do not establish OEM parts.
"""
import FreeCAD as App
import Part

from .core import V
from . import geometry as g
from .handheld_refinement import replace
from .retro_common import d_profile


FRONT_PORT_X = (54.0,86.5)
REAR_EXT_X, REAR_AV_X, REAR_DC_X = -29.7,-71.3,-91.8
HEADPHONE_X = -86.5
DSUB_PITCH, DSUB_ROW_SPACING = 2.77,2.84
CARTRIDGE_PITCH = 2.54


def _tool(m,label):
    objects=[o for o in m.doc.Objects if o.Label.startswith(label+' · tool')]
    assert len(objects)==1,(label,len(objects))
    return objects[0]


def _replace(m,key,shape,reason):
    shape.check(True)
    return replace(m,key,shape,reason)


def _move_x(m,key,delta,reason):
    shape=m.parts[key].Shape.copy();shape.translate(V(delta,0,0))
    return _replace(m,key,shape,reason)


def add_registration_lip(m):
    """Close the visible case seam with an estimated internal overlap lip."""
    from .retro_common import fuse_feature
    old=m.parts['LowerHousing']
    if getattr(old,'FidelityOverlapLip',False):
        return
    number=getattr(old,'PartNumber',None)
    flange=m.rr(277,209,.4,(0,0,17.6),8.5).cut(
        m.rr(270,202,.6,(0,0,17.5),5))
    upright=m.rr(274.6,206.6,2.7,(0,0,17.6),7.3).cut(
        m.rr(272.2,204.2,2.9,(0,0,17.5),6.1))
    lip=flange.fuse(upright).removeSplitter()
    opening=next(o for o in m.doc.Objects if o.Label.startswith('Right expansion-bus cover opening · tool'))
    lip=lip.cut(opening.Shape);lip.check(True)
    fuse_feature(m,'LowerHousing',lip,'Estimated inner overlap lip with expansion-cover clearance')
    obj=m.parts['LowerHousing'];obj.addProperty('App::PropertyBool','FidelityOverlapLip','Refinement');obj.FidelityOverlapLip=True
    if number is not None:
        obj.addProperty('App::PropertyString','PartNumber','Study');obj.PartNumber=number


def _de9(m,key,origin,normal,female=False,front=False,plug=False):
    frame=App.Placement(V(*origin),g.rotation(normal,(0,0,1)))
    def place(shape):
        shape.Placement=frame.multiply(shape.Placement)
        return shape
    if plug:
        outer_w,outer_h,inner_w,inner_h,insert_w,insert_h=16.33,7.9,14.9,6.5,14.3,5.9
    elif front:
        outer_w,outer_h,inner_w,inner_h,insert_w,insert_h=18.4,10.0,16.9,8.4,16.3,7.8
    else:
        outer_w,outer_h,inner_w,inner_h,insert_w,insert_h=22.4,12.0,16.7,8.4,16.3,7.8
    shell=d_profile(outer_w,outer_h).extrude(V(0,0,7)).cut(
        d_profile(inner_w,inner_h,-.1).extrude(V(0,0,7.2)))
    obj=_replace(m,key+'Shield',place(shell),
                 'SEGA original port photograph: fitted exterior housing, with distinct front/rear treatment')
    if front:
        obj.MaterialDescription='black';g.appearance(obj,m.colors['black'])
        obj.Label=key+' · Black molded controller-port housing'
    elif plug:
        obj.Label=key+' · Female connector nose metal shell'
    else:
        obj.Label=key+' · Rear EXT metal surround study'
    points=[((i-2)*DSUB_PITCH,DSUB_ROW_SPACING/2) for i in range(5)]
    points += [((i-1.5)*DSUB_PITCH,-DSUB_ROW_SPACING/2) for i in range(4)]
    holes=[Part.makeCylinder(.67,3.4,V(x,y,-.2)) for x,y in points]
    insert=d_profile(insert_w,insert_h).extrude(V(0,0,3)).cut(Part.makeCompound(holes))
    _replace(m,key+'Insert',place(insert),'DE-9 five/four contact rows at 2.77 x 2.84 mm')
    for i,(x,y) in enumerate(points):
        pin=Part.makeCylinder(.65 if female else .49,5.8,V(x,y,.1))
        if female:pin=pin.cut(Part.makeCylinder(.52,6,V(x,y,0)))
        _replace(m,key+'Pin'+str(i),place(pin),
                 'DE-9 female receptacle' if female else 'DE-9 male contact; standard row pitch')
    for side in [-1,1]:
        ear_z=-1.0 if key=='ExtensionPort' else 0.0
        ear=g.rr_shape(4,10.6,.8,1,(side*12.495,0,ear_z)).cut(
            Part.makeCylinder(1.45,1.4,V(side*12.495,0,ear_z-.2)))
        _replace(m,key+'Tab'+str(side),place(ear),'24.99 mm mounting-axis separation; local ear form remains a study')
    return place(d_profile(outer_w+.6,outer_h+.8,-1).extrude(V(0,0,10)))


def refine_megadrive_interfaces(m):
    """Apply after the DIN correction, retaining existing IDs and registration order."""
    before=tuple(m.parts)
    for i,(old_x,x) in enumerate(zip((-59.0,5.0),FRONT_PORT_X),1):
        opening=_de9(m,'PadPort'+str(i),(x,-99,29),(0,-1,0),front=True)
        _tool(m,'Front controller '+str(i)+' aperture').Shape=opening
        for part in ['PadPortSupport'+str(i),'PortNumber'+str(i)]:
            _move_x(m,part,x-old_x,'Controller-port right-side position fitted to SEGA front photograph')
    opening=_de9(m,'ExtensionPort',(REAR_EXT_X,99,29),(0,1,0),female=True)
    _tool(m,'Original rear extension-controller socket').Shape=opening
    _de9(m,'PadPlug',(187,-185,12),(1,0,0),female=True,plug=True)
    right=g.rotation((1,0,0),(0,0,1))
    body=m.rr(34,15,18,(177.2,-185,12),3,right)
    body=body.cut(m.rr(17,8.8,9,(186.6,-185,12),1,right))
    body=body.cut(m.rr(35,12,3,(186.8,-185,12),1,right))
    _replace(m,'PadPlugBody',body,'Controller plug nose fitted around the corrected female mating insert')

    for key,old_x,x in [('Headphones',-113,HEADPHONE_X),('AV',-11,REAR_AV_X),('PowerDC',83,REAR_DC_X)]:
        for suffix in ['Barrel','Insulator']:
            _move_x(m,key+suffix,x-old_x,'Front/rear X position fitted to SEGA official original Model 1 view')
        tool=_tool(m,key+' rear/front panel opening')
        shape=tool.Shape.copy();shape.translate(V(x-old_x,0,0));tool.Shape=shape
    for key in ['AVInsert']+['AVContact'+str(i) for i in range(8)]:
        _move_x(m,key,REAR_AV_X+11,'DIN-8 assembly follows the corrected rear AV position')
    _move_x(m,'PowerCenter',REAR_DC_X-83,'DC centre contact follows the corrected rear port')

    # A 5.5 / 2.1 mm compatible power plug needs an annular entry around its
    # centre pin, rather than the former 2 mm single bore through a solid face.
    barrel=Part.makeCylinder(3.5,6.5,V(REAR_DC_X,98,30),V(0,1,0)).cut(
        Part.makeCylinder(2.8,6.7,V(REAR_DC_X,97.9,30),V(0,1,0)))
    _replace(m,'PowerDCBarrel',barrel,'Annular entry for a nominal 5.5 mm DC plug; local clearance estimated')
    insulator=Part.makeCylinder(2.75,1,V(REAR_DC_X,98,30),V(0,1,0)).cut(
        Part.makeCylinder(1.05,1.2,V(REAR_DC_X,97.9,30),V(0,1,0)))
    _replace(m,'PowerDCInsulator',insulator,'Recessed rear insulator leaves the coaxial insertion space open')
    _replace(m,'PowerCenter',Part.makeCylinder(1,4,V(REAR_DC_X,99,30),V(0,1,0)),
             '2.0 mm study centre pin with clearance for the compatible 2.1 mm plug bore')
    direction=V(10,-20,0).normalize();start=V(174,106,12)+direction*13.4
    plug=Part.makeCylinder(2.75,8,start,direction).cut(
        Part.makeCylinder(1.05,8.2,start-direction*.1,direction))
    _replace(m,'DCPlugBarrel',plug,'Compatible 5.5 mm OD / 2.1 mm ID power plug; original displayed depth retained')

    for side in [-1,1]:
        for i in range(32):
            delta=(i-15.5)*(CARTRIDGE_PITCH-2.8)
            _move_x(m,'CardLeaf'+str(side)+'_'+str(i),delta,
                    '64-contact Mega Drive card reader: 2.54 mm pitch')
            _move_x(m,'CartFinger'+str(side)+'_'+str(i),delta,
                    'Matching blank cartridge edge: 2.54 mm pitch')
    m.doc.recompute()
    add_registration_lip(m)
    assert tuple(m.parts)==before
    m.profile['stages']=15
    return m.checkpoint(15,'official_port_layout_and_matched_interfaces',
        '按 SEGA 官方正背面图校正两只前手柄口、耳机口与后 EXT/AV/DC 的侧别和位置，'
        '缩小前口轮廓并改为黑色壳，修正 EXT 母口及匹配手柄插头；DE-9 采用 2.77×2.84 mm 节距，'
        '卡座与卡带采用 2.54 mm 节距，电源口保留 5.5/2.1 mm 插头的环形插入空间，并以内搭接唇遮挡壳体分缝。'
        '局部位置、壳体轮廓和搭接尺寸为图像拟合或构造估计。')


stage15=refine_megadrive_interfaces
