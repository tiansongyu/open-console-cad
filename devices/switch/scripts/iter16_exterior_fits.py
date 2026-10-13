"""Fit the revised exterior to retained schematic internal components."""

# These adjustments follow the independent iteration-15 Boolean audit.
exterior_move('JoyLPot0', (-.85, 0, 0))
for tag in ['L', 'R']:
    for j in range(4):
        key = 'Joy' + tag + 'Boss' + str(j)
        exterior_move(key, (0, 0, .07))
        exterior_revision(key, C[key].Shape.cut(C['Joy' + tag + 'Rear'].Shape),
                          '螺钉柱底面贴合后壳内圆角')
    cut('Joy' + tag + 'Bumper', C['BumperLegend' + tag].Shape,
        '肩键字样凹嵌，消除实体重叠')
for suffix in ['HapticCase', 'HapticMass', 'HapticCoil', 'HapticSpring0', 'HapticSpring1']:
    exterior_move('JoyR' + suffix, (0, 4.0, 0))
for key in ['IRCameraPCB', 'IRCameraSensor', 'IRCameraLens']:
    exterior_move(key, (-6.5, .7, 0))
D.recompute()

# The factory front view shows two low speaker apertures and the light
# sensor below the display. Retain four independent grille half-sections.
bezel = rr_shape(171.0, 99.0, 3.1, .7, (0, 0, 13.2))
bezel = roll_face(bezel, 13.9, .16)
bezel = bezel.cut(rr_shape(active_w + .14, active_h + .14, .35, 1.2, (0, 0, 13.0)))
for side in [-1, 1]:
    bezel = bezel.cut(rr_shape(8.8, .95, .45, 1.2, (side * 65.5, -47.2, 13.0)))
    for j in range(2):
        mesh = rr_shape(8.9, 1.05, .48, .14, (side * 65.5, -47.2, 13.0))
        half = Part.makeBox(4.5, 2, 1, vec(side * 65.5 - 4.5 + j * 4.5, -48.2, 12.9))
        exterior_revision('SpeakerMesh' + str(side) + '_' + str(j), mesh.common(half),
                          '前下缘扬声器格栅半片')
exterior_move('AmbientSensorWindow', (51.6, -14.3, 0))
bezel = bezel.cut(Part.makeCylinder(.8, 1.2, vec(-25, -43.5, 13.0)))
exterior_revision('FrontBezel', bezel, '官方位置的双扬声器孔和下方亮度传感器')

# Shaded surfaces suppress tangent construction edges without changing BRep.
for obj in C.values():
    obj.ViewObject.DisplayMode = 'Shaded'
    obj.ViewObject.Deviation = .025
    obj.ViewObject.AngularDeflection = 6
D.recompute()
RESULT = stage_done(16, 'exterior_fit_verification',
    '修正曲面版本的螺钉柱、振动模块、摇杆传感器与排线、IR 光学组件及肩键字样配合；'
    '按官方正视图修正扬声器和亮度传感器位置。',
    views=[('front', {'assemblies': HANDHELD_GROUPS, 'span': 165, 'size': (2400, 1400)}),
           ('hero', {'assemblies': HANDHELD_GROUPS, 'normal': (-.38, .50, 1.5), 'span': 165, 'size': (2400, 1400)}),
           ('back', {'assemblies': HANDHELD_GROUPS, 'normal': (0, 0, -1), 'span': 165, 'size': (2400, 1400)})])
