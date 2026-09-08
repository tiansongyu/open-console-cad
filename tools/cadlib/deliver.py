"""Save self-contained native assemblies, exact STEP and traceable exploded views."""
import json,re,csv,hashlib
from pathlib import Path
from collections import Counter
import FreeCAD as App
import FreeCADGui as Gui
import Part,ImportGui
from . import geometry as g
V=g.vec


def finalize(m):
    p=m.profile;out=m.out;prefix=p['prefix'];main_groups=[a for a in m.groups if a not in ['Accessories','Cradle','Construction']]
    for i,o in enumerate(m.parts.values(),1):
        if 'PartNumber' not in o.PropertiesList:o.addProperty('App::PropertyString','PartNumber','Study')
        o.PartNumber=p['id'].upper()+f'-{i:04d}';o.Label=o.PartNumber+' · '+re.sub(r'^\S+-\d{4} · ','',o.Label)
    m.set_pose(p.get('default_opening',180));m.doc.Label=p['title']+' · complete CAD study'
    info=m.doc.getObject('StudyInfo') or m.doc.addObject('App::FeaturePython','StudyInfo')
    for key,typ in [('ProfileJSON','App::PropertyString'),('HingePivot','App::PropertyVector'),('OpeningDegrees','App::PropertyFloat'),('SourceDigest','App::PropertyString')]:
        if key not in info.PropertiesList:info.addProperty(typ,key,'Provenance')
    info.ProfileJSON=json.dumps(p,ensure_ascii=False);info.HingePivot=V(0,p.get('hinge_y',0),p.get('hinge_z',0));info.OpeningDegrees=p.get('default_opening',180)
    sources=sorted((m.root/'scripts').glob('iter*.py'))+sorted((m.repo/'tools/cadlib').glob('*.py'))
    info.SourceDigest=hashlib.sha256(b''.join(s.read_bytes() for s in sources)).hexdigest()
    views={}
    settings=[('hero',dict()),('front',dict(normal=(0,0,1))),('back',dict(normal=(0,0,-1))),('internal',dict(normal=(.2,-.3,-2),exclude=['BackCover','BatteryDoor','BatteryDoorScrew','RearSupportPlate','EMIShield','LidBackCover','RearModelMark','UpperModelMark','UpperPanelIcon0','UpperPanelIcon1'])),('controls',dict(normal=(0,0,1),assemblies=['Controls','Internal'])),('accessories',dict(assemblies=['Accessories','Cradle'],normal=(-.4,-.8,2)))]
    for name,kw in settings:
        kw.setdefault('assemblies',main_groups);views[name]=m.snapshot('final_'+name,**kw)
    m.snapshot('final_hero',assemblies=main_groups);m.doc.saveAs(str(out/(prefix+'_Complete.FCStd')))
    if p['family']=='clamshell':
        m.set_pose(0);views['closed']=m.snapshot('final_closed',normal=(.3,-.5,2),assemblies=main_groups)
        m.doc.saveCopy(str(out/(prefix+'_Closed.FCStd')))
        ImportGui.export([o for o in m.parts.values() if o.Assembly in main_groups],str(out/(prefix+'_Closed.step')))
        closed_shapes=[o.Shape.copy() for o in m.parts.values() if o.Assembly in main_groups]
        m.set_pose(p['default_opening'])
    else:closed_shapes=[o.Shape.copy() for o in m.parts.values() if o.Assembly in main_groups]
    envelope=Part.makeCompound(closed_shapes).optimalBoundingBox(False,False)
    m.visible(main_groups);m.snapshot('final_hero',assemblies=main_groups);m.doc.save()
    exploded=App.newDocument(prefix+'Exploded');exploded.Label=p['title']+' · exploded assembly'
    ec={};offsets={};groups={}
    rotation=App.Rotation(V(1,0,0),180-p.get('default_opening',180))
    for key,src in m.parts.items():
        layer=src.ExplodeLayer
        if src.PoseGroup=='Lid':
            z={-6:-360,0:-160,1:-110,2:-60,3:-10,5:160,6:260,7:360}.get(layer,layer*60)
            z={'LidFrame':-160,'LidBackCover':-360,'UpperLCDBackplate':-60,'UpperLCD':40,'LidBezel':160,'ParallaxBarrier':260,'UpperGlass':360}.get(key,z)
            if key.startswith('OuterCameraRing') or key.startswith('OuterCameraLens'):z=-360
            if key.startswith('InnerCameraRing') or key.startswith('InnerCameraLens'):z=160
            delta=rotation.multVec(V(0,0,z))+V(0,280,0)
        else:
            z={-6:-350,-5:-250,-4:-140,-3:-100,-2:-40,0:0,1:30,2:70,3:110,4:210,5:270,6:300,7:410}.get(layer,layer*60)
            z={'MainFrame':0,'Mainboard':-40,'EMIShield':-200,'RearSupportPlate':-250,'BackCover':-350,'LowerLCDBackplate':40,'LowerLCD':110,'FrontDeck':210,'LowerDisplaySurround':270,'LowerTouchDigitizer':340,'LowerGlass':410}.get(key,z)
            delta=V(0,0,z)
        if src.Assembly=='Cradle':delta+=V(0,-70,0)
        if src.Assembly=='Accessories':delta+=V(-50,0,0)
        shape=src.Shape.copy();shape.translate(delta);o=g.part_feature(exploded,src.Name,src.Label,shape)
        o.ViewObject.ShapeAppearance=src.ViewObject.ShapeAppearance
        if src.Assembly not in groups:groups[src.Assembly]=exploded.addObject('App::DocumentObjectGroup',src.Assembly+'Group')
        groups[src.Assembly].addObject(o)
        for name in ['PartID','PartNumber','Assembly','MaterialDescription','Fidelity','PoseGroup']:
            o.addProperty('App::PropertyString',name,'Trace');setattr(o,name,getattr(src,name))
        o.addProperty('App::PropertyVector','ExplodeOffset','Trace');o.ExplodeOffset=delta
        offsets[key]=list(delta);ec[key]=o
    exploded.recompute();App.setActiveDocument(exploded.Name);Gui.activateView('Gui::View3DInventor',True)
    def render_exploded(name,assembly_list):
        selected=[o for o in ec.values() if o.Assembly in assembly_list]
        g.set_visible_components(exploded,selected)
        normal=(1.7,-.2,-1);q=g.rotation(normal);shape=Part.makeCompound([o.Shape for o in selected]);shape.Placement=App.Placement(V(),q.inverted()).multiply(shape.Placement)
        b=shape.optimalBoundingBox(False,False);size=(2300,1700);span=max(b.YLength,b.XLength*size[1]/size[0])*1.14
        return g.render(out/'previews'/('final_'+name+'.png'),normal=normal,target=tuple(q.multVec(b.Center)),span=span,size=size)
    views['exploded']=render_exploded('exploded',main_groups)
    views['exploded_lower']=render_exploded('exploded_lower',[a for a in main_groups if a not in ['Lid','LidDisplay','LidInternal']])
    views['exploded_upper']=render_exploded('exploded_upper',['Lid','LidDisplay','LidInternal'])
    render_exploded('exploded',main_groups);exploded.saveAs(str(out/(prefix+'_Exploded.FCStd')))
    ImportGui.export(list(m.parts.values()),str(out/(prefix+'_FullKit.step')))
    ImportGui.export([o for o in m.parts.values() if o.Assembly in main_groups],str(out/(prefix+'_Handheld.step')))
    ImportGui.export(list(ec.values()),str(out/(prefix+'_Exploded.step')))
    rows=g.audit_objects(list(m.parts.values()));erows=g.audit_objects(list(ec.values()))
    for row,o in zip(rows,m.parts.values()):row.update(part_id=o.PartID,part_number=o.PartNumber,assembly=o.Assembly,layer=o.ExplodeLayer,material=o.MaterialDescription,fidelity=o.Fidelity,pose_group=o.PoseGroup)
    for row,o in zip(erows,ec.values()):row.update(part_id=o.PartID,part_number=o.PartNumber,assembly=o.Assembly,explode_offset=offsets[o.PartID])
    native=[prefix+'_Complete.FCStd',prefix+'_Exploded.FCStd'];steps=[prefix+'_FullKit.step',prefix+'_Handheld.step',prefix+'_Exploded.step']
    if p['family']=='clamshell':native.append(prefix+'_Closed.FCStd');steps.append(prefix+'_Closed.step')
    report={'project':p['title']+' '+p['model'],'device':p['id'],'prefix':prefix,'design_iterations':p['stages'],'physical_components':len(m.parts),'solids':sum(len(o.Shape.Solids) for o in m.parts.values()),'assemblies':dict(Counter(o.Assembly for o in m.parts.values())),'handheld_groups':main_groups,'native_files':native,'step_files':steps,'views':{k:str(Path(v).relative_to(m.repo)) for k,v in views.items()},'objects':rows,'exploded_objects':erows,'offsets':offsets,'published_envelope_mm':[p['width'],p['height'],p['closed_depth']],'envelope_pose':'closed' if p['family']=='clamshell' else 'body','measured_envelope_mm':[envelope.XLength,envelope.YLength,envelope.ZLength],'pose':{'type':'hinge' if p['family']=='clamshell' else 'fixed','group':'Lid','pivot_mm':[0,p.get('hinge_y',0),p.get('hinge_z',0)],'axis':[1,0,0],'default_opening':p.get('default_opening',180),'range':[0,p.get('default_opening',180)]},'fidelity':'Published envelope; approximate exterior details and schematic major internals','source_digest':info.SourceDigest}
    (out/'reports/final_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    with (out/'COMPONENTS.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.writer(f,lineterminator='\n');writer.writerow(['Part number','Part ID','Label','Assembly','Material','Solid count','Volume mm3','X mm','Y mm','Z mm','Fidelity'])
        for o in m.parts.values():
            b=o.Shape.optimalBoundingBox(False,False);writer.writerow([o.PartNumber,o.PartID,o.Label,o.Assembly,o.MaterialDescription,len(o.Shape.Solids),o.Shape.Volume,b.XLength,b.YLength,b.ZLength,o.Fidelity])
    App.setActiveDocument(m.doc.Name);m.snapshot('final_hero',assemblies=main_groups)
    print(json.dumps({k:v for k,v in report.items() if k not in ['objects','exploded_objects','offsets','views']},ensure_ascii=False))
    return report,exploded
