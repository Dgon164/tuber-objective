# Phase B: the same loop, now with the vehicle on the socket

2026-10-11. Same loop as Phase A (`loop.py --vehicle`), same 33 raw
actions, nothing named. The vehicle model from the 10-10 package
(`vehicle.py`, with the hand controller removed) is a second client on
the emulator's socket: it feeds the computer gimbal angles and
accelerometer pulses and takes jet and engine commands back. One
additional input: the goal, stated in the vehicle's own fields -- on the
ground and still, meaning altitude 0, each turn rate under 0.5 deg/s,
vertical and horizontal speed under 5 m/s.

90 steps, 10 s of machine time each. `goalB.py` checks the goal against
the vehicle's record.

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

The story is in the last two lines. Altitude 0 was reached at 136 s --
by falling. Nothing the loop pressed changed the engine, the thrust, the
jets, or the horizontal speed, in 90 steps across the machine's states.
The goal was never fully met, so there is no chain from it back to a
key press. The record shows which parts of the goal were never achieved:
horizontal speed (`vx`) under 5, and vertical speed (`vz`) under 5
anywhere near altitude 0.

That is the root cause, read straight from the record: the vehicle
starts at 15 km altitude and 1,690 m/s horizontal speed with no engine
running. Nothing you can press on the DSKY starts the engine. The only
way altitude reaches 0 is by crashing.

## Why nothing on the DSKY starts the engine

This is the finding I predicted before the run, and the record confirms
it. The engine is controlled by the descent program (P63). P63 needs the
state vector (where the spacecraft is), the landing site coordinates,
and the ignition time loaded into erasable memory. On the real mission,
the ground crew sent all that up by radio before the burn. A
fresh-started machine has none of it, and the DSKY has no key sequence
that writes it. So the machine as delivered to this loop -- with only
its rope (read-only program) and no pre-loaded memory -- cannot land, no
matter what you press. The "loaded memory" (the machine includes its
memory the way it includes its rope -- it is part of what defines the
machine) was not supplied here; supplying it is the next run, and it is
a stated input, not outside help.

## Two things the run showed about the loop itself

- **The startup transient.** With the vehicle attached, the computer
  runs an IMU (inertial measurement unit) turn-on sequence for the first
  87 s, and the display and several channels change on their own during
  it. The sixteen-window baseline ran inside that period, so it tagged
  the display (010) and channels 011, 012, 014, 030 as self-movers --
  and the context lost the DSKY for the entire run (45 state-action
  pairs instead of Phase A's 232). The fix: the baseline should wait
  until the machine has stopped changing on its own before it decides
  what "changing on its own" means. In other words, loop until stable
  before running the baseline. Not done here.
- **The clock.** 136 s to impact is only 14 steps at this dwell time.
  On this vehicle model there is no run long enough to matter until the
  engine can be started, and the engine cannot be started without the
  loaded memory. The two fixes go together.

## What was given

Phase A's list, plus: the vehicle model (hardware; it may know physics
internally, but the loop never looks inside it); the goal described
above; the vehicle's record (`vehicle.bin`) read as the sensor for
checking the goal.

Not given: anything about the engine, the programs, the memory that
needs to be pre-loaded, or how a landing is actually flown.

## Files

`loop.log`, `vehicle.out`, `vehicle.csv` (every 100 ms), `goal.txt`
(the reader's output), `goalB.py`.
