from pathlib import Path
import json,math,time
PROJECT_ROOT=(globals().get('PROJECT_ROOT') or str(Path(__file__).resolve().parents[1]))
exec(compile((Path(PROJECT_ROOT)/'scripts/cad_base.py').read_bytes(),'cad_base.py','exec'))
PALETTE={'shell':(.095,.10,.11),'bezel':(.022,.025,.03),'screen':(.035,.045,.055),'metal':(.63,.66,.69),'black':(.035,.037,.04),'rubber':(.13,.14,.15),'pcb':(.035,.20,.13),'gold':(.84,.66,.23),'copper':(.72,.36,.16),'blue':(.015,.63,.84),'red':(.94,.17,.20),'white':(.83,.84,.83),'battery':(.15,.15,.16),'led':(.40,.95,.22)}
C={};G={}

def group(key,label=None):
    if key not in G:
        g=D.addObject('App::DocumentObjectGroup',key+'Group');g.Label=label or key;G[key]=g
    return G[key]

def register(o,key,assembly,layer,material='shell',internal=False):
    for prop,typ in [('PartID','App::PropertyString'),('Assembly','App::PropertyString'),('ExplodeLayer','App::PropertyInteger'),('MaterialDescription','App::PropertyString'),('PhysicalPart','App::PropertyBool'),('Fidelity','App::PropertyString')]:
        if prop not in o.PropertiesList:o.addProperty(typ,prop,'CAD study')
    o.PartID=key;o.Assembly=assembly;o.ExplodeLayer=layer;o.MaterialDescription=material;o.PhysicalPart=True
    o.Fidelity='Schematic internal layout' if internal else 'Approximate exterior detail; published envelope dimensions'
    group(assembly).addObject(o);C[key]=o
    appearance(o,PALETTE.get(material,PALETTE['shell']))
    return o

def feature(key,label,shape,assembly='Tablet',layer=0,material='shell',internal=False):
    assert not shape.isNull() and shape.isValid() and len(shape.Solids)>0,key
    return register(part_feature(D,key,label,shape),key,assembly,layer,material,internal)

def box(key,label,w,h,t,pos,assembly='Tablet',layer=0,material='shell',r=0,internal=False,orient=None):
    return feature(key,label,rr_shape(w,h,r,t,pos,orient),assembly,layer,material,internal)

def cyl(key,label,r,t,pos,assembly='Tablet',layer=0,material='metal',axis=(0,0,1),internal=False):
    return register(cylinder(D,key,label,r,t,pos,axis,PALETTE[material]),key,assembly,layer,material,internal)

def ringpart(key,label,ro,ri,t,pos,assembly='Tablet',layer=0,material='metal',axis=(0,0,1),internal=False):
    v=vec(*pos);n=vec(*axis)
    shape=Part.makeCylinder(ro,t,v,n).cut(Part.makeCylinder(ri,t+.2,v-n*.1,n))
    return feature(key,label,shape,assembly,layer,material,internal)

def cut(key,tools,reason='开孔'):
    old=C[key]
    tsh=Part.makeCompound(tools) if isinstance(tools,list) else tools
    tool=part_feature(D,key+'Tool',reason+' · 刀具',tsh)
    group('Construction','隐藏的构造历史').addObject(tool)
    new=boolean_cut(D,key+'Refined',old.Label,old,tool)
    old.PhysicalPart=False
    register(new,key,old.Assembly,old.ExplodeLayer,old.MaterialDescription,old.Fidelity.startswith('Schematic'))
    old.Visibility=False;tool.Visibility=False
    return new

def textpart(key,text,size,pos,assembly='Tablet',layer=0,material='white',orient=None):
    o=printed_text(D,key,text,text,size,pos,orient,PALETTE[material])
    return register(o,key,assembly,layer,material,False)

def visible(assemblies=None,exclude=None):
    for k,g in G.items():g.Visibility=True
    selected=[o for o in C.values() if assemblies is None or o.Assembly in assemblies]
    set_visible_components(D,selected)
    for k in exclude or []:
        if k in C:C[k].Visibility=False
    Gui.Selection.clearSelection()

def snap(name,normal=(0,0,1),target=(0,0,6.95),span=165,size=(2000,1200),assemblies=None,exclude=None,up=(0,1,0)):
    visible(assemblies,exclude)
    return render(OUT/'previews'/(name+'.png'),normal=normal,up=up,target=target,span=span,size=size)

def stage_done(n,slug,summary,views=None,extra=None):
    D.recompute()
    invalid=[o.Name for o in D.Objects if 'Invalid' in o.State]
    assert not invalid,invalid
    visible()
    rows=audit_objects(list(C.values()))
    for r,o in zip(rows,C.values()):r.update(part_id=o.PartID,assembly=o.Assembly,layer=o.ExplodeLayer,material=o.MaterialDescription,fidelity=o.Fidelity)
    path=OUT/'iterations'/f'{n:02d}_{slug}.FCStd';D.saveAs(str(path))
    pictures=[]
    for suffix,settings in (views or [('front',{}),('perspective',{'normal':(-.6,-.5,2)})]):
        pictures.append(snap(f'{n:02d}_{slug}_{suffix}',**settings))
    visible()
    report={'iteration':n,'slug':slug,'summary':summary,'time':time.time(),'file':str(path),'physical_components':len(C),'objects':rows,'invalid_features':invalid,'views':pictures,'extra':extra or {}}
    (OUT/'reports'/f'{n:02d}_{slug}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    return {k:v for k,v in report.items() if k!='objects'}

def screw(key,pos,assembly='Tablet',layer=-5,radius=1.6,length=3.8,axis=(0,0,1),drive='tri'):
    head=Part.makeCylinder(radius,.38)
    shaft=Part.makeCylinder(.72,length,vec(0,0,.36))
    body=head.fuse(shaft)
    grooves=[]
    for a in ([0,120,240] if drive=='tri' else [0,90,180,270]):
        g=Part.makeBox(.34,radius*.85,.24,vec(-.17,-.05,-.03));g.rotate(vec(),vec(0,0,1),a);grooves.append(g)
    body=body.cut(Part.makeCompound(grooves));body.Placement=App.Placement(vec(*pos),App.Rotation(vec(0,0,1),vec(*axis)))
    return feature(key,'三翼槽紧固螺钉' if drive=='tri' else '十字槽紧固螺钉',body,assembly,layer,'black')

def official_logo(key,width,pos,assembly='Tablet',layer=-5,material='white',orientation=None):
    global LOGO_MASTER
    if 'LOGO_MASTER' not in globals():
        import importSVG
        names={o.Name for o in D.Objects};importSVG.insert(str(ROOT/'references/switch_mark.svg'),D.Name)
        imported=[o for o in D.Objects if o.Name not in names and hasattr(o,'Shape')]
        faces=[f for o in imported for f in o.Shape.Faces]
        LOGO_MASTER=Part.makeCompound(faces);bb=LOGO_MASTER.BoundBox
        LOGO_MASTER.translate(vec(-bb.Center.x,-bb.Center.y,0))
        for o in imported:D.removeObject(o.Name)
    shape=LOGO_MASTER.copy();m=App.Matrix();m.A11=m.A22=m.A33=width/shape.BoundBox.XLength;shape=shape.transformGeometry(m)
    solid=Part.makeCompound([f.extrude(vec(0,0,.018)) for f in shape.Faces]);solid.Placement=App.Placement(vec(*pos),orientation or App.Rotation())
    return feature(key,'Nintendo Switch 官方轮廓标识',solid,assembly,layer,material)

def joy_outline_shape(width,height,outer_r,inner_r,depth,pos,side):
    s=Part.makeBox(width,height,depth,vec(-width/2,-height/2,0))
    outer=[e for e in s.Edges if e.BoundBox.ZLength>depth-1e-7 and abs(e.BoundBox.XMin-side*width/2)<1e-7]
    s=s.makeFillet(outer_r,outer)
    inner=[e for e in s.Edges if e.BoundBox.ZLength>depth-1e-7 and abs(e.BoundBox.XMin+side*width/2)<1e-7]
    s=s.makeFillet(inner_r,inner);s.translate(vec(*pos));return s

def joy_body(key,label,side,depth,z,material):
    x=side*103.0
    b=rounded_body(D,key+'Blank',label+' · 原坯',33,102,0,depth,(x,0,z),color=PALETTE[material],expr={'Height':'Parameters.JoyHeight'})
    pad=b.Tip
    names=[f'Edge{i+1}' for i,e in enumerate(pad.Shape.Edges) if e.BoundBox.ZLength>depth-1e-7 and abs(e.BoundBox.XMin-side*16.5)<1e-7]
    f=b.newObject('PartDesign::Fillet',key+'OuterCorner');f.Base=(pad,names);f.Radius=15.8;b.Tip=f;D.recompute();pad.Visibility=False
    names=[f'Edge{i+1}' for i,e in enumerate(f.Shape.Edges) if e.BoundBox.ZLength>depth-1e-7 and abs(e.BoundBox.XMin+side*16.5)<1e-7]
    g=b.newObject('PartDesign::Fillet',key+'InnerCorner');g.Base=(f,names);g.Radius=1.9;b.Tip=g;D.recompute();f.Visibility=False
    return register(b,key,'JoyLeft' if side<0 else 'JoyRight',4 if z>0 else -4,material)
