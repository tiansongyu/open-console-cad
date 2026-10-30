"""Check public gross dimensions and declared fitted details from saved BReps.

This is a model consistency check, not a hardware metrology certificate.
"""
import argparse,hashlib,json,os,sys
from pathlib import Path
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App
import Part,Sketcher

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('device',choices=['switch2','3ds','nds','psp','psv'])
parser.add_argument('--output',type=Path)
a=parser.parse_args();repo=Path(__file__).resolve().parents[1]
out=a.output or repo/'devices'/a.device/'output'
prefix={'switch2':'Switch2','3ds':'Nintendo3DS','nds':'NintendoDS','psp':'PSP1000','psv':'PSVita'}[a.device]
source=out/(prefix+'_Complete.FCStd');doc=App.openDocument(str(source))
c={o.PartID:o for o in doc.Objects if getattr(o,'PhysicalPart',False)}
checks=[]
def check(name,actual,expected,basis):
    checks.append(dict(name=name,actual_mm=actual,expected_mm=expected,basis=basis,passed=abs(actual-expected)<1e-5))
def bounds(keys):return Part.makeCompound([c[k].Shape for k in keys]).optimalBoundingBox(False,False)
if a.device=='switch2':
    keys=[k for k,o in c.items() if o.Assembly.startswith(('Tablet','Display','Joy'))]
    b=bounds(keys)
    for axis,expected in zip('XYZ',[272,116,30.7]):check('handheld.'+axis,getattr(b,axis+'Length'),expected,'Nintendo published gross envelope')
    check('tablet.depth',bounds(['TabletFrame','TabletRear','FrontBezel','DisplayGlass']).ZLength,13.9,'Nintendo published body depth')
    for tag in 'LR':
        bb=[c['Joy'+tag+'FaceButton'+str(i)].Shape.optimalBoundingBox(False,False) for i in range(4)]
        check('Joy'+tag+'.face_button_diameter',bb[0].XLength,8.4,'Official image fit; not a factory dimension')
        check('Joy'+tag+'.face_button_pitch',(bb[0].Center.y-bb[2].Center.y)/2,8.5,'Official image fit; not a factory dimension')
elif a.device in ['3ds','nds']:
    p=json.loads(doc.getObject('StudyInfo').ProfileJSON)
    transform=App.Placement(App.Vector(),App.Rotation(App.Vector(1,0,0),180),App.Vector(0,p['hinge_y'],p['hinge_z']))
    shapes=[]
    for o in c.values():
        if o.Assembly in ['Accessories','Cradle']:continue
        s=o.Shape.copy();s.Placement=transform.multiply(o.FlatPlacement) if o.PoseGroup=='Lid' else o.FlatPlacement;shapes.append(s)
    b=Part.makeCompound(shapes).optimalBoundingBox(False,False)
    for axis,expected in zip('XYZ',[p['width'],p['height'],p['closed_depth']]):check('closed.'+axis,getattr(b,axis+'Length'),expected,'Nintendo published closed envelope')
    if a.device=='3ds':
        cap=c['CirclePadCap'].Shape;b=cap.optimalBoundingBox(False,False)
        line=Part.makeLine(App.Vector(b.Center.x,b.Center.y,b.ZMin-1),App.Vector(b.Center.x,b.Center.y,b.ZMax+1))
        top=max(v.Point.z for v in line.common(cap).Vertexes)
        check('CirclePad.center_depression',b.ZMax-top,.42,'Estimated concavity; not a factory dimension')
else:
    b=bounds(k for k,o in c.items() if o.Assembly=='Body')
    for axis,expected in zip('XYZ',{'psp':[170,74,23],'psv':[182,83.5,18.6]}[a.device]):check('body.'+axis,getattr(b,axis+'Length'),expected,'Sony published envelope excluding largest projections')
    if a.device=='psp':
        b=bounds(['DPadUp','DPadDown','DPadLeft','DPadRight']);check('directional_span',b.XLength,26,'Original manual image fit')
        check('face_button_diameter',c['ButtonCircle'].Shape.optimalBoundingBox(False,False).XLength,9.2,'Original manual image fit')
        b1=c['ButtonTriangle'].Shape.optimalBoundingBox(False,False);b2=c['ButtonCross'].Shape.optimalBoundingBox(False,False)
        check('face_button_pitch',(b1.Center.y-b2.Center.y)/2,10.4,'Original manual image fit')
    else:
        for side in [-1,1]:
            s=c['StrapEye'+str(side)].Shape.copy();s.rotate(App.Vector(side*68.7,-35.15,0),App.Vector(0,0,1),-side*28)
            check('strap_eye_'+str(side)+'.length',s.optimalBoundingBox(False,False).XLength,10,'Official oblique image fit; not a factory dimension')
bad=[k for k,o in c.items() if o.Shape.isNull() or not o.Shape.isValid()]
report=dict(device=a.device,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),checks=checks,
            invalid_components=bad,passed=not bad and all(x['passed'] for x in checks),
            factory_equivalence_verified=False,method='Read-only saved BRep measurements; no history recompute')
(out/'reports/exterior_calibration_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report));App.closeDocument(doc.Name)
raise SystemExit(0 if report['passed'] else 1)
