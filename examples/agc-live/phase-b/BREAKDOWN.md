# Phase B: the same loop, with the vehicle on the socket

2026-10-11. The loop is the same loop as Phase A (`loop.py --vehicle`),
with the same 33 raw actions. No name is given. The vehicle model from
the 10-10 package (`vehicle.py`, without the hand controller) is a
second client on the socket of the emulator. The model sends gimbal
angles and accelerometer pulses to the computer. The model gets jet
commands and engine commands back from the computer.

The loop gets 1 more input: the goal. The goal is in the fields of the
vehicle. The goal is "on the ground and at rest":

- altitude 0
- each turn rate less than 0.5 deg/s
- vertical speed and horizontal speed less than 5 m/s

The run is 90 steps, each 10 s of machine time. The script `goalB.py`
checks the goal against the record of the vehicle.

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

The last 2 lines show the result. The vehicle got to altitude 0 at
136 s, in a fall. In 90 steps across the states of the machine, no press
of the loop changed these fields:

- the engine
- the thrust
- the jets
- the horizontal speed

The vehicle did not satisfy the full goal at any time. Thus there is no
chain from the goal back to a key press. The record shows the parts of
the goal that the vehicle did not satisfy: a horizontal speed (`vx`)
less than 5, and a vertical speed (`vz`) less than 5 near altitude 0.

The record shows the root cause directly. The vehicle starts at an
altitude of 15 km and a horizontal speed of 1,690 m/s, with the engine
off. The DSKY is the display and keyboard unit of the computer. No key
on the DSKY starts the engine. The altitude gets to 0 only in a crash.

## The cause of the failure to start the engine

The author predicted this result before the run. The record agrees with
the prediction. The descent program (P63) controls the engine. The
erasable memory is the part of the memory that the program can change.
P63 needs 3 values in the erasable memory:

- the state vector (the position of the spacecraft)
- the coordinates of the landing site
- the ignition time

On the real mission, the ground crew sent the 3 values by radio before
the burn. A machine with a fresh start has none of the 3 values. The
DSKY has no key sequence that writes the 3 values. The rope is the
read-only program memory. The machine that this loop got has only its
rope, and the erasable memory has no values at the start. Thus the
machine cannot land, with any sequence of presses.

The "loaded memory" is part of the machine, in the same way that the
rope is part of the machine. The memory is part of the definition of the
machine. This run did not get the loaded memory. The next run will
supply the loaded memory. The loaded memory is an input in the list of
inputs, not help from outside.

## Two results of the run about the loop itself

- **The transient at the start.** With the vehicle on the socket, the
  computer runs the turn-on sequence of the IMU (the inertial
  measurement unit) for the first 87 s. The display and some channels
  change on their own during the sequence. The baseline of 16 windows
  ran in that period. Thus the baseline tagged the display (010) and the
  channels 011, 012, 014, 030 as self-movers. The context lost the DSKY
  for the full run: 45 pairs of state and action, against the 232 pairs
  of Phase A. The correction: the baseline must wait until the machine
  no longer changes on its own. Only then can the baseline decide the
  meaning of "changes on its own". That is: loop until the machine is
  stable, then run the baseline. This run did not do this.
- **The clock.** The 136 s before impact is only 14 steps at this dwell
  time. On this vehicle model, no run is long enough to be useful until
  the engine can start. The engine cannot start without the loaded
  memory. The 2 corrections go together.

## The inputs

The inputs are the list of Phase A, and:

- the vehicle model (hardware). The model can have physics inside, but
  the loop does not look inside the model.
- the goal above
- the record of the vehicle (`vehicle.bin`), read as the sensor for the
  goal check

The loop did not get these inputs:

- information about the engine
- information about the programs
- the memory that must have values before the start
- the method to fly a landing

## Files

The files are:

- `loop.log`
- `vehicle.out`
- `vehicle.csv` (1 row for each 100 ms)
- `goal.txt` (the output of the reader)
- `goalB.py`
