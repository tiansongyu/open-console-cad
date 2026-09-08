# Resolve measured interference using purpose-specific seats and component placement.
for tag in ['L','R']:
    cut('DisplayBackplate',[C['ConsoleLiner'+tag].Shape,C['Joy'+tag+'MagneticSpine'].Shape],'显示背板磁吸连接区避让')
    cut('RearEMIShield',[C['ConsoleLiner'+tag].Shape,C['Joy'+tag+'MagneticSpine'].Shape],'屏蔽板磁吸连接区避让')
    cut('TabletFrame',C['Speaker'+tag+'MouthDuct'].Shape,'前向声道穿框通道')
    cut('Speaker'+tag+'LowerDuct',C['Speaker'+tag+'MouthDuct'].Shape,'水平与前向声道台阶接合')
    side=-1 if tag=='L' else 1
    def mirrored(s):return s.mirror(vec(),vec(1,0,0)) if side<0 else s
    for j,y in enumerate([-27,27]):
        C['Joy'+tag+'SteelTarget'+str(j)].Placement.Base+=vec(side*1.8,0,0)
        cut('Joy'+tag+'MagneticSpine',mirrored(rr_shape(6.4,17.8,.85,.95,(96.8,y,7),XROT)),'磁靶片移至侧键背后独立安装层')
    C['Joy'+tag+'Ejector1'].Shape=mirrored(rr_shape(3.5,2.0,.8,.75,(94.65,-41.9,7),XROT))
    cut('Joy'+tag+'MagneticSpine',mirrored(rr_shape(3.7,2.2,.85,1.1,(94.45,-41.9,7),XROT)),'下部磁吸顶脚滑动孔')
    cut('Joy'+tag+'Trigger',Part.makeCylinder(1.48,9,vec(side*104,47,-6.1)),'扳机上方后盖紧固件通孔')
    cut('Joy'+tag+'HapticCase',Part.makeCylinder(1.44,6,vec(side*104,-50,-.8)),'振动外壳安装柱避让')
cut('MicroSDPCB',C['ConsoleMagnetL0'].Shape,'microSD 小板磁体安装缺口')
for j in range(1,5):cut('RearBoss'+str(j),C['ConsoleLiner'+('L' if j%2 else 'R')].Shape,'后壳螺柱连接槽避让')
cut('TopControlFlex',C['ConsoleLinerL'].Shape,'顶部排线端头连接槽避让')
# The antenna now occupies a dedicated thin layer above the battery, below the LCD backplate.
C['AntennaLeft'].Shape=rr_shape(5.5,29,.6,.20,(-87.2,24,10.30))
cut('Mainboard',rr_shape(24.2,14.0,2.8,2.0,(76,-49.0,9.1)),'右扬声器模组与声道 PCB 缺口')
for key in ['Passive13','Passive13End-1','Passive13End1']:C[key].Placement.Base+=vec(3,0,0)
for key in ['Passive20','Passive20End-1','Passive20End1']:C[key].Placement.Base+=vec(0,-5,0)
cut('SoCThermalPad',C['SoCMark'].Shape,'封装标记接触层微量凹嵌')
cut('FanHousing',C['CopperHeatPipe'].Shape,'风扇侧缘热管通道')
cut('BatterySocket',[Part.makeCylinder(.35,4.8,vec(-24.6,-27.6+j*1.05,7.0),vec(1,0,0)) for j in range(4)],'电池连接线插接孔')
for j in range(1,5):cut('DockSpringPlatform',C['DockSpringRod'+str(j)].Shape,'浮动插头导杆压入孔')
cut('DockPlugInsulator',[C[f'DockPlugContact{row}_{j}'].Shape for row in [-1,1] for j in [0,11]],'USB-C 外侧触点绝缘嵌槽')
D.recompute()
RESULT=stage_done(13,'assembly_clearance_refinement','依据独立实体交集检查，分离磁吸钢片与侧键安装层，重置下顶脚和天线层，补齐显示背板、PCB、热管、声道及插接件避让。',views=[('handheld',{'assemblies':['Tablet','Display','TabletInternal','JoyLeft','JoyRight','JoyMountL','JoyMountR','JoyInternalL','JoyInternalR'],'normal':(-.4,-.4,2),'span':200}),('internal',{'assemblies':['Tablet','Display','TabletInternal','JoyLeft','JoyRight','JoyMountL','JoyMountR','JoyInternalL','JoyInternalR'],'normal':(0,0,-1),'span':200,'exclude':['TabletRear','Kickstand','StandFoot-1','StandFoot1','RearNintendoMark','RearModelMark','RearEMIShield','JoyLRear','JoyRRear']})])
print(json.dumps(RESULT,ensure_ascii=False))
