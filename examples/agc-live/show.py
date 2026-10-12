"""
show.py -- print a trace in octal so a person can read it.

    python show.py writes.bin [N]        first N memory writes (default 40)
    python show.py channels.bin [N]      first N channel packets

This is a lens: it changes how the records are displayed and nothing
else. Discovery never sees the names.
"""
import struct
import sys

OPCODES = {0: 'TC', 1: 'CCS/TCF', 2: 'DAS/LXCH/INCR/ADS', 3: 'CA', 4: 'CS',
           5: 'INDEX/DXCH/TS/XCH', 6: 'AD', 7: 'MASK'}


def writes(path, n):
    with open(path, 'rb') as f:
        data = f.read(10 * n)
    print(' instr   word   opcode             erasable   old     new')
    for i in range(0, len(data) - 9, 10):
        ia, iw, ea, old, new = struct.unpack('>5H', data[i:i + 10])
        print(f'{ia:6d}  {iw:05o}  {OPCODES[iw >> 12]:18s} {ea:04o}      {old:06o}  {new:06o}')


def channels(path, n):
    with open(path, 'rb') as f:
        data = f.read(4 * n)
    print(' channel  value')
    for i in range(0, len(data) - 3, 4):
        b = data[i:i + 4]
        ch = (b[0] << 3) | ((b[1] >> 3) & 7)
        v = ((b[1] & 7) << 12) | ((b[2] & 0x3f) << 6) | (b[3] & 0x3f)
        print(f'   {ch:03o}    {v:05o}')


if __name__ == '__main__':
    path = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    (channels if 'channel' in path else writes)(path, n)
