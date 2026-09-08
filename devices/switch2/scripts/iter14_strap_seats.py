for tag in ['L','R']:
    a='Strap'+tag
    cut(a+'Frame',[C[a+'Light'+str(j)].Shape for j in range(4)],'腕带导光窗嵌槽')
    cut(a+'Frame',C[a+'Cord'].Shape,'按实际曲线绳路设置穿绳通道')
RESULT=stage_done(14,'strap_light_and_cord_seats','按腕带真实织绳路径完善底端穿绳通道，并补齐两套腕带的八个导光窗嵌槽。',views=[('straps',{'assemblies':['StrapL','StrapR'],'target':(-34,-422,3.5),'span':250,'size':(2200,1400)}),('back',{'assemblies':HANDHELD_GROUPS,'normal':(0,0,-1),'span':200})])
print(json.dumps(RESULT,ensure_ascii=False))
