"""
vehicle.py -- a small lunar module on the other side of the socket (v2, 2026-10-10).

Owner: "lets fill the other side of the rocket."

The smallest vehicle that lets the flight program's control loop close: a rigid body with
sixteen reaction jets and one throttleable engine over a flat moon, an inertial platform that
reports its gimbal angles to the computer as CDU pulses and its sensed acceleration as PIPA
pulses, the cockpit switches that tell the computer the platform is on and the autopilot is in
AUTO, and a hand that presses DSKY keys on a schedule (one socket client does everything).

Its clock is the computer's own: the downlink heartbeat (channel 034, every 20 ms of machine
time) advances the vehicle two 10 ms steps, so vehicle time = machine time, and the key schedule
and the kick are in machine seconds. Keys go one at a time; the next waits for the display to
answer the last (or 1.5 s), so none are lost.

What it reads from the computer:
  channel 005, 006   jet bits (eight jets each)
  channel 011        bit 13 engine on, bit 14 engine off
  channel 012        bit 5 zero the IMU CDUs (on its rising edge the platform is taken to be where the body is);
                     bit 15 ISS turn-on delay complete (then the turn-on request is dropped, as the real switch does)
  channel 034        the downlink heartbeat = the clock
  counter 055        throttle pulses (015 up, 016 down)
What it sends:
  counters 032/033/034   CDU pulses for the OUTER, INNER, MIDDLE gimbal angles = body angles about X, Y, Z
                         (the flight program's own words: CDUX = PHI = OGA, CDUY = THETA = IGA, CDUZ = PSI = MGA)
  counters 037/040/041   PIPA pulses, 1 cm/s each, along the platform axes
  channels 030-033       switches (bits inverted: 0 = present); channel 015 keys; channel 032 bit 14 = PRO
What it writes: vehicle.csv (every 10th step) and vehicle.bin (same rows as fixed fields, 32 bytes:
  t ax ay az wx wy wz alt vx vz thrust jets5 jets6 cdu pipa prop armed engine).
--pad starts it at rest on the ground; --ctl-port N opens a socket for the astronaut's direct controls (CTL).

Quad geometry from the flight program's own tables (Q,R-AXES: +V = jets 1,10 = 1U+3D; +U = jets 5,14 = 2U+4D;
ROT-TOUV: U = Q+R, V = -Q+R): quad 1 at +45 degrees from +Y toward +Z, quads numbered clockwise looking down +X.

    python vehicle.py --speed 20 --seconds 450 --kick 340 --keys "100:V37E00E,110:V48E,114:P,116:V21E,118:33000E,122:P,128:V46E" --out runs/<stamp>
"""
import math, os, socket, struct, sys, time

MASS = 15000.0
INERTIA = (25000.0, 25000.0, 25000.0)
JET_F = 445.0
QUAD_R = 2.0
QUAD_OFFSET = 45.0
QUAD_STEP = -90.0
ENGINE_MIN = 4670.0
ENGINE_STEP = 12.5
ENGINE_MAX = 43900.0
G_MOON = 1.62
DRY = 10000.0                 # dry mass, kg; MASS below is the total at start
PROP0 = 5000.0                # propellant at start, kg
ISP = 311.0                   # engine exhaust: seconds (mass burns at thrust / (ISP * 9.81))
# the astronaut's own controls, direct, with the computer in the loop or not (a second socket, --ctl-port)
CTL = {0o300: 'arm', 0o301: 'engine on', 0o302: 'engine off', 0o303: 'throttle up', 0o304: 'throttle down',
       0o305: '+roll', 0o306: '-roll', 0o307: '+pitch', 0o310: '-pitch', 0o311: '+yaw', 0o312: '-yaw'}
CDU_PER_TURN = 32768
PIPA_MS = 0.01

CDUX, CDUY, CDUZ = 0o32, 0o33, 0o34
PIPAX, PIPAY, PIPAZ = 0o37, 0o40, 0o41
THRUST = 0o55
PORT = 19697
KEYS = {'0': 16, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'V': 17, 'N': 31, 'E': 28, 'C': 30, 'K': 25, 'R': 18, '+': 26, '-': 27}


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
    """gimbal angles (outer about X, inner about Y, middle about Z) from q = body -> platform, exactly:
    the body-to-platform matrix is taken as Rx(outer) * Rz(middle) * Ry(inner), which agrees with the
    small-angle reading (x, y, z) near zero and does not pollute one angle with the others' products."""
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
    def __init__(self):
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
        self.prop = PROP0
        self.armed = False
        self.manual_engine = False
        self.pulse_until = [0.0, 0.0, 0.0]      # direct-mode hand-controller pulse: jets about an axis until this time
        self.pulse_sign = [0, 0, 0]

    def on_pad(self):
        self.pos = [0.0, 0.0, 0.0]
        self.vel = [0.0, 0.0, 0.0]
        self.down = True

    def mass(self):
        return DRY + self.prop

    def body_to_inertial(self, v):
        v = qrot(self.q, v)
        return (-v[2], v[1], v[0])

    def step(self, dt):
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
        # direct-mode hand controller: a pulse fires two jets about one axis for a tenth of a second
        for ax_i in range(3):
            if self.t < self.pulse_until[ax_i]:
                T[ax_i] += self.pulse_sign[ax_i] * 2 * JET_F * QUAD_R
        thrust = 0.0
        engine = (self.engine or (self.manual_engine and self.armed)) and self.prop > 0
        if engine:
            thrust = max(ENGINE_MIN, min(ENGINE_MAX, ENGINE_MIN + self.throttle_pulses * ENGINE_STEP))
            F[0] += thrust
            self.prop = max(0.0, self.prop - dt * thrust / (ISP * 9.81))
        m = self.mass()
        Ix, Iy, Iz = INERTIA
        wx, wy, wz = self.w
        if not self.down:                          # on the ground the legs hold it; no rotation
            self.w[0] += dt * (T[0] - (Iz - Iy) * wy * wz) / Ix
            self.w[1] += dt * (T[1] - (Ix - Iz) * wz * wx) / Iy
            self.w[2] += dt * (T[2] - (Iy - Ix) * wx * wy) / Iz
            self.q = qnorm(qmul(self.q, (1.0, 0.5 * self.w[0] * dt, 0.5 * self.w[1] * dt, 0.5 * self.w[2] * dt)))
        a_body = (F[0] / m, F[1] / m, F[2] / m)
        if self.down and thrust > m * G_MOON:      # lift-off: thrust beats weight
            self.down = False
            print(f"  t={self.t:7.2f}s  lift-off: thrust {thrust:.0f} N, weight {m * G_MOON:.0f} N", flush=True)
        if not self.down:
            a_in = self.body_to_inertial(a_body)
            for i in range(3):
                self.vel[i] += dt * (a_in[i] - (G_MOON if i == 2 else 0.0))
                self.pos[i] += dt * self.vel[i]
            if self.pos[2] <= 0.0:
                self.down = True
                self.pos[2] = 0.0
                print(f"  t={self.t:7.2f}s  ground: speed {math.hypot(self.vel[0], self.vel[2]):.1f} m/s", flush=True)
                self.vel = [0.0, 0.0, 0.0]
                self.w = [0.0, 0.0, 0.0]
        rel = qmul(qconj(self.platform), self.q)
        a_plat = qrot(rel, a_body)
        for i in range(3):
            self.dv_acc[i] += a_plat[i] * dt
        self.t += dt
        return thrust

    def gimbals(self):
        return small_angles(qmul(qconj(self.platform), self.q))


def main():
    args = sys.argv[1:]
    opt = {'speed': '10', 'seconds': '120', 'kick': '0', 'out': '.', 'port': str(PORT), 'keys': '', 'ctl-port': '0', 'pad': '0'}
    i = 0
    while i < len(args):
        if args[i].startswith('--'):
            opt[args[i][2:]] = args[i + 1]
            i += 2
        else:
            i += 1
    speed, seconds, kick = float(opt['speed']), float(opt['seconds']), float(opt['kick'])
    out = opt['out']
    if 'inertia' in opt:                                  # --inertia N: the same moment about all three axes, kg m^2
        global INERTIA
        INERTIA = (float(opt['inertia']),) * 3
        print(f"  inertia {INERTIA[0]:.0f} kg m^2; one jet about a diagonal = {math.degrees(JET_F * QUAD_R / INERTIA[0]):.2f} deg/s^2", flush=True)
    schedule = []
    for item in [x for x in opt['keys'].split(',') if x.strip()]:
        t0, ks = item.split(':')
        for i_k, k in enumerate(ks.strip().upper()):
            schedule.append((float(t0) + 0.001 * i_k, k))      # keep the typed order (sorting on time alone scrambled it)
    schedule.sort()
    v = Vehicle()
    if opt['pad'] != '0':
        v.on_pad()
        print(f"  on the pad: mass {v.mass():.0f} kg, propellant {v.prop:.0f} kg, engine {ENGINE_MIN:.0f}..{ENGINE_MAX:.0f} N, weight {v.mass() * G_MOON:.0f} N", flush=True)
    ctl_srv = ctl = None
    if opt['ctl-port'] != '0':
        ctl_srv = socket.socket(); ctl_srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ctl_srv.bind(('127.0.0.1', int(opt['ctl-port']))); ctl_srv.listen(1); ctl_srv.setblocking(False)
    sock = socket.create_connection(('127.0.0.1', int(opt['port'])))
    sock.setblocking(False)
    csv = open(os.path.join(out, 'vehicle.csv'), 'w')
    csv.write('t,oga_deg,iga_deg,mga_deg,wx_dps,wy_dps,wz_dps,alt_m,vx,vz,thrust_N,jets5,jets6,cdu_sent,pipa_sent,prop_kg,armed,engine\n')
    binf = open(os.path.join(out, 'vehicle.bin'), 'wb')
    BIT = lambda b: 1 << (b - 1)
    ch30 = 0o77777 & ~BIT(9) & ~BIT(10) & ~BIT(15) & ~BIT(14) & ~BIT(5)
    ch31 = 0o77777 & ~BIT(14)
    ch32 = 0o77777
    for ch, val in ((0o30, ch30), (0o31, ch31), (0o32, ch32), (0o33, 0o77777)):
        sock.sendall(mask(ch, 0o77777))
        sock.sendall(packet(ch, val))
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
                if name == 'arm': v.armed = True
                elif name == 'engine on': v.manual_engine = True
                elif name == 'engine off': v.manual_engine = False
                elif name == 'throttle up': v.throttle_pulses += 400       # one notch = 5000 N
                elif name == 'throttle down': v.throttle_pulses -= 400
                elif name and name[1:] in ('roll', 'pitch', 'yaw'):
                    axis = ('roll', 'pitch', 'yaw').index(name[1:])
                    v.pulse_sign[axis] = 1 if name[0] == '+' else -1
                    v.pulse_until[axis] = v.t + 0.1
                if name:
                    print(f"  t={v.t:7.2f}s  manual: {name}", flush=True)
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
        if not heartbeat or time.time() - last_downlink_wall > 1e9:   # the heartbeat is the clock; no wall-clock fallback (the loop pauses the machine)
            due = int((time.time() - t_wall0) * speed / dt) - n
            if due > 0:
                steps_due = max(steps_due, min(due, 50))
        if steps_due <= 0:
            time.sleep(0.0005)
            continue
        steps_due -= 1
        n += 1
        if schedule and v.t >= schedule[0][0] and v.t >= key_wait_until and \
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
        if pro_down and v.t >= key_wait_until:
            sock.sendall(packet(0o32, ch32))
            pro_down = False
        if kick and not kicked and v.t >= kick:
            v.w[1] += math.radians(0.5)
            kicked = True
            print(f"  t={v.t:7.2f}s  kick: +0.5 deg/s about Y", flush=True)
        thrust = v.step(dt)
        ax, ay, az = v.gimbals()
        targets = [round(a / (2 * math.pi) * CDU_PER_TURN) for a in (ax, ay, az)]
        outbuf = bytearray()
        for ctr, idx in ((CDUX, 0), (CDUY, 1), (CDUZ, 2)):
            diff = max(-20, min(20, targets[idx] - v.sent[idx]))
            for _ in range(abs(diff)):
                # high-rate CDU pulses (kinds 021/023): the emulator paces low-rate pulses (1/3) at only ~170 per
                # second per gimbal and drops the rest when its queue fills, which lagged the computer's view of the
                # angle by seconds (flights 3-5); high rate is 6,500 per second, as a real gimbal moving fast sends
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
        if max(abs(x) for x in v.w) > math.radians(30):
            print(f"  t={v.t:7.2f}s  stop: tumbling, rates {[round(math.degrees(x), 2) for x in v.w]} deg/s", flush=True)
            break
        if n % 10 == 0:
            row = (v.t, math.degrees(ax), math.degrees(ay), math.degrees(az), math.degrees(v.w[0]), math.degrees(v.w[1]), math.degrees(v.w[2]),
                   v.pos[2], v.vel[0], v.vel[2], thrust, v.jets5, v.jets6, cdu_sent, pipa_sent, v.prop, int(v.armed), int(thrust > 0))
            csv.write(','.join(f"{x:.4f}" if isinstance(x, float) else str(x) for x in row) + '\n')
            s16 = lambda x, scale: max(-32767, min(32767, int(round(x * scale))))
            binf.write(struct.pack('>HhhhhhhHhhHBBHHHBB', int(v.t * 10) & 0xffff, s16(ax, 10000), s16(ay, 10000), s16(az, 10000),
                                   s16(v.w[0], 10000), s16(v.w[1], 10000), s16(v.w[2], 10000), int(v.pos[2]) & 0xffff,
                                   s16(v.vel[0], 10), s16(v.vel[2], 10), int(thrust / 10) & 0xffff, v.jets5, v.jets6,
                                   cdu_sent & 0xffff, pipa_sent & 0xffff, int(v.prop) & 0xffff, int(v.armed), int(thrust > 0)))
            binf.flush()
    csv.close()
    binf.close()
    sock.close()
    print(f"  vehicle done: {v.t:.1f} s on the computer's clock ({'heartbeat' if heartbeat else 'wall clock'}), "
          f"{cdu_sent} CDU pulses, {pipa_sent} PIPA pulses, final angles {math.degrees(ax):.2f} {math.degrees(ay):.2f} {math.degrees(az):.2f} deg, "
          f"rates {math.degrees(v.w[0]):.3f} {math.degrees(v.w[1]):.3f} {math.degrees(v.w[2]):.3f} deg/s, altitude {v.pos[2]:.0f} m", flush=True)


if __name__ == '__main__':
    main()
