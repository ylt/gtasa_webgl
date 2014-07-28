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
                "Interior":int(ldata[2]),
                "PosX":float(ldata[3]),
                "PosY":float(ldata[4]),
                "PosZ":float(ldata[5]),
                "RotX":float(ldata[6]),
                "RotY":float(ldata[7]),
                "RotZ":float(ldata[8]),
                "RotW":float(ldata[9]),
                "LOD":int(ldata[10]),
            })
        else:
            data[current].append(ldata)

    for k in list(data.keys()):
        if len(data[k]) == 0:
            del data[k]
    return data
    