import struct

def read_struct(f,format):
    size = struct.calcsize(format)
    return struct.unpack(format, f.read(size))    

def read(self, filename):
    f = open(filename, "r")
    
    header = read_struct(f, "<IIIIIIIIIIIIIIIIII")
    
    item_count = header[1]
    car_count = header[5]
    item_offset = header[7]
    car_offset = header[15]
    
    data = {"inst":[], "cars":[]}
    
    f.seek(item_offset)
    for i in range(0, item_count):
        d = read_struct(f, "<fffffffIII")
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
        data["inst"].append(entry)
        
    f.seek(car_offset)
    for i in range(0, car_count):
        d = read_struct(f, "<ffffIIIIIIII")
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
        data["cars"].append(entry)
    return data