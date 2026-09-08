"""Shared exact BRep drawing primitives. Call init_drawing(root) in FreeCAD Python."""
import sys,os,json,math,hashlib,re,html
from pathlib import Path
import FreeCAD as App,Part,TechDraw
FONT='TsangerJinKai02, Noto Serif CJK SC, serif'

def init_drawing(device_root):
 global ROOT,OUT,DRAW,CACHE,M,D,E,CD,C,EC,CC,OBJECT_SETS,HH,PAGES,CHECKS
 ROOT=Path(device_root).resolve();OUT=ROOT/'output';DRAW=OUT/'drawings';CACHE=DRAW/'projections';CACHE.mkdir(parents=True,exist_ok=True)
 M=json.loads((OUT/'reports/final_manifest.json').read_text());prefix=M['prefix']
 D=App.openDocument(str(OUT/(prefix+'_Complete.FCStd')));E=App.openDocument(str(OUT/(prefix+'_Exploded.FCStd')))
 CD=App.openDocument(str(OUT/(prefix+'_Closed.FCStd'))) if (OUT/(prefix+'_Closed.FCStd')).exists() else D
 C={r['part_id']:D.getObject(r['name']) for r in M['objects']};EC={r['part_id']:E.getObject(r['name']) for r in M['exploded_objects']};CC={r['part_id']:CD.getObject(r['name']) for r in M['objects']}
 OBJECT_SETS={'open':C,'closed':CC,'exploded':EC};HH=M['handheld_groups'];PAGES=[];CHECKS=[]

def rot(normal,up=(0,1,0)):
 z=App.Vector(*normal);z.normalize();x=App.Vector(*up).cross(z);x.normalize();y=z.cross(x)
 m=App.Matrix();m.A11,m.A21,m.A31=x.x,x.y,x.z;m.A12,m.A22,m.A32=y.x,y.y,y.z;m.A13,m.A23,m.A33=z.x,z.y,z.z
 return App.Rotation(m)

def keys_for(assemblies,internal=True):
 return [k for k,o in C.items() if o.Assembly in assemblies and (internal or not o.Fidelity.startswith('Schematic'))]

def bb(keys,exploded=False,source=None):
 objs=OBJECT_SETS[source or ('exploded' if exploded else 'open')]
 return Part.makeCompound([objs[k].Shape for k in keys]).optimalBoundingBox(False,False)

def projection(keys,normal,up,center,exploded=False,source=None):
 source=source or ('exploded' if exploded else 'open');objs=OBJECT_SETS[source]
 token=hashlib.sha256(json.dumps([keys,normal,up,center,source,[(k,objs[k].Shape.Volume,list(objs[k].Shape.optimalBoundingBox(False,False).Center)) for k in keys]]).encode()).hexdigest()[:20]
 file=CACHE/(token+'.svg')
 if file.exists():return file.read_text()
 q=rot(normal,up).inverted();shape=Part.makeCompound([objs[k].Shape for k in keys]);shape.Placement=App.Placement(-q.multVec(App.Vector(*center)),q).multiply(shape.Placement)
 raw=TechDraw.projectToSVG(shape,App.Vector(0,0,1));raw=re.sub(r'stroke-width="[^"]+"','stroke-width="0.18"',raw);raw=re.sub(r'id=\s*"[^"]+"','',raw)
 file.write_text(raw);print('projected',source,len(keys),token,flush=True);return raw

class Sheet:
 def __init__(self,num,title,notes):
  self.num=num;self.title=title;self.notes=notes;self.elements=[];self.views=[];self.dimensions=[]
 def text(self,x,y,s,size=3.2,anchor='start',fill='#141413'):
  self.elements.append(f'<text x="{x:.4f}" y="{y:.4f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}">{html.escape(str(s))}</text>')
 def line(self,p1,p2,dash=False):
  self.elements.append(f'<path d="M {p1[0]:.5f} {p1[1]:.5f} L {p2[0]:.5f} {p2[1]:.5f}" stroke="#504e49" stroke-width="0.16" fill="none"'+(' stroke-dasharray="2 1"' if dash else '')+'/>')
 def arrow(self,tip,angle):
  pts=[tip,(tip[0]+2.1*math.cos(angle+.24),tip[1]+2.1*math.sin(angle+.24)),(tip[0]+2.1*math.cos(angle-.24),tip[1]+2.1*math.sin(angle-.24))]
  self.elements.append('<polygon points="'+' '.join(f'{x:.4f},{y:.4f}' for x,y in pts)+'" fill="#504e49"/>')
 def view(self,name,keys,x,y,scale=1,normal=(0,0,1),up=(0,1,0),center=(0,0,0),exploded=False,source=None):
  raw=projection(keys,normal,up,center,exploded,source)
  raw=re.sub(r'stroke-width="[^"]+"',f'stroke-width="{.18/scale:.7f}"',raw)
  self.elements.append(f'<g data-cad-view="{name}" transform="translate({x},{y}) scale({scale})">{raw}</g>')
  v={'name':name,'keys':keys,'x':x,'y':y,'scale':scale,'normal':list(normal),'up':list(up),'center':list(center),'exploded':exploded,'source':source or ('exploded' if exploded else 'open')};self.views.append(v);return v
 def view_fit(self,name,keys,rect,normal,up=(0,1,0),exploded=False,source=None):
  objs=OBJECT_SETS[source or ('exploded' if exploded else 'open')];q=rot(normal,up)
  shape=Part.makeCompound([objs[k].Shape for k in keys]);shape.Placement=App.Placement(App.Vector(),q.inverted()).multiply(shape.Placement)
  bounds=shape.optimalBoundingBox(False,False);center=list(q.multVec(bounds.Center))
  x,y,w,h=rect;scale=min(w/bounds.XLength,h/bounds.YLength)*.94
  return self.view(name,keys,x+w/2,y+h/2,scale,normal,up,center,exploded,source)
 def point(self,v,p):
  a=rot(v['normal'],v['up']).inverted().multVec(App.Vector(*p)-App.Vector(*v['center']))
  return(v['x']+a.x*v['scale'],v['y']-a.y*v['scale'])
 def dim(self,v,p1,p2,axis,offset,label=None,published=False):
  a,b=self.point(v,p1),self.point(v,p2);scale=v['scale']
  if axis=='x':
   value=abs(a[0]-b[0])/scale;pa=(a[0],offset);pb=(b[0],offset);self.line((a[0],a[1]),pa);self.line((b[0],b[1]),pb)
   self.line(pa,pb);left,right=sorted([pa,pb]);self.arrow(left,0);self.arrow(right,math.pi);tx,ty=(pa[0]+pb[0])/2,offset-1.6
  else:
   value=abs(a[1]-b[1])/scale;pa=(offset,a[1]);pb=(offset,b[1]);self.line(a,pa);self.line(b,pb);self.line(pa,pb);top,bottom=sorted([pa,pb],key=lambda p:p[1]);self.arrow(top,math.pi/2);self.arrow(bottom,-math.pi/2);tx,ty=offset-2,(pa[1]+pb[1])/2
  display=label or f'{value:.2f}'.rstrip('0').rstrip('.')
  if not published:display='≈ '+display
  self.text(tx,ty,display,anchor='middle' if axis=='x' else 'end',fill='#1B365D')
  record={'view':v['name'],'p1':list(p1),'p2':list(p2),'axis':axis,'value_mm':value,'label':display,'published':published,'label_position':[tx,ty]};self.dimensions.append(record);CHECKS.append({'sheet':self.num,**record});return value
 def leader(self,v,key,anchor,label=None):
  objs=OBJECT_SETS[v['source']];end=self.point(v,list(objs[key].Shape.optimalBoundingBox(False,False).Center));self.line(anchor,(anchor[0]+6,anchor[1]));self.line((anchor[0]+6,anchor[1]),end)
  self.elements.append(f'<circle cx="{end[0]:.3f}" cy="{end[1]:.3f}" r=".65" fill="#1B365D"/>')
  self.text(anchor[0],anchor[1]-1.3,label or C[key].PartNumber,3.2)
 def save(self):
  svg='<svg xmlns="http://www.w3.org/2000/svg" width="396mm" height="214mm" viewBox="0 0 396 214"><style>text {font-family:'+FONT+';font-weight:400;}</style>'+''.join(self.elements)+'</svg>'
  path=DRAW/f'{self.num:02d}.svg';path.write_text(svg)
  import xml.etree.ElementTree as ET
  ET.register_namespace('','http://www.w3.org/2000/svg')
  tree=ET.fromstring(svg)
  for item in list(tree):
   if 'data-cad-view' in item.attrib:tree.remove(item)
  (DRAW/f'{self.num:02d}_annotations.svg').write_text(ET.tostring(tree,encoding='unicode'))
  PAGES.append({'number':self.num,'title':self.title,'svg':path.name,'notes':self.notes,'views':self.views,'dimensions':self.dimensions})

def finish_drawing():
 (DRAW/'drawing_pages.json').write_text(json.dumps(PAGES,ensure_ascii=False,indent=2))
 (OUT/'reports/drawing_checks.json').write_text(json.dumps({'pass':all(c['value_mm']>0 for c in CHECKS),'page_count':len(PAGES),'dimensions':CHECKS,'method':'BRep orthographic projections, model-derived endpoints, and planar cross sections; source pose identified per view'},ensure_ascii=False,indent=2))
 for name in set([D.Name,E.Name,CD.Name]):App.closeDocument(name)
 print(json.dumps({'pages':len(PAGES),'dimensions':len(CHECKS),'complete':True}),flush=True)

def dimension_box(sheet,view,keys,axis,offset,published=False,label=None):
 objs=OBJECT_SETS[view['source']];q=rot(view['normal'],view['up']);center=App.Vector(*view['center'])
 shape=Part.makeCompound([objs[k].Shape for k in keys]);shape.Placement=App.Placement(-q.inverted().multVec(center),q.inverted()).multiply(shape.Placement)
 b=shape.optimalBoundingBox(False,False);p1=b.Center;p2=App.Vector(p1)
 if axis=='x':p1.x=b.XMin;p2.x=b.XMax
 else:p1.y=b.YMin;p2.y=b.YMax
 a=q.multVec(p1)+center;z=q.multVec(p2)+center
 return sheet.dim(view,tuple(a),tuple(z),axis,offset,label=label,published=published)

def section_view(sheet,name,keys,rect,normal=(0,1,0),up=(0,0,1),offset=0,source='open'):
 objs=OBJECT_SETS[source];faces=[];ids=[]
 for key in keys:
  wires=objs[key].Shape.slice(App.Vector(*normal),offset);closed=[w for w in wires if w.isClosed()]
  if closed:
   face=Part.makeFace(closed,'Part::FaceMakerBullseye');faces.extend(face.Faces);ids.append(key)
 assert faces,name
 q=rot(normal,up);shape=Part.makeCompound(faces);temp=shape.copy();temp.Placement=App.Placement(App.Vector(),q.inverted()).multiply(temp.Placement);bounds=temp.optimalBoundingBox(False,False)
 x,y,w,h=rect;scale=min(w/bounds.XLength,h/bounds.YLength)*.94;center=q.multVec(bounds.Center)
 for face in faces:
  paths=[]
  for wire in face.Wires:
   points=wire.discretize(Deflection=.02);points=[q.inverted().multVec(p-center) for p in points]
   paths.append('M '+' L '.join(f'{x+w/2+p.x*scale:.5f} {y+h/2-p.y*scale:.5f}' for p in points)+' Z')
  sheet.elements.append('<path d="'+' '.join(paths)+'" fill="#e8e6dc" fill-rule="evenodd" stroke="#504e49" stroke-width=".16"/>')
 v={'name':name,'keys':keys,'x':x+w/2,'y':y+h/2,'scale':scale,'normal':list(normal),'up':list(up),'center':list(center),'source':source,'exploded':False,'section_part_ids':ids,'plane_offset':offset}
 sheet.views.append(v);return v
