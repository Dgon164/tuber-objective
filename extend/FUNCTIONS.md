# Functions: making words from what Discovery found

## What this is

Discovery reads *Alice in Wonderland* and writes a record of everything
it finds — the parts, what each is made of, what changes turn one part
into another. That record is layer 0.

This program reads that record and asks: can Discovery's own changes
become functions — things that take a part and make a new part — and can
those functions, guided only by feedback from an answer key, create real
English words that were not in the original text?

The answer is yes. The words it made, every attempt it took, and what it
cost are in its output: `alice.functions.txt`, which `run_examples.sh`
regenerates (the 20-word run; `functions.output.txt` is what the run
printed). For the full run:

```
python functions.py examples/text/alice.txt 100
```


## Layer 0: the record

Discovery runs on `alice.txt` exactly as it always does. No parameters
set for this task, no hints about what the signal is. The record is
`examples/text/alice.txt.record.txt`: the bytes and the frame, the
distinct words (runs between spaces), the parts in the mint pool, and
the changes the crystal found.

A **change** is what Discovery found that turns one part into another:
`+ed` turns `walk` into `walked`, `m+` turns `are` into `mare`, `+s`
turns `cat` into `cats`. These are the raw material.


## Layer 1: functions

Not every change is a function. A change that was seen on only one part
is a connection — it tells you about that part, but it can't generalize.
A change seen on two or more parts acts like a function: it takes one
kind of thing and makes another kind. How many changes the record has
and how many of them are functions is the first line of
`alice.functions.txt`.

One more restriction, and it matters. The functions act on **whole
runs** — parts the signal stood up on their own (their whole count is
above zero). Fragments like `e` or `ucked` are what changes are made of,
not what they act on. The letter `e` sits inside more parts than almost
any other (PARTS BY DENSITY in the record). It takes nearly every change
and so says nothing about any one of them. Including fragments
multiplied the functions and the sibling pairs many times over — the
search took minutes and learned nothing. Restricting to whole runs cut
the pairs by orders of magnitude (the count is on the first line
`functions.py` prints) and the search finishes in seconds.

A function's **in-kind** is learned from the parts it was seen on: the
other functions those parts also take. `+s` was seen on many parts;
those parts also take `+ed`, `+ing`, `+'s`, and so on. That is `+s`'s
in-kind.

A function's **out-kind** is the functions seen applied to what it made.
`+s` made plurals; those plurals were seen to take `+,` and `+.` (word
then comma, word then period). That is `+s`'s out-kind. The function
table in `alice.functions.txt` lists each function's out-kind.


## Layer 2: siblings and paths

Two functions are **siblings** when two or more parts take both. `+s`
and `+ed` are siblings — many words take both. `+s` and `m+` are not —
no word in Alice takes both `+s` and a prefix `m`.

The sibling links are the wiring; their count is on the first line of
`alice.functions.txt`.

A **path** is one function after another: apply `+s` to `ground`, get
`grounds`; now `grounds` is a part, and the functions in `+s`'s out-kind
can be offered on it. Paths are how the system chains.


## Making a word

The system offers a function on a part that doesn't already have it. The
offer is made when the part takes siblings of that function — it looks
like the kind of thing that function acts on.

Each offer gets a **standing**, and standing is the comparator run both
ways:

- **Same**: the functions the part takes that are unflagged siblings of
  the offered function.
- **Different**: the functions the part takes that are *not* siblings of
  the offered function.
- **Standing = same − different.**

This is the key step. A part like `a` or `it` or `to` takes a great
many changes because it sits inside many words. Its same count is high
— but so is its different count. It agrees with every function and is
like none of them. It scores low. A part like `are` takes a focused set
of changes — prefixes and suffixes that act on short verb-like stems.
Its siblings overlap heavily. It scores high.

Highest standing first. Zero or below is not offered.


## Holds and flags

Every (function, sibling) pair is a **hold**: "this function takes the
kind of thing that sibling takes." Each answer reads against it.

- **Yes** sets the hold and resets any negative flag on it.
- **No** counts against it. Two noes with no yes raise a **negative
  flag**: "this function does not take what that sibling takes." The flag
  is held, and reset by the next yes.

One size up: a **function** whose outputs have been refused twice and
never accepted is flagged — it emits a kind the answer key does not
accept. `+,` (word then comma) is the clearest case. Its offers stand
lower by its refusal count. Reset by a yes.

A **seam** the signal never shows — the two-character boundary where the
change meets the part, if that pair never sits side by side anywhere in
the signal — counts one against the offer. Reset by a yes that passes
through that seam.

Feedback acts on the producer (the hold), not on the record. The record
is what was found. The holds are what was learned about how to use it.

How many negative flags stand at the end, and how many whole functions
are flagged, is in the header and the NEGATIVE FLAGS section of
`alice.functions.txt`.


## What it made

Words not in Alice, checked against `/usr/share/dict/american-english`.
The MADE table in `alice.functions.txt` lists each one with the part and
the function that made it, the attempt it came on, and how many failed
attempts came before it.

Read the first rows: `are` takes many prefix-functions and they are
siblings of each other, so `m+`, `t+`, `f+`, `p+`, `r+`, `b+` are all
offered on `are` with high standing, and most of them work. Once the
first of them succeeds, the next ones follow at once — the holds were
set.

Read the later rows: suffixes on longer stems, and prefix functions on
whole words (`d+` on `reading`). The system didn't know what a prefix or
suffix is; it found them as changes in the record and learned which ones
take the same kinds.


## The function table (what ships)

The compacted output: THE FUNCTION TABLE in `alice.functions.txt`. This
is what was found, not the search. For each function: how many parts it
was seen on, how many words it made, how many times it was refused, its
sibling links, its flagged pairs, and its out-kind.

Read `+s`: the most words made and the most refusals; an out-kind of
`+,`, `+.`, `+\n` — its outputs tend to come before punctuation. That
is correct: plurals often end clauses.

Read the flagged functions: mostly punctuation attachments — `+,` (word
then comma), `\n+` (newline then word), `+.` (word then period). They
are functions of the signal — they were seen on real parts — but their
outputs are not standalone English words. The system learned that by
failing.


## The cost

The header of `alice.functions.txt` has the count of failed attempts,
the attempts in all, and the time, split into the record, the function
table, and the search.

The failures are the evidence that the feedback works. Read the "failed
before it" column of the MADE table from top to bottom: the early words
cost many failures each, and once the flags accumulate most bad offers
are skipped. Some words still cost many attempts, where the stem takes
an unusual set of changes the flags hadn't narrowed yet.

The attempt log (EVERY ATTEMPT) is kept as the cost of finding the
function table.


## What each piece is, in the theory

Each piece of this system is one idea used at a different scale:

- A **function** is a compulon: it accepts one kind (its in-kind),
  emits one kind (its out-kind), and refuses the rest.
- A **hold** on a (function, sibling) pair is a hold: set by yes, reset
  by the comparator's no, current best assessment of whether that pair
  is real.
- A **negative flag** is a negative flag: held information about what
  something is NOT, with set (two noes, no yes) and reset (a yes).
- **Standing** is the comparator run both ways, same minus different —
  a number that means "how much does this part look like the kind of
  thing this function takes?"
- **Layers**: the record is layer 0, functions are layer 1, siblings
  and paths are layer 2. Each keeps a running total.
- **Feedback** changes the producer (the hold), not the record. That is
  feedback, not recurrence — the record is what was found; the holds
  are what was learned about what works.


## What was tried before this

Three earlier approaches, each one closer. The cost — failed attempts
per word made — is the measure of each.

**Open offers** (no feedback). Discovery's class-pairs as offers,
accepted or rejected, no memory of what failed. `make_words.py` is this
approach, kept for comparison. The most failures.

**Per-ending feedback**. Track refusals per ending: `+,` refused on
this stem. Worse than no feedback. The feedback was too narrow: a
refusal of `+,` taught nothing about `+.'` or `+;`. It needed to
build a group, not a list.

**Negative groups** (symbol-level). Group the refused changes by what
they share. Punctuation endings enter the same negative group after a
few refusals. Far fewer failures — but the feedback was bolted on, not
built from the structure.

**Functions** (this). The changes are the functions. The record is the
wiring. The feedback is holds on the wiring. About the cost of the
negative groups in failures, in less than half the time, and the system
is the structure, not a patch on it.


## What it doesn't do yet

Two-step paths (a function of a function's output) were attempted a
few dozen times with no successes in the run that tested them. The
out-kind mostly points at punctuation functions, which are flagged. For
paths to work, the out-kind needs to carry more than what the signal's
crystal saw; it needs what the *made* words take, updated as words are
made.

That is the next layer.
