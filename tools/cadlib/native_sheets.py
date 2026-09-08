"""Self-contained TechDraw pages with native measurable endpoint references."""
import json,time,html
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Part,TechDraw
from PySide import QtCore
from .geometry import rotation,vec


def create_native_sheets(model):
    root=model.root;out=model.out;draw=out/'drawings';prefix=model.profile['prefix'];pages=json.loads((draw/'drawing_pages.json').read_text())
    QtCore.QThreadPool.globalInstance().setMaxThreadCount(1);Gui.activateWorkbench('TechDrawWorkbench')
    for group in ['General','Dimensions','Labels','Colors','Decoration','Hatching','Files','Scale','Advanced','Annotations']:App.ParamGet('User parameter:BaseApp/Preferences/Mod/TechDraw/'+group)
    doc=App.newDocument(prefix+'Drawings');doc.Label=model.profile['title']+' · A3 drawing sheets';checks=[]
    for page in pages:
        number=page['number'];title=html.escape(page['title'])
        template=draw/'source'/f'TechDraw_Template_{number:02d}.svg'
        template.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:freecad="http://www.freecad.org/wiki/index.php?title=Svg_Namespace" width="420mm" height="297mm" viewBox="0 0 420 297"><g fill="none" stroke="#504e49" stroke-width=".2"><rect x="8" y="8" width="404" height="281"/><path d="M 8 264 H 412 M 252 264 V 289 M 338 264 V 289"/></g><g font-family="Noto Serif CJK SC" fill="#141413"><text x="12" y="19" font-size="7.0">{title}</text><text x="12" y="278" font-size="4.0">{html.escape(model.profile['title'])} · CAD Study</text><text x="12" y="285" font-size="3.2">局部尺寸近似，内部为布局示意</text><text x="258" y="274" font-size="3.2">单位 mm · 比例见视图</text><text x="258" y="283" font-size="3.2">2026.09.08</text><text x="344" y="274" font-size="3.0">{prefix}-DWG-{number:02d}</text><text x="344" y="283" font-size="3.2">A3 · {number} / {len(pages)}</text></g></svg>''')
        pg=doc.addObject('TechDraw::DrawPage',f'Sheet{number:02d}');pg.Label=f'{number:02d} · '+page['title']
        t=doc.addObject('TechDraw::DrawSVGTemplate',f'Template{number:02d}');t.Template=str(template);pg.Template=t
        symbol=doc.addObject('TechDraw::DrawViewSymbol',f'VectorSheet{number:02d}');symbol.Symbol=(draw/page['svg']).read_text();symbol.Scale=1;symbol.X=210;symbol.Y=156;pg.addView(symbol)
        symbol.addProperty('App::PropertyString','SourceDescription','Trace');symbol.SourceDescription='Snapshot of model BRep projections and sections. Regenerate after model edits.'
        for i,dim in enumerate(page['dimensions'],1):
            spec=next(v for v in page['views'] if v['name']==dim['view']);q=rotation(spec['normal'],spec['up']).inverted()
            p1=q.multVec(vec(*dim['p1'])-vec(*spec['center']));p2=q.multVec(vec(*dim['p2'])-vec(*spec['center']));p1.z=p2.z=0
            src=doc.addObject('Part::Feature',f'ReferenceLine{number:02d}_{i}');src.Shape=Part.makeLine(p1,p2);src.Visibility=False
            view=doc.addObject('TechDraw::DrawViewPart',f'ReferenceView{number:02d}_{i}');view.Source=[src];view.Direction=vec(0,0,1);view.XDirection=vec(1,0,0);view.ScaleType='Custom';view.Scale=spec['scale'];pg.addView(view)
            view.X=12+spec['x']+(p1.x+p2.x)/2*spec['scale'];view.Y=263-spec['y']+(p1.y+p2.y)/2*spec['scale'];doc.recompute()
            deadline=time.time()+8
            while len(view.getVisibleVertexes())<2 and time.time()<deadline:
                loop=QtCore.QEventLoop();QtCore.QTimer.singleShot(20,loop.quit);loop.exec_();Gui.updateGui()
            assert len(view.getVisibleVertexes())==2
            n=doc.addObject('TechDraw::DrawViewDimension',f'Dimension{number:02d}_{i}');n.Type='DistanceX' if dim['axis']=='x' else 'DistanceY';n.References2D=[(view,('Vertex0','Vertex1'))];pg.addView(n)
            n.X=12+dim['label_position'][0];n.Y=263-dim['label_position'][1];n.Label=dim['label']+' mm · '+dim['view'];n.ShowUnits=True;doc.recompute()
            value=n.getRawValue();assert abs(value-dim['value_mm'])<1e-5,(number,i,value,dim['value_mm'])
            view.Visibility=False;n.Visibility=False;checks.append({'sheet':number,'dimension':n.Name,'expected_mm':dim['value_mm'],'measured_mm':value,'pass':True})
        doc.recompute();Gui.updateGui();doc.saveAs(str(out/(prefix+'_Drawings.FCStd')))
    invalid=[o.Name for o in doc.Objects if 'Invalid' in o.State];assert not invalid,invalid
    report={'pass':True,'pages':len(pages),'native_dimension_references':len(checks),'checks':checks,'invalid':invalid,'file':str(Path(doc.FileName).relative_to(model.repo)),'presentation':'Self-contained SVG sheets and native dimension references; rebuild sheets after edits to the 3D model.'}
    (out/'reports/native_drawings_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    App.setActiveDocument(model.doc.Name)
    print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False));return doc
