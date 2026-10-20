"""
vehicle.py -- the lunar module, version 3 (2026-10-20): a round moon, two stages, and a way to die.

Everything from phase-c's vehicle stays: the rigid body, sixteen jets, the inertial platform that
sends CDU and PIPA pulses to the flight computer, the cockpit switches, the DSKY key schedule, and the
astronaut's direct controls on a second socket. Three things are new.

1. A round moon. Gravity pulls toward the moon's center and gets weaker with height. In the
   vehicle's own frame (x downrange, z up) that is: vertical acceleration = thrust part - g(r) + vx^2/r,
   downrange acceleration = thrust part - vx*vz/r. At the right horizontal speed the vx^2/r term
   cancels gravity and the vehicle stays up: an orbit. Two instrument fields report the orbit the
   vehicle is on right now, as a real cockpit would: the lowest and highest points it will reach
   (periapsis and apoapsis altitude). A negative periapsis means the path hits the ground.

2. Two stages. A descent stage with a throttleable engine, and an ascent stage with a fixed-thrust
   engine, each with its own propellant. One more control, 'stage', drops the stage you are on. The
   engine goes off, the throttle resets, the mass drops. Neither stage alone has the speed for orbit.

3. Death. Hitting the ground faster than 10 m/s, or tumbling past 30 degrees per second, destroys the
   vehicle. So does running out of propellant in every stage while on a path into the ground or away
   from the moon: that vehicle is lost, and the model says so at once instead of waiting for the
   impact. For the next 30 seconds every instrument reads null. Then a new vehicle appears on the pad
   with full tanks. The clock keeps running. The nulls and the jump back to the pad are the only
   signal that something went wrong; nothing names the cause to the computer or to whoever presses.
   One more message on the control socket, ABORT, is not a control: it is mission control giving the
   vehicle up, and it kills it the same way.

Each throttle press moves the descent engine by 10 kN. Engine off puts the throttle back to minimum.
A hand-controller press fires the jets for 0.1 s, the same length every time, so a press one way and
a press the other way cancel exactly.

--pad starts it at rest on the ground. --ctl-port N opens the direct-control socket. --no-agc runs
it without the flight computer, on the wall clock, for testing the physics alone. --ctl "t:name,..."
is a schedule of direct controls by time, for a scripted flight.

    python vehicle.py --pad 1 --no-agc 1 --speed 200 --seconds 900 --ctl "60:arm,70:engine on,75:throttle up,..." --out runs/x
"""
import math, os, socket, struct, sys, time

R_MOON = 1737400.0            # m
GM_MOON = 4.9048695e12        # m^3/s^2
G_PAD = GM_MOON / R_MOON ** 2 # 1.62 at the surface
INERTIA = (25000.0, 25000.0, 25000.0)
JET_F = 445.0
QUAD_R = 2.0
QUAD_OFFSET = 45.0
QUAD_STEP = -90.0
ISP = 311.0
STAGES = [
    dict(name='descent', dry=2100.0, prop=5000.0, fmin=4670.0, fmax=43900.0, step=12.5),
    dict(name='ascent', dry=2150.0, prop=1200.0, fmin=15600.0, fmax=15600.0, step=0.0),
]
CRASH_SPEED = 10.0            # m/s at ground contact
TUMBLE = math.radians(30)     # rad/s
PULSE_STEPS = 10              # a hand-controller pulse: 10 physics steps of 0.01 s
NULL_SECONDS = 30.0           # how long the instruments read null after a death (vehicle seconds)
# the astronaut's own controls, direct, with the computer in the loop or not (a second socket, --ctl-port)
CTL = {0o300: 'arm', 0o301: 'engine on', 0o302: 'engine off', 0o303: 'throttle up', 0o304: 'throttle down',
       0o305: '+roll', 0o306: '-roll', 0o307: '+pitch', 0o310: '-pitch', 0o311: '+yaw', 0o312: '-yaw',
       0o313: 'stage'}
ABORT = 0o377                  # not a control: mission control ending the attempt; the vehicle is lost
CDU_PER_TURN = 32768
PIPA_MS = 0.01

CDUX, CDUY, CDUZ = 0o32, 0o33, 0o34
PIPAX, PIPAY, PIPAZ = 0o37, 0o40, 0o41
THRUST = 0o55
PORT = 19697
KEYS = {'0': 16, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'V': 17, 'N': 31, 'E': 28, 'C': 30, 'K': 25, 'R': 18, '+': 26, '-': 27}

# the instrument row, as written to vehicle.bin: t, then 20 fields
#  0 oga 1 iga 2 mga (deg*100)  3 wx 4 wy 5 wz (deg/s*100)  6 alt (10 m)  7 vx 8 vz (0.1 m/s)
#  9 thrust (10 N)  10 jets5 11 jets6  12 cdu 13 pipa (counts)  14 prop (kg, this stage)
#  15 armed 16 engine 17 stage  18 peri 19 apo (100 m, clamped)
ROW = '>HhhhhhhHhhHBBHHHBBBhh'
CSV_HEADER = 't,oga_deg,iga_deg,mga_deg,wx_dps,wy_dps,wz_dps,alt_m,vx,vz,thrust_N,jets5,jets6,cdu_sent,pipa_sent,prop_kg,armed,engine,stage,peri_m,apo_m'
NULL_ROW = (0xffff, -32768, -32768, -32768, -32768, -32768, -32768, 0xffff, -32768, -32768, 0xffff, 255, 255,
            0xffff, 0xffff, 0xffff, 255, 255, 255, -32768, -32768)


def packet(channel, value):
    return bytes([channel >> 3, 0x40 | ((channel << 3) & 0x38) | ((value >> 12) & 7),
                  0x80 | ((value >> 6) & 0x3f), 0xc0 | (value & 0x3f)])


def unpacket(b):
    return (b[0] << 3) | ((b[1] >> 3) & 7), ((b[1] & 7) << 12) | ((b[2] & 0x3f) << 6) | (b[3] & 0x3f)


def pulse(counter, kind):          # 0 PINC, 1 PCDU, 2 MINC, 3 MCDU
    return packet(0x80 | counter, kind)


def mask(channel, bits):
    return packet(0o400 | channel, bits)


CH5_JETS = [1, 2, 5, 6, 9, 10, 13, 14]
CH6_JETS = [3, 4, 7, 8, 11, 12, 15, 16]
PLUS_P = {4, 7, 12, 15}


def jet_force(j):
    quad = (j - 1) // 4
    phi = math.radians(QUAD_OFFSET + QUAD_STEP * quad)
    pos = (0.0, QUAD_R * math.cos(phi), QUAD_R * math.sin(phi))
    k = (j - 1) % 4
    if k == 0:
        f = (-JET_F, 0.0, 0.0)
    elif k == 1:
        f = (JET_F, 0.0, 0.0)
    else:
        t = (0.0, -math.sin(phi), math.cos(phi))
        s = JET_F if j in PLUS_P else -JET_F
        f = (0.0, s * t[1], s * t[2])
    return pos, f


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def qmul(a, b):
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b
    return (w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2, w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2, w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2)


def qnorm(q):
    n = math.sqrt(sum(c * c for c in q))
    return tuple(c / n for c in q)


def qrot(q, v):
    w, x, y, z = q
    r = qmul(qmul(q, (0.0, v[0], v[1], v[2])), (w, -x, -y, -z))
    return (r[1], r[2], r[3])


def qconj(q):
    return (q[0], -q[1], -q[2], -q[3])


def small_angles(q):
    w, x, y, z = q
    m00 = 1 - 2 * (y * y + z * z)
    m01 = 2 * (x * y - w * z)
    m02 = 2 * (x * z + w * y)
    m11 = 1 - 2 * (x * x + z * z)
    m21 = 2 * (y * z + w * x)
    middle = math.asin(max(-1.0, min(1.0, -m01)))
    outer = math.atan2(m21, m11)
    inner = math.atan2(m02, m00)
    return (outer, inner, middle)


class Vehicle:
    def __init__(self, pad=False):
        self.q = (1.0, 0.0, 0.0, 0.0)
        self.w = [0.0, 0.0, 0.0]
        self.pos = [0.0, 0.0, 15000.0]
        self.vel = [1690.0, 0.0, 0.0]
        self.engine = False
        self.throttle_pulses = 0
        self.jets5 = 0
        self.jets6 = 0
        self.platform = (1.0, 0.0, 0.0, 0.0)
        self.sent = [0, 0, 0]
        self.dv_acc = [0.0, 0.0, 0.0]
        self.t = 0.0
        self.down = False
        self.stage = 0
        self.prop = [s['prop'] for s in STAGES]
        self.armed = False
        self.manual_engine = False
        self.pulse_left = [0, 0, 0]          # physics steps left in a hand-controller pulse, per axis
        self.pulse_sign = [0, 0, 0]
        self.dead_until = 0.0            # while t < dead_until the instruments read null
        self.cause = ''
        if pad:
            self.on_pad()

    def on_pad(self):
        self.pos = [0.0, 0.0, 0.0]
        self.vel = [0.0, 0.0, 0.0]
        self.down = True

    def mass(self):
        return sum(STAGES[i]['dry'] + self.prop[i] for i in range(self.stage, len(STAGES)))

    def body_to_inertial(self, v):
        v = qrot(self.q, v)
        return (-v[2], v[1], v[0])

    def orbit(self):
        """the lowest and highest altitude the current path reaches, in metres (None, None if escaping)"""
        r = R_MOON + self.pos[2]
        vx, vz = self.vel[0], self.vel[2]
        eps = 0.5 * (vx * vx + vz * vz) - GM_MOON / r
        if eps >= 0:
            return None, None
        h = r * vx
        a = -GM_MOON / (2 * eps)
        e2 = 1 + 2 * eps * h * h / (GM_MOON * GM_MOON)
        e = math.sqrt(max(0.0, e2))
        return a * (1 - e) - R_MOON, a * (1 + e) - R_MOON

    def die(self, cause):
        self.cause = cause
        self.dead_until = self.t + NULL_SECONDS
        print(f"  t={self.t:7.2f}s  DEAD: {cause}", flush=True)

    def reborn(self):
        """a new vehicle on the pad, full tanks; the clock and the platform zeroing carry on"""
        t, sent = self.t, self.sent
        self.__init__(pad=True)
        self.t = t
        self.platform = (1.0, 0.0, 0.0, 0.0)
        print(f"  t={self.t:7.2f}s  reset: on the pad, stage 1, {sum(self.prop):.0f} kg propellant", flush=True)

    def do_stage(self):
        if self.stage + 1 < len(STAGES):
            self.stage += 1
            self.engine = False
            self.manual_engine = False
            self.throttle_pulses = 0
            print(f"  t={self.t:7.2f}s  staged: now on the {STAGES[self.stage]['name']} stage, mass {self.mass():.0f} kg", flush=True)

    def step(self, dt):
        if self.t < self.dead_until:
            self.t += dt
            if self.t >= self.dead_until:
                self.reborn()
            return 0.0
        st = STAGES[self.stage]
        F = [0.0, 0.0, 0.0]
        T = [0.0, 0.0, 0.0]
        for bits, jets in ((self.jets5, CH5_JETS), (self.jets6, CH6_JETS)):
            for i, j in enumerate(jets):
                if bits >> i & 1:
                    pos, f = jet_force(j)
                    tq = cross(pos, f)
                    for a in range(3):
                        F[a] += f[a]
                        T[a] += tq[a]
        for ax_i in range(3):
            if self.pulse_left[ax_i] > 0:
                T[ax_i] += self.pulse_sign[ax_i] * 2 * JET_F * QUAD_R
                self.pulse_left[ax_i] -= 1
        thrust = 0.0
        engine = (self.engine or (self.manual_engine and self.armed)) and self.prop[self.stage] > 0
        if engine:
            thrust = max(st['fmin'], min(st['fmax'], st['fmin'] + self.throttle_pulses * st['step']))
            F[0] += thrust
            self.prop[self.stage] = max(0.0, self.prop[self.stage] - dt * thrust / (ISP * 9.81))
        m = self.mass()
        Ix, Iy, Iz = INERTIA
        wx, wy, wz = self.w
        if not self.down:
            self.w[0] += dt * (T[0] - (Iz - Iy) * wy * wz) / Ix
            self.w[1] += dt * (T[1] - (Ix - Iz) * wz * wx) / Iy
            self.w[2] += dt * (T[2] - (Iy - Ix) * wx * wy) / Iz
            self.q = qnorm(qmul(self.q, (1.0, 0.5 * self.w[0] * dt, 0.5 * self.w[1] * dt, 0.5 * self.w[2] * dt)))
        a_body = (F[0] / m, F[1] / m, F[2] / m)
        r = R_MOON + self.pos[2]
        g = GM_MOON / (r * r)
        if self.down and thrust > m * g:
            self.down = False
            print(f"  t={self.t:7.2f}s  lift-off: thrust {thrust:.0f} N, weight {m * g:.0f} N", flush=True)
        if not self.down:
            a_in = self.body_to_inertial(a_body)
            vx, vz = self.vel[0], self.vel[2]
            self.vel[0] += dt * (a_in[0] - vx * vz / r)
            self.vel[1] += dt * a_in[1]
            self.vel[2] += dt * (a_in[2] - g + vx * vx / r)
            self.pos[0] += dt * self.vel[0]
            self.pos[2] += dt * self.vel[2]
            if self.pos[2] <= 0.0:
                speed = math.hypot(self.vel[0], self.vel[2])
                self.pos[2] = 0.0
                if speed > CRASH_SPEED:
                    self.die(f'crashed at {speed:.0f} m/s')
                    return 0.0
                self.down = True
                print(f"  t={self.t:7.2f}s  ground: speed {speed:.1f} m/s", flush=True)
                self.vel = [0.0, 0.0, 0.0]
                self.w = [0.0, 0.0, 0.0]
        if max(abs(x) for x in self.w) > TUMBLE:
            self.die(f'tumbling, rates {[round(math.degrees(x), 1) for x in self.w]} deg/s')
            return 0.0
        if not self.down and sum(self.prop[self.stage:]) <= 0.0:
            # no propellant left in this stage or any later one: the path it is on now is the path it keeps
            peri, _ = self.orbit()
            if peri is None:
                self.die('lost: no propellant left, leaving the moon')
                return 0.0
            if peri < 0.0:
                self.die(f'lost: no propellant left, on a path into the ground (lowest point {peri / 1000:.0f} km)')
                return 0.0
        rel = qmul(qconj(self.platform), self.q)
        a_plat = qrot(rel, a_body)
        for i in range(3):
            self.dv_acc[i] += a_plat[i] * dt
        self.t += dt
        return thrust

    def pulse(self, axis, sgn):
        """one hand-controller pulse: the jets fire for PULSE_STEPS physics steps, the same length every time"""
        self.pulse_sign[axis] = sgn
        self.pulse_left[axis] = PULSE_STEPS

    def gimbals(self):
        return small_angles(qmul(qconj(self.platform), self.q))

    def dead(self):
        return self.t < self.dead_until


def main():
    args = sys.argv[1:]
    opt = {'speed': '10', 'seconds': '120', 'kick': '0', 'out': '.', 'port': str(PORT), 'keys': '', 'ctl-port': '0',
           'pad': '0', 'no-agc': '0', 'ctl': ''}
    i = 0
    while i < len(args):
        if args[i].startswith('--'):
            opt[args[i][2:]] = args[i + 1]
            i += 2
        else:
            i += 1
    speed, seconds, kick = float(opt['speed']), float(opt['seconds']), float(opt['kick'])
    out = opt['out']
    no_agc = opt['no-agc'] != '0'
    schedule = []
    for item in [x for x in opt['keys'].split(',') if x.strip()]:
        t0, ks = item.split(':')
        for i_k, k in enumerate(ks.strip().upper()):
            schedule.append((float(t0) + 0.001 * i_k, k))
    schedule.sort()
    ctl_schedule = []
    for item in [x for x in opt['ctl'].split(',') if x.strip()]:
        t0, name = item.split(':', 1)
        ctl_schedule.append((float(t0), name.strip()))
    ctl_schedule.sort()
    v = Vehicle(pad=opt['pad'] != '0')
    if v.down:
        print(f"  on the pad: mass {v.mass():.0f} kg, propellant {sum(v.prop):.0f} kg in {len(STAGES)} stages, "
              f"engine {STAGES[0]['fmin']:.0f}..{STAGES[0]['fmax']:.0f} N, weight {v.mass() * G_PAD:.0f} N", flush=True)
    ctl_srv = ctl = None
    if opt['ctl-port'] != '0':
        ctl_srv = socket.socket(); ctl_srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ctl_srv.bind(('127.0.0.1', int(opt['ctl-port']))); ctl_srv.listen(1); ctl_srv.setblocking(False)
    sock = None
    BIT = lambda b: 1 << (b - 1)
    ch30 = 0o77777 & ~BIT(9) & ~BIT(10) & ~BIT(15) & ~BIT(14) & ~BIT(5)
    ch31 = 0o77777 & ~BIT(14)
    ch32 = 0o77777
    if not no_agc:
        sock = socket.create_connection(('127.0.0.1', int(opt['port'])))
        sock.setblocking(False)
        for ch, val in ((0o30, ch30), (0o31, ch31), (0o32, ch32), (0o33, 0o77777)):
            sock.sendall(mask(ch, 0o77777))
            sock.sendall(packet(ch, val))
    os.makedirs(out, exist_ok=True)
    csv = open(os.path.join(out, 'vehicle.csv'), 'w')
    csv.write(CSV_HEADER + '\n')
    binf = open(os.path.join(out, 'vehicle.bin'), 'wb')
    dt = 0.01
    cdu_sent = pipa_sent = 0
    pending = bytearray()
    kicked = turnon_seen = False
    zero_was = False
    pro_down = False
    display_seen = 0
    key_wait_until = 0.0
    key_display_mark = 0
    n = 0
    t_wall0 = time.time()
    last_downlink_wall = time.time()
    steps_due = 0
    heartbeat = False
    ax = ay = az = 0.0
    deaths = 0

    def do_control(name):
        if name == 'arm': v.armed = True
        elif name == 'engine on': v.manual_engine = True
        elif name == 'engine off': v.manual_engine = False; v.throttle_pulses = 0    # the throttle goes back to minimum
        elif name == 'throttle up': v.throttle_pulses = min(3200, v.throttle_pulses + 800)
        elif name == 'throttle down': v.throttle_pulses = max(0, v.throttle_pulses - 800)
        elif name == 'stage': v.do_stage()
        elif name and name[1:] in ('roll', 'pitch', 'yaw'):
            axis = ('roll', 'pitch', 'yaw').index(name[1:])
            v.pulse(axis, 1 if name[0] == '+' else -1)
        print(f"  t={v.t:7.2f}s  manual: {name}", flush=True)

    while v.t < seconds:
        if ctl_srv is not None and ctl is None:
            try:
                ctl, _ = ctl_srv.accept(); ctl.setblocking(False)
            except BlockingIOError:
                pass
        if ctl is not None:
            try:
                cdata = ctl.recv(4096)
            except BlockingIOError:
                cdata = b''
            for k in range(0, len(cdata) - 3, 4):
                ch, val = unpacket(cdata[k:k + 4])
                name = CTL.get(ch)
                if name and not v.dead():
                    do_control(name)
                elif ch == ABORT and not v.dead():
                    v.die('aborted: mission control called the attempt off')
        while ctl_schedule and v.t >= ctl_schedule[0][0]:
            _, name = ctl_schedule.pop(0)
            if not v.dead():
                do_control(name)
        data = b''
        if sock is not None:
            try:
                data = sock.recv(65536)
            except BlockingIOError:
                data = b''
        for k in range(0, len(data) - 3, 4):
            ch, val = unpacket(data[k:k + 4])
            if ch == 0o34:
                steps_due += 2
                heartbeat = True
                last_downlink_wall = time.time()
            elif ch == 0o10:
                display_seen += 1
            elif ch == 0o5:
                v.jets5 = val & 0xff
            elif ch == 0o6:
                v.jets6 = val & 0xff
            elif ch == 0o11:
                if val & BIT(13):
                    v.engine = True
                if val & BIT(14):
                    v.engine = False
            elif ch == 0o12:
                zero_now = bool(val & BIT(5))
                if zero_now and not zero_was:
                    v.platform = v.q
                    v.sent = [0, 0, 0]
                    print(f"  t={v.t:7.2f}s  computer zeroes the IMU CDUs: platform taken as the body's frame now", flush=True)
                zero_was = zero_now
                if val & BIT(15) and not turnon_seen:
                    turnon_seen = True
                    ch30 |= BIT(14)
                    sock.sendall(packet(0o30, ch30))
                    print(f"  t={v.t:7.2f}s  computer says: ISS turn-on delay complete; request dropped", flush=True)
            elif ch == (0x80 | THRUST):
                if val == 0o15:
                    v.throttle_pulses += 1
                elif val == 0o16:
                    v.throttle_pulses -= 1
        if not heartbeat:
            due = int((time.time() - t_wall0) * speed / dt) - n
            if due > 0:
                steps_due = max(steps_due, min(due, 500))
        if steps_due <= 0:
            time.sleep(0.0005)
            continue
        steps_due -= 1
        n += 1
        if sock is not None and schedule and v.t >= schedule[0][0] and v.t >= key_wait_until and \
                (display_seen > key_display_mark or key_wait_until == 0.0 or v.t - key_wait_until > 1.5):
            _, key = schedule.pop(0)
            key_display_mark = display_seen
            if key == 'P':
                sock.sendall(packet(0o32, ch32 & ~BIT(14)))
                pro_down = True
                key_wait_until = v.t + 0.5
            elif key in KEYS:
                sock.sendall(packet(0o15, KEYS[key]))
                key_wait_until = v.t + 0.3
            print(f"  t={v.t:7.2f}s  key {key}", flush=True)
        if sock is not None and pro_down and v.t >= key_wait_until:
            sock.sendall(packet(0o32, ch32))
            pro_down = False
        if kick and not kicked and v.t >= kick:
            v.w[1] += math.radians(0.5)
            kicked = True
            print(f"  t={v.t:7.2f}s  kick: +0.5 deg/s about Y", flush=True)
        was_dead = v.dead()
        thrust = v.step(dt)
        if v.dead() and not was_dead:
            deaths += 1
        dead = v.dead()
        if not dead:
            ax, ay, az = v.gimbals()
            if sock is not None:
                targets = [round(a / (2 * math.pi) * CDU_PER_TURN) for a in (ax, ay, az)]
                outbuf = bytearray()
                for ctr, idx in ((CDUX, 0), (CDUY, 1), (CDUZ, 2)):
                    diff = max(-20, min(20, targets[idx] - v.sent[idx]))
                    for _ in range(abs(diff)):
                        outbuf += pulse(ctr, 0o21 if diff > 0 else 0o23)
                    v.sent[idx] += diff
                    cdu_sent += abs(diff)
                for ctr, idx in ((PIPAX, 0), (PIPAY, 1), (PIPAZ, 2)):
                    while abs(v.dv_acc[idx]) >= PIPA_MS:
                        sgn = 1 if v.dv_acc[idx] > 0 else -1
                        outbuf += pulse(ctr, 0 if sgn > 0 else 2)
                        v.dv_acc[idx] -= sgn * PIPA_MS
                        pipa_sent += 1
                pending += outbuf
                if pending:
                    try:
                        sent_n = sock.send(pending)
                        del pending[:sent_n]
                    except BlockingIOError:
                        pass
                    if len(pending) > 200000:
                        print(f"  t={v.t:7.2f}s  stop: the computer is not taking packets ({len(pending)} bytes waiting)", flush=True)
                        break
        if n % 10 == 0:
            if dead:
                csv.write(f"{v.t:.4f}," + ','.join(['nan'] * 20) + '\n')
                binf.write(struct.pack(ROW, *NULL_ROW))
            else:
                peri, apo = v.orbit()
                p100 = lambda x: 32767 if x is None else max(-32767, min(32767, int(x / 100)))
                row = (v.t, math.degrees(ax), math.degrees(ay), math.degrees(az), math.degrees(v.w[0]), math.degrees(v.w[1]), math.degrees(v.w[2]),
                       v.pos[2], v.vel[0], v.vel[2], thrust, v.jets5, v.jets6, cdu_sent, pipa_sent, v.prop[v.stage], int(v.armed), int(thrust > 0),
                       v.stage, -1e9 if peri is None else peri, -1e9 if apo is None else apo)
                csv.write(','.join(f"{x:.4f}" if isinstance(x, float) else str(x) for x in row) + '\n')
                s16 = lambda x, scale: max(-32767, min(32767, int(round(x * scale))))
                binf.write(struct.pack(ROW, int(v.t * 10) & 0xffff, s16(math.degrees(ax), 100), s16(math.degrees(ay), 100), s16(math.degrees(az), 100),
                                       s16(math.degrees(v.w[0]), 100), s16(math.degrees(v.w[1]), 100), s16(math.degrees(v.w[2]), 100), int(v.pos[2] / 10) & 0xffff,
                                       s16(v.vel[0], 10), s16(v.vel[2], 10), int(thrust / 10) & 0xffff, v.jets5, v.jets6,
                                       cdu_sent & 0xffff, pipa_sent & 0xffff, int(v.prop[v.stage]) & 0xffff, int(v.armed), int(thrust > 0),
                                       v.stage, p100(peri), p100(apo)))
            binf.flush()
            csv.flush()
    csv.close()
    binf.close()
    if sock is not None:
        sock.close()
    peri, apo = v.orbit()
    print(f"  vehicle done: {v.t:.1f} s, {deaths} deaths, stage {v.stage + 1}, altitude {v.pos[2]:.0f} m, vx {v.vel[0]:.0f} vz {v.vel[2]:.0f} m/s, "
          f"periapsis {'escape' if peri is None else f'{peri / 1000:.1f} km'}, apoapsis {'escape' if apo is None else f'{apo / 1000:.1f} km'}, "
          f"propellant {v.prop[0]:.0f} + {v.prop[1]:.0f} kg", flush=True)


if __name__ == '__main__':
    main()
