"""Numerical STEP checks with explicit geometric confirmation of bound anomalies.

OCCT's analytic bounds can differ after trimmed B-spline STEP conversion even
when the solids have empty differences. Such a discrepancy is never silently
ignored: require valid bidirectional Boolean differences and matching sampled
bounds at two deflections, preserving the original discrepancy in the report.
"""

def bounds(shape):
    b=shape.optimalBoundingBox(False,False)
    return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]


def sampled_bounds(shape,deflection):
    points,_=shape.tessellate(deflection)
    if not points:raise ValueError('No tessellation vertices')
    axes=[[getattr(p,axis) for p in points] for axis in ['x','y','z']]
    return [min(a) for a in axes]+[max(a) for a in axes],len(points)


def compare_solids(source,imported,tolerance=1e-6):
    delta=imported.Volume-source.Volume
    bd=max(abs(a-b) for a,b in zip(bounds(source),bounds(imported)))
    check={'bbox_max_delta_mm':bd,'volume_delta_mm3':delta,'valid':imported.isValid(),
           'boolean_confirmation':None,'sampled_bounds_confirmation':None}
    if abs(delta)>tolerance or bd>=tolerance:
        differences=[source.cut(imported),imported.cut(source)]
        residuals=[sum(abs(s.Volume) for s in diff.Solids) for diff in differences]
        valid=all(diff.isValid() for diff in differences)
        check['boolean_confirmation']={'residual_volumes_mm3':residuals,'valid':valid,'pass':valid and max(residuals)<tolerance}
    bounds_pass=bd<tolerance
    if not bounds_pass and check['boolean_confirmation']['pass']:
        samples=[]
        for deflection in [.01,.005]:
            a,na=sampled_bounds(source.copy(),deflection);b,nb=sampled_bounds(imported.copy(),deflection)
            maximum=max(abs(x-y) for x,y in zip(a,b))
            samples.append({'deflection_mm':deflection,'source_bounds_mm':a,'step_bounds_mm':b,
                            'source_vertices':na,'step_vertices':nb,'max_delta_mm':maximum,'pass':maximum<tolerance})
        bounds_pass=all(row['pass'] for row in samples)
        check['sampled_bounds_confirmation']={'pass':bounds_pass,'checks':samples,
            'basis':'Analytic bounds discrepancy additionally requires empty bidirectional Boolean differences and sampled-bound agreement at both deflections.'}
    check['pass']=check['valid'] and bounds_pass and (check['boolean_confirmation'] is None or check['boolean_confirmation']['pass'])
    return check
