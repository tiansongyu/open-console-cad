HANDHELD_GROUPS=['Tablet','Display','TabletInternal','JoyLeft','JoyRight','JoyMountL','JoyMountR','JoyInternalL','JoyInternalR']
import ImportGui,re,csv
from collections import Counter
App.setActiveDocument(D.Name)
exec(compile((ROOT/'scripts/exploded_layout.py').read_bytes(),'exploded_layout.py','exec'))
# Stable numbers link model tree, bill of materials and drawing balloons.
for i,o in enumerate(C.values(),1):
    if 'PartNumber' not in o.PropertiesList:o.addProperty('App::PropertyString','PartNumber','CAD study')
    o.PartNumber=f'SW2-{i:04d}'
    label=re.sub(r'\d{3,}$','',re.sub(r'^SW2-\d+ · ','',o.Label)).replace('主机框架原坯','主机框架').replace(' · 原坯','')
    o.Label=o.PartNumber+' · '+label
visible(HANDHELD_GROUPS);camera((-.45,-.4,2),target=(0,0,7),span=200)
D.Label='Nintendo Switch 2 · 完整套装 · 参数化'
D.saveAs(str(OUT/'Switch2_Complete.FCStd'))
FINAL_VIEWS={}
settings=[('front',{'assemblies':HANDHELD_GROUPS}),('back',{'assemblies':HANDHELD_GROUPS,'normal':(0,0,-1)}),('hero',{'assemblies':HANDHELD_GROUPS,'normal':(-.45,-.4,2)}),('hero_back',{'assemblies':HANDHELD_GROUPS,'normal':(.45,-.4,-2)}),
('top',{'assemblies':HANDHELD_GROUPS,'normal':(0,1,.12),'up':(0,0,1),'target':(0,56,7),'span':57,'size':(2400,650)}),
('bottom',{'assemblies':HANDHELD_GROUPS,'normal':(0,-1,.12),'up':(0,0,1),'target':(0,-56,7),'span':57,'size':(2400,650)}),
('internal',{'assemblies':HANDHELD_GROUPS,'normal':(0,0,-1),'exclude':['TabletRear','Kickstand','StandFoot-1','StandFoot1','RearNintendoMark','RearModelMark','RearEMIShield','JoyLRear','JoyRRear']}),
('cooling',{'assemblies':HANDHELD_GROUPS,'normal':(0,0,-1),'exclude':['TabletRear','Kickstand','StandFoot-1','StandFoot1','RearNintendoMark','RearModelMark','RearEMIShield'],'target':(38,16,5),'span':120,'size':(1500,1400)}),
('usb_detail',{'assemblies':HANDHELD_GROUPS,'normal':(.2,-1,.18),'up':(0,0,1),'target':(0,-58,7),'span':14,'size':(1500,850)}),
('dock',{'assemblies':['Dock','DockInternal'],'normal':(-.65,.3,2),'target':(0,DOCK_Y,0),'span':175}),
('dock_open',{'assemblies':['Dock','DockInternal'],'normal':(-.35,.2,-2),'target':(0,DOCK_Y,0),'span':175,'exclude':['DockBackCover']}),
('grip',{'assemblies':['Grip'],'normal':(-.6,-.25,2),'target':(GRIP_X,GRIP_Y,0),'span':145}),
('straps',{'assemblies':['StrapL','StrapR'],'target':(-34,-422,3.5),'span':250})]
for name,options in settings:
    options.setdefault('span',200)
    FINAL_VIEWS[name]=snap('final_'+name,**options)
visible(HANDHELD_GROUPS);camera((-.45,-.4,2),target=(0,0,7),span=200);D.save()
# One independent exploded document holds all the kit parts with traceable offsets.
E=App.newDocument('Switch2Exploded');E.Label='Nintendo Switch 2 · 分层拆解'
EC={};EG={};OFFSET={}
for key,src in C.items():
    layer=src.ExplodeLayer;assembly=src.Assembly
    delta=exploded_offset(key,src)
    if assembly not in EG:
        EG[assembly]=E.addObject('App::DocumentObjectGroup',assembly+'Group');EG[assembly].Label=assembly
    s=src.Shape.copy();s.translate(delta)
    o=part_feature(E,src.Name,src.Label,s);EG[assembly].addObject(o)
    o.ViewObject.ShapeAppearance=src.ViewObject.ShapeAppearance
    for name in ['PartID','PartNumber','Assembly','MaterialDescription','Fidelity']:
        o.addProperty('App::PropertyString',name,'Trace');setattr(o,name,getattr(src,name))
    o.addProperty('App::PropertyVector','ExplodeOffset','Trace');o.ExplodeOffset=delta
    o.addProperty('App::PropertyInteger','ExplodeLayer','Trace');o.ExplodeLayer=layer
    EC[key]=o;OFFSET[key]=[delta.x,delta.y,delta.z]
E.recompute()
def eview(name,assemblies,normal=(1,-.2,1.5),target=(0,0,-10),span=280,size=(2400,1400)):
    App.setActiveDocument(E.Name)
    for o in EC.values():o.Visibility=o.Assembly in assemblies
    q=rotation(normal);sh=Part.makeCompound([o.Shape for o in EC.values() if o.Assembly in assemblies])
    sh.Placement=App.Placement(vec(),q.inverted()).multiply(sh.Placement)
    bounds=sh.optimalBoundingBox(False,False)
    target=tuple(q.multVec(bounds.Center));span=max(bounds.YLength,bounds.XLength*size[1]/size[0])*1.14
    return render(OUT/'previews'/('final_'+name+'.png'),normal=normal,target=target,span=span,size=size)
for name,options in EXPLODED_CAMERAS.items():FINAL_VIEWS[name]=eview(name,**options)
eview('exploded_handheld',**EXPLODED_CAMERAS['exploded_handheld'])
E.saveAs(str(OUT/'Switch2_Exploded.FCStd'))
# Explicit object lists prevent construction history from leaking into exports.
ImportGui.export(list(C.values()),str(OUT/'Switch2_FullKit.step'))
ImportGui.export([o for o in C.values() if o.Assembly in HANDHELD_GROUPS],str(OUT/'Switch2_Handheld.step'))
ImportGui.export([o for o in C.values() if o.Assembly in ['Dock','DockInternal']],str(OUT/'Switch2_Dock.step'))
ImportGui.export(list(EC.values()),str(OUT/'Switch2_Exploded.step'))
rows=audit_objects(list(C.values()));erows=audit_objects(list(EC.values()))
for row,o in zip(rows,C.values()):row.update(part_id=o.PartID,part_number=o.PartNumber,assembly=o.Assembly,layer=o.ExplodeLayer,material=o.MaterialDescription,fidelity=o.Fidelity)
for row,o in zip(erows,EC.values()):row.update(part_id=o.PartID,part_number=o.PartNumber,assembly=o.Assembly,explode_offset=OFFSET[o.PartID])
manifest={'project':'Nintendo Switch 2 BEE-001 launch model study','design_iterations':15,'physical_components':len(C),'solids':sum(len(o.Shape.Solids) for o in C.values()),'assemblies':dict(Counter(o.Assembly for o in C.values())),'handheld_groups':HANDHELD_GROUPS,'native_files':['Switch2_Complete.FCStd','Switch2_Exploded.FCStd'],'step_files':['Switch2_FullKit.step','Switch2_Handheld.step','Switch2_Dock.step','Switch2_Exploded.step'],'views':FINAL_VIEWS,'objects':rows,'exploded_objects':erows,'offsets':OFFSET,'published_handheld_mm':[272,116,30.7],'published_main_body_depth_mm':13.9,'published_dock_mm':[201,115,51.2],'fidelity':'Published overall envelopes; local dimensions approximate; major internals schematic'}
(OUT/'reports/final_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
with (OUT/'COMPONENTS.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f);w.writerow(['Part number','Part ID','Label','Assembly','Material','Solid count','Volume mm3','X mm','Y mm','Z mm','Fidelity'])
    for o in C.values():
        bb=o.Shape.optimalBoundingBox(False,False);w.writerow([o.PartNumber,o.PartID,o.Label,o.Assembly,o.MaterialDescription,len(o.Shape.Solids),o.Shape.Volume,bb.XLength,bb.YLength,bb.ZLength,o.Fidelity])
App.setActiveDocument(D.Name);visible(HANDHELD_GROUPS);camera((-.45,-.4,2),target=(0,0,7),span=200)
RESULT={k:v for k,v in manifest.items() if k not in ['objects','exploded_objects','offsets','views']}

print(json.dumps(RESULT,ensure_ascii=False))
