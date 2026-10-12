"""
row_by_row.py -- a new place to point the comparator: a row against the
row before it.

The frame step compares a column with itself one row down.  A signal
with time in it (a state sequence) has a second kind of sameness: this
row against the previous row.  Same bits stayed; different bits flipped.
The flips, row by row, are a new signal, and Discovery reads that new
signal exactly as it reads any other.

Input: the reservoir states from hybrid/net_as_lens.py (32 units, one
bit each, one row per byte of Alice fed through the net).

    python row_by_row.py ../hybrid/alice.txt.reservoir

The signal is read as discovery.py reads it (one call, Root); the lines
marked NEW are the only new thing.
"""
import sys, os, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import discovery as D

# ---- the signal, as discovery.py reads it -------------------------------
path = sys.argv[1]
R = D.Root(path)
rows, frame = R.words, R.frame

# ---- NEW: a row against the row before it -------------------------------
flips = [a ^ b for a, b in zip(rows, rows[1:])]
per_column = [sum((f >> (frame - 1 - c)) & 1 for f in flips) / len(flips) for c in range(frame)]
print('frame %d; %d rows; %d row-to-row comparisons' % (frame, len(rows), len(flips)))
print('units that flip least:  %s' % ', '.join('unit %2d %.3f' % (c, per_column[c]) for c in sorted(range(frame), key=lambda c: per_column[c])[:5]))
print('units that flip most:   %s' % ', '.join('unit %2d %.3f' % (c, per_column[c]) for c in sorted(range(frame), key=lambda c: -per_column[c])[:5]))
print('bits flipped per step:  %.2f of %d on average; %d steps with no change' % (
    sum(bin(f).count('1') for f in flips) / len(flips), frame, sum(1 for f in flips if f == 0)))
print()
print('most common changes (which units flipped together):')
for f, n in collections.Counter(flips).most_common(8):
    print('  %s  %d' % (format(f, '0%db' % frame), n))

# ---- the flips, as discovery.py reads them: a new signal ----------------
out = os.path.join(os.path.dirname(os.path.abspath(path)), os.path.basename(path) + '.flips')
open(out, 'wb').write(b''.join(f.to_bytes(frame // 8, 'big') for f in flips))   # NEW: written out as bytes
txt, js = D.discover(out, quiet=True, out=os.path.dirname(os.path.abspath(__file__)))

# ---- what it found ------------------------------------------------------
rec = open(txt).read().split('LEVEL 1')[0]                                # level 0 only
print()
print('Discovery on the flips (level 0):')
print('\n'.join(l for l in rec.splitlines() if l.startswith(('  chosen width', 'WORDS', 'SEPARATOR', 'RUNS', 'MINT'))))
