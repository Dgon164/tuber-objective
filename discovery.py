"""
Discovery -- finds the structure of any file with no prior knowledge.
Jason Weeks, thetuberobjective@gmail.com -- github.com/Dgon164/tuber-objective

The program reads a file as a string of bits and compares the bits to
each other, over and over. Each comparison gives three things: what the
two sides share, what is left of each once the shared part is removed,
and what the comparison never touched. The program keeps all three. It
runs the comparison on the raw bits, then on its own results, until a
pass finds nothing new.

The names used in the code, in the order they appear:
    word       one unit of the file, once the program has worked out how wide a unit is
    separator  the most common word; it divides the file the way a space divides text
    run        everything between two separators; a chunk
    pool       the pile of every distinct run and every part found inside them
    mint       to find the part two runs share and add it, and the leftovers, to the pool
    class      a group of parts that all take the same additions (walk, talk, look: +ed, +ing)
    level      one full pass; the next level treats each run as a word and goes again

Input   any file. No format is assumed.
Output  a record, in plain text and JSON, of every repeated part it
        found: what each is made of, what each is inside of, what comes
        before and after it, and what you would add to one part to get
        another.

No dependencies.  Run:  python discovery.py FILE [--lens ascii|utf8|octal]
                        python discovery.py --help   for the other options
From Python:            R = discovery.Root(FILE)   the file as words, the first level
                        of parts, and the pool. discover() is that plus every
                        further level and the written record.
"""

import sys, os, json, collections, heapq, bisect


class Refusal(ValueError):
    """The program can't do what was asked: an option that doesn't exist, a
    memory file from a different word width or an old format. It says why
    and stops, with no traceback."""


# --------------------------------------------------------------------------
# 1. SIGNAL  -- read the file as one long string of bits
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
# 2. FRAME  -- work out how wide one word is
#
# The program doesn't know whether the file is bytes, 15-bit words, or
# 64-bit words. It finds out by trying each width. Lay the bits out in
# rows of that width and look down each column. At the right width, each
# column has its own habit: in ASCII text at width 8, the first column is
# never 1 and the third is almost always 1. At a wrong width every column
# looks about the same. The width whose columns differ the most wins,
# and a wider width only beats a narrower one if it wins by more than
# chance would give with that many rows.
#
# One check after that. A width that is a multiple of the real one (16
# on byte data) shows the same columns twice over. If the winner's
# columns look like a smaller width's columns repeated, the program uses
# the smaller width.
#
# Only the first 64 KB of the file is used for this.
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
    fold = {}                                   # divisor -> the mean difference from the columns of the width that won
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
# 3. WORDS  -- cut the bits into words of that width, count them, and
#              count which word follows which
# --------------------------------------------------------------------------

def cut_words(bits, width):
    return [int(bits[i:i + width], 2) for i in range(0, len(bits) - width + 1, width)]


def count(items):
    return collections.Counter(items)


def follows(items):
    return collections.Counter(zip(items, items[1:]))


# --------------------------------------------------------------------------
# 4. RUNS  -- cut the file into chunks
#
# The most common word is the separator. It divides the file the way a
# space divides text (in a compiled program it's the zero byte). A run
# is everything between two separators.
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
# 5. MINT  -- find the parts that runs share
#
# Sort every distinct run. Two neighbors in sorted order start the same
# way, and that shared start is a part. The program records the shared
# start and the two leftovers as new parts and puts them in the pool, so
# they get compared too. It does the same with every run reversed, to
# catch shared endings. It repeats until a pass finds nothing new. This
# is what "mint" means here. Nothing is ever thrown away.
#
# Two details that keep this fast and correct:
#
# Nothing is removed, so two runs that were neighbors last pass still
# are. The program only compares pairs where at least one side is new
# since the last pass.
#
# Two words count as the same if they're identical, or if they belong to
# the same class (classes come from the level below; there are none at
# level 0). When two words match only by class, the class marker takes
# that slot, so the new part is the pattern the two share with the class
# standing in where they differ.
#
# One pool, one made_of map, and one part_of map are shared by every
# level, so a new part links to whatever it's made of at any level.
#
# Memory: parts from earlier runs, loaded from a file, sit in the same
# sorted pool, so a new run gets compared against what was seen before
# as well as against the rest of this file. A comparison only counts if
# this file is on one side of it. A remembered part that comes out of a
# comparison again is confirmed, and gets one more pass as if it were
# new. The record reports confirmed (seen before and again), added (new),
# and not seen (remembered, but not produced this time).
#
# Cap: on a big file with long runs the pool can grow huge. Past the cap
# the loop stops early and the record says so. This is a memory limit,
# not part of the method; raise it or cut the file.
# --------------------------------------------------------------------------

def node(x):
    """A part that holds exactly one element, at any level above 0, is that
    element: a run of one run is the run. Links go to the element itself."""
    return x[0] if isinstance(x, tuple) and len(x) == 1 and isinstance(x[0], tuple) else x


def mint(run_counts, pool, made_of, part_of, cap=1000000, class_of=None, level=0, memory=()):
    mine = set(run_counts)                     # this level's parts, in this level's form
    produced = set(node(r) for r in run_counts)
    for r in run_counts:
        k = node(r)
        pool[k] = pool.get(k, 0) + (run_counts[r] if level == 0 else 0)   # whole-run counts only matter at level 0
    remembered_only = set()                    # parts from memory at this depth that this file did not produce
    reached = set(run_counts)                  # every part this file has produced or run so far
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
        def head(a, b):                        # no classes: just the shared start
            i = 0
            for x, y in zip(a, b):
                if x != y:
                    break
                i += 1
            return a[:i]

    def merged(keys, batch):
        """Put a sorted batch into a sorted list where each item belongs.
        Returns the new list and where each batch item landed."""
        out, at, i = [], [], 0
        for item in batch:
            j = bisect.bisect_left(keys, item, i)
            out += keys[i:j]
            at.append(len(out))
            out.append(item)
            i = j
        out += keys[i:]
        return out, at

    endings = collections.Counter()            # what was left after a shared start
    beginnings = collections.Counter()         # what was left before a shared ending
    rounds = []
    reached_again = []                         # per pass: remembered parts this file produced again
    nodal = level > 0                          # at level 0 a part is its own node
    # The pool in both orders: forward as the parts, and reversed, to catch
    # shared endings. New parts are merged in where they belong. The first
    # pass compares every pair; after that, only pairs with a part that is
    # new since the last pass (and in the reversed order, also the parts
    # the forward pass just made, which are new for one more pass).
    order = [sorted(mine), sorted((p[::-1], p) for p in mine)]
    pending = [[], []]                         # minted since each order was last merged
    forward_made, carried = [], []             # reversed copies of what the forward pass just made
    touched = []                               # remembered parts this file produced again last pass: treated as new once more
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
                    continue                   # both remembered, neither reached by this file: already compared when they were made
                h = head(a2, b2)
                n = len(h)
                if n == 0:
                    continue
                same = h[::-1] if mirror else h
                for whole, flipped in ((a, a2), (b, b2)):
                    if same == whole:
                        continue                       # the whole run is the shared part; nothing left over
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
                            reached.add(piece)         # this file produced a remembered part again: confirmed, and new for the next pass
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
# 6. CRYSTAL  -- group parts by what you can add to them
#
# For each part, look at everything it's inside of and note what was
# added to get there: "+ed" if the part is the start, "un+" if it's the
# end. Parts that take the same set of additions go in one class. That's
# how 22 verb stems end up together: they all take +ed and +ing. The pool
# isn't changed. This is a second table that reads it.
# --------------------------------------------------------------------------

def depth(x):
    d = 0
    while isinstance(x, tuple):
        d += 1
        x = x[0] if x else 0
    return d


def as_element_of(part, parent):
    """The form of a part that matches the elements of a parent one level
    up: a level-0 run inside a level-1 part is one element of it."""
    return (part,) if depth(parent) == depth(part) + 1 else part


def changes_of(part, part_of):
    out = set()
    k = node(part)
    d = depth(k)
    for parent in part_of.get(k, ()):
        p = (k,) if depth(parent) == d + 1 else k   # as_element_of, with the depth of the part found 1 time
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
    """A class, written so it can sit in a sequence one level up. A
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
# 7. LEVELS  -- do it all again one level up, until nothing is left
#
# One level is: count the words, cut at the most common one, find the
# shared parts, group them. The next level's words are this level's
# runs, unchanged, and this level's classes become a second way two
# words can count as the same. Everything each level finds goes into
# the one shared pool. Each level's sequence is shorter than the last,
# because the separator is always present, so the loop ends on its own
# when a level is down to a single run. In practice the additions dry
# up before that.
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
    memory = frozenset(pool)                   # what was remembered before this file
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
# 7b. TIME  -- read the sequence as before-and-after
#
# The file is in order, and the order is time. FOLLOWS already holds
# what comes right after what. Three more readings of the same sequence:
#
#   arrows    a pair seen in both orders. The order that wins is the
#             arrow; how much it wins by is its strength.
#   effects   what shows up after a part more often than it shows up in
#             general. The stretch looked at is the typical distance to
#             the next level's separator, so the unit comes from the file.
#   chains    the strongest effect, followed forward: a -> b -> c.
#
# On a file that was only observed, this gives before and after. When
# the program can also act (examples/agc-live: press a key, record,
# compare), the effect that's only there after the press is what the
# press caused.
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
            if c >= 2 and c >= 2 * expected:          # seen at least twice, at twice the usual rate: two make a pattern, same as the classes
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
    """A part as JSON wrote it (nested lists), back to the tuples the pool uses."""
    return tuple(tuples(e) for e in x) if isinstance(x, list) else x


def load_memory(path):
    """Read a memory file. It's JSON: the pool as [part, count] pairs,
    part_of as [part, [what it's inside of]] pairs (made_of is rebuilt from
    that), and a history of the files read. Any program can read it, and
    reading it runs nothing."""
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
# 8. LENS  -- display only. The lens decides how a word is drawn on the
#             page: as a character, a hex number, an octal number. It
#             never touches the method.
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
    """Draws any part on the page. A word uses the lens; a level-0 run is
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
            if n > self.wide:                  # display only: nothing shown past the width
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

    T = L.get('time')
    if T:
        short = lambda x: (lambda s: s if len(s) <= 24 else s[:24] + '...')(draw(x))   # display only
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
    """A JSON key for any part: a level-0 run as its hex words joined by
    '.', a deeper part as its elements' keys joined by ' ' (level 1) or
    ' | ' (level 2 and up), a class as {level.index}. Each part is keyed
    once; keys (a Keys) holds the ones done."""
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
    """part -> JSON key. A part not seen yet is keyed on first use."""

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
    open(out_json, 'wb').write(json.dumps(J, separators=(',', ':')).encode())   # compact JSON
    return '\n'.join(T)


# --------------------------------------------------------------------------
# 10. RUN  -- the whole thing, top to bottom
#
# Root is the one call a program built on Discovery makes. It reads the
# file, finds the word width, cuts the words, and runs the first level
# on a shared pool, and it has a call for each further level. discover()
# is Root plus every level to the end plus the written record. Every
# script in extend/ and hybrid/ is Root plus one new thing.
# --------------------------------------------------------------------------

class Root:
    """The file, as Discovery reads it.

        R = Root(path)                 read, find the width, cut the words, run level 0
        R.words, R.frame               the file as words of R.frame bits
        R.L0                           level 0: runs, run_counts, run_follows, parts,
                                       endings, beginnings, classes, next_class_of
        R.pool, R.made_of, R.part_of   the shared pool and its links
        R.level(seq, separators, class_of)   one more level on the same pool
        R.all_levels()                 level after level until one run is left, as discover() does
        R.draw(x)                      a part as text, through the lens

    separators: 1 for the most common word, N for the N most common, or a
    list of words. same: a map from a word to what stands in for it when
    two words count as the same (the band in extend/same_within.py).
    pool, made_of, part_of, history: a memory to start from, as
    load_memory gives it. A memory holds files read at one word width,
    because a word is a number and the same number means different things
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
        self.memory = frozenset(self.pool)       # what was remembered before this file
        self.earlier = set()                     # what earlier levels of this run produced
        self.cap = cap
        self.levels = []
        self.glyphs = Glyphs(make_lens(lens, self.frame))
        self.L0 = self.level(self.words, separators, same)

    def level(self, seq, separators=1, class_of=None):
        """One more level on the shared pool: cut, find shared parts, group."""
        L = run_level(seq, separators, self.pool, self.made_of, self.part_of, self.cap,
                      class_of, len(self.levels), self.memory, self.earlier)
        self.levels.append(L)
        self.earlier |= L['produced']
        return L

    def all_levels(self):
        """Level after level, each on the runs of the one before with its
        classes as a way to be the same, until a level is left with one run."""
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
        # separators named by hand, in hex: 20,0a  or  0x20  or  20,  (digits alone are a count: --separators 2)
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
