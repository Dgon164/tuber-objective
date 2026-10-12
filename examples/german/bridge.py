"""
bridge.py -- the same comparator, run between two records instead of
inside one.

Discovery was run on the German text and on its English translation,
separately.  Each run produced a pool of parts.  This script collides the
two pools: a part that exists in both pools is SAME across the two
languages; its parents on each side are the DIFFERENT half.

    python bridge.py ep-00-01-17.de.record.json ep-00-01-17.en.record.json

Nothing here knows what German or English is.  It only reads the two
JSON records, which were made from bits.
"""

import sys, json


def load(path):
    rec = json.load(open(path))
    return rec['levels'][0]['parts']          # level 0: the parts of the signal itself


def glyph(key):
    """A part key is hex bytes joined by '.'  Draw it as text (UTF-8),
    falling back to escapes.  Display only."""
    raw = bytes(int(h, 16) for h in key.split('.'))
    try:
        return raw.decode('utf8').replace('\n', '\\n')
    except UnicodeDecodeError:
        return ''.join(chr(b) if 32 <= b < 127 else '\\x%02x' % b for b in raw)


def main(a_path, b_path, top=40, longest_first=True):
    A, B = load(a_path), load(b_path)
    shared = [k for k in A if k in B]
    # rank: a shared part is more interesting the more parents it has on
    # BOTH sides, and the longer it is
    def rank(k):
        return (min(A[k]['density'], B[k]['density']), len(k))
    shared.sort(key=rank, reverse=True)

    print('BRIDGE   %d parts in A, %d in B, %d shared' % (len(A), len(B), len(shared)))
    print()
    print('  %-16s %7s %7s   %-34s %s' % ('shared part', 'dens A', 'dens B', 'parents in A', 'parents in B'))
    for k in shared[:top]:
        pa = sorted((q for q in A[k]['part_of'] if q in A), key=lambda q: -A[q]['whole'])[:3]
        pb = sorted((q for q in B[k]['part_of'] if q in B), key=lambda q: -B[q]['whole'])[:3]
        print('  %-16s %7d %7d   %-34s %s' % (glyph(k), A[k]['density'], B[k]['density'],
                                             ', '.join(glyph(q) for q in pa),
                                             ', '.join(glyph(q) for q in pb)))

    print()
    print('LONG SHARED PARTS   (4 or more words long, by length)')
    long_shared = [k for k in shared if len(k.split('.')) >= 4]
    long_shared.sort(key=lambda k: (-len(k.split('.')), -min(A[k]['density'], B[k]['density'])))
    for k in long_shared[:top]:
        pa = sorted((q for q in A[k]['part_of'] if q in A), key=lambda q: -A[q]['whole'])[:2]
        pb = sorted((q for q in B[k]['part_of'] if q in B), key=lambda q: -B[q]['whole'])[:2]
        print('  %-20s  A: %-30s  B: %s' % (glyph(k), ', '.join(glyph(q) for q in pa), ', '.join(glyph(q) for q in pb)))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
