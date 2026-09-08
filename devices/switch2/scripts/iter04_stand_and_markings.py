exec('def official_logo'+(ROOT/'scripts/common.py').read_text().split('def official_logo',1)[1].split('def joy_outline_shape',1)[0])
# Wide U-shaped kickstand with a modeled recessed seat and independent hinge hardware.
outer=rr_shape(183,59,9.0,1.15,(0,-27.2,0))
inner=rr_shape(168,57,4.6,1.6,(0,-21.3,-.2))
stand=outer.cut(inner)
feature('Kickstand','U 形金属支架',stand,'Tablet',-6,'shell')
pocket=rr_shape(183.5,59.5,9.25,1.6,(0,-27.2,-.1)).cut(rr_shape(167.6,57,4.4,2,(0,-21.3,-.3)))
cut('TabletRear',pocket,'U 形支架嵌入位')
cut('TabletFrame',pocket,'支架底缘框架配合')
# Bearing bores and transverse pins are placed wholly inside the back envelope.
for side in [-1,1]:
    x=side*87
    ringpart('StandHinge'+str(side),'支架转轴套',1.10,.55,7.0,(x-3.5,.70,2.40),'Tablet',-4,'metal',axis=(1,0,0))
    cyl('StandPin'+str(side),'支架转轴销',.50,7.4,(x-3.7,.70,2.40),'Tablet',-4,'metal',axis=(1,0,0))
    box('StandMount'+str(side),'支架铰链安装块',7.4,5.0,.9,(x,.7,3.55),'TabletInternal',-3,'metal',.8,True)
    cut('Kickstand',rr_shape(18.4,4.9,.8,.20,(side*59,-53.3,-.03)),'防滑垫安装槽')
    box('StandFoot'+str(side),'支架防滑垫',18,4.5,.12,(side*59,-53.3,.02),'Tablet',-6,'rubber',.6)
# microSD Express reader under the left folded leg, opposite the original Switch layout.
box('MicroSDPCB','microSD Express 小板',16,22,.70,(-85,-22,3.35),'TabletInternal',-3,'pcb',.8,True)
box('MicroSDCage','microSD Express 金属卡座',13,16,1.4,(-85,-22,1.75),'TabletInternal',-3,'metal',.5,True)
cut('MicroSDCage',rr_shape(11.5,16.4,.25,.92,(-85,-22,2.00)),'microSD 卡片通道')
box('MicroSDCard','microSD Express 示意卡片',10.9,14.7,.70,(-85,-22.4,2.08),'TabletInternal',-3,'black',.2,True)
for j in range(8):box('MicroSDPad'+str(j),'存储卡接点',.62,2.6,.04,(-88.5+j,-16.8,2.81),'TabletInternal',-3,'gold',.04,True)
# Rear service fasteners, with counterbores and matching mounting bosses.
holes=[]
for j,(x,y) in enumerate([(-93,-51),(93,-51),(-93,51),(93,51)],1):
    holes.extend([Part.makeCylinder(1.58,.62,vec(x,y,-.05)),Part.makeCylinder(.86,1.2,vec(x,y,-.05))])
    screw('RearScrew'+str(j),(x,y,.02),'Tablet',-5,radius=1.45,length=3.6,drive='cross')
    ringpart('RearBoss'+str(j),'后壳固定柱',1.55,.84,3.5,(x,y,1.05),'TabletInternal',-3,'shell',internal=True)
cut('TabletRear',holes,'后壳螺钉沉孔')
# Exact official vector mark, placed as a flush printed inlay.
official_logo('RearNintendoMark',40,(0,12,.018),'Tablet',-5,'white',BACKROT)
cut('TabletRear',C['RearNintendoMark'].Shape,'背面官方标識凹嵌')
textpart('RearModelMark','BEE-001   CAD STUDY',1.7,(23,-24,.012),'Tablet',-5,'white',BACKROT)
cut('TabletRear',C['RearModelMark'].Shape,'型号字样凹嵌')
RESULT=stage_done(4,'u_stand_and_rear_details','建立宽 U 形支架、铰链和固定柱、左侧 microSD Express 卡座，以及官网矢量背面标识和服务螺钉。',views=[('back',{'normal':(0,0,-1),'span':185}),('rear_detail',{'normal':(.5,-.4,-2),'span':185}),('reader',{'normal':(0,0,-1),'target':(-84,-22,2),'span':48,'exclude':['Kickstand']})])
print(json.dumps(RESULT,ensure_ascii=False))
