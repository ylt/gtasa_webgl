class ipl():
    def __init__(self, gtapath, filename):
        self.inst = []
        self.cull = []
        self.path = []
        self.grge = []
        self.enex = []
        self.pick = []
        self.jump = []
        self.tcyc = []
        self.auzo = []
        self.mult = []
        self.cars = []
        self.occl = []
        self.zone = []
        
        self.gtapath = gtapath        
        
        self.read_text(filename)
    def read_text(self, filename):
        f = self.gtapath.getFileHandle(filename, "r")
        
        current = None     
        
        for line in f:
            line = line.strip()
        
            if line[0] == "#":
                continue
            if current == None:
                current = line
            elif line == "end":
                current = None
                continue
            
            ldata = [item.strip() for item in line.split(",")]        
                 
            
            if current == "inst":
                ID, ModelName, Interior, PosX, PosY, PosZ, RotX, RotY, RotZ, RotW, LOD = ldata
                
                entry = {
                    "ID":int(ldata[0]),
                    "ModelName":ldata[1],
                    "Interior":int(ldata[2]),
                    "PosX":float(ldata[3]),
                    "PosY":float(ldata[4]),
                    "PosZ":float(ldata[5]),
                    "RotX":float(ldata[6]),
                    "RotY":float(ldata[7]),
                    "RotZ":float(ldata[8]),
                    "RotW":float(ldata[9]),
                    "LOD":int(ldata[10]),
                }                
                self.inst.append(entry)
            else:
                getattr(self, current, ldata)
        
    def markLOD(self):
        for inst in self.inst:
            if inst["LOD"] == -1:
                continue
            
            self.inst[inst["LOD"]]["isLOD"] = True
