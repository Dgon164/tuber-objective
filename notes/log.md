# Build log

What was built, in the order it happened, and what each run changed. Dates are 2026.

## 10-09, morning -- the core

- Wrote `discovery.py` as a single file: signal -> frame -> words -> runs ->
  mint -> crystal -> record. No dependencies.
- First run on `alice.txt`: frame 8, 73 words, space as separator, `the`
  as the most common run, `e` as the densest part (the one that shows up
  inside the most other parts), and a class `[+ed, +ing]` covering
  22 stems. Four seconds.
- The first frame rule (pick the most lopsided column) chose width 40 on
  the German file: UTF-8's top bit is set 3.6% of the time, so no column
  is exactly constant, and taking the maximum across more columns gets
  biased upward by noise. Replaced it with the spread between the
  most-constant and least-constant columns, where a wider width only wins
  if it beats the narrower one by more than you'd expect from chance at
  that row count.
- Compiled C program: 93% zero bytes made every width score the same
  under the old rule; the spread rule gives 64, and you can see the
  little-endian fall-off in the column rates.
- Added `--frame N` so a binary can be read at the byte level too.
- Added `--separators N` after the Alice record showed `\n` as the
  second densest part with no whole count.
- Reordered `changes` in the crystal entry by parent count instead of
  alphabetically, so punctuation stops crowding the top.

## 10-09, morning -- the examples

- German (Europarl, UTF-8): `\xc3` shows up as a 2,827-count word;
  found `+en`, `+ung`, `+lich`, `be+`, `ge+`; classes of 52 verb stems
  and 42 adjective stems; capitalized pairs.
- `bridge.py`: collide the German and English records; 2,188 shared
  parts; `technologi`, `transport`, `programm`, `instrument`,
  `international` with their parent words on each side; proper names.
- Code: Discovery run on its own source code (`=`, `in`, `for`, `if`,
  `return` at the top; `(` as the second densest part) and the compiled
  `hello` binary at 64 bits (shows the layout) and at 8 bits (finds the
  strings: `usage: hello TEXT`, `strlen`, `puts`, `hello.c`, the compiler
  version, the loader path).
- Hybrid: `record_to_rules.py` (turns a record into next-run, forms-of,
  and same-kind rules), `net_as_lens.py` (a 32-unit reservoir network's
  internal states turned into bits and fed to Discovery; frame 32 found
  automatically; dead units visible in the column rates),
  `loop.py` (walk the rules, read the walk back, collide: 8,543 shared,
  13,903 lost, 1,925 new).

## 10-09, late morning -- the Apollo Guidance Computer

- Luminary 099 octal listing (public domain, Virtual AGC) packed into
  tight 15-bit words. The frame step picked 60; this was the case that
  showed the pick alone isn't enough (60 = 15 x 4, and the spread metric
  rises slightly with more copies). Added the fold: if a picked width's
  column rates are just a smaller width's rates repeated (within the
  expected wobble from chance), fold down to that smaller width. 60 -> 15.
- Rope record: 00006 (EXTEND, a machine instruction) is the most common
  word and so becomes the separator; 04616, 06037, 05353, 04674, 04635
  show up with steady partners. Checked against the source by locating
  each subroutine's first words in the listing: BANKCALL, INTPRET,
  PHASCHNG, IBNKCALL, POSTJUMP.
- Assembly source (1.6 MB): the first run with one separator (tab) grew the
  pool past memory and was killed. Two fixes: neighbors are only compared
  when one is fresh from the last round (identical results, Alice 4 s ->
  2 s), and `--cap` (default 1,000,000 parts) stops the loop and says so
  in the record. With `--separators 2` the source runs in 19 s.
- Added `--lens octal` so the rope record lines up with the published
  listing.
- Record file names now carry `.frameN` and `.sepN` when those options are
  set, so two runs of one file don't overwrite each other.

## 10-09, midday -- crystallize, then loop again, until no change

- The crystal originally ran once and that was it -- it made classes and
  nothing used them. Jason's direction: "crystallize then loop again;
  loop until no change; it will stabilize and run out of new connections."
- First version built levels by replacing each classed run with its
  class label and running on the copy. Jason: "You don't replace. You
  add. Run has 300, next has 50 added structures for 350, then 25 for
  375, then 5 for 380, then stable."
- Reworked to use one shared pool. The next level runs on the runs as
  they are; the classes from the level below serve as a second way two
  symbols can be "the same" inside `mint()` (a class can stand in the
  slot where two sequences differ by class-mates); every run of runs,
  minted part, and class token joins the same pool, and its connections
  land on the parts it's made of (a run of one run is just that run).
  Stop when a level adds nothing or leaves a single run.
- Counts, as he described them: Alice 22,446 -> +6,709 -> +5 -> +1; German
  19,210 -> +14,943 -> +9 -> +1; Apollo rope 8,538 -> +11 -> +1; Apollo source
  126,406 -> +121,058 -> +11 -> +1. `said` at level 0 goes from 16
  containing parts up to 444 once the level-1 stretches that hold it are
  counted.
- The class-as-same comparison fired zero times on the four signals
  (class members are stems, not whole runs); noted in open.md.
- The record now has a LEVELS table with *added* and *pool total* columns,
  plus the full set of tables per level. JSON carries `levels` and the
  pool size; the hybrid scripts and `bridge.py` read `levels[0]`. JSON
  records are no longer committed; `run_examples.sh` builds them (about
  2.5 minutes total, most of it the 1.6 MB Apollo source).

## 10-09, late morning -- the end-compare looped

- Jason's five steps of understanding: identification, association,
  reduction, composition, evaluation. Four were already in the file;
  evaluation looked missing. His correction: evaluation is the root
  comparator -- "is the end-compare real, or is this the same as that" --
  it was already there, it just wasn't looped.
- Added `--memory FILE`: the pool is loaded before a run and saved
  after; remembered parts sit in the sorted pool next to the new
  signal's runs (association against memory -- basically, "have I seen
  something like this before?"); the output is sorted into confirmed /
  added / not seen this time. Nothing removed.
- Test, `examples/memory/`: first half of Alice from nothing adds
  14,079; second half against that memory confirms 11,941, adds 9,337;
  second half again confirms 21,278, adds 0 at level 0 and 5 at level 1
  (five class-in-slot parts -- the first time class-as-same fired on
  real text); German against the English memory confirms 18,971, adds
  17,987.
- The level loop now always runs until a level is left with a single
  run, instead of stopping at the first level that adds nothing: with a
  memory, level 0 can add nothing while level 1 still does.

## 10-09, noon -- how to build from it

- Jason: "How do we show that you can build from this. The general
  claims and how to expand and build from them. Explain why the
  prerequisites are enough."
- Wrote `guides/building-from-discovery.md`: the eight givens with where
  each shows in the records; the sufficiency argument (every step is the
  comparator pointed somewhere; no extension has needed a new operation);
  the four places you can point it (the cut, the kind of same, the
  comparison target, the signal); the way to add a thing.
- `extend/`: three extensions as evidence, each just a few lines calling
  into discovery.py. `cut_at_class.py`: level 1 cut at the {+ed, +ing}
  class -- what comes before a verb: and, to, she; what comes after:
  herself, out, the, a, at. `same_within.py`: words within a band of 8
  count as same on the Apollo rope -- 8,538 -> 50,319 parts, 2,580 with
  a band in a slot; `05353.~04020` collects the PHASCHNG calls across
  their argument codes. `row_by_row.py`: consecutive reservoir states
  compared -- units 28, 21, 2 never move; 8.38 bits flip per step; the
  most common joint flip happened 149 times; the flips read as a signal
  give frame 32, 6,701 distinct changes.

## Still to do before publishing

- Cold run of `run_examples.sh` from a fresh checkout.
- Read every document against the regenerated records.
- Licence file.

## 10-10 -- the flight program, running

- `examples/agc-live/`: the Virtual AGC emulator with a trace patch
  (logs every write to erasable memory and every channel packet), a
  socket client that presses DSKY keys, a build script, and one
  recording read by Discovery: it finds the 80-bit write record on its
  own and the idle loop as the most common words.

## 10-11 -- the nudge, the loop, the launch

- `nudge-run/`: two flights from the 10-10 package, one where the
  spacecraft gets kicked. The bridge on words and the flips on a shared
  clock put the whole reaction-control autopilot (the system that keeps
  the spacecraft pointed the right way) on the kicked-only side, from
  the Y gimbal pulses going in to the jet bits coming out to the
  vehicle's rates. Names were added after the fact. The vehicle rows read
  at 16 bits showed the rate plateaus between jet firings and the kicked
  axis as the field that moves while its neighbors hold steady; a new
  open end.
- `loop.py`, `walk.py`, `do.py`, `phase-a/`: the loop on the DSKY (the
  Apollo keyboard/display) with 33 raw codes and no names. 250 key
  presses built the DSKY's grammar as a state map (VERB, digit, digit);
  the walk gave key sequences for goal words; pressed fresh, they
  showed up. A word never seen: no plan was made.
- `phase-b/`: the vehicle attached as delivered; the goal row (the state
  you want to reach) never seen; the record says why (no engine, impact
  at 136 s).
- `vehicle.py` pad start and direct controls; `launch.py`; `phase-c/`:
  3,480 key presses over three lives built the effects table (engine on:
  thrust, accelerometer, propellant, engine, 13 of 13; throttle up:
  thrust, 14 of 14; 24 DSKY codes: nothing). Given a goal row, 22
  presses: arm, engine on, four notches, lift-off, hold, 223 m.
- `notes/review-2026-10-11.md`: the 10-10 package checked against the
  design rules.

## 10-12 -- functions, sentences, and the launch

- `extend/same_slot.py`: groups words by WHERE they appear (same left
  neighbor, same right neighbor). Found pronouns, modals (words like
  "can," "will," "should"), characters, determiners ("the," "a") --
  parts of speech with no labels given.
- `extend/functions.py`: Discovery's changes become functions (things
  that turn one part into another). In-kind and out-kind (what type goes
  in, what type comes out) learned from the record. Siblings are
  functions that share inputs. Standing = same minus different. Holds and
  negative flags at two levels: (function, sibling) pairs and whole
  functions. Generated 100 new English words not in Alice, with 985
  failed attempts, in 6.3 seconds. Progression through four approaches:
  open (3,341 failures), per-ending feedback (7,871 -- worse), negative
  groups (662), functions over the record (985 in 6s -- the structure
  itself is the feedback).
- `extend/FUNCTIONS.md`: writeup of the functions work.
- `extend/sentence.py`: sentences built from the follows table.
  Word-level bigrams (which-word-comes-after-which) chained from starters
  (words that follow sentence-ending punctuation) to enders. 15
  sentences in 1.4 seconds.
- The class-pair approach (the earlier iteration of word-making) was
  not kept as a script; FUNCTIONS.md describes it under what was tried
  before.
- Paper: line count fixed (470 -> 726).
- README rewritten: opens with Wheeler ("it from bit") and Bateson
  ("a difference that makes a difference"), shows how Discovery
  implements both literally.
- `notes/on-the-bitter-lesson.md`: Discovery as the Bitter Lesson taken
  to its logical absolute -- no human knowledge at all. Knowledge is the
  output, not the input.
- `guides/thinking-in-self-assembly.md`: how to work with a
  self-assembling system. Don't help it. Try it. Find the missing
  difference.
- Repo created: github.com/dgon164/tuber-objective, public, MIT.

## 10-12 -- the cold run, four times faster

- `run_examples.sh` from a fresh checkout: 393 s -> 100 s, every record
  byte for byte the same. Measured before touching anything: on Alice,
  85% of the time was writing the record, not finding the structure.
- The record. A part's JSON key was being recomputed for every connection
  it appeared in (`key_of` recursed through every nested element each
  time); now each part is keyed once (`Keys`). `json.dump`, the
  pure-Python encoder, replaced by `json.dumps`, the C-based one,
  written as bytes. Drawing a level-2 part stops at the display width
  instead of drawing the whole book and cutting it after. The density
  table grabs its top 25 with a heap instead of sorting every part.
- The mint. The pool is kept in both sorted orders between rounds; what
  a round mints is merged in where it belongs and only the pairs with a
  fresh part are compared -- the fresh-pair rule's natural extension that
  open.md asked for. Same pairs in the same rounds, so the same pool:
  Alice 22,446 -> +6,709 -> +5 -> +1 as before. The plain shared head
  (no classes) has its own fast path; at level 0 a part is its own node.
  `changes_of` looks at the first and last element before slicing.
- The comment on memory in `mint()` said two remembered parts are not
  compared again; the code always compared them (that's how a
  remembered part comes out again and counts as confirmed). Comment
  corrected, code unchanged.
- `extend/functions.py`: `standing()` counts a part's sibling functions
  with a set intersection -- same count, C speed; the making phase 5.9 s
  -> 3.3 s for 20 words.
- `run_examples.sh` sets `PYTHONHASHSEED=0`. `functions.py` keys on
  strings, so its tie-breaks followed the per-process hash seed and its
  output changed on every run; now it's the same run every time.
  (`sentence.py` draws at random and its output still changes.)
- Where the 100 s go now: the 1.6 MB Apollo source 44 s (mint 14 s; the
  rest is its record -- the JSON lists every connection in both
  directions and is 300 MB for that file); the four memory runs 15 s;
  `functions.py` 7 s; `same_within.py` 6 s; Alice and German 3-4 s each.

## 10-12 -- time

- `TIME` in every record, one level at a time: the sequence read as
  time. ARROWS -- a pair seen in both orders, counted each way (`said ->
  Alice` 25 against 7, `if -> you` 12 against 1). EFFECTS -- what shows
  up in the stretch after a run that appears at least twice its usual
  rate, actual count vs. expected (`I` -> `think`, `know`, `can`;
  `a` -> `good`, `large`, `curious`; `little` -> `golden`, `door`,
  `key`; `the` -> `King`, `March`, `Rabbit`, `Hatter`). CHAINS -- the
  strongest effect followed forward (`a -> good -> deal -> I -> think`;
  on the rope the instruction flow loops back on itself: `22156 -> 63411
  -> 74756 -> 02031 -> 70000`). The stretch is the typical distance to
  the next level's separator, so the unit of measurement is the signal's
  own.
- The time step was always there -- `examples/agc-live/` is the whole
  loop with a *do* step -- but the core never read its own sequence as
  time and no document named it. Paper section 10 now maps the six steps
  (roots, layers, interactions, crystals, relations, causes) to the code
  and the scales; reading-a-record.md has the TIME section.

## 10-12 -- persistence

- `paper/persistence.md`: a proposed alignment paper. A root-cause
  objective is one under which complex things persist: the comparator
  needs the thing and needs it again (the loop reopens); what's gone
  can't be compared again (rule 4, deletion is irreversible); the root
  cause of a harm is upstream, and upstream is a need. Persistence, not
  preservation: the thing continuing on its own terms, not kept frozen
  as it is.
- The baby model, the paper's evidence: the loop, given "keep the baby
  from touching the hot stove," proposed changing, feeding, and reading
  the baby to sleep in the crib -- addressing the cause, not building a
  restraint. Not yet in this repo; the replication plan is in open.md
  (a simulation with a baby, a stove, needs; unnamed actions that either
  remove something or satisfy something; the walk from the goal; what it
  proposes first, across worlds with the costs varied).

## 10-12 -- each example on its own

- The front page now says run one example, not run everything: each
  example's BREAKDOWN opens with its own command and its record is
  committed beside its input; `extend/` and `hybrid/` have READMEs
  listing each script with its command and what it writes; the table of
  folders links to each. `run_examples.sh` is the optional bulk
  regeneration.
- Documents point at records and outputs instead of quoting run
  numbers (design rule 11, applied to the documents): FUNCTIONS.md,
  the self-assembly guide, the TIME examples in the paper and guides,
  the timings.

## 10-12 -- one shape for every program

- Every script in `extend/`, `hybrid/`, and `examples/german/bridge.py`
  now has the same three sections: *the signal, as discovery.py reads it*
  (the same lines in each: read, frame, words, level 0) -- or *the
  record, as discovery.py wrote it* for the ones that read a record --
  then *NEW: the one new thing*, then *what it found*. The hybrid
  scripts and the bridge used to be `main()` functions; they're flat now
  like the rest. `same_slot.py` used to cut its runs by hand with the two
  separators; it goes through `run_level` now. Every output byte for byte
  the same as before. `guides/building-from-discovery.md` shows the
  shape.
- Then the root itself, as one call: `discovery.Root(path)` -- read,
  frame, words, level 0 on a shared pool, a call per further level,
  `all_levels()`, `draw()`. The four places to point are its arguments
  where they are arguments (`separators`, `same`, the path).
  `discover()` is `Root` plus `all_levels()` plus the record, so the
  root of every program and the root of the program are the same call;
  the extensions are `R = D.Root(path)` plus their NEW section. Records
  and outputs byte for byte the same.
- `notes/generations.md`: the proposal for generations of AI (1.0
  human-made, 1.1 with self-refinement, 2.0 neural networks, 2.1
  hybrid, 3.0 self-assembling and learning) and where this repo sits:
  3.0 by the definition, with `hybrid/` as the meeting point.
- `extend/template.py`: the shape to copy -- the three sections, with
  the middle one left to write (as it stands, for the most common runs,
  what follows them and how much of the time).
- A name and an address on it: Jason Weeks, thetuberobjective@gmail.com
  -- the README's Contact, both papers' bylines, the LICENSE holder, the
  header of `discovery.py`, a `CITATION.cff`, and the author of the
  commits from here on.

## 10-12 -- what a new reader found, fixed

- A cold read of the repo: every example run from a fresh checkout, the
  emulator built and run, random bytes and a CSV fed in, the memory
  loop probed with a two-byte file. What it found, all fixed the same
  day; records without a memory are byte for byte the same.
- MEMORY's *confirmed* column was counting the memory colliding with
  itself: a two-byte file run against the first-half memory "confirmed"
  11,476 of the 11,941 the second half did. In `mint()` the first round
  compared every neighboring pair, remembered pairs included. Now a
  comparison counts only when the current signal is part of it; a
  remembered part that the signal produces again is confirmed and marked
  fresh for one more round, so anything minted from it last time still
  gets reached. The two-byte file now confirms 3. `examples/memory`
  regenerated: the second half confirms 10,588 (was 11,941) and adds
  9,337 as before; the same half again confirms 19,833 of the 19,925 it
  produced and adds 0 and 5 as before; German confirms 14,797 (was
  18,971) and adds 17,987 as before. The MINT line gained a second line
  for memory runs: remembered parts produced again, per round.
- A memory took signals at any frame width, and the same number means a
  different word at a different width. One memory, one frame: a signal
  at another width is refused with the reason, or read with `--frame`.
- The memory file was a pickle; it's JSON now (pool with counts,
  part_of, history; made_of rebuilt on load). An old pickle file is
  refused with a note to delete it.
- The text record was written in the locale's encoding and crashed on
  the German example under an ASCII locale; UTF-8 now, here and in
  `extend/functions.py` and `hybrid/loop.py`.
- `--separators 20` was ambiguous -- did you mean the top twenty words,
  or the space character (byte 0x20)? Digits alone are treated as a
  count, so to name one specific word you use `0x20` or `20,` (record
  tag `.sepx20`). An option the program doesn't have, or one with its
  value left off, now gives an error message instead of being silently
  ignored or throwing a traceback. `--limit 0` reads nothing instead of
  everything.
- `run_examples.sh` died without `/usr/share/dict/american-english`;
  it skips `functions.py` and says so, the same way it already did for
  numpy.
- Noted in the guides: the frame is decided from the first 64 KB.
- Measured and left alone: random bytes fold to a frame of one bit and
  mint nothing at level 0, then the levels above mint from the
  run-length sequence like any signal, and two unrelated noise files
  confirm 40-50% of each other's level-1 and level-2 parts. A null
  (a baseline for "is this real or just chance?") for the mint and the
  levels is filed in open.md as the design question it is.
