exec('def joy_body'+(ROOT/'scripts/common.py').read_text().split('def joy_body',1)[1])
for side,tag,color in [(-1,'L','blue'),(1,'R','orange')]:
    assembly='JoyLeft' if side<0 else 'JoyRight';x=side*117.5
    joy_body('Joy'+tag+'Front','Joy-Con 2 '+tag+' 前壳',side,6.5,7.4,'shell')
    cut('Joy'+tag+'Front',joy_outline_shape(34.4,113.4,27.7,.65,5.35,(x,0,7.25),side),'前壳内腔')
    joy_body('Joy'+tag+'Rear','Joy-Con 2 '+tag+' 后壳',side,9.15,-1.9,'shell')
    cut('Joy'+tag+'Rear',joy_outline_shape(34.4,113.4,27.7,.65,8.4,(x,0,-.85),side),'后壳内腔')
    seam=joy_outline_shape(36.6,115.6,28.8,1.6,.08,(x,0,7.29),side).cut(joy_outline_shape(34.4,113.4,27.7,.65,.25,(x,0,7.2),side))
    feature('Joy'+tag+'Seam','手柄分型边缝',seam,assembly,0,'black')
    def mirror(shape):return shape.mirror(vec(),vec(1,0,0)) if side<0 else shape
    # Rounded male block nests in the tablet connector well; blue/orange remain separate materials.
    strip=rr_shape(9.8,103.4,4.7,4.2,(94.6,0,7.0),XROT)
    feature('Joy'+tag+'MagneticSpine','磁吸手柄彩色连接脊',mirror(strip),'JoyMount'+tag,0,color)
    # Female decorative liner remains with the console when the controller is removed.
    liner=rr_shape(9.9,103.5,4.75,.18,(94.16,0,7),XROT).cut(rr_shape(4.0,18.0,.5,.5,(94.05,0,7),XROT))
    feature('ConsoleLiner'+tag,'主机磁吸槽彩色内衬',mirror(liner),'Tablet',0,color)
    # Main console magnets and controller steel targets; local layout is schematic.
    for j,y in enumerate([-27,27]):
        magnet=rr_shape(6.4,18.0,.9,2.75,(91.15,y,7),XROT)
        feature('ConsoleMagnet'+tag+str(j),'主机磁吸磁体示意',mirror(magnet),'TabletInternal',0,'metal',True)
        target=rr_shape(6.2,17.6,.8,.75,(95.10,y,7),XROT)
        feature('Joy'+tag+'SteelTarget'+str(j),'手柄磁吸钢质靶片',mirror(target),'JoyInternal'+tag,0,'metal',True)
        cut('Joy'+tag+'MagneticSpine',mirror(rr_shape(6.4,17.8,.85,.95,(95.0,y,7),XROT)),'钢质靶片安装槽')
    # Central matching contact carriers, each with thirteen individually modeled gold pads.
    receiver=rr_shape(3.75,17.6,.5,.20,(94.36,0,7),XROT)
    feature('ConsoleConnector'+tag,'主机磁吸多触点接插件',mirror(receiver),'Tablet',0,'black')
    male=rr_shape(3.70,17.5,.45,.50,(94.64,0,7),XROT)
    cut('Joy'+tag+'MagneticSpine',mirror(rr_shape(3.95,17.8,.55,.85,(94.45,0,7),XROT)),'手柄接插件座')
    feature('Joy'+tag+'Connector','手柄多触点接插件',mirror(male),'JoyMount'+tag,0,'black')
    for j in range(13):
        pad=Part.makeBox(.025,.72,1.85,vec(94.568,-7.6+j*1.20,6.075))
        feature(f'ConsoleContact{tag}{j+1}','主机连接触点示意',mirror(pad),'Tablet',0,'gold')
        pad=Part.makeBox(.020,.72,1.80,vec(94.611,-7.6+j*1.20,6.10))
        feature(f'Joy{tag}Contact{j+1}','手柄连接触点示意',mirror(pad),'JoyMount'+tag,0,'gold')
RESULT=stage_done(5,'joycon2_magnetic_shells','建立更圆润的黑色手柄空心前后壳、蓝/橙连接脊、主机槽内衬、磁体与钢片，以及分离的多触点接插件。',views=[('front',{'span':200}),('back',{'normal':(0,0,-1),'span':200}),('perspective',{'normal':(-.45,-.4,2),'span':200})])
print(json.dumps(RESULT,ensure_ascii=False))
