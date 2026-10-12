"""
same_within.py -- a new kind of same.

discovery.py knows two ways two symbols can be the same: the same word,
or runs of one class.  Here a third is added for numbers: two words are
the same if they fall in the same band of 8 (the low three bits dropped).
On the Apollo rope the words are 15-bit instructions, so two runs that
differ only by a nearby address collide, and the band stands in that
slot of the minted part: "the same instruction, to an address near X".

The hook already exists: mint() takes class_of, a map from symbol to
the thing that stands in for it when two symbols match by it.  Nothing
else in the file changes.

    python same_within.py ../examples/agc/input/luminary099.rope

Lines of new code: the ones marked NEW.
"""
import sys, os, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import discovery as D

path = sys.argv[1]
data, bits = D.read_signal(path)
frame, profile, score, folding = D.find_frame(bits)
words = D.cut_words(bits, frame)

band = {w: -1 - (w >> 3) for w in set(words)}                             # NEW: same band of 8 -> same
pool, made_of, part_of = {}, collections.defaultdict(set), collections.defaultdict(set)
L = D.run_level(words, 1, pool, made_of, part_of, 1000000, band, 0)

octal = lambda w: ('~%05o' % ((-1 - w) << 3)) if w < 0 else ('%05o' % w)  # NEW: draw a band as ~base
draw = lambda part: '.'.join(octal(w) for w in part)

plain = D.run_level(words, 1, {}, collections.defaultdict(set), collections.defaultdict(set), 1000000, None, 0)
print('plain mint:        %d parts' % len(plain['parts']))
print('with same-within:  %d parts, of which %d carry a band (~) in a slot' % (
    len(L['parts']), sum(1 for p in L['parts'] if any(w < 0 for w in p))))
print()
print('densest parts of two or more words with a band in a slot  (density = how many parts sit on them)')
banded = [p for p in L['parts'] if len(p) >= 2 and any(w < 0 for w in p)]
for p in sorted(banded, key=lambda p: -len(part_of[p]))[:14]:
    ex = sorted(part_of[p], key=lambda q: -pool.get(q, 0))[:2]
    print('  %-24s %4d   e.g. %s' % (draw(p), len(part_of[p]), ' / '.join(draw(q)[:40] for q in ex)))
