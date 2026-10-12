# Discovery

*A learning subroutine made of one comparator and a memory*

Jason Weeks — Project Discovery, October 2026 — thetuberobjective@gmail.com

## 1. What it is

Discovery takes any file, reads it as raw bits, and writes down
everything it finds: the parts, what each part is made of, what
contains it, what shows up before and after it, and what you'd change
to turn one part into another. It doesn't know what kind of file it's
looking at. It has no dictionary, no grammar, no list of file types,
and no training step. The same one file of Python reads an English
novel, a German parliamentary debate, a compiled program, and the
15-bit flight software of the Apollo Lunar Module — and writes a record
of each one.

This paper explains how the system works and why it's built the way it
is. It doesn't make claims about what the system can do beyond what the
four example records in `examples/` show. Those records are the
evidence; this is the explanation.

## 2. Where the comparator came from

Discovery started from reservoir nets — small random neural networks
that are never trained. The finding, over many experiments, was that
simpler was always better. A smaller net worked better than a bigger
one. So the net got reduced: many layers to one layer. Floating-point
numbers to integers. Integers to smaller integers. Smaller integers to
binary. Binary to boolean.

What came out the other end was the core of the whole system: A is not
B. A boolean operation in the smallest possible net gives you the
finest resolution of information you can get with a computer — one bit,
one comparison, yes or no. And from that single operation, everything
else self-assembles: the parts, the connections, the classes, the
levels. The comparator finds what is the same and what is different.
The memory holds what it found. And from those two pieces, structure
builds itself up through the same logic used in basic Hebbian learning
— things that show up together get connected.

That is why the program has no training step, no gradient, no
optimization. The net was reduced until there was no net left — just
the comparison that every net is made of.

## 3. The one tool

The entire system is built on one operation: compare two things, and
split the result three ways.

- **Same** — the part the two share.
- **Different** — what's left of each one after you remove the shared part.
- **Not part** — everything the comparison never touched.

That's the comparator. The other piece is a memory — a place to keep
what the comparator has already seen, so there's something to compare
the next thing against.

That's the whole kit. A comparator with nothing in memory can only tell
you something is there. A comparator with one thing in memory can tell
you whether the next thing matches, and if not, which part is different.
From there, every step in the program is the same comparator run again
on what it already produced.

Here's how that one operation shows up at every level of the program:

| step | what two things are compared | what's the same | what's different |
|---|---|---|---|
| frame | a column of bits, and that same column shifted one row down | a column that stays the same | a column that changes |
| levels | a run and its neighbour one level up | the same run, or runs of the same kind | whatever's left over |
| words | a word and every other word | the same word showing up again (counted) | a different word |
| mint | two neighbours in the sorted pool | the head (or tail) they share | the two leftover pieces |
| crystal | a part and its larger containing parts | the part itself | the change that turns it into the larger part |
| classes | two parts and their sets of changes | the same set of changes | a different set |
| bridge | a part in one record and all the parts in another record | a part that appears in both | its containing parts on each side |

Nothing else is introduced. When a step looks like it has its own idea
— a "frame" or a "separator" or a "class" — that idea is just a name
for what the comparator's output looks like at that point.

## 4. Why bits

Everything a computer stores is bits — ones and zeroes. A text file, a
program, a picture, a sound recording, a database — all of them are a
string of bits that some program reads in chunks of a certain size. The
chunk size is an agreement between whoever wrote the file and whoever
reads it. It's not written in the bits themselves. ASCII text uses
8-bit chunks with 7 bits actually used. A compiled program on a modern
computer has 64-bit sections and 8-bit strings mixed together in the
same file. The Apollo Guidance Computer used 15-bit chunks, and when
its memory is packed into a file, none of those chunks even lines up
with byte boundaries.

Reading everything as bits means the program can't be told the chunk
size — it has to figure it out. That's a cost: a text file could have
been read as bytes right away. But you pay that cost once, in the frame
step, and it buys you everything else: one input path, one mechanism,
no special code for each format, and a program that reads a 15-bit
machine from 1969 without any changes.

## 5. The frame (finding the chunk size)

Imagine laying all the bits out in rows of some width *w*. Each column
is every *w*-th bit in the file. If you pick the right width, each
column has its own pattern: the top bit of an ASCII byte is never 1;
the next bit down is almost always 1. If you pick the wrong width, the
bits get scrambled across columns, and every column ends up around 50/50.

The score for a width is the gap between the column that's 1 most
often and the column that's 1 least often. Plain text at width 8 scores
0.95. Plain text at width 7 scores 0.05. The width with the biggest
gap wins, with one rule: a wider width only wins if it beats the
narrower one by more than random chance would explain.

There's one more step: folding. A width of 60 looks almost as good as
a width of 15, because 60 is just four copies of 15 side by side. So
after picking a width, the program checks every number that divides
evenly into it. If the smaller width's column pattern is just the
bigger width's pattern repeated, the smaller one is the real answer.
This is exactly what happened with the Apollo flight software: the
program first picked 60, then noticed it was just 15 repeated four
times, and folded down to 15.

The frame step is the only place in the program that uses a tolerance
(a "close enough" check), and that tolerance is calculated from the
data — the number of rows — not chosen by hand.

## 6. Words, the separator, and runs

Now that the program knows the chunk size, it cuts the bits into words
of that width. It counts how often each word appears. It counts which
words show up next to which other words.

The most common word is the separator. A run is everything that sits
between two separators.

Using the most common word as the separator is a deliberate choice — it's
the simplest rule that works. In text, it gives you the space character.
In a compiled program, it gives you the zero byte. In the Apollo rope,
it gives you EXTEND (the most common instruction prefix). Each of those
is a reasonable place to cut.

When a signal has more than one good cutting point, the record will show
the others as high-frequency parts that never appear on their own. The
`--separators N` flag lets you cut at the N most common words instead.

## 7. The mint (finding the shared pieces)

The pool starts as every distinct run. The mint smashes the pool against
itself over and over until nothing new comes out:

1. Sort the pool. Two neighbours in sorted order share the longest
   beginning that either of them shares with anything else in the pool.
2. For each pair of neighbours that share a beginning: make three new
   parts — the shared beginning and the two leftovers. Write down that
   each original is *made of* its pieces and each piece is *part of*
   the originals. The new parts join the pool.
3. Flip every part backwards and do the same thing. This finds shared
   endings.
4. If this round made nothing new, stop. Otherwise go back to step 1.

Nothing is ever removed. Each part keeps a count of how often it
appeared as a complete run, and a density — how many other parts it
sits inside of. The letter `e` is never a complete word in Alice, but
it sits inside 1,615 parts. The word `the` appears as a complete word
1,340 times and sits inside 178 other parts. The word `walk` appears
4 times and sits inside 4 parts.

Three rules from the larger project this was distilled from:

- *Keep smashing things together until nothing new comes out.* The loop
  runs until it reaches a stable state. The stable state is the stopping
  rule, not a round limit.
- *Rare but real is worth keeping.* A part made from a single collision
  has the same standing as a part made from a thousand. Nothing fades
  away.
- *Store each thing once with a count, not a thousand copies.* The pool
  has one entry per distinct part, with a number saying how many times
  it appeared. That's the only compression done.

## 8. The crystal (grouping by what changes)

The pool is the raw memory. The crystal is a second table that reads
the pool and groups parts together without losing any detail — dedup.

Here's how it works. For any part, a *change* is the piece that turns
it into one of its containing parts. For example, `walk` becomes
`walked` by adding `+ed`. The set of changes a part takes is a property
of that part. Parts that take the same set of changes form a *class*.

In Alice, 22 stems take both `+ed` and `+ing` — that's the class
`{+ed, +ing}`. A grammar book would call these verbs. The record calls
them by their set of changes, because that's the only label the signal
itself supports.

In the German text, the class `{+en, +t}` has 52 members (verb stems)
and `{+n, +r}` has 42 (adjective stems).

The crystal's last table is like a dictionary entry for each common run:
what it's made of, what contains it, its changes, what comes after it,
what comes before it. The entry says: *this run is X; the change from X
to Y is Z; X shows up next to these other things.* That sentence is the
whole form of the knowledge the record holds, and every piece of it
comes with a count.

## 9. Crystallize, then loop again, until nothing changes

The crystal makes structure. If the system stopped there, it would make
structure and then never use it — stopping one step short of its own
rule. So it uses what the crystal just made in the next round, and
nothing gets replaced — everything gets added.

A level means: count the symbols, cut runs at the most common one,
mint, crystallize. The next level's sequence of symbols is this level's
runs, as they are. This level's classes become a second way two symbols
can count as "the same": either the exact same run, or two runs that
belong to the same class. Every structure the new level makes — a run
of runs, a minted part, a class — joins the one shared pool, and its
connections land on the parts it's made of wherever they live. So a
word that sits inside forty stretches one level up gains forty to its
density count.

The loop keeps going until a level has only a single run left, which
can't be cut. The additions reach zero well before that.

Each level's sequence is shorter than the one before, because the
separator is always present and gets cut out, so the loop can't run
forever. And it doesn't run long. The pool only grows, and the growth
runs out:

- Alice: 22,446 parts, then 6,709 more, then 5, then 1, then stable.
- German text: 19,210, then 14,943, then 9, then 1.

What does level 1 actually look like? In Alice, level 1 cuts at `the`
(the most common level-0 run). Its runs are the stretches between one
`the` and the next. What shows up right before `the`: `said`, `and`,
`to`, `of`. In the German text, level 1 cuts at the comma; its most
repeated stretches are the forms of address. In the Apollo assembly
source, level 1 cuts at the comment mark `#`; its densest parts are
instruction sequences like `TC BANKCALL`, `CAF ZERO`, `CCS A`; and
how the programmers started a comment: `TO`, `FOR`, `IN`, `IF`, `AND`,
`SET`.

## 10. The five steps, and the fifth one

The steps of understanding something, said plainly:

1. **Identification** — drawing the border. "This is a thing, separate
   from the background."
2. **Association** — connecting it to what you know. "This looks like
   that one I remember."
3. **Reduction** — stripping it down. "What are the basic pieces?"
4. **Composition** — putting it together. "How do the pieces fit
   together to make the whole?"
5. **Evaluation** — checking the result. "Does the thing I built
   actually match what's out there?"

Where each one lives in the file:

| step | where it is in the program |
|---|---|
| identification | the frame step and the separator: the most common word is the background, and a run is what sits between two of them; one level up, the same thing again |
| association | the sort: a part's neighbour in sorted order is the thing in memory that most looks like it from the front; flipped, from the back. Also FOLLOWS and, one level up, matching by class |
| reduction | the mint loop, run until nothing new comes out; the shared cores sorted out from the leftovers, with the leftovers kept |
| composition | made_of, part_of, the crystal entry, the classes, the levels |
| evaluation | the comparator again — pointed at the model's own output instead of at a new part |

Evaluation is not a separate mechanism. "Does the model match reality?"
and "Is this the same as that?" are the same question, and the
comparator answers both. What was missing at first was not the
comparison itself but the loop: a run would read one signal, build the
pool, and stop — so the final comparison never became the starting
point of the next round.

### The same steps, said the other way: roots, layers, interactions, crystals, relations, causes

The five steps are one operation pointed at different places and
scales. The same list in the words we use when we talk about what the
system finds, with where each one lives:

| find the | which is | where it is | at which scales |
|---|---|---|---|
| roots | identification | the frame (the word width, from the bits); the separator (the most common word); PARTS BY DENSITY (what everything else is made of); the stems in a class | bits, words, parts; across signals (memory's *confirmed*); across records (`bridge.py`, the shared parts) |
| layers | composition | the levels: runs of runs into the one pool, `made_of` and `part_of` across levels | every level; memory keeps the levels |
| interactions | association | FOLLOWS and RUN FOLLOWS at every level; the sorted neighbour; the new signal against memory; `extend/same_slot.py`, `extend/sentence.py` | every level; across signals |
| crystals | reduction | CLASSES: the same set of changes; a class counts as same one level up; `extend/functions.py`'s siblings | every level; the functions |
| relations | composition | the changes (`+ed`, `un+`); the classes; in-kind, out-kind and paths in `extend/functions.py`; `bridge.py`'s parents on each side | parts, functions, across records |
| causes | evaluation, with time | TIME: the sequence read as time — ARROWS (a pair seen both ways, and which way wins), EFFECTS (what comes after a part more than it comes at all), CHAINS (the strongest effect followed forward); then `examples/agc-live/`: press, record, compare — the effect that is only there after the press | every level of a passive signal; across a *do* on the running machine |

Time is in the signal from the start: the signal is in order, and the
order is time. FOLLOWS was always a reading of it. The TIME tables
read it three more ways, each the comparator pointed along the
sequence: before against after. The TIME tables at level 0 of
`examples/text/alice.txt.record.txt` show it on the novel: the arrows
among the words (`said -> Alice`, `if -> you`, `I -> shall`, each with
its count each way), the effects of `I`, of `a`, of `little`, and the
chains. The same tables in `examples/agc/luminary099.rope.record.txt`
show the instruction flow, with chains that loop back through it. None
of that is a cause
yet. A cause is an arrow that holds across a *do*: `examples/agc-live/`
presses a key, records every signal, and compares the run with the
press against the run without it; the effect that is only there after
the press (engine on → thrust, propellant, accelerometer, 13 of 13) is
the causal structure, and `walk.py` runs it backward from a goal to the
presses that reach it. Same comparator, same tables; the *do* is the
only thing added.

Grouped the way a program is, these are three subroutines:

- **Interpret** (input): takes the signal in and applies identification
  and association — the frame, the separator, the sort.
- **Evaluate** (process): runs reduction, composition, and "this is not
  that" to sort the noise out and build the model — the mint, the
  crystal, the levels, and the comparison against memory.
- **Act** (output): does something with the result. In this program,
  the act is two things: the record gets written, and the memory gets
  updated. The memory update is the program acting on itself based on
  its own evaluation. That's the only action it takes. Acting on
  anything else is another system's job — that's what the hybrid systems
  guide is for.

Memory closes the loop. With `--memory FILE`, the pool is saved after a
run and loaded before the next one. The remembered parts sit in the
sorted pool right next to the new signal's runs, so a new run gets
compared against what's remembered as well as against the rest of the
signal. A comparison counts only when the new signal is in it: two
remembered parts it has not reached are left alone, so a memory never
confirms itself. Everything the run produces gets sorted into three
bins: confirmed, added, and not seen this time. Nothing gets removed.

The test is simple:

- First half of Alice, from nothing: adds 14,079 parts.
- Second half, against that memory: confirms 10,588 and adds 9,337.
- Second half again: confirms 19,833 of the 19,925 it produced the
  first time and adds 0 at level 0 (5 at level 1).
- German text against the English memory: confirms 14,797 (the short
  parts the two alphabets share) and adds 17,987 that English never
  produced.

The fifth step is the first step with memory, and the loop runs out
of new things the same way the levels do.

## 11. What "meaning" is in a record

The record doesn't say what `the` means, what EXTEND does, or what a
German verb is. What it holds for each part is its position in the web
of connections: what it's made of, what contains it, what it changes
into, what shows up next to it.

A part's meaning, in the only sense the signal provides, is that
position. Two parts with the same position are the same thing under
different names. A part whose position is unlike any other's is unique.

This is why the bridge works. Run two signals separately — the German
and the English of the same day of debate — then smash the two pools
together. A part that appears in both is *same* across the two
languages; its containing parts on each side are *different*.

For example: `technologi` appears inside `technologische` and
`technologien` on the German side, and inside `technologies` and
`technological` on the English side. Nothing told either record about
the other. The shared parts are the bridge between the two languages,
and the containing parts are each language's way of building on them.

This same collision is how a system can read its own output: run the
output back through, smash the two records together, and get three
bins — what came back the same, what was lost, what's new. `hybrid/
loop.py` does this by hand on a walk of the model; `--memory` does it
automatically on every signal that follows (section 10).

## 12. What was left out on purpose

The stance this program was built on: build a machine born one
millisecond ago, with nothing but input, output and its own code.
Define nothing — because what you tell it to look for may not be what
it needs to find.

So there is:

- No file-type detection — the frame step *is* the detection.
- No character set — the lens draws letters on the page after the fact,
  and the core algorithm never looks at it.
- No stop-word list, no tokenizer, no stemmer — the separator is the
  most common word, the runs are what sits between, the stems are what
  the mint found.
- No threshold set by hand to fit an example — the one tolerance is the
  random-chance wobble, computed from the number of rows.
- No training, no weights, no objective function.
- No error handling on bad input — a random file gives a flat frame
  table and folds to a frame of one bit, and that's reported as found.
  The only refusals are at the door, each with its reason: an option
  the program doesn't have, a value left off, a memory written at
  another frame or in an older format.

Two things were added after the first examples ran, both limits rather
than new methods (the level loop was added after them, and that is
method):

1. A pair of neighbours is only compared when one of them is new from
   the last round. Same result, half the time. (Alice went from 4
   seconds to 2.)
2. A cap on pool size (`--cap`, defaults to 1,000,000 parts) that stops
   the loop on a very large signal and says so in the record.

## 13. The four examples

| signal | word size found | separator | what the record shows |
|---|---|---|---|
| English novel (ASCII) | 8 bits — column 0 never on | the space | 73 symbols, their frequency order, the words, `+ed`/`+ing`, 22 verb stems |
| German debate (UTF-8) | 8 bits — column 0 on 3.6% | the space | the umlaut lead byte (only appears before four others), `+en`/`+ung`/`+lich`, `be+`/`ge+`, 52 verb stems, 42 adjective stems, capitalized pairs |
| compiled C program | 64 bits with little-endian fall-off; at 8 bits, the strings | zero | the file's layout; at the byte level: `hello.c`, `strlen`, `puts`, `usage: hello TEXT`, the loader path, the compiler version |
| Apollo LM flight software, packed 15-bit | 15 (picked 60 first, folded) | EXTEND | the machine's word size; the instruction prefix as separator; `TC BANKCALL`, `TC INTPRET`, `TC PHASCHNG` with their argument words; `RETURN` as the most connected part |

Each example folder has the input, the record, and a breakdown that
walks through every table.

## 14. Building from it

`guides/building-from-discovery.md` lays out the eight things the
program rests on, each with the place in the records where you can see
it working; the case that those eight things are enough for what the
program does (every step is the comparator pointed somewhere, and no
extension so far has needed a new operation); and three extensions built
to show it, in `extend/`:

- Cut a level at a class instead of the most common word — what shows
  up before and after a verb.
- A new kind of "same" for numbers within a range — calls to PHASCHNG
  with any of its argument codes smash into one part.
- The comparator pointed at consecutive rows of a net's states — which
  units move together.

Each is a few lines on top of the main file, and none of them changes
the mint, the crystal, or the levels.

`guides/the-process.md` is the general method written as a recipe: eight
steps, with a quick reference card at the top and the reasoning below.
It covers what Discovery does and what it doesn't (ablation, external
scoring), so someone applying the process to a different problem knows
where the choices are. At the bottom are proofs for each step that makes
a claim: the split is lossless, ablation from both sides squares the
loss, the comparator is its own scorer, the loop always stops, it finds
everything the sorted order can show, every part it finds is real, and
deletion is irreversible.

One distinction worth stating plainly: base Discovery records all
recurring structure in a signal. It doesn't pick out one thing and
ignore the rest. If you need to isolate one designated target buried
under heavy noise — find a specific pattern while ignoring everything
else — you need an additional selection signal: an answer key to compare
against, an external yes/no, or some other way to tell the system which
parts you care about. Discovery supplies the components; which ones
matter for a given task is supplied by whoever is using it.

## 15. Open ends

`notes/open.md` lists what hasn't been tried and what the records
suggest trying next. The short version: separators chosen from the
record itself rather than by count; the row-against-the-row-before
reading of time in the core, next to the TIME tables, which read the
sequence of runs as time; images, where the frame step meets a second
dimension; reading a trained net's weights instead of a reservoir's
states; the bridge in the other direction — shared changes between two
records, not only shared parts; the baby model, the loop given "keep
the baby from touching the hot stove" (`paper/persistence.md`); and the
AGC in the loop, where the walk has run and the opcodes-by-effect
stages have not.
