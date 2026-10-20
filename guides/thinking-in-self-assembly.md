# Self-assembly: how to work with the system

This guide is about how to work with a system that finds its own
structure. It isn't about the code. It's about what you do, and what you
don't do, as the person running it.

## The only rule

**Don't help the system. Run it. Then find the difference it doesn't
have.**

That's the whole method. Each section below explains that one sentence.

## What self-assembly means

A self-assembling system builds structure out of its own output. You give
it a file. It compares things, finds what occurs many times, and builds
more structure out of what it found. The output of each round becomes
the input of the next. You don't tell it what to look for, and you don't
tell it what it found.

You don't correct its categories. You don't rename its parts. The
structure it finds is the structure the file has. If the file has no
structure, it finds none, and that's a correct answer too.

There's a kind of chemical reaction whose product speeds up the very
reaction that made it, so the reaction feeds itself; chemists call it
autocatalysis. The comparison at the heart of this program works the
same way, literally: whatever it produces is what it compares next. You
don't drive it. You set it up and let it run until a pass finds nothing
new.

## Things to stop doing

**Don't predict what the system will find.** Your prediction will be
wrong. Then you'll start changing the system to agree with your
prediction instead of reading what it found. Discovery found that in the
Apollo flight program, the most common unit, and so the divider it cuts
the file at, is the EXTEND instruction. Nobody could have predicted that.
It's correct.

**Don't define the categories.** If you name the groups in advance,
you've already decided the answer. The system's categories come from the
file, and they can differ from yours. That difference is information,
not an error.

**Don't filter the input.** Don't do any of these:

- clean the data
- remove unusual values
- strip punctuation
- change the case of the letters

Each of those decisions tells the system what matters. Let it find what
matters. Discovery found that the top bit of every ASCII byte is never 1.
It found that because nobody stripped the top bit first.

**Don't score the system against your expectations.** The system's own
comparison is the scorer. A part that occurs many times means something.
A part that occurs once is noise. That test is already built in. If you
add a second score on top, you split the system in two: a part that
learns and a part that judges. Then you have to show why the judge is
right.

**Don't add special cases.** If the system doesn't find something, the
answer is not a rule for that thing. The answer is a difference the
system doesn't have yet. The next section says what that means.

## What to do instead

### 1. Run the system

Give it the file. Read the record it writes. Don't look for what you
expected. Look at what's there.

### 2. Find the difference the system doesn't have

If the record doesn't show something you know is in the file, don't add
a detector for it. Ask this instead: **what difference would the system
have to see in order to find this thing on its own?**

The system finds structure by comparing. If it didn't find a thing, one
of three statements is true:

- **The difference isn't in the file.** The information you're looking
  for isn't in the file at this resolution. That's a real answer, not an
  error. You need a different file, not a different system.

- **The difference is in the file but doesn't repeat enough.** The
  comparison finds what repeats. A thing that occurs once is a data
  point, not a pattern. More data can bring it out, and so can a
  different cut, which means dividing the file into chunks at a
  different divider.

- **The difference is in the file but the comparison can't reach it.**
  The structure exists, but the system as it stands isn't comparing the
  right things. This is the interesting case. The fix isn't a rule. The
  fix is to point the comparison at a new target.

### 3. Point the comparison at a new target

The scripts in `extend/` do exactly this. Each one is a few lines that
take Discovery's output and run the same comparison on a different part
of it:

- `same_slot.py` compares words by where they sit (the same word on the
  left, the same word on the right), not by what they contain. It finds
  parts of speech.
- `functions.py` compares changes by what they act on (the parts that
  take the same set of changes), not by their shape. It finds the
  operations that build words, and those operations can build new words.
- `sentence.py` follows the sequence (which word comes after each word)
  instead of the parts. It writes sentences.

None of these needed a change to `discovery.py`. Each one points the
comparison at a different relation already in the record. The difference
was in the data all along. The comparison just hadn't looked at that part
of the data yet.

### 4. Check the cost, not the output

The output is what the system found, and you don't grade it. What you
measure is what it cost to get there: the number of tries that failed,
the time, and the number of paths that led nowhere before the system
settled.

If the cost is high, the system is searching too widely. It doesn't have
enough differences to narrow the search. The fix is the same as before:
find the difference it doesn't have.

If the cost is low, the system has enough structure to reach the output
directly. A low cost tells you the differences it has are the right ones.

The script `functions.py` went through four versions. The measure of each
was its cost: the number of tries that failed for each word the script
managed to make (`extend/FUNCTIONS.md`, "The earlier methods"):

- The first version proposed every change the record suggested, checked
  each against a word list, and kept no memory of the refusals. It had
  the most failures.
- The second version remembered the refusals, one ending at a time. It
  had more failures still, because the feedback was too narrow: being
  refused on one ending taught it nothing about endings that were almost
  the same.
- The third version grouped the refused changes by what they had in
  common, so one refusal ruled out a whole group of similar changes. It
  had far fewer failures, because each piece of feedback covered more
  cases.
- The fourth version worked from the operations the record already held.
  It cost about the same as the third, took less than half the time, and
  added nothing from outside. The structure of the record was the
  feedback. The numbers from the current run are in the header of
  `extend/alice.functions.txt`.

The cost fell as the system found the right differences to compare.

### 5. Remove. Don't add.

If the system is too slow or too noisy, the first idea is always to add
something: a filter, a shortcut, a special case. Don't. The answer is
almost always to take something away: stop comparing things that don't
matter.

`functions.py` was unusable while it treated every fragment as a target.
The letter `e` sits inside more parts than almost any other part (see
PARTS BY DENSITY in `examples/text/alice.txt.record.txt`). It takes
almost every change there is, so it says nothing useful about any one of
them.

Limiting the script to whole chunks, meaning parts the file produced on
its own as complete chunks, cut the number of sibling pairs by orders of
magnitude. (Two changes are siblings when the same parts take both of
them.) The count is on the first line of `extend/functions.output.txt`.
The comparison and the logic were the same as before, with less noise.
What the script took away wasn't information. It was a difference that
made no difference.

## The short version

```
1. Run the program.
2. Read what it found, not what you expected to find.
3. If something is missing, work out which difference the program
   can't see yet.
4. Point the comparison at that difference.
5. If the program is slow, take away noise. Don't add rules.
6. Measure the cost of getting there. The output is the answer.
```

The system builds its own structure. Your job is to give it a file.
When it stops, your job is to find the comparison it hasn't made yet.
That's the whole job. Everything else belongs to the system.
