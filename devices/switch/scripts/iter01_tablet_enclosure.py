from pathlib import Path
exec(compile((Path((globals().get('PROJECT_ROOT') or str(Path(__file__).resolve().parents[1])))/'scripts/common.py').read_bytes(),'common.py','exec'))
D=App.newDocument('NintendoSwitch');D.Label='Nintendo Switch · 标准版详细装配'
Gui.activateWorkbench('PartDesignWorkbench');Gui.runCommand('Std_DrawStyle',5)
PARAM=D.addObject('Spreadsheet::Sheet','Parameters');PARAM.Label='尺寸参数 · mm'
PARAM.set('A1','参数');PARAM.set('B1','值');PARAM.set('C1','依据')
for i,(alias,val,note) in enumerate([('TabletWidth',173,'官方单机宽'),('TabletHeight',101,'官方单机高'),('BodyDepth',13.9,'官方主体厚'),('OverallWidth',239,'含手柄官方宽'),('JoyHeight',102,'手柄官方高'),('JoyWidth',35.9,'含滑轨官方宽'),('TotalDepth',28.4,'摇杆至扳机官方厚'),('ShellWall',1.1,'局部近似'),('StickProjection',9.1,'局部近似')],2):
    PARAM.set(f'A{i}',alias);PARAM.set(f'B{i}',str(val)+' mm');PARAM.setAlias(f'B{i}',alias);PARAM.set(f'C{i}',note)
PARAM.setColumnWidth('A',175);PARAM.setColumnWidth('B',110);PARAM.setColumnWidth('C',200);PARAM.setStyle('A1:C1','bold','add');D.recompute()
outer=rounded_body(D,'FrameBlank','主机框架原坯',173,101,3.8,12.15,origin=(0,0,1.05),color=PALETTE['shell'],expr={'Width':'Parameters.TabletWidth','Height':'Parameters.TabletHeight'})
register(outer,'TabletFrame','Tablet',0,'shell')
cut('TabletFrame',rr_shape(169.8,97.8,2.5,12.6,(0,0,.9)),'主机框架内腔')
# Small edge breaks on the native frame, with front/rear cover seats.
cut('TabletFrame',[rr_shape(171.4,99.4,3.1,.45,(0,0,12.9)),rr_shape(170.9,98.9,2.8,.4,(0,0,.95))],'前后盖定位台阶')
rear=rounded_body(D,'RearBlank','主机后壳原坯',172.8,100.8,3.7,1.04,origin=(0,0,0),color=PALETTE['shell'])
register(rear,'TabletRear','Tablet',-5,'shell')
# Back cover is a molded plate with a shallow inner recess and perimeter lip.
cut('TabletRear',rr_shape(168.8,96.8,2.2,.40,(0,0,.70)),'后壳内面浅腔')
RESULT=stage_done(1,'tablet_enclosure','建立官方 173 × 101 × 13.9 mm 单机基准、参数化框架、空腔、前后盖安装台阶及独立后壳。',extra={'published_tablet_dimensions_mm':[173,101,13.9]})
