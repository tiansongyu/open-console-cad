"""Reload the current CECHA00 study, check each saved solid and layout claim."""
from pathlib import Path
import hashlib,json,os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App,Part
repo=Path(__file__).resolve().parents[3]
out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else repo/'devices/ps3/output'
native=out/'PlayStation3_Complete.FCStd';doc=App.openDocument(str(native))
parts={o.PartID:o for o in doc.Objects if getattr(o,'PhysicalPart',False)}
manifest_path=out/'reports/final_manifest.json'
if not manifest_path.exists():manifest_path=repo/'devices/ps3/output/reports/final_manifest.json'
manifest=json.loads(manifest_path.read_text());checks={};errors=[]
for key,obj in parts.items():
 try:obj.Shape.check(True)
 except Exception as exc:errors.append({'part_id':key,'error':str(exc)})
checks['strict_saved_brep']=not errors
checks['components']=len(parts)==1592
checks['part_ids_and_numbers']=all(parts[r['part_id']].PartNumber==r['part_number'] for r in manifest['objects'])
bounds=lambda key:parts[key].Shape.optimalBoundingBox(False,False)
for key,x,z in [('HDMIShield',-32,34),('LANShield',-51,31),('OpticalSocket',-71,32),('AVShield',-96,31.5),('ACSocket',-134,16)]:
 b=bounds(key);checks[key+'_centre']=abs(b.Center.x-x)<1e-6 and abs(b.Center.z-z)<1e-6
b=bounds('HDMIShield');checks['HDMI_sleeve']=abs(b.XLength-15)<1e-6 and abs(b.ZLength-5.65)<1e-6
for side,n in [(1,10),(-1,9)]:
 xs=[bounds('HDMIContact'+str(side)+'_'+str(i)).Center.x for i in range(n)]
 checks['HDMI_row_'+str(side)]=all(abs(b-a-1)<1e-6 for a,b in zip(xs,xs[1:]))
xs=[bounds('LANContact'+str(i)).Center.x for i in range(8)]
checks['LAN_102_pitch']=all(abs(b-a-1.02)<1e-6 for a,b in zip(xs,xs[1:]))
contacts=[bounds('AVContact'+str(side)+'_'+str(i)) for side in [-1,1] for i in range(6)]
checks['AV_single_row']=all(abs(b.Center.z-contacts[0].Center.z)<1e-6 for b in contacts)
checks['AV_125_pitch']=all(abs(b.Center.x-a.Center.x-1.25)<1e-6 for a,b in zip(contacts,contacts[1:]))
checks['AV_reduced_sleeve']=abs(bounds('AVShield').XLength-19)<1e-6
for name,x in [('Power',130),('Eject',75)]:checks[name+'_touch_x']=abs(bounds(name+'TouchSurface').Center.x-x)<1e-6
checks['rear_fixing_stack_y']=abs(bounds('CasePillar1').Center.y-95)<1e-6
checks['rear_closure_skirt']=parts['RearFascia'].Shape.common(Part.makeLine(App.Vector(0,126,47),App.Vector(0,132,47))).Length>1
shell=parts['LowerCase'].Shape
line_length=lambda x,z:shell.common(Part.makeLine(App.Vector(x,116,z),App.Vector(x,126,z))).Length
checks['old_AC_opening_closed']=line_length(124,22)>1
for key,x,z in [('HDMI',-32,34),('LAN',-51,31),('optical',-71,32),('AV',-96,31.5),('AC',-134,16)]:checks[key+'_aperture_clear']=line_length(x,z)<1e-6
for column,x in enumerate([12,27,42,57,72,87]):
 for row,z in enumerate([6.4,11.4,16.4,21.4,26.4]):
  clear=line_length(x,z+1.1)<1e-6
  checks['left_vent_%s_%s'%(column,row)]=clear if not (column==5 and row<2) else not clear
for column,x in enumerate([-24,-39,-54,-69,-84,-99]):
 for row,z in enumerate([5.3,9.8,14.3,18.8]):checks['right_vent_%s_%s'%(column,row)]=line_length(x,z+1.1)<1e-6
modules=['tools/cadlib/ps3.py','tools/cadlib/fidelity_ps3.py','devices/ps3/scripts/iter31_official_exterior_layout_and_matched_av_interface.py']
r={'device':'ps3','iteration':31,'source_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'module_sha256':{s:hashlib.sha256((repo/s).read_bytes()).hexdigest() for s in modules},'checks':checks,'strict_brep_errors':errors,'passed':all(checks.values()),'factory_match_verified':False}
(out/'reports/fidelity_geometry.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False));App.closeDocument(doc.Name);raise SystemExit(0 if r['passed'] else 1)
