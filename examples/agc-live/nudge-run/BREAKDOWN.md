# The nudge, in the record of the comparator

2026-10-11. The run is 2 flights from the 10-10 package, with the same
setup, the same key schedule, and 430 seconds each. In 1 flight, the
vehicle got a nudge at 340 s (+0.5 deg/s about the Y axis). The
autopilot of the flight program damped the rotation. In the other
flight, no event occurred.

The comparator is the tool of Discovery that finds differences. The run
tests 1 question. The comparator gets no information. The comparator
must find the chain that the nudge started. The chain goes from the
pulse that comes in, to the jets that go out, to the motion of the
vehicle.

The comparator found the chain. The method follows.

## The inputs

The full list of inputs:

- The 2 flights, 1 with a nudge and 1 without a nudge. The 2 flights
  are the design of the experiment.
- The window: 10 s before the first pulse from outside got to the
  computer, and 90 s after. A channel is a signal path with a number,
  between the computer and the hardware. The start came from the signal itself
  (the first counter packet in the channel trace). No person picked the
  start.
- Each record without the clock. The clock was removed from each record
  before Discovery read the record. The cycle counter gives the row
  order. A cycle counter inside each word makes each row unique. Then no
  row repeats, and the counter hides the sequences. The rows stay in
  time order.
- For the last step, the row record. The row record has 1 row for each
  100 ms (the row rate of the vehicle). Each row has the fields of the
  vehicle and the last value of each channel, in a column order that
  does not change. Then the flips: the fields that changed from the row
  before. The flips come from `extend/row_by_row.py` on the row record.
- A names file. The names file is used only to print names that a
  person can read, next to the results.

The comparator did not get these inputs:

- the meaning of a jet
- the meaning of a gimbal
- the identity of each channel
- the identity of each memory cell
- the meaning of a rate or an error
- a threshold
- a category of change
- a score

## Step 1. Discovery on each signal, each flight

| signal | flight | frame that Discovery found | distinct words | parts |
|---|---|---|---|---|
| memory writes | with nudge | 80 bits | 58,917 | 173,946 |
| memory writes | quiet | 80 bits | 20,497 | 94,352 |
| channel packets | with nudge | 32 bits (set by the flag, because 16 and 32 get the same score) | 316 | 11,500 |
| channel packets | quiet | 32 bits | 89 | 930 |
| vehicle rows | with nudge | 208 bits | 901 of 1,000 | 1 |
| vehicle rows | quiet | 208 bits | 1 of 1,000 | 0 |

The nudge made the number of distinct memory writes 3 times larger. The
nudge made the number of channel parts (sequences that repeat) 12 times
larger. The vehicle rows show the other half of the result. In the quiet
flight, each row is the same (no field changes). Thus there is only 1
distinct word. In the flight with the nudge, almost all rows are
different.

The mint is the step of Discovery that finds the sequences that repeat.
To mint a part is to make a new part from 2 parts that have the same
start or the same end. Thus the mint has no 2 rows to match. A thing in
continuous motion has no words that repeat. The continuous motion is
the time case in `notes/open.md`. Step 3 below is the answer to the
time case.

## Step 2. The bridge: the things in the flight with the nudge and not in the quiet flight

The bridge is the tool of Discovery that compares 2 different signals.
The bridge does set operations on the words, in the same way that
`bridge.py` compares 2 languages.

**Memory writes.** The flight with the nudge has 40,636 distinct writes
that the quiet flight does not have. The lens is the tool that finds the
name of a code or an address. The list below shows the memory cells of
those writes, in order of write count, with names from the lens:

```
3352 DAPTREG6    26851       3027 EDOT       10397       3050 DYERROR   4050
0033 CDUY        14334       3337 ABSEDOT     7526       3031 TRAPEDQ   3754
3340 DAPTEMP2    10973       0031 TIME6       7488       3026 OMEGAU    3177
                             3341 FIREFCT     5567       3052 DZERROR   3164
                             0034 CDUZ        4934       3023 OMEGAR    3127
```

The routines that do those writes (the nearest label below the
instruction address gives the routine):

```
BACKP  ROT-TOUV  TJCALC  QERRCALC  TJLAW  PAXIS  NEGEDOT  SETSENSE
RERRCALC  SCALEE  CALCPERR  P-RATE  Q-RATE  STILLRCS  SCALEDOT  TJETLAW
DACLOOP  ERRTEST  R-RATE  ROTORQUE  RCS  QRAXIS
```

Only in the quiet flight: `NQTRAPS`, `NRTRAPS`, `NPTRAPS`. The 3
routines are the idle records of the autopilot when the autopilot has
no work. The idle records stop when the autopilot has work to do.

**Channel packets.** The flight with the nudge has 254 distinct packets
that the quiet flight does not have:

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

Only in the quiet flight: downlink words on 035, and no other packets.

The lens gives the meaning of the results. The nudge was about the Y
axis. Channel 233 is the pulse counter of the Y gimbal. Channel 233 is
the nudge as the nudge gets to the computer, 5,817 pulses. The cell
`CDUY` is the memory cell that gets those pulses. The cells `EDOT`,
`OMEGA`, `DYERROR`, and `DZERROR` are the rate cells and the error cells
of the autopilot.

The routines `TJLAW`, `TJETLAW`, and `TJCALC` calculate the fire times
of the jets. Channel 013 is the control word of the autopilot. Channel
005 is the jet commands that go out to the vehicle. The comparator put
the full reaction-control autopilot on the side of the nudge only, cell
by cell and routine by routine. The cause: those things occurred in 1
flight and not in the other flight.

## Step 3. Channel to motion, on the common clock

The vehicle rows do not repeat. Thus the reader read the row record as
flips: for each 100 ms slice, the fields that changed from the row
before. There are 39 fields: 14 from the vehicle and 25 channels. Each
row is 1 word of 40 bits.

The flight with the nudge has 169 distinct flip rows. The most common
flip rows, with names from the lens:

```
 124  ay az cdu_sent
  94  ay cdu_sent
  84  ay cdu_sent ch034 ch035
  82  ay az cdu_sent ch034 ch035
  41  (no change)
  37  ax ay az cdu_sent ch034 ch035
```

The quiet flight has 10 distinct flip rows. Each flip row is only
`ch034` and `ch035` (the downlink, the telemetry), with `ch013` in some
rows.

The rows with a flip of channel 005 (jet commands):

```
   7  ax ay az cdu_sent ch005 ch013 ch034 ch035
   6  ax ay az wy wz cdu_sent ch005 ch013 ch034 ch035
   4  ax ay az wy wz jets5 cdu_sent ch034 ch035
   2  ay wy wz jets5 cdu_sent
```

The jet rows are the last link. In the rows with a change of channel
005 of the computer, the jet field of the vehicle also changed. In the same rows,
the turn rates `wy` and `wz` also changed.

The field order was set before the run. No input gave the identity of each field. The only
question for the comparator was "these fields change in the same
100 ms". The comparator put the jet channel, the jet field, and the
turn rates together.

The RUNS table of the flip rows of the flight with the nudge is the
flight in sequence:

- a long sequence of rows with the downlink only
- then 1 row where the angles start to move
- then hundreds of rows of `ay cdu_sent`, with jet rows at intervals
  that become longer

The sequence is the nudge, the drift, the jet fires, and the decrease
of the rotation, as 1 continuous run.

## Step 3b. The vehicle rows at a smaller frame

The read at 208 bits made each row 1 word. Thus 2 rows with a difference
in only the last bit of 1 field were different words. The mint did not
look inside a row. A read of the same file at 16 bits (`--frame 16`)
makes each field 1 word. Then repeats appear:

- **Fields with no motion**: `4204` and `f764` have a count of exactly
  1,000, 1 for each row. Through the lens: vx = 1690.0 m/s and
  vz = -220.4, the 2 velocity fields. The 2 fields did not change.
- **Rate plateaus.** The top parts by density are pairs of rate words
  that hold for a period:
  - `ff8f.0007` repeats 244 times
  - `0013.004f` repeats 94 times
  - `0154.ffc0` repeats 74 times
  - `ff94.0002` repeats 65 times
  - `ff7c.ffb8` repeats 58 times
  - `ff42.ff7e` repeats 37 times

  The vehicle turns at a constant rate until a jet fires. Then the
  vehicle goes to a new constant rate. The plateaus are the jet fires of
  the autopilot, as steps in the record of the vehicle.
- **The axis of the nudge.** The class `{0.0} [0004+, +00b1]` has 5
  members, `fa5e fa3d fa53 fa48 f894`. The members are 5 rows with
  `0004` in the field before and `00b1` in the field after. Only this 1
  field is different. The classes `{0.1}` to `{0.5}` have the same
  shape.

  Through the lens, the neighbors that do not change are `ax` and
  `az`. The field in motion is `ay`, the Y angle. The Y angle is exactly
  the axis of the nudge. No input said Y.

At 8 bits (`--frame 8`), the result is finer: 89 classes at level 1.

The cause of the miss in the first read: a full row gets a score of
1.000 in the frame step. The frame step finds a column that is always 1
and a column that is always 0. Thus the frame step picked 208. To fold a
width is to divide the width into equal parts when the parts have the
same form. The fold check found that the 2 halves were different, so the
frame step did not fold. For a signal of rows, 208 is the wrong frame
for the mint, but the correct frame to see the layout.

Open task: the frame that the frame step chose can have no words that
repeat. In that case, try a read at the next width down that has words
that repeat. To cut a signal is to divide the signal into parts at a
boundary. The next width down is the same signal at a finer cut. The
records:
`held-vehicle.bin.frame16.record.txt`,
`held-vehicle.bin.frame8.record.txt`.

## The chain, backward

Each link in the list comes from the link below the link:

1. The vehicle rates change.
2. The jet field of the vehicle changes.
3. Channel 005 changes.
4. `TJLAW`, `TJETLAW`, and `TJCALC` write `FIREFCT` and `DAPTREG6`.
5. `P-RATE`, `Q-RATE`, and `QERRCALC` write `EDOT`, `OMEGA*`, and
   `D*ERROR`.
6. The pulses from channel 233 write `CDUY`.
7. The pulses come from outside.

Each link in the chain is 1 of 2 things. The first thing is a set of
words that the comparator put on the side of the nudge only. The second
thing is a set of fields that the comparator put in the same flip row.
The names came after the result. The comparator found the chain.

## The limits

- The "last value" of each channel in the row record loses the pulse
  channels. Channel 233 sends the same code 5,817 times. Thus the last
  value of channel 233 does not change, and channel 233 does not appear
  in the flips. The `cdu_sent` count of the vehicle carries that link in
  place of channel 233. A field with a count for each row, for each
  channel, can carry the link on the side of the computer also.
- Step 2 is a bridge on whole words. A bridge on parts (the sequences
  that the mint found) can give the *sequences* of the nudge only. Those
  sequences are routines as runs of writes, not only the single cells.
  The JSON of the writes record is 4 GB for a window of 100 s. The size
  of the JSON is the limit. The top parts of the text record are in
  `held-writes.bin.record.head.txt`.
- The flip rows have classes (190 classes). This run did not examine the
  classes.

## Files

- `bridge.txt`: the full output of step 2.
- `held-flips.bin.record.txt`, `quiet-flips.bin.record.txt`,
  `fields.txt`: the records of step 3 and the field order.
- `*-channels.bin.frame32.record.txt`: the channel records.
- `*-writes.bin.record.head.txt`: the top of the write records.
- `../bridge_flights.py`, `../flips.py`: the 2 readers. The readers use
  the lens only for the print step.
