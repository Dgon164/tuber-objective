# Running phases D and E on another machine

Everything the learner needs is in this repository. No flight computer
emulator is needed for these phases: the vehicle runs on its own, in
lockstep with the learner.

## What to install

- Python 3.10 or newer (these runs used 3.13).
- numpy, for phase E only (these runs used 2.5). Phase D needs nothing
  beyond Python.

```
git clone https://github.com/Dgon164/tuber-objective.git
cd tuber-objective
git checkout claude/sleepy-tesla-efzbaf
pip install -r examples/agc-live/phase-e/requirements.txt
```

## The pieces

| file | what it is |
|---|---|
| `examples/agc-live/phase-d/vehicle.py` | the vehicle: round moon, two stages, death, 22 instruments, lockstep clock. Both phases use it. |
| `examples/agc-live/phase-d/mission.py` | phase D's loop: directions of effects, a walk through seen states, rules, retries. Reaches orbit 62 of 63 attempts with the flight plan. |
| `examples/agc-live/phase-d/mission.txt` | phase D's flight plan (five phases). |
| `examples/agc-live/phase-e/grade.py` | phase E's loop: amounts, a model fitted from the rows, closeness learned from the record, plans tried in its head. Has not reached orbit. |
| `examples/agc-live/phase-e/mission.txt` | the bare mission: a path that never comes down, highest point under 300 km, engine off. |
| `examples/agc-live/phase-e/mission-plan.txt` | the five-phase flight plan for phase E. |
| `examples/agc-live/phase-e/goals/*.txt` | five other goals (a hop, a ballistic shot, a higher orbit, a speed, a velocity). |
| `examples/agc-live/phase-e/transfer.sh` | runs every goal from an earlier run's record, then from nothing. |
| `examples/agc-live/*/BREAKDOWN.md` | what went in, what the loop does, what happened, what it took. |
| `examples/agc-live/*/runs/*.log` | the logs of the runs the write-ups describe. |

## Phase D (the one that reaches orbit)

```
cd examples/agc-live/phase-d
python mission.py RUN_DIR 6000 --no-agc --max-attempt 300
```

`RUN_DIR` is created. It gets `mission.log` (one line per press),
`vehicle.out` (the vehicle's own log: lift-off, staging, deaths),
`vehicle.csv` and `vehicle.bin` (every instrument row), `memory.pkl`
(the learner's record, saved every 20 steps and loaded again if the
same RUN_DIR is used). 6,000 steps took about 2 minutes here. The
mission file is `--mission FILE`; `mission-bare.txt` is the same
mission without the pitch-over phase.

## Phase E

```
cd examples/agc-live/phase-e
python grade.py RUN_DIR 3000 --max-attempt 150 --mission mission.txt
python grade.py RUN_DIR 3000 --max-attempt 150 --mission mission-plan.txt
```

Options: `--step S` seconds of flight per press (5), `--horizon H`
steps the imagination runs (100), `--plans P` plans tried per step
(50), `--seed N`. The log is `grade.log`: one line per press with the
state, the plan chosen and what the model expected of it; at the end
of every attempt its closest approach and where it ended up; every 100
steps a summary of the model; at the end a table of all attempts.

Each step costs 1 to 3 seconds of wall clock, nearly all of it the
planning, so 3,000 steps is one to three hours. The runs here were
made on one processor core; two runs at once share it. More cores help
only by running separate runs in parallel; one run uses one core.

To start from an earlier run's record and plan against a different goal:

```
python grade.py NEW_RUN_DIR 600 --max-attempt 120 --mission goals/hop.txt --memory OLD_RUN_DIR
```

The old run's rows, presses and give-ups are loaded, the model is
fitted from them, and every past attempt is measured against the new
goal. To run all five goals from a record and then from nothing:

```
bash transfer.sh OLD_RUN_DIR OUT_DIR 400
```

That is ten runs of 400 steps, run one after another: about three
hours on one core.

## Writing a mission

One line per phase, worked in order; targets separated by `;`; `fK`
is the field at position K in the instrument row, listed at the top
of `vehicle.py`; operators `>`, `<`, `==`. A `prefer:` line sets the
second measure: `steps least` (default), `steps most`, `fK least`,
`fK most`, `fK == V`. Field 20 is where the current path comes down,
in km downrange from the pad, 32767 meaning never; field 19 the highest
point of the path in 100 m; field 16 the engine flag; field 17 the
stage; field 14 the propellant in the current stage in kg.

## With the flight computer

Phase D can also run with the Apollo flight computer in the loop
(`mission.py` without `--no-agc`), which needs the emulator built as
described in `examples/agc-live/README.md`. Phase E does not use it.

## State at close, 2026-10-20

- Phase D: complete; orbit 62 of 63 attempts with the flight plan,
  0 of 28 without.
- Phase E: six launches, no orbit. Launch 6 (flight plan, kept-target
  fix, all rates zero) was stopped at 1,386 of 3,000 steps: 15
  attempts, the turn reached twice, crashes after it. Launch 8 (bare
  mission, learned closeness, fall destination) was stopped at 262 of
  3,000 steps: 3 attempts. The transfer suite was written and checked
  but not run. Their logs are under `phase-e/runs/`.
