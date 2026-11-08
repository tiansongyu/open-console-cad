"""Read-only published dimensions and original Nintendo layout checks for WUP-001/010."""
from pathlib import Path
import argparse,hashlib,json,os,sys
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App
import Part
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path);args=parser.parse_args()
out=args.output or Path(__file__).resolve().parents[1]/'output'
source=out/'WiiU_Complete.FCStd';doc=App.openDocument(str(source.resolve()))
parts={o.PartID:o for o in doc.Objects if getattr(o,'PhysicalPart',False)}
checks=[]
def check(name,actual,expected,basis='Nintendo photograph/diagram fit; not a factory dimension'):
 checks.append({'name':name,'actual':actual,'expected':expected,'basis':basis,'passed':abs(actual-expected)<1e-5})
def bounds(keys):return Part.makeCompound([parts[k].Shape for k in keys]).optimalBoundingBox(False,False)
def bb(key):return parts[key].Shape.optimalBoundingBox(False,False)
for group,keys,want in [('console',['LowerHousing','UpperHousing','FrontBezel'],[172,268.5,46]),('gamepad',['PadBack','PadFront'],[255.4,133.4,41]),('stylus',['StylusBarrel','StylusTip','StylusCap'],[8.4,97.9,5.4]),('console_adapter',['ConsoleACLower','ConsoleACUpper'],[150,70,49]),('gamepad_adapter',['GamePadACLower','GamePadACUpper'],[100,35,28])]:
 b=bounds(keys)
 for axis,expected in zip('XYZ',want):check(group+'.'+axis,getattr(b,axis+'Length'),expected,'Published Nintendo envelope in model axes; accessory cords and protrusions excluded')
for key,x,y in [('LStickRim',-105.2,35),('RStickRim',105.2,35),('PadDPad',-94.5,6.5),('PadA',105.5,5.5),('PadB',95.5,-4.5),('PadX',95.5,15.5),('PadY',85.5,5.5),('PadPlus',84.5,-20.5),('PadMinus',84.5,-33),('PadTV',54,-54),('PadPower',66.5,-54),('PadHome',0,-54),('SpeakerOpening-1',-84.5,-54),('SpeakerOpening1',84.5,-54)]:
 b=bb(key);check(key+'.x',b.Center.x,x);check(key+'.local_y',b.Center.y+275,y)
for key,x in [('PadVolume',56.5),('PadAudioJack',-49),('PadChargeSocket',-62.5),('PowerButton',-73),('EjectButton',-73),('SyncButton',-38.5)]:check(key+'.x',bb(key).Center.x,x)
for i,z in enumerate((13.5,22)):
 b=bb('RearUSB'+str(i));check('RearUSB'+str(i)+'.x',b.Center.x,-58);check('RearUSB'+str(i)+'.z',b.Center.z,z)
for side in (-1,1):
 b=bb('PadDockPad'+str(side));check('dock_contact'+str(side)+'.x',b.Center.x,side*16.5)
 check('dock_contact'+str(side)+'.bottom_edge',int(b.YMax<-338 and b.YLength<2 and b.ZLength>2),1,'Nintendo manual: contacts on bottom edge, not rear face')
for key,axis,want in [('CameraIRWindow','X',72.2),('CameraIRWindow','Y',8.6),('LStickCap','X',16.4),('RStickCap','X',16.4),('LStickRim','X',21.6),('RStickRim','X',21.6),('EjectButton','X',10.6),('EjectButton','Z',6),('FrontFlap','X',82.4),('PadTVIRWindow','X',13.5),('PadTVIRWindow','Z',14)]:check(key+'.'+axis,getattr(bb(key),axis+'Length'),want)
vents=[o for o in doc.Objects if o.Label.startswith('Three-column rear cooling grille · tool')]
for i,v in enumerate(vents):check('rear_grille'+str(i)+'.openings',len(v.Shape.Solids),21,'Nintendo rear photograph: three columns by seven rows')
strict={}
strict_keys=['LowerHousing','UpperHousing','FrontBezel','PadFront','PadBack','PadTVIRWindow','PadDockPad-1','PadDockPad1','PadSyncButton','PadDPad','PadTV','NFCMark','CameraIRWindow','LStickCap','RStickCap','StylusCap','ConsoleACLower','ConsoleACUpper','GamePadACLower','GamePadACUpper']
strict_keys+=['Pad'+s+'Legend' for s in ['Start','Select','Mic','Home','Battery','TV','Power']]
for key in strict_keys:
 try:parts[key].Shape.check(True);strict[key]=True
 except Exception as exc:strict[key]=str(exc)
invalid=[k for k,o in parts.items() if o.Shape.isNull() or not o.Shape.isValid() or not o.Shape.Solids]
required=['CameraOuterRing','PadSyncButton','PadTVIRWindow']+['Pad'+s+'Legend' for s in ['Start','Select','Mic','Home','Battery','TV','Power']]
report={'device':'wiiu','iteration':23,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'checks':checks,'invalid_parts':invalid,'strict_changed_breps':strict,'new_features_present':all(k in parts for k in required),'factory_equivalence_verified':False,'scope':'Published overall dimensions and fitted exterior layout; inherited rear crossbar, battery door, shoulder curves and internal structures remain approximate.'}
report['passed']=not invalid and len(vents)==2 and report['new_features_present'] and all(v is True for v in strict.values()) and all(c['passed'] for c in checks)
(out/'reports/fidelity_detail_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False));App.closeDocument(doc.Name)
raise SystemExit(0 if report['passed'] else 1)
