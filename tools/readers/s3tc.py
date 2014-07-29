 # ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions 
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
# $Id:$

'''Software decoder for S3TC compressed texture (i.e., DDS).

http://oss.sgi.com/projects/ogl-sample/registry/EXT/texture_compression_s3tc.txt
'''

import ctypes

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]

def decode_dxt1_rgba(data, width, height):
    # Decode to GL_RGBA
    out = (ctypes.c_ubyte * (width * height * 4))()
    pitch = width << 2

    # Read 8 bytes at a time
    image_offset = 0
    for c0_lo, c0_hi, c1_lo, c1_hi, b0, b1, b2, b3 in chunks(data, 8):
        color0 = c0_lo | c0_hi << 8
        color1 = c1_lo | c1_hi << 8
        bits = b0 | b1 << 8 | b2 << 16 | b3 << 24

        r0 = color0 & 0x1f
        g0 = (color0 & 0x7e0) >> 5
        b0 = (color0 & 0xf800) >> 11
        r1 = color1 & 0x1f
        g1 = (color1 & 0x7e0) >> 5
        b1 = (color1 & 0xf800) >> 11

        # i is the dest ptr for this block
        i = image_offset
        for y in range(4):
            for x in range(4):
                code = bits & 0x3
                a = 255

                if code == 0:
                    r, g, b = r0, g0, b0
                elif code == 1:
                    r, g, b = r1, g1, b1
                elif code == 3 and color0 <= color1:
                    r = g = b = a = 0
                else:
                    if code == 2 and color0 > color1:
                        r = int((2 * r0 + r1) / 3)
                        g = int((2 * g0 + g1) / 3)
                        b = int((2 * b0 + b1) / 3)
                    elif code == 3 and color0 > color1:
                        r = int((r0 + 2 * r1) / 3)
                        g = int((g0 + 2 * g1) / 3)
                        b = int((b0 + 2 * b1) / 3)
                    else:
                        assert code == 2 and color0 <= color1
                        r = int((r0 + r1) / 2)
                        g = int((g0 + g1) / 2)
                        b = int((b0 + b1) / 2)

                out[i] = b << 3
                out[i+1] = g << 2
                out[i+2] = r << 3
                out[i+3] = a << 4

                bits >>= 2
                i += 4
            i += pitch - 16

        # Move dest ptr to next 4x4 block
        advance_row = (image_offset + 16) % pitch == 0
        image_offset += pitch * 3 * advance_row + 16
    return out


def decode_dxt3(data, width, height):
    # Decode to GL_RGBA
    out = (ctypes.c_ubyte * (width * height * 4))()
    pitch = width << 2

    # Read 16 bytes at a time
    image_offset = 0
    for (a0, a1, a2, a3, a4, a5, a6, a7,
         c0_lo, c0_hi, c1_lo, c1_hi, 
         b0, b1, b2, b3) in chunks(data, 16):
        color0 = c0_lo | c0_hi << 8
        color1 = c1_lo | c1_hi << 8
        bits = b0 | b1 << 8 | b2 << 16 | b3 << 24
        alpha = a0 | a1 << 8 | a2 << 16 | a3 << 24 | \
            a4 << 32 | a5 << 40 | a6 << 48 | a7 << 56

        r0 = color0 & 0x1f
        g0 = (color0 & 0x7e0) >> 5
        b0 = (color0 & 0xf800) >> 11
        r1 = color1 & 0x1f
        g1 = (color1 & 0x7e0) >> 5
        b1 = (color1 & 0xf800) >> 11

        # i is the dest ptr for this block
        i = image_offset
        for y in range(4):
            for x in range(4):
                code = bits & 0x3
                a = alpha & 0xf

                if code == 0:
                    r, g, b = r0, g0, b0
                elif code == 1:
                    r, g, b = r1, g1, b1
                elif code == 3 and color0 <= color1:
                    r = g = b = 0
                else:
                    if code == 2 and color0 > color1:
                        r = int((2 * r0 + r1) / 3)
                        g = int((2 * g0 + g1) / 3)
                        b = int((2 * b0 + b1) / 3)
                    elif code == 3 and color0 > color1:
                        r = int((r0 + 2 * r1) / 3)
                        g = int((g0 + 2 * g1) / 3)
                        b = int((b0 + 2 * b1) / 3)
                    else:
                        assert code == 2 and color0 <= color1
                        r = int((r0 + r1) / 2)
                        g = int((g0 + g1) / 2)
                        b = int((b0 + b1) / 2)

                out[i] = b << 3
                out[i+1] = g << 2
                out[i+2] = r << 3
                out[i+3] = a << 4

                bits >>= 2
                alpha >>= 4
                i += 4
            i += pitch - 16

        # Move dest ptr to next 4x4 block
        advance_row = (image_offset + 16) % pitch == 0
        image_offset += pitch * 3 * advance_row + 16
    return out
