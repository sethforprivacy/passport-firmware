#!/usr/bin/env python3
#
# (c) Copyright 2018 by Coinkite Inc. This file is part of Coldcard <coldcardwallet.com>
# and is covered by GPLv3 license found in COPYING.
#
import os, sys, pdb
from PIL import Image, ImageOps
import zlib

def read_text(fname):

    w = 0
    rows = [] 
    Z = b'\0'
    F = b'\xff'

    # do not trim whitespace; perhaps it is spacing data

    for ln in open(fname, 'rt').readlines():
        ln = ln.rstrip('\n')
        r = b''.join(F if i != ' ' else Z for i in ln)
        w = max(w, len(r))
        rows.append(r)

    raw = b''
    for r in rows:
        r += Z*(w - len(r))
        raw += r

    return Image.frombytes('L', (w, len(rows)), raw).convert('1')

def read_img(fn):
    img = Image.open(fn)
    w,h = img.size

    img = img.convert('L')
    # fix colour issues: assume minority colour is white (1)
    histo = img.histogram()
    assert len(histo) == 256, repr(histo)
    assert len(set(histo)) == 3, "Too many colors: "+repr(histo)

    # if histo[-1] > histo[0]:
    img = ImageOps.invert(img)

    return img.convert('1', dither=False)

def compress(n, wbits=-9):
    z = zlib.compressobj(wbits=wbits)
    rv = z.compress(n)
    rv += z.flush(zlib.Z_FINISH)
    return rv

def crunch(n):
    # try them all... not finding any difference tho.
    a = [(wb,compress(n, wb)) for wb in range(-9, -15, -1)]

    a.sort(key=lambda i: (-len(i[1]), -i[0]))

    #print(' / '.join("%d => %d" % (wb,len(d)) for wb,d in a))

    return a[0]
        

def gen_header(outfile, fnames):

    assert fnames, "need some files"

    fp = open('{}.h'.format(outfile_prefix), 'wt')

    fp.write("""\
// SPDX-FileCopyrightText: 2020 Foundation Devices, Inc. <hello@foundationdevices.com>
// SPDX-License-Identifier: GPL-3.0-or-later
//
//
// Autogenerated - Do not edit!
//

#include <stdint.h>

typedef struct _Image {
    int16_t width;
    int16_t height;
    int16_t byte_width;
    uint8_t* data;
} Image;

""")

    from io import StringIO
    for fn in fnames:
        varname = fn.split('.')[0].replace('-', '_')

        fp.write("extern Image {}_img;\n".format(varname))


def gen_source(outfile_prefix, fnames):

    assert fnames, "need some files"

    fp = open('{}.c'.format(outfile_prefix), 'wt')

    fp.write("""\
// SPDX-FileCopyrightText: 2020 Foundation Devices, Inc. <hello@foundationdevices.com>
// SPDX-License-Identifier: GPL-3.0-or-later
//
//
// Autogenerated - Do not edit!
//

#include "{}.h"

""".format(outfile_prefix))

    from io import StringIO
    for fn in fnames:
        if fn.endswith('.txt'):
            img = read_text(fn)
        else:
            img = read_img(fn)

        assert img.mode == '1'
        #img.show()

        varname = fn.split('.')[0].replace('-', '_')

        w,h = img.size
        raw = img.tobytes()
        str = StringIO()
        i=0
        print('w={}, h={} len(raw)={}'.format(w, h, len(raw)))
        str.write('{')
        str.write(os.linesep)
        w_bytes = (w + 7) // 8
        for y in range(h):
            str.write('    ')
            for x in range(w_bytes):
                b = raw[(y * w_bytes) + x]
                str.write('0x{:02x}{} '.format(b, ',' if x < w-1 else ''))
            str.write('\n')
        str.write('};')

        fp.write("uint8_t {}_data[] = {}\n".format(varname, str.getvalue()))
        fp.write("Image {}_img = {{ {}, {}, {}, {}_data }};\n\n".format(varname, w, h, (w+7)//8, varname))

        print("done: '%s' (%d x %d)" % (varname, w, h))

if 1:
    outfile_prefix = sys.argv[1]
    sources = sys.argv[2:].copy()
    sources.sort()
    gen_header(outfile_prefix, sources)
    gen_source(outfile_prefix, sources)