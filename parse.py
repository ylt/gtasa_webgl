bl_info = {
    "name": "RenderWare importer/exporter for GTA III/VC/SA (.dff)",
    "author": "Ago Allikmaa (maxorator)",
    "version": (0, 9, 2),
    "blender": (2, 6, 3),
    "location": "File > Import-Export > Renderware (.dff) ",
    "description": "RenderWare importer/exporter for GTA III/VC/SA",
    "category": "Import-Export" }

import struct
import zlib
import base64

from collections import deque

import mathutils
    
class RwTypes():
    ANY = -1
    
    STRUCT = 0x0001
    STRING = 0x0002
    EXTENSION = 0x0003
    TEXTURE = 0x0006
    MATERIAL = 0x0007
    MATERIALLIST = 0x0008
    FRAMELIST = 0x000E
    GEOMETRY = 0x000F
    CLUMP = 0x0010
    ATOMIC = 0x0014
    GEOMETRYLIST = 0x001A
    RENDERRIGHTS = 0x001F
    
    MORPHPLG = 0x0105
    SKINPLG = 0x116
    HANIMPLG = 0x11E
    MATEFFECTS = 0x0120
    BINMESHPLG = 0x050E
    FRAMENAME = 0x253F2FE
    COLLISION = 0x253F2FA
    MATSPECULAR = 0x253F2F6
    NIGHTCOLS = 0x253F2F9
    MATREFLECTION = 0x253F2FC
    MESHEXTENSION = 0x253F2FD
    
    def decodeVersion(version):
        if (version & 0xFFFF0000) == 0:
            return version << 8
        else:
            p1 = ((version >> 14) & 0x3FF00) + 0x30000
            p2 = (version >> 16) & 0x3F
            
            return p1 | p2
            
class RpGeomFlag:
    TRISTRIP = 0x0001
    POSITIONS = 0x0002
    TEXTURED = 0x0004
    PRELIT = 0x0008
    NORMALS = 0x0010
    LIGHT = 0x0020
    MODULATEMATERIALCOLOR = 0x0040
    TEXTURED2 = 0x0080

class ImportRenderware:
    class RwTriangle:
        def __init__(self, verts, mat):
            self.verts = verts
            self.mat = mat
            
        def desc(self):
            return (self.verts[0], self.verts[1], self.verts[2])
            
    class RwVertex:
        def __init__(self, coords, normal):
            self.coords = coords
            self.normal = normal
            self.uv = None
            self.uv_env = None
            
        def desc(self):
            return (self.coords[0], self.coords[1], self.coords[2])
    
    class RwFrame:
        def __init__(self, loader, index, rot, pos, parent):
            self.loader = loader
            self.index = index
            
            self.geometry = None
            self.atomic = None
            
            self.blobj = None
            self.bldata = None
            
            self.hanimdata = None
            
            self.name = None
            
            rmatrix = mathutils.Matrix.Identity(3)
            rmatrix[0] = rot[0], rot[1], rot[2]
            rmatrix[1] = rot[3], rot[4], rot[5]
            rmatrix[2] = rot[6], rot[7], rot[8]
            rmatrix.resize_4x4()
            rmatrix.translation = pos[0], pos[1], pos[2]
            
            self.matrix = rmatrix
            
            self.parent = parent
            
            self.loader.childrenOf[parent+1].append(self.index)
            
        def setAtomic(self, atomic):
            self.atomic = atomic
            self.geometry = atomic.geometry
            

                
    class RpGeometry:
        def __init__(self, loader, index):
            self.loader = loader
            self.index = index  
            self.vertices = []
            self.triangles = []
            self.materials = []
            self.mesh = None
            self.atomic = None
            self.skindata = None
            self.hasEnvUV = False
            self.vertCol = None
            self.nightVertCol = None
            self.hasNormals = False
            
        def setAtomic(self, atomic):
            self.atomic = atomic
            
        def addMaterial(self, material):
            material.setIndex(len(self.materials))
            self.materials.append(material)
            
        def addVertex(self, vertex):
            self.vertices.append(vertex)
            
        def addTriangle(self, triangle):
            self.triangles.append(triangle)
        
    class RpMaterial:
        def __init__(self, geometry, flags=None, col=None, textured=None, ambient=None, specular=None, diffuse=None):
            self.index = None
            self.name = "g" + str(geometry.index) + "m"
            self.geometry = geometry
            self.flags = flags
            self.col = col
            self.ambient = ambient
            self.specular = specular
            self.diffuse = diffuse
            self.textured = textured
            self.texture = None
            self.blmat = None
            
            self.envtex = None
            self.readenvmap = False
            self.envIntensity = 1
            
            self.reflectColour = None
            self.reflectIntensity = None
            
            self.spectex = None
            
        def setIndex(self, index):
            self.index = index
            self.name = "g" + str(self.geometry.index) + "m" + str(index)
            
        def setTexture(self, texture):
            self.texture = texture
            
        def setEnvTexture(self, texture):
            self.envtex = texture
            
        def setSpecTexture(self, texture):
            self.spectex = texture
            
        def setReflection(self, colour, intensity):
            self.reflectColour = colour
            self.reflectIntensity = intensity
            
            
    class RwTexture:
        def __init__(self, loader, material, name, texType, intensity=1):
            self.material = material
            self.bltex = None
            self.bltexslot = None
            self.name = name
            self.loader = loader
            self.texType = texType
            self.intensity = intensity
                
    class RpAtomic:
        def __init__(self, loader, frame, geometry, flags):
            self.loader = loader
            self.frame = frame
            self.geometry = geometry
            self.flags = flags
            
            self.renderPlugin = None
            self.renderExtra = None
            
            self.matfxpipe = False
            
            frame.setAtomic(self)
            geometry.setAtomic(self)
            
        def setRenderRights(self, plugin, extra):
            self.renderPlugin = plugin
            self.renderExtra = extra
    
    def __init__(self, filename):
        self.filename = filename
        self.texpool = {}
        self.envtexpool = {}
        
        self.colhex = None
        
        self.childrenOf = None
        self.frames = []
        self.geoms = []
        
        self.f = open(filename, "rb")
        self.readSection(RwTypes.CLUMP)
        self.f.close()
            
    def writeDebug(self, text):
        g = open(self.filename + ".txt", "a")
        g.write(text + "\n")
        g.close()
        
    def readFormat(self, format):
        return struct.unpack(format, self.f.read(struct.calcsize(format)))
    
    def readSlice(self, format, slice):
        size = struct.calcsize(format)
        
        if(len(slice) < size):
            raise Exception("Failed to read slice, buffer is too small.")
        
        return struct.unpack(format, slice[:size]), slice[size:]
        
    def readSection(self, type, extra = None):
        header = self.readFormat("III")
        header = (header[0], header[1], RwTypes.decodeVersion(header[2]))
        
        if type >= 0 and header[0] != type:
            raise Exception("Expected type " + str(type) + ", found " + str(header[0]))
            
        curPos = self.f.tell()
        
        res = None
            
        if header[0] == RwTypes.STRUCT: res = self.readSectionStruct(header)
        elif header[0] == RwTypes.STRING: res = self.readSectionString(header)
        elif header[0] == RwTypes.EXTENSION: res = self.readSectionExtension(header, extra)
        elif header[0] == RwTypes.TEXTURE: res = self.readSectionTexture(header, extra)
        elif header[0] == RwTypes.MATERIAL: res = self.readSectionMaterial(header, extra)
        elif header[0] == RwTypes.MATERIALLIST: res = self.readSectionMaterialList(header, extra)
        elif header[0] == RwTypes.FRAMELIST: res = self.readSectionFrameList(header)
        elif header[0] == RwTypes.GEOMETRY: res = self.readSectionGeometry(header, extra)
        elif header[0] == RwTypes.CLUMP: res = self.readSectionClump(header)
        elif header[0] == RwTypes.ATOMIC: res = self.readSectionAtomic(header)
        elif header[0] == RwTypes.GEOMETRYLIST: res = self.readSectionGeometryList(header)
        elif header[0] == RwTypes.MORPHPLG: res = self.readSectionMorphPLG(header, extra)
        elif header[0] == RwTypes.BINMESHPLG: res = self.readSectionBinMeshPLG(header, extra)
        elif header[0] == RwTypes.FRAMENAME: res = self.readSectionFrameName(header, extra)
        elif header[0] == RwTypes.COLLISION: res = self.readSectionCollision(header, extra)
        elif header[0] == RwTypes.MATEFFECTS: res = self.readSectionMatEffects(header, extra)
        elif header[0] == RwTypes.MATSPECULAR: res = self.readSectionMatSpecular(header, extra)
        elif header[0] == RwTypes.MATREFLECTION: res = self.readSectionMatReflection(header, extra)
        elif header[0] == RwTypes.MESHEXTENSION: res = self.readSectionMeshExtension(header, extra)
        elif header[0] == RwTypes.RENDERRIGHTS: res = self.readSectionRenderRights(header, extra)
        elif header[0] == RwTypes.HANIMPLG: res = self.readSectionHAnimPLG(header, extra)
        elif header[0] == RwTypes.SKINPLG: res = self.readSectionSkinPLG(header, extra)
        elif header[0] == RwTypes.NIGHTCOLS: res = self.readSectionNightCols(header, extra)
        elif type >= 0: raise Exception("Missing read function for section type " + str(type))
        else: print("Ignoring extension data of type " + hex(header[0]))
        
        self.f.seek(curPos + header[1])
        
        return res
        
    def readSectionStruct(self, header):
        return header, self.f.read(header[1])
        
    def readSectionString(self, header):
        byteList = b""
        
        for i in range(header[1]):
            newByte = self.f.read(1)
            if newByte[0] == 0:
                break
            
            byteList += newByte
            
        return header, byteList.decode("ascii")
    
    def readSectionExtension(self, header, extra):
        endPos = self.f.tell() + header[1]
        
        while self.f.tell() < endPos:
            self.readSection(RwTypes.ANY, extra)
            
        return header, None
    
    def readSectionTexture(self, header, material):
        metaHeader, slice = self.readSection(RwTypes.STRUCT)
        (flags, x), slice = self.readSlice("HH", slice)
        
        x, texName = self.readSection(RwTypes.STRING)
        x, alphaName = self.readSection(RwTypes.STRING)
        
        if material.readenvmap:
            texture = self.RwTexture(self, material, texName, 1, material.envIntensity)
            material.setEnvTexture(texture)
        else:
            texture = self.RwTexture(self, material, texName, 0, 1)
            material.setTexture(texture)
        
        self.readSection(RwTypes.EXTENSION)
        
        return header, None
        
    def readSectionMaterial(self, header, geometry):
        metaHeader, slice = self.readSection(RwTypes.STRUCT)
        (flags,), slice = self.readSlice("I", slice)
        col, slice = self.readSlice("BBBB", slice)
        (x, textured, ambient, specular, diffuse), slice = self.readSlice("iifff", slice)
        
        material = self.RpMaterial(geometry, flags, col, textured, ambient, specular, diffuse)
        geometry.addMaterial(material)
        
        if textured > 0:
            self.readSection(RwTypes.TEXTURE, material)
            
        self.readSection(RwTypes.EXTENSION, material)
        
        return header, None
        
    def readSectionMaterialList(self, header, geometry):
        metaHeader, slice = self.readSection(RwTypes.STRUCT)
        (matCount,), slice = self.readSlice("i", slice)
        
        for i in range(matCount):
            junk, slice = self.readSlice("i", slice)
            
        for i in range(matCount):
            self.readSection(RwTypes.MATERIAL, geometry)
            
        return header, None
    
    def readSectionFrameList(self, header):
        metaHeader, slice = self.readSection(RwTypes.STRUCT)
        (frameCount,), slice = self.readSlice("i", slice)
        
        self.childrenOf = []
        
        for i in range(frameCount+1):
            self.childrenOf.append([])
        
        for i in range(frameCount):
            rot, slice = self.readSlice("fffffffff", slice)
            pos, slice = self.readSlice("fff", slice)
            (parent, flags), slice = self.readSlice("ii", slice)
            
            self.frames.append(self.RwFrame(self, i, rot, pos, parent))
        
        for i in range(frameCount):
            self.readSection(RwTypes.EXTENSION, self.frames[i])
            
        return header, None
    
    def readSectionGeometry(self, header, index):
        metaHeader, slice = self.readSection(RwTypes.STRUCT)
        (flags, texCount, triCount, vertCount, morphCount), slice = self.readSlice("HHiii", slice)
        
        geometry = self.RpGeometry(self, index)
        self.geoms.append(geometry)
        
        geometry.flags = flags
        
        if metaHeader[2] < 0x34001:
            (surfAmbient, surfSpecular, surfDiffuse), slice = self.readSlice("fff", slice)
        
        for i in range(vertCount):
            geometry.addVertex(self.RwVertex(None, None))
            
        if flags & RpGeomFlag.PRELIT:
            geometry.vertCol = []
            
            for i in range(vertCount):
                (vcr, vcg, vcb, vca), slice = self.readSlice("BBBB", slice)
                
                geometry.vertCol.append((vcr / 255, vcg / 255, vcb / 255))
            
        for i in range(vertCount):
            uv, slice = self.readSlice("ff", slice)
            geometry.vertices[i].uv = (uv[0], 1-uv[1])
            
        if texCount > 1:
            geometry.hasEnvUV = True
            
            for i in range(vertCount):
                uv_env, slice = self.readSlice("ff", slice)
                geometry.vertices[i].uv_env = (uv_env[0], 1-uv_env[1])
            
        if texCount > 2:
            slice = slice[struct.calcsize("ff")*(texCount-2)*(vertCount):]
            
        for i in range(triCount):
            (c, b, mat, a), slice = self.readSlice("HHHH", slice)
            
            if a >= vertCount or b >= vertCount or c >= vertCount:
                raise Exception("Vertex indices out of range for triangle.")
            
            geometry.addTriangle(self.RwTriangle((a, b, c), mat))
            
        if morphCount is not 1:
            raise Exception("Multiple frames not supported")
        
        for i in range(morphCount):
            (bx, by, bz, br, hasVerts, hasNormals), slice = self.readSlice("ffffii", slice)
            
            if hasVerts > 0:
                for j in range(vertCount):
                    coords, slice = self.readSlice("fff", slice)
                    geometry.vertices[j].coords = coords
            
            if hasNormals > 0:
                geometry.hasNormals = True
                
                for j in range(vertCount):
                    normal, slice = self.readSlice("fff", slice)
                    
                    geometry.vertices[j].normal = normal
        
        self.readSection(RwTypes.MATERIALLIST, geometry)
        self.readSection(RwTypes.EXTENSION, geometry)
        
        return header, None
    
    def readSectionClump(self, header):
        metaHeader, slice = self.readSection(RwTypes.STRUCT)
        (atomicCount,), slice = self.readSlice("i", slice)
        
        if metaHeader[2] > 0x33000:
            (lightCount, cameraCount), slice = self.readSlice("ii", slice)
        
        self.readSection(RwTypes.FRAMELIST)
        self.readSection(RwTypes.GEOMETRYLIST)
        
        for i in range(atomicCount):
            self.readSection(RwTypes.ATOMIC)
            
        self.readSection(RwTypes.EXTENSION)
        
        return header, None
        
    def readSectionAtomic(self, header):
        metaHeader, slice = self.readSection(RwTypes.STRUCT)
        (frameIndex, geomIndex, flags, x, x, x, x), slice = self.readSlice("iiBBBBi", slice)
        
        atomic = self.RpAtomic(self, self.frames[frameIndex], self.geoms[geomIndex], flags)
        
        self.readSection(RwTypes.EXTENSION, atomic)
        
        return header, None
    
    def readSectionGeometryList(self, header):
        metaHeader, slice = self.readSection(RwTypes.STRUCT)
        (geomCount,), slice = self.readSlice("i", slice)
        
        for i in range(geomCount):
            self.readSection(RwTypes.GEOMETRY, i)
    
    def readSectionMorphPLG(self, header, geometry):
        return header, None
    
    def readSectionBinMeshPLG(self, header, geometry):
        slice = self.f.read(header[1])
        
        (type, splits, total), slice = self.readSlice("iii", slice)
        
        if type != 0 and type != 1:
            print("Morph PLG section in unknown type - ignoring.")
            return header, None
        
        lookup = {}
        
        for i in range(len(geometry.triangles)):
            v = geometry.triangles[i].verts
            v = list(v)
            v.sort()
            
            lookup[tuple(v)] = i
            
        #totals = 0
        
        for i in range(splits):
            (sub, mat), slice = self.readSlice("ii", slice)
            
            if type == 0:
                for j in range(sub//3):
                    vx, slice = self.readSlice("iii", slice)
                    vx = list(vx)
                    vx.sort()
                    vx = tuple(vx)
                    
                    if vx in lookup:
                        geometry.triangles[lookup[vx]].mat = mat
            else:
                elems = deque()
                
                for j in range(sub):
                    if len(elems) > 2:
                        elems.popleft()
                    
                    (item,), slice = self.readSlice("i", slice)
                    
                    if len(elems) > 1:
                        checklist = [elems[0], elems[1], item]
                        checklist.sort()
                        check = tuple(checklist)
                        
                        if check in lookup:
                            geometry.triangles[lookup[check]].mat = mat
                            
                    elems.append(item)
                    
        return header, None
    
    def readSectionFrameName(self, header, frame):
        frame.name = self.f.read(header[1]).decode("ascii")
        
        return header, None
    
    def readSectionCollision(self, header, geometry):
        if not self.childrenOf or len(self.childrenOf[0]) is 0:
            print("Collision extension - no frame to attach to.")
            return header, None
        
        binary = self.f.read(header[1])
            
        self.colhex = base64.b64encode(zlib.compress(binary)).decode("ascii")
        
        return header, None
    
    def readSectionMatEffects(self, header, parent):
        if parent.__class__ == self.RpMaterial:
            return self.readSectionMaterialMatEffects(header, parent)
        elif parent.__class__ == self.RpAtomic:
            return self.readSectionAtomicMatEffects(header, parent)
        
        return header, None
    
    def readSectionMaterialMatEffects(self, header, material):
        (flags,) = self.readFormat("I")
        
        for i in range(2):
            (effectType,) = self.readFormat("I")
            
            if effectType == 0:
                continue
            elif effectType != 2:
                print("Unknown material effect type.")
                return header, None
            
            (coefficient, frameBufferAlpha, textured) = self.readFormat("fii")
            
            if textured:
                material.readenvmap = True
                material.envIntensity = coefficient
                
                self.readSection(RwTypes.TEXTURE, material)
        
    def readSectionAtomicMatEffects(self, header, atomic):
        (check,) = self.readFormat("i")
        
        if check != 0:
            atomic.matfxpipe = True
        
        return header, None
    
    def readSectionMatSpecular(self, header, material):
        slice = self.f.read(header[1])
        
        (intensity,), slice = self.readSlice("f", slice)
        
        specName = ""
        
        for i in range(len(slice)):
            if int(slice[i]) == 0:
                break
            
            specName += slice[i:i+1].decode("ascii")
            
        texture = self.RwTexture(self, material, specName, 2, intensity)
        material.setSpecTexture(texture)
        
        return header, None
        
    def readSectionMatReflection(self, header, material):
        slice = self.f.read(header[1])
        
        colour, slice = self.readSlice("fff", slice)
        (x, intensity), slice = self.readSlice("ff", slice)
        
        material.setReflection(colour, intensity)
        
        return header, None
        
    def readSectionMeshExtension(self, header, geometry):
        slice = self.f.read(header[1])
        
        (hasData,), slice = self.readSlice("i", slice)
        
        if hasData:
            print("Mesh extension extension actually has data. Not sure what to do with it.")
            
        return header, None
    
    def readSectionRenderRights(self, header, atomic):
        if not hasattr(atomic, "__class__") or atomic.__class__ != self.RpAtomic:
            print("Render rights extension is not in the right section, should be in atomic.")
            return
            
        slice = self.f.read(header[1])
        (plugin, extra), slice = self.readSlice("ii", slice)
        
        atomic.setRenderRights(plugin, extra)
        
    def readSectionHAnimPLG(self, header, frame):
        if not hasattr(frame, "__class__") or frame.__class__ != self.RwFrame:
            print("HAnim extension is not in the right section, should be in frame.")
            return
        
        binary = self.f.read(header[1])
        
        frame.hanimdata = base64.b64encode(zlib.compress(binary)).decode("ascii")
        
        return header, None
    
    def readSectionSkinPLG(self, header, geometry):
        if not hasattr(geometry, "__class__") or geometry.__class__ != self.RpGeometry:
            print("Skin extension is not in the right section, should be in geometry.")
            return
        
        binary = self.f.read(header[1])
        
        geometry.skindata = base64.b64encode(zlib.compress(binary)).decode("ascii")
        
        return header, None
        
    def readSectionNightCols(self, header, geometry):
        if not hasattr(geometry, "__class__") or geometry.__class__ != self.RpGeometry:
            print("Night vertex colours extension is not in the right section, should be in geometry.")
            return
            
        slice = self.f.read(header[1])
        (x,), slice = self.readSlice("I", slice)
        
        geometry.nightVertCol = []
        
        for i in range(len(geometry.vertices)):
            (vcr, vcg, vcb, vca), slice = self.readSlice("BBBB", slice)
            
            geometry.nightVertCol.append((vcr / 255, vcg / 255, vcb / 255))
        
        return header, None