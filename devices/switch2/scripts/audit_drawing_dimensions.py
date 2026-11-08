import os,sys,json,csv,re
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App,Part
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output';m=json.loads((OUT/'reports/final_manifest.json').read_text());d=App.openDocument(str(OUT/'Switch2_Complete.FCStd'));c={r['part_id']:d.getObject(r['name']) for r in m['objects']}
def bound(keys):return Part.makeCompound([c[k].Shape for k in keys]).optimalBoundingBox(False,False)
def group(names):return [k for k,o in c.items() if o.Assembly in names]
rows=[]
def check(name,value,expected,tol=1e-5):
 row={'measurement':name,'actual_mm':value,'expected_mm':expected,'absolute_error_mm':abs(value-expected),'pass':abs(value-expected)<tol};rows.append(row);assert row['pass'],row
for name,keys,expected in [('handheld',group(m['handheld_groups']),[272,116,30.7]),('tablet_body',['TabletFrame','TabletRear','FrontBezel','DisplayGlass'],[198,116,13.9]),('dock',group(['Dock','DockInternal']),[201,115,51.2]),('joy_left',group(['JoyLeft','JoyMountL','JoyInternalL']),[41.4,116,30.7]),('joy_right',group(['JoyRight','JoyMountR','JoyInternalR']),[41.4,116,30.7])]:
 b=bound(keys)
 for axis,ex in zip(['XLength','YLength','ZLength'],expected):check(name+'.'+axis,getattr(b,axis),ex)
for name,axis,expected in [('DisplayGlass','XLength',174.89034727941205),('Kickstand','XLength',183),('Kickstand','YLength',58.87411967464943),('USBLowerShell','XLength',8.8),('USBLowerShell','ZLength',3.2),('JoyLStickCap','XLength',17.1),('JoyRFaceButton0','XLength',8.4)]:check(name+'.'+axis,getattr(bound([name]),axis),expected)
radii=sorted(set(round(f.Surface.Radius,8) for f in c['HeadphoneRim'].Shape.Faces if hasattr(f.Surface,'Radius')));check('headphone_internal_diameter',2*min(radii),3.52)
check('stick_projection',bound(['JoyLStickCap']).ZMax-13.9,10.8)
check('dock_guide_gap',bound(['DockFrontGuide-1']).ZMin-bound(['DockRearGuide-1']).ZMax,14.25)
a=c['JoyRFaceButton1'].Shape.optimalBoundingBox(False,False).Center;b=c['JoyRFaceButton3'].Shape.optimalBoundingBox(False,False).Center;check('face_button_opposite_spacing',abs(a.x-b.x),17.0)
# Audit the saved drawing annotations, including prose captions. Previously a
# historical 7.4 / 10.8 caption and 21.6 dimension survived a button revision.
pages=json.loads((OUT/'drawings/drawing_pages.json').read_text());control_page=next(p for p in pages if p['number']==3)
opposite=next(x for x in control_page['dimensions'] if x['view']=='JoyRightFront')
check('drawing.face_button_opposite_spacing',opposite['value_mm'],abs(a.x-b.x))
texts=[''.join(node.itertext()) for node in ET.parse(OUT/'drawings'/control_page['svg']).iter() if node.tag.rsplit('}',1)[-1]=='text']
caption=next(text for text in texts if text.startswith('摇杆帽 Ø'))
values=[float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',caption)]
assert len(values)==3,caption
for name,value,expected in zip(['stick_cap_diameter','face_button_diameter','button_center_radius'],values,[bound(['JoyLStickCap']).XLength,bound(['JoyRFaceButton0']).XLength,abs(a.x-b.x)/2]):check('caption.'+name,value,expected)
caption=next(text for text in texts if text.startswith('L 摇杆中心：'))
values=[float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',caption)]
left=bound(['JoyLStickCap']).Center;right=bound(['JoyRStickCap']).Center
assert len(values)==4,caption
for name,value,expected in zip(['left_x','left_y','right_x','right_y'],values,[left.x,left.y,right.x,right.y]):check('caption.stick_'+name,value,expected)
report=json.loads((OUT/'reports/drawing_checks.json').read_text());report['model_measurements']=rows;report['pass']=all(r['pass'] for r in rows) and len(report['dimensions'])>20
report['geometry_source']='saved BRep; full feature history not recomputed'
report['bounding_method']='optimalBoundingBox(False, False), independent of display triangulation'
(OUT/'reports/drawing_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
# Refresh the CSV from exact boundaries, preserving the stable identifiers.
with (OUT/'COMPONENTS.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Part number','Part ID','Label','Assembly','Material/display role','Solid count','Volume estimate mm3','X mm','Y mm','Z mm','Fidelity'])
 for key,o in c.items():
  b=bound([key]);w.writerow([o.PartNumber,key,o.Label,o.Assembly,o.MaterialDescription,len(o.Shape.Solids),o.Shape.Volume,b.XLength,b.YLength,b.ZLength,o.Fidelity])
print(json.dumps({'pass':report['pass'],'model_measurements':len(rows),'dimension_annotations':len(report['dimensions'])}))
App.closeDocument(d.Name)
