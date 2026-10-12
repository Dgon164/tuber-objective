"""
functions.py -- connections, then functions, then functions of functions.

Layer 0, the record.  discovery.py on the signal, its own cut.  Parts,
    what each is made of, what contains it.

Layer 1, functions.  Every change the crystal found (+ed, un+, +ly) is a
    node that turns one part into another: f(x) = pre + x + post.  A
    function acts on WHOLE RUNS -- parts the signal stands up on its own
    (whole count above 0).  Fragments (e, ucked) are what changes are made
    of, not what they act on; a fragment takes nearly every change and so
    says nothing about any one of them.  Its
    IN-KIND is learned from the parts it was seen on: the other functions
    those parts also take.  Its OUT-KIND is the functions seen applied to
    what it makes.  A change seen on fewer than two parts is a connection,
    not yet a function (two make a group, as with the classes).

Layer 2, functions of functions.
    siblings     g and h are siblings when two or more parts take both.
    paths        f then g is legal when g is in f's out-kind: g was seen
                 applied to something f made.

Making a word.  A path is run on a part that does not yet have it:
    g(x) is offered when x takes siblings of g.  Its STANDING is the
    comparator's answer, both sides: SAME = the functions x takes that
    are unflagged siblings of g; DIFFERENT = the functions x takes that
    are not.  Standing = same - different.  A part that takes a little of
    everything (a, it, to) agrees with every function and is like none of
    them; it scores low.  Highest standing first; 0 or below is not
    offered.
    A made word is a part too: the functions in its maker's out-kind are
    offered on it next (paths two and three deep).

Holds and flags.  Each (function g, sibling h) pair is a hold: "g takes
    what h takes".  An answer is a read against it.
    yes  sets it (and resets a flag on it).
    no   counts against it; two noes and no yes raise a NEGATIVE FLAG:
         "g does not take what h takes".  Held, and reset by a yes.
    The same rule one size up: a FUNCTION whose outputs have been
    refused twice and never taken is flagged -- it emits a kind the key
    does not take (word -> word-plus-comma).  Its offers stand lower by
    its refusals.  Reset by a yes.
    A seam the signal never shows (the symbol pair where the change meets
    the part never sits side by side in the signal) is a negative flag
    read from the signal: it counts one against the offer.  It is reset
    when a yes passes through that seam.
    Feedback acts on the producer (the hold), not on the record.

What ships (compaction).  The function table: each function, what it was
    seen on, what it made, its flags; the paths that worked.  The attempt
    log is kept as the cost of finding them.

Given (stated): the answer key (a word list, the only selection signal);
"not in the signal" = not a whole word of the signal, lower-cased.

    python functions.py ../examples/text/alice.txt [N] [WORDLIST]

The signal is read as discovery.py reads it; the sections marked NEW are
the only new thing.
"""
import sys, os, re, time, heapq, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import discovery as D

T0 = time.time()
path = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 100
wordlist = sys.argv[3] if len(sys.argv) > 3 else '/usr/share/dict/american-english'

# ---- the signal, as discovery.py reads it (layer 0: the record) ---------
data, bits = D.read_signal(path)
frame, profile, score, folding = D.find_frame(bits)
words = D.cut_words(bits, frame)
pool, made_of, part_of = {}, collections.defaultdict(set), collections.defaultdict(set)
L0 = D.run_level(words, 1, pool, made_of, part_of, 1000000, None, 0)
fol = L0['follows']
T1 = time.time()

text = lambda t: bytes(t).decode('latin-1')
key = set(w.strip() for w in open(wordlist, encoding='utf-8', errors='replace'))
seen = set(re.findall(r"[a-z']+", data.decode('latin-1').lower()))

def apply(f, x):
    pre, post = f
    return (pre if pre != '+' else ()) + x + (post if post != '+' else ())

def show(f):
    pre, post = f
    return ('+' + text(post)) if pre == '+' else (text(pre) + '+')

# ---- NEW: layer 1, functions --------------------------------------------
dom = collections.defaultdict(set)                  # f -> parts it was seen on
kind = collections.defaultdict(set)                 # part -> functions it takes
runs = [p for p in L0['parts'] if pool.get(p, 0) > 0]       # whole runs: what the signal stands up on its own
for p in runs:
    for f in D.changes_of(p, part_of):
        dom[f].add(p)
funcs = {f for f, d in dom.items() if len(d) >= 2}
for f in funcs:
    for p in dom[f]:
        kind[p].add(f)
outk = collections.defaultdict(collections.Counter)  # f -> functions seen on what f made
for f in funcs:
    for p in dom[f]:
        for g in kind.get(apply(f, p), ()):
            outk[f][g] += 1

# ---- NEW: layer 2, siblings ---------------------------------------------
pair = collections.Counter()
for p, ks in kind.items():
    ks = sorted(ks, key=repr)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            pair[(ks[i], ks[j])] += 1
sib = collections.defaultdict(set)
for (a, b), n in pair.items():
    if n >= 2:
        sib[a].add(b); sib[b].add(a)
T2 = time.time()
print('record %.1fs functions %.1fs; %d funcs, %d pairs, max kind %d' % (T1-T0, T2-T1, len(funcs), len(pair), max(len(k) for k in kind.values())), flush=True)

# ---- NEW: making words --------------------------------------------------
yes_h, no_h = collections.Counter(), collections.Counter()   # (g, h) holds
flag = set()                                                  # negative flags (g, h)
yes_g, no_g = collections.Counter(), collections.Counter()    # per function: does what it makes get taken?
seam_ok = set()                                               # seams reset by a yes

def seam(f, x):
    pre, post = f
    return (x[-1], post[0]) if pre == '+' else (pre[-1], x[0])

def standing(g, x, via=None):
    k = kind.get(x, frozenset())
    both = k & sib[g]
    same = len(both)
    if flag:
        same -= sum(1 for h in both if (g, h) in flag)
    s = same - (len(k) - same)                     # same minus different: the comparator, both sides
    if via is not None:
        s += via                                   # a path: what its maker's outputs took
    if no_g[g] >= 2 and not yes_g[g]:
        s -= no_g[g]                               # flagged function: its outputs are a kind not taken
    sm = seam(g, x)
    if sm not in fol and sm not in seam_ok:
        s -= 1                                     # never side by side in the signal
    return s

heap, offered, tick = [], set(), [0]
def offer(g, x, via=None):
    if (g, x) in offered:
        return
    offered.add((g, x))
    s = standing(g, x, via)
    if s > 0:
        tick[0] += 1; heapq.heappush(heap, (-s, tick[0], g, x, via))

for x, ks in kind.items():                       # one function on a part that lacks it
    cand = set()
    for h in ks:
        cand |= sib[h]
    for g in cand - ks:
        offer(g, x)

print('offers %d at %.1fs' % (len(heap), time.time()-T0), flush=True)
tried, made, log, recalls = set(), [], [], 0
while heap and len(made) < N:
    negs, _, g, x, via = heapq.heappop(heap)
    s = standing(g, x, via)
    if s < -negs:                                # a flag came up since: back in at its new standing
        if s > 0:
            tick[0] += 1; heapq.heappush(heap, (-s, tick[0], g, x, via))
        continue
    w = apply(g, x)
    wt = text(w)
    if wt.lower() in seen:
        recalls += 1
        continue
    if wt in tried:
        continue
    tried.add(wt)
    ok = wt in key
    hs = [h for h in kind.get(x, ()) if h in sib[g]]
    for h in hs:
        if ok:
            yes_h[(g, h)] += 1; flag.discard((g, h))
        else:
            no_h[(g, h)] += 1
            if no_h[(g, h)] >= 2 and not yes_h[(g, h)]:
                flag.add((g, h))
    (yes_g if ok else no_g)[g] += 1
    if ok:
        seam_ok.add(seam(g, x))
    log.append((len(log) + 1, wt, text(x), show(g), s, 'path' if via is not None else 'sibling', ok))
    if ok:
        made.append((len(log), wt, text(x), show(g), via is not None))
        kind[w] |= set()                         # a made word is a part
        for f2, n in outk[g].most_common():      # paths: what g's outputs were seen to take
            offer(f2, w, via=n)
T3 = time.time()

# ---- what it found (what ships) -----------------------------------------
out = os.path.splitext(os.path.basename(path))[0] + '.functions.txt'
fails = len(log) - len(made)
with open(out, 'w') as f:
    say = lambda s='': f.write(s + '\n')
    say('FUNCTIONS   signal %s   answer key %s' % (os.path.basename(path), wordlist))
    say('  time: record %.1fs, functions %.1fs, making %.1fs, total %.1fs'
        % (T1 - T0, T2 - T1, T3 - T2, T3 - T0))
    say('  %d changes in the record, %d are functions (seen on 2+ parts), %d sibling links'
        % (len(dom), len(funcs), sum(len(v) for v in sib.values()) // 2))
    say('  %d made, %d failed attempts, %d attempts, %d recalls, %d negative flags at the end'
        % (len(made), fails, len(log), recalls, len(flag)))
    say()
    say('MADE   n  word              part + function     how      attempt#  failed before it')
    prev = 0
    for i, (at, wt, xt, gt, isp) in enumerate(made, 1):
        say('  %3d  %-17s %-19s %-8s %8d  %d' % (i, wt, '%s %s' % (xt, gt), 'path' if isp else 'sibling', at, at - prev - 1))
        prev = at
    say()
    say('THE FUNCTION TABLE   (compacted: what was found, not the search)')
    say('  function   seen on  made  refused  siblings  flags  out-kind (what its outputs take)')
    used = collections.Counter(); bad = collections.Counter()
    for at, wt, xt, gt, s, how, ok in log:
        (used if ok else bad)[gt] += 1
    say('  flagged functions (outputs refused 2+, never taken): %d' % sum(1 for g in no_g if no_g[g] >= 2 and not yes_g[g]))
    shown = sorted(funcs, key=lambda g: (-used[show(g)], -len(dom[g]), show(g)))[:40]
    for g in shown:
        nf = sum(1 for (a, b) in flag if a == g)
        ok_out = ', '.join(show(h) for h, _ in outk[g].most_common(5))
        say('  %-10s %7d  %4d  %7d  %8d  %5d  %s' % (show(g), len(dom[g]), used[show(g)], bad[show(g)], len(sib[g]), nf, ok_out))
    say()
    say('NEGATIVE FLAGS   g does not take what h takes  (most refusals first)')
    fl = sorted(flag, key=lambda gh: -no_h[gh])[:40]
    say('  ' + ', '.join('%s !~ %s (%d)' % (show(a), show(b), no_h[(a, b)]) for a, b in fl))
    say()
    say('EVERY ATTEMPT   #  word  part  function  standing  how  answer')
    for at, wt, xt, gt, s, how, ok in log:
        say('  %5d  %-22r %-18r %-8s %3d  %-8s %s' % (at, wt, xt, gt, s, how, 'yes' if ok else 'no'))
print('made %d, failed %d, attempts %d, recalls %d  | record %.1fs, functions %.1fs, making %.1fs  -> %s'
      % (len(made), fails, len(log), recalls, T1 - T0, T2 - T1, T3 - T2, out))
