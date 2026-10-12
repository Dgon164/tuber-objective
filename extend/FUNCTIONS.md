# Functions: making words from what Discovery found

## What this is

Discovery reads *Alice in Wonderland* and writes a record of everything
it finds — the parts, what each is made of, what changes turn one part
into another. That record is layer 0.

This program reads that record and asks: can Discovery's own changes
become functions — things that take a part and make a new part — and can
those functions, guided only by feedback from an answer key, create real
English words that were not in the original text?

The answer is yes. 100 new English words, 985 failed attempts, 6.3
seconds total.

```
python functions.py examples/text/alice.txt 100
```


## Layer 0: the record

Discovery runs on `alice.txt` exactly as it always does. No parameters
set for this task, no hints about what the signal is. The result:

- 144,395 bytes, 8-bit words, space is the separator
- 6,466 distinct English words (runs between spaces)
- 22,446 parts in the mint pool
- 5,935 changes found by the crystal

A **change** is what Discovery found that turns one part into another:
`+ed` turns `walk` into `walked`, `m+` turns `are` into `mare`, `+s`
turns `cat` into `cats`. These are the raw material.


## Layer 1: functions

Not every change is a function. A change that was seen on only one part
is a connection — it tells you about that part, but it can't generalize.
A change seen on two or more parts acts like a function: it takes one
kind of thing and makes another kind.

The filter: 5,935 changes in the record, 1,734 are functions.

One more restriction, and it matters. The functions act on **whole
runs** — parts the signal stood up on their own (their whole count is
above zero). Fragments like `e` or `ucked` are what changes are made of,
not what they act on. The letter `e` sits inside 1,615 parts. It takes
nearly every change and so says nothing about any one of them. Including
fragments gave 13,109 functions and 6.8 million sibling pairs — the
search took minutes and learned nothing. Restricting to whole runs gave
1,734 functions and 184,278 pairs. The search finishes in seconds.

A function's **in-kind** is learned from the parts it was seen on: the
other functions those parts also take. `+s` was seen on 167 parts; those
parts also take `+ed`, `+ing`, `+'s`, and so on. That is `+s`'s in-kind.

A function's **out-kind** is the functions seen applied to what it made.
`+s` made plurals; those plurals were seen to take `+,` and `+.` (word
then comma, word then period). That is `+s`'s out-kind.


## Layer 2: siblings and paths

Two functions are **siblings** when two or more parts take both. `+s`
and `+ed` are siblings — many words take both. `+s` and `m+` are not —
no word in Alice takes both `+s` and a prefix `m`.

25,992 sibling links in all. These are the wiring.

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

By the end: 1,379 negative flags. 245 whole functions flagged (outputs
refused 2+, never accepted).


## What it made

100 words not in Alice, checked against `/usr/share/dict/american-english`.

The first few and what made them:

```
  word        part    function    attempt#   failed before it
  mare        are     m+              30     23
  tare        are     t+              31      0
  fare        are     f+              32      0
  ham         am      h+              38      5
  pare        are     p+              63     24
  rare        are     r+              69      5
  bare        are     b+              70      0
  fate        ate     f+              81     10
  fend        end     f+              83      1
  offed       off     +ed             88      4
  cone        one     c+              91      2
  tour        our     t+             118     26
```

`are` takes many prefix-functions and they are siblings of each other.
So `m+`, `t+`, `f+`, `p+`, `r+`, `b+` are all offered on `are` with
high standing. Most of them work. After `mare` succeeds (attempt 30),
the next three follow immediately — the holds were set.

Later words come from suffixes on longer stems:

```
  tailing     tail    +ing           411     75
  answering   answer  +ing           694      4
  drying      dry     +ing           786     81
  dreading    reading d+            1041      3
  buttering   butter  +ing          1058      2
```

`dreading` is `d+` applied to `reading` — a prefix function on a whole
word. The system didn't know what a prefix or suffix is; it found them
as changes in the record and learned which ones take the same kinds.


## The function table (what ships)

The compacted output. This is what was found, not the search.

```
  function   seen on  made  refused  siblings  flags
  +s             167    33       46       625     29
  +'s             50    21       11       103      2
  +ing            93     7       12       119     10
  p+              19     5       19       223     16
  +ed             64     4       12        78      4
  f+              27     4       21       277     15
  m+              19     4       18       274     13
  d+              18     4       19       169      9
  +t              58     3       13       494     22
  t+              46     3       22       360     23
```

`+s` made 33 words and was refused 46 times. It has 625 sibling links
and 29 flagged pairs. Its out-kind is `+,`, `+.`, `+\n` — its outputs
tend to come before punctuation. That is correct: plurals often end
clauses.

The 245 flagged functions are mostly punctuation attachments: `+,` (word
then comma), `\n+` (newline then word), `+.` (word then period). They
are functions of the signal — they were seen on real parts — but their
outputs are not standalone English words. The system learned that by
failing.


## The cost

985 failed attempts for 100 words. 6.3 seconds total (1.3s for the
record, 0.5s for the function table, 4.5s for the search).

The failures are the evidence that the feedback works. The first word
(`Os`, attempt 6) had 5 failures before it. By word 50 (`nothings`,
attempt 504) the system has enough flags to skip most bad offers. Some
words still cost many attempts — `drying` (attempt 786, 81 failures
before it) because `dry` takes an unusual set of changes and the flags
hadn't narrowed it yet.

The attempt log is kept as the cost of finding the function table.


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

Three earlier approaches, each one closer.

**Open offers** (no feedback). Discovery's class-pairs as offers,
accepted or rejected, no memory of what failed. 3,341 failed attempts
for 100 words.

**Per-ending feedback**. Track refusals per ending: `+,` refused on
this stem. Worse — 7,871 failures. The feedback was too narrow: a
refusal of `+,` taught nothing about `+.'` or `+;`. It needed to
build a group, not a list.

**Negative groups** (symbol-level). Group the refused changes by what
they share. Punctuation endings enter the same negative group after a
few refusals. 662 failures — better, but the feedback was bolted on,
not built from the structure.

**Functions** (this). The changes are the functions. The record is the
wiring. The feedback is holds on the wiring. 985 failures — slightly
more than the bolted-on version, but the system is the structure, not a
patch on it. And it runs in 6 seconds, not 14.


## What it doesn't do yet

Two-step paths (a function of a function's output) were attempted 37
times with 0 successes in the run that tested them. The out-kind mostly
points at punctuation functions, which are flagged. For paths to work,
the out-kind needs to carry more than what the signal's crystal saw;
it needs what the *made* words take, updated as words are made.

That is the next layer.
