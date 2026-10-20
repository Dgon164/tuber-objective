# Hybrid systems: connecting Discovery to other systems

Discovery reads a file and writes a record. The record lists every part
the program found and how the parts relate to each other, in plain text
and in JSON. So there's one input (a file) and one output (a record), and
that simple shape makes connecting Discovery to other systems easy. Any
system that can write a file can hand Discovery something to read. Any
system that can read JSON can use what Discovery found.

There are three ways to make the connection. The `hybrid/` folder has
one script for each. All three scripts run on `examples/text/alice.txt`.

## 1. Discovery in front: record -> rules -> another system

In this arrangement Discovery reads the raw file first, and the other
system never sees the raw file at all. It works from Discovery's record.
The other system can be anything that takes rules, tables, or features.
What you get out is a rule table.

The script `hybrid/record_to_rules.py` builds that table from three
parts of the record. (The record calls a chunk of the file between two
dividers a run.)

| record table | rule the script makes from it | question the rule answers |
|---|---|---|
| RUN FOLLOWS (which chunk came after which) | next-run rules | what comes after X? |
| PARTS (part_of: which parts sit inside which) | forms-of rules | what forms does X take? |
| CLASSES (groups of parts that take the same changes) | same-kind rules | what else takes the same changes as X? |

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

The "walk" at the end of the output is a random walk through the
next-run table: start at one chunk, pick one of the chunks that followed
it at random, with the ones that followed it more often more likely to
be picked, and repeat. The counts in the table are what set those odds.
The script shows the walk because it's the simplest way to see what the
table holds. It is not a language model and doesn't try to be one.

This arrangement works for any system that takes rules, tables, or
features: a rule engine, a planner, a search index, or a classifier. The
record is a set of tables. The other system picks the tables it wants
and decides how to hold them. The `Rules` class in the script is 40
lines and works as a template.

## 2. A network in front: another system -> bytes -> Discovery

In this arrangement the other system runs first. Its output goes to a
file, and Discovery reads that file as it would read any other. Discovery
knows nothing about where the file came from. What you get out is a
record of what the other system does.

The other system in the script `hybrid/net_as_lens.py` is a reservoir: a
small network of 32 units whose connections are set at random and never
change. Nobody trains it. The script feeds the bytes of the text through
the reservoir, one byte per step. After each step, it writes down whether
each unit's value is positive or negative (on or off), as one bit per
unit.

Then 20,000 steps make a file of 80,000 bytes, and Discovery reads it:

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

The frame step, the part of the program that works out how wide one
unit is, found the width of the network's state (32) from the bits
alone. The column rates, how often each bit position is 1, are a readout
of the network unit by unit. Units 2, 21, and 28 are almost never on.
Units 7, 9, and 22 are almost always on. Those six units no longer do
anything of interest.

The word table shows which states the network actually used (1,904 of
the 4 billion possible) and how often. The FOLLOWS table shows which
state comes after which. Put together, that's a map of what the network
does. Discovery made the map without ever looking inside the network.

This arrangement works for any system that can write its state or its
output as bits. For example:

- the activations of a network someone trained
- a sensor log
- the state vector of a simulation
- the output of a different program

Discovery writes back a record of that system's habits.

## 3. The loop: the output as the next input

```
signal -> Discovery -> record -> rules -> output
             ^                              |
             +------------- bytes <---------+
```

In this arrangement the other system is Discovery's own output, fed back
in. The script `hybrid/loop.py` does three things in sequence:

1. It runs the first arrangement: builds rules from the record and
   writes a random walk of 8,000 chunks to a file.
2. It runs the second arrangement: Discovery reads the walk as a new
   file.
3. It compares the two records, the same way `bridge.py` compares two
   languages.

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

What you get is three bins:

- the parts both records share
- the parts the walk lost
- the parts the walk made that the original pool never had

The "new" parts exist because the walk put different chunks next to each
other. When Discovery sorted that pool, different parts ended up as
neighbours, and the step that splits neighbours into shared starts and
leftovers cut different parts. The program never made `flamingoes` from
the original text, because nothing next to `flamingoes` shared a start
or an end with it. In the walk, a neighbour did.

This three-bin comparison is how a system checks its own output. The
bins show what came back the same, what the walk lost, and what's new.
The script stops at reporting the bins. What a system does with them is
up to that system. The comparison is the same one Discovery uses for
everything else. The only difference is the input: two records instead
of two parts.

## Make your own connection

- **To hand Discovery a file from a program**: write bytes to a file.
  Call `discovery.discover(path, quiet=True)`. Read the JSON.
- **To hand a program Discovery's output**: open the JSON. `levels[0]`
  is the file itself. `levels[1]` and up are the levels the program
  built on top of it, where each chunk from the level below is treated
  as one unit. The tables are `runs`, `run_follows`, `parts` (with
  `whole`, `density`, `made_of`, `part_of`), `endings`, `beginnings`,
  and `classes`.
  - At level 0, the keys are hex bytes with `.` between them. The
    function `glyph()` in `record_to_rules.py` turns a key back into
    text.
  - At higher levels, the keys are symbol numbers. The level's `symbols`
    table says what each number stands for.
- **To compare two records**: see `bridge.py` (two files) and `loop.py`
  (a file and what a system made from it). Both scripts are 20 lines of
  set operations on the `parts` keys.

Nothing here needs the other system to be any particular kind of system.
The record is the interface.
