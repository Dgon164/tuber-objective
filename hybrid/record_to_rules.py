"""
record_to_rules.py -- Discovery in front of another system.

Discovery reads the signal and writes a record.  A second system never
sees the signal; it works from the record.  Here the second system is a
small rule table built from three parts of the record:

    FOLLOWS    run A is followed by run B, n times      -> next-run rules
    PARTS      part P sits inside parents Q1, Q2 ...    -> forms-of rules
    CLASSES    parts that take the same set of changes  -> same-kind rules

    python record_to_rules.py ../examples/text/alice.txt.record.json

It then answers three questions from the rules, and walks the next-run
table to produce a sequence.  The walk is a walk through a table; it is
shown because it is the plainest way to see what the table holds.
"""

import sys, json, random


def glyph(key):
    raw = bytes(int(h, 16) for h in key.split('.'))
    try:
        return raw.decode('utf8').replace('\n', '\\n')
    except UnicodeDecodeError:
        return ''.join(chr(b) if 32 <= b < 127 else '\\x%02x' % b for b in raw)


def key_of(text):
    return '.'.join('%02x' % b for b in text.encode('utf8'))


class Rules:
    def __init__(self, record):
        self.rec = record
        record = record['levels'][0]            # level 0: the signal's own runs and parts
        self.next = {}                          # run -> {run: count}
        for a, b, n in record['run_follows']:
            self.next.setdefault(a, {})[b] = n
        self.parts = record['parts']
        self.kind = {}                          # part -> class label
        for c in record['classes']:
            label = ', '.join(('+' + glyph(ch[1:])) if ch.startswith('+') else (glyph(ch[:-1]) + '+')
                              for ch in c['changes'])
            for m in c['members']:
                self.kind[m] = label

    def what_follows(self, run, top=5):
        table = self.next.get(key_of(run), {})
        return sorted(table.items(), key=lambda kv: -kv[1])[:top]

    def forms_of(self, part, top=8):
        p = self.parts.get(key_of(part))
        if not p:
            return []
        same_level = [q for q in p['part_of'] if q in self.parts]       # a form of a word is a word
        return sorted(same_level, key=lambda q: -self.parts[q]['whole'])[:top]

    def same_kind_as(self, part):
        label = self.kind.get(key_of(part))
        if label is None:
            return None, []
        members = [m for m, l in self.kind.items() if l == label]
        return label, members

    def walk(self, start, steps=20, seed=1):
        rng = random.Random(seed)
        here, out = key_of(start), [start]
        for _ in range(steps):
            table = self.next.get(here)
            if not table:
                break
            runs, counts = zip(*table.items())
            here = rng.choices(runs, weights=counts)[0]
            out.append(glyph(here))
        return out


def main(path):
    rules = Rules(json.load(open(path)))
    print('RULES built from %s' % path)
    print('  next-run rules : %d' % sum(len(t) for t in rules.next.values()))
    print('  forms-of rules : %d' % len(rules.parts))
    print('  same-kind rules: %d parts in %d classes' % (len(rules.kind), len(set(rules.kind.values()))))
    print()
    for run in ('said', 'the', 'Alice'):
        print('what follows %-6s -> %s' % (run, ', '.join('%s %d' % (glyph(k), n) for k, n in rules.what_follows(run))))
    print()
    for part in ('walk', 'look', 'think'):
        print('forms of %-6s -> %s' % (part, ', '.join(glyph(q) for q in rules.forms_of(part))))
    print()
    for part in ('swallow', 'consider'):
        label, members = rules.same_kind_as(part)
        print('same kind as %-9s [%s] -> %s' % (part, label, ', '.join(glyph(m) for m in members[:10])))
    print()
    print('walk from "Alice":')
    print('  ' + ' '.join(rules.walk('Alice', steps=24)))


if __name__ == '__main__':
    main(sys.argv[1])
