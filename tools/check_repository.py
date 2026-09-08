"""Check publishable assets, GLB identity/structure, CAD archives and source syntax."""
from pathlib import Path
import ast, hashlib, json, struct, zipfile
ROOT=Path(__file__).resolve().parents[1]
for device,count in [('switch',654),('switch2',799)]:
    folder=ROOT/'devices'/device;report=json.loads((ROOT/'site/public/models'/f'{device}.json').read_text())
    manifest=json.loads((folder/'output/reports/final_manifest.json').read_text())
    glb=(ROOT/'site/public/models'/f'{device}.glb').read_bytes()
    magic,version,length=struct.unpack_from('<III',glb);assert magic==0x46546c67 and version==2 and length==len(glb)
    size,kind=struct.unpack_from('<II',glb,12);assert kind==0x4e4f534a
    doc=json.loads(glb[20:20+size]);assert len(doc['nodes'])==count==manifest['physical_components']==report['components']
    assert {n['extras']['partId'] for n in doc['nodes']}=={r['part_id'] for r in manifest['objects']}
    for n in doc['nodes']:assert len(n['extras']['explodeOffset'])==3 and len(n['translation'])==3
    assert hashlib.sha256(glb).hexdigest()==report['sha256']
    source=ROOT/report['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==report['source_sha256']
    for p in (folder/'output').glob('*.FCStd'):
        with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
    for filename in manifest['step_files']:assert (folder/'output'/filename).stat().st_size>1000
    for p in folder.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
    for p in folder.glob('*.FCMacro'):ast.parse(p.read_text(),filename=str(p))
    for image in ['hero','rear','internal','exploded','dock']:assert (ROOT/'site/public/images'/device/f'{image}.webp').exists()
    prefix='Switch' if device=='switch' else 'Switch2'
    assert (folder/'output/drawings'/f'{prefix}_Drawings.pdf').read_bytes().startswith(b'%PDF-')
    for p in folder.rglob('*'):
        if p.is_file():
            assert p.stat().st_size<100*1024*1024,p
            if p.suffix in ['.py','.md','.json','.FCMacro']:assert '/home/ubuntu/' not in p.read_text(),p
    print(f'{device}: {count} component identities, GLB hashes, FCStd archives and sources OK')
print('Repository checks passed')
