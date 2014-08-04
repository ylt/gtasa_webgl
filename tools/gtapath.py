import readers
import os
 
class gtapath():
    def __init__(self, gtapath):
        self.gtapath = gtapath
        #Fill in some default paths
        self.paths = [
            gtadir(gtapath, ''),
        ]
        
        self.ipls = ipls(self)
        self.ides = ides(self)
        
        self.loadImg("models/gta3.img")
        self.loadDat("data/gta.dat")
        self.loadDat("data/default.dat")
        
    def loadImg(self, path):
        fullPath = self.getFilePath(path)
        if not fullPath:
            raise Exception("Missing IMG")
        img = readers.img(fullPath)
        self.paths.append(img)
        
    def loadDat(self, path):
        f = self.getFileHandle(path, "r")
        for line in f:
            line = line.strip()
            if line == "" or line[0] == "#":
                continue
            
            
            #TODO: TIDY UP
            val = line.split(" ")
            key = val[0]
            del val[0]
            if len(val) == 1:
                val = val[0]
            
            if key == "IMG":
                self.loadImg(val)
            elif key == "IPL":
                self.ipls.load(val)
            elif key == "IDE":
                self.ides.load(val)
                
    def hasFile(self, path):
        for item in self.paths:
            if item.hasFile(path):
                return True
        return False

    def getFileData(self, path, mode="r"):
        for item in self.paths:
            if item.hasFile(path):
                return item.readFile(path, mode)

    def getFileHandle(self, path, mode="r"):
        for item in self.paths:
            if item.hasFile(path):
                f = item.getFileHandle(path, mode)
                return f
        
    #used for IMG files, they're too big to read into memory
    # and you never get an IMG file within an IMG file
    def getFilePath(self, path):
        for item in self.paths:
            if type(item) is gtadir and item.hasFile(path):
                return item.getFilePath(path)
        
        
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

    def hasFile(self, path):
        return self.getFilePath(path) != None
        
    def getFilePath(self, path):
        #R* did not even consider linux compatibility.. ;)
        # file cases are wrong also, but our dict solves that
        path = path.replace("\\",os.sep).lower()
        
        if path in self.path_lookup:
            return self.path_lookup[path]
        file = os.path.basename(path)
        if file in self.file_lookup:
            return self.file_lookup[file]
            
    def readFile(self, path, mode):
        fullpath = self.getFilePath(path)
        with open(fullpath, mode) as f:
            return f.read()
    
    def getFileHandle(self, path, mode):
        fullpath = self.getFilePath(path)
        f = open(fullpath, mode)
        return f
        
class ipls():
    def __init__(self, gtapath):
        self.gtapath = gtapath
        
        self.ipls = []
        
    def load(self, filename):
        self.ipls.append(readers.ipl(self.gtapath, filename))
                
class ides():
    def __init__(self, gtapath):
        self.gtapath = gtapath
        self.ides = []
    def load(self, filename):
        self.ides.append(readers.ide(self.gtapath, filename))