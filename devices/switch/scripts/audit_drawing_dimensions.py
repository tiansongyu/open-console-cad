import os,sys,json,csv
from pathlib import Path
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
sys.path.insert(0,str(Path(os.environ.get('PATH_TO_FREECAD_LIBDIR','')).parent/'Mod'))
import FreeCAD as App,Part
import Sketcher, _PartDesign, Spreadsheet
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output';m=json.loads((OUT/'reports/final_manifest.json').read_text());d=App.openDocument(str(OUT/'Switch_Complete.FCStd'));c={r['part_id']:d.getObject(r['name']) for r in m['objects']}
def bound(keys):
 b=App.BoundBox()
 for key in keys:b.add(c[key].Shape.optimalBoundingBox(False,False))
 return b
def group(names):return [k for k,o in c.items() if o.Assembly in names]
rows=[]
def check(name,value,expected,tol=1e-5):
 row={'measurement':name,'actual_mm':value,'expected_mm':expected,'absolute_error_mm':abs(value-expected),'pass':abs(value-expected)<tol};rows.append(row);assert row['pass'],row
for name,keys,expected in [('handheld',group(m['handheld_groups']),[239,102,28.4]),('tablet_body',['TabletFrame','TabletRear','FrontBezel','DisplayGlass'],[173,101,13.9]),('dock',group(['Dock','DockInternal']),[173,104,54]),('joy_left',group(['JoyLeft','JoyRailL','JoyInternalL']),[35.9,102,28.4]),('joy_right',group(['JoyRight','JoyRailR','JoyInternalR']),[35.9,102,28.4])]:
 b=bound(keys)
 for axis,ex in zip(['XLength','YLength','ZLength'],expected):check(name+'.'+axis,getattr(b,axis),ex)
for name,axis,expected in [('DisplayGlass','XLength',137.255715586374),('Kickstand','XLength',21),('Kickstand','YLength',57.6),('USBCShell','XLength',8.8),('USBCShell','ZLength',3.2),('JoyLStickCap','XLength',15.8),('JoyRFaceButton0','XLength',7.6)]:check(name+'.'+axis,getattr(bound([name]),axis),expected)
radii=sorted(set(round(f.Surface.Radius,8) for f in c['HeadphoneRim'].Shape.Faces if hasattr(f.Surface,'Radius')));check('headphone_internal_diameter',2*min(radii),3.52)
check('stick_projection',bound(['JoyLStickCap']).ZMax-13.9,9.1)
check('dock_guide_gap',bound(['DockGuideFront-1']).ZMin-bound(['DockGuideBack-1']).ZMax,14.5)
a=c['JoyRFaceButton1'].Shape.optimalBoundingBox(False,False).Center;b=c['JoyRFaceButton3'].Shape.optimalBoundingBox(False,False).Center;check('face_button_opposite_spacing',abs(a.x-b.x),15.4)
report=json.loads((OUT/'reports/drawing_checks.json').read_text());report['model_measurements']=rows;report['pass']=all(r['pass'] for r in rows) and len(report['dimensions'])==23
report['bounding_method']='Saved BRep optimalBoundingBox(False, False), independent of display triangulation; numerical model tolerance 0.00001 mm, not a hardware accuracy claim'
report['full_history_recompute_tested']=False
(OUT/'reports/drawing_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
# Refresh the CSV from exact boundaries, preserving the stable identifiers.
with (OUT/'COMPONENTS.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Part number','Part ID','Label','Assembly','Material/display role','Solid count','Volume estimate mm3','X mm','Y mm','Z mm','Fidelity'])
 for key,o in c.items():
  b=bound([key]);w.writerow([o.PartNumber,key,o.Label,o.Assembly,o.MaterialDescription,len(o.Shape.Solids),o.Shape.Volume,b.XLength,b.YLength,b.ZLength,o.Fidelity])
print(json.dumps({'pass':report['pass'],'model_measurements':len(rows),'dimension_annotations':len(report['dimensions'])}))
App.closeDocument(d.Name)
