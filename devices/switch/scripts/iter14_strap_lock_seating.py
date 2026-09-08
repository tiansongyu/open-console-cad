App.setActiveDocument(D.Name)
for side,tag in [(-1,'L'),(1,'R')]:
    xx=side*105+18*math.sqrt(1-(18/31)**2);yy=-327-63.1
    revise('Strap'+tag+'CordLock',rr_shape(5.2,7,1,4,(xx,yy,4)),'调节扣沿织绳一侧就位')
    cut('Strap'+tag+'CordLock',C['Strap'+tag+'Cord'].Shape,'与当前织绳位置匹配的穿孔')
RESULT=stage_done(14,'strap_lock_seating','把腕带调节扣沿织绳侧段就位，并按当前绳路重做穿孔，消除锁扣与锚环、腕带壳体的重叠。',views=[('straps',{'assemblies':['StrapL','StrapR'],'target':(0,-350,6),'span':150}),('front',{'assemblies':HANDHELD_GROUPS})])
