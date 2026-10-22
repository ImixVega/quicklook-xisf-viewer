"""Tworzy syntetyczne XISF 1.0 do testu QuickLook XISF Viewer v0.1.
Wymagania: Python 3; zstd CLI do odtwarzania dodatkowych fixture ZSTD.
"""
from pathlib import Path
import math
import struct
import zlib
import subprocess

HERE = Path(__file__).resolve().parent


def shuffle(payload, item_size):
    n = len(payload) // item_size
    return b''.join(payload[i::item_size][:n] for i in range(item_size))


def lz4_literals_only(src):
    """Poprawny blok LZ4: same literały, bez dopasowań."""
    n = len(src)
    out = bytearray([min(n, 15) << 4])
    if n >= 15:
        extra = n - 15
        while extra >= 255:
            out.append(255)
            extra -= 255
        out.append(extra)
    out.extend(src)
    return bytes(out)


def pixel_luminance(x, y, w, h):
    nebula = 0.02 * math.exp(-((x - w * .53)**2 / (w * .22)**2 +
                                (y - h * .49)**2 / (h * .16)**2))
    stars = [(w*.13, h*.12), (w*.72, h*.64), (w*.35, h*.82),
             (w*.79, h*.24), (w*.52, h*.52)]
    star = sum(.15 * math.exp(-((x - sx)**2+(y-sy)**2) / 3.0)
               for sx, sy in stars)
    return min(1, .006 + nebula + star + .0007*math.sin(x*.16+y*.73))


def write_test(name, w, h, channels, sample_format, payload, codec='', shuffle_size=1, cfa=None, subblocks_enabled=True, raw_first=False):
    uncompressed = len(payload)
    comp_label = ''
    subblocks = ''
    compressed = payload
    if codec:
        source = shuffle(payload, shuffle_size) if shuffle_size > 1 else payload
        pieces = [source[:len(source)//2], source[len(source)//2:]] if subblocks_enabled else [source]
        compressed_pieces = []
        lengths = []
        for index, piece in enumerate(pieces):
            if raw_first and index == 0:
                c = piece   # XISF: compressed==uncompressed denotes a stored subblock
            elif codec == 'zlib':
                c = zlib.compress(piece)
            elif codec == 'zstd':
                c = subprocess.run(['zstd', '-3', '--quiet', '--stdout'], input=piece,
                                   stdout=subprocess.PIPE, check=True).stdout
            else:
                c = lz4_literals_only(piece)
            compressed_pieces.append(c)
            lengths.append(f'{len(c)},{len(piece)}')
        compressed = b''.join(compressed_pieces)
        comp_label = f' compression="{codec}{"+sh" if shuffle_size > 1 else ""}:{uncompressed}{f":{shuffle_size}" if shuffle_size > 1 else ""}"'
        if subblocks_enabled:
            subblocks = f' subblocks="{":".join(lengths)}"'
    cfa_xml = f'<ColorFilterArray pattern="{cfa}" width="2" height="2" />' if cfa else ''
    header = ('<?xml version="1.0" encoding="UTF-8"?>\n'
              '<xisf version="1.0" xmlns="http://www.pixinsight.com/xisf">\n'
              f'<Image geometry="{w}:{h}:{channels}" sampleFormat="{sample_format}" '
              f'colorSpace="{"RGB" if channels == 3 else "Gray"}" '
              f'location="attachment:4096:{len(compressed)}"{comp_label}{subblocks}>'
              f'{cfa_xml}</Image></xisf>\n').encode('utf-8')
    assert len(header) + 16 < 4096
    blob = b'XISF0100' + struct.pack('<II', len(header), 0) + header
    blob += b'\0' * (4096-len(blob)) + compressed
    (HERE / name).write_bytes(blob)


def make_mono():
    w, h = 320, 180
    pix = bytearray()
    for y in range(h):
        for x in range(w):
            pix.extend(struct.pack('<f', pixel_luminance(x, y, w, h)))
    write_test('test_mono_zlib_sh.xisf', w, h, 1, 'Float32', bytes(pix), 'zlib', 4)


def make_rgb():
    w, h = 240, 144
    pix = bytearray()
    for color in range(3):  # planar channel data
        for y in range(h):
            for x in range(w):
                value = pixel_luminance(x, y, w, h) * [1.35, 1.0, .72][color]
                pix.extend(struct.pack('<H', max(0, min(65535, int(value*65535)))))
    write_test('test_rgb_lz4hc_sh.xisf', w, h, 3, 'UInt16', bytes(pix), 'lz4hc', 2)


def make_zstd():
    w, h = 320, 180
    pix = bytearray()
    for y in range(h):
        for x in range(w):
            pix.extend(struct.pack('<f', pixel_luminance(x, y, w, h)))
    write_test('test_mono_zstd_sh.xisf', w, h, 1, 'Float32', bytes(pix), 'zstd', 4)
    write_test('test_mono_zstd_mixed_subblocks.xisf', w, h, 1, 'Float32', bytes(pix), 'zstd', 4, raw_first=True)

    w, h = 240, 144
    rgb = bytearray()
    for color in range(3):
        for y in range(h):
            for x in range(w):
                rgb.extend(struct.pack('<H', max(0, min(65535,
                    int(pixel_luminance(x, y, w, h) * [1.35, 1., .72][color] * 65535)))))
    write_test('test_rgb_zstd.xisf', w, h, 3, 'UInt16', bytes(rgb), 'zstd', subblocks_enabled=False)


def make_cfa():
    w, h = 160, 90
    pix = bytearray()
    pat = 'RGGB'
    for y in range(h):
        for x in range(w):
            color = pat[(y & 1)*2 + (x & 1)]
            gain = {'R':1.4, 'G':1., 'B':.65}[color]
            pix.extend(struct.pack('<H', max(0, min(65535, int(pixel_luminance(x, y, w, h)*65535*gain)))))
    write_test('test_cfa_uncompressed.xisf', w, h, 1, 'UInt16', bytes(pix), cfa=pat)


if __name__ == '__main__':
    make_mono()
    make_rgb()
    make_cfa()
    make_zstd()
    for p in HERE.glob('test_*.xisf'):
        print(p.name, p.stat().st_size, 'bajtów')
