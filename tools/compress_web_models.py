"""Create and verify a lossless gzip preview alongside an exported GLB."""
from pathlib import Path
import argparse,gzip,hashlib,json,re

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('device');args=parser.parse_args()
assert re.fullmatch(r'[a-z0-9][a-z0-9-]*',args.device), 'Invalid device identifier'
path=root/'site/public/models'/f'{args.device}.glb';raw=path.read_bytes()
meta=json.loads(path.with_suffix('.json').read_text())
assert hashlib.sha256(raw).hexdigest()==meta['sha256'], 'Re-export the GLB before compression'
compressed=gzip.compress(raw,compresslevel=9,mtime=0)
assert gzip.decompress(compressed)==raw
path.with_suffix('.glb.gz').write_bytes(compressed)
meta['gzip']={'bytes':len(compressed),'sha256':hashlib.sha256(compressed).hexdigest(),'decoded_sha256':meta['sha256'],'lossless':True}
path.with_suffix('.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
report=root/'devices'/args.device/'output/reports/web_export.json'
if report.exists():report.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'device':args.device,'raw_bytes':len(raw),'gzip':meta['gzip']},ensure_ascii=False))
