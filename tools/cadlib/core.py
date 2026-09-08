"""Native CAD study primitives, component tracing, pose control and checkpoints."""
from pathlib import Path
import json,math,time,csv,hashlib
import FreeCAD as App
import FreeCADGui as Gui
import Part
from . import geometry as g
V=g.vec
PALETTE={'shell':(.12,.13,.14),'black':(.035,.038,.045),'bezel':(.018,.020,.026),'screen':(.045,.065,.080),'metal':(.62,.65,.68),'rubber':(.18,.19,.21),'white':(.78,.79,.80),'pcb':(.04,.24,.15),'gold':(.82,.64,.24),'copper':(.68,.32,.15),'battery':(.14,.14,.15),'led':(.18,.74,.38),'red':(.72,.12,.13),'blue':(.08,.35,.72),'thermal':(.45,.46,.49)}

class Study:
    def __init__(self,repository,device):
        self.repo=Path(repository).resolve();self.root=self.repo/'devices'/device;self.out=self.root/'output'
        self.profile=json.loads((self.root/'profile.json').read_text());self.id=device
        for p in ['iterations','previews','reports','drawings']:(self.out/p).mkdir(parents=True,exist_ok=True)
        self.doc=App.newDocument(self.profile['prefix']+'Study');self.doc.Label=self.profile['title']+' · staged CAD study'
        self.parts={};self.groups={};self.colors={**PALETTE,'accent':tuple(self.profile['color'])}
        self.params=self.doc.addObject('Spreadsheet::Sheet','Parameters');self.params.Label='Dimensions and presentation parameters'
        self.params.set('A1','Parameter');self.params.set('B1','Value');self.params.set('C1','Basis')
        self.param_cells={}
        for i,(key,val,note) in enumerate([('Width',self.profile['width'],'Published closed/body envelope'),('Height',self.profile['height'],'Published closed/body envelope'),('ClosedDepth',self.profile['closed_depth'],'Published closed/body envelope'),('BaseDepth',self.profile['base_depth'],'Approximate internal split'),('Opening',self.profile.get('default_opening',180),'Presentation opening; use pose macro'),('Wall',1.25,'Approximate shell thickness')],2):
            self.params.set(f'A{i}',key);self.params.set(f'B{i}',str(val)+('' if key=='Opening' else ' mm'));self.params.setAlias(f'B{i}',key);self.params.set(f'C{i}',note);self.param_cells[key]=f'B{i}'
        self.params.setColumnWidth('A',145);self.params.setColumnWidth('B',95);self.params.setColumnWidth('C',285)
        self.doc.recompute();self.opening=180
    def group(self,name):
        if name not in self.groups:self.groups[name]=self.doc.addObject('App::DocumentObjectGroup',name+'Group')
        return self.groups[name]
    def register(self,o,key,assembly,layer,material,internal=False,pose='Base'):
        for prop,typ in [('PartID','App::PropertyString'),('Assembly','App::PropertyString'),('ExplodeLayer','App::PropertyInteger'),('MaterialDescription','App::PropertyString'),('PhysicalPart','App::PropertyBool'),('Fidelity','App::PropertyString'),('PoseGroup','App::PropertyString'),('FlatPlacement','App::PropertyPlacement')]:
            if prop not in o.PropertiesList:o.addProperty(typ,prop,'Study')
        o.PartID=key;o.Assembly=assembly;o.ExplodeLayer=layer;o.MaterialDescription=material;o.PhysicalPart=True;o.PoseGroup=pose;o.FlatPlacement=o.Placement
        o.Fidelity='Schematic internal layout' if internal else 'Published envelope; approximate local detail'
        self.group(assembly).addObject(o);self.parts[key]=o;g.appearance(o,self.colors[material]);return o
    def feature(self,key,label,shape,assembly='Body',layer=0,material='shell',internal=False,pose='Base'):
        assert key not in self.parts,key
        assert not shape.isNull() and shape.isValid() and shape.Solids,key
        o=g.part_feature(self.doc,key,label,shape);return self.register(o,key,assembly,layer,material,internal,pose)
    def native(self,key,label,w,h,r,t,pos,assembly='Body',layer=0,material='accent',pose='Base',expr=None):
        o=g.rounded_body(self.doc,key+'Body',label,w,h,min(r,min(w,h)/2-.01),t,pos,color=self.colors[material],expr=expr)
        return self.register(o,key,assembly,layer,material,False,pose)
    def rr(self,w,h,t,pos=(0,0,0),r=.4,orient=None):
        return g.rr_shape(w,h,max(0,min(r,min(w,h)/2-.02)),t,pos,orient)
    def box(self,key,label,w,h,t,pos,assembly='Body',layer=0,material='shell',r=.4,internal=False,pose='Base',orient=None):
        return self.feature(key,label,self.rr(w,h,t,pos,r,orient),assembly,layer,material,internal,pose)
    def cyl(self,key,label,r,t,pos,assembly='Body',layer=0,material='metal',axis=(0,0,1),internal=False,pose='Base'):
        return self.feature(key,label,Part.makeCylinder(r,t,V(*pos),V(*axis)),assembly,layer,material,internal,pose)
    def ring(self,key,label,ro,ri,t,pos,assembly='Body',layer=0,material='metal',axis=(0,0,1),internal=False,pose='Base'):
        p=V(*pos);n=V(*axis);s=Part.makeCylinder(ro,t,p,n).cut(Part.makeCylinder(ri,t+.1,p-n*.05,n))
        return self.feature(key,label,s,assembly,layer,material,internal,pose)
    def cut(self,key,tools,reason):
        old=self.parts[key];shape=Part.makeCompound(tools) if isinstance(tools,list) else tools
        tool=g.part_feature(self.doc,key+'Tool',reason+' · tool',shape);self.group('Construction').addObject(tool)
        new=g.boolean_cut(self.doc,key+'Cut',old.Label,old,tool)
        old.PhysicalPart=False
        self.register(new,key,old.Assembly,old.ExplodeLayer,old.MaterialDescription,old.Fidelity.startswith('Schematic'),old.PoseGroup)
        old.Visibility=False;tool.Visibility=False;return new
    def label(self,key,text,size,pos,assembly='Body',layer=0,material='white',pose='Base',rotation=None):
        font=self.root/'references/DejaVuSans.ttf'
        wires=Part.makeWireString(text,str(font.parent)+'/',font.name,size)
        faces=[]
        for character in wires:
            if character:
                face=Part.makeFace(character,'Part::FaceMakerBullseye');faces.extend(face.Faces)
        sh=Part.makeCompound([f.extrude(V(0,0,.018)) for f in faces]);sh.Placement=App.Placement(V(*pos),rotation or App.Rotation())
        return self.feature(key,text,sh,assembly,layer,material,False,pose)
    def screw(self,key,pos,assembly='Internal',layer=-2,length=3.2,radius=1.2,pose='Base',axis=(0,0,1)):
        body=Part.makeCylinder(radius,.35).fuse(Part.makeCylinder(.62,length,V(0,0,.33)))
        cutters=[Part.makeBox(.28,radius*1.5,.22,V(-.14,-radius*.75,-.02)),Part.makeBox(radius*1.5,.28,.22,V(-radius*.75,-.14,-.02))]
        body=body.cut(Part.makeCompound(cutters));body.rotate(V(),V(0,1,0),180 if axis==(0,0,-1) else 0);body.translate(V(*pos));return self.feature(key,'Cross-head fastener',body,assembly,layer,'metal',True,pose)
    def set_pose(self,opening):
        theta=180-opening;py=self.profile.get('hinge_y',0);pz=self.profile.get('hinge_z',0)
        transform=App.Placement(V(),App.Rotation(V(1,0,0),theta),V(0,py,pz))
        for o in self.parts.values():o.Placement=transform.multiply(o.FlatPlacement) if o.PoseGroup=='Lid' else o.FlatPlacement
        self.opening=opening;self.params.set(self.param_cells['Opening'],str(opening));self.doc.recompute()
    def visible(self,assemblies=None,exclude=()):
        for group in self.groups.values():group.Visibility=True
        selected=[o for o in self.parts.values() if (assemblies is None or o.Assembly in assemblies) and o.PartID not in exclude]
        g.set_visible_components(self.doc,selected);Gui.Selection.clearSelection();return selected
    def snapshot(self,name,normal=(-.6,-.7,2.4),assemblies=None,exclude=(),size=(1800,1400)):
        App.setActiveDocument(self.doc.Name);Gui.activateView('Gui::View3DInventor',True)
        objs=self.visible(assemblies,exclude);q=g.rotation(normal)
        shape=Part.makeCompound([o.Shape for o in objs]);shape.Placement=App.Placement(V(),q.inverted()).multiply(shape.Placement)
        b=shape.optimalBoundingBox(False,False);target=q.multVec(b.Center);span=max(b.YLength,b.XLength*size[1]/size[0])*1.16
        return g.render(self.out/'previews'/(name+'.png'),normal=normal,target=tuple(target),span=span,size=size)
    def checkpoint(self,n,slug,summary):
        self.doc.recompute();bad=[o.Name for o in self.doc.Objects if 'Invalid' in o.State];assert not bad,bad
        rows=g.audit_objects(list(self.parts.values()))
        for row,o in zip(rows,self.parts.values()):row.update(part_id=o.PartID,assembly=o.Assembly,layer=o.ExplodeLayer,material=o.MaterialDescription,fidelity=o.Fidelity,pose_group=o.PoseGroup)
        self.set_pose(self.profile.get('default_opening',180));self.visible()
        file=self.out/'iterations'/f'{n:02d}_{slug}.FCStd';self.doc.saveAs(str(file))
        previews=[self.snapshot(f'{n:02d}_{slug}_hero')]
        if n in [2,5,8,10,12]:previews.append(self.snapshot(f'{n:02d}_{slug}_front',normal=(0,0,1)))
        self.set_pose(180)
        report={'iteration':n,'slug':slug,'summary':summary,'physical_components':len(self.parts),'objects':rows,'invalid_features':bad,'file':str(file.relative_to(self.repo)),'views':[str(Path(p).relative_to(self.repo)) for p in previews],'geometry_audit_pose':'flat / opening 180 degrees','saved_pose':self.profile.get('default_opening',180)}
        (self.out/'reports'/f'{n:02d}_{slug}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
        print(json.dumps({k:v for k,v in report.items() if k!='objects'},ensure_ascii=False));return report
