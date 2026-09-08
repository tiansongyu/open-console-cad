# Display stack, front molding and real speaker/sensor openings.
box('FrontBezel','前面板黑色边框',172.8,100.8,.7,(0,0,13.2),'Tablet',5,'bezel',3.7)
active_h=6.2*25.4/math.sqrt(16*16+9*9)*9;active_w=active_h*16/9
cut('FrontBezel',rr_shape(active_w+.14,active_h+.14,.35,.9,(0,0,13.1)),'显示区开口')
box('DisplayGlass','触控显示窗口',active_w,active_h,.65,(0,0,13.25),'Display',6,'screen',.3)
box('LCDModule','6.2 英寸 LCD 模组',143.0,83.0,1.7,(0,0,11.45),'Display',4,'black',.65,True)
box('DisplayBackplate','显示模组金属背板',166.5,94,.50,(0,0,10.85),'Display',3,'metal',1.7,True)
# Four slit apertures, two per stereo channel, and a recessed perforated screen.
holes=[]
for side in [-1,1]:
    for j in range(2):
        x=side*(57.5+j*11.5)
        holes.append(rr_shape(9.4,1.0,.45,1.1,(x,-44.0,13.0)))
        mesh=rr_shape(9.5,1.1,.5,.18,(x,-44,13.0))
        drill=[Part.makeCylinder(.10,.3,vec(x-4.15+k*.38,-44,12.95)) for k in range(23)]
        feature(f'SpeakerMesh{side}_{j}','前扬声器防尘网',mesh.cut(Part.makeCompound(drill)),'Tablet',5,'black')
cut('FrontBezel',holes,'立体声扬声器音孔')
cut('FrontBezel',Part.makeCylinder(.8,1.0,vec(-76.6,-29.2,13.0)),'亮度传感器开口')
cyl('AmbientSensorWindow','环境亮度感应窗',.73,.64,(-76.6,-29.2,13.2),'Tablet',5,'screen')
RESULT=stage_done(2,'display_stack','增加触控窗口、6.2 英寸 LCD、显示背板、立体声狭缝与 92 个声学网孔、环境亮度感应窗。',extra={'active_display_mm':[active_w,active_h],'diagonal_inches':6.2})
