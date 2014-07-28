def convert(filename):
    f = open(filename)
    
    data = {}
    current = None
    for line in f:
        line = line.strip()
    
        if line[0] == "#":
            continue
        if current == None:
            current = line
            if current not in data:
                data[current] = []
                continue
        elif line == "end":
            current = None
            continue
        
        ldata = [item.strip() for item in line.split(",")]        
        
        if current == "inst":
            ID, ModelName, Interior, PosX, PosY, PosZ, RotX, RotY, RotZ, RotW, LOD = ldata
            
            data[current].append({
                "ID":int(ldata[0]),
                "ModelName":ldata[1],
                "PosX":float(ldata[2]),
                "PosY":float(ldata[3]),
                "PosZ":float(ldata[4]),
                "RotX":float(ldata[5]),
                "RotY":float(ldata[6]),
                "RotZ":float(ldata[7]),
                "RotW":float(ldata[8]),
                "LOD":int(ldata[9]),
            })
        else:
            data[current].append(ldata)

    for k in list(data.keys()):
        if len(data[k]) == 0:
            del data[k]
    return data
