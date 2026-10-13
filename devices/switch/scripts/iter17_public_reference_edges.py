"""Integrate the unequal-edge study with the already verified V16 cavities.

The study provides editable native loft sections and envelope intersections.
Its exploratory replacement cavity was rejected; retain the existing cavity
and opening tools instead. Image-derived curvature is not factory metrology.
"""
study_path = ROOT / 'studies/public-reference/Switch_Public_Reference_Study.FCStd'
study = next((d for d in App.listDocuments().values()
              if d.FileName and Path(d.FileName).resolve() == study_path.resolve()), None)
study_owned = study is None
if study_owned:
    study = App.openDocument(str(study_path))
App.setActiveDocument(D.Name)

for row, (alias, value, note) in enumerate([
    ('CalibratedFrontOuterRoll', 3.5, '专利图 3 拟合；记录值，改动需重建外缘截线'),
    ('CalibratedRearOuterRoll', 6.0, '专利图 4 拟合；记录值，改动需重建外缘截线'),
    ('CalibratedRailRoll', .65, '窄导轨侧过渡；图像估计，非制造尺寸'),
    ('CalibratedFaceButtonDiameter', 7.6, '官方照片与专利图交叉估计；需重建按键及孔'),
], 18):
    PARAM.set('A' + str(row), alias)
    PARAM.set('B' + str(row), str(value) + ' mm')
    PARAM.setAlias('B' + str(row), alias)
    PARAM.set('C' + str(row), note)

for tag in ['L', 'R']:
    for half in ['Front', 'Rear']:
        key = 'Joy' + tag + half
        old = C[key]
        tools = []
        obj = old
        while obj.TypeId == 'Part::Cut':
            tools.append((obj.Tool.Shape.copy(), obj.Tool.Label.split(' · 刀具')[0]))
            obj = obj.Base
        assert tools and obj.TypeId == 'PartDesign::Body', key
        names = {o.Name for o in D.Objects}
        envelope = D.copyObject(study.getObject(half + 'Candidate'), True)
        for obj in D.Objects:
            if obj.Name not in names:
                group('Construction').addObject(obj)
                obj.Visibility = False
        # Undo the study display layout to recover the left shell coordinates.
        envelope.Placement = (App.Placement(vec(-78, 0, 0), App.Rotation()) if half == 'Front'
                              else App.Placement(vec(-28, 0, 12.6), App.Rotation(vec(0, 1, 0), 180)))
        D.recompute()
        if tag == 'R':
            mirrored = D.addObject('Part::Mirroring', key + 'CalibratedEnvelope')
            mirrored.Source = envelope
            mirrored.Normal = vec(1, 0, 0)
            mirrored.Base = vec()
            group('Construction').addObject(mirrored)
            D.recompute()
            envelope.Visibility = False
            envelope = mirrored
        assert envelope.Shape.isValid() and len(envelope.Shape.Solids) == 1, key
        old.PhysicalPart = False
        register(envelope, key, old.Assembly, old.ExplodeLayer, old.MaterialDescription)
        envelope.Label = old.Label
        envelope.addProperty('App::PropertyLink', 'PreviousRevision', 'Revision')
        envelope.PreviousRevision = old
        old.Visibility = False
        for shape, reason in reversed(tools):
            cut(key, shape, reason + ' · 沿用已验证的内腔和孔位')
        assert C[key].Shape.isValid() and len(C[key].Shape.Solids) == 1, key

# Enlarge the eight round caps and corresponding holes. Keep existing switch
# stems, membranes and control centres; neither public source measures internals.
for tag in ['L', 'R']:
    holes = []
    for j in range(4):
        key = 'Joy' + tag + 'FaceButton' + str(j)
        bounds = C[key].Shape.optimalBoundingBox(False, False)
        x, y = bounds.Center.x, bounds.Center.y
        cap = Part.makeCylinder(3.8, 2.0, vec(x, y, 13.35))
        cap = cap.makeFillet(.22, [e for e in cap.Edges if e.BoundBox.ZLength < 1e-7])
        exterior_revision(key, cap, '公开照片和外观专利一致支持的约 7.6 mm 面键直径')
        holes.append(Part.makeCylinder(3.95, 2.5, vec(x, y, 12)))
    cut('Joy' + tag + 'Front', holes, '扩大面键孔，保持原中心位置')

for obj in C.values():
    obj.ViewObject.DisplayMode = 'Shaded'
    obj.ViewObject.Deviation = .025
    obj.ViewObject.AngularDeflection = 6
D.recompute()
if study_owned:
    App.closeDocument(study.Name)
App.setActiveDocument(D.Name)
RESULT = stage_done(17, 'public_reference_edges',
    '采用外侧宽、导轨侧窄的前后外缘放样；保留既有内腔及孔位；'
    '按官方产品图和 D819642 专利图将八个面键直径调整为约 7.6 mm。'
    '局部曲率为公开图拟合，内部仍为示意；不是原厂 CAD。',
    views=[('front', {'assemblies': HANDHELD_GROUPS, 'span': 165, 'size': (2400, 1400)}),
           ('hero', {'assemblies': HANDHELD_GROUPS, 'normal': (-.38, .50, 1.5), 'span': 165, 'size': (2400, 1400)}),
           ('back', {'assemblies': HANDHELD_GROUPS, 'normal': (0, 0, -1), 'span': 165, 'size': (2400, 1400)})])
