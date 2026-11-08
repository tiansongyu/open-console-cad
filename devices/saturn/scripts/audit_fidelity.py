"""Independent saved-geometry and interface checks for HST-3200 iteration 23."""
from pathlib import Path
import hashlib,json,os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App,Part
repo=Path(__file__).resolve().parents[3];out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else repo/'devices/saturn/output'
native=out/'Saturn_Complete.FCStd';doc=App.openDocument(str(native));parts={o.PartID:o for o in doc.Objects if getattr(o,'PhysicalPart',False)}
manifest=json.loads((out/'reports/final_manifest.json').read_text());checks={};errors=[]
for key,obj in parts.items():
 try:obj.Shape.check(True)
 except Exception as exc:errors.append({'part_id':key,'error':str(exc)})
checks['strict_saved_brep']=not errors;checks['components']=len(parts)==715
checks['part_ids_and_numbers']=all(parts[r['part_id']].PartNumber==r['part_number'] for r in manifest['objects'])
bb=lambda key:parts[key].Shape.optimalBoundingBox(False,False)
expected=[i-37.5 for i in list(range(1,37))+list(range(44,75))]
for side in [-1,1]:
 solids=parts['CartridgeContactBank'+str(side)].Shape.Solids;xs=sorted(s.optimalBoundingBox(False,False).Center.x for s in solids)
 checks['contacts_67_'+str(side)]=len(xs)==67
 checks['contact_centres_'+str(side)]=len(xs)==67 and all(abs(a-b)<1e-6 for a,b in zip(xs,expected))
reader=parts['CartridgeReader'].Shape
checks['cartridge_locating_key']=reader.isInside(App.Vector(2.5,81,74),1e-6,True)
checks['cartridge_left_tab_clear']=not reader.isInside(App.Vector(-20,81,74),1e-6,True)
checks['cartridge_right_tab_clear']=not reader.isInside(App.Vector(20,81,74),1e-6,True)
checks['case_overlap_lip']=getattr(parts['LowerHousing'],'FidelityOverlapLip',False)
checks['reader_width']=abs(bb('CartridgeReader').XLength-83.4)<1e-6
checks['C8_pitch']=abs(bb('ACInletPin1').Center.x-bb('ACInletPin0').Center.x-8.6)<1e-6
checks['C7_pitch']=abs(bb('ACDeviceContact1').Center.y-bb('ACDeviceContact0').Center.y-8.6)<1e-6
checks['C7_nose_width']=abs(bb('ACDeviceHead').YLength-16)<1e-6
checks['C7_nose_height']=abs(bb('ACDeviceHead').ZLength-7.85)<1e-6
checks['C7_contacts_clear_male_pin']=all(any(type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Radius-1.05)<1e-6 for f in parts['ACDeviceContact'+str(i)].Shape.Faces) for i in range(2))
checks['inlet_T_stem']=parts['ACInlet'].Shape.isInside(App.Vector(-91,112,34),1e-6,True)
checks['inlet_lower_fixing']=abs(bb('ACFixing2').Center.x+79)<1e-6 and abs(bb('ACFixing2').Center.z-35.5)<1e-6
checks['mini_DIN_male_diameter']=any(type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Radius-4.75)<1e-6 for f in parts['AVPlugShield'].Shape.Faces)
checks['mini_DIN_continuous_sleeve']=len(parts['AVPlugShield'].Shape.Solids)==1
checks['socket_key']=parts['AVCarrier'].Shape.isInside(App.Vector(-91,109,21.6),1e-6,True)
checks['male_key_slot']=not parts['AVPlugCarrier'].Shape.isInside(App.Vector(220,-1,12.2),1e-6,True)
checks['male_flat_wall']=parts['AVPlugShield'].Shape.isInside(App.Vector(220,1,3.75),1e-6,True)
for port in [1,2]:
 xs=[bb(f'ControllerContact{port}_{i}').Center.x for i in range(9)]
 checks['matched_controller_pitch_'+str(port)]=all(abs(b-a-2.55)<1e-6 for a,b in zip(xs,xs[1:]))
modules=['tools/cadlib/saturn.py','tools/cadlib/fidelity_saturn.py','devices/saturn/scripts/iter23_keyed_134_contact_cartridge_and_original_rear_interfaces.py']
r={'device':'saturn','iteration':23,'source_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'module_sha256':{s:hashlib.sha256((repo/s).read_bytes()).hexdigest() for s in modules},'checks':checks,'strict_brep_errors':errors,'passed':all(checks.values()),'factory_match_verified':False};(out/'reports/fidelity_geometry.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False));App.closeDocument(doc.Name);raise SystemExit(0 if r['passed'] else 1)
