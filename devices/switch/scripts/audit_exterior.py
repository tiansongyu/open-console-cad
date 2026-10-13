"""Independently reload the exterior revision and verify millimetre envelopes.

Run with the FreeCAD Python runtime and PATH_TO_FREECAD_LIBDIR set. The Mod
path is also required so native PartDesign history is fully restored.
"""
import os,sys,json,hashlib
from pathlib import Path
sys.path.insert(0,os.environ['PATH_TO_FREECAD_LIBDIR'])
sys.path.insert(0,str(Path(os.environ['PATH_TO_FREECAD_LIBDIR']).parent/'Mod'))
import FreeCAD as App,Part,Sketcher,PartDesign,Spreadsheet
root=Path(__file__).resolve().parents[1];out=root/'output'
m=json.loads((out/'reports/final_manifest.json').read_text())
d=App.openDocument(str((out/'Switch_Complete.FCStd').resolve()))
c={o.PartID:o for o in d.Objects if getattr(o,'PhysicalPart',False)}
invalid=[o.Name for o in d.Objects if 'Invalid' in o.State]
assert not invalid,invalid
checks=[]
def dimensions(name,keys,expected):
 b=App.BoundBox()
 for k in keys:b.add(c[k].Shape.optimalBoundingBox(False,False))
 actual=[b.XLength,b.YLength,b.ZLength]
 checks.append(dict(name=name,actual_mm=actual,expected_mm=expected,tolerance_mm=1e-5,max_error_mm=max(abs(a-b) for a,b in zip(actual,expected)),passed=max(abs(a-b) for a,b in zip(actual,expected))<1e-5))
dimensions('handheld',[k for k,o in c.items() if o.Assembly in m['handheld_groups']],[239,102,28.4])
dimensions('tablet',['TabletFrame','TabletRear','FrontBezel','DisplayGlass'],[173,101,13.9])
for tag in ['L','R']:
 groups=['JoyLeft','JoyRailL','JoyInternalL'] if tag=='L' else ['JoyRight','JoyRailR','JoyInternalR']
 dimensions('joy_'+tag,[k for k,o in c.items() if o.Assembly in groups],[35.9,102,28.4])
rounds=[]
for tag in ['L','R']:
 for side in ['Front','Rear']:
  for suffix in ['Outer15','RailSide15','PerimeterRoll15']:
   o=d.getObject('Joy'+tag+side+suffix)
   rounds.append(dict(feature=o.Name,radius_mm=o.Radius.Value,expression=list(o.ExpressionEngine),valid=o.Shape.isValid()))
shells=[dict(part_id=k,solids=len(c[k].Shape.Solids),valid=c[k].Shape.isValid()) for k in ['JoyLFront','JoyLRear','JoyRFront','JoyRRear','TabletFrame','TabletRear']]
external_links=[{'object':o.Name,'target':v.Name,'document':v.Document.Name} for o in d.Objects for v in o.OutList if v.Document != d]
lofts=[dict(feature=o.Name,sections=len(o.Sections),valid=o.Shape.isValid()) for o in d.Objects if o.TypeId=='Part::Loft' and 'UnequalEdgeLoft' in o.Name]
buttons=[dict(part_id=k,diameter_mm=c[k].Shape.optimalBoundingBox(False,False).XLength) for k in c if 'FaceButton' in k]
report=dict(revision=17,model='Nintendo Switch HAC-001',source='devices/switch/output/Switch_Complete.FCStd',source_sha256=hashlib.sha256((out/'Switch_Complete.FCStd').read_bytes()).hexdigest(),physical_components=len(c),solids=sum(len(o.Shape.Solids) for o in c.values()),envelope_checks=checks,historical_native_fillet_features=rounds,calibrated_native_lofts=lofts,face_buttons=buttons,shells=shells,local_geometry_basis='Official Nintendo product images and design patent D819642 Fig.3/4; fitted exterior estimates, not factory measurements. Retained V16 cavities and schematic internals.',invalid_features=invalid,external_document_links=external_links,scope='Saved exterior geometry. Envelope tolerance is a CAD numerical check, not a manufacturing tolerance or physical-device accuracy.',passed=not external_links and all(x['passed'] for x in checks) and all(x['valid'] for x in rounds+shells+lofts) and len(lofts)==4 and all(abs(x['diameter_mm']-7.6)<1e-5 for x in buttons))
(out/'reports/exterior_refinement_audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['native_fillet_features','shells']},indent=2))
assert report['passed']

App.closeDocument(d.Name)
