# Work log

This log shows what the author made, in the order of the work, and what
each run changed. All dates are in 2026.

## 10-09, morning -- the core

- The author wrote `discovery.py` as 1 file. The file does these steps in
  this order: signal, frame, words, runs, mint, crystal, record. To mint a
  part is to make a new part from 2 parts that have the same start or the
  same end. The file has no dependencies.
- The first run on `alice.txt` found a frame of 8 and 73 words. The run
  found the space character as the separator. The run found `the` as the
  most common run and `e` as the part with the highest density. The part
  with the highest density is the part that occurs inside the most other
  parts. The run found a class `[+ed, +ing]` that contains 22 stems. The
  run took 4 seconds.
- The first frame rule selected the most unequal column. This rule
  selected a width of 40 on the German file. In UTF-8 the top bit is 1 in
  3.6 percent of the bytes, so no column is fully constant. The maximum
  across more columns becomes higher because of noise. The author replaced
  the rule with the spread between the most constant column and the least
  constant column. With the new rule, a wider width wins only if the
  spread of the wider width is larger than the spread of the narrower
  width. The difference must be more than chance gives at that row count.
- In the compiled C program, 93 percent of the bytes are zero. With the
  old rule, each width got the same score. The spread rule gives 64. The
  column rates show the little-endian decrease.
- The author added `--frame N`. With this flag, the program can also read
  a binary file at the byte level.
- The author added `--separators N` after the Alice record showed `\n` as
  the part with the second highest density and no whole count.
- The author changed the order of `changes` in the crystal entry. The
  order is now by parent count, not alphabetical. Thus punctuation no
  longer fills the top of the list.

## 10-09, morning -- the examples

- In the German file (Europarl, UTF-8), `\xc3` occurs as a word with a
  count of 2,827. The run found `+en`, `+ung`, `+lich`, `be+`, and `ge+`.
  The run found a class of 52 verb stems and a class of 42 adjective
  stems. The run found pairs of words with capital letters.
- The script `bridge.py` compares the German record with the English
  record. The 2 records share 2,188 parts. The shared parts include
  `technologi`, `transport`, `programm`, `instrument`, and
  `international`, each with its parent words on each side. The shared
  parts include proper names.
- The author ran Discovery on the source code of Discovery. The top words
  are `=`, `in`, `for`, `if`, and `return`. The part with the second
  highest density is `(`. The author ran Discovery on the compiled `hello`
  binary at 64 bits and at 8 bits. The run at 64 bits shows the layout of
  the file. The run at 8 bits finds the strings: `usage: hello TEXT`,
  `strlen`, `puts`, `hello.c`, the compiler version, the loader path.
- The hybrid script `record_to_rules.py` makes 3 kinds of rules from a
  record: next-run rules, forms-of rules, and same-kind rules. The script
  `net_as_lens.py` changes the internal states of a reservoir network
  with 32 units into bits and gives the bits to Discovery. Discovery
  found the frame of 32 without help, and the dead units are visible in
  the column rates. The script `loop.py` walks the rules and reads the
  walk as a signal. Then the script compares the result with the record:
  8,543 parts shared, 13,903 parts lost, 1,925 parts new.

## 10-09, late morning -- the Apollo Guidance Computer

- The author packed the Luminary 099 octal listing (public domain,
  Virtual AGC) into 15-bit words with no gaps. The frame step picked 60,
  and this case showed that the pick alone is not enough. The width 60 is
  15 x 4, and the spread metric increases a small amount with more
  copies. The author added the fold. To fold is to go down from the width
  that the frame step picked to a smaller width. The program folds when
  the column rates of the wide width are the rates of the smaller width
  repeated. The repeat must agree within the variation that chance gives.
  The fold changed 60 to 15.
- In the rope record, 00006 (EXTEND, a machine instruction) is the most
  common word, so 00006 becomes the separator. The words 04616, 06037,
  05353, 04674, and 04635 occur with constant partners. The author checked
  the record against the source. The author found the first words of each
  subroutine in the listing: BANKCALL, INTPRET, PHASCHNG, IBNKCALL,
  POSTJUMP.
- The assembly source is 1.6 MB. The first run, with 1 separator (the
  tab), made the pool larger than the RAM of the machine, and the run was
  stopped. The author made 2 changes. The program now compares 2
  neighbors only when 1 of the neighbors is fresh from the last round.
  The results are the same, and the Alice run went from 4 s to 2 s. The
  flag `--cap` (default 1,000,000 parts) stops the loop and writes a note
  in the record. With `--separators 2`, the source runs in 19 s.
- The author added `--lens octal`. With this lens, the rope record agrees
  with the public listing.
- The record file names now contain `.frameN` and `.sepN` when the user
  sets those options. Thus 2 runs of 1 file do not overwrite each other.

## 10-09, midday -- crystallize, then loop again, until no change

- To crystallize is to make classes from the parts in the pool. At first
  the crystal ran 1 time only. The crystal made classes, and no step used
  the classes. Jason gave this direction: "crystallize then loop again;
  loop until no change; it will stabilize and run out of new
  connections."
- The first version made the levels in 2 steps. The program replaced each
  run that had a class with the class label. Then the program ran on the
  copy. Jason said: "You don't replace. You add. Run has 300, next has 50
  added structures for 350, then 25 for 375, then 5 for 380, then
  stable."
- The author changed the program to use 1 shared pool. The next level
  runs on the runs with no change to the runs. The classes from the level
  below give a second way for 2 symbols to be the same inside `mint()`.
  A class can stand in the slot where 2 sequences differ by members of 1
  class. Each run of runs, each part that the program mints, and each
  class token joins the same pool. The connections of each new part land
  on the parts that the new part contains. A run of 1 run is that run.
  The program stops when a level adds nothing or leaves 1 run.
- The counts agree with the description that Jason gave:
  - Alice 22,446 -> +6,709 -> +5 -> +1
  - German 19,210 -> +14,943 -> +9 -> +1
  - Apollo rope 8,538 -> +11 -> +1
  - Apollo source 126,406 -> +121,058 -> +11 -> +1

  At level 0, the part `said` has 16 parts that contain it. When the
  program counts the level-1 stretches that hold `said`, the count goes
  up to 444.
- The class-as-same comparison occurred 0 times on the 4 signals. The
  members of a class are stems, not whole runs. The author wrote a note
  about this result in open.md.
- The record now has a LEVELS table with the columns *added* and *pool
  total*. The record also has the full set of tables for each level. The
  JSON record contains `levels` and the pool size. The hybrid scripts and
  `bridge.py` read `levels[0]`. The JSON records are no longer committed.
  The script `run_examples.sh` makes the JSON records in approximately
  2.5 minutes, and most of that time goes to the 1.6 MB Apollo source.

## 10-09, late morning -- the end-compare in a loop

- Jason gave 5 steps of understanding: identification, association,
  reduction, composition, and evaluation. The file already had 4 of the
  steps. Evaluation looked absent. Jason corrected this view: evaluation
  is the root comparator, "is the end-compare real, or is this the same
  as that". Evaluation was already in the file, but evaluation was not in
  a loop.
- The author added `--memory FILE`. The program loads the pool before a
  run and saves the pool after the run. The parts from the memory sit in
  the pool, in sort order, next to the runs of the new signal. The
  comparison is association against the memory: "have I seen something
  like this before?". The program sorts the output into 3 groups:
  confirmed, added, and not seen this time. The program removes nothing.
- The test is in `examples/memory/`. The first half of Alice, with no
  memory, adds 14,079 parts. The second half, against that memory,
  confirms 11,941 parts and adds 9,337 parts. The second half again
  confirms 21,278 parts, adds 0 parts at level 0, and adds 5 parts at
  level 1. The 5 parts are class-in-slot parts, the first occurrence of
  class-as-same on real text. German, against the English memory,
  confirms 18,971 parts and adds 17,987 parts.
- The level loop now always runs until a level has 1 run. Before, the
  loop stopped at the first level that added nothing. With a memory,
  level 0 can add nothing, but level 1 can still add parts.

## 10-09, noon -- how to make new things from Discovery

- Jason said: "How do we show that you can build from this. The general
  claims and how to expand and build from them. Explain why the
  prerequisites are enough."
- The author wrote `guides/building-from-discovery.md`. The cut is the
  step that divides the signal into runs at a separator. The guide
  contains 4 things:
  - the 8 givens, and where each given shows in the records
  - the argument that the givens are enough: each step is the comparator
    pointed at a thing, and no extension has needed a new operation
  - the 4 places where you can point the comparator: the cut, the kind of
    same, the comparison target, and the signal
  - the way to add a thing
- The folder `extend/` has 3 extensions as evidence. Each extension is a
  few lines that call discovery.py.
  - The script `cut_at_class.py` cuts level 1 at the class {+ed, +ing}.
    The words before a verb are: and, to, she. The words after a verb
    are: herself, out, the, a, at.
  - The script `same_within.py` counts words within a band of 8 as the
    same on the Apollo rope. The parts go from 8,538 to 50,319, and 2,580
    parts have a band in a slot. The part `05353.~04020` collects the
    PHASCHNG calls across their argument codes.
  - The script `row_by_row.py` compares each reservoir state with the
    next state. The units 28, 21, and 2 never change. In each step, 8.38
    bits flip. The most common joint flip occurred 149 times. The flips,
    read as a signal, give a frame of 32 and 6,701 distinct changes.

## Tasks that remain before publication

- Do a cold run of `run_examples.sh` from a fresh checkout.
- Read each document and compare the document with the new records.
- Write the licence file.

## 10-10 -- the flight program in operation

- The folder `examples/agc-live/` contains 4 things:
  - the Virtual AGC emulator with a trace patch. The patch logs each
    write to the erasable memory and each channel packet.
  - a socket client that presses DSKY keys
  - a build script
  - 1 recording that Discovery reads. Discovery finds the 80-bit write
    record without help. Discovery finds the idle loop as the most common
    words.

## 10-11 -- the nudge, the loop, the launch

- The folder `nudge-run/` has 2 flights from the 10-10 package. In 1
  flight, the spacecraft gets a kick. The author ran the bridge on the
  words and the flips on a shared clock. The result put the whole
  reaction-control autopilot on the side of the flight with the kick
  only. The reaction-control autopilot is the system that keeps the
  spacecraft pointed in the correct direction. The side with the kick
  includes the Y gimbal pulses that go in, the jet bits that come out,
  and the rates of the vehicle. The author added the names after the
  run. The vehicle rows, read at 16 bits, showed the rate plateaus
  between the times when the jets fire. The rows showed the axis with
  the kick as the field that moves when its neighbors stay constant.
  This result is a new open end.
- The scripts `loop.py`, `walk.py`, `do.py`, and the folder `phase-a/`
  run the loop on the DSKY (the Apollo keyboard and display). The loop
  used 33 raw codes and no names. The loop made the grammar of the DSKY
  as a state map (VERB, digit, digit) from 250 key presses. The walk gave
  key sequences for the goal words. The author pressed the sequences
  again, and the goal words appeared. For a word never seen, the loop
  made no plan.
- In `phase-b/`, the author attached the vehicle with no change. The goal
  row is the state that you want to reach. The loop never saw the goal
  row. The record gives the reason: no engine, and impact at 136 s.
- The author added a pad start and direct controls to `vehicle.py`, and
  wrote `launch.py`. In `phase-c/`, 3,480 key presses over 3 lives made
  the effects table. The table shows these effects:
  - engine on: thrust, accelerometer, propellant, engine, 13 of 13
  - throttle up: thrust, 14 of 14
  - 24 DSKY codes: nothing

  With a goal row, the loop found 22 presses: arm, engine on, 4 notches,
  lift-off, hold. The result was 223 m.
- The note `notes/review-2026-10-11.md` is a check of the 10-10 package
  against the design rules.

## 10-12 -- functions, sentences, and the launch

- The script `extend/same_slot.py` groups words by the place where the
  words occur (the same left neighbor, the same right neighbor). The
  script found pronouns, modals (words such as "can," "will," "should"),
  characters, and determiners ("the," "a"). The groups are parts of
  speech, and the script got no labels.
- In `extend/functions.py`, the changes of Discovery become functions. A
  function is a thing that changes 1 part into a different part. The
  script learns the in-kind and the out-kind from the record. The in-kind
  is the type that goes in, and the out-kind is the type that comes out.
  Siblings are functions that share inputs. Standing is same minus
  different. The script keeps holds and negative flags at 2 levels:
  (function, sibling) pairs and whole functions. The script made 100 new
  English words that are not in Alice, with 985 tries that failed, in 6.3
  seconds. The work went through 4 approaches:
  - open: 3,341 failures
  - feedback for each ending: 7,871 failures, worse
  - negative groups: 662 failures
  - functions over the record: 985 failures in 6 s. The structure is the
    feedback.
- The file `extend/FUNCTIONS.md` is the report on the functions work.
- The script `extend/sentence.py` makes sentences from the follows table.
  The script chains word-level bigrams (the word that comes after a word)
  from starters to enders. A starter is a word that follows the
  punctuation at the end of a sentence. The script made 15 sentences in
  1.4 seconds.
- The author did not keep the class-pair approach as a script. The
  class-pair approach was the earlier version of the word maker. The file
  FUNCTIONS.md describes the class-pair approach in the section on
  earlier tries.
- The author corrected the line count in the paper (470 -> 726).
- The author wrote the README again. The README opens with Wheeler ("it
  from bit") and Bateson ("a difference that makes a difference"). The
  README shows how Discovery applies both quotations directly.
- The note `notes/on-the-bitter-lesson.md` shows Discovery as the Bitter
  Lesson taken to its logical limit: no human knowledge at all. Knowledge
  is the output, not the input.
- The guide `guides/thinking-in-self-assembly.md` shows how to work with
  a system that assembles itself. Do not help the system. Try the system.
  Find the difference that is absent.
- The author made the repository: github.com/dgon164/tuber-objective,
  public, MIT.

## 10-12 -- the cold run, 4 times faster

- The script `run_examples.sh` from a fresh checkout went from 393 s to
  100 s. Each record is the same, byte for byte. The author measured the
  time before any change. On Alice, 85 percent of the time went to the
  write of the record, not to the search for the structure.
- The record. Before, the program computed the JSON key of a part again
  for each connection that contained the part. The function `key_of`
  went through each nested value each time. Now the program gives each
  part a key 1 time (`Keys`). The author replaced `json.dump`, the
  pure-Python encoder, with `json.dumps`, the C-based encoder, and the
  program writes the output as bytes. The draw of a level-2 part stops at
  the display width. Before, the program drew the whole book and removed
  the extra text after. The density table gets its top 25 with a heap,
  and does not sort each part.
- The mint. The program keeps the pool in both sort orders between
  rounds. The program merges the parts that a round mints into the
  correct places. The program compares only the pairs with a fresh part.
  The change is the natural extension of the fresh-pair rule that open.md
  asked for. The same pairs occur in the same rounds, so the pool is the
  same: Alice 22,446 -> +6,709 -> +5 -> +1, as before. The plain shared
  head (no classes) has its own fast path. At level 0, a part is its own
  node. The function `changes_of` looks at the first value and the last
  value before the slice.
- The comment on the memory in `mint()` said that the program does not
  compare 2 parts from the memory again. The code always compared the 2
  parts. That comparison is how a part from the memory comes out again
  and counts as confirmed. The author corrected the comment. The code did
  not change.
- In `extend/functions.py`, `standing()` now counts the sibling functions
  of a part with a set intersection. The count is the same, at C speed.
  The make phase went from 5.9 s to 3.3 s for 20 words.
- The script `run_examples.sh` sets `PYTHONHASHSEED=0`. The script
  `functions.py` keys on strings, so its tie-breaks followed the hash
  seed of each process. Thus its output changed on each run. Now the run
  is the same each time. The script `sentence.py` draws at random, and
  its output still changes.
- The 100 s now go to these runs:
  - the 1.6 MB Apollo source: 44 s. The mint takes 14 s. The rest is the
    record of the source. The JSON record lists each connection in both
    directions and is 300 MB for that file.
  - the 4 memory runs: 15 s
  - `functions.py`: 7 s
  - `same_within.py`: 6 s
  - Alice and German: 3-4 s each

## 10-12 -- time

- Each record now has a `TIME` section, 1 level at a time. The section
  reads the sequence as time. The section has 3 tables:
  - ARROWS: a pair that occurs in both orders, with a count for each
    order (`said -> Alice` 25 against 7, `if -> you` 12 against 1).
  - EFFECTS: what occurs in the stretch after a run at a rate that is at
    least 2 times its usual rate. The table gives the real count against
    the count that the usual rate gives. Examples: `I` -> `think`, `know`, `can`;
    `a` -> `good`, `large`, `curious`; `little` -> `golden`, `door`,
    `key`; `the` -> `King`, `March`, `Rabbit`, `Hatter`.
  - CHAINS: the strongest effect, when the program follows the effect
    forward (`a -> good -> deal -> I -> think`). On the rope, the
    instruction flow loops back to itself: `22156 -> 63411 -> 74756 ->
    02031 -> 70000`.

  The stretch is the usual distance to the separator of the next level.
  Thus the unit of measurement comes from the signal.
- The time step was always present. The folder `examples/agc-live/` is
  the whole loop with a *do* step. But the core never read its own
  sequence as time, and no document named the time step. Section 10 of
  the paper now maps the 6 steps (roots, layers, interactions, crystals,
  relations, causes) to the code and to the scales. The guide
  reading-a-record.md has the TIME section.

## 10-12 -- persistence

- The file `paper/persistence.md` is a proposed alignment paper. A
  root-cause objective is an objective under which complex things
  continue. The comparator needs the thing, and needs the thing again
  (the loop opens again). A thing that is gone cannot be compared again
  (rule 4, deletion is irreversible). The root cause of a harm is
  upstream, and upstream is a need. The idea is persistence, not
  preservation: the thing continues on its own terms, and nothing keeps
  the thing frozen as it is.
- The baby model is the evidence of the paper. The loop got the goal
  "keep the baby from touching the hot stove." The loop proposed 3
  actions: change the baby, feed the baby, and read the baby to sleep in
  the crib. The loop went to the cause, and did not make a restraint.
  The baby model is not yet in this repository. The plan to repeat the
  baby model is in open.md. The plan has these parts:
  - a simulation with a baby, a stove, and needs
  - actions with no names. Each action removes a thing or satisfies a
    need.
  - the walk from the goal
  - what the loop proposes first, across worlds with different costs

## 10-12 -- each example on its own

- The front page now says to run 1 example, not to run all examples. The
  BREAKDOWN of each example opens with its own command. The record of
  each example is committed next to its input. The folders `extend/` and
  `hybrid/` have READMEs that list each script with its command and what
  the script writes. The table of folders links to each folder. The
  script `run_examples.sh` is the optional step that makes all records
  again.
- The documents now point at the records and the outputs, and do not
  quote run numbers. The change applies design rule 11 to the documents.
  The change covers FUNCTIONS.md, the self-assembly guide, the TIME
  examples in the paper and the guides, and the timings.

## 10-12 -- one shape for each program

- Each script in `extend/`, `hybrid/`, and `examples/german/bridge.py`
  now has the same 3 sections:
  - *the signal, as discovery.py reads it*, with the same lines in each
    script: read, frame, words, level 0. A script that reads a record has
    *the record, as discovery.py wrote it* in place of this section.
  - *NEW: the one new thing*
  - *what it found*

  Before, the hybrid scripts and the bridge were `main()` functions. Now
  the hybrid scripts and the bridge are flat, like the other scripts.
  Before, `same_slot.py` cut its runs by hand with the 2 separators. Now
  `same_slot.py` goes through `run_level`. Each output is the same as
  before, byte for byte. The guide `guides/building-from-discovery.md`
  shows the shape.
- Then the author made the root 1 call: `discovery.Root(path)`. The call
  does the read, the frame, the words, and level 0 on a shared pool. The
  root has 1 call for each more level, and has `all_levels()` and
  `draw()`. The 4 places to point are the arguments of the call, where
  the places are arguments (`separators`, `same`, the path). The function
  `discover()` is `Root` plus `all_levels()` plus the record. Thus the
  root of each program and the root of the program are the same call.
  The extensions are `R = D.Root(path)` plus their NEW section. The
  records and the outputs are the same, byte for byte.
- The note `notes/generations.md` is the proposal for the generations of
  AI. The generations are:
  - 1.0, made by humans
  - 1.1, with self-refinement
  - 2.0, neural networks
  - 2.1, hybrid
  - 3.0, a system that assembles itself and learns

  The note shows where this repository sits: 3.0 by the definition, with
  `hybrid/` as the point where the generations meet.
- The file `extend/template.py` is the shape to copy. The file has the 3
  sections, and the middle section is open for you to write. As the file
  stands, the middle section shows, for the most common runs, what
  follows them and how much of the time.
- The author put a name and an address on the work: Jason Weeks,
  thetuberobjective@gmail.com. The name and the address are in these
  places:
  - the Contact section of the README
  - the bylines of both papers
  - the LICENSE holder
  - the header of `discovery.py`
  - a `CITATION.cff`
  - the author of the commits from now on

## 10-12 -- the findings of a new reader, and the corrections

- A new reader did a cold read of the repository. The reader ran each
  example from a fresh checkout. The reader built and ran the emulator,
  and gave random bytes and a CSV file to the program. The reader tested
  the memory loop with a 2-byte file. The author corrected each problem that the reader found
  on the same day. The records without a memory are the same, byte for
  byte.
- The *confirmed* column of MEMORY counted the comparison of the memory
  with itself. A 2-byte file, run against the first-half memory,
  "confirmed" 11,476 of the 11,941 parts that the second half confirmed.
  In `mint()`, the first round compared each pair of neighbors, with the
  pairs from the memory included. Now a comparison counts only when the
  current signal is part of the comparison. The program counts a part
  from the memory that the signal makes again as confirmed. The program
  marks that part fresh for 1 more round. Thus the program still reaches
  each part that the program minted from that part the last time. The
  2-byte file now confirms 3 parts. The author made `examples/memory`
  again:
  - The second half confirms 10,588 parts (before, 11,941) and adds 9,337
    parts, as before.
  - The same half again confirms 19,833 of the 19,925 parts that the half
    made, and adds 0 parts and 5 parts, as before.
  - German confirms 14,797 parts (before, 18,971) and adds 17,987 parts,
    as before.

  The MINT line got a second line for memory runs: the parts from the
  memory that the signal made again, for each round.
- Before, a memory accepted signals at any frame width. But the same
  number means a different word at a different width. Now 1 memory has 1
  frame. The program refuses a signal at a different width and gives the
  reason. The user can read the signal with `--frame` instead.
- The memory file was a pickle. The memory file is JSON now. The JSON
  file contains the pool with counts, part_of, and history. The program
  makes made_of again at load. The program refuses an old pickle file and
  gives a note to remove the file.
- The program wrote the text record in the encoding of the locale. The
  program crashed on the German example under an ASCII locale. Now the
  program writes UTF-8. The same change is in `extend/functions.py` and
  `hybrid/loop.py`.
- The flag `--separators 20` had 2 possible meanings: the top 20 words,
  or the space character (byte 0x20). The program treats digits alone as
  a count. To name 1 specific word, use `0x20` or `20,` (record tag
  `.sepx20`). An option that the program does not have, or an option
  with no value, now gives an error message. Before, the program ignored
  the option with no message, or gave a traceback. The flag `--limit 0`
  reads nothing, and does not read everything.
- The script `run_examples.sh` failed without
  `/usr/share/dict/american-english`. Now the script omits `functions.py`
  and writes a note, in the same way as the script already did for
  numpy.
- The author added a note to the guides: the program decides the frame
  from the first 64 KB.
- The author measured the behavior below and did not change the program.
  Random bytes fold to a frame of 1 bit and mint nothing at level 0.
  Then the levels above mint from the run-length sequence, like any
  signal. Two noise files with no relation confirm 40-50 percent of the
  level-1 parts and the level-2 parts of each other. A null for the mint
  and the levels is in open.md as a design question. A null is a baseline
  for the question "is this real or just chance?".
