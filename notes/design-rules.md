# Design rules

These are the rules Discovery was built on. Each one is stated as a rule, then I show where it shows up in the code.

## 1. You only need two things: a comparator and a memory

To find anything, you look at what came before and what came after, and you check for differences. A comparator (something that checks "are these two things the same?") plus a memory (somewhere to stash the thing you're comparing against) is enough to get started. Everything else in the system is just that pair used again and again.

*In the code:* every function in `discovery.py` is a comparison of two things that gives one of three answers (same, different, not part), or a count of those answers.

## 2. Three buckets: same, different, not part

What's different doesn't get thrown away -- it gets sorted. These three buckets show up at every level of the system: in the frame step, where a column either stays constant or changes; in the mint, where two sequences share a common beginning and the rest is leftovers; in the bridge, where a part appears in both records or only in one.

*In the code:* `shared_head()` returns the length of the matching part. The caller takes whatever's left over. What the pair never had in common is left alone.

## 3. Keep smashing things together until nothing new comes out

Collide two things, mint what you find, put it back in the pool, repeat. The only reason to stop is a round that produces nothing new -- that's the fixed point.

*In the code:* `mint()`; the `while True` ends on `if not new: break`.

## 4. Nothing is ever removed

Never delete means never erase. Something found once has just as much standing as something found a thousand times. Rare but real is worth keeping. Compression means storing something once with a count next to it, not throwing things out.

*In the code:* the pool is a dict keyed by content. Counts are values. There is no deletion anywhere.

## 5. A thing is defined by what contains it and what it connects to

A part's connections -- what it's made of, what it belongs to, what it turns into, what sits next to it -- that's its definition. Density is the number of things that contain it (basically, how many places does this part show up).

*In the code:* `made_of`, `part_of`, `changes_of()`, and the FOLLOWS and RUN FOLLOWS tables. Density is `len(part_of[p])`. The CRYSTAL entry is all those connections printed out for one part.

## 6. The crystal makes groups but doesn't collapse them

It builds a grouping and leaves the pool exactly as it was. It sees the whole pool each round, including what it made before. Each new thing goes back in for the next round: crystallize, loop again, stop when nothing changes. You don't replace things -- you add: a run might have 300 parts, the next level adds 50 for a total of 350, the next adds 25, the next 5, then it's stable.

*In the code:* `crystallize()` reads the pool and writes a `classes` table. Minted parts go back into the pool and get sorted with everything else on the next round. `run_levels()` runs the next level on the runs as they are, with the classes serving as a second way for two things to count as "the same" inside `mint()`'s `head()`. Every new part goes into the one shared `pool`, until a level is left with a single run. The additions reach zero before that. The LEVELS table in the record is the 300 / 350 / 375 / 380 count.

## 6a. Feedback and evaluation are the same comparator

"Does the model match reality?" and "is this the same as that?" are the same question. Evaluation was always built in -- it just wasn't looped. The loop is memory: save the pool after one signal, compare the next signal against it, add whatever's different.

*In the code:* `load_memory()`, `save_memory()`, the `memory` argument to `mint()` and `run_levels()`, and the MEMORY table in the record (confirmed / added / not seen this time).

## 7. Define nothing -- start from zero

The system gets only input, output, and its own code. No target, no idea of right or wrong, no feature list -- because what you tell it to look for might not be what it actually needs to find. Every output matters -- never treat any of it as meaningless.

*In the code:* no file-type table, no character set, no tokenizer, no stop list, no training. The lens is display-only. The one tolerance is computed from the signal.

## 8. Knowledge is a dictionary entry

What the system "knows" takes the form of a dictionary entry: a thing, the forms it takes, and the changes between them. Classes are groups of things that take the same changes (like how "walk," "talk," and "look" all take "+ed" and "+ing").

*In the code:* `changes_of()` and the CLASSES and CRYSTAL tables.

## 9. Take the easy path

Don't pre-solve problems you think might happen. Don't add checks and filters nobody asked for. Build it. Be surprised. Deal with issues as they actually come up. Pull everything in, and never treat a common, highly-connected part as unimportant -- lots of connections means it matters.

*In the code:* the separator is the most common word, full stop. The sorted-neighbor collide is the plain way to find shared heads. No part is dropped for being common. The cap and the fresh-pair rule were added when a 1.6 MB file ran out of memory, not before.

## 10. Loop until stable

Repeat until no new information comes out. Whatever's left over at that point is reported, not hidden.

*In the code:* the MINT line in the record lists the parts produced per round down to 0.

## 11. The thing stands for itself

No claims in the documents. The records are the evidence, and the breakdowns explain how to read them and how to check them against an outside source where one exists.

*In the repo:* `examples/*/BREAKDOWN.md`.

## The choices it does make

Rule 7 says define nothing, and the program defines no file types,
alphabets, or targets. But it does make a few decisions about how to
look at a signal, and you should know where they are:

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

These are the places where a different choice would give a different
record from the same signal. `extend/` shows three of them changed.
