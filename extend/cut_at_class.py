"""
cut_at_class.py -- a new cut.  Same comparator, same mint, same crystal;
the only change is where the run sequence is cut one level up.

discovery.py cuts every level at its most common symbol (for Alice,
level 1 cuts at "the").  Here level 1 is cut at a CLASS instead: every
run that belongs to the largest level-0 class is a separator.  For Alice
the largest class is {+ed, +ing} -- the stems that take both -- so the
level-1 runs are the stretches between those stems.

    python cut_at_class.py ../examples/text/alice.txt

The signal is read as discovery.py reads it (one call, Root); the lines
marked NEW are the only new thing.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import discovery as D

# ---- the signal, as discovery.py reads it -------------------------------
R = D.Root(sys.argv[1], lens='ascii')

# ---- NEW: level 1 cut at the largest level-0 class ----------------------
changes, members = R.L0['classes'][0]
label = ', '.join(sorted(R.glyphs.change(d, x) for d, x in changes))
seps = set(m for m in members)
# a member that is a stem (never a whole run) cannot be a separator; its parents can:
# every whole run that is made of a member counts as that member.        # NEW
seps |= set(parent for m in members for parent in R.part_of.get(m, ()) if parent in R.L0['run_counts'])
L1 = R.level(R.L0['runs'], sorted(seps), R.L0['next_class_of'])

# ---- what it found ------------------------------------------------------
print('level 1 cut at class [%s]: %d separators (the stems and the whole runs built on them)' % (label, len(seps)))
print('  %d runs between them, %d distinct, %d parts minted' % (len(L1['runs']), len(L1['run_counts']), L1['minted']))
print()
print('RUNS (stretches between those stems)')
for r, c in L1['run_counts'].most_common(12):
    print('  %-50s %d' % (R.draw(r), c))
print()
print('ENDINGS (what sits right before such a stem)        BEGINNINGS (right after)')
E = L1['endings'].most_common(10); B = L1['beginnings'].most_common(10)
for i in range(10):
    e = ('+' + R.draw(E[i][0]), E[i][1]) if i < len(E) else ('', '')
    b = (R.draw(B[i][0]) + '+', B[i][1]) if i < len(B) else ('', '')
    print('  %-30s %-6s   %30s %s' % (e[0], e[1], b[0], b[1]))
