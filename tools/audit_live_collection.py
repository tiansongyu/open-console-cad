"""Verify published collection assets and downloadable CAD against local SHA-256."""
from pathlib import Path
import hashlib,json,subprocess,time
import requests
ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/'site/src/catalog.json').read_text());assert len(CAT)==27
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
base='https://tiansongyu.github.io/open-console-cad/'
raw=f'https://raw.githubusercontent.com/tiansongyu/open-console-cad/{commit}/'
tasks=[]
def add(path,url):
 assert path.is_file(),path
 tasks.append((path,url))
for p in [ROOT/'dist/index.html',*sorted((ROOT/'dist/assets').glob('*'))]:add(p,base+str(p.relative_to(ROOT/'dist')))
for d in CAT:
 slug=d['id'];root=ROOT/'devices'/slug;out=root/'output';m=json.loads((out/'reports/final_manifest.json').read_text());prefix=d['prefix']
 for name in [f'{slug}.glb',f'{slug}.json']+([f'{slug}.glb.gz'] if d.get('gzip') else []):
  p=ROOT/'site/public/models'/name;add(p,base+'models/'+name)
 for p in sorted((ROOT/'site/public/images'/slug).glob('*.webp')):add(p,base+'images/'+slug+'/'+p.name)
 files=[root/'README.md',root/f'Open_{prefix}.FCMacro',root/f'Rebuild_{prefix}.FCMacro',out/'COMPONENTS.csv',out/'drawings'/f'{prefix}_Drawings.pdf']
 files += [out/f'{prefix}_{suffix}.FCStd' for suffix in ['Complete','Exploded','Drawings']]
 html=out/'drawings'/f'{prefix}_Drawings.html'
 if html.exists():files.append(html)
 study=out/f'{prefix}_Study.FCStd'
 if study.exists():files.append(study)
 files += [out/name for name in m['step_files']]
 if d['family']=='clamshell':files.append(out/f'{prefix}_Closed.FCStd')
 for p in files:assert p.is_file(),p;add(p,raw+str(p.relative_to(ROOT)))
 # Exercise the same moving-main URLs used by the visible CAD/PDF download buttons.
 for p in [out/f'{prefix}_Complete.FCStd',out/'drawings'/f'{prefix}_Drawings.pdf']:
  add(p,'https://github.com/tiansongyu/open-console-cad/raw/refs/heads/main/'+str(p.relative_to(ROOT)))
def check(item):
 p,url=item;expected=hashlib.sha256(p.read_bytes()).hexdigest();row=dict(path=str(p.relative_to(ROOT)),url=url,expected_sha256=expected)
 for attempt in range(3):
  try:
   with requests.get(url,timeout=(20,120)) as r:
    payload=r.content;actual=hashlib.sha256(payload).hexdigest()
    row.update(status=r.status_code,bytes=len(payload),sha256=actual,passed=r.status_code==200 and actual==expected)
   if row['passed']:return row
  except requests.RequestException as e:row.update(passed=False,error=str(e))
 return row
result=dict(passed=False,release_commit=commit,devices=len(CAT),scope='Published index/assets, all device models/gallery images and every listed native CAD/STEP/PDF/HTML/component/macro download; actual response bytes compared to local SHA-256.',started_unix=time.time(),files=[])
for item in tasks:
 row=check(item);result['files'].append(row);print(json.dumps(dict(path=row['path'],passed=row['passed'])),flush=True)
result['files'].sort(key=lambda x:x['path']);result.update(passed=all(x['passed'] for x in result['files']),elapsed_seconds=time.time()-result['started_unix'],file_count=len(tasks))
(ROOT/'docs/collection_live_delivery_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if result['passed'] else 1)
