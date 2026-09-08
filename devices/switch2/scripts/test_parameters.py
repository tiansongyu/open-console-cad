App.setActiveDocument(D.Name)
# Locate by alias so the check remains valid if the sheet rows change.
cell=PARAM.getCellFromAlias('StickProjection');old=PARAM.getContents(cell)
keys=['JoyLStickStem','JoyRStickStem','JoyLStickCap','JoyRStickCap']
before={k:[C[k].Shape.Volume,C[k].Shape.optimalBoundingBox(False,False).ZMin,C[k].Shape.optimalBoundingBox(False,False).ZMax] for k in keys}
PARAM.set(cell,'11.0 mm');D.recompute()
changed={k:[C[k].Shape.Volume,C[k].Shape.optimalBoundingBox(False,False).ZMin,C[k].Shape.optimalBoundingBox(False,False).ZMax] for k in keys}
invalid_during=[o.Name for o in D.Objects if 'Invalid' in o.State]
PARAM.set(cell,old);D.recompute()
after={k:[C[k].Shape.Volume,C[k].Shape.optimalBoundingBox(False,False).ZMin,C[k].Shape.optimalBoundingBox(False,False).ZMax] for k in keys}
invalid_after=[o.Name for o in D.Objects if 'Invalid' in o.State]
assert not invalid_during and not invalid_after
assert all(abs(changed[k][2]-before[k][2]-.2)<1e-6 for k in keys)
assert all(max(abs(a-b) for a,b in zip(before[k],after[k]))<1e-7 for k in keys)
RESULT={'pass':True,'parameter':'StickProjection','original':old,'tested':'11.0 mm','keys':keys,'before':before,'changed':changed,'restored':after,'invalid_during':invalid_during,'invalid_after':invalid_after}
(OUT/'reports/parameter_edit_test.json').write_text(json.dumps(RESULT,ensure_ascii=False,indent=2));D.save()

print(json.dumps(RESULT,ensure_ascii=False))
