"""
sentence.py -- write sentences from what Discovery learned.

The record gives run_follows: which English words come after which,
and how often.  A sentence is a chain of follows from a starter to
an ender.  No grammar, no templates -- just what was found.

    python sentence.py ../examples/text/alice.txt [N sentences]

The signal is read as discovery.py reads it; the sections marked NEW are
the only new thing.
"""
import sys, os, re, time, collections, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import discovery as D

T0 = time.time()
path = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 10

# ---- the signal, as discovery.py reads it -------------------------------
R = D.Root(path)
T1 = time.time()

text = lambda t: bytes(t).decode('latin-1')

# ---- NEW: the follows table as a chain to walk --------------------------
# run_follows: (run_a, run_b) -> count
rfol = R.L0['run_follows']

# build adjacency: word -> [(next_word, count), ...]
adj = collections.defaultdict(list)
for (a, b), n in rfol.items():
    adj[text(a)].append((text(b), n))
# sort each by count descending
for k in adj:
    adj[k].sort(key=lambda x: -x[1])

# sentence starters: words that follow something ending in . ! ? and start uppercase
# sentence enders: words ending in . ! ?
def is_ender(w):
    w = w.rstrip()
    return w.endswith('.') or w.endswith('!') or w.endswith('?')

starters = collections.Counter()
for (a, b), n in rfol.items():
    ta, tb = text(a), text(b)
    if is_ender(ta) and tb and tb[0].isupper():
        starters[tb] += n

T2 = time.time()

# ---- NEW: make a sentence: follow the chain ------------------------------
def make_sentence(max_words=25):
    if not starters:
        return None
    # weighted pick of starter
    items = starters.most_common(50)
    total = sum(c for _, c in items)
    r = random.random() * total
    cum = 0
    start = items[0][0]
    for w, c in items:
        cum += c
        if cum >= r:
            start = w
            break

    sentence = [start]
    current = start
    seen = {start}

    for _ in range(max_words):
        followers = adj.get(current)
        if not followers:
            break
        # weighted pick from top followers, avoid repeats
        cands = [(w, c) for w, c in followers[:15] if w not in seen or is_ender(w)]
        if not cands:
            cands = followers[:5]
        total = sum(c for _, c in cands)
        r = random.random() * total
        cum = 0
        picked = cands[0][0]
        for w, c in cands:
            cum += c
            if cum >= r:
                picked = w
                break
        sentence.append(picked)
        seen.add(picked)
        current = picked
        if is_ender(picked):
            break

    return ' '.join(sentence)


# ---- what it found ------------------------------------------------------
print('record %.1fs, build %.1fs' % (T1 - T0, T2 - T1))
print('%d words with followers, %d starters' % (len(adj), len(starters)))
print()

for i in range(N):
    s = make_sentence()
    if s:
        print('%2d  %s' % (i + 1, s))

T3 = time.time()
print('\ntotal %.1fs' % (T3 - T0))
