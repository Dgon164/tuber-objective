# Discovery

*A subroutine that learns, with 1 comparator and 1 memory*

Jason Weeks — Project Discovery, October 2026 — thetuberobjective@gmail.com

## 1. What Discovery is

Discovery reads any file as raw bits. Discovery writes a record of
everything that Discovery finds. The record shows:

- the parts
- what each part contains
- what contains each part
- what occurs before and after each part
- the change that makes one part into a different part

Discovery does not know the type of the file that you give to
Discovery. Discovery has no dictionary, no grammar rules, no list of
file types, and no training step. The program is 1 Python file. The
same Python file reads 4 inputs:

- an English novel
- a German parliament debate
- a compiled program
- the 15-bit flight software from the Apollo Lunar Module

The same Python file writes a record of each input.

This paper explains how the program operates and why the program has
this design. This paper makes no claim about the program beyond what
the 4 example records in `examples/` show. The records are the proof.
This paper is the explanation of the records, step by step.

## 2. The origin of the comparator

Discovery started from reservoir nets. A reservoir net is a small
random neural net. A reservoir net gets no training step. Many
experiments showed the same result: a simpler net was always a better
net. A smaller net gave a better result than a larger net each time. So
the net became smaller at each step.

Many layers became 1 layer. Floating-point numbers became integers.
Integers became smaller integers. Smaller integers became binary
numbers. Binary numbers became boolean values.

The result of this process is the center of the whole program: A is
not B. A boolean operation has 2 values, true or false. A boolean
operation in the smallest possible net gives the smallest unit of
information that a computer can use. That unit is 1 bit, 1 comparison,
yes or no. From that 1 operation, all the other structure makes itself:
the parts, the connections, the groups, the layers.

The comparator is the operation that checks if 2 things are the same.
The comparator finds what is the same and what is different. The memory
holds what the comparator found. From these 2 tools, structure makes
itself. The idea is the same as the idea of Hebbian learning: things
that occur together get a link to each other.

The net became smaller until no net remained. Only the comparison
remained, and that comparison is the base of each net. So the program
has no training step, no gradient descent, and no optimization.

## 3. The one tool

The whole program uses 1 operation: compare 2 things, and divide the
result into 3 bins.

- **Same**: the part that the 2 things share.
- **Different**: what remains of each thing after you remove the shared part.
- **Not part**: everything that the comparison did not touch.

This operation is the comparator. The other tool is a memory. The
memory is a place that stores what the comparator saw before. Thus the
comparator can compare the next thing against the contents of the
memory.

The comparator and the memory are the whole set of tools. A comparator
with an empty memory can only tell you that a thing exists. A
comparator with 1 thing in memory can tell you if the next thing is the
same. If the next thing is not the same, the comparator can tell you
what part is different. After that, each step in the program is the
same comparator again. The comparator operates again on what the
comparator made before.

Two of the steps below have technical verbs. To mint a part is to make
a new part from 2 parts that have the same start or the same end. To
crystallize the pool is to read the pool and to make the crystal. The
crystal is a table that puts the parts in groups by their changes. The
table below shows the 1 operation at each level of the program:

| step | the 2 things that the program compares | what is the same | what is different |
|---|---|---|---|
| frame | a column of bits, and the same column moved 1 row down | a column that stays the same | a column that changes |
| levels | a run and its neighbour 1 level up | the same run, or runs of the same kind | what remains |
| words | a word and each other word | the same word, each time the word occurs again (with a count) | a different word |
| mint | 2 neighbours in the sort order of the pool | the start (or the end) that the 2 neighbours share | the 2 parts that remain |
| crystal | a part and the larger parts that contain the part | the part itself | the change that makes the part into the larger part |
| classes | 2 parts and their sets of changes | the same set of changes | a different set of changes |
| bridge | a part in 1 record and all the parts in a different record | a part that occurs in both records | the parts that contain the part, on each side |

The program adds nothing else. A step can appear to add an idea of its
own, for example a "frame", a "separator", or a "class". That idea is
only a name for the shape of the output of the comparator at that step.

## 4. The reason to read bits

Everything that a computer stores is bits. A bit is a 1 or a 0. A text
file, a program, a picture, a sound file, and a database are all a
sequence of bits. A program reads the sequence of bits in words. All
the words have the same width. The word width is an agreement between
the person who wrote the file and the person who reads the file.

The bits do not contain the word width. ASCII text uses 8-bit words.
Only 7 of the 8 bits carry data. A compiled program on a modern machine
has 64-bit sections and 8-bit strings in the same file. The Apollo
Guidance Computer used 15-bit words. When the memory of the Apollo
Guidance Computer is packed into a file, no 15-bit word matches the
byte boundaries (the standard 8-bit grid).

The program reads everything as bits. Thus nobody can tell the program
the word width. The program must find the word width without help. This
search has a cost. A program can read a text file as bytes at once, with
no search. But you pay the cost 1 time, in the frame step.

The cost gets you everything else:

- 1 input path
- 1 mechanism
- no special code for each format
- a program that reads a 15-bit machine from 1969 with no changes

## 5. The frame (the search for the word width)

Put all the bits in rows of a width *w*. Each column then contains each
*w*-th bit of the file. If you pick the correct width, each column has
its own pattern. For example, the top bit of an ASCII byte is never 1.
The next bit down is almost always 1.

If you pick the wrong width, the bits are mixed across the columns.
Each column then has approximately 50 percent 1s and 50 percent 0s.
That column rate is random noise.

The score of a width is the gap between 2 column rates. The first rate
is the rate of the column that is 1 most often. The second rate is the
rate of the column that is 1 least often. Plain text at width 8 has a
score of 0.95. Plain text at width 7 has a score of 0.05. The width
with the largest gap wins.

There is 1 rule: a wider width wins over a narrower width only if the
difference is more than random chance can explain.

There is 1 more step: the fold. To fold a width is to divide the width
by a number and to keep the smaller width as the answer. A width of 60
has almost the same score as a width of 15, because 60 is 4 copies of
15 side by side. So, after the program picks a width, the program
checks each number that divides the width exactly. The program compares
the column pattern of the larger width with copies of the column
pattern of the smaller width. If the 2 patterns are the same, the
smaller width is the true answer.

The fold occurred with the Apollo flight software. The program first
picked 60. Then the program found that 60 is 15 repeated 4 times. The
program folded down to 15.

The frame step is the only place in the program that uses a tolerance.
A tolerance is a check that accepts a small difference. The program
calculates the tolerance from the data, from the number of rows. Nobody
sets the tolerance by hand.

## 6. Words, the separator, and runs

The program now knows the word width. The program cuts the bits into
words of that width. To cut a sequence is to divide the sequence into
smaller sequences. The program counts how often each word occurs. For
each word, the program counts the words that occur next to that word.

The most common word becomes the separator. The separator divides the
sequence. A run is everything between 2 separators.

The author chose the most common word as the separator on purpose.
That rule is the simplest rule that gives a good result. In text, the
rule gives the space character. In a compiled program, the rule gives
the zero byte. In the Apollo rope, the rule gives EXTEND (the most
common instruction prefix). Each of these 3 words is a good place for a
cut.

A signal can have more than 1 good point for a cut. Then the record
will show the other points as parts with a high frequency that never
occur alone. The flag `--separators N` makes the program cut at the N
most common words instead.

## 7. The mint (the search for the shared parts)

The pool starts as the set of all different runs. The mint is the step
of the program that mints new parts from collisions. To mint a part is
to make a new part from 2 parts that have the same start or the same
end. A collision is a match between 2 neighbours in the pool. The mint
compares the pool against itself again and again, until no new part
comes out:

1. Sort the pool. In the sort order, 2 neighbours share the longest
   start that either neighbour shares with any part in the pool.
2. Make 3 new parts for each pair of neighbours that share a start. The
   3 new parts are the shared start and the 2 parts that remain. Record
   that each neighbour is *made of* its new parts. Record that each new
   part is *part of* the neighbours that contain the new part. Add the
   new parts to the pool.
3. Reverse each part. Do steps 1 and 2 again on the parts in reverse.
   The reverse pass finds the ends that parts share.
4. If this round made no new part, stop. If this round made a new part,
   go back to step 1.

The program never removes a part. Each part keeps a count of how often
the part occurred as a complete run. Each part also keeps a density.
The density of a part is the number of other parts that contain the
part.

The letter `e` is never a complete word in Alice, but 1,615 parts
contain `e`. The word `the` occurs as a complete word 1,340 times, and
178 other parts contain `the`. The word `walk` occurs 4 times, and 4
parts contain `walk`.

The program keeps 3 rules from the larger project that Discovery came
from:

- *Compare things again and again until no new thing comes out.* The
  loop runs until the pool reaches a stable state. That stable state is
  the stop rule. A limit on the number of rounds is not the stop rule.
- *Keep a thing that is rare but real.* A part that came from 1
  collision has the same status as a part that came from 1,000
  collisions. No part fades away.
- *Store each thing 1 time with a count, not as 1,000 copies.* The pool
  has 1 entry for each different part. The entry has a number that says
  how many times the part occurred. That count is the only compression
  in the program.

## 8. The crystal (the groups of parts by their changes)

The pool is the raw memory. The crystal is a second table. To
crystallize the pool is to read the pool and to make the crystal. The
crystal puts the parts in groups and loses no detail. The crystal is a
form of deduplication. Deduplication removes the copies of a thing and
keeps everything that is important.

The crystal operates as follows. For a part, a *change* is what makes
the part into one of the larger parts that contain the part. For
example, the addition of `+ed` makes `walk` into `walked`. The set of
changes that a part accepts is a property of that part. Parts that
accept the same set of changes make a *class*. A class is a group of
parts that accept the same changes.

In Alice, 22 stems accept both `+ed` and `+ing`. These 22 stems are the
class `{+ed, +ing}`. A grammar book calls these stems verbs. The record
calls these stems by their set of changes, because the set of changes
is the only label that the signal supports.

In the German text, the class `{+en, +t}` has 52 members (verb stems).
The class `{+n, +r}` has 42 members (adjective stems).

The last table of the crystal is like a dictionary entry for each
common run. The entry shows:

- what the run contains
- what contains the run
- the changes of the run
- what comes after the run
- what comes before the run

The entry says: *This run is X. The change from X to Y is Z. X occurs
next to these other things.* That sentence is the whole shape of the
knowledge in the record. Each fact in that sentence comes with a count.

## 9. Crystallize, then loop again, until nothing changes

The crystal makes structure. If the program stops after the crystal,
the program makes structure but never uses the structure. That stop is
1 step short of the rule of the program. So the program gives what the
crystal made to the next round. The program replaces nothing. The
program adds everything.

A level has 4 steps: count the symbols, cut the runs at the most common
symbol, mint, and crystallize. The sequence of symbols of the next
level is the runs of this level, with no change. The classes of this
level become a second way for 2 symbols to count as "the same". Then 2
symbols are the same in 2 cases: the 2 symbols are the same run, or the
2 symbols are runs in the same class.

Each structure that the new level makes joins the 1 shared pool. The
structure can be a run of runs, a part that the mint made, or a class.
The connections of the structure go to the parts that the structure
contains, at each level where those parts are. So a word that is inside
40 stretches 1 level up gets 40 more in its density count.

The loop continues until a level has only 1 run. The program cannot cut
1 run. The additions become very small long before that level.

The sequence of each level is shorter than the sequence of the level
before. The separator is always present, and the cut removes the
separator. So the loop cannot run forever. The loop also does not run
for a long time. The pool only grows, and the growth stops:

- Alice: 22,446 parts, then 6,709 more, then 5, then 1, then stable.
- German text: 19,210, then 14,943, then 9, then 1.

Level 1 has this shape. In Alice, level 1 cuts at `the` (the most
common run of level 0). The runs of level 1 are the stretches between
one `the` and the next `the`. The words that occur directly before
`the` are `said`, `and`, `to`, and `of`. In the German text, level 1
cuts at the comma. The stretches that occur most often are the forms of
address.

In the Apollo assembly source, level 1 cuts at the comment mark `#`.
The parts with the highest density are instruction sequences such as
`TC BANKCALL`, `CAF ZERO`, and `CCS A`. The parts with the highest
density also include the words that the programmers wrote at the start
of a comment: `TO`, `FOR`, `IN`, `IF`, `AND`, `SET`.

## 10. The 5 steps, and the fifth step

The steps to understand a thing are as follows, in the plainest words:

1. **Identification**: the border around the thing. "This is a thing,
   separate from the background."
2. **Association**: the connection to what you know. "This thing is
   like a thing that I remember."
3. **Reduction**: the division into basic parts. "What are the basic
   parts?"
4. **Composition**: the assembly of the parts. "How do the parts fit
   together to make the whole?"
5. **Evaluation**: the check of the result. "Does the thing that I made
   match what is out there?"

The place of each step in the program:

| step | the place of the step in the program |
|---|---|
| identification | the frame step and the separator. The most common word is the background. A run is what is between 2 separators. One level up, the program does the same thing again. |
| association | the sort. The neighbour of a part in the sort order is the thing in memory that is most like the part from the front. In reverse, the neighbour is most like the part from the back. Also FOLLOWS and, 1 level up, the match by class. |
| reduction | the mint loop. The loop runs until no new part comes out. The loop separates the shared cores from the parts that remain, and keeps the parts that remain. |
| composition | made_of, part_of, the crystal entry, the classes, the levels |
| evaluation | the comparator again. The program points the comparator at the output of the model instead of at a new part. |

Evaluation is not a separate mechanism. "Does the model match reality?"
and "Is this the same as that?" are the same question. The comparator
answers both questions. At first, the comparison was present but the
loop was not. A run read 1 signal, made the pool, and stopped. So the
final comparison never became the start point of the next round.

### The same steps in other words: roots, layers, interactions, crystals, relations, causes

The 5 steps are 1 operation. The program points the operation at
different places and at different scales. The table below gives the
same list in the words that we use for the things that the program
finds. The table also gives the place of each step:

| the thing to find | the step | the place | the scales |
|---|---|---|---|
| roots | identification | the frame (the word width, from the bits). The separator (the most common word). PARTS BY DENSITY (the parts that everything else contains). The stems in a class. | bits, words, parts. Across signals (the *confirmed* bin of the memory). Across records (`bridge.py`, the shared parts). |
| layers | composition | the levels: runs of runs go into the 1 pool. `made_of` and `part_of` go across levels. | each level. The memory keeps the levels. |
| interactions | association | FOLLOWS and RUN FOLLOWS at each level. The neighbour in the sort order. The new signal against the memory. `extend/same_slot.py` and `extend/sentence.py`. | each level. Across signals. |
| crystals | reduction | CLASSES: the same set of changes. A class counts as the same 1 level up. The siblings in `extend/functions.py`. | each level. The functions. |
| relations | composition | the changes (`+ed`, `un+`). The classes. In-kind, out-kind, and paths in `extend/functions.py`. The parents on each side in `bridge.py`. | parts, functions, across records |
| causes | evaluation, with time | TIME: the program reads the sequence as time. ARROWS: a pair that occurs in both orders, and the order that wins. EFFECTS: a thing that comes after a part more often than that thing occurs at all. CHAINS: the program follows the strongest effect forward. Then `examples/agc-live/`: press, record, compare. The effect that is present only after the press. | each level of a passive signal. Across a *do* on the machine in operation. |

Time is in the signal from the start. The signal is in order, and the
order is time. FOLLOWS was always 1 way to read the order as time. The
TIME tables read the order in 3 more ways. Each way uses the comparator
along the sequence: the program compares what comes before against
what comes after.

The TIME tables at level 0 of `examples/text/alice.txt.record.txt` show
these 3 ways on the novel. The tables show:

- the arrows among the words (`said -> Alice`, `if -> you`, `I -> shall`,
  each with a count in each direction)
- the effects of `I`, of `a`, and of `little`
- the chains

The same tables in `examples/agc/luminary099.rope.record.txt` show the
instruction flow. The chains loop back through the instruction flow.
None of these tables shows a cause yet. A cause is an arrow that holds
across a *do*. The example `examples/agc-live/` presses a key and
records each signal. Then the example compares the run with the press
against the run without the press.

The effect that is present only after the press is the causal
structure. For example, engine on leads to thrust, propellant, and
accelerometer, 13 of 13. The script `walk.py` runs the causal structure
backward, from a goal to the presses that reach the goal. The comparator
is the same, and the tables are the same. The *do* is the only addition.

In the form of a program, these steps are 3 subroutines:

- **Interpret** (input): takes the signal in and applies identification
  and association. These 2 steps are the frame, the separator, and the
  sort.
- **Evaluate** (process): runs reduction, composition, and "this is not
  that". These steps remove the noise and make the model. These steps
  are the mint, the crystal, the levels, and the comparison against the
  memory.
- **Act** (output): does a thing with the result. In this program, the
  action is 2 things: the program writes the record, and the program
  updates the memory. The memory update is an action of the program on
  itself, from its own evaluation. That action is the only action that
  the program does. An action on anything else is the job of a
  different system. The guide for hybrid systems covers that job.

The memory closes the loop. With `--memory FILE`, the program saves the
pool after a run and loads the pool before the next run. The parts from
the memory are in the sort order of the pool, directly next to the runs
of the new signal. So the program compares a new run against the parts
from the memory and against the rest of the signal. A comparison counts
only if the comparison includes the new signal. The program does not
compare 2 parts from the memory that the new signal did not reach yet.

So a memory never confirms itself. The program sorts everything that
the run makes into 3 bins: confirmed, added, and not seen this time.
The program removes nothing.

The test is simple:

- The first half of Alice, with no memory: the run adds 14,079 parts.
- The second half, against that memory: the run confirms 10,588 parts
  and adds 9,337 parts.
- The second half again: the run confirms 19,833 of the 19,925 parts
  that the second half made the first time. The run adds 0 parts at
  level 0 (5 at level 1).
- The German text against the English memory: the run confirms 14,797
  parts (the short parts that the 2 alphabets share). The run adds
  17,987 parts that English never made.

The fifth step is the first step with a memory. The loop runs out of
new things in the same way as the levels.

## 11. The "meaning" of a part in a record

The record does not say what `the` means, what EXTEND does, or what a
German verb is. For each part, the record holds the position of the
part in the web of connections. The position is:

- what the part contains
- what contains the part
- what the part changes into
- what occurs next to the part

What a part means, in the only sense that the signal can give, is that
position. Two parts with the same position are the same thing with
different names. A part with a position that is not like the position
of any other part is unique.

This position is the reason that the bridge operates. Run 2 signals
separately, for example the German text and the English text from the
same day of debate. Then compare the 2 pools against each other. A part
that occurs in both pools is *same* across the 2 languages. The parts
that contain the part on each side are *different*.

For example, `technologi` occurs inside `technologische` and
`technologien` on the German side. On the English side, `technologi`
occurs inside `technologies` and `technological`. Nothing told either
record about the other record. The shared parts are the bridge between
the 2 languages. The parts that contain the shared parts show what each
language makes on top of the shared parts.

The same collision method lets a system read its own output. Give the
output to the program again. Compare the 2 records against each other.
The result is 3 bins: what came back the same, what was lost, and what
is new. The script `hybrid/loop.py` does this comparison by hand on a
walk of the model. The flag `--memory` does this comparison
automatically on each later signal (section 10).

## 12. The things that the design omits on purpose

This program has 1 design principle. Make a machine that is 1
millisecond old, with only an input, an output, and its own code.
Define nothing, because the thing that you tell the machine to look for
is possibly not the thing that the machine must find.

So the program has:

- No file-type detection. The frame step *is* the detection.
- No character set. The lens draws the letters on the page after the
  core algorithm is complete. The core algorithm never looks at the
  lens.
- No stop-word list, no tokenizer, and no stemmer. The separator is the
  most common word. The runs are what is between the separators. The
  stems are what the mint found.
- No threshold that a person set by hand to fit an example. The 1
  tolerance is the variation from random chance. The program calculates
  the tolerance from the number of rows.
- No training step, no weights, and no objective function.
- No special code for bad input. A random file gives a flat frame
  table. The program then folds to a frame of 1 bit and reports that
  frame as its result. The only refusals are at the input, each with a
  reason:
  - an option that the program does not have
  - an option with no value
  - a memory that a run wrote at a different frame or in an older
    format

The author added 2 things after the first examples ran. Both things are
limits, not new methods. The level loop came after these 2 things, and
the level loop is a method.

1. The program compares a pair of neighbours only if 1 of the 2
   neighbours is new from the last round. The result is the same, in
   half the time. (Alice went from 4 seconds to 2.)
2. A limit on the pool size (`--cap`, with a default of 1,000,000
   parts). The limit stops the loop on a very large signal and says so
   in the record.

## 13. The 4 examples

| signal | word width found | separator | what the record shows |
|---|---|---|---|
| English novel (ASCII) | 8 bits. Column 0 is never on. | the space | 73 symbols in order of frequency, the words, `+ed`/`+ing`, 22 verb stems |
| German debate (UTF-8) | 8 bits. Column 0 is on in 3.6% of the words. | the space | the umlaut lead byte (a byte that occurs only before 4 other bytes), `+en`/`+ung`/`+lich`, `be+`/`ge+`, 52 verb stems, 42 adjective stems, pairs of words with capital letters |
| compiled C program | 64 bits, with a little-endian decrease in the column rates. At 8 bits, the strings. | zero | the layout of the file. At the byte level: `hello.c`, `strlen`, `puts`, `usage: hello TEXT`, the loader path, the compiler version |
| Apollo LM flight software, packed 15-bit | 15 bits (the program picked 60 first, then folded to 15) | EXTEND | the word width of the machine, the instruction prefix as the separator, `TC BANKCALL`, `TC INTPRET`, `TC PHASCHNG` with their argument words, `RETURN` as the part with the most connections |

Each example folder has the input, the record, and a breakdown that
explains each table.

## 14. How to make new things on Discovery

The guide `guides/building-from-discovery.md` gives 3 things. First,
the guide gives the 8 things that the program rests on. For each of the
8 things, the guide gives the place in the records where you can see
that thing in operation. Second, the guide makes the case that those 8
things are enough for what the program does. Each step is the
comparator with a target. So far, no extension needed a new operation.

Third, the guide gives 3 extensions in `extend/` that show the case:

- Cut a level at a class instead of at the most common word. The result
  shows what occurs before and after a verb.
- A new kind of "same" for numbers in a range. Calls to PHASCHNG with
  any of its argument codes become 1 part.
- The comparator with the states of a net as its target, each row
  against the row before. The result shows the units that move
  together.

Each extension is a few lines on top of the main file. No extension
changes the mint, the crystal, or the levels.

The guide `guides/the-process.md` is the general method in the form of
a procedure. The guide has 8 steps, with a quick reference card at the
top and the reasons below. The guide covers what Discovery does and
what Discovery does not do (ablation, external scores). Thus a person
who applies the process to a different problem knows where the choices
are. At the bottom, the guide gives a proof for each step that makes a
claim:

- the split loses nothing
- ablation from both sides squares the loss
- the comparator is its own scorer
- the loop always stops
- the program finds everything that the sort order can show
- each part that the program finds is real
- a removal is permanent

This point must be clear: base Discovery records all the structure in a
signal that occurs more than 1 time. Discovery does not select 1 thing
and ignore the rest. If you must find 1 specific target under heavy
noise and ignore everything else, you need 1 more selection signal. The
selection signal can be:

- an answer key for the comparison
- an external yes/no
- a different way to tell the program the parts that are important to
  you

Discovery supplies the parts. The person who uses Discovery decides
what parts are important for a task.

## 15. Open ends

The file `notes/open.md` lists the things that nobody tried and the
things that the records show as the next things to try. The short list
is:

- separators that the program chooses from the record itself, not by
  count
- a read of time in the core, each row against the row before, next to
  the TIME tables that read the sequence of runs as time
- images, where the frame step meets a second dimension
- a read of the weights of a net after a training step, instead of the
  states of a reservoir
- the bridge in the other direction: the changes that 2 records share,
  not only the parts that 2 records share
- the baby model, where the loop gets the goal "keep the baby from
  touching the hot stove" (`paper/persistence.md`)
- the AGC in the loop, where the walk ran and the stages of opcodes by
  effect did not run
