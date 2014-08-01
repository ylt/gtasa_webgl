import struct
import ctypes
class img():
    def read_struct(self,format):
        size = struct.calcsize(format)
        return struct.unpack(format, self.f.read(size))
        
    def __init__(self, filename):
        self.f = open(filename, "rb")
        magic, self.file_count = self.read_struct("<II")
        #TODO: check if magic == 2REV (VER2 in little endian)
        if magic != 0x32524556:
            raise "Not an IMG file"
        
        
        self.files = []
        self.file_dict = {}
        for i in range(0, self.file_count):
            d = self.read_struct("<IHH24s")
            
            filename = self.texture_name = ctypes.c_char_p(d[3]).value.decode('ascii')
            entry= {
               "Offset":d[0],
               "Size_Second":d[1],
               "Size_First":d[2],
               "Filename":filename
            }
            
            self.files.append(entry)
            self.file_dict[filename.lower()] = entry
    def hasFile(self, filename):
        return filename.lower() in self.file_dict
        
    def readFile(self, filename):
        entry = self.file_dict[filename.lower()]
        self.f.seek(entry["Offset"]*2048)
        size = entry["Size_First"] if entry["Size_First"] != 0 else entry["Size_Second"]
        return self.f.read(size*2048)