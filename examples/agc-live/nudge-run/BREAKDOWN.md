# The push, as the comparator recorded it

2026-10-11. Two flights from the 10-10 work, with the same setup, the
same key schedule, and 430 seconds each. In one flight the vehicle got
a push at 340 s (+0.5 degrees per second about the Y axis), and the
flight program's autopilot damped the rotation out. In the other flight
nothing happened.

Discovery's basic comparison, which says whether two things are the
same, different, or one is part of the other, is called the comparator.
The run tests one question. Given no names and no explanation, can the
comparator find the chain of events the push started, from the pulse
that comes into the computer, to the jets that fire, to the motion of
the vehicle?

It can. The method follows.

## What went in

The full list:

- The two flights, one with a push and one without. That's the design
  of the experiment.
- The window: 10 seconds before the first pulse from outside reached
  the computer, and 90 seconds after. A channel is a numbered signal
  path between the computer and the hardware around it. The start of
  the window came from the signal itself (the first counter packet in
  the channel recording), not from a person.
- Each record with its clock removed before Discovery read it. The
  cycle counter gives the row order anyway, and a counter inside each
  word would make every row unique, so nothing would repeat and the
  counter would hide the sequences. The rows stay in time order.
- For the last step, the row record: one row per 100 ms (the vehicle's
  row rate), each holding the vehicle's fields and the last value seen
  on each channel, in a fixed column order. Then the flips: the fields
  that changed from the row before, made by `extend/row_by_row.py` from
  the row record.
- A names file, used only to print readable names next to the results.

The comparator was not given:

- what a jet is
- what a gimbal is
- which channel is which
- which memory cell is which
- what a rate or an error is
- any threshold
- any category of change
- a score

## Step 1. Discovery on each signal, each flight

| signal | flight | record width Discovery found | distinct words | parts |
|---|---|---|---|---|
| memory writes | with push | 80 bits | 58,917 | 173,946 |
| memory writes | quiet | 80 bits | 20,497 | 94,352 |
| channel packets | with push | 32 bits (set by the flag, because 16 and 32 get the same score) | 316 | 11,500 |
| channel packets | quiet | 32 bits | 89 | 930 |
| vehicle rows | with push | 208 bits | 901 of 1,000 | 1 |
| vehicle rows | quiet | 208 bits | 1 of 1,000 | 0 |

The push made the number of distinct memory writes three times larger
and the number of channel parts (repeating sequences) twelve times
larger. The vehicle rows show the other half of the picture. In the
quiet flight every row is the same, no field changes, so there's one
distinct word. In the pushed flight almost every row is different.

Discovery's mint step compares chunks that look alike and records what
they share, making a new part from two parts that start or end the same
way. With no two rows alike, it has nothing to match: a thing in
continuous motion has no words that repeat. That's the "time case" from
`notes/open.md`, and step 3 below is the answer to it.

## Step 2. The bridge: what's in the pushed flight and not the quiet one

The bridge is the step that compares two records and sorts their words
into what's in both, what's only in the first, and what's only in the
second. It's the same set arithmetic `bridge.py` uses to compare two
languages.

**Memory writes.** The pushed flight has 40,636 distinct writes the
quiet flight doesn't. A lens is a names file used only when printing,
so a person can read a name next to each number. The memory cells those
writes went to, in order of write count, named through the lens:

```
3352 DAPTREG6    26851       3027 EDOT       10397       3050 DYERROR   4050
0033 CDUY        14334       3337 ABSEDOT     7526       3031 TRAPEDQ   3754
3340 DAPTEMP2    10973       0031 TIME6       7488       3026 OMEGAU    3177
                             3341 FIREFCT     5567       3052 DZERROR   3164
                             0034 CDUZ        4934       3023 OMEGAR    3127
```

The routines that did the writing (the nearest label below each
instruction's address names its routine):

```
BACKP  ROT-TOUV  TJCALC  QERRCALC  TJLAW  PAXIS  NEGEDOT  SETSENSE
RERRCALC  SCALEE  CALCPERR  P-RATE  Q-RATE  STILLRCS  SCALEDOT  TJETLAW
DACLOOP  ERRTEST  R-RATE  ROTORQUE  RCS  QRAXIS
```

Only in the quiet flight: `NQTRAPS`, `NRTRAPS`, `NPTRAPS`. Those three
are what the autopilot writes when it has nothing to do, and they stop
as soon as it has work.

**Channel packets.** The pushed flight has 254 distinct packets the
quiet one doesn't:

```
233   5817 packets   values 00023, 00021
234   1409
035    248
034    235
005    193           values 00041, 00151, 00110, 00022 ...
232    142
013     85           values 40100, 40000
175/176/174  138
```

Only in the quiet flight: downlink words on 035 (the computer's
telemetry stream), and nothing else.

The lens says what the results mean. The push was about the Y axis.
Channel 233 is the pulse counter for the Y gimbal, so it's the push
itself as it arrives at the computer: 5,817 pulses. `CDUY` is the
memory cell that receives those pulses. `EDOT`, `OMEGA`, `DYERROR` and
`DZERROR` are the autopilot's rate and error cells.

`TJLAW`, `TJETLAW` and `TJCALC` work out how long to fire the jets.
Channel 013 is the autopilot's control word, and channel 005 is the jet
commands going out to the vehicle. The comparator put the whole
reaction-control autopilot, the part of the flight program that fires
the small thruster jets to keep the vehicle pointed the right way, on
the pushed side only, cell by cell and routine by routine, because
those things happened in one flight and not the other.

## Step 3. Channel to motion, on a shared clock

The vehicle rows never repeat, so the reader read the row record as
flips: for each 100 ms slice, which fields changed from the row before.
There are 39 fields, 14 from the vehicle and 25 channels, and each row
is one 40-bit word.

The pushed flight has 169 distinct flip rows. The most common, named
through the lens:

```
 124  ay az cdu_sent
  94  ay cdu_sent
  84  ay cdu_sent ch034 ch035
  82  ay az cdu_sent ch034 ch035
  41  (no change)
  37  ax ay az cdu_sent ch034 ch035
```

The quiet flight has 10 distinct flip rows, every one just `ch034` and
`ch035` (the downlink), with `ch013` in some.

The rows where channel 005 (jet commands) flipped:

```
   7  ax ay az cdu_sent ch005 ch013 ch034 ch035
   6  ax ay az wy wz cdu_sent ch005 ch013 ch034 ch035
   4  ax ay az wy wz jets5 cdu_sent ch034 ch035
   2  ay wy wz jets5 cdu_sent
```

The jet rows are the last link. In the rows where the computer's
channel 005 changed, the vehicle's jet field changed too, and so did
the turn rates `wy` and `wz`.

The field order was fixed before the run, and nothing said which field
was which. The only question the comparator asked was "do these fields
change in the same 100 ms", and it put the jet channel, the jet field
and the turn rates together.

The RUNS table, the record's list of chunks between dividers in the
order they occur, for the pushed flight's flip rows is the flight in
sequence:

- a long stretch of rows with only the downlink
- then one row where the angles start to move
- then hundreds of rows of `ay cdu_sent`, with jet rows at intervals
  that grow longer

That's the push, the drift, the jet firings, and the rotation dying
away, as one continuous run.

## Step 3b. The vehicle rows at a narrower width

Read at 208 bits, each row was one word, so two rows that differed in
only the last bit of one field were different words, and the mint never
looked inside a row. Reading the same file at 16 bits (`--frame 16`)
makes each field one word, and then repeats appear:

- **Fields that don't move**: `4204` and `f764` each occur exactly
  1,000 times, once per row. Through the lens: vx = 1690.0 m/s and
  vz = -220.4, the two velocity fields, which never changed.
- **Rate plateaus.** The parts with the highest density (the ones
  contained in the most other parts) are pairs of rate words that hold
  for a while:
  - `ff8f.0007` repeats 244 times
  - `0013.004f` repeats 94 times
  - `0154.ffc0` repeats 74 times
  - `ff94.0002` repeats 65 times
  - `ff7c.ffb8` repeats 58 times
  - `ff42.ff7e` repeats 37 times

  The vehicle turns at a constant rate until a jet fires, then settles
  to a new constant rate. The plateaus are the autopilot's jet
  firings, seen as steps in the vehicle's record.
- **The axis of the push.** A class is a group of parts that take the
  same set of changes. The class `{0.0} [0004+, +00b1]` has five
  members, `fa5e fa3d fa53 fa48 f894`: five rows with `0004` in the
  field before and `00b1` in the field after, differing only in this
  one field. Classes `{0.1}` to `{0.5}` have the same shape.

  Through the lens, the unchanging neighbours are `ax` and `az`, and
  the moving field is `ay`, the Y angle: exactly the axis of the push.
  Nothing said Y.

At 8 bits (`--frame 8`) the result is finer still: 89 classes at level
1.

Why the first read missed it: Discovery's frame step works out how wide
a record is by trying widths and seeing which one lines the bit
patterns up. A full row scores a perfect 1.000, because the frame step
finds a column that's always 1 and a column that's always 0, so it
picked 208. The fold check, which asks whether the chosen width is just
a smaller width repeated, found the two halves were different, so it
didn't fold. For a signal made of rows, 208 is the wrong width for the
mint but the right width for seeing the layout.

Open task: the width the frame step picks can have no repeating words
at all. When that happens, try the next width down that does repeat.
Cutting a signal means dividing it into pieces at a boundary, and the
next width down is the same signal cut finer. The records:
`held-vehicle.bin.frame16.record.txt`,
`held-vehicle.bin.frame8.record.txt`.

## The chain, backward

Each link comes from the one below it:

1. The vehicle's turn rates change.
2. The vehicle's jet field changes.
3. Channel 005 changes.
4. `TJLAW`, `TJETLAW`, and `TJCALC` write `FIREFCT` and `DAPTREG6`.
5. `P-RATE`, `Q-RATE`, and `QERRCALC` write `EDOT`, `OMEGA*`, and
   `D*ERROR`.
6. The pulses from channel 233 write `CDUY`.
7. The pulses come from outside.

Every link is one of two things: a set of words the comparator put on
the pushed side only, or a set of fields the comparator put in the same
flip row. The names came afterward. The comparator found the chain.

## What it couldn't do

- Taking the "last value" of each channel for the row record loses the
  pulse channels. Channel 233 sends the same code 5,817 times, so its
  last value never changes and it never shows up in the flips. The
  vehicle's `cdu_sent` count carries that link instead. A per-row count
  for each channel would carry it on the computer's side too.
- Step 2 is a bridge on whole words. A bridge on parts (the sequences
  the mint found) could give the *sequences* that belong to the push
  only: routines as runs of writes, not just single cells. The JSON of
  the writes record is 4 GB for a 100-second window, and that size is
  the limit. The top parts of the text record are in
  `held-writes.bin.record.head.txt`.
- The flip rows have classes (190 of them). This run didn't look at
  them.

## Files

- `bridge.txt`: the full output of step 2.
- `held-flips.bin.record.txt`, `quiet-flips.bin.record.txt`,
  `fields.txt`: the records of step 3 and the field order.
- `*-channels.bin.frame32.record.txt`: the channel records.
- `*-writes.bin.record.head.txt`: the top of the write records.
- `../bridge_flights.py`, `../flips.py`: the two readers. They use the
  lens only when printing.
