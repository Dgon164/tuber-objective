# Functions: new words from the record of Discovery

## Description

Discovery reads *Alice in Wonderland*. Discovery writes a record of each
thing that Discovery finds. The record has the parts that repeat, the
contents of each part, and the changes that make one part into a
different part. The record is layer 0.

This program reads the record and tests 2 ideas. The first idea: the
changes of Discovery can become functions. A function is a thing that
takes a part and makes a new part. The second idea: those functions can
make real English words that are not in the original text. The only
guide is the feedback from an answer key.

Both ideas are correct. The output `alice.functions.txt` has the words
that the program made, each try, and the cost. The script
`run_examples.sh` makes `alice.functions.txt` again (the run with 20
words). The file `functions.output.txt` is the output that the run
printed. The command for the full run:

```
python functions.py examples/text/alice.txt 100
```


## Layer 0: the record

Discovery runs on `alice.txt` in the usual way. No parameter is set for
this task. Discovery gets no information about the signal. The record is
`examples/text/alice.txt.record.txt`. The record has:

- the bytes and the frame
- the distinct words (the sequences between spaces)
- the parts in the mint pool. The mint is the step that finds the
  sequences that repeat. To mint a part is to make a new part from 2
  parts that have the same start or the same end.
- the changes that the crystal found. The crystal is the step that finds
  the relations between parts. To crystallize the pool is to find the
  change that makes one part into a different part.

A **change** is a thing that Discovery found that makes one part into a
different part. Examples:

- `+ed` makes `walk` into `walked`
- `m+` makes `are` into `mare`
- `+s` makes `cat` into `cats`

The changes are the raw material.


## Layer 1: functions

Not each change is a function. A change that occurred on only 1 part is
a connection for 1 case. The change gives information about that part,
but the change cannot apply to other parts. A change that occurred on 2
or more parts operates as a function. The function takes one kind of
thing and makes a different kind. The first line of
`alice.functions.txt` gives the number of changes in the record and the
number of changes that are functions.

There is 1 more limit, and the limit is important. The functions act on
**whole runs**. A whole run is a part that occurs on its own in the
signal (the whole count of the part is more than 0). Fragments such as
`e` or `ucked` are the material of changes, not the things that changes
act on.

The letter `e` is inside more parts than almost each other part (see
PARTS BY DENSITY in the record). The letter `e` takes almost each
change. Thus the letter `e` gives no information about any 1 change.
With the fragments, the number of functions and the number of sibling
pairs were many times larger. The search took minutes and learned no new
thing.

With whole runs only, the number of pairs is smaller by orders of
magnitude. The count is on the first line that `functions.py` prints.
The search ends in seconds.

The **in-kind** of a function is the kind of thing that the function
operates on. The program learns the in-kind from the parts where the
function occurred: the other functions that those parts also take. The
function `+s` occurred on many parts. Those parts also take `+ed`,
`+ing`, `+'s`, and other functions. That set is the in-kind of `+s`.

The **out-kind** of a function is the kind of thing that the function
makes. The out-kind is the set of functions that occurred on the parts
that the function made. The function `+s` made plurals. Those plurals
take `+,` and `+.` (word then comma, word then period). That set is the
out-kind of `+s`. The function table in `alice.functions.txt` lists the
out-kind of each function.


## Layer 2: siblings and paths

Two functions are **siblings** when 2 or more parts take both functions.
The functions `+s` and `+ed` are siblings: many words take both. The
functions `+s` and `m+` are not siblings: no word in Alice takes both
`+s` and the prefix `m`.

The sibling links are the connections. The count of the sibling links is
on the first line of `alice.functions.txt`.

A **path** is one function after a different function. Apply `+s` to
`ground`, and get `grounds`. Now `grounds` is a part, and the program
can try the functions in the out-kind of `+s` on `grounds`. Paths are
the method of the system to connect things in a chain.


## The method to make a word

The system offers a function on a part that does not have the function.
The system makes the offer when the part takes siblings of that
function. Then the part appears to be the kind of thing that the
function operates on.

Each offer gets a **standing**. The standing is the comparator in both
directions:

- **Same**: the functions that the part takes, when those functions are
  siblings of the function in the offer and have no flag.
- **Different**: the functions that the part takes, when those functions
  are *not* siblings of the function in the offer.
- **Standing = same - different.**

This is the key step. A part such as `a`, `it`, or `to` takes a very
large number of changes, because the part is inside many words. The same
count of the part is high. But the different count of the part is also
high. The part matches each thing. Thus the part is not specially like
any one thing.

A part such as `a` gets a low score. A part such as `are` takes a narrow
set of changes: prefixes and suffixes that act on short stems like
verbs. The siblings of `are` overlap very much. The part `are` gets a
high score.

The system tries the highest standing first. A standing of 0 or less
means: do not offer.


## Holds and flags

Each (function, sibling) pair is a **hold**: "this function operates on
the kind of thing that the sibling operates on". The system checks each
answer from the answer key against the hold.

- **Yes** sets the hold and resets each negative flag on the hold.
- **No** counts against the hold. Two answers of no with no yes set a
  **negative flag**: "this function does not operate on the things that
  the sibling operates on". The flag stays. The next yes resets the
  flag.

One level up: a **function** gets a flag when the answer key refused the
outputs of the function 2 times and did not accept any output. The
function makes a kind of thing that the answer key does not accept. The
function `+,` (word then comma) is the most clear case. The offers of a
function with a flag rank lower by the count of refusals. A yes resets
the flag.

A **seam** is the 2-character boundary where the change meets the part.
If that pair of characters is not side by side at any place in the
signal, the seam counts 1 against the offer. A yes that passes through
that seam resets the count.

Feedback acts on the producer (the hold), not on the record. The record
is the result that Discovery found. The holds are the knowledge about
the use of the record.

The header and the NEGATIVE FLAGS section of `alice.functions.txt` give
the number of negative flags at the end and the number of whole
functions with a flag.


## The words that the program made

The words are not in Alice. The program checked the words against
`/usr/share/dict/american-english`. The MADE table in
`alice.functions.txt` lists each word with:

- the part and the function that made the word
- the number of the try
- the number of tries that failed before the word

Read the first rows. The part `are` takes many prefix functions, and the
prefix functions are siblings of each other. Thus the system offers
`m+`, `t+`, `f+`, `p+`, `r+`, and `b+` on `are` with a high standing.
Most of the offers are correct. After the first offer is correct, the
other offers follow quickly, because the holds are already set.

Read the later rows: suffixes on longer stems, and prefix functions on
whole words (`d+` on `reading`). The system had no knowledge of a prefix
or a suffix. The system found the prefixes and the suffixes as changes
in the record. The system learned the changes that operate on the same
kinds of parts.


## The function table (the final output)

The compact output is THE FUNCTION TABLE in `alice.functions.txt`. The
table is the result, not the search. For each function, the table gives:

- the number of parts where the function occurred
- the number of words that the function made
- the number of refusals
- the sibling links
- the pairs with a flag
- the out-kind

Read `+s`: the largest number of words and the largest number of
refusals. The out-kind of `+s` is `+,`, `+.`, `+\n`. The outputs of `+s`
usually come before punctuation. That is correct: plurals often end
clauses.

Read the functions with a flag. Most of them are punctuation
attachments: `+,` (word then comma), `\n+` (newline then word), `+.`
(word then period). The functions with a flag are functions of the
signal, because the functions occurred on real parts. But the outputs of
the functions are not English words on their own. The system learned
that from the failures.


## The cost

The header of `alice.functions.txt` has the count of tries that failed,
the total number of tries, and the time. The time is in 3 parts: the
record, the function table, and the search.

The failures are the evidence that the feedback operates. Read the
"failed before it" column of the MADE table from top to bottom. Each of
the early words cost many failures. After the flags accumulate, the
system omits most bad offers. Some words still cost many tries, because
the stem takes an unusual set of changes that the flags did not narrow
yet.

The log of tries (EVERY ATTEMPT) stays in the output as the cost to find
the function table.


## Each part in the theory

Each part of this system is one idea at a different scale:

- A **function** is a compulon (a unit of computation). The function
  accepts one kind (the in-kind), makes one kind (the out-kind), and
  refuses the rest.
- A **hold** on a (function, sibling) pair is a hold. A yes sets the
  hold. A no from the comparator resets the hold. The hold is the
  current best estimate that the pair is real.
- A **negative flag** is information in a hold about what a thing is
  NOT. The flag has a set condition (2 answers of no, no yes) and a
  reset condition (a yes).
- **Standing** is the comparator in both directions, same minus
  different. The standing is a number for the degree to which this part
  is like the kind of thing that this function operates on.
- **Layers**: the record is layer 0, the functions are layer 1, and the
  siblings and paths are layer 2. Each layer keeps a total that the
  layer updates.
- **Feedback** changes the producer (the hold), not the record. That is
  feedback, not recurrence. The record is the result that Discovery
  found. The holds are the knowledge about the things that operate.


## The earlier methods

There were 3 earlier methods, each one nearer to this method. The cost
of each method is the measure: the number of tries that failed for each
word that the method made.

**Open offers** (no feedback). The class pairs of Discovery are the
offers. The answer key accepts or refuses each offer. The method has no
memory of the failures. This method had the most failures.

**Feedback for each ending**. The method records the refusals for each
ending: `+,` refused on this stem. This method was worse than no
feedback. The feedback was too narrow: a refusal of `+,` gave no
information about `+.'` or `+;`. The method needed to make a group, not
a list.

**Negative groups** (at the symbol level). The method groups the changes
with refusals by the things that the changes share. Punctuation endings
go into the same negative group after a small number of refusals. This
method had many fewer failures. But the feedback was an addition from
outside, not a part of the structure.

**Functions** (this version). The changes are the functions. The record
is the connections. The feedback is holds on the connections. This
method has approximately the same failure rate as the negative groups,
in less than half the time. The system is the structure itself, not a
patch on top of the structure.


## The limits

The program tried 2-step paths (a function on the output of a function)
a few dozen times in the run that tested them. No try was a success. The
out-kind points mostly at punctuation functions, and those functions
have flags. For paths to operate, the out-kind must carry more than the
result of the crystal on the signal. The out-kind must carry the
functions that the *new* words take. The out-kind must get an update
each time the program makes a new word.

That is the next layer.
