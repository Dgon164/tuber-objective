# Design rules

These are the rules the author followed while building Discovery. Each section says what one rule means in plain words, why the program follows it, and then where the rule shows up in the code.

A few of the program's own names come up in nearly every rule, so here they are once. The program reads a file as a string of bits and works out how wide one unit is. It calls those units words. The most common word becomes the separator: the program cuts the file at every copy of it, the way a space cuts a line of text into words. The stretches between two separators are called runs. Everything the program finds goes into one shared table called the pool, which lists every part found so far and how many times it was seen.

## 1. Two things are enough: something that compares and something that remembers

To find anything in a signal, you look at what came before and what came after, and you check whether they differ. That takes two things. The first is a comparator: a piece of code that takes two things and says whether they're the same. The second is a memory: a place that holds the thing you compare against, so that the next comparison has something to meet. Those two are enough to start. The program follows this rule because once you have that pair, every later step turns out to be the same pair pointed at a new place, so nothing else needs to be invented.

*In the code:* each function in `discovery.py` is a comparison of two things, or a count of the answers from such comparisons. A comparison gives one of three answers: same, different, or not part.

## 2. Three answers: same, different, or not part

When the program compares two things, it doesn't throw away whatever differs. It sorts the result into three piles: the piece the two things share, the piece that differs, and the case where one thing isn't inside the other at all. The program keeps the differing piece because the leftover of one comparison is the input to the next one, and a leftover that comes back again later is a real part in its own right. The three answers show up at every level of the system:

- In the frame step, which is where the program works out how wide one unit is. It lays the bits out in rows of a trial width and looks down each column. A column either keeps the same value row after row, or it changes.
- In the mint step, which is where the program compares two runs that begin the same way. The shared beginning is the same, and what remains of each run is different. To mint a part is to make a new part out of two parts that share a start or share an end: the shared piece becomes a part, and so does each leftover.
- In the bridge, which is a script that compares the records of two different files. A part either appears in both records or in only one.

*In the code:* `shared_head()` returns the length of the part that matches. The caller takes what remains. The program does not change what the pair never had in common.

## 3. Repeat the comparison until nothing new turns up

The main loop has four steps. Compare two things. Make a new part out of what they share. Put the new part back into the pool, where it can be compared in its turn. Then do it all again. The only reason to stop is a whole round that makes nothing new. When a round adds nothing, the comparison has found everything it can find in this signal, and the program stops there. There is no other stopping rule, because any other rule would be a guess about how much structure the file has, and the program has no way to know that in advance.

*In the code:* `mint()`. The `while True` loop ends on `if not new: break`.

## 4. Remove nothing

Nothing is ever erased. A thing the program found once is kept with the same care as a thing it found 1,000 times, because a thing that is rare can still be real, and the only way to find out is to keep it and see whether it shows up again later. When the program needs to save space, it stores a thing once with a count next to it. That's what compression means here. It never means dropping anything.

*In the code:* the pool is a dict. The key of each entry is the content of the part. The counts are the values. The code has no removal operation at any point.

## 5. What a thing is: what it's inside of and what connects to it

A part has no definition apart from its connections. The connections are:

- what the part is made of
- what the part is inside of
- what the part turns into when something is added to it (the way `walk` turns into `walked`)
- what sits next to the part: the record keeps a table of which word comes right after which, and the same for runs

The program also counts how many other parts contain a given part. That number is called the part's density. A part with a high density is one that appears inside many places.

*In the code:* `made_of`, `part_of`, `changes_of()`, and the FOLLOWS and RUN FOLLOWS tables. The density is `len(part_of[p])`. The CRYSTAL entry shows all of those connections for one part.

## 6. Group the parts into classes without changing the pool

After the mint step, the program reads the pool and groups together the parts that take the same set of additions. The parts `walk`, `talk`, and `look` all take `+ed` and `+ing`, so they go in one group. A group like that is called a class, and the step that makes the groups is called the crystal. The crystal writes its groups into a second table and leaves the pool exactly as it was. In each round the crystal sees the whole pool, together with the groups it made before, and anything new goes back into the pool for the next round.

Then the program goes one level up. It treats each run from this level as a single unit, makes the most common run the new separator, and cuts, compares, and groups again. That's a level. The loop is: group the parts, go one level up and do it all again, and stop when a level changes nothing.

The program never replaces anything along the way. It only adds. For example, a run can have 300 parts. The next level adds 50 parts, for a total of 350. The next level adds 25, and the next adds 5. Then the count is stable.

*In the code:* `crystallize()` reads the pool and writes a `classes` table. The parts that the program minted go back into the pool. On the next round, the program sorts those parts with all other parts. `run_levels()` runs the next level on the runs as they are. In `mint()`, the function `head()` uses the classes as a second way for two things to count as the same. Each new part goes into the one shared `pool`, until a level has only one run.

The additions reach 0 before that level. The LEVELS table in the record is the 300 / 350 / 375 / 380 count.

## 6a. Checking the result and learning from it use the same comparison

To check whether what the program found agrees with the world, you ask whether two things are the same. That's the comparator again, so the check was always inside the system. What the system didn't do at first was feed the check back in. The memory is that feedback loop, and it has three steps. The program saves the pool after reading one file. When the next file arrives, the program compares it against the saved pool. Then it adds whatever is different. The record reports what happened against the memory: which remembered parts this file made again, which parts are new, and which remembered parts this file didn't make.

*In the code:* `load_memory()`, `save_memory()`, the `memory` argument to `mint()` and `run_levels()`, and the MEMORY table in the record (confirmed / added / not seen this time).

## 7. Define nothing and start from zero

The program gets three things: the input file, its own code, and the output it writes. It has no target to aim at, no notion of right or wrong, and no list of features to look for. The reason is that what you tell a program to find can be different from what it needs to find. If you give it a target, it finds the target and nothing else. So every output counts, and the program never treats an output as something without meaning.

In practice this means there's no table of file types, no fixed alphabet, no rule for splitting text into words, no list of words to ignore, and no training. The only setting that looks like knowledge is the lens, which chooses how to print the bytes the program found as readable characters, and the lens changes nothing about what gets found. The one allowance the program makes for chance, when it decides which unit width is real, is a number it works out from the signal itself rather than a setting someone typed in.

*In the code:* no file-type table, no character set, no tokenizer, no stop list, no training. The lens is for display only. The program computes the one tolerance from the signal.

## 8. What the program knows looks like a dictionary entry

Whatever the program knows has the shape of a dictionary entry with three parts: a thing, the forms of that thing, and the changes that turn one form into another. Classes are the groups of things that accept the same changes. For example, "walk," "talk," and "look" all accept "+ed" and "+ing", so the dictionary groups them together.

*In the code:* `changes_of()` and the CLASSES and CRYSTAL tables.

## 9. Take the simple way

Don't solve a problem before it happens. Don't add checks and filters that nobody asked for. Build the program, accept results you didn't expect, and fix each problem when it actually occurs. Include every part.

In particular, never decide that a common part with many connections is unimportant. Many connections are the sign that a part matters.

Two things in the code show this rule at work. To find parts that share a start, the program sorts the pool alphabetically, so that any two parts with the same beginning end up next to each other, and then compares each part with its neighbor. That's the plain way to do it. And two limits that now exist, a cap on how many parts the pool may hold before the loop stops early and says so, and a rule that a pair is compared only when at least one of the two is new since the last round, were added only when a real file ran the computer out of memory.

*In the code:* the separator is the most common word, with no other condition. The comparison of neighbors in sort order is the plain way to find shared heads. The program does not remove a part because the part is common. The author added the cap and the fresh-pair rule when a 1.6 MB file used all of the computer memory, not before.

## 10. Repeat the loop until the result is stable

Run the loop until no new information appears. Then report what's left, exactly as it is. The program doesn't hide what remains, and the record shows the whole approach: how many parts each round made, all the way down to a round that made none.

*In the code:* the MINT line in the record lists the parts that each round made, down to 0.

## 11. The thing is its own evidence

The documents in this repository make no claims. The records the program writes are the evidence. Each example has a breakdown that explains how to read its record, and, when an outside source exists, how to check the record against that source.

*In the repo:* `examples/*/BREAKDOWN.md`.

## The choices the program does make

Rule 7 says to define nothing, and the program defines no file types, no alphabets, and no targets. But it does make a few decisions about how to look at a signal, and you should know where they are:

- **The program compares words as sequences with a fixed order**, from the front and from the back. It finds a shared middle only when the loop turns that middle into the start or the end of some leftover.
- **The separator is the most common word.** The runs are the stretches between copies of the separator. To cut a signal is to divide it into runs at every copy of the separator, and a different cut gives different runs.
- **The unit width is the width where the columns differ from each other the most.** The program lays the bits out in rows of each trial width and measures, for each column, how often that column holds a 1. The width with the widest spread between its columns wins. Then the program checks whether the winning width is really a smaller width repeated, with the same column pattern showing up two or more times across the row. If a smaller width explains the same pattern, the program folds down to the smaller width.
- **At a level above 0, two things count as the same in two cases.** Either they're the same run, or they're members of the same class one level down. Nothing else counts as the same.

At each of these places, a different choice gives a different record from the same signal. `extend/` shows what happens when three of these choices are changed.
