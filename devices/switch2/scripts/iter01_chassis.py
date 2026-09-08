from pathlib import Path
import json
PROJECT_ROOT=(globals().get('PROJECT_ROOT') or str(Path(__file__).resolve().parents[1]))
HANDHELD_GROUPS=['Tablet','Display','TabletInternal','JoyLeft','JoyRight','JoyMountL','JoyMountR','JoyInternalL','JoyInternalR']
exec(compile((Path(PROJECT_ROOT)/'scripts/common.py').read_bytes(),'common.py','exec'))
D=App.newDocument('NintendoSwitch2');D.Label='Nintendo Switch 2 · BEE-001 详细设计'
Gui.runCommand('Std_DrawStyle',5)
PALETTE.update(shell=(.15,.16,.17),bezel=(.025,.027,.030),screen=(.055,.07,.08),blue=(.23,.66,.85),orange=(.97,.38,.27),black=(.055,.06,.065))
PARAM=D.addObject('Spreadsheet::Sheet','Parameters');PARAM.Label='尺寸 · 公开包络与近似细节'
PARAM.set('A1','参数');PARAM.set('B1','值');PARAM.set('C1','来源/说明')
rows=[('TabletWidth',198,'局部比例近似'),('TabletHeight',116,'整机公开高度'),('BodyDepth',13.9,'公开主体厚度'),('OverallWidth',272,'公开整机宽度'),('JoyHeight',116,'公开手柄高度'),('JoyWidth',41.4,'日文官网：含连接突起'),('TotalDepth',30.7,'公开摇杆至扳机厚'),('ShellWall',1.15,'本模型近似'),('StickProjection',10.8,'本模型近似')]
for i,(alias,value,note) in enumerate(rows,2):PARAM.set(f'A{i}',alias);PARAM.set(f'B{i}',str(value)+' mm');PARAM.setAlias(f'B{i}',alias);PARAM.set(f'C{i}',note)
PARAM.setColumnWidth('A',175);PARAM.setColumnWidth('B',110);PARAM.setColumnWidth('C',230);PARAM.setStyle('A1:C1','bold','add');D.recompute()
outer=rounded_body(D,'TabletBlank','主机金属框架原坯',198,116,5.1,12.2,(0,0,.95),color=PALETTE['shell'],expr={'Width':'Parameters.TabletWidth','Height':'Parameters.TabletHeight'})
register(outer,'TabletFrame','Tablet',0,'shell')
cut('TabletFrame',rr_shape(194.6,112.6,3.8,12.7,(0,0,.7)),'中框内腔')
cut('TabletFrame',[rr_shape(196.5,114.5,4.3,.5,(0,0,12.85)),rr_shape(196.2,114.2,4.2,.4,(0,0,.85))],'玻璃与后盖安装台阶')
back=rounded_body(D,'RearBlank','主机后壳',197.8,115.8,5.0,.94,(0,0,0),color=PALETTE['shell'])
register(back,'TabletRear','Tablet',-5,'shell')
cut('TabletRear',rr_shape(193.4,111.4,3.4,.35,(0,0,.64)),'后壳内表面凹腔')
# Deep rounded female connector wells distinguish the magnetic mounting system.
XROT=App.Rotation(vec(0,0,1),vec(1,0,0));YROT=App.Rotation(vec(0,0,1),vec(0,1,0));BACKROT=App.Rotation(vec(0,1,0),180)
for side in [-1,1]:
    cutter=rr_shape(10.4,104,5.0,5.2,(94.0,0,7),XROT)
    if side<0:cutter=cutter.mirror(vec(),vec(1,0,0))
    cut('TabletFrame',cutter,'磁吸连接器圆角凹槽')
RESULT=stage_done(1,'magnetic_chassis','建立 Switch 2 的独立参数框架、玻璃台阶、后盖及深圆角磁吸连接凹槽，整体宽度基准 272 mm。',views=[('front',{'span':185}),('chassis',{'normal':(-.7,-.4,2),'span':185})],extra={'reference':'BEE-001 launch model','tablet_width_is_approximate':True})
print(json.dumps(RESULT,ensure_ascii=False))
