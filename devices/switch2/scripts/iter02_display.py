# Larger display and laminated front stack, keeping the published 13.9 mm body depth.
active_h=7.9*25.4/math.sqrt(16**2+9**2)*9;active_w=active_h*16/9
box('FrontBezel','前玻璃黑色边框',197.8,115.8,.70,(0,0,13.20),'Tablet',5,'bezel',5.0)
cut('FrontBezel',rr_shape(active_w+.16,active_h+.16,.7,.9,(0,0,13.10)),'7.9 英寸显示窗口')
box('DisplayGlass','显示与触控窗口',active_w,active_h,.60,(0,0,13.25),'Display',6,'screen',.6)
box('AntiShatterFilm','前表面防碎保护膜',active_w,active_h,.05,(0,0,13.85),'Display',7,'screen',.6)
box('LCDModule','7.9 英寸 LCD 模组',180.2,104,1.55,(0,0,11.50),'Display',4,'black',1.2,True)
box('DisplayBackplate','液晶模组金属背板',191,109.0,.52,(0,0,10.75),'Display',3,'metal',2.7,True)
# The loudspeaker mouths sit along the lower front edge, separate from bottom air intakes.
openings=[]
for side in [-1,1]:
 x=side*76.0;openings.append(rr_shape(16.5,1.5,.65,1.0,(x,-55.25,13.1)))
 mesh=rr_shape(16.3,1.3,.55,.20,(x,-55.25,13.2))
 holes=[Part.makeCylinder(.14,.35,vec(x-7.4+j*.52,-55.50+row*.50,13.10)) for row in range(2) for j in range(29)]
 feature('SpeakerMesh'+str(side),'前向扬声器微孔网',mesh.cut(Part.makeCompound(holes)),'Tablet',5,'black')
cut('FrontBezel',openings,'前向扬声器开口')
RESULT=stage_done(2,'large_display_stack','增加 7.9 英寸显示区域、独立防碎膜、LCD 与背板、两组前向扬声器开口及 116 个微孔。',views=[('front',{'span':185}),('perspective',{'normal':(-.5,-.4,2),'span':185})],extra={'display_active_mm':[active_w,active_h],'screen_diagonal_inches':7.9})
print(json.dumps(RESULT,ensure_ascii=False))
