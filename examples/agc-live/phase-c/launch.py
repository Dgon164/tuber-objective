"""
launch.py -- on the pad, at rest, with the astronaut's controls. Watch, touch, compare, remember.
Then predict. Then, if a goal is given, walk.

The machine: the AGC (Luminary 099) on its socket, with the vehicle plant (vehicle.py --pad) as a
second client; the plant also opens a control socket for the astronaut's direct controls. The loop
can press 33 things on the DSKY and 11 things on the controls. It is told nothing about any of them.

Signals, all on the machine's clock: the channel packets (latched, as in loop.py), the plant's
instrument rows (every 100 ms: angles, rates, altitude, speeds, thrust, jets, pulse counts,
propellant, armed, engine), and the computer's memory writes (recorded, not read here).

Each step:
  watch    the baseline: no action, until two windows in a row add no self-mover
  state    the latched channels that don't move by themselves, plus what is holding on the
           instruments right now: each field's level-1 word (this row minus the row before) and
           level-2 word (the difference of those), the one that occurred most in the window.
           Raw rows never repeat; their differences do. That is Discovery's levels, pointed at time.
  touch    least tried in this state (model phase), or what the walk asks for (goal phase)
  compare  the effect: for every instrument field, did its level-1 word go up, down, or hold
           between the window before the press and the window after. Kept per (state, action)
           and per action, as counts. The next state too (the map).
  predict  before pressing: the remembered effect for (state, action). After: the comparator on
           expected vs actual, per field. Misses are counted and kept.
  record   Discovery on the channel packets, the instrument rows, and the level-1 rows, each against
           its own memory across steps; the words table of the level-1 rows is where the constants live.

Givens: the sockets; the record formats; the 44 raw actions; the DSKY latch and the plant (hardware);
the dwell; the budgets; the goal (goal phase only), as a list of instrument-field constraints.

    python launch.py RUN_DIR model STEPS [speed] [dwell]
    python launch.py RUN_DIR goal  STEPS [speed] [dwell]     (loads RUN_DIR/memory.pkl and continues)
"""
import os, sys, time, socket, struct, pickle, subprocess, collections, signal
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import loop as L
import discovery as D

CTL_ACTIONS = [('ctl', c) for c in (0o300, 0o301, 0o302, 0o303, 0o304, 0o305, 0o306, 0o307, 0o310, 0o311, 0o312)]
ACTIONS = L.ACTIONS + CTL_ACTIONS
CH_LIMIT = 0                                          # per-step Discovery on the channel log is off here (the log is kept on disk; the pool re-sort is the size open end)
ROW = '>HhhhhhhHhhHBBHHHBB'                           # the plant's row (vehicle.py)
ROW_SIZE = struct.calcsize(ROW)
NFIELD = 17                                           # fields after t
GOAL = {6: ('>', 200), 3: ('abs<', 5000), 4: ('abs<', 5000), 5: ('abs<', 5000)}   # a given, goal phase only:
# field 6 = altitude over 200 m; fields 3,4,5 = turn rates under 0.5 deg/s (units: 1e-4 deg/s). The numbers
# name instrument fields by position, which is all the loop ever sees of them.


def packet(ch, v):
    return L.packet(ch, v)


class Instruments:
    """the plant's rows since the last step, and the holding level-1 / level-2 words"""
    def __init__(self):
        self.pos = 0
        self.last_row = None
        self.last_d1 = None
        self.last_win = tuple([0] * NFIELD)

    def read(self):
        size = os.path.getsize('vehicle.bin')
        with open('vehicle.bin', 'rb') as f:
            f.seek(self.pos); data = f.read(size - self.pos)
        n = len(data) // ROW_SIZE
        self.pos += n * ROW_SIZE
        rows = [struct.unpack(ROW, data[i * ROW_SIZE:(i + 1) * ROW_SIZE])[1:] for i in range(n)]
        first = self.last_row if self.last_row is not None else (rows[0] if rows else None)
        prev = self.last_row
        d1, d2 = [], []
        pd = self.last_d1
        for r in rows:
            if prev is not None:
                d = tuple((r[k] - prev[k]) for k in range(NFIELD))
                d1.append(d)
                if pd is not None:
                    d2.append(tuple(d[k] - pd[k] for k in range(NFIELD)))
                pd = d
            prev = r
        self.last_row = prev
        self.last_d1 = pd
        # what each field did over this window: end minus start (the comparator across the window)
        win = tuple((self.last_row[k] - first[k]) if (first is not None and self.last_row is not None) else 0 for k in range(NFIELD))
        nchange = tuple(sum(1 for d in d1 if d[k] != 0) for k in range(NFIELD))
        # moving: changed in more than one row of the window, which way. One row is a jump, not motion.
        h1 = tuple(sign(win[k]) if (win[k] != 0 and nchange[k] >= 2) else 0 for k in range(NFIELD))
        self.last_win = win
        return rows, d1, h1, win


def sign(x):
    return (x > 0) - (x < 0)


def main():
    run, phase = sys.argv[1], sys.argv[2]
    budget = int(sys.argv[3])
    speed = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    dwell = float(sys.argv[5]) if len(sys.argv) > 5 else 0.25
    os.makedirs(run, exist_ok=True); os.chdir(run)
    port = 19697 + (os.getpid() % 500) * 10
    ctl_port = port + 2000
    for f in ('core', 'writes.bin', 'channels.bin', 'vehicle.bin', 'vehicle.csv'):
        if os.path.exists(f):
            os.remove(f)
    env = dict(os.environ, AGC_SPEED=str(speed), AGC_TRACE_WRITES='writes.bin', AGC_TRACE_CHANNELS='channels.bin')
    agc = subprocess.Popen([os.path.join(HERE, 'virtualagc', 'yaAGC', 'yaAGC'), '--nodebug', '--no-resume', '--quiet',
                            f'--port={port}', os.path.join(HERE, 'virtualagc', 'Luminary099', 'MAIN.agc.bin')],
                           stdout=open('yaagc.out', 'w'), stderr=subprocess.STDOUT, env=env)
    time.sleep(1.5)
    veh = subprocess.Popen([sys.executable, os.path.join(HERE, 'vehicle.py'), '--port', str(port), '--ctl-port', str(ctl_port),
                            '--speed', str(speed), '--seconds', '1000000', '--pad', '1', '--out', '.'],
                           stdout=open('vehicle.out', 'w'), stderr=subprocess.STDOUT)
    time.sleep(1.5)
    sock = socket.create_connection(('127.0.0.1', port)); sock.setblocking(False)
    ctl = socket.create_connection(('127.0.0.1', ctl_port))
    log = open('launch.log', 'a')
    say = lambda s: (print(s, flush=True), log.write(s + '\n'), log.flush())

    hw = L.Hardware()
    ins = Instruments()
    ch = L.Signal('channels', 32); rows_sig = L.Signal('instr', 16); d1_sig = L.Signal('instr-d1', 16)
    tried = collections.Counter(); went = collections.Counter(); contexts = {}
    effects = collections.defaultdict(collections.Counter)      # (state, action) -> Counter of (field, sign)
    effects_any = collections.defaultdict(collections.Counter)  # action -> Counter of (field, sign)
    misses = collections.Counter()                              # (state, action, field) -> times expected != actual
    hits = collections.Counter()
    self_moving = set(); ever_moving = set()
    step0 = 0
    if os.path.exists('memory.pkl'):
        M = pickle.load(open('memory.pkl', 'rb'))
        for sig, key in ((ch, 'ch'), (rows_sig, 'rows'), (d1_sig, 'd1')):
            sig.__dict__.update(M[key])
        tried.update(M['tried']); went.update(M['went']); contexts.update(M['contexts'])
        for k, v in M['effects'].items(): effects[k].update(v)
        for k, v in M['effects_any'].items(): effects_any[k].update(v)
        misses.update(M['misses']); hits.update(M['hits']); self_moving = set(M['self_moving']); ever_moving = set(M.get('ever_moving', ())); step0 = M['step'] + 1
        say(f'{phase} phase: resumed memory at step {step0}: {len(went)} transitions, {len(effects_any)} actions with effects (a new life; the plant is back on the pad)')

    def read_channels():
        nonlocal pos_c
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

    pos_c = 0
    # ---- watch: the baseline, until two windows in a row add nothing
    quiet = 0; windows = 0
    time.sleep(1.0); read_channels(); ins.read()
    while quiet < 2 and windows < 60:
        time.sleep(dwell)
        _, moving = read_channels()
        rows, d1, h1, h2 = ins.read()
        before = len(self_moving)
        self_moving |= moving
        windows += 1
        quiet = quiet + 1 if len(self_moving) == before else 0
    say(f'baseline: {windows} windows; channels that move by themselves: ' + ' '.join(f'{c:03o}' for c in sorted(self_moving)))
    say(f'baseline: instruments holding at level 1: {h1}  level 2: {h2}')
    def make_state(row, h1, h2):
        # a field that has ever been seen moving is continuous: it contributes only its direction (or 'holding').
        # a field that has only ever jumped contributes its value. The machine learns which is which by seeing it move.
        for k in range(NFIELD):
            if h1[k] != 0:
                ever_moving.add(k)
        return hw.showing(self_moving) + tuple(('move', k, h1[k]) if k in ever_moving else ('hold', k, row[k]) for k in range(NFIELD))
    state = make_state(ins.last_row, h1, h2)
    contexts[hash(state) & 0xffff] = state
    t0 = time.time()
    for step in range(step0, step0 + budget):
        # ---- choose
        if phase == 'goal':
            # what the goal needs, from the last row
            row = ins.last_row
            need = {}
            for k, (op, val) in GOAL.items():
                if op == '>' and row[k] <= val: need[k] = +1
                if op == 'abs<' and abs(row[k]) >= val: need[k] = -sign(row[k]) or -1
            if not need:
                say(f'step {step:4d}  GOAL SATISFIED: row {row}')
                break
            # the walk: states in the map where every needed field was moving the needed way; backward through
            # the map to the state we are in; the first action on that path. If we are in such a state already,
            # the least-effect action (the record's no-op). If no path, an action whose own effect moved a needed
            # field the needed way. If none, explore.
            # a stored state read through what is known now: a field seen moving since then is direction-only
            norm = lambda c: tuple(('move', x[1], 0) if (x and x[0] == 'hold' and x[1] in ever_moving) else x for x in c)
            proj = lambda c: tuple(x for x in norm(c) if x and x[0] in ('move', 'hold'))   # the instrument part
            sa_total = collections.Counter()
            for (a0, act, b0), n in went.items():
                sa_total[(norm(a0), act)] += n
            psa_total = collections.Counter()
            for (a0, act, b0), n in went.items():
                psa_total[(proj(a0), act)] += n
            usual = lambda a0, act, n, tot: n >= 2 and n * 2 >= tot[(a0, act)]     # what usually follows
            targets = [norm(c) for c in contexts.values() if all(('move', k, sg) in c for k, sg in need.items())]
            action, why = None, ''
            nstate = norm(state)
            if nstate in targets:
                action, why = min(ACTIONS, key=lambda a: (sum(effects_any[a].values()) - effects_any[a][(0, 0)] * 0, tried[(state, a)])), 'hold'
                action = min(ACTIONS, key=lambda a: sum(n for (k, sg), n in effects_any[a].items() if sg != 0))
            elif targets:
                back = {}
                for strict in (True, False):                # the usual edges first; then any edge
                    back = {t: [] for t in targets}; frontier = list(targets); depth = 0
                    while frontier and depth < 12 and nstate not in back:
                        nxt = []
                        for b in frontier:
                            for (a0, act, b0), n in went.items():
                                na, nb = norm(a0), norm(b0)
                                if nb == b and na not in back and na != nb and (not strict or usual(na, act, n, sa_total)):
                                    back[na] = [act] + back[b]; nxt.append(na)
                        frontier = nxt; depth += 1
                    if nstate in back:
                        break
                if nstate in back and back[nstate]:
                    action, why = back[nstate][0], f'walk({len(back[nstate])} steps)'
                else:
                    # no exact match for this state: walk on the instrument part alone (the channels set aside)
                    ps = proj(state); ptargets = {proj(t) for t in targets}
                    pm = collections.Counter()
                    for (a0, act, b0), n in went.items():
                        pm[(proj(a0), act, proj(b0))] += n
                    for strict in (True, False):
                        back = {t: [] for t in ptargets}; frontier = list(ptargets); depth = 0
                        while frontier and depth < 12 and ps not in back:
                            nxt = []
                            for b in frontier:
                                for (pa, act, pb), n in pm.items():
                                    if pb == b and pa not in back and pa != pb and (not strict or usual(pa, act, n, psa_total)):
                                        back[pa] = [act] + back[b]; nxt.append(pa)
                            frontier = nxt; depth += 1
                        if ps in back:
                            break
                    if ps in back and back[ps]:
                        action, why = back[ps][0], f'walk*({len(back[ps])} steps)'
            if action is None:
                direct = [a for a in ACTIONS if any(effects_any[a][(k, sg)] > effects_any[a][(k, -sg)] for k, sg in need.items())]
                if direct:
                    action, why = max(direct, key=lambda a: sum(effects_any[a][(k, sg)] for k, sg in need.items())), 'direct'
            if action is None:
                action, why = min(ACTIONS, key=lambda a: (tried[(state, a)], ACTIONS.index(a))), 'explore'
        else:
            action = min(ACTIONS, key=lambda a: (tried[(state, a)], ACTIONS.index(a)))
            why = 'explore'
        tried[(state, action)] += 1
        # ---- predict
        expected = {}
        for (k, s), n in effects[(state, action)].items():
            if n > expected.get(k, (0, 0))[1]:
                expected[k] = (s, n)
        # ---- act
        h1_before = h1; row_before = ins.last_row
        if action[0] == 'ctl':
            ctl.sendall(packet(action[1], 0))
        else:
            L.send(sock, action)
        time.sleep(dwell)
        agc.send_signal(signal.SIGUSR1); time.sleep(0.02)
        try:
            while sock.recv(65536):
                pass
        except BlockingIOError:
            pass
        # ---- record
        cdata, moving = read_channels()
        rows, d1, h1, h2 = ins.read()
        self_moving |= moving
        rc = ch.read(cdata[:CH_LIMIT]) if CH_LIMIT else dict(new=0, words=0, confirmed=0)                    # size, not method: the first packets of the window
        rr = dict(new=0)                                   # the raw rows are on disk (vehicle.bin); the differences are read
        rd = d1_sig.read(b''.join(struct.pack('>' + 'h' * NFIELD, *[max(-32768, min(32767, x)) for x in d]) for d in d1)) if d1 else dict(new=0)
        agc.send_signal(signal.SIGUSR2)
        # ---- compare: the effect on every field, and the prediction
        before_state = state
        state = make_state(ins.last_row, h1, h2)
        contexts[hash(state) & 0xffff] = state
        went[(before_state, action, state)] += 1
        changed = []
        for k in range(NFIELD):
            # the effect on a field: its motion started, stopped or reversed (level 1), or, if it was holding
            # before and after, its value jumped (level 0). Motion already under way is the state's, not the action's.
            sw0, sw1 = sign(h1_before[k]), sign(h1[k])
            s = sign(sw1 - sw0)
            if s == 0 and sw0 == 0 and sw1 == 0:
                s = sign(ins.last_row[k] - row_before[k])
            effects[(before_state, action)][(k, s)] += 1
            effects_any[action][(k, s)] += 1
            if s:
                changed.append(f'f{k}{"+" if s > 0 else "-"}')
            if k in expected:
                if expected[k][0] == s:
                    hits[(before_state, action, k)] += 1
                else:
                    misses[(before_state, action, k)] += 1
        pred = '' if not expected else f"  predicted {len(expected)} fields, missed {sum(1 for k in expected if expected[k][0] != sign(h1[k] - h1_before[k]))}"
        say(f"step {step:4d}  st {hash(before_state) & 0xffff:04x}  {why:7s} {action[0]}{action[1]:>4o}  rows {len(rows):3d}  "
            f"new ch {rc['new']:4d} rows {rr['new']:4d} d1 {rd['new']:4d}  effect: {' '.join(changed) or '-'}{pred}  {time.time() - t0:5.0f}s")
        if step % 20 == 19 or step == step0 + budget - 1:
            pickle.dump(dict(ch=ch.__dict__, rows=rows_sig.__dict__, d1=d1_sig.__dict__, tried=dict(tried), went=dict(went),
                             contexts=contexts, effects={k: dict(v) for k, v in effects.items()},
                             effects_any={k: dict(v) for k, v in effects_any.items()}, misses=dict(misses), hits=dict(hits),
                             self_moving=self_moving, ever_moving=ever_moving, step=step), open('memory.pkl', 'wb'))
    sock.close(); ctl.close(); veh.terminate(); agc.terminate(); agc.wait()
    say(f"done: {len(went)} transitions, {len(contexts)} states, predictions right {sum(hits.values())} wrong {sum(misses.values())}")


if __name__ == '__main__':
    main()
