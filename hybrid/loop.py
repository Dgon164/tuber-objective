"""
loop.py -- the tick: a second system's output goes back through Discovery.

    signal -> Discovery -> record -> rules -> output
                 ^                              |
                 +------------- bits <----------+

1. Discovery has already read a text and written a record.
2. The rule table from record_to_rules.py walks the next-run table and
   writes out a new text.
3. Discovery reads that new text as a fresh signal and writes a second
   record.
4. The two records are collided (same / different / not part):
       shared   parts in both records
       lost     parts in the first record only
       new      parts in the second record only

    python loop.py ../examples/text/alice.txt.record.json

Writes  loop.output.txt       the walked text
        loop.output.txt.record.txt / .json
"""

import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import discovery
from record_to_rules import Rules, glyph

RUNS_OUT = 8000


def main(record_path):
    first = json.load(open(record_path))
    rules = Rules(first)
    walk = rules.walk('Alice', steps=RUNS_OUT, seed=3)
    text = ' '.join(walk).replace('\\n', '\n')
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'loop.output.txt')
    open(out_path, 'w').write(text)
    print('walked %d runs into %s' % (len(walk), os.path.basename(out_path)))

    discovery.discover(out_path, lens='ascii', quiet=True)
    second = json.load(open(out_path + '.record.json'))

    A, B = first['levels'][0]['parts'], second['levels'][0]['parts']
    shared = [k for k in A if k in B]
    lost = [k for k in A if k not in B]
    new = [k for k in B if k not in A]
    print()
    print('COLLIDE   first record %d parts, second %d parts' % (len(A), len(B)))
    print('  shared %d   lost %d   new %d' % (len(shared), len(lost), len(new)))
    print()
    print('  most common lost parts (in the text, not in the walk):')
    for k in sorted(lost, key=lambda k: -A[k]['whole'])[:15]:
        print('    %-20s seen %d' % (glyph(k), A[k]['whole']))
    print()
    print('  most common new parts (in the walk, not in the text):')
    for k in sorted(new, key=lambda k: -B[k]['whole'])[:15]:
        print('    %-20s seen %d   made of %s' % (glyph(k), B[k]['whole'],
                                                  ', '.join(glyph(q) for q in B[k]['made_of'] if q in B)[:60]))
    print()
    print('  classes in first: %d   in second: %d' % (len(first['levels'][0]['classes']), len(second['levels'][0]['classes'])))


if __name__ == '__main__':
    main(sys.argv[1])
