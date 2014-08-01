import readers.ipl
import model
import readers.txd

import os
import json
import math
import pprint

def gta3_dat(filename):
    #our loader does not care about order
    # as dependencies are solved at runtime instead
    out = {}
    f = open(filename)
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
    return out

# Thanks Chris Morgan!
#  http://stackoverflow.com/a/8462613
# now,to just determine the license..
def path_insensitive(path):
    if path == '' or os.path.exists(path):
        return path

    base = os.path.basename(path)  # may be a directory or a file
    dirname = os.path.dirname(path)

    suffix = ''
    if not base:  # dir ends with a slash?
        if len(dirname) < len(path):
            suffix = path[:len(path) - len(dirname)]

        base = os.path.basename(dirname)
        dirname = os.path.dirname(dirname)

    if not os.path.exists(dirname):
        dirname = path_insensitive(dirname)
        if not dirname:
            return

    # at this point, the directory exists but not the file

    try:  # we are expecting dirname to be a directory, but it could be a file
        files = os.listdir(dirname)
    except OSError:
        return

    baselow = base.lower()
    try:
        basefinal = next(fl for fl in files if fl.lower() == baselow)
    except StopIteration:
        return

    if basefinal:
        return os.path.join(dirname, basefinal) + suffix
    else:
        return
    

#extremely limited functon, is used for combining output of ipl reader
def merge_dicts(dicta, dictb):
    #dicta = dict(dicta) #think performance is more important
    for key,value in dictb.items():
        if key in dicta:
            dicta[key].extend(value)
        else:
            dicta[key] = list(value)
    return dicta
    
def distance(pos1, pos2):
    return math.sqrt(math.pow(pos1[0]-pos2[0], 2) + math.pow(pos1[1]-pos2[1], 2))

gtapath = "/home/joe/win8vm-files/Grand Theft Auto San Andreas/"
gtaimgpath = "/home/joe/win8vm-files/gta3/"
target = "/home/joe/sineapps/gta/git/web/data/"
dat = gta3_dat(gtapath+"data/gta.dat")
overwrite = True #don't redo already done models

filter_flags = ["NONE", "NEAREST", "LINEAR", "MIP_NEAREST", "MIP_LINEAR", "LINEAR_MIP_NEAREST", "LINEAR_MIP_LINEAR"]
texture_wrap = ["NONE", "WRAP", "MIRROR", "CLAMP"]
    
def do_txds(txds, txdpath, targetpath):
    print("*** Processing %d TXD's ***" % len(txds))
    for txdfile in txds:
        writepath = targetpath + txdfile + "/"
        if os.path.exists(writepath):
            if not overwrite:
                continue
        else:
            os.makedirs(writepath)
        txd = readers.txd.file(txdpath+txdfile.lower()+".txd")
        
        flags = {}        
        
        for tex in txd.children:
            #tex.texture_name
            tex.getImage().save(writepath+tex.texture_name.lower()+".png")
            flags[tex.texture_name] = {
                "wrap_v":tex.texture_wrap_v,
                "wrap_u":tex.texture_wrap_u,
                "filter_flags":tex.filter_flags,
                "raster_format":tex.raster_format,
                "bit_depth":tex.depth,
                "compression":tex.getCompression()
            }
        
        f = open(writepath+"metadata.json", "w")
        json.dump(flags, f)
        f.close()
        
def do_dffs(dffs, in_models, dffpath, targetpath):
    print("*** Processing %d DFF's ***" % len(dffs))
    for dfffile in dffs:
        writepath = targetpath + dfffile + ".js"
        if not overwrite and os.path.exists(writepath):
            continue
        
        txdpath = ""
        if dfffile.lower() in in_models:
            txdpath = "data/textures/"+in_models[dfffile.lower()][2]+"/"
        
        dff = model.convert(dffpath+dfffile.lower()+".dff", txdpath)
        
        f = open(writepath, "w")
        json.dump(dff.data, f)
        f.close()
        
#load in IDE's
data = {}
for ide in dat["IDE"]:
    filename = path_insensitive(gtapath+ide)
    d = readers.ipl.convert(filename)
    
    merge_dicts(data, d)

#and the IPL's
for ipl in dat["IPL"]:
    if 'paths' in ipl:
        continue
    filename = path_insensitive(gtapath+ipl)
    d = readers.ipl.convert(filename)
    
    merge_dicts(data, d)


objects = data["objs"]
in_models = {}
in_id = {}
for obj in objects:
    in_models[obj[1].lower()] = obj
    in_id[int(obj[0])] = obj
#print(json.dumps(objects, sort_keys=True))

textures = []
models = []
models_ipl = []
for inst in data["inst"]:
    #filter to specific area for now
    dis = distance((2048,2150), (inst["PosX"], inst["PosY"]))
    if dis > 500:
        continue
    
    if inst["ID"] in in_id:
        obj = in_id[inst["ID"]]
        
        if obj[2] not in textures:
            textures.append(obj[2])
            
        inst["ide"] = obj
    else:
        pass
        #print("Missing: %s", inst)
        
    if inst not in models:   
        models.append(inst["ModelName"])
        models_ipl.append(inst)
#print(textures)
#print(models)

do_txds(textures, gtaimgpath, target+"textures/")
do_dffs(models, in_models, gtaimgpath, target+"models/")


f = open(target+"positions.json", "w")
json.dump(models_ipl, f)
f.close()