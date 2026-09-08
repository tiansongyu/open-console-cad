"""Exact BRep visible-line projection and model-derived drawing dimensions.
Run with FreeCAD's Python runtime after finalize_models.py. No GUI required.
"""
import sys,os,json,math,hashlib,re,html
from pathlib import Path
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App,Part,TechDraw
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output';DRAW=OUT/'drawings';CACHE=DRAW/'projections';CACHE.mkdir(parents=True,exist_ok=True)
M=json.loads((OUT/'reports/final_manifest.json').read_text())
D=App.openDocument(str(OUT/'Switch_Complete.FCStd'));E=App.openDocument(str(OUT/'Switch_Exploded.FCStd'))
C={r['part_id']:D.getObject(r['name']) for r in M['objects']};EC={r['part_id']:E.getObject(r['name']) for r in M['exploded_objects']}
HH=M['handheld_groups'];FONT='TsangerJinKai02, Noto Serif CJK SC, serif'
PAGES=[];CHECKS=[]

def rot(normal,up=(0,1,0)):
 z=App.Vector(*normal);z.normalize();x=App.Vector(*up).cross(z);x.normalize();y=z.cross(x)
 m=App.Matrix();m.A11,m.A21,m.A31=x.x,x.y,x.z;m.A12,m.A22,m.A32=y.x,y.y,y.z;m.A13,m.A23,m.A33=z.x,z.y,z.z
 return App.Rotation(m)

def keys_for(assemblies,internal=True):
 return [k for k,o in C.items() if o.Assembly in assemblies and (internal or not o.Fidelity.startswith('Schematic'))]

def bb(keys,exploded=False):
 objs=EC if exploded else C
 return Part.makeCompound([objs[k].Shape for k in keys]).optimalBoundingBox(False,False)

def projection(keys,normal,up,center,exploded=False):
 objs=EC if exploded else C
 token=hashlib.sha256(json.dumps([keys,normal,up,center,exploded,[(k,objs[k].Shape.Volume,list(objs[k].Shape.optimalBoundingBox(False,False).Center)) for k in keys]]).encode()).hexdigest()[:20]
 p=CACHE/(token+'.svg')
 if p.exists():return p.read_text()
 q=rot(normal,up).inverted();s=Part.makeCompound([objs[k].Shape for k in keys]);s.Placement=App.Placement(-q.multVec(App.Vector(*center)),q).multiply(s.Placement)
 raw=TechDraw.projectToSVG(s,App.Vector(0,0,1))
 raw=re.sub(r'stroke-width="[^"]+"','stroke-width="0.18"',raw)
 raw=re.sub(r'id=\s*"[^"]+"','',raw)
 p.write_text(raw);print('projected',len(keys),token,flush=True);return raw

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
 def view(self,name,keys,x,y,scale=1,normal=(0,0,1),up=(0,1,0),center=(0,0,0),exploded=False):
  raw=projection(keys,normal,up,center,exploded)
  raw=re.sub(r'stroke-width="[^"]+"',f'stroke-width="{.18/scale:.7f}"',raw)
  self.elements.append(f'<g data-cad-view="{name}" transform="translate({x},{y}) scale({scale})">{raw}</g>')
  v={'name':name,'keys':keys,'x':x,'y':y,'scale':scale,'normal':list(normal),'up':list(up),'center':list(center),'exploded':exploded};self.views.append(v);return v
 def view_fit(self,name,keys,rect,normal,up=(0,1,0),exploded=False):
  objs=EC if exploded else C;q=rot(normal,up)
  shape=Part.makeCompound([objs[k].Shape for k in keys]);shape.Placement=App.Placement(App.Vector(),q.inverted()).multiply(shape.Placement)
  bounds=shape.optimalBoundingBox(False,False);center=list(q.multVec(bounds.Center))
  x,y,w,h=rect;scale=min(w/bounds.XLength,h/bounds.YLength)*.94
  return self.view(name,keys,x+w/2,y+h/2,scale,normal,up,center,exploded)
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
  objs=EC if v['exploded'] else C;end=self.point(v,list(objs[key].Shape.optimalBoundingBox(False,False).Center));self.line(anchor,(anchor[0]+6,anchor[1]));self.line((anchor[0]+6,anchor[1]),end)
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
# 01 / complete handheld envelope, three orthographic projections.
ext=keys_for(['Tablet','Display','JoyLeft','JoyRight','JoyRailL','JoyRailR'],False)
s=Sheet(1,'手持整机总装图',['标准版 HAC-001，图中最大厚度包含摇杆与扳机。','公开包络尺寸采用 Nintendo 资料，局部轮廓为本模型近似设计。'])
v=s.view('HandheldFront',ext,151,80,1,center=(0,0,6.95));s.text(151,139,'正面 · 1:1',anchor='middle')
s.dim(v,(-119.5,0,0),(119.5,0,0),'x',17,published=True);s.dim(v,(0,-51,0),(0,51,0),'y',19,published=True)
r=s.view('HandheldRight',ext,333,80,1,normal=(1,0,0),center=(0,0,8.8));s.text(333,139,'右视 · 1:1',anchor='middle')
s.dim(r,(0,0,-5.4),(0,0,23),'x',149,published=True)
t=s.view('HandheldTop',ext,151,177,1,normal=(0,1,0),up=(0,0,1),center=(0,0,8.8));s.text(151,207,'顶视 · 1:1',anchor='middle')
s.text(293,180,'主机主体厚度 13.9 mm',3.2);s.text(293,188,'所有尺寸单位：mm',3.2);s.text(293,196,'局部近似值用 ≈ 标识',3.2);s.save()
# 02 / tablet front, back and interfaces.
tablet=keys_for(['Tablet','Display'],False)
s=Sheet(2,'主机结构尺寸',['显示区由 6.2 英寸、16:9 的参考比例建立。','支架、进风口和接口位置为本模型尺寸，孔位未使用制造公差。'])
f=s.view('TabletFront',tablet,102,71,1,center=(0,0,6.95));b=s.view('TabletBack',tablet,294,71,1,normal=(0,0,-1),center=(0,0,6.95))
s.text(102,129,'主机正面 · 1:1',anchor='middle');s.text(294,129,'主机背面 · 1:1',anchor='middle')
s.dim(f,(-86.5,0,0),(86.5,0,0),'x',13,published=True);s.dim(f,(0,-50.5,0),(0,50.5,0),'y',12,published=True)
s.dim(f,(-68.627857793,0,13.9),(68.627857793,0,13.9),'x',26,label='137.26')
s.dim(b,(54.5,-20.6,.02),(75.5,-20.6,.02),'x',138,label='21')
s.dim(b,(65,-49.4,.02),(65,8.2,.02),'y',208,label='57.6')
t=s.view('TabletTop',tablet,102,166,1,normal=(0,1,0),up=(0,0,1),center=(0,0,6.95));u=s.view('TabletBottom',tablet,294,166,1,normal=(0,-1,0),up=(0,0,1),center=(0,0,6.95))
s.text(102,190,'顶部：电源 / 音量 / 排风 / 耳机 / 卡槽',3.2,'middle');s.text(294,190,'底部：识别标签 / USB-C / 定位孔',3.2,'middle')
s.dim(u,(0,-50.4,0),(0,-50.4,13.9),'y',388,published=True)
s.save()
# 03 / controller exterior and button locations.
lkeys=keys_for(['JoyLeft','JoyRailL'],False);rkeys=keys_for(['JoyRight','JoyRailR'],False)
s=Sheet(3,'左右 Joy-Con 尺寸',['左右手柄具有相同的包络，摇杆与面按键的位置不同。','手柄宽度包含导轨端部，最大厚度包含摇杆与后扳机。'])
l=s.view('JoyLeftFront',lkeys,56,80,1,center=(-101.55,0,8.8));r=s.view('JoyRightFront',rkeys,158,80,1,center=(101.55,0,8.8));inner=s.view('JoyLeftInnerRail',lkeys,259,80,1,normal=(1,0,0),center=(-101.55,0,8.8));back=s.view('JoyRightBack',rkeys,353,80,1,normal=(0,0,-1),center=(101.55,0,8.8))
for x,label in [(56,'L 正面'),(158,'R 正面'),(259,'L 内侧'),(353,'R 背面')]:s.text(x,145,label+' · 1:1',anchor='middle')
s.dim(l,(-119.5,0,0),(-83.6,0,0),'x',16,published=True);s.dim(l,(-103,-51,0),(-103,51,0),'y',20,published=True)
s.dim(r,(93.6,25.1,15.35),(112.4,25.1,15.35),'x',163,label='18.8')
s.dim(inner,(-103,0,-5.4),(-103,0,23),'x',163,published=True)
s.text(10,184,'摇杆帽 Ø15.8 · 面按键 Ø6.36 · 按键中心间距 9.4',3.2)
s.text(10,194,'L 摇杆中心：X=-103，Y=25.3，R 摇杆中心：X=103，Y=-12',3.2)
s.text(10,204,'上述局部尺寸均为近似值，按当前模型坐标记录。',3.2)
s.save()
# 04 / connector, rail and analog details, with enlarged actual BRep curves.
s=Sheet(4,'接口与控制机构详图',['USB-C 的金属壳、绝缘舌片与上下触点分开建模。','导轨与摇杆详图保留实体几何，尺寸为当前研究模型值。'])
usbc=[k for k in C if k.startswith('USBC')]
v=s.view('USBCDetail',usbc,65,49,5,normal=(0,-1,0),up=(0,0,1),center=(0,-50.4,6.9));s.text(65,80,'USB-C 插座正视 · 5:1',anchor='middle')
s.dim(v,(-4.4,-50.4,6.9),(4.4,-50.4,6.9),'x',27,label='8.8');s.dim(v,(0,-50.4,5.3),(0,-50.4,8.5),'y',20,label='3.2')
v=s.view('HeadphoneDetail',['HeadphoneRim','HeadphoneContact'],192,49,5,normal=(0,1,0),up=(0,0,1),center=(49,50,7.2));s.text(192,80,'耳机插座 · 5:1',anchor='middle');s.dim(v,(47.24,50,7.2),(50.76,50,7.2),'x',27,label='Ø3.52')
v=s.view('StickDetail',[k for k in C if k.startswith('JoyLStick')],315,51,2,normal=(0,1,0),up=(0,0,1),center=(-103,25.3,17));s.text(315,80,'摇杆侧视 · 2:1',anchor='middle');s.dim(v,(-103,25.3,13.9),(-103,25.3,23),'y',356,label='9.1')
v=s.view('RailSection',['ConsoleRail-1','JoyLRailTongue','JoyLRailBack'],65,150,5,normal=(0,-1,0),up=(0,0,1),center=(-84.7,-10,7.15));s.text(65,196,'导轨端面 · 5:1',anchor='middle')
v=s.view('RailScrewDetail',['RailScrew-1_1','RailBoss-1_1'],192,150,5,normal=(-1,0,0),up=(0,1,0),center=(-82,-37,7.15));s.text(192,196,'导轨螺钉与安装柱 · 5:1',anchor='middle')
v=s.view('HapticDetail',['JoyLHapticCase','JoyLHapticMass','JoyLHapticCoil','JoyLHapticSpring0','JoyLHapticSpring1'],315,151,5,normal=(.3,-.3,-1),center=(-100,-34.5,3.8));s.text(315,196,'振动单元 · 5:1',anchor='middle')
s.save()
# 05 / true planar sections from the physical BRep, shaded by cut material regions.
def section_view(sheet,name,keys,x,y,scale,plane_y,center):
 faces=[];sections=[]
 sheet.elements.append(f'<g data-cad-section="{name}">')
 for key in keys:
  wires=C[key].Shape.slice(App.Vector(0,1,0),plane_y)
  closed=[w for w in wires if w.isClosed()]
  if not closed:continue
  cutface=Part.makeFace(closed,'Part::FaceMakerBullseye');faces.extend(cutface.Faces)
  q=rot((0,1,0),(0,0,1)).inverted()
  for face in cutface.Faces:
   path=[]
   for wire in face.Wires:
    pts=wire.discretize(Deflection=.018)
    xy=[]
    for p in pts:
     a=q.multVec(p-App.Vector(*center));xy.append((x+a.x*scale,y-a.y*scale))
    path.append('M '+' L '.join(f'{a:.5f} {b:.5f}' for a,b in xy)+' Z')
   sheet.elements.append('<path d="'+' '.join(path)+'" fill="#e8e6dc" fill-rule="evenodd" stroke="#504e49" stroke-width="0.16"/>')
  sections.append(key)
 sheet.elements.append('</g>')
 shape=Part.makeCompound(faces);shape.exportBrep(str(DRAW/(name+'.brep')))
 v={'name':name,'keys':keys,'x':x,'y':y,'scale':scale,'normal':[0,1,0],'up':[0,0,1],'center':list(center),'exploded':False,'section_brep':name+'.brep','cut_plane_y':plane_y,'section_part_ids':sections};sheet.views.append(v);return v
s=Sheet(5,'主机与手柄剖面',['浅色填充表示实体与指定 Y 平面的真实交线所围区域。','本页剖面穿过指定部位，不把未被剖切平面经过的扳机算入厚度。'])
v=section_view(s,'TabletSectionY0',keys_for(['Tablet','Display','TabletInternal']),198,51,2,0,(0,0,6.95));s.text(198,20,'A-A · 主机 Y=0 剖面 · 2:1',anchor='middle');s.dim(v,(0,0,0),(0,0,13.9),'y',18,published=True)
v=section_view(s,'JoyLeftSection',keys_for(['JoyLeft','JoyRailL','JoyInternalL']),105,146,5.0,25.3,(-101.55,25.3,11));s.text(105,78,'B-B · L 摇杆中心 · 5:1',anchor='middle')
v=section_view(s,'JoyRightSection',keys_for(['JoyRight','JoyRailR','JoyInternalR']),293,146,5.0,-12,(101.55,-12,11));s.text(293,78,'C-C · R 摇杆中心 · 5:1',anchor='middle');s.text(105,213,'剖切坐标 Y=25.3',anchor='middle');s.text(293,213,'剖切坐标 Y=-12',anchor='middle');s.save()
# 06 / tablet exploded modules and traceable part-number legend.
s=Sheet(6,'主机分层爆炸图',['沿厚度方向展开主要装配层，爆炸位移只用于展示。','序号对应组件 CSV 与原生模型树，细小固定件保留在所属功能层中。'])
ks=keys_for(['Tablet','Display','TabletInternal']);v=s.view('TabletExploded',ks,198,73,.34,normal=(1.7,-.2,-1),center=(0,0,-100),exploded=True)
legend=[('DisplayGlass','触控显示窗口'),('FrontBezel','前面板'),('LCDModule','LCD 模组'),('DisplayBackplate','显示背板'),('TabletFrame','中框及接口'),('Mainboard','主板与封装'),('BatteryPouch','电池组件'),('CopperHeatPipe','热管和风扇'),('RearEMIShield','屏蔽板'),('TabletRear','后壳'),('Kickstand','支架')]
for i,(key,label) in enumerate(legend):
 col=i%4;row=i//4;xx=8+col*97;yy=145+row*21
 s.text(xx,yy,C[key].PartNumber,3.2,fill='#1B365D');s.text(xx,yy+6,label,3.2)
 if True:
  pt=s.point(v,list(EC[key].Shape.optimalBoundingBox(False,False).Center));s.text(pt[0],pt[1]-28,C[key].PartNumber,3.2,'middle');s.line((pt[0],pt[1]-25),(pt[0],pt[1]-8))
s.save()
# 07 / separate controller exploded layouts.
s=Sheet(7,'左右手柄分层爆炸图',['手柄前后壳、电池、PCB、摇杆及振动单元分层展示。','右侧增加 NFC 和红外组件，左右主板轮廓和摇杆位置不同。'])
l=s.view('JoyLeftExploded',keys_for(['JoyLeft','JoyRailL','JoyInternalL']),101,79,.78,normal=(.9,-.15,1.2),center=(-260,-220,-15),exploded=True)
r=s.view('JoyRightExploded',keys_for(['JoyRight','JoyRailR','JoyInternalR']),296,79,.78,normal=(-.9,-.15,1.2),center=(260,-220,-15),exploded=True)
s.text(101,18,'Joy-Con L',4,'middle');s.text(296,18,'Joy-Con R',4,'middle')
for side,tag in [(0,'L'),(1,'R')]:
 for i,(suffix,caption) in enumerate([('Front','前壳'),('PCB','主板'),('GimbalHousing','摇杆机构'),('Battery','电池'),('HapticCase','振动单元'),('Rear','后壳')]):
  xx=12+side*194+(i%2)*94;yy=151+(i//2)*20;key='Joy'+tag+suffix
  s.text(xx,yy,C[key].PartNumber,3.2,fill='#1B365D');s.text(xx,yy+6,caption)
s.save()
# 08 / dock three-view dimensional drawing.
dockkeys=keys_for(['Dock','DockInternal'])
s=Sheet(8,'底座结构尺寸',['含防滑脚的底座包络为 173 × 104 × 54 mm。','前后软垫限定主机插入槽，内部连接器和主板可在爆炸页中观察。'])
f=s.view('DockFront',dockkeys,109,71,1.0,center=(0,-182,0));r=s.view('DockSide',dockkeys,310,71,1.0,normal=(1,0,0),center=(0,-182,0));t=s.view('DockTop',dockkeys,109,175,1.0,normal=(0,1,0),up=(0,0,1),center=(0,-182,0))
s.dim(f,(-86.5,-182,0),(86.5,-182,0),'x',12,published=True);s.dim(f,(0,-234,0),(0,-130,0),'y',13,published=True);s.dim(r,(0,-182,-27),(0,-182,27),'x',137,published=True)
s.text(109,130,'正面 · 1:1',anchor='middle');s.text(310,130,'右视 · 1:1',anchor='middle');s.text(109,212,'顶视 · 1:1',anchor='middle')
s.text(230,171,'两侧导垫之间：≈14.5 mm',3.2);s.text(230,182,'后部：USB-C / USB-A / HDMI',3.2);s.text(230,193,'左侧：2 个 USB-A 接口',3.2);s.save()
# 09 / dock exploded view with service-part legend.
s=Sheet(9,'底座分层爆炸图',['后盖移开后，可单独观察接口板和后部接插件。','主机导垫与插头支座分别编号，外壳保持与总装页相同的几何。'])
v=s.view_fit('DockExploded',dockkeys,(10,18,376,117),normal=(1.5,-.2,-1),exploded=True)
for i,(key,label) in enumerate([('DockFront','前壳'),('DockGuideFront-1','前导垫'),('DockUSBCPlug','插头'),('DockTower','后部壳体'),('DockPCB','接口板'),('DockBackCover','后盖'),('DockScrew1','后盖螺钉'),('DockFloor','底部连接梁')]):
 xx=10+(i%4)*97;yy=163+(i//4)*24;s.text(xx,yy,C[key].PartNumber,3.2,fill='#1B365D');s.text(xx,yy+6,label,3.2)
s.save()
# 10 / grip and wrist strap dimensions from the actual accessory bounds.
s=Sheet(10,'握把与腕带结构',['握把为非充电型外观研究，侧轨与手持控制器使用相同装配概念。','腕带包含锁扣、轨道按钮、锚环、闭合织绳和沿绳调节扣。'])
gkeys=keys_for(['Grip']);gb=bb(gkeys);gc=list(gb.Center)
v=s.view('GripFront',gkeys,77,82,1,center=gc);s.dim(v,(gb.XMin,gc[1],gc[2]),(gb.XMax,gc[1],gc[2]),'x',17)
s.text(77,151,'握把正视 · 1:1',anchor='middle');v=s.view('GripSide',gkeys,188,82,1,normal=(1,0,0),center=gc);s.text(188,151,'握把侧视',anchor='middle')
for xx,tag in [(278,'L'),(355,'R')]:
 ks=keys_for(['Strap'+tag]);b=bb(ks);center=list(b.Center);v=s.view('Strap'+tag,ks,xx,83,.8,center=center)
 s.text(xx,162,'腕带 '+tag+' · 0.8:1',anchor='middle')
 if tag=='R':s.dim(v,(center[0],b.YMin,center[2]),(center[0],b.YMax,center[2]),'y',390)
s.text(10,181,'握把外包络 ≈ '+f'{gb.XLength:.2f} × {gb.YLength:.2f} × {gb.ZLength:.2f} mm')
s.text(10,192,'腕带外壳：≈14.6 × 101 × 13.9 mm；织绳截面 Ø1.7 mm'.replace('；','，'))
s.text(10,203,'附件数字均为本模型尺寸，未作为 Nintendo 公开规格使用。');s.save()
# 11 / complete component roll-up and material key.
CN={'Display':'显示组件','Tablet':'主机外部结构','TabletInternal':'主机内部布局','JoyLeft':'左手柄外部','JoyRight':'右手柄外部','JoyRailL':'左手柄导轨','JoyRailR':'右手柄导轨','JoyInternalL':'左手柄内部','JoyInternalR':'右手柄内部','Dock':'底座外壳','DockInternal':'底座内部','Grip':'握把','StrapL':'左腕带','StrapR':'右腕带'}
s=Sheet(11,'零件与材料索引',['每个物理组件有独立 SW 编号，可对照模型树和 COMPONENTS.csv。','多实体的标识字形与网格仍作为一个组件记录，组件数与实体数分别列出。'])
for x,t in [(10,'子装配'),(122,'组件数'),(158,'主要材质/显示'),(282,'首末编号 · 非连续')]:s.text(x,13,t,4,fill='#1B365D')
s.line((10,17),(386,17))
for i,(assembly,count) in enumerate(M['assemblies'].items()):
 rows=[r for r in M['objects'] if r['assembly']==assembly];numbers=[r['part_number'] for r in rows];mats=sorted(set(r['material'] for r in rows));mats=[{'black':'深色零件','metal':'金属件','screen':'光学窗口','bezel':'黑色面板','gold':'金色触点','battery':'电池包','copper':'铜色零件','blue':'蓝色壳体','red':'红色壳体','rubber':'弹性体','led':'指示灯','pcb':'电路板','shell':'塑料壳体','white':'浅色标记'}[x] for x in mats];y=29+i*11.3
 s.text(10,y,CN[assembly]);s.text(129,y,count,anchor='middle');s.text(158,y,' / '.join(mats[:4]),3.2);s.text(282,y,numbers[0]+' … '+numbers[-1],3.2);s.line((10,y+4),(386,y+4))
s.text(10,198,f"合计 {M['physical_components']} 个物理组件 · {M['solids']} 个实体 · 全量清单见 COMPONENTS.csv",3.5,fill='#1B365D');s.save()
# 12 / publication basis, iteration and verification index.
s=Sheet(12,'尺寸依据与检查索引',['公开包络与本模型局部尺寸严格区分，内部用于结构学习和装配观察。','检查报告随项目交付，图纸不包含真实电路和未公开的制造公差。'])
for y,title,lines in [
(16,'公开尺寸',["整机 239 × 102 × 13.9 mm，含摇杆/扳机最大厚 28.4 mm。","主机单体 173 × 101 × 13.9 mm，手柄含轨道宽 35.9 mm。","底座 173 × 104 × 54 mm。"]),
(59,'模型范围',["局部壁厚、孔位、紧固件和安装间隙为近似设计。","电池、主板、芯片、风扇和控制器内部为主要模块布局示意。","尺寸数字描述此版模型，不能代替制造方工程资料。"]),
(102,'验证文件',["14 轮设计迭代和每轮模型保存在 iterations/。","14_interference_audit.json：完整实体干涉核验。","parameter_edit_test.json、rebuild_verification.json：参数与源码重建。","export_roundtrip_audit.json、drawing_checks.json：导出回读与尺寸检查。"]),
(157,'参考来源',["Nintendo 官方产品规格、Joy-Con/底座规格、部位图和数字手册。","iFixit 2017 年 Nintendo Switch 现场拆解：主要内部模块布局。","完整链接与尺寸依据见 references/SOURCES.md。"])
]:
 s.text(10,y,title,4,fill='#1B365D')
 for j,line in enumerate(lines):s.text(10,y+10+j*8,line,3.2)
s.text(385,210,'CAD STUDY · 2026.09.08',3.2,'end');s.save()
assert len(PAGES)==12
(DRAW/'drawing_pages.json').write_text(json.dumps(PAGES,ensure_ascii=False,indent=2))
(OUT/'reports/drawing_checks.json').write_text(json.dumps({'page_count':12,'dimensions':CHECKS,'model_envelope':M['published_handheld_mm'],'method':'visible-line projection of the final BRep; coordinates projected with the same rotation as dimension endpoints; section regions from planar BRep slices','pass':all(c['value_mm']>0 for c in CHECKS)},ensure_ascii=False,indent=2))
App.closeDocument(D.Name);App.closeDocument(E.Name)
print(json.dumps({'pages':12,'dimensions':len(CHECKS),'completed':True}),flush=True)
