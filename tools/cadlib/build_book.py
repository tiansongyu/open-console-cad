"""Fill the copied Kami long-document template and use Kami's PDF build pipeline."""
from pathlib import Path
import json,html,re,sys,os
ROOT=Path(sys.argv[1]).resolve();DRAW=ROOT/'output/drawings'
manifest=json.loads((ROOT/'output/reports/final_manifest.json').read_text());prefix=manifest['prefix']
approximate_envelope=manifest.get('envelope_kind')=='approximate'
dimension_note='全部尺寸均为本模型学习近似值，不能用作制造公差或真实电子规格。' if approximate_envelope else '公开整体尺寸已注明来源，局部近似数字不能用作制造公差或真实电子规格。'
fidelity_note='全部尺寸为本模型近似值 · 内部为布局示意' if approximate_envelope else '局部尺寸为本模型近似值 · 内部为布局示意'
KAMI=Path(os.environ.get('KAMI_HOME','~/.codex/skills/kami')).expanduser();sys.path.insert(0,str(KAMI/'scripts'))
from render import render_pdf
pages=json.loads((DRAW/'drawing_pages.json').read_text());ir=json.loads((DRAW/'content.json').read_text())
assert len(pages)==12

for i,page in enumerate(pages[1:11]):
 ch=ir['content']['chapters'][i];ch['title']=page['title'];ch['claim']=page['notes'][0]+page['notes'][1]
 if len(ch['claim'])<40:ch['claim']+='可在原生文件中对照相同零件编号。'
 ch['paragraphs']=[page['notes'][0]+' 图中尺寸单位统一为 mm，数字对应当前模型的几何和坐标。'+dimension_note,page['notes'][1]+' 爆炸位移用于区分装配层，缩放视图不会改变尺寸数字。每个零件编号都可在组件清单中检索，重新修改模型后应同步重建这些图纸。']
 ch.pop('figure',None)
# A native CAD artifact is the required visual source, so no separate external hero is needed.
ir['brief']['required_assets']=[]
(DRAW/'content.json').write_text(json.dumps(ir,ensure_ascii=False,indent=2))
template=(DRAW/'source/kami_long_doc_template.html').read_text();head=template.split('<body>',1)[0]
for key,value in {'{{文档标题}}':ir['content']['title'],'{{作者}}':'CAD Study','{{摘要}}':ir['content']['summary']['claim'],'{{关键词}}':ir['content']['title']+', FreeCAD, CAD'}.items():head=head.replace(key,value)
# Keep Kami's type/color system; make an explicit A3 landscape drawing adaptation.
head=re.sub(r'@font-face\s*\{.*?\}', '',head,flags=re.S)
style='''<style>
@page {size:A3 landscape;margin:12mm 12mm 10mm;background:#f5f4ed;@top-right{content:""}@bottom-center{content:""}}
@page:first{@top-right{content:""}@bottom-center{content:""}}
html,body {margin:0;padding:0;max-width:none;font-family:"TsangerJinKai02","Noto Serif CJK SC",serif;font-size:10pt;letter-spacing:.1pt;}
.drawing-sheet {height:275mm;position:relative;break-before:page;break-inside:avoid;}
.drawing-sheet:first-child {break-before:auto;}
.drawing-header {height:22mm;}
.eyebrow {font-size:9pt;line-height:1.35;color:#1B365D;letter-spacing:.3pt;}
.drawing-header h1 {font-size:22pt;line-height:1.2;font-weight:500;margin:1mm 0;padding:0;border:0;}
.drawing-header .claim {font-size:9pt;line-height:1.35;color:#504e49;margin:0;}
.drawing-figure {height:214mm;margin:0;}
.drawing-figure svg {width:396mm;height:214mm;max-width:none;display:block;}
.drawing-notes {margin-top:2mm;font-size:9pt;line-height:1.35;}
.drawing-notes p {font-size:9pt;line-height:1.35;margin:0 0 1mm;}
.title-block {position:absolute;bottom:0;left:0;right:0;height:18mm;border-top:.25mm solid #504e49;display:grid;grid-template-columns:1.6fr 1fr .8fr;column-gap:6mm;padding-top:2mm;font-size:9pt;line-height:1.35;color:#504e49;}
.title-block .title {color:#141413;font-size:10pt;}
</style>'''
head=head.replace('</head>',style+'</head>')
body=[]
for i,page in enumerate(pages):
 if i==0:
  claim=ir['content']['summary']['claim'];notes=ir['content']['summary']['takeaways'];notes=[' '.join(notes[:2]),notes[2]]
 elif i==11:
  claim='本模型的工作尺寸和内部布局均为学习近似值，检查证据随工程一并交付。' if approximate_envelope else '公开尺寸、局部近似值与内部布局示意分开记录，检查证据随工程一并交付。'
  notes=[ir['content']['references'][0],ir['content']['references'][1]]
 else:
  ch=ir['content']['chapters'][i-1];claim=ch['claim'];notes=ch['paragraphs']
 svg=(DRAW/page['svg']).read_text().replace('rgb(0, 0, 0)','#141413').replace('#000000','#141413')
 body.append(f'''<section class="drawing-sheet" id="sheet-{i+1:02d}"><div class="drawing-header"><div class="eyebrow">{html.escape(ir['content']['subtitle'])} <span style="float:right">{prefix}-DWG-{i+1:02d} / 12</span></div><h1>{html.escape(page['title'])}</h1><p class="claim">{html.escape(claim)}</p></div><figure class="drawing-figure">{svg}</figure><div class="drawing-notes">{''.join('<p>'+html.escape(x)+'</p>' for x in notes)}</div><div class="title-block"><div><div class="title">{html.escape(ir['content']['title'])}</div><div>{fidelity_note}</div></div><div>单位 mm · 比例见各视图<br>CAD Study · {html.escape(ir['content']['date'])}</div><div>图号 {prefix}-DWG-{i+1:02d}<br>第 {i+1} / 12 页 · A3</div></div></section>''')
# Resolve the copied template tokens to literal values so static content visibility is provable.
declared=dict(re.findall(r'(--[\w-]+)\s*:\s*([^;]+);',head))
for _ in range(8):head=re.sub(r'var\((--[\w-]+)\)',lambda m:declared.get(m.group(1),m.group(0)),head)
filled=head+'<body>'+''.join(body)+'</body></html>'
filled='\n'.join(line.rstrip() for line in filled.splitlines())+'\n'
assert not re.search(r'\{\{[^{}]*\}\}',filled)
out=DRAW/(prefix+'_Drawings.html');out.write_text(filled)
count=render_pdf(out,DRAW/(prefix+'_Drawings.pdf'));assert count==12,count
print(json.dumps({'pages':count,'html':str(out),'pdf':str(DRAW/(prefix+'_Drawings.pdf')),'pipeline':'Kami render_pdf'},ensure_ascii=False))
