import struct
import os

def _read_struct(f,format):
    size = struct.calcsize(format)
    return struct.unpack(format, f.read(size))    

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
        
        name = os.path.splitext(os.path.basename(filename))[0]
        i = 0
        while gtapath.hasFile("%s_stream%d.ipl" % (name, i)):
            self.read_binary("%s_stream%d.ipl" % (name, i))
            i += 1
            
        self.markLOD()
        
    def read_text(self, filename):
        f = self.gtapath.getFileHandle(filename, "r")
        current = None     
        
        for line in f:
            line = line.strip()
        
            if line[0] == "#":
                continue
            if current == None:
                current = line
                continue
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
                
    def read_binary(self, filename):
        print(filename)
        f = self.gtapath.getFileHandle(filename, "rb")
        print(f)
        
        header = _read_struct(f, "<IIIIIIIIIIIIIIIIII")
        
        item_count = header[1]
        car_count = header[5]
        item_offset = header[7]
        car_offset = header[15]
        
        f.seek(item_offset)
        for i in range(0, item_count):
            d = _read_struct(f, "<fffffffIII")
            entry = {
                "PosX":d[0],
                "PosY":d[1],
                "PosZ":d[2],
                "RotX":d[3],
                "RotY":d[4],
                "RotZ":d[5],
                "RotW":d[6],
                "ID":d[7],
                "Interior":d[8],
                "LOD":d[9]
            }
            self.inst.append(entry)
            
        f.seek(car_offset)
        for i in range(0, car_count):
            d = _read_struct(f, "<ffffIIIIIIII")
            entry = {
                "PosX":d[0],
                "PosY":d[1],
                "PosZ":d[2],
                "Angle":d[3],
                "ID":d[4],
                "Color1":d[5],
                "Color2":d[6],
                "ForceSpawn":d[7] != 0,
                "AlarmProbability":d[8],
                "LockedProbability":d[9],   
                "Color3":d[10],
                "Color4":d[11]
            }
            self.cars.append(entry)         
         
    def markLOD(self):
        for inst in self.inst:
            if inst["LOD"] == -1:
                continue
            
            if inst["LOD"] >= len(self.inst):
                continue
            
            self.inst[inst["LOD"]]["isLOD"] = True
