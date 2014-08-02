import readers.img 
import os
 
class gtapath():
    def __init__(self, gtapath):
        self.gtapath = gtapath
        #Fill in some default paths
        self.paths = [
            gtadir(gtapath, ''),
        ]
        
        self.loadImg("models/gta3.img")
    
    def getFileData(self, path, mode="r"):
        for item in self.paths:
            if item.hasFile(path):
                return item.readFile(path, mode)
    
    #used for IMG files, they're too big to read into memory
    def getFilePath(self, path):
        for item in self.paths:
            if object is gtadir and item.hasFile(path):
                return item.getFilePath(path)
            
    def loadImg(self, path):
        fullPath = self.getFilePath(path)
        if not fullPath:
            raise "Missing IMG"
        img = readers.img.img(fullPath)
        self.paths.append(img)
        
class gtadir():
    def __init__(self, base, path):
        self.path_lookup = {}
        self.file_lookup = {}
        
        for root, subFolders, files in os.walk(base+path):
            for file in files:
                apath = root + "/" + file
                rpath = os.path.relpath(apath, base)
                
                self.path_lookup[rpath.lower()] = apath
                self.file_lookup[file.lower()] = apath
        print(self.path_lookup)
    def getFilePath(self, path):
        if path in self.path_lookup:
            return self.path_lookup[path]        
    def getAnyFilePath(self, file):
        if file in self.file_lookup:
            return self.file_lookup[file]
            
    def readFile(self, path, mode):
        if path in self.path_lookup:
            with open(self.path_lookup[path], mode) as f:
                return f.read()
    def readAnyFile(self, path, mode):
        if path in self.file_lookup:
            with open(self.file_lookup[path], mode) as f:
                return f.read()
            
"""
class inst():
    def __init__(self, filename):
        #our loader does not care about order
        # as dependencies are solved at runtime instead
        out = {}
        f = open(filename, "r")
        for line in f:
            line = line.strip()
            if line == "" or line[0] == "#":
                continue
            
            key,val = line.split(" ")
            if key not in out:
                out[key] = []
                
            #R* did not even consider linux compatibility..
            # not all files are lowercase, but this will get the most hits
            val = val.replace("\\","/").lower()
            
            out[key].append(val)
        return out"""