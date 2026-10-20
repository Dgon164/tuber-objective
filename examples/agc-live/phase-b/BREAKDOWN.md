# Phase B: the same loop, with the vehicle attached

2026-10-11. The loop is the same as in Phase A (`loop.py --vehicle`),
with the same 33 raw actions and still no names for any of them. This
time a model of the lunar module, `vehicle.py` from the 10-10 work,
without the hand controller, is attached as a second client on the
emulator's socket, the network connection through which any program can
act as the computer's hardware. The model sends the computer gimbal
angles (which way the vehicle is pointing) and accelerometer pulses
(how hard it's accelerating), and gets jet commands and engine commands
back.

The loop gets one more input than in Phase A: a goal, stated in the
vehicle's own fields. The goal is "on the ground and at rest":

- altitude 0
- each turn rate under 0.5 degrees per second
- vertical speed and horizontal speed under 5 metres per second

The run is 90 steps, each 10 seconds of machine time. `goalB.py` checks
the goal against the vehicle's recording.

## What came out

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

The last two lines tell the story. The vehicle reached altitude 0 at
136 seconds, falling. Across 90 steps and every state the machine was
in, no press changed:

- the engine
- the thrust
- the jets
- the horizontal speed

The vehicle never satisfied the whole goal at once, so there's no chain
to trace from the goal back to a key press. The recording shows which
parts of the goal were never met: horizontal speed (`vx`) under 5, and
vertical speed (`vz`) under 5 near altitude 0.

The recording shows the root cause directly. The vehicle starts at
15 km altitude and 1,690 m/s horizontal speed with the engine off. The
DSKY is the panel of keys and lit digits the astronauts used to talk to
the computer, and no key on it starts the engine. The only way altitude
reaches 0 is a crash.

## Why the engine couldn't start

The author predicted this before the run, and the recording agrees. The
engine is controlled by P63, the descent program, the part of the
flight program that flies the braking burn. P63 needs three values to be
in erasable memory, the part of the computer's memory the program can
change while it runs:

- the state vector (where the spacecraft is and how fast it's moving)
- the coordinates of the landing site
- the ignition time

On the real mission the ground crew sent those three values up by radio
before the burn. A freshly started machine has none of them, and there
is no key sequence on the DSKY that writes them. The rope is the
computer's read-only program memory, and the machine this loop was
given had only its rope; erasable memory started empty. So the machine
can't land, whatever is pressed.

The loaded memory is part of the machine in the same way the rope is:
it's part of what the machine is. This run didn't get it. The next run
will supply it, as one more item on the list of inputs, not as help
from outside.

## Two things the run showed about the loop itself

- **The startup transient.** The IMU is the inertial measurement unit,
  the gyroscope platform that tells the computer which way the vehicle
  is pointing. With the vehicle attached, the computer spends its first
  87 seconds running the IMU's turn-on sequence, and during that time
  the display and some channels change on their own. A channel is a
  numbered signal path between the computer and the hardware around
  it. The 16-window baseline, the loop's test for channels that move
  with nothing pressed, ran during that period, so it tagged the
  display (010) and channels 011, 012, 014 and 030 as self-movers. The
  loop then left the DSKY out of its state for the whole run: 45
  state-action pairs, against 232 in Phase A.

  The fix: the baseline has to wait until the machine has stopped
  changing on its own, because only then can it tell what "changes on
  its own" means. In short, loop until the machine is stable, then run
  the baseline. This run didn't.
- **The clock.** The 136 seconds before impact is only 14 steps at this
  dwell. On this vehicle model no run is long enough to be useful until
  the engine can start, and the engine can't start without the loaded
  memory. The two fixes go together.

## What went in

Everything on Phase A's list, plus:

- the vehicle model, treated as hardware. The model has physics inside,
  but the loop never looks inside it.
- the goal above
- the vehicle's recording (`vehicle.bin`), read as the sensor for the
  goal check

The loop was not given:

- anything about the engine
- anything about the programs
- the memory that has to be loaded before the start
- how to fly a landing

## Files

- `loop.log`
- `vehicle.out`
- `vehicle.csv` (one row per 100 ms)
- `goal.txt` (what the reader printed)
- `goalB.py`
