"""
grade.py -- the loop with quantities, a grade of its own, and plans tried in its head.

The same vehicle as phase-d (round moon, two stages, death, lockstep clock) and the same kind of
mission file. What is different is how the loop chooses a press.

Phase-d kept the direction of every effect (thrust went up) and walked through states it had seen.
This loop keeps the amounts, and from them makes three things:

  model   What each press does to each instrument, as a jump: throttle up adds about 1000 to the
          thrust reading, +pitch adds 41 to the pitch rate. And how the instruments move on their
          own between presses, as a formula per instrument fitted to the rows: the altitude changes
          by the vertical speed, the pitch angle by the pitch rate, the sideways speed by thrust times
          angle. Also the things that happen on their own when a reading crosses a line (the thrust
          dropping to zero when the propellant runs out), and where it has died.
  grade   For any state, how many presses away from the targets it is: for each target not met, the
          gap divided by the most that reading has ever changed in one step. Dead is worse than any
          grade. The loop writes this grade from its own record. Nobody hands it one.
  plans   A plan is a list of presses with amounts: throttle up 4 times, +pitch once, wait 50 steps,
          -pitch once, stage, engine on, wait 6, engine off. The loop runs a plan through its model,
          grades where it ends up, and keeps the best of a hundred or so variants. Then it makes the
          first press of the best plan, reads the instruments, and plans again from wherever it is.

A plan is judged first on whether it reaches the targets, then on a second measure from the mission
file: fewest steps by default, or most, or a reading as low, high or close to a number as possible.

When the model has nothing to say (every plan grades the same as doing nothing), the loop explores
the way phase-d did: the press tried least often in a state like this one.

    python grade.py RUN_DIR STEPS [--mission FILE] [--step S] [--max-attempt N] [--horizon H] [--plans P]
"""
import os, sys, time, socket, struct, pickle, subprocess, collections, re, random
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AGC = os.path.join(HERE, '..')
PHASE_D = os.path.join(AGC, 'phase-d')
sys.path.insert(0, AGC)
sys.path.insert(0, PHASE_D)
import loop as L
import vehicle as VH
import mission as MD

NFIELD = MD.NFIELD
FIELD = MD.FIELD[:NFIELD]
ROW_SIZE = MD.ROW_SIZE
NULL_ALT = MD.NULL_ALT
ACTIONS = [('ctl', c) for c in sorted(VH.CTL)]      # the presses; -1 in a plan means wait
WAIT = -1
ROWS_PER_SEC = 10                                     # the vehicle writes a row every 0.1 s


def aname(i):
    return 'wait' if i == WAIT else VH.CTL[ACTIONS[i][1]]


def load_mission(path):
    """phases as in phase-d, plus the second measure: ('steps'|field, 'least'|'most'|('==', value))"""
    phases = []
    prefer = ('steps', 'least')
    for line in open(path):
        line = line.split('#')[0].strip()
        if not line:
            continue
        name, rest = line.split(':', 1)
        if name.strip() == 'prefer':
            m = re.match(r'\s*(steps|f\d+)\s+(least|most|==\s*-?\d+)\s*$', rest)
            if not m:
                raise SystemExit(f'mission: cannot read "{line}"')
            what = 'steps' if m.group(1) == 'steps' else int(m.group(1)[1:])
            how = m.group(2)
            prefer = (what, ('==', int(how[2:])) if how.startswith('==') else how)
            continue
        cons = []
        for c in rest.split(';'):
            m = re.match(r'\s*f(\d+)\s*(==|>|<)\s*(-?\d+)\s*$', c)
            if not m:
                raise SystemExit(f'mission: cannot read "{c.strip()}"')
            cons.append((int(m.group(1)), m.group(2), int(m.group(3))))
        phases.append((name.strip(), cons))
    return phases, prefer


def met(cons, row):
    """which constraints the row meets, as a boolean array over cons"""
    out = []
    for k, op, val in cons:
        x = row[k]
        out.append((x > val) if op == '>' else (x < val) if op == '<' else (abs(x - val) < 0.5))
    return np.array(out)


# ----------------------------------------------------------------------------------------------------
# the model

class Model:
    """everything the loop knows about what moves what, fitted from the rows"""
    SUB = 2                          # sub-steps per step in the imagination

    def __init__(self, step_rows):
        self.step_rows = step_rows             # rows per step (50 for 5 s)
        self.sub_rows = step_rows // self.SUB  # rows per sub-step
        self.fitted = False
        self.mean = np.zeros(NFIELD); self.std = np.ones(NFIELD)
        self.X = None; self.Y = None; self.Z = None                     # drift samples: rows, changes, standardized rows
        self.K = 50; self.LAM = 20.0; self.NMAX = 1500
        self.noise = np.ones(NFIELD)
        self.dmax = np.ones(NFIELD)
        self.jump_rows = []; self.jump_vals = []; self.jump_act = []     # presses: the row, the jump, the action
        self.event_rows = []; self.event_vals = []                      # jumps with no press
        self.label_rows = []; self.label_dead = []                      # rows labelled alive / dead
        self.jump_only = np.zeros(NFIELD, bool)
        self.best_rate = np.zeros((NFIELD, 2))                          # most a field moved per step, down / up
        self.ground_fatal = None                                        # speed at the ground that killed; None: unknown
        self.summary = ''
    def standard(self, rows):
        """rows in standard units, with the jump-only fields counted three times over so that neighbours share
        the same switch settings"""
        z = (rows - self.mean) / self.std
        return z * self.wz

    def fit(self, rows, alive, attempt, presses, step_starts, aborts=()):
        """rows: all rows seen (N x NFIELD); alive: bool per row; attempt: int per row; presses: list of (row
        index of the step start, action); step_starts: row index of every step start"""
        rows = np.asarray(rows, float)
        N = len(rows)
        if N < 20 * self.step_rows:
            return
        press_at = {p: a for p, a in presses}
        # sub-step pairs with no press inside: the drift
        X = []; Y = []
        for s in step_starts:
            if s + self.step_rows >= N:
                break
            a0 = attempt[s]
            first = s + 4 if s in press_at else s      # after a press, skip the rows the jump is in
            for i in range(first, s + self.step_rows - self.sub_rows + 1, 5):
                j = i + self.sub_rows
                if alive[i] and alive[j] and attempt[j] == a0:
                    X.append(rows[i]); Y.append(rows[j] - rows[i])
        if len(X) < 100:
            return
        X = np.array(X); Y = np.array(Y)
        live = rows[alive]
        self.mean = live.mean(0); self.std = np.maximum(live.std(0), 1.0)
        absY = np.abs(Y)
        self.noise = np.maximum(np.percentile(absY, 98, axis=0) * 1.5, 1.0)
        self.dmax = np.maximum(absY.max(0) * 2, 1.0)
        self.jump_only = np.percentile(absY, 98, axis=0) < 0.5
        self.wz = np.where(self.jump_only, 3.0, 1.0); self.wz[self.std <= 1.0] = 0.0
        if len(X) > self.NMAX:
            keep = np.random.default_rng(0).choice(len(X), self.NMAX, replace=False)
            X = X[keep]; Y = Y[keep]
        self.X = X; self.Y = Y; self.Z = self.standard(X)
        # jumps: what a press changed in the first three rows, beyond the drift of the three rows before
        self.jump_rows = []; self.jump_vals = []; self.jump_act = []
        for p, a in presses:
            if p + 3 < N and p >= 4 and alive[p - 1] and alive[p + 2] and attempt[p + 2] == attempt[p - 1]:
                before = rows[p - 1]; j = (rows[p + 2] - before) - (before - rows[p - 4])
                j[np.abs(j) < self.noise * 0.3] = 0.0
                self.jump_rows.append(before); self.jump_vals.append(j); self.jump_act.append(a)
        # events: a jump in a jump-only field during a step with no press
        self.event_rows = []; self.event_vals = []
        for s in step_starts:
            if s in press_at or s + self.step_rows > N:
                continue
            for i in range(s + 3, s + self.step_rows - 3, 3):
                if not (alive[i] and alive[i + 3] and attempt[i] == attempt[i + 3]):
                    continue
                d = rows[i + 3] - rows[i]
                big = self.jump_only & (np.abs(d) > self.noise)
                if big.any():
                    j = np.where(big, d, 0.0)
                    self.event_rows.append(rows[i]); self.event_vals.append(j)
        # alive and dead rows, for the imagination to tell where it dies
        self.label_rows = []; self.label_dead = []
        for i in range(1, N):
            if alive[i - 1] and not alive[i] and i not in aborts:        # a row mission control gave up on is not a death
                self.label_rows.append(rows[i - 1]); self.label_dead.append(True)
        every = max(25, N // 400)
        for i in range(0, N, every):
            if alive[i] and not (i + 1 < N and not alive[i + 1]):
                self.label_rows.append(rows[i]); self.label_dead.append(False)
        # the ground: the slowest arrival that killed, the fastest that did not. A row is an arrival at the
        # ground if the next row would be there at its speed (altitude in 10 m, speed in 0.1 m/s, rows 0.1 s apart)
        ground = [(abs(rows[i - 1][8]), not alive[i]) for i in range(1, N)
                  if alive[i - 1] and i not in aborts and rows[i - 1][6] <= abs(rows[i - 1][8]) / 1000 + 1 and (not alive[i] or rows[i][6] <= 0)]
        fatal = [v for v, d in ground if d]; safe = [v for v, d in ground if not d]
        self.ground_fatal = None if not fatal else (min(fatal) + max([v for v in safe if v < min(fatal)] + [0])) / 2
        # the most a field has moved in one step, each way
        S = []
        for s in step_starts:
            if s + self.step_rows < N and alive[s] and alive[s + self.step_rows] and attempt[s] == attempt[s + self.step_rows]:
                S.append(rows[s + self.step_rows] - rows[s])
        if S:
            S = np.array(S)
            for k in range(NFIELD):
                down = -S[:, k][S[:, k] < 0]; up = S[:, k][S[:, k] > 0]
                self.best_rate[k, 0] = np.percentile(down, 90) if len(down) else 0.0
                self.best_rate[k, 1] = np.percentile(up, 90) if len(up) else 0.0
        self.fitted = True
        acts = collections.Counter(self.jump_act)
        self.summary = (f'{len(X)} drift samples, {len(self.jump_rows)} presses, {len(self.event_rows)} events, '
                        f'{sum(self.label_dead)} deaths; ground fatal above {self.ground_fatal}; '
                        f'presses per action: ' + ' '.join(f'{aname(a)}:{n}' for a, n in sorted(acts.items())))

    def local(self, rows_q):
        """for each query row: the change per sub-step of every field, and the slope of that change against every
        field, from a line fitted through the K nearest drift samples (ridge toward the flat line)"""
        Zq = self.standard(rows_q)
        d = ((Zq[:, None, :] - self.Z[None, :, :]) ** 2).sum(-1)
        k = min(self.K, len(self.Z))
        nb = np.argpartition(d, k - 1, axis=1)[:, :k]                       # P x k
        dn = np.take_along_axis(d, nb, axis=1)
        w = np.exp(-dn / (dn.max(1, keepdims=True) + 1e-9))                  # the nearest count most
        A = np.concatenate([np.ones((len(rows_q), k, 1)), self.Z[nb] - Zq[:, None, :]], axis=2)   # P x k x (1+F)
        Yn = self.Y[nb]                                                      # P x k x F
        AtA = np.einsum('pki,pk,pkj->pij', A, w, A) + self.LAM * np.eye(A.shape[2])[None]
        AtY = np.einsum('pki,pk,pkf->pif', A, w, Yn)
        W = np.linalg.solve(AtA, AtY)                                        # P x (1+F) x F
        return W[:, 0, :], W[:, 1:, :]

    def formulas(self, row=None):
        """what the model says near this row: for each field that moves, the three fields its change depends on
        most, as change per standard unit of that field"""
        if self.Z is None or row is None:
            return []
        val, slope = self.local(np.array([row], float))
        out = []
        for k in range(NFIELD):
            if self.jump_only[k] or abs(val[0, k]) < 0.5 and np.abs(slope[0, :, k]).max() < 0.5:
                continue
            top = np.argsort(-np.abs(slope[0, :, k]))[:3]
            out.append(f'  d{FIELD[k]} = {val[0, k]:.1f} per sub-step here; slopes: ' +
                       ', '.join(f'{slope[0, j, k]:+.1f}/{FIELD[j]}' for j in top if abs(slope[0, j, k]) > 0.05))
        return out

    # ---- the imagination
    def nearest(self, rows_q, table, weights):
        """index of the nearest table row to each query row, in weighted standardized distance"""
        T = (np.asarray(table) - self.mean) / self.std * weights
        Q = (rows_q - self.mean) / self.std * weights
        d = ((Q[:, None, :] - T[None, :, :]) ** 2).sum(-1)
        return d.argmin(1), d.min(1)

    def weights(self):
        return self.wz * np.where(self.jump_only, 10.0 / 3.0, 1.0)

    def jump(self, rows_q, action):
        """the jump this press makes, from the nearest recorded press of it"""
        idx = [i for i, a in enumerate(self.jump_act) if a == action]
        if not idx:
            return np.zeros_like(rows_q)
        near, _ = self.nearest(rows_q, [self.jump_rows[i] for i in idx], self.weights())
        return np.array([self.jump_vals[idx[n]] for n in near])

    def drift(self, rows_q):
        if self.Z is None:
            return np.zeros_like(rows_q)
        d, _ = self.local(rows_q)
        d[:, self.jump_only] = 0.0
        return np.clip(d, -self.dmax, self.dmax)

    def events(self, rows_q, rows_prev):
        """jumps that happen on their own: if the nearest labelled wait row with a big jump is nearer than any
        recorded quiet row, it happens here too"""
        if not self.event_rows:
            return np.zeros_like(rows_q)
        table = self.event_rows + [r for r, d in zip(self.label_rows, self.label_dead) if not d]
        near, _ = self.nearest(rows_q, table, self.weights())
        out = np.zeros_like(rows_q)
        for q, n in enumerate(near):
            if n < len(self.event_rows):
                out[q] = self.event_vals[n]
        return out

    def dead(self, rows_q, rows_prev):
        """dead if nearer to a row that preceded a death than to any live row, or on the ground faster than has
        ever been survived"""
        out = np.zeros(len(rows_q), bool)
        if self.ground_fatal is not None:
            out |= (rows_q[:, 6] <= 0) & (np.abs(rows_q[:, 8]) > self.ground_fatal)
        if self.label_rows and any(self.label_dead):
            near, _ = self.nearest(rows_q, self.label_rows, self.weights())
            out |= np.array([self.label_dead[n] for n in near])
        return out

    def run(self, row, plans, horizon, phases, phase0, prefer):
        """run every plan from this row for horizon steps, through the phases of the mission in order. Returns per
        plan a cost tuple (phases still to reach, dead, best grade in the furthest phase, second measure) and a
        note. Reaching the last phase gives (0, 0, 0, second measure)."""
        P = len(plans); nph = len(phases)
        cons_of = [ph[1] for ph in phases]
        kept_of = [[c for q in range(i) for c in phases[q][1] if c[1] == '==' and c[0] not in {k for k, op, v in phases[i][1]}]
                   for i in range(nph)]
        cur = np.tile(np.asarray(row, float), (P, 1))
        seg = [0] * P; left = [plans[p][0][1] if plans[p] else 0 for p in range(P)]
        ph = [phase0] * P; best = np.full(P, np.inf); t_best = [0] * P
        reached = [None] * P; dead_at = [None] * P; at_reach = [None] * P
        alive = np.ones(P, bool)
        for t in range(horizon):
            for p in range(P):
                if not alive[p] or reached[p] is not None:
                    continue
                while seg[p] < len(plans[p]) and left[p] <= 0:
                    seg[p] += 1; left[p] = plans[p][seg[p]][1] if seg[p] < len(plans[p]) else 0
                if seg[p] < len(plans[p]):
                    a = plans[p][seg[p]][0]; left[p] -= 1
                    if a != WAIT:
                        cur[p] += self.jump(cur[p:p + 1], a)[0]
            prev = cur.copy()
            for _ in range(self.SUB):
                cur = cur + self.drift(cur)
                cur += self.events(cur, prev)
            cur[:, 6] = np.maximum(cur[:, 6], 0)
            died = self.dead(cur, prev) & alive
            G = np.array([self.grade(cur, cons_of[i], kept_of[i]) for i in range(nph)])     # phase x plan
            for p in range(P):
                if not alive[p] or reached[p] is not None:
                    continue
                if died[p]:
                    alive[p] = False; dead_at[p] = t; continue
                while G[ph[p], p] == 0 and ph[p] < nph - 1:
                    ph[p] += 1; best[p] = np.inf; t_best[p] = t
                g = G[ph[p], p]
                if g == 0:
                    reached[p] = t; at_reach[p] = cur[p].copy(); best[p] = 0
                elif g < best[p]:
                    best[p] = g; t_best[p] = t
            if not (alive & np.array([r is None for r in reached])).any():
                break
        out = []
        for p in range(P):
            remaining = nph - 1 - ph[p]
            if reached[p] is not None:
                what, how = prefer
                v = reached[p] + 1 if what == 'steps' else at_reach[p][what]
                sec = v if how == 'least' else -v if how == 'most' else abs(v - how[1])
                out.append(((0, 0, 0.0, float(sec)), f'reach {reached[p] + 1}'))
            elif dead_at[p] is not None:
                out.append(((remaining, 1, float(best[p]), 0.0), f'phase {ph[p] + 1} best {best[p]:.0f} dead {dead_at[p] + 1}'))
            else:
                out.append(((remaining, 0, float(best[p]), float(t_best[p])), f'phase {ph[p] + 1} best {best[p]:.0f} at {t_best[p] + 1}'))
        return out

    def grade(self, rows_q, cons, kept):
        """presses to go: for each constraint not met, the gap over a one-step change that field sustains (the 90th
        percentile of its one-step changes that way)"""
        g = np.zeros(len(rows_q))
        for k, op, val in cons + kept:
            x = rows_q[:, k]
            gap = np.where(x <= val, val - x + 1, 0) if op == '>' else np.where(x >= val, x - val + 1, 0) if op == '<' else np.abs(x - val)
            if op == '==':
                gap = np.where(gap < 0.5, 0, gap)
            up = (op == '>') | ((op == '==') & (x < val))
            rate = np.where(up, self.best_rate[k, 1], self.best_rate[k, 0])
            g += np.where(gap > 0, gap / np.maximum(rate, 1e-9) + 1, 0)
            g = np.minimum(g, 1e6)
        return g


# ----------------------------------------------------------------------------------------------------
# the plans

def mutate(plan, rng, nact):
    plan = [list(s) for s in plan]
    r = rng.random()
    if plan and r < 0.3:
        s = rng.randrange(len(plan)); plan[s][1] = max(1, plan[s][1] + rng.choice([-3, -1, 1, 3]))
    elif plan and r < 0.5:
        s = rng.randrange(len(plan)); plan[s][0] = rng.choice([WAIT] + list(range(nact)))
    elif r < 0.75 or not plan:
        s = rng.randrange(len(plan) + 1)
        a = rng.choice([WAIT] + list(range(nact)))
        plan.insert(s, [a, rng.randrange(1, 40) if a == WAIT else rng.randrange(1, 5)])
    else:
        del plan[rng.randrange(len(plan))]
    plan = [tuple(s) for s in plan if s[1] > 0][:8]
    return plan


def random_plan(rng, nact):
    plan = []
    for _ in range(rng.randrange(1, 5)):
        a = rng.choice([WAIT] + list(range(nact)))
        plan.append((a, rng.randrange(1, 40) if a == WAIT else rng.randrange(1, 5)))
    return plan


def shift(plan):
    """the plan after its first press is made"""
    if not plan:
        return []
    a, n = plan[0]
    return ([(a, n - 1)] if n > 1 else []) + list(plan[1:])


def plan_text(plan):
    return ' '.join(f'{aname(a)}x{n}' if a != WAIT else f'wait{n}' for a, n in plan) or '(nothing)'


# ----------------------------------------------------------------------------------------------------
# the loop

def main():
    run = sys.argv[1]; budget = int(sys.argv[2]); opts = sys.argv[3:]
    get = lambda flag, default, typ: typ(opts[opts.index(flag) + 1]) if flag in opts else default
    step_s = get('--step', 5.0, float)
    max_attempt = get('--max-attempt', 300, int)
    horizon = get('--horizon', 100, int)
    nplans = get('--plans', 50, int)
    mission_file = get('--mission', os.path.join(HERE, 'mission.txt'), str)
    seed = get('--seed', 1, int)
    rng = random.Random(seed)
    phases, prefer = load_mission(mission_file)
    os.makedirs(run, exist_ok=True); os.chdir(run)
    for f in ('vehicle.bin', 'vehicle.csv'):
        if os.path.exists(f):
            os.remove(f)
    port = 19697 + (os.getpid() % 500) * 10; ctl_port = port + 2000
    veh = subprocess.Popen([sys.executable, os.path.join(PHASE_D, 'vehicle.py'), '--port', str(port), '--ctl-port', str(ctl_port),
                            '--speed', '100', '--seconds', '100000000', '--pad', '1', '--out', '.', '--no-agc', '1', '--lockstep', '1'],
                           stdout=open('vehicle.out', 'w'), stderr=subprocess.STDOUT)
    time.sleep(1.5)
    ctl = socket.create_connection(('127.0.0.1', ctl_port))
    log = open('grade.log', 'a')
    say = lambda s: (print(s, flush=True), log.write(s + '\n'), log.flush())
    step_rows = int(step_s * ROWS_PER_SEC)
    ins = MD.Instruments()

    def pause():
        want = os.path.getsize('vehicle.bin') + step_rows * ROW_SIZE
        ctl.sendall(L.packet(VH.TICK, int(step_s * 10)))
        t_end = time.time() + 30
        while os.path.getsize('vehicle.bin') < want and time.time() < t_end:
            time.sleep(0.002)

    rows = []; alive = []; attempt_of = []; presses = []; step_starts = []
    attempt = 1
    tried = collections.Counter()
    aborts = set()                      # row indices where mission control gave the vehicle up

    def read():
        """rows since the last read, live ones and the count of null ones, in order of arrival"""
        size = os.path.getsize('vehicle.bin')
        with open('vehicle.bin', 'rb') as f:
            f.seek(ins.pos); data = f.read(size - ins.pos)
        n = len(data) // ROW_SIZE; ins.pos += n * ROW_SIZE
        died = reborn = False
        for i in range(n):
            r = struct.unpack(MD.ROW, data[i * ROW_SIZE:(i + 1) * ROW_SIZE])[1:]
            if r[6] == NULL_ALT and r[9] == 0xffff:
                if not ins.dead:
                    died = True
                ins.dead = True
                rows.append(np.full(NFIELD, np.nan)); alive.append(False); attempt_of.append(attempt)
            else:
                if ins.dead:
                    reborn = True
                ins.dead = False
                ins.last_row = np.array([float(x) for x in r]); rows.append(ins.last_row); alive.append(True); attempt_of.append(attempt)
        return died, reborn

    def state_key(row):
        """a coarse state for exploring: the value of every jump-only field, the sign of change of the rest"""
        prev = rows[-1 - step_rows // 5] if len(rows) > step_rows // 5 and alive[-1 - step_rows // 5] else row
        return tuple(int(row[k]) if (model.jump_only[k] or not model.fitted) else int(np.sign(round(row[k] - prev[k]))) for k in range(NFIELD))

    def last_cause():
        try:
            lines = [l for l in open('vehicle.out') if 'DEAD:' in l]
            return lines[-1].split('DEAD:')[1].strip() if lines else '?'
        except OSError:
            return '?'

    model = Model(step_rows)
    pause(); read()
    attempts = []
    att = dict(start=0, reached=0, progress=0, max_alt=0, best_grade=float('inf'), pressed=set())
    credit = collections.defaultdict(list)       # (state key, action) -> best grade of each attempt it was pressed in
    plan = []; phase_i = 0; step = 0; t0 = time.time()
    say(f'mission: ' + ' -> '.join(f'{n} [{"; ".join(f"f{k} {op} {v}" for k, op, v in c)}]' for n, c in phases) + f'; prefer {prefer}')

    def rollover(cause):
        nonlocal attempt, phase_i, att, plan
        att['end'] = step; att['cause'] = cause; attempts.append(att)
        for ka in att['pressed']:
            credit[ka].append(att['best_grade'])
        say(f'attempt {attempt} over: reached phase {att["reached"]} of {len(phases)}, max altitude {att["max_alt"] * 10:.0f} m, best grade {att["best_grade"]:.0f}, {cause}; attempt {attempt + 1} on the pad')
        attempt += 1; phase_i = 0; plan = []
        att = dict(start=step, reached=0, progress=step, max_alt=0, best_grade=float('inf'), pressed=set())

    while step < budget:
        row = ins.last_row
        if ins.dead or row is None:
            pause(); died, reborn = read()
            if reborn:
                rollover(last_cause())
            continue
        if step - att['progress'] >= max_attempt:
            say(f'step {step:4d}  attempt {attempt}  aborted: {max_attempt} steps without reaching phase {phase_i + 1}')
            aborts.add(len(rows)); ctl.sendall(L.packet(VH.ABORT, 0)); pause(); died, reborn = read()
            if reborn:
                rollover(last_cause())
            att['progress'] = step
            continue
        att['max_alt'] = max(att['max_alt'], row[6])
        while phase_i < len(phases) and met(phases[phase_i][1], row).all():
            att['reached'] = phase_i + 1; att['progress'] = step
            say(f'step {step:4d}  attempt {attempt}  PHASE {phase_i + 1} {phases[phase_i][0]} reached: alt {row[6] * 10:.0f} m, vx {row[7] / 10:.0f} vz {row[8] / 10:.0f} m/s, '
                f'stage {row[17] + 1:.0f}, low {row[18] / 10:.0f} km high {row[19] / 10:.0f} km')
            phase_i += 1
        if phase_i >= len(phases):
            say(f'step {step:4d}  attempt {attempt}  MISSION COMPLETE in {step - att["start"]} steps, {sum(1 for p, a in presses if p >= step_starts[att["start"]])} presses: '
                f'alt {row[6] * 10:.0f} m, vx {row[7] / 10:.0f} vz {row[8] / 10:.0f} m/s, low {row[18] / 10:.0f} km high {row[19] / 10:.0f} km, {row[14]:.0f} kg left')
            att['done'] = True
            aborts.add(len(rows)); ctl.sendall(L.packet(VH.ABORT, 0)); pause(); died, reborn = read()
            if reborn:
                rollover('mission complete')
            continue
        cons = phases[phase_i][1]
        kept = [c for p in range(phase_i) for c in phases[p][1] if c[1] == '==' and c[0] not in {k for k, op, v in cons}]
        # an exact target that has only ever moved away from its value, for 30 steps now: nothing known brings it
        # back, and the attempt is called off rather than waited out
        lost = [k for k, op, val in cons + kept if op == '==' and abs(row[k] - val) >= 0.5 and model.fitted
                and model.best_rate[k, 1 if row[k] < val else 0] == 0 and model.best_rate[k, 0 if row[k] < val else 1] > 0]
        att['lost_since'] = min(att.get('lost_since', step), step) if lost else step
        if lost and step - att['lost_since'] >= 30:
            say(f'step {step:4d}  attempt {attempt}  aborted: {FIELD[lost[0]]} has only ever moved away from its target')
            aborts.add(len(rows)); ctl.sendall(L.packet(VH.ABORT, 0)); pause(); died, reborn = read()
            if reborn:
                rollover(last_cause())
            continue
        # ---- fit the model now and then
        if step % 25 == 0 and len(rows) >= 20 * step_rows:
            al = np.array(alive); R = np.array([r if a else np.zeros(NFIELD) for r, a in zip(rows, al)])
            model.fit(R, al, np.array(attempt_of), presses, step_starts, aborts)
            if step % 100 == 0 and model.fitted:
                say(f'step {step:4d}  model: {model.summary}')
                for f in model.formulas(row):
                    say(f)
        # ---- choose
        why = ''; action = WAIT
        g_now = model.grade(np.array([row]), cons, kept)[0] if model.fitted else float('nan')
        avoid = set()
        if model.fitted:
            cands = [[], plan] + [[(a, 1)] for a in range(len(ACTIONS))]
            for _ in range(nplans):
                cands.append(mutate(plan, rng, len(ACTIONS)) if (plan and rng.random() < 0.6) else random_plan(rng, len(ACTIONS)))
            scored = model.run(row, cands, horizon, phases, phase_i, prefer)
            order = sorted(range(len(cands)), key=lambda i: (scored[i][0], len(cands[i])))
            b = order[0]; nothing = scored[0][0]; top = scored[b][0]
            # a plan is taken if it reaches the end, gets a phase further or avoids a death that doing nothing
            # meets, or ends at least one press closer within the same phase
            if top[2] == 0 and top[0] == 0 or top[:2] < nothing[:2] or (top[:2] == nothing[:2] and top[2] <= nothing[2] - 1):
                plan = list(cands[b]); action = plan[0][0] if plan else WAIT
                why = f'plan[{scored[b][1]}] {plan_text(plan)}'
            elif plan and scored[1][0][:3] <= nothing[:3]:
                # the plan from last step is still no worse than doing nothing: keep it
                action = plan[0][0]; why = f'plan[{scored[1][1]}] {plan_text(plan)}'
            elif row[6] > 0 and step % 10 != 0:
                plan = []; why = 'wait'; action = WAIT
            else:
                plan = []
            # a single press the model says loses a phase is not explored either (a predicted death is not enough:
            # the death check is a nearest-row guess and early on it flags most presses)
            avoid = {a for a in range(len(ACTIONS)) if scored[2 + a][0][0] > nothing[0] or scored[2 + a][0][2] > 2 * nothing[2] + 10}
        if not why:
            # explore: presses never made in a state like this first; then the ones whose attempts got closest
            key = state_key(row)
            def score(a):
                c = credit.get((key, a))
                return (a in avoid, tried[(key, a)] > 0, np.mean(c) if c else 0.0, rng.random())
            action = min(range(len(ACTIONS)), key=score)
            tried[(key, action)] += 1
            why = 'explore'
        if not np.isnan(g_now):
            att['best_grade'] = min(att['best_grade'], g_now)
        if action != WAIT:
            att['pressed'].add((state_key(row), action))
        # ---- act
        p0 = len(rows); step_starts.append(p0)
        if action != WAIT:
            presses.append((p0, action)); ctl.sendall(L.packet(ACTIONS[action][1], 0))
        pause(); died, reborn = read()
        plan = shift(plan) if why.startswith('plan') else []
        if why == 'wait':
            why = 'wait (in flight, nothing better; exploring every tenth step)'
        r = ins.last_row if not (ins.dead or died) else None
        where = '' if r is None else f'alt {r[6] * 10:7.0f} vx {r[7] / 10:5.0f} vz {r[8] / 10:5.0f} pitch {r[1] / 100:6.1f} st {r[17] + 1:.0f} low {r[18] / 10:6.0f}km high {r[19] / 10:6.0f}km'
        say(f'step {step:4d}  a{attempt:<2d} p{phase_i + 1}  grade {g_now:8.0f}  {aname(action):13s} {where}  {why[:90]}{"  DEAD" if died else ""}  {time.time() - t0:5.0f}s')
        if step % 50 == 49:
            pickle.dump(dict(rows=np.array([r if a else np.full(NFIELD, np.nan) for r, a in zip(rows, alive)]), alive=np.array(alive),
                             attempt=np.array(attempt_of), presses=presses, step_starts=step_starts, attempts=attempts, step=step),
                        open('memory.pkl', 'wb'))
        step += 1
        if reborn:
            rollover(last_cause())
    ctl.close(); veh.terminate()
    say(f'done: {step} steps, {attempt} attempts; {time.time() - t0:.0f} s')
    say('attempts:')
    for i, a in enumerate(attempts):
        say(f'  {i + 1:3d}  steps {a["end"] - a["start"]:4d}  reached {a["reached"]}/{len(phases)}  max altitude {a["max_alt"] * 10:7.0f} m  {a["cause"]}')
    wins = [a for a in attempts if a.get('done')]
    say(f'missions complete: {len(wins)} of {len(attempts)} attempts' + (f'; first at attempt {attempts.index(wins[0]) + 1}; steps per complete mission {[a["end"] - a["start"] for a in wins]}' if wins else ''))
    if model.fitted:
        say('model: ' + model.summary)


if __name__ == '__main__':
    main()
