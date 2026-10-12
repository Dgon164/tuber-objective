"""
Discovery -- finds structure in any file, from scratch.
Jason Weeks, thetuberobjective@gmail.com -- github.com/Dgon164/tuber-objective

The whole thing boils down to one operation: compare two things.

    same       what the two things have in common
    different  what's left over once you take that out
    not part   everything the comparison didn't touch

That's it. The program runs this comparison on the raw bits, then on its
own results, over and over until nothing new shows up.

Input   any file, read as raw bits. It doesn't assume any format.
Output  a record (plain text and JSON) of everything it found:
        what each piece is made of, what contains it, what shows up
        before and after it, and how to turn one piece into another.

No dependencies.  Run:  python discovery.py FILE [--lens ascii|utf8|octal]
                        python discovery.py --help   for the other options
From Python:            R = discovery.Root(FILE)   gives you the signal, level 0, and the pool;
                        discover() does all of that plus every level and writes the record.
"""

import sys, os, json, collections, heapq, bisect


class Refusal(ValueError):
    """When the program can't do what you asked -- wrong option, incompatible
    memory file, etc. -- it says why and stops cleanly instead of crashing."""


# --------------------------------------------------------------------------
# 1. SIGNAL  -- read the file as a string of 0s and 1s
# --------------------------------------------------------------------------

def read_signal(path, limit=None):
    data = open(path, 'rb').read()
    if limit is not None:
        data = data[:limit]
    if not data:
        return data, ''
    bits = bin(int.from_bytes(data, 'big'))[2:].zfill(len(data) * 8)
    return data, bits


# --------------------------------------------------------------------------
# 2. FRAME  -- figure out how wide one "word" is
#
# Imagine laying all the bits out in rows of some width w. Each column
# (every w-th bit starting at position c) has a rate: how often it's a 1.
# At the RIGHT width, each column has its own personality -- for example,
# with 8-bit ASCII text, column 0 is never 1 and column 2 almost always
# is. At the WRONG width, all the columns blur together to similar rates.
#
# So we score each width by the spread between its most-1 column and its
# least-1 column. Biggest spread wins. A wider width has to beat a narrower
# one by more than you'd expect from random chance.
#
# Then we check for multiples. Width 16 on 8-bit text is just the same 8
# columns repeated twice. If the winning width's column rates are a
# smaller width's rates repeated (within the wobble you'd get by chance),
# we fold down to that smaller width.
#
# We only look at the first 64 KB of the file to decide this.
# --------------------------------------------------------------------------

def find_frame(bits, widest=64, sample=1 << 19, force=None):
    s = bits[:sample]
    profile, score = {}, {}
    for w in range(1, widest + 1):
        cols = []
        for c in range(w):
            col = s[c::w]
            cols.append(col.count('1') / len(col) if col else 0.5)
        profile[w] = cols
        score[w] = max(cols) - min(cols)
    picked = 1
    for w in range(2, widest + 1):
        rows = len(s) // w
        chance = 1 / rows ** 0.5 if rows else 1
        if score[w] > score[picked] + chance:
            picked = w
    fold = {}                                   # divisor -> mean difference from picked's columns
    rows = max(len(s) // picked, 1)
    wobble = 0.5 / rows ** 0.5
    frame = picked
    for w in range(1, picked):
        if picked % w:
            continue
        fold[w] = sum(abs(profile[picked][c] - profile[w][c % w]) for c in range(picked)) / picked
        if fold[w] <= wobble and frame == picked:
            frame = w
    return force or frame, profile, score, {'picked': picked, 'wobble': wobble, 'fold': fold}


# --------------------------------------------------------------------------
# 3. WORDS  -- chop the bits into words and count them
# --------------------------------------------------------------------------

def cut_words(bits, width):
    return [int(bits[i:i + width], 2) for i in range(0, len(bits) - width + 1, width)]


def count(items):
    return collections.Counter(items)


def follows(items):
    return collections.Counter(zip(items, items[1:]))


# --------------------------------------------------------------------------
# 4. RUNS  -- the most common word is the separator (like spaces in text,
#             or zero bytes in a program). A "run" is everything between
#             two separators -- basically, a word or chunk.
# --------------------------------------------------------------------------

def cut_runs(words, separators):
    runs, run = [], []
    for word in words:
        if word in separators:
            if run:
                runs.append(tuple(run))
                run = []
        else:
            run.append(word)
    if run:
        runs.append(tuple(run))
    return runs


# --------------------------------------------------------------------------
# 5. MINT  -- smash parts together until nothing new comes out
#
# Start with every distinct run in a sorted list (the "pool"). Neighbors
# in sorted order share the longest common beginning. That shared piece
# and the two leftover tails become new parts and go back into the pool.
# Do the same thing backwards (mirror everything) to catch shared endings.
# Keep going until a round produces nothing new. Nothing ever gets deleted.
#
# Since nothing gets removed, two parts that were neighbors last round are
# still neighbors this round, so we only bother comparing pairs where at
# least one of them is new from the last round.
#
# Two elements count as "the same" if they're identical, OR if they belong
# to the same class (classes come from the level below; there aren't any
# at level 0). When they match by class, the class marker takes that slot
# in the shared piece -- so the new part is the pattern they share, with
# the class standing in for where they differ.
#
# The pool, made_of, and part_of are shared across all levels, so new
# parts automatically connect to whatever they're built from.
#
# Memory: parts that were in the pool from a previous run (loaded from a
# file). They sit in the sorted pool next to the new runs, so new things
# collide with remembered things too. But a comparison only counts if the
# current signal is involved -- two old remembered parts that this signal
# hasn't touched get left alone. When a remembered part comes out of a
# comparison again, it's "confirmed" and gets one more round of being
# treated as fresh. Reading the same signal twice confirms everything from
# the first time. The record reports what happened: confirmed (was in
# memory AND showed up again), added (brand new), not seen (was in memory
# but didn't come up this time).
#
# Cap: the pool can get huge on big signals with long runs. If it passes
# the cap, the loop stops early and the record says so. This is just a
# memory limit, not part of the method -- raise it or use a smaller signal.
# --------------------------------------------------------------------------

def node(x):
    """Unwrap single-element wrappers. A run containing just one run IS
    that run, so connections should point to the thing itself."""
    return x[0] if isinstance(x, tuple) and len(x) == 1 and isinstance(x[0], tuple) else x


def mint(run_counts, pool, made_of, part_of, cap=1000000, class_of=None, level=0, memory=()):
    mine = set(run_counts)                     # all parts at this level
    produced = set(node(r) for r in run_counts)
    for r in run_counts:
        k = node(r)
        pool[k] = pool.get(k, 0) + (run_counts[r] if level == 0 else 0)   # only count whole occurrences at level 0
    remembered_only = set()                    # old parts from memory that this signal hasn't seen yet
    reached = set(run_counts)                  # everything this signal has touched so far
    if memory and run_counts:
        d = depth(next(iter(run_counts)))
        remembered_only = set(p for p in memory if depth(p) == d and not is_token(p)) - mine
        mine |= remembered_only
    if not class_of:
        class_of = {}

    def head(a, b):
        h = []
        for x, y in zip(a, b):
            if x == y:
                h.append(x)
            elif x in class_of and class_of[x] == class_of.get(y):
                h.append(class_of[x])
            else:
                break
        return tuple(h)

    if not class_of:
        def head(a, b):                        # no classes to worry about: just find the shared beginning
            i = 0
            for x, y in zip(a, b):
                if x != y:
                    break
                i += 1
            return a[:i]

    def merged(keys, batch):
        """Merge a sorted batch into a sorted list. Returns the combined
        list and the positions where each batch item ended up."""
        out, at, i = [], [], 0
        for item in batch:
            j = bisect.bisect_left(keys, item, i)
            out += keys[i:j]
            at.append(len(out))
            out.append(item)
            i = j
        out += keys[i:]
        return out, at

    endings = collections.Counter()            # leftover tails after a shared beginning
    beginnings = collections.Counter()         # leftover fronts before a shared ending
    rounds = []
    reached_again = []                         # per round: how many old memories got re-confirmed
    nodal = level > 0                          # at level 0 a part is its own node
    # We keep the pool sorted in two ways: forward (the parts themselves) and
    # mirrored (reversed, so we can find shared endings). Each round, we only
    # compare pairs where at least one part is new. First round compares
    # everything; after that, just the freshly added ones and their neighbors.
    order = [sorted(mine), sorted((p[::-1], p) for p in mine)]
    pending = [[], []]                         # minted since each order was last merged
    forward_made, carried = [], []             # mirrored versions of what the forward pass just made
    touched = []                               # old memories re-confirmed last round -- they get one more fresh round
    r = 0
    while True:
        new = set()
        touched_now = []
        for mirror in (False, True):
            keys, at = order[mirror], []
            if pending[mirror]:
                pending[mirror].sort()
                keys, at = merged(keys, pending[mirror])
                order[mirror], pending[mirror] = keys, []
            if mirror:
                at += [bisect.bisect_left(keys, e) for e in carried]
                carried, forward_made = forward_made, []
            at += [bisect.bisect_left(keys, (p[::-1], p) if mirror else p) for p in touched]
            if r == 0:
                left = range(len(keys) - 1)
            else:
                left = sorted(set(i for j in at for i in (j - 1, j) if 0 <= i < len(keys) - 1))
            tally = beginnings if mirror else endings
            for i in left:
                x, y = keys[i], keys[i + 1]
                if mirror:
                    (a2, a), (b2, b) = x, y
                else:
                    a2 = a = x
                    b2 = b = y
                if a not in reached and b not in reached:
                    continue                   # both are old memories this signal hasn't touched -- skip
                h = head(a2, b2)
                n = len(h)
                if n == 0:
                    continue
                same = h[::-1] if mirror else h
                for whole, flipped in ((a, a2), (b, b2)):
                    if same == whole:
                        continue                       # nothing left over -- the whole thing IS the shared part
                    rest = flipped[n:]
                    if mirror:
                        rest = rest[::-1]
                    wn = node(whole) if nodal else whole
                    for piece in ((same, rest) if rest else (same,)):
                        k = node(piece) if nodal else piece
                        produced.add(k)
                        made_of[wn].add(k)
                        part_of[k].add(wn)
                        if k not in pool:
                            pool[k] = 0
                            mine.add(piece)
                            new.add(piece)
                            reached.add(piece)
                            pending[0].append(piece)
                            e = (piece[::-1], piece)
                            pending[1].append(e)
                            if not mirror:
                                forward_made.append(e)
                        elif piece in remembered_only and piece not in reached:
                            reached.add(piece)         # this signal just re-confirmed an old memory -- give it one more fresh round
                            touched_now.append(piece)
                    if rest:
                        tally[rest] += 1
        rounds.append(len(new))
        reached_again.append(len(touched_now))
        touched = touched_now
        if not new and not touched:
            break
        if len(pool) > cap:
            rounds.append('stopped: pool passed the cap of %d parts' % cap)
            break
        r += 1
    return mine, produced, endings, beginnings, rounds, reached_again


# --------------------------------------------------------------------------
# 6. CRYSTAL  -- group parts by what they have in common
#
# The pool stays as-is; the crystal is a second view that reads it.
#
#   change(part -> parent): the piece you'd add to turn the part into
#       a bigger part. "+rest" means it goes on the end, "rest+" on the front.
#   class: parts that take the same set of changes belong to the same group.
#       (Like how "walk", "talk", "look" all take "+ed" and "+ing".)
# --------------------------------------------------------------------------

def depth(x):
    d = 0
    while isinstance(x, tuple):
        d += 1
        x = x[0] if x else 0
    return d


def as_element_of(part, parent):
    """Wrap or unwrap a part so it matches the nesting level of its parent's elements."""
    return (part,) if depth(parent) == depth(part) + 1 else part


def changes_of(part, part_of):
    out = set()
    k = node(part)
    d = depth(k)
    for parent in part_of.get(k, ()):
        p = (k,) if depth(parent) == d + 1 else k   # as_element_of, with the part's depth found once
        n = len(p)
        if parent[0] == p[0] and parent[:n] == p:
            out.add(('+', parent[n:]))
        elif parent[-1] == p[-1] and parent[-n:] == p:
            out.add((parent[:-n], '+'))
    return out


def changes_in_order(part, part_of, pool):
    """Same as changes_of, but as a list ordered by how common the parent is."""
    seen, out = set(), []
    for parent in sorted(part_of.get(node(part), ()), key=lambda q: -pool.get(q, 0)):
        p = as_element_of(node(part), parent)
        if parent[:len(p)] == p:
            ch = ('+', parent[len(p):])
        elif parent[-len(p):] == p:
            ch = (parent[:-len(p)], '+')
        else:
            continue
        if ch not in seen:
            seen.add(ch)
            out.append(ch)
    return out


def crystallize(parts, part_of):
    classes = collections.defaultdict(list)
    for part in parts:
        ch = frozenset(changes_of(part, part_of))
        if len(ch) >= 2:
            classes[ch].append(part)
    return sorted(classes.items(), key=lambda kv: (-len(kv[1]), sorted(kv[1])))


def class_token(level, i):
    """Make a placeholder that can stand in for any member of a class
    in the sequence one level up. Uses negative numbers so it's easy to spot."""
    tok = (-1 - i,)
    for _ in range(level):
        tok = (tok,)
    return tok


def is_token(x):
    while isinstance(x, tuple):
        if len(x) != 1:
            return False
        x = x[0]
    return isinstance(x, int) and x < 0


# --------------------------------------------------------------------------
# 7. LEVELS  -- zoom out, one level at a time, until there's nothing left
#
# Each level does: count the symbols, split at the most common one, smash
# parts together (mint), and group them (crystallize). Then the runs from
# this level become the symbols for the next level -- nothing gets replaced,
# and this level's classes become another way two things can count as
# "the same." Everything each level finds (runs of runs, minted parts,
# classes) goes into one shared pool with connections to everything else.
#
# Each level's sequence is shorter than the last (since the separator is
# always present), so the loop naturally stops when a level has just one
# run left. In practice the additions shrink to nothing well before that.
# --------------------------------------------------------------------------

def run_level(seq, separators, pool, made_of, part_of, cap, class_of, level, memory=frozenset(),
              earlier=frozenset()):
    counts = count(seq)
    flw = follows(seq)
    if isinstance(separators, (list, tuple)):
        sep = list(separators)
    else:
        sep = [w for w, n in counts.most_common(int(separators))]
    runs = cut_runs(seq, set(sep))
    run_counts = count(runs)
    run_follows = follows(runs)
    before = len(pool)
    mine, produced, endings, beginnings, rounds, reached_again = mint(run_counts, pool, made_of, part_of, cap,
                                                                      class_of, level, memory)
    classes = crystallize(mine, part_of)
    d = depth(next(iter(run_counts))) if run_counts else 0
    remembered = set(p for p in memory if depth(p) == d and not is_token(p))
    confirmed = produced & remembered
    new = produced - memory - earlier            # not remembered, not made by an earlier level of this run
    unseen = remembered - produced
    next_class_of = {}
    for i, (ch, members) in enumerate(classes):
        if len(members) >= 2:
            tok = class_token(level, i)
            for m in members:
                next_class_of[m] = tok
    return dict(level=level, seq=seq, counts=counts, follows=flw, separator=sep, runs=runs,
                run_counts=run_counts, run_follows=run_follows, parts=mine,
                endings=endings, beginnings=beginnings, rounds=rounds, reached_again=reached_again, classes=classes,
                minted=sum(x for x in rounds if isinstance(x, int)),
                added=len(pool) - before, total=len(pool), next_class_of=next_class_of,
                produced=produced, confirmed=confirmed, new=new, unseen=unseen, remembered=remembered)


def run_levels(words, separators, cap, pool=None, made_of=None, part_of=None):
    pool = {} if pool is None else pool
    made_of = collections.defaultdict(set) if made_of is None else made_of
    part_of = collections.defaultdict(set) if part_of is None else part_of
    memory = frozenset(pool)                   # snapshot of what was in memory before this signal
    levels, seq, class_of, earlier = [], words, None, set()
    while True:
        L = run_level(seq, separators if not levels else 1, pool, made_of, part_of, cap,
                      class_of, len(levels), memory, earlier)
        levels.append(L)
        earlier |= L['produced']
        seq, class_of = L['runs'], L['next_class_of']
        if len(seq) < 2:
            break
    return levels, pool, made_of, part_of


# --------------------------------------------------------------------------
# 7b. TIME  -- reading the sequence as a timeline
#
# The signal is in order, and that order is time. FOLLOWS already tracks
# what comes right after what. Here we get three more views:
#
#   arrows    when A->B and B->A both happen, which direction wins?
#             The winning direction is the arrow; the margin is its strength.
#   effects   what shows up after a part more often than you'd expect by
#             chance? We look at a window after each occurrence (sized to
#             match the signal's own rhythm) and compare what we see vs.
#             what we'd expect if things were random.
#   chains    follow the strongest effect forward: a -> b -> c -> ...
#
# For a signal you're just observing, this gives you before-and-after.
# With a "do" (like in examples/agc-live: press a button, record what
# happens, compare), the effect that only shows up after the press is
# what the press caused.
# --------------------------------------------------------------------------

def time_tables(runs, run_counts, run_follows, window, top):
    n = len(runs)
    arrows = []
    for (a, b), c in run_follows.items():
        back = run_follows.get((b, a))
        if a == b or back is None or c < back or (c == back and not a < b):
            continue
        arrows.append((c - back, c, back, a, b))
    arrows.sort(key=lambda t: (-t[0], -t[1], t[3], t[4]))
    arrows = [(a, b, c, back) for d, c, back, a, b in arrows[:top]]

    at = collections.defaultdict(list)
    for i, r in enumerate(runs):
        at[r].append(i)

    def effects_of(a):
        after, slots = collections.Counter(), 0
        for i in at[a]:
            w = runs[i + 1:i + 1 + window]
            after.update(w)
            slots += len(w)
        out = []
        for b, c in after.items():
            expected = slots * run_counts[b] / n
            if c >= 2 and c >= 2 * expected:          # shows up at least twice and at 2x the background rate -- that's a real effect
                out.append((c - expected, b, c, expected))
        out.sort(key=lambda t: (-t[0], t[1]))
        return [(b, c, expected) for d, b, c, expected in out[:8]]

    found = {}
    for a, c in run_counts.most_common(top):
        found[a] = effects_of(a)
    effects = [(a, found[a]) for a, c in run_counts.most_common(top)]

    chains = []
    for a, c in run_counts.most_common(min(top, 10)):
        chain = [a]
        while len(chain) < 5:
            x = chain[-1]
            if x not in found:
                found[x] = effects_of(x)
            step = [b for b, c2, e in found[x] if b not in chain]
            if not step:
                break
            chain.append(step[0])
        if len(chain) > 1:
            chains.append(chain)
    return dict(window=window, arrows=arrows, effects=effects, chains=chains)


def tuples(x):
    """Convert a part from JSON format (nested lists) back to the tuples
    the pool uses internally."""
    return tuple(tuples(e) for e in x) if isinstance(x, list) else x


def load_memory(path):
    """Load a memory file (JSON). It stores the pool as [part, count] pairs,
    part_of as [part, [containers]] pairs (made_of is rebuilt from that),
    and a history of which signals have been read. Any program can open
    this file -- it's just data, no code gets executed."""
    if not path or not os.path.exists(path):
        return {}, collections.defaultdict(set), collections.defaultdict(set), []
    raw = open(path, 'rb').read()
    if not raw.lstrip().startswith(b'{'):
        raise Refusal('%s is not a JSON memory (earlier versions wrote a pickle, which is no longer read): '
                      'delete it and run the signals again' % path)
    M = json.loads(raw)
    pool = {tuples(k): c for k, c in M['pool']}
    part_of = collections.defaultdict(set, {tuples(k): set(tuples(v) for v in vs) for k, vs in M['part_of']})
    made_of = collections.defaultdict(set)
    for part, wholes in part_of.items():
        for whole in wholes:
            made_of[whole].add(part)
    return pool, made_of, part_of, [tuple(h) for h in M['history']]


def save_memory(path, pool, made_of, part_of, history):
    M = {'pool': [[k, c] for k, c in pool.items()],
         'part_of': [[k, list(v)] for k, v in part_of.items()],
         'history': history}
    open(path, 'wb').write(json.dumps(M, separators=(',', ':')).encode())


# --------------------------------------------------------------------------
# 8. LENS  -- how to display things (purely cosmetic, doesn't affect the algorithm)
# --------------------------------------------------------------------------

def make_lens(name, width):
    hexw = (width + 3) // 4

    def raw(word):
        return format(word, '0%dx' % hexw)

    def ascii_glyph(word):
        if 32 <= word < 127:
            return chr(word)
        return {10: '\\n', 13: '\\r', 9: '\\t'}.get(word, '\\x%02x' % word)

    if name == 'octal':
        octw = (width + 2) // 3
        return (lambda word: format(word, '0%do' % octw)), \
               (lambda run: '.'.join(format(w, '0%do' % octw) for w in run))
    if name == 'ascii' and width == 8:
        return ascii_glyph, lambda run: ''.join(ascii_glyph(w) for w in run)
    if name == 'utf8' and width == 8:
        def run_glyph(run):
            try:
                s = bytes(run).decode('utf8')
                return s.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            except UnicodeDecodeError:
                return ''.join(ascii_glyph(w) for w in run)
        return ascii_glyph, run_glyph
    return raw, lambda run: '.'.join(raw(w) for w in run)


class Glyphs:
    """Turns any part into readable text. Words use the lens, runs show
    their words, higher-level parts show their pieces, and classes show
    as {level.index}."""

    def __init__(self, lens, wide=72):
        self.g0, self.r0 = lens
        self.wide = wide

    def draw(self, x):
        x = node(x)
        if isinstance(x, int):
            return self.g0(x)
        if is_token(x):
            d = depth(x)
            while isinstance(x, tuple):
                x = x[0]
            return '{%d.%d}' % (d - 1, -1 - x)
        d = depth(x)
        if d == 1:
            return self.r0(x)
        sep = ' ' if d == 2 else ' | '
        pieces, n = [], -len(sep)              # running length of what we've built so far
        for e in x:
            if n > self.wide:                  # too wide for display, stop here
                break
            s = self.draw(e)
            pieces.append(s)
            n += len(s) + len(sep)
        text = sep.join(pieces)
        return text if len(text) <= self.wide else text[:self.wide] + '...'   # truncate for display

    def change(self, d, x):
        return ('+' + self.draw(x)) if d == '+' else (self.draw(d) + '+')


# --------------------------------------------------------------------------
# 9. RECORD  -- write everything that was found to text and JSON files
# --------------------------------------------------------------------------

def write_level(say, L, G, pool, made_of, part_of, top, frame):
    n = L['level']
    draw = G.draw
    what = 'word' if n == 0 else 'symbol'

    if n == 0:
        say('WORDS   %d words, %d distinct' % (len(L['seq']), len(L['counts'])))
        say('  %-*s  %-6s  %s' % (frame, 'bits', 'glyph', 'count'))
        for wd, c in L['counts'].most_common(top):
            say('  %s  %-6s  %d' % (format(wd, '0%db' % frame), draw(wd), c))
    else:
        say('SYMBOLS   %d symbols, %d distinct  (each is a level %d run; level %d classes count as same)'
            % (len(L['seq']), len(L['counts']), n - 1, n - 1))
        for wd, c in L['counts'].most_common(top):
            say('  %-40s  %d' % (draw(wd), c))
    say('')

    say('FOLLOWS   which %s comes after which (top %d of %d pairs)' % (what, top, len(L['follows'])))
    for (a, b), c in L['follows'].most_common(top):
        say('  %-24s -> %-24s  %d' % (draw(a), draw(b), c))
    say('')

    say('SEPARATOR   the most common %s%s: %s' % (
        what, 's' if len(L['separator']) > 1 else '',
        ', '.join(('%s (%s)' % (format(x, '0%db' % frame), draw(x))) if n == 0 else draw(x)
                  for x in L['separator'])))
    say('')

    say('RUNS   %d runs between separators, %d distinct' % (len(L['runs']), len(L['run_counts'])))
    for r, c in L['run_counts'].most_common(top):
        say('  %-40s  %d' % (draw(r), c))
    say('')

    say('RUN FOLLOWS   which run comes after which (top %d of %d pairs)' % (top, len(L['run_follows'])))
    for (a, b), c in L['run_follows'].most_common(top):
        say('  %-24s -> %-24s  %d' % (draw(a), draw(b), c))
    say('')

    T = L.get('time')
    if T:
        short = lambda x: (lambda s: s if len(s) <= 24 else s[:24] + '...')(draw(x))   # truncate for display
        say('TIME   the sequence read as time; the stretch after a run is %d runs (the typical distance to the next level\'s separator)'
            % T['window'])
        say('  ARROWS   pairs seen in both orders, counted each way (top %d by the difference)' % top)
        for a, b, c, back in T['arrows']:
            say('    %-27s -> %-27s  %6d   the other way %d' % (short(a), short(b), c, back))
        say('  EFFECTS   what comes in the stretch after a run more often than it comes overall: seen/expected')
        for a, eff in T['effects']:
            if eff:
                say('    %-27s %s' % (short(a), ', '.join('%s %d/%.1f' % (short(b), c, e) for b, c, e in eff[:6])))
        say('  CHAINS   the strongest effect, followed forward')
        for chain in T['chains']:
            say('    ' + ' -> '.join(short(x) for x in chain))
        say('')

    say('MINT   %d rounds; parts minted per round: %s' % (len(L['rounds']), ' '.join(map(str, L['rounds']))))
    if L['remembered']:
        say('  remembered parts this signal produced again, per round: %s' % ' '.join(map(str, L['reached_again'])))
    say('  pool: %d distinct runs in, %d structures added, %d in the pool now' % (
        len(L['run_counts']), L['added'], L['total']))
    say('')

    whole = lambda p: pool.get(node(p), 0) if n == 0 else L['run_counts'].get(p, 0)
    dens = lambda p: len(part_of.get(node(p), ()))
    say('PARTS BY DENSITY   density = how many parts this one sits inside, at any level (top %d)' % top)
    say('  %-30s  %7s  %6s  %s' % ('part', 'density', 'whole', 'inside (sample)'))
    dense = heapq.nsmallest(top, L['parts'], key=lambda p: (-dens(p), -whole(p), p))
    for p in dense:
        inside = sorted(part_of.get(node(p), ()), key=lambda q: -pool.get(q, 0))[:4]
        say('  %-30s  %7d  %6d  %s' % (draw(p), dens(p), whole(p), ', '.join(draw(q) for q in inside)))
    say('')

    say('ENDINGS   what gets added to the end of a part to make another (top %d)' % top)
    for e, c in L['endings'].most_common(top):
        say('  +%-24s  %d' % (draw(e), c))
    say('')

    say('BEGINNINGS   what gets added to the start of a part to make another (top %d)' % top)
    for b, c in L['beginnings'].most_common(top):
        say('  %24s+  %d' % (draw(b), c))
    say('')

    say('CLASSES   parts that take the same set of changes (largest %d of %d; two or more members count as same one level up)'
        % (top, len(L['classes'])))
    for i, (ch, members) in enumerate(L['classes'][:top]):
        label = ', '.join(sorted(G.change(d, x) for d, x in ch))
        members = sorted(members, key=lambda p: -whole(p))
        say('  {%d.%d} [%s]' % (n, i, label))
        say('     %d members: %s' % (len(members), ', '.join(draw(m) for m in members[:12])))
    say('')

    say('CRYSTAL   dictionary entries for the most common runs (top %d)' % top)
    nxt = collections.defaultdict(collections.Counter)
    prv = collections.defaultdict(collections.Counter)
    for (a, b), c in L['run_follows'].items():
        nxt[a][b] += c
        prv[b][a] += c
    for r, c in L['run_counts'].most_common(top):
        k = node(r)
        say('  %s   seen %d' % (draw(r), c))
        say('    made of    %s' % ', '.join(draw(q) for q in sorted(made_of.get(k, ()), key=lambda q: -depth(q) * 1000 - len(q))[:8]))
        say('    part of    %s' % ', '.join(draw(q) for q in sorted(part_of.get(k, ()), key=lambda q: -pool.get(q, 0))[:8]))
        say('    changes    %s' % ', '.join(G.change(d, x) for d, x in changes_in_order(r, part_of, pool)[:8]))
        say('    followed   %s' % ', '.join('%s %d' % (draw(q), kk) for q, kk in nxt[r].most_common(6)))
        say('    preceded   %s' % ', '.join('%s %d' % (draw(q), kk) for q, kk in prv[r].most_common(6)))
    say('')


def key_of(x, frame, keys=None):
    """Turn any part into a string key for JSON output. Level-0 runs become
    hex words joined by dots, deeper parts join their pieces with spaces
    or pipes, and classes show as {level.index}."""
    if keys is None:
        keys = Keys(frame)
    x = node(x)
    k = keys.get(x)
    if k is not None:
        return k
    if isinstance(x, int):
        k = format(x, '0%dx' % ((frame + 3) // 4))
    elif is_token(x):
        d = depth(x)
        while isinstance(x, tuple):
            x = x[0]
        k = '{%d.%d}' % (d - 1, -1 - x)
    else:
        d = depth(x)
        k = ('.' if d == 1 else ' ' if d == 2 else ' | ').join([keys[e] for e in x])
    keys[x] = k
    return k


class Keys(dict):
    """Lookup from parts to their JSON key strings. Auto-generates a key
    the first time you ask for a part."""

    def __init__(self, frame):
        self.frame = frame

    def __missing__(self, x):
        k = key_of(x, self.frame, self)
        self[x] = k
        return k


def level_json(L, pool, made_of, part_of, G, frame, keys=None):
    kc = Keys(frame) if keys is None else keys
    key = kc.__getitem__
    n = L['level']
    parts = {}
    for p in L['parts']:
        k = node(p)
        parts[kc[p]] = {'whole': pool.get(k, 0),
                        'density': len(part_of.get(k, ())),
                        'made_of': [kc[q] for q in made_of.get(k, ())],
                        'part_of': [kc[q] for q in part_of.get(k, ())]}
    return {
        'level': n,
        'separator': [key(s) if n else s for s in L['separator']],
        'words': {key(k) if n else str(k): v for k, v in L['counts'].items()},
        'follows': [[key(a) if n else a, key(b) if n else b, c] for (a, b), c in L['follows'].items()],
        'runs': {key(r): c for r, c in L['run_counts'].items()},
        'run_follows': [[key(a), key(b), c] for (a, b), c in L['run_follows'].items()],
        'parts': parts,
        'endings': {key(e): c for e, c in L['endings'].items()},
        'beginnings': {key(b): c for b, c in L['beginnings'].items()},
        'classes': [{'id': '%d.%d' % (n, i),
                     'changes': sorted(('+' + key(x)) if d == '+' else (key(d) + '+') for d, x in ch),
                     'members': [key(m) for m in members]} for i, (ch, members) in enumerate(L['classes'])],
        'rounds': L['rounds'], 'minted': L['minted'], 'added': L['added'], 'total': L['total'],
        'time': None if 'time' not in L else {
            'window': L['time']['window'],
            'arrows': [[key(a), key(b), c, back] for a, b, c, back in L['time']['arrows']],
            'effects': {key(a): [[key(b), c, round(e, 2)] for b, c, e in eff] for a, eff in L['time']['effects']},
            'chains': [[key(x) for x in chain] for chain in L['time']['chains']]},
    }


def write_record(out_txt, out_json, name, data, bits, frame, profile, score, folding,
                 levels, pool, made_of, part_of, lens, top, memory=None):
    G = Glyphs(lens)
    T = []
    say = T.append

    say('DISCOVERY RECORD')
    say('signal     %s' % name)
    say('size       %d bytes, %d bits' % (len(data), len(bits)))
    say('')

    say('FRAME   score = spread between the column most often 1 and the column least often 1')
    say('  width  score   least-1 column   most-1 column      (best 8 of %d widths tried)' % len(profile))
    ranked = sorted(profile, key=lambda w: (-score[w], w))
    for w in ranked[:8]:
        lo = min(range(w), key=lambda c: profile[w][c])
        hi = max(range(w), key=lambda c: profile[w][c])
        say('  %3d    %.3f   col %3d at %.3f   col %3d at %.3f' % (w, score[w], lo, profile[w][lo], hi, profile[w][hi]))
    say('  picked width %d' % folding['picked'])
    for w, d in sorted(folding['fold'].items()):
        say('    fold to %2d: columns differ by %.4f on average (wobble by chance %.4f) -> %s'
            % (w, d, folding['wobble'], 'same' if d <= folding['wobble'] else 'different'))
    say('  chosen width %d' % frame)
    say('  column rates at width %d:' % frame)
    say('    ' + ' '.join('%.3f' % r for r in profile[frame]))
    say('')

    say('LEVELS   each level runs on the runs of the one before; nothing replaced, every structure added to one pool')
    say('  level  symbols  distinct     runs  distinct   minted  classes(2+)    added  pool total')
    for L in levels:
        say('  %5d  %7d  %8d  %7d  %8d  %7d  %11d  %7d  %10d' % (
            L['level'], len(L['seq']), len(L['counts']), len(L['runs']), len(L['run_counts']),
            L['minted'], sum(1 for ch, m in L['classes'] if len(m) >= 2), L['added'], L['total']))
    say('  stopped: level %d left a single run; nothing more to cut' % levels[-1]['level'])
    say('')

    if memory:
        say('MEMORY   %s' % memory['path'])
        say('  before this signal: %d parts, from %s' % (
            memory['parts_before'],
            ', '.join('%s (%d bytes, frame %d)' % h for h in memory['history_before']) or 'nothing'))
        say('  this signal, against memory:')
        say('  level  produced  confirmed      added  not seen this time')
        for L in levels:
            say('  %5d  %8d  %9d  %9d  %18d' % (
                L['level'], len(L['produced']), len(L['confirmed']), len(L['new']), len(L['unseen'])))
        say('  after: %d parts, saved' % len(pool))
        say('')

    for i, L in enumerate(levels):
        above = levels[i + 1]['runs'] if i + 1 < len(levels) else ()
        window = max(1, round(len(L['runs']) / len(above))) if above else len(L['runs'])
        L['time'] = time_tables(L['runs'], L['run_counts'], L['run_follows'], window, top)

    for L in levels:
        say('=' * 78)
        say('LEVEL %d' % L['level'])
        say('=' * 78)
        say('')
        write_level(say, L, G, pool, made_of, part_of, top, frame)

    open(out_txt, 'w', encoding='utf-8').write('\n'.join(T) + '\n')

    keys = Keys(frame)                         # one key table shared across all levels
    J = {
        'signal': name, 'bytes': len(data), 'bits': len(bits),
        'frame': frame, 'profile': {str(w): profile[w] for w in profile},
        'frame_score': {str(w): score[w] for w in score},
        'frame_fold': {'picked': folding['picked'], 'wobble': folding['wobble'],
                       'fold': {str(w): d for w, d in folding['fold'].items()}},
        'pool': len(pool),
        'memory': None if not memory else {
            'path': memory['path'], 'parts_before': memory['parts_before'],
            'history_before': memory['history_before'],
            'levels': [{'produced': len(L['produced']), 'confirmed': len(L['confirmed']),
                        'added': len(L['new']), 'unseen': len(L['unseen'])} for L in levels]},
        'levels': [level_json(L, pool, made_of, part_of, G, frame, keys) for L in levels],
    }
    open(out_json, 'wb').write(json.dumps(J, separators=(',', ':')).encode())   # compact JSON, no extra whitespace
    return '\n'.join(T)


# --------------------------------------------------------------------------
# 10. RUN  -- put it all together
#
# Root is the starting point for anything built on Discovery: it reads the
# file, figures out the frame, chops it into words, and runs level 0 on a
# shared pool. You can then call for more levels as needed. discover() is
# Root plus all levels plus writing the record. Every script in extend/
# and hybrid/ is just Root plus one new idea.
# --------------------------------------------------------------------------

class Root:
    """The starting point for reading any signal with Discovery.

        R = Root(path)                 reads the file, finds the frame, runs level 0
        R.words, R.frame               the signal as a list of numbers, and how wide each one is
        R.L0                           level 0 results: runs, counts, classes, etc.
        R.pool, R.made_of, R.part_of   the shared pool and all the connections between parts
        R.level(seq, separators, class_of)   run one more level on the same pool
        R.all_levels()                 keep running levels until there's nothing left to split
        R.draw(x)                      show any part as readable text

    separators: 1 for the most common word, N for the N most common, or
    a specific list of words. same: a map from a word to what stands in
    for it when two words should count as matching (used by
    extend/same_within.py). pool, made_of, part_of, history: pass these
    in to start from a saved memory (from load_memory). A memory only
    works at one frame width -- the same number means different things
    at different widths.
    """

    def __init__(self, path, separators=1, lens='raw', same=None, cap=1000000, limit=None,
                 widest=64, frame=None, pool=None, made_of=None, part_of=None, history=()):
        self.path = path
        self.name = os.path.basename(path)
        self.data, self.bits = read_signal(path, limit)
        self.frame, self.profile, self.score, self.folding = find_frame(self.bits, widest, force=frame)
        frames = sorted(set(h[2] for h in history))
        if frames and self.frame not in frames:
            raise Refusal('%s reads at %d bits; the memory holds signals read at %s. A memory is one frame: '
                          'use another memory file, or --frame %d to read this signal at the memory\'s width.'
                          % (self.name, self.frame, ', '.join(map(str, frames)), frames[0]))
        self.words = cut_words(self.bits, self.frame)
        self.pool = {} if pool is None else pool
        self.made_of = collections.defaultdict(set) if made_of is None else made_of
        self.part_of = collections.defaultdict(set) if part_of is None else part_of
        self.memory = frozenset(self.pool)       # snapshot of the pool before this signal
        self.earlier = set()                     # parts produced by earlier levels of this run
        self.cap = cap
        self.levels = []
        self.glyphs = Glyphs(make_lens(lens, self.frame))
        self.L0 = self.level(self.words, separators, same)

    def level(self, seq, separators=1, class_of=None):
        """Run one more level: split at the separator, smash parts together, group them."""
        L = run_level(seq, separators, self.pool, self.made_of, self.part_of, self.cap,
                      class_of, len(self.levels), self.memory, self.earlier)
        self.levels.append(L)
        self.earlier |= L['produced']
        return L

    def all_levels(self):
        """Keep running levels (each one on the runs of the one before,
        using its classes as another way things can match) until there's
        only one run left."""
        while len(self.levels[-1]['runs']) >= 2:
            L = self.levels[-1]
            self.level(L['runs'], 1, L['next_class_of'])
        return self.levels

    def draw(self, x):
        return self.glyphs.draw(x)


def discover(path, lens='raw', limit=None, widest=64, top=25, out=None, quiet=False,
             separators=1, frame=None, cap=1000000, memory=None):
    forced = frame
    pool, made_of, part_of, history = load_memory(memory)
    mem = None
    if memory:
        mem = {'path': memory, 'parts_before': len(pool), 'history_before': list(history)}
    if isinstance(separators, str) and not separators.isdigit():
        # separator given as hex values: 20,0a  or  0x20  or  20,  (plain digits are a count: --separators 2)
        names = [h.strip().lower() for h in separators.split(',')]
        names = [h[2:] if h.startswith('0x') else h for h in names if h]
        try:
            sep0 = [int(h, 16) for h in names]
            sep_tag = '.sep' + '-'.join(names) if len(names) > 1 else '.sepx' + names[0]
        except (ValueError, IndexError):
            raise Refusal('--separators %s: give a count (2), or words in hex (20,0a; one word as 0x20 or 20,)' % separators)
    else:
        sep0 = int(separators)
        sep_tag = '.sep%d' % sep0 if sep0 > 1 else ''
    R = Root(path, sep0, lens, cap=cap, limit=limit, widest=widest, frame=frame,
             pool=pool, made_of=made_of, part_of=part_of, history=history)
    R.all_levels()
    if memory:
        history.append((R.name, len(R.data), R.frame))
        save_memory(memory, R.pool, R.made_of, R.part_of, history)

    out = out or os.path.dirname(os.path.abspath(path))
    os.makedirs(out, exist_ok=True)
    tag = R.name + ('.frame%d' % forced if forced else '') + sep_tag + ('.m%d' % len(history) if memory else '')
    out_txt = os.path.join(out, tag + '.record.txt')
    out_json = os.path.join(out, tag + '.record.json')
    text = write_record(out_txt, out_json, R.name, R.data, R.bits, R.frame, R.profile, R.score, R.folding,
                        R.levels, R.pool, R.made_of, R.part_of, make_lens(lens, R.frame), top, mem)
    if not quiet:
        print(text)
        print('record written: %s' % out_txt)
    return out_txt, out_json


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__)
        print('options: --lens raw|ascii|utf8|octal  --limit BYTES  --widest BITS  --frame BITS  '
              '--top N  --separators N|HEX,HEX,...  --cap PARTS  --memory FILE  --out DIR  --quiet')
        return
    path, opts = argv[0], {}
    if path.startswith('-'):
        raise Refusal('the first argument is the file to read; the options come after it')
    known = ('lens', 'limit', 'widest', 'frame', 'top', 'separators', 'cap', 'memory', 'out')
    i = 1
    while i < len(argv):
        if argv[i] == '--quiet':
            opts['quiet'] = True
            i += 1
        else:
            name = argv[i].lstrip('-')
            if not argv[i].startswith('--') or name not in known:
                raise Refusal('%s is not an option; python discovery.py --help lists them' % argv[i])
            if i + 1 >= len(argv):
                raise Refusal('--%s needs a value' % name)
            opts[name] = argv[i + 1]
            i += 2
    discover(path,
             lens=opts.get('lens', 'raw'),
             limit=int(opts['limit']) if 'limit' in opts else None,
             widest=int(opts.get('widest', 64)),
             top=int(opts.get('top', 25)),
             out=opts.get('out'),
             quiet=opts.get('quiet', False),
             separators=opts.get('separators', 1),
             frame=int(opts['frame']) if 'frame' in opts else None,
             cap=int(opts.get('cap', 1000000)),
             memory=opts.get('memory'))


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
