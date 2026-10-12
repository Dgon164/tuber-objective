# Phase B: the same loop with the vehicle on the socket

2026-10-11. Same loop as Phase A (`loop.py --vehicle`), same 33 raw
actions, nothing named. The vehicle plant from the 10-10 package
(`vehicle.py`, the hand removed) is a second client on the emulator's
socket: it feeds the computer gimbal and accelerometer pulses and takes
jet and engine commands back. One more given: the goal row, stated in
the vehicle's own fields — on the ground and still: altitude 0, each
turn rate under 0.5 deg/s, vertical and horizontal speed under 5 m/s.

90 steps, 10 s of machine time each. `goalB.py` reads the goal row
against the vehicle's record.

## The result

```
10512 vehicle rows, 1051 s of machine time
  alt    satisfied in  9152 rows  (first at 136.1 s)
  rates  satisfied in 10512 rows  (first at 0.0 s)
  vz     satisfied in    30 rows  (first at 0.0 s)
  vx     satisfied in     0 rows  -- NEVER
  the whole row: NEVER seen together
  fields that ever changed: alt, vz;  never changed: engine, jets, thrust, vx, wx, wy, wz
  at the first altitude-0 row: vz = -220.4 m/s, vx = 1690.0 m/s
```

The walk's answer is the last two lines. Altitude 0 was reached at
136 s — by falling. Nothing the loop pressed changed the engine, the
thrust, the jets, or the horizontal speed, in 90 steps across the
machine's states. The goal row was never seen, so there is no chain
from it to a key, and the record says which parts of it were never seen
at all: `vx` under 5, and `vz` under 5 anywhere near altitude 0.

That is the root cause, read off the record: the vehicle starts at
15 km and 1,690 m/s with no engine running; nothing on the DSKY lights
the engine; the only way altitude reaches 0 is impact.

## Why nothing on the DSKY lights the engine

This is the finding I said to expect before the run, and the record
bears it out. The engine is lit by the descent program (P63). P63 needs
the state vector, the landing site, and the ignition time in erasable
memory. On the real flight the ground sent those up by radio before the
burn. A fresh-start machine has none of them, and the DSKY has no key
sequence that writes them. So the machine as delivered to this loop —
rope only, no loaded memory — cannot land, whatever is pressed. The
"loaded memory" given from the plan (the machine includes its memory
the way it includes its rope) was not supplied here; supplying it is
the next run, and it is a stated given, not help.

## Two things the run showed about the loop itself

- **The startup transient.** With the vehicle attached, the computer
  runs an IMU turn-on sequence for the first 87 s, and the display and
  several channels change on their own during it. The sixteen-window
  baseline ran inside that, so it marked the display (010) and channels
  011, 012, 014, 030 as self-movers — and the context lost the DSKY for
  the whole run (45 state-action pairs instead of Phase A's 232). The
  baseline should wait until the machine has stopped changing on its
  own before it decides what "on its own" means: loop until stable,
  applied to the baseline. Not done here.
- **The clock.** 136 s to impact is 14 steps at this dwell. On this
  plant there is no run long enough to matter until the engine can be
  lit, and the engine can't be lit without the loaded memory. The two
  fixes go together.

## Givens

Phase A's list, plus: the vehicle plant (hardware; it may know
physics, the loop never sees inside it); the goal row above; the
vehicle's record (`vehicle.bin`) read as the goal's sensor.

Not given: anything about the engine, the programs, the pad load, or
how a landing is flown.

## Files

`loop.log`, `vehicle.out`, `vehicle.csv` (every 100 ms), `goal.txt`
(the reader's output), `goalB.py`.
