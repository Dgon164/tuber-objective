# How to write about this system

Read this before you change any document in this repository.

## The rule

Write for someone who has never seen the system. Explain each part at
the level of its designed function: what goes in, what the part does to
it, what comes out, under normal conditions.

Use the words you would use to describe an engine to another adult: the
fuel-air mixture is compressed and ignited, and the pressure drives the
piston. That sentence tells you what an engine is for and roughly how it
gets there. It does not tell you the stoichiometry, how to detect knock,
or how to check the compression. That is the level.

## What this means in practice

**Say what a part does before you use its name.** Not "the mint step
runs until stable." Instead: "the program compares chunks that look
alike and records what they share. This is the mint step. It runs until
a pass finds nothing new."

**Never use a word that only means something if you already know the
system.** Booked, ledger, verdict, void, lock, fork, seed, lift, spine,
forcing, doctrine. These are borrowed from accounting, courtrooms, sports
and physics, and they mean nothing to a new reader. Say the operation:
the program records how much the signal changed. The score does not
count. The program adds a new branch.

**Skip the internals, the math, the edge cases, and the proofs.** A
document that explains how the code works line by line is a different
document from one that explains what the system does. Most readers need
the second one. If a guide's job is to go deeper, it still opens each
section with the engine sentence before it goes deeper.

**Do not compress.** "Lag nominates. Propagation confirms." is a
reminder for someone who already knows. It is not an explanation. Write
the explanation.

**Plain English.** Short sentences where they help, longer ones where
they read better. Active voice. Contractions are fine. Numbers as words
when they are small and casual (one file, two commands), as digits when
they are data (144,395 bytes, 22 verb stems).

**State it. Don't comment on it.** A sentence about the work instead of
about the thing gets cut. Not "what the test taught us" but "the test
showed." Not "the critic is right" but the fact itself. Not "what's
still open" but "not tested yet" or "todo." Not "the signal that holds
up" but "the gap is 0.89." Not "the one place the bar was wrong" but
"the 0.95 bar is above the noise floor." Status words are plain: done,
not done, untested, todo, next. Headings are labels, not sentences with
a twist in them.

## Two examples at the right level

Before: "Lag nominates. Propagation confirms."

After: "To find out whether one signal causes another, the program first
looks for a time delay between them. If it finds one, it adds a small
push to the first signal and checks whether that push shows up in the
second. If it does, the first signal causes the second."

Before: "Every operator books exactly one work term."

After: "Before the program compares a signal to a template, it lines the
signal up: shifts it, stretches it, and rescales it. Each step changes
the signal a little, and the program writes down how much. If the steps
had to change the signal a lot, the comparison is not trusted."

Roughly 40 to 60 words per mechanism. Enough to know what it is for and
how it gets there. Not enough to build it. That is the point.

## The test

Hand the paragraph to someone who has never seen the repository. If they
can tell you what the part is for and roughly what it does, the
paragraph is done. If they ask "what does X mean" about any word in it,
it is not.
