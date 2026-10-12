"""
same_slot.py -- a new kind of "same" for whole runs: two runs are the same
in a slot when they sit between the same left neighbour and the same right
neighbour.  "the ___ said" holds King, Queen, Hatter; "to ___ the" holds
see, get, open.

discovery.py's classes group a part by what it CHANGES INTO (walk ->
walked, walking).  This groups a run by WHERE IT STANDS: the comparator on
contexts instead of on spellings.  Every slot a run fills is kept with a
count; two runs are compared by the slots they share (the bridge on slot
sets).  Nothing is dropped; the tables show the top of each list.

    python same_slot.py ../examples/text/alice.txt

Given: the cut at space and newline, as in alice.txt.sep20-0a.record.txt.
"""
import sys, os, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import discovery as D

path = sys.argv[1]
data, bits = D.read_signal(path)
frame, profile, score, folding = D.find_frame(bits)
words = D.cut_words(bits, frame)
runs = D.cut_runs(words, {0x20, 0x0a})
G = D.Glyphs(D.make_lens('ascii', frame))
draw = lambda r: G.draw(r)

# NEW: every slot a run fills -- (left neighbour, right neighbour)
slots = collections.defaultdict(collections.Counter)      # run -> slot -> count
fillers = collections.defaultdict(collections.Counter)    # slot -> run -> count
for a, w, b in zip(runs, runs[1:], runs[2:]):
    slots[w][(a, b)] += 1
    fillers[(a, b)][w] += 1

# NEW: two runs are compared by the slots they share
def mates(w):
    shared = collections.Counter()
    for s in slots[w]:
        for m in fillers[s]:
            if m != w:
                shared[m] += 1
    return shared

count = collections.Counter(runs)
print('%d runs, %d distinct, %d distinct slots' % (len(runs), len(count), len(fillers)))
print()
print('SLOTS   the slots with the most different fillers (top 20)')
for s, f in sorted(fillers.items(), key=lambda kv: -len(kv[1]))[:20]:
    print('  %-22s %4d fillers: %s' % ('%s ___ %s' % (draw(s[0]), draw(s[1])), len(f),
          ', '.join(draw(r) for r, _ in f.most_common(10))))
print()

probe = [w for w, _ in count.most_common(40)]
for extra in ['Alice', 'King', 'Queen', 'Hatter', 'little', 'large', 'looked', 'went',
              'thought', 'head', 'could', 'would', 'must', 'very', 'Rabbit', 'door',
              'him', 'them', 'my', 'his', 'this', 'two', 'three', 'never', 'quite']:
    t = tuple(ord(c) for c in extra)
    if t in count and t not in probe:
        probe.append(t)
print('SLOT-MATES   for each run: the runs that share the most slots with it (slots shared)')
for w in probe:
    m = mates(w).most_common(10)
    print('  %-10s %5d  %s' % (draw(w), count[w], ', '.join('%s %d' % (draw(r), c) for r, c in m)))
