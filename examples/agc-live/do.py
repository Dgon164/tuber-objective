"""
do.py -- the walk's answer, carried out on a fresh machine, and checked.

    python do.py RUN_DIR GOAL

Starts the AGC fresh, waits for the display to settle, presses what walk.py
says to press for GOAL, reads what the DSKY is showing (the same hardware
latch the loop uses), and compares it with the goal: same or different.
That is the whole check. No score.
"""
import os, sys, time, socket, subprocess, signal
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import loop as L
import walk as W

run, goal = sys.argv[1], sys.argv[2]
path, why = W.walk(goal)
print(why)
if not path:
    sys.exit(0)
print('plan from rest:', ' '.join(f"{a[0]}{a[1]}" for a in path))

port = 19697 + (os.getpid() % 1000)
env = dict(os.environ, AGC_SPEED='20', AGC_TRACE_CHANNELS='do-channels.bin')
os.chdir(run)
for f in ('core', 'do-channels.bin'):
    if os.path.exists(f):
        os.remove(f)
agc = subprocess.Popen([os.path.join(HERE, 'virtualagc', 'yaAGC', 'yaAGC'), '--nodebug', '--no-resume', '--quiet',
                        f'--port={port}', os.path.join(HERE, 'virtualagc', 'Luminary099', 'MAIN.agc.bin')],
                       stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, env=env)
time.sleep(1.5)
sock = socket.create_connection(('127.0.0.1', port))
sock.setblocking(False)
time.sleep(4.0)                                           # settle, as the loop did
hw = L.Hardware()
pos = 0


def read():
    global pos
    size = os.path.getsize('do-channels.bin')
    with open('do-channels.bin', 'rb') as f:
        f.seek(pos); data = f.read(size - pos)
    pos = size
    for i in range(0, len(data) - 3, 4):
        c, v = L.unpacket(data[i:i + 4])
        if c not in L.CONTROL_CHANNELS:
            hw.take(c, v)


read()
for a in path:
    L.send(sock, a)
    time.sleep(0.25)
    try:
        while sock.recv(65536):
            pass
    except BlockingIOError:
        pass
    read()
    print(f"  pressed {a[0]}{a[1]}")
sock.close(); agc.terminate(); agc.wait()
if os.path.exists('core'):
    os.remove('core')

kind, _, spec = goal.partition(':')
showing = hw.state
if kind == 'word':
    ch, val = spec.split(':')
    hit = [(k, v) for k, v in showing.items() if k[0] == int(ch, 8) and v == int(val, 8)]
    print('showing on channel %s:' % ch, ' '.join(f'row{k[1]}={v:05o}' for k, v in sorted(showing.items()) if k[0] == int(ch, 8)))
    print('goal %s on channel %s: %s' % (val, ch, 'SAME -- it is showing' if hit else 'DIFFERENT -- not showing'))
else:
    print('goal was a context; showing:', {f'{k[0]:03o}.{k[1]}': f'{v:05o}' for k, v in sorted(showing.items())})
