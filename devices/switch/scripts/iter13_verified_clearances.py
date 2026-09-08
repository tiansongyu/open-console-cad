App.setActiveDocument(D.Name)
shift('WiFiPackage',(-3,0,0))
for side,tag in [(-1,'L'),(1,'R')]:
    cut('Speaker'+tag+'Housing',Part.makeCylinder(1.64,4.0,vec(side*84,-37,7.15),vec(-side,0,0)),'扬声器外壳导轨安装柱容置槽')
    shift('Strap'+tag+'Cord',(0,2.9,0));shift('Strap'+tag+'CordLock',(0,2.9,0))
    cut('Strap'+tag+'Body',rr_shape(12,4,1,2.1,(side*105,-327-50.2,4.95)),'腕带织绳穿过锚环的通道')
RESULT=stage_done(13,'verified_assembly_clearances','完成无线封装与阻容间距、扬声器外壳固定柱槽、织绳锚环穿线路径三类最后配合修正。',views=[('front',{'assemblies':HANDHELD_GROUPS}),('internal',{'assemblies':HANDHELD_GROUPS,'normal':(0,0,-1),'exclude':['TabletRear','Kickstand','StandFoot','RearNintendoMark','RearModelMark','RearEMIShield','JoyLRear','JoyRRear']}),('straps',{'assemblies':['StrapL','StrapR'],'target':(0,-350,6),'span':150})])
