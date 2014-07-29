import ctypes
import struct
import s3tc
from PIL import Image

from enum import Enum

class section():
    def read_struct(self,format):
        size = struct.calcsize(format)
        return struct.unpack(format, self.f.read(size))
    
    def readSection(self):
        section, section_size, rw_version = self.read_struct("<III")
        end = self.f.tell() + section_size
        #print("Section %s" % hex(section))
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
    Compression = Enum('DXT1','DXT2')
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
        self.raster_format, \
        self.fourcc, \
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
        self.texture_name = ctypes.c_char_p(self.texture_name).value.decode('ascii')
        self.alpha_name = ctypes.c_char_p(self.alpha_name).value.decode('ascii')
        
    def hasAlpha(self):
        format = self.fourcc
        compression = self.flags
        if format == 0 or format == 0x16 or compression == 8:
            return False
        elif format == 1 or format == 0x15 or compression == 8:
            return True
        return None
    
    def getCompression(self):    
        fourcc = self.fourcc
        compression = self.flags
        
        if fourcc == 0x31545844 or fourcc == 1:
            return "DXT1"
        elif fourcc == 0x33545844 or fourcc == 3:
            return "DXT3"
        
        if compression == 0 or compression == 1: #no compression
            return False
        
        return False
        
    def getImage(self):
        compression = self.getCompression()
        if compression == "DXT1":
            t = s3tc.decode_dxt1_rgba(self.texture, self.width, self.height)
            return Image.frombuffer("RGBA", (self.width, self.height), t, 'raw', 'RGBA', 0, 1)
        elif compression == "DXT3":
            t = s3tc.decode_dxt3(self.texture, self.width, self.height)
            return Image.frombuffer("RGBA", (self.width, self.height), t, 'raw', 'RGBA', 0, 1)
        
        raster_format = self.raster_format & 0x0100
        if raster_format == 0x0500: #RGBA :D
            return Image.frombuffer("RGBA", (self.width, self.height), self.texture, 'raw', 'RGBA', 0, 1)
        elif raster_format == 0x0600: #RGB :D
            return Image.frombuffer("RGB", (self.width, self.height), self.texture, 'raw', 'RGB', 0, 1)
        elif raster_format == 0x0400:
            return Image.frombuffer("L", (self.width, self.height), self.texture, 'raw', 'L', 0, 1)
            
        out = (ctypes.c_ubyte * (self.width * self.height * 4))()
        out_pos = 0
        for pos in range(0, self.width*self.height, self.depth/4):
            r,g,b,a = 0,0,0,0
            value, = struct.unpack_from("H", self.texture, pos)
            if raster_format == 0x0000: # Default - Wut do here?
                pass
            elif raster_format == 0x0100: # FORMAT_1555
                #(1 bit alpha, RGB 5 bits each; also used for DXT1 with alpha)
                r = (value & 0xf8)        / 0xf8 * 255
                g = ((value >> 5) & 0xf8) / 0xf8 * 255
                b = ((value >> 10) & 0xf8)/ 0xf8 * 255
                a = ((value >> 15) & 0x01)       * 255
                
            elif raster_format == 0x0200: # FORMAT_565
                #(5 bits red, 6 bits green, 5 bits blue; also used for DXT1 without alpha)
                r = (value & 0xf8)        / 0xf8 * 255
                g = ((value >> 5) & 0xfc) / 0xfc * 255
                b = ((value >> 11) & 0xf8)/ 0xf8 * 255
                
            elif raster_format == 0x0300: # FORMAT_4444
                #(RGBA 4 bits each; also used for DXT3)
                r = (value & 0xf0)        / 0xf0 * 255
                g = ((value >> 4) & 0xf0) / 0xf0 * 255
                b = ((value >> 8) & 0xf0) / 0xf0 * 255
                a = ((value >> 12) & 0xf0)/ 0xf0 * 255
                
            elif raster_format == 0x0A00: # FORMAT_555
                #(5 bits red, 6 bits green, 5 bits blue; also used for DXT1 without alpha)
                r = (value & 0xf8)        / 0xf8 * 255
                g = ((value >> 5) & 0xf8) / 0xfc * 255
                b = ((value >> 10) & 0xf8)/ 0xf8 * 255
            
            out[out_pos] = b
            out[out_pos+1] = g
            out[out_pos+3] = r
            out[out_pos+4] = a
            out_pos += 4
        return Image.frombuffer("RGBA", (self.width, self.height), out, 'raw', 'RGBA', 0, 1)
f = file("../particle.txd")