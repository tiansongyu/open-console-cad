"""Inspect current saved SHVC-001 geometry; photo fits are not factory tolerances."""
from pathlib import Path
import os,sys,json,hashlib
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App,Part
root=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1]) if len(sys.argv)>1 else root/'output/SuperFamicom_Complete.FCStd'
out=Path(sys.argv[2]) if len(sys.argv)>2 else root/'output/reports/fidelity_detail_audit.json'
doc=App.openDocument(str(source));parts={o.PartID:o for o in doc.Objects if getattr(o,'PhysicalPart',False)};checks=[]
def box(key):return parts[key].Shape.optimalBoundingBox(False,False)
def check(name,actual,expected,basis):
 passed=abs(actual-expected)<1e-5 if isinstance(expected,(int,float)) else actual==expected
 checks.append(dict(name=name,actual=actual,expected=expected,basis=basis,passed=passed))
for axis,value in [('X',200.),('Y',242.)]:check('shell.'+axis,getattr(box('BottomShell'),axis+'Length'),value,'Published Japanese body envelope')
check('control.maximum_z',box('PowerRidge').ZMax,74.,'Published Japanese overall height; feet datum Z0')
for prefix in ('CartUpperContact','CartLowerContact'):
 for row in range(2):
  xs=sorted(box(prefix+str(row*31+i)).Center.x for i in range(31))
  pitch=[round(xs[i+1]-xs[i],6) for i in range(30)]
  check(prefix+str(row)+'.intervals',pitch,[7.5 if i in (3,26) else 2.5 for i in range(30)],'Compatible SNES/SFC 62-position footprint')
  check(prefix+str(row)+'.span',xs[-1]-xs[0],85.,'Footprint first-to-last contact span')
check('front.panel_width',box('FrontPortPanel').XLength,148.,'Hardware photograph fit; no factory tolerance')
for n,cx in [(1,-34.),(2,34.)]:
 check('socket'+str(n)+'.center_x',box('ControllerSocket'+str(n)).Center.x,cx,'Hardware photograph fit')
 xs=sorted(box(f'ControllerContact{n}_{i}').Center.x-cx for i in range(7))
 expected=[-14.,-10.,-6.,0.,4.,8.,12.] if n==1 else [-12.,-8.,-4.,0.,6.,10.,14.]
 check('socket'+str(n)+'.ordered_contacts',[round(x,6) for x in xs],expected,'Observed handed three/four contact banks; local pitch estimated')
 check('number'+str(n)+'.center_x',box('ControllerNumberRing'+str(n)).Center.x,-64. if n==1 else 64.,'Outboard circled numbers visible in hardware photograph')
check('power.ridge_height',box('PowerRidge').ZLength,2.28,'Photo-fitted raised grip')
for name in ('Power','Reset'):check(name+'.surround_present',name+'LightSurround' in parts,True,'Original light aperture outline')
check('power_lens.center_x',box('PowerLens').Center.x,54.,'Photo-fitted optical-window location')
check('power_lens.center_y',box('PowerLens').Center.y,-95.,'Photo-fitted optical-window location')
for key,w in [('NintendoWord',47.),('SuperFamicomWord',68.)]:check(key+'.width',box(key).XLength,w,'Photo-fitted wordmark proportions; font outline approximate')
check('cartridge_flap_instruction','FlapInstruction' in parts,True,'Observed original instruction')
check('cartridge_flap_arrow','FlapArrow' in parts,True,'Observed original insertion arrow')
check('dc_plug.OD',box('ACDCBarrel').XLength,5.5,'Compatible HVC-002 barrel interface')
radii=[f.Surface.Radius for f in parts['ACDCBarrel'].Shape.Faces if isinstance(f.Surface,Part.Cylinder)]
check('dc_plug.ID',2*min(radii),2.1,'Compatible HVC-002 barrel interface')
check('rf_jack.OD',box('RFSocket').XLength,8.3,'Same Sky compatible RCA jack drawing')
for i in range(3):
 check('rca'+str(i)+'.pin_diameter',box('RCAPin'+str(i)).XLength,3.2,'Within Same Sky RCP-02 pin tolerance')
 check('rca'+str(i)+'.projection',box('RCAPin'+str(i)).YMax-box('RCASleeve'+str(i)).YMax,8.,'Same Sky RCP-02 compatible interface')
invalid=[key for key,o in parts.items() if o.Shape.isNull() or not o.Shape.isValid() or not o.Shape.Solids]
report=dict(device='sfc',iteration=22,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),physical_components=len(parts),checks=checks,invalid_components=invalid,passed=not invalid and all(c['passed'] for c in checks),factory_equivalence_verified=False)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(checks),'failed':[x for x in checks if not x['passed']]}));App.closeDocument(doc.Name)
raise SystemExit(0 if report['passed'] else 1)
