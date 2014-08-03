import uuid
import os
import readers.dff
import random

GEOM_QUAD              = 0b00000001
GEOM_FACE_MATERIAL     = 0b00000010
GEOM_FACE_UV           = 0b00000100
GEOM_FACE_VERTEX_UV    = 0b00001000
GEOM_FACE_NORMAL       = 0b00010000
GEOM_FACE_VERTEX_NORMAL= 0b00100000
GEOM_FACE_COLOR        = 0b01000000
GEOM_FACE_VERTEX_COLOR = 0b10000000

class convert():
    @staticmethod
    def convert(filename, txdpath):
        return convert(filename, txdpath).data
        
    # data
    def __init__(self, filename, txdpath, randCols=False):
        self.data = {
            "metadata": {
                "version": 4.3,
                "type": "Object",
                "generator": "ObjectExporter"
            },
            "geometries": [
            ],
            "materials":[{"type": "MeshFaceMaterial", "materials":[]}],
            "textures":[],
            "images":[]
        }
        self.randCols = randCols
        self.txdpath = txdpath
        
        self.objects = []
        
        rw = readers.dff.ImportRenderware(filename)
        
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
    
    #def build_image(self, image):
    #    for d in self.data["images"]:
            
    #engine will properly finish texture construction during runtime
    def build_texture(self, texture, t_uuid):
        i_uuid = str(uuid.uuid4())
        self.data["textures"].append({
            "uuid":t_uuid,
            "intensity":texture.intensity, #not sure how to use
            "image":i_uuid
        })
        
        self.data["images"].append({
            "uuid":i_uuid,
            "url":"data/textures/"+texture.name+".png",
        })
    
    def build_material(self, m_uuid, mat, geometry):
        if self.randCols:
            mat.col = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)
        material = {
            "uuid":m_uuid,
            #"type":"MeshNormalMaterial",
            "type":"MeshPhongMaterial",
            "Dbgcolor":(mat.col[0], mat.col[1], mat.col[2]),
            #"transparency": mat.col[3]/255,
            #"colorEmissive": (mat.col[0], mat.col[1], mat.col[2]),
            #"specularCoef": 100,
            #"colorAmbient": self.convert_rgb(mat.col[0]/255*mat.ambient, mat.col[1]/255*mat.ambient, mat.col[2]/255*mat.ambient),
            #"colorSpecular": (mat.col[0]*mat.specular, mat.col[1]*mat.specular, mat.col[2]*mat.specular),
            #"vertexColors": geometry.vertCol,
            #"shading": "lambert"
            "colorAmbient" : [0.5, 0.5, 0.5],
            "colorDiffuse" : [0.6400000190734865, 0.6400000190734865, 0.6400000190734865],
            "colorSpecular" : [0.5, 0.5, 0.5],
            "specularCoef" : 12,
        }
        
        if mat.texture:
            #t_uuid = str(uuid.uuid4())
            #self.build_texture(mat.texture, t_uuid)
            material["mapDiffuse"] = "data/textures/"+mat.texture.name+".png",
        
        self.data["materials"][0]["materials"].append(material)
        
        return len(self.data["materials"][0]["materials"])-1
    
    def build_geometry(self, g_uuid, geometry, frame):
        geo = {
            "uuid": g_uuid,
            "type": "Geometry",
            "data": {
                "vertices": [],
                "faces": [],
                "normals": [],
                "uvs": [[]]
            }
        }
        self.data["geometries"].append(geo)
        
        
        mats = []
        for mat in geometry.materials:
            m_uuid = str(uuid.uuid4())
            m_id = self.build_material(m_uuid, mat, geometry)
            mats.append(m_id)
            
        vertices = geo["data"]["vertices"]
        uvs = geo["data"]["uvs"][0]
        normals = geo["data"]["normals"]
        faces = geo["data"]["faces"]
        
        for vertex in geometry.vertices:
            vertices.extend(vertex.desc() or [])
            normals.extend(vertex.normal or [])
            uvs.extend(vertex.uv or [])
            
        for triangle in geometry.triangles:
            faces.append(GEOM_FACE_MATERIAL | GEOM_FACE_VERTEX_NORMAL | GEOM_FACE_VERTEX_UV)
            faces.extend(triangle.desc())
            faces.append(mats[triangle.mat])
            faces.extend(triangle.desc())
            faces.extend(triangle.desc())
            
            
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
        
        if not frame.name or "_vlo" in frame.name or "_dam" in frame.name:
            ob["visible"]=False
        
        if len(frame.loader.childrenOf[frame.index+1]) > 0:
            ob["children"] = []
            for c_frame in frame.loader.childrenOf[frame.index+1]:
                self.build_frame(frame.loader.frames[c_frame], ob["children"])
