# Hybrid systems: connecting Discovery to other things

Discovery reads a signal and writes a record. It has one input (a file)
and one output (a record). That simple interface is what makes it easy
to connect to other systems: anything that can write a file can feed
it, and anything that can read JSON can use what it found.

There are three ways to wire it. The `hybrid/` folder has one working
script for each, all run on `examples/text/alice.txt`.

## 1. Discovery in front: record → rules → another system

Discovery reads the signal. The second system never sees the signal —
it works from the record. `hybrid/record_to_rules.py` builds a rule
table out of three parts of the record:

| record table | rule it makes | question it answers |
|---|---|---|
| RUN FOLLOWS | next-run rules | what comes after X? |
| PARTS (part_of) | forms-of rules | what forms does X take? |
| CLASSES | same-kind rules | what else takes the same changes as X? |

```
python record_to_rules.py ../examples/text/alice.txt.record.json

  next-run rules : 17450
  forms-of rules : 22446
  same-kind rules: 12241 parts in 11693 classes

what follows said   -> the 197, Alice, 35, to 32, Alice 25, Alice; 9
what follows the    -> Mock 47, March 25, King 22, Queen 20, White 17

forms of walk   -> walked, walking, walk!", walking\na
forms of look   -> looked, looking, look-out, look\nof, (look, ...

same kind as swallow   [+ed, +ing] -> swallow, remain, consider, crawl, fann, mutter, nibbl, peep, produc, pull

walk from "Alice":
  Alice felt dreadfully one of gloves and as she turned away.\n\n'Come back!' the Queen. ...
```

The "walk" at the bottom is a random walk through the next-run table,
weighted by the counts. It's shown because it's the simplest way to see
what the table holds. It's not a language model and isn't meant to be.

This same pattern works for any system that takes rules, tables, or
features: a rule engine, a planner, a search index, a classifier. The
record is a set of tables; the second system picks which tables it
wants and how to hold them. The `Rules` class in the script is forty
lines and works as a template.

## 2. A net in front: another system → bytes → Discovery

The other system runs first and its output gets written to a file.
Discovery reads that file as a signal, knowing nothing about what
produced it.

`hybrid/net_as_lens.py` builds a reservoir: a fixed random recurrent
net with 32 units, never trained. It gets driven by the bytes of the
text, one byte per step. After every step, the sign of each unit (on or
off) gets written out as one bit. 20,000 steps make an 80,000-byte
file. Discovery reads it:

```
  picked width 32
  chosen width 32
  column rates at width 32:
    0.588 0.593 0.003 0.024 0.487 0.084 0.962 0.985 0.329 0.983 0.103 0.901
    0.321 0.650 0.082 0.343 0.794 0.225 0.813 0.116 0.618 0.002 0.967 0.939
    0.791 0.682 0.101 0.171 0.001 0.909 0.348 0.019

WORDS   20000 words, 1904 distinct
  0b502bc6   331
  0bd0a3c6   314
  c35dab94   309
```

The frame step found the width of the net's state (32) from the bits
alone. The column rates are a unit-by-unit reading of the net: units 2,
21, and 28 are almost never on; units 7, 9, and 22 are almost always
on. Those are units that stopped moving. The word table is the list of
states the net actually used (1,904 out of the 4 billion it could
have) and how often. FOLLOWS shows which state leads to which. That's a
map of what the net does, made without looking inside the net.

This same wiring works for any system whose state or output can be
written as bits: a trained net's activations, a sensor log, a
simulation's state vector, the output of another program. What
Discovery writes back is a record of that system's habits.

## 3. The loop: output goes back in

```
signal -> Discovery -> record -> rules -> output
             ^                              |
             +------------- bytes <---------+
```

`hybrid/loop.py` runs the first pattern (rules from the record, then a
random walk of 8,000 runs written to a file), then the second
(Discovery reads the walk as a new signal), then smashes the two
records together the way `bridge.py` smashes two languages:

```
COLLIDE   first record 22446 parts, second 10468 parts
  shared 8543   lost 13903   new 1925

  most common lost parts (in the text, not in the walk):
    *          seen 51
    both       seen 13
    walked     seen 10
  most common new parts (in the walk, not in the text):
    nsider,    made of ,, nside, sider,, n
    Sentence   made of Se, ntence, S, entence
    flamingoes made of mingoes, f, fla, lamingoes
```

Three bins: the parts both records have, the parts the walk lost, and
the parts the walk produced that the original pool never had. The "new"
parts exist because the walk put different runs next to each other, so
the sorted pool had different neighbours and the mint cut different
pieces. `flamingoes` was never minted from the original text because
nothing sat next to it that shared a beginning or ending; in the walk,
something did.

That three-bin collision is how a system checks its own output: what
came back the same, what was lost along the way, what's new. The script
stops at reporting the bins. What a system does with them is its own
business. The point is that the comparison uses the same comparator as
everything else in Discovery, applied to two records instead of two
parts.

## Wiring it yourself

- **To feed Discovery from a program**: write bytes to a file; call
  `discovery.discover(path, quiet=True)`; read the JSON.
- **To feed a program from Discovery**: open the JSON and look at
  `levels[0]` for the signal itself (`levels[1]` and up are the levels
  built on it). `runs`, `run_follows`, `parts` (with `whole`, `density`,
  `made_of`, `part_of`), `endings`, `beginnings`, and `classes` are the
  tables. At level 0 the keys are hex bytes joined by `.`; `glyph()` in
  `record_to_rules.py` turns a key back into text. At higher levels the
  keys are symbol numbers and the level's `symbols` table says what each
  stands for.
- **To compare two records**: `bridge.py` (two signals) and `loop.py`
  (a signal and a system's output from it) are both twenty lines of set
  operations on the `parts` keys.

Nothing here requires the other system to be any particular kind. The
record is the handshake.
