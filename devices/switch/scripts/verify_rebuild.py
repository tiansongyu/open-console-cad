# Fresh namespace and fresh document: compare every rebuilt physical part against delivery.
original_doc=D
expected={k:o.Shape.copy() for k,o in C.items()}
ns={'App':App,'Gui':Gui,'__name__':'__switch_rebuild_check__','PROJECT_ROOT':str(ROOT),'PROJECT_OUTPUT':str(ROOT/'output/rebuild_verification')}
progress=OUT/'reports/rebuild_progress.json'
for p in sorted((ROOT/'scripts').glob('iter[0-9][0-9]_*.py')):
    progress.write_text(json.dumps({'state':'running','stage':p.name,'time':time.time()}))
    exec(compile(p.read_bytes(),str(p),'exec'),ns)
rebuilt=ns['C'];checks=[]
assert set(rebuilt)==set(expected)
for key,o in rebuilt.items():
    a=expected[key];b=o.Shape
    delta=b.Volume-a.Volume
    ad=a.optimalBoundingBox(False,False);bd=b.optimalBoundingBox(False,False)
    box_delta=max(abs(getattr(ad,v)-getattr(bd,v)) for v in ['XMin','XMax','YMin','YMax','ZMin','ZMax'])
    check={'part_id':key,'valid':b.isValid(),'solid_match':len(b.Solids)==len(a.Solids),'volume_delta_mm3':delta,'bbox_max_delta_mm':box_delta}
    if abs(delta)>1e-4:
        check['boolean_difference_mm3']=[sum(s.Volume for s in a.cut(b).Solids),sum(s.Volume for s in b.cut(a).Solids)]
    check['pass']=check['valid'] and check['solid_match'] and box_delta<1e-6 and (abs(delta)<1e-4 or max(check['boolean_difference_mm3'])<1e-6)
    checks.append(check)
assert all(r['pass'] for r in checks)
ns['D'].saveAs(str(ROOT/'output/rebuild_verification/Switch_Rebuilt.FCStd'))
RESULT={'pass':True,'stages':14,'physical_components':len(rebuilt),'max_volume_delta_mm3':max(abs(x['volume_delta_mm3']) for x in checks),'max_bbox_delta_mm':max(x['bbox_max_delta_mm'] for x in checks),'checks':checks}
(OUT/'reports/rebuild_verification.json').write_text(json.dumps(RESULT,ensure_ascii=False,indent=2))
progress.write_text(json.dumps({'state':'done','pass':True,'time':time.time()}))
App.closeDocument(ns['D'].Name);App.setActiveDocument(original_doc.Name)
RESULT={k:v for k,v in RESULT.items() if k!='checks'}
