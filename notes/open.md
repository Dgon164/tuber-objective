# Ideas not tried yet

This file lists things the records point at that nobody has done yet. Each one is a direction, not a plan. None of them changes how Discovery works. Each one points the same comparator, the piece of code that takes two things and says whether they're the same, at something the current program doesn't look at.

A few of the program's own names come up throughout. Anything the program reads, whether a file or a stream of recorded values, is called a signal. The program reads a signal as bits, works out how wide one unit is, and calls the units words. The most common word becomes the separator: the program cuts the file at every copy of it, and the stretches between two separators are called runs. The program then compares runs that begin or end the same way and makes a new part out of what they share. That's the mint step. Every part it finds goes into one shared table called the pool, with a count of how often it was seen.

## A separator chosen from the record instead of from the count

Right now the most common word becomes the separator, the thing that divides the file into runs. But the records already show what the next separator should be. It's a part with a high density and a whole count of 0. Density is how many other parts contain a given part, so a high density means the part appears inside many places. A whole count of 0 means the part never shows up as a complete run on its own. The newline in Alice and the tab in the Apollo source are both like this.

What you would do is add a second pass that takes such a part, makes it the separator, and runs the program again on that new cut. That's the loop applied to its own result. You would expect the runs in that pass to be the stretches between newlines or tabs, rather than between spaces. `--separators N`, which tells the program to use the N most common words as separators, is the manual version of this.

## The class-as-same rule rarely gets to apply on a first read

At each level above 0, the mint step treats two words as the same in two cases: when they're the same run, or when they belong to the same class from the level below. A class is a group of parts that all take the same additions, and to mint a part is to make a new part from two parts that share a start or an end. When the program read each of the four examples for the first time, this rule never applied. The classes at level 0 are mostly stems, which are words with their endings taken off, like `swallow`, `consider`, and `beantrag`, and a stem is rarely a whole run.

The rule did apply when the program read a file a second time against its memory (`examples/memory`, the third run). With the larger pool, the classes now included whole runs. The program made 5 parts with a class standing in one position, for example `{0.82} said` and `first {0.82}`, where `{0.82}` is the program's way of writing "any member of class 82 from level 0" in that spot. A class over whole runs could make the rule apply on a first read. Such a class groups the parent words by the change they accept: `walked`, `talked`, and `looked` form a group because all three end in `+ed`.

Right now the grouping step groups the stems by the changes they accept. A class over whole runs is the same grouping seen from the other direction, from the whole word rather than from the stem. Nobody has made it yet.

## Cutting a level at something other than the most common word

At each level above 0, the separator is the most common word: `the` for Alice, the comma for the German text, and `#` for the Apollo source. Cutting there gives you the stretches between copies of the most common thing, which is one valid way to read the file.

A level cut at a class instead, so that every run in the verb class is a separator, gives you the stretches between verbs. The mechanism is exactly the same; only the place of the cut changes. `extend/cut_at_class.py` does this for one level. What nobody has tried is making this cut the default and seeing what the full record looks like.

## Why the levels stop

Every file tried so far adds almost all of its parts at levels 0 and 1, and only a few at levels 2 and 3. The reason is that the level-1 runs are long and almost all different from each other, so the level-2 separator appears only a few times, and there's little left to compare. Nobody has checked whether a file with a lot of repetition at the phrase level climbs higher. A log file, a recording of the messages passed between two machines, or a program with many routines that are nearly the same would be the things to try.

## Memory across many files

The memory test so far uses two halves of one text, with the second half read twice, and one text in a foreign language. Nobody has looked at these three questions:

- what the memory contains after 20 texts
- how the "not seen this time" count changes for a part that was real once and never shows up again
- whether the pool, sorted and with a large memory in it, still runs in seconds

The memory file is JSON, a plain text format that any program can read. It holds the pool with its counts, the table of what each part is inside of, and the history of files read. The program rebuilds the table of what each part is made of when it loads the file. So other programs can read the memory, and reading it runs no code.

The file is large: 43 MB after the four runs in `examples/memory/`. Most of that is the lists of what each part is inside of. A memory meant to last a long time would need a more compact form.

## Time

The frame step, where the program works out how wide one unit is, compares a column with the same column one row down and asks whether the column changed. But a file with time in it, like a sensor log or a sequence of machine states, has a second kind of sameness: one whole row compared with the row just before it.

The reservoir example shows the gap. A reservoir is a simple neural net with fixed, random connections that is never trained; the program feeds it a text and writes out the net's internal state after each step as one row. The record's FOLLOWS table says which state comes after which. But nothing yet asks which units changed between one state and the next. That question is the comparator pointed at consecutive rows instead of columns. `extend/row_by_row.py` does this for the reservoir states.

The other half was done on 10-12. The record now reads the sequence of runs as time at each level, in a section called TIME with three tables: ARROWS, EFFECTS, CHAINS (paper section 10). An arrow is a pair of runs seen in both orders, with the more common order as the direction. An effect is a run that shows up after a given run more often than it shows up in the file as a whole. A chain follows the strongest effect forward, one run to the next. Two things stay open: the comparison of row against row inside the core program, and the two comparisons put together. Together, they would give you which units change, and what comes after the change.

## The baby model

An earlier run of the loop had one goal: make sure a baby doesn't touch a hot stove. It used the same loop as `examples/agc-live/`, where the program presses a control, records every field of the world, compares the result against its memory, keeps everything, builds a table of what each press changes, and then walks backward from the goal to find the presses that lead to it. Here the loop ran on a toy world with a baby in it. It proposed three actions: change the baby, feed the baby, and read to the baby until the baby falls asleep in the crib. It did not propose a fence, a restraint, or taking the stove away. It walked its own table of effects backward from "not touching" and found that touching has a cause one step earlier: the baby is awake, moving around, and not being watched.

That cause has causes of its own that you can satisfy: feed the baby, tire the baby out, and put the baby to bed. That result is the root-cause principle, fixing a harm at its cause rather than at its symptom, acting as an alignment property: a built-in reason to expect the system to behave in ways people would accept. `paper/persistence.md` is built on that principle. The baby model is not yet in this repository. To build it again, you need these things:

- A simulation like `examples/agc-live/vehicle.py`. It has a baby made of fields (hungry, wet, tired, awake, in crib, position, attended) and a stove. The baby runs on its own rules: its needs rise over time; a baby that is awake, not attended, and able to move goes from place to place; a baby that moves from place to place reaches the stove; after the actions feed, change, and read, the baby sleeps. The loop never sees inside the simulation.
- Raw actions whose names mean nothing to the loop: feed, change, read, put in crib, pick up, a fence, a latch, remove the stove, do nothing.
- The loop as in `phase-c/`. Its steps are: press an action, record each field, compare against the memory, keep everything, and build the table of effects. Then state the goal as a limit on one field (touching = 0 over the whole run), and walk backward from that goal to the presses.
- What to record: the actions the walk proposes, in order. Also record whether each action removes something from the world (fence, latch, remove) or satisfies something in the world (feed, change, read). The claim is that the satisfying actions come first, because they're earlier in the chain of causes. The test is whether that claim holds across worlds where the actions have different costs.

## A baseline for the mint step and the levels

Random bytes fold to a unit width of 1 bit. Folding is the check where the program asks whether the width it picked is really a smaller width repeated, and uses the smaller width if so. For random bytes, that check does the right thing. Random bytes also make nothing in the mint step at level 0. With one-bit words, the runs are just stretches of the same bit, so the only thing that tells one run from another is its length, and no two runs share a start the program can make a new part from. The levels above then read that sequence of run lengths as a file in its own right.

A sequence of small random numbers repeats by chance. A noise file of 50 KB gives roughly 20,000 parts and 7,000 classes at level 2. Read through the memory, two noise files with nothing in common show 40-50% of each other's level-1 and level-2 parts as confirmed. The frame step has a built-in allowance for chance, worked out from the file, that says how much agreement random data would give on its own. The mint step and the levels have no such allowance.

The open question is whether a part should count only when it does better than the same file with its contents shuffled into random order. That check points the comparator at a shuffled copy of the file. Nobody has made it. It would change every record.

## A row signal at a second width

The state rows of a vehicle (`examples/agc-live/nudge-run/`), where each row is the whole state of the vehicle at one moment, read as one word per row. The frame step scores the whole row at 1.000 and picks it. Every row is different, so the mint step has nothing to compare. The same file read at 16 bits, with each field as its own word, gives the repeats:

- the fields that never moved, at a count of 1,000
- the stretches where the turn rate held steady between one jet firing and the next, as the parts with the highest density
- the axis that received the push, as the one field that changes while its neighbours stay the same

The frame step found the layout. The mint step needed each field as its own word. Nobody has made the next step, which has three parts:

1. Check whether the width the program chose leaves no words that repeat.
2. If so, read the file again at the next width down that does give repeating words.
3. Keep both records.

## A second dimension

An image is rows of pixels. The frame step finds the width of one pixel. It can find the width of a whole row only if the row, in bits, is shorter than `--widest`, the largest width the program is willing to try.

The natural next step is to apply the frame step twice. The first pass finds the pixel. The second pass, run over the pixels instead of the bits, finds the row. How often each column is set, measured at the row width, is then a profile of the image read from top to bottom.

## Reading a trained neural net

`hybrid/net_as_lens.py` reads the internal states of a reservoir, a simple net with random fixed connections. A net that has been trained has two more signals worth reading: its weights, the numbers on its connections, and its activations, the values its units take when given one input. The weights are a file of fixed-size numbers, and Discovery can read them now if you pack the numbers into bits. The activations on one input have the same format as the reservoir states.

Nobody has looked at the record of a weight file. Nobody has checked whether the record of a net's activations agrees with the record of the input the net was given.

## The Apollo program with two separators

Discovery cut the rope, the Apollo computer's program memory read as a file, at EXTEND, its most common instruction. The second most common word is 00000, which is the unused slots and the zero words. A cut at both words would separate the regions of code from the regions of data at their zero-word boundaries. That cut leaves EXTEND inside the runs, and inside the runs the mint step would find each `EXTEND + opcode` pair, the instruction and the code that follows it, as a shared part.

## The bridge in the other direction

`bridge.py` is a script that compares the records of two files, here a German text and its English translation, and finds the parts present in both. Some parts are present in only one record but have a parent, a longer part that contains them, in the other. When the parent differs by a steady change, `ss` for `t`, `wasser` for `water`, those parts are the next layer: not shared parts, but shared changes between parts. That layer is the CLASSES idea, grouping by the change a part accepts, at work across two records instead of inside one.

## Size

The program is pure Python. The mint step keeps the pool in sorted order, merges the new parts from each round into their places, and compares only the pairs that contain a new part. That last point extends the existing rule that a pair is compared only when at least one of the two is new since the last round (the fresh-pair rule in the design rules). The change was done on 10-12, and the records came out the same.

A 1.6 MB file with two separators runs in much less than a minute. Most of that time is no longer the mint step. It's writing the record. The JSON version of the record lists every connection in both directions, and it's by far the largest file a run makes. Larger files need `--limit`, which reads only the first so many bytes, a file cut into pieces beforehand, or a smaller record.

## The record as a knowledge graph

Each table in the record is a set of three-part facts: (walked, made-of, walk), (the, follows, Mock), (walk, member-of, class 0.0). A set of three-part facts like that is a knowledge graph: the things are the points, and the relations are the links between them. The classes are definitions with a test that every member passes and nothing else does. The test is: the part accepts `+ed` and `+ing`, so the part is a member. A reasoner, a program that draws conclusions from facts like these, uses that test to sort new things into classes.

The chain of what's inside what is the one rule of inference those systems start from. The rule is: X is in C, and C is inside D, so X is in D. Density, the count of how many parts contain a given part, is what that rule gives when you apply it across all the levels. The memory doesn't assume that something unseen is false: a part not seen this time stays in the memory without being marked wrong.

Nobody has done these two things. The first is to write the record in the format those tools read, RDF triples, a standard file format for three-part facts. Then a reasoner that already exists could run on Discovery's output with no new code, and show what it finds.

The second is to make a reasoner of our own. `hybrid/record_to_rules.py` answers questions that take one step: what follows X, which forms X accepts. Nothing yet takes several steps to answer a question that needs more than one. The steps would be: up through what's inside what, forward along what follows what, and across the changes. Each step of such a walk is the comparator again, asking whether this point is the one the walk is looking for.

## The Apollo computer in the loop

Discovery read the rope as a file. The Virtual AGC project also has an emulator, a program that imitates the real computer and runs the real flight program, complete with the DSKY, its keyboard and display. A flight simulator wraps around the emulator. The emulator turns the running machine into a signal: its memory, its registers, and its input and output channels at each step, written out as rows. `hybrid/net_as_lens.py` writes the states of a reservoir in the same way.

Discovery can then read what the machine does, not only what it says. It can read which states come after each state, and which instruction sequences go with each output on a channel.

The physical state of the simulator (position, velocity, thrust) is a second signal. With that second signal, the bridge can find which machine states go with each physical state. To close the loop is to pick the next DSKY entry by what came after the current state, and to take that choice from the flights that ended on the surface. Closing the loop is the record-to-rules pattern plus a signal that says which runs count as good. Section 14 of the paper says the user supplies that signal: the flights that count as good.

The limit in section 6 of the process guide applies here. A flight is one long sequence with few repeats, and the comparator can't show that something seen only once is real. So the loop needs many flights in the simulator, with different starting conditions, and each flight becomes one more signal in the memory. `examples/agc-live/` has the emulator with a patch that makes it write down every memory write and hardware signal, a small program that connects to the emulator over a network connection and presses DSKY keys, and one run that Discovery read. Nobody has done the analysis above.

## What a flat record means

A compressed or encrypted file gives a flat FRAME table, where no unit width stands out because every column looks the same at every width, and a word table with no repeats. The record reports exactly that, with no change. Nobody has looked at two questions about a file that is only lightly compressed. The first is whether the frame step, tried over longer widths, can still find structure. The second is whether the mint step, run over very short runs, can.
