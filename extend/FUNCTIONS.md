# Functions: new words from Discovery's record

## What this is

Discovery reads *Alice in Wonderland* and writes a record of everything
it finds: the parts that repeat, what each part is made of, and the
changes that turn one part into another. That record is layer 0.

This program reads the record and tests two ideas. The first is that
the changes Discovery found can be used as functions, where a function
is a thing that takes a part and makes a new part from it. The second
is that those functions can make real English words that aren't in the
book, with nothing to guide them but yes-or-no answers from an answer
key.

Both ideas hold up. The output, `alice.functions.txt`, has the words
the program made, every try it made, and what each word cost in failed
tries. `run_examples.sh` regenerates `alice.functions.txt` (the 20-word
run), and `functions.output.txt` is what that run printed. The full run
is:

```
python functions.py examples/text/alice.txt 100
```


## Layer 0: the record

Discovery runs on `alice.txt` in the usual way, with no settings for
this task and no information about the signal. The record is
`examples/text/alice.txt.record.txt`. It has:

- the bytes and the record width
- the distinct words (the sequences between spaces)
- the parts in the pool. Discovery's mint step compares chunks that
  look alike and records what they share, making a new part from two
  parts that start or end the same way. The pool is where those parts
  are kept.
- the changes. Discovery's crystal step reads the pool and finds, for
  each part, what you would add to it to get another part. It's called
  the crystal because it groups the parts by which additions they
  accept.

A **change** is one of those additions: something Discovery found that
makes one part into another. For example:

- `+ed` makes `walk` into `walked`
- `m+` makes `are` into `mare`
- `+s` makes `cat` into `cats`

The changes are the raw material.


## Layer 1: functions

Not every change is a function. A change that was seen on only one
part is a one-off connection: it says something about that part, but
there's no reason to think it applies anywhere else. A change seen on
two or more parts acts as a function: something that takes one kind of
thing and makes another kind. The first line of `alice.functions.txt`
gives how many changes are in the record and how many of them count as
functions.

There's one more restriction, and it matters. Functions act only on
**whole runs**: parts that occur on their own in the text, so their
whole count (the number of times the part appeared as a complete chunk)
is above 0. Fragments like `e` or `ucked` are what changes are made of,
not what they act on.

The letter `e` is contained in more parts than almost anything else
(see PARTS BY DENSITY in the record), so it takes almost every change,
and so it tells you nothing about any one of them. With fragments
included, the number of functions and sibling pairs was many times
larger, the search took minutes, and it learned nothing new.

With whole runs only, there are orders of magnitude fewer pairs (the
count is on the first line `functions.py` prints), and the search
finishes in seconds.

Each function has an **in-kind**: the kind of thing it acts on. The
program learns it from the parts the function was seen on, by
collecting the other functions those parts also take. `+s` was seen on
many parts, and those parts also take `+ed`, `+ing`, `+'s` and others;
that set of functions is the in-kind of `+s`.

Each function also has an **out-kind**: the kind of thing it makes,
learned the same way from the parts it made. `+s` makes plurals, and
those plurals take `+,` and `+.` (word then comma, word then full
stop); that set of functions is the out-kind of `+s`. The function
table in `alice.functions.txt` lists each function's out-kind.


## Layer 2: siblings and paths

Two functions are **siblings** when two or more parts take both. `+s`
and `+ed` are siblings: many words take both. `+s` and `m+` aren't: no
word in Alice takes both `+s` and the prefix `m`.

The sibling links are the connections between functions. Their count
is on the first line of `alice.functions.txt`.

A **path** is one function after another. Apply `+s` to `ground` and
you get `grounds`. Now `grounds` is a part, and the program can try the
functions in the out-kind of `+s` on it. Paths are how the system
chains things together.


## How a word gets made

The system proposes applying a function to a part that doesn't already
have it, and it makes the proposal when the part takes siblings of that
function. If it does, the part looks like the kind of thing the
function acts on.

Each proposal gets a score, which the program calls its **standing**.
The score is the comparator run both ways:

- **Same**: the functions the part takes that are siblings of the
  proposed function and carry no flag.
- **Different**: the functions the part takes that are *not* siblings
  of the proposed function.
- **Standing = same - different.**

This is the key step. A part like `a`, `it` or `to` takes an enormous
number of changes, because it sits inside so many words. Its same count
is high, but its different count is high too. It matches everything, so
it isn't especially like any one thing.

A part like `a` gets a low score. A part like `are` takes a narrow set
of changes, the prefixes and suffixes that act on short stems like
verbs, and its siblings overlap heavily, so `are` gets a high score.

The system tries the highest score first. A score of 0 or below is not
proposed at all.


## Holds and flags

Each (function, sibling) pair carries a claim, which the program calls
a **hold**: "this function acts on the kind of thing that sibling acts
on". Every answer from the answer key is checked against it.

- **Yes** confirms the hold and clears any negative flag on it.
- **No** counts against the hold. Two no's with no yes set a
  **negative flag**: "this function does not act on the things that
  sibling acts on". The flag stays until the next yes clears it.

One level up, a whole **function** gets a flag in one case: the answer
key has refused its outputs twice and accepted none. That means the
function makes a kind of thing the answer key doesn't accept; `+,`
(word then comma) is the clearest case. Proposals from a flagged
function are ranked lower by the number of refusals. A yes clears the
flag.

A **seam** is the two characters where the change meets the part. If
that pair of characters never appears side by side anywhere in the
text, the seam counts one against the proposal. A yes that goes through
that seam clears the count.

Feedback acts on the thing making the proposals (the holds), not on the
record. The record is what Discovery found. The holds are what the
system has learned about how to use it.

The header of `alice.functions.txt` and its NEGATIVE FLAGS section give
two numbers: the negative flags at the end of the run, and the number
of whole functions carrying a flag.


## The words it made

None of these words are in Alice. The program checked each one against
`/usr/share/dict/american-english`. The MADE table in
`alice.functions.txt` lists each word with:

- the part and the function that made it
- the number of the try
- how many tries failed before it

Read the first rows. `are` takes many prefix functions, and those
prefixes are siblings of each other, so the system proposes `m+`, `t+`,
`f+`, `p+`, `r+` and `b+` on `are` with a high score. Most of them are
right, and once the first is confirmed the rest follow quickly, because
the holds are already set.

Read the later rows: suffixes on longer stems, and prefixes on whole
words (`d+` on `reading`). The system was never told what a prefix or a
suffix is. It found them as changes in the record, and then learned
which changes act on the same kinds of parts.


## The function table (the final output)

The compact output is THE FUNCTION TABLE in `alice.functions.txt`. It's
the result, not the search. For each function it gives:

- how many parts the function was seen on
- how many words it made
- how many refusals it got
- its sibling links
- its flagged pairs
- its out-kind

Read `+s`: the most words made and the most refusals. Its out-kind is
`+,`, `+.`, `+\n`: what `+s` makes usually comes right before
punctuation. That's right; plurals often end clauses.

Read the flagged functions. Most are punctuation attachments: `+,`
(word then comma), `\n+` (newline then word), `+.` (word then full
stop). They're genuine functions of the text, because they were seen on
real parts, but what they make isn't an English word on its own. The
system learned that from the failures.


## The cost

The header of `alice.functions.txt` gives the number of failed tries,
the total tries, and the time, split three ways: reading the record,
building the function table, and the search.

The failures are the evidence that the feedback is working. Read the
"failed before it" column of the MADE table from top to bottom. Each
early word cost many failures. As flags accumulate, the system skips
most of the bad proposals. Some words still cost many tries, because
their stem takes an unusual set of changes that the flags haven't
narrowed down yet.

The log of every try (EVERY ATTEMPT) stays in the output as the price
of finding the function table.


## Each part, as an idea

Each piece of this system is one idea at a different scale:

- A **function** is a unit of computation (the repository's word for
  this is a compulon): it accepts one kind of thing, its in-kind, makes
  one kind of thing, its out-kind, and refuses the rest.
- A **hold** on a (function, sibling) pair is a claim held open. A yes
  confirms it, a no from the comparator weakens it, and at any moment
  it's the current best estimate that the pair is real.
- A **negative flag** is a hold's record of what something is NOT. It
  has a condition that sets it (two no's, no yes) and a condition that
  clears it (a yes).
- **Standing** is the comparator run both ways, same minus different:
  one number for how much a part looks like the kind of thing a
  function acts on.
- **Layers**: the record is layer 0, the functions are layer 1, and the
  siblings and paths are layer 2. Each layer keeps a running total that
  it updates.
- **Feedback** changes the thing making the proposals (the holds), not
  the record. That makes it feedback, not recurrence: the record is
  never fed back into itself. The record is what Discovery found; the
  holds are what's known about the things that act on it.


## The earlier methods

There were three earlier methods, each a step closer to this one. The
measure for all of them is the cost: how many tries failed for each
word a method made.

**Open proposals** (no feedback). Discovery's class pairs are the
proposals, and the answer key accepts or refuses each one. The method
has no memory of its failures, and it had the most of them.

**Feedback per ending**. This records each refusal against its ending:
`+,` was refused on this stem. It was worse than no feedback at all,
because the feedback was too narrow: a refusal of `+,` said nothing
about `+.'` or `+;`. What was needed was a group, not a list.

**Negative groups** (at the symbol level). This groups the refused
changes by what they share, so the punctuation endings all land in the
same negative group after a few refusals. Far fewer failures. But the
feedback was bolted on from outside, not part of the structure.

**Functions** (this version). The changes are the functions, the record
is the connections, and the feedback is holds on those connections.
About the same failure rate as negative groups, in less than half the
time, and the system is the structure itself rather than a patch on top
of it.


## What it couldn't do

The run that tested two-step paths (a function applied to the output of
another function) tried a few dozen of them, and none succeeded. The
out-kinds point mostly at punctuation functions, and those are flagged.
For paths to work, the out-kind has to carry more than what the crystal
found in the original text: it has to carry the functions that the
*new* words take, and it has to be updated every time the program makes
a new word.

An out-kind that updates is the next layer.
