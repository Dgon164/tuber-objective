"""
make_rope.py -- turn the Virtual AGC octal listing of Luminary 099 (the
Apollo 11 Lunar Module flight program, public domain) into a binary file
of tightly packed 15-bit words.

The Apollo Guidance Computer word is 15 bits.  The listing gives each word
as five octal digits.  Here every word is written as exactly 15 bits, one
after another, with no padding: 36 banks x 1024 words x 15 bits.  An
unused word (marked @ in the listing) is written as fifteen 0s.

    python make_rope.py input/Luminary099.binsource input/luminary099.rope
"""
import sys, re

src, dst = sys.argv[1], sys.argv[2]
bits = []
for line in open(src):
    if line.startswith(';') or line.startswith('BANK'):
        continue
    for tok in line.split():
        if tok == '@':
            bits.append('0' * 15)
        elif re.fullmatch(r'[0-7]{5}', tok):
            bits.append(format(int(tok, 8), '015b'))
s = ''.join(bits)
s += '0' * (-len(s) % 8)
open(dst, 'wb').write(int(s, 2).to_bytes(len(s) // 8, 'big'))
print('%d words -> %d bytes' % (len(bits), len(s) // 8))
