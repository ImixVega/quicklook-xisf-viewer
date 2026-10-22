"""Source-byte decompression smoke test for supplied fixtures (requires zstd CLI)."""
from pathlib import Path
import struct
import zlib
import subprocess
import xml.etree.ElementTree as ET
from make_test_xisf import shuffle

here = Path(__file__).resolve().parent
for path in here.glob('test_*.xisf'):
    blob = path.read_bytes()
    assert blob[:8] == b'XISF0100'
    n, reserved = struct.unpack_from('<II', blob, 8)
    root = ET.fromstring(blob[16:16+n])
    image = next(iter(root))
    geo = list(map(int, image.attrib['geometry'].split(':')))
    fmt = image.attrib['sampleFormat']
    sz = {'Float32': 4, 'UInt16': 2}[fmt]
    off, cmp_size = map(int, image.attrib['location'].split(':')[1:])
    source = blob[off:off+cmp_size]
    if 'compression' in image.attrib:
        c = image.attrib['compression'].split(':')
        pieces = []
        pos = 0
        entries = image.attrib.get('subblocks', f'{len(source)},{c[1]}').split(':')
        for entry in entries:
            packed_len, orig_len = map(int, entry.split(','))
            block = source[pos:pos+packed_len]
            if packed_len == orig_len:
                expanded = block
            elif c[0].startswith('zlib'):
                expanded = zlib.decompress(block)
            elif c[0].startswith('zstd'):
                expanded = subprocess.run(['zstd', '-d', '--quiet', '--stdout'], input=block,
                                          stdout=subprocess.PIPE, check=True).stdout
            else:
                # literal-only LZ4 blocks created by test generator
                i=1; literal=block[0]>>4
                if literal == 15:
                    while True:
                        b = block[i]; i += 1; literal += b
                        if b != 255: break
                expanded=block[i:i+literal]
            assert len(expanded) == orig_len, (path, len(expanded), orig_len)
            pieces.append(expanded)
            pos += packed_len
        assert pos == len(source)
        output = b''.join(pieces)
        if '+sh' in c[0]:
            shuffle_size = int(c[2]); nitems=len(output)//shuffle_size
            output = bytes(output[b*nitems+i] for i in range(nitems) for b in range(shuffle_size))
    else:
        output=source
    assert len(output) == geo[0]*geo[1]*geo[2]*sz, (path, len(output))
    print('OK', path.name, geo, fmt, len(output), 'bajtów danych obrazu')
