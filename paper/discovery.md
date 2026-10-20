# Discovery

*A subroutine that learns, with one comparison and one memory*

Jason Weeks — Project Discovery, October 2026 — thetuberobjective@gmail.com

## 1. What Discovery is

Discovery is a program that reads any file as a string of raw bits,
finds the repeated structure in those bits by comparing them to each
other, and writes down what it found. What it writes is called the
record. The record shows:

- the parts
- what each part contains
- what contains each part
- what occurs before and after each part
- the change that makes one part into a different part

Discovery doesn't know what kind of file you've given it. It has no
dictionary, no grammar rules, no list of file types, and no training
step. The whole program is one Python file, and that same file reads
four very different inputs:

- an English novel
- a German parliament debate
- a compiled program
- the 15-bit flight software from the Apollo Lunar Module

and writes a record of each.

This paper explains how the program works and why it is built the way
it is. It claims nothing about the program beyond what the four example
records in `examples/` show. The records are the proof. This paper
walks through them, step by step, and says what each step does.

## 2. Where the comparison came from

Discovery started out as work on reservoir nets. A reservoir net is a
small neural net whose connections are chosen at random and never
trained. Experiment after experiment gave the same result: the simpler
net did better. Every time, a smaller net beat a larger one. So at each
step the net was made smaller.

Many layers became one layer. Floating-point numbers (numbers with a
decimal point) became whole numbers. The whole numbers became smaller
whole numbers, then binary numbers made of nothing but 1s and 0s, then
true-or-false values.

What's left at the end of that process is the center of the whole
program: A is not B. A true-or-false check has two possible answers. In
the smallest net there is, that check gives the smallest unit of
information a computer can use: one bit, one comparison, yes or no. From
that one operation, everything else builds itself up: the parts, the
connections between them, the groups, and the layers.

The operation that checks whether two things are the same, and says
what they share and where they differ, is what this paper calls the
comparator. The memory is the place that holds what the comparator
found. From these two tools, structure builds itself. The idea is the
same as Hebbian learning, the rule from brain science that things which
happen together get connected to each other.

The net kept getting smaller until there was no net left. Only the
comparison remained, and the comparison is what every net is built on.
That's why the program has no training step, no gradient descent (the
usual way a net is trained, by nudging its numbers a little at a time
toward less error), and no search for a best setting of anything.

## 3. The one tool

The whole program uses one operation: compare two things, and sort what
comes out into three bins.

- **Same**: the part the two things share.
- **Different**: what's left of each thing once you take the shared part away.
- **Not part**: everything the comparison didn't touch.

That operation is the comparator. The only other tool is the memory, a
place that stores what the comparator saw before, so that the comparator
can compare the next thing against what's already there.

The comparator and the memory are the entire set of tools. A comparator
with an empty memory can only tell you that a thing exists. A comparator
with one thing in memory can tell you whether the next thing is the
same, and if it isn't, which part differs. From there on, every step in
the program is the same comparator again, pointed at what the comparator
made the step before.

The table below shows that one operation at each step of the program.
Several of the steps have names of their own, so here is what each one
does in plain words. The *frame* is the step that works out how wide one
unit of the file is, by lining the bits up in columns; a *word* is one
unit of that width. The *separator* is the most common word, which the
program treats as a divider, and a *run* is a stretch of words between
two separators. The *pool* is the one list the program keeps of every
different part it has found, each with a count.

To *mint* a part is to make a new part from two parts that have the same
start or the same end; the *mint* step does this across the whole pool.
To *crystallize* the pool is to read the pool and make the *crystal*, a
table that puts the parts into groups by the changes they take; one such
group is a *class*. The *levels* are the rounds in which the program
takes the runs it found, treats each run as a single unit, and runs the
whole process again one level up. The *bridge* is the comparison run
between two separate records instead of inside one.

| step | the two things the program compares | what is the same | what is different |
|---|---|---|---|
| frame | a column of bits, and the same column moved down one row | a column that stays the same | a column that changes |
| levels | a run and its neighbour one level up | the same run, or runs of the same kind | what remains |
| words | a word and each other word | the same word, each time it occurs again (with a count) | a different word |
| mint | two neighbours in the sorted pool | the start (or the end) that the two neighbours share | the two leftovers |
| crystal | a part and the larger parts that contain it | the part itself | the change that makes the part into the larger part |
| classes | two parts and their sets of changes | the same set of changes | a different set of changes |
| bridge | a part in one record and all the parts in a different record | a part that occurs in both records | the parts that contain it, on each side |

The program adds nothing else. A step can look as if it brings in an
idea of its own, such as a "frame", a "separator", or a "class", but
each of those is only a name for the shape the comparator's output takes
at that step.

## 4. Why the program reads bits

Everything a computer stores is bits, and a bit is a 1 or a 0. A text
file, a program, a picture, a sound file, and a database are all one
long sequence of bits. A program reads that sequence in words, and every
word has the same width. The width of a word is an agreement between
whoever wrote the file and whoever reads it.

The bits themselves don't say what the word width is. ASCII text, the
plain English character set, uses 8-bit words, and only 7 of the 8 bits
carry data. A compiled program on a modern machine has 64-bit sections
and 8-bit strings in the same file. The Apollo Guidance Computer (the
AGC) used 15-bit words, and when its memory is packed into a file, no
15-bit word lines up with the 8-bit grid that bytes use.

Discovery reads everything as bits, so nobody can tell it the word
width. It has to find the width on its own. That search has a cost: a
program that knew it was reading text could read the file straight off
as bytes, with no search at all. But you pay that cost once, in the
frame step.

And the cost buys everything else:

- one input path
- one mechanism
- no special code for each format
- a program that reads a 15-bit machine from 1969 without any changes

## 5. The frame: finding the word width

The frame step takes the bits of the file and works out how wide one
unit is. Lay all the bits out in rows of some width *w*. Each column
then holds every *w*-th bit of the file. If you picked the right width,
each column has a pattern of its own. In ASCII text, for example, the
top bit of each byte is never 1, and the next bit down is almost always
1.

If you picked the wrong width, the bits get mixed across the columns,
and each column comes out roughly half 1s and half 0s. A column like
that is random noise.

For each column, the program counts how often that column holds a 1;
call that the column's rate. The score of a width is the gap between two
of those rates: the rate of the column that is 1 most often, and the
rate of the column that is 1 least often. Plain text scores 0.95 at
width 8 and 0.05 at width 7. The width with the largest gap wins.

There is one rule on top of that: a wider width beats a narrower one
only when the difference is bigger than random chance could explain.

There's one more step, the fold. To fold a width is to divide it by a
whole number and keep the smaller width as the answer. A width of 60
scores almost the same as a width of 15, because 60 is four copies of 15
side by side. So once the program has picked a width, it checks each
number that divides that width exactly. It compares the column pattern
of the larger width with copies of the column pattern of the smaller
width, and if the two patterns are the same, the smaller width is the
true answer.

This happened with the Apollo flight software. The program first picked
60, then found that 60 is 15 repeated four times, and folded down to 15.

The frame step is the only place in the program that uses a tolerance,
that is, an allowance for how far apart two numbers can be and still
count as the same. The program works the tolerance out from the data,
from the number of rows. Nobody sets it by hand.

## 6. Words, the separator, and runs

Now that the program knows the word width, it cuts the bits into words
of that width and counts how often each word occurs. For each word, it
also counts which words occur next to it.

The most common word becomes the separator: the word the program treats
as a divider. A run is everything between two separators.

Choosing the most common word as the separator was a deliberate
decision. It's the simplest rule that gives a good result. In text it
picks out the space. In a compiled program it picks out the zero byte.
In the Apollo flight software it picks out EXTEND, the code that most
often sits in front of an instruction (the instruction prefix). Each of
those three is a good place to cut.

A signal can have more than one good place to cut. When it does, the
record shows the other candidates as parts that occur very often but
never on their own. The flag `--separators N` tells the program to cut
at the N most common words instead of just the first.

## 7. The mint: finding the shared parts

The pool starts out as the set of all the different runs. The mint is
the step that makes new parts out of pairs of parts that match. To mint
a part is to make a new part from two parts that have the same start or
the same end. The mint compares the pool against itself over and over,
until no new part comes out:

1. Sort the pool. Once it's sorted, any two neighbours share the longest
   start that either of them shares with any part in the pool.
2. For each pair of neighbours that share a start, make three new parts:
   the shared start and the two leftovers. Record that each neighbour is
   *made of* its new parts, and that each new part is *part of* the
   neighbours that contain it. Add the new parts to the pool.
3. Reverse every part, and do steps 1 and 2 again on the reversed parts.
   This pass finds the ends that parts share.
4. If this round made no new part, stop. If it made one, go back to
   step 1.

The program never removes a part. Each part keeps a count of how often
it occurred as a complete run. Each part also keeps a count of how many
other parts contain it; that count is the part's density.

The letter `e` is never a complete word in Alice, but 1,615 parts
contain it. The word `the` occurs as a complete word 1,340 times, and
178 other parts contain it. The word `walk` occurs 4 times, and 4 parts
contain it.

The program keeps three rules from the larger project Discovery came out
of:

- *Compare things again and again until nothing new comes out.* The
  loop runs until the pool stops changing. That is the stop rule. A
  limit on the number of rounds is not.
- *Keep a thing that is rare but real.* A part that came from one match
  has the same standing as a part that came from 1,000 matches. No part
  fades away.
- *Store each thing once, with a count, rather than as 1,000 copies.*
  The pool has one entry for each different part, and the entry carries
  a number saying how many times that part occurred. That count is the
  only compression in the program.

## 8. The crystal: grouping the parts by their changes

The pool is the raw memory. The crystal is a second table built from it.
To crystallize the pool is to read the pool and make the crystal, which
puts the parts into groups without losing any detail. The crystal is a
way of removing duplicates: it collapses the copies of a thing into one
entry and keeps everything that matters.

Here is how the crystal works. For any part, a *change* is what turns
that part into one of the larger parts that contain it. Adding `+ed`,
for example, turns `walk` into `walked`. The set of changes a part
accepts is a property of that part, and parts that accept the same set
of changes make up a *class*: a group of parts that all take the same
changes.

In Alice, 22 stems accept both `+ed` and `+ing`. Those 22 stems are the
class `{+ed, +ing}`. A grammar book would call them verbs. The record
calls them by their set of changes, because that set is the only label
the signal itself supports.

In the German text, the class `{+en, +t}` has 52 members, which are verb
stems, and the class `{+n, +r}` has 42 members, which are adjective
stems.

The last table of the crystal reads like a dictionary entry for each
common run. The entry shows:

- what the run contains
- what contains the run
- the changes the run takes
- what comes after the run
- what comes before the run

In words, the entry says: *This run is X. The change from X to Y is Z. X
occurs next to these other things.* That sentence is the whole shape of
what the record knows, and every fact in it comes with a count.

## 9. Crystallize, then go round again, until nothing changes

The crystal makes structure. If the program stopped after the crystal,
it would have made structure without ever using it, and that would be
one step short of the program's own rule. So the program hands what the
crystal made to the next round. Nothing is replaced; everything is
added.

A level is one full round of the process. The units a level counts are
called its symbols: at level 0 they are the words of the frame width,
and at level 1 they are the runs of level 0. A level has four steps:
count the symbols, cut the sequence into runs at the most common symbol,
mint, and crystallize. The sequence of symbols for the next level is
just the runs of this level, unchanged. The classes of this level become
a second way for two symbols to count as "the same". So two symbols are
the same in two cases: they are the same run, or they are runs in the
same class.

Every structure the new level makes goes into the one shared pool,
whether it's a run of runs, a part the mint made, or a class. Its
connections go to the parts it contains, at every level those parts live
on. So a word that sits inside 40 stretches one level up gets 40 more on
its density count.

The loop goes on until a level has only one run, which can't be cut. The
additions get very small long before that level.

Each level's sequence is shorter than the one before, because the
separator is always present and the cut removes it, so the loop can't
run forever. It doesn't run for long, either. The pool only grows, and
the growth stops:

- Alice: 22,446 parts, then 6,709 more, then 5, then 1, then stable.
- German text: 19,210, then 14,943, then 9, then 1.

Level 1 looks like this. In Alice, level 1 cuts at `the`, the most
common run of level 0. The runs of level 1 are the stretches between one
`the` and the next `the`. The words that come directly before `the` are
`said`, `and`, `to`, and `of`. In the German text, level 1 cuts at the
comma, and the stretches that occur most often are the forms of address.

In the Apollo assembly source (the human-readable listing of the flight
software), level 1 cuts at the comment mark `#`. The parts with the
highest density are instruction sequences such as `TC BANKCALL`,
`CAF ZERO`, and `CCS A`, along with the words the programmers wrote at
the start of a comment: `TO`, `FOR`, `IN`, `IF`, `AND`, `SET`.

## 10. The five steps, and the fifth step

In the plainest words, these are the steps to understanding a thing:

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

Here is where each step lives in the program:

| step | where the step lives in the program |
|---|---|
| identification | the frame step and the separator. The most common word is the background, and a run is what sits between two separators. One level up, the program does the same thing again. |
| association | the sort. A part's neighbour in the sorted pool is the thing in memory most like it from the front; in the reversed pass, the thing most like it from the back. Also the table of what comes right after each word (FOLLOWS) and, one level up, the match by class. |
| reduction | the mint loop, which runs until no new part comes out. It separates the shared cores from the leftovers, and keeps the leftovers. |
| composition | made_of, part_of, the crystal entry, the classes, the levels |
| evaluation | the comparator again, pointed at the output of the model instead of at a new part. |

Evaluation isn't a separate mechanism. "Does the model match reality?"
and "Is this the same as that?" are the same question, and the
comparator answers both. At first, the comparison was there but the loop
wasn't: a run read one signal, built the pool, and stopped, so the final
comparison never became the starting point of the next round.

### The same five steps, named by what they find: roots, layers, interactions, crystals, relations, causes

The five steps are one operation, pointed at different places and at
different scales. The table below gives the same list using the words we
use for the things the program finds, and says where each one lives.
Several entries name tables in the record, so here is what each table
holds. PARTS BY DENSITY ranks the parts by how many other parts contain
them. FOLLOWS lists which word comes after which, and RUN FOLLOWS does
the same for runs. CLASSES lists the parts that take the same set of
changes. TIME reads the sequence as time and holds three tables of its
own: ARROWS, for pairs that occur in both orders, with the order that
wins; EFFECTS, for things that come after a part more often than they
occur overall; and CHAINS, which follow the strongest effect forward.
Two entries also mention functions: in `extend/functions.py`, each
change the crystal found is treated as a function, a rule that turns one
part into another.

| the thing to find | the step | the place | the scales |
|---|---|---|---|
| roots | identification | the frame (the word width, from the bits). The separator (the most common word). PARTS BY DENSITY (the parts that everything else contains). The stems in a class. | bits, words, parts. Across signals (the parts a new signal makes again that the memory already held: the *confirmed* bin of the memory). Across records (`bridge.py`, the shared parts). |
| layers | composition | the levels: runs of runs go into the one pool. `made_of` and `part_of` reach across levels. | each level. The memory keeps the levels. |
| interactions | association | FOLLOWS and RUN FOLLOWS at each level. The neighbour in the sorted pool. The new signal against the memory. `extend/same_slot.py`, which groups words by the neighbours they sit between, and `extend/sentence.py`, which writes sentences by following what comes after what. | each level. Across signals. |
| crystals | reduction | CLASSES: the same set of changes. A class counts as the same one level up. The siblings in `extend/functions.py` (two changes that the same parts take). | each level. The functions. |
| relations | composition | the changes (`+ed`, `un+`). The classes. In `extend/functions.py`: for each change, the other changes seen on the same parts (its in-kind), the changes seen applied to what it makes (its out-kind), and the chains of changes that can follow one another (paths). In `bridge.py`, the larger parts that contain a shared part on each side (its parents). | parts, functions, across records |
| causes | evaluation, with time | TIME: the program reads the sequence as time. ARROWS: a pair that occurs in both orders, and the order that wins. EFFECTS: a thing that comes after a part more often than it occurs at all. CHAINS: the program follows the strongest effect forward. Then `examples/agc-live/`: press, record, compare. The effect that is there only after the press. | each level of a signal the program only watches. Across an action taken on the running machine. |

Time is in the signal from the start. The signal is in order, and the
order is time. FOLLOWS was always one way to read that order as time;
the TIME tables read it in three more ways. Each way uses the comparator
along the sequence: the program compares what comes before against what
comes after.

The TIME tables at level 0 of `examples/text/alice.txt.record.txt` show
these three ways on the novel. They show:

- the arrows among the words (`said -> Alice`, `if -> you`, `I -> shall`,
  each with a count in each direction)
- the effects of `I`, of `a`, and of `little`
- the chains

The same tables in `examples/agc/luminary099.rope.record.txt` show the
flow of instructions, and the chains loop back through that flow. None
of these tables shows a cause yet. A cause is an arrow that still holds
when you act on the machine instead of just watching it. The example in
`examples/agc-live/` presses a key and records every signal, then
compares the run with the press against the run without it.

The effect that is there only after the press is the causal structure.
For example, engine on leads to thrust, propellant, and accelerometer,
13 of 13. The script `walk.py` runs that structure backward, from a goal
to the presses that reach it. The comparator is the same, and the tables
are the same. The only thing added is the action on the machine.

Written as a program, these steps are three pieces, each with one job
(three subroutines):

- **Interpret** (input): takes the signal in and applies identification
  and association. These two steps are the frame, the separator, and
  the sort.
- **Evaluate** (process): runs reduction, composition, and "this is not
  that". These steps remove the noise and build the model. They are the
  mint, the crystal, the levels, and the comparison against the memory.
- **Act** (output): does something with the result. In this program,
  the action is two things: the program writes the record, and it
  updates the memory. The memory update is the program acting on
  itself, from its own evaluation, and it is the only action the
  program takes. Acting on anything else is the job of a different
  system; the guide for hybrid systems (programs that connect Discovery
  to another system) covers that.

The memory closes the loop. With `--memory FILE`, the program saves the
pool after a run and loads it back before the next run. The parts from
the memory sit in the sorted pool directly next to the runs of the new
signal, so the program compares a new run against the remembered parts
and against the rest of the signal alike. A comparison only counts if it
includes the new signal: the program doesn't compare two parts from the
memory that the new signal hasn't reached yet.

So a memory never confirms itself. The program sorts everything the run
makes into three bins: confirmed (already in the memory, and made again
by this signal), added (new), and not seen this time (in the memory,
but this signal didn't make it). Nothing is removed.

The test is simple:

- The first half of Alice, with no memory: the run adds 14,079 parts.
- The second half, against that memory: the run confirms 10,588 parts
  and adds 9,337.
- The second half again: the run confirms 19,833 of the 19,925 parts
  the second half made the first time, and adds 0 parts at level 0 (5
  at level 1).
- The German text against the English memory: the run confirms 14,797
  parts (the short parts the two alphabets share) and adds 17,987 parts
  that English never made.

The fifth step is the first step, with a memory. The loop runs out of
new things the same way the levels do.

## 11. What a part "means" in a record

The record doesn't say what `the` means, what EXTEND does, or what a
German verb is. For each part, it holds that part's position in the web
of connections:

- what the part contains
- what contains the part
- what the part changes into
- what occurs next to the part

That position is what a part means, in the only sense the signal can
give. Two parts with the same position are the same thing under
different names. A part whose position is unlike any other part's is
unique.

This position is what makes the bridge work. The bridge is the same
comparison, run between two records instead of inside one. Run two
signals separately, say the German text and the English text from the
same day of debate, then compare the two pools against each other. A
part that occurs in both pools is *same* across the two languages. The
parts that contain it on each side are *different*.

For example, `technologi` occurs inside `technologische` and
`technologien` on the German side, and inside `technologies` and
`technological` on the English side. Nothing told either record about
the other. The shared parts are the bridge between the two languages,
and the parts that contain them show what each language builds on top.

The same matching method lets a system read its own output. Feed the
output back into the program, then compare the two records against each
other. The result is three bins: what came back the same, what was lost,
and what is new. The script `hybrid/loop.py` does this comparison by
hand on a text the program wrote by following its own what-comes-next
table (a walk of the model). The flag `--memory` does the same
comparison automatically on each later signal (section 10).

## 12. What the design leaves out on purpose

This program has one design principle. Build a machine as if it were one
millisecond old, with nothing but an input, an output, and its own code.
Define nothing, because the thing you tell the machine to look for might
not be the thing it needs to find.

So the program has:

- No file-type detection. The frame step *is* the detection.
- No character set. The lens is the setting that says how to draw the
  words as characters on the page, as ASCII letters for example, and it
  only comes into play after the core algorithm is finished. The core
  algorithm never looks at it.
- No stop-word list (a list of common words to ignore), no tokenizer (a
  rule for splitting text into words), and no stemmer (a rule for
  cutting a word down to its root). The separator is the most common
  word. The runs are what lies between the separators. The stems are
  what the mint found.
- No threshold that a person set by hand to fit an example. The one
  tolerance is the wobble you'd expect from random chance, and the
  program works it out from the number of rows.
- No training step, no weights, and no score to push up or down.
- No special code for bad input. A random file gives a frame table where
  every width scores about the same. The program then folds down to a
  frame of 1 bit and reports that frame as its result. The only things
  it refuses are at the input, and each refusal comes with a reason:
  - an option the program doesn't have
  - an option with no value
  - a memory that a run wrote at a different frame or in an older
    format

Two things were added after the first examples ran. Both are limits, not
new methods. The level loop came after these two, and the level loop is
a method.

1. The program compares a pair of neighbours only if one of the two is
   new since the last round. The result is the same, in half the time:
   Alice went from 4 seconds to 2.
2. A limit on the pool size (`--cap`, with a default of 1,000,000
   parts). On a very large signal, the limit stops the loop and says so
   in the record.

## 13. The four examples

| signal | word width found | separator | what the record shows |
|---|---|---|---|
| English novel (ASCII) | 8 bits. Column 0 is never 1. | the space | 73 symbols in order of frequency, the words, `+ed`/`+ing`, 22 verb stems |
| German debate (UTF-8 text, where some letters take more than one byte) | 8 bits. Column 0 is 1 in 3.6% of the words. | the space | the umlaut lead byte (a byte that occurs only before 4 other bytes), `+en`/`+ung`/`+lich`, `be+`/`ge+`, 52 verb stems, 42 adjective stems, pairs of words with capital letters |
| compiled C program | 64 bits. The column rates fall off from the first byte of each word to the last, which is how numbers look when their low byte is stored first (little-endian). At 8 bits, the strings. | zero | the layout of the file. At the byte level: `hello.c`, `strlen`, `puts`, `usage: hello TEXT`, the loader path, the compiler version |
| Apollo Lunar Module flight software, packed 15-bit | 15 bits (the program picked 60 first, then folded to 15) | EXTEND | the word width of the machine, the instruction prefix as the separator, `TC BANKCALL`, `TC INTPRET`, `TC PHASCHNG` with their argument words, `RETURN` as the part with the most connections |

Each example folder has the input, the record, and a breakdown that
explains each table.

## 14. How to build new things on Discovery

The guide `guides/building-from-discovery.md` does three things. First,
it names the eight things the program rests on, and for each one it
points to the place in the records where you can see that thing at
work. Second, it makes the case that those eight things are enough for
what the program does: each step is the comparator pointed at a target,
and so far no extension has needed a new operation.

Third, it gives three extensions in `extend/` that show the case:

- Cut a level at a class instead of at the most common word. The result
  shows what comes before and after a verb.
- A new kind of "same" for numbers in a range. Calls to PHASCHNG with
  any of its argument codes become one part.
- The comparator pointed at the activity of a neural net (its states),
  each row against the row before. The result shows the units that move
  together.

Each extension is a few lines on top of the main file. None of them
changes the mint, the crystal, or the levels.

The guide `guides/the-process.md` is the general method written out as
a procedure. It has eight steps, with a quick reference card at the top
and the reasons below. It covers what Discovery does and what it doesn't
do: it doesn't thin the data before comparing (ablation), and it doesn't
score with an outside measure. So someone applying the process to a
different problem knows where the choices are. At the bottom, the guide
gives a proof for each step that makes a claim:

- the split loses nothing
- thinning the data on both sides squares the loss, because a part has
  to survive both removals
- the comparator needs no outside score; it is its own scorer
- the loop always stops
- the program finds everything the sort order can show
- each part the program finds is real
- a removal is permanent

One point has to be clear: base Discovery records all the structure in a
signal that occurs more than once. It doesn't pick out one thing and
ignore the rest. If you need to find one specific target under heavy
noise and ignore everything else, you need one more signal to select
with. That selection signal can be:

- an answer key for the comparison
- an outside yes/no
- some other way of telling the program which parts matter to you

Discovery supplies the parts. The person using Discovery decides which
parts matter for a task.

## 15. Open ends

The file `notes/open.md` lists the things nobody has tried yet and the
things the records point to as the next things to try. The short list:

- separators the program chooses from the record itself, not by count
- a read of time in the core, each row against the row before,
  alongside the TIME tables that read the sequence of runs as time
- images, where the frame step meets a second dimension
- a read of the numbers on a trained net's connections (its weights),
  instead of the activity of an untrained one (the states of a
  reservoir)
- the bridge in the other direction: the changes two records share, not
  only the parts they share
- the baby model, where the loop is given the goal "keep the baby from
  touching the hot stove" (`paper/persistence.md`)
- the AGC in the loop, where the backward walk from a goal to the
  presses ran, but sorting the machine's instruction codes into stages
  by what each one causes did not run
