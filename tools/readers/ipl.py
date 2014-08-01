def convert(filename):
    f = open(filename)
    
    data = {}
    current = None

    objlods = []       
    
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
            
            if entry["LOD"] != -1:
                objlods.append(entry["LOD"])
                
            data[current].append(entry)
        elif current == "objs":
            entry = {
                "ID":int(ldata[0]),
                "ModelName": ldata[1],
                "TextureName": ldata[2],
            }
            dlen= len(ldata)
            if dlen == 4: #Type 0
                entry["ObjectCount"] = int(ldata[3])
            elif dlen == 6: #Type 1
                entry["ObjectCount"] = int(ldata[3])
                entry["DrawDistance"] = float(ldata[4])
                entry["Flags"] = int(ldata[5])
            elif dlen == 7: #Type 2
                entry["ObjectCount"] = int(ldata[3])
                entry["DrawDistance"] = float(ldata[4])
                entry["DrawDistance2"] = float(ldata[5])
                entry["Flags"] = ldata[6]
            elif dlen == 8: #Type 3
                entry["ObjectCount"] = int(ldata[3])
                entry["DrawDistance"] = float(ldata[4])
                entry["DrawDistance2"] = float(ldata[5])
                entry["DrawDistance3"] = float(ldata[6])
                entry["Flags"] = ldata[7]
            elif dlen == 5:
                entry["DrawDistance"] = float(ldata[3])
                entry["Flags"] = int(ldata[4])
                
            data[current].append(entry)
        elif current == "tobj":
            entry = {
                "ID":int(ldata[0]),
                "ModelName": ldata[1],
                "TextureName": ldata[2],
                "DrawDistance": float(ldata[4]),
                "Flags":int(ldata[-3]),
                "TImeOn":int(ldata[-2]),
                "TImeOff":int(ldata[-1])
            }
            if len(entry) > 7:
                entry["ObjectCount"] = int(ldata[3])
            
            
            data[current].append(entry)
        elif current == "anim":
            data[current].append({
                "ID":int(ldata[0]),
                "ModelName": ldata[1],
                "TextureName": ldata[2],
                "AnimationName": ldata[3],
                "DrawDistance": float(ldata[4]),
                "Flags":int(ldata[5]),
            })
            
            data[current].append(entry)
        else:
            data[current].append(ldata)

    for k in list(data.keys()):
        if len(data[k]) == 0:
            del data[k]
            
    #print (objlods)
    for inst in objlods:
        data["inst"][inst]["isLOD"] = True
        
    return data
