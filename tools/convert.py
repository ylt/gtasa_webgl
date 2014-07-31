import readers.ipl
import os
import json

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
    
    
gtapath = "/home/joe/win8vm-files/Grand Theft Auto San Andreas/"
gtaimgpath = "/home/joe/win8vm-files/gta3/"
target = "/home/joe/sineapps/gta/git/web/data/"
dat = gta3_dat(gtapath+"data/gta.dat")

#load in IDE's
data = {}
for ide in dat["IDE"]:
    filename = path_insensitive(gtapath+ide)
    d = readers.ipl.convert(filename)
    
    merge_dicts(data, d)

i = 0
for ide in dat["IPL"]:
    filename = path_insensitive(gtapath+ide)
    d = readers.ipl.convert(filename)
    
    #print(d)    
    
    merge_dicts(data, d)
    #=if i > 2:
    #    break
    i+=1


objects = data["objs"]
in_models = {}
in_id = {}
for obj in objects:
    in_models[obj[1].lower()] = obj
    in_id[int(obj[0])] = obj
print(json.dumps(objects, sort_keys=True))

for inst in data["inst"]:
    #print(inst)
    if inst["ID"] in in_id:
        obj = in_id[inst["ID"]]
    else:
        print(json.dumps(inst, sort_keys=True))
        
