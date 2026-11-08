"""Read-only checks for the saved DMG exterior calibration; no hardware tolerance claim."""
from pathlib import Path
import hashlib,json,math,os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App,Part
repo=Path(__file__).resolve().parents[3]
p=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else repo/'devices/gameboy/output/GameBoy_Complete.FCStd'
out=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else p.parent/'reports/fidelity_geometry.json'
d=App.openDocument(str(p));parts={o.PartID:o for o in d.Objects if getattr(o,'PhysicalPart',False)};checks=[]
def check(name,value,expected,basis,tolerance=1e-5):
 ok=abs(value-expected)<tolerance if isinstance(expected,(float,int)) else value==expected
 checks.append({'name':name,'actual':value,'expected':expected,'basis':basis,'passed':ok})
def bb(key):return parts[key].Shape.optimalBoundingBox(False,False)
for key,axis,value,basis in [
 ('DisplayGlass','XLength',47,'Nintendo nominal screen size, active pixel boundary unverified'),
 ('DisplayGlass','YLength',43,'Nintendo nominal screen size, active pixel boundary unverified'),
 ('ContrastWheel','YMin',23.3029003906244,'Photo-fitted center Y28.5'),
 ('ContrastWheel','ZLength',1.55,'Retained thin contrast thumbwheel'),
 ('VolumeWheel','ZLength',3,'Photo-fitted thicker volume thumbwheel'),
 ('DCJack','YMin',47,'Photo-fitted power-jack center Y49.5'),
 ('DCJack','ZMin',8.5,'Photo-fitted power-jack center Z11'),
 ('LinkPortShell','YLength',14,'Photo-fitted original large connector width'),
 ('LinkPortShell','ZLength',6.4,'Photo-fitted original large connector height')]:check(key+'.'+axis,getattr(bb(key),axis),value,basis)
check('contrast on left',bb('ContrastWheel').Center.x<0,True,'Original front-view device left')
check('volume and link on right',bb('VolumeWheel').Center.x>0 and bb('LinkPortShell').Center.x>0,True,'Original front-view device right')
check('power jack nearer top than contrast',bb('DCJack').Center.y>bb('ContrastWheel').Center.y,True,'Firsthand side photograph')
centers=[bb('LinkPin'+str(i)).Center for i in range(6)]
check('link contact rows',sorted(set(round(v.z,5) for v in centers)),[10.45,11.55],'Documented 2-by-3 topology; local coordinates fitted')
check('link contact columns',sorted(set(round(v.y,5) for v in centers)),[39.5,42.0,44.5],'Documented 2-by-3 topology; pitch fitted')
check('six contacts',len([k for k in parts if k.startswith('LinkPin')]),6,'Pan Docs external connectors')
radii=sorted(set(round(f.Surface.Radius,5) for f in parts['DCJack'].Shape.Faces if hasattr(f.Surface,'Radius')))
check('power-jack bore for 3.5mm plug',1.8 in radii,True,'3.5mm nominal plug plus estimated0.1mm diametral clearance')
case=parts['FrontFace'].Shape
for i in range(6):
 x,y=15.5+i*4.5,-63.5+i*2.6
 check('grille recessed groove '+str(i),case.isInside(App.Vector(x,y,30.6),1e-7,False),False,'Photographed six molded grooves')
 check('grille floor '+str(i),case.isInside(App.Vector(x-.3*math.cos(math.radians(23)),y-.3*math.sin(math.radians(23)),30.0),1e-7,False),i==0,'Photographed five through slots; lowest groove remains blind')
for key in ['RearOrigin','ContrastLegend','VolumeLegend','LinkLegend','PowerSideLegend','PhonesLegend','LinkPortCover']:
 check('present '+key,key in parts,True,'Observed original molded marking or removable cover')
invalid=[k for k,o in parts.items() if o.Shape.isNull() or not o.Shape.isValid()]
r={'passed':all(x['passed'] for x in checks) and not invalid,'source':str(p.relative_to(repo)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'physical_components':len(parts),'solids':sum(len(o.Shape.Solids) for o in parts.values()),'invalid_features':invalid,'checks':checks,'factory_equivalence_verified':False,'limitations':['Local contour radii, port coordinates, lettering and fit clearances are fitted to photographs.','47x43mm is Nintendo nominal screen size; no identified LCD-module drawing establishes the active pixel boundary.']}
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');App.closeDocument(d.Name)
print(json.dumps({'passed':r['passed'],'checks':len(checks),'failed':[x for x in checks if not x['passed']]}));assert r['passed']
