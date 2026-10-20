"""
mission.py -- the loop from phase-c, with retries, death, a mission in steps, and rules on top of the walk.

The same machine as phase-c: the flight computer on its socket, the vehicle as a second client, the
astronaut's controls on a third. The loop presses, records every instrument, keeps the effect of each
press in each state, and walks backward from a target through what it has seen. Four things are new.

  retries   The vehicle can die (vehicle.py: a crash or a tumble). The instruments go null, then a
            new vehicle is on the pad. The loop does not stop. It watches the nulls, waits for the pad,
            and counts a new attempt. Everything it learned stays.
  death     Dying is an effect like any other. The press before the nulls, in the state it was pressed
            in, gets the effect "alive went down". Surviving a step gets "alive held". So each (state,
            press) has a death rate, and the walk will not take a press whose death rate in this state
            is high.
  mission   The targets come from mission.txt: phases in order, each a list of field constraints.
            The loop works on the first phase not yet met. When all are met the mission is complete.
  rules     When the walk finds no path, the loop reads its own effects table as rules: press A moves
            field K this way. Where a rule held in some states and not others, it looks for the one
            field whose value separates the two sets: the condition. Then it chains backward from the
            target through rules and conditions to a press it can make now.

And on top of those, what the first runs showed was needed:

  order     Within a phase the targets are worked in the order written. The first one not met is the
            one being worked on. An exact-value target that is met and comes before it is to be kept:
            a press known to move that field is not made.
  credit    When an attempt ends, every press it made is marked against every phase the attempt did
            or did not reach. A press whose attempts missed a phase clearly more often than attempts
            in general did is not made again in that state while working on that phase.
  abort     An attempt that goes 300 steps (--max-attempt) without reaching a new phase is called
            off: the vehicle is given up, the instruments go null, the next attempt starts. A complete
            mission ends the same way, so the loop can try again and show whether it can repeat it.
  wait      One more action, wait, presses nothing. Holding, while a target the loop is already moving
            toward arrives, is waiting.

    python mission.py RUN_DIR STEPS [--speed N] [--dwell S] [--no-agc] [--step S] [--mission FILE] [--max-attempt N]
      RUN_DIR/memory.pkl is loaded if present and saved every 20 steps. --no-agc leaves out the flight
      computer and its DSKY keys and runs the vehicle in lockstep: it flies --step seconds (5 by default)
      per press and stands still while the loop thinks, however long that takes.
"""
import os, sys, time, socket, struct, pickle, subprocess, collections, signal, re
HERE = os.path.dirname(os.path.abspath(__file__))
AGC = os.path.join(HERE, '..')
sys.path.insert(0, AGC)
sys.path.insert(0, HERE)
import loop as L
import vehicle as VH

CTL_ACTIONS = [('ctl', c) for c in sorted(VH.CTL)]
ROW = VH.ROW
ROW_SIZE = struct.calcsize(ROW)
NFIELD = 20
ALIVE = NFIELD                                    # a virtual field: 1 alive, 0 dead
FIELD = ['oga', 'iga', 'mga', 'wx', 'wy', 'wz', 'alt', 'vx', 'vz', 'thrust', 'jets5', 'jets6', 'cdu', 'pipa',
         'prop', 'armed', 'engine', 'stage', 'peri', 'apo', 'alive']      # the lens: names for the log only
NULL_ALT = 0xffff


def sign(x):
    return (x > 0) - (x < 0)


def load_mission(path):
    phases = []
    for line in open(path):
        line = line.split('#')[0].strip()
        if not line:
            continue
        name, rest = line.split(':', 1)
        cons = []
        for c in rest.split(';'):
            m = re.match(r'\s*f(\d+)\s*(abs<|==|>|<)\s*(-?\d+)\s*$', c)
            if not m:
                raise SystemExit(f'mission.txt: cannot read "{c.strip()}"')
            cons.append((int(m.group(1)), m.group(2), int(m.group(3))))
        phases.append((name.strip(), cons))
    return phases


def unmet(cons, row):
    """which constraints the row fails, as (field, direction needed, op, value)"""
    out = []
    for k, op, val in cons:
        x = row[k]
        if op == '>' and x <= val: out.append((k, +1, op, val))
        if op == '<' and x >= val: out.append((k, -1, op, val))
        if op == '==' and x != val: out.append((k, sign(val - x) or +1, op, val))
        if op == 'abs<' and abs(x) >= val: out.append((k, -sign(x) or -1, op, val))
    return out


class Instruments:
    """the vehicle's rows since the last step; null rows mean dead"""
    def __init__(self):
        self.pos = 0
        self.last_row = None
        self.last_d1 = None
        self.dead = False

    def read(self):
        size = os.path.getsize('vehicle.bin')
        with open('vehicle.bin', 'rb') as f:
            f.seek(self.pos); data = f.read(size - self.pos)
        n = len(data) // ROW_SIZE
        self.pos += n * ROW_SIZE
        rows = [struct.unpack(ROW, data[i * ROW_SIZE:(i + 1) * ROW_SIZE])[1:] for i in range(n)]
        died = reborn = False
        live = []
        for r in rows:
            if r[6] == NULL_ALT and r[9] == 0xffff:
                if not self.dead:
                    died = True
                self.dead = True
            else:
                if self.dead:
                    reborn = True
                    self.last_row = None; self.last_d1 = None
                self.dead = False
                live.append(r)
        first = self.last_row if self.last_row is not None else (live[0] if live else None)
        prev = self.last_row
        d1 = []
        pd = self.last_d1
        for r in live:
            if prev is not None:
                d = tuple((r[k] - prev[k]) for k in range(NFIELD))
                d1.append(d); pd = d
            prev = r
        if live:
            self.last_row = prev
            self.last_d1 = pd
        win = tuple((self.last_row[k] - first[k]) if (first is not None and self.last_row is not None) else 0 for k in range(NFIELD))
        nchange = tuple(sum(1 for d in d1 if d[k] != 0) for k in range(NFIELD))
        # moving: changed on three or more rows in the window and ended somewhere else. A jump that takes two rows
        # (a hand-controller pulse) is a jump, not a movement
        h1 = tuple(sign(win[k]) if (win[k] != 0 and nchange[k] >= 3) else 0 for k in range(NFIELD))
        return live, d1, h1, died, reborn


def main():
    run = sys.argv[1]; budget = int(sys.argv[2])
    opts = sys.argv[3:]
    speed = int(opts[opts.index('--speed') + 1]) if '--speed' in opts else 20
    dwell = float(opts[opts.index('--dwell') + 1]) if '--dwell' in opts else 0.25
    step_s = float(opts[opts.index('--step') + 1]) if '--step' in opts else 5.0      # vehicle seconds per press without the flight computer
    no_agc = '--no-agc' in opts
    max_attempt = int(opts[opts.index('--max-attempt') + 1]) if '--max-attempt' in opts else 300   # steps without a new phase before mission control calls the attempt off
    mission_file = opts[opts.index('--mission') + 1] if '--mission' in opts else os.path.join(HERE, 'mission.txt')
    phases = load_mission(mission_file)
    os.makedirs(run, exist_ok=True); os.chdir(run)
    ACTIONS = ([] if no_agc else L.ACTIONS) + CTL_ACTIONS + [('wait', 0)]    # wait: press nothing this step
    port = 19697 + (os.getpid() % 500) * 10
    ctl_port = port + 2000
    for f in ('core', 'writes.bin', 'channels.bin', 'vehicle.bin', 'vehicle.csv'):
        if os.path.exists(f):
            os.remove(f)
    agc = None
    if not no_agc:
        env = dict(os.environ, AGC_SPEED=str(speed), AGC_TRACE_WRITES='writes.bin', AGC_TRACE_CHANNELS='channels.bin')
        agc = subprocess.Popen([os.path.join(AGC, 'virtualagc', 'yaAGC', 'yaAGC'), '--nodebug', '--no-resume', '--quiet',
                                f'--port={port}', os.path.join(AGC, 'virtualagc', 'Luminary099', 'MAIN.agc.bin')],
                               stdout=open('yaagc.out', 'w'), stderr=subprocess.STDOUT, env=env)
        time.sleep(1.5)
    veh = subprocess.Popen([sys.executable, os.path.join(HERE, 'vehicle.py'), '--port', str(port), '--ctl-port', str(ctl_port),
                            '--speed', str(speed), '--seconds', '100000000', '--pad', '1', '--out', '.', '--no-agc', '1' if no_agc else '0',
                            '--lockstep', '1' if no_agc else '0'],
                           stdout=open('vehicle.out', 'w'), stderr=subprocess.STDOUT)
    time.sleep(1.5)
    sock = None
    if not no_agc:
        sock = socket.create_connection(('127.0.0.1', port)); sock.setblocking(False)
    ctl = socket.create_connection(('127.0.0.1', ctl_port))
    log = open('mission.log', 'a')
    say = lambda s: (print(s, flush=True), log.write(s + '\n'), log.flush())

    hw = L.Hardware()
    ins = Instruments()

    def pause():
        """let the vehicle fly for one step. With the flight computer: wait dwell seconds of wall clock. Without
        it: tell the vehicle to advance step_s seconds and wait until its rows for that time are written"""
        if not no_agc:
            time.sleep(dwell)
            return
        want = os.path.getsize('vehicle.bin') + int(step_s / 0.1) * ROW_SIZE
        ctl.sendall(L.packet(VH.TICK, int(step_s * 10)))
        t_end = time.time() + 30
        while os.path.getsize('vehicle.bin') < want and time.time() < t_end:
            time.sleep(0.002)
    tried = collections.Counter(); went = collections.Counter(); contexts = {}
    effects = collections.defaultdict(collections.Counter)      # (state, action) -> Counter of (field, sign)
    effects_any = collections.defaultdict(collections.Counter)  # action -> Counter of (field, sign)
    misses = collections.Counter(); hits = collections.Counter()
    conditions = {}                                             # (action, field, sign) -> (state index j, frozenset of values)
    attempts = []                                               # per attempt: dict(start step, end step, phase reached, cause)
    doom = collections.Counter(); okay = collections.Counter()  # (state, action, phase) -> presses in attempts that missed / reached that phase
    presses = []                                                # this attempt's (state, action, phase at the time)
    self_moving = set(); ever_moving = set()
    step0 = 0; attempt = 1; phase_i = 0
    if os.path.exists('memory.pkl'):
        M = pickle.load(open('memory.pkl', 'rb'))
        tried.update(M['tried']); went.update(M['went']); contexts.update(M['contexts'])
        for k, v in M['effects'].items(): effects[k].update(v)
        for k, v in M['effects_any'].items(): effects_any[k].update(v)
        misses.update(M['misses']); hits.update(M['hits']); conditions.update(M.get('conditions', {}))
        attempts.extend(M.get('attempts', [])); doom.update(M.get('doom', {})); okay.update(M.get('okay', {}))
        self_moving = set(M['self_moving']); ever_moving = set(M.get('ever_moving', ())); step0 = M['step'] + 1
        attempt = M.get('attempt', 1) + 1
        say(f'resumed memory at step {step0}: {len(went)} transitions, {len(effects_any)} actions with effects, {len(attempts)} attempts so far; attempt {attempt} starts on the pad')
    say('mission: ' + ' -> '.join(f'{n} [{"; ".join(f"f{k} {op} {v}" for k, op, v in c)}]' for n, c in phases))

    pos_c = 0
    def read_channels():
        nonlocal pos_c
        if no_agc:
            return b'', set()
        size = os.path.getsize('channels.bin')
        with open('channels.bin', 'rb') as f:
            f.seek(pos_c); data = f.read(size - pos_c)
        pos_c = size
        n4 = len(data) // 4; mid = {}
        for i in range(n4):
            c, v = L.unpacket(data[4 * i:4 * i + 4])
            if c not in L.CONTROL_CHANNELS:
                hw.take(c, v)
            if i == n4 // 2:
                mid = dict(hw.state)
        moving = {k[0] for k in set(mid) | set(hw.state) if mid.get(k) != hw.state.get(k)}
        return data, moving

    # ---- watch: the baseline
    quiet = 0; windows = 0
    pause(); read_channels(); ins.read()
    h1 = tuple([0] * NFIELD)
    while quiet < 2 and windows < 60:
        pause()
        _, moving = read_channels()
        rows, d1, h1, died, reborn = ins.read()
        before = len(self_moving)
        self_moving |= moving
        windows += 1
        quiet = quiet + 1 if len(self_moving) == before else 0
    say(f'baseline: {windows} windows; channels that move by themselves: ' + ' '.join(f'{c:03o}' for c in sorted(self_moving)))

    def make_state(row, h1):
        if row is None:
            return ('dead',)
        for k in range(NFIELD):
            if h1[k] != 0:
                ever_moving.add(k)
        return hw.showing(self_moving) + tuple(('move', k, h1[k]) if k in ever_moving else ('hold', k, row[k]) for k in range(NFIELD))

    def instr(c):
        """the instrument part of a state, as a dict field -> ('move', dir) or ('hold', value)"""
        return {x[1]: (x[0], x[2]) for x in c if isinstance(x, tuple) and len(x) == 3 and x[0] in ('move', 'hold')}

    def death_rate(st, a):
        e = effects[(st, a)]
        d, s = e[(ALIVE, -1)], e[(ALIVE, 0)]
        return (d / (d + s)) if d + s >= 2 else 0.0

    def doom_rate(st, a, p):
        """of the attempts in which this press was made in this state while working on phase p, the share that
        never reached phase p"""
        d, o = doom[(st, a, p)], okay[(st, a, p)]
        return (d / (d + o)) if d + o >= 2 else 0.0

    def base_fail(p):
        """the share of all finished attempts that never reached phase p"""
        n = len(attempts)
        return (sum(1 for x in attempts if x['reached'] <= p) / n) if n else 1.0

    def bad(st, a, p):
        """a press that killed the vehicle here more often than not, or whose attempts missed phase p clearly more
        often than attempts in general did"""
        return death_rate(st, a) >= 0.5 or doom_rate(st, a, p) > max(0.5, base_fail(p) + 0.2)

    def harm(st, a, kept):
        """known to move a field this phase needs kept where it is: the press has ever moved it, anywhere.
        kept: list of (field, bad direction or 0 for any)"""
        for k, s in kept:
            e = effects_any[a]
            if (s == 0 and (e[(k, 1)] or e[(k, -1)])) or (s != 0 and e[(k, s)]):
                return True
        return False

    def close_attempt(reached):
        """credit by outcome: every press of this attempt, against every phase, by whether the attempt reached it"""
        for st, a, p in presses:
            for q in range(p, len(phases)):
                (okay if q < reached else doom)[(st, a, q)] += 1
        presses.clear()

    def learn_conditions():
        """for each (action, field, sign) that happened in some states and not in others where the action was
        pressed: the one instrument field whose values in the yes-states and the no-states do not overlap"""
        by_action = collections.defaultdict(list)
        for (st, a), e in effects.items():
            by_action[a].append((st, e))
        for a, lst in by_action.items():
            keys = set(k for st, e in lst for k in e)
            for (k, s) in keys:
                if s == 0 and k != ALIVE:
                    continue
                yes = [st for st, e in lst if e[(k, s)] > 0]
                no = [st for st, e in lst if e[(k, s)] == 0 and sum(e.values()) >= 1]
                if len(yes) < 2 or len(no) < 2:
                    continue
                best = None
                for j in range(NFIELD):
                    yv = set(instr(st).get(j, (None, None)) for st in yes)
                    nv = set(instr(st).get(j, (None, None)) for st in no)
                    if yv and nv and not (yv & nv):
                        score = len(yes) + len(no)
                        if best is None or score > best[0]:
                            best = (score, j, frozenset(yv))
                if best:
                    conditions[(a, k, s)] = (best[1], best[2])

    def condition_met(a, k, s, st):
        c = conditions.get((a, k, s))
        if c is None:
            return True
        j, vals = c
        return instr(st).get(j, (None, None)) in vals

    def works_here(a, k, s, st):
        """not known to fail here: fewer than two presses of a in this state without the move (k, s)"""
        e = effects[(st, a)]
        return not (sum(e.values()) >= 2 and e[(k, s)] == 0)

    def chain(need_k, need_s, st, depth, seen):
        """backward through the rules: an action that moves need_k the needed way, whose condition holds here;
        else an action that brings the condition about. Returns (action, why) or None."""
        if depth > 3:
            return None
        cands = [a for a in ACTIONS if effects_any[a][(need_k, need_s)] > effects_any[a][(need_k, -need_s)]
                 and not bad(st, a, phase_i) and works_here(a, need_k, need_s, st)]
        cands.sort(key=lambda a: -effects_any[a][(need_k, need_s)])
        for a in cands:
            if condition_met(a, need_k, need_s, st):
                return a, f'rule f{need_k}{"+" if need_s > 0 else "-"}'
        for a in cands:
            c = conditions.get((a, need_k, need_s))
            if c is None or (a, need_k, need_s) in seen:
                continue
            j, vals = c
            have = instr(st).get(j, (None, None))
            # what direction would take field j from what we have toward a value in vals
            want = None
            for kind, val in vals:
                if kind == 'hold' and have[0] == 'hold' and isinstance(val, int) and isinstance(have[1], int):
                    want = sign(val - have[1]); break
                if kind == 'move' and isinstance(val, int) and val != 0:
                    want = val; break
            if want:
                sub = chain(j, want, st, depth + 1, seen | {(a, need_k, need_s)})
                if sub:
                    return sub[0], f'{sub[1]} for f{j} then f{need_k}{"+" if need_s > 0 else "-"}'
        return None

    def save(step):
        pickle.dump(dict(tried=dict(tried), went=dict(went), contexts=contexts,
                         effects={k: dict(v) for k, v in effects.items()},
                         effects_any={k: dict(v) for k, v in effects_any.items()}, misses=dict(misses), hits=dict(hits),
                         conditions=conditions, attempts=attempts, doom=dict(doom), okay=dict(okay),
                         self_moving=self_moving, ever_moving=ever_moving,
                         step=step, attempt=attempt), open('memory.pkl', 'wb'))

    def last_cause():
        try:
            lines = [l for l in open('vehicle.out') if 'DEAD:' in l]
            return lines[-1].split('DEAD:')[1].strip() if lines else '?'
        except OSError:
            return '?'

    state = make_state(ins.last_row, h1)
    contexts[hash(state) & 0xffff] = state
    att = dict(start=step0, reached=0, max_alt=0, cause='', progress=step0)
    t0 = time.time()
    step = step0

    def rollover():
        """the vehicle is back on the pad: close the attempt, credit its presses, start the next"""
        nonlocal attempt, phase_i, att, state
        att['cause'] = 'mission complete' if att.get('done') else last_cause(); att['end'] = step
        attempts.append(att)
        close_attempt(att['reached'])
        say(f'attempt {attempt} over: reached phase {att["reached"]} of {len(phases)} ({phases[att["reached"] - 1][0] if att["reached"] else "none"}), '
            f'max altitude {att["max_alt"] * 10} m, {att["cause"]}; attempt {attempt + 1} on the pad')
        attempt += 1; phase_i = 0
        att = dict(start=step, reached=0, max_alt=0, cause='', progress=step)
        state = make_state(ins.last_row, h1)
        contexts[hash(state) & 0xffff] = state

    while step < step0 + budget:
        row = ins.last_row
        # ---- the mission: which phase, what it needs
        if ins.dead or row is None:
            pause()
            _, moving = read_channels(); rows, d1, h1, died, reborn = ins.read()
            if reborn:
                rollover()
            continue
        if step - att['progress'] >= max_attempt:
            say(f'step {step:4d}  attempt {attempt}  aborted: {max_attempt} steps without reaching phase {phase_i + 1} ({phases[phase_i][0]})')
            ctl.sendall(L.packet(VH.ABORT, 0)); pause()
            rows, d1, h1, died, reborn = ins.read()
            if reborn:
                rollover()
            att['progress'] = step
            continue
        att['max_alt'] = max(att['max_alt'], row[6] if row[6] != NULL_ALT else 0)
        while phase_i < len(phases) and not unmet(phases[phase_i][1], row):
            att['reached'] = phase_i + 1; att['progress'] = step
            say(f'step {step:4d}  attempt {attempt}  PHASE {phase_i + 1} {phases[phase_i][0]} reached: alt {row[6] * 10} m, vx {row[7] / 10:.0f} vz {row[8] / 10:.0f} m/s, stage {row[17] + 1}, peri {row[18] / 10:.0f} km')
            phase_i += 1
        if phase_i >= len(phases):
            say(f'step {step:4d}  attempt {attempt}  MISSION COMPLETE in {step - att["start"]} steps: alt {row[6] * 10} m, vx {row[7] / 10:.0f} vz {row[8] / 10:.0f} m/s, '
                f'lowest point {row[18] / 10:.0f} km, highest {row[19] / 10:.0f} km, {row[14]} kg left')
            # the mission is done; the vehicle is given up so that the next attempt can start from the pad
            att['done'] = True
            ctl.sendall(L.packet(VH.ABORT, 0)); pause()
            rows, d1, h1, died, reborn = ins.read()
            if reborn:
                rollover()
            continue
        need = unmet(phases[phase_i][1], row)
        need_map = {k: s for k, s, op, val in need}
        # the safety reflex: if this state matches what preceded deaths (a learned condition on 'alive went
        # down'), the first need is to change that field, before any mission target
        danger = []
        for (a, k, s), (j, vals) in conditions.items():
            if k == ALIVE and s == -1 and instr(state).get(j, (None, None)) in vals:
                kinds = {v[0] for v in vals}
                if kinds == {'move'}:
                    d = {v[1] for v in vals}
                    if len(d) == 1 and next(iter(d)) != 0:
                        danger.append((j, -next(iter(d))))
                elif kinds == {'hold'}:
                    # a held value that preceded deaths: move it toward the values that did not
                    here = instr(state)[j][1]
                    safe = [c[1] for st_a, e in effects.items() if e[(ALIVE, 0)] and not e[(ALIVE, -1)]
                            for c in [instr(st_a[0]).get(j)] if c and c[0] == 'hold' and c[1] != here]
                    if safe:
                        danger.append((j, sign(sum(safe) / len(safe) - here)))
        danger = list(dict.fromkeys(danger))
        first = need[:1]                                          # the target being worked on: the first not met, in written order
        work = danger + [(k, s) for k, s, op, val in first]      # in order: get out of danger, then that target
        # the targets of this phase to keep: the exact-value ones that are met and come before the first one not met
        kept = []
        for k, op, val in phases[phase_i][1]:
            if k in need_map:
                break
            if op == '==':
                kept.append((k, 0))
        ok = lambda a: not bad(state, a, phase_i) and not harm(state, a, kept)
        # ---- choose
        norm = lambda c: tuple(('move', x[1], 0) if (x and x[0] == 'hold' and x[1] in ever_moving) else x for x in c)
        nstate = norm(state)
        action, why = None, ''
        # 1. the walk through states seen, as in phase-c. A target state: every needed moving field was moving the
        #    needed way, and every needed jumping field held a value that satisfies its constraint.
        def satisfies(c):
            d = instr(c)
            for k, s, op, val in first:
                if k in ever_moving:
                    if d.get(k) != ('move', s):
                        return False
                else:
                    kind, v = d.get(k, (None, None))
                    if kind != 'hold' or unmet([(k, op, val)], [v if i == k else 0 for i in range(NFIELD)]):
                        return False
            return True
        targets = [norm(c) for c in contexts.values() if satisfies(c)]
        walk_path = None
        if targets:
            sa_total = collections.Counter()
            for (a0, act, b0), n in went.items():
                sa_total[(norm(a0), act)] += n
            usual = lambda a0, act, n, tot: n >= 2 and n * 2 >= tot[(a0, act)]
            if nstate in targets:
                def quiet_here(a):
                    """how often a press of a moves something: the share of presses that moved the field it moves
                    most, here if it was pressed here, else anywhere if pressed three times or more, else a half"""
                    for e, per_press in ((effects[(state, a)], NFIELD + 1), (effects_any[a], NFIELD)):
                        presses = sum(e.values()) / per_press
                        if presses >= (1 if e is effects[(state, a)] else 3):
                            return max([e[(k, 1)] + e[(k, -1)] for k in range(NFIELD)] + [0]) / presses
                    return 0.5
                # holding is waiting. If waiting is ruled out here, the press that most rarely moves anything
                action, why = (('wait', 0) if ok(('wait', 0)) else min(ACTIONS, key=lambda a: (not ok(a), quiet_here(a)))), 'hold'
            else:
                for strict in (True, False):
                    back = {t: [] for t in targets}; frontier = list(targets); depth = 0
                    while frontier and depth < 12 and nstate not in back:
                        nxt = []
                        for b in frontier:
                            for (a0, act, b0), n in went.items():
                                na, nb = norm(a0), norm(b0)
                                if nb == b and na not in back and na != nb and (not strict or usual(na, act, n, sa_total)) \
                                        and not bad(a0, act, phase_i) and not harm(a0, act, kept):
                                    back[na] = [act] + back[b]; nxt.append(na)
                        frontier = nxt; depth += 1
                    if nstate in back:
                        break
                if nstate in back and back[nstate] and ok(back[nstate][0]):
                    walk_path = back[nstate]
        # a walk of one press is taken as it is. A longer walk replays every press of the path once seen, side
        # trips included, so a rule that names one press for the first thing on the work list comes before it
        if action is None and walk_path and len(walk_path) == 1:
            action, why = walk_path[0], 'walk(1)'
        if action is None:
            for k, s in work:
                r = chain(k, s, state, 0, frozenset())
                if r and ok(r[0]) and r[1].startswith('rule'):
                    action, why = r[0], (('danger ' if (k, s) in danger else '') + r[1]); break
        if action is None and walk_path:
            action, why = walk_path[0], f'walk({len(walk_path)})'
        # 2. the rules: backward through effects and conditions, for the first thing on the work list
        if action is None:
            for k, s in work:
                r = chain(k, s, state, 0, frozenset())
                if r and ok(r[0]):
                    action, why = r[0], (('danger ' if (k, s) in danger else '') + r[1]); break
        # 3. direct: an action that has moved the first needed field the needed way, anywhere
        if action is None:
            for k, s in work:
                direct = [a for a in ACTIONS if effects_any[a][(k, s)] > effects_any[a][(k, -s)] and ok(a) and works_here(a, k, s, state)]
                if direct:
                    action, why = max(direct, key=lambda a: effects_any[a][(k, s)]), f'direct f{k}{"+" if s > 0 else "-"}'; break
        # 4. explore: least tried in this state; among those, one pressed 8+ times anywhere with no effect ever goes
        #    after the others, then least tried anywhere; one that was deadly, doomed or harmful here goes last of all
        if action is None:
            tried_any = collections.Counter()
            for (st, a), n in tried.items():
                tried_any[a] += n
            quiet_act = lambda a: tried_any[a] >= 8 and not any(sg != 0 for (k, sg) in effects_any[a])
            action, why = min(ACTIONS, key=lambda a: (not ok(a), tried[(state, a)], quiet_act(a), tried_any[a], ACTIONS.index(a))), 'explore'
        tried[(state, action)] += 1
        presses.append((state, action, phase_i))
        # ---- predict
        expected = {}
        for (k, s), n in effects[(state, action)].items():
            if k != ALIVE and n > expected.get(k, (0, 0))[1]:
                expected[k] = (s, n)
        # ---- act
        h1_before = h1; row_before = ins.last_row
        if action[0] == 'ctl':
            ctl.sendall(L.packet(action[1], 0))
        elif action[0] != 'wait':
            L.send(sock, action)
        pause()
        if agc is not None:
            agc.send_signal(signal.SIGUSR1); time.sleep(0.02)
            try:
                while sock.recv(65536):
                    pass
            except BlockingIOError:
                pass
        # ---- record
        cdata, moving = read_channels()
        rows, d1, h1, died, reborn = ins.read()
        self_moving |= moving
        if agc is not None:
            agc.send_signal(signal.SIGUSR2)
        # ---- compare: the effect on every field, death included, and the prediction
        before_state = state
        state = make_state(ins.last_row if not (ins.dead or died) else None, h1)
        if not (ins.dead or died):
            contexts[hash(state) & 0xffff] = state
        went[(before_state, action, state)] += 1
        changed = []
        if died:
            effects[(before_state, action)][(ALIVE, -1)] += 1
            effects_any[action][(ALIVE, -1)] += 1
            changed.append('DEAD')
        else:
            effects[(before_state, action)][(ALIVE, 0)] += 1
            if row_before is not None and ins.last_row is not None:
                for k in range(NFIELD):
                    sw0, sw1 = sign(h1_before[k]), sign(h1[k])
                    s = sign(sw1 - sw0)
                    if s == 0 and sw0 == 0 and sw1 == 0:
                        s = sign(ins.last_row[k] - row_before[k])
                    effects[(before_state, action)][(k, s)] += 1
                    effects_any[action][(k, s)] += 1
                    if s:
                        changed.append(f'{FIELD[k]}{"+" if s > 0 else "-"}')
                    if k in expected:
                        (hits if expected[k][0] == s else misses)[(before_state, action, k)] += 1
        name = VH.CTL.get(action[1], '') if action[0] == 'ctl' else 'wait' if action[0] == 'wait' else f'{action[0]} {action[1]}'
        r = ins.last_row
        where = '' if r is None else f'alt {r[6] * 10:6d} vx {r[7] / 10:5.0f} vz {r[8] / 10:5.0f} st {r[17] + 1} peri {r[18] / 10:6.0f}km'
        say(f"step {step:4d}  a{attempt:<2d} p{phase_i + 1}  {why:28s} {name:12s} {where}  effect: {' '.join(changed) or '-'}  {time.time() - t0:5.0f}s")
        if step % 20 == 19:
            learn_conditions()
            save(step)
        step += 1
        if reborn:
            rollover()
    learn_conditions()
    save(step)
    if agc is not None:
        sock.close(); agc.terminate(); agc.wait()
    ctl.close(); veh.terminate()
    say(f'done: {step - step0} steps, {attempt} attempts, {len(went)} transitions, {len(conditions)} conditions learned, predictions right {sum(hits.values())} wrong {sum(misses.values())}')
    say('attempts:')
    for i, a in enumerate(attempts):
        say(f'  {i + 1:3d}  steps {a["end"] - a["start"]:4d}  reached {a["reached"]}/{len(phases)}  max altitude {a["max_alt"] * 10:7d} m  {a["cause"]}')
    wins = [a for a in attempts if a.get('done')]
    say(f'missions complete: {len(wins)} of {len(attempts)} attempts' + (f'; first at attempt {attempts.index(wins[0]) + 1}; steps per complete mission {[a["end"] - a["start"] for a in wins]}' if wins else ''))
    if conditions:
        say('conditions:')
        for (a, k, s), (j, vals) in sorted(conditions.items(), key=lambda kv: str(kv[0])):
            name = VH.CTL.get(a[1], '') if a[0] == 'ctl' else 'wait' if a[0] == 'wait' else f'{a[0]} {a[1]}'
            say(f'  {name:12s} -> {FIELD[k]}{"+" if s > 0 else "-" if s < 0 else "="}  when {FIELD[j]} is {sorted(vals)[:4]}')


if __name__ == '__main__':
    main()
