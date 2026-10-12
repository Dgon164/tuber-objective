"""
template.py -- the shape of a program built on Discovery.  Copy it, keep
the first and last sections, write the middle one.

    python template.py ../examples/text/alice.txt

As it stands it points the comparator at one thing: for the most common
runs, what follows them most, and how much of the time.  Replace that.
The signal is read as discovery.py reads it (one call, Root); the lines
marked NEW are the only new thing.
"""
import sys, os, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import discovery as D

# ---- the signal, as discovery.py reads it -------------------------------
R = D.Root(sys.argv[1], lens='ascii')
#   R.words, R.frame        the signal as words of R.frame bits
#   R.L0                    level 0: runs, run_counts, run_follows, parts, endings, beginnings, classes
#   R.pool, R.part_of       the shared pool: part -> whole count; part -> what it sits inside
#   R.level(seq, separators, class_of)   one more level on the same pool
#   R.all_levels()          every level, as discover() runs them
#   R.draw(x)               a part as text

# ---- NEW: the one new thing ---------------------------------------------
after = collections.defaultdict(collections.Counter)      # run -> what follows it -> count
for (a, b), n in R.L0['run_follows'].items():
    after[a][b] += n

# ---- what it found ------------------------------------------------------
print('%d runs, %d distinct; the most common and what follows them' % (len(R.L0['runs']), len(R.L0['run_counts'])))
for r, c in R.L0['run_counts'].most_common(12):
    nxt = after[r].most_common(4)
    print('  %-12s %6d   %s' % (R.draw(r), c, ', '.join('%s %d%%' % (R.draw(b), 100 * n // c) for b, n in nxt)))
