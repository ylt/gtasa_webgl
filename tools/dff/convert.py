import uuid
import json
import os
import parse
import random

class convert():
    @staticmethod
    def convert(filename):
        return convert(filename).data
        
    # data
    def __init__(self, filename):
        self.data = {
            "metadata": {
                "version": 4.3,
                "type": "Object",
                "generator": "ObjectExporter"
            },
            "geometries": [
            ],
            "materials":[{"type": "MeshFaceMaterial", "materials":[]}],
        }
        
        self.objects = []
        
        rw = parse.ImportRenderware(filename)
        
        for frame in rw.childrenOf[0]:
            self.build_frame(rw.frames[frame], self.objects)
            
            
        if len(self.objects) > 1:
            self.data["object"] =  {
                "uuid": str(uuid.uuid4()),
                "type": "Object3D",
                "matrix": [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
                "children":[self.objects],
                "name":os.path.basename(filename)
            }
        else:
            self.data["object"] = self.objects[0]
            
    def convert_rgb(self, r,g,b):
        return (int(b) << 16) + (int(g) << 8) + int(r),
    
    def build_texture(self, texture):
        {
            "url":"url"
        }
    
    def build_material(self, uuid, mat, geometry):
        mat.col = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)
        self.data["materials"][0]["materials"].append({
            "uuid":uuid,
            "type":"MeshPhongMaterial",
            #"type":"MeshBasicMaterial",
            "color":self.convert_rgb(mat.col[0], mat.col[1], mat.col[2]),
            "transparency": mat.col[3]/255,
            "emissive": self.convert_rgb(mat.col[0], mat.col[1], mat.col[2]),
            "ambient": self.convert_rgb(mat.col[0]/255*mat.ambient, mat.col[1]/255*mat.ambient, mat.col[2]/255*mat.ambient),
            "specular": self.convert_rgb(mat.col[0]*mat.specular, mat.col[1]*mat.specular, mat.col[2]*mat.specular),
            "vertexColors": geometry.vertCol,
            "shading": "Phong"
        })
        return len(self.data["materials"][0]["materials"])-1
    
    def build_geometry(self, g_uuid, geometry, frame):
        geo = {
            "uuid": g_uuid,
            "type": "Geometry",
            "data": {
                "vertices": [],
                "faces": [],
                "normals": []
                #uv
            }
        }
        self.data["geometries"].append(geo)
        
        
        mats = []
        for mat in geometry.materials:
            m_uuid = str(uuid.uuid4())
            m_id = self.build_material(m_uuid, mat, geometry)
            mats.append(m_id)
            
        vertices = geo["data"]["vertices"]
        normals = geo["data"]["normals"]
        faces = geo["data"]["faces"]
        
        for vertex in geometry.vertices:
            vertices.extend(vertex.desc() or [])
            normals.extend(vertex.normal or [])
            
        for triangle in geometry.triangles:
            faces.append(2)
            faces.extend(triangle.desc())
            faces.append(mats[triangle.mat])
            
    def build_frame(self, frame, parent):
        
        ob = {
            "uuid": str(uuid.uuid4()),
            "name": frame.name,
            "type": "Object3D",
            #"matrix": [item for sublist in frame.matrix for item in sublist]
        }
        #print(frame.matrix)
        #print([item for sublist in frame.matrix for item in sublist])
        parent.append(ob)    
        
        matrix = []
        for y in range(0,4):
            for x in range(0,4):
                matrix.append(frame.matrix[x][y])
        
        ob["matrix"] = matrix  
        
        if frame.geometry:
            ob["type"] = "Mesh"
            ob["geometry"] = str(uuid.uuid4())
            
            self.build_geometry(ob["geometry"], frame.geometry, frame)
        
        if "_vlo" in frame.name or "_dam" in frame.name:
            ob["visible"]=False
        
        if len(frame.loader.childrenOf[frame.index+1]) > 0:
            ob["children"] = []
            for c_frame in frame.loader.childrenOf[frame.index+1]:
                self.build_frame(frame.loader.frames[c_frame], ob["children"])