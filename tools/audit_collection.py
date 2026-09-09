"""Read-only final collection audit. Run with the matching FreeCAD Python runtime.

Reopens every complete/exploded/closed CAD file, validates physical BReps and
saved bounds, checks editable history and native drawing pages, and records the
identity of all delivered files. Device-specific rebuild, interference, STEP and
PDF review evidence remains in each device's reports folder.
"""
from pathlib import Path
import csv,hashlib,json,os,re,subprocess,sys,time,zipfile
import xml.etree.ElementTree as ET
sys.path.insert(0,os.environ.get('PATH_TO_FREECAD_LIBDIR',''))
import FreeCAD as App
import Part,Sketcher
ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/'site/src/catalog.json').read_text())
assert {c['id'] for c in CAT}=={'switch','switch2','3ds','nds','psp','psv','steamdeck'}
result={'passed':False,'scope':'Seven independent device projects, current saved native geometry and delivery evidence','started_unix':time.time(),'manifest_bbox_tolerance_mm':1e-5,'devices':[]}
def read(path):return json.loads(path.read_text())
def passed(d):return d.get('passed',d.get('pass',d.get('cad_complete',d.get('complete',False)))) is True
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for entry in CAT:
    slug=entry['id'];root=ROOT/'devices'/slug;out=root/'output';reports=out/'reports';m=read(reports/'final_manifest.json');prefix=entry['prefix']
    assert entry['count']==m['physical_components'] and entry['iterations']==m['design_iterations']
    row={'device':slug,'variant':entry['model'],'components':m['physical_components'],'solids':m['solids'],'iterations':m['design_iterations'],'native_geometry':[],'files':{},'reports':{}}
    assert (root/'README.md').exists() and (root/'ITERATIONS.md').exists() and (root/'references/SOURCES.md').exists()
    assert (root/f'Open_{prefix}.FCMacro').exists() and (root/f'Rebuild_{prefix}.FCMacro').exists()
    stages=sorted((root/'scripts').glob('iter[0-9][0-9]_*.py'))
    assert len(stages)==m['design_iterations'],(slug,len(stages),m['design_iterations'])
    for suffix,key in [('Complete','objects'),('Exploded','exploded_objects')]+([('Closed','objects')] if entry['family']=='clamshell' else []):
        path=out/f'{prefix}_{suffix}.FCStd';doc=App.openDocument(str(path));items=m[key];checks=[]
        for spec in items:
            obj=doc.getObject(spec['name']);assert obj is not None,(slug,spec['name'])
            shape=obj.Shape;valid=not shape.isNull() and shape.isValid() and len(shape.Solids)==spec['solids'];assert valid,(slug,suffix,spec['name'])
            bb=shape.optimalBoundingBox(False,False);coords=[bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax]
            delta=max(abs(a-b) for a,b in zip(coords,spec['bounds'])) if suffix!='Closed' else None
            if delta is not None:assert delta<1e-5,(slug,suffix,spec['name'],delta)
            checks.append({'part_id':spec['part_id'],'valid':True,'solids':len(shape.Solids),'bbox_delta_mm':delta})
        assert not [o.Name for o in doc.Objects if 'Invalid' in o.State]
        if suffix=='Complete':
            types=[o.TypeId for o in doc.Objects]
            row['editable_history']={'sketches':types.count('Sketcher::SketchObject'),'pads':types.count('PartDesign::Pad'),'fillets':types.count('PartDesign::Fillet'),'cuts':types.count('Part::Cut')}
            assert row['editable_history']['sketches'] and row['editable_history']['pads'] and row['editable_history']['cuts'],slug
        row['native_geometry'].append({'file':path.name,'components':len(checks),'max_manifest_bbox_delta_mm':max((c['bbox_delta_mm'] or 0) for c in checks),'checks':checks});row['files'][path.name]=sha(path);App.closeDocument(doc.Name)
    drawing=out/f'{prefix}_Drawings.FCStd'
    with zipfile.ZipFile(drawing) as archive:
        assert archive.testzip() is None
        xml=ET.fromstring(archive.read('Document.xml'));objects=xml.findall('./Objects/Object')
        page_count=sum(o.get('type')=='TechDraw::DrawPage' for o in objects);assert page_count==12
    row['native_drawing_pages']=page_count;row['files'][drawing.name]=sha(drawing)
    pdf=out/'drawings'/f'{prefix}_Drawings.pdf';info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
    assert re.search(r'^Pages:\s+12$',info,re.M)
    dimensions=re.search(r'Page size:\s+([\d.]+) x ([\d.]+) pts',info);assert dimensions and abs(float(dimensions[1])-1190.55)<1 and abs(float(dimensions[2])-841.89)<1
    row['pdf_pages']=12;row['files'][pdf.name]=sha(pdf)
    for name in m['step_files']:assert (out/name).exists();row['files'][name]=sha(out/name)
    with (out/'COMPONENTS.csv').open(encoding='utf-8-sig',newline='') as stream:assert len(list(csv.reader(stream)))-1==m['physical_components']
    for name in ['completion_audit','rebuild_verification','export_roundtrip_audit','native_drawings_audit','drawing_checks']:
        data=read(reports/(name+'.json'));assert passed(data),(slug,name);row['reports'][name+'.json']=sha(reports/(name+'.json'))
    visual=reports/'visual_acceptance.json'
    if visual.exists():
        data=read(visual);assert passed(data) and data['pdf_sha256']==sha(pdf);row['reports'][visual.name]=sha(visual)
    else:assert read(reports/'completion_audit.json')['pdf_checks'] is True
    glb=ROOT/'site/public/models'/f'{slug}.glb';web=read(glb.with_suffix('.json'))
    assert web['source_sha256']==sha(ROOT/web['source']) and web['sha256']==sha(glb)
    row['files'][glb.name]=sha(glb);row['passed']=True;result['devices'].append(row)
    print(json.dumps({'device':slug,'components':row['components'],'native_geometry_valid':True,'editable_history':row['editable_history'],'pdf_pages':12}),flush=True)
result.update(passed=True,total_devices=len(CAT),total_components=sum(d['components'] for d in result['devices']),total_solids=sum(d['solids'] for d in result['devices']),total_pdf_pages=84,elapsed_seconds=time.time()-result['started_unix'])
path=ROOT/'docs/seven_device_delivery_audit.json';path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='devices'}),flush=True)
