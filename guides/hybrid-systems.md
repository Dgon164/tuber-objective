# Hybrid systems: the connection of Discovery to other systems

Discovery reads a signal and writes a record. There is 1 input (a file)
and 1 output (a record). This simple interface makes the connection to
other systems easy. Each system that can write a file can give a signal
to Discovery. Each system that can read JSON can use what Discovery
found.

There are 3 ways to make the connection. The `hybrid/` folder has 1
script that works for each way. All 3 scripts run on
`examples/text/alice.txt`.

## 1. Discovery in front: record -> rules -> another system

Discovery reads the signal first. The second system never sees the raw
signal. The second system works from the record of Discovery. The script
`hybrid/record_to_rules.py` makes a rule table from 3 parts of that
record:

| record table | rule that the script makes | question that the rule answers |
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

The "walk" at the end of the output is a random walk through the
next-run table. The counts give the weights of the walk. The output shows
the walk because the walk is the simplest way to see what the table
holds. The walk is not a language model and does not try to be a
language model.

This pattern works for each system that takes rules, tables, or
features: a rule engine, a planner, a search index, or a classifier. The
record is a set of tables. The second system selects the tables that the
second system wants and how to hold the tables. The `Rules` class in the
script is 40 lines and works as a template.

## 2. A network in front: another system -> bytes -> Discovery

The other system runs first. The output of the other system goes to a
file. Discovery reads that file as a signal. Discovery knows nothing
about the source of the file.

The script `hybrid/net_as_lens.py` makes a reservoir. A reservoir is a
random recurrent network. The network does not change, and nobody trains
the network. This reservoir has 32 units. The bytes of the text drive the
reservoir, 1 byte for each step. After each step, the script writes the
sign of each unit (on or off) as 1 bit.

Then 20,000 steps make a file of 80,000 bytes. Discovery reads the file:

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

The frame step found the width of the state of the network (32) from the
bits alone. The column rates are a readout of the network, unit by unit.
Units 2, 21, and 28 are almost never on. Units 7, 9, and 22 are almost
always on. These 6 units no longer do anything of interest.

The word table shows the states that the network used (1,904 of the 4
billion possible states) and how often. FOLLOWS shows the state that
comes after each state. The result is a map of what the network does. Discovery
made the map and never looked inside the network.

This connection works for each system that can write its state or its
output as bits. Examples:

- the activations of a network that someone trained
- a sensor log
- the state vector of a simulation
- the output of a different program

Discovery writes back a record of the habits of that system.

## 3. The loop: the output as the next input

```
signal -> Discovery -> record -> rules -> output
             ^                              |
             +------------- bytes <---------+
```

The script `hybrid/loop.py` does 3 things in sequence:

1. The script runs the first pattern. The script makes rules from the
   record and writes a random walk of 8,000 runs to a file.
2. The script runs the second pattern. Discovery reads the walk as a new
   signal.
3. The script compares the 2 records in the same way that `bridge.py`
   compares 2 languages.

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

There are 3 bins:

- the parts that both records share
- the parts that the walk lost
- the parts that the walk made but the original pool never had

The "new" parts exist because the walk put different runs next to
each other. Thus the pool in order had different adjacent parts, and the
mint step cut different parts. The program never minted `flamingoes` from
the original text, because nothing next to `flamingoes` shared a start or
an end. In the walk, an adjacent part shared a start or an end.

This collision with 3 bins is how a system checks its own output. The
bins show what came back the same, what the walk lost, and what is new. The script stops
at the report of the bins. What a system does with the bins is the
decision of that system. The comparison uses the same comparator as
everything else in Discovery. The only difference is the input: 2 records
instead of 2 parts.

## Make your own connection

- **To give Discovery a signal from a program**: write bytes to a file.
  Call `discovery.discover(path, quiet=True)`. Read the JSON.
- **To give a program the output of Discovery**: open the JSON. Look at
  `levels[0]` for the signal itself. The entries `levels[1]` and up are
  the levels that the program made on the signal. The tables are `runs`,
  `run_follows`, `parts` (with `whole`, `density`, `made_of`, `part_of`),
  `endings`, `beginnings`, and `classes`.
  - At level 0, the keys are hex bytes with `.` between the bytes. The
    function `glyph()` in `record_to_rules.py` turns a key back into
    text.
  - At higher levels, the keys are symbol numbers. The `symbols` table of
    the level says what each number stands for.
- **To compare 2 records**: see `bridge.py` (2 signals) and `loop.py` (a
  signal and the output of a system from that signal). Both scripts are
  20 lines of set operations on the `parts` keys.

Nothing here needs the other system to be a specific kind of system. The
record is the interface.
