# Design rules

The rules Discovery was built by. Each one is stated as a rule, then shown where it lands in the code.

## 1. A comparator and a memory are the only tools you need

To find anything, look at the before and after and check for differences. A comparator plus a memory to hold something to compare against is enough to start. Everything else is that pair run again.

*In the code:* every function in `discovery.py` is a comparison of two things with the three-way result (same, different, not part), or a count of such results.

## 2. Same, different, not part

What is different does not get thrown away — it gets sorted. These three channels show up at every level: in the frame step as a constant column versus a changing one, in the mint as the shared head versus the leftovers, in the bridge as a part in both records versus a part in one.

*In the code:* `shared_head()` returns the length of the same part. The caller takes the leftovers. What the pair never shared is left alone.

## 3. Keep smashing things together until nothing new comes out

Collide, mint, put back in the pool, loop. The fixed point — a round that produces nothing new — is the only stopping rule.

*In the code:* `mint()`; the `while True` ends on `if not new: break`.

## 4. Nothing is ever removed

Never delete means never erase. A part found once is kept with the same standing as a part found a thousand times. Rare but real is worth having. Compression is storing a thing once with a count, not throwing things out.

*In the code:* the pool is a dict keyed by content. Counts are values. There is no deletion anywhere.

## 5. What contains a thing and what it connects to are its definition

A part's connections — what it is made of, what it is part of, what it changes into, what sits next to it — are its definition. Density is the number of things that contain it.

*In the code:* `made_of`, `part_of`, `changes_of()`, and the FOLLOWS and RUN FOLLOWS tables. Density is `len(part_of[p])`. The CRYSTAL entry is those connections printed for one part.

## 6. The crystal makes groups but does not collapse them

It builds a grouping and leaves the pool as it is. It sees the whole pool each round, including what it made before. Each new thing goes back in for the next round: crystallize, then loop again, until nothing changes. You do not replace — you add: a run has 300 parts, the next level adds 50 for 350, the next adds 25, the next 5, then stable.

*In the code:* `crystallize()` reads the pool and writes a `classes` table. Minted parts rejoin the pool and are sorted with everything else on the next round. `run_levels()` runs the next level on the runs as they are, with the classes as a second way two things can count as "the same" in `mint()`'s `head()`. Every new part goes into the one shared `pool`, until a level is left with a single run. The additions reach zero before that. The LEVELS table in the record is the 300 / 350 / 375 / 380 count.

## 6a. Feedback and evaluation are the same comparator

"Does the model match reality?" and "is this the same as that?" are the same question. Evaluation was always there — it just was not looped. The loop is memory: the pool saved after one signal, the next signal compared against it, the difference added.

*In the code:* `load_memory()`, `save_memory()`, the `memory` argument to `mint()` and `run_levels()`, and the MEMORY table in the record (confirmed / added / not seen this time).

## 7. Define nothing — start from zero

Only input, output, and its own code. No target, no notion of right or wrong, no feature list, because what you tell it to look for may not be what it needs to find. Every output is there for a reason — never treat it as nothing.

*In the code:* no file-type table, no character set, no tokenizer, no stop list, no training. The lens is display-only. The one tolerance is computed from the signal.

## 8. Knowledge is a dictionary entry

The form of what is known is a dictionary entry: a thing, its forms, and the change between them. Classes are things that take the same changes.

*In the code:* `changes_of()` and the CLASSES and CRYSTAL tables.

## 9. Take the easy path

Do not pre-solve predicted problems. Do not add checks and filters that were not asked for. Build and be surprised. Address issues as they come up. Pull everything in, and never treat a common, highly-connected part as unimportant — connection means meaning.

*In the code:* the separator is the most common word, full stop. The sorted-neighbor collide is the plain way to find shared heads. No part is dropped for being common. The cap and the fresh-pair rule were added when a 1.6 MB file ran out of memory, not before.

## 10. Loop until stable

Repeat until no new information comes out. The remainder at that point is reported, not hidden.

*In the code:* the MINT line in the record lists the parts produced per round down to 0.

## 11. The thing stands for itself

No claims in the documents. The records are the evidence, and the breakdowns say how to read them and how to check them against an outside source where one exists.

*In the repo:* `examples/*/BREAKDOWN.md`.

## The choices it does make

Rule 7 says define nothing, and the program defines no file types,
alphabets, or targets. But it does make a few decisions about how to
look at a signal, and a reader should know where they are:

- **Words are compared as ordered sequences**, from the front and from
  the back. Shared middles are found only when the loop exposes them
  as a beginning or ending of a leftover.
- **The separator is the most common word.** Runs are what sit between
  copies of it. A different cut gives different runs.
- **The frame is the width with the widest spread of column rates**,
  folded down if a smaller width explains it.
- **Two things are "the same" at a level above 0** if they are the same
  run or belong to the same class one level down. Nothing else counts
  as same.

These are the places where another choice would give a different
record from the same signal. `extend/` shows three of them changed.
