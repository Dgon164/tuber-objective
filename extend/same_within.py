"""
same_within.py -- a new kind of same.

discovery.py knows two ways two symbols can be the same: the same word,
or runs of one class.  Here a third is added for numbers: two words are
the same if they fall in the same band of 8 (the low three bits dropped).
On the Apollo rope the words are 15-bit instructions, so two runs that
differ only by a nearby address collide, and the band stands in that
slot of the minted part: "the same instruction, to an address near X".

The hook already exists: mint() takes class_of, a map from symbol to
the thing that stands in for it when two symbols match by it, and Root
takes it as `same`.  Nothing else in the file changes.

    python same_within.py ../examples/agc/input/luminary099.rope

The signal is read as discovery.py reads it (one call, Root); the lines
marked NEW are the only new thing.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import discovery as D

# ---- the signal, as discovery.py reads it -------------------------------
R = D.Root(sys.argv[1])

# ---- NEW: same band of 8 -> same, as a third way to be the same ---------
band = {w: -1 - (w >> 3) for w in set(R.words)}
B = D.Root(sys.argv[1], same=band)                                        # the same signal, read with the band
octal = lambda w: ('~%05o' % ((-1 - w) << 3)) if w < 0 else ('%05o' % w)  # NEW: draw a band as ~base
draw = lambda part: '.'.join(octal(w) for w in part)

# ---- what it found ------------------------------------------------------
print('plain mint:        %d parts' % len(R.L0['parts']))
print('with same-within:  %d parts, of which %d carry a band (~) in a slot' % (
    len(B.L0['parts']), sum(1 for p in B.L0['parts'] if any(w < 0 for w in p))))
print()
print('densest parts of two or more words with a band in a slot  (density = how many parts sit on them)')
banded = [p for p in B.L0['parts'] if len(p) >= 2 and any(w < 0 for w in p)]
for p in sorted(banded, key=lambda p: -len(B.part_of[p]))[:14]:
    ex = sorted(B.part_of[p], key=lambda q: -B.pool.get(q, 0))[:2]
    print('  %-24s %4d   e.g. %s' % (draw(p), len(B.part_of[p]), ' / '.join(draw(q)[:40] for q in ex)))
