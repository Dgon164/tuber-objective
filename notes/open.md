# Open directions

This file lists things that the records point at, and that nobody has done yet. Each thing is a direction, not a plan. No direction changes how Discovery operates. Each direction points the same comparator at a thing that the current program does not examine.

## Separators from the record, not from the count

At present, the most common word becomes the separator. The separator is the thing that divides the signal into runs. But the records show the next separator. The next separator is a part with a high density and a whole count of 0. A part with a high density appears inside many other parts. Examples are the newline in Alice and the tab in the AGC source.

A second pass can make such a part the separator. Then the second pass runs the program again. That second pass applies the loop to its own cut. To cut a signal is to divide the signal into runs at each copy of the separator. `--separators N` is the manual version.

## The late start of the class-as-same rule

At each level above 0, the mint step treats 2 words as the same if the 2 words are the same run. The mint step also treats 2 words as the same if the 2 words are in the same class from the level below. To mint a part is to make a new part from 2 parts that have the same start or the same end. When the program read each of the 4 examples the first time, this rule never applied. The classes at level 0 are mostly stems, for example `swallow`, `consider`, and `beantrag`. A stem is rarely a whole run.

The rule did apply when the program read a signal a second time against the memory (`examples/memory`, third run). With the larger pool, the classes include whole runs. The program made 5 parts with a class in a slot, for example `{0.82} said` and `first {0.82}`. A class over whole runs can make the rule apply when the program reads a signal the first time. Such a class groups the parent words by the change that the parent words accept. For example, `walked`, `talked`, and `looked` make a group because all 3 words end in `+ed`.

At present, the crystal groups the stems by the changes that the stems accept. A class over whole runs is the same crystal from the other direction. Nobody has made this class yet.

## Levels with a cut at a place other than the most common word

At each level above 0, the separator is the most common word: `the` for Alice, the comma for the German text, and `#` for the Apollo source. The cut at the most common word gives the stretches between the most common thing. Those stretches are 1 valid way to read the signal.

A level with a cut at a class (for example, each run in the verb class) gives the stretches between verbs. The mechanism is the same. Only the cut changes. `extend/cut_at_class.py` does this for 1 level. Nobody has tried this cut as a replacement for the default cut.

## The reason that the levels stop

Each signal that was tried adds almost all of its parts at levels 0 and 1. Each signal adds only a few parts at levels 2 and 3. The reason is that the level-1 runs are long and almost all different. Thus the level-2 separator appears only a few times, and there is little to compare. Nobody has examined if a signal with much repetition at the phrase level climbs higher. Examples of such a signal are a log file, a protocol trace, and a program with many routines that are the same.

## Memory across signals, beyond the test

The memory test uses 2 halves of 1 text, the second half 2 times, and 1 foreign text. Nobody has examined these 3 questions:

- what a memory contains after 20 texts
- how the "not seen this time" count changes for a part that was real 1 time and never appears again
- if the pool in sort order, with a large memory in it, still runs in seconds

The memory file is JSON. The file contains the pool with its counts, part_of, and the history. The program makes made_of again when the program loads the file. Thus other programs can read the file. To read the file runs no code.

The file is large: 43 MB after the 4 runs in `examples/memory/`. Most of the 43 MB is the part_of lists. A memory with a long life needs a more compact form.

## Time

The frame step compares a column with the same column 1 row down. The frame step checks if the column changed. A signal with time structure (a sensor log, a state sequence) has a second type of sameness. The second type is a comparison of a row with the row before that row.

The reservoir example shows the gap. FOLLOWS gives the transitions from state to state (what comes after what). But nothing yet checks the units that changed between 1 state and the next state. That check is the comparator on consecutive rows, not on columns. `extend/row_by_row.py` does this check for the reservoir states.

The other half was done on 10-12. The record now reads the sequence of runs as time at each level: TIME: ARROWS, EFFECTS, CHAINS (paper section 10). These 2 things stay open: the comparison of row with row in the core, and the 2 comparisons together. The 2 comparisons together give the units that change, and what comes after the change.

## The baby model

An earlier run of the loop had 1 goal: make sure that the baby does not touch the hot stove. The run used the same press-record-compare-walk loop as `examples/agc-live/`, but on a toy world with a baby in it. The loop proposed 3 actions: change the baby, feed the baby, and read to the baby until the baby sleeps in the crib. The loop did not propose a fence, a restraint, or the removal of the stove. The loop walked its own effects table backward from "not touching". The loop found that the touch has a cause upstream: the baby is awake, mobile, and not attended.

That cause has causes that you can satisfy: feed the baby, tire the baby, and put the baby to bed. That result is the root-cause principle in the role of an alignment property. `paper/persistence.md` has that principle as its base. The baby model is not yet in this repository. To make the baby model again, you need these things:

- A simulation like `examples/agc-live/vehicle.py`. The simulation has a baby as fields (hungry, wet, tired, awake, in crib, position, attended) and a stove. The baby has its own dynamics. The needs of the baby rise with time. A baby that is awake, not attended, and mobile moves from place to place. A baby that moves from place to place reaches the stove. After the actions feed, change, and read, the baby sleeps. The loop never sees inside the simulation.
- Raw actions. The names of the actions mean nothing to the loop. The actions are: feed, change, read, put in crib, pick up, a fence, a latch, remove the stove, do nothing.
- The loop as in `phase-c/`. The loop steps are: press, record each field, compare against the memory, keep all things, make the effects table. Then the goal is a constraint on a field (touching = 0 over the run). Then the loop walks backward from the goal to the presses.
- What to record: the actions that the walk proposes, in order. Also record if each action removes a thing from the world (fence, latch, remove) or satisfies a thing in the world (feed, change, read). The claim is that the actions that satisfy come first, because those actions are upstream in the chain. The test is if that claim holds across worlds with different costs.

## A null for the mint step and the levels

Random bytes fold to a frame of 1 bit. To fold a width is to replace the width with a smaller width that explains the same column rates. For random bytes, the fold step operates correctly. Random bytes mint nothing at level 0. The runs are only run-lengths, and no 2 runs have the same head. The levels above then read the sequence of run-lengths as a signal.

A sequence of small random numbers repeats by chance. A noise file of 50 KB gives approximately 20,000 parts and 7,000 classes at level 2. Through the memory, 2 noise files with no relation show 40-50% of the level-1 and level-2 parts of each other as confirmed. The frame step has a chance term that the program computes from the signal. The chance term is the amount of agreement that random data gives. The mint step and the levels do not have a chance term.

The open question is if a part must count only when the part does better than a copy of the same signal in random order. That check points the comparator at a copy of the signal in random order. Nobody has made this check. The check will change each record.

## A row signal at a second frame

The state rows of a vehicle (`examples/agc-live/nudge-run/`) read as 1 word per row. The frame step scores a whole row at 1.000 and picks the whole row. Each row is different, so the mint step has nothing to compare. The same file at 16 bits, with each field as its own word, gives the repeats:

- the fields that never moved, at a count of 1,000
- the turn-rate plateaus between the times when the jets fire, as the densest parts
- the axis that received the kick, as the field that changes when its neighbors stay the same

The frame step found the layout. The mint step needed each field as its own word. Nobody has made the next step. The next step has 3 parts:

1. Check if the frame that the program chose leaves no words that repeat.
2. If the check is true, read the file again at the next width down that gives words that repeat.
3. Keep both records.

## A second dimension

An image is rows of pixels. The frame step finds the pixel width. The frame step can find the row width only if the row in bits is less than `--widest`.

After that, the natural next step is to apply the frame step 2 times. The first time finds the pixel. The second time, over the pixels, finds the row. The column habits at the row width are then a vertical profile of the image.

## The record of a neural net after training

`hybrid/net_as_lens.py` reads the internal states of a reservoir. A neural net after training has 2 more signals of interest: the weights and the activations. The weights are a file of fixed-size numbers. Discovery can read the weights now, if you pack the numbers into bits. The activations on 1 input have the same format as the reservoir states.

Nobody has examined the record of the weight file. Nobody has examined if the activation record of the net agrees with the record of the input that the net received.

## The AGC rope with 2 separators

Discovery cut the rope at EXTEND (the most common instruction). The second most common word is 00000 (slots not in use, and zero words). A cut at both words separates the code regions from the data regions at their zero-word boundaries. That cut leaves EXTEND inside the runs. Inside the runs, the mint step finds the `EXTEND + opcode` pairs as shared parts.

## The bridge in the other direction

`bridge.py` finds the parts that are present in both records. Some parts are present in only 1 record and have a parent in the other record. If the parent differs by a steady change (`ss` for `t`, `wasser` for `water`), those parts are the next layer. The next layer is not shared parts but shared changes between parts. That layer is the CLASSES idea at work across 2 records, not inside 1 record.

## Size

The program is pure Python. The mint step keeps the pool in sort order. The mint step merges the new parts of each round into the pool at the correct places. The mint step compares only the pairs with a new part. That behavior is the natural extension of the fresh-pair rule. The change was done on 10-12, with the same records.

A 1.6 MB file with 2 separators runs in much less than 1 minute. Most of that time is no longer the mint step. The program uses most of that time to write the record. The JSON of the record lists each connection in both directions. The JSON is by far the largest file that the run makes. Larger signals need `--limit`, a cut file, or a smaller record.

## The record as a knowledge graph

Each table in the record is a set of 3-part facts: (walked, made-of, walk), (the, follows, Mock), (walk, member-of, class 0.0). A set of 3-part facts is a knowledge graph. In a knowledge graph, the things are the nodes and the relations are the edges. The classes are definitions with a necessary-and-sufficient condition. The condition is: the part accepts `+ed` and `+ing`, so the part is a member. A reasoner in that world uses that condition to classify.

The part-of chain is the 1 inference rule that those systems start from. The rule is: X is in C, C is inside D, so X is in D. The density is the result of that rule across all levels. The memory is open-world. The memory does not mark a part as false when the part is not seen this time.

Nobody has done these 2 things. The first thing is to write the record in a format that those tools read (RDF triples). Then a reasoner that already exists can run on the output of Discovery with no new code and show what the reasoner finds.

The second thing is to make a reasoner of our own. `hybrid/record_to_rules.py` answers 1-hop questions (what follows X, the forms that X accepts). Nothing yet walks several hops to answer a question that needs more than 1 step. The hops are: up part-of, forward along follows, and across changes. Each step of such a walk is the comparator again. The comparator checks if this node is the node that the walk looks for.

## The AGC in the loop

Discovery read the rope as a file. The Virtual AGC project also has an emulator that runs the real rope. The emulator has the DSKY (keyboard and display). A flight simulator encloses the emulator. The emulator makes the machine in operation into a signal. The signal is the memory of the machine, the registers, and the I/O channels at each step, in rows. `hybrid/net_as_lens.py` writes the states of a reservoir in the same way.

Discovery can then read what the machine does, not only what the machine says. Discovery can read the states that come after each state, and the instruction sequences that come with each channel output.

The physical state of the simulator (position, velocity, thrust) is a second signal. With that second signal, the bridge can find the machine states that come with each physical state. To close the loop is to pick the next DSKY entry by what came after the current state. The source of that choice is the flights that ended on the surface. To close the loop is the record-to-rules pattern plus the selection signal. Section 14 of the paper says that the user supplies the selection signal: the flights that count as good.

The limit in section 6 of the process guide applies. A flight is 1 long sequence with few repeats. Thus the loop needs many flights in the simulator, with different start conditions. Each flight is 1 more signal in the memory. `examples/agc-live/` has the emulator with a trace patch, a socket client that presses DSKY keys, and 1 run that Discovery read. Nobody has done the analysis above.

## The meaning of a flat record

A compressed or encrypted file gives a flat FRAME table and a word table with no repeats. The record reports that result with no change. Nobody has examined 2 questions about a lightly compressed signal. The first question is if the frame step over longer widths can still find structure. The second question is if the mint step over very short runs can still find structure.
