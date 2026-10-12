# Build log

What was built, in order, and what each run changed. Dates are 2026.

## 10-09, morning — the core

- `discovery.py` written as one file: signal → frame → words → runs →
  mint → crystal → record. No dependencies.
- First run on `alice.txt`: frame 8, 73 words, space separator, `the`
  the most common run, `e` the densest part, class `[+ed, +ing]` with
  22 stems. Four seconds.
- First frame rule (most lopsided column) picked width 40 on the German
  file: the UTF-8 top bit is set 3.6% of the time, so no column is
  exactly constant, and the maximum over more columns is biased up by
  noise. Replaced with the spread between the most-1 and least-1
  columns, with a wider width taking over only when it beats the
  narrower by more than chance at that row count.
- Compiled C program: 93% zero bytes made every width score the same
  under the old rule; the spread rule gives 64, with the little-endian
  fall-off visible in the column rates.
- `--frame N` added so a binary can be read at the byte grain as well.
- `--separators N` added after the Alice record showed `\n` as the
  second densest part with no whole count.
- `changes` in the crystal entry ordered by parent count instead of
  alphabetically, so punctuation stops crowding the top.

## 10-09, morning — the examples

- German (Europarl, UTF-8): `\xc3` as a 2,827-count word; `+en`, `+ung`,
  `+lich`, `be+`, `ge+`; classes of 52 verb stems and 42 adjective
  stems; capitalised pairs.
- `bridge.py`: collide the German and English records; 2,188 shared
  parts; `technologi`, `transport`, `programm`, `instrument`,
  `international` with their parents on each side; proper names.
- Code: Discovery's own source (`=`, `in`, `for`, `if`, `return` at the
  top; `(` the second densest part) and the compiled `hello` at 64 bits
  (layout) and at 8 bits (strings: `usage: hello TEXT`, `strlen`,
  `puts`, `hello.c`, the compiler version, the loader path).
- Hybrid: `record_to_rules.py` (record → next-run, forms-of, same-kind
  rules), `net_as_lens.py` (a 32-unit reservoir's states → bits →
  Discovery; frame 32 found; dead units visible in the column rates),
  `loop.py` (walk the rules, read the walk back, collide: 8,543 shared,
  13,903 lost, 1,925 new).

## 10-09, late morning — the Apollo Guidance Computer

- Luminary 099 octal listing (public domain, Virtual AGC) packed into
  tight 15-bit words. Frame step picked 60; this was the case that
  showed the pick alone is not enough (60 = 15 × 4 and the max-based
  spread rises slightly with more copies). Added the fold: a picked
  width whose column rates are a divisor's rates repeated, within the
  chance wobble, folds to that divisor. 60 → 15.
- Rope record: 00006 (EXTEND) the most common word and so the
  separator; 04616, 06037, 05353, 04674, 04635 with steady partners.
  Checked against the source by locating each subroutine's first words
  in the listing: BANKCALL, INTPRET, PHASCHNG, IBNKCALL, POSTJUMP.
- Assembly source (1.6 MB): first run with one separator (tab) grew the
  pool past memory and was killed. Two changes: neighbours compared only
  when one is fresh from the last round (identical result, Alice 4 s →
  2 s), and `--cap` (default 1,000,000 parts) that stops the loop and
  says so in the record. With `--separators 2` the source runs in 19 s.
- `--lens octal` added so the rope record lines up with the published
  listing.
- Record file names carry `.frameN` and `.sepN` when those options are
  set, so two runs of one file don't overwrite each other.

## 10-09, midday — crystallize, then loop again, until no change

- The crystal ran once and its output was terminal: it made classes and
  nothing used them. Turtle: "crystallize then loop again; loop until no
  change; it will stabilize and run out of new connections."
- First version built levels by replacing each classed run with its
  class and running on the copy. Turtle: "You don't replace. You add.
  Run has 300, next has 50 added structures for 350, then 25 for 375,
  then 5 for 380, then stable."
- Reworked to one shared pool. The next level runs on the runs as they
  are; the classes from the level below are a second way two symbols can
  be the same inside `mint()` (a class stands in the slot where two
  sequences differ by class-mates); every run of runs, minted part and
  class token joins the same pool and its connections land on the parts
  it is made of (a run of one run is that run). Stop when a level adds
  nothing or leaves a single run.
- Counts, as he described them: Alice 22,446 → +6,709 → +5 → +1; German
  19,210 → +14,943 → +9 → +1; Apollo rope 8,538 → +11 → +1; Apollo source
  126,406 → +121,058 → +11 → +1. `said` at level 0 goes from 16
  containing parts to 444 once the level-1 stretches that hold it are
  counted.
- The class-as-same comparison fired zero times on the four signals
  (class members are stems, not whole runs); noted in open.md.
- Record has a LEVELS table with *added* and *pool total* columns and the
  full set of tables per level. JSON carries `levels` and the pool size;
  the hybrid scripts and `bridge.py` read `levels[0]`. JSON records are
  no longer committed; `run_examples.sh` builds them (about 2.5 minutes
  in all, most of it the 1.6 MB Apollo source).

## 10-09, late morning — the end-compare looped

- Turtle's five steps of understanding: identification, association,
  reduction, composition, evaluation. Four were in the file; evaluation
  looked missing. His correction: evaluation is the root comparator —
  "is the end-compare real, or is this the same as that" — it was there,
  just not looped.
- Added `--memory FILE`: the pool is loaded before a run and saved
  after; remembered parts sit in the sorted pool next to the new
  signal's runs (association against memory); the run's output is
  sorted into confirmed / added / not seen this time. Nothing removed.
- Test, `examples/memory/`: first half of Alice from nothing adds
  14,079; second half against it confirms 11,941, adds 9,337; second
  half again confirms 21,278, adds 0 at level 0 and 5 at level 1 (five
  class-in-slot parts — the first time class-as-same fired on real
  text); German against the English memory confirms 18,971, adds
  17,987.
- The level loop now always runs until a level is left with a single
  run, instead of stopping at the first level that adds nothing: with a
  memory, level 0 can add nothing while level 1 still does.

## 10-09, noon — how to build from it

- Turtle: "How do we show that you can build from this. The general
  claims and how to expand and build from them. Explain why the
  prerequisites are enough."
- `guides/building-from-discovery.md`: the eight givens with where each
  shows in the records; the sufficiency argument (every step is the
  comparator pointed somewhere; no extension has needed a new
  operation); the four places to point (the cut, the kind of same, the
  comparison target, the signal); the way to add a thing.
- `extend/`: three extensions as evidence, each a few lines calling
  into discovery.py. `cut_at_class.py`: level 1 cut at the {+ed, +ing}
  class — before a verb: and, to, she; after: herself, out, the, a, at.
  `same_within.py`: words in the same band of 8 count as same on the
  Apollo rope — 8,538 → 50,319 parts, 2,580 with a band in a slot;
  `05353.~04020` collects the PHASCHNG calls over their argument codes.
  `row_by_row.py`: consecutive reservoir states compared — units 28,
  21, 2 never move; 8.38 bits flip per step; the most common joint
  flip happened 149 times; the flips read as a signal give frame 32,
  6,701 distinct changes.

## Still to do before publishing

- Cold run of `run_examples.sh` from a fresh checkout.
- Read every document against the regenerated records.
- Licence file.

## 10-10 — the flight program, running

- `examples/agc-live/`: the Virtual AGC emulator with a trace patch
  (every erasable write; every channel packet), a socket client that
  presses DSKY keys, a build script, and one recording read by
  Discovery: it finds the 80-bit write record on its own and the idle
  loop as the most common words.

## 10-11 — the nudge, the loop, the launch

- `nudge-run/`: two flights from the 10-10 package, one kicked. The
  bridge on words and the flips on a shared clock put the whole
  reaction-control autopilot on the kicked-only side, from the Y gimbal
  pulses in to the jet bits out to the vehicle's rates. Names went on
  after. The vehicle rows read at 16 bits gave the rate plateaus between
  firings and the kicked axis as the field that moves while its
  neighbours hold; a new open end.
- `loop.py`, `walk.py`, `do.py`, `phase-a/`: the loop on the DSKY with
  33 raw codes and no names. 250 presses built the DSKY's grammar as a
  state map (VERB, digit, digit); the walk gave key sequences for goal
  words; pressed fresh, they showed. A word never seen: no plan.
- `phase-b/`: the vehicle attached as delivered; the goal row never
  seen; the record says why (no engine, impact at 136 s).
- `vehicle.py` pad start and direct controls; `launch.py`; `phase-c/`:
  3,480 presses over three lives built the effects table (engine on:
  thrust, accelerometer, propellant, engine, 13 of 13; throttle up:
  thrust, 14 of 14; 24 DSKY codes: nothing). Given a goal row, 22
  presses: arm, engine on, four notches, lift-off, hold, 223 m.
- `notes/review-2026-10-11.md`: the 10-10 package against the rules.

## 10-12 — functions, sentences, and the launch

- `extend/same_slot.py`: groups words by WHERE they stand (same left
  neighbor, same right neighbor). Found pronouns, modals, characters,
  determiners — parts of speech with no labels given.
- `extend/functions.py`: Discovery's changes become functions (nodes
  that turn one part into another). In-kind and out-kind learned from
  the record. Siblings are functions sharing inputs. Standing = same −
  different. Holds and negative flags at two levels: (function, sibling)
  pairs and whole functions. 100 new English words not in Alice, 985
  failed attempts, 6.3 seconds. Progression through four approaches:
  open (3,341 failures), per-ending feedback (7,871 — worse), negative
  groups (662), functions over the record (985 in 6s — the structure is
  the feedback).
- `extend/FUNCTIONS.md`: writeup of the functions work.
- `extend/sentence.py`: sentences from the follows table. Word-level
  bigrams chained from starters (after sentence-ending punctuation) to
  enders. 15 sentences in 1.4 seconds.
- `extend/make_words.py`: the class-pair approach (earlier iteration
  of word-making, kept for comparison).
- Paper: line count fixed (470 → 726).
- README rewritten: opens with Wheeler ("it from bit") and Bateson
  ("a difference that makes a difference"), shows how Discovery
  implements both literally.
- `notes/on-the-bitter-lesson.md`: Discovery as the Bitter Lesson taken
  to its logical absolute — no human knowledge at all. Knowledge is the
  output, not the input.
- `guides/thinking-in-self-assembly.md`: how to work with a
  self-assembling system. Don't help it. Try it. Find the missing
  difference.
- Repo created: github.com/dgon164/tuber-objective, public, MIT.
