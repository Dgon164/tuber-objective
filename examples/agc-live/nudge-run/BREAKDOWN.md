# The nudge, read by the comparator

2026-10-11. Two flights from the 10-10 package, same setup, same key
schedule, 430 seconds each. In one, the vehicle was nudged at 340 s
(+0.5 deg/s about the Y axis) and the flight program's autopilot damped
the rotation. In the other, nothing happened. The question: with nothing
told to it, can the comparator (Discovery's tool for finding differences)
figure out what the nudge set off, from the incoming pulse all the way to
the outgoing jets to the vehicle moving?

It can. Here is how.

## What was given

Every input, so you can see the complete list:

- Two flights, one with a nudge and one without. That is the
  experiment's design.
- The window: 10 s before the first pulse from outside reached the
  computer, 90 s after. The start was found in the signal itself (the
  first counter packet in the channel log), not picked by hand.
- The clock stripped from each record before Discovery read it. The
  cycle counter gives the row order; inside each word it would make
  every row unique and nothing would repeat, which would hide the
  patterns. Rows stay in time order.
- For the last step, one row per 100 ms (the vehicle's own row rate)
  holding the vehicle's fields and the last value seen on each channel,
  in a fixed column order; then the flips -- which fields changed from
  the row before. That is `extend/row_by_row.py` on the combined
  record.
- A names file, used only to print human-readable names next to what
  was found.

Not given: what a jet is, what a gimbal is, which channel is which,
which memory cell is which, what a rate or an error is, any threshold,
any category of change, any score.

## Step 1. Discovery on each signal, each flight

| signal | flight | frame found | distinct words | parts |
|---|---|---|---|---|
| memory writes | nudged | 80 bits | 58,917 | 173,946 |
| memory writes | quiet | 80 bits | 20,497 | 94,352 |
| channel packets | nudged | 32 bits (forced; 16 and 32 tie) | 316 | 11,500 |
| channel packets | quiet | 32 bits | 89 | 930 |
| vehicle rows | nudged | 208 bits | 901 of 1,000 | 1 |
| vehicle rows | quiet | 208 bits | 1 of 1,000 | 0 |

The nudge tripled the number of distinct memory writes and multiplied
the channel parts (repeated sequences) by twelve. The vehicle rows tell
the other half of the story: in the quiet flight every row is the same
(nothing is changing), so there is only 1 distinct word; in the nudged
flight almost every row is different, so there is nothing for the mint
(Discovery's pattern-finder) to match up. Something that moves
continuously has no repeated words. That is the time case discussed in
`notes/open.md`, and step 3 below is the answer to it.

## Step 2. The bridge: things in the nudged flight and not the quiet one

Set operations on the words, the same way `bridge.py` compares two
languages.

**Memory writes.** 40,636 distinct writes happen only in the nudged
flight. The memory cells they write to, sorted by how often they were
written, with names from the lens:

```
3352 DAPTREG6    26851       3027 EDOT       10397       3050 DYERROR   4050
0033 CDUY        14334       3337 ABSEDOT     7526       3031 TRAPEDQ   3754
3340 DAPTEMP2    10973       0031 TIME6       7488       3026 OMEGAU    3177
                             3341 FIREFCT     5567       3052 DZERROR   3164
                             0034 CDUZ        4934       3023 OMEGAR    3127
```

The routines doing those writes (identified by the nearest label below
the instruction address):

```
BACKP  ROT-TOUV  TJCALC  QERRCALC  TJLAW  PAXIS  NEGEDOT  SETSENSE
RERRCALC  SCALEE  CALCPERR  P-RATE  Q-RATE  STILLRCS  SCALEDOT  TJETLAW
DACLOOP  ERRTEST  R-RATE  ROTORQUE  RCS  QRAXIS
```

Only in the quiet flight: `NQTRAPS`, `NRTRAPS`, `NPTRAPS` -- the
autopilot's idle bookkeeping for "nothing to respond to," which stops
once there is actual work to do.

**Channel packets.** 254 distinct packets only in the nudged flight:

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

Only in the quiet flight: nothing but downlink words on 035.

What the lens tells us this all means: the nudge was about the Y axis.
Channel 233 is the Y gimbal pulse counter -- that is the nudge arriving
at the computer, 5,817 pulses of it. `CDUY` is the memory cell those
pulses land in. `EDOT`, the `OMEGA` cells, `DYERROR`, `DZERROR` are the
autopilot's rate and error cells. `TJLAW`, `TJETLAW`, `TJCALC` compute
the jet firing times. Channel 013 is the autopilot's control word.
Channel 005 is the jet commands going out to the vehicle. The comparator
put the whole reaction-control autopilot on the nudged-only side, cell
by cell and routine by routine, because those are the things that
happened in one flight and not the other.

## Step 3. Channel to motion, on the shared clock

Vehicle rows do not repeat, so the combined record was read as flips:
for each 100 ms slice, which fields changed from the row before. 39
fields -- 14 from the vehicle, 25 channels. One 40-bit word per row.

Nudged flight, 169 distinct flip rows. The most common, with names from
the lens:

```
 124  ay az cdu_sent
  94  ay cdu_sent
  84  ay cdu_sent ch034 ch035
  82  ay az cdu_sent ch034 ch035
  41  (no change)
  37  ax ay az cdu_sent ch034 ch035
```

Quiet flight, 10 distinct flip rows, and every one of them is only
`ch034` and `ch035` (the downlink, meaning telemetry) with an occasional
`ch013`.

The rows where channel 005 (jet commands) flipped:

```
   7  ax ay az cdu_sent ch005 ch013 ch034 ch035
   6  ax ay az wy wz cdu_sent ch005 ch013 ch034 ch035
   4  ax ay az wy wz jets5 cdu_sent ch034 ch035
   2  ay wy wz jets5 cdu_sent
```

That is the final link. The rows where the computer's channel 005
changed are the same rows where the vehicle's own jet field changed and
the turn rates `wy` and `wz` changed. The field order was fixed in
advance and nothing said which field was which; "these change in the
same 100 ms" is all the comparator was asked, and it put the jet
channel, the jet field, and the turn rates together.

The RUNS table of the nudged flip rows is the flight in sequence: a long
stretch of downlink-only rows, then one row where the angles start
moving, then hundreds of rows of `ay cdu_sent` with jet rows scattered
through them, thinning out. That is the nudge, the drift, the jet
firings, and the damping, read as one continuous run.

## Step 3b. The vehicle rows at a smaller frame

The 208-bit read made every row one word, so rows that differed in even
the last bit of one field were different words and the mint never got to
look inside. The same file read at 16 bits (`--frame 16`) makes each
field its own word, and now repeats show up:

- **Fields that never moved**: `4204` and `f764` have count exactly
  1,000 -- one per row. Through the lens: vx = 1690.0 m/s and
  vz = -220.4, the two velocity fields. They never changed.
- **Rate plateaus.** The top parts by density are pairs of rate words
  that hold steady for a stretch: `ff8f.0007` repeats 244 times,
  `0013.004f` 94 times, `0154.ffc0` 74 times, `ff94.0002` 65 times,
  `ff7c.ffb8` 58 times, `ff42.ff7e` 37 times. The vehicle turns at a
  constant rate until a jet fires, then settles into a new constant
  rate. Those are the autopilot's firings, seen as steps in the
  vehicle's own record.
- **The nudge's axis.** Class `{0.0} [0004+, +00b1]` has five members,
  `fa5e fa3d fa53 fa48 f894`: five rows where the field before was
  `0004` and the field after was `00b1` and only this one field
  differed. Classes `{0.1}` to `{0.5}` are the same shape. Through the
  lens, the fixed neighbors are `ax` and `az` and the moving field is
  `ay` -- the Y angle, exactly the axis the nudge was about. Nothing
  said Y.

At 8 bits (`--frame 8`) it gets finer still: 89 classes at level 1.

Why the first read missed this: a whole row scores 1.000 in the frame
step (it finds a column that is always 1 and a column that is always 0),
so 208 was picked, and the fold check (which tests whether the two
halves match) found the halves different and did not fold. For a signal
made of rows, that is the wrong frame for the mint even though it is the
right one for seeing the layout. Open end: when the chosen frame leaves
no repeated words, try reading at the next width down that gives some --
the same signal at a finer cut. Records: `held-vehicle.bin.frame16.record.txt`,
`held-vehicle.bin.frame8.record.txt`.

## The chain, read backward

Vehicle rates change <-- vehicle jet field changes <-- channel 005
changes <-- `TJLAW` / `TJETLAW` / `TJCALC` write `FIREFCT`, `DAPTREG6`
<-- `EDOT`, `OMEGA*`, `D*ERROR` written by `P-RATE`, `Q-RATE`,
`QERRCALC` <-- `CDUY` written from channel 233 <-- pulses from outside.

Every link in that chain is a set of words the comparator put on the
nudged-only side, or a set of fields it put in the same flip row. The
names were attached afterward. The chain was found by the comparator.

## Where it stopped

- The combined record's "last value" per channel loses pulse channels:
  channel 233 sends the same code 5,817 times, so its last value never
  changes and it does not show up in the flips. The vehicle's own
  `cdu_sent` count carries that link instead. A count-per-row field for
  each channel would carry it on the computer's side too.
- Step 2 is a bridge on whole words. A bridge on parts (the repeated
  sequences the mint found) would give the nudged-only *sequences* --
  routines as runs of writes -- not just the individual cells. The
  writes record's JSON is 4 GB for a 100 s window, which is the size
  bottleneck; the text record's top parts are in
  `held-writes.bin.record.head.txt`.
- Classes on the flip rows exist (190 of them) and were not explored
  here.

## Files

- `bridge.txt` -- step 2's output in full.
- `held-flips.bin.record.txt`, `quiet-flips.bin.record.txt`, `fields.txt`
  -- step 3's records and the field order.
- `*-channels.bin.frame32.record.txt` -- the channel records.
- `*-writes.bin.record.head.txt` -- the top of the write records.
- `../bridge_flights.py`, `../flips.py` -- the two readers. The lens is
  used only when printing.
