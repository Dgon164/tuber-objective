# Work log

This log records what the author built, in the order it was built, and
what each run of the program changed. The program is Discovery,
`discovery.py`: it reads any file as raw bits and finds the file's
structure by comparing pieces of it with each other, with no file-type
list, no dictionary and no training. All dates are in 2026.

## 10-09, morning -- the core

- The author wrote `discovery.py` as one file with no dependencies. The
  file does seven steps, in this order. It reads the file as one long
  string of bits (the signal). It works out how wide one unit is, by
  finding the bit width at which the columns of bits line up (the
  frame). It cuts the bits into units of that width and counts them (the
  words). It takes the most common unit as a divider, called the
  separator, and cuts the file into the pieces between separators (the
  runs). It compares the runs with each other and, whenever two of them
  start or end the same way, makes a new part out of the shared piece
  and the two leftovers (the mint; to mint a part is to make a new part
  from two parts that have the same start or the same end). It groups
  the parts that take the same additions (the crystal). And it writes
  everything it found to a file (the record).
- The first run on `alice.txt` found a unit width of 8 bits and 73
  distinct words. At 8 bits a word is one character, so that is 73
  distinct characters. The run picked the space character as the
  separator, so the runs were the words of the book, and `the` was the
  most common run. The part found inside the most other parts was `e`.
  The number of other parts that contain a part is called its density,
  so `e` had the highest density. The run also found a group of 22 stems
  (word bases such as `walk`, the part that endings attach to) that all
  take both `+ed` and `+ing`. A group of parts that take the
  same set of additions is a class, written here as `[+ed, +ing]`. The
  run took 4 seconds.
- The frame step lays the bits out in rows of a trial width and looks at
  each column: how often that column holds a 1. At the right width each
  column has its own steady rate; at a wrong width the bits mix and
  every column drifts toward half. The first rule for picking a width
  took the single most lopsided column, the one closest to always 1 or
  always 0. That rule chose a width of 40 on the German file, which is
  wrong. The reason: in UTF-8 text the top bit of a byte is 1 in 3.6
  percent of the bytes, so no column is ever completely constant, and a
  wider trial width has more columns, so the most extreme one gets more
  extreme just by chance. The author replaced the rule with the spread:
  the gap between the most constant column and the least constant one.
  Under the new rule a wider width beats a narrower one only if its
  spread is larger, and larger by more than chance alone would give at
  that number of rows.
- In the compiled C program, 93 percent of the bytes are zero. Under the
  old rule every width scored the same. The spread rule picks 64 bits,
  and the column rates at that width show how the machine lays out
  numbers: it stores the low byte of a number first, so a small number
  puts its 1 bits in the first byte and leaves the rest zero, and the
  rate of 1s falls off from the first byte of each 64-bit word to the
  last. That is the little-endian pattern, and it is visible in the
  rates alone.
- The author added `--frame N`, which lets you set the unit width
  yourself instead of letting the program pick it. With it, a compiled
  program can be read at the byte level as well as at the width the
  program picked for it.
- The author added `--separators N`, which cuts the file at the N most
  common units instead of only the single most common one. The Alice
  record prompted this. The newline `\n` had the second highest density
  of any part, but its whole count, the number of times it appeared as a
  complete run on its own, was zero. That is the sign of a divider the
  program did not cut at: it sits inside lots of runs because nothing
  split them there.
- Each common part gets a crystal entry, which is like a dictionary
  entry for that part. One line of the entry is its `changes`: what you
  add to the part to turn it into another part, such as `+ed` on `walk`.
  Those changes used to be listed alphabetically, so punctuation filled
  the top of every list. They are now listed by how common the larger
  part each change produces is, so the most-used changes come first.

## 10-09, morning -- the examples

- The German file is a day of European Parliament debate (Europarl)
  stored as UTF-8. In UTF-8, a letter such as an umlaut takes two bytes,
  and the first of them is a fixed lead byte. That lead byte, `\xc3`,
  showed up as a word of its own with a count of 2,827. The run found the
  endings `+en`, `+ung` and `+lich` and the beginnings `be+` and `ge+`.
  It found one class of 52 verb stems and another of 42 adjective stems,
  and it found pairs of words that begin with capital letters.
- The script `bridge.py` takes two records and finds what they share.
  Run on the German record and the English record, it found 2,188 shared
  parts. Among them are `technologi`, `transport`, `programm`,
  `instrument` and `international`, each listed with the words that
  contain it on the German side and on the English side. Proper names
  are shared too.
- The author ran Discovery on Discovery's own source code. The most
  common words were `=`, `in`, `for`, `if` and `return`, and the part
  with the second highest density was `(`. The author also ran it on the
  compiled `hello` program twice, at 64 bits and at 8 bits. The 64-bit
  run shows the layout of the file. The 8-bit run finds the readable
  strings inside it: `usage: hello TEXT`, `strlen`, `puts`, `hello.c`,
  the compiler version and the loader path.
- The `hybrid/` folder holds scripts that connect Discovery to other
  kinds of system. `record_to_rules.py` reads a record and turns it into
  three kinds of rule that another program could run: which run comes
  next, which parts are forms of the same word, and which parts are the
  same kind of thing. `net_as_lens.py` runs a small neural network, a
  reservoir of 32 units with fixed random connections, over the text,
  writes the network's internal states out as bits, and hands those bits
  to Discovery as a new file. Discovery found the 32-bit width on its own,
  and the units that never fire show up as constant columns in the column
  rates. `loop.py` follows the rules from `record_to_rules.py` to write a
  new text, reads that text as a signal, and compares the new record with
  the original: 8,543 parts shared, 13,903 lost and 1,925 new.

## 10-09, late morning -- the Apollo Guidance Computer

- Luminary 099 is the flight program of the Apollo 11 Lunar Module, and
  it ran on the Apollo Guidance Computer, whose words are 15 bits wide.
  The Virtual AGC project publishes the program as a listing in octal
  (base 8), in the public domain. The author packed that listing into
  15-bit words with no gaps between them. The frame step picked a width
  of 60, which showed that picking the widest spread is not enough on
  its own: 60 is 15 x 4, and the spread measure creeps up a little when
  the same columns are repeated more times. So the author added the
  fold. To fold is to step down from the width the frame step picked to
  a smaller width that divides it, when the column rates at the wide
  width are just the rates of the smaller width repeated. The repeat has
  to match within what chance variation allows. The fold took 60 down to
  15.
- The packed file is called the rope, after the read-only rope memory
  the real machine ran from. In its record, the most common word is
  00006, the machine instruction EXTEND, so 00006 became the separator.
  The words 04616, 06037, 05353, 04674 and 04635 always appeared with the
  same partners. The author checked the record against the source
  listing and found that those are the first words of subroutines, the
  named blocks of code that each do one job, in the listing: BANKCALL,
  INTPRET, PHASCHNG, IBNKCALL and POSTJUMP.
- The assembly source of the program, the human-readable text the
  machine code was built from, is 1.6 MB. The first run, cutting at one
  separator (the tab), grew the pool, the collection of every part found
  so far, past the machine's RAM and had to be stopped. The author made
  two changes.
  First, the mint now compares two neighbouring parts only when one of
  them is fresh from the last round, since two parts that were both there
  last round were already compared then. The results are the same, and
  the Alice run went from 4 s to 2 s. Second, a new flag `--cap`, with a
  default of 1,000,000 parts, stops the loop if the pool reaches that
  size and writes a note in the record saying so. With `--separators 2`,
  the source now runs in 19 s.
- The author added `--lens octal`. A lens only changes how the record
  prints a word, never what the program finds, and this one prints words
  in base 8. With it, the rope record reads the same way as the public
  listing.
- Record file names now include `.frameN` and `.sepN` when you set those
  options, so two runs on one file with different settings no longer
  overwrite each other.

## 10-09, midday -- crystallize, then loop again, until no change

- To crystallize is to sort the parts in the pool into classes, groups of
  parts that take the same additions. At first the crystal ran only once,
  at the end: it made classes, and nothing used them. Jason gave this
  direction: "crystallize then loop again; loop until no change; it will
  stabilize and run out of new connections."
- The first version of looping again worked in two steps. It replaced
  every run that belonged to a class with that class's label, then ran
  the whole program on the copy. Jason said: "You don't replace. You add.
  Run has 300, next has 50 added structures for 350, then 25 for 375,
  then 5 for 380, then stable."
- So the author changed the program to use one shared pool. The next
  level runs on the runs of the level below, unchanged: it treats each
  run as a unit, finds the most common one, cuts at it, and mints again.
  The classes from the level below give the mint a second way for two
  units to count as the same: they match if they are the same run, or if
  they are two members of one class. When two sequences differ only in a
  position where each has a member of the same class, the class itself
  stands in that position of the part they share. Every run of runs,
  every new minted part and every class, as a unit of its own, goes into
  the same pool.
  The connections of each new part land on the parts it contains, so a
  low-level part's density grows when higher-level parts include it. A
  run that consists of a single run is just that run. The loop stops when
  a level adds nothing, or when a level is left with only one run.
- The counts match the description Jason gave:
  - Alice 22,446 -> +6,709 -> +5 -> +1
  - German 19,210 -> +14,943 -> +9 -> +1
  - Apollo rope 8,538 -> +11 -> +1
  - Apollo source 126,406 -> +121,058 -> +11 -> +1

  At level 0, `said` is contained in 16 parts. Once the level-1 stretches
  that hold `said` are counted too, that number rises to 444.
- The class-as-same match, two units counting as the same because they
  belong to one class, fired 0 times on the four signals. The reason is
  that the members of a class are stems like `walk`, not whole runs like
  `walked`, so they never sit in a run's slot. The author wrote a note on
  this in open.md.
- The record now opens with a LEVELS table that has columns for *added*
  (how many parts each level put into the pool) and *pool total*, and
  then prints the full set of tables for every level. The JSON record,
  the copy of the record written for programs rather than people, has a
  `levels` list and the pool size. The hybrid scripts and `bridge.py`
  read `levels[0]`, the first level. The JSON records are no longer
  committed to the repository because they are large; the script
  `run_examples.sh` rebuilds them in about 2.5 minutes, most of which
  goes to the 1.6 MB Apollo source.

## 10-09, late morning -- the end-compare in a loop

- Jason gave five steps of understanding: identification, association,
  reduction, composition and evaluation. The file already had the first
  four. Evaluation looked like it was missing. Jason corrected that view:
  evaluation is the root comparison itself, "is the end-compare real, or
  is this the same as that". So evaluation was already in the file, but
  it was not being run in a loop.
- The author added `--memory FILE`. With it, the program loads a saved
  pool of parts before a run and saves the pool back after. The pool is
  kept sorted so that parts with the same start sit next to each other,
  which is how the mint finds shared starts, and the remembered parts are
  sorted in among the runs of the new signal. So a new run gets compared
  with what the program remembers in the same way it gets compared with
  the rest of its own file. That comparison is association against the
  memory: "have I seen something like this before?". The program sorts
  what it finds into three groups: confirmed (it was in memory and the
  new signal made it again), added (it is new) and not seen this time (it
  was in memory and the new signal did not make it). Nothing is removed.
- The test is in `examples/memory/`. The first half of Alice, run with no
  memory, adds 14,079 parts. The second half, run against that memory,
  confirms 11,941 parts and adds 9,337. The second half run again
  confirms 21,278 parts, adds 0 at level 0 and adds 5 at level 1. Those 5
  are parts with a class standing in one slot, the first time the
  class-as-same match has fired on real text. The German file, run
  against the English memory, confirms 18,971 parts and adds 17,987.
- The level loop now always runs until a level is left with one run.
  Before, it stopped at the first level that added nothing. With a
  memory, level 0 can add nothing while level 1 still adds parts, so the
  old stop rule would have cut the run short.

## 10-09, noon -- how to make new things from Discovery

- Jason said: "How do we show that you can build from this. The general
  claims and how to expand and build from them. Explain why the
  prerequisites are enough."
- The author wrote `guides/building-from-discovery.md`. A given is a thing
  the program is handed rather than something it finds; the cut, for
  instance, is the step that divides the signal into runs at a separator,
  and the rule for choosing that separator is a given. The guide covers
  four things:
  - the eight givens, and where each one shows up in the records
  - the argument that those givens are enough: every step of the program
    is the same comparison pointed at a different thing, and no extension
    so far has needed a new operation
  - the four places you can point the comparison somewhere new: the cut
    (where the signal is divided), the kind of same (what counts as a
    match), the comparison target (what a thing is compared against),
    and the signal itself
  - how to add a new thing
- The `extend/` folder holds three extensions as evidence. Each is a few
  lines that call discovery.py.
  - `cut_at_class.py` cuts level 1 at the class {+ed, +ing} instead of at
    the most common word, so the level-1 runs are the stretches between
    verbs. The words that come right before a verb are: and, to, she. The
    words that come right after one are: herself, out, the, a, at.
  - `same_within.py` changes what counts as the same on the Apollo rope:
    two words that fall in the same band of 8 (the same value with the
    low three bits ignored) match. That makes two instructions that point
    at nearby addresses count as one. The parts went from 8,538 to 50,319,
    and 2,580 of them have a band standing in a slot. The part
    `05353.~04020` collects the PHASCHNG calls across all their argument
    codes, the values each call passes along with it.
  - `row_by_row.py` takes the reservoir states from `net_as_lens.py` and
    compares each state with the next. Units 28, 21 and 2 never change.
    On average 8.38 bits flip per step. The most common joint flip, the
    same set of units changing together, happened 149 times. Read as a
    signal of their own, the flips give a width of 32 and 6,701 distinct
    changes.

## Tasks that remain before publication

- Run `run_examples.sh` from a fresh checkout, with nothing left over
  from earlier runs.
- Read each document and check it against the new records.
- Write the licence file.

## 10-10 -- the flight program in operation

- The folder `examples/agc-live/` runs the Apollo flight program on an
  emulator, a program that imitates the original computer, instead of
  only reading the program as a file. The folder contains four things:
  - the Virtual AGC emulator with a trace patch. The patch is a small
    change to the emulator that writes a log line for every write the
    flight program makes to its erasable memory (the part of memory the
    program can change) and for every packet that passes on a channel
    (a numbered signal path between the computer and its hardware).
  - a socket client, a script that connects to the running emulator and
    presses keys on the DSKY, the computer's keyboard and display
  - a build script
  - one recording that Discovery read. Discovery found on its own that
    each write record is 80 bits wide, and the most common words it found
    are the idle loop, the small set of writes the computer repeats when
    it has nothing to do.

## 10-11 -- the nudge, the loop, the launch

- The folder `nudge-run/` holds two flights from the 10-10 package, both
  with the same setup. In one of them the spacecraft gets a kick, a short
  push that starts it turning. The author ran the bridge, the step that
  finds what two records share and what is in only one of them, on the
  words of each recording and on the flips (the fields that changed from
  one row to the next), with all the recordings on one shared clock. The
  result put the whole reaction-control autopilot on the side of the
  kicked flight only. The reaction-control autopilot is the part of the
  flight program that keeps the spacecraft pointed the right way by
  firing small jets. The kicked-only side held the Y gimbal pulses coming
  in (the signals that report turning about the Y axis), the jet bits
  going out (the commands that fire the jets), and the turning rates of
  the vehicle. The author added the names only after the run; the bridge
  saw none of them. The vehicle's rows of readings, read at 16 bits so
  that each field is its own word, showed the rate plateaus, stretches
  where the turning rate holds steady between one jet firing and the
  next. The rows also showed the kicked axis as the one field that moves
  while its neighbours stay constant. This result opens a new question
  that is not yet answered.
- The scripts `loop.py`, `walk.py` and `do.py`, with their output in
  `phase-a/`, run a loop on the DSKY (the Apollo keyboard and display).
  The loop presses a key, records what the machine shows, compares that
  with what it remembers, and chooses the next key to press. It was given
  33 raw key codes and no names for any of them. From 250 key presses it
  built a map of which press takes the display from one state to another,
  and that map is the DSKY's input grammar: VERB, then a digit, then a
  digit. The walk then goes backward through that map from a display
  word you ask for to the key presses that lead to it. The author pressed
  those sequences again on a fresh machine, and the asked-for words
  appeared. For a word the loop had never seen, it made no plan.
- In `phase-b/`, the author attached the simulated vehicle to the same
  loop with no other change. The loop was given a goal row, the state of
  the vehicle's readings you want it to reach. The loop never reached the
  goal row, and the record shows why: the engine never came on, and the
  vehicle hit the ground at 136 s.
- The author added a start on the launch pad and the astronaut's direct
  controls (arm, engine on and off, throttle, hand controller) to
  `vehicle.py`, and wrote `launch.py`. In `phase-c/`, 3,480 key presses
  over three lives, three separate runs of the vehicle, built an effects
  table: for each control, which readings changed when it was pressed,
  and in how many of the tries. The table shows:
  - engine on: thrust, accelerometer, propellant, engine, 13 of 13
  - throttle up: thrust, 14 of 14
  - 24 DSKY codes: nothing

  Given a goal row, the loop found a sequence of 22 presses: arm, engine
  on, four notches of throttle, lift-off, hold. The vehicle rose to 223 m.
- The note `notes/review-2026-10-11.md` checks the 10-10 package against
  the design rules.

## 10-12 -- functions, sentences, and the launch

- The script `extend/same_slot.py` groups words by the places they occur
  in: two words go together when they turn up with the same word on the
  left and the same word on the right. The groups it found were pronouns,
  modals (words such as "can," "will," "should"), the characters of the
  book, and determiners ("the," "a"). Those groups are parts of speech,
  and the script was given no labels.
- In `extend/functions.py`, the changes Discovery found become functions.
  A function is a thing that turns one part into a different part, the
  way `+ed` turns `walk` into `walked`. The script learns each function's
  in-kind and out-kind from the record: the in-kind is the kind of thing
  the function acts on, worked out from which other functions those
  things also take, and the out-kind is the kind of thing it produces,
  worked out the same way. Two functions are siblings when they act on
  the same inputs. Before the script tries a function on a new part, it
  gives the try a standing: the number of the part's functions that are
  siblings of the one being tried, minus the number that are not. It
  tries the highest standing first. It keeps two kinds of memory of how
  tries went, at two levels: a hold for each (function, sibling) pair,
  which records that the function works on the things its sibling works
  on, and a negative flag, set after repeated refusals, which says it
  does not; the same two things are kept for whole functions. The script
  made 100 new English words that are not in Alice, with 985 tries that
  failed, in 6.3 seconds. Getting there took four approaches:
  - open, trying anything: 3,341 failures
  - feedback kept for each ending: 7,871 failures, worse
  - negative groups: 662 failures
  - functions over the record: 985 failures in 6 s. The structure found
    in the record is itself the feedback.
- The file `extend/FUNCTIONS.md` is the report on the functions work.
- The script `extend/sentence.py` makes sentences from the follows table,
  the table in the record that says which run comes after which. It
  chains word pairs (each word and the word that follows it) from a
  starter to an ender. A starter is a word that comes right after the
  punctuation that ends a sentence. It made 15 sentences in 1.4 seconds.
- The author did not keep the class-pair approach as a script. That was
  the earlier version of the word maker. `FUNCTIONS.md` describes it in
  its section on earlier tries.
- The author corrected the line count in the paper (470 -> 726).
- The author rewrote the README. It opens with Wheeler ("it from bit")
  and Bateson ("a difference that makes a difference") and shows how
  Discovery takes both quotations literally.
- The note `notes/on-the-bitter-lesson.md` presents Discovery as the
  Bitter Lesson taken to its logical limit. The Bitter Lesson is the
  argument that methods built on search and computation beat methods
  built on human knowledge; Discovery uses no human knowledge at all.
  Knowledge is what comes out, not what goes in.
- The guide `guides/thinking-in-self-assembly.md` is about how to work
  with a system that builds its own structure. Don't help the system.
  Run it. Then find the difference it is missing.
- The author published the repository at
  github.com/dgon164/tuber-objective, public, under the MIT licence.

## 10-12 -- the cold run, 4 times faster

- Run from a fresh checkout, `run_examples.sh` went from 393 s to 100 s.
  Every record is the same as before, byte for byte. The author measured
  where the time went before changing anything: on Alice, 85 percent of
  it went to writing the record, not to finding the structure.
- Writing the record. The JSON record gives every part a key, and the
  program used to compute a part's key again for every connection that
  mentioned the part, with `key_of` walking through each nested value
  every time. Now each part gets its key once, in a `Keys` table. The
  author swapped `json.dump`, the encoder written in Python, for
  `json.dumps`, the one written in C, and the program writes the output as
  bytes. Drawing a level-2 part for the text record, which means printing
  it in readable form, now stops at the display width; before, the
  program drew the whole book and trimmed the extra text after. The
  density table finds its top 25 by keeping the 25 largest as it goes,
  instead of sorting every part.
- The mint. The program now keeps the pool in both sort orders (forward
  and reversed) between rounds and merges each round's new parts into
  their places, instead of sorting from scratch. It compares only the
  pairs that include a fresh part, which is the natural extension of the
  fresh-pair rule that open.md had asked for. The same pairs meet in the
  same rounds, so the pool comes out the same: Alice 22,446 -> +6,709 ->
  +5 -> +1, as before. Finding the plain shared start, with no classes
  involved, has its own fast path. At level 0 a part is its own node
  rather than a wrapper around one. And `changes_of`, which works out what
  you add to a part to get a larger one, looks at the first and last
  values before slicing.
- A comment on the memory in `mint()` said that the program does not
  compare two parts from memory with each other again. The code always
  did compare them, and that comparison is how a remembered part comes
  out again and counts as confirmed. The author corrected the comment.
  The code did not change.
- In `extend/functions.py`, `standing()` now counts a part's sibling
  functions with a set intersection. The count is the same, at the speed
  of C. The phase that makes words went from 5.9 s to 3.3 s for 20 words.
- `run_examples.sh` now sets `PYTHONHASHSEED=0`. Python mixes a random
  number, different for each process, into how it orders strings in sets
  and dictionaries. `functions.py` keys on strings, so its tie-breaks
  followed that random number and its output changed on every run.
  Fixing the number makes each run come out the same. `sentence.py` draws
  at random on purpose, so its output still changes.
- The 100 s now go to these runs:
  - the 1.6 MB Apollo source: 44 s. The mint takes 14 s. The rest is
    writing the record: the JSON record lists each connection in both
    directions and comes to 300 MB for that file.
  - the four memory runs: 15 s
  - `functions.py`: 7 s
  - `same_within.py`: 6 s
  - Alice and German: 3-4 s each

## 10-12 -- time

- Each record now has a `TIME` section, one per level, that reads the
  order of the sequence as time: what came before and what came after.
  It has three tables:
  - ARROWS: pairs that occur in both orders, with a count for each order,
    so you can see which way round is usual (`said -> Alice` 25 against
    7, `if -> you` 12 against 1).
  - EFFECTS: what shows up in the stretch after a run at least twice as
    often as it shows up in general. The table gives the real count next
    to the count you would expect from the usual rate. Examples: `I` ->
    `think`, `know`, `can`; `a` -> `good`, `large`, `curious`; `little`
    -> `golden`, `door`, `key`; `the` -> `King`, `March`, `Rabbit`,
    `Hatter`.
  - CHAINS: the strongest effect, followed forward step by step (`a ->
    good -> deal -> I -> think`). On the rope, the flow of instructions
    loops back on itself: `22156 -> 63411 -> 74756 -> 02031 -> 70000`.

  The stretch is the usual distance from one run to the next separator
  of the level above, so the unit of time comes from the signal itself,
  not from a setting.
- The time step was always there. The folder `examples/agc-live/` is the
  whole loop with a *do* step, where the program acts and records what
  happens. But the core program had never read its own sequence as time,
  and no document named the time step. Section 10 of the paper now maps
  the six steps (roots, layers, interactions, crystals, relations,
  causes) to the code and to the scales each one works at. The guide
  reading-a-record.md now has a TIME section.

## 10-12 -- persistence

- The file `paper/persistence.md` is a proposed alignment paper. Its
  claim is that a system whose only job is finding root causes keeps
  complex things alive. The reasoning: the comparison needs the thing it
  compares against, and needs it again the next time the loop runs. A
  thing that is gone cannot be compared again (design rule 4: remove
  nothing, because deletion cannot be undone). And the root cause of a
  harm sits upstream, and upstream of a harm is a need that was not met.
  The idea is persistence, not preservation: the thing continues on its
  own terms, and nothing holds it frozen as it is.
- The paper's evidence is the baby model. The loop was given the goal
  "keep the baby from touching the hot stove." It proposed three actions:
  change the baby, feed the baby, and read the baby to sleep in the crib.
  It went to the cause, the baby's unmet needs, and did not propose a
  restraint. The baby model is not yet in this repository. The plan to
  repeat it is in open.md and has these parts:
  - a simulation with a baby, a stove and needs
  - actions with no names, each of which removes a thing or satisfies a
    need
  - the walk backward from the goal
  - what the loop proposes first, across worlds where the actions have
    different costs

## 10-12 -- each example on its own

- The front page now tells you to run one example, not all of them. Each
  example's BREAKDOWN opens with its own command, and each example's
  record is committed next to its input, so you can read before you run.
  The `extend/` and `hybrid/` folders have READMEs that list every script
  with its command and what it writes. The table of folders links to each
  folder. `run_examples.sh` is the optional step that rebuilds every
  record.
- The documents now point at the records and the outputs instead of
  quoting run numbers in the text. This applies design rule 11, that the
  records are the evidence, to the documents themselves. The change
  covers FUNCTIONS.md, the self-assembly guide, the TIME examples in the
  paper and the guides, and the timings.

## 10-12 -- one shape for each program

- Every script in `extend/` and `hybrid/`, and `examples/german/bridge.py`,
  now has the same three sections:
  - *the signal, as discovery.py reads it*, with the same lines in every
    script: read the file, find the width, cut the words, run level 0.
    A script that reads a record instead of a file has *the record, as
    discovery.py wrote it* in place of this section.
  - *NEW: the one new thing*
  - *what it found*

  Before, the hybrid scripts and the bridge were wrapped in `main()`
  functions. Now they are flat, top to bottom, like the other scripts.
  Before, `same_slot.py` cut its runs by hand using the two separators.
  Now it goes through `run_level`, the same function the core uses. Every
  output is the same as before, byte for byte. The guide
  `guides/building-from-discovery.md` shows the shape.
- Then the author made the starting point one call: `discovery.Root(path)`.
  That call reads the file, finds the width, cuts the words and runs
  level 0 on a shared pool. The result has one call for each further
  level, plus `all_levels()` to run them all and `draw()` to print a part
  in readable form. The four places you can point the comparison are
  arguments of that call where they are arguments at all (`separators`,
  `same`, and the path). The program's own `discover()` is `Root` plus
  `all_levels()` plus writing the record, so every program built on
  Discovery and Discovery itself now start from the same call. The
  extensions are `R = D.Root(path)` followed by their NEW section. The
  records and the outputs are the same, byte for byte.
- The note `notes/generations.md` proposes a way of numbering the
  generations of AI:
  - 1.0, built by people
  - 1.1, built by people, able to tune itself
  - 2.0, neural networks
  - 2.1, hybrids of neural networks and other methods
  - 3.0, a system that builds its own structure and learns from nothing

  The note places this repository at 3.0 by that definition, with
  `hybrid/` as the point where the generations meet.
- The file `extend/template.py` is the shape to copy. It has the three
  sections, with the middle one left open for you to write. As it
  stands, the middle section shows, for the most common runs, what comes
  after them and how much of the time.
- The author put a name and an address on the work: Jason Weeks,
  thetuberobjective@gmail.com. They appear in these places:
  - the Contact section of the README
  - the bylines of both papers
  - the LICENSE holder
  - the header of `discovery.py`
  - a `CITATION.cff`
  - the author of the commits from now on

## 10-12 -- the findings of a new reader, and the corrections

- A new reader went through the repository cold. They ran each example
  from a fresh checkout, built and ran the emulator, and fed the program
  random bytes and a CSV file. They tested the memory loop with a 2-byte
  file. The author fixed each problem they found on the same day. The
  records made without a memory are the same as before, byte for byte.
- The *confirmed* column of the MEMORY table was counting the memory
  against itself. A 2-byte file, run against the first-half memory,
  "confirmed" 11,476 of the 11,941 parts that the whole second half had
  confirmed, which is nonsense for two bytes. The cause was in `mint()`:
  the first round compared every pair of neighbours in the sorted pool,
  including pairs where both parts came from memory. Now a comparison
  counts only when the current signal is one side of it. A part from
  memory that the signal makes again counts as confirmed, and the program
  marks it fresh for one more round, so the signal can still reach the
  parts that were minted from it last time. The 2-byte file now confirms
  3 parts. The author rebuilt `examples/memory`:
  - The second half confirms 10,588 parts (before, 11,941) and adds
    9,337, as before.
  - The same half run again confirms 19,833 of the 19,925 parts it made,
    and adds 0 and 5, as before.
  - German confirms 14,797 parts (before, 18,971) and adds 17,987, as
    before.

  The MINT line of the record, which lists what each round made, got a
  second line for memory runs: the parts from memory that the signal made
  again, round by round.
- Before, a memory would accept a signal read at any unit width. But the
  same number is a different word at a different width, so mixing widths
  in one memory makes the comparisons meaningless. Now one memory has one
  width. The program refuses a signal at a different width and says why.
  You can read the signal at the memory's width with `--frame` instead.
- The memory file used to be a pickle, Python's own binary save format,
  which only Python can read. It is JSON now, a plain text format. The
  file holds the pool with its counts, the part_of table (which parts
  contain each part) and the history of the signals that went in. The
  program rebuilds made_of (what each part is made of) when it loads the
  file. It refuses an old pickle file and tells you to remove it.
- The program wrote the text record in whatever character encoding the
  system's locale was set to, and crashed on the German example under an
  ASCII locale. Now it always writes UTF-8. The same change went into
  `extend/functions.py` and `hybrid/loop.py`.
- The flag `--separators 20` could have meant two things: the top 20
  words, or the space character (byte 0x20). Now digits on their own
  always mean a count. To name one specific word, write it as `0x20` or
  `20,`; the record tag is then `.sepx20`. An option the program does not
  have, or an option with no value, now gives an error message; before,
  the program ignored it silently or printed a traceback. `--limit 0`,
  which sets how many bytes to read, now reads nothing rather than
  everything.
- `run_examples.sh` failed when `/usr/share/dict/american-english`, the
  word list `functions.py` checks its words against, was not there. Now
  the script skips `functions.py` and writes a note, as it already did
  when numpy was missing.
- The author added a note to the guides: the program decides the unit
  width from the first 64 KB of the file.
- The author measured the behaviour below and did not change the
  program. Random bytes fold to a width of 1 bit and mint nothing at
  level 0, because no two runs share a start. The levels above then mint
  from the sequence of run lengths, as they would with any signal. Two
  noise files with no relation to each other confirm 40-50 percent of
  each other's level-1 and level-2 parts. A null for the mint and the
  levels is listed in open.md as a design question. A null is a baseline
  for the question "is this real, or just chance?", such as the same
  signal in random order, so that a result has to beat it before it
  counts.
