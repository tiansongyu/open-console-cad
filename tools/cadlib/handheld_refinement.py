"""Public-reference exterior refinements; fitted details are not factory dimensions.

These operations preserve the existing physical part identifiers and native
construction history. Run with the clamshell in its flat construction pose.
"""
import math
import FreeCAD as App
import Part
from .core import V
from . import geometry as g


def replace(m, key, shape, reason):
    # Finalize assigns part numbers in registration order. Retain that order
    # while feature() requires the old key to be temporarily absent.
    registered = list(m.parts.items())
    old = m.parts.pop(key)
    assert shape.isValid() and shape.Solids, key
    old.PhysicalPart = False
    new = m.feature(key, old.Label, shape, old.Assembly, old.ExplodeLayer,
                    old.MaterialDescription, old.Fidelity.startswith('Schematic'), old.PoseGroup)
    m.parts.clear()
    m.parts.update((part_id, new if part_id == key else part)
                   for part_id, part in registered)
    new.addProperty('App::PropertyLink', 'PreviousRevision', 'Revision')
    new.PreviousRevision = old
    new.addProperty('App::PropertyString', 'RevisionReason', 'Revision')
    new.RevisionReason = reason
    if 'PartNumber' in old.PropertiesList:
        new.addProperty('App::PropertyString', 'PartNumber', 'Study')
        new.PartNumber = old.PartNumber
    new.ViewObject.ShapeAppearance = old.ViewObject.ShapeAppearance
    old.Visibility = False
    return new


def edge_roll(m, key, width, height, plan_radius, depth, pos, radius, top=True):
    """Cut only the outer edge of a blank, retaining every existing aperture."""
    blank = m.rr(width, height, depth, pos, plan_radius)
    z = pos[2] + (depth if top else 0)
    edges = [e for e in blank.Edges if e.BoundBox.ZLength < 1e-6
             and abs(e.BoundBox.ZMin-z) < 1e-6]
    rounded = blank.makeFillet(radius, edges)
    tool = blank.cut(rounded)
    assert tool.isValid() and tool.Volume > 0
    result = m.cut(key, tool, 'Public-reference outer edge roll %.2f mm (estimated)' % radius)
    assert result.Shape.isValid() and result.Shape.Solids, key


def refine_3ds(m):
    m.set_pose(180)
    cap = m.parts['CirclePadCap'].Shape
    b = cap.optimalBoundingBox(False, False)
    sphere = Part.makeSphere(24, V(b.Center.x, b.Center.y, b.ZMax+24-.42))
    m.cut('CirclePadCap', sphere, 'Concave Circle Pad face; depth estimated from original CTR-001 imagery')
    g.appearance(m.parts['CirclePadCap'], (.59, .60, .61))
    p = m.profile
    edge_roll(m, 'FrontDeck', p['width']-.4, p['height']-.4, 5.4, 1,
              (0, 0, p['base_depth']-1.8), .35)
    m.profile['stages'] = 14
    m.checkpoint(14, 'public_reference_circle_pad_and_edges',
                 '依据原版部位图补充 Circle Pad 凹面与灰色胶面，软化控制面板外缘；局部曲率为估计。')


def refine_nds(m):
    m.set_pose(180)
    p = m.profile
    edge_roll(m, 'FrontDeck', p['width']-.7, p['height']-.7, 9.65, 1.05,
              (0, 0, p['base_depth']-1.85), .45)
    edge_roll(m, 'LidBackCover', p['lid_width'], p['lid_height'], 7.2, 1,
              (0, 2*p['hinge_y'], 2*p['hinge_z']-p['closed_depth']), .40, False)
    m.profile['stages'] = 16
    m.checkpoint(16, 'public_reference_enclosure_edges',
                 '依据 NTR-001 官方外观图增加控制面板与上盖的厚度方向圆润过渡，保留闭合包络和接口。圆角为图像估计。')


def refine_psp(m):
    from .psp import _polygon
    from .clamshell import _move
    # The original manual p20 shows four inward-pointing, flat-ended petals.
    # Front diagram ratios constrain these estimates, but are not production dimensions.
    holes = [o for o in m.doc.Objects if o.Label.startswith('Directional-key opening · tool')]
    stem_holes = [o for o in m.doc.Objects if o.Label.startswith('Directional stem passage · tool')]
    face_holes = [o for o in m.doc.Objects if o.Label.startswith('Face-button bore · tool')]
    assert len(holes) == 4
    for i, (key, angle) in enumerate([('Up',0),('Right',-90),('Down',180),('Left',90)]):
        pts = [(0,1.8),(4.2,6.0),(4.2,13.0),(-4.2,13.0),(-4.2,6.0)]
        shape = _polygon([(-65+x,4.5+y) for x,y in pts],22.6,.95)
        shape.rotate(V(-65,4.5,0),V(0,0,1),angle)
        replace(m,'DPad'+key,shape,'Inward-pointing pentagonal petal from Sony PSP-1000 manual p20')
        clearance=[(0,1.5),(4.4,5.9),(4.4,13.2),(-4.4,13.2),(-4.4,5.9)]
        tool = _polygon([(-65+x,4.5+y) for x,y in clearance],21.65,2.15)
        tool.rotate(V(-65,4.5,0),V(0,0,1),angle)
        holes[i].Shape = tool
        a=math.radians(angle);dx=-3.5*math.sin(a);dy=-5.5+3.5*math.cos(a)
        for name in ['DPadStem'+key,'DPadArrow'+key]+['Control'+s+str(i) for s in ['Contact','Pill','Rubber','Boss']]:
            _move(m,name,(dx,dy,0))
        stem_holes[i].Shape=m.parts['DPadStem'+key].Shape.copy()
    replace(m,'DPadCarrier',Part.makeCylinder(12.6,.35,V(-65,4.5,20.94)),
            'Carrier follows the enlarged directional control cluster (schematic)')
    replace(m,'DPadPCB',m.rr(25.5,23,.50,(-65,4.5,16.5),1),
            'Directional board follows calibrated contact locations (schematic)')
    for j,(ux,uy,ch) in enumerate([(0,1,'Triangle'),(1,0,'Circle'),(0,-1,'Cross'),(-1,0,'Square')]):
        x,y=65+ux*10.4,4.5+uy*10.4;dx,dy=ux*2.9,-4.5+uy*2.9
        cap=Part.makeCylinder(4.6,1.15,V(x,y,22.5))
        cap=cap.makeFillet(.22,[e for e in cap.Edges if e.BoundBox.ZLength<1e-6])
        replace(m,'Button'+ch,cap,'Face-button proportions fitted to the original PSP-1000 front diagram')
        for name in ['ButtonSymbol'+ch,'ButtonStem'+ch]+['Control'+s+str(j+4) for s in ['Contact','Pill','Rubber','Boss']]:
            _move(m,name,(dx,dy,0))
        face_holes[j].Shape=Part.makeCylinder(4.78,2.6,V(x,y,21.4))
    # Restore the narrow window border visible in the same front diagram;
    # the oversized old border collided with the corrected square-button cap.
    w,h=m.profile['upper_display']
    surround=m.rr(99.0,58.0,.35,(0,3.5,22.6),.8).cut(m.rr(w+.12,h+.12,.6,(0,3.5,22.5),.2))
    replace(m,'DisplaySurround',surround,'Narrower front display border from Sony front diagram; active display unchanged')
    next(o for o in m.doc.Objects if o.Label.startswith('LCD and window-surround recess · tool')).Shape=m.rr(99.3,58.3,1.7,(0,3.5,21.6),.9)
    _move(m,'PowerLegend',(0,-4.5,0))
    names=['PSPFrontMark','SonyFrontMark','PlayStationFrontMark','PowerLegend','HoldLegend']
    next(o for o in m.doc.Objects if o.Label.startswith('Flush front-face legend inlays · tool')).Shape=Part.makeCompound([m.parts[k].Shape for k in names])
    replace(m,'PowerBoard',m.rr(11,18,.6,(75,-8,15.65),.7),
            'Schematic daughterboard clearance below the repositioned action-button contacts')
    m.doc.recompute()
    edge_roll(m,'FrontBezel',169.6,73.6,30.8,1.2,(0,0,21.8),.45)
    m.profile['stages'] = 15
    m.checkpoint(15,'public_reference_directional_petals',
                 '按索尼 PSP-1000 原版说明书纠正四向键方向与比例、面键直径和间距，同步孔位与传动接点，并柔化前面板外缘；局部坐标为图像拟合。')


def refine_psv(m):
    from .psv import _ellipse
    seats = [o for o in m.doc.Objects if o.Label.startswith('Strap-eye seat and through opening · tool')]
    rear = [o for o in m.doc.Objects if o.Label.startswith('Strap-eye rear through-opening · tool')]
    pcbs = [o for o in m.doc.Objects if o.Label.startswith('Controller-board strap-eye notch · tool')]
    assert (len(seats),len(rear),len(pcbs)) == (6,2,2)
    for j,side in enumerate([-1,1]):
        x,y=side*68.7,-35.15
        outer=_ellipse(10.0,3.8,16.9,1.7,x,y)
        opening=_ellipse(6.8,1.8,-.1,20,x,y)
        for shape in [outer,opening]:shape.rotate(V(x,y,0),V(0,0,1),side*28)
        eye=outer.cut(opening)
        replace(m,'StrapEye'+str(side),eye,
                'Reduced corner strap loop prominence from Sony PCH-1000 parts image; dimensions estimated')
        for tool in seats[j*3:j*3+3]:tool.Shape=Part.makeCompound([eye,opening])
        rear[j].Shape=opening.copy();pcbs[j].Shape=opening.copy()
    m.doc.recompute()
    m.profile['stages']=15
    m.checkpoint(15,'public_reference_corner_strap_eyes',
                 '按索尼 PCH-1000 部位图缩小过大的角部腕带环，重新生成前后壳及操作板孔位；局部尺寸为外观拟合。')


def refine_switch2(ns):
    """Update both face-button clusters and matching stems, contacts and seats."""
    D,C=ns['D'],ns['C']
    holes=[o for o in D.Objects if o.Label.startswith('方向/ABXY 按键孔 · 刀具')]
    assert len(holes)==2, len(holes)
    for tag,cx,cy,tool in [('L',-118,-1.0,holes[0]),('R',118,29.3,holes[1])]:
        cutters=[]
        for j,(ux,uy,char) in enumerate([(0,1,'X'),(1,0,'A'),(0,-1,'B'),(-1,0,'Y')]):
            dx,dy=ux*(8.5-10.8),uy*(8.5-10.8)
            x,y=cx+ux*8.5,cy+uy*8.5
            key='Joy'+tag+'FaceButton'+str(j)
            cap=Part.makeCylinder(4.2,1.85,V(x,y,13.45))
            cap=cap.makeFillet(.20,[e for e in cap.Edges if e.BoundBox.ZLength<1e-7])
            old=C[key];old.PhysicalPart=False
            new=ns['feature'](key,old.Label,cap,old.Assembly,old.ExplodeLayer,old.MaterialDescription)
            new.addProperty('App::PropertyLink','PreviousRevision','Revision');new.PreviousRevision=old
            if 'PartNumber' in old.PropertiesList:
                new.addProperty('App::PropertyString','PartNumber','CAD study');new.PartNumber=old.PartNumber
            old.Visibility=False
            for suffix in ['ButtonStem','ButtonPad','ButtonDome']:
                o=C['Joy'+tag+suffix+str(j)];o.Placement.Base+=V(dx,dy,0)
            glyph=C['Arrow'+str(j) if tag=='L' else 'Glyph'+char]
            glyph.Placement.Base+=V(dx,dy,0)
            cutters.append(Part.makeCylinder(4.35,2.2,V(x,y,12.2)))
        tool.Shape=Part.makeCompound(cutters)
    D.recompute()
    return ns['stage_done'](16,'public_reference_face_button_spacing',
        '依据官方 Joy-Con 2 正面部位图将八枚面键中心距从 10.8 调为 8.5 mm、直径从 7.4 调为 8.4 mm；同步孔位、传力柱、接点和弹片。数值为图像拟合，非原厂标注。',
        views=[('front',{'span':200}),('hero',{'normal':(-.4,-.4,2),'span':200})])
