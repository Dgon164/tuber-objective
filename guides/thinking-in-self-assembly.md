# Self-assembly: how to work with the system

This guide shows how to work with a system that finds its own structure.
This guide is not about the code. This guide is about what you do and do
not do as the person who runs the system.

## The only rule

**Do not help the system. Run the system. Then find the difference that
the system does not have.**

That is the whole method. Each section below explains that sentence.

## Self-assembly: a definition

A self-assembly system makes structure from its own output. You give the
system a signal. The system compares things, finds what occurs many
times, and makes more structure from what the system found. The output
of each round becomes the input of the next round. You do not tell the
system what to look for. You do not tell the system what the system
found.

You do not correct the categories of the system. You do not rename the
parts of the system. The structure that the system finds is the
structure that the signal has. If the signal has no structure, the
system finds no structure. That result is also a correct answer.

In autocatalysis, the product of a chemical reaction makes the same
reaction faster. The comparator has the same property: the output of the
comparator is what the comparator compares next. You do not drive the
system. You set the system up and let the system run until the system is
stable.

## Actions to stop

**Do not predict what the system will find.** Your prediction will be
wrong. Then you will try to change the system to agree with your
prediction. You will not read what the system found. Discovery found that
the EXTEND instruction of the Apollo computer is the separator, the most
common word. No person can predict that result. The result is correct.

**Do not define the categories.** If you name the groups in advance, you
have already decided the answer. The categories of the system come from
the signal. The categories can be different from your categories. That
difference is information, not an error.

**Do not filter the input.** Do not do any of these things:

- clean the data
- remove unusual values
- remove punctuation
- change the case of the letters

Each of these decisions tells the system what is important. Let the
system find what is important. Discovery found that the top bit of ASCII
is never 1. Discovery found that fact because nobody removed the top bit
first.

**Do not score the system against your expectations.** The comparator of
the system is the scorer. A part that occurs many times has meaning. A
part that occurs 1 time is noise. That test is already in the system. If
you add a second score function, you split the system into 2 parts: the
part that learns and the part that judges. Then you must show why the
judge is correct.

**Do not add special cases.** If the system does not find a thing, the
answer is not a rule for that thing. The answer is a difference that the
system does not have. See the next section.

## Actions to do instead

### 1. Run the system

Give the system the signal. Read the record. Do not look for what you
expected. Look at what is in the record.

### 2. Find the difference that the system does not have

If the record does not show a thing that you know is in the signal, do
not add a detector for that thing. Ask this question: **what difference
must the system see to find this thing without help?**

The system finds structure by comparison. If the system did not find a
thing, 1 of these 3 statements is true:

- **The difference is not in the signal.** The information that you look
  for is not in the signal at this resolution. That result is a real
  answer, not an error. You need a different signal, not a different
  system.

- **The difference is in the signal but does not occur enough times.**
  The comparator finds what repeats. A thing that occurs only 1 time is a
  data point, not a pattern. More signal, or a different cut, can show
  the thing. To cut is to divide the signal into runs at a separator.

- **The difference is in the signal but the comparator cannot reach the
  difference.** The structure exists, but the current path of the system
  does not compare the correct things. This case is the case of interest.
  The fix is not a rule. The fix is to point the comparator at a new
  target.

### 3. Point the comparator at a new target

The scripts in `extend/` do this step. Each script is a few lines that
take the output of Discovery and run the same comparator on a different
part of the output:

- `same_slot.py` compares words by their position (the same word on the
  left, the same word on the right), not by their contents. The script
  finds parts of speech.
- `functions.py` compares changes by the parts that the changes act on
  (the parts that take the same set of changes), not by their form. The
  script finds functions that make words. The functions can make new
  words.
- `sentence.py` follows the sequence (the word that comes after each
  word), not the parts. The script writes sentences.

None of these scripts needed a change to `discovery.py`. Each script
points the comparator at a different relation in the record. The
difference was already in the data. The comparator had not yet compared
that part of the data.

### 4. Check the cost, not the output

The output of the system is what the system found. You do not grade the
output. You measure the cost to find the output. The cost is the number
of tries that failed, the time, and the number of paths that gave no
result before the system was stable.

If the cost is high, the search of the system is too wide. The system
does not have enough differences to make the search space small. The fix
is the same: find the difference that the system does not have.

If the cost is low, the system has enough structure to get to the output
directly. A low cost shows that the differences that the system has are
the correct differences.

The script `functions.py` went through 4 versions. The cost (the tries
that failed for each word that the script made) is the measure of each
version (`extend/FUNCTIONS.md`, "What was tried before this"):

- Open offers, no feedback: the most failures.
- Feedback for each ending: more failures still. The feedback was too
  narrow. Each refusal taught nothing about refusals that were almost the
  same.
- Negative groups: far fewer failures. The feedback applied to more
  cases.
- Functions over the record: approximately the same cost as the negative
  groups, in less than half of the time, with nothing added. The
  structure of the record is the feedback. The numbers of the current run
  are in the header of `extend/alice.functions.txt`.

The cost decreased as the system found the correct differences to
compare.

### 5. Remove. Do not add.

If the system is too slow or has too much noise, the first idea is to
add: a filter, a heuristic, or a special case. Do not add. The answer is
almost always to remove something: stop the comparison of things that
are not important.

The script `functions.py` was not usable when the script treated each
fragment as a target. The letter `e` is inside more parts than almost any
other part (PARTS BY DENSITY in `examples/text/alice.txt.record.txt`).
The letter `e` takes almost each change and says nothing useful about any
1 change.

A limit to whole runs decreased the sibling pairs by orders of magnitude.
A whole run is a part that the signal made on its own. The count is on
the first line of `extend/functions.output.txt`. The comparator and the
logic were the same, with less noise. The thing that the script removed
was not information. The thing was a difference that made no difference.

## The short version

```
1. Run the program.
2. Read what the program found, not what you expected.
3. If a thing is missing, find the missing difference.
4. Point the comparator at that difference.
5. If the program is slow, remove noise. Do not add rules.
6. The cost is the measure. The output is the answer.
```

The system assembles itself. Your job is to give the system a signal.
When the system stops, your job is to find the comparison that the
system has not yet made. That is the whole job. Everything else is the
task of the system.
