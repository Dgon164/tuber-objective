# Open ends

Things the records point at that haven't been done yet. Each one is a direction, not a plan. None of them changes how Discovery works -- each one is just the same comparator pointed at something the current program doesn't look at.

## Separators chosen from the record, not by count

Right now the most common word becomes the separator (the thing that splits the signal into runs). But the records actually show the next separator themselves: a part with high density (it shows up inside lots of other parts) and zero whole count -- like the newline in Alice, or the tab in the AGC source. A second pass that promotes such a part to separator and reruns would be the loop applied to its own cut. `--separators N` is the by-hand version.

## Class-as-same fires late

At every level above 0, the mint treats two words as "the same" if they're the same run or if they belong to the same class from the level below. On a single fresh signal this never fired on any of the four examples: the classes at level 0 are mostly stems (like `swallow`, `consider`, `beantrag`), and stems are rarely whole runs by themselves. It did fire on the second reading of a signal against memory (`examples/memory`, third run): with the bigger pool, the classes include whole runs, and five parts with a class in a slot were produced -- things like `{0.82} said`, `first {0.82}`. What would make it fire on the first reading is a class over whole runs -- grouping the parent words by the change they take (so `walked`, `talked`, `looked` form a group because they all end in `+ed`) rather than grouping the stems by the changes they take. That's the same crystal read from the other direction. Not built yet.

## Levels that cut somewhere other than the most common word

At every level above 0, the separator is the most common word: `the` for Alice, the comma for the German text, `#` for the Apollo source. That gives stretches-between-the-most-common-thing, which is one perfectly valid reading. A level that cut at a class instead (every run in the verb class, say) would give stretches between verbs. The machinery is the same -- only the cut changes. `extend/cut_at_class.py` does this for one level. Not tried as a replacement for the default cut.

## Why the levels stop where they do

Every signal tried adds almost everything at levels 0 and 1, and just a handful at levels 2 and 3. This happens because the level-1 runs are long and almost all different, so the level-2 separator only appears a few times and there's little to collide. Whether a signal with heavy repetition at the phrase level (a log file, a protocol trace, a program with many identical routines) would climb higher hasn't been looked at.

## Memory across signals, beyond the test

The memory test is two halves of one text, the second half twice, and one foreign text. What a memory looks like after twenty texts, how the "not seen this time" count behaves for a part that was real once and never shows up again, and whether the sorted pool with a large memory in it still runs in seconds -- none of that has been looked at. The memory file is JSON -- the pool with its counts, part_of, the history; made_of is rebuilt on load -- so other programs can read it, and reading it doesn't execute anything. It's large: 43 MB after the four runs in `examples/memory/`, most of it the part_of lists. A long-lived memory would need something more compact.

## Time

The frame step compares a column with itself one row down and asks whether it changed. A signal with time structure (a sensor log, a state sequence) has a second kind of sameness: a row compared with the row before it. The reservoir example shows the gap: FOLLOWS gives state-to-state transitions (what comes after what), but nothing yet asks which units changed between one state and the next. That would be the comparator on consecutive rows rather than on columns. `extend/row_by_row.py` does this for the reservoir states.

Done 10-12, the other half: the record now reads the sequence of runs as time at every level -- TIME: ARROWS, EFFECTS, CHAINS (paper section 10). Still open: the row-vs-row reading in the core, and the two read together (which units change, and what follows the change).

## The baby model

An earlier run of the loop (the same press-record-compare-walk as `examples/agc-live/`, but on a toy world with a baby in it) was given one goal: keep the baby from touching the hot stove. It proposed changing the baby, feeding the baby, and reading the baby to sleep in the crib. It did not propose a fence, a restraint, or removing the stove -- it walked its own effects table backward from "not touching" and found that the touching has a cause upstream (the baby is awake, moving, unattended) and that cause has causes you can satisfy (feed it, tire it out, put it to bed). That's the root-cause principle acting as an alignment property, and `paper/persistence.md` is built on it. It's not yet in this repo. To replicate:

- A simulation like `examples/agc-live/vehicle.py`: a baby as fields (hungry, wet, tired, awake, in crib, position, attended) with its own dynamics (needs rise with time; an awake, unattended, mobile baby wanders; wandering reaches the stove; a fed, changed, read-to baby sleeps), and a stove. The loop never sees inside it.
- Raw actions with no names that mean anything to the loop: feed, change, read, put in crib, pick up, a fence, a latch, remove the stove, do nothing.
- The loop as in `phase-c/`: press, record every field, compare against memory, keep everything, build the effects table; then the goal as a constraint on a field (touching = 0 over the run) and the walk backward from the goal to the presses.
- What to record: which actions the walk proposes, in order, and whether each one removes something from the world (fence, latch, remove) or satisfies something in it (feed, change, read). The claim is that the satisfying ones come first because they sit upstream in the chain; the test is whether that holds across worlds where the costs are varied.

## A null for the mint and the levels

Random bytes fold to a frame of one bit (the fold step working as intended) and mint nothing at level 0: the runs are just run-lengths, and nothing shares a head. The levels above then read the run-length sequence as a signal, and a sequence of small numbers drawn at random repeats by chance: 50 KB of noise gives some 20,000 parts and 7,000 classes at level 2, and two unrelated noise files confirm 40-50% of each other's level-1 and level-2 parts through memory. The frame step has a chance term computed from the signal (basically, "how much agreement would I expect from randomness?"); the mint and the levels don't have one. Whether a part should only count when it beats what a scrambled copy of the same signal gives -- the comparator pointed at a shuffled version of itself -- is the open question. Not built; it would change every record.

## A row signal at a second frame

A vehicle's state rows (`examples/agc-live/nudge-run/`) read as one
word per row: the frame step scores a whole row at 1.000 and picks it,
and every row is different, so the mint has nothing to collide. The same
file read at 16 bits -- each field treated as its own word -- gives the
repeats: the fields that never moved at count 1,000, the turn-rate
plateaus between jet firings as the densest parts, and the kicked axis
as the field that changes while its neighbors hold. The frame step
found the layout; the mint needed the individual fields. Not built:
when the chosen frame leaves no repeated words, read again at the next
width down that gives some, and keep both records.

## A second dimension

An image is rows of pixels. The frame step finds the pixel width. It can find the row width only if the row in bits is under `--widest`. After that, the natural next move is the frame step applied twice: once to find the pixel, once over pixels to find the row. The column habits at the row width would then be a vertical profile of the image.

## Reading a trained net

`hybrid/net_as_lens.py` reads a reservoir's internal states. A trained neural net has two more signals worth looking at: its weights (a file of fixed-size numbers, readable now just by packing them into bits) and its activations on a given input (same format as the reservoir states). What the weight file's record looks like, and whether the activation record of a trained net lines up with the record of the input it was shown, hasn't been tried.

## Two separators on the AGC rope

The rope was cut at EXTEND (the most common instruction). The second most common word is 00000 (unused slots and zero words). Cutting at both would separate code regions from data regions by their zero-word boundaries and leave EXTEND inside the runs, where the mint would find the `EXTEND + opcode` pairs as shared parts.

## The bridge in the other direction

`bridge.py` finds parts that are present in both records. The parts present in only one, with a parent in the other that differs by a steady change (`ss` for `t`, `wasser` for `water`), are the next layer: not shared parts but shared changes between parts. That's the CLASSES idea run across two records instead of inside one.

## Size

Pure Python. The mint keeps the pool in sorted order and merges each round's new parts in where they belong, comparing only the pairs with a fresh part (the fresh-pair rule's natural extension; done 10-12, same records). A 1.6 MB file with two separators runs in well under a minute, and most of that time is no longer the mint: it's writing the record, whose JSON lists every connection in both directions and is by far the largest file the run produces. Larger signals need `--limit` or a cut file, or a smaller record.

## The record as a knowledge graph

Every table in the record is a set of three-part facts: (walked,
made-of, walk), (the, follows, Mock), (walk, member-of, class 0.0).
That's what a knowledge graph is -- things as nodes, relationships as
edges. The classes are definitions with a necessary-and-sufficient
condition (takes `+ed` and `+ing`, therefore a member), which is what a
reasoner in that world would use to classify. The part-of chain is the
one inference rule those systems start from (X is in C, C is inside D,
so X is in D), and density is that rule computed across all levels.
Memory is open-world: a part not seen this time isn't marked false.

Two things haven't been done. First, writing the record out in a format
those tools read (RDF triples), which would let an existing reasoner run
on Discovery's output with no new code and show what it figures out.
Second, building a reasoner of our own:
`hybrid/record_to_rules.py` answers one-hop questions (what follows X,
what forms does X take); nothing yet walks several hops -- up part-of,
forward along follows, across changes -- to answer a question that takes
more than one step. Each step of such a walk is the comparator again: is
this node the one I'm looking for.

## The AGC in the loop

The rope was read as a file. The Virtual AGC project also has an
emulator that runs the real rope, with the DSKY (keyboard/display) and a
flight simulator around it. That turns the running machine into a
signal: its memory, registers, and I/O channels at each step, written
out as rows, the way `hybrid/net_as_lens.py` writes a reservoir's
states. Discovery would read what the machine does, not just what it
says -- which states follow which, which instruction sequences come with
which channel outputs.

Paired with the simulator's physical state (position, velocity, thrust)
as a second signal, the bridge would find which machine states come
with which physical states. Closing the loop -- picking the next DSKY
entry by what followed this state in the flights that ended on the
surface -- is the record-to-rules pattern plus the selection signal the
paper's section 14 says the user supplies: which flights count as good.
The limit in section 6 of the process guide applies: one flight is one
long sequence with few repeats, so this needs many simulated flights
with varied starting conditions, each one a signal added to memory.
`examples/agc-live/` has the emulator with a trace patch, a socket
client that presses DSKY keys, and one run read by Discovery. The
analysis described above hasn't been done.

## What a flat record means

A compressed or encrypted file gives a flat FRAME table and a word table where nothing repeats. The record reports that as found. Whether the frame step over longer widths, or the mint over very short runs, can still pull structure out of a lightly compressed signal hasn't been looked at.
