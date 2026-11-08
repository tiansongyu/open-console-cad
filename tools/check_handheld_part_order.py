"""Exercise replacement registration without importing or changing FreeCAD data."""
import ast,json
from pathlib import Path
from types import SimpleNamespace
from cadlib.part_numbers import allocate_part_numbers

repo=Path(__file__).resolve().parents[1]
source=repo/'tools/cadlib/handheld_refinement.py'
module=ast.parse(source.read_text())
function=next(node for node in module.body if isinstance(node,ast.FunctionDef) and node.name=='replace')
namespace={}
exec(compile(ast.Module(body=[function],type_ignores=[]),str(source),'exec'),namespace)
replace=namespace['replace']
class FakePart:
    def __init__(self,key,label,assembly,layer,material,internal=False,pose='Base',number=None):
        self.PartID=key;self.Label=label;self.Assembly=assembly;self.ExplodeLayer=layer
        self.MaterialDescription=material;self.Fidelity='Schematic internal layout' if internal else 'Approximate exterior detail'
        self.PoseGroup=pose;self.PhysicalPart=True;self.Visibility=True;self.PropertiesList=[]
        self.ViewObject=SimpleNamespace(ShapeAppearance=object())
        if number is not None:self.addProperty('App::PropertyString','PartNumber','Study');self.PartNumber=number
    def addProperty(self,typ,key,group):
        assert key not in self.PropertiesList,key
        self.PropertiesList.append(key)
class FakeModel:
    def __init__(self,rows):
        self.parts={r['part_id']:FakePart(r['part_id'],r['label'],r['assembly'],r['layer'],r['material'],r['fidelity'].startswith('Schematic'),r['pose_group'],r['part_number']) for r in rows}
    def feature(self,key,label,shape,assembly,layer,material,internal,pose):
        assert key not in self.parts
        new=FakePart(key,label,assembly,layer,material,internal,pose)
        self.parts[key]=new
        return new
results=[]
for device,replacements in {
 'psp':['DPadUp','DPadRight','DPadDown','DPadLeft','DPadCarrier','DPadPCB','ButtonTriangle','ButtonCircle','ButtonCross','ButtonSquare','DisplaySurround','PowerBoard'],
 'psv':['StrapEye-1','StrapEye1'],
}.items():
    manifest=json.loads((repo/'devices'/device/'output/reports/final_manifest.json').read_text())
    profile=json.loads((repo/'devices'/device/'profile.json').read_text())
    rows=manifest['objects']
    model=FakeModel(rows);registry=model.parts;order=list(registry)
    for key in replacements:
        old=model.parts[key];new=replace(model,key,SimpleNamespace(isValid=lambda:True,Solids=[object()]),'registration order regression check')
        assert registry is model.parts
        assert list(model.parts)==order
        assert model.parts[key] is new and new.PreviousRevision is old
        assert new.PhysicalPart and not old.PhysicalPart and not old.Visibility
        assert new.PartNumber==old.PartNumber
        assert new.ViewObject.ShapeAppearance is old.ViewObject.ShapeAppearance
    # Exercise the same allocator used by deliver.finalize, including retained
    # identities with deliberate gaps after false contacts have been retired.
    expected={r['part_id']:r['part_number'] for r in rows}
    retired=manifest.get('numbering',{}).get('retired_part_numbers',[])
    numbers=allocate_part_numbers([part.PartNumber for part in model.parts.values()],
                                  device.upper(),profile.get('preserve_part_numbers',False),retired)
    for (key,part),assigned in zip(model.parts.items(),numbers):
        assert assigned==expected[key],(key,assigned,expected[key])
    assert not set(retired).intersection(numbers)
    results.append({'device':device,'physical_components':len(rows),'replacements':len(replacements),'registry_identity_preserved':True,'registration_order_preserved':True,'all_part_numbers_match_saved_manifest':True,'passed':True})
report={'passed':True,'scope':'Pure Python registration and numbering simulation of the actual replacement function; no CAD geometry or full source rebuild exercised','checks':results}
print(json.dumps(report,indent=2))
