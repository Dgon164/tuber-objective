"""
scripted.py -- step the vehicle directly, no sockets, with a hand-written pilot, to show that orbit is
reachable and what it takes. Not the learner. A check on the physics and a yardstick for the learner.

    python scripted.py [pitch_start pitch_pulses pitch_stop_deg cut_peri_km]
"""
import sys, math
import vehicle as V

def fly(pitch_start=15.0, pitch_pulses=1, pitch_stop_deg=80.0, cut_peri_km=12.0, max_t=1500.0, quiet=False):
    v = V.Vehicle(pad=True)
    dt = 0.01
    def ctl(name):
        if name == 'arm': v.armed = True
        elif name == 'engine on': v.manual_engine = True
        elif name == 'engine off': v.manual_engine = False
        elif name == 'throttle up': v.throttle_pulses = min(3200, v.throttle_pulses + 800)
        elif name == 'stage': v.do_stage()
        elif name in ('+pitch', '-pitch'):
            v.pulse(1, 1 if name[0] == '+' else -1)
    plan = [(0.5, 'arm'), (1.0, 'engine on')] + [(2.0 + 0.5 * i, 'throttle up') for i in range(4)]
    liftoff_t = None; pitched = 0; stopped = False; staged = False; cut = False; log = []
    while v.t < max_t and not v.dead():
        while plan and v.t >= plan[0][0]:
            ctl(plan.pop(0)[1])
        if liftoff_t is None and not v.down:
            liftoff_t = v.t
        if liftoff_t is not None:
            el = v.t - liftoff_t
            if el >= pitch_start and pitched < pitch_pulses and v.pulse_left[1] == 0:
                ctl('+pitch'); pitched += 1
            pitch_deg = abs(math.degrees(v.gimbals()[1]))
            if pitched >= pitch_pulses and not stopped and pitch_deg >= pitch_stop_deg:
                for _ in range(pitch_pulses):
                    ctl('-pitch'); v.step(dt)          # cancel the rotation
                stopped = True
            if v.stage == 0 and v.prop[0] <= 0.0 and not staged:
                ctl('stage'); ctl('engine on'); staged = True
            peri, apo = v.orbit()
            if staged and not cut and peri is not None and peri > cut_peri_km * 1000:
                ctl('engine off'); cut = True
                if not quiet:
                    print(f"  cut at t={v.t:.0f}s alt {v.pos[2]/1000:.1f} km vx {v.vel[0]:.0f} vz {v.vel[2]:.0f} peri {peri/1000:.1f} apo {apo/1000:.1f} km, prop left {v.prop[1]:.0f} kg")
            if cut and v.t - liftoff_t > el + 1:
                pass
        v.step(dt)
        if cut and (v.t % 100) < dt:
            pass
        if int(v.t) % 60 == 0 and abs(v.t - round(v.t)) < dt / 2 and not quiet:
            peri, apo = v.orbit()
            print(f"  t={v.t:5.0f} alt {v.pos[2]/1000:6.1f} km  vx {v.vel[0]:6.0f} vz {v.vel[2]:5.0f}  pitch {abs(math.degrees(v.gimbals()[1])):5.1f}  stage {v.stage+1} prop {v.prop[v.stage]:5.0f}  peri {'esc' if peri is None else f'{peri/1000:6.1f}'} apo {'esc' if apo is None else f'{apo/1000:6.1f}'}")
        if cut and v.t - liftoff_t > 0 and v.t > (liftoff_t + 1200):
            break
    peri, apo = v.orbit()
    ok = (not v.dead()) and cut and peri is not None and peri > 10000 and v.pos[2] > 10000
    return dict(ok=ok, dead=v.cause, t=v.t, alt=v.pos[2], vx=v.vel[0], vz=v.vel[2], peri=peri, apo=apo, staged=staged, cut=cut, prop2=v.prop[1])

if __name__ == '__main__':
    a = [float(x) for x in sys.argv[1:]]
    if a:
        r = fly(*a)
        print(r)
    else:
        print("sweep: pitch_start, pulses, stop_deg -> outcome")
        for ps in (10, 20, 40):
            for pulses in (1, 2):
                for stop in (60, 75, 88):
                    r = fly(ps, pulses, stop, quiet=True)
                    print(f"  start {ps:3.0f}s  pulses {pulses}  stop {stop:2.0f}deg  ->  {'ORBIT' if r['ok'] else 'no   '}  "
                          f"dead={r['dead'] or '-':28s} alt {r['alt']/1000:7.1f} km  peri {('esc' if r['peri'] is None else f'{r['peri']/1000:7.1f}')} km  "
                          f"apo {('esc' if r['apo'] is None else f'{r['apo']/1000:7.1f}')} km  staged={r['staged']} cut={r['cut']} prop2 {r['prop2']:.0f}")
