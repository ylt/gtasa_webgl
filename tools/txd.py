import struct
from enum import Enum

class section():
    def read_struct(self,format):
        size = struct.calcsize(format)
        return struct.unpack(format, self.f.read(size))
    
    def readSection(self):
        section, section_size, rw_version = self.read_struct("<III")
        end = self.f.tell() + section_size
        print("Section %s" % hex(section))
        if section == 0x01: #struct
            return self.readStruct()
        elif section == 0x15:
            return texture_native(self.f, end)
        
        self.f.seek(end)
        
        return False
    def readStruct(self):
        pass
    def readAll(self):
        while True:
            if self.f.tell() >= self.end:
                break
            
            child = self.readSection()

            if child:
                self.children.append(child)
            
            
class file(section):
    def __init__(self, file):
        self.f = open(file, "rb")
        
        self.section_id, self.end, self.rw_version = self.read_struct("<III")
        
        if self.section_id != 0x16:
            raise Exception("Not a TXD file.")
        
        self.children = []
        self.readAll()
        
    def readStruct(self):
        self.texture_count, self.unknown = self.read_struct("HH")

class texture_native(section):
    def __init__(self, f, end):
        self.f = f
        self.end = end
        
        self.children = []
        self.readAll()

    def readStruct(self):
        self.version, \
        self.filter_flags, \
        self.texture_wrap_v, \
        self.texture_wrap_u, \
        self.texture_name, \
        self.alpha_name, \
        self.alpha_flags, \
        self.direct3d_texture_format, \
        self.width,\
        self.height,\
        self.depth, \
        self.mipmap_count, \
        self.texcode_type, \
        self.flags, \
        self.data_size \
                = self.read_struct("<IHBB32s32sIIHHBBBBI")
            
        self.texture = self.f.read(self.data_size)
        
        #convert back to ascii string and strip off the null terminators
        self.texture_name = self.texture_name.decode('ascii').rstrip("\x00")
        self.alpha_name = self.alpha_name.decode('ascii').rstrip("\x00")
        
    def hasAlpha(self):
        format = self.direct3d_texture_format
        if format == 0 or format == 0x16 or format == 0x31545844: # 1TXD
            return False
        elif format == 1 or format == 0x15 or format == 0x33545844: #3TXD
            return True
        return None
    
f = file("../fronten1.txd")