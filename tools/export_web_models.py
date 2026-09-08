"""Export actual FreeCAD component BReps to a colored, named glTF 2.0 GLB.

Run in the FreeCAD Python console or via freecad-mcp:
    exec(open('/path/open-console-cad/tools/export_web_models.py').read())
    export_device('/path/open-console-cad', 'switch')
The web representation uses meters. FCStd and STEP retain millimeters.
"""
from pathlib import Path
import json, math, struct, array, hashlib
import FreeCAD as App
import MeshPart


def export_device(repository, device, deflection=0.25):
    if device not in ('switch','switch2'):
        raise ValueError('Unknown device')
    root=Path(repository).resolve();folder=root/'devices'/device
    manifest=json.loads((folder/'output/reports/final_manifest.json').read_text())
    filename=folder/'output'/manifest['native_files'][0]
    doc=next((d for d in App.listDocuments().values() if d.FileName==str(filename)),None)
    owned=doc is None
    if owned:doc=App.openDocument(str(filename))
    binary=bytearray()
    gltf={'asset':{'version':'2.0','generator':'Open Console CAD / FreeCAD BRep tessellation'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'materials':[],'buffers':[],'bufferViews':[],'accessors':[]}
    colors={};triangle_count=0
    def accessor(values,kind,count,component,target,extents=None):
        while len(binary)%4:binary.append(0)
        offset=len(binary);raw=array.array(kind,values)
        import sys
        if sys.byteorder!='little':raw.byteswap()
        binary.extend(raw.tobytes());view=len(gltf['bufferViews'])
        gltf['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(raw)*raw.itemsize,'target':target})
        item={'bufferView':view,'componentType':component,'count':count,'type':'SCALAR' if kind=='I' else 'VEC3'}
        if extents:item.update(min=extents[0],max=extents[1])
        gltf['accessors'].append(item);return len(gltf['accessors'])-1
    try:
        for row in manifest['objects']:
            obj=doc.getObject(row['name']);shape=obj.Shape
            mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=deflection,AngularDeflection=0.45,Relative=False)
            vertices,triangles=mesh.Topology
            if not vertices or not triangles:raise ValueError('No mesh for '+row['part_id'])
            b=shape.optimalBoundingBox(False,False);c=b.Center
            pts=[((v.x-c.x)/1000,(v.y-c.y)/1000,(v.z-c.z)/1000) for v in vertices]
            # Split vertices across hard edges, keeping curved faces smooth.
            clusters=[[] for _ in pts];new_points=[];normals=[];new_triangles=[]
            for i,j,k in triangles:
                pa,pb,pc=pts[i],pts[j],pts[k]
                u=[pb[t]-pa[t] for t in range(3)];v=[pc[t]-pa[t] for t in range(3)]
                n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
                length=math.sqrt(sum(x*x for x in n));unit=[x/length for x in n] if length else [0.,0.,1.]
                tri=[]
                for index in (i,j,k):
                    match=next((entry for entry in clusters[index] if sum(a*b for a,b in zip(entry[0],unit))>0.766044),None)
                    if match is None:
                        match=(unit,len(new_points));clusters[index].append(match);new_points.append(pts[index]);normals.append([0.,0.,0.])
                    ni=match[1];tri.append(ni)
                    for axis in range(3):normals[ni][axis]+=n[axis]
                new_triangles.append(tri)
            pts=new_points;triangles=new_triangles
            for n in normals:
                length=math.sqrt(sum(x*x for x in n))
                if length:
                    for axis in range(3):n[axis]/=length
                else:n[2]=1.
            appearance=obj.ViewObject.ShapeAppearance
            color=tuple(round(float(x),5) for x in appearance[0].DiffuseColor[:3])
            role=row['material'];signature=(color,role)
            if signature not in colors:
                colors[signature]=len(gltf['materials'])
                gltf['materials'].append({'name':role,'doubleSided':False,'pbrMetallicRoughness':{'baseColorFactor':[(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4) for x in color]+[1.0],'metallicFactor':0.65 if role in ['metal','gold','copper'] else 0.05,'roughnessFactor':0.3 if role in ['metal','screen'] else 0.65}})
            amin=[min(p[a] for p in pts) for a in range(3)];amax=[max(p[a] for p in pts) for a in range(3)]
            position=accessor([v for p in pts for v in p],'f',len(pts),5126,34962,(amin,amax))
            normal=accessor([v for n in normals for v in n],'f',len(normals),5126,34962)
            indices=accessor([v for tri in triangles for v in tri],'I',len(triangles)*3,5125,34963)
            mi=len(gltf['meshes']);gltf['meshes'].append({'name':row['part_number'],'primitives':[{'attributes':{'POSITION':position,'NORMAL':normal},'indices':indices,'material':colors[signature]}]})
            gltf['scenes'][0]['nodes'].append(len(gltf['nodes']))
            gltf['nodes'].append({'name':row['part_id'],'mesh':mi,'translation':[c.x/1000,c.y/1000,c.z/1000],'extras':{'partId':row['part_id'],'partNumber':row['part_number'],'label':obj.Label,'assembly':row['assembly'],'material':role,'explodeOffset':[v/1000 for v in manifest['offsets'][row['part_id']]]}})
            triangle_count+=len(triangles)
        gltf['buffers']=[{'byteLength':len(binary)}]
        encoded=json.dumps(gltf,ensure_ascii=False,separators=(',',':')).encode()
        encoded+=b' '*((-len(encoded))%4);binary+=b'\0'*((-len(binary))%4)
        payload=struct.pack('<III',0x46546c67,2,12+8+len(encoded)+8+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary
        dest=root/'site/public/models';dest.mkdir(parents=True,exist_ok=True);file=dest/(device+'.glb');file.write_bytes(payload)
        report={'device':device,'components':len(gltf['nodes']),'triangles':triangle_count,'materials':len(colors),'bytes':len(payload),'deflection_mm':deflection,'units':'meters','color_conversion':'FreeCAD sRGB to glTF linear RGB','normal_crease_degrees':40,'source':str(filename.relative_to(root)),'source_sha256':hashlib.sha256(filename.read_bytes()).hexdigest(),'sha256':hashlib.sha256(payload).hexdigest(),'preserved':['part IDs','part numbers','assembly groups','colors','exploded offsets']}
        (dest/(device+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report))
        return report
    finally:
        if owned:App.closeDocument(doc.Name)
