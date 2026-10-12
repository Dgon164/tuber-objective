# Open ends

Things the records point at that have not been done. Each is a direction, not a plan. None of them changes the mechanism — each is the same comparator pointed at something the current program does not look at.

## Separators chosen from the record, not by count

Right now the most common word is the separator. But the records show the next separator themselves: a part with high density and zero whole count (the newline in Alice, the tab in the AGC source). A second pass that promotes such a part to separator and reruns would be the loop applied to its own cut. `--separators N` is the by-hand version.

## Class-as-same fires late

At every level above 0, the mint treats two words as "the same" if they are the same run or if they belong to the same class from the level below. On a single fresh signal this did not fire on any of the four examples: the classes at level 0 are mostly stems (`swallow`, `consider`, `beantrag`), and stems are rarely whole runs. It did fire on the second reading of a signal against memory (`examples/memory`, third run): with the bigger pool, the classes include whole runs, and five parts with a class in a slot were produced — `{0.82} said`, `first {0.82}`. What would make it fire on the first reading is a class over whole runs — the parents grouped by the change they take (`walked`, `talked`, `looked` as `stem + ed`) rather than the stems grouped by the changes they take. That is the same crystal read from the other direction. Not built.

## Levels that cut somewhere other than the most common word

At every level above 0, the separator is the most common word: `the` for Alice, the comma for the German text, `#` for the Apollo source. That gives stretches-between-the-most-common-thing, which is one true reading. A level that cut at a class instead (every run in the verb class, say) would give stretches between verbs. The machinery is the same — only the cut changes. `extend/cut_at_class.py` does this for one level. Not tried as a replacement for the default cut.

## Why the levels stop where they do

Every signal tried adds almost everything at levels 0 and 1, and just a handful at levels 2 and 3. This is because the level-1 runs are long and almost all different, so the level-2 separator only appears a few times and there is little to collide. Whether a signal with heavy repetition at the phrase level (a log file, a protocol trace, a program with many identical routines) climbs higher has not been looked at.

## Memory across signals, beyond the test

The memory test is two halves of one text, the second half twice, and one foreign text. What a memory looks like after twenty texts, how the "not seen this time" count behaves for a part that was real once and never again, and whether the sorted pool with a large memory in it still runs in seconds — none of that has been looked at. The memory file is a Python pickle, which is the easy path. A long-lived memory would want a format other programs can read.

## Time

The frame step compares a column with itself one row down and asks whether it changed. A signal with time structure (a sensor log, a state sequence) has a second kind of sameness: a row compared with the row before it. The reservoir example shows the gap: FOLLOWS gives state-to-state transitions, but nothing yet asks which units changed between one state and the next. That is the comparator on consecutive rows rather than on columns. `extend/row_by_row.py` does this for the reservoir states.

## A row signal at a second frame

A vehicle's state rows (`examples/agc-live/nudge-run/`) read as one
word per row: the frame step scores a whole row at 1.000 and picks it,
and every row is distinct, so the mint has nothing to collide. The same
file read at 16 bits — each field a word — gives the repeats: the
fields that never moved at count 1,000, the turn-rate plateaus between
jet firings as the densest parts, and the kicked axis as the field
that changes while its neighbours hold. The frame step found the
layout; the mint needed the field. Not built: when the chosen frame
leaves no repeated words, read again at the next width down that
gives some, and keep both records.

## A second dimension

An image is rows of pixels. The frame step finds the pixel width. It can find the row width only if the row in bits is under `--widest`. After that, the natural move is the frame step applied twice: once to find the pixel, once over pixels to find the row. The column habits at the row width would then be a vertical profile of the image.

## Reading a trained net

`hybrid/net_as_lens.py` reads a reservoir's states. A trained net has two more signals: its weights (a file of fixed-size numbers, readable now by packing them) and its activations on a given input (same as the reservoir states). What the weight file's record looks like, and whether the activation record of a trained net lines up with the record of the input it was shown, has not been tried.

## Two separators on the AGC rope

The rope was cut at EXTEND. The second most common word is 00000 (unused and zero words). Cutting at both would separate code regions from data regions by their zero-word boundaries and leave EXTEND inside the runs, where the mint would find the `EXTEND + opcode` pairs as shared parts.

## The bridge in the other direction

`bridge.py` finds parts present in both records. The parts present in only one, with a parent in the other that differs by a steady change (`ss` for `t`, `wasser` for `water`), are the next layer: not shared parts but shared changes between parts. That is the CLASSES idea run across two records instead of inside one.

## Size

Pure Python. The mint is a sort per round. A 1.6 MB file runs in 20 seconds with two separators. Larger signals need either `--limit`, cutting the file, or the fresh-pair rule's natural extension: sort only the fresh parts into the existing order instead of resorting the whole pool.

## The record as a knowledge graph

Every table in the record is a set of three-part facts: (walked,
made-of, walk), (the, follows, Mock), (walk, member-of, class 0.0).
That is what a knowledge graph is — things as nodes, relationships as
edges. The classes are definitions with a necessary-and-sufficient
condition (takes `+ed` and `+ing`, therefore a member), which is what a
reasoner in that world uses to classify. The part-of chain is the one
inference rule those systems start from (X is in C, C is inside D, so X
is in D), and density is that rule computed across all levels. Memory
is open-world: a part not seen this time is not marked false.

Two things have not been done. First, writing the record out in a
format those tools read (RDF triples), which would let an existing
reasoner run on Discovery's output with no new code and show what it
infers. Second, a reasoner of our own: `hybrid/record_to_rules.py`
answers one-hop questions (what follows X, what forms does X take);
nothing yet walks several hops — up part-of, forward along follows,
across changes — to answer a question that takes more than one step.
Each step of such a walk is the comparator again: is this node the one
I'm looking for.

## The AGC in the loop

The rope was read as a file. The Virtual AGC project also has an
emulator that runs the real rope, with the DSKY and a flight simulator
around it. That makes the running machine a signal: its memory,
registers, and I/O channels at each step, written out as rows, the way
`hybrid/net_as_lens.py` writes a reservoir's states. Discovery would
read what the machine does, not just what it says — which states follow
which, which instruction sequences come with which channel outputs.

Paired with the simulator's physical state (position, velocity, thrust)
as a second signal, the bridge would find which machine states come
with which physical states. Closing the loop — picking the next DSKY
entry by what followed this state in the flights that ended on the
surface — is the record-to-rules pattern plus the selection signal the
paper's section 14 says the user supplies: which flights count as good.
The limit in section 6 of the process guide applies: one flight is one
long sequence with few repeats, so this needs many simulated flights
with varied starting conditions, each one a signal added to memory.
`examples/agc-live/` has the emulator with a trace patch, a socket
client that presses DSKY keys, and one run read by Discovery. The
analysis above hasn't been done.

## What a flat record means

A compressed or encrypted file gives a flat FRAME table and a word table where nothing repeats. The record reports that as found. Whether the frame step over longer widths, or the mint over very short runs, can still read structure out of a lightly compressed signal has not been looked at.
