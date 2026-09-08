exec('def joy_outline_shape'+(ROOT/'scripts/common.py').read_text().split('def joy_outline_shape',1)[1])
for side,tag,material in [(-1,'L','blue'),(1,'R','red')]:
    assembly='JoyLeft' if side<0 else 'JoyRight';x=side*103.0
    joy_body('Joy'+tag+'Front','Joy-Con '+tag+' · 前壳',side,6.4,7.5,material)
    cut('Joy'+tag+'Front',joy_outline_shape(30.4,99.4,14.5,.8,5.3,(x,0,7.35),side),'前壳内腔')
    joy_body('Joy'+tag+'Rear','Joy-Con '+tag+' · 后壳',side,8.6,-1.3,material)
    cut('Joy'+tag+'Rear',joy_outline_shape(30.4,99.4,14.5,.8,7.7,(x,0,-.30),side),'后壳内腔')
    # Slim black seam follows the molded shell without filling the cavity.
    seam=joy_outline_shape(32.55,101.55,15.55,1.7,.12,(x,0,7.33),side).cut(joy_outline_shape(30.4,99.4,14.5,.8,.4,(x,0,7.2),side))
    feature('Joy'+tag+'Seam','Joy-Con '+tag+' · 分型缝边条',seam,assembly,0,'black')
    # Sliding tongue is nested in the console's U-shaped rail, with finite clearance.
    def mir(s):return s.mirror(vec(),vec(1,0,0)) if side<0 else s
    tongue=Part.makeBox(1.70,89.6,6.9,vec(84.1,-44.8,3.7))
    shoulder=Part.makeBox(.60,90.2,7.6,vec(85.90,-45.1,3.4))
    feature('Joy'+tag+'RailTongue','Joy-Con '+tag+' · 金属插入导轨',mir(tongue),'JoyRail'+tag,0,'metal')
    feature('Joy'+tag+'RailBack','Joy-Con '+tag+' · 内侧导轨底条',mir(shoulder),'JoyRail'+tag,0,'black')
    for j in range(10):
        pad=Part.makeBox(.035,1.74,.32,vec(84.045,-44.77,3.66+j*.63))
        feature(f'Joy{tag}Contact{j+1}','Joy-Con 导轨连接触点',mir(pad),'JoyRail'+tag,0,'gold')
RESULT=stage_done(5,'joycon_split_shells','建立红蓝 Joy-Con 非对称圆角外轮廓、原生草图与凸台、独立空心前后壳、分型边缝和插入式金属导轨。',views=[('front',{}),('back',{'normal':(0,0,-1)}),('perspective',{'normal':(-.65,-.45,2)})],extra={'assembled_width_mm':239,'joycon_height_mm':102,'individual_width_including_rail_mm':35.9})
