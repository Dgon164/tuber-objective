"""
loop.py -- act, record, read, compare, choose. Nobody in the data path.

The machine is the AGC on its socket. The loop can press 33 things: the
32 key codes the DSKY channel accepts (channel 015, values 0..31, most
of them not real keys) and PRO (channel 032 bit 14). It is not told which
code is which key, which channel is the display, or what any of it does.

Each step:
  1. choose an action: in the current context (the last value seen on
     every channel -- the machine's visible state, as a tuple), the
     least-tried action; ties go to the lowest code
  2. send it, let the machine run for a moment
  3. read what the machine wrote in that moment: every channel packet
     (the action itself is in there, as the machine received it) and
     every memory write
  4. Discovery on both, against the memory from all earlier steps: what
     was confirmed, what is new
  5. keep everything: the pool, the follows (what came after what), the
     step log
until a full pass over the actions in the current context adds nothing
new, or the step budget runs out.

Givens, all of them: the socket; the record formats (32-bit packets,
80-bit write records); the list of 33 raw actions; the dwell time per
step; a byte limit per step on the write trace (size, not method); the
step budget; and the DSKY as hardware: its display channel (010) carries
eleven rows of latching relays, each packet replacing the word for the
row named in its top four bits -- so what is *showing* is the latched
rows, not the last packet. (The vehicle, when attached, is hardware the
same way.) Nothing about what any row means.

    python loop.py OUT_DIR [steps] [speed] [dwell_seconds]
"""
import os, sys, time, socket, struct, pickle, subprocess, collections, signal
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
import discovery as D

# ---- givens
ACTIONS = [('key', v) for v in range(32)] + [('pro', 1)]
WRITE_LIMIT = 100_000          # bytes of write trace read per step (10,000 writes)
CONTROL_CHANNELS = {0o15, 0o32, 0o432}       # the given controls: keys, PRO, and PRO's mask
DISPLAY_CHANNEL = 0o10                       # the DSKY: hardware with latching rows (a given)
NO_WRITES = '--no-writes' in sys.argv
RESUME = '--resume' in sys.argv


class Hardware:
    """what the machine is showing right now: the last value on every channel, with the DSKY's rows latched"""
    def __init__(self):
        self.state = {}
    def take(self, c, v):
        if c == DISPLAY_CHANNEL:
            self.state[(c, v >> 11)] = v            # one latch per row
        else:
            self.state[(c, 0)] = v
    def showing(self, skip):
        return tuple(sorted((k, v) for k, v in self.state.items() if k[0] not in skip))
PORT = 19697 + (os.getpid() % 1000)      # a port of our own, so a stray emulator can't take the keys


def packet(channel, value):
    return bytes([channel >> 3, 0x40 | ((channel << 3) & 0x38) | ((value >> 12) & 7),
                  0x80 | ((value >> 6) & 0x3f), 0xc0 | (value & 0x3f)])


def send(sock, action):
    kind, v = action
    if kind == 'key':
        sock.sendall(packet(0o15, v))
    else:                                               # PRO: a level on channel 032 bit 14, down then up
        sock.sendall(packet(0o432, 0o20000) + packet(0o32, 0))
        time.sleep(0.05)
        sock.sendall(packet(0o432, 0o20000) + packet(0o32, 0o20000))


def unpacket(b):
    return ((b[0] << 3) | ((b[1] >> 3) & 7), ((b[1] & 7) << 12) | ((b[2] & 0x3f) << 6) | (b[3] & 0x3f))


class Signal:
    """one signal's memory across steps: the pool (parts with counts), made-of, part-of, follows"""
    def __init__(self, name, frame):
        self.name, self.frame = name, frame
        self.pool, self.made_of, self.part_of = {}, collections.defaultdict(set), collections.defaultdict(set)
        self.follows = collections.Counter()
        self.run_follows = collections.Counter()
        self.word_counts = collections.Counter()

    def read(self, data):
        if len(data) < self.frame // 8 * 2:
            return dict(words=0, new=0, confirmed=0)
        bits = bin(int.from_bytes(data, 'big'))[2:].zfill(len(data) * 8)     # as read_signal() does
        words = D.cut_words(bits, self.frame)
        self.word_counts.update(words)
        levels, self.pool, self.made_of, self.part_of = D.run_levels(words, 1, 1000000, self.pool, self.made_of, self.part_of)
        L = levels[0]
        self.follows.update(L['follows'])
        self.run_follows.update(L['run_follows'])
        return dict(words=len(words), new=sum(len(l['new']) for l in levels),
                    confirmed=sum(len(l['confirmed']) for l in levels))


def main():
    out = sys.argv[1]
    args = [a for a in sys.argv[2:] if not a.startswith('--')]
    budget = int(args[0]) if len(args) > 0 else 200
    speed = int(args[1]) if len(args) > 1 else 20
    dwell = float(args[2]) if len(args) > 2 else 0.25
    os.makedirs(out, exist_ok=True)
    os.chdir(out)
    for f in (('writes.bin', 'channels.bin') if RESUME else ('core', 'writes.bin', 'channels.bin')):
        if os.path.exists(f):
            os.remove(f)
    env = dict(os.environ, AGC_SPEED=str(speed), AGC_TRACE_WRITES='writes.bin', AGC_TRACE_CHANNELS='channels.bin')
    agc = subprocess.Popen([os.path.join(HERE, 'virtualagc', 'yaAGC', 'yaAGC'), '--nodebug', '--quiet', '--dump-time=2'] + ([] if RESUME else ['--no-resume']) + [
                            f'--port={PORT}', os.path.join(HERE, 'virtualagc', 'Luminary099', 'MAIN.agc.bin')],
                           stdout=open('yaagc.out', 'w'), stderr=subprocess.STDOUT, env=env)
    time.sleep(1.5)
    if agc.poll() is not None:
        sys.exit('the emulator did not start; see yaagc.out')
    sock = socket.create_connection(('127.0.0.1', PORT))
    sock.setblocking(False)
    time.sleep(2.0)                                     # let the machine settle after power-up

    ch = Signal('channels', 32)
    wr = Signal('writes', 80)
    tried = collections.Counter()                       # (context, action) -> times
    step0 = 0
    went = collections.Counter()                        # (context, action, next context) -> times: the map of the machine
    contexts = {}                                       # context -> the tuple itself (the hash is just for printing)
    context = ()
    last_seen = {}
    log = open('loop.log', 'w')
    pos_w = pos_c = 0
    # baseline: press nothing for sixteen windows. A channel whose showing value differs between any two
    # windows moves by itself; it is not the machine answering an action, so it stays out of the context
    # (it stays in the record).
    hw = Hardware()
    windows = []
    for _ in range(16):
        p0 = os.path.getsize('channels.bin'); time.sleep(dwell)
        with open('channels.bin', 'rb') as f:
            f.seek(p0); base = f.read()
        for i in range(0, len(base) - 3, 4):
            c, v = unpacket(base[i:i + 4])
            if c not in CONTROL_CHANNELS:
                hw.take(c, v)
        windows.append(dict(hw.state))
    allk = set().union(*[set(w) for w in windows])
    self_moving = {k[0] for k in allk if len({w.get(k) for w in windows}) > 1}
    print('baseline: channels that move with nothing pressed:', ' '.join(f'{c:03o}' for c in sorted(self_moving)),
          '  steady:', ' '.join(f'{c:03o}' for c in sorted({k[0] for k in allk} - self_moving)))
    log.write('baseline self-moving channels: ' + ' '.join(f'{c:03o}' for c in sorted(self_moving)) + '\n')
    pos_c = os.path.getsize('channels.bin'); pos_w = os.path.getsize('writes.bin')
    stable_pass = collections.Counter()                 # context -> actions in a row that added nothing
    if RESUME and os.path.exists('memory.pkl'):
        M = pickle.load(open('memory.pkl', 'rb'))
        ch.__dict__.update(M['ch']); wr.__dict__.update(M['wr'])
        tried.update(M['tried']); went.update(M['went']); contexts.update(M['contexts'])
        step0 = M.get('step', 0) + 1
        hw.state.update(M.get('hw', {})); self_moving = set(M.get('self_moving', self_moving)); context = M.get('context', context)
        print(f'resumed at step {step0}: {len(went)} transitions, {len(contexts)} contexts')
    t0 = time.time()
    for step in range(step0, step0 + budget):
        # 1. choose
        cands = sorted(ACTIONS, key=lambda a: (tried[(context, a)], ACTIONS.index(a)))
        action = cands[0]
        tried[(context, action)] += 1
        # 2. act
        send(sock, action)
        time.sleep(dwell)
        agc.send_signal(signal.SIGUSR1)                 # pause the machine while we read
        time.sleep(0.02)
        try:
            while sock.recv(65536):
                pass
        except BlockingIOError:
            pass
        # 3. record: what the machine wrote in that moment
        size_c = os.path.getsize('channels.bin'); size_w = os.path.getsize('writes.bin')
        with open('channels.bin', 'rb') as f:
            f.seek(pos_c); cdata = f.read(size_c - pos_c)
        with open('writes.bin', 'rb') as f:
            f.seek(pos_w); wdata = f.read(min(size_w - pos_w, WRITE_LIMIT))
        pos_c, pos_w = size_c, size_w
        # 4. read and compare against memory
        rc = ch.read(cdata)
        rw = wr.read(wdata) if not NO_WRITES else dict(words=0, new=0, confirmed=0)
        agc.send_signal(signal.SIGUSR2)                 # resume
        # the new context: what each channel showed in this moment (the set of its values), as the
        # machine shows it, leaving out the channels that move by themselves
        # the action's effect lands in the first half of the window; a channel that keeps changing in the
        # second half is moving by itself right now (a flashing lamp) -- the baseline test, taken every step
        n4 = len(cdata) // 4
        mid = {}
        for i in range(n4):
            c, v = unpacket(cdata[4 * i:4 * i + 4])
            if c not in CONTROL_CHANNELS:               # what we sent is not what the machine showed
                hw.take(c, v)
            if i == n4 // 2:
                mid = dict(hw.state)
        moving_now = {k[0] for k in set(mid) | set(hw.state) if mid.get(k) != hw.state.get(k)}
        self_moving |= moving_now                       # once seen moving by itself, it is a self-mover: kept as a fact
        before = context
        context = hw.showing(self_moving)
        went[(before, action, context)] += 1
        contexts[hash(context) & 0xffff] = context
        # 5. keep: the log line
        added = rc['new'] + rw['new']
        key = hash(context) & 0xffff
        if added == 0:
            stable_pass[context] += 1
        else:
            stable_pass[context] = 0
        line = (f"step {step:4d}  ctx {key:04x}  act {action[0]}{action[1]:>3}  packets {rc['words']:5d} new {rc['new']:4d} conf {rc['confirmed']:4d}"
                f"  writes {rw['words']:6d} new {rw['new']:5d} conf {rw['confirmed']:5d}  pool ch {len(ch.pool):6d} wr {len(wr.pool):7d}  {time.time()-t0:6.0f}s")
        print(line, flush=True); log.write(line + '\n'); log.flush()
        if stable_pass[context] >= len(ACTIONS):
            msg = f"stable: {len(ACTIONS)} actions in a row added nothing in context {key:04x}"
            print(msg); log.write(msg + '\n')
            break
        if step % 25 == 24:
            pickle.dump(dict(ch=ch.__dict__, wr=wr.__dict__, tried=dict(tried), went=dict(went), contexts=contexts, self_moving=self_moving, step=step, hw=hw.state, context=context), open('memory.pkl', 'wb'))
    pickle.dump(dict(ch=ch.__dict__, wr=wr.__dict__, tried=dict(tried), went=dict(went), contexts=contexts, self_moving=self_moving, step=step, hw=hw.state, context=context), open('memory.pkl', 'wb'))
    sock.close(); agc.terminate(); agc.wait()          # the emulator writes its core file on the way out, for --resume
    log.close()
    print(f"done: channel pool {len(ch.pool)} parts, write pool {len(wr.pool)} parts, {len(tried)} (context, action) pairs tried")


if __name__ == '__main__':
    main()
