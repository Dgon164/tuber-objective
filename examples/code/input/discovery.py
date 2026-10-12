"""
Discovery -- the learning subroutine.

One mechanism: a comparator and a memory.

    same       the part two signals share
    different  what is left of each once the shared part is removed
    not part   what the comparison never touched

Everything in this file is that one mechanism, run over the signal and
then over its own results, until nothing new comes out.

Input   any file, read as bits.  No format is assumed.
Output  a record (plain text and JSON) of the parts that were found,
        what each is made of, what it is part of, what comes before and
        after it, and which change turns one part into another.

No dependencies.  Run:  python discovery.py FILE [--lens ascii|utf8|octal]
                        python discovery.py --help   for the other options
"""

import sys, os, json, pickle, collections, heapq, bisect


# --------------------------------------------------------------------------
# 1. SIGNAL  -- the file as a string of bits
# --------------------------------------------------------------------------

def read_signal(path, limit=None):
    data = open(path, 'rb').read()
    if limit:
        data = data[:limit]
    if not data:
        return data, ''
    bits = bin(int.from_bytes(data, 'big'))[2:].zfill(len(data) * 8)
    return data, bits


# --------------------------------------------------------------------------
# 2. FRAME  -- how wide is one word?
#
# Lay the bits in rows of width w.  Column c is every w-th bit starting at
# bit c, and its rate is how often that bit is a 1.  At the right width
# each column has its own habit: at width 8, column 0 of plain ASCII text
# is never 1 and column 2 is nearly always 1.  At a wrong width the
# columns all drift to the same rate.
#
# score(w) = the spread between the column that is 1 most often and the
# column that is 1 least often.  Pick the width with the biggest spread; a
# wider width only takes over if it beats the narrower one by more than
# chance would give with that many rows.
#
# Then fold.  A multiple of the true frame is the true frame's columns laid
# side by side (width 16 on 8-bit text is the 8 columns twice).  If the
# picked width's column rates are a smaller width's rates repeated, within
# the wobble a rate can have by chance (half over root rows), the frame is
# that smaller width.  Smallest divisor that fits wins.
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
# 3. WORDS  -- cut the signal into words, count them, count what follows
# --------------------------------------------------------------------------

def cut_words(bits, width):
    return [int(bits[i:i + width], 2) for i in range(0, len(bits) - width + 1, width)]


def count(items):
    return collections.Counter(items)


def follows(items):
    return collections.Counter(zip(items, items[1:]))


# --------------------------------------------------------------------------
# 4. RUNS  -- the most common word is the separator; a run is what sits
#             between separators.  (Space in text.  The zero byte in a
#             compiled program.)
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
# 5. MINT  -- collide parts until nothing new comes out
#
# The pool starts as every distinct run.  Sort the pool; neighbours in
# sorted order share the longest head any two parts share.  The shared
# head and the two remainders are minted as new parts and rejoin the
# pool.  Do the same on the mirrored parts to catch shared tails.
# Loop until a round mints nothing.  Nothing is ever removed.
#
# Two neighbours that were both in the pool last round were neighbours
# last round too (nothing is ever removed), so a pair is only compared
# when at least one of the two is fresh from the last round.
#
# Two elements are the same if they are the same, or if they belong to the
# same class (classes come from the level below; there are none at level
# 0).  When two elements are the same only by class, the class stands in
# that slot of the shared head, so the minted part is the pattern the two
# have in common with the class in the place where they differ.
#
# The pool, made_of and part_of are shared by every level, so a new part
# adds connections to the parts it is made of wherever those live.
#
# memory: the parts that were in the pool before this signal arrived
# (loaded from a memory file).  Remembered parts of this level's depth sit
# in the sorted pool next to the new runs, so a new run collides with what
# is remembered as well as with the rest of the signal.  Remembered parts
# are fresh in the first round like everything else, so they are compared
# again too; a remembered part that comes out of a comparison again is
# confirmed.  What this run produces is reported against memory:
# confirmed (remembered and produced again), added (new), not seen
# (remembered, not produced this time).
#
# cap: the pool can grow large on a big signal with long runs.  When it
# passes the cap the loop stops early and the record says so.  This is a
# memory limit, not part of the method; raise it or cut the signal.
# --------------------------------------------------------------------------

def node(x):
    """A part of one element, at a level above 0, IS that element: a run
    of one run is the run.  Connections land on the element itself."""
    return x[0] if isinstance(x, tuple) and len(x) == 1 and isinstance(x[0], tuple) else x


def mint(run_counts, pool, made_of, part_of, cap=1000000, class_of=None, level=0, memory=()):
    mine = set(run_counts)                     # this level's parts, in this level's form
    produced = set(node(r) for r in run_counts)
    for r in run_counts:
        k = node(r)
        pool[k] = pool.get(k, 0) + (run_counts[r] if level == 0 else 0)   # whole count: level 0 only
    if memory and run_counts:
        d = depth(next(iter(run_counts)))
        mine |= set(p for p in memory if depth(p) == d and not is_token(p))
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
        def head(a, b):                        # no classes: the plain shared head
            i = 0
            for x, y in zip(a, b):
                if x != y:
                    break
                i += 1
            return a[:i]

    def merged(keys, batch):
        """batch, sorted, put into keys, sorted, where each belongs: the
        new list, and where each of batch landed in it."""
        out, at, i = [], [], 0
        for item in batch:
            j = bisect.bisect_left(keys, item, i)
            out += keys[i:j]
            at.append(len(out))
            out.append(item)
            i = j
        out += keys[i:]
        return out, at

    endings = collections.Counter()            # remainder after a shared head
    beginnings = collections.Counter()         # remainder before a shared tail
    rounds = []
    nodal = level > 0                          # at level 0 a part is its own node
    # The pool in both orders: forward as the parts, mirrored as (mirrored
    # part, part).  What a round mints is merged in where it belongs, and
    # only the pairs with a fresh part are compared: the first round
    # compares every pair; after that, the parts merged in at this pass,
    # and in the mirrored order also the ones the forward pass minted last
    # round (merged in a pass earlier, fresh for one more).
    order = [sorted(mine), sorted((p[::-1], p) for p in mine)]
    pending = [[], []]                         # minted since each order was last merged
    forward_made, carried = [], []             # mirrored entries minted by a forward pass
    r = 0
    while True:
        new = set()
        for mirror in (False, True):
            keys, at = order[mirror], []
            if pending[mirror]:
                pending[mirror].sort()
                keys, at = merged(keys, pending[mirror])
                order[mirror], pending[mirror] = keys, []
            if mirror:
                at += [bisect.bisect_left(keys, e) for e in carried]
                carried, forward_made = forward_made, []
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
                h = head(a2, b2)
                n = len(h)
                if n == 0:
                    continue
                same = h[::-1] if mirror else h
                for whole, flipped in ((a, a2), (b, b2)):
                    if same == whole:
                        continue                       # the whole IS the shared part
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
                            pending[0].append(piece)
                            e = (piece[::-1], piece)
                            pending[1].append(e)
                            if not mirror:
                                forward_made.append(e)
                    if rest:
                        tally[rest] += 1
        rounds.append(len(new))
        if not new:
            break
        if len(pool) > cap:
            rounds.append('stopped: pool passed the cap of %d parts' % cap)
            break
        r += 1
    return mine, produced, endings, beginnings, rounds


# --------------------------------------------------------------------------
# 6. CRYSTAL  -- the interpretation copy (dedup).  The pool is left as it
#                is; the crystal is a second table that reads it.
#
#   change(part -> parent): the remainder that turns the part into the
#       parent.  "+rest" when the part is the head, "rest+" when the tail.
#   class: parts that take the same set of changes belong together.
# --------------------------------------------------------------------------

def depth(x):
    d = 0
    while isinstance(x, tuple):
        d += 1
        x = x[0] if x else 0
    return d


def as_element_of(part, parent):
    """The form of part that matches parent's elements: a level-0 run inside
    a level-1 part is one element of it."""
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
    """The class as a thing that can sit in a sequence one level up.  A
    negative number marks it; the nesting puts it at the right depth."""
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
# 7. LEVELS  -- crystallize, then loop again, until no change
#
# One level is: count the symbols, cut runs at the most common one, mint,
# crystallize.  The next level's symbols are this level's runs, as they
# are -- nothing replaced -- and this level's classes become a second way
# two symbols can be the same.  Every structure a level makes (a run of
# runs, a minted part, a class) joins the one shared pool and adds
# connections to what is already there.  Each level's sequence is shorter
# than the one before (the separator is always present), so the loop ends
# on its own when a level is left with a single run; the additions shrink
# to nothing before that.
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
    mine, produced, endings, beginnings, rounds = mint(run_counts, pool, made_of, part_of, cap,
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
                endings=endings, beginnings=beginnings, rounds=rounds, classes=classes,
                minted=sum(x for x in rounds if isinstance(x, int)),
                added=len(pool) - before, total=len(pool), next_class_of=next_class_of,
                produced=produced, confirmed=confirmed, new=new, unseen=unseen, remembered=remembered)


def run_levels(words, separators, cap, pool=None, made_of=None, part_of=None):
    pool = {} if pool is None else pool
    made_of = collections.defaultdict(set) if made_of is None else made_of
    part_of = collections.defaultdict(set) if part_of is None else part_of
    memory = frozenset(pool)                   # what was remembered before this signal
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


def load_memory(path):
    if not path or not os.path.exists(path):
        return {}, collections.defaultdict(set), collections.defaultdict(set), []
    M = pickle.load(open(path, 'rb'))
    return (M['pool'], collections.defaultdict(set, M['made_of']),
            collections.defaultdict(set, M['part_of']), M['history'])


def save_memory(path, pool, made_of, part_of, history):
    pickle.dump({'pool': pool, 'made_of': dict(made_of), 'part_of': dict(part_of),
                 'history': history}, open(path, 'wb'))


# --------------------------------------------------------------------------
# 8. LENS  -- display only.  The lens never touches the algorithm; it only
#             decides how a word is drawn on the page.
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
    """Draws any part on the page.  A word uses the lens; a level-0 run is
    its words; a higher part is its elements, drawn in turn; a class is
    {level.index}."""

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
        pieces, n = [], -len(sep)              # n: the length of sep.join(pieces)
        for e in x:
            if n > self.wide:                  # display only: past the width nothing more is shown
                break
            s = self.draw(e)
            pieces.append(s)
            n += len(s) + len(sep)
        text = sep.join(pieces)
        return text if len(text) <= self.wide else text[:self.wide] + '...'   # display only

    def change(self, d, x):
        return ('+' + self.draw(x)) if d == '+' else (self.draw(d) + '+')


# --------------------------------------------------------------------------
# 9. RECORD  -- write what was found, in plain text and in JSON
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

    say('MINT   %d rounds; parts minted per round: %s' % (len(L['rounds']), ' '.join(map(str, L['rounds']))))
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
    """A JSON key for any part: level-0 runs as hex words joined by '.',
    deeper parts as their elements' keys joined by ' ' (level 1) or ' | '
    (level 2 and up); a class as {level.index}.  Each part is keyed once;
    keys (a Keys) holds the ones done."""
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
    """part -> JSON key; a part not seen yet is keyed on first use."""

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

    for L in levels:
        say('=' * 78)
        say('LEVEL %d' % L['level'])
        say('=' * 78)
        say('')
        write_level(say, L, G, pool, made_of, part_of, top, frame)

    open(out_txt, 'w').write('\n'.join(T) + '\n')

    keys = Keys(frame)                         # shared by every level
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
    open(out_json, 'wb').write(json.dumps(J, separators=(',', ':')).encode())   # dumps: the C encoder
    return '\n'.join(T)


# --------------------------------------------------------------------------
# 10. RUN  -- the whole thing, top to bottom
# --------------------------------------------------------------------------

def discover(path, lens='raw', limit=None, widest=64, top=25, out=None, quiet=False,
             separators=1, frame=None, cap=1000000, memory=None):
    name = os.path.basename(path)
    forced = frame
    data, bits = read_signal(path, limit)
    frame, profile, score, folding = find_frame(bits, widest, force=frame)
    words = cut_words(bits, frame)
    pool, made_of, part_of, history = load_memory(memory)
    mem = None
    if memory:
        mem = {'path': memory, 'parts_before': len(pool), 'history_before': list(history)}
    if isinstance(separators, str) and not separators.isdigit():
        sep0 = [int(h, 16) for h in separators.split(',')]          # named by hand, in hex
        sep_tag = '.sep' + separators.replace(',', '-')
    else:
        sep0 = int(separators)
        sep_tag = '.sep%d' % sep0 if sep0 > 1 else ''
    levels, pool, made_of, part_of = run_levels(words, sep0, cap, pool, made_of, part_of)
    if memory:
        history.append((name, len(data), frame))
        save_memory(memory, pool, made_of, part_of, history)

    out = out or os.path.dirname(os.path.abspath(path))
    os.makedirs(out, exist_ok=True)
    tag = name + ('.frame%d' % forced if forced else '') + sep_tag + ('.m%d' % len(history) if memory else '')
    out_txt = os.path.join(out, tag + '.record.txt')
    out_json = os.path.join(out, tag + '.record.json')
    text = write_record(out_txt, out_json, name, data, bits, frame, profile, score, folding,
                        levels, pool, made_of, part_of, make_lens(lens, frame), top, mem)
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
    i = 1
    while i < len(argv):
        if argv[i] == '--quiet':
            opts['quiet'] = True
            i += 1
        else:
            opts[argv[i].lstrip('-')] = argv[i + 1]
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
    main(sys.argv[1:])
