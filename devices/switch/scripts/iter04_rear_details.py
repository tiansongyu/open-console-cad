exec('def screw'+(ROOT/'scripts/common.py').read_text().split('def screw',1)[1])
# Rear kickstand, independent hinge and card reader underneath.
cut('TabletRear',rr_shape(21.4,58.0,2.3,1.4,(65,-20.6,-.1)),'支架收纳位')
box('Kickstand','后置翻折支架',21.0,57.6,.72,(65,-20.6,.02),'Tablet',-6,'shell',2.1)
box('StandRecess','支架底部收纳槽',21.2,58.0,.45,(65,-20.6,1.15),'Tablet',-4,'black',2.2)
cut('StandRecess',rr_shape(14.0,4.0,.6,.7,(65,-43.6,1.0)),'microSD 读卡器开口')
for j,x in enumerate([57.0,65.0,73.0]):
    ringpart('StandHinge'+str(j),'支架铰链节',1.0,.51,5.6,(x-2.8,7.3,1.8),'Tablet',-6,'metal',axis=(1,0,0))
cyl('StandHingePin','支架铰链销轴',.48,21.5,(54.3,7.3,1.8),'Tablet',-6,'metal',axis=(1,0,0))
box('StandFoot','支架底缘防滑垫',16.5,2.2,.11,(65,-47.9,-.09),'Tablet',-6,'rubber',.6)
box('MicroSDCage','microSD 卡座金属屏蔽',13.4,13.8,1.2,(65,-39,1.7),'TabletInternal',-3,'metal',.4,True)
cut('MicroSDCage',rr_shape(11.5,13.9,.2,.86,(65,-39,1.88)),'microSD 插入腔')
box('MicroSDCard','microSD 卡片示意',10.9,14.8,.69,(65,-38.8,1.97),'TabletInternal',-3,'black',.2,True)
for j in range(8):box('MicroSDPad'+str(j),'microSD 镀金触点',.70,3.0,.03,(61.5+j,-33,2.67),'TabletInternal',-3,'gold',.04,True)
# Twin rear intake banks with a real staggered perforation pattern.
vent_tools=[]
for side in [-1,1]:
    x=side*28.8;vent_tools.append(rr_shape(42.0,3.8,1.8,1.3,(x,-40.5,-.1)))
    mesh=rr_shape(41.8,3.6,1.7,.24,(x,-40.5,.12))
    drill=[Part.makeCylinder(.28,.5,vec(x-19.5+j*.80+(row%2)*.4,-41.55+row*1.0,.02)) for row in range(3) for j in range(49)]
    feature('RearIntakeMesh'+str(side),'后盖进风防尘网',mesh.cut(Part.makeCompound(drill)),'Tablet',-5,'black')
cut('TabletRear',vent_tools,'后置进风口')
# Four serviceable tri-point screws and matching bosses.
screwtools=[]
for i,(x,y) in enumerate([(-80.5,-45.2),(80.5,-45.2),(-80.5,45.2),(80.5,45.2)],1):
    screwtools.extend([Part.makeCylinder(1.72,.52,vec(x,y,-.05)),Part.makeCylinder(.89,1.4,vec(x,y,-.05))])
    screw('RearScrew'+str(i),(x,y,.04))
    ringpart('RearBoss'+str(i),'后壳螺钉支柱',1.60,.86,3.6,(x,y,1.1),'TabletInternal',-2,'shell',internal=True)
cut('TabletRear',screwtools,'后盖三翼螺钉沉孔')
BACKROT=App.Rotation(vec(0,1,0),180)
official_logo('RearNintendoMark',36,(0,3,-.019),orientation=BACKROT)
textpart('RearModelMark','HAC-001   |   CAD STUDY',1.8,(40,-34.8,-.02),'Tablet',-5,'white',BACKROT)
# Serial zone is a study label, not an invented device serial number.
box('BottomLabel','底部识别标签',23,3.0,.018,(-56,-50.515,6.7),'Tablet',0,'white',.2,orient=YROT)
textpart('BottomLabelText','SWITCH CAD',1.35,(-65.4,-50.535,7.25),'Tablet',0,'black',YROT)
RESULT=stage_done(4,'stand_and_rear','增加可分离后支架与铰链、microSD 卡座和触点、294 个进风网孔、三翼螺钉及官网 SVG 背面标识。',views=[('back',{'normal':(0,0,-1)}),('rear_perspective',{'normal':(-.7,-.4,-2)}),('stand_open_detail',{'normal':(0,0,-1),'target':(64,-24,1),'span':76,'exclude':['Kickstand','StandFoot']})])
