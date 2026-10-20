# Design rules

These are the rules that the author used to make Discovery. Each section states 1 rule. Each section then shows where the rule appears in the code.

## 1. The 2 necessary things: a comparator and a memory

To find a thing, you look at what came before and what came after. Then you check for differences. A comparator is a thing that checks if 2 things are the same. A memory is a place that keeps the thing that you compare against. A comparator and a memory are enough to start. The rest of the system uses that pair again and again.

*In the code:* each function in `discovery.py` is a comparison of 2 things, or a count of the answers from such comparisons. A comparison gives 1 of 3 answers: same, different, or not part.

## 2. The 3 answers: same, different, not part

The program does not remove what is different. The program sorts what is different. The 3 answers appear at each level of the system:

- In the frame step, a column stays constant or a column changes.
- In the mint step, 2 sequences have the same start, and what remains of each sequence is different. To mint a part is to make a new part from 2 parts that have the same start or the same end.
- In the bridge, a part appears in both records or in only 1 record.

*In the code:* `shared_head()` returns the length of the part that matches. The caller takes what remains. The program does not change what the pair never had in common.

## 3. Repeat the comparison until nothing new appears

The loop has 4 steps:

1. Compare 2 things.
2. Mint what you find.
3. Put the new part back in the pool.
4. Repeat the steps.

The only reason to stop is a round that makes nothing new. That round is the fixed point.

*In the code:* `mint()`. The `while True` loop ends on `if not new: break`.

## 4. Remove nothing

The rule to remove nothing means to erase nothing. A thing that the program found 1 time is as important as a thing that the program found 1,000 times. A rare but real thing is important to keep. Compression means to store a thing 1 time with a count next to the thing. Compression does not mean to remove things.

*In the code:* the pool is a dict. The key of each entry is the content of the part. The counts are the values. The code has no removal operation at any point.

## 5. The definition of a thing: what contains the thing and what connects to the thing

The connections of a part are the definition of the part. The connections are:

- what the part contains
- what contains the part
- what the part changes into
- what occurs next to the part

The density of a part is the number of things that contain the part. The density is the number of places where the part appears.

*In the code:* `made_of`, `part_of`, `changes_of()`, and the FOLLOWS and RUN FOLLOWS tables. The density is `len(part_of[p])`. The CRYSTAL entry shows all of those connections for 1 part.

## 6. The crystal: new groups, no change to the pool

The crystal makes groups of parts. To crystallize the pool is to sort the parts of the pool into classes, with no change to the pool. The crystal sees the whole pool in each round, with the groups that the crystal made before. Each new thing goes back in the pool for the next round. The loop is: crystallize, loop again, and stop when nothing changes.

The program does not replace things. The program adds things. For example, a run can have 300 parts. The next level adds 50 parts, for a total of 350. The next level adds 25, and the next level adds 5. Then the count is stable.

*In the code:* `crystallize()` reads the pool and writes a `classes` table. The parts that the program minted go back into the pool. On the next round, the program sorts those parts with all other parts. `run_levels()` runs the next level on the runs as they are. In `mint()`, the function `head()` uses the classes as a second way for 2 things to count as the same. Each new part goes into the 1 shared `pool`, until a level has only 1 run.

The additions reach 0 before that level. The LEVELS table in the record is the 300 / 350 / 375 / 380 count.

## 6a. Feedback and evaluation: the same comparator

To check if the model agrees with reality is to check if 2 things are the same. The 2 checks are the same comparison. The system always contained the evaluation. But the system did not loop the evaluation. The loop is the memory. The loop has 3 steps:

1. Save the pool after 1 signal.
2. Compare the next signal against the pool.
3. Add what is different.

*In the code:* `load_memory()`, `save_memory()`, the `memory` argument to `mint()` and `run_levels()`, and the MEMORY table in the record (confirmed / added / not seen this time).

## 7. Define nothing and start from 0

The system gets only the input, the output, and its own code. The system has no target, no idea of right or wrong, and no feature list. The reason is that what you tell the system to find can be different from what the system needs to find. Each output is important. Never treat an output as a thing with no meaning.

*In the code:* no file-type table, no character set, no tokenizer, no stop list, no training. The lens is for display only. The program computes the 1 tolerance from the signal.

## 8. Knowledge as a dictionary entry

What the system knows has the form of a dictionary entry. The entry has 3 parts: a thing, the forms of the thing, and the changes between the forms. Classes are groups of things that accept the same changes. For example, "walk," "talk," and "look" all accept "+ed" and "+ing".

*In the code:* `changes_of()` and the CLASSES and CRYSTAL tables.

## 9. Take the simple way

Do not solve problems before the problems occur. Do not add checks and filters that nobody asked for. Make the program. Accept results that you did not expect. Solve each problem when the problem occurs. Include each part.

Never think that a common part with many connections is not important. Many connections show that a part is important.

*In the code:* the separator is the most common word, with no other condition. The comparison of neighbors in sort order is the plain way to find shared heads. The program does not remove a part because the part is common. The author added the cap and the fresh-pair rule when a 1.6 MB file used all of the computer memory, not before.

## 10. Repeat the loop until the result is stable

Repeat the loop until no new information appears. At that point, the program reports what remains. The program does not hide what remains.

*In the code:* the MINT line in the record lists the parts that each round made, down to 0.

## 11. The thing as its own evidence

The documents make no claims. The records are the evidence. The breakdowns explain how to read the records. The breakdowns explain how to check the records against an outside source, when an outside source exists.

*In the repo:* `examples/*/BREAKDOWN.md`.

## The choices of the program

Rule 7 says to define nothing. The program defines no file types, no alphabets, and no targets. But the program makes a few decisions about how to look at a signal. You must know where those decisions are:

- **The program compares words as sequences with a fixed order**, from the front and from the back. The program finds a shared middle only when the loop shows the middle as the start or the end of what remains.
- **The separator is the most common word.** The runs are the parts between copies of the separator. To cut a signal is to divide the signal into runs at each copy of the separator. A different cut gives different runs.
- **The frame is the width with the widest spread of column rates.** The program folds the width down if a smaller width explains the column rates. To fold a width is to replace the width with a smaller width that explains the same column rates.
- **At a level above 0, 2 things are the same** in 2 cases. In the first case, the 2 things are the same run. In the second case, the 2 things are members of the same class 1 level down. Nothing else counts as the same.

At each of these places, a different choice gives a different record from the same signal. `extend/` shows 3 of these choices after a change.
